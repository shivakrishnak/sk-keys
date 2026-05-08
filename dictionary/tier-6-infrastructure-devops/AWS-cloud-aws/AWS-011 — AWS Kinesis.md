---
layout: default
title: "AWS Kinesis"
parent: "Cloud — AWS"
nav_order: 11
permalink: /cloud-aws/aws-kinesis/
id: AWS-011
category: Cloud — AWS
difficulty: ★★★
depends_on: Streaming Data, AWS, Kafka
used_by: Big Data & Streaming, Cloud — AWS
related: Apache Kafka, AWS SQS, AWS Glue
tags:
  - aws
  - cloud
  - streaming
  - advanced
  - dataengineering
---

# AWS-011 — AWS Kinesis

⚡ **TL;DR —** AWS's managed real-time data streaming service that ingests, stores, and delivers ordered data streams via shards, enabling multiple consumers to replay and process events independently.

| Attribute    | Value                                  |
|--------------|----------------------------------------|
| Depends on   | Streaming Data, AWS, Kafka             |
| Used by      | Big Data & Streaming, Cloud — AWS      |
| Related      | Apache Kafka, AWS SQS, AWS Glue        |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** You process millions of clickstream events, IoT sensor readings, or financial transactions per second. Writing to a database directly overwhelms it. Sending to SQS loses ordering, has no replay capability, and allows only one consumer per message. Batch files introduce minutes of latency and lose the real-time characteristic that makes streaming analytics valuable.

**THE BREAKING POINT:** Your fraud detection model needs to see every transaction in order, in real time, within 200 ms. Your analytics team also needs the same events — but they cannot share the SQS queue because SQS deletes messages on consumption. A second copy of every event doubles your write costs. A third consumer means a third copy. You are now running three duplicate pipelines.

**THE INVENTION MOMENT:** What if you could write data to a durable, ordered log that multiple independent consumers can read independently — each maintaining its own position, each replaying from any point in the last 24 hours? All consumers see the same ordered stream. New consumers can backfill from the beginning. No message is deleted on read.

---

### 📘 Textbook Definition

**Amazon Kinesis Data Streams** is a fully managed real-time data streaming service that captures, stores, and delivers data records in strict per-shard order. A stream is divided into **shards** — each shard provides 1 MB/s write throughput and 2 MB/s read throughput. Records are assigned to shards via a **partition key** (MD5-hashed to determine shard). Records are identified by a **sequence number** (monotonically increasing per shard) and retained for 24 hours by default (extendable to 365 days). Multiple consumers can independently read from the same shard using either standard (shared 2 MB/s) or **enhanced fan-out** (dedicated 2 MB/s per consumer via HTTP/2 push). The **Kinesis Producer Library (KPL)** provides aggregation and batching; the **Kinesis Client Library (KCL)** handles consumer checkpointing, shard leases, and dynamic load balancing.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Kinesis is a distributed, durable, ordered log of records that any number of consumers can read independently without consuming the data.

> Think of it as a conveyor belt at a factory: items flow past in order, any worker can inspect items at their station, items are not removed when inspected, and a new worker can start from any earlier position on the belt.

**One insight:** The key difference from SQS is non-destructive reads — reading a record does not remove it. This enables multiple independent consumers, message replay, backfill processing, and crash recovery without re-sending data.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Order matters — real-time event processing often requires causal ordering (event A before event B).
2. Multiple consumers need the same data independently — one queue per consumer is prohibitively expensive.
3. Consumer failures must not lose data — consumers should resume from their last checkpoint, not from "now".
4. Write throughput must scale horizontally — a single node cannot absorb millions of events/second.

**DERIVED DESIGN:**

A Kinesis stream partitions data across shards. The producer specifies a partition key; Kinesis hashes it to determine the shard, ensuring all records with the same key land on the same shard in order. Each shard is an independent ordered log. Consumers maintain a **shard iterator** (a cursor into the shard) and checkpoint their position in DynamoDB via KCL. When a shard is split or merged (resharding), KCL redistributes shard leases across consumer workers automatically.

**THE TRADE-OFFS:**

**Gain:** Strict per-shard ordering. Non-destructive reads enable multiple independent consumers and replay. Configurable retention (up to 365 days) enables backfill. Enhanced fan-out gives each consumer dedicated 2 MB/s without competing for shared bandwidth.

**Cost:** Manual shard capacity management (each shard: 1 MB/s write, 2 MB/s read). Partition key hotspots concentrate load on one shard. KCL requires a DynamoDB table for checkpointing (adds latency and cost). Enhanced fan-out costs $0.015/shard-hour + $0.013/GB — significantly more than standard reads.

---

### 🧪 Thought Experiment

**SETUP:** You emit 10 000 clickstream events/second from a web application. Three consumers need the data: a real-time dashboard (reads latest), a fraud model (reads all events in order), and an S3 archiver (batches into files).

**WHAT HAPPENS WITHOUT Kinesis:** You use SQS. The dashboard consumes and deletes messages — fraud model never sees them. You create three SQS queues and publish to each — 3× write cost, 3× storage cost. S3 archiver falls behind during peak — it cannot catch up because SQS does not support replay; those events are gone.

**WHAT HAPPENS WITH Kinesis:** One stream with 10 shards (10 MB/s write capacity). All three consumers use enhanced fan-out — each gets 2 MB/s per shard, independently. The S3 archiver falls behind → its iterator is simply behind the current position; it catches up by reading forward. A fraud model is added three months later → it subscribes from the beginning of retention (or day 0 if using 365-day retention) and backfills without re-instrumentation.

**THE INSIGHT:** Kinesis separates write throughput (shards, partition keys) from read throughput (enhanced fan-out, independent iterators). The stream is the single source of truth; consumers are independent views over it.

---

### 🧠 Mental Model / Analogy

> Kinesis is like a multi-lane highway with toll cameras at every point. Cars (records) travel in one direction, in lane order (shard order). Every toll camera (consumer) can photograph every car independently — one camera photographing a car does not remove it from the highway. A new camera installed today can scroll back through stored footage from yesterday.

- **Highway** → Kinesis stream
- **Lanes** → Shards (each lane has independent throughput)
- **Cars** → Data records
- **Lane assignment** → Partition key → shard mapping
- **Toll camera** → Consumer (application/Lambda/KCL worker)
- **Camera position (checkpoint)** → Sequence number cursor stored in DynamoDB
- **Stored footage** → Record retention window (24 hr to 365 days)

Where this analogy breaks down: unlike a highway with fixed lanes, Kinesis shards can be split (doubling a lane's capacity) or merged (halving) while the stream is live — the highway can be dynamically reconfigured.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Kinesis is a conveyor belt for data. Many producers load items onto it; many readers can watch items pass, each from their own position. Items stay on the belt for up to a year.

**Level 2 — How to use it (junior developer):**
Create a Kinesis Data Stream with N shards. Use `PutRecord` (single) or `PutRecords` (batch, up to 500) to write. Specify `PartitionKey` to control which shard receives the record. Use `GetShardIterator` + `GetRecords` to read, or configure Lambda as an event source (managed polling). Store the last `SequenceNumber` as your checkpoint.

**Level 3 — How it works (mid-level engineer):**
Each shard supports 1 MB/s or 1 000 records/s writes, and 2 MB/s or 5 `GetRecords` calls/s reads (shared mode). With standard reading, all consumers on a shard share the 2 MB/s limit. With **enhanced fan-out** (`RegisterStreamConsumer`), each registered consumer gets a dedicated 2 MB/s HTTP/2 push subscription per shard — latency drops from ~200 ms to ~70 ms. KPL aggregation packs multiple small records into one Kinesis record (up to 1 MB), increasing effective throughput. KCL creates one worker per shard, stores lease and checkpoint in DynamoDB, and rebalances on worker failure or scaling.

**Level 4 — Why it was designed this way (senior/staff):**
Kinesis shards are the unit of both capacity and ordering. Per-shard ordering is a deliberate constraint — global ordering across all shards would require a global sequence number coordinator, which is a distributed systems bottleneck (similar to why Kafka partitions have per-partition ordering only). The partition key design puts ordering control in the producer: records for the same entity (user ID, device ID) use the same partition key → same shard → guaranteed in-order processing. Shard-level throughput limits exist because each shard is backed by a dedicated set of storage servers — this is a capacity reservation model, not a shared pool. Enhanced fan-out uses HTTP/2 server-push to achieve sub-100 ms latency by eliminating the polling round-trip of `GetRecords` — each registered consumer gets a dedicated multiplexed stream per shard from the storage layer.

---

### ⚙️ How It Works (Mechanism)

```
+-----------------------------------------------+
| Producer (KPL or SDK)                         |
|  PutRecords(records, partitionKey)            |
|       |                                       |
|       v                                       |
| Kinesis stream routing:                       |
|  MD5(partitionKey) -> shard assignment        |
|       |                                       |
|  [Shard 0]  [Shard 1]  [Shard 2]             |
|  ordered    ordered    ordered                |
|  log        log        log                    |
|       |          |          |                 |
|  Consumer A  Consumer A  Consumer A           |
|  Consumer B  Consumer B  Consumer B           |
|  (each maintains own sequence number cursor)  |
|       |                                       |
| Checkpoint: DynamoDB (KCL) per shard          |
+-----------------------------------------------+
```

**Kinesis Data Firehose** (managed delivery):

```
+-----------------------------------------------+
| Producers -> Firehose delivery stream         |
| -> Buffers (size: up to 128 MB,               |
|             interval: up to 900 s)            |
| -> Transforms (Lambda, optional)              |
| -> Delivers to: S3, Redshift, OpenSearch,     |
|                 Splunk, HTTP endpoint         |
| Auto-scales; no shards to manage             |
+-----------------------------------------------+
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**

```
IoT sensors / app events
  |
  v
KPL: aggregate small records, retry on error
  |
  v
PutRecords(batch)                <- YOU ARE HERE
  |
  v
Kinesis: MD5(partitionKey)
  -> Shard 3 (userId hash)
  |
  v
Record stored with SequenceNumber
Retention: 24 hr (default)
  |
  v
Consumer A (real-time dashboard):
  GetShardIterator(LATEST)
  GetRecords every 200 ms
  -> process, no checkpoint needed (stateless)

Consumer B (fraud model, KCL):
  GetShardIterator(AFTER_SEQUENCE_NUMBER, checkpoint)
  -> process batch
  -> checkpoint(sequenceNumber) to DynamoDB
  -> on crash: restart from last DynamoDB checkpoint

Consumer C (enhanced fan-out):
  RegisterStreamConsumer
  SubscribeToShard (HTTP/2 push, ~70 ms latency)
  -> records pushed without polling
```

**FAILURE PATH:** Consumer B crashes mid-batch → DynamoDB checkpoint is at last successful record → KCL worker restart reads from checkpoint → records are reprocessed (at-least-once). Producers handle `ProvisionedThroughputExceededException` (shard write limit exceeded) via KPL retry with exponential backoff. Data not consumed within retention window is permanently deleted — no DLQ equivalent.

**WHAT CHANGES AT SCALE:** Partition key hotspots send all traffic to one shard. Monitor `WriteProvisionedThroughputExceeded` per shard. Add a random suffix to partition keys for write-heavy keys (trades ordering for write distribution). Use `UpdateShardCount` to split hot shards. For massive scale (>1 GB/s), Kinesis Data Streams on-demand mode auto-scales without shard management.

---

### 💻 Code Example

**BAD — Hotspot partition key (all records on one shard):**
```python
import boto3
kinesis = boto3.client('kinesis')

# BAD: constant partition key -> all records -> shard 0
# Throughput limited to 1 MB/s regardless of stream capacity
for event in events:
    kinesis.put_record(
        StreamName='clickstream',
        Data=json.dumps(event),
        PartitionKey='all-events'   # HOTSPOT
    )
```

**GOOD — High-cardinality partition key + batch writes:**
```python
import boto3, json, hashlib

kinesis = boto3.client('kinesis')

def put_events_batch(events: list[dict]):
    """
    Batch up to 500 records per PutRecords call.
    Use userId as partition key: orders all events
    per user on the same shard.
    """
    records = [
        {
            'Data': json.dumps(event).encode('utf-8'),
            # High-cardinality key: events per user ordered
            'PartitionKey': event['userId']
        }
        for event in events
    ]
    # PutRecords: up to 500 records, up to 5 MB total
    response = kinesis.put_records(
        StreamName='clickstream',
        Records=records
    )
    # Handle partial failures (individual record errors)
    failed = response.get('FailedRecordCount', 0)
    if failed > 0:
        retry_records = [
            records[i]
            for i, r in enumerate(response['Records'])
            if 'ErrorCode' in r
        ]
        # Retry failed records with backoff
        put_events_batch_with_retry(retry_records)
```

```python
# Lambda consumer with KCL-managed checkpointing
def lambda_handler(event, context):
    for record in event['Records']:
        # Kinesis record: base64-encoded Data
        import base64
        payload = json.loads(
            base64.b64decode(record['kinesis']['data'])
        )
        process_event(payload)
    # Lambda checkpoints automatically on success
    # On exception: Lambda retries from last checkpoint
```

---

### ⚖️ Comparison Table

| Feature              | Kinesis Data Streams | Apache Kafka     | AWS SQS          | Kinesis Firehose  |
|----------------------|----------------------|------------------|------------------|-------------------|
| Ordering             | Per shard            | Per partition    | FIFO only        | No               |
| Replay               | Yes (up to 365d)     | Yes (configurable)| No               | No               |
| Multiple consumers   | Yes (fan-out)        | Yes (consumer groups)| No (destructive)| Delivery only   |
| Management overhead  | Low (managed)        | High (self-managed)| None (fully managed)| None           |
| Max record size      | 1 MB                 | Configurable     | 256 KB           | 1 MB             |
| Throughput unit      | Shard (1 MB/s write) | Partition        | Unlimited        | Auto-scales      |
| Latency              | 70–200 ms            | <10 ms possible  | 0–20 s           | 60 s – 15 min    |
| Schema registry      | No (use Glue)        | Confluent Schema | No               | No               |

---

### 🔁 Flow / Lifecycle

**Record Lifecycle:**

```
+-----------------------------------------------+
| 1. PRODUCED  -> PutRecord/PutRecords called   |
| 2. ROUTED    -> MD5(partitionKey)->shard      |
| 3. STORED    -> Assigned SequenceNumber;      |
|               replicated across AZs           |
| 4. READABLE  -> Available for GetRecords      |
|               or enhanced fan-out push        |
| 5. CONSUMED  -> Consumer reads; record stays  |
|               (non-destructive read)          |
| 6. EXPIRED   -> Retention period elapsed;     |
|               record permanently deleted      |
+-----------------------------------------------+
```

**Shard Lifecycle (resharding):**

1. **Provision** — Create stream with N shards (or on-demand mode)
2. **Monitor** — Watch `WriteProvisionedThroughputExceeded` and `ReadProvisionedThroughputExceeded`
3. **Split** — Hot shard split into 2; parent shard sealed, children inherit records
4. **Redistribute** — KCL detects new shards; redistributes leases to workers
5. **Drain** — Parent shard reads reach end of data; KCL transitions to child shards
6. **Merge** — Cold adjacent shards merged; reduces cost

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Kinesis guarantees global ordering" | Ordering is per-shard only. Records with different partition keys on different shards have no global order guarantee. |
| "Reading a record removes it from the stream" | Records remain in the stream until the retention window expires. All consumers independently read the same records. |
| "More shards = faster processing" | More shards increase write capacity. Consumer processing speed depends on consumer count, batch size, and processing logic — not shard count alone. |
| "Kinesis and Kinesis Firehose are the same" | Data Streams is a low-latency stream with consumer-managed cursors. Firehose is a managed delivery pipeline to S3/Redshift with buffering — no direct consumer control. |
| "Partition key only determines throughput" | Partition key determines both shard assignment AND ordering. All records with the same partition key are on the same shard in the order they were written. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1 — Shard hotspot (ProvisionedThroughputExceededException)**

**Symptom:** Producers receive `ProvisionedThroughputExceededException`; one shard is at 100% utilisation while others are idle. Some records are dropped by KPL retries.
**Root Cause:** Low-cardinality or constant partition key (e.g. `"all"`, date string) routes all writes to one shard.
**Diagnostic:**
```bash
# Check per-shard write metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Kinesis \
  --metric-name WriteProvisionedThroughputExceeded \
  --dimensions \
    Name=StreamName,Value=clickstream \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-01T01:00:00Z \
  --period 60 --statistics Sum
# Non-zero = shard is exceeding write limit
```
**Fix:** Use high-cardinality partition keys (userId, deviceId, UUID). If the data has inherently low cardinality (e.g. event type), append a random suffix: `eventType + "-" + random(0,N)` and accept cross-shard ordering.
**Prevention:** Analyse partition key distribution before production. Use KPL aggregation to pack small records efficiently. Consider on-demand capacity mode for unpredictable workloads.

---

**Mode 2 — Consumer falling behind (iterator age growing)**

**Symptom:** `GetRecords.IteratorAgeMilliseconds` metric grows over time; consumers are reading old data; processing latency increases.
**Root Cause:** Consumer processing speed is less than producer write rate. Slow downstream (database, API), insufficient consumer instances, or large record processing time.
**Diagnostic:**
```bash
# IteratorAge = how far behind the consumer is
aws cloudwatch get-metric-statistics \
  --namespace AWS/Kinesis \
  --metric-name GetRecords.IteratorAgeMilliseconds \
  --dimensions \
    Name=StreamName,Value=clickstream \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-01T02:00:00Z \
  --period 300 --statistics Maximum
# Growing trend = consumer falling behind
```
**Fix:** Scale consumer workers (one KCL worker per shard is optimal). Optimise processing logic (reduce downstream latency, parallelise work within a batch). Split hot shards to distribute load.
**Prevention:** Alert on `IteratorAgeMilliseconds` exceeding a threshold (e.g. > 1 min for real-time workloads). Capacity plan: consumer throughput must exceed peak producer throughput.

---

**Mode 3 — Data loss at retention window boundary**

**Symptom:** Consumer stops for maintenance. Returns to find records older than 24 hours are gone. Critical events are permanently lost.
**Root Cause:** Default retention is 24 hours. Consumer outage exceeded retention window.
**Diagnostic:**
```bash
# Check stream retention period
aws kinesis describe-stream-summary \
  --stream-name clickstream \
  | jq '.StreamDescriptionSummary.RetentionPeriodHours'
# 24 = default; increase if needed
```
**Fix:**
```bash
# BAD: default 24-hour retention for critical data
# No buffer for consumer outages

# GOOD: extend retention based on SLA
aws kinesis increase-stream-retention-period \
  --stream-name clickstream \
  --retention-period-hours 168  # 7 days
```
**Prevention:** Set retention to at least 2× your maximum expected consumer downtime. For compliance use cases, use 365-day retention. Monitor consumer iterator age — alert before data approaches the retention boundary.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- Streaming Data — the general pattern of continuous, ordered event ingestion
- AWS — IAM, CloudWatch metrics, Lambda event source mapping, DynamoDB
- Apache Kafka — understanding Kafka's partition model helps explain Kinesis shard design

**Builds On This (learn these next):**
- AWS Glue — ETL transformations on Kinesis data for data lake ingestion
- Apache Flink — stateful stream processing on Kinesis (Kinesis Data Analytics)
- Kinesis Data Firehose — managed delivery pipeline built on top of Kinesis

**Alternatives / Comparisons:**
- Apache Kafka — self-managed (or Confluent/MSK), lower latency, richer ecosystem; preferred for >1 GB/s or multi-region
- AWS SQS — use when ordering is not required and exactly-once matters more than replay
- AWS MSK (Managed Kafka) — managed Kafka on AWS, preferred for Kafka-compatible workloads

---

### 📌 Quick Reference Card

```
+--------------------------------------------------+
| WHAT IT IS   | Managed ordered data stream       |
| PROBLEM      | Ordered, replayable multi-consumer|
|              | stream at scale                   |
| KEY INSIGHT  | Non-destructive reads: N consumers|
|              | independent, each with cursor     |
| USE WHEN     | Real-time, ordered, multi-consumer|
| AVOID WHEN   | Simple queue; no ordering needed  |
| TRADE-OFF    | Shard management vs unlimited SQS |
| ONE-LINER    | PutRecords(partitionKey) ->        |
|              | ordered per shard; replay anytime |
| NEXT EXPLORE | KPL/KCL, Enhanced Fan-Out, Glue   |
+--------------------------------------------------+
```

---

### 🧠 Think About This Before We Continue

1. **(First Principles)** You use `userId` as your Kinesis partition key. A viral influencer generates 10 000 events/second from their account while average users generate 1 event/second. What problem does this cause, and what are your two architectural options — each with its own ordering trade-off?

2. **(Scale)** Your stream has 10 shards. You add a second consumer application. Standard mode gives all consumers a shared 2 MB/s per shard. Enhanced fan-out gives each consumer a dedicated 2 MB/s. At what consumer count does the cost of enhanced fan-out ($0.015/shard-hour) become cheaper than the latency cost of standard mode, and how would you measure the break-even point?

3. **(System Interaction)** A KCL consumer crashes mid-batch after processing 50 of 100 records. It checkpointed after record 50. On restart, it replays records 51–100. But records 47–50 modified a database that was not transactional with the checkpoint. What data integrity problem exists, and what design pattern resolves it?
