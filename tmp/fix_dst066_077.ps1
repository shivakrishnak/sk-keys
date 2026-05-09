# pwsh -ExecutionPolicy Bypass -File tmp\fix_dst066_077.ps1
# Fixes DST-066 to DST-077:
#   1. Removes BOM (rewrites with UTF-8 no-BOM)
#   2. tag '  - dst' -> '  - distributed'
#   3. permalink '/dst/' -> '/distributed-systems/'
#   4. 'status: draft' -> 'status: complete'

Set-Location "c:\ASK\MyWorkspace\sk-keys"
$enc = [System.Text.UTF8Encoding]::new($false)
$dst = "dictionary\tier-5-distributed-architecture\DST-distributed-systems"
$fixed = 0

66..77 | ForEach-Object {
    $n   = $_.ToString().PadLeft(3, '0')
    $f   = Get-ChildItem $dst -Filter "DST-$n*.md" | Select-Object -First 1
    if (-not $f) { Write-Host "DST-$n not found - skipping"; return }

    $raw = [System.IO.File]::ReadAllText($f.FullName, [System.Text.Encoding]::UTF8)

    # Strip BOM if present
    if ($raw[0] -eq [char]0xFEFF) { $raw = $raw.Substring(1) }

    $raw = $raw -replace '(?m)^  - dst$', '  - distributed'
    $raw = $raw -replace 'permalink: /dst/', 'permalink: /distributed-systems/'
    $raw = $raw -replace 'status: draft', 'status: complete'

    [System.IO.File]::WriteAllText($f.FullName, $raw, $enc)
    $fixed++
    Write-Host "Fixed: $($f.Name)"
}

Write-Host "`nTotal fixed: $fixed"

# Verify sample
$sample = "DST-066 - Distributed System Architecture Strategy.md"
$bytes = [System.IO.File]::ReadAllBytes("$dst\$sample")
Write-Host "BOM check (must NOT be 239,187,191): $($bytes[0]),$($bytes[1]),$($bytes[2])"
$preview = [System.Text.Encoding]::UTF8.GetString($bytes[0..500])
if ($preview -match '/distributed-systems/') { Write-Host "Permalink: OK" }
if ($preview -match 'status: complete') { Write-Host "Status: OK" }
