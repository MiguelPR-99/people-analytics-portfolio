"""Evaluate DQ-001 through DQ-008 and materialize the Gold quality model.

Fabric prerequisite: attach ``lh_hr_data_quality_dev`` as the default lakehouse
and run notebooks 02 and 04 successfully. The notebook validates every rule
against the synthetic manifest before replacing any Gold result table.
"""

import json
from functools import reduce

from pyspark.sql import functions as F


RUN_ID = "dq-run-initial-20261013"
MANIFEST_PATH = "/lakehouse/default/Files/bronze/_control/manifest.json"

RESULT_TABLE = "dbo.gold_dq_rule_result"
EXCEPTION_TABLE = "dbo.gold_dq_exception"
SCORE_TABLE = "dbo.gold_dq_score_snapshot"
AUDIT_TABLE = "dbo.gold_dq_run_audit"

spark.conf.set("spark.sql.session.timeZone", "America/Mexico_City")


RULES = {
    "DQ-001": {
        "name": "Required fields complete",
        "dimension": "Completeness",
        "severity": "High",
        "weight": 3,
        "owner": "HR Operations Data",
        "source": "GHRIS",
        "expected": "Required worker attributes are populated for the employment state.",
    },
    "DQ-002": {
        "name": "Employee snapshot key unique",
        "dimension": "Uniqueness",
        "severity": "Critical",
        "weight": 4,
        "owner": "HRIS Integration",
        "source": "GHRIS",
        "expected": "Exactly one source row exists per SnapshotDate and EmployeeID.",
    },
    "DQ-003": {
        "name": "Manager reference valid and eligible",
        "dimension": "Referential Integrity",
        "severity": "High",
        "weight": 3,
        "owner": "Organization Management",
        "source": "GHRIS",
        "expected": "The manager exists in the snapshot, is active, is not self, and occupies an eligible position.",
    },
    "DQ-004": {
        "name": "Organizational assignment valid as of snapshot",
        "dimension": "Validity",
        "severity": "High",
        "weight": 3,
        "owner": "Organization Management",
        "source": "GHRIS",
        "expected": "Worker organizational attributes match the referenced position.",
    },
    "DQ-005": {
        "name": "Position occupancy within allowed capacity",
        "dimension": "Consistency",
        "severity": "High",
        "weight": 3,
        "owner": "Organization Management",
        "source": "GHRIS",
        "expected": "Observed occupants do not exceed MaxIncumbents.",
    },
    "DQ-006": {
        "name": "Employment dates temporally coherent",
        "dimension": "Temporal Coherence",
        "severity": "Critical",
        "weight": 4,
        "owner": "HR Operations Data",
        "source": "GHRIS",
        "expected": "Employment, termination, and leave dates form a coherent timeline.",
    },
    "DQ-007": {
        "name": "HRIS state reconciles to completed lifecycle events",
        "dimension": "Cross-system Consistency",
        "severity": "Critical",
        "weight": 4,
        "owner": "HRIS Integration",
        "source": "CROSS_SYSTEM",
        "expected": "HRIS agrees with reconstructed event state after the two-business-day tolerance.",
    },
    "DQ-008": {
        "name": "Source record updated within freshness threshold",
        "dimension": "Timeliness",
        "severity": "Medium",
        "weight": 2,
        "owner": "HRIS Integration",
        "source": "GHRIS",
        "expected": "Update or confirmation is not future and is no more than five business days old.",
    },
}


workers_all = spark.table("dbo.silver_worker_snapshot")
workers = workers_all.filter(F.col("IsCanonical") & F.col("EmployeeID").isNotNull())
positions = spark.table("dbo.silver_position_reference").filter(F.col("IsCanonical"))
lifecycle_state = spark.table("dbo.gold_employee_lifecycle_state")


def business_days_between(start_date_column, end_date_column):
    start_date = F.to_date(start_date_column)
    end_date = F.to_date(end_date_column)
    return (
        F.when(start_date.isNull() | end_date.isNull(), F.lit(None).cast("int"))
        .when(start_date >= end_date, F.lit(0))
        .otherwise(
            F.size(
                F.filter(
                    F.sequence(F.date_add(start_date, 1), end_date),
                    lambda day: F.dayofweek(day).between(2, 6),
                )
            )
        )
    )


def operational_sla(severity_column):
    return (
        F.when(severity_column == "Critical", 1)
        .when(severity_column == "High", 3)
        .when(severity_column == "Medium", 5)
        .otherwise(10)
    )


def finalize_rule(
    frame,
    rule_code,
    business_key,
    field_scope,
    pass_flag,
    observed_value,
    operational_severity=None,
):
    metadata = RULES[rule_code]
    severity = (
        operational_severity
        if operational_severity is not None
        else F.lit(metadata["severity"])
    )
    selected = frame.select(
        F.lit(RUN_ID).alias("RunID"),
        F.lit(rule_code).alias("RuleCode"),
        F.lit(metadata["name"]).alias("RuleName"),
        F.lit(metadata["dimension"]).alias("QualityDimension"),
        F.col("SnapshotDate"),
        F.lit(metadata["source"]).alias("SourceSystem"),
        business_key.cast("string").alias("BusinessKey"),
        field_scope.cast("string").alias("FieldScope"),
        F.lit(True).alias("EligibleFlag"),
        pass_flag.cast("boolean").alias("PassFlag"),
        F.lit(metadata["severity"]).alias("Severity"),
        F.lit(metadata["weight"]).cast("int").alias("SeverityWeight"),
        severity.alias("OperationalSeverity"),
        operational_sla(severity).cast("int").alias("SlaBusinessDays"),
        F.lit(metadata["owner"]).alias("OwnerDomain"),
        observed_value.alias("ObservedValue"),
        F.lit(metadata["expected"]).alias("ExpectedCondition"),
        F.current_timestamp().alias("EvaluatedAt"),
    )
    return selected.withColumn(
        "RuleResultID",
        F.sha2(
            F.concat_ws(
                "|",
                "RunID",
                "RuleCode",
                F.col("SnapshotDate").cast("string"),
                "BusinessKey",
                "FieldScope",
                "ObservedValue",
            ),
            256,
        ),
    ).select(
        "RunID",
        "RuleResultID",
        "RuleCode",
        "RuleName",
        "QualityDimension",
        "SnapshotDate",
        "SourceSystem",
        "BusinessKey",
        "FieldScope",
        "EligibleFlag",
        "PassFlag",
        "Severity",
        "SeverityWeight",
        "OperationalSeverity",
        "SlaBusinessDays",
        "OwnerDomain",
        "ObservedValue",
        "ExpectedCondition",
        "EvaluatedAt",
    )


# DQ-001 — completeness on every physical GHRIS row.
required_fields = [
    "EmployeeID",
    "EmploymentStatus",
    "WorkerType",
    "EmployeeGroup",
    "HireDate",
    "PositionID",
    "OrgUnitCode",
    "CostCenterCode",
    "LocationCode",
    "SourceUpdatedAt",
    "RecordConfirmedAt",
]

dq1_missing = [
    F.when(F.col(name).isNull(), F.lit(name))
    for name in required_fields
]
dq1_missing.extend([
    F.when(
        (F.col("EmploymentStatus") == "Terminated") & F.col("TerminationDate").isNull(),
        F.lit("TerminationDate"),
    ),
    F.when(
        (F.col("EmploymentStatus") == "Leave") & F.col("LeaveStartDate").isNull(),
        F.lit("LeaveStartDate"),
    ),
    F.when(
        (F.col("EmploymentStatus") == "Leave") & F.col("LeaveExpectedEndDate").isNull(),
        F.lit("LeaveExpectedEndDate"),
    ),
])

dq1_base = workers_all.withColumn(
    "MissingFields",
    F.filter(F.array(*dq1_missing), lambda item: item.isNotNull()),
)
dq1_operational_severity = F.when(
    F.array_contains(F.col("MissingFields"), "EmployeeID")
    | F.array_contains(F.col("MissingFields"), "EmploymentStatus"),
    F.lit("Critical"),
).otherwise(F.lit("High"))

dq1 = finalize_rule(
    dq1_base,
    "DQ-001",
    F.coalesce("EmployeeID", "SourceRecordID"),
    F.when(F.size("MissingFields") > 0, F.concat_ws(",", "MissingFields"))
    .otherwise(F.lit("RequiredFields")),
    F.size("MissingFields") == 0,
    F.to_json(F.struct("SourceRecordID", "EmploymentStatus", "MissingFields")),
    dq1_operational_severity,
)


# DQ-002 — one row per employee and snapshot.
dq2_base = (
    workers_all
    .filter(F.col("EmployeeID").isNotNull())
    .groupBy("SnapshotDate", "EmployeeID")
    .agg(
        F.count(F.lit(1)).alias("ObservedRows"),
        F.sort_array(F.collect_list("SourceRecordID")).alias("SourceRecordIDs"),
        F.sort_array(F.collect_list("RecordVersion")).alias("RecordVersions"),
    )
)
dq2 = finalize_rule(
    dq2_base,
    "DQ-002",
    F.col("EmployeeID"),
    F.lit("SnapshotDate+EmployeeID"),
    F.col("ObservedRows") == 1,
    F.to_json(F.struct("ObservedRows", "SourceRecordIDs", "RecordVersions")),
)


# DQ-003 — manager exists, is active, is not self, and is manager-eligible.
w = workers.alias("w")
p = positions.alias("p")
m = workers.select(
    "SnapshotDate",
    F.col("EmployeeID").alias("ManagerLookupID"),
    F.col("EmploymentStatus").alias("ManagerEmploymentStatus"),
    F.col("PositionID").alias("ManagerPositionID"),
).alias("m")
mp = positions.select(
    "SnapshotDate",
    F.col("PositionID").alias("ManagerPositionLookupID"),
    F.col("ManagerEligibleFlag").alias("ManagerEligibleFlag"),
).alias("mp")

dq3_base = (
    w
    .join(
        p,
        (F.col("w.SnapshotDate") == F.col("p.SnapshotDate"))
        & (F.col("w.PositionID") == F.col("p.PositionID")),
        "left",
    )
    .join(
        m,
        (F.col("w.SnapshotDate") == F.col("m.SnapshotDate"))
        & (F.col("w.ManagerEmployeeID") == F.col("m.ManagerLookupID")),
        "left",
    )
    .join(
        mp,
        (F.col("w.SnapshotDate") == F.col("mp.SnapshotDate"))
        & (F.col("m.ManagerPositionID") == F.col("mp.ManagerPositionLookupID")),
        "left",
    )
    .filter(
        F.col("w.EmploymentStatus").isin("PreHire", "Active", "Leave")
        & (F.col("p.ManagerRequiredFlag") == True)
    )
    .select(
        F.col("w.SnapshotDate").alias("SnapshotDate"),
        F.col("w.EmployeeID").alias("EmployeeID"),
        F.col("w.ManagerEmployeeID").alias("ManagerEmployeeID"),
        "ManagerLookupID",
        "ManagerEmploymentStatus",
        "ManagerPositionID",
        "ManagerEligibleFlag",
    )
)

dq3_reasons = F.filter(
    F.array(
        F.when(F.col("ManagerEmployeeID").isNull(), F.lit("Missing")),
        F.when(F.col("ManagerEmployeeID") == F.col("EmployeeID"), F.lit("SelfReference")),
        F.when(F.col("ManagerLookupID").isNull(), F.lit("NotFound")),
        F.when(
            F.col("ManagerLookupID").isNotNull()
            & ~F.col("ManagerEmploymentStatus").isin("Active", "Leave"),
            F.lit("Inactive"),
        ),
        F.when(
            F.col("ManagerLookupID").isNotNull() & F.col("ManagerPositionID").isNull(),
            F.lit("PositionNotFound"),
        ),
        F.when(
            F.col("ManagerPositionID").isNotNull()
            & (F.coalesce(F.col("ManagerEligibleFlag"), F.lit(False)) == False),
            F.lit("NotEligible"),
        ),
    ),
    lambda item: item.isNotNull(),
)
dq3_base = dq3_base.withColumn("FailureReasons", dq3_reasons)
dq3 = finalize_rule(
    dq3_base,
    "DQ-003",
    F.col("EmployeeID"),
    F.lit("ManagerEmployeeID"),
    F.size("FailureReasons") == 0,
    F.to_json(F.struct("ManagerEmployeeID", "ManagerEmploymentStatus", "ManagerPositionID", "FailureReasons")),
)


# DQ-004 — worker assignment agrees with the position reference.
dq4_base = (
    workers.alias("w")
    .filter(F.col("w.PositionID").isNotNull())
    .join(
        positions.alias("p"),
        (F.col("w.SnapshotDate") == F.col("p.SnapshotDate"))
        & (F.col("w.PositionID") == F.col("p.PositionID")),
        "left",
    )
    .select(
        F.col("w.SnapshotDate").alias("SnapshotDate"),
        F.col("w.EmployeeID").alias("EmployeeID"),
        F.col("w.PositionID").alias("PositionID"),
        F.col("p.PositionID").alias("ReferencePositionID"),
        *[
            F.col(f"w.{name}").alias(f"Observed{name}")
            for name in ["OrgUnitCode", "CostCenterCode", "LocationCode", "CountryCode"]
        ],
        *[
            F.col(f"p.{name}").alias(f"Expected{name}")
            for name in ["OrgUnitCode", "CostCenterCode", "LocationCode", "CountryCode"]
        ],
    )
)

dq4_mismatches = [
    F.when(
        ~F.col(f"Observed{name}").eqNullSafe(F.col(f"Expected{name}")),
        F.lit(name),
    )
    for name in ["OrgUnitCode", "CostCenterCode", "LocationCode", "CountryCode"]
]
dq4_base = dq4_base.withColumn(
    "MismatchFields",
    F.when(
        F.col("ReferencePositionID").isNull(),
        F.array(F.lit("PositionID")),
    ).otherwise(F.filter(F.array(*dq4_mismatches), lambda item: item.isNotNull())),
)
dq4 = finalize_rule(
    dq4_base,
    "DQ-004",
    F.col("EmployeeID"),
    F.lit("PositionID+OrgAssignment"),
    F.size("MismatchFields") == 0,
    F.to_json(F.struct(
        "PositionID",
        "ReferencePositionID",
        "MismatchFields",
        "ObservedOrgUnitCode",
        "ExpectedOrgUnitCode",
        "ObservedCostCenterCode",
        "ExpectedCostCenterCode",
        "ObservedLocationCode",
        "ExpectedLocationCode",
        "ObservedCountryCode",
        "ExpectedCountryCode",
    )),
)


# DQ-005 — active occupancy does not exceed position capacity.
dq5_occupancy = (
    workers
    .filter(
        F.col("EmploymentStatus").isin("PreHire", "Active", "Leave")
        & F.col("PositionID").isNotNull()
    )
    .groupBy("SnapshotDate", "PositionID")
    .agg(
        F.count(F.lit(1)).alias("ObservedOccupants"),
        F.sort_array(F.collect_list("EmployeeID")).alias("EmployeeIDs"),
    )
)
dq5_base = (
    dq5_occupancy.alias("o")
    .join(
        positions.alias("p"),
        (F.col("o.SnapshotDate") == F.col("p.SnapshotDate"))
        & (F.col("o.PositionID") == F.col("p.PositionID")),
        "inner",
    )
    .select(
        F.col("o.SnapshotDate").alias("SnapshotDate"),
        F.col("o.PositionID").alias("PositionID"),
        "ObservedOccupants",
        "EmployeeIDs",
        F.col("p.MaxIncumbents").alias("MaxIncumbents"),
    )
)
dq5 = finalize_rule(
    dq5_base,
    "DQ-005",
    F.col("PositionID"),
    F.lit("PositionID+Occupancy"),
    F.col("ObservedOccupants") <= F.col("MaxIncumbents"),
    F.to_json(F.struct("ObservedOccupants", "MaxIncumbents", "EmployeeIDs")),
)


# DQ-006 — temporal coherence on each canonical employee state.
dq6_invalid_reasons = F.filter(
    F.array(
        F.when(F.col("HireDate").isNull(), F.lit("HireDateMissing")),
        F.when(F.col("HireDate") > F.col("SnapshotDate"), F.lit("HireAfterSnapshot")),
        F.when(F.col("TerminationDate") < F.col("HireDate"), F.lit("TerminationBeforeHire")),
        F.when(
            (F.col("EmploymentStatus") == "Terminated") & F.col("TerminationDate").isNull(),
            F.lit("TerminatedWithoutDate"),
        ),
        F.when(
            (F.col("EmploymentStatus") == "Terminated")
            & (F.col("TerminationDate") > F.col("SnapshotDate")),
            F.lit("TerminationAfterSnapshot"),
        ),
        F.when(
            F.col("EmploymentStatus").isin("Active", "Leave")
            & (F.col("TerminationDate") <= F.col("SnapshotDate")),
            F.lit("ActiveAfterTermination"),
        ),
        F.when(
            (F.col("EmploymentStatus") == "Leave") & F.col("LeaveStartDate").isNull(),
            F.lit("LeaveStartMissing"),
        ),
        F.when(
            (F.col("EmploymentStatus") == "Leave") & F.col("LeaveExpectedEndDate").isNull(),
            F.lit("LeaveEndMissing"),
        ),
        F.when(
            (F.col("EmploymentStatus") == "Leave")
            & (F.col("LeaveStartDate") > F.col("LeaveExpectedEndDate")),
            F.lit("LeaveStartAfterEnd"),
        ),
    ),
    lambda item: item.isNotNull(),
)
dq6_base = workers.withColumn("FailureReasons", dq6_invalid_reasons)
dq6 = finalize_rule(
    dq6_base,
    "DQ-006",
    F.col("EmployeeID"),
    F.lit("EmploymentDates"),
    F.size("FailureReasons") == 0,
    F.to_json(F.struct(
        "EmploymentStatus",
        "HireDate",
        "TerminationDate",
        "LeaveStartDate",
        "LeaveExpectedEndDate",
        "FailureReasons",
    )),
)


# DQ-007 — consume the already validated lifecycle reconstruction.
dq7_operational_severity = F.when(
    F.array_contains(F.col("ActionableMismatchFields"), "EmploymentStatus"),
    F.lit("Critical"),
).otherwise(F.lit("High"))
dq7 = finalize_rule(
    lifecycle_state.filter(F.col("ReconciliationEligibleFlag")),
    "DQ-007",
    F.col("EmployeeID"),
    F.when(
        F.size("ActionableMismatchFields") > 0,
        F.concat_ws(",", "ActionableMismatchFields"),
    ).otherwise(F.lit("LifecycleState")),
    F.col("ReconciliationPassFlag"),
    F.to_json(F.struct(
        "MismatchFields",
        "ActionableMismatchFields",
        "ToleranceAppliedFlag",
        "ObservedEmploymentStatus",
        "ReconstructedEmploymentStatus",
        "ObservedManagerEmployeeID",
        "ReconstructedManagerEmployeeID",
        "ObservedPositionID",
        "ReconstructedPositionID",
        "ObservedOrgUnitCode",
        "ReconstructedOrgUnitCode",
        "ObservedCostCenterCode",
        "ReconstructedCostCenterCode",
        "ObservedLocationCode",
        "ReconstructedLocationCode",
    )),
    dq7_operational_severity,
)


# DQ-008 — freshness using both material update and confirmation timestamps.
dq8_base = (
    workers
    .filter(F.col("EmploymentStatus").isin("PreHire", "Active", "Leave"))
    .withColumn(
        "FreshestDate",
        F.greatest(F.to_date("SourceUpdatedAt"), F.to_date("RecordConfirmedAt")),
    )
)
dq8_base = dq8_base.withColumn(
    "BusinessDaysOld",
    business_days_between(F.col("FreshestDate"), F.col("SnapshotDate")),
)
dq8_pass = (
    F.col("SourceUpdatedAt").isNotNull()
    & F.col("RecordConfirmedAt").isNotNull()
    & (F.col("FreshestDate") <= F.col("SnapshotDate"))
    & (F.col("BusinessDaysOld") <= 5)
)
dq8 = finalize_rule(
    dq8_base,
    "DQ-008",
    F.col("EmployeeID"),
    F.lit("SourceUpdatedAt+RecordConfirmedAt"),
    dq8_pass,
    F.to_json(F.struct(
        "SourceUpdatedAt",
        "RecordConfirmedAt",
        "FreshestDate",
        "BusinessDaysOld",
    )),
)


rule_results = reduce(
    lambda left, right: left.unionByName(right),
    [dq1, dq2, dq3, dq4, dq5, dq6, dq7, dq8],
).persist()


# Validate rule counts against the independent synthetic manifest.
manifest = json.loads(notebookutils.fs.head(MANIFEST_PATH, 1_000_000))
expected_quality = manifest["quality_evaluation"]["by_snapshot"]

observed_quality = {}
for row in (
    rule_results
    .groupBy("SnapshotDate", "RuleCode")
    .agg(
        F.sum(F.col("EligibleFlag").cast("long")).alias("eligible"),
        F.sum(F.when(F.col("PassFlag") == True, 1).otherwise(0)).alias("passed"),
        F.sum(F.when(F.col("PassFlag") == False, 1).otherwise(0)).alias("failed"),
    )
    .collect()
):
    snapshot = row["SnapshotDate"].isoformat()
    observed_quality.setdefault(snapshot, {})[row["RuleCode"]] = {
        "eligible": row["eligible"],
        "passed": row["passed"],
        "failed": row["failed"],
    }

assert observed_quality == expected_quality, {
    "expected": expected_quality,
    "observed": observed_quality,
}

assert rule_results.count() == rule_results.select("RuleResultID").distinct().count()


exceptions = (
    rule_results
    .filter(F.col("EligibleFlag") & (F.col("PassFlag") == False))
    .withColumn(
        "ExceptionInstanceID",
        F.sha2(F.concat_ws("|", "RunID", "RuleResultID"), 256),
    )
    .withColumn(
        "ExceptionFingerprint",
        F.sha2(F.concat_ws(
            "|",
            "RuleCode",
            "SourceSystem",
            F.col("SnapshotDate").cast("string"),
            "BusinessKey",
            "FieldScope",
        ), 256),
    )
    .withColumn(
        "RecurrenceKey",
        F.sha2(F.concat_ws(
            "|",
            "RuleCode",
            "SourceSystem",
            "BusinessKey",
            "FieldScope",
        ), 256),
    )
    .select(
        "ExceptionInstanceID",
        "ExceptionFingerprint",
        "RecurrenceKey",
        "RunID",
        "RuleResultID",
        "RuleCode",
        "RuleName",
        "QualityDimension",
        "SnapshotDate",
        "SourceSystem",
        "BusinessKey",
        "FieldScope",
        "OperationalSeverity",
        "SlaBusinessDays",
        "OwnerDomain",
        "ObservedValue",
        "ExpectedCondition",
        "EvaluatedAt",
    )
).persist()

assert exceptions.count() == rule_results.filter(F.col("PassFlag") == False).count()
assert exceptions.count() == exceptions.select("ExceptionInstanceID").distinct().count()


rule_scores = (
    rule_results
    .groupBy(
        "SnapshotDate",
        "RuleCode",
        "RuleName",
        "QualityDimension",
        "SourceSystem",
    )
    .agg(
        F.count(F.lit(1)).alias("EligibleChecks"),
        F.sum(F.when(F.col("PassFlag") == True, 1).otherwise(0)).alias("PassedChecks"),
        F.sum(F.when(F.col("PassFlag") == False, 1).otherwise(0)).alias("FailedChecks"),
        F.sum("SeverityWeight").alias("WeightedEligible"),
        F.sum(
            F.when(F.col("PassFlag") == True, F.col("SeverityWeight")).otherwise(0)
        ).alias("WeightedPassed"),
        F.countDistinct("BusinessKey").alias("RecordsEvaluated"),
        F.countDistinct(
            F.when(F.col("PassFlag") == False, F.col("BusinessKey"))
        ).alias("RecordsWithException"),
    )
    .withColumn("AggregationLevel", F.lit("RULE"))
    .withColumn(
        "DQScore",
        F.round(100 * F.col("WeightedPassed") / F.col("WeightedEligible"), 1),
    )
)

overall_scores = (
    rule_results
    .groupBy("SnapshotDate")
    .agg(
        F.count(F.lit(1)).alias("EligibleChecks"),
        F.sum(F.when(F.col("PassFlag") == True, 1).otherwise(0)).alias("PassedChecks"),
        F.sum(F.when(F.col("PassFlag") == False, 1).otherwise(0)).alias("FailedChecks"),
        F.sum("SeverityWeight").alias("WeightedEligible"),
        F.sum(
            F.when(F.col("PassFlag") == True, F.col("SeverityWeight")).otherwise(0)
        ).alias("WeightedPassed"),
        F.countDistinct("BusinessKey").alias("RecordsEvaluated"),
        F.countDistinct(
            F.when(F.col("PassFlag") == False, F.col("BusinessKey"))
        ).alias("RecordsWithException"),
    )
    .withColumn("RuleCode", F.lit("ALL"))
    .withColumn("RuleName", F.lit("Overall data quality"))
    .withColumn("QualityDimension", F.lit("All"))
    .withColumn("SourceSystem", F.lit("ALL"))
    .withColumn("AggregationLevel", F.lit("OVERALL"))
    .withColumn(
        "DQScore",
        F.round(100 * F.col("WeightedPassed") / F.col("WeightedEligible"), 1),
    )
)

score_columns = [
    "SnapshotDate",
    "AggregationLevel",
    "RuleCode",
    "RuleName",
    "QualityDimension",
    "SourceSystem",
    "EligibleChecks",
    "PassedChecks",
    "FailedChecks",
    "WeightedEligible",
    "WeightedPassed",
    "RecordsEvaluated",
    "RecordsWithException",
    "DQScore",
]

scores = (
    overall_scores.select(score_columns)
    .unionByName(rule_scores.select(score_columns))
    .withColumn("RunID", F.lit(RUN_ID))
    .withColumn("CalculatedAt", F.current_timestamp())
)

observed_scores = {
    row["SnapshotDate"].isoformat(): float(row["DQScore"])
    for row in scores.filter(F.col("AggregationLevel") == "OVERALL").collect()
}
expected_scores = {
    snapshot: float(score)
    for snapshot, score in manifest["quality_evaluation"]["score_by_snapshot"].items()
}
assert observed_scores == expected_scores, {
    "expected": expected_scores,
    "observed": observed_scores,
}


result_count = rule_results.count()
exception_count = exceptions.count()

run_audit = spark.createDataFrame([(
    RUN_ID,
    6,
    8,
    result_count,
    exception_count,
    True,
    "PASS",
)], [
    "RunID",
    "SnapshotCount",
    "RuleCount",
    "RuleResultCount",
    "ExceptionCount",
    "ManifestValidatedFlag",
    "RunStatus",
]).withColumn("CompletedAt", F.current_timestamp())


for frame, table_name, partition_column in [
    (rule_results, RESULT_TABLE, "SnapshotDate"),
    (exceptions, EXCEPTION_TABLE, "SnapshotDate"),
    (scores, SCORE_TABLE, "SnapshotDate"),
]:
    (
        frame.write
        .format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .partitionBy(partition_column)
        .saveAsTable(table_name)
    )

(
    run_audit.write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(AUDIT_TABLE)
)


assert spark.table(RESULT_TABLE).count() == result_count
assert spark.table(EXCEPTION_TABLE).count() == exception_count
assert spark.table(AUDIT_TABLE).filter(F.col("RunStatus") == "PASS").count() == 1

display(
    spark.table(SCORE_TABLE)
    .filter(F.col("AggregationLevel") == "OVERALL")
    .select("SnapshotDate", "EligibleChecks", "FailedChecks", "RecordsWithException", "DQScore")
    .orderBy("SnapshotDate")
)
print("GOLD_DQ_ENGINE: PASS")
