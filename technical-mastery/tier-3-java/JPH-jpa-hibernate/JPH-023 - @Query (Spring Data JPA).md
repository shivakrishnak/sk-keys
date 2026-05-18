---
id: JPH-023
title: "@Query (Spring Data JPA)"
category: JPA & Hibernate
tier: tier-3-java
folder: JPH-jpa-hibernate
difficulty: ★★☆
depends_on: JPH-014, JPH-016, JPH-021, JPH-022
used_by: JPH-024, JPH-025, JPH-027, JPH-030, JPH-037
related: JPH-029, JPH-036, JPH-043
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
nav_order: 23
permalink: /technical-mastery/jpa-hibernate/query-annotation/
---

⚡ **TL;DR** - `@Query` on a Spring Data repository method
lets you write a JPQL (or native SQL) string directly,
bypassing method-name derivation for queries too complex
for the naming convention. Always use named parameters
(`:name`). For UPDATE/DELETE, pair with `@Modifying` and
`@Transactional`.

| #023            | Category: JPA & Hibernate                                                             | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------------------------------------------ | :-------------- |
| **Depends on:** | JPQL, CrudRepository/JpaRepository, FetchType, CascadeType                            |                 |
| **Used by:**    | Derived Query Methods, Pagination/Sorting, N+1 Problem, DTO Projections, @EntityGraph |                 |
| **Related:**    | @NamedQuery/Native Queries, Criteria API, Spring Data Specifications                  |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Spring Data's method name derivation handles simple queries
(`findByNameAndStatus`), but complex queries with JOINs,
subqueries, aggregations, or specific WHERE conditions
cannot be expressed as method names without becoming
unreadable (e.g., `findByCategory_NameAndPriceBetweenAndStatusOrderByCreatedAtDesc`).

**THE BREAKING POINT:**
A repository with 20 complex queries expressed as method
names becomes a maintenance nightmare. The method names
are not documentation; they are code. A subquery, GROUP BY,
or HAVING clause is simply impossible via method name
derivation.

**THE INVENTION MOMENT:**
`@Query("SELECT p FROM Product p JOIN p.category c WHERE
c.name = :cat AND p.price > :min ORDER BY p.price")` on
a repository method provides the full expressiveness of
JPQL with Spring Data's proxy generation and parameter
binding - no need to inject `EntityManager` directly.

---

### 📘 Textbook Definition

**`@Query`** is a Spring Data annotation applied to a
repository interface method. It specifies a JPQL query
(or native SQL with `nativeQuery=true`) that Spring Data
executes for that method. Spring Data binds `@Param`
parameters to named query parameters, manages the
transaction (inheriting from `SimpleJpaRepository`'s
class-level `@Transactional(readOnly=true)`), and maps
results to the method's return type.

Key attributes:

- `value`: the JPQL or native SQL string
- `nativeQuery`: if `true`, the value is raw SQL (default: false)
- `countQuery`: custom count query for `Page<T>` return types
  (default: derived from main query)
- `countProjection`: field to use in the auto-derived count query

---

### ⏱️ Understand It in 30 Seconds

**One line:** `@Query` puts a JPQL (or SQL) string directly
on a repository method - full query control with Spring
Data's proxy convenience.

**One analogy:**

> Method name derivation is like ordering off a standard
> menu. `@Query` is like writing the full recipe yourself
> and handing it to the kitchen. Same service (Spring Data),
> but you control every ingredient.

**One insight:** `@Query` methods that modify data (UPDATE,
DELETE) require both `@Modifying` AND `@Transactional`.
`@Modifying` alone is not enough. Forgetting `@Transactional`
causes `TransactionRequiredException` at runtime.

---

### 🔩 First Principles Explanation

**HOW @Query IS PROCESSED:**

```
Repository interface parsed at startup:
    findActiveProductsByCategory(String cat)
    @Query("SELECT p FROM Product p WHERE ...")
    |
    v
[ Spring Data RepositoryFactory ]
    |  Detects @Query annotation
    |  Stores JPQL string with parameter names
    v
[ At call time: ]
    |  Spring Data proxy intercepts method call
    |  Creates: em.createQuery(jpql, Product.class)
    |  Binds: :cat = cat
    |  Executes, returns List<Product>
```

**PARAMETER BINDING RULES:**

```java
// Named parameter (preferred):
@Query("SELECT p FROM Product p WHERE p.name = :name")
Product findByName(@Param("name") String name);

// Positional parameter (avoid):
@Query("SELECT p FROM Product p WHERE p.name = ?1")
Product findByName(String name);
// Positional numbers must match argument position (1-based)

// SpEL entity placeholder (advanced):
@Query("SELECT p FROM #{#entityName} p WHERE p.id = :id")
Optional<T> findById(@Param("id") ID id);
// #{#entityName} resolves to the repository's entity class
```

**RETURN TYPE OPTIONS:**

```java
// Single entity:
Optional<Product> findBySlug(@Param("slug") String slug);

// Collection:
List<Product> findByCategoryName(
    @Param("cat") String cat);

// Paginated:
Page<Product> findByStatus(
    @Param("s") String s, Pageable pageable);

// DTO projection:
@Query("SELECT new ProductSummaryDto(p.id, p.name)" +
       " FROM Product p")
List<ProductSummaryDto> findAllSummaries();

// Interface projection:
List<ProductNameOnly> findAllBy();
// Interface: { String getName(); }
```

**CORE INVARIANTS:**

1. `@Query` JPQL is compiled and validated at startup if
   the method is called during context initialization;
   otherwise at first call time
2. `@Modifying` + `@Transactional` required for UPDATE/DELETE
3. Named parameters (`:name` with `@Param`) are preferred
   over positional parameters (`?1`)
4. `nativeQuery=true` bypasses entity validation - column
   names must match the database schema exactly
5. A `Page<T>` return type requires a count query; Spring
   Data auto-derives it but `countQuery` can override it

---

### 🧪 Thought Experiment

**SCENARIO: query too complex for method name derivation**

Required: "Find all orders that have at least one item
with price > X, placed by a customer in city Y, in the
last N days, sorted by total descending."

**Method name approach:**

```java
// Not possible - this would be absurd:
List<Order> findByItems_PriceGreaterThanAndCustomer_CityAndCreatedAtAfterOrderByTotalDesc(
    BigDecimal price, String city, LocalDateTime since);
// This works but is unreadable and does not express
// the "at least one item" semantics correctly
```

**@Query approach:**

```java
@Query("SELECT DISTINCT o FROM Order o " +
       "JOIN o.customer c " +
       "JOIN o.items i " +
       "WHERE i.price > :price " +
       "AND c.city = :city " +
       "AND o.createdAt > :since " +
       "ORDER BY o.total DESC")
List<Order> findComplexOrders(
    @Param("price") BigDecimal price,
    @Param("city") String city,
    @Param("since") LocalDateTime since);
```

**THE INSIGHT:** `@Query` is the escape hatch from method
name derivation. It is the right tool when the query has
JOINs, subqueries, aggregations, DISTINCT, or multiple
conditions that would produce unreadable method names.

---

### 🧠 Mental Model / Analogy

> `@Query` is a labeled pipe in a plumbing system. Method
> name derivation generates the pipe automatically from the
> method name (standard sizes, standard bends). `@Query`
> lets you hand-craft the pipe to exact specifications for
> non-standard flows. The plumbing infrastructure (Spring
> Data proxy, parameter binding, transaction management)
> is the same; only the pipe specification changes.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
`@Query` lets you write a custom query string for a Spring
Data repository method. Spring Data handles the wiring.

**Level 2 - How to use it (junior developer):**
Add `@Query("SELECT p FROM Product p WHERE p.name = :name")`
above the method. Add `@Param("name")` to the parameter.
For UPDATE/DELETE, add `@Modifying` and `@Transactional`.

**Level 3 - How it works (mid-level engineer):**
Spring Data detects `@Query` on a method and stores the
JPQL string. At method invocation time, the proxy creates
`em.createQuery(jpql, returnType)`, binds `@Param` values
to named parameters, executes the query, and maps results
to the return type using the JPA result mapping.

**Level 4 - Why it was designed this way (senior/staff):**
`@Query` keeps complex queries co-located with their
repository method declarations. The alternative (creating
a custom `EntityManager`-based repository fragment) is
necessary for dynamic queries but adds boilerplate. For
static, complex JPQL, `@Query` provides the expressiveness
of raw JPQL within the Spring Data abstraction - no need
to bypass the repository pattern.

**Level 5 - Mastery (distinguished engineer):**
`@Query` with `nativeQuery=true` bypasses Hibernate's
entity validation and query plan cache. Native SQL queries
are type-unsafe (no compile-time validation), database-specific,
and cannot use `@EntityGraph`. For complex reporting queries
that need database-specific features (window functions,
JSON path, full-text search), native `@Query` is appropriate.
For standard entity graph traversal, JPQL `@Query` is
preferred. The query plan cache applies to both native
and JPQL queries, but native queries are keyed by the
exact SQL string, not an AST - making parameter concatenation
even more dangerous for native queries (SQL injection risk
via `nativeQuery=true` if parameters are not bound properly).

---

### ⚙️ How It Works (Mechanism)

**@Query EXECUTION PIPELINE:**

```
At startup:
  RepositoryFactory finds: @Query("SELECT p FROM Product p
  WHERE p.category.name = :cat") on findByCategory()
  -> stores JPQL string in QueryMetadata map
  -> validates: if @NamedQuery validation mode enabled,
     parse at startup

At call time:
  repo.findByCategory("electronics")
    |
    v
  [ Spring Data proxy ]
    |  look up QueryMetadata for method
    v
  [ em.createQuery("SELECT p FROM Product p ...",
    Product.class) ]
    |  (hits query plan cache if JPQL)
    v
  [ bind @Param("cat") = "electronics" ]
    v
  [ em.createQuery.setParameter("cat", "electronics") ]
    v
  [ query.getResultList() ]
    v
  [ returns List<Product>, all MANAGED ]
```

**@Modifying EXECUTION:**

```
At call time for UPDATE/DELETE @Query:
  repo.updatePrice(42L, 29.99)
    |
    v
  [ Spring Data proxy - detects @Modifying ]
    |  uses executeUpdate() instead of getResultList()
    v
  [ em.createQuery("UPDATE Product ...") ]
    v
  [ query.setParameter("id", 42L).setParameter(...) ]
    v
  [ query.executeUpdate() ]
    |  returns int (rows affected)
    |  bypasses persistence context (entities may be stale)
    v
  [ if @Modifying(clearAutomatically=true): em.clear() ]
```

---

### 🔄 The Complete Picture - End-to-End Flow

**COMPLEX @Query WITH PAGINATION:**

```java
@Query(value =
    "SELECT p FROM Product p " +
    "JOIN p.category c " +
    "WHERE c.id = :catId " +
    "AND p.price BETWEEN :min AND :max",
  countQuery =
    "SELECT COUNT(p) FROM Product p " +
    "JOIN p.category c " +
    "WHERE c.id = :catId " +
    "AND p.price BETWEEN :min AND :max")
Page<Product> findByCategoryAndPriceRange(
    @Param("catId") Long catId,
    @Param("min") BigDecimal min,
    @Param("max") BigDecimal max,
    Pageable pageable);

// Call:
Page<Product> page = repo.findByCategoryAndPriceRange(
    1L, BigDecimal.ZERO,
    BigDecimal.valueOf(100),
    PageRequest.of(0, 20, Sort.by("price")));

// SQL generated:
// SELECT p.id, p.name, p.price, ...
// FROM products p JOIN categories c ON p.cat_id = c.id
// WHERE c.id = 1 AND p.price BETWEEN 0 AND 100
// ORDER BY p.price ASC
// LIMIT 20 OFFSET 0
//
// Count SQL:
// SELECT COUNT(p.id) FROM products p JOIN categories c
// ON p.cat_id = c.id WHERE c.id = 1 AND p.price ...
```

---

### 💻 Code Example

**Example 1 - Standard JPQL @Query:**

```java
@Repository
public interface ProductRepository
        extends JpaRepository<Product, Long> {

    @Query("SELECT p FROM Product p " +
           "JOIN FETCH p.category " +
           "WHERE p.status = :status " +
           "ORDER BY p.name")
    List<Product> findActiveWithCategory(
        @Param("status") String status);
}
```

**Example 2 - BAD: @Modifying without @Transactional:**

```java
// BAD: @Modifying alone is insufficient
@Modifying
@Query("UPDATE Product p SET p.price = :price " +
       "WHERE p.id = :id")
void updatePrice(@Param("id") Long id,
                 @Param("price") BigDecimal price);
// Throws: TransactionRequiredException at runtime

// GOOD: @Modifying + @Transactional
@Modifying
@Transactional
@Query("UPDATE Product p SET p.price = :price " +
       "WHERE p.id = :id")
int updatePrice(@Param("id") Long id,
                @Param("price") BigDecimal price);
// Returns number of rows updated
```

**Example 3 - Native SQL @Query:**

```java
@Query(value = "SELECT * FROM products p " +
               "WHERE MATCH(p.name, p.description) " +
               "AGAINST (:term IN BOOLEAN MODE) " +
               "ORDER BY p.price",
       nativeQuery = true)
List<Product> fullTextSearch(
    @Param("term") String searchTerm);
// MySQL full-text search - not possible in JPQL
// Returns Object[] or mapped via @SqlResultSetMapping
```

**Example 4 - DTO projection with @Query:**

```java
@Query("SELECT new " +
       "com.example.dto.ProductSummary(" +
       "  p.id, p.name, p.price, p.status) " +
       "FROM Product p " +
       "WHERE p.category.id = :catId")
List<ProductSummary> findSummariesByCategory(
    @Param("catId") Long catId);

// ProductSummary:
public class ProductSummary {
    private final Long id;
    private final String name;
    private final BigDecimal price;
    private final String status;
    // All-args constructor required for SELECT new
}
// Results NOT in persistence context - no dirty checking
```

**Example 5 - @Modifying with clearAutomatically:**

```java
@Modifying(clearAutomatically = true)
@Transactional
@Query("UPDATE Product p " +
       "SET p.price = p.price * :factor " +
       "WHERE p.category.id = :catId")
int applyPriceIncrease(
    @Param("catId") Long catId,
    @Param("factor") BigDecimal factor);
// clearAutomatically=true: calls em.clear() after update
// Ensures managed Product entities in session reflect
// new prices (not stale pre-update values)
```

---

### ⚖️ Comparison Table

| Approach                   | When to use                                        | Validation                       | Type safety              | Dynamic?           |
| -------------------------- | -------------------------------------------------- | -------------------------------- | ------------------------ | ------------------ |
| Method name derivation     | Simple conditions (1-3 fields, no JOINs)           | Compile-time (method name parse) | High                     | No                 |
| `@Query` (JPQL)            | Complex JPQL (JOINs, subqueries, aggregations)     | First call / startup             | Medium (no compile-time) | No (static string) |
| `@Query(nativeQuery=true)` | DB-specific features (window functions, full-text) | None (runtime only)              | None                     | No                 |
| Criteria API / Querydsl    | Dynamic queries (conditions built at runtime)      | Compile-time                     | High                     | Yes                |
| Spring Data Specifications | Complex dynamic queries in repository pattern      | Compile-time                     | High                     | Yes                |

---

### ⚠️ Common Misconceptions

| Misconception                                            | Reality                                                                                                                                                                                                                                                |
| -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| "`@Modifying` alone makes an UPDATE @Query work"         | `@Modifying` marks the query as an update operation (uses `executeUpdate()` instead of `getResultList()`). It does NOT provide a transaction. Without `@Transactional`, `TransactionRequiredException` is thrown. Both are required.                   |
| "`@Query` is validated at compile time"                  | `@Query` JPQL strings are not validated at compile time. Errors (unknown entity names, field names) surface at first execution. Use `@NamedQuery` on the entity class (validated at startup) for early validation.                                     |
| "nativeQuery=true @Query is immune to SQL injection"     | `nativeQuery=true` with BOUND parameters (`:name`) is safe. But if the query string is dynamically built with concatenated values, it is vulnerable to SQL injection since the string is sent as raw SQL to the database. Always use bound parameters. |
| "Spring Data auto-adds DISTINCT to fix @OneToMany JOINs" | Spring Data does NOT add `DISTINCT` automatically. If you `JOIN FETCH` a `@OneToMany` collection in a `@Query`, the result list has duplicate parent entities. Add `DISTINCT` to your JPQL: `SELECT DISTINCT o FROM Order o LEFT JOIN FETCH o.items`.  |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: TransactionRequiredException for @Modifying**

**Symptom:** `javax.persistence.TransactionRequiredException:
Executing an update/delete query` at runtime for a
`@Modifying @Query` method.

**Root Cause:** `@Modifying` without `@Transactional`. The
method does not have an active transaction (or the
`SimpleJpaRepository` class-level `readOnly=true` transaction
is insufficient for write operations).

**Diagnostic:** Check if `@Transactional` is missing or if
the method has a wrong propagation.

**Fix:** Add `@Transactional` to the method (or to the
service calling it - but for a `@Modifying` repository
method, `@Transactional` on the method itself is explicit
and recommended).

---

**Failure Mode 2: Stale Entities After @Modifying UPDATE**

**Symptom:** After a successful `@Modifying @Query` UPDATE,
a subsequent `findById()` returns the OLD value for the
updated field.

**Root Cause:** The JPQL bulk UPDATE bypasses the persistence
context. Managed entities in the session still have their
pre-update field values.

**Fix:** Use `@Modifying(clearAutomatically = true)` to
automatically call `em.clear()` after the update.

```java
@Modifying(clearAutomatically = true)
@Transactional
@Query("UPDATE Product p SET p.status = :s " +
       "WHERE p.id = :id")
void updateStatus(@Param("id") Long id,
                  @Param("s") String s);
```

---

**Failure Mode 3: Duplicate Results From JOIN FETCH Without DISTINCT**

**Symptom:** `@Query` returns 15 `Order` entities for a
query expecting 5 orders (each with 3 items).

**Root Cause:** `JOIN FETCH o.items` produces SQL Cartesian
product. Without `DISTINCT` in JPQL, each parent appears
once per child row.

**Fix:**

```java
@Query("SELECT DISTINCT o FROM Order o " +
       "LEFT JOIN FETCH o.items " +
       "WHERE o.customerId = :cid")
List<Order> findWithItems(@Param("cid") Long cid);
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[JPH-014 - JPQL (Java Persistence Query Language)]] -
  `@Query` value is JPQL; all JPQL rules apply
- [[JPH-016 - CrudRepository and JpaRepository]] -
  `@Query` is applied on Spring Data repository methods

**Builds On This (learn these next):**

- [[JPH-024 - Derived Query Methods]] - simpler alternative
  for basic queries
- [[JPH-025 - Pagination and Sorting (Pageable, Sort)]] -
  `@Query` methods can take `Pageable` parameter
- [[JPH-027 - N+1 Problem (ORM Context)]] - JOIN FETCH
  in `@Query` solves N+1
- [[JPH-030 - DTO Projections in Spring Data JPA]] -
  `SELECT new Dto(...)` projection in `@Query`
- [[JPH-037 - EntityGraph]] - alternative to JOIN FETCH
  in `@Query` for fetch control

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ BASIC        │ @Query("SELECT p FROM Product p WHERE ...│
│              │ Use @Param("name") for named parameters  │
├──────────────┼──────────────────────────────────────────┤
│ UPDATE/DELETE│ MUST pair: @Modifying + @Transactional   │
│              │ @Modifying(clearAutomatically=true)      │
│              │ to avoid stale entity state              │
├──────────────┼──────────────────────────────────────────┤
│ NATIVE SQL   │ @Query(value="...", nativeQuery=true)    │
│              │ For DB-specific features only            │
├──────────────┼──────────────────────────────────────────┤
│ PAGINATION   │ Add Pageable parameter + countQuery attr │
├──────────────┼──────────────────────────────────────────┤
│ JOIN FETCH   │ Add DISTINCT to avoid duplicate parents  │
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "@Query = custom JPQL on Spring Data repo│
│              │ method. @Modifying + @Transactional for  │
│              │ UPDATE/DELETE. Always use :named params."│
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. `@Query` value is JPQL by default; use `nativeQuery=true`
   only for database-specific SQL features
2. UPDATE/DELETE `@Query` requires BOTH `@Modifying` AND
   `@Transactional` - neither alone is sufficient
3. `JOIN FETCH` in `@Query` with `@OneToMany` needs
   `DISTINCT` in JPQL to prevent duplicate parent entities

**Interview one-liner:** `@Query` puts a custom JPQL (or
native SQL) string directly on a Spring Data repository
method for queries too complex for method name derivation.
Use named parameters (`:name` + `@Param`). For UPDATE/DELETE,
add `@Modifying` + `@Transactional`. Add `@Modifying(clearAutomatically=true)`
to prevent stale entities after bulk updates. JOIN FETCH
in `@Query` needs DISTINCT to avoid Cartesian product
duplicates.

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Static query definition
at the use site (co-located with the interface method)
is better than scattered query definitions (named queries
in XML or on entities). `@Query` embodies the principle
of proximity: the query is defined where it is used,
making the code self-documenting and eliminating the
need to search for the query definition across multiple
files. This principle applies to GraphQL resolvers (query
defined with the resolver), REST controllers (endpoint
defined with the handler), and stream processing pipelines
(filter/map defined with the processor).

---

### 💡 The Surprising Truth

Spring Data auto-derives a count query for `Page<T>` return
types by replacing `SELECT e` with `SELECT COUNT(e)` in
your `@Query` JPQL. This works for simple queries but
fails for queries with `JOIN FETCH` (because count queries
cannot use `JOIN FETCH` - it would multiply count rows).
Hibernate throws an exception: `org.hibernate.query.SemanticException:
COUNT queries cannot use collection-valued path expressions`.
The fix: provide an explicit `countQuery` attribute in
`@Query` without the JOIN FETCH:

```java
@Query(value = "SELECT DISTINCT o FROM Order o " +
               "LEFT JOIN FETCH o.items",
       countQuery = "SELECT COUNT(DISTINCT o) FROM Order o")
Page<Order> findAllWithItems(Pageable pageable);
```

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **WRITE** a `@Query` method with named parameters, JOIN
   FETCH, DISTINCT, and a `Pageable` parameter including
   a custom `countQuery`
2. **FIX** a `TransactionRequiredException` by adding both
   `@Modifying` and `@Transactional` to an UPDATE method
3. **EXPLAIN** why JOIN FETCH in a `@Query` with `@OneToMany`
   requires DISTINCT and demonstrate the duplicate behavior
4. **CHOOSE** between `@Query(nativeQuery=true)` and JPQL
   `@Query` for three different scenarios with justification
5. **DEBUG** stale entity state after a `@Modifying @Query`
   update and fix it with `clearAutomatically=true`

---

### 🎯 Interview Deep-Dive

**Q1: What annotations are required for a @Query that
executes an UPDATE or DELETE statement, and why?**
_Why they ask:_ Very common practical question; tests
understanding of transaction + @Modifying interaction.
_Strong answer includes:_

- `@Modifying`: tells Spring Data to use `executeUpdate()`
  instead of `getResultList()` for the query
- `@Transactional`: provides the transaction context
  required for write operations (SimpleJpaRepository runs
  in readOnly=true by default; UPDATE requires readOnly=false)
- Both are required; `@Modifying` alone causes
  `TransactionRequiredException`
- `clearAutomatically=true` on `@Modifying` is recommended
  to avoid stale entities after bulk updates

**Q2: Why do you need DISTINCT in a @Query with JOIN FETCH
on a @OneToMany collection?**
_Why they ask:_ Tests understanding of SQL Cartesian product
and JPQL DISTINCT semantics.
_Strong answer includes:_

- JOIN FETCH with `@OneToMany` produces SQL Cartesian product:
  parent rows multiplied by child rows
- Without DISTINCT: result list contains one `Order` object
  per join result row (order appears 3 times for 3 items)
- DISTINCT in JPQL: Hibernate deduplicates at the object
  identity level (not SQL DISTINCT), returning unique parent
  entities while still loading all children
- Alternative: use `Set<OrderItem>` for the collection
  (Set identity deduplicates) or use `@BatchSize` instead
  of JOIN FETCH to avoid the Cartesian product entirely

**Q3: When would you use nativeQuery=true in @Query vs
standard JPQL?**
_Why they ask:_ Tests awareness of when JPA abstractions
are insufficient and native SQL is needed.
_Strong answer includes:_

- Use native SQL for database-specific features: window
  functions (`ROW_NUMBER() OVER(...)`), JSON path
  expressions, full-text search (`MATCH AGAINST`), stored
  procedure calls, complex CTEs (`WITH` clauses)
- JPQL cannot express these because they are not portable
  across databases
- Trade-offs: native SQL is not validated by JPA at startup,
  is database-specific, and cannot use `@EntityGraph`
- Security note: native `@Query` with bound parameters
  (`:name`) is safe; concatenating user input into a
  `nativeQuery=true` query string is SQL injection
