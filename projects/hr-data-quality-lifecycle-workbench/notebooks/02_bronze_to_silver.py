"""Create the initial Silver Delta tables from validated Bronze CSV files.

Fabric prerequisite: attach ``lh_hr_data_quality_dev`` as the default lakehouse.
This initial load is idempotent: rerunning it replaces the same four Silver tables.
All source rows are retained; duplicate business keys are flagged, not deleted.
"""

import json

from pyspark.sql import functions as F
from pyspark.sql import types as T
from pyspark.sql.window import Window


BRONZE_ROOT = "Files/bronze"
MANIFEST_PATH = f"{BRONZE_ROOT}/_control/manifest.json"
INGESTION_RUN_ID = "bronze-initial-20261013"

spark.conf.set("spark.sql.session.timeZone", "America/Mexico_City")


WORKER_SCHEMA = """
    SourceRecordID STRING, SnapshotDate DATE, ExtractedAt TIMESTAMP,
    EmployeeID STRING, EmploymentStatus STRING, WorkerType STRING,
    EmployeeGroup STRING, HireDate DATE, TerminationDate DATE,
    LeaveStartDate DATE, LeaveExpectedEndDate DATE, ManagerEmployeeID STRING,
    PositionID STRING, OrgUnitCode STRING, CostCenterCode STRING,
    LocationCode STRING, CountryCode STRING, SourceUpdatedAt TIMESTAMP,
    RecordConfirmedAt TIMESTAMP, RecordVersion INT
"""

EVENT_SCHEMA = """
    SourceRecordID STRING, ExtractBatchDate DATE, ExtractedAt TIMESTAMP,
    EventID STRING, EmployeeID STRING, EventType STRING, EventStatus STRING,
    EffectiveDate DATE, CompletedAt TIMESTAMP, PreviousEmploymentStatus STRING,
    NewEmploymentStatus STRING, PreviousManagerEmployeeID STRING,
    NewManagerEmployeeID STRING, PreviousPositionID STRING, NewPositionID STRING,
    PreviousOrgUnitCode STRING, NewOrgUnitCode STRING,
    PreviousCostCenterCode STRING, NewCostCenterCode STRING,
    PreviousLocationCode STRING, NewLocationCode STRING,
    SourceUpdatedAt TIMESTAMP, RecordVersion INT
"""

POSITION_SCHEMA = """
    SourceRecordID STRING, SnapshotDate DATE, ExtractedAt TIMESTAMP,
    PositionID STRING, PositionStatus STRING, PositionFamily STRING,
    OrgUnitCode STRING, OrgUnitName STRING, FunctionGroup STRING,
    CostCenterCode STRING, CostCenterName STRING, LocationCode STRING,
    LocationName STRING, LocationType STRING, CountryCode STRING,
    ManagerEligibleFlag BOOLEAN, ManagerRequiredFlag BOOLEAN,
    MaxIncumbents INT, ValidFrom DATE, ValidTo DATE,
    SourceUpdatedAt TIMESTAMP, RecordVersion INT
"""


manifest = json.loads(notebookutils.fs.head(MANIFEST_PATH, 1_000_000))
manifest_files = {
    item["path"].removeprefix("raw/"): item
    for item in manifest["files"]
}

hash_pairs = []
for relative_path, metadata in manifest_files.items():
    hash_pairs.extend([F.lit(relative_path), F.lit(metadata["sha256"])])
hash_lookup = F.create_map(*hash_pairs)


def read_bronze(relative_glob, schema, source_system, batch_column):
    return (
        spark.read
        .option("header", "true")
        .option("mode", "FAILFAST")
        .option("dateFormat", "yyyy-MM-dd")
        .option("timestampFormat", "yyyy-MM-dd['T'HH:mm:ssXXX]")
        .schema(schema)
        .csv(f"{BRONZE_ROOT}/{relative_glob}")
        .withColumn(
            "SourceFilePath",
            F.regexp_replace(
                F.regexp_extract(F.input_file_name(), r"/bronze/(.*)$", 1),
                r"\?.*$",
                "",
            ),
        )
        .withColumn("SourceFileHash", hash_lookup[F.col("SourceFilePath")])
        .withColumn("SourceSystem", F.lit(source_system))
        .withColumn("BatchDate", F.col(batch_column))
        .withColumn("IngestionRunID", F.lit(INGESTION_RUN_ID))
        .withColumn("IngestedAt", F.current_timestamp())
    )


def normalize_strings(frame):
    """Trim strings, convert empty strings to null, and uppercase technical codes."""
    string_columns = [
        field.name
        for field in frame.schema.fields
        if isinstance(field.dataType, T.StringType)
    ]
    for column_name in string_columns:
        frame = frame.withColumn(
            column_name,
            F.when(F.trim(F.col(column_name)) == "", F.lit(None))
            .otherwise(F.trim(F.col(column_name))),
        )

    uppercase_columns = [
        name for name in [
            "SourceRecordID", "EmployeeID", "EventID", "ManagerEmployeeID",
            "PreviousManagerEmployeeID", "NewManagerEmployeeID", "PositionID",
            "PreviousPositionID", "NewPositionID", "OrgUnitCode",
            "PreviousOrgUnitCode", "NewOrgUnitCode", "CostCenterCode",
            "PreviousCostCenterCode", "NewCostCenterCode", "LocationCode",
            "PreviousLocationCode", "NewLocationCode", "CountryCode",
        ]
        if name in frame.columns
    ]
    for column_name in uppercase_columns:
        frame = frame.withColumn(column_name, F.upper(F.col(column_name)))
    return frame


def add_record_hash(frame, source_columns):
    canonical_values = [
        F.coalesce(F.col(name).cast("string"), F.lit("<NULL>"))
        for name in source_columns
    ]
    return frame.withColumn(
        "RecordContentHash",
        F.sha2(F.concat_ws("||", *canonical_values), 256),
    )


def add_business_key_flags(frame, business_key, order_columns):
    """Flag duplicate business keys while retaining every physical source row."""
    effective_key = F.coalesce(
        F.col(business_key),
        F.concat(F.lit("__SOURCE__"), F.col("SourceRecordID")),
    )
    group_window = Window.partitionBy("BatchDate", effective_key)
    rank_window = group_window.orderBy(*order_columns)
    return (
        frame
        .withColumn("BusinessKeyRowCount", F.count(F.lit(1)).over(group_window))
        .withColumn(
            "IsDuplicateBusinessKey",
            F.col(business_key).isNotNull() & (F.col("BusinessKeyRowCount") > 1),
        )
        .withColumn("CanonicalRank", F.row_number().over(rank_window))
        .withColumn("IsCanonical", F.col("CanonicalRank") == 1)
    )


worker_source_columns = spark.createDataFrame([], WORKER_SCHEMA).columns
event_source_columns = spark.createDataFrame([], EVENT_SCHEMA).columns
position_source_columns = spark.createDataFrame([], POSITION_SCHEMA).columns


workers = normalize_strings(read_bronze(
    "global_hris/snapshot_date=*/workers.csv",
    WORKER_SCHEMA,
    "GHRIS",
    "SnapshotDate",
))
workers = add_record_hash(workers, worker_source_columns)
workers = add_business_key_flags(
    workers,
    "EmployeeID",
    [
        F.col("RecordVersion").desc_nulls_last(),
        F.col("SourceUpdatedAt").desc_nulls_last(),
        F.col("SourceRecordID").asc_nulls_last(),
    ],
)


lifecycle_events = normalize_strings(read_bronze(
    "local_hr_operations/extract_date=*/lifecycle_events.csv",
    EVENT_SCHEMA,
    "LHROPS",
    "ExtractBatchDate",
))
lifecycle_events = add_record_hash(lifecycle_events, event_source_columns)
lifecycle_events = add_business_key_flags(
    lifecycle_events,
    "EventID",
    [
        F.col("RecordVersion").desc_nulls_last(),
        F.col("SourceUpdatedAt").desc_nulls_last(),
        F.col("SourceRecordID").asc_nulls_last(),
    ],
)


positions = normalize_strings(read_bronze(
    "organization_master/snapshot_date=*/positions.csv",
    POSITION_SCHEMA,
    "ORGMD",
    "SnapshotDate",
))
positions = add_record_hash(positions, position_source_columns)
positions = add_business_key_flags(
    positions,
    "PositionID",
    [
        F.col("RecordVersion").desc_nulls_last(),
        F.col("ValidFrom").desc_nulls_last(),
        F.col("SourceRecordID").asc_nulls_last(),
    ],
)


expected_rows_by_source = {}
for relative_path, metadata in manifest_files.items():
    source_folder = relative_path.split("/", 1)[0]
    expected_rows_by_source[source_folder] = (
        expected_rows_by_source.get(source_folder, 0) + metadata["rows"]
    )

silver_frames = {
    "dbo.silver_worker_snapshot": (
        workers,
        expected_rows_by_source["global_hris"],
        "GHRIS",
    ),
    "dbo.silver_lifecycle_event": (
        lifecycle_events,
        expected_rows_by_source["local_hr_operations"],
        "LHROPS",
    ),
    "dbo.silver_position_reference": (
        positions,
        expected_rows_by_source["organization_master"],
        "ORGMD",
    ),
}


observed_before_write = {}
for table_name, (frame, expected_rows, _) in silver_frames.items():
    frame.persist()
    observed_rows = frame.count()
    observed_before_write[table_name] = observed_rows
    assert observed_rows == expected_rows, {
        "table": table_name,
        "expected": expected_rows,
        "observed": observed_rows,
    }
    assert frame.filter(F.col("SourceFileHash").isNull()).limit(1).count() == 0
    assert frame.filter(F.col("SourceFilePath").isNull()).limit(1).count() == 0


for table_name, (frame, _, _) in silver_frames.items():
    (
        frame.write
        .format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .partitionBy("BatchDate")
        .saveAsTable(table_name)
    )


audit_rows = []
for table_name, (_, expected_rows, source_system) in silver_frames.items():
    persisted_rows = spark.table(table_name).count()
    assert persisted_rows == expected_rows, {
        "table": table_name,
        "expected": expected_rows,
        "persisted": persisted_rows,
    }
    audit_rows.append((
        INGESTION_RUN_ID,
        source_system,
        table_name,
        6,
        expected_rows,
        persisted_rows,
        "PASS",
    ))


audit_schema = T.StructType([
    T.StructField("IngestionRunID", T.StringType(), False),
    T.StructField("SourceSystem", T.StringType(), False),
    T.StructField("TargetTable", T.StringType(), False),
    T.StructField("SourceFileCount", T.IntegerType(), False),
    T.StructField("ExpectedRows", T.LongType(), False),
    T.StructField("PersistedRows", T.LongType(), False),
    T.StructField("LoadStatus", T.StringType(), False),
])

silver_load_audit = (
    spark.createDataFrame(audit_rows, audit_schema)
    .withColumn("AuditedAt", F.current_timestamp())
)

(
    silver_load_audit.write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable("dbo.silver_load_audit")
)

display(spark.table("dbo.silver_load_audit").orderBy("TargetTable"))
print("SILVER_INITIAL_LOAD: PASS")
