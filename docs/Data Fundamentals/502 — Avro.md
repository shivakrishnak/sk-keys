---
layout: default
title: "Avro"
parent: "Data Fundamentals"
nav_order: 502
permalink: /data-fundamentals/avro/
number: "0502"
category: Data Fundamentals
difficulty: ★★☆
depends_on: Binary Formats, Serialization Formats, Schema Registry, Apache Kafka
used_by: Schema Registry, Schema Evolution, Kafka Streams, Data Lake
related: Parquet, Protobuf, Schema Registry, Schema Evolution, Data Formats
tags:
  - dataengineering
  - streaming
  - intermediate
  - bigdata
  - kafka
---

# 502 — Avro

⚡ TL;DR — Avro is a compact binary serialisation format designed for Kafka and Hadoop that stores its schema alongside data, enabling schema evolution without breaking consumers.

| #502 | Category: Data Fundamentals | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Binary Formats, Serialization Formats, Schema Registry, Apache Kafka | |
| **Used by:** | Schema Registry, Schema Evolution, Kafka Streams, Data Lake | |
| **Related:** | Parquet, Protobuf, Schema Registry, Schema Evolution, Data Formats | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A Kafka producer emits JSON events. All 12 consumer services
parse the JSON and extract fields. One day the producer team
renames `userId` to `user_id` for consistency. They deploy at
9 AM on a Tuesday. By 9:05 AM, all 12 consumers are silently
dropping `NULL` for the ID field. No error. The bug propagates
to 12 downstream databases and 5 dashboards before anyone notices.

**THE BREAKING POINT:**
In a distributed system with many producers and consumers, schema
changes are inevitable — and every change risks breaking
consumers. JSON has no formal schema enforcement. A renamed field
or a changed type is invisible until a consumer crashes or
silently corrupts data. With 50 services, one schema change per
week, and no coordination mechanism, you accumulate dozens of
undetected schema mismatches in your pipelines.

**THE INVENTION MOMENT:**
This is exactly why Avro (with Schema Registry) was created.
Avro enforces that every message is validated against a registered
schema before it enters the topic. Schema compatibility is checked
on every change — backward, forward, or full compatibility rules
block breaking changes at the producer, not the consumer.

---

### 📘 Textbook Definition

**Apache Avro** is a language-neutral binary serialisation system
originally developed for Apache Hadoop. An Avro schema is defined
in JSON format and describes the data types and field names. Avro
stores the schema reference (or full schema) with data — typically
in a file header (for data files) or as a schema ID reference
(for Kafka messages, managed by Schema Registry). Avro uses
a compact binary encoding: fields are written in schema-declared
order with no field names in the binary payload. Avro natively
supports schema evolution through field defaults, optional fields
(`null` union types), and the schema compatibility model enforced
by Confluent Schema Registry.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Avro packs data as binary bytes with the schema stored once — not
repeated in every message.

**One analogy:**

> Imagine shipping furniture flat-packed. Without Avro: you ship
> every piece of furniture with a full instruction manual taped
> to each plank. With Avro: you register the instruction manual
> once at the warehouse (Schema Registry) and every shipment
> carries only a reference number (schema ID). Less weight,
> same information.

**One insight:**
The critical insight is the separation of schema from data. In
JSON the schema (field names) travels with every message.
In Avro the schema lives in the registry; the message carries
only a 4-byte schema ID + binary field values. At 1 billion
messages per day, storing field names in the binary payload
vs storing them once in a registry is the difference between
90 GB and 20 GB per day.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Every producer must declare the schema before writing.
2. Every consumer must have access to the same schema to decode.
3. Schema evolution must be predictable: old consumers must be
   able to read new data (backward); new consumers must read
   old data (forward).

**DERIVED DESIGN:**
Given invariant 1+2: Avro cannot be self-contained per message
(unlike JSON). It requires a shared schema store. In Kafka, this
is the Confluent Schema Registry: a REST service that assigns a
sequential integer ID to each schema version. The producer
serialises the message as:
`[0x00][schema_id: 4 bytes][binary data]`
The consumer reads the 4-byte schema ID, fetches the
corresponding schema (cached after first fetch), then uses
it to decode the binary data.

Given invariant 3: Avro defines compatibility rules. Backward
compatibility means new schema can read old messages. Forward
compatibility means old schema can read new messages. Full
compatibility means both. Rules enforce:
- Adding a field with a default: BACKWARD compatible
  (old consumers ignore the new field using the default)
- Removing a field: FORWARD compatible only if new consumers
  can handle missing values

**THE TRADE-OFFS:**
**Gain:** Compact binary encoding; schema enforcement at
producer; schema evolution with compatibility guarantees;
native Hadoop/Kafka integration.
**Cost:** Not human-readable; requires Schema Registry dependency;
schema management adds operational complexity.

---

### 🧪 Thought Experiment

**SETUP:**
A banking Kafka topic `transactions` has 15 consumer services.
The producer team wants to add a new required field:
`risk_score: float`.

**WITHOUT AVRO (JSON topic):**
1. Producer deploys — messages now include `"risk_score": 0.85`.
2. All 15 consumers continue reading fine (JSON ignores unknown
   fields in most parsers).
3. BUT: some consumers use strict JSON parsing: they fail with
   `UnexpectedFieldException`.
4. Three consumers use JavaScript that auto-coerces the float
   to a string → silent type error.
5. There is no way to know which consumers broke until you check
   all 15 individually. No central enforcement.

**WITH AVRO + SCHEMA REGISTRY:**
1. Producer registers new schema version with `risk_score` field.
2. Schema Registry checks: is `risk_score` backward compatible?
   No default value → backward incompatible → **REJECTED**.
3. Producer adds `"default": 0.0` to make it backward compatible.
4. Schema Registry accepts v2. Old consumers using v1 still read
   v2 messages — `risk_score` defaults to 0.0 for them.
5. Migration is gradual; no consumer is broken.

**THE INSIGHT:**
Schema enforcement at the producer is a system boundary. It makes
incompatibility a deployment-time failure (visible, fast, fixable)
instead of a runtime failure (invisible, slow, downstream damage).

---

### 🧠 Mental Model / Analogy

> Think of Avro + Schema Registry as a government standards bureau
> for data shapes. Before publishing data, a producer registers
> the shape with the bureau. The bureau assigns an ID (say, #47)
> and issues a certificate. Every message says "I'm shape #47."
> Every consumer looks up shape #47 at the bureau and knows
> exactly how to interpret the bytes. If a producer tries to
> register a breaking shape change, the bureau rejects it until
> the change is backward compatible.

- "Bureau" → Schema Registry
- "Shape registration" → schema submission
- "ID certificate" → 4-byte schema ID in message header
- "Certified shape" → Avro schema (JSON definition)
- "Breaking change rejection" → compatibility check enforcement
- "Consumer looks up shape" → Schema Registry `GET /schemas/ids/47`

**Where this analogy breaks down:** The "bureau" is not always
Confluent Schema Registry — other implementations exist (Apicurio,
AWS Glue Schema Registry). The Avro specification itself does not
require a registry — only Kafka use cases do.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Avro is a way to compress data for sending between computer
systems. Instead of writing `"customer_id": 123` (18 characters),
Avro writes the number 123 in 4 bytes, with rules about what
each byte means stored separately. It's like a codebook: you
agree on the codebook once, then use it to decode the short
messages.

**Level 2 — How to use it (junior developer):**
Define your schema as a `.avsc` JSON file. Register it with
Schema Registry. Use `confluent_kafka.avro.AvroProducer` in Python
(or the Java `KafkaAvroSerializer`) to produce. The serialiser
validates your message against the schema before sending —
if a field is missing or the wrong type, it throws an exception
before the message reaches Kafka. Consumers use
`KafkaAvroDeserializer` which automatically fetches and caches
the schema.

**Level 3 — How it works (mid-level engineer):**
Avro binary encoding:
- `null` → 0 bytes
- `boolean` → 1 byte (0 or 1)
- `int`/`long` → variable-length zigzag encoding
  (small values use fewer bytes: 1 → `0x02`, -1 → `0x01`)
- `float`/`double` → IEEE 754, 4 or 8 bytes
- `string`/`bytes` → length (zigzag long) + bytes
- `array` → blocks: count (zigzag long) + items... repeat until
  count=0
- `record` → fields written in schema-declared order, no
  field name bytes

Schema evolution resolution: writer schema (producer's schema
at write time) and reader schema (consumer's schema) may differ.
The Avro library resolves field-by-field: if reader has a field
not in writer, use default; if writer has a field not in reader,
skip bytes; if types differ and are promotable (int→long), promote.

**Level 4 — Why it was designed this way (senior/staff):**
Avro was designed at Yahoo for Hadoop in 2009 as an alternative
to Thrift and Protocol Buffers that was more tightly integrated
with dynamic languages. The critical design decision: schema is
stored WITH the data (in the file header) rather than requiring
an external schema compiler (like Protobuf's `.proto` → generated
code). This enables dynamic reading without code generation —
a Python script can read any Avro file without knowing the schema
at compile time. For Kafka, this was extended: schema lives in
the Schema Registry; the 5-byte magic header is added by the
Confluent serialiser convention (not in the Avro spec itself).
This is an important distinction — the "Avro+Registry" pattern
is a Confluent convention, not IETF/Apache standard.

---

### ⚙️ How It Works (Mechanism)

**Avro file format (Hadoop, not Kafka):**
```
┌────────────────────────────────────────────────────────┐
│              AVRO FILE FORMAT                          │
├────────────────────────────────────────────────────────┤
│  Header:                                               │
│    - Magic bytes: "Obj\x01"                            │
│    - Metadata: {"avro.schema": <JSON schema>}          │
│    - 16-byte sync marker                               │
├────────────────────────────────────────────────────────┤
│  Block 0:                                              │
│    - count (zigzag long): 1000 objects in block        │
│    - size (zigzag long): compressed block bytes        │
│    - [binary encoded records × 1000]                   │
│    - sync marker (verify block boundary)               │
├────────────────────────────────────────────────────────┤
│  Block 1 ... Block N                                   │
└────────────────────────────────────────────────────────┘
```

**Kafka Avro message format (Confluent convention):**
```
Byte 0:    0x00  (magic byte — signals Avro + registry)
Bytes 1-4: schema ID (big-endian integer)
Bytes 5+:  Avro-binary-encoded payload
```

**Schema Evolution: writer vs reader resolution:**
```
Writer schema (v1):          Reader schema (v2):
{                            {
  "name": "temperature",       "name": "temperature",
  "type": "float"              "type": "float",
}                              "default": 0.0
                               "name": "unit",   ← NEW field
                               "type": "string",
                               "default": "C"
                             }

Resolution:
- temperature: present in writer → read float directly
- unit: NOT in writer → use default "C"
→ backward compatible: old messages readable by new consumers
```

---

### 💻 Code Example

**Example 1 — Define and register Avro schema:**
```python
# Define schema as Python dict (or .avsc file)
schema_dict = {
    "type": "record",
    "name": "SensorReading",
    "namespace": "com.mycompany.iot",
    "fields": [
        {"name": "device_id",  "type": "string"},
        {"name": "temperature","type": "float"},
        {"name": "ts",         "type": "long",
         "logicalType": "timestamp-millis"},
        # Backward-compatible optional field:
        {"name": "unit",       "type": ["null","string"],
         "default": None}
    ]
}
```

**Example 2 — Produce Avro messages to Kafka:**
```python
from confluent_kafka.avro import AvroProducer
from confluent_kafka import avro
import json, time

schema_str = json.dumps(schema_dict)
value_schema = avro.loads(schema_str)

producer = AvroProducer(
    {
        "bootstrap.servers": "broker:9092",
        "schema.registry.url": "http://registry:8081"
    },
    default_value_schema=value_schema
)

producer.produce(
    topic="sensor-readings",
    value={
        "device_id": "sensor-42",
        "temperature": 23.7,
        "ts": int(time.time() * 1000),
        "unit": "C"
    }
)
producer.flush()
```

**Example 3 — Consume and deserialise:**
```python
from confluent_kafka.avro import AvroConsumer

consumer = AvroConsumer(
    {
        "bootstrap.servers": "broker:9092",
        "group.id": "analytics-consumer",
        "schema.registry.url": "http://registry:8081",
        "auto.offset.reset": "earliest"
    }
)
consumer.subscribe(["sensor-readings"])

while True:
    msg = consumer.poll(timeout=1.0)
    if msg is None:
        continue
    record = msg.value()  # already deserialized dict
    print(record["device_id"], record["temperature"])
```

**Example 4 — Check schema compatibility before deployment:**
```bash
# Test backward compatibility before registering new schema
curl -X POST \
  http://registry:8081/compatibility/subjects/sensor-readings-value/versions/latest \
  -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  -d '{"schema": "{\"type\":\"record\",\"name\":\"SensorReading\",
      \"fields\":[{\"name\":\"device_id\",\"type\":\"string\"},
      {\"name\":\"temperature\",\"type\":\"float\"},
      {\"name\":\"ts\",\"type\":\"long\"},
      {\"name\":\"unit\",\"type\":[\"null\",\"string\"],
       \"default\":null},
      {\"name\":\"humidity\",\"type\":[\"null\",\"float\"],
       \"default\":null}]}"}'
# Expected: {"is_compatible": true}
```

---

### ⚖️ Comparison Table

| Format | Layout | Schema Location | Evolution | Best For |
|---|---|---|---|---|
| **Avro** | Row, binary | Header / Registry | Built-in (backward/forward) | Kafka streaming |
| Parquet | Columnar, binary | File footer | Limited | OLAP analytics |
| Protobuf | Row, binary | .proto file (compiled) | Manual field numbering | gRPC, tight coupling |
| JSON | Row, text | Inline (field names) | None enforced | APIs, small-scale |
| ORC | Columnar, binary | Stripe footer | Limited | Hive analytics |

**How to choose:** Use Avro for Kafka event streaming where schema
evolution over time is expected. Use Parquet/ORC for data lake
analytical storage. Use Protobuf for gRPC when you control both
producer and consumer and want compiled language bindings.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Avro and Parquet are the same kind of thing | Avro is row-oriented (one record = one binary blob); Parquet is columnar (one column = one block). Different use cases entirely |
| Schema Registry is part of Avro | Schema Registry is a separate Confluent product; Avro files can exist without it. The 5-byte magic header is a Confluent convention, not the Avro spec |
| Adding a field is always safe with Avro | Adding a non-nullable field without a default is a backward-incompatible change that breaks old consumers reading new messages |
| Avro compresses data | Avro binary encoding is compact but not compressed by default; compression (Deflate, Snappy) is a separate optional setting on the block level |
| Schema ID collisions are impossible | Different Schema Registries have separate ID namespaces; if you mix data from two registries, schema IDs may collide — messages will be decoded with wrong schemas silently |

---

### 🚨 Failure Modes & Diagnosis

**Schema Compatibility Violation Break**

**Symptom:**
Consumer raises `SchemaParseException: Could not read record`
after a producer deployed a new schema version. Messages pile
up with errors.

**Root Cause:**
Producer registered an incompatible schema (removed a required
field, changed a type) without checking compatibility first.

**Diagnostic Command / Tool:**
```bash
# Check schema history for the subject
curl http://registry:8081/subjects/my-topic-value/versions

# Get specific version
curl http://registry:8081/subjects/my-topic-value/versions/3

# View compatibility level
curl http://registry:8081/config/my-topic-value
```

**Fix:**
Roll back producer to previous schema version. Add the field
back with a default value. Re-register with compatibility check.

**Prevention:**
Set compatibility level to `BACKWARD` (default in Confluent). Add
CI pipeline step that calls compatibility API before every deploy
that changes a schema.

---

**Schema Registry Unavailable (Producer Fails)**

**Symptom:**
All Avro producers fail with
`Error registering Avro schema: Connection refused`.
Kafka topic stops receiving messages.

**Root Cause:**
Schema Registry is a single point of failure if not HA. One-node
deployment went down.

**Diagnostic Command / Tool:**
```bash
curl -s http://registry:8081/subjects | head -c 100
# Should return list of subjects
# If connection refused: Schema Registry is down
docker logs schema-registry --tail 50
```

**Fix:**
Deploy Schema Registry in HA mode (3-node Kafka Connect cluster
or Confluent Cloud managed). Configure producer with
`auto.register.schemas=false` + pre-registered schemas to
reduce registry dependency on hot path.

**Prevention:**
Run Schema Registry on 3 nodes. Monitor `/health` endpoint.
Use client-side schema caching (built into Confluent clients)
to absorb brief registry outages.

---

**Deserialization With Wrong Schema Registry URL**

**Symptom:**
Consumer deserialises messages as garbage bytes or throws
`SerializationException: Error deserializing key/value for
partition`.

**Root Cause:**
Consumer is pointed at a different Schema Registry instance
(dev vs prod). Schema ID 7 in dev registry resolves to a
completely different schema than Schema ID 7 in prod registry.

**Diagnostic Command / Tool:**
```bash
# Inspect the raw Kafka message bytes
kafkacat -b broker:9092 -t my-topic -C -o-1 -e | \
  xxd | head -5
# First byte should be 0x00 (Avro magic)
# Bytes 1-4: schema ID (big-endian)

# Fetch schema from both registries and compare
curl http://dev-registry:8081/schemas/ids/7
curl http://prod-registry:8081/schemas/ids/7
```

**Fix:**
Ensure consumer `schema.registry.url` points to the same
registry used by the producer for that environment.

**Prevention:**
Inject registry URL via environment variable; validate
in deploy pipeline that dev/prod configs are distinct.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Binary Formats` — Avro is a specific binary format;
  understanding why binary formats exist explains Avro's purpose
- `Serialization Formats` — Avro is the streaming-optimised
  member of the serialisation format family
- `Apache Kafka` — Avro's primary use case is Kafka event
  streaming; the two are typically deployed together

**Builds On This (learn these next):**
- `Schema Registry` — the governance layer that makes Avro's
  schema evolution safe in a multi-team environment
- `Schema Evolution` — the rules and strategies for
  changing Avro schemas over time without breaking consumers
- `Kafka Streams` — Kafka's stream processing layer that
  consumes and produces Avro-serialised events

**Alternatives / Comparisons:**
- `Parquet` — columnar binary format; Avro counterpart for
  analytical (non-streaming) storage
- `Protobuf` — binary format with compiled language bindings;
  similar compactness to Avro but different schema evolution
  model (field numbering)
- `JSON` — text format that Avro replaces in high-volume
  streaming; 3–5× larger for the same data

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Binary row-oriented serialisation format  │
│              │ with schema-in-registry and evolution     │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ JSON schema changes silently break Kafka  │
│ SOLVES       │ consumers with no enforcement layer       │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Schema lives once in registry; 4-byte ID  │
│              │ in message = 60-80% size reduction vs JSON│
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Kafka event streaming where schema        │
│              │ evolves over time across many services    │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Analytical column scans (use Parquet);    │
│              │ direct service RPC (use Protobuf)         │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Compactness + evolution vs human          │
│              │ readability + registry dependency         │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Avro is JSON that went on a diet and     │
│              │  enrolled in schema therapy."             │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Schema Registry → Schema Evolution →      │
│              │ Kafka Streams                             │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A Kafka topic has 30 consumer groups. The producer
wants to rename a field from `customer_id` to `customerId`
to match a new company naming convention. Explain step by step
how this change would be handled with Avro + Schema Registry
under BACKWARD, FORWARD, and FULL compatibility checks —
which one allows the rename without breaking any consumer,
and what is the migration path if no compatibility level allows
a direct rename?

**Q2.** Your Schema Registry goes down at 2 AM. Avro producers
are configured with `auto.register.schemas=true`. Consumers use
a 10-minute local schema cache. Trace exactly what happens to
producers and consumers in the first 10 minutes, the next hour,
and what happens when the registry comes back up — including
any message loss, ordering, or data corruption risks.

