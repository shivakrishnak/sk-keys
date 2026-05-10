---
version: 2
layout: default
title: "Schema Evolution"
parent: "Database Fundamentals"
grand_parent: "Technical Dictionary"
nav_order: 55
permalink: /databases/schema-evolution/
id: DBF-055
category: Database Fundamentals
difficulty: ★★★
depends_on: Database Migration, Backward Compatibility, Distributed Systems
used_by: Microservices, Event Sourcing, API Design
related: Database Migration, Protobuf, Avro, Flyway
tags:
  - database
  - schema
  - compatibility
  - deep-dive
---

# DBF-055 - Schema Evolution

⚡ TL;DR - Schema evolution is the discipline of changing a database or message schema over time without breaking deployed consumers - using additive-only changes, multi-phase deployments, and schema registries to manage backward and forward compatibility.

| #450            | Category: Database Fundamentals                                 | Difficulty: ★★★ |
| :-------------- | :-------------------------------------------------------------- | :-------------- |
| **Depends on:** | Database Migration, Backward Compatibility, Distributed Systems |                 |
| **Used by:**    | Microservices, Event Sourcing, API Design                       |                 |
| **Related:**    | Database Migration, Protobuf, Avro, Flyway                      |                 |

---

### 🔥 The Problem This Solves

**SCHEMA CHANGE BREAKS CONSUMERS:**
Service A writes events to Kafka. Schema v1: `{userId, amount}`. Service B reads these events and processes them. You add a required field: `{userId, amount, currency}`. Service B deployed with old schema: reads an event, tries to access `currency` field - it doesn't exist. NullPointerException. Service B crashes. Or worse: silently processes events as if currency is USD when it might be EUR.

**DISTRIBUTED SYSTEMS COMPOUND THIS:**
In a monolith: one app, one schema, deploy everything at once. In microservices: 20 services, 20 schemas, 20 independent deploy cycles. You cannot upgrade all consumers simultaneously. Some services will always be running an older version while you deploy the new version. Every schema change must work with the current deployed version AND the next version - sometimes multiple versions simultaneously.

**THE DISCIPLINE:**
Schema evolution is the practice of planning schema changes so that every change is safe to apply while multiple schema versions coexist. You don't just write a migration - you write a compatibility strategy.

---

### 📘 Textbook Definition

**Schema evolution** is the controlled, planned process of changing a data schema (database table, Avro/Protobuf message schema, JSON API schema) over time while maintaining **backward compatibility** (new code can read old data) and **forward compatibility** (old code can read new data without breaking). Key principles: **additive-only changes** are safe (add fields, add tables, add optional columns); **subtractive or renaming changes** are unsafe without a multi-phase migration plan (expand-contract). Schema registries (Confluent Schema Registry for Avro/Protobuf, AWS Glue Schema Registry) enforce compatibility rules and prevent incompatible schema versions from being published. The **expand-contract pattern** (also called **parallel change**) is the canonical technique: expand (add new structure alongside old), migrate (fill in new structure), contract (remove old structure after all consumers updated).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Schema evolution ensures that changing a schema over time doesn't break things that are already deployed - by planning changes to be backward and forward compatible.

**One analogy:**

> Adding a new form field to a government document. If the new field is OPTIONAL: old forms without the field are still valid (backward compatible - new processor can handle old forms). New forms with the field are processed correctly. If the new field is REQUIRED: old forms without the field are now INVALID - you've broken backward compatibility. Every office that accepts old forms is now broken.

- "Government form fields" → schema fields
- "Offices that accept forms" → consumers/services using the schema
- "Optional new field" → backward compatible change (additive)
- "Required new field" → backward incompatible change (breaking)
- "Old forms still accepted" → backward compatibility (new code reads old data)
- "Offices that haven't retrained yet" → services still on old schema version

**One insight:**
"Required" is the enemy of backward compatibility. In a distributed system where you cannot update all consumers simultaneously, a new required field is almost always a mistake. The default for new schema fields should be: optional with a sensible default. "Required" belongs only to fields that were there from the very beginning.

---

### 🔩 First Principles Explanation

**COMPATIBILITY MATRIX:**

```
BACKWARD COMPATIBILITY:
  New schema can read data written by old schema
  "Old data in, new reader" - new reader handles missing fields gracefully
  SAFE changes:
    - ADD optional field (new reader handles missing field by using default)
    - ADD enum value (old writers won't use it; new readers must handle it)
    - WIDEN type (INT → BIGINT; old data fits in new type)
  UNSAFE changes:
    - ADD required field (old data is missing it → validation failure)
    - REMOVE field (new reader expecting it → NPE or silent default)
    - RENAME field (new reader looks for new name; old data has old name → missing)
    - CHANGE type incompatibly (VARCHAR → INTEGER; "hello" fails to cast)

FORWARD COMPATIBILITY:
  Old schema can read data written by new schema
  "New data in, old reader" - old reader ignores unknown fields
  SAFE changes:
    - ADD field (old reader ignores the new field it doesn't know about)
    - ADD enum value (IF old reader handles unknown enum gracefully)
  UNSAFE changes:
    - REMOVE field that old reader expects → old reader fails
    - CHANGE field meaning (same name, different semantics → silent corruption)

FULL COMPATIBILITY (BOTH):
  Both old readers handle new data AND new readers handle old data
  Most restrictive; only additive changes are safe
```

**AVRO SCHEMA EVOLUTION:**

```json
// Avro Schema v1
{
  "type": "record",
  "name": "Order",
  "fields": [
    {"name": "order_id", "type": "string"},
    {"name": "amount",   "type": "double"}
  ]
}

// Avro Schema v2 - BACKWARD COMPATIBLE (new optional field with default)
{
  "type": "record",
  "name": "Order",
  "fields": [
    {"name": "order_id", "type": "string"},
    {"name": "amount",   "type": "double"},
    {"name": "currency", "type": "string", "default": "USD"}  ← optional + default
  ]
}
// New reader: reads old Avro record → currency is missing → uses default "USD" ✓
// Old reader: reads new Avro record → currency is unknown → IGNORED by Avro ✓
// Full backward + forward compatibility
```

**PROTOBUF SCHEMA EVOLUTION:**

```protobuf
// Proto v1
message Order {
  string order_id = 1;
  double amount   = 2;
}

// Proto v2 - BACKWARD COMPATIBLE
message Order {
  string order_id  = 1;
  double amount    = 2;
  string currency  = 3;  // new optional field; field number 3 (NEW; never reuse field numbers!)
  // If not present in serialized bytes: default value (empty string / zero / null)
}

// Proto rules:
// NEVER change a field number (1, 2, 3) - field numbers are the binary key
// NEVER reuse a field number after deletion - use reserved keyword
// NEVER change field type incompatibly (double → string would break)
// DO mark removed fields as reserved:
message Order {
  reserved 3;  // reserved field number 3 (was currency, removed)
  reserved "currency";  // reserved field name
  string order_id = 1;
  double amount   = 2;
}
```

**CONFLUENT SCHEMA REGISTRY:**

```
Kafka producer: publishes Order event
  → Schema Registry: "I want to publish with schema v2 of 'Order'"
  → Registry: is v2 compatible with latest registered version?
    BACKWARD: can a v2-schema reader read v1-written data? ← default check
    FORWARD:  can a v1-schema reader read v2-written data?
    FULL:     both
  → If compatible: register schema, return schema_id
  → Producer: serialize event with schema_id header + Avro bytes

Kafka consumer:
  → Read event: extract schema_id from header
  → Schema Registry: "give me schema for id=42"
  → Deserialize with correct schema (handles evolution automatically)

Registry prevents publishing an incompatible schema:
  Try to add REQUIRED field → Registry returns 409 Conflict
  This prevents breaking consumers before they even deploy
```

**RELATIONAL DB: EXPAND-CONTRACT (full example):**

```
Goal: rename column `users.username` → `users.display_name`
Service version: v1 (uses username), v2 (uses display_name)

PHASE 1 - EXPAND (deploy with migration, no app change):
  Migration: ALTER TABLE users ADD COLUMN display_name VARCHAR(255);
  App v1: SELECT username; INSERT username; (unchanged)
  Sync trigger or application dual-write: copy username → display_name on writes

PHASE 2 - BACKFILL (batch migration, no app deployment):
  Migration: UPDATE users SET display_name = username WHERE display_name IS NULL;
  All historical rows now have display_name populated

PHASE 3 - DEPLOY v2 (app reads/writes display_name; keeps writing username):
  App v2: reads display_name; writes BOTH username AND display_name
  Why write both: v1 instances may still be running (rolling deploy); they need username updated

PHASE 4 - CONFIRM v1 FULLY RETIRED:
  All pod instances are now v2. No v1 running.

PHASE 5 - CONTRACT (deploy with migration):
  Migration: ALTER TABLE users ALTER COLUMN display_name SET NOT NULL;
             ALTER TABLE users DROP COLUMN username;
  App v3: reads/writes only display_name; username column gone

TOTAL: 5 phases, 3 app deployments, 2 migrations, ZERO downtime
SHORTCUT (monolith, maintenance window): ALTER TABLE RENAME COLUMN + single deploy
REQUIRED approach (microservices, high availability): full expand-contract
```

---

### 🧪 Thought Experiment

**EVENT SOURCING + SCHEMA EVOLUTION (The Hard Case)**

Event sourcing stores every state change as an immutable event. Ten years of events in the event store: order events from 2015, 2018, 2020, 2024. Each year, the Order schema evolved. Now you need to re-process all events from the beginning (rebuild a read model from scratch).

**THE PROBLEM:**

- 2015 events: `{orderId, amount}` (no currency field - USD was assumed)
- 2018 events: `{orderId, amount, currency}` (currency added)
- 2020 events: `{orderId, amount, currency, taxAmount}` (tax added)
- 2024 events: `{orderId, amount, currency, taxAmount, discountCode}` (discounts added)

Your current event reader code expects the 2024 schema. Playing back 2015 events: `currency` is null (assumed USD), `taxAmount` is null (assume 0), `discountCode` is null (no discount). This is **upcasting**: transforming an old event into the current schema at read time.

**UPCASTING PATTERN:**

```java
// Event Upcaster: transforms old schema → current schema at read time
public class OrderV1ToV2Upcaster implements EventUpcaster {
    public DomainEvent upcast(DomainEvent event) {
        OrderCreatedV1 old = (OrderCreatedV1) event;
        return new OrderCreatedV2(
            old.orderId,
            old.amount,
            "USD"  // default for events before currency was tracked
        );
    }
    public boolean canUpcast(DomainEvent event) {
        return event instanceof OrderCreatedV1;
    }
}
// Chain upcasters: V1→V2→V3→V4 (applied in sequence at read time)
```

**THE DEEPER LESSON:**
With event sourcing, you NEVER change old events (immutable). Instead, you add upcasters that transform old events to the latest schema at read time. Schema evolution for event stores = managing a chain of upcasters, one per schema version transition. This is the permanent record of every schema change in the system's history.

---

### 🧠 Mental Model / Analogy

> Schema evolution is like international electrical standards for plug shapes. Countries have different standards (UK 3-pin, US 2-pin, EU 2-round-pin). When you travel, you use an adapter (upcaster) that transforms the plug shape your device uses into the shape the socket expects - without changing either the device or the socket. Backward compatible change: adding a 3rd ground pin socket that also accepts old 2-pin plugs. Breaking change: requiring 3-pin for all sockets, and old 2-pin devices stop working.

- "Different plug shapes" → different schema versions
- "Travel adapter" → upcaster / schema converter
- "Socket that accepts both 2-pin and 3-pin" → backward compatible schema (accepts old + new)
- "Requiring 3-pin only" → breaking schema change (old data/consumers fail)
- "Device's plug shape" → producer's schema (what data is written as)
- "Socket's expected shape" → consumer's schema (what the reader expects)

---

### 📶 Gradual Depth - Four Levels

**Level 1:** When you change a database table or message format, existing code that uses the old format might break. Schema evolution means planning your changes carefully so the old code and new code can work at the same time - by adding optional fields instead of required ones, and never removing fields until no code uses them anymore.

**Level 2:** Follow the expand-contract pattern for any structural change: add first, migrate data, update code, then remove. In Kafka/Avro systems, register schemas in Confluent Schema Registry with backward compatibility enforcement. In Protobuf, never reuse field numbers; mark removed fields as `reserved`. Test backward compatibility explicitly: read v1-written data with your v2 reader before deploying.

**Level 3:** Schema compatibility becomes especially complex in long-running distributed systems: Kafka topics retain events for weeks; event-sourced systems retain events forever. Every deployed service instance may be running a different schema version simultaneously. Design your schema changes for the "N-1 compatible" constraint: the new schema must work with the previous version of the consumer. After all consumers are updated to N, you can release N+1 which removes compatibility with N-1. This is a sliding window of compatibility. For relational databases, use `NOT VALID` constraints for large table migrations: `ALTER TABLE orders ADD CONSTRAINT ck_positive_amount CHECK (amount > 0) NOT VALID` - doesn't lock the table during addition, but existing rows aren't validated. Then `VALIDATE CONSTRAINT` in a separate transaction - validates in background without a full table lock.

**Level 4:** Schema evolution is, fundamentally, the distributed systems problem of managing shared mutable contracts. In a distributed system with independent deployment cycles, the schema is a shared API between independently deployed components. Like APIs, schemas must follow a versioning strategy: explicitly versioned (`/v2/orders`), semantically versioned (MAJOR.MINOR.PATCH), or compatibility-tested (schema registry with compatibility rules). The theoretical underpinning: a schema is a type system for data at rest and in transit. Type system changes that are subtype-compatible (Liskov Substitution: new schema can be used wherever old schema was expected) are backward compatible. In type theory terms: adding fields to a record type creates a subtype (more specific → can be used as the parent type). Removing fields creates a supertype (more general → cannot be safely used as the parent type, missing properties). Schema evolution design is therefore: only make downward substitution changes (subtyping) in non-breaking releases. Breaking changes (supertyping, renaming, type changes) require a versioned migration path with explicit backward compatibility planning.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────────┐
│ SCHEMA REGISTRY COMPATIBILITY ENFORCEMENT                │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Developer proposes schema v3 (adds required field)      │
│     ↓                                                    │
│  Schema Registry: check compatibility (BACKWARD)         │
│  Can v3-schema reader read v2-schema data?               │
│  New required field: v2 data has no value → FAIL         │
│     ↓                                                    │
│  Registry returns 409 Incompatible Schema                │
│  Developer blocked from publishing incompatible schema   │
│                                                          │
│  Developer fixes: make new field optional with default   │
│     ↓                                                    │
│  Schema Registry: check again                            │
│  Optional with default: v2 data missing field → use default → OK  │
│     ↓                                                    │
│  Registry registers v3, returns schema_id=3             │
│  [SCHEMA EVOLUTION ← YOU ARE HERE: compatibility enforced]│
│                                                          │
│  Producer: publishes events using v3 schema (schema_id=3)│
│  Consumer A (v2): ignores unknown field (forward compat) │
│  Consumer B (v3): uses new field                         │
└──────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**MICROSERVICE SCHEMA EVOLUTION:**

```
Current state:
  Service A: produces OrderCreated events (schema v2)
  Service B: consumes OrderCreated events (schema v2)
  Kafka topic: orders with Schema Registry (BACKWARD compatibility)

Goal: add `currency` field to OrderCreated

Phase 1 - Design:
  Add currency as OPTIONAL with default "USD"
  Verify backward compatibility: v3 reader reads v2 data → currency = "USD" ✓
  Verify forward compatibility: v2 reader reads v3 data → currency ignored ✓
  Register schema v3 in Schema Registry

Phase 2 - Update Producer (Service A):
  Deploy Service A v3 → produces events with currency field
  [SCHEMA EVOLUTION: producer updated first; consumers still on v2]
  Service B (v2): reads v3 events → currency field unknown → IGNORED (forward compat) ✓

Phase 3 - Update Consumer (Service B):
  Deploy Service B v3 → reads and uses currency field
  Historical v2 events (no currency): currency = "USD" (default) ✓

Phase 4 - Done
  All events have currency; all consumers use currency
  Schema v2 still compatible (retained in registry for historical reads)
```

---

### ⚖️ Comparison Table

| Change Type                       | Backward Compat                | Forward Compat                  | Safe to Deploy Without Coordination    |
| --------------------------------- | ------------------------------ | ------------------------------- | -------------------------------------- |
| Add optional field with default   | ✅ Yes                         | ✅ Yes                          | ✅ Yes                                 |
| Add required field                | ❌ No (old data missing value) | ✅ Yes                          | ❌ No (requires consumer update first) |
| Remove field (that consumers use) | ✅ Yes                         | ❌ No (old consumers expect it) | ❌ No (requires consumer deprecation)  |
| Rename field                      | ❌ No (old name gone)          | ❌ No (new name unknown)        | ❌ No (full migration required)        |
| Widen type (INT → BIGINT)         | ✅ Yes                         | ✅ Yes (usually)                | ✅ Yes                                 |
| Narrow type (BIGINT → INT)        | ❌ No (data may not fit)       | ❌ No (truncation risk)         | ❌ No                                  |

---

### ⚠️ Common Misconceptions

| Misconception                                                | Reality                                                                                                                                                                                                                                  |
| ------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "We can rename fields easily - just update the column"       | Renaming is the most dangerous schema change in a distributed system. It requires full expand-contract across all producers and consumers - typically 3-5 deployment cycles                                                              |
| "New optional fields are always safe"                        | In JSON without schema enforcement, new optional fields are safe. In strict schema systems (Avro with FULL compatibility), even adding optional fields may fail forward compatibility if the schema registry is configured for FULL mode |
| "Schema evolution only matters for messaging systems"        | It matters equally for REST APIs (contract with consumers), database schemas (contract between app and DB), and gRPC/Protobuf (binary protocol)                                                                                          |
| "If consumers ignore unknown fields, we don't need to worry" | Unknown field tolerance (forward compat) is only guaranteed if the serialization format supports it. Avro and Protobuf do. Strict JSON schema validators do not. Know your serialization format's evolution semantics                    |

---

### 🚨 Failure Modes & Diagnosis

**1. Silent Data Corruption from "Safe" Optional Field Removal**

**Symptom:** After removing an old field (that consumers had stopped using), billing reports start showing wrong totals. No errors - just wrong numbers.

**Root Cause:** Service C was still reading the old field as a fallback. "No one's using it" was wrong. The field contained non-null data for 2% of records; Service C silently treated absent field as zero, corrupting billing totals.

**Diagnostic:**

```
Check: schema registry - who still reads the removed schema field?
Check: application logs - any consumer still referencing the old field name?
Check: data - what % of records had non-null values in the removed field?
Alert: data quality checks comparing post-removal report totals to historical baselines
```

**Fix (immediate):** Re-add the field (as optional) to stop corruption. Enumerate all consumers via schema registry usage audit. Update all consumers before removing.

**Prevention:** Before removing any field: (1) mark it deprecated in the schema and documentation, (2) query all consumers from schema registry, (3) monitor field usage in observability system for 30+ days, (4) only remove when confident field is truly unused. Use `reserved` keyword in Protobuf to prevent future reuse of the field number.

---

**2. Schema Registry Rejects Producer - Incompatible Schema Change**

**Symptom:** New service deployment fails. Producer logs: `409 Conflict - Schema is incompatible with version N`. Service cannot start or publish events.

**Root Cause:** Developer added a required field (no default) or removed an existing field, violating the registry's BACKWARD compatibility rules.

**Diagnostic:**

```
Check: schema difference between v_new and v_current
confluent schema-registry schemas diff --subject orders-value --version latest --new-schema new_schema.avsc
Output: "Field 'currency' (required, no default) added - BACKWARD incompatible"
```

**Fix:** Make the new field optional with a meaningful default. Or: remove the field and instead create a new event type for the new use case (additive: new event type). Or: set the subject's compatibility to NONE temporarily (DANGEROUS - only for dev/test, never production).

**Prevention:** Test schema compatibility before committing: `confluent schema-registry schemas check-compatibility` in CI pipeline. Treat schema changes with the same review rigor as API changes.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Database Migration` - the tooling (Flyway/Liquibase) for managing schema changes; evolution is the broader discipline
- `Backward Compatibility` - the contract that schema evolution must maintain
- `Distributed Systems` - why simultaneous schema updates are impossible; why evolution is necessary

**Builds On This (learn these next):**

- `Event Sourcing` - permanent immutable event history makes schema evolution a lifelong concern
- `API Design` - REST/gRPC API versioning follows the same backward compatibility principles
- `Avro / Protobuf` - the serialization formats designed with schema evolution in mind

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ ALWAYS SAFE  │ Add optional field with default           │
│              │ Widen type (INT → BIGINT)                 │
│              │ Add new table/message type (additive)     │
├──────────────┼───────────────────────────────────────────┤
│ NEVER SAFE   │ Add required field (without migration)    │
│              │ Rename field (use expand-contract)        │
│              │ Remove used field (deprecate first)       │
│              │ Narrow type (BIGINT → INT)                │
├──────────────┼───────────────────────────────────────────┤
│ TECHNIQUE    │ Expand-Contract: add → migrate → remove   │
│              │ Upcasting: transform old events at read   │
│              │ Schema Registry: enforce compatibility    │
├──────────────┼───────────────────────────────────────────┤
│ TOOLS        │ Confluent Schema Registry (Avro/Protobuf) │
│              │ Protobuf reserved keyword (field numbers) │
│              │ Flyway/Liquibase (relational DB)          │
├──────────────┼───────────────────────────────────────────┤
│ CORE RULE    │ "Optional + default = safe.               │
│              │  Required = breaking. Rename = migration." │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Change schemas like you push code -      │
│              │  backward compat first, never break prod" │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE C - Design Question) You have a Kafka topic `user-events` with events consumed by 8 different services. Schema currently has 10 fields. You need to: (a) rename `user_name` → `display_name`, (b) split `full_address` into `street`, `city`, `country`, (c) add `timezone` (required for a new billing feature). Design the full migration plan: which changes are safe vs. breaking, what phases are required, what do you deploy in what order, and how do you validate before removing old fields?

**Q2.** (TYPE F - Comparison Depth) Compare Avro schema evolution vs. Protobuf schema evolution on: (a) how they handle field removal, (b) how they handle adding a required field, (c) how they prevent accidental incompatible changes, (d) the role of the schema registry vs. the `.proto` file itself as the compatibility enforcement mechanism. What does each approach get right, and what are the failure modes unique to each?
