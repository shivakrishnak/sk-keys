---
layout: default
title: "Binary Formats (Avro, Parquet, ORC, Protobuf)"
parent: "Data Fundamentals"
nav_order: 500
permalink: /data-fundamentals/binary-formats/
number: "500"
category: Data Fundamentals
difficulty: ★★☆
depends_on: "Data Formats (JSON, XML, YAML, CSV), Semi-Structured Data, Columnar vs Row Storage"
used_by: "Avro, Parquet, ORC, Delta Lake, Kafka pipelines, Spark analytics"
tags: #data, #avro, #parquet, #orc, #protobuf, #binary-formats, #serialization, #columnar
---

# 500 — Binary Formats (Avro, Parquet, ORC, Protobuf)

`#data` `#avro` `#parquet` `#orc` `#protobuf` `#binary-formats` `#serialization` `#columnar`

⚡ TL;DR — **Binary formats** replace text (JSON/CSV) for performance at scale. **Parquet/ORC** are columnar → analytics. **Avro** is row-based → streaming/serialization. **Protobuf** is cross-language RPC/service serialization. The rule: use Avro on Kafka, use Parquet/ORC in data lake analytics layers.

| #500            | Category: Data Fundamentals                                                        | Difficulty: ★★☆ |
| :-------------- | :--------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Data Formats (JSON, XML, YAML, CSV), Semi-Structured Data, Columnar vs Row Storage |                 |
| **Used by:**    | Avro, Parquet, ORC, Delta Lake, Kafka pipelines, Spark analytics                   |                 |

---

### 📘 Textbook Definition

**Avro**: Apache Avro — a row-based binary serialization format. Schema is defined in JSON and embedded in the file header or registered in a Schema Registry. Supports schema evolution (backward/forward compatibility). Primary use: Apache Kafka event streaming, Hadoop data exchange. Compact binary encoding; no field names in each record (schema handles it).

**Parquet**: Apache Parquet — an open-source columnar storage format. Data is stored column-by-column rather than row-by-row. Each column is compressed independently using encoding schemes optimized per data type (run-length encoding, dictionary encoding, delta encoding). Supports nested schemas (maps, arrays, structs). Primary use: data lake analytics (Spark, Presto/Trino, Athena, BigQuery external tables), batch processing.

**ORC (Optimized Row Columnar)**: Apache ORC — a columnar storage format optimized for Hive workloads. Stores column statistics (min/max/count/bloom filters) per stripe (row group). Predicate pushdown reads only relevant stripes. Primary use: Hive-based analytics, AWS EMR, enterprise data warehouses on Hadoop.

**Protobuf (Protocol Buffers)**: Google's binary serialization format. Schema defined in `.proto` files; code generated for multiple languages. Extremely compact and fast. Used in gRPC (Google's RPC framework). Strong versioning (field numbers). Primary use: microservice-to-microservice communication, gRPC APIs, mobile app backends.

---

### 🟢 Simple Definition (Easy)

Text formats (JSON, CSV) store data as readable characters — humans can open them in Notepad. Binary formats store data as bytes — unreadable to humans, but:

- Much smaller (2-10x compression)
- Much faster to read (computer reads bytes, not ASCII characters)
- Type-safe (no ambiguity between string "123" and integer 123)

**Parquet**: a spreadsheet stored column-by-column. Sum of one column? Read only that column — skip the rest.
**Avro**: a row-by-row serialization format. Great for sending individual records over a network (Kafka messages).
**Protobuf**: Google's compact format for service calls. `.proto` file = contract between services.

---

### 🔵 Simple Definition (Elaborated)

The choice between binary formats depends on **access pattern**:

- **Parquet/ORC** (columnar): analytics queries read a few columns from millions of rows → columnar is 10-100x faster than row-based (only read the columns you need, skip the rest).

- **Avro** (row-based): streaming events — one record at a time, all fields needed → row-based is optimal. Embedded schema enables schema evolution in Kafka topics.

- **Protobuf** (row-based, generated code): synchronous microservice calls — compact, fast, strongly typed, generated client/server code → ideal for gRPC. Not designed for analytics.

The standard data engineering stack: **Kafka + Avro** for transport → **Spark** for processing → **Parquet** for storage → **Athena/Trino** for SQL analytics.

---

### 🔩 First Principles Explanation

```
WHY COLUMNAR WINS FOR ANALYTICS:

  Row-based (JSON, Avro, CSV):
  Row 1: [id=1001, name="Alice",  amount=149.99, city="Seattle"]
  Row 2: [id=1002, name="Bob",    amount=89.50,  city="Austin" ]
  Row 3: [id=1003, name="Charlie",amount=299.00, city="NYC"   ]

  Query: SELECT SUM(amount) FROM orders WHERE city = 'Seattle'
  Must read ALL bytes of ALL rows to get amount and city

  Columnar (Parquet):
  Column "id":     [1001, 1002, 1003, ...]
  Column "name":   ["Alice", "Bob", "Charlie", ...]
  Column "amount": [149.99, 89.50, 299.00, ...]
  Column "city":   ["Seattle", "Austin", "NYC", ...]

  Query: SELECT SUM(amount) FROM orders WHERE city = 'Seattle'
  Step 1: Read "city" column → find rows where city="Seattle" → row indexes {0}
  Step 2: Read only those row indexes from "amount" column → 149.99
  Step 3: SUM(149.99) = 149.99

  Reads: 2 columns × (relevant rows only) = tiny fraction of file
  Skips: "id" and "name" columns entirely

PARQUET FILE STRUCTURE:

  ┌─────────────────────────────────────────────────────┐
  │ Magic bytes: PAR1                                   │
  │ Row Group 1 (e.g., rows 0-128,000):                 │
  │   Column Chunk: "id" (compressed: delta encoding)  │
  │   Column Chunk: "name" (compressed: dict encoding) │
  │   Column Chunk: "amount" (compressed: byte-stream) │
  │   Column Chunk: "city" (compressed: dict encoding) │
  │ Row Group 2 (rows 128,001-256,000):                 │
  │   ... (same structure)                             │
  │ File Footer (metadata):                             │
  │   Row group statistics: min/max/null_count per col  │
  │   Schema definition                                 │
  │   Row group offsets (byte positions in file)        │
  │ Magic bytes: PAR1                                   │
  └─────────────────────────────────────────────────────┘

  PREDICATE PUSHDOWN:
  WHERE amount > 1000
  → Read footer: row group 3 has max(amount)=500 → SKIP entire row group 3
  → Row group 1: max(amount)=2000 → read (may contain values > 1000)

  COLUMN PRUNING:
  SELECT name, amount FROM orders (not id, city)
  → Read only "name" and "amount" column chunks
  → Skip "id" and "city" column chunks entirely

AVRO FILE STRUCTURE:

  ┌──────────────────────────────────────────────┐
  │ Header:                                      │
  │   Magic bytes: Obj\x01                       │
  │   metadata: schema (JSON, encoded)           │
  │   sync_marker: 16 random bytes               │
  │ Data Block 1:                                │
  │   object_count: 1000                         │
  │   byte_count: 4521                           │
  │   [1000 binary-encoded Avro records]         │
  │   sync_marker (boundary marker)              │
  │ Data Block 2:                                │
  │   ... (same structure)                       │
  └──────────────────────────────────────────────┘

  In Kafka: schema NOT in message (too expensive to repeat per message)
  Instead: [0x00][schema_id: 4 bytes][avro binary payload]
  Consumer: reads schema_id → fetches from Schema Registry (cached)

PROTOBUF .proto DEFINITION:

  syntax = "proto3";

  message Order {
    int64 order_id = 1;        // field number 1 (wire format key)
    string customer_id = 2;    // field number 2
    double amount = 3;         // field number 3
    repeated OrderItem items = 4;  // array
    OrderStatus status = 5;

    enum OrderStatus {
      PENDING = 0;
      COMPLETED = 1;
      CANCELLED = 2;
    }

    message OrderItem {
      string product_id = 1;
      int32 quantity = 2;
      double price = 3;
    }
  }

  Wire format: each field encoded as (field_number, type, value)
  → If field 6 added in v2, v1 reader: ignores unknown field 6 (forward compat)
  → If field 3 (amount) removed in v3, v1 reader: field missing → default value

COMPRESSION COMPARISON (100M order records):

  Format    │ Size    │ Compression │ Read time (Spark, 1 col)
  ──────────┼─────────┼─────────────┼──────────────────────────
  CSV       │ 8 GB    │ None        │ 120s (read all 8GB)
  JSON      │ 16 GB   │ None        │ 240s (parse + 16GB read)
  Avro      │ 2 GB    │ snappy      │ 30s (row-based, all cols)
  Parquet   │ 1 GB    │ snappy      │ 3s (1 col = ~50MB)
  ORC       │ 0.8 GB  │ zlib        │ 2.5s (1 col + bloom filter)

  Parquet/ORC: 40-50x smaller than JSON + 80x faster for column queries
```

---

### ❓ Why Does This Exist (Why Before What)

JSON at scale becomes the bottleneck: 1 TB of JSON events — every analytics query must scan all 1 TB, parse each JSON string, extract fields. With Parquet, the same 1 TB → 100 GB of Parquet (10x smaller) → query scans 5 GB (only the needed columns) → 200x less I/O. At petabyte scale, the difference is the boundary between "can afford to run" and "too expensive to run." Binary formats exist because humans don't read production analytics data directly — machines do, and machines are much faster with binary.

---

### 🧠 Mental Model / Analogy

> **Filing cabinet organizations**: **CSV/JSON** is a filing cabinet where each drawer is a folder containing all information about one person — name, address, salary, department in one document. To find everyone's salary, open every drawer, read the whole document, find the salary field. **Parquet/ORC** reorganizes the same cabinet: one drawer for all names, one drawer for all salaries, one drawer for all departments. To find everyone's salary: open only the salary drawer. Skip every other drawer. **Avro** is the mailroom — each package (record) has everything inside it for shipping, optimized for sending one complete record at a time. **Protobuf** is a standardized shipping label format — compact, versioned, generated by machines for machines.

---

### ⚙️ How It Works (Mechanism)

```
ENCODING OPTIMIZATIONS IN PARQUET:

  Dictionary Encoding (low-cardinality strings, e.g., "city"):
  City column: ["Seattle", "NYC", "Seattle", "Austin", "Seattle", "NYC", ...]

  Dictionary: {0:"Seattle", 1:"NYC", 2:"Austin"}
  Encoded:    [0, 1, 0, 2, 0, 1, ...]  (ints instead of strings)

  "Seattle" (7 bytes) → 0 (1 byte) per occurrence
  → ~7x compression for strings; faster equality comparisons (int vs string)

  Run-Length Encoding (repeated values):
  Status column: [1,1,1,1,1,1,1,1,2,2,2]  (8 COMPLETED, 3 CANCELLED)
  RLE: [(1,8), (2,3)]  → 2 values instead of 11

  Delta Encoding (monotonically increasing values, e.g., timestamps):
  Timestamps: [1705000000, 1705000060, 1705000120, 1705000180]
  Deltas:     [1705000000, 60, 60, 60]  → store base + small deltas
  → Small deltas compress much better than full timestamps
```

---

### 🔄 How It Connects (Mini-Map)

```
Text formats are too slow/large at scale
        │
        ▼
Binary Formats (Avro, Parquet, ORC, Protobuf) ◄── (you are here)
        │
        ├── Avro: row-based, schema evolution, Kafka streaming
        ├── Parquet: columnar, analytics, data lake storage
        ├── ORC: columnar, Hive-optimized, bloom filters
        ├── Protobuf: compact, versioned, gRPC services
        ├── Columnar vs Row Storage: the architectural principle
        └── Delta Lake: transactional layer on top of Parquet
```

---

### 💻 Code Example

```python
# Python: write and read Parquet with PyArrow

import pyarrow as pa
import pyarrow.parquet as pq

# Create a table with typed schema
schema = pa.schema([
    pa.field("order_id", pa.int64()),
    pa.field("customer_id", pa.string()),
    pa.field("amount", pa.float64()),
    pa.field("city", pa.string()),
    pa.field("status", pa.string()),
])

data = pa.table({
    "order_id": [1001, 1002, 1003, 1004, 1005],
    "customer_id": ["C001", "C002", "C001", "C003", "C002"],
    "amount": [149.99, 89.50, 299.00, 49.99, 199.00],
    "city": ["Seattle", "NYC", "Seattle", "Austin", "NYC"],
    "status": ["COMPLETED", "COMPLETED", "PENDING", "COMPLETED", "CANCELLED"],
}, schema=schema)

# Write Parquet with snappy compression
pq.write_table(data, "orders.parquet", compression="snappy")

# Read with column pruning + predicate pushdown
result = pq.read_table(
    "orders.parquet",
    columns=["customer_id", "amount"],          # column pruning
    filters=[("city", "=", "Seattle"),           # predicate pushdown
             ("status", "=", "COMPLETED")],
)
print(result.to_pandas())
# customer_id  amount
# C001         149.99

# Avro write with Python (fastavro)
import fastavro
from io import BytesIO

avro_schema = {
    "type": "record",
    "name": "Order",
    "fields": [
        {"name": "order_id", "type": "long"},
        {"name": "amount", "type": "double"},
        {"name": "currency", "type": ["string", "null"], "default": "USD"},  # union: string or null
    ]
}

records = [
    {"order_id": 1001, "amount": 149.99, "currency": "USD"},
    {"order_id": 1002, "amount": 89.50, "currency": None},  # null currency
]

buffer = BytesIO()
fastavro.writer(buffer, fastavro.parse_schema(avro_schema), records)

# Read back:
buffer.seek(0)
for record in fastavro.reader(buffer):
    print(record)
```

---

### ⚠️ Common Misconceptions

| Misconception                              | Reality                                                                                                                                                                                                                                                                                                             |
| ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Parquet is always better than Avro         | Access pattern matters. Avro is better for row-by-row streaming (Kafka: process one message at a time). Parquet is better for columnar analytics (Spark: aggregate over millions of rows, few columns). Avro is better for schema evolution in streaming; Parquet supports evolution too but is designed for batch. |
| Binary formats are unreadable/undebuggable | Tools exist: `parquet-tools`, `avro-tools`, `protoc --decode`. Spark `df.show()` reads Parquet perfectly. Avro records are readable with fastavro CLI. The binary nature is not an operational problem — it just means you need the right tool.                                                                     |
| ORC and Parquet are interchangeable        | Both are columnar, but: ORC has built-in ACID support (used in Hive/Iceberg ORC tables); Parquet has broader ecosystem support (Spark, Presto, Athena, BigQuery, Pandas, Arrow). ORC is often slightly better compressed; Parquet has better tooling. Default choice for new projects: Parquet.                     |

---

### 🔥 Pitfalls in Production

```
PITFALL: writing many small Parquet files (the "small files problem")

  # Spark default: writes one file per partition
  df.repartition(1000).write.parquet("s3://bucket/orders/")
  # Result: 1000 files × 10KB each = 10MB total data
  # But: each S3 LIST + OPEN has ~50ms overhead
  # Reading 1000 files: 50s overhead before first byte read
  # Athena: charges per file scan; 1000 small files → high cost

  # RULE: target 128MB–1GB per Parquet file
  df.coalesce(10).write.parquet(...)   # combine to ~10 files
  # or use Delta Lake: OPTIMIZE command merges small files automatically

PITFALL: Parquet schema mismatch on append

  # Week 1: write Parquet with schema {id: int64, amount: float64}
  # Week 4: upstream source changes amount to Decimal(10,2)
  # Spark tries to append new Parquet (Decimal) to old Parquet (float64)
  # → schema mismatch → job fails

  # FIX: use Delta Lake / Iceberg → schema evolution with ALTER TABLE
  # or: explicit schema casting before write:
  df = df.withColumn("amount", df["amount"].cast("double"))
```

---

### 🔗 Related Keywords

- `Avro` — deep dive: schema evolution, schema registry, Kafka integration
- `Parquet` — deep dive: row groups, column chunks, nested schemas, Delta Lake
- `ORC` — deep dive: Hive integration, ACID, bloom filters
- `Columnar vs Row Storage` — the foundational principle behind Parquet/ORC
- `Delta Lake` — transactional, ACID-compliant layer on top of Parquet

---

### 📌 Quick Reference Card

```
┌────────────┬──────────────┬────────────────┬──────────────────┐
│            │ Parquet      │ Avro           │ Protobuf         │
├────────────┼──────────────┼────────────────┼──────────────────┤
│ Layout     │ Columnar     │ Row-based      │ Row-based        │
│ Use case   │ Analytics    │ Kafka/streaming│ gRPC/services    │
│ Schema     │ File footer  │ Header/Registry│ .proto files     │
│ Evolution  │ Add columns  │ Backward/fwd   │ Field numbers    │
│ Ecosystem  │ Spark/Athena │ Kafka/Hadoop   │ gRPC/microsvcs   │
│ Compression│ Snappy/zstd  │ Deflate/snappy │ Built-in         │
├────────────┴──────────────┴────────────────┴──────────────────┤
│ Rule: Avro on Kafka → Spark reads → write Parquet → SQL query │
└──────────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Apache Iceberg and Delta Lake both use Parquet as the underlying file format but add a metadata/transaction layer on top. What problem does this solve that plain Parquet cannot? Specifically: how do they handle concurrent writes, schema evolution, and time-travel queries? What would break if you tried to implement these features with plain Parquet files?

**Q2.** At Uber, the Data Platform team migrated from JSON Kafka messages to Avro + Schema Registry. What are the specific failure modes that JSON caused that motivated the migration? Enumerate at least three concrete scenarios where JSON in Kafka causes operational problems and explain how Avro + Schema Registry solves each one.
