---
layout: default
title: "Data Formats (JSON, XML, YAML, CSV)"
parent: "Data Fundamentals"
nav_order: 499
permalink: /data-fundamentals/data-formats/
number: "499"
category: Data Fundamentals
difficulty: ★☆☆
depends_on: "Semi-Structured Data, Structured vs Unstructured Data"
used_by: "Binary Formats (Avro, Parquet, ORC), ETL pipelines, API design"
tags: #data, #json, #xml, #yaml, #csv, #data-formats, #serialization
---

# 499 — Data Formats (JSON, XML, YAML, CSV)

`#data` `#json` `#xml` `#yaml` `#csv` `#data-formats` `#serialization`

⚡ TL;DR — **JSON** is the web default (APIs, events). **XML** is the enterprise/B2B default (SOAP, financial). **YAML** is the config default (CI/CD, Kubernetes). **CSV** is the spreadsheet default (tabular bulk data). All are text-based, human-readable, and schema-optional — the baseline before considering binary formats (Avro, Parquet).

| #499            | Category: Data Fundamentals                                    | Difficulty: ★☆☆ |
| :-------------- | :------------------------------------------------------------- | :-------------- |
| **Depends on:** | Semi-Structured Data, Structured vs Unstructured Data          |                 |
| **Used by:**    | Binary Formats (Avro, Parquet, ORC), ETL pipelines, API design |                 |

---

### 📘 Textbook Definition

**JSON (JavaScript Object Notation)**: a lightweight, text-based data-interchange format. Supports: strings, numbers, booleans, null, arrays, and nested objects. Key-value pairs with keys always as strings. Spec: RFC 8259. Encoding: UTF-8. Use cases: REST APIs, event streaming (Kafka), configuration, NoSQL documents.

**XML (eXtensible Markup Language)**: a tag-based hierarchical format. Verbose: every value has an opening and closing tag. Supports attributes and namespaces. Schema validation via XSD. Transformation via XSLT. Use cases: SOAP web services, financial data (FIX, SWIFT, SEPA), healthcare (HL7, FHIR), enterprise B2B integration.

**YAML (YAML Ain't Markup Language)**: a human-readable data serialization format. Superset of JSON (valid JSON is valid YAML). Uses indentation (significant whitespace) instead of braces. Supports anchors and aliases (reference reuse). Use cases: configuration files (Kubernetes, CI/CD, dbt, Helm charts, Docker Compose).

**CSV (Comma-Separated Values)**: plain text tabular format. One row per line; delimiter-separated fields (comma, tab, pipe). No schema, no nesting, no types. RFC 4180. Use cases: bulk data export/import, spreadsheets, data science input files, legacy system integration.

---

### 🟢 Simple Definition (Easy)

The same data in four formats:

```
JSON:    {"name": "Alice", "age": 30, "city": "Seattle"}
XML:     <person><name>Alice</name><age>30</age><city>Seattle</city></person>
YAML:    name: Alice
         age: 30
         city: Seattle
CSV:     Alice,30,Seattle
```

All represent the same information. JSON: web. XML: enterprise. YAML: config. CSV: spreadsheets and bulk export.

---

### 🔵 Simple Definition (Elaborated)

The choice of format is determined by the ecosystem and use case:

- **JSON**: default for any HTTP API built after 2010. Compact, fast to parse, natively supported in JavaScript. Every language has a JSON library. Natively stored in MongoDB (BSON), Redis, DynamoDB.

- **XML**: the pre-JSON default. Still mandatory in financial services (SWIFT MT/MX, ISO 20022), healthcare (HL7 v2, FHIR), government, and SOAP services. Verbose but supports XSD schema validation, XSLT transformation, and XPath queries — a mature ecosystem.

- **YAML**: the config file format of the cloud-native era. Kubernetes manifests, GitHub Actions workflows, GitLab CI, dbt project config, Helm charts. More readable than JSON for multi-line config. Famous footgun: significant whitespace (indentation errors are silent/hard to debug).

- **CSV**: the lowest common denominator for tabular data. No standard for: header row presence, quoting rules, delimiter choice, encoding. But every tool reads it: Excel, Python pandas, Spark, SQL `COPY` commands. Used for bulk data exports, data science training sets, legacy migrations.

---

### 🔩 First Principles Explanation

```
DETAILED FORMAT COMPARISON:

  FEATURE          │ JSON        │ XML           │ YAML        │ CSV
  ─────────────────┼─────────────┼───────────────┼─────────────┼──────────────
  Human-readable   │ ✅ Yes      │ ⚠️ Verbose   │ ✅ Best     │ ✅ Simple
  Nesting          │ ✅ Objects  │ ✅ Elements   │ ✅ Dicts    │ ❌ Flat only
  Arrays           │ ✅ []       │ ✅ Repeated   │ ✅ - items  │ ❌ Not native
  Types            │ Partial*    │ String only** │ Partial*    │ ❌ None
  Schema support   │ JSON Schema │ XSD           │ None        │ None
  Comments         │ ❌ None     │ <!-- -->       │ # hash      │ None
  Namespace        │ ❌ None     │ ✅ xmlns:     │ ❌ None     │ ❌ None
  Binary encoding  │ ❌ Text     │ ❌ Text       │ ❌ Text     │ ❌ Text
  Compression      │ gzip/zstd   │ gzip/zstd     │ gzip        │ gzip/zstd
  Streaming parse  │ ✅ jq,gjson │ ✅ SAX        │ ❌ Hard     │ ✅ row-by-row

  * JSON has types: string, number, boolean, null, array, object
    BUT: no distinction between int and float at spec level
    AND: no Date type → dates as strings → parsing inconsistency
  ** XML attributes can carry structured data but everything is text

JSON STRUCTURE:
  {
    "key": "string value",          // string
    "count": 42,                    // number (int or float, same type)
    "price": 19.99,                 // number
    "active": true,                 // boolean
    "metadata": null,               // null
    "tags": ["sale", "featured"],   // array
    "address": {                    // nested object
      "city": "Seattle",
      "zip": "98101"
    }
  }

XML STRUCTURE:
  <?xml version="1.0" encoding="UTF-8"?>
  <product xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
           xsi:noNamespaceSchemaLocation="product.xsd">
    <name>Widget A</name>
    <price currency="USD">19.99</price>  <!-- attribute: currency -->
    <tags>
      <tag>sale</tag>
      <tag>featured</tag>
    </tags>
    <address>
      <city>Seattle</city>
      <zip>98101</zip>
    </address>
  </product>

  Note: attributes (currency="USD") vs elements (<city>) distinction
  XSD validates structure; XSLT transforms to other formats; XPath queries

YAML STRUCTURE:
  product:
    name: Widget A
    price: 19.99
    currency: USD
    active: true
    tags:
      - sale
      - featured
    address:
      city: Seattle
      zip: "98101"  # quoted to prevent interpretation as int

  YAML GOTCHAS:
  - Significant whitespace: mix tabs/spaces → parse error
  - YAML 1.1 (PyYAML default): "yes"/"no" → boolean (!) → use quotes
  - Large YAML files: easy to have merge errors; use yamllint
  - Security: yaml.load() (unsafe, allows arbitrary code execution!)
    ALWAYS use yaml.safe_load() in Python

CSV STRUCTURE:
  id,name,amount,date
  1001,Alice,149.99,2024-01-15
  1002,Bob,89.50,2024-01-15

  CSV GOTCHAS:
  - No standard: some use tab (TSV), pipe (|), semicolon
  - Quoting: fields with commas must be quoted: "Smith, John"
  - No encoding standard: UTF-8 vs Latin-1 → character corruption
  - No type info: amount "149.99" is a string; 149.99 is a float
    Parser must infer or be told the type
  - No nested structures → must flatten or use multiple files
  - No null vs empty string distinction (unless convention: "" vs ,, )

PERFORMANCE AT SCALE:

  100M records comparison (estimated):

  Format    │ Raw size  │ gzip size │ Parse time (Spark)
  ──────────┼───────────┼───────────┼────────────────────
  CSV       │ 8 GB      │ 1.5 GB    │ Baseline
  JSON      │ 16 GB     │ 2.5 GB    │ 3-5x slower than CSV
  XML       │ 40 GB     │ 4 GB      │ 10-20x slower than CSV
  Parquet   │ 1 GB      │ n/a*      │ 10-50x faster than CSV
  Avro      │ 2 GB      │ 1.2 GB    │ 2-3x faster than CSV

  * Parquet is already compressed internally (snappy/zstd/gzip)

  Conclusion: text formats (JSON/XML/CSV) are for interchange.
  Binary formats (Parquet/Avro/ORC) are for storage and analytics.
  Convert at ingest time.
```

---

### ❓ Why Does This Exist (Why Before What)

Data must be serialized to cross system boundaries: over HTTP, written to disk, sent over Kafka, exported from a database. Different ecosystems standardized on different formats based on historical context: XML predates JSON (XML: 1996; JSON: 2001); YAML grew from the DevOps tooling ecosystem; CSV has been the lingua franca of tabular data since spreadsheets. Understanding each format's trade-offs prevents: choosing JSON for analytics (performance disaster), using CSV for nested data (not possible), using YAML for high-throughput event streaming (wrong tool).

---

### 🧠 Mental Model / Analogy

> **Four ways to ship furniture**: **CSV** is flat-pack (IKEA) — everything disassembled, every piece labeled with a number, no nesting possible, but extremely space-efficient and universally understood. **JSON** is a labeled moving box — items grouped logically, some boxes inside boxes, every item labeled. **XML** is formal white-glove moving service — every item wrapped, tagged, re-tagged, with a manifest, namespace certification, and insurance documentation. **YAML** is a hand-drawn map of the room layout — human-readable, intuitive, but if you mis-draw one line, the furniture goes in the wrong place.

---

### ⚙️ How It Works (Mechanism)

```
PARSING STRATEGIES:

  JSON: streaming parsers (jq, GJSON) for large files
  → jq '.[] | select(.event=="purchase") | .amount' events.json
  → Python: json.loads() (in-memory) or ijson (streaming)

  XML: DOM (load entire tree) vs SAX (streaming event-based)
  → DOM: easy to use, high memory for large files
  → SAX: low memory, event-driven, complex code
  → Java: javax.xml.parsers.DocumentBuilder (DOM) or SAXParser (SAX)

  YAML: single-pass; load entire document into memory
  → Python: yaml.safe_load(file) → dict
  → Never use yaml.load() (unsafe: can execute arbitrary Python)

  CSV: line-by-line; very low memory
  → Python: csv.DictReader (handles quoting, escaping)
  → Spark: spark.read.option("header","true").csv("s3://...")
```

---

### 🔄 How It Connects (Mini-Map)

```
Data crosses a system boundary (API, file export, event stream)
        │
        ▼
Data Formats (JSON, XML, YAML, CSV) ◄── (you are here)
        │
        ├── Semi-Structured Data: JSON/XML are semi-structured
        ├── Binary Formats (Avro, Parquet, ORC): replace text formats for storage
        ├── ETL pipelines: text format → binary format conversion
        ├── REST APIs: JSON as default wire format
        └── SOAP / B2B Integration: XML as wire format
```

---

### 💻 Code Example

```python
import json, csv, yaml
from io import StringIO

# JSON: parse and extract
raw_json = '{"user":"Alice","orders":[{"id":"O1","total":149.99},{"id":"O2","total":89.50}]}'
data = json.loads(raw_json)
total = sum(o["total"] for o in data["orders"])  # 239.49

# CSV: parse with headers, handle quoting
csv_data = 'id,name,amount\n1001,"Smith, John",149.99\n1002,Alice,89.50'
reader = csv.DictReader(StringIO(csv_data))
for row in reader:
    print(row["name"], float(row["amount"]))
# Smith, John 149.99  ← correctly handles embedded comma

# YAML: safe_load config file
config_yaml = """
database:
  host: db.example.com
  port: 5432
  name: orders
feature_flags:
  new_checkout: true
  beta_users: [alice, bob]
"""
config = yaml.safe_load(config_yaml)  # ALWAYS safe_load
db_host = config["database"]["host"]  # "db.example.com"

# XML: parse with ElementTree
import xml.etree.ElementTree as ET
xml_data = '<order><id>O001</id><amount currency="USD">149.99</amount></order>'
root = ET.fromstring(xml_data)
order_id = root.find("id").text          # "O001"
amount = float(root.find("amount").text) # 149.99
currency = root.find("amount").attrib["currency"]  # "USD"
```

---

### ⚠️ Common Misconceptions

| Misconception              | Reality                                                                                                                                                                                                                                                                                                                                                             |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| JSON has a Date type       | JSON has no Date type. Dates are represented as strings (ISO 8601: `"2024-01-15T14:23:00Z"`) or Unix timestamps (numbers). Every consuming system must agree on the format. This is a common source of bugs when systems disagree on UTC vs local time or timestamp precision.                                                                                      |
| YAML is just readable JSON | YAML has significantly more features: anchors/aliases, block vs flow style, multi-line strings, multiple document types. It's also a superset of JSON, meaning valid JSON is valid YAML. But YAML 1.1 (the default in most parsers) has notorious implicit type coercions: `yes`/`no`/`on`/`off` → boolean; `3:00` → 180 (seconds). Always quote ambiguous strings. |
| CSV is simple and safe     | CSV has no formal standard for: quoting, encoding, null values, or header presence. A "CSV" from Excel may use semicolons (European locale), Latin-1 encoding, and Windows line endings. Always specify `encoding`, `delimiter`, and `quoting` parameters explicitly when reading CSV files in production pipelines.                                                |

---

### 🔥 Pitfalls in Production

```
PITFALL: yaml.load() remote code execution vulnerability

  # ❌ DANGEROUS: arbitrary Python execution via YAML
  import yaml
  malicious = "!!python/object/apply:os.system ['rm -rf /']"
  result = yaml.load(malicious)  # EXECUTES THE COMMAND

  # ✅ SAFE: always use safe_load
  result = yaml.safe_load(malicious)
  # → raises yaml.constructor.ConstructorError: could not determine a constructor

PITFALL: CSV encoding corruption in international data

  # ❌ PROBLEM: reading UTF-8 file as Latin-1
  df = pd.read_csv("data.csv")  # default encoding: platform-dependent
  # "Müller" → "MÃ¼ller" (garbled)

  # ✅ FIX: always specify encoding explicitly
  df = pd.read_csv("data.csv", encoding="utf-8-sig")  # handles BOM from Excel
  # or
  df = pd.read_csv("data.csv", encoding="utf-8")

PITFALL: JSON number precision loss with large integers

  # JavaScript/JSON: numbers are IEEE 754 double-precision floating-point
  # Maximum safe integer: 2^53 - 1 = 9007199254740991 (16 digits)

  # 18-digit Snowflake/Twitter ID: 123456789012345678
  # As JSON number: loses precision → 123456789012345680 (wrong!)

  # FIX: represent large IDs as strings in JSON
  {"id": "123456789012345678", "id_as_int": 123456789012345678}
  # String: exact. Number: potentially imprecise in JS parsers.
```

---

### 🔗 Related Keywords

- `Semi-Structured Data` — JSON/XML are the primary semi-structured formats
- `Binary Formats (Avro, Parquet, ORC, Protobuf)` — binary alternatives for performance at scale
- `Avro` — binary semi-structured format replacing JSON for high-throughput Kafka pipelines
- `Parquet` — columnar binary format replacing CSV/JSON for analytics storage
- `REST APIs` — JSON as the default wire format; content negotiation

---

### 📌 Quick Reference Card

```
┌──────────┬──────────┬──────────┬──────────┬──────────────┐
│          │ JSON     │ XML      │ YAML     │ CSV          │
├──────────┼──────────┼──────────┼──────────┼──────────────┤
│ Use for  │ APIs,    │ SOAP,    │ Config,  │ Tabular bulk │
│          │ events   │ B2B,     │ CI/CD,   │ export,      │
│          │          │ HL7/FHIR │ Helm     │ spreadsheets │
│ Nesting  │ ✅       │ ✅       │ ✅       │ ❌           │
│ Types    │ Partial  │ None     │ Partial  │ None         │
│ Schema   │ Optional │ XSD      │ None     │ None         │
│ Gotcha   │ No Date  │ Verbose  │ indent!  │ No standard  │
│ Replace  │ → Avro   │ → Avro   │ n/a      │ → Parquet    │
│  with... │ at scale │ at scale │          │ for analytics│
└──────────┴──────────┴──────────┴──────────┴──────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A financial services company exchanges payment data with partners. Some partners send SOAP/XML (ISO 20022 format); others send REST/JSON. How would you design a data ingestion layer that accepts both formats and normalizes them into a single internal structured format (Parquet/Avro) for analytics? What are the schema mapping challenges?

**Q2.** Large Language Models (LLMs) are increasingly used to extract structured data from unstructured text and generate JSON/XML responses. What are the risks of relying on LLM-generated JSON for production pipelines? How would you validate and sanitize LLM output before it enters a data pipeline? What format is better for LLM output — JSON or YAML — and why?
