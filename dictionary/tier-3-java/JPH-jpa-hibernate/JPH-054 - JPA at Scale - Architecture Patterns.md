---
id: JPH-054
title: JPA at Scale - Architecture Patterns
category: JPA & Hibernate
tier: tier-3-java
folder: JPH-jpa-hibernate
difficulty: ★★★
depends_on: JPH-011, JPH-014, JPH-016, JPH-026, JPH-027, JPH-031, JPH-033, JPH-034, JPH-035, JPH-045, JPH-046, JPH-047, JPH-048, JPH-052
used_by: JPH-056
related: JPH-043, JPH-049, JPH-053, JPH-055, JPH-058
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
nav_order: 54
permalink: /jpa-hibernate/jpa-at-scale/
---

# JPH-054 - JPA at Scale - Architecture Patterns

⚡ **TL;DR** - At scale, JPA performance degrades in
predictable ways: N+1 queries, dirty checking overhead,
unbounded session size, connection pool exhaustion, and
2LC invalidation storms. The proven architectural
responses: (1) `@Transactional(readOnly=true)` for all
reads, (2) entity graphs or JOIN FETCH for association
loading, (3) projections (DTOs) instead of full entity
loads for reporting, (4) flush+clear cycle in batch
processing, (5) CQRS split (JPA for writes, JOOQ for
reads), (6) read replicas for read traffic.

| #054 | Category: JPA & Hibernate | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Entity Lifecycle, JPQL, Spring Data JPA, @Transactional, N+1 Problem, Persistence Context, First Level Cache, Second Level Cache, Query Cache, Batch Processing, Hibernate Statistics, Connection Pooling, Multi-Tenancy, Dirty Checking | |
| **Used by:** | Spring Data JPA Architecture Design | |
| **Related:** | Spring Data Specifications, Hibernate Envers, QueryDSL, ORM Selection Framework, Hibernate Internals | |

---

### 🔥 The Problem This Solves

**WHICH JPA PATTERNS BREAK AT SCALE:**

```
50 RPS (requests/sec) with Hibernate:
  - All queries complete in ~50ms
  - No visible issues

500 RPS same configuration:
  - Symptom 1: "Connection is not available" (pool=10 exhausted)
    Root: @Transactional methods holding connections during reports
  - Symptom 2: Response time spikes to 2s randomly
    Root: 2LC invalidation storm when bulk products update
  - Symptom 3: GC pressure, OOM on report endpoints
    Root: loading 50K entities for aggregations (no projections)
  - Symptom 4: N+1 visible in stats (100+ queries per request)
    Root: lazy loading triggered in view layer

5,000 RPS (with horizontal scaling):
  - ALL of the above, amplified
  - Plus: 2LC inconsistency across instances
  - Plus: DB master saturated with reads; replicas idle
```

None of these are "JPA is bad" - they are specific
patterns that require specific architectural responses.

---

### 📘 Textbook Definition

**JPA at scale** refers to architectural patterns for
running Hibernate/JPA effectively under high concurrent
load (hundreds to thousands of requests per second).

**Seven architectural patterns:**

| Pattern | Problem Solved | Implementation |
|---|---|---|
| Read-only transactions | Dirty check overhead | `@Transactional(readOnly=true)` on all reads |
| Projection queries | Entity load overhead for reports | DTO constructors in JPQL, Spring projections |
| CQRS split | Mixed read/write load | JPA for writes; JOOQ/JDBC for complex reads |
| Batch write optimization | High-volume inserts/updates | `batch_size`, `flush()+clear()`, StatelessSession |
| Read replicas | DB read saturation | `AbstractRoutingDataSource` to route reads |
| 2LC tuning | Cache thrashing | Region sizing, TTL per entity type |
| Connection pool tuning | Pool exhaustion | Reduce tx scope, tune `maximumPoolSize` |

---

### ⏱️ Understand It in 30 Seconds

**One line:** JPA at scale is a checklist of eight known
failure modes and their proven architectural responses,
applied systematically before performance problems hit
production.

**One analogy:**
> JPA at scale is like building a water distribution
> system for a city. The pipes (JDBC connections) have
> a max throughput. The reservoir (2LC) reduces demand
> on the source (DB). Dirty checking is like inspecting
> every pipe joint after every water usage (unnecessary
> for clean pipes). Projections are narrow pipes (only
> carry what's needed). The CQRS split is separating
> drinking water (writes to master) from irrigation
> (reads from replica). Each pattern reduces load on
> the bottleneck. No single fix; multiple patterns
> working together.

**One insight:** The most high-value JPA performance
optimization often has nothing to do with JPA: adding a
`WHERE` clause index to the most-queried table. Before
applying all JPA architectural patterns: run `EXPLAIN
ANALYZE` on the top 5 slowest queries. Missing indexes
are responsible for >50% of JPA performance issues
in production.

---

### 🔩 First Principles Explanation

**THE EIGHT FAILURE MODES AND THEIR FIXES:**

```
1. N+1 QUERIES (most common JPA issue)
   Symptom: 100+ queries for a "list orders" request
   Cause: lazy loading triggered for each entity
   Fix A: @EntityGraph or JOIN FETCH for known association patterns
   Fix B: batch fetch size (hibernate.default_batch_fetch_size=16)
   Fix C: explicit DTO projection (no association loading at all)

2. DIRTY CHECK OVERHEAD (read-heavy workloads)
   Symptom: 30-50ms overhead on "read-only" reports
   Cause: 1000+ entity snapshots created + compared at commit
   Fix: @Transactional(readOnly=true) on ALL read methods

3. SESSION GROWTH IN BATCH PROCESSING
   Symptom: OutOfMemoryError at 50,000 entities processed
   Cause: session accumulates all processed entities + snapshots
   Fix: em.flush(); em.clear(); every 50-100 entities

4. ENTITY LOADING FOR AGGREGATIONS
   Symptom: 2GB heap for monthly revenue report
   Cause: SELECT e FROM Entity e loading full entity objects
   Fix: JPQL aggregate: SELECT SUM(e.amount) FROM Entity e
         Or DTO projection: SELECT NEW dto(e.id, e.name) FROM Entity e

5. EAGER LOADING CARTESIAN PRODUCT
   Symptom: result set 10x larger than expected; slow queries
   Cause: JOIN FETCH on 2+ collection associations
   Fix: Two-query pattern (fetch root entities; fetch each collection separately)

6. 2LC INVALIDATION STORM
   Symptom: cache hit rate drops to 0% during bulk updates;
            DB load spikes immediately after
   Cause: bulk JPQL UPDATE invalidates entire entity region
   Fix: Row-by-row updates for cached entities (maintains 2LC);
        Or evict region after bulk update; Or don't cache volatile entities

7. CONNECTION POOL EXHAUSTION
   Symptom: "Connection not available"; latency spikes; 503s
   Cause: long @Transactional methods holding connections
   Fix: Move external calls outside @Transactional;
        Reduce pool borrow time; increase maximumPoolSize (short-term)

8. MULTI-INSTANCE 2LC INCONSISTENCY
   Symptom: App instance A reads stale data after instance B updates
   Cause: Each instance has independent in-memory 2LC
   Fix: Use distributed cache (Redis, Hazelcast) as 2LC provider;
        Or disable 2LC entirely and use application-level Redis caching
```

---

### 🧪 Thought Experiment

**WHEN TO ABANDON JPA FOR A SPECIFIC USE CASE:**

```
Scenario: product import endpoint
  - 100,000 products imported per night
  - Each product: 5 fields; no associations needed
  - Must run in <2 minutes

APPROACH 1: JPA save() with batch
  - 100K entity lifecycle events (persist, flush)
  - Order_inserts + sequence generator needed
  - IDENTITY generator: batching disabled
  -> Result: ~5 min; borderline acceptable

APPROACH 2: JOOQ batch insert
  - ctx.batchInsert(records).execute()
  - 100K rows / batch_size=500 = 200 SQL batches
  -> Result: ~30 sec; clear winner for this use case

APPROACH 3: Spring JDBC BatchUtils
  - jdbcTemplate.batchUpdate(sql, batchArgs, 500, setter)
  -> Result: ~25 sec; similar to JOOQ; simpler setup

Decision: JPA for entity CRUD (domain logic).
JOOQ/JDBC for bulk insert/update without entity lifecycle.
Both in same application, same @Transactional context.
```

---

### 🧠 Mental Model / Analogy

> JPA at scale is like managing a growing restaurant.
> At 10 tables (10 RPS): one chef, one waiter, manual
> tracking. At 100 tables (100 RPS): specialization needed.
> The dirty checking chef (inspects every dish) is replaced
> by the `readOnly` mode (no inspection for read orders).
> The connection pool is the serving stations (limited;
> don't hold them during customer chat). The 2LC is the
> mise en place (pre-prepared ingredients; reuse across
> orders). The read replica is a separate prep kitchen
> for cold dishes (reads) so the main kitchen (master DB)
> focuses on hot dishes (writes). No single role change
> fixes the restaurant; all roles must scale together.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - Key principles (anyone can understand):**
At scale: (1) read-only transactions for reads, (2) fetch
only what you need (projections), (3) don't mix external
calls inside DB transactions.

**Level 2 - Quick wins (junior developer):**
```java
// Win 1: readOnly on all query methods
@Transactional(readOnly = true)
public List<ProductDto> findAll() { ... }

// Win 2: projection instead of entity load for lists
@Query("SELECT new com.example.ProductDto" +
    "(p.id, p.name, p.price) FROM Product p")
List<ProductDto> findAllAsDto();

// Win 3: explicit fetch to prevent N+1
@Query("SELECT p FROM Product p " +
    "LEFT JOIN FETCH p.images")
List<Product> findAllWithImages();
```

**Level 3 - CQRS split (mid-level engineer):**
```java
// Write side: JPA handles complex domain logic
@Transactional
public Order placeOrder(PlaceOrderCommand cmd) {
    Customer customer = customerRepo.findById(
        cmd.getCustomerId()).orElseThrow();
    Product product = productRepo.findById(
        cmd.getProductId()).orElseThrow();
    Order order = Order.place(customer, product,
        cmd.getQuantity()); // domain logic
    return orderRepo.save(order);
}

// Read side: JOOQ handles complex joins + aggregations
@Transactional(readOnly = true)
public OrderDashboardDto getDashboard(Long customerId) {
    return jooq
        .select(
            count(ORDER.ID).as("totalOrders"),
            sum(ORDER.TOTAL).as("totalSpent"),
            max(ORDER.CREATED_AT).as("lastOrderDate"))
        .from(ORDER)
        .where(ORDER.CUSTOMER_ID.eq(customerId))
        .fetchOneInto(OrderDashboardDto.class);
}
```

**Level 4 - Read replica routing (senior engineer):**
```java
// Route reads to replica, writes to primary
public class ReadWriteRoutingDataSource
    extends AbstractRoutingDataSource {

    private static final ThreadLocal<DataSourceType>
        CONTEXT = new ThreadLocal<>();

    public static void useReadReplica() {
        CONTEXT.set(DataSourceType.REPLICA);
    }

    public static void usePrimary() {
        CONTEXT.set(DataSourceType.PRIMARY);
    }

    @Override
    protected Object determineCurrentLookupKey() {
        return CONTEXT.get() != null
            ? CONTEXT.get()
            : DataSourceType.PRIMARY;
    }
}

// AOP advice: readOnly transactions -> replica
@Around("@annotation(transactional)")
public Object routeReadOnly(
    ProceedingJoinPoint pjp,
    Transactional transactional) throws Throwable {
    if (transactional.readOnly()) {
        ReadWriteRoutingDataSource.useReadReplica();
    }
    try {
        return pjp.proceed();
    } finally {
        ReadWriteRoutingDataSource.usePrimary();
    }
}
```

**Level 5 - 2LC distributed caching (staff engineer):**
For multi-instance deployments: Hibernate's default
in-memory 2LC (EhCache) is node-local - update on
instance A doesn't evict cache on instance B. Solution
options: (1) Hazelcast as distributed 2LC provider
(Hibernate integrates via `hazelcast-hibernate` module);
(2) Infinispan distributed cache (JBoss ecosystem);
(3) Disable 2LC; use application-level Redis cache with
`@Cacheable` + explicit eviction on writes (simpler to
reason about). Option 3 is most common in microservices:
`@Cacheable("products")` on service methods, `@CacheEvict`
on writes, Redis as the distributed store.

---

### ⚙️ How It Works (Mechanism)

**PRODUCTION JPA CONFIGURATION TEMPLATE:**

```properties
# application.properties - production hardened

# Connection pool:
spring.datasource.hikari.maximum-pool-size=20
spring.datasource.hikari.connection-timeout=5000
spring.datasource.hikari.max-lifetime=1680000
spring.datasource.hikari.keepalive-time=300000

# Hibernate core:
spring.jpa.properties.hibernate.jdbc.batch_size=50
spring.jpa.properties.hibernate.order_inserts=true
spring.jpa.properties.hibernate.order_updates=true
spring.jpa.properties.hibernate
  .jdbc.batch_versioned_data=true
spring.jpa.properties.hibernate
  .default_batch_fetch_size=16

# DDL - NEVER create/update in production:
spring.jpa.hibernate.ddl-auto=validate

# Statistics - enable for staging, disable in prod
# (or use sampling):
spring.jpa.properties.hibernate
  .generate_statistics=false

# Logging (dev only):
spring.jpa.show-sql=false
logging.level.org.hibernate.SQL=WARN
```

---

### 🔄 The Complete Picture - End-to-End Flow

**PERFORMANCE CHECKLIST FOR A HIGH-TRAFFIC SERVICE:**

```
STEP 1: BASELINE
  -> Enable Hibernate statistics in staging
  -> Run load test at 10x production traffic
  -> Capture: queryExecutionCount, entityLoadCount,
     secondLevelCacheHitRate, connectCount

STEP 2: N+1 DETECTION
  -> If queryExecutionCount > expected per request:
     Check all @OneToMany, @ManyToOne associations
     -> Add @EntityGraph or JOIN FETCH for each access pattern
     -> Or use DTO projections (no associations loaded)

STEP 3: READ OPTIMIZATION
  -> Add @Transactional(readOnly=true) to all query methods
     (in Service layer; not Repository)
  -> Measure: is dirty checking overhead visible in profiler?

STEP 4: CACHE EFFECTIVENESS
  -> If 2LC hit rate < 50%: tune TTL, region sizes
  -> If volatile entities: remove @Cache; use Redis
  -> If multi-instance: consider distributed cache

STEP 5: CONNECTION POOL
  -> If connectCount per request > 1: connection acquired
     multiple times; check @Transactional boundaries
  -> If waiting threads > 0: pool exhaustion;
     reduce tx scope, review long-running methods

STEP 6: SCALING READS
  -> Add read replica + routing DataSource
  -> Route @Transactional(readOnly=true) to replica
  -> Verify: replica lag < acceptable threshold

STEP 7: BATCH OPERATIONS
  -> Replace entity-by-entity inserts with batch=50
  -> Use StatelessSession for large imports (no 1LC overhead)
  -> Or replace with JOOQ/JDBC batch insert (fastest)
```

---

### 💻 Code Example

**Example 1 - Complete read-optimized service:**

```java
@Service
@RequiredArgsConstructor
public class ProductQueryService {

    private final ProductRepository repo;
    private final JPAQueryFactory queryFactory;

    // Pattern 1: readOnly + DTO projection
    @Transactional(readOnly = true)
    public Page<ProductSummaryDto> listProducts(
        Pageable pageable) {
        return repo.findAllProjectedBy(
            ProductSummaryDto.class, pageable);
    }

    // Pattern 2: readOnly + explicit JOIN FETCH (no N+1)
    @Transactional(readOnly = true)
    public List<ProductWithImages> listWithImages() {
        return repo.findAllWithImages();
        // Repository: @Query with JOIN FETCH p.images
    }

    // Pattern 3: JOOQ for analytics (not entity loading)
    @Transactional(readOnly = true)
    public RevenueReportDto getRevenueReport(int year) {
        return queryFactory
            .select(
                sum(PRODUCT.PRICE).as("total"),
                count(ORDER.ID).as("orderCount"))
            .from(ORDER)
            .join(PRODUCT).on(...)
            .where(year(ORDER.CREATED_AT).eq(year))
            .fetchOneInto(RevenueReportDto.class);
    }
}
```

---

### ⚖️ Comparison Table

| Scale tier | Characteristic queries | Key bottleneck | Recommended pattern |
|---|---|---|---|
| <100 RPS | Simple CRUD, <5 joins | Usually none visible | Standard Spring Data JPA |
| 100-1000 RPS | Reports, complex search | N+1, dirty check | readOnly tx, projections, JOIN FETCH |
| 1000-10K RPS | High concurrency, analytics | Pool exhaustion, 2LC thrash | CQRS, read replicas, Redis |
| >10K RPS | Millions of rows/sec | DB single-node limit | Sharding, CQRS, event sourcing |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "2LC solves all read performance problems" | 2LC is effective for reference data (infrequently changed entities like categories, config). For user data (orders, transactions) that changes per user per request: 2LC hit rate will be low. The fix for user data reads: DTO projections + indexed queries, not 2LC. |
| "Horizontal scaling (more app instances) solves JPA problems" | Horizontal scaling adds instances, but EACH instance creates connections to the DB. 10 instances * 20 pool connections = 200 DB connections. DB has ~300 max connections. 15 instances = 300 connections = DB saturated. JPA problems AMPLIFY with scaling. Fix the per-instance efficiency before scaling out. |
| "Read replicas eliminate read load on primary" | Read replicas have replication lag (milliseconds to seconds for async replication). A `@Transactional(readOnly=true)` method that reads data it just wrote (in the same request flow) may get stale data from the replica. Pattern: writes always to primary; reads to replica ONLY when stale reads are acceptable (eventually consistent reads). |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode: JPA Performance Cliff at 2x Load**

**Symptom:** Application performs well at 100 RPS.
At 200 RPS: latency doubles, then triples. Error rate
increases. Looks like application "falls off a cliff"
at 200 RPS rather than degrading gracefully.
**Root Cause (most common):** Connection pool exhaustion.
At 100 RPS: pool=10 connections, each request uses a
connection for ~50ms -> 10/0.050 = 200 concurrent requests
serviced. At 200 RPS: pool is fully occupied; requests
queue; latency adds pool wait time; queue grows faster
than connections are returned -> cascade failure.
**Diagnosis:**
```java
// Add HikariCP monitoring:
int waiting = pool.getThreadsAwaitingConnection();
// If waiting > 0 during load: pool is the bottleneck

// Check: is connection-timeout too long?
// Default 30s: 200 requests * 30s wait = timeout cascade
// Set to 5s: fail fast; clients see 503 quickly
spring.datasource.hikari.connection-timeout=5000
```
**Fix:** (1) Reduce transaction scope (no external calls
inside `@Transactional`), (2) optimize slow queries
(reduce connection hold time), (3) add `readOnly=true`
to free connections faster (no dirty check delay at commit).

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[JPH-027 - N+1 Problem]] - most common JPA scale issue
- [[JPH-033 - First Level Cache]] - session size management
- [[JPH-034 - Second Level Cache]] - cache tuning at scale
- [[JPH-045 - Batch Processing]] - batch optimization patterns
- [[JPH-046 - Hibernate Statistics]] - measuring performance
- [[JPH-047 - Connection Pooling]] - pool exhaustion diagnosis

**Builds On This (learn these next):**
- [[JPH-056 - Spring Data JPA Architecture Design]] -
  structured architecture for scalable Spring Data apps

**Related:**
- [[JPH-058 - Hibernate Internals]] - understanding internals
  enables targeted optimization (dirty check mechanism, hydration)
- [[JPH-055 - ORM Selection Framework]] - when JPA scale
  limits are reached; alternative tool evaluation

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ TOP WINS     │ 1. @Transactional(readOnly=true) on reads │
│ (in order)   │ 2. DTO projections (not entity loads)     │
│              │ 3. JOIN FETCH / @EntityGraph for N+1      │
│              │ 4. Reduce @Transactional scope (no ext.   │
│              │    calls inside transactions)             │
│              │ 5. JOOQ/JDBC for bulk & analytics         │
├──────────────┼───────────────────────────────────────────┤
│ MONITOR      │ Hibernate statistics: queryCount,         │
│              │ entityLoadCount, 2LC hit rate, flushCount  │
├──────────────┼───────────────────────────────────────────┤
│ 2LC MULTI    │ In-memory 2LC per instance = stale        │
│ INSTANCE     │ Fix: Redis @Cacheable or Hazelcast 2LC    │
├──────────────┼───────────────────────────────────────────┤
│ SCALE READS  │ AbstractRoutingDataSource: readOnly->      │
│              │ read replica; others -> primary           │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "JPA at scale = 8 failure modes + fixes:  │
│              │ N+1, dirty check, session size, entity    │
│              │ loading, pool exhaustion, 2LC thrash,     │
│              │ Cartesian product, multi-instance cache." │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Add `@Transactional(readOnly=true)` to ALL read methods -
   instant dirty check elimination; most free performance win
2. N+1 is the #1 JPA scale problem: detect via `queryExecutionCount`
   in stats; fix via `JOIN FETCH`/`@EntityGraph`/batch fetch size
3. Don't load full entities for aggregations/reports -
   use JPQL aggregate or JOOQ; entity load for 50K rows = OOM

**Interview one-liner:** JPA at scale breaks in predictable ways:
N+1 queries (fix: JOIN FETCH, @EntityGraph), dirty check overhead
(fix: `readOnly=true`), session growth in batches (fix: `flush+clear`),
entity loading for analytics (fix: projections/JOOQ), pool exhaustion
(fix: reduce transaction scope). Architecture responses: CQRS split,
read replicas, distributed 2LC (Redis/Hazelcast) for multi-instance.

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Every ORM/database
access framework has scale limits that appear as "cliffs"
rather than gradual degradation - because their internal
data structures (session cache, dirty checking, connection
pool) accumulate state. N+1 is 1 query at small scale;
100 queries at medium scale; timeout at large scale.
Dirty checking is negligible at 10 entities; visible at
1,000; dominant at 100,000. The ORM cliff pattern:
acceptable performance followed by sudden failure when
a threshold is crossed. This same pattern appears in:
thread pool exhaustion (gradual until queue fills; then
cliff), JVM GC pressure (efficient until heap fills; then
stop-the-world), React state management (flat at small
state; tree walk dominates at large state). Design for
gradual degradation: set bounded queues, use projections
instead of full loads, add timeouts everywhere.

---

### 💡 The Surprising Truth

The most common JPA scale problem is NOT N+1 queries
or dirty checking - it's SCHEMA DESIGN. Hibernate/JPA
makes schema changes easy to delay (entities map to tables,
DDL auto-generated), which means teams often ship to
production with schemas designed for correctness but not
for query performance. The most impactful optimizations:
(1) Add a composite index for the most common query
patterns (e.g., `(customer_id, created_at)` for
"recent orders per customer"), (2) denormalize a frequently
read column to avoid a JOIN. Both of these are outside JPA -
they're SQL and schema concerns. Before applying all the JPA
architectural patterns in this entry: run `EXPLAIN ANALYZE`
on your top 5 slowest queries. If any show sequential scans
on large tables: add an index. A single index addition can
make a 2-second query run in 5ms - far better than any
ORM optimization pattern.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **IDENTIFY** the 8 JPA scale failure modes given a
   symptom description (slow report, OOM, pool exhaustion)
2. **APPLY** `@Transactional(readOnly=true)` correctly
   and explain WHY it improves performance
3. **DESIGN** a CQRS pattern using JPA for writes
   and JOOQ/JDBC for complex reads in the same service
4. **IMPLEMENT** a batch processing loop with `flush+clear`
   at the correct interval
5. **ROUTE** reads to a read replica using
   `AbstractRoutingDataSource` based on transaction readOnly flag

---

### 🎯 Interview Deep-Dive

**Q1: Your order listing endpoint is slow at 1,000 RPS.
Where do you start investigating?**
*Why they ask:* Tests systematic JPA performance diagnosis.
*Strong answer includes:*
- Start with Hibernate statistics: `queryExecutionCount` per request
  - If >2 for a list endpoint: N+1 suspected
  - Check `entityLoadCount`: if 100x higher than expected: lazy loading
- Check connection pool: `HikariPoolMXBean.getThreadsAwaitingConnection()`
  - If >0: pool exhaustion; reduce tx scope
- Add `@Transactional(readOnly=true)` if not present on the endpoint
- Check query plan: `EXPLAIN ANALYZE` on the generated SQL
  - Sequential scan on `orders` table? Missing index on `customer_id`?
- Check: is the endpoint loading full `Order` entities when it
  only needs 3 fields? Replace with DTO projection.

**Q2: You have 10 app instances with Hibernate 2LC (EhCache).
After a product price update, some users see old prices.
Why and how do you fix this?**
*Why they ask:* Tests distributed caching knowledge.
*Strong answer includes:*
- Root cause: each app instance has its own in-memory EhCache 2LC
  Instance A updates product price, evicts its own cache
  Instance B still has the old price in its local cache
  Users routed to instance B get stale data until TTL expires
- Fix option 1: Use distributed 2LC provider (Hazelcast/Infinispan)
  - All instances share a distributed cache; eviction is cluster-wide
  - Complexity: cluster membership, network overhead on cache ops
- Fix option 2: Disable 2LC for Product; use Spring @Cacheable with Redis
  - `@Cacheable("products")` on ProductService.findById()
  - `@CacheEvict("products")` on ProductService.update()
  - Redis is the single source of truth; all instances use same Redis
  - Simpler to reason about; explicit cache management