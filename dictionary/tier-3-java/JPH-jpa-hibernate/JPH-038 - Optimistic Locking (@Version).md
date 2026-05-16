---
id: JPH-038
title: "Optimistic Locking (@Version)"
category: JPA & Hibernate
tier: tier-3-java
folder: JPH-jpa-hibernate
difficulty: ★★★
depends_on: JPH-006, JPH-011, JPH-012, JPH-013, JPH-026, JPH-033
used_by: JPH-039, JPH-048, JPH-054, JPH-058
related: JPH-032, JPH-052
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
nav_order: 38
permalink: /jpa-hibernate/optimistic-locking/
---

# JPH-038 - Optimistic Locking (@Version)

⚡ **TL;DR** - Add `@Version` to an entity field
(typically `Long version` or `Instant lastModified`).
Hibernate adds `WHERE version=?` to every UPDATE/DELETE.
If the row was modified since last read (version mismatch),
the update affects 0 rows and Hibernate throws
`OptimisticLockException`. The caller retries. No database
locks held; high throughput. Fails under contention:
if two users edit the same record simultaneously, one
gets the exception. Handle it - don't swallow it.

| #038 | Category: JPA & Hibernate | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | @Entity, EntityManager, Session/Transaction, @Transactional, First Level Cache | |
| **Used by:** | Pessimistic Locking, Multi-Tenancy, JPA at Scale, Hibernate Internals | |
| **Related:** | JPA Auditing, Dirty Checking | |

---

### 🔥 The Problem This Solves

**THE LOST UPDATE PROBLEM:**
Two users load order #100 (status=PENDING, total=$200).
- User A changes status to CONFIRMED, saves.
- User B (who loaded stale data) changes total to $250, saves.
- User B's save overwrites User A's status change.
- Order is now: status=PENDING (reverted!), total=$250.
- User A's update is silently lost.

**WITHOUT LOCKING:**
```
T1: User A reads order (version=1, status=PENDING)
T2: User B reads order (version=1, status=PENDING)
T3: User A updates -> status=CONFIRMED, version=2
T4: User B updates -> total=250  (version still 1 in memory)
    -> UPDATE orders SET total=250, version=2 WHERE id=100
    -> NO version check -> blindly overwrites version=2!
    -> status=PENDING again (lost User A's change)
```

**WITH @VERSION:**
```
T4: User B's save:
    UPDATE orders SET total=250, version=2 WHERE id=100 AND version=1
    -> 0 rows affected (version is 2, not 1!)
    -> Hibernate throws OptimisticLockException
    -> User B gets "Conflict" error; must reload and retry
```

---

### 📘 Textbook Definition

**@Version** is a JPA annotation that designates a field
as the optimistic locking version counter. On every UPDATE
or DELETE, Hibernate adds `AND version = :currentVersion`
to the WHERE clause and increments the version on success.
If the WHERE clause matches 0 rows, a `StaleObjectStateException`
is thrown (which Spring wraps in `ObjectOptimisticLockingFailureException`).

**Supported field types:**
- `int` / `Integer` - counter (auto-incremented by Hibernate)
- `long` / `Long` - counter (same; recommended for large tables)
- `short` / `Short` - counter (overflow risk for active entities)
- `Timestamp` / `Instant` - timestamp (set to current time on update)
- `LocalDateTime` - timestamp

**Version field is managed by Hibernate** - application
code must NEVER manually set or increment the version field.

---

### ⏱️ Understand It in 30 Seconds

**One line:** `@Version` turns every UPDATE into
`UPDATE ... WHERE id=? AND version=?` - preventing
silent overwrites when concurrent sessions modify the
same entity.

**One analogy:**
> Editing a shared Google Doc is like optimistic locking:
> you work freely (no lock), but when you save, Google
> checks "did anyone else save since you opened this?"
> If yes: "Conflict detected - merge or discard." The
> document server doesn't lock you out while you're
> reading; it only checks for conflict at save time.
> That's optimistic locking: assume no conflict (optimistic),
> detect it at commit time.

**One insight:** Optimistic locking is appropriate when
conflicts are RARE (most users edit different records).
When conflicts are common (hundreds of users editing
the same hot row), pessimistic locking (SELECT FOR UPDATE)
is better - optimistic locking causes high retry rates
and poor UX under contention.

---

### 🔩 First Principles Explanation

**HOW @VERSION CHANGES THE SQL:**

```java
@Entity
public class Product {
    @Id private Long id;
    private String name;
    private BigDecimal price;

    @Version
    private Long version;  // Hibernate-managed
}

// When you call product.setPrice(newPrice) and flush:
```

```sql
-- WITHOUT @Version:
UPDATE products SET name=?, price=? WHERE id=?
-- Can silently overwrite concurrent changes

-- WITH @Version:
UPDATE products
SET name=?, price=?, version=3   -- always increments
WHERE id=? AND version=2         -- checks expected version

-- 0 rows affected? -> StaleObjectStateException
-- 1 row affected? -> success; entity version now = 3
```

**OPTIMISTIC LOCK EXCEPTION CHAIN:**

```
Hibernate:          StaleObjectStateException
JPA spec:           OptimisticLockException
Spring Data JPA:    ObjectOptimisticLockingFailureException
  (extends:)          OptimisticLockingFailureException
```

---

### 🧪 Thought Experiment

**WHAT HAPPENS IF YOU NEVER HANDLE THE EXCEPTION?**

```java
// Controller calls service:
@PostMapping("/products/{id}/price")
public ResponseEntity<ProductDto> updatePrice(
        @PathVariable Long id, @RequestBody BigDecimal price) {
    productService.updatePrice(id, price);
    return ResponseEntity.ok(...);
}

@Transactional
public void updatePrice(Long id, BigDecimal price) {
    Product p = productRepo.findById(id).orElseThrow();
    p.setPrice(price);
    // Transaction commits here; @Version check fires
    // If concurrent update: ObjectOptimisticLockingFailureException
}

// If exception is not caught:
// -> Spring's @Transactional rolls back
// -> Exception propagates to controller
// -> Spring Boot default error handler: HTTP 500
// -> User sees "Internal Server Error" with no useful message

// FIX: Catch and return 409 Conflict:
@PostMapping("/products/{id}/price")
public ResponseEntity<ProductDto> updatePrice(...) {
    try {
        productService.updatePrice(id, price);
        return ResponseEntity.ok(...);
    } catch (ObjectOptimisticLockingFailureException e) {
        return ResponseEntity.status(409)
            .body("Conflict: please reload and retry");
    }
}
```

---

### 🧠 Mental Model / Analogy

> Optimistic locking is like the "edit conflict" in Wikipedia:
> You open an article (read, no lock). You spend 10 minutes
> editing. You click Save. Wikipedia checks: "Did anyone
> else save this section since you opened it?" If yes:
> "Edit conflict - your changes are on the right, the
> current version on the left. Merge and re-save."
>
> No one was blocked while you were editing. The conflict
> check only happens at save time. Conflicts are rare for
> obscure articles (low contention). Conflicts are common
> for "Today's featured article" (high contention).
> When conflicts are common, the optimistic strategy fails.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
`@Version` prevents two users from accidentally overwriting
each other's changes. If two people edit the same record
simultaneously, the second save fails with an error
instead of silently overwriting the first person's work.

**Level 2 - How to add it (junior developer):**
Add `@Version private Long version;` to your entity.
JPA manages this field; never set it manually. When a
conflict occurs, catch `ObjectOptimisticLockingFailureException`
and return HTTP 409 Conflict to the client.

**Level 3 - How it works (mid-level engineer):**
On every UPDATE, Hibernate adds `AND version=?` to the
WHERE clause using the version value loaded at entity
read time. If another transaction incremented the version
between read and update, 0 rows are affected. Hibernate
detects this and throws `OptimisticLockException`.
The version field is incremented to `currentVersion + 1`
in the UPDATE SET clause.

**Level 4 - Timestamp vs counter version (senior engineer):**
Integer/Long version: counter increments on every update.
Monotonically increasing; comparison is exact (`version=2`).
Timestamp version: set to `NOW()` on update; only works if
timestamp precision is high enough that two concurrent updates
produce different timestamps. On some databases/JVMs,
two updates in the same millisecond produce the same timestamp
and the conflict is NOT detected. Counter-based version
is more reliable. Timestamp version is useful when you
also need the last-modified time for display, but add a
separate counter for the actual locking.

**Level 5 - Detached entity re-attach and ETag (staff engineer):**
A detached entity retains its `version` value. When
re-attached and updated via `em.merge()`, the version
check still fires - protecting against stale detached
entities. REST API pattern: include `version` (or an
ETag derived from it) in the response. Client sends
the version back in a `If-Match` header or request body.
Server loads the entity, checks client-provided version
against entity version before updating. If they differ:
`409 Conflict`. This is optimistic locking over HTTP
without a database session.

---

### ⚙️ How It Works (Mechanism)

**VERSION FIELD MANAGEMENT:**

```java
@Entity
public class BankAccount {
    @Id
    @GeneratedValue
    private Long id;

    private BigDecimal balance;

    @Version
    private Long version;  // starts at 0 on INSERT
    // Hibernate increments: 0 -> 1 -> 2 -> ...
    // DO NOT set this field in application code
    // DO NOT @Column(updatable=false) on this field
    // DO NOT reset to 0

    // BAD patterns:
    // this.version = 0;    // never reset
    // this.version++;      // never manually increment
    // DO NOT expose a setter for version
}
```

**EXCEPTION HANDLING PATTERN:**

```java
@Service
@RequiredArgsConstructor
public class BankAccountService {

    private final BankAccountRepository repo;

    @Transactional
    public void transfer(Long fromId, Long toId,
                         BigDecimal amount) {
        BankAccount from = repo.findById(fromId)
            .orElseThrow();
        BankAccount to = repo.findById(toId)
            .orElseThrow();

        if (from.getBalance().compareTo(amount) < 0) {
            throw new InsufficientFundsException();
        }

        from.setBalance(from.getBalance().subtract(amount));
        to.setBalance(to.getBalance().add(amount));

        // Transaction commit: Hibernate fires:
        // UPDATE bank_accounts SET balance=?, version=2
        //   WHERE id=1 AND version=1   -- checks version
        // UPDATE bank_accounts SET balance=?, version=2
        //   WHERE id=2 AND version=1   -- checks version
        // If either check fails: OptimisticLockException
    }
}

// REST controller:
@PatchMapping("/accounts/{id}/transfer")
public ResponseEntity<Void> transfer(
        @PathVariable Long id,
        @RequestBody TransferRequest req) {
    try {
        accountService.transfer(id, req.getToId(),
                                req.getAmount());
        return ResponseEntity.ok().build();
    } catch (ObjectOptimisticLockingFailureException e) {
        return ResponseEntity.status(HttpStatus.CONFLICT)
            .header("Retry-After", "1")
            .build();
    }
}
```

---

### 🔄 The Complete Picture - End-to-End Flow

**CONCURRENT UPDATE SCENARIO - FULL TIMELINE:**

```
Initial state: Product id=100, price=50.00, version=3

Thread A: loadProduct(100)  -> price=50, version=3 (in 1LC)
Thread B: loadProduct(100)  -> price=50, version=3 (in 1LC)

Thread A: product.setPrice(75.00)
Thread A: tx.commit()
  Hibernate: UPDATE products
             SET price=75.00, version=4
             WHERE id=100 AND version=3
  -> 1 row updated -> SUCCESS
  -> DB: price=75, version=4

Thread B: product.setPrice(60.00)
Thread B: tx.commit()
  Hibernate: UPDATE products
             SET price=60.00, version=4
             WHERE id=100 AND version=3
  -> 0 rows updated (version is 4, not 3!)
  -> Hibernate: StaleObjectStateException
  -> Spring: ObjectOptimisticLockingFailureException

Thread B handler: catch OptimisticLockingFailureException
  -> reload product (price=75, version=4)
  -> apply business logic again (re-apply price change)
  -> retry: UPDATE WHERE id=100 AND version=4
  -> 1 row updated -> SUCCESS
```

---

### 💻 Code Example

**Example 1 - BAD: swallowing OptimisticLockException:**

```java
// BAD: silently ignoring the conflict
@Transactional
public void updatePrice(Long id, BigDecimal price) {
    try {
        Product p = repo.findById(id).orElseThrow();
        p.setPrice(price);
    } catch (OptimisticLockException e) {
        log.warn("Conflict ignored: " + e.getMessage());
        // DO NOTHING
        // User thinks update succeeded; it didn't
        // Data: unchanged; UI: shows success
        // This is a data corruption scenario
    }
}

// GOOD: propagate or retry
@Transactional
public void updatePrice(Long id, BigDecimal price) {
    Product p = repo.findById(id).orElseThrow();
    p.setPrice(price);
    // Let OptimisticLockException propagate
    // Caller decides: retry, 409, or user notification
}
```

**Example 2 - REST ETag-based optimistic locking:**

```java
// Response includes version as ETag:
@GetMapping("/products/{id}")
public ResponseEntity<ProductDto> getProduct(
        @PathVariable Long id) {
    Product p = repo.findById(id).orElseThrow();
    return ResponseEntity.ok()
        .eTag(String.valueOf(p.getVersion()))
        .body(ProductDto.from(p));
}

// Update requires If-Match header with current version:
@PutMapping("/products/{id}")
public ResponseEntity<ProductDto> updateProduct(
        @PathVariable Long id,
        @RequestHeader("If-Match") String ifMatch,
        @RequestBody ProductDto dto) {
    Product p = repo.findById(id).orElseThrow();
    long clientVersion = Long.parseLong(
        ifMatch.replace("\"", ""));
    if (p.getVersion() != clientVersion) {
        return ResponseEntity.status(412).build();
        // 412 Precondition Failed = conflict
    }
    p.setName(dto.getName());
    p.setPrice(dto.getPrice());
    // @Version check still fires at commit
    return ResponseEntity.ok(ProductDto.from(repo.save(p)));
}
```

---

### ⚖️ Comparison Table

| Approach | Locking? | DB Cost | Contention | Best for |
|---|---|---|---|---|
| No locking | None | None | Lost updates | Single-user or append-only |
| Optimistic (@Version) | No lock | Check at UPDATE | Rare conflicts | Most web apps |
| Pessimistic (SELECT FOR UPDATE) | Row lock held | Lock held until commit | Common conflicts | Inventory, banking |
| Application-level mutex | External lock | Redis/DB call | Custom | Distributed systems |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "@Version prevents all concurrent access" | It does NOT block reads. Multiple transactions can read the same entity simultaneously. It only prevents silent overwrites at commit time. It's called "optimistic" because it assumes conflicts are rare. |
| "Timestamp @Version is as reliable as counter @Version" | Timestamp version can miss conflicts if two updates happen within the same clock tick (millisecond precision). Counter version is exact. On databases with low timestamp precision, timestamp locking has correctness bugs. |
| "I can call repository.save() to retry after OptimisticLockException" | After an `OptimisticLockException`, the EntityManager is in an inconsistent state. The transaction is invalid. You MUST start a new transaction with a fresh EntityManager (load the entity again) before retrying. Never retry within the same transaction. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode: High OptimisticLockException Rate Under Load**

**Symptom:** Under concurrent load, error logs fill with
`ObjectOptimisticLockingFailureException`. Service
degradation. Retry storms.
**Root Cause:** High contention on a "hot" entity (e.g.,
global counter, shared resource, popular product).
Many concurrent transactions read the same version;
only one wins; all others fail and retry - creating
more load.
**Diagnosis:** Check which entity is causing failures
from logs (`entity: Product#42 version: N -> expected N`).
If one entity ID dominates: it's a hot-row problem.
**Fix:** (1) Use pessimistic locking for the hot entity
(`@Lock(PESSIMISTIC_WRITE)`), (2) partition the hot
entity (separate row per shard), (3) use database
increment/decrement instead of read-modify-write,
(4) use CQRS with event sourcing for audit trail.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[JPH-026 - @Transactional with JPA]] - optimistic
  locking fires at transaction commit time
- [[JPH-033 - First Level Cache]] - version is part of
  the entity snapshot in the 1LC

**Builds On This (learn these next):**
- [[JPH-039 - Pessimistic Locking]] - the alternative
  for high-contention scenarios

**Related:**
- [[JPH-032 - JPA Auditing]] - @LastModifiedDate is
  often combined with @Version for display + locking
- [[JPH-052 - Dirty Checking and Flush Mode]] - flush
  is where the version check SQL is issued

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ ANNOTATION   │ @Version on Long/Integer field            │
│ SQL EFFECT   │ AND version=? added to every UPDATE       │
│ INCREMENT    │ Hibernate increments version automatically │
├──────────────┼───────────────────────────────────────────┤
│ EXCEPTION    │ ObjectOptimisticLockingFailureException   │
│ RESPONSE     │ HTTP 409 Conflict to client               │
│ RETRY        │ New transaction; reload entity; re-apply  │
├──────────────┼───────────────────────────────────────────┤
│ NEVER        │ Manually set version field                │
│ NEVER        │ Swallow the exception (data corruption)   │
│ NEVER        │ Retry in same transaction after exception │
├──────────────┼───────────────────────────────────────────┤
│ LIMIT        │ High contention -> many failures -> retry │
│              │ storms; use pessimistic lock for hot rows │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "@Version adds version check to UPDATE;  │
│              │ 0 rows affected = conflict;               │
│              │ OptimisticLockException thrown."          │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. `@Version` adds `AND version=?` to every UPDATE/DELETE;
   0 rows updated = `OptimisticLockException` = conflict
2. Always handle the exception - return HTTP 409; never
   swallow it; retry in a NEW transaction, not the same one
3. Under high contention (hot row): use pessimistic locking
   instead - optimistic locking causes retry storms

**Interview one-liner:** `@Version` implements optimistic
locking by adding `AND version=?` to UPDATE/DELETE statements.
If the version mismatches (another transaction updated
between read and write), 0 rows are affected and Hibernate
throws `OptimisticLockException` (Spring wraps to
`ObjectOptimisticLockingFailureException`). Application
returns HTTP 409; client reloads and retries in a new
transaction. Appropriate for low-contention writes.

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Optimistic vs pessimistic
concurrency control is a fundamental distributed systems
trade-off. Optimistic: assume no conflict; detect at commit;
high throughput; fails under contention. Pessimistic: acquire
lock before operation; guaranteed no conflict; lower throughput;
deadlock risk. The same choice appears in: database transactions
(MVCC is optimistic; `SELECT FOR UPDATE` is pessimistic),
distributed systems (CAS operations are optimistic; distributed
locks are pessimistic), version control (Git merge is optimistic;
SVN checkout lock is pessimistic), HTTP caching (ETags/If-Match
is optimistic). Choose based on measured or expected conflict rate.

**Where else this pattern appears:**
- **HTTP ETags** - `ETag` + `If-Match` header implement
  optimistic locking over HTTP for REST APIs
- **CAS (Compare-And-Swap)** - hardware atomic instruction;
  exact equivalent of `UPDATE WHERE version=?`
- **Git merge conflicts** - optimistic model; conflict
  detected at merge time, not at branch creation
- **MongoDB findAndModify** - `{ $set: ..., $inc: { version: 1 } }`
  combined with version filter is MongoDB optimistic locking

---

### 💡 The Surprising Truth

Hibernate's `@Version` does NOT work correctly with
bulk UPDATE/DELETE operations (`@Modifying @Query`).
Bulk operations bypass the EntityManager's entity
lifecycle - they execute direct SQL without checking
entity versions. This means: if you do a bulk UPDATE
(`UPDATE Product SET price = price * 0.9`), the version
field is NOT incremented (unless you include it in
the SET clause explicitly). Any entity already loaded
in a persistence context now has a STALE version - the
database has `version=3` but the in-memory entity has
`version=2`. The next `save()` call for that entity
will fail with `OptimisticLockException` even though
there was no actual concurrent modification. Fix: always
call `em.clear()` after bulk operations to evict stale
entities from the persistence context.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **IMPLEMENT** optimistic locking on an entity and
   handle the exception correctly (HTTP 409, retry logic)
2. **EXPLAIN** the SQL Hibernate generates with `@Version`
   and why 0 rows affected triggers the exception
3. **DIAGNOSE** unexpected `OptimisticLockException`
   after a bulk UPDATE (version staleness issue)
4. **DECIDE** when to use optimistic vs pessimistic locking
   based on expected conflict rate
5. **IMPLEMENT** REST API optimistic locking using ETags
   and `If-Match` headers

---

### 🎯 Interview Deep-Dive

**Q1: What does @Version do and when would you use it?**
*Why they ask:* Core concurrency pattern.
*Strong answer includes:*
- `@Version` adds `AND version=?` to UPDATE/DELETE SQL
- Hibernate increments the version in the SET clause
- 0 rows affected: `OptimisticLockException` thrown
- Use when: concurrent updates to same entity are possible
  but rare; high read throughput needed (no locks on reads)
- Don't use when: high contention on same entity (retry storms)

**Q2: What happens when two threads concurrently update the
same entity with @Version? Walk through the exact SQL.**
*Why they ask:* Tests depth of mechanism understanding.
*Strong answer includes:*
- Thread A reads (version=2), Thread B reads (version=2)
- Thread A commits: `UPDATE ... SET version=3 WHERE id=? AND version=2` -> 1 row updated
- Thread B commits: `UPDATE ... SET version=3 WHERE id=? AND version=2` -> 0 rows (version is now 3!)
- Hibernate detects 0 rows: throws `StaleObjectStateException`
- Spring wraps: `ObjectOptimisticLockingFailureException`
- Handler: new transaction, reload entity (version=3), re-apply changes, retry