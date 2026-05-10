# ALWAYS run with: pwsh -ExecutionPolicy Bypass -File tmp\create_gap_stubs.ps1
Set-Location 'c:\ASK\MyWorkspace\sk-keys'
$enc = [System.Text.UTF8Encoding]::new($false)

function Write-Stub($fp, $id, $title, $cat, $tier, $folder, $diff, $parent, $tags, $slug, $nav) {
    $titleVal = if ($title -match ': ') { "`"$title`"" } else { $title }
    $tagLines = ($tags | ForEach-Object { "  - $_" }) -join "`n"
    $c = @"
---
id: $id
title: $titleVal
category: $cat
tier: $tier
folder: $folder
difficulty: $diff
depends_on:
used_by:
related:
tags:
$tagLines
status: draft
version: 0
layout: default
parent: "$parent"
grand_parent: "Technical Dictionary"
nav_order: $nav
permalink: /$slug/
---
"@
    [System.IO.File]::WriteAllText($fp, $c, $enc)
}

$created = 0

# ── SYD gap fill: SYD-063 to SYD-077 ────────────────────────────────────────
$sydBase = "dictionary\tier-5-distributed-architecture\SYD-system-design"
$sydStubs = @(
    @{ n=63; t="What is Scalability (Conceptual)";                   d="★☆☆";  tags=@("architecture","foundational","mental-model") }
    @{ n=64; t="What is a Cache (System Design Context)";            d="★☆☆";  tags=@("caching","foundational","mental-model") }
    @{ n=65; t="What is a Message Queue (Conceptual)";               d="★☆☆";  tags=@("messaging","foundational","mental-model") }
    @{ n=66; t="What is Database Replication (Basic)";               d="★☆☆";  tags=@("database","foundational","mental-model") }
    @{ n=67; t="CDN Architecture Pattern";                           d="★★☆";  tags=@("architecture","performance","intermediate") }
    @{ n=68; t="Connection Pooling (System Design)";                 d="★★☆";  tags=@("database","performance","intermediate") }
    @{ n=69; t="Cache Invalidation Strategies";                      d="★★★";  tags=@("caching","advanced","pattern") }
    @{ n=70; t="Blob Storage Design";                                d="★★☆";  tags=@("architecture","distributed","intermediate") }
    @{ n=71; t="Payment System Design";                              d="★★★";  tags=@("architecture","distributed","advanced") }
    @{ n=72; t="File Storage System Design (Dropbox/S3)";            d="★★★";  tags=@("architecture","distributed","advanced") }
    @{ n=73; t="Email System Design";                                d="★★★";  tags=@("architecture","distributed","advanced") }
    @{ n=74; t="Game Leaderboard Design";                            d="★★★";  tags=@("architecture","distributed","advanced") }
    @{ n=75; t="Booking and Reservation System Design";              d="★★★";  tags=@("architecture","distributed","advanced") }
    @{ n=76; t="Real-Time Collaboration System Design";              d="★★★";  tags=@("architecture","distributed","advanced") }
    @{ n=77; t="Global Key-Value Store Design";                      d="★★★";  tags=@("architecture","distributed","advanced") }
)
foreach ($s in $sydStubs) {
    $id  = "SYD-0$($s.n)"
    $slug = "system-design/$(($s.t -replace '[^a-zA-Z0-9 ]','') -replace ' +','-' | ForEach-Object { $_.ToLower() })"
    $fp  = "$sydBase\$id - $($s.t).md"
    if (-not (Test-Path $fp)) {
        Write-Stub $fp $id $s.t "System Design" "tier-5-distributed-architecture" "SYD-system-design" `
            $s.d "System Design" $s.tags $slug $s.n
        Write-Host "Created: $fp"
        $created++
    } else { Write-Host "EXISTS:  $(Split-Path $fp -Leaf)" }
}

# ── DPT gap fill: DPT-073 to DPT-084 ────────────────────────────────────────
$dptBase = "dictionary\tier-5-distributed-architecture\DPT-design-patterns"
$dptStubs = @(
    @{ n=73; t="Dependency Inversion vs Dependency Injection";       d="★★★"; tags=@("pattern","advanced","bestpractice") }
    @{ n=74; t="SOLID - Single Responsibility Principle";            d="★★☆"; tags=@("pattern","intermediate","bestpractice") }
    @{ n=75; t="SOLID - Open/Closed Principle";                      d="★★☆"; tags=@("pattern","intermediate","bestpractice") }
    @{ n=76; t="SOLID - Liskov Substitution Principle";              d="★★★"; tags=@("pattern","advanced","bestpractice") }
    @{ n=77; t="SOLID - Interface Segregation Principle";            d="★★☆"; tags=@("pattern","intermediate","bestpractice") }
    @{ n=78; t="SOLID - Dependency Inversion Principle";             d="★★★"; tags=@("pattern","advanced","bestpractice") }
    @{ n=79; t="Repository Pattern";                                 d="★★☆"; tags=@("pattern","intermediate","architecture") }
    @{ n=80; t="Reactor Pattern";                                    d="★★★"; tags=@("pattern","advanced","concurrency") }
    @{ n=81; t="Anti-Pattern: Shotgun Surgery";                      d="★★☆"; tags=@("antipattern","intermediate","bestpractice") }
    @{ n=82; t="Anti-Pattern: Feature Envy";                         d="★★☆"; tags=@("antipattern","intermediate","bestpractice") }
    @{ n=83; t="Anti-Pattern: Circular Dependencies";                d="★★★"; tags=@("antipattern","advanced","architecture") }
    @{ n=84; t="Inbox Pattern";                                      d="★★★"; tags=@("pattern","advanced","distributed") }
)
foreach ($s in $dptStubs) {
    $id  = "DPT-0$($s.n)"
    $slug = "design-patterns/$(($s.t -replace '[^a-zA-Z0-9 ]','') -replace ' +','-' | ForEach-Object { $_.ToLower() })"
    $fp  = "$dptBase\$id - $($s.t).md"
    if (-not (Test-Path $fp)) {
        Write-Stub $fp $id $s.t "Design Patterns" "tier-5-distributed-architecture" "DPT-design-patterns" `
            $s.d "Design Patterns" $s.tags $slug $s.n
        Write-Host "Created: $fp"
        $created++
    } else { Write-Host "EXISTS:  $(Split-Path $fp -Leaf)" }
}

# ── DST gap fill: DST-078 to DST-085 ────────────────────────────────────────
$dstBase = "dictionary\tier-5-distributed-architecture\DST-distributed-systems"
$dstStubs = @(
    @{ n=78; t="Replication Lag";                                    d="★★★"; tags=@("distributed","database","advanced") }
    @{ n=79; t="Write-Ahead Log (Distributed)";                      d="★★★"; tags=@("distributed","database","advanced") }
    @{ n=80; t="Distributed Rate Limiting";                          d="★★★"; tags=@("distributed","advanced","pattern") }
    @{ n=81; t="Phi Accrual Failure Detector";                       d="★★★"; tags=@("distributed","advanced","algorithm") }
    @{ n=82; t="Global Sequence Number";                             d="★★★"; tags=@("distributed","advanced","pattern") }
    @{ n=83; t="Distributed Cache Coherence";                        d="★★★"; tags=@("distributed","caching","advanced") }
    @{ n=84; t="Compaction in Distributed Logs";                     d="★★★"; tags=@("distributed","advanced","internals") }
    @{ n=85; t="Deterministic Simulation Testing";                   d="★★★"; tags=@("distributed","testing","advanced") }
)
foreach ($s in $dstStubs) {
    $id  = "DST-0$($s.n)"
    $slug = "distributed-systems/$(($s.t -replace '[^a-zA-Z0-9 ]','') -replace ' +','-' | ForEach-Object { $_.ToLower() })"
    $fp  = "$dstBase\$id - $($s.t).md"
    if (-not (Test-Path $fp)) {
        Write-Stub $fp $id $s.t "Distributed Systems" "tier-5-distributed-architecture" "DST-distributed-systems" `
            $s.d "Distributed Systems" $s.tags $slug $s.n
        Write-Host "Created: $fp"
        $created++
    } else { Write-Host "EXISTS:  $(Split-Path $fp -Leaf)" }
}

# ── MSV gap fill: MSV-078 to MSV-085 ────────────────────────────────────────
$msvBase = "dictionary\tier-5-distributed-architecture\MSV-microservices"
$msvStubs = @(
    @{ n=78; t="Platform Engineering";                               d="★★★"; tags=@("microservices","devops","advanced") }
    @{ n=79; t="Internal Developer Platform (IDP)";                  d="★★★"; tags=@("microservices","devops","advanced") }
    @{ n=80; t="GraphQL Federation (Microservices)";                 d="★★★"; tags=@("microservices","api","advanced") }
    @{ n=81; t="Dead Letter Queue Strategy";                         d="★★★"; tags=@("microservices","messaging","advanced") }
    @{ n=82; t="Progressive Delivery";                               d="★★★"; tags=@("microservices","cicd","advanced") }
    @{ n=83; t="Multi-Tenancy in Microservices";                     d="★★★"; tags=@("microservices","architecture","advanced") }
    @{ n=84; t="FinOps for Microservices";                           d="★★★"; tags=@("microservices","cloud","advanced") }
    @{ n=85; t="Service Catalog";                                    d="★★☆"; tags=@("microservices","intermediate","pattern") }
)
foreach ($s in $msvStubs) {
    $id  = "MSV-0$($s.n)"
    $slug = "microservices/$(($s.t -replace '[^a-zA-Z0-9 ]','') -replace ' +','-' | ForEach-Object { $_.ToLower() })"
    $fp  = "$msvBase\$id - $($s.t).md"
    if (-not (Test-Path $fp)) {
        Write-Stub $fp $id $s.t "Microservices" "tier-5-distributed-architecture" "MSV-microservices" `
            $s.d "Microservices" $s.tags $slug $s.n
        Write-Host "Created: $fp"
        $created++
    } else { Write-Host "EXISTS:  $(Split-Path $fp -Leaf)" }
}

# ── SAP gap fill: SAP-077 to SAP-086 ────────────────────────────────────────
$sapBase = "dictionary\tier-5-distributed-architecture\SAP-software-architecture"
$sapStubs = @(
    @{ n=77; t="Conway's Law";                                       d="★★☆"; tags=@("architecture","intermediate","mental-model") }
    @{ n=78; t="Inverse Conway Maneuver";                            d="★★★"; tags=@("architecture","advanced","pattern") }
    @{ n=79; t="Technical Debt Quantification";                      d="★★★"; tags=@("architecture","advanced","bestpractice") }
    @{ n=80; t="Architecture Trade-off Analysis Method (ATAM)";      d="★★★"; tags=@("architecture","advanced","pattern") }
    @{ n=81; t="Software Architecture Anti-Patterns";                d="★★★"; tags=@("antipattern","advanced","architecture") }
    @{ n=82; t="Feature Toggle Architecture";                        d="★★☆"; tags=@("architecture","intermediate","pattern") }
    @{ n=83; t="Strangler Fig for Monolith-to-Service Migration";    d="★★★"; tags=@("architecture","advanced","pattern") }
    @{ n=84; t="Service-Oriented Architecture (SOA)";                d="★★☆"; tags=@("architecture","intermediate","pattern") }
    @{ n=85; t="API-First Architecture";                             d="★★☆"; tags=@("architecture","intermediate","bestpractice") }
    @{ n=86; t="Composable Architecture";                            d="★★★"; tags=@("architecture","advanced","pattern") }
)
foreach ($s in $sapStubs) {
    $id  = "SAP-0$($s.n)"
    $slug = "software-architecture/$(($s.t -replace '[^a-zA-Z0-9 ]','') -replace ' +','-' | ForEach-Object { $_.ToLower() })"
    $fp  = "$sapBase\$id - $($s.t).md"
    if (-not (Test-Path $fp)) {
        Write-Stub $fp $id $s.t "Software Architecture Patterns" "tier-5-distributed-architecture" "SAP-software-architecture" `
            $s.d "Software Architecture Patterns" $s.tags $slug $s.n
        Write-Host "Created: $fp"
        $created++
    } else { Write-Host "EXISTS:  $(Split-Path $fp -Leaf)" }
}

# ── CSF gap fill: CSF-081 to CSF-085 ────────────────────────────────────────
$csfBase = "dictionary\tier-1-foundations\CSF-cs-fundamentals"
$csfStubs = @(
    @{ n=81; t="Abstraction Levels in Computing";                    d="★☆☆"; tags=@("foundational","mental-model","first-principles") }
    @{ n=82; t="Computational Complexity Overview";                  d="★★☆"; tags=@("algorithm","intermediate","foundational") }
    @{ n=83; t="Formal Reasoning in Software";                       d="★★★"; tags=@("advanced","deep-dive","first-principles") }
    @{ n=84; t="Software Correctness and Proof";                     d="★★★"; tags=@("advanced","deep-dive","foundational") }
    @{ n=85; t="Cross-Paradigm Design Patterns";                     d="★★★"; tags=@("pattern","advanced","mental-model") }
)
foreach ($s in $csfStubs) {
    $id  = "CSF-0$($s.n)"
    $slug = "cs-fundamentals/$(($s.t -replace '[^a-zA-Z0-9 ]','') -replace ' +','-' | ForEach-Object { $_.ToLower() })"
    $fp  = "$csfBase\$id - $($s.t).md"
    if (-not (Test-Path $fp)) {
        Write-Stub $fp $id $s.t "CS Fundamentals - Paradigms" "tier-1-foundations" "CSF-cs-fundamentals" `
            $s.d "CS Fundamentals - Paradigms" $s.tags $slug $s.n
        Write-Host "Created: $fp"
        $created++
    } else { Write-Host "EXISTS:  $(Split-Path $fp -Leaf)" }
}

Write-Host "`nTotal created: $created"
