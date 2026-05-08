---
layout: default
title: "Thundering Herd"
parent: "Caching"
grand_parent: "Technical Dictionary"
nav_order: 14
permalink: /caching/thundering-herd/
id: CCH-014
category: Caching
difficulty: ★★★
depends_on: Cache Stampede, Distributed Systems, Caching
used_by: System Design, Distributed Systems, Caching
related: Cache Stampede, Cache Invalidation, Negative Caching
tags:
  - caching
  - thundering-herd
  - distributed-systems
  - overload
  - deep-dive
---

# CCH-014 — Thundering Herd

⚡ TL;DR — The Thundering Herd problem occurs when many sleeping processes or connections are awakened simultaneously by a single event — each rushes to handle it, but only one can succeed, and the rest create wasteful contention; in distributed systems it manifests as: burst of reconnections after server recovery, CPU spikes from a released lock, and cache stampedes after expiry — all preventable with **staggered wakeups**, **jitter**, and **exponential backoff**.

| #484            | Category: Caching                                    | Difficulty: ★★★ |
| :-------------- | :--------------------------------------------------- | :-------------- |
| **Depends on:** | Cache Stampede, Distributed Systems, Caching         |                 |
| **Used by:**    | System Design, Distributed Systems, Caching          |                 |
| **Related:**    | Cache Stampede, Cache Invalidation, Negative Caching |                 |

---

### 🔥 The Problem This Solves

**SYNCHRONIZED EVENTS CREATE OVERLOAD:**
Many distributed systems problems share the same root cause: a large number of processes are all waiting for the same event, and when it happens, all respond simultaneously. The resource they compete for (database, server, CPU) can handle N/second requests normally, but receives N all at once — N times the sustainable rate — causing overload, OOM, timeouts, or cascading failures.

---

### 📘 Textbook Definition

The **Thundering Herd Problem** (also **stampeding herd**) is a system performance anti-pattern where a large number of waiting processes, threads, or connections are simultaneously awakened by a single event, all compete for the same limited resource, and most fail or must retry — creating a burst of wasteful work. Classic manifestations: **(1) accept() thundering herd**: pre-Linux 3.9, when a new TCP connection arrived, all sleeping threads waiting on `accept()` were woken simultaneously — only one succeeds, the rest go back to sleep. Fixed in Linux by `EPOLLEXCLUSIVE` and SO_REUSEPORT. **(2) Lock release herd**: many threads waiting on a mutex; when released, all threads wake up to compete — only one wins. **(3) Cache stampede**: all clients observe cache miss simultaneously and rush to the database — special case of thundering herd (covered in Cache Stampede). **(4) Reconnection herd**: after a server restart, thousands of clients all try to reconnect at the same time — server is overwhelmed at startup. Prevention: **jitter** (randomize retry/reconnect timing), **exponential backoff**, **circuit breakers**, **staggered initialization**.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Thundering herd = many processes wake up simultaneously for the same event, only one can win, the rest create wasted load — prevent with jitter and backoff.

**One analogy:**

> A traffic light turns green (server recovers / lock released). 500 cars were waiting. All 500 accelerate simultaneously. The first intersection (limited resource) can only handle 20 cars at a time. 480 cars jam up and stall. If cars had started with random delays (jitter): car 1 at 0ms, car 2 at 100ms, car 3 at 200ms... — the intersection handles traffic smoothly, no jam.

- "Traffic light turns green" → event (lock released, server recovered, cache expired)
- "500 cars waiting" → processes/connections waiting
- "Only 20 cars handled at once" → resource limit
- "480 cars jam" → thundering herd → overload → failures
- "Random delays" → jitter → staggered wakeup → no jam

**One insight:**
Jitter is the most important tool against thundering herds. Without jitter, any time-based retry (sleep for 5 seconds, then retry) causes all failed-simultaneously clients to retry at the same moment — creating a periodic herd. With jitter: `sleep(baseDelay + random(0, baseDelay))` distributes retries over a range, preventing synchronized spikes. AWS documents this extensively in their "Exponential Backoff and Jitter" blog post — even random (no backoff, just jitter) is much better than deterministic retries for thundering herd prevention.

---

### 🔩 First Principles Explanation

**RECONNECTION THUNDERING HERD AND FIX:**

```java
// PROBLEM: all clients reconnect with same fixed delay after server outage
// Server recovers at T=0
// All clients: sleep(5000) then reconnect
// T=5000ms: 10,000 clients all reconnect simultaneously → server overwhelmed

// FIX: exponential backoff with full jitter
public long calculateRetryDelay(int attempt) {
    // Exponential backoff: delay grows exponentially with each attempt
    long baseDelay = 1000;      // 1 second base
    long maxDelay = 30000;      // 30 second max
    long exponential = (long)(baseDelay * Math.pow(2, attempt));  // 1s, 2s, 4s, 8s...
    long capped = Math.min(exponential, maxDelay);

    // Full jitter: randomize between 0 and capped delay
    // "Full jitter" is better than "equal jitter" for thundering herd prevention
    long jitter = (long)(Math.random() * capped);

    return jitter;  // [0, min(1000 * 2^attempt, 30000)]
}

// Example connection retry:
public void connectWithRetry(String serverUrl) {
    int attempt = 0;
    while (true) {
        try {
            connect(serverUrl);
            return;  // Success
        } catch (ConnectionException e) {
            long delay = calculateRetryDelay(attempt++);
            log.info("Connection failed, retrying in {}ms (attempt {})", delay, attempt);
            Thread.sleep(delay);
        }
    }
}

// With 10,000 clients and maxDelay=30s:
// Reconnections are spread over 30 seconds
// Server receives: ~333 connections/second (sustainable)
// vs. without jitter: 10,000/second at T=5s (overwhelming)
```

**SPRING RETRY WITH BACKOFF:**

```java
// Spring @Retryable with exponential backoff + jitter
@Service
public class DatabaseService {

    @Retryable(
        value = {TransientDataAccessException.class, RecoverableDataAccessException.class},
        maxAttempts = 5,
        backoff = @Backoff(
            delay = 1000,       // initial delay 1s
            multiplier = 2,     // each retry: delay × 2
            maxDelay = 30000,   // max 30s
            random = true       // enable jitter (randomize delay ±50%)
        )
    )
    public void saveOrder(Order order) {
        orderRepository.save(order);
    }

    @Recover
    public void recoverSaveOrder(Exception e, Order order) {
        // Called after all retries exhausted
        deadLetterQueue.publish(order);
        log.error("Failed to save order {} after retries: {}", order.getId(), e.getMessage());
    }
}
```

**LOCK RELEASE THUNDERING HERD:**

```java
// PROBLEM: 1000 threads waiting on a synchronized block
// Thread holding lock finishes → all 1000 wake up → compete for lock
// Only 1 wins; 999 thrash (context switch overhead)

// FIX 1: Use ReentrantLock with fair mode (threads acquire in FIFO order)
private final ReentrantLock fairLock = new ReentrantLock(true);  // fair=true

public void processWithFairLock() {
    fairLock.lock();  // Threads are served in order they called lock()
    try {
        // Critical section
    } finally {
        fairLock.unlock();  // Wakes only NEXT thread in queue, not all threads
    }
}
// Tradeoff: fair locks have lower throughput than unfair locks
// (fair = FIFO overhead; unfair = a recently active thread gets priority = better cache utilization)

// FIX 2: Reduce contention with finer-grained locking
// Instead of one lock for all users, one lock per user ID:
private final ConcurrentHashMap<String, ReentrantLock> userLocks = new ConcurrentHashMap<>();

public void processUserAction(String userId) {
    ReentrantLock lock = userLocks.computeIfAbsent(userId, k -> new ReentrantLock());
    lock.lock();
    try {
        // Only users with the SAME userId compete — 1000× less contention
    } finally {
        lock.unlock();
    }
}
// Thundering herd for userId=X: only competing requests for user X, not all requests

// FIX 3: Semaphore-based bounded concurrency
private final Semaphore semaphore = new Semaphore(50);  // max 50 concurrent

public void processWithBoundedConcurrency() throws InterruptedException {
    semaphore.acquire();  // blocks if 50 already running; doesn't wake all at once
    try {
        // Critical section
    } finally {
        semaphore.release();  // wakes ONE waiting thread (not all 1000)
    }
}
```

**KUBERNETES POD RESTART THUNDERING HERD:**

```yaml
# PROBLEM: 100 pods all restart simultaneously (node failure, deployment)
# All 100 pods try to re-establish DB connections at the same time
# DB max_connections = 200; 100 pods × 10 connections = 1000 (5x capacity)

# FIX: Pod disruption budgets + rolling restart delay
# kubernetes/deployment.yaml:
apiVersion: apps/v1
kind: Deployment
spec:
  replicas: 100
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 5 # max 5 new pods starting simultaneously
      maxUnavailable: 5 # max 5 old pods stopping simultaneously
  # Stagger pod startup to prevent thundering herd on reconnect

  # Also: add readinessProbe delay
  containers:
    - name: api-service
      readinessProbe:
        initialDelaySeconds: 10 # Wait 10s before accepting traffic
        # Prevents new pod from immediately receiving 100% load before warmed up

# Spring Boot startup delay for connection pool initialization:
# HikariCP: minimumIdle=1 → connections grow gradually, not 10 at once
# application.yml:
spring:
  datasource:
    hikari:
      minimum-idle: 1 # start with 1 connection per pod (not all 10)
      maximum-pool-size: 10
      connection-timeout: 30000
      initialization-fail-timeout: 30000
```

---

### 🧪 Thought Experiment

**SERVER RECOVERY WITHOUT JITTER:**

A downstream API service (rate limit: 1,000 req/s) goes down at T=0. 5,000 microservice instances are calling it. Each instance detects the failure and configures: `retryDelay = 5 seconds` (fixed, no jitter).

At T=5000ms: all 5,000 instances retry simultaneously. The API receives 5,000 requests in < 1ms. API rate limiter rejects 4,000 with HTTP 429. All 4,000 retrying instances see failure, add another 5-second delay... **The herd reconstitutes exactly every 5 seconds.** The server can never recover: every time it comes back online, it's immediately overloaded again.

**With full jitter:** `retryDelay = random(0, 5000)ms`. At T=5000ms: ~200 instances retry (the ones whose random jitter was ≤ 5s). API handles 200 requests (well within 1,000/s limit). Success. Over the next 5 seconds, the remaining 4,800 instances trickle back. Server recovers gracefully. The API returns to serving steady state in 10 seconds instead of oscillating indefinitely.

---

### 🧠 Mental Model / Analogy

> Thundering herd = a stadium with 50,000 fans, all trying to exit through the same 10 doors simultaneously at the final whistle. Doors handle 100 people/minute normally. 50,000 at once: crush, panic, nobody exits efficiently. Fix: stagger the exits — section by section, with randomized 5-minute intervals. The door capacity is unchanged; the timing of demand is smoothed.

- "Final whistle" → triggering event (server recovery, lock release, cache expiry)
- "50,000 fans rushing simultaneously" → thundering herd
- "Only 10 doors" → limited resource (DB connections, API rate limit)
- "Staggered exits with random delays" → jitter + backoff
- "Section by section" → circuit breaker / rate limiting

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Thundering herd = many processes simultaneously wake up for one event, overwhelm a shared resource. Prevention: jitter (randomize retry timing) and backoff (increase delay between retries). Never use fixed retry delays without jitter.

**Level 2:** Apply in: (1) HTTP client retry (Spring @Retryable with `random=true`); (2) Kafka consumer restart (randomize poll interval); (3) connection pool initialization (start with minimumIdle=1, grow gradually); (4) Kubernetes rolling updates (maxSurge=5, not 100). Cache stampede is a special case — use mutex or stale-while-revalidate.

**Level 3:** Types of jitter: full jitter (random 0 to cap — best for thundering herd), equal jitter (cap/2 + random 0 to cap/2 — keeps some base delay), decorrelated jitter (delay = random(base, delay\*3) — good for single-client backoff). AWS benchmark: full jitter and decorrelated jitter have significantly lower 99th percentile completion times than equal jitter or exponential-without-jitter. Circuit breaker (Resilience4j) prevents thundering herd on failing services: after N failures, open circuit → all requests fail fast → no thundering herd possible (no requests reach the failing service).

**Level 4:** The thundering herd is a consequence of **synchronized state** — all clients are in the same state (waiting, failed) at the same time, and the same event triggers them all. The fundamental solution is **desynchronization**: ensure clients have different state timing (different TTLs, different retry delays, different connection intervals). This is the same principle as TCP's congestion control: when many TCP connections experience packet loss simultaneously (a congestion signal), they all back off — but with random jitter to prevent resynchronization. The Internet's stability under load depends on this randomization. Large-scale distributed systems learn the same lesson: the more synchronized your clients are, the more fragile your system is under any shared event (failure, recovery, peak load). Building in entropy (jitter, randomization) is a resilience strategy.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ RECONNECTION THUNDERING HERD WITH FULL JITTER        │
├──────────────────────────────────────────────────────┤
│                                                      │
│ WITHOUT JITTER:                                      │
│   T=0: Server crashes                                │
│   T=0 to T=5s: 10,000 clients detect failure        │
│   T=5s: ALL 10,000 reconnect simultaneously          │
│         → 10,000 TCP SYN in < 1ms                   │
│         → Server overwhelmed → crashes again         │
│         → T=10s: repeat herd                         │
│                                                      │
│ WITH FULL JITTER (base=1s, max=30s):                 │
│   T=0: Server crashes                                │
│   T=0-30s: 10,000 clients reconnect at random times  │
│         ~333 connections/second (manageable)         │
│   [HERD ← YOU ARE HERE: jitter prevents synchrony]  │
│   T=30s: All clients connected ✓                     │
│         Server gracefully handles load               │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**KAFKA CONSUMER GROUP RESTART WITH JITTER:**

```
Scenario: 50 Kafka consumers in a consumer group, all restart simultaneously (deployment)

Without jitter:
T=0: All 50 consumers start → all join consumer group simultaneously
T=0-2s: Consumer group rebalance: 50 consumers fight for 100 partitions
   → Multiple rebalances triggered (each consumer join triggers rebalance)
   → All consumers paused during rebalance
   → 10-30 second pause in message processing (rebalance storm)

With staggered startup (Kubernetes maxSurge=5 + HikariCP startup delay):
T=0-10s: 5 new consumers start and stabilize
   → Consumer group rebalances (manageable: 5 joins not 50)
T=10-20s: Next 5 consumers start
   → Rolling rebalance, not mass rebalance
T=100s: All 50 consumers started and stable
   → Total pause in processing: ~2s per 5-consumer wave, not 30s for 50

[THUNDERING HERD ← YOU ARE HERE: staggered join prevents rebalance storm]

Also add: Kafka consumer `group.instance.id` (static membership)
→ Avoids rebalance entirely if same consumer rejoins within session.timeout.ms
→ Best solution for planned restarts (zero rebalance)
```

---

### ⚖️ Comparison Table

| Context         | Thundering Herd Trigger    | Prevention                                               |
| --------------- | -------------------------- | -------------------------------------------------------- |
| Cache           | Key expires                | Mutex, stale-while-revalidate, jitter                    |
| Service restart | Server recovers            | Exponential backoff + jitter in clients                  |
| Lock release    | Mutex unlocked             | Fair lock, finer-grained locking                         |
| Kafka rebalance | All consumers restart      | Static membership, rolling restart (maxSurge)            |
| Kubernetes pods | All pods restart           | RollingUpdate strategy, readiness probe delay            |
| DNS change      | TTL expires on all clients | Short TTL + health checks (not thundering herd specific) |

---

### ⚠️ Common Misconceptions

| Misconception                                                 | Reality                                                                                                                                                                                                                                                      |
| ------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| "Thundering herd only applies to caches"                      | Thundering herd is a general pattern: lock release, TCP accept, server restart, Kafka rebalance, cron job firing. Cache stampede is one specific case                                                                                                        |
| "Exponential backoff without jitter prevents thundering herd" | Exponential backoff grows the delay but keeps it deterministic. If all clients fail at the same time with the same base delay and multiplier, they'll all retry at the same exponential time steps — still synchronized. Jitter is required to desynchronize |
| "Fair locks prevent thundering herd"                          | Fair locks prevent the "all wake up at once" issue (only next-in-queue wakes up) but at the cost of throughput. They're a form of serialization, not truly a thundering herd prevention for the original problem                                             |

---

### 🚨 Failure Modes & Diagnosis

**1. Retry Storm on Downstream Service Failure**

**Symptom:** Downstream service (payment API) is degraded. Your service's error rate is 5%. After the payment API fully recovers, your error rate INCREASES to 80% briefly, then recovers. This pattern repeats every 15 seconds.

**Root Cause:** Retry logic: `retryDelay = 15s` (fixed). When payment API fails: all in-flight requests fail, all clients schedule retry at T+15s. T+15s: 100× normal load hits payment API simultaneously (all concurrent requests + retried requests) → payment API crashes again → cycle repeats.

**Diagnosis:**

```bash
# Check retry timing patterns in logs
grep "retry" service.log | awk '{print $1}' | sort | uniq -c | sort -rn
# If you see bursts at exact 15-second intervals → thundering herd from fixed retry

# Check concurrent retries vs capacity
grep "retry attempt" service.log | xargs -I{} date -d "{}" +%s | sort -n | uniq -c
# Large count values at specific seconds = synchronized retries = thundering herd
```

**Fix:**

```java
// Replace fixed delay with exponential backoff + full jitter
RetryPolicy<Object> retryPolicy = RetryPolicy.builder()
    .handle(PaymentServiceException.class)
    .withBackoff(Duration.ofMillis(500), Duration.ofSeconds(30),
                 2.0, 0.5)  // 0.5 = 50% jitter factor
    .withMaxRetries(5)
    .build();
// Also: add circuit breaker to stop retries when service is clearly down
```

---

### 🔗 Related Keywords

**Prerequisites:** Cache Stampede, Distributed Systems, Caching
**Builds On This:** System Design, Distributed Systems
**Related:** Cache Stampede, Cache Invalidation, Negative Caching

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ PATTERN     │ Many processes awaken simultaneously = herd│
│ CAUSE       │ Synchronized state + shared event          │
│ FIX 1       │ Full jitter: random(0, max_delay)          │
│ FIX 2       │ Exponential backoff + jitter               │
│ FIX 3       │ Circuit breaker (stop retrying when down)  │
│ FIX 4       │ Staggered start (K8s maxSurge=5, not 50)  │
│ KAFKA FIX   │ Static membership (no rebalance on restart)│
│ JITTER RULE │ Never use fixed delay without jitter       │
│ ONE-LINER   │ "All wake up for one event → overwhelm    │
│             │  resource → fix with randomized timing"    │
│ NEXT EXPLORE│ Negative Caching → Distributed Cache       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE C — Design Question) A microservice calls 3 downstream APIs: Auth, Payment, Inventory. Each has its own circuit breaker and retry logic. During a network blip at 3 PM, all 3 APIs return errors for 5 seconds. After recovery, all 3 are hit simultaneously by your service's retry queues — each retry causes a thundering herd. Design a composite retry strategy that: (a) prevents thundering herd against each downstream, (b) prioritizes retrying critical operations (payments) over less critical ones (inventory cache refresh), (c) limits total concurrent retries to avoid overloading your own service.

**Q2.** (TYPE D — Failure Scenario) A Kubernetes cluster has 200 pods running a Spring Boot application. The cluster node group is recycled (all 200 pods restart simultaneously due to spot instance interruption). Within 30 seconds of restart, your RDS PostgreSQL CPU hits 100% and 50% of API requests return HTTP 503. Walk through: (a) exactly what is happening at the database level, (b) which specific configurations would have prevented this, (c) immediate mitigation steps to recover, (d) permanent infrastructure changes.
