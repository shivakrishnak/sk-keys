# pwsh -ExecutionPolicy Bypass -File tmp\strip_bom_all.ps1
# Strips UTF-8 BOM (EF BB BF) from all .md files in the dictionary folder.
# Writes back only files that actually have BOM — all others untouched.

Set-Location "c:\ASK\MyWorkspace\sk-keys"
$enc = [System.Text.UTF8Encoding]::new($false)   # UTF-8, no BOM
$fixed = 0; $skipped = 0

Get-ChildItem "dictionary" -Recurse -Filter "*.md" | ForEach-Object {
    $bytes = [System.IO.File]::ReadAllBytes($_.FullName)
    if ($bytes.Length -ge 3 -and $bytes[0] -eq 239 -and $bytes[1] -eq 187 -and $bytes[2] -eq 191) {
        # Has BOM — re-read as UTF-8 string (framework strips the BOM on read), write back clean
        $text = [System.IO.File]::ReadAllText($_.FullName, [System.Text.Encoding]::UTF8)
        # Belt-and-suspenders: manually strip BOM char if still present
        if ($text.Length -gt 0 -and [int][char]$text[0] -eq 65279) { $text = $text.Substring(1) }
        [System.IO.File]::WriteAllText($_.FullName, $text, $enc)
        $fixed++
    } else {
        $skipped++
    }
}

Write-Host "Stripped BOM from : $fixed files"
Write-Host "Already clean     : $skipped files"

# Verify: no BOMs should remain
$remaining = (Get-ChildItem "dictionary" -Recurse -Filter "*.md" | Where-Object {
    $b = [System.IO.File]::ReadAllBytes($_.FullName)
    $b.Length -ge 3 -and $b[0] -eq 239 -and $b[1] -eq 187 -and $b[2] -eq 191
}).Count
Write-Host "Remaining BOM files: $remaining (should be 0)"
