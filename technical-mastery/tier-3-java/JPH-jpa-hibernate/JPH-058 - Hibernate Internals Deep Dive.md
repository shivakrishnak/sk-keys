---
id: JPH-058
title: Hibernate Internals Deep Dive
category: JPA & Hibernate
tier: tier-3-java
folder: JPH-jpa-hibernate
difficulty: ★★★
depends_on: JPH-001, JPH-006, JPH-011, JPH-012, JPH-013, JPH-026, JPH-031, JPH-033, JPH-057
used_by: []
related: JPH-057, JPH-052, JPH-046, JPH-034, JPH-035
tags:
  - java
  - jpa
  - hibernate
  - advanced
status: complete
version: 4
layout: default
parent: "JPA & Hibernate"
grand_parent: "Technical Mastery"
nav_order: 58
permalink: /technical-mastery/jpa-hibernate/hibernate-internals/
---

⚡ **TL;DR** - Inside Hibernate: `SessionFactory` is the
heavyweight singleton (one per app) that holds metadata, SQL
templates, 2LC. `Session` (wraps `EntityManager`) holds the
persistence context - a first-level identity map.
Dirty checking is snapshot-based: Hibernate takes a "snapshot"
of entity state at load time; at flush it compares current state
to snapshot to build UPDATE statements. The SQL generator
(`SqmTranslator` in H6) compiles HQL/JPQL AST -> SQL.
`ActionQueue` batches INSERT/UPDATE/DELETE in dependency order.
Understanding these internals explains 80% of Hibernate
performance issues and debugging challenges.

| #058            | Category: JPA & Hibernate                                                                                                    | Difficulty: ★★★ |
| :-------------- | :--------------------------------------------------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | JPA Overview, Entity Basics, EntityManager, Persistence Context, Caching, SQL Logging, N+1 Problem, Dirty Checking, JPA Spec |                 |
| **Used by:**    | -                                                                                                                            |                 |
| **Related:**    | JPA Spec, Dirty Checking/Flush, Statistics, Batch Processing, 2LC                                                            |                 |

---

### 🔥 The Problem This Solves

**WHY UNDERSTANDING INTERNALS MATTERS:**

```
Surface view (most developers):
  Call .save(), Hibernate inserts row. Magic.
  Call .find(), Hibernate returns entity. Magic.
  Performance is slow: add @BatchSize, add @Cache. Magic.
  Problem persists: "Hibernate is slow."

With internal understanding:
  "The flush took 2s because the persistence context
   has 10,000 managed entities and dirty checking
   is O(N) per entity snapshot comparison."
  Fix: call em.clear() every 500 entities in batch job

  "Why did my batch job run 1000 separate SELECTs
   after the first SELECT?"
  "Because the @OneToMany collection is LAZY and
   the proxy fires N separate SQL queries."
  Fix: JOIN FETCH or @BatchSize(size=50)

  "Why did my unit test pass but production failed
   with OptimisticLockException?"
  "Two requests fetched the same entity version=5,
   both modified and flushed; second flush saw version=5
   in DB but entity says version=5 -> conflict."
  Fix: retry logic, or PESSIMISTIC_WRITE for
    high-contention

Understanding Hibernate internals is the difference
between "Hibernate magic broke" and root cause analysis.
```

---

### 📘 Textbook Definition

**Hibernate** is an ORM (Object-Relational Mapping)
framework and the reference implementation of the
Jakarta Persistence specification. Internally composed of:

| Component               | Class                                                      | Role                                                                                                                   |
| ----------------------- | ---------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| `SessionFactory`        | `org.hibernate.internal.SessionFactoryImpl`                | Heavyweight singleton; bootstrapped at startup; holds: entity metadata, SQL plan cache, connection pool reference, 2LC |
| `Session`               | `org.hibernate.internal.SessionImpl`                       | Lightweight; one per request; holds persistence context (identity map); implements `EntityManager`                     |
| `StatisticsImpl`        | `org.hibernate.stat.internal.StatisticsImpl`               | Runtime counters: queries, hits, misses, load times                                                                    |
| `PersistenceContext`    | `org.hibernate.engine.internal.StatefulPersistenceContext` | Identity map: entity snapshots, entity entries, collection entries                                                     |
| `ActionQueue`           | `org.hibernate.engine.spi.ActionQueue`                     | Batches and orders INSERT/UPDATE/DELETE before flush                                                                   |
| `EventListenerRegistry` | `org.hibernate.event.service.spi.EventListenerRegistry`    | Lifecycle events: pre/post persist, pre/post update, etc.                                                              |
| `SqmTranslator`         | `org.hibernate.query.sqm.sql.SqmTranslator`                | Hibernate 6: compiles HQL/JPQL SQM tree -> SQL AST -> SQL string                                                       |
| `TypeSystem`            | `org.hibernate.type`                                       | Maps Java types -> JDBC types; handles custom converters                                                               |

---

### ⏱️ Understand It in 30 Seconds

**One line:** Hibernate's core loop: load entity -> take
state snapshot -> let app modify entity -> at flush, compare
current state to snapshot -> generate UPDATE only for changed columns.

**One analogy:**

> Hibernate's persistence context is like a spreadsheet with
> "Track Changes" enabled. When you open a row (load an entity),
> Hibernate records the original values. When you save the sheet
> (flush), it computes which cells changed and generates a minimal
> UPDATE SQL. If no cells changed: no UPDATE is sent - this is
> why `em.merge()` on an unchanged entity produces no SQL.
> The identity map (first-level cache) ensures that within
> one request, loading the same entity ID twice returns the
> exact same Java object - not a copy. This prevents
> inconsistent views within a transaction.

---

### 🔩 First Principles Explanation

**THE SESSION FACTORY BOOTSTRAP:**

```
Application Startup:
  1. HibernateJpaAutoConfiguration runs (Spring Boot)
  2. LocalContainerEntityManagerFactoryBean created
  3. Hibernate scans @Entity classes
     -> builds EntityMetamodel (ClassMetadata,
       EntityPersister)
     -> builds association graph
     -> validates against DB schema (if ddl-auto=validate)
  4. Generates SQL templates per entity:
     INSERT INTO product (id, name, price) VALUES (?, ?, ?)
     UPDATE product SET name=?, price=? WHERE id=? AND
       version=?
     SELECT p.* FROM product p WHERE p.id=?
     (cached as PreparedStatement templates in plan cache)
  5. Registers TypeDescriptors (Java type -> JDBC type
    mapping)
  6. Initializes 2LC regions if configured
  7. SessionFactory is ready: ~500ms-2s startup cost

Per-Request:
  Session.open() -> ~50 microseconds (HashMap allocation
    only)
  Transaction.begin() -> JDBC
    Connection.setAutoCommit(false)
  Entity operations -> tracked in
    StatefulPersistenceContext
  Flush -> ActionQueue executes SQL via JDBC
  Transaction.commit() -> JDBC Connection.commit()
  Session.close() -> detach all, return connection to pool
```

---

### 🧪 Thought Experiment

**PERSISTENCE CONTEXT IDENTITY MAP:**

```java
// Within one Session (one HTTP request):
Product p1 = em.find(Product.class, 1L);
// SQL: SELECT * FROM product WHERE id=1
// PersistenceContext.entityMap: {(Product,1L) -> p1}

Product p2 = em.find(Product.class, 1L);
// NO SQL! Returns p1 from identity map
// p1 == p2 (same Java object reference)

// This prevents:
p1.setPrice(BigDecimal.valueOf(99.0));
// If p2 were a different object, p2.price would still be 100.0
// With identity map: p1 == p2, so both see 99.0
// Consistent view within transaction

// Cross-session: NOT same object
Session s1 = sessionFactory.openSession();
Session s2 = sessionFactory.openSession();
Product a = s1.find(Product.class, 1L);
Product b = s2.find(Product.class, 1L);
// a != b (different sessions, different identity maps)
// a.price and b.price may differ if DB changed between loads
```

---

### 🧠 Mental Model / Analogy

> Think of Hibernate's session as a short-lived workspace:
> you pull documents off a shelf (DB), work on them
> locally, and file them back (flush). Hibernate keeps a
> "before" photo of each document when you pull it. When
> you file back, it compares current to "before" and only
> marks the changed pages. If you never changed a document,
> it's returned to the shelf without any update. The
> `SessionFactory` is the permanent filing room: its metadata,
> indexes, and structure persist for the application lifetime.
> Sessions are temporary desks: cheap to create, discarded
> after each task. Never keep a Session open longer than
> one request/transaction; and never share a Session
> between threads (it's not thread-safe).

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What SessionFactory is (junior):**
`SessionFactory` is the Hibernate singleton created at
startup. Expensive to create (~2s). Should be created once.
`Session` wraps it for each request. Cheap to create.

**Level 2 - Identity map and snapshot (junior-mid):**
Within one `Session`, loading the same entity ID twice
returns the same Java object (identity map / 1LC).
Hibernate saves a snapshot of loaded entity state.
At `flush()`, snapshot comparison generates UPDATE SQL.

**Level 3 - ActionQueue ordering (mid):**

```
Flush execution order (ActionQueue):
  1. OrphanRemoval actions
  2. INSERT actions (in entity dependency order)
     - Insert parent before child (FK constraint)
     - Hibernate topologically sorts inserts
  3. UPDATE actions (no specific order)
  4. DELETE actions (reverse dependency order)
     - Delete child before parent
  5. Collection operations (insert/delete)

This is why @OrderColumn or orphanRemoval=true
can affect flush performance: adds more actions.
ActionQueue.sort() may be called to reorder
to satisfy FK constraints.
```

**Level 4 - SQL plan cache and SQM (senior):**

```
Hibernate 6 query pipeline (per query):
  1. Parse HQL string -> SQM (Semantic Query Model) tree
     (internal AST: com.hibernate.query.sqm.tree.*)
  2. SQM -> SQL AST (com.hibernate.sql.ast.tree.*)
  3. SQL AST -> SQL string + JDBC parameters
  4. Plan cached in SessionFactory.queryPlanCache
     (LRU cache; default size: 2048 plans)
  5. On re-use: skip steps 1-3, use cached SQL template
     with new parameter bindings

Plan cache miss symptoms:
  - Too many distinct HQL string patterns (not
    parameterized)
  - org.hibernate.engine.query.spi.QueryPlanCache WARN
  - Increase cache:
    hibernate.query.plan_cache_max_size=4096
  - Fix: always use parameters, never string-concatenate
    values
    into HQL
```

**Level 5 - Event system and interceptors (staff):**

```
Hibernate event listener chain (for persist operation):
  Session.persist(entity) ->
  EventListenerRegistry.getEventListenerGroup(
      EventType.PERSIST) ->
  DefaultPersistEventListener.onPersist() ->
    1. Entity state check (TRANSIENT/MANAGED/DETACHED?)
    2. EntityEntry creation in PersistenceContext
    3. EntityPersister.getIdentifierGenerator().generate()
       (if @GeneratedValue)
    4. Insert action added to ActionQueue
    5. Cascade persist to PERSIST-cascaded associations
    6. @PrePersist callback fired on EntityListeners

Interception points:
  Custom: implement EventListener + override registration
  Envers: hooks into PostInsertEvent, PostUpdateEvent,
          PostDeleteEvent for audit trail
  Envers example:
    AuditProcess.doBeforeTransactionCompletion() builds
    revision entities and flushes them within same
      transaction
```

---

### ⚙️ How It Works (Mechanism)

**DIRTY CHECKING DEEP DIVE:**

```
On entity load (find / JPQL query result):
  EntityEntry created in StatefulPersistenceContext:
    entityEntry = {
      entity: <Java object reference>,
      status: MANAGED,
      loadedState: Object[] snapshot of column values,
        // loadedState[0] = "Laptop" (name)
        // loadedState[1] = BigDecimal("999.00") (price)
      entityPersister: ProductPersister
    }

On em.flush():
  for each EntityEntry in persistenceContext.entityEntries:
    currentState =
      entityPersister.getPropertyValues(entity)
    // currentState[0] = "Laptop Pro" (name changed!)
    // currentState[1] = BigDecimal("999.00") (price same)
    dirtyProperties = type.isDirty(loadedState,
      currentState)
    // -> dirtyProperties = [0] (name column dirty)
    if dirtyProperties.isEmpty: skip (no UPDATE needed)
    else: ActionQueue.addAction(new EntityUpdateAction(
              entity, dirtyProperties, ...))

EntityUpdateAction.execute():
  EntityPersister.update() ->
  preparedStatement = "UPDATE product SET name=? WHERE
    id=?"
  (NOT: "SET name=?, price=?" - only dirty columns!)
  Hibernate generates UPDATE for ONLY the changed columns
  (unless hibernate.entity.update.diff=false or
    @DynamicUpdate
   not present - by default Hibernate updates ALL columns)

@DynamicUpdate optimization:
  @Entity
  @DynamicUpdate  // generate UPDATE only for dirty columns
  public class Product { ... }
  Without @DynamicUpdate: UPDATE product SET name=?,
    price=? WHERE id=? (all columns, always)
  With @DynamicUpdate: UPDATE product SET name=?
    WHERE id=? (only changed)
  Trade-off: @DynamicUpdate requires dirty tracking per
    flush;
    small performance cost; only useful if entity has many
    columns and updates are partial
```

---

### 🔄 The Complete Picture - End-to-End Flow

**FULL REQUEST LIFECYCLE (WITH INTERNALS):**

```
HTTP Request:
  1. Spring: open Session (Transaction.begin())
             StatefulPersistenceContext: empty HashMap

  2. em.find(Product.class, 42L):
     - 1LC check: not in context -> DB hit
     - SQL: SELECT p.* FROM product p WHERE p.id=42
     - ResultSet -> hydrate Product entity
     - loadedState snapshot created in EntityEntry
     - Identity map: {(Product,42) -> product42}

  3. product42.setName("New Name"):
     - Just a POJO setter: Hibernate not notified yet
     - (unless @DynamicUpdate with bytecode enhancement:
       dirty tracking tracks field writes immediately)

  4. em.find(Product.class, 42L):
     - 1LC hit! Returns same product42 object. No SQL.

  5. em.flush() (at end of @Transactional method):
     - Dirty check: product42.name changed
     - ActionQueue: EntityUpdateAction for product42
     - SQL: UPDATE product SET name=?, ... WHERE id=42
     - ActionQueue cleared

  6. Transaction.commit():
     - JDBC commit
     - 2LC update (if @Cacheable configured)
     - Session close: all EntityEntries cleared
     - Connection returned to HikariCP pool

  7. @Transactional proxy returns to Spring
```

---

### 💻 Code Example

**Enabling and reading Hibernate internal statistics:**

```java
// application.properties
spring.jpa.properties.hibernate.generate_statistics=true
// logs stats per session to DEBUG level

// Programmatic access:
@Autowired
private EntityManagerFactory emf;

public void diagnoseSession() {
    SessionFactory sf =
        emf.unwrap(SessionFactory.class);
    Statistics stats = sf.getStatistics();

    // Key metrics:
    stats.getQueryExecutionCount()    // total JPQL executed
    stats.getEntityLoadCount()        // entities loaded from DB
    stats.getEntityInsertCount()      // INSERT count
    stats.getEntityUpdateCount()      // UPDATE count
    stats.getSecondLevelCacheHitCount()  // 2LC hits
    stats.getSecondLevelCacheMissCount() // 2LC misses
    stats.getSessionOpenCount()       // sessions opened
    stats.getFlushCount()             // flush calls
    stats.getPrepareStatementCount()  // JDBC prepared stmts

    // Useful for: detecting N+1 (entityLoadCount >> 1
    //   when you expect 1 query to load all),
    //   detecting missing 2LC (hit count stays 0)

    // Reset between tests:
    stats.clear();
}
```

**Inspecting persistence context state:**

```java
// Unwrap Hibernate Session from EntityManager:
Session session = em.unwrap(Session.class);

// Check managed entity count (session memory pressure):
SessionImplementor impl =
    (SessionImplementor) session;
int managedCount = impl.getPersistenceContext()
    .getNumberOfManagedEntities();
// If this is > 1000 in a batch job: call em.clear()!
// High count = slow dirty checking at flush

// Force flush then clear (batch processing pattern):
if (count % 500 == 0) {
    em.flush();   // write pending changes to DB
    em.clear();   // detach all: zero the identity map
    // Now managedCount = 0; dirty check is fast again
}
```

---

### ⚖️ Comparison Table

| Component            | Hibernate 5.x         | Hibernate 6.x                | Notes                                        |
| -------------------- | --------------------- | ---------------------------- | -------------------------------------------- |
| Query AST            | HQL: Antlr2-based AST | HQL: SQM (new AST model)     | H6 rewrote query engine                      |
| Type system          | `@Type(type="...")`   | `@JavaType`, `@JdbcType`     | More type-safe in H6                         |
| Bytecode enhancement | Optional              | Optional (recommended in H6) | Lazy loading proxy                           |
| Package              | `org.hibernate`       | `org.hibernate` (unchanged)  | `javax` -> `jakarta` in provider integration |
| JPQL compliance      | JPA 2.2               | Jakarta Persistence 3.1      | H6 adds new JPQL functions                   |

---

### ⚠️ Common Misconceptions

| Misconception                                       | Reality                                                                                                                                                                                                                                                                                                                                                                    |
| --------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Hibernate generates UPDATE for ALL columns always" | By default YES - unless `@DynamicUpdate` is applied. Without `@DynamicUpdate`, Hibernate generates UPDATE with all mapped columns, even unchanged ones. This is a deliberate trade-off: one SQL template per entity (cached) vs N templates per dirty pattern. `@DynamicUpdate` generates SQL at runtime for only dirty columns; more I/O efficient but requires more CPU. |
| "Session and EntityManager are different classes"   | In Hibernate, `Session` EXTENDS `EntityManager`. `SessionImpl` implements both. `em.unwrap(Session.class)` returns the same underlying object. Use `EntityManager` API for JPA-portable code; unwrap to `Session` only for Hibernate-specific features.                                                                                                                    |
| "em.clear() is dangerous and should be avoided"     | `em.clear()` is ESSENTIAL in batch processing. It detaches all managed entities, resetting the identity map. Without it, batch jobs accumulate thousands of managed entities; dirty checking becomes O(N) at each flush, eventually causing OutOfMemoryError or severe slowdown. Pattern: flush every N entities, then clear.                                              |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode: OutOfMemoryError in Batch Job**

**Symptom:** Batch import of 100,000 rows starts fast,
progressively slows, eventually crashes with
`java.lang.OutOfMemoryError: Java heap space`.
GC log shows increasing old gen usage.

**Root Cause:** Each entity loaded or persisted is added to
the `StatefulPersistenceContext` identity map. After processing
50,000 entities, the persistence context holds 50,000 `EntityEntry`
objects with their snapshots. Dirty checking at flush is
O(50,000) comparisons. GC cannot collect these because the
`Session` holds strong references.

**Diagnosis:**

```java
// Check managed entity count:
int count = ((SessionImplementor) em.unwrap(Session.class))
    .getPersistenceContext()
    .getNumberOfManagedEntities();
// If this grows without bound: missing flush/clear loop
```

**Fix:**

```java
// Batch processing with flush/clear:
int batchSize = 500;
for (int i = 0; i < entities.size(); i++) {
    em.persist(entities.get(i));
    if (i % batchSize == 0) {
        em.flush();   // write to DB
        em.clear();   // release all entity references
    }
}
em.flush();  // final flush for remainder
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[JPH-011 - EntityManager and Persistence Context]] - the
  core API that Hibernate implements
- [[JPH-031 - N+1 Select Problem]] - most common symptom
  of not understanding lazy loading internals

**Builds On This (learn these next):**

- [[JPH-046 - Hibernate Statistics and Monitoring]] - using
  the statistics API described in this entry

**Related:**

- [[JPH-052 - Dirty Checking and Flush Mode]] - deep dive on
  the dirty checking mechanism described here
- [[JPH-057 - JPA Specification]] - the spec that Hibernate implements

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ SESSION FACTORY │ Singleton; holds metadata, plan cache │
│                 │ 2LC. Expensive to create. One per app.│
├─────────────────┼───────────────────────────────────────┤
│ SESSION         │ Per-request. Identity map + snapshots.│
│                 │ Cheap to create. NOT thread-safe.     │
├─────────────────┼───────────────────────────────────────┤
│ DIRTY CHECKING  │ Snapshot at load, compare at flush.   │
│                 │ O(N*cols). Add @DynamicUpdate for     │
│                 │ partial UPDATE column generation.     │
├─────────────────┼───────────────────────────────────────┤
│ ACTION QUEUE    │ Batches ops; topological sort for FK. │
│                 │ INSERT parent before child.           │
├─────────────────┼───────────────────────────────────────┤
│ BATCH JOB FIX   │ flush+clear every 500 entities.       │
│                 │ Prevents OOM and O(N) dirty checking. │
├─────────────────┼───────────────────────────────────────┤
│ ONE-LINER       │ "Hibernate: snapshot identity map.    │
│                 │ Flush = compare snapshots -> SQL.     │
│                 │ SessionFactory = singleton.           │
│                 │ Session = per request, not thread-safe│
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. `SessionFactory` is heavyweight singleton; `Session` is lightweight per-request
2. Dirty checking = snapshot comparison at flush; grows O(N) with persistence context size
3. Batch jobs MUST call `em.flush(); em.clear()` every N entities to prevent OOM

**Interview one-liner:** Hibernate's `Session` (wraps `EntityManager`) holds a
persistence context - an identity map of managed entities plus their loaded-state
snapshots. At `flush()`, Hibernate compares current entity state to snapshots and
generates UPDATE SQL only for changed entities. `SessionFactory` is the heavyweight
singleton holding entity metadata, SQL plan cache, and connection pool reference;
`Session` is per-request and not thread-safe. Batch processing must call
`em.flush() + em.clear()` every ~500 entities to prevent the persistence context
growing to tens of thousands of entries (causing O(N) dirty checking and OOM).

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Understanding the
"change detection" mechanism of any stateful framework
is key to predicting its performance characteristics.
Rails ActiveRecord, Django ORM, and Hibernate all track
"what changed" via different mechanisms (Hibernate: snapshot;
ActiveRecord: `changed?` tracking; Django: original values
on model instance). The pattern is universal: (1) record
initial state, (2) allow application modification, (3) at
"save time" compute diff and generate minimal write operation.
When the tracked collection grows unbounded (Hibernate
persistence context, Redux store, Observable subscriptions),
performance degrades O(N). The fix is always the same:
periodically flush + clear the tracked collection. Know
your framework's "change detector" and its cost model.

---

### 💡 The Surprising Truth

Hibernate's default dirty checking is UNCONDITIONAL at
flush - it checks EVERY managed entity in the persistence
context, not just entities your code modified. This means:
a persistence context with 10,000 managed entities will run
10,000 snapshot comparisons at every flush, even if only
1 entity was modified. The comparison is per-column, so a
wide entity (50 columns) in a 10,000-entity context runs
500,000 comparisons at flush. This is the root cause of
the "Hibernate is slow" perception in batch use cases.
The fix is either: (a) bytecode enhancement (tracks dirty
fields at write time, skips unchanged entities in dirty check),
or (b) flush + clear loop. Bytecode enhancement is off by
default because it requires compile-time instrumentation and
can interfere with proxying. Hibernate 6 recommends
bytecode enhancement for entities with many fields in
high-throughput scenarios.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **DRAW** the lifecycle of a Hibernate entity through
   persist, load, dirty check, flush, and session close
2. **EXPLAIN** why loading the same entity ID twice in one
   session returns the same Java object reference
3. **DIAGNOSE** OutOfMemoryError in a batch Hibernate job
   and implement the flush/clear fix
4. **EXPLAIN** why `em.flush()` may generate UPDATE SQL
   even if you didn't explicitly call any setter since load
5. **DESCRIBE** what `SessionFactory` holds and why
   it must not be recreated per-request

---

### 🎯 Interview Deep-Dive

**Q1: How does Hibernate detect which entities to UPDATE
on flush? Walk through the mechanism.**
_Why they ask:_ Separates candidates who "know Hibernate is dirty-checking"
from those who understand how it works.
_Strong answer includes:_

- When entity is loaded (`find`, JPQL result, `merge`), Hibernate creates an
  `EntityEntry` in the `StatefulPersistenceContext`
- `EntityEntry.loadedState`: an `Object[]` snapshot of all mapped column values
  at load time
- At `flush()`, Hibernate iterates all managed `EntityEntry` objects
- For each: calls `entityPersister.getPropertyValues(entity)` to get current state
- Compares property-by-property using `Type.isDirty(current, loaded)` per column
- If any column is dirty: adds `EntityUpdateAction` to `ActionQueue`
- `ActionQueue.execute()`: generates and runs UPDATE SQL via JDBC
- Without `@DynamicUpdate`: UPDATE includes all mapped columns (one SQL template)
- With `@DynamicUpdate`: UPDATE includes only dirty columns (generated per flush)

**Q2: A batch job that imports 200,000 records runs fine for
the first 50,000 rows, then gets progressively slower and
eventually crashes. What do you suspect and how do you fix it?**
_Why they ask:_ Tests batch processing knowledge and persistence context behavior.
_Strong answer includes:_

- Diagnosis: persistence context accumulates managed entities; dirty check
  is O(entities \* columns) at each flush
- After 50,000 entities: 50,000 EntityEntry snapshots held in memory
- Each flush compares all 50,000 snapshots (most unchanged)
- Memory: heap fills with snapshot arrays; GC pressure increases
- Eventually: OOM, GC thrashing, or severe slowdown
- Fix:
  ```java
  for (int i = 0; i < records.size(); i++) {
      em.persist(entities.get(i));
      if (i % 500 == 0) {
          em.flush(); // write batch to DB
          em.clear(); // detach all; reset identity map to empty
      }
  }
  em.flush();
  ```
- Additional: enable JDBC batching (`hibernate.jdbc.batch_size=50`)
  for INSERT batching; use `StatelessSession` for pure write-only batch
  (no dirty checking at all, no 1LC, no cascade)
