$dictRoot = "c:\ASK\MyWorkspace\sk-keys\dictionary"
$results = @()

# Structural markers from .github/copilot-instructions.md version rules.
$v2RequiredSections = @(
    "The Problem This Solves",
    "Understand It in 30 Seconds",
    "Thought Experiment",
    "The Complete Picture - End-to-End Flow",
    "Comparison Table",
    "Failure Modes & Diagnosis"
)

$v21RequiredSections = @(
    "Transferable Wisdom",
    "The Surprising Truth"
)

$v31Markers = @(
    "**Version Evolution:**",
    "Decision Tree:"
)

$v4RequiredSections = @(
    "Gradual Depth - Five Levels",
    "Mastery Checklist"
)

Get-ChildItem -Path $dictRoot -Recurse -Filter "*.md" | Where-Object { $_.Name -ne "index.md" } | ForEach-Object {
    $file = $_
    $filePath = $file.FullName

    try {
        $content = Get-Content -Path $filePath -Raw -Encoding UTF8

        # Get current version
        $versionMatch = [regex]::Match($content, 'version:\s*(\d+)')
        $currentVersion = if ($versionMatch.Success) { [int]$versionMatch.Groups[1].Value } else { 0 }

        # Check if stub
        $isStub = ($content -like "*Entry stub*") -and ($content.Length -lt 5000)

        # Parse frontmatter
        $lines = $content -split "`n"
        $fmEnd = 0
        for ($i = 1; $i -lt $lines.Count; $i++) {
            if ($lines[$i].Trim() -eq "---") {
                $fmEnd = $i
                break
            }
        }

        if ($fmEnd -gt 0) {
            $fm = $lines[0..$fmEnd] -join "`n"
        } else {
            $fm = ""
        }

        if ($fmEnd -lt $lines.Count) {
            $body = $lines[($fmEnd + 1)..($lines.Count - 1)] -join "`n"
        } else {
            $body = ""
        }

        # Check required FM fields
        $missingFM = @()
        if ($fm -notmatch "layout\s*:") { $missingFM += "layout" }
        if ($fm -notmatch "title\s*:") { $missingFM += "title" }
        if ($fm -notmatch "parent\s*:") { $missingFM += "parent" }
        if ($fm -notmatch "nav_order\s*:") { $missingFM += "nav_order" }
        if ($fm -notmatch "permalink\s*:") { $missingFM += "permalink" }

        # Check required sections for v2 baseline.
        $missingContent = @()
        foreach ($section in $v2RequiredSections) {
            if ($body -notlike "*$section*") {
                $missingContent += $section
            }
        }

        $hasFourLevels = $body -like "*Gradual Depth - Four Levels*"
        $hasFiveLevels = $body -like "*Gradual Depth - Five Levels*"
        if (-not ($hasFourLevels -or $hasFiveLevels)) {
            $missingContent += "Gradual Depth"
        }

        $hasV2 = $missingFM.Count -eq 0 -and $missingContent.Count -eq 0

        # v2.1 markers
        $hasV21 = $hasV2
        foreach ($section in $v21RequiredSections) {
            if ($body -notlike "*$section*") {
                $hasV21 = $false
                break
            }
        }
        if ($hasV21) {
            $hintCount = ([regex]::Matches($body, '(?im)^\*Hint:')).Count
            $hasV21 = ($body -match '(?m)^\*\*EVOLUTION:\*\*') -and $hintCount -ge 3
        }

        # v3.0 YAML / ID migration markers
        $hasIdField = $fm -match '(?m)^id\s*:\s*[A-Z]{3}-\d{3}\s*$'
        $hasStatusField = $fm -match '(?m)^status\s*:\s*(draft|in-progress|complete)\s*$'
        $hasFullIdDependencies = $true
        foreach ($fieldName in @('depends_on', 'used_by', 'related')) {
            $fieldMatch = [regex]::Match($fm, "(?m)^$fieldName\s*:\s*(.*)$")
            if (-not $fieldMatch.Success) {
                $hasFullIdDependencies = $false
                break
            }

            $value = $fieldMatch.Groups[1].Value.Trim()
            if ($value.Length -eq 0) {
                continue
            }

            foreach ($item in ($value -split ',')) {
                $trimmed = $item.Trim()
                if ($trimmed.Length -eq 0) {
                    continue
                }
                if ($trimmed -notmatch '^[A-Z]{3}-\d{3}$') {
                    $hasFullIdDependencies = $false
                    break
                }
            }

            if (-not $hasFullIdDependencies) {
                break
            }
        }
        $hasV30 = $hasV21 -and $hasIdField -and $hasStatusField -and $hasFullIdDependencies

        # v3.1 structural indicators from repo instructions.
        $hasV31Indicator = $false
        foreach ($marker in $v31Markers) {
            if ($body -like "*$marker*") {
                $hasV31Indicator = $true
                break
            }
        }
        $hasV31 = $hasV30 -and $hasV31Indicator

        # v4.0 structural indicators.
        $hasV4 = $hasV31
        foreach ($section in $v4RequiredSections) {
            if ($body -notlike "*$section*") {
                $hasV4 = $false
                break
            }
        }
        if ($hasV4) {
            $hasAntiPatternRow = $body -match '(?m)^.*ANTI-PATTERN.*$'
            $hasIndustryApplications = $body -like "***Industry applications:***"
            $hasTypeGQuestion = $body -match 'TYPE G'
            $hasV4 = $hasAntiPatternRow -and $hasIndustryApplications -and $hasTypeGQuestion
        }

        # Determine correct version using the repo rules (5-level 0-4 scale):
        # 0 = stub (placeholder, no generated content)
        # 1 = pre-v2 / incomplete (some content but baseline sections missing)
        # 2 = v2 or v2.1 (all baseline sections present; v2.1 additions keep version 2)
        # 3 = v3.x (v3.0 or v3.1 — id field + full IDs in dependencies)
        # 4 = v4.0 (five-level depth, Mastery Checklist, ANTI-PATTERN row, Industry applications)
        if ($isStub -or $body.Length -lt 500) {
            $correctVersion = 0
        } elseif (-not $hasV2) {
            $correctVersion = 1
        } elseif ($hasV4) {
            $correctVersion = 4
        } elseif ($hasV30) {
            $correctVersion = 3
        } else {
            $correctVersion = 2
        }

        $results += [PSCustomObject]@{
            FilePath = $filePath
            FileName = $file.Name
            CurrentVersion = $currentVersion
            CorrectVersion = $correctVersion
            IsStub = $isStub
            MissingFM = ($missingFM -join ",")
            MissingContent = if ($missingContent.Count -le 2) { ($missingContent -join ",") } else { "$($missingContent[0]),$($missingContent[1])..." }
            HasV21 = $hasV21
            HasV30 = $hasV30
            HasV31 = $hasV31
            HasV4 = $hasV4
            NeedsUpdate = if ($currentVersion -ne $correctVersion) { "YES" } else { "NO" }
        }
    } catch {
        Write-Host "Error processing $filePath : $_"
    }
}

# Export to CSV
$outputPath = "c:\ASK\MyWorkspace\sk-keys\tmp\version_updates.csv"
$results | Export-Csv -Path $outputPath -Encoding UTF8 -NoTypeInformation

Write-Host "Scan complete. Results: $($results.Count) files"
Write-Host "Needing updates: $($results | Where-Object { $_.NeedsUpdate -eq 'YES' } | Measure-Object | Select-Object -ExpandProperty Count)"
Write-Host "Output: $outputPath"
