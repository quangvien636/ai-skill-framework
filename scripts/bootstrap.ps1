# AI Skill Framework Bootstrap

$Root = "C:\AI\ai-skill-framework"

$Folders = @(
  "docs\architecture",
  "docs\principles",
  "docs\guides",
  "docs\references",
  "docs\roadmaps",
  "docs\adr",
  "knowledge",
  "skills",
  "workflows",
  "templates",
  "tests",
  "examples",
  "prompts",
  "runtime",
  "src"
)

foreach ($f in $Folders) {
  New-Item -ItemType Directory -Force -Path "$Root\$f" | Out-Null
}

function New-MarkdownFile($Path, $Title) {
  if (!(Test-Path $Path)) {
@"
# $Title

Version: 0.1  
Status: Draft

## Purpose

TODO

## Scope

TODO

## Notes

TODO

## Revision History

| Version | Date | Description |
|---------|------|-------------|
| 0.1 | 2026-07-04 | Initial draft |
"@ | Set-Content -Encoding UTF8 $Path
  }
}

New-MarkdownFile "$Root\docs\principles\DESIGN_PRINCIPLES.md" "AI Skill Framework - Design Principles"
New-MarkdownFile "$Root\docs\principles\NAMING_CONVENTION.md" "Naming Convention"
New-MarkdownFile "$Root\docs\guides\GETTING_STARTED.md" "Getting Started"
New-MarkdownFile "$Root\docs\guides\DEVELOPMENT_GUIDE.md" "Development Guide"
New-MarkdownFile "$Root\docs\references\GLOSSARY.md" "Glossary"
New-MarkdownFile "$Root\docs\roadmaps\ROADMAP.md" "Roadmap"
New-MarkdownFile "$Root\PROJECT_TRACKER.md" "AI Skill Framework Project Tracker"

Write-Host "Bootstrap completed."
