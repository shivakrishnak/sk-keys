---
id: JPH-007
title: "@Id and @GeneratedValue"
category: JPA & Hibernate
tier: tier-3-java
folder: JPH-jpa-hibernate
difficulty: ★☆☆
depends_on: JPH-006
used_by: JPH-011, JPH-013, JPH-038
related: JPH-008, JPH-040
tags:
  - java
  - database
  - jpa
  - foundational
status: complete
version: 4
layout: default
parent: "JPA & Hibernate"
grand_parent: "Technical Dictionary"
nav_order: 7
permalink: /jpa-hibernate/id-generatedvalue/
---

# JPH-007 - @Id and @GeneratedValue

⚡ **TL;DR** - `@Id` marks the primary key field of a JPA
entity; `@GeneratedValue` tells the JPA provider how to
automatically assign a value to it on insert.

| #007 | Category: JPA & Hibernate | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | @Entity | |
| **Used by:** | EntityManager, Entity Lifecycle, Optimistic Locking (@Version) | |
| **Related:** | @Table and @Column, Inheritance Mapping Strategies | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Every time you insert a new entity, you need a unique
identifier. Without ORM support, you write a separate query
to get the next sequence value, assign it to the object,
then insert - three operations instead of one. Worse, if two
threads execute concurrently, they might generate the same ID.
Distributed systems make this harder still: the same table
gets inserts from multiple nodes and needs globally unique IDs.

**THE BREAKING POINT:**
Hand-managed IDs introduce race conditions, sequence table
contention, and fragile code that assumes the database
serialises inserts. The ID generation strategy is also a
performance tuner: `IDENTITY` (auto-increment) is simple but
prevents batch insert optimisation; `SEQUENCE` allows batching;
`UUID` is globally unique but 36 bytes vs 8 for a Long.

**THE INVENTION MOMENT:**
JPA codified four ID generation strategies under one
`@GeneratedValue` annotation: `AUTO`, `IDENTITY`, `SEQUENCE`,
and `TABLE`. Each maps to a different database mechanism.
Declaring `@GeneratedValue` once means the developer never
writes ID assignment code again - the JPA provider handles
generation according to the chosen strategy.

---

### 📘 Textbook Definition

**`@Id`** is a Jakarta Persistence annotation that designates
the field (or property) in an `@Entity` class that serves as
the persistent identifier - the primary key mapped to the
database primary key column. The field type must be one of:
primitive types, wrapper types (`Long`, `Integer`), `String`,
`java.util.Date`, `java.sql.Date`, or `java.util.UUID`.

**`@GeneratedValue`** configures automatic generation of the
`@Id` value when a new entity is persisted. It takes two
optional attributes: `strategy` (one of `AUTO`, `IDENTITY`,
`SEQUENCE`, `TABLE`) and `generator` (the name of a defined
sequence generator). If absent, the developer must assign
the `@Id` value manually before calling `em.persist()`.

---

### ⏱️ Understand It in 30 Seconds

**One line:** `@Id` says "this is the primary key"; 
`@GeneratedValue` says "let the database generate its value."

**One analogy:**
> `@Id` is like a social security number field on a form.
> `@GeneratedValue` is like the government automating SSN
> assignment - you submit the form and they fill in the
> unique number. Without `@GeneratedValue`, you write your
> own SSN, which requires a central registry and careful
> coordination.

**One insight:** The ID generation strategy is a fundamental
architectural choice, not a detail. `IDENTITY` is simple but
blocks Hibernate's batch insert optimisation (Hibernate needs
the ID to exist before it can process the next entity in a
batch). `SEQUENCE` enables batching by pre-fetching ID blocks
from a database sequence. This single annotation choice
determines whether bulk inserts scale.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Every `@Entity` must have exactly one `@Id` (or composite
   key via `@IdClass` / `@EmbeddedId`)
2. The `@Id` value uniquely identifies an entity row within
   its table - it is the primary key
3. Hibernate uses the `@Id` value to maintain the identity
   map: `em.find(Product.class, 42L)` looks up by this value
4. A new entity (not yet persisted) has a null or zero `@Id`;
   after `em.persist()`, the `@Id` is populated by the chosen
   generation strategy
5. Changing an entity's `@Id` after persist is illegal
   (undefined behaviour in JPA spec)

**DERIVED DESIGN:**
The four generation strategies reflect the four underlying
database mechanisms:
- `IDENTITY`: database `AUTO_INCREMENT` / `SERIAL` column;
  the database assigns the value on INSERT
- `SEQUENCE`: database sequence object; Hibernate calls
  `NEXT VALUE FOR sequence` before INSERT
- `TABLE`: a dedicated `hibernate_sequence` table; used
  when the database has no sequence support
- `AUTO`: Hibernate picks the best strategy for the database

**THE TRADE-OFFS:**

| Strategy | Batch support | DB dependency | Globally unique |
|---|---|---|---|
| `IDENTITY` | No | Specific to DB | No (per-table) |
| `SEQUENCE` | Yes (allocationSize) | Requires sequences | No (per-sequence) |
| `TABLE` | Yes | Database-agnostic | No |
| `UUID` (manual) | Yes | None | Yes |

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Every stored entity needs a unique identifier -
that is irreducible.
**Accidental:** Managing sequence generation manually in
application code is accidental. `@GeneratedValue` delegates
this to the database where it belongs.

---

### 🧪 Thought Experiment

**SETUP:**
You are inserting 10,000 `Order` rows. You have two choices:
`GenerationType.IDENTITY` (MySQL AUTO_INCREMENT) or
`GenerationType.SEQUENCE` with `allocationSize=50`.

**WHAT HAPPENS WITH IDENTITY:**
Hibernate must execute each INSERT individually and wait for
the database to return the generated key before issuing the
next INSERT. Batch insert is disabled. 10,000 round trips to
the database.

**WHAT HAPPENS WITH SEQUENCE (allocationSize=50):**
Hibernate calls `NEXT VALUE FOR order_seq` once, gets an ID
block (e.g. 1 to 50), then inserts rows 1-50 as a JDBC batch.
Then gets 51-100, batches those. Total: 200 sequence calls +
200 JDBC batches of 50 instead of 10,000 individual round
trips.

**THE INSIGHT:** The `@GeneratedValue` strategy choice is a
performance decision disguised as a mapping annotation.
`SEQUENCE` with a tuned `allocationSize` can be 5-10x faster
than `IDENTITY` for bulk insert workloads.

---

### 🧠 Mental Model / Analogy

> `@Id` is a parking space number painted on the ground.
> `@GeneratedValue` is the parking attendant who assigns
> you the next available space when you arrive.
> Without the attendant (no `@GeneratedValue`), you must
> find and paint your own number - which works until two
> cars arrive simultaneously and paint the same number.

- "Parking space number" - primary key value
- "Space itself" - the entity row
- "Parking attendant" - `@GeneratedValue` strategy
- "Finding your own number" - manual ID assignment
- "Two cars, same number" - race condition without generation

Where this analogy breaks down: a parking attendant assigns
spaces sequentially from a single counter. `UUID` generation
assigns IDs randomly from a 128-bit space - no attendant
needed, no counter, no coordination.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
`@Id` marks the field that uniquely identifies each record
in the database (the primary key). `@GeneratedValue` makes
the database assign it automatically when you save a new
record.

**Level 2 - How to use it (junior developer):**
Add `@Id` to the primary key field. Add
`@GeneratedValue(strategy = GenerationType.IDENTITY)` for
auto-increment (MySQL/PostgreSQL `SERIAL`). The field is
null before saving; after saving, Hibernate populates it
with the generated value. Use `Long` as the field type
for standard numeric IDs.

**Level 3 - How it works (mid-level engineer):**
With `IDENTITY`, Hibernate issues the INSERT and then calls
`JDBC.getGeneratedKeys()` to retrieve the auto-assigned key.
With `SEQUENCE`, Hibernate calls `SELECT NEXT VALUE FOR seq`
before the INSERT, uses the returned value as the ID, and
inserts with that value. The `allocationSize` parameter
lets Hibernate cache a block of IDs in memory - for
`allocationSize=50`, one sequence call covers 50 inserts.

**Level 4 - Why it was designed this way (senior/staff):**
`IDENTITY` is the simplest strategy but makes Hibernate
unable to batch inserts: it cannot reorder or batch
`INSERT` statements when it does not know the entity IDs
in advance. `SEQUENCE` pre-assigns IDs, enabling Hibernate
to build a JDBC batch for all inserts before sending to
the database. The `allocationSize` default of 50 means
the sequence increments by 50 in the database but Hibernate
uses 50 consecutive values in memory per allocation.
Setting `allocationSize=1` eliminates gaps but removes
the batching advantage.

**Level 5 - Mastery (distinguished engineer):**
ID strategy selection is a system-wide consistency decision.
`IDENTITY` in MySQL/PostgreSQL is idiomatic but blocks
`hibernate.jdbc.batch_size`. If bulk inserts are a use
case, switch to `SEQUENCE`. For distributed systems where
insert sources span multiple nodes (microservices writing
to a shared table), `UUID` eliminates coordination entirely
at the cost of storage (16 bytes vs 8 for Long) and index
performance (UUID v4 random values cause index fragmentation;
UUID v7 time-ordered values are B-tree friendly). In
high-throughput financial systems, `SEQUENCE` with a large
`allocationSize` (500-1000) is the standard pattern.

**Expert Thinking Cues:**
- Ask: "Does this entity need batch insert support?"
  If yes, `IDENTITY` is wrong; use `SEQUENCE`
- Watch: gaps in `SEQUENCE` values are normal due to
  `allocationSize` allocation and transaction rollbacks;
  never assume sequence values are gapless
- Know: composite keys (`@EmbeddedId`, `@IdClass`) are
  valid JPA but significantly complicate queries and
  repository method signatures - avoid unless the
  domain model genuinely requires them

---

### ⚙️ How It Works (Mechanism)

**ID Assignment Flow for Each Strategy:**

```
┌─────────────────────────────────────────────┐
│      ID GENERATION STRATEGY COMPARISON      │
├────────────────┬────────────────────────────┤
│ IDENTITY       │ 1. INSERT row (no id)       │
│                │ 2. DB assigns auto-inc id   │
│                │ 3. Hibernate reads key back  │
│                │ Batch: NOT POSSIBLE         │
├────────────────┼────────────────────────────┤
│ SEQUENCE       │ 1. SELECT NEXT VALUE        │
│ (alloc=50)     │ 2. Cache 50 IDs in memory   │
│                │ 3. INSERT with known ID     │
│                │ 4. After 50, repeat step 1  │
│                │ Batch: POSSIBLE             │
├────────────────┼────────────────────────────┤
│ TABLE          │ 1. SELECT from seq table    │
│                │ 2. UPDATE seq table         │
│                │ 3. INSERT with acquired ID  │
│                │ Batch: POSSIBLE, but slow   │
├────────────────┼────────────────────────────┤
│ UUID (manual)  │ 1. UUID.randomUUID() in Java│
│                │ 2. INSERT with UUID id      │
│                │ Batch: POSSIBLE             │
└────────────────┴────────────────────────────┘
```

**Key Hibernate Detail - `isNew()` detection:**
`SimpleJpaRepository.save()` calls `entityInformation.isNew(entity)`:
- If `@Id` is null/0 -> `persist()` (INSERT)
- If `@Id` is non-null/non-0 -> `merge()` (SELECT + UPDATE)

This means: if you manually set the `@Id` field before
calling `save()`, Spring Data will call `merge()` which
triggers a SELECT first. For `SEQUENCE` or `UUID` strategies
this is expected; for `IDENTITY` this is usually wrong.

**CONCURRENCY / THREAD-SAFETY BEHAVIOR:**
`IDENTITY`: database enforces uniqueness via `AUTO_INCREMENT`
lock; safe under concurrent inserts.
`SEQUENCE`: Hibernate increments by `allocationSize` in one
DB call; the database sequence itself is concurrency-safe.
`UUID.randomUUID()`: generates locally; cryptographic
randomness makes collision probability negligible.

---

### 🔄 The Complete Picture - End-to-End Flow

**SEQUENCE STRATEGY FLOW:**

```
em.persist(new Order(...))
    |
    v
[ Hibernate checks: id is null ]
    |   entity is NEW
    v
[ SEQUENCE strategy ]
    |   SELECT NEXT VALUE FOR order_seq
    |   DB returns: 51 (allocationSize=50)
    |   Cache range: 1-50 for next 50 inserts
    v
[ entity.id = 1 assigned in memory ]
    |
    v
[ ActionQueue: INSERT buffered ]
    |
    v
[ At flush: JDBC batch INSERT ]
    |   50 rows in one batch
    v
[ Transaction commit ]
    |
    v
[ Entity id = 1 confirmed in session ]
```

**FAILURE PATH:**
If the database sequence object is dropped or the sequence
table is corrupted (`TABLE` strategy), every persist fails
with `SequenceGenerationException`. The application cannot
insert any entity that uses the broken sequence.

**WHAT CHANGES AT SCALE:**
At 1000 inserts/second, `IDENTITY` strategy creates 1000
database round trips/second. `SEQUENCE` with `allocationSize=50`
reduces this to 20 sequence calls/second plus 20 JDBC batches
of 50. For high-throughput event ingestion, this is the
difference between saturating the database and headroom.

---

### 💻 Code Example

**Example 1 - IDENTITY strategy (simple, most common):**

```java
@Entity
public class Customer {

    @Id
    @GeneratedValue(
        strategy = GenerationType.IDENTITY)
    private Long id;  // null before persist

    private String email;

    protected Customer() {}

    public Customer(String email) {
        this.email = email;
        // id is null - database assigns it
    }
}

// Usage:
Customer c = new Customer("alice@example.com");
System.out.println(c.getId()); // null
em.persist(c);
em.flush();
System.out.println(c.getId()); // 1 (assigned)
```

**Example 2 - SEQUENCE strategy with allocationSize:**

```java
@Entity
@SequenceGenerator(
    name = "order_seq_gen",
    sequenceName = "order_seq",
    allocationSize = 50)  // DB increments by 50
public class Order {

    @Id
    @GeneratedValue(
        strategy = GenerationType.SEQUENCE,
        generator = "order_seq_gen")
    private Long id;

    private BigDecimal total;

    protected Order() {}
}

// With hibernate.jdbc.batch_size=50:
// 1000 inserts = 20 DB sequence calls
// + 20 JDBC batches of 50 rows each
```

**Example 3 - UUID as primary key:**

```java
@Entity
public class AuditLog {

    @Id
    // @GeneratedValue not needed for UUID
    private UUID id = UUID.randomUUID();

    private String action;
    private LocalDateTime timestamp =
        LocalDateTime.now();

    // UUID is assigned at construction time
    // No DB round trip needed for ID generation
    protected AuditLog() {}
    public AuditLog(String action) {
        this.action = action;
    }
}
```

**Example 4 - Composite key with @EmbeddedId:**

```java
// Only use when the domain genuinely requires it
@Embeddable
public class OrderItemId
        implements Serializable {
    private Long orderId;
    private Long productId;
    // equals() and hashCode() required
}

@Entity
public class OrderItem {

    @EmbeddedId
    private OrderItemId id;

    private int quantity;
    // No @GeneratedValue - composite key is
    // always assigned manually
}
```

---

### ⚖️ Comparison Table

| Strategy | DB Mechanism | Batch Insert | Gaps | Global Unique | Use Case |
|---|---|---|---|---|---|
| **IDENTITY** | AUTO_INCREMENT | No | Possible | No | Simple apps, MySQL default |
| SEQUENCE | DB sequence | Yes | Normal | No | High-throughput, PostgreSQL |
| TABLE | Sequence table | Yes | Normal | No | DB without sequences |
| UUID (manual) | Java UUID | Yes | N/A | Yes | Distributed, microservices |

**How to choose:**
Default to `IDENTITY` for simple Spring Boot applications
on MySQL/PostgreSQL. Switch to `SEQUENCE` when batch insert
performance matters. Use `UUID` when inserting from multiple
nodes without coordination, or when you need stable IDs before
database round-trips.

**Decision Tree:**
Bulk insert > 100 rows frequently? - Use SEQUENCE
Multi-node distributed inserts? - Use UUID (v7 for indexing)
Simple CRUD app, single node? - IDENTITY is fine
Database has no sequence support? - TABLE (last resort)

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "IDENTITY is always the best default" | IDENTITY is simplest but disables Hibernate batch insert. For bulk operations, SEQUENCE with a tuned `allocationSize` can be 5-10x faster. |
| "UUID primary keys have no downsides" | UUID v4 (random) causes B-tree index fragmentation on insert, leading to page splits and slower INSERT/SELECT performance at scale. UUID v7 (time-ordered) solves this. UUID columns are 16 bytes vs 8 for Long, doubling all FK storage. |
| "SEQUENCE values are always gapless" | Sequences skip values on transaction rollback and advance by `allocationSize` per allocation. Never use sequence values as invoice numbers or order numbers requiring gapless sequences. |
| "You can change an entity's @Id after persist" | Changing a managed entity's `@Id` value is undefined behaviour in the JPA spec. Hibernate may or may not detect the change, leading to duplicate-key errors or silent data corruption. |
| "@GeneratedValue is required with @Id" | `@GeneratedValue` is optional. Without it, you assign the ID value manually before `em.persist()`. This is valid for business keys (e.g. ISBN, tax number) that are known before insert. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Batch Insert Broken by IDENTITY Strategy**

**Symptom:** Bulk import of 50,000 rows takes 60 seconds;
SQL log shows 50,000 individual INSERT statements.
**Root Cause:** `GenerationType.IDENTITY` disables Hibernate
batch insert; `hibernate.jdbc.batch_size` has no effect.
**Diagnostic:**

```bash
# Enable statistics to see batch behaviour
spring.jpa.properties.hibernate.generate_statistics=true
# Look for: "Executed 50000 statements" vs "Executed 1000 batches"
logging.level.org.hibernate.stat=DEBUG
```

**Fix:**

```java
// BAD for bulk insert:
@GeneratedValue(
    strategy = GenerationType.IDENTITY)

// GOOD for bulk insert:
@SequenceGenerator(
    name = "product_seq",
    sequenceName = "product_seq",
    allocationSize = 50)
@GeneratedValue(
    strategy = GenerationType.SEQUENCE,
    generator = "product_seq")
```

**Prevention:** Use `SEQUENCE` strategy when bulk insert is
a known use case. Document the performance implication of
`IDENTITY` in the architecture decision record.

---

**Failure Mode 2: Duplicate Key from Manual ID Assignment**

**Symptom:** `org.hibernate.exception.ConstraintViolationException:
duplicate key value violates unique constraint "products_pkey"`.
**Root Cause:** Manual `@Id` assignment combined with
`@GeneratedValue(SEQUENCE)` - developer sets `product.setId(1L)`
then persists, but the sequence independently assigns ID 1.
**Diagnostic:**

```bash
# Check if entities have manually set IDs before save
spring.jpa.show-sql=true
# Look for INSERT with explicit ID values vs. SELECT NEXT VALUE
```

**Fix:** Never manually set an `@Id` field when using
`@GeneratedValue`. If a specific ID is needed (e.g. for
upsert), use `merge()` not `persist()`.
**Prevention:** Make the `@Id` setter package-private or
remove it entirely; only JPA should set generated IDs.

---

**Failure Mode 3: isNew() Triggering Unexpected SELECT**

**Symptom:** Spring Data `repository.save(entity)` executes
a SELECT before the INSERT, causing extra database round trips.
**Root Cause:** When saving an entity with a pre-assigned UUID
(non-null ID), Spring Data calls `merge()` instead of
`persist()` because `isNew()` returns false for non-null IDs.
**Diagnostic:**

```bash
spring.jpa.show-sql=true
# Look for SELECT before INSERT for new entities
# "select ... from products where id=?"
```

**Fix:**

```java
// Option 1: implement Persistable to override isNew()
@Entity
public class AuditLog
        implements Persistable<UUID> {
    @Id
    private UUID id = UUID.randomUUID();

    @Transient
    private boolean isNew = true;

    @Override
    public boolean isNew() { return isNew; }

    @PostPersist
    @PostLoad
    void markNotNew() { this.isNew = false; }
}
```

**Prevention:** Use `Persistable<ID>` interface when UUID
is assigned before persist; document the `isNew()` override
rationale.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[JPH-006 - @Entity]] - `@Id` is always required on
  an `@Entity` class; cannot exist without it

**Builds On This (learn these next):**
- [[JPH-008 - @Table and @Column]] - customising the column
  that `@Id` maps to
- [[JPH-011 - EntityManager]] - uses the `@Id` value for
  identity map lookup in `find()`
- [[JPH-013 - Entity Lifecycle (NEW, MANAGED, DETACHED, REMOVED)]] -
  `@Id` being null/zero determines whether an entity is NEW
- [[JPH-038 - Optimistic Locking (@Version)]] - works
  alongside `@Id` to detect concurrent modifications

**Alternatives / Comparisons:**
- [[JPH-040 - Inheritance Mapping Strategies (SINGLE_TABLE, JOINED, TABLE_PER_CLASS)]] -
  how `@Id` propagates through inheritance hierarchies

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ @Id: marks primary key field              │
│              │ @GeneratedValue: auto-assigns ID on insert │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Eliminates manual ID generation code and  │
│ SOLVES       │ race conditions in concurrent inserts     │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Strategy choice = batch insert capability:│
│              │ IDENTITY blocks batching; SEQUENCE enables│
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Every @Entity needs @Id. Use IDENTITY for │
│              │ simple apps; SEQUENCE for bulk insert     │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Never assign @Id manually with            │
│              │ @GeneratedValue active                    │
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ IDENTITY with hibernate.jdbc.batch_size - │
│              │ they are mutually exclusive               │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ IDENTITY: simple vs. no batch insert      │
│              │ SEQUENCE: batch ready vs. sequence gaps   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "@Id is the entity's name tag; strategy   │
│              │ decides who writes it on the tag"         │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ @Table -> @Column -> EntityManager -> save │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. `IDENTITY` disables Hibernate batch inserts - use
   `SEQUENCE` with `allocationSize` for bulk workloads
2. `@GeneratedValue` is optional - omit it when the ID
   is a natural business key known before insert
3. UUID IDs must implement `Persistable` to override
   `isNew()`, otherwise Spring Data calls `merge()` (SELECT
   + update) instead of `persist()` for new entities

**Interview one-liner:** `@Id` marks the primary key field;
`@GeneratedValue` configures the automatic assignment strategy.
The choice between `IDENTITY` (simple, no batch) and
`SEQUENCE` (batch-enabled via `allocationSize`) is a
performance trade-off that affects bulk insert throughput
by up to 10x.

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Identity assignment in
distributed systems is always a trade-off between coordination
cost and uniqueness guarantee. Central sequences require
coordination but are ordered; UUIDs require no coordination
but are unordered (affecting index performance). The
correct choice is determined by the system's insertion
rate, distribution of insert sources, and downstream
query patterns.

**Where else this pattern appears:**
- **Distributed databases (Cassandra, DynamoDB)** - partition
  keys are manually assigned UUIDs or composite keys; no
  auto-increment equivalent because coordination is impossible
- **Event streaming (Kafka)** - message offsets are sequence
  numbers within a partition; exactly the same allocationSize
  concept applies to offset reservation
- **URL shorteners** - assigning short codes to URLs is an
  identity generation problem; centralized sequence vs.
  distributed random ID vs. hash-based are the same
  trade-offs as JPA ID strategies

**Industry applications:**
- E-commerce order processing: `SEQUENCE` strategy with
  `allocationSize=100` enables batching 10,000+ orders/minute
  during flash sales without database saturation
- Audit logging in financial systems: UUID primary keys
  allow audit records to be generated on multiple service
  nodes simultaneously and merged into a single audit table
  without coordination or duplicate-key conflicts

---

### 💡 The Surprising Truth

Hibernate's default `GenerationType.AUTO` on PostgreSQL
does NOT use `SERIAL` / `IDENTITY` columns as most developers
expect. It uses a shared `hibernate_sequence` table that all
entities share - meaning every entity's ID increments from
the same counter. This causes IDs to jump unexpectedly
(Customer ID 1, then Order ID 2, then Customer ID 3) and
creates contention under concurrent inserts. The correct
choice on PostgreSQL is always explicit
`GenerationType.SEQUENCE` with a per-entity sequence.
This is one of the most common Hibernate misconfiguration
issues in production PostgreSQL systems.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN** why `GenerationType.IDENTITY` disables
   Hibernate batch inserts, tracing the mechanism from
   ID assignment timing through JDBC batch requirements
2. **DEBUG** a bulk insert performance problem where
   `hibernate.jdbc.batch_size=50` has no effect, identify
   that `IDENTITY` strategy is the cause, and propose
   the correct fix with `SEQUENCE` and `allocationSize`
3. **DECIDE** between `IDENTITY`, `SEQUENCE`, and `UUID`
   for a given scenario (simple CRUD, bulk import, or
   distributed multi-node insert) with clear reasoning
   for each choice
4. **BUILD** a `@SequenceGenerator` configuration with
   `allocationSize=50` and verify via Hibernate statistics
   that 1000 inserts trigger 20 sequence calls and 20
   JDBC batches rather than 1000 round trips
5. **EXTEND** the UUID identity pattern to a distributed
   microservices scenario and implement `Persistable<UUID>`
   to prevent Spring Data from issuing a SELECT before
   every INSERT

---

### 🧠 Think About This Before We Continue

**Q1 (TYPE B - Scale):** Your application uses
`GenerationType.SEQUENCE` with `allocationSize=50`.
At 1000 inserts/second, the sequence is called 20 times/second.
What happens if the sequence call fails (database unreachable
for 100ms)? How many entity inserts fail, and what does
Hibernate do with the partially allocated ID block?
*Hint: Consider what happens to in-memory ID allocations
when the transaction rolls back, and whether Hibernate
reuses the allocated IDs after a failure.*

**Q2 (TYPE C - Design Trade-off):** UUID v4 (random) causes
index fragmentation at scale; UUID v7 (time-ordered) solves
this but requires Java 17+ or a UUID library. SEQUENCE is
ordered but requires a database sequence object. How would
you choose between UUID v7 and SEQUENCE for the primary key
of a high-throughput events table in a distributed system
where events are written from 10 service instances?
*Hint: Consider database index page fill factor, the cost
of a distributed sequence lock vs. local UUID generation,
and what happens during a database failover for each strategy.*

**Q3 (TYPE G - Hands-On):** Create a benchmark Spring Boot
test that inserts 10,000 `Order` entities using three
strategies: `IDENTITY`, `SEQUENCE(allocationSize=50)`, and
`SEQUENCE(allocationSize=500)`. Measure total insert time
and sequence call count for each. What configuration is
required to enable JDBC batching, and what `application.properties`
settings interact with the ID strategy?
*Hint: `hibernate.jdbc.batch_size`, `hibernate.order_inserts`,
`hibernate.generate_statistics`, and the `@SequenceGenerator`
`allocationSize` all interact. Use `Statistics.getPrepareStatementCount()`
to verify actual query counts.*

---

### 🎯 Interview Deep-Dive

**Q1: What is the difference between
`GenerationType.IDENTITY` and `GenerationType.SEQUENCE`,
and when would you choose each?**
*Why they ask:* Tests performance awareness - a common
interview distinction between experienced and inexperienced
JPA developers.
*Strong answer includes:*
- `IDENTITY`: DB assigns ID via AUTO_INCREMENT after INSERT;
  Hibernate cannot batch because it does not know the ID
  before inserting
- `SEQUENCE`: Hibernate calls `NEXT VALUE FOR seq` before
  INSERT, enabling JDBC batch; `allocationSize` controls
  how many IDs are pre-fetched per sequence call
- Choose `SEQUENCE` when bulk inserts matter; `IDENTITY`
  for simple single-row CRUD apps

**Q2: A developer reports that `hibernate.jdbc.batch_size=50`
has no effect - each insert is still individual. What is
the most likely cause and fix?**
*Why they ask:* Tests knowledge of a real production gotcha
that trips up most developers the first time.
*Strong answer includes:*
- Most likely cause: `GenerationType.IDENTITY` is used;
  it disables batching because Hibernate cannot reorder
  inserts without knowing the IDs first
- Fix: switch to `SEQUENCE` strategy and add
  `hibernate.order_inserts=true` to allow Hibernate to
  sort inserts by entity type before batching
- Verify: `hibernate.generate_statistics=true` shows
  statement count; should drop from N to N/50

**Q3: What problems arise when using UUID as a primary
key, and how do you mitigate them?**
*Why they ask:* Tests depth of UUID knowledge beyond "it's
globally unique" - a senior-level distinction.
*Strong answer includes:*
- UUID v4 (random): B-tree index fragmentation on insert
  (random values go to random index pages, causing constant
  page splits); 2-3x slower inserts vs. sequential keys
- Mitigation: use UUID v7 (time-ordered, available in Java
  via a UUID library); it clusters inserts in the B-tree
  like sequential IDs
- Implement `Persistable<UUID>` to prevent Spring Data's
  `isNew()` from triggering a SELECT before every INSERT