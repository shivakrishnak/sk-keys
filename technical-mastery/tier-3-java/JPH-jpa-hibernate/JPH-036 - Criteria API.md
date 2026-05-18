---
id: JPH-036
title: Criteria API
category: JPA & Hibernate
tier: tier-3-java
folder: JPH-jpa-hibernate
difficulty: ★★★
depends_on: JPH-006, JPH-007, JPH-008, JPH-011, JPH-014, JPH-025
used_by: JPH-043, JPH-053, JPH-054, JPH-056
related: JPH-028, JPH-030, JPH-053
tags:
  - java
  - jpa
  - database
  - advanced
status: complete
version: 4
layout: default
parent: "JPA & Hibernate"
grand_parent: "Technical Mastery"
nav_order: 36
permalink: /technical-mastery/jpa-hibernate/criteria-api/
---

⚡ **TL;DR** - The JPA Criteria API builds JPQL queries
programmatically using Java objects instead of string
concatenation. Type-safe (catch field name typos at
compile time via JPA metamodel), but verbose. Best for
dynamic queries where WHERE clauses are assembled based
on runtime conditions. For static queries: `@Query` is
cleaner. For dynamic queries: Criteria API or Querydsl
(JPH-053). Never concatenate strings to build JPQL.

| #036            | Category: JPA & Hibernate                                                                 | Difficulty: ★★★ |
| :-------------- | :---------------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | @Entity, @Id/@GeneratedValue, @Table/@Column, EntityManager, JPQL, Pagination             |                 |
| **Used by:**    | Spring Data Specifications, QueryDSL with JPA, JPA at Scale, Spring Data JPA Architecture |                 |
| **Related:**    | HQL, DTO Projections, QueryDSL                                                            |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A product search endpoint has 10 optional filters:
name, category, min price, max price, status, tags,
rating, featured, in-stock, created-after. A naive
developer builds the query with string concatenation:

```java
String jpql = "FROM Product p WHERE 1=1";
if (name != null)     jpql += " AND p.name LIKE :name";
if (category != null) jpql += " AND p.category=:cat";
// ... 8 more conditions
```

This is fragile (typos not caught until runtime), opens
HQL injection if parameters sneak into the string,
and makes the query plan cache useless (unique strings
per combination). With 10 optional filters, there are
1,024 possible query strings - 1,024 unique cache entries.

**THE CRITERIA API SOLUTION:**

```java
CriteriaBuilder cb = em.getCriteriaBuilder();
CriteriaQuery<Product> cq = cb.createQuery(Product.class);
Root<Product> p = cq.from(Product.class);
List<Predicate> predicates = new ArrayList<>();
if (name != null) predicates.add(
    cb.like(p.get("name"), "%" + name + "%"));
// ...
cq.where(predicates.toArray(new Predicate[0]));
```

Predicates are Java objects. No string concatenation.
Query plan cache key is the generated SQL structure.

---

### 📘 Textbook Definition

**JPA Criteria API** is a programmatic, type-safe API
for building JPA queries using Java objects (no string
JPQL). Defined in `jakarta.persistence.criteria` package.
Core classes:

- `CriteriaBuilder` - factory for predicates, expressions, query objects
- `CriteriaQuery<T>` - the query being built; specifies return type
- `Root<T>` - the FROM clause entity; field access via `root.get("fieldName")`
- `Predicate` - a boolean condition (WHERE clause element)
- `Expression<T>` - a typed expression (field, function result, literal)
- `Path<T>` - navigates entity fields: `root.get("category").get("name")`

**JPA Metamodel** (static type-safe Criteria):
Generated classes (via `hibernate-jpamodelgen`) provide
compile-time field references: `Product_.price` instead
of `"price"`. Field renames are caught at compile time.

---

### ⏱️ Understand It in 30 Seconds

**One line:** The Criteria API builds JPQL queries
using Java objects instead of string concatenation -
type-safe, dynamic, but verbose.

**One analogy:**

> Writing JPQL by hand is like writing a letter in a
> foreign language from memory - a typo may not be
> noticed until someone reads it (runtime). The Criteria
> API is like using a grammar checker and spell-check -
> Java's type system catches field name typos and type
> mismatches at compile time. The letter takes longer
> to write but arrives correct.

**One insight:** The Criteria API is primarily valuable
for DYNAMIC queries where the WHERE clause is assembled
at runtime. For static queries, `@Query("SELECT ...")` is
far more readable. Use Criteria (or Querydsl/Specifications)
only when you need to build different predicates based
on runtime conditions.

---

### 🔩 First Principles Explanation

**CRITERIA API VS JPQL:**

```
JPQL: static string, runtime-validated
  "SELECT p FROM Product p WHERE p.price > :min
   AND p.category.name = :cat"
  -> Validated at startup (if @NamedQuery or @Query)
  -> NOT validated if created with createQuery() inline

Criteria API: Java objects, compile-time type-checkable
  CriteriaBuilder cb = em.getCriteriaBuilder();
  CriteriaQuery<Product> cq =
    cb.createQuery(Product.class);
  Root<Product> p = cq.from(Product.class);
  cq.select(p)
    .where(cb.and(
        cb.gt(p.get(Product_.price), minPrice),
        cb.equal(p.get(Product_.category)
                   .get(Category_.name), catName)));
  -> Typo in "price" = compile error (with metamodel)
  -> Type mismatch (comparing price to String) = compile
    error
```

**METAMODEL CLASSES:**

```java
// Generated by hibernate-jpamodelgen annotation processor:
@Generated(value =
    "org.hibernate.jpamodelgen.JPAMetaModelEntityProcessor")
@StaticMetamodel(Product.class)
public abstract class Product_ {
    public static volatile SingularAttribute<Product, Long> id;
    public static volatile SingularAttribute<Product, String> name;
    public static volatile SingularAttribute<Product,
        BigDecimal> price;
    public static volatile SingularAttribute<Product, Boolean> active;
    public static volatile ManyToOneAttribute<Product,
        Category> category;
    // ... one field per entity field
}

// Usage (compile-time safe):
p.get(Product_.name)
// returns Path<String>; compile error if "name" renamed
p.get(Product_.price)    // returns Path<BigDecimal>
cb.gt(p.get(Product_.price), 100)
// type-safe: price is BigDecimal; 100 is Number
cb.like(p.get(Product_.name), "%") // type-safe: name is String
```

---

### 🧪 Thought Experiment

**STRING CRITERIA (BAD) VS CRITERIA API (GOOD):**

```java
// Renaming entity field from "price" to "unitPrice"

// String-based JPQL (string reference - won't fail until runtime):
em.createQuery("FROM Product p WHERE p.price > :min")
  .setParameter("min", 100)
  .getResultList();
// After rename: RuntimeException on first execution
// QueryException: could not resolve property: price

// Criteria API with metamodel (fails at compile time):
p.get(Product_.price)
// After rename:
// 1. Entity field renamed: Product.price -> Product.unitPrice
// 2. Metamodel regenerated: Product_.price -> Product_.unitPrice
// 3. All usages of Product_.price: compile error
//    -> refactoring tool (IDE) can rename all references
//    -> Cannot be deployed if compile fails
// FAIL FAST: caught before test, before deployment
```

---

### 🧠 Mental Model / Analogy

> Writing JPQL is like writing SQL as a string in any
> language - it works, but "SELECT \* FROM productz" won't
> fail until runtime. The Criteria API with the JPA
> metamodel is like using an ORM query builder with
> model classes - `Product.where(price: gt(100))` - where
> accessing `Product.pricee` is a compile error. The
> tradeoff: fluency vs safety. Querydsl (JPH-053) gives
> you both by generating even cleaner syntax.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
The Criteria API builds database queries using Java method
calls and objects, instead of writing SQL/JPQL strings.
Field names are Java class fields, not strings, so typos
are caught by the compiler.

**Level 2 - How to use it (junior developer):**
Get a `CriteriaBuilder` from `em.getCriteriaBuilder()`.
Create a `CriteriaQuery`. Create a `Root` for the entity.
Build predicates using `cb.equal()`, `cb.like()`, `cb.gt()`.
Combine with `cb.and()` / `cb.or()`. Execute via
`em.createQuery(criteriaQuery).getResultList()`.

**Level 3 - How it works (mid-level engineer):**
The Criteria API builds an AST (Abstract Syntax Tree)
of the query in Java objects. When `createQuery(cq)` is
called, Hibernate translates the AST into a JPQL/HQL
string, which is then parsed through the normal query
execution pipeline. The generated HQL is then compiled
to SQL via the dialect.

**Level 4 - Metamodel and Spring Data Specifications (senior):**
Generate `Product_` metamodel classes with `hibernate-jpamodelgen`
(or Spring Data JPA auto-generates them). Spring Data's
`Specification<T>` interface wraps a `CriteriaQuery` predicate
as a reusable, composable object: `spec1.and(spec2)`.
`JpaSpecificationExecutor<T>` in a repository provides
`findAll(Specification<T> spec, Pageable pageable)`.
This is the idiomatic way to use the Criteria API in Spring.

**Level 5 - When NOT to use it (distinguished engineer):**
The Criteria API is verbose (5-10x more code than JPQL
for the same query), difficult to read and review,
and produces generated SQL that is harder to understand
in query logs. For static queries: use `@Query`. For
dynamic queries: use `Specification<T>` (Spring Data wrapper)
or Querydsl (generates cleaner syntax from metamodel).
The Criteria API directly is only appropriate when writing
framework-level query builders or when Querydsl is not
available. At scale, teams using raw Criteria API have
harder-to-review PRs and more maintenance burden than
teams using Querydsl or Specifications.

---

### ⚙️ How It Works (Mechanism)

**CRITERIA API QUERY CONSTRUCTION PIPELINE:**

```
1. CriteriaQuery AST built in Java objects:
   CriteriaQuery<Product>
     -> Root<Product> (FROM product)
     -> List<Predicate> (WHERE conditions)
     -> Order (ORDER BY)

2. em.createQuery(criteriaQuery):
   -> Hibernate traverses AST
   -> Generates HQL string:
      "SELECT p FROM Product p WHERE
       p.price > :param1 AND p.category.name = :param2
       ORDER BY p.name ASC"
   -> Compiles HQL to SQL via dialect

3. Parameters bound and query executed
```

**SUBQUERY EXAMPLE:**

```java
CriteriaBuilder cb = em.getCriteriaBuilder();
CriteriaQuery<Product> cq = cb.createQuery(Product.class);
Root<Product> p = cq.from(Product.class);

// Subquery: find products with avg rating > 4.0
Subquery<Double> ratingSubquery = cq.subquery(Double.class);
Root<Review> r = ratingSubquery.from(Review.class);
ratingSubquery.select(cb.avg(r.get(Review_.rating)))
    .where(cb.equal(
        r.get(Review_.product), p));

cq.select(p)
  .where(cb.gt(ratingSubquery, 4.0));

List<Product> topRated = em.createQuery(cq)
    .getResultList();
// SQL: SELECT p.* FROM products p
//      WHERE (SELECT AVG(r.rating) FROM reviews r
//             WHERE r.product_id = p.id) > 4.0
```

---

### 🔄 The Complete Picture - End-to-End Flow

**DYNAMIC SEARCH WITH CRITERIA API (FULL EXAMPLE):**

```java
@Repository
public class ProductSearchRepository {

    @PersistenceContext
    private EntityManager em;

    public List<Product> search(ProductSearchCriteria c) {
        CriteriaBuilder cb = em.getCriteriaBuilder();
        CriteriaQuery<Product> cq = cb.createQuery(
            Product.class);
        Root<Product> p = cq.from(Product.class);

        List<Predicate> predicates = new ArrayList<>();

        if (c.getName() != null) {
            predicates.add(cb.like(
                cb.lower(p.get(Product_.name)),
                "%" + c.getName().toLowerCase() + "%"));
        }
        if (c.getMinPrice() != null) {
            predicates.add(cb.ge(
                p.get(Product_.price), c.getMinPrice()));
        }
        if (c.getMaxPrice() != null) {
            predicates.add(cb.le(
                p.get(Product_.price), c.getMaxPrice()));
        }
        if (c.getCategoryId() != null) {
            predicates.add(cb.equal(
                p.get(Product_.category).get(Category_.id),
                c.getCategoryId()));
        }
        if (c.getActive() != null) {
            predicates.add(cb.equal(
                p.get(Product_.active), c.getActive()));
        }

        cq.select(p)
          .where(cb.and(predicates.toArray(
              new Predicate[0])))
          .orderBy(cb.asc(p.get(Product_.name)));

        return em.createQuery(cq)
            .setFirstResult(c.getOffset())
            .setMaxResults(c.getLimit())
            .getResultList();
    }
}
```

---

### 💻 Code Example

**Example 1 - BAD: string concatenation for dynamic query:**

```java
// BAD: JPQL injection risk + query plan cache pollution
public List<Product> search(String name, BigDecimal min) {
    String jpql = "FROM Product p WHERE 1=1";
    if (name != null) jpql += " AND p.name LIKE '%" +
        name + "%'";  // HQL injection if name has quotes!
    if (min != null)  jpql += " AND p.price > " + min;
    // 1,024 unique strings for 10 optional filters
    // -> query plan cache full of unique entries
    return em.createQuery(jpql, Product.class)
        .getResultList();
}

// GOOD: Criteria API with named parameters
// (see Dynamic Search example above)
```

**Example 2 - BETTER: Spring Data Specification:**

```java
// Much cleaner than raw Criteria API:
public class ProductSpecs {
    public static Specification<Product> hasName(String n) {
        return (root, query, cb) ->
            n == null ? null :
            cb.like(cb.lower(root.get(Product_.name)),
                    "%" + n.toLowerCase() + "%");
    }

    public static Specification<Product> minPrice(
            BigDecimal min) {
        return (root, query, cb) ->
            min == null ? null :
            cb.ge(root.get(Product_.price), min);
    }
}

// Service: compose specifications
Specification<Product> spec =
    where(hasName(name)).and(minPrice(minPrice));
Page<Product> results = productRepo.findAll(
    spec, pageable);
// Still uses Criteria API internally; but readable code
```

---

### ⚖️ Comparison Table

| Approach                  | Type-safe             | Dynamic? | Verbosity | Readability | Best for                              |
| ------------------------- | --------------------- | -------- | --------- | ----------- | ------------------------------------- |
| JPQL `@Query`             | No                    | No       | Low       | High        | Static queries                        |
| Criteria API              | Yes (with metamodel)  | Yes      | High      | Low         | Dynamic queries (framework code)      |
| Spring Data Specification | Yes (with metamodel)  | Yes      | Medium    | Medium      | Dynamic search in Spring Boot         |
| QueryDSL                  | Yes (generated types) | Yes      | Low       | High        | Dynamic queries with high readability |

---

### ⚠️ Common Misconceptions

| Misconception                                                      | Reality                                                                                                                                                                                                                             |
| ------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Criteria API is type-safe without the JPA metamodel"              | Without metamodel, field access is `root.get("price")` (string) - no compile-time safety. Metamodel generates `Product_.price` (typed). Without metamodel, the advantage over JPQL strings is minimal.                              |
| "Criteria API is necessary for all dynamic queries in Spring Data" | Spring Data `Specification<T>` (a wrapper around Criteria API predicates) is the idiomatic approach. Even cleaner: Querydsl with `QuerydslPredicateExecutor`. Raw Criteria API is rarely used directly in Spring Boot applications. |
| "CriteriaQuery executes immediately on creation"                   | `CriteriaQuery` is just a builder. Query execution happens when `em.createQuery(cq).getResultList()` is called. The query is translated and compiled at execution time.                                                             |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode: Type Mismatch at Query Execution**

**Symptom:** `java.lang.IllegalArgumentException: Parameter value
[java.lang.String] did not match expected type [java.math.BigDecimal]`
at runtime despite using the Criteria API.

**Root Cause:** Using string-based field access `root.get("price")`
(not metamodel). No compile-time type checking.
`cb.gt(root.get("price"), "100")` compiles but fails at runtime
because price is `BigDecimal`, not `String`.

**Fix:** Generate and use JPA metamodel (`Product_.price`).
The compiler enforces: `cb.gt(p.get(Product_.price), BigDecimal.valueOf(100))`.

---

**Failure Mode: Query Plan Cache Pollution (Literal in Criteria)**

**Symptom:** Query plan cache fills up. Heap grows.

**Root Cause:** Using literals in Criteria predicates
instead of parameters: `cb.equal(p.get(Product_.name), "Laptop")`.
Hibernate embeds the literal in the generated JPQL string,
creating unique strings per value.

**Fix:** Use `cb.parameter(String.class, "name")` to create
named parameters, or ensure Criteria predicates use bound
variables (via `cb.literal()` vs bound parameters).

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[JPH-014 - JPQL]] - Criteria API generates JPQL; understand
  JPQL semantics first
- [[JPH-011 - EntityManager]] - Criteria API uses the
  EntityManager for query execution

**Builds On This (learn these next):**

- [[JPH-043 - Spring Data Specifications]] - Spring Data's
  abstraction over Criteria API predicates
- [[JPH-053 - QueryDSL with JPA]] - modern, more readable
  alternative to raw Criteria API

**Related:**

- [[JPH-030 - DTO Projections]] - Criteria API supports
  tuple and constructor result projections
- [[JPH-025 - Pagination and Sorting]] - Criteria queries
  accept `setFirstResult`/`setMaxResults` for pagination

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ BUILDER      │ CriteriaBuilder cb = em.getCriteriaBuilde│
│ QUERY        │ CriteriaQuery<T> cq = cb.createQuery(T)  │
│ ROOT         │ Root<T> p = cq.from(T.class)             │
│ PREDICATE    │ cb.equal(), cb.like(), cb.gt(), cb.and() │
│ EXECUTE      │ em.createQuery(cq).getResultList()       │
├──────────────┼──────────────────────────────────────────┤
│ METAMODEL    │ Add hibernate-jpamodelgen to build       │
│              │ Product_.price = compile-safe field ref  │
├──────────────┼──────────────────────────────────────────┤
│ DYNAMIC      │ Build List<Predicate> conditionally      │
│              │ cq.where(cb.and(predicates.toArray(...)))│
├──────────────┼──────────────────────────────────────────┤
│ SPRING DATA  │ Use Specification<T> instead of raw API  │
│              │ Cleaner; composable with .and()/.or()    │
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "Criteria API = type-safe programmatic   │
│              │ JPQL builder. Verbose but compile-safe.  │
│              │ Use Specifications or QueryDSL in Spring.│
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Criteria API builds JPQL dynamically using Java objects
   instead of string concatenation - compile-time safety
   requires the JPA metamodel (`Product_.price`)
2. Use for DYNAMIC queries; `@Query` is better for static;
   Querydsl is better for readable dynamic queries
3. In Spring Boot, `Specification<T>` wraps Criteria API
   predicates into reusable, composable objects -
   use that instead of raw Criteria API

**Interview one-liner:** The JPA Criteria API builds JPQL
queries programmatically using Java objects. With the JPA
metamodel (`Product_.price`), field names are compile-time
type-safe - renaming a field causes a compile error, not
a runtime exception. Best for dynamic queries; verbose for
static ones. In Spring Data, `Specification<T>` provides
a cleaner wrapper over Criteria API predicates with
`findAll(spec, pageable)`.

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** For dynamic queries
with conditional predicates, use a builder/AST approach,
never string concatenation. String concatenation of SQL/
query languages creates: injection vulnerabilities, query
plan cache pollution, runtime-only error detection, and
maintenance nightmares. This principle applies universally:
SQL (use PreparedStatement/QueryBuilder), Elasticsearch
(use query DSL objects), MongoDB (use query objects, not
string pipelines), Cypher for Neo4j (use parameterized
queries). Every query language has a programmatic builder
pattern for dynamic query construction; prefer it over
string manipulation.

**Where else this pattern appears:**

- **JOOQ** - SQL type-safe builder; same concept as
  Criteria API but for SQL directly (not JPQL)
- **Querydsl** - cleaner alternative to JPA Criteria API;
  generates Q-type classes from entities
- **Elasticsearch QueryBuilders** - programmatic ES query
  builder; no string concatenation
- **LINQ (C#)** - type-safe query building integrated
  into the C# language syntax

---

### 💡 The Surprising Truth

The JPA Criteria API was added in JPA 2.0 (2009) partly
as a compile-time-safe alternative to JPQL strings.
However, the JPA metamodel generator tooling is complex
enough that many teams skip it - and without the metamodel,
Criteria API uses string-based `root.get("price")`
which offers NO type safety over JPQL strings. The net
result: teams use verbose Criteria API code with string
field references and get the worst of both worlds:
maximum verbosity with no safety advantage. The actual
safety benefit of Criteria API requires properly configured
`hibernate-jpamodelgen` annotation processing in the
build, and consistent use of `Entity_.field` syntax.
Without this setup, Querydsl (which generates its own
type-safe query classes) is more practical.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **BUILD** a dynamic 5-condition Criteria API query
   using the JPA metamodel for type-safe field references
2. **CONFIGURE** `hibernate-jpamodelgen` to generate
   `Product_` metamodel classes in the build
3. **REFACTOR** a string-concatenation dynamic query to
   use Criteria API predicates
4. **WRITE** a Spring Data `Specification<T>` for a given
   business rule and combine two specifications with `.and()`
5. **EXPLAIN** when Criteria API is the right choice vs
   `@Query` vs `Specification` vs Querydsl

---

### 🎯 Interview Deep-Dive

**Q1: What is the JPA Criteria API and when would you
use it over JPQL @Query?**
_Why they ask:_ Tests knowledge of dynamic query building.
_Strong answer includes:_

- Criteria API: programmatic query builder using Java
  objects; with JPA metamodel - compile-time field safety
- Use over @Query when: WHERE clause conditions are
  determined at runtime (optional filters, search APIs);
  string concatenation would otherwise be needed
- @Query preferred for: static, known-at-write-time queries
  (cleaner, more readable, startup-validated)
- Spring Data Specification is the recommended Criteria API
  wrapper for Spring Boot applications

**Q2: What is the JPA Metamodel and how does it make
the Criteria API type-safe?**
_Why they ask:_ Tests depth of Criteria API knowledge.
_Strong answer includes:_

- JPA Metamodel: generated classes (`Product_`) with
  static fields for each entity field, typed with
  JPA attribute types (`SingularAttribute<Product, BigDecimal>`)
- Generation: via `hibernate-jpamodelgen` annotation
  processor in Maven/Gradle build
- Type safety: `p.get(Product_.price)` returns `Path<BigDecimal>`;
  `cb.gt(p.get(Product_.price), "100")` is a compile error
  (type mismatch: String vs BigDecimal)
- Without metamodel: `p.get("price")` returns `Path<Object>`;
  no compile-time safety; equivalent to JPQL string
