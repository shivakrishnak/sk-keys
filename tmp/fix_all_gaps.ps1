# Fix all remaining sync issues
# Run with: pwsh -ExecutionPolicy Bypass -File tmp\fix_all_gaps.ps1
Set-Location 'c:\ASK\MyWorkspace\sk-keys'
$enc = [System.Text.UTF8Encoding]::new($false)

# ─── 1. OBS-027: remove stub, keep content file ─────────────────────────────
$obsBase = 'dictionary\tier-6-infrastructure-devops\OBS-observability-sre'
$obsStub = "$obsBase\OBS-027 - AppDynamics -- APM.md"
if (Test-Path $obsStub) {
    Remove-Item $obsStub -Force
    Write-Host "Removed OBS-027 stub (content kept in AppDynamics.md)"
}

# ─── 2. AWS-065: rename bad file and add to index ───────────────────────────
$awsBase = 'dictionary\tier-6-infrastructure-devops\AWS-cloud-aws'
$badFile = "$awsBase\AWS-065 - 955b - Immutable Infrastructure.md"
$goodFile = "$awsBase\AWS-065 - Immutable Infrastructure.md"
if (Test-Path $badFile) {
    Rename-Item $badFile $goodFile -Force
    Write-Host "Renamed: AWS-065 - 955b... -> AWS-065 - Immutable Infrastructure.md"
}
# Fix the id in the file (it might still say something odd)
if (Test-Path $goodFile) {
    $raw = [System.IO.File]::ReadAllText($goodFile, [System.Text.Encoding]::UTF8)
    # Update id if it's wrong
    if ($raw -notmatch '^id: AWS-065' -and $raw -notmatch "`nid: AWS-065") {
        $raw = $raw -replace '(?m)^id:\s+\S+', 'id: AWS-065'
    }
    [System.IO.File]::WriteAllText($goodFile, $raw, $enc)
}
# Add AWS-065 to index
$awsIdx = [System.IO.File]::ReadAllText("$awsBase\index.md", [System.Text.Encoding]::UTF8)
if (-not ($awsIdx -match 'AWS-065')) {
    $awsIdx = $awsIdx.TrimEnd() + "`n| AWS-065 | Immutable Infrastructure | ★★★ |`n"
    [System.IO.File]::WriteAllText("$awsBase\index.md", $awsIdx, $enc)
    Write-Host "Added AWS-065 to index"
}

# ─── 3. RCT-024 duplicate: remove new stub, update index ────────────────────
$rctBase = 'dictionary\tier-7-frontend\RCT-react'
$rctDup = "$rctBase\RCT-024 - JSX Syntax and Rules.md"
if (Test-Path $rctDup) {
    Remove-Item $rctDup -Force
    Write-Host "Removed duplicate: RCT-024 - JSX Syntax and Rules.md"
}
# Remove duplicate row from index (keep "Component Design Thinking")
$rctIdx = [System.IO.File]::ReadAllText("$rctBase\index.md", [System.Text.Encoding]::UTF8)
$rctIdx = $rctIdx -replace "(?m)^\| RCT-024 \| JSX Syntax and Rules[^\n]+\n", ''
[System.IO.File]::WriteAllText("$rctBase\index.md", $rctIdx, $enc)
Write-Host "Fixed: RCT index (removed duplicate JSX Syntax row)"

# ─── 4. Create DPT stub files ────────────────────────────────────────────────
$dptBase = 'dictionary\tier-5-distributed-architecture\DPT-design-patterns'
$dptStubs = @(
    @{ id='DPT-081'; title='Anti-Pattern: Shotgun Surgery'; diff='★★☆'; slug='anti-pattern-shotgun-surgery'; nav=81 }
    @{ id='DPT-082'; title='Anti-Pattern: Feature Envy';    diff='★★☆'; slug='anti-pattern-feature-envy';    nav=82 }
    @{ id='DPT-083'; title='Anti-Pattern: Circular Dependencies'; diff='★★★'; slug='anti-pattern-circular-dependencies'; nav=83 }
)
foreach ($s in $dptStubs) {
    $fp = "$dptBase\$($s.id) - $($s.title).md"
    if (-not (Test-Path $fp)) {
        $content = @"
---
id: $($s.id)
title: "$($s.title)"
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: $($s.diff)
depends_on:
used_by:
related:
tags:
  - pattern
  - antipattern
  - bestpractice
status: draft
version: 0
layout: default
parent: "Design Patterns"
grand_parent: "Technical Dictionary"
nav_order: $($s.nav)
permalink: /design-patterns/$($s.slug)/
---
"@
        [System.IO.File]::WriteAllText($fp, $content, $enc)
        Write-Host "Created: $($s.id)"
    }
}

# ─── 5. Create DSA stub files ─────────────────────────────────────────────────
$dsaBase = 'dictionary\tier-1-foundations\DSA-data-structures'
$dsaStubs = @(
    @{ id='DSA-088'; title='PSPACE and EXPTIME -- Beyond P vs NP'; diff='★★★'; slug='pspace-and-exptime-beyond-p-vs-np'; nav=88 }
    @{ id='DSA-089'; title='Online Algorithms and Competitive Analysis'; diff='★★★'; slug='online-algorithms-and-competitive-analysis'; nav=89 }
)
foreach ($s in $dsaStubs) {
    $fp = "$dsaBase\$($s.id) - $($s.title).md"
    if (-not (Test-Path $fp)) {
        $content = @"
---
id: $($s.id)
title: "$($s.title)"
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: $($s.diff)
depends_on:
used_by:
related:
tags:
  - algorithm
  - advanced
  - deep-dive
status: draft
version: 0
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Dictionary"
nav_order: $($s.nav)
permalink: /data-structures/$($s.slug)/
---
"@
        [System.IO.File]::WriteAllText($fp, $content, $enc)
        Write-Host "Created: $($s.id)"
    }
}

Write-Host "`n=== All gaps fixed ==="
