---
id: OBS-019
title: "ELK / EFK Stack -- Log Management"
category: Observability & SRE
tier: tier-6-infrastructure-devops
folder: OBS-observability-sre
difficulty: ★★☆
depends_on: OBS-007, OBS-001
used_by: OBS-018, OBS-009
related: OBS-007, OBS-018, OBS-015, OBS-016
tags:
  - observability
  - logging
  - devops
  - pattern
  - intermediate
status: complete
version: 4
layout: default
parent: "Observability & SRE"
grand_parent: "Technical Dictionary"
nav_order: 19
permalink: /obs/elk-efk-stack-log-management/
---

# OBS-019 - ELK / EFK Stack -- Log Management

⚡ TL;DR - The ELK stack (Elasticsearch + Logstash

- Kibana) and its Kubernetes variant EFK (Fluentd
  replaces Logstash) provide centralised log aggregation,
  full-text search, and visualisation. They are the
  most widely deployed log management solution for
  cloud-native applications.

| #019            | Category: Observability & SRE                            | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------------- | :-------------- |
| **Depends on:** | Logging Fundamentals, Observability Fundamentals         |                 |
| **Used by:**    | Jaeger/Zipkin (log-trace correlation), Alerting          |                 |
| **Related:**    | Logging Fundamentals, Jaeger/Zipkin, Prometheus, Grafana |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
50 microservices deployed across 200 Kubernetes pods.
An incident occurs at 3 AM. The on-call engineer needs
to find what caused a checkout failure 15 minutes ago.
Without centralised logging: SSH into each pod and
run `kubectl logs`. But the pod that had the error
was evicted (OOMKilled) 5 minutes ago. Its logs are
gone. The engineer checks 50 services manually. Two
hours later, no root cause found. The post-mortem
has "insufficient data."

**WITH ELK/EFK:**
Every log from every pod ships to Elasticsearch
continuously. Even after the pod is evicted, its logs
are preserved. The on-call engineer opens Kibana,
searches `service:checkout AND level:ERROR AND
@timestamp:[now-20m TO now-10m]` and finds: "payment
gateway connection refused at 02:47:23." Root cause
in 30 seconds.

---

### 📘 Textbook Definition

**ELK Stack:**

- **Elasticsearch:** distributed, full-text search
  database. Stores logs as JSON documents. Provides
  a REST API for search and aggregation.
- **Logstash:** a data processing pipeline. Collects
  logs from sources, transforms them (parse, enrich,
  filter), and ships to Elasticsearch. CPU-intensive.
- **Kibana:** the visualisation and query UI for
  Elasticsearch. Log search, dashboards, alerting.

**EFK Stack (Kubernetes-preferred):**

- **Elasticsearch:** same role
- **Fluentd (or Fluent Bit):** replaces Logstash.
  Lower memory footprint than Logstash. Runs as a
  DaemonSet (one per Kubernetes node) to collect
  all pod logs on that node.
- **Kibana:** same role

**OpenSearch:**
AWS fork of Elasticsearch/Kibana (after Elastic
changed licence). API-compatible but separately
maintained. Used in AWS managed deployments.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
ELK centralises all service logs into one searchable
database, so when something breaks you can find the
log lines from any service from the last N days in
seconds.

> Think of a city's 911 dispatch centre. Each
> neighbourhood (service) generates incident reports
> (logs). Without a central system, finding all
> incidents related to "drug-related" last week
> requires calling 50 precincts. With the centralised
> dispatch database (Elasticsearch), one query returns
> all relevant reports. The dispatch operator (Kibana)
> provides the search interface. The courier who
> collects reports from each precinct and delivers
> them to the database is Fluentd (the log shipper).

---

### 🔩 First Principles Explanation

**THE LOG PIPELINE:**

```
[Application Pod]
  Writes to stdout/stderr
  (structured JSON: {"level":"ERROR","msg":"..."})
        ↓
[Fluent Bit DaemonSet - on every node]
  Reads /var/log/containers/*.log on the node
  Parses: adds k8s metadata (pod, namespace, label)
  Buffers in memory + disk (handles backpressure)
  Ships to Elasticsearch via HTTP
        ↓
[Elasticsearch Cluster]
  Ingests: parses JSON, indexes fields
  Stores: index per day (logs-2024-04-15)
  Index: inverted index on all text fields
  ILM: hot (1 day) → warm (6 days) → cold (23 days)
        → delete after 30 days
        ↓
[Kibana]
  Discover: full-text search with KQL/Lucene
  Dashboards: log volume, error rate by service
  Alerts: trigger on log pattern matches
```

**ELASTICSEARCH INDEX DESIGN:**

```json
// Mapping for logs index
{
  "mappings": {
    "properties": {
      "@timestamp": { "type": "date" },
      "level": { "type": "keyword" },
      "service": { "type": "keyword" },
      "message": { "type": "text" },
      "trace_id": { "type": "keyword" },
      "span_id": { "type": "keyword" },
      "http.status_code": { "type": "integer" },
      "error.type": { "type": "keyword" },
      "error.message": { "type": "text" }
    }
  }
}
```

**KEYWORD vs TEXT:**

- `keyword`: exact match, faceting, sorting
  (use for: level, service, status_code, trace_id)
- `text`: full-text search with tokenisation
  (use for: message, error.message)
  Indexing both: use `fields` mapping to get both
  keyword and text behaviour on the same field.

---

### 🧪 Thought Experiment

**THE QUERY POWER DEMONSTRATION:**

It's 2 AM. An alert fires: checkout error rate spike.
You have 200 pods, 50 services, and 3 million log
lines in the last hour. Relevant events:

In traditional log debugging (no Kibana):

1. kubectl logs checkout-api-pod-1 | grep ERROR
2. kubectl logs checkout-api-pod-2 | grep ERROR
3. ... repeat for 15 checkout pods ...
4. Nothing found. The error is downstream.
5. Check payment-gateway logs... 20 more pods...
   Time: 30-45 minutes.

In Kibana (ELK):

```
KQL query: level:ERROR AND @timestamp:[now-30m TO now]
  AND (service:checkout* OR service:payment*)
  AND message:"connection refused"

Results: 47 error log lines in 3 seconds
Top result: "payment-gateway: connection refused
to stripe-api.external.com:443"
Spike started: 02:44:31
```

Time: 45 seconds.

**The insight:** the value of centralised logging
is not just storage - it is the elimination of the
N*M search problem. Without central logs, finding
a specific error across N services with M pods each
requires N*M kubectl commands. With central logs,
it requires one query.

---

### 🧠 Mental Model / Analogy

> A library without a catalogue is still a library.
> But finding a specific book requires walking every
> aisle. A library with a full catalogue (by author,
> subject, keyword, year) lets you find any book in
> seconds. Elasticsearch is the catalogue. Logs are
> the books. Kibana is the librarian's terminal.
> Fluentd is the book acquisition process that
> ensures every new book (log line) is catalogued
> as soon as it arrives.
>
> Without the catalogue: you grep through individual
> log files like walking random library aisles.
> With the catalogue: you search across every book
> ever published to the library in one query.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone):**
ELK collects logs from all your services into one
place. You can search all logs at once using Kibana.

**Level 2 - How to use it (junior):**
Open Kibana Discover. Select the logs-\* index pattern.
Set time range to the incident window. Use KQL to
filter: `level:ERROR AND service:"checkout-api"`.
Click on a log line to see all fields. Look at the
`trace_id` field - use it to jump to Jaeger.

**Level 3 - How it works (mid-level):**
Fluentd DaemonSet reads pod logs from the node's
`/var/log/containers/` directory. It parses JSON
logs (or uses regex for unstructured logs), adds
Kubernetes metadata labels, and ships to Elasticsearch
via the Elasticsearch output plugin. Elasticsearch
creates an inverted index (like a book index) on all
`text` fields. `keyword` fields support exact match
and aggregation. ILM policies manage storage by
moving older indices to slower (warm/cold) nodes
and deleting after the retention window.

**Level 4 - Operations at scale (senior):**
Elasticsearch cluster sizing: heap ≤ 32GB per node
(JVM compressed oops boundary). Shard count: 1 shard
per 50GB of data per index. Too many shards = overhead
(each shard uses memory and file handles). Index
lifecycle: hot-warm-cold-delete architecture separates
recent (fast NVMe) from archive (cheaper storage).
Mapping explosion: `dynamic: "strict"` prevents
uncontrolled field creation. Slow search queries:
use `profile` API to find expensive query stages.

**Level 5 - Platform engineering (staff):**
ELK vs OpenSearch vs Loki. For pure log management
at extreme scale, Loki (Grafana) uses a label-based
index (like Prometheus) rather than full-text search,
reducing storage by 5-10x but limiting search
flexibility (Loki searches log content with regex,
not full inverted-index search). The choice: ELK
for rich search requirements (security, compliance,
full-text) vs Loki for Kubernetes-native low-cost
log storage with basic search. The Elastic SIEM
use case: ELK is not just observability - it is
also the SIEM (security information and event
management) platform for threat detection.

---

### ⚙️ How It Works (Mechanism)

**FLUENTD LOG COLLECTION FLOW:**

```
[Kubernetes Node]
  /var/log/containers/checkout-api-xxx.log
  (symlink to /var/log/pods/...)
        ↓
[Fluent Bit DaemonSet - same node]
  Input plugin: tail
    path /var/log/containers/*.log
    tag kube.*
  Filter plugin: kubernetes
    kube_url https://kubernetes.default.svc
    merge_log true  # parse JSON from log field
    k8s_logging.parser true
  Output plugin: elasticsearch
    host elasticsearch.logging.svc.cluster.local
    port 9200
    index_name logs-${namespace}
    buffer:
      type file
      path /var/log/fluentd-buffers/
      chunk_limit_size 8M
      total_limit_size 512M
```

**ELASTICSEARCH WRITE PATH:**

```
[Fluent Bit POST /logs-2024-04-15/_bulk]
  Elasticsearch receives bulk request
  Routes to primary shard (based on _id hash or round-robin)
  Primary writes to translog (WAL) + in-memory buffer
  Replicates to N replica shards
  Refresh (default 1s): flush buffer to searchable segment
  Merge: background compaction of segments
```

---

### 🔄 The Complete Picture - End-to-End Flow

**INCIDENT INVESTIGATION WITH ELK:**

```
[02:47 AM: Alert fires - checkout error rate spike]
        ↓
[On-call opens Kibana Discover]
  Index pattern: logs-*
  Time range: last 30 minutes
  KQL: level:ERROR
  Result: 847 error log lines in last 15 minutes
        ↓
[Refine query]
  KQL: level:ERROR AND service:checkout-api
  Result: 312 errors in checkout-api
  First error: 02:44:31
        ↓
[Click on error log line]
  message: "payment-gateway connection refused"
  trace_id: "abc123def456"
  service: checkout-api
  error.type: "java.net.ConnectException"
        ↓
[Jump to Jaeger: search trace_id=abc123def456]
  Trace shows: checkout-api called payment-gateway
  payment-gateway span: FAILED at stripe-api call
        ↓
[Search payment-gateway logs]
  KQL: service:payment-gateway AND level:ERROR
        AND trace_id:abc123def456
  Log: "Stripe API: connection timeout after 5000ms"
        ↓
[Root cause: Stripe API connectivity issue]
  Mitigation: enable fallback payment provider
  Timeline: 4 minutes to diagnosis
```

---

### 💻 Code Example

**Example 1 - BAD: Unstructured log (un-parseable):**

```java
// BAD: unstructured log - grep-only, cannot filter
// by specific fields in Kibana, cannot aggregate
log.error("ERROR: payment failed for user " + userId
    + " order " + orderId + " amount " + amount
    + " at " + LocalDateTime.now()
    + " error: " + ex.getMessage());

// In Kibana: only full-text search works
// Cannot filter: amount > 100 or status_code = 503
// Cannot aggregate: error count by error.type
```

**Example 2 - GOOD: Structured JSON log:**

```java
// GOOD: structured JSON log
// Every field is indexed, filterable, aggregatable
import org.slf4j.MDC;

MDC.put("trace_id", span.getSpanContext().getTraceId());
MDC.put("span_id", span.getSpanContext().getSpanId());

log.atError()
    .addKeyValue("service", "checkout-api")
    .addKeyValue("action", "process_payment")
    .addKeyValue("order_id", orderId)
    .addKeyValue("payment.method", "visa")
    .addKeyValue("payment.amount", amount)
    .addKeyValue("error.type",
        ex.getClass().getSimpleName())
    .addKeyValue("error.message", ex.getMessage())
    .addKeyValue("http.status_code", 503)
    .log("Payment processing failed");
// In Kibana:
// payment.amount > 100 AND error.type:ConnectException
// Aggregation: count by error.type → top errors
// trace_id link to Jaeger trace
```

**Example 3 - Kibana KQL cheat sheet:**

```
# Search by field value (keyword field: exact match)
level:ERROR
service:"checkout-api"
http.status_code:503

# Range queries
@timestamp:[now-30m TO now]
payment.amount:[100 TO *]      # amount >= 100
http.status_code:[500 TO 599]  # 5xx errors

# Boolean operators
level:ERROR AND service:checkout*
level:WARN OR level:ERROR
NOT level:DEBUG

# Full-text search on message field
message:"connection refused"
message:"timeout" AND service:payment*

# Log-trace correlation
trace_id:"abc123def456"

# Aggregation: top 10 errors by type
# Kibana Visualize: terms aggregation on error.type

# Wildcard
service:checkout*     # checkout-api, checkout-worker
message:*timeout*     # contains timeout anywhere
```

**Example 4 - Fluent Bit Kubernetes DaemonSet:**

```yaml
# fluent-bit-config.yaml
[SERVICE]
    Flush         1
    Log_Level     info
    Parsers_File  parsers.conf

[INPUT]
    Name              tail
    Tag               kube.*
    Path              /var/log/containers/*.log
    Parser            docker
    DB                /var/log/flb_kube.db
    Mem_Buf_Limit     50MB
    Skip_Long_Lines   On
    Refresh_Interval  10

[FILTER]
    Name                  kubernetes
    Match                 kube.*
    Kube_URL              https://kubernetes.default.svc:443
    Kube_CA_File          /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
    Kube_Token_File       /var/run/secrets/kubernetes.io/serviceaccount/token
    Merge_Log             On
    Merge_Log_Key         log_processed
    K8S-Logging.Parser    On
    K8S-Logging.Exclude   On

# Drop health check logs (reduce volume)
[FILTER]
    Name    grep
    Match   kube.*
    Exclude log /healthz

[OUTPUT]
    Name            es
    Match           kube.*
    Host            elasticsearch.logging.svc.cluster.local
    Port            9200
    Index           logs
    Generate_ID     On
    Buffer_Size     False
    Retry_Limit     False
```

---

### ⚖️ Comparison Table

| Feature           | ELK (Elasticsearch)                  | Loki (Grafana)                    | CloudWatch Logs      | Datadog Logs      |
| ----------------- | ------------------------------------ | --------------------------------- | -------------------- | ----------------- |
| Search capability | Full inverted index (rich)           | Label-based + regex (limited)     | Full-text (basic)    | Full-text (rich)  |
| Storage cost      | High (all fields indexed)            | Low (only labels indexed)         | Medium               | High (SaaS)       |
| Query language    | KQL / Lucene                         | LogQL                             | CloudWatch Insights  | DQL               |
| Kubernetes native | Via Fluentd/Fluent Bit               | Native (Promtail agent)           | Via Fluent Bit to CW | Via Datadog Agent |
| Trace correlation | Via trace_id field                   | Built into Grafana                | Limited              | Strong (APM)      |
| Licence           | Elastic (SSPL) / OpenSearch (Apache) | Apache 2.0                        | AWS proprietary      | SaaS              |
| Best for          | Rich search, compliance, SIEM        | Kubernetes cost-efficient logging | AWS-only workloads   | All-in-one SaaS   |

---

### ⚠️ Common Misconceptions

| Misconception                        | Reality                                                                                                                                                                                                                                               |
| ------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "ELK can store logs forever cheaply" | Elasticsearch is expensive in storage costs. Full-text indexing stores each field's inverted index, which can be 1.5-2x the size of the raw log data. Use ILM policies to delete after 30 days and archive to S3 cold storage.                        |
| "Logstash is required in EFK"        | Logstash is CPU-intensive and adds latency. In Kubernetes, Fluentd or Fluent Bit (lighter) replaces Logstash entirely. Many ELK deployments now use Beats (Filebeat, Metricbeat) instead of Logstash.                                                 |
| "JSON logs are automatically parsed" | Elasticsearch can auto-detect JSON if you configure dynamic mapping. But without explicit mapping, fields may be mapped as wrong types (a status code as text instead of integer), breaking numeric range queries. Define explicit mappings.          |
| "ELK and OpenSearch are the same"    | Elastic changed its licence to SSPL (non-OSI open source) in 2021. AWS forked the project as OpenSearch under Apache 2.0. They have diverged. OpenSearch is API-compatible with older Elasticsearch but has different roadmaps and features.          |
| "More shards = better performance"   | Each Elasticsearch shard has overhead (heap memory, file handles). Under-sharding (one shard that's too large) reduces query parallelism. Over-sharding (too many small shards) wastes resources. Rule: 1 shard per 50GB, maximum 20 shards per node. |

---

### 🚨 Failure Modes & Diagnosis

**Elasticsearch cluster red (data loss risk)**

**Symptom:**
Kibana shows "cluster health: red." Some log data
is not searchable. Log ingestion is slow or backing
up. Fluent Bit logs show 429/503 errors from Elasticsearch.

**Root Cause:**
Cluster is red when one or more primary shards are
unassigned. This means some indices are missing
primary shards - data cannot be read or written for
those indices.

**Diagnostic:**

```bash
# Check cluster health
curl http://elasticsearch:9200/_cluster/health?pretty

# Find unassigned shards
curl http://elasticsearch:9200/_cat/shards?h=index,shard,prirep,state,unassigned.reason&v \
  | grep UNASSIGNED

# Check allocation explanation
curl http://elasticsearch:9200/_cluster/allocation/explain?pretty

# Common unassigned reasons:
# NODE_LEFT: the node holding this shard left the cluster
# ALLOCATION_FAILED: disk full, cannot allocate shard
```

**Fix:**
For NODE_LEFT: wait for node to rejoin or redistribute
shards. If node is permanently gone and no replicas
exist, the shard is lost.

```bash
# Reroute unassigned shard (if replicas exist)
curl -XPOST http://elasticsearch:9200/_cluster/reroute \
  -H "Content-Type: application/json" \
  -d '{"commands":[{"allocate_replica":{"index":"logs-2024-04-15","shard":0,"node":"node-2"}}]}'
```

**Prevention:**

- Set replication factor ≥ 1 for all production indices
- Monitor disk usage: alert at 70%, hard limit at 85%
- Set up Elasticsearch cluster health alert in Grafana

---

**Fluent Bit backpressure: log buffer filling up**

**Symptom:**
Fluent Bit pod logs show "chunk limit reached" errors.
Fluent Bit memory usage is climbing. Recent logs
(last 5-10 minutes) are missing from Kibana.

**Root Cause:**
Elasticsearch is ingesting slower than Fluent Bit
is producing (due to ES cluster degradation, network
issues, or indexing bottleneck). Fluent Bit's memory
buffer fills up. If disk buffering is not configured,
logs are dropped.

**Diagnostic:**

```bash
# Check Fluent Bit metrics
curl http://fluent-bit-pod:2020/api/v1/metrics/prometheus \
  | grep "fluentbit_output_retries_failed"

# Check Elasticsearch indexing rate
curl http://elasticsearch:9200/_cat/indices/logs*?v&h=index,docs.count,pri.store.size
```

**Fix:**
Configure Fluent Bit disk buffer to handle backpressure:

```ini
[OUTPUT]
    Name            es
    Match           kube.*
    storage.type    filesystem  # use disk buffer
    [BUFFER]
        type file
        path /var/log/fluentbit-buffers
        chunk_limit_size 1M
        total_limit_size 1G     # 1GB disk buffer
```

---

**Mapping explosion from dynamic fields**

**Symptom:**
Elasticsearch returns HTTP 400 "Limit of total fields
[1000] in index has been exceeded." New logs cannot
be indexed. Kibana shows "mapping conflict" warnings.

**Root Cause:**
An application started logging deeply nested JSON
objects with unpredictable field names (e.g., request
headers, database row payloads). Each unique field
name creates a new mapping entry. Default limit is
1,000 fields per index.

**Fix:**

```json
// Use dynamic: "strict" with explicit mapping
// for known fields; use an opaque object for unknown
{
  "mappings": {
    "dynamic": "strict",
    "properties": {
      "@timestamp": { "type": "date" },
      "level": { "type": "keyword" },
      "message": { "type": "text" },
      "service": { "type": "keyword" },
      "trace_id": { "type": "keyword" },
      // Store arbitrary extra fields as opaque object
      // (not indexed, not searchable)
      "extras": {
        "type": "object",
        "dynamic": false,
        "enabled": false
      }
    }
  }
}
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Logging Fundamentals` - structured logs, log levels,
  the principles that ELK implements at scale
- `Observability Fundamentals` - the three-pillar
  context (logs are one of the three pillars)

**Builds On This (learn these next):**

- `Jaeger / Zipkin Distributed Tracing` - log-trace
  correlation via trace_id enables jumping between
  a log in Kibana and its trace in Jaeger
- `Alerting Fundamentals` - Elasticsearch Watcher and
  Kibana Alerts fire on log patterns (e.g., error rate
  per service exceeds threshold)

**Alternatives / Comparisons:**

- `Loki (Grafana Loki)` - label-based log storage.
  Much lower cost, simpler architecture. Limited full-
  text search. Best for Kubernetes-native cost-sensitive
  environments.
- `Splunk` - enterprise log management. More powerful
  analytics, higher cost, popular in security/compliance.
- `CloudWatch Logs` - AWS managed. No operational
  overhead, but higher cost and limited to AWS.

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ ELK          │ E=Elasticsearch (store+search)            │
│ COMPONENTS   │ L=Logstash (transform, on-prem)           │
│              │ K=Kibana (visualise+search UI)            │
│ EFK          │ F=Fluentd/Fluent Bit (Kubernetes shipper) │
├──────────────┼───────────────────────────────────────────┤
│ KEY KIBANA   │ level:ERROR AND service:checkout*         │
│ KQL PATTERNS │ http.status_code:[500 TO 599]             │
│              │ @timestamp:[now-30m TO now]               │
│              │ trace_id:"abc123" (log-trace correlation) │
├──────────────┼───────────────────────────────────────────┤
│ FIELD TYPES  │ keyword: exact match, aggregation         │
│              │ text: full-text search (tokenised)        │
│              │ date: time range queries                  │
├──────────────┼───────────────────────────────────────────┤
│ ILM PHASES   │ hot (active write) → warm (search only)   │
│              │ → cold (archive) → delete                 │
├──────────────┼───────────────────────────────────────────┤
│ CLUSTER HEALTH│ Green: all shards OK                     │
│              │ Yellow: replicas missing (OK for now)     │
│              │ Red: primary shard missing (data at risk) │
├──────────────┼───────────────────────────────────────────┤
│ COMMON BUGS  │ Red cluster = unassigned primary shard    │
│              │ Mapping explosion = dynamic fields + JSON │
│              │ Log gaps = Fluent Bit backpressure         │
├──────────────┼───────────────────────────────────────────┤
│ LOG BEST     │ Structured JSON, trace_id + span_id field │
│ PRACTICE     │ Bounded cardinality (no user IDs as keys) │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Jaeger (trace correlation) → Loki (cheaper│
│              │ alternative) → ES security/SIEM           │
└──────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Centralise observability data at ingestion, not at
query time. The ELK stack's value is that logs are
indexed (centralised, structured, searchable) at
the moment they are written, not when an incident
occurs. The same principle applies to metrics
(Prometheus scrapes continuously, not on demand)
and traces (spans shipped continuously, not pulled
at incident time). Systems that centralise data
proactively can answer questions about the past;
systems that centralise reactively (grep on demand)
can only answer questions about the present.

---

### 💡 The Surprising Truth

The most counterintuitive ELK insight: the cost of
centralised logging is dominated not by log storage
but by Elasticsearch's index overhead. Elasticsearch
stores each log line multiple times: once as raw
source (for display), once in the inverted index
(for full-text search), and once per field in the
doc values (for aggregation and sorting). For a
structured log with 20 fields, Elasticsearch may
store 3-5x the raw log size on disk. This is why
Grafana Loki (which indexes only labels, not log
content) is 5-10x cheaper in storage than ELK for
the same log volume. The right choice depends on
whether you need full-text search (ELK) or just
log storage with label-based search (Loki).

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **[SEARCH]** Write Kibana KQL queries for: all
   ERROR logs in the last hour, checkout service
   errors with HTTP 5xx status, all log lines
   containing a specific trace_id, and error count
   by service for a specific time window.
2. **[CONFIGURE]** Deploy Fluent Bit as a DaemonSet
   in Kubernetes: configure the input (tail pod logs),
   filter (add k8s metadata, exclude health checks),
   and output (Elasticsearch with disk buffering).
3. **[DEBUG]** Given an Elasticsearch red cluster, use
   the `_cat/shards` and `_cluster/allocation/explain`
   APIs to identify unassigned shards and diagnose
   the cause (node left, disk full, or shard limit).
4. **[DESIGN]** Design the index mapping for a log
   index: specify which fields are `keyword`, which
   are `text`, why the message field should have both,
   and how to prevent mapping explosion from dynamic
   fields.
5. **[COMPARE]** Explain to a team choosing a log
   management solution when you would recommend ELK
   vs Loki vs CloudWatch Logs, with specific criteria
   for each choice.

---

### 🧠 Think About This Before We Continue

**Q1.** Your team stores 30 days of logs in Elasticsearch.
The cluster uses 3TB of storage. The operations team
wants to reduce costs by 50%. What are your options,
and what are the tradeoffs of each? Consider: index
lifecycle policies, storage tiers (hot/warm/cold),
compression, and alternative backends like S3.
_Hint: Options: (1) Reduce retention from 30 days
to 14 days (50% storage saving, risk: post-incidents
may not have 30 days of history). (2) ILM cold tier:
move 14-30 day indices to cheaper nodes (cold storage,
slower search). (3) Index compression: force-merge
with compression reduces size 40-60% (but makes
shards read-only). (4) Move archived logs to S3 via
searchable snapshots (ES 7.13+ feature: search directly
from S3 frozen tier at very low cost). (5) Migrate
new logs to Loki (5-10x cheaper), keep ES for legacy._

**Q2.** An application logs 100,000 lines/second during
peak traffic. Each log line is approximately 500 bytes
as structured JSON. Elasticsearch is currently
indexing all fields. Calculate: (a) raw log volume
per day, (b) estimated Elasticsearch storage including
index overhead at 2x, (c) Fluent Bit throughput
requirement in MB/s.
_Hint: (a) 100,000 lines/s x 500B x 86,400s = 4.32TB/day
raw. (b) 4.32 x 2 = 8.64TB/day in ES. Monthly: 259TB
at 30-day retention. (c) Fluent Bit: 100,000 x 500B
= 50MB/s throughput required. This is beyond a single
Fluent Bit instance's typical capacity of 20-30MB/s.
Needs multiple Fluent Bit instances (DaemonSet handles
this automatically - one per node)._

**Q3 (TYPE G):** Your company is moving from a monolith
(one application, one log file) to 100 microservices
over 18 months. Design the log management evolution:
what you deploy in months 1-3 (single service), 4-6
(10 services), 7-12 (50 services), and 13-18 (100
services). For each phase: what is the log volume,
what are the operational requirements, and what
changes to the ELK configuration or architecture
are needed? Also address: how do you onboard each
new service to centralised logging?
_Hint: Months 1-3: single service, ELK with Filebeat
(simple), 1 ES node. Months 4-6: 10 services, Fluent
Bit DaemonSet on Kubernetes, 3-node ES cluster.
Months 7-12: 50 services, dedicated Fluent Bit config
per service (different index per service for access
control), add ILM policies. Months 13-18: 100 services,
cross-cluster search or Elastic federation, consider
Loki for noisy low-value services. Onboarding: service
must emit structured JSON to stdout; Fluent Bit handles
the rest automatically via k8s annotations._

---

### 🎯 Interview Deep-Dive

**Q1: "Explain the ELK stack. What does each component do?"**
_Why they ask:_ Tests basic understanding of the most
common log management stack.
_Strong answer includes:_

- E = Elasticsearch: distributed search database,
  stores logs as JSON documents, full-text indexed
- L/F = Logstash/Fluentd: log shipping and processing
  pipeline. In Kubernetes, Fluentd or Fluent Bit runs
  as a DaemonSet to collect all pod logs automatically
- K = Kibana: the UI for searching and visualising
  logs. Uses KQL (Kibana Query Language) or Lucene.
- Data flow: application → stdout → Fluent Bit →
  Elasticsearch → Kibana query

**Q2: "How do you search for all errors from the
checkout service in the last hour in Kibana?"**
_Why they ask:_ Tests practical Kibana usage, a key
operational competency.
_Strong answer includes:_

- In Kibana Discover, set time range to "last 1 hour"
- KQL query: `level:ERROR AND service:"checkout-api"`
- Or with HTTP status: `level:ERROR AND service:"checkout-api" AND http.status_code:[500 TO 599]`
- Refine by message content: add `AND message:"connection refused"` if looking for specific error
- Check the histogram to see when errors started
- Bonus: add `trace_id` to the search to correlate
  a specific request's logs and trace

**Q3: "Your Elasticsearch cluster is yellow. Is this
a problem? What do you do?"**
_Why they ask:_ Tests Elasticsearch operations knowledge.
_Strong answer includes:_

- Yellow = all primary shards assigned and healthy,
  but one or more replica shards are unassigned
- Not immediately a data loss risk (primary is OK)
  but you are running without redundancy
- If a node now fails, you could lose the primary
  shard that was relying on the missing replica
  for protection
- Common cause: cluster has fewer nodes than the
  required replica count, or a node recently left
  the cluster
- Diagnosis: `GET /_cat/shards?h=index,shard,prirep,state&v` - find UNASSIGNED replicas
- Fix: add the node back (if it left), or if you
  intentionally have fewer nodes, reduce replica
  count: `PUT /logs-*/_settings {"index.number_of_replicas": 0}`
- Monitor via Kibana Stack Monitoring or Grafana
  Elasticsearch dashboard
