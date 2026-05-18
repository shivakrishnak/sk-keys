---
id: JPH-046
title: Hibernate Statistics and Monitoring
category: JPA & Hibernate
tier: tier-3-java
folder: JPH-jpa-hibernate
difficulty: ★★☆
depends_on: JPH-011, JPH-031, JPH-033, JPH-034, JPH-035, JPH-045
used_by: JPH-054, JPH-058
related: JPH-027, JPH-047, JPH-052
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
nav_order: 46
permalink: /technical-mastery/jpa-hibernate/hibernate-statistics/
---

⚡ **TL;DR** - Hibernate's `Statistics` API exposes
query execution counts, entity operations, cache hit/miss
rates, connection acquisition times, and second-level
cache metrics at runtime. Enable with
`hibernate.generate_statistics=true`. Access via
`SessionFactory.getStatistics()`. Exposes to JMX and
Spring Boot Actuator metrics automatically. Use during
load tests and production monitoring to detect N+1
patterns, cache inefficiency, and unexpected query volumes.
Never leave `generate_statistics=true` in production
unless you understand the overhead (3-5% throughput cost).

| #046            | Category: JPA & Hibernate                                                                                               | Difficulty: ★★☆ |
| :-------------- | :---------------------------------------------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | EntityManager, Hibernate Session vs EntityManager, First Level Cache, Second Level Cache, Query Cache, Batch Processing |                 |
| **Used by:**    | JPA at Scale, Hibernate Internals                                                                                       |                 |
| **Related:**    | N+1 Problem, Connection Pooling, Dirty Checking                                                                         |                 |

---

### 🔥 The Problem This Solves

**DIAGNOSING PRODUCTION PERFORMANCE ISSUES:**
A service endpoint is slow (500ms). You suspect N+1 queries
but `show_sql=true` produces thousands of log lines in
production - unreadable. You need a way to see:

- How many SQL queries were executed per request?
- Were second-level cache entries hit or missed?
- How long did connection acquisition take?
- How many entity objects were loaded?

**WITH HIBERNATE STATISTICS:**

```java
Statistics stats = sessionFactory.getStatistics();
stats.setStatisticsEnabled(true);
stats.clear(); // reset before the request

// ... execute service logic ...

System.out.println("Queries: " + stats.getQueryExecutionCount());
System.out.println("Entities loaded: " + stats.getEntityLoadCount());
System.out.println("2LC hits: " +
    stats.getSecondLevelCacheHitCount());
System.out.println("2LC misses: " +
    stats.getSecondLevelCacheMissCount());
System.out.println("Connections: " + stats.getConnectCount());
```

---

### 📘 Textbook Definition

**Hibernate Statistics** is a runtime instrumentation API
(`org.hibernate.stat.Statistics`) that tracks query and
cache operations. Enabled per `SessionFactory`.

**Key metric groups:**

| Group       | Metrics                                                                 |
| ----------- | ----------------------------------------------------------------------- |
| Query       | executionCount, executionRowCount, maxTime, minTime                     |
| Entity      | loadCount, insertCount, updateCount, deleteCount, fetchCount            |
| Collection  | loadCount, updateCount, recreateCount, removeCount, fetchCount          |
| 2LC         | hitCount, missCount, putCount, elementCountInMemory, elementCountOnDisk |
| Connection  | connectCount (JDBC connection acquisitions)                             |
| Session     | openCount, closeCount, flushCount                                       |
| Transaction | count, successfulCount, failedCount                                     |

**Key integration points:**

- `SessionFactory.getStatistics()` - direct Java access
- JMX MBean auto-registered when statistics enabled
- Spring Boot Actuator: exposed via `/actuator/metrics`
  as `hibernate.*` metrics (with `spring-boot-actuator` + `hibernate.generate_statistics=true`)

---

### ⏱️ Understand It in 30 Seconds

**One line:** Hibernate Statistics is a runtime counter
for all JPA/Hibernate operations - queries, cache hits,
entity loads, connections. Essential for diagnosing
performance issues without relying on SQL log parsing.

**One analogy:**

> Hibernate Statistics is the "dashboard" of your JPA
> layer - like the dashboard gauges in a car (RPM, speed,
> fuel level). SQL logging (`show_sql=true`) is looking
> out the windshield at each moment - high detail, low
> context. Statistics gives you the overview: "total queries
> this minute: 10,000", "cache hit ratio: 35%",
> "max query time: 2,300ms". Use statistics for operational
> monitoring; use SQL logging for targeted debugging.

**One insight:** The most important statistic for N+1
detection is comparing `entityLoadCount` to `queryExecutionCount`.
If loading 100 orders produces 101+ queries and 1,000+
entity loads, N+1 is confirmed. No SQL log parsing needed.

---

### 🔩 First Principles Explanation

**KEY COUNTERS AND WHAT THEY REVEAL:**

```java
Statistics s = sf.getStatistics();

// N+1 detection:
long queries  = s.getQueryExecutionCount();
long entities = s.getEntityLoadCount();
// If queries >> expected (e.g., 101 for 1 request): N+1
// If entities >> queries: many eager loads or N+1 fetches

// Cache effectiveness:
long hits   = s.getSecondLevelCacheHitCount();
long misses = s.getSecondLevelCacheMissCount();
long puts   = s.getSecondLevelCachePutCount();
double hitRate = (double) hits / (hits + misses);
// hitRate < 0.5: cache is not effective
// high puts, low hits: data evicted too quickly

// Query performance:
String[] queryNames = s.getQueries();
for (String q : queryNames) {
    QueryStatistics qs = s.getQueryStatistics(q);
    // qs.getExecutionCount()
    // qs.getExecutionRowCount()    - rows returned
    // qs.getExecutionMaxTime()     - slowest execution (ms)
    // qs.getExecutionMinTime()     - fastest execution (ms)
    // qs.getExecutionAvgTime()     - average execution (ms)
}
```

---

### 🧪 Thought Experiment

**VERIFYING BATCH PROCESSING EFFECTIVENESS:**

```java
sf.getStatistics().setStatisticsEnabled(true);
sf.getStatistics().clear();

importService.batchImport(products100000);

Statistics s = sf.getStatistics();
long stmts   = s.getPrepareStatementCount();
long inserts = s.getEntityInsertCount();
double ratio = (double) inserts / stmts;

// If ratio ≈ 1: batching not working
// -> Check: IDENTITY generator? order_inserts missing?
//    spring.jpa.properties.* prefix wrong?

// If ratio ≈ 50: batching working correctly
// -> 100,000 inserts / ~2,000 prepared statements = 50

System.out.printf(
    "Inserts: %d, Stmts: %d, Ratio: %.1f%n",
    inserts, stmts, ratio);
```

---

### 🧠 Mental Model / Analogy

> Hibernate Statistics is like a flight data recorder
> ("black box") for your JPA layer. Every query, entity
> load, cache hit, and connection acquisition is logged
> to counters. After a slow request: check the counters
> to understand what happened. 10,000 entity loads for a
> single API call? N+1. Cache hit rate of 5%? Cache
> misconfigured. Connection count spiking? Connection
> pool exhaustion. Statistics gives the "what happened"
> without requiring SQL log analysis.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Hibernate Statistics counts database operations: how many
queries ran, how many entities were loaded, whether cache
was used. Useful for finding performance problems.

**Level 2 - How to enable it (junior developer):**

```properties
spring.jpa.properties.hibernate.generate_statistics=true
spring.jpa.properties.hibernate.session.events.log=true
# Logs session stats per session close
```

Access in code: `sessionFactory.getStatistics()`.

**Level 3 - Key metrics (mid-level engineer):**
Primary diagnostics: `queryExecutionCount` (N+1 detection),
`secondLevelCacheHitCount/MissCount` (cache effectiveness),
`entityLoadCount` (eager loading detection),
`prepareStatementCount` / `entityInsertCount` ratio (batch
processing verification).

**Level 4 - Spring Boot Actuator integration (senior engineer):**
Spring Boot auto-exposes Hibernate statistics via Micrometer
when `spring-boot-actuator` and `hibernate.generate_statistics=true`
are present. Metrics available as: `hibernate.sessions.open`,
`hibernate.entity.deletes`, `hibernate.query.executions`,
`hibernate.second_level_cache.hits`, etc.
Export to Prometheus/Grafana for continuous monitoring.

**Level 5 - Per-entity region statistics (staff engineer):**
For the 2LC, per-region statistics show which entity types
have high miss rates:

```java
for (String region : s.getSecondLevelCacheRegionNames()) {
    CacheRegionStatistics rs =
        s.getDomainDataRegionStatistics(region);
    double regionHitRate = (double) rs.getHitCount()
        / (rs.getHitCount() + rs.getMissCount());
    // Identify entities with low cache hit rates
    // -> Increase TTL, increase region size, or remove caching
}
```

This granularity allows targeted cache configuration
per entity type.

---

### ⚙️ How It Works (Mechanism)

**ENABLING STATISTICS:**

```properties
# application.properties
spring.jpa.properties.hibernate.generate_statistics=true

# Optional: log stats at session close
spring.jpa.properties.hibernate.session.events.log=org.hibernate.internal.SessionImpl

# Spring Boot Actuator metrics export (auto with actuator):
management.endpoints.web.exposure.include=health,info,metrics
management.metrics.export.prometheus.enabled=true
```

**PROGRAMMATIC ACCESS:**

```java
@Component
@RequiredArgsConstructor
public class HibernateStatsDiagnostics {

    private final EntityManagerFactory emf;

    public void logStats() {
        Statistics stats = emf
            .unwrap(SessionFactory.class)
            .getStatistics();

        log.info("=== Hibernate Statistics ===");
        log.info("Queries executed: {}",
            stats.getQueryExecutionCount());
        log.info("Entity loads: {}",
            stats.getEntityLoadCount());
        log.info("Entity inserts: {}",
            stats.getEntityInsertCount());
        log.info("Entity updates: {}",
            stats.getEntityUpdateCount());
        log.info("Entity deletes: {}",
            stats.getEntityDeleteCount());
        log.info("2LC hits: {}",
            stats.getSecondLevelCacheHitCount());
        log.info("2LC misses: {}",
            stats.getSecondLevelCacheMissCount());
        log.info("Connections acquired: {}",
            stats.getConnectCount());
        log.info("Transactions: {}",
            stats.getTransactionCount());
        log.info("Max query time: {} ms",
            stats.getQueryExecutionMaxTime());
        log.info("Slowest query: {}",
            stats.getQueryExecutionMaxTimeQueryString());
    }
}
```

---

### 🔄 The Complete Picture - End-to-End Flow

**MONITORING IN SPRING BOOT + PROMETHEUS:**

```yaml
# application.yml
spring:
  jpa:
    properties:
      hibernate:
        generate_statistics: true

management:
  endpoints:
    web:
      exposure:
        include: metrics,health,info
  metrics:
    export:
      prometheus:
        enabled: true
```

```java
// Metrics auto-exported by spring-boot-actuator:
// GET /actuator/metrics/hibernate.query.executions
// GET /actuator/metrics/hibernate.entity.loads
// GET /actuator/metrics/hibernate.second_level_cache.hits
// GET /actuator/metrics/hibernate.sessions.open

// Prometheus scrape:
// hibernate_query_executions_total{...} 12345
// hibernate_second_level_cache_hits_total{...} 5432
// hibernate_second_level_cache_misses_total{...} 987
```

**Grafana dashboard panels:**

- Query execution rate (req/sec)
- 2LC hit ratio (should be >70% for cached entities)
- Avg query execution time (trend alert)
- Entity load count per request

---

### 💻 Code Example

**Example 1 - N+1 detection test using statistics:**

```java
@SpringBootTest
@Transactional
class N1DetectionTest {

    @Autowired SessionFactory sf;
    @Autowired OrderRepository orderRepo;

    @Test
    void loadOrdersWithItems_shouldNotTriggerN1() {
        // Given: 10 orders with items
        setupTestData(10);
        sf.getStatistics().setStatisticsEnabled(true);
        sf.getStatistics().clear();

        // When: load all orders
        List<Order> orders = orderRepo.findAll();
        // Access items to trigger any lazy loading:
        orders.forEach(o -> o.getItems().size());

        // Then: should be <=2 queries (1 orders + 1 items)
        long queries = sf.getStatistics()
            .getQueryExecutionCount();
        assertThat(queries)
            .as("Expected 2 queries; found N+1")
            .isLessThanOrEqualTo(2);
    }
}
```

**Example 2 - Cache hit rate monitoring:**

```java
@Scheduled(fixedDelay = 60_000)
public void logCacheStats() {
    Statistics s = sf.getStatistics();
    long hits   = s.getSecondLevelCacheHitCount();
    long misses = s.getSecondLevelCacheMissCount();
    long total  = hits + misses;
    if (total > 0) {
        double hitRate = 100.0 * hits / total;
        if (hitRate < 50.0) {
            log.warn("Low 2LC hit rate: {:.1f}% " +
                "(hits={}, misses={})",
                hitRate, hits, misses);
        }
    }
}
```

---

### ⚖️ Comparison Table

| Tool                            | Granularity              | Overhead            | Use case                          |
| ------------------------------- | ------------------------ | ------------------- | --------------------------------- |
| `hibernate.show_sql=true`       | Per-SQL statement        | Low                 | Dev debugging: see exact SQL      |
| `hibernate.generate_statistics` | Aggregate counters       | 3-5%                | Performance diagnosis, monitoring |
| `hibernate.session.events.log`  | Per-session summary      | Low                 | Per-request query counts in dev   |
| Spring Boot Actuator metrics    | Aggregate, exported      | Micrometer overhead | Production Prometheus/Grafana     |
| P6Spy / datasource-proxy        | Per-SQL with full params | High                | Integration testing               |

---

### ⚠️ Common Misconceptions

| Misconception                                                | Reality                                                                                                                                                                                                                                                                                             |
| ------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Statistics are thread-safe to reset during load tests"      | `statistics.clear()` resets ALL counters atomically, but calling clear while concurrent requests are running makes the statistics unreliable. For accurate per-request analysis: test in isolation or use per-session statistics.                                                                   |
| "generate_statistics=true has no production cost"            | Enabling statistics has a measurable overhead (3-5% throughput reduction). For production, either disable statistics or use sampling (log stats periodically and reset, not per-request). In latency-sensitive applications, disable in production and enable only when diagnosing specific issues. |
| "Statistics show current operation count, not since startup" | Statistics are cumulative since the last `clear()` (or application start). Call `statistics.clear()` before a test to get fresh counts. In production monitoring, use the rate of change (delta over time interval), not absolute values.                                                           |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode: Statistics Show Zero Despite Enable**

**Symptom:** `statistics.getQueryExecutionCount()` returns
0 even though queries are clearly running.

**Root Cause:** Statistics is enabled in properties but
`statistics.isStatisticsEnabled()` returns false. Two
causes: (1) using the wrong property key
(`spring.jpa.hibernate.generate_statistics` instead of
`spring.jpa.properties.hibernate.generate_statistics`), or
(2) multiple persistence units - checking wrong `SessionFactory`.

**Fix:**

```java
Statistics s = emf.unwrap(SessionFactory.class)
    .getStatistics();
// Verify:
log.info("Stats enabled: {}",
    s.isStatisticsEnabled());
// If false: property key wrong; add
// spring.jpa.properties.hibernate.generate_statistics=true
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[JPH-033 - First Level Cache]] - statistics track 1LC
  interactions (entity loads, flushes)
- [[JPH-034 - Second Level Cache]] - 2LC hit/miss rate
  is the primary 2LC diagnostic from statistics

**Builds On This (learn these next):**

- [[JPH-054 - JPA at Scale]] - statistics patterns in
  production monitoring at scale

**Related:**

- [[JPH-027 - N+1 Problem]] - statistics is the primary
  N+1 detection tool in integration tests
- [[JPH-045 - Batch Processing]] - batch effectiveness
  verified via prepareStatementCount/entityInsertCount ratio

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ ENABLE       │ spring.jpa.properties.hibernate          │
│              │   .generate_statistics=true              │
├──────────────┼──────────────────────────────────────────┤
│ ACCESS       │ emf.unwrap(SessionFactory.class)         │
│              │   .getStatistics()                       │
├──────────────┼──────────────────────────────────────────┤
│ N+1 CHECK    │ queryExecutionCount vs expected          │
│ BATCH CHECK  │ entityInsertCount / prepareStatementCount│
│ CACHE CHECK  │ secondLevelCacheHitCount /               │
│              │   (hitCount + missCount)                 │
├──────────────┼──────────────────────────────────────────┤
│ OVERHEAD     │ 3-5% throughput cost; evaluate for prod  │
├──────────────┼──────────────────────────────────────────┤
│ ACTUATOR     │ Auto-exported as hibernate.* metrics     │
│              │ Requires spring-boot-actuator on classpat│
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "Hibernate Statistics = cumulative       │
│              │ counters for queries, entity ops, cache. │
│              │ Use for N+1 detection + cache monitoring.│
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Enable with `spring.jpa.properties.hibernate.generate_statistics=true`;
   access via `emf.unwrap(SessionFactory.class).getStatistics()`
2. `queryExecutionCount` for N+1 detection in tests;
   `2LCHitCount/(hitCount+missCount)` for cache effectiveness
3. 3-5% overhead - use sampling or disable in production
   unless actively diagnosing an issue

**Interview one-liner:** Hibernate Statistics (`SessionFactory.getStatistics()`)
provides aggregate counters for query executions, entity
operations, cache hits/misses, and connection acquisitions.
Enable with `hibernate.generate_statistics=true`. Primary
uses: N+1 detection (queryExecutionCount in tests), batch
verification (prepareStatementCount ratio), 2LC effectiveness
(hit rate). 3-5% overhead - use judiciously in production.

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** White-box monitoring
(instrumenting application internals) vs black-box monitoring
(measuring external behavior) serve different diagnostic
purposes. Black-box: "response time is 500ms" - detects
the problem. White-box (like Hibernate Statistics): "101
queries executed" - explains the cause. Both are needed.
The pattern: deploy with black-box monitoring (response
time, error rate, throughput); when an alert fires, enable
white-box metrics to diagnose root cause. The same approach
applies to: JVM GC metrics (white-box for memory analysis),
database slow query log (white-box for query performance),
connection pool metrics (white-box for connection exhaustion).
White-box metrics have overhead; enable selectively.

---

### 💡 The Surprising Truth

Spring Boot's Micrometer integration automatically exposes
Hibernate statistics as `hibernate.*` metrics ONLY if both
conditions are true: (1) `spring-boot-actuator` is on the
classpath AND (2) `hibernate.generate_statistics=true`.
However, the Micrometer metrics names differ from the raw
Statistics API names. `statistics.getQueryExecutionCount()`
becomes `hibernate.query.executions` in Actuator. This
means you need to know both the Java API names (for testing)
and the Micrometer metric names (for dashboards). The
mapping is not immediately obvious from either the Statistics
Javadoc or the Actuator documentation. The best way to
discover all available metrics: hit `/actuator/metrics` in
a running application with Hibernate stats enabled - you'll
see all `hibernate.*` metric names exposed.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **ENABLE** Hibernate statistics with the correct property
   key and verify it's active via `isStatisticsEnabled()`
2. **WRITE** a test that asserts `queryExecutionCount <=
expected` to detect N+1 regressions
3. **COMPUTE** the 2LC hit rate from `hitCount` and `missCount`
   and interpret what a low hit rate means
4. **VERIFY** batch processing effectiveness using the
   `prepareStatementCount / entityInsertCount` ratio
5. **EXPLAIN** the overhead trade-off of `generate_statistics`
   and when to enable/disable it in production

---

### 🎯 Interview Deep-Dive

**Q1: How would you detect an N+1 query problem in an
integration test without reading SQL logs?**
_Why they ask:_ Tests practical monitoring knowledge.
_Strong answer includes:_

- Enable Hibernate statistics: `sf.getStatistics().setStatisticsEnabled(true)`
- `sf.getStatistics().clear()` before the test
- Execute the test operation
- Assert: `stats.getQueryExecutionCount() <= expectedQueryCount`
- Example: loading 10 orders with items should produce <=2 queries
  (1 order query + 1 batch items query); if it produces 11: N+1 confirmed
- Advantage over SQL logs: deterministic assertion, not manual parsing

**Q2: What overhead does hibernate.generate_statistics=true
add and how do you manage it in production?**
_Why they ask:_ Tests production-readiness thinking.
_Strong answer includes:_

- Overhead: 3-5% throughput reduction (atomic counter increments
  on every query, entity load, cache access)
- Production strategy: (1) disable in production (zero overhead);
  enable only during incident investigation; (2) if always needed:
  use sampling - collect stats every 60s, log delta, clear, repeat;
  (3) Spring Boot Actuator with Micrometer exports to Prometheus
  at low overhead for periodic scrapes, not per-request
- Key: never call `statistics.clear()` from multiple threads
  during concurrent load (race condition in metrics values)
