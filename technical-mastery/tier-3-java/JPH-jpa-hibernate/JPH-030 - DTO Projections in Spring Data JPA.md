---
id: JPH-030
title: DTO Projections in Spring Data JPA
category: JPA & Hibernate
tier: tier-3-java
folder: JPH-jpa-hibernate
difficulty: ★★☆
depends_on: JPH-014, JPH-016, JPH-023, JPH-025, JPH-027, JPH-029
used_by: JPH-037, JPH-043, JPH-054, JPH-056
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
grand_parent: "Technical Mastery"
nav_order: 30
permalink: /technical-mastery/jpa-hibernate/dto-projections/
---

⚡ **TL;DR** - DTO projections load only the specific
columns needed, avoiding full entity materialization.
Spring Data supports three projection types: Interface
projections (auto-mapped), Class projections (constructor
expression JPQL), and Dynamic projections (type decided
at call time). Use projections on all read-only query
methods: they eliminate dirty checking overhead, prevent
accidental entity modification, load fewer columns, and
are the cleanest fix for N+1 on read endpoints.

| #030            | Category: JPA & Hibernate                                                                       | Difficulty: ★★☆ |
| :-------------- | :---------------------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | JPQL, CrudRepository/JpaRepository, @Query, Pagination, N+1 Problem, @NamedQuery/Native Queries |                 |
| **Used by:**    | EntityGraph, Spring Data Specifications, JPA at Scale, Spring Data JPA Architecture             |                 |
| **Related:**    | Criteria API, QueryDSL with JPA                                                                 |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A product listing API returns a list of products. The
`Product` entity has 40 fields including large text
descriptions, binary image data, audit fields, and 5
lazy associations. The API only needs `id`, `name`, and
`price`. Using `findAll()` loads all 40 fields for every
product from the database, creates 40-field entity objects
in Java heap, and serializes only 3 fields to JSON.
37 fields are loaded, held in memory, and then discarded.

**THE COST AT SCALE:**
100 products x 40 fields = 4,000 column values loaded.
100 products x 3 fields actually needed = 300.
Memory waste: 13x. Additional DB network IO: proportional
to all unused columns. Dirty checking overhead: Hibernate
snapshots all 40 fields per entity. Garbage collection
pressure: large unused object graphs.

**THE SOLUTION:**
`SELECT new com.example.ProductSummary(p.id, p.name, p.price) FROM Product p`
loads exactly 3 fields, creates lightweight DTO objects,
no dirty checking, no proxy creation, no entity lifecycle
overhead. For read-only endpoints: projections are always
the correct choice.

---

### 📘 Textbook Definition

**DTO Projection** in Spring Data JPA refers to returning
a subset of entity fields (or computed values) mapped to
a non-entity class or interface, instead of loading full
managed entity objects.

**Three projection types in Spring Data:**

1. **Interface Projection** - an interface with getter
   methods matching field names; Spring Data creates a
   proxy at runtime that delegates field access to the
   underlying query result. Supports `@Value` SpEL
   expressions for computed fields.

2. **Class Projection (DTO Projection)** - a class with
   a matching constructor. Spring Data uses the constructor
   expression in JPQL: `SELECT new com.example.Dto(...)`.
   No Spring proxy; plain Java objects.

3. **Dynamic Projection** - repository method returns
   `<T>` with the projection type passed as a `Class<T>`
   parameter at call time. Same method can return either
   the full entity or any projection type.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Projections load only the columns you need
into lightweight DTOs instead of full managed entities.

**One analogy:**

> Loading a full entity is like ordering a complete
> restaurant meal when you only want the appetizer.
> A DTO projection is the a-la-carte order: only what
> you actually need arrives at the table (loaded from
> the database), and nothing is wasted.

**One insight:** Interface projections are convenient but
use a Spring-generated proxy under the hood - each field
access goes through the proxy. For complex mappings or
high-performance scenarios, class projections (plain
Java classes with constructors) are faster and more
explicit, with zero proxy overhead.

---

### 🔩 First Principles Explanation

**WHY PROJECTIONS ARE FASTER THAN ENTITY LOADING:**

```
Full Entity loading:
  1. SQL: SELECT * FROM products (all 40 columns)
  2. For each row:
     a. Allocate Product entity object
     b. Snapshot all 40 fields for dirty checking
     c. Create proxy for each lazy association
     d. Register entity in persistence context (1L cache)
  3. Cost: 40 columns * N rows loaded + snapshot arrays
           + proxy objects + 1L cache Map entries

Class Projection loading:
  1. SQL: SELECT id, name, price FROM products (3 columns)
  2. For each row:
     a. Call new ProductSummary(id, name, price)
  3. NO dirty checking snapshots
  4. NO proxies for associations
  5. NOT registered in persistence context
  6. Cost: 3 columns * N rows + simple constructors
```

**WHEN INTERFACE PROJECTION IS SUFFICIENT:**

```java
// Simple interface: Spring auto-maps by getter name
interface ProductSummary {
    Long getId();
    String getName();
    BigDecimal getPrice();
}

// Spring Data generates SQL: SELECT id, name, price
// Spring auto-creates a proxy:
// ProductSummary = JDK Proxy -> routes getName() to
//   the column value from the result set
// No entity object; no dirty checking
// BUT: proxy object per result row
```

---

### 🧪 Thought Experiment

**INTERFACE PROJECTION CLOSED vs OPEN:**

```java
// CLOSED projection: all fields from the interface
// come from entity fields (no SpEL)
interface ProductView {
    Long getId();
    String getName();
    // SQL: SELECT p.id, p.name FROM products p
    // Spring knows exactly which columns to fetch
}

// OPEN projection: uses SpEL expressions
interface ProductView {
    @Value("#{target.name + ' (' + target.price + ')'}")
    String getDisplayName();
    // Problem: Spring CANNOT determine which columns
    // to include from SpEL expression
    // -> loads the FULL entity (all columns)
    // -> performance benefit of projection is LOST
}
```

**KEY INSIGHT:** Open projections with `@Value` SpEL
defeat the purpose of projections for performance.
The underlying entity must be loaded to evaluate SpEL
expressions. For computed fields that require SpEL:
use a class projection and compute the value in the
constructor, or compute it in the service layer after
loading the closed projection.

---

### 🧠 Mental Model / Analogy

> An entity is a live bank account object: it knows its
> current balance, has history, can be modified, and
> changes are tracked. A DTO projection is a bank
> statement snapshot: it shows the data you requested
> (balance, last 3 transactions), is immutable, and has
> no connection to the live account after creation.
>
> For reading data (display, reporting), you need a
> statement (DTO). For modifying data, you need the live
> account (entity). Spring Data gives you both depending
> on what the method returns.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Instead of loading all fields of an entity, a projection
loads only the specific fields the caller needs. This
is faster and uses less memory.

**Level 2 - How to use it (junior developer):**
Create an interface with getter methods matching the
field names you need. Use that interface as the repository
method return type. Spring Data generates the SQL with
only those columns.

**Level 3 - How it works (mid-level engineer):**
For interface projections: Spring Data generates a JPQL
`SELECT` clause with the fields matching the interface's
getter names, and wraps results in JDK dynamic proxies
that implement the interface and delegate to result set
values. For class projections: Spring Data generates a
`SELECT new com.example.Dto(...)` JPQL constructor
expression; the DTO class requires a matching constructor.

**Level 4 - Trade-offs (senior/staff):**
Interface projections are convenient (no constructor
needed) but have proxy overhead per row. Class projections
are faster (plain Java objects, no proxy) but require
a matching constructor and explicit `@Query` or method
naming that matches the constructor. Open projections
with `@Value` defeat the column selection optimization
by loading the full entity. For high-performance reads,
class projections or native queries with interface
projections are optimal.

**Level 5 - Architecture (distinguished engineer):**
In CQRS-aligned architectures, projections formalize the
read model. The write model (entities with full lifecycle)
and read model (DTOs/projections) are separate Java types.
This prevents accidental mutation of read-side data
(DTOs are not managed entities; calling `dto.setName()`
has no database effect). At scale, the projection's
`SELECT` clause can be tuned to match database covering
index columns exactly, ensuring index-only scans without
hitting the data pages. This requires coordination between
DTO field selection and DBA-managed index strategy -
a read-model optimization loop.

---

### ⚙️ How It Works (Mechanism)

**SQL GENERATION BY PROJECTION TYPE:**

```java
// Entity:
// @Table(name="products")
// fields: id, name, price, description, imageData,
//         createdAt, updatedAt, ...

// Interface projection -> Spring generates:
// SELECT p.id, p.name, p.price FROM products p
interface ProductCard {
    Long getId();
    String getName();
    BigDecimal getPrice();
}

// Class projection -> Spring generates:
// SELECT new com.example.dto.ProductCard(p.id, p.name, p.price)
// FROM Product p WHERE ...
// (JPQL constructor expression)
record ProductCardDto(Long id, String name,
                      BigDecimal price) {}

// Native projection -> explicit SQL:
@Query(value="SELECT id, name, price FROM products " +
             "WHERE active=true", nativeQuery=true)
List<ProductCard> findActiveCards();
// Spring maps column names to interface methods by name
```

---

### 🔄 The Complete Picture - End-to-End Flow

**ALL THREE PROJECTION TYPES IN ONE REPOSITORY:**

```java
@Repository
public interface ProductRepository
        extends JpaRepository<Product, Long> {

    // --- Interface projection ---
    List<ProductCard> findByActive(boolean active);
    // SQL: SELECT p.id, p.name, p.price FROM products p
    //      WHERE p.active = ?
    // Returns Spring-proxy objects implementing ProductCard

    // --- Class projection (@Query required) ---
    @Query("SELECT new com.example.dto.ProductCardDto(" +
           "p.id, p.name, p.price) " +
           "FROM Product p WHERE p.active = :a")
    List<ProductCardDto> findCardDtos(
        @Param("a") boolean active);
    // Returns plain Java record/DTO objects; no proxy

    // --- Dynamic projection ---
    <T> List<T> findByCategory(String category,
                                Class<T> type);
    // Caller decides projection at runtime:
    // repo.findByCategory("Tech", ProductCard.class)
    // repo.findByCategory("Tech", Product.class)

    // --- Native projection ---
    @Query(value = "SELECT id, name, " +
                   "AVG(r.score) AS avg_rating " +
                   "FROM products p " +
                   "LEFT JOIN reviews r " +
                   "  ON r.product_id = p.id " +
                   "WHERE p.active = true " +
                   "GROUP BY p.id, p.name",
           nativeQuery = true)
    List<ProductRating> findActiveWithRatings();
}

// Usage in service:
@Transactional(readOnly = true)
public List<ProductCard> getProductCards() {
    return productRepo.findByActive(true);
    // No entity loaded; no dirty checking;
    // SELECT p.id, p.name, p.price only
}
```

---

### 💻 Code Example

**Example 1 - BAD: loading full entity for read-only API:**

```java
// BAD: loads all 40 fields, creates entity objects,
//      sets up dirty checking for ALL
// Just to return id + name + price to the API
@Transactional(readOnly = true)
public List<ProductResponse> getProducts() {
    return productRepo.findAll()
        .stream()
        .map(p -> new ProductResponse(
            p.getId(), p.getName(), p.getPrice()))
        .collect(toList());
    // SELECT * FROM products (all 40 columns)
    // Creates 40-field entities
    // Maps 3 fields to response
    // Wastes 37 fields + dirty checking overhead
}

// GOOD: interface projection
interface ProductCard {
    Long getId();
    String getName();
    BigDecimal getPrice();
}

@Transactional(readOnly = true)
public List<ProductCard> getProducts() {
    return productRepo.findByActive(true);
    // SELECT id, name, price FROM products (3 columns)
}
```

**Example 2 - BAD: open projection defeats optimization:**

```java
// BAD: @Value SpEL -> loads full entity
interface ProductView {
    @Value("#{target.name + ' - ' + target.price}")
    String getDisplay(); // SpEL: needs full entity
    // SQL: SELECT * FROM products (ALL columns)
    // Performance benefit of projection LOST
}

// GOOD: class projection with computed value
record ProductView(Long id, String name,
                   BigDecimal price) {
    public String getDisplay() {
        return name + " - " + price; // computed in Java
    }
}
// SQL: SELECT p.id, p.name, p.price FROM products p
```

**Example 3 - Nested interface projection (association):**

```java
interface OrderSummary {
    Long getId();
    String getStatus();
    CustomerInfo getCustomer(); // nested projection

    interface CustomerInfo {
        String getName();
        String getEmail();
    }
}

// SQL: SELECT o.id, o.status, c.name, c.email
//      FROM orders o JOIN customers c ON c.id = o.customer_id
// Spring Data handles nested interface projection
// and generates the JOIN automatically
```

---

### ⚖️ Comparison Table

| Projection Type    | Proxy overhead?     | Constructor needed? | Computed fields?                 | Best for                   |
| ------------------ | ------------------- | ------------------- | -------------------------------- | -------------------------- |
| Interface (closed) | Yes (JDK proxy)     | No                  | No (@Value defeats optimization) | Simple field subsets       |
| Class / Record     | No                  | Yes                 | Yes (in constructor)             | Performance-critical reads |
| Dynamic            | Depends on type     | Depends on type     | N/A                              | Flexible APIs              |
| Native + interface | No (direct mapping) | No                  | Via SQL expressions              | Analytics, complex SQL     |

---

### ⚠️ Common Misconceptions

| Misconception                                                               | Reality                                                                                                                                                                                                        |
| --------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Interface projections always load fewer columns"                           | Only CLOSED interface projections (no @Value SpEL) load fewer columns. Open projections with `@Value("#{target.field}")` load the full entity. Spring cannot determine required columns from SpEL expressions. |
| "Class projections require the DTO to be in the same package as the entity" | Class projections require the FULL qualified class name in the JPQL constructor expression: `SELECT new com.example.dto.ProductDto(...)`. Any package is fine as long as the FQN is used.                      |
| "DTO projections prevent SQL injection"                                     | Projections are not a security mechanism. They use the same JPQL parameter binding as regular queries. SQL injection protection comes from using named parameters, not from using projections.                 |
| "Projections can be updated; changes are saved"                             | DTO projections are NOT managed entities. Calling setters on a DTO has NO effect on the database. To update, load the managed entity explicitly.                                                               |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Open Projection Loads Full Entity (Performance Regression)**

**Symptom:** Adding a computed field to an interface
projection causes the `SELECT` to expand to `SELECT *`.
Response time increases significantly for large tables.

**Root Cause:** `@Value("#{target.someField + ...}")` on
an interface projection getter forces Spring to load the
full entity because it cannot statically determine which
columns the SpEL expression needs.

**Diagnosis:** Check Hibernate SQL log - if `SELECT *`
appears for a query that should use a projection, look
for `@Value` annotations on the projection interface.

**Fix:** Convert to a class projection; compute the value
in the constructor or a separate method. Use closed
interface projections (no `@Value`) for column selection
optimization.

---

**Failure Mode 2: ConstructorExpression ClassNotFoundException**

**Symptom:** `org.hibernate.exception.GenericJDBCException:
Unable to instantiate class: ...ProductDto`
or `java.lang.ClassNotFoundException: ProductDto`
during query execution.

**Root Cause:** The JPQL constructor expression uses a
simple class name instead of the fully qualified name:
`SELECT new ProductDto(...)` instead of
`SELECT new com.example.dto.ProductDto(...)`.

**Fix:** Always use fully qualified class names in JPQL
constructor expressions. Java imports do not apply to
JPQL strings.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[JPH-014 - JPQL]] - constructor expression syntax
  `SELECT new ...` is JPQL
- [[JPH-027 - N+1 Problem]] - projections are the cleanest
  fix for N+1 on read-only endpoints

**Builds On This (learn these next):**

- [[JPH-037 - EntityGraph]] - EntityGraph is a different
  approach to controlling what associations are loaded;
  compare with projections
- [[JPH-043 - Spring Data Specifications]] - Specifications
  can be combined with projections for dynamic filtering

**Related:**

- [[JPH-036 - Criteria API]] - Criteria API also supports
  tuple and constructor result projections
- [[JPH-054 - JPA at Scale]] - read model vs write model
  separation using projections

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ INTERFACE    │ interface ProductView { Long getId(); ...│
│ PROJECTION   │ Returned by: findByActive(bool)          │
│              │ Closed=SELECT specific cols. Open=SELECT │
├──────────────┼──────────────────────────────────────────┤
│ CLASS        │ record ProductDto(Long id, String name) {│
│ PROJECTION   │ @Query("SELECT new pkg.ProductDto(p.id," │
│              │   "p.name) FROM Product p WHERE ...")    │
├──────────────┼──────────────────────────────────────────┤
│ DYNAMIC      │ <T> List<T> findByStatus(String s,       │
│              │ Class<T> type);                          │
├──────────────┼──────────────────────────────────────────┤
│ NO @Value    │ @Value SpEL -> loads full entity         │
│ IN INTERFACE │ Use class projection for computed fields │
├──────────────┼──────────────────────────────────────────┤
│ NOT MANAGED  │ DTOs are not entities; setters don't save│
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "Projections load only needed columns;   │
│              │ no dirty checking; use for all read-only │
│              │ endpoints. Closed interface or class     │
│              │ projection for performance."             │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Closed interface projections load only the columns
   matching the getter names - never use `@Value` SpEL
   (forces full entity load)
2. Class projections (record/class with constructor) have
   no proxy overhead and are faster for high-volume reads
3. DTO projections are not managed entities - mutations
   do not persist; use them for read-only API responses

**Interview one-liner:** Spring Data projections load
only the specific columns needed into lightweight DTOs
instead of full managed entities. Three types: closed
interface (auto-mapped, proxy-based), class/record
(constructor expression, no proxy), and dynamic (type
decided at call time). Use projections for all read-only
endpoints: fewer columns, no dirty checking, no proxy
creation - typically 3-10x less memory than loading full
entities for read-only scenarios.

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** The read model and
write model should be separate. Entities (write model)
carry state, lifecycle, associations, and change tracking.
DTOs (read model) carry only what the caller needs:
specific fields, computed values, aggregations. This
principle is formalized in CQRS (Command Query
Responsibility Segregation) but applies at the method
level in any service layer: methods that read data should
return projections/DTOs, not managed entities that can
be accidentally mutated. This separation prevents an
entire class of bugs (unintended entity modification
from view/report code), simplifies serialization (no
lazy-load surprises in JSON serialization), and enables
independent optimization of read and write paths.

**Where else this pattern appears:**

- **GraphQL** - fields in queries are projections; only
  the requested fields are resolved (if resolvers are
  efficient)
- **MongoDB** - projection operator `{name: 1, price: 1}`
  limits returned fields at the database level
- **Elasticsearch** - `_source` includes filter; same
  concept: specify only the fields to return
- **SQL views** - a database view is a stored projection;
  application queries the view, not the base table
- **CQRS** - read side uses dedicated read models
  (projections) optimized for query patterns

---

### 💡 The Surprising Truth

Spring Data interface projections have a subtle performance
trap with Spring's `Page<T>` pagination. When you return
`Page<ProductCard>` (interface projection with pagination),
Spring Data generates a `COUNT(*)` query for `Page<T>`
metadata. The count query is generated based on the
ORIGINAL query, not the projection. If the repository
method uses a JOIN to populate the projection, the
`COUNT(*)` also JOINs - which can be significantly slower
than a plain `COUNT(*) FROM products WHERE ...`. To
optimize: provide an explicit `countQuery` in `@Query`:

```java
@Query(value = "SELECT p.id, p.name, c.name AS catName " +
               "FROM Product p JOIN p.category c " +
               "WHERE p.active = :a",
       countQuery = "SELECT COUNT(p) FROM Product p " +
                   "WHERE p.active = :a")
Page<ProductCard> findActiveCards(
    @Param("a") boolean active, Pageable pageable);
// Count query uses no JOIN; much faster on large tables
```

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **CREATE** all three projection types (interface, class,
   dynamic) for a repository method
2. **EXPLAIN** why closed interface projections optimize
   SELECT columns while open projections (with `@Value`)
   do not
3. **WRITE** a native query with interface projection that
   includes a computed SQL column (e.g., `COUNT`, `AVG`)
4. **FIX** a scenario where an open projection inadvertently
   loads the full entity
5. **COMBINE** a class projection with `Pageable` and
   provide a separate `countQuery` for optimal pagination

---

### 🎯 Interview Deep-Dive

**Q1: What are the different types of projections in
Spring Data JPA, and when would you use each?**
_Why they ask:_ Core Spring Data knowledge; tests practical
JPA expertise.
_Strong answer includes:_

- Interface projection (closed): getters match field names;
  Spring generates SELECT with those columns; uses JDK
  proxy; good for simple field subsets
- Interface projection (open): has `@Value` SpEL;
  loads full entity (optimization lost); use rarely
- Class projection: constructor-based `SELECT new DTO(...)`;
  no proxy overhead; best for performance-critical reads;
  requires `@Query`
- Dynamic projection: generic `<T>` return with `Class<T>`
  param; same method, different projection at runtime
- Native query + interface projection: automatic column-
  to-method mapping by name; useful for complex SQL with
  computed columns

**Q2: What is the difference between a DTO projection
and a managed entity in terms of JPA behavior?**
_Why they ask:_ Tests understanding of JPA lifecycle.
_Strong answer includes:_

- Managed entity: registered in persistence context;
  dirty checking tracks changes; flush sends SQL on changes;
  lazy associations can be loaded while session is open
- DTO projection: NOT registered in persistence context;
  no dirty checking; mutations have no database effect;
  no lazy loading (no proxy for associations)
- Consequence: DTOs are safe to modify without
  accidentally persisting changes; entities can be
  accidentally modified in service code that should only read
- Best practice: return DTOs from read-only service
  methods; return entities from write methods

**Q3: You have a paginated interface projection query
with a JOIN. The COUNT(\*) query is slow. How do you fix it?**
_Why they ask:_ Tests depth of Spring Data Pagination
and @Query knowledge.
_Strong answer includes:_

- Root cause: `Page<T>` auto-generates a `COUNT(*)` query
  derived from the data query; if the data query has a
  JOIN, the count query also JOINs unnecessarily
- Fix: provide explicit `countQuery` in `@Query`:
  `@Query(value="...", countQuery="SELECT COUNT(p) FROM Product p WHERE ...")`
  The count query does not need the JOIN (counting the
  parent entity is sufficient for total pages)
- Result: data query uses JOIN (for projection columns),
  count query is a simple COUNT without JOIN
