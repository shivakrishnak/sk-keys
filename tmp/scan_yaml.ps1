$pattern = [regex]'^(depends_on|used_by|related):\s+"[^"]*",\s*'
$results = @()
$files = Get-ChildItem 'c:\ASK\MyWorkspace\sk-keys\dictionary' -Recurse -Filter '*.md'
foreach ($file in $files) {
    $inFm = $false; $fmCount = 0
    foreach ($l in [System.IO.File]::ReadAllLines($file.FullName, [System.Text.Encoding]::UTF8)) {
        if ($l -eq '---') {
            $fmCount++
            if ($fmCount -eq 1) { $inFm = $true }
            elseif ($fmCount -eq 2) { break }
        }
        if ($inFm -and $pattern.IsMatch($l)) {
            $results += "$($file.FullName) | $l"
            break
        }
    }
}
Write-Host "Still broken: $($results.Count)"
$results | ForEach-Object { Write-Host $_ }
