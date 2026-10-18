-- HR Data Quality & Employee Lifecycle Workbench
-- Capa de consumo del SQL analytics endpoint de lh_hr_data_quality_dev.
-- Las tablas Delta siguen siendo administradas por Spark; estas vistas no duplican datos.

CREATE OR ALTER VIEW dbo.vw_dq_score_trend
AS
SELECT
    SnapshotDate,
    EligibleChecks,
    PassedChecks,
    FailedChecks,
    WeightedEligible,
    WeightedPassed,
    RecordsEvaluated,
    RecordsWithException,
    DQScore,
    RunID,
    CalculatedAt
FROM dbo.gold_dq_score_snapshot
WHERE AggregationLevel = 'OVERALL';
GO

CREATE OR ALTER VIEW dbo.vw_dq_rule_performance
AS
SELECT
    SnapshotDate,
    RuleCode,
    RuleName,
    QualityDimension,
    SourceSystem,
    EligibleChecks,
    PassedChecks,
    FailedChecks,
    WeightedEligible,
    WeightedPassed,
    RecordsEvaluated,
    RecordsWithException,
    DQScore,
    RunID,
    CalculatedAt
FROM dbo.gold_dq_score_snapshot
WHERE AggregationLevel = 'RULE';
GO

CREATE OR ALTER VIEW dbo.vw_dq_exception_register
AS
SELECT
    ExceptionInstanceID,
    ExceptionFingerprint,
    RecurrenceKey,
    RunID,
    RuleResultID,
    RuleCode,
    RuleName,
    QualityDimension,
    SnapshotDate,
    SourceSystem,
    BusinessKey,
    FieldScope,
    OperationalSeverity,
    SlaBusinessDays,
    OwnerDomain,
    ObservedValue,
    ExpectedCondition,
    EvaluatedAt
FROM dbo.gold_dq_exception;
GO

CREATE OR ALTER VIEW dbo.vw_dq_latest_snapshot
AS
WITH LatestSnapshot AS (
    SELECT MAX(SnapshotDate) AS SnapshotDate
    FROM dbo.gold_dq_score_snapshot
    WHERE AggregationLevel = 'OVERALL'
)
SELECT
    score.SnapshotDate,
    score.EligibleChecks,
    score.PassedChecks,
    score.FailedChecks,
    score.RecordsEvaluated,
    score.RecordsWithException,
    score.DQScore,
    score.RunID,
    score.CalculatedAt
FROM dbo.gold_dq_score_snapshot AS score
INNER JOIN LatestSnapshot AS latest
    ON latest.SnapshotDate = score.SnapshotDate
WHERE score.AggregationLevel = 'OVERALL';
GO
