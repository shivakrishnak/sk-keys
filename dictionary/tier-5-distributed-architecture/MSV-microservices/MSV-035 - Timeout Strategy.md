---
layout: default
title: "Timeout Strategy"
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 35
permalink: /microservices/timeout-strategy/
id: MSV-035
category: Microservices
difficulty: ★★☆
depends_on: Inter-Service Communication, Synchronous vs Async Communication, HTTP & APIs
used_by: Circuit Breaker (Microservices), Retry Strategy, Bulkhead Pattern
related: Rate Limiting (Microservices), Fallback Strategy, Resilience4j
tags:
  - microservices
  - reliability
  - networking
  - intermediate
  - pattern
---

# MSV-035 - Timeout Strategy

⚡ TL;DR - A timeout is a hard deadline on how long a service waits for a response, so one slow dependency cannot freeze your entire call chain.

| #650            | Category: Microservices                                                      | Difficulty: ★★☆ |
| :-------------- | :--------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Inter-Service Communication, Synchronous vs Async Communication, HTTP & APIs |                 |
| **Used by:**    | Circuit Breaker (Microservices), Retry Strategy, Bulkhead Pattern            |                 |
| **Related:**    | Rate Limiting (Microservices), Fallback Strategy, Resilience4j               |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Your checkout service calls a payment gateway synchronously. The gateway is healthy 99.9% of the time, but today their datacenter is experiencing slowness - responses take 30 seconds instead of 200ms. Your checkout service threads sit there waiting. Each thread holds a database connection, a socket, and heap memory. With 1,000 concurrent users, 1,000 threads are stuck waiting for payment responses. Within minutes, your thread pool is exhausted. New requests to checkout queue up and then timeout at the load balancer. The payment issue is isolated - but it took down your entire store.

**THE BREAKING POINT:**
No thread can help new users while it's waiting indefinitely. Latency in a dependency became a complete availability failure in your service. This is called a _latency amplification cascade_ - slow downstream converts to dead upstream.

**THE INVENTION MOMENT:**
This is exactly why timeout strategy was created - to give every outgoing call a deadline so that a single slow dependency cannot hold hostage all threads in your service.

---

### 📘 Textbook Definition

A **timeout strategy** is a resilience pattern that places an upper bound on how long a service waits for a response from an external dependency (HTTP call, database query, message broker). When the deadline expires, the call is abandoned, an error is surfaced immediately, and the thread is freed to serve other requests. Timeouts are configured at connection establishment (`connect timeout`) and at data receipt (`read timeout`) and must be tuned to be shorter than the caller's own SLA.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Set a maximum wait time for every outgoing call so slow dependencies cannot block your threads forever.

**One analogy:**

> When you call a plumber and they put you on hold, you don't wait forever - you hang up after 5 minutes and call someone else. Timeouts are the "hang up after 5 minutes" rule for every network call your service makes.

**One insight:**
Timeouts don't prevent failure - they _control_ failure. Instead of a slow failure that steals resources indefinitely, you get a fast failure that lets you recover, retry, or fall back immediately.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Threads are finite; any thread waiting on I/O is unavailable for other work.
2. A remote call can take arbitrarily long due to network conditions, upstream bugs, or GC pauses.
3. Your SLA commitment requires you to respond within a fixed time - regardless of what dependencies do.

**DERIVED DESIGN:**
If threads are finite and calls can take infinite time, you must decouple "call made" from "thread held indefinitely." The mechanism: start a timer when the call is made; if the response arrives before the timer fires, use it; if the timer fires first, cancel the call and free the thread.

Two timeout types matter:

- **Connect timeout**: How long to wait for TCP handshake/TLS to complete. Usually 1–3 seconds. A timeout here indicates network partition or dead host.
- **Read timeout**: How long to wait for data after a connection is established. Usually 2–30 seconds depending on operation. A timeout here indicates a live but slow dependency.

**Timeout budget** is the key advanced concept: in a call chain A→B→C, if A's SLA is 500ms, B must timeout to C in less than 500ms minus B's own overhead. Each hop must shrink the remaining deadline. This is implemented via _deadline propagation_ (passing remaining budget in request headers).

**THE TRADE-OFFS:**
**Gain:** Thread safety under slow dependencies; predictable response times; enables circuit breaker to detect failures.
**Cost:** Correctly-timed responses that arrive just after timeout are wasted; choosing the right timeout value requires measuring P99 latency of dependencies; too-short timeouts cause false failures; too-long timeouts allow thread exhaustion.

---

### 🧪 Thought Experiment

**SETUP:**
Service A has 100 threads and calls Service B for every request. Service B normally responds in 50ms. No timeouts are configured. Service B experiences a GC pause and stops responding for 60 seconds.

**WHAT HAPPENS WITHOUT TIMEOUT:**
At 60ms into the pause, all 100 threads are waiting on B. Thread 101 arrives - rejected (thread pool full). Service A is now completely unavailable even though its own code is healthy. 60 seconds later B recovers, all threads unblock simultaneously, flooding B with retries.

**WHAT HAPPENS WITH TIMEOUT (500ms):**
Requests to B begin failing at 500ms with a timeout error. Service A catches the error, returns a cached result or error response immediately, and frees the thread. The thread pool never exhausts. When B recovers, A naturally starts receiving successful responses again.

**THE INSIGHT:**
A timeout converts an availability dependency into a latency dependency. With a timeout, B being slow hurts response quality (you get fallback/error) but not availability (threads keep flowing).

---

### 🧠 Mental Model / Analogy

> In cooking, you set a kitchen timer when something goes in the oven. When the timer rings, you pull it out - even if it looks like it needs more time - because leaving it in until "done" risks burning everything else on the stove.

- "Kitchen timer" → timeout duration configuration
- "Pulling it out at the bell" → aborting the in-flight HTTP/DB call
- "Everything else on the stove" → other concurrent requests needing threads
- "Burned dinner" → thread pool exhaustion / cascading failure
- "How long to set the timer" → P99 response time of the dependency × safety margin

Where this analogy breaks down: in software, you can't always "check on" progress mid-cook - some timeout implementations can only cancel at the socket level, not interrupt mid-execution in the downstream service.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
A timeout is a stopwatch. You start it when you make a call; if the call doesn't finish before the stopwatch runs out, you stop waiting and move on. It's how you prevent one slow thing from ruining everything else.

**Level 2 - How to use it (junior developer):**
Configure connect and read timeouts on every HTTP client, database driver, and message client your service uses. A common starting point: 1s connect timeout, 5s read timeout. Always configure both - a missing read timeout means you can connect but then wait forever for data. Return a meaningful error or fallback when a timeout fires.

**Level 3 - How it works (mid-level engineer):**
HTTP clients like `OkHttp` or `Feign` set timeouts at the socket level - the OS fires a `SocketTimeoutException` when the deadline passes. For async clients, a scheduled executor fires a cancel after the deadline. At the service mesh level (Envoy/Istio), timeouts are configured in routing rules and enforced at the proxy - the application never even receives the slow response. Deadline propagation: include `X-Request-Timeout-Ms` (or gRPC deadline) in outgoing headers so each hop knows the remaining budget.

**Level 4 - Why it was designed this way (senior/staff):**
The fundamental tension: too short → false positives (healthy-but-busy service killed); too long → threads held too long under real failures. The solution is statistical: set timeout at P99.9 of healthy response latency. This means 0.1% of legitimate calls will be killed, but 99.9% of failure-mode calls are caught quickly. Teams often discover that their P99.9 is 10× their P50 - revealing hidden latency spikes that _should_ be investigated, not accommodated by longer timeouts.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────────────────┐
│              Timeout Strategy - Flow                    │
└─────────────────────────────────────────────────────────┘

Service A                        Service B
    │                                │
    │  Connect (1s timeout starts)   │
    │───────────────────────────────►│
    │◄───────────────────────────────│  TCP SYN-ACK
    │  connected (50ms ✓)            │
    │                                │
    │  GET /data (5s timeout starts) │
    │───────────────────────────────►│
    │                                │  ← GC Pause (60s)
    │                                │
    ├── 5s timeout fires ────────────┤
    │
    │  SocketTimeoutException raised
    │  Thread freed immediately
    │  Fallback or error returned to caller
```

**Timeout configuration in Spring Boot / Feign:**

```yaml
feign:
  client:
    config:
      default:
        connectTimeout: 1000 # 1 second
        readTimeout: 5000 # 5 seconds
```

**Deadline propagation header pattern:**

```
Request enters A: X-Request-Deadline: <now + 500ms>
A calls B: X-Request-Deadline: <same value>
B calls C: X-Request-Deadline: <same value>
C checks: if now > deadline → return error immediately
```

**Happy path:** All calls complete within timeout; no timeout fires; normal responses propagate back.
**Error path:** Timeout fires → thread freed → `TimeoutException` caught → fallback executed → caller receives 503 or cached response.

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
[User Request] → [Service A (500ms SLA)]
  → [Call to B, timeout=300ms ← YOU ARE HERE]
  → [B responds in 50ms]
  → [A responds to user in 80ms total]
```

**FAILURE PATH:**

```
[B slow] → [Timeout fires at 300ms]
  → [A catches TimeoutException]
  → [A returns cached/fallback response or 503]
  → [User gets fast error, not 60s hang]
  → [Circuit breaker records failure]
```

**WHAT CHANGES AT SCALE:**
At 10k RPS, a 1% timeout rate means 100 timeout errors per second - enough to trigger circuit breaker tripping. At 100k RPS, even sub-millisecond timeout overhead multiplied across calls matters; proxied timeouts (service mesh) add <0.5ms overhead vs JVM-level timeouts which involve scheduled executor overhead. At massive scale, teams use adaptive timeouts - dynamically shrinking based on observed P99 latency.

---

### 💻 Code Example

**Example 1 - Wrong: no timeout on HTTP client:**

```java
// Default OkHttp has no read timeout!
OkHttpClient client = new OkHttpClient();
Response response = client.newCall(request).execute();
// This can hang forever
```

**Example 2 - Right: explicit timeouts:**

```java
OkHttpClient client = new OkHttpClient.Builder()
  .connectTimeout(1, TimeUnit.SECONDS)
  .readTimeout(5, TimeUnit.SECONDS)
  .writeTimeout(5, TimeUnit.SECONDS)
  .build();

try {
  Response response = client.newCall(request).execute();
  return parseResponse(response);
} catch (SocketTimeoutException e) {
  log.warn("Timeout calling payment service: {}",
           e.getMessage());
  return PaymentResult.timedOut();
}
```

**Example 3 - Production: Resilience4j with timeout + fallback:**

```java
TimeLimiterConfig config = TimeLimiterConfig.custom()
  .timeoutDuration(Duration.ofMillis(500))
  .cancelRunningFuture(true)
  .build();

TimeLimiter limiter = TimeLimiter.of("payment", config);

CompletableFuture<PaymentResult> future =
  CompletableFuture.supplyAsync(
    () -> paymentClient.charge(request));

return Try.of(limiter.decorateFutureSupplier(
        () -> future))
  .recover(TimeoutException.class,
           e -> PaymentResult.useCachedApproval())
  .get();
```

---

### ⚖️ Comparison Table

| Strategy                 | Controls                     | Frees Thread | Best For                       |
| ------------------------ | ---------------------------- | ------------ | ------------------------------ |
| **Connect Timeout**      | TCP/TLS establishment        | Yes          | Dead hosts, network partitions |
| **Read Timeout**         | Response data wait           | Yes          | Slow upstream processing       |
| **Request Timeout**      | Full request lifecycle       | Yes          | End-to-end SLA enforcement     |
| **Deadline Propagation** | Remaining budget across hops | Yes          | Distributed call chains        |
| No timeout               | Nothing                      | No           | Never - always set timeouts    |

**How to choose:** Always set both connect (1–3s) and read timeout (based on dependency P99 × 2). Add deadline propagation once you have call chains deeper than 2 hops.

---

### ⚠️ Common Misconceptions

| Misconception                                    | Reality                                                                                  |
| ------------------------------------------------ | ---------------------------------------------------------------------------------------- |
| Default HTTP clients have sensible timeouts      | Most default clients have NO timeout - you must configure explicitly                     |
| One timeout value works for all operations       | Read vs write vs connect need separate values; batch operations need longer than queries |
| Timeout means the upstream request was cancelled | The upstream may continue executing - timeout only frees the caller's thread             |
| Longer timeouts are "safer"                      | Longer timeouts allow more threads to accumulate, worsening cascades                     |
| Timeouts and retries are independent choices     | Timeout × retries × concurrency = maximum wait time - they must be designed together     |

---

### 🚨 Failure Modes & Diagnosis

**Thread Pool Exhaustion Despite Timeouts**

**Symptom:** Service becomes unresponsive even with timeouts configured; thread pool shows 100% utilization.

**Root Cause:** Timeout is set at 30s; at 500 RPS, 30s × 500 = 15,000 concurrent "in-flight" requests - exceeding thread pool size.

**Diagnostic Command:**

```bash
# Check thread pool utilization
curl -s http://localhost:8080/actuator/metrics/\
  executor.active | jq '.measurements[0].value'
# Or for JVM threads:
jcmd <pid> Thread.print | grep -c "WAITING"
```

**Fix:** Timeout must be ≤ (thread_pool_size / max_RPS). Reduce timeout or increase thread pool.

**Prevention:** Calculate max concurrency at design time: `max_concurrent = timeout_ms / 1000 × expected_RPS`.

---

**Upstream Side Effects After Timeout**

**Symptom:** Service A times out on a payment call; user sees error; but payment was actually charged (duplicate charges on retry).

**Root Cause:** A timed out but B had already processed the request before responding. Retry causes duplicate execution.

**Diagnostic Command:**

```bash
# Check idempotency key usage in payment logs
grep "idempotency_key" /var/log/payment-service/*.log \
  | grep -c "duplicate"
```

**Fix:** Always use idempotency keys on mutating calls so retries are safe.

**Prevention:** Design all timeout-able operations to be idempotent before adding retry logic.

---

**Missing Read Timeout (Connect Only)**

**Symptom:** Service connects quickly but hangs on data receipt; connect timeout doesn't fire.

**Root Cause:** Only connect timeout was configured, not read timeout.

**Diagnostic Command:**

```bash
# Check socket states - many ESTABLISHED is normal,
# but many with same remote IP + long duration = hang
ss -tn | grep ESTAB | awk '{print $5}' | sort | uniq -c
```

**Fix:** Always configure both connect and read timeout independently.

**Prevention:** Code review checklist: every HTTP/DB/cache client must have both timeout values explicitly set.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Inter-Service Communication` - how services call each other synchronously
- `HTTP & APIs` - TCP connect/read semantics that timeout interacts with
- `Synchronous vs Async Communication` - timeouts primarily affect sync calls

**Builds On This (learn these next):**

- `Circuit Breaker (Microservices)` - uses timeout failures to trip and stop calling failing services
- `Retry Strategy` - what you do after a timeout fires
- `Bulkhead Pattern` - limits concurrent in-flight requests to bound timeout exposure

**Alternatives / Comparisons:**

- `Rate Limiting (Microservices)` - limits request count, not duration
- `Fallback Strategy` - defines what to return when timeout fires
- `Resilience4j` - Java library implementing timeout (TimeLimiter) and other patterns

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Deadline on how long any outgoing call    │
│              │ is allowed to wait for a response         │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Slow dependency holds threads indefinitely│
│ SOLVES       │ causing cascading unavailability          │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Timeout converts infinite wait (resource  │
│              │ hold) into finite fast failure (release)  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Every synchronous outgoing call - no      │
│              │ exceptions, ever                          │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Never avoid - set timeouts everywhere;    │
│              │ only the value changes per operation      │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Thread safety under slow deps vs          │
│              │ false timeouts on legitimately slow ops   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The kitchen timer that stops your        │
│              │  service burning down"                    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Circuit Breaker → Retry Strategy →        │
│              │ Bulkhead Pattern                          │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Service A calls B (timeout 200ms), which calls C (timeout 300ms). A user request arrives at A. C is slow - taking 250ms. Trace the exact sequence: does A's timeout fire? Does B's? What does the user see? Now reconfigure B's timeout to 150ms and re-trace. What changes and why is this the correct approach for deadline propagation?

**Q2.** You set a 500ms read timeout on all calls to your inventory service. After deploying, you discover 2% of requests are timing out even though inventory looks healthy. Your P50 latency is 40ms. Describe step-by-step how you would diagnose whether this is a genuine inventory issue, a timeout configured too low, or a specific caller pattern - and what you would change.
