$d = "c:\ASK\MyWorkspace\sk-keys\dictionary\tier-5-distributed-architecture\SAP-software-architecture"

$metaData = @{
    "SAP-036" = @{ dep = "SAP-035"; used = "SAP-035"; rel = "SAP-035, SAP-037, SAP-038" }
    "SAP-037" = @{ dep = "SAP-035, SAP-034"; used = "SAP-035, SAP-038"; rel = "SAP-034, SAP-035, SAP-038" }
    "SAP-038" = @{ dep = "SAP-037, SAP-035"; used = "SAP-037"; rel = "SAP-035, SAP-037" }
    "SAP-039" = @{ dep = "SAP-013, SAP-050, SAP-051"; used = "-"; rel = "SAP-011, SAP-012, SAP-040" }
    "SAP-040" = @{ dep = "SAP-043, SAP-050, SAP-051"; used = "-"; rel = "SAP-039, SAP-041" }
    "SAP-041" = @{ dep = "SAP-043, SAP-050"; used = "-"; rel = "SAP-040, SAP-042" }
    "SAP-042" = @{ dep = "SAP-043"; used = "-"; rel = "SAP-040, SAP-041" }
    "SAP-043" = @{ dep = "SAP-050, SAP-051"; used = "SAP-044, SAP-045, SAP-046, SAP-047"; rel = "SAP-044, SAP-045, SAP-046, SAP-047" }
    "SAP-044" = @{ dep = "SAP-043"; used = "-"; rel = "SAP-043, SAP-045, SAP-046" }
    "SAP-045" = @{ dep = "SAP-043, SAP-046"; used = "-"; rel = "SAP-043, SAP-044, SAP-046" }
}

foreach ($key in ($metaData.Keys | Sort-Object)) {
    $f = (Get-ChildItem "$d\$key*")[0].FullName
    $c = [IO.File]::ReadAllText($f, [Text.Encoding]::UTF8)

    $m = $metaData[$key]
    $newTable = "`n`n| Field          | Value                              |`n| -------------- | ---------------------------------- |`n| **Depends on** | $($m.dep) |`n| **Used by**    | $($m.used) |`n| **Related**    | $($m.rel) |"

    # Remove the Entry Metadata block
    $c = [regex]::Replace($c, "\r?\n---\r?\n\r?\n### [^\r\n]*Entry Metadata[\s\S]*?---\r?\n", "`n---`n")

    # Add new metadata table after TL;DR line
    $c = [regex]::Replace($c, "(TL;DR - [^\r\n]+)(\r?\n)", "`$1$newTable`$2")

    # Fix _Hint:_ to *Hint:*
    $c = $c -replace '_Hint:_', '*Hint:*'

    [IO.File]::WriteAllText($f, $c, [Text.Encoding]::UTF8)
    Write-Host "$key`: done"
}
Write-Host "Batch 4 Entry Metadata removal complete."
