---
layout: default
title: "Serialization Formats"
parent: "Data Fundamentals"
nav_order: 509
permalink: /data-fundamentals/serialization-formats/
number: "0509"
category: Data Fundamentals
difficulty: ★★☆
depends_on: Data Formats, Binary Formats, Data Types, HTTP and APIs
used_by: Schema Registry, Avro, Protobuf, Microservices, Distributed Systems
related: Data Formats (JSON, XML, YAML, CSV), Binary Formats, Avro, Schema Registry
tags:
  - dataengineering
  - intermediate
  - api
  - distributed
  - performance
---

# 509 — Serialization Formats

⚡ TL;DR — Serialization is the process of converting in-memory objects into a byte sequence for storage or transmission — the format chosen determines speed, size, compatibility, and debuggability.

| #509 | Category: Data Fundamentals | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Data Formats, Binary Formats, Data Types, HTTP and APIs | |
| **Used by:** | Schema Registry, Avro, Protobuf, Microservices, Distributed Systems | |
| **Related:** | Data Formats (JSON, XML, YAML, CSV), Binary Formats, Avro, Schema Registry | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A Java microservice receives an HTTP request and creates an `Order`
object in memory: a JVM object with pointers, class metadata,
heap references — a structure tied to a specific JVM process.
To send that `Order` to another service running Python on a
different host, you cannot pass the JVM memory bytes directly.
They're meaningless to a Python interpreter. You need a way to
convert the `Order` object into bytes that any language can
reconstruct into an equivalent `Order` representation.

**THE BREAKING POINT:**
In distributed systems, every service boundary requires data
to cross a language or process boundary. Without standardised
serialisation, each pair of services would need to agree on a
custom binary protocol — O(N²) custom parsers for N services.
Early enterprise systems like CORBA tried to solve this with
complex IDL (Interface Definition Language) but the overhead
was enormous.

**THE INVENTION MOMENT:**
This is exactly why serialisation formats emerged. JSON solved
this for web APIs: any language can produce and consume a JSON
string. Binary formats (Avro, Protobuf, Thrift, MessagePack)
solved it for high-performance pipelines where JSON's overhead
was too large. Each format is a contract: "here is how bytes
map to typed values."

---

### 📘 Textbook Definition

**Serialisation** is the process of converting an in-memory data
structure or object into a format (byte sequence or text string)
that can be stored, transmitted, and later reconstructed
(**deserialisation**) into an equivalent data structure — possibly
in a different language or process. A **serialisation format**
specifies the encoding rules: what bytes represent an integer,
string, nested object, or list. Text-based serialisation formats
(JSON, XML, YAML) produce human-readable output at the cost of
verbosity and parsing overhead. Binary serialisation formats
(Avro, Protobuf, Thrift, MessagePack, FlatBuffers) produce
compact, fast-to-parse output at the cost of human readability.
Schema-defined formats (Protobuf, Avro, Thrift) require a
pre-agreed schema; self-describing formats (JSON, MessagePack)
embed type information in the stream.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Serialisation turns objects into bytes so they can travel
between processes, languages, and machines.

**One analogy:**

> Imagine disassembling a piece of IKEA furniture to ship it.
> Serialisation is the disassembly — packing flat pieces into
> a box with an instruction manual. Deserialisation is the
> reassembly at the destination. Different formats are different
> disassembly strategies: some pack everything labelled (JSON),
> others pack only the pieces numbered by the manual (Protobuf).

**One insight:**
Every serialisation format makes a choice about where the schema
lives. In JSON, the schema is in the bytes themselves (field names
are strings embedded in every record). In Protobuf, the schema
is in a `.proto` file shared ahead of time — the bytes contain
only field numbers and values. This one choice has the largest
impact on size, speed, and forward-compatibility.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. An in-memory object must survive a round-trip (same logical
   value after serialise → transmit → deserialise).
2. Both parties (producer and consumer) must agree on the format.
3. The schema is always somewhere — it's either in the bytes
   (self-describing) or external (schema-on-read / schema-defined).

**DERIVED DESIGN:**

*Self-describing (JSON, MessagePack):*
Each record carries all type metadata. No external agreement
needed beyond "we're using JSON." Flexible. Verbose. Safe for
consumers that ignore unknown fields. Fragile when consumers
assume specific structure.

*Schema-defined binary (Protobuf, Thrift):*
Schema in `.proto` file. Fields identified by number, not name.
Field 3 (type int32) is `customer_id` according to the schema.
On the wire: `[field_tag: 3 bytes || value: 4 bytes]`. Field names
never transmitted — saves ~80% for name-heavy payloads. Consumer
reads schema from `.proto` to map field numbers to names.

*Schema + registry (Avro + Confluent Schema Registry):*
Schema defined in Avro JSON format. Schema registered with a
Schema Registry (gets schema ID = integer). Each Kafka message:
`[0x00][schema ID: 4 bytes][Avro-binary-payload]`. Consumer
looks up schema by ID. Schema evolution rules (backward,
forward, full compatibility) enforced by registry.

*In-memory format (FlatBuffers, Cap'n Proto):*
No parse step needed — memory layout IS the wire format.
`GetCustomerId()` reads directly from the message bytes at a
fixed offset. Zero-copy: no deserialisation allocation.
Used in high-performance game engines (FlatBuffers by Google),
storage systems, and inter-process communication.

**THE TRADE-OFFS:**

| Format | Schema Location | Size | Speed | Human-Readable | Evolution |
|---|---|---|---|---|---|
| JSON | Inline (field names) | Large | Moderate | Yes | Implicit |
| MessagePack | Inline (type tags) | Medium | Fast | No | Implicit |
| Protobuf | External (.proto) | Small | Very fast | No | Field numbers |
| Avro | Registry / header | Small | Very fast | No | Compatibility rules |
| FlatBuffers | External (.fbs) | Smallest | Zero-copy | No | Additive only |

---

### 🧪 Thought Experiment

**SETUP:**
A gRPC microservice sends 100 million customer records per day
between services. Each record has 5 fields: id (int64), name
(string, avg 10 chars), email (string, avg 20 chars),
created_at (int64 timestamp), active (boolean).

**WITH JSON:**
Average record: `{"id":1234567890,"name":"Alice Chen","email":"alice@example.com","created_at":1714608000000,"active":true}` = ~95 bytes.
100M records × 95 bytes = 9.5 GB/day. Parse: each byte must be
lexed (JSON tokeniser), field names matched (string comparison),
types coerced (string → int64 for id). At 1M records/s: parser
uses 1 CPU core.

**WITH PROTOBUF:**
```
// proto encoding for same record:
// field 1 (id): tag byte + varint = 1 + 8 bytes = 9
// field 2 (name): tag + length + 10 chars = 1 + 1 + 10 = 12
// field 3 (email): tag + length + 20 chars = 1 + 1 + 20 = 22
// field 4 (created_at): tag + varint = 1 + 8 = 9
// field 5 (active): tag + 1 byte = 2
// Total: ~54 bytes (vs 95 JSON)
```
100M records × 54 bytes = 5.4 GB/day (43% smaller).
Parse: field_tag → 1 byte read; varint → 1-8 bytes; struct.
At 1M records/s: 0.2 CPU cores. 5× faster than JSON parsing.

**THE INSIGHT:**
For 100M records/day, the format choice is a $1,000/month
infrastructure decision (storage + compute). For 100 billion
records/day, it's a $1,000,000/month decision. At scale, the
format IS the cost.

---

### 🧠 Mental Model / Analogy

> Serialisation formats differ on one crucial dimension: WHERE
> they store the schema. Think of shipping a custom jigsaw puzzle.
> JSON: each piece has its shape and label printed on it —
> no instruction needed, but pieces are bigger. Protobuf: pieces
> have only a number; the instruction manual (`.proto` file)
> is shared separately — smaller pieces, must have the manual.
> FlatBuffers: the box IS the assembled puzzle, with a transparent
> window — no disassembly, no reassembly, just look through the
> window directly.

- "Labelled pieces" → JSON (field names in payload)
- "Numbered pieces + manual" → Protobuf (field numbers + .proto)
- "Transparent window box" → FlatBuffers (zero-copy memory layout)
- "Numbered pieces + shared registry" → Avro + Schema Registry
- "Anyone can read labelled pieces" → JSON (schema-free interop)
- "Must have the manual to read numbered pieces" → Protobuf

**Where this analogy breaks down:** FlatBuffers doesn't eliminate
schema — you still need the `.fbs` schema file to generate accessor
code. The "transparent window" means zero runtime parse, but the
schema is just as mandatory as in Protobuf.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Serialisation is packing data into a format that can travel
across a network or be saved to a file. Deserialisation is
unpacking it back into usable form. Every time your app sends
data to a server (e.g., a form submission), something is being
serialised. The format chosen (JSON, binary, etc.) determines
how big the package is and how fast it's assembled/disassembled.

**Level 2 — How to use it (junior developer):**
For REST APIs: use JSON. For gRPC services: use Protobuf (define
`.proto` file, run `protoc` to generate code). For Kafka: use
Avro with Schema Registry. For configuration: YAML or JSON. For
database serialisation (storing objects): use frameworks like
Jackson (Java), `pickle` (Python — never across trust boundaries),
or `msgpack`. Always validate deserialised input — never trust
that incoming bytes match the expected schema.

**Level 3 — How it works (mid-level engineer):**
Protobuf wire format: each field is a TLV (Tag-Length-Value) tuple.
The tag encodes `(field_number << 3) | wire_type`. Wire types:
0=varint, 1=64-bit, 2=length-delimited, 5=32-bit. A varint
uses 7 bits per byte; the MSB (most significant bit) signals
"more bytes follow". So integers 1–127 take 1 byte; 128–16383
take 2 bytes. Strings are length-delimited (wire type 2): tag
byte, varint length, then raw bytes. Unknown fields are preserved
by the parser and re-emitted on serialisation — enabling forward
compatibility (new consumers that don't know new fields still
keep them when forwarding).

JSON parse pipeline: lexer → tokeniser → DOM/SAX → application
objects. The slowest step is DOM allocation (every field =
a heap-allocated string). SAX (event-driven) avoids DOM but
requires more complex consumer code.

**Level 4 — Why it was designed this way (senior/staff):**
The history of serialisation is a history of lessons learned.
Sun RPC's XDR (1987) was the first standardised binary format —
simple but not self-describing. CORBA's CDR (1991) added IDL
for cross-language support — overly complex. Java Serialisation
(1997) made objects serialisable automatically — but was
language-locked and had catastrophic security vulnerabilities
(deserialisation gadget chains led to arbitrary code execution).
Apache Thrift (Facebook, 2007) and Protobuf (Google, 2008) were
designed specifically for large-scale internal microservice
communication: fast, schema-defined, forward/backward compatible.
Avro (2009) added schema-in-file for Hadoop's write-once/read-many
model. FlatBuffers (2014) addressed embedded systems and game
engines where dynamic allocation was unacceptable. JSON won the
web API battle not on technical merit but on simplicity of
adoption: `JSON.parse()` in every browser. The 2020s trend:
Protobuf for gRPC (synchronous service calls), Avro for async
streams (Kafka), and a third option emerging — Apache Arrow
IPC format for columnar in-memory analytics data sharing.

---

### ⚙️ How It Works (Mechanism)

**Protobuf wire format encoding:**
```
Proto definition:
  message Customer {
    int64  id         = 1;
    string name       = 2;
    bool   active     = 3;
  }

Encoded "Customer{id:1001, name:'Alice', active:true}":

  Field 1 (id=1001, wire_type=0 varint):
    Tag byte: (1 << 3) | 0 = 0x08
    Varint(1001) = 0xE9 0x07 (2 bytes: 1001 > 127)
  → bytes: 08 E9 07

  Field 2 (name='Alice', wire_type=2 length-delimited):
    Tag byte: (2 << 3) | 2 = 0x12
    Length varint: 5
    'Alice' = 41 6C 69 63 65
  → bytes: 12 05 41 6C 69 63 65

  Field 3 (active=true, wire_type=0 varint):
    Tag byte: (3 << 3) | 0 = 0x18
    Varint(1) = 0x01
  → bytes: 18 01

  Total: 12 bytes
  (JSON equivalent: {"id":1001,"name":"Alice","active":true} = 43 bytes)
```

**Format comparison for the same data:**
```
┌─────────────────────────────────────────────────────┐
│ Format      │ Size for above Customer record        │
├─────────────┼───────────────────────────────────────┤
│ JSON        │ 43 bytes                              │
│ MessagePack │ 31 bytes (binary JSON variant)        │
│ Protobuf    │ 12 bytes (72% smaller than JSON)      │
│ FlatBuffers │ 48 bytes (larger! vtable overhead)    │
│ Avro        │ 14 bytes (similar to protobuf)        │
└─────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 — Protobuf serialisation (Python):**
```python
# customer.proto:
# syntax = "proto3";
# message Customer {
#   int64 id = 1;
#   string name = 2;
#   bool active = 3;
# }
# Compile: protoc --python_out=. customer.proto

import customer_pb2

# Serialise
c = customer_pb2.Customer(id=1001, name="Alice", active=True)
data = c.SerializeToString()  # 12 bytes
print(len(data))  # 12

# Deserialise
c2 = customer_pb2.Customer()
c2.ParseFromString(data)
print(c2.name)  # "Alice"
```

**Example 2 — JSON vs Protobuf benchmark:**
```python
import json, time, customer_pb2

record = {"id": 1001, "name": "Alice Chen", "active": True}
proto = customer_pb2.Customer(id=1001, name="Alice Chen", active=True)

N = 1_000_000

# JSON serialise
t0 = time.time()
for _ in range(N):
    json.dumps(record)
print(f"JSON:  {time.time()-t0:.2f}s for {N} records")

# Protobuf serialise
t0 = time.time()
for _ in range(N):
    proto.SerializeToString()
print(f"Proto: {time.time()-t0:.2f}s for {N} records")
# Typical result:
# JSON:  4.20s
# Proto: 0.75s  (~5.6x faster)
```

**Example 3 — Schema evolution safety:**
```python
# v1 proto: Customer{id, name, active}
# v2 proto: Customer{id, name, active, email=3}
# (added new field with new field number)

# Consumer using v1 schema reads v2 message:
c = customer_pb2_v1.Customer()
c.ParseFromString(v2_bytes)
# email field (tag=3) is an unknown field — stored but ignored
print(c.name)  # works fine
# Forward compatible: v1 consumer reads v2 data safely

# Consumer using v2 schema reads v1 message:
c = customer_pb2_v2.Customer()
c.ParseFromString(v1_bytes)
print(c.email)  # "" (zero value) — email absent in v1 data
# Backward compatible: v2 consumer reads v1 data safely
```

---

### ⚖️ Comparison Table

| Format | Schema Needed | Size | Speed | Human-Readable | Best For |
|---|---|---|---|---|---|
| **JSON** | No | Large | Moderate | Yes | REST APIs, configs |
| MessagePack | No | Medium | Fast | No | When JSON is too big |
| **Protobuf** | Yes (.proto) | Small | Very fast | No | gRPC, service-to-service |
| **Avro** | Yes (registry) | Small | Very fast | No | Kafka streaming |
| Thrift | Yes (.thrift) | Small | Very fast | No | Cross-language RPC |
| FlatBuffers | Yes (.fbs) | Varies | Zero-copy | No | Embedded, game engines |

**How to choose:** REST/public APIs → JSON. Internal gRPC
microservices → Protobuf. Kafka event streaming → Avro.
High-frequency analytics inter-process → Arrow IPC.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Serialisation is just JSON.stringify | JSON is one serialisation format; binary formats are 3–10× smaller and faster for the same data |
| Java Serializable is safe | Java's built-in serialisation (`implements Serializable`) has been a major source of remote code execution CVEs; never deserialise untrusted Java objects |
| All serialisation formats are equally forward-compatible | JSON ignores unknown fields in most parsers; Protobuf preserves them; Avro drops unknown fields by default (configurable). These differ critically for API versioning |
| Smaller format = faster end-to-end | If the bottleneck is CPU (parsing), smaller and simpler format wins. If bottleneck is I/O, compression matters more than raw format size |
| Schema definition is a burden | Schema definition prevents a whole class of integration bugs (type mismatches, field renames, missing required fields) — it's actually liability reduction, not overhead |

---

### 🚨 Failure Modes & Diagnosis

**Java Serialisation RCE Gadget Chain**

**Symptom:**
Application receives unexpected HTTP requests or executes
arbitrary commands after deserialising a `POST /data` payload.
CVE patterns in log files from deserialization exploit tools.

**Root Cause:**
Java's native serialisation allows serialised objects to execute
`readObject()` on deserialisation. Attacker crafts a payload
using a gadget chain (e.g., Commons Collections) that executes
arbitrary code when deserialised.

**Diagnostic Command / Tool:**
```bash
# Scan for Java deserialization vulnerabilities
ysoserial --help  # attacker tool you need to know about
# Defensive: look for ObjectInputStream usage
grep -r "ObjectInputStream" src/ --include="*.java"
```

**Fix:**
Never use Java native serialisation for untrusted input.
Replace with JSON, Protobuf, or Avro.

**Prevention:**
Apply `java.io.ObjectInputFilter` to restrict allowed classes.
Prefer JSON/Protobuf/Avro for all external-facing APIs.

---

**Protobuf Field Number Reuse Breaking Compatibility**

**Symptom:**
After a proto schema update, consumers receive garbled data for
a field — the `customer_id` field contains timestamps.

**Root Cause:**
An engineer deleted field number 2 (`customer_id`) and later
reused field number 2 for a new field (`last_updated_at`).
Old messages on wire still have field number 2 = customer_id
integer. New consumer interprets field 2 as `last_updated_at`
timestamp — same number, different semantic = silent corruption.

**Diagnostic Command / Tool:**
```bash
# Inspect field numbers in proto file
grep -n "= [0-9]\+;" customer.proto
# Verify no field number appears twice — use reserved
```

**Fix:**
Never reuse field numbers. Mark deleted field numbers as reserved:
```protobuf
message Customer {
  reserved 2;  // was customer_id — do not reuse
  reserved "customer_id";  // also reserve the name
  int64 id = 1;
  int64 last_updated_at = 3;  // use NEW number
}
```

**Prevention:**
Add `reserved` declarations for ALL deleted fields in CI.
Use `buf breaking` tool to enforce breaking change detection.

---

**MessagePack Integer Overflow Across Languages**

**Symptom:**
Java service sends a `long` (int64) value `9876543210` via
MessagePack. JavaScript consumer receives `9876543216` (wrong).

**Root Cause:**
MessagePack defines integer types by value range: if the value
fits in int32, it uses 4 bytes. If the JS MessagePack library
decodes a 64-bit integer and JavaScript `Number` loses precision
(> 2^53), the value is silently truncated.

**Diagnostic Command / Tool:**
```javascript
const msgpack = require('msgpack5')();
const buf = /* bytes from Java */;
const val = msgpack.decode(buf);
// log typeof val, val — check for numeric precision loss
```

**Fix:**
Use BigInt types in JavaScript for int64 values, or serialise
large integers as strings.

**Prevention:**
Define cross-language precision rules in the data contract.
All IDs and timestamps > int32 must be tested in all consuming
languages.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Data Formats (JSON, XML, YAML, CSV)` — the text-based
  serialisation formats that are the most common starting point
- `Binary Formats (Avro, Parquet, ORC, Protobuf)` — the
  binary serialisation formats optimised for scale
- `Data Types` — serialisation formats encode typed values;
  understanding types explains encoding choices

**Builds On This (learn these next):**
- `Schema Registry` — manages versions of Avro serialisation
  schemas across producers and consumers
- `Avro` — the streaming-optimised binary serialisation format
  with built-in schema evolution via Schema Registry
- `Microservices` — service-to-service communication requires
  choosing a serialisation format for inter-service contracts

**Alternatives / Comparisons:**
- `Data Formats (JSON, XML, YAML, CSV)` — the text-based
  alternative; simpler, human-readable, less efficient
- `Data Compression` — orthogonal: applies on top of any
  serialisation format to further reduce byte size
- `Binary Formats` — the broader category; serialisation
  formats are a subset that includes both text and binary

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Converting in-memory objects to bytes     │
│              │ for transmission or storage               │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Objects are process-local; bytes can      │
│ SOLVES       │ cross language and network boundaries     │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Where the schema lives determines size,   │
│              │ speed, and forward-compatibility          │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Any time data crosses a service, process, │
│              │ or host boundary                          │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Java native Serializable for untrusted    │
│              │ input — severe security vulnerability     │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Human readability vs size/speed           │
│              │ (JSON vs Protobuf/Avro)                   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "JSON wears a name badge; Protobuf        │
│              │  uses employee numbers."                  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Schema Registry → Avro → Protobuf         │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A microservice ecosystem has 50 services all communicating
via JSON over HTTP/2. The team wants to migrate to Protobuf for
performance. The migration must not break any existing consumer
during a 6-month rolling deployment. Given that Protobuf and
JSON have completely different wire representations, describe the
dual-serialisation strategy that enables a 6-month gradual
migration, what happens when a v1 (JSON) consumer receives a
Protobuf message, and how you detect migration completion without
a big-bang cutover.

**Q2.** You are building a high-frequency trading system that
processes 10 million order events per second. Each event is 200
bytes serialised. The architecture must choose between JSON
(no schema coordination), Protobuf (`.proto` file compiled into
generated code), and FlatBuffers (zero-copy read). Compute the
approximate CPU cycles consumed by deserialization for each format
at 10M events/s on a 3 GHz 16-core machine, and explain which
format choice is architecturally correct given that 95% of
events only read 2 of 20 fields.

