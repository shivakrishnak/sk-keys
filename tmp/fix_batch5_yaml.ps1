# Fix YAML for batch 5 SAP files using regex (handles CRLF/LF differences)
$d = "c:\ASK\MyWorkspace\sk-keys\dictionary\tier-5-distributed-architecture\SAP-software-architecture"

# Map: filename -> [depends_on, used_by, related, new tags array]
$updates = @{
    "SAP-046 - YAGNI (You Aren't Gonna Need It).md" = @{
        depends_on = "SAP-043, SAP-045"
        used_by    = ""
        related    = "SAP-043, SAP-044, SAP-045"
        tags       = "  - architecture`r`n  - principles`r`n  - pattern"
        title_raw  = $false   # don't need to re-quote title
    }
    "SAP-047 - Law of Demeter.md" = @{
        depends_on = "SAP-043, SAP-051"
        used_by    = ""
        related    = "SAP-043, SAP-048, SAP-051"
        tags       = "  - architecture`r`n  - principles`r`n  - pattern"
        title_raw  = $false
    }
    "SAP-048 - Tell Don't Ask.md" = @{
        depends_on = "SAP-043, SAP-047"
        used_by    = ""
        related    = "SAP-047, SAP-049"
        tags       = "  - architecture`r`n  - principles`r`n  - pattern"
        title_raw  = $false
    }
    "SAP-049 - Command-Query Separation (CQS).md" = @{
        depends_on = "SAP-043, SAP-048"
        used_by    = ""
        related    = "SAP-018, SAP-048"
        tags       = "  - architecture`r`n  - principles`r`n  - pattern"
        title_raw  = $false
    }
    "SAP-050 - Cohesion.md" = @{
        depends_on = "SAP-043"
        used_by    = ""
        related    = "SAP-051, SAP-052"
        tags       = "  - architecture`r`n  - principles`r`n  - pattern"
        title_raw  = $false
    }
    "SAP-051 - Coupling.md" = @{
        depends_on = "SAP-043"
        used_by    = ""
        related    = "SAP-050, SAP-052"
        tags       = "  - architecture`r`n  - principles`r`n  - pattern"
        title_raw  = $false
    }
    "SAP-052 - Connascence.md" = @{
        depends_on = "SAP-050, SAP-051"
        used_by    = ""
        related    = "SAP-050, SAP-051"
        tags       = "  - architecture`r`n  - principles`r`n  - deep-dive"
        title_raw  = $false
    }
}

foreach ($fn in $updates.Keys) {
    $fp = Join-Path $d $fn
    $c = [IO.File]::ReadAllText($fp, [Text.Encoding]::UTF8)

    $u = $updates[$fn]

    # 1. Reorder YAML: put id: first (move id line before layout line)
    # Find the YAML block end
    $yamlEnd = $c.IndexOf("`r`n---`r`n", 5)
    if ($yamlEnd -eq -1) { $yamlEnd = $c.IndexOf("`n---`n", 5) }

    # Extract the id value
    $idMatch = [regex]::Match($c, "^id: (SAP-\d+)", [System.Text.RegularExpressions.RegexOptions]::Multiline)
    $idVal = if ($idMatch.Success) { $idMatch.Value } else { "id: SAP-0XX" }

    # 2. Update depends_on, used_by, related
    $c = [regex]::Replace($c, "(?m)^depends_on:.*$", "depends_on: $($u.depends_on)")
    $c = [regex]::Replace($c, "(?m)^used_by:.*$", "used_by: $($u.used_by)")
    $c = [regex]::Replace($c, "(?m)^related:.*$", "related: $($u.related)")

    # 3. Replace tags block with new tags
    $c = [regex]::Replace($c, "(?ms)^tags:\r?\n(  - [^\r\n]+\r?\n)+", "tags:`r`n$($u.tags)`r`n")

    # 4. Add missing fields after tags block if not present
    if ($c -notmatch "^status: complete") {
        $c = [regex]::Replace($c, "(?m)^status: .*$", "status: complete")
    }
    if ($c -notmatch "^status:") {
        # Insert status after tags block
        $c = [regex]::Replace($c, "((?ms)^tags:\r?\n(  - [^\r\n]+\r?\n)+)", "`$1status: complete`r`n")
    }

    if ($c -notmatch "^version:") {
        $c = [regex]::Replace($c, "(?m)^status: complete", "status: complete`r`nversion: 1")
    }

    if ($c -notmatch "^tier:") {
        $c = [regex]::Replace($c, "(?m)^category: Software Architecture Patterns", "category: Software Architecture Patterns`r`ntier: tier-5-distributed-architecture`r`nfolder: SAP-software-architecture")
    }

    # 5. Move id: to be the first field (after ---)
    # Remove id from where it is, put it at top
    if ($c -match "(?m)^layout: default") {
        # id is below layout; restructure to put id first
        $c = [regex]::Replace($c, "(?m)^id: (SAP-\d+)\r?\n", "")
        $c = [regex]::Replace($c, "(?m)^---\r?\n", "---`r`n$idVal`r`n", 1)
        # remove any duplicate id lines
        $count = ([regex]::Matches($c, "(?m)^id: SAP-")).Count
        if ($count -gt 1) {
            # keep first, remove subsequent
            $firstIdx = $c.IndexOf("`r`nid: SAP-")
            $secondIdx = $c.IndexOf("`r`nid: SAP-", $firstIdx + 5)
            if ($secondIdx -gt 0) {
                $lineEnd = $c.IndexOf("`r`n", $secondIdx + 2)
                $c = $c.Remove($secondIdx, $lineEnd - $secondIdx)
            }
        }
    }

    [IO.File]::WriteAllText($fp, $c, [Text.Encoding]::UTF8)
    Write-Host "$fn : YAML updated"
}
Write-Host "Done."
