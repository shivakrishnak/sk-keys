---
id: JPH-052
title: Dirty Checking and Flush Mode
category: JPA & Hibernate
tier: tier-3-java
folder: JPH-jpa-hibernate
difficulty: ★★★
depends_on: JPH-006, JPH-011, JPH-012, JPH-013, JPH-026, JPH-033
used_by: JPH-045, JPH-054, JPH-058
related: JPH-031, JPH-033, JPH-038, JPH-046
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
nav_order: 52
permalink: /jpa-hibernate/dirty-checking-flush/
---

# JPH-052 - Dirty Checking and Flush Mode

⚡ **TL;DR** - Hibernate's **dirty checking** compares
each managed entity's current state to its "snapshot"
(taken at load time). Changed fields -> automatic UPDATE
at flush. No `save()` call needed for updates. **Flush**
is the point where in-memory changes are written to the
database (within the transaction). `FlushModeType.AUTO`
(default): Hibernate flushes before JPQL queries that
might be affected, and before transaction commit. Performance
cost: dirty checking scans ALL managed entities. Fix for
large sessions: use `@Transactional(readOnly=true)` for
reads (disables dirty checking), or call `em.clear()` in
batch processing to drop managed entities from session.

| #052 | Category: JPA & Hibernate | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Entity Basics, EntityManager, JPA Lifecycle, @Transactional, First Level Cache | |
| **Used by:** | Batch Processing, JPA at Scale, Hibernate Internals | |
| **Related:** | Session and Persistence Context, First Level Cache, Optimistic Locking, Hibernate Statistics | |

---

### 🔥 The Problem This Solves

**WHY UPDATE WITHOUT save():**

```java
@Transactional
public void giveDiscount(Long productId) {
    Product p = repo.findById(productId).orElseThrow();
    // snapshot taken: price=100.00

    p.setPrice(p.getPrice().multiply(
        new BigDecimal("0.90")));
    // price now 90.00 in memory
    // NO repo.save(p) called here!

    // At transaction commit:
    // Hibernate compares price=90.00 vs snapshot price=100.00
    // -> DIRTY: generates UPDATE products SET price=90.00
    // WHERE id=? AND version=?
    // -> Committed to DB
}
// The UPDATE happened without calling save()
// This is automatic dirty checking.
```

**THE PERFORMANCE COST:**
```java
@Transactional
public void processReport() {
    // Load 1,000 products for a report
    List<Product> products = repo.findAll();
    // Hibernate takes snapshot of ALL 1,000 entities

    // Read-only report computation:
    double total = products.stream()
        .mapToDouble(p -> p.getPrice().doubleValue())
        .sum();

    // At transaction commit:
    // Hibernate compares 1,000 snapshots to 1,000 current states
    // -> 1,000 comparison cycles (even though nothing changed)
    // -> Wasted CPU, memory for snapshots
}
// FIX: use readOnly=true to disable dirty checking:
@Transactional(readOnly = true)
```

---

### 📘 Textbook Definition

**Dirty checking** is Hibernate's mechanism for detecting
entity field changes between load time and flush time.
At load, Hibernate creates a "hydrated state" (snapshot)
of each managed entity. At flush, it compares current state
to snapshot. Changed fields generate UPDATE SQL.

**Flush** is the process of writing the in-memory persistence
context changes to the database (still within transaction).

**FlushModeType options:**

| Mode | When auto-flush triggers |
|---|---|
| `AUTO` (default) | Before JPQL/HQL queries that might be affected by pending changes; before transaction commit |
| `COMMIT` | Only before transaction commit |
| `ALWAYS` | Before every query execution |
| `MANUAL` | Never automatic; only when `em.flush()` explicitly called |

**Key distinction:**
- **Flush** = write to DB (within transaction, still reversible)
- **Commit** = make DB changes permanent (ends transaction)

---

### ⏱️ Understand It in 30 Seconds

**One line:** Dirty checking compares entity state at
flush to the snapshot taken at load; changed entities
generate UPDATE SQL automatically without calling `save()`.

**One analogy:**
> Dirty checking is like a hotel room inspection system.
> When you check in (load entity), the hotel takes a
> photo of the room (snapshot). When you check out (flush),
> they compare the room now vs the photo. Any differences
> (moved furniture = changed fields) generate a
> "room-change fee" (UPDATE SQL). You don't report changes
> yourself (no `save()` needed) - the inspection catches
> everything. The downside: inspecting 500 rooms (500 loaded
> entities) takes time even if all rooms are unchanged.

**One insight:** `@Transactional(readOnly=true)` is
primarily a dirty-checking optimization, not just a hint.
Hibernate uses it to skip snapshot creation entirely
(no hydrated state copied), which saves memory and
eliminates flush comparison. For read-heavy operations
loading many entities, `readOnly=true` is one of the
cheapest performance wins available.

---

### 🔩 First Principles Explanation

**DIRTY CHECKING INTERNALS:**

```
At em.find(Product.class, 42):
  1. Load from DB: {id=42, name="Widget", price=100.00}
  2. Create entity object: Product{...}
  3. Store hydrated state (snapshot) in SessionImpl:
     entityEntries map: {id=42} -> Object[]{42, "Widget", 100.00}

At product.setPrice(90.00):
  1. Entity object updated in memory
  2. Snapshot unchanged: still {42, "Widget", 100.00}

At em.flush() (or before JPQL query in AUTO mode):
  1. For each managed entity in session:
     a. Get current state: [42, "Widget", 90.00]
     b. Get snapshot:      [42, "Widget", 100.00]
     c. Compare field by field:
        - id: 42 vs 42 -> SAME
        - name: "Widget" vs "Widget" -> SAME
        - price: 90.00 vs 100.00 -> DIFFERENT (dirty!)
     d. Generate: UPDATE products SET price=90.00 WHERE id=42
  2. Execute all dirty entity UPDATEs
  3. Update snapshots to reflect new "clean" state
```

**FLUSH BEFORE QUERY (AUTO mode):**

```java
@Transactional
public void updateAndQuery() {
    Product p = repo.findById(1L).orElseThrow();
    p.setPrice(new BigDecimal("99.00")); // dirty

    // JPQL query on the SAME entity type:
    List<Product> allProducts = em.createQuery(
        "SELECT p FROM Product p WHERE p.price > 50",
        Product.class).getResultList();
    // AUTO mode: Hibernate detects "pending UPDATE on Product"
    // -> Flushes FIRST: UPDATE products SET price=99.00...
    // -> Then: SELECT FROM products WHERE price > 50
    // This ensures the query sees the updated price (99.00)
    // vs the DB state (100.00) - prevents stale reads.
    // Consequence: unexpected flush = unexpected UPDATE SQL
}
```

---

### 🧪 Thought Experiment

**THE FLUSH MODE PERFORMANCE MATRIX:**

```
Scenario: 50 JPQL queries in one transaction, 100 managed entities

FlushModeType.AUTO:
  - Each JPQL query checks: "do pending changes affect this query?"
  - If any dirty entities match the query's entity type: FLUSH FIRST
  - Potential: up to 50 flush cycles (worst case: every query triggers flush)
  - Dirty check: 100 entities * 50 flush opportunities = 5,000 comparisons

FlushModeType.COMMIT:
  - No automatic flush before queries
  - One dirty check at commit time: 100 entities * 1 flush = 100 comparisons
  - Risk: JPQL queries may not see pending in-memory changes
  - Use only when you know queries don't depend on pending changes

FlushModeType.MANUAL:
  - Zero automatic flushes
  - Must call em.flush() exactly when you need it
  - Zero overhead from unexpected flushes
  - Requires careful manual flush management
```

---

### 🧠 Mental Model / Analogy

> Flush mode is the garbage collection strategy for
> the persistence context. `AUTO`: collect garbage before
> each room you enter (before each query) - always clean
> but overhead on every entry. `COMMIT`: collect all garbage
> at the end of the day (before commit) - minimal overhead
> but accumulated garbage during the day. `MANUAL`: you decide
> exactly when to collect - maximum control, requires discipline.
>
> The default (`AUTO`) is correct for most cases because
> query consistency matters. Switch to `COMMIT` only
> when you know queries don't need to see pending changes,
> or use `MANUAL` in batch processing where you control
> the flush cycle explicitly.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What dirty checking is (anyone can understand):**
Hibernate watches for changes to loaded entities and
automatically writes those changes to the DB at flush time.
No `save()` call needed to update an entity.

**Level 2 - How flush works (junior developer):**
```java
// Three ways to trigger a flush:
// 1. Transaction commit (always)
@Transactional
public void update(Long id) {
    Entity e = repo.findById(id).orElseThrow();
    e.setName("New");
    // Automatic flush at method return (commit)
}

// 2. Before JPQL query (AUTO mode, default)
// 3. Explicit:
em.flush();
```

**Level 3 - Flush mode trade-offs (mid-level engineer):**
```java
// For read-only operations: disable dirty checking
@Transactional(readOnly = true)
public List<Product> getActiveProducts() {
    return repo.findByActiveTrue();
    // Hibernate: no snapshot taken, no flush comparison
    // ~30% faster for queries loading many entities
}

// For batch processing: flush + clear cycle
@Transactional
public void processLargeDataset(List<Record> records) {
    int i = 0;
    for (Record r : records) {
        em.persist(buildEntity(r));
        if (++i % 50 == 0) {
            em.flush();  // write to DB
            em.clear();  // drop all managed entities from session
            // Session now has 0 managed entities
            // Next dirty check: 0 entities (not 50,000)
        }
    }
}
```

**Level 4 - Bytecode enhancement (senior engineer):**
Hibernate's default dirty checking is "property-level":
compare all fields of all managed entities. Hibernate
also supports "bytecode enhancement" (enable in build):
instead of comparing snapshots, Hibernate instruments
entity setters to mark the entity as dirty on ANY setter
call (set a `isDirty` flag). Benefit: O(1) dirty detection
(no field comparison); only dirty entities are checked at flush.
Trade-off: build complexity; setter instrumentation can
interfere with some frameworks (Lombok `@Builder`, etc.).
For most apps: default property-level dirty checking is sufficient.

**Level 5 - The partial flush problem (staff engineer):**
In `AUTO` mode, Hibernate performs "partial flush": before
a JPQL query, it only flushes entities whose types appear
in the query's FROM clause. If a query is `SELECT p FROM Product p`
and you have dirty `Order` entities: `Order` entities are
NOT flushed before that query. This is the "partial flush"
optimization. Edge case: in a complex inheritance hierarchy,
Hibernate may flush more than expected (the entire
hierarchy). The safest diagnostic: enable `hibernate.generate_statistics`
and check `flushCount` per transaction.

---

### ⚙️ How It Works (Mechanism)

**DISABLING DIRTY CHECKING - SPRING DATA WAY:**

```java
// Option 1: readOnly transaction (preferred)
@Transactional(readOnly = true)
public Page<Product> findPagedProducts(Pageable p) {
    return repo.findAll(p);
}

// Option 2: detach entities after reading (selective)
@Transactional
public List<ProductDto> getProductDtos() {
    List<Product> products = repo.findAll();
    List<ProductDto> dtos = products.stream()
        .map(ProductDto::from)
        .collect(Collectors.toList());
    // Detach after mapping to DTOs:
    products.forEach(em::detach);
    // Now: products not tracked; dirty checking skipped
    return dtos;
}

// Option 3: MANUAL flush mode for a specific query
em.setFlushMode(FlushModeType.COMMIT); // entire session
// Or per query:
em.createQuery("SELECT p FROM Product p")
    .setFlushMode(FlushModeType.COMMIT)
    .getResultList();
```

---

### 🔄 The Complete Picture - End-to-End Flow

**FULL TRANSACTION DIRTY CHECK LIFECYCLE:**

```
@Transactional method starts:
  -> EntityManager session opens
  -> FlushMode = AUTO

em.find(Product.class, 1):
  -> SQL: SELECT ... FROM products WHERE id=1
  -> Entity Product{1, "Widget", 100.00} loaded
  -> Snapshot {1, "Widget", 100.00} stored in session

product.setPrice(90.00):
  -> Entity state changed; snapshot unchanged

em.createQuery("SELECT p FROM Product p WHERE p.active=true"):
  -> AUTO: check pending changes for Product type
  -> Product #1 is dirty (price changed)
  -> Flush: UPDATE products SET price=90.00 WHERE id=1
  -> Snapshot updated: {1, "Widget", 90.00}
  -> THEN execute SELECT query

em.persist(new Product("New", 50.00)):
  -> New entity added to session
  -> No snapshot yet (not yet inserted)

@Transactional method returns:
  -> Commit begins
  -> Flush (final):
     - New Product: INSERT INTO products(name, price)
     - No other dirty entities (all cleaned after earlier flush)
  -> Transaction commits
  -> Session closed; all entities detached
```

---

### 💻 Code Example

**Example 1 - BAD: unnecessary dirty checking in reporting:**

```java
// BAD: loading entities for read-only aggregation
// -> snapshot taken, dirty checked at commit
@Transactional
public ReportDto generateReport() {
    List<Order> orders = orderRepo.findAll();
    // 50,000 Order snapshots in memory
    BigDecimal total = orders.stream()
        .map(Order::getTotal)
        .reduce(BigDecimal.ZERO, BigDecimal::add);
    // Commit: compare 50,000 entities to 50,000 snapshots
    // -> 50,000 comparisons; none are dirty; wasted CPU
    return new ReportDto(total);
}

// GOOD: readOnly transaction + JPQL aggregate
@Transactional(readOnly = true)
public ReportDto generateReport() {
    BigDecimal total = em.createQuery(
        "SELECT SUM(o.total) FROM Order o",
        BigDecimal.class).getSingleResult();
    // 0 entity snapshots; 0 dirty checks
    return new ReportDto(total);
}
```

**Example 2 - Unexpected flush due to AUTO mode:**

```java
@Transactional
public void updateAndSearch(Long id, String keyword) {
    Product p = repo.findById(id).orElseThrow();
    p.setName("Updated");  // product is dirty now

    // This JPQL triggers a flush (AUTO mode):
    List<Product> results = em.createQuery(
        "SELECT p FROM Product p WHERE p.name LIKE :kw",
        Product.class)
        .setParameter("kw", "%" + keyword + "%")
        .getResultList();
    // Before the SELECT runs:
    // Hibernate sees: Product entity dirty, query on Product type
    // -> Flushes: UPDATE products SET name='Updated'...
    // -> THEN SELECT
    // This is correct behavior but may surprise developers
    // who expected the UPDATE to happen only at commit.
}
```

---

### ⚖️ Comparison Table

| FlushMode | Auto-flush when? | Risk | Use case |
|---|---|---|---|
| `AUTO` | Before JPQL query on dirty type; before commit | Unexpected flush mid-transaction | Default; most cases |
| `COMMIT` | Only before commit | Queries may not see pending changes | Batch reads; data import |
| `ALWAYS` | Before every query | Too many flushes; performance risk | Legacy/test scenarios |
| `MANUAL` | Never | Changes lost if `em.flush()` forgotten | Expert batch processing |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "You must call save() to update an entity" | NO - for MANAGED (loaded via EntityManager) entities, dirty checking generates the UPDATE automatically at flush. `save()` in Spring Data is for NEW entities (triggers INSERT) or for DETACHED entities (triggers merge + UPDATE). Calling `save()` on an already-managed entity is a no-op that returns the same entity. |
| "`@Transactional(readOnly=true)` prevents writes" | readOnly=true is a HINT to Hibernate to skip snapshot/dirty-check overhead. It does NOT prevent you from calling `save()` or `persist()`. Hibernate may still emit writes in readOnly mode (it's a hint, not an enforcement). For strict read-only: use JDBC directly or detach entities. |
| "FlushModeType.COMMIT is always faster than AUTO" | Not necessarily. With `COMMIT` mode, all dirty entities accumulate in the session and are flushed at commit. For long transactions with many entity changes: one large flush at commit vs many small flushes during execution. Large batch flush may cause: large INSERT/UPDATE batches, longer lock hold time, more undo log space. AUTO spreads the load. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode: Unintended Entity Update**

**Symptom:** A REPORT method (not intended to modify data)
is causing UPDATE statements in the transaction log.
**Root Cause:** An entity was loaded in a `@Transactional`
(without `readOnly=true`) method, a field was modified
(perhaps by a downstream service or mapper that called
a setter), and dirty checking detected the change.
**Diagnosis:**
```java
// Enable SQL log to catch unexpected UPDATEs:
logging.level.org.hibernate.SQL=DEBUG

// Or use Hibernate statistics:
long updates = sf.getStatistics()
    .getEntityUpdateCount();
// Unexpected updates > 0 in a "read" method = problem

// Stack trace approach: add a PostUpdateEventListener:
@Component
public class UpdateTracer
    implements PostUpdateEventListener {
    @Override
    public void onPostUpdate(PostUpdateEvent event) {
        if (inReadOnlyContext()) {
            log.warn("Unexpected update: {} #{}",
                event.getEntity().getClass(),
                event.getId());
        }
    }
}
```
**Fix:** Add `@Transactional(readOnly=true)` to read
methods; audit mappers/utilities that may call setters
on loaded entities.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[JPH-033 - First Level Cache]] - dirty checking works
  on entities in the first-level cache (persistence context)
- [[JPH-011 - Entity Lifecycle]] - managed state is
  required for dirty checking; detached entities are not checked

**Builds On This (learn these next):**
- [[JPH-045 - Batch Processing]] - flush+clear pattern
  for batch: flush every N entities, then clear() to prevent
  accumulated dirty check overhead
- [[JPH-058 - Hibernate Internals]] - hydrated state storage
  mechanism; dirty detection implementation details

**Related:**
- [[JPH-038 - Optimistic Locking]] - `@Version` check is
  part of the flush UPDATE: `WHERE version = ?`
- [[JPH-046 - Hibernate Statistics]] - `flushCount` and
  `entityUpdateCount` for measuring dirty check impact

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ DIRTY CHECK  │ entity state != snapshot -> UPDATE at flush│
│ NO save()    │ Required for managed entity updates       │
├──────────────┼───────────────────────────────────────────┤
│ FLUSH        │ Write session changes to DB (pre-commit)  │
│ MODES        │ AUTO(default), COMMIT, ALWAYS, MANUAL     │
├──────────────┼───────────────────────────────────────────┤
│ READ-ONLY    │ @Transactional(readOnly=true)             │
│ WIN          │ Skips snapshot; skips dirty check; faster │
├──────────────┼───────────────────────────────────────────┤
│ BATCH FIX    │ em.flush(); em.clear(); every N entities  │
│              │ Prevents 100K entity dirty check at end   │
├──────────────┼───────────────────────────────────────────┤
│ AUTO FLUSH   │ Before JPQL query touching dirty entities │
│ TRIGGER      │ Unexpected UPDATE mid-transaction?        │
│              │ This is why. Check pending dirty entities │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Dirty checking = auto UPDATE on field    │
│              │ change; flush writes to DB pre-commit.    │
│              │ readOnly=true disables snapshots."        │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Dirty checking compares entity snapshot (taken at load)
   to current state at flush; changed fields -> auto UPDATE (no `save()`)
2. `@Transactional(readOnly=true)` disables dirty checking -
   most important performance optimization for read-heavy code
3. `em.flush(); em.clear();` every N entities in batch processing
   to prevent session growing to 100K managed entities

**Interview one-liner:** Hibernate dirty checking compares
entity state to its hydrated snapshot at flush; changed fields
generate UPDATE SQL automatically without calling `save()`.
`FlushModeType.AUTO` flushes before JPQL queries that could
be affected by pending changes and before commit.
`@Transactional(readOnly=true)` disables snapshot creation
for reads; `em.flush()+clear()` controls batch processing memory.

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Change tracking via
snapshots (Hibernate dirty checking) vs change tracking
via mutation interception (Observer/Proxy pattern) is a
fundamental trade-off. Snapshots: simple implementation,
works with any Java objects (plain setters), but O(n*m)
comparison overhead (n entities * m fields). Mutation
interception (bytecode enhancement, Proxy, Java 21's
Valhalla): O(1) dirty detection per mutation, but requires
instrumentation of entity classes. This same trade-off
appears in: React's reconciler (virtual DOM diff = snapshot
comparison vs Svelte's compile-time change tracking =
mutation interception), Redux vs MobX (snapshot immutable
diff vs proxy mutation), database WAL (redo log = capture
mutations) vs DB snapshots (MVCC copy-on-write). Understanding
which model your system uses determines its performance
characteristics under load.

---

### 💡 The Surprising Truth

Hibernate's dirty checking scans ALL managed entities,
not just the ones you changed. In a long `@Transactional`
method that loads 5,000 entities for a batch report and
then updates 3 of them, ALL 5,000 entities are compared
to their snapshots at flush - even the 4,997 unchanged ones.
The total cost: 5,000 field comparisons, not 3. With entities
having 20+ fields each: 100,000+ field comparisons per flush
for one "batch update 3 entities" operation. This is why
`em.clear()` in batch processing is critical: it drops
all managed entities from the session (freeing both the
entity objects and their snapshots from memory), so the
next dirty check starts with only the newly loaded/modified
entities. Without `clear()`, the session grows without bound
and dirty checking becomes quadratic as batch size increases.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN** why entity updates work without `save()` for
   managed entities (dirty checking snapshots)
2. **DESCRIBE** when `FlushModeType.AUTO` triggers an early
   flush (before JPQL queries on dirty entity types)
3. **USE** `@Transactional(readOnly=true)` for read-heavy
   operations and explain the performance benefit
4. **IMPLEMENT** the `flush()+clear()` pattern for batch
   processing and explain why `clear()` is necessary
5. **DIAGNOSE** unexpected UPDATE statements in "read-only"
   transaction methods

---

### 🎯 Interview Deep-Dive

**Q1: Explain how Hibernate's dirty checking works. When
does an entity get an automatic UPDATE in the database?**
*Why they ask:* Tests deep understanding of JPA lifecycle.
*Strong answer includes:*
- At `em.find()` / `repo.findById()`: entity loaded + snapshot (hydrated state) stored
- Mutations via setters: entity state changes; snapshot unchanged -> "dirty"
- At flush (pre-commit or pre-JPQL query in AUTO mode):
  compare current state to snapshot field by field
- Dirty fields: generate UPDATE SQL for those fields
- No `save()` needed for managed entities - this is automatic
- Detail: snapshot is deep-copied at load; modification of nested
  fields in embedded objects is also tracked

**Q2: A batch processing job loads 100,000 entities,
updates each, and commits. It runs out of memory at 50,000.
What is wrong and how do you fix it?**
*Why they ask:* Tests production batch processing knowledge.
*Strong answer includes:*
- Root cause: all 100,000 entities accumulate in first-level
  cache (session) with their snapshots. Each entity + snapshot
  = ~2x memory per entity. 100K entities * 2x memory = OOM.
- Additionally: dirty check at commit = 100K entity comparisons
- Fix: flush+clear every N entities (N=50-100):
  ```java
  if (i % 50 == 0) { em.flush(); em.clear(); }
  ```
- `flush()`: write current batch to DB; `clear()`: drop all
  50 entities + their snapshots from session
- After clear(): session has 0 managed entities;
  next 50 start fresh; memory stays bounded
- Additional: use `hibernate.jdbc.batch_size=50` with
  ordered inserts for batching INSERT/UPDATE SQL