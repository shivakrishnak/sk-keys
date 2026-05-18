---
id: JPH-021
title: "FetchType (LAZY vs EAGER)"
category: JPA & Hibernate
tier: tier-3-java
folder: JPH-jpa-hibernate
difficulty: ★★☆
depends_on: JPH-012, JPH-013, JPH-017, JPH-018, JPH-019, JPH-020
used_by: JPH-027, JPH-037, JPH-052
related: JPH-033, JPH-034
tags:
  - java
  - jpa
  - database
  - intermediate
status: complete
version: 4
layout: default
parent: "JPA & Hibernate"
grand_parent: "Technical Mastery"
nav_order: 21
permalink: /technical-mastery/jpa-hibernate/fetchtype-lazy-eager/
---

⚡ **TL;DR** - `LAZY` loads related data only on first
access; `EAGER` loads it immediately via JOIN or extra
SELECT. Default: `@ManyToOne` = EAGER (dangerous),
`@OneToMany`/`@ManyToMany` = LAZY (safe). Always override
`@ManyToOne` to LAZY. EAGER is almost never the right
choice in production code.

| #021            | Category: JPA & Hibernate                                                                                    | Difficulty: ★★☆ |
| :-------------- | :----------------------------------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Persistence Context, Entity Lifecycle, @OneToOne, @OneToMany/@ManyToOne, @ManyToMany, @JoinColumn/@JoinTable |                 |
| **Used by:**    | N+1 Problem, @EntityGraph, Dirty Checking and Flush Mode                                                     |                 |
| **Related:**    | First Level Cache, Second Level Cache                                                                        |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Without a fetch strategy, every entity load would join
all related tables eagerly. Loading an `Order` would
immediately JOIN to `Customer`, `OrderItem[]`,
`Product[]`, `Category[]`, `Supplier[]` - potentially
dozens of JOINs. For a list of 100 orders, a single query
would return a massive Cartesian product, load gigabytes
of data into memory, and waste cycles mapping thousands
of objects that the caller never uses.

**THE BREAKING POINT:**
A REST API endpoint returning "list of order summaries"
(id, status, total) still loads every customer object,
every item, every product - because all associations are
eagerly loaded. The response time is 10 seconds instead
of 50ms. The query returns 50,000 rows for 100 orders
due to the Cartesian product.

**THE INVENTION MOMENT:**
`FetchType.LAZY` defers loading related entities until
they are actually accessed. Loading an `Order` only
executes `SELECT * FROM orders WHERE id=?`. When
`order.getItems()` is called (and only then), the items
are fetched. Endpoints that never access items pay zero
cost for the association.

---

### 📘 Textbook Definition

**`FetchType`** is a JPA enum with two values:

- `LAZY`: related entities or collections are NOT loaded
  immediately. A proxy object is returned. The actual
  data is fetched from the database on first access to
  a field on the proxy.
- `EAGER`: related entities or collections ARE loaded
  immediately, either via a SQL JOIN in the same query
  or via a separate SELECT executed immediately after
  the owning entity is loaded.

**JPA Specification Defaults:**

- `@ManyToOne`: EAGER (default - should almost always override to LAZY)
- `@OneToOne`: EAGER (default - should almost always override to LAZY)
- `@OneToMany`: LAZY (safe default - leave as is)
- `@ManyToMany`: LAZY (safe default - leave as is)

LAZY is a hint: the JPA provider MAY load lazily but is
not required to. EAGER is a requirement: the provider
MUST load eagerly.

---

### ⏱️ Understand It in 30 Seconds

**One line:** LAZY = load on demand; EAGER = load now.
Always LAZY for all associations; load what you need
via JOIN FETCH or `@EntityGraph`.

**One analogy:**

> EAGER is like a waiter who brings the entire menu, full
> appetizers, main course, and dessert when you sit down
> "just in case". LAZY is like a waiter who takes your
> order and brings exactly what you ask for. EAGER is
> comfortable for testing; LAZY is correct for production.

**One insight:** EAGER does not eliminate N+1 - it can
CAUSE it. When loading a list of entities, EAGER on a
`@OneToMany` collection triggers N separate collection
SELECT statements (one per parent), not a JOIN. Hibernate
uses JOIN for EAGER on `@ManyToOne` (single entity)
but falls back to separate SELECT for EAGER on collections
to avoid Cartesian products.

---

### 🔩 First Principles Explanation

**HOW LAZY LOADING WORKS:**

```
em.find(Order.class, 1L)
    |
    v
[ SELECT * FROM orders WHERE id=1 ]
    |  Returns: Order proxy with id, status, total
    |  order.items = LazyList (proxy, no SQL)
    v
[ order.getItems() called ]
    |  Hibernate intercepts proxy getter
    |  session is open? YES -> proceed
    v
[ SELECT * FROM order_items WHERE order_id=1 ]
    |  Returns: List<OrderItem> loaded
    v
[ order.items replaced with loaded list ]
```

**HOW EAGER LOADING WORKS (for @ManyToOne):**

```
em.find(Order.class, 1L)
    |
    v
[ SELECT o.*, c.* FROM orders o
  LEFT JOIN customers c ON o.customer_id=c.id
  WHERE o.id=1 ]
    |  Single query loads order AND customer
    v
[ Both Order and Customer entities in persistence context ]
```

**HOW EAGER LOADING WORKS (for @OneToMany - BAD):**

```
em.find(Order.class, 1L)
    |
    v
[ SELECT * FROM orders WHERE id=1 ]
    |  Then immediately:
    v
[ SELECT * FROM order_items WHERE order_id=1 ]
    |  Second query fires immediately after first
    |  NOT a JOIN for collections (Cartesian product risk)
```

**CORE INVARIANTS:**

1. LAZY on a closed session (no persistence context) ->
   `LazyInitializationException` on first field access
2. EAGER on `@ManyToOne` -> JOIN in the owning entity's
   SELECT query (one query, more columns)
3. EAGER on `@OneToMany`/`@ManyToMany` -> separate SELECT
   per entity in a list query -> N+1
4. LAZY is a HINT; EAGER is a REQUIREMENT
5. Overriding LAZY to EAGER in a query (via JOIN FETCH
   or `@EntityGraph`) overrides the field-level setting
   for that specific query

---

### 🧪 Thought Experiment

**SETUP:**
`Order` has `@OneToMany(fetch=EAGER)` on `items`.
You run: `orderRepo.findAll()` to get 100 orders.

**WHAT HAPPENS:**

```
1. SELECT * FROM orders             (1 query)
2. SELECT * FROM order_items        (1 query per order)
   WHERE order_id = 1
   WHERE order_id = 2
   ...
   WHERE order_id = 100
Total: 1 + 100 = 101 queries
```

**CONTRADICTION:** You set EAGER thinking "fewer queries,
better performance". You got MORE queries than LAZY would
produce for a list endpoint that does not access items.

**WITH LAZY (list endpoint, items not accessed):**

```
1. SELECT * FROM orders             (1 query)
   getItems() never called
Total: 1 query
```

**THE INSIGHT:** EAGER does not prevent N+1 for
`@OneToMany`. It makes N+1 happen automatically for
every query. Use LAZY with explicit JOIN FETCH when
you need the collection.

---

### 🧠 Mental Model / Analogy

> LAZY fetch is like a smart assistant who only looks up
> information when you explicitly ask: "What are the items
> on Order #1?" EAGER is an over-eager assistant who looks
> up every related piece of information the moment a record
> is mentioned - even for information you will never use
> in this conversation.
>
> The EAGER assistant is helpful in a one-on-one conversation
> (single entity load, testing). In a busy office handling
> 100 requests simultaneously, the EAGER assistant is
> making 100x as many database calls as needed.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
LAZY = JPA waits until you access the related data before
loading it. EAGER = JPA loads related data immediately
whenever the owning entity is loaded.

**Level 2 - How to use it (junior developer):**
Always add `fetch=FetchType.LAZY` to all `@ManyToOne` and
`@OneToOne` annotations. Leave `@OneToMany` and
`@ManyToMany` at their LAZY defaults. When you need
the related data in a specific query, use JOIN FETCH
or `@EntityGraph`.

**Level 3 - How it works (mid-level engineer):**
LAZY uses proxy objects (Hibernate generates a subclass
of the entity at startup). When the proxy's getter is
called, the proxy intercepts and issues a SELECT if a
session is available. EAGER adds a JOIN to the entity's
SELECT, or fires a second SELECT immediately after the
entity is loaded (for collections).

**Level 4 - Why it was designed this way (senior/staff):**
EAGER was the JPA 1.0 default for `@ManyToOne` because
early JPA usage assumed single-entity lookups (find an
order, show its customer). The EAGER default made this
convenient. JPA 2.0 added LAZY for collections because
EAGER on collections was obviously problematic. The
`@ManyToOne` EAGER default survived as a historical
artifact. Modern JPA practice universally treats `@ManyToOne`
EAGER as a bug to be fixed.

**Level 5 - Mastery (distinguished engineer):**
`FetchType` is a per-field static setting. Runtime fetch
control (load lazily in most cases, eagerly in specific
queries) is the production pattern. `@EntityGraph` and
JOIN FETCH override the field-level setting per query.
This two-layer design (field-level default + query-level
override) gives maximum flexibility: globally lazy (safe
default), explicitly eager per query (precise loading).
The `@NamedEntityGraph` pattern allows common fetch plans
to be declared on entities and referenced by name in
repository methods - a cleaner alternative to JOIN FETCH
in JPQL strings.

**Expert Thinking Cues:**

- Ask: "What is the fetch type on this `@ManyToOne`?" -
  if not explicitly LAZY, it is EAGER (the dangerous default)
- Watch: `open-in-view=true` (Spring Boot default) hides
  `LazyInitializationException` by keeping the session
  open through the view layer - masking LAZY loading in
  production code that will break when OEIV is disabled
- Know: bytecode enhancement enables true LAZY loading
  for `@OneToOne` inverse side and basic field loading
  (`@Basic(fetch=LAZY)`) - an advanced optimization rarely
  needed but critical for LOB fields (large strings, blobs)

---

### ⚙️ How It Works (Mechanism)

**PROXY GENERATION (LAZY):**

```
Startup:
  Hibernate generates: OrderProxy extends Order {
      @Override
      public List<OrderItem> getItems() {
          if (items == UNINITIALIZED) {
              Session session = SessionUtil.current();
              if (session == null) throw LIE();
              items = session.load("Order.items", id);
          }
          return items;
      }
  }

Runtime:
  em.find(Order.class, 1L)
  -> returns OrderProxy with id=1, items=UNINITIALIZED

  order.getItems()  <- proxy intercepts
  -> issues SELECT WHERE order_id=1
  -> loads and caches in items field
```

**EAGER JOIN (for @ManyToOne):**

```sql
-- EAGER @ManyToOne Customer on Order
SELECT o.id, o.status, o.total,
       c.id, c.name, c.email
FROM orders o
LEFT JOIN customers c ON o.customer_id = c.id
WHERE o.id = ?
-- Single query, both entities loaded
```

**N+1 FROM EAGER @OneToMany:**

```sql
-- EAGER @OneToMany List<OrderItem> items
SELECT * FROM orders WHERE id = ?
-- Then immediately:
SELECT * FROM order_items WHERE order_id = ?
-- One extra query per order loaded
```

---

### 🔄 The Complete Picture - End-to-End Flow

**PRODUCTION PATTERN: LAZY default + explicit load:**

```java
// Entity: everything LAZY
@ManyToOne(fetch = FetchType.LAZY)
private Customer customer;

@OneToMany(mappedBy = "order", fetch = FetchType.LAZY)
private List<OrderItem> items;

// Repository: specific queries load what's needed
@Query("SELECT o FROM Order o " +
       "LEFT JOIN FETCH o.items i " +
       "LEFT JOIN FETCH i.product p " +
       "WHERE o.id = :id")
Optional<Order> findByIdWithItems(@Param("id") Long id);

// Summary endpoint: no items needed
@Query("SELECT new OrderSummary(o.id, o.status, o.total)" +
       " FROM Order o WHERE o.customerId = :cid")
List<OrderSummary> findSummariesByCustomer(
    @Param("cid") Long cid);
// No items, no customer join - minimal query
```

---

### 💻 Code Example

**Example 1 - Fix the EAGER @ManyToOne default:**

```java
// BAD: default EAGER @ManyToOne
@ManyToOne
@JoinColumn(name = "category_id")
private Category category;
// Every ProductRepository.findAll() JOINs category table
// 100 products -> 100 JOINs to category in one big query
// (or worse: N+1 if collection)

// GOOD: explicit LAZY
@ManyToOne(fetch = FetchType.LAZY)
@JoinColumn(name = "category_id")
private Category category;
// category loaded only when product.getCategory() called
```

**Example 2 - LAZY collection with JOIN FETCH override:**

```java
// Entity: LAZY collection (default)
@OneToMany(mappedBy = "order",
           fetch = FetchType.LAZY)
private List<OrderItem> items;

// Standard find: no items loaded
Order order = orderRepo.findById(1L).get();
// order.items = UNINITIALIZED proxy

// Specific query: JOIN FETCH loads items
@Query("SELECT DISTINCT o FROM Order o " +
       "LEFT JOIN FETCH o.items " +
       "WHERE o.id = :id")
Optional<Order> findWithItems(@Param("id") Long id);
// Overrides LAZY with EAGER for this query only
```

**Example 3 - Detect and fix EAGER @ManyToOne on entity:**

```java
// Audit all @ManyToOne and @OneToOne for fetch type:
// grep -r "@ManyToOne" --include="*.java" | grep -v "LAZY"
// -> any result is a potential EAGER association to fix

// Systematic fix:
@Entity
public class OrderItem {
    // BAD: EAGER default
    @ManyToOne
    private Order order;

    // GOOD: explicit LAZY
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "order_id")
    private Order order;

    // BAD: EAGER default
    @ManyToOne
    private Product product;

    // GOOD: explicit LAZY
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "product_id")
    private Product product;
}
```

**Example 4 - @Basic(fetch=LAZY) for LOB fields:**

```java
@Entity
public class Document {
    @Id @GeneratedValue
    private Long id;
    private String title;

    // Load large content only when explicitly accessed
    @Lob
    @Basic(fetch = FetchType.LAZY)
    @Column(name = "content", columnDefinition = "LONGTEXT")
    private String content;

    // Listing documents: only title loaded
    // document.getContent() triggers: SELECT content FROM documents
}
// Note: @Basic(fetch=LAZY) requires bytecode enhancement
// to actually work in Hibernate
```

---

### ⚖️ Comparison Table

|                        | LAZY                       | EAGER                                    |
| ---------------------- | -------------------------- | ---------------------------------------- |
| When loaded            | First field access         | Immediately on entity load               |
| SQL impact             | Extra SELECT when accessed | JOIN or extra SELECT on load             |
| N+1 risk               | Only if accessed in a loop | Automatic for every query                |
| LazyInitException risk | After session closes       | None (already loaded)                    |
| Memory                 | Loads only needed data     | Loads all related data                   |
| Testing                | May hide missing joins     | "Convenient" but masks real load         |
| Production             | Correct for most use cases | Correct only for always-needed relations |

---

### ⚠️ Common Misconceptions

| Misconception                                                  | Reality                                                                                                                                                                                                                                                                                                            |
| -------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| "EAGER prevents N+1 by loading everything in one query"        | EAGER for `@OneToMany` causes N separate SELECT statements - one per parent entity. It does NOT produce a single JOIN. EAGER causes N+1, it does not prevent it.                                                                                                                                                   |
| "`fetch=LAZY` on @OneToOne (inverse side) makes it truly lazy" | On the inverse side of `@OneToOne` (mappedBy side), Hibernate still issues a SELECT to check null vs. proxy even with `fetch=LAZY`. True lazy on inverse `@OneToOne` requires `@MapsId` or bytecode enhancement.                                                                                                   |
| "EAGER is safer because you always have the data available"    | EAGER loads data even when never used. In production, most requests access only a subset of an entity's relationships. EAGER wastes database I/O, memory, and network for data that goes unused.                                                                                                                   |
| "`open-in-view=true` fixes LazyInitializationException"        | OEIV keeps the session open through the view (HTTP response serialization) layer, hiding LIE in development. It delays session close until after the view is rendered, creating a transaction per HTTP request. This hides lazy loading issues that only appear under load when session timeout becomes a problem. |
| "LAZY loading always issues a separate SELECT"                 | Hibernate can batch lazy loads with `@BatchSize` (loads N collections in one IN query) or with second-level cache (returns cached data without a SELECT). LAZY does not always mean one extra SELECT.                                                                                                              |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: LazyInitializationException in Production**

**Symptom:** `org.hibernate.LazyInitializationException:
failed to lazily initialize a collection of role:
Order.items - could not initialize proxy - no Session`
appearing in production logs (but not in development with
OEIV enabled).

**Root Cause:** `order.getItems()` is called after the
transaction and persistence context have closed. In
development, OEIV keeps the session open; in production
without OEIV, the session is closed.

**Diagnostic:**

```
spring.jpa.open-in-view=false  # surface the bug
# Stacktrace will show where the lazy access occurs
# -> fix by loading within transaction (JOIN FETCH)
```

**Fix:** Load the collection within the service
transaction using JOIN FETCH or `@EntityGraph`. Convert
entities to DTOs within the service before the session
closes.

**Prevention:** Always disable OEIV in development
(`spring.jpa.open-in-view=false`) to surface lazy loading
bugs immediately.

---

**Failure Mode 2: EAGER @ManyToOne Creating Multi-JOIN Queries**

**Symptom:** A simple `findAll()` query generates SQL
with 5 JOINs; response time is high; explain plan shows
large join overhead.

**Root Cause:** Entity has multiple `@ManyToOne` fields
with EAGER (default) fetch. `findAll()` generates:
`SELECT ... FROM orders o
LEFT JOIN customers c ON o.customer_id=c.id
LEFT JOIN products p ON o.product_id=p.id
...` for every order.

**Diagnostic:**

```bash
spring.jpa.show-sql=true
# Count JOINs in the findAll() SQL output
# Each EAGER @ManyToOne adds one LEFT JOIN
```

**Fix:** Change all `@ManyToOne` to `fetch=LAZY`.
Use `@EntityGraph` or JOIN FETCH only in the specific
queries that need the related entities.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[JPH-012 - Persistence Context]] - LAZY requires an
  open persistence context when the proxy is accessed
- [[JPH-018 - @OneToMany and @ManyToOne]] - fetch defaults
  differ: `@ManyToOne` EAGER, `@OneToMany` LAZY

**Builds On This (learn these next):**

- [[JPH-027 - N+1 Problem (ORM Context)]] - EAGER on
  collections causes N+1; LAZY without JOIN FETCH also
  causes N+1; both are fetch strategy failures
- [[JPH-037 - EntityGraph (Solving N+1)]] - the primary
  tool for controlling fetch per query at the Spring Data
  level
- [[JPH-052 - Dirty Checking and Flush Mode]] - related to
  persistence context lifespan (which affects LAZY safety)

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ DEFAULTS     │ @ManyToOne = EAGER (BAD - always override│
│              │ @OneToOne  = EAGER (BAD - always override│
│              │ @OneToMany = LAZY  (good - keep)         │
│              │ @ManyToMany= LAZY  (good - keep)         │
├──────────────┼──────────────────────────────────────────┤
│ RULE         │ All associations: fetch=LAZY             │
│              │ Load what you need: JOIN FETCH / @EntityG│
├──────────────┼──────────────────────────────────────────┤
│ EAGER TRAPS  │ @OneToMany EAGER -> N SELECT (not JOIN)  │
│              │ EAGER doesn't prevent N+1, it causes it  │
├──────────────┼──────────────────────────────────────────┤
│ LAZY TRAPS   │ LazyInitException outside session        │
│              │ @OneToOne inverse: LAZY doesn't work     │
│              │ OEIV hides lazy bugs (disable in dev)    │
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "Always LAZY; load explicitly with JOIN  │
│              │ FETCH or @EntityGraph when needed.       │
│              │ EAGER causes N+1, not prevents it."      │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. `@ManyToOne` and `@OneToOne` default to EAGER - always
   add `fetch=LAZY`; EAGER causes N+1 on list queries
2. `LazyInitializationException` = accessing LAZY data
   after the session closed; fix by loading within
   the transaction (JOIN FETCH or `@EntityGraph`)
3. EAGER on `@OneToMany` does NOT produce a JOIN - it issues
   N separate SELECT statements (one per parent entity)

**Interview one-liner:** `FetchType.LAZY` defers loading
until first access; `EAGER` loads immediately (JOIN for
`@ManyToOne`, separate SELECT for `@OneToMany`). JPA defaults:
`@ManyToOne`/`@OneToOne` = EAGER (dangerous), `@OneToMany`/`@ManyToMany`
= LAZY. Production rule: all associations LAZY; load
what you need per query with JOIN FETCH or `@EntityGraph`.
EAGER on collections causes automatic N+1.

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Default-to-lazy with
explicit-eager-per-operation is the correct pattern for
any data loading system. Load the minimum required data
by default; load additional data only when a specific
operation needs it. This principle appears in:

- **Microservice API design**: sparse field sets by default
  (only id, name, status); include related entities via
  query parameter (`?include=items,customer`)
- **GraphQL**: fetch only the fields the client requests;
  related types loaded only when included in the query
- **React data fetching**: initial render loads minimal
  data; detail views fetch additional data on demand
  (all are LAZY by default with explicit EAGER on demand)

---

### 💡 The Surprising Truth

EAGER is a REQUIREMENT in the JPA spec, but LAZY is only
a HINT. A JPA provider is allowed to load LAZY associations
eagerly if it determines that is more efficient. Conversely,
no provider is allowed to violate EAGER - it must always
be loaded. This asymmetry means: code that depends on
LAZY not being loaded (e.g., "if this field is null,
it was not loaded") is not portable. The only portable
way to control fetch behavior per query is JOIN FETCH
or `@EntityGraph` - both override the field-level hint
with a requirement.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **AUDIT** an entity class and identify all EAGER
   associations (both explicit and default) and explain
   the SQL impact of each
2. **FIX** a `LazyInitializationException` by identifying
   where the lazy access occurs and adding JOIN FETCH or
   `@EntityGraph` to the query in the service layer
3. **DEMONSTRATE** that EAGER on `@OneToMany` causes N+1
   by reading SQL logs for a `findAll()` call on a
   collection with 100 parents
4. **APPLY** the "always LAZY + explicit JOIN FETCH" pattern
   to a new entity with 3 associations
5. **EXPLAIN** why disabling OEIV (`open-in-view=false`)
   is the recommended development practice and what it
   surfaces

---

### 🎯 Interview Deep-Dive

**Q1: What are the default fetch types for @ManyToOne and
@OneToMany, and why are they problematic?**
_Why they ask:_ Tests daily-use JPA knowledge; the EAGER
default on `@ManyToOne` is a common production performance
issue.
_Strong answer includes:_

- `@ManyToOne` default: EAGER - dangerous
  (`findAll()` JOINs all EAGER associations)
- `@OneToMany` default: LAZY - safe
- EAGER on `@ManyToOne`: adds JOINs to every query
  loading the owning entity; multiple EAGER `@ManyToOne`
  fields multiply the JOINs
- Fix: always explicitly add `fetch=FetchType.LAZY` to all
  `@ManyToOne` and `@OneToOne` annotations

**Q2: Why does EAGER fetch on @OneToMany NOT prevent N+1?**
_Why they ask:_ Tests understanding of how JPA implements
EAGER for collections (SELECT, not JOIN).
_Strong answer includes:_

- EAGER `@OneToMany` does not generate a JOIN
- Hibernate avoids JOINs for collections to prevent
  Cartesian product rows in the result
- Instead: Hibernate issues N separate SELECT statements
  (one per parent entity) immediately after loading parents
- Loading 100 orders with EAGER items = 1 + 100 = 101
  queries, same as N+1
- The difference: with LAZY N+1, you can fix it with
  JOIN FETCH; with EAGER N+1, it fires automatically
  for every query

**Q3: What is the risk of Spring Boot's `open-in-view=true`
default and what should you do about it?**
_Why they ask:_ Tests production readiness knowledge and
awareness of the OEIV anti-pattern.
_Strong answer includes:_

- OEIV keeps the JPA session open for the entire HTTP
  request lifecycle (including view rendering/serialization)
- During development: hides `LazyInitializationException`
  because lazy data can be loaded in the view layer
- In production: creates long-held database connections,
  hides missing JOIN FETCH, and can cause issues under load
  when connection pool exhaustion occurs due to long sessions
- Fix: set `spring.jpa.open-in-view=false` in all
  environments; fix `LazyInitializationException` by
  loading data within the service transaction
