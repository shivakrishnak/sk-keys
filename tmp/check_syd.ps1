$folder = "C:\ASK\MyWorkspace\sk-keys\dictionary\tier-5-distributed-architecture\SYD-system-design"
$files = Get-ChildItem $folder -Filter "SYD-*.md" | Sort-Object Name

$checks = @{
    "TL;DR" = "TL;DR"
    "Problem" = "The Problem This Solves"
    "Textbook" = "Textbook Definition"
    "30Sec" = "Understand It in 30 Seconds"
    "FirstPrinciples" = "First Principles"
    "ThoughtExp" = "Thought Experiment"
    "MentalModel" = "Mental Model"
    "GradualDepth" = "Gradual Depth"
    "Mechanism" = "How It Works"
    "CompletePicture" = "Complete Picture"
    "FailureModes" = "Failure Modes"
    "Related" = "Related Keywords"
    "QuickRef" = "Quick Reference"
    "Wisdom" = "Transferable Wisdom"
    "Surprising" = "Surprising Truth"
    "ThinkAbout" = "Think About This"
}

$results = @()

foreach ($file in $files) {
    $content = [System.IO.File]::ReadAllText($file.FullName)
    $lineCount = ($content -split "`n").Count
    $missing = @()

    foreach ($key in $checks.Keys) {
        if ($content -notmatch [regex]::Escape($checks[$key])) {
            $missing += $key
        }
    }

    if ($missing.Count -eq 0) {
        $status = "COMPLETE"
    } elseif ($lineCount -lt 50) {
        $status = "STUB"
    } else {
        $status = "PARTIAL"
    }

    $results += [PSCustomObject]@{
        File = $file.Name
        Lines = $lineCount
        Status = $status
        Missing = ($missing -join ", ")
    }

    Write-Host "$($file.Name) | Lines:$lineCount | $status | $($missing -join ', ')"
}

Write-Host ""
Write-Host "--- SUMMARY ---"
Write-Host "Total: $($results.Count)"
$incomplete = $results | Where-Object { $_.Status -ne "COMPLETE" }
Write-Host "Incomplete: $($incomplete.Count)"
foreach ($r in $incomplete) {
    Write-Host "  NEEDS WORK: $($r.File) ($($r.Status))"
}

