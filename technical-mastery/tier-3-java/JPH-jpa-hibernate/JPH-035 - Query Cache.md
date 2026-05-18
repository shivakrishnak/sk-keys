---
id: JPH-035
title: Query Cache
category: JPA & Hibernate
tier: tier-3-java
folder: JPH-jpa-hibernate
difficulty: ★★☆
depends_on: JPH-014, JPH-026, JPH-033, JPH-034
used_by: JPH-046, JPH-058
related: JPH-028, JPH-036
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
nav_order: 35
permalink: /technical-mastery/jpa-hibernate/query-cache/
---

⚡ **TL;DR** - The Hibernate Query Cache caches JPQL/HQL
query result sets (not entity data - the 2LC does that).
The cache key = (query string, parameters, sort). On
a cache hit, Hibernate returns the cached list of entity
IDs, then looks up each entity from the 2LC (or database).
Requires the 2LC to be enabled and the entity to be
`@Cache`-annotated. Useful only for expensive queries
with stable parameters. Almost never worth the complexity.

| #035            | Category: JPA & Hibernate                                   | Difficulty: ★★☆ |
| :-------------- | :---------------------------------------------------------- | :-------------- |
| **Depends on:** | JPQL, @Transactional, First Level Cache, Second Level Cache |                 |
| **Used by:**    | Hibernate Statistics, Hibernate Internals                   |                 |
| **Related:**    | HQL, Criteria API                                           |                 |

---

### 🔥 The Problem This Solves

**THE SCENARIO WHERE IT HELPS:**
An application has a dashboard showing "Top 10 most popular
products". The query runs a `GROUP BY + COUNT + ORDER BY`
that takes 500ms on a large orders table. The results
change at most once per day. Without the query cache,
every dashboard page load re-runs this expensive 500ms
query. With the query cache: the first request runs the
SQL, subsequent requests return the cached result in <1ms.

**WHY IT'S RARELY WORTH IT:**
The query cache is only useful for a very specific pattern:

- Expensive query
- Identical parameters on repeated calls
- Results are stable (don't change often)
- The result set entities are also in the 2LC

This pattern describes at most 5-10% of queries in a
typical application. For the other 90%, the query cache
adds complexity with zero benefit. Spring's `@Cacheable`
is simpler and more flexible for most caching needs.

---

### 📘 Textbook Definition

**Hibernate Query Cache** caches the result of a JPQL/HQL
query as a list of primary keys (or scalar values for
scalar queries). On subsequent identical calls, Hibernate
returns the cached key list and then fetches each entity
from the second-level cache (or database if not in 2LC).

**Key characteristics:**

- Requires `hibernate.cache.use_query_cache=true`
- Requires the 2LC to be enabled AND the entity to be `@Cache`-annotated
- Cache key = (SQL string + bind parameter values + first result + max results)
- Stores entity IDs, not entity state (entity state is in 2LC)
- Invalidated when any entity in the query's result type is modified
- Configured separately from 2LC regions

---

### ⏱️ Understand It in 30 Seconds

**One line:** The Query Cache stores query result IDs
between sessions; on cache hit, Hibernate still needs
the entities from the 2LC (or DB).

**One analogy:**

> The query cache is like a cached search results page
> that remembers "searching for 'laptops' returns product
> IDs [101, 205, 307]". The products themselves are in
> the 2LC (product storage). On cache hit: results page
> retrieved in 0ms; products fetched from 2LC in 1ms.
> Without the query cache: search runs the database query
> (100ms), then fetches products.

**One insight:** The query cache rarely helps because
most queries have varying parameters (different user
IDs, date ranges, etc.) that make each query cache key
unique - no hits. And when parameters DO match, Spring's
`@Cacheable` at the service method level is simpler and
more explicit.

---

### 🔩 First Principles Explanation

**QUERY CACHE STRUCTURE:**

```
Cache key:
  QueryKey = (SQL string, parameter values, first, max,
    sort)

Cache value:
  QueryResultsCacheImpl.CacheValue =
    List<Serializable> entityIds  // for entity queries
  OR
    List<Object> scalarValues    // for scalar queries
  + timestamp of when results were cached

Example:
  Key: ("FROM Product p WHERE p.featured=true", [], 0, 10)
  Value: [101L, 205L, 307L, 412L]  (entity IDs)
```

**FULL QUERY CACHE LOOKUP FLOW:**

```
1. em.createQuery("FROM Product p WHERE p.featured=true")
     .setHint("org.hibernate.cacheable", true)
     .getResultList()

2. Compute QueryKey from query + params

3. Check QueryResultsRegion for QueryKey
   -> Cache HIT: return cached [101L, 205L, 307L, 412L]

4. For each ID in result list:
   -> Check 2LC for (Product.class, 101L)
      -> 2LC HIT: return Product#101 (no DB query)
      -> 2LC MISS: SELECT * FROM products WHERE id=101
   -> Repeat for each ID

5. If ANY ID is a 2LC miss: DB query fires for that entity
   So: query cache + 2LC MISS = more queries than no cache!
```

**INVALIDATION:**

```
Any INSERT/UPDATE/DELETE on a Product entity
-> Hibernate timestamps the "Product" entity region
-> Next query cache check: compares timestamps
-> If entity region is newer than query cache entry: STALE
-> Query cache entry evicted; query re-executed
```

---

### 🧪 Thought Experiment

**THE PARADOX: QUERY CACHE + NO 2LC = SLOWER:**

```
Scenario: Query cache hit for IDs [101, 205, 307]
          BUT entities are NOT in the 2LC

Without query cache:
  1. SELECT id, name, price FROM products WHERE
    featured=true
     -> 1 SQL query, returns 3 rows, 3 entities loaded
  Total: 1 SQL query

With query cache hit + no 2LC:
  1. Query cache returns [101, 205, 307] (no SQL for query)
  2. For Product#101: not in 2LC -> SELECT WHERE id=101
  3. For Product#205: not in 2LC -> SELECT WHERE id=205
  4. For Product#307: not in 2LC -> SELECT WHERE id=307
  Total: 3 SQL queries (N+1 problem!)

CONCLUSION: Query cache without 2LC = N+1 problem
The query cache is ONLY useful when the entity is ALSO
in the 2LC (@Cache annotated AND 2LC enabled).
```

---

### 🧠 Mental Model / Analogy

> The query cache is a restaurant's "special of the day"
> board that lists dish IDs. When a customer asks "what
> are today's specials?", the waiter reads the board
> (cache hit) instead of going to the kitchen to check
> (DB query). Then they fetch the actual dishes from
> the warming station (2LC) by ID. But if the dishes
> aren't on the warming station (no 2LC), the waiter
> still has to go to the kitchen for each dish - now
> making more trips than if they'd just asked the kitchen
> for "all specials" directly.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
The Query Cache remembers the results of specific
database queries. If the same query is run with the same
parameters, it returns the cached results without hitting
the database.

**Level 2 - How to enable it (junior developer):**

1. Enable 2LC: `hibernate.cache.use_second_level_cache=true`
2. Enable query cache: `hibernate.cache.use_query_cache=true`
3. Annotate entity with `@Cache`
4. Mark query as cacheable: `.setHint("org.hibernate.cacheable", true)`

**Level 3 - How it works (mid-level engineer):**
The query cache stores a list of entity IDs (or scalar
values) for a given query+parameter combination. On cache
hit, Hibernate looks up each entity from the 2LC.
If the entity is not in the 2LC, it issues individual
SELECT queries - potentially creating N+1 behavior.
The cache is invalidated whenever any entity in the
query's result type is modified.

**Level 4 - When to use it (senior/staff):**
Only use the query cache for: (1) expensive queries with
stable parameters (same parameters called many times),
(2) entities that are also in the 2LC (`@Cache`-annotated),
(3) query results that don't change often (reference data
queries: `findAllCountries()`, `findAllCategories()`).
For most application queries: Spring's `@Cacheable` on the
service method is simpler and does not require 2LC setup.

**Level 5 - Why it's rarely used (distinguished engineer):**
The query cache is one of the most misunderstood and
misused features in Hibernate. It requires TWO configured
caches (2LC + query results), specific query hints, and
its invalidation strategy (any change to the entity type
invalidates ALL queries of that type) is extremely coarse.
In practice, a `@Cacheable` annotation on a service method
that calls the expensive query is: simpler to implement,
more predictable in invalidation, works without 2LC,
and supports programmatic eviction. The query cache is
a Hibernate-era feature predating Spring Cache abstraction;
use `@Cacheable` instead.

---

### ⚙️ How It Works (Mechanism)

**CONFIGURATION:**

```properties
# Required: second-level cache must be enabled
spring.jpa.properties.hibernate.cache.use_second_level_cache=true
spring.jpa.properties.hibernate.cache.region.factory_class=\
  org.hibernate.cache.ehcache.EhcacheRegionFactory

# Query cache specific:
spring.jpa.properties.hibernate.cache.use_query_cache=true

# Statistics (to verify cache hits):
spring.jpa.properties.hibernate.generate_statistics=true
```

**QUERY HINT:**

```java
// JPQL query with caching enabled:
List<ProductCategory> categories = em
    .createQuery("FROM ProductCategory c ORDER BY c.name",
                 ProductCategory.class)
    .setHint(QueryHints.HINT_CACHEABLE, true)
    // QueryHints.HINT_CACHEABLE = "org.hibernate.cacheable"
    .setHint(QueryHints.HINT_CACHE_REGION,
             "productCategoryQueryCache")
    // Optional: separate cache region name
    .getResultList();

// Spring Data @Query equivalent:
@QueryHints({@QueryHint(name = "org.hibernate.cacheable",
                        value = "true")})
@Query("FROM ProductCategory c ORDER BY c.name")
List<ProductCategory> findAllCached();
```

---

### 🔄 The Complete Picture - End-to-End Flow

**QUERY CACHE WITH 2LC - CORRECT SETUP:**

```java
// 1. Entity: cacheable via 2LC
@Entity
@Cache(usage = CacheConcurrencyStrategy.READ_WRITE)
public class ProductCategory {
    @Id private Long id;
    private String name;
}

// 2. Query: cached via Query Cache
@Repository
public interface ProductCategoryRepository
        extends JpaRepository<ProductCategory, Long> {

    @QueryHints({@QueryHint(
        name = "org.hibernate.cacheable",
        value = "true")})
    List<ProductCategory> findAllByOrderByName();
}

// 3. Monitor:
Statistics stats = emf.unwrap(SessionFactory.class)
    .getStatistics();
// On first call:
stats.getQueryCacheMissCount();  // +1 (cache miss)
stats.getQueryCacheHitCount();   // 0
// On second call (same query):
stats.getQueryCacheHitCount();   // +1 (cache HIT)
// CONFIRM: query cache working
```

---

### 💻 Code Example

**Example 1 - BAD: query cache without entity 2LC:**

```java
// BAD: query cache enabled but entity NOT @Cache-annotated
// -> query cache hit returns IDs
// -> entity lookup: NOT in 2LC -> N SELECT queries
// Net effect: worse than no cache!

@Entity
// @Cache MISSING <-- problem
public class ProductCategory { ... }

@QueryHints({@QueryHint(name="org.hibernate.cacheable",
                        value="true")})
List<ProductCategory> findAll();
// Cache hit returns [1L, 2L, 3L, 4L, 5L]
// Each ID causes: SELECT FROM product_categories WHERE id=?
// 5 DB queries instead of 1!
```

**Example 2 - GOOD: Spring @Cacheable (simpler alternative):**

```java
// Simpler: use Spring's @Cacheable instead of Hibernate QC
// No 2LC required; no query hints; full control

@Service
public class CategoryService {

    @Cacheable("categories")
    public List<CategoryDto> findAllCategories() {
        return categoryRepo.findAllByOrderByName()
            .stream()
            .map(CategoryDto::from)
            .collect(toList());
    }

    @CacheEvict(value = "categories", allEntries = true)
    public void updateCategory(Long id, String name) {
        category.setName(name);
        // Cache evicted; next call re-fetches from DB
    }
}
// application.properties:
// spring.cache.type=caffeine (or redis for cluster)
// spring.cache.caffeine.spec=maximumSize=1000,expireAfterWrite=1h
```

---

### ⚖️ Comparison Table

| Feature            | Hibernate Query Cache      | Spring @Cacheable           |
| ------------------ | -------------------------- | --------------------------- |
| Granularity        | Per query + parameters     | Per method call + key       |
| Requires 2LC?      | Yes (for entity queries)   | No                          |
| Invalidation       | Auto (any entity mutation) | Manual (@CacheEvict) or TTL |
| Complexity         | High (2 cache layers)      | Low (one annotation)        |
| Works for scalars? | Yes                        | Yes                         |
| Cluster support    | Via 2LC provider (Redis)   | Via Spring Cache (Redis)    |
| Recommended?       | Rarely                     | Default choice for caching  |

---

### ⚠️ Common Misconceptions

| Misconception                                              | Reality                                                                                                                                                                                                                                                                 |
| ---------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "The query cache stores full entity objects"               | The query cache stores only entity PRIMARY KEYS (or scalar values). Entity state is stored in the 2LC separately. A query cache hit still requires 2LC lookups for each ID.                                                                                             |
| "Enabling the query cache speeds up all queries"           | The query cache only caches queries marked with `org.hibernate.cacheable=true`. Unmarked queries are not cached. And for mutable data, the cache is constantly invalidated, providing zero benefit.                                                                     |
| "The query cache invalidates only for exact table matches" | The Hibernate query cache uses "table space" tracking. ANY modification to a Product entity invalidates ALL query cache entries that return Product results - regardless of whether the specific modified row appeared in the cached results. Very coarse invalidation. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode: Low Cache Hit Rate + Performance Regression**

**Symptom:** Enabling the query cache does not improve
performance. Statistics show high miss rate and the
overall query count has INCREASED.

**Root Cause:** Either (1) query parameters vary per
call (no two calls have the same key -> no hits), or
(2) entity is not in the 2LC -> every cache hit triggers
N individual SELECT queries (N+1), or (3) entity is
modified frequently -> cache is constantly invalidated.

**Diagnosis:**

```java
Statistics stats = sf.getStatistics();
long hits   = stats.getQueryCacheHitCount();
long misses = stats.getQueryCacheMissCount();
long puts   = stats.getQueryCachePutCount();
// If puts >> hits: cache is constantly invalidated
// or rarely reused
```

**Fix:** Remove the query cache hint; use `@Cacheable`
at the service layer, or redesign the query to reduce
mutations on the cached entity.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[JPH-034 - Second Level Cache]] - query cache requires
  2LC to be enabled and entity to be @Cache-annotated

**Builds On This (learn these next):**

- [[JPH-046 - Hibernate Statistics and Monitoring]] -
  monitoring query cache hit/miss rates

**Related:**

- [[JPH-028 - HQL]] - query cache works with HQL/JPQL
- [[JPH-036 - Criteria API]] - Criteria API queries can
  also be marked cacheable

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ REQUIRES     │ 2LC enabled + entity @Cache-annotated    │
│              │ hibernate.cache.use_query_cache=true     │
├──────────────┼──────────────────────────────────────────┤
│ MARK QUERY   │ .setHint("org.hibernate.cacheable","true"│
├──────────────┼──────────────────────────────────────────┤
│ WHAT'S CACHED│ Entity IDs (not entity data)             │
│              │ Entity data still needs to be in 2LC     │
├──────────────┼──────────────────────────────────────────┤
│ INVALIDATION │ Any modification to queried entity type  │
│              │ invalidates ALL related query cache entri│
├──────────────┼──────────────────────────────────────────┤
│ BETTER OPTION│ Spring @Cacheable at service layer       │
│              │ Simpler, more flexible, no 2LC required  │
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "Query Cache caches result IDs not data. │
│              │ Requires entity in 2LC. High complexity, │
│              │ coarse invalidation. Prefer @Cacheable." │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. The query cache stores entity IDs, not entity data -
   it still needs entities from the 2LC; without 2LC on
   the entity, a query cache hit causes N+1 queries
2. Invalidation is coarse: any modification to the entity
   type evicts ALL query cache entries for that type
3. Spring's `@Cacheable` at the service layer is simpler
   and usually preferable to Hibernate's query cache

**Interview one-liner:** The Hibernate Query Cache caches
JPQL/HQL result sets as entity ID lists. On cache hit,
entities are fetched from the 2LC. Requires both the 2LC
and entity `@Cache` annotation - without the entity in
the 2LC, a query cache hit causes N+1 queries. Invalidated
whenever any entity of the queried type is modified (coarse).
Spring's `@Cacheable` is simpler and more commonly used.

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Two-tier caching
(query results + entity state) is a powerful but complex
pattern. Complexity grows multiplicatively: two caches
to configure, two caches to monitor, two invalidation
paths, two sources of staleness. The general principle:
add caching layers incrementally, only when there is a
measured performance problem that cannot be solved by
query optimization first. "More caching" is not always
better - each layer adds failure modes. This principle
applies to: CDN + browser caching (two-tier for HTTP),
L1 + L2 CPU cache analogy (hardware-managed), Redis +
local Caffeine (application-layer two-tier cache). Each
tier must be justified by the problem it solves.

**Where else this pattern appears:**

- **CPU cache hierarchy** - L1/L2/L3 caches: exact same
  concept; inner cache stores IDs/addresses; outer stores
  data
- **Spring Cache abstraction** - `@Cacheable` at service
  layer; simpler than Hibernate query cache; same TTL/
  eviction concepts
- **Elasticsearch** - request cache caches query results
  as shard-level responses; similar invalidation issues

---

### 💡 The Surprising Truth

The Hibernate Query Cache has a known performance anti-
pattern called "cache bloat with parameter variations."
For a query like `findByStatus(String status)` with many
distinct status values, each unique status creates a
separate query cache entry. With 50 distinct statuses,
50 entries accumulate. If entities are modified frequently,
all 50 entries are invalidated simultaneously - causing
a cache stampede where all 50 are re-populated
concurrently. The query cache's LRU eviction then
removes older entries, and the whole cycle repeats.
This produces WORSE performance than no cache (due to
serialization overhead, invalidation cost, and cache
churn). The query cache is only a net win for queries
with a very small set of distinct parameter combinations
(ideally 1: `findAllActive()`).

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **CONFIGURE** the query cache correctly (2LC enabled,
   entity @Cache, query hint) and verify with statistics
2. **EXPLAIN** why query cache without entity 2LC causes
   N+1 queries instead of improving performance
3. **DESCRIBE** the coarse invalidation behavior (any
   mutation to entity type evicts all queries of that type)
4. **DECIDE** when Spring `@Cacheable` is preferable to
   the Hibernate query cache (and justify why)
5. **DIAGNOSE** a query cache that has near-zero hit rate
   and explain the root cause

---

### 🎯 Interview Deep-Dive

**Q1: What does the Hibernate Query Cache store, and
what does it need to work correctly?**
_Why they ask:_ Tests understanding of two-tier caching.
_Strong answer includes:_

- Query Cache stores: list of entity primary keys (not entity state)
- Requires: 2LC enabled AND entity annotated with `@Cache`
- Without entity in 2LC: cache hit returns IDs; each ID
  triggers `SELECT WHERE id=?` -> N+1 queries
- Query hint required: `org.hibernate.cacheable=true`
- Invalidated: any modification to the queried entity type
  evicts ALL related query cache entries

**Q2: When is Spring @Cacheable preferable to Hibernate
Query Cache?**
_Why they ask:_ Tests practical decision-making between
two caching approaches.
_Strong answer includes:_

- `@Cacheable`: no 2LC required; simpler setup; explicit
  cache keys; manual eviction with `@CacheEvict`; works
  for any service method result (DTOs, scalars, complex objects)
- Hibernate query cache: automatic invalidation (but coarse);
  integrated with entity lifecycle; only useful for entity
  queries where entities are also in 2LC
- Prefer `@Cacheable`: when caching DTOs/projections (not
  entities), when caching service-layer results, when
  invalidation needs to be explicit and precise
- Prefer query cache: almost never; the benefit is very
  narrow compared to complexity
