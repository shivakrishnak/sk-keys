---
layout: default
title: "Failure Modes"
parent: "Distributed Systems"
nav_order: 594
permalink: /distributed-systems/failure-modes/
number: "594"
category: Distributed Systems
difficulty: ★★☆
depends_on: "Split Brain, Quorum"
used_by: "Timeouts, Circuit Breakers, Bulkhead, Retry"
tags: #intermediate, #distributed, #resilience, #fault-tolerance, #design
---

# 594 — Failure Modes

`#intermediate` `#distributed` `#resilience` `#fault-tolerance` `#design`

⚡ TL;DR — **Failure Modes** are the distinct ways distributed components fail (crash, omission, timing, byzantine) — each requiring different detection and recovery strategies, from simple retries to full Byzantine fault-tolerant consensus.

| #594            | Category: Distributed Systems               | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------ | :-------------- |
| **Depends on:** | Split Brain, Quorum                         |                 |
| **Used by:**    | Timeouts, Circuit Breakers, Bulkhead, Retry |                 |

---

### 📘 Textbook Definition

**Failure Modes** in distributed systems are classified by how nodes deviate from correct behavior. The **Failure Hierarchy** (Cristian 1991, Lynch 1996) from least to most severe: **Crash-stop failure** — node stops permanently, sends no further messages (detectable via timeout; simplest to handle); **Crash-recovery failure** — node crashes but may restart (must account for pre-crash state; Raft handles this via persistent log); **Omission failure** — node runs but drops some messages (send omission: doesn't send; receive omission: doesn't receive; network: messages lost in transit); **Timing failure** — node responds but outside expected time bounds (common in distributed systems; heartbeat timeouts classify this as "failed"); **Byzantine failure** — node sends arbitrary/incorrect/malicious messages (most severe; requires N ≥ 3f+1 nodes to tolerate f Byzantine failures via PBFT or similar). Additional failure dimensions: **Fail-slow** (node operates but at reduced throughput — hardest to detect; appears healthy but causes cascading latency); **Gray failure** (partial failure; node works for some operations but not others — firewall blocking specific ports, disk I/O only for certain patterns). In cloud environments: fail-slow and gray failures are more common than clean crash-stop, making detection and circuit-breaking critical.

---

### 🟢 Simple Definition (Easy)

Failure modes: the different ways something can break in a distributed system. A server can: (1) completely stop (crash), (2) stop responding to some requests but not others, (3) respond but very slowly, (4) respond with wrong data (bug/attacker), (5) crash and come back. Each failure type is detected differently and needs a different response. "Is the server dead or just slow?" is the fundamental question — and in distributed systems, you often can't tell the difference (you just see a timeout).

---

### 🔵 Simple Definition (Elaborated)

The hardest failure in practice is NOT the crash (easily detected) but the **fail-slow**: a server that's partially broken — maybe it processes 10% of requests correctly, 90% at 30-second latency. From outside: it looks alive (health checks pass) but it's poisoning your p99 latency. Circuit breakers detect this by counting failures and latency. Gray failures are similar: a firewall blocking HTTPS but not HTTP makes a service appear broken to some clients but not others. Distributed systems must assume every failure mode can happen simultaneously — design for all of them.

---

### 🔩 First Principles Explanation

**Each failure mode with detection and recovery:**

```
FAILURE TAXONOMY:

┌──────────────────────────────────────────────────────────────────────┐
│ Crash-Stop                                                           │
│ Node fails permanently. No messages after failure.                  │
│ Detection: timeout (wait T seconds, no response → crashed).         │
│ Recovery: no state recovery possible. Redeploy. Replicate data.    │
│ Example: JVM OOM crash, kernel panic, power loss.                  │
│ Handle: replicate data (Raft quorum), retry on other replicas.     │
└──────────────────────────────────────────────────────────────────────┘
        ↓ harder
┌──────────────────────────────────────────────────────────────────────┐
│ Crash-Recovery                                                       │
│ Node crashes then restarts with durable state.                      │
│ Detection: node reconnects, announces itself. Or: timeout → restart.│
│ Recovery: node reloads state from durable storage. Rejoins cluster. │
│ Example: etcd restart, JVM restart with persistent state.           │
│ Handle: durable state (WAL, Raft log). Leader waits for catchup.   │
│ Pitfall: stale in-memory cache on restart (cold start penalty).    │
└──────────────────────────────────────────────────────────────────────┘
        ↓ harder
┌──────────────────────────────────────────────────────────────────────┐
│ Omission                                                             │
│ Node runs but drops messages (sends or receives).                   │
│ Detection: timeout + retry. Message may have been received           │
│            but response lost (so: idempotency required for retries).│
│ Example: Full kernel send buffer (TCP buffer full, drops packets),  │
│          network switch drops UDP packets, firewall drops packets.  │
│ Handle: retry with idempotency key. Exponential backoff.           │
│ Pitfall: ambiguous: client timed out → was write applied or not?   │
│          Without idempotency: retry may double-charge user.        │
└──────────────────────────────────────────────────────────────────────┘
        ↓ harder
┌──────────────────────────────────────────────────────────────────────┐
│ Timing                                                               │
│ Node responds, but outside expected time bound.                     │
│ Detection: timeout (T ms exceeded → "failure" from requester's view)│
│ Example: GC pause, disk I/O latency spike, CPU thrashing.          │
│ Handle: timeout detection, circuit breaker, graceful degradation.  │
│ Pitfall: node wasn't failed — just slow. After timeout, node        │
│          sends response that caller already abandoned → phantom.    │
│          Zombie leader risk if leadership based on heartbeat timing.│
└──────────────────────────────────────────────────────────────────────┘
        ↓ harder
┌──────────────────────────────────────────────────────────────────────┐
│ Fail-Slow (Gray failure variant)                                    │
│ Node is functional but severely degraded in throughput/latency.    │
│ Detection: p99 latency monitoring. Health checks may still pass.   │
│ Example: disk I/O degradation (read errors, RAID rebuild),         │
│          CPU throttling (noisy neighbor in cloud), memory pressure.│
│ Handle: circuit breaker tracking response time, not just failures. │
│         Remove slow node from load balancer. Auto-scaling.         │
│ Pitfall: traditional health checks (HTTP /health returns 200)       │
│          pass even when node is severely degraded.                 │
│          → Need synthetic monitoring and latency alerting.         │
└──────────────────────────────────────────────────────────────────────┘
        ↓ hardest
┌──────────────────────────────────────────────────────────────────────┐
│ Byzantine                                                            │
│ Node sends INCORRECT or MALICIOUS messages.                        │
│ Detection: cross-validate responses from multiple nodes.           │
│ Example: bit flips in memory (ECC failure), compromised node,       │
│          software bug causing wrong values (rare but possible).    │
│ Handle: Byzantine Fault Tolerant (BFT) consensus: N ≥ 3f+1.      │
│         PBFT, Tendermint, HotStuff (blockchain consensus).         │
│ Pitfall: standard Raft/Paxos: NOT Byzantine tolerant.              │
│          A single Byzantine Raft node can corrupt entire cluster.  │
└──────────────────────────────────────────────────────────────────────┘

REAL-WORLD FAILURE TAXONOMY (what actually fails in production):

  1. Network partitions (most common "catastrophic" failure):
     - Full partition: two subnets can't communicate.
     - Partial partition: A→B works, B→A doesn't (asymmetric partition).
     - Packet loss: some packets drop, causing omission failures.

  2. Slow disk I/O (most common fail-slow):
     - NVMe latency spikes from 100μs to 10ms during GC/compaction.
     - HDD read errors → retry → slow reads → cascading latency.
     - Kubernetes: ephemeral storage throttling.

  3. Memory pressure → GC thrashing (timing failure):
     - JVM: GC pause 30s → heartbeat missed → Raft election.
     - Node still alive but unresponsive for 30s.

  4. CPU throttling (timing failure + fail-slow):
     - Cloud CPUs: burstable instances (T-series) exhaust CPU credits.
     - Container CPU limits: requests completed slowly.

  5. Software bugs (semi-Byzantine):
     - Returns incorrect data (not deliberate — bug).
     - Technically not Byzantine (no adversary), but same detection/handling.

FAILURE DETECTION IN PRACTICE:

  TIMEOUT-BASED:
    Wait T seconds. No response → node "failed."
    Problem: CANNOT distinguish crash from timing from network partition.
    T too short: false positives (slow-but-alive node considered dead → unnecessary failover).
    T too long: slow failure detection → long unavailability window.

    Raft election timeout: 150-300ms (random). Balances false positives vs. detection speed.

  HEARTBEAT-BASED (Φ Accrual Failure Detector):
    Cassandra gossip uses Φ accrual failure detector.
    Track heartbeat intervals. Compute arrival distribution.
    φ (phi) = -log(probability that heartbeat was lost).
    φ < threshold: node alive. φ > threshold: node suspected dead.
    Threshold = 8 (default): about 8 missed heartbeats in expected interval.
    Adaptive: accounts for actual network variability (high jitter → higher tolerance).

  HEALTH CHECK LIMITATIONS:
    HTTP /health → 200 OK: only checks if process is alive, not performance.
    Synthetic monitoring: send real requests (specific test queries) and measure latency.
    Application-level health: check DB connection pool, queue depth, error rate.

  GRAY FAILURE DETECTION:
    Metrics: p50/p95/p99 latency per instance.
    Error budget: track error rate per instance over 5-minute window.
    Auto-healing: if instance p99 > 5× cluster average → remove from load balancer.

FAILURE HANDLING PATTERNS:

  CRASH-STOP:
    Replicate data (N replicas, Raft/Paxos quorum).
    Retry on another replica immediately.

  CRASH-RECOVERY:
    Persistent state (WAL, Raft log). Re-sync after restart.
    Avoid long startup times (snapshot-based recovery).

  OMISSION:
    Retry with idempotency keys. Exponential backoff.
    At-least-once delivery → exactly-once via deduplication.

  TIMING:
    Timeout + fallback (circuit breaker, graceful degradation).
    Async processing: don't block caller on slow downstream.

  FAIL-SLOW:
    Circuit breaker counting latency (not just errors).
    P99 monitoring. Auto-remove slow instances from pool.

  BYZANTINE:
    Avoid if possible (internal systems: trust all nodes).
    If needed: PBFT or blockchain-style consensus.
    Validate data from multiple sources (2f+1 agreement).
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT failure mode taxonomy:

- "Handle errors" is vague — what kind of errors? Crash? Timeout? Wrong data?
- Single error handling strategy: retry everything → double-charges on omission failures
- Silent degradation: fail-slow nodes undetected, polluting p99 for all users

WITH failure mode taxonomy:
→ Precise handling: crash → retry replica; omission → idempotent retry; byzantine → multi-source validation
→ Correct detection: timeout-based for crash/timing; latency-based for fail-slow; data validation for byzantine
→ Pattern vocabulary: circuit breaker, bulkhead, retry, fallback — each targets specific failure modes

---

### 🧠 Mental Model / Analogy

> A postal system with different delivery failure modes. Crash-stop: post office permanently closed (return to sender). Crash-recovery: post office temporarily closed, reopens (deliver when it reopens). Omission: letter dropped in transit (resend — but check if first letter already arrived). Timing: delivery takes 3 weeks instead of 3 days (was it lost? Should you resend?). Fail-slow: post office processes 1 letter per hour instead of 1000 (still "working" but useless). Byzantine: postal worker delivers forged letters (validate via signed originals from multiple independent sources).

"Post office permanently closed" = crash-stop failure
"Letter dropped in transit" = omission failure (need idempotent retry)
"3 weeks instead of 3 days" = timing failure (timeout → decide: resend or abandon)
"Processes 1 letter/hour" = fail-slow (traditional health checks won't detect it)

---

### ⚙️ How It Works (Mechanism)

**Kubernetes pod failure detection:**

```bash
# Kubernetes: liveness probe = crash detection.
# readinessProbe: is the pod ready to serve? Remove from load balancer if not.
# livenessProbe: is the pod alive? Restart if not.

# Pod spec with multi-mode failure detection:
spec:
  containers:
  - name: payment-service
    livenessProbe:
      httpGet:
        path: /internal/health
        port: 8080
      initialDelaySeconds: 30
      periodSeconds: 10       # Check every 10s
      failureThreshold: 3     # 3 consecutive failures → restart pod (crash or timing failure)
      timeoutSeconds: 5       # Timeout if no response in 5s (timing failure detection)

    readinessProbe:
      httpGet:
        path: /internal/ready  # Checks DB connection, queue depth, error rate
        port: 8080
      periodSeconds: 5
      failureThreshold: 2      # Remove from service after 2 failures (fail-slow detection)

    # Fail-slow detection: custom readiness check includes latency:
    # /internal/ready returns 503 if:
    #   - p99 latency of last 100 requests > 2000ms (fail-slow)
    #   - DB connection pool exhausted (resource exhaustion)
    #   - Error rate > 5% in last 60s (high error rate)
    #   - Returns 200 OK only when all checks pass.
```

---

### 🔄 How It Connects (Mini-Map)

```
CAP Theorem (availability vs. consistency during failures)
        │
        ▼
Failure Modes ◄──── (you are here)
(taxonomy: crash-stop, crash-recovery, omission, timing, fail-slow, byzantine)
        │
        ├── Circuit Breaker (detects timing + fail-slow; stops sending to broken node)
        ├── Retry with Backoff (handles omission + transient timing failures)
        └── Timeout (the universal detection mechanism for all non-crash failures)
```

---

### 💻 Code Example

**Resilience4j handling multiple failure modes:**

```java
@Configuration
public class ResilienceConfig {

    @Bean
    public CircuitBreaker paymentCircuitBreaker(CircuitBreakerRegistry registry) {
        return registry.circuitBreaker("payment", CircuitBreakerConfig.custom()
            // Omission + Timing failure: count both exceptions AND slow calls:
            .slidingWindowType(SlidingWindowType.COUNT_BASED)
            .slidingWindowSize(20)
            .failureRateThreshold(50)           // Open if 50%+ calls fail (omission)
            .slowCallDurationThreshold(Duration.ofSeconds(2)) // Timing: >2s = slow
            .slowCallRateThreshold(80)          // Open if 80%+ calls are slow (fail-slow)
            .waitDurationInOpenState(Duration.ofSeconds(30)) // Wait 30s before retry
            .build()
        );
    }

    @Bean
    public Retry paymentRetry(RetryRegistry registry) {
        return registry.retry("payment", RetryConfig.custom()
            // Omission failure: retry on connection errors (message may not have reached server)
            .retryExceptions(ConnectException.class, SocketTimeoutException.class)
            // Crash-recovery: retry on 503 (server restarting)
            .retryOnResult(response -> response.getStatus() == 503)
            // Do NOT retry on business errors (400, 409): not a failure mode
            .ignoreExceptions(ClientErrorException.class)
            .maxAttempts(3)
            .waitDuration(Duration.ofMillis(500))
            .build()
        );
    }
}

// Service using resilience patterns per failure mode:
@Service
public class PaymentService {

    // Handles: omission (retry), timing (circuit breaker timeout),
    //          fail-slow (circuit breaker slow-call threshold), crash (fallback).
    @CircuitBreaker(name = "payment", fallbackMethod = "fallbackPayment")
    @Retry(name = "payment")
    @TimeLimiter(name = "payment") // Timeout: fail fast if > 2s (timing failure)
    public CompletableFuture<PaymentResult> processPayment(PaymentRequest req) {
        return CompletableFuture.supplyAsync(() -> {
            // Include idempotency key in request (handles omission: safe to retry):
            return paymentGateway.charge(req.toGatewayRequest()
                .withIdempotencyKey(req.getIdempotencyKey())); // Hash of (userId, amount, timestamp)
        });
    }

    // Fallback for crash-stop or open circuit breaker:
    public CompletableFuture<PaymentResult> fallbackPayment(PaymentRequest req, Exception e) {
        log.warn("Payment service unavailable. Queuing for later processing.", e);
        outbox.save(req); // Async processing via outbox pattern (eventual processing)
        return CompletableFuture.completedFuture(PaymentResult.queued(req.getId()));
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                                   | Reality                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| --------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| A timeout means the operation failed                            | A timeout means you don't know if the operation succeeded or failed. The request may have arrived, been processed, and the response was lost (omission failure on the return path). Or the request never arrived (send-side omission). Or the server processed it but slowly. This ambiguity is why idempotency is critical: retrying a timed-out operation without idempotency may double-execute it (double charge, double insert, etc.)                                                                         |
| Crash-stop is the most dangerous failure mode                   | Byzantine failure is the most dangerous. Crash-stop is the most DETECTABLE. Fail-slow is often the most IMPACTFUL in production: a failed node is quickly routed around; a slow node keeps receiving requests, slowly poisoning p99 latency for the entire service as other services wait for it. The silent, gradual degradation of fail-slow often causes more service disruption than an outright crash                                                                                                         |
| Health checks reliably detect all failure modes                 | Simple HTTP health checks (GET /health → 200 OK) only detect crash-stop and some crash-recovery failures. They do NOT detect: fail-slow (the process responds 200 OK but processes requests at 1% normal throughput), partial Byzantine (returns correct data for /health but incorrect data for business operations), resource exhaustion (DB connection pool full — process is alive but can't serve new requests), or downstream dependency failures (DB is down, but the process itself is running fine)       |
| Byzantine failures only occur in blockchain/adversarial systems | Byzantine failures can occur in any distributed system due to software bugs. A node with a memory corruption bug may send incorrect data to peers — indistinguishable from malicious Byzantine behavior. Distributed databases have had incidents where bugs caused nodes to send incorrect replication data (corrupted WAL entries), requiring Byzantine-like cross-validation to detect. Hardware bit-flip errors (without ECC memory) are another source of Byzantine-like failures in non-adversarial settings |

---

### 🔥 Pitfalls in Production

**Fail-slow node not detected by health checks, poisoning p99:**

```
SCENARIO: Payment service with 10 pods behind load balancer.
  Pod-7: disk I/O degraded (RAID array rebuilding). Processes requests at 10× normal latency.
  Health check: GET /health → 200 OK (process is alive, health endpoint responds fast).
  Load balancer: Pod-7 is "healthy." Routes 10% of traffic to Pod-7.

  Result:
    p50 latency: 5ms (normal — 90% of requests to healthy pods).
    p99 latency: 800ms (10% of requests going to Pod-7 at 10× latency + occasional retries).
    Users: 1% experiencing timeouts. Black Friday: payment failures spike.

  Health check doesn't catch fail-slow. Manual detection: ops team checks per-pod metrics.
  Hours of elevated latency before detection.

BAD: Health check only validates process liveness:
  @GetMapping("/health")
  public ResponseEntity<String> health() {
      return ResponseEntity.ok("OK"); // Always returns 200. Doesn't check performance.
  }

FIX 1: Performance-aware readiness probe:
  @GetMapping("/ready")
  public ResponseEntity<HealthStatus> ready() {
      // Check recent performance metrics:
      double recentP99 = metricsRegistry.timer("http.server.requests")
          .percentile(0.99);
      long dbConnections = connectionPool.getActiveConnections();
      long maxConnections = connectionPool.getMaximumPoolSize();

      boolean ready = recentP99 < 2000.0 &&          // p99 < 2 seconds
                      dbConnections < maxConnections * 0.9 && // Connection pool < 90%
                      errorRateTracker.getRate() < 0.05;       // Error rate < 5%

      return ready ? ResponseEntity.ok(HealthStatus.READY)
                   : ResponseEntity.status(503).body(HealthStatus.DEGRADED);
  }

FIX 2: Outlier detection in load balancer (Envoy example):
  # Envoy outlier detection: auto-ejects slow pods from load balancer.
  # envoy config:
  outlier_detection:
    interval: 10s
    base_ejection_time: 30s
    max_ejection_percent: 20  # Never eject > 20% of instances
    consecutive_5xx: 5        # Crash/omission: 5 consecutive errors → eject
    # Fail-slow: high latency detection via success_rate_ejection:
    success_rate_minimum_hosts: 5
    success_rate_request_volume: 100
    success_rate_stdev_factor: 1900  # Eject if success rate > 1.9σ below mean
```

---

### 🔗 Related Keywords

- `Circuit Breaker` — pattern to handle timing and fail-slow failures (stop sending to broken service)
- `Retry with Backoff` — pattern for omission and transient timing failures
- `Timeout` — the universal mechanism for detecting all non-crash failures
- `Byzantine Fault Tolerance` — consensus algorithm for adversarial/Byzantine failure mode

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Crash-stop < crash-recovery < omission < │
│              │ timing < fail-slow < byzantine.           │
│              │ Each mode needs different detection +     │
│              │ recovery strategy.                        │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Designing error handling; choosing retry  │
│              │ vs. circuit breaker vs. fallback strategy │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ — (Failure modes are universal; must     │
│              │ handle all in any distributed system)    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The hardest failure: a postal worker     │
│              │  who's still 'delivering' — at 1/hour."  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Circuit Breaker → Retry with Backoff →   │
│              │ Timeout → Graceful Degradation           │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A microservice calls a downstream payment gateway. The gateway sometimes returns HTTP 200 with a body of `{"status": "error", "code": "INSUFFICIENT_FUNDS"}`. Sometimes it returns HTTP 500. Sometimes it times out after 30 seconds. Sometimes it returns HTTP 200 with correct data but after 25 seconds. Which of these are "failure modes" from the caller's perspective? How should each be handled? Which ones require idempotency? Which ones should trigger circuit breaker?

**Q2.** Network partition detection dilemma: in a 3-node Raft cluster, node N3 loses network to N1 but can still communicate with N2. From N3's perspective: N1 appears crashed. From N1's perspective: N3 appears crashed (asymmetric partition). From N2's perspective: both N1 and N3 are alive. What failure mode does each node observe? How does Raft handle this asymmetric partition? Which node (if any) can become the new leader? What happens to writes during this period?
