cd 'c:\ASK\MyWorkspace\sk-keys'

foreach ($cat in @('JVM-java-jvm-internals','JCC-java-concurrency','JLG-java-language','SPR-spring-core')) {
    Write-Host "`n=== $cat ==="
    $files = Get-ChildItem "dictionary\tier-3-java\$cat\*.md" | Where-Object { $_.Name -ne 'index.md' } | Sort-Object Name
    foreach ($f in $files) {
        $raw = [System.IO.File]::ReadAllText($f.FullName)
        $id    = if ($raw -match '(?m)^id:\s*(\S+)')         { $Matches[1] } else { 'NO_ID' }
        $title = if ($raw -match '(?m)^title:\s*"?(.+?)"?\s*$') { $Matches[1].Trim('"').Trim() } else { 'NO_TITLE' }
        $diff  = if ($raw -match '(?m)^difficulty:\s*(.+?)\s*$') { $Matches[1].Trim() } else { '?' }
        $fid   = $f.BaseName.Split(' ')[0]  # ID from file name
        $match = if ($id -eq $fid) { 'OK' } else { "MISMATCH(file=$fid)" }
        Write-Host "  $id | $diff | $title | $match"
    }
}
