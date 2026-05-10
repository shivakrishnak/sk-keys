<#
.SYNOPSIS
    Upgrades dictionary entries to v4.0 by surgically adding missing sections.

.DESCRIPTION
    Without -Upgrade : shows version statistics only (safe, read-only).
    With    -Upgrade : adds missing v4.0 sections to files with version 1-3.
                       Existing content is NEVER modified — only new section
                       stubs are appended / inserted where they are absent.

    v4.0 additions this script detects and adds:
      - ### ✅ Mastery Checklist         (new section if completely absent)
      - **Industry applications:**        (inside Transferable Wisdom if absent)
      - Level 5 label stub               (if only Four Levels heading found)

    After upgrading, search files for "TODO v4.0" and fill stubs with Copilot.

.PARAMETER Upgrade
    Enable upgrade mode. Default is stats-only.

.PARAMETER Category
    Filter to a specific category code, e.g. -Category JVM

.PARAMETER Tier
    Filter to a specific tier number, e.g. -Tier 3

.PARAMETER BatchSize
    Max files to upgrade per run. Default: 10.

.EXAMPLE
    # Stats only (all files):
    pwsh -ExecutionPolicy Bypass -File tmp\upgrade_to_v4.ps1

    # Stats for one category:
    pwsh -ExecutionPolicy Bypass -File tmp\upgrade_to_v4.ps1 -Category JVM

    # Upgrade next 10 eligible files:
    pwsh -ExecutionPolicy Bypass -File tmp\upgrade_to_v4.ps1 -Upgrade

    # Upgrade a whole category at once:
    pwsh -ExecutionPolicy Bypass -File tmp\upgrade_to_v4.ps1 -Upgrade -Category MSV -BatchSize 100

    # Upgrade a tier:
    pwsh -ExecutionPolicy Bypass -File tmp\upgrade_to_v4.ps1 -Upgrade -Tier 5 -BatchSize 50
#>
param(
    [switch]$Upgrade,
    [string]$Category  = "",
    [string]$Tier      = "",
    [int]$BatchSize    = 10
)

Set-Location "c:\ASK\MyWorkspace\sk-keys"
$dictRoot = "c:\ASK\MyWorkspace\sk-keys\dictionary"
$enc      = [System.Text.UTF8Encoding]::new($false)

# ─────────────────────────────────────────────────────────────────────────────
# GATHER FILES
# ─────────────────────────────────────────────────────────────────────────────
$allFiles = Get-ChildItem -Path $dictRoot -Recurse -Filter "*.md" |
    Where-Object { $_.Name -ne "index.md" }

if ($Category) { $allFiles = $allFiles | Where-Object { $_.FullName -match "\\$Category-" } }
if ($Tier)     { $allFiles = $allFiles | Where-Object { $_.FullName -match "\\tier-$Tier-" } }

# ─────────────────────────────────────────────────────────────────────────────
# ANALYZE
# ─────────────────────────────────────────────────────────────────────────────
$vDist     = @{ 0=0; 1=0; 2=0; 3=0; 4=0 }
$candidates = [System.Collections.Generic.List[hashtable]]::new()

foreach ($f in $allFiles) {
    try {
        $raw = [System.IO.File]::ReadAllText($f.FullName, [System.Text.Encoding]::UTF8)
        $vm  = [regex]::Match($raw, '(?m)^version:\s*(\d+)')
        $v   = if ($vm.Success) { [int]$vm.Groups[1].Value } else { 1 }
        $vDist[$v]++
        if ($v -in 1,2,3) { $candidates.Add(@{ File=$f; Version=$v; Raw=$raw }) }
    } catch { }
}

# ─────────────────────────────────────────────────────────────────────────────
# SHOW STATISTICS
# ─────────────────────────────────────────────────────────────────────────────
$filterLabel = if ($Category) { " [category: $Category]" } elseif ($Tier) { " [tier: $Tier]" } else { "" }

Write-Host ""
Write-Host "=== Dictionary Version Statistics$filterLabel ===" -ForegroundColor Cyan
Write-Host ("  v0  stubs              : {0,5}  (placeholders - no generated content)" -f $vDist[0])
Write-Host ("  v1  pre-v2 / incomplete: {0,5}  (some content, baseline sections missing)" -f $vDist[1])
Write-Host ("  v2  v2 / v2.1          : {0,5}  (all baseline sections present)" -f $vDist[2])
Write-Host ("  v3  v3.x               : {0,5}  (new YAML id: field + full IDs)" -f $vDist[3])
Write-Host ("  v4  v4.0 complete      : {0,5}  (Five Levels + Mastery Checklist + all v4 markers)" -f $vDist[4])
Write-Host ("  ─────────────────────────────────────────────────────────────") -ForegroundColor DarkGray
Write-Host ("  Total                  : {0,5}" -f $allFiles.Count)
Write-Host ""
Write-Host ("  Eligible for upgrade (v1+v2+v3): {0}" -f $candidates.Count) -ForegroundColor Yellow

if (-not $Upgrade) {
    Write-Host ""
    Write-Host "  Run with -Upgrade [-Category CODE] [-Tier N] [-BatchSize N] to add missing v4 sections."  -ForegroundColor Gray
    Write-Host ""
    exit 0
}

# ─────────────────────────────────────────────────────────────────────────────
# UPGRADE — surgical addition of missing v4 sections only
# ─────────────────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "=== Upgrading (batch: $BatchSize files) ===" -ForegroundColor Cyan
Write-Host ""

$batch = $candidates | Select-Object -First $BatchSize
$ok = 0; $skip = 0; $fail = 0

foreach ($item in $batch) {
    $f   = $item.File
    $raw = $item.Raw
    $v   = $item.Version

    # Split frontmatter from body
    $fmEnd = $raw.IndexOf("`n---", 4)
    if ($fmEnd -lt 0) {
        $skip++
        Write-Host ("  SKIP  {0,-50} (no frontmatter boundary)" -f $f.Name) -ForegroundColor DarkGray
        continue
    }
    $fm   = $raw.Substring(0, $fmEnd + 4)
    $body = $raw.Substring($fmEnd + 4)
    $changed = $false
    $log  = [System.Collections.Generic.List[string]]::new()

    # ── 1. Upgrade "Four Levels" heading to "Five Levels" + add Level 5 stub ──
    if ($body -like "*Gradual Depth - Four Levels*" -and $body -notlike "*Gradual Depth - Five Levels*") {
        $body = $body -replace 'Gradual Depth - Four Levels', 'Gradual Depth - Five Levels'

        if ($body -notlike "*Level 5 - Mastery*") {
            $level5Stub = @"

**Level 5 - Mastery (distinguished engineer):**
<!-- TODO v4.0: Add cross-system reasoning, novel application, teaching others.
     What are the hidden costs no beginner knows? What would you change if redesigning today? -->
[Cross-system reasoning. Novel application. Teaching others. Design critique.]
"@
            # Append Level 5 before the next --- or ### after level 4
            $body = [regex]::Replace(
                $body,
                '(\*\*Level 4[^*]+?\*\*[\s\S]+?)(\r?\n---|\r?\n###)',
                { $args[0].Groups[1].Value + $level5Stub + $args[0].Groups[2].Value },
                [System.Text.RegularExpressions.RegexOptions]::Singleline
            )
        }
        $log.Add("Level 5 stub added")
        $changed = $true
    }

    # ── 2. Add Mastery Checklist section if completely absent ──
    if ($body -notlike "*Mastery Checklist*") {
        $masteryBlock = @"

---

### ✅ Mastery Checklist

<!-- TODO v4.0: Replace each placeholder with a concept-specific, testable indicator -->
**You've mastered this when you can:**
1. [EXPLAIN] Articulate the core invariant of this concept clearly to a junior developer.
2. [DEBUG]   Identify and resolve the most common production failure using the right diagnostic command.
3. [DECIDE]  Choose between this and its primary alternative given a specific engineering constraint.
4. [BUILD]   Implement or configure this correctly in a production-like scenario from scratch.
5. [EXTEND]  Apply the underlying principle from this concept to a novel problem you have not seen before.

"@
        if ($body -match '(?s)(\r?\n---\r?\n\s*### 🧠 Think About This)') {
            $body = $body -replace '(\r?\n---\r?\n\s*### 🧠 Think About This)', "$masteryBlock`$1"
        } else {
            $body = $body.TrimEnd() + "`n" + $masteryBlock
        }
        $log.Add("Mastery Checklist added")
        $changed = $true
    }

    # ── 3. Add Industry applications inside Transferable Wisdom if absent ──
    if (($body -like "*Transferable Wisdom*") -and ($body -notlike "*Industry applications:*")) {
        $industryBlock = @"

**Industry applications:**
<!-- TODO v4.0: Replace with 2 specific, concrete industry examples relevant to this concept -->
- [Industry/system 1] - [why this concept is critical in this context]
- [Industry/system 2] - [how it is applied differently here]

"@
        # Insert at end of "Where else this pattern appears" list, before next section
        $body = [regex]::Replace(
            $body,
            '(\*\*Where else this pattern appears:\*\*[\s\S]+?)(?=\r?\n---|\r?\n###|\z)',
            { $args[0].Groups[1].Value + $industryBlock },
            [System.Text.RegularExpressions.RegexOptions]::Singleline
        )
        $log.Add("Industry applications stub added")
        $changed = $true
    }

    # ── 4. Set version: 4 in frontmatter ──
    $newFm = $fm -replace '(?m)^version:\s*\d+', 'version: 4'
    if ($newFm -ne $fm) { $changed = $true }

    if (-not $changed) {
        $skip++
        Write-Host ("  SKIP  {0,-50} (nothing to add)" -f $f.Name) -ForegroundColor DarkGray
        continue
    }

    try {
        [System.IO.File]::WriteAllText($f.FullName, $newFm + $body, $enc)
        $ok++
        $logStr = if ($log.Count -gt 0) { " [" + ($log -join " | ") + "]" } else { "" }
        Write-Host ("  OK    v{0}->4  {1,-50}{2}" -f $v, $f.Name, $logStr) -ForegroundColor Green
    } catch {
        $fail++
        Write-Host ("  ERR          {0,-50} $_" -f $f.Name) -ForegroundColor Red
    }
}

# ─────────────────────────────────────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host ("=== Upgrade complete: {0} upgraded | {1} skipped | {2} errors ===" -f $ok, $skip, $fail) -ForegroundColor Cyan
if ($ok -gt 0) {
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "  1. Search for '<!-- TODO v4.0:' in upgraded files and fill stubs with Copilot."
    Write-Host "  2. Run without -Upgrade to verify stats."
    Write-Host "  3. git add dictionary/ && git commit -m 'upgrade: add v4.0 sections - batch N'"
}
Write-Host ""
