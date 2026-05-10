$dictRoot = "c:\ASK\MyWorkspace\sk-keys\dictionary"
$results = @()

# V4.0 marker patterns
$v4Patterns = @{
    "GradualDepth5" = "Gradual Depth.*Five Levels"
    "MasteryChecklist" = "Mastery Checklist"
    "AntiPatternRow" = "\| ANTI-PATTERN \|"
    "IndustryApps" = "\*\*Industry applications"
    "TypeG" = "TYPE G"
}

Get-ChildItem -Path $dictRoot -Recurse -Filter "*.md" | Where-Object { $_.Name -ne "index.md" } | ForEach-Object {
    $file = $_
    $content = Get-Content -Path $file.FullName -Raw -Encoding UTF8

    $markers = @{}
    foreach ($pattern in $v4Patterns.Keys) {
        $markers[$pattern] = ($content -match $v4Patterns[$pattern])
    }

    $markerCount = ($markers.Values | Where-Object { $_ -eq $true } | Measure-Object).Count

    if ($markerCount -ge 3) {
        $results += [PSCustomObject]@{
            FileName = $file.Name
            FilePath = $file.FullName
            GradualDepth5 = $markers["GradualDepth5"]
            MasteryChecklist = $markers["MasteryChecklist"]
            AntiPatternRow = $markers["AntiPatternRow"]
            IndustryApps = $markers["IndustryApps"]
            TypeG = $markers["TypeG"]
            V4MarkerCount = $markerCount
        }
    }
}

Write-Host "Files with 3+ v4.0 markers: $($results.Count)"
$results | Select-Object -First 10 | ForEach-Object {
    Write-Host "$($_.FileName) - $($_.V4MarkerCount) markers"
}

if ($results.Count -gt 0) {
    Write-Host ""
    Write-Host "Total v4.0-ready files: $($results.Count)"
    $results | Export-Csv -Path "c:\ASK\MyWorkspace\sk-keys\tmp\v4_ready_files.csv" -Encoding UTF8 -NoTypeInformation
}
