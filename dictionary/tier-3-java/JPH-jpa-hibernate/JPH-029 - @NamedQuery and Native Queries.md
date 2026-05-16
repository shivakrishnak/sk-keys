---
id: JPH-029
title: "@NamedQuery and Native Queries"
category: JPA & Hibernate
tier: tier-3-java
folder: JPH-jpa-hibernate
difficulty: ★★☆
depends_on: JPH-006, JPH-011, JPH-014, JPH-023, JPH-028
used_by: JPH-030, JPH-031, JPH-058
related: JPH-036, JPH-048
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
nav_order: 29
permalink: /jpa-hibernate/named-native-queries/
---

# JPH-029 - @NamedQuery and Native Queries

⚡ **TL;DR** - `@NamedQuery` pre-defines and validates
JPQL/HQL at application startup (not at runtime). Native
queries use raw SQL strings mapped back to entities or
DTOs via `@SqlResultSetMapping`. Use `@NamedQuery` when
you want startup-time validation of frequently reused
queries. Use native queries for DB-specific features,
complex analytics, or stored procedure calls that JPQL
cannot express.

| #029            | Category: JPA & Hibernate                                                | Difficulty: ★★☆ |
| :-------------- | :----------------------------------------------------------------------- | :-------------- |
| **Depends on:** | @Entity, EntityManager, JPQL, @Query, HQL                                |                 |
| **Used by:**    | DTO Projections, Hibernate Session vs EntityManager, Hibernate Internals |                 |
| **Related:**    | Criteria API, Multi-Tenancy                                              |                 |

---

### 🔥 The Problem This Solves

**@NamedQuery - THE PROBLEM:**
In large applications, the same JPQL queries are repeated
in multiple service methods. A typo in a field name
(`o.statuss` instead of `o.status`) compiles fine but
throws `QuerySyntaxException` at runtime - only when
that code path is executed in production. Without named
queries, there is no mechanism to validate JPQL strings
at application startup.

**NATIVE QUERIES - THE PROBLEM:**
JPQL cannot express certain SQL constructs: window
functions (`RANK() OVER PARTITION BY`), CTEs (`WITH`
clauses), `UPSERT`/`ON CONFLICT`, database-specific
JSON operators (PostgreSQL's `->>`), full-text search
predicates, and stored procedure calls. For complex
analytics or DB-specific optimizations, raw SQL is the
only option.

**THE SOLUTION:**

- `@NamedQuery`: defines JPQL at the entity class level;
  validated (parsed + checked) during `EntityManagerFactory`
  initialization at startup. Errors surface immediately,
  not in production.
- `createNativeQuery()`: executes raw SQL and maps results
  to entities or value types via `@SqlResultSetMapping`
  or interface projections.

---

### 📘 Textbook Definition

**`@NamedQuery`** is a JPA annotation placed on an entity
class that pre-defines a JPQL query with a unique name.
The query is validated at `EntityManagerFactory` startup.
It is referenced at runtime by name using
`em.createNamedQuery("queryName", ResultClass.class)`.

**`@NamedNativeQuery`** is the equivalent for raw SQL
with a result mapping declaration.

**Native Query** (via `em.createNativeQuery()`) executes
raw SQL. Results can be:

- Object arrays (`Object[]`) - no mapping
- A specific entity class - Hibernate maps columns to fields
- A custom mapping via `@SqlResultSetMapping`
- An interface projection (Spring Data) - for DTO results

**Named Query Repository Method** in Spring Data:
`@Query(name = "Product.findActive")` can reference a
`@NamedQuery` defined on the entity.

---

### ⏱️ Understand It in 30 Seconds

**One line:** `@NamedQuery` pre-defines and validates
JPQL at startup; native queries run raw SQL when JPQL
cannot express the needed operation.

**One analogy:**

> `@NamedQuery` is like a restaurant's printed menu
> (queries pre-approved by the chef). If a dish isn't
> on the menu, it's caught before opening. Native query
> is like calling the chef directly and asking for
> something off-menu - you specify exactly what you want,
> bypassing the menu system entirely.

**One insight:** Spring Data `@Query` is functionally
a named query that is validated at startup by Hibernate
(same validation path). The key difference is that
`@NamedQuery` lives on the entity class; `@Query` lives
on the repository interface. Both validate JPQL at
`EntityManagerFactory` creation.

---

### 🔩 First Principles Explanation

**@NamedQuery VALIDATION TIMING:**

```
Application startup:
  1. Spring Boot creates EntityManagerFactory
  2. Hibernate processes all @Entity classes
  3. For each @NamedQuery found:
     a. Parses JPQL string (ANTLR grammar)
     b. Resolves entity names -> metadata
     c. Validates field names against entity fields
     d. Validates types (e.g., numeric parameter for
        numeric field)
  4. If validation fails: startup fails with
     QuerySyntaxException
     -> Forces fix before deployment reaches production

Runtime (no re-validation):
  - em.createNamedQuery("name", Type.class) looks up
    pre-compiled query plan from cache
  - No re-parsing; faster than ad-hoc queries
  - Named query re-uses same plan every execution
```

**NATIVE QUERY RESULT MAPPING OPTIONS:**

```
Option 1: Object array (simplest, no type safety)
  em.createNativeQuery("SELECT id, name FROM products")
  -> returns List<Object[]>

Option 2: Entity mapping (automatic if columns match)
  em.createNativeQuery(sql, Product.class)
  -> Hibernate maps columns to @Column fields by name
  -> Returns List<Product>

Option 3: @SqlResultSetMapping (explicit, flexible)
  @SqlResultSetMapping(name="ProductMap",
    entities=@EntityResult(entityClass=Product.class))
  em.createNativeQuery(sql, "ProductMap")

Option 4: Spring Data interface projection
  @Query(value="SELECT id, name FROM products",
         nativeQuery=true)
  List<ProductProjection> findActive();
  // ProductProjection is an interface with getId(),getName()
```

---

### 🧪 Thought Experiment

**NAMED QUERY VS AD-HOC: STARTUP VALIDATION BENEFIT:**

```java
// Scenario 1: @NamedQuery (VALIDATED AT STARTUP)
@NamedQuery(
    name = "Order.findByStatus",
    query = "SELECT o FROM Order o " +
            "WHERE o.statuss = :s")  // TYPO: statuss

// At startup: Hibernate parses this query and finds
// "statuss" is not a field on Order entity
// -> Application FAILS TO START
// -> Error caught before any deployment
// -> "Unknown state field path 'o.statuss'"

// Scenario 2: @Query (ALSO validated at startup via
// Spring Data's query validation)
@Query("SELECT o FROM Order o WHERE o.statuss = :s")
// Same result: startup fails with validation error

// Scenario 3: em.createQuery() in service method (NOT validated)
public List<Order> findActive() {
    return em.createQuery(
        "FROM Order o WHERE o.statuss = :s", Order.class)
        .getResultList();
    // ONLY fails when this code path is called at runtime
    // Typo survives until production execution
}
```

---

### 🧠 Mental Model / Analogy

> `@NamedQuery` is like a pre-approved recipe in a kitchen.
> Every component is validated before service begins
> (startup). If an ingredient is wrong (bad field name),
> the kitchen refuses to open. Native query is like a
> special order written on a napkin - the chef follows
> the exact instructions, no validation is done by the
> menu system (ORM), and the result must be mapped back
> to the kitchen's standard dishes manually
> (`@SqlResultSetMapping`).

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
`@NamedQuery` gives a name to a JPQL query so it can be
reused by name. Native queries let you write raw SQL when
JPQL can't do the job.

**Level 2 - How to use it (junior developer):**
Put `@NamedQuery(name="...", query="...")` on an entity
class. Execute with `em.createNamedQuery("name", Type.class)`.
Use `@Query(nativeQuery=true, value="...")` in Spring
Data for native SQL.

**Level 3 - How it works (mid-level engineer):**
`@NamedQuery` is parsed and validated during Hibernate
startup via the same ANTLR parser used for ad-hoc queries.
The difference: errors surface at startup instead of
runtime. The compiled query plan is stored in the query
plan cache and reused on every execution (faster than
re-parsing).

**Level 4 - Trade-offs (senior/staff):**
`@NamedQuery` tightly couples query definitions to the
entity class (violates separation of concerns for complex
repositories). In Spring Data projects, `@Query` on
the repository interface is preferred - same startup
validation, better co-location with the repository.
Native queries are not validated at startup and are
database-specific; they require testing against each
target database. For complex analytics native queries,
JOOQ or Querydsl with SQL dialect generates type-safe
native SQL with IDE refactoring support.

**Level 5 - Architecture (distinguished engineer):**
`@NamedNativeQuery` with `@SqlResultSetMapping` can map
complex SQL result sets to entity graphs (including
nested associations via `@ConstructorResult`). For very
high performance read paths where entity materialization
overhead is unacceptable, native queries returning
`@ConstructorResult` (flat DTOs) bypass the full
entity lifecycle, avoid dirty checking setup, and are
typically 2-5x faster than loading managed entities.
This is the pattern used in high-QPS read models within
JPA-based applications, bridging the gap to raw JDBC
performance without leaving the Spring ecosystem.

---

### ⚙️ How It Works (Mechanism)

**@NamedQuery LIFECYCLE:**

```java
@Entity
@NamedQuery(
    name  = "Product.findByCategoryAndStatus",
    query = "SELECT p FROM Product p " +
            "JOIN p.category c " +
            "WHERE c.name = :cat AND p.active = :active " +
            "ORDER BY p.name"
)
@NamedQuery(  // Multiple: use @NamedQueries({...})
    name  = "Product.countByCategory",
    query = "SELECT COUNT(p) FROM Product p " +
            "JOIN p.category c " +
            "WHERE c.name = :cat"
)
public class Product {
    // Entity fields...
}

// Runtime usage:
List<Product> results = em
    .createNamedQuery("Product.findByCategoryAndStatus",
                      Product.class)
    .setParameter("cat", "Electronics")
    .setParameter("active", true)
    .getResultList();
```

**MULTIPLE @NamedQuery SYNTAX:**

```java
@NamedQueries({
    @NamedQuery(name="Product.findActive",
                query="FROM Product p WHERE p.active=true"),
    @NamedQuery(name="Product.findByPrice",
                query="FROM Product p WHERE p.price < :max")
})
@Entity
public class Product { ... }
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NATIVE QUERY PATTERNS:**

```java
// Pattern 1: Simple scalar result
List<Object[]> rows = em
    .createNativeQuery(
        "SELECT id, name, price FROM products " +
        "WHERE price > ? AND active = true")
    .setParameter(1, 100.0)
    .getResultList();
// Positional ? parameters in native queries
// Returns Object[]: rows[i][0]=id, [1]=name, [2]=price

// Pattern 2: Entity result (column names must match
//             or use @Column(name=...) annotations)
List<Product> products = em
    .createNativeQuery(
        "SELECT * FROM products WHERE active = true",
        Product.class)
    .getResultList();

// Pattern 3: Window function (not possible in JPQL)
List<Object[]> ranked = em
    .createNativeQuery(
        "SELECT id, name, price, " +
        "  RANK() OVER (PARTITION BY category_id " +
        "               ORDER BY price DESC) AS rnk " +
        "FROM products")
    .getResultList();

// Pattern 4: Spring Data nativeQuery=true
@Query(value = "SELECT p.id, p.name, " +
               "COALESCE(AVG(r.score), 0) AS avg_score " +
               "FROM products p " +
               "LEFT JOIN reviews r ON r.product_id = p.id " +
               "GROUP BY p.id, p.name " +
               "ORDER BY avg_score DESC",
       nativeQuery = true)
List<ProductRatingProjection> findTopRated();

// interface projection (Spring auto-maps by column name):
interface ProductRatingProjection {
    Long getId();
    String getName();
    Double getAvgScore();
}
```

---

### 💻 Code Example

**Example 1 - BAD: ad-hoc query with typo (runtime failure):**

```java
// BAD: ad-hoc query - typo not caught until execution
public List<Order> findPending() {
    return em.createQuery(
        "FROM Order o WHERE o.statuss = :s",
        Order.class)
        .setParameter("s", "PENDING")
        .getResultList();
    // RuntimeException when this method is called:
    // "QuerySyntaxException: Undefined attribute:
    //  statuss in Order"
}

// GOOD: use @NamedQuery or @Query
// Caught at startup:
@NamedQuery(name="Order.findPending",
    query="FROM Order o WHERE o.status = :s")
// OR (Spring Data):
@Query("SELECT o FROM Order o WHERE o.status = :s")
List<Order> findByStatus(@Param("s") String status);
```

**Example 2 - Native query with interface projection:**

```java
// Complex SQL: CTE + window function (JPQL cannot do this)
@Query(value =
    "WITH ranked AS (" +
    "  SELECT *, ROW_NUMBER() OVER " +
    "    (PARTITION BY customer_id " +
    "     ORDER BY created_at DESC) AS rn " +
    "  FROM orders" +
    ") " +
    "SELECT id, customer_id, total, created_at " +
    "FROM ranked WHERE rn = 1",
    nativeQuery = true)
List<LatestOrderProjection> findLatestPerCustomer();

interface LatestOrderProjection {
    Long getId();
    Long getCustomerId();
    BigDecimal getTotal();
    LocalDateTime getCreatedAt();
}
// Spring Data auto-maps columns to interface methods
// by name (camelCase = snake_case mapping automatic)
```

**Example 3 - Named native query with SqlResultSetMapping:**

```java
@SqlResultSetMapping(
    name = "ProductSummaryMapping",
    classes = @ConstructorResult(
        targetClass = ProductSummary.class,
        columns = {
            @ColumnResult(name = "id",    type = Long.class),
            @ColumnResult(name = "name",  type = String.class),
            @ColumnResult(name = "total", type = Integer.class)
        }
    )
)
@NamedNativeQuery(
    name = "Product.summaryByCategory",
    query = "SELECT p.id, p.name, COUNT(o.id) AS total " +
            "FROM products p " +
            "LEFT JOIN order_items oi ON oi.product_id=p.id " +
            "WHERE p.category_id = :catId " +
            "GROUP BY p.id, p.name",
    resultSetMapping = "ProductSummaryMapping"
)
@Entity
public class Product { ... }

// ProductSummary must have matching constructor:
public class ProductSummary {
    public ProductSummary(Long id, String name,
                          Integer total) { ... }
}
```

---

### ⚖️ Comparison Table

| Query Type               | Validation   | Database portability                         | Use case                                   |
| ------------------------ | ------------ | -------------------------------------------- | ------------------------------------------ |
| `@NamedQuery` (JPQL)     | Startup      | Portable (all JPQL-compatible DBs)           | Reusable named JPQL; early error detection |
| `@Query` (Spring Data)   | Startup      | Portable (JPQL) or DB-specific (native=true) | Repository-scoped queries                  |
| `em.createQuery()`       | Runtime only | Portable                                     | One-off JPQL in service methods            |
| `em.createNativeQuery()` | Runtime only | DB-specific                                  | DB-specific features; stored procs         |

---

### ⚠️ Common Misconceptions

| Misconception                                                     | Reality                                                                                                                                                                                                                                                                      |
| ----------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "`@NamedQuery` is required for named queries in Spring Data"      | Spring Data `@Query` is equivalent and more common. `@NamedQuery` is the pure JPA approach. `@Query` has the same startup validation and better co-location with repository code.                                                                                            |
| "Native queries bypass all JPA features"                          | Native queries returning entity classes still go through the Hibernate entity lifecycle: returned entities are managed, dirty checking applies, and the first-level cache holds them. Only `createNativeQuery(sql)` with `Object[]` result fully bypasses entity management. |
| "Native queries can return any columns in any order"              | Native queries mapped to an entity class depend on column-to-field name matching (Hibernate maps by column alias to `@Column` names). Mismatched aliases cause mapping errors or null fields.                                                                                |
| "`@NamedQuery` is faster than `@Query` because it's pre-compiled" | Both `@NamedQuery` and Spring Data `@Query` pre-compile and cache the query plan at startup. The runtime performance is identical. `@NamedQuery`'s advantage is startup validation, not execution speed over `@Query`.                                                       |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: @NamedQuery References Wrong Field (caught at startup)**

**Symptom:** Application fails to start with:
`org.hibernate.QueryException: could not resolve property: statuss of: com.example.Order`
**Cause:** Typo in the `@NamedQuery` JPQL string.
**Fix:** Correct the field name in the `@NamedQuery`.
The startup failure is the desired behavior - it prevents
a runtime bug from reaching production.

---

**Failure Mode 2: Native Query Column Mismatch**

**Symptom:** Entity fields are `null` after `createNativeQuery(sql, Product.class)`. No exception.
**Root Cause:** SQL `SELECT` aliases do not match the
`@Column(name=...)` values for the entity's fields.
Hibernate silently sets unmatched fields to `null`.
**Diagnosis:** Log the SQL and check that every `@Column(name="...")` has a matching column in the SELECT.
**Fix:** Use column aliases that match `@Column` names:

```sql
SELECT p.product_id AS id, p.product_name AS name
FROM products p
```

---

**Failure Mode 3: Startup Performance from Too Many @NamedQuery**

**Symptom:** Application startup is slow (>30 seconds)
with thousands of entity classes each having multiple
`@NamedQuery` annotations.
**Root Cause:** Each `@NamedQuery` is parsed and compiled
at startup. With many queries, ANTLR parsing + metadata
resolution accumulates.
**Fix:** Batch large query sets. Prefer Spring Data `@Query`
(same startup validation) but loaded lazily per repository.
Consider splitting into multiple persistence units if the
model is very large.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[JPH-014 - JPQL]] - `@NamedQuery` uses JPQL syntax;
  understand JPQL first
- [[JPH-023 - @Query]] - Spring Data equivalent with
  same startup validation

**Builds On This (learn these next):**

- [[JPH-030 - DTO Projections]] - native queries with
  interface projections are a DTO strategy
- [[JPH-031 - Hibernate Session vs EntityManager]] - HQL
  named queries vs JPA named queries

**Related:**

- [[JPH-036 - Criteria API]] - type-safe programmatic
  alternative to string-based named queries
- [[JPH-057 - JPA Specification (JSR 338)]] - `@NamedQuery`
  is a formal part of the JPA spec

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ @NamedQuery  │ On @Entity; validated at startup         │
│              │ Ref: em.createNamedQuery("Name", T.class) │
├──────────────┼───────────────────────────────────────────┤
│ MULTIPLE     │ @NamedQueries({@NamedQuery(...), ...})   │
├──────────────┼───────────────────────────────────────────┤
│ NATIVE       │ em.createNativeQuery(sql, Entity.class)  │
│              │ OR @Query(nativeQuery=true) Spring Data   │
├──────────────┼───────────────────────────────────────────┤
│ PROJECTION   │ nativeQuery=true + interface projection  │
│              │ Spring Data auto-maps column->method name │
├──────────────┼───────────────────────────────────────────┤
│ WHEN NATIVE  │ Window functions, CTEs, UPSERT,          │
│              │ DB JSON operators, stored procs           │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "@NamedQuery: startup-validated reusable │
│              │ JPQL. Native queries: raw SQL for DB-     │
│              │ specific features JPQL can't express."   │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. `@NamedQuery` validates JPQL at startup - typos fail
   the startup rather than failing at runtime in production
2. Spring Data `@Query` gives the same startup validation
   and is preferred in Spring Boot projects
3. Use native queries for SQL features JPQL cannot express:
   window functions, CTEs, DB-specific operators, stored
   procedures

**Interview one-liner:** `@NamedQuery` pre-defines JPQL
on an entity class and validates it at EntityManagerFactory
startup - errors surface before deployment. `@Query` in
Spring Data has equivalent validation. Native queries
execute raw SQL for DB-specific features that JPQL cannot
express (window functions, CTEs, JSON operators). Native
query results map to entities or interface projections.

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Fail-fast at startup,
not at runtime. `@NamedQuery`'s startup validation embodies
this principle: detect errors as early as possible in the
deployment pipeline. This same principle drives compile-
time type checking (vs runtime), unit test assertions
(vs production failures), and database migration validation
(Flyway/Liquibase fail builds if migrations break). The
cost of detecting an error grows exponentially with how
late it is caught: compile-time < test-time < staging <
production. Startup validation falls between test-time
and staging - better than runtime, but earlier startup
validation (via compile-time query builders like JOOQ or
Querydsl) is possible and even more powerful.

**Where else this pattern appears:**

- **JOOQ** - SQL queries are compile-time type-checked
  (DSL against generated schema classes)
- **Querydsl** - JPQL-based queries generated from
  metamodel classes; compile-time type safety
- **Flyway/Liquibase** - SQL migration scripts validated
  at startup; fail-fast on schema errors
- **Spring Cache** - `@Cacheable` expressions validated
  at context creation in strict mode

---

### 💡 The Surprising Truth

Native queries in JPA are NOT automatically sanitized.
If you build a native query string by concatenating
user input - even a small part like an ORDER BY column
name - it is vulnerable to SQL injection. Unlike JPQL
named parameters which are bound at the JDBC
`PreparedStatement` level, native query string
concatenation is direct SQL manipulation. This means:
never use string concatenation with user-provided values
in native SQL. For dynamic ORDER BY column names from
user input, use a whitelist/allowlist validation (compare
the input against a set of allowed column names before
embedding in the query). For dynamic WHERE clauses,
use `setParameter()` for values (not column names -
column names cannot be parameterized in SQL). The fact
that `@NamedQuery` and `@Query` with JPQL use named
parameters internally (bound via `PreparedStatement`)
is why they are injection-safe; native queries with
string concatenation are not.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **DEFINE** a `@NamedQuery` on an entity and call it
   via `em.createNamedQuery()`
2. **WRITE** a Spring Data repository method using
   `nativeQuery=true` with an interface projection
3. **EXPLAIN** why `@NamedQuery` catches errors at startup
   vs `em.createQuery()` catching them at runtime
4. **MAP** a native query result to a DTO using
   `@SqlResultSetMapping` with `@ConstructorResult`
5. **IDENTIFY** use cases where native queries are the
   correct tool (window functions, CTEs, DB functions)

---

### 🎯 Interview Deep-Dive

**Q1: What is the advantage of @NamedQuery over creating
the JPQL string inline in the service method?**
_Why they ask:_ Tests understanding of fail-fast and
startup validation benefits.
_Strong answer includes:_

- Startup validation: JPQL parsed and field names resolved
  at `EntityManagerFactory` initialization; typos/wrong
  fields cause startup failure, not runtime exceptions
- Pre-compiled query plan: no re-parsing on each execution;
  query plan cached and reused
- Reusability: same named query reused across multiple
  service methods by name; reduces duplication
- Spring Data `@Query` alternative: preferred in Spring
  Boot for co-location with repository interface; same
  startup validation benefit

**Q2: When would you choose a native query over JPQL?
Give three concrete examples.**
_Why they ask:_ Tests practical SQL and ORM knowledge.
_Strong answer includes:_

1. Window functions: `RANK() OVER (PARTITION BY ... ORDER BY ...)` - not available in JPQL; required for ranked lists, percentile calculations
2. CTEs (`WITH`): recursive queries, multi-step transformations - JPQL has no CTE support
3. DB-specific operators: PostgreSQL JSON operators (`->>`, `@>`), `SIMILAR TO`, `ILIKE`, `array_agg()` - not in JPQL/HQL standard
4. `UPSERT`/`ON CONFLICT DO UPDATE` (PostgreSQL) or `INSERT ... ON DUPLICATE KEY UPDATE` (MySQL) - not in JPQL
5. Stored procedure calls (though `@StoredProcedureQuery` also works)

**Q3: Are native queries safe from SQL injection?**
_Why they ask:_ Tests security awareness with JPA/Hibernate.
_Strong answer includes:_

- Native queries using `setParameter()` or `:namedParam`
  are safe: Hibernate binds values via JDBC
  `PreparedStatement`, which sanitizes values
- Native queries built with string concatenation of user
  input are NOT safe: it's direct SQL string manipulation
- Common mistake: dynamically constructing ORDER BY with
  user-provided column name: `"ORDER BY " + userInput`
  - column names cannot be parameterized in SQL; must
    use whitelist validation
- Named parameters work for WHERE clause values only;
  table/column names must always be whitelisted if dynamic
