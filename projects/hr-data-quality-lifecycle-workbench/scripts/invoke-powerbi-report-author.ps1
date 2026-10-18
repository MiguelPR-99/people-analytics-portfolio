[CmdletBinding(PositionalBinding = $false)]
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$CliArguments
)

$ErrorActionPreference = 'Stop'
$resolver = Join-Path $PSScriptRoot 'set_powerbi_desktop_path.ps1'
& $resolver -NoPersist | Out-Null

& powerbi-report-author @CliArguments
exit $LASTEXITCODE
