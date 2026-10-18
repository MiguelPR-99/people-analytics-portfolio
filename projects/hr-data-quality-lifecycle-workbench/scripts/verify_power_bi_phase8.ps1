[CmdletBinding()]
param(
    [string]$ToolRoot = 'D:\PBI-Agentic'
)

$ErrorActionPreference = 'Stop'
$checks = [System.Collections.Generic.List[object]]::new()

function Add-Check {
    param(
        [string]$Name,
        [bool]$Passed,
        [string]$Detail
    )

    $checks.Add([pscustomobject]@{
        Check = $Name
        Result = if ($Passed) { 'PASS' } else { 'FAIL' }
        Detail = $Detail
    })
}

function Invoke-VersionCheck {
    param(
        [string]$Name,
        [string]$Executable,
        [string[]]$Arguments,
        [string]$Expected
    )

    if (-not (Test-Path -LiteralPath $Executable)) {
        Add-Check -Name $Name -Passed $false -Detail "Missing: $Executable"
        return
    }

    try {
        $output = (& $Executable @Arguments 2>&1 | Out-String).Trim()
        Add-Check -Name $Name -Passed ($output -match [regex]::Escape($Expected)) -Detail ($output -replace "`r?`n", ' ')
    }
    catch {
        Add-Check -Name $Name -Passed $false -Detail $_.Exception.Message
    }
}

$expectedRoot = [System.IO.Path]::GetFullPath('D:\PBI-Agentic')
$actualRoot = [System.IO.Path]::GetFullPath($ToolRoot)
if ($actualRoot -ne $expectedRoot) {
    throw 'This verifier is restricted to D:\PBI-Agentic.'
}

Invoke-VersionCheck -Name 'Azure CLI' -Executable "$ToolRoot\bin\az.cmd" -Arguments @('version') -Expected '2.91.0'
Invoke-VersionCheck -Name 'Fabric CLI' -Executable "$ToolRoot\bin\fab.cmd" -Arguments @('--version') -Expected '1.7.0'
Invoke-VersionCheck -Name 'APM CLI' -Executable "$ToolRoot\python\Scripts\apm.exe" -Arguments @('--version') -Expected '0.33.0'
Invoke-VersionCheck -Name 'Report Author CLI' -Executable "$ToolRoot\npm\node_modules\.bin\powerbi-report-author.cmd" -Arguments @('--version') -Expected '0.5.0'
Invoke-VersionCheck -Name 'Modeling MCP package' -Executable 'D:\npm.cmd' -Arguments @('list','--prefix',"$ToolRoot\npm",'@microsoft/powerbi-modeling-mcp','--depth=0') -Expected '@microsoft/powerbi-modeling-mcp@1.0.0'

$doctorPath = "$ToolRoot\npm\node_modules\.bin\powerbi-report-author.cmd"
try {
    $doctor = (& $doctorPath doctor --pretty 2>&1 | Out-String)
    Add-Check -Name 'Report Author doctor' -Passed ($doctor -match '"ok": true') -Detail 'Node, AJV and visual metadata provider'
}
catch {
    Add-Check -Name 'Report Author doctor' -Passed $false -Detail $_.Exception.Message
}

$skills = @('semantic-model-authoring','powerbi-report-cli')
foreach ($skill in $skills) {
    $skillPath = Join-Path (Join-Path $env:USERPROFILE '.agents\skills') $skill
    $item = Get-Item -LiteralPath $skillPath -Force -ErrorAction SilentlyContinue
    $target = if ($item) { [string]$item.Target } else { '' }
    Add-Check -Name "Skill $skill" -Passed ($item -and $target.StartsWith($ToolRoot, [System.StringComparison]::OrdinalIgnoreCase)) -Detail $target
}

$codexConfig = Join-Path $env:USERPROFILE '.codex\config.toml'
$configText = if (Test-Path -LiteralPath $codexConfig) { Get-Content -Raw -LiteralPath $codexConfig } else { '' }
$mcpConfigured = $configText -match '\[mcp_servers\.powerbi-modeling\]' -and $configText -match [regex]::Escape("$ToolRoot\npm\node_modules\@microsoft\powerbi-modeling-mcp\index.js")
Add-Check -Name 'Codex Modeling MCP' -Passed $mcpConfigured -Detail 'Local stdio server references D:\PBI-Agentic'

$desktop = Get-AppxPackage -Name 'Microsoft.MicrosoftPowerBIDesktop' -ErrorAction SilentlyContinue
$desktopStart = Get-StartApps -ErrorAction SilentlyContinue | Where-Object { $_.AppID -like 'Microsoft.MicrosoftPowerBIDesktop*' } | Select-Object -First 1
$desktopDetected = ($null -ne $desktop) -or ($null -ne $desktopStart)
$desktopDetail = if ($desktop) { [string]$desktop.Version } elseif ($desktopStart) { [string]$desktopStart.AppID } else { 'Package and Start entry not detected' }
Add-Check -Name 'Power BI Desktop' -Passed $desktopDetected -Detail $desktopDetail

$desktopCliPath = $env:PBI_DESKTOP_PATH
if (-not $desktopCliPath) {
    $desktopCliPath = [Environment]::GetEnvironmentVariable('PBI_DESKTOP_PATH', 'User')
}
if (-not $desktopCliPath) {
    $desktopCliPath = Get-Process PBIDesktop -ErrorAction SilentlyContinue |
        Where-Object { $_.Path -and (Test-Path -LiteralPath $_.Path) } |
        Select-Object -First 1 -ExpandProperty Path
}
$desktopCliReady = $desktopCliPath -and (Test-Path -LiteralPath $desktopCliPath)
Add-Check -Name 'Power BI Desktop CLI path' -Passed $desktopCliReady -Detail $(if ($desktopCliPath) { $desktopCliPath } else { 'PBI_DESKTOP_PATH is not set for the user' })

$dateTablePath = Join-Path $PSScriptRoot '..\power-bi\HRDataQualityScorecard.SemanticModel\definition\tables\Fecha.tmdl'
$dateTableText = if (Test-Path -LiteralPath $dateTablePath) { Get-Content -Raw -LiteralPath $dateTablePath } else { '' }
$dateTypeIsExplicit = $dateTableText -match "column 'Fecha de snapshot'\s+dataType: dateTime" -and
    $dateTableText -match 'TypedCalendar = Table\.TransformColumnTypes\(Calendar, \{\{\"Fecha de snapshot\", type date\}\}'
Add-Check -Name 'Calendar date type contract' -Passed $dateTypeIsExplicit -Detail 'Fecha de snapshot is DateTime in TMDL and explicitly typed as date in Power Query'

$lockPath = "$ToolRoot\fabric-skills\apm.lock.yaml"
$lockText = if (Test-Path -LiteralPath $lockPath) { Get-Content -Raw -LiteralPath $lockPath } else { '' }
Add-Check -Name 'Pinned Fabric skills' -Passed ($lockText -match 'bc42aaf734771bf752c1d7082dd91e5a6ca72b9f') -Detail 'Microsoft skills-for-fabric pinned commit'

$checks | Format-Table -AutoSize -Wrap

$failed = @($checks | Where-Object Result -eq 'FAIL')
if ($failed.Count -gt 0) {
    throw "$($failed.Count) Phase 8 local readiness check(s) failed."
}

Write-Output "Phase 8 local readiness: PASS ($($checks.Count)/$($checks.Count))."
