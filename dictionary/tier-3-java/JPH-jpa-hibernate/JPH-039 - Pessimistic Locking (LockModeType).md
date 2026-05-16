---
id: JPH-039
title: "Pessimistic Locking (LockModeType)"
category: JPA & Hibernate
tier: tier-3-java
folder: JPH-jpa-hibernate
difficulty: ★★★
depends_on: JPH-011, JPH-012, JPH-013, JPH-026, JPH-033, JPH-038
used_by: JPH-048, JPH-054, JPH-058
related: JPH-052, JPH-045
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
nav_order: 39
permalink: /jpa-hibernate/pessimistic-locking/
---

# JPH-039 - Pessimistic Locking (LockModeType)

⚡ **TL;DR** - `em.find(Product.class, id, LockModeType.PESSIMISTIC_WRITE)`
generates `SELECT ... FOR UPDATE`, holding a database
row lock until the transaction commits. Use for high-
contention scenarios (inventory decrement, seat booking)
where optimistic locking's retry storm is worse than
the cost of the lock. Critical risk: deadlock if two
transactions lock rows in different orders. Always lock
rows in a consistent order. Keep transactions SHORT -
the lock is held for the entire transaction duration.

| #039 | Category: JPA & Hibernate | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | EntityManager, Session/Transaction, JPA Lifecycle, @Transactional, First Level Cache, Optimistic Locking | |
| **Used by:** | Multi-Tenancy, JPA at Scale, Hibernate Internals | |
| **Related:** | Dirty Checking, Batch Processing | |

---

### 🔥 The Problem This Solves

**WHEN OPTIMISTIC LOCKING IS NOT ENOUGH:**
An e-commerce site sells 100 seats for a concert.
At ticket release time, 1,000 users simultaneously
try to purchase. With optimistic locking:
- 1,000 concurrent reads (all see quantity=100)
- First 100 succeed; remaining 900 get `OptimisticLockException`
- 900 retries; most fail again
- Retry storm: server overloaded processing 1,000+
  failed attempts plus the retries

**REAL SCENARIO: INVENTORY DECREMENT:**
```java
// Without locking: race condition
Product product = repo.findById(id).orElseThrow();
if (product.getStock() > 0) {
    product.setStock(product.getStock() - 1);
    // Two concurrent threads: both read stock=1
    // Both pass the if-check
    // Both decrement: stock goes to -1
    // Oversold!
}
```

**WITH PESSIMISTIC WRITE:**
```java
Product product = em.find(Product.class, id,
    LockModeType.PESSIMISTIC_WRITE);
// SELECT ... FROM products WHERE id=? FOR UPDATE
// First thread acquires the lock
// Second thread BLOCKS at the SELECT FOR UPDATE
// First thread decrements and commits
// Second thread proceeds, reads stock=0
// Second thread: correctly rejects purchase
```

---

### 📘 Textbook Definition

**Pessimistic Locking** acquires a database-level lock
on a row before reading it, preventing other transactions
from modifying (or reading, depending on lock type) it
until the lock is released at commit/rollback.

**JPA LockModeType values:**

| Mode | SQL | Behavior |
|---|---|---|
| `PESSIMISTIC_READ` | `SELECT ... FOR SHARE` (or `LOCK IN SHARE MODE`) | Prevents other writers; multiple readers can coexist |
| `PESSIMISTIC_WRITE` | `SELECT ... FOR UPDATE` | Exclusive lock; blocks other readers (in some databases) and all writers |
| `PESSIMISTIC_FORCE_INCREMENT` | `SELECT ... FOR UPDATE` + version increment | Exclusive lock AND increments @Version counter |
| `OPTIMISTIC` | No SQL lock; version check at commit | See JPH-038 |
| `OPTIMISTIC_FORCE_INCREMENT` | No SQL lock; force version increment at commit | Use when updating owned collections |

---

### ⏱️ Understand It in 30 Seconds

**One line:** Pessimistic locking says "I'm going to
update this row - block everyone else from touching it
until I'm done."

**One analogy:**
> A pessimistic transaction is like reserving a meeting
> room before your meeting: you book it (lock acquired),
> nobody else can book it while you have the reservation
> (lock held), and you release it when done (commit).
> An optimistic transaction is: you walk in assuming
> it's free, do your meeting, and when you try to book
> the room record, you discover someone else grabbed it.
> Room = database row. Meeting = transaction.

**One insight:** Pessimistic locking trades throughput
for correctness under contention. The lock is held from
`SELECT FOR UPDATE` to transaction commit - everything
in between is "locked time". The longer the transaction,
the longer other transactions wait. Keep transactions
with pessimistic locks as short as possible: acquire lock,
do the critical section, commit immediately.

---

### 🔩 First Principles Explanation

**HOW PESSIMISTIC WRITE WORKS:**

```
Transaction A:
  BEGIN TRANSACTION
  SELECT * FROM products WHERE id=42 FOR UPDATE
  -> Lock acquired on row 42
  product.stock = 99  (decremented)
  UPDATE products SET stock=99 WHERE id=42
  COMMIT
  -> Lock released

Transaction B (while A holds the lock):
  BEGIN TRANSACTION
  SELECT * FROM products WHERE id=42 FOR UPDATE
  -> BLOCKS (waits for A's lock to release)
  [A commits; lock released]
  -> Proceeds; reads stock=99
  product.stock = 98  (decremented)
  UPDATE products SET stock=98 WHERE id=42
  COMMIT
```

**LOCK SCOPE:**
Database pessimistic locks are per-row (row-level locking).
Only the locked row is blocked; other rows in the same table
are not affected. On MySQL InnoDB: gap locks may be acquired
if the WHERE condition uses a non-unique index (locking
a range of potential rows). On PostgreSQL: strict row-level
locking, no gap locks for `SELECT FOR UPDATE`.

---

### 🧪 Thought Experiment

**DEADLOCK - CLASSIC PATTERN:**

```
Transaction A: Transfer $100 from Account 1 to Account 2
  T=1: SELECT ... FROM accounts WHERE id=1 FOR UPDATE  [Lock 1]
  T=2: SELECT ... FROM accounts WHERE id=2 FOR UPDATE  [Wait for Lock 2]

Transaction B: Transfer $50 from Account 2 to Account 1
  T=1: SELECT ... FROM accounts WHERE id=2 FOR UPDATE  [Lock 2]
  T=2: SELECT ... FROM accounts WHERE id=1 FOR UPDATE  [Wait for Lock 1]

Result: A waits for B's lock on row 2.
        B waits for A's lock on row 1.
        Neither can proceed: DEADLOCK.

Database detects cycle; rolls back one transaction:
  SQLState: 40001 "Deadlock found when trying to get lock"

FIX: Always lock rows in the SAME order:
  Both transactions: lock row with lower ID first
  A: lock(1), lock(2)  [OK]
  B: lock(1), lock(2)  [OK - waits for A, then proceeds]
  No circular wait -> no deadlock
```

---

### 🧠 Mental Model / Analogy

> Pessimistic locking is like the old-school library book
> checkout system: you physically remove the book from the
> shelf (acquire lock) and place it on your desk. While you
> have it, nobody else can read it (blocked). You return it
> when done (commit). The library only has one copy of the
> "Hot Row: Product Stock" book, so everyone must wait.
> The checkout period (transaction duration) determines
> how long others wait. If you take the book to a coffee shop
> for an hour (long transaction), you block everyone for
> an hour. The book should never leave the room (keep
> transactions short).

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Pessimistic locking reserves a database row for exclusive
use during a transaction. Other transactions that want
the same row must wait. This prevents two transactions
from making conflicting changes simultaneously.

**Level 2 - How to use it (junior developer):**
Add `LockModeType.PESSIMISTIC_WRITE` to `em.find()` or
to a Spring Data query hint. Keep the transaction short.
Catch `PessimisticLockException` for deadlock/timeout
handling.

**Level 3 - Lock modes (mid-level engineer):**
`PESSIMISTIC_READ`: `SELECT FOR SHARE` - multiple readers
OK; writers blocked. Good for check-then-act where
concurrent reads are acceptable.
`PESSIMISTIC_WRITE`: `SELECT FOR UPDATE` - exclusive lock;
all other access blocked. Use for modify operations.
`PESSIMISTIC_FORCE_INCREMENT`: exclusive lock AND
increments `@Version` - needed for cross-entity version
coordination.

**Level 4 - Deadlock prevention (senior engineer):**
Deadlocks occur when two transactions hold and wait for
each other's locks in a cycle. Prevent by: (1) consistent
lock ordering (always lock by entity ID ascending),
(2) minimizing the number of rows locked per transaction,
(3) using `NOWAIT` to fail fast instead of blocking
(Hibernate: `javax.persistence.lock.timeout=0`),
(4) keeping transactions very short. Detect deadlocks
via `PessimisticLockException` with `SQLState 40001`.

**Level 5 - Lock escalation and isolation level (staff engineer):**
In databases with lock escalation (SQL Server), too many
row locks on a table may escalate to a table lock,
blocking ALL transactions on that table. PostgreSQL and
MySQL InnoDB do not escalate row locks to table locks
(no automatic escalation), but table locks can still be
acquired via `LOCK TABLE` or DDL operations. Know your
database's isolation level default: `READ COMMITTED`
(PostgreSQL, MySQL default for InnoDB in most configs)
means non-locked reads are not blocked by `SELECT FOR UPDATE`
(only other `SELECT FOR UPDATE` or writes are blocked).
`SERIALIZABLE` isolation blocks non-locked reads too.

---

### ⚙️ How It Works (Mechanism)

**SPRING DATA JPAREPOSITORY WITH LOCK:**

```java
public interface ProductRepository
        extends JpaRepository<Product, Long> {

    // Method with @Lock annotation:
    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("SELECT p FROM Product p WHERE p.id = :id")
    Optional<Product> findByIdForUpdate(
        @Param("id") Long id);
    // Generates: SELECT ... FROM products WHERE id=?
    //            FOR UPDATE

    // Lock timeout (database-level, in milliseconds):
    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @QueryHints({@QueryHint(
        name = "javax.persistence.lock.timeout",
        value = "3000")})  // 3 second timeout; then throw
    @Query("SELECT p FROM Product p WHERE p.id = :id")
    Optional<Product> findByIdForUpdateWithTimeout(
        @Param("id") Long id);
}
```

**ENTITY MANAGER DIRECT USE:**

```java
@Transactional
public void decrementStock(Long productId, int quantity) {
    // Acquire lock immediately on read:
    Product product = em.find(Product.class, productId,
        LockModeType.PESSIMISTIC_WRITE);
    // SELECT ... FROM products WHERE id=? FOR UPDATE
    // Blocks until lock acquired (or timeout)

    if (product.getStock() < quantity) {
        throw new InsufficientStockException(
            "Stock: " + product.getStock() +
            ", requested: " + quantity);
    }
    product.setStock(product.getStock() - quantity);
    // UPDATE fires at flush; lock released at commit
}
```

**LOCK ON EXISTING ENTITY:**

```java
@Transactional
public void lockExisting(Long id) {
    Product product = em.find(Product.class, id);
    // Entity loaded without lock (possibly from 1LC)

    // Upgrade lock AFTER initial load:
    em.lock(product, LockModeType.PESSIMISTIC_WRITE);
    // Issues: SELECT ... FOR UPDATE for the row

    // Or in one call (em.refresh upgrades to lock):
    em.refresh(product, LockModeType.PESSIMISTIC_WRITE);
    // Reloads AND acquires lock
}
```

---

### 🔄 The Complete Picture - End-to-End Flow

**TICKET BOOKING WITH PESSIMISTIC LOCK:**

```java
@Service
@RequiredArgsConstructor
public class TicketService {

    private final EventRepository eventRepo;
    private final BookingRepository bookingRepo;

    @Transactional
    public Booking bookTickets(Long eventId, Long userId,
                               int quantity) {
        // 1. Acquire exclusive lock on event row
        Event event = eventRepo.findByIdForUpdate(eventId)
            .orElseThrow(() -> new EventNotFoundException(
                eventId));
        // SELECT * FROM events WHERE id=? FOR UPDATE
        // Other concurrent bookings BLOCK here

        // 2. Check availability (atomic check under lock)
        if (event.getAvailableSeats() < quantity) {
            throw new NoSeatsAvailableException(
                "Available: " + event.getAvailableSeats());
        }

        // 3. Reserve seats
        event.setAvailableSeats(
            event.getAvailableSeats() - quantity);

        // 4. Create booking record
        Booking booking = new Booking();
        booking.setEventId(eventId);
        booking.setUserId(userId);
        booking.setQuantity(quantity);
        bookingRepo.save(booking);

        // 5. Commit releases lock
        return booking;
        // Other concurrent bookings proceed from step 1
    }
}
```

---

### 💻 Code Example

**Example 1 - BAD: lock acquired too late:**

```java
// BAD: entity already loaded and checked without lock
@Transactional
public void purchaseTicket(Long eventId) {
    Event event = eventRepo.findById(eventId).orElseThrow();
    // No lock - two threads can read simultaneously

    if (event.getAvailableSeats() > 0) {
        // RACE CONDITION: both threads pass this check
        event.setAvailableSeats(
            event.getAvailableSeats() - 1);
        // Both decrement: oversold!
    }
}

// GOOD: lock on initial read
@Transactional
public void purchaseTicket(Long eventId) {
    Event event = eventRepo.findByIdForUpdate(eventId)
        .orElseThrow();
    // Lock acquired at read; check is now atomic

    if (event.getAvailableSeats() > 0) {
        event.setAvailableSeats(
            event.getAvailableSeats() - 1);
    } else {
        throw new SoldOutException();
    }
}
```

**Example 2 - Handle lock timeout gracefully:**

```java
@Transactional
public void purchaseWithTimeout(Long eventId) {
    try {
        Event event = eventRepo
            .findByIdForUpdateWithTimeout(eventId)
            .orElseThrow();
        // 3-second timeout; if lock not acquired in 3s:
        // -> PessimisticLockException thrown

        event.setAvailableSeats(
            event.getAvailableSeats() - 1);
    } catch (PessimisticLockException |
             LockTimeoutException e) {
        throw new ServiceBusyException(
            "System busy; please retry in a moment");
    }
}
```

---

### ⚖️ Comparison Table

| Feature | Optimistic (@Version) | Pessimistic (FOR UPDATE) |
|---|---|---|
| DB lock held? | No | Yes (until commit) |
| Read throughput | High | Blocked (WRITE mode) |
| Conflict detection | At commit | At read |
| Deadlock risk | None | Yes |
| Best for | Low contention | High contention |
| Transaction length | Any | Keep short |
| Exception | OptimisticLockException | PessimisticLockException |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Pessimistic locking blocks ALL reads" | Depends on lock mode and database. `PESSIMISTIC_WRITE` (FOR UPDATE) blocks other FOR UPDATE readers and writers. Regular (non-locked) reads at READ COMMITTED isolation level are NOT blocked in PostgreSQL and MySQL InnoDB. MVCC allows consistent reads of the last committed version. |
| "Lock is acquired when the method starts" | The lock is acquired when `em.find(..., PESSIMISTIC_WRITE)` or the repository query executes - not when the `@Transactional` method starts. The lock window = from `SELECT FOR UPDATE` to commit. |
| "Pessimistic locking prevents all data anomalies" | Pessimistic WRITE locks the specified row(s). It does NOT prevent phantom reads (new rows inserted that match a query's WHERE). To prevent phantoms: use `SERIALIZABLE` isolation or lock the index range. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode: Deadlock Exception in Production**

**Symptom:** `com.mysql.jdbc.exceptions.jdbc4.MySQLTransactionRollbackException:
Deadlock found when trying to get lock; try restarting transaction`
or PostgreSQL: `ERROR: deadlock detected DETAIL: Process X waits
for ShareLock on transaction N; blocked by process Y`.
**Root Cause:** Two concurrent transactions lock rows in
different orders, creating a circular wait.
**Diagnosis:**
```sql
-- MySQL: check deadlock details
SHOW ENGINE INNODB STATUS;
-- Look for "LATEST DETECTED DEADLOCK" section

-- PostgreSQL: pg_stat_activity + pg_locks
SELECT pid, query, state, wait_event_type, wait_event
FROM pg_stat_activity
WHERE wait_event_type = 'Lock';
```
**Fix:**
1. Lock rows in consistent order (by primary key ascending)
2. Add a lock ordering utility:
   ```java
   List<Long> sorted = ids.stream().sorted().toList();
   for (Long id : sorted) { em.find(X.class, id, PESS_WRITE); }
   ```
3. Use NOWAIT to fail fast; implement retry with backoff

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[JPH-038 - Optimistic Locking]] - understand optimistic
  locking trade-offs before choosing pessimistic
- [[JPH-026 - @Transactional]] - pessimistic lock is held
  for the full transaction duration

**Builds On This (learn these next):**
- [[JPH-048 - Multi-Tenancy]] - multi-tenant scenarios
  often require fine-grained locking strategies

**Related:**
- [[JPH-052 - Dirty Checking and Flush Mode]] - flush
  timing matters for when locked-entity updates execute
- [[JPH-045 - Batch Processing]] - batch inserts/updates
  interact with row-level locks

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ READ LOCK    │ PESSIMISTIC_READ  -> FOR SHARE            │
│ WRITE LOCK   │ PESSIMISTIC_WRITE -> FOR UPDATE           │
│ BOTH+VERSION │ PESSIMISTIC_FORCE_INCREMENT               │
├──────────────┼───────────────────────────────────────────┤
│ SPRING DATA  │ @Lock(LockModeType.PESSIMISTIC_WRITE)     │
│ EM           │ em.find(X.class, id, PESSIMISTIC_WRITE)   │
├──────────────┼───────────────────────────────────────────┤
│ LOCK WINDOW  │ SELECT FOR UPDATE -> COMMIT/ROLLBACK      │
│ RULE         │ Keep the window as SHORT as possible      │
├──────────────┼───────────────────────────────────────────┤
│ DEADLOCK     │ Lock rows in SAME ORDER (ascending ID)   │
│ TIMEOUT      │ javax.persistence.lock.timeout (ms)       │
├──────────────┼───────────────────────────────────────────┤
│ EXCEPTION    │ PessimisticLockException (deadlock/TO)   │
│ USE WHEN     │ High contention; optimistic fails         │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "SELECT FOR UPDATE held until commit;    │
│              │ blocks concurrent writes; deadlock risk;  │
│              │ lock in consistent order; keep tx short." │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. `PESSIMISTIC_WRITE` generates `SELECT FOR UPDATE`;
   row is locked from that point until transaction commits
2. Keep the transaction as short as possible - others
   block for the entire lock duration
3. Deadlocks happen when locks are acquired in different
   orders - always lock rows in a consistent order (by ID)

**Interview one-liner:** Pessimistic locking uses
`SELECT FOR UPDATE` to acquire a database row lock at read
time, blocking other writers until the transaction commits.
Use for high-contention scenarios (inventory, seats) where
optimistic locking's retry storms are worse than the lock
cost. Risks: deadlock (lock rows in consistent order),
long-held locks (keep transactions short), timeout
(catch `PessimisticLockException`).

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** When choosing between
optimistic and pessimistic concurrency control, the
decision factor is conflict probability, not safety.
Both mechanisms are safe (neither allows silent data
corruption). The trade-off: optimistic provides higher
read throughput but degrades under contention (retry storms);
pessimistic provides deterministic behavior under contention
but lower throughput and deadlock risk. Measure the expected
conflict rate for the specific operation. For operations
where conflict probability > 10-20%, pessimistic typically
outperforms optimistic due to reduced retry overhead.
This analysis applies to: distributed locks (Redis SETNX),
file system locks (flock), message queue consumer groups
(partition assignment locking).

**Where else this pattern appears:**
- **Redis SETNX** - `SET key value NX EX 30` is pessimistic
  locking: acquire or fail immediately; held for TTL
- **Database transactions SERIALIZABLE** - serializable
  isolation is a form of pessimistic concurrency (predicate
  locks on ranges)
- **JVM synchronized** - `synchronized(monitor)` is
  pessimistic: thread blocks until lock available
- **File locking** - `java.nio.file.FileLock` is pessimistic:
  lock held until released

---

### 💡 The Surprising Truth

JPA's `PESSIMISTIC_READ` mode (generating `SELECT FOR SHARE`)
is rarely useful in practice and often misunderstood.
At READ COMMITTED isolation (the default for most production
databases), regular reads are NOT blocked by `SELECT FOR UPDATE`
or `SELECT FOR SHARE` due to MVCC - they simply read
the last committed version. So `PESSIMISTIC_READ`'s claim
to "allow concurrent reads while blocking writes" only
applies to other `PESSIMISTIC_READ` reads vs. regular reads
- regular reads aren't blocked by writers anyway under MVCC.
The practical result: `PESSIMISTIC_READ` primarily prevents
other `PESSIMISTIC_WRITE` from acquiring an exclusive lock
(because shared locks block exclusive locks). This is only
useful in the specific pattern "I want to ensure nobody
is currently updating this row while I read it" - even
though regular reads don't block. `PESSIMISTIC_WRITE` is
the almost universally correct choice for pessimistic
concurrency in production.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **IMPLEMENT** a ticket booking system using
   `PESSIMISTIC_WRITE` that prevents overselling
2. **EXPLAIN** the deadlock scenario and implement
   consistent lock ordering to prevent it
3. **COMPARE** optimistic vs pessimistic locking trade-offs
   and recommend the right one for a given use case
4. **CONFIGURE** lock timeout and handle
   `PessimisticLockException` gracefully
5. **EXPLAIN** why regular reads are not blocked by
   `PESSIMISTIC_WRITE` at READ COMMITTED isolation level

---

### 🎯 Interview Deep-Dive

**Q1: When would you choose pessimistic locking over
optimistic locking?**
*Why they ask:* Core concurrency decision-making.
*Strong answer includes:*
- Choose pessimistic when: high contention expected
  (same hot row, many concurrent writes); cost of retry
  storm (optimistic) > cost of lock holding (pessimistic)
- Examples: inventory decrement, seat booking, bank transfer
- Choose optimistic when: low contention; most users edit
  different records; high read throughput required
- Trade-off: optimistic = higher throughput under low contention;
  pessimistic = predictable latency under high contention

**Q2: How do you prevent deadlocks when using pessimistic locking?**
*Why they ask:* Practical production safety knowledge.
*Strong answer includes:*
- Root cause: circular wait - A holds X, waits for Y;
  B holds Y, waits for X
- Prevention: consistent lock acquisition ORDER (sort
  entity IDs ascending, lock in that order across all transactions)
- NOWAIT: `lock.timeout=0` - fail immediately if lock
  unavailable; no blocking; implement retry with backoff
- Detection: `PessimisticLockException` with `SQLState 40001`
- Timeouts: `lock.timeout=N` (milliseconds) prevents infinite waits