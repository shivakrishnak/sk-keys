---
id: JPH-037
title: "EntityGraph (Solving N+1)"
category: JPA & Hibernate
tier: tier-3-java
folder: JPH-jpa-hibernate
difficulty: ★★★
depends_on: JPH-006, JPH-007, JPH-008, JPH-014, JPH-018, JPH-021, JPH-022, JPH-027
used_by: JPH-054, JPH-056, JPH-058
related: JPH-025, JPH-043, JPH-045
tags:
  - java
  - jpa
  - database
  - advanced
status: complete
version: 4
layout: default
parent: "JPA & Hibernate"
grand_parent: "Technical Dictionary"
nav_order: 37
permalink: /jpa-hibernate/entity-graph/
---

# JPH-037 - EntityGraph (Solving N+1)

⚡ **TL;DR** - `@EntityGraph` tells JPA to eagerly fetch
specified associations in a single JOIN query, overriding
the default LAZY fetch strategy for that one query. Use
it to solve N+1 problems where JOIN FETCH in JPQL is
not practical. Critical limits: EntityGraph + `Pageable`
causes HHH90003004 (in-memory pagination) for collections
- same problem as JOIN FETCH. Solution: two-query approach
(fetch IDs first, then fetch entities by ID with EntityGraph).

| #037 | Category: JPA & Hibernate | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | @Entity, Relationships, @OneToMany, JPQL, LAZY Loading, Fetch Types, N+1 Problem | |
| **Used by:** | JPA at Scale, Spring Data JPA Architecture, Hibernate Internals | |
| **Related:** | Pagination, Specifications, Batch Processing | |

---

### 🔥 The Problem This Solves

**N+1 CONTEXT:**
You have `Order` with a `@OneToMany(fetch=LAZY)` collection
`orderItems`. Loading 100 orders in a list view requires:
1 query for orders + 100 queries for items (N+1 = 101 queries).

**WITH JOIN FETCH IN JPQL:**
`SELECT o FROM Order o JOIN FETCH o.orderItems` solves
N+1 for simple cases. But fails for pagination:
adding Pageable causes HHH90003004 (in-memory pagination
of the FULL result set).

**WITH @EntityGraph:**
`@EntityGraph(attributePaths = {"orderItems"})` on a
repository method generates a LEFT JOIN in the SQL -
same as JOIN FETCH but expressed at the method level,
not in the query string. Works with Spring Data
`findById`, `findAll`, and custom queries. Still has
the same Pageable/collection limitation.

**THE REAL SOLUTION:**
EntityGraph solves N+1 for: `findById` (single entity),
`findAll` without pagination, or `findAllByXxx` when
result sets are small. For paginated lists: use the
two-query pattern (count + IDs query, then fetch by IDs
with EntityGraph).

---

### 📘 Textbook Definition

**@EntityGraph** is a JPA 2.1 feature that allows specifying
at query time which entity associations should be fetched
eagerly, overriding the default fetch strategy. Two types:
- **@NamedEntityGraph** - declares the graph on the entity class
- **@EntityGraph** on repository method - references a named
  graph or specifies `attributePaths` inline
- **EntityGraphType.FETCH** (default) - specified associations
  are EAGER; all others LAZY
- **EntityGraphType.LOAD** - specified associations are EAGER;
  all others use their mapped fetch type

**Effect:** Hibernate generates a LEFT JOIN FETCH in SQL
for each specified association, loading all data in one
query instead of N queries.

---

### ⏱️ Understand It in 30 Seconds

**One line:** `@EntityGraph` tells JPA "for THIS query,
also load these associations via JOIN" - solving N+1
without changing the entity's global fetch strategy.

**One analogy:**
> Entity associations are like books in a library with
> two checkout modes: "on-demand" (LAZY - you request
> each book separately when needed) and "bundled" (EAGER -
> all related books delivered together). Changing the
> entity's `fetch=EAGER` is like changing the library's
> global policy for everyone. `@EntityGraph` is like
> saying "for THIS patron's checkout, bundle these specific
> books" - request-scoped, not global.

**One insight:** `@EntityGraph` and `JOIN FETCH` in JPQL
generate identical SQL. The difference is where the fetch
instruction lives: in the query string (JPQL) vs on the
repository method (`@EntityGraph`). EntityGraph wins for
readability when the same JPQL query needs different
association loading strategies in different contexts.

---

### 🔩 First Principles Explanation

**ENTITY SETUP:**

```java
@Entity
@NamedEntityGraph(
    name = "Order.withItems",
    attributeNodes = @NamedAttributeNode("orderItems")
)
public class Order {
    @Id private Long id;
    private String status;

    @OneToMany(mappedBy = "order",
               fetch = FetchType.LAZY)
    private List<OrderItem> orderItems;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "customer_id")
    private Customer customer;
}
```

**REPOSITORY WITH @EntityGraph:**

```java
public interface OrderRepository
        extends JpaRepository<Order, Long> {

    // References @NamedEntityGraph by name:
    @EntityGraph("Order.withItems")
    Optional<Order> findById(Long id);

    // Inline attributePaths (no @NamedEntityGraph needed):
    @EntityGraph(attributePaths = {"orderItems"})
    List<Order> findByStatus(String status);

    // Multiple associations:
    @EntityGraph(attributePaths = {
        "orderItems",
        "orderItems.product",  // nested navigation
        "customer"
    })
    Optional<Order> findWithFullGraphById(Long id);
}
```

**GENERATED SQL:**

```sql
-- @EntityGraph(attributePaths = {"orderItems"})
SELECT o.*, oi.*
FROM orders o
LEFT JOIN order_items oi ON oi.order_id = o.id
WHERE o.status = ?
-- 1 query for all orders + their items (no N+1)

-- Without EntityGraph:
SELECT * FROM orders WHERE status = ?          -- 1
SELECT * FROM order_items WHERE order_id = 1  -- N
SELECT * FROM order_items WHERE order_id = 2  -- N
-- ... N more queries
```

---

### 🧪 Thought Experiment

**ENTITYGRAPH vs FETCH=EAGER - WHY NOT JUST USE EAGER?**

```java
// Option A: EAGER on the entity
@OneToMany(fetch = FetchType.EAGER)
private List<OrderItem> orderItems;

// Problem: EVERY query for Order loads orderItems
// findById: LEFT JOIN (wanted - 1 query instead of N+1)
// findAll: LEFT JOIN (maybe unwanted - loads 1M rows)
// countBy: LEFT JOIN (insane - counting causes full join)
// DELETE query: still joins (pointless)
// Every Criteria/JPQL query: LEFT JOIN added

// Option B: LAZY + @EntityGraph on specific methods
@OneToMany(fetch = FetchType.LAZY)
private List<OrderItem> orderItems;

@EntityGraph(attributePaths = {"orderItems"})
Optional<Order> findById(Long id); // <- join only here

// findAll: no join (only loads orders, items loaded lazily)
// countBy: no join (efficient)
// findById: join (N+1 solved only where needed)

// RULE: Default LAZY. Use EntityGraph for specific methods.
```

---

### 🧠 Mental Model / Analogy

> LAZY loading is "just-in-time" delivery - items ordered
> when needed. EAGER is "always-preload" - items always
> shipped with every order, whether you need them or not.
> EntityGraph is "request-specific bundling" - this specific
> query bundles X, Y, Z; all other queries use just-in-time.
>
> Changing `fetch=EAGER` affects ALL queries globally.
> EntityGraph affects exactly the methods you annotate.
> This per-query control is why EntityGraph is preferred.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
`@EntityGraph` tells JPA to load an entity's related data
(e.g., an order's items) in the same database query, instead
of making separate queries for each order. This prevents
the "N+1 query problem."

**Level 2 - How to add it (junior developer):**
Add `@EntityGraph(attributePaths = {"orderItems"})` above
a repository method that needs to load an `Order` with
its `orderItems`. Hibernate automatically generates a
LEFT JOIN in the SQL. No JPQL change needed.

**Level 3 - How it works (mid-level engineer):**
`@EntityGraph` generates a `javax.persistence.fetchgraph`
or `loadgraph` hint on the query. Hibernate applies this
hint during SQL generation: it adds a `LEFT JOIN FETCH`
for each attribute path. The result is equivalent to
writing `SELECT o FROM Order o LEFT JOIN FETCH o.orderItems`
in JPQL but expressed at the repository method level.

**Level 4 - Limitations (senior engineer):**
EntityGraph with a collection association + `Pageable`
causes HHH90003004: Hibernate fetches all matching rows
into memory and then paginates in Java - not in SQL.
This defeats the purpose of pagination for large result
sets. Solution: the two-query pattern. First query:
`SELECT o.id FROM Order o` with pagination (gets page
of IDs). Second query: `findAllById(ids)` with EntityGraph
(fetches full entities with associations for those IDs).

**Level 5 - Cartesian product risk (staff engineer):**
EntityGraph with multiple collections (`orderItems` AND
`orderTags`) generates a cross-join - the Cartesian product
produces duplicate parent rows. Hibernate deduplicates
entities in memory (via `distinct` semantics), but the
SQL returns `M * N` rows (M items x N tags per order).
With 100 orders, 10 items, 5 tags each: 100*10*5 = 5,000
rows sent over the wire, deduplicated to 100 orders.
Solution: load multiple collections with separate queries
(`@BatchSize` or separate EntityGraph calls) not
simultaneous JOIN FETCH of both collections.

---

### ⚙️ How It Works (Mechanism)

**ENTITYGRAPH TYPES:**

```java
// FETCH graph (default):
// Specified paths -> EAGER; everything else -> LAZY
@EntityGraph(
    value = "Order.withItems",
    type = EntityGraph.EntityGraphType.FETCH
)

// LOAD graph:
// Specified paths -> EAGER; everything else -> uses MAPPED fetch
@EntityGraph(
    value = "Order.withItems",
    type = EntityGraph.EntityGraphType.LOAD
)
// Difference: If Customer has fetch=EAGER mapped on entity,
// FETCH graph overrides it to LAZY (unless also in graph).
// LOAD graph respects the mapped fetch for non-listed paths.
```

**NESTED ATTRIBUTE PATHS:**

```java
// Loads Order -> orderItems -> product (3 levels)
@EntityGraph(attributePaths = {
    "orderItems",
    "orderItems.product",      // product of each item
    "orderItems.product.category"  // category of product
})
Optional<Order> findWithDeepGraphById(Long id);

// SQL:
// SELECT o.*, oi.*, p.*, cat.*
// FROM orders o
// LEFT JOIN order_items oi ON ...
// LEFT JOIN products p ON ...
// LEFT JOIN categories cat ON ...
// WHERE o.id = ?
```

---

### 🔄 The Complete Picture - End-to-End Flow

**TWO-QUERY PATTERN FOR PAGINATED LISTS:**

```java
@Repository
public class OrderQueryRepository {

    @PersistenceContext
    private EntityManager em;

    private final OrderRepository orderRepo;

    public Page<Order> findOrdersWithItems(
            String status, Pageable pageable) {

        // Step 1: Count query (no joins needed)
        long count = em.createQuery(
            "SELECT COUNT(o) FROM Order o WHERE o.status=:s",
            Long.class)
            .setParameter("s", status)
            .getSingleResult();
        if (count == 0) return Page.empty(pageable);

        // Step 2: ID query (small result, proper SQL LIMIT)
        List<Long> ids = em.createQuery(
            "SELECT o.id FROM Order o " +
            "WHERE o.status=:s " +
            "ORDER BY o.createdAt DESC",
            Long.class)
            .setParameter("s", status)
            .setFirstResult((int) pageable.getOffset())
            .setMaxResults(pageable.getPageSize())
            .getResultList();
        if (ids.isEmpty()) return new PageImpl<>(
            Collections.emptyList(), pageable, count);

        // Step 3: Fetch entities with associations
        // EntityGraph on this method handles N+1:
        List<Order> orders = orderRepo
            .findAllWithItemsAndCustomerByIdIn(ids);

        // Restore sort order from IDs query
        Map<Long, Order> orderMap = orders.stream()
            .collect(Collectors.toMap(Order::getId, o -> o));
        List<Order> sorted = ids.stream()
            .map(orderMap::get)
            .collect(Collectors.toList());

        return new PageImpl<>(sorted, pageable, count);
    }
}

// Repository method with EntityGraph:
@EntityGraph(attributePaths = {"orderItems", "customer"})
List<Order> findAllWithItemsAndCustomerByIdIn(
    Collection<Long> ids);
```

---

### 💻 Code Example

**Example 1 - BAD: EntityGraph + Pageable on collection:**

```java
// BAD: causes HHH90003004 - in-memory pagination
@EntityGraph(attributePaths = {"orderItems"})
Page<Order> findByStatus(String status, Pageable pageable);
// Hibernate warning:
// HHH90003004: firstResult/maxResults specified with
// collection fetch; applying in memory!
// Fetches ALL orders + ALL items; paginates in Java
// -> full table scan for every page
```

**Example 2 - GOOD: EntityGraph for single-entity load:**

```java
// GOOD: single entity by ID - no pagination, no N+1
@EntityGraph(attributePaths = {"orderItems",
                                "orderItems.product",
                                "customer"})
Optional<Order> findById(Long id);
// SELECT order + items + products + customer in 1 query
// Appropriate use: detail page, order processing
```

---

### ⚖️ Comparison Table

| Approach | N+1 Solved? | Works with Pageable? | Verbosity | Best for |
|---|---|---|---|---|
| `fetch=EAGER` | Yes | No (HHH90003004) | Low | Avoid |
| JOIN FETCH (JPQL) | Yes | No for collections | Medium | Single associations |
| `@EntityGraph` | Yes | No for collections | Low | Same as JOIN FETCH, cleaner |
| Two-query pattern | Yes | Yes | High | Paginated lists |
| `@BatchSize` | Partial (batch) | Yes | Low | Large collection lists |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "@EntityGraph fixes N+1 for paginated lists" | EntityGraph + `Pageable` + collection = HHH90003004 (in-memory pagination). Same problem as JOIN FETCH + Pageable. Fix: two-query pattern. |
| "EntityGraph overrides ALL associations to EAGER" | Only the associations listed in `attributePaths`. All others remain LAZY (with FETCH graph type, default). Unlisted mappings with `fetch=EAGER` on the entity ARE overridden to LAZY when using FETCH type. |
| "Using multiple attributePaths for multiple collections is safe" | Multiple collection JOIN FETCHes produce a Cartesian product. 10 items * 5 tags = 50 rows per parent entity. Can severely increase result set size. Use @BatchSize or separate queries for multiple collections. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode: HHH90003004 Warning + Slow Pagination**

**Symptom:** Logs show `HHH90003004: firstResult/maxResults
specified with collection fetch; applying in memory!`.
API pages 1-10 all take the same time (not improving
as offset increases) - all pages scan the full table.
**Root Cause:** `@EntityGraph` with a collection
(`@OneToMany`) on a method that accepts `Pageable`.
Hibernate can't apply SQL LIMIT when collection JOINs
multiply rows - so it fetches everything and paginates in Java.
**Fix:** Remove EntityGraph from the paginated method.
Use the two-query pattern: page IDs with SQL LIMIT, then
fetch entities with EntityGraph by IDs.

---

**Failure Mode: Cartesian Product / Duplicate Results**

**Symptom:** `Order` entities appear multiple times in
results. `orders.size()` returns 500 when expecting 50.
**Root Cause:** Multiple collection associations in
EntityGraph (e.g., `orderItems` AND `orderTags`).
Each item*tag combination produces a row. Hibernate
assembles duplicate order objects for each row.
**Fix:** Remove one collection from EntityGraph.
Use `@BatchSize` on the second collection, or load the
second collection in a separate query.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[JPH-027 - N+1 Problem]] - EntityGraph is one solution;
  understand the problem first
- [[JPH-018 - @OneToMany]] - EntityGraph applies to
  association mappings

**Builds On This (learn these next):**
- [[JPH-054 - JPA at Scale]] - EntityGraph usage patterns
  in high-load production systems

**Related:**
- [[JPH-025 - Pagination]] - HHH90003004 is the interaction
  between EntityGraph and pagination
- [[JPH-043 - Spring Data Specifications]] - Specifications
  can be combined with EntityGraph via `findAll(spec, pageable)`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ ON METHOD    │ @EntityGraph(attributePaths = {"items"})  │
│ ON ENTITY    │ @NamedEntityGraph(name="X",               │
│              │   attributeNodes=@NamedAttributeNode("x"))│
├──────────────┼───────────────────────────────────────────┤
│ GENERATES    │ LEFT JOIN in SQL; 1 query instead of N+1  │
├──────────────┼───────────────────────────────────────────┤
│ WARNING      │ + Pageable + collection = HHH90003004    │
│ FIX          │ Two-query: page IDs, then fetch by IDs   │
├──────────────┼───────────────────────────────────────────┤
│ MULTI-COLL   │ Cartesian product! Use @BatchSize instead │
├──────────────┼───────────────────────────────────────────┤
│ RULE         │ Default LAZY everywhere; EntityGraph only │
│              │ on specific methods that need eager load  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "@EntityGraph adds LEFT JOIN to a single │
│              │ query; not a global change. No fix for   │
│              │ Pageable+collection; use two-query."     │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. `@EntityGraph` generates a LEFT JOIN FETCH for named
   associations - solves N+1 for non-paginated queries
2. EntityGraph + `Pageable` + collection = HHH90003004
   (in-memory pagination) - fix with the two-query pattern
3. Multiple collection EntityGraphs produce Cartesian
   products; use `@BatchSize` or separate queries instead

**Interview one-liner:** `@EntityGraph` is a per-method
fetch strategy override - it adds LEFT JOIN FETCH for
specified associations, solving N+1 without changing the
entity's global `fetch` type. Critical limitation: combined
with `Pageable` for collection associations, it triggers
HHH90003004 (in-memory pagination). Fix: separate ID
pagination query, then entity fetch with EntityGraph by ID.

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Global configuration
changes are dangerous for performance. Per-request
(per-query) specification is safer. Entity `fetch=EAGER`
is global: affects ALL queries on that entity. EntityGraph
is per-method: affects exactly the queries you intend.
This "scope of effect" principle generalizes: database
indexes should target specific query patterns, not all
queries on a table; caching should target specific
read-heavy paths, not all service methods; connection
pool settings should match specific workload patterns.
Precision of effect reduces unintended side effects.

**Where else this pattern appears:**
- **SQL query hints** - `/*+ INDEX(t idx_name) */` applies
  an index hint to one specific query, not globally
- **@Transactional isolation levels** - specify isolation
  per method where needed, not globally for all transactions
- **Spring @Cacheable** - cache specific methods, not
  all methods on a class

---

### 💡 The Surprising Truth

`@EntityGraph` and `JOIN FETCH` in JPQL generate
identical SQL - both add a `LEFT OUTER JOIN`. The
practical difference: JPQL `JOIN FETCH` must be written
into the query string (affects every repository method
that uses that query), while `@EntityGraph` is a method-
level annotation (same query string, different loading
per method). This means you can share a `@NamedEntityGraph`
across multiple repository methods with different
attribute sets, without duplicating JPQL. However, Spring
Data's derived query generation (`findByStatus`) cannot
use `JOIN FETCH` in the generated JPQL at all - EntityGraph
is the ONLY way to specify eager loading on derived
queries without writing custom JPQL. This makes EntityGraph
essential for Spring Data JPA's derived query feature.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **WRITE** an `@EntityGraph` that loads `Order` with
   its `orderItems` and each item's `product` in one query
2. **EXPLAIN** why EntityGraph + Pageable + @OneToMany
   causes HHH90003004 and how to verify it with SQL logs
3. **IMPLEMENT** the two-query pattern for paginated
   list with associations (ID query, then EntityGraph fetch)
4. **DIAGNOSE** Cartesian product issues with multiple
   collection EntityGraphs and propose the @BatchSize fix
5. **COMPARE** EntityGraph, JOIN FETCH, @BatchSize, and
   the two-query pattern for four specific use cases

---

### 🎯 Interview Deep-Dive

**Q1: What is @EntityGraph and how does it solve N+1?**
*Why they ask:* Core JPA performance concept.
*Strong answer includes:*
- `@EntityGraph` is a per-method fetch strategy override
- Generates a LEFT JOIN FETCH in SQL for specified associations
- Identical SQL to `JOIN FETCH` in JPQL; difference: expressed
  at method level, not in query string
- Useful for derived queries (can't write JOIN FETCH in derived query)
- Solves N+1 for non-paginated methods: `findById`, `findByStatus`

**Q2: Why does @EntityGraph with Pageable on a collection
association cause a performance problem, and how do you fix it?**
*Why they ask:* Tests depth - most candidates know EntityGraph
but miss the Pageable interaction.
*Strong answer includes:*
- HHH90003004: LEFT JOIN of collection multiplies rows;
  Hibernate can't apply SQL LIMIT/OFFSET when rows are multiplied
  (page 1 needs rows 1-20 of deduped entities, but SQL rows
  are many more due to JOIN)
- Hibernate workaround: fetch ALL rows, paginate in Java
  -> `fetchAll()` on every page request; O(N) for every page
- Fix: two-query pattern:
  1. `SELECT o.id FROM Order o ... LIMIT 20 OFFSET ?` (SQL LIMIT)
  2. `findAllByIdIn(ids)` with `@EntityGraph` (fetch 20 entities
     with associations; no pagination, no HHH90003004)