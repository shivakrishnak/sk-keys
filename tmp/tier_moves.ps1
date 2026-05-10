# tier_moves.ps1 - Move ASY->Tier5, PLT->Tier6, fix all nav_order conflicts, add ASY-012 stub
# Run: pwsh -ExecutionPolicy Bypass -File tmp\tier_moves.ps1
Set-Location 'c:\ASK\MyWorkspace\sk-keys'
$enc = [System.Text.UTF8Encoding]::new($false)

# ─── Clean nav_order assignment for all 55 categories ────────────────────────
# Each category gets a globally unique nav_order 1-55 in tier sequence.
# ASY moves: tier-9 -> tier-5 (nav 26)
# PLT moves: tier-9 -> tier-6 (nav 39)
$navOrders = [ordered]@{
    # Tier 1
    'CSF-cs-fundamentals'              = 1
    'DSA-data-structures'              = 2
    'OSY-operating-systems'            = 3
    'LNX-linux'                        = 4
    # Tier 2
    'NET-networking'                   = 5
    'API-http-apis'                    = 6
    'SEC-security'                     = 7
    'IAM-iam-access'                   = 8
    'CRY-cryptography'                 = 9
    # Tier 3
    'JVM-java-jvm-internals'           = 10
    'JLG-java-language'                = 11
    'JCC-java-concurrency'             = 12
    'SPR-spring-core'                  = 13
    'JPH-jpa-hibernate'                = 14
    # Tier 4
    'DBF-database-fundamentals'        = 15
    'NDB-nosql-distributed'            = 16
    'CCH-caching'                      = 17
    'DAT-data-fundamentals'            = 18
    'BIG-bigdata-streaming'            = 19
    'MSG-messaging-streaming'          = 20
    # Tier 5 (ASY added here)
    'DST-distributed-systems'          = 21
    'MSV-microservices'                = 22
    'SYD-system-design'                = 23
    'SAP-software-architecture'        = 24
    'DPT-design-patterns'              = 25
    'ASY-async-background'             = 26
    # Tier 6 (PLT added here)
    'CTR-containers'                   = 27
    'K8S-kubernetes'                   = 28
    'AWS-cloud-aws'                    = 29
    'AZR-cloud-azure'                  = 30
    'GCP-cloud-gcp'                    = 31
    'CCD-cicd'                         = 32
    'GIT-git-branching'                = 33
    'MVN-maven-build'                  = 34
    'CDQ-code-quality'                 = 35
    'TST-testing'                      = 36
    'OBS-observability-sre'            = 37
    'IAC-infrastructure-code'          = 38
    'PLT-platform-swe'                 = 39
    # Tier 7
    'HTM-html'                         = 40
    'CSS-css'                          = 41
    'JSC-javascript'                   = 42
    'TSC-typescript'                   = 43
    'RCT-react'                        = 44
    'ANG-angular'                      = 45
    'NDJ-nodejs'                       = 46
    'NPM-npm-packages'                 = 47
    'WBP-webpack-build'                = 48
    # Tier 8
    'AIF-ai-foundations'               = 49
    'LLM-llms-prompt-eng'              = 50
    'RAG-rag-agents-llmops'            = 51
    'AIP-ai-product'                   = 52
    # Tier 9 (ASY+PLT moved out, 3 remain)
    'BHV-behavioral-leadership'        = 53
    'DGN-document-generation'          = 54
    'FIN-financial-domain'             = 55
}

# ─── STEP 1: Move ASY folder tier-9 -> tier-5 ────────────────────────────────
Write-Host "`n=== STEP 1: Move ASY to Tier 5 ==="
$asySrc = 'dictionary\tier-9-professional-domain\ASY-async-background'
$asyDst = 'dictionary\tier-5-distributed-architecture\ASY-async-background'
if (Test-Path $asySrc) {
    Move-Item $asySrc $asyDst
    Write-Host "  Moved: $asySrc -> $asyDst"
} else {
    Write-Host "  ASY already moved or not found"
}

# ─── STEP 2: Move PLT folder tier-9 -> tier-6 ────────────────────────────────
Write-Host "`n=== STEP 2: Move PLT to Tier 6 ==="
$pltSrc = 'dictionary\tier-9-professional-domain\PLT-platform-swe'
$pltDst = 'dictionary\tier-6-infrastructure-devops\PLT-platform-swe'
if (Test-Path $pltSrc) {
    Move-Item $pltSrc $pltDst
    Write-Host "  Moved: $pltSrc -> $pltDst"
} else {
    Write-Host "  PLT already moved or not found"
}

# ─── STEP 3: Update tier: field in ALL ASY entry files ────────────────────────
Write-Host "`n=== STEP 3: Update tier field in ASY files ==="
$asyFiles = Get-ChildItem "$asyDst\*.md" | Where-Object { $_.Name -ne 'index.md' }
foreach ($f in $asyFiles) {
    $raw = [System.IO.File]::ReadAllText($f.FullName, [System.Text.Encoding]::UTF8)
    $updated = $raw -replace '(?m)^tier:\s+tier-9-professional-domain', 'tier: tier-5-distributed-architecture'
    if ($updated -ne $raw) {
        [System.IO.File]::WriteAllText($f.FullName, $updated, $enc)
    }
}
Write-Host "  Updated tier field in $($asyFiles.Count) ASY files"

# ─── STEP 4: Update tier: field in ALL PLT entry files ────────────────────────
Write-Host "`n=== STEP 4: Update tier field in PLT files ==="
$pltFiles = Get-ChildItem "$pltDst\*.md" | Where-Object { $_.Name -ne 'index.md' }
foreach ($f in $pltFiles) {
    $raw = [System.IO.File]::ReadAllText($f.FullName, [System.Text.Encoding]::UTF8)
    $updated = $raw -replace '(?m)^tier:\s+tier-9-professional-domain', 'tier: tier-6-infrastructure-devops'
    if ($updated -ne $raw) {
        [System.IO.File]::WriteAllText($f.FullName, $updated, $enc)
    }
}
Write-Host "  Updated tier field in $($pltFiles.Count) PLT files"

# ─── STEP 5: Fix nav_order in ALL category index.md files ─────────────────────
Write-Host "`n=== STEP 5: Fix nav_orders in all category indexes ==="
$allCatDirs = Get-ChildItem 'dictionary\tier-*\*' -Directory
foreach ($d in $allCatDirs) {
    $idxPath = "$($d.FullName)\index.md"
    if (-not (Test-Path $idxPath)) { continue }
    $name = $d.Name
    if ($navOrders.Contains($name)) {
        $newNav = $navOrders[$name]
        $raw = [System.IO.File]::ReadAllText($idxPath, [System.Text.Encoding]::UTF8)
        $updated = $raw -replace '(?m)^nav_order:\s+\d+', "nav_order: $newNav"
        if ($updated -ne $raw) {
            [System.IO.File]::WriteAllText($idxPath, $updated, $enc)
            $oldNav = if ($raw -match '(?m)^nav_order:\s+(\d+)') { $Matches[1] } else { '?' }
            Write-Host ("  $name" + ": $oldNav -> $newNav")
        }
    } else {
        Write-Host "  WARNING: $name not in navOrders map!"
    }
}

# ─── STEP 6: Add ASY-012 stub ─────────────────────────────────────────────────
Write-Host "`n=== STEP 6: Add ASY-012 stub ==="
$asy012 = "$asyDst\ASY-012 - Amazon SQS (Simple Queue Service).md"
if (-not (Test-Path $asy012)) {
    $content = @"
---
id: ASY-012
title: Amazon SQS (Simple Queue Service)
category: Async & Background Processing
tier: tier-5-distributed-architecture
folder: ASY-async-background
difficulty: ★★☆
depends_on:
used_by:
related:
tags:
  - aws
  - async
  - messaging
  - cloud
status: draft
version: 0
layout: default
parent: "Async & Background Processing"
grand_parent: "Technical Dictionary"
nav_order: 12
permalink: /async-background/amazon-sqs/
---
"@
    [System.IO.File]::WriteAllText($asy012, $content, $enc)
    Write-Host "  Created: ASY-012 - Amazon SQS"
} else {
    Write-Host "  ASY-012 already exists"
}

# ─── STEP 7: Rebuild ASY index ────────────────────────────────────────────────
Write-Host "`n=== STEP 7: Rebuild ASY index ==="
$asyAllFiles = Get-ChildItem "$asyDst\*.md" | Where-Object { $_.Name -ne 'index.md' } | Sort-Object Name
$asyRows = foreach ($f in $asyAllFiles) {
    $raw = [System.IO.File]::ReadAllText($f.FullName, [System.Text.Encoding]::UTF8)
    $id = if ($raw -match '(?m)^id:\s+(\S+)') { $Matches[1] } else { '' }
    $title = if ($raw -match '(?m)^title:\s+"?([^"^\n]+)"?') { $Matches[1] } else { '' }
    $diff = if ($raw -match '(?m)^difficulty:\s+(.+)') { $Matches[1].Trim() } else { '' }
    if ($id) { "| $id | $title | $diff |" }
}
$asyMax = ($asyAllFiles | ForEach-Object { if ($_.Name -match '^ASY-(\d+)') { [int]$Matches[1] } } | Sort-Object -Descending | Select-Object -First 1)
$asyIdxContent = @"
---
layout: default
title: "Async & Background Processing"
parent: "Technical Dictionary"
nav_order: 26
has_children: true
permalink: /async-background/
---

# Async & Background Processing

Task queues, job workers, event-driven architecture, message broker patterns (RabbitMQ, Kafka, SQS, Celery), retry strategies, idempotency, dead letter queues, the Saga pattern, and async observability.

**Keywords:** ASY-001--ASY-$('{0:D3}' -f $asyMax) ($($asyAllFiles.Count) terms)

| ID | Keyword | Difficulty |
|----|---------|------------|
$($asyRows -join "`n")
"@
[System.IO.File]::WriteAllText("$asyDst\index.md", $asyIdxContent, $enc)
Write-Host "  ASY index rebuilt: $($asyAllFiles.Count) terms"

# ─── STEP 8: Rebuild PLT index ────────────────────────────────────────────────
Write-Host "`n=== STEP 8: Rebuild PLT index ==="
$pltAllFiles = Get-ChildItem "$pltDst\*.md" | Where-Object { $_.Name -ne 'index.md' } | Sort-Object Name
$pltRows = foreach ($f in $pltAllFiles) {
    $raw = [System.IO.File]::ReadAllText($f.FullName, [System.Text.Encoding]::UTF8)
    $id = if ($raw -match '(?m)^id:\s+(\S+)') { $Matches[1] } else { '' }
    $title = if ($raw -match '(?m)^title:\s+"?([^"^\n]+)"?') { $Matches[1] } else { '' }
    $diff = if ($raw -match '(?m)^difficulty:\s+(.+)') { $Matches[1].Trim() } else { '' }
    if ($id) { "| $id | $title | $diff |" }
}
$pltMax = ($pltAllFiles | ForEach-Object { if ($_.Name -match '^PLT-(\d+)') { [int]$Matches[1] } } | Sort-Object -Descending | Select-Object -First 1)
$pltIdxContent = @"
---
layout: default
title: "Platform & Modern SWE"
parent: "Technical Dictionary"
nav_order: 39
has_children: true
permalink: /platform-engineering/
---

# Platform & Modern SWE

Platform engineering, internal developer platforms (IDP), golden paths, developer experience (DX), DORA metrics, SPACE framework, release engineering, feature flags, monorepo tooling, incident management, progressive delivery, and FinOps.

**Keywords:** PLT-001--PLT-$('{0:D3}' -f $pltMax) ($($pltAllFiles.Count) terms)

| ID | Keyword | Difficulty |
|----|---------|------------|
$($pltRows -join "`n")
"@
[System.IO.File]::WriteAllText("$pltDst\index.md", $pltIdxContent, $enc)
Write-Host "  PLT index rebuilt: $($pltAllFiles.Count) terms"

# ─── Summary ──────────────────────────────────────────────────────────────────
Write-Host "`n=== Done ==="
Write-Host "ASY: $(Test-Path $asyDst) in tier-5"
Write-Host "PLT: $(Test-Path $pltDst) in tier-6"
Write-Host "ASY files: $((Get-ChildItem "$asyDst\ASY-*.md").Count)"
Write-Host "PLT files: $((Get-ChildItem "$pltDst\PLT-*.md").Count)"
Write-Host "Tier 9 remaining: $((Get-ChildItem 'dictionary\tier-9-professional-domain' -Directory).Count) categories"
