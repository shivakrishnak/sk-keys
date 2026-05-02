---
layout: default
title: "Data Types (Primitive, Complex, Semi-Structured)"
parent: "Data Fundamentals"
nav_order: 496
permalink: /data-fundamentals/data-types/
number: "496"
category: Data Fundamentals
difficulty: ★☆☆
depends_on: ""
used_by: "Structured vs Unstructured Data, Data Formats, Columnar vs Row Storage"
tags: #data, #data-types, #primitive, #complex, #semi-structured, #fundamentals
---

# 496 — Data Types (Primitive, Complex, Semi-Structured)

`#data` `#data-types` `#primitive` `#complex` `#semi-structured` `#fundamentals`

⚡ TL;DR — **Data types** classify values by structure: **primitive** (integers, strings, booleans), **complex/structured** (rows with schema), and **semi-structured** (self-describing, flexible schema like JSON/XML). Understanding data types drives storage format, query strategy, and pipeline design.

| #496            | Category: Data Fundamentals                                            | Difficulty: ★☆☆ |
| :-------------- | :--------------------------------------------------------------------- | :-------------- |
| **Depends on:** | —                                                                      |                 |
| **Used by:**    | Structured vs Unstructured Data, Data Formats, Columnar vs Row Storage |                 |

---

### 📘 Textbook Definition

**Primitive data types**: atomic, indivisible values — integers (`INT`, `BIGINT`), floating-point (`FLOAT`, `DOUBLE`), booleans (`BOOLEAN`), strings (`VARCHAR`, `TEXT`), dates/times (`DATE`, `TIMESTAMP`). Stored directly; fixed or bounded size. Used as the building blocks of higher-level structures.

**Complex / Structured data types**: composite values with a defined schema — records/rows, arrays, maps (key-value), structs/objects. Columns in a relational table are composed of primitive types. Formats like Parquet and ORC support nested complex types (arrays, maps, nested records).

**Semi-structured data types**: data that carries its own schema inline (self-describing) but does not require a fixed, pre-declared schema. Examples: JSON, XML, YAML, Avro (with embedded schema). Fields may vary record-to-record. Schema enforcement is optional and flexible. Contrast with structured (schema-on-write, rigid) and unstructured (no schema, e.g., images, audio, free text).

---

### 🟢 Simple Definition (Easy)

Three kinds of data:

- **Primitive**: single values — a number `42`, a string `"Alice"`, a date `2024-01-01`. The atoms of data.
- **Structured (complex)**: a table with fixed columns — every row has the same fields. Like a spreadsheet with headers.
- **Semi-structured**: a JSON document — it has field names, but different documents can have different fields. Self-describing, flexible.

Everything in data engineering is built from these three building blocks.

---

### 🔵 Simple Definition (Elaborated)

In data systems, the type of data dictates how you store it, query it, and process it:

- **Primitive types**: stored compactly (4 bytes for INT, 8 bytes for BIGINT). SQL databases use primitive types as column types. Columnar formats compress them very efficiently (dictionary encoding for low-cardinality strings, delta encoding for timestamps).

- **Complex/structured types**: relational tables, Parquet rows, Avro records. Schema is pre-declared (schema-on-write). All records conform to the same structure. Enables SQL queries, column pruning, predicate pushdown.

- **Semi-structured**: JSON/XML/YAML in data lakes, NoSQL documents (MongoDB, DynamoDB). Schema is embedded with the data (schema-on-read). Flexible — new fields can appear without schema migration. Trade-off: query complexity increases; storage is less efficient than columnar formats.

---

### 🔩 First Principles Explanation

```
DATA TYPE CLASSIFICATION:

  PRIMITIVE (atoms):
  ┌──────────────┬───────────────────────────────────────────┐
  │ Category     │ Examples                                  │
  ├──────────────┼───────────────────────────────────────────┤
  │ Numeric      │ INT (4B), BIGINT (8B), FLOAT, DOUBLE,    │
  │              │ DECIMAL(p,s)                              │
  │ Boolean      │ BOOLEAN (1 bit / 1 byte)                 │
  │ String       │ VARCHAR(n), TEXT, CHAR(n)                │
  │ Date/Time    │ DATE, TIME, TIMESTAMP, INTERVAL          │
  │ Binary       │ BLOB, BYTES, VARBINARY                   │
  └──────────────┴───────────────────────────────────────────┘

  COMPLEX / STRUCTURED (composed from primitives):
  ┌──────────────┬───────────────────────────────────────────┐
  │ Struct/Row   │ { name: STRING, age: INT, city: STRING } │
  │ Array        │ [1, 2, 3, 4]                              │
  │ Map/Dict     │ { "US": 100, "EU": 200 }                 │
  │ Nested       │ { order: { id: INT, items: ARRAY<STRUCT>}}│
  └──────────────┴───────────────────────────────────────────┘

  Storage formats that support complex types:
  - Parquet: nested schema (repeated fields, map, list)
  - Avro: records, arrays, maps, unions
  - ORC: struct, list, map, union

  SEMI-STRUCTURED (self-describing, no fixed schema):
  ┌──────────────┬───────────────────────────────────────────┐
  │ Format       │ Characteristics                          │
  ├──────────────┼───────────────────────────────────────────┤
  │ JSON         │ Key-value + nested objects/arrays        │
  │              │ Schema-on-read; most common in REST APIs │
  │ XML          │ Tag-based hierarchy; verbose; XPath/XSLT │
  │ YAML         │ Human-readable; config files, CI/CD      │
  │ Avro         │ Binary + embedded JSON schema; Kafka     │
  │ Parquet/ORC  │ Binary columnar; NOT semi-structured     │
  └──────────────┴───────────────────────────────────────────┘

DATA LAKE PATTERN: schema-on-read

  Raw zone: JSON files (semi-structured, flexible ingestion)
      │
      ▼ ETL / transformation
  Curated zone: Parquet files (structured, columnar, compressed)
      │
      ▼ SQL query engine (Athena, Presto, Spark SQL)
  Analytics: query typed, compressed, column-prunable data

QUERY IMPACT:

  Primitive types: direct comparison, index, range scan
  Complex/structured: column pruning, predicate pushdown possible
  Semi-structured (JSON): must parse at query time (costly)
                          or extract to columns first (ETL)

  SELECT data:name FROM my_table            -- structured: fast
  SELECT json_extract(raw, '$.name') ...    -- semi-structured: slow (parse)
  → Solution: parse JSON at ingest time, write to Parquet
```

---

### ❓ Why Does This Exist (Why Before What)

Different data sources produce different types of data. Event streams from web apps → JSON (semi-structured, flexible schema — new fields added as features ship). Financial transactions → structured tables (rigid schema, ACID transactions needed). ML feature stores → dense numeric arrays (optimized for vector operations). Understanding data types tells you: which storage format to use, how to query efficiently, where schema enforcement is needed, and what transformation is required to move between zones in a data lake.

---

### 🧠 Mental Model / Analogy

> **Three kinds of things in a library**: (1) **Cards** (primitives) — a single number on a library card (member ID, fine amount). (2) **Catalog entries** (structured) — every book has the same fields: title, author, ISBN, shelf number. (3) **Sticky notes inside books** (semi-structured) — each note has content and a name, but format varies wildly — some have dates, some have doodles, some are blank.

"Cards" = primitive values
"Catalog entries" = structured records with fixed schema
"Sticky notes" = semi-structured data, self-describing but variable format
"Catalog is fast to search" = structured data enables fast SQL queries
"Reading sticky notes requires opening each book" = semi-structured requires parsing at query time

---

### ⚙️ How It Works (Mechanism)

```
SCHEMA-ON-WRITE (structured):
  Define schema → enforce at write time → reject non-conforming data
  PostgreSQL: CREATE TABLE orders (id BIGINT, amount DECIMAL(10,2), ...)
  Parquet: schema declared in file header; all rows must conform

  ✅ Fast reads, column pushdown
  ❌ Schema migrations required for changes; rigid ingestion

SCHEMA-ON-READ (semi-structured):
  Accept any data → define interpretation at query time
  S3 JSON files: no pre-declared schema; Athena reads and parses at query
  MongoDB: any document structure stored; query must handle null fields

  ✅ Flexible ingestion; no migration needed
  ❌ Slower queries; errors surface at read time, not write time

HYBRID (Avro with schema registry):
  Schema embedded in file header (self-describing) + registered in schema registry
  Writer embeds schema → reader can decode without out-of-band schema
  Schema registry enforces backward/forward compatibility
  ✅ Best of both: flexible evolution + schema enforcement
```

---

### 🔄 How It Connects (Mini-Map)

```
Data enters a system
        │
        ▼
Data Types (Primitive, Complex, Semi-Structured) ◄── (you are here)
        │
        ├── Structured vs Unstructured Data: where each type falls
        ├── Semi-Structured Data: deeper dive into flexible schemas
        ├── Data Formats (JSON, XML, YAML, CSV): wire formats for each type
        ├── Columnar vs Row Storage: how primitive/complex types are stored
        └── Avro / Parquet / ORC: binary formats for structured data
```

---

### 💻 Code Example

```python
# Python / PySpark: handling all three data type categories

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, ArrayType
from pyspark.sql.functions import from_json, col

spark = SparkSession.builder.appName("DataTypes").getOrCreate()

# STRUCTURED: fixed schema DataFrame
schema = StructType([
    StructField("id", IntegerType(), False),        # primitive
    StructField("name", StringType(), False),       # primitive
    StructField("tags", ArrayType(StringType()), True),  # complex (array of primitives)
])
df_structured = spark.read.schema(schema).parquet("s3://bucket/orders/")

# SEMI-STRUCTURED: JSON column embedded in row
json_schema = StructType([
    StructField("event_type", StringType()),
    StructField("payload", StringType()),  # raw JSON stored as string
])
df_raw = spark.read.schema(json_schema).json("s3://bucket/raw-events/")

# Parse semi-structured JSON into structured columns (schema-on-read → schema-on-write)
payload_schema = StructType([
    StructField("user_id", StringType()),
    StructField("product_id", StringType()),
    StructField("amount", IntegerType()),
])
df_parsed = df_raw.withColumn("payload_parsed", from_json(col("payload"), payload_schema)) \
                  .select("event_type",
                          col("payload_parsed.user_id"),
                          col("payload_parsed.amount"))

# Write as structured Parquet (columnar, efficient, query-optimized)
df_parsed.write.mode("overwrite").parquet("s3://bucket/curated-events/")
```

---

### ⚠️ Common Misconceptions

| Misconception                                         | Reality                                                                                                                                                                                                           |
| ----------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Semi-structured data is the same as unstructured data | Semi-structured data has structure — it just carries its schema with it (self-describing). Unstructured data (images, audio, free text) has no queryable schema. JSON is semi-structured; a JPEG is unstructured. |
| Parquet and ORC are semi-structured formats           | Parquet/ORC are binary columnar formats for STRUCTURED data. They require a schema declared upfront. Contrast with JSON (semi-structured): no schema required, but less efficient.                                |
| Primitive types are always fast to query              | Cardinality and index support matter. A full-table scan of 1 billion VARCHAR rows is slow regardless of the type being "primitive."                                                                               |

---

### 🔥 Pitfalls in Production

```
ANTI-PATTERN: storing everything as JSON in a relational DB

  -- PostgreSQL: JSON column for "flexible" data
  CREATE TABLE events (
      id BIGINT,
      payload JSONB   -- tempting: "future-proof", "flexible"
  );

  SELECT payload->>'user_id', SUM((payload->>'amount')::INT)
  FROM events
  WHERE payload->>'event_type' = 'purchase';
  -- ❌ Full table scan; no column statistics; bloated storage
  -- ❌ Type errors at query time (amount may be missing/null in some records)
  -- ❌ Cannot partition by payload fields efficiently

  FIX: extract known fields at ingest time:
  CREATE TABLE events (
      id BIGINT,
      event_type VARCHAR(50),
      user_id VARCHAR(36),
      amount INT,
      extra_data JSONB   -- only truly variable/rare fields in JSON
  );
  CREATE INDEX ON events(event_type);
  CREATE INDEX ON events(user_id);
  -- ✅ Fast indexed queries on known fields
  -- ✅ Type-safe: amount is always INT or NULL (detected early)
  -- ✅ Column statistics available for query planner
```

---

### 🔗 Related Keywords

- `Structured vs Unstructured Data` — how primitive/complex/semi-structured maps to the structured/unstructured spectrum
- `Semi-Structured Data` — deep-dive on JSON/XML/Avro flexible schemas
- `Data Formats (JSON, XML, YAML, CSV)` — wire formats for each data type category
- `Columnar vs Row Storage` — how data type choice impacts storage efficiency
- `Parquet` — binary columnar format for structured (complex + primitive) data

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ TYPE          │ Examples          │ Schema     │ Format  │
├───────────────┼───────────────────┼────────────┼─────────┤
│ Primitive     │ INT, STRING, DATE │ N/A        │ Any     │
│ Structured    │ Row, Table, Parq  │ Pre-defined│ Parquet │
│ Semi-struct   │ JSON, XML, Avro   │ Self-desc  │ JSON/Av │
│ Unstructured  │ Image, audio, txt │ None       │ Binary  │
├───────────────┴───────────────────┴────────────┴─────────┤
│ Rule: Convert semi-structured → structured at ingest    │
│       Store structured as Parquet/ORC for analytics     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A data lake has three zones: raw (JSON), refined (Parquet), curated (Parquet, partitioned). JSON files land in raw every minute. Your ETL job parses JSON into structured Parquet and writes to refined. What happens when the upstream service adds a new field to the JSON payload? What happens when it removes a field? How do you design the ETL to handle schema evolution in the semi-structured source without breaking the structured target?

**Q2.** PostgreSQL's `JSONB` type lets you store semi-structured data in a relational table, with partial GIN indexing on specific JSON keys. MongoDB stores all documents as BSON (binary JSON) with no schema enforcement. Compare the trade-offs: when would you choose `JSONB` in PostgreSQL vs. a dedicated document database like MongoDB? What's the difference in how each handles schema evolution at scale?
