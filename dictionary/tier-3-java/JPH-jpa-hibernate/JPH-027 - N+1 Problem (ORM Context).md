---
id: JPH-027
title: "N+1 Problem (ORM Context)"
category: JPA & Hibernate
tier: tier-3-java
folder: JPH-jpa-hibernate
difficulty: ★★☆
depends_on: JPH-014, JPH-018, JPH-021, JPH-023, JPH-025, JPH-026
used_by: JPH-030, JPH-037, JPH-045, JPH-054
related: JPH-033, JPH-043
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
nav_order: 27
permalink: /jpa-hibernate/n-plus-1-problem/
---

# JPH-027 - N+1 Problem (ORM Context)

⚡ **TL;DR** - The N+1 problem: 1 query loads N entities,
then N additional queries load their associations (one
per entity). 100 orders load 100 separate supplier
queries = 101 total queries instead of 2. Root cause:
lazy loading triggered per-entity in a loop. Fixes:
JOIN FETCH in JPQL, `@EntityGraph`, `@BatchSize`, or
DTO projections. This is the most common JPA performance
bug in production.

| #027 | Category: JPA & Hibernate | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | JPQL, @OneToMany/@ManyToOne, FetchType, @Query, Pagination, @Transactional | |
| **Used by:** | DTO Projections, EntityGraph, Batch Processing, JPA at Scale | |
| **Related:** | First Level Cache, Spring Data Specifications | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT AWARENESS:**
An e-commerce application displays a list of orders with
their customer names. The developer writes:
`orderRepo.findAll()` (1 query returns 100 orders),
then the Thymeleaf template renders `order.getCustomer().getName()`
for each. Each `getCustomer()` triggers a lazy load ->
100 additional SELECT queries. 101 SQL statements go to
the database for what could have been 1 JOIN query.

**THE BREAKING POINT:**
In development with 20 orders: response time 150ms.
In staging with 500 orders: 500 + 1 = 501 queries, 2.5 seconds.
In production with 5,000 orders: 5,001 queries -> database
connection pool exhausted -> timeouts -> cascading failure.
The application was never explicitly coded to make 5,001
queries - the ORM generated them transparently.

**THE DISCOVERY MOMENT:**
Enabling Hibernate SQL logging reveals the explosion:
```
Hibernate: select * from orders
Hibernate: select * from customers where id=1
Hibernate: select * from customers where id=2
Hibernate: select * from customers where id=3
... (100 more) ...
```
The fix - a JOIN FETCH - collapses 101 queries into 1.

---

### 📘 Textbook Definition

**N+1 Problem** occurs when an application executes 1
query to load N parent entities, then executes N
additional queries to load associated entities for
each parent. Total database round-trips = N+1 instead
of 1 or 2.

It arises from ORM lazy loading: by default, associations
are loaded on first access (lazy proxy). When code
iterates N entities and accesses an association on each,
the proxy triggers N individual SELECT statements.

The problem is invisible at small data sizes and
catastrophic at production scale.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Loading N parent entities then accessing
a lazy association on each causes N extra queries -
N+1 queries total instead of one JOIN.

**One analogy:**
> You're a librarian fetching 100 book requests. First,
> you fetch the request list (1 query). Then, for each
> of the 100 requests, you separately look up the
> borrower's card in the filing cabinet (100 queries).
> The efficient version: fetch the request list WITH
> the borrower info using one JOIN (1 query total).
> The N+1 problem is making 101 trips to the filing
> cabinet instead of 1.

**One insight:** N+1 does not require LAZY fetch type
to exist. EAGER associations on `@ManyToOne` cause N+1
too - each entity load triggers separate EAGER joins.
The real cause is "accessing an unloaded association
in a loop."

---

### 🔩 First Principles Explanation

**THREE ROOT CAUSES:**

```
1. LAZY association accessed in iteration loop
   -> Each access fires proxy.load() -> SELECT

2. EAGER @ManyToOne on parent entity
   -> SELECT parent: "where id=1"
   -> (EAGER triggers) SELECT associated: "where id=X"
   -> One separate SELECT per parent (not a JOIN!)
   -> Hibernate uses separate queries, not always JOINs

3. @Query with JOIN FETCH but also Pageable
   -> HibernateJpaDialect: "firstResult/maxResults
      specified with collection fetch; applying in memory"
   -> Loads ALL rows, paginates in Java memory
   -> Effectively N+1 on steroids: loads everything
```

**HOW LAZY LOADING FIRES:**

```java
// 1 query: SELECT * FROM orders (returns 100 rows)
List<Order> orders = orderRepo.findAll();

// At this point: customer field on each Order is
// a Hibernate proxy (not yet loaded)

for (Order o : orders) {
    // THIS LINE: proxy.getName() triggers
    // SELECT * FROM customers WHERE id = ?
    // -> fires once per order = 100 SELECT queries
    System.out.println(o.getCustomer().getName());
}

// Total: 101 queries
```

---

### 🧪 Thought Experiment

**EAGER vs LAZY: BOTH CAN CAUSE N+1:**

```java
@Entity
public class Order {
    @ManyToOne(fetch = FetchType.EAGER) // EAGER
    private Customer customer;
}

// With EAGER: finding multiple orders by status
// JPQL: "FROM Order o WHERE o.status = :s"
// Hibernate: 
//   SELECT * FROM orders WHERE status=?  (returns N rows)
//   SELECT * FROM customers WHERE id=1   (per row!)
//   SELECT * FROM customers WHERE id=2
//   ...
// Hibernate does NOT automatically JOIN for EAGER @ManyToOne
// when querying a list. It fires individual SELECTs.
// This is N+1 with EAGER fetch!

// The only way EAGER triggers a JOIN is with
// em.find(Order.class, id) for a single entity.
// Collection queries with EAGER => N+1
```

**THE COUNTERINTUITIVE TRUTH:** Changing `FetchType.LAZY`
to `FetchType.EAGER` does NOT fix N+1. It makes it worse
by loading the association even when the caller does
not need it, AND still fires N separate queries.

---

### 🧠 Mental Model / Analogy

> The N+1 problem is like ordering a pizza with N
> toppings one at a time. "Give me a pizza base." The
> kitchen delivers it. "Now add pepperoni." Kitchen runs
> back. "Now add mushrooms." Another trip. N toppings =
> N kitchen trips + 1 for the base = N+1 trips.
>
> JOIN FETCH is like saying: "Give me a pizza with
> pepperoni and mushrooms in one order." The kitchen makes
> one trip with the complete pizza. The database JOIN
> returns parent + child data in one result set.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
N+1 is when the application asks the database for the
same data in many small requests instead of one efficient
request. Loading 100 orders then separately asking for
each order's customer one-by-one = N+1 queries.

**Level 2 - How to identify it (junior developer):**
Enable Hibernate SQL logging: `spring.jpa.show-sql=true`.
If you see 1 query followed by N nearly identical queries
(same table, different ID), you have N+1. The pattern is
unmistakable in logs.

**Level 3 - How to fix it (mid-level engineer):**
- **JOIN FETCH** in JPQL: `FROM Order o JOIN FETCH o.customer`
- **@EntityGraph**: `@EntityGraph(attributePaths = {"customer"})`
  on repository method
- **@BatchSize**: loads associations in batches of N
  instead of one-by-one (N/batch_size + 1 queries)
- **DTO Projection**: `SELECT new OrderDto(o.id, c.name)
  FROM Order o JOIN o.customer c` - no proxy involved

**Level 4 - Trade-offs (senior/staff):**
JOIN FETCH with pagination (`Pageable`) causes Hibernate
to warn "applying in memory" - it loads ALL rows into
memory and paginates in Java, not in SQL. This is because
SQL LIMIT/OFFSET with a JOIN that multiplies rows
produces incorrect page counts. Fix: use `@BatchSize`,
`@EntityGraph` with subselect, or two queries (page IDs
first, then fetch with JOIN FETCH by ID list).

**Level 5 - Architecture (distinguished engineer):**
N+1 at scale (millions of rows, microservices) requires
architectural decisions. Options: (1) Denormalize reads
with a read model (CQRS) so no JOIN is needed. (2) Use
DTO projections with native SQL or JOOQ where ORM is
bypassed entirely. (3) Store aggregates as JSON columns
for read-heavy data. (4) Cache association lookups at
the service layer with Caffeine or Redis. For high-QPS
APIs, even 2 queries per request vs 1 matters; tracking
query count per request as a metric catches N+1 regressions
before production.

---

### ⚙️ How It Works (Mechanism)

**HIBERNATE PROXY MECHANISM:**

```
1. Hibernate loads Order entity from DB
2. customer field: Hibernate creates a HibernateProxy
   subclass of Customer with only the id populated
3. Proxy.isLoaded() = false; real data not fetched
4. When code calls proxy.getName():
   a. Proxy intercept fires
   b. Proxy calls EntityManager to load Customer by id
   c. SELECT * FROM customers WHERE id=?
   d. Customer fields populated
   e. proxy.getName() returns the value
5. Step 4 fires ONCE PER ENTITY in the loop
```

**DETECTION TOOLS:**

```java
// 1. Hibernate SQL log:
spring.jpa.show-sql=true
logging.level.org.hibernate.SQL=DEBUG
logging.level.org.hibernate.type.descriptor.sql=TRACE

// 2. p6spy (SQL interceptor with timing):
// Shows every SQL + elapsed time; easy to spot duplicates

// 3. datasource-proxy (Spring Boot):
// Can count queries per request in tests
@Bean
DataSource dataSource(DataSourceProperties props) {
    return ProxyDataSourceBuilder
        .create(actualDs)
        .countQuery()
        .build();
}

// 4. Production APM (Datadog, New Relic):
// Slow endpoint traces reveal query explosion
// Look for "SQL call count" spike on specific endpoints
```

---

### 🔄 The Complete Picture - End-to-End Flow

**N+1 DETECTION AND FIX:**

```java
// ===== PROBLEM: N+1 in service =====
@Transactional(readOnly = true)
public List<OrderDto> getOrders() {
    List<Order> orders = orderRepo.findAll();
    // 1 SELECT from orders
    return orders.stream()
        .map(o -> new OrderDto(
            o.getId(),
            o.getCustomer().getName())) // N SELECTs!
        .collect(toList());
}

// ===== FIX 1: JOIN FETCH in @Query =====
@Query("SELECT o FROM Order o " +
       "JOIN FETCH o.customer c " +
       "WHERE o.status = :status")
List<Order> findWithCustomer(
    @Param("status") String status);
// 1 SELECT with JOIN -> no lazy loads

// ===== FIX 2: @EntityGraph =====
@EntityGraph(attributePaths = {"customer"})
List<Order> findByStatus(String status);
// Spring Data adds LEFT JOIN FETCH to the query

// ===== FIX 3: @BatchSize (Hibernate annotation) =====
@Entity
public class Order {
    @ManyToOne
    @BatchSize(size = 25)  // load 25 customers at once
    private Customer customer;
}
// Instead of N queries: ceil(N/25) queries
// Trade-off: still multiple queries but dramatically fewer

// ===== FIX 4: DTO projection (best for read endpoints)=====
@Query("SELECT new com.example.OrderDto(" +
       "o.id, c.name) " +
       "FROM Order o JOIN o.customer c " +
       "WHERE o.status = :status")
List<OrderDto> findOrderDtos(
    @Param("status") String status);
// No entities loaded; no lazy proxies; 1 query
```

---

### 💻 Code Example

**Example 1 - BAD: Classic N+1 detection:**

```java
// Enable: spring.jpa.show-sql=true
// Watch the log:

List<Post> posts = postRepo.findAll();
// Hibernate: select * from post   <- 1 query

for (Post p : posts) {
    System.out.println(p.getAuthor().getName());
    // Hibernate: select * from author where id=1
    // Hibernate: select * from author where id=2
    // Hibernate: select * from author where id=3
    // ... N queries for N posts
}
// Total: N + 1 queries
```

**Example 2 - BAD: JOIN FETCH with Pageable (wrong fix):**

```java
// BAD: JOIN FETCH + Pageable -> Hibernate loads ALL rows
@Query("SELECT o FROM Order o " +
       "JOIN FETCH o.items " +  // items is @OneToMany
       "WHERE o.status = :s")
Page<Order> findPaged(
    @Param("s") String s, Pageable pageable);

// Hibernate warning:
// "HHH90003004: firstResult/maxResults specified with
//  collection fetch; applying in memory!"
// -> Loads ALL orders + all items into RAM
// -> Paginates in Java, not SQL
// -> Memory OOM with large tables
```

**Example 3 - GOOD: Two-query approach for pagination:**

```java
// Step 1: page IDs only (no JOIN, LIMIT works correctly)
@Query("SELECT o.id FROM Order o " +
       "WHERE o.status = :s ORDER BY o.createdAt DESC")
Page<Long> findOrderIds(
    @Param("s") String s, Pageable pageable);

// Step 2: fetch entities + associations by IDs
@Query("SELECT o FROM Order o " +
       "JOIN FETCH o.items " +
       "WHERE o.id IN :ids")
List<Order> findByIdsWithItems(
    @Param("ids") List<Long> ids);

// Service:
@Transactional(readOnly = true)
public Page<OrderDto> getPagedOrders(Pageable pageable) {
    Page<Long> ids = repo.findOrderIds("ACTIVE",pageable);
    List<Order> orders = repo.findByIdsWithItems(
        ids.getContent());
    // Only 2 queries; correct pagination; no memory blowup
    return ids.map(id -> toDto(
        orders.stream()
            .filter(o -> o.getId().equals(id))
            .findFirst().orElseThrow()));
}
```

---

### ⚖️ Comparison Table

| Fix | Queries | Works with Pageable? | Use case |
|---|---|---|---|
| JOIN FETCH | 1 | No (in-memory pagination) | Non-paginated lists |
| @EntityGraph | 1 | No (same as JOIN FETCH) | Read-heavy single associations |
| @BatchSize | ceil(N/size)+1 | Yes | When JOIN FETCH is impractical |
| Two-query (IDs then fetch) | 2 | Yes | Paginated lists with associations |
| DTO projection | 1 | Yes | Read-only APIs (best performance) |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Changing from LAZY to EAGER fixes N+1" | EAGER on a collection query still generates N separate queries (not a JOIN). It also loads data even when not needed. EAGER makes N+1 worse, not better. |
| "JOIN FETCH always works" | JOIN FETCH multiplies rows for @OneToMany collections. With Pageable, Hibernate loads ALL rows in memory and paginates in Java, causing `HHH90003004` warning and potential OOM. |
| "@EntityGraph solves all N+1 problems" | @EntityGraph uses LEFT JOIN FETCH. Same limitation as JOIN FETCH when used with Pageable (collection associations). Works well for @ManyToOne and @OneToOne. |
| "N+1 only occurs with LAZY loading" | N+1 occurs whenever an association is loaded per-entity in a loop. Even EAGER @ManyToOne in a collection query causes N separate SELECTs (Hibernate queries each by ID). |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Production Timeout Under Load**

**Symptom:** Endpoint works fine locally (20 records).
In production with 5,000 records, the endpoint times out.
DB CPU spikes. Connection pool exhausted.
**Diagnosis:**
```
# Enable slow query logging in application
spring.jpa.properties.hibernate.generate_statistics=true
spring.jpa.properties.hibernate.session.events.log.LOG_QUERIES_SLOWER_THAN_MS=10

# Or check application log for repeated queries:
grep "select.*from customers where id=" app.log | wc -l
# If count approaches N (number of orders), it's N+1

# Use p6spy or datasource-proxy in staging:
# Reports total SQL count per request
```
**Fix:** Add JOIN FETCH or @EntityGraph to the repository
method, or use DTO projections.

---

**Failure Mode 2: HHH90003004 Warning (In-Memory Pagination)**

**Symptom:**
`HHH90003004: firstResult/maxResults specified with
collection fetch; applying in memory`
**Root Cause:** JOIN FETCH on a `@OneToMany` collection
combined with `Pageable`. SQL LIMIT/OFFSET does not
work correctly with collection JOINs (which multiply rows).
Hibernate falls back to loading all data and paginating
in Java.
**Fix:** Use the two-query approach (page IDs first, then
JOIN FETCH by ID list) or `@BatchSize` instead of JOIN FETCH.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[JPH-018 - @OneToMany and @ManyToOne]] - the associations
  that most commonly cause N+1
- [[JPH-021 - FetchType]] - LAZY vs EAGER; why EAGER does
  not fix N+1
- [[JPH-014 - JPQL]] - JOIN FETCH syntax
- [[JPH-026 - @Transactional]] - N+1 fires within a transaction

**Builds On This (learn these next):**
- [[JPH-037 - EntityGraph]] - `@EntityGraph` as a
  structured fix for N+1
- [[JPH-030 - DTO Projections]] - best long-term fix for
  read-only N+1 scenarios
- [[JPH-045 - Hibernate Batch Processing]] - `@BatchSize`
  for reducing N+1 to N/batch queries

**Related:**
- [[JPH-033 - First Level Cache]] - repeated loads of the
  same ID are cached; N+1 with same IDs hits 1L cache
- [[JPH-054 - JPA at Scale]] - N+1 in high-QPS services

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ DETECT       │ show-sql=true; look for N identical SELECTs│
│              │ differing only by WHERE id=?              │
├──────────────┼───────────────────────────────────────────┤
│ ROOT CAUSE   │ Lazy proxy accessed in loop               │
│              │ OR EAGER ManyToOne in collection query    │
├──────────────┼───────────────────────────────────────────┤
│ FIX (simple) │ JOIN FETCH or @EntityGraph (no Pageable)  │
├──────────────┼───────────────────────────────────────────┤
│ FIX (paged)  │ Two-query: page IDs, then fetch by IDs   │
│              │ OR @BatchSize on association              │
├──────────────┼───────────────────────────────────────────┤
│ FIX (best)   │ DTO projection: no entities, no proxies  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID        │ Changing LAZY->EAGER: doesn't fix N+1    │
│              │ JOIN FETCH + Pageable: in-memory OOM risk │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "1 query loads N entities, N lazy loads  │
│              │ fire = N+1 total. Fix: JOIN FETCH, Entity │
│              │ Graph, BatchSize, or DTO projection."    │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. N+1 = 1 query loads N parents, then N queries load
   each parent's association = N+1 total queries
2. Switching LAZY to EAGER does NOT fix N+1; JOIN FETCH
   or @EntityGraph do (but not with Pageable on @OneToMany)
3. DTO projections are the cleanest fix for read-only
   APIs - no entity loading, no lazy proxies, one query

**Interview one-liner:** N+1 is when loading N entities
triggers N additional queries for lazy-loaded associations.
Caused by lazy proxy access in a loop or EAGER fetch on
collection queries. Fixes: JOIN FETCH (no pagination),
@EntityGraph (same caveat), @BatchSize (paged OK),
two-query approach (IDs then fetch), or DTO projections.
Changing LAZY to EAGER does NOT fix it.

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** ORM transparency is
a double-edged sword. The ORM hides SQL complexity and
makes code readable, but it also hides query count.
Transparent lazy loading means "the obvious code" (loop
and access associations) generates catastrophic SQL.
This pattern repeats in all ORMs: ActiveRecord has N+1
(use `includes:`), Django has N+1 (use `select_related`/
`prefetch_related`), TypeORM/Sequelize have it too (use
`relations` in findOptions). The principle: always know
how many SQL queries your data access layer generates.
Establish a "max queries per request" metric in tests.

**Where else this pattern appears:**
- **GraphQL** - N+1 in resolvers (each field resolver
  loads data separately). Fix: DataLoader (batch loading)
- **REST API clients** - N+1 across services: fetch list
  of user IDs from service A, then N calls to service B
  per ID. Fix: bulk/batch API endpoint
- **Django** - `select_related` (JOIN, like JOIN FETCH),
  `prefetch_related` (separate IN query, like @BatchSize)
- **ActiveRecord** - `includes :customer` triggers one
  additional query with IN clause (like @BatchSize)

---

### 💡 The Surprising Truth

The most dangerous N+1 pattern in Spring applications
is NOT in a service method - it is in the REST controller
layer via `@JsonProperty` serialization. The entity is
loaded in a `@Transactional` service method, returned
to the controller, and then Jackson serializes the entity
to JSON. During serialization (OUTSIDE the transaction),
Jackson accesses every field including lazy associations,
triggering proxy loads. Since the persistence context
is closed (transaction ended), this causes `LazyInitializationException`.
If Open EntityManager In View (OEIV) is enabled (Spring Boot
default: true), the persistence context stays open for
the entire HTTP request, which "fixes" the exception but
silently re-enables N+1 during JSON serialization.
This is why disabling OEIV (`spring.jpa.open-in-view=false`)
is recommended: it forces developers to explicitly fetch
all required associations within the transaction boundary.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **REPRODUCE** an N+1 scenario in code and confirm it
   via Hibernate SQL logs showing repeated queries
2. **APPLY** three different fixes (JOIN FETCH, @EntityGraph,
   DTO projection) and explain when each is appropriate
3. **DIAGNOSE** the `HHH90003004` in-memory pagination
   warning and implement the two-query alternative
4. **EXPLAIN** why EAGER does not fix N+1 and can make
   it worse
5. **CONFIGURE** datasource-proxy or p6spy to count
   queries per request in an integration test

---

### 🎯 Interview Deep-Dive

**Q1: What is the N+1 problem, and how would you detect
it in production?**
*Why they ask:* Core JPA question. Tests both understanding
and operational awareness.
*Strong answer includes:*
- Definition: 1 query loads N parents, N lazy loads fire
  = N+1 total; instead of 1-2 with JOIN
- Detection in development: `spring.jpa.show-sql=true`,
  look for repeated identical queries with different ID
- Detection in production: APM query count per trace
  (Datadog, New Relic), p6spy in staging, Hibernate
  statistics (`hibernate.generate_statistics=true`)
- Log pattern: `select * from customers where id=?`
  appearing N times in a single request trace

**Q2: You have a paginated endpoint returning orders with
customer data. Your JOIN FETCH fix causes the Hibernate
in-memory pagination warning. How do you fix it?**
*Why they ask:* Tests deep practical knowledge combining
N+1, JOIN FETCH, and pagination limitations.
*Strong answer includes:*
- Root cause: JOIN FETCH on @OneToMany multiplies rows;
  SQL LIMIT/OFFSET cannot paginate correctly; Hibernate
  loads all rows and paginates in Java
- Fix: two-query approach
  1. `Page<Long> orderIds = findOrderIds(pageable)` - pages
     correctly because no JOIN
  2. `findByIdsWithItems(ids)` - JOIN FETCH by the paged
     ID list - returns only the N items for this page
- Alternative: @BatchSize on the `items` collection -
  no JOIN FETCH needed; loads items in batches
- Best for read-only: DTO projection with native SQL or JOOQ

**Q3: Why does changing FetchType from LAZY to EAGER not
fix the N+1 problem?**
*Why they ask:* Tests understanding of HOW Hibernate loads
EAGER associations in collection queries.
*Strong answer includes:*
- `em.find(Order.class, id)` for a single entity: EAGER
  triggers a JOIN (one query)
- JPQL collection query `FROM Order WHERE status=X`:
  Hibernate loads the result set (N rows from the orders
  table) and then loads EAGER associations with
  SEPARATE SELECT statements per entity - N extra queries
- EAGER just means "load immediately" not "load with JOIN"
  in collection queries
- Only explicit JOIN FETCH in JPQL forces a SQL JOIN
- EAGER also loads data when NOT needed, wasting resources