Set-Location 'c:\ASK\MyWorkspace\sk-keys'

# Read titles of orphan files in CSF (CSF-065 to CSF-080)
Write-Host "=== CSF ORPHANS (in folder but not in index) ==="
65..80 | ForEach-Object {
    $n = $_.ToString('D3')
    $f = Get-ChildItem "dictionary\tier-1-foundations\CSF-cs-fundamentals\CSF-$n*.md" -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($f) {
        $raw = [IO.File]::ReadAllText($f.FullName)
        $title = if ($raw -match '(?m)^title:\s*"?(.+?)"?\s*$') { $Matches[1].Trim('"') } else { 'NO_TITLE' }
        $diff  = if ($raw -match '(?m)^difficulty:\s*(.+?)\s*$') { $Matches[1].Trim() } else { '?' }
        Write-Host "  CSF-$n | $diff | $title"
    } else { Write-Host "  CSF-$n | MISSING FILE" }
}

# Read titles of orphan files in LNX (check which 4 are missing)
Write-Host "`n=== LNX FILES IN FOLDER vs INDEX ==="
$lnxFiles = Get-ChildItem "dictionary\tier-1-foundations\LNX-linux\*.md" | Where-Object { $_.Name -ne 'index.md' }
$lnxIdx   = [IO.File]::ReadAllText("dictionary\tier-1-foundations\LNX-linux\index.md")
$lnxInIdx = [regex]::Matches($lnxIdx, 'LNX-\d+') | ForEach-Object { $_.Value } | Sort-Object -Unique
$lnxFiles | ForEach-Object {
    $nm = $_.BaseName.Split(' ')[0]
    if ($nm -notin $lnxInIdx) { Write-Host "  ORPHAN: $($_.Name)" }
}
Write-Host "  Index has $($lnxInIdx.Count) IDs. Files: $($lnxFiles.Count)"

# Check OSY orphans
Write-Host "`n=== OSY FILES vs INDEX ==="
$osyFiles = Get-ChildItem "dictionary\tier-1-foundations\OSY-operating-systems\*.md" | Where-Object { $_.Name -ne 'index.md' }
$osyIdx   = [IO.File]::ReadAllText("dictionary\tier-1-foundations\OSY-operating-systems\index.md")
$osyInIdx = [regex]::Matches($osyIdx, 'OSY-\d+') | ForEach-Object { $_.Value } | Sort-Object -Unique
$osyFiles | ForEach-Object {
    $nm = $_.BaseName.Split(' ')[0]
    if ($nm -notin $osyInIdx) { Write-Host "  ORPHAN: $($_.Name)" }
}
Write-Host "  Index has $($osyInIdx.Count) IDs. Files: $($osyFiles.Count)"

# Check NET and API
Write-Host "`n=== NET FILES vs INDEX ==="
$netFiles = Get-ChildItem "dictionary\tier-2-networking-security\NET-networking\*.md" | Where-Object { $_.Name -ne 'index.md' }
$netIdx   = [IO.File]::ReadAllText("dictionary\tier-2-networking-security\NET-networking\index.md")
$netInIdx = [regex]::Matches($netIdx, 'NET-\d+') | ForEach-Object { $_.Value } | Sort-Object -Unique
$netFiles | ForEach-Object {
    $nm = $_.BaseName.Split(' ')[0]
    if ($nm -notin $netInIdx) { Write-Host "  ORPHAN: $($_.Name)" }
}
Write-Host "  Index has $($netInIdx.Count) IDs. Files: $($netFiles.Count)"

Write-Host "`n=== API FILES vs INDEX ==="
$apiFiles = Get-ChildItem "dictionary\tier-2-networking-security\API-http-apis\*.md" | Where-Object { $_.Name -ne 'index.md' }
$apiIdx   = [IO.File]::ReadAllText("dictionary\tier-2-networking-security\API-http-apis\index.md")
$apiInIdx = [regex]::Matches($apiIdx, 'API-\d+') | ForEach-Object { $_.Value } | Sort-Object -Unique
$apiFiles | ForEach-Object {
    $nm = $_.BaseName.Split(' ')[0]
    if ($nm -notin $apiInIdx) { Write-Host "  ORPHAN: $($_.Name)" }
}
Write-Host "  Index has $($apiInIdx.Count) IDs. Files: $($apiFiles.Count)"

Write-Host "`n=== SEC FILES vs INDEX ==="
$secFiles = Get-ChildItem "dictionary\tier-2-networking-security\SEC-security\*.md" | Where-Object { $_.Name -ne 'index.md' }
Write-Host "  Files: $($secFiles.Count), highest: $(($secFiles | ForEach-Object { if ($_.BaseName -match '^SEC-0*(\d+)') {[int]$Matches[1]} else {0} } | Measure-Object -Maximum).Maximum)"
