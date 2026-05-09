# Fix YAML for DPT-009 through DPT-060
# Uses UTF-8 encoding throughout to preserve Unicode/emoji characters
# Adds: status, version, tier, folder fields
# Clears keyword-based depends_on/used_by/related
# Fixes metadata table IDs (| #NNN | -> | DPT-NNN |)

$folder = "C:\ASK\MyWorkspace\sk-keys\dictionary\tier-5-distributed-architecture\DPT-design-patterns"

$files = Get-ChildItem $folder -Filter "DPT-0*.md" | Where-Object {
    $_.Name -ne "index.md"
} | Sort-Object Name

foreach ($file in $files) {
    # Read with explicit UTF-8
    $content = [System.IO.File]::ReadAllText($file.FullName, [System.Text.Encoding]::UTF8)

    # Skip if already has status field
    if ($content -match '(?m)^status:') {
        Write-Host "SKIP (has status): $($file.Name)"
        continue
    }

    # Skip if no id: field (not a DPT entry)
    if (-not ($content -match '(?m)^id:\s*DPT-')) {
        Write-Host "SKIP (no id): $($file.Name)"
        continue
    }

    $original = $content

    # Add status, version, tier, folder after tags block
    # Match: tags:\n  - ...\n  - ...\n---
    $content = [regex]::Replace($content,
        '(?ms)(tags:(?:\r?\n  - [^\r\n]+)+)(\r?\n---)',
        {
            param($m)
            $tagsBlock = $m.Groups[1].Value
            $endYaml = $m.Groups[2].Value
            "$tagsBlock`nstatus: complete`nversion: 1`ntier: tier-5-distributed-architecture`nfolder: DPT-design-patterns$endYaml"
        })

    # Clear keyword-based depends_on/used_by/related (replace value after colon with nothing)
    $content = [regex]::Replace($content, '(?m)^(depends_on:) .+$', '${1}')
    $content = [regex]::Replace($content, '(?m)^(used_by:) .+$', '${1}')
    $content = [regex]::Replace($content, '(?m)^(related:) .+$', '${1}')

    # Fix metadata table IDs: extract DPT number from filename/id
    if ($file.Name -match 'DPT-0*(\d+)') {
        $num = [int]$Matches[1]
        $oldId = 760 + $num
        $dptId = "DPT-{0:D3}" -f $num
        $content = $content -replace "\| #$oldId \|", "| $dptId |"
    }

    if ($content -ne $original) {
        [System.IO.File]::WriteAllText($file.FullName, $content, [System.Text.Encoding]::UTF8)
        Write-Host "FIXED: $($file.Name)"
    } else {
        Write-Host "NO CHANGE: $($file.Name)"
    }
}

Write-Host "`nDone!"

