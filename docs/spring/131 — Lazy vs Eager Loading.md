---
layout: default
title: "Lazy vs Eager Loading"
parent: "Spring & Spring Boot"
nav_order: 131
permalink: /spring/lazy-vs-eager-loading/
number: "131"
category: Spring & Spring Boot
difficulty: ★★☆
depends_on: "JPA, Hibernate, N+1 Problem, @Transactional, Session"
used_by: "N+1 fixes, @EntityGraph, OSIV, LazyInitializationException"
tags: #java, #spring, #database, #intermediate, #performance
---

# 131 — Lazy vs Eager Loading

`#java` `#spring` `#database` `#intermediate` `#performance`

⚡ TL;DR — Lazy loading defers fetching associations until they are accessed; eager loading fetches them immediately with the parent — each is optimal for different access patterns.

| #131 | Category: Spring & Spring Boot | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | JPA, Hibernate, N+1 Problem, @Transactional, Session | |
| **Used by:** | N+1 fixes, @EntityGraph, OSIV, LazyInitializationException | |

---

### 📘 Textbook Definition

In JPA/Hibernate, **fetch type** controls when associated entities are loaded from the database. `FetchType.LAZY` (default for `@OneToMany`, `@ManyToMany`) generates a proxy for the association; the SQL is issued only when the association is first accessed. `FetchType.EAGER` (default for `@ManyToOne`, `@OneToOne`) joins the association in the same query that loads the owning entity. LAZY prevents loading unnecessary data for operations that don't use the association. EAGER guarantees the association is always available but forces joins regardless of whether the data is needed. Both defaults are JPA specification defaults; Hibernate may deviate from the spec in some implementations.

---

### 🟢 Simple Definition (Easy)

Lazy: "Don't load a customer's orders until I actually ask for them." Eager: "Every time I load a customer, immediately load all their orders too." Lazy saves work; Eager guarantees availability.

---

### 🔵 Simple Definition (Elaborated)

JPA maps Java object relationships to SQL joins. When you load an `Order`, it has related `Customer`, `Items`, and `Payments`. You don't always need all of them. LAZY loading defers fetching related data to when you first access the field — `order.getItems()` — triggering a SQL at that point. EAGER loading fetches everything when the parent loads, even if you never access it. The JPA defaults (LAZY for collections, EAGER for single associations) are a practical compromise, but the right choice depends on your access patterns. The wrong choice in either direction causes either `LazyInitializationException` (LAZY accessed outside session) or N+1 queries (LAZY in a loop).

---

### 🔩 First Principles Explanation

**JPA defaults and their rationale:**

```
FetchType defaults (JPA spec):
  @ManyToOne   → EAGER  (one linked entity — safe to join)
  @OneToOne    → EAGER  (one linked entity — safe to join)
  @OneToMany   → LAZY   (collection — could be huge, don't join)
  @ManyToMany  → LAZY   (collection — could be huge, don't join)

Why collections default to LAZY:
  Order has 0-10,000 items
  Eagerly joining items when loading orders:
    SELECT * FROM orders JOIN items ON order_id
    → Returns 10,000 rows for an order with 10,000 items
    → Even if you only need the order's status field

Why single associations default to EAGER:
  Order has exactly 1 customer
  Eagerly joining customer: +1 row — negligible cost
  Lazily loading customer: +1 query per access — adds up
```

**The two failure modes:**

```
LAZY accessed outside Hibernate session:
  @Transactional ends → Session closes
  Later code accesses lazy proxy:
  → LazyInitializationException
  (Hibernate session is closed — cannot load)

EAGER on collection in a list query:
  "Load all orders" → JOIN items for each order
  1000 orders × 100 items = 100,000 row result set
  → Memory spike
  → Cartesian product if multiple collections EAGERed
```

---

### ❓ Why Does This Exist (Why Before What)

**Without configurable fetch types:**

```
Always EAGER:
  Load 1 order → load all 10,000 items immediately
  SELECT 1 order needed → 10,000 rows returned
  10× memory usage for a status-check endpoint

Always LAZY:
  Every access to any relationship = extra query
  Accessing customer.getName() = SELECT FROM customers
  Works fine, but predictable in performance terms

With configurable fetch types:
  LAZY default: don't load what you don't need
  EAGER override: always need this, join it
  @EntityGraph: fetch specific associations per query
  → Flexibility to optimise per use case
```

---

### 🧠 Mental Model / Analogy

> Lazy loading is like **ordering à la carte** — you only order each dish when you're ready for it, avoiding waste. Eager loading is like the **prix fixe menu** — you get every course automatically, even if you don't eat the salad. Lazy is better when you often skip courses; eager is better when you always eat everything and want it all at once. `LazyInitializationException` is the restaurant closing before you ordered dessert — the session (kitchen) is shut.

"À la carte ordering" = lazy loading (on demand)
"Prix fixe menu" = eager loading (everything upfront)
"Skipping some courses" = not always needing all associations
"Restaurant closing" = Hibernate session closing (end of @Transactional)
"Ordering dessert after closing" = LazyInitializationException

---

### ⚙️ How It Works (Mechanism)

**Fetch type in entity mapping:**

```java
@Entity
public class Order {
  @Id
  Long id;

  // EAGER (default for @ManyToOne) — joined always
  @ManyToOne(fetch = FetchType.EAGER)
  @JoinColumn(name = "customer_id")
  Customer customer;

  // LAZY (default for @OneToMany) — loaded on access
  @OneToMany(mappedBy = "order", fetch = FetchType.LAZY)
  List<Item> items;

  // Override: force EAGER on collection (usually a mistake)
  // @OneToMany(mappedBy = "order", fetch = FetchType.EAGER)
  // ↑ Never do this for collections — Cartesian product risk
}
```

**LAZY proxy under the hood:**

```
When Hibernate loads an Order:
  items field = Hibernate PersistentBag proxy (not null)
  proxy knows: order_id=42, associations not loaded yet

When you call order.getItems():
  proxy checks: is Hibernate session still open?
    YES → execute: SELECT * FROM items WHERE order_id=42
    NO  → throw LazyInitializationException
```

**Open Session in View (OSIV) — the controversial "fix":**

```
spring.jpa.open-in-view=true (Spring Boot DEFAULT until 2.x)

OSIV: keeps Hibernate session open for the entire
HTTP request lifecycle (even after @Transactional ends)
→ Lazy loading works from controller, view template, etc.
→ BUT: holds DB connection entire request duration
→ At 100 RPS: 100 connections held during entire response
→ Kills performance under load

spring.jpa.open-in-view=false (recommended)
→ LazyInitializationException exposed explicitly
→ Forces proper fetch strategy in service layer
→ Connections released when @Transactional ends
```

---

### 🔄 How It Connects (Mini-Map)

```
@OneToMany(fetch = LAZY) → association = proxy
        ↓
  Access proxy inside @Transactional → SQL fired
        ↓
  Access proxy OUTSIDE @Transactional
  → LAZY VS EAGER LOADING (131)  ← you are here
  → LazyInitializationException (session closed)
        ↓
  Fixes:
  @EntityGraph / JOIN FETCH → fetch in query
  N+1 Problem (130) if lazy in a loop
  OSIV (controversial) → keep session open
  DTO Projection → no entity loading at all
```

---

### 💻 Code Example

**Example 1 — LazyInitializationException and fixes:**

```java
// SERVICE (transaction ends after return)
@Transactional(readOnly = true)
public Order findOrder(long id) {
  return orderRepo.findById(id).orElseThrow();
  // Transaction ends here — session closed
}

// CONTROLLER (outside transaction)
public OrderDto getOrder(@PathVariable long id) {
  Order order = orderService.findOrder(id);
  // LAZY association accessed outside session:
  order.getItems().size(); // LazyInitializationException!
}

// FIX 1: fetch in the service (inside transaction)
@Transactional(readOnly = true)
public OrderWithItemsDto findOrderWithItems(long id) {
  Order order = orderRepo.findWithItems(id); // JOIN FETCH
  return OrderWithItemsDto.from(order);
  // DTO built inside TX — no lazy access outside
}

// FIX 2: @EntityGraph in repository
@EntityGraph(attributePaths = {"items"})
Optional<Order> findById(Long id);
```

**Example 2 — OSIV false vs true comparison:**

```yaml
# application.yml

# BAD (default in older Spring Boot): OSIV enabled
spring:
  jpa:
    open-in-view: true
# DB connection held from first query to full HTTP response
# At 200ms response time + 100 RPS = 20 connections held
# HikariCP pool of 20 → all consumed → queuing starts

# GOOD: OSIV disabled
spring:
  jpa:
    open-in-view: false
# Connection held only during @Transactional execution
# At 50ms service time + 100 RPS = 5 connections needed
# 4× more capacity from same pool size
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Switching @OneToMany to EAGER fixes LazyInitializationException | EAGER on a collection forces all items to be fetched even when not needed, and risks Cartesian product multiplication if multiple EAGER collections exist on the same entity |
| Lazy loading is always faster than eager | Lazy is faster when the association is not needed. When the association IS needed, lazy adds an extra round-trip query vs. eager's join |
| spring.jpa.open-in-view=true is the correct default | OSIV was a convenience default that causes severe connection pool pressure in production. Disable it and fix fetch strategies properly |
| EAGER on @ManyToOne is always safe | EAGER on @ManyToOne is usually safe for single-entity loads but still causes N queries when loading a list of entities (each eager-loads its @ManyToOne) |

---

### 🔥 Pitfalls in Production

**1. Multiple EAGER collections → Cartesian product explosion**

```java
// BAD: two EAGER collections on same entity
@Entity
class Order {
  @OneToMany(fetch = EAGER) List<Item> items;     // 100 items
  @OneToMany(fetch = EAGER) List<Payment> payments; // 5 payments
}
// SELECT * FROM orders JOIN items JOIN payments
// → 100 × 5 = 500 rows per order!
// → 1000 orders = 500,000 rows result set
// Hibernate: MultipleBagFetchException or OOM

// GOOD: both LAZY, fetch specifically when needed
@OneToMany(fetch = LAZY) List<Item> items;
@OneToMany(fetch = LAZY) List<Payment> payments;
// @EntityGraph(attributePaths={"items"}) when needed
```

**2. OSIV masking LazyInitializationException in tests**

```java
// Tests pass with spring.jpa.open-in-view=true (session open)
// Production fails with open-in-view=false (session closed)

// BAD: test passes but production fails
@SpringBootTest
// No explicit open-in-view=false config
void testGetOrder() {
  OrderDto dto = controller.getOrder(1L);
  // Lazy loading works in test (OSIV open)
  // But fails in production with OSIV disabled
}

// GOOD: test with same OSIV settings as production
@SpringBootTest
@TestPropertySource(properties =
    "spring.jpa.open-in-view=false")
void testGetOrder() {
  // LazyInitializationException surface here in test
  // → forced to fix fetch strategy before production
}
```

---

### 🔗 Related Keywords

- `N+1 Problem` — caused by iterating over LAZY associations without JOIN FETCH
- `@EntityGraph` — declarative fetch join to load LAZY associations on demand
- `LazyInitializationException` — Hibernate's error for LAZY access outside session
- `OSIV (Open Session in View)` — keeps session open; hides lazy bugs but kills perf
- `HikariCP` — the pool from which connections are borrowed during lazy loading
- `DTO Projection` — skips entity loading entirely — no lazy/eager concerns

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ LAZY = on-demand SQL; EAGER = join always  │
│              │ LAZY default for collections is correct;  │
│              │ fetch per use case with @EntityGraph      │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ LAZY: standard; EAGER: small guaranteed-  │
│              │ needed single associations only           │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ EAGER on collections (Cartesian product); │
│              │ OSIV in production (connection exhaustion) │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Lazy is à la carte; Eager is prix fixe — │
│              │  only order what you'll actually eat."    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ HikariCP (132) → @EntityGraph →           │
│              │ N+1 Problem (130)                         │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Hibernate's first-level cache (persistence context) within a `@Transactional` method means that accessing the same entity twice returns the same Java object — the second access doesn't hit the database. But when LAZY loading is involved with the persistence context open, the first access to a lazy proxy triggers a SQL; the second access returns the already-loaded collection from context without a new query. Explain how this interacts with `@Transactional(readOnly = true)` and Hibernate's `FlushMode.MANUAL`: if you modify the loaded collection (add an item), does Hibernate detect this and flush at transaction end or is the change silently lost?

**Q2.** Spring Boot's `spring.jpa.open-in-view=true` (OSIV) extends the Hibernate session across the HTTP request lifecycle via `OpenSessionInViewInterceptor` (a Spring MVC `HandlerInterceptor`). Explain what happens to database connections during a long-running request that causes OSIV concern: trace the connection lifecycle from session open → service method → @Transactional commits → controller renders template → session closes. At which point is the JDBC connection held vs. idle-but-open, and describe the difference between a Hibernate session being open vs. a transaction being active.

