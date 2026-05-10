# reorganize_batch1.ps1 - Fix CRY and BIG ID gaps by renumbering
# Run: pwsh -ExecutionPolicy Bypass -File tmp\reorganize_batch1.ps1
Set-Location 'c:\ASK\MyWorkspace\sk-keys'
$enc = [System.Text.UTF8Encoding]::new($false)

function Get-FM($raw, $field) {
    if ($raw -match "(?m)^$([regex]::Escape($field)):\s*(.+)") { $Matches[1].Trim() }
    else { '' }
}

function Rename-Entry($dir, $oldFile, $newId, $newNav) {
    $src = "$dir\$oldFile"
    if (-not (Test-Path $src)) { Write-Host "MISSING: $src"; return }
    $raw = [System.IO.File]::ReadAllText($src, [System.Text.Encoding]::UTF8)
    $oldId = if ($oldFile -match '^([A-Z]+-\d+)') { $Matches[1] } else { '' }

    # Update frontmatter fields
    $raw = $raw -replace '(?m)^id:\s+\S+', "id: $newId"
    $raw = $raw -replace '(?m)^nav_order:\s+\d+', "nav_order: $newNav"
    # Update H1 heading if it starts with old id
    if ($oldId) {
        $raw = $raw -replace "(?m)^# $([regex]::Escape($oldId))\b", "# $newId"
    }

    $title = (Get-FM $raw 'title') -replace '^"', '' -replace '"$', ''
    $newName = "$newId - $title.md"
    $dest = "$dir\$newName"

    [System.IO.File]::WriteAllText($dest, $raw, $enc)
    if ($dest -ne $src) { Remove-Item $src -Force }
    Write-Host "  $oldId -> $newId ($($title.Substring(0, [Math]::Min(45,$title.Length))))"
}

# ─────────────────────────────────────────────────────────────────────────────
# PART 1: Renumber CRY - close the gap (013-023 don't exist)
#   CRY-024 -> CRY-013, CRY-025 -> CRY-014, ..., CRY-037 -> CRY-026
# ─────────────────────────────────────────────────────────────────────────────
Write-Host "`n=== CRY: Renumber 024-037 -> 013-026 ==="
$cryDir = 'dictionary\tier-2-networking-security\CRY-cryptography'

# Get current high-numbered CRY files (024-037)
$cryHigh = Get-ChildItem "$cryDir\CRY-0[23]\d*.md" | Sort-Object Name
# More precise:
$cryHigh = Get-ChildItem "$cryDir\*.md" |
    Where-Object { $_.Name -match '^CRY-(0[2-9]\d|[1-9]\d\d+)' -and $_.Name -ne 'index.md' } |
    Where-Object { if ($_.Name -match '^CRY-(\d+)') { [int]$Matches[1] -ge 24 } } |
    Sort-Object Name

$cryStart = 13
foreach ($f in $cryHigh) {
    $newId = "CRY-$("{0:D3}" -f $cryStart)"
    Rename-Entry $cryDir $f.Name $newId $cryStart
    $cryStart++
}

# ─────────────────────────────────────────────────────────────────────────────
# PART 2: Renumber BIG - close all gaps from MSG migration
#   Current: 001-014, 029-036, 045-064 (gaps at 015-028 and 037-044)
#   Target:  001-042 sequential
# ─────────────────────────────────────────────────────────────────────────────
Write-Host "`n=== BIG: Renumber to fill gaps -> 001-042 ==="
$bigDir = 'dictionary\tier-4-data\BIG-bigdata-streaming'

# Map old number -> new number (only those that need renaming)
# 001-014: no change
# 029-036 -> 015-022 (shift by -14)
# 045-064 -> 023-042 (shift by -22)
$bigRenameMap = @{}
15..64 | ForEach-Object { $bigRenameMap[$_] = $null }  # init
# 029->015, 030->016, ..., 036->022
for ($i = 029; $i -le 036; $i++) { $bigRenameMap[$i] = $i - 14 }
# 045->023, 046->024, ..., 064->042
for ($i = 045; $i -le 064; $i++) { $bigRenameMap[$i] = $i - 22 }

# Process in REVERSE order to avoid overwriting
$bigFiles = Get-ChildItem "$bigDir\*.md" |
    Where-Object { $_.Name -ne 'index.md' -and $_.Name -match '^BIG-(\d+)' } |
    Sort-Object Name -Descending

foreach ($f in $bigFiles) {
    if ($f.Name -match '^BIG-(\d+)') {
        $oldNum = [int]$Matches[1]
        if ($bigRenameMap.ContainsKey($oldNum) -and $null -ne $bigRenameMap[$oldNum]) {
            $newNum = $bigRenameMap[$oldNum]
            $newId = "BIG-$("{0:D3}" -f $newNum)"
            Rename-Entry $bigDir $f.Name $newId $newNum
        }
    }
}

Write-Host "`n=== Verification ==="
$cryCount = (Get-ChildItem "$cryDir\*.md" | Where-Object { $_.Name -ne 'index.md' }).Count
$bigCount  = (Get-ChildItem "$bigDir\*.md" | Where-Object { $_.Name -ne 'index.md' }).Count
$cryMax = (Get-ChildItem "$cryDir\CRY-*.md" | Where-Object { $_.Name -match '^CRY-(\d+)' } |
    ForEach-Object { [int]$Matches[1] } | Sort-Object -Descending | Select-Object -First 1)
$bigMax = (Get-ChildItem "$bigDir\BIG-*.md" | Where-Object { $_.Name -match '^BIG-(\d+)' } |
    ForEach-Object { [int]$Matches[1] } | Sort-Object -Descending | Select-Object -First 1)
Write-Host "CRY: $cryCount files, max=$cryMax (expected: 26 files, max=26)"
Write-Host "BIG: $bigCount files, max=$bigMax (expected: 42 files, max=42)"
