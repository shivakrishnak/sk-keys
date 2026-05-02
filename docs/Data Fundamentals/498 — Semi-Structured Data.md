---
layout: default
title: "Semi-Structured Data"
parent: "Data Fundamentals"
nav_order: 498
permalink: /data-fundamentals/semi-structured-data/
number: "498"
category: Data Fundamentals
difficulty: ★☆☆
depends_on: "Structured vs Unstructured Data, Data Types (Primitive, Complex, Semi-Structured)"
used_by: "Data Formats, Avro, Schema Registry, Data Lake, ETL pipelines"
tags: #data, #semi-structured, #json, #xml, #avro, #schema-on-read
---

# 498 — Semi-Structured Data

`#data` `#semi-structured` `#json` `#xml` `#avro` `#schema-on-read`

⚡ TL;DR — **Semi-structured data** carries its own schema inline (self-describing) but does not require a pre-declared, fixed schema. JSON events, XML feeds, and Avro records are the dominant formats. Schema-on-read: structure is interpreted at query/processing time. The universal pattern: ingest semi-structured → validate → convert to structured columnar format (Parquet) for analytics.

| #498            | Category: Data Fundamentals                                   | Difficulty: ★☆☆ |
| :-------------- | :------------------------------------------------------------ | :-------------- |
| **Depends on:** | Structured vs Unstructured Data, Data Types                   |                 |
| **Used by:**    | Data Formats, Avro, Schema Registry, Data Lake, ETL pipelines |                 |

---

### 📘 Textbook Definition

**Semi-structured data**: data that does not conform to the rigid structure of relational tables but contains tags, markers, or hierarchical nesting that distinguishes its elements. The schema is either embedded inline (JSON/XML: field names are stored with each record) or encoded separately but linked to each record (Avro: schema referenced by ID in schema registry). Key characteristics: (1) **Self-describing** — each record contains its own field names; (2) **Flexible schema** — records can have different fields without a central schema migration; (3) **Hierarchical / nested** — supports nested objects and arrays, unlike flat relational rows; (4) **Schema-on-read** — the application interprets the structure when reading, not when writing. Common formats: JSON, XML, YAML, Avro (with schema registry), Parquet (not semi-structured — requires pre-declared schema).

---

### 🟢 Simple Definition (Easy)

JSON is the classic example:

```json
{"user_id": "U001", "event": "purchase", "amount": 149.99}
{"user_id": "U002", "event": "view", "product_id": "P555"}
```

Both records are "data" but have different fields. A relational database would struggle — it needs fixed columns. JSON says "each record carries its own field names." That's semi-structured: it has structure (key-value pairs, nesting), but the structure is flexible and embedded in the data itself, not declared externally in a schema.

---

### 🔵 Simple Definition (Elaborated)

Semi-structured data solves the problem of **flexible, evolving schemas**. A mobile app releasing new features every sprint sends new event types with new fields. If you stored events in a relational table, you'd need a schema migration every sprint. Instead, you stream JSON events to Kafka/S3 — each event carries its fields inline. The downstream consumers decide which fields they care about (schema-on-read).

The trade-off: every downstream system must parse the format. JSON parsing is CPU-intensive at scale. The standard data lake pattern converts semi-structured raw JSON → structured Parquet in the refinement step, getting the best of both worlds: flexible ingestion + fast columnar analytics.

---

### 🔩 First Principles Explanation

```
SEMI-STRUCTURED FORMAT COMPARISON:

  FORMAT   │ SCHEMA      │ BINARY? │ COMPRESSION │ USE CASE
  ─────────┼─────────────┼─────────┼─────────────┼──────────────────
  JSON     │ Inline keys │ No      │ Yes (gzip)  │ REST APIs, events
  XML      │ Inline tags │ No      │ Yes (gzip)  │ Enterprise/B2B
  YAML     │ Inline keys │ No      │ Rarely      │ Config files
  Avro     │ Linked      │ Yes     │ Yes (snappy)│ Kafka, streaming
  BSON     │ Inline keys │ Yes     │ No          │ MongoDB storage

SELF-DESCRIBING vs SCHEMA-LINKED:

  JSON (self-describing):
  {"name": "Alice", "age": 30}  ← field names embedded in every record

  Avro (schema-linked):
  Binary payload: [0x01, 0x0A, 0x41, 0x6C, ...]
  + Schema ID: 42
  Schema registry: ID 42 = {fields: [{name:"name",type:"string"},{name:"age",type:"int"}]}

  JSON: every record repeats field names → verbose but self-contained
  Avro: field names stored once in registry → compact but requires registry access

NESTING: JSON supports arbitrary depth

  {
    "order_id": "ORD-001",
    "customer": {
      "id": "CUST-001",
      "address": {
        "street": "123 Main St",
        "city": "Seattle"
      }
    },
    "items": [
      {"product_id": "P001", "qty": 2, "price": 29.99},
      {"product_id": "P002", "qty": 1, "price": 89.50}
    ],
    "tags": ["express", "gift"],
    "metadata": null
  }

  Relational normalization: this → 3 tables (orders, order_items, addresses)
  JSON: single document; flexible; one read to get all data
  Trade-off: joins are replaced by nesting, but querying nested data is harder

SCHEMA-ON-READ vs SCHEMA-ON-WRITE:

  SCHEMA-ON-WRITE (PostgreSQL, Parquet):
  1. Define schema: CREATE TABLE events (id BIGINT, type VARCHAR(50), ...)
  2. Write: INSERT validates against schema → reject non-conforming data
  3. Read: column layout known → fast scan, statistics, push-down
  ✅ Errors at write time (fail fast), fast queries
  ❌ Schema migration required for new fields; rigid

  SCHEMA-ON-READ (JSON on S3):
  1. Write: any JSON accepted; no schema enforcement
  2. Read: define how to interpret data at query time
     SELECT json_extract(raw, '$.amount') FROM events
  ✅ Flexible ingestion; no migration needed
  ❌ Errors at read time; slower queries; no column statistics

  HYBRID (Avro + Schema Registry):
  1. Producer registers schema in registry → schema has version ID
  2. Write: Avro producer validates payload against schema
     → fail fast at producer if schema violated (schema-on-write benefit)
  3. Read: consumer fetches schema by ID → decode binary payload
     → compact binary storage (schema-on-read benefit: consumer chooses interpretation)
  ✅ Fail fast + compact binary + schema evolution support
  ✅ Backward/forward compatibility enforced by registry

SCHEMA EVOLUTION IN SEMI-STRUCTURED DATA:

  JSON evolution (no registry):
  Week 1:  {"event":"purchase", "amount":149.99}
  Week 4:  {"event":"purchase", "amount":149.99, "currency":"USD"}  ← new field
  Week 8:  {"event":"purchase", "total":149.99}  ← renamed field (BREAKING)

  Consumers of Week 8 data: $.amount → NULL (silently broken)

  Avro evolution (with registry):
  Schema v1: {fields: [name:"amount", type:"double"]}
  Schema v2: {fields: [name:"amount", type:"double"],
                       [name:"currency", type:"string", default:"USD"]}  ← add w/ default

  Consumer with v1 schema reads v2 record:
  → currency field: not in v1 schema → IGNORED (backward compatible)
  Consumer with v2 schema reads v1 record:
  → currency field missing → use default "USD" (forward compatible)

  BREAKING change detected at registry registration time, not at consumption time
```

---

### ❓ Why Does This Exist (Why Before What)

Real-world data sources evolve constantly: mobile apps ship new features weekly, each producing new event fields. Requiring a schema migration before every new field is possible leads to either: (a) blocked feature development waiting for DBA approval, or (b) data engineers scrambling to update DDL on every release. Semi-structured formats decouple producer schema evolution from consumer schema requirements — enabling independent deployment of producers and consumers. This is the core proposition of Kafka + Avro + Schema Registry in streaming architectures.

---

### 🧠 Mental Model / Analogy

> **A bulletin board at a community center** (semi-structured) vs **a structured intake form** (structured). The intake form has fixed fields: Name, Address, Phone. If you want to add "Email," you print new forms (schema migration). The bulletin board accepts any notice, in any format — some have phone numbers, some have QR codes, some have maps. You read each notice and interpret it yourself (schema-on-read). Avro + Schema Registry is like a bulletin board with a librarian: you can post any format, but you must register it with the librarian first, and the librarian checks compatibility with previous versions.

---

### ⚙️ How It Works (Mechanism)

```
JSON INGESTION PIPELINE:

  Mobile app → HTTP POST {"event":"purchase","amount":149.99,"userId":"U001"}
      │
      ▼
  API Gateway → Kafka topic "events" (JSON strings)
      │
      ▼
  Spark Streaming / Flink reads JSON strings
  → parse with schema (explicit or inferred)
  → validate (filter malformed records to dead-letter topic)
  → flatten nested fields
  → write as Parquet to S3 (partitioned by date + event_type)
      │
      ▼
  Athena / Presto / Spark SQL: query structured Parquet
  SELECT SUM(amount) FROM events WHERE event_type='purchase' AND date='2024-01-15'
  → columnar scan, predicate pushdown, column pruning

AVRO + SCHEMA REGISTRY:

  Producer:
  1. Register schema v1 in registry → receive ID=42
  2. Serialize: [magic_byte=0x00][schema_id=42 (4 bytes)][avro_binary_payload]
  3. Publish to Kafka topic

  Consumer:
  1. Receive Kafka message
  2. Read first 5 bytes → schema ID = 42
  3. Fetch schema v1 from registry (cached after first fetch)
  4. Deserialize binary payload using schema
  5. Process typed Java/Python object
```

---

### 🔄 How It Connects (Mini-Map)

```
Flexible data sources (APIs, mobile events, IoT)
        │
        ▼
Semi-Structured Data ◄── (you are here)
(JSON, XML, Avro — self-describing, schema-on-read)
        │
        ├── Data Formats (JSON, XML, YAML, CSV): the specific formats
        ├── Avro: binary semi-structured + schema registry
        ├── ETL pipeline: semi-structured → Parquet (structured)
        ├── Schema Registry: adding governance to semi-structured streams
        └── Delta Lake: handles schema evolution on top of Parquet
```

---

### 💻 Code Example

```python
# Python: reading and validating JSON (semi-structured) then writing Parquet (structured)

import json
import pyarrow as pa
import pyarrow.parquet as pq
from pathlib import Path

# SEMI-STRUCTURED: variable JSON records
events = [
    '{"user_id": "U001", "event": "purchase", "amount": 149.99, "currency": "USD"}',
    '{"user_id": "U002", "event": "view", "product_id": "P555"}',  # no amount
    '{"user_id": "U003", "event": "purchase", "amount": 89.50}',    # no currency
    '{"user_id": "U004", "event": "refund", "amount": -49.99, "reason": "damaged"}',
]

# PARSE + NORMALIZE: extract known fields, handle missing ones
rows = []
dead_letter = []

for raw in events:
    try:
        record = json.loads(raw)
        # Extract with defaults for optional fields
        rows.append({
            "user_id": record["user_id"],        # required
            "event_type": record["event"],        # required
            "amount": record.get("amount"),       # optional → None if missing
            "currency": record.get("currency", "USD"),  # default "USD"
            "product_id": record.get("product_id"),     # optional
        })
    except (json.JSONDecodeError, KeyError) as e:
        dead_letter.append({"raw": raw, "error": str(e)})

# WRITE AS STRUCTURED PARQUET:
schema = pa.schema([
    pa.field("user_id", pa.string()),
    pa.field("event_type", pa.string()),
    pa.field("amount", pa.float64()),    # nullable
    pa.field("currency", pa.string()),
    pa.field("product_id", pa.string()), # nullable
])

table = pa.Table.from_pylist(rows, schema=schema)
pq.write_table(table, "events.parquet")
# ✅ Now queryable with SQL: SELECT SUM(amount) WHERE event_type='purchase'
```

---

### ⚠️ Common Misconceptions

| Misconception                                            | Reality                                                                                                                                                                                                                                                                                                                 |
| -------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Avro is not semi-structured because it requires a schema | Avro is semi-structured: it carries a schema reference inline (schema ID in each message). The schema itself is stored externally (registry) but the data is self-identifying. This is different from Parquet (fully structured — schema in file footer) and from plain JSON (schema inference required at query time). |
| Schema-on-read means no schema at all                    | Schema-on-read means the schema is applied when reading, not when writing. You still need a schema to interpret the data — you just apply it later. Spark's JSON reader infers a schema from a sample; Athena infers from a CREATE EXTERNAL TABLE DDL.                                                                  |
| YAML is used in data pipelines                           | YAML is primarily a configuration format (CI/CD pipelines, Kubernetes manifests, dbt config). It's semi-structured but not used for data transport at scale (verbose, slow to parse, no binary representation).                                                                                                         |

---

### 🔥 Pitfalls in Production

```
PITFALL: silent data loss with permissive JSON parsing

  # PySpark: inferSampling samples 1% of records by default
  df = spark.read.option("inferSchema", "true").json("s3://bucket/events/")

  # If a field appears in only 5% of records and none are in the sample:
  # → field is not in inferred schema → silently NULL for all records

  # If a field is INT in 99% of records and STRING in 1%:
  # → Spark may infer INT → 1% of records fail to parse → silently NULL

  FIX 1: always use explicit schema for production pipelines
  FIX 2: use schema registry (Avro) → type enforcement at producer
  FIX 3: route parse failures to dead-letter queue, alert on DLQ size

  # Dead-letter pattern in PySpark:
  from pyspark.sql.functions import from_json, col

  schema = StructType([...])  # explicit
  df_parsed = df_raw.withColumn("parsed", from_json(col("value"), schema))
  df_good = df_parsed.filter(col("parsed").isNotNull())
  df_bad = df_parsed.filter(col("parsed").isNull())  # DLQ
  df_bad.write.mode("append").json("s3://bucket/dead-letter/events/")
```

---

### 🔗 Related Keywords

- `Structured vs Unstructured Data` — where semi-structured fits on the spectrum
- `Data Formats (JSON, XML, YAML, CSV)` — the specific wire formats for semi-structured data
- `Avro` — binary semi-structured format with embedded schema references
- `Schema Registry` — adds governance and compatibility enforcement to semi-structured streams
- `Delta Lake` — handles schema evolution for structured data derived from semi-structured sources

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ SEMI-STRUCTURED │ Self-describing, flexible schema,      │
│                 │ schema-on-read; key-value / nested     │
├─────────────────┼────────────────────────────────────────┤
│ Formats         │ JSON, XML, YAML, Avro, BSON           │
│ Schema          │ Inline keys (JSON) or ID reference    │
│                 │ (Avro + registry)                     │
│ Query           │ json_extract() slow; convert→Parquet  │
│ Evolution       │ Flexible (JSON) or governed (Avro)    │
├─────────────────┴────────────────────────────────────────┤
│ PATTERN: semi-structured raw → ETL → structured Parquet │
│           + dead-letter queue for parse failures        │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Avro with a Schema Registry is described as a "hybrid" between schema-on-write and schema-on-read. Explain why: which part is schema-on-write (fail fast, validation), and which part is schema-on-read (flexibility, consumer autonomy)? How does the registry's backward/forward compatibility mode affect what changes producers are allowed to make?

**Q2.** The JSON → Parquet ETL conversion is the standard data lake pattern. But it introduces latency (batch ETL runs every hour) and complexity (another job to maintain). Streaming query engines like Apache Flink and Spark Structured Streaming can query Kafka JSON topics in real time without first converting to Parquet. When would you skip the ETL step and query raw semi-structured data directly? What are the performance and reliability trade-offs?
