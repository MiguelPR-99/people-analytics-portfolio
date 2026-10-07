param(
    [int]$CaseCount = 9000,
    [int]$Seed = 20260824,
    [switch]$Force
)

$projectPath = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$generatorPath = Join-Path $PSScriptRoot "generate_synthetic_data.py"
$outputPath = Join-Path $projectPath "data"
$generatorArgs = @($generatorPath, "--case-count", $CaseCount, "--seed", $Seed, "--output-dir", $outputPath)

if ($Force) {
    $generatorArgs += "--force"
}

$pythonLauncher = Get-Command py -ErrorAction SilentlyContinue
if ($pythonLauncher) {
    & $pythonLauncher.Source -3 @generatorArgs
    exit $LASTEXITCODE
}

$pythonCommand = Get-Command python -ErrorAction SilentlyContinue
if ($pythonCommand) {
    & $pythonCommand.Source @generatorArgs
    exit $LASTEXITCODE
}

Write-Error "Python 3 no esta instalado o no se encuentra disponible en PATH."
exit 1

