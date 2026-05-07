param([string]$code, [string]$folder)
$enc = [System.Text.UTF8Encoding]::new($false)
$files = Get-ChildItem $folder -Filter "*.md" | Where-Object { $_.Name -ne "index.md" } | Sort-Object Name
$seq = 1
foreach ($file in $files) {
    $newId = "$code-{0:D3}" -f $seq
    $content = [System.IO.File]::ReadAllText($file.FullName, [System.Text.Encoding]::UTF8)
    $keywordName = $file.BaseName -replace '^[\w]+-\d{3}\s+—\s+|^\d+\s+—\s+', ''
    $content = $content -replace '(?m)^number:\s+"[^"]+"', "number: `"$newId`""
    $content = $content -replace '(?m)^nav_order:\s+\d+', "nav_order: $seq"
    $content = $content -replace '(?m)^# [\w]+-\d{3} — |(?m)^# \d+ — ', "# $newId — "
    $newFileName = "$newId — $keywordName.md"
    $newPath = Join-Path $folder $newFileName
    [System.IO.File]::WriteAllText($newPath, $content, $enc)
    if ($file.Name -ne $newFileName) { Remove-Item $file.FullName }
    $seq++
}
Write-Host "✅ $code done. $($seq-1) files."
