---
layout: default
title: "Transaction Propagation"
parent: "Spring Core"
nav_order: 396
permalink: /spring/transaction-propagation/
number: "396"
category: Spring Core
difficulty: ★★★
depends_on: "@Transactional, Spring AOP, JPA, PlatformTransactionManager"
used_by: "Service layering, audit logging, batch processing, retry patterns"
tags: #java, #spring, #database, #advanced, #deep-dive
---

# 396 — Transaction Propagation

`#java` `#spring` `#database` `#advanced` `#deep-dive`

⚡ TL;DR — Controls what happens when a `@Transactional` method is called while a transaction already exists — whether to join it, suspend it, reject it, or always start a new one.

| #396 | category: Spring Core
|:---|:---|:---|
| **Depends on:** | @Transactional, Spring AOP, JPA, PlatformTransactionManager | |
| **Used by:** | Service layering, audit logging, batch processing, retry patterns | |

---

### 📘 Textbook Definition

**Transaction Propagation** defines the transactional behaviour when a `@Transactional` method is called while a transaction is already active on the current thread. Spring's `Propagation` enum has seven values: `REQUIRED` (join existing or create new — default), `REQUIRES_NEW` (always create new, suspend existing), `SUPPORTS` (join if exists, run non-transactionally if not), `NOT_SUPPORTED` (suspend existing, run non-transactionally), `MANDATORY` (fail if no active transaction), `NEVER` (fail if active transaction exists), and `NESTED` (create a savepoint within existing transaction). `PlatformTransactionManager` implements propagation by maintaining the active transaction status in `TransactionSynchronizationManager`'s `ThreadLocal` binding.

---

### 🟢 Simple Definition (Easy)

Propagation answers the question: "When this transactional method is called, what does it do with the transaction that's already running?" Does it join, start its own, ignore it, or refuse to run?

---

### 🔵 Simple Definition (Elaborated)

Most methods use `REQUIRED` (the default) — they join the caller's transaction if one exists, or start a new one if not. This means all service operations in the same call stack share one transaction and commit or roll back together. `REQUIRES_NEW` breaks this: it suspends the outer transaction, opens a fresh one on a new DB connection, commits independently, and then resumes the outer transaction. This is essential for audit logging — you want the audit record written even if the outer transaction rolls back.

---

### 🔩 First Principles Explanation

**The propagation decision tree:**

```
Method B is called (annotated @Transactional(propagation=X))
Is there an active transaction on the ThreadLocal?

  YES active TX       NO active TX
  ──────────          ──────────
  REQUIRED  → join    REQUIRED  → create new
  REQUIRES_NEW→suspend REQUIRES_NEW→create new
              create new
  SUPPORTS  → join    SUPPORTS  → no transaction
  NOT_SUPPORTED→suspend NOT_SUPPORTED→no transaction
              run non-TX
  MANDATORY → proceed  MANDATORY → throw exception
  NEVER     → throw    NEVER     → proceed non-TX
  NESTED    → savepoint NESTED   → create new TX
```

**Why REQUIRES_NEW uses a new DB connection:**

```
ThreadLocal can only hold one active connection per thread.
REQUIRES_NEW SUSPENDS the outer transaction (saves it aside)
and creates a NEW transaction on a NEW connection.

ThreadLocal state during REQUIRES_NEW inner method:
  [outer TX suspended: conn1, TX1]
  [active TX: conn2, TX2]         ← inner method sees this

After inner method returns:
  [restored: conn1, TX1]          ← outer TX resumes
  conn2 released back to pool
```

---

### ❓ Why Does This Exist (Why Before What)

**Real-world scenarios each propagation handles:**

```
REQUIRED (default):
  Service A calls Service B — one transaction
  If B fails, A's work also rolls back (correct)

REQUIRES_NEW:
  Audit log MUST be written even if outer TX fails
  Batch processing: each item in its own transaction
  → outer rollback does NOT affect audit write

SUPPORTS:
  Helper that works with OR without a transaction
  (read-only query — doesn't care either way)

NOT_SUPPORTED:
  Expensive non-transactional operation
  (sending email, calling remote API)
  → holding DB connection during email send = waste

MANDATORY:
  Internal helper that REQUIRES caller started a TX
  → Enforce API contract: "only call me in a TX"

NESTED:
  Try something risky; if it fails, rollback to
  savepoint (not entire outer TX) and continue
```

---

### 🧠 Mental Model / Analogy

> Transaction propagation is like **billing policies between departments** in a company. REQUIRED: you use the same company credit card as your manager (join the outer transaction). REQUIRES_NEW: you open your own personal card for this purchase, pay it off immediately regardless of what your manager does. SUPPORTS: you'll use the card if there is one, else pay cash. MANDATORY: refuse to buy anything unless you're given a card first.

"Company credit card" = the active transaction
"Using same card as manager" = REQUIRED — join existing
"Opening your own personal card" = REQUIRES_NEW — new TX
"Using card if offered, else cash" = SUPPORTS
"Refusing without a card" = MANDATORY — throw if no TX
"Paying separately regardless of dept budget" = REQUIRES_NEW commits independently

---

### ⚙️ How It Works (Mechanism)

**All seven propagation types:**

```java
// REQUIRED (DEFAULT) — join or create
@Transactional(propagation = Propagation.REQUIRED)
void methodA() {
  // If called alone: new TX opened
  // If called from within TX: joins it
}

// REQUIRES_NEW — always fresh TX
@Transactional(propagation = Propagation.REQUIRES_NEW)
void auditLog(String event) {
  auditRepo.save(new AuditEntry(event));
  // Commits immediately, independently of outer TX
  // Even if outer TX rolls back, this audit entry persists
}

// SUPPORTS — optional TX
@Transactional(propagation = Propagation.SUPPORTS)
List<Order> findOrders(String status) {
  return orderRepo.findByStatus(status);
  // Works in or out of transaction — reads either way
}

// NOT_SUPPORTED — suspend TX for this call
@Transactional(propagation = Propagation.NOT_SUPPORTED)
void sendEmail(String to, String body) {
  emailClient.send(to, body);
  // DB connection NOT held during SMTP operation
}

// MANDATORY — caller must have an active TX
@Transactional(propagation = Propagation.MANDATORY)
void internalHelper() {
  // Use this for internal methods that are not
  // safe to call without a managing transaction
}

// NEVER — reject if in a TX
@Transactional(propagation = Propagation.NEVER)
void readFromReadReplica() {
  // This must NOT run inside a transaction
  // (read-replica routing breaks inside TX)
}

// NESTED — savepoint within outer TX
@Transactional(propagation = Propagation.NESTED)
void riskyOperation() {
  // If this throws: rollback to savepoint, not outer TX
  // Outer TX can catch the exception and continue
}
```

**NESTED vs REQUIRES_NEW — key distinction:**

```
NESTED:
  Uses SAME connection as outer TX
  Uses database savepoint
  If nested fails: rolls back to savepoint only
  If outer fails: nested work also rolls back
              (nested is still inside outer)

REQUIRES_NEW:
  Opens a NEW connection, NEW transaction
  Commits INDEPENDENTLY of outer TX
  If outer fails: inner committed work REMAINS
  If inner fails: only inner rolls back, outer unaffected
```

---

### 🔄 How It Connects (Mini-Map)

```
Method A (@Transactional) calls Method B (@Transactional)
        ↓
  TRANSACTION PROPAGATION (128)  ← you are here
  (what does B do with A's active transaction?)
        ↓
  PlatformTransactionManager evaluates:
  TransactionSynchronizationManager.getResource()
  (checks ThreadLocal for active TX)
        ↓
  Decision:
  REQUIRED → join A's TX
  REQUIRES_NEW → suspend A, new TX (new connection)
  NESTED → savepoint in A's TX
        ↓
  Related: Transaction Isolation (129)
  (what data B sees, orthogonal to propagation)
```

---

### 💻 Code Example

**Example 1 — REQUIRES_NEW for independent audit:**

```java
@Service
public class OrderService {
  private final AuditService audit;
  private final OrderRepository orderRepo;

  @Transactional  // propagation = REQUIRED (default)
  public Order place(OrderRequest req) {
    // WILL be rolled back if exception thrown
    Order order = orderRepo.save(Order.from(req));

    // AuditService uses REQUIRES_NEW
    audit.log("ORDER_PLACED", order.getId());
    // ↑ committed independently — NOT rolled back
    // even if place() throws below this line

    if (someCondition) {
      throw new BusinessException("Rejected");
      // order save rolls back, audit log PERSISTS
    }
    return order;
  }
}

@Service
public class AuditService {
  @Transactional(propagation = Propagation.REQUIRES_NEW)
  public void log(String event, long entityId) {
    auditRepo.save(new AuditEntry(event, entityId));
    // own TX: committed immediately, independent of caller
  }
}
```

**Example 2 — NESTED for partial rollback:**

```java
@Service
@Transactional
public class BatchProcessor {
  private final ItemRepository itemRepo;

  public BatchResult processBatch(List<Item> items) {
    int successes = 0, failures = 0;

    for (Item item : items) {
      try {
        processItem(item);  // nested TX
        successes++;
      } catch (ItemProcessingException e) {
        failures++;
        // Only this item's savepoint rolled back
        // Outer TX continues processing remaining items
      }
    }
    return new BatchResult(successes, failures);
  }

  @Transactional(propagation = Propagation.NESTED)
  void processItem(Item item) {
    itemRepo.save(item.process());
    // Savepoint here — if this fails,
    // only this item is rolled back, not entire batch
  }
}
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| REQUIRES_NEW is the same as calling a method outside a transaction | REQUIRES_NEW suspends the outer TX on the same thread and opens a new one. The outer TX resumes after the inner method. Without REQUIRES_NEW, you'd need a different thread entirely to get true independence |
| NESTED is the same as REQUIRES_NEW | NESTED uses a savepoint within the SAME connection. If the outer TX rolls back, NESTED work is also rolled back. REQUIRES_NEW uses a new connection and commits independently |
| Propagation controls the database isolation level | Propagation is about transaction boundaries; isolation is about data visibility. They are orthogonal settings. Use both in @Transactional independently |
| SUPPORTS is a safe default for read-only methods | SUPPORTS in a non-transactional context results in no transaction — JPA lazy loading will fail, and Hibernate's session may be closed unexpectedly |

---

### 🔥 Pitfalls in Production

**1. REQUIRES_NEW bloating the connection pool**

```java
// BAD: REQUIRES_NEW opens new connection per call
// In a loop of 1000 items:
for (Item item : 1000Items) {
  auditService.log(item); // each: new connection from pool
}
// HikariCP has 20 connections → 980 waits for free conn
// → Latency spike, potential deadlock

// GOOD: batch audit writes in one TX
auditService.logBatch(items); // one REQUIRES_NEW for all

// OR: async audit (non-critical path)
@Async
public void logAsync(Item item) { ... }
```

**2. NESTED propagation not supported by all transaction managers**

```java
// BAD: using NESTED with JpaTransactionManager
// on databases that don't support savepoints
@Transactional(propagation = Propagation.NESTED)
void processItem(Item item) { ... }

// DB2, SQL Server: savepoints supported ✅
// MySQL (InnoDB): savepoints supported ✅
// Some JPA providers: may not support NESTED properly
// → NestedTransactionNotSupportedException at runtime

// GOOD: test NESTED behaviour in staging before release
// Fallback: use REQUIRES_NEW if NESTED not supported
```

---

### 🔗 Related Keywords

- `@Transactional` — the annotation on which propagation is configured
- `PlatformTransactionManager` — implements the actual suspend/resume logic
- `Transaction Isolation Levels` — orthogonal setting controlling data visibility
- `Savepoint` — the mechanism behind NESTED propagation
- `REQUIRES_NEW` — the most important non-default propagation (independent TX)
- `TransactionSynchronizationManager` — the ThreadLocal holder tracking active transactions

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Controls what happens when @Transactional │
│              │ method called while TX already active     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ REQUIRED: default; REQUIRES_NEW: audit,  │
│              │ independent commit; NESTED: partial retry │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ REQUIRES_NEW in tight loops (pool bloat); │
│              │ NESTED without testing DB savepoints      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "REQUIRED shares the family card;         │
│              │  REQUIRES_NEW opens your own."            │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Transaction Isolation Levels (129) →      │
│              │ HikariCP (132) → N+1 Problem (130)        │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A service method `A` (REQUIRED) calls service method `B` (REQUIRES_NEW) which calls service method `C` (REQUIRED). During execution, `B`'s transaction is the active one when `C` runs. If `A` rolls back after `B` has committed, describe the exact state in the database. Now consider: thread T1 is in method A with connection conn1 (TX1 open). When B starts, it needs conn2 for TX2 — this conn2 comes from HikariCP pool. If the pool size is 1, describe exactly what happens and why `REQUIRES_NEW` in a single-connection pool is a deadlock scenario.

**Q2.** Spring's `NESTED` propagation behaviour with JPA is subtly different from JDBC savepoints. With `DataSourceTransactionManager` (pure JDBC), NESTED creates a real `java.sql.Savepoint`. With `JpaTransactionManager`, the behaviour depends on the JPA provider's support. Explain the specific problem with Hibernate and NESTED: Hibernate's first-level cache (persistence context) is NOT cleared when rolling back to a savepoint, meaning entities loaded before the nested savepoint are still cached with their pre-savepoint state, causing stale reads. Describe the mitigation.

