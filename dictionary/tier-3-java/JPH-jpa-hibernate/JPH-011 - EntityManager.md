---
id: JPH-011
title: EntityManager
category: JPA & Hibernate
tier: tier-3-java
folder: JPH-jpa-hibernate
difficulty: ★★☆
depends_on: JPH-006, JPH-007, JPH-009
used_by: JPH-012, JPH-013, JPH-014, JPH-016
related: JPH-029, JPH-033
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
nav_order: 11
permalink: /jpa-hibernate/entity-manager/
---

# JPH-011 - EntityManager

⚡ **TL;DR** - `EntityManager` is the primary JPA API for
managing entities: it persists, finds, merges, removes, and
queries, while owning the persistence context (first-level
cache and dirty-checking state) for its session lifetime.

| #011 | Category: JPA & Hibernate | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | @Entity, @Id and @GeneratedValue, JPA Configuration | |
| **Used by:** | Persistence Context, Entity Lifecycle, JPQL, CrudRepository and JpaRepository | |
| **Related:** | @Transactional, Native SQL Queries | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Without a standardised session/unit-of-work API, every
database interaction requires opening a JDBC connection,
manually writing SQL, mapping ResultSet columns to Java
fields, tracking what changed, and issuing UPDATE statements
for every modified field. Developer time is consumed by
bookkeeping (which objects changed, in which order to insert
foreign keys, how to handle rollbacks) rather than business
logic.

**THE BREAKING POINT:**
In a transaction that touches 15 entities - creating some,
updating others, and deleting a few - hand-coded JDBC
requires precise ordering to avoid FK violations, manual
tracking of which records need INSERT vs UPDATE, and
explicit handling of cascades. A single missed UPDATE
produces silent data corruption. The cognitive load is
high and the code is untestable without a database.

**THE INVENTION MOMENT:**
JPA's `EntityManager` encapsulates all of this into a
unit-of-work pattern: call `persist()`, `merge()`, or
`remove()` on entities, and at flush time the
`EntityManager` determines the correct SQL to issue,
in the correct order, for all changes tracked in the
session. The developer interacts with Java objects;
the `EntityManager` translates to SQL automatically.

---

### 📘 Textbook Definition

**`EntityManager`** is the Jakarta Persistence API interface
that serves as the primary interface between Java application
code and the JPA persistence layer. It manages the lifecycle
of entity instances within a **persistence context** -
a set of managed entity instances representing a unit of work.

The `EntityManager` API provides:
- **CRUD operations**: `persist()`, `find()`, `merge()`,
  `remove()`, `refresh()`
- **Query creation**: `createQuery()` (JPQL), `createNativeQuery()`,
  `createNamedQuery()`, `getCriteriaBuilder()`
- **Context management**: `flush()`, `clear()`, `detach()`,
  `contains()`, `isOpen()`
- **Transaction access**: `getTransaction()` (resource-local)

An `EntityManager` instance is NOT thread-safe and must not
be shared between threads. In Spring, `@PersistenceContext`
injects a thread-safe proxy that delegates to the correct
per-transaction `EntityManager` instance.

---

### ⏱️ Understand It in 30 Seconds

**One line:** `EntityManager` is the session object that
tracks entities, translates Java operations to SQL, and
maintains the first-level cache within a unit of work.

**One analogy:**
> `EntityManager` is a shopping cart at a supermarket.
> You add items (persist), modify them (merge), remove them
> (remove), and look them up by barcode (find). At checkout
> (flush/commit), all the items are processed as a single
> transaction. The cart tracks what you added, changed, or
> removed - you don't scan each item twice.

- "Shopping cart" - the EntityManager session
- "Adding items" - `em.persist(entity)`
- "Looking up by barcode" - `em.find(Product.class, id)`
- "Checkout" - `em.flush()` / `tx.commit()`
- "Scanning twice" - without first-level cache, the same
  entity would be re-fetched from DB on each access

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. One `EntityManager` = one persistence context = one unit of work
2. `EntityManager` is NOT thread-safe; never share an
   instance across threads
3. In Spring, `@PersistenceContext` injects a transaction-scoped
   proxy; a new `EntityManager` is created per `@Transactional`
   method and closed at transaction end
4. `flush()` writes pending changes to the DB in the current
   transaction; `commit()` makes them permanent
5. The identity map: within one `EntityManager` session,
   `em.find(Product.class, 1L)` always returns the same Java
   object instance

**SIX CORE OPERATIONS:**

| Operation | SQL Generated | Entity State After |
|---|---|---|
| `persist(entity)` | `INSERT` (at flush) | MANAGED |
| `find(Class, id)` | `SELECT` (or cache hit) | MANAGED |
| `merge(detached)` | `SELECT` + `UPDATE` (if changed) | Returns new MANAGED copy |
| `remove(entity)` | `DELETE` (at flush) | REMOVED |
| `refresh(entity)` | `SELECT` (forced reload) | MANAGED (overwritten) |
| `detach(entity)` | None | DETACHED |

**THE CRITICAL DISTINCTION - persist vs merge:**
- `persist()`: transitions a NEW entity to MANAGED; entity
  becomes tracked; cannot be called on a detached entity
- `merge()`: copies state from a detached entity into a
  new MANAGED copy; returns the MANAGED copy (caller must
  use the return value); triggers SELECT to check if the
  entity exists

---

### 🧪 Thought Experiment

**SETUP:**
You load a `Product` entity, modify it, then accidentally
call `em.detach(product)` before the transaction commits.

```java
@Transactional
public void updatePrice(Long id, BigDecimal newPrice) {
    Product p = em.find(Product.class, id); // MANAGED
    p.setPrice(newPrice);   // dirty - tracked
    em.detach(p);           // NOW: DETACHED
    // Transaction commits - NO UPDATE issued
    // p's price change is silently lost
}
```

**THE INSIGHT:**
`em.detach()` removes the entity from the persistence
context's tracking. The price change is never flushed.
No error is thrown. This is silent data loss - the kind
that causes "I changed it but the database didn't update"
bugs that take hours to diagnose.

**THE FIX:**
Never call `detach()` on a modified entity within the same
transaction unless you deliberately want to discard changes.
If you want to discard changes, call `refresh()` instead
(reloads from DB, discarding modifications).

---

### 🧠 Mental Model / Analogy

> The `EntityManager` is an office manager for a unit of
> work. Every entity that enters the office becomes a
> "managed employee" (tracked). The manager keeps notes
> on everything they do (dirty checking). At end of day
> (flush), the manager processes all the changes in the
> correct order. Employees who quit (detach) are no longer
> tracked; whatever they did after leaving is not recorded.

- "Office manager" - EntityManager
- "Managed employees" - entities in MANAGED state
- "Manager's notes" - dirty checking snapshots
- "End of day processing" - flush to database
- "Employees who quit" - DETACHED entities (changes not tracked)

Where this analogy breaks down: an office manager does
not "merge" a former employee back in. `EntityManager.merge()`
copies the detached entity's state into a new managed copy,
whereas a returned employee in the office would just
resume their old role.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
`EntityManager` is the Java object you use to talk to
the database: `em.find()` to read, `em.persist()` to
insert, `em.merge()` to update a detached object,
`em.remove()` to delete.

**Level 2 - How to use it (junior developer):**
In Spring, inject it with `@PersistenceContext`:

```java
@Repository
public class ProductDao {
    @PersistenceContext
    private EntityManager em;

    public Product findById(Long id) {
        return em.find(Product.class, id);
    }
    // persist, merge, remove work same way
}
```

The injected `em` is a thread-safe proxy; Spring creates
a real `EntityManager` per transaction.

**Level 3 - How it works (mid-level engineer):**
At the start of a `@Transactional` method, Spring opens
a new `EntityManager` session and binds it to the current
thread. Every call to `em.find()`, `em.persist()`, etc.,
operates within this session. Entities loaded are
registered in the identity map. At transaction commit,
Spring calls `em.flush()` (writes pending SQL) then
commits the JDBC connection. The session is then closed.

**Level 4 - Why it was designed this way (senior/staff):**
The `EntityManager` implements the Unit of Work pattern
(Fowler). It batches all entity changes across a business
transaction and writes them in the correct order at flush
time, respecting FK constraints automatically (parents before
children for INSERT, children before parents for DELETE).
This eliminates a class of JDBC ordering bugs entirely.
The identity map (first-level cache) ensures consistency:
if two parts of the same transaction load the same entity,
they get the same Java object, so modifications from one
part are visible to the other without a DB round trip.

**Level 5 - Mastery (distinguished engineer):**
`FlushModeType` controls when the `EntityManager` writes
pending changes: `AUTO` (before query execution, to ensure
queries see the latest data) vs `COMMIT` (only at transaction
commit). `AUTO` is safer but adds implicit flushes before
every JPQL query. In batch processing scenarios, setting
`em.setFlushMode(FlushModeType.COMMIT)` and manually calling
`em.flush()` and `em.clear()` every N entities prevents
memory exhaustion from snapshot accumulation. The `em.clear()`
call detaches all entities, releasing their snapshots from
memory - essential when processing 100,000+ rows.

**Expert Thinking Cues:**
- Ask: "Is `em.merge()` being called when `em.persist()`
  is expected?" - `merge()` on a new entity (null ID) still
  works but triggers an unnecessary SELECT first
- Watch: `em.clear()` in a loop that processes large
  datasets - without it, the persistence context accumulates
  one snapshot per loaded entity, causing GC pressure
- Know: Spring Data's `repository.save()` calls either
  `persist()` or `merge()` based on `isNew()` - but the
  entity returned by `merge()` is the managed copy, not
  the input entity

---

### ⚙️ How It Works (Mechanism)

**EntityManager Lifecycle in a Spring Transaction:**

```
@Transactional method called
    |
    v
[ Spring AOP proxy intercepts ]
    |  checks: is there an active tx?
    v
[ DataSourceTransactionManager or JpaTransactionManager ]
    |  opens new EntityManager
    |  begins JDBC transaction
    v
[ EntityManager bound to current thread ]
    |
    v
[ Business logic runs ]
    |  em.find() -> identity map lookup, then SELECT
    |  entity.setField() -> tracked, snapshot taken
    |  em.persist(newEntity) -> buffered for INSERT
    v
[ Transaction ready to commit ]
    |
    v
[ em.flush() called automatically ]
    |  dirty check: compare entities to snapshots
    |  INSERT for new entities (in FK order)
    |  UPDATE for modified entities (changed fields only)
    |  DELETE for removed entities
    v
[ JDBC commit ]
    |  changes become permanent
    v
[ EntityManager closed ]
    |  all entities become DETACHED
    v
[ @Transactional method returns ]
```

**Flush Modes:**

```
FlushModeType.AUTO (default)
  - Flush before any JPQL/Criteria query
  - Ensures queries see pending changes
  - Can cause unexpected SELECTs before queries

FlushModeType.COMMIT
  - Flush only at transaction commit
  - Faster for write-heavy transactions
  - JPQL queries may not see uncommitted changes
```

**CONCURRENCY / THREAD-SAFETY BEHAVIOR:**
The `EntityManager` instance itself is NOT thread-safe.
Spring's `@PersistenceContext` injection provides a
transaction-scoped proxy. The proxy dispatches each call
to the real `EntityManager` bound to the current thread's
transaction. Two threads in concurrent transactions each
have their own real `EntityManager` and isolated
persistence context.

---

### 🔄 The Complete Picture - End-to-End Flow

**EXAMPLE: Update a product price:**

```
HTTP PATCH /products/42
    |
    v
[ @PatchMapping -> ProductController.updatePrice() ]
    |  calls productService.updatePrice(42, 29.99)
    v
[ @Transactional -> Spring opens EntityManager ]
    |
    v
[ em.find(Product.class, 42L) ]
    |  identity map: miss
    |  SELECT * FROM products WHERE id=42
    |  Product loaded, snapshot stored
    v
[ product.setPrice(29.99) ]
    |  Java object modified, NOT DB
    v
[ @Transactional method returns ]
    |
    v
[ Spring calls em.flush() ]
    |  dirty check: price changed from 19.99 to 29.99
    |  UPDATE products SET price=29.99 WHERE id=42
    v
[ JDBC commit ]
    |
    v
[ EntityManager closed, product becomes DETACHED ]
```

**FAILURE PATH:**
If `flush()` generates a constraint violation (FK violation,
unique key violation), `PersistenceException` is thrown,
the transaction is rolled back, and no changes are applied.
Entities in the session revert to their pre-transaction state.

**WHAT CHANGES AT SCALE:**
At 100,000 entity operations per transaction (batch jobs),
the persistence context accumulates 100,000 snapshots in
memory. Use `em.clear()` every 1000 entities to release
snapshots, and `em.flush()` before clearing to write pending
changes. This reduces memory from GB to MB.

---

### 💻 Code Example

**Example 1 - BAD: sharing EntityManager across threads:**

```java
// BAD: EntityManager as instance variable
// Shared between threads -> corrupt state
@Repository
public class BadOrderRepo {
    @PersistenceContext
    private EntityManager em; // PROXY - this is ok

    // BAD: extracting the real EM from the proxy
    // and sharing it
    private EntityManager realEm;

    @PostConstruct
    public void init() {
        // realEm is NOT thread-safe
        this.realEm = em.getEntityManagerFactory()
            .createEntityManager();
        // This single instance shared across threads
        // -> race condition on identity map
    }
}
```

**Example 2 - GOOD: standard Spring usage:**

```java
// GOOD: @PersistenceContext provides thread-safe proxy
@Repository
public class ProductRepository {

    @PersistenceContext
    private EntityManager em;

    public Optional<Product> findById(Long id) {
        return Optional.ofNullable(
            em.find(Product.class, id));
    }

    @Transactional
    public Product save(Product p) {
        if (p.getId() == null) {
            em.persist(p);
            return p;
        }
        return em.merge(p); // returns managed copy
    }
}
```

**Example 3 - persist() vs merge() distinction:**

```java
// NEW entity: use persist()
@Transactional
public void createProduct(Product p) {
    // p.getId() is null
    em.persist(p);
    // p IS the managed entity; id is set after flush
    System.out.println(p.getId()); // non-null after flush
}

// DETACHED entity: use merge()
@Transactional
public Product updateDetachedProduct(Product detached) {
    // detached came from outside the transaction
    Product managed = em.merge(detached);
    // detached is STILL detached; managed is the new copy
    // ALWAYS use the returned value - not the input
    return managed;
}
```

**Example 4 - Batch processing with flush/clear:**

```java
// Processing 500,000 records efficiently
@Transactional
public void processAllOrders(
        List<Long> orderIds) {
    int batchSize = 1000;

    for (int i = 0; i < orderIds.size(); i++) {
        Order o = em.find(Order.class,
                          orderIds.get(i));
        processOrder(o);

        if (i % batchSize == 0) {
            em.flush();  // write pending changes
            em.clear();  // release snapshots
            // Without this: OutOfMemoryError at ~50k
        }
    }
}
```

---

### ⚖️ Comparison Table

| Operation | When to use | State before | State after | SQL |
|---|---|---|---|---|
| `persist(e)` | NEW entity, first save | NEW (null id) | MANAGED | INSERT at flush |
| `find(C, id)` | Load by primary key | Any | MANAGED | SELECT (or cache hit) |
| `merge(e)` | Detached entity, update | DETACHED | Returned MANAGED copy | SELECT + UPDATE |
| `remove(e)` | Delete entity | MANAGED | REMOVED | DELETE at flush |
| `refresh(e)` | Reload from DB, discard changes | MANAGED | MANAGED (fresh) | SELECT |
| `detach(e)` | Stop tracking | MANAGED | DETACHED | None |
| `flush()` | Force write to DB | - | - | Pending SQL executed |
| `clear()` | Release all from context | - | All DETACHED | None |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "`em.persist()` immediately INSERTs to DB" | `persist()` only changes entity state to MANAGED and buffers the INSERT. The SQL is sent at `flush()` time (either automatic before a query, or at transaction commit). |
| "`em.merge()` updates the entity I passed in" | `merge()` returns a NEW managed copy. The entity you passed to `merge()` remains DETACHED. If you continue using the input object, changes are not tracked. Always use the return value. |
| "I can call `em.persist()` on a detached entity to re-attach it" | `persist()` on a detached entity throws `EntityExistsException`. Use `merge()` to re-attach a detached entity. |
| "`em.find()` always hits the database" | `find()` checks the first-level cache (identity map) first. If the entity was loaded earlier in the same session, it returns the cached instance without a DB query. |
| "Spring Data's `repository.save()` always calls `persist()`" | `save()` calls `isNew()` - if the `@Id` is null/0 it calls `persist()`; if non-null it calls `merge()`. For entities with pre-assigned UUID IDs, `save()` always calls `merge()`, triggering a SELECT before every INSERT. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: TransactionRequiredException**

**Symptom:**
```
javax.persistence.TransactionRequiredException:
No transactional EntityManager available
```
**Root Cause:** `em.persist()`, `em.merge()`, or `em.remove()`
called outside a `@Transactional` context. Write operations
require an active transaction.
**Diagnostic:**

```bash
# Verify @Transactional is on the correct layer
# (service, not just controller)
logging.level.org.springframework.transaction=DEBUG
# Logs: "Creating new transaction" vs "No active transaction"
```

**Fix:** Ensure the calling method is annotated with
`@Transactional` or called from within a transactional
context. Check for the self-invocation trap (calling
a `@Transactional` method within the same bean).
**Prevention:** Use Spring Data repositories which manage
their own transactions, or apply `@Transactional` at
the service layer.

---

**Failure Mode 2: merge() Return Value Ignored**

**Symptom:** Entity changes made after `merge()` are not
persisted; queries return old data even after apparent updates.
**Root Cause:** Developer called `em.merge(detached)` but
continued modifying the input `detached` object instead of
the returned managed copy.

```java
// BAD: continuing to use detached after merge()
Product detached = getDetachedProduct();
em.merge(detached);           // returned value ignored!
detached.setPrice(newPrice);  // modifying DETACHED object
// flush() does NOT send UPDATE - detached is not tracked
```

**Diagnostic:**

```bash
spring.jpa.show-sql=true
# No UPDATE statement generated - confirms changes not tracked
```

**Fix:**

```java
// GOOD: use the returned managed copy
Product managed = em.merge(detached);
managed.setPrice(newPrice);  // modifying MANAGED object
// flush() generates UPDATE correctly
```

**Prevention:** Code review rule: `em.merge()` return value
must always be assigned and used. Discard the input
reference after merge.

---

**Failure Mode 3: OutOfMemoryError in Batch Jobs**

**Symptom:** Batch job processing 100,000 records fails with
`OutOfMemoryError: Java heap space` after processing ~20,000
records. Heap dump shows millions of Hibernate entity snapshots.
**Root Cause:** Each entity loaded via `em.find()` adds its
snapshot to the persistence context. Without `em.clear()`,
the context grows unbounded.
**Diagnostic:**

```bash
# Enable Hibernate statistics:
spring.jpa.properties.hibernate.generate_statistics=true
# Look for: "session open count", "entity load count"
# If entity load count >> manual batch size, context is accumulating
jvisualvm # Heap analysis: org.hibernate.engine.spi.EntityEntry
```

**Fix:**

```java
for (int i = 0; i < ids.size(); i++) {
    processEntity(em.find(Entity.class, ids.get(i)));
    if (i % 1000 == 0) {
        em.flush();  // commit pending writes
        em.clear();  // release snapshots from memory
    }
}
```

**Prevention:** Any batch job touching more than 10,000
entities must use `flush()/clear()` pattern or use
`StatelessSession` (Hibernate-specific, no dirty checking).

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[JPH-006 - @Entity]] - entities are what the
  EntityManager manages; @Entity is the prerequisite
- [[JPH-007 - @Id and @GeneratedValue]] - the identity
  that `em.find()` uses for lookup and the identity
  map key
- [[JPH-009 - JPA Configuration (persistence.xml, application.properties)]] -
  configuration that creates the `EntityManagerFactory`
  from which `EntityManager` instances are created

**Builds On This (learn these next):**
- [[JPH-012 - Persistence Context]] - deep dive into the
  identity map and dirty checking that the EntityManager
  maintains
- [[JPH-013 - Entity Lifecycle (NEW, MANAGED, DETACHED, REMOVED)]] -
  the state machine that EntityManager operations transition
- [[JPH-014 - JPQL (Java Persistence Query Language)]] -
  queries executed through the EntityManager
- [[JPH-016 - CrudRepository and JpaRepository]] - Spring
  Data abstracts EntityManager behind repositories

**Alternatives / Comparisons:**
- [[JPH-029 - @Transactional]] - transactions that scope
  the EntityManager's lifetime
- [[JPH-033 - Native SQL Queries]] - `em.createNativeQuery()`
  bypasses JPA and executes SQL directly

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ The JPA session API that manages entity   │
│              │ lifecycle and translates operations to SQL │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Eliminates manual JDBC bookkeeping:       │
│ SOLVES       │ change tracking, FK ordering, SQL gen     │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ NOT thread-safe. Spring injects a proxy   │
│              │ that routes to per-transaction instance   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Custom queries beyond Spring Data; batch  │
│              │ processing with flush/clear; direct JPA   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Don't share EntityManager across threads; │
│              │ don't use outside a transaction for writes│
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ Ignoring merge() return value; not        │
│              │ calling flush/clear in large batch loops  │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Automatic change tracking convenience vs  │
│              │ memory overhead of snapshots at scale     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "EntityManager is the shopping cart:      │
│              │ you add/modify/remove; flush = checkout"  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Persistence Context -> Entity Lifecycle   │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. `persist()` for NEW entities; `merge()` for DETACHED -
   and always use `merge()`'s return value, not the input
2. `EntityManager` is NOT thread-safe; `@PersistenceContext`
   injects a proxy that routes per-transaction
3. Batch jobs: call `em.flush(); em.clear()` every 1000
   entities to prevent `OutOfMemoryError` from snapshot growth

**Interview one-liner:** `EntityManager` is the JPA session
API that manages entity lifecycle and owns the persistence
context. It is NOT thread-safe; Spring's `@PersistenceContext`
injects a thread-safe proxy. Key operation distinction:
`persist()` is for NEW entities (null ID); `merge()` is for
DETACHED entities and returns a NEW managed copy - the input
object remains detached.

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** The Unit of Work pattern
(EntityManager) and Identity Map pattern (first-level cache)
are complementary. The Unit of Work batches all changes for
a business transaction; the Identity Map ensures consistency
within the session by preventing duplicate object instances
for the same entity identity. These two patterns together
solve the fundamental impedance mismatch between object
graphs (which can have multiple references to the same
conceptual object) and database rows (which are identified
by a single primary key).

**Where else this pattern appears:**
- **Active Record (Ruby on Rails)** - `record.save()` is
  Unit of Work applied to a single record; the session
  is the HTTP request
- **Mongoose (Node.js ODM)** - `document.save()` follows
  the same Unit of Work pattern for MongoDB documents
- **SQLAlchemy Session (Python)** - `session.add()`,
  `session.commit()` is structurally identical to JPA's
  `em.persist()`, `tx.commit()`

**Industry applications:**
- Microservices with shared databases: each service has its
  own `EntityManagerFactory` with separate entity scan scope;
  `EntityManager` sessions are strictly scoped to service
  boundaries to prevent cross-service entity contamination
- Event sourcing systems: `EntityManager` writes event
  records in a single transaction per command, maintaining
  causality consistency for the same aggregate entity

---

### 💡 The Surprising Truth

`em.persist()` does not immediately execute an INSERT
statement. It transitions the entity to MANAGED state and
buffers the INSERT. If you call `em.persist(product)` and
then immediately call `System.out.println(product.getId())`,
you may see a non-null ID (from `GenerationType.SEQUENCE`)
or null (from `GenerationType.IDENTITY`, which needs the
INSERT to happen before the DB assigns the ID). The behaviour
depends entirely on the ID generation strategy. This is why
`SEQUENCE` enables batching (IDs are pre-assigned before
INSERT) while `IDENTITY` does not (the INSERT must execute
immediately to get the ID). Many developers assume `persist()`
is synchronous and are surprised to find that `getId()` is
null until `flush()` with `IDENTITY` strategy.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN** the difference between `persist()` and
   `merge()` including which entity state transitions each
   triggers, and why you must use the return value of `merge()`
2. **TRACE** the full lifecycle of an entity from `em.persist()`
   through `em.flush()` to `tx.commit()`, including what
   SQL is generated and when
3. **DEBUG** a scenario where entity changes are silently
   lost, identifying whether the cause is `detach()` before
   flush, `merge()` return value ignored, or `@Transactional`
   missing on the calling method
4. **BUILD** a batch processing loop that handles 1,000,000
   rows efficiently using `flush()/clear()` to prevent
   `OutOfMemoryError`, with correct handling of the
   `allocationSize` interaction with SEQUENCE strategy
5. **EXPLAIN** why `EntityManager` is not thread-safe and
   how Spring's `@PersistenceContext` injection provides
   thread safety via a transaction-scoped proxy

---

### 🧠 Think About This Before We Continue

**Q1 (TYPE D - Root Cause Trace):** A developer updates a
`Customer` entity: loads it with `em.find()`, modifies a
field, and calls `em.merge(customer)`. The update is not
persisted to the database. Trace three possible root causes
and the diagnostic steps to identify each.
*Hint: (1) merge() return value ignored - changes made on
detached input; (2) @Transactional missing - flush never
called; (3) FlushMode.COMMIT with no transaction commit.*

**Q2 (TYPE B - Scale):** You are writing a batch job that
processes 1,000,000 `Order` entities, calculating a summary
field for each. After processing 100,000 entities, the JVM
OOM-crashes. What is the root cause, and what is the correct
fix? Explain why `em.clear()` alone (without `em.flush()`
before it) could cause data loss.
*Hint: clear() detaches entities and releases snapshots,
but if there are pending INSERT/UPDATE operations, they are
also discarded. flush() must come before clear() to write
pending changes.*

**Q3 (TYPE G - Hands-On):** Write a test that demonstrates
the identity map behaviour: load the same entity twice in
the same transaction, modify it via the first reference,
and assert that the second reference sees the change.
Then write a second test that loads the entity in two
separate transactions and demonstrates that changes in
one transaction are not visible to the other until committed.
*Hint: Use @Transactional with REQUIRES_NEW for the
second transaction; or two separate EntityManager instances.*

---

### 🎯 Interview Deep-Dive

**Q1: What is the difference between `em.persist()` and
`em.merge()`? When would you use each?**
*Why they ask:* Tests daily-use JPA understanding; a very
common source of bugs in production code.
*Strong answer includes:*
- `persist()`: for NEW entities (null ID); transitions
  to MANAGED; entity IS the managed object; throws
  `EntityExistsException` if called on a detached entity
- `merge()`: for DETACHED entities; copies state into a
  new managed copy; RETURNS the managed copy; input
  remains detached; triggers SELECT to check existence
- Use `persist()` for first-time inserts;
  use `merge()` when re-attaching objects from outside
  the current transaction (e.g. from a REST request)
- Spring Data's `save()` chooses automatically based on `isNew()`

**Q2: Why is `EntityManager` not thread-safe, and how does
Spring make it safe to use in a multi-threaded web application?**
*Why they ask:* Tests understanding of Spring internals
and concurrency model.
*Strong answer includes:*
- Not thread-safe because it holds a mutable identity map;
  concurrent access from two threads corrupts the snapshot
  state
- Spring's `@PersistenceContext` injects a proxy
  (`SharedEntityManagerCreator`) that delegates each call
  to the real `EntityManager` bound to the current thread's
  transaction (stored in `TransactionSynchronizationManager`)
- Each `@Transactional` method gets its own real
  `EntityManager`; the proxy routes to the correct one
  per thread

**Q3: Explain the consequences of NOT calling `em.clear()`
in a batch job that processes 100,000 entities.**
*Why they ask:* Tests production operational knowledge -
batch processing is a common JPA use case with specific
pitfalls.
*Strong answer includes:*
- Each `em.find()` adds the entity and its snapshot to the
  persistence context; 100,000 entities = 100,000 snapshots
- At flush time, Hibernate must dirty-check all 100,000
  entities against their snapshots - O(N) CPU and memory
- Result: OutOfMemoryError, GC pressure, or extreme
  flush latency
- Fix: `em.flush(); em.clear()` every 1000 entities;
  flush first to write pending changes, then clear to
  release snapshots