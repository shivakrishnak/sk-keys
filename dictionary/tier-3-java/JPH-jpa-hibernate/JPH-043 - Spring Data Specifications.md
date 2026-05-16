---
id: JPH-043
title: Spring Data Specifications
category: JPA & Hibernate
tier: tier-3-java
folder: JPH-jpa-hibernate
difficulty: ★★★
depends_on: JPH-014, JPH-016, JPH-023, JPH-025, JPH-027, JPH-036
used_by: JPH-053, JPH-054, JPH-056
related: JPH-030, JPH-036, JPH-037, JPH-053
tags:
  - java
  - jpa
  - spring
  - advanced
status: complete
version: 4
layout: default
parent: "JPA & Hibernate"
grand_parent: "Technical Dictionary"
nav_order: 43
permalink: /jpa-hibernate/spring-data-specifications/
---

# JPH-043 - Spring Data Specifications

⚡ **TL;DR** - `Specification<T>` is Spring Data's wrapper
around a single JPA Criteria API predicate, implemented
as a functional interface: `(Root<T>, CriteriaQuery<?>,
CriteriaBuilder) -> Predicate`. Specifications are reusable,
composable (`spec1.and(spec2).or(spec3)`), and null-safe
(return `null` to indicate "no filter"). Used with
`JpaSpecificationExecutor<T>` in repositories.
Best for dynamic search endpoints with optional filters.
Returning `null` from a Specification is idiomatic - means
"no restriction" not "IS NULL".

| #043            | Category: JPA & Hibernate                                                             | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------------------------------------ | :-------------- |
| **Depends on:** | JPQL, Spring Data JPA Repository, CRUD Methods, Pagination, N+1 Problem, Criteria API |                 |
| **Used by:**    | QueryDSL with JPA, JPA at Scale, Spring Data JPA Architecture Design                  |                 |
| **Related:**    | DTO Projections, Criteria API, EntityGraph, QueryDSL                                  |                 |

---

### 🔥 The Problem This Solves

**SEARCH API WITH OPTIONAL FILTERS:**
A product search endpoint accepts 8 optional parameters.
Without Specifications, you need one of:

1. String concatenation JPQL - injection risk, cache pollution
2. Raw Criteria API - 80 lines of verbose boilerplate
3. 256 repository methods (one per filter combination)

**WITH SPECIFICATIONS:**

```java
// Each filter is ONE Specification:
Specification<Product> spec =
    where(hasName(filter.getName()))
    .and(hasCategory(filter.getCategoryId()))
    .and(priceRange(filter.getMin(), filter.getMax()))
    .and(isActive(filter.getActive()));

Page<Product> results = productRepo.findAll(spec, pageable);
```

- Each Specification is reusable across features
- Null filter = null Specification = no WHERE clause added
- Composable: combine with `.and()`, `.or()`, `.not()`
- Testable in isolation

---

### 📘 Textbook Definition

**Specification<T>** is a functional interface from Spring Data:

```java
public interface Specification<T> {
    Predicate toPredicate(
        Root<T> root,
        CriteriaQuery<?> query,
        CriteriaBuilder criteriaBuilder);

    // Composition methods:
    default Specification<T> and(Specification<T> other)
    default Specification<T> or(Specification<T> other)
    default Specification<T> not()
    static <T> Specification<T> where(Specification<T> spec)
    static <T> Specification<T> not(Specification<T> spec)
}
```

**JpaSpecificationExecutor<T>** adds specification-aware
query methods to a repository:

```java
public interface JpaSpecificationExecutor<T> {
    Optional<T> findOne(Specification<T> spec);
    List<T> findAll(Specification<T> spec);
    Page<T> findAll(Specification<T> spec, Pageable pageable);
    List<T> findAll(Specification<T> spec, Sort sort);
    long count(Specification<T> spec);
}
```

**Key behavior:** When a Specification's `toPredicate()` returns
`null`, Spring Data treats it as "no restriction" for that
predicate - it is excluded from the WHERE clause.

---

### ⏱️ Understand It in 30 Seconds

**One line:** `Specification<T>` is a single, reusable,
composable WHERE clause condition expressed as a lambda
instead of JPQL string or Criteria boilerplate.

**One analogy:**

> A SQL WHERE clause is built from AND/OR conditions.
> A Specification is one such condition as a Java object.
> `spec1.and(spec2)` is `WHERE cond1 AND cond2`.
> `spec1.or(spec2)` is `WHERE cond1 OR cond2`.
> Returning `null` from `toPredicate` means "skip this
> condition entirely". You build the full WHERE clause
> from a list of individual conditions, composing at runtime.

**One insight:** The Specification pattern (from Eric Evans'
Domain-Driven Design, 2003) encapsulates a business rule as
an object that can be combined with AND/OR/NOT. Spring Data's
implementation applies this to JPA queries: each business
filter rule is a Specification, composed at the query layer.

---

### 🔩 First Principles Explanation

**SPECIFICATION AS PREDICATE FACTORY:**

```java
// Each method returns: (root, query, cb) -> Predicate
// The method is called "specification factory method"

public class ProductSpecs {

    // Returns null if name is null (means: no name filter)
    public static Specification<Product> hasName(String name) {
        return (root, query, cb) ->
            name == null ? null :
            cb.like(cb.lower(root.get(Product_.name)),
                    "%" + name.toLowerCase() + "%");
    }

    public static Specification<Product> hasCategory(
            Long categoryId) {
        return (root, query, cb) ->
            categoryId == null ? null :
            cb.equal(
                root.get(Product_.category).get(Category_.id),
                categoryId);
    }

    public static Specification<Product> priceRange(
            BigDecimal min, BigDecimal max) {
        // Compose two predicates within one Specification:
        return (root, query, cb) -> {
            List<Predicate> preds = new ArrayList<>();
            if (min != null) preds.add(
                cb.ge(root.get(Product_.price), min));
            if (max != null) preds.add(
                cb.le(root.get(Product_.price), max));
            return preds.isEmpty() ? null :
                cb.and(preds.toArray(new Predicate[0]));
        };
    }

    public static Specification<Product> isActive() {
        return (root, query, cb) ->
            cb.isTrue(root.get(Product_.active));
    }
}
```

---

### 🧪 Thought Experiment

**NULL SPECIFICATION HANDLING:**

```java
// Caller: name=null, categoryId=5, min=null, max=100
Specification<Product> spec =
    where(hasName(null))          // null -> excluded
    .and(hasCategory(5L))         // cb.equal -> included
    .and(priceRange(null, 100))   // only max pred -> included
    .and(isActive());             // always included

// Spring Data assembles:
// WHERE category.id = 5
//   AND price <= 100
//   AND active = true
// (no name condition; null spec = no restriction)

// SQL:
// SELECT p.* FROM products p
// INNER JOIN categories c ON c.id = p.category_id
// WHERE c.id = ?      -- categoryId = 5
//   AND p.price <= ?  -- max = 100
//   AND p.active = true
```

---

### 🧠 Mental Model / Analogy

> A `Specification<Product>` is like a single row in a
> filter configuration: `{field: "category", op: "eq",
value: "Electronics"}`. The Specification's `toPredicate()`
> method is the executor that translates this to a SQL
> predicate. Composing specifications (`spec1.and(spec2)`)
> is building a filter chain: "category = Electronics"
> AND "price < 100". The Specification pattern makes
> each filter rule an independent, testable object that
> can be composed at runtime - a functional approach to
> dynamic query building.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Specifications let you build database search filters as
reusable Java objects. You combine them with `.and()` and
`.or()` to create complex queries without writing JPQL strings.

**Level 2 - How to use it (junior developer):**

1. Add `JpaSpecificationExecutor<T>` to your repository
2. Create static methods that return `Specification<T>` lambdas
3. Compose with `Specification.where(spec1).and(spec2)`
4. Call `findAll(spec, pageable)`
5. Return null from toPredicate to skip a condition

**Level 3 - How it works (mid-level engineer):**
Specifications wrap Criteria API predicates. Spring Data
calls each Specification's `toPredicate()` and combines
non-null results. The combined Predicate becomes the WHERE
clause of the generated JPQL/SQL. Under the hood: it's
the same as writing Criteria API manually, but with
composable objects instead of inline code.

**Level 4 - Fetch joins with Specifications (senior engineer):**
Combining Specifications with `findAll(spec, pageable)` and
`@EntityGraph` can cause HHH90003004 (in-memory pagination)
if the Specification is used with a JOIN on a collection.
The Specification lambda receives the `CriteriaQuery<?>` -
you can call `query.distinct(true)` inside the specification
to deduplicate rows from JOIN. However, `distinct` with
LIMIT/OFFSET still has Hibernate pagination issues. For
paginated queries with JOINs: use the two-query pattern.

**Level 5 - Specification for authorization (staff engineer):**
Specifications are powerful for row-level security: inject
the current user/tenant into the specification to add
an automatic filter. Every query automatically includes
the tenant or user filter:

```java
Specification<Order> tenantSpec = (root, q, cb) ->
    cb.equal(root.get(Order_.tenantId), currentTenantId);
// Applied to ALL order queries for this tenant
```

This is the Specification pattern as a cross-cutting
concern - no service method needs to remember to add
the tenant filter; the base specification handles it.

---

### ⚙️ How It Works (Mechanism)

**REPOSITORY SETUP:**

```java
public interface ProductRepository
        extends JpaRepository<Product, Long>,
                JpaSpecificationExecutor<Product> {
    // JpaSpecificationExecutor adds:
    // findAll(Specification, Pageable) -> Page<T>
    // findAll(Specification) -> List<T>
    // count(Specification) -> long
    // findOne(Specification) -> Optional<T>
}
```

**COMPLETE SEARCH SERVICE:**

```java
@Service
@RequiredArgsConstructor
public class ProductSearchService {

    private final ProductRepository repo;

    public Page<Product> search(ProductFilter filter,
                                Pageable pageable) {
        Specification<Product> spec =
            Specification.where(
                ProductSpecs.hasName(filter.getName()))
            .and(ProductSpecs.hasCategory(
                filter.getCategoryId()))
            .and(ProductSpecs.priceRange(
                filter.getMinPrice(),
                filter.getMaxPrice()))
            .and(filter.isActiveOnly() ?
                ProductSpecs.isActive() : null);

        return repo.findAll(spec, pageable);
    }

    public long countMatching(ProductFilter filter) {
        Specification<Product> spec =
            Specification.where(
                ProductSpecs.hasName(filter.getName()))
            .and(ProductSpecs.hasCategory(
                filter.getCategoryId()));
        return repo.count(spec);
    }
}
```

---

### 🔄 The Complete Picture - End-to-End Flow

**TESTING SPECIFICATIONS IN ISOLATION:**

```java
// Unit test: Specification produces correct predicate
@ExtendWith(MockitoExtension.class)
class ProductSpecsTest {
    @Mock CriteriaBuilder cb;
    @Mock Root<Product> root;
    @Mock CriteriaQuery<?> query;
    @Mock Path<String> namePath;
    @Mock Expression<String> lowerNamePath;
    @Mock Predicate likePredicate;

    @Test
    void hasName_returnsNullWhenNameIsNull() {
        Predicate result = ProductSpecs.hasName(null)
            .toPredicate(root, query, cb);
        assertNull(result); // null = no restriction
    }

    @Test
    void hasName_returnsLikePredicateWhenNameProvided() {
        when(root.get(Product_.name)).thenReturn(namePath);
        when(cb.lower(namePath)).thenReturn(lowerNamePath);
        when(cb.like(lowerNamePath, "%laptop%"))
            .thenReturn(likePredicate);

        Predicate result = ProductSpecs.hasName("Laptop")
            .toPredicate(root, query, cb);

        assertEquals(likePredicate, result);
        verify(cb).like(lowerNamePath, "%laptop%");
    }
}

// Integration test (SpringBootTest + @Transactional):
@Test
void search_filtersByNameAndCategory() {
    Product laptop = createProduct("Laptop", "Electronics", 999.99);
    Product mouse = createProduct("Mouse", "Electronics", 29.99);
    Product book = createProduct("Java Book", "Books", 49.99);

    Specification<Product> spec =
        where(hasName("Laptop"))
        .and(hasCategory(electronicsId));

    List<Product> results = repo.findAll(spec);
    assertThat(results).containsExactly(laptop);
}
```

---

### 💻 Code Example

**Example 1 - BAD: null check missing, NullPointerException:**

```java
// BAD: calling .and() with null spec crashes
public static Specification<Product> priceRange(
        BigDecimal min, BigDecimal max) {
    Specification<Product> spec =
        (root, q, cb) -> cb.ge(
            root.get(Product_.price), min); // NPE if min null!
    if (max != null) {
        spec = spec.and((root, q, cb) -> cb.le(
            root.get(Product_.price), max));
    }
    return spec;
}

// GOOD: return null when not applicable
public static Specification<Product> minPrice(
        BigDecimal min) {
    return (root, q, cb) ->
        min == null ? null :
        cb.ge(root.get(Product_.price), min);
}
```

**Example 2 - Reusable tenant filter:**

```java
// Tenant-aware specification (multi-tenancy safety):
public static Specification<Order> belongsToTenant(
        String tenantId) {
    return (root, query, cb) ->
        tenantId == null ?
            cb.conjunction()  // always-true (admin bypass)
            : cb.equal(root.get(Order_.tenantId), tenantId);
}

// Applied automatically in base query:
public Page<Order> findOrders(OrderFilter filter,
                              String tenantId,
                              Pageable pageable) {
    return orderRepo.findAll(
        Specification.where(belongsToTenant(tenantId))
            .and(OrderSpecs.hasStatus(filter.getStatus())),
        pageable);
}
```

---

### ⚖️ Comparison Table

| Approach             | Type-safe       | Composable     | Reusable      | Verbosity | Best for                               |
| -------------------- | --------------- | -------------- | ------------- | --------- | -------------------------------------- |
| String JPQL `@Query` | No              | No             | No            | Low       | Static queries                         |
| Criteria API (raw)   | Yes (metamodel) | Manual         | Manual        | Very High | Framework code                         |
| `Specification<T>`   | Yes (metamodel) | Yes (built-in) | Yes (methods) | Medium    | Dynamic search in Spring               |
| Querydsl             | Yes (generated) | Yes            | Yes           | Low       | Dynamic queries, preferred alternative |

---

### ⚠️ Common Misconceptions

| Misconception                                                     | Reality                                                                                                                                                                                                                                                                                                     |
| ----------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Returning null from toPredicate means 'match null rows'"         | Returning `null` from `toPredicate` means "no predicate" - the condition is excluded from the WHERE clause entirely. To match NULL values in a column, use `cb.isNull(root.get("field"))`.                                                                                                                  |
| "Specifications work with regular JpaRepository"                  | Specifications require `JpaSpecificationExecutor<T>`. The repository must extend BOTH `JpaRepository<T, ID>` AND `JpaSpecificationExecutor<T>`.                                                                                                                                                             |
| "spec1.and(spec2) when spec2 is null throws NullPointerException" | Spring Data handles null gracefully in `Specification.where(null)` (returns all-matching spec). However, calling `spec1.and(null)` directly on a Specification instance MAY throw NPE depending on implementation. Use `Specification.where(spec1).and(spec2)` and return null from within `toPredicate()`. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode: Duplicate Results with JOIN**

**Symptom:** `findAll(spec, pageable)` returns duplicate
entities. `products.size()` returns 300 when expecting 30.
**Root Cause:** The specification adds a JOIN (e.g., on
a collection association). The JOIN multiplies rows.
Without `DISTINCT`, each row in the result is mapped to
a separate entity (with duplicates).
**Fix:**

```java
// In the Specification that adds a JOIN:
public static Specification<Product> hasTag(String tag) {
    return (root, query, cb) -> {
        query.distinct(true);  // Add DISTINCT to the query
        Join<Product, String> tags =
            root.join(Product_.tags, JoinType.INNER);
        return cb.equal(tags, tag);
    };
}
// Note: DISTINCT + LIMIT may still cause HHH90003004
// for collection JOINs with Pageable
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[JPH-036 - Criteria API]] - Specifications are wrappers
  around Criteria API predicates

**Builds On This (learn these next):**

- [[JPH-053 - QueryDSL with JPA]] - more expressive
  alternative to raw Specifications
- [[JPH-056 - Spring Data JPA Architecture]] - how
  Specifications fit in the overall architecture

**Related:**

- [[JPH-030 - DTO Projections]] - combine with Specifications
  for efficient dynamic queries returning DTOs
- [[JPH-037 - EntityGraph]] - combine with findAll(spec, pageable)
  carefully to avoid HHH90003004

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ INTERFACE    │ Specification<T> (functional interface)   │
│ REPO EXTENDS │ JpaSpecificationExecutor<T>               │
├──────────────┼───────────────────────────────────────────┤
│ COMPOSE      │ where(s1).and(s2).or(s3).not()            │
│ NO FILTER    │ return null from toPredicate()            │
│ ALWAYS TRUE  │ cb.conjunction() (no restriction)         │
├──────────────┼───────────────────────────────────────────┤
│ PAGINATED    │ findAll(spec, pageable) -> Page<T>         │
│ COUNT        │ count(spec) -> long                       │
├──────────────┼───────────────────────────────────────────┤
│ DUPLICATES   │ query.distinct(true) in Specification     │
│ METAMODEL    │ Product_.name for compile-safe field refs │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Specification<T> = composable WHERE      │
│              │ clause fragment; return null = no filter; │
│              │ compose with .and()/.or()/.not()."        │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. `Specification<T>` is a `(root, query, cb) -> Predicate`
   lambda; composable with `.and()`, `.or()`, `.not()`
2. Return `null` from `toPredicate()` = "no restriction"
   (idiomatic null-safety pattern for optional filters)
3. Repository must extend `JpaSpecificationExecutor<T>`;
   then `findAll(spec, pageable)` builds the WHERE dynamically

**Interview one-liner:** Spring Data's `Specification<T>`
wraps a JPA Criteria API predicate as a reusable, composable
object. Factory methods return `null` when the filter is
not active (skips the condition). Compose with `where(s1).and(s2)`.
Repository must extend `JpaSpecificationExecutor<T>`. Best
for dynamic search endpoints with optional filters; Querydsl
provides a cleaner syntax for the same use case.

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** The Specification
pattern (DDD, Evans 2003) encapsulates a business rule
as an object that can be combined with AND/OR/NOT.
It enables: (1) Reuse - define once, use in multiple queries,
(2) Testability - each specification testable in isolation,
(3) Composability - combine specifications for complex rules,
(4) Readability - `where(isActive()).and(belongsToTenant(t))` reads
like English. This pattern generalizes beyond JPA:
ElasticSearch has Query DSL composed from bool/must/should queries;
Mongo has `$and`/`$or` aggregation pipelines; GraphQL has
filtering inputs composed at the resolver level.
The core insight: break down complex boolean logic into
named, composable, independent pieces.

**Where else this pattern appears:**

- **ElasticSearch Bool Query** - `must`, `should`, `filter`,
  `must_not` clauses compose exactly like Specifications
- **MongoDB Query** - `Query.query(where("active").is(true).and("category").is("X"))`
  uses Spring's `Criteria` for the same pattern
- **Querydsl** - generates type-safe `Predicate` objects;
  composes with `.and()`/`.or()`; similar concept, better syntax

---

### 💡 The Surprising Truth

Spring Data's `Specification<T>` has a lesser-known third
parameter in `toPredicate()`: `CriteriaQuery<?> query`.
Most developers only use `root` and `cb` (CriteriaBuilder).
But `query` allows modifying the entire query from within
a Specification: adding `ORDER BY`, calling `query.distinct(true)`,
adding subqueries, or even changing the `SELECT` clause.
This means a Specification can be more than a predicate -
it can be a query-modifier. Common use: `query.distinct(true)`
for JOIN deduplication. Uncommon but valid: a Specification
that adds `ORDER BY` to the query. Very advanced: a
Specification that adds a `HAVING` clause via subquery.
The parameter name `query` is the key to unlocking these
advanced capabilities.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **IMPLEMENT** 5 Specification factory methods with proper
   null handling and JPA metamodel field references
2. **COMPOSE** specifications: `where(s1).and(s2).or(s3).not()`
3. **EXPLAIN** why returning `null` from `toPredicate()` means
   "no restriction" and how Spring Data handles it
4. **ADD** `JpaSpecificationExecutor<T>` and use `findAll(spec, pageable)`
5. **WRITE** a unit test for an individual Specification
   using mocked CriteriaBuilder/Root

---

### 🎯 Interview Deep-Dive

**Q1: What is a Spring Data Specification and how does it
relate to the JPA Criteria API?**
_Why they ask:_ Tests Spring Data + JPA knowledge combination.
_Strong answer includes:_

- Specification: functional interface `(Root, CriteriaQuery, CriteriaBuilder) -> Predicate`
- Spring Data wrapper around a Criteria API predicate
- Adds composability: `.and()`, `.or()`, `.not()`
- Return null = no restriction (not "is null")
- Requires `JpaSpecificationExecutor<T>` in repository
- `findAll(spec, pageable)` builds the WHERE clause from the predicate

**Q2: When would you return null vs cb.conjunction() from a Specification?**
_Why they ask:_ Tests precise understanding of null semantics.
_Strong answer includes:_

- Return `null`: "this filter is not active; exclude this
  condition entirely from the WHERE clause"
- Return `cb.conjunction()`: "add a 1=1 always-true predicate;
  no real restriction, but predicate IS added"
- Practical difference: `null` is cleaner (spring ignores it);
  `cb.conjunction()` still appears in the query but has no effect
- Pattern: null-safe factory methods (`name == null ? null : cb.like(...)`)
  produce null when the filter parameter is absent; Spring Data
  excludes null predicates from the final WHERE clause
