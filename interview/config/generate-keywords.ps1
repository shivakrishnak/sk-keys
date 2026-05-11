<#
.SYNOPSIS
    Interview Mastery Dictionary - Keyword Generator & Folder Scaffolding
.DESCRIPTION
    Generates keyword lists for interview topics, groups them into
    sub-topic files, and creates folder/index/stub structure.

    Supports three flows:
    1. New topic from scratch (generates keywords via AI prompt)
    2. New topic from existing dictionary category
    3. Add subtopic to existing topic

    ALWAYS use pwsh (PowerShell 7+):
      pwsh -ExecutionPolicy Bypass -File interview/config/generate-keywords.ps1

.PARAMETER Topic
    Topic name (e.g., "Java", "Angular", "Kubernetes")
.PARAMETER FromDictionary
    Dictionary category code(s) to source keywords from (e.g., "JLG", "JVM,JLG")
.PARAMETER Subtopic
    Add a new subtopic file to an existing topic
.PARAMETER Keywords
    Comma-separated list of keywords for a new subtopic
.PARAMETER DryRun
    Preview what would be created without writing files
.EXAMPLE
    pwsh -File generate-keywords.ps1 -Topic Java -FromDictionary "JVM,JLG"
.EXAMPLE
    pwsh -File generate-keywords.ps1 -Topic Angular
.EXAMPLE
    pwsh -File generate-keywords.ps1 -Topic React -Subtopic "Hooks" -Keywords "useState,useEffect,useContext,useReducer,useMemo,useCallback,useRef,Custom Hooks"
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$Topic,

    [Parameter()]
    [string]$FromDictionary,

    [Parameter()]
    [string]$Subtopic,

    [Parameter()]
    [string]$Keywords,

    [Parameter()]
    [switch]$DryRun
)

# ── Constants ──────────────────────────────────────────────
$ErrorActionPreference = "Stop"
$WorkspaceRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$InterviewRoot = Join-Path $WorkspaceRoot "interview"
$DictionaryRoot = Join-Path $WorkspaceRoot "dictionary"
$Utf8NoBom     = [System.Text.UTF8Encoding]::new($false)

# ── Helper Functions ───────────────────────────────────────

function Get-TopicFolder {
    param([string]$TopicName)
    return ($TopicName.ToLower() -replace '\s+', '-' -replace '[^a-z0-9\-]', '')
}

function Get-TopicPath {
    param([string]$TopicName)
    return Join-Path $InterviewRoot (Get-TopicFolder $TopicName)
}

function Write-SafeFile {
    param([string]$Path, [string]$Content)
    $dir = Split-Path -Parent $Path
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
    [System.IO.File]::WriteAllText($Path, $Content, $Utf8NoBom)
}

function Read-DictionaryIndex {
    param([string]$CategoryPath)
    $indexPath = Join-Path $CategoryPath "index.md"
    if (-not (Test-Path $indexPath)) { return @() }
    $content = [System.IO.File]::ReadAllText($indexPath, $Utf8NoBom)
    $entries = @()
    foreach ($line in ($content -split "`n")) {
        if ($line -match '^\|\s*([A-Z]{3}-\d{3})\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|') {
            $diff = $Matches[3].Trim()
            $level = switch -Regex ($diff) {
                '^\x{2605}\x{2606}\x{2606}' { "easy" }
                '^\x{2605}\x{2605}\x{2606}' { "medium" }
                '^\x{2605}\x{2605}\x{2605}' { "hard" }
                default { "mixed" }
            }
            $entries += @{
                Id         = $Matches[1].Trim()
                Title      = $Matches[2].Trim()
                Difficulty = $level
                RawDiff    = $diff
            }
        }
    }
    return $entries
}

function Find-DictionaryCategory {
    param([string]$TopicName)
    $search = $TopicName.ToLower() -replace '\s+', '-'
    $allCats = Get-ChildItem -Path $DictionaryRoot -Recurse -Directory |
        Where-Object { $_.Name -match '^[A-Z]{3}-' }

    $matches = $allCats | Where-Object {
        $folderSearch = $_.Name.ToLower()
        $folderSearch -like "*$search*" -or
        $folderSearch -like "*$($TopicName.ToLower().Replace(' ', ''))*"
    }
    return $matches
}

function Group-KeywordsIntoSubtopics {
    <#
    .SYNOPSIS
        Intelligently groups keywords into sub-topic files.
        Uses difficulty level and keyword name patterns to create
        logical groupings of 5-15 keywords per file.
    #>
    param(
        [string]$TopicName,
        [array]$AllKeywords
    )

    if ($AllKeywords.Count -le 15) {
        # Small category - one file
        return @{
            "Fundamentals" = $AllKeywords
        }
    }

    # Group by difficulty as baseline
    $easy = $AllKeywords | Where-Object { $_.Difficulty -eq "easy" }
    $medium = $AllKeywords | Where-Object { $_.Difficulty -eq "medium" }
    $hard = $AllKeywords | Where-Object { $_.Difficulty -eq "hard" }

    $groups = @{}

    # Easy keywords -> "Basics" or "Fundamentals"
    if ($easy.Count -gt 0) {
        if ($easy.Count -le 15) {
            $groups["Basics"] = $easy
        } else {
            # Split large easy group into chunks
            $chunkSize = [Math]::Ceiling($easy.Count / 2)
            $groups["Basics"] = $easy[0..($chunkSize - 1)]
            $groups["Core Concepts"] = $easy[$chunkSize..($easy.Count - 1)]
        }
    }

    # Medium keywords -> split if needed
    if ($medium.Count -gt 0) {
        if ($medium.Count -le 15) {
            $groups["Intermediate"] = $medium
        } else {
            $chunkSize = [Math]::Ceiling($medium.Count / 2)
            $groups["Intermediate"] = $medium[0..($chunkSize - 1)]
            $groups["Working Patterns"] = $medium[$chunkSize..($medium.Count - 1)]
        }
    }

    # Hard keywords -> "Advanced" or "Deep Dive"
    if ($hard.Count -gt 0) {
        if ($hard.Count -le 15) {
            $groups["Advanced"] = $hard
        } else {
            $chunkSize = [Math]::Ceiling($hard.Count / 2)
            $groups["Advanced"] = $hard[0..($chunkSize - 1)]
            $groups["Architecture and Internals"] = $hard[$chunkSize..($hard.Count - 1)]
        }
    }

    # Handle ungrouped (mixed/unknown difficulty)
    $mixed = $AllKeywords | Where-Object { $_.Difficulty -eq "mixed" }
    if ($mixed.Count -gt 0) {
        $groups["Additional Topics"] = $mixed
    }

    return $groups
}

function New-SubtopicStub {
    param(
        [string]$TopicName,
        [string]$SubtopicName,
        [array]$KeywordEntries,
        [string]$DifficultyRange = "mixed"
    )
    $topicPath = Get-TopicPath $TopicName
    $fileName = "$TopicName - $SubtopicName.md"
    $filePath = Join-Path $topicPath $fileName

    if (Test-Path $filePath) {
        Write-Host "  SKIP (exists): $fileName" -ForegroundColor Yellow
        return
    }

    $kwNames = $KeywordEntries | ForEach-Object {
        if ($_ -is [hashtable]) { $_.Title } else { "$_" }
    }
    $kwYaml = ($kwNames | ForEach-Object { "  - $_" }) -join "`n"

    # Determine difficulty range
    if ($KeywordEntries[0] -is [hashtable]) {
        $diffs = $KeywordEntries | Select-Object -ExpandProperty Difficulty -Unique
        if ($diffs.Count -eq 1) { $DifficultyRange = $diffs[0] }
        else { $DifficultyRange = "mixed" }
    }

    $stub = @"
---
title: $TopicName - $SubtopicName
topic: $TopicName
subtopic: $SubtopicName
keywords:
$kwYaml
difficulty_range: $DifficultyRange
status: draft
version: 0
---

# $TopicName - $SubtopicName

> Content generation pending. Run generate-content.ps1 to populate.

"@

    if (-not $DryRun) {
        Write-SafeFile -Path $filePath -Content $stub
    }
    Write-Host "  CREATED stub: $fileName ($($kwNames.Count) keywords)" -ForegroundColor Green
}

function Update-TopicIndex {
    param([string]$TopicName)
    $topicPath = Get-TopicPath $TopicName
    $indexPath = Join-Path $topicPath "index.md"

    $files = Get-ChildItem -Path $topicPath -Filter "*.md" -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -ne "index.md" } |
        Sort-Object Name

    $rows = @()
    $totalKeywords = 0
    foreach ($f in $files) {
        $content = [System.IO.File]::ReadAllText($f.FullName, $Utf8NoBom)
        $kwCount = 0
        if ($content -match '(?s)keywords:\s*\n((?:\s+- [^\n]+\n?)+)') {
            $kwLines = $Matches[1] -split "`n" |
                Where-Object { $_ -match '^\s+- ' }
            $kwCount = $kwLines.Count
        }
        $totalKeywords += $kwCount

        $desc = ""
        if ($content -match 'subtopic:\s*(.+)') {
            $desc = $Matches[1].Trim()
        }
        $rows += "| $($f.Name) | $kwCount | $desc |"
    }

    $indexContent = @"
---
title: $TopicName
description: Interview mastery content for $TopicName
keywords_count: $totalKeywords
files_count: $($files.Count)
---

# $TopicName

Interview mastery content for $TopicName - complete knowledge, zero to mastery.

| File | Keywords | Description |
|------|----------|-------------|
$($rows -join "`n")
"@

    if (-not $DryRun) {
        Write-SafeFile -Path $indexPath -Content $indexContent
    }
    Write-Host "  INDEX: $TopicName ($($files.Count) files, $totalKeywords keywords)" -ForegroundColor Cyan
}

# ── Main Logic ─────────────────────────────────────────────

Write-Host "╔═══════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  Interview Mastery - Keyword Generator    ║" -ForegroundColor Cyan
Write-Host "║  Topic: $($Topic.PadRight(34))║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════╝" -ForegroundColor Cyan

if ($DryRun) {
    Write-Host "[DRY RUN MODE]" -ForegroundColor DarkGray
}

$topicPath = Get-TopicPath $Topic

# ── Flow 1: Add subtopic to existing topic ─────────────────
if ($Subtopic) {
    Write-Host "`n=== ADD SUBTOPIC: $Subtopic ===" -ForegroundColor Magenta

    if (-not (Test-Path $topicPath)) {
        Write-Error "Topic folder not found: $topicPath. Create the topic first."
        return
    }

    if (-not $Keywords) {
        Write-Host "`nProvide keywords with -Keywords parameter:" -ForegroundColor Yellow
        Write-Host "  -Keywords 'Keyword1,Keyword2,Keyword3'"
        Write-Host "`nOr use AI to generate keywords:" -ForegroundColor Yellow
        Write-Host @"

Generate a keyword list for interview mastery:
  Topic: $Topic
  Subtopic: $Subtopic

Requirements:
- 5-15 keywords covering the subtopic comprehensively
- Order: foundational concepts first, advanced last
- Each keyword should be a distinct, teachable concept
- Focus on interview-relevant knowledge
- Include both theoretical and practical concepts

Output format (one keyword per line):
  - Keyword Name
"@
        return
    }

    $kwList = $Keywords -split ',' | ForEach-Object { $_.Trim() } | Where-Object { $_ }
    $kwEntries = $kwList | ForEach-Object { @{ Title = $_; Difficulty = "mixed" } }

    New-SubtopicStub -TopicName $Topic -SubtopicName $Subtopic -KeywordEntries $kwEntries
    Update-TopicIndex -TopicName $Topic

    Write-Host "`n=== SUBTOPIC ADDED ===" -ForegroundColor Magenta
    Write-Host "Next: pwsh -File generate-content.ps1 -Mode file -Topic '$Topic' -File '$Subtopic'"
    return
}

# ── Flow 2: From dictionary category ──────────────────────
if ($FromDictionary) {
    Write-Host "`n=== IMPORT FROM DICTIONARY: $FromDictionary ===" -ForegroundColor Magenta

    $codes = $FromDictionary -split ',' | ForEach-Object { $_.Trim().ToUpper() }
    $allKeywords = @()

    foreach ($code in $codes) {
        # Find the category folder
        $catFolders = Get-ChildItem -Path $DictionaryRoot -Recurse -Directory |
            Where-Object { $_.Name -match "^$code-" }

        if (-not $catFolders) {
            Write-Warning "Dictionary category not found: $code"
            continue
        }

        foreach ($catFolder in $catFolders) {
            Write-Host "  Reading: $($catFolder.Name)" -ForegroundColor Cyan
            $entries = Read-DictionaryIndex $catFolder.FullName
            Write-Host "    $($entries.Count) keywords found" -ForegroundColor White
            $allKeywords += $entries
        }
    }

    if ($allKeywords.Count -eq 0) {
        Write-Error "No keywords found in specified dictionary categories"
        return
    }

    Write-Host "`nTotal keywords: $($allKeywords.Count)" -ForegroundColor Cyan

    # Group into sub-topic files
    $groups = Group-KeywordsIntoSubtopics -TopicName $Topic -AllKeywords $allKeywords

    Write-Host "`nSub-topic grouping:" -ForegroundColor Yellow
    foreach ($entry in $groups.GetEnumerator()) {
        $kwCount = $entry.Value.Count
        Write-Host "  $Topic - $($entry.Key).md ($kwCount keywords)"
    }

    # Create folder and stubs
    if (-not $DryRun) {
        if (-not (Test-Path $topicPath)) {
            New-Item -ItemType Directory -Path $topicPath -Force | Out-Null
            Write-Host "`nCREATED folder: $(Get-TopicFolder $Topic)/" -ForegroundColor Green
        }
    }

    foreach ($entry in $groups.GetEnumerator()) {
        New-SubtopicStub -TopicName $Topic -SubtopicName $entry.Key -KeywordEntries $entry.Value
    }

    Update-TopicIndex -TopicName $Topic

    Write-Host "`n=== IMPORT COMPLETE ===" -ForegroundColor Magenta
    Write-Host "Next: pwsh -File generate-content.ps1 -Mode topic -Topic '$Topic'"
    return
}

# ── Flow 3: New topic (no dictionary source) ──────────────
Write-Host "`n=== NEW TOPIC: $Topic ===" -ForegroundColor Magenta

# Check for existing dictionary match
$dictMatch = Find-DictionaryCategory $Topic
if ($dictMatch) {
    $codes = ($dictMatch | ForEach-Object { ($_.Name -split '-')[0] }) -join ','
    Write-Host "Found matching dictionary categories: $codes" -ForegroundColor Cyan
    Write-Host "Consider running with -FromDictionary '$codes'" -ForegroundColor Yellow
    Write-Host ""
}

if (Test-Path $topicPath) {
    Write-Host "Topic folder already exists: $(Get-TopicFolder $Topic)/" -ForegroundColor Yellow
    Write-Host "Existing files:" -ForegroundColor White
    Get-ChildItem -Path $topicPath -Filter "*.md" |
        ForEach-Object { Write-Host "  $($_.Name)" }
    Write-Host ""
}

# Output AI prompt for keyword generation
Write-Host "┌─────────────────────────────────────────────┐" -ForegroundColor Green
Write-Host "│ USE THIS PROMPT TO GENERATE KEYWORDS        │" -ForegroundColor Green
Write-Host "└─────────────────────────────────────────────┘" -ForegroundColor Green
Write-Host ""

$kwPrompt = @"
Generate a comprehensive keyword list for interview mastery on: $Topic

Requirements:
1. Cover the topic from zero to god-level mastery
2. Include 30-80 keywords depending on topic breadth
3. Order: foundational -> intermediate -> advanced -> architecture
4. Each keyword is a distinct, teachable concept
5. Focus on what interviewers actually ask about
6. Include both theoretical concepts and practical skills
7. Cover: fundamentals, patterns, internals, debugging,
   performance, architecture, production concerns

Group keywords into sub-topic files (5-15 keywords each):
- Group related concepts together
- Each group should be self-sufficient
- Name groups clearly: "$Topic - [Subtopic Name]"

Output format:

## $Topic - Basics
- Keyword 1
- Keyword 2
...

## $Topic - [Next Subtopic]
- Keyword N
...

After generating, run:
  pwsh -File interview/config/generate-keywords.ps1 \`
    -Topic '$Topic' -Subtopic '[Name]' \`
    -Keywords 'Keyword1,Keyword2,Keyword3'

Repeat for each sub-topic group.
"@

Write-Host $kwPrompt

Write-Host ""
Write-Host "┌─────────────────────────────────────────────┐" -ForegroundColor Green
Write-Host "│ END OF PROMPT                               │" -ForegroundColor Green
Write-Host "└─────────────────────────────────────────────┘" -ForegroundColor Green

# Create empty folder if not dry run
if (-not $DryRun -and -not (Test-Path $topicPath)) {
    New-Item -ItemType Directory -Path $topicPath -Force | Out-Null
    Write-Host "`nCREATED folder: $(Get-TopicFolder $Topic)/" -ForegroundColor Green

    # Create empty index
    $indexContent = @"
---
title: $Topic
description: Interview mastery content for $Topic
keywords_count: 0
files_count: 0
---

# $Topic

Interview mastery content for $Topic - complete knowledge, zero to mastery.

| File | Keywords | Description |
|------|----------|-------------|
"@
    $indexPath = Join-Path $topicPath "index.md"
    Write-SafeFile -Path $indexPath -Content $indexContent
    Write-Host "CREATED index: $Topic/index.md" -ForegroundColor Green
}

Write-Host "`n=== TOPIC SCAFFOLDED ===" -ForegroundColor Magenta
