---
layout: default
title: "Optimistic vs Pessimistic Locking"
parent: "Database Fundamentals"
nav_order: 49
permalink: /databases/optimistic-vs-pessimistic-locking/
id: DBF-049
category: Database Fundamentals
difficulty: ★★★
depends_on: Locking, MVCC, Transaction
used_by: Deadlock Detection, ORM Patterns, Concurrency
related: Locking, Deadlock Detection, MVCC, CAS
tags:
  - database
  - concurrency
  - patterns
  - deep-dive
---

# DBF-049 — Optimistic vs Pessimistic Locking

⚡ TL;DR — Pessimistic locking blocks others from modifying data while you work (high contention safety, deadlock risk); optimistic locking detects conflicts at commit time via a version number (no blocking, retry on conflict) — choose based on conflict probability.

| #444            | Category: Database Fundamentals               | Difficulty: ★★★ |
| :-------------- | :-------------------------------------------- | :-------------- |
| **Depends on:** | Locking, MVCC, Transaction                    |                 |
| **Used by:**    | Deadlock Detection, ORM Patterns, Concurrency |                 |
| **Related:**    | Locking, Deadlock Detection, MVCC, CAS        |                 |

---

### 🔥 The Problem This Solves

**SHARED PROBLEM:**
Two users try to update the same product record simultaneously. User A reads stock=10, User B reads stock=10. User A saves stock=8 (sold 2). User B saves stock=9 (sold 1, based on their stale read of 10). Final stock: 9. Should be 7. One unit appears from nowhere — a lost update.

**THE DEBATE:**

- **Pessimistic approach:** "Block User B while User A is working — no concurrent access to the same row."
- **Optimistic approach:** "Let both proceed; at save time, check if anyone else modified the row first — if yes, reject and retry."

**THE INVENTION MOMENT:**
Pessimistic: "Lock first, work safely." Optimistic: "Work freely, verify at end." Which is right depends on how often conflicts actually happen.

---

### 📘 Textbook Definition

**Pessimistic locking** acquires an exclusive lock on a resource before reading or modifying it, assuming conflicts are likely — other transactions must wait until the lock is released. Implemented via `SELECT ... FOR UPDATE`.

**Optimistic locking** assumes conflicts are rare — it does not acquire a lock at read time, but instead detects conflicts at write time using a **version identifier** (a version number column, or timestamp, or hash). At update time: `WHERE id=? AND version=<original_version>`. If 0 rows are updated (version changed by another transaction), a conflict is detected and the operation is retried with fresh data. Implemented via `@Version` in JPA/Hibernate, manual `WHERE version=?` checks, or database CAS operations.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Pessimistic: "Lock the door while you're inside"; Optimistic: "Leave the door open but check if anyone rearranged the furniture before you commit your changes."

**One analogy:**

> **Pessimistic:** A single bathroom key passed between users — whoever has the key is inside; others wait outside. Guaranteed no conflicts; high wait time when busy.
> **Optimistic:** An honor system — everyone works in open shared office; before you file your finished work, check that nobody modified the same file since you started. If they did, merge or retry. No waiting upfront; occasional rework.

- "Bathroom key" → exclusive DB row lock (`FOR UPDATE`)
- "Others waiting outside" → lock contention (queue of blocked transactions)
- "Open shared office" → no lock at read time (optimistic)
- "Check before filing" → version check at UPDATE time
- "Rework if conflict" → StaleObjectStateException → retry

**One insight:**
Optimistic locking shines when conflicts are rare (< 5% of operations) — no blocking, maximum concurrency. Pessimistic locking shines when conflicts are common — reduces wasted work from retries. For a seat reservation system (100 users racing for the last seat), optimistic locking means 99% will retry — use pessimistic. For a CMS where two authors rarely edit the same article, pessimistic locking means writers constantly block each other needlessly — use optimistic.

---

### 🔩 First Principles Explanation

**PESSIMISTIC LOCKING:**

```sql
-- PostgreSQL: acquire exclusive row lock at READ time
BEGIN;
SELECT stock FROM products WHERE id = 42 FOR UPDATE;
-- Other transactions trying to UPDATE product 42 are BLOCKED here
-- until this transaction commits or rolls back

UPDATE products SET stock = stock - 1 WHERE id = 42;
COMMIT;
-- Lock released: blocked transactions proceed
```

**OPTIMISTIC LOCKING (SQL manual):**

```sql
-- Read (no lock):
SELECT stock, version FROM products WHERE id = 42;
-- Gets: stock=10, version=7

-- Application computes new value: stock=9

-- Conditional update (CAS — Compare And Swap):
UPDATE products
SET stock = 9, version = 8
WHERE id = 42 AND version = 7;  -- only if version unchanged

-- Check rowcount:
-- rows_affected = 1 → success (no concurrent modification)
-- rows_affected = 0 → CONFLICT (version changed → retry from read)
```

**OPTIMISTIC LOCKING (JPA/Hibernate @Version):**

```java
@Entity
public class Product {
    @Id private Long id;

    @Column(name = "stock")
    private int stock;

    @Version  // Hibernate manages this automatically
    private int version;  // or Long, or Timestamp
}

@Transactional
public void sellProduct(Long productId, int quantity) {
    Product product = productRepo.findById(productId)
        .orElseThrow(() -> new NotFoundException(...));

    if (product.getStock() < quantity) {
        throw new InsufficientStockException();
    }

    product.setStock(product.getStock() - quantity);
    // Hibernate generates:
    // UPDATE products SET stock=?, version=version+1
    // WHERE id=? AND version=<original_version>
    // If 0 rows affected: throws OptimisticLockException
}
```

**OPTIMISTIC LOCKING RETRY PATTERN:**

```java
@Retryable(
    value = {OptimisticLockException.class, StaleObjectStateException.class},
    maxAttempts = 3,
    backoff = @Backoff(delay = 50, multiplier = 2)
)
@Transactional
public void sellProduct(Long productId, int quantity) {
    // ... as above
}
```

**THE TRADE-OFFS:**

**Pessimistic:**

- **Pro:** No wasted work — once you have the lock, the update will succeed.
- **Pro:** Appropriate for high-conflict scenarios (inventory depletion, seat booking).
- **Con:** Deadlock risk (two transactions locking resources in different orders).
- **Con:** Blocking — reduces concurrency; lock held for entire think time.
- **Con:** Lock hold time includes any application logic between read and write.

**Optimistic:**

- **Pro:** No blocking — maximum read concurrency.
- **Pro:** No deadlocks (no locks held).
- **Con:** Wasted work on conflict — read + compute + fail → read + compute + succeed.
- **Con:** Starvation possible under high conflict — transaction keeps retrying and losing.
- **Con:** Requires retry logic in application code.
- **Con:** Version field must be present in schema.

---

### 🧪 Thought Experiment

**SCENARIO: Event Ticket Booking (100 seats, 10,000 concurrent users)**

**WITH OPTIMISTIC LOCKING:**

- All 10,000 users read `seats_available = 100` (no lock — fast)
- First 100 users increment version, reduce seats: 100 succeed
- Users 101–10,000: `UPDATE ... WHERE version=original_version` → rows_affected=0 → conflict
- All 9,900 retry: read new version, check availability, attempt update
- Some seats are already 0: application rejects gracefully
- Result: high retry rate (990× retries), but no blocking
- Problem: under stampede, retry storm amplifies load

**WITH PESSIMISTIC LOCKING:**

- 10,000 users request `SELECT ... FOR UPDATE` on the booking record
- Database queues them: 1 at a time (serialized)
- Each reads current count, decrements, commits — next in line reads fresh count
- After seat 100: all remaining users read count=0, fail gracefully
- Result: no retries, no wasted work — but up to 9,999 concurrent lock waits
- Connection pool exhausted if wait time × concurrent users exceeds capacity

**THE INSIGHT:**
Neither is universally better. For this specific case (high contention, many losers), pessimistic avoids the retry storm but creates a connection queue. A better design: a queue with a single worker processing bookings serially (eliminating the conflict entirely), or Redis atomic DECR for the counter (then confirm in DB).

---

### 🧠 Mental Model / Analogy

> **Pessimistic:** Checking out a library book — one person checks it out; others wait for it to be returned. The librarian records it out; nobody else can take it. No conflicts possible; other people wait.
> **Optimistic:** Working on a shared Google Doc — everyone edits simultaneously; at "save," Google checks if the paragraph you edited was modified by someone else first; if yes, shows you a merge conflict to resolve.

- "Library checkout" → `SELECT FOR UPDATE` (exclusive lock)
- "Others waiting for return" → lock contention (blocked transactions)
- "Google Doc simultaneous editing" → optimistic (no lock at read time)
- "Merge conflict" → `OptimisticLockException` (version mismatch)
- "Resolving the merge" → application retry with fresh data

Where the analogy breaks down: Library books can only be held by one person; DB pessimistic locks can be released before the user is "done thinking" (a transaction commit) — the analogy breaks at the granularity of what "done" means.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
When two people try to modify the same data at the same time, one approach is to lock the data so only one person can work at a time (pessimistic — assume conflict will happen). The other approach is to let both work freely, but check when saving whether someone else also saved first (optimistic — assume conflict is rare). Pessimistic is like a locked room: guaranteed exclusive, but others wait. Optimistic is like comparing file timestamps: usually fine, occasionally you need to redo your work.

**Level 2 — How to use it (junior developer):**
Use optimistic locking (`@Version` in JPA) for: most business data where concurrent edits are rare (user profiles, product catalog, configuration). Add retry logic for `OptimisticLockException`. Use pessimistic locking (`SELECT FOR UPDATE`) for: inventory/stock counts, financial account balances, seat reservations — where concurrent conflicts are common and wasted retry work is expensive. Never use pessimistic locking for long operations (holding the lock while showing a user a form — minutes-long lock hold) — this blocks all other users.

**Level 3 — How it works (mid-level engineer):**
Hibernate `@Version` mechanism: on `entityManager.persist()` / `repo.save()`, Hibernate appends `AND version=N` to the UPDATE WHERE clause. `executeUpdate()` returns 0 if no rows matched → Hibernate throws `OptimisticLockException`. The entity's version field is incremented in the UPDATE: `SET version=N+1`. On load: the loaded version is stored in the persistence context snapshot. On flush: the snapshot version is used in the WHERE clause. This is why loading an entity twice in the same session returns the same object (identity map) — the version only updates on the initial load from DB. `SELECT FOR UPDATE SKIP LOCKED` is a powerful combination for queue processing: skip rows that are currently locked by another worker — implements a distributed job queue without a dedicated message broker.

**Level 4 — Why it was designed this way (senior/staff):**
The optimistic/pessimistic choice is fundamentally a bet about the conflict rate in the system. This is related to the CAP theorem's perspective on availability vs. consistency: pessimistic locking prioritizes consistency (no conflicts ever seen) at the cost of availability (others wait). Optimistic locking prioritizes availability (no waiting) with the cost of retries on conflict. The MVCC mechanism in PostgreSQL is a form of system-level optimistic concurrency: readers never block on writers (each sees their own snapshot); writers detect conflicts through the SSI (Serializable Snapshot Isolation) mechanism. The `@Version` pattern in JPA is an application-level implementation of the same principle. At scale, the debate is often resolved by avoiding shared mutable state: instead of multiple processes contending over the same row, use event sourcing (append-only log, no updates), or use a Compare-And-Swap operation in Redis (atomic INCR/DECR), or use a message queue (one consumer per message). These patterns eliminate the optimistic/pessimistic tradeoff by eliminating the shared-mutable-state architecture.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ PESSIMISTIC: SERIALIZE AT LOCK ACQUISITION           │
├──────────────────────────────────────────────────────┤
│ T1: SELECT stock FROM products WHERE id=1 FOR UPDATE │
│ T1: acquires exclusive row lock                      │
│ T2: SELECT stock FROM products WHERE id=1 FOR UPDATE │
│ T2: BLOCKED — waits for T1's lock                    │
│ T1: UPDATE products SET stock=9 WHERE id=1           │
│ T1: COMMIT → lock released                           │
│ T2: acquires lock, reads stock=9 (fresh)             │
│ T2: UPDATE products SET stock=8 WHERE id=1           │
│ T2: COMMIT → no conflict; correct final value: 8     │
├──────────────────────────────────────────────────────┤
│ OPTIMISTIC: DETECT CONFLICT AT COMMIT                │
├──────────────────────────────────────────────────────┤
│ T1: SELECT stock, version FROM products WHERE id=1   │
│     → stock=10, version=3 (no lock)                  │
│ T2: SELECT stock, version FROM products WHERE id=1   │
│     → stock=10, version=3 (no lock)                  │
│ T1: UPDATE products SET stock=9, version=4           │
│     WHERE id=1 AND version=3                         │
│     → rows_affected=1 → SUCCESS                     │
│ T2: UPDATE products SET stock=9, version=4           │
│     WHERE id=1 AND version=3                         │
│     → rows_affected=0 (version is now 4!) → CONFLICT│
│     → Application: OptimisticLockException → RETRY  │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**OPTIMISTIC CONFLICT RESOLUTION:**

```
User A and User B both load product P (stock=10, version=3)
→ [OPTIMISTIC LOCKING ← YOU ARE HERE: no lock held]
User A: reduce stock to 8, saves first:
  UPDATE products SET stock=8, version=4 WHERE id=P AND version=3 → SUCCESS
User B: tries to reduce stock to 9, saves second:
  UPDATE products SET stock=9, version=4 WHERE id=P AND version=3 → 0 rows
  → OptimisticLockException thrown
  → @Retryable catches it
  → User B's transaction retries: reloads (stock=8, version=4)
  → Reduces stock to 7, saves: WHERE id=P AND version=4 → SUCCESS
Final stock: 7 (correct)
```

**WHAT CHANGES AT SCALE:**
At high concurrency (1,000 concurrent requests to the same resource): optimistic locking generates N-1 retries → N-1 additional queries → amplification factor = concurrent users. Pessimistic serializes N requests → predictable queue depth. High-contention systems (flash sales, limited inventory) → pessimistic or Redis atomic operations. Low-contention systems (typical SaaS entities) → optimistic.

---

### ⚖️ Comparison Table

| Dimension          | Pessimistic                   | Optimistic                 |
| ------------------ | ----------------------------- | -------------------------- |
| Lock held          | From read until commit        | Never                      |
| Blocking           | Yes (others wait)             | No                         |
| Deadlock risk      | Yes (circular waits)          | No                         |
| Wasted work        | No (conflict impossible)      | Yes (retry on conflict)    |
| Schema change      | None (no version column)      | Yes (add `version` column) |
| Best conflict rate | High (> 10%)                  | Low (< 5%)                 |
| Best for           | Financial, inventory, booking | CMS, user profiles, config |

---

### ⚠️ Common Misconceptions

| Misconception                                        | Reality                                                                                                                                                                        |
| ---------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Optimistic locking has no performance cost           | Each retry is a full read-compute-write cycle — at high conflict rates, optimistic locking costs more CPU than pessimistic                                                     |
| `@Version` prevents all concurrent modification bugs | `@Version` only covers updates via Hibernate within the same loaded entity's session; bypassing JPA (native SQL update) can change the row without updating the version column |
| Pessimistic locking prevents all inconsistency       | Only within the transaction holding the lock; if the application holds a lock for minutes (showing a form to the user), the connection is wasted and others starve             |
| Optimistic locking can't deadlock                    | Correct — no locks are held, so no circular waits are possible. This is a genuine advantage                                                                                    |

---

### 🚨 Failure Modes & Diagnosis

**1. Optimistic Lock Starvation**

**Symptom:** A transaction retries many times and eventually fails or times out; high conflict rate on a hot entity.

**Root Cause:** Many transactions competing for the same row; the optimistic lock retry loop can't win quickly enough.

**Diagnostic:**

```
Log analysis: count OptimisticLockException per minute
If count > 5% of total writes to entity → consider pessimistic for this entity
```

**Fix:** Switch to pessimistic locking (`SELECT FOR UPDATE`) for the specific hot entity. Or redesign: use Redis DECR for the counter, confirm in DB asynchronously. Or shard the hot row (multiple rows that sum to the total).

---

**2. Pessimistic Lock Held Too Long**

**Symptom:** Application holds `FOR UPDATE` lock while waiting for user input (e.g., locks a seat while user fills out billing form); other users timeout waiting.

**Root Cause:** Transaction started before user interaction, lock held until user submits form (could be minutes).

**Fix:** Never hold a pessimistic lock during user think time. Pattern: use optimistic locking with a timeout token — lock the seat for 10 minutes via a separate "reservation" mechanism, not a DB lock. Release if payment not completed within 10 minutes.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Locking (Row, Table, Gap, Next-Key)` — pessimistic locking uses row locks
- `MVCC` — optimistic locking shares principles with MVCC (snapshot + conflict detection)
- `Transaction` — both strategies operate within transactions

**Builds On This (learn these next):**

- `Deadlock Detection (DB)` — pessimistic locking can cause deadlocks; optimistic cannot
- `ORM Patterns` — `@Version` is the ORM implementation of optimistic locking

**Alternatives / Comparisons:**

- `Locking` — pessimistic locking IS database locking
- `CAS (Compare-And-Swap)` — optimistic locking IS CAS applied to database rows
- `MVCC` — system-level optimistic concurrency built into the database engine

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ PESSIMISTIC  │ SELECT ... FOR UPDATE                     │
│              │ Blocks others; no retries; deadlock risk  │
│              │ Use: high-conflict, financial, inventory  │
├──────────────┼───────────────────────────────────────────┤
│ OPTIMISTIC   │ @Version column + WHERE version=N check   │
│              │ No blocking; retry on conflict; no deadlk │
│              │ Use: low-conflict, CMS, user profiles     │
├──────────────┼───────────────────────────────────────────┤
│ CHOOSE BY    │ Conflict rate < 5% → optimistic           │
│              │ Conflict rate > 10% → pessimistic         │
├──────────────┼───────────────────────────────────────────┤
│ RETRY LOGIC  │ @Retryable(OptimisticLockException.class) │
│              │ maxAttempts=3, backoff with jitter        │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Pessimistic: lock first, work safely.    │
│              │  Optimistic: work freely, verify at end." │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Locking → Deadlock Detection → MVCC       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE C — Design Question) A ticket booking platform needs to handle 50,000 concurrent users trying to book one of 100 remaining seats for a concert. Compare: (a) pessimistic locking on the `remaining_seats` row, (b) optimistic locking with retries, (c) Redis DECR atomic operation with DB confirmation. For each: estimate conflict rate, retry overhead, connection pool pressure, and UX (how long does a user wait?). Which do you recommend and why?

**Q2.** (TYPE F — Comparison Depth) Explain how PostgreSQL's Serializable Snapshot Isolation (SSI) implements system-level optimistic concurrency. Compare SSI to application-level optimistic locking (`@Version`): (a) what anomalies does each prevent? (b) what is the overhead of each? (c) in what scenario would SSI abort a transaction that `@Version` would not detect as a conflict?
