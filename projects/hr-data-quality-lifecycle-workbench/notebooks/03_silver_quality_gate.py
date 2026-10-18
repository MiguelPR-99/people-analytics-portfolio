"""Validate Silver invariants before any Gold quality rule is evaluated.

Fabric prerequisite: attach ``lh_hr_data_quality_dev`` as the default lakehouse.
This notebook is read-only and intentionally fails on the first broken invariant.
"""

from pyspark.sql import functions as F
from pyspark.sql import types as T


workers = spark.table("dbo.silver_worker_snapshot")
events = spark.table("dbo.silver_lifecycle_event")
positions = spark.table("dbo.silver_position_reference")
audit = spark.table("dbo.silver_load_audit")


def null_metadata_rows(frame):
    required_metadata = [
        "SourceFilePath",
        "SourceFileHash",
        "SourceSystem",
        "BatchDate",
        "IngestionRunID",
        "IngestedAt",
        "RecordContentHash",
        "BusinessKeyRowCount",
        "IsDuplicateBusinessKey",
        "CanonicalRank",
        "IsCanonical",
    ]
    missing_condition = None
    for column_name in required_metadata:
        current = F.col(column_name).isNull()
        missing_condition = current if missing_condition is None else missing_condition | current
    return frame.filter(missing_condition).count()


def duplicate_group_count(frame, business_key):
    return (
        frame
        .filter(F.col(business_key).isNotNull())
        .groupBy("BatchDate", business_key)
        .count()
        .filter(F.col("count") > 1)
        .count()
    )


def canonical_group_violations(frame, business_key):
    return (
        frame
        .filter(F.col(business_key).isNotNull())
        .groupBy("BatchDate", business_key)
        .agg(
            F.count(F.lit(1)).alias("ObservedRows"),
            F.max("BusinessKeyRowCount").alias("DeclaredRows"),
            F.sum(F.col("IsCanonical").cast("int")).alias("CanonicalRows"),
        )
        .filter(
            (F.col("ObservedRows") != F.col("DeclaredRows"))
            | (F.col("CanonicalRows") != 1)
        )
        .count()
    )


def schema_type(frame, column_name):
    return next(
        field.dataType
        for field in frame.schema.fields
        if field.name == column_name
    )


checks = [
    ("worker_rows", 8359, workers.count()),
    ("event_rows", 2867, events.count()),
    ("position_rows", 8700, positions.count()),
    ("worker_partitions", 6, workers.select("BatchDate").distinct().count()),
    ("event_partitions", 6, events.select("BatchDate").distinct().count()),
    ("position_partitions", 6, positions.select("BatchDate").distinct().count()),
    ("worker_duplicate_groups", 24, duplicate_group_count(workers, "EmployeeID")),
    ("worker_duplicate_flagged_rows", 48, workers.filter("IsDuplicateBusinessKey").count()),
    ("worker_noncanonical_rows", 24, workers.filter(~F.col("IsCanonical")).count()),
    ("event_duplicate_groups", 0, duplicate_group_count(events, "EventID")),
    ("position_duplicate_groups", 0, duplicate_group_count(positions, "PositionID")),
    ("worker_canonical_violations", 0, canonical_group_violations(workers, "EmployeeID")),
    ("event_canonical_violations", 0, canonical_group_violations(events, "EventID")),
    ("position_canonical_violations", 0, canonical_group_violations(positions, "PositionID")),
    ("worker_null_metadata_rows", 0, null_metadata_rows(workers)),
    ("event_null_metadata_rows", 0, null_metadata_rows(events)),
    ("position_null_metadata_rows", 0, null_metadata_rows(positions)),
    ("audit_pass_rows", 3, audit.filter(F.col("LoadStatus") == "PASS").count()),
]


assert isinstance(schema_type(workers, "SnapshotDate"), T.DateType)
assert isinstance(schema_type(workers, "RecordVersion"), T.IntegerType)
assert isinstance(schema_type(workers, "IsCanonical"), T.BooleanType)
assert isinstance(schema_type(events, "EffectiveDate"), T.DateType)
assert isinstance(schema_type(positions, "ManagerEligibleFlag"), T.BooleanType)


failed_checks = [
    {"Check": name, "Expected": expected, "Observed": observed}
    for name, expected, observed in checks
    if expected != observed
]
assert not failed_checks, {"failed_checks": failed_checks}


quality_gate = spark.createDataFrame(
    [
        (name, expected, observed, "PASS" if expected == observed else "FAIL")
        for name, expected, observed in checks
    ],
    ["Check", "Expected", "Observed", "Status"],
)

display(quality_gate.orderBy("Check"))
print("SILVER_QUALITY_GATE: PASS")
