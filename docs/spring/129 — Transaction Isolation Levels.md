---
layout: default
title: "Transaction Isolation Levels"
parent: "Spring Framework"
nav_order: 129
permalink: /spring/transaction-isolation-levels/
number: "129"
category: Spring & Spring Boot
difficulty: ★★★
depends_on: @Transactional, Database Transactions
used_by: Concurrency control, dirty read prevention
tags: #spring, #database, #internals, #advanced
---

# 129 — Transaction Isolation Levels

`#spring` `#database` `#internals` `#advanced`

⚡ TL;DR — Transaction Isolation Levels control how much concurrent transactions can "see" each other's uncommitted data — trading consistency for performance/concurrency.

| #129 | Category: Spring & Spring Boot | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | @Transactional, Database Transactions | |
| **Used by:** | Concurrency control, dirty read prevention | |

---

### 📘 Textbook Definition

Transaction isolation levels define the degree to which one transaction must be isolated from changes made by concurrent transactions. SQL standard defines four levels: READ_UNCOMMITTED, READ_COMMITTED, REPEATABLE_READ, and SERIALIZABLE, each preventing different concurrency anomalies (dirty reads, non-repeatable reads, phantom reads).

### 🟢 Simple Definition (Easy)

Isolation level answers: "If another transaction is changing data right now, can my transaction see those in-progress changes?" Higher isolation = more consistency; lower isolation = better performance.

### 🔩 First Principles Explanation

**Concurrency anomalies:**
```
Dirty Read     — reading uncommitted changes (another tx might rollback)
Non-Repeatable — reading same row twice gets different values (updated between reads)
Phantom Read   — reading same range twice gets different rows (inserted between reads)
```
**Isolation levels and what they prevent:**
```
Level              | Dirty Read | Non-Repeat | Phantom
────────────────────────────────────────────────────────
READ_UNCOMMITTED   |    ✗        |    ✗        |   ✗
READ_COMMITTED     |    ✓        |    ✗        |   ✗   ← Postgres default
REPEATABLE_READ    |    ✓        |    ✓        |   ✗   ← MySQL InnoDB default
SERIALIZABLE       |    ✓        |    ✓        |   ✓   ← Full isolation (slowest)
```

### 💻 Code Example
```java
// Set isolation level with @Transactional
@Transactional(isolation = Isolation.READ_COMMITTED)
public Order findOrder(Long id) { return orderRepo.findById(id).orElseThrow(); }
@Transactional(isolation = Isolation.SERIALIZABLE)
public void criticalTransfer(Account from, Account to, BigDecimal amount) {
    // Fully isolated — no dirty/non-repeatable/phantom reads possible
    // Lowest concurrency — use only when absolutely required
}
@Transactional(isolation = Isolation.REPEATABLE_READ)
public BigDecimal calculateBalance(Long accountId) {
    // Same query returns same result even if another tx updates between calls
    BigDecimal credits = ledgerRepo.sumCredits(accountId);
    BigDecimal debits = ledgerRepo.sumDebits(accountId);
    return credits.subtract(debits); // no non-repeatable read possible
}
```

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| Higher isolation = always better | Higher isolation = more locking = less concurrency = slower |
| SERIALIZABLE prevents all anomalies | Yes, but at the cost of effectively serializing all transactions |
| Isolation level is set in Spring | Spring passes it to the DB; the DB enforces it |

### 🔗 Related Keywords

- **[@Transactional](./127 — @Transactional.md)** — annotation that sets isolation level
- **[Transaction Propagation](./128 — Transaction Propagation.md)** — how transactions compose

### 📌 Quick Reference Card
```
+------------------------------------------------------------------+
| READ_UNCOMMITTED | Sees uncommitted changes — avoid in production  |
+------------------------------------------------------------------+
| READ_COMMITTED   | Sees only committed — Postgres default           |
+------------------------------------------------------------------+
| REPEATABLE_READ  | Same row read twice = same result               |
+------------------------------------------------------------------+
| SERIALIZABLE     | Full isolation — transactions appear sequential  |
+------------------------------------------------------------------+
```
