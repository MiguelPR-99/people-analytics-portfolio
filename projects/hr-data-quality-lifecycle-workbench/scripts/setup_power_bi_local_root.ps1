[CmdletBinding()]
param(
    [string]$TargetPath = 'D:\PBI-Agentic',
    [string]$Account = "$env:USERDOMAIN\$env:USERNAME"
)

$ErrorActionPreference = 'Stop'

if (-not ([System.IO.Path]::GetFullPath($TargetPath) -eq 'D:\PBI-Agentic')) {
    throw "Refusing to modify permissions outside D:\PBI-Agentic."
}

New-Item -ItemType Directory -Path $TargetPath -Force | Out-Null

$grant = "${Account}:(OI)(CI)M"
& icacls.exe $TargetPath /grant $grant /T /C | Out-Null

if ($LASTEXITCODE -ne 0) {
    throw "icacls failed with exit code $LASTEXITCODE."
}

Write-Output "Prepared $TargetPath for $Account."
