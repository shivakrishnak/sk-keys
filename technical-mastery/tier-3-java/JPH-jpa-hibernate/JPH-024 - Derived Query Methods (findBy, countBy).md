---
id: JPH-024
title: "Derived Query Methods (findBy, countBy)"
category: JPA & Hibernate
tier: tier-3-java
folder: JPH-jpa-hibernate
difficulty: ★★☆
depends_on: JPH-014, JPH-016, JPH-023
used_by: JPH-025, JPH-030
related: JPH-036, JPH-043
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
nav_order: 24
permalink: /technical-mastery/jpa-hibernate/derived-query-methods/
---

⚡ **TL;DR** - Spring Data parses repository method names
to auto-generate JPQL at startup. `findByEmailAndStatus`
becomes `SELECT e FROM Entity e WHERE e.email=? AND e.status=?`.
Works well for 1-3 conditions; use `@Query` for complex
queries. Method names over 5 conditions become unreadable
and should be replaced with `@Query` or Specifications.

| #024            | Category: JPA & Hibernate                  | Difficulty: ★★☆ |
| :-------------- | :----------------------------------------- | :-------------- |
| **Depends on:** | JPQL, CrudRepository/JpaRepository, @Query |                 |
| **Used by:**    | Pagination/Sorting, DTO Projections        |                 |
| **Related:**    | Criteria API, Spring Data Specifications   |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Without derived query methods, every query on a repository
requires either a full JPQL `@Query` string or direct
`EntityManager` usage. For simple lookups like "find user
by email" or "count products by category", the developer
must write `@Query("SELECT u FROM User u WHERE u.email = :email")`.
This is verbose for simple, common patterns.

**THE BREAKING POINT:**
An application with 50 entity types, each needing 5-10
standard finder methods, requires 250-500 `@Query`
string definitions - a lot of JPQL for simple conditions.

**THE INVENTION MOMENT:**
Spring Data's method name parser reads repository method
signatures and generates JPQL automatically. `findByEmail(String email)`
generates `SELECT u FROM User u WHERE u.email = :email`
and binds the parameter. Zero JPQL required for standard
cases.

---

### 📘 Textbook Definition

**Derived query methods** are Spring Data repository
methods whose JPQL queries are automatically generated
at application startup by parsing the method name.
Spring Data's `PartTree` parser splits the method name
into subject (what to do: `find`, `count`, `exists`,
`delete`) and predicate (conditions: `By`, `And`, `Or`,
comparison keywords).

Method name structure:

```
[Subject][By][Property][Operator][And/Or][Property]...
  find      By  Email    Contains  And    Status
  count     By  Price    Between
  exists    By  Username
  delete    By  Status
```

---

### ⏱️ Understand It in 30 Seconds

**One line:** Name a repository method with `findBy` +
field names and Spring Data generates the JPQL for you.

**One analogy:**

> Derived query methods are like ordering coffee by
> description: "I want a large, oat-milk, one-shot latte
> with no sugar". The barista (Spring Data) translates
> your description into the exact drink recipe (JPQL).
> You don't write the recipe - you just describe what
> you want in a standard language.

**One insight:** Method names are compiled into JPQL at
startup - invalid field names or unsupported operators
cause an error at application startup, not at runtime.
This is actually an advantage over `@Query` strings
(which fail at first execution). If the application
starts, the derived query methods are valid.

---

### 🔩 First Principles Explanation

**METHOD NAME PARSING RULES:**

```
Subject keywords:
  find...By, read...By, get...By, query...By, stream...By
  count...By
  exists...By
  delete...By, remove...By

Comparison keywords:
  (none)          = equal (default)
  Not             = not equal
  Like            = LIKE (use %)
  NotLike         = NOT LIKE
  StartingWith    = LIKE 'value%'
  EndingWith      = LIKE '%value'
  Containing      = LIKE '%value%'
  IgnoreCase      = UPPER comparison
  Between         = BETWEEN x AND y
  LessThan        = <
  LessThanEqual   = <=
  GreaterThan     = >
  GreaterThanEqual = >=
  IsNull / Null   = IS NULL
  IsNotNull / NotNull = IS NOT NULL
  True            = = true
  False           = = false
  In              = IN (collection)
  NotIn           = NOT IN (collection)
  OrderBy         = ORDER BY (appended at end)
```

**NESTED PROPERTY TRAVERSAL:**

```java
// Traverses @ManyToOne relationship:
findByCategory_Name(String catName)
// JPQL: WHERE e.category.name = :catName
// SQL: JOIN categories c ON e.cat_id=c.id WHERE c.name=?

// Two levels deep:
findByCategory_Parent_Name(String name)
// JPQL: WHERE e.category.parent.name = :name
```

**CORE INVARIANTS:**

1. Method names are parsed at startup via Spring Data's
   `PartTree` - invalid names cause `PropertyReferenceException`
   at startup
2. Field names in method names are Java field names (not
   column names), same as JPQL
3. Use `_` to escape ambiguity in nested property traversal
   (e.g., `findByAddressCity` vs `findByAddress_City`)
4. The `OrderBy` suffix only works without `Pageable`;
   use `Pageable` with `Sort` for dynamic ordering
5. The `Top` and `First` keywords limit results:
   `findTop5ByStatus` = JPQL `... LIMIT 5`

---

### 🧪 Thought Experiment

**AMBIGUITY IN PROPERTY TRAVERSAL:**

```java
// Entity with: String addressCity and Address address (Address.city)
findByAddressCity(String city)
// Spring Data tries: property "addressCity" first
// If no such property: property "address.city"
// Both valid on this entity -> AMBIGUOUS!

// Fix: use _ to force traversal boundary:
findByAddress_City(String city)
// Explicitly: address.city (navigates @ManyToOne)
```

**THE INSIGHT:** Method names involving nested entities
should always use `_` to make the traversal explicit
and prevent ambiguity errors.

---

### 🧠 Mental Model / Analogy

> Spring Data's method name parser is like a smart GPS
> that converts spoken directions ("go left at the big
> red building, then right at the coffee shop") into
> precise turn-by-turn route instructions. The "spoken
> directions" are the method name keywords. The "turn-by-turn
> instructions" are the JPQL query. The GPS (Spring Data)
> handles the translation at startup so you don't need
> to write the instructions manually.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Name your repository method using Spring Data's naming
convention and the query is written for you. No JPQL
required.

**Level 2 - How to use it (junior developer):**

```java
List<User> findByEmail(String email);
Optional<User> findByEmailAndStatus(String email, String status);
long countByStatus(String status);
boolean existsByEmail(String email);
List<Product> findByPriceBetween(BigDecimal min, BigDecimal max);
List<Product> findTop5ByOrderByPriceDesc();
List<Product> findByNameContainingIgnoreCase(String term);
```

**Level 3 - How it works (mid-level engineer):**
At startup, `PartTreeJpaQuery` parses the method name into
a `PartTree` AST. The AST is converted to JPQL using the
entity metadata (Java field names, association paths).
The JPQL is stored and reused for all subsequent calls.
Parameters are bound by position, matching the parameter
order in the method signature.

**Level 4 - Why it was designed this way (senior/staff):**
The method name convention is a domain-specific language
(DSL) for expressing data access patterns in Java syntax.
The DSL is intentionally limited to prevent complex queries
(JOINs, subqueries) from being expressed as method names -
these should use `@Query` or Specifications for readability.
The convention also makes repository methods self-documenting:
the method signature IS the documentation of the query's
intent.

**Level 5 - Mastery (distinguished engineer):**
Derived query methods with deep navigation chains
(`findByOrder_Customer_Address_City`) generate multi-level
JOINs in SQL. Each `_` traversal adds a SQL JOIN. For
performance, understanding which derived method generates
what SQL is critical. A method like
`findByOrder_Customer_Memberships_Type` traverses three
levels and potentially generates multiple JOINs with
collection traversal, leading to Cartesian products.
At this complexity, replacing with `@Query` and explicit
JOIN FETCH is more readable and controllable.

---

### ⚙️ How It Works (Mechanism)

**METHOD NAME TO JPQL:**

```
findByEmailAndStatusOrderByCreatedAtDesc(String email,
  String status)
    |
    v
[ PartTree parsing: ]
    subject = "find"
    predicate = [{field="email", op=EQUAL},
                 {field="status", op=EQUAL}]
    orders = [{field="createdAt", dir=DESC}]
    |
    v
[ JPQL generation: ]
    "SELECT u FROM User u
     WHERE u.email = ?1
     AND u.status = ?2
     ORDER BY u.createdAt DESC"
    |
    v
[ Parameter binding at call time: ]
    ?1 = email argument
    ?2 = status argument
```

**STARTUP VALIDATION:**

```
Application context initializing:
    UserRepository.findByEmailAndStatus -> parse method
      name
    -> "email" field: found on User entity
    -> "status" field: found on User entity
    -> JPQL generated and cached
    -> SUCCESS (application starts)

    UserRepository.findByEmailAddress -> parse method name
    -> "emailAddress" field: NOT found on User entity
    -> PropertyReferenceException: No property
      "emailAddress"
       found for type User
    -> APPLICATION FAILS TO START (caught early!)
```

---

### 🔄 The Complete Picture - End-to-End Flow

```java
// Repository:
Optional<Product> findByNameAndStatus(
    String name, String status);

// Spring Data generates JPQL at startup:
// "SELECT p FROM Product p WHERE p.name = ?1
//  AND p.status = ?2"

// Service call:
productRepo.findByNameAndStatus("Widget", "ACTIVE");

// SQL generated:
// SELECT p.id, p.name, p.price, p.status, ...
// FROM products p
// WHERE p.name = 'Widget' AND p.status = 'ACTIVE'
// (with bound parameters via PreparedStatement)
```

---

### 💻 Code Example

**Example 1 - Common derived query patterns:**

```java
@Repository
public interface ProductRepository
        extends JpaRepository<Product, Long> {

    // Equality
    Optional<Product> findBySlug(String slug);

    // AND condition
    List<Product> findByStatusAndCategory(
        String status, String category);

    // OR condition
    List<Product> findByStatusOrFeatured(
        String status, boolean featured);

    // Range
    List<Product> findByPriceBetween(
        BigDecimal min, BigDecimal max);

    // Null check
    List<Product> findByDiscountPriceIsNull();

    // Like
    List<Product> findByNameContainingIgnoreCase(
        String term);

    // Top N
    List<Product> findTop10ByStatusOrderByViewsDesc(
        String status);

    // Count
    long countByStatus(String status);

    // Exists
    boolean existsBySlug(String slug);

    // Delete
    void deleteByStatus(String status);

    // Nested property traversal:
    List<Product> findByCategory_Name(String catName);
}
```

**Example 2 - BAD: method name too complex:**

```java
// BAD: this method name is a bug magnet
List<Order> findByCustomer_EmailAndStatusInAndTotalGreaterThanEqualAndCreatedAtBetweenOrderByCreatedAtDesc(
    String email, List<String> statuses,
    BigDecimal minTotal, LocalDate from, LocalDate to);
// Impossible to review; error-prone to write
// Any field rename breaks silently at startup

// GOOD: use @Query for complex conditions
@Query("SELECT o FROM Order o " +
       "JOIN o.customer c " +
       "WHERE c.email = :email " +
       "AND o.status IN :statuses " +
       "AND o.total >= :minTotal " +
       "AND o.createdAt BETWEEN :from AND :to " +
       "ORDER BY o.createdAt DESC")
List<Order> findComplexOrders(
    @Param("email") String email,
    @Param("statuses") List<String> statuses,
    @Param("minTotal") BigDecimal minTotal,
    @Param("from") LocalDate from,
    @Param("to") LocalDate to);
```

**Example 3 - Derived delete (transactional required):**

```java
// Spring Data generates: DELETE FROM products WHERE status=?
// @Transactional is required; Spring Data does NOT add it
@Transactional
void deleteByStatus(String status);
// Returns void or long (count of deleted entities)
// IMPORTANT: this loads entities first, then calls
// em.remove() on each (N individual DELETEs)
// For bulk delete without loading: use @Modifying @Query
```

---

### ⚖️ Comparison Table

| Complexity                         | Method name  | @Query       | Criteria API |
| ---------------------------------- | ------------ | ------------ | ------------ |
| 1-2 conditions, simple types       | Best         | Overkill     | Overkill     |
| 3-5 conditions, no JOINs           | OK           | Better       | OK           |
| JOINs, subqueries, aggregations    | Not possible | Best         | Verbose      |
| Dynamic conditions (runtime built) | Not possible | Not possible | Best         |

---

### ⚠️ Common Misconceptions

| Misconception                                                      | Reality                                                                                                                                                                                                                                                                                  |
| ------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Derived query methods are validated at runtime"                   | Derived queries are parsed and validated at application startup. `PropertyReferenceException` is thrown at startup if a field name is wrong - not at first call.                                                                                                                         |
| "`findByStatus` and `findByStatus(String)` are different methods"  | Method names are the primary key for Spring Data query derivation. Parameter types are NOT part of the query derivation - only names. Two methods with same name but different parameter types on a Spring Data repository interface is a compilation error.                             |
| "The `_` separator in method names is required for all traversals" | `_` is only required to disambiguate when both a flat property and a nested property path could match. For unambiguous paths, Spring Data resolves traversal automatically (e.g., `findByAddressZipCode` if only `Address.zipCode` exists). Using `_` always is safer and more readable. |
| "`deleteBy` performs a single bulk DELETE SQL"                     | `deleteBy` in Spring Data loads all matching entities first (`findBy`), then calls `em.remove()` on each. For 1000 entities, this is 1 SELECT + 1000 DELETEs. For bulk delete, use `@Modifying @Transactional @Query("DELETE FROM ... WHERE ...")`.                                      |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: PropertyReferenceException at Startup**

**Symptom:** `org.springframework.data.mapping.PropertyReferenceException:
No property 'emailAddress' found for type 'User'` prevents
application startup.

**Root Cause:** Method name references a property that
does not exist on the entity class (typo, or field renamed
without updating the repository method name).

**Diagnostic:** The exception message names the missing
property. Check the entity class for the correct field name.

**Fix:** Rename the method to use the correct field name.
If the field was renamed, update all repository methods
that reference the old name - or use IDE refactoring to
rename the field (should update method names if named
correctly).

---

**Failure Mode 2: deleteBy Causing N+1 DELETEs**

**Symptom:** Deleting 1000 entities by status generates
1001 SQL statements (1 SELECT + 1000 DELETEs).

**Root Cause:** Spring Data's `deleteBy` implementation
calls `findBy` first (to load entities for JPA lifecycle
events and cascade), then `em.remove()` on each.

**Fix:** Use `@Modifying @Transactional @Query` for bulk
delete without entity loading:

```java
@Modifying
@Transactional
@Query("DELETE FROM Product p WHERE p.status = :status")
int deleteByStatusBulk(@Param("status") String status);
// Single DELETE SQL; bypasses @PreRemove and cascade
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[JPH-014 - JPQL]] - derived methods generate JPQL
- [[JPH-016 - CrudRepository and JpaRepository]] -
  derived methods are defined on the repository interface

**Builds On This (learn these next):**

- [[JPH-025 - Pagination and Sorting (Pageable, Sort)]] -
  add `Pageable` to derived methods for pagination
- [[JPH-030 - DTO Projections]] - return interface or
  class projections from derived methods

**Alternatives:**

- [[JPH-036 - Criteria API]] - type-safe dynamic queries
- [[JPH-043 - Spring Data Specifications]] - predicate-based
  dynamic query building

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ STRUCTURE    │ find/count/exists/deleteBy + properties  │
│              │ + And/Or + keywords                      │
├──────────────┼──────────────────────────────────────────┤
│ KEYWORDS     │ Between, LessThan, GreaterThan, Like,    │
│              │ Containing, StartingWith, In, IsNull,    │
│              │ IgnoreCase, OrderBy, Top/First           │
├──────────────┼──────────────────────────────────────────┤
│ TRAVERSAL    │ Use _ for nested: findByCategory_Name    │
│ SAFETY       │ (explicit traversal boundary)            │
├──────────────┼──────────────────────────────────────────┤
│ LIMIT        │ 1-3 conditions OK; 5+ -> use @Query      │
│              │ deleteBy loads then removes (N+1 deletes)│
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "Name = query: findByStatus generates    │
│              │ WHERE status=?. Validated at startup.    │
│              │ Use @Query for >3 conditions."           │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Method names are parsed at startup - invalid field
   names cause startup failure, not runtime errors
2. Use `_` for nested property traversal to avoid
   ambiguity: `findByCategory_Name` not `findByCategoryName`
3. `deleteBy` loads entities first then deletes each
   individually; use `@Modifying @Query DELETE` for
   bulk delete without entity loading

**Interview one-liner:** Spring Data derived query methods
parse repository method names at startup into JPQL.
`findByEmailAndStatus` generates `WHERE e.email=? AND e.status=?`.
Invalid field names fail at startup. Use `_` for nested
traversal (`findByCategory_Name`). Use `@Query` when
method names exceed 3-4 conditions or require JOINs and
aggregations. `deleteBy` loads entities before deleting;
use `@Modifying @Query` for true bulk delete.

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Convention over configuration

- when a naming convention expresses intent precisely,
  code generation from the convention eliminates boilerplate
  while preserving readability. Spring Data's method name
  DSL is a prime example: the method name IS the specification.
  The same principle appears in Rails ActiveRecord
  (`find_by_email_and_status`), Swift Core Data fetch
  predicates, and REST URL conventions (`/users/{id}/orders`).
  The convention reduces cognitive load when it matches
  the domain language naturally; it becomes an obstacle
  when the domain requires expressiveness beyond the
  convention's scope (at which point `@Query`, Specifications,
  or native SQL take over).

---

### 💡 The Surprising Truth

Spring Data generates JPQL from method names using the
entity's Java field names - NOT the database column names.
This is consistent with JPQL's entity-first design.
However, there is a subtle implication: if you rename
a Java field with `@Column(name="old_column")` (keeping
the same DB column), derived query methods must use the
new Java field name. A `findByOldFieldName()` after
renaming the Java field to `newFieldName` will fail at
startup with `PropertyReferenceException`, even though
the underlying database column is unchanged. The repository
method must be renamed to `findByNewFieldName()`. This
is the correct behavior (repository methods document the
domain model, not the schema), but it can surprise
developers who think of repositories as schema mappers.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **WRITE** derived query methods for: equality, range,
   IN clause, null check, case-insensitive LIKE, and
   nested property traversal
2. **EXPLAIN** why a `PropertyReferenceException` at
   startup is actually better than a runtime exception
   from a `@Query` string
3. **CHOOSE** between a derived method and `@Query` for
   5 different query scenarios with justification
4. **FIX** the N+1 delete issue by replacing `deleteByStatus`
   with a `@Modifying @Query` bulk DELETE
5. **DISAMBIGUATE** a nested property traversal by using
   `_` separator in the method name

---

### 🎯 Interview Deep-Dive

**Q1: How does Spring Data generate queries from method
names, and when are they validated?**
_Why they ask:_ Tests foundational Spring Data knowledge
and understanding of the startup-vs-runtime tradeoff.
_Strong answer includes:_

- Method names are parsed by `PartTree` at application
  startup via `RepositoryFactory`
- The parser splits the name into subject (`findBy`,
  `countBy`) and predicates (field names + operators)
- JPQL is generated from entity metadata (Java field
  names, not column names)
- Validation happens at startup: invalid field names
  throw `PropertyReferenceException` before the app
  starts - earlier than `@Query` strings (which fail
  at first execution)
- This makes derived query methods "safer" for simple
  cases: if the app starts, the queries are valid

**Q2: What is the performance difference between
deleteByStatus and a @Modifying @Query DELETE?**
_Why they ask:_ Tests awareness of ORM overhead in batch
operations.
_Strong answer includes:_

- `deleteByStatus(String status)`: Spring Data calls
  `findByStatus(status)` first (loads all matching entities
  into persistence context), then calls `em.remove()` on
  each entity individually -> 1 SELECT + N DELETE statements
- `@Modifying @Query("DELETE FROM Product p WHERE p.status = :s")`:
  single DELETE SQL, no entity loading, no persistence
  context involvement
- Use case for `deleteBy`: when `@PreRemove` callbacks
  or JPA cascade are needed (they require managed entities)
- Use case for `@Modifying DELETE`: bulk delete of large
  sets without lifecycle events (performance-critical)

**Q3: When would you use `findByCategory_Name` vs
`findByCategoryName`?**
_Why they ask:_ Tests understanding of nested property
traversal and disambiguation.
_Strong answer includes:_

- `findByCategoryName`: Spring Data tries to find a direct
  field called `categoryName` on the entity. If not found,
  it tries `category.name` (navigating the `@ManyToOne`).
  If both exist, `PropertyReferenceException` (ambiguous)
- `findByCategory_Name`: the `_` explicitly marks the
  traversal boundary: `category` is the field on the
  entity; `name` is the field on the related entity
- Best practice: always use `_` for nested traversal to
  make the navigation explicit and immune to ambiguity
  if a flat property with the same combined name is
  ever added to the entity
