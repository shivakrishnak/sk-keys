---
id: JPH-034
title: "Second Level Cache (Ehcache, Redis)"
category: JPA & Hibernate
tier: tier-3-java
folder: JPH-jpa-hibernate
difficulty: ★★★
depends_on: JPH-012, JPH-013, JPH-026, JPH-031, JPH-033
used_by: JPH-035, JPH-046, JPH-048, JPH-054, JPH-058
related: JPH-037, JPH-047
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
nav_order: 34
permalink: /technical-mastery/jpa-hibernate/second-level-cache/
---

⚡ **TL;DR** - The second-level cache (2LC) is a shared,
application-scoped cache for entity data that persists
across transactions and sessions. Unlike the first-level
cache (per-transaction), the 2LC is shared by all
sessions in the JVM (or across nodes with Redis/Hazelcast).
Enable with `@Cache(usage=CacheConcurrencyStrategy.READ_WRITE)` on an entity. The 2LC trades cache invalidation complexity
for reduced database load on frequently-read, rarely-
modified entities (reference data, lookups, configuration).
Never cache mutable high-write entities.

| #034            | Category: JPA & Hibernate                                                                                    | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Persistence Context, Entity Lifecycle, @Transactional, Hibernate Session vs EntityManager, First Level Cache |                 |
| **Used by:**    | Query Cache, Hibernate Statistics, Multi-Tenancy, JPA at Scale, Hibernate Internals                          |                 |
| **Related:**    | EntityGraph, Connection Pooling                                                                              |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A web application serves product catalog requests.
Every HTTP request that needs `em.find(Country.class, "US")`
(country lookup), `em.find(Currency.class, "USD")`,
or `em.find(ProductCategory.class, 5L)` issues a
database SELECT. These entities never change. With 1,000
requests/second, this is 1,000+ redundant DB queries per
second for data that is identical every time.

**THE PERFORMANCE WALL:**
At high traffic, the database becomes the bottleneck
even though it is serving the same data repeatedly.
Connection pool exhaustion happens even for "read-only"
reference data. The application scales up replicas, but
each replica hits the DB for the same lookup data.

**THE 2LC SOLUTION:**
The second-level cache stores entity data in a shared,
application-scoped cache (Ehcache in-process, Redis
distributed). After the first load, subsequent
`em.find(Country.class, "US")` in ANY session returns
the cached data without hitting the database. The cache
is populated on first access and invalidated when the
entity is modified. For reference data that changes once
a week, the hit rate approaches 99.9%.

---

### 📘 Textbook Definition

**Second Level Cache (2LC)** is an optional, application-
scoped cache in Hibernate that stores entity state across
sessions and transactions. Unlike the first-level cache
(scoped to one persistence context), the 2LC is shared:
data loaded by Session A is available to Session B,
Session C, and across HTTP requests.

**Cache Concurrency Strategies** (choose per entity):

- `READ_ONLY`: no updates; cache never invalidated. Best for immutable reference data. Highest performance.
- `READ_WRITE`: updates invalidate the cache; soft-lock mechanism prevents stale reads. Suitable for entities that are updated occasionally.
- `NONSTRICT_READ_WRITE`: no locking; race condition window during updates. Suitable for data where brief staleness is acceptable.
- `TRANSACTIONAL` (JTA only): full transactional cache; most expensive; requires JTA transaction manager.

**Cache Providers:** Hibernate supports pluggable cache providers:

- **Ehcache** (in-process): `hibernate-ehcache` dependency; local JVM heap cache; no network overhead
- **Caffeine** (in-process): modern successor to Guava Cache; high throughput
- **Redis** (distributed, via Redisson/Spring Cache): shared across cluster nodes; invalidation propagated
- **Hazelcast** (distributed, in-memory grid): cluster-wide cache with data replication

---

### ⏱️ Understand It in 30 Seconds

**One line:** The 2LC is a shared cache for entity data
that persists across transactions - `em.find()` checks
the 2LC before hitting the database in any session.

**One analogy:**

> The first-level cache is your personal notepad during
> one meeting (transaction). The second-level cache is
> the whiteboard in the office kitchen - shared by everyone,
> persists between meetings, and shows frequently-needed
> information. You write on it once (first DB query), and
> everyone reads from it without going to the source
> (database) until the information changes (cache invalidation).

**One insight:** The 2LC is NOT a cure-all. It only helps
for entities loaded by primary key (`em.find()`). JPQL
queries do NOT use the 2LC by default (the Query Cache
handles that separately - JPH-035). For mutable, high-
write entities, the cache invalidation cost exceeds the
benefit.

---

### 🔩 First Principles Explanation

**2LC DATA FLOW:**

```
Request 1 (Session A): em.find(Country.class, "US")
  1. Check 1LC (Session A): NOT found
  2. Check 2LC: NOT found (first access)
  3. Execute: SELECT * FROM countries WHERE code='US'
  4. Store in 2LC: key="Country#US", value={name:"United
    States",...}
  5. Store in 1LC (Session A)
  6. Return entity

Request 2 (Session B): em.find(Country.class, "US")
  1. Check 1LC (Session B): NOT found (different session)
  2. Check 2LC: FOUND key="Country#US"
  3. Deserialize/retrieve from 2LC
  4. Return entity (NO DB query)

em.merge(countryUS):  // UPDATE fired
  1. Hibernate updates DB
  2. INVALIDATES 2LC entry for Country#US
     (or updates it with new values in READ_WRITE)
  3. Next request: cache miss -> DB query -> re-populate
    2LC
```

**CACHE CONCURRENCY STRATEGY DETAILS:**

```
READ_ONLY (immutable reference data):
  - Entry stored once; never invalidated
  - Attempting to update -> exception in strict mode
  - Highest performance; no lock overhead

READ_WRITE (occasionally modified):
  - On update: Hibernate acquires a "soft lock" on the
    cache entry, preventing reads of the stale copy
  - After commit: cache entry updated with new data
  - Soft lock released; reads resume from new cached value
  - Prevents stale reads at cost of soft-lock mechanism

NONSTRICT_READ_WRITE:
  - Cache entry removed after update (not locked)
  - Small window: concurrent reader might see stale data
    between DB update and cache invalidation
  - Acceptable for data that can be briefly stale
```

---

### 🧪 Thought Experiment

**DISTRIBUTED CACHE INVALIDATION PROBLEM:**

```
Cluster with 3 JVM instances:

Instance 1 (Ehcache in-process):
  Cache: Country#US = {name: "United States"}

Instance 2 (Ehcache in-process):
  Cache: Country#US = {name: "United States"}

Instance 3 updates country US:
  UPDATE countries SET name='USA' WHERE code='US'
  Invalidates: Instance 3's Ehcache entry

Problem: Instance 1 and Instance 2 still cache the OLD
  value
"United States". They are STALE.

With Ehcache in-process:
  - No cross-instance invalidation
  - Stale cache for up to cache.expiry (e.g., 30 minutes)
  - Acceptable only if brief staleness is tolerable

With Redis (distributed via Redisson):
  - Invalidation message published to Redis pub/sub
  - All instances subscribe; invalidate their local copy
  - Cross-instance consistency
  - Cost: network round-trip for every 2LC operation
```

**CHOOSING IN-PROCESS vs DISTRIBUTED:**

- **In-process (Ehcache)**: zero network latency; data may
  be stale on other nodes; fine for single-node or
  infrequently-changed data
- **Distributed (Redis/Hazelcast)**: consistent across
  nodes; adds network hop per 2LC operation; needed for
  clustered apps where invalidation must propagate

---

### 🧠 Mental Model / Analogy

> The 2LC is like a city library's quick-reference shelf
> (vs the full archives in the basement). Common reference
> books (immutable entities: countries, currencies) sit
> on the quick shelf - anyone grabs them instantly without
> requesting from the archives (DB). Occasionally-updated
> books (READ_WRITE entities) are locked when being
> replaced, preventing someone from reading a half-changed
> edition. The distributed cache is a city-wide network
> of libraries where any update in one branch is instantly
> reflected in all branches.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
The 2LC stores entity data in memory, shared across all
database requests. If the same entity is loaded many
times across many requests, the 2LC serves it from memory
after the first load, saving database trips.

**Level 2 - How to enable it (junior developer):**
Add `@Cache(usage = CacheConcurrencyStrategy.READ_WRITE)`
to an entity class. Configure the cache provider (Ehcache,
Caffeine) in `application.properties`. Enable the 2LC
globally: `spring.jpa.properties.hibernate.cache.use_second_level_cache=true`.

**Level 3 - How it works (mid-level engineer):**
The 2LC stores a disassembled (serialized) form of entity
state keyed by entity type + primary key. When `em.find()`
is called, Hibernate checks the 2LC before issuing SQL.
On `merge()`/flush with dirty entity, Hibernate invalidates
or updates the 2LC entry based on the concurrency strategy.
The 2LC region is configured per-entity with TTL (time-to-live) and max size.

**Level 4 - Strategy selection (senior/staff):**
Match concurrency strategy to entity mutation rate:

- `READ_ONLY` for immutable lookup tables (country, currency, product categories that never change)
- `READ_WRITE` for infrequently-updated reference data
- Avoid 2LC for: high-write entities (orders, inventory), entities with fine-grained updates, entities where stale reads cause business logic bugs
- Monitor cache hit rate (`Statistics.getEntityRegionStatistics()`); below 80% hit rate = cache isn't helping

**Level 5 - Architecture (distinguished engineer):**
The 2LC fundamentally changes the read path semantics.
With the 2LC disabled: reads always reflect committed DB
state. With the 2LC enabled: reads reflect DB state at
time of last cache population, which may be minutes or
hours old depending on TTL and mutation rate. For
financial or inventory data, this is unacceptable - a
product showing "in stock" when the warehouse is empty
because the 2LC cached the old quantity. The 2LC is
NEVER appropriate for transactional data that affects
business decisions at read time. Use it exclusively for
true reference data where the application can tolerate
eventual consistency.

---

### ⚙️ How It Works (Mechanism)

**EHCACHE CONFIGURATION (Spring Boot):**

```xml
<!-- ehcache.xml -->
<ehcache>
  <cache name="com.example.Country"
         maxEntriesLocalHeap="1000"
         timeToLiveSeconds="86400"
         timeToIdleSeconds="3600">
    <!-- 1000 entries; 24h TTL; 1h idle TTL -->
  </cache>

  <cache name="com.example.ProductCategory"
         maxEntriesLocalHeap="500"
         timeToLiveSeconds="3600"/>
</ehcache>
```

**application.properties:**

```properties
spring.jpa.properties.hibernate.cache.use_second_level_cache=true
spring.jpa.properties.hibernate.cache.region.factory_class=\
  org.hibernate.cache.ehcache.EhcacheRegionFactory
spring.jpa.properties.hibernate.cache.use_query_cache=false

# Statistics (for monitoring):
spring.jpa.properties.hibernate.generate_statistics=true
```

**ENTITY ANNOTATION:**

```java
@Entity
@Cache(usage = CacheConcurrencyStrategy.READ_WRITE)
public class ProductCategory {
    @Id private Long id;
    private String name;
    private String code;
}

// READ_ONLY (immutable; fastest):
@Entity
@Cache(usage = CacheConcurrencyStrategy.READ_ONLY)
public class Country {
    @Id private String code;
    private String name;
}
```

---

### 🔄 The Complete Picture - End-to-End Flow

**CACHE STATISTICS MONITORING:**

```java
// Hibernate statistics for 2LC monitoring:
@Component
public class CacheMonitor {

    @PersistenceUnit
    private EntityManagerFactory emf;

    public void logCacheStats() {
        Statistics stats = emf.unwrap(SessionFactory.class)
            .getStatistics();

        CacheRegionStatistics region =
            stats.getDomainDataRegionStatistics(
                "com.example.Country");

        log.info("2LC hit ratio: {}/{}",
            region.getHitCount(),
            region.getHitCount() + region.getMissCount());
        // Target: >80% hit ratio for justified caching
        // Below 50%: cache is not helping; consider removing
    }
}
```

---

### 💻 Code Example

**Example 1 - Entity with 2LC setup:**

```java
// READ_WRITE: updated infrequently
@Entity
@Table(name = "product_categories")
@Cache(usage = CacheConcurrencyStrategy.READ_WRITE,
       region = "productCategoryCache")
public class ProductCategory {
    @Id @GeneratedValue
    private Long id;

    @Column(nullable = false, unique = true)
    private String name;

    // @OneToMany collection can also be cached:
    @OneToMany(mappedBy = "category")
    @Cache(usage = CacheConcurrencyStrategy.READ_WRITE)
    private List<Product> products;
}

// READ_ONLY: immutable after initial data load
@Entity
@Table(name = "countries")
@Cache(usage = CacheConcurrencyStrategy.READ_ONLY)
public class Country {
    @Id
    @Column(length = 2)
    private String code;      // "US", "GB"
    private String name;      // "United States"
    private String currency;  // "USD"
}
```

**Example 2 - BAD: caching a high-write entity:**

```java
// BAD: Order is a high-write entity
// Cache is invalidated on every status update
// (paid, shipped, delivered, returned...)
// -> cache is always COLD for order entities
// -> cache invalidation overhead with zero benefit
@Entity
@Cache(usage = CacheConcurrencyStrategy.READ_WRITE)
public class Order {
    @Id private Long id;
    private String status; // changes frequently
    private BigDecimal total;
}
// 2LC hurts here: adds serialization/deserialization
// overhead for every write with no read benefit
// REMOVE @Cache from high-write entities

// GOOD: only cache truly reference/lookup data
// Orders: NO cache
// ProductCategory: YES cache (READ_WRITE)
// Country: YES cache (READ_ONLY)
```

**Example 3 - Verifying 2LC hit in code:**

```java
@Autowired
private EntityManagerFactory emf;

public void verifyCacheHit(Long catId) {
    SessionFactory sf = emf.unwrap(SessionFactory.class);
    Statistics stats = sf.getStatistics();
    stats.setStatisticsEnabled(true);

    long missBefore = stats.getSecondLevelCacheMissCount();

    // First load: cache miss -> DB query
    em.find(ProductCategory.class, catId);

    // Second load in same or different session: cache hit
    em.clear(); // clear 1LC to force 2LC check
    em.find(ProductCategory.class, catId);

    long missAfter = stats.getSecondLevelCacheMissCount();
    // missAfter == missBefore + 1 (only first call was a miss)
    // Confirm: only 1 miss for 2 loads
}
```

---

### ⚖️ Comparison Table

| Strategy             | Concurrency  | Invalidation      | Use case                            |
| -------------------- | ------------ | ----------------- | ----------------------------------- |
| READ_ONLY            | None needed  | Never (immutable) | Countries, currencies, status codes |
| READ_WRITE           | Soft lock    | On UPDATE         | Infrequently changed lookup data    |
| NONSTRICT_READ_WRITE | None         | Remove on UPDATE  | Data where brief staleness is OK    |
| TRANSACTIONAL        | Full XA lock | On TX commit      | Critical consistent data (JTA only) |

| Provider             | Scope   | Network latency | Best for                           |
| -------------------- | ------- | --------------- | ---------------------------------- |
| Ehcache (local)      | JVM     | Zero            | Single-node or tolerable staleness |
| Caffeine (local)     | JVM     | Zero            | High-throughput single-node        |
| Redis (via Redisson) | Cluster | ~1ms            | Multi-node consistent cache        |
| Hazelcast            | Cluster | ~1ms            | Multi-node with data grid features |

---

### ⚠️ Common Misconceptions

| Misconception                                                      | Reality                                                                                                                                                                                                        |
| ------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "The 2LC caches JPQL query results"                                | The 2LC caches entity state by primary key. JPQL query results are cached by the Query Cache (a separate, additional feature). They work independently.                                                        |
| "Enabling the 2LC is always a performance improvement"             | For high-write entities, the 2LC adds serialization overhead on every write and rarely gets cache hits. Net result: slower. Enable 2LC only on low-write, high-read entities.                                  |
| "The 2LC is consistent across JVM instances without configuration" | In-process caches (Ehcache, Caffeine) are NOT shared across JVM instances. Updates in one JVM leave stale entries in others. For cluster-consistent 2LC, use a distributed cache (Redis, Hazelcast).           |
| "@Cache on an entity also caches its collections"                  | `@Cache` on an entity caches the entity itself. Collections (`@OneToMany`) require a SEPARATE `@Cache` annotation on the collection field to be cached. Without it, collections are always loaded from the DB. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Stale Data Served to Clients**

**Symptom:** Users see outdated product category names
or stale prices after an admin update. The database
shows the new value but the API returns the old one.

**Root Cause:** The entity is cached with a long TTL.
The admin update committed to the database, but the 2LC
entry was not properly invalidated (e.g., update was done
via native SQL/bulk DML bypassing Hibernate's cache
invalidation).

**Diagnosis:** Check if the update path uses
`@Modifying @Query` (native SQL bypasses cache invalidation)
or if the Hibernate session that ran the update is the
same process as the reader.

**Fix:**

- If native SQL is used for updates: call `em.clear()` or
  evict the cache region explicitly:
  ```java
  emf.getCache().evict(ProductCategory.class, categoryId);
  ```
- Use a shorter TTL for entities that can be updated
- Set `READ_WRITE` strategy (not `READ_ONLY`) for mutable entities

---

**Failure Mode 2: 2LC Not Being Used (Zero Hit Rate)**

**Symptom:** `Statistics.getSecondLevelCacheHitCount()` is 0.

**Root Cause (common):**

1. `@Cache` annotation missing on entity
2. `hibernate.cache.use_second_level_cache=false` in config
3. Cache provider JAR missing from classpath
4. `@Cache` on entity but not on collections being accessed
   **Fix:** Check all four above. Verify via:

```java
stats.getDomainDataRegionStatistics("com.example.Country")
    .getHitCount();
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[JPH-033 - First Level Cache]] - understand 1LC first;
  2LC complements it
- [[JPH-026 - @Transactional]] - transaction boundaries
  affect when 2LC entries are invalidated

**Builds On This (learn these next):**

- [[JPH-035 - Query Cache]] - caches JPQL query results;
  uses 2LC infrastructure
- [[JPH-046 - Hibernate Statistics and Monitoring]] -
  monitoring 2LC hit rates

**Related:**

- [[JPH-047 - Connection Pooling with JPA (HikariCP)]] -
  2LC reduces DB load; both are database pressure mitigations
- [[JPH-054 - JPA at Scale]] - 2LC strategy in distributed systems

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ ENABLE       │ @Cache(usage=READ_WRITE) on entity       │
│              │ hibernate.cache.use_second_level_cache=tr│
├──────────────┼──────────────────────────────────────────┤
│ STRATEGIES   │ READ_ONLY (immutable data, fastest)      │
│              │ READ_WRITE (infrequent updates, safe)    │
│              │ NONSTRICT (brief staleness tolerable)    │
├──────────────┼──────────────────────────────────────────┤
│ GOOD TARGETS │ Countries, currencies, product types,    │
│              │ config values, status codes              │
├──────────────┼──────────────────────────────────────────┤
│ BAD TARGETS  │ Orders, inventory, payments, user data   │
│              │ (high-write = cache is always invalidated│
├──────────────┼──────────────────────────────────────────┤
│ CLUSTER      │ In-process (Ehcache): stale on other JVMs│
│              │ Distributed (Redis): consistent cluster  │
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "2LC = application-scoped entity cache.  │
│              │ Shared across sessions. Use for low-write│
│              │ high-read reference data only."          │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. The 2LC is shared across all sessions/transactions;
   unlike the 1LC, it persists between HTTP requests
2. Only cache low-write, high-read reference entities
   (`READ_ONLY` for immutable, `READ_WRITE` for occasionally
   updated); never cache transactional data
3. In-process (Ehcache) caches are not cluster-consistent;
   use Redis or Hazelcast for multi-node deployments

**Interview one-liner:** The second-level cache is Hibernate's
application-scoped entity cache, shared across sessions.
Configured per entity with `@Cache`. Suitable for rarely-
modified reference data (countries, categories); not
suitable for frequently-updated transactional entities.
In-process providers (Ehcache) are JVM-local; distributed
providers (Redis via Redisson) sync across cluster nodes.
Monitor via Hibernate statistics; target >80% hit rate.

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Cache only what is
worth caching: data that is read frequently, changes rarely,
and where stale reads are tolerable. The cost of a cache
is not just memory - it is the complexity of cache
invalidation, the risk of serving stale data, and the
operational overhead of monitoring hit rates and tuning
TTLs. "Cache everything" is an anti-pattern. "Cache
reference data that is accessed >100x per mutation" is
a sound heuristic. This principle applies to all caching
layers: database query cache, CDN edge caching, HTTP
response caching (`Cache-Control: max-age`), DNS TTL,
and in-memory maps in microservices.

**Where else this pattern appears:**

- **HTTP caching** - `Cache-Control: max-age=86400` on
  static assets; only practical for rarely-changing content
- **DNS TTL** - DNS records have TTL; lower TTL = more
  queries; higher TTL = staler data after IP change
- **CDN edge caching** - only cache assets that are safe
  to serve stale (images, JS bundles); never cache
  personalized or authenticated responses
- **Redis application cache** - `@Cacheable` in Spring;
  same trade-off: read throughput vs staleness

---

### 💡 The Surprising Truth

The Hibernate 2LC does NOT automatically evict entries
when records are modified by another application, a batch
script, or a stored procedure that bypasses Hibernate.
If your database is updated by Python scripts, DBA SQL
queries, or direct JDBC (not through the same Hibernate
session that populated the cache), those updates are
invisible to the 2LC. The cache will serve stale data
until TTL expires. This is the most common source of
"the database has the right data but the app shows the
wrong data" bugs in production. The fix: either route
ALL writes through Hibernate (so cache invalidation fires),
or use a short TTL (to limit staleness window), or disable
the 2LC for entities that have external write paths.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **CONFIGURE** the 2LC for an entity using Ehcache with
   `READ_WRITE` strategy and verify the hit rate via
   Hibernate statistics
2. **CHOOSE** the correct concurrency strategy for four
   different entity types with different mutation rates
3. **EXPLAIN** why in-process 2LC causes staleness in
   a 3-node cluster and describe the Redis alternative
4. **DIAGNOSE** stale 2LC data after a bulk update
   bypassing Hibernate and implement the eviction fix
5. **DECIDE** which entities in a given domain model
   are appropriate 2LC candidates and justify the choice

---

### 🎯 Interview Deep-Dive

**Q1: What is the difference between the first-level
cache and the second-level cache in Hibernate?**
_Why they ask:_ Core Hibernate caching knowledge; tests
understanding of scope and purpose.
_Strong answer includes:_

- 1LC (first-level): scoped to one Session/transaction;
  always enabled; cannot be shared; cleared at TX end
- 2LC (second-level): application-scoped; shared across
  all sessions; optional; configured per entity; persists
  across transactions
- Together: 1LC absorbs within-transaction redundant loads;
  2LC absorbs cross-transaction redundant loads for reference data
- 2LC requires explicit opt-in via `@Cache`; choosing wrong
  entities to cache causes staleness

**Q2: When would you NOT use the second-level cache?**
_Why they ask:_ Tests understanding of when the cache
creates problems rather than solving them.
_Strong answer includes:_

- High-write entities: orders, inventory - every write
  invalidates the cache; hit rate approaches 0%; adds
  serialization overhead with no read benefit
- Financial/inventory data where stale reads cause business
  errors: showing "in stock" when cache is stale
- Entities modified by external processes (batch scripts,
  stored procs, other apps): 2LC not notified of changes
- In clustered deployments with in-process cache (Ehcache)
  and no distributed invalidation: stale data on other nodes
- Short-lived entities: sessions, tokens, queued messages -
  TTL makes no sense for short-lived data

**Q3: How does the second-level cache interact with
cluster deployments?**
_Why they ask:_ Tests architectural awareness for distributed systems.
_Strong answer includes:_

- In-process caches (Ehcache): each JVM has independent cache;
  updates on one node do NOT invalidate others; stale data
  persists until TTL expires or the entry is evicted on that node
- Distributed caches (Redis via Redisson, Hazelcast): cache
  entries stored in shared cache; invalidation propagates
  to all nodes via pub/sub or cluster protocol; consistent
  across nodes at cost of network latency per cache operation
- Trade-off: in-process = zero latency, possible staleness;
  distributed = ~1ms latency, consistent
- Recommendation: Ehcache for entities updated less than
  once per hour and where brief staleness is tolerable;
  Redis for entities updated more frequently in multi-node
