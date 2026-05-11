---
layout: default
title: "Hibernate - Performance"
parent: "Hibernate"
grand_parent: "Interview Mastery"
nav_order: 3
permalink: /interview/hibernate/performance/
topic: Hibernate
subtopic: Performance
keywords:
  - First-Level and Second-Level Cache
  - N+1 Detection and Prevention
  - Batch Fetching and Bulk Operations
  - Query Optimization
  - Hibernate Statistics and Monitoring
difficulty_range: ★★☆ to ★★★
status: complete
version: 1
---

# First-Level and Second-Level Cache

**TL;DR** - First-level cache (persistence context) is per-session and automatic. Second-level cache (L2C) is shared across sessions and optional. L2C stores entities/queries across requests, reducing database roundtrips by 60-90% for read-heavy data that changes infrequently.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
Every `findById(42)` hits the database, even if 1000 requests/second ask for the same entity. Catalog data (countries, categories, config) queried repeatedly with identical results.

---

### Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
First-level: "If I already loaded this entity in the current request, don't load it again." Second-level: "If ANY request already loaded this entity recently, reuse it."

**Level 2 - How to use it (junior developer):**

**First-level cache (automatic):**

```java
@Transactional
public void process() {
    // Query 1: hits DB
    Order o1 = em.find(Order.class, 1L);
    // Query 2: returns same object from cache!
    Order o2 = em.find(Order.class, 1L);
    assert o1 == o2; // true, same reference
}
```

**Second-level cache (opt-in):**

```xml
<dependency>
    <groupId>org.hibernate.orm</groupId>
    <artifactId>hibernate-jcache</artifactId>
</dependency>
<dependency>
    <groupId>org.ehcache</groupId>
    <artifactId>ehcache</artifactId>
</dependency>
```

```java
@Entity
@Cache(usage = CacheConcurrencyStrategy
    .READ_WRITE)
public class Country {
    @Id private String code;
    private String name;
}
```

```yaml
spring:
  jpa:
    properties:
      hibernate:
        cache:
          use_second_level_cache: true
          region.factory_class: org.hibernate.cache.jcache.
            JCacheRegionFactory
```

**Level 3 - How it works (mid-level engineer):**

**Cache levels:**

| Level                    | Scope               | Lifetime    | Shared | Eviction            |
| ------------------------ | ------------------- | ----------- | ------ | ------------------- |
| L1 (Persistence Context) | Session/Transaction | Request     | No     | Session close       |
| L2 (Entity Cache)        | SessionFactory      | Application | Yes    | TTL / Size / Update |
| Query Cache              | SessionFactory      | Application | Yes    | Table modification  |

**Concurrency strategies:**

| Strategy             | Use For                 | Guarantee                      |
| -------------------- | ----------------------- | ------------------------------ |
| READ_ONLY            | Immutable data          | Best performance               |
| READ_WRITE           | Read-heavy, some writes | Soft locks prevent dirty reads |
| NONSTRICT_READ_WRITE | Eventual consistency OK | No locks, possible stale reads |
| TRANSACTIONAL        | JTA transactions        | Full ACID (XA)                 |

**Level 4 - Mastery (senior/staff+ engineer):**

**Query cache (often misunderstood):**

```java
@QueryHints(@QueryHint(
    name = "org.hibernate.cacheable",
    value = "true"))
List<Country> findAll();
```

The query cache stores: `{query + params -> list of entity IDs}`. The entity cache stores the actual data. Both must be enabled for query cache to work.

**Query cache invalidation:** Invalidated when ANY insert/update/delete touches the queried table. For `SELECT * FROM countries` - any write to countries table invalidates ALL cached queries on that table.

Rule: Only cache queries on tables that rarely change (reference data).

**When NOT to use L2 cache:**

- Frequently updated entities (constant invalidation)
- Large entities (memory pressure)
- Entities with complex relationships (partial cache hits cause N+1)
- Multi-node deployments without distributed cache (stale data)

---

### Quick Recall

**If you remember only 3 things:**

1. L1 is automatic (per session). L2 is opt-in (shared across sessions).
2. Use L2 for read-heavy, rarely-changing data (config, catalogs, lookups)
3. Query cache = query -> IDs mapping. Invalidated on ANY table write.

---

### Interview Deep-Dive

**Q1: When would you NOT use second-level cache?**

_Why they ask:_ Tests understanding beyond "caching is good."

_Strong answer:_

Don't use L2C when:

1. **High write frequency:** Entity updated every few seconds. Cache invalidation overhead exceeds cache hit benefit.
2. **Large result sets:** Caching 1M entities exhausts memory. Cache eviction thrashes.
3. **Multi-node without distributed cache:** Node A caches entity, Node B updates it. Node A serves stale data until TTL expires.
4. **Security-sensitive data:** Cached across sessions means potential cross-user leakage if misconfigured.
5. **Short-lived entities:** Orders being processed - loaded once, updated, never read again.

Good candidates: Country lists, product categories, feature flags, configuration tables - read 1000x per write.

---

---

# N+1 Detection and Prevention

**TL;DR** - N+1 occurs when loading N entities triggers N additional queries for their lazy relationships. Detect with Hibernate Statistics or `datasource-proxy`. Prevent with `JOIN FETCH`, `@EntityGraph`, `@BatchSize`, or DTO projections.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
APIs that work fine in development (10 records) become unusably slow in production (10,000 records). A "list orders" endpoint that generates 10,001 SQL queries instead of 1-2.

---

### Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
You load a list of 100 items. For each item, Hibernate makes a separate query for related data. That's 1 + 100 = 101 queries when you could have done it in 1-2.

**Level 2 - How to use it (junior developer):**

**Detection:**

```yaml
# application.yml - log all SQL
logging:
  level:
    org.hibernate.SQL: DEBUG
    org.hibernate.type.descriptor.sql: TRACE
```

Look for repeated similar queries:

```sql
-- This pattern = N+1:
SELECT * FROM orders WHERE status = 'PENDING'
SELECT * FROM customers WHERE id = 1
SELECT * FROM customers WHERE id = 2
SELECT * FROM customers WHERE id = 3
-- ... (repeated for every order)
```

**Level 3 - How it works (mid-level engineer):**

**Prevention strategies ranked by preference:**

1. **DTO Projection (best for read-only lists):**

```java
public interface OrderSummary {
    Long getId();
    String getCustomerName();
    BigDecimal getTotal();
}
// No entities = no lazy loading = no N+1
List<OrderSummary> findByStatus(
    OrderStatus status);
```

2. **JOIN FETCH (when you need full entities):**

```java
@Query("SELECT o FROM Order o " +
       "JOIN FETCH o.customer " +
       "WHERE o.status = :status")
List<Order> findWithCustomer(OrderStatus status);
```

3. **@EntityGraph (declarative):**

```java
@EntityGraph(attributePaths = {"customer"})
List<Order> findByStatus(OrderStatus status);
```

4. **@BatchSize (reduces but doesn't eliminate):**

```java
@BatchSize(size = 25)
@OneToMany(mappedBy = "order")
private List<OrderItem> items;
// 100 orders: 4 batch queries instead of 100
```

**Level 4 - Mastery (senior/staff+ engineer):**

**Automated N+1 detection in tests:**

```java
// Using datasource-proxy:
@Bean
public DataSource dataSource(DataSource real) {
    return ProxyDataSourceBuilder.create(real)
        .countQuery()
        .build();
}

@Test
void shouldNotCauseNPlus1() {
    QueryCountHolder.clear();

    orderService.getOrdersPage(0);

    QueryCount count = QueryCountHolder.get(
        dataSource);
    assertThat(count.getSelect())
        .as("N+1 detected!")
        .isLessThanOrEqualTo(3);
}
```

**Hibernate Statistics:**

```yaml
spring.jpa.properties.hibernate.generate_statistics: true
```

```java
Statistics stats = sessionFactory.getStatistics();
log.info("Queries: {}",
    stats.getQueryExecutionCount());
log.info("L2C hits: {}",
    stats.getSecondLevelCacheHitCount());
```

---

### Quick Recall

**If you remember only 3 things:**

1. DTO projections = best prevention (no entities, no lazy loading)
2. JOIN FETCH for full entity graphs (single query with JOINs)
3. Automate detection in integration tests with query counting

---

### Interview Deep-Dive

**Q1: You join a project where the API is slow. How do you find and fix N+1 problems?**

_Why they ask:_ Tests systematic debugging approach.

_Strong answer:_

1. **Enable Hibernate Statistics** to get query count per endpoint
2. **Add datasource-proxy** for detailed query logging
3. **Profile the slowest endpoints** (APM tool or manual timing)
4. **Look for the pattern:** Repeated SELECT statements with different WHERE id=N

Fix strategy:

- **List endpoints:** Switch to DTO projections (eliminate the problem entirely)
- **Detail endpoints:** Use `@EntityGraph` or JOIN FETCH for needed relationships
- **Batch endpoints:** Add `@BatchSize(size=25)` as quick win, then refactor to JOIN FETCH
- **Prevent regression:** Add integration test with query count assertions

---

---

# Batch Fetching and Bulk Operations

**TL;DR** - Batch fetching (`@BatchSize`, `IN` clause grouping) reduces N+1 to N/batchSize+1 queries. Bulk operations (`@Modifying` queries, StatelessSession) bypass the persistence context for high-performance mass updates/inserts.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
Importing 100,000 records: 100,000 INSERT statements, persistence context grows to 100,000 entities consuming GBs of memory, massive GC pauses. Updating 50,000 rows: 50,000 individual UPDATE statements taking 30+ minutes.

---

### Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Instead of doing things one at a time, batch them: insert 50 rows in one statement, update 1000 rows in one query.

**Level 2 - How to use it (junior developer):**

**JDBC batching (insert/update):**

```yaml
spring:
  jpa:
    properties:
      hibernate:
        jdbc:
          batch_size: 50
        order_inserts: true
        order_updates: true
```

```java
@Transactional
public void importProducts(
        List<ProductDTO> dtos) {
    for (int i = 0; i < dtos.size(); i++) {
        em.persist(toEntity(dtos.get(i)));

        if (i % 50 == 0) {
            em.flush();  // Execute batch INSERT
            em.clear();  // Free memory
        }
    }
}
```

**Level 3 - How it works (mid-level engineer):**

**Bulk UPDATE/DELETE (bypass persistence context):**

```java
// Single SQL statement for mass update:
@Modifying(clearAutomatically = true)
@Query("UPDATE Order o SET o.status = :status " +
       "WHERE o.created < :cutoff")
int archiveOldOrders(
    @Param("status") OrderStatus status,
    @Param("cutoff") LocalDate cutoff);
// Returns affected row count
// clearAutomatically = true: clears L1 cache
// (prevents stale entities in context)
```

**@BatchSize for lazy collections:**

```java
@Entity
public class Order {
    @OneToMany(mappedBy = "order")
    @BatchSize(size = 25)
    private List<OrderItem> items;
}

// Without @BatchSize: 100 orders = 100 queries
// With @BatchSize(25): 100 orders = 4 queries
// SELECT * FROM items WHERE order_id IN (1..25)
// SELECT * FROM items WHERE order_id IN (26..50)
// ...
```

**Level 4 - Mastery (senior/staff+ engineer):**

**StatelessSession for maximum throughput:**

```java
public void bulkImport(List<Product> products) {
    StatelessSession ss = sessionFactory
        .openStatelessSession();
    Transaction tx = ss.beginTransaction();

    for (Product p : products) {
        ss.insert(p); // Immediate SQL, no cache
    }

    tx.commit();
    ss.close();
}
// No first-level cache
// No dirty checking
// No cascading
// No interceptors/listeners
// Pure JDBC speed with entity mapping
```

**Spring Batch for enterprise ETL:**

```java
@Bean
public JdbcBatchItemWriter<Product> writer(
        DataSource ds) {
    return new JdbcBatchItemWriterBuilder<Product>()
        .sql("INSERT INTO products " +
             "(name, price) VALUES (:name, :price)")
        .dataSource(ds)
        .beanMapped()
        .build();
}
// Handles chunking, transactions, retry,
// restart from failure point
```

---

### Quick Recall

**If you remember only 3 things:**

1. `hibernate.jdbc.batch_size=50` + `flush()/clear()` every N rows for bulk inserts
2. `@Modifying` JPQL for bulk UPDATE/DELETE (single SQL, no entity loading)
3. StatelessSession for maximum import throughput (no persistence context overhead)

---

### Interview Deep-Dive

**Q1: How would you import 10 million records into the database?**

_Why they ask:_ Tests large-scale data handling knowledge.

_Strong answer:_

For 10M records, don't use JPA at all for the import:

1. **Best option: Database native bulk load**
   - PostgreSQL: `COPY` command (100K rows/sec)
   - MySQL: `LOAD DATA INFILE`
   - Fastest possible, bypasses ORM entirely

2. **If you need validation/transformation:**
   - Spring Batch with `JdbcBatchItemWriter`
   - Chunk size: 1000-5000
   - Partitioned processing (parallel chunks)
   - Skip/retry for bad records

3. **If you must use JPA:**
   - StatelessSession (no L1 cache)
   - Batch size 100-500
   - Disable second-level cache for import
   - Disable audit listeners during import
   - Consider disabling indexes, re-enable after

Never: Regular JPA `em.persist()` without flush/clear - OutOfMemoryError guaranteed at 10M entities in persistence context.

---

---

# Query Optimization

**TL;DR** - Hibernate query optimization involves choosing the right query type (JPQL, Criteria, native SQL), using projections to avoid loading full entities, pagination strategies (offset vs keyset), and understanding how Hibernate generates SQL to avoid performance traps.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
Developers write `repo.findAll()` and filter in Java, loading entire tables into memory. Queries return 50 columns when 3 are needed. Pagination with OFFSET degrades linearly with page depth.

---

### Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Write queries that get exactly what you need from the database - no more, no less. The database is always faster at filtering and joining than your Java code.

**Level 2 - How to use it (junior developer):**

```java
// BAD: Load full entities for a list view
List<Order> orders = orderRepo.findAll();
// Loads ALL columns, ALL orders, into memory

// GOOD: Projection with only needed fields
public interface OrderListView {
    Long getId();
    String getOrderNumber();
    BigDecimal getTotal();
    OrderStatus getStatus();
}
List<OrderListView> findByStatus(
    OrderStatus status, Pageable pageable);
```

**Level 3 - How it works (mid-level engineer):**

**Pagination strategies:**

```java
// OFFSET pagination (simple but slow at depth):
Page<Order> findByStatus(
    OrderStatus status,
    PageRequest.of(1000, 20));
// SQL: SELECT ... LIMIT 20 OFFSET 20000
// DB must scan 20,000 rows to skip them!

// KEYSET pagination (fast at any depth):
@Query("SELECT o FROM Order o " +
       "WHERE o.status = :status " +
       "AND o.id > :lastId " +
       "ORDER BY o.id " +
       "LIMIT 20")
List<Order> findNextPage(
    OrderStatus status, Long lastId);
// SQL: SELECT ... WHERE id > 20000 LIMIT 20
// Uses index! Constant speed regardless of page.
```

**Avoiding SELECT N+1 in projections:**

```java
// BAD: Projection still triggers N+1
public interface OrderView {
    String getOrderNumber();
    CustomerView getCustomer(); // lazy load!
}

// GOOD: Flat projection (no relationships)
@Query("SELECT o.orderNumber as orderNumber, " +
       "c.name as customerName " +
       "FROM Order o JOIN o.customer c " +
       "WHERE o.status = :status")
List<OrderFlat> findFlat(OrderStatus status);
```

**Level 4 - Mastery (senior/staff+ engineer):**

**Read-only queries for performance:**

```java
@QueryHints({
    @QueryHint(
        name = HINT_FETCH_SIZE, value = "50"),
    @QueryHint(
        name = HINT_READONLY, value = "true"),
    @QueryHint(
        name = HINT_CACHEABLE, value = "true")
})
List<Order> findByStatus(OrderStatus status);
// readOnly: no dirty checking snapshot created
// fetchSize: JDBC fetch size (reduces roundtrips)
// cacheable: enable L2 query cache
```

**Blaze-Persistence for complex queries:**
Complex reporting queries with CTEs, window functions, and entity views often exceed JPQL capabilities. Use native queries or Blaze-Persistence for these cases rather than fighting JPQL limitations.

---

### Quick Recall

**If you remember only 3 things:**

1. Use DTO/interface projections for read-only list views (less data, no dirty checking)
2. Keyset pagination for deep pages (constant speed vs O(offset) for OFFSET)
3. `@QueryHints(HINT_READONLY)` skips snapshot creation for read-only queries

---

---

# Hibernate Statistics and Monitoring

**TL;DR** - Hibernate Statistics tracks query counts, cache hit ratios, session metrics, and slow queries. Essential for detecting N+1 problems, cache effectiveness, and connection pool issues in production.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
"The API is slow" with no way to know: Is it the query? The connection pool? Lazy loading? Cache misses? Without metrics, debugging is guesswork.

---

### Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Hibernate counts everything it does: how many queries, how long they took, how often caches were hit. You can see exactly where time is spent.

**Level 2 - How to use it (junior developer):**

```yaml
spring:
  jpa:
    properties:
      hibernate:
        generate_statistics: true
# Logs stats at session close:
# Queries executed: 23
# Entities loaded: 150
# L2C hit ratio: 78%
```

**Level 3 - How it works (mid-level engineer):**

**Expose via Micrometer + Actuator:**

```java
@Bean
public HibernateMetricsExporter
        hibernateMetrics(EntityManagerFactory emf) {
    return new HibernateMetricsExporter(
        emf, "hibernate");
}
// Exposes to /actuator/metrics:
// hibernate.query.executions
// hibernate.sessions.open
// hibernate.cache.hits / misses
// hibernate.transactions.count
```

**Key metrics to alert on:**

- `hibernate.query.executions` per request > 10 (N+1)
- `hibernate.cache.miss.ratio` > 50% (cache ineffective)
- `hibernate.sessions.open` growing (session leak)
- Slow query log (queries > 100ms)

**Level 4 - Mastery (senior/staff+ engineer):**

**Production monitoring stack:**

```
Hibernate Statistics
     |
     v
Micrometer Metrics Registry
     |
     v
Prometheus scraping /actuator/prometheus
     |
     v
Grafana Dashboard:
  - Queries per endpoint (detect N+1)
  - P99 query duration
  - L2C hit ratio over time
  - Connection pool utilization
  - Slow query count
```

**Custom slow query detection:**

```yaml
spring.jpa.properties.hibernate:
  session.events.log.LOG_QUERIES_SLOWER_THAN_MS: 100
```

**datasource-proxy for detailed query analysis:**

```java
@Bean
public DataSource dataSource(DataSource actual) {
    return ProxyDataSourceBuilder.create(actual)
        .name("SQL-Trace")
        .multiline()
        .slowQuery(100, TimeUnit.MILLISECONDS,
            (info) -> log.warn(
                "Slow query ({}ms): {}",
                info.getElapsedTime(),
                info.getQuery()))
        .countQuery()
        .build();
}
```

---

### Quick Recall

**If you remember only 3 things:**

1. `hibernate.generate_statistics=true` enables all metrics
2. Monitor: queries per request (N+1), cache hit ratio, slow queries
3. Use datasource-proxy for per-query timing and count assertions in tests
