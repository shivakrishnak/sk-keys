---
version: 2
layout: default
title: "AWS CloudWatch Log Insights"
parent: "Observability & SRE"
grand_parent: "Technical Dictionary"
nav_order: 4
permalink: /observability/aws-cloudwatch-log-insights/
number: "OBS-004"
category: Observability & SRE
difficulty: ★★★
depends_on: Logging, AWS, Distributed Systems
used_by: Observability & SRE, Cloud - AWS
related: AWS CloudWatch Dashboards, OpenSearch  Elasticsearch, Structured Logging
tags:
  - observability
  - aws
  - advanced
  - production
---

# OBS-004 - AWS CloudWatch Log Insights

⚡ **TL;DR -** CloudWatch Log Insights is a purpose-built interactive query engine for CloudWatch Logs that enables ad-hoc aggregation, filtering, and pattern analysis across log groups without an external log platform.

| Field | Value |
|---|---|
| **Depends on** | Logging, AWS, Distributed Systems |
| **Used by** | Observability & SRE, Cloud - AWS |
| **Related** | AWS CloudWatch Dashboards, OpenSearch / Elasticsearch, Structured Logging |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Your Lambda functions emit logs to CloudWatch Logs. An error occurs. You open the Log Streams view, scroll through raw JSON log events one stream at a time, and use browser Ctrl+F to search for an error message. You have 200 log streams across 50 Lambda invocations. Manual log review is not a debugging strategy.

**THE BREAKING POINT:**
CloudWatch Logs stores the data, but raw storage without query capability is an archive, not an observability tool. `grep` on log streams does not aggregate, does not compute statistics, and does not work across multiple log groups simultaneously.

**THE INVENTION MOMENT:**
Log Insights provides a SQL-like query language with commands (`filter`, `stats`, `sort`, `limit`, `parse`, `fields`) that runs directly against CloudWatch Logs data - no export, no ETL, no external platform - returning aggregated results within seconds.

---

### 📘 Textbook Definition

**AWS CloudWatch Log Insights** is a managed, interactive query service for CloudWatch Logs. It uses a proprietary query language with commands for field extraction, filtering, aggregation (`stats`), sorting, limiting, and pattern parsing. Queries run against one or more log groups, can span custom time ranges, and return up to 10,000 rows. Results can be visualised as time-series charts, saved as named queries, and embedded as widgets in CloudWatch Dashboards. Queries are charged per GB of log data scanned.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Log Insights turns your CloudWatch log streams into a queryable database you interrogate with a simple command language.

> Like a librarian who can instantly search the full text of every book in the library, count how many books mention a topic, and show you the top 10 most-mentioned authors - without you having to pull books off shelves yourself.

**One insight:** The `stats` command is the most powerful feature - it transforms raw log events into aggregated metrics (error counts by customer, p99 latency by endpoint) that CloudWatch Metrics does not automatically capture.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. **Logs are semi-structured text** - Log Insights can parse JSON fields automatically and extract fields from unstructured text using `parse` with regex or glob patterns.
2. **Aggregation happens at query time** - unlike pre-computed metrics, Log Insights aggregates on demand, enabling retroactive analysis of fields you did not think to index.
3. **Scanned data drives cost** - queries scan all log data in the specified time range; narrow time windows and specific log groups reduce cost.
4. **Log groups are the query boundary** - you query across up to 50 log groups per query; cross-account queries require cross-account log sharing.

**DERIVED DESIGN:**
The query engine indexes log events on ingestion for time-range queries. Each log event is parsed as JSON if the message field is valid JSON; otherwise, the `@message` field contains the raw text. Built-in fields (`@timestamp`, `@message`, `@logStream`, `@log`) are always available. The `parse` command extracts fields using patterns. The `stats` command groups and aggregates. The `filter` command applies boolean predicates.

**THE TRADE-OFFS:**
**Gain:** No external infrastructure, zero setup, works immediately on existing CloudWatch Logs, retroactive analysis.
**Cost:** Per-GB scan cost (can be expensive on high-volume log groups), 10,000 row result limit, 15-minute query timeout, limited join capability.

---

### 🧪 Thought Experiment

**SETUP:** A Lambda function processes 1 million events per day. On a given day, 5,000 events failed. You need to know which customer IDs had the most failures and what the average processing time was for failed events.

**WHAT HAPPENS WITHOUT Log Insights:**
You export logs to S3 (15-minute delay), download a 2 GB gzipped file, run `jq` locally, write a Python script to aggregate by customer ID. Total time: 45 minutes. By the time you have results, the SLA breach has already escalated.

**WHAT HAPPENS WITH Log Insights:**
You write a 5-line query. Results return in under 30 seconds. You see that customer `acct-4892` accounts for 60% of failures with an average processing time of 12 seconds (vs 800ms normal). You diagnose a data shape problem in that customer's input records.

**THE INSIGHT:** Retroactive aggregation - the ability to ask a question you did not pre-define - is what separates an observability tool from a monitoring tool.

---

### 🧠 Mental Model / Analogy

> CloudWatch Log Insights is a database `SELECT` statement applied to your logs. Each log event is a row, each JSON field is a column. `filter` is `WHERE`, `stats` is `GROUP BY` + aggregate functions, `sort` is `ORDER BY`, `limit` is `LIMIT`, and `parse` is a computed column from raw text.

**Element mapping:**
- Log group = database table
- Log event = table row
- JSON field = column
- `filter` = WHERE clause
- `stats count(*) by fieldX` = GROUP BY fieldX
- `sort desc` = ORDER BY DESC
- `parse` = regexp_extract computed column
- `@timestamp` = a built-in indexed datetime column

Where this analogy breaks down: Log Insights does not support JOINs across log groups - each query is effectively a single-table scan.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Log Insights lets you search and analyse your application logs using simple commands - like asking "how many errors happened per customer in the last hour?" - and getting the answer in seconds.

**Level 2 - How to use it (junior developer):**
Go to CloudWatch → Log Insights. Select your log group(s). Type a query like `filter @message like /ERROR/ | stats count(*) as errors by bin(5m)`. Set the time range and click Run. Results appear as a table and optionally as a bar chart. Save frequently used queries with "Save query."

**Level 3 - How it works (mid-level engineer):**
Log Insights uses a columnar index over log events partitioned by time. When you run a query, the engine determines which time partitions to scan based on your time range, extracts fields (auto-parsing JSON or applying `parse` patterns), evaluates `filter` predicates, computes `stats` aggregations, applies `sort` and `limit`. The query runs in parallel across log stream shards. Built-in fields (`@timestamp`, `@message`, `@logStream`, `@log`) are pre-indexed; JSON sub-fields are extracted on-the-fly. Results are truncated at 10,000 rows.

**Level 4 - Why it was designed this way (senior/staff):**
The custom command language (rather than SQL) was chosen for readability by operators unfamiliar with SQL, and because the pipeline model (`|` chaining) maps naturally to log processing: filter first (reduce data), then aggregate, then sort, then limit. Per-GB scan pricing aligns cost with value - short-duration queries on small log groups are cheap; long-range queries on high-volume groups are expensive, incentivising structured logging and narrow query windows. The 10,000-row limit prevents accidental full-table exports that would both cost money and overwhelm the UI; for bulk export, CloudWatch Logs Insights has a separate export-to-S3 path.

---

### ⚙️ How It Works (Mechanism)

```
Query submitted
  (log groups + time range + query text)
  ↓
Time partition scan
  (only partitions within time range)
  ↓
Per-event processing (parallel):
  ├── JSON auto-parse → extracted fields
  ├── parse command → regex extraction
  └── filter → discard non-matching events
  ↓
stats aggregation
  (count, sum, avg, min, max, pct, stddev)
  ↓
sort + limit applied
  ↓
Results returned (max 10,000 rows)
  ├── Table view
  └── Visualisation (if stats + bin())
```

**Built-in fields always available:**
```
@timestamp   - event ingestion time (ms)
@message     - raw log event text
@logStream   - source log stream name
@log         - log group ARN
@requestId   - Lambda request ID (if Lambda)
@duration    - Lambda billed duration (if Lambda)
@billedDuration - Lambda cost unit
@memorySize  - Lambda memory config
@maxMemoryUsed  - Lambda peak memory
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
Lambda invocation
  ↓ console.log(JSON.stringify({
      level: "INFO",
      customerId: "acct-001",
      durationMs: 120
    }))
CloudWatch Logs ingests event
  ↓ auto-parses JSON fields
Log Insights query:
  fields customerId, durationMs
  | filter level = "ERROR"
  | stats avg(durationMs) as avgMs,
          count(*) as errors
          by customerId
  | sort errors desc
  | limit 20
  ← YOU ARE HERE
Results: table of top customers
  by error count with avg latency
```

**FAILURE PATH:**
```
Query times out (> 15 minutes)
  ↓ log volume too large for time range
  ↓ Error: "Query timed out"
Narrow time range to 1 hour
  + add filter early in pipeline
  + reduce log groups queried
  ↓ Query completes in 8 seconds
```

**WHAT CHANGES AT SCALE:**
At very high log volumes (TB/day), Log Insights queries become expensive and slow. Consider: (1) emitting critical aggregations as custom CloudWatch Metrics at source (cheaper to query), (2) shipping logs to OpenSearch for lower-cost bulk analytics, (3) using S3 export + Athena for historical log analysis at cents per TB.

---

### 💻 Code Example

**BAD - Searching logs manually via filter streams:**
```bash
# Manually downloading log streams.
# Does not aggregate. Does not scale.
# Cannot compute error rates or p99.
aws logs filter-log-events \
  --log-group-name /aws/lambda/checkout \
  --filter-pattern "ERROR" \
  --start-time 1700000000000 \
  --limit 50
```

**GOOD - Log Insights queries for common patterns:**
```bash
# 1. Error rate per 5-minute bucket
fields @timestamp, @message
| filter level = "ERROR"
| stats count(*) as errorCount
  by bin(5m)
| sort @timestamp asc

# 2. P99 latency by endpoint
fields endpoint, durationMs
| filter ispresent(endpoint)
| stats
    pct(durationMs, 99) as p99,
    avg(durationMs) as avgMs,
    count(*) as requests
  by endpoint
| sort p99 desc
| limit 20

# 3. Top customers by error count
fields customerId, level
| filter level = "ERROR"
| stats count(*) as errors
  by customerId
| sort errors desc
| limit 10

# 4. Parse unstructured log line
fields @message
| parse @message
  "* ERROR * duration=*ms"
  as logTime, errMsg, durationStr
| stats count(*) as errors
  by errMsg
| sort errors desc
```

**Programmatic query via Python (AWS SDK):**
```python
import boto3, time

logs = boto3.client("logs")

# Start query
resp = logs.start_query(
    logGroupName="/aws/lambda/checkout",
    startTime=int(start.timestamp()),
    endTime=int(end.timestamp()),
    queryString="""
        fields customerId, level
        | filter level = "ERROR"
        | stats count(*) as errors
          by customerId
        | sort errors desc
        | limit 10
    """,
)
query_id = resp["queryId"]

# Poll for results
while True:
    result = logs.get_query_results(
        queryId=query_id
    )
    if result["status"] == "Complete":
        return result["results"]
    time.sleep(1)
```

---

### ⚖️ Comparison Table

| Feature | Log Insights | OpenSearch | Athena (S3 logs) | Splunk |
|---|---|---|---|---|
| **Setup required** | None | Cluster provisioning | S3 export pipeline | Heavy |
| **Query language** | Insights QL | Lucene / SQL | SQL (Presto) | SPL |
| **Cost model** | Per GB scanned | Instance + storage | Per TB scanned | Per GB/day indexed |
| **Result limit** | 10,000 rows | Configurable | Configurable | Configurable |
| **Real-time lag** | ~5 seconds | ~1 second | 15+ min (export) | ~1 minute |
| **Joins** | No | Limited | Full SQL JOINs | Yes |
| **Best for** | Ad-hoc AWS log queries | Full-text search | Historical bulk analysis | Enterprise SIEM |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Log Insights queries are free" | Charges apply per GB of log data scanned; large time ranges on high-volume groups generate significant costs |
| "10,000 row limit applies to raw events" | The limit applies to the final result set after `stats` aggregation - a `stats count(*)` query returns 1 row regardless of how many events were scanned |
| "`filter` after `stats` filters aggregated rows" | Correct - `filter` before `stats` filters events; `filter` after `stats` filters aggregated results (like SQL HAVING); order matters |
| "JSON fields are always auto-detected" | Only if `@message` is valid JSON; nested JSON inside a string field requires `parse` or `json_parse()` |
| "Log Insights replaces CloudWatch Metrics" | Log-derived aggregations are retroactive and ad-hoc; for real-time alerting, emit custom CloudWatch Metrics from your application |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Query returns 0 results despite known log data**

**Symptom:** Query runs successfully but returns no rows.
**Root Cause:** Field name case mismatch (JSON is case-sensitive), wrong log group selected, or time range misalignment.
**Diagnostic:**
```bash
# Run a basic query to see raw events first
fields @timestamp, @message
| limit 5
# Then check what fields actually exist
fields @timestamp, @message
| limit 1
# Inspect the raw JSON to confirm field names
```
**Fix:** Use `fields @message` first to see the raw event format; confirm exact field names including case.
**Prevention:** Use structured logging with a consistent schema; document the log schema in the service README.

---

**Mode 2: High scan cost from broad queries**

**Symptom:** Log Insights costs spike unexpectedly; queries scanning terabytes of data.
**Root Cause:** Queries spanning days or weeks on high-volume log groups (e.g., VPC Flow Logs, ALB access logs).
**Diagnostic:**
```bash
# Check CloudWatch Logs Insights costs
# in AWS Cost Explorer:
# Service: CloudWatch
# Usage Type: DataScanned-Bytes
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-02-01 \
  --granularity MONTHLY \
  --filter '{"Dimensions":{"Key":"SERVICE",
    "Values":["AmazonCloudWatch"]}}' \
  --metrics "UnblendedCost"
```
**Fix:** Add selective `filter` commands at the top of queries (before `stats`) to reduce scanned data. Use narrow time ranges. For bulk historical analysis, export logs to S3 and use Athena instead.
**Prevention:** Set Log Group retention policies; archive old logs to S3; emit high-frequency signals as CloudWatch Metrics rather than logs.

---

**Mode 3: Query timeout on large log groups**

**Symptom:** Query status returns `Timeout` after 15 minutes.
**Root Cause:** Too much data to scan within the 15-minute execution limit.
**Diagnostic:**
```bash
aws logs get-query-results \
  --query-id <queryId>
# Check "status": "Timeout"
# Check "statistics": { "recordsScanned" }
```
**Fix:**
```bash
# BAD: Wide time range, no pre-filter
fields @message
| stats count(*) by bin(1h)
# (scanning 30 days of 10GB/day logs)

# GOOD: Narrow range + early filter
fields @message
| filter @timestamp > 1700000000000
| filter level = "ERROR"
| stats count(*) by bin(1h)
```
**Prevention:** Break wide-range queries into hourly chunks using the SDK's `start_query` / `get_query_results` pattern; aggregate results programmatically.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- Logging - the discipline of emitting and storing structured log events
- Structured Logging - JSON-formatted logs that Log Insights auto-parses into queryable fields
- AWS CloudWatch Logs - the log storage layer that Log Insights queries

**Builds On This (learn these next):**
- AWS CloudWatch Dashboards - embed Log Insights query results as dashboard widgets
- AWS CloudWatch Alarms - combine with metric filters on logs to create log-based alarms
- OpenSearch / Elasticsearch - full-text search and analytics platform for higher-volume log workloads

**Alternatives / Comparisons:**
- Athena - SQL queries on S3-exported logs; cheaper at scale, slower to query
- OpenSearch - richer full-text search, Kibana dashboards, but requires cluster management
- Splunk - enterprise-grade log analytics with SIEM capabilities; significantly higher cost

---

### 📌 Quick Reference Card

```
╔════════════════════════════════════════════╗
║ WHAT IT IS   Query engine for CloudWatch   ║
║              Logs - no setup required      ║
║ PROBLEM      Raw log streams not           ║
║              searchable or aggregatable    ║
║ KEY INSIGHT  stats + parse = retroactive   ║
║              aggregation of any log field  ║
║ USE WHEN     Ad-hoc log analysis in AWS,   ║
║              incident diagnosis, cost      ║
║              reporting from log data       ║
║ AVOID WHEN   TB-scale historical analysis  ║
║              (use Athena), full-text search║
║              (use OpenSearch)              ║
║ TRADE-OFF    Zero setup vs per-GB cost     ║
║              + 10K row limit               ║
║ ONE-LINER    SELECT/GROUP BY for your      ║
║              CloudWatch log groups         ║
║ NEXT EXPLORE Structured Logging, Athena    ║
╚════════════════════════════════════════════╝
```

---

### 🧠 Think About This Before We Continue

1. **(E - First Principles)** Log Insights charges per GB scanned. A `stats count(*) by customerId` query that scans 100 GB returns 1 aggregated row per unique customer. An alternative design would emit a custom CloudWatch Metric `ErrorsByCustomer` from the Lambda function at runtime. Compare the operational characteristics (cost, latency, retroactive capability, cardinality limits) of these two approaches for a system processing 1 million events per day.

2. **(A - System Interaction)** A distributed transaction spans Lambda → SQS → Lambda → DynamoDB. Each service logs its trace ID as a JSON field. Design a Log Insights query strategy to reconstruct the full event timeline for a single transaction ID across three separate log groups, given that Log Insights does not support JOINs.

3. **(B - Scale)** Your team has 100 microservices each writing to their own log group. During a P1 incident, you need to identify which services are emitting ERROR logs. Design a Log Insights query and a CloudWatch log group naming convention that makes cross-service incident triage possible with a single query.
