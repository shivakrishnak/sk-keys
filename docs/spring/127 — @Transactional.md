---
layout: default
title: "@Transactional"
parent: "Spring Framework"
nav_order: 127
permalink: /spring/transactional/
number: "127"
category: Spring & Spring Boot
difficulty: ★★☆
depends_on: AOP, CGLIB Proxy, Transaction Manager
used_by: Transaction Propagation, Transaction Isolation Levels
tags: #spring, #database, #internals, #intermediate
---

# 127 — @Transactional

`#spring` `#database` `#internals` `#intermediate`

⚡ TL;DR — @Transactional tells Spring to wrap a method in a database transaction — automatically beginning before the method and committing (or rolling back on exception) after.

| #127 | Category: Spring & Spring Boot | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | AOP, CGLIB Proxy, Transaction Manager | |
| **Used by:** | Transaction Propagation, Transaction Isolation Levels | |

---

### 📘 Textbook Definition

`@Transactional` is a Spring annotation that declaratively manages database transaction boundaries. When applied to a method or class, Spring's `PlatformTransactionManager` (via AOP proxy) starts a transaction before execution, commits on successful return, and rolls back on unchecked exceptions (or checked exceptions if `rollbackFor` is specified) — eliminating manual `beginTransaction()`/`commit()`/`rollback()` calls.

### 🟢 Simple Definition (Easy)

`@Transactional` says "wrap this method in a database transaction." If everything succeeds, commit. If something throws an exception, rollback all database changes. No manual BEGIN/COMMIT/ROLLBACK needed.

### 🔵 Simple Definition (Elaborated)

Spring implements `@Transactional` via AOP: a proxy intercepts the method call, opens a transaction, delegates to your real method, then commits or rolls back based on the outcome. The annotation supports rich configuration: isolation level, propagation behavior, timeout, read-only flag, and specific rollback rules.

### 🔩 First Principles Explanation

**Without @Transactional:**
```java
public void transferFunds(Account from, Account to, BigDecimal amount) {
    try {
        txManager.beginTransaction();
        from.debit(amount);
        to.credit(amount);   // if this throws, from.debit() is already done!
        txManager.commit();
    } catch (Exception e) {
        txManager.rollback();
        throw e;
    }
}
```
**With @Transactional:**
```java
@Transactional  // Spring handles begin/commit/rollback automatically
public void transferFunds(Account from, Account to, BigDecimal amount) {
    from.debit(amount);   // these share the same transaction
    to.credit(amount);    // if this throws → everything rolls back atomically
}
```

### 💻 Code Example
```java
@Service
public class OrderService {
    // Basic — commit on success, rollback on RuntimeException
    @Transactional
    public Order placeOrder(OrderRequest req) {
        Order order = orderRepo.save(new Order(req));
        inventoryService.deduct(order);   // all in same transaction
        paymentService.charge(order);
        return order;
    }
    // Rollback for checked exception too
    @Transactional(rollbackFor = {PaymentException.class, InventoryException.class})
    public void processOrder(Long orderId) throws PaymentException { ... }
    // Read-only: hint to DB + ORM that no writes expected
    @Transactional(readOnly = true)
    public List<Order> findAll() { return orderRepo.findAll(); }
    // Timeout: rollback if takes more than 30 seconds
    @Transactional(timeout = 30)
    public void longRunningProcess() { ... }
    // Specific propagation (see Transaction Propagation entry)
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void auditLog(String action) { ... } // always its own transaction
}
```

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| @Transactional works on private methods | AOP proxy can't intercept private methods — @Transactional silently ignored |
| Checked exceptions trigger rollback | Only unchecked (RuntimeException) by default — add rollbackFor for checked |
| @Transactional on interface works too | Avoid @Transactional on interfaces — put it on implementation |
| Calling @Transactional method within same class triggers TX | Self-invocation bypasses the proxy — no new transaction starts |

### 🔥 Pitfalls in Production

**Pitfall: Self-invocation bypasses transaction**
```java
@Service
public class OrderService {
    @Transactional
    public void placeOrder() { processPayment(); } // proxy NOT invoked!
    @Transactional(propagation = REQUIRES_NEW) // has no effect here!
    public void processPayment() { ... }
}
// Fix: inject OrderService and call self.processPayment()
// Or: extract processPayment to another @Service bean
```
**Pitfall: @Transactional(readOnly=true) on write operations**
```java
@Transactional(readOnly = true) // Hibernate disables dirty checking — write silently ignored!
public void updateUser(User user) { userRepo.save(user); } // no DB write!
```

### 🔗 Related Keywords

- **[Transaction Propagation](./128 — Transaction Propagation.md)** — how transactions compose across method calls
- **[Transaction Isolation Levels](./129 — Transaction Isolation Levels.md)** — concurrency guarantees
- **[AOP](./118 — AOP (Aspect-Oriented Programming).md)** — mechanism behind @Transactional
- **[CGLIB Proxy](./116 — CGLIB Proxy.md)** — proxy type used to intercept @Transactional methods

### 📌 Quick Reference Card
```
+------------------------------------------------------------------+
| DEFAULT     | Begins TX, commits on success, rollbacks on RuntimeEx|
+------------------------------------------------------------------+
| readOnly    | Optimization hint — no writes; ORM dirty check off   |
+------------------------------------------------------------------+
| rollbackFor | Include checked exceptions in rollback               |
+------------------------------------------------------------------+
| SELF-INVOKE | DOESN'T WORK — must call via proxy (another bean)    |
+------------------------------------------------------------------+
| PRIVATE     | DOESN'T WORK — AOP cannot intercept private methods  |
+------------------------------------------------------------------+
```

### 🧠 Think About This Before We Continue

**Q1.** What is the difference between `@Transactional(rollbackFor=Exception.class)` and the default behavior?
**Q2.** A method marked `@Transactional` calls another method marked `@Transactional(propagation=REQUIRES_NEW)` in the SAME class. What happens and why?
**Q3.** What is "transaction-aware datasource" and how does Spring make the same DB connection available throughout a single transaction?
