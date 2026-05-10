$csvPath = "c:\ASK\MyWorkspace\sk-keys\tmp\version_updates.csv"
$updates = Import-Csv -Path $csvPath | Where-Object { $_.NeedsUpdate -eq "YES" }

$totalCount = $updates.Count
$successCount = 0
$errorCount = 0

Write-Host "Starting version updates: $totalCount files to update"

foreach ($update in $updates) {
    $filePath = $update.FilePath
    $newVersion = $update.CorrectVersion

    try {
        # Read file
        $content = Get-Content -Path $filePath -Raw -Encoding UTF8

        # Replace version field: version: X -> version: newVersion (preserving any spacing)
        $updated = $content -replace 'version:\s*\d+', "version: $newVersion"

        # Write back only if changed
        if ($updated -ne $content) {
            [System.IO.File]::WriteAllText(
                $filePath,
                $updated,
                [System.Text.UTF8Encoding]::new($false))
            $successCount++
        }

        # Progress every 100 files
        if ($successCount % 100 -eq 0) {
            Write-Host "Progress: $successCount / $totalCount updated"
        }
    } catch {
        Write-Host "ERROR: $filePath - $_"
        $errorCount++
    }
}

Write-Host ""
Write-Host "===== COMPLETE ====="
Write-Host "Total to update: $totalCount"
Write-Host "Successful: $successCount"
Write-Host "Errors: $errorCount"
