$sapDir = "c:\ASK\MyWorkspace\sk-keys\dictionary\tier-5-distributed-architecture\SAP-software-architecture"

# Map of SAP IDs to their v3.0 values
$upgrades = @{
    "SAP-016" = @{
        dependsOn = "SAP-014, SAP-015, SAP-023"
        usedBy    = "SAP-018, SAP-019"
        related   = "SAP-014, SAP-015, SAP-017"
    }
    "SAP-017" = @{
        dependsOn = "SAP-013, SAP-043"
        usedBy    = "SAP-039"
        related   = "SAP-013, SAP-014, SAP-015, SAP-018"
    }
    "SAP-018" = @{
        dependsOn = "SAP-049, SAP-023, SAP-031"
        usedBy    = "SAP-019"
        related   = "SAP-019, SAP-049, SAP-031"
    }
    "SAP-019" = @{
        dependsOn = "SAP-018, SAP-031"
        usedBy    = "SAP-018"
        related   = "SAP-018, SAP-030, SAP-031"
    }
    "SAP-020" = @{
        dependsOn = "SAP-013, SAP-043"
        usedBy    = "SAP-014"
        related   = "SAP-014, SAP-015, SAP-021, SAP-034"
    }
    "SAP-021" = @{
        dependsOn = "SAP-023, SAP-020, SAP-043"
        usedBy    = "SAP-022"
        related   = "SAP-022, SAP-029, SAP-023"
    }
    "SAP-022" = @{
        dependsOn = "SAP-021, SAP-023"
        usedBy    = "SAP-021"
        related   = "SAP-021, SAP-029"
    }
    "SAP-023" = @{
        dependsOn = "SAP-043, SAP-050, SAP-051"
        usedBy    = "SAP-024, SAP-025"
        related   = "SAP-024, SAP-025, SAP-030"
    }
    "SAP-024" = @{
        dependsOn = "SAP-023"
        usedBy    = "SAP-025"
        related   = "SAP-023, SAP-025"
    }
    "SAP-025" = @{
        dependsOn = "SAP-023, SAP-024"
        usedBy    = "SAP-030"
        related   = "SAP-023, SAP-030"
    }
}

foreach ($id in $upgrades.Keys) {
    $file = Get-ChildItem "$sapDir\$id*" | Select-Object -First 1
    if (-not $file) { Write-Host "NOT FOUND: $id"; continue }

    $content = [IO.File]::ReadAllText($file.FullName, [Text.Encoding]::UTF8)

    # 1. Remove the ### 📊 Entry Metadata section and replace with | Field | Value | table
    # Pattern: ---\n\n### 📊 Entry Metadata\n\n| #NNN ...\n...\n\n---\n\n### 🔥
    $do = $upgrades[$id].dependsOn
    $ub = $upgrades[$id].usedBy
    $re = $upgrades[$id].related

    $newMetaTable = "| Field | Value |`n|---|---|`n| **Depends on** | $do |`n| **Used by** | $ub |`n| **Related** | $re |`n`n---`n`n### 🔥 The Problem This Solves"

    # Use regex to replace the Entry Metadata block
    $content = [regex]::Replace(
        $content,
        '---\r?\n\r?\n### 📊 Entry Metadata\r?\n\r?\n[\s\S]*?\r?\n\r?\n---\r?\n\r?\n### 🔥 The Problem This Solves',
        $newMetaTable
    )

    # 2. Fix _Hint:_ -> *Hint:*
    $content = $content -replace '_Hint:_', '*Hint:*'

    # 3. Fix broken Transferable Wisdom emoji if present
    $content = [regex]::Replace($content, '### .{1,3}Transferable Wisdom', '### 💎 Transferable Wisdom')

    [IO.File]::WriteAllText($file.FullName, $content, [Text.Encoding]::UTF8)
    Write-Host "${id}: Entry Metadata removed, metadata table added"
}
