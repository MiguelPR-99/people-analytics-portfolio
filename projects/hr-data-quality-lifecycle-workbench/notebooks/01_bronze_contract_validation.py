"""Validate the initial Bronze landing before any Delta table is written.

Fabric prerequisite: attach ``lh_hr_data_quality_dev`` as the default lakehouse.
The notebook is intentionally fail-fast. A failed assertion prevents promotion to Silver.
"""

import json

from pyspark.sql import functions as F
from pyspark.sql import types as T


BRONZE_ROOT = "/lakehouse/default/Files/bronze"
MANIFEST_PATH = f"{BRONZE_ROOT}/_control/manifest.json"
INGESTION_RUN_ID = "bronze-initial-20261013"


WORKER_COLUMNS = [
    "SourceRecordID", "SnapshotDate", "ExtractedAt", "EmployeeID",
    "EmploymentStatus", "WorkerType", "EmployeeGroup", "HireDate",
    "TerminationDate", "LeaveStartDate", "LeaveExpectedEndDate",
    "ManagerEmployeeID", "PositionID", "OrgUnitCode", "CostCenterCode",
    "LocationCode", "CountryCode", "SourceUpdatedAt", "RecordConfirmedAt",
    "RecordVersion",
]

EVENT_COLUMNS = [
    "SourceRecordID", "ExtractBatchDate", "ExtractedAt", "EventID",
    "EmployeeID", "EventType", "EventStatus", "EffectiveDate", "CompletedAt",
    "PreviousEmploymentStatus", "NewEmploymentStatus",
    "PreviousManagerEmployeeID", "NewManagerEmployeeID", "PreviousPositionID",
    "NewPositionID", "PreviousOrgUnitCode", "NewOrgUnitCode",
    "PreviousCostCenterCode", "NewCostCenterCode", "PreviousLocationCode",
    "NewLocationCode", "SourceUpdatedAt", "RecordVersion",
]

POSITION_COLUMNS = [
    "SourceRecordID", "SnapshotDate", "ExtractedAt", "PositionID",
    "PositionStatus", "PositionFamily", "OrgUnitCode", "OrgUnitName",
    "FunctionGroup", "CostCenterCode", "CostCenterName", "LocationCode",
    "LocationName", "LocationType", "CountryCode", "ManagerEligibleFlag",
    "ManagerRequiredFlag", "MaxIncumbents", "ValidFrom", "ValidTo",
    "SourceUpdatedAt", "RecordVersion",
]


def field(name, data_type):
    # Raw values can be deliberately missing, so every field remains nullable here.
    return T.StructField(name, data_type, True)


WORKER_SCHEMA = T.StructType([
    field("SourceRecordID", T.StringType()),
    field("SnapshotDate", T.DateType()),
    field("ExtractedAt", T.TimestampType()),
    field("EmployeeID", T.StringType()),
    field("EmploymentStatus", T.StringType()),
    field("WorkerType", T.StringType()),
    field("EmployeeGroup", T.StringType()),
    field("HireDate", T.DateType()),
    field("TerminationDate", T.DateType()),
    field("LeaveStartDate", T.DateType()),
    field("LeaveExpectedEndDate", T.DateType()),
    field("ManagerEmployeeID", T.StringType()),
    field("PositionID", T.StringType()),
    field("OrgUnitCode", T.StringType()),
    field("CostCenterCode", T.StringType()),
    field("LocationCode", T.StringType()),
    field("CountryCode", T.StringType()),
    field("SourceUpdatedAt", T.TimestampType()),
    field("RecordConfirmedAt", T.TimestampType()),
    field("RecordVersion", T.IntegerType()),
])

EVENT_SCHEMA = T.StructType([
    field("SourceRecordID", T.StringType()),
    field("ExtractBatchDate", T.DateType()),
    field("ExtractedAt", T.TimestampType()),
    field("EventID", T.StringType()),
    field("EmployeeID", T.StringType()),
    field("EventType", T.StringType()),
    field("EventStatus", T.StringType()),
    field("EffectiveDate", T.DateType()),
    field("CompletedAt", T.TimestampType()),
    field("PreviousEmploymentStatus", T.StringType()),
    field("NewEmploymentStatus", T.StringType()),
    field("PreviousManagerEmployeeID", T.StringType()),
    field("NewManagerEmployeeID", T.StringType()),
    field("PreviousPositionID", T.StringType()),
    field("NewPositionID", T.StringType()),
    field("PreviousOrgUnitCode", T.StringType()),
    field("NewOrgUnitCode", T.StringType()),
    field("PreviousCostCenterCode", T.StringType()),
    field("NewCostCenterCode", T.StringType()),
    field("PreviousLocationCode", T.StringType()),
    field("NewLocationCode", T.StringType()),
    field("SourceUpdatedAt", T.TimestampType()),
    field("RecordVersion", T.IntegerType()),
])

POSITION_SCHEMA = T.StructType([
    field("SourceRecordID", T.StringType()),
    field("SnapshotDate", T.DateType()),
    field("ExtractedAt", T.TimestampType()),
    field("PositionID", T.StringType()),
    field("PositionStatus", T.StringType()),
    field("PositionFamily", T.StringType()),
    field("OrgUnitCode", T.StringType()),
    field("OrgUnitName", T.StringType()),
    field("FunctionGroup", T.StringType()),
    field("CostCenterCode", T.StringType()),
    field("CostCenterName", T.StringType()),
    field("LocationCode", T.StringType()),
    field("LocationName", T.StringType()),
    field("LocationType", T.StringType()),
    field("CountryCode", T.StringType()),
    field("ManagerEligibleFlag", T.BooleanType()),
    field("ManagerRequiredFlag", T.BooleanType()),
    field("MaxIncumbents", T.IntegerType()),
    field("ValidFrom", T.DateType()),
    field("ValidTo", T.DateType()),
    field("SourceUpdatedAt", T.TimestampType()),
    field("RecordVersion", T.IntegerType()),
])


def walk_files(root_path):
    """Return relative file paths and byte sizes below root_path."""
    discovered = {}

    def visit(current_path, relative_parent=""):
        for item in notebookutils.fs.ls(current_path):
            relative_path = f"{relative_parent}/{item.name}".lstrip("/")
            if item.isDir:
                visit(item.path, relative_path)
            else:
                discovered[relative_path] = item.size

    visit(root_path)
    return discovered


manifest = json.loads(notebookutils.fs.head(MANIFEST_PATH, 1_000_000))
manifest_files = {
    item["path"].removeprefix("raw/"): item
    for item in manifest["files"]
}

actual_files = walk_files(BRONZE_ROOT)
expected_paths = set(manifest_files) | {"_control/manifest.json"}
actual_paths = set(actual_files)

assert actual_paths == expected_paths, {
    "missing": sorted(expected_paths - actual_paths),
    "unexpected": sorted(actual_paths - expected_paths),
}

size_mismatches = {
    path: {"expected": metadata["bytes"], "actual": actual_files[path]}
    for path, metadata in manifest_files.items()
    if metadata["bytes"] != actual_files[path]
}
assert not size_mismatches, {"size_mismatches": size_mismatches}


expected_headers = {
    "global_hris": WORKER_COLUMNS,
    "local_hr_operations": EVENT_COLUMNS,
    "organization_master": POSITION_COLUMNS,
}

header_mismatches = {}
for relative_path in sorted(manifest_files):
    source_name = relative_path.split("/", 1)[0]
    header_line = notebookutils.fs.head(
        f"{BRONZE_ROOT}/{relative_path}", 8192
    ).splitlines()[0].lstrip("\ufeff")
    observed_header = header_line.split(",")
    if observed_header != expected_headers[source_name]:
        header_mismatches[relative_path] = {
            "expected": expected_headers[source_name],
            "observed": observed_header,
        }

assert not header_mismatches, {"header_mismatches": header_mismatches}


hash_pairs = []
for relative_path, metadata in manifest_files.items():
    hash_pairs.extend([F.lit(relative_path), F.lit(metadata["sha256"])])
hash_lookup = F.create_map(*hash_pairs)


def read_typed_csv(relative_glob, schema, source_system, batch_column):
    frame = (
        spark.read
        .option("header", "true")
        .option("mode", "FAILFAST")
        .option("dateFormat", "yyyy-MM-dd")
        .option("timestampFormat", "yyyy-MM-dd'T'HH:mm:ssXXX")
        .schema(schema)
        .csv(f"{BRONZE_ROOT}/{relative_glob}")
        .withColumn(
            "SourceFilePath",
            F.regexp_extract(F.input_file_name(), r"/bronze/(.*)$", 1),
        )
        .withColumn("SourceFileHash", hash_lookup[F.col("SourceFilePath")])
        .withColumn("SourceSystem", F.lit(source_system))
        .withColumn("BatchDate", F.col(batch_column))
        .withColumn("IngestionRunID", F.lit(INGESTION_RUN_ID))
        .withColumn("IngestedAt", F.current_timestamp())
    )
    return frame


workers = read_typed_csv(
    "global_hris/snapshot_date=*/workers.csv",
    WORKER_SCHEMA,
    "GHRIS",
    "SnapshotDate",
)

lifecycle_events = read_typed_csv(
    "local_hr_operations/extract_date=*/lifecycle_events.csv",
    EVENT_SCHEMA,
    "LHROPS",
    "ExtractBatchDate",
)

positions = read_typed_csv(
    "organization_master/snapshot_date=*/positions.csv",
    POSITION_SCHEMA,
    "ORGMD",
    "SnapshotDate",
)


row_counts = (
    workers.select("SourceFilePath")
    .unionByName(lifecycle_events.select("SourceFilePath"))
    .unionByName(positions.select("SourceFilePath"))
    .groupBy("SourceFilePath")
    .count()
    .collect()
)
observed_rows = {row["SourceFilePath"]: row["count"] for row in row_counts}
expected_rows = {path: item["rows"] for path, item in manifest_files.items()}

row_mismatches = {
    path: {"expected": expected_rows[path], "actual": observed_rows.get(path)}
    for path in expected_rows
    if expected_rows[path] != observed_rows.get(path)
}
assert not row_mismatches, {"row_mismatches": row_mismatches}

assert all(observed_rows.values()), "At least one Bronze file produced zero rows."
assert workers.filter(F.col("SourceFileHash").isNull()).limit(1).count() == 0
assert lifecycle_events.filter(F.col("SourceFileHash").isNull()).limit(1).count() == 0
assert positions.filter(F.col("SourceFileHash").isNull()).limit(1).count() == 0


validation_summary = spark.createDataFrame([
    ("global_hris", 6, len(WORKER_COLUMNS), workers.count()),
    ("local_hr_operations", 6, len(EVENT_COLUMNS), lifecycle_events.count()),
    ("organization_master", 6, len(POSITION_COLUMNS), positions.count()),
], ["Source", "Files", "SourceColumns", "Rows"])

display(validation_summary.orderBy("Source"))
print("BRONZE_CONTRACT_VALIDATION: PASS")
