# MSG Category Migration Script
# Creates Messaging & Event Streaming category from BIG and ASY files
# Run with: pwsh -ExecutionPolicy Bypass -File tmp\create_msg_category.ps1

Set-Location 'c:\ASK\MyWorkspace\sk-keys'
$enc  = [System.Text.UTF8Encoding]::new($false)
$msgBase = 'dictionary\tier-4-data\MSG-messaging-streaming'
$bigBase = 'dictionary\tier-4-data\BIG-bigdata-streaming'
$asyBase = 'dictionary\tier-9-professional-domain\ASY-async-background'

New-Item -ItemType Directory -Force -Path $msgBase | Out-Null
Write-Host "Created folder: $msgBase"

# ─── Helper: migrate a file to MSG ──────────────────────────────────────────
function Migrate-File($srcPath, $newId, $newNavOrder, $newPermalinkSlug) {
    if (-not (Test-Path $srcPath)) { Write-Host "MISSING: $srcPath"; return }
    $raw = [System.IO.File]::ReadAllText($srcPath, [System.Text.Encoding]::UTF8)

    # Get old ID and title for H1 update
    $oldId = ''
    if ($raw -match '^id:\s+(\S+)'    ) { $oldId = $Matches[1] }
    elseif ($raw -match "`nid:\s+(\S+)") { $oldId = $Matches[1] }

    # Update frontmatter fields via string replacement
    $raw = $raw -replace '(?m)^id:\s+\S+',                        "id: $newId"
    $raw = $raw -replace '(?m)^category:\s+Big Data & Streaming',  'category: Messaging & Event Streaming'
    $raw = $raw -replace '(?m)^category:\s+Async & Background Processing', 'category: Messaging & Event Streaming'
    $raw = $raw -replace '(?m)^folder:\s+\S+',                     'folder: MSG-messaging-streaming'
    $raw = $raw -replace '(?m)^parent:\s+"Big Data & Streaming"',  'parent: "Messaging & Event Streaming"'
    $raw = $raw -replace '(?m)^parent:\s+"Async & Background Processing"', 'parent: "Messaging & Event Streaming"'
    $raw = $raw -replace '(?m)^tier:\s+\S+',                       'tier: tier-4-data'
    $raw = $raw -replace '(?m)^nav_order:\s+\d+',                  "nav_order: $newNavOrder"
    $raw = $raw -replace '(?m)^permalink:\s+/[^/]+/([^/]+)/',      "permalink: /messaging-streaming/$newPermalinkSlug/"
    # Fix case where permalink didn't match the pattern (absolute)
    if ($raw -match "permalink: /big-data-streaming/") {
        $raw = $raw -replace 'permalink: /big-data-streaming/([^/]+)/', "permalink: /messaging-streaming/$newPermalinkSlug/"
    }
    if ($raw -match "permalink: /async-background/") {
        $raw = $raw -replace 'permalink: /async-background/([^/]+)/', "permalink: /messaging-streaming/$newPermalinkSlug/"
    }

    # Update H1 heading (# BIG-015 → # MSG-006)
    if ($oldId) {
        $raw = $raw -replace "(?m)^# $([regex]::Escape($oldId))\s+-\s+", "# $newId - "
    }

    # Determine destination filename (keep original keyword name, just change ID prefix)
    $srcFile = Split-Path $srcPath -Leaf
    $newName = $srcFile -replace '^[A-Z]+-\d+\s+-\s+', "$newId - "
    $destPath = "$msgBase\$newName"

    [System.IO.File]::WriteAllText($destPath, $raw, $enc)
    Remove-Item $srcPath -Force
    Write-Host "Moved: $srcFile -> $newName"
}

# ─── 1. Create 5 MSG orientation stubs ──────────────────────────────────────
$orientations = @(
    @{ id='MSG-001'; nav=1; title='What Is Messaging -- The Communication Problem'; diff='★☆☆'; slug='what-is-messaging-the-communication-problem' }
    @{ id='MSG-002'; nav=2; title='The Messaging Ecosystem Map (Kafka, RabbitMQ, SQS, Pulsar)'; diff='★☆☆'; slug='the-messaging-ecosystem-map' }
    @{ id='MSG-003'; nav=3; title='When to Use Messaging vs REST vs RPC'; diff='★☆☆'; slug='when-to-use-messaging-vs-rest-vs-rpc' }
    @{ id='MSG-004'; nav=4; title='Delivery Guarantees Mental Model (At-Least-Once, Exactly-Once)'; diff='★☆☆'; slug='delivery-guarantees-mental-model' }
    @{ id='MSG-005'; nav=5; title='Messaging in Production -- What Engineers Face'; diff='★☆☆'; slug='messaging-in-production-what-engineers-face' }
)
foreach ($o in $orientations) {
    $tq = if ($o.title -match ': ') { "`"$($o.title)`"" } else { $o.title }
    $content = @"
---
id: $($o.id)
title: $tq
category: Messaging & Event Streaming
tier: tier-4-data
folder: MSG-messaging-streaming
difficulty: $($o.diff)
depends_on:
used_by:
related:
tags:
  - messaging
  - foundational
status: draft
version: 0
layout: default
parent: "Messaging & Event Streaming"
grand_parent: "Technical Dictionary"
nav_order: $($o.nav)
permalink: /messaging-streaming/$($o.slug)/
---
"@
    $fp = "$msgBase\$($o.id) - $($o.title).md"
    [System.IO.File]::WriteAllText($fp, $content, $enc)
    Write-Host "Created stub: $($o.id)"
}

# ─── 2. Migrate BIG messaging files → MSG-006 to MSG-027 ─────────────────────
$bigMoves = @(
    @{ src='BIG-015 - Apache Kafka.md';                           newId='MSG-006'; nav=6;  slug='apache-kafka' }
    @{ src='BIG-016 - Kafka Topic  Partition  Offset.md';         newId='MSG-007'; nav=7;  slug='kafka-topic-partition-offset' }
    @{ src='BIG-017 - Consumer Group.md';                         newId='MSG-008'; nav=8;  slug='consumer-group' }
    @{ src='BIG-018 - ISR (In-Sync Replicas).md';                 newId='MSG-009'; nav=9;  slug='isr-in-sync-replicas' }
    @{ src='BIG-019 - Log Compaction.md';                         newId='MSG-010'; nav=10; slug='log-compaction' }
    @{ src='BIG-020 - Exactly-Once Semantics.md';                 newId='MSG-011'; nav=11; slug='exactly-once-semantics' }
    @{ src='BIG-021 - Kafka Streams.md';                          newId='MSG-012'; nav=12; slug='kafka-streams' }
    @{ src='BIG-022 - KSQL.md';                                   newId='MSG-013'; nav=13; slug='ksql' }
    @{ src='BIG-023 - Consumer Lag.md';                           newId='MSG-014'; nav=14; slug='consumer-lag' }
    @{ src='BIG-024 - Idempotent Producer.md';                    newId='MSG-015'; nav=15; slug='idempotent-producer' }
    @{ src='BIG-025 - Transactional Producer.md';                 newId='MSG-016'; nav=16; slug='transactional-producer' }
    @{ src='BIG-026 - Dead Letter Queue (DLQ).md';                newId='MSG-017'; nav=17; slug='dead-letter-queue-dlq' }
    @{ src='BIG-027 - Fan-Out Pattern.md';                        newId='MSG-018'; nav=18; slug='fan-out-pattern' }
    @{ src='BIG-028 - Message Ordering.md';                       newId='MSG-019'; nav=19; slug='message-ordering' }
    @{ src='BIG-037 - Pulsar.md';                                 newId='MSG-020'; nav=20; slug='pulsar' }
    @{ src='BIG-038 - RabbitMQ.md';                               newId='MSG-021'; nav=21; slug='rabbitmq' }
    @{ src='BIG-039 - Message Broker vs Event Bus.md';            newId='MSG-022'; nav=22; slug='message-broker-vs-event-bus' }
    @{ src='BIG-040 - Point-to-Point vs Pub-Sub.md';              newId='MSG-023'; nav=23; slug='point-to-point-vs-pub-sub' }
    @{ src='BIG-041 - Competing Consumers.md';                    newId='MSG-024'; nav=24; slug='competing-consumers' }
    @{ src='BIG-042 - Outbox Pattern.md';                         newId='MSG-025'; nav=25; slug='outbox-pattern' }
    @{ src='BIG-043 - Transactional Outbox.md';                   newId='MSG-026'; nav=26; slug='transactional-outbox' }
    @{ src='BIG-044 - Event-Driven Architecture.md';              newId='MSG-027'; nav=27; slug='event-driven-architecture' }
)
foreach ($m in $bigMoves) {
    Migrate-File "$bigBase\$($m.src)" $m.newId $m.nav $m.slug
}

# ─── 3. Migrate ASY messaging files → MSG-028 to MSG-033 ─────────────────────
$asyMoves = @(
    @{ src='ASY-012 - AWS SQS and SNS.md';                                              newId='MSG-028'; nav=28; slug='aws-sqs-and-sns' }
    @{ src='ASY-023 - Message Schema Evolution (Avro, Protobuf).md';                    newId='MSG-029'; nav=29; slug='message-schema-evolution-avro-protobuf' }
    @{ src='ASY-024 - Poison Pill Messages and Circuit Breaker.md';                     newId='MSG-030'; nav=30; slug='poison-pill-messages-and-circuit-breaker' }
    @{ src='ASY-027 - Message Deduplication.md';                                        newId='MSG-031'; nav=31; slug='message-deduplication' }
    @{ src='ASY-038 - Kafka Internals Deep Dive (Replication, ISR, Log Compaction).md'; newId='MSG-032'; nav=32; slug='kafka-internals-deep-dive' }
    @{ src='ASY-039 - Message Queue Algorithm Research.md';                             newId='MSG-033'; nav=33; slug='message-queue-algorithm-research' }
)
foreach ($m in $asyMoves) {
    Migrate-File "$asyBase\$($m.src)" $m.newId $m.nav $m.slug
}

# ─── 4. Create MSG index.md ──────────────────────────────────────────────────
$msgIndex = @'
---
layout: default
title: "Messaging & Event Streaming"
parent: "Technical Dictionary"
nav_order: 16
has_children: true
permalink: /messaging-streaming/
---

# Messaging & Event Streaming

Message brokers, event streaming, Kafka internals, RabbitMQ, SQS/SNS, Pulsar, messaging patterns (DLQ, outbox, fan-out, ordering), and event-driven architecture.

**Keywords:** MSG-001--MSG-033 (33 terms)

| ID | Keyword | Difficulty |
|----|---------|------------|
| MSG-001 | What Is Messaging -- The Communication Problem | ★☆☆ |
| MSG-002 | The Messaging Ecosystem Map (Kafka, RabbitMQ, SQS, Pulsar) | ★☆☆ |
| MSG-003 | When to Use Messaging vs REST vs RPC | ★☆☆ |
| MSG-004 | Delivery Guarantees Mental Model (At-Least-Once, Exactly-Once) | ★☆☆ |
| MSG-005 | Messaging in Production -- What Engineers Face | ★☆☆ |
| MSG-006 | Apache Kafka | ★★☆ |
| MSG-007 | Kafka Topic / Partition / Offset | ★★☆ |
| MSG-008 | Consumer Group | ★★☆ |
| MSG-009 | ISR (In-Sync Replicas) | ★★★ |
| MSG-010 | Log Compaction | ★★★ |
| MSG-011 | Exactly-Once Semantics | ★★★ |
| MSG-012 | Kafka Streams | ★★★ |
| MSG-013 | KSQL | ★★★ |
| MSG-014 | Consumer Lag | ★★★ |
| MSG-015 | Idempotent Producer | ★★★ |
| MSG-016 | Transactional Producer | ★★★ |
| MSG-017 | Dead Letter Queue (DLQ) | ★★☆ |
| MSG-018 | Fan-Out Pattern | ★★☆ |
| MSG-019 | Message Ordering | ★★★ |
| MSG-020 | Pulsar | ★★★ |
| MSG-021 | RabbitMQ | ★★☆ |
| MSG-022 | Message Broker vs Event Bus | ★★☆ |
| MSG-023 | Point-to-Point vs Pub-Sub | ★★☆ |
| MSG-024 | Competing Consumers | ★★☆ |
| MSG-025 | Outbox Pattern | ★★★ |
| MSG-026 | Transactional Outbox | ★★★ |
| MSG-027 | Event-Driven Architecture | ★★★ |
| MSG-028 | AWS SQS and SNS | ★☆☆ |
| MSG-029 | Message Schema Evolution (Avro, Protobuf) | ★★☆ |
| MSG-030 | Poison Pill Messages and Circuit Breaker | ★★☆ |
| MSG-031 | Message Deduplication | ★★☆ |
| MSG-032 | Kafka Internals Deep Dive (Replication, ISR, Log Compaction) | ★★★ |
| MSG-033 | Message Queue Algorithm Research | ★★★ |
'@
[System.IO.File]::WriteAllText("$msgBase\index.md", $msgIndex, $enc)
Write-Host "`nCreated: MSG index.md"

# ─── 5. Update BIG index.md ──────────────────────────────────────────────────
$bigIdxPath = "$bigBase\index.md"
$bigIdx = [System.IO.File]::ReadAllText($bigIdxPath, [System.Text.Encoding]::UTF8)

# Remove moved rows (BIG-015 to BIG-028, BIG-037 to BIG-044)
$idsToRemove = @(15,16,17,18,19,20,21,22,23,24,25,26,27,28,37,38,39,40,41,42,43,44)
foreach ($n in $idsToRemove) {
    $pad = $n.ToString('D3')
    $bigIdx = $bigIdx -replace "(?m)^\| BIG-$pad \|[^\n]+\n", ''
}

# Update keyword count: 57 - 22 = 35 terms
$bigIdx = $bigIdx -replace '\*\*Keywords:\*\*\s+BIG-001[^(]+\(\d+ terms\)',
    '**Keywords:** BIG-001--BIG-057 (35 terms)'

[System.IO.File]::WriteAllText($bigIdxPath, $bigIdx, $enc)
Write-Host "Updated: BIG index.md (57 -> 35 terms, removed 22 moved entries)"

# ─── 6. Update ASY index.md ──────────────────────────────────────────────────
$asyIdxPath = "$asyBase\index.md"
$asyIdx = [System.IO.File]::ReadAllText($asyIdxPath, [System.Text.Encoding]::UTF8)

# Remove moved ASY rows (012, 023, 024, 027, 038, 039)
foreach ($n in @(12,23,24,27,38,39)) {
    $pad = $n.ToString('D2')
    $asyIdx = $asyIdx -replace "(?m)^\| ASY-0$pad \|[^\n]+\n", ''
}

# Update keyword count: 44 - 6 = 38 terms
$asyIdx = $asyIdx -replace '\*\*Keywords:\*\*\s+ASY-001[^(]+\(\d+ terms\)',
    '**Keywords:** ASY-001--ASY-044 (38 terms)'

[System.IO.File]::WriteAllText($asyIdxPath, $asyIdx, $enc)
Write-Host "Updated: ASY index.md (44 -> 38 terms, removed 6 moved entries)"

Write-Host "`n=== MSG category creation complete ==="
Write-Host "MSG: 33 terms (5 new orientation + 22 from BIG + 6 from ASY)"
Write-Host "BIG: 35 terms remaining"
Write-Host "ASY: 38 terms remaining"
