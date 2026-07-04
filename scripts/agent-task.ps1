param(
    [string]$CommitMessage = "docs: add machine-readable schemas and validation architecture"
)

$ErrorActionPreference = "Stop"
$repo = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $repo

$sprintFiles = @(
    "PROJECT_CONTEXT.md",
    "PROJECT_TRACKER.md",
    "README.md",
    "docs/architecture/SYSTEM_ARCHITECTURE.md",
    "docs/architecture/CONTRACT_VALIDATION_ARCHITECTURE.md",
    "docs/guides/VALIDATION_GUIDE.md",
    "docs/roadmaps/VALIDATOR_ROADMAP.md",
    "docs/specifications/README.md",
    "schemas/README.md",
    "schemas/skill.schema.json",
    "schemas/workflow.schema.json",
    "schemas/knowledge.schema.json",
    "schemas/evaluation.schema.json",
    "schemas/reflection.schema.json",
    "schemas/metadata.schema.json",
    "schemas/version.schema.json",
    "scripts/agent-task.ps1"
)

Write-Output "--- JSON SYNTAX AND SCHEMA HEADERS ---"
$schemaFiles = Get-ChildItem -LiteralPath "schemas" -Filter "*.schema.json" -File
if ($schemaFiles.Count -ne 7) {
    throw "Expected 7 core schemas, found $($schemaFiles.Count)."
}

foreach ($file in $schemaFiles) {
    $schema = Get-Content -Raw -LiteralPath $file.FullName | ConvertFrom-Json
    if ($schema.'$schema' -ne "https://json-schema.org/draft/2020-12/schema") {
        throw "$($file.Name) does not declare Draft 2020-12."
    }
    foreach ($field in @('$id', 'title', 'description')) {
        if (-not $schema.PSObject.Properties[$field]) {
            throw "$($file.Name) is missing $field."
        }
    }
    if (-not $schema.PSObject.Properties["examples"]) {
        throw "$($file.Name) is missing top-level examples."
    }
    Write-Output "OK $($file.Name)"
}

Write-Output "--- LOCAL SCHEMA REFERENCES ---"
foreach ($file in $schemaFiles) {
    $text = Get-Content -Raw -LiteralPath $file.FullName
    $matches = [regex]::Matches($text, '"\$ref"\s*:\s*"([^"]+)"')
    foreach ($match in $matches) {
        $ref = $match.Groups[1].Value
        if ($ref.StartsWith("#") -or $ref.StartsWith("http")) {
            continue
        }
        $relativeFile = ($ref -split "#", 2)[0]
        $target = Join-Path $file.DirectoryName $relativeFile
        if (-not (Test-Path -LiteralPath $target)) {
            throw "Broken schema ref in $($file.Name): $ref"
        }
    }
}
Write-Output "OK local schema files"

Write-Output "--- MARKDOWN LINKS ---"
$brokenLinks = @()
Get-ChildItem -Recurse -File -Filter "*.md" | ForEach-Object {
    $source = $_
    $content = Get-Content -Raw -LiteralPath $source.FullName
    foreach ($match in [regex]::Matches($content, '\[[^\]]+\]\(([^)#]+)(?:#[^)]+)?\)')) {
        $link = $match.Groups[1].Value
        if ($link -match '^(https?://|mailto:)') {
            continue
        }
        $target = Join-Path $source.DirectoryName $link
        if (-not (Test-Path -LiteralPath $target)) {
            $brokenLinks += "$($source.FullName) -> $link"
        }
    }
}
if ($brokenLinks.Count -gt 0) {
    throw "Broken Markdown links:`n$($brokenLinks -join "`n")"
}
Write-Output "OK Markdown links"

Write-Output "--- SCOPE AND DIFF ---"
$changed = @(git status --porcelain -uall | ForEach-Object { $_.Substring(3).Replace("\", "/") })
$unexpected = @($changed | Where-Object { $_ -notin $sprintFiles })
if ($unexpected.Count -gt 0) {
    throw "Unexpected changed files:`n$($unexpected -join "`n")"
}
git status --short
git diff --stat
git diff --check
if ($LASTEXITCODE -ne 0) {
    throw "git diff --check failed."
}

Write-Output "--- STAGE AND REVIEW ---"
git add -- $sprintFiles
if ($LASTEXITCODE -ne 0) {
    throw "git add failed."
}
git diff --cached --name-status
git diff --cached --stat
git diff --cached --check
if ($LASTEXITCODE -ne 0) {
    throw "git diff --cached --check failed."
}

$staged = @(git diff --cached --name-only)
if ($staged.Count -eq 0) {
    Write-Output "No staged changes; skipping commit and push."
} else {
    Write-Output "--- COMMIT AND PUSH ---"
    git commit -m $CommitMessage
    if ($LASTEXITCODE -ne 0) {
        throw "git commit failed."
    }
    git push origin main
    if ($LASTEXITCODE -ne 0) {
        throw "git push failed."
    }
}

Write-Output "--- FINAL ---"
git rev-parse HEAD
git status --branch --short
if ((git status --porcelain).Count -ne 0) {
    throw "Working tree is not clean."
}
