---
layout: default
title: "N+1 Problem"
parent: "Spring Core"
nav_order: 398
permalink: /spring/n-plus-1-problem/
number: "398"
category: Spring Core
difficulty: ★★★
depends_on: "@Transactional, Lazy vs Eager Loading, Spring Data JPA"
used_by: "Lazy vs Eager Loading, Spring Data JPA, HikariCP"
tags: #advanced, #spring, #database, #performance, #deep-dive
---

# 398 — N+1 Problem

`#advanced` `#spring` `#database` `#performance` `#deep-dive`

⚡ TL;DR — The **N+1 problem** occurs when loading N parent entities triggers N additional SQL queries to load their children — instead of 1 query with a JOIN. It silently degrades performance: fetching 100 orders could fire 101 queries. The fix is a JOIN FETCH query or `@EntityGraph`.

| #398            | Category: Spring Core                                  | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------------- | :-------------- |
| **Depends on:** | @Transactional, Lazy vs Eager Loading, Spring Data JPA |                 |
| **Used by:**    | Lazy vs Eager Loading, Spring Data JPA, HikariCP       |                 |

---

### 📘 Textbook Definition

The **N+1 problem** (also called the N+1 query problem or select N+1 problem) is a data access antipattern where an application executes 1 query to load a collection of N entities, then executes N additional queries to load each entity's associated data — instead of 1 query (with JOIN) that fetches everything at once. In JPA/Hibernate terminology, it arises when a lazily-loaded association (e.g., `@OneToMany(fetch = FetchType.LAZY)`) is accessed outside the original query: the initial `SELECT * FROM orders` loads N orders, but when `order.getItems()` is called for each order, Hibernate fires `SELECT * FROM order_items WHERE order_id = ?` for each — resulting in N+1 total queries. The solutions are: **JOIN FETCH** in JPQL (`SELECT o FROM Order o JOIN FETCH o.items`), **`@EntityGraph`** (declarative fetch plan), **Hibernate `@BatchSize`** (groups N lazy loads into batches), or Spring Data **projection interfaces** (avoids loading associations entirely).

---

### 🟢 Simple Definition (Easy)

The N+1 problem is when your app asks the database "give me the orders" (1 query), and then asks "give me the items for order 1", "give me the items for order 2"... N more times. One query should have been enough with a JOIN.

---

### 🔵 Simple Definition (Elaborated)

You have a page showing 100 orders with their items. The ORM fetches all 100 orders in one query. But `order.getItems()` is lazy — each access triggers a separate database round-trip. The page silently fires 101 queries: 1 for orders + 100 for items. On a local database this is tolerable; on a remote database with 1ms network latency, 100 extra queries add 100ms to page load time. On a database under load, 100 extra queries consume 100 connection slots. The N+1 problem is silent — there is no exception, just slow performance that is hard to notice in development (local DB is fast) but catastrophic in production (remote DB, load, connection limits).

---

### 🔩 First Principles Explanation

**N+1 generation step-by-step with Hibernate SQL logging:**

```java
// Entity:
@Entity class Order {
    @Id Long id;
    @OneToMany(fetch = FetchType.LAZY, mappedBy = "order")
    List<OrderItem> items; // LAZY: not loaded until accessed
}

// Repository:
List<Order> orders = orderRepository.findAll(); // SELECT * FROM orders

// Usage (triggers N+1):
for (Order order : orders) {
    log.info("Order {} has {} items", order.getId(), order.getItems().size());
    //                                               ↑ triggers LAZY load!
}

// Hibernate SQL log output for 3 orders:
// SELECT * FROM orders                          ← query 1 (1 query)
// SELECT * FROM order_items WHERE order_id = 1 ← query 2 (for order 1)
// SELECT * FROM order_items WHERE order_id = 2 ← query 3 (for order 2)
// SELECT * FROM order_items WHERE order_id = 3 ← query 4 (for order 3)
// Total: 1 + N = 4 queries for 3 orders
// For 1000 orders: 1001 queries
```

**The 4 solutions with their tradeoffs:**

```java
// ────────────────────────────────────────────────────────────────
// SOLUTION 1: JOIN FETCH (JPQL)
// ────────────────────────────────────────────────────────────────
@Repository
public interface OrderRepository extends JpaRepository<Order, Long> {

    @Query("SELECT DISTINCT o FROM Order o JOIN FETCH o.items")
    List<Order> findAllWithItems();
    // SQL: SELECT DISTINCT o.*, i.* FROM orders o
    //      INNER JOIN order_items i ON i.order_id = o.id
    // → 1 query, all data in one result set
    // GOTCHA: DISTINCT required to avoid duplicate Order objects in result
    // GOTCHA: HHH90003004 warning if combined with pagination (see pitfall)
}

// ────────────────────────────────────────────────────────────────
// SOLUTION 2: @EntityGraph (declarative fetch override)
// ────────────────────────────────────────────────────────────────
@Entity
@NamedEntityGraph(
    name = "order-with-items",
    attributeNodes = @NamedAttributeNode("items")
)
class Order { ... }

@Repository
public interface OrderRepository extends JpaRepository<Order, Long> {

    @EntityGraph("order-with-items")   // eager-fetch 'items' for this query only
    List<Order> findAll();             // standard findAll(), but with items join-fetched
    // SQL: same as JOIN FETCH — LEFT JOIN fetch on items
}

// ────────────────────────────────────────────────────────────────
// SOLUTION 3: @BatchSize (grouped lazy loads — good for paginated results)
// ────────────────────────────────────────────────────────────────
@Entity class Order {
    @BatchSize(size = 50)  // load items for up to 50 orders in ONE query
    @OneToMany(fetch = FetchType.LAZY, mappedBy = "order")
    List<OrderItem> items;
}
// Hibernate batches lazy loads:
// Instead of N queries of "SELECT WHERE order_id = ?"
// → "SELECT WHERE order_id IN (1, 2, 3, ... 50)" (batch of 50)
// Reduces N queries to CEIL(N/50) queries
// Great for pagination (page of 20 → 1 extra query for batch of 20)

// ────────────────────────────────────────────────────────────────
// SOLUTION 4: DTO Projection (avoid associations entirely)
// ────────────────────────────────────────────────────────────────
@Query("""
    SELECT new com.example.dto.OrderSummary(
        o.id, o.createdAt, COUNT(i), SUM(i.price))
    FROM Order o
    LEFT JOIN o.items i
    GROUP BY o.id, o.createdAt
    """)
List<OrderSummary> findOrderSummaries();
// Never loads Order entities or Item entities
// → pure SQL projection, no lazy loading risk at all
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT awareness of N+1:

What breaks without it:

1. The app appears correct in development (small data, local DB, fast latency) but degrades in production.
2. Connection pool exhaustion: N+1 queries hold connections longer, starving other requests.
3. Database CPU spikes from thousands of small queries instead of a few efficient queries.
4. Query count is invisible in application logs — only Hibernate SQL logging or a profiler reveals it.

WITH N+1 awareness:
→ Queries are designed with JOIN FETCH or `@EntityGraph` from the start.
→ Hibernate SQL logging is enabled in development to catch N+1 early.
→ Tools like Datasource Proxy or `spring.jpa.show-sql=true` provide visibility.
→ `@BatchSize` provides a middle ground when pagination makes JOIN FETCH impractical.

---

### 🧠 Mental Model / Analogy

> The N+1 problem is like a librarian who retrieves books by first asking "what books are on the shelf?" (1 query), then going back to the storeroom for EACH book individually (N queries), rather than loading all relevant books in one trip. An experienced librarian (optimised ORM/query) reads the full list first, then makes ONE trip to collect all books at once (JOIN FETCH). The lazy librarian (N+1) gets the same result but with N unnecessary round-trips to the storeroom.

"Asking what books are on the shelf" = SELECT _ FROM orders (the 1 query)
"Going to storeroom for each book" = SELECT _ FROM items WHERE order_id=? (the N queries)
"One efficient trip with full list" = JOIN FETCH / @EntityGraph
"N unnecessary round-trips" = the performance cost of N+1

---

### ⚙️ How It Works (Mechanism)

**Detecting N+1 in Spring Boot:**

```yaml
# application.properties — enable SQL logging in development
spring.jpa.show-sql=true
spring.jpa.properties.hibernate.format_sql=true
logging.level.org.hibernate.SQL=DEBUG
logging.level.org.hibernate.type.descriptor.sql.BasicBinder=TRACE
# Better: use p6spy or Datasource Proxy for structured logging
# or use Hypersistence Optimizer for automated N+1 detection
```

```java
// Programmatic N+1 detection test (using Datasource Proxy):
@Test
void shouldNotTriggerNPlusOne() {
    MeterRegistry meterRegistry = new SimpleMeterRegistry();
    int[] queryCount = {0};

    DataSource proxied = ProxyDataSourceBuilder.create(dataSource)
        .countQuery()
        .afterQuery((execInfo, queryInfoList) -> queryCount[0]++)
        .build();

    // execute service method with proxied datasource
    List<Order> orders = orderService.getRecentOrders();
    orders.forEach(o -> o.getItems().size()); // trigger potential N+1

    assertThat(queryCount[0])
        .as("Expected 1 query but fired " + queryCount[0])
        .isEqualTo(1); // fail if N+1 occurs
}
```

---

### 🔄 How It Connects (Mini-Map)

```
@OneToMany(fetch = LAZY)  ←────── Lazy vs Eager Loading
  (association accessed outside tx)
        │
        ▼
N+1 Problem  ◄──── (you are here)
(N extra queries triggered per parent entity)
        │
        ├── Fix: JOIN FETCH (JPQL)
        ├── Fix: @EntityGraph (declarative)
        ├── Fix: @BatchSize (grouped lazy loads)
        └── Fix: DTO Projection (avoid entity loading)
        │
        ▼
HikariCP / Connection Pool
(N+1 increases connection hold time and query count)
```

---

### 💻 Code Example

**REST controller exposing order summary — correct vs N+1 version:**

```java
// WRONG: N+1 in REST endpoint
@RestController
class OrderController {
    @Autowired OrderRepository orderRepo;

    @GetMapping("/orders")
    List<OrderResponse> getOrders() {
        return orderRepo.findAll().stream()  // 1 query: SELECT orders
            .map(order -> OrderResponse.builder()
                .id(order.getId())
                .itemCount(order.getItems().size())  // N queries: each access fires SQL!
                .totalPrice(order.getItems().stream()
                    .mapToDouble(i -> i.getPrice().doubleValue()).sum()) // uses cached lazy load
                .build())
            .collect(toList());
    }
}

// CORRECT: DTO projection — zero N+1 risk
@RestController
class OrderController {
    @Autowired OrderRepository orderRepo;

    @GetMapping("/orders")
    List<OrderSummaryDto> getOrders() {
        // 1 query with GROUP BY — no entity loading, no lazy load risk
        return orderRepo.findOrderSummaries();
    }
}

// In repository:
@Query("""
    SELECT new com.example.dto.OrderSummaryDto(
        o.id, o.customerName, COUNT(i), COALESCE(SUM(i.price), 0))
    FROM Order o
    LEFT JOIN o.items i
    GROUP BY o.id, o.customerName
    """)
List<OrderSummaryDto> findOrderSummaries();
```

---

### ⚠️ Common Misconceptions

| Misconception                                                                                            | Reality                                                                                                                                                                                                                                                      |
| -------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Switching from `LAZY` to `EAGER` fetch type fixes N+1                                                    | Eager fetch with the default `@OneToMany` still fires N+1 — Hibernate uses secondary SELECT queries for `@OneToMany` by default even with `EAGER`. The fix is not the fetch type but the fetch strategy (JOIN FETCH or `@EntityGraph`)                       |
| N+1 only happens with `@OneToMany`                                                                       | N+1 can occur with any lazily-loaded association: `@ManyToOne` (each entity triggers a separate load of its parent), `@ManyToMany`, and even `@OneToOne` with lazy loading                                                                                   |
| `JOIN FETCH` can be combined with Hibernate pagination (`setFirstResult`/`setMaxResults`) without issues | Hibernate emits a `HHH90003004` warning and loads ALL data into memory, then paginates in memory — not in the database. This can cause OutOfMemoryError for large datasets. Use `@BatchSize` or a two-query approach for paginated N+1 solutions             |
| N+1 is always visible in development                                                                     | In development with a local in-memory database (H2), each extra query takes <1ms. N+1 with 100 entities adds <100ms locally but 500ms+ in production with a remote database at 5ms latency. N+1 is often only visible in production load tests or APM traces |

---

### 🔥 Pitfalls in Production

**N+1 + pagination = OutOfMemoryError**

```java
// WRONG: JOIN FETCH + pagination = Hibernate fetches ALL data, paginates in memory
@Query("SELECT DISTINCT o FROM Order o JOIN FETCH o.items")
Page<Order> findAllWithItemsPaged(Pageable pageable);
// Hibernate warning: HHH90003004: firstResult/maxResults specified with collection fetch;
// applying in memory → ALL orders loaded into heap, then first 20 taken

// CORRECT approach: two queries
// 1. Get the page of IDs with pagination:
@Query(value  = "SELECT o.id FROM orders o ORDER BY o.created_at DESC",
       countQuery = "SELECT COUNT(o.id) FROM orders o",
       nativeQuery = true)
Page<Long> findPagedOrderIds(Pageable pageable);

// 2. Fetch those specific orders with items (no pagination issue):
@Query("SELECT DISTINCT o FROM Order o JOIN FETCH o.items WHERE o.id IN :ids")
List<Order> findOrdersWithItemsByIds(@Param("ids") List<Long> ids);

// OR: Use @BatchSize on the collection — Hibernate batches lazy loads per page:
// Page<Order> = 20 orders → 1 extra query for all 20 items batches
```

---

### 🔗 Related Keywords

- `Lazy vs Eager Loading` — lazy loading is the most common trigger for N+1
- `Spring Data JPA` — the repository abstraction where N+1 most commonly manifests
- `@Transactional` — the active transaction context needed for lazy loading to work
- `HikariCP` — connection pool that takes the load of N+1's extra queries

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ CAUSE        │ Accessing lazy association in a loop      │
│              │ → 1 (parent fetch) + N (per-child fetch)  │
├──────────────┼───────────────────────────────────────────┤
│ SOLUTIONS    │ JOIN FETCH: 1 query, all data             │
│              │ @EntityGraph: declarative JOIN FETCH      │
│              │ @BatchSize: group lazy loads (IN clause)  │
│              │ DTO Projection: avoid entity loading      │
├──────────────┼───────────────────────────────────────────┤
│ DETECT       │ spring.jpa.show-sql=true in dev           │
│              │ Datasource Proxy / p6spy                  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "N+1 = asking the DB for each item        │
│              │  individually instead of one JOIN"       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** `@BatchSize(size = 50)` groups N lazy loads into batches using `IN (?, ?, ...)` clauses. Describe the database query plan implications: does a batched IN query use an index on `order_id` efficiently? For a `@BatchSize` of 50 on `order_items`, if the page size is 20, Hibernate fires one batch for 20 items — but the batch size is 50, meaning Hibernate pads the IN clause with NULL literals: `WHERE order_id IN (1, 2, 3, ..., 20, null, null, ..., null)`. Why does Hibernate do this (query plan caching — the number of parameters must be consistent), and what is the impact on query plan cache hit rate?

**Q2.** The "N+1 for `@ManyToOne`" pattern is less intuitive. Given 100 `OrderItem` entities each with a `@ManyToOne` reference to `Order`, and a query that loads all `OrderItem` records: if each `OrderItem.order` is lazily loaded, describe when and how Hibernate triggers the N+1 loads. How does Hibernate's "entity identity map" (first-level cache / `PersistenceContext`) help: if all 100 items belong to only 5 distinct orders, does Hibernate still fire 100 queries? And what is the second-level cache's role in preventing N+1 selects across different transactions?
