---
id: JPH-053
title: QueryDSL with JPA
category: JPA & Hibernate
tier: tier-3-java
folder: JPH-jpa-hibernate
difficulty: ★★★
depends_on: JPH-006, JPH-007, JPH-008, JPH-014, JPH-016, JPH-023, JPH-025, JPH-036, JPH-043
used_by: JPH-054, JPH-055, JPH-059
related: JPH-036, JPH-043, JPH-050, JPH-055
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
nav_order: 53
permalink: /jpa-hibernate/querydsl/
---

# JPH-053 - QueryDSL with JPA

⚡ **TL;DR** - QueryDSL generates `Q`-prefixed meta-model
classes from JPA entities (`QProduct`, `QOrder`). Use them
to write type-safe, composable JPQL queries in Java.
`JPAQueryFactory.select().from(QProduct.product).where()`
compiles correctly only if `QProduct.product.name` exists.
Typos and wrong field types = compile errors. Integrates
with Spring Data via `QuerydslPredicateExecutor<T>`:
`repo.findAll(predicate, pageable)`. Used for dynamic
filters (search forms with optional fields). Overlap with
Spring Data Specifications; choose one consistently.

| #053            | Category: JPA & Hibernate                                                                                                        | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Entity Basics, @ManyToOne, @OneToMany, JPQL, Spring Data JPA, Spring Data Repositories, Criteria API, Spring Data Specifications |                 |
| **Used by:**    | JPA at Scale, ORM Selection Framework, Spring Data JPA vs JOOQ                                                                   |                 |
| **Related:**    | Criteria API, Spring Data Specifications, Hibernate vs MyBatis vs JOOQ, ORM Selection                                            |                 |

---

### 🔥 The Problem This Solves

**TYPE-SAFE DYNAMIC QUERIES:**

```java
// BAD: JPQL string concatenation for dynamic search
public List<Product> search(String name, Double minPrice,
    String category) {
    StringBuilder jpql = new StringBuilder(
        "SELECT p FROM Product p WHERE 1=1");
    if (name != null) {
        jpql.append(" AND p.name LIKE :name");
    }
    if (minPrice != null) {
        jpql.append(" AND p.price >= :minPrice");
    }
    if (category != null) {
        jpql.append(" AND p.category.name = :category");
    }
    TypedQuery<Product> q =
        em.createQuery(jpql.toString(), Product.class);
    if (name != null) q.setParameter("name", "%"+name+"%");
    // ... fragile string concatenation; no compile check

// GOOD: QueryDSL type-safe predicate composition
public List<Product> search(String name, Double minPrice,
    String category) {
    QProduct p = QProduct.product;
    BooleanBuilder predicate = new BooleanBuilder();
    if (name != null)
        predicate.and(p.name.containsIgnoreCase(name));
    if (minPrice != null)
        predicate.and(p.price.goe(minPrice));
    if (category != null)
        predicate.and(p.category.name.eq(category));
    return repo.findAll(predicate);
    // Compile-time safe; p.name, p.price are typed fields
```

---

### 📘 Textbook Definition

**QueryDSL** is a Java DSL library for constructing
type-safe queries. QueryDSL-JPA generates `Q` meta-model
classes from JPA entity classes (similar to JPA's own
metamodel but with fluent query API).

**Core components:**

| Component                          | Role                                                                        |
| ---------------------------------- | --------------------------------------------------------------------------- |
| `Q` classes (`QProduct`, `QOrder`) | Type-safe query meta-model; field-level predicates                          |
| `JPAQueryFactory`                  | Entry point for building JPA queries                                        |
| `BooleanBuilder`                   | Composable boolean predicate (`and`, `or`, `not`)                           |
| `Predicate`                        | Single condition (`p.price.gt(100)`)                                        |
| `QuerydslPredicateExecutor<T>`     | Spring Data interface: `findAll(Predicate)`, `findAll(Predicate, Pageable)` |

**Dependencies:**

```xml
<dependency>
    <groupId>com.querydsl</groupId>
    <artifactId>querydsl-jpa</artifactId>
    <classifier>jakarta</classifier> <!-- for Jakarta EE -->
</dependency>
<dependency>
    <groupId>com.querydsl</groupId>
    <artifactId>querydsl-apt</artifactId>
    <classifier>jakarta</classifier>
    <scope>provided</scope>
</dependency>
```

APT (annotation processor) generates Q classes at build time.

---

### ⏱️ Understand It in 30 Seconds

**One line:** QueryDSL generates `Q`-prefixed meta-model
classes from JPA entities so you can write JPQL-like
queries as Java code with compile-time type safety.

**One analogy:**

> QueryDSL is to JPQL what a type-safe HTTP client
> (Feign, Retrofit) is to raw `HttpClient.get(urlString)`.
> Without QueryDSL: write JPQL as strings ("WHERE p.price
>
> > :min"); typos found at runtime. With QueryDSL: write
> > `QProduct.product.price.gt(min)`; `price` is a typed
> > Java field. Typo (`QProduct.product.priice`) = compile
> > error. The `Q` class is the "interface definition" of
> > your entity, just like Feign interface defines your API.

**One insight:** QueryDSL-JPA generates JPQL under the hood -
it is NOT a SQL DSL (unlike JOOQ). It still goes through JPA's
query engine. This means it has the same JPQL limitations:
no window functions, no CTEs, no PostgreSQL-specific features.
For complex SQL: use JOOQ. For type-safe entity queries with
dynamic predicates: use QueryDSL or Spring Data Specifications.

---

### 🔩 First Principles Explanation

**Q CLASS GENERATION:**

```
Entity: Product.java
  @Entity
  @Table(name = "products")
  public class Product {
      @Id Long id;
      String name;
      BigDecimal price;
      @ManyToOne Category category;
  }

APT generates: QProduct.java
  public class QProduct extends EntityPathBase<Product> {
      public static final QProduct product =
          new QProduct("product");

      public final NumberPath<Long> id =
          createNumber("id", Long.class);
      public final StringPath name =
          createString("name");
      public final NumberPath<BigDecimal> price =
          createNumber("price", BigDecimal.class);
      public final QCategory category;

      // Methods available on NumberPath<BigDecimal>:
      //   .gt(value)    -> greater than
      //   .goe(value)   -> greater than or equal
      //   .lt(value)    -> less than
      //   .between(a,b) -> between range
      // Methods on StringPath:
      //   .eq(value)    -> equals
      //   .containsIgnoreCase(value) -> LIKE %value%
      //   .startsWith(value)         -> LIKE value%
      //   .isNotNull()               -> IS NOT NULL
  }
```

---

### 🧪 Thought Experiment

**QueryDSL vs Spring Data Specifications - choosing:**

```
Project with 20 dynamic search endpoints.
Each has 5-10 optional filter fields.

QueryDSL approach:
  BooleanBuilder b = new BooleanBuilder();
  b.and(qProduct.name.containsIgnoreCase(name));
  b.and(qProduct.price.goe(minPrice));
  // Concise; method chaining; readable
  // External Predicate type (not JPA Specification)
  // Must add QuerydslPredicateExecutor to ALL 20 repos

Specifications approach:
  Specification<Product> spec =
    Specification
      .where(name != null ? nameLike(name) : null)
      .and(minPrice != null ? priceGoe(minPrice) : null);
  // Pure JPA standard (no extra dep after Spring Data)
  // Composition: where().and().or() is readable
  // Reusable individual specs (nameLike, priceGoe)

Decision matrix:
  - Team knows QueryDSL well: QueryDSL
  - Want pure Spring Data JPA (no APT build step): Specs
  - Complex path navigation (category.supplier.country.name):
    both work equally; QueryDSL is more concise
  - Projects using JOOQ already for SQL: use JOOQ for
    dynamic queries too (consistent DSL)
  DO NOT use both - pick one and be consistent.
```

---

### 🧠 Mental Model / Analogy

> QueryDSL is a "compiler plugin" for your query layer.
> Regular JPQL: the compiler doesn't know that
> `"SELECT p FROM Product p WHERE p.name LIKE :n"` has
> `p.name` referencing a String field - it's just a String.
> Typo: `p.nme` - compiles fine, fails at runtime.
> QueryDSL's Q class: `QProduct.product.name` is a
> `StringPath` field in a Java class. `QProduct.product.nme`
> doesn't compile - the field doesn't exist. QueryDSL
> moved the "schema is correct" check from runtime
> to compile time.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
QueryDSL generates helper classes from JPA entities so
you can write database queries as Java code instead of
SQL/JPQL strings. Errors caught by compiler, not at runtime.

**Level 2 - Basic usage (junior developer):**

```java
@Repository
@RequiredArgsConstructor
public class ProductQueryRepository {

    private final JPAQueryFactory factory;

    public List<Product> findByNameAndMinPrice(
        String name, BigDecimal minPrice) {
        QProduct p = QProduct.product;
        return factory
            .selectFrom(p)
            .where(
                p.name.containsIgnoreCase(name),
                p.price.goe(minPrice))
            .orderBy(p.price.asc())
            .fetch();
    }
}
```

**Level 3 - Spring Data integration (mid-level engineer):**

```java
// Repository with QuerydslPredicateExecutor:
public interface ProductRepository
    extends JpaRepository<Product, Long>,
    QuerydslPredicateExecutor<Product> {
}

// Usage: findAll accepts Predicate + Pageable
@Service
@RequiredArgsConstructor
public class ProductSearchService {
    private final ProductRepository repo;

    public Page<Product> search(
        ProductSearchCriteria criteria,
        Pageable pageable) {
        QProduct p = QProduct.product;
        BooleanBuilder pred = new BooleanBuilder();
        if (criteria.getName() != null) {
            pred.and(p.name.containsIgnoreCase(
                criteria.getName()));
        }
        if (criteria.getMinPrice() != null) {
            pred.and(p.price.goe(
                criteria.getMinPrice()));
        }
        return repo.findAll(pred, pageable);
    }
}
```

**Level 4 - JOIN queries (senior engineer):**

```java
QProduct product = QProduct.product;
QCategory cat    = QCategory.category;

List<ProductDto> results = factory
    .select(Projections.constructor(
        ProductDto.class,
        product.id,
        product.name,
        product.price,
        cat.name.as("categoryName")))
    .from(product)
    .leftJoin(product.category, cat)
    .where(
        cat.name.in("Electronics", "Books"),
        product.price.between(
            new BigDecimal("10"),
            new BigDecimal("500")))
    .orderBy(product.price.desc())
    .offset(pageable.getOffset())
    .limit(pageable.getPageSize())
    .fetch();
```

**Level 5 - Count + fetchResults pattern (staff engineer):**

```java
// Pagination with total count (efficient):
QProduct p = QProduct.product;
BooleanPredicate predicate = buildPredicate(criteria);

List<Product> content = factory
    .selectFrom(p)
    .where(predicate)
    .orderBy(p.price.desc())
    .offset(pageable.getOffset())
    .limit(pageable.getPageSize())
    .fetch();

JPAQuery<Long> countQuery = factory
    .select(p.count())
    .from(p)
    .where(predicate);

return PageableExecutionUtils.getPage(
    content, pageable, countQuery::fetchOne);
// PageableExecutionUtils: only runs count query if
// needed (e.g., not last page already determined)
```

---

### ⚙️ How It Works (Mechanism)

**BUILD CONFIGURATION:**

```xml
<!-- Maven: APT annotation processor -->
<plugin>
    <groupId>com.mysema.maven</groupId>
    <artifactId>apt-maven-plugin</artifactId>
    <version>1.1.3</version>
    <executions>
        <execution>
            <goals><goal>process</goal></goals>
            <configuration>
                <outputDirectory>
                    target/generated-sources/java
                </outputDirectory>
                <processor>
                    com.querydsl.apt.jpa.JPAAnnotationProcessor
                </processor>
            </configuration>
        </execution>
    </executions>
</plugin>
```

```java
// JPAQueryFactory Spring bean:
@Configuration
public class QueryDslConfig {
    @Bean
    public JPAQueryFactory jpaQueryFactory(
        EntityManager em) {
        return new JPAQueryFactory(em);
    }
}
```

---

### 🔄 The Complete Picture - End-to-End Flow

**DYNAMIC FILTER WITH PAGINATION:**

```java
@Service
@RequiredArgsConstructor
public class OrderSearchService {
    private final JPAQueryFactory factory;

    public Page<OrderDto> searchOrders(
        OrderSearchForm form, Pageable pageable) {

        QOrder order   = QOrder.order;
        QCustomer cust = QCustomer.customer;

        // Build predicate dynamically:
        BooleanBuilder pred = new BooleanBuilder();
        if (form.getStatus() != null)
            pred.and(order.status.eq(form.getStatus()));
        if (form.getMinAmount() != null)
            pred.and(order.total.goe(form.getMinAmount()));
        if (form.getCustomerName() != null)
            pred.and(cust.name.containsIgnoreCase(
                form.getCustomerName()));
        if (form.getFromDate() != null)
            pred.and(order.createdAt.goe(
                form.getFromDate()));

        // Fetch content:
        List<OrderDto> content = factory
            .select(Projections.constructor(
                OrderDto.class,
                order.id, order.total,
                order.status, cust.name))
            .from(order)
            .join(order.customer, cust)
            .where(pred)
            .orderBy(order.createdAt.desc())
            .offset(pageable.getOffset())
            .limit(pageable.getPageSize())
            .fetch();

        // Count:
        JPAQuery<Long> count = factory
            .select(order.count())
            .from(order)
            .join(order.customer, cust)
            .where(pred);

        return PageableExecutionUtils.getPage(
            content, pageable, count::fetchOne);
    }
}
```

---

### 💻 Code Example

**Example 1 - BAD: Q class path navigation typo - compile error:**

```java
QProduct p = QProduct.product;

// GOOD: compile-time safe
p.category.name.eq("Electronics"); // compiles

// BAD: typo - caught at compile time (not runtime)
p.category.nme.eq("Electronics"); // COMPILE ERROR
// 'nme' does not exist in QCategory

// Compare to JPQL string (typo found at runtime only):
em.createQuery(
    "SELECT p FROM Product p " +
    "WHERE p.category.nme = :cat") // RUNTIME failure
```

**Example 2 - Reusable predicates:**

```java
// Create reusable predicate factory:
public class ProductPredicates {

    public static Predicate inPriceRange(
        BigDecimal min, BigDecimal max) {
        QProduct p = QProduct.product;
        BooleanBuilder b = new BooleanBuilder();
        if (min != null) b.and(p.price.goe(min));
        if (max != null) b.and(p.price.loe(max));
        return b.getValue();
    }

    public static Predicate inCategory(String... cats) {
        return QProduct.product.category.name.in(cats);
    }

    public static Predicate isActive() {
        return QProduct.product.active.isTrue();
    }
}

// Usage: compose reusable predicates:
repo.findAll(
    ProductPredicates.isActive()
        .and(ProductPredicates.inPriceRange(10, 500))
        .and(ProductPredicates.inCategory("Electronics")));
```

---

### ⚖️ Comparison Table

| Feature                  | QueryDSL                      | Spring Data Specifications        | JOOQ                          |
| ------------------------ | ----------------------------- | --------------------------------- | ----------------------------- |
| Type safety              | Yes (Q classes)               | Partial (CriteriaBuilder verbose) | Yes (generated table classes) |
| SQL backend              | JPQL (via JPA)                | JPQL (via JPA)                    | Native SQL                    |
| Complex SQL (window fn)  | No                            | No                                | Yes                           |
| Code generation          | APT (Q classes)               | None needed                       | Schema-based codegen          |
| Learning curve           | Medium                        | Medium (CriteriaBuilder verbose)  | Medium                        |
| Spring Data integration  | `QuerydslPredicateExecutor`   | `JpaSpecificationExecutor`        | Manual                        |
| Jakarta EE compatibility | Requires `jakarta` classifier | Native JPA                        | Separate dialects             |

---

### ⚠️ Common Misconceptions

| Misconception                                | Reality                                                                                                                                                                                                                                       |
| -------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "QueryDSL generates native SQL like JOOQ"    | NO - QueryDSL-JPA generates JPQL, not SQL. It goes through JPA's query engine. Window functions, CTEs, and DB-specific SQL are NOT supported. For native SQL type-safety: use JOOQ.                                                           |
| "QueryDSL replaces Spring Data repositories" | NO - `QuerydslPredicateExecutor` is an extension to Spring Data repositories. You still extend `JpaRepository<T,ID>` and ADD `QuerydslPredicateExecutor<T>`. Standard methods (`save`, `findById`, `findAll`) still work.                     |
| "Q classes must be manually maintained"      | NO - APT regenerates Q classes from entity annotations on every build. Never manually edit Q classes (they're in `target/generated-sources` and should be gitignored). Any entity change automatically regenerates the corresponding Q class. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode: Q Classes Not Generated**

**Symptom:** `QProduct cannot be resolved to a type`.
Code that uses `QProduct.product` doesn't compile.
**Root Cause:** APT annotation processor not configured,
not running, or generated sources directory not added
to build classpath.
**Diagnosis:**

```
# Check: does target/generated-sources/java exist?
ls target/generated-sources/java/

# If empty/missing: APT not running
# Verify: querydsl-apt dependency is present
#   AND processor configured in build plugin
# For IntelliJ: File -> Invalidate Caches
#   OR: Mark directory as "Generated Sources Root"
#   (target/generated-sources/java)
```

**Fix:** In Maven: add `apt-maven-plugin` with processor
`com.querydsl.apt.jpa.JPAAnnotationProcessor`. Rebuild.
In Gradle: use `querydsl` plugin. Verify the generated
sources directory is on the build classpath.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[JPH-036 - Criteria API]] - QueryDSL solves the same
  problem as Criteria API but with a cleaner syntax; compare
- [[JPH-043 - Spring Data Specifications]] - both are used
  for dynamic predicates; pick one approach, don't mix

**Builds On This (learn these next):**

- [[JPH-055 - ORM Selection Framework]] - when to choose
  QueryDSL vs Specifications vs JOOQ
- [[JPH-059 - Spring Data JPA vs JOOQ vs MyBatis Decision]]
  - QueryDSL position in the broader tool selection decision

**Related:**

- [[JPH-050 - Hibernate vs MyBatis vs JOOQ]] - JOOQ is an
  alternative to QueryDSL for type-safe queries; comparison
- [[JPH-023 - Spring Data Repositories]] - QuerydslPredicateExecutor
  extends Spring Data repository interfaces

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ Q CLASSES    │ APT generates from @Entity classes        │
│              │ target/generated-sources/java/            │
├──────────────┼───────────────────────────────────────────┤
│ QUERY        │ JPAQueryFactory.selectFrom(QProduct.p)    │
│ FACTORY      │   .where(pred).fetch()                    │
├──────────────┼───────────────────────────────────────────┤
│ DYNAMIC      │ BooleanBuilder pred = new BooleanBuilder()│
│ PREDICATES   │   pred.and(q.name.containsIgnoreCase(...))│
│              │   pred.and(q.price.goe(min))              │
├──────────────┼───────────────────────────────────────────┤
│ SPRING DATA  │ extend QuerydslPredicateExecutor<T>       │
│ INTEGRATION  │ repo.findAll(predicate, pageable)         │
├──────────────┼───────────────────────────────────────────┤
│ LIMITATION   │ JPQL backend - no window functions/CTEs   │
│              │ Use JOOQ for complex native SQL            │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "QueryDSL = type-safe JPQL via Q classes. │
│              │ BooleanBuilder for dynamic predicates.    │
│              │ QuerydslPredicateExecutor for Spring Data."│
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Q classes (generated by APT) enable type-safe field references:
   `QProduct.product.price.goe(100)` vs `"p.price >= :min"` string
2. `BooleanBuilder` is the key for dynamic predicates:
   `pred.and(condition)` only if condition is not null
3. QueryDSL-JPA generates JPQL, not SQL - same limitations as JPQL
   (no window functions); use JOOQ for complex SQL queries

**Interview one-liner:** QueryDSL generates `Q`-prefixed meta-model
classes from JPA entities via APT, enabling type-safe JPQL query
composition. `BooleanBuilder` composes dynamic predicates fluently.
`QuerydslPredicateExecutor<T>` integrates with Spring Data's
`findAll(Predicate, Pageable)`. QueryDSL-JPA generates JPQL (not SQL);
same JPQL limitations apply (no window functions, no CTEs).

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Moving validation
from runtime to compile time is a high-value engineering
practice ("shift left"). QueryDSL moves query schema
validation from runtime (`ColumnNotFoundException`) to
compile time (`does not compile`). The same principle:
OpenAPI client generation (Swagger Codegen) moves HTTP
API shape validation from runtime (`HttpClientException`)
to compile time. Protobuf/gRPC moves message format validation
from runtime (JSON parse error) to compile time. Every time
you replace a stringly-typed interface (SQL string, HTTP URL
string, JSON key string) with a typed meta-model, you shift
an entire class of errors from production to development.
The cost: a code generation step. The benefit: runtime
failures eliminated for that class of errors. QueryDSL/JOOQ
for SQL, Feign/Retrofit for HTTP, Protobuf for serialization.

---

### 💡 The Surprising Truth

QueryDSL-JPA translates your type-safe Java code back into
JPQL - and then Hibernate translates that JPQL into SQL.
So your `QProduct.product.price.goe(new BigDecimal("100"))`
becomes `SELECT p FROM Product p WHERE p.price >= ?1` in
JPQL, which becomes `SELECT p.* FROM products p WHERE p.price >= 100.00`
in SQL. There are TWO layers of translation, not one.
This means: the JPQL generated by QueryDSL is subject to all
JPQL limitations and Hibernate query optimizations. QueryDSL
cannot generate a `SELECT FOR UPDATE SKIP LOCKED` query because
JPQL doesn't support it. QueryDSL cannot generate a CTE because
JPQL doesn't support CTEs. QueryDSL is powerful within the
JPQL boundary, but it is NOT a replacement for SQL when
SQL features are required. The architectural decision:
"Does this query fit within JPQL semantics?" If yes:
QueryDSL. If no: JOOQ or Spring JDBC.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **SET UP** QueryDSL in a Maven/Gradle project with
   APT configuration and verify Q classes are generated
2. **WRITE** a dynamic search query using `BooleanBuilder`
   with optional filters mapped to QueryDSL predicates
3. **INTEGRATE** with Spring Data via `QuerydslPredicateExecutor`
   for paginated, filtered queries
4. **EXPLAIN** the difference between QueryDSL and JOOQ
   (JPQL vs native SQL backend)
5. **COMPARE** QueryDSL vs Spring Data Specifications
   and explain when to choose each

---

### 🎯 Interview Deep-Dive

**Q1: When would you choose QueryDSL over Spring Data
Specifications for dynamic filtering?**
_Why they ask:_ Tests practical Spring Data JPA expertise.
_Strong answer includes:_

- Both solve the same problem; main differentiators:
  (1) QueryDSL: more concise predicate syntax
  (`q.price.goe(100)` vs `cb.greaterThanOrEqualTo(root.get("price"), 100)`)
  (2) Specifications: no code generation step; pure Spring Data JPA
  (3) QueryDSL: joins and path navigation more readable
  (`q.category.supplier.name.eq(...)` vs nested `Join` in Criteria)
- Team familiarity is the deciding factor for simple cases
- QueryDSL wins for complex joins; Specifications win for simple filters
  where you don't want APT in the build pipeline
- Either way: don't use both in the same project

**Q2: A QueryDSL query on a large table is slow. How do you diagnose?**
_Why they ask:_ Tests understanding of underlying execution.
_Strong answer includes:_

- QueryDSL generates JPQL; JPQL generates SQL
- Enable `logging.level.org.hibernate.SQL=DEBUG` to see the SQL
- Check the EXPLAIN PLAN for the generated SQL (PostgreSQL: `EXPLAIN ANALYZE`)
- Common issues: missing index on filter column; Cartesian product
  from missing JOIN ON condition; fetching all columns (SELECT p.\*)
  when only a few needed -> use `Projections.constructor(DTO.class, ...)` to select specific fields
- QueryDSL limitation: cannot hint the DB optimizer directly;
  for index hints or `FOR UPDATE SKIP LOCKED`: fall back to native SQL
