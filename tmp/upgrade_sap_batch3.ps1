$d = "c:\ASK\MyWorkspace\sk-keys\dictionary\tier-5-distributed-architecture\SAP-software-architecture"

$metaData = @{
    "SAP-026" = @{ dep = "SAP-013, SAP-023, SAP-043"; used = "SAP-017, SAP-018"; rel = "SAP-021, SAP-027" }
    "SAP-027" = @{ dep = "SAP-023, SAP-043"; used = "-"; rel = "SAP-023, SAP-026, SAP-028" }
    "SAP-028" = @{ dep = "SAP-023, SAP-021"; used = "-"; rel = "SAP-021, SAP-029, SAP-027" }
    "SAP-029" = @{ dep = "SAP-021, SAP-023"; used = "SAP-021, SAP-022"; rel = "SAP-021, SAP-028" }
    "SAP-030" = @{ dep = "SAP-023, SAP-031, SAP-032, SAP-033"; used = "SAP-018, SAP-019"; rel = "SAP-031, SAP-032, SAP-033" }
    "SAP-031" = @{ dep = "SAP-023, SAP-030"; used = "SAP-018, SAP-019"; rel = "SAP-018, SAP-019, SAP-030" }
    "SAP-032" = @{ dep = "SAP-023, SAP-043"; used = "SAP-030"; rel = "SAP-030, SAP-033" }
    "SAP-033" = @{ dep = "SAP-023, SAP-032"; used = "SAP-030"; rel = "SAP-030, SAP-032" }
    "SAP-034" = @{ dep = "SAP-035, SAP-014"; used = "SAP-035"; rel = "SAP-035, SAP-037, SAP-038" }
    "SAP-035" = @{ dep = "SAP-034, SAP-036, SAP-037"; used = "SAP-034, SAP-036, SAP-037"; rel = "SAP-034, SAP-036, SAP-037, SAP-038" }
}

foreach ($key in ($metaData.Keys | Sort-Object)) {
    $f = (Get-ChildItem "$d\$key*")[0].FullName
    $c = [IO.File]::ReadAllText($f, [Text.Encoding]::UTF8)

    $m = $metaData[$key]
    $newTable = "`n`n| Field          | Value                              |`n| -------------- | ---------------------------------- |`n| **Depends on** | $($m.dep) |`n| **Used by**    | $($m.used) |`n| **Related**    | $($m.rel) |"

    # Remove the Entry Metadata block (---\n\n### Entry Metadata...\n\n---) up to the next ###
    $c = [regex]::Replace($c, "\r?\n---\r?\n\r?\n### [^\r\n]*Entry Metadata[\s\S]*?---\r?\n", "`n---`n")

    # Add new metadata table after TL;DR line
    $c = [regex]::Replace($c, "(TL;DR - [^\r\n]+)(\r?\n)", "`$1$newTable`$2")

    # Fix _Hint:_ to *Hint:*
    $c = $c -replace '_Hint:_', '*Hint:*'

    # Fix broken TW emoji if needed
    $c = [regex]::Replace($c, '### .{1,3}Transferable Wisdom', '### ' + [char]0xD83D + [char]0xDC8E + ' Transferable Wisdom')

    [IO.File]::WriteAllText($f, $c, [Text.Encoding]::UTF8)
    Write-Host "$key`: done"
}
Write-Host "Batch 3 Entry Metadata removal complete."
