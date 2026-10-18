/*
Purpose:
  Export a small, deterministic Dataverse demo load from the Fabric Gold layer.

Expected result:
  Eight rows: one exception for each DQ-001 through DQ-008 rule from the
  latest project snapshot (2026-06-30).

Run this query in the Lakehouse SQL analytics endpoint and download the
result grid as CSV. The aliases intentionally match the Dataverse display
names to simplify import mapping.
*/

WITH ranked_exceptions AS (
    SELECT
        ExceptionInstanceID,
        ExceptionFingerprint,
        RecurrenceKey,
        RunID,
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
        EvaluatedAt,
        ROW_NUMBER() OVER (
            PARTITION BY RuleCode
            ORDER BY ExceptionInstanceID
        ) AS rule_row_number
    FROM dbo.gold_dq_exception
    WHERE SnapshotDate = CAST('2026-06-30' AS date)
)
SELECT
    CONCAT(
        RuleCode,
        ' | ',
        BusinessKey,
        ' | ',
        CONVERT(varchar(10), SnapshotDate, 23)
    ) AS [Exception Label],
    ExceptionInstanceID AS [Exception Instance ID],
    ExceptionFingerprint AS [Exception Fingerprint],
    RecurrenceKey AS [Recurrence Key],
    RunID AS [Fabric Run ID],
    RuleCode AS [Rule Code],
    RuleName AS [Rule Name],
    QualityDimension AS [Quality Dimension],
    CONVERT(char(10), SnapshotDate, 23) AS [Snapshot Date],
    SourceSystem AS [Source System],
    BusinessKey AS [Business Key],
    FieldScope AS [Field Scope],
    OperationalSeverity AS [Operational Severity],
    SlaBusinessDays AS [SLA Business Days],
    OwnerDomain AS [Owner Domain],
    ObservedValue AS [Observed Value],
    ExpectedCondition AS [Expected Condition],
    CONCAT(CONVERT(varchar(19), EvaluatedAt, 126), 'Z') AS [Fabric Evaluated At]
FROM ranked_exceptions
WHERE rule_row_number = 1
ORDER BY RuleCode;
