$enc = [System.Text.UTF8Encoding]::new($false)
$dir = "c:\ASK\MyWorkspace\sk-keys\dictionary\tier-3-java\SPR-spring-core"
$pattern = [regex]'^(depends_on|used_by|related):\s+"'
$fixed = 0

foreach ($file in Get-ChildItem $dir -Filter "SPR-*.md") {
    $lines = [System.IO.File]::ReadAllLines($file.FullName, [System.Text.Encoding]::UTF8)
    $changed = $false
    $inFm = $false
    $fmCount = 0
    $newLines = New-Object System.Collections.Generic.List[string]

    foreach ($l in $lines) {
        if ($l -eq '---') {
            $fmCount++
            if ($fmCount -eq 1) { $inFm = $true }
            elseif ($fmCount -eq 2) { $inFm = $false }
        }
        if ($inFm -and $pattern.IsMatch($l)) {
            $colon = $l.IndexOf(':')
            $key = $l.Substring(0, $colon)
            $val = $l.Substring($colon + 1).Trim()
            $cleaned = $val.Replace('"', '')
            $l = "${key}: `"${cleaned}`""
            $changed = $true
        }
        $newLines.Add($l)
    }

    if ($changed) {
        [System.IO.File]::WriteAllLines($file.FullName, $newLines.ToArray(), $enc)
        $fixed++
        Write-Host "Fixed: $($file.Name)"
    }
}
Write-Host "Total: $fixed"
