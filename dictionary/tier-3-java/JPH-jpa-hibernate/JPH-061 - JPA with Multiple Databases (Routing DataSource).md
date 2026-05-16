---
id: JPH-061
title: "JPA with Multiple Databases (Routing DataSource)"
category: JPA & Hibernate
tier: tier-3-java
folder: JPH-jpa-hibernate
difficulty: ★★★
depends_on: JPH-001, JPH-011, JPH-012, JPH-026, JPH-047, JPH-048
used_by: []
related: JPH-048, JPH-047, JPH-054
tags:
  - java
  - jpa
  - database
  - architecture
  - advanced
status: complete
version: 4
layout: default
parent: "JPA & Hibernate"
grand_parent: "Technical Dictionary"
nav_order: 61
permalink: /jpa-hibernate/jpa-with-multiple-databases-routing-datasource/
---

# JPH-061 - JPA with Multiple Databases (Routing DataSource)

⚡ **TL;DR** - Two patterns for multiple databases in Spring JPA:
(1) **Multiple `EntityManagerFactory`** - separate EMF per DB; entities
in different packages; completely isolated persistence units. Use when
each DB has different entities.
(2) **`AbstractRoutingDataSource`** - single EMF, single schema;
routes connection to different DB replicas at runtime based on
a key (ThreadLocal). Use for primary/replica read-write splitting
or multi-tenant schema-per-tenant.
Key pitfalls: `@Transactional` propagation across different EMFs is
not supported without JTA; routing after transaction starts loses effect;
distributed transactions require Atomikos or JTA manager.

| #061            | Category: JPA & Hibernate                                                           | Difficulty: ★★★ |
| :-------------- | :---------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | JPA Overview, EntityManager, Persistence Context, Connection Pooling, Multi-Tenancy |                 |
| **Used by:**    | -                                                                                   |                 |
| **Related:**    | Multi-Tenancy, Connection Pooling, JPA at Scale                                     |                 |

---

### 🔥 The Problem This Solves

**WHY MULTIPLE DATABASES ARE NEEDED:**

```
Common scenarios requiring multiple DB connections:

1. Primary/Replica read-write splitting:
   WRITE operations -> primary (single writer)
   READ operations  -> replica (multiple readers, lower latency)
   Goal: reduce read load on primary; improve read throughput
   Tool: AbstractRoutingDataSource

2. Multiple distinct databases (separate business domains):
   OrderService connects to orders_db
   InventoryService connects to inventory_db
   Both in same Spring Boot app (monolith or shared service)
   Goal: schema isolation; different schemas, entities per DB
   Tool: Multiple EntityManagerFactory beans

3. Multi-tenant: database-per-tenant:
   Tenant A -> DB instance tenant_a
   Tenant B -> DB instance tenant_b
   Single code; route to correct DB per HTTP request
   Goal: strict data isolation
   Tool: AbstractRoutingDataSource OR Hibernate multi-tenancy

4. Analytics DB (OLAP) + operational DB (OLTP):
   Writes: operational DB (normalized, OLTP)
   Reports: analytics DB (denormalized, OLAP, read replica)
   Tool: Multiple DataSource beans; JOOQ for analytics queries

The critical constraint: Spring @Transactional uses ONE
DataSource per transaction. Cross-DataSource operations in one
@Transactional method are NOT automatically atomic without JTA.
```

---

### 📘 Textbook Definition

**Multiple DataSource Configuration** in Spring Boot refers to
configuring more than one JDBC `DataSource` bean, each potentially
with its own `EntityManagerFactory`, `TransactionManager`, and
connection pool.

**`AbstractRoutingDataSource`** (`org.springframework.jdbc.datasource.lookup.AbstractRoutingDataSource`)
is a Spring JDBC abstraction that routes JDBC connection requests
to one of several backing `DataSource` beans based on a lookup
key determined at runtime (typically from a `ThreadLocal`).

**Two patterns compared:**

| Pattern                         | When to use                               | What it enables                                            |
| ------------------------------- | ----------------------------------------- | ---------------------------------------------------------- |
| Multiple `EntityManagerFactory` | Different entities in different databases | Per-DB entity management; fully isolated persistence units |
| `AbstractRoutingDataSource`     | Same schema, different DB instances       | Dynamic routing; primary/replica; multi-tenant same schema |

---

### ⏱️ Understand It in 30 Seconds

**One line:** Multiple EMFs = different entities in different
databases. `AbstractRoutingDataSource` = same entities, different
database instances, chosen at runtime per request.

**One analogy:**

> Multiple `EntityManagerFactory` is like having two separate
> HR departments at two different offices. Each office has
> its own staff list (entity classes), its own filing system
> (schema), and its own HR policies (transaction manager).
> A person from office A cannot work directly with office B's
> files without a cross-office transfer process (JTA).
> `AbstractRoutingDataSource` is like having one HR department
> with two identical offices (same schema). The HR manager checks
> your badge (ThreadLocal key) and routes you to office A
> (primary) for important updates or office B (replica) for
> casual lookups. Both offices have identical file layouts.

---

### 🔩 First Principles Explanation

**PATTERN 1 - MULTIPLE ENTITYMANAGERFACTORY:**

```
Spring Boot auto-configuration assumes ONE DataSource ->
ONE EntityManagerFactory -> ONE TransactionManager.

For multiple databases:
  1. DISABLE auto-configuration:
     @SpringBootApplication(exclude = {
       DataSourceAutoConfiguration.class,
       HibernateJpaAutoConfiguration.class,
       DataSourceTransactionManagerAutoConfiguration.class
     })

  2. Define primary DataSource (one @Primary):
     @Bean @Primary
     @ConfigurationProperties("spring.datasource.orders")
     DataSource ordersDataSource()

  3. Define secondary DataSource:
     @Bean
     @ConfigurationProperties("spring.datasource.inventory")
     DataSource inventoryDataSource()

  4. Define EntityManagerFactory per DataSource:
     - ordersEntityManagerFactory (scans com.example.orders)
     - inventoryEntityManagerFactory (scans com.example.inventory)

  5. Define TransactionManager per EMF:
     - ordersTransactionManager
     - inventoryTransactionManager

  6. Use @Transactional("ordersTransactionManager") on services
     that use the orders DB (explicit qualifier)

ISOLATION GUARANTEE:
  Within one @Transactional("ordersTransactionManager"):
    All operations use ordersDataSource connection
    Atomic commit/rollback on ordersDataSource only
  inventoryDataSource is INDEPENDENT - its own transaction

CROSS-DATABASE ATOMICITY:
  Not available without JTA (2-phase commit)
  If ordersDataSource commits but inventoryDataSource fails:
    data inconsistency (partial commit)
  Fix: Saga pattern (eventual consistency) or JTA + Atomikos
```

---

### 🧪 Thought Experiment

**ABSTRACT ROUTING DATASOURCE - HOW ROUTING WORKS:**

```
AbstractRoutingDataSource internal flow:

HTTP Request: GET /products (read operation)

1. Filter/AOP: DataSourceContextHolder.set(READ)
   ThreadLocal<String> = "READ"

2. Service method called:
   @Transactional("replicaTransactionManager")
   public List<Product> findAll() { ... }

3. Spring opens transaction:
   -> RoutingDataSource.getConnection()
      -> determineCurrentLookupKey() -> "READ"
      -> targetDataSources.get("READ") -> replicaDataSource
      -> replicaDataSource.getConnection() -> PG replica connection

4. EntityManager uses this connection for all queries

5. Transaction commit -> connection returned to HikariCP replica pool

6. Filter cleanup: DataSourceContextHolder.clear()

HTTP Request: POST /products (write operation)

1. Filter: DataSourceContextHolder.set(WRITE)
2. @Transactional: RoutingDataSource -> determineCurrentLookupKey()
   -> "WRITE" -> primaryDataSource -> PG primary connection
3. Entity persisted, transaction committed on primary
4. Replica receives replication event async from primary

KEY CONSTRAINT:
  Routing key is determined at connection acquisition time
  (when @Transactional opens the transaction / first DB call).
  Changing the ThreadLocal AFTER transaction starts:
    has NO effect for that transaction.
  Routing decision is PER TRANSACTION, not per query.
```

---

### 🧠 Mental Model / Analogy

> `AbstractRoutingDataSource` is a smart traffic light at a
> junction. Before you enter the junction (before the transaction
> opens), you show your badge (ThreadLocal lookup key). The
> light routes you to the left road (primary) for heavy trucks
> (writes) or the right road (replica) for bicycles (reads).
> Once you're past the junction (transaction open), the traffic
> light has no more control over you - you stay on whichever
> road you were routed to for your entire journey (transaction).
> Trying to change roads mid-journey (mid-transaction) doesn't work.
> The trick: show your badge BEFORE entering the junction
> (set ThreadLocal BEFORE `@Transactional` proxy fires).

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What you need (anyone):**
If you have two separate databases (orders, inventory): you
need two `EntityManagerFactory` beans. If you have one database
with a read replica (same schema): you need `AbstractRoutingDataSource`.

**Level 2 - Read/write splitting wiring (junior-mid):**

```java
// Read/write split with AbstractRoutingDataSource
public class ReadWriteRoutingDataSource
    extends AbstractRoutingDataSource {

    @Override
    protected Object determineCurrentLookupKey() {
        return DataSourceContext.isReadOnly()
            ? "replica"
            : "primary";
    }
}

// Thread-local context holder:
public class DataSourceContext {
    private static final ThreadLocal<Boolean> READ_ONLY =
        ThreadLocal.withInitial(() -> false);

    public static void setReadOnly() {
        READ_ONLY.set(true);
    }
    public static boolean isReadOnly() {
        return READ_ONLY.get();
    }
    public static void clear() {
        READ_ONLY.remove();
    }
}
```

**Level 3 - Transaction interaction (mid):**

```java
// CRITICAL: Set routing key BEFORE @Transactional proxy fires
// @Transactional proxy: opens transaction on method entry
// -> RoutingDataSource.getConnection() called on entry
// ThreadLocal must be set BEFORE method is entered

// BAD: set inside @Transactional method (too late):
@Transactional
public List<Product> findAllBad() {
    DataSourceContext.setReadOnly(); // TOO LATE - TX already opened
    return repository.findAll();
    // TX opened on primary even though we set read-only
}

// GOOD: AOP aspect sets before transaction opens:
@Aspect
@Order(Ordered.HIGHEST_PRECEDENCE)
public class DataSourceAspect {
    @Around("@annotation(readOnlyOp)")
    public Object routeToReplica(ProceedingJoinPoint pjp,
        ReadOnlyOperation readOnlyOp) throws Throwable {
        DataSourceContext.setReadOnly();  // set BEFORE TX opens
        try {
            return pjp.proceed();
        } finally {
            DataSourceContext.clear();
        }
    }
}
```

**Level 4 - Multiple EMF configuration (senior):**

```java
// Multiple EntityManagerFactory beans:
@Configuration
@EnableTransactionManagement
public class OrdersDbConfig {
    @Primary @Bean
    @ConfigurationProperties("app.datasource.orders")
    public DataSource ordersDataSource() {
        return DataSourceBuilder.create().build();
    }

    @Primary @Bean
    public LocalContainerEntityManagerFactoryBean
            ordersEntityManagerFactory(
            @Qualifier("ordersDataSource") DataSource ds,
            JpaVendorAdapter adapter) {
        var factory =
            new LocalContainerEntityManagerFactoryBean();
        factory.setDataSource(ds);
        factory.setPackagesToScan("com.example.orders.domain");
        factory.setJpaVendorAdapter(adapter);
        return factory;
    }

    @Primary @Bean
    public PlatformTransactionManager ordersTransactionManager(
            @Qualifier("ordersEntityManagerFactory")
            EntityManagerFactory emf) {
        return new JpaTransactionManager(emf);
    }
}
```

**Level 5 - JTA for cross-DB atomicity (staff):**

```xml
<!-- pom.xml: add Atomikos JTA for distributed transactions -->
<dependency>
    <groupId>com.atomikos</groupId>
    <artifactId>transactions-spring-boot3-starter</artifactId>
    <version>6.0.0</version>
</dependency>
```

```java
// With JTA: both DataSources participate in one atomic TX
@Transactional  // JTA transaction manager (XA)
public void crossDatabaseOperation() {
    ordersRepo.save(order);       // orders DB
    inventoryRepo.update(item);   // inventory DB
    // If either fails: both roll back (2-phase commit)
    // Cost: ~3x slower than single-DB transaction
    // Use only when cross-DB atomicity is truly required
}
// RECOMMENDATION: avoid JTA if possible.
// Prefer Saga pattern (eventual consistency) for
// cross-database operations in microservice context.
// JTA is appropriate for: same-JVM, tightly coupled services,
// moderate throughput, where atomic guarantee outweighs latency.
```

---

### ⚙️ How It Works (Mechanism)

**SPRING BOOT AUTO-CONFIGURATION OVERRIDE:**

```
Default Spring Boot (single DataSource):
  DataSourceAutoConfiguration
    -> creates DataSource from spring.datasource.*
    -> creates HikariDataSource (pool)
  HibernateJpaAutoConfiguration
    -> creates LocalContainerEntityManagerFactoryBean
    -> uses the single DataSource
  JpaTransactionManagerAutoConfiguration
    -> creates JpaTransactionManager
    -> uses the single EntityManagerFactory
  -> Everything auto-wired: zero config needed

Multiple DataSource:
  Must exclude these auto-configurations
  Must manually define all beans for each DataSource
  @Primary marks the "default" (used by Spring Data auto)
  Non-primary beans must use @Qualifier at injection points
  @Transactional("beanName") must explicitly name TM
    (without name: uses @Primary transaction manager)

AbstractRoutingDataSource bootstrap:
  @Bean RoutingDataSource:
    targetDataSources = {"primary": primaryDS, "replica": replicaDS}
    defaultTargetDataSource = primaryDS
    afterPropertiesSet() -> resolves and caches DataSource refs
  -> Returns single DataSource to EMF
  -> EMF/Hibernate has NO knowledge of routing
  -> Routing is transparent at JDBC Connection level
```

---

### 🔄 The Complete Picture - End-to-End Flow

**READ/WRITE SPLIT ARCHITECTURE:**

```
HTTP Request: GET /api/products

  1. RequestFilter: detect GET -> DataSourceContext.setReadOnly()

  2. ProductController.list() -> ProductService.findAll()

  3. @Transactional(readOnly=true) on ProductService.findAll()
     -> JPA TX Manager opens TX
     -> RoutingDataSource.getConnection()
     -> determineCurrentLookupKey() -> "replica"
     -> HikariCP replica pool -> PG replica connection

  4. JPA query: SELECT * FROM products
     -> executes on PG replica (read-only connection)

  5. @Transactional commit (read-only: no flush, no write)
     -> connection returned to replica pool

  6. RequestFilter finally: DataSourceContext.clear()

HTTP Request: POST /api/products

  1. RequestFilter: detect POST -> DataSourceContext not set
     (default = primary)

  2. @Transactional on ProductService.save()
     -> RoutingDataSource -> "primary"
     -> HikariCP primary pool -> PG primary connection

  3. em.persist(product) -> INSERT on primary
  4. commit -> WAL replication to replica (async, ~ms latency)
  5. Subsequent GETs will read from replica
     (replication lag ~10ms-100ms: acceptable for most use cases)
```

---

### 💻 Code Example

**Complete AbstractRoutingDataSource setup:**

```java
// application.yml:
// app.datasource.primary.url=jdbc:postgresql://primary:5432/db
// app.datasource.replica.url=jdbc:postgresql://replica:5432/db

@Configuration
public class RoutingDataSourceConfig {

    @Bean
    @ConfigurationProperties("app.datasource.primary")
    public DataSource primaryDataSource() {
        return DataSourceBuilder.create().build();
    }

    @Bean
    @ConfigurationProperties("app.datasource.replica")
    public DataSource replicaDataSource() {
        return DataSourceBuilder.create().build();
    }

    @Primary @Bean
    public DataSource routingDataSource(
            @Qualifier("primaryDataSource") DataSource primary,
            @Qualifier("replicaDataSource") DataSource replica) {
        var routing = new ReadWriteRoutingDataSource();
        Map<Object, Object> sources = new HashMap<>();
        sources.put("primary", primary);
        sources.put("replica", replica);
        routing.setTargetDataSources(sources);
        routing.setDefaultTargetDataSource(primary);
        routing.afterPropertiesSet();
        return routing;
    }
}

// Routing DataSource:
public class ReadWriteRoutingDataSource
    extends AbstractRoutingDataSource {
    @Override
    protected Object determineCurrentLookupKey() {
        return DataSourceContext.isReadOnly()
            ? "replica" : "primary";
    }
}

// AOP aspect (sets BEFORE @Transactional fires):
@Aspect @Component
@Order(1)  // must be lower order number than @Transactional
public class ReadOnlyRoutingAspect {
    @Around("@within(org.springframework.stereotype.Service)" +
        " && @annotation(tx)")
    public Object route(ProceedingJoinPoint pjp,
            Transactional tx) throws Throwable {
        if (tx.readOnly()) {
            DataSourceContext.setReadOnly();
        }
        try {
            return pjp.proceed();
        } finally {
            DataSourceContext.clear();
        }
    }
}
// Usage: @Transactional(readOnly=true) -> routed to replica
//        @Transactional -> routed to primary
```

---

### ⚖️ Comparison Table

| Pattern                   | Isolation                          | Transaction scope                  | Use case                          |
| ------------------------- | ---------------------------------- | ---------------------------------- | --------------------------------- |
| Multiple EMF              | Full (different entities, schemas) | Per DataSource; no cross-DS atomic | Orders DB + Inventory DB          |
| AbstractRoutingDataSource | None (same schema)                 | Single TX per routing key          | Primary/replica split             |
| JTA (Atomikos)            | Full (XA)                          | Cross-DataSource atomic            | When cross-DB atomicity required  |
| Saga pattern              | Eventual consistency               | Per-service local TX               | Microservices; preferred over JTA |

---

### ⚠️ Common Misconceptions

| Misconception                                                          | Reality                                                                                                                                                                                                                                                                                                |
| ---------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| "AbstractRoutingDataSource routes individual queries"                  | It routes at connection acquisition time - when the transaction opens (first `@Transactional` method entry). All queries within that transaction use the same connection (same DataSource). Changing the ThreadLocal mid-transaction has no effect. The decision is per-transaction, not per-query.    |
| "Two EntityManagerFactory beans can participate in one @Transactional" | NO - each `JpaTransactionManager` manages one `EntityManagerFactory`. A `@Transactional` without a qualifier uses the `@Primary` TM. Using both DataSources in one method without JTA means two independent local transactions - no atomicity guarantee.                                               |
| "readOnly=true on @Transactional automatically routes to replica"      | NOT automatically. `readOnly=true` is a Hibernate optimization hint (no flush, no dirty checking). It does NOT route to a replica unless you've wired routing logic (AbstractRoutingDataSource + AOP aspect) that reads this flag. The routing is YOUR code; Spring doesn't provide it out of the box. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode: Writes Go to Replica (Read Replica Is Read-Only)**

**Symptom:** `PSQLException: ERROR: cannot execute INSERT in
a read-only transaction` (PostgreSQL). `HY000: The MySQL server
is running with the --read-only option`. Write operations
fail with "read-only" error.
**Root Cause:** ThreadLocal routing key is set to "replica" when
a write operation is performed. Either: (a) the AOP aspect that
clears the ThreadLocal is not being called in finally block
(exception path), or (b) the routing key is set outside the
thread-safe scope (async operation, thread pool).
**Diagnosis:**

```java
// Debug: log the routing key:
@Override
protected Object determineCurrentLookupKey() {
    Object key = DataSourceContext.isReadOnly()
        ? "replica" : "primary";
    log.debug("Routing to: {} for thread: {}",
        key, Thread.currentThread().getName());
    return key;
}
```

**Fix:** Ensure `DataSourceContext.clear()` is in a `finally` block.
For async operations: pass routing context explicitly (do not use
ThreadLocal across thread boundaries without propagation).

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[JPH-047 - Connection Pooling with JPA (HikariCP)]] - underlying
  connection pool that `AbstractRoutingDataSource` routes to
- [[JPH-048 - Multi-Tenancy in JPA and Hibernate]] - multi-tenancy
  approaches including separate DB per tenant

**Builds On This (learn these next):**

- [[JPH-054 - JPA at Scale - Architecture Patterns]] - how
  multiple DataSource fits into larger architecture patterns

**Related:**

- [[JPH-047 - Connection Pooling]] - HikariCP configuration
  per DataSource in routing setup

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ PATTERN 1      │ Multiple EntityManagerFactory:          │
│ (diff schemas) │ different entities per DB;              │
│                │ @Transactional("specificTxMgr")         │
│                │ No cross-DB atomic (need JTA)           │
├────────────────┼─────────────────────────────────────────┤
│ PATTERN 2      │ AbstractRoutingDataSource:              │
│ (same schema)  │ routes to primary or replica per TX.    │
│                │ Set ThreadLocal BEFORE @Transactional.  │
│                │ Single EMF; routing transparent to JPA  │
├────────────────┼─────────────────────────────────────────┤
│ ROUTING TIMING │ Connection acquired at TX open.         │
│                │ ThreadLocal must be set BEFORE TX.      │
│                │ Mid-TX routing change: has no effect.   │
├────────────────┼─────────────────────────────────────────┤
│ CROSS-DB ATOMIC│ Requires JTA (Atomikos) or Saga.        │
│                │ Prefer Saga for microservices.          │
│                │ JTA for same-JVM, low-throughput.       │
├────────────────┼─────────────────────────────────────────┤
│ ONE-LINER      │ "Multiple EMF: different entities per   │
│                │ DB. Routing DataSource: same schema,    │
│                │ route connection at TX start by         │
│                │ ThreadLocal key. No cross-DS atomic     │
│                │ without JTA."                           │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Multiple EMF = different entities/schemas per DB; `AbstractRoutingDataSource` = same schema, different DB instances
2. Routing decision is made at transaction start (connection acquisition); ThreadLocal must be set BEFORE `@Transactional`
3. Cross-DataSource atomicity requires JTA (costly) or Saga pattern (eventual consistency); prefer Saga for microservices

**Interview one-liner:** For multiple databases in Spring JPA:
if databases have different schemas/entities, use separate `EntityManagerFactory` beans (one per DB,
each with its own `@Transactional("specificTxManager")` qualifier).
For primary/replica read-write splitting with the same schema,
use `AbstractRoutingDataSource` - a Spring `DataSource` wrapper that routes JDBC connections
to primary or replica based on a `ThreadLocal` key. Critical constraint: routing key must be set
BEFORE the `@Transactional` proxy fires (AOP aspect with `@Order(1)` before transaction aspect).
Cross-DataSource atomicity requires JTA (Atomikos/Bitronix) or the Saga pattern.

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** `ThreadLocal` is the right
tool for request-scoped context that must flow through multiple
layers without explicit parameter passing. Read/write routing
key, tenant ID, user locale, security context - all use this
pattern. The universal rule for `ThreadLocal` in server applications:
ALWAYS clear in a `finally` block. Thread pools reuse threads; a
`ThreadLocal` not cleared in `finally` leaks into the next request
handled by the same thread. This is the source of "wrong tenant
data leak" security bugs in multi-tenant applications - the tenant
context from request A flows into request B via a dirty `ThreadLocal`.
The pattern: Set in filter entry -> use throughout request chain ->
clear in filter finally. This is exactly how Spring `SecurityContextHolder`,
`RequestContextHolder`, and `TransactionSynchronizationManager` work
internally.

---

### 💡 The Surprising Truth

`AbstractRoutingDataSource` has a subtle interaction with Spring's
`LazyConnectionDataSourceProxy`. If you wrap your routing datasource
with `LazyConnectionDataSourceProxy` (a common optimization to defer
actual JDBC connection acquisition until the first query), the routing
key is evaluated at first-query time, not at `@Transactional`-method-entry
time. This WIDENS the window where routing is still effective and
CLOSES the window for the "too late to set ThreadLocal" bug. Many
production read/write splitting setups use this combination specifically
to avoid the ordering problem between the routing aspect and the
transaction aspect. The setup is: `RoutingDataSource` wrapped by
`LazyConnectionDataSourceProxy`, then passed to the
`EntityManagerFactory`. Hibernate calls `getConnection()` lazily
(at first query) rather than eagerly (at `@Transactional` entry).
This is an underdocumented optimization that solves a real ordering
problem.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **CHOOSE** between multiple EMF and `AbstractRoutingDataSource`
   for a given use case (different schemas vs read/write split)
2. **EXPLAIN** why the ThreadLocal must be set BEFORE `@Transactional`
   and how `LazyConnectionDataSourceProxy` changes this
3. **CONFIGURE** a basic read/write routing DataSource in Spring Boot
   with proper AOP aspect ordering
4. **EXPLAIN** why two `EntityManagerFactory` beans cannot participate
   in one `@Transactional` without JTA
5. **COMPARE** JTA vs Saga for cross-DataSource atomicity and
   recommend when each is appropriate

---

### 🎯 Interview Deep-Dive

**Q1: You need to implement read/write splitting in a Spring Boot
app: reads to a PostgreSQL replica, writes to the primary. How
would you implement this with JPA?**
_Why they ask:_ Tests practical multi-DataSource architecture knowledge.
_Strong answer includes:_

- Use `AbstractRoutingDataSource` extending class with `determineCurrentLookupKey()`
- Two target DataSources: `primaryDataSource`, `replicaDataSource` (both HikariCP pools)
- Routing key stored in `ThreadLocal` (custom `DataSourceContext` class)
- AOP `@Aspect` with `@Order(1)` (lower order = higher precedence) that:
  sets `READ` key for `@Transactional(readOnly=true)` methods BEFORE the transaction proxy
- Transaction proxy (`@Order(2)`) fires next, calls `getConnection()`,
  which calls `determineCurrentLookupKey()` -> routes to correct DataSource
- Single `EntityManagerFactory` using the routing `DataSource` as its source
- Mention: `LazyConnectionDataSourceProxy` wrapping to defer connection acquisition
- Caveat: replication lag (~10-100ms); reads immediately after writes may see stale data;
  consider "sticky primary" for requests that just performed a write

**Q2: A team member wants to connect to two completely separate
databases (orders-db and inventory-db) in one Spring Boot service.
What configuration approach would you recommend, and what are the
transaction management implications?**
_Why they ask:_ Tests multiple EMF knowledge and transaction boundary understanding.
_Strong answer includes:_

- Approach: two separate `DataSource` beans, two `LocalContainerEntityManagerFactoryBean`,
  two `JpaTransactionManager` beans
- Entity scanning: configure each EMF to scan separate package
  (`com.example.orders.domain`, `com.example.inventory.domain`) - prevents entity conflicts
- `@Primary` on one set of beans (Spring Data repositories auto-wire to @Primary)
- Non-primary: `@Transactional("inventoryTxManager")` must be explicit
- Transaction implication: `@Transactional("ordersTxManager")` is local to orders-db only;
  if same method also calls inventory-db under a different TM, these are TWO INDEPENDENT TRANSACTIONS
- Cross-DB atomicity NOT guaranteed without JTA
- Recommendation for the team: avoid cross-DB writes in single service method where possible;
  use event-driven Saga if consistency is required; JTA if true atomicity is needed and
  throughput allows (2PC overhead)
