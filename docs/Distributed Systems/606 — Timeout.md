---
layout: default
title: "Timeout"
parent: "Distributed Systems"
nav_order: 606
permalink: /distributed-systems/timeout/
number: "0606"
category: Distributed Systems
difficulty: ★★☆
depends_on: Distributed Locking, Heartbeat, Failure Modes
used_by: Circuit Breaker, Retry with Backoff, Bulkhead, HTTP Clients, gRPC
related: Circuit Breaker, Retry with Backoff, Deadline Propagation, Heartbeat, Bulkhead
tags:
  - distributed
  - reliability
  - resilience
  - pattern
---

# 606 — Timeout

⚡ TL;DR — A timeout bounds the maximum time a caller waits for a response; without timeouts, slow or crashed dependencies block threads indefinitely and cascade into full service failure; timeouts must be calibrated to p99 latency and propagated through the entire call chain as a shrinking deadline.

| #606            | Category: Distributed Systems                                                  | Difficulty: ★★☆ |
| :-------------- | :----------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Distributed Locking, Heartbeat, Failure Modes                                  |                 |
| **Used by:**    | Circuit Breaker, Retry with Backoff, Bulkhead, HTTP Clients, gRPC              |                 |
| **Related:**    | Circuit Breaker, Retry with Backoff, Deadline Propagation, Heartbeat, Bulkhead |                 |

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Payment service calls a card validation API. Card validation API goes down at 2 AM. Without a timeout, Payment service threads block indefinitely on the card validation call. Each blocked thread occupies a connection pool slot. After 200 blocked threads, the payment service is completely unresponsive to new requests. The payment service is down — not because it crashed, but because it's waiting forever for a service that will never respond. The entire platform is down because of a single hung dependency with no timeout.

**THE INVENTION MOMENT:**
The timeout is one of the oldest primitives in distributed systems — socket connect timeouts and read timeouts have existed since the early days of TCP networking. The insight: a distributed call that never completes is functionally identical to a call that fails; therefore, you must set an upper bound on how long you're willing to wait and treat expiry as failure.

---

### 📘 Textbook Definition

A **timeout** is a configurable maximum duration that a caller is willing to wait for a response before declaring the operation failed. **Categories:**

- **Connection timeout**: maximum time to establish a TCP connection (typically: 1–5 seconds).
- **Read/socket timeout**: maximum time to wait for data after the connection is established (typically: 5–30 seconds depending on operation).
- **Request timeout**: end-to-end timeout for the entire request (preferred over separating connect + read).
- **Idle timeout**: maximum time an idle connection is kept alive in a pool.

**Deadline propagation**: in multi-level service calls (A→B→C→D), each hop must use the remaining portion of the original deadline, not a fixed per-hop timeout. If A gives itself 5 seconds and calls B with 5 seconds (ignoring elapsed time), B can take 5 more seconds → total latency can be N × timeout. Deadline propagation passes the absolute expiry time through gRPC context metadata / HTTP headers (`grpc-timeout`, `X-Request-Timeout`).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Set a maximum wait time for every remote call — if no response by then, fail fast and free the thread instead of waiting forever.

**One analogy:**

> Timeout is like a restaurant's 90-minute table limit. After 90 minutes, the table is automatically freed for the next customer, whether or not the current diners have finished. Without this rule (no timeout), one table that never leaves holds the entire restaurant hostage — all other customers wait indefinitely for a table that never becomes available.

**One insight:**
The worst timeout value is "no timeout." The second worst is a timeout that's too long (e.g., 60 seconds for a call that should take 200ms) — it still blocks threads for a minute, causing cascade failure, just more slowly. The correct timeout is calibrated to `p99_latency × 1.5` — it lets most calls succeed while bounding worst-case thread blocking to a reasonable duration.

---

### 🔩 First Principles Explanation

**TIMEOUT CALIBRATION:**

```
For each downstream service, measure:
  p50 latency = 50ms (typical case)
  p95 latency = 200ms (slightly elevated)
  p99 latency = 800ms (tail latency, e.g., during GC pauses)
  p999 latency = 5000ms (extremely rare, storage hiccup)

Setting timeout to p99 (800ms):
  - 99% of calls succeed within timeout
  - 1% of calls timeout (acceptable error rate)
  - Thread blocked for max 800ms per call (bounded)

Setting timeout to p50 (50ms):
  - 50% of calls timeout → unacceptable error rate

Setting timeout to p999 (5000ms):
  - Threads blocked up to 5 seconds each
  - With 200 RPS and 200 thread pool: 200 × 5s = 1000 thread-seconds of blocking
  - Pool of 200 threads filled in 1 second during an outage
  → effectively no protection against cascade failure

Rule: timeout = p99_latency × (1.5 to 2.0) with adjustment for SLA headroom
```

**DEADLINE PROPAGATION (gRPC PATTERN):**

```
Without deadline propagation:
  User request arrives. API Gateway: 30s timeout.
  Gateway calls Service B with: 30s timeout (new, full timeout).
  Service B calls Service C with: 30s timeout (new, full timeout).
  Service C calls DB with: 30s timeout (new, full timeout).

  If everything hangs: user waits 30s. API Gateway times out.
  But Service B is still running! And Service C! And DB query!
  Resource leak: calls are running for 30s each at multiple levels.
  Total wasted work: 30s × 3 services = 90 service-seconds.

With deadline propagation (gRPC ctx.WithTimeout):
  User request. Deadline: T+5s.
  API Gateway calls Service B with: Deadline=T+5s (absolute timestamp).
  Service B calls Service C: remaining = T+5s - now. (e.g., T+4.8s if 200ms elapsed).
  Service C calls DB: remaining = T+4.6s.

  If user abandons request at T+5s:
  All services detect expired deadline via context cancellation.
  All sub-calls cancel simultaneously.
  Total wasted work: near-zero. Calls cancelled the moment the deadline expires.
```

**JAVA HTTP CLIENT TIMEOUT CONFIGURATION:**

```java
HttpClient client = HttpClient.newBuilder()
    .connectTimeout(Duration.ofSeconds(2))    // connection timeout
    .build();

HttpRequest request = HttpRequest.newBuilder()
    .uri(URI.create("https://api.example.com/data"))
    .timeout(Duration.ofSeconds(5))           // read/request timeout
    .GET()
    .build();

// With deadline propagation — pass remaining deadline as timeout:
Instant deadline = requestContext.getDeadline();
Duration remaining = Duration.between(Instant.now(), deadline);
Duration timeoutForThisCall = remaining.minus(Duration.ofMillis(100)); // 100ms buffer

HttpRequest request = HttpRequest.newBuilder()
    .uri(URI.create("https://service-b/api"))
    .timeout(timeoutForThisCall)
    .build();
```

---

### 🧪 Thought Experiment

**THE CASCADING TIMEOUT AVALANCHE:**

Service A (p99=2s timeout) calls B (p99=2s timeout) calls C (p99=2s timeout).
C has a DB query that starts taking 3 seconds (DB slow).

Without deadline propagation:

- C waits 2s, times out → B gets error from C.
- B retries C. C: 2s timeout again. B total: 4s now.
- B's own timeout? Also 2s. B times out before its retry completes.
- Actually: B got C's error at 2s, retries C, C takes 2s again → B's total is 4s, but B only has 2s timeout! B times out after 2s total. A gets error from B after 2s.
- A retries? A only has 2s total. Already at 2s. A times out.

Actually, without deadline propagation, each timeout is independent:

- C: 2s timeout → fails.
- B: 2s timeout (from its own timer, starting when B received A's call) → B may timeout before C even does, or after, depending on when each started.

**The guaranteed failure mode**: with independent timeouts, user's total response time can be up to `N × timeout_per_service` (if each level retries once). Deadline propagation caps total time at the user-facing SLA.

---

### 🧠 Mental Model / Analogy

> Timeout is like a kitchen timer for cooking. You set it for 20 minutes for your pasta. When it rings, you check the pasta — regardless of whether it looks done. No timer? You might leave pasta cooking for 2 hours while doing other things, returning to mush (or fire). The timer doesn't guarantee the pasta is done; it guarantees you check and take action at a bounded time.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Set a maximum wait time for every remote call. If no response by then, fail — don't wait forever. Required for every distributed call.

**Level 2:** Connection timeout vs. read timeout vs. request timeout. Calibrate to p99 latency × 1.5. Deadline propagation: pass shrinking deadline through call chain (gRPC context, HTTP headers). Too-long timeout = slow cascade failure vs. too-short = high error rate.

**Level 3:** Hedged requests (Google SRE technique): send same request to 2 replicas after 95th percentile timeout; use whichever responds first; cancel the other. Reduces tail latency for read-heavy workloads at cost of double load for 5% of requests. Effective for read replicas, not for write paths.

**Level 4:** Timeout and retries interact: `total_allowed_time = max_attempts × timeout_per_attempt + sum(backoff_delays)`. Budget this against the user-facing SLA. For a 10-second user SLA with 3 retries, 500ms backoffs: `3 × timeout + 2 × 500ms = 10s → timeout = (10s - 1s) / 3 = 3s per attempt`. gRPC metadata `grpc-timeout` carries remaining duration in the `Hm` header format (hours, minutes, seconds, milliseconds, microseconds, nanoseconds). Context cancellation in Go: `ctx, cancel := context.WithTimeout(parentCtx, 5*time.Second)` — deadline is automatically propagated if you pass the `ctx` to downstream gRPC calls.

---

### ⚙️ How It Works (Mechanism)

**gRPC Deadline Propagation (Go):**

```go
// Client sets deadline on outgoing call:
func (s *ServiceA) HandleRequest(ctx context.Context, req *Request) (*Response, error) {
    // ctx already has a deadline from the incoming call (propagated from caller)
    // Add a local bound if needed (whichever expires first wins):
    ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
    defer cancel()

    // gRPC automatically propagates the ctx deadline via grpc-timeout metadata:
    resp, err := s.serviceBClient.ProcessRequest(ctx, &ServiceBRequest{...})
    if err != nil {
        if status.Code(err) == codes.DeadlineExceeded {
            return nil, status.Error(codes.DeadlineExceeded, "upstream timeout")
        }
        return nil, err
    }
    return mapResponse(resp), nil
}
```

---

### ⚖️ Comparison Table

| Approach                     | Thread Release Speed           | Prevents Cascade           | Complexity |
| ---------------------------- | ------------------------------ | -------------------------- | ---------- |
| No timeout                   | Never (until process dies)     | No                         | None       |
| Fixed timeout                | At expiry                      | Yes (if calibrated)        | Low        |
| Adaptive timeout (p99-based) | At tail latency bound          | Yes                        | Medium     |
| Deadline propagation         | When original deadline expires | Yes (at all levels)        | Medium     |
| Deadline + hedging           | Before p95 at each call        | Yes + reduces tail latency | High       |

---

### ⚠️ Common Misconceptions

| Misconception                             | Reality                                                                                                                                                                            |
| ----------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Timeout means the downstream call stopped | Timeout means the caller stopped waiting. The downstream service may still be processing the request (wasting resources). With deadline propagation, the downstream cancels too    |
| Longer timeout = better availability      | Longer timeout = slower cascade failure, not prevention. A hung service with a 60s timeout takes 60s to fail each request; thread pool fills slowly, then all at once              |
| Timeout on each call = sufficient         | Without deadline propagation, independent timeouts allow total latency = N × per-call timeout. The user's SLA is only respected if the outermost timeout is honored and propagated |

---

### 🚨 Failure Modes & Diagnosis

**Timeout Cascade During Downstream Recovery**

Symptom: Downstream service recovers from outage. Upstream caller's thread pool is full
(all threads blocked at timeout duration). Downstream is healthy but upstream can't process
new requests until old timeout threads expire. Service appears stuck for timeout_duration
after downstream has already recovered.

Cause: Timeout is too long (e.g., 30 seconds). Thread pool fills during outage. Recovery
takes 30 seconds of "stuck" time while old threads drain.

Fix: Use bulkhead to cap number of threads that can be consumed by each downstream
service. Reduce timeout. Add circuit breaker: opens during outage, probits new calls
while breaker is open, allowing thread pool to drain; HALF-OPEN probes test recovery
without filling the pool.

---

### 🔗 Related Keywords

- `Circuit Breaker` — activated by repeated timeouts; stops calling a consistently slow/failing service
- `Bulkhead` — bounds the thread pool damage timeouts can cause
- `Retry with Backoff` — each retry attempt needs its own timeout; total budget caps total retries
- `Heartbeat` — uses timeout to detect node failure via missed heartbeat signal
- `Graceful Degradation` — what to do when timeout fires instead of propagating the error

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│  TIMEOUT: bound the maximum wait for a remote call       │
│  Calibrate: timeout = p99_latency × 1.5                  │
│  Never: no timeout or 60+ second timeouts in hot paths   │
│  Deadline propagation: pass shrinking deadline through   │
│  gRPC: ctx.WithTimeout propagates automatically          │
│  Combine with: circuit breaker + bulkhead + retry        │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A microservice handles 500 requests/second with a thread pool of 100 threads (each request holds a thread for its duration). The downstream database normally responds in 50ms (p99=200ms). Set timeout to 300ms. Calculate: during a database outage, how many seconds until the thread pool fills completely? If timeout were 30 seconds, how many seconds until pool fills?

**Q2.** You have a 3-tier call chain: API Gateway → Order Service → Payment Service. The user-facing SLA is 3 seconds. Design the timeout budget for each tier, accounting for: (a) internal processing time at each tier (~50ms each), (b) network latency between tiers (~10ms each), and (c) one retry at the Order Service level with 200ms backoff. Show the calculation that ensures the total cannot exceed 3 seconds even in the worst case.
