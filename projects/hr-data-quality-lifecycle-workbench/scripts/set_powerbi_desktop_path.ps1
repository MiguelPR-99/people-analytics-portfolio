[CmdletBinding()]
param(
    [switch]$NoPersist
)

$ErrorActionPreference = 'Stop'

$desktopPath = Get-Process PBIDesktop -ErrorAction SilentlyContinue |
    Where-Object { $_.Path -and (Test-Path -LiteralPath $_.Path) } |
    Select-Object -First 1 -ExpandProperty Path

if (-not $desktopPath) {
    $classicCandidates = @(
        "$env:ProgramFiles\Microsoft Power BI Desktop\bin\PBIDesktop.exe",
        "${env:ProgramFiles(x86)}\Microsoft Power BI Desktop\bin\PBIDesktop.exe"
    )

    $desktopPath = $classicCandidates |
        Where-Object { $_ -and (Test-Path -LiteralPath $_) } |
        Select-Object -First 1
}

if (-not $desktopPath) {
    $package = Get-AppxPackage -Name 'Microsoft.MicrosoftPowerBIDesktop' -ErrorAction SilentlyContinue |
        Sort-Object Version -Descending |
        Select-Object -First 1

    if ($package) {
        $storeCandidate = Join-Path $package.InstallLocation 'bin\PBIDesktop.exe'
        if (Test-Path -LiteralPath $storeCandidate) {
            $desktopPath = $storeCandidate
        }
    }
}

if (-not $desktopPath) {
    throw 'Power BI Desktop was not found. Start Power BI Desktop once and rerun this script.'
}

$desktopPath = [System.IO.Path]::GetFullPath($desktopPath)
$env:PBI_DESKTOP_PATH = $desktopPath

if (-not $NoPersist) {
    [Environment]::SetEnvironmentVariable('PBI_DESKTOP_PATH', $desktopPath, 'User')
}

[pscustomobject]@{
    Path = $desktopPath
    Exists = Test-Path -LiteralPath $desktopPath
    Scope = if ($NoPersist) { 'Current process' } else { 'Current process and user' }
}
