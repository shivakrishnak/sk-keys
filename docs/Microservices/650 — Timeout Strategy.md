---
layout: default
title: "Timeout Strategy"
parent: "Microservices"
nav_order: 650
permalink: /microservices/timeout-strategy/
number: "650"
category: Microservices
difficulty: ★★☆
depends_on: "Inter-Service Communication, Resilience4j, Circuit Breaker (Microservices)"
used_by: "Retry Strategy, Fallback Strategy"
tags: #intermediate, #microservices, #reliability, #distributed
---

# 650 — Timeout Strategy

`#intermediate` `#microservices` `#reliability` `#distributed`

⚡ TL;DR — A **Timeout Strategy** ensures that a service call will not block indefinitely. Every inter-service call must have a **connection timeout** (how long to wait to establish a connection) and a **read timeout** (how long to wait for a response). Without timeouts, a slow downstream service exhausts the caller's thread pool. Best practice: timeout < retry × count < circuit breaker detection window.

| #650            | Category: Microservices                                                    | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Inter-Service Communication, Resilience4j, Circuit Breaker (Microservices) |                 |
| **Used by:**    | Retry Strategy, Fallback Strategy                                          |                 |

---

### 📘 Textbook Definition

A **Timeout Strategy** in microservices defines the maximum duration a service is willing to wait for a response from a downstream service before treating the call as failed and releasing the waiting thread or future. Timeouts are the first line of defence against cascade failures from slow downstream services. Two types: **Connection Timeout** — the maximum time to establish a TCP connection to the downstream service; **Read Timeout** (or Response Timeout) — the maximum time to wait for the downstream service to send a complete response after the connection is established. Both must be configured on every HTTP client, gRPC stub, and database connection. Without timeouts, a single slow service can block caller threads for minutes, leading to thread pool exhaustion. Timeout configuration must consider the **total timeout budget** across a call chain: if a request at the API Gateway has a 10-second budget and calls 3 services in sequence, each service should have a timeout of ~3 seconds to stay within budget. Propagating deadlines (gRPC deadline propagation, HTTP `X-Request-Deadline` headers) ensures the full chain respects the original caller's budget.

---

### 🟢 Simple Definition (Easy)

A timeout tells a service: "if you haven't heard back from PaymentService within 3 seconds, give up and handle the failure." Without a timeout, the service would wait forever (or until a TCP keep-alive drops the connection — which can take minutes). Timeouts are the simplest and most fundamental resilience mechanism.

---

### 🔵 Simple Definition (Elaborated)

`OrderService` calls `PaymentService` which normally responds in 200ms. During a database issue, PaymentService starts responding in 45 seconds. Without a timeout: each OrderService thread waits 45 seconds per call. With 50 requests/second: 50 × 45s = 2,250 blocked threads needed. Thread pool (200) exhausted in 4 seconds. With a 3-second timeout: each blocked thread is released after 3 seconds. Max concurrent blocks: 50 × 3 = 150 threads. Thread pool never fully exhausted. Circuit breaker also detects the timeouts and opens within its window. Timeouts limit the blast radius during downstream slowdowns.

---

### 🔩 First Principles Explanation

**Connection timeout vs Read timeout — two different failure modes:**

```
CONNECTION TIMEOUT (e.g., 1 second):
  Failure mode: target service not reachable at all (host down, network issue)
  Without it: TCP SYN sent → no SYN-ACK → wait for OS TCP timeout (minutes!)
  With it: if connection not established in 1s → throw ConnectTimeoutException
  Typical value: 500ms – 2 seconds (network should establish connection fast)

READ TIMEOUT (e.g., 3 seconds):
  Failure mode: connection established but server slow to respond
  Without it: connected → waiting for HTTP response → can wait forever
  With it: if no response data received in 3s → throw ReadTimeoutException
  Typical value: depends on service SLA (p99 latency × 1.5 safety factor)

TOTAL REQUEST TIMEOUT:
  Some clients have a total request timeout that covers connection + read:
  WebClient.create()
    .timeout(Duration.ofSeconds(4))  // total: 4s including connection + read
  vs per-phase:
  HttpComponentsClientHttpRequestFactory
    .setConnectTimeout(1000)   // phase 1: connect
    .setReadTimeout(3000)      // phase 2: read
```

**Timeout budget — distributed deadline propagation:**

```
PROBLEM: user request at API Gateway has 10s budget
  Gateway → ServiceA (5s timeout) → ServiceB (5s timeout) → ServiceC (5s timeout)
  Total potential wait: 15 seconds!
  User gets a 10-second timeout from the gateway, but services can wait 15s
  → inconsistent experience

SOLUTION: Deadline Propagation

  Gateway receives request at T=0 with 10s total budget
  → Add header: X-Request-Deadline: T+10s (absolute Unix timestamp)

  ServiceA receives at T=1 (1s elapsed):
  → Reads X-Request-Deadline → 9 seconds remaining
  → Set own timeout: min(5s, 9s) = 5s
  → Forward to ServiceB with X-Request-Deadline: same header

  ServiceB receives at T=3 (3s elapsed):
  → 7 seconds remaining
  → Set own timeout: min(5s, 7s) = 5s
  → Forward to ServiceC

  ServiceC receives at T=5:
  → 5 seconds remaining
  → If ServiceC has a 5s timeout: OK (exactly at budget)
  → If ServiceC's own processing takes > 5s: deadline exceeded → cancel

  gRPC handles this natively:
    stub.withDeadline(Deadline.after(5, TimeUnit.SECONDS))
    Deadline automatically propagated to child RPCs

  REST: manual header propagation required
```

**Timeout tuning — the wrong way and the right way:**

```
WRONG WAY: set all timeouts to 30 seconds "to be safe"
  → Slow service causes 30-second blocks per thread
  → 200 threads × 30s = 6,000 thread-seconds of waste
  → Thread pool exhausted quickly on any slowdown
  → Users wait 30 seconds for an error page

WRONG WAY: set all timeouts to 100ms "to be fast"
  → Normal p99 latency is 300ms for some services
  → 100ms timeout causes false timeouts under normal load
  → Circuit breaker opens on false positives
  → Unnecessary fallback invocations

RIGHT WAY: set timeout = p99 latency × 1.5 (safety margin)
  Service p99 latency | Recommended Timeout
  ------------------- | -------------------
  50ms                | 75ms
  200ms               | 300ms
  1s                  | 1.5s
  3s                  | 5s

  Measure p99 latency: use Grafana/Prometheus to find actual p99
  Don't guess: wrong timeouts cause real production issues

RIGHT WAY: set total timeout budget
  If end-to-end user SLA is 5 seconds:
  API Gateway timeout: 5s
  Per-service timeout in chain: 5s / (number of hops) × safety = ~1.5s per hop
```

---

### ❓ Why Does This Exist (Why Before What)

TCP connections don't inherently time out quickly. A connection to a slow server can hang for minutes waiting for a response. In distributed systems where one service is always calling others, an unresponsive downstream service without timeouts means threads (the most valuable finite resource in a traditional JVM service) are blocked indefinitely. Timeouts convert "thread blocked forever" into "thread blocked for at most N seconds" — a small but crucial difference that determines whether cascade failure occurs.

---

### 🧠 Mental Model / Analogy

> A timeout is like a waiter's patience limit. A customer (service) orders food (makes a request). The waiter goes to the kitchen (downstream service) and waits. Normally the kitchen responds in 2 minutes. Today the kitchen is overwhelmed. Without a patience limit: the waiter stands at the kitchen window for an hour, blocking other customers. With a 5-minute limit: the waiter returns after 5 minutes, tells the customer "kitchen is unavailable, try the salad" (fallback), and moves to the next customer. The waiter is not blocking other customers' service.

---

### ⚙️ How It Works (Mechanism)

**Configuring timeouts on different Java HTTP clients:**

```java
// 1. Spring RestTemplate:
@Bean
RestTemplate restTemplate() {
    HttpComponentsClientHttpRequestFactory factory =
        new HttpComponentsClientHttpRequestFactory();
    factory.setConnectTimeout(Duration.ofMillis(1_000));
    factory.setReadTimeout(Duration.ofMillis(3_000));
    return new RestTemplate(factory);
}

// 2. Spring WebClient (reactive):
@Bean
WebClient webClient() {
    return WebClient.builder()
        .clientConnector(new ReactorClientHttpConnector(
            HttpClient.create()
                .option(ChannelOption.CONNECT_TIMEOUT_MILLIS, 1_000)
                .responseTimeout(Duration.ofMillis(3_000))
        ))
        .build();
}

// 3. OpenFeign:
feign:
  client:
    config:
      default:
        connectTimeout: 1000
        readTimeout: 3000

// 4. gRPC stub (always use deadline, not timeout, for propagation):
PaymentServiceGrpc.PaymentServiceBlockingStub stub = ...;
// Deadline is absolute (clock time), propagates through call chain:
Deadline deadline = Deadline.after(3, TimeUnit.SECONDS);
PaymentResponse response = stub.withDeadline(deadline).processPayment(request);

// 5. Resilience4j TimeLimiter (for async calls):
resilience4j:
  timelimiter:
    instances:
      payment-service:
        timeoutDuration: 3s
        cancelRunningFuture: true  # cancel underlying CompletableFuture on timeout
```

---

### 🔄 How It Connects (Mini-Map)

```
Inter-Service Communication
(every call across network boundaries)
        │
        ▼
Timeout Strategy  ◄──── (you are here)
(first line of defence against slow downstream)
        │
        ├── Circuit Breaker → opens when timeout-based failures accumulate
        ├── Retry Strategy → retries after timeout; must combine carefully
        ├── Fallback Strategy → handles TimeoutException with graceful degradation
        └── Bulkhead Pattern → limits concurrent threads even within timeout window
```

---

### 💻 Code Example

**Timeout + Circuit Breaker integration:**

```java
// Layered: TimeLimiter wraps the call, CircuitBreaker tracks the failures:
@CircuitBreaker(name = "payment-service", fallbackMethod = "fallback")
@TimeLimiter(name = "payment-service")  // inner decorator
public CompletableFuture<PaymentResponse> processPayment(PaymentRequest request) {
    return CompletableFuture.supplyAsync(() ->
        paymentGatewayClient.charge(request));  // blocked if slow
    // TimeLimiter cancels if >3s → TimeoutException
    // CircuitBreaker records TimeoutException as failure
    // After N timeouts: circuit OPENS → no more calls (fast fail)
}

public CompletableFuture<PaymentResponse> fallback(PaymentRequest req, Exception ex) {
    if (ex instanceof TimeoutException) {
        log.warn("Payment service timeout for order {}", req.getOrderId());
    } else if (ex instanceof CallNotPermittedException) {
        log.warn("Payment circuit breaker open for order {}", req.getOrderId());
    }
    return CompletableFuture.completedFuture(
        PaymentResponse.pending(req.getOrderId(), "Payment queued for processing")
    );
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                              | Reality                                                                                                                                                                                                                 |
| ---------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Setting a high timeout is safe because it's "just waiting" | Every blocked thread consumes memory and prevents other requests from being served. 200 threads × 30s timeout = effectively a 30-second brownout window during any downstream slowdown                                  |
| Timeouts and circuit breakers solve the same problem       | Timeouts bound individual call duration. Circuit breakers detect patterns across many calls and stop all calls when the failure rate is too high. Timeouts are per-call; circuit breakers are systemic. Both are needed |
| HTTP connection keep-alive prevents the need for timeouts  | Keep-alive prevents reconnection overhead — it does not reduce the read timeout window. A slow server can still hold a keep-alive connection open while processing a request indefinitely without a read timeout        |

---

### 🔥 Pitfalls in Production

**Timeout too short relative to downstream's actual p99 — false circuit trips**

```
SCENARIO:
  PaymentService normal p99: 800ms
  OrderService timeout: 500ms (set too low)
  → 20% of normal requests timeout
  → Circuit breaker accumulates 20% failure rate
  → At 60% threshold: never opens (20% fails only)
  → But: 20% of payments fail → customers frustrated

  OR with stricter circuit breaker:
  failureRateThreshold=15% → circuit opens during NORMAL operation!
  Payment service is fine, but OrderService's bad timeout makes it appear broken.

HOW TO DETECT:
  Look at Prometheus metric:
  resilience4j_circuitbreaker_failure_rate{name="payment-service"} = 18
  (18% failure rate when payment service is healthy)
  → Your timeout is too short

HOW TO FIX:
  1. Measure actual p99: query Grafana → find p99 latency of PaymentService calls
  2. Set timeout = max(p99 × 1.5, p99 + 2σ standard deviation)
  3. Re-measure after change: failure rate should drop to near-zero

  Rule: timeoutDuration > your service's p99 response time (measured, not guessed)
```

---

### 🔗 Related Keywords

- `Circuit Breaker (Microservices)` — opens when timeouts accumulate to indicate systemic failure
- `Retry Strategy` — retries after timeout; combine carefully (retry × timeout = max wait)
- `Fallback Strategy` — handles `TimeoutException` with degraded responses
- `Resilience4j` — provides `@TimeLimiter` for async timeout enforcement

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ CONNECT      │ TCP connection establishment timeout      │
│ TIMEOUT      │ Typical: 500ms – 1s                       │
├──────────────┼───────────────────────────────────────────┤
│ READ         │ Time to receive complete response         │
│ TIMEOUT      │ Typical: p99_latency × 1.5               │
├──────────────┼───────────────────────────────────────────┤
│ ALWAYS SET   │ RestTemplate, WebClient, Feign, gRPC stub │
│              │ Default = NO timeout = cascade failure    │
├──────────────┼───────────────────────────────────────────┤
│ BUDGET       │ API Gateway total budget ÷ hops           │
│ PROPAGATION  │ gRPC: Deadline.after() / REST: header     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A service has an SLA of p99 < 500ms. However, every hour, a batch job runs on the shared database, causing p99 to spike to 2,000ms for 30 seconds. During this window, services calling the database-dependent endpoint time out. Describe three approaches to handle this: (a) adjust timeout to accommodate the spike; (b) add a circuit breaker that detects the spike and stops calls; (c) redesign the data access (caching, read replica) to eliminate the spike. What are the trade-offs of each approach? When is approach (c) the only acceptable solution?

**Q2.** gRPC's `Deadline` propagates through the call chain: if a client sets a 5-second deadline and the request reaches Service B after 3 seconds (2 seconds remaining), Service B's gRPC call to Service C automatically uses the remaining 2 seconds as its deadline. HTTP REST does not have this built-in. Design an HTTP middleware that propagates a deadline: (a) what header should be used (`X-Request-Deadline` as Unix timestamp or `X-Request-Timeout-Ms` as remaining milliseconds)? (b) how does the middleware intercept outgoing calls and set the timeout based on remaining budget? (c) what happens when the service receives the header but the remaining budget is 0ms (already expired)?
