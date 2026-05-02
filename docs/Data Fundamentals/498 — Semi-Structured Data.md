---
layout: default
title: "Semi-Structured Data"
parent: "Data Fundamentals"
nav_order: 498
permalink: /data-fundamentals/semi-structured-data/
number: "0498"
category: Data Fundamentals
difficulty: ★☆☆
depends_on: Structured vs Unstructured Data, Data Types, Data Formats
used_by: Schema Registry, Schema Evolution, Data Catalog, ETL vs ELT
related: Data Formats (JSON, XML, YAML, CSV), Structured vs Unstructured Data, Serialization Formats
tags:
  - dataengineering
  - foundational
  - mental-model
  - database
---

# 498 — Semi-Structured Data

⚡ TL;DR — Semi-structured data carries its own schema embedded inside the data itself — like JSON — giving flexibility without total chaos.

| #498 | Category: Data Fundamentals | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Structured vs Unstructured Data, Data Types, Data Formats | |
| **Used by:** | Schema Registry, Schema Evolution, Data Catalog, ETL vs ELT | |
| **Related:** | Data Formats (JSON, XML, YAML, CSV), Structured vs Unstructured Data, Serialization Formats | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You are building an e-commerce platform. Each product has a core
set of attributes: ID, name, price. But a T-shirt also has size
and colour; a laptop has RAM and CPU; a book has ISBN and author.
In a strictly structured relational table, you either add 200
nullable columns (one per attribute per product type) or create
dozens of type-specific tables — and every new product type
requires a schema migration. Both approaches become unmanageable
at hundreds of product categories.

**THE BREAKING POINT:**
Schema migrations in production relational databases are expensive,
risky, and slow. The business needs to add a new product category
in hours; the DBA says the migration will take two weeks. Every
new attribute requires a developer, a review cycle, and a
deployment. The schema becomes the bottleneck for business velocity.

**THE INVENTION MOMENT:**
This is exactly why semi-structured data formats were embraced.
JSON, XML, and YAML allow each record to carry its own attribute
set. The product record carries exactly the fields it needs — no
null padding, no schema migration. The structure is in the data;
the storage layer just persists bytes.

---

### 📘 Textbook Definition

**Semi-structured data** is data that does not conform to a formal
relational or fixed schema, but nonetheless contains structural
elements — such as tags, markers, or key-value pairs — that
describe and organise the data within the content itself.
Semi-structured formats include JSON, XML, YAML, and Avro (with
schema evolution). Each record may have a different set of fields,
and fields may be nested, repeated, or absent. Queries require
traversing the embedded structural markers rather than relying on
a pre-defined column offset.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Semi-structured data is self-describing — it carries labels for
its own fields inside the data.

**One analogy:**

> A completed form (structured) vs a labelled box of belongings
> (semi-structured). The form forces every person to fill the same
> fields. The labelled box lets each person use whatever containers
> fit their stuff — each container is labelled, but the set of
> containers varies per person.

**One insight:**
The critical insight is "self-describing." A relational row is
meaningless without its schema DDL. A JSON object carries its own
field names — parse it without any external schema and you can
still read it. This portability is both the power and the
performance challenge of semi-structured data.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Each record in semi-structured data is self-describing:
   field names (keys) are embedded alongside values.
2. Different records in the same collection can have different
   fields — no universal schema enforced at the storage level.
3. Nesting is native: a field's value can itself be a structure,
   an array, or a primitive.

**DERIVED DESIGN:**
Given invariant 1, storage does not need a schema registry to
interpret a record. This enables schema-on-read: the consumer
decides what fields to use at query time. It also enables easy
versioning — producers add new fields without breaking consumers
that ignore unknown fields (forward compatibility).

Given invariant 2, queries cannot use fixed-offset addressing.
A query engine must parse each record to locate a field. This
makes full-table scans expensive. To recover performance, databases
like PostgreSQL offer GIN indexes on `jsonb` columns that index
key paths.

Given invariant 3, nested structures can model real-world
complexity (orders with line items with products with attributes)
in a single document — eliminating joins at the cost of data
duplication.

**THE TRADE-OFFS:**
**Gain:** Schema flexibility, self-description, easy versioning,
natural fit for hierarchical / polymorphic data.
**Cost:** No static type guarantees, query performance requires
explicit indexing, no referential integrity enforcement, storage
overhead from repeated key names.

---

### 🧪 Thought Experiment

**SETUP:**
You build a product catalog for 500 product categories.
Option A: one relational table with nullable columns.
Option B: one `jsonb` column storing semi-structured product data.

**WHAT HAPPENS WITH RIGID STRUCTURE (Option A):**
Month 1: you have 50 categories. The table has 120 columns; 70%
are NULL for any given row. A new category (drone accessories)
needs 8 new columns. DBA runs `ALTER TABLE ADD COLUMN` on a
500 million row table. It takes 4 hours with a table lock. Your
catalog goes read-only. The business is furious.

**WHAT HAPPENS WITH SEMI-STRUCTURED (Option B):**
Month 1: you launch. Month 6: drone accessories. The dev adds the
new category JSON template in 10 minutes, deploys, and the new
products appear immediately. No migration. The `jsonb` column
stores whatever the category template defines. A GIN index on
`(data->>'category')` keeps category lookups fast.

**THE INSIGHT:**
Semi-structured data trades query-time flexibility against
write-time schema discipline. The savings are front-loaded (no
migration); the cost is back-loaded (index maintenance, query
complexity). Both costs are real — the question is which cost
your system can better absorb.

---

### 🧠 Mental Model / Analogy

> Think of a library where every book has its own custom index
> at the back, rather than a central card catalogue. Each book
> decides what terms to index and how. You can search within
> any single book quickly using its index. But to answer "which
> books mention quantum entanglement?" you need to check every
> book's index independently — which is why you also need a
> library-wide index (like a search engine or GIN index).

- "Individual book index" → embedded JSON keys
- "Book content" → field values (potentially nested)
- "Library catalogue" → external index (search engine / GIN)
- "Books with different index structures" → heterogeneous records
- "Searching without the library catalogue" → full table scan

**Where this analogy breaks down:** In a real library, the search
engine (catalogue) is built by librarians once. In a database,
the GIN index is maintained automatically on every write — at a
write performance cost proportional to index complexity.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Semi-structured data is like a flexible form where each record
can have different fields. A JSON file for a T-shirt product has
`size` and `colour`; a JSON file for a laptop has `RAM` and `CPU`.
Both are valid records in the same system — no fixed template
forces both to have the same fields.

**Level 2 — How to use it (junior developer):**
Use JSON/YAML for configuration files, API responses, and event
streams. In databases, use `jsonb` (PostgreSQL) or `document`
(MongoDB) types when the schema varies per record. Always add
an index on the JSON path you filter by most often. Validate
JSON at the application boundary with a schema library (Pydantic,
JSON Schema, Joi) even if the DB allows anything.

**Level 3 — How it works (mid-level engineer):**
PostgreSQL `jsonb` stores JSON as a binary decomposed format (not
plain text), enabling GIN indexes on key paths. A GIN index on
`data jsonb_path_ops` allows efficient queries like
`WHERE data @> '{"category":"laptop"}'`. Without the GIN index,
every query does a sequential scan parsing every `jsonb` value.
Key name storage overhead: each field name is stored per row,
so `{"customer_id": 12345}` uses more bytes than a dedicated
`customer_id` column. MongoDB BSON format is similar — binary
representation with per-document field names.

**Level 4 — Why it was designed this way (senior/staff):**
Semi-structured formats emerged from the tension between the
rigidity of relational schemas (designed for stable enterprise
domains in the 1970s) and the dynamism of internet-era product
development. The "join-free" document model trades referential
integrity for horizontal scalability and schema evolution. The
deeper design insight: semi-structured formats push schema
enforcement from the storage layer to the application layer.
This is the right trade-off when the schema is owned by a single
producer team; it becomes dangerous when multiple producers emit
to the same stream without governance — hence the rise of Schema
Registry as a mandatory companion for semi-structured data in
event streaming systems.

---

### ⚙️ How It Works (Mechanism)

**JSON document anatomy:**
```json
{
  "product_id": "A001",
  "name": "Laptop Pro 15",
  "category": "electronics",
  "attributes": {
    "ram_gb": 16,
    "cpu": "Intel i7",
    "storage": [
      {"type": "SSD", "size_gb": 512}
    ]
  },
  "tags": ["featured", "sale"]
}
```

Each record carries:
- **Key-value pairs** at the top level (self-describing)
- **Nested objects** (`attributes`) for hierarchical data
- **Arrays** (`storage`, `tags`) for repeated elements
- **Mixed value types** per key (string, number, array, object)

**How PostgreSQL jsonb query works:**
```
┌───────────────────────────────────────────────────┐
│   JSONB QUERY EXECUTION PATH                      │
│                                                   │
│  Query: WHERE data->>'category' = 'electronics'  │
│                ↓                                  │
│  With GIN index: index lookup → matching row IDs │
│  → fetch rows → O(log n + k matches)             │
│                                                   │
│  Without GIN index:                               │
│  Seq Scan → parse every jsonb value → compare    │
│  → O(n) — scales linearly with table size         │
└───────────────────────────────────────────────────┘
```

**Key name redundancy:**
```
Relational (typed column):
  [4 bytes int] [10 bytes varchar] per row for id + name
  Column name stored ONCE in schema DDL

JSON (key included per row):
  {"product_id":4,"name":"A"}
  Key "product_id" (10 chars) repeated EVERY row
  → 10x overhead for small integer values
```

---

### 💻 Code Example

**Example 1 — PostgreSQL jsonb queries:**
```sql
-- Create table with jsonb column
CREATE TABLE products (
  id   SERIAL PRIMARY KEY,
  data JSONB NOT NULL
);

-- Insert semi-structured records
INSERT INTO products (data) VALUES
  ('{"name":"T-Shirt","category":"clothing","size":"M"}'),
  ('{"name":"Laptop","category":"electronics","ram_gb":16}');

-- Query: filter by embedded field (slow without index)
SELECT data->>'name' FROM products
WHERE data->>'category' = 'electronics';

-- Add GIN index for performance
CREATE INDEX idx_products_data ON products USING GIN (data);

-- Now the query uses the index
EXPLAIN SELECT data->>'name' FROM products
WHERE data @> '{"category":"electronics"}';
```

**Example 2 — Validating semi-structured data at boundary:**
```python
# BAD: accept any JSON with no validation
@app.post("/product")
def create_product(data: dict):
    db.insert(data)  # garbage in, garbage out

# GOOD: validate shape at API boundary
from pydantic import BaseModel
from typing import Optional, List

class ProductIn(BaseModel):
    name: str
    category: str
    price: float
    attributes: Optional[dict] = None  # flexible sub-attrs
    tags: Optional[List[str]] = []

@app.post("/product")
def create_product(data: ProductIn):
    db.insert(data.model_dump())
    # Core fields enforced; attributes still flexible
```

**Example 3 — XML as semi-structured (legacy systems):**
```xml
<!-- Each record has different sub-elements -->
<product id="A001" category="clothing">
  <name>T-Shirt</name>
  <size>M</size>
  <color>Blue</color>
</product>

<product id="A002" category="electronics">
  <name>Laptop</name>
  <ram_gb>16</ram_gb>
  <cpu>Intel i7</cpu>
</product>
```
```python
# XPath query — traverses embedded structure
import lxml.etree as ET
root = ET.parse("products.xml").getroot()
laptops = root.xpath('//product[@category="electronics"]')
```

---

### ⚖️ Comparison Table

| Format | Schema | Human Readable | Binary | Best For |
|---|---|---|---|---|
| **JSON** | Self-describing | Yes | No | APIs, web, configs |
| XML | Self-describing + DTD/XSD | Yes | No | Enterprise integrations, legacy |
| YAML | Self-describing | Yes | No | Config files, CI/CD pipelines |
| Avro | Schema + registry | No | Yes | Kafka streams, schema evolution |
| MessagePack | Self-describing | No | Yes | High-throughput APIs |

**How to choose:** Use JSON for APIs and human-maintained data.
Use Avro/Protobuf for high-volume streaming where binary compactness
and schema evolution guarantees are required. Use YAML only for
configuration — never for data interchange at scale.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Semi-structured means schema-free | Every semi-structured consumer has an implicit schema — just not enforced at the storage layer. When producers violate it, consumers break silently |
| JSON in a database is always flexible | Querying JSON without indexes is a full table scan — flexibility has a direct query performance cost |
| YAML is a good data format | YAML's parsing is surprisingly complex and error-prone (Norway problem: `NO` parses as boolean `false`). Use JSON for data, YAML for config |
| Semi-structured data needs no governance | Without a schema registry, producers silently add/remove fields. Consumers break in production with no warning |
| Nested JSON is better than joins | Deep JSON nesting duplicates data (denormalisation). 1 million orders each embedding a 1 KB customer JSON = 1 GB of duplicated customer data |

---

### 🚨 Failure Modes & Diagnosis

**Silent Schema Drift**

**Symptom:**
Dashboard shows NULL values for a metric that was working last
week. No error in logs. Data just missing.

**Root Cause:**
A producer renamed a JSON key (`user_id` → `userId`). The consumer
reads `user_id`, gets `None`, inserts NULL. No validation layer
caught the key rename.

**Diagnostic Command / Tool:**
```bash
# Check schema versions in Schema Registry
curl http://schema-registry:8081/subjects

# Compare recent Kafka messages for field names
kafkacat -b broker:9092 -t my-topic -C -o -10 | \
  python3 -c "import sys,json; [print(list(json.loads(l).keys()))
              for l in sys.stdin]"
```

**Fix:**
Enforce schema via Avro + Schema Registry with compatibility check.

**Prevention:**
Treat JSON key names as a public API. Add Schema Registry
with `BACKWARD` compatibility enforcement on every topic.

---

**GIN Index Not Used (jsonb Full Scan)**

**Symptom:**
`SELECT * FROM events WHERE data->>'type' = 'click'` takes 30s
on a 10M row table in production. Query plan shows `Seq Scan`.

**Root Cause:**
No GIN index on the `data` column. PostgreSQL scans and parses
every `jsonb` row.

**Diagnostic Command / Tool:**
```sql
EXPLAIN ANALYZE
SELECT * FROM events WHERE data->>'type' = 'click';
-- Look for: "Seq Scan on events" (problem)
-- vs: "Bitmap Index Scan" (healthy)
```

**Fix:**
```sql
CREATE INDEX CONCURRENTLY idx_events_type
  ON events USING GIN ((data->>'type'));
-- Or for containment queries:
CREATE INDEX CONCURRENTLY idx_events_gin
  ON events USING GIN (data jsonb_path_ops);
```

**Prevention:**
Identify the top 3 JSON paths filtered by; add GIN indexes
before going to production.

---

**Key Name Storage Explosion**

**Symptom:**
A Kafka topic's storage grows 5× faster than expected. Topic
messages look small but total bytes are huge.

**Root Cause:**
Each message includes full verbose JSON key names
(`"customer_identifier"`, `"transaction_timestamp"`) repeated
per message vs Avro with a schema reference — key names stored
once in registry, not per message.

**Diagnostic Command / Tool:**
```bash
# Check average message size
kafka-log-dirs.sh --bootstrap-server broker:9092 \
  --topic-list my-topic | python3 -c \
  "import sys, json; d = json.load(sys.stdin);
  print(d)"
```

**Fix:**
Migrate to Avro or Protobuf. Keys stored in schema registry,
not per message. Typical 60-80% size reduction.

**Prevention:**
For high-volume event streams (>10k msg/s), always use binary
schema-based formats. JSON is for small-volume human-readable
scenarios only.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Structured vs Unstructured Data` — semi-structured is the
  middle ground; you need both extremes to understand the middle
- `Data Types` — JSON fields still have implicit types
  (string, number, boolean, null) even without enforcement
- `Data Formats (JSON, XML, YAML, CSV)` — the concrete file
  formats that carry semi-structured data

**Builds On This (learn these next):**
- `Schema Registry` — the governance layer that adds schema
  enforcement back to semi-structured event streams
- `Schema Evolution` — how to change semi-structured
  records over time without breaking consumers
- `Data Catalog` — discovering what semi-structured data
  exists in a data lake and inferring its schema

**Alternatives / Comparisons:**
- `Avro` — binary semi-structured format with mandatory
  external schema; more disciplined than plain JSON
- `Parquet` — columnar format that converts semi-structured
  data into typed columns for analytics
- `Serialization Formats` — the broader category
  of which JSON/XML are specific instances

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Data that carries its own structure       │
│              │ (keys/tags) but has no enforced schema    │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Rigid schemas cannot accommodate          │
│ SOLVES       │ polymorphic or evolving data shapes       │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Flexibility is deferred schema — the cost │
│              │ is paid at query time, not write time     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Product attributes vary by type; event    │
│              │ schemas evolve; external API responses    │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ High-volume analytics on fixed fields —   │
│              │ use typed columnar formats instead        │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Schema flexibility vs query performance   │
│              │ and data quality guarantees               │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "JSON is a schema that moves — it just    │
│              │  moves to where it's hardest to enforce." │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Schema Registry → Schema Evolution →      │
│              │ Avro                                      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A streaming pipeline receives JSON events from 20
different microservices into a single Kafka topic. Service A
emits `{"userId": 123}`, Service B emits `{"user_id": 123}`,
Service C adds a new field `{"userId": 123, "sessionId": "abc"}`
without notice. A downstream consumer reads all three. Trace
exactly how each variation manifests in the consumer, what
silent errors occur, and design a three-layer defence to prevent
this across all 20 services without requiring a centralised team
to approve every schema change.

**Q2.** You store product catalog data in PostgreSQL as `jsonb`.
Today you have 50 million products and 200 distinct attribute
sets. Your analytics team wants to compute the average `price`
across all products in the `electronics` category every hour.
Explain precisely why this query degrades as product count grows,
what the two architectural solutions are, and at what scale
each solution is appropriate.

