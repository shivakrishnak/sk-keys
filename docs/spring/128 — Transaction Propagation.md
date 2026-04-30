---
layout: default
title: "Transaction Propagation"
parent: "Spring Framework"
nav_order: 128
permalink: /spring/transaction-propagation/
number: "128"
category: Spring & Spring Boot
difficulty: ★★☆
depends_on: @Transactional
used_by: Nested transactions, service layer design
tags: #spring, #database, #internals, #intermediate
---

# 128 — Transaction Propagation

`#spring` `#database` `#internals` `#intermediate`

⚡ TL;DR — Transaction Propagation defines what Spring does when a @Transactional method is called while a transaction is already active: join it, start a new one, suspend it, or fail.

| #128 | Category: Spring & Spring Boot | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | @Transactional | |
| **Used by:** | Nested transactions, service layer design | |

---

### 📘 Textbook Definition
`Propagation` is an attribute of `@Transactional` that controls the transaction boundaries when a transactional method is invoked in the context of an existing transaction. The seven propagation types define whether the method joins the caller's transaction, creates its own, suspends the caller's, or throws an exception.
### 🟢 Simple Definition (Easy)
Propagation answers: "If someone is already in a transaction when they call my method, what should I do?" Should I join their transaction? Start my own? Refuse to run inside one?
### 🔩 First Principles Explanation
**Seven propagation types:**
```
REQUIRED (DEFAULT)   — Join existing tx; create new if none
REQUIRES_NEW         — Always create new tx; suspend existing
SUPPORTS             — Join if exists; run without tx if none
NOT_SUPPORTED        — Run without tx; suspend existing if any
MANDATORY            — Join existing; throw if no active tx
NEVER                — Run without tx; throw if tx exists
NESTED               — Run in nested tx (savepoint); part of outer tx
```
**Most important — REQUIRED vs REQUIRES_NEW:**
```
Method A (@Transactional REQUIRED)
   → starts TX-A
   → calls Method B (@Transactional REQUIRED)
      → JOINS TX-A (same transaction)
      → if B throws and rolls back, TX-A also rolls back
Method A (@Transactional REQUIRED)
   → starts TX-A
   → calls Method B (@Transactional REQUIRES_NEW)
      → TX-A suspended, new TX-B started
      → if B throws and rolls back, only TX-B rolls back
      → TX-A continues after B (success or failure)
```
### 💻 Code Example
```java
@Service
public class OrderService {
    @Autowired OrderService self; // inject self to bypass proxy issue
    @Transactional
    public void placeOrder(Order order) {
        orderRepo.save(order);
        self.auditLog("ORDER_PLACED"); // via proxy — REQUIRES_NEW works
    }
    // Audit log must ALWAYS commit regardless of outer transaction outcome
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void auditLog(String event) {
        auditRepo.save(new AuditEntry(event, LocalDateTime.now()));
    }
    // Must always run in an existing transaction
    @Transactional(propagation = Propagation.MANDATORY)
    public void deductInventory(Order order) {
        // throws IllegalTransactionStateException if no active tx
    }
    // Reporting — can run with or without transaction
    @Transactional(propagation = Propagation.SUPPORTS, readOnly = true)
    public List<Order> report() {
        return orderRepo.findAll();
    }
}
```
### ⚠️ Common Misconceptions
| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| REQUIRES_NEW works with self-invocation | Must call through proxy; self-invocation bypasses propagation entirely |
| NESTED = REQUIRES_NEW | NESTED uses savepoints — rollback goes to savepoint, not full rollback |
| SUPPORTS always uses a transaction | SUPPORTS joins if exists, but runs non-transactionally if none |
### 🔗 Related Keywords
- **[@Transactional](./127 — @Transactional.md)** — the annotation that uses propagation
- **[Transaction Isolation Levels](./129 — Transaction Isolation Levels.md)** — concurrency behavior within a transaction
### 📌 Quick Reference Card
```
+------------------------------------------------------------------+
| REQUIRED     | Join existing or create new (DEFAULT)              |
+------------------------------------------------------------------+
| REQUIRES_NEW | Always new TX — suspend outer                       |
+------------------------------------------------------------------+
| NOT_SUPPORTED| Never use TX — suspend outer                        |
+------------------------------------------------------------------+
| MANDATORY    | Must have existing TX or throw                       |
+------------------------------------------------------------------+
| NESTED       | Savepoint in outer TX (partial rollback)             |
+------------------------------------------------------------------+
```
