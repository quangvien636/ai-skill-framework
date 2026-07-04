$ErrorActionPreference = "Stop"
$repo = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$validator = Join-Path $PSScriptRoot "validate_contracts.py"

Push-Location $repo
try {
    python $validator
    if ($LASTEXITCODE -ne 0) {
        throw "Contract validation failed with exit code $LASTEXITCODE."
    }
}
finally {
    Pop-Location
}
