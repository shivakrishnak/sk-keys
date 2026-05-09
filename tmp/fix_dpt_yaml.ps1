
# Fix YAML for DPT-009 through DPT-060
# Adds: status, version, tier, folder
# Clears keyword-based depends_on/used_by/related
# Fixes metadata table IDs

$folder = "C:\ASK\MyWorkspace\sk-keys\dictionary\tier-5-distributed-architecture\DPT-design-patterns"

# Map of DPT-NNN to metadata table old IDs (offset 760 from DPT number)
# DPT-006 = #766, DPT-007 = #767, etc.

$files = Get-ChildItem $folder -Filter "DPT-0*.md" | Where-Object {
    $_.Name -ne "index.md" -and
    $_.Name -match "DPT-0([0-9]+)"
} | Sort-Object Name

foreach ($file in $files) {
    $content = Get-Content $file.FullName -Raw

    # Skip if already has status field
    if ($content -match '(?m)^status:') {
        Write-Host "SKIP (has status): $($file.Name)"
        continue
    }

    # Extract DPT number
    $num = 0
    if ($file.Name -match 'DPT-0*(\d+)') {
        $num = [int]$Matches[1]
    }

    # Fix tags block - add YAML fields after tags section
    # Find the pattern: tags:\n  - ...\n  - ...\n---
    $newContent = $content -replace '(?ms)(tags:(?:\n  - [^\n]+)+)\n---', @"
`$1
status: complete
version: 1
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
---
"@

    # Clear keyword-based depends_on/used_by/related
    $newContent = $newContent -replace '(?m)^(depends_on:) .+$', '${1}'
    $newContent = $newContent -replace '(?m)^(used_by:) .+$', '${1}'
    $newContent = $newContent -replace '(?m)^(related:) .+$', '${1}'

    # Fix metadata table ID: | #NNN | -> | DPT-XXX |
    $oldId = 760 + $num
    $dptId = "DPT-{0:D3}" -f $num
    $newContent = $newContent -replace "\| #$oldId \|", "| $dptId |"

    if ($newContent -ne $content) {
        Set-Content $file.FullName $newContent -NoNewline
        Write-Host "FIXED: $($file.Name)"
    } else {
        Write-Host "NO CHANGE: $($file.Name)"
    }
}

Write-Host "Done!"

