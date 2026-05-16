---
id: JPH-026
title: "@Transactional with JPA"
category: JPA & Hibernate
tier: tier-3-java
folder: JPH-jpa-hibernate
difficulty: ★★☆
depends_on: JPH-011, JPH-012, JPH-013, JPH-021, JPH-022
used_by: JPH-027, JPH-033, JPH-038, JPH-039, JPH-045, JPH-052
related: JPH-031, JPH-048
tags:
  - java
  - jpa
  - database
  - intermediate
status: complete
version: 4
layout: default
parent: "JPA & Hibernate"
grand_parent: "Technical Dictionary"
nav_order: 26
permalink: /jpa-hibernate/transactional-with-jpa/
---

# JPH-026 - @Transactional with JPA

⚡ **TL;DR** - `@Transactional` on a Spring service method
binds one EntityManager (persistence context) to the
thread for that method's duration. All JPA reads and
writes within that method join the same transaction.
On method exit: flush (SQL to DB) + commit. On exception:
rollback. Without `@Transactional`, every JPA operation
in a Spring Data repository uses its own tiny transaction
(read is auto-transactional; write requires explicit tx).

| #026            | Category: JPA & Hibernate                                                                                 | Difficulty: ★★☆ |
| :-------------- | :-------------------------------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | EntityManager, Persistence Context, Entity Lifecycle, FetchType, CascadeType                              |                 |
| **Used by:**    | N+1 Problem, First Level Cache, Optimistic Locking, Pessimistic Locking, Batch Processing, Dirty Checking |                 |
| **Related:**    | Hibernate Session vs EntityManager, Multi-Tenancy                                                         |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Without `@Transactional`, each Spring Data repository
call opens its own connection from the pool, begins a
transaction, executes one SQL statement, and closes.
A service method calling `order.setStatus("PAID")` +
`inventory.decreaseStock(itemId, qty)` runs in 2 separate
transactions. If the inventory update fails, the order
status is already committed. The system is inconsistent.

**THE BREAKING POINT:**
E-commerce checkout: deduct stock, record order, charge
payment, send confirmation. Each is a separate repository
call. If payment fails after stock deduction, stock is
gone but money was not charged. Without wrapping all
4 operations in one transaction, partial failures create
phantom orders, incorrect inventory, and financial
discrepancies.

**THE INVENTION MOMENT:**
`@Transactional` on the service method tells Spring:
"Open one transaction before this method; close it
(commit) when the method returns normally; roll it back
if the method throws a runtime exception. Bind one
EntityManager to this transaction for the duration."
All repository calls within this method share the same
connection and rollback as a unit if anything fails.

---

### 📘 Textbook Definition

**`@Transactional`** is a Spring AOP annotation that
wraps the annotated method in a transactional proxy.
When the method is called through a Spring bean
reference (proxied call), Spring opens a transaction
before the method body begins and commits or rolls it
back after the method body completes.

**Transaction Propagation** controls what happens when
a `@Transactional` method calls another `@Transactional`
method. Default is `REQUIRED`: join an existing transaction
if one is active, otherwise start a new one.

**Rollback Rules** control when Spring rolls back:
by default, only unchecked exceptions (`RuntimeException`
and subclasses) cause rollback. Checked exceptions do
NOT cause rollback unless explicitly declared with
`rollbackFor = Exception.class`.

**Read-Only Transactions** (`@Transactional(readOnly = true)`)
hint to Hibernate to skip dirty checking (no entity state
comparison at flush time) and hint to the JDBC driver/
database to use a read replica or disable write locks.

---

### ⏱️ Understand It in 30 Seconds

**One line:** `@Transactional` on a service method wraps
all JPA calls in one database transaction - all succeed
or all roll back.

**One analogy:**

> A transaction is like a Google Doc batch save. You make
> 10 edits (add paragraph, delete heading, change font).
> Until you click "Save", none of the changes are committed.
> `@Transactional` is the mechanism that says: "All JPA
> operations in this method are one batch save. If any
> edit fails, revert all edits. Only save all edits when
> the method exits normally."

**One insight:** Spring's `@Transactional` is a proxy
wrapper - it only works when the method is called through
the Spring bean (external call). Calling a `@Transactional`
method from WITHIN THE SAME CLASS bypasses the proxy
and runs without a transaction. This is the single most
common `@Transactional` bug in production code.

---

### 🔩 First Principles Explanation

**WHAT SPRING DOES WHEN @Transactional IS HIT:**

```
1. Spring AOP proxy intercepts the call
2. TransactionManager calls DataSource.getConnection()
3. Sets connection.setAutoCommit(false)
4. Stores connection in ThreadLocal (TransactionSynchronizationManager)
5. Calls the actual method
6. All EntityManager operations within the method use this
   same connection (via the ThreadLocal-bound transaction)
7. On normal exit: session.flush() -> commit()
8. On RuntimeException: rollback()
9. Return connection to pool
```

**PROPAGATION TYPES:**

```
REQUIRED (default):
  - Join existing tx if active, else start new
  - Most common; use for most service methods

REQUIRES_NEW:
  - Always start a NEW transaction
  - Suspend any existing transaction
  - Use for: audit log that must commit even if
    outer tx rolls back

SUPPORTS:
  - Join tx if active; no tx if not
  - Use for: query methods that can run either way

NOT_SUPPORTED:
  - Suspend tx if active; run without tx
  - Use for: calling legacy code that breaks in a tx

MANDATORY:
  - Caller MUST have an active tx; error if not
  - Use for: methods that must always be called
    within a transaction

NEVER:
  - Error if called within a transaction
  - Use for: operations that must be non-transactional

NESTED:
  - Run within a nested tx (savepoint) if parent tx exists
  - Rollback of nested doesn't roll back parent
  - JPA does not support savepoints; JDBC only
```

---

### 🧪 Thought Experiment

**THE SELF-INVOCATION TRAP:**

```java
@Service
public class OrderService {

    // BAD: calling @Transactional from same class
    public void processOrder(Long id) {
        // NOT proxied! No transaction opened.
        sendConfirmation(id);
    }

    @Transactional  // annotation is IGNORED
    public void sendConfirmation(Long id) {
        order.setStatus("CONFIRMED");
        // Dirty check runs but no active tx -> exception
    }
}
```

**WHY IT FAILS:** Spring's `@Transactional` uses JDK
dynamic proxies or CGLIB proxies. The proxy wraps the
bean. When external code calls `orderService.processOrder()`,
the PROXY is called first, sees `processOrder` has no
`@Transactional`, and delegates to the real method.
Inside `processOrder`, `this.sendConfirmation()` is a
direct method call on the actual object - it bypasses the
proxy entirely. The `@Transactional` on `sendConfirmation`
is never processed.

**THE FIX - 3 APPROACHES:**

1. Move `sendConfirmation()` to a separate `@Service` bean
2. Inject the service into itself via `@Autowired private OrderService self;` then `self.sendConfirmation(id)`
3. Use `AopContext.currentProxy()` (fragile; avoid in new code)
4. Use `@Transactional` on `processOrder()` instead

---

### 🧠 Mental Model / Analogy

> `@Transactional` is like a bank teller's session. When
> you step up to the window (enter the method), the teller
> opens a ledger (connection/transaction). Every account
> change you request (JPA operations) is recorded in
> the ledger. When you step away (method returns), the
> teller finalizes the ledger (commit). If you demand
> something impossible (exception), the teller shreds
> the ledger (rollback) - all changes disappear.
>
> The self-invocation trap: imagine the teller talks to
> themselves. The second request never reaches the
> teller at the window - it's handled internally without
> a new ledger session.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
`@Transactional` groups multiple database operations
into one unit. Either all succeed or all are undone.
Put it on a service method that does multiple related
database changes.

**Level 2 - How to use it (junior developer):**
Put `@Transactional` on service methods that modify data.
For read-only queries, use `@Transactional(readOnly = true)`.
By default, `RuntimeException` causes rollback; checked
exceptions do not.

**Level 3 - How it works (mid-level engineer):**
Spring AOP proxy intercepts the method call. It binds
an EntityManager and database connection to the thread
via `ThreadLocal`. On normal exit, `EntityManager.flush()`
is called (SQL sent to DB) then `commit()`. On
`RuntimeException`, `rollback()` is called instead.
The self-invocation bypass means `@Transactional`
methods calling themselves don't get a transaction.

**Level 4 - Why it was designed this way (senior/staff):**
`@Transactional` uses the interceptor (AOP) pattern to
separate transaction management concerns from business
logic. The `TransactionSynchronizationManager` uses
`ThreadLocal` to associate resources with the current
thread, allowing any code in the call stack to
participate in the same transaction transparently.
This enables the Spring template pattern: `JdbcTemplate`,
`EntityManager`, etc. all look up the thread-bound
connection and join the active transaction automatically.

**Level 5 - Mastery (distinguished engineer):**
For microservices with distributed transactions, `@Transactional`
only covers a single datasource. The Saga pattern (with
compensating transactions) or CQRS with eventual
consistency replaces XA/2PC for distributed scenarios.
When using `REQUIRES_NEW` for audit logging, be aware
that the new transaction opens a new connection from
the pool - under high load, this can exhaust the
connection pool if the parent transaction is long-lived.
For read-heavy services, `@Transactional(readOnly = true)`
should be the default on all query methods; Hibernate
skips dirty checking (EntityState comparison), saving
CPU proportional to the number of loaded entities.

---

### ⚙️ How It Works (Mechanism)

**FLUSH MODES AND WHEN SQL IS SENT:**

```
FlushMode.AUTO (default):
  - Hibernate flushes before executing a query that
    could be affected by pending changes
  - Flushes at @Transactional method exit (commit)

FlushMode.COMMIT:
  - Hibernate only flushes at commit time
  - Reads within the tx may not see pending writes
  - Useful for batch operations (reduces intermediate
    flushes)

FlushMode.MANUAL:
  - Never auto-flush; developer calls em.flush() manually
  - Use for read-only transactions that never modify data
  - Slightly faster for complex queries

FlushMode.ALWAYS:
  - Flush before every query
  - Safest but most expensive
  - Useful in testing to ensure consistency
```

**READOLY TRANSACTION OPTIMIZATIONS:**

```java
@Transactional(readOnly = true)
public List<ProductDto> findAll() {
    // Hibernate skips dirty checking:
    // - No EntityState snapshot comparison on flush
    // - Entities are in "read-only" mode in 1L cache
    // Database: may hint to use read replica
    // HikariCP: connection may be routed to read pool
    //           (with AbstractRoutingDataSource setup)
}
```

---

### 🔄 The Complete Picture - End-to-End Flow

**FULL TRANSACTIONAL METHOD LIFECYCLE:**

```java
@Service
@Transactional  // class-level: applies to all public methods
public class OrderService {

    private final OrderRepository orderRepo;
    private final InventoryRepository inventoryRepo;

    // 1. Spring proxy intercepts call
    // 2. Opens connection from HikariCP pool
    // 3. Sets autoCommit=false
    // 4. Binds EntityManager to thread
    public OrderConfirmation checkout(CartDto cart) {

        // 5. All JPA ops share the same tx/connection:
        Order order = new Order(cart);
        orderRepo.save(order);         // INSERT queued
        inventoryRepo.deduct(cart);    // UPDATE queued

        // 6. Validation: throws RuntimeException
        if (order.getTotal().compareTo(MAX) > 0) {
            throw new OrderLimitException("...");
            // -> ROLLBACK: INSERT and UPDATE undone
        }

        // 7. Normal exit:
        // EntityManager.flush() -> INSERT+UPDATE sent to DB
        // connection.commit()
        // EntityManager closed, connection returned to pool
        return new OrderConfirmation(order.getId());
    }
}
```

---

### 💻 Code Example

**Example 1 - BAD: no transaction on multi-step write:**

```java
// BAD: each repo call is its own transaction
@Service
public class TransferService {
    public void transfer(Long from, Long to, BigDecimal amt) {
        accountRepo.debit(from, amt);   // tx1: committed
        accountRepo.credit(to, amt);    // tx2: may fail
        // If credit fails: debit committed, credit not
        // -> money lost!
    }
}

// GOOD: both operations in one transaction
@Service
public class TransferService {
    @Transactional
    public void transfer(Long from, Long to,
                         BigDecimal amt) {
        accountRepo.debit(from, amt);
        accountRepo.credit(to, amt);
        // If credit fails: BOTH rolled back
    }
}
```

**Example 2 - BAD: self-invocation bypasses transaction:**

```java
// BAD: self-invocation
@Service
public class AuditService {
    public void doWork() {
        // 'this.saveAudit' bypasses proxy -> no tx
        this.saveAudit("work started");
    }

    @Transactional
    public void saveAudit(String msg) {
        auditRepo.save(new AuditLog(msg));
        // No transaction -> may fail silently or throw
    }
}

// GOOD: inject self or refactor to separate bean
@Service
public class AuditService {
    @Autowired
    private AuditService self;  // proxy-injected self

    public void doWork() {
        self.saveAudit("work started");  // goes through proxy
    }

    @Transactional
    public void saveAudit(String msg) {
        auditRepo.save(new AuditLog(msg));
    }
}
```

**Example 3 - REQUIRES_NEW for audit log:**

```java
@Service
public class AuditWriter {

    // Always commits, even if caller rolls back:
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void writeAudit(String action, Long userId) {
        auditRepo.save(new AuditLog(action, userId));
        // Opens NEW connection; commits independently
        // Parent rollback does NOT undo this
    }
}

@Service
public class OrderService {
    @Transactional
    public void cancelOrder(Long id) {
        orderRepo.delete(id);
        auditWriter.writeAudit("CANCEL", currentUser);
        // If deleteOrder fails and rolls back,
        // audit log is STILL committed (REQUIRES_NEW)
    }
}
```

**Example 4 - rollbackFor for checked exceptions:**

```java
// BAD: checked exception does NOT trigger rollback
@Transactional
public void process() throws IOException {
    repo.save(entity);
    throw new IOException("file missing");
    // -> IOException is CHECKED -> tx COMMITS!
    // Entity is saved despite the exception
}

// GOOD: explicit rollbackFor
@Transactional(rollbackFor = Exception.class)
public void process() throws IOException {
    repo.save(entity);
    throw new IOException("file missing");
    // -> rollbackFor = Exception covers IOException
    // -> ROLLBACK: entity save undone
}
```

---

### ⚖️ Comparison Table

| Aspect            | @Transactional          | No @Transactional          | REQUIRES_NEW                                |
| ----------------- | ----------------------- | -------------------------- | ------------------------------------------- |
| Transaction scope | Method duration         | Per-repo-call auto-tx      | New tx per method; parent suspended         |
| Rollback          | RuntimeException        | Auto per operation         | Independent; does not roll back with parent |
| Connection usage  | 1 connection for method | 1 connection per repo call | 2 connections (parent + new)                |
| readOnly hint     | Yes (skip dirty check)  | N/A                        | Yes (per method)                            |

---

### ⚠️ Common Misconceptions

| Misconception                                        | Reality                                                                                                                                                                                                                                            |
| ---------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "`@Transactional` can be placed on private methods"  | Spring's AOP proxy cannot intercept private methods. `@Transactional` on a private method is silently ignored. Methods must be public and called through the proxy (externally).                                                                   |
| "Checked exceptions automatically trigger rollback"  | Only unchecked exceptions (`RuntimeException`) trigger rollback by default. `IOException`, `SQLException` (checked) do NOT cause rollback. Use `rollbackFor = Exception.class` or catch and rethrow as `RuntimeException`.                         |
| "`@Transactional` on a class applies to all methods" | Class-level `@Transactional` applies to all PUBLIC methods of the class. Private and protected methods are not proxied. Method-level annotation overrides class-level.                                                                             |
| "readOnly=true prevents all writes"                  | `readOnly = true` is a hint to Hibernate (skip dirty checking) and the database driver. It does NOT enforce immutability. Hibernate will still execute INSERTs/UPDATEs if the code calls them. The hint is used for optimization, not enforcement. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Transaction Silently Not Applied (Self-Invocation)**

**Symptom:** Service method `A()` calls `B()` in the same
class. `B()` has `@Transactional` but changes are NOT
rolled back on exception, or `LazyInitializationException`
occurs inside `B()`.
**Root Cause:** `A()` is called through the Spring proxy,
but `A()` calls `this.B()` directly on the real object,
bypassing the proxy. The `@Transactional` on `B()` is never
processed.
**Diagnosis:** Check if the calling code is in the same
class as the `@Transactional` method.
**Fix:** Move `B()` to a separate `@Service` bean, or
annotate `A()` with `@Transactional` instead.

---

**Failure Mode 2: Checked Exception Does Not Roll Back**

**Symptom:** Service method throws `IOException`. The
application catches it and retries, but the partial data
written in the method is already committed to the database.
**Root Cause:** Spring default rollback rule only covers
`RuntimeException`. `IOException` is a checked exception
and commits the transaction.
**Diagnosis:** Check exception type. Add logging at the
`@Transactional` boundary to verify rollback.
**Fix:**

```java
@Transactional(rollbackFor = Exception.class)
public void processFile() throws IOException { ... }
```

---

**Failure Mode 3: LazyInitializationException Outside Transaction**

**Symptom:** `org.hibernate.LazyInitializationException:
could not initialize proxy - no Session` thrown in the
controller or DTO mapping layer after the service method
has returned.
**Root Cause:** Entity was loaded inside a `@Transactional`
service method. After method return, the persistence
context (and its session) was closed. The controller
accesses a lazy-loaded association that was not loaded
while the session was open.
**Fix Options:**

1. Fetch associations eagerly in the service query (JOIN FETCH)
2. Map entities to DTOs inside `@Transactional` (before context closes)
3. Use `@Transactional(readOnly = true)` on the controller (OEIV - anti-pattern)

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[JPH-011 - EntityManager]] - `@Transactional` manages
  the EntityManager lifecycle
- [[JPH-012 - Persistence Context]] - one persistence
  context is bound per transaction
- [[JPH-013 - Entity Lifecycle]] - transactions control
  when entities transition between states

**Builds On This (learn these next):**

- [[JPH-027 - N+1 Problem]] - N+1 occurs within a
  transaction when lazy loading fires N queries
- [[JPH-033 - First Level Cache]] - first-level cache is
  scoped to the persistence context / transaction
- [[JPH-038 - Optimistic Locking]] - version checks happen
  at flush time within the transaction

**Related:**

- [[JPH-052 - Dirty Checking and Flush Mode]] - flush mode
  controls when SQL is sent to DB within the transaction

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ BASIC USE    │ @Transactional on service method         │
│              │ (not repository, not controller)          │
├──────────────┼───────────────────────────────────────────┤
│ ROLLBACK     │ Default: RuntimeException only           │
│              │ Add: rollbackFor=Exception.class for all  │
├──────────────┼───────────────────────────────────────────┤
│ SELF-INVOKE  │ @Transactional ignored on same-class calls│
│              │ Use separate bean or annotate caller      │
├──────────────┼───────────────────────────────────────────┤
│ READ-ONLY    │ @Transactional(readOnly=true) on queries  │
│              │ Skips dirty check; hints read replica     │
├──────────────┼───────────────────────────────────────────┤
│ REQUIRES_NEW │ Independent tx; use for audit logs        │
│              │ Uses 2 connections from pool              │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "@Transactional wraps all JPA ops in one │
│              │ tx. Self-invocation bypasses proxy.       │
│              │ Rollback on RuntimeException by default." │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. `@Transactional` only works for calls through the
   Spring proxy - same-class `this.method()` calls bypass
   it silently
2. Default rollback: unchecked exceptions only. Add
   `rollbackFor = Exception.class` for checked exceptions
3. `readOnly = true` is a performance hint (skips dirty
   checking); use it for all query-only service methods

**Interview one-liner:** `@Transactional` binds one
EntityManager to the thread for the method duration -
all JPA ops share one transaction. Rollback on
`RuntimeException` by default (not checked exceptions).
Self-invocation bypasses the proxy and silently loses the
transaction. `readOnly=true` skips Hibernate dirty checking.
`REQUIRES_NEW` opens a second connection for an independent
transaction - useful for audit logs that commit regardless
of outer rollback.

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Transaction boundaries
define consistency units. Always place `@Transactional`
at the service layer (not repository layer or controller
layer). The service knows the business invariants that
must hold atomically. Repositories are single-operation;
controllers should not own persistence context lifetimes.
This principle (transaction at the service boundary) is
universal: Rails has `ActiveRecord.transaction {}`, Django
has `@transaction.atomic`, Go apps use explicit `db.Begin()`/
`db.Commit()` scopes, all serving the same purpose.

**Where else this pattern appears:**

- **Django** - `@transaction.atomic` decorator on views/
  service functions; same proxy/decorator pattern
- **Rails** - `ActiveRecord::Base.transaction do ... end`;
  same rollback-on-exception semantic
- **Go** - `tx, err := db.Begin(); defer tx.Rollback();`
  explicit transaction management (no annotation)
- **Database stored procedures** - `BEGIN TRANSACTION` /
  `COMMIT` / `ROLLBACK` - the same concept at SQL level

---

### 💡 The Surprising Truth

`@Transactional(readOnly = true)` does more than just hint
to the database. In Hibernate, it puts entities loaded in
that session into "read-only" mode: Hibernate does NOT
take a snapshot of their state for dirty checking. This
means: (1) Memory savings - no snapshot copy of every
field for every loaded entity. (2) CPU savings at flush
time - Hibernate skips comparing current state vs snapshot.
For a service method loading 1,000 entities for reporting,
`readOnly = true` can reduce memory usage by ~50% (no
snapshot copies) and eliminate the flush-time dirty check
CPU cost entirely. The database "hint" (using read replica)
is a bonus - the Hibernate optimization alone is worth it.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **EXPLAIN** why `@Transactional` on a private method
   or self-invoked method is silently ignored, and describe
   three fixes
2. **DIAGNOSE** a case where checked exception causes
   unexpected committed state, and write the correct
   `rollbackFor` annotation
3. **CHOOSE** between `REQUIRED`, `REQUIRES_NEW`, and
   `SUPPORTS` propagation for three different use cases
4. **DESIGN** a service class with correct class-level
   and method-level `@Transactional` annotations,
   including `readOnly = true` for query methods
5. **TRACE** the lifecycle of a transaction from proxy
   intercept through flush, commit, connection return

---

### 🎯 Interview Deep-Dive

**Q1: When does @Transactional NOT work, even though it
is annotated correctly?**
_Why they ask:_ Tests understanding of AOP proxy mechanics

- a critical Spring gotcha.
  _Strong answer includes:_
- Self-invocation: `this.method()` bypasses the proxy
- Private methods: proxy cannot intercept; annotation
  silently ignored
- Non-Spring-managed beans: `@Transactional` requires
  the bean to be in the Spring context
- Class is `final` with JDK proxy (CGLIB handles final;
  JDK proxy requires interface)
- Thread spawned inside a `@Transactional` method: new
  thread has no transaction (ThreadLocal is not inherited)

**Q2: What is the difference between @Transactional
readOnly=true and readOnly=false in terms of what Hibernate
does?**
_Why they ask:_ Tests depth of Hibernate internals
knowledge beyond basic usage.
_Strong answer includes:_

- `readOnly = false` (default): Hibernate takes a snapshot
  of every loaded entity for dirty checking at flush time
- `readOnly = true`: Hibernate skips entity snapshots;
  entities are loaded in "read-only" mode
- Performance impact: for large result sets, skipping
  snapshots can halve memory usage and eliminate CPU cost
  of dirty checking
- Does NOT enforce immutability: JPA operations still work
- Also hints to database driver/connection pool to route
  to read replica (with `AbstractRoutingDataSource`)

**Q3: How do you handle a scenario where you need a
database audit log entry to persist even if the main
business transaction rolls back?**
_Why they ask:_ Tests knowledge of transaction propagation
and a common architectural requirement.
_Strong answer includes:_

- Use `REQUIRES_NEW` on the audit writing method
- This suspends the outer transaction, opens a new
  connection, and commits the audit entry independently
- Outer rollback does NOT affect the REQUIRES_NEW tx
- Caveat: REQUIRES_NEW uses a second connection from the
  pool; under high concurrency this can cause pool exhaustion
  if parent transactions are long-lived
- Alternative: publish an application event (e.g.,
  `ApplicationEventPublisher`) that writes audit after
  the outer transaction commits (`@TransactionalEventListener`
  with `AFTER_COMMIT` phase)
