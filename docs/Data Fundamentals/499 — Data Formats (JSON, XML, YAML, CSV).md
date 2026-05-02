---
layout: default
title: "Data Formats (JSON, XML, YAML, CSV)"
parent: "Data Fundamentals"
nav_order: 499
permalink: /data-fundamentals/data-formats/
number: "0499"
category: Data Fundamentals
difficulty: ★☆☆
depends_on: Semi-Structured Data, Data Types, HTTP and APIs
used_by: Serialization Formats, Schema Registry, ETL vs ELT, Data Pipelines
related: Binary Formats, YAML, Serialization Formats, Semi-Structured Data
tags:
  - dataengineering
  - foundational
  - api
  - mental-model
---

# 499 — Data Formats (JSON, XML, YAML, CSV)

⚡ TL;DR — Data formats are the agreed-upon languages for writing data to text so that any system can read it — JSON for APIs, CSV for spreadsheets, XML for enterprise, YAML for configs.

| #499 | Category: Data Fundamentals | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Semi-Structured Data, Data Types, HTTP and APIs | |
| **Used by:** | Serialization Formats, Schema Registry, ETL vs ELT, Data Pipelines | |
| **Related:** | Binary Formats, YAML, Serialization Formats, Semi-Structured Data | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Two systems need to exchange data. System A stores customer
records as in-memory Java objects. System B is a Python service
on a different server. Java objects cannot cross the wire — they
are binary heap structures tied to a specific JVM instance.
Without an agreed text representation, every pair of systems
would invent its own wire protocol — a Tower of Babel where
nothing can talk to anything.

**THE BREAKING POINT:**
Before standardised data formats, every enterprise integration
required custom parsers. Mainframe exports used fixed-width flat
files. Different vendors sent data in incompatible proprietary
formats. A single data exchange project required weeks of
bespoke parser development, version-specific tools, and test
coverage for every edge case in the proprietary format.

**THE INVENTION MOMENT:**
This is exactly why standardised text data formats emerged. CSV
brought universal spreadsheet exchange in the 1970s. XML brought
structured, hierarchical, self-describing exchange in 1998.
JSON brought lightweight, human-readable API exchange in the
2000s. Each solved the specific pain of its era. Today these
formats are universal: every major programming language ships
with parsers for all four.

---

### 📘 Textbook Definition

A **data format** is a specification for encoding structured
information as a sequence of characters or bytes for storage
or transmission. Text-based data formats make data human-readable
and language-agnostic. **CSV** (Comma-Separated Values) encodes
flat tabular data as delimited rows. **JSON** (JavaScript Object
Notation) encodes hierarchical key-value structures using a
lightweight syntax derived from JavaScript object literals.
**XML** (eXtensible Markup Language) encodes hierarchical data
as tagged elements with attributes, supporting both schema
validation (XSD) and transformation (XSLT). **YAML** (YAML Ain't
Markup Language) is a human-readable superset of JSON intended
primarily for configuration files.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A data format is the common language two systems agree to speak
so they can exchange information.

**One analogy:**

> Imagine international travellers all speaking different native
> languages. They agree to communicate in English. Data formats
> are the "English" for data — every system that learns the format
> can speak to every other system that knows it, regardless of
> the internal language each uses.

**One insight:**
Every text data format makes a fundamental trade-off: human
readability vs machine efficiency. CSV is the simplest and
smallest but can express very little. JSON adds nesting and types
but pays a verbosity overhead. XML adds schema validation but pays
even more verbosity. Binary formats (Avro, Parquet, Protobuf)
abandon human readability entirely in exchange for compactness
and speed — which is why they dominate at scale.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Data must survive a round-trip: serialize → transmit/store →
   deserialize → same logical value.
2. Both producer and consumer must agree on the format.
3. Human-readable formats sacrifice size for debuggability.

**DERIVED DESIGN:**

*CSV* is the minimal text format: values separated by commas,
rows separated by newlines. No nesting, no types (everything is
a string), no schema. Its simplicity is its longevity — any
spreadsheet, database, or scripting language handles CSV natively.

*JSON* adds types (string, number, boolean, null, array, object),
nesting, and key names. It was designed to be a subset of
JavaScript for easy browser parsing — the `eval()` shortcut that
made AJAX practical in 2001. Its simplicity (6 types, no
comments, no schema) made it the de-facto API wire format.

*XML* was designed for document markup. It adds: element
attributes, namespaces (to avoid key name collisions across
organisations), DTD/XSD schema validation, XPath queries, and
XSLT transformations. Power comes at the cost of verbosity
(every value wrapped in opening and closing tags). XML dominates
in legacy enterprise systems, healthcare (HL7), and banking (SWIFT).

*YAML* is a superset of JSON (valid JSON is valid YAML) designed
for human-written configuration files. It supports comments,
multi-line strings, anchors (references to reuse values), and
indentation-based structure without brackets. Its parsing
complexity is notorious — 23 data types, the Norway problem
(`NO` → `false`), and implicit type coercion make it fragile
for machine-generated data.

**THE TRADE-OFFS:**
**Gain (Text formats):** Universal readability, no binary tools
needed, easy debugging, grep-able.
**Cost (Text formats):** 3–10× overhead vs binary; no type
enforcement at storage level (everything is a string in CSV);
parsing CPU cost at scale.

---

### 🧪 Thought Experiment

**SETUP:**
You need to transfer a table of 10 million customer records
(id: int, name: string, balance: decimal) between two systems.

**WHAT HAPPENS WITH CSV:**
10 million rows, average 30 characters per row = 300 MB.
Parse: split on comma, strip whitespace, read all values as
strings, convert balance `"123.45"` to decimal in application code.
Problem: name `"Smith, John"` contains a comma — the parser
splits it incorrectly unless the value is quoted. Quoting rules
vary between RFC 4180 implementations. Two systems with slightly
different CSV dialects silently corrupt data on `"Smith, Jr."`.

**WHAT HAPPENS WITH JSON:**
Each row becomes
`{"id":1,"name":"Smith, John","balance":123.45}`.
Comma in name is safe — JSON strings use `"..."` delimiters.
Balance is a JSON number — type preserved. File size: ~600 MB
(double due to key names repeated 10 million times). Parse cost
higher than CSV.

**THE INSIGHT:**
No text format is universally correct. CSV is compact but fragile
for strings with delimiters. JSON is robust but verbose. The
correct format depends on the data shape (flat vs hierarchical),
the volume, and whether human readability is required.

---

### 🧠 Mental Model / Analogy

> Think of data formats as packing methods for shipping goods.
> **CSV** is stacking items in a flat box with just commas to
> separate them — minimal packing material, but fragile for items
> that contain commas. **JSON** is bubble-wrapping each item
> with its label attached — clearly marked, handles nesting,
> but the bubble wrap adds bulk. **XML** is professional crating
> with certified labels and a manifest — maximally safe and
> self-describing, but takes more cardboard per item. **Avro/
> Parquet** is vacuum-seal packaging — tiny, fast to unpack,
> but requires the factory specification to reassemble.

- "Flat box" → CSV (tabular, no nesting)
- "Bubble wrap + label" → JSON (structured, human-readable)
- "Professional crating + manifest" → XML (verbose, schema-validated)
- "Vacuum seal" → Binary formats (Avro, Parquet)
- "Packing specification" → schema in Schema Registry

**Where this analogy breaks down:** Unlike physical packages,
serialised data can be repackaged (transcoded) from one format
to another losslessly — e.g., CSV → JSON → Parquet in an ETL
pipeline.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A data format is a way of writing information as text so any
computer program can read it. CSV is used for spreadsheets;
JSON is used for web APIs; XML is used by old enterprise systems;
YAML is used for configuration files like Kubernetes manifests.

**Level 2 — How to use it (junior developer):**
Use JSON for REST APIs and JavaScript-heavy applications. Use
CSV for data exports/imports to/from spreadsheets and analytics
tools. Use YAML for configuration files (Docker Compose,
Kubernetes). Avoid XML for new projects unless integrating with
legacy systems that mandate it. Always specify the encoding
(UTF-8) and handle parsing errors — malformed JSON or CSV
will crash a naive parser.

**Level 3 — How it works (mid-level engineer):**
JSON parsing is two phases: lexing (tokenise the character stream
into tokens: `{`, `"key"`, `:`, value, `}`) and parsing
(build the in-memory tree). Numbers are always parsed as floats
unless the parser is told otherwise — so very large integers
(beyond 2^53) lose precision in standard JavaScript JSON.
CSV parsers must handle quoted fields, escaped quotes, BOM bytes
(Windows Excel), different line endings (CRLF vs LF), and missing
trailing commas. YAML's implicit type coercion is based on the
YAML 1.1 spec: `yes`, `on`, `true`, `1` all parse as boolean
true — a source of prod bugs in Kubernetes manifests where
`country: NO` (for Norway) becomes `country: false`.

**Level 4 — Why it was designed this way (senior/staff):**
JSON's design philosophy was radical simplicity: 6 types, no
comments (to prevent commented-out code in config files — a
deliberate choice by Douglas Crockford), no schema, no
namespaces. This made it trivially parseable in every language.
XML's design philosophy was maximum expressiveness for document
markup — its heritage in SGML shows. The trade-off (schema
validation, namespaces, XSLT) was appropriate for document
publishing workflows but created accidental complexity for data
exchange. YAML's design mistake: it tried to be a human-friendly
superset of JSON but added so many implicit conventions that its
formal grammar spans 23 scalar types and its canonicalisation
rules are famously difficult to implement correctly. In practice,
YAML parsing bugs are a significant source of CI/CD security
vulnerabilities (YAML injection in CI pipeline configs).

---

### ⚙️ How It Works (Mechanism)

**The same record in four formats:**

```json
// JSON — hierarchical, typed
{
  "id": 1001,
  "name": "Alice Chen",
  "balance": 1250.50,
  "tags": ["gold", "active"]
}
```

```xml
<!-- XML — verbose, tag-enclosed, namespace-ready -->
<customer id="1001">
  <name>Alice Chen</name>
  <balance>1250.50</balance>
  <tags>
    <tag>gold</tag>
    <tag>active</tag>
  </tags>
</customer>
```

```yaml
# YAML — human-readable, indentation-based
id: 1001
name: Alice Chen
balance: 1250.50
tags:
  - gold
  - active
```

```
CSV — flat, no nesting (tags must be serialised as a string)
id,name,balance,tags
1001,"Alice Chen",1250.50,"gold,active"
```

**Size comparison for 1 million such records (approximate):**
```
┌──────────────────────────────────────────────────┐
│ Format   │ Size (1M records) │ Parse Speed        │
├──────────┼───────────────────┼────────────────────┤
│ CSV      │ ~40 MB            │ Fastest            │
│ JSON     │ ~90 MB            │ Fast               │
│ XML      │ ~160 MB           │ Slow               │
│ YAML     │ ~100 MB           │ Slowest            │
│ Parquet  │ ~8 MB             │ Very fast (column) │
└──────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 — JSON parse and produce (Python):**
```python
import json

# Deserialise: string → Python dict
raw = '{"id": 1001, "name": "Alice", "balance": 1250.50}'
record = json.loads(raw)
print(record["balance"])  # 1250.5 (float)

# Serialise: Python dict → string
output = json.dumps(record, ensure_ascii=False, indent=2)
```

**Example 2 — CSV with quoting edge cases (Python):**
```python
import csv, io

# BAD: manual split — breaks on quoted fields
line = '1001,"Smith, Jr.",1250.50'
bad = line.split(",")  # ["1001", '"Smith', ' Jr."', "1250.50"]

# GOOD: use csv.reader — handles RFC4180 quoting
reader = csv.reader(io.StringIO(line))
good = next(reader)  # ["1001", "Smith, Jr.", "1250.50"]
print(good[1])  # "Smith, Jr." — correct
```

**Example 3 — YAML Norway problem:**
```yaml
# DANGEROUS YAML (spec 1.1 behaviour)
config:
  country: NO       # parses as false (boolean!) in PyYAML
  active: yes       # parses as true (boolean!)
  port: 8080        # parses as int
  version: 1.0      # parses as float
```
```python
import yaml
cfg = yaml.safe_load(open("config.yaml"))
print(cfg["country"])   # False  ← WRONG! should be "NO"
print(type(cfg["port"]))  # <class 'int'>

# FIX: quote all non-obvious string values
# country: "NO"
```

**Example 4 — XML parse with namespace:**
```python
import xml.etree.ElementTree as ET

xml = """
<ns:customer xmlns:ns="http://example.com/schema">
  <ns:name>Alice</ns:name>
  <ns:balance>1250.50</ns:balance>
</ns:customer>
"""
root = ET.fromstring(xml)
ns = {"ns": "http://example.com/schema"}
name = root.find("ns:name", ns).text  # "Alice"
```

---

### ⚖️ Comparison Table

| Format | Hierarchical | Typed | Schema Support | Human-Readable | Best For |
|---|---|---|---|---|---|
| **CSV** | No | No (strings) | None | Yes | Tabular data, spreadsheet I/O |
| **JSON** | Yes | Partial | JSON Schema (optional) | Yes | REST APIs, configs, events |
| XML | Yes | No (strings) | XSD, DTD | Verbose | Enterprise, document markup |
| YAML | Yes | Implicit | None | Yes | Config files (K8s, CI/CD) |
| Avro | Yes | Full | Mandatory (registry) | No | Kafka streams, schema evolution |
| Parquet | Yes (nested) | Full | Yes | No | Analytics, data lake |

**How to choose:** JSON for APIs and event streaming at moderate
scale. CSV for flat data exchange with humans and spreadsheets.
YAML only for hand-written config files. Binary formats (Avro,
Parquet) for high-volume pipelines where size and speed matter.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| JSON numbers are always accurate | JSON number parsing in JavaScript loses precision for integers > 2^53; large IDs must be sent as strings |
| CSV is simple so it never breaks | CSV has no universal standard; quoting rules, line endings (CRLF vs LF), BOM bytes, and encoding vary between tools causing subtle parse failures |
| YAML is a good data serialisation format | YAML is designed for human-written configs, not machine-generated data; implicit type coercion causes data corruption bugs |
| XML is dead | XML dominates in healthcare (HL7 FHIR), finance (ISO 20022), and many government systems — billions of XML documents flow daily |
| JSON Schema enforces types at API boundaries | JSON Schema is only enforced if you explicitly validate against it; HTTP APIs accept any JSON by default |

---

### 🚨 Failure Modes & Diagnosis

**Large JSON ID Precision Loss**

**Symptom:**
A frontend receives a JSON response with `"order_id": 9876543210123456`
and stores `9876543210123456` in JavaScript. On the next API
call it sends back `9876543210123456` as `9876543210123450`
(the last digits became zero). Order lookup fails silently.

**Root Cause:**
JavaScript's `JSON.parse()` represents all numbers as IEEE 754
`double`, which has 53-bit mantissa — integers > 2^53 lose
precision.

**Diagnostic Command / Tool:**
```javascript
JSON.parse('{"id": 9876543210123456}').id
// Output: 9876543210123456 → actually 9876543210123456
// (may show correctly on small examples; test with >15 digits)
Number.MAX_SAFE_INTEGER  // 9007199254740991
```

**Fix:**
```json
// BAD: large integer as JSON number
{"order_id": 9876543210123456}

// GOOD: large integer as JSON string
{"order_id": "9876543210123456"}
```

**Prevention:**
Rule: all IDs > 32 bits must be serialised as JSON strings.

---

**CSV Encoding / Quoting Mismatch**

**Symptom:**
ETL job imports CSV from an external vendor. 1% of rows have
extra columns or wrong data. Customer names are scrambled.

**Root Cause:**
Vendor CSV uses Windows-1252 encoding; pipeline expects UTF-8.
Names with accented characters (Müller, Pérez) are corrupted.

**Diagnostic Command / Tool:**
```bash
# Detect encoding
file -i vendor_data.csv
# or
python3 -c "import chardet; \
  print(chardet.detect(open('vendor_data.csv','rb').read(100000)))"
```

**Fix:**
```python
# BAD: assume UTF-8
with open("vendor.csv", "r") as f:
    reader = csv.reader(f)

# GOOD: detect and convert
with open("vendor.csv", "r", encoding="windows-1252") as f:
    reader = csv.reader(f)
```

**Prevention:**
Always specify encoding in the data exchange contract.
Auto-detect on ingestion as defence in depth.

---

**YAML Type Coercion in Config**

**Symptom:**
Kubernetes deployment fails with
`error: field version is of type bool, not string` after a
config edit.

**Root Cause:**
Developer wrote `version: 1.0` intending a string; YAML parses
it as a float. Or `enabled: yes` parses as boolean.

**Diagnostic Command / Tool:**
```bash
# Validate YAML types before applying
python3 -c "import yaml, sys; print(yaml.safe_load(sys.stdin))" \
  < config.yaml
```

**Fix:**
Quote all values that should be strings:
```yaml
version: "1.0"
country: "NO"
enabled: "yes"
```

**Prevention:**
Use a YAML linter (yamllint) in CI that flags implicit type
coercions. Consider JSON-only for machine-generated configs.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Semi-Structured Data` — JSON, XML, and YAML are the primary
  semi-structured data formats; understanding what semi-structured
  means explains why these formats exist
- `Data Types` — each format handles types differently;
  JSON has 6 types, CSV has none
- `HTTP and APIs` — JSON became the dominant API format
  because of HTTP's ubiquity

**Builds On This (learn these next):**
- `Binary Formats (Avro, Parquet, ORC, Protobuf)` — the
  next evolution: abandon human-readability for scale
- `Serialization Formats` — the programming-layer abstraction
  above raw format
- `Schema Registry` — adds type safety back to schema-loose
  formats like JSON in streaming systems

**Alternatives / Comparisons:**
- `Binary Formats` — Avro, Parquet, Protobuf trade
  human-readability for 5–10× size and speed improvement
- `Columnar vs Row Storage` — Parquet's columnar layout is
  orthogonal to format but enabled by binary encoding

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Agreed text encoding for exchanging       │
│              │ structured data between systems           │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Systems speaking different internal        │
│ SOLVES       │ representations need a common language    │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Human-readability costs 3–10× size vs     │
│              │ binary formats; choose accordingly        │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ JSON: APIs; CSV: tabular exports;         │
│              │ XML: legacy enterprise; YAML: configs     │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ High-volume data pipelines — use binary   │
│              │ formats (Avro, Parquet) instead           │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Human readability vs compactness          │
│              │ and parse speed                           │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "JSON won APIs; Parquet won analytics;    │
│              │  CSV won spreadsheets; XML won lawyers."  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Binary Formats → Serialization Formats →  │
│              │ Schema Registry                           │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A financial services firm transfers 50 GB of trade
records daily from an upstream bank using XML (ISO 20022
standard). The receiving system must store and query these in a
data warehouse. Describe the complete pipeline from XML ingestion
to queryable columnar storage, explain why each transformation
step exists, and identify precisely where data loss or type
coercion risks appear.

**Q2.** Both JSON and Avro can represent the same hierarchical
data. At 1 billion events per day in a Kafka topic, what is
the concrete cost difference in storage, network bandwidth, and
parse CPU between the two formats, and at what event rate does
the difference in a cloud bill justify a migration from JSON to
Avro?

