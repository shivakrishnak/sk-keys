#!/usr/bin/env pwsh

# ==============================================================================
# Bulk Frontmatter Update Script
# ==============================================================================
# Purpose: Update all markdown files in docs folder with Jekyll frontmatter
# Usage: .\Bulk-Update-All-Sections.ps1
# ==============================================================================

# Section configuration
$sections = @(
    @{ Path = "docs\java"; Parent = "Java Fundamentals" },
    @{ Path = "docs\spring"; Parent = "Spring" },
    @{ Path = "docs\Distributed Systems"; Parent = "Distributed Systems" },
    @{ Path = "docs\Databases"; Parent = "Databases" },
    @{ Path = "docs\Messaging & Streaming"; Parent = "Messaging & Streaming" },
    @{ Path = "docs\Networking & HTTP"; Parent = "Networking & HTTP" },
    @{ Path = "docs\OS & Systems"; Parent = "OS & Systems" },
    @{ Path = "docs\System Design"; Parent = "System Design" },
    @{ Path = "docs\DSA"; Parent = "DSA" },
    @{ Path = "docs\Software Design"; Parent = "Software Design" },
    @{ Path = "docs\Cloud & Infrastructure"; Parent = "Cloud & Infrastructure" },
    @{ Path = "docs\DevOps & SDLC"; Parent = "DevOps & SDLC" }
)

Write-Host "`n╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║       Bulk Frontmatter Update - All Sections              ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Process each section
foreach ($section in $sections) {
    $sectionPath = Join-Path (Get-Location) $section.Path

    if (Test-Path -Path $sectionPath) {
        Write-Host "Processing: $($section.Parent)" -ForegroundColor Yellow
        & .\Update-MarkdownFrontmatter.ps1 -SectionPath $section.Path -ParentTitle $section.Parent
    }
    else {
        Write-Host "⚠️  Skipping: $($section.Parent) (path not found)" -ForegroundColor Yellow
    }
}

Write-Host "`n✅ All sections updated!`n" -ForegroundColor Green

