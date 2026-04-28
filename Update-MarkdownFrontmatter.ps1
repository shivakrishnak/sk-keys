# GitHub Pages Auto-Frontmatter Generator
# Usage: .\Update-MarkdownFrontmatter.ps1 -SectionPath "docs\java" -ParentTitle "Java Fundamentals"

param(
    [Parameter(Mandatory=$true)][string]$SectionPath,
    [Parameter(Mandatory=$true)][string]$ParentTitle,
    [Parameter(Mandatory=$false)][string]$BasePermalink = $null
)

$ErrorActionPreference = "Stop"

Write-Host "`n=== GitHub Pages Auto-Frontmatter Generator ===" -ForegroundColor Cyan
Write-Host "Processing: $SectionPath`n" -ForegroundColor Cyan

# Extract number from filename
function Get-FileNumber {
    param([string]$Filename)
    if ($Filename -match '(\d{3})') { return [int]$matches[1] }
    return $null
}

# Extract title from filename
function Get-TitleFromFilename {
    param([string]$Filename)
    $filename = $Filename -replace '\.md$', ''
    $title = $filename -replace '^[^\s]*\s+', ''  # Remove emoji
    $title = $title -replace '^\d+\s*-\s*', ''     # Remove numbers
    return $title.Trim()
}

# Create permalink from title
function New-Permalink {
    param([string]$Title, [string]$Section)
    $slug = $Title.ToLower()
    $slug = $slug -replace '[^\w\s-]', ''
    $slug = $slug -replace '\s+', '-'
    $slug = $slug -replace '-+', '-'
    $slug = $slug -replace '-$', ''
    if ($Section) { return "/$Section/$slug/" }
    return "/$slug/"
}

# Check if file has frontmatter
function Test-HasFrontmatter {
    param([string]$FilePath)
    $content = Get-Content -Path $FilePath -Raw
    return $content -match '^---'
}

# Remove existing frontmatter
function Remove-ExistingFrontmatter {
    param([string]$FilePath)
    $lines = @(Get-Content -Path $FilePath)
    $start = -1
    $end = -1

    for ($i = 0; $i -lt $lines.Count; $i++) {
        if ($lines[$i] -eq '---') {
            if ($start -eq -1) { $start = $i }
            elseif ($end -eq -1) { $end = $i; break }
        }
    }

    if ($start -ge 0 -and $end -gt $start) {
        return ($lines[($end+1)..($lines.Count-1)] -join "`n")
    }
    return (Get-Content -Path $FilePath -Raw)
}

# Add frontmatter to file
function Add-Frontmatter {
    param([string]$FilePath, [string]$Title, [string]$ParentTitle, [int]$NavOrder, [string]$Permalink)

    if (Test-HasFrontmatter -FilePath $FilePath) {
        $content = Remove-ExistingFrontmatter -FilePath $FilePath
    } else {
        $content = Get-Content -Path $FilePath -Raw
    }

    $fm = @"
---
layout: default
title: "$Title"
parent: "$ParentTitle"
nav_order: $NavOrder
permalink: $Permalink
---

"@

    Set-Content -Path $FilePath -Value ($fm + $content.TrimStart()) -Encoding UTF8
}

# Main
try {
    if (-not (Test-Path -Path $SectionPath)) {
        Write-Host "ERROR: Path not found: $SectionPath`n" -ForegroundColor Red
        exit 1
    }

    if (-not $BasePermalink) {
        $PathSegment = Split-Path -Leaf $SectionPath
        $BasePermalink = $PathSegment.ToLower() -replace '\s+', '-'
    }

    $mdFiles = Get-ChildItem -Path $SectionPath -Filter "*.md" -File | Where-Object { $_.Name -ne "index.md" } | Sort-Object Name

    if ($mdFiles.Count -eq 0) {
        Write-Host "No markdown files found.`n" -ForegroundColor Yellow
        exit 0
    }

    Write-Host "Found: $($mdFiles.Count) files`n" -ForegroundColor Yellow

    $processed = 0
    foreach ($file in $mdFiles) {
        try {
            $fileNumber = Get-FileNumber -Filename $file.Name
            $title = Get-TitleFromFilename -Filename $file.Name
            $navOrder = if ($fileNumber) { $fileNumber } else { $processed + 1 }
            $permalink = New-Permalink -Title $title -Section $BasePermalink

            Add-Frontmatter -FilePath $file.FullName -Title $title -ParentTitle $ParentTitle -NavOrder $navOrder -Permalink $permalink

            Write-Host "[OK] $($file.Name)" -ForegroundColor Green
            Write-Host "     Title: $title | Order: $navOrder | URL: $permalink"
            $processed++
        }
        catch {
            Write-Host "[ERROR] $($file.Name): $_" -ForegroundColor Red
        }
    }

    Write-Host "`nDone! Processed $processed files`n" -ForegroundColor Green
}
catch {
    Write-Host "`nERROR: $_`n" -ForegroundColor Red
    exit 1
}

