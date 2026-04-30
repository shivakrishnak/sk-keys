---
layout: default
title: "@Transactional"
parent: "Spring Core"
nav_order: 395
permalink: /spring/transactional/
number: "395"
category: Spring Core
difficulty: ★★★
depends_on: "Spring AOP, CGLIB Proxy, ACID, Bean Lifecycle, Transaction Propagation"
used_by: "Transaction Propagation, Isolation Levels, JPA, Spring Data, Rollback"
tags: #java, #spring, #springboot, #database, #advanced, #deep-dive
---

# 395 — @Transactional

`#java` `#spring` `#springboot` `#database` `#advanced` `#deep-dive`

⚡ TL;DR — Declarative transaction demarcation via Spring AOP — applied to a method or class, it wraps calls in begin/commit/rollback logic using a proxy, with behaviour controlled by propagation and isolation settings.

| #395 | category: Spring Core
|:---|:---|:---|
| **Depends on:** | Spring AOP, CGLIB Proxy, ACID, Bean Lifecycle, Transaction Propagation | |
| **Used by:** | Transaction Propagation, Isolation Levels, JPA, Spring Data, Rollback | |

---

### 📘 Textbook Definition

**`@Transactional`** is Spring's declarative transaction annotation. When applied to a public method (or class, applying to all public methods), `AbstractAutoProxyCreator` wraps the bean in a CGLIB or JDK proxy. At invocation time, `TransactionInterceptor` (Spring's `@Around` advice) calls `PlatformTransactionManager.getTransaction()` to begin a transaction, invokes the target method, and commits on normal return or rolls back on unchecked exceptions (and `Error`) by default. Rollback rules, propagation behaviour, isolation level, read-only hint, and timeout are configurable per annotation. Only works on public, non-final, non-private methods on Spring-managed beans invoked through the CGLIB/JDK proxy — self-invocation via `this.` bypasses the proxy entirely.

---

### 🟢 Simple Definition (Easy)

`@Transactional` means "run this method inside a database transaction." If it succeeds, Spring commits. If it throws a RuntimeException, Spring rolls back. You never write begin/commit/rollback code.

---

### 🔵 Simple Definition (Elaborated)

Without `@Transactional`, every individual database operation runs in its own mini-transaction — if step 2 of 3 fails, step 1's changes are already committed, leaving the database in a partial state. `@Transactional` puts all operations inside one transaction: all-or-nothing. Spring achieves this via a proxy that opens a transaction before calling your method and commits or rolls back after. The proxy stores the transaction context in a `ThreadLocal` so all JPA and JDBC operations in the same thread automatically join the same transaction without you passing a `Connection` object around.

---

### 🔩 First Principles Explanation

**The atomicity problem without @Transactional:**

```java
// BAD: three ops, each in its own auto-committed transaction
public void transferFunds(long from, long to, BigDecimal amount) {
  Account src = accountRepo.findById(from).orElseThrow();
  src.debit(amount);
  accountRepo.save(src);  // TX1 committed immediately

  // Application crashes here (disk full, OOM, etc.)

  Account dst = accountRepo.findById(to).orElseThrow();
  dst.credit(amount);
  accountRepo.save(dst);  // TX2 never runs
  // Money lost: debited source, never credited destination
}

// GOOD: entire method is one atomic transaction
@Transactional
public void transferFunds(long from, long to, BigDecimal amount) {
  Account src = accountRepo.findById(from).orElseThrow();
  src.debit(amount);
  Account dst = accountRepo.findById(to).orElseThrow();
  dst.credit(amount);
  // Both saves happen, or neither does
}
```

**How the proxy implements this — ThreadLocal binding:**

```
┌──────────────────────────────────────────────────────┐
│  @TRANSACTIONAL PROXY CHAIN                          │
│                                                      │
│  1. TransactionInterceptor.invoke()                  │
│  2. txManager.getTransaction(txDef)                  │
│     → obtains Connection from HikariCP pool          │
│     → binds Connection to ThreadLocal                │
│  3. pjp.proceed() → your real method runs            │
│     → JPA EntityManager uses ThreadLocal connection  │
│     → all SQL runs on same connection/transaction    │
│  4. On normal return: txManager.commit()             │
│  5. On RuntimeException/Error: txManager.rollback()  │
│  6. Connection returned to pool                      │
│  7. ThreadLocal binding cleared                      │
└──────────────────────────────────────────────────────┘
```

---

### ❓ Why Does This Exist (Why Before What)

**WITHOUT @Transactional:**

```
Without declarative transactions:

  Every service method needs:
    Connection conn = pool.getConnection();
    conn.setAutoCommit(false);
    try {
      executeStep1(conn);
      executeStep2(conn);
      conn.commit();
    } catch (Exception e) {
      conn.rollback();
      throw e;
    } finally {
      conn.close();
    }
  → Every method: ~12 lines of boilerplate
  → 100 transactional methods = 1200 lines of boilerplate
  → Forget rollback → data corruption
  → Different isolation per method = complex manual code
```

**WITH @Transactional:**

```
→ Add @Transactional → Spring handles all boilerplate
→ Atomicity guaranteed by proxy
→ Exception handler is the proxy — never forgotten
→ Connection managed automatically from HikariCP pool
→ ThreadLocal binding — no passing Connection around
→ readOnly=true hint → DB can optimise read-only ops
→ Propagation control: REQUIRED, REQUIRES_NEW, etc.
→ Rollback rules: specify which exceptions trigger rollback
```

---

### 🧠 Mental Model / Analogy

> `@Transactional` is like **booking a multi-leg flight itinerary**. You book all legs as one booking (transaction). If leg 2 (connecting flight) is cancelled, the whole booking gets refunded (rolled back) — you don't get stranded with a one-way ticket to Frankfurt. The airline's booking system (Spring's TransactionInterceptor) handles all the "open booking → confirm all legs → close booking" logic. You just say "I want all-or-nothing."

"Multi-leg booking" = @Transactional wrapping multiple DB operations
"All legs confirmed or none" = commit vs rollback
"Airline's booking system" = TransactionInterceptor
"Cancellation policy" = rollback rules (which exceptions trigger rollback)
"Open booking / close booking" = begin transaction / commit transaction

---

### ⚙️ How It Works (Mechanism)

**Rollback rules — critical defaults:**

```java
@Transactional
public void process() throws Exception {
  // DEFAULT rollback rules:
  // RuntimeException → ROLLBACK  (unchecked)
  // Error            → ROLLBACK
  // Exception        → COMMIT!   (checked — no rollback!)
  // ← SURPRISE: checked exceptions commit by default!
}

// Override with explicit rollback rules:
@Transactional(rollbackFor = Exception.class)
public void process() throws Exception { ... }
// Rolls back on ALL exceptions including checked

@Transactional(noRollbackFor = OptimisticLockException.class)
public void process() {
  // Rolls back on everything EXCEPT OptimisticLockException
}
```

**Key attributes:**

```java
@Transactional(
  propagation  = Propagation.REQUIRED,      // default
  isolation    = Isolation.READ_COMMITTED,  // default (DB-specific)
  readOnly     = false,                     // default
  timeout      = 30,                        // seconds
  rollbackFor  = {Exception.class},
  noRollbackFor = {ItemNotFoundException.class}
)
```

**`readOnly = true` — what it actually does:**

```java
@Transactional(readOnly = true)
public List<Order> findActiveOrders() {
  return orderRepo.findByStatus(ACTIVE);
}
// readOnly=true:
// → Hint to JPA: skip dirty-checking (performance win)
// → Hint to DB driver: may route to read replica
// → Hibernate: flushMode = NEVER (no flush before query)
// → PostgreSQL: START TRANSACTION READ ONLY
// NOT a guarantee: writes can still succeed in some DBs
```

---

### 🔄 How It Connects (Mini-Map)

```
Spring AOP (118) creates CGLIB proxy at startup
        ↓
  @TRANSACTIONAL (127)  ← you are here
  TransactionInterceptor (@Around advice)
        ↓
  PlatformTransactionManager.getTransaction()
  (DataSourceTransactionManager / JpaTransactionManager)
        ↓
  Connection bound to ThreadLocal
  (TransactionSynchronizationManager)
        ↓
  JPA / JDBC operations use same connection
        ↓
  Transaction Propagation (128):
  REQUIRED / REQUIRES_NEW / SUPPORTS / NOT_SUPPORTED
        ↓
  Transaction Isolation (129):
  READ_COMMITTED / REPEATABLE_READ / SERIALIZABLE
```

---

### 💻 Code Example

**Example 1 — Self-invocation bypasses proxy:**

```java
@Service
public class OrderService {
  @Transactional
  public void processAll(List<OrderRequest> requests) {
    for (OrderRequest req : requests) {
      this.place(req); // BYPASSES PROXY — no transaction!
    }
  }

  @Transactional(propagation = REQUIRES_NEW)
  public Order place(OrderRequest req) {
    return orderRepo.save(Order.from(req));
    // REQUIRES_NEW never fires — not called via proxy
  }
}

// FIX: inject self-reference to call through proxy
@Service
public class OrderService {
  @Autowired @Lazy OrderService self;

  public void processAll(List<OrderRequest> requests) {
    requests.forEach(req -> self.place(req)); // via proxy!
  }
}
```

**Example 2 — Checked exception silently commits:**

```java
// SILENT BUG: checked exception commits partial work
@Transactional
public void importUsers(List<UserDto> users)
    throws CsvParseException {
  for (UserDto dto : users) {
    User user = mapper.toEntity(dto);
    userRepo.save(user); // 50 users saved so far...
    if (dto.isInvalid()) {
      throw new CsvParseException("Row " + dto.row());
      // throws checked exception → COMMITS the 50 saves!
    }
  }
}

// FIX: declare rollbackFor
@Transactional(rollbackFor = CsvParseException.class)
public void importUsers(...)
    throws CsvParseException { ... }
```

**Example 3 — JPA dirty-check flush timing:**

```java
@Transactional
public void updateAndAudit(long id, String newName) {
  User user = userRepo.findById(id).orElseThrow();
  user.setName(newName);        // marks entity dirty
  // No explicit save() needed — JPA tracks changes

  auditRepo.save(new AuditEntry(id, "name changed"));
  // Dirty-check flush happens at transaction COMMIT
  // BOTH operations in one transaction → atomicity
}
// If you had @Transactional(readOnly=true):
// → Hibernate sets flushMode=NEVER
// → user.setName() change NEVER flushed
// → Silent data loss — never saved to DB
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| @Transactional rolls back on any exception | Default rollback only on RuntimeException and Error. Checked exceptions (Exception subtypes) commit by default — use rollbackFor to override |
| @Transactional on a private method works | Spring AOP proxy cannot intercept private methods — @Transactional on private methods is silently ignored with no warning |
| @Transactional(readOnly=true) prevents writes | readOnly is a performance hint to JPA and the DB driver. Writes can still physically execute in some configurations |
| Adding @Transactional to repository interfaces is wrong | Spring Data repository methods are already @Transactional (CRUD operations). You only need to add it to service methods that span multiple repository operations |

---

### 🔥 Pitfalls in Production

**1. Long transactions holding DB connections under load**

```java
// BAD: @Transactional on a method that does external I/O
@Transactional
public Order processWithPayment(OrderRequest req) {
  Order order = orderRepo.save(Order.from(req));
  // DB connection held while waiting for Stripe (200ms!)
  Receipt receipt = stripeClient.charge(req.getPayment());
  order.setReceiptId(receipt.getId());
  return orderRepo.save(order);
}
// At 100 RPS: 100 connections × 200ms = pool exhaustion!

// GOOD: transaction only around DB operations
public Order processWithPayment(OrderRequest req) {
  Order order = orderService.saveInitialOrder(req); // TX 1
  Receipt receipt = stripeClient.charge(req.getPayment());
  return orderService.updateReceipt(order, receipt); // TX 2
}

@Transactional
Order saveInitialOrder(OrderRequest req) {
  return orderRepo.save(Order.from(req));
}
```

**2. LazyInitializationException after transaction end**

```java
@Transactional
public Order findWithItems(long id) {
  Order order = orderRepo.findById(id).orElseThrow();
  // items are LAZY — proxy reference, not loaded yet
  return order;
}
// Transaction commits here — Session closed!

// CALLER (outside transaction):
List<Item> items = order.getItems();
// LazyInitializationException: no Session!

// FIX option 1: Fetch join in query
@Query("SELECT o FROM Order o LEFT JOIN FETCH o.items WHERE o.id=?1")
Optional<Order> findWithItemsById(long id);

// FIX option 2: DTO projection
// FIX option 3: @Transactional on the CALLER (parent TX)
```

---

### 🔗 Related Keywords

- `Spring AOP` — @Transactional is powered by a BPP-created proxy
- `Transaction Propagation` — how nested @Transactional calls interact
- `Transaction Isolation Levels` — controls visibility of concurrent changes
- `HikariCP` — the connection pool that provides the database connection
- `JPA / Hibernate` — the persistence layer that uses the transaction-bound connection
- `PlatformTransactionManager` — the Spring interface abstracting DB transactions

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Declarative begin/commit/rollback via AOP │
│              │ proxy; ThreadLocal binds connection to    │
│              │ current thread                            │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Service methods spanning multiple DB ops; │
│              │ readOnly=true for read-heavy query methods │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Long transactions with external I/O;      │
│              │ private methods; self-invocation via this.│
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "All legs confirmed or all refunded —     │
│              │  the proxy handles the booking system."   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Transaction Propagation (128) →           │
│              │ Transaction Isolation Levels (129)        │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A `@Transactional` service method calls a `@Transactional(propagation = REQUIRES_NEW)` method on ANOTHER service bean (not self-invocation). The outer transaction is open. Explain step-by-step what `JpaTransactionManager` does: does it suspend the outer transaction, open a new JDBC connection, or reuse the same connection with a savepoint? Describe the exact ThreadLocal state during the inner method execution and what happens to the outer transaction if the inner method throws and rolls back.

**Q2.** Spring's `@Transactional(readOnly = true)` sets Hibernate's `FlushMode` to `MANUAL` (never flush dirty changes). A developer writes a method annotated `@Transactional(readOnly = true)` that loads an entity, modifies it, and calls `entityManager.flush()` explicitly. Explain what happens: does the explicit flush succeed, fail silently, or throw an exception — and why the `readOnly` flag does NOT prevent writes at the SQL level in most databases. Then describe the specific case where `readOnly=true` routed to a PostgreSQL read-replica does throw an error, and how to fix the routing logic.

