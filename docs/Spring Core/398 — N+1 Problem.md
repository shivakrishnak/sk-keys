---
layout: default
title: "N+1 Problem"
parent: "Spring Core"
nav_order: 398
permalink: /spring/n-plus-1-problem/
number: "0398"
category: Spring Core
difficulty: ★★★
depends_on: "@Transactional, Transaction Isolation Levels, Spring Data JPA, Hibernate"
used_by: Spring Data JPA, ORM frameworks, REST APIs
related: "@Transactional, Transaction Isolation Levels, Hibernate, JOIN FETCH, EntityGraph, Batch Size"
tags:
  - spring
  - springboot
  - advanced
  - jpa
  - performance
---

# 398 — N+1 Problem

⚡ TL;DR — The N+1 problem occurs when loading N entities triggers N additional queries (1 query to fetch the list + N queries to fetch each entity's lazy associations) — solved by JOIN FETCH, EntityGraph, or batch fetching to collapse N+1 queries into 1 or few.

| #398            | Category: Spring Core                                                                        | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | @Transactional, Transaction Isolation Levels, Spring Data JPA, Hibernate                     |                 |
| **Used by:**    | Spring Data JPA, ORM frameworks, REST APIs                                                   |                 |
| **Related:**    | @Transactional, Transaction Isolation Levels, Hibernate, JOIN FETCH, EntityGraph, Batch Size |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You load 100 users. Each user has a list of orders. The ORM lazy-loads orders — perfectly reasonable for cases where you don't need them. But your API needs to return users WITH their orders. The ORM issues 1 query for users + 100 queries for each user's orders = 101 total queries. For 1000 users: 1001 queries. In production with a remote database, each round trip adds ~1ms. 1001 queries × 1ms = 1 second just in database round trips, not counting actual query execution. Your API times out.

**THE DISCOVERY MOMENT:**
"It works fine in development (small dataset, same machine) but collapses in production (large dataset, remote database)." — The N+1 problem is usually discovered in production performance incidents, not in unit tests.

---

### 📘 Textbook Definition

The **N+1 problem** is an ORM anti-pattern where a single application-level operation triggers one query to retrieve a list of N entities followed by N additional queries — one per entity — to load a lazily-fetched association. Total = N+1 queries. The root cause is the combination of **lazy loading** (associations not fetched until accessed) and **iteration over a collection** (forcing each lazy association to load individually). The problem is ORM-agnostic (Hibernate, EclipseLink, MyBatis, etc.) and occurs in any data access layer that uses lazy loading. Solutions: **eager JOIN FETCH** (SQL JOIN in the same query), **@EntityGraph** (declarative eager fetch specification), **Hibernate @BatchSize** (batch lazy loads into `WHERE id IN (...)` queries), or **DTO projections** (fetch only needed data via custom queries).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Loading N things + accessing each thing's lazy collection = N+1 queries — use JOIN FETCH or EntityGraph to load everything in 1 query.

**One analogy:**

> Ordering food at a restaurant. You ask for the menu (1 query). Then you ask the waiter about each item individually: "What's in item 1?" "What's in item 2?" ... "What's in item 100?" — That's 101 questions instead of asking "describe all items" (1 JOIN FETCH query). The waiter (database) can answer all at once — but you have to ask the right way.

**One insight:**
N+1 is almost always invisible until production load. A dev with 5 test users never sees it. A prod system with 50,000 users has its API timed out. SQL logging in development (`spring.jpa.show-sql=true`) catches it immediately.

---

### 🔩 First Principles Explanation

**ROOT CAUSE — Lazy loading:**

```java
@Entity
public class User {
    @Id private Long id;
    private String name;

    @OneToMany(mappedBy = "user", fetch = FetchType.LAZY)
    private List<Order> orders;  // LAZY: not loaded until accessed
}

// This code triggers N+1:
List<User> users = userRepo.findAll();  // Query 1: SELECT * FROM users
for (User u : users) {
    System.out.println(u.getOrders().size());  // Query 2...N+1 each iteration
    // Hibernate: SELECT * FROM orders WHERE user_id = ?  ← repeated N times
}
```

**SQL log output (N=3 users):**

```sql
-- Query 1: get users
SELECT u.id, u.name FROM users u;

-- Query 2: get orders for user 1
SELECT o.id, o.amount FROM orders o WHERE o.user_id = 1;

-- Query 3: get orders for user 2
SELECT o.id, o.amount FROM orders o WHERE o.user_id = 2;

-- Query 4: get orders for user 3
SELECT o.id, o.amount FROM orders o WHERE o.user_id = 3;

-- Total: 4 queries for 3 users (N+1 where N=3)
-- For 1000 users: 1001 queries
```

---

### 🧪 Thought Experiment

**SETUP:**
REST endpoint `GET /api/users/summary` — returns all users with their total order count and most recent order date.

**NAIVE IMPLEMENTATION:**

```java
@GetMapping("/api/users/summary")
public List<UserSummary> getUserSummaries() {
    List<User> users = userRepo.findAll();     // 1 query
    return users.stream()
        .map(u -> new UserSummary(
            u.getName(),
            u.getOrders().size(),              // +1 query per user
            u.getOrders().stream()
                .map(Order::getDate)
                .max(Comparator.naturalOrder())
                .orElse(null)                  // (same N lazy loads)
        ))
        .collect(toList());
    // 1000 users = 1001 queries
}
```

**APPROACH 1 — JOIN FETCH (1 query, memory trade-off):**

```java
@Query("SELECT u FROM User u LEFT JOIN FETCH u.orders")
List<User> findAllWithOrders();
// 1 query with JOIN — loads all users + all orders
// Trade-off: Cartesian product can cause duplicate users (use DISTINCT or Set)
```

**APPROACH 2 — DTO projection (best — fetch only what you need):**

```java
@Query("""
    SELECT new com.app.dto.UserSummary(
        u.name, COUNT(o), MAX(o.date)
    )
    FROM User u LEFT JOIN u.orders o
    GROUP BY u.id, u.name
    """)
List<UserSummary> getUserSummaries();
// 1 query, no entity loading, no N+1 possible
// Returns only the data needed — no lazy loading involved
```

**THE INSIGHT:**
DTO projections are the best solution for read-only operations — you query exactly what you need, with no lazy loading. JOIN FETCH is appropriate when you need full entities. Never use lazy collection access in loops without explicit loading.

---

### 🧠 Mental Model / Analogy

> The N+1 problem is like a chef checking the pantry for each ingredient one by one during prep: walk to pantry, check if you have eggs (query 1), walk back, cook a bit, walk to pantry, check if you have flour (query 2), walk back... vs. making ONE trip to the pantry and checking everything at once (JOIN FETCH). The round trips are the killer — not the actual checking. In a restaurant kitchen (high production load), 100 pantry trips will destroy service speed.

- "Each pantry trip" = one SQL round trip to the database
- "Walk to pantry and back" = network latency (~1ms+ per round trip)
- "Check everything at once" = JOIN FETCH or batch loading

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
When you load a list of users and then look at each user's orders, you might accidentally trigger one database query PER user instead of one query for all users at once. With 100 users, that's 101 database trips instead of 1 (or 2). This is called the N+1 problem — it makes APIs very slow.

**Level 2 — How to use it (junior developer):**
Enable SQL logging (`spring.jpa.show-sql=true`) in development. If you see the same query repeated N times, you have N+1. Fix with JOIN FETCH in your JPQL query: `SELECT u FROM User u JOIN FETCH u.orders`. For repositories, use `@EntityGraph` to specify associations to eagerly fetch for specific query methods. Use DTO projections with `@Query` for read-only endpoints — they avoid entity loading entirely.

**Level 3 — How it works (mid-level engineer):**
When Hibernate encounters a lazy association access (`getOrders()`), it checks if the proxy is initialized. If not, it creates and executes a SELECT query for that specific association. Hibernate has no way to "look ahead" and batch these queries unless explicitly told to. `@BatchSize(size = 50)` tells Hibernate: instead of individual SELECTs, emit `WHERE user_id IN (1, 2, 3, ..., 50)` for up to 50 lazy loads at once — reducing N+1 to ceil(N/50)+1 queries. `JOIN FETCH` in JPQL generates a SQL JOIN — Hibernate loads all entities and their associations in one result set. The trade-off: a JOIN FETCH on a `@OneToMany` causes Hibernate to return duplicate parent rows (one per child) — use `DISTINCT` in JPQL or return a `Set` to deduplicate.

**Level 4 — Why it was designed this way (senior/staff):**
Lazy loading was the correct ORM default for a compelling reason: in many use cases, you don't need the association. If every object load eagerly fetched all associations transitively, an `Account` load might load all `Transactions`, each loading its `Category`, each loading its `SubCategories` — resulting in loading the entire database. Lazy loading deferred the decision to "do I need this?" to the point of actual access. The N+1 problem is the cost of this design — it's not a bug, it's a feature used incorrectly. The CORRECT rule is: for LIST operations (pagination, bulk reads), always specify exactly what you need via JOIN FETCH or DTO projection. Lazy loading is appropriate ONLY for single-entity operations where association access is conditional. The spring-data-jpa `@EntityGraph` annotation is the modern declarative approach — it lets you define fetch graphs per query method without writing JPQL.

---

### ⚙️ How It Works (Mechanism)

**Hibernate proxy initialization:**

```
userRepo.findAll() executes:
    SELECT u.id, u.name FROM users u
    → Returns 3 User objects
    → User.orders = PersistentBag (uninitialized proxy)

Loop iteration 1: user.getOrders().size()
    → PersistentBag.isInitialized? NO
    → Hibernate: SELECT o.* FROM orders o WHERE o.user_id = 1
    → PersistentBag populated
    → .size() = 5

Loop iteration 2: user.getOrders().size()
    → PersistentBag.isInitialized? NO (different User object)
    → Hibernate: SELECT o.* FROM orders o WHERE o.user_id = 2
    → PersistentBag populated
    → .size() = 3

[... repeat for all N users ...]
```

**JOIN FETCH mechanism:**

```
JPQL: SELECT u FROM User u LEFT JOIN FETCH u.orders

SQL generated:
    SELECT u.id, u.name, o.id, o.amount, o.user_id
    FROM users u
    LEFT JOIN orders o ON o.user_id = u.id

Result set (3 users, user 1 has 2 orders, user 2 has 1 order, user 3 has 0):
    Row 1: user_id=1, user_name=Alice, order_id=101
    Row 2: user_id=1, user_name=Alice, order_id=102  ← duplicate user row!
    Row 3: user_id=2, user_name=Bob,   order_id=103
    Row 4: user_id=3, user_name=Carol, order_id=null ← LEFT JOIN: no orders

Hibernate deduplicates into:
    User[1 Alice, orders=[101, 102]]
    User[2 Bob, orders=[103]]
    User[3 Carol, orders=[]]
Total: 1 query
```

---

### 🔄 The Complete Picture — REST API with N+1

```
GET /api/orders/summary
    ↓
OrderController.getOrderSummaries()
    ↓
@Transactional (session open)
    ↓
orderRepo.findAll()
    ↓ ← Query 1
SELECT o.id, o.status FROM orders o (N=1000 orders)
    ↓
Stream: for each order, access order.getCustomer().getName()
    ↓ ← N+1 TRIGGER
    ↓ Query 2:   SELECT * FROM customers WHERE id = 1
    ↓ Query 3:   SELECT * FROM customers WHERE id = 2
    ↓ ...
    ↓ Query 1001: SELECT * FROM customers WHERE id = 1000
1001 SQL queries sent to database
@Transactional ends (session closed)
API response after 1001 round trips — 10+ seconds
    ↓
FIXED: Use DTO projection
orderRepo.findOrderSummaries()  ← 1 JPQL query with JOIN
→ 1 SQL query, 1 result set
API response in milliseconds
```

---

### 💻 Code Example

**Example 1 — Detecting and fixing with JOIN FETCH:**

```java
// BAD: N+1
@Transactional(readOnly = true)
public List<UserResponse> getAllUsers() {
    return userRepo.findAll()          // Query 1
        .stream()
        .map(u -> new UserResponse(
            u.getName(),
            u.getOrders().size()       // Query per user!
        ))
        .toList();
}

// GOOD: JOIN FETCH
public interface UserRepository extends JpaRepository<User, Long> {
    @Query("SELECT DISTINCT u FROM User u LEFT JOIN FETCH u.orders")
    List<User> findAllWithOrders();
}

@Transactional(readOnly = true)
public List<UserResponse> getAllUsers() {
    return userRepo.findAllWithOrders()  // 1 query with JOIN
        .stream()
        .map(u -> new UserResponse(u.getName(), u.getOrders().size()))
        .toList();
}
```

**Example 2 — @EntityGraph (declarative, no JPQL needed):**

```java
public interface UserRepository extends JpaRepository<User, Long> {

    // Dynamically applies eager fetch for 'orders' for this specific method
    @EntityGraph(attributePaths = {"orders"})
    List<User> findAll();

    // Different method — no entity graph — lazy loading default
    Optional<User> findByEmail(String email);
}
```

**Example 3 — DTO projection (best for read-only):**

```java
// DTO — just the data you need
public record OrderSummary(
    Long orderId, String customerName, BigDecimal total
) {}

public interface OrderRepository extends JpaRepository<Order, Long> {

    @Query("""
        SELECT new com.app.dto.OrderSummary(
            o.id, c.name, o.total
        )
        FROM Order o JOIN o.customer c
        """)
    List<OrderSummary> findOrderSummaries();
    // 1 query, no entity loading, no lazy associations, no N+1 possible
}
```

**Example 4 — @BatchSize for reducing N+1 without JOIN FETCH:**

```java
@Entity
public class User {
    @OneToMany(mappedBy = "user", fetch = FetchType.LAZY)
    @BatchSize(size = 50)  // Load 50 users' orders per query
    private List<Order> orders;
}

// For 100 users:
// Without @BatchSize: 101 queries
// With @BatchSize(50): 3 queries (1 for users + 2 batch loads of 50)
// SELECT * FROM orders WHERE user_id IN (1,2,...,50)
// SELECT * FROM orders WHERE user_id IN (51,52,...,100)
```

---

### ⚖️ Comparison Table

| Solution              | Queries        | Use Case                   | Trade-offs                               |
| --------------------- | -------------- | -------------------------- | ---------------------------------------- |
| Lazy loading (no fix) | N+1            | Never in production loops  | Performance disaster                     |
| JOIN FETCH            | 1              | Need full entity graph     | Cartesian product, deduplication needed  |
| @EntityGraph          | 1              | Repository method-level    | Same as JOIN FETCH but declarative       |
| @BatchSize            | ceil(N/size)+1 | Fallback/second-level      | Still multiple queries, but manageable   |
| DTO Projection        | 1              | Read-only, specific fields | Best performance, no entity graph needed |
| Native SQL            | 1+             | Complex queries            | No ORM benefits, manual mapping          |

---

### ⚠️ Common Misconceptions

| Misconception                                        | Reality                                                                                                                                                           |
| ---------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Making all associations EAGER fixes N+1              | EAGER fetch in entity mapping means ALL queries for that entity also fetch the association — often worse than N+1 for use cases that don't need the data.         |
| JOIN FETCH on a collection always returns duplicates | Hibernate deduplicates at the in-memory level. Adding `DISTINCT` in JPQL or returning a `LinkedHashSet` handles this. Spring Data's `@Query` result type matters. |
| @BatchSize prevents N+1                              | @BatchSize REDUCES N+1 (N+1 becomes N/size + 1). It doesn't eliminate it. DTO projection or JOIN FETCH eliminate it.                                              |
| N+1 only happens with @OneToMany                     | N+1 can happen with any lazy association: @ManyToOne (loading user's department), @OneToOne, etc. Even @ManyToOne in a list triggers N+1 if accessed in a loop.   |

---

### 🚨 Failure Modes & Diagnosis

**Detecting N+1 in development**

**Enable SQL logging:**

```yaml
# application.yml
spring:
  jpa:
    show-sql: true
    properties:
      hibernate:
        format_sql: true

logging:
  level:
    org.hibernate.SQL: DEBUG
    org.hibernate.type.descriptor.sql: TRACE
```

**Or use Hibernate Statistics:**

```java
@SpringBootTest
class N1DetectionTest {

    @PersistenceContext EntityManager em;

    @Test
    void detectN1() {
        SessionFactory sf = em.getEntityManagerFactory().unwrap(SessionFactory.class);
        sf.getStatistics().setStatisticsEnabled(true);
        sf.getStatistics().clear();

        userRepo.findAll().forEach(u -> u.getOrders().size());  // trigger N+1

        long queryCount = sf.getStatistics().getQueryExecutionCount();
        assertThat(queryCount).isEqualTo(1);  // fails: reveals N+1
    }
}
```

---

**MultipleBagFetchException when JOIN FETCHing two collections**

**Symptom:** `org.hibernate.loader.MultipleBagFetchException: cannot simultaneously fetch multiple bags`

**Root Cause:** JOIN FETCHing two `List` associations simultaneously creates a Cartesian product that Hibernate can't correctly deduplicate.

**Fix:**

```java
// Option 1: Change one List to Set
@OneToMany(mappedBy = "user")
private Set<Order> orders;  // Set instead of List

// Option 2: Use @BatchSize on one association
@OneToMany
@BatchSize(size = 25)
private List<Tag> tags;  // Batch-load this one, JOIN FETCH the other

// Option 3: Separate queries (EntityGraphs don't solve MultipleBag either)
// Fetch users with orders first, then tags in a second query
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `@Transactional` — N+1 occurs within transaction sessions; lazy loading requires open session
- `Transaction Isolation Levels` — concurrent lazy load queries have isolation implications

**Builds On This (learn these next):**

- `Optimistic Locking` — `@Version` on entities where N+1 fix uses JOIN FETCH
- `Caching` — Second-level cache (Ehcache, Caffeine) can mitigate repeated lazy loads
- `Spring Data JPA Projections` — interface/DTO projections to avoid N+1 structurally

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────────┐
│ WHAT IT IS  │ 1 query for N entities + N queries for their  │
│             │ lazy associations = N+1 total queries         │
├─────────────┼────────────────────────────────────────────────┤
│ DETECTION   │ spring.jpa.show-sql=true → repeated SELECT    │
│             │ with WHERE id=? changing each iteration       │
├─────────────┼────────────────────────────────────────────────┤
│ FIXES       │ 1. JOIN FETCH (1 JOIN query)                  │
│             │ 2. @EntityGraph (declarative JOIN FETCH)      │
│             │ 3. DTO projection (best for read-only)        │
│             │ 4. @BatchSize (reduces to N/size+1 queries)   │
├─────────────┼────────────────────────────────────────────────┤
│ DON'T       │ EAGER on entity mapping — fetches for ALL     │
│             │ queries including those that don't need it    │
├─────────────┼────────────────────────────────────────────────┤
│ ONE-LINER   │ "Load N + access each N's lazy collection     │
│             │  = N+1 queries. JOIN FETCH = 1 query."        │
└─────────────┴────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** DTO projections completely avoid the N+1 problem — you write a JPQL query that returns exactly the data you need. But DTO projections can't use the JPA first-level cache (no entity is loaded). In a write-then-read pattern (save an entity, then query it via DTO projection), what consistency guarantees do you have? Could the DTO projection read stale data if the write is pending in the EntityManager's first-level cache but not yet flushed to the database? How does Hibernate's flush mode affect this?

**Q2.** The N+1 problem grows linearly: 100 entities = 101 queries. But with a deep association graph (User → Orders → OrderItems → Products → Categories), a single `getUsers()` with naive lazy access at every level becomes N × M × P × Q queries. At what point does this become worse than loading the entire database at once? What architectural decisions (CQRS, read models, materialized views) fundamentally change this trade-off?
