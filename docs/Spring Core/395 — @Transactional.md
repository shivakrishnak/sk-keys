---
layout: default
title: "@Transactional"
parent: "Spring Core"
nav_order: 395
permalink: /spring/transactional/
number: "395"
category: Spring Core
difficulty: ★★☆
depends_on: "AOP (Aspect-Oriented Programming), CGLIB Proxy, Bean Lifecycle, Transaction Propagation"
used_by: "Transaction Propagation, Transaction Isolation Levels, Spring Data JPA"
tags: #intermediate, #spring, #database, #pattern
---

# 395 — @Transactional

`#intermediate` `#spring` `#database` `#pattern`

⚡ TL;DR — `@Transactional` declaratively wraps a method in a database transaction using Spring AOP proxies. It begins a transaction before the method, commits on success, and rolls back on unchecked exceptions (`RuntimeException` or `Error`) by default.

| #395            | Category: Spring Core                                                                   | Difficulty: ★★☆ |
| :-------------- | :-------------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | AOP (Aspect-Oriented Programming), CGLIB Proxy, Bean Lifecycle, Transaction Propagation |                 |
| **Used by:**    | Transaction Propagation, Transaction Isolation Levels, Spring Data JPA                  |                 |

---

### 📘 Textbook Definition

`@Transactional` is a Spring annotation that declaratively demarcates transaction boundaries using AOP proxies. When a method annotated with `@Transactional` is called through a Spring proxy, `TransactionInterceptor` (a `MethodInterceptor`) invokes `PlatformTransactionManager.getTransaction()` to begin (or join) a transaction, then calls the actual method. On successful return, `PlatformTransactionManager.commit()` is called; if a `RuntimeException` or `Error` propagates out, `PlatformTransactionManager.rollback()` is called. For checked exceptions, the transaction commits by default (configurable via `rollbackFor`). `@Transactional` attributes include `propagation` (how to behave relative to existing transactions — `REQUIRED`, `REQUIRES_NEW`, etc.), `isolation` (read/write visibility — `READ_COMMITTED`, `REPEATABLE_READ`, etc.), `timeout` (auto-rollback after N seconds), `readOnly` (optimisation hint for read-only transactions), and `rollbackFor`/`noRollbackFor` (exception type customisation). `@EnableTransactionManagement` on a `@Configuration` class registers the AOP infrastructure; Spring Boot auto-enables this.

---

### 🟢 Simple Definition (Easy)

`@Transactional` tells Spring: "wrap this method in a database transaction — if everything succeeds, commit; if anything goes wrong (a RuntimeException), roll everything back." It is the alternative to manual `connection.commit()` / `connection.rollback()` code.

---

### 🔵 Simple Definition (Elaborated)

Without `@Transactional`, if you save three records in one service method and the third one fails, the first two are already committed to the database — they cannot be undone. With `@Transactional`, all three saves are part of one transaction: either all succeed and commit together, or one fails and all three are rolled back. Spring implements this by wrapping your service bean in a proxy — the proxy starts the transaction before calling your method and commits or rolls back after. You write clean business logic; the transaction plumbing is completely separate.

---

### 🔩 First Principles Explanation

**How the transaction proxy works:**

```
ApplicationContext startup:
  1. @EnableTransactionManagement registers TransactionInterceptor (AOP Advice)
  2. BeanFactoryTransactionAttributeSourceAdvisor wraps it as an Advisor
  3. For every bean: does this class have @Transactional methods?
     YES → wrap bean in CGLIB/JDK proxy with TransactionInterceptor

At runtime, calling a @Transactional method through the proxy:
  ┌──────────────────────────────────────────────────────────────┐
  │ TransactionInterceptor.invoke(MethodInvocation invocation)   │
  │                                                              │
  │ 1. Inspect method's @Transactional metadata                  │
  │    → propagation, isolation, timeout, readOnly, rollbackFor  │
  │                                                              │
  │ 2. PlatformTransactionManager.getTransaction(definition)     │
  │    → Propagation logic: JOIN existing? CREATE NEW? SUSPEND?  │
  │    → Begin transaction (get Connection from pool)            │
  │    → Bind Connection to current thread via ThreadLocal        │
  │      (TransactionSynchronizationManager)                     │
  │                                                              │
  │ 3. invocation.proceed() ← calls actual @Service method       │
  │    → All DB calls in thread use the SAME bound Connection     │
  │                                                              │
  │ 4a. No exception → txManager.commit(status)                  │
  │     → SQL flushed to DB → DB commits                         │
  │     → Connection returned to pool                            │
  │                                                              │
  │ 4b. RuntimeException/Error thrown:                           │
  │     → completeTransactionAfterThrowing() called              │
  │     → rollbackFor check: should we roll back?                │
  │     → txManager.rollback(status) → all SQL undone            │
  │     → Connection returned to pool                            │
  │     → Exception re-thrown to caller                          │
  │                                                              │
  │ 4c. Checked exception thrown (by default):                   │
  │     → txManager.commit(status) ← commits on checked ex!      │
  │     → To roll back on checked: rollbackFor=IOException.class │
  └──────────────────────────────────────────────────────────────┘
```

**ThreadLocal connection binding (why it works across multiple DAO calls):**

```java
@Service
class OrderService {
    @Autowired OrderRepository orderRepo;   // JPA repository
    @Autowired InventoryRepository invRepo; // another JPA repository

    @Transactional
    public void placeOrder(OrderRequest req) {
        // Both these calls use the SAME Connection (same transaction)
        // Because TransactionSynchronizationManager bound the Connection
        // to the current thread when the transaction started
        Order order = orderRepo.save(new Order(req));   // INSERT orders
        invRepo.decrementStock(req.getProductId(), 1);  // UPDATE inventory
        // If decrementStock() throws RuntimeException:
        //   → BOTH the INSERT and UPDATE are rolled back
    }
    // On method return: commit → both INSERT and UPDATE go to DB atomically
}
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT @Transactional:

What breaks without it:

1. Manual transaction management clutters business logic with `try-catch-commit-rollback`.
2. If two DAO methods are called, they may use different database connections — they are NOT atomic.
3. `EntityManager` without an active transaction cannot flush changes — they are silently lost.
4. Partial failures leave data in inconsistent state (some records saved, others not).

WITH @Transactional:
→ Business logic is clean — no transaction boilerplate.
→ All DB operations in the method share one connection, one transaction.
→ Atomicity, Consistency, Isolation, Durability (ACID) properties are ensured.
→ `readOnly=true` enables optimisation — JPA skips dirty checking, database may use read replicas.

---

### 🧠 Mental Model / Analogy

> Think of `@Transactional` as a "save game" checkpoint in a video game. When you enter a `@Transactional` method, Spring saves the current state (begins a transaction). If you complete the method successfully, the progress is saved permanently (commit). If the method crashes (RuntimeException), Spring reloads the checkpoint — everything is exactly as it was before you entered (rollback). Manual transactions are like playing without any auto-save: if the game crashes, you have lost all progress since the last manual save.

"Save game checkpoint" = transaction begin (getTransaction)
- "Complete level" = method returns normally → commit
- "Game crashes" = RuntimeException thrown → rollback to checkpoint
"Multiple game actions" = multiple DB calls all within the same transaction

---

### ⚙️ How It Works (Mechanism)

**The self-invocation trap — the most common @Transactional bug:**

```java
@Service
class PaymentService {

    // Called externally → goes through proxy → transaction STARTS
    public void processPayments(List<Payment> payments) {
        for (Payment p : payments) {
            this.processOne(p); // 'this' = raw bean → bypasses proxy → NO TRANSACTION!
        }
    }

    @Transactional
    public void processOne(Payment p) {
        // @Transactional annotation is IGNORED here
        // because 'this' is the raw object, not the proxy
        paymentRepo.save(p);
    }
}

// FIX 1: Inject self (Spring Boot allows circular injection with @Lazy):
@Autowired
@Lazy
private PaymentService self;
self.processOne(p); // goes through proxy → transaction works

// FIX 2: Extract to separate bean:
@Autowired
private PaymentProcessor processor;
processor.processOne(p); // separate bean → separate proxy → transaction works
```

**readOnly=true — JPA optimisation:**

```java
@Transactional(readOnly = true)
public List<Order> getRecentOrders(LocalDate since) {
    // JPA Hibernate: skips dirty checking (no need to track entity changes)
    // Spring Data: may route to read replica datasource
    // JDBC: may set Connection.setReadOnly(true)
    return orderRepo.findBySinceDate(since);
}
```

---

### 🔄 How It Connects (Mini-Map)

```
@Transactional  ◄──── (you are here)
(annotation on method/class)
        │
        ▼
TransactionInterceptor (AOP Advice — MethodInterceptor)
        │
        ▼
PlatformTransactionManager
(JpaTransactionManager, DataSourceTransactionManager, etc.)
        │
        ├── Transaction Propagation → how to handle existing transactions
        │   (REQUIRED, REQUIRES_NEW, SUPPORTS, MANDATORY, ...)
        │
        ├── Transaction Isolation Levels → concurrent read/write behaviour
        │   (READ_COMMITTED, REPEATABLE_READ, SERIALIZABLE, ...)
        │
        └── Spring Data JPA → @Repository methods inherit @Transactional
```

---

### 💻 Code Example

**Complete @Transactional example with rollback and custom exceptions:**

```java
@Service
@Transactional          // class-level default: REQUIRED propagation
public class OrderService {

    @Autowired private OrderRepository orderRepo;
    @Autowired private PaymentGateway paymentGateway;
    @Autowired private InventoryService inventoryService;

    // Inherits class-level @Transactional: REQUIRED propagation
    public Order createOrder(OrderRequest req) {
        Order order = orderRepo.save(Order.fromRequest(req)); // INSERT
        inventoryService.reserve(req.getProductId(), req.getQty()); // UPDATE

        try {
            paymentGateway.charge(req.getPaymentDetails()); // external call
        } catch (PaymentDeclinedException ex) {
            // PaymentDeclinedException is a RuntimeException
            // → Transaction will be rolled back (order and inventory)
            throw ex; // re-throw to trigger rollback
        }

        return order; // commit: INSERT + UPDATE persist
    }

    // Read-only: no dirty checking, possible read replica routing
    @Transactional(readOnly = true)
    public Order findOrder(Long id) {
        return orderRepo.findById(id)
            .orElseThrow(() -> new OrderNotFoundException(id));
    }

    // Checked exception: must configure rollbackFor explicitly
    @Transactional(rollbackFor = InsufficientFundsException.class)
    public void transferFunds(Long from, Long to, BigDecimal amount)
        throws InsufficientFundsException {
        // InsufficientFundsException is checked → must declare rollbackFor
        // Without it: the transaction would COMMIT even with this exception!
        accountService.debit(from, amount);
        accountService.credit(to, amount);
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                                               | Reality                                                                                                                                                                                                                                                                           |
| --------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `@Transactional` works when you call a method via `this`                    | Self-invocation bypasses the Spring proxy. If `methodA()` calls `this.methodB()` where `methodB()` is `@Transactional`, the annotation is ignored. The call must go through the proxy — either inject self or extract to a separate bean                                          |
| Checked exceptions always roll back a `@Transactional` method               | By default, `@Transactional` only rolls back on `RuntimeException` and `Error`. Checked exceptions (e.g., `IOException`, custom checked exceptions) cause a COMMIT by default. To roll back on a checked exception, use `rollbackFor = YourException.class`                       |
| `@Transactional` on a `private` or `final` method works                     | CGLIB cannot proxy `private`, `final`, or `static` methods. The annotation is silently ignored. The method must be `public` (or at minimum `protected` for CGLIB) and overridable. Spring logs a warning for `private` `@Transactional` methods if Spring Boot DevTools is active |
| `@Transactional` on a class applies to all methods including inherited ones | Class-level `@Transactional` is the default for all methods defined in that class. Inherited methods from a non-transactional superclass do NOT inherit the annotation unless overridden or the superclass is also annotated                                                      |

---

### 🔥 Pitfalls in Production

**Lazy loading outside transaction — LazyInitializationException**

```java
@Transactional
public Order findOrder(Long id) {
    Order order = orderRepo.findById(id).orElseThrow();
    return order; // @Transactional ends here → Hibernate session closed
}

// OUTSIDE the transaction:
Order order = orderService.findOrder(1L);
order.getItems().size(); // LazyInitializationException!
// order.items is a lazy collection — Hibernate session is closed

// FIX 1: Use @Transactional in the caller layer or open-session-in-view
// FIX 2: Eagerly fetch in the query:
@Query("SELECT o FROM Order o JOIN FETCH o.items WHERE o.id = :id")
Optional<Order> findWithItems(@Param("id") Long id);

// FIX 3: Use a DTO projection instead of returning entities
```

---

### 🔗 Related Keywords

- `Transaction Propagation` — controls what happens when `@Transactional` methods call each other
- `Transaction Isolation Levels` — controls read/write visibility between concurrent transactions
- `AOP (Aspect-Oriented Programming)` — `@Transactional` is implemented as AOP advice (`TransactionInterceptor`)
- `CGLIB Proxy` — the proxy mechanism that intercepts `@Transactional` method calls
- `Spring Data JPA` — Spring Data repositories are `@Transactional` by default on write methods

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ ROLLBACK ON  │ RuntimeException + Error (default)        │
│ COMMITS ON   │ Checked exceptions (default)              │
│ FIX CHECKED  │ rollbackFor = MyCheckedException.class    │
├──────────────┼───────────────────────────────────────────┤
│ SELF-INVOKE  │ BYPASSES proxy → @Transactional ignored   │
│ FIX          │ Inject self (@Lazy) or extract to bean    │
├──────────────┼───────────────────────────────────────────┤
│ READONLY     │ true → JPA skips dirty check, faster reads│
├──────────────┼───────────────────────────────────────────┤
│ WORKS ON     │ public methods only (CGLIB requirement)   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "@Transactional = save game checkpoint:   │
│              │  commit on success, rollback on crash."  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Spring's `@Transactional` binds the database Connection to the current thread via `TransactionSynchronizationManager` (a `ThreadLocal` map). Describe what happens in a multi-threaded scenario: if a `@Transactional` method spawns a new thread (via `@Async` or manually with `new Thread()`), does the spawned thread share the same transaction? Does it get its own Connection? Can the spawned thread's database work be rolled back if the parent method fails? And what is the correct approach for executing parallel database work that must be atomic with the parent transaction?

**Q2.** `@Transactional(readOnly = true)` is described as an "optimisation hint." Describe exactly what each layer does with this hint: (a) Hibernate: how does `FlushMode.MANUAL` differ from `FlushMode.AUTO`, and what dirty checking does Hibernate skip? (b) `PlatformTransactionManager`: what does `DataSourceTransactionManager` do with `Connection.setReadOnly(true)` — is this guaranteed to prevent writes? (c) Spring Data's connection routing: how does `AbstractRoutingDataSource` use the `readOnly` flag to route to a read replica? And what is the risk if a `readOnly` transaction is mistakenly used for a write operation?
