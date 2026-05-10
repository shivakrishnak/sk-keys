$csv = Import-Csv "c:\ASK\MyWorkspace\sk-keys\tmp\version_updates.csv"
Write-Host "Correct version distribution:"
$csv | Group-Object CorrectVersion | Sort-Object Name | ForEach-Object {
    Write-Host "  v$($_.Name): $($_.Count)"
}
Write-Host ""
Write-Host "Current version distribution:"
$csv | Group-Object CurrentVersion | Sort-Object Name | ForEach-Object {
    Write-Host "  v$($_.Name): $($_.Count)"
}
Write-Host ""
Write-Host "Sample upgrades:"
$csv | Where-Object { $_.NeedsUpdate -eq "YES" } | Select-Object -First 8 FileName, CurrentVersion, CorrectVersion, HasV21, HasV30, HasV31, HasV4 | Format-Table -AutoSize | Out-String -Width 220 | Write-Host
