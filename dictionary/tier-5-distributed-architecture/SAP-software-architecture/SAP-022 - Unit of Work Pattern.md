---
id: SAP-022
title: Unit of Work Pattern
category: Software Architecture Patterns
tier: tier-5-distributed-architecture
folder: SAP-software-architecture
difficulty: ★★★
depends_on: SAP-021, SAP-023
used_by: SAP-021
related: SAP-021, SAP-029
tags:
  - architecture
  - pattern
  - database
  - advanced
status: complete
version: 1
layout: default
parent: "Software Architecture Patterns"
grand_parent: "Technical Dictionary"
nav_order: 22
permalink: /software-architecture/unit-of-work-pattern/
---

# SAP-022 - Unit of Work Pattern

⚡ TL;DR - The Unit of Work tracks all domain object changes during a business operation and commits them to the database in a single atomic transaction.

| Field          | Value            |
| -------------- | ---------------- |
| **Depends on** | SAP-021, SAP-023 |
| **Used by**    | SAP-021          |
| **Related**    | SAP-021, SAP-029 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A business operation "transfer money" updates two accounts: debit source, credit target. Without coordination, the debit saves to the database, then an unexpected error occurs before the credit save. The source account has less money. The target account has no more money. The money has vanished. You've introduced an accounting inconsistency.

**THE BREAKING POINT:**
Without a mechanism to group all changes from one business operation into a single atomic commit, every multi-step write operation is a potential source of data corruption. The more repositories and domain objects a single business operation touches, the more dangerous the problem becomes.

**THE INVENTION MOMENT:**
This is exactly why the Unit of Work pattern was created - to buffer all changes made during a business operation and apply them atomically as a single database transaction, ensuring either all changes commit or none do.

**EVOLUTION:**
Martin Fowler documented the Unit of Work in "Patterns of Enterprise Application Architecture" (2002). The JPA `EntityManager` is the canonical Java implementation - when a Spring `@Transactional` method completes, the EntityManager's Unit of Work flushes all pending changes in a single transaction. Hibernate's Session and .NET's Entity Framework DbContext both implement the same pattern. The pattern predates ORM frameworks - ADO.NET's `SqlTransaction` is a manual implementation. Modern Event Sourcing systems extend the Unit of Work concept to include publishing domain events atomically alongside database writes via the Outbox Pattern.

---

### 📘 Textbook Definition

The Unit of Work Pattern, documented by Martin Fowler in "Patterns of Enterprise Application Architecture," is a structural pattern that maintains a list of domain objects affected by a business transaction. It tracks new objects, modified objects, and deleted objects, and at the end of the business operation, it coordinates the writing out of all changes as a single atomic database transaction. The Unit of Work ensures that all writes within a business operation either succeed together or fail together, maintaining data consistency.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A shopping basket for database changes - collect everything, then pay (commit) once.

**One analogy:**

> A shopping basket at a supermarket. You walk through the store adding items (registering domain changes). You don't pay for each item as you pick it up - you pay once at the checkout (commit). If your card is declined, you return everything (rollback). The payment is atomic: either you pay for everything or for nothing.

**One insight:**
The Unit of Work separates the "deciding what changes to make" (domain logic phase) from the "actually making the changes" (persistence phase). This separation is what allows domain logic to be tested without database transactions, and what ensures changes are atomic.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. A Unit of Work represents exactly one business transaction - it begins when an operation starts and ends when it commits or rolls back.
2. The Unit of Work tracks domain objects in three states: new (to be inserted), dirty (to be updated), deleted (to be removed).
3. Commit applies all tracked changes in the correct order within a single database transaction.

**DERIVED DESIGN:**

```
┌──────────────────────────────────────────────────────────┐
│              UNIT OF WORK LIFECYCLE                      │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Business Operation Start                                │
│       ↓                                                  │
│  UnitOfWork.begin()                                      │
│       ↓                                                  │
│  Load Order (tracked as "clean")                         │
│  Load Customer (tracked as "clean")                      │
│       ↓                                                  │
│  order.addItem(item)  → UoW marks Order as "dirty"       │
│  customer.deductCredit() → UoW marks Customer as "dirty" │
│  invoice = new Invoice() → UoW marks Invoice as "new"    │
│       ↓                                                  │
│  UnitOfWork.commit()                                     │
│  → BEGIN TRANSACTION                                     │
│  → INSERT Invoice (new)                                  │
│  → UPDATE Order (dirty)                                  │
│  → UPDATE Customer (dirty)                               │
│  → COMMIT TRANSACTION                                    │
│  (all succeed or all rollback)                           │
└──────────────────────────────────────────────────────────┘
```

**THE TRADE-OFFS:**
**Gain:** Atomicity across multiple domain objects and repositories. Dirty tracking prevents unnecessary database writes (only changed objects are saved). Single round-trip to the database for all changes.
**Cost:** In-memory state can drift from database state during a long operation. Long-running units of work hold database connections and locks, affecting concurrency. Debugging is harder because the commit point is detached from the domain operations.

---

### 🧪 Thought Experiment

**SETUP:**
Transferring £100 from Account A to Account B. Two domain objects, two saves.

**WHAT HAPPENS WITHOUT UNIT OF WORK:**

```
accountARepo.save(accountA.debit(100));  // saves debit
// Exception thrown here (server crash, network failure)
accountBRepo.save(accountB.credit(100)); // NEVER REACHED
Result: £100 debited from A, NOT credited to B. Money lost.
```

**WHAT HAPPENS WITH UNIT OF WORK:**

```
unitOfWork.begin();
accountA.debit(100);   // UoW marks A as dirty
accountB.credit(100);  // UoW marks B as dirty
unitOfWork.commit();   // BEGIN TX → UPDATE A → UPDATE B → COMMIT
// If ANYTHING fails between begin() and commit():
// ROLLBACK → both accounts unchanged → money safe
```

**THE INSIGHT:**
The Unit of Work doesn't prevent exceptions - it ensures that when exceptions occur, the system remains in a consistent state. Consistency is the result of making change atomic, not of preventing failures.

---

### 🧠 Mental Model / Analogy

> Think of a batch file operation. When you move 1,000 files from one directory to another, the OS doesn't move one file at a time - it prepares the full operation, then commits it. If the disk runs out of space midway, the OS rolls back to the original state. The move is atomic: all files moved or none moved.

- "Preparing the move list" → Unit of Work tracking changes
- "Executing the move" → committing all changes in one transaction
- "Disk full error" → exception during commit → rollback
- "Original directory unchanged" → database rollback to pre-operation state

Where this analogy breaks down: File systems have different atomicity guarantees than ACID databases. The Unit of Work's atomicity guarantee comes from the database transaction, not from the pattern itself.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
The Unit of Work remembers all the changes you made to your data during one task. When the task is done, it saves everything at once. If anything goes wrong, it undoes all the changes.

**Level 2 - How to use it (junior developer):**
In Spring applications, `@Transactional` is your Unit of Work. JPA's `EntityManager` acts as the Unit of Work - it tracks all entities loaded within a transaction. When the transaction commits, JPA automatically detects changed entities (dirty checking) and generates the necessary SQL. You rarely implement Unit of Work manually; you use your ORM's built-in implementation.

**Level 3 - How it works (mid-level engineer):**
JPA's `EntityManager` implements Unit of Work via dirty checking: when you load an entity, JPA takes a "snapshot" of its state. At commit time, JPA compares the current state to the snapshot - if they differ, the entity is "dirty" and JPA generates an UPDATE statement. New entities (persisted via `em.persist()`) are tracked as "new." Removed entities are tracked as "deleted." The `flush()` operation writes changes to the database (within the transaction) without committing; this is useful for forcing the order of SQL operations.

**Level 4 - Why it was designed this way (senior/staff):**
The explicit Unit of Work pattern (versus the implicit ORM implementation) becomes important in two scenarios: 1) Non-ORM systems (event-sourced, CQRS command side) where you need to coordinate writes to multiple repositories. 2) Distributed transactions where you need to coordinate commits across multiple services or data stores (solved by Saga + Outbox rather than pure Unit of Work). In DDD, the Unit of Work boundary should align with aggregate boundaries - one aggregate's changes per Unit of Work. When a Unit of Work spans multiple aggregates, it's often a sign that the aggregate boundaries are wrong.

---

### ⚙️ How It Works (Mechanism)

**JPA EntityManager as implicit Unit of Work:**

```
@Transactional  ←  begins Unit of Work (opens EntityManager + transaction)
public void transferMoney(AccountId from, AccountId to, Money amount) {
    Account source = accountRepo.findById(from);
    // JPA snapshot: { balance: 1000 }

    Account target = accountRepo.findById(to);
    // JPA snapshot: { balance: 500 }

    source.debit(amount);   // source.balance = 900
    target.credit(amount);  // target.balance = 600

    // NO explicit save needed - JPA dirty checking handles it
}  ← commits Unit of Work:
      JPA detects source is dirty (1000 → 900)
      JPA detects target is dirty (500 → 600)
      BEGIN TX
        UPDATE accounts SET balance=900 WHERE id=?
        UPDATE accounts SET balance=600 WHERE id=?
      COMMIT
```

**Explicit Unit of Work for non-ORM systems:**

```
┌──────────────────────────────────────────────────────────┐
│          EXPLICIT UNIT OF WORK IMPLEMENTATION            │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  IUnitOfWork {                                           │
│    registerNew(DomainObject obj)                         │
│    registerDirty(DomainObject obj)                       │
│    registerDeleted(DomainObject obj)                     │
│    commit() throws ConcurrencyException                  │
│    rollback()                                            │
│  }                                                       │
│                                                          │
│  commit() sequence:                                      │
│    1. BEGIN TRANSACTION                                  │
│    2. INSERT all "new" objects                           │
│    3. UPDATE all "dirty" objects                         │
│    4. DELETE all "deleted" objects                       │
│    5. COMMIT (or ROLLBACK on any failure)                │
└──────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
POST /transfers (TransferMoneyCommand)
  → @Transactional boundary opens (Unit of Work begins)
  → accountRepo.findById(sourceId) → source loaded + tracked
  → accountRepo.findById(targetId) → target loaded + tracked
  → source.debit(amount)  [dirty tracking]
  → target.credit(amount) [dirty tracking]
  → ← YOU ARE HERE (UoW has tracked 2 dirty objects)
  → @Transactional commit (UoW commit):
     UPDATE source, UPDATE target in single transaction
  → HTTP 200 OK
```

**FAILURE PATH:**

```
source.debit(amount) throws InsufficientFundsException
  → @Transactional catches exception
  → Transaction ROLLBACK
  → No database changes written
  → HTTP 422 returned
  → Both accounts unchanged
```

**WHAT CHANGES AT SCALE:**
At scale, long-running units of work cause lock contention - holding a transaction open while performing computation blocks other operations from reading/writing the same rows. The solution: minimise transaction scope to include only the write operations, not the read/computation phase. Read data outside the transaction, compute, open transaction, write, commit.

---

### 💻 Code Example

**Example 1 - Wrong: manual commits without Unit of Work:**

```java
// BAD - two separate transactions, no atomicity
@Service
public class TransferService {
    @Autowired
    private AccountRepository accountRepo;

    // NOT @Transactional - two separate transactions!
    public void transfer(AccountId from,
                         AccountId to, Money amount) {
        Account source = accountRepo.findById(from);
        source.debit(amount);
        accountRepo.save(source);  // Transaction 1 commits

        // If exception here: source debited, target not credited
        Account target = accountRepo.findById(to);
        target.credit(amount);
        accountRepo.save(target);  // Transaction 2 commits
    }
}
```

**Example 2 - Right: single transactional Unit of Work:**

```java
// GOOD - single @Transactional = single Unit of Work
@Service
@RequiredArgsConstructor
public class TransferService {
    private final AccountRepository accountRepo;

    @Transactional  // opens UoW, commits at end of method
    public void transfer(AccountId from,
                         AccountId to, Money amount) {
        Account source = accountRepo.findById(from)
            .orElseThrow(() ->
                new AccountNotFoundException(from));
        Account target = accountRepo.findById(to)
            .orElseThrow(() ->
                new AccountNotFoundException(to));

        source.debit(amount);   // JPA tracks as dirty
        target.credit(amount);  // JPA tracks as dirty
        // No explicit save() needed - JPA dirty checking
        // Both save atomically at @Transactional commit
    }
}
```

**Example 3 - Explicit Unit of Work (non-JPA context):**

```java
// For event-sourced or non-ORM systems
public interface UnitOfWork {
    void registerNew(Object domainObject);
    void registerDirty(Object domainObject);
    void commit();
    void rollback();
}

@Service
@RequiredArgsConstructor
public class TransferService {
    private final UnitOfWork uow;
    private final AccountRepository accountRepo;

    public void transfer(AccountId from,
                         AccountId to, Money amount) {
        Account source = accountRepo.findById(from);
        Account target = accountRepo.findById(to);

        source.debit(amount);
        uow.registerDirty(source);  // explicit tracking

        target.credit(amount);
        uow.registerDirty(target);

        uow.commit();  // atomic write of both accounts
    }
}
```

---

### ⚖️ Comparison Table

| Approach                 | Atomicity               | Dirty tracking         | Scope                     | Best For                                |
| ------------------------ | ----------------------- | ---------------------- | ------------------------- | --------------------------------------- |
| **Unit of Work**         | Full                    | Yes (auto or explicit) | Business operation        | Multi-object transactional writes       |
| Explicit transactions    | Full                    | No (manual save)       | Method level              | Simple single-object writes             |
| Saga Pattern             | Eventual                | No                     | Distributed multi-service | Cross-service coordination              |
| Optimistic Locking alone | No (conflict detection) | No                     | Row level                 | Conflict detection without coordination |

**How to choose:** Use Unit of Work (via `@Transactional` + ORM dirty checking) for most business operations involving multiple domain objects. Use Saga when coordination spans multiple services - Unit of Work cannot span service boundaries.

---

### ⚠️ Common Misconceptions

| Misconception                                           | Reality                                                                                                                            |
| ------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| Unit of Work is the same as a database transaction      | A Unit of Work coordinates domain objects; it uses a database transaction as its underlying mechanism - they're not identical      |
| @Transactional automatically implements Unit of Work    | @Transactional provides the transaction boundary; JPA's EntityManager provides the Unit of Work tracking - they work together      |
| You should always use the largest possible Unit of Work | Long-running Units of Work hold locks and reduce concurrency; scope them to the minimum needed                                     |
| Unit of Work tracks everything in the application       | Each request/business operation has its own Unit of Work; they're not shared across requests                                       |
| Unit of Work prevents all concurrency bugs              | It prevents partial writes; concurrency conflicts (two operations modifying the same object) require Optimistic Locking separately |

---

### 🚨 Failure Modes & Diagnosis

**LazyInitializationException (JPA entity accessed outside Unit of Work)**

**Symptom:** `org.hibernate.LazyInitializationException: failed to lazily initialize a collection - no session`. Occurs when accessing entity relationships after the transaction has closed.

**Root Cause:** Entity loaded within `@Transactional` method; code outside the method boundary accesses a lazy-loaded relationship. JPA session (Unit of Work) is already closed.

**Diagnostic Command / Tool:**

```bash
# Stack trace will show the LazyInitializationException
# Check where the entity relationship is accessed
# relative to where @Transactional method ends
grep -rn "LazyInitializationException" \
  logs/application.log | tail -20
```

**Fix:** Either extend the transaction scope, use `@EntityGraph` to eagerly load the relationship, or fetch the needed data within the transactional boundary and return a DTO.

**Prevention:** Never return JPA entities from `@Transactional` methods that have unloaded lazy relationships. Return DTOs with all needed data already populated.

---

**Transaction too large (holding locks too long)**

**Symptom:** Under load, database deadlocks or timeout exceptions. Slow response times with high database lock wait metrics.

**Root Cause:** `@Transactional` method includes expensive operations (external HTTP calls, file processing) between the first database read and the commit, keeping locks held for the duration.

**Diagnostic Command / Tool:**

```bash
# PostgreSQL: find long-running transactions holding locks
SELECT pid, now() - pg_stat_activity.query_start AS duration,
       query, state, wait_event_type, wait_event
FROM pg_stat_activity
WHERE state != 'idle'
  AND now() - pg_stat_activity.query_start > interval '5 seconds';
```

**Fix:** Move computation outside the transaction. Pattern: read (outside tx) → compute → write (inside tx). Minimise time spent holding write locks.

**Prevention:** `@Transactional` scope should span only the minimum number of reads and writes needed for atomicity. Never include external HTTP calls inside a transaction.

---

**Accidental Unit of Work sharing (thread safety)**

**Symptom:** Data corruption in concurrent requests; changes from one request appear in another; unexpected `OptimisticLockException` at high load.

**Root Cause:** A stateful Unit of Work or EntityManager inadvertently shared between threads - for example, a Spring-managed bean with request-scoped EntityManager used in a multi-threaded executor.

**Diagnostic Command / Tool:**

```bash
# Check JPA entity manager proxy configuration
# Each thread must have its own EntityManager
grep -rn "EntityManager\|@PersistenceContext" \
  src/main/java/ | grep -v test
# Verify no @Singleton beans hold EntityManager
```

**Fix:** Ensure EntityManager is never shared between threads. Spring's `@PersistenceContext` provides thread-local EntityManager automatically.

**Prevention:** Never inject `EntityManager` into singleton beans without using thread-safe proxies. Use Spring's standard DI mechanisms for `EntityManager` injection.

---

### � Transferable Wisdom

**Reusable Engineering Principle:** Buffering changes during an operation and committing them atomically in a single transaction is a general mechanism for ensuring all-or-nothing consistency. This pattern appears wherever a set of related changes must succeed or fail together.

**Where else this pattern appears:**

- **Git staging area:** `git add` buffers changes into the staging area (the Unit of Work); `git commit` atomically writes all staged changes as a single commit - the same deferred, batched write pattern.
- **Shopping cart checkout:** all items are in the cart (buffered); the checkout process attempts to atomically place the order, charge payment, and reduce inventory - a business-level Unit of Work across multiple systems.
- **Database batch inserts:** buffering 1,000 rows and writing in a single `INSERT ... VALUES (...)` batch is more efficient than 1,000 individual inserts - the same deferred-write principle applied for performance rather than consistency.

---

### 💡 The Surprising Truth

The JPA `EntityManager` IS the Unit of Work - and Spring's `@Transactional` annotation creates one automatically. When a developer writes a Spring `@Service` method annotated with `@Transactional`, they are using the Unit of Work pattern without necessarily knowing it. The `EntityManager` tracks every entity it has loaded (the "identity map"), detects changes during dirty checking at commit time, and generates the minimum SQL to persist those changes. The Unit of Work is not an optional pattern in JPA - it is the only way JPA works.

---

### �🔗 Related Keywords

**Prerequisites (understand these first):**

- SAP-021 - Repository Pattern (the Unit of Work coordinates multiple repositories; you must understand repositories before the coordination pattern makes sense)
- SAP-023 - Domain Model (Unit of Work tracks domain object changes; the objects being tracked are domain model entities)

**Builds On This (learn these next):**

- SAP-021 - Repository Pattern (repositories participate in a Unit of Work; understanding both together reveals the full persistence pattern)
- SAP-029 - Data Mapper (the mapping layer that translates between domain objects and database rows, which the Unit of Work coordinates)

**Alternatives / Comparisons:**

- Saga Pattern - eventual consistency across services when Unit of Work scope cannot span multiple services or databases
- Transaction Script - simpler pattern without change tracking; each save is explicit and immediate, no buffering

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Tracks domain changes during an operation │
│              │ and commits them atomically               │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Multi-step writes risk partial commits - │
│ SOLVES       │ inconsistent data on any failure          │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Separate "what changes" (domain phase)    │
│              │ from "writing changes" (commit phase)     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Multiple domain objects must change       │
│              │ atomically in one business operation      │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Cross-service distributed writes -        │
│              │ use Saga for that                         │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Atomicity + dirty tracking vs lock        │
│              │ duration and transaction scope complexity │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Collect all changes; pay once at         │
│              │  the checkout"                            │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Outbox Pattern → Saga Pattern → CQRS     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A business operation transfers money between two accounts in different banks. Each bank has its own database. A classic Unit of Work (single database transaction) cannot span two databases. The operation must still be atomic from the business perspective - either both databases reflect the transfer, or neither does. What mechanism replaces the Unit of Work in this distributed scenario, and what consistency guarantee can it actually provide versus what the Unit of Work guarantees in a single database?

*Hint:* Research the Saga Pattern (also see the CAP theorem and "exactly-once" delivery) - specifically the difference between ACID atomicity (guaranteed by the Unit of Work within a single database) and eventual consistency with compensating transactions (the best guarantee available across distributed databases). Look at the two variants: choreography-based sagas (events trigger compensations) and orchestration-based sagas (a saga orchestrator manages the steps).

**Q2.** In a JPA application with `@Transactional`, a developer loads an `Order` aggregate (with 50 `OrderItem` children), adds one item, and commits. JPA dirty checking compares the current state to the snapshot and generates SQL for the change. As the `Order` aggregate grows to thousands of items over its lifetime, what performance implications does dirty checking at commit time introduce, and how does the Unit of Work's change tracking mechanism turn into a performance bottleneck?

*Hint:* Research JPA/Hibernate dirty checking performance - specifically the O(n) entity comparison at flush time where n is the number of entities in the session. Look at Hibernate's "byte code enhancement" for dirty tracking (comparing only changed fields rather than all fields) and the "stateless session" pattern for bulk operations that bypass the Unit of Work entirely.

**Q3.** A `@Transactional` service method A calls `@Transactional` service method B. What transaction propagation mode determines whether B participates in A's Unit of Work or starts a new one? What are the consequences if B has REQUIRES_NEW propagation and throws an exception - does A's transaction roll back, and does B's commit persist even though A ultimately fails?

*Hint:* Research Spring's `@Transactional(propagation = ...)` modes - specifically REQUIRED (default: joins existing or creates new), REQUIRES_NEW (always creates new, suspends outer), NESTED (savepoint within outer). Look at the specific case of REQUIRES_NEW: B commits before A returns, so B's writes persist even if A subsequently throws. This is the behaviour that the Outbox Pattern was designed to avoid.
