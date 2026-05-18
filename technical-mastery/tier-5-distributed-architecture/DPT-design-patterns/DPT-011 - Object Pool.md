---
id: DPT-011
title: Object Pool
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★★★
depends_on: DPT-001, DPT-005, DPT-010
used_by: DPT-033
related: DPT-010, DPT-033, DPT-035
tags:
  - pattern
  - creational
  - advanced
  - performance
  - concurrency
status: complete
version: 4
layout: default
parent: "Design Patterns"
grand_parent: "Technical Mastery"
nav_order: 11
permalink: /technical-mastery/design-patterns/object-pool/
---

⚡ TL;DR - Object Pool pre-creates a fixed set of expensive
objects and REUSES them rather than creating and destroying
them repeatedly - eliminating allocation and initialization
cost at the expense of managing object lifecycle and state
reset between uses.

| #11 | Category: Design Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | DPT-001, DPT-005, DPT-010 | |
| **Used by:** | DPT-033 | |
| **Related:** | DPT-010, DPT-033, DPT-035 | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A web server handles 10,000 requests per second. Each request
opens a new database connection, runs a query, and closes the
connection. Database connection setup: 50-100ms (TCP handshake,
TLS negotiation, authentication, session setup). At 10,000
req/s, this means 10,000 new connection setups per second -
100x more time spent setting up connections than doing actual
work. The database server's connection limit (typically 500-2000)
is hit almost immediately.

**THE BREAKING POINT:**
With no pool, latency is 50-100ms per request just for
connection overhead. Throughput caps at the database's
connection creation rate. Under traffic spikes, connection
queue depth grows until requests time out. The database's
max_connections setting becomes the system's hard throughput
ceiling.

**THE INVENTION MOMENT:**
Object Pool: pre-create N database connections at startup.
When a request needs a connection, BORROW one from the pool
(near-zero latency). When done, RETURN it to the pool (reset
any request-specific state, no teardown). The pool
holds ready-to-use connections at all times.

**EVOLUTION:**
Connection pooling was the first and still most critical
Object Pool application in enterprise Java: HikariCP,
c3p0, DBCP, PgBouncer (proxy-level). Thread pools (the
Java Executor framework IS an Object Pool for threads -
creating and destroying threads is expensive). HTTP
connection pools in clients (OkHttp, Apache HttpClient).
Memory buffer pools in NIO (ByteBuffer pool).

---

### 📘 Textbook Definition

The **Object Pool** pattern is a Creational design pattern
that maintains a set of initialized objects ready for use,
rather than creating and destroying them on demand. When an
object is needed, it is taken from the pool; when no longer
needed, it is returned to the pool. If no objects are
available, the pool either creates new ones (up to a
configured maximum) or blocks the caller until one is
returned. Object Pool trades memory for time: pre-allocated
objects eliminate initialization cost at the cost of holding
idle resources.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Object Pool pre-creates expensive objects and lends them
to callers, getting them back when done - no construction
cost on the critical path.

**One analogy:**
> A car rental agency (the pool) keeps 20 cars (pooled
> objects) ready in the parking lot. Customers (callers)
> borrow a car (acquire from pool), drive it (use it), and
> return it (release to pool). No manufacturing delay when
> you arrive - the cars are pre-built. The rental agency
> cleans and inspects each returned car (reset state) before
> making it available again.

**One insight:**
Object Pool moves the creation cost from the critical path
(request time) to startup time. The trade-off is holding
resources even when idle. The key complexity is state reset:
a returned object must be cleaned of the previous caller's
state before the next caller receives it.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. A pooled object is in one of two states at any time:
   AVAILABLE (in the pool, ready for acquisition) or IN-USE
   (borrowed by a caller, not available).
2. The pool guarantees mutual exclusion: one object is
   never lent to two callers simultaneously.
3. A returned object is RESET before becoming available
   again: the next caller must receive a clean object with
   no state from the previous caller.

**DERIVED DESIGN:**
Three participants:
- **Pool**: manages the available/in-use sets; handles
  acquire() and release(); enforces max pool size
- **PooledObject**: the expensive resource being pooled;
  must support a reset/clean operation
- **Client**: borrows from pool via acquire(), returns
  via release(); must not use an object after release()

**KEY LIFECYCLE:**
```
Pool startup → create N objects (min pool size)
acquire() → object state: AVAILABLE → IN-USE
          → if no available: create new (if < max)
          → if at max: block OR throw OR return null
release() → reset object state (clear previous caller
  state)
          → state: IN-USE → AVAILABLE
          → notify waiting threads if any
```

**TRADE-OFFS:**

**Gain:** Near-zero object acquisition time on critical path.
Bounded resource usage (max pool size prevents resource
exhaustion). Connection reuse reduces connection overhead
on the server side.

**Cost:** Memory held for idle objects. State reset complexity
(must correctly clean ALL caller-specific state). Deadlock
risk if a caller acquires multiple objects from a pool with
max-size constraints. Object leak risk if callers forget
to return objects.

---

### 🧪 Thought Experiment

**SETUP:**
HikariCP database connection pool with `maximumPoolSize=10`.
Application receives 100 concurrent requests, all needing
a database connection simultaneously.

**WHAT HAPPENS:**
First 10 requests: each acquires one of the 10 available
connections from the pool. Acquisition time: ~0ms (atomic
queue poll).
Requests 11-100: no connections available. HikariCP's
`connectionTimeout=30s` clock starts. These 90 threads
park (sleep) waiting for a connection to be returned.
As the first 10 requests complete: each releases its
connection back to the pool. HikariCP wakes a waiting
thread. The connection is validated (ping/keepalive)
if it has been idle, then handed to the next thread.
By the time all 100 requests complete, HikariCP has
handled them all using only 10 connections, never
creating more than 10 simultaneous connections to the
database.

**THE INSIGHT:**
The pool acts as a back-pressure mechanism: when resources
are exhausted, requests queue rather than failing
immediately. The pool's `connectionTimeout` becomes the
latency SLA for requests that could not immediately
acquire a connection.

---

### 🧠 Mental Model / Analogy

> Object Pool is a LIBRARY BOOK system. The library has
> 10 copies of a popular book. Patrons (callers) check out
> a book (acquire), read it (use), and return it (release).
> When all 10 are checked out, a new patron waits on a
> hold list until one is returned. The library stamps out
> any patron's notes from the returned book (state reset)
> before giving it to the next patron.

- "Library" = the pool manager
- "Books" = pooled objects
- "Check out" = acquire()
- "Return" = release()
- "Stamp out notes" = state reset
- "Hold list" = wait queue when pool is exhausted

**Where this analogy breaks down:**
Books are passive; pooled objects (connections, threads)
may have internal state that breaks in subtle ways if not
properly reset. A connection that was mid-transaction when
"returned" corrupts the next caller silently - the library
analogy does not capture this corruption risk.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Object Pool keeps a set of pre-built objects ready to use.
Instead of building a new object for each request and then
throwing it away, you borrow one from the pool, use it,
and put it back. The pool is always ready; no construction
delay on the critical path.

**Level 2 - How to use it (junior developer):**
Use HikariCP for database connection pooling. Configure
`minimumIdle`, `maximumPoolSize`, `connectionTimeout`. Call
`dataSource.getConnection()` to acquire (returns from pool
or creates up to max). Wrap in try-with-resources to
ensure `connection.close()` is called (which returns it
to the pool, not actually closing it). Never hold a
connection longer than the request.

**Level 3 - How it works (mid-level engineer):**
HikariCP maintains a `ConcurrentBag<PoolEntry>`: a lock-free
data structure tracking available and in-use connections.
`getConnection()` does a `ConcurrentBag.borrow()`: O(1)
CAS operation if a connection is available. If none are
available and pool is below max, creates a new connection
asynchronously. If at max, parks the calling thread with
a timeout. `connection.close()` is intercepted by a proxy
that calls `ConcurrentBag.requite()` to return the connection
to available state. HikariCP validates connections before
lending them using `isValid()` or a `connectionTestQuery`.

**Level 4 - Why it was designed this way (senior/staff):**
Object Pool exists at the intersection of two truths:
(1) some objects are expensive to create and can be reused,
and (2) the number of concurrent users is bounded in practice.
The pool makes both truths useful: N objects serve M > N
concurrent users because not all M use the object at the
same moment. This is a fundamentally different approach
from caching (same data returned repeatedly) - pooled
objects are BORROWED and RETURNED, not READ from a cache.
The key design decision is what happens when the pool is
exhausted: block (back-pressure), create temporary overflow
(risk resource exhaustion), or fail fast (strict resource
control). HikariCP blocks with a timeout; this IS the
back-pressure behavior that prevents database overload.

**Level 5 - Mastery (distinguished engineer):**
Pool sizing is not obvious: setting `maximumPoolSize` too
high causes database connection exhaustion (the pool has
more connections than the database can handle). Setting it
too low causes excessive wait time. The optimal pool size
is bounded by `database_max_connections / app_instances`
(share the database resource across instances) and also
by the database server's CPU cores (more connections than
CPU cores provides no benefit for CPU-bound queries).
HikariCP's own documentation recommends a formula: `pool
size = (core_count * 2) + effective_spindle_count`. Expert
engineers also instrument pool metrics (active, idle, wait
time) to detect pool exhaustion before it causes latency
spikes: if `hikaricp_pending_threads > 0` in Prometheus,
the pool is undersized for current load.

---

### ⚙️ How It Works (Mechanism)

```
Object Pool Internal State Machine
┌────────────────────────────────────────────────────────┐
│  Pool                                                  │
│  available: [C1, C2, C3, C4, C5]  ← ready to lend    │
│  inUse: []                         ← currently lent   │
│  waitQueue: []                     ← blocked callers  │
│  maxSize: 10  minIdle: 5                               │
│                                                        │
│  acquire():                                            │
│    if available.isEmpty():                             │
│      if inUse.size() < maxSize:                        │
│        create new pooled object → return               │
│      else:                                             │
│        block thread until timeout / return available   │
│    else:                                               │
│      obj = available.poll()                            │
│      validate(obj) ← test query / isValid()            │
│      inUse.add(obj) → return obj                       │
│                                                        │
│  release(obj):                                         │
│    reset(obj) ← clear caller-specific state            │
│    inUse.remove(obj)                                   │
│    if waitQueue.notEmpty():                            │
│      hand directly to waiting thread                  │
│    else:                                               │
│      available.offer(obj)                              │
└────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
App startup: pool creates 5 connections (minIdle)
Request arrives: acquire() → poll connection from available
  → validate: is connection still alive? (ping)
  → if dead: discard, create new, retry acquire
  → connection in-use, handed to request handler
Request completes: try-with-resources calls close()
  → HikariCP proxy intercepts close()
  → clears connection state (autoCommit reset, etc.)
  → returns connection to available pool
  → notifies any waiting threads
```

**FAILURE PATH:**
```
Request acquires connection, throws uncaught exception:
  → Connection not returned to pool (object leak)
  → Pool slowly drains as more requests leak connections
  → At pool exhaustion: all requests block/timeout
  → System appears healthy until traffic spike reveals leak
```

**WHAT CHANGES AT SCALE:**
Scale multiplies the pool sizing problem. 100 app instances,
each with maxPoolSize=20 = 2,000 connections to one database.
Most databases (PostgreSQL) handle 200-500 connections well;
2,000 causes severe context-switching overhead. Solution:
a connection proxy (PgBouncer) between app and database
that maintains its own pool - the app instances pool to
PgBouncer, PgBouncer multiplexes to a smaller database pool.

---

### 💻 Code Example

**Example 1 - The problem: creating connections on demand:**

```java
// BAD: new connection per request - 50-100ms overhead each
@GetMapping("/users/{id}")
User getUser(int id) throws SQLException {
    // Opens new connection: 50-100ms TCP+TLS+auth
    try (Connection c = DriverManager.getConnection(URL, U, P);
         PreparedStatement ps =
             c.prepareStatement("SELECT * FROM users WHERE id=?")) {
        ps.setInt(1, id);
        ResultSet rs = ps.executeQuery();
        return mapResult(rs);
    } // closes connection: tears down TCP+TLS session
}
```

**Example 2 - HikariCP connection pool (correct):**

```java
// GOOD: configure once, reuse connections from pool
@Configuration
class DataSourceConfig {
    @Bean
    DataSource dataSource() {
        HikariConfig cfg = new HikariConfig();
        cfg.setJdbcUrl("jdbc:postgresql://db:5432/app");
        cfg.setUsername("app");
        cfg.setPassword("secret");
        cfg.setMaximumPoolSize(10);       // max connections
        cfg.setMinimumIdle(5);            // warm connections
        cfg.setConnectionTimeout(30_000); // wait max 30s
        cfg.setIdleTimeout(600_000);      // close idle after 10m
        cfg.setMaxLifetime(1_800_000);    // recycle after 30m
        return new HikariDataSource(cfg);
    }
}

@Repository
class UserRepository {
    private final DataSource ds;
    // Inject pooled data source

    User findById(int id) throws SQLException {
        // acquire() from pool: ~0ms (not 50-100ms)
        try (Connection c = ds.getConnection();
             PreparedStatement ps =
                 c.prepareStatement(
                     "SELECT * FROM users WHERE id=?")) {
            ps.setInt(1, id);
            return mapResult(ps.executeQuery());
        } // release() to pool: ~0ms, connection reused
    }
}
```

**Example 3 - Custom Object Pool implementation:**

```java
// GOOD: Custom pool for a heavyweight processing object
class ProcessorPool {
    private final BlockingQueue<HeavyProcessor> available;
    private final int maxSize;

    ProcessorPool(int maxSize) throws Exception {
        this.maxSize = maxSize;
        available = new ArrayBlockingQueue<>(maxSize);
        // Pre-populate pool at startup (eager)
        for (int i = 0; i < maxSize; i++) {
            available.offer(new HeavyProcessor()); // expensive
        }
    }

    public HeavyProcessor acquire(long timeoutMs)
            throws InterruptedException {
        HeavyProcessor p =
            available.poll(timeoutMs, TimeUnit.MILLISECONDS);
        if (p == null) throw new IllegalStateException(
            "Pool exhausted after " + timeoutMs + "ms");
        return p;
    }

    public void release(HeavyProcessor p) {
        p.reset(); // CRITICAL: clear caller-specific state
        available.offer(p);
    }
}

// Usage with try-finally (or custom AutoCloseable wrapper):
HeavyProcessor p = pool.acquire(5000);
try {
    p.process(input);
} finally {
    pool.release(p); // ALWAYS return - even on exception
}
```

**How to test/verify correctness:**
Test pool under concurrent load: N threads all acquiring
simultaneously, verify at most maxSize objects are lent
at once. Test object leak scenario: acquire without release,
verify pool exhaustion is detected within connectionTimeout.
Test state isolation: two threads acquire the same returned
object sequentially; verify thread B never sees thread A's
state.

---

### ⚖️ Comparison Table

| Approach               | Acquisition Cost | Memory Usage | Complexity | Best For                          |
| ---------------------- | ---------------- | ------------ | ---------- | --------------------------------- |
| **Object Pool**        | ~0ms             | Pre-allocated| High       | Expensive, frequently reused objs |
| Create on demand       | Full init cost   | Low          | None       | Cheap objects                     |
| Prototype (clone)      | Clone cost       | Per instance | Medium     | Fast copies from complex template |
| Cache (memoize)        | ~0ms (hit)       | Per value    | Medium     | Repeat reads of same data         |
| Thread-local           | ~0ms             | Per thread   | Medium     | Thread-bound single instances     |

**How to choose:** Use Object Pool when: object initialization
is measurably slow (>5ms), objects are created and discarded
frequently, and the number of concurrent users is bounded.
Use simple creation when objects are cheap to create. Use
Prototype when many similar starting-state objects are needed
without concurrency management complexity.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Object Pool is the same as a Cache | Cache stores data results to avoid re-computing; Pool manages objects to avoid re-initializing. Pool objects are BORROWED and RETURNED; cached values are read-only |
| Larger pool is always better | More connections cause more database context switching overhead; optimal pool size is limited by the server's CPU count and connection handling capacity |
| Pool objects must be stateless | Pool objects CAN have state (connections do); the requirement is that state from the PREVIOUS caller is reset before the next caller receives the object |
| try-with-resources calls DataSource.close() | HikariCP's Connection implements AutoCloseable; close() on the proxied connection returns it to the pool, it does NOT close the underlying TCP connection |
| Object Pool prevents all resource exhaustion | Pool prevents object creation exhaustion; if callers borrow and never return (leak), the pool drains and becomes a source of exhaustion |

---

### 🚨 Failure Modes & Diagnosis

**Connection Pool Exhaustion Under Load**

**Symptom:**
Under traffic spike, application latency jumps from 5ms
to 30,000ms (connectionTimeout). All requests are pending
connection acquisition. `HikariPool-1 - Connection is not
available, request timed out after 30000ms` in logs.

**Root Cause:**
Pool size is too small for peak concurrent request rate,
OR connections are being held longer than necessary (long
transaction, slow query, connection leak), OR both.

**Diagnostic Signal:**
HikariCP metrics via JMX or Micrometer:
```
hikaricp_pending_threads > 0  ← callers waiting for
  connection
hikaricp_connections_active == maximumPoolSize ← pool full
hikaricp_connections_idle == 0 ← no connections available
```
If pending_threads grows under load: pool is undersized
or connections are held too long.

**Fix:**
Short term: increase `maximumPoolSize` (if database can
handle more connections).
Medium term: identify long-held connections with slow
query log; optimize queries holding connections.
Long term: add connection pool proxy (PgBouncer) between
app tier and database for connection multiplexing.

```java
// Check average connection hold time:
cfg.setMetricsTrackerFactory(new PrometheusMetricsTrackerFactory());
// Histogram: hikaricp_connection_usage_millis_sum /
//            hikaricp_connection_usage_millis_count
// If average > 100ms: connections held too long
```

**Prevention:**
Keep database connections for the minimum time needed.
Never hold a connection across non-database operations
(HTTP calls, file I/O) that happen inside a transaction.
Set `connectionTimeout` to match your latency SLA; alert
when `pending_threads > 0` for more than 5 seconds.

---

**State Leak Between Pool Borrowers**

**Symptom:**
Requests occasionally fail with SQL errors about being in
a transaction that was not started by the current code.
Some requests see data from other requests' uncommitted
transactions. Spring's `@Transactional` seems to randomly
not commit.

**Root Cause:**
A connection is returned to the pool while in an active
transaction (the caller threw an exception and the catch
block did not roll back). The next caller receives a
connection that is mid-transaction. Its `setAutoCommit(true)`
or `rollback()` on connection return was not called.

**Diagnostic Signal:**
Add logging to connection acquisition:
```java
// Log autoCommit state on acquire
Connection c = ds.getConnection();
log.debug("acquired: autoCommit={}", c.getAutoCommit());
// If autoCommit=false when you didn't set it: previous
// caller left the connection in transaction state
```

**Fix:**
HikariCP's `autoCommit=true` configuration resets
`autoCommit` to true on connection return. Spring's
`DataSourceTransactionManager` manages rollback on exception;
ensure all code that modifies `autoCommit` is inside
Spring transaction management, not ad-hoc JDBC code.

**Prevention:**
Never directly call `connection.setAutoCommit(false)` outside
of transaction management code. Always use Spring's
`@Transactional` or explicit `TransactionTemplate` to
ensure the transaction is correctly committed or rolled back
before the connection is returned.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Prototype` - the Creational pattern focused on copying;
  Object Pool is about reuse; understand the contrast between
  copy (Prototype) and reuse (Pool)

**Builds On This (learn these next):**
- `Thread Pool Pattern` - the most important Object Pool
  application; Java's `ExecutorService` IS an Object Pool
  for threads
- `Read-Write Lock Pattern` - commonly combined with Pool
  for concurrent pool access management

**Alternatives / Comparisons:**
- `Prototype` - creates new independent copies; Pool reuses
  the same objects; Prototype for isolated starting state,
  Pool for shared expensive resources
- `Flyweight` - shares immutable state across many objects;
  Pool lends mutable objects one at a time; different
  problems with overlapping terminology

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Pre-created set of expensive objects;    │
│              │ BORROW to use, RETURN when done          │
├──────────────┼──────────────────────────────────────────┤
│ KEY PROBLEM  │ Object creation cost on the critical path│
│ IT SOLVES    │ (connections, threads, buffers)          │
├──────────────┼──────────────────────────────────────────┤
│ CRITICAL     │ State RESET on return: next caller must  │
│ REQUIREMENT  │ receive a clean object                   │
├──────────────┼──────────────────────────────────────────┤
│ FAILURE MODE │ Pool exhaustion: all objects in-use,     │
│              │ callers block or timeout                 │
├──────────────┼──────────────────────────────────────────┤
│ FAILURE MODE │ State leak: returned object not reset;   │
│              │ next caller sees previous state          │
├──────────────┼──────────────────────────────────────────┤
│ JAVA IMPL    │ HikariCP (DB), ExecutorService (threads),│
│              │ ArrayBlockingQueue (custom)              │
├──────────────┼──────────────────────────────────────────┤
│ SIZING RULE  │ pool_size = (cpu_cores * 2) + spindles   │
│              │ (HikariCP team recommendation)           │
├──────────────┼──────────────────────────────────────────┤
│ USE WHEN     │ Creation cost > 1ms AND frequent reuse   │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Thread Pool → Read-Write Lock → Flyweight│
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Object Pool: borrow + use + RETURN. "Return" is what
   makes Pool different from just pre-creating objects -
   without return, the pool drains
2. State reset on return is not optional: failing to clear
   caller-specific state causes state leaks across callers -
   the most insidious Pool bug
3. Pool size is bounded by the resource server's capacity,
   NOT by the application's desire for more concurrency;
   a larger pool than the DB can handle causes MORE latency,
   not less

**Interview one-liner:**
"Object Pool pre-creates expensive objects and lends them
to callers - borrow, use, return. HikariCP for database
connections and Java's ExecutorService for threads are the
canonical production implementations. Pool failure modes
are exhaustion (no objects available) and state leak (returned
object not reset). Optimal pool size is bounded by the
downstream resource's capacity, not the application's
concurrency."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
When an operation's setup cost dominates its execution cost,
amortize the setup across many executions. Object Pool is
the Creational expression of amortized cost: pay setup
once, use many times, never pay setup again.

**Where else this pattern appears:**
- **Thread pools** - Java's `ExecutorService` IS an Object
  Pool for threads; thread creation is expensive (1-5ms, 1MB
  stack allocation); the pool keeps N threads alive and
  reuses them for submitted tasks; `Executors.newFixedThreadPool(N)`
  creates exactly N threads and reuses them
- **HTTP connection pools** - OkHttp, Apache HttpClient,
  Java's HttpClient all maintain connection pools to reuse
  TCP connections (and TLS sessions) across multiple HTTP
  requests to the same host
- **Netty ByteBuffer pool** - `PooledByteBufAllocator` pools
  direct memory buffers to avoid expensive native memory
  allocation per I/O operation in high-throughput network code

**Industry applications:**
- **JDBC DataSource** - every enterprise Java application
  uses Object Pool via a DataSource implementation;
  HikariCP is the default in Spring Boot 2+
- **Redis connection pool** - Jedis, Lettuce both support
  connection pooling; Lettuce uses a single thread-safe
  connection (or a small pool) vs Jedis requiring a pool
  per thread; pool configuration directly impacts Redis
  throughput in high-concurrency applications

---

### 💡 The Surprising Truth

Java's `ThreadPoolExecutor` (the class behind all
`Executors.*` factory methods) is the most-used Object Pool
in the Java ecosystem - yet few engineers recognise it as
a design pattern implementation. `new Thread()` costs
1-5ms and allocates ~1MB of stack; thread creation at high
concurrency is a throughput killer. The thread pool solves
this exactly as Object Pool prescribes: pre-create threads,
borrow them for tasks, return them when tasks complete.
The `corePoolSize` is the minimum idle pool size,
`maximumPoolSize` is the max size, and `keepAliveTime`
is the idle timeout before reducing to `corePoolSize`.
If you have ever configured these parameters, you have been
a pool administrator for an Object Pool without using that
terminology.

---

### ✅ Mastery Checklist

**You have mastered this when you can:**
1. [EXPLAIN] Describe the borrow-use-return lifecycle and
   explain why state reset on return is a hard requirement
   with a concrete example of what breaks if it is skipped
2. [DIAGNOSE] Given HikariCP metrics showing `pending_threads
   > 0` and `connections_active == maximumPoolSize`, describe
   two distinct root causes and two corresponding remediation
   strategies
3. [CONFIGURE] Explain why setting `maximumPoolSize=100` for
   a service connecting to PostgreSQL with `max_connections=100`
   and 5 application instances will cause database overload
   rather than improved performance
4. [BUILD] Implement a minimal thread-safe Object Pool using
   `ArrayBlockingQueue<T>` with acquire(timeout) and release()
   methods, including the state reset hook
5. [COMPARE] Explain when to prefer Object Pool vs Prototype:
   given (a) a game engine spawning enemy instances, (b) a
   web server managing DB connections - identify which pattern
   fits each and why

---

### 🧠 Think About This Before We Continue

**Q1.** Java's `ThreadPoolExecutor` accepts a `BlockingQueue
<Runnable>` as its task queue. When the pool is at
`maximumPoolSize` AND the queue is full, it rejects the
task. HikariCP, by contrast, blocks the caller for up to
`connectionTimeout`. Design-wise: which behavior is more
appropriate for connection pooling vs task scheduling?
What system property decides which behavior to use?

*Hint: Back-pressure style. ThreadPoolExecutor: "I have a
queue to buffer tasks - if that's also full, reject." This
is appropriate when tasks can be retried or dropped. HikariCP:
"A request MUST get a connection to proceed - blocking is
correct because there is no alternative path." The decision
is whether the work can wait vs must proceed. Connection
borrowing cannot proceed without the connection; task submission
can be rejected and retried.*

**Q2.** HikariCP validates connections before lending them
using a `connectionTestQuery` ("SELECT 1") or `isValid()`
call. This adds 1-3ms to every acquisition. What is the
trade-off: when should you enable validation, when should
you disable it, and what failure mode appears if validation
is disabled?

*Hint: Validation prevents lending dead connections (TCP
connection dropped by firewall after idle period, database
restarted). Without validation: caller gets dead connection,
tries to use it, SQL error or exception, must retry. With
validation: 1-3ms extra per acquisition, but no dead
connection surprise. Disabled validation is acceptable when:
pool has `keepaliveTime` configured (HikariCP sends keepalives
to maintain connections) AND the network is reliable AND
connection lifetime is bounded by `maxLifetime`. Enabled
validation is required when: long idle periods are common,
firewalls terminate idle connections.*

**Q3.** A service uses an Object Pool for an external API
client that supports 5 concurrent connections. The service
has 4 instances, each with poolSize=5, totaling 20 concurrent
connections. The external API has a rate limit of 10
concurrent connections total. Design a distributed pool
that respects the 10-connection global limit across all
4 instances without a central coordinator bottleneck.

*Hint: True distributed pool with no coordinator is hard:
you need distributed counting. Approaches: (1) Redis counter:
`INCR pool:available`, `DECR pool:available`; claim if
counter > 0; works but Redis becomes a bottleneck.
(2) Each instance gets maxPoolSize = totalLimit / instances
= 10/4 = 2 (round down) - simple, no coordinator, but
underutilizes if some instances are idle. (3) Token bucket
in Redis with Lua script for atomic acquire/release.
Trade-off: coordination cost vs resource utilization.*

---

### 🎯 Interview Deep-Dive

**Q1: What is the difference between an Object Pool and
a Cache? When would you use each?**

*Why they ask:* Very common confusion in interviews; tests
precise vocabulary.

*Strong answer includes:*
- Cache: stores computed values to avoid re-computing them;
  values are read; multiple readers can have the same cached
  value simultaneously
- Object Pool: manages object instances to avoid re-creating
  them; objects are borrowed exclusively (one borrower at a time)
  and returned after use
- The key difference: Cache = shared access to data; Pool =
  exclusive temporary access to objects
- Use Cache: computed results, database query results,
  deserialized objects, parsed config
- Use Pool: database connections, network connections, threads,
  heavyweight processors

**Q2: Why does HikariCP's recommended pool size formula
use CPU cores rather than expected concurrent users?**

*Why they ask:* Tests understanding of why bigger pool is
not always better.

*Strong answer includes:*
- Database queries run on the database server's CPU threads
- If the database has 8 CPU cores, 8 threads can execute
  queries simultaneously; more concurrent connections means
  more context-switching overhead on the database side
- Adding connections beyond CPU capacity causes more context
  switches, MORE latency, not less
- The formula `(cpu_cores * 2) + spindle_count` accounts
  for I/O wait time: during disk I/O, another query can run
- Practical: set poolSize = min(formula, db_max_connections
  / app_instances); never let all instances saturate the db

**Q3: Describe exactly what happens when HikariCP's
`try (Connection c = ds.getConnection())` block exits.
Does the TCP connection close?**

*Why they ask:* Tests whether the candidate understands the
proxy pattern underlying pool implementations.

*Strong answer includes:*
- HikariCP wraps the real JDBC connection in a proxy
  (`ProxyConnection` class)
- When `close()` is called on the proxy: HikariCP intercepts
  the call and does NOT close the underlying TCP connection
- Instead: rolls back any open transaction (if autoCommit
  was false), resets connection state (autoCommit, isolation
  level), marks connection as AVAILABLE in the pool
- The underlying TCP connection remains open and alive,
  ready for the next borrower
- This is why `ds.getConnection()` takes ~0ms from pool
  (just a queue poll) vs 50-100ms without pool (real TCP
  connection establishment)

