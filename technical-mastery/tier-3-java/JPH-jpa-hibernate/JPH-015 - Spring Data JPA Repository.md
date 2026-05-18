---
id: JPH-015
title: Spring Data JPA Repository
category: JPA & Hibernate
tier: tier-3-java
folder: JPH-jpa-hibernate
difficulty: ★★☆
depends_on: JPH-011, JPH-012, JPH-014
used_by: JPH-023, JPH-024, JPH-025
related: JPH-016, JPH-030, JPH-043
tags:
  - java
  - database
  - jpa
  - spring
  - foundational
status: complete
version: 4
layout: default
parent: "JPA & Hibernate"
grand_parent: "Technical Mastery"
nav_order: 15
permalink: /technical-mastery/jpa-hibernate/spring-data-jpa-repository/
---

⚡ **TL;DR** - Spring Data JPA Repository eliminates CRUD boilerplate by generating
data-access implementations from plain Java interfaces at runtime.

| Relationship | IDs |
|---|---|
| Depends on | [[JPH-011 - EntityManager]], [[JPH-012 - Persistence Context]], [[JPH-014 - JPQL (Java Persistence Query Language)]] |
| Used by | [[JPH-023 - @Query (Spring Data JPA)]], [[JPH-024 - Derived Query Methods (findBy, countBy)]], [[JPH-025 - Pagination and Sorting (Pageable, Sort)]] |
| Related | [[JPH-016 - CrudRepository and JpaRepository]], [[JPH-030 - DTO Projections in Spring Data JPA]], [[JPH-043 - Spring Data Specifications]] |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Every entity needs a DAO class with the same `save`, `findById`, `delete`,
and `findAll` methods hand-written against `EntityManager`. Across 20 entities
that means 20 classes, each 80-100 lines of boilerplate. Every new entity
spawns another round of copy-paste error.

**THE BREAKING POINT:**
A developer adding `findByEmailAndActive(String email, boolean active)` must
write JPQL, bind parameters manually, and test the plumbing. The actual
business logic drowns in infrastructure code.

**THE INVENTION MOMENT:**
Spring Data (2011) introduced the Repository abstraction: declare a Java
interface extending `JpaRepository<Entity, ID>` and Spring generates a proxy
implementation at startup. CRUD methods appear for free; query methods are
derived from method names; custom queries use `@Query`.

**EVOLUTION:**
Spring Data 1.x provided basic CRUD and query-derivation. Spring Data 2.x
added reactive variants (`ReactiveCrudRepository`) and Kotlin extension
support. Spring Data 3.x introduced `ListCrudRepository` (returns `List`
instead of `Iterable`) and improved Jakarta Persistence 3 alignment.

---

### 📘 Textbook Definition

**Spring Data JPA Repository** is an interface-based abstraction provided by
Spring Data JPA that removes boilerplate data-access code. A developer
declares an interface extending one of the Spring Data repository markers
(`Repository`, `CrudRepository`, `PagingAndSortingRepository`, or
`JpaRepository`), optionally adds method signatures following naming
conventions or annotated with `@Query`, and Spring generates a JDK proxy
implementing those methods against the underlying JPA `EntityManager`.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Declare an interface, get a complete data-access layer - no
implementation required.

**One analogy:**
> A Spring Data Repository is like a contract with a staffing agency: write
> a job description (interface methods), and the agency supplies a fully
> qualified worker (generated proxy) at runtime. You never train the worker
> yourself.

**One insight:** The power is in what you do NOT write. Spring Data generates
the implementation from your interface signature - method names become SQL
queries, type parameters become table bindings.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. A repository is a pure interface - no implementation code belongs here
2. Type parameters `<T, ID>` bind the repository to exactly one entity
   class and its primary key type
3. Method names follow a grammar (`findBy`, `countBy`, `deleteBy` plus
   property paths plus conditions) that Spring Data parses into JPQL
4. The JPA `EntityManager` is the sole execution engine; the repository
   is a facade over it

**DERIVED DESIGN:**
Because Java interfaces carry no executable state, Spring generates a proxy
class at application startup via `SimpleJpaRepository` (the default
implementation). This proxy intercepts every method call and routes it to
JPQL, Criteria API, or native SQL as appropriate.

**THE TRADE-OFFS:**

**Gain:** Zero boilerplate CRUD; queries derived from method names; testable
without a real DB via Mockito or `@DataJpaTest`.

**Cost:** Query derivation fails silently on typos (only caught at startup);
complex queries still need `@Query`; generated queries may be suboptimal
without tuning.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

**Essential:** A repository must map domain operations (save, find, delete)
to relational storage operations.

**Accidental:** Writing the same `EntityManager.persist(entity)` block for
every entity class is accidental complexity. Spring Data removes it entirely.

---

### 🧪 Thought Experiment

**SETUP:** You have `User`, `Order`, and `Product` entities. You need CRUD
plus custom finders for each.

**WHAT HAPPENS WITHOUT Spring Data JPA Repository:**
You write three DAO classes, each injecting `EntityManager`, each repeating
the same try-catch-finally commit pattern. `findByEmail` means writing JPQL,
binding parameters, and casting the result - 15 lines per query method,
multiplied across all three DAOs.

**WHAT HAPPENS WITH Spring Data JPA Repository:**

```java
interface UserRepository
        extends JpaRepository<User, Long> {
    Optional<User> findByEmail(String email);
}
```

That is the entire data-access layer for `User`. Spring generates `findAll`,
`save`, `deleteById`, and the custom `findByEmail` automatically.

**THE INSIGHT:** The interface IS the specification. Spring Data treats it as
a DSL for data access. You describe WHAT you want; Spring decides HOW to
implement it.

---

### 🧠 Mental Model / Analogy

> A Spring Data Repository is like an ORM-aware compiler: your interface
> signature is source code; the generated proxy is the compiled artifact.
> You write types and method names; the compiler emits working data-access
> code.

- **Interface method** = high-level instruction
- **Generated proxy** = compiled SQL/JPQL
- **`EntityManager`** = execution engine
- **JPA entity class** = schema binding

Where this analogy breaks down: unlike a compiler, the proxy is generated at
JVM startup, not ahead-of-time - query errors surface at startup, not at
compile time.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Spring Data JPA Repository is a shortcut. Instead of writing code to save
and load things from a database, you write an interface and Spring writes the
code for you.

**Level 2 - How to use it (junior developer):**
Extend `JpaRepository<YourEntity, Long>`. You immediately get `save()`,
`findById()`, `findAll()`, `deleteById()`, and more. Add method signatures
like `findByLastName(String name)` for custom queries - Spring derives the
JPQL from the method name automatically.

**Level 3 - How it works (mid-level engineer):**
At startup, Spring scans for interfaces extending a repository marker. For
each, it creates a `SimpleJpaRepository` proxy backed by `EntityManager`.
Method names are parsed by `PartTreeJpaQuery` into a `PartTree` structure,
which compiles to JPQL. `@Query` methods bypass name parsing and execute the
annotation's JPQL or native SQL directly.

**Level 4 - Why it was designed this way (senior/staff):**
The Repository pattern (Domain-Driven Design) separates domain logic from
persistence mechanics. Spring Data formalises this by making the interface
the sole public surface - callers never touch `EntityManager` directly. This
lets you swap implementations (JPA to MongoDB to R2DBC) by changing the base
interface with zero caller changes. The JDK proxy approach avoids bytecode
generation (no Java agent needed) while still providing compile-time
interface checking.

**Level 5 - Mastery (distinguished engineer):**
At scale, repository abstractions introduce subtle risks: N+1 queries from
lazy collection traversal in callers, unbounded `findAll()` on large tables,
and derived queries that bypass index hints. Expert use means treating
`JpaRepository` as a thin veneer and pushing complex queries into `@Query`
with `JOIN FETCH`, Spring Data Specifications for dynamic filtering, or JOOQ
for read-heavy paths. Understand that `SimpleJpaRepository` wraps every write
method in `@Transactional(readOnly=false)` and every read in
`@Transactional(readOnly=true)` - overriding at the service layer requires
careful propagation mode selection to avoid silent transaction boundary
conflicts.

**Expert Thinking Cues:**
- Ask: "Is this query derivable, or am I encoding domain rules in a method
  name?" - if the latter, use a Specification or named query
- Watch: startup time grows linearly with repository count; each proxy
  validates query methods against the schema
- Know: `@NoRepositoryBean` stops Spring from creating a proxy for
  intermediate interfaces in your hierarchy

---

### ⚙️ How It Works (Mechanism)

Spring Data JPA repository processing has three phases:

**1. Scanning (startup)**
`@EnableJpaRepositories` triggers `JpaRepositoriesRegistrar`, which scans
the classpath for interfaces extending a Spring Data marker. Each is
registered as a `JpaRepositoryFactoryBean` in the application context.

**2. Proxy creation (startup)**
`JpaRepositoryFactory` creates a JDK dynamic proxy implementing the
repository interface. The proxy's invocation handler wraps a
`SimpleJpaRepository` instance that holds a reference to the `EntityManager`
for that persistence unit.

**3. Method resolution (request time)**
On each method call, the invocation handler looks up a `RepositoryQuery`:
- **Derived query:** name parsed by `PartTreeJpaQuery` to JPQL, then
  `EntityManager.createQuery()`
- **`@Query`:** JPQL or native SQL from annotation, executed directly
- **Built-in (`save`, `findById`):** delegated to `SimpleJpaRepository`
- **Custom fragment:** delegated to a user-supplied `Impl` class

**Concurrency note:** The generated proxy is a Spring singleton shared
across threads. The `EntityManager` it holds is a thread-bound proxy
injected by `SharedEntityManagerCreator` - each thread uses a separate
`EntityManager` instance from the connection pool, preventing cross-request
state leaks.

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
HTTP Request
    |
    v
[ Controller ]
    |  calls service method
    v
[ Service Layer ]
    |  calls repository method    <- YOU ARE HERE
    v
[ Repository Interface (proxy) ]
    |  method intercepted
    v
[ SimpleJpaRepository / PartTreeJpaQuery ]
    |  builds JPQL or delegates
    v
[ EntityManager ]
    |  executes via JDBC driver
    v
[ Relational Database ]
    |  returns ResultSet
    v
[ Hibernate result mapping ]
    |  rows -> entity objects
    v
[ Service / Controller ]
```

**FAILURE PATH:**
If a derived query method name is misspelled (e.g. `findByEmial`), Spring
throws `PropertyReferenceException` at application context startup - the
application fails to start. This is intentional: broken queries never reach
production.

**WHAT CHANGES AT SCALE:**
- `findAll()` on a 10M-row table loads all rows into the JVM heap; replace
  with `findAll(Pageable)`
- Derived queries with multiple `And`/`Or` clauses generate verbose JPQL;
  verify with `spring.jpa.show-sql=true`
- Under high concurrency, connection pool starvation surfaces as
  `HikariPool-1 - Connection is not available` errors

**CONCURRENCY & DISTRIBUTED IMPLICATIONS:**
Each HTTP thread gets a separate `EntityManager` via Spring's thread-local
binding. In distributed systems, repositories are always node-local;
cross-node coordination requires messaging or saga orchestration - a
repository cannot span service boundaries.

---

### 💻 Code Example

**BAD - Hand-rolling a DAO against EntityManager:**

```java
// 60+ lines of boilerplate repeated per entity
@Repository
public class UserDaoImpl implements UserDao {

    @PersistenceContext
    private EntityManager em;

    public User save(User user) {
        if (user.getId() == null) {
            em.persist(user);
            return user;
        }
        return em.merge(user);
    }

    public Optional<User> findById(Long id) {
        return Optional.ofNullable(
            em.find(User.class, id));
    }
    // ... repeated for every entity ...
}
```

**GOOD - Spring Data JPA Repository:**

```java
// The entire data-access layer for User
public interface UserRepository
        extends JpaRepository<User, Long> {

    // Derived query - no implementation needed
    Optional<User> findByEmail(String email);

    // Compound condition
    List<User> findByActiveAndRole(
        boolean active, String role);

    // Explicit JPQL for complex joins
    @Query("""
        SELECT u FROM User u
        LEFT JOIN FETCH u.orders o
        WHERE u.active = true
        AND SIZE(o) > :minOrders
        """)
    List<User> findActiveWithOrders(
        @Param("minOrders") int minOrders);

    // Pagination built in
    Page<User> findByActive(
        boolean active, Pageable pageable);
}
```

```java
// Usage in service layer
@Service
@RequiredArgsConstructor
public class UserService {

    private final UserRepository users;

    public Page<User> listActive(int page) {
        return users.findByActive(
            true,
            PageRequest.of(page, 20,
                Sort.by("lastName")));
    }
}
```

**How to test / verify correctness:**

```java
@DataJpaTest // in-memory H2, auto-rollback
class UserRepositoryTest {

    @Autowired
    UserRepository users;

    @Test
    void findByEmail_returnsUser() {
        users.save(
            new User("alice@example.com"));
        Optional<User> found =
            users.findByEmail(
                "alice@example.com");
        assertThat(found).isPresent();
    }
}
```

---

### ⚖️ Comparison Table

| Approach | Boilerplate | Query flexibility | Testability | Best for |
|---|---|---|---|---|
| `JpaRepository` | None | Medium (derived + `@Query`) | `@DataJpaTest` | Standard CRUD + simple queries |
| Direct `EntityManager` | High | Maximum | Manual mocking | Complex multi-step persistence |
| Spring JDBC Template | Medium | High (raw SQL) | Easy | Read-heavy, stored procedures |
| JOOQ | Low | Maximum (type-safe SQL) | Easy | Complex SQL, DSL-preferred teams |
| MyBatis | Medium | High (XML/annotation SQL) | Medium | Legacy SQL, DBA-owned queries |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Spring Data generates code at compile time" | It creates JDK dynamic proxies at application startup. No source generation occurs unless you add an annotation processor such as Querydsl's APT. |
| "Derived query methods are validated at compile time" | Method names are parsed at startup. A typo causes `PropertyReferenceException` when the Spring context loads, not during `javac`. |
| "`save()` always inserts a new row" | `SimpleJpaRepository.save()` calls `persist()` for new entities (null/zero ID) and `merge()` for detached ones. The entity state drives the operation. |
| "Repository methods are always transactional" | `SimpleJpaRepository` applies `@Transactional(readOnly=true)` to reads and `@Transactional` to writes by default, but the service-layer transaction takes precedence via propagation. Always define transaction boundaries at the service layer. |
| "`findAll()` is safe for any table" | It loads all matching rows into the JVM heap with no limit. Use `findAll(Pageable)` for any table with more than a few thousand rows in production. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: PropertyReferenceException at startup**

**Symptom:** Application fails to start with `No property 'emial' found for
type 'User'`.

**Root Cause:** Derived query method name contains a typo or references a
non-existent entity field.

**Diagnostic:**

```bash
grep "PropertyReferenceException" application.log
```

**Fix:**

```java
// BAD
Optional<User> findByEmial(String email); // typo

// GOOD
Optional<User> findByEmail(String email);
```

**Prevention:** Run `@DataJpaTest` integration tests in CI; query validation
fires at context load, catching this before deployment.

---

**Failure Mode 2: OutOfMemoryError from unbounded findAll()**

**Symptom:** `java.lang.OutOfMemoryError: Java heap space` during batch jobs
or report generation.

**Root Cause:** `findAll()` returns `List<Entity>` - loads all rows into a
single heap-allocated list.

**Diagnostic:**

```bash
# Heap dump: look for large List<Entity> instances
jmap -dump:format=b,file=heap.hprof <pid>
# Analyse in Eclipse MAT or VisualVM
```

**Fix:**

```java
// BAD
List<User> all = userRepository.findAll();
all.forEach(this::processUser);

// GOOD
Pageable page = PageRequest.of(0, 500);
Page<User> result;
do {
    result = userRepository.findAll(page);
    result.forEach(this::processUser);
    page = page.next();
} while (result.hasNext());
```

**Prevention:** Enforce `findAll(Pageable)` in code review for any table
known to exceed a configurable row threshold.

---

**Failure Mode 3: LazyInitializationException outside transaction**

**Symptom:** `org.hibernate.LazyInitializationException: could not initialize
proxy - no Session`.

**Root Cause:** A lazy collection (`@OneToMany`) is accessed after the
`EntityManager` closes - typically in the controller or serializer.

**Diagnostic:**

```properties
# Trace session lifecycle in logs
logging.level.org.hibernate.orm.jdbc=TRACE
```

**Fix:**

```java
// BAD - lazy collection accessed after session closes
User user = userRepository
    .findById(id).orElseThrow();
// Controller accesses user.getOrders() here - error

// GOOD - JOIN FETCH within transaction boundary
@Query("SELECT u FROM User u " +
       "LEFT JOIN FETCH u.orders " +
       "WHERE u.id = :id")
Optional<User> findWithOrders(
    @Param("id") Long id);
```

**Prevention:** Use DTO projections or `JOIN FETCH` to load required
associations before the transaction boundary closes. Avoid Open Session in
View for new projects.

---

**Failure Mode 4: Mass Assignment via save() (Security)**

**Symptom:** API callers can overwrite privileged fields (e.g. `role`,
`isAdmin`) by sending arbitrary JSON that gets deserialised into a JPA entity
and passed directly to `repository.save()`.

**Root Cause:** JPA `merge()` writes ALL fields; no field-level authorisation
is applied by default.

**Diagnostic:**

```bash
# Send a crafted request and inspect the DB after
curl -X PUT /users/42 \
  -d '{"id":42,"name":"Alice","role":"ADMIN"}'
```

**Fix:**

```java
// BAD - request body mapped directly to entity
@PutMapping("/users/{id}")
public User update(@RequestBody User user) {
    return userRepository.save(user);
}

// GOOD - use a DTO; copy only safe fields
@PutMapping("/users/{id}")
public User update(
        @PathVariable Long id,
        @RequestBody @Valid UpdateUserRequest r) {
    User user = userRepository
        .findById(id).orElseThrow();
    user.setName(r.getName()); // safe fields only
    return userRepository.save(user);
}
```

**Prevention:** Never map API request bodies directly to JPA entities. Always
use separate DTO/command classes for external input.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[JPH-011 - EntityManager]] - the execution engine behind every repository
- [[JPH-012 - Persistence Context]] - the unit-of-work repositories operate within
- [[JPH-014 - JPQL (Java Persistence Query Language)]] - query language generated by derived methods

**Builds On This (learn these next):**
- [[JPH-023 - @Query (Spring Data JPA)]] - explicit JPQL/native queries in repositories
- [[JPH-024 - Derived Query Methods (findBy, countBy)]] - deep-dive into method name grammar
- [[JPH-025 - Pagination and Sorting (Pageable, Sort)]] - handling large result sets safely

**Alternatives / Comparisons:**
- [[JPH-016 - CrudRepository and JpaRepository]] - choosing the right base interface
- [[JPH-043 - Spring Data Specifications]] - dynamic query building
- [[JPH-030 - DTO Projections in Spring Data JPA]] - efficient read models

---

### 📌 Quick Reference Card

```
+--------------------------------------------------+
| WHAT IT IS   | Interface-based data-access layer |
|              | generated at startup by Spring     |
+--------------------------------------------------+
| PROBLEM      | CRUD boilerplate per entity class  |
+--------------------------------------------------+
| KEY INSIGHT  | Interface = spec; proxy = impl     |
+--------------------------------------------------+
| USE WHEN     | Spring Boot app needs CRUD and     |
|              | simple query methods               |
+--------------------------------------------------+
| AVOID WHEN   | Complex batch ops, heavy SQL DSL,  |
|              | or non-JPA data store              |
+--------------------------------------------------+
| ANTI-PATTERN | findAll() on large tables; saving  |
|              | request body directly as entity    |
+--------------------------------------------------+
| TRADE-OFF    | Zero boilerplate vs. implicit      |
|              | query behaviour at runtime         |
+--------------------------------------------------+
| ONE-LINER    | extends JpaRepository<T, ID>       |
+--------------------------------------------------+
| NEXT EXPLORE | @Query, Specifications, JOOQ       |
+--------------------------------------------------+
```

**If you remember only 3 things:**
1. Extend `JpaRepository<Entity, ID>` - CRUD is free
2. Method names ARE queries - `findByEmailAndActive` generates JPQL
3. Never call `findAll()` without pagination on production-scale tables

**Interview one-liner:** Spring Data JPA Repository generates data-access
proxies from interface definitions, eliminating boilerplate CRUD while
letting you declare queries by method name or `@Query` annotation.

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Specify the WHAT in an interface; let
the framework implement the HOW. This inversion reduces coupling between
business logic and infrastructure, enabling substitution without caller
changes.

**Where else this pattern appears:**
- **MyBatis Mapper interfaces** - Java interfaces map to SQL XML without
  implementation classes; same interface-as-spec principle
- **Feign HTTP clients** - interfaces declare REST calls; Feign generates
  the HTTP client at startup
- **gRPC stubs** - protobuf generates both server skeletons and client stubs
  from a single IDL specification

**Industry applications:**
- E-commerce platforms use `findAll(Pageable)` to safely paginate product
  catalogs with millions of rows, avoiding heap exhaustion in listing APIs
- SaaS multi-tenant systems use Spring Data Specifications to build dynamic,
  tenant-scoped queries without string-concatenated SQL, preventing SQL
  injection at the query-construction layer

---

### 💡 The Surprising Truth

Most developers believe the repository abstraction exists primarily for
testability. The actual primary motivation was **polyglot persistence**:
Spring Data's unified repository interface lets teams switch from JPA to
MongoDB, Cassandra, or Redis by changing one import - the service layer is
unaware of the change. `JpaRepository` is just one of over a dozen Spring
Data `Repository` implementations spanning SQL, NoSQL, search engines, and
key-value stores.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN** why `SimpleJpaRepository.save()` calls `persist()` for new
   entities and `merge()` for detached ones, and describe the persistence
   context state difference after each call
2. **DEBUG** a `LazyInitializationException` by identifying the session
   boundary and choosing between `JOIN FETCH`, DTO projection, or
   `@Transactional` scope adjustment
3. **DECIDE** when derived query methods are sufficient versus when `@Query`,
   Specifications, or JOOQ are more appropriate, citing the specific
   complexity threshold for each transition
4. **BUILD** a paginated, sorted repository query using `JpaRepository`,
   `Pageable`, and `@Query` with `@Param`, plus a `@DataJpaTest` that
   verifies correct results and no N+1 queries
5. **EXTEND** a repository with a custom implementation fragment by creating
   `UserRepositoryCustom` and `UserRepositoryCustomImpl`, and explain how
   Spring Data discovers and wires the fragment via the `Impl` suffix
   convention

---

### 🧠 Think About This Before We Continue

**Question 1 (TYPE B - Scale):** Your `UserRepository.findAll()` works fine
in development with 500 rows but causes `OutOfMemoryError` in production with
8 million rows. What are three distinct layers of defence (at the repository,
service, and infrastructure level) you would add to prevent this across all
repositories in the codebase?

*Hint:* Look at `Pageable`, `Stream<T>` return types in Spring Data, JVM heap
metrics, and database-level query timeout settings.

**Question 2 (TYPE C - Design Trade-off):** Spring Data generates queries
from names like `findByFirstNameAndLastNameAndActiveAndRoleIn`. At what
complexity threshold does query derivation become a liability rather than an
asset, and what would you use instead?

*Hint:* Consider `@Query`, Spring Data Specifications (`Specification<T>`),
and QueryDSL - what does each add and at what complexity cost?

**Question 3 (TYPE G - Hands-On Challenge):** Create a `ProductRepository`
that: (a) returns a paginated list of active products sorted by price; (b)
supports dynamic filtering by optional category and price range without string
concatenation; and (c) loads the product's `Category` association in a single
query. Write the interface, the relevant `@Query` or Specification, and a
`@DataJpaTest` that verifies no N+1 queries occur.

*Hint:* Explore `JpaSpecificationExecutor`, `JOIN FETCH` in `@Query`, and
Hibernate's SQL log (`spring.jpa.show-sql=true`) to count actual queries.

---

### 🎯 Interview Deep-Dive

**Q1: What is a Spring Data JPA Repository and how does Spring implement it
at runtime?**

*Why they ask:* Tests whether the candidate understands the framework
mechanism, not just how to use the annotation.

*Strong answer includes:*
- Interface extends `JpaRepository` (or another marker)
- Spring creates a JDK dynamic proxy via `JpaRepositoryFactory` at startup
- Proxy delegates to `SimpleJpaRepository` backed by the `EntityManager`
- Derived method names parsed at startup by `PartTreeJpaQuery`

---

**Q2: A colleague writes `findByFirstName` but accidentally types
`findByFirstNam`. What happens and when?**

*Why they ask:* Probes understanding of startup-time validation vs. runtime
failure.

*Strong answer includes:*
- `PropertyReferenceException` thrown at application context startup
- Not a compile-time error - Java sees a valid interface method signature
- Prevents broken queries from ever reaching production - a deliberate design
- Caught by `@DataJpaTest` integration tests in CI before deployment

---

**Q3: You call `userRepository.findAll()` in a nightly batch job. The job
crashes with OutOfMemoryError in production. Walk me through diagnosing and
fixing this.**

*Why they ask:* Tests production awareness and pagination knowledge.

*Strong answer includes:*
- `findAll()` returns `List<User>` - loads all rows into the JVM heap at once
- Fix: use `findAll(Pageable)` in a loop or `Stream<User>` with query hints
- For bulk updates, prefer `@Modifying @Query` to avoid loading entities
- Add heap monitoring (JVM metrics, GC logs) to detect pressure before crash

---

**Q4: How would you add a custom query method that cannot be expressed as a
derived method name or `@Query` annotation?**

*Why they ask:* Tests knowledge of the repository fragment pattern - a
senior-level Spring Data concept.

*Strong answer includes:*
- Create `UserRepositoryCustom` interface with the method signature
- Implement `UserRepositoryCustomImpl` using `EntityManager` or JOOQ
- Have `UserRepository extends JpaRepository<User, Long>, UserRepositoryCustom`
- Spring auto-discovers the `Impl` suffix class and wires it into the proxy
- The class name must be exactly `{RepositoryInterface}Impl`

---

**Q5: A `@DataJpaTest` passes but the production endpoint throws
`LazyInitializationException`. What went wrong?**

*Why they ask:* Tests understanding of transaction scope differences between
test and production environments.

*Strong answer includes:*
- `@DataJpaTest` wraps each test in a transaction that stays open throughout;
  lazy collections load fine within it
- In production, the `EntityManager` closes when the service-layer
  `@Transactional` method returns
- Controller or JSON serializer accesses the lazy collection after session
  closes
- Fix: use `JOIN FETCH`, DTO projection, or extend transaction scope
  deliberately; avoid Open Session in View in new systems