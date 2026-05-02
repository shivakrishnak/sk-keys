---
layout: default
title: "Binary Formats (Avro, Parquet, ORC, Protobuf)"
parent: "Data Fundamentals"
nav_order: 500
permalink: /data-fundamentals/binary-formats/
number: "0500"
category: Data Fundamentals
difficulty: ★★☆
depends_on: Data Formats, Serialization Formats, Columnar vs Row Storage, Data Types
used_by: Schema Registry, Data Lake, Big Data, Apache Spark, Kafka Streams
related: Avro, Parquet, ORC, Serialization Formats, Data Compression
tags:
  - dataengineering
  - intermediate
  - bigdata
  - streaming
  - performance
---

# 500 — Binary Formats (Avro, Parquet, ORC, Protobuf)

⚡ TL;DR — Binary data formats sacrifice human-readability for dramatically smaller size and faster parsing, enabling data pipelines to handle billions of records efficiently.

| #500 | Category: Data Fundamentals | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Data Formats, Serialization Formats, Columnar vs Row Storage, Data Types | |
| **Used by:** | Schema Registry, Data Lake, Big Data, Apache Spark, Kafka Streams | |
| **Related:** | Avro, Parquet, ORC, Serialization Formats, Data Compression | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Your Kafka topic processes 1 billion JSON events per day. Each
JSON event is 400 bytes on average: key names like
`"customer_id"`, `"transaction_timestamp"`, `"amount_usd"`
repeated 1 billion times. That's 400 GB of data per day just for
one topic. Your S3 bill is $150/month for this topic alone.
Your Spark job reads 400 GB and must parse every character to
extract the three fields it actually uses for its aggregation.

**THE BREAKING POINT:**
At scale, JSON parsing becomes a CPU bottleneck. Spark workers
spend 40% of their time tokenising JSON characters instead of
doing computation. The schema is transmitted redundantly with
every record. Text representation of numbers is 3–8× larger than
binary. You cannot skip unneeded columns — you must read and
parse the entire record even if you only need 2 of 50 fields.

**THE INVENTION MOMENT:**
This is exactly why binary formats were created. Avro stores key
names once in a header schema, not per record. Parquet groups data
by column, so reading column X requires reading only column X's
bytes — not entire rows. Protobuf uses field numbers not names —
tiny on the wire. Numbers store as binary, not ASCII digits.
The same 1 billion events: 40 GB instead of 400 GB.

---

### 📘 Textbook Definition

**Binary data formats** encode structured data as compact binary
byte sequences rather than text characters, typically using
schemas to avoid repeating field metadata per record.
**Avro** is a row-oriented binary format with a schema embedded
in the file header; its primary design goal is schema evolution
and Kafka compatibility. **Parquet** is a columnar binary format
designed for analytical workloads; it groups data by column and
applies column-specific compression and encoding. **ORC**
(Optimised Row Columnar) is Hive's columnar format with built-in
indexes and Bloom filters. **Protobuf** (Protocol Buffers) is
a language-neutral schema-defined binary serialisation format
designed by Google for inter-service RPC and storage.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Binary formats pack data as bytes instead of characters —
smaller, faster, but not human-readable.

**One analogy:**

> Compare a handwritten recipe card (JSON) to a barcode (binary).
> The recipe card is readable by anyone without equipment.
> The barcode is unreadable to humans but a scanner reads it
> in microseconds and it packs the same information in a fraction
> of the space. Binary formats are barcodes for data.

**One insight:**
The key distinction is WHERE the schema lives. In JSON, the schema
is inlined per record (as key names). In a binary format, the
schema lives in a header file, a schema registry, or a `.proto`
file — shared once, referenced by every record. This one change
alone reduces event size by 30–60%.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. A binary format must be able to round-trip: serialize →
   deserialize → same logical value.
2. Compactness requires eliminating redundancy — the schema
   must NOT be repeated per record.
3. Fast reads require data locality — fields frequently read
   together should be stored together.

**DERIVED DESIGN:**

*Avro — row-oriented, schema-in-header:*
Invariant 2 → schema stored once in file header (or Schema
Registry). Each row encodes values in schema-declared order with
no field names. Schema evolution supported via compatibility rules.
Best for: streaming records, event logs, Kafka — where you read
full records one by one.

*Parquet — columnar, schema-per-file:*
Invariant 3 → different access pattern: analytics reads 3 of 50
columns over billions of rows. Parquet stores all values of
column X together so a query needing only col X reads only col X
bytes. Row groups (128 MB blocks) partition data for parallel
reading. Column chunks within row groups use encoding specific
to each type: dictionary encoding for low-cardinality strings,
delta encoding for monotonic timestamps. Best for: OLAP queries,
data lake analytics.

*ORC — like Parquet with built-in indexes:*
Each ORC stripe (256 MB) has a stripe-level footer with
column-level min/max/bloom filter statistics. Reading engine can
skip entire stripes that don't match a WHERE clause predicate
before reading any data bytes. Best for: Hive workloads.

*Protobuf — schema-defined, field-number encoding:*
Field names replaced by field numbers (1 byte each). Each value
preceded by a wire type tag (field number + type = 1–2 bytes).
Optional fields absent from the stream entirely. Best for:
gRPC inter-service communication, Android apps, database storage
of structured messages. Schema defined in `.proto` files compiled
to language-specific classes.

**THE TRADE-OFFS:**
**Gain:** 3–10× size reduction; 5–20× faster analytics;
column pruning (read only needed columns); predicate pushdown
(skip rows/blocks not matching WHERE clause).
**Cost:** Not human-readable (cannot `cat` or `grep` a Parquet file);
requires schema management tooling; more complex ETL setup.

---

### 🧪 Thought Experiment

**SETUP:**
A data warehouse holds 1 billion IoT sensor records. Analysts
run one query 50 times per day:
`SELECT AVG(temperature) FROM sensors WHERE device_id = 'X42'`
The schema has 40 columns; the query uses 2.

**WHAT HAPPENS WITH JSON:**
Spark reads 400 GB. It parses every JSON record to find
`device_id` and `temperature` keys. CPU spends 70% of time in
JSON tokeniser. Query takes 45 minutes.

**WHAT HAPPENS WITH PARQUET:**
Spark reads only the `device_id` and `temperature` column files
— approximately 2 GB instead of 400 GB (column pruning). Within
those columns, row group statistics (min/max) let Spark skip row
groups where `device_id` != 'X42' without reading their data
(predicate pushdown). Temperature values are stored as `INT32`
with a scale factor, not ASCII strings — dictionary-decoded
in microseconds. Query takes 80 seconds.

**THE INSIGHT:**
Columnar storage and predicate pushdown are multiplicative
optimisations: reading fewer columns AND fewer rows means reading
orders of magnitude less data. The query was not rewritten —
the format change alone delivered a 33× speedup.

---

### 🧠 Mental Model / Analogy

> Think of a massive spreadsheet. **Row-oriented storage (Avro,
> JSON)** is like filing each complete row in its own folder —
> convenient when you need the whole record (one customer's
> complete profile). **Columnar storage (Parquet, ORC)** is like
> storing all values from column A together, all values from
> column B together — convenient when you need "show me all
> temperatures" without caring about the other 39 columns.

- "One folder per row" → Avro/JSON row-oriented storage
- "One folder per column" → Parquet/ORC columnar storage
- "Schema on the folder label" → Avro schema header
- "Skipping folders whose label says wrong range" → predicate pushdown
- "Compressing all temperatures together" → column-specific encoding

**Where this analogy breaks down:** Real Parquet uses **row groups**
— blocks of rows stored column-by-column within each block.
It's not pure columnar; it's a hybrid that balances write
performance with read performance.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Binary formats store data as compact bytes instead of readable
text. They're like compressed zip files for data — smaller and
faster to process, but you need special software to open them.
Parquet is for analytics (data warehouses). Avro is for data
streaming. Protobuf is for sending data between services.

**Level 2 — How to use it (junior developer):**
When writing Spark jobs, save DataFrames as Parquet:
`df.write.parquet("s3://my-bucket/data/")`. When setting up Kafka,
configure producers to use Avro with Schema Registry. When writing
gRPC services, define the API in a `.proto` file and use
generated client/server code. Reading: `spark.read.parquet(...)`,
`spark.read.format("avro").load(...)`.

**Level 3 — How it works (mid-level engineer):**
Parquet file anatomy: file header → N row groups → file footer.
Each row group: one column chunk per column → pages (default
1 MB) per column chunk. Column encoding is auto-selected:
`PLAIN` (raw bytes), `DICTIONARY` (encode values as IDs into a
dictionary — good for low-cardinality), `RLE_DICTIONARY` (run-
length-encode repetitive dictionary IDs — best for sorted data).
`SNAPPY` or `ZSTD` compression applied per column chunk.
Row group statistics (min, max, null count) written to footer —
used for predicate pushdown. Avro uses a JSON schema header
then binary-encoded rows using variable-length integer encoding
(zigzag for signed integers).

**Level 4 — Why it was designed this way (senior/staff):**
Parquet was co-designed by Twitter and Cloudera specifically to
solve the Hadoop era's problem of reading entire 512 MB map-
reduce splits when analytics only needed 5% of columns. The row
group / column chunk hybrid was a deliberate compromise: pure
column stores (like MonetDB) are optimal for reads but
catastrophic for streaming inserts, which always arrive as rows.
Parquet's 128 MB row groups make both streaming writes (one row
at a time) and analytical reads (entire column) tolerable —
not optimal for either, but good enough for both. This is the
key design insight: format design is always about the write/read
trade-off of the dominant workload-pair, not optimising for one
extreme.

---

### ⚙️ How It Works (Mechanism)

**Parquet file structure:**
```
┌──────────────────────────────────────────────────────┐
│              PARQUET FILE LAYOUT                     │
├──────────────────────────────────────────────────────┤
│  Magic bytes: "PAR1"                                 │
├──────────────────────────────────────────────────────┤
│  Row Group 0 (128 MB by default)                     │
│  ┌─────────────────────────────────────────────────┐ │
│  │ Column Chunk: device_id  [dict-encoded+snappy]  │ │
│  │ Column Chunk: timestamp  [delta-encoded]        │ │
│  │ Column Chunk: temperature [plain+snappy]        │ │
│  └─────────────────────────────────────────────────┘ │
├──────────────────────────────────────────────────────┤
│  Row Group 1 ... Row Group N                         │
├──────────────────────────────────────────────────────┤
│  Footer (Thrift-encoded)                             │
│  - Schema                                            │
│  - Row group offsets + sizes                         │
│  - Column statistics (min/max/nullCount per chunk)   │
│  Footer length (4 bytes)                             │
│  Magic bytes: "PAR1"                                 │
└──────────────────────────────────────────────────────┘
```

**How predicate pushdown works:**
```
Query: WHERE temperature > 100

Step 1: Read footer — free (metadata only)
  Row Group 0: temperature min=20, max=85 → SKIP ← no bytes read
  Row Group 1: temperature min=90, max=120 → READ
  Row Group 2: temperature min=10, max=70 → SKIP

Step 2: Read only Row Group 1's temperature column chunk
Step 3: Filter in memory
```

**Avro row layout:**
```
[schema JSON, compressed] [sync marker]
[block count][block bytes][sync marker] ...

Each record within a block:
  [field1_value][field2_value][field3_value]...
  (no field names — schema defines order)
```

---

### 💻 Code Example

**Example 1 — Write/read Parquet with PySpark:**
```python
from pyspark.sql import SparkSession
spark = SparkSession.builder.getOrCreate()

# Write DataFrame as Parquet — partitioned by date
df.write \
  .partitionBy("event_date") \
  .mode("overwrite") \
  .parquet("s3://my-bucket/events/")

# Read with column pruning (Spark passes needed columns down)
result = spark.read.parquet("s3://my-bucket/events/") \
  .select("device_id", "temperature") \
  .filter("device_id = 'X42'")
# Spark only reads device_id + temperature columns
# + skips row groups where predicates don't match
```

**Example 2 — Avro with confluent schema registry:**
```python
from confluent_kafka.avro import AvroProducer
from confluent_kafka import avro

schema_str = """
{
  "type": "record",
  "name": "SensorEvent",
  "fields": [
    {"name": "device_id",    "type": "string"},
    {"name": "temperature",  "type": "float"},
    {"name": "ts",           "type": "long",
     "logicalType": "timestamp-millis"}
  ]
}
"""
value_schema = avro.loads(schema_str)

producer = AvroProducer(
    {"bootstrap.servers": "broker:9092",
     "schema.registry.url": "http://registry:8081"},
    default_value_schema=value_schema
)
producer.produce(
    topic="sensors",
    value={"device_id": "X42", "temperature": 23.5,
           "ts": 1714608000000}
)
```

**Example 3 — Protobuf definition and usage:**
```protobuf
// sensor.proto
syntax = "proto3";
message SensorEvent {
  string device_id   = 1;
  float  temperature = 2;
  int64  ts          = 3;
}
```
```python
# Generated Python usage
import sensor_pb2

event = sensor_pb2.SensorEvent(
    device_id="X42",
    temperature=23.5,
    ts=1714608000000
)
# Serialize: 3 fields = ~20 bytes vs ~80 bytes JSON
serialized = event.SerializeToString()
# Deserialize
parsed = sensor_pb2.SensorEvent()
parsed.ParseFromString(serialized)
```

---

### ⚖️ Comparison Table

| Format | Layout | Schema | Best Query | Best For |
|---|---|---|---|---|
| **JSON** | Row, text | Per-record (keys) | Any (slow) | APIs, small data |
| **Avro** | Row, binary | File header / registry | Full-record scan | Kafka streams |
| **Parquet** | Columnar, binary | File footer | Column scan + analytics | Data lake, Spark |
| **ORC** | Columnar, binary | Stripe footer + indexes | Column + predicate | Hive, Hudi |
| **Protobuf** | Row, binary | .proto file | Full-record | gRPC, inter-service |

**How to choose:** Avro for Kafka event streaming where schema
evolution is needed. Parquet/ORC for data lake storage queried
by Spark/Hive. Protobuf for gRPC service contracts and storage
where language-neutral generated code is required.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Parquet is always better than JSON | For single-record lookups by primary key, Parquet is worse — reading a 128 MB row group to find one record is much slower than a direct key lookup |
| Avro and Parquet are interchangeable | Avro is row-oriented (good for streaming), Parquet is columnar (good for analytics) — they are complementary, not substitutes |
| Binary formats are write-once | Parquet files are append-immutable, but table formats (Delta Lake, Iceberg) layer ACID transactions on top of Parquet to enable updates and deletes |
| Compressing a JSON file makes it as good as Parquet | Compression helps with size but not with column pruning or predicate pushdown — you still parse 100% of the data for every query |
| Protobuf is only for gRPC | Protobuf is a general-purpose serialisation format used in databases (BigTable), Kafka, Android (Play Store), and many non-RPC storage contexts |

---

### 🚨 Failure Modes & Diagnosis

**Small Files Problem (Parquet)**

**Symptom:**
Spark job produces 50,000 Parquet files each 1 MB. Subsequent
reads are slow; S3 LIST calls are expensive; Spark task count
explodes to 50,000 tasks.

**Root Cause:**
Each micro-batch or partition wrote one small file. Parquet
metadata (footer) overhead and S3 API call overhead dominate
over actual data reading.

**Diagnostic Command / Tool:**
```bash
# Count and size files in S3 prefix
aws s3 ls s3://bucket/data/ --recursive | \
  awk '{sum+=$3; count++} END {
    print count" files, avg size: "sum/count" bytes"}'
```

**Fix:**
```python
# Compact before writing (Spark)
df.coalesce(100)  # reduce to 100 partitions / files
  .write.parquet("s3://bucket/data/")
# Or use Delta Lake OPTIMIZE command for existing tables
```

**Prevention:**
Target 128–256 MB per Parquet file. Use Delta Lake/Iceberg
`OPTIMIZE` command for ongoing compaction.

---

**Schema Evolution Break (Avro)**

**Symptom:**
A consumer raises `SchemaParseException` after a producer
deployed a schema change. Messages stop processing.

**Root Cause:**
Producer added a non-nullable field with no default value.
Old consumers (using previous schema version) cannot deserialise
new messages — backward compatibility broken.

**Diagnostic Command / Tool:**
```bash
# Check schema compatibility in Confluent Schema Registry
curl -X POST \
  http://registry:8081/compatibility/subjects/topic-value/versions/latest \
  -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  -d '{"schema": "{...new schema JSON...}"}'
# Response: {"is_compatible": false} ← problem!
```

**Fix:**
Only add fields with defaults:
```json
{
  "name": "new_field",
  "type": ["null", "string"],
  "default": null  ← makes it backward compatible
}
```

**Prevention:**
Set Schema Registry compatibility level to `BACKWARD` for all
consumer topics. CI pipeline checks compatibility before merge.

---

**Parquet Predicate Pushdown Not Working**

**Symptom:**
Spark query with `WHERE date = '2024-01-01'` reads all data
instead of just one day's partition. Query slower than expected.

**Root Cause:**
Data is not partitioned by date. Row group statistics for date
column span the full range — no row groups can be skipped.

**Diagnostic Command / Tool:**
```python
# Check how many files and bytes Spark plans to read
df = spark.read.parquet("s3://bucket/events/")
df.filter("event_date = '2024-01-01'").explain(True)
# Look for PartitionFilters vs DataFilters in plan
# PartitionFilters = partition pruning (fastest)
# DataFilters on parquet = row group statistics
```

**Fix:**
Re-partition data by date on write:
```python
df.write.partitionBy("event_date").parquet("s3://bucket/events/")
```

**Prevention:**
Always partition Parquet tables by the most common filter
column (usually date/timestamp). For point queries, use an
additional sort by the point-query key within partitions.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Data Formats (JSON, XML, YAML, CSV)` — binary formats are
  the next evolution; understanding text formats reveals why
  binary formats were needed
- `Columnar vs Row Storage` — the architectural split between
  Avro (row) and Parquet/ORC (columnar) maps directly to
  this fundamental concept
- `Data Types` — binary formats encode types precisely;
  understanding types explains the encoding choices

**Builds On This (learn these next):**
- `Avro` — deep dive into Avro's schema model and evolution
  semantics
- `Parquet` — deep dive into Parquet's columnar layout,
  encodings, and compression tiers
- `Schema Registry` — the governance layer that manages
  Avro schemas across producers and consumers

**Alternatives / Comparisons:**
- `Data Compression` — compression (gzip, Snappy, Zstd) is
  applied inside binary formats but is also a separate concern
- `Serialization Formats` — the higher-level programming
  concept of which these are specific implementations
- `ORC` — Hive's alternative to Parquet with different
  trade-offs (stripe-level indexes, better Hive integration)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Compact binary data encodings that store  │
│              │ schema separately from records            │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Text formats are 3–10× too large and      │
│ SOLVES       │ slow for billion-record data pipelines    │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Parquet = columnar (read 2 of 50 columns) │
│              │ Avro = row (read full records in streams) │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Avro: Kafka. Parquet/ORC: data lake OLAP. │
│              │ Protobuf: gRPC / inter-service storage    │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Small data (<1 GB), need human-readable   │
│              │ debugging, or single-record random access  │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Size + speed vs human readability         │
│              │ + tooling complexity                      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "JSON is a memo; Parquet is a compressed   │
│              │  filing system sorted by topic."          │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Avro → Parquet → Schema Registry          │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A data platform team must choose between Parquet and Avro
as the storage format for a new data lake table that is:
(a) appended to every 5 minutes by a Kafka consumer writing
10,000 rows per batch, and (b) queried 30 times/day by Spark
jobs that read 3 of 40 columns over 90-day windows. Explain
exactly how the write access pattern and read access pattern
create conflicting format requirements, and design an architecture
that satisfies both using both formats in different layers.

**Q2.** A team migrates 500 TB of JSON log data in S3 to Parquet.
After migration, S3 storage costs rose by 20% instead of falling.
List the three most likely causes, describe the diagnostic
command for each, and explain the correct remediation.

