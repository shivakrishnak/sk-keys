---
layout: default
title: "N+1 Problem"
parent: "Spring Core"
nav_order: 398
permalink: /spring/n-plus-1-problem/
number: "398"
category: Spring Core
difficulty: ★★☆
depends_on: "JPA, Hibernate, Lazy Loading, Spring Data, JPQL"
used_by: "Fetch join, @EntityGraph, batch fetching, DTO projections"
tags: #java, #spring, #database, #performance, #intermediate
---

# 398 — N+1 Problem

`#java` `#spring` `#database` `#performance` `#intermediate`

⚡ TL;DR — Fetching N parent entities then issuing N additional queries to load each entity's collection — a silent performance killer caused by lazy loading in JPA.

| #398 | category: Spring Core
|:---|:---|:---|
| **Depends on:** | JPA, Hibernate, Lazy Loading, Spring Data, JPQL | |
| **Used by:** | Fetch join, @EntityGraph, batch fetching, DTO projections | |

---

### 📘 Textbook Definition

The **N+1 problem** is a data access anti-pattern that occurs when loading a collection of N parent entities triggers N additional SQL queries to lazily load each entity's association. Total queries = 1 (for N parents) + N (one per parent's association load) = N+1. In JPA/Hibernate, it occurs when a `@OneToMany` or `@ManyToOne` association is mapped as `FetchType.LAZY` (the default for collections) and the association is accessed outside the flush boundary. Solutions include JOIN FETCH in JPQL, `@EntityGraph`, Hibernate batch fetching (`@BatchSize`), or DTO projections that select only required fields.

---

### 🟢 Simple Definition (Easy)

The N+1 problem is when loading 100 orders triggers 101 SQL queries — one to get all orders, then one more for each order to get its related items. That's massively inefficient.

---

### 🔵 Simple Definition (Elaborated)

JPA's lazy loading sounds efficient: "don't load related data until it's needed." But when you iterate over a list of entities and access a lazy relationship on each one, Hibernate fires a separate SELECT for each entity. Load 1,000 orders and access `order.getItems()` for each → 1,001 SQL queries in one request. The problem is insidious because it's invisible in code — there's no loop with explicit queries, just a simple `.stream().map()` in what looks like clean business code. Without query logging enabled, it can silently destroy performance.

---

### 🔩 First Principles Explanation

**The mechanics:**

```java
// THIS LOOKS INNOCENT:
List<Order> orders = orderRepo.findAll();        // Query 1
List<OrderSummary> summaries = orders.stream()
    .map(o -> new OrderSummary(
        o.getId(),
        o.getItems().size()))                    // Query 2,3,4...N+1
    .toList();

// WHAT HIBERNATE ACTUALLY EXECUTES:
// SELECT * FROM orders                          ← 1 query
// SELECT * FROM items WHERE order_id = 1        ← query for order 1
// SELECT * FROM items WHERE order_id = 2        ← query for order 2
// SELECT * FROM items WHERE order_id = 3        ← query for order 3
// ... × N orders
// Total: N+1 queries
```

**Why lazy loading defaults exist despite N+1:**

The default is LAZY because EAGER is worse for many use cases:

```
EAGER: load 1 order → immediately JOIN all items/user/payments
→ One order page: loads 10× more data than needed

LAZY: load 1 order → items only if accessed
→ Optimal for single-entity operations
→ Only N+1 problem when iterating collections
```

---

### ❓ Why Does This Exist (Why Before What)

**N+1 emerges from:**

```
JPA's object-relational mapping goal:
  Let you work with Java objects, not SQL
  Associations are Java references (order.getItems())
  Not SQL joins you must write manually

The tradeoff:
  Lazy loading: access item when needed
  → sounds great for one entity
  → adds hidden SQL for every entity in a list
  → 1000 entities = 1000 hidden SQLs
  → developer never wrote a SQL,
    never expected a SQL flood

Visibility problem:
  ORM hides SQL → developer doesn't see N+1
  First visible signal: slowness under load
  Without query logging: never caught in dev
```

---

### 🧠 Mental Model / Analogy

> The N+1 problem is like a **supermarket checkout queue going wrong**. You need to price 100 items: a cashier scans item 1, then walks to the stockroom to check its price, returns, scans item 2, walks to stockroom again... 100 trips in total. What was needed: one trip to collect all 100 prices at once (JOIN FETCH), then scan everything. The overhead is the 100 separate trips (SQL queries) instead of one batch.

"Scanning item 1" = loading entity 1
"Walking to stockroom" = lazy SQL to fetch item's collection
"100 trips" = N+1 separate queries
"One trip for all prices" = JOIN FETCH in one query
"Cashier unaware of inefficiency" = developer unaware of lazy SQL calls

---

### ⚙️ How It Works (Mechanism)

**Diagnosing N+1 — query logging:**

```yaml
# application.properties for N+1 detection:
spring:
  jpa:
    show-sql: true
    properties:
      hibernate:
        format_sql: true
        use_sql_comments: true

logging:
  level:
    org.hibernate.SQL: DEBUG
    org.hibernate.type.descriptor.sql: TRACE
    # TRACE shows bind parameters — helps spot duplicate queries

# Better: use p6spy or datasource-proxy for:
# - Query count per request
# - Duplicate query detection
# - Slow query logging
```

**Four solutions with code:**

```java
// SOLUTION 1: JPQL JOIN FETCH (explicit)
@Query("SELECT o FROM Order o LEFT JOIN FETCH o.items "
     + "WHERE o.status = :status")
List<Order> findActiveOrdersWithItems(
    @Param("status") OrderStatus status);
// ONE query: SELECT o.*, i.* FROM orders o
//            LEFT JOIN items i ON i.order_id = o.id

// SOLUTION 2: @EntityGraph (declarative fetch)
@EntityGraph(attributePaths = {"items", "items.product"})
List<Order> findByCustomerId(long customerId);
// Generates JOIN FETCH automatically from attribute paths

// SOLUTION 3: @BatchSize — fetches in batches of N
@OneToMany(mappedBy = "order", fetch = LAZY)
@BatchSize(size = 25) // 100 orders = 4 queries, not 100
private List<Item> items;

// SOLUTION 4: DTO projection — fetch only needed columns
@Query("SELECT new com.example.OrderSummaryDto("
     + "o.id, o.createdAt, COUNT(i)) "
     + "FROM Order o LEFT JOIN o.items i "
     + "GROUP BY o.id, o.createdAt")
List<OrderSummaryDto> findOrderSummaries();
// Single query, no lazy loading at all, minimal data
```

---

### 🔄 How It Connects (Mini-Map)

```
@OneToMany(fetch = LAZY) — default
        ↓
  accessed in a loop → N+1 PROBLEM  ← you are here
        ↓
  Detection: Hibernate SQL logging / p6spy
        ↓
  Solutions:
  JOIN FETCH in @Query → one SQL
  @EntityGraph → declarative fetch join
  @BatchSize → N queries → N/batchSize queries
  DTO Projection → no entity at all
        ↓
  Related: Lazy vs Eager Loading (131)
  (choosing the right fetch strategy)
```

---

### 💻 Code Example

**Example 1 — Comparing N+1 before and after fix:**

```java
// BEFORE: N+1 (100 orders → 101 queries)
List<Order> orders = orderRepo.findByCustomerId(customerId);
return orders.stream()
    .map(o -> Map.of(
        "id", o.getId(),
        "itemCount", o.getItems().size()  // triggers N lazy loads
    ))
    .toList();

// AFTER: 1 query with DTO projection
@Query("SELECT new OrderSummary(o.id, COUNT(i)) "
     + "FROM Order o LEFT JOIN o.items i "
     + "WHERE o.customer.id = :cid GROUP BY o.id")
List<OrderSummary> findSummariesByCustomer(
    @Param("cid") long customerId);

// Call:
return orderRepo.findSummariesByCustomer(customerId);
// ONE SQL: SELECT o.id, COUNT(i.id) FROM orders o
//          LEFT JOIN items i GROUP BY o.id
```

**Example 2 — Using @EntityGraph for selective fetch:**

```java
@Repository
public interface OrderRepository
    extends JpaRepository<Order, Long> {

  // Default: lazy items (good for single-record endpoints)
  Optional<Order> findById(Long id);

  // Explicit fetch: good for list/export endpoints
  @EntityGraph(attributePaths = {"items", "customer"})
  List<Order> findByStatus(OrderStatus status);
  // Generates: SELECT o, i, c FROM Order o
  //            LEFT JOIN FETCH o.items
  //            LEFT JOIN FETCH o.customer
  //            WHERE o.status = ?
}
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Switching to EAGER loading fixes N+1 | EAGER loading on @OneToMany forces a JOIN on every single query that loads the parent — even when you don't need the collection. This often performs WORSE than N+1 for single-entity operations |
| N+1 only happens with @OneToMany | N+1 can happen with @ManyToOne too — accessing 100 orders' lazy customer reference triggers 100 SELECT FROM customers queries |
| JOIN FETCH always creates a Cartesian product | LEFT JOIN FETCH on a collection DOES create a Cartesian product — use DISTINCT or DTO projections to avoid duplicate parent rows |
| p6spy or datasource-proxy is only for debugging | These tools should be enabled in staging with slow-query thresholds and query-count-per-request alerts to catch N+1 before production |

---

### 🔥 Pitfalls in Production

**1. JOIN FETCH causing duplicates with pagination**

```java
// BAD: combined fetch join + setMaxResults = unpredictable
@Query("SELECT DISTINCT o FROM Order o "
     + "LEFT JOIN FETCH o.items")
Page<Order> findAllOrders(Pageable pageable);
// Hibernate WARN: "HHH90003004: firstResult/maxResults
//                  specified with collection fetch"
// Hibernate loads ALL orders into memory then slices!
// → OutOfMemoryError on large tables

// GOOD option 1: two queries (count + fetch)
@Query(value = "SELECT o FROM Order o",
       countQuery = "SELECT COUNT(o) FROM Order o")
Page<Order> findAllOrders(Pageable pageable);
// Then fetch items in a second query by IDs:
List<Long> ids = page.stream().map(Order::getId).toList();
orderRepo.findWithItemsByIdIn(ids);

// GOOD option 2: DTO projection doesn't have this issue
```

**2. N+1 invisible in service method — caught only in load test**

```java
// Service method looks perfectly clean:
@Transactional(readOnly = true)
public List<InvoiceReport> generateReport() {
  return invoiceRepo.findAllByMonthYear(month, year)
      .stream()
      .map(this::toReport)  // accesses lazy line items
      .toList();
}
// 500 invoices = 501 SQL queries per report generation
// In dev: runs in 80ms
// In staging with real data: runs in 8 seconds
// FIX: add query logging to CI integration tests
// Assert: SQL count per test < threshold (e.g. < 5 queries)
```

---

### 🔗 Related Keywords

- `Lazy vs Eager Loading` — the fetch strategy choice that causes N+1
- `@EntityGraph` — Spring Data's declarative JOIN FETCH mechanism
- `JPQL JOIN FETCH` — the explicit query-level solution to N+1
- `@BatchSize` — Hibernate hint to batch lazy loads together
- `HikariCP` — every N+1 query borrows a connection from the pool
- `DTO Projection` — the ultimate N+1 fix: don't load entities at all

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ 1 query for N parents + N queries for     │
│              │ each association = N+1 silent perf killer  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Detect: enable SQL logging in staging;    │
│              │ Fix: JOIN FETCH, @EntityGraph, @BatchSize  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Never switch @OneToMany to EAGER as a fix │
│              │ — it makes single-entity queries worse    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "100 orders = 101 trips to the stockroom  │
│              │  — make one trip and grab everything."    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Lazy vs Eager Loading (131) →             │
│              │ HikariCP (132) → @EntityGraph             │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Spring Data's `@EntityGraph` generates a JOIN FETCH internally. When you apply `@EntityGraph(attributePaths = {"items"})` to a `findAll(Pageable)` method, Hibernate warns about in-memory pagination. Explain the root cause: why does a fetch join on a collection make `LIMIT`/`OFFSET` at the SQL level incorrect — what happens to the row count, and why does Hibernate load all rows into memory before paginating. Describe the two-phase approach (count query + IN-list fetch) that correctly paginates entities with collection associations.

**Q2.** Hibernate's `@BatchSize` approach is a middle-ground solution. Instead of 100 separate queries, it groups lazy loads into `SELECT * FROM items WHERE order_id IN (1, 2, 3, ..., 25)` batches. Explain how Hibernate determines which IDs to include in each batch — does it batch by the order they were accessed, by proximity in the persistence context, or by some other strategy — and describe the specific scenario where `@BatchSize` can still cause poor performance when the collection sizes are highly skewed (e.g. 1 order has 10,000 items and 99 orders have 1 item each).

