$csv = Import-Csv "c:\ASK\MyWorkspace\sk-keys\tmp\version_updates.csv"

Write-Host "Correct version distribution (after v4.0 detection):"
$csv | Group-Object CorrectVersion | Sort-Object Name | ForEach-Object {
    Write-Host "  v$($_.Name): $($_.Count) files"
}

Write-Host ""
Write-Host "Files with 3+ v4 markers:"
$v4Files = $csv | Where-Object { [int]$_.V4Markers -ge 3 }
Write-Host "  $($v4Files | Measure-Object | Select-Object -ExpandProperty Count) files"

Write-Host ""
Write-Host "Current vs Correct version mismatches:"
$mismatches = $csv | Where-Object { [int]$_.CurrentVersion -ne [int]$_.CorrectVersion }
Write-Host "  $($mismatches | Measure-Object | Select-Object -ExpandProperty Count) files need updates"

Write-Host ""
Write-Host "Sample v4 files:"
$v4Files | Select-Object -First 3 | ForEach-Object {
    Write-Host "  $($_.FileName) - current: v$($_.CurrentVersion), correct: v$($_.CorrectVersion), v4markers: $($_.V4Markers)"
}
