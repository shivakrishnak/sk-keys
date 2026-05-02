---
layout: default
title: "Object Pool Pattern"
parent: "Design Patterns"
nav_order: 789
permalink: /design-patterns/object-pool-pattern/
number: "789"
category: Design Patterns
difficulty: ★★★
depends_on: "Heap Memory, Thread Safety, Connection Management, Flyweight Pattern"
used_by: "Database connection pools, thread pools, HTTP client pools, JVM string interning"
tags: #advanced, #design-patterns, #creational, #performance, #resource-management, #concurrency
---

# 789 — Object Pool Pattern

`#advanced` `#design-patterns` `#creational` `#performance` `#resource-management` `#concurrency`

⚡ TL;DR — **Object Pool** maintains a cache of reusable, pre-initialized objects — avoiding the cost of creating and destroying expensive objects on every use by lending them out and reclaiming them when done.

| #789            | Category: Design Patterns                                                        | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Heap Memory, Thread Safety, Connection Management, Flyweight Pattern             |                 |
| **Used by:**    | Database connection pools, thread pools, HTTP client pools, JVM string interning |                 |

---

### 📘 Textbook Definition

**Object Pool** (Gamma et al.; popularized as a performance pattern): a creational design pattern that maintains a set of initialized, reusable objects ready for use. When a client needs an object, it borrows one from the pool; when done, it returns it rather than destroying it. Avoids the overhead of creating/destroying expensive objects (database connections, threads, socket connections, heavyweight parsers). Key properties: **pre-initialization** (objects created at startup or lazily but not on-demand per request); **borrow/return lifecycle** (client acquires from pool, returns when done); **pool management** (max size, idle eviction, validation on borrow/return). Java: `java.sql.Connection` pools (`HikariCP`, `c3p0`); `java.util.concurrent.Executors` (thread pool = Object Pool for threads); Spring's `JdbcTemplate` uses an underlying `DataSource` connection pool.

---

### 🟢 Simple Definition (Easy)

A car rental agency. Car creation (building a new car from scratch) is expensive and slow. Rental agency (the pool) maintains a fleet of ready cars. You rent (borrow) a car when you need it, drive it, return it to the agency when done. Agency cleans the car, puts it back in the available fleet. Next customer gets the same (cleaned, ready) car. No manufacturing costs per trip. This is Object Pool: the agency is the pool, cars are the objects.

---

### 🔵 Simple Definition (Elaborated)

Database connections. Creating a new connection: TCP handshake + authentication + session setup = 50-100ms. Destroying it: teardown overhead. With `HikariCP` (the most popular JDBC connection pool): 10 connections pre-created at startup. Each request borrows one, runs queries, returns it. Borrowing from pool: <1ms. 1000 concurrent requests: still only 10 real connections. Pool manages: waiting queue, timeout, health check (validate before lending), idle eviction (close connections not used for X minutes). HikariCP's pool IS the Object Pool pattern in production.

---

### 🔩 First Principles Explanation

**Pool lifecycle and thread-safety considerations:**

```
OBJECT POOL STRUCTURE:

  class ObjectPool<T> {
      private final BlockingQueue<T> available;  // thread-safe queue of idle objects
      private final int maxSize;
      private final AtomicInteger currentSize = new AtomicInteger(0);
      private final Supplier<T> factory;         // how to create new objects
      private final Consumer<T> resetter;        // how to reset before reuse
      private final Predicate<T> validator;      // check if still healthy

      ObjectPool(int maxSize, Supplier<T> factory, Consumer<T> resetter, Predicate<T> validator) {
          this.maxSize   = maxSize;
          this.available = new LinkedBlockingQueue<>(maxSize);
          this.factory   = factory;
          this.resetter  = resetter;
          this.validator = validator;
      }

      // BORROW: get an object from the pool (blocking if pool is exhausted)
      T borrow(long timeout, TimeUnit unit) throws InterruptedException, TimeoutException {
          T obj = available.poll(timeout, unit);  // try to get an available object

          if (obj == null) {
              // No available object — try to create new one if under max size:
              if (currentSize.get() < maxSize) {
                  obj = factory.get();    // create new object
                  currentSize.incrementAndGet();
              } else {
                  // At max capacity — wait for return or timeout:
                  obj = available.poll(timeout, unit);
                  if (obj == null) throw new TimeoutException("Pool exhausted — no object available");
              }
          }

          // Validate borrowed object (e.g., connection still alive?):
          if (!validator.test(obj)) {
              // Object is stale — discard and create fresh:
              currentSize.decrementAndGet();
              obj = factory.get();
              currentSize.incrementAndGet();
          }

          return obj;
      }

      // RETURN: put object back into pool for reuse
      void returnToPool(T obj) {
          resetter.accept(obj);       // clean state: clear buffers, reset position, etc.
          boolean offered = available.offer(obj);
          if (!offered) {
              // Pool queue full (shouldn't happen if borrowed correctly) — discard:
              destroyObject(obj);
              currentSize.decrementAndGet();
          }
      }

      private void destroyObject(T obj) { /* close/cleanup */ }
  }

HIKARICP — PRODUCTION OBJECT POOL FOR JDBC:

  # application.properties — HikariCP pool configuration:
  spring.datasource.hikari.minimum-idle=5          # pre-warmed connections
  spring.datasource.hikari.maximum-pool-size=20    # max concurrent connections
  spring.datasource.hikari.connection-timeout=30000 # ms to wait for connection
  spring.datasource.hikari.idle-timeout=600000     # ms before idle connection evicted
  spring.datasource.hikari.max-lifetime=1800000    # ms before connection forcibly recycled
  spring.datasource.hikari.keepalive-time=120000   # ms between keepalive queries
  spring.datasource.hikari.connection-test-query=SELECT 1  # validate before lending

  // Spring's @Transactional automatically manages borrow/return:
  @Transactional
  void processOrder(Order order) {
      // START: borrows connection from pool
      orderRepo.save(order);         // uses borrowed connection
      paymentRepo.save(payment);     // same connection (same transaction)
      // END: returns connection to pool (commit/rollback handled)
  }

THREAD POOL — Object Pool for Threads:

  // java.util.concurrent.ThreadPoolExecutor IS an Object Pool for Thread objects.
  // Creating threads: ~100μs + stack allocation (512KB–1MB per thread).
  // Thread pool: reuse threads across multiple tasks.

  ExecutorService pool = Executors.newFixedThreadPool(10);
  // 10 threads pre-created; reused for submitted tasks.

  for (int i = 0; i < 10000; i++) {
      pool.submit(() -> processItem(items.get(i)));
      // Each task reuses an existing thread — no thread creation overhead.
  }

  pool.shutdown();  // pool gracefully waits for pending tasks, then releases threads

OBJECT POOL SIZING — LITTLE'S LAW:

  L = λ × W
  L = average concurrent pool users (connections in use)
  λ = arrival rate (requests per second)
  W = average service time per request (seconds)

  Example: 500 requests/sec, average 20ms query time:
  L = 500 × 0.020 = 10 connections needed concurrently
  Pool size: 10-15 (with headroom).

  Oversized pool: DB server overwhelmed with idle connections (connection memory, locks).
  Undersized pool: requests queue up, timeouts, latency spikes.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Object Pool:

- Create new DB connection per request: 50-100ms overhead, TCP/auth each time
- 1000 concurrent users → 1000 simultaneous connections → DB overwhelmed

WITH Object Pool:
→ 10 pre-initialized connections shared among 1000 users. Borrow: <1ms. DB gets 10 concurrent connections (manageable). Throughput increases dramatically.

---

### 🧠 Mental Model / Analogy

> Kayak rental at a lake. The rental shack (pool) maintains 10 kayaks. Visitors borrow kayaks, paddle, return them. Rental shack cleans them up, puts them back in the fleet. When all 10 are out, new visitors wait or come back later. The shack doesn't build a new kayak for each visitor — too slow, too expensive. Total visitors: unlimited. Max concurrent kayakers: 10.

"Kayak rental shack" = Object Pool manager (maintains available/leased objects)
"Visitor borrows kayak" = client acquires from pool
"Visitor returns kayak" = client returns to pool
"Shack cleans kayak before next rental" = resetter (reset state before reuse)
"Capacity check — 10 kayaks max" = maxSize constraint
"Visitor waits if all kayaks out" = blocking borrow with timeout

---

### ⚙️ How It Works (Mechanism)

```
OBJECT POOL LIFECYCLE:

  STARTUP:
  Pool creates min-idle objects (pre-warmed)

  BORROW:
  1. Check available queue — take idle object
  2. If none available AND under max: create new object
  3. If at max: wait (with timeout) for return
  4. Validate object before returning to caller

  USE:
  Client uses borrowed object exclusively

  RETURN:
  1. Reset object state (clear buffers, close transactions)
  2. Put back in available queue

  EVICTION (background):
  Idle objects beyond idle-timeout → close and remove
  Objects exceeding max-lifetime → force recycle
```

---

### 🔄 How It Connects (Mini-Map)

```
Pre-allocated reusable resource cache for expensive-to-create objects
        │
        ▼
Object Pool Pattern ◄──── (you are here)
(borrow/return lifecycle; thread-safe pool management; max size)
        │
        ├── Flyweight: shares immutable objects (vs Pool: lends mutable objects exclusively)
        ├── Singleton: one instance (vs Pool: multiple instances managed collectively)
        ├── Factory Method: Pool uses factory to create new objects when pool is empty
        └── HikariCP / Thread Pool: production Object Pool implementations
```

---

### 💻 Code Example

```java
// Simple generic object pool using BlockingQueue:
public class SimpleObjectPool<T> implements AutoCloseable {
    private final BlockingQueue<T> pool;
    private final Supplier<T> creator;
    private final Consumer<T> resetter;

    public SimpleObjectPool(int size, Supplier<T> creator, Consumer<T> resetter) {
        this.creator  = creator;
        this.resetter = resetter;
        this.pool = new LinkedBlockingQueue<>(size);
        // Pre-warm: fill pool at startup
        IntStream.range(0, size).forEach(i -> pool.offer(creator.get()));
    }

    // Try to borrow — blocks up to timeout
    public T borrow(long timeout, TimeUnit unit) throws InterruptedException {
        T obj = pool.poll(timeout, unit);
        if (obj == null) throw new IllegalStateException("Pool exhausted");
        return obj;
    }

    // Return to pool — clean state first
    public void release(T obj) {
        resetter.accept(obj);
        pool.offer(obj);
    }

    @Override
    public void close() { /* drain pool and close/cleanup objects */ }
}

// Usage: PDF parser pool (heavy constructor)
SimpleObjectPool<PdfParser> parserPool = new SimpleObjectPool<>(
    5,
    PdfParser::new,            // creator: new heavy parser
    PdfParser::reset           // resetter: clear parsed state
);

PdfParser parser = parserPool.borrow(5, TimeUnit.SECONDS);
try {
    return parser.parse(documentBytes);
} finally {
    parserPool.release(parser);  // always return — use try-finally
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                   | Reality                                                                                                                                                                                                                                                                                                                                                          |
| ----------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Object Pool always improves performance         | Only for objects with high creation cost. For lightweight objects (POJOs, simple DTOs), pool overhead (synchronization, queue operations, validation) costs MORE than just creating new objects. Profile before pooling: object creation cost vs pool overhead. Rule of thumb: pool objects whose creation takes > ~1ms (connections, threads, heavy parsers).   |
| Object Pool is thread-safe by default           | A naively implemented pool is NOT thread-safe. Multiple threads borrowing/returning simultaneously can cause double-lending (same object to two threads), pool corruption, or race conditions. Production pools use `BlockingQueue`, `ConcurrentLinkedQueue`, or other thread-safe structures. HikariCP has an extensively tuned concurrent pool implementation. |
| Returning an object always restores correctness | Only if the resetter is thorough. Incomplete reset = state leak between users. Database connection pool: if a transaction was left open on return, the next borrower inherits that transaction state. HikariCP calls `rollback()` and resets autoCommit on return. Custom pools must implement reset carefully.                                                  |

---

### 🔥 Pitfalls in Production

**Connection pool exhaustion under load:**

```java
// ANTI-PATTERN: holding a connection longer than needed — exhausts the pool:
@Service
class ReportService {
    @Autowired DataSource dataSource;

    void generateReport() throws SQLException {
        Connection conn = dataSource.getConnection();  // borrows from pool

        List<Data> data = loadData(conn);    // DB query

        // PROBLEM: connection held during slow external call:
        String enriched = externalApiClient.enrich(data);  // 2-5 seconds HTTP call!

        saveReport(conn, enriched);          // another DB query
        conn.close();                        // returns to pool — but held for 2-5+ seconds!
    }
}
// With pool size 10, only ~2 concurrent reports before pool exhausts (10 / 5 seconds each).

// FIX: return connection as soon as DB work is done; re-acquire for second DB work:
void generateReport() throws SQLException {
    List<Data> data;
    try (Connection conn = dataSource.getConnection()) {
        data = loadData(conn);               // borrow → query → return immediately
    }                                        // ← connection returned HERE (AutoCloseable)

    String enriched = externalApiClient.enrich(data);   // external call WITHOUT holding conn

    try (Connection conn = dataSource.getConnection()) {
        saveReport(conn, enriched);          // borrow again only when needed
    }
}
// Connection held for milliseconds (DB query time only), not seconds (external call time).
// Pool can serve many more concurrent requests.
```

---

### 🔗 Related Keywords

- `Flyweight Pattern` — shares immutable objects (vs Pool: exclusively lends mutable objects)
- `Thread Pool` — Object Pool for threads (`ExecutorService`, `ThreadPoolExecutor`)
- `HikariCP` — production JDBC connection pool: Object Pool implementation for DB connections
- `Singleton Pattern` — one instance; Pool manages a collection of instances
- `Factory Method` — Pool uses factory to create new objects when the pool needs to grow

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Pre-create expensive objects. Lend on    │
│              │ demand, reclaim when done. Avoids        │
│              │ creation/destruction overhead per use.   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Object creation is expensive (>1ms);     │
│              │ object count needs to be capped;         │
│              │ high request rate; DB/thread/socket mgmt │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Objects are cheap to create (POJOs);     │
│              │ objects have complex state hard to reset;│
│              │ pool overhead exceeds creation cost      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Kayak rental: 10 kayaks shared by all  │
│              │  visitors — borrow, use, return; no new  │
│              │  kayak built per visitor."               │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ HikariCP → Thread Pool → Flyweight →    │
│              │ Connection Management → Little's Law      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** HikariCP is the default Spring Boot connection pool and is famous for being extremely fast. One of its key optimizations is a custom `ConcurrentBag` data structure (instead of a standard `BlockingQueue`) that uses thread-local caching: threads that just returned a connection are most likely to get the same connection on the next borrow. Why is thread-local affinity valuable in a connection pool? How does it reduce contention compared to a global shared queue? What threading behavior in typical Java web servers (thread-per-request) makes this optimization effective?

**Q2.** Object Pool and Flyweight both avoid object creation overhead, but via different mechanisms. Flyweight: objects are SHARED simultaneously (immutable, stateless — safe to share). Object Pool: objects are LEASED exclusively (one at a time per borrower — must not be shared). What property of an object determines which pattern is appropriate? Give an example of an object that can use Flyweight but NOT Object Pool (shared by multiple callers simultaneously), and an example that requires Object Pool but NOT Flyweight (must be exclusive to one caller at a time).
