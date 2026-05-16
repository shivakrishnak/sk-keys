---
id: JPH-028
title: "HQL (Hibernate Query Language)"
category: JPA & Hibernate
tier: tier-3-java
folder: JPH-jpa-hibernate
difficulty: ★★☆
depends_on: JPH-006, JPH-007, JPH-008, JPH-011, JPH-014, JPH-018
used_by: JPH-029, JPH-031, JPH-033, JPH-058
related: JPH-036, JPH-053
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
nav_order: 28
permalink: /jpa-hibernate/hql/
---

# JPH-028 - HQL (Hibernate Query Language)

⚡ **TL;DR** - HQL is Hibernate's own object-oriented
query language - a superset of JPQL. It uses class and
field names (not table/column names), supports all JPQL
features, plus Hibernate-specific extensions:
`session.createQuery()` API, natural-id queries, SQL
functions via `function()`, and a richer type system.
If you are using pure JPA (`EntityManager`), write JPQL.
If you use Hibernate's `Session` API directly, you write
HQL. In Spring Boot, JPQL through `@Query` covers 95%
of cases; HQL is for Hibernate-native code paths.

| #028            | Category: JPA & Hibernate                                                                                  | Difficulty: ★★☆ |
| :-------------- | :--------------------------------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | @Entity, @Id/@GeneratedValue, @Table/@Column, EntityManager, JPQL, @OneToMany/@ManyToOne                   |                 |
| **Used by:**    | @NamedQuery and Native Queries, Hibernate Session vs EntityManager, First Level Cache, Hibernate Internals |                 |
| **Related:**    | Criteria API, QueryDSL with JPA                                                                            |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Before HQL (introduced in Hibernate 1.x, 2001), object-
relational mapping frameworks required raw SQL queries
that coupled application code to specific database column
names and table structures. A rename of the `customer_name`
column to `cust_name` required changing SQL strings
throughout the codebase. Schema refactoring was expensive.

**THE INVENTION:**
Hibernate Query Language queries against Java class names
and field names. The mapping layer (XML or annotations)
translates HQL to the correct SQL for the target database.
A schema rename only requires updating the `@Column`
mapping in one place; all HQL queries continue to work
unchanged. HQL is also database-portable: the same query
generates MySQL-dialect SQL or PostgreSQL-dialect SQL
automatically.

**RELATIONSHIP TO JPQL:**
JPQL (Java Persistence Query Language) was standardized
in JPA 1.0 (2006) and was directly inspired by HQL.
JPQL is the portable subset. HQL adds Hibernate-specific
features. In practice: JPQL queries are valid HQL queries
(Hibernate is the JPA provider, so it interprets both).
HQL queries with Hibernate extensions are NOT valid JPQL.

---

### 📘 Textbook Definition

**HQL (Hibernate Query Language)** is a string-based,
object-oriented query language native to Hibernate.
It queries against the Java entity model (class names,
field names, inheritance hierarchies) rather than
database tables and columns. Hibernate's query parser
translates HQL to SQL at query execution time using
the configured dialect.

**Key characteristics:**

- Case-insensitive for HQL keywords (`FROM`, `WHERE`, `JOIN`)
- Case-SENSITIVE for entity class names and field names
  (Java is case-sensitive: `Product` not `product`)
- Supports named parameters (`:paramName`) and
  positional parameters (`?1`)
- Supports aggregate functions, GROUP BY, HAVING,
  ORDER BY, DISTINCT
- HQL-only extensions: `FETCH ALL PROPERTIES`, natural-id
  queries, `ELEMENTS()`, `INDICES()`, tuple syntax,
  SQL function calls via `function('fn_name', args)`

---

### ⏱️ Understand It in 30 Seconds

**One line:** HQL queries Java class names and field names
instead of table/column names; Hibernate translates to
the correct SQL for your database.

**One analogy:**

> SQL is like giving GPS coordinates to a taxi driver.
> HQL is like saying "take me to the Empire State Building."
> The taxi driver (Hibernate) knows the actual address
> (SQL). You speak in human-readable names (Java classes
> and fields); the ORM knows the physical coordinates
> (table/column names in the database).

**One insight:** `SELECT * FROM Product p` in SQL fails
if you renamed the table. `FROM Product p` in HQL always
works because it refers to the Java class name, which is
mapped by `@Entity`/`@Table` to the current physical
table name. The mapping is the source of truth.

---

### 🔩 First Principles Explanation

**HQL vs JPQL vs NATIVE SQL COMPARISON:**

```
HQL ("FROM Product p WHERE p.name LIKE :n"):
  - Hibernate-specific; rich feature set
  - Uses Session.createQuery() or
    EntityManager.createQuery()
  - Supports Hibernate type extensions
  - Works through Hibernate dialect

JPQL ("SELECT p FROM Product p WHERE p.name LIKE :n"):
  - JPA standard; portable across JPA providers
  - Uses EntityManager.createQuery() only
  - Subset of HQL (most HQL is valid JPQL)
  - SELECT clause required (HQL allows omission)

Native SQL ("SELECT * FROM products WHERE name LIKE ?"):
  - Raw database SQL
  - Not portable; tied to DB dialect
  - Can return entities (with @SqlResultSetMapping)
  - Use for: stored procs, DB-specific features,
    performance-critical queries
```

**WHEN THE SELECT IS OPTIONAL IN HQL:**

```java
// JPQL (standard): SELECT is REQUIRED
TypedQuery<Product> q = em.createQuery(
    "SELECT p FROM Product p", Product.class);

// HQL (Hibernate): SELECT clause can be omitted
// Hibernate fills it in automatically
Query<Product> q = session.createQuery(
    "FROM Product p WHERE p.price > :min",
    Product.class);
// Equivalent to "SELECT p FROM Product p WHERE..."
// Valid HQL; not valid JPQL
```

---

### 🧪 Thought Experiment

**POLYMORPHIC QUERIES - HQL'S SUPERPOWER:**

```java
// Entity hierarchy:
// Animal (abstract @Entity @Inheritance(SINGLE_TABLE))
//   |- Dog @Entity
//   |- Cat @Entity

// HQL: polymorphic query - matches ALL subtypes
List<Animal> allAnimals =
    session.createQuery(
        "FROM Animal", Animal.class)
    .getResultList();
// SQL: SELECT * FROM animal WHERE dtype IN ('Dog', 'Cat')
// Hibernate handles the DTYPE discriminator automatically

// JPQL: same syntax, same behavior
// Only possible because HQL/JPQL understands inheritance

// SQL equivalent would require knowing DTYPE column exists
// HQL abstracts away the discriminator column completely
```

**WHY THIS MATTERS:** A new subtype `Parrot` added to the
hierarchy is automatically included in `FROM Animal` queries
without any query changes. The inheritance strategy
determines the SQL, not the query text.

---

### 🧠 Mental Model / Analogy

> HQL is like writing a search query against a
> well-catalogued library by topic, author, and subject
> (Java class names and field names). The library's index
> system (Hibernate mapping) translates your request
> to actual shelf and row numbers (SQL table/column names).
>
> The physical location (database schema) can change -
> a book moved to a different shelf - but your search
> query ("find all books by author X") remains valid
> because the catalog (ORM mapping) is always current.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
HQL lets you query the database using Java class and field
names instead of SQL table and column names. Hibernate
translates your HQL query into the correct SQL.

**Level 2 - How to use it (junior developer):**
Use `EntityManager.createQuery(hql, ResultClass.class)`
or `session.createQuery(hql, ResultClass.class)`. Write
queries using the Java entity name and its fields.
Always use named parameters (`:paramName`), never string
concatenation.

**Level 3 - How it works (mid-level engineer):**
Hibernate parses HQL using an ANTLR grammar at query
creation time (or startup for named queries). The parse
tree is converted to SQL using the configured dialect
(`MySQLDialect`, `PostgreSQLDialect`, etc.). Type
information from the entity metadata is used to generate
correct SQL type mappings. The generated SQL is cached
in the query plan cache.

**Level 4 - JPQL relationship (senior/staff):**
JPQL is the JPA standard; HQL is Hibernate's superset.
When you write a `@Query` annotation in Spring Data,
Hibernate receives the query string and parses it as HQL
(which accepts JPQL as a subset). In practice, most
developers write JPQL-compatible syntax and use
`EntityManager.createQuery()` to stay portable. HQL-only
features (like omitting SELECT, or calling DB functions
with `function()`) are used only when needed.

**Level 5 - Architecture (distinguished engineer):**
HQL has two areas where it beats raw JPQL for production:
(1) `function('db_function', arg)` to call vendor-specific
SQL functions (PostgreSQL's `array_agg`, `json_build_object`,
etc.) without falling back to native SQL queries, keeping
type safety. (2) Tuple result mapping: `SELECT new com.example.dto.ProductView(p.id, p.name, SUM(o.amount)) FROM ...` creates DTO instances directly in HQL via the
constructor expression, avoiding entity materialization
entirely. At scale, this is the preferred read pattern:
no entity lifecycle overhead, no dirty checking, no proxy
creation.

---

### ⚙️ How It Works (Mechanism)

**HQL QUERY PARSING PIPELINE:**

```
1. Query string submitted to HQL parser (ANTLR)
2. Lexer: tokenizes HQL string into tokens
3. Parser: builds Abstract Syntax Tree (AST)
4. Semantic analysis: resolves entity names,
   field names to metadata (column names, types)
5. SQL generation: AST + Dialect -> SQL string
   Example: "FROM Product p WHERE p.price > :min"
   -> "SELECT p.id, p.name, p.price FROM products p
       WHERE p.price > ?"
6. JDBC PreparedStatement with bound parameters
7. ResultSet mapped back to entities via TypeDescriptors

QUERY PLAN CACHE:
- Steps 1-5 are cached in query plan cache (default 2048)
- Subsequent calls with same HQL string skip parsing
- Cache key = HQL string + result type
- Important: NEVER concatenate values into HQL string
  (unique strings bypass cache, cause memory leak)
```

---

### 🔄 The Complete Picture - End-to-End Flow

**COMPLETE HQL USAGE PATTERNS:**

```java
// --- Session API (Hibernate native) ---
Session session = sessionFactory.getCurrentSession();

// 1. Basic query
List<Product> products = session
    .createQuery("FROM Product p WHERE p.active = true",
                 Product.class)
    .getResultList();

// 2. Named parameters (ALWAYS use; never concatenate)
List<Product> byCategory = session
    .createQuery(
        "FROM Product p WHERE p.category.name = :cat",
        Product.class)
    .setParameter("cat", categoryName)
    .getResultList();

// 3. Aggregate query
Long count = session
    .createQuery(
        "SELECT COUNT(p) FROM Product p " +
        "WHERE p.price > :min",
        Long.class)
    .setParameter("min", BigDecimal.valueOf(100))
    .getSingleResult();

// 4. JOIN FETCH (avoid N+1)
List<Order> orders = session
    .createQuery(
        "FROM Order o JOIN FETCH o.items " +
        "WHERE o.status = :s",
        Order.class)
    .setParameter("s", "ACTIVE")
    .getResultList();

// 5. DTO constructor expression
List<ProductDto> dtos = session
    .createQuery(
        "SELECT new com.example.ProductDto(" +
        "p.id, p.name, p.price) FROM Product p " +
        "WHERE p.active = true",
        ProductDto.class)
    .getResultList();

// 6. Bulk UPDATE (bypasses dirty checking)
int updated = session
    .createMutationQuery(
        "UPDATE Product p SET p.price = p.price * 1.1 " +
        "WHERE p.category.name = :cat")
    .setParameter("cat", "Electronics")
    .executeUpdate();
// After bulk update: clear session to avoid stale state
session.clear();
```

---

### 💻 Code Example

**Example 1 - BAD: String concatenation in HQL (injection + cache pollution):**

```java
// BAD: String concatenation
// 1. SQL injection risk (if categoryName comes from input)
// 2. Every unique value creates a new cache entry
//    -> query plan cache fills with unique strings
//    -> memory leak + slower query plan lookup
String hql = "FROM Product p WHERE p.category.name = '"
    + categoryName + "'";
// DO NOT DO THIS

// GOOD: Named parameter
session.createQuery(
    "FROM Product p WHERE p.category.name = :cat",
    Product.class)
.setParameter("cat", categoryName);
// Named parameter: same HQL string every time
// -> cache hit; parameter bound at JDBC level
```

**Example 2 - Vendor function call in HQL:**

```java
// Call PostgreSQL date_trunc without native SQL:
List<Object[]> results = session
    .createQuery(
        "SELECT function('date_trunc', 'month', " +
        "o.createdAt), COUNT(o) " +
        "FROM Order o " +
        "GROUP BY function('date_trunc', 'month', " +
        "o.createdAt)",
        Object[].class)
    .getResultList();
// Stays in HQL world; entity field names; type-safe
// SQL generated: date_trunc('month', o.created_at)
```

**Example 3 - ELEMENTS and INDICES for collections:**

```java
// HQL-specific: query ELEMENTS of a collection
// (not available in JPQL)
List<Tag> popularTags = session
    .createQuery(
        "SELECT ELEMENTS(p.tags) FROM Product p " +
        "WHERE p.category.name = :cat",
        Tag.class)
    .setParameter("cat", "Electronics")
    .getResultList();
// Extracts collection elements directly
```

---

### ⚖️ Comparison Table

| Feature                   | HQL                           | JPQL                    | Native SQL              |
| ------------------------- | ----------------------------- | ----------------------- | ----------------------- |
| SELECT clause             | Optional (Hibernate fills in) | Required                | Required                |
| Entity/field names        | Yes                           | Yes                     | No (table/column names) |
| Polymorphic queries       | Yes                           | Yes                     | No (manual DTYPE)       |
| DB vendor functions       | `function()`                  | `function()` (JPA 2.1+) | Native syntax           |
| Portability               | Hibernate only                | All JPA providers       | DB-specific             |
| `ELEMENTS()`, `INDICES()` | Yes                           | No                      | N/A                     |
| Bulk DML                  | `createMutationQuery()`       | `createQuery()`         | Yes                     |

---

### ⚠️ Common Misconceptions

| Misconception                                    | Reality                                                                                                                                                                                                      |
| ------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| "HQL and JPQL are the same thing"                | JPQL is the JPA standard and a subset of HQL. HQL has Hibernate-specific extensions (optional SELECT, ELEMENTS(), INDICES(), more functions). All JPQL is valid HQL but not vice versa.                      |
| "HQL queries table names"                        | HQL queries entity class names and their Java field names. `FROM Product` queries the Java class `Product`, not the table `product`. The class-to-table mapping is in `@Entity`/`@Table`.                    |
| "Omitting SELECT in HQL is fine in all contexts" | Omitting SELECT is valid in Hibernate's HQL but NOT in standard JPQL. If you switch JPA providers from Hibernate to EclipseLink, queries without SELECT will fail. Write `SELECT p FROM...` for portability. |
| "HQL is safe from SQL injection by default"      | HQL is safe IF you use named or positional parameters. HQL built by string concatenation is vulnerable to HQL injection (analogous to SQL injection). Always use `.setParameter()`.                          |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Query Plan Cache Memory Leak**

**Symptom:** Application memory grows over time.
`OutOfMemoryError` after hours/days of production load.
Heap dump shows thousands of `QueryKey` objects and
unique query string instances in memory.
**Root Cause:** HQL queries built with string concatenation:
`"FROM Product WHERE price > " + value`. Each unique
`value` creates a unique HQL string -> a new cache entry.
With thousands of unique prices, thousands of entries
fill the query plan cache.
**Diagnosis:**

```java
// Hibernate statistic: query plan cache misses
Statistics stats = sessionFactory.getStatistics();
stats.getQueryPlanCacheMissCount();
// High miss count with large query count = cache thrashing
```

**Fix:** Always use named parameters. Never concatenate
values into HQL strings. Query plan cache size is
configurable: `hibernate.query.plan_cache_max_size=4096`.

---

**Failure Mode 2: Case-Sensitive Entity Name Error**

**Symptom:**
`org.hibernate.hql.internal.ast.QuerySyntaxException:
product is not mapped [FROM product p]`
**Root Cause:** HQL entity names are case-sensitive
(Java class names). `product` (lowercase) is not the
class name; `Product` (capitalized) is.
**Fix:** Always use the exact Java class name: `FROM Product p`.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[JPH-014 - JPQL]] - JPQL is the portable foundation;
  understand it before HQL extensions
- [[JPH-011 - EntityManager]] - HQL is used through
  EntityManager (or Hibernate Session)

**Builds On This (learn these next):**

- [[JPH-029 - @NamedQuery and Native Queries]] - named
  queries pre-compile HQL/JPQL at startup
- [[JPH-031 - Hibernate Session vs EntityManager]] -
  HQL is the native query language for Hibernate Session

**Related:**

- [[JPH-036 - Criteria API]] - type-safe programmatic
  alternative to HQL strings
- [[JPH-053 - QueryDSL with JPA]] - fluent DSL that
  generates HQL/JPQL at runtime

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ BASIC        │ FROM Product p WHERE p.price > :min      │
│              │ (entity name, field name, named param)    │
├──────────────┼───────────────────────────────────────────┤
│ HQL vs JPQL  │ HQL: superset; SELECT optional           │
│              │ JPQL: standard; SELECT required           │
├──────────────┼───────────────────────────────────────────┤
│ DTO          │ SELECT new com.pkg.Dto(p.id, p.name)     │
│ PROJECTION   │ FROM Product p WHERE ...                  │
├──────────────┼───────────────────────────────────────────┤
│ BULK UPDATE  │ UPDATE Product SET price=price*1.1       │
│              │ WHERE ... ; then session.clear()          │
├──────────────┼───────────────────────────────────────────┤
│ NEVER        │ Concatenate values into HQL strings      │
│              │ -> cache pollution + HQL injection        │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "HQL = Hibernate's object-oriented query │
│              │ language; uses Java class/field names;    │
│              │ superset of standard JPQL."              │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. HQL uses Java entity class names and field names
   (case-sensitive), not SQL table/column names
2. HQL is a Hibernate-specific superset of JPQL;
   SELECT clause is optional in HQL but required in JPQL
3. Always use named parameters (`:param`) - never build
   HQL by string concatenation (injection + cache pollution)

**Interview one-liner:** HQL is Hibernate's native query
language that references Java class and field names instead
of table/column names. It's a superset of JPA's JPQL with
Hibernate-specific extensions. Hibernate translates HQL
to SQL using the configured dialect. Always use named
parameters - string concatenation causes query plan cache
pollution and HQL injection.

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Object-oriented query
languages (HQL, JPQL, LINQ, SOQL) share a universal
principle: query the domain model, not the storage model.
When storage changes (column rename, table split, sharding),
the query remains valid as long as the domain model
mapping is updated. This separation of concerns (query
vs storage) is why ORMs exist. The same principle applies
in NoSQL (MongoDB's query language references document
field names, not underlying storage format), GraphQL
(queries against the schema type, not the resolver
implementation), and Elasticsearch (queries against the
document structure, not the Lucene index internals).

**Where else this pattern appears:**

- **LINQ (C#/.NET)** - query C# objects/Entity Framework
  models using C# property names; EF generates SQL
- **SOQL (Salesforce)** - queries Salesforce object model
  (Opportunity.Name) not underlying Oracle columns
- **MongoDB query language** - queries document fields;
  index selection and storage layout are transparent
- **GraphQL** - query the schema type hierarchy;
  resolvers handle actual data fetching strategy

---

### 💡 The Surprising Truth

HQL (and JPQL) bulk `UPDATE` and `DELETE` statements
bypass the Hibernate session entirely. When you run
`UPDATE Product SET price = price * 1.1 WHERE ...`,
Hibernate executes the SQL directly without loading
entities into the persistence context. This is intentional
(it's the performance advantage of bulk operations).
But the consequence: the in-memory persistence context
(first-level cache) now holds stale entity snapshots.
If your code later accesses `product.getPrice()` on
a previously loaded entity in the same session, it reads
the OLD price from the cache - not the updated price from
the database. The fix is mandatory: call `session.clear()`
(or `em.clear()`) after any bulk DML statement to evict
all stale entities from the first-level cache.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **WRITE** an HQL query with JOIN FETCH, named parameters,
   and DTO constructor expression
2. **EXPLAIN** why HQL queries use entity class names
   and the consequence of case sensitivity
3. **DISTINGUISH** HQL-only features from JPQL standard
   features, and choose the appropriate query type
4. **DIAGNOSE** query plan cache pollution from string
   concatenation and explain why named parameters prevent it
5. **EXECUTE** a bulk UPDATE in HQL and explain why
   `session.clear()` is required afterward

---

### 🎯 Interview Deep-Dive

**Q1: What is the difference between HQL and JPQL?
When would you choose HQL over JPQL?**
_Why they ask:_ Tests understanding of Hibernate vs JPA
layers and when to use each.
_Strong answer includes:_

- JPQL: JPA standard; portable across providers
  (Hibernate, EclipseLink, OpenJPA)
- HQL: Hibernate's superset; adds SELECT-optional syntax,
  ELEMENTS(), INDICES(), additional DB functions
- Most applications should write JPQL for portability;
  HQL extensions for specific features
- In Spring Data `@Query`: values are parsed by Hibernate
  as HQL (so JPQL syntax is fully supported)
- Choose HQL explicitly: when using Hibernate Session
  API directly; when needing HQL-only features

**Q2: Why is string concatenation in HQL queries
dangerous, and what are the consequences beyond
security?**
_Why they ask:_ Tests both security awareness and
Hibernate internals knowledge.
_Strong answer includes:_

- Security: HQL injection (same concept as SQL injection
  but for the ORM query layer; can traverse entity
  relationships to extract data)
- Performance: unique HQL strings each create a new query
  plan cache entry; high rate of unique queries causes
  cache thrashing -> frequent parse overhead + memory
  growth
- Monitoring: each unique query string appears as a
  distinct query in APM tools, hiding the true hot queries
- Fix: always use `.setParameter("name", value)`;
  Hibernate binds the value at JDBC level, outside the
  query string; same HQL string every time = cache hit
