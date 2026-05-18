---
id: JPH-031
title: Hibernate Session vs EntityManager
category: JPA & Hibernate
tier: tier-3-java
folder: JPH-jpa-hibernate
difficulty: ★★☆
depends_on: JPH-011, JPH-012, JPH-013, JPH-014, JPH-026, JPH-028
used_by: JPH-033, JPH-034, JPH-038, JPH-045, JPH-049, JPH-058
related: JPH-036, JPH-052, JPH-057
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
nav_order: 31
permalink: /technical-mastery/jpa-hibernate/session-vs-entitymanager/
---

⚡ **TL;DR** - `EntityManager` is the JPA standard API
(interface in `jakarta.persistence`). `Session` is
Hibernate's proprietary extension that IMPLEMENTS
`EntityManager` and adds Hibernate-specific operations:
`session.saveOrUpdate()`, natural-id lookups, `byId()` /
`bySimpleNaturalId()`, `Filter`, `setReadOnly()`,
`doWork()`, and `setFlushMode()` directly. In Spring Boot
projects: use `EntityManager` for portability; unwrap to
`Session` only when you need Hibernate-specific features.

| #031            | Category: JPA & Hibernate                                                                                          | Difficulty: ★★☆ |
| :-------------- | :----------------------------------------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | EntityManager, Persistence Context, Entity Lifecycle, JPQL, @Transactional, HQL                                    |                 |
| **Used by:**    | First Level Cache, Second Level Cache, Optimistic Locking, Batch Processing, Hibernate Envers, Hibernate Internals |                 |
| **Related:**    | Criteria API, Dirty Checking and Flush Mode, JPA Specification                                                     |                 |

---

### 🔥 The Problem This Solves

**THE VENDOR LOCK-IN DILEMMA:**
JPA standardized the ORM API (`EntityManager`) so
applications could theoretically switch from Hibernate
to EclipseLink or OpenJPA without code changes. But
Hibernate has powerful features that JPA never standardized:
batch inserts, natural-id caching, session-level filters,
read-only entity optimization, and multi-tenancy.

Using `EntityManager` exclusively means no access to
Hibernate-specific performance and feature toolbox.
Using `Session` exclusively means the code is tightly
coupled to Hibernate (can't switch providers).

**THE SOLUTION:**
Spring's `@PersistenceContext EntityManager` gives you
the JPA-standard API. When you need a Hibernate-specific
feature: `em.unwrap(Session.class)` gives you the
underlying `Session` object without creating a new session.
The same persistence context and transaction are used;
you just gain access to the Hibernate API on top of it.

---

### 📘 Textbook Definition

**`EntityManager`** (JPA standard, `jakarta.persistence.EntityManager`)
is the primary JPA interface for:

- Persisting entities: `persist()`, `merge()`, `remove()`
- Finding entities: `find()`, `getReference()`
- Querying: `createQuery()`, `createNamedQuery()`, `createNativeQuery()`
- Transaction interaction: `flush()`, `clear()`, `contains()`, `refresh()`
- EntityManagerFactory access: `getEntityManagerFactory()`

**`Session`** (Hibernate-specific, `org.hibernate.Session`)
extends `EntityManager` and adds:

- `saveOrUpdate()` - upsert-like behavior
- `byId()`, `bySimpleNaturalId()`, `byNaturalId()` - typed load APIs
- `setReadOnly(entity, true)` - mark entity read-only in session
- `doWork(Connection -> {...})` - direct JDBC connection access
- `setHibernateFlushMode()` - Hibernate-level flush control
- `createFilter()` - query against a collection with additional WHERE
- `evict(entity)` - remove specific entity from first-level cache
- `getStatistics()` - Hibernate statistics

**`SessionFactory`** vs `EntityManagerFactory`:

- `SessionFactory` is the Hibernate-specific factory
- `EntityManagerFactory` is the JPA standard factory
- In Hibernate's implementation: `EntityManagerFactory.unwrap(SessionFactory.class)`
  gives you the `SessionFactory`

---

### ⏱️ Understand It in 30 Seconds

**One line:** `EntityManager` is the JPA standard API;
`Session` is Hibernate's extended implementation of it -
unwrap `EntityManager` to get a `Session` when you need
Hibernate-specific features.

**One analogy:**

> `EntityManager` is like a standard car with the
> required controls (steering, gas, brake). `Session`
> is the same car but with the hood open and additional
> controls exposed (turbo boost, sport mode, diagnostics).
> You drive the standard car daily; you open the hood
> only when you need the extra features.

**One insight:** `Session session = em.unwrap(Session.class)`
does NOT create a new session or a new transaction. It
returns a reference to the same underlying `Session`
that the `EntityManager` is already using. All operations
on the unwrapped `Session` participate in the same
persistence context and transaction.

---

### 🔩 First Principles Explanation

**THE INHERITANCE RELATIONSHIP:**

```
jakarta.persistence.EntityManager (JPA interface)
    ^
    |
org.hibernate.Session (Hibernate interface, extends
  EntityManager)
    ^
    |
org.hibernate.internal.SessionImpl (concrete
  implementation)

// Hibernate's EntityManagerImpl is also SessionImpl
// em.unwrap(Session.class) returns the same SessionImpl
// object without creating anything new

// Verify:
EntityManager em = ...;
Session session = em.unwrap(Session.class);
System.out.println(em == session);          // false
  (different type)
System.out.println(session.isOpen());       // true (same
  session)
System.out.println(em.isOpen());            // true (same
  session)
```

**JPA vs Hibernate OPERATION MAPPING:**

```
EntityManager              Session equivalent
-----------                ---------
em.persist(entity)         session.persist(entity)
em.find(T.class, id)       session.get(T.class, id)
em.getReference(T.class,id)session.load(T.class, id)
em.merge(entity)           session.merge(entity)
em.remove(entity)          session.remove(entity)
em.flush()                 session.flush()
em.clear()                 session.clear()
em.refresh(entity)         session.refresh(entity)
em.createQuery(hql,T.class)session.createQuery(hql,T.class)
(no equivalent)            session.saveOrUpdate(entity)
(no equivalent)            session.evict(entity)
(no equivalent)            session.byId(T.class)...
(no equivalent)            session.doWork(work)
(no equivalent)            session.setReadOnly(e, true)
```

---

### 🧪 Thought Experiment

**WHY saveOrUpdate IS PROBLEMATIC (AND WHY JPA OMITTED IT):**

```java
// Hibernate: saveOrUpdate
// - If entity is TRANSIENT (no id): INSERT
// - If entity is DETACHED (has id): UPDATE
// - If entity is already MANAGED: nothing special
session.saveOrUpdate(product);

// THE PROBLEM: it checks if the entity is detached
// by checking if the id field is null. But:
// - With UUID natural ids: product has an id even
//   when transient -> saveOrUpdate treats it as detached
//   -> fires an UPDATE for a new entity -> rows not found
//   -> confusing behavior

// JPA's answer: merge() is the portable alternative
// merge() checks persistence context + DB:
// - If managed: returns same instance
// - If detached: merges state into managed instance
// - If new (not in DB): inserts
em.merge(product); // always correct, more explicit

// That's why JPA spec omitted saveOrUpdate:
// merge() has clearer semantics despite being slower
// (may require an extra SELECT to check existence)
```

---

### 🧠 Mental Model / Analogy

> `EntityManager` is the dashboard controls of a car
> (standardized by law: pedals, steering, gear). `Session`
> is the car manufacturer's own mobile app that gives
> additional controls: performance mode, real-time
> diagnostics, battery management. The dashboard (EM)
> works for all driving tasks. The app (Session) unlocks
> features specific to that manufacturer.
>
> `em.unwrap(Session.class)` is opening the manufacturer's
> app while the car is already running - it connects to
> the same car session, does not restart the engine or
> change the current state.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
`EntityManager` is the standard JPA way to interact with
the database. `Session` is Hibernate's version of the
same thing, with extra features. You can access the
extra features by calling `em.unwrap(Session.class)`.

**Level 2 - How to use it (junior developer):**
Inject `@PersistenceContext EntityManager em` for all
standard operations. When you need a Hibernate-specific
feature (like `session.evict()` or `byId()`), call
`Session session = em.unwrap(Session.class)`.

**Level 3 - How it works (mid-level engineer):**
Hibernate's `Session` interface extends `EntityManager`.
The concrete implementation (`SessionImpl`) is the same
object. `em.unwrap(Session.class)` casts to `Session`
without creating a new object. Both references share
the same persistence context, same transaction, same
first-level cache.

**Level 4 - When to use Session (senior/staff):**
Prefer `EntityManager` for all standard operations.
Use `Session.unwrap()` for: (1) `session.setReadOnly(entity, true)` -
mark entities read-only to skip dirty checking for
specific entities (not the whole session like
`readOnly=true` transaction hint). (2) `session.doWork()`
for direct JDBC access within the Hibernate-managed
connection. (3) `session.byNaturalId()` for efficient
natural-id lookup with second-level cache. (4) `session.evict(entity)`
to manually remove a specific entity from the first-level
cache (fine-grained cache management in batch processing).

**Level 5 - Architecture (distinguished engineer):**
In Hibernate 5 -> 6 migration, many `Session`-specific
methods were moved closer to the JPA standard or changed
signatures. Code that uses `Session` directly is more
sensitive to Hibernate major version upgrades. In a
microservices architecture where the Hibernate version
may be upgraded independently in each service, extensive
use of `Session`-specific APIs creates version-specific
coupling. For shared library code (common repositories),
prefer `EntityManager`. For service-internal advanced
usage, `Session` is acceptable with documented rationale.

---

### ⚙️ How It Works (Mechanism)

**HIBERNATE-SPECIFIC SESSION FEATURES:**

```java
// 1. Natural-id lookup with L2 cache
Product product = session
    .bySimpleNaturalId(Product.class)
    .load(sku);          // SKU is natural id
// Checks second-level cache (if enabled) by natural id
// Efficient; avoids table scan for natural key lookup

// 2. Mark entity read-only (fine-grained, per entity)
List<Product> products = session
    .createQuery("FROM Product p WHERE p.active=true",
                 Product.class)
    .getResultList();
products.forEach(p -> session.setReadOnly(p, true));
// Hibernate skips dirty checking for these entities only
// Other entities in same session still track changes

// 3. Direct JDBC access within Hibernate transaction
session.doWork(conn -> {
    try (PreparedStatement ps = conn.prepareStatement(
             "CALL update_inventory(?, ?)")) {
        ps.setLong(1, productId);
        ps.setInt(2, quantity);
        ps.execute();
    }
});
// Same connection as Hibernate transaction
// Stored procedure call within same TX

// 4. Evict specific entity from first-level cache
// (useful in batch processing to free memory):
session.evict(processedEntity);
// Entity removed from 1L cache; GC can collect it
// Without evict: all N processed entities remain in cache
```

---

### 🔄 The Complete Picture - End-to-End Flow

**USING BOTH APIs IN ONE SERVICE:**

```java
@Service
public class ProductService {

    @PersistenceContext
    private EntityManager em;

    // Standard JPA operations: use EntityManager
    @Transactional
    public Product createProduct(ProductDto dto) {
        Product p = new Product(dto.getName(), dto.getPrice());
        em.persist(p);          // JPA standard
        return p;
    }

    // Hibernate-specific: unwrap Session
    @Transactional(readOnly = true)
    public Product findBySku(String sku) {
        // Natural-id lookup: uses L2 cache if enabled
        return em.unwrap(Session.class)
            .bySimpleNaturalId(Product.class)
            .load(sku);
    }

    // Fine-grained read-only per entity:
    @Transactional
    public void processReports(List<Long> ids) {
        Session session = em.unwrap(Session.class);
        for (Long id : ids) {
            Product p = em.find(Product.class, id);
            session.setReadOnly(p, true); // skip dirty check
            reportService.generate(p);
            session.evict(p); // free 1L cache memory
        }
    }
}
```

---

### 💻 Code Example

**Example 1 - BAD: using Session everywhere (vendor lock-in):**

```java
// BAD: entire repository uses Session directly
// Cannot switch to EclipseLink without full rewrite
@Repository
public class ProductDao {
    @Autowired
    private SessionFactory sessionFactory;

    public Product findById(Long id) {
        return sessionFactory.getCurrentSession()
            .get(Product.class, id); // Hibernate-only API
    }

    public void save(Product p) {
        sessionFactory.getCurrentSession()
            .saveOrUpdate(p); // Hibernate-only; ambiguous semantics
    }
}

// GOOD: use EntityManager for standard operations
@Repository
public class ProductDao {
    @PersistenceContext
    private EntityManager em;

    public Product findById(Long id) {
        return em.find(Product.class, id); // JPA standard
    }

    public void save(Product p) {
        em.persist(p); // or em.merge(p) - JPA standard
    }

    // Hibernate-specific only where needed:
    public Product findBySku(String sku) {
        return em.unwrap(Session.class)
            .bySimpleNaturalId(Product.class)
            .load(sku);
    }
}
```

**Example 2 - Session filters for multi-tenancy:**

```java
// Hibernate filter: conditional WHERE added to all queries
// within a session (e.g., tenant isolation)
@FilterDef(name = "tenantFilter",
    parameters = @ParamDef(name = "tenantId",
                           type = Long.class))
@Filter(name = "tenantFilter",
        condition = "tenant_id = :tenantId")
@Entity
public class Product { ... }

// Activate filter for the current session:
Session session = em.unwrap(Session.class);
session.enableFilter("tenantFilter")
    .setParameter("tenantId", currentTenantId);

// All queries in this session now automatically
// include: AND tenant_id = ?
// JPA EntityManager has no equivalent feature
```

---

### ⚖️ Comparison Table

| Operation            | EntityManager (JPA)         | Session (Hibernate)                            |
| -------------------- | --------------------------- | ---------------------------------------------- |
| Persist new          | `persist(entity)`           | `persist(entity)`                              |
| Load by ID           | `find(T.class, id)`         | `get(T.class, id)` or `byId(T.class).load(id)` |
| Proxy load           | `getReference(T.class, id)` | `load(T.class, id)`                            |
| Merge detached       | `merge(entity)`             | `merge(entity)`                                |
| Delete               | `remove(entity)`            | `remove(entity)`                               |
| Flush                | `flush()`                   | `flush()`                                      |
| Evict single         | No direct method            | `evict(entity)`                                |
| Natural-id lookup    | No direct method            | `bySimpleNaturalId(T.class).load(key)`         |
| Per-entity read-only | No direct method            | `setReadOnly(entity, true)`                    |
| Direct JDBC          | No direct method            | `doWork(conn -> {...})`                        |
| Session filters      | No equivalent               | `enableFilter("name").setParameter(...)`       |

---

### ⚠️ Common Misconceptions

| Misconception                                                          | Reality                                                                                                                                                                                                                                                 |
| ---------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "`Session` and `EntityManager` use different persistence contexts"     | `em.unwrap(Session.class)` returns the same underlying `SessionImpl`. They share exactly one persistence context. Changes via `Session` are immediately visible via the `EntityManager` reference and vice versa.                                       |
| "`saveOrUpdate()` is equivalent to JPA `merge()`"                      | `saveOrUpdate()` determines INSERT vs UPDATE based on whether the ID field is null. This fails with natural IDs or UUIDs. `merge()` checks the persistence context first, then issues a SELECT to check the database if needed - more robust semantics. |
| "Using `SessionFactory` directly is always bad"                        | `SessionFactory` is Hibernate's native factory. In Spring Boot, the `EntityManagerFactory` IS the `SessionFactory` (unwrap it). For test setup, batch jobs without Spring context, or tools, accessing `SessionFactory` directly is perfectly fine.     |
| "`EntityManager` is slower than `Session` due to abstraction overhead" | There is no measurable overhead. `EntityManagerImpl` in Hibernate is a thin wrapper that delegates to the `Session` implementation for all operations. The JPA interface adds zero runtime cost.                                                        |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: unwrap() Called Outside Transaction Scope**

**Symptom:** `em.unwrap(Session.class)` throws
`HibernateException: No TransactionSynchronizationRegistry`.

**Root Cause:** `em.unwrap()` was called in a context
where no active EntityManager is bound to the thread
(outside `@Transactional` scope or in a new thread).

**Fix:** Ensure the method is called within a
`@Transactional` context. The container-managed
`EntityManager` is only valid within a transaction.

---

**Failure Mode 2: saveOrUpdate UUID Entity Fires UPDATE on New Entity**

**Symptom:** New entity with `@GeneratedValue(AUTO)`
and UUID type causes Hibernate to fire `UPDATE` instead
of `INSERT`. `0 rows updated` warning in logs. Entity not saved.

**Root Cause:** `saveOrUpdate()` checks if the ID field
is `null` to decide INSERT vs UPDATE. UUID is never null
(it's generated before `saveOrUpdate()` is called). So
Hibernate assumes it's detached -> fires UPDATE -> 0 rows.

**Fix:** Use `session.persist(entity)` (or `em.persist()`)
instead of `saveOrUpdate()` for new entities. For detached
entities: use `em.merge()` which correctly checks
persistence context + database.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[JPH-011 - EntityManager]] - the JPA standard API;
  understand it before Session
- [[JPH-012 - Persistence Context]] - Session and
  EntityManager both wrap a persistence context

**Builds On This (learn these next):**

- [[JPH-033 - First Level Cache]] - first-level cache is
  the persistence context managed by Session/EM
- [[JPH-034 - Second Level Cache]] - Session provides
  direct access to second-level cache operations
- [[JPH-052 - Dirty Checking and Flush Mode]] - Session
  provides fine-grained flush mode control

**Related:**

- [[JPH-057 - JPA Specification]] - EntityManager is
  defined in the JPA specification; Session is Hibernate's
  proprietary extension
- [[JPH-058 - Hibernate Internals]] - SessionImpl
  architecture and internals

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ RULE         │ Use EntityManager for portability        │
│              │ Use Session only for Hibernate features  │
├──────────────┼──────────────────────────────────────────┤
│ UNWRAP       │ Session s = em.unwrap(Session.class);    │
│              │ Same persistence context; no new session │
├──────────────┼──────────────────────────────────────────┤
│ SESSION ONLY │ evict(entity), setReadOnly(e,true),      │
│              │ doWork(conn->{}), byNaturalId(T.class),  │
│              │ enableFilter("name"), getStatistics()    │
├──────────────┼──────────────────────────────────────────┤
│ AVOID        │ saveOrUpdate() - use persist() or merge()│
│              │ (fails with UUID/natural-id entities)    │
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "EntityManager = JPA standard API.       │
│              │ Session = Hibernate's extended version.  │
│              │ Same object; unwrap EM to get Session."  │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. `Session` extends and implements `EntityManager` -
   they are the same underlying object; `unwrap()` just
   exposes additional methods
2. Use `EntityManager` for all standard operations;
   `unwrap(Session.class)` only for Hibernate-specific
   features (evict, natural-id, doWork, setReadOnly)
3. Avoid `saveOrUpdate()` - use `persist()` for new
   entities and `merge()` for detached entities; both
   have clearer semantics

**Interview one-liner:** `EntityManager` is the JPA
standard API for database operations. Hibernate's `Session`
extends it with proprietary features: `evict()`, `setReadOnly()`,
natural-id lookups, `doWork()` for JDBC, and session
filters. In Spring Boot, use `EntityManager` by default;
call `em.unwrap(Session.class)` to access Hibernate-
specific features in the same persistence context.

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Standard API vs
proprietary extension is a recurring trade-off in
software. The pattern repeats everywhere: JDBC
(`Connection`) vs vendor-specific extensions; Servlet API
vs Tomcat/Jetty internals; Java NIO vs
Netty's ByteBuf; JPA vs Hibernate. The principle: code
to the standard interface for portability and testability;
unwrap/cast to the implementation only at the point where
the proprietary feature is explicitly needed, and document
why. This creates a "seam": if the vendor changes (Hibernate
-> EclipseLink) or upgrades (Hibernate 5 -> 6), only the
code at the seam needs review. Standard-API code is
unchanged.

**Where else this pattern appears:**

- **JDBC**: `Connection.unwrap(OracleConnection.class)` for
  Oracle-specific LOB handling while keeping standard JDBC
  elsewhere
- **Java EE/Jakarta Servlet**: `request.getAttribute()` (standard)
  vs `((HttpServletRequestWrapper) request).getXForwardedFor()` (custom)
- **Netty vs NIO**: code to `Channel`/`ChannelHandler`
  (Netty abstraction); unwrap to implementation only for
  performance tuning
- **AWS SDK**: standard `S3Client` interface; `CrtS3Client.builder()`
  for AWS CRT (faster native transport) when needed

---

### 💡 The Surprising Truth

In Spring Boot, `@Autowired SessionFactory sessionFactory`
and `@PersistenceContext EntityManager em` resolve to
the SAME underlying Hibernate `SessionFactory`/`SessionImpl`.
The `EntityManagerFactory` created by
`LocalContainerEntityManagerFactoryBean` in Spring Boot
auto-configuration IS a Hibernate `SessionFactory` wrapped
in a JPA adapter. You can verify: `emf.unwrap(SessionFactory.class)`.
This means: there is NO overhead from using `EntityManager`
instead of `Session` in Spring Boot. The abstraction is
purely at the API/interface level. The reason to prefer
`EntityManager` is not performance - it is portability,
testability (easy to mock `EntityManager`), and protection
from Hibernate-specific API changes between major versions.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **DIAGRAM** the inheritance relationship: `SessionImpl`
   implements both `Session` and `EntityManager`
2. **LIST** five Hibernate-specific `Session` features
   that `EntityManager` does not have
3. **EXPLAIN** why `saveOrUpdate()` fails with UUID
   entities and what to use instead
4. **WRITE** a service method that uses `EntityManager`
   for standard operations and unwraps to `Session` for
   an evict operation in batch processing
5. **DESCRIBE** when to inject `SessionFactory` directly
   vs `EntityManager` in a Spring application

---

### 🎯 Interview Deep-Dive

**Q1: What is the relationship between Hibernate Session
and JPA EntityManager?**
_Why they ask:_ Common confusion; tests Hibernate/JPA
architecture understanding.
_Strong answer includes:_

- `Session` extends/implements `EntityManager` in Hibernate
- Hibernate's `SessionImpl` is the concrete class that
  implements both interfaces
- `em.unwrap(Session.class)` returns the same `SessionImpl`
  object - no new session created; same persistence context
- `EntityManager` is the JPA standard (portable);
  `Session` adds Hibernate-specific features
- In Spring Boot: `@PersistenceContext EntityManager` and
  `@Autowired SessionFactory` work with the same underlying
  Hibernate infrastructure

**Q2: When would you prefer to use Hibernate Session
directly over EntityManager?**
_Why they ask:_ Tests practical knowledge of Hibernate
features.
_Strong answer includes:_

- `session.evict(entity)`: remove specific entity from
  first-level cache in batch processing (free memory per entity)
- `session.setReadOnly(entity, true)`: mark specific
  entities read-only (skip dirty checking per entity,
  not per transaction)
- `session.bySimpleNaturalId(T.class).load(key)`: natural-id
  lookup with second-level cache support
- `session.doWork(conn -> {})`: direct JDBC access within
  Hibernate-managed transaction
- `session.enableFilter("filterName")`: Hibernate filter
  for automatic WHERE clause addition (e.g., soft-delete,
  tenant isolation)
- `session.getStatistics()`: query statistics for performance
  monitoring
