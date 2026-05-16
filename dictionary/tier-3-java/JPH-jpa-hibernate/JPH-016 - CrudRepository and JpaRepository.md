---
id: JPH-016
title: CrudRepository and JpaRepository
category: JPA & Hibernate
tier: tier-3-java
folder: JPH-jpa-hibernate
difficulty: ★★☆
depends_on: JPH-011, JPH-013, JPH-014
used_by: JPH-020, JPH-023, JPH-028
related: JPH-015, JPH-025, JPH-029
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
nav_order: 16
permalink: /jpa-hibernate/crudrepository-jparepository/
---

# JPH-016 - CrudRepository and JpaRepository

⚡ **TL;DR** - `CrudRepository` provides 11 generic CRUD
operations; `JpaRepository` extends it with JPA-specific
features (batch operations, flush control, paging/sorting,
and `Specification` support). In Spring Data JPA, almost
all repositories should extend `JpaRepository`.

| #016            | Category: JPA & Hibernate                                                                   | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------------------------------------------------ | :-------------- |
| **Depends on:** | EntityManager, Entity Lifecycle, JPQL                                                       |                 |
| **Used by:**    | N+1 Problem, @EntityGraph, Spring Data JPA Auto-configuration                               |                 |
| **Related:**    | CrudRepository vs PagingAndSortingRepository vs JpaRepository, Criteria API, @Transactional |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Without Spring Data repositories, every persistence class
requires the same boilerplate: inject `EntityManager`,
write `findById()` with null check and `Optional` wrapping,
write `save()` that distinguishes persist from merge,
write `delete()` that loads the entity first (since
`em.remove()` requires a managed entity), write `findAll()`
with a JPQL query. This is 50-100 lines of identical code
repeated for each of 50+ entity types.

**THE BREAKING POINT:**
When every DAO class is identical except for the type
parameter, the abstraction has been lost. Developers copy-paste
the template and make subtle mistakes: forget to check for
null in `findById()`, return the wrong type from `save()`,
miss the `em.contains()` check before `em.remove()`. The
repetition also means every improvement to the template
(adding pagination, adding specifications) must be propagated
to all 50 DAOs.

**THE INVENTION MOMENT:**
Spring Data's repository abstraction generates the entire
DAO implementation at runtime based on a generic interface.
Declare `interface ProductRepository extends JpaRepository<Product, Long>` -
Spring Data generates the implementation, wires the
`EntityManager`, and provides the full CRUD API with
correct `persist()`/`merge()` logic, proper transactions,
and optional method-name-derived queries. Zero boilerplate.

---

### 📘 Textbook Definition

**`CrudRepository<T, ID>`** is a Spring Data interface that
provides 11 generic CRUD operations for entity type `T`
with primary key type `ID`: `save()`, `saveAll()`,
`findById()`, `existsById()`, `findAll()`, `findAllById()`,
`count()`, `deleteById()`, `delete()`, `deleteAllById()`,
`deleteAll()`.

**`JpaRepository<T, ID>`** extends `CrudRepository` via
`PagingAndSortingRepository` and adds JPA-specific methods:
`flush()`, `saveAndFlush()`, `saveAllAndFlush()`,
`deleteAllInBatch()`, `getById()` (returns reference proxy),
`findAll(Sort)`, `findAll(Pageable)`, and Spring Data JPA's
`Specification` support via `JpaSpecificationExecutor`.

Both interfaces are generic; Spring Data generates a
`SimpleJpaRepository` implementation at application startup
via JDK dynamic proxies. The generated implementation is
annotated with `@Repository` and `@Transactional`.

---

### ⏱️ Understand It in 30 Seconds

**One line:** `JpaRepository` is a Spring Data interface
that generates a full, transaction-aware DAO implementation
for any entity - no code required.

**One analogy:**

> `JpaRepository` is like a bank's ATM network. You don't
> write the ATM software - you just use the standard ATM
> interface (deposit, withdraw, balance). Spring Data
> provides the implementation behind the interface for every
> entity, just as every bank gets the same ATM network.

**One insight:** The key design decision in `save()` is
`isNew()` detection. If `@Id` is null/0 -> `em.persist()`.
If non-null -> `em.merge()`. For entities with pre-assigned
UUID IDs, every `save()` calls `merge()`, triggering a SELECT
before every INSERT. This is the most common `JpaRepository`
performance gotcha.

---

### 🔩 First Principles Explanation

**HIERARCHY:**

```
Repository (marker interface)
  |
  v
CrudRepository<T, ID>
  | save(), findById(), findAll(), count(),
  | delete(), deleteById(), existsById()
  v
PagingAndSortingRepository<T, ID>
  | findAll(Sort), findAll(Pageable)
  v
JpaRepository<T, ID>
  | flush(), saveAndFlush(), saveAllAndFlush()
  | getById() (reference proxy, no SELECT)
  | deleteAllInBatch() (bulk DELETE, bypasses cascade)
  | + JpaSpecificationExecutor for Specifications
```

**SAVE() DECISION LOGIC:**

```java
// SimpleJpaRepository.save():
public <S extends T> S save(S entity) {
    if (entityInformation.isNew(entity)) {
        em.persist(entity);
        return entity;  // entity IS the managed object
    } else {
        return em.merge(entity);
        // merge() returns NEW managed copy!
        // caller must use the RETURNED value
    }
}
```

**isNew() CHECK ORDER:**

1. Does entity implement `Persistable<ID>`? -> use `isNew()`
2. Does entity have an `@Version` field? -> new if version is null
3. Else: new if `@Id` is null (or 0 for primitives)

**CORE INVARIANTS:**

1. `save()` returns the managed entity; callers must use
   the return value when `merge()` is called
2. `deleteById()` loads the entity first (`em.find()`)
   then calls `em.remove()` - this triggers two SQL queries
3. `deleteAllInBatch()` generates `DELETE FROM table WHERE
id IN (...)` - bypasses cascade and `@PreRemove`
4. `getById()` returns a Hibernate proxy (no SQL); the
   SELECT fires only on first field access
5. `findAll()` loads all entities with no WHERE - dangerous
   on large tables; use `findAll(Pageable)` or a
   `@Query` with a condition

---

### 🧪 Thought Experiment

**SETUP:**
You have `Product` with a UUID primary key assigned in
the constructor: `this.id = UUID.randomUUID()`.

```java
public class Product {
    @Id
    private UUID id = UUID.randomUUID();
    // ...
}
```

**WHAT HAPPENS WITH repository.save(new Product(...)):**

1. `isNew()` checks `@Id` - it is non-null (UUID assigned
   in constructor)
2. `save()` calls `em.merge()` (not `em.persist()`)
3. `merge()` triggers a SELECT to check if the entity
   exists in the database
4. SELECT returns nothing (new entity, not yet in DB)
5. `merge()` then triggers an INSERT

**RESULT:** Every new `Product` INSERT requires a SELECT
first - 2 queries instead of 1.

**THE FIX:**

```java
// Option 1: implement Persistable<UUID>
@Entity
public class Product implements Persistable<UUID> {
    @Id
    private UUID id = UUID.randomUUID();

    @Transient
    private boolean isNew = true;

    @Override
    public boolean isNew() { return isNew; }

    @PostPersist
    @PostLoad
    void markNotNew() { this.isNew = false; }
}
```

**THE INSIGHT:** `JpaRepository.save()` design assumes
entities with non-null IDs are detached (need `merge()`).
UUID entities break this assumption. The fix is explicit
`isNew()` signalling via `Persistable`.

---

### 🧠 Mental Model / Analogy

> `JpaRepository` is a vending machine for CRUD operations.
> You insert the coin (entity type), press the button
> (save/find/delete), and get the result. The vending
> machine handles the wiring, transactions, and correct
> `EntityManager` calls internally. You never need to know
> how the machine works - just how to use the buttons.
>
> `JpaRepository` adds premium buttons to the standard
> `CrudRepository` machine: batch delete, flush control,
> paging with sorting.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
`JpaRepository` is an interface you extend to get free
CRUD methods for any entity: `save()`, `findById()`,
`findAll()`, `delete()`, and more. Spring generates the
implementation for you.

**Level 2 - How to use it (junior developer):**

```java
public interface ProductRepository
        extends JpaRepository<Product, Long> {

    // Method name derived queries:
    List<Product> findByCategory(String category);
    Optional<Product> findByName(String name);

    // Custom JPQL:
    @Query("SELECT p FROM Product p WHERE " +
           "p.price BETWEEN :min AND :max")
    List<Product> findInPriceRange(
        @Param("min") BigDecimal min,
        @Param("max") BigDecimal max);
}
```

No implementation needed. Spring Data generates it at startup.

**Level 3 - How it works (mid-level engineer):**
At startup, Spring Data's `JpaRepositoriesAutoConfiguration`
scans for `Repository` sub-interfaces. For each, it creates
a `SimpleJpaRepository` instance using JDK dynamic proxies.
The proxy intercepts all method calls: standard methods
(like `findById`) are routed to `SimpleJpaRepository`'s
built-in implementation; custom methods (like
`findByCategory`) are parsed into JPQL by the method name
parser or use the `@Query` value.

**Level 4 - Why it was designed this way (senior/staff):**
The repository abstraction (DDD pattern) separates the
domain layer from the persistence mechanism. By coding
to `JpaRepository<Product, Long>` instead of an `EntityManager`
directly, the domain model does not depend on JPA
implementation details. The repository can be swapped
for a MongoDB repository or an in-memory repository for
testing. This is why `CrudRepository` is in Spring Data
Commons (not Spring Data JPA) - the interface is persistence
mechanism agnostic.

**Level 5 - Mastery (distinguished engineer):**
`SimpleJpaRepository` applies `@Transactional` at the class
level with `readOnly=true`, then overrides write methods with
`@Transactional(readOnly=false)`. This means:
(1) all read operations run in a read-only transaction
(Hibernate can optimise: no dirty check, no flush, no
snapshot overhead); (2) write operations run in a
read-write transaction. Calling `findById()` from within
a service's `@Transactional(readOnly=true)` transaction
participates in the existing transaction with `REQUIRED`
propagation - the read-only hint from `SimpleJpaRepository`
has no effect because the outer transaction already exists.
This is a subtle interaction between transaction propagation
and read-only optimisation that affects performance in
read-heavy services.

**Expert Thinking Cues:**

- Ask: "Does `save()` call persist() or merge()?" - for
  UUID entities it calls merge() for all inserts; fix
  with `Persistable`
- Watch: `deleteAllInBatch()` bypasses `@PreRemove` and
  cascade; can leave orphan records if relationships are
  cascade-remove only at the JPA level
- Know: `getById()` (formerly `getOne()`) returns a proxy;
  the entity is not loaded until a field is accessed; call
  it outside a transaction and you get
  `LazyInitializationException` on first field access

---

### ⚙️ How It Works (Mechanism)

**Repository Proxy Generation:**

```
Application startup:
    |
    v
[ JpaRepositoriesRegistrar scans @EnableJpaRepositories ]
    |  or Spring Boot auto-configuration
    v
[ Finds: ProductRepository extends JpaRepository ]
    |
    v
[ RepositoryFactory creates proxy ]
    |  JDK dynamic proxy implementing ProductRepository
    |  delegate: SimpleJpaRepository<Product, Long>
    v
[ Method name parser runs ]
    |  findByCategory(String) -> JPQL query generated
    |  @Query methods -> JPQL string stored
    v
[ Proxy registered as Spring bean: productRepository ]

Request time:
    productRepository.findByCategory("electronics")
    |
    v
[ Proxy intercepts ]
    |  method = findByCategory
    v
[ Method resolver: custom JPQL method ]
    |  execute: "SELECT p FROM Product p WHERE p.category = :cat"
    v
[ SimpleJpaRepository delegates to EntityManager ]
    |  em.createQuery(jpql, Product.class)
    v
[ Return List<Product> ]
```

**CONCURRENCY / THREAD-SAFETY BEHAVIOR:**
The repository bean (the proxy) is thread-safe: it holds
no mutable state. The underlying `EntityManager` operations
use a transaction-scoped proxy (thread-safe). Multiple
threads calling `repository.findById(1L)` concurrently
each get their own `EntityManager` session.

---

### 🔄 The Complete Picture - End-to-End Flow

**SERVICE -> REPOSITORY -> DATABASE:**

```
ProductService.updatePrice(42L, 29.99)
    |  @Transactional
    v
[ JpaTransactionManager: new transaction ]
    |  new EntityManager bound to thread
    v
[ productRepository.findById(42L) ]
    |  SimpleJpaRepository.findById()
    |  em.find(Product.class, 42L)
    |  SELECT * FROM products WHERE id=42
    v
[ Product entity: MANAGED ]
    |  entity.setPrice(29.99)
    v
[ @Transactional method ends ]
    |  flush: UPDATE products SET price=29.99 WHERE id=42
    |  commit
    v
[ Entity becomes DETACHED ]
```

**FAILURE PATH:**
`repository.save(entity)` where entity has a non-null ID
that does not exist in the database causes `merge()` to
do a SELECT (no rows), then INSERT. If the INSERT violates
a constraint, `DataIntegrityViolationException` is thrown.
The transaction rolls back.

**WHAT CHANGES AT SCALE:**
`repository.findAll()` on a table with 10 million rows loads
ALL rows into memory. Always use `findAll(Pageable)` or
a `@Query` with a WHERE clause. Use `repository.findAll(Pageable.ofSize(1000))`
for batch processing.

---

### 💻 Code Example

**Example 1 - Standard repository definition:**

```java
@Repository
public interface ProductRepository
        extends JpaRepository<Product, Long> {

    // Derived query: findBy + field name
    List<Product> findByCategory(String category);

    // Multiple conditions
    List<Product> findByCategoryAndPriceGreaterThan(
        String category, BigDecimal price);

    // @Query for complex JPQL
    @Query("SELECT p FROM Product p " +
           "WHERE p.price BETWEEN :min AND :max " +
           "ORDER BY p.price ASC")
    List<Product> findInPriceRange(
        @Param("min") BigDecimal min,
        @Param("max") BigDecimal max);

    // Pagination
    Page<Product> findByCategory(
        String category, Pageable pageable);
}
```

**Example 2 - save() return value contract:**

```java
@Transactional
public Product updateName(Long id, String name) {
    Product p = productRepo.findById(id)
        .orElseThrow(ProductNotFoundException::new);

    p.setName(name);

    // Dirty checking handles the UPDATE automatically
    // No explicit save() needed when entity is MANAGED
    // But explicitly saving is also correct:
    Product saved = productRepo.save(p);
    // For a MANAGED entity, save() calls merge()
    // which returns the MANAGED copy (same object
    // since it's already managed in this session)
    return saved;
}
```

**Example 3 - Batch delete with deleteAllInBatch() caveats:**

```java
// BAD: deleteAllInBatch bypasses @PreRemove and cascade
List<Product> toDelete = productRepo
    .findByCategory("discontinued");
productRepo.deleteAllInBatch(toDelete);
// If Product has @OneToMany children with CascadeType.REMOVE,
// the cascade DOES NOT fire. Child rows remain -> FK violation

// GOOD: use deleteAll() for cascade-delete with events
productRepo.deleteAll(toDelete);
// deleteAll() calls em.remove() on each -> cascade fires
// (but N individual DELETE statements)
```

**Example 4 - UUID with Persistable fix:**

```java
@Entity
public class AuditEvent
        implements Persistable<UUID> {

    @Id
    private UUID id = UUID.randomUUID();

    @Transient
    private boolean isNew = true;

    private String action;
    private LocalDateTime timestamp =
        LocalDateTime.now();

    @Override
    public UUID getId() { return id; }

    @Override
    public boolean isNew() { return isNew; }

    @PostPersist
    @PostLoad
    void markNotNew() { this.isNew = false; }

    protected AuditEvent() {}
    public AuditEvent(String action) {
        this.action = action;
    }
}
// Now auditEventRepo.save(new AuditEvent("LOGIN"))
// calls persist() directly (no SELECT before INSERT)
```

---

### ⚖️ Comparison Table

| Repository                   | Extends                      | Key additions                                                  | Use case                       |
| ---------------------------- | ---------------------------- | -------------------------------------------------------------- | ------------------------------ |
| `CrudRepository`             | `Repository`                 | 11 CRUD methods                                                | Non-JPA (MongoDB, Redis, etc.) |
| `PagingAndSortingRepository` | `CrudRepository`             | `findAll(Sort)`, `findAll(Pageable)`                           | Any Spring Data with paging    |
| `JpaRepository`              | `PagingAndSortingRepository` | `flush()`, `saveAndFlush()`, `getById()`, `deleteAllInBatch()` | JPA/Hibernate applications     |

**When to use each:**

- Always use `JpaRepository` in Spring Data JPA projects
- Use `CrudRepository` in the interface contract if you
  want to keep the persistence layer abstraction (allows
  swapping to MongoDB later)
- Use `PagingAndSortingRepository` if you need paging
  but want to keep MongoDB compatibility

---

### ⚠️ Common Misconceptions

| Misconception                                                   | Reality                                                                                                                                                                                                                                          |
| --------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| "`repository.save()` always calls INSERT"                       | `save()` calls `isNew()` first. Non-null `@Id` -> `merge()` (SELECT + potential INSERT/UPDATE). Null `@Id` -> `persist()` (INSERT). For UUID entities with auto-assigned IDs, every `save()` calls `merge()` and triggers a SELECT first.        |
| "`deleteAllInBatch()` is always faster than `deleteAll()`"      | `deleteAllInBatch()` is faster (single DELETE SQL) but bypasses `@PreRemove` callbacks and JPA cascade. If your entity has cascade-delete relationships or `@PreRemove` logic, `deleteAllInBatch()` silently skips them, leaving orphan records. |
| "`findAll()` is safe for any table"                             | `findAll()` without a `Pageable` loads ALL rows. On a table with millions of rows, this causes `OutOfMemoryError`. Always use `findAll(Pageable)` or a `@Query` with pagination for production code.                                             |
| "`getById()` always loads the entity from the database"         | `getById()` returns a Hibernate proxy without hitting the database. The SELECT fires only when a field is accessed. If called outside a transaction, accessing the proxy later causes `LazyInitializationException`.                             |
| "Custom `@Query` methods in a repository are not transactional" | `SimpleJpaRepository` is annotated `@Transactional(readOnly=true)` at the class level. All repository methods (including custom `@Query` ones) run in a read-only transaction unless overridden with `@Modifying @Transactional`.                |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: SELECT Before Every INSERT for UUID Entities**

**Symptom:** Batch import of 10,000 entities takes 60 seconds;
SQL log shows alternating SELECT and INSERT pairs instead
of only INSERTs.
**Root Cause:** UUID entities have non-null `@Id` fields
assigned at construction time; `isNew()` returns false;
`save()` calls `merge()` which triggers a SELECT per entity.
**Diagnostic:**

```bash
spring.jpa.show-sql=true
# Count SELECT statements for inserts:
# If every INSERT has a preceding SELECT, UUID isNew() issue confirmed
spring.jpa.properties.hibernate.generate_statistics=true
# prepareStatementCount: should be N inserts
# if 2*N, merge() SELECT+INSERT pattern confirmed
```

**Fix:** Implement `Persistable<UUID>` with `@Transient isNew = true`
field and `@PostPersist` / `@PostLoad` to mark not-new.
**Prevention:** All entities with pre-assigned IDs (UUID,
business keys) must implement `Persistable` or use
`@Version` (null version = new entity for `isNew()`).

---

**Failure Mode 2: Orphan Records After deleteAllInBatch()**

**Symptom:** `DataIntegrityViolationException: foreign key
constraint violation` after `deleteAllInBatch()` on parent
entities. Child records (order items, comments) still exist
after parents are deleted.
**Root Cause:** `deleteAllInBatch()` issues a single
`DELETE FROM products WHERE id IN (...)` without invoking
JPA cascade or `@PreRemove` callbacks. Child records are
not deleted.
**Diagnostic:**

```bash
spring.jpa.show-sql=true
# deleteAllInBatch() shows single DELETE SQL
# deleteAll() shows N individual DELETE SQLs (correct for cascade)
```

**Fix:** Use `deleteAll(entities)` when cascade or
`@PreRemove` logic is required. Reserve `deleteAllInBatch()`
for tables with no JPA-level children.
**Prevention:** Document each repository method with
"cascade-safe" or "bulk delete only" annotation. Code review
checklist: `deleteAllInBatch()` must only be used on leaf
entities or when cascade is handled at the database level
(ON DELETE CASCADE).

---

**Failure Mode 3: @Modifying @Query Without Transaction**

**Symptom:** `TransactionRequiredException: Executing an
update/delete query` on a custom `@Query` UPDATE or DELETE
method.
**Root Cause:** Custom `@Modifying` queries require a
read-write transaction. `SimpleJpaRepository` runs in
`readOnly=true` by default; `@Modifying` alone is insufficient
without `@Transactional`.
**Diagnostic:**

```bash
logging.level.org.springframework.transaction=DEBUG
# Confirms: "no transaction in progress"
```

**Fix:**

```java
// BAD: @Modifying alone is insufficient
@Modifying
@Query("UPDATE Product p SET p.price = :price " +
       "WHERE p.id = :id")
void updatePrice(@Param("id") Long id,
                 @Param("price") BigDecimal price);

// GOOD: @Modifying + @Transactional
@Modifying
@Transactional
@Query("UPDATE Product p SET p.price = :price " +
       "WHERE p.id = :id")
void updatePrice(@Param("id") Long id,
                 @Param("price") BigDecimal price);
```

**Prevention:** Code review rule: `@Modifying` always paired
with `@Transactional`. Static analysis tools (Checkstyle,
SonarQube) can detect this.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[JPH-011 - EntityManager]] - `JpaRepository` wraps
  `EntityManager` operations; understanding persist/merge
  is required to understand save() behaviour
- [[JPH-013 - Entity Lifecycle (NEW, MANAGED, DETACHED, REMOVED)]] -
  `isNew()` determines which lifecycle transition `save()` triggers
- [[JPH-014 - JPQL (Java Persistence Query Language)]] -
  `@Query` annotation accepts JPQL strings

**Builds On This (learn these next):**

- [[JPH-020 - N+1 Problem]] - the most common performance
  issue in JpaRepository-based code
- [[JPH-023 - @EntityGraph]] - declarative fetch plans
  applied to repository methods
- [[JPH-028 - Spring Data JPA Auto-configuration]] - how
  Spring Boot wires repositories automatically

**Alternatives / Comparisons:**

- [[JPH-015 - CrudRepository vs PagingAndSortingRepository vs JpaRepository]] -
  detailed comparison of the hierarchy
- [[JPH-025 - Criteria API]] - type-safe programmatic
  alternative for dynamic queries
- [[JPH-029 - @Transactional]] - transaction management
  for repository methods

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Spring Data interface that generates a   │
│              │ full JPA DAO implementation at startup   │
├──────────────┼───────────────────────────────────────────┤
│ KEY METHODS  │ save(), findById(), findAll(Pageable),   │
│              │ delete(), deleteAllInBatch(), flush()    │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ save() -> isNew() -> null id = persist; │
│              │ non-null id = merge (SELECT + INSERT)   │
├──────────────┼───────────────────────────────────────────┤
│ TRAPS        │ UUID entity: save() always calls merge() │
│              │ Fix: implement Persistable<UUID>         │
│              │ deleteAllInBatch: bypasses cascade/events│
│              │ findAll(): OOM on large tables           │
├──────────────┼───────────────────────────────────────────┤
│ @Modifying   │ Must pair with @Transactional for UPDATE │
│              │ and DELETE @Query methods                │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "JpaRepository: Spring generates the DAO;│
│              │ save() calls persist or merge via isNew()│
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. `save()` uses `isNew()` to decide `persist()` vs `merge()`;
   UUID entities always call `merge()` (SELECT first) unless
   `Persistable` is implemented
2. `deleteAllInBatch()` is fast but bypasses JPA cascade
   and `@PreRemove` - only use on leaf entities
3. `@Modifying` queries need `@Transactional` - without it,
   UPDATE/DELETE `@Query` methods throw at runtime

**Interview one-liner:** `JpaRepository` extends `CrudRepository`
and `PagingAndSortingRepository` with JPA-specific operations
(batch delete, flush control). `save()` calls `isNew()`:
null ID -> `persist()`; non-null ID -> `merge()` (triggers
a SELECT). UUID entities with auto-assigned IDs always
call `merge()`, triggering a wasted SELECT per insert.
The fix is implementing `Persistable<UUID>` to override
`isNew()`.

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** The Repository pattern
(DDD) separates the domain model from the persistence
mechanism. Coding domain services to `CrudRepository`
interfaces (not `EntityManager` directly) makes the domain
testable with in-memory repositories and swappable to
different storage backends (MongoDB, Redis, JPA) without
changing the domain logic. This is the same principle
as depending on interfaces rather than implementations:
the domain service does not know or care how data is stored.

**Where else this pattern appears:**

- **Spring Data MongoDB** - `MongoRepository<Product, String>`
  provides the same 11 CRUD methods as `CrudRepository`
  for MongoDB documents; same interface, different storage
- **Spring Data Redis** - `RedisRepository` for Redis hash
  storage; same interface contract
- **Querydsl** - extends repository with type-safe predicate
  queries: `QuerydslPredicateExecutor<Product>` adds
  `findAll(Predicate)` to the `JpaRepository` interface

**Industry applications:**

- Microservices data layer isolation: each service has its
  own `JpaRepository` interface per aggregate root; no
  cross-service entity access; the interface boundary is
  enforced by the architecture
- Hexagonal architecture: repository interfaces in the
  domain layer; `JpaRepository` implementations in the
  infrastructure layer; domain depends on the interface,
  not the JPA implementation

---

### 💡 The Surprising Truth

`SimpleJpaRepository` - the generated implementation of
every `JpaRepository` - is annotated with
`@Transactional(readOnly=true)` at the class level.
This means `findById()`, `findAll()`, and all read methods
run in a read-only transaction even if you do not
`@Transactional` anything. The read-only hint tells
Hibernate to skip dirty checking and snapshot creation
for the loaded entities, and may tell the JDBC driver to
use a read-only database connection (useful with
read replica routing). Most Spring Boot developers have
never noticed this default read-only transaction on
every find operation.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **EXPLAIN** the `save()` isNew() decision tree including
   the UUID entity gotcha and the `Persistable` fix
2. **CHOOSE** between `deleteAll()` and `deleteAllInBatch()`
   and justify the choice based on cascade and event requirements
3. **DEBUG** a UUID entity insert that triggers a SELECT
   before every INSERT by reading the SQL log and tracing
   to the `merge()` call in `SimpleJpaRepository`
4. **WRITE** a repository with a `@Modifying @Transactional
@Query` bulk UPDATE and verify it works without triggering
   `TransactionRequiredException`
5. **APPLY** `findAll(Pageable)` with `Sort` for paginated
   reads and explain why `findAll()` without paging is
   dangerous on any table that could grow

---

### 🧠 Think About This Before We Continue

**Q1 (TYPE C - Design Trade-off):** Your service layer has
a method annotated `@Transactional(readOnly=true)` that
calls `productRepository.findById(id)`. What transaction
runs during `findById()`? Does the `readOnly=true` hint
from `SimpleJpaRepository`'s default apply? What is the
effective read-only status of the operation?
_Hint: With REQUIRED propagation (default), the service's
existing transaction is used. The outer transaction's
readOnly setting overrides the method-level readOnly hint.
If the outer is readOnly=true, that applies._

**Q2 (TYPE B - Scale):** A batch service processes 1 million
events by calling `eventRepository.save(new Event(...))` in
a loop with UUID IDs. After 100,000 iterations, the job is
running at 200 events/second (expected: 10,000/second).
What is the bottleneck and how would you fix it?
_Hint: UUID -> merge() -> 1 SELECT per event -> 2 DB round
trips per insert. Fix: Persistable<UUID> + SEQUENCE strategy
alternative + JDBC batch insert._

**Q3 (TYPE G - Hands-On):** Configure a Spring Boot
integration test that (1) measures query count per
`repository.save()` call for a UUID-based entity WITHOUT
Persistable, (2) then WITH Persistable, and asserts that
WITH Persistable reduces the query count from 2 to 1.
Use Hibernate statistics (`hibernate.generate_statistics=true`)
to count prepared statement executions.

---

### 🎯 Interview Deep-Dive

**Q1: Explain how `JpaRepository.save()` works and when
it calls `persist()` vs `merge()`.**
_Why they ask:_ Tests daily-use JPA knowledge; a common
source of production bugs (extra SELECTs, wrong entity
returned).
_Strong answer includes:_

- `save()` calls `entityInformation.isNew(entity)`:
  returns true if `@Id` is null/0 -> calls `persist()`
- Returns false if `@Id` is non-null -> calls `merge()`
- `merge()` returns a new managed copy; the input stays
  as-is; caller must use the returned value
- UUID gotcha: UUID assigned in constructor = non-null ID =
  `merge()` = SELECT before every INSERT
- Fix: implement `Persistable<UUID>` to override `isNew()`

**Q2: When would you use `deleteAllInBatch()` vs `deleteAll()`
and what are the risks of each?**
_Why they ask:_ Tests awareness of the cascade/event bypass
trap in batch delete operations.
_Strong answer includes:_

- `deleteAllInBatch()`: single DELETE SQL, fast, no cascade,
  no `@PreRemove` - use for leaf entities or when cascade
  is handled at database (ON DELETE CASCADE) level
- `deleteAll()`: calls `em.remove()` on each entity, triggers
  JPA cascade and `@PreRemove` callbacks, N individual
  DELETE statements - use when JPA-level cascade is needed
- Risk: using `deleteAllInBatch()` on an entity with
  `@OneToMany` children without database-level cascade
  leaves orphan records and may cause FK violations

**Q3: How does Spring Data generate the implementation
for a `@Query` method defined in a repository interface?**
_Why they ask:_ Tests understanding of Spring Data internals;
distinguishes senior candidates who know the framework
deeply.
_Strong answer includes:_

- At startup, `RepositoryFactory` scans the repository
  interface for methods with `@Query` annotations
- The JPQL string from `@Query` is stored as a
  `NamedQuery` equivalent in the proxy's method metadata
- When the method is called, the proxy intercepts,
  creates `em.createQuery(jpql, returnType)`, binds
  `@Param` parameters, and executes
- For `@Modifying` methods, `executeUpdate()` is called
  instead of `getResultList()`
- Method-name derived queries (without `@Query`) are
  parsed by `PartTree` into JPQL at startup and cached
