---
id: JPH-033
title: First Level Cache (Persistence Context Cache)
category: JPA & Hibernate
tier: tier-3-java
folder: JPH-jpa-hibernate
difficulty: ★★☆
depends_on: JPH-011, JPH-012, JPH-013, JPH-026, JPH-027, JPH-031
used_by: JPH-034, JPH-038, JPH-045, JPH-052, JPH-058
related: JPH-028, JPH-037
tags:
  - java
  - jpa
  - database
  - intermediate
status: complete
version: 4
layout: default
parent: "JPA & Hibernate"
grand_parent: "Technical Mastery"
nav_order: 33
permalink: /technical-mastery/jpa-hibernate/first-level-cache/
---

⚡ **TL;DR** - The first-level cache (1LC) IS the
persistence context: a `Map<EntityKey, Object>` keyed
by entity type + primary key, held for the lifetime of
the session/transaction. It guarantees identity within
a transaction: `em.find(Product.class, 1L)` called twice
returns the SAME Java object. It is always enabled, cannot
be disabled, and is automatically cleared when the session/
transaction closes. Memory problems in batch processing
come from unbounded 1LC growth - fix with `em.clear()` or
`em.evict()` periodically.

| #033            | Category: JPA & Hibernate                                                                                             | Difficulty: ★★☆ |
| :-------------- | :-------------------------------------------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | EntityManager, Persistence Context, Entity Lifecycle, @Transactional, N+1 Problem, Hibernate Session vs EntityManager |                 |
| **Used by:**    | Second Level Cache, Optimistic Locking, Batch Processing, Dirty Checking and Flush Mode, Hibernate Internals          |                 |
| **Related:**    | HQL, EntityGraph                                                                                                      |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Without a first-level cache, every `em.find()` call
goes to the database even if the same entity was just
loaded 1 line earlier. Within a service method that loads
an Order, its Customer, and then the Customer again for
validation - 3 SELECT queries would hit the DB when
only 1 is needed.

**THE ENTITY IDENTITY PROBLEM:**
Without the 1LC, two calls to `em.find(Product.class, 1L)`
within the same transaction return two separate Java
objects representing the same database row. Modifying
one Java object does not affect the other. Your in-memory
model is out of sync with itself. Dirty checking would
not know which copy to compare.

**THE 1LC SOLUTION:**
The persistence context acts as a per-transaction
identity map: guarantees that within one transaction,
each entity (by type + id) exists as exactly one Java
object. All references to `product(id=1)` within the
transaction point to the same object. Loading it twice
returns the same reference. Modifying it via any
reference is visible everywhere in the same transaction.

---

### 📘 Textbook Definition

**First Level Cache (1LC)** is the in-memory cache
maintained by the persistence context (Hibernate Session /
EntityManager) for the duration of the session's lifetime.
It is a `Map<EntityKey, Object>` where `EntityKey = (EntityClass, primaryKey)`.

**Key properties:**

- Always enabled; cannot be configured off
- Scoped to a single Session/EntityManager (transaction-scoped in Spring)
- Guarantees within-session identity: same entity loaded twice
  returns the same Java object reference
- Provides dirty checking: snapshot of original state stored
  alongside the entity for comparison at flush time
- Cleared automatically when the session closes
- Manual control: `em.clear()` (evict all), `em.unwrap(Session.class).evict(entity)` (evict one)

**Identity Map Pattern:** The 1LC implements the
Identity Map pattern from "Patterns of Enterprise Application
Architecture" (Fowler, 2002): ensures that each object
gets loaded only once by keeping every loaded object in
a map. Lookups check the map before going to the database.

---

### ⏱️ Understand It in 30 Seconds

**One line:** The first-level cache is a per-transaction
map of loaded entities - same entity loaded twice in the
same transaction hits the cache (no second DB query)
and returns the same Java object.

**One analogy:**

> The first-level cache is your desk during a work session.
> Every document you pull from the filing cabinet (database)
> goes on your desk (1LC). If you need the same document
> again, you pick it up from your desk - no second trip
> to the cabinet. When you leave for the day (transaction
> ends), your desk is cleared (1LC flushed and closed).
> Tomorrow's session starts with an empty desk.

**One insight:** The 1LC is NOT a performance cache in
the traditional sense. It is first and foremost the
mechanism for transaction-scoped entity identity.
Avoiding redundant DB queries is a side effect of the
identity guarantee, not the primary design goal.

---

### 🔩 First Principles Explanation

**1LC DATA STRUCTURE:**

```
Persistence Context (1LC) =
  Map<EntityKey, EntityEntry>
    EntityKey = (entityClass, primaryKey)
    EntityEntry contains:
      - The entity object (the Java instance)
      - Status (MANAGED, REMOVED, etc.)
      - Snapshot (copy of field values at load time,
        used for dirty checking)

Example at runtime:
  {
    (Product.class, 1L) -> {entity: product1, snapshot:
      {...}},
    (Product.class, 2L) -> {entity: product2, snapshot:
      {...}},
    (Customer.class, 10L) -> {entity: customer10,
      snapshot: {...}}
  }
```

**WHAT THE 1LC DOES ON EACH OPERATION:**

```
em.find(Product.class, 1L):
  1. Compute key: (Product.class, 1L)
  2. Look up in 1LC map
  3. If found: return the cached entity object (NO DB
    query)
  4. If not found: SELECT FROM products WHERE id=1
     Store in 1LC map
     Return entity

em.persist(newProduct):
  1. Assign ID (via generator)
  2. Put entity in 1LC as MANAGED
  3. Queue INSERT for flush

em.remove(product):
  1. Mark entity as REMOVED in 1LC
  2. Queue DELETE for flush

flush():
  1. For each MANAGED entity in 1LC:
     Compare current state with snapshot (dirty checking)
     If different: generate UPDATE SQL
  2. Execute queued INSERT/DELETE/UPDATE SQLs
  3. Update snapshots to match current state
```

---

### 🧪 Thought Experiment

**THE IDENTITY GUARANTEE IN ACTION:**

```java
@Transactional
public void demonstrateIdentity(Long productId) {
    // First load: hits the database
    Product p1 = em.find(Product.class, productId);
    // 1LC: {(Product, productId) -> p1}

    // Second load: same transaction, same id
    Product p2 = em.find(Product.class, productId);
    // 1LC check: (Product, productId) found -> return p1
    // NO second SELECT to DB

    System.out.println(p1 == p2);  // TRUE (same object)
    System.out.println(p1.equals(p2)); // TRUE (same ref)

    // Modify via p1 reference:
    p1.setPrice(BigDecimal.valueOf(100));

    // Visible via p2 (same object!):
    System.out.println(p2.getPrice()); // 100.0
    // dirty check at flush: compares snapshot vs current
    // -> UPDATE products SET price=100 WHERE id=?
}
```

**THE QUERY BYPASS ISSUE:**

```java
@Transactional
public void queryDoesNotUseLc(Long id) {
    // Load into 1LC:
    Product p1 = em.find(Product.class, id);
    p1.setPrice(BigDecimal.TEN); // dirty, not flushed yet

    // JPQL query: bypasses 1LC identity map
    // BUT Hibernate auto-flushes before queries by default
    // So: flush() fires first -> UPDATE price=10 -> then SELECT
    List<Product> results = em.createQuery(
        "FROM Product p WHERE p.id = :id", Product.class)
        .setParameter("id", id)
        .getResultList();
    // Hibernate returns the 1LC entity (same p1 object)
    // NOT a new object (identity map merge)
    System.out.println(results.get(0) == p1); // TRUE
}
```

---

### 🧠 Mental Model / Analogy

> The first-level cache is like a pharmacist's short-term
> memory during a patient consultation. They pull the
> patient's record once (DB query). Every time they need
> to reference it during the same consultation (transaction),
> they remember it from memory (1LC) - no need to refetch.
> When the consultation ends (transaction closes), they
> put the record back and forget the session details.
> The NEXT consultation for the same patient starts with
> a fresh fetch - no cross-session contamination.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
During a transaction, Hibernate remembers every entity
it has loaded. If you ask for the same entity twice,
it returns the remembered copy - no second database
call. The memory is cleared at the end of the transaction.

**Level 2 - How to use it (junior developer):**
You do not need to manage the 1LC for normal use.
It is always active. Be aware: `em.find(Product.class, id)`
twice in the same transaction = 1 SQL query, not 2.
For batch processing, call `em.clear()` periodically
to prevent memory exhaustion.

**Level 3 - How it works (mid-level engineer):**
The persistence context is a `HashMap<EntityKey, EntityEntry>`.
Each entry holds the entity object plus a snapshot of
its field values at load time. On `find()`, Hibernate
checks the map before issuing SQL. At flush, Hibernate
compares current field values vs snapshot for dirty
checking. Clear/evict removes entries from the map.

**Level 4 - JPQL interaction (senior/staff):**
JPQL queries do NOT look up the 1LC before executing SQL
(they always hit the database). However, Hibernate
auto-flushes pending changes before executing a query
(FlushMode.AUTO) to ensure query results see uncommitted
changes. After the query, Hibernate merges results into
the 1LC: if a returned entity is already in the 1LC,
Hibernate returns the 1LC copy (not the DB result),
preserving identity.

**Level 5 - Architecture (distinguished engineer):**
The 1LC's snapshot mechanism is the foundation of dirty
checking. The snapshot doubles the memory used by managed
entities (entity data + snapshot copy). For `@Transactional(readOnly = true)`,
Hibernate 6+ skips snapshot creation for read-only
sessions, cutting memory usage by ~50% for reporting
queries. At scale, this matters: 10,000 entities loaded
in a read-only batch report use half the memory of the
same entities in a writable transaction. For batch jobs
processing millions of rows, explicit snapshot management
(`session.setReadOnly()` per entity + `session.evict()`)
is critical for memory stability.

---

### ⚙️ How It Works (Mechanism)

**DIRTY CHECKING MECHANISM (TIED TO 1LC):**

```java
// At em.find() time:
// entity: {id=1, name="Laptop", price=999}
// snapshot stored: {name="Laptop", price=999}

// Developer modifies:
product.setPrice(BigDecimal.valueOf(1099));
// entity: {id=1, name="Laptop", price=1099}
// snapshot: {name="Laptop", price=999} (unchanged)

// At flush():
// Hibernate compares entity vs snapshot:
//   name: "Laptop" == "Laptop" (no change)
//   price: 1099 != 999 (CHANGED!)
// Generates: UPDATE products SET price=1099 WHERE id=1
// Updates snapshot to {name="Laptop", price=1099}
```

**MEMORY IMPLICATION:**

```
Per managed entity:
  - Entity object: 1x field storage
  - Snapshot array: 1x field storage (for dirty check)
  - Map entry: EntityKey + EntityEntry overhead

100 entities with 20 fields each:
  - Entity data: ~100 * 20 = 2000 field values
  - Snapshots: ~2000 more field value copies
  - Total: ~4000 field values in heap

With readOnly=true (Hibernate 6+):
  - No snapshots allocated
  - Total: ~2000 field values (50% savings)
```

---

### 🔄 The Complete Picture - End-to-End Flow

**BATCH PROCESSING WITH 1LC MANAGEMENT:**

```java
@Service
@Transactional
public void processBatch(List<Long> productIds) {
    int batchSize = 50;

    for (int i = 0; i < productIds.size(); i++) {
        Long id = productIds.get(i);
        Product p = em.find(Product.class, id);

        // Process product...
        p.setStatus("PROCESSED");

        // Every 50 items: flush + clear
        if (i % batchSize == 0) {
            em.flush();  // Send pending SQL to DB
            em.clear();  // Evict ALL from 1LC
            // 1LC is now empty; next em.find() will
            // re-query DB (cannot use cache after clear)
        }
    }
    // Final flush for remaining items
    em.flush();
}
```

**WHY em.flush() BEFORE em.clear():**
If `em.clear()` is called without `em.flush()` first:
pending dirty changes in the 1LC are DISCARDED - the
SQLs were never sent to the database. Always flush
before clearing in batch jobs.

---

### 💻 Code Example

**Example 1 - Demonstrating cache hit:**

```java
@Transactional
public void cacheHitDemo(Long id) {
    // Query 1: cache miss -> SQL executed
    Product p1 = em.find(Product.class, id);
    // SELECT * FROM products WHERE id=?

    // Query 2: cache hit -> NO SQL
    Product p2 = em.find(Product.class, id);
    // NO SELECT: returned from 1LC

    // Reference equality: same Java object
    assert p1 == p2;

    // JPQL query: always issues SQL (bypasses 1LC map)
    // But returns the 1LC entity after merging:
    Product p3 = em.createQuery(
            "FROM Product p WHERE p.id = :id",
            Product.class)
        .setParameter("id", id)
        .getSingleResult();
    // SELECT * FROM products WHERE id=?  (SQL executed)
    // But: result merged into 1LC -> returns p1!
    assert p1 == p3;  // TRUE
}
```

**Example 2 - BAD: large batch without 1LC management:**

```java
// BAD: 1 million products loaded, all stay in 1LC
// -> heap exhaustion -> OutOfMemoryError
@Transactional
public void processMillion(List<Long> ids) {
    for (Long id : ids) {
        Product p = em.find(Product.class, id);
        p.setStatus("DONE");
        // 1 million entities in 1LC by end of loop
        // 2 million objects (entity + snapshot per entity)
    }
}

// GOOD: periodic flush + clear
@Transactional
public void processMillion(List<Long> ids) {
    for (int i = 0; i < ids.size(); i++) {
        Product p = em.find(Product.class, ids.get(i));
        p.setStatus("DONE");
        if (i % 100 == 0) {
            em.flush();  // commit pending changes to DB
            em.clear();  // evict all entities from 1LC
        }
    }
    em.flush();
}
```

---

### ⚖️ Comparison Table

| Cache                    | Scope               | Always on? | Shared?            | Controlled by                     |
| ------------------------ | ------------------- | ---------- | ------------------ | --------------------------------- |
| First Level Cache (1LC)  | Transaction/Session | Always on  | No (per session)   | Developer via `clear()`/`evict()` |
| Second Level Cache (2LC) | Application-wide    | Optional   | Yes (all sessions) | Config + `@Cache` on entity       |
| Query Cache              | Application-wide    | Optional   | Yes (all sessions) | Config + `@QueryHints`            |

---

### ⚠️ Common Misconceptions

| Misconception                                                            | Reality                                                                                                                                                                              |
| ------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| "The first-level cache can be disabled for performance-sensitive paths"  | The 1LC CANNOT be disabled. It is the persistence context itself. If you want non-cached behavior, use native JDBC queries or stateless sessions (`Session.openStatelessSession()`). |
| "JPQL queries use the first-level cache to avoid database hits"          | JPQL queries ALWAYS execute SQL. They do NOT check the 1LC before querying. However, Hibernate merges query results into the 1LC afterward, ensuring identity consistency.           |
| "em.clear() is safe to call at any time in a batch"                      | `em.clear()` DISCARDS all pending dirty changes without flushing them to the database. Always call `em.flush()` BEFORE `em.clear()` or dirty changes will be lost.                   |
| "Two EntityManagers in the same application share the first-level cache" | The 1LC is NEVER shared. Each EntityManager has its own 1LC. Changes in one EM are invisible to another EM until they are committed to the database.                                 |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Batch Job OutOfMemoryError**

**Symptom:** Batch job processes millions of records.
JVM heap grows steadily until `OutOfMemoryError`. Heap
dump shows millions of entity objects and their snapshot
arrays.

**Root Cause:** All loaded entities accumulate in the
1LC (persistence context) for the duration of the batch
transaction. With 1 million entities, 2 million objects
(entity + snapshot) fill the heap.

**Fix:**

```java
if (i % 100 == 0) {
    em.flush();
    em.clear();
}
```

Or use `StatelessSession` for read-heavy batch jobs
(no 1LC at all):

```java
StatelessSession ss = sessionFactory.openStatelessSession();
ScrollableResults results = ss.createQuery(
    "FROM Product", Product.class)
    .scroll(ScrollMode.FORWARD_ONLY);
while (results.next()) {
    Product p = (Product) results.get();
    // process; ss.update(p) if needed
}
```

---

**Failure Mode 2: Stale Entity After Bulk UPDATE**

**Symptom:** After running a bulk UPDATE (`@Modifying @Query`),
the entity loaded previously in the same transaction
still shows the old value. The 1LC returns the cached
(stale) entity rather than re-querying the database.

**Root Cause:** Bulk UPDATE bypasses the 1LC. The 1LC
entry for the updated entity is not invalidated.

**Fix:** Call `em.clear()` or `em.refresh(entity)` after
bulk DML to evict stale entities:

```java
repo.updatePrices(category, multiplier);
em.clear(); // evict all; force re-fetch from DB
// OR
em.refresh(specificEntity); // re-fetch single entity
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[JPH-011 - EntityManager]] - the 1LC is the persistence
  context managed by EntityManager
- [[JPH-012 - Persistence Context]] - 1LC IS the
  persistence context

**Builds On This (learn these next):**

- [[JPH-034 - Second Level Cache]] - shared, configurable
  cache complementing the transaction-scoped 1LC
- [[JPH-052 - Dirty Checking and Flush Mode]] - dirty
  checking compares entity state vs 1LC snapshot

**Related:**

- [[JPH-045 - Hibernate Batch Processing]] - periodic
  flush+clear pattern for 1LC memory management
- [[JPH-058 - Hibernate Internals]] - 1LC implementation
  details in Hibernate's `StatefulPersistenceContext`

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IS IT   │ Map<(EntityClass,id), EntityEntry>       │
│              │ Per-transaction; always enabled          │
├──────────────┼──────────────────────────────────────────┤
│ CACHE HIT    │ em.find() same id twice = 1 SQL          │
│              │ Second call hits 1LC (no DB query)       │
├──────────────┼──────────────────────────────────────────┤
│ IDENTITY     │ Same entity loaded twice = same Java obj │
│              │ p1 == p2: true                           │
├──────────────┼──────────────────────────────────────────┤
│ BATCH FIX    │ em.flush(); em.clear(); every N items    │
│              │ flush BEFORE clear (or lose dirty changes│
├──────────────┼──────────────────────────────────────────┤
│ STALE FIX    │ After bulk DML: em.clear() or            │
│              │ em.refresh(entity)                       │
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "1LC = transaction-scoped identity map.  │
│              │ Same entity same tx = 1 SQL, same object.│
│              │ Batch: flush+clear every N to free memory│
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. The 1LC guarantees entity identity within a transaction:
   same entity loaded twice returns the same Java object
   reference, with only one SQL query
2. The 1LC is the persistence context itself - it cannot
   be disabled; only cleared (`em.clear()`) or partially
   evicted (`session.evict(entity)`)
3. In batch processing: `em.flush()` then `em.clear()`
   every N items to prevent heap exhaustion

**Interview one-liner:** The first-level cache is the
persistence context itself - a per-transaction identity
map ensuring each entity (by type + ID) is loaded only
once per session and exists as one Java object reference.
Cannot be disabled. For batch jobs: flush + clear
periodically to prevent OutOfMemoryError. After bulk
UPDATE: clear or refresh to evict stale 1LC entries.

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** The Identity Map
pattern (Fowler, PEAA) is fundamental to ORM correctness.
Without it: two references to "the same row" could be
different Java objects; modifying one wouldn't affect the
other; dirty checking would need to track all copies.
The 1LC is what makes the ORM "feel like objects" rather
than "rows returned from queries." This pattern repeats:
Hibernate's 1LC, JPA's persistence context, ActiveRecord's
`identity_map` option, SQLAlchemy's Session identity map,
Core Data's managed object context - all implement the
same Identity Map pattern. The universal rule: within
one "unit of work" (transaction, session, context), each
entity has exactly one in-memory representation.

**Where else this pattern appears:**

- **SQLAlchemy (Python)**: `Session` maintains an identity
  map; `session.get(User, 1)` twice returns the same
  Python object
- **ActiveRecord (Rails)**: Identity map is optional
  (`ActiveRecord::IdentityMap`) but the ORM tracks loaded
  objects in associations
- **Core Data (iOS/macOS)**: `NSManagedObjectContext`
  is the identity map; same `NSManagedObjectID` = same
  `NSManagedObject` reference
- **Apollo Client (GraphQL)**: normalized cache = identity
  map keyed by type + ID for frontend entities

---

### 💡 The Surprising Truth

Hibernate's first-level cache has a subtle behavior with
`em.getReference()` (lazy proxy) vs `em.find()` (immediate
load). If you call `em.find(Product.class, 1L)` after
previously calling `em.getReference(Product.class, 1L)`,
Hibernate does NOT load the entity from the database -
it initializes the already-cached proxy. Conversely, if
you call `em.getReference(Product.class, 1L)` after
`em.find(Product.class, 1L)`, the reference returns the
ALREADY LOADED entity (not a proxy) - because the 1LC
already holds the real entity object. This identity
guarantee means the 1LC can "upgrade" a lazy proxy to
a real entity on subsequent find(), and can "downgrade"
a getReference() call to a cached real entity. All without
additional SQL queries.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **EXPLAIN** the data structure of the 1LC (Map of
   EntityKey to EntityEntry with snapshot)
2. **DEMONSTRATE** with code that two `em.find()` calls
   for the same entity in one transaction issue one SQL
   and return the same Java object
3. **EXPLAIN** why JPQL queries always issue SQL while
   `em.find()` can cache-hit, and how Hibernate merges
   both into the same identity map
4. **IMPLEMENT** the flush+clear batch pattern and explain
   why flush must precede clear
5. **DIAGNOSE** an OutOfMemoryError in batch processing
   caused by unbounded 1LC growth

---

### 🎯 Interview Deep-Dive

**Q1: What is the first-level cache in Hibernate, and
what problem does it solve?**
_Why they ask:_ Core Hibernate knowledge; tests understanding
of persistence context mechanics.
_Strong answer includes:_

- The 1LC is the persistence context: a Map keyed by
  entity type + primary key
- Solves the identity problem: within one transaction,
  the same entity (by id) is the same Java object reference
- Performance benefit: `em.find()` for an already-loaded
  entity returns from cache (no SQL)
- Always enabled; cannot be disabled; scoped to
  one Session/EntityManager (one transaction)
- Stores snapshot of each entity's state for dirty checking

**Q2: Why does a batch job cause OutOfMemoryError, and
how do you fix it?**
_Why they ask:_ Common production incident; tests practical
batch processing knowledge.
_Strong answer includes:_

- Root cause: every `em.find()` or query result adds an
  entity to the 1LC; in a long transaction, 1 million
  entities = 2 million objects (entity + snapshot)
- Fix: periodic `em.flush()` + `em.clear()`:
  flush sends pending SQL to DB; clear evicts all from 1LC
- Flush MUST come before clear (clear without flush
  discards un-flushed dirty changes)
- Alternative: `StatelessSession` for bulk reads (no 1LC)
- Batch size typically 50-500 entities between flushes

**Q3: What happens when you call JPQL query for an
entity that is already in the first-level cache?**
_Why they ask:_ Tests deep understanding of 1LC + query
interaction.
_Strong answer includes:_

- JPQL always issues SQL (does NOT check 1LC for cache hit)
- After the query, Hibernate merges results into 1LC:
  if an entity with that id is already in 1LC, Hibernate
  returns the 1LC copy (not the freshly-loaded DB copy)
- This preserves identity: `p1 == results.get(0)` is true
  if p1 was already loaded before the JPQL query
- However, if dirty entity in 1LC has unsaved changes,
  Hibernate flushes FIRST (FlushMode.AUTO) before the JPQL
  so the query sees the committed state
