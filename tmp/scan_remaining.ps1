# Scan all remaining tier categories
Set-Location 'c:\ASK\MyWorkspace\sk-keys'

$tiers = @(
    'dictionary\tier-4-data',
    'dictionary\tier-6-infrastructure-devops',
    'dictionary\tier-7-frontend',
    'dictionary\tier-8-artificial-intelligence',
    'dictionary\tier-9-professional-domain'
)

foreach ($tier in $tiers) {
    $tierName = Split-Path $tier -Leaf
    Write-Host "`n=== $tierName ==="
    $catFolders = Get-ChildItem $tier -Directory
    foreach ($cat in $catFolders) {
        $code = $cat.Name.Split('-')[0]
        $files = (Get-ChildItem "$($cat.FullName)\*.md" | Where-Object { $_.Name -ne 'index.md' }).Count
        $idxPath = "$($cat.FullName)\index.md"
        $idxClaim = 0
        $highestId = 0
        if (Test-Path $idxPath) {
            $idxContent = Get-Content $idxPath -Raw
            $matches2 = [regex]::Matches($idxContent, "$code-(\d+)")
            foreach ($m in $matches2) { $n = [int]$m.Groups[1].Value; if ($n -gt $highestId) { $highestId = $n } }
            $idxClaim = $matches2 | ForEach-Object { $_.Value } | Sort-Object -Unique | Measure-Object | Select-Object -ExpandProperty Count
        }
        $delta = $highestId - $files
        $status = if ($delta -eq 0) { "SYNCED" } elseif ($delta -gt 0) { "MISSING $delta stubs" } else { "ORPHANS $(- $delta)" }
        Write-Host "  $code | files=$files | highest=$highestId | idx_unique=$idxClaim | $status"
    }
}
