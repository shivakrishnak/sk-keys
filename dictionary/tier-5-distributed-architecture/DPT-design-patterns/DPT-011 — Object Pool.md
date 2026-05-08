---
layout: default
title: "Object Pool"
parent: "Design Patterns"
nav_order: 11
permalink: /design-patterns/object-pool/
id: DPT-011
category: Design Patterns
difficulty: ★★★
depends_on: Singleton, Concurrency, Resource Management, Thread Safety
used_by: Database Connection Pool, Thread Pool Pattern, HTTP Connection Reuse
related: Singleton, Thread Pool Pattern, Flyweight, Prototype
tags:
  - pattern
  - deep-dive
  - performance
  - concurrency
  - java
---

# DPT-011 — Object Pool

⚡ TL;DR — Object Pool pre-creates a fixed set of expensive objects, lends them to callers, and recycles them on return — eliminating repeated construction/destruction costs.

| #771 | Category: Design Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Singleton, Concurrency, Resource Management, Thread Safety | |
| **Used by:** | Database Connection Pool, Thread Pool Pattern, HTTP Connection Reuse | |
| **Related:** | Singleton, Thread Pool Pattern, Flyweight, Prototype | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A Java web application handles 2,000 requests/second. Each request opens a database connection (authenticates, establishes TCP handshake, creates a session): 60 ms per connection open, 20 ms per close. At 2,000 req/s: 160 seconds of thread time per second spent just opening and closing connections — an impossible overhead. The database server also reaches its connection limit of 200 simultaneously active connections immediately, rejecting new ones with "too many connections."

**THE BREAKING POINT:**
Database connections are "heavy" objects: they involve OS-level TCP sockets, database-side session state, authentication tokens, and memory allocations on both sides. Creating and destroying them per-request is like hiring a plumber and immediately firing them after every single tap-repair — paying full recruitment costs for 2 minutes of work. At production scale, this saturates both the application server's CPU and the database server's connection capacity.

**THE INVENTION MOMENT:**
This is exactly why the Object Pool pattern was created. Pre-create 20 connections at startup. When a request needs one: borrow from the pool (microseconds). Use it. Return it. The next request gets the same physical connection re-used. Construction cost: 60 ms × 20 = 1.2 seconds at startup. Runtime cost per borrow: ~5 µs. 2,000 req/s now uses the same 20 connections in rotation with sub-millisecond overhead.

---

### 📘 Textbook Definition

The **Object Pool** pattern is a creational and resource management design pattern that maintains a set of pre-initialised, reusable objects. When a client needs an object, it borrows one from the pool rather than creating a new one. When the client is done, it returns the object to the pool rather than destroying it. The pool manages the lifecycle (creation, validation, reset, destruction) of pooled objects. The pattern is essential for managing objects whose creation and destruction are significantly more expensive than configuration and reuse.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Borrow a pre-built expensive object, use it, return it — never build or destroy it in the hot path.

**One analogy:**
> A library book system. The library pre-buys 10 copies of a popular book. Readers borrow a copy, read it, and return it. The next reader gets the same physical book. The library never prints new books on demand — it manages a fixed pool of copies.

**One insight:**
An Object Pool is not just an optimisation — it is also a *resource governor*. The pool's maximum size defines the maximum concurrent resource usage. A database connection pool capped at 20 forces all requests to share 20 connections — protecting the database from being overwhelmed. The pool is a backpressure mechanism, not just a cache.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Object creation has a fixed overhead so large that paying it per-use is intolerable at production throughput.
2. The pooled object can be validly reset to a clean state and reused by a subsequent borrower.
3. The number of simultaneously active instances must be bounded to protect the underlying resource.

**DERIVED DESIGN:**
Given invariant 1: pre-create objects at pool initialisation (eager) or on first use up to pool maximum (lazy). Given invariant 2: on return, validate the object (is the connection still open? is the thread still runnable?) and reset it (clear any per-borrower state). Given invariant 3: cap pool size at `maxPoolSize`. When all objects are borrowed, subsequent borrow requests block (wait for a return) or fail fast (throw after timeout).

Key state machine for a pooled object:
```
IDLE (in pool) → BORROWED (in use) → IDLE (returned, reset)
                                   → DESTROYED (failed validation after return)
```

Thread-safe pool requires: thread-safe borrow/return operations; no two threads receive the same object simultaneously; blocking borrow waits correctly without spinning.

**THE TRADE-OFFS:**
**Gain:** Eliminates per-request object creation/destruction cost; provides resource governance (bounded concurrency to downstream systems); reducing GC pressure (long-lived objects avoid GC overhead).
**Cost:** Pre-created objects consume memory even when idle; pool size requires tuning (too small: requests wait; too large: overwhelms downstream); resource leaks if borrowed objects are never returned; stale objects in the pool must be detected and replaced; complexity compared to simple `new`.

---

### 🧪 Thought Experiment

**SETUP:**
An HTTP service calls a downstream payment API. Each outbound call requires an SSL-authenticated HTTP connection (TLS handshake: 150 ms). The service handles 500 payment requests/second.

**WHAT HAPPENS WITHOUT OBJECT POOL:**
Each of 500 requests/second creates a new HTTPS connection (150 ms) and closes it after. 500 × 150 ms = 75 seconds of TLS handshake time per second — far exceeding available CPU. TLS sessions cannot be established fast enough. Requests pile up. Latency explodes. At 500 req/s, the service effectively cannot function.

**WHAT HAPPENS WITH OBJECT POOL (keep-alive connection pool):**
10 persistent connections are established at startup (10 × 150 ms = 1.5 seconds). Each of 500 requests borrows a connection in ~5 µs, sends the payment request over the existing TLS session (no handshake), and returns the connection. At 500 req/s, average connection utilisation is ~50 ms per request across 10 connections = 10 × 1,000 ms / 50 ms = 200 requests/second per connection × 10 = 2,000 requests/second capacity. Pool of 10 handles the load with <1% overhead.

**THE INSIGHT:**
Object Pool converts per-request creation cost into startup cost, and converts unbounded resource usage into bounded, manageable concurrency.

---

### 🧠 Mental Model / Analogy

> An Object Pool is a car rental agency. The agency has 20 cars (pool size). Customers rent a car (borrow), return it when done. The agency washes and inspects the car (reset and validate), then makes it available for the next customer. If all 20 cars are rented, new customers wait or go elsewhere. The agency never builds a new car on demand — the fleet is fixed.

- "Car rental agency" → the Object Pool manager
- "Fleet of 20 cars" → pre-created pool of connections/threads
- "Renting a car" → borrowing from the pool (lease/acquire)
- "Wash and inspect on return" → validation and reset logic
- "All cars rented, customer waits" → borrow blocks (queue)
- "Car breaks down — removed from fleet" → invalid object destroyed

Where this analogy breaks down: a rental agency can grow its fleet over time. Object Pools typically have a fixed maximum size to protect the downstream resource.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
An Object Pool is a recycling system for expensive objects. Instead of making a new one every time and throwing it away after, you keep a small stock, pass them around, and get them back when each borrower is done.

**Level 2 — How to use it (junior developer):**
Don't implement your own database connection pool in 2024. Use HikariCP (fastest Java DBCP), Apache Commons Pool 2, or c3p0. Configure: `maximumPoolSize` (how many connections), `minimumIdle` (kept warm when idle), `connectionTimeout` (max wait before throwing), `idleTimeout` (close idle connections). For thread pools: use `java.util.concurrent.ThreadPoolExecutor` instead of creating threads directly. The pool is a black box — borrow via `dataSource.getConnection()`, always release in `finally` or try-with-resources.

**Level 3 — How it works (mid-level engineer):**
Pool internally manages a queue of available objects. Borrow: atomically dequeue the head, mark as borrowed, return to caller. If empty: wait (on a `Semaphore` or `LinkedBlockingQueue`) up to `connectionTimeout`. Return: validate (ping database or check socket), reset per-caller state, enqueue back. Proactive health checking ("keeper" thread) pings idle connections every N seconds and replaces stale ones. HikariCP uses a `ConcurrentBag` (lock-free, thread-biased connection borrowing) — each thread has a local list of connections it previously used, reducing contention at high concurrency.

**Level 4 — Why it was designed this way (senior/staff):**
Pool size tuning is a non-trivial systems problem. The ideal pool size depends on: downstream service's connection throughput, average request hold time, desired tail latency SLO, and application thread count. A common mistake: set pool size = number of application threads (1:1 ratio). This creates all core count connections while threads wait, leading to starvation when any thread holds a connection and waits for I/O while other threads need a connection. The optimal pool size is often surprisingly small: for CPU-bound databases, pool_size ≈ number of database CPU cores × 2. HikariCP's documentation explicitly recommends starting at 10 and tuning down. The Pool is also a backpressure signal — if borrow blocks regularly, the system is over-subscribed and needs capacity, not a bigger pool.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────────┐
│  OBJECT POOL STATE MACHINE                      │
│                                                 │
│  ┌──────────┐                                   │
│  │  IDLE    │ ← objects waiting in pool queue   │
│  │  (free)  │                                   │
│  └────┬─────┘                                   │
│       │  borrow()                               │
│       ↓                                         │
│  ┌──────────┐                                   │
│  │ BORROWED │ ← held by one borrower thread     │
│  │ (in use) │                                   │
│  └────┬─────┘                                   │
│       │  return()                               │
│       ↓                                         │
│  ┌──────────┐   fails validation                │
│  │VALIDATION│ ────────────────────────────────→ │
│  │  CHECK   │                             DESTROY│
│  └────┬─────┘                                   │
│       │  passes                                 │
│       ↓                                         │
│  ┌──────────┐                                   │
│  ��  RESET   │ ← clear per-borrower state        │
│  └────┬─────┘                                   │
│       │                                         │
│       ↓                                         │
│    IDLE again                                   │
└─────────────────────────────────────────────────┘
```

**Borrow under pool exhaustion:**
```
Pool has 0 available objects
  → borrower thread blocks on queue.poll(timeout)
  → waits up to connectionTimeout (e.g., 30 seconds)
  → if another thread returns an object:
      → waiting thread receives it immediately
  → if timeout expires:
      → throws SQLTimeoutException or PoolExhaustedException
```

**Keep-alive mechanism:**
```
Background thread (every 30 seconds):
  for each IDLE object in pool:
    if (now - lastUsedTime > idleTimeout):
      destroy(object)
      if (currentSize < minIdle):
        create new replacement object
    else:
      send validation query (SELECT 1)
      if validation fails: destroy + replace
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
HTTP request arrives at servlet
  → service layer calls userRepo.findById(id)
  → repository calls dataSource.getConnection()
  → HikariCP pool borrow()       ← YOU ARE HERE
  → returns pre-created Connection in ~5µs
  → repository executes SQL, reads result
  → connection released via try-with-resources
  → pool receives connection back → validates → resets
  → Connection is IDLE again for next borrower
```

**FAILURE PATH:**
```
All N connections busy (pool exhausted)
  → getConnection() blocks 30 seconds
  → times out → throws SQLTimeoutException
  → request fails with 503 Service Unavailable
  → Alert fires: "connection pool exhaustion"
  Root causes: queries too slow, pool too small,
    connections not returned (leak)
```

**WHAT CHANGES AT SCALE:**
At 10,000 req/s, pool size tuning becomes critical. A pool of 10 serving 10,000 req/s must turn over each connection 1,000 times/second — each loan must last ≤ 1 ms. If any query takes 50 ms, 10 connections become a bottleneck. At this scale: read replicas split the load, and pool sizes per replica are tuned to match query rates. Observability (pool metrics: active, idle, waiting, timeout rate) is mandatory.

---

### 💻 Code Example

**Example 1 — BAD: New connection per query:**
```java
// BAD: 60ms per connection open, unbounded connections
public User findById(long id) {
    // Creates new TCP connection + auth every call!
    try (Connection conn = DriverManager.getConnection(
            url, user, pass)) {
        PreparedStatement ps = conn.prepareStatement(
            "SELECT * FROM users WHERE id = ?");
        ps.setLong(1, id);
        return map(ps.executeQuery());
    }
}
```

**Example 2 — GOOD: HikariCP connection pool:**
```java
// HikariCP configuration — set once at startup
HikariConfig config = new HikariConfig();
config.setJdbcUrl("jdbc:postgresql://db:5432/app");
config.setUsername("app");
config.setPassword("secret");
config.setMaximumPoolSize(20);      // max concurrent conns
config.setMinimumIdle(5);          // keep 5 warm always
config.setConnectionTimeout(30_000); // 30s wait before fail
config.setIdleTimeout(600_000);    // 10min idle, then close
config.setMaxLifetime(1_800_000);  // 30min max connection age
config.setConnectionTestQuery("SELECT 1"); // health check

HikariDataSource dataSource = new HikariDataSource(config);

// Usage — pool manages borrow/return automatically:
public User findById(long id) {
    // getConnection() borrows in ~5µs from pool
    try (Connection conn = dataSource.getConnection();
         PreparedStatement ps = conn.prepareStatement(
             "SELECT * FROM users WHERE id = ?")) {
        ps.setLong(1, id);
        return map(ps.executeQuery());
    }
    // try-with-resources AUTOMATICALLY returns to pool
    // Never call conn.close() manually in a finally block
    // with HikariCP — try-with-resources is the safe pattern
}
```

**Example 3 — Custom lightweight pool for non-DB resources:**
```java
// Generic pool for any expensive object type
public class GenericPool<T> {
    private final BlockingQueue<T> pool;
    private final Supplier<T> factory;
    private final Consumer<T> resetFn;

    public GenericPool(int size,
                       Supplier<T> factory,
                       Consumer<T> resetFn) {
        this.factory = factory;
        this.resetFn = resetFn;
        this.pool = new LinkedBlockingQueue<>(size);
        // Eager initialisation
        for (int i = 0; i < size; i++) {
            pool.offer(factory.get());
        }
    }

    // Borrow — blocks if pool empty
    public T borrow(long timeoutMs)
            throws InterruptedException {
        T obj = pool.poll(timeoutMs,
                          TimeUnit.MILLISECONDS);
        if (obj == null) throw new RuntimeException(
            "Pool exhausted after " + timeoutMs + "ms");
        return obj;
    }

    // Return — resets state before making available
    public void release(T obj) {
        resetFn.accept(obj);   // clear per-use state
        pool.offer(obj);       // back to pool
    }
}

// Usage: pool of 5 RsaSigners (expensive key loading)
GenericPool<RsaSigner> signerPool = new GenericPool<>(
    5,
    () -> new RsaSigner(keyStore),  // expensive: 200ms
    signer -> signer.clearContext()  // reset: 0.1ms
);

RsaSigner signer = signerPool.borrow(5000);
try {
    return signer.sign(data);
} finally {
    signerPool.release(signer);
}
```

**Example 4 — Pool monitoring with JMX/Micrometer:**
```java
// HikariCP exposes pool metrics automatically
// Register with Micrometer for Grafana/Prometheus:
HikariDataSource ds = new HikariDataSource(config);

MeterRegistry registry = new PrometheusMeterRegistry(
    PrometheusConfig.DEFAULT);
ds.setMetricRegistry(registry);

// Key metrics to alert on:
// hikaricp_connections_active    — currently borrowed
// hikaricp_connections_idle      — waiting in pool
// hikaricp_connections_pending   — requests waiting
// hikaricp_connection_timeout_total — exhaustion events
// Alert if pending > 0 for > 5 seconds → pool too small
// Alert if timeout_total increasing → critical issue
```

---

### ⚖️ Comparison Table

| Pattern | Object Lifecycle | Use Case | Thread Safety | Bounded? |
|---|---|---|---|---|
| **Object Pool** | Borrow → use → return | Expensive reusable resources | Required | Yes (pool max) |
| Prototype | Clone once per use | Expensive construction, disposable | Any | No |
| Singleton | Permanent shared use | Single shared resource | Required | 1 (always) |
| Flyweight | Permanent shared state | Many objects sharing immutable state | Usually yes | By design |
| Factory Method | Create per use | Variable polymorphic type | Not needed | No |

How to choose: use Object Pool when objects are expensive to create AND can be safely reset for reuse AND concurrent usage must be bounded. Use Prototype when objects are expensive to create but each user needs their own independent copy permanently. Use Flyweight when the expensive state is immutable and can be shared without borrowing.

---

### 🔁 Flow / Lifecycle

```
POOL LIFECYCLE
──────────────────────────────────────────────────
STARTUP
  → create minIdle objects via factory()
  → validate each (connectivity check)
  → add to available queue
  → pool is READY

REQUEST PHASE
  → borrow():
      if available: dequeue, mark BORROWED
      if empty: wait up to connectionTimeout
      if timeout: throw exception
  → caller uses object
  → release():
      validate object (still healthy?)
      if valid: reset state, enqueue to available
      if invalid: destroy, create replacement

MAINTENANCE (background thread, periodic)
  → scan idle objects
  → if exceed maxLifetime: destroy + replace
  → if idle too long (idleTimeout): destroy
  → if pool below minIdle: create new objects
  → health check via testWhileIdle query

SHUTDOWN
  → signal stop
  → wait for all borrowed objects to be returned
  → destroy all objects (close connections, etc.)
  → pool is CLOSED
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Bigger pool = better performance | Beyond the optimal size, a larger pool exhausts the downstream resource faster. For databases: pool_size > db_cores × 2 is often counter-productive |
| Object Pool guarantees thread safety of the pooled objects | The pool ensures each object is used by at most one thread at a time. Thread safety of the object's methods is a separate concern |
| Connections are automatically returned when the method finishes | Only if using try-with-resources or proxy wrappers. If `conn.close()` is never called, the connection leaks and the pool exhausts silently |
| Pool validation overhead is negligible | `SELECT 1` validation on every borrow adds latency. HikariCP defaults to validation only on idle connections, not on every borrow — a better default for performance |
| Object Pool and Thread Pool are different things | Thread Pool IS an Object Pool applied to threads. Thread Pool borrows a thread from a fixed pool to execute a task, then returns it when the task completes |

---

### 🚨 Failure Modes & Diagnosis

**1. Connection Leak — Pool Silent Exhaustion**

**Symptom:** Application works for minutes, then all requests hang indefinitely. Logs show "connection timeout" after 30 seconds. Restarting the application fixes it for another few minutes.

**Root Cause:** A code path borrows a connection and throws an exception before returning it. Without try-with-resources, the connection is never returned to the pool. Over time, all connections are "borrowed" but never returned — the pool is exhausted.

**Diagnostic:**
```bash
# HikariCP leak detection — set in config:
config.setLeakDetectionThreshold(2000); # 2 seconds
# Log warning if connection held > 2s:
# "Connection leak detection triggered for..."
# with stack trace of borrow site

# Active metrics:
SELECT * FROM pg_stat_activity
  WHERE state != 'idle';
-- Count should equal active requests, not accumulate
```

**Fix:**
```java
// BAD: exception between borrow and explicit close = leak
Connection conn = dataSource.getConnection();
doSomethingRisky();  // throws! conn never closed
conn.close();

// GOOD: try-with-resources guarantees return
try (Connection conn = dataSource.getConnection()) {
    doSomethingRisky();
}  // conn.close() called in finally automatically
```

**Prevention:** Always use try-with-resources for borrowed objects. Enable `leakDetectionThreshold` in HikariCP. Automated code review rule: every `getConnection()` must be inside a try-with-resources.

---

**2. Pool Exhaustion Under Load — All Connections Active**

**Symptom:** Under normal load, P99 latency is 50 ms. When load doubles, latency spikes to 30 seconds then fails with `SQLTimeoutException`. Pool metrics show `hikaricp_connections_pending > 0`.

**Root Cause:** Pool size is insufficient for the request rate × average hold duration. With pool=10, hold=200ms, throughput = 10 / 0.2 = 50 req/s maximum. Above 50 req/s, requests queue.

**Diagnostic:**
```bash
# Prometheus/Grafana query for pool pressure:
rate(hikaricp_connections_timeout_total[1m])
# Anything > 0 = exhaustion happening

# Check average hold time:
hikaricp_connections_usage_seconds{pool="mainPool"}
# If > 100ms average, queries are slow — fix queries first
```

**Fix:**
1. First, profile slow queries — reducing hold time is more impactful than increasing pool size.
2. If queries are optimal, increase `maximumPoolSize` incrementally (but not beyond database capacity).
3. Add read replicas to distribute query load.

**Prevention:** Load test at 2× expected peak. Alert on `pending_connections > 0` for more than 5 seconds.

---

**3. Stale Connection — Object Used After Network Disconnect**

**Symptom:** `SQLException: broken pipe` or `SocketException: Connection reset` on first use of a borrowed connection after a period of low traffic (overnight, weekends).

**Root Cause:** The database server or a firewall closed idle connections after a timeout. The pool's idle objects became stale (socket closed on the database side) but the pool doesn't know — it can't detect a closed socket until an operation is attempted on it.

**Diagnostic:**
```bash
# Check database server's idle timeout:
SHOW wait_timeout;  # MySQL — default 8 hours
SHOW idle_in_transaction_session_timeout; # PostgreSQL
# If shorter than pool maxLifetime: connections go stale

# Check pool maxLifetime:
config.getMaxLifetime() # Should be < DB idle timeout
```

**Fix:**
Set `maxLifetime` to less than the database or firewall's idle timeout. Enable `keepaliveTime` (HikariCP 5.0+) to ping idle connections periodically.

**Prevention:** Set `maxLifetime` = 30-minute and `keepaliveTime` = 30-second as safe defaults. Always set `maxLifetime` < any network device's idle timeout (typically 30 minutes for AWS security groups).

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Singleton` — Object Pool is often itself a Singleton (one pool instance); understanding singleton lifecycle management is foundational
- `Concurrency` — borrow and return operations must be thread-safe; the pool is inherently shared across threads
- `Resource Management` — deterministic resource release (try-with-resources) is essential; understanding Java's resource lifecycle prevents leaks

**Builds On This (learn these next):**
- `Thread Pool Pattern` — Thread Pool is Object Pool applied to threads; understanding Object Pool directly explains how ThreadPoolExecutor works
- `Database Connection Pool` — the canonical production application of Object Pool; HikariCP, c3p0, and DBCP2 are implementations to know
- `Bulkhead Pattern` — uses pool size as a bulkhead: isolates different request types into separate pools so one type's exhaustion does not starve others

**Alternatives / Comparisons:**
- `Prototype` — creates new instances via cloning rather than recycling; use when objects cannot be safely reset, or when copies must be independent
- `Flyweight` — shares state permanently across all users rather than lending it; use when state is immutable and sharing introduces no risk
- `Singleton` — shares one instance permanently; use when only one instance is needed, not a bounded number

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Fixed set of pre-created objects lent to  │
│              │ callers and recycled on return            │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Expensive object construction/destruction  │
│ SOLVES       │ in the hot path kills throughput          │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Pool max size = backpressure cap;         │
│              │ bigger pool ≠ always faster               │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Objects are expensive to create, can be   │
│              │ safely reset, and concurrency must be     │
│              │ bounded to protect downstream resource    │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Construction is cheap; or objects have    │
│              │ per-user state that cannot be cleaned     │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Construction cost eliminated vs memory    │
│              │ held idle + leak/stale connection risk    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Rent, don't buy — return the keys        │
│              │  when you're done."                       │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Thread Pool Pattern → Database Connection  │
│              │ Pool → Bulkhead Pattern                   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A microservice uses a thread pool of 50 threads and a database connection pool of 10. Each thread, when handling a request, acquires a database connection mid-processing. Trace exactly how a deadlock occurs when all 50 threads are simultaneously waiting for a database connection. What is the mathematical relationship between thread count, pool size, and deadlock risk? How should the thread pool and connection pool sizes be co-designed to prevent this?

**Q2.** Your Object Pool resets pooled objects by calling `reset()` on return. A `DecryptionContext` object holds an AES key loaded from a hardware security module (HSM). The `reset()` method clears the per-request decryption state but intentionally keeps the AES key in memory for reuse. A security audit finds that if an attacker can cause a pooled `DecryptionContext` to be borrowed by a tenant's request handler, the AES key from the previous tenant leaks. Describe the exact isolation boundary violation, how it manifests in a multi-tenant SaaS, and two design-level approaches to prevent cross-tenant key exposure while maintaining pool performance.

