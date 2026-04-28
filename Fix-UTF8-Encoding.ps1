# UTF-8 Encoding Fix Script
# This script fixes corrupted UTF-8 characters in markdown files

Get-ChildItem -Path "C:\ASK\MyWorkspace\sk-keys\docs" -Recurse -Filter "*.md" | ForEach-Object {
    $filePath = $_.FullName

    # Read with UTF-8 encoding
    $content = Get-Content -Path $filePath -Encoding UTF8 -Raw

    # Define replacement mappings for corrupted characters
    $replacements = @{
        'â˜•' = '☕'
        'ðŸ·ï¸' = '🏷️'
        'âš¡' = '⚡'
        'ðŸ"˜' = '📘'
        'ðŸŸ¢' = '🟢'
        'ðŸ"µ' = '🔵'
        'ðŸ"©' = '🔩'
        'ðŸ§' = '🧠'
        'ðŸ'»' = '💻'
        'ðŸ"„' = '📄'
        'ðŸ"¥' = '🔥'
        'ðŸ…' = '🔅'
        'ðŸ"' = '📋'
        'ðŸš€' = '🚀'
        'ðŸŽê‚ƒ' = '🎯'
        'ðŸ"„' = '📄'
        'â"Œâ"€â"€' = '┌──'
        'â"‚' = '│'
        'â"œâ"€' = '├─'
        'â""â"€' = '└─'
        'â"„' = '┄'
        'ðŸ˜' = '😊'
        'ðŸ"' = '🔔'
        '€â"€' = '─'
    }

    $modified = $false
    foreach ($oldChar in $replacements.Keys) {
        if ($content -match [regex]::Escape($oldChar)) {
            $content = $content -replace [regex]::Escape($oldChar), $replacements[$oldChar]
            $modified = $true
        }
    }

    if ($modified) {
        Write-Host "Fixing: $($_.Name)"
        Set-Content -Path $filePath -Value $content -Encoding UTF8
    }
}

Write-Host "`nAll files fixed!"

