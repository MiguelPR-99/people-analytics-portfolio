param(
    [int]$Seed = 20261012,
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$generator = Join-Path $PSScriptRoot "generate_synthetic_data.py"
$arguments = @($generator, "--seed", $Seed, "--output-dir", (Join-Path $projectRoot "data"))

if ($Force) {
    $arguments += "--force"
}

py -3 @arguments
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

