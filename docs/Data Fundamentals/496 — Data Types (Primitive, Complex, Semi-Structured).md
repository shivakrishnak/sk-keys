---
layout: default
title: "Data Types (Primitive, Complex, Semi-Structured)"
parent: "Data Fundamentals"
nav_order: 496
permalink: /data-fundamentals/data-types/
number: "0496"
category: Data Fundamentals
difficulty: ★☆☆
depends_on: Variables, Memory Management Models, Abstraction
used_by: Serialization Formats, Data Formats, Schema Evolution
related: Structured vs Unstructured Data, Semi-Structured Data, Data Formats
tags:
  - dataengineering
  - foundational
  - mental-model
  - first-principles
---

# 496 — Data Types (Primitive, Complex, Semi-Structured)

⚡ TL;DR — Data types classify what kind of value a piece of data holds, determining how it is stored, interpreted, and processed.

| #496 | Category: Data Fundamentals | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Variables, Memory Management Models, Abstraction | |
| **Used by:** | Serialization Formats, Data Formats, Schema Evolution | |
| **Related:** | Structured vs Unstructured Data, Semi-Structured Data, Data Formats | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Imagine every piece of data stored as raw bytes with no label.
The number 42 stored in memory is identical at the bit level to
the ASCII character `*`. An image file's bytes look like random
numbers. A temperature reading of `36.6` is indistinguishable
from the string `"36.6"`. Without a system to classify data by
its nature, every program would need to track separately "this
is a number, that is text" — and one mix-up would silently
corrupt calculations or crash systems.

**THE BREAKING POINT:**
In early computing, type confusion was a genuine cause of program
failure. Arithmetic on textual data produces garbage. Treating a
float as an integer truncates precision. Memory systems that
allocate fixed sizes cannot handle variable-length structures like
strings without explicit rules for where they start and end.

**THE INVENTION MOMENT:**
This is exactly why data types were created. They encode the
contract: "this memory region holds a 32-bit integer," "this
field holds a UTF-8 string up to 255 characters." The type system
enforces correct interpretation at every layer — from CPU
instructions to database schemas to API contracts.

---

### 📘 Textbook Definition

A **data type** is a classification that specifies the kind of
value a variable or data field can hold, the operations valid on
that value, and how it is stored in memory or on disk. Primitive
types (int, float, boolean, char) are atomic, fixed-size, and
directly supported by hardware. Complex types (arrays, structs,
objects) compose primitives into richer structures. Semi-structured
data types lack a rigid schema but carry embedded metadata (keys,
tags) that partially describe their structure — examples include
JSON objects and XML documents.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A data type tells both the computer and the programmer: "this
value is a number / text / list / object."

**One analogy:**

> Imagine mail slots in a post office. Each slot has a label:
> "letters only," "packages only," "parcels under 5 kg." The label
> is the data type — it decides what can go in, how much space is
> reserved, and what gets delivered to whom.

**One insight:**
The deepest truth about data types is that they exist for TWO
audiences: the machine (so it knows how many bytes to allocate and
which CPU instruction to use) and the programmer (so they know
what operations are valid). When these two contracts align,
software is robust. When they diverge — e.g., in dynamically typed
languages at runtime — entire classes of bugs emerge.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Every value in a computer system is ultimately stored as bits.
2. Bits are meaningless without an interpretation rule.
3. A data type IS that interpretation rule — nothing more.

**DERIVED DESIGN:**
Given that bits need interpretation, a minimal type system must
define: (a) the size in memory, (b) the valid operations, and (c)
the range of representable values. This immediately splits into
two tiers:

*Primitive types* — directly map to CPU operations. An `int32`
maps to a 32-bit register and the CPU's ADD instruction. A
`float64` maps to an IEEE 754 double-precision float with its
own arithmetic unit. These are the atoms.

*Complex types* — compose atoms into structures. An array is a
contiguous block of same-typed atoms. A struct groups different
types together. A string is typically an array of chars plus a
length or null terminator. These enable modelling real-world
entities.

*Semi-structured types* — the middle ground between rigid schemas
and raw blobs. A JSON object has key-value pairs where keys are
strings and values can be any type, including nested objects. The
schema is not enforced externally but is implied by the data
itself. This flexibility is its power and its danger.

**THE TRADE-OFFS:**
**Gain (Primitive):** Speed, predictability, CPU-native operations.
**Cost (Primitive):** Inflexibility — cannot represent missing
values, nested structures, or variable-length data natively.

**Gain (Complex):** Expressiveness — model any real-world entity.
**Cost (Complex):** Overhead: pointer indirection, heap allocation,
serialization cost.

**Gain (Semi-structured):** Schema flexibility — evolve without
migration, heterogeneous records.
**Cost (Semi-structured):** No static validation, larger storage
footprint, slower query performance without indexes.

---

### 🧪 Thought Experiment

**SETUP:**
You store a temperature sensor reading in a database. You have two
columns: `sensor_id` and `temperature`. You choose to store both
as the generic type `TEXT`.

**WHAT HAPPENS WITHOUT PROPER DATA TYPES:**
A week later you run `SELECT AVG(temperature) FROM readings`.
The database tries to average text strings. Some readings are
`"23.5"`, some are `"N/A"` (sensor offline), one is `"23.5°C"`
(a display bug). The query either errors or silently returns
`NULL`. You write a data-cleaning script. Six months later a new
engineer stores `"VERY_HOT"` in temperature. The entire pipeline
breaks. Debugging takes two days.

**WHAT HAPPENS WITH PROPER DATA TYPES:**
`sensor_id` is `VARCHAR(64)`, `temperature` is `DECIMAL(5,2)`
allowing `NULL`. The database rejects `"N/A"` at insert time —
the sensor driver must store `NULL` explicitly. `"23.5°C"` is
rejected before it pollutes the table. `AVG()` works correctly
and `NULL` values are excluded per SQL standard. The type
contract enforces quality at the boundary.

**THE INSIGHT:**
Data types are quality gates. Moving type enforcement from
application code to the storage layer catches bugs at the source
rather than downstream — where they are orders of magnitude more
expensive to fix.

---

### 🧠 Mental Model / Analogy

> Think of data types like the coloured slots in a children's
> shape-sorting toy. The square hole only accepts squares. The
> circle hole only accepts circles. You cannot force a triangle
> through the round hole — and the toy (the type system) rejects
> the attempt immediately rather than letting you discover the
> mismatch later when you empty the box.

- "Square slot" → integer type: only whole numbers fit
- "Round slot" → float type: decimal numbers fit
- "Star slot" → string type: text fits
- "Mystery bag" → semi-structured (JSON/map): anything fits,
  but you must check what's inside every time
- "Forcing the wrong shape" → type coercion / type error at runtime

**Where this analogy breaks down:** In weakly typed languages
(JavaScript, PHP), the toy actively reshapes pieces to fit the
slot (implicit type coercion) rather than rejecting them. This is
dangerous: `"5" + 3 = "53"` in JS, not `8`.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A data type is the label on a container that says what kind of
thing can go inside — numbers, words, true/false, lists, etc. It
helps both the computer and the programmer know how to handle the
data correctly.

**Level 2 — How to use it (junior developer):**
Choose the narrowest type that satisfies your need: use `int32`
not `string` for a count; use `boolean` not `int` for a flag;
use `DECIMAL` not `FLOAT` for money (floats have precision
errors). In databases, choosing the right column type improves
storage efficiency and enables correct aggregations. In APIs, use
`number` for JSON numerics rather than string-encoding them,
unless leading zeros matter (e.g., zip codes).

**Level 3 — How it works (mid-level engineer):**
Primitive types map directly to CPU word sizes. `int32` aligns to
a 4-byte boundary; unaligned access causes a CPU penalty or trap.
Floating-point uses IEEE 754 binary representation: `0.1` cannot
be represented exactly in binary, causing the infamous `0.1 + 0.2
≠ 0.3`. Complex types like `ArrayList<Integer>` in Java box each
integer into a heap object (16-byte overhead per element), making
them 4–8× more memory-intensive than primitive `int[]` arrays.
Semi-structured types like JSON pay a serialisation tax: a 4-byte
integer stored as JSON text might consume 1–6 bytes
depending on its value, plus key name overhead.

**Level 4 — Why it was designed this way (senior/staff):**
The split between primitive and complex types mirrors the Von
Neumann architecture split between register operations (fast,
fixed-size) and memory operations (flexible, indirect). Languages
like Java made the mistake of unifying under "everything is an
object" — causing primitive boxing performance issues that haunted
the JVM for decades, addressed only partly in Java 8 streams and
fully fixed in Project Valhalla's value types. Semi-structured
types emerged as a pragmatic response to the impedance mismatch
between relational schemas and the real-world polymorphism of
data — a compromise whose cost only becomes visible when you need
to run analytics on millions of JSON records without indexes.

---

### ⚙️ How It Works (Mechanism)

When a programming language or database processes a value, the
type determines four things:

**1. Memory size:**
`boolean` → 1 bit (padded to 1 byte). `int32` → 4 bytes.
`float64` → 8 bytes. `varchar(255)` → 1–256 bytes (variable).

**2. Alignment:**
CPUs require types to start at address multiples of their size.
A struct `{char a; int b;}` uses 8 bytes, not 5, due to padding.

**3. Valid operations:**
The type decides which instructions are invoked:
- Integer: ADD, SUB, MUL, DIV (integer arithmetic unit)
- Float: FADD, FMUL (floating-point unit — different circuit)
- String: compare byte-by-byte, no arithmetic

**4. Interpretation:**
The same 4 bytes `0x41424344` mean:
- As `int32`: 1094861636
- As `float32`: approximately 12.141
- As ASCII string: "ABCD"

```
┌──────────────────────────────────────────────────┐
│         DATA TYPE TIER OVERVIEW                  │
├──────────────┬───────────────────────────────────┤
│ PRIMITIVE    │ int, float, bool, char             │
│              │ Fixed size, CPU-native ops         │
├──────────────┼───────────────────────────────────┤
│ COMPLEX      │ Array, Struct, Object, String      │
│              │ Composed, heap-allocated           │
├──────────────┼───────────────────────────────────┤
│ SEMI-        │ JSON, XML, Map<K,V>                │
│ STRUCTURED   │ Self-describing, schema-optional   │
└──────────────┴───────────────────────────────────┘
```

**Numeric precision trap:**
```python
# BAD — using float for money
price = 0.1 + 0.2
print(price)  # 0.30000000000000004

# GOOD — use Decimal for exact decimal arithmetic
from decimal import Decimal
price = Decimal("0.1") + Decimal("0.2")
print(price)  # 0.3
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Sensor/API/User Input
  ↓
Application Layer (type validated in code)
  ↓
Serialization (JSON/Avro/Protobuf)       ← YOU ARE HERE
  ↓
Database Schema (type enforced at write)
  ↓
Query Engine (type-specific operations: AVG, SUM, LIKE)
  ↓
Output (rendered correctly)
```

**FAILURE PATH:**
Type mismatch at API boundary → silent coercion → wrong
aggregation → wrong dashboards → business decisions on bad data.

**WHAT CHANGES AT SCALE:**
At 10 billion rows, choosing `VARCHAR(255)` instead of `CHAR(10)`
for a fixed-length field wastes terabytes of storage. JSON columns
in relational databases become query bottlenecks at scale because
every JSON extraction requires parsing. Columnar formats (Parquet,
ORC) achieve 10× compression on typed columns because they can
apply type-specific encoding (dictionary encoding for strings,
delta encoding for timestamps).

---

### 💻 Code Example

**Example 1 — Type choice matters for storage:**
```sql
-- BAD: everything as TEXT
CREATE TABLE sensor_readings (
  sensor_id TEXT,
  temperature TEXT,
  recorded_at TEXT
);

-- GOOD: type-correct schema
CREATE TABLE sensor_readings (
  sensor_id    VARCHAR(64)   NOT NULL,
  temperature  DECIMAL(5,2),          -- NULL = offline
  recorded_at  TIMESTAMP     NOT NULL
);
```

**Example 2 — Primitive vs boxed type performance (Java):**
```java
// BAD: boxed Integer — heap-allocated, GC pressure
List<Integer> values = new ArrayList<>();
for (int i = 0; i < 1_000_000; i++) {
    values.add(i);  // auto-boxes each int
}

// GOOD: primitive array — stack/contiguous memory
int[] values = new int[1_000_000];
for (int i = 0; i < 1_000_000; i++) {
    values[i] = i;  // no boxing
}
// 4 bytes per element vs ~16 bytes per element
```

**Example 3 — Semi-structured JSON with type discipline:**
```python
# BAD: no type enforcement on JSON input
def process(data: dict):
    discount = data["discount"]  # could be "10%" or 10 or null
    total = price * (1 - discount)  # crashes on "10%"

# GOOD: validate types at boundary with Pydantic
from pydantic import BaseModel
from typing import Optional

class OrderIn(BaseModel):
    price: float
    discount: Optional[float] = 0.0  # enforced as float

def process(data: OrderIn):
    total = data.price * (1 - data.discount)
```

---

### ⚖️ Comparison Table

| Type Class | Schema Required | Query Speed | Flexibility | Best For |
|---|---|---|---|---|
| **Primitive** | Yes (rigid) | Fastest | None | Counters, flags, timestamps |
| Complex/Struct | Yes (rigid) | Fast | Low | Entity records |
| Semi-structured (JSON) | No | Slow without index | High | Event logs, dynamic attributes |
| Columnar (Parquet) | Yes | Very fast for analytics | Low | OLAP, data lake queries |
| Schema-on-read | No | Slowest | Highest | Exploratory data analysis |

**How to choose:** Use primitive/complex types when you control
the schema and need performance. Use semi-structured types when
data shape varies per record or evolves rapidly. Switch to
columnar formats when analytical read performance dominates.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Strings are always safe for numbers | Strings allow values like `"N/A"`, `""`, or `"1,000"` — arithmetic silently fails or returns wrong results |
| `float` is fine for money | IEEE 754 binary floats cannot represent many decimal fractions exactly; use `DECIMAL` or `Numeric` for financial values |
| JSON is schema-less so schema doesn't matter | JSON has an implicit schema enforced by the consumer; when consumers diverge, the system silently corrupts |
| Bigger types are always safer | Using `BIGINT` for a value that fits in `INT` wastes memory, slows scans, and reduces cache efficiency |
| Type conversions are free | Implicit type coercion (especially in JS and SQL) is a major source of subtle bugs and performance issues |

---

### 🚨 Failure Modes & Diagnosis

**Floating-Point Money Errors**

**Symptom:**
Rounding errors accumulate over millions of financial
transactions. A balance shows `$100.00000000001`.

**Root Cause:**
`float`/`double` uses binary fractions — `0.1` in binary is a
repeating fraction, like `1/3` in decimal.

**Diagnostic Command / Tool:**
```python
python3 -c "print(0.1 + 0.2)"
# Output: 0.30000000000000004
```

**Fix:**
```python
# BAD
total = 0.1 + 0.2

# GOOD
from decimal import Decimal
total = Decimal('0.1') + Decimal('0.2')
```

**Prevention:**
Define a coding standard: money is always `DECIMAL`/`Numeric`;
never `float`/`double`.

---

**Type Coercion Silent Bugs (SQL)**

**Symptom:**
A query returns wrong row count or silently drops rows.

**Root Cause:**
SQL compares `WHERE user_id = '007'` against an `INT` column.
The string `'007'` is coerced to integer `7` — rows with
`user_id = 7` match, but the intent was string matching.

**Diagnostic Command / Tool:**
```sql
EXPLAIN SELECT * FROM users WHERE user_id = '007';
-- Look for implicit cast in query plan
```

**Fix:**
```sql
-- BAD
SELECT * FROM users WHERE user_id = '007';

-- GOOD — match literal type to column type
SELECT * FROM users WHERE user_id = 7;
-- Or store user_id as VARCHAR if leading zeros matter
```

**Prevention:**
Use an ORM or parameterised queries that enforce type binding.

---

**JSON Column Query Slowness**

**Symptom:**
Queries on a `jsonb` column grow from 10ms to 10s as table grows.

**Root Cause:**
Every row requires JSON parsing to extract a nested field;
no columnar index exists.

**Diagnostic Command / Tool:**
```sql
EXPLAIN ANALYZE
SELECT data->>'temperature' FROM readings
WHERE data->>'sensor_id' = 'S42';
-- Look for: Seq Scan (bad) vs Index Scan (good)
```

**Fix:**
Add a generated column with a GIN or B-tree index, or extract
the hot field to a typed column.

**Prevention:**
Treat frequently-queried JSON keys as promoted typed columns;
reserve JSON for truly variable attributes only.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Variables` — a variable is just a named container for a typed
  value; understanding types is understanding what can fill that container
- `Memory Management Models` — how types dictate allocation on
  stack vs heap
- `Abstraction` — types are the first and most fundamental
  abstraction layer over raw bits

**Builds On This (learn these next):**
- `Serialization Formats` — serialization is the translation of
  typed in-memory values into bytes for storage or transmission
- `Schema Evolution` — how types in a schema change over time
  without breaking consumers
- `Data Formats (JSON, XML, YAML, CSV)` — each format has its
  own type system and coercion rules

**Alternatives / Comparisons:**
- `Structured vs Unstructured Data` — the extreme opposite: raw
  blobs with no type metadata at all
- `Semi-Structured Data` — the middle ground between rigid types
  and raw blobs

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Classification of values by kind,         │
│              │ size, and valid operations                 │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Bits are meaningless without an           │
│ SOLVES       │ interpretation contract                   │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Types enforce quality at the boundary;    │
│              │ wrong types propagate silently downstream  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Defining any data storage schema,         │
│              │ API contract, or data pipeline column      │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Exploratory prototyping where schema      │
│              │ is genuinely unknown yet                   │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Type safety vs schema flexibility         │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "A type is not just a size — it's a       │
│              │  promise about what the bits mean."        │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Data Formats → Serialization Formats →    │
│              │ Schema Evolution                           │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A microservice receives a `price` field as a JSON number
(e.g., `{"price": 9.99}`). JavaScript parses this as a 64-bit
IEEE 754 double. The service multiplies by a quantity and stores
the result in PostgreSQL as `NUMERIC(10,2)`. After a million such
transactions, a reconciliation job finds a $0.03 discrepancy.
Trace exactly which step introduced the error, why IEEE 754 cannot
represent `9.99` precisely, and what the fix is at each layer.

**Q2.** You're designing a data lake schema for IoT sensor events.
Each sensor type emits a different payload shape — temperature
sensors emit `{temp, unit}`, vibration sensors emit
`{frequency, amplitude, axis}`. You consider two designs: one
JSON column per row vs a wide table with nullable typed columns.
At 10 billion events per day with 95% of queries filtering by
sensor type and computing `AVG`, which design wins on query
performance and why? What would change your answer?

