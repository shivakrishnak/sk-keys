# pwsh -ExecutionPolicy Bypass -File tmp\patch_version_field.ps1
# Adds version: 1 to all entry files that are missing it.
# Strategy A: has status: -> insert version: 1 on the line after status:
# Strategy B: no status:  -> insert version: 1 on the line before layout:

Set-Location "c:\ASK\MyWorkspace\sk-keys"
$enc = [System.Text.UTF8Encoding]::new($false)
$patched = 0; $skipped = 0; $errors = 0

Get-ChildItem "dictionary" -Recurse -Filter "*.md" |
    Where-Object { $_.Name -ne 'index.md' } |
    ForEach-Object {
        $path = $_.FullName
        $raw  = [System.IO.File]::ReadAllText($path, [System.Text.Encoding]::UTF8)
        $lines = $raw -split "`n"

        # Check first 30 lines for version:
        $top30 = $lines | Select-Object -First 30
        $hasVersion = ($top30 | Where-Object { $_ -cmatch '^version:' }).Count -gt 0
        if ($hasVersion) { $skipped++; return }

        # Find second '---' (end of frontmatter) to bound the search
        $fmEnd = -1
        for ($i = 1; $i -lt [Math]::Min($lines.Count, 35); $i++) {
            if ($lines[$i] -cmatch '^---') { $fmEnd = $i; break }
        }
        if ($fmEnd -lt 0) { $errors++; return }   # no frontmatter found

        # Strategy A: insert after status:
        $statusIdx = -1
        for ($i = 1; $i -lt $fmEnd; $i++) {
            if ($lines[$i] -cmatch '^status:') { $statusIdx = $i; break }
        }
        if ($statusIdx -ge 0) {
            $newLines = $lines[0..$statusIdx] + 'version: 1' + $lines[($statusIdx+1)..($lines.Count-1)]
            [System.IO.File]::WriteAllText($path, ($newLines -join "`n"), $enc)
            $patched++; return
        }

        # Strategy B: insert before layout:
        $layoutIdx = -1
        for ($i = 1; $i -lt $fmEnd; $i++) {
            if ($lines[$i] -cmatch '^layout:') { $layoutIdx = $i; break }
        }
        if ($layoutIdx -ge 0) {
            $newLines = $lines[0..($layoutIdx-1)] + 'version: 1' + $lines[$layoutIdx..($lines.Count-1)]
            [System.IO.File]::WriteAllText($path, ($newLines -join "`n"), $enc)
            $patched++; return
        }

        $errors++
    }

Write-Host "Patched: $patched  Already had version: $skipped  Errors: $errors"
