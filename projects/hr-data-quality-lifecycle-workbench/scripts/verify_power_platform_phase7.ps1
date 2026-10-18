[CmdletBinding()]
param(
    [switch]$IncludeE2E,
    [switch]$IncludeVisual,
    [string]$MutationBusinessKey,
    [string]$ReportPath
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$pageRoot = Join-Path $projectRoot "power-apps/generative-pages/dq-command-center"
$e2eRoot = Join-Path $projectRoot "power-apps/tests/e2e"
$results = [System.Collections.Generic.List[object]]::new()

function Invoke-GateStep {
    param(
        [Parameter(Mandatory)] [string]$Name,
        [Parameter(Mandatory)] [string]$WorkingDirectory,
        [Parameter(Mandatory)] [string]$Command,
        [Parameter(Mandatory)] [string[]]$Arguments
    )

    Write-Host "`n==> $Name" -ForegroundColor Cyan
    $startedAt = Get-Date
    Push-Location -LiteralPath $WorkingDirectory
    try {
        & $Command @Arguments
        if ($LASTEXITCODE -ne 0) {
            throw "$Name failed with exit code $LASTEXITCODE."
        }
    }
    finally {
        Pop-Location
    }

    $results.Add([pscustomobject]@{
        step = $Name
        status = "passed"
        durationSeconds = [math]::Round(((Get-Date) - $startedAt).TotalSeconds, 2)
    })
}

if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    throw "npm is required but was not found in PATH."
}

if (-not (Test-Path -LiteralPath (Join-Path $pageRoot "node_modules"))) {
    throw "Dependencies are missing in $pageRoot. Run npm ci there first."
}

Invoke-GateStep -Name "Generative Page typecheck and component tests" `
    -WorkingDirectory $pageRoot -Command "npm" -Arguments @("run", "verify")

$needsBrowser = $IncludeE2E -or $IncludeVisual -or -not [string]::IsNullOrWhiteSpace($MutationBusinessKey)
if ($needsBrowser) {
    if (-not (Test-Path -LiteralPath (Join-Path $e2eRoot "node_modules"))) {
        throw "E2E dependencies are missing in $e2eRoot. Run npm ci there first."
    }
    if (-not (Test-Path -LiteralPath (Join-Path $e2eRoot ".env"))) {
        throw "The E2E .env file is missing. Copy .env.example to .env and configure it."
    }
    if (-not (Test-Path -LiteralPath (Join-Path $e2eRoot ".auth/state.json"))) {
        throw "The saved Power Apps session is missing. Run npm run auth in $e2eRoot."
    }
}

if ($IncludeE2E) {
    Invoke-GateStep -Name "Published Power Apps smoke tests" `
        -WorkingDirectory $e2eRoot -Command "npm" -Arguments @("run", "test:smoke")
}

if ($IncludeVisual) {
    Invoke-GateStep -Name "Published Power Apps visual regression" `
        -WorkingDirectory $e2eRoot -Command "npm" -Arguments @("run", "test:visual")
}

if (-not [string]::IsNullOrWhiteSpace($MutationBusinessKey)) {
    $previousBusinessKey = $env:DQ_CREATE_CASE_BUSINESS_KEY
    try {
        $env:DQ_CREATE_CASE_BUSINESS_KEY = $MutationBusinessKey
        Invoke-GateStep -Name "Published Power Apps case-creation test" `
            -WorkingDirectory $e2eRoot -Command "npm" -Arguments @("run", "test:mutation")
    }
    finally {
        $env:DQ_CREATE_CASE_BUSINESS_KEY = $previousBusinessKey
    }
}

$summary = [pscustomobject]@{
    generatedAt = (Get-Date).ToUniversalTime().ToString("o")
    project = "HR Data Quality & Lifecycle Workbench"
    gate = "Power Platform Phase 7"
    status = "passed"
    browserVerification = [bool]$needsBrowser
    mutationExecuted = -not [string]::IsNullOrWhiteSpace($MutationBusinessKey)
    steps = $results
}

if (-not [string]::IsNullOrWhiteSpace($ReportPath)) {
    $resolvedReportPath = if ([System.IO.Path]::IsPathRooted($ReportPath)) {
        $ReportPath
    }
    else {
        Join-Path $projectRoot $ReportPath
    }
    $reportDirectory = Split-Path -Parent $resolvedReportPath
    if ($reportDirectory -and -not (Test-Path -LiteralPath $reportDirectory)) {
        New-Item -ItemType Directory -Path $reportDirectory -Force | Out-Null
    }
    $summary | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $resolvedReportPath -Encoding utf8
    Write-Host "`nReport written to $resolvedReportPath" -ForegroundColor Green
}

Write-Host "`nPhase 7 local verification passed." -ForegroundColor Green
$summary | ConvertTo-Json -Depth 5
