---
id: JPH-014
title: "JPQL (Java Persistence Query Language)"
category: JPA & Hibernate
tier: tier-3-java
folder: JPH-jpa-hibernate
difficulty: ★★☆
depends_on: JPH-006, JPH-008, JPH-011, JPH-013
used_by: JPH-020, JPH-021, JPH-022, JPH-023
related: JPH-025, JPH-033
tags:
  - java
  - database
  - jpa
  - foundational
status: complete
version: 4
layout: default
parent: "JPA & Hibernate"
grand_parent: "Technical Dictionary"
nav_order: 14
permalink: /jpa-hibernate/jpql/
---

# JPH-014 - JPQL (Java Persistence Query Language)

⚡ **TL;DR** - JPQL is an object-oriented query language that
operates on entity classes and their fields (not database
tables and columns), producing results that are either
managed entity instances or scalar values.

| #014 | Category: JPA & Hibernate | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | @Entity, @Table and @Column, EntityManager, Entity Lifecycle | |
| **Used by:** | N+1 Problem, JOIN FETCH, Named Queries, @EntityGraph | |
| **Related:** | Criteria API, Native SQL Queries | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Without JPQL, every database query requires writing SQL
that references database table names and column names.
When an entity class is renamed, every SQL string must be
found and updated manually. When a field is renamed in Java,
the SQL strings are not updated by IDE rename refactors
because they are plain strings.

**THE BREAKING POINT:**
A large application with 200 `@Entity` classes and 1000+
SQL strings in code becomes a maintenance nightmare. Each
database schema change cascades into dozens of SQL updates.
The type safety of Java is lost the moment the query crosses
into a string literal. Typos in column names are caught
only at runtime.

**THE INVENTION MOMENT:**
JPQL targets the Java entity model, not the database schema.
`SELECT p FROM Product p WHERE p.name = :name` uses the Java
class `Product` and Java field `name` - not the database table
`tbl_products` and column `PROD_NM`. The JPA provider
translates JPQL to SQL at query execution time using the
entity metadata. If the entity is renamed or the `@Column`
mapping changes, the SQL changes automatically - the JPQL
string remains valid.

---

### 📘 Textbook Definition

**JPQL (Java Persistence Query Language)** is a
platform-independent query language defined in the Jakarta
Persistence specification. It operates on the logical entity
model: queries reference entity class names and their field
names, not database table and column names. JPQL is similar
to SQL in structure (SELECT, FROM, WHERE, JOIN, GROUP BY,
ORDER BY) but entity-model oriented.

Key characteristics:
- **Entity-centric**: `FROM Product p` references the Java
  entity class, not the database table
- **Field-name based**: `p.name` references the Java field,
  not the database column (`PROD_NM`)
- **Database-independent**: the same JPQL runs on MySQL,
  PostgreSQL, or Oracle
- **Returns managed entities or scalars**: query results
  are placed in the persistence context unless projections
  are used

---

### ⏱️ Understand It in 30 Seconds

**One line:** JPQL is SQL for entity objects - it queries
your Java classes and fields instead of database tables
and columns.

**One analogy:**
> JPQL is to SQL what Google Maps street names are to
> GPS coordinates. SQL requires exact coordinates (table
> names, column names). JPQL uses human-readable names
> (Java class names, field names) and the JPA provider
> does the coordinate translation. If the building moves
> (schema change), the GPS coordinates need updating,
> but the street name address still works.

**One insight:** JPQL is always translated to SQL at
runtime by the JPA provider. The same JPQL can generate
very different SQL depending on the database dialect,
entity mapping configuration, and the number of entities
in the result set. When debugging JPQL, always check the
generated SQL with `spring.jpa.show-sql=true`.

---

### 🔩 First Principles Explanation

**JPQL vs SQL NAMING:**

```
JPQL                   SQL (generated)
─────────────────────  ─────────────────────────────
Product                tbl_products (via @Table)
p.name                 p.PROD_NM (via @Column)
p.category.name        c.CAT_NAME (via JOIN on FK)
```

**FIVE CLAUSE TYPES:**

```
SELECT p          -- what to return (entity or fields)
FROM Product p    -- entity class (NOT table name)
JOIN p.orders o   -- entity field (NOT FK column)
WHERE p.price > 100
ORDER BY p.name
```

**PARAMETER BINDING (two styles):**

```
Named parameters (preferred):
  "SELECT p FROM Product p WHERE p.id = :id"
  query.setParameter("id", 42L);

Positional parameters (avoid in Spring):
  "SELECT p FROM Product p WHERE p.id = ?1"
  query.setParameter(1, 42L);
```

**CORE INVARIANTS:**
1. JPQL FROM clause uses entity class names (Java), not table names
2. JPQL field paths use Java field names, not column names
3. JPQL results are managed entities (unless using projections)
4. JPQL queries bypass the first-level cache - they always
   execute SQL; results ARE stored in the persistence context
5. Named parameters (`:name`) are safe from SQL injection
   - positional and named parameters both go through JDBC
   PreparedStatement, never concatenated into SQL

---

### 🧪 Thought Experiment

**SETUP:**
You have a `Product` entity with `@Table(name="tbl_products")`
and `@Column(name="PROD_NM")` on the `name` field.

**WITH SQL (raw):**

```sql
SELECT * FROM tbl_products WHERE PROD_NM = 'Widget'
```

This works. Now you rename the table to `products` (Flyway
migration) and update `@Table(name="products")`. The raw
SQL is now broken - you must find and update it.

**WITH JPQL:**

```java
"SELECT p FROM Product p WHERE p.name = :name"
```

When `@Table(name="products")` is updated, Hibernate
regenerates the SQL as `SELECT ... FROM products ...`
automatically. The JPQL string has not changed. The
developer does not need to find and update any string.

**THE INSIGHT:** JPQL provides a layer of indirection
between the query language and the database schema.
Schema changes that are reflected in entity annotations
propagate automatically to all JPQL queries. This is
the core value of JPQL over embedded SQL strings.

---

### 🧠 Mental Model / Analogy

> JPQL is the object-relational query bridge.
> On the left bank: Java classes, fields, relationships.
> On the right bank: SQL tables, columns, foreign keys.
> JPQL lets you write queries on the LEFT bank and the
> JPA provider builds the bridge to the RIGHT bank
> automatically using entity metadata.

- "Left bank" - Java object model
- "Right bank" - database schema
- "Bridge" - JPA provider's JPQL-to-SQL translation
- "Bridge construction" - entity metadata (annotations)
- "Bridge changes automatically" - JPQL survives schema changes

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
JPQL is a query language like SQL, but instead of writing
`FROM users WHERE email = 'alice@x.com'` (database table),
you write `FROM User u WHERE u.email = :email` (Java class).
JPA translates it to the correct SQL automatically.

**Level 2 - How to use it (junior developer):**
Use `em.createQuery(jpqlString, ResultType.class)`.
Use named parameters (`:name`). For Spring Data JPA,
add `@Query("SELECT p FROM Product p WHERE ...")` to a
repository method. The `@Query` value is JPQL by default.

**Level 3 - How it works (mid-level engineer):**
JPQL is parsed at `createQuery()` call time into an AST
(Abstract Syntax Tree). The AST is then compiled into an
SQL string using the entity metadata (table/column names
from annotations) and the database dialect. The SQL is
sent as a JDBC PreparedStatement with bound parameters.
Results are mapped back to entity instances and placed
in the persistence context.

**Level 4 - Why it was designed this way (senior/staff):**
JPQL's entity-centric design was driven by the goal of
database portability - the same JPQL should work across
MySQL, PostgreSQL, Oracle, and H2. The JPA provider
generates database-specific SQL from the portable JPQL.
This portability is the reason JPQL does NOT support all
SQL features: window functions, JSON path expressions, and
advanced aggregations are database-specific and thus
outside JPQL's scope. For such features, native SQL
(`em.createNativeQuery()`) is required.

**Level 5 - Mastery (distinguished engineer):**
JPQL query compilation is expensive and is cached by
Hibernate's query plan cache. The default cache size is
2048 entries. If your application generates dynamic JPQL
strings with literals (not parameters), the cache fills up,
old entries are evicted, and recompilation occurs for
every query - causing a performance cliff under load.
The fix: always use parameters (`:name`) not literals in JPQL;
never concatenate values into JPQL strings. The query plan
cache hit rate is visible in Hibernate statistics:
`org.hibernate.stat.QueryStatistics`.

**Expert Thinking Cues:**
- Ask: "Does this JPQL use JOIN FETCH or not?" - the
  presence of JOIN FETCH determines whether N+1 occurs
- Watch: JPQL with `IN` clauses and large parameter lists
  (`:ids` with 1000+ values) - each unique parameter count
  generates a different query plan; cache pollution
- Know: JPQL `UPDATE` and `DELETE` statements bypass the
  persistence context (bulk operations); after a JPQL
  bulk UPDATE, managed entities in the session may have
  stale field values until `em.refresh()` or `em.clear()`

---

### ⚙️ How It Works (Mechanism)

**JPQL Execution Pipeline:**

```
em.createQuery(
  "SELECT p FROM Product p WHERE p.price > :min")
    |
    v
[ JPQL Parser: string -> AST ]
    |  validates entity names, field names
    v
[ Query Plan Cache lookup ]
    |  cache hit -> skip compilation
    |  cache miss -> compile to SQL
    v
[ SQL Generator ]
    |  uses @Table, @Column, dialect
    |  "SELECT p.prod_id, p.PROD_NM, p.UNIT_PRICE"
    |  "FROM tbl_products p WHERE p.UNIT_PRICE > ?"
    v
[ JDBC PreparedStatement: bind :min parameter ]
    |
    v
[ Database executes SQL ]
    |
    v
[ ResultSet -> entity instances ]
    |  mapped to Java objects via column metadata
    v
[ Identity map: merge into persistence context ]
    |  if entity already in context, use existing
    |  if new entity, add to context
    v
[ Return List<Product> ]
```

**JPQL vs HQL (Hibernate Query Language):**
HQL is Hibernate's proprietary extension of JPQL. All
JPQL is valid HQL, but HQL supports additional features:
`TREAT`, implicit joins, `NATURAL JOIN`, and some aggregate
functions not in the JPQL spec. Use JPQL for portability;
use HQL only when a specific Hibernate feature is needed.

**CONCURRENCY / THREAD-SAFETY BEHAVIOR:**
`Query` objects returned by `createQuery()` are NOT
thread-safe. Each thread must call `createQuery()` to
obtain its own `Query` object. The query plan cache is
shared and thread-safe. `@NamedQuery` definitions are
compiled once at startup and cached.

---

### 🔄 The Complete Picture - End-to-End Flow

**SPRING DATA @Query FLOW:**

```
@Query("SELECT p FROM Product p " +
       "WHERE p.category.id = :catId " +
       "ORDER BY p.price DESC")
List<Product> findByCategoryOrderByPrice(
    @Param("catId") Long catId);

--- at call time: ---
repository.findByCategoryOrderByPrice(3L)
    |
    v
[ Spring Data proxy intercepts method call ]
    |  retrieves @Query annotation value
    v
[ em.createQuery(jpql, Product.class) ]
    |  parameter binding: catId=3L
    v
[ Generated SQL: ]
    SELECT p.id, p.prod_nm, p.unit_price,
           p.category_id
    FROM tbl_products p
    WHERE p.category_id = 3
    ORDER BY p.unit_price DESC
    |
    v
[ List<Product> returned, all MANAGED entities ]
```

**FAILURE PATH:**
If the JPQL uses a field name that does not exist on the
entity, `HibernateQueryException: could not resolve property:
prodName of: com.example.Product` is thrown at query parse
time. This happens at first execution (or at startup if
`@NamedQuery` is used, which is validated at startup).

**WHAT CHANGES AT SCALE:**
At scale, JPQL queries that return full entity objects carry
the overhead of loading all mapped columns and adding
entities to the persistence context (with snapshots for
dirty checking). For read-only reporting queries touching
millions of rows, use DTO projections: `SELECT new com.example.ProductDto(p.id, p.name)`
or interface-based projections in Spring Data. This reduces
memory by 50-90% for large result sets.

---

### 💻 Code Example

**Example 1 - Basic JPQL with named parameter:**

```java
public List<Product> findByCategory(
        String categoryName) {
    return em.createQuery(
        "SELECT p FROM Product p " +
        "WHERE p.category.name = :catName",
        Product.class)
        .setParameter("catName", categoryName)
        .getResultList();
}
```

**Example 2 - BAD: string concatenation (SQL injection and cache pollution):**

```java
// BAD: never concatenate values into JPQL
String jpql = "SELECT p FROM Product p " +
    "WHERE p.name = '" + name + "'";
// Pollutes query plan cache (unique query per name value)
// Technically injection-resistant (JPQL is not SQL)
// but still bad practice and cache-busting
em.createQuery(jpql, Product.class).getResultList();

// GOOD: always use parameters
em.createQuery(
    "SELECT p FROM Product p WHERE p.name = :n",
    Product.class)
    .setParameter("n", name)
    .getResultList();
```

**Example 3 - JPQL JOIN (implicit vs. explicit):**

```java
// Implicit join (JPQL only, not in standard SQL)
// Hibernate generates the JOIN automatically
em.createQuery(
    "SELECT p FROM Product p " +
    "WHERE p.category.name = :cat",
    Product.class);
// Generated: ... JOIN category c ON p.cat_id=c.id
//            WHERE c.name = ?

// Explicit JOIN (more control)
em.createQuery(
    "SELECT p FROM Product p " +
    "JOIN p.category c " +
    "WHERE c.name = :cat",
    Product.class);
```

**Example 4 - DTO projection to avoid full entity load:**

```java
// For read-only reporting: load only needed fields
em.createQuery(
    "SELECT new com.example.dto.ProductSummary(" +
    "  p.id, p.name, p.price) " +
    "FROM Product p " +
    "WHERE p.price > :min",
    ProductSummary.class)
    .setParameter("min", BigDecimal.valueOf(100))
    .getResultList();
// ProductSummary constructor:
// public ProductSummary(Long id, String name, BigDecimal price)
// Results are NOT added to persistence context
// No snapshot overhead; read-only optimised
```

**Example 5 - Bulk UPDATE (bypasses persistence context):**

```java
// Updates database directly - managed entities
// in session may have stale values after this
int updatedCount = em.createQuery(
    "UPDATE Product p SET p.price = p.price * 1.1 " +
    "WHERE p.category.id = :catId")
    .setParameter("catId", 5L)
    .executeUpdate();

// IMPORTANT: clear persistence context after bulk update
em.clear(); // ensures stale entities are not used
```

---

### ⚖️ Comparison Table

| Feature | JPQL | HQL | Criteria API | Native SQL |
|---|---|---|---|---|
| Syntax | SQL-like string | SQL-like string | Type-safe Java API | Raw SQL string |
| Target | Entity model | Entity model | Entity model | Database schema |
| Type safety | No (compile time) | No | Yes | No |
| IDE support | Limited | Limited | Full | None |
| Portability | Full | Hibernate only | Full | DB-specific |
| Complex queries | Good | Better (HQL extensions) | Verbose but powerful | Unlimited |

**How to choose:**
- Simple to medium queries: JPQL with `@Query` in Spring Data
- Dynamic queries (runtime-built): Criteria API or Querydsl
- Complex aggregations/window functions: Native SQL
- Full text search, JSON path: Native SQL

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "JPQL query results bypass the persistence context because it's a query" | JPQL results ARE loaded into the persistence context. Each returned entity is added to the identity map and tracked for dirty checking. Only DTO projections bypass the persistence context. |
| "JPQL WHERE clause uses database column names" | JPQL uses Java field names. `WHERE p.firstName = :name` (Java field) NOT `WHERE p.FIRST_NM = :name` (DB column). Using the column name in JPQL causes a `QueryException: could not resolve property`. |
| "`IN` clause with a List parameter works without size limits" | JPQL `WHERE p.id IN :ids` with a list of 1000+ IDs may fail on databases with IN clause limits (Oracle has a 1000-item limit per IN clause). Split large lists or use a JOIN with a temporary table. |
| "JPQL bulk UPDATE and DELETE are tracked by dirty checking" | Bulk JPQL UPDATE/DELETE bypass the persistence context entirely. Managed entities in the session are NOT updated. After a bulk operation, call `em.clear()` to ensure the session reflects the new database state. |
| "JPQL is compiled once and cached globally" | JPQL is compiled per distinct query string. If parameters are concatenated into the string (anti-pattern), each value creates a new unique query string that is separately compiled and cached - exhausting the query plan cache. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Stale Entities After Bulk Update**

**Symptom:** After a JPQL bulk `UPDATE`, loading the same
entities shows old values even though the database was updated.
**Root Cause:** JPQL bulk operations bypass the persistence
context. Managed entities in the session still have pre-update
snapshots and field values.
**Diagnostic:**

```bash
spring.jpa.show-sql=true
# Verify UPDATE executed: "update tbl_products set price=..."
# Then verify subsequent SELECT still returns old price
# -> confirms persistence context serving stale data
```

**Fix:**

```java
// After any JPQL bulk update:
em.createQuery(
    "UPDATE Product p SET p.price = p.price * 1.1")
    .executeUpdate();
em.clear();  // evict stale managed entities
// Next em.find() will load fresh data from DB
```

**Prevention:** Encapsulate bulk operations in methods that
call `em.clear()` after the bulk statement. Document that
callers should not hold references to managed entities
that overlap with the bulk update's scope.

---

**Failure Mode 2: Query Plan Cache Exhaustion**

**Symptom:** Application performance degrades over time;
heap profiler shows growing `org.hibernate.query.spi.QueryPlanCache`;
memory usage climbs without recovery.
**Root Cause:** JPQL strings with concatenated values
(not parameters) generate unique query strings per value,
each cached in the query plan cache (default 2048 entries,
LRU eviction). Recompilation on every cache miss is expensive.
**Diagnostic:**

```bash
spring.jpa.properties.hibernate.generate_statistics=true
logging.level.org.hibernate.stat=DEBUG
# Look for: "QueryPlanCache miss" ratio
# or monitor: hibernate.cache.query_plan_cache.miss_count
```

**Fix:** Replace all concatenated JPQL strings with
named parameters:

```java
// BAD: unique cache entry per status value
String jpql = "FROM Order o WHERE o.status = '"
    + status + "'";

// GOOD: one cache entry for all status values
String jpql =
    "FROM Order o WHERE o.status = :status";
query.setParameter("status", status);
```

**Prevention:** Code review policy: no string concatenation
in JPQL. Use static analysis to detect it.

---

**Failure Mode 3: N+1 from Missing JOIN FETCH**

**Symptom:** Logging shows 1 SELECT for the product list
plus N SELECT statements for each product's category:
1 + N = N+1 queries for N products.
**Root Cause:** `@ManyToOne(fetch=EAGER)` on `category`
with JPQL `SELECT p FROM Product p` - Hibernate issues
N separate SELECTs for each product's category (EAGER
but no JOIN in the query).
**Diagnostic:**

```bash
spring.jpa.show-sql=true
# Count the number of SELECT statements for a list query
# If count > 1, N+1 is occurring
```

**Fix:**

```java
// BAD: N+1 with EAGER fetch and no JOIN
em.createQuery(
    "SELECT p FROM Product p",
    Product.class).getResultList();

// GOOD: JOIN FETCH loads category in one query
em.createQuery(
    "SELECT DISTINCT p FROM Product p " +
    "LEFT JOIN FETCH p.category",
    Product.class).getResultList();
```

**Prevention:** All JPQL queries accessing lazy collections
must use `JOIN FETCH` or `@EntityGraph`. See JPH-020 (N+1
Problem) for comprehensive fix strategies.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[JPH-006 - @Entity]] - JPQL FROM clause uses @Entity
  class names
- [[JPH-008 - @Table and @Column]] - the metadata JPQL
  relies on for SQL translation; `@Column(name=...)` maps
  Java field names to DB columns
- [[JPH-011 - EntityManager]] - `em.createQuery()` is
  the entry point for all JPQL queries
- [[JPH-013 - Entity Lifecycle (NEW, MANAGED, DETACHED, REMOVED)]] -
  JPQL results are MANAGED entities in the persistence context

**Builds On This (learn these next):**
- [[JPH-020 - N+1 Problem]] - the most critical JPQL
  performance failure mode
- [[JPH-021 - JOIN FETCH]] - the JPQL solution to N+1
- [[JPH-022 - Named Queries (@NamedQuery)]] - compile-time
  validated JPQL queries
- [[JPH-023 - @EntityGraph]] - declarative fetch plan
  for JPQL queries

**Alternatives / Comparisons:**
- [[JPH-025 - Criteria API]] - type-safe programmatic
  alternative to JPQL strings
- [[JPH-033 - Native SQL Queries]] - for database-specific
  features beyond JPQL scope

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Object-oriented query language targeting  │
│              │ entity classes, not database tables       │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Database-independent queries; survives    │
│ SOLVES       │ schema changes via entity metadata        │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Uses Java field names (not column names). │
│              │ Results ARE in persistence context.       │
│              │ Always use :named parameters.             │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Standard entity queries; portability;     │
│              │ conditions on entity relationships        │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Window functions, JSON, DB-specific SQL  │
│              │ (use Native SQL); complex dynamic queries │
│              │ (use Criteria API / Querydsl)             │
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ String concatenation in JPQL; bulk UPDATE │
│              │ without em.clear(); no JOIN FETCH         │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ DB portability + refactor safety vs.     │
│              │ limited SQL feature coverage             │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "JPQL: SQL for your entity model;        │
│              │ always use :params, always JOIN FETCH"   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ JOIN FETCH -> N+1 Problem -> @EntityGraph │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. JPQL uses Java class/field names (not DB table/column
   names) - the JPA provider translates to SQL
2. Always use named parameters (`:name`) - never
   concatenate values into the JPQL string
3. JPQL bulk UPDATE/DELETE bypass the persistence context -
   call `em.clear()` after them to avoid stale entity state

**Interview one-liner:** JPQL is JPA's object-oriented query
language targeting entity class names and Java field names,
not database tables and columns. The JPA provider translates
JPQL to SQL using entity metadata. Always use named parameters
(`:name`) to prevent query plan cache pollution. Results are
managed entities in the persistence context; DTO projections
avoid this overhead for read-only queries.

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Indirection between
query language and storage schema is the key to schema
evolution without query breakage. Systems that query at
the logical model level (entities, fields) rather than
the physical model level (tables, columns) survive schema
changes more gracefully. This principle applies to
GraphQL (queries entity-shaped data, not tables),
Elasticsearch DSL (queries document fields, not column
names), and MongoDB aggregation pipelines (operate on
document fields, not SQL tables).

**Where else this pattern appears:**
- **GraphQL** - queries use field names from the GraphQL
  schema (logical model), not database columns; the resolver
  translates to DB queries - same indirection as JPQL
- **Elasticsearch Query DSL** - `{"match": {"title": "widget"}}`
  uses document field names; the index mapping translates
  to internal structure
- **Spring Data method names** - `findByFirstNameAndLastName()`
  is parsed into JPQL by Spring Data's method name parser;
  another layer of the same abstraction

---

### 💡 The Surprising Truth

JPQL queries do not guarantee that entity aliases in the
FROM clause match Java variable naming. `FROM Product p`
makes `p` the alias, but the generated SQL alias is
assigned by Hibernate (could be `product0_`, `product1_`,
etc. depending on the query context). This is why you must
use JPQL aliases (`p.name`) in the WHERE and SELECT clauses,
not column aliases from the generated SQL. Developers who
inspect the generated SQL and copy column aliases back into
JPQL are surprised when the query breaks on the next
Hibernate version upgrade (alias naming has changed between
Hibernate 5 and 6).

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **WRITE** a JPQL query with a JOIN (explicit), named
   parameters, and DTO projection from memory without
   referencing documentation
2. **TRACE** a JPQL query through the execution pipeline:
   parse -> plan cache -> SQL generation -> JDBC -> result
   mapping -> persistence context
3. **DISTINGUISH** when to use JPQL vs Criteria API vs
   Native SQL for a given query requirement and justify
   the choice with specific trade-offs
4. **DEBUG** a query plan cache exhaustion by recognising
   the symptom (growing memory, cache misses), identifying
   the concatenated JPQL root cause, and refactoring to
   named parameters
5. **APPLY** bulk JPQL UPDATE correctly including the
   `em.clear()` call after to prevent stale entity state

---

### 🧠 Think About This Before We Continue

**Q1 (TYPE D - Root Cause Trace):** A developer writes
`em.createQuery("SELECT p FROM Product p WHERE p.productName = :n")`.
At runtime, `HibernateQueryException: could not resolve
property: productName` is thrown. The database has a
column `PROD_NM`. The Java entity has a field named
`name` with `@Column(name="PROD_NM")`. What is the cause
and fix?
*Hint: JPQL uses Java field names (name), not property
names (productName) or column names (PROD_NM). The JPQL
must use `p.name`, not `p.productName` or `p.PROD_NM`.*

**Q2 (TYPE C - Design Trade-off):** Your reporting endpoint
returns a list of 50,000 `Product` entities using JPQL.
Response time is 8 seconds and memory usage spikes to 2GB.
Compare the options: (1) keep returning full entities, 
(2) use a DTO projection `SELECT new ProductDto(p.id, p.name, p.price)`,
(3) use native SQL with manual mapping. What does each
approach gain and sacrifice?
*Hint: Full entities = persistence context overhead + dirty
checking overhead + all column data. DTO projection = no
persistence context, selective columns, but still uses
JPQL. Native SQL = maximum flexibility but loses type
safety and portability.*

**Q3 (TYPE G - Hands-On):** Configure Hibernate statistics
in a Spring Boot application. Write a test that calls a
JPQL query 100 times with different literal values
concatenated into the string (bad practice), then call
the same query 100 times with named parameters. Measure
and compare: (a) query plan cache miss count, (b) query
execution time. Confirm that named parameters reduce
cache misses to 1 (the first call).

---

### 🎯 Interview Deep-Dive

**Q1: What is the difference between JPQL and SQL?
Why would you use JPQL instead of native SQL?**
*Why they ask:* Tests fundamental understanding of JPA
abstractions - why they exist and when to use them.
*Strong answer includes:*
- JPQL uses entity class names and Java field names;
  SQL uses database table and column names
- JPA translates JPQL to SQL using entity metadata;
  schema changes in `@Column` mappings propagate
  automatically to generated SQL
- JPQL is database-portable; SQL is database-specific
- Use native SQL for database-specific features (window
  functions, JSON path, full-text search) not in JPQL
- Use JPQL for standard queries on entity relationships

**Q2: What happens to the query plan cache when you
concatenate values into a JPQL string instead of using
parameters?**
*Why they ask:* Tests depth of JPQL implementation knowledge
and awareness of production performance traps.
*Strong answer includes:*
- Each unique JPQL string is compiled into a distinct
  query plan and cached separately
- Concatenating values produces a new unique string per
  value: `WHERE status = 'PENDING'`, `WHERE status = 'SHIPPED'`
  are two cache entries instead of one
- Under load with many distinct values, the cache fills
  (default 2048 entries), eviction occurs, and recompilation
  happens for every cache miss - CPU-intensive
- Fix: always use named parameters (`:status`); one cache
  entry covers all values of the parameter

**Q3: Why must you call `em.clear()` after a JPQL bulk
UPDATE or DELETE statement?**
*Why they ask:* Tests understanding of the persistence
context bypass by bulk operations.
*Strong answer includes:*
- JPQL bulk UPDATE/DELETE execute directly on the database
  without going through the persistence context
- Any managed entities in the session that match the
  UPDATE/DELETE criteria still have their pre-operation
  field values; they are now stale
- Calling `em.clear()` evicts all entities from the session;
  subsequent `em.find()` calls reload from the database
  with the correct post-operation values
- Without `em.clear()`, code that reads entities after a
  bulk update sees old data - a silent stale read bug