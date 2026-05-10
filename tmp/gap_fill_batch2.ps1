# Gap fill batch 2: BIG + MSG + CCH new stubs
# Run with: pwsh -ExecutionPolicy Bypass -File tmp\gap_fill_batch2.ps1
Set-Location 'c:\ASK\MyWorkspace\sk-keys'
$enc = [System.Text.UTF8Encoding]::new($false)

function Write-Stub($id, $title, $diff, $folder, $catName, $tier, $slug, $nav, $tags) {
    $tq = if ($title -match ': ') { "`"$title`"" } else { $title }
    $tagLines = ($tags | ForEach-Object { "  - $_" }) -join "`n"
    $code = $id.Split('-')[0]
    $catSlug = switch ($code) {
        'BIG' { 'big-data-streaming' }
        'MSG' { 'messaging-streaming' }
        'CCH' { 'caching' }
    }
    $content = @"
---
id: $id
title: $tq
category: $catName
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
parent: "$catName"
grand_parent: "Technical Dictionary"
nav_order: $nav
permalink: /$catSlug/$slug/
---
"@
    $safeName = $title -replace '[/\\:*?"<>|]', '-'
    $fp = "dictionary\$tier\$folder\$id - $safeName.md"
    [System.IO.File]::WriteAllText($fp, $content, $enc)
    Write-Host "Created: $id - $title"
}

# ─── BIG: Data lake, Spark SQL, Orchestration (BIG-058 to BIG-072) ──────────
$bigCat = 'Big Data & Streaming'
$bigFolder = 'BIG-bigdata-streaming'
$bigTier = 'tier-4-data'

Write-Stub 'BIG-058' 'Spark SQL'                               '★★☆' $bigFolder $bigCat $bigTier 'spark-sql'                           58  @('dataengineering','bigdata','intermediate')
Write-Stub 'BIG-059' 'PySpark API Fundamentals'                '★★☆' $bigFolder $bigCat $bigTier 'pyspark-api-fundamentals'            59  @('dataengineering','bigdata','python','intermediate')
Write-Stub 'BIG-060' 'Apache Parquet Format'                   '★★☆' $bigFolder $bigCat $bigTier 'apache-parquet-format'               60  @('dataengineering','bigdata','intermediate')
Write-Stub 'BIG-061' 'Apache ORC Format'                       '★★☆' $bigFolder $bigCat $bigTier 'apache-orc-format'                   61  @('dataengineering','bigdata','intermediate')
Write-Stub 'BIG-062' 'Apache Avro (Big Data Context)'          '★★☆' $bigFolder $bigCat $bigTier 'apache-avro-big-data-context'        62  @('dataengineering','bigdata','intermediate')
Write-Stub 'BIG-063' 'Delta Lake'                              '★★★' $bigFolder $bigCat $bigTier 'delta-lake'                          63  @('dataengineering','bigdata','advanced')
Write-Stub 'BIG-064' 'Apache Iceberg'                          '★★★' $bigFolder $bigCat $bigTier 'apache-iceberg'                      64  @('dataengineering','bigdata','advanced')
Write-Stub 'BIG-065' 'Apache Hudi'                             '★★★' $bigFolder $bigCat $bigTier 'apache-hudi'                         65  @('dataengineering','bigdata','advanced')
Write-Stub 'BIG-066' 'Data Lakehouse Architecture'             '★★★' $bigFolder $bigCat $bigTier 'data-lakehouse-architecture'         66  @('dataengineering','bigdata','architecture','advanced')
Write-Stub 'BIG-067' 'Databricks Platform'                     '★★★' $bigFolder $bigCat $bigTier 'databricks-platform'                 67  @('dataengineering','bigdata','advanced')
Write-Stub 'BIG-068' 'Apache Airflow (Orchestration)'          '★★☆' $bigFolder $bigCat $bigTier 'apache-airflow-orchestration'        68  @('dataengineering','bigdata','intermediate')
Write-Stub 'BIG-069' 'dbt (Data Build Tool)'                   '★★☆' $bigFolder $bigCat $bigTier 'dbt-data-build-tool'                 69  @('dataengineering','bigdata','intermediate')
Write-Stub 'BIG-070' 'Data Quality and Validation'             '★★★' $bigFolder $bigCat $bigTier 'data-quality-and-validation'         70  @('dataengineering','bigdata','advanced')
Write-Stub 'BIG-071' 'Streaming Data Pipeline Design Patterns' '★★★' $bigFolder $bigCat $bigTier 'streaming-data-pipeline-design'      71  @('dataengineering','bigdata','pattern','advanced')
Write-Stub 'BIG-072' 'Big Data Platform Cost Optimization'     '★★★' $bigFolder $bigCat $bigTier 'big-data-platform-cost-optimization' 72  @('dataengineering','bigdata','advanced')

# Update BIG index
$bigIdxPath = "dictionary\$bigTier\$bigFolder\index.md"
$bigIdx = [System.IO.File]::ReadAllText($bigIdxPath, [System.Text.Encoding]::UTF8)
$bigIdx = $bigIdx -replace '\*\*Keywords:\*\* BIG-001--BIG-057 \(35 terms\)', '**Keywords:** BIG-001--BIG-072 (50 terms)'
$newBigRows = @"
| BIG-058 | Spark SQL | ★★☆ |
| BIG-059 | PySpark API Fundamentals | ★★☆ |
| BIG-060 | Apache Parquet Format | ★★☆ |
| BIG-061 | Apache ORC Format | ★★☆ |
| BIG-062 | Apache Avro (Big Data Context) | ★★☆ |
| BIG-063 | Delta Lake | ★★★ |
| BIG-064 | Apache Iceberg | ★★★ |
| BIG-065 | Apache Hudi | ★★★ |
| BIG-066 | Data Lakehouse Architecture | ★★★ |
| BIG-067 | Databricks Platform | ★★★ |
| BIG-068 | Apache Airflow (Orchestration) | ★★☆ |
| BIG-069 | dbt (Data Build Tool) | ★★☆ |
| BIG-070 | Data Quality and Validation | ★★★ |
| BIG-071 | Streaming Data Pipeline Design Patterns | ★★★ |
| BIG-072 | Big Data Platform Cost Optimization | ★★★ |
"@
$bigIdx = $bigIdx.TrimEnd() + "`n" + $newBigRows.TrimStart()
[System.IO.File]::WriteAllText($bigIdxPath, $bigIdx, $enc)
Write-Host "Updated: BIG index (35 -> 50 terms)"

# ─── MSG: Kafka Connect, Schema Registry, Azure SB, etc. (MSG-034 to MSG-046) ─
$msgCat = 'Messaging & Event Streaming'
$msgFolder = 'MSG-messaging-streaming'
$msgTier = 'tier-4-data'

Write-Stub 'MSG-034' 'Kafka Connect'                              '★★☆' $msgFolder $msgCat $msgTier 'kafka-connect'                               34  @('messaging','kafka','intermediate')
Write-Stub 'MSG-035' 'Kafka Schema Registry'                      '★★☆' $msgFolder $msgCat $msgTier 'kafka-schema-registry'                       35  @('messaging','kafka','intermediate')
Write-Stub 'MSG-036' 'Azure Service Bus'                          '★★☆' $msgFolder $msgCat $msgTier 'azure-service-bus'                           36  @('messaging','azure','intermediate')
Write-Stub 'MSG-037' 'GCP Cloud Pub/Sub'                          '★★☆' $msgFolder $msgCat $msgTier 'gcp-cloud-pub-sub'                           37  @('messaging','gcp','intermediate')
Write-Stub 'MSG-038' 'ActiveMQ'                                   '★★☆' $msgFolder $msgCat $msgTier 'activemq'                                    38  @('messaging','intermediate')
Write-Stub 'MSG-039' 'AMQP Protocol'                              '★★☆' $msgFolder $msgCat $msgTier 'amqp-protocol'                               39  @('messaging','protocol','intermediate')
Write-Stub 'MSG-040' 'Message Priority and TTL'                   '★★☆' $msgFolder $msgCat $msgTier 'message-priority-and-ttl'                    40  @('messaging','intermediate')
Write-Stub 'MSG-041' 'Request-Reply Pattern'                      '★★☆' $msgFolder $msgCat $msgTier 'request-reply-pattern'                       41  @('messaging','pattern','intermediate')
Write-Stub 'MSG-042' 'Topic Exchange Routing (RabbitMQ Exchanges)' '★★☆' $msgFolder $msgCat $msgTier 'topic-exchange-routing-rabbitmq-exchanges'    42  @('messaging','rabbitmq','intermediate')
Write-Stub 'MSG-043' 'Message Serialization (Avro, Protobuf, JSON)' '★★☆' $msgFolder $msgCat $msgTier 'message-serialization-avro-protobuf-json'   43  @('messaging','intermediate')
Write-Stub 'MSG-044' 'Consumer Poll Loop and Backpressure'         '★★★' $msgFolder $msgCat $msgTier 'consumer-poll-loop-and-backpressure'          44  @('messaging','kafka','advanced')
Write-Stub 'MSG-045' 'Kafka Lag Monitoring and Consumer Health'    '★★★' $msgFolder $msgCat $msgTier 'kafka-lag-monitoring-and-consumer-health'     45  @('messaging','kafka','observability','advanced')
Write-Stub 'MSG-046' 'Messaging Architecture Selection Framework'  '★★★' $msgFolder $msgCat $msgTier 'messaging-architecture-selection-framework'   46  @('messaging','architecture','advanced')

# Update MSG index
$msgIdxPath = "dictionary\$msgTier\$msgFolder\index.md"
$msgIdx = [System.IO.File]::ReadAllText($msgIdxPath, [System.Text.Encoding]::UTF8)
$msgIdx = $msgIdx -replace '\*\*Keywords:\*\* MSG-001--MSG-033 \(33 terms\)', '**Keywords:** MSG-001--MSG-046 (46 terms)'
$newMsgRows = @"
| MSG-034 | Kafka Connect | ★★☆ |
| MSG-035 | Kafka Schema Registry | ★★☆ |
| MSG-036 | Azure Service Bus | ★★☆ |
| MSG-037 | GCP Cloud Pub/Sub | ★★☆ |
| MSG-038 | ActiveMQ | ★★☆ |
| MSG-039 | AMQP Protocol | ★★☆ |
| MSG-040 | Message Priority and TTL | ★★☆ |
| MSG-041 | Request-Reply Pattern | ★★☆ |
| MSG-042 | Topic Exchange Routing (RabbitMQ Exchanges) | ★★☆ |
| MSG-043 | Message Serialization (Avro, Protobuf, JSON) | ★★☆ |
| MSG-044 | Consumer Poll Loop and Backpressure | ★★★ |
| MSG-045 | Kafka Lag Monitoring and Consumer Health | ★★★ |
| MSG-046 | Messaging Architecture Selection Framework | ★★★ |
"@
$msgIdx = $msgIdx.TrimEnd() + "`n" + $newMsgRows.TrimStart()
[System.IO.File]::WriteAllText($msgIdxPath, $msgIdx, $enc)
Write-Host "Updated: MSG index (33 -> 46 terms)"

# ─── CCH: HTTP caching, CDN, Spring Cache, etc. (CCH-038 to CCH-047) ────────
$cchCat = 'Caching'
$cchFolder = 'CCH-caching'
$cchTier = 'tier-4-data'

Write-Stub 'CCH-038' 'HTTP Cache-Control Header'                  '★★☆' $cchFolder $cchCat $cchTier 'http-cache-control-header'                   38  @('caching','networking','intermediate')
Write-Stub 'CCH-039' 'ETag and Conditional Requests'              '★★☆' $cchFolder $cchCat $cchTier 'etag-and-conditional-requests'               39  @('caching','networking','intermediate')
Write-Stub 'CCH-040' 'CDN Caching (Edge Caching)'                 '★★☆' $cchFolder $cchCat $cchTier 'cdn-caching-edge-caching'                    40  @('caching','networking','intermediate')
Write-Stub 'CCH-041' 'Browser Caching Strategies'                 '★★☆' $cchFolder $cchCat $cchTier 'browser-caching-strategies'                  41  @('caching','frontend','intermediate')
Write-Stub 'CCH-042' 'Cache Busting Techniques'                   '★★☆' $cchFolder $cchCat $cchTier 'cache-busting-techniques'                    42  @('caching','frontend','intermediate')
Write-Stub 'CCH-043' 'Database Query Cache'                       '★★★' $cchFolder $cchCat $cchTier 'database-query-cache'                        43  @('caching','database','advanced')
Write-Stub 'CCH-044' 'Spring Cache Abstraction'                   '★★☆' $cchFolder $cchCat $cchTier 'spring-cache-abstraction'                    44  @('caching','spring','java','intermediate')
Write-Stub 'CCH-045' 'Object vs Fragment Caching'                 '★★☆' $cchFolder $cchCat $cchTier 'object-vs-fragment-caching'                  45  @('caching','pattern','intermediate')
Write-Stub 'CCH-046' 'Service Worker Cache (Offline-First)'       '★★★' $cchFolder $cchCat $cchTier 'service-worker-cache-offline-first'           46  @('caching','frontend','advanced')
Write-Stub 'CCH-047' 'Cache Observability and Monitoring'         '★★★' $cchFolder $cchCat $cchTier 'cache-observability-and-monitoring'           47  @('caching','observability','advanced')

# Update CCH index
$cchIdxPath = "dictionary\$cchTier\$cchFolder\index.md"
$cchIdx = [System.IO.File]::ReadAllText($cchIdxPath, [System.Text.Encoding]::UTF8)
$cchIdx = $cchIdx -replace '\*\*Keywords:\*\* CCH-001--CCH-037 \(37 terms\)', '**Keywords:** CCH-001--CCH-047 (47 terms)'
$newCchRows = @"
| CCH-038 | HTTP Cache-Control Header | ★★☆ |
| CCH-039 | ETag and Conditional Requests | ★★☆ |
| CCH-040 | CDN Caching (Edge Caching) | ★★☆ |
| CCH-041 | Browser Caching Strategies | ★★☆ |
| CCH-042 | Cache Busting Techniques | ★★☆ |
| CCH-043 | Database Query Cache | ★★★ |
| CCH-044 | Spring Cache Abstraction | ★★☆ |
| CCH-045 | Object vs Fragment Caching | ★★☆ |
| CCH-046 | Service Worker Cache (Offline-First) | ★★★ |
| CCH-047 | Cache Observability and Monitoring | ★★★ |
"@
$cchIdx = $cchIdx.TrimEnd() + "`n" + $newCchRows.TrimStart()
[System.IO.File]::WriteAllText($cchIdxPath, $cchIdx, $enc)
Write-Host "Updated: CCH index (37 -> 47 terms)"

Write-Host "`n=== Gap fill batch 2 complete ==="
Write-Host "BIG: +15 stubs (058-072)"
Write-Host "MSG: +13 stubs (034-046)"
Write-Host "CCH: +10 stubs (038-047)"
