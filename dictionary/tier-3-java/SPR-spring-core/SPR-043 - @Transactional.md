---
layout: default
title: "@Transactional"
parent: "Spring Core"
grand_parent: "Technical Dictionary"
nav_order: 43
permalink: /spring/transactional/
id: SPR-043
category: Spring Core
difficulty: ★★☆
depends_on: AOP, CGLIB Proxy, JDK Dynamic Proxy, Bean, Transaction Propagation
used_by: Spring Data JPA, JDBC, JTA, Spring Services
related: Transaction Propagation, Transaction Isolation Levels, CGLIB Proxy, AOP, "@EnableTransactionManagement"
tags:
  - spring
  - springboot
  - intermediate
  - pattern
  - bestpractice
---

# SPR-043 - @Transactional

⚡ TL;DR - @Transactional marks a method or class for declarative transaction management - Spring AOP wraps the call in a transaction that auto-commits on success and auto-rolls-back on unchecked exceptions (RuntimeException) unless configured otherwise.

| #395            | Category: Spring Core                                                                                 | Difficulty: ★★☆ |
| :-------------- | :---------------------------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | AOP, CGLIB Proxy, JDK Dynamic Proxy, Bean, Transaction Propagation                                    |                 |
| **Used by:**    | Spring Data JPA, JDBC, JTA, Spring Services                                                           |                 |
| **Related:**    | Transaction Propagation, Transaction Isolation Levels, CGLIB Proxy, AOP, @EnableTransactionManagement |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Every service method that touches the database needs: `TransactionManager.getTransaction()`, try/catch around the business logic, `commit()` on success, `rollback()` on failure. 50 service methods = 50 identical try/commit/rollback blocks. When transaction configuration needs to change (e.g., add read-only optimization to all read methods), you edit 50 files. Exception handling differences between methods create subtle inconsistencies.

**THE BREAKING POINT:**
Transaction management is pure infrastructure concern. It has nothing to do with `createUser()` or `findAllOrders()`. Embedding it inside each business method violates SRP and makes the business logic unreadable.

**THE INVENTION MOMENT:**
"This is exactly why @Transactional exists - declarative transaction management via AOP."

---

### 📘 Textbook Definition

**@Transactional** is a Spring annotation (`org.springframework.transaction.annotation.Transactional`) that marks a method or class to be wrapped in a transaction by Spring's AOP `TransactionInterceptor`. When a matching method is called through the Spring proxy, `TransactionInterceptor` calls `PlatformTransactionManager.getTransaction()` with the annotation's configured `propagation`, `isolation`, `readOnly`, `timeout`, and `rollbackFor`/`noRollbackFor` rules. After the method returns normally, `commit()` is called. If a `RuntimeException` (or `Error`) is thrown, `rollback()` is called. Checked exceptions do NOT trigger rollback by default - they must be specified in `rollbackFor`. `@Transactional` can be placed on methods, classes (applies to all public methods), or interfaces (not recommended).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
@Transactional says "wrap this method in a database transaction - commit on success, rollback on RuntimeException."

**One analogy:**

> @Transactional is a financial escrow service. You instruct: "hold the money in escrow (begin transaction), deliver it only if both parties sign (commit on success), return it if the deal falls through (rollback on exception)." The escrow service handles all the mechanics - you just say "this is an escrow transaction" on the instruction sheet.

**One insight:**
`@Transactional` only works when called through the Spring proxy. A call to `this.transactionalMethod()` from within the same class bypasses the proxy - the transaction never starts. This is the self-invocation limitation of Spring AOP.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Only applies to public methods (CGLIB/JDK proxies can't intercept private/package-private methods effectively).
2. Rollback on `RuntimeException` and `Error` by default. Checked exceptions do NOT trigger rollback unless specified.
3. Self-invocation (calling `this.save()`) bypasses the proxy - no transaction starts.
4. Read-only transactions (`readOnly = true`) are a hint to the persistence provider - may optimize (e.g., Hibernate skips dirty checking).
5. `@Transactional` on a class applies to all public methods (equivalent to annotating each method).

**TRANSACTION ATTRIBUTES:**

```java
@Transactional(
    propagation = Propagation.REQUIRED,    // default: join existing or create new
    isolation = Isolation.DEFAULT,          // default: use DB default
    readOnly = false,                       // default: read-write
    timeout = -1,                           // default: no timeout (seconds)
    rollbackFor = {RuntimeException.class}, // default
    noRollbackFor = {},                     // default: none
    rollbackForClassName = {},
    noRollbackForClassName = {}
)
```

---

### 🧪 Thought Experiment

**SETUP:**
`UserService.createUser()` creates a user AND sends a welcome email. The email sending can fail.

**WITHOUT @Transactional consideration:**

```java
public void createUser(User user) {
    userRepo.save(user);          // DB commit
    emailService.sendWelcome(user); // throws MailException (checked!)
    // User saved in DB but email failed
    // No automatic rollback for checked exceptions!
}
```

**WITH @Transactional and rollbackFor:**

```java
@Transactional(rollbackFor = Exception.class)  // ALL exceptions trigger rollback
public void createUser(User user) {
    userRepo.save(user);
    emailService.sendWelcome(user);  // throws MailException → rollback!
    // User NOT saved if email fails
}
```

**BUT: email sending should NOT be in the transaction:**

```java
@Transactional
public User createUser(User user) {
    return userRepo.save(user);  // commit user first
}

public void createUserAndNotify(User user) {
    User saved = createUser(user);  // committed
    emailService.sendWelcome(saved); // outside transaction
    // User saved even if email fails
    // Failure modes are independent
}
```

**THE INSIGHT:**
Transaction boundaries should wrap exactly the operations that must be atomic. Email sending (external service) should be outside the DB transaction - failure in email should not roll back the user creation.

---

### 🧠 Mental Model / Analogy

> @Transactional is an insurance policy wrapped around a database operation. You take out the policy (begin transaction) before you start work. If everything goes perfectly (normal return), the policy pays out (commit - changes are permanent). If something goes wrong at runtime (RuntimeException), the insurance covers it (rollback - changes are reversed). But the policy only covers runtime accidents, not "expected problems" (checked exceptions) unless you specifically add them to the policy coverage (`rollbackFor`).

- "Take out policy" → `PlatformTransactionManager.getTransaction()`
- "Policy pays out" → `commit()`
- "Insurance covers it" → `rollback()`
- "Expected problems not covered" → checked exceptions don't rollback by default

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
@Transactional wraps your method in a database transaction. If the method completes without error, the database changes are saved permanently. If an error occurs, the database changes are cancelled (rolled back) as if they never happened.

**Level 2 - How to use it (junior developer):**
Put `@Transactional` on service methods that perform multiple database operations that must succeed or fail together. Use `readOnly = true` on query methods for performance. Remember: rollback is automatic for RuntimeExceptions only - add `rollbackFor = Exception.class` if you need rollback on checked exceptions. Don't put `@Transactional` on private methods or call transactional methods from within the same class.

**Level 3 - How it works (mid-level engineer):**
`@EnableTransactionManagement` registers `TransactionInterceptor` as an AOP advice. When a `@Transactional` method is called through the proxy, `TransactionInterceptor.invoke()` calls `createTransactionIfNecessary()` which delegates to `PlatformTransactionManager` (e.g., `JpaTransactionManager`). JPA `EntityManager` is bound to the current thread via `TransactionSynchronizationManager`. On commit, `EntityManager.flush()` is called. On rollback, the underlying JDBC connection's `rollback()` is called. Transaction state is stored in `ThreadLocal` variables - this is why `@Transactional` doesn't work with `CompletableFuture` or `@Async` without explicit context propagation.

**Level 4 - Why it was designed this way (senior/staff):**
The default rollback-on-RuntimeException (not checked exceptions) was controversial but deliberate. In Java's exception model, checked exceptions represent expected outcomes that the caller should handle - the Spring team argued that "expected outcomes" (file not found, invalid input) shouldn't necessarily roll back transactions. Only unexpected failures (NPE, constraint violation) should rollback. This is philosophically coherent but practically surprising - developers often annotate with `rollbackFor = Exception.class` to override. The thread-local transaction binding is a key design choice: it enables `@Transactional` methods to call each other (via `REQUIRED` propagation) and share the same transaction without explicit parameter passing. The cost is incompatibility with async operations - a known limitation documented in the Spring reference guide.

---

### ⚙️ How It Works (Mechanism)

**TransactionInterceptor flow:**

```java
// Simplified TransactionInterceptor.invoke():
public Object invoke(MethodInvocation invocation) throws Throwable {
    // 1. Determine transaction attributes
    TransactionAttribute txAttr = getTransactionAttributeSource()
        .getTransactionAttribute(method, targetClass);

    // 2. Get or create transaction
    TransactionStatus status = transactionManager
        .getTransaction(txAttr);

    try {
        // 3. Invoke the real method
        Object retVal = invocation.proceed();

        // 4. Commit on success
        transactionManager.commit(status);
        return retVal;

    } catch (Throwable ex) {
        // 5. Rollback if rule matches
        if (txAttr.rollbackOn(ex)) {
            transactionManager.rollback(status);
        } else {
            transactionManager.commit(status);  // commit even on exception!
        }
        throw ex;
    }
}
```

**ThreadLocal transaction storage:**

```
Thread 1: request to createUser()
    ↓
TransactionSynchronizationManager:
  transactionHolder (ThreadLocal) = JpaTransactionObject {
      EntityManager: em_1,
      ConnectionHolder: conn_1
  }
    ↓
userRepo.save(user) → uses em_1 (same transaction)
    ↓
auditRepo.save(audit) → uses em_1 (same transaction)
    ↓
commit() → em_1.flush() → conn_1.commit()
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
userService.createUser(user) called
    ↓
CGLIB proxy intercepts ← @Transactional proxy wraps the call
    ↓
TransactionInterceptor: @Transactional found
    ↓
JpaTransactionManager.getTransaction():
  Current transaction? No → BEGIN new transaction
  EntityManager bound to ThreadLocal
    ↓ ← YOU ARE HERE (transaction started)
real UserService.createUser() executes
  userRepo.save() uses thread-local EntityManager
  auditRepo.save() uses SAME EntityManager (same tx)
    ↓
Normal return
    ↓
TransactionInterceptor: commit
  EntityManager.flush() → SQL sent to DB
  connection.commit()
    ↓
Transaction cleared from ThreadLocal
```

**EXCEPTION FLOW:**

```
method throws DataIntegrityViolationException (RuntimeException)
    ↓
TransactionInterceptor: is this a rollback exception?
  YES (RuntimeException) → rollback
    ↓
connection.rollback()
    ↓
Exception rethrown to caller
```

---

### 💻 Code Example

**Example 1 - Standard service transaction:**

```java
@Service
@Transactional  // applies to all public methods
public class OrderService {

    // Inherits @Transactional from class
    public Order placeOrder(OrderRequest req) {
        Order order = orderRepo.save(new Order(req));
        inventoryService.reserveItems(req.getItems());  // same transaction!
        return order;
    }

    // Read-only optimization
    @Transactional(readOnly = true)
    public List<Order> findByCustomer(Long customerId) {
        return orderRepo.findByCustomerId(customerId);
    }

    // New transaction regardless of existing
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void saveAuditLog(String action) {
        auditRepo.save(new AuditLog(action));
        // Always committed independently - even if outer tx rolls back
    }

    // Rollback on checked exception
    @Transactional(rollbackFor = Exception.class)
    public void createAndNotify(User user) throws MailException {
        userRepo.save(user);
        emailService.send(user.getEmail());  // checked MailException triggers rollback
    }
}
```

**Example 2 - Self-invocation pitfall and fix:**

```java
@Service
public class ReportService {

    // BAD: self-invocation - @Transactional on saveReport ignored!
    @Transactional
    public void generateAndSave(Long reportId) {
        Report report = generate(reportId);
        this.saveReport(report);  // 'this' = raw bean, not proxy!
    }

    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void saveReport(Report report) {
        reportRepo.save(report);  // REQUIRES_NEW never activates
    }

    // FIX 1: Inject self
    @Autowired private ReportService self;

    @Transactional
    public void generateAndSaveFix(Long reportId) {
        Report report = generate(reportId);
        self.saveReport(report);  // goes through proxy - REQUIRES_NEW works!
    }
}
```

---

### ⚖️ Comparison Table

| Propagation          | Behavior                                                    | Use Case                                    |
| -------------------- | ----------------------------------------------------------- | ------------------------------------------- |
| `REQUIRED` (default) | Join existing or create new                                 | Standard service methods                    |
| `REQUIRES_NEW`       | Always new transaction; suspend existing                    | Audit logging (must commit independently)   |
| `SUPPORTS`           | Join if exists; non-transactional if not                    | Optional transaction operations             |
| `NOT_SUPPORTED`      | Suspend existing; run non-transactionally                   | Avoid transaction for specific operation    |
| `MANDATORY`          | Must join existing; throw if none                           | Internal helpers that require a transaction |
| `NEVER`              | Must not be transactional; throw if transaction exists      | Non-transactional operations                |
| `NESTED`             | Nested savepoint within existing; partial rollback possible | Partial rollback scenarios                  |

---

### ⚠️ Common Misconceptions

| Misconception                               | Reality                                                                                                                                                     |
| ------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| @Transactional rolls back on ALL exceptions | Only RuntimeException and Error by default. Checked exceptions COMMIT by default unless specified in rollbackFor.                                           |
| @Transactional works on private methods     | No - AOP proxies can't intercept private methods. The annotation is silently ignored on private methods.                                                    |
| @Transactional on interface methods is fine | It works but is not recommended - the annotation may not be inherited correctly with certain proxy configurations. Put it on the implementation class.      |
| readOnly = true prevents all writes         | readOnly is a hint to the persistence provider - it doesn't enforce a read-only SQL transaction on all databases. Hibernate uses it to skip dirty checking. |

---

### 🚨 Failure Modes & Diagnosis

**Transaction not rolling back on checked exception**

**Symptom:** User saved to DB despite `MailException` being thrown from `createUser()`.

**Root Cause:** `MailException` is a checked exception (or a Spring's own `MailException` hierarchy). Default rollback only applies to `RuntimeException`.

**Fix:**

```java
@Transactional(rollbackFor = Exception.class)  // or specific: MailException.class
public void createUser(User user) throws MailException { ... }
```

---

**LazyInitializationException outside transaction**

**Symptom:** `LazyInitializationException: could not initialize proxy - no Session` when accessing a lazy-loaded collection.

**Root Cause:** The `@Transactional` method returned, the EntityManager/Session was closed. A caller outside the transaction tried to access a lazy collection on the returned entity.

**Fix:**

```java
// Option 1: Use EAGER loading for the specific query
@Query("SELECT u FROM User u JOIN FETCH u.orders WHERE u.id = :id")
Optional<User> findByIdWithOrders(@Param("id") Long id);

// Option 2: Extend transaction scope (Open Session in View - discouraged)
// Option 3: Use DTOs with all required data loaded within the transaction
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `AOP` - @Transactional is implemented as an AOP aspect (TransactionInterceptor)
- `CGLIB Proxy / JDK Dynamic Proxy` - the proxy mechanisms that implement @Transactional

**Builds On This (learn these next):**

- `Transaction Propagation` - the `propagation` attribute's full semantics
- `Transaction Isolation Levels` - the `isolation` attribute's database semantics
- `N+1 Problem` - a common JPA performance issue that appears within @Transactional contexts

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Declarative transaction management via    │
│              │ AOP - commit on success, rollback on      │
│              │ RuntimeException (by default)             │
├──────────────┼───────────────────────────────────────────┤
│ DEFAULT      │ propagation=REQUIRED, isolation=DEFAULT,  │
│ ATTRS        │ readOnly=false, rollback=RuntimeException  │
├──────────────┼───────────────────────────────────────────┤
│ KEY GOTCHAS  │ 1. Self-invocation bypasses proxy         │
│              │ 2. Checked exceptions don't rollback      │
│              │ 3. private methods ignored                │
│              │ 4. Thread-local: incompatible with @Async │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Zero boilerplate vs "magic" - must know   │
│              │ proxy mechanics to avoid surprises        │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Wrap this in a DB transaction - commit   │
│              │  on success, rollback on RuntimeException" │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** `@Transactional` stores transaction state in `ThreadLocal` variables. When a Spring `@Async` method is called from a `@Transactional` method, a new thread is created. The new thread has no `ThreadLocal` transaction state. What happens to the transaction? Does the `@Async` method's database operations run in the parent transaction, in their own transaction, or with no transaction? How would you propagate the transaction to the async thread if needed?

**Q2.** `@Transactional(readOnly = true)` is a hint to the persistence provider. For JPA with Hibernate, what specifically does `readOnly=true` change? Does it set a SQL-level read-only transaction on the connection? Does it affect dirty checking, snapshot caching, or flush mode? In a read-heavy application, what's the actual performance benefit?
