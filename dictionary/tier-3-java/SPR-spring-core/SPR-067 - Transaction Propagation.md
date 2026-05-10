---
version: 2
layout: default
title: "Transaction Propagation"
parent: "Spring Core"
grand_parent: "Technical Dictionary"
nav_order: 67
permalink: /spring/transaction-propagation/
id: SPR-085
category: Spring Core
difficulty: ★★★
depends_on: "@Transactional, AOP, Bean"
used_by: Spring Services, Spring Data JPA, JTA
related: "@Transactional, Transaction Isolation Levels, REQUIRES_NEW, NESTED"
tags:
  - spring
  - springboot
  - advanced
  - pattern
  - transactions
---

# SPR-067 - Transaction Propagation

⚡ TL;DR - Transaction propagation defines what happens when a `@Transactional` method is called while a transaction may (or may not) already be active - the 7 propagation levels control whether the call joins, creates, suspends, or forbids a transaction.

| #396            | Category: Spring Core                                              | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------------------------- | :-------------- |
| **Depends on:** | @Transactional, AOP, Bean                                          |                 |
| **Used by:**    | Spring Services, Spring Data JPA, JTA                              |                 |
| **Related:**    | @Transactional, Transaction Isolation Levels, REQUIRES_NEW, NESTED |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Service A calls Service B. Service A started a transaction. Does Service B use Service A's transaction, or start its own? If they use the same transaction, a rollback in B rolls back A's work too - sometimes desired, sometimes disastrous. If B starts its own, B can commit independently - sometimes right, sometimes leaving A's transaction in an inconsistent state. Without a propagation mechanism, you must manually pass `TransactionStatus` objects between methods, coordinate commits/rollbacks explicitly, and handle suspension/resumption of transactions by hand.

**THE INVENTION MOMENT:**
"Propagation is the contract between two @Transactional methods about how their transactions relate."

---

### 📘 Textbook Definition

**Transaction propagation** (`org.springframework.transaction.annotation.Propagation`) is an attribute of `@Transactional` that specifies the behavior when a transactional method is called in the context of an existing (or absent) transaction. Spring's `PlatformTransactionManager` evaluates the current thread's `TransactionSynchronizationManager` state and the requested propagation level to determine whether to: (1) join the existing transaction, (2) create a new transaction (optionally suspending the existing one), (3) execute without a transaction (optionally suspending the existing one), or (4) throw an exception if the transactional context is not as expected. The 7 propagation levels are: `REQUIRED`, `REQUIRES_NEW`, `SUPPORTS`, `NOT_SUPPORTED`, `MANDATORY`, `NEVER`, `NESTED`.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Propagation = what a @Transactional method does when there's already a transaction running.

**One analogy:**

> REQUIRED is like riding a bus: "Is there a bus running? I'll jump on. No bus? I'll start one." REQUIRES_NEW is like ordering a private taxi: "Whether or not a bus is running, I'm taking my own taxi - and the bus waits." SUPPORTS is like walking or bussing: "Bus running? I'll take it. No bus? I'll walk." MANDATORY is like a subway turnstile: "Already have a ticket (transaction)? Come through. No ticket? You're blocked."

**One insight:**
`REQUIRES_NEW` suspends the outer transaction - commits independently even if the outer rolls back. This is essential for audit logging (you want to log the failure even when the business transaction fails).

---

### 🔩 First Principles Explanation

**DECISION MATRIX:**

| Propagation     | Existing TX present                      | No existing TX                           |
| --------------- | ---------------------------------------- | ---------------------------------------- |
| `REQUIRED`      | Join it                                  | Create new                               |
| `REQUIRES_NEW`  | Suspend existing, create new             | Create new                               |
| `SUPPORTS`      | Join it                                  | Run without TX                           |
| `NOT_SUPPORTED` | Suspend existing, run without TX         | Run without TX                           |
| `MANDATORY`     | Join it                                  | Throw `IllegalTransactionStateException` |
| `NEVER`         | Throw `IllegalTransactionStateException` | Run without TX                           |
| `NESTED`        | Create savepoint within existing         | Create new (like REQUIRED)               |

**THE THREAD-LOCAL STATE:**
Spring stores the current transaction in `TransactionSynchronizationManager` (backed by `ThreadLocal`). Before starting a `REQUIRES_NEW` transaction, Spring saves the current `ConnectionHolder` and `EntityManagerHolder`, then unbinds them from the thread - effectively "suspending" the outer transaction. When the inner transaction completes, the outer is restored.

---

### 🧪 Thought Experiment

**SETUP:**
`OrderService.placeOrder()` [REQUIRED] calls `AuditService.logAction()` [REQUIRES_NEW].

**SCENARIO 1 - Inner method throws:**

```
placeOrder() begins TX_1
    → logAction() begins TX_2 (suspends TX_1)
    → logAction() throws RuntimeException → ROLLBACK TX_2
    → TX_1 resumed
    → placeOrder() sees exception, handle it
    → TX_1 commits or rolls back based on placeOrder's logic
```

TX_2 rolled back. TX_1 can still commit. Audit entry lost.

**SCENARIO 2 - Outer method throws:**

```
placeOrder() begins TX_1
    → logAction() begins TX_2 (suspends TX_1)
    → logAction() completes → COMMIT TX_2 (audit entry saved!)
    → TX_1 resumed
    → placeOrder() throws RuntimeException → ROLLBACK TX_1
    → Order rolled back. But audit entry is COMMITTED independently.
```

TX_1 rolled back. TX_2 already committed. CORRECT - you WANT to see the audit entry even when the order fails.

**THE INSIGHT:**
REQUIRES_NEW for audit logging is the canonical pattern - audit records must survive a business transaction failure. Without REQUIRES_NEW, a rollback of the business transaction would also delete the audit log entry.

---

### 🧠 Mental Model / Analogy

> Think of transactions as physical boxes in a warehouse. REQUIRED says "put all items in the current box - if there's no box, get a new one." REQUIRES_NEW says "set the current box aside and get a completely new box - seal and ship it regardless of what happens to the other box." SUPPORTS says "if there's an open box, put items in it - if not, just hand the items directly to the customer without boxing." MANDATORY says "there must be an open box or I refuse to work." NESTED creates a "box within a box" - you can undo only the inner box without touching the outer box (savepoints).

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
When one Spring service method calls another, propagation decides: "Do they share the same database transaction, or does the called method get its own transaction?" The most common answer is REQUIRED (share), and the most important alternative is REQUIRES_NEW (own separate transaction).

**Level 2 - How to use it (junior developer):**

- Default is `REQUIRED` - most methods should use this.
- Use `REQUIRES_NEW` for audit logging, notification recording, and any operation that must commit independently of the caller.
- Use `MANDATORY` for internal helpers that should only be called from within a transaction - it acts as a safety assertion.
- Use `NOT_SUPPORTED` for operations that should never run in a transaction (e.g., sending an HTTP request - you don't want to hold a DB connection open during an HTTP call).

**Level 3 - How it works (mid-level engineer):**
`AbstractPlatformTransactionManager.getTransaction()` implements the propagation logic. For `REQUIRED`: calls `isExistingTransaction()`; if true, calls `handleExistingTransaction()` which may join it. For `REQUIRES_NEW`: calls `suspend(existingTransaction)` which unbinds all resources from `TransactionSynchronizationManager` and saves them in a `SuspendedResourcesHolder`. After the inner transaction completes, `resume(suspendedResources)` rebinds them. For `NESTED`: Spring calls `connection.setSavepoint()` - requires the underlying JDBC driver to support savepoints. On inner rollback, `connection.rollback(savepoint)` is called without affecting the outer transaction.

**Level 4 - Why it was designed this way (senior/staff):**
The 7 propagation levels map to the EJB transaction model (Spring's original propagation design was influenced by EJB's container-managed transactions). `NESTED` is the most sophisticated - it uses JDBC savepoints to enable partial rollback without full transaction nesting (which would require two separate database connections). `REQUIRES_NEW` truly suspends the outer transaction and uses a different database connection for the inner transaction - this means two DB connections are open simultaneously, which can cause connection pool exhaustion if nested too deeply. The `NESTED` vs `REQUIRES_NEW` distinction is subtle but critical: `NESTED` commits/rolls back together with the outer transaction (it just allows partial rollback), while `REQUIRES_NEW` commits/rolls back completely independently.

---

### ⚙️ How It Works (Mechanism)

**REQUIRED - join existing:**

```
Thread: [TX_1 active in ThreadLocal]

Service B called with REQUIRED:
    isExistingTransaction? YES
    → participate in TX_1
    → service B runs within TX_1's connection
    → no new transaction started
    → if B throws RuntimeException:
        TX_1 is marked "rollback-only"
        (B's exception propagates to A)
        When A's proxy tries to commit:
        → "Transaction marked for rollback-only" → ROLLBACK TX_1
```

**REQUIRES_NEW - suspend and create:**

```
Thread: [TX_1 active in ThreadLocal]

Service C called with REQUIRES_NEW:
    suspend(TX_1):
        Remove TX_1's ConnectionHolder from ThreadLocal
        Save in SuspendedResourcesHolder

    Create TX_2:
        New DB connection obtained from pool
        TX_2 bound to ThreadLocal

    Service C runs within TX_2

    If C returns normally:
        COMMIT TX_2
        close TX_2's connection
    If C throws:
        ROLLBACK TX_2

    resume(TX_1):
        TX_1's ConnectionHolder restored to ThreadLocal

Thread continues with TX_1
```

---

### 🔄 The Complete Picture - End-to-End Flow

**E-commerce order flow with multiple propagation levels:**

```
HTTP POST /orders → OrderController.placeOrder()
    ↓
OrderService.placeOrder()  [REQUIRED]
    TX_1 begins
    ↓
    inventoryService.reserve()  [REQUIRED]
        Joins TX_1 (no new TX)
        ↓
        Updates inventory (same TX_1)
    ↓
    paymentService.charge()  [REQUIRED]
        Joins TX_1
        ↓
        Records payment (same TX_1)
    ↓
    auditService.logOrder()  [REQUIRES_NEW]
        TX_1 suspended
        TX_2 begins (new DB connection)
        ↓
        Writes audit record (TX_2)
        ↓
        COMMIT TX_2 (audit always saved!)
        TX_1 resumed
    ↓
    notificationService.sendEmail()  [NOT_SUPPORTED]
        TX_1 suspended
        No transaction for HTTP call to email service
        ↓
        HTTP call made (no DB connection held)
        TX_1 resumed
    ↓
COMMIT TX_1 (order, inventory, payment all committed)
    ↓
HTTP 201 Created
```

---

### 💻 Code Example

**Example 1 - The audit logging pattern (REQUIRES_NEW):**

```java
@Service
public class OrderService {

    @Autowired private AuditService auditService;
    @Autowired private OrderRepository orderRepo;

    @Transactional  // REQUIRED (default)
    public Order placeOrder(OrderRequest req) {
        Order order = orderRepo.save(new Order(req));
        auditService.logAction("ORDER_CREATED", order.getId());  // REQUIRES_NEW
        // If auditService fails, its TX rolls back but THIS TX continues
        return order;
    }
}

@Service
public class AuditService {

    @Autowired private AuditRepository auditRepo;

    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void logAction(String action, Long entityId) {
        // Runs in its own independent transaction
        // Committed even if the outer transaction rolls back
        // Rolled back if THIS method throws - but outer is unaffected
        auditRepo.save(new AuditLog(action, entityId));
    }
}
```

**Example 2 - MANDATORY for internal assertion:**

```java
@Service
public class InternalTransactionHelper {

    // This method MUST be called from within a transaction
    // It acts as a safety assertion at the code level
    @Transactional(propagation = Propagation.MANDATORY)
    public void doSomethingThatRequiresTransaction() {
        // If called without active transaction: throws IllegalTransactionStateException
        // This is a bug in the calling code - fail fast
        repo.performCriticalUpdate();
    }
}
```

**Example 3 - NOT_SUPPORTED for external HTTP calls:**

```java
@Service
public class NotificationService {

    // Suspend any active transaction during HTTP call
    // Avoids holding a DB connection while waiting for HTTP response
    @Transactional(propagation = Propagation.NOT_SUPPORTED)
    public void sendEmailViaHttpApi(String to, String body) {
        httpClient.post("https://api.email.com/send", new EmailPayload(to, body));
        // No DB connection held during HTTP call
        // If this method is called from a @Transactional method,
        // the outer transaction is suspended and resumed after
    }
}
```

**Example 4 - NESTED for partial rollback:**

```java
@Transactional
public void importUsers(List<UserDto> users) {
    for (UserDto dto : users) {
        try {
            importSingleUser(dto);  // NESTED - savepoint per user
        } catch (Exception e) {
            log.warn("Failed to import user {}: {}", dto.getEmail(), e.getMessage());
            // Inner rollback to savepoint - this user's changes undone
            // BUT outer transaction continues for remaining users
        }
    }
    // Commits all successfully imported users
}

@Transactional(propagation = Propagation.NESTED)
public void importSingleUser(UserDto dto) {
    userRepo.save(dto.toUser());
    addressRepo.save(dto.toAddress());
    // If this throws: rolls back to savepoint, outer transaction unaffected
}
```

---

### ⚖️ Comparison Table

|                       | REQUIRED                  | REQUIRES_NEW       | NESTED                  | NOT_SUPPORTED       |
| --------------------- | ------------------------- | ------------------ | ----------------------- | ------------------- |
| Existing TX           | Join                      | Suspend + New      | Savepoint               | Suspend             |
| No existing TX        | Create new                | Create new         | Create new              | None                |
| Independent commit    | No (part of outer)        | YES                | No (commits with outer) | N/A                 |
| Independent rollback  | Marks outer rollback-only | YES                | YES (savepoint only)    | N/A                 |
| Use case              | Standard                  | Audit, logging     | Batch partial rollback  | External HTTP calls |
| DB connections needed | 1                         | 2 (simultaneously) | 1                       | 1 then 0            |

---

### ⚠️ Common Misconceptions

| Misconception                                     | Reality                                                                                                                                 |
| ------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| REQUIRES_NEW and NESTED both commit independently | NESTED does NOT commit independently - it commits with the outer transaction. NESTED only allows ROLLBACK independently (to savepoint). |
| REQUIRED always creates a new transaction         | REQUIRED JOINS an existing transaction. Only creates new if none exists.                                                                |
| Propagation works within same class               | Self-invocation (`this.method()`) bypasses the proxy - propagation is never evaluated.                                                  |
| REQUIRES_NEW is free                              | REQUIRES_NEW requires a second DB connection from the pool simultaneously. Overuse can exhaust the connection pool.                     |

---

### 🚨 Failure Modes & Diagnosis

**Outer transaction silently rolled back after inner REQUIRED exception was caught**

**Symptom:** `OrderService.placeOrder()` catches an exception from `inventoryService.reserve()` and thinks the order was saved. But a `UnexpectedRollbackException` is thrown at the commit of `placeOrder()`.

**Root Cause:** `reserve()` threw a `RuntimeException` which triggered rollback - even though the exception was caught by `placeOrder()`. Because `reserve()` joined the outer transaction (`REQUIRED`), the outer transaction was marked **rollback-only**. When `placeOrder()`'s proxy tries to commit, it finds `rollback-only` and throws `UnexpectedRollbackException`.

**Fix:**

```java
// Option 1: Let reserve() propagate the exception (don't catch it)
// Option 2: Use REQUIRES_NEW for reserve() if it should be independent
// Option 3: Understand that in REQUIRED, inner exception = outer tx marked rollback-only
@Transactional(propagation = Propagation.REQUIRES_NEW)
public void reserve(List<Item> items) { ... }  // Now independent tx
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `@Transactional` - the annotation that accepts the propagation attribute

**Builds On This (learn these next):**

- `Transaction Isolation Levels` - the `isolation` attribute works independently of propagation
- `N+1 Problem` - appears within REQUIRED transactions that load lazy collections in loops

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ REQUIRED       │ Join existing or create new (default)   │
│ REQUIRES_NEW   │ Suspend existing, create own, commit    │
│                │ independently (audit logs!)             │
│ SUPPORTS       │ Join if exists, else no-tx              │
│ NOT_SUPPORTED  │ Suspend existing, run no-tx (HTTP calls)│
│ MANDATORY      │ Must join existing, throw if none       │
│ NEVER          │ Must have no TX, throw if one exists    │
│ NESTED         │ Savepoint in existing (partial rollback)│
├────────────────┼─────────────────────────────────────────┤
│ KEY INSIGHT    │ REQUIRES_NEW = 2 DB connections. NESTED │
│                │ = 1 connection + savepoint.             │
│ CRITICAL TRAP  │ REQUIRED inner exception → outer TX     │
│                │ marked rollback-only even if caught!    │
└────────────────┴─────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** `REQUIRES_NEW` requires a second database connection from the pool while the first connection (outer transaction) is suspended. If a service method calls another `REQUIRES_NEW` method 100 times in a loop (e.g., saving 100 audit entries one by one), what happens to the connection pool? How would you design the audit logging service to avoid this problem while still maintaining independent transaction behavior?

**Q2.** When a NESTED transaction rolls back to its savepoint, the outer transaction continues and eventually commits. What happens to database-side effects that the NESTED transaction caused BEFORE it rolled back? For example, if the nested call inserted a row, then threw an exception, and the outer transaction commits - is that row present or absent in the final committed state?
