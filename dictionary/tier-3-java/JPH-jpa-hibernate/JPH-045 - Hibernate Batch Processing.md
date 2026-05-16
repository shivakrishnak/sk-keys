---
id: JPH-045
title: Hibernate Batch Processing
category: JPA & Hibernate
tier: tier-3-java
folder: JPH-jpa-hibernate
difficulty: ★★★
depends_on: JPH-011, JPH-012, JPH-013, JPH-026, JPH-031, JPH-033
used_by: JPH-046, JPH-054, JPH-058
related: JPH-027, JPH-039, JPH-047, JPH-052
tags:
  - java
  - jpa
  - database
  - advanced
status: complete
version: 4
layout: default
parent: "JPA & Hibernate"
grand_parent: "Technical Dictionary"
nav_order: 45
permalink: /jpa-hibernate/hibernate-batch-processing/
---

# JPH-045 - Hibernate Batch Processing

⚡ **TL;DR** - Hibernate batch processing groups multiple
SQL INSERT/UPDATE/DELETE statements into a single JDBC
`addBatch()` / `executeBatch()` call, reducing roundtrips.
Enable with `hibernate.jdbc.batch_size=50`. Critical: also
set `hibernate.order_inserts=true` and `hibernate.order_updates=true`
(groups same-table statements together to fill batches).
Must call `em.flush()` + `em.clear()` every N entities or
the persistence context grows unboundedly (OOM). For bulk
operations, `@Modifying @Query` is faster (no entity loading).

| #045            | Category: JPA & Hibernate                                                                                                | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | EntityManager, Session/Transaction, JPA Lifecycle, @Transactional, Hibernate Session vs EntityManager, First Level Cache |                 |
| **Used by:**    | Hibernate Statistics, JPA at Scale, Hibernate Internals                                                                  |                 |
| **Related:**    | N+1 Problem, Pessimistic Locking, Connection Pooling, Dirty Checking                                                     |                 |

---

### 🔥 The Problem This Solves

**INSERTING 100,000 ENTITIES WITHOUT BATCHING:**

```java
@Transactional
public void importProducts(List<ProductDto> products) {
    for (ProductDto dto : products) {
        productRepo.save(new Product(dto));
        // Each save: individual INSERT to DB
        // 100,000 products = 100,000 network roundtrips
        // Time: ~10-30 seconds (1 roundtrip ~100-300 microseconds)
        // Memory: persistence context holds 100,000 entities
    }
}
// Duration: ~30 seconds for 100,000 rows on local DB
```

**WITH HIBERNATE BATCH INSERT:**

```java
@Transactional
public void importProducts(List<ProductDto> products) {
    int batchSize = 50;
    for (int i = 0; i < products.size(); i++) {
        em.persist(new Product(products.get(i)));
        if (i % batchSize == 0 && i > 0) {
            em.flush();  // Execute batch: 50 INSERTs in 1 call
            em.clear();  // Evict entities from persistence context
        }
    }
    em.flush(); // Final batch
}
// Duration: ~3 seconds for 100,000 rows
// 100,000 / 50 = 2,000 JDBC executeBatch() calls
// vs 100,000 individual roundtrips
```

---

### 📘 Textbook Definition

**Hibernate Batch Processing** accumulates SQL statements
in a JDBC `PreparedStatement` batch buffer. When the buffer
reaches `hibernate.jdbc.batch_size`, Hibernate calls
`PreparedStatement.executeBatch()` to send all accumulated
statements in a single server roundtrip.

**Configuration properties:**

- `hibernate.jdbc.batch_size=50` - number of statements
  per batch (50-100 typical for INSERTs; test for your workload)
- `hibernate.order_inserts=true` - sort INSERT statements
  by table so same-table INSERTs are grouped (required for batching
  with multiple entity types to work efficiently)
- `hibernate.order_updates=true` - same for UPDATEs
- `hibernate.jdbc.batch_versioned_data=true` - enables
  batching for entities with `@Version` (off by default due
  to JDBC batching limitations with row count verification)

**Batch processing modes:**

- `em.persist()` loop + `flush()/clear()` - for INSERT batching
- `@Modifying @Query("UPDATE ...")` - bulk UPDATE (no entity loading)
- `@Modifying @Query("DELETE ...")` - bulk DELETE (no entity loading)
- `StatelessSession` (Hibernate-specific) - bypasses persistence
  context entirely; higher throughput for write-only imports

---

### ⏱️ Understand It in 30 Seconds

**One line:** Hibernate batching groups multiple INSERTs/
UPDATEs into a single JDBC call, reducing network roundtrips
from N to N/batchSize. Must flush+clear periodically to
prevent OOM.

**One analogy:**

> Without batching: a grocery store cashier scans one item,
> walks to the register, punches it in, walks back, scans
> next item. 100 items = 100 trips.
>
> With batching: cashier scans 50 items, walks once to the
> register, punches all 50 in one go. 100 items = 2 trips.
>
> The "register trip" is the network roundtrip to the database.
> Batching reduces trips by grouping multiple SQL statements
> into one executeBatch() call.

**One insight:** The `flush() + clear()` every N entities
is NOT optional. `flush()` sends the batch to the database.
`clear()` evicts entities from the first-level cache.
Without `clear()`, the persistence context grows unboundedly
(every persisted entity stays in memory), causing OOM for
large imports. The pattern is mandatory for bulk operations.

---

### 🔩 First Principles Explanation

**HOW JDBC BATCHING WORKS:**

```
Without batching:
  PreparedStatement ps = conn.prepareStatement(
      "INSERT INTO products ...");
  for each entity:
    ps.setString(1, name); ps.setInt(2, price); ...
    ps.executeUpdate();  // 1 roundtrip per entity
    // 100,000 entities = 100,000 executeUpdate() calls

With batching (batch_size=50):
  PreparedStatement ps = conn.prepareStatement(
      "INSERT INTO products ...");
  for each entity:
    ps.setString(1, name); ps.setInt(2, price); ...
    ps.addBatch();           // queue the statement
    if (count % 50 == 0):
      ps.executeBatch();     // 1 roundtrip for 50 statements
  ps.executeBatch();         // final batch

100,000 / 50 = 2,000 executeBatch() calls
vs 100,000 executeUpdate() calls
~50x fewer roundtrips (actual speedup depends on latency)
```

**WHY order_inserts IS NEEDED:**

```
Without order_inserts: entities persist in creation order
  Entity type A -> INSERT INTO table_a
  Entity type B -> INSERT INTO table_b
  Entity type A -> INSERT INTO table_a  (new batch! A+B mixed)
  Entity type B -> INSERT INTO table_b  (new batch!)
  Each table switch breaks the current batch -> many small batches

With order_inserts=true:
  All entity type A INSERTs grouped: -> fill full 50-row batches
  All entity type B INSERTs grouped: -> fill full 50-row batches
  Maximizes batch fill factor; fewer executeBatch() calls
```

---

### 🧪 Thought Experiment

**BULK UPDATE: @Modifying QUERY vs LOOP:**

```java
// Scenario: deactivate all expired products
// (products where expiresAt < now)

// Option A: Loop (EntityManager-based)
@Transactional
public void deactivateExpired() {
    List<Product> expired = productRepo
        .findAllByExpiresAtBefore(Instant.now());
    // SELECT: loads 50,000 Product entities into 1LC
    for (Product p : expired) {
        p.setActive(false);
        // 50,000 entity objects in memory
    }
    // At flush: 50,000 UPDATE statements (batched if configured)
    // Still: 50,000 entities in heap; GC pressure
}
// Time: 50,000 SELECTs (1 query) + 50,000 UPDATEs
// Memory: 50,000 Product objects on heap

// Option B: @Modifying bulk UPDATE
@Transactional
@Modifying
@Query("UPDATE Product p SET p.active=false " +
       "WHERE p.expiresAt < :now")
void deactivateExpiredBulk(@Param("now") Instant now);
// Time: 1 SQL UPDATE statement; no entity loading
// Memory: 0 entities loaded; SQL engine handles it
// 100x+ faster for large row counts

// Choice:
// Bulk @Modifying: best for updating many rows without
//   needing to apply complex business logic per entity
// Loop: needed when per-entity logic is required
//   (trigger lifecycle events, validate per entity, etc.)
```

---

### 🧠 Mental Model / Analogy

> Think of Hibernate batch processing as filling a truck
> before a delivery run. Without batching: a courier picks
> up one package from the warehouse, drives to the delivery
> address (database), drops it off, drives back, picks
> up the next package. 1,000 packages = 1,000 round trips.
>
> With batching (batch_size=50): courier loads 50 packages
> into the truck, makes one trip to the database, delivers
> all 50, drives back. 1,000 packages = 20 round trips.
>
> The `flush()` is "load the truck and go". The `clear()`
> is "the empty warehouse is now free for the next 50
> packages" (evict entities from memory to prevent OOM).

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Hibernate batching groups multiple database INSERT/UPDATE
operations into a single call, instead of one call per
record. This is much faster for importing thousands of
records.

**Level 2 - How to enable it (junior developer):**

```properties
spring.jpa.properties.hibernate.jdbc.batch_size=50
spring.jpa.properties.hibernate.order_inserts=true
spring.jpa.properties.hibernate.order_updates=true
```

Then in the import loop: `em.flush(); em.clear()` every
N entities. Both properties and the flush/clear loop are
required for effective batching.

**Level 3 - How it works (mid-level engineer):**
Hibernate accumulates `PreparedStatement.addBatch()` calls
until the batch size is reached, then fires `executeBatch()`.
`order_inserts` groups same-table statements so batches
are full. Without `clear()`, every persisted entity
accumulates in the first-level cache, eventually causing
OOM for large imports.

**Level 4 - StatelessSession (senior engineer):**
`Session.unwrap()` or `SessionFactory.openStatelessSession()`
opens a Hibernate `StatelessSession` - no first-level cache,
no dirty checking, no lifecycle events. For pure write
imports (no callbacks needed), `StatelessSession` is 2-5x
faster than regular Session because it skips all persistence
context overhead:

```java
try (StatelessSession ss = sf.openStatelessSession()) {
    Transaction tx = ss.beginTransaction();
    for (ProductDto dto : products) {
        ss.insert(new Product(dto)); // direct INSERT; no 1LC
        // No flush/clear needed - no persistence context!
    }
    tx.commit();
}
```

**Level 5 - SEQUENCE vs IDENTITY generators for batching (staff engineer):**
`@GeneratedValue(strategy = GenerationType.IDENTITY)` (MySQL
AUTO_INCREMENT, PostgreSQL SERIAL) forces Hibernate to
execute each INSERT individually before batching, because
the database generates the ID AFTER INSERT and Hibernate
needs the ID for the persistence context. This effectively
DISABLES batching for IDENTITY-generated IDs.
Solution: use `SEQUENCE` strategy:

```java
@GeneratedValue(strategy = GenerationType.SEQUENCE,
    generator = "product_seq")
@SequenceGenerator(name="product_seq",
    sequenceName="product_id_seq",
    allocationSize=50)  // pre-allocate 50 IDs
```

Hibernate pre-allocates 50 IDs in one sequence call,
then batches 50 INSERTs without individual SELECT calls.
This is why `SEQUENCE` + batching outperforms `IDENTITY` + batching.

---

### ⚙️ How It Works (Mechanism)

**STANDARD BATCH INSERT PATTERN:**

```java
@Service
@RequiredArgsConstructor
public class ProductImportService {

    @PersistenceContext
    private EntityManager em;

    private static final int BATCH_SIZE = 50;

    @Transactional
    public void batchImport(List<ProductDto> products) {
        for (int i = 0; i < products.size(); i++) {
            Product product = new Product();
            product.setName(products.get(i).getName());
            product.setPrice(products.get(i).getPrice());
            em.persist(product);

            // Every BATCH_SIZE entities: flush + clear
            if (i > 0 && i % BATCH_SIZE == 0) {
                em.flush();
                // -> executeBatch() for BATCH_SIZE INSERTs
                em.clear();
                // -> evict all entities from 1LC
                // -> frees heap memory for next batch
            }
        }
        // Final batch (remaining entities):
        em.flush();
        // DO NOT call clear() after last flush if you
        // need entities for post-processing
    }
}
```

**CONFIGURATION:**

```properties
# application.properties:
spring.jpa.properties.hibernate.jdbc.batch_size=50
spring.jpa.properties.hibernate.order_inserts=true
spring.jpa.properties.hibernate.order_updates=true
spring.jpa.properties.hibernate.jdbc.batch_versioned_data=true
# batch_versioned_data: enable batching for @Version entities
# (Hibernate checks row counts after batch; some drivers support this)

# Verify batching with statistics:
spring.jpa.properties.hibernate.generate_statistics=true
# Check stats: sf.getStatistics().getPrepareStatementCount()
```

---

### 🔄 The Complete Picture - End-to-End Flow

**STATELESS SESSION IMPORT:**

```java
@Component
@RequiredArgsConstructor
public class BulkProductImporter {

    private final SessionFactory sessionFactory;

    public void bulkImport(List<ProductDto> products) {
        // StatelessSession: no 1LC, no dirty checking, no events
        try (StatelessSession session =
                 sessionFactory.openStatelessSession()) {
            Transaction tx = session.beginTransaction();

            try {
                for (ProductDto dto : products) {
                    Product product = new Product(dto);
                    session.insert(product);
                    // Direct INSERT; no persistence context
                    // No flush/clear needed; no heap accumulation
                }
                tx.commit();
            } catch (Exception e) {
                tx.rollback();
                throw e;
            }
        }
        // 100,000 rows: StatelessSession + batch=50
        // -> ~2,000 executeBatch calls
        // -> ~5-10 seconds (vs ~30 without batching)
    }
}
```

---

### 💻 Code Example

**Example 1 - BAD: batch_size configured but no flush/clear:**

```java
// BAD: batch_size set but missing flush/clear loop
@Transactional
public void importWithoutClear(List<ProductDto> products) {
    for (ProductDto dto : products) {
        em.persist(new Product(dto));
        // No flush/clear!
    }
    // All 100,000 products stay in 1LC (heap)
    // em.flush() at transaction end sends all 100,000
    // But: 100,000 Product objects accumulate in heap
    // -> OutOfMemoryError for large imports
    // -> Even if OOM doesn't occur: GC pressure, slow
}

// GOOD: flush+clear every batch
@Transactional
public void importWithBatch(List<ProductDto> products) {
    for (int i = 0; i < products.size(); i++) {
        em.persist(new Product(products.get(i)));
        if (i > 0 && i % 50 == 0) {
            em.flush();
            em.clear();
        }
    }
    em.flush();
}
```

**Example 2 - IDENTITY generator disables batching (diagnosis):**

```java
// BAD: IDENTITY strategy = batching disabled
@Entity
public class Product {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    // MySQL auto_increment / PostgreSQL serial
    private Long id;
    // Hibernate must execute INSERT, get generated ID,
    // then store in 1LC - cannot batch!
}

// GOOD: SEQUENCE strategy = batching works
@Entity
public class Product {
    @Id
    @GeneratedValue(strategy = GenerationType.SEQUENCE,
                    generator = "product_gen")
    @SequenceGenerator(name = "product_gen",
                       sequenceName = "product_seq",
                       allocationSize = 50)
    // 1 sequence call gives 50 IDs; batches 50 INSERTs
    private Long id;
}
```

---

### ⚖️ Comparison Table

| Approach                       | Use case             | Memory        | Speed               | Complexity  |
| ------------------------------ | -------------------- | ------------- | ------------------- | ----------- |
| `em.persist()` loop (no batch) | Small datasets       | O(N)          | Slow (N roundtrips) | Low         |
| `em.persist()` + flush/clear   | Large INSERT batches | O(batch_size) | Fast                | Medium      |
| `StatelessSession.insert()`    | Very large imports   | Minimal       | Very fast           | Medium-High |
| `@Modifying @Query UPDATE`     | Bulk UPDATE/DELETE   | Minimal       | Fastest             | Low         |

---

### ⚠️ Common Misconceptions

| Misconception                                                | Reality                                                                                                                                                                                                                                                                      |
| ------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Setting hibernate.jdbc.batch_size is enough for batching"   | You also need `order_inserts=true` and `order_updates=true` for full batch efficiency. And you MUST call `flush() + clear()` every N entities in the loop - without it, the persistence context grows unboundedly.                                                           |
| "IDENTITY generator works fine with batching"                | IDENTITY generators (auto_increment) force individual INSERT execution because Hibernate needs the generated ID before proceeding. Use `SEQUENCE` with `allocationSize` matching batch_size for true batching.                                                               |
| "@Transactional means all INSERTs are batched automatically" | `@Transactional` opens a transaction but does not enable batching. Batching requires `hibernate.jdbc.batch_size` configuration AND the `flush() + clear()` pattern in code. Without explicit configuration, every `persist()` results in an individual INSERT at flush time. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode: OutOfMemoryError During Bulk Import**

**Symptom:** Application OOM during large data import.
Heap dump shows millions of entity objects in memory.
**Root Cause:** Missing `em.clear()` in the import loop.
Every `em.persist()` entity is held in the first-level cache.
100,000 entities with 10 fields each = millions of objects
in the persistence context map.
**Diagnosis:**

```java
// Add logging to confirm clear() is firing:
if (i > 0 && i % batchSize == 0) {
    em.flush();
    em.clear();
    log.debug("Batch {}: flush+clear executed",
              i / batchSize);
}
// If log never appears: clear is NOT being called
```

**Fix:** Add `em.flush(); em.clear();` inside the loop
at every `batchSize` interval. Use `StatelessSession`
for extreme throughput requirements.

---

**Failure Mode: Batching Not Happening (Statistics Show N Statements)**

**Symptom:** `hibernate.generate_statistics=true` shows
`PrepareStatementCount = N` (same as entity count).
Batching should reduce to N/batchSize.
**Root Cause:** Either `IDENTITY` generator used (disables
batching), or `order_inserts=false` (mixed-table statements
break batch grouping).
**Diagnosis:**

```java
Statistics stats = sessionFactory.getStatistics();
long prepStmts = stats.getPrepareStatementCount();
long entities  = entityCount;
double ratio   = (double) prepStmts / entities;
// If ratio ≈ 1.0: batching not working
// If ratio ≈ 1/batchSize: batching working correctly
```

**Fix:** Switch from IDENTITY to SEQUENCE generator;
set `order_inserts=true`; verify `batch_size` property
is set (Spring property: `spring.jpa.properties.hibernate.jdbc.batch_size`).

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[JPH-033 - First Level Cache]] - flush+clear pattern
  manages the 1LC during batch operations
- [[JPH-031 - Hibernate Session vs EntityManager]] -
  StatelessSession is a Hibernate extension for batch processing

**Builds On This (learn these next):**

- [[JPH-046 - Hibernate Statistics and Monitoring]] -
  verify batch effectiveness with statistics API

**Related:**

- [[JPH-027 - N+1 Problem]] - batch loading (@BatchSize)
  is different from batch INSERT/UPDATE
- [[JPH-052 - Dirty Checking and Flush Mode]] - flush
  mode controls when dirty checking and SQL execution occur

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ CONFIG       │ hibernate.jdbc.batch_size=50              │
│              │ hibernate.order_inserts=true              │
│              │ hibernate.order_updates=true              │
├──────────────┼───────────────────────────────────────────┤
│ PATTERN      │ em.persist(entity)                        │
│              │ if (i % batchSize == 0) {                 │
│              │   em.flush(); em.clear(); }               │
├──────────────┼───────────────────────────────────────────┤
│ IDENTITY     │ DISABLES batching; use SEQUENCE instead   │
│ SEQUENCE     │ allocationSize = batch_size for best perf │
├──────────────┼───────────────────────────────────────────┤
│ STATELESS    │ SessionFactory.openStatelessSession()      │
│              │ No 1LC; faster; no lifecycle events       │
├──────────────┼───────────────────────────────────────────┤
│ BULK OP      │ @Modifying @Query fastest for UPDATE/DELETE│
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "batch_size + order_inserts + flush/clear │
│              │ = 50x fewer roundtrips. SEQUENCE not      │
│              │ IDENTITY. StatelessSession for imports."  │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Configure `batch_size`, `order_inserts`, `order_updates`;
   call `em.flush(); em.clear()` every N entities in the loop
2. `IDENTITY` generator (auto_increment) disables batching;
   use `SEQUENCE` with `allocationSize = batchSize` instead
3. `@Modifying @Query("UPDATE ...")` is faster than loading
   entities and updating in a loop - bypasses persistence context

**Interview one-liner:** Hibernate JDBC batching groups
multiple SQL statements into a single `executeBatch()` call,
reducing network roundtrips by N/batchSize. Requires:
`hibernate.jdbc.batch_size`, `order_inserts=true`, and
`em.flush()+em.clear()` every N entities to prevent OOM.
`IDENTITY` generators disable batching; use `SEQUENCE` with
matching `allocationSize`. `StatelessSession` bypasses the
persistence context entirely for highest-throughput imports.

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Batching is a universal
optimization pattern: reduce the number of expensive
operations (network roundtrips, API calls, file system
syncs) by grouping them. The same pattern applies to:
Kafka producer `batch.size` + `linger.ms` (batch messages
before sending), Elasticsearch bulk API (batch documents
per index request), Redis pipelining (batch commands
before network send), AWS SDK S3 multipart upload (batch
upload parts), HTTP/2 multiplexing (batch requests over
single TCP connection). In all cases: higher throughput,
lower latency per-item, at the cost of increased latency
for the first item (must wait to fill the batch). Batch
size is a tuning parameter: too small = frequent small
batches; too large = high memory, slow first-item latency.

**Where else this pattern appears:**

- **Spring Batch** - framework for batch processing jobs;
  chunk-oriented processing = read N, process N, write N
- **JDBC `addBatch()` / `executeBatch()`** - raw JDBC
  batching; Hibernate wraps this
- **Redis pipelining** - `Jedis.pipelined()` / Lettuce
  pipeline mode - same reduce-roundtrips concept

---

### 💡 The Surprising Truth

Setting `hibernate.jdbc.batch_size=50` in Spring Boot
properties requires using the FULL key prefix:
`spring.jpa.properties.hibernate.jdbc.batch_size=50`.
Many developers use `spring.jpa.hibernate.ddl-auto=update`
and think `spring.jpa.hibernate.jdbc.batch_size=50`
should work by the same pattern. But it doesn't - the
`spring.jpa.hibernate.*` shorthand only works for a few
specific properties. For ALL other Hibernate properties
(including batch_size, order_inserts, order_updates,
statistics, etc.), the full prefix
`spring.jpa.properties.hibernate.*` is required.
Without this, the property is silently ignored and batching
never activates. Verify by checking if
`sf.getStatistics().getEntityInsertCount()` divided by
`sf.getStatistics().getPrepareStatementCount()` equals
roughly `batchSize`. If ratio is ~1: batching is not working.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **IMPLEMENT** a batch import with `em.persist()`,
   `flush()`, `clear()` loop using the correct batch size
2. **EXPLAIN** why `IDENTITY` generator disables batching
   and how `SEQUENCE` with `allocationSize` fixes it
3. **VERIFY** batching is working using Hibernate statistics
   (prepareStatementCount vs entityInsertCount ratio)
4. **COMPARE** regular Session + batch vs `StatelessSession`
   for write-heavy imports
5. **DECIDE** when `@Modifying @Query` is preferable to
   entity-based batch loops

---

### 🎯 Interview Deep-Dive

**Q1: How do you implement efficient batch insert of 100,000
records using JPA/Hibernate?**
_Why they ask:_ Common performance engineering question.
_Strong answer includes:_

- Configure: `hibernate.jdbc.batch_size=50`, `order_inserts=true`,
  `order_updates=true`
- Loop with flush+clear every 50 entities
- Use SEQUENCE generator (not IDENTITY) - IDENTITY disables batching
- Optional: `StatelessSession` for maximum throughput (no 1LC)
- Mention: `@Modifying @Query` for bulk UPDATE/DELETE (no entity loading)

**Q2: Why does using GenerationType.IDENTITY disable Hibernate
batching and how do you fix it?**
_Why they ask:_ Tests deep knowledge of ID generation + batching interaction.
_Strong answer includes:_

- `IDENTITY` = database generates ID after INSERT (auto_increment, SERIAL)
- Hibernate needs the generated ID to store entity in 1LC IMMEDIATELY
- Must execute INSERT individually (not batch) to get the ID via `getGeneratedKeys()`
- Cannot add to batch: `executeBatch()` deferred execution would
  mean IDs are not available until batch fires
- Fix: `GenerationType.SEQUENCE` with `allocationSize=50`
  (matches batch_size); Hibernate pre-allocates 50 IDs from sequence,
  assigns them to entities BEFORE INSERTs, then batches all 50
