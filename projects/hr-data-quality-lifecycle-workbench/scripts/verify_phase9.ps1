[CmdletBinding()]
param(
    [switch]$IncludeTenantE2E,
    [switch]$IncludeVisual,
    [string]$MutationBusinessKey,
    [string]$ReportPath = 'evidence/phase-9/local-regression.json'
)

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$repositoryRoot = [System.IO.Path]::GetFullPath((Join-Path $projectRoot '../..'))
$results = [System.Collections.Generic.List[object]]::new()
$publicationBlockers = [System.Collections.Generic.List[string]]::new()

function Add-Result {
    param(
        [string]$Name,
        [string]$Status,
        [double]$DurationSeconds,
        [string]$Detail
    )

    $results.Add([pscustomobject]@{
        step = $Name
        status = $Status
        durationSeconds = $DurationSeconds
        detail = $Detail
    })
}

function Invoke-Step {
    param(
        [string]$Name,
        [string]$WorkingDirectory,
        [string]$Command,
        [string[]]$Arguments
    )

    Write-Host "`n==> $Name" -ForegroundColor Cyan
    $startedAt = Get-Date
    Push-Location -LiteralPath $WorkingDirectory
    try {
        $previousErrorActionPreference = $ErrorActionPreference
        $ErrorActionPreference = 'Continue'
        $output = (& $Command @Arguments 2>&1 | Out-String).Trim()
        $nativeExitCode = $LASTEXITCODE
        $ErrorActionPreference = $previousErrorActionPreference
        if ($output) { Write-Host $output }
        if ($nativeExitCode -ne 0) {
            throw "$Name failed with exit code $nativeExitCode."
        }
        Add-Result -Name $Name -Status 'passed' `
            -DurationSeconds ([math]::Round(((Get-Date) - $startedAt).TotalSeconds, 2)) `
            -Detail 'Completed without errors.'
    }
    finally {
        $ErrorActionPreference = 'Stop'
        Pop-Location
    }
}

Invoke-Step -Name 'Synthetic data regression' -WorkingDirectory $projectRoot `
    -Command 'cmd.exe' -Arguments @('/d','/s','/c','python -m unittest discover -s scripts/tests -v 2>&1')

$platformArguments = @(
    '-NoProfile',
    '-ExecutionPolicy','Bypass',
    '-File',(Join-Path $projectRoot 'scripts/verify_power_platform_phase7.ps1')
)
if ($IncludeTenantE2E) { $platformArguments += '-IncludeE2E' }
if ($IncludeVisual) { $platformArguments += '-IncludeVisual' }
if (-not [string]::IsNullOrWhiteSpace($MutationBusinessKey)) {
    $platformArguments += @('-MutationBusinessKey',$MutationBusinessKey)
}
Invoke-Step -Name 'Power Platform regression' -WorkingDirectory $projectRoot `
    -Command 'powershell' -Arguments $platformArguments

Invoke-Step -Name 'Power BI local readiness' -WorkingDirectory $projectRoot `
    -Command 'powershell' -Arguments @(
        '-NoProfile',
        '-ExecutionPolicy','Bypass',
        '-File',(Join-Path $projectRoot 'scripts/verify_power_bi_phase8.ps1')
    )

Write-Host "`n==> Power BI PBIR validation" -ForegroundColor Cyan
$validationStarted = Get-Date
Push-Location -LiteralPath $projectRoot
try {
    $validationOutput = (& powerbi-report-author validate '.\power-bi\HRDataQualityScorecard.Report' 2>&1 | Out-String).Trim()
    if ($LASTEXITCODE -ne 0) {
        throw "Power BI PBIR validation failed with exit code $LASTEXITCODE."
    }
    $validation = $validationOutput | ConvertFrom-Json
    $errorCount = [int]$validation.data.errorCount
    $warningCount = [int]$validation.data.warningCount
    if ($errorCount -ne 0) {
        throw "Power BI PBIR validation returned $errorCount error(s)."
    }
    $validationStatus = if ($warningCount -eq 0) { 'passed' } else { 'passed_with_warnings' }
    Add-Result -Name 'Power BI PBIR validation' -Status $validationStatus `
        -DurationSeconds ([math]::Round(((Get-Date) - $validationStarted).TotalSeconds, 2)) `
        -Detail "0 errors; $warningCount warning(s)."
}
finally {
    Pop-Location
}

Write-Host "`n==> Repository hygiene" -ForegroundColor Cyan
$hygieneStarted = Get-Date
$localOnlyPaths = @(
    'projects/hr-data-quality-lifecycle-workbench/power-apps/tests/e2e/.env',
    'projects/hr-data-quality-lifecycle-workbench/power-apps/tests/e2e/.auth/state.json',
    'projects/hr-data-quality-lifecycle-workbench/power-bi/HRDataQualityScorecard.Report/.pbi/localSettings.json',
    'projects/hr-data-quality-lifecycle-workbench/power-bi/HRDataQualityScorecard.SemanticModel/.pbi/cache.abf'
)
$notIgnored = [System.Collections.Generic.List[string]]::new()
foreach ($relativePath in $localOnlyPaths) {
    & git -C $repositoryRoot check-ignore -q -- $relativePath
    if ($LASTEXITCODE -ne 0) { $notIgnored.Add($relativePath) }
}
if ($notIgnored.Count -gt 0) {
    throw "Local-only paths are not ignored: $($notIgnored -join ', ')"
}
Add-Result -Name 'Repository hygiene' -Status 'passed' `
    -DurationSeconds ([math]::Round(((Get-Date) - $hygieneStarted).TotalSeconds, 2)) `
    -Detail 'Credentials, authentication state, Power BI cache and local settings are ignored.'

$expressionsPath = Join-Path $projectRoot 'power-bi/HRDataQualityScorecard.SemanticModel/definition/expressions.tmdl'
$expressionsText = Get-Content -Raw -LiteralPath $expressionsPath
$safeParameterDefaults = @(
    'contoso.datawarehouse.fabric.microsoft.com',
    'lh_hr_data_quality',
    'https://contoso.crm.dynamics.com'
)
foreach ($safeDefault in $safeParameterDefaults) {
    if (-not $expressionsText.Contains($safeDefault)) {
        $publicationBlockers.Add("Public Power BI parameter default is missing: $safeDefault")
    }
}
$tenantIdentifierMatches = (& git -C $repositoryRoot grep -n -I -E `
    'org[0-9a-f]{8}\.crm\.dynamics\.com|[a-z0-9]{20,}-[a-z0-9]{20,}\.datawarehouse\.fabric\.microsoft\.com|@iberoleon' -- `
    'projects/hr-data-quality-lifecycle-workbench' `
    ':(exclude)projects/hr-data-quality-lifecycle-workbench/scripts/verify_phase9.ps1' 2>$null | Out-String).Trim()
if ($LASTEXITCODE -eq 0 -and $tenantIdentifierMatches) {
    $publicationBlockers.Add('Remove institutional tenant identifiers from tracked text files.')
}
if (-not (Test-Path -LiteralPath (Join-Path $projectRoot 'README.md'))) {
    $publicationBlockers.Add('Create the project README in English.')
}
if (-not (Test-Path -LiteralPath (Join-Path $projectRoot 'README.es.md'))) {
    $publicationBlockers.Add('Create the project README in Spanish.')
}
$videoEvidence = @(Get-ChildItem -LiteralPath (Join-Path $projectRoot 'evidence/phase-9') -File -ErrorAction SilentlyContinue |
    Where-Object Extension -in @('.mp4','.webm'))
if (-not (Test-Path -LiteralPath (Join-Path $projectRoot 'evidence/phase-9/evidence-manifest.es.md'))) {
    $publicationBlockers.Add('Create the Spanish public evidence manifest.')
}
if (-not (Test-Path -LiteralPath (Join-Path $projectRoot 'evidence/phase-9/evidence-manifest.md'))) {
    $publicationBlockers.Add('Create the English public evidence manifest.')
}
$overallStatus = if ($publicationBlockers.Count -eq 0) { 'passed' } else { 'local_passed_publication_blocked' }
$summary = [pscustomobject]@{
    generatedAt = (Get-Date).ToUniversalTime().ToString('o')
    project = 'HR Data Quality & Lifecycle Workbench'
    gate = 'Phase 9'
    status = $overallStatus
    tenantE2EExecuted = [bool]$IncludeTenantE2E
    visualRegressionExecuted = [bool]$IncludeVisual
    mutationExecuted = -not [string]::IsNullOrWhiteSpace($MutationBusinessKey)
    optionalVideoRecorded = $videoEvidence.Count -gt 0
    steps = $results
    publicationBlockers = $publicationBlockers
}

$resolvedReportPath = if ([System.IO.Path]::IsPathRooted($ReportPath)) {
    $ReportPath
}
else {
    Join-Path $projectRoot $ReportPath
}
$reportDirectory = Split-Path -Parent $resolvedReportPath
if (-not (Test-Path -LiteralPath $reportDirectory)) {
    New-Item -ItemType Directory -Path $reportDirectory -Force | Out-Null
}
$summary | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $resolvedReportPath -Encoding utf8

Write-Host "`nPhase 9 local regression: PASS." -ForegroundColor Green
if ($publicationBlockers.Count -gt 0) {
    Write-Host "Publication remains blocked by $($publicationBlockers.Count) item(s)." -ForegroundColor Yellow
}
elseif ($videoEvidence.Count -eq 0) {
    Write-Host 'Publication gate passed. The portfolio video remains an optional follow-up.' -ForegroundColor Yellow
}
Write-Host "Report written to $resolvedReportPath" -ForegroundColor Green
$summary | ConvertTo-Json -Depth 6

