"""Reconstruct lifecycle state by attribute and event semantics.

Fabric prerequisite: attach ``lh_hr_data_quality_dev`` as the default lakehouse.
An event only updates the attributes implied by its type. This prevents a leave
event, for example, from overwriting a later organizational assignment.
"""

import json
from functools import reduce

from pyspark.sql import functions as F
from pyspark.sql.window import Window


RUN_ID = "dq-run-initial-20261013"
MANIFEST_PATH = "/lakehouse/default/Files/bronze/_control/manifest.json"
TARGET_TABLE = "dbo.gold_employee_lifecycle_state"

spark.conf.set("spark.sql.session.timeZone", "America/Mexico_City")


workers = (
    spark.table("dbo.silver_worker_snapshot")
    .filter(F.col("IsCanonical") & F.col("EmployeeID").isNotNull())
    .select(
        "SnapshotDate",
        "EmployeeID",
        F.col("EmploymentStatus").alias("ObservedEmploymentStatus"),
        F.col("ManagerEmployeeID").alias("ObservedManagerEmployeeID"),
        F.col("PositionID").alias("ObservedPositionID"),
        F.col("OrgUnitCode").alias("ObservedOrgUnitCode"),
        F.col("CostCenterCode").alias("ObservedCostCenterCode"),
        F.col("LocationCode").alias("ObservedLocationCode"),
        F.col("SourceRecordID").alias("WorkerSourceRecordID"),
        F.col("SourceFilePath").alias("WorkerSourceFilePath"),
    )
)

events = (
    spark.table("dbo.silver_lifecycle_event")
    .filter(F.col("IsCanonical") & (F.col("EventStatus") == "Completed"))
)


attribute_config = {
    "EmploymentStatus": {
        "new_value": "NewEmploymentStatus",
        "event_types": ["PreHireCreated", "Hire", "LeaveStart", "LeaveEnd", "Termination"],
    },
    "ManagerEmployeeID": {
        "new_value": "NewManagerEmployeeID",
        "event_types": ["PreHireCreated", "Hire", "ManagerChange", "Promotion", "Transfer"],
    },
    "PositionID": {
        "new_value": "NewPositionID",
        "event_types": ["PreHireCreated", "Hire", "Promotion", "Transfer"],
    },
    "OrgUnitCode": {
        "new_value": "NewOrgUnitCode",
        "event_types": ["PreHireCreated", "Hire", "Promotion", "Transfer"],
    },
    "CostCenterCode": {
        "new_value": "NewCostCenterCode",
        "event_types": ["PreHireCreated", "Hire", "CostCenterChange", "Promotion", "Transfer"],
    },
    "LocationCode": {
        "new_value": "NewLocationCode",
        "event_types": ["PreHireCreated", "Hire", "LocationChange", "Promotion", "Transfer"],
    },
}


def latest_attribute_state(attribute_name, new_value_column, event_types):
    """Return the last event allowed to update one attribute for each snapshot."""
    candidates = (
        workers.select("SnapshotDate", "EmployeeID").alias("w")
        .join(
            events.filter(F.col("EventType").isin(event_types)).alias("e"),
            (F.col("w.EmployeeID") == F.col("e.EmployeeID"))
            & (F.col("e.EffectiveDate") <= F.col("w.SnapshotDate"))
            & (F.to_date(F.col("e.CompletedAt")) <= F.col("w.SnapshotDate"))
            & (F.col("e.ExtractBatchDate") <= F.col("w.SnapshotDate")),
            "left",
        )
    )
    latest_window = (
        Window
        .partitionBy(F.col("w.SnapshotDate"), F.col("w.EmployeeID"))
        .orderBy(
            F.col("e.EffectiveDate").desc_nulls_last(),
            F.col("e.CompletedAt").desc_nulls_last(),
            F.col("e.RecordVersion").desc_nulls_last(),
            F.col("e.EventID").desc_nulls_last(),
        )
    )
    return (
        candidates
        .withColumn("_attribute_rank", F.row_number().over(latest_window))
        .filter(F.col("_attribute_rank") == 1)
        .select(
            F.col("w.SnapshotDate").alias("SnapshotDate"),
            F.col("w.EmployeeID").alias("EmployeeID"),
            F.col(f"e.{new_value_column}").alias(f"Reconstructed{attribute_name}"),
            F.col("e.EventID").alias(f"{attribute_name}EventID"),
            F.col("e.EventType").alias(f"{attribute_name}EventType"),
            F.col("e.EffectiveDate").alias(f"{attribute_name}EffectiveDate"),
            F.col("e.CompletedAt").alias(f"{attribute_name}CompletedAt"),
        )
    )


attribute_states = [
    latest_attribute_state(
        attribute_name,
        config["new_value"],
        config["event_types"],
    )
    for attribute_name, config in attribute_config.items()
]

lifecycle_state = reduce(
    lambda left, right: left.join(right, ["SnapshotDate", "EmployeeID"], "left"),
    attribute_states,
    workers,
)


def business_days_since(completed_at_column):
    completion_date = F.to_date(F.col(completed_at_column))
    return (
        F.when(completion_date.isNull(), F.lit(None).cast("int"))
        .when(completion_date >= F.col("SnapshotDate"), F.lit(0))
        .otherwise(
            F.size(
                F.filter(
                    F.sequence(
                        F.date_add(completion_date, 1),
                        F.col("SnapshotDate"),
                    ),
                    lambda day: F.dayofweek(day).between(2, 6),
                )
            )
        )
    )


mismatch_candidates = []
actionable_mismatch_candidates = []
event_ids = []

for attribute_name in attribute_config:
    observed = F.col(f"Observed{attribute_name}")
    reconstructed = F.col(f"Reconstructed{attribute_name}")
    completed_at_column = f"{attribute_name}CompletedAt"
    business_days_column = f"{attribute_name}BusinessDaysSinceCompletion"

    lifecycle_state = lifecycle_state.withColumn(
        business_days_column,
        business_days_since(completed_at_column),
    )
    mismatch = ~observed.eqNullSafe(reconstructed)
    mismatch_candidates.append(F.when(mismatch, F.lit(attribute_name)))
    actionable_mismatch_candidates.append(
        F.when(
            mismatch & (F.col(business_days_column) > 2),
            F.lit(attribute_name),
        )
    )
    event_ids.append(F.col(f"{attribute_name}EventID"))


lifecycle_state = (
    lifecycle_state
    .withColumn("RunID", F.lit(RUN_ID))
    .withColumn(
        "MismatchFields",
        F.filter(F.array(*mismatch_candidates), lambda item: item.isNotNull()),
    )
    .withColumn(
        "ActionableMismatchFields",
        F.filter(
            F.array(*actionable_mismatch_candidates),
            lambda item: item.isNotNull(),
        ),
    )
    .withColumn(
        "ReconciliationEligibleFlag",
        reduce(lambda left, right: left & right.isNotNull(), event_ids, F.lit(True)),
    )
    .withColumn(
        "ToleranceAppliedFlag",
        F.size("MismatchFields") > F.size("ActionableMismatchFields"),
    )
    .withColumn(
        "ReconciliationPassFlag",
        F.when(~F.col("ReconciliationEligibleFlag"), F.lit(None).cast("boolean"))
        .otherwise(F.size("ActionableMismatchFields") == 0),
    )
    .withColumn("EvaluatedAt", F.current_timestamp())
)


manifest = json.loads(notebookutils.fs.head(MANIFEST_PATH, 1_000_000))
expected_dq7 = {
    snapshot: values["DQ-007"]
    for snapshot, values in manifest["quality_evaluation"]["by_snapshot"].items()
}

observed_dq7 = {
    row["SnapshotDate"].isoformat(): {
        "eligible": row["eligible"],
        "passed": row["passed"],
        "failed": row["failed"],
    }
    for row in (
        lifecycle_state
        .groupBy("SnapshotDate")
        .agg(
            F.sum(F.col("ReconciliationEligibleFlag").cast("long")).alias("eligible"),
            F.sum(
                F.when(F.col("ReconciliationPassFlag") == True, 1).otherwise(0)
            ).alias("passed"),
            F.sum(
                F.when(F.col("ReconciliationPassFlag") == False, 1).otherwise(0)
            ).alias("failed"),
        )
        .collect()
    )
}

assert lifecycle_state.count() == 8335
assert lifecycle_state.select("SnapshotDate").distinct().count() == 6
assert lifecycle_state.filter(~F.col("ReconciliationEligibleFlag")).count() == 0
assert observed_dq7 == expected_dq7, {
    "expected": expected_dq7,
    "observed": observed_dq7,
}


(
    lifecycle_state.write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .partitionBy("SnapshotDate")
    .saveAsTable(TARGET_TABLE)
)

assert spark.table(TARGET_TABLE).count() == 8335


reconciliation_summary = (
    spark.table(TARGET_TABLE)
    .groupBy("SnapshotDate")
    .agg(
        F.count(F.lit(1)).alias("Rows"),
        F.sum(F.col("ReconciliationEligibleFlag").cast("long")).alias("Eligible"),
        F.sum(
            F.when(F.col("ReconciliationPassFlag") == False, 1).otherwise(0)
        ).alias("Failed"),
        F.sum(F.size("ActionableMismatchFields")).alias("ActionableFields"),
        F.sum(F.col("ToleranceAppliedFlag").cast("long")).alias("ToleranceApplied"),
    )
    .orderBy("SnapshotDate")
)

display(reconciliation_summary)
print("GOLD_LIFECYCLE_STATE: PASS")
