-- Checkpoint esperado después de ejecutar 01_create_gold_consumption_views.sql.
-- El resultado debe ser una única fila con los valores documentados abajo.

SELECT
    (
        SELECT COUNT(*)
        FROM sys.views
        WHERE schema_id = SCHEMA_ID('dbo')
          AND name IN (
              'vw_dq_score_trend',
              'vw_dq_rule_performance',
              'vw_dq_exception_register',
              'vw_dq_latest_snapshot'
          )
    ) AS ConsumptionViews,
    (SELECT COUNT(*) FROM dbo.vw_dq_score_trend) AS SnapshotRows,
    (SELECT COUNT(*) FROM dbo.vw_dq_rule_performance) AS RuleRows,
    (SELECT COUNT(*) FROM dbo.vw_dq_exception_register) AS ExceptionRows,
    (SELECT MAX(SnapshotDate) FROM dbo.vw_dq_latest_snapshot) AS LatestSnapshotDate,
    (SELECT MAX(DQScore) FROM dbo.vw_dq_latest_snapshot) AS LatestDQScore,
    (SELECT MAX(EligibleChecks) FROM dbo.vw_dq_latest_snapshot) AS LatestEligibleChecks,
    (SELECT MAX(FailedChecks) FROM dbo.vw_dq_latest_snapshot) AS LatestFailedChecks,
    (SELECT MAX(RecordsWithException) FROM dbo.vw_dq_latest_snapshot) AS LatestRecordsWithException;

-- Valores esperados:
-- ConsumptionViews            = 4
-- SnapshotRows                = 6
-- RuleRows                    = 48
-- ExceptionRows               = 923
-- LatestSnapshotDate          = 2026-06-30
-- LatestDQScore               = 98.9
-- LatestEligibleChecks        = 11272
-- LatestFailedChecks          = 113
-- LatestRecordsWithException  = 78
