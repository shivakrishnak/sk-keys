---
layout: default
title: "Transaction Propagation"
parent: "Spring Core"
nav_order: 396
permalink: /spring/transaction-propagation/
number: "396"
category: Spring Core
difficulty: ★★★
depends_on: "@Transactional, PlatformTransactionManager"
used_by: "@Transactional, Transaction Isolation Levels, Spring Data JPA"
tags: #advanced, #spring, #database, #deep-dive
---

# 396 — Transaction Propagation

`#advanced` `#spring` `#database` `#deep-dive`

⚡ TL;DR — **Transaction Propagation** defines what Spring does when a `@Transactional` method is called while a transaction may or may not already be active. The default `REQUIRED` joins an existing transaction or creates a new one; `REQUIRES_NEW` always suspends the current and starts fresh; `NESTED` creates a savepoint within the current.

| #396            | Category: Spring Core                                         | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------------ | :-------------- |
| **Depends on:** | @Transactional, PlatformTransactionManager                    |                 |
| **Used by:**    | @Transactional, Transaction Isolation Levels, Spring Data JPA |                 |

---

### 📘 Textbook Definition

**Transaction Propagation** (`org.springframework.transaction.annotation.Propagation`) specifies how a `@Transactional` method participates in an existing transactional context. Spring's `AbstractPlatformTransactionManager.getTransaction()` evaluates the propagation behaviour using the current thread's `TransactionSynchronizationManager` state (whether a transaction is bound to the thread). The seven propagation types are: **REQUIRED** (default — join if exists, create if not), **REQUIRES_NEW** (always suspend current and create new independent transaction), **SUPPORTS** (join if exists, execute non-transactionally if not), **NOT_SUPPORTED** (always suspend current and execute non-transactionally), **MANDATORY** (must join existing, throw if none), **NEVER** (must NOT have existing transaction, throw if one exists), and **NESTED** (create a savepoint within current transaction — partial rollback possible; falls back to `REQUIRES_NEW` if no savepoint support). `REQUIRES_NEW` creates a genuinely independent transaction that commits/rolls back independently; `NESTED` is within the outer transaction — the outer rolling back also rolls back the nested.

---

### 🟢 Simple Definition (Easy)

Transaction Propagation answers: "when my `@Transactional` method is called, should I join the caller's transaction or start my own?" The default is: "join if there is one, otherwise start new."

---

### 🔵 Simple Definition (Elaborated)

Imagine a bank transfer: `transferService.transfer()` is `@Transactional`. It calls `auditService.logAudit()` which is also `@Transactional`. What should `logAudit()` do with the existing transaction? The answer depends on the business requirement. If audit logging should be rolled back if the transfer fails — use default `REQUIRED` (join the transfer's transaction). If audit logging must be committed even if the transfer fails (you always want to record the attempt) — use `REQUIRES_NEW` (suspend the transfer's transaction, run audit in a separate transaction, commit it independently). Transaction propagation is the mechanism that controls this choice.

---

### 🔩 First Principles Explanation

**All seven propagation types with transaction state diagram:**

```
CALLER STATE:  [Has T1]  or  [No Transaction]

REQUIRED (default):
  Has T1   → JOIN T1 (same connection, same transaction)
  No txn   → CREATE new T1
  Result: "always in a transaction"

REQUIRES_NEW:
  Has T1   → SUSPEND T1, CREATE T2 (independent connection!)
           → T2 commits/rolls back independently of T1
           → After method: RESUME T1
  No txn   → CREATE new T1
  Result: "always in a fresh, isolated transaction"

SUPPORTS:
  Has T1   → JOIN T1
  No txn   → run WITHOUT transaction (non-transactional)
  Result: "transactional if there is one, but OK without"

NOT_SUPPORTED:
  Has T1   → SUSPEND T1, run without transaction
  No txn   → run without transaction
  Result: "never in a transaction"

MANDATORY:
  Has T1   → JOIN T1
  No txn   → throw IllegalTransactionStateException
  Result: "must be called within existing transaction"

NEVER:
  Has T1   → throw IllegalTransactionStateException
  No txn   → run without transaction
  Result: "must NOT be in a transaction"

NESTED:
  Has T1   → CREATE SAVEPOINT within T1
           → On rollback: rollback to savepoint (T1 continues)
           → On commit: savepoint released (T1 continues)
           → T1 rolling back: nested rolls back too
  No txn   → CREATE new T1 (like REQUIRED)
  Result: "partial rollback within outer transaction"
```

**REQUIRED vs REQUIRES_NEW rollback behaviour:**

```java
@Service class OrderService {
    @Autowired AuditService auditService;
    @Autowired OrderRepository orderRepo;

    @Transactional  // T1 begins
    public void createOrder(OrderRequest req) {
        orderRepo.save(new Order(req));  // INSERT in T1

        // Case 1: REQUIRED propagation
        auditService.logAttempt(req);    // joins T1
        // If logAttempt throws: T1 rolls back → ORDER INSERT rolled back too
        // If createOrder throws: T1 rolls back → audit entry rolled back too

        // Case 2: REQUIRES_NEW propagation
        auditService.logAttempt(req);    // T1 suspended, T2 begins
        // T2 commits the audit entry independently
        // T1 resumes after auditService.logAttempt() returns
        // If createOrder then throws: T1 rolls back → ORDER rolled back
        // BUT audit entry from T2 is ALREADY COMMITTED → remains in DB!
    }
}

@Service class AuditService {
    @Autowired AuditRepository auditRepo;

    // Change this to switch between REQUIRED (default) and REQUIRES_NEW:
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void logAttempt(OrderRequest req) {
        auditRepo.save(new AuditEntry(req, LocalDateTime.now()));
    }
}
```

**NESTED vs REQUIRES_NEW — key difference:**

```java
@Transactional           // T1 begins
public void processOrder(Order order) {
    orderRepo.save(order); // step 1 in T1

    try {
        // REQUIRES_NEW: genuinely separate transaction
        // → commit is independent. T1 rolling back does NOT roll this back
        notificationService.sendEmail(order);

        // NESTED: savepoint within T1
        // → if sendEmail fails: rollback to savepoint, T1 continues
        // → if T1 rolls back: nested work rolls back too (it's within T1)
        notificationService.sendEmail(order);
    } catch (Exception e) {
        log.warn("Notification failed, continuing..."); // catch the nested rollback
    }

    inventoryService.reserve(order); // step 2 in T1 — still runs
    // T1 commits: step 1 + step 2 committed; sendEmail (NESTED) committed too
}
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Transaction Propagation:

What breaks without it:

1. No way to have a method participate in an outer transaction OR start its own — it is all-or-nothing.
2. Audit logging and error logging that must survive a rollback cannot be expressed declaratively.
3. Nested operations with partial rollback require explicit savepoint management in application code.
4. Helper services cannot declare "I work transactionally only if the caller is transactional" (`SUPPORTS`).

WITH Transaction Propagation:
→ `@Transactional(propagation = REQUIRES_NEW)` for audit/notification services guarantees they commit independently.
→ `MANDATORY` enforces invariants: "this method must be called within a transaction."
→ `NESTED` allows try-catch over partial operations without aborting the outer transaction.

---

### 🧠 Mental Model / Analogy

> Think of transactions as rooms with locked doors. A transaction is a room where all your work happens — when you commit, the door opens and everyone can see your work. `REQUIRED`: if the caller already has a room, you enter their room. If not, you open your own room. `REQUIRES_NEW`: regardless, you get your own separate room — the caller's room is temporarily locked while you work. When you finish, your room is committed and the caller's room is resumed. `NESTED`: you work inside a corner of the caller's room marked with tape (savepoint). If your corner work fails, only the tape-marked area is cleaned up — the rest of the room is fine. If the whole room is abandoned (outer rollback), your corner work is lost too.

"Room" = database transaction (Connection with open transaction)
"Enter their room" = REQUIRED joining existing transaction
"Your own separate room" = REQUIRES_NEW (independent commit/rollback)
"Corner with tape" = NESTED (savepoint — partial rollback within outer)
"Whole room abandoned" = outer transaction rollback

---

### ⚙️ How It Works (Mechanism)

**Transaction suspension in REQUIRES_NEW:**

```java
// AbstractPlatformTransactionManager (simplified):

TransactionStatus status = txManager.getTransaction(definition);
// If REQUIRES_NEW and existing transaction:
//   1. suspend(existingTransaction) — saves current Connection to SuspendedResources
//   2. TransactionSynchronizationManager.unbindResource(dataSource)
//   3. Opens NEW Connection from pool
//   4. Binds NEW Connection to TransactionSynchronizationManager
//   → inner transaction is now using a DIFFERENT Connection from the outer

// When inner transaction completes:
//   1. commit/rollback the inner Connection
//   2. resume(suspendedResources) — restores the outer Connection
//   3. TransactionSynchronizationManager rebinds the outer Connection
```

---

### 🔄 How It Connects (Mini-Map)

```
@Transactional  →  propagation attribute
                            │
                            ▼
Transaction Propagation  ◄──── (you are here)
(controls join vs new vs suspend vs nested)
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
    REQUIRED            REQUIRES_NEW          NESTED
  (join or create)    (always new,        (savepoint within
                       independent)         outer txn)
                            │
                            ▼
                PlatformTransactionManager
                (JpaTransactionManager, etc.)
```

---

### 💻 Code Example

**Practical: audit logging that survives outer rollback**

```java
@Service
class OrderService {
    @Autowired private OrderRepository orderRepo;
    @Autowired private AuditService auditService;

    @Transactional
    public Order createOrder(CreateOrderCommand cmd) {
        // 1. Save order in T1 (outer transaction)
        Order order = orderRepo.save(Order.from(cmd));

        // 2. Log the attempt — REQUIRES_NEW commits independently
        auditService.logOrderAttempt(cmd.getCustomerId(), order.getId(), "PROCESSING");

        // 3. Business validation that might fail
        if (inventoryShortage(order)) {
            auditService.logOrderAttempt(cmd.getCustomerId(), order.getId(), "FAILED");
            throw new InsufficientInventoryException(order);
            // T1 rolls back: order INSERT is undone
            // Audit entries from REQUIRES_NEW are ALREADY COMMITTED → preserved
        }

        auditService.logOrderAttempt(cmd.getCustomerId(), order.getId(), "COMPLETED");
        return order; // T1 commits: order INSERT persists
    }
}

@Service
class AuditService {
    @Autowired private AuditRepository auditRepo;

    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void logOrderAttempt(Long customerId, Long orderId, String status) {
        AuditEntry entry = AuditEntry.builder()
            .customerId(customerId)
            .orderId(orderId)
            .status(status)
            .timestamp(Instant.now())
            .build();
        auditRepo.save(entry); // Always committed — independent of outer transaction
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                                       | Reality                                                                                                                                                                                                                                                                       |
| ------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `REQUIRES_NEW` rolls back when the outer transaction rolls back     | `REQUIRES_NEW` creates a genuinely independent transaction. It commits at the end of the inner method, BEFORE the outer transaction completes. The outer rolling back does NOT affect the already-committed inner transaction                                                 |
| `NESTED` and `REQUIRES_NEW` are the same                            | `NESTED` uses JDBC savepoints — it is WITHIN the outer transaction. If the outer rolls back, the nested work rolls back too. `REQUIRES_NEW` is a completely independent transaction — outer rollback does not affect it. Not all databases/drivers support savepoints         |
| The default propagation `REQUIRED` always creates a new transaction | `REQUIRED` creates a new transaction only if there is no active transaction on the current thread. If a transaction exists, it joins it — using the SAME Connection. Most repository methods within a service `@Transactional` method use the same Connection for this reason |
| `SUPPORTS` is the same as no `@Transactional`                       | `SUPPORTS` joins an existing transaction if one exists (participates in transactional behaviour). A method with no `@Transactional` annotation is entirely unaware of Spring transaction management                                                                           |

---

### 🔥 Pitfalls in Production

**REQUIRES_NEW + same database deadlock**

```java
@Transactional       // T1 holds lock on orders row
public void updateOrder(Long orderId, ...) {
    Order o = orderRepo.findByIdWithLock(orderId); // SELECT FOR UPDATE in T1

    auditService.logUpdate(orderId); // REQUIRES_NEW → T2 starts on new Connection
    // T2 tries: INSERT audit_entries (orderId FK) → may need shared lock on orders
    // But T1 (same thread) holds exclusive lock!
    // T2 waits for T1... T1 is waiting for T2 (its child) to complete
    // DEADLOCK → database timeout after N seconds
}

// RISK: REQUIRES_NEW opening a new Connection while the outer transaction
// holds row locks that the inner transaction also needs → deadlock.
// Always check for lock contention when using REQUIRES_NEW on related tables.
```

---

### 🔗 Related Keywords

- `@Transactional` — declares propagation as an attribute; propagation logic is invoked by `TransactionInterceptor`
- `Transaction Isolation Levels` — a separate `@Transactional` attribute controlling concurrent read/write visibility
- `Spring Data JPA` — Spring Data repository methods default to `REQUIRED` propagation on write operations

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ PROPAGATION    │ HAS TX         │ NO TX                  │
├────────────────┼────────────────┼────────────────────────┤
│ REQUIRED       │ Join existing  │ Create new             │
│ REQUIRES_NEW   │ Suspend, new   │ Create new             │
│ SUPPORTS       │ Join existing  │ No transaction         │
│ NOT_SUPPORTED  │ Suspend, no tx │ No transaction         │
│ MANDATORY      │ Join existing  │ Exception!             │
│ NEVER          │ Exception!     │ No transaction         │
│ NESTED         │ Savepoint      │ Create new             │
├────────────────┴────────────────────────────────────────┤
│ KEY DIFF: REQUIRES_NEW commits independently             │
│           NESTED shares outer lifecycle (savepoint)     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** `REQUIRES_NEW` suspends the outer transaction by unbinding the outer Connection from `TransactionSynchronizationManager` and opening a new Connection. In a connection pool of size 10 and 10 concurrent requests, each `@Transactional` method calling a `REQUIRES_NEW` inner method, how many connections does this require? Show the calculation for the worst case and explain the connection starvation scenario where the outer transaction is holding a connection and the pool is exhausted waiting for a new connection for `REQUIRES_NEW` — resulting in a deadlock at the pool level (not the database level). What is the pool size recommendation?

**Q2.** `NESTED` propagation uses JDBC savepoints (`Connection.setSavepoint()`). Not all databases/connection pools support savepoints. Describe: (a) what Spring does if `NESTED` is requested but savepoints are not supported (hint: it falls back to `REQUIRES_NEW` behaviour by default, configurable via `AbstractPlatformTransactionManager.setNestedTransactionAllowed()`), (b) what the NESTED semantics are at the database level for PostgreSQL vs MySQL InnoDB — do both support savepoints? (c) what happens to the savepoint at the end of the NESTED method — is it released or maintained until the outer commits?
