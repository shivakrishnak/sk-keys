---
layout: default
title: "Schema Evolution (Data)"
parent: "Data Fundamentals"
nav_order: 511
permalink: /data-fundamentals/schema-evolution/
number: "0511"
category: Data Fundamentals
difficulty: ★★★
depends_on: Schema Registry, Avro, Serialization Formats, Data Types, Distributed Systems
used_by: Data Governance, Data Catalog, Kafka Streams, Data Lakehouse
related: Schema Registry, Avro, Protobuf, Data Formats, Data Modeling
tags:
  - dataengineering
  - advanced
  - streaming
  - distributed
  - database
---

# 511 — Schema Evolution (Data)

⚡ TL;DR — Schema evolution is the strategy for changing data structure definitions over time without breaking producers or consumers that haven't yet been updated.

| #511 | Category: Data Fundamentals | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Schema Registry, Avro, Serialization Formats, Data Types, Distributed Systems | |
| **Used by:** | Data Governance, Data Catalog, Kafka Streams, Data Lakehouse | |
| **Related:** | Schema Registry, Avro, Protobuf, Data Formats, Data Modeling | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A company has been collecting IoT sensor data for 3 years.
The original schema had 5 fields. Over 3 years, the team added
10 new fields in 15 schema changes. Each change required:
1. A maintenance window to stop all writers.
2. All historical files to be reprocessed with the new schema.
3. All consumer services to be updated simultaneously.
4. A coordinated "flag day" deployment across 30 microservices.

If a consumer misses the flag day, it crashes parsing the new
format. If the reprocessing job fails midway, the data lake has
mixed schemas — some files in v3, some in v4. The complexity
compounds with every change.

**THE BREAKING POINT:**
In a live production system with data flowing continuously and
30 services all deployed independently by different teams,
a "stop everything and migrate" approach is impossible. Yet
the business needs to add new data fields every sprint. Without
a strategy for schema evolution, these two realities collide —
and the data platform becomes a change-averse monolith.

**THE INVENTION MOMENT:**
This is exactly why schema evolution strategies were developed.
By defining compatibility contracts (backward, forward, full)
and encoding rules (field defaults, reserved field numbers),
data can evolve continuously while old and new producers and
consumers coexist safely — no flag days, no forced simultaneous
upgrades.

---

### 📘 Textbook Definition

**Schema evolution** is the ability to change the data schema
(field additions, removals, type changes, renames) of a stored
or transmitted dataset over time while maintaining
interoperability between producers and consumers that use
different schema versions. Key compatibility models:
**Backward compatibility** — new schema can read data written
with old schema (new consumer reads old data).
**Forward compatibility** — old schema can read data written
with new schema (old consumer reads new data).
**Full compatibility** — both backward and forward simultaneously.
Schema evolution strategies vary by format: Avro uses field
defaults and union types; Protobuf uses field numbers (never
reused) and optional fields; relational databases use SQL
migrations (ADD COLUMN, ALTER TABLE); columnar formats (Parquet)
support additive column addition without rewriting files.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Schema evolution lets you change data structure definitions
without forcing every consumer to update at the same time.

**One analogy:**

> Imagine a shared language used between 50 people. When you
> add a new word to the vocabulary (add a field), older speakers
> don't know the word — but they can still understand everything
> else you say (backward compatible). If you change the meaning
> of an existing word (change type), older speakers misunderstand
> sentences — not backward compatible. Schema evolution is
> the discipline of expanding the vocabulary without changing
> the meaning of existing words.

**One insight:**
The hardest part of schema evolution is not the technology —
it's the discipline of never changing the MEANING of an existing
field, only adding new optional fields. Every schema evolution
problem traces back to someone changing field semantics instead
of adding a new field with the new semantics.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Distributed systems cannot be updated atomically — some
   producers/consumers will always be on old schemas during
   a migration.
2. The wire format of an existing field must not change meaning
   (bytes written as int32 must always be decoded as int32 by
   that field number/name).
3. New information should be expressed as NEW fields, not as
   changed meanings of existing fields.

**COMPATIBILITY RULES BY FORMAT:**

*Avro (field-name-based resolution):*
- ADD field with default: backward compatible (old data lacks
  field → use default; consumers using old schema ignore unknown).
- REMOVE field: forward compatible only (new messages missing
  field → old consumers get old default or null).
- RENAME field: BREAKING — old consumers look for old name,
  not found. Solution: use Avro aliases: add new name + mark
  old name as alias — both names resolve to same field.
- TYPE CHANGE: only safe promotions (int → long, float → double).
  Any non-promotable type change is breaking.

*Protobuf (field-number-based resolution):*
- ADD field (new number): backward + forward compatible.
  Old consumers skip unknown field numbers. New consumers get
  zero value if field absent in old message.
- REMOVE field: Mark as `reserved` (number + name) to prevent
  reuse. Old messages with this field are decoded as unknown
  field (ignored).
- RENAME field: Compatible if field NUMBER is unchanged.
  Protobuf uses field numbers for encoding, not names.
  Rename = schema-level change only, wire format unchanged.
- TYPE CHANGE: Only compatible within wire type group
  (all varints are compatible: int32/int64/bool/enum/sint32).
  Changing from int32 to string: breaking.

*Relational databases (SQL migrations):*
- ADD COLUMN NOT NULL without DEFAULT: breaking for existing
  rows (NULL violation). Always add with DEFAULT first.
- ADD COLUMN NULL: safe (existing rows get NULL).
- RENAME COLUMN: breaking for all queries/apps using old name.
  Strategy: add new column, dual-write, migrate readers, drop old.
- CHANGE TYPE: usually breaking. Strategy: add new column,
  migrate data, switch readers, drop old.

*Parquet files (columnar, schema-per-file):*
- ADD COLUMN: safe with schema merging enabled
  (`spark.read.option("mergeSchema","true")`). Old files return
  NULL for the new column. New files have the column.
- REMOVE COLUMN: files still have column bytes — safe to ignore
  with schema merging; old readers still work.
- RENAME: incompatible — old files have old name, new files
  have new name. Schema merging produces both columns with NULL
  for whichever file lacks it.

**THE TRADE-OFFS:**
**Gain:** Independent deployment of producers and consumers;
continuous data evolution without flag days; historical data
remains readable.
**Cost:** Schema discipline required (discipline = toil); all
changes must be additive; semantics must be preserved; tooling
(schema registry, compatibility checks in CI) required to
enforce.

---

### 🧪 Thought Experiment

**SETUP:**
A `UserEvent` Avro schema has 4 fields. The team needs to add
a `loyalty_tier` field. There are currently 2 billion messages
in the topic from the past year, all written with the v1 schema.
10 consumer services use v1. The producer team wants to deploy
a change next week.

**CHANGE A — BREAKING (wrong approach):**
Add `loyalty_tier` as a required string. Deploy producer.
Old consumers using v1 read new messages. Avro decoder sees
`loyalty_tier` bytes (unknown field in v1 schema). Library
behaviour: some skip and continue (OK), some throw exception
(disaster). Consumers that use the field before update get
null/exception. Three services crash.

**CHANGE B — BACKWARD COMPATIBLE (right approach):**
Add `loyalty_tier` as `["null", "string"]` with `"default": null`.
Register v2 in Schema Registry (compatibility check: PASSES).
Deploy producer next Tuesday. Old consumers on v1: receive v2
messages → `loyalty_tier` bytes present → Avro decoder sees
unknown field → **uses default null** (v1 union field resolution).
No consumer crashes. Consumers can be updated over the next 2
weeks at their own pace.

**THE INSIGHT:**
Schema evolution converts a "coordinated deployment" (all 10
teams must upgrade simultaneously) into a "rolling deployment"
(each team upgrades when ready). The discipline is simply:
always add optional with defaults, never change existing field
semantics. This discipline converts a multi-hour coordinated
migration into a 10-minute schema registration.

---

### 🧠 Mental Model / Analogy

> Schema evolution is like evolving a government tax form.
> Each year, the government ADDS new fields (for new regulations)
> but NEVER removes or renames old fields — because millions of
> people filed with the old form, and the IRS (consumer) must
> still process old filings. "New field in 2024 form: Question 42."
> People filing with 2023 forms: Question 42 is blank → treated
> as zero. The new form (v2) is backward compatible with old
> returns (v1 data). The IRS (consumer) can read both 2023 and
> 2024 forms simultaneously.

- "Tax form version" → schema version
- "Adding Question 42" → adding field with default
- "IRS processing old forms" → backward compatibility
- "Old form filer omitting new field" → producer on old schema
- "Never renaming Question 5 to Question 8" → never changing field numbers (Protobuf)
- "Auditor requiring old forms to still be processable" → BACKWARD_TRANSITIVE

**Where this analogy breaks down:** Unlike tax forms, schema
evolution is bidirectional: you also need old consumers to
safely read NEW forms (forward compatibility). The tax form
analogy only captures backward compatibility. A full schema
evolution strategy must address both directions.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Change the structure of your data (add fields, rename things)
without forcing every system that reads the data to update at
the same moment. Old systems keep working; new systems get the
new fields.

**Level 2 — How to use it (junior developer):**
Rules of thumb: always add optional fields with defaults. Never
rename a field — instead deprecate the old name and add the new
one alongside. Never change a field's type to an incompatible type.
Never delete a field until all consumers have been confirmed to
no longer use it. In SQL databases: `ALTER TABLE ... ADD COLUMN ...
DEFAULT ... NULL` before deploying code that expects the column.

**Level 3 — How it works (mid-level engineer):**
The full compatibility matrix for Avro:

| Change | BACKWARD | FORWARD | FULL |
|---|---|---|---|
| Add field (with default) | ✅ | ❌ | ❌ |
| Add field (no default) | ❌ | ✅ | ❌ |
| Remove field (has default) | ❌ | ✅ | ❌ |
| Remove field (no default) | ❌ | ❌ | ❌ |
| Change type (promotable) | ✅ | ✅ | ✅ |
| Change type (incompatible) | ❌ | ❌ | ❌ |
| Rename via alias | ✅ | ❌ | ❌ |

To achieve FULL compatibility: all changes must be additive (new
field with default) — never remove or change. Fields can be
"logically deprecated" in documentation but must persist in the
schema.

For Protobuf, the Expand-Contract pattern:
1. Add new field (new number) — deploy producers.
2. Deploy consumers reading new field.
3. (Optional) Write migration to back-fill historical records.
4. Only then mark old field deprecated; much later remove.

**Level 4 — Why it was designed this way (senior/staff):**
The formal study of schema evolution is rooted in Liskov
Substitution Principle applied to data: a new schema should be
"substitutable" for the old one in any context where the old
one was used. BACKWARD compatibility is the data equivalent of
LSP in class hierarchies. The reason FULL compatibility is
rarely achieved in practice is the same reason LSP-compliant
class hierarchies are rare: adding new functionality (new fields
with new semantics) and removing old liability (dead fields) are
both needed, but each satisfies only one direction of compatibility.
BACKWARD_TRANSITIVE is the gold standard because long-running
consumers (batch jobs, regulatory audit systems, ML model
training pipelines) may sit dormant for months and resume
consuming from arbitrary historical offsets — using schema v1
on data written with schema v7. Without transitivity guarantee,
each version-N-to-N+1 hop is safe but the N-to-N+7 path has
no formal guarantee. This is the silent killer of schema evolution
programs that switch from BACKWARD_TRANSITIVE to BACKWARD during
"fast-moving" sprints.

---

### ⚙️ How It Works (Mechanism)

**Avro schema resolution algorithm (writer + reader schema):**
```
Writer schema (v1):
  {name: "order_id", type: "long"}
  {name: "amount",   type: "double"}

Reader schema (v2):
  {name: "order_id", type: "long"}
  {name: "amount",   type: "double"}
  {name: "currency", type: ["null","string"], default: null}

Resolution:
  For each field in READER schema:
    1. Find matching field in WRITER schema by name
       (or alias in Avro).
    2. If found: decode using WRITER's type encoding,
       project to READER's type (promote if needed).
    3. If NOT found in WRITER: use READER's default value.
  For each field in WRITER schema NOT in READER:
    4. Read and discard bytes (advance position).

Result: currency=null (from default), order_id and amount decoded normally.
```

**ADD/REMOVE field decision tree:**
```
┌──────────────────────────────────────────────────────┐
│         SCHEMA CHANGE COMPATIBILITY GUIDE            │
│                                                      │
│  Want to ADD a field?                                │
│    Has default value? → ✅ Backward compatible        │
│    No default?        → ✅ Forward compatible only    │
│                         ❌ Not backward compatible    │
│                                                      │
│  Want to REMOVE a field?                             │
│    Has default in reader schema?                     │
│      → ✅ Backward compatible (reader uses default)  │
│      → use "reserved" in Protobuf to block reuse     │
│                                                      │
│  Want to RENAME a field?                             │
│    Avro:     add new name + old name as ALIAS        │
│    Protobuf: just change the name in .proto file     │
│              (wire format uses field number, not name)│
│    SQL:      Expand-Contract pattern                 │
│                                                      │
│  Want to CHANGE TYPE?                                │
│    Promotable (int→long, float→double)?              │
│      → ✅ Compatible                                 │
│    Non-promotable (string→int, long→string)?         │
│      → ❌ BREAKING — use Expand-Contract             │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 — Avro safe field addition:**
```python
# v1 schema
schema_v1 = {
    "type": "record", "name": "UserEvent",
    "fields": [
        {"name": "user_id",    "type": "long"},
        {"name": "event_type", "type": "string"},
        {"name": "timestamp",  "type": "long"}
    ]
}

# v2 schema — BACKWARD COMPATIBLE additions
schema_v2 = {
    "type": "record", "name": "UserEvent",
    "fields": [
        {"name": "user_id",       "type": "long"},
        {"name": "event_type",    "type": "string"},
        {"name": "timestamp",     "type": "long"},
        # New optional fields with defaults:
        {"name": "session_id",    "type": ["null","string"],
         "default": None},
        {"name": "loyalty_tier",  "type": ["null","string"],
         "default": None}
    ]
}
# Old consumers reading v2 messages: session_id/loyalty_tier
# → use null default. No crash, no missing fields.
```

**Example 2 — Protobuf Expand-Contract pattern (type change):**
```protobuf
// v1: amount was int (mistake — should have been float)
message Order {
  int64 order_id = 1;
  int32 amount   = 2;  // WRONG type — need to change
}

// v2: add new field, keep old (Expand phase)
message Order {
  int64  order_id    = 1;
  int32  amount      = 2;  // keep old — don't break readers
  double amount_v2   = 3;  // new correct field
}
// Producer: writes BOTH amount and amount_v2
// New consumers: read amount_v2; old consumers: read amount

// v3: mark old deprecated (after all consumers migrated)
message Order {
  int64  order_id    = 1;
  reserved 2;              // reserved, not reusable
  reserved "amount";       // reserve name too
  double amount_v2   = 3;
}
```

**Example 3 — SQL Expand-Contract (column rename):**
```sql
-- Phase 1: Add new column, keep old
ALTER TABLE users ADD COLUMN user_name VARCHAR(255);
-- Phase 2: Deploy app writing to BOTH columns
UPDATE users SET user_name = username;
-- Phase 3: Deploy consumers reading new column
-- Phase 4: Verify no reads of 'username' remain
-- Phase 5: Drop old column
ALTER TABLE users DROP COLUMN username;
```

---

### ⚖️ Comparison Table

| Compatibility Level | Safe Changes | Breaks On | Best For |
|---|---|---|---|
| **BACKWARD** | Add optional field | Remove field | Consumer-first teams |
| **FORWARD** | Remove optional field | Add required field | Producer-first teams |
| **FULL** | Only optional additions | Removals, type changes | Mutual dependency |
| **BACKWARD_TRANSITIVE** | Same as BACKWARD + chain-safe | Any removal or type change | Long-running consumers |
| **NONE** | Anything | Anything | Dev/test only |

**How to choose:** BACKWARD_TRANSITIVE for production Kafka topics
used by multiple teams. FULL for REST APIs with strict versioning.
NONE only in development. Never use NONE in production multi-team
topics.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Backward and forward compatibility are the same thing | BACKWARD: new schema reads old data. FORWARD: old schema reads new data. They are inverse — satisfying one does not satisfy the other |
| Adding a field always breaks nothing | Adding a REQUIRED field (no default) in Avro breaks backward compatibility — old consumers reading new messages get an unexpected field they don't know how to handle |
| Field renaming in Protobuf is breaking | Protobuf wire format uses field numbers, not names. Renaming in the .proto file changes documentation only — wire format is identical. Old and new consumers both work |
| Schema evolution only matters for Kafka | Schema evolution applies to REST APIs (OpenAPI versioning), database schemas (SQL migrations), file formats (Parquet schema merging), and any long-lived data contract |
| BACKWARD_TRANSITIVE is always safe | BACKWARD_TRANSITIVE ensures each new schema is backward compatible with ALL previous versions — but a consumer on a very old schema version may still have application logic that breaks on new fields they receive as defaults |

---

### 🚨 Failure Modes & Diagnosis

**Silent Data Loss From Field Removal**

**Symptom:**
A downstream ML model trained on `risk_score` field suddenly
receives all-null values. Dashboard shows 100% null rate for
`risk_score` from a specific date.

**Root Cause:**
Producer team removed `risk_score` field (it was FORWARD
compatible per registry). Old consumer (ML pipeline) used v5
schema; producer upgraded to v6 where `risk_score` was removed.
The consumer's Avro library resolved missing `risk_score` to null
via the field's default — silently corrupting the ML training set.

**Diagnostic Command / Tool:**
```bash
# Check schema history
curl http://registry:8081/subjects/events-value/versions
# Compare v5 to v6 — look for removed fields
curl http://registry:8081/subjects/events-value/versions/5
curl http://registry:8081/subjects/events-value/versions/6
```

**Fix:**
Re-add `risk_score` to v7. Backfill ML pipeline from historical
data (before v6 was deployed). Deploy consumer update to read
from correct date.

**Prevention:**
Never remove a field from production topics under BACKWARD
compatibility. Only remove after confirming via observability
that zero consumers read the field.

---

**Type Promotion Error (int → long truncation)**

**Symptom:**
After schema change, certain `order_id` values arrive as incorrect
numbers. Large order IDs (> 2 billion) are corrupted.

**Root Cause:**
Schema changed `order_id` from `long` (int64) to `int` (int32)
(a regression, not a promotion). Values exceeding int32 max
(2,147,483,647) are silently truncated.

**Diagnostic Command / Tool:**
```python
# Compare schema versions
import fastavro
import io
schema_v1 = # fetch from registry
schema_v2 = # fetch from registry
# Look for type change in field definitions
for f1, f2 in zip(schema_v1["fields"], schema_v2["fields"]):
    if f1["type"] != f2["type"]:
        print(f"TYPE CHANGE: {f1['name']}: {f1['type']} → {f2['type']}")
```

**Fix:**
Revert to `long` in schema v3. Any messages written with int32
`order_id` have corrupted values — if retention allows, replay
from source.

**Prevention:**
Schema Registry's compatibility check rejects int64 → int32
(not a valid promotion). But int32 → int64 is allowed.
If this occurred, NONE compatibility was set — set to BACKWARD
immediately.

---

**Stale Consumer on Very Old Schema**

**Symptom:**
After months dormant, a nightly batch job resumes. It reads from
Kafka offset 0 (reprocessing), using schema v1. Current topic
is on schema v9. The job produces confusing results — all new
fields are null, some fields have unexpected types.

**Root Cause:**
BACKWARD compatibility was set (not TRANSITIVE). v9 is backward
compatible with v8, v8 with v7, ... but no check was done for
v9 vs v1 directly.

**Diagnostic Command / Tool:**
```bash
# Test v1 vs v9 compatibility
curl -X POST \
  http://registry:8081/compatibility/subjects/topic-value/versions/1 \
  -d '{"schema": "'"$(curl http://registry:8081/subjects/topic-value/versions/9)"'"}'
# Test AGAINST a specific old version, not just latest
```

**Fix:**
Update the batch job to use schema v9 for deserialization.
Use Avro's writer-schema + reader-schema mechanism: decode with
writer schema (from message's schema ID), project to reader's v9
schema — handles the multi-version gap.

**Prevention:**
Set BACKWARD_TRANSITIVE on all topics. Maintain a "min consumer
schema version" document per topic. Deprecate old schema versions
only when all known consumers are updated.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Schema Registry` — the enforcement layer for schema
  evolution compatibility; understanding the registry explains
  how compatibility is enforced
- `Avro` — the format whose field resolution rules define
  backward/forward compatibility in streaming systems
- `Distributed Systems` — schema evolution exists because
  distributed systems cannot be updated atomically

**Builds On This (learn these next):**
- `Data Governance` — schema evolution is one pillar of
  data governance, alongside data lineage and data quality
- `Data Catalog` — schema history is surfaced in data catalogs
  for discoverability and impact analysis
- `Data Modeling` — schema evolution is the runtime expression
  of good (extensible) data modeling decisions

**Alternatives / Comparisons:**
- `Schema Registry` — the infrastructure that enforces schema
  evolution rules; the two are complementary not competing
- `Data Formats (JSON, XML, YAML, CSV)` — text formats evolve
  differently (no explicit compatibility checking) vs binary
  formats with schema registries
- `API Versioning` — the REST API equivalent of schema
  evolution; same patterns (additive changes, deprecation cycles)
  applied at the HTTP layer

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Strategy for changing data schemas over   │
│              │ time without breaking old producers or    │
│              │ consumers                                 │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Distributed systems cannot be updated     │
│ SOLVES       │ atomically — old and new schemas coexist  │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Change semantics = breaking; add new      │
│              │ optional fields = safe. Always expand,    │
│              │ never mutate                              │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Any data contract that is consumed by     │
│              │ more than one independent system          │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Short-lived data with a single consumer   │
│              │ — overhead exceeds benefit                │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Schema discipline (no free mutations) vs  │
│              │ independent deployability of all services │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "You can always add a word; you must      │
│              │  never change the meaning of one."        │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Data Modeling → Star Schema →             │
│              │ Dimensional Modeling                      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A financial audit system reads raw Kafka messages from
an `account_transactions` topic. Due to regulatory requirements,
it must replay all messages from the past 7 years. Over those
7 years, the schema has gone through 23 versions. Some versions
removed fields that were later discovered to be needed by the
audit trail. Describe the complete recovery strategy including
which schema version to use for decoding which historical
messages, how to handle fields removed in v8 that are needed
for the audit, and what process controls would have prevented
this situation.

**Q2.** A public REST API uses JSON with no explicit schema
versioning. The team wants to rename `customerId` to `customer_id`
in the response payload for all new endpoints but must not break
existing clients. Design the complete migration strategy as a
time-sequenced plan, specifying: what the API returns during
each phase, how long each phase lasts, how you detect when it
is safe to remove the old field name, and what observability
is required to make the migration visible.

