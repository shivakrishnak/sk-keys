---
id: DST-008
title: "Timeout"
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★☆
depends_on: DST-026
related: DST-027, DST-028, DST-026, DST-009
tags:
  - distributed
  - reliability
  - pattern
  - foundational
  - deep-dive
status: complete
version: 2
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Dictionary"
nav_order: 17
permalink: /distributed-systems/timeout/
---

# DST-010 - Timeout

⚡ TL;DR - A timeout bounds the maximum time a caller will wait for a response from a dependency — without it, a slow or crashed remote service holds threads indefinitely, causing resource exhaustion and cascade failure across the entire system.

| Metadata        |                                    |     |
| :-------------- | :--------------------------------- | :-- |
| **Depends on:** | DST-026                            |     |
| **Related:**    | DST-027, DST-028, DST-026, DST-009 |     |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A service calls a database query. The database is overloaded. The query hangs. The calling thread waits. Forever. No timeout = indefinite wait. Each incoming request occupies a thread. After 200 requests: 200 threads are waiting for a hung database. New requests cannot get threads. The service appears dead — completely unavailable — because of one slow database query. The caller has surrendered all control to the dependency.

**THE BREAKING POINT:**
Michael Nygard documented dozens of production incidents in _Release It!_ (2007) where missing timeouts caused total service outages. The pattern: a single slow third-party integration (credit card processor, database, external API) caused an entire service to stop responding. Engineers who added timeouts found that partial degradation (some operations fail) was infinitely better than total failure (all operations fail). Without a timeout, a service is as reliable as its slowest dependency.

**THE INVENTION MOMENT:**
TCP sockets have had timeouts since the 1970s (connect timeout, receive timeout). But these are OS-level defaults (often minutes). Application developers need BUSINESS-LEVEL timeouts: "I will wait at most 2 seconds for this database query, because my user expects a response in < 3 seconds." Application-level timeouts separate business requirements (SLO-based wait time) from OS defaults (connection management).

**EVOLUTION:**
1970s: TCP socket timeout (OS-level, minutes). 1990s: HTTP timeout (per-request, seconds). 2007: Nygard's _Release It!_ — timeout as a stability pattern. 2012: Hystrix — per-command execution timeout. 2016: gRPC deadline propagation (distributed timeout that flows through all services). 2018: Resilience4j — `TimeLimiter` component. Today: timeout is the most fundamental resilience primitive — all other patterns (circuit breaker, retry) depend on timeouts.

---

### 📘 Textbook Definition

**Timeout** in distributed systems is a configurable maximum wait time before a blocked operation is abandoned. Types: (1) **Connection timeout:** maximum time to establish a connection. (2) **Read timeout (socket timeout):** maximum time between receiving bytes once connected. (3) **Request timeout:** maximum total time for a request (connect + read + processing). (4) **Deadline:** an absolute timestamp by which an operation must complete (propagates through service calls). **Deadline propagation (gRPC):** each service receives the original deadline and reduces it for downstream calls. If deadline passed before downstream call: short-circuit with `DEADLINE_EXCEEDED`. **Timeout vs deadline:** timeout is a duration (relative to when call starts). Deadline is a timestamp (absolute). gRPC uses deadlines; HTTP typically uses timeouts.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Set a maximum wait time — if the dependency doesn't respond by then, give up and handle the failure.

> A timeout is like a cooking timer. You put the roast in the oven (make a remote call). You set the timer for 2 hours (timeout). When the timer rings: you check — if the roast is done, great. If not: you take it out anyway (return failure). You don't wait until the oven consumes itself.

**One insight:** The timeout value is a SERVICE LEVEL AGREEMENT commitment. If your SLO is 3-second response time: your internal timeout budget for all dependencies combined must be < 3 seconds. Each nested service call consumes some of that budget.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **Every blocking call must have a timeout.** No exception. An untimed call is a thread held hostage to an external dependency.
2. **Timeout < caller's own timeout.** If Service A calls B, and A has a 5-second timeout: B's timeout must be < 5 seconds (e.g., 2 seconds). Otherwise: A can never detect B's failure before A itself times out. Nested timeouts must shrink.
3. **Timeout is not just for failures.** A slow-but-successful call that consumes 29 of your 30-second budget is as dangerous as a failed call. Timeouts protect against slow success too.
4. **Timeout must release resources.** Canceling a timed-out call must release the thread, connection, and memory associated with it. Many HTTP clients timeout the RESPONSE but not the underlying connection — socket remains open, connection pool exhausted.

**DERIVED DESIGN:**

```
Connection timeout: 1-3s (TCP handshake is fast)
Read timeout: depends on SLO - (connect + overhead)
  For SLO=3s: read_timeout = 3s - 0.5s overhead = 2.5s
Total request timeout: SLO - (upstream latency budget)
  For SLO=3s with 3 serial calls: each gets ~0.8s
```

**THE TRADE-OFFS:**
**Gain:** Thread/resource release on dependency failure. Bounded latency (P99 bounded by timeout, not dependency behavior). Enables circuit breaker (needs failures to count).
**Cost:** False failures (slow-but-correct calls abandoned). User experiences error where the operation might have succeeded. Configuration complexity (every call needs a tuned timeout).

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** The correct timeout value for each call is unknowable without empirical measurement (what IS the 99th percentile latency of this call in production?). Over-tight timeout = false failures. Over-loose timeout = thread holding.
**Accidental:** gRPC deadline propagation vs per-hop timeout. Deadline (absolute timestamp) is strictly better — it prevents a slow first service from stealing all the time budget before downstream calls can start.

---

### 🧪 Thought Experiment

**SETUP:** Service A → Service B → Service C. Total timeout budget: 3 seconds. Service C has a 30-second outage.

**WITHOUT TIMEOUTS:**

- A calls B. B calls C. C hangs for 30 seconds.
- B's thread waits 30s. A's thread waits 30s.
- After 200 concurrent requests: 200 A-threads, 200 B-threads all waiting.
- Both A and B are dead for 30 seconds per hung request.

**WITH PER-HOP TIMEOUTS (A=3s, B=2s):**

- A calls B. B calls C. After 2 seconds: B times out on C.
- B returns error to A after 2 seconds.
- A gets error after 2 seconds (< 3 second timeout). Thread released.
- User gets error: "C unavailable." A and B remain responsive for other requests.

**WITH DEADLINE PROPAGATION (gRPC-style):**

- A creates deadline: T + 3000ms.
- A calls B: passes deadline T + 3000ms.
- B calls C: passes remaining deadline.
- If T has elapsed (even 1ms remaining): B short-circuits before calling C.
- Prevents B from making a call to C when A has already timed out.

**THE INSIGHT:** Without timeout: one slow dependency makes ALL callers wait indefinitely. With timeout: each caller waits at most T_timeout, then releases resources. Service remains partially available.

---

### 🧠 Mental Model / Analogy

> Timeout is like a parking meter. You want to park for some purpose (make a remote call). You have a meter that limits your time (timeout value). When the meter expires: you must move or get ticketed (operation fails). The parking lot doesn't fill up with abandoned cars waiting forever (threads aren't held indefinitely). Other cars can use the spot (other requests can get threads).

**Mapping:**

- **Parking meter** → timeout configuration
- **Parking time** → allowed wait time for remote call
- **Meter expiry** → timeout event (TimeoutException)
- **Moving the car** → releasing thread/connection
- **Other cars using the spot** → other requests getting the freed thread

Where this analogy breaks down: a parking meter charges money for the slot. A timeout doesn't charge for the time SPENT waiting — it only bounds the maximum. The "cost" of timeout is the false failure (abandoned operation that might have succeeded).

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
A timeout says: "I'll wait for you — but only for N seconds. After that, I'm moving on." Like a restaurant telling customers: "Your table will be ready in 20 minutes. If you can't wait that long, we understand." Without timeout: customers wait forever. With timeout: customers leave after 20 minutes, freeing the waiting area for others.

**Level 2 - How to use it (junior developer):**
Java HttpClient: `HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(3)).build()`. Then per-request: `.timeout(Duration.ofSeconds(5))`. Spring RestTemplate: `SimpleClientHttpRequestFactory factory = new SimpleClientHttpRequestFactory(); factory.setConnectTimeout(3000); factory.setReadTimeout(5000);`. gRPC stub: `stub.withDeadlineAfter(3, TimeUnit.SECONDS)`.

**Level 3 - How it works (mid-level engineer):**
Java's `SocketTimeoutException` is thrown by the OS when `SO_TIMEOUT` on the socket fires. This happens when no bytes are received for `readTimeout` ms after the first byte arrives. The OS signals the socket; the JVM throws the exception; the calling thread is unblocked. Critical: `SocketTimeoutException` does NOT close the socket. You must explicitly close `HttpURLConnection` or the underlying socket to release the connection back to the pool. Without explicit close: timed-out connections leak from the connection pool — pool exhausted, new requests block waiting for connections, not on the original dependency.

**Level 4 - Why it was designed this way (senior/staff):**
gRPC's deadline model (timestamp, not duration) is strictly superior to timeout (duration) for multi-service chains. Consider: Service A (timeout=3s) → Service B (timeout=2s) → Service C (timeout=1s). A calls B at T=0. B takes 1.5 seconds to process before calling C. B calls C: timeout=1s, but A has already used 1.5s of its 3s budget. A will timeout in 1.5 seconds. But B calls C with timeout=1s. C may succeed in 0.9 seconds (valid for B). But A already timed out at T=3. B's response to A is abandoned. C did work that nobody wanted. With gRPC deadline: A creates deadline=T+3s. Passes to B. B passes remaining deadline (1.5s remaining) to C. If deadline has already passed: B doesn't call C (short-circuits). C never does unnecessary work. Deadline propagation eliminates orphaned work.

**Expert Thinking Cues:**

- "Service has correct timeout but P99 latency = exactly timeout value" → Timeout is too aggressive (many legitimate calls are being cut off) OR the dependency's P99 is legitimately near the timeout. Check: histogram of call durations — are there many calls clustering at exactly T=timeout? Those are timeouts, not natural completions. Fix: measure P99 latency of the dependency in healthy state, set timeout = P99 × 1.5 + connection overhead.
- "Timeout doesn't help — threads are still stuck" → Check: is the timeout releasing the HTTP connection back to the pool? HttpClient libraries may throw `TimeoutException` but not close the underlying socket. Check connection pool metrics: `available connections` vs `max connections`. If available always near 0: connection leak on timeout. Fix: ensure `response.close()` is called in a `finally` block even on timeout.
- "Different timeout for same call depending on caller's SLO" → This is correct — timeouts should be context-dependent. Use gRPC deadline propagation: the original caller sets the overall deadline; each service in the chain uses `Math.min(deadline_remaining, local_timeout)` for downstream calls. This ensures all downstream calls respect the original SLO without each service knowing about the overall deadline independently.

---

### ⚙️ How It Works (Mechanism)

**Timeout types and their scope:**

```
HTTP call lifecycle:
  ├── DNS resolution: (no standard timeout, ~100ms)
  ├── TCP connect: connect_timeout (e.g., 1-3s)
  │   [SO_CONNECT_TIMEOUT on socket]
  ├── TLS handshake: (included in connect timeout usually)
  ├── Request write: (rarely timed explicitly)
  └── Response read: read_timeout (e.g., 2-5s)
      [SO_TIMEOUT on socket, per inter-byte gap]

Total request timeout (OkHttp, Apache HttpClient):
  [connect + read + write all within one budget]

gRPC deadline propagation:
  Client: context deadline = now() + 3s
  Service A receives: X-GRPC-DEADLINE: <timestamp>
  Service A calls B:  passes min(remaining, local_budget)
  Service B calls C:  passes min(remaining, local_budget)
  If deadline_remaining < 0: short-circuit, return
    Status.DEADLINE_EXCEEDED without calling downstream
```

---

### 🔄 The Complete Picture - End-to-End Flow

**TIMEOUT IN SERVICE CHAIN:**

```
User  ServiceA(3s)  ServiceB(2s)  ServiceC
  │       │              │             │
  │─req──▶│              │             │
  │       │─call(B)─────▶│             │
  │       │              │─call(C)────▶│
  │       │              │             │ [C slow...]
  │       │              │ [2s elapsed]│
  │       │              │ TimeoutException
  │       │              │◀────────────┘ (B releases thread)
  │       │◀─503─────────│
  │       │ [A still has │ ← YOU ARE HERE
  │       │  1s remaining]
  │       │ [records failure for circuit breaker]
  │◀─error│ (total: 2s, within A's 3s budget)
```

**WHAT CHANGES AT SCALE:**
At scale: timeout values that are correct under normal load may be too tight under high load. Under 10× traffic: database query P99 latency increases. Previously correct 1s read_timeout → now 20% of requests timeout spuriously. Solution: monitor timeout rate as a metric. Alert when timeout_rate > 1%. Use P99 latency of dependency × 2 as timeout value, not a fixed number. Recompute quarterly.

**CONCURRENCY & DISTRIBUTED IMPLICATIONS:**
Timeout in the caller does not cancel work in the callee. Service B times out waiting for Service C — but C is still processing the request. C will complete and write a result that nobody reads. For expensive operations (database writes, external API calls): timed-out requests create orphaned work. Solution: use cancellation tokens (gRPC context cancellation propagates to the server; server checks for cancellation and aborts). Without explicit cancellation: timeout reduces latency for callers but doesn't reduce load on callees.

---

### 💻 Code Example

**BAD - No timeout (thread held indefinitely):**

```java
// BAD: no timeout anywhere
public Inventory getInventory(String id) {
    // If inventory service hangs: this thread hangs forever
    // 200 concurrent requests = 200 hung threads = dead service
    HttpURLConnection conn =
        (HttpURLConnection) inventoryUrl.openConnection();
    // No connect timeout, no read timeout
    return parseResponse(conn.getInputStream());
}
```

**GOOD - Explicit connect + read timeout + resource release:**

```java
// GOOD: timeout at every level
public Inventory getInventory(String id) {
    HttpURLConnection conn = null;
    try {
        conn = (HttpURLConnection) inventoryUrl.openConnection();
        conn.setConnectTimeout(1000);  // 1s to connect
        conn.setReadTimeout(2000);     // 2s to receive response
        conn.connect();
        return parseResponse(conn.getInputStream());
    } catch (SocketTimeoutException e) {
        // Timeout: dependency slow or unreliable
        // Log and let caller handle (circuit breaker, fallback)
        throw new DependencyTimeoutException(
            "inventory", id, e);
    } finally {
        if (conn != null) conn.disconnect(); // MUST release
    }
}

// OkHttp (better: single total timeout):
OkHttpClient client = new OkHttpClient.Builder()
    .connectTimeout(1, TimeUnit.SECONDS)
    .readTimeout(2, TimeUnit.SECONDS)
    .callTimeout(3, TimeUnit.SECONDS) // total budget
    .build();
```

**gRPC deadline propagation:**

```java
// Service A: set deadline for the whole operation
public void handleRequest(Context ctx) {
    // Propagate deadline to downstream:
    Context withDeadline = ctx.withDeadlineAfter(
        3, TimeUnit.SECONDS, ScheduledExecutorService);
    // gRPC stub with deadline:
    InventoryGrpc.InventoryBlockingStub stub =
        inventoryStub.withDeadline(
            Deadline.after(3, TimeUnit.SECONDS));
    try {
        return stub.getInventory(request);
    } catch (StatusRuntimeException e) {
        if (e.getStatus().getCode()
            == Status.Code.DEADLINE_EXCEEDED) {
            throw new DependencyTimeoutException(e);
        }
        throw e;
    }
}
```

---

### ⚖️ Comparison Table

| Timeout type                | Scope                    | Config location      | gRPC equivalent    |
| :-------------------------- | :----------------------- | :------------------- | :----------------- |
| Connect timeout             | TCP handshake only       | Per client           | Deadline (start)   |
| Read timeout                | Between bytes received   | Per client           | Deadline (overall) |
| Call timeout (OkHttp)       | Total: connect + read    | Per client           | Deadline           |
| Execution timeout (Hystrix) | Call runs in thread pool | Per command          | Deadline           |
| Deadline (gRPC)             | Absolute timestamp       | Per-call, propagated | Native             |

---

### ⚠️ Common Misconceptions

| Misconception                                                | Reality                                                                                                                                                                                                                                                                                                                                                            |
| :----------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "A short timeout means better performance"                   | A timeout that's too short causes false failures (healthy calls abandoned). Optimal timeout = P99 latency of the dependency in healthy state × 1.5. Too short: false failures and unnecessary retries. Too long: slow failure detection and thread holding.                                                                                                        |
| "Timeout cleans up the downstream work"                      | Timeout unblocks the CALLER — the downstream service continues processing the request. If the downstream call eventually completes: the result is discarded. For database writes and external API calls: timed-out requests cause orphaned work (DB rows written, external charges processed). Use gRPC context cancellation to propagate cancellation downstream. |
| "Connection timeout and read timeout serve the same purpose" | Connection timeout: for TCP handshake (server may be unreachable, firewall drops, network partition). Read timeout: for slow response after connected (server connected but processing slowly). Both are needed. A 1s connection timeout + no read timeout: still hangs indefinitely once connected.                                                               |
| "Timeout prevents resource exhaustion"                       | Timeout releases the CALLING THREAD. But many HTTP clients don't close the underlying socket on timeout. The socket remains in the connection pool as a "lent out" connection that will never return. Connection pool exhaustion still occurs. Must explicitly close connections on timeout.                                                                       |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Connection Pool Exhaustion Despite Timeout**

**Symptom:** Service has 3-second read timeout. Database becomes slow. After some time: despite timeouts firing, service still hangs. Connection pool shows `available=0, max=100`. New requests queue for pool connections, not for database responses.
**Root Cause:** Read timeout fires, `SocketTimeoutException` thrown, but the underlying socket is not closed. HTTP connection pool still counts the socket as "lent out." The timed-out socket eventually returns to the pool after the OS detects the connection is dead (TCP keepalive, minutes). But by then: 100 timed-out sockets have depleted the pool.
**Diagnostic:**

```bash
# Check HikariCP or HTTP connection pool status:
# For HikariCP (DB pool):
curl http://service/actuator/metrics/hikaricp.connections.active
# If active ≈ max AND request_latency is high: pool exhausted

# For OkHttp connection pool:
curl http://service/actuator/metrics/okhttp.connections.active
# Count active vs max

# Check OS-level socket state:
netstat -an | grep CLOSE_WAIT | wc -l
# High CLOSE_WAIT count: sockets not properly closed by app
```

**Fix:**
BAD: Catching `SocketTimeoutException` without closing the connection.
GOOD: Always close in `finally` block: `conn.disconnect()` for HttpURLConnection. For OkHttp: `response.close()` (closes body and connection). For Apache HttpClient: `EntityUtils.consume(response.getEntity())`.
**Prevention:** Use connection pool metrics as a health indicator. Alert when `active_connections / max_connections > 80%`. Code review: verify all HTTP connections are closed in finally blocks.

**Failure Mode 2: Timeout Too Tight — P99 Spikes**

**Symptom:** During peak traffic (Black Friday), 15% of calls to the product catalog service fail with timeout. The catalog service is healthy — it's just slower under load (P99 = 1.8s instead of normal P99 = 0.6s). Timeout configured: 1.5s. False timeouts.
**Root Cause:** Timeout value was set based on P99 latency in normal conditions (0.6s × 2 = 1.2s, rounded to 1.5s). Under load: P99 increases to 1.8s. Timeout now cuts off the slowest 20% of legitimate calls — causing failures that cascade through the system.
**Diagnostic:**

```bash
# Check histogram of call durations:
curl http://service/actuator/metrics/http.client.requests?\
  tag=outcome:TIMEOUT
# If timeout_count / total_count > 2%: timeout too tight

# Check dependency's P99 latency:
curl http://catalog-service/actuator/metrics/\
  http.server.requests?tag=outcome:SUCCESS
# P99 value: if > timeout_value: false timeouts occurring

# Correlate timeout rate with traffic volume:
grep "TimeoutException.*catalog" app.log | \
  awk '{print $1}' | cut -c1-13 | sort | uniq -c
# Rising count during peak: load-dependent false timeouts
```

**Fix:**
BAD: timeout = P99_normal (no headroom for load-induced latency increase).
GOOD: timeout = P99_peak × 1.5. For catalog: P99_peak = 1.8s → timeout = 2.7s. Also: add rate limiting (DST-009 bulkhead) to prevent catalog from being overloaded in the first place.
**Prevention:** Measure dependency P99 latency under LOAD TEST conditions, not just normal conditions. Set timeout based on P99 under peak load × 1.5.

**Failure Mode 3: Security - Slowloris Attack via No Timeout**

**Symptom:** Web server connections increase to max. New connections rejected. Server appears to serve no requests. No error logs — connections are open but sending data very slowly. CPU usage: minimal. Connection count: maxed.
**Root Cause:** Slowloris attack: attacker opens many connections to the server, sends HTTP headers very slowly (one byte every 30 seconds). Without read timeout: the server waits for complete headers indefinitely. Attacker can exhaust all available connections with just a few hundred attacking connections. No real DDoS needed — one laptop can take down a server without read timeout.
**Diagnostic:**

```bash
# Check connection counts by state:
netstat -an | grep ESTABLISHED | awk '{print $5}' | \
  cut -d: -f1 | sort | uniq -c | sort -rn | head -20
# Many connections from same IP(s): potential Slowloris

# Check bytes transferred per connection:
ss -i | grep -A 2 "ESTABLISHED"
# Many connections with tiny rcv_bytes + long duration:
# Slowloris pattern

# Check if Nginx has read timeout configured:
grep "client_header_timeout\|client_body_timeout" /etc/nginx/nginx.conf
# Default in older Nginx: 60s (too long for defense)
```

**Fix:**
BAD: `client_header_timeout 60s` (default) or no timeout at all.
GOOD: `client_header_timeout 10s; client_body_timeout 10s;` in Nginx. For application servers: set `requestTimeout` or equivalent. For Java NIO: non-blocking I/O with idle connection timeout.
**Prevention:** Always configure server-side read timeout (not just client-side). Nginx: `client_header_timeout 5s`. Apache: `RequestReadTimeout header=5-20,MinRate=500`. Rate limit connections per IP at the load balancer.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- DST-026 - Heartbeat (heartbeat and timeout both address failure detection — heartbeat is proactive, timeout is reactive)

**Builds On This (learn these next):**

- DST-027 - Circuit Breaker (circuit breaker aggregates timeout-based failures into state transitions)
- DST-028 - Retry with Backoff (retry triggers on timeout; timeout must be set before retry makes sense)
- DST-009 - Bulkhead (bulkhead limits concurrent calls, reduces timeout load)

**Alternatives / Comparisons:**

- DST-026 - Heartbeat (proactive liveness detection vs reactive timeout)
- DST-027 - Circuit Breaker (aggregates many timeouts into a circuit-level decision)

---

### 📌 Quick Reference Card

```
+------------------+--------------------------------+
| WHAT IT IS       | Maximum wait time for a        |
|                  | remote call before giving up   |
|                  | and releasing the thread       |
+------------------+--------------------------------+
| PROBLEM SOLVED   | Indefinite thread blocking:    |
|                  | one slow dependency holds all  |
|                  | threads, killing the service   |
+------------------+--------------------------------+
| KEY INSIGHT      | Timeout value = P99 latency    |
|                  | of dependency under peak load  |
|                  | × 1.5 (measured, not guessed)  |
+------------------+--------------------------------+
| USE WHEN         | Every blocking remote call —   |
|                  | HTTP, database, queue, 3rd     |
|                  | party API, file I/O            |
+------------------+--------------------------------+
| AVOID WHEN       | N/A: ALWAYS use timeouts on    |
|                  | remote calls. No exceptions.   |
+------------------+--------------------------------+
| TRADE-OFF        | False failures (tight timeout) |
|                  | vs thread holding (loose)      |
+------------------+--------------------------------+
| ONE-LINER        | Bound wait time or lose the    |
|                  | service to slow dependencies   |
+------------------+--------------------------------+
| NEXT EXPLORE     | DST-027 Circuit Breaker,       |
|                  | DST-028 Retry with Backoff     |
+------------------+--------------------------------+
```

**If you remember only 3 things:**

1. Every blocking remote call must have a timeout — no exceptions. An untimed call is a thread held hostage to an external dependency. One slow dependency without a timeout can kill your entire service.
2. Timeout value = P99 latency of the dependency under PEAK LOAD × 1.5. Not a guess, not a round number. Measure P99, calculate. Re-measure quarterly.
3. Timeout fires on the CALLER — the callee keeps running. Close the connection explicitly in the `finally` block or use gRPC context cancellation to propagate cancellation downstream and avoid orphaned work.

**Interview one-liner:**
"Timeout bounds the maximum time a caller waits for a remote response. Without it: a slow dependency blocks all threads → thread pool exhausted → service completely dead. With timeout: threads are released after T seconds → service remains available for other operations. Timeout configuration: connect timeout (TCP handshake, 1-3s) + read timeout (response wait, P99_peak × 1.5). gRPC deadline propagation is strictly better for multi-service chains — it propagates an absolute timestamp through all services, preventing downstream calls when the original deadline has already passed."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Any resource that can be held indefinitely will eventually exhaust. Bound every resource acquisition: time (timeout), quantity (bulkhead), rate (rate limiter). This principle applies universally: mutexes (lock timeout), database transactions (statement timeout), message consumers (visibility timeout), leases (TTL), and HTTP requests (read timeout). The cost of bounding: false failures (releasing a resource that would have completed successfully). The cost of NOT bounding: guaranteed eventual exhaustion. Always bound.

**Where else this pattern appears:**

- **Database transaction timeout (MySQL `wait_timeout`, Postgres `statement_timeout`):** A long-running transaction holds row-level locks. Without timeout: other transactions that need those rows block indefinitely. With `statement_timeout=5000ms` (Postgres): slow queries are killed after 5 seconds, releasing locks for other transactions. Same principle: bound resource holding time to prevent indefinite blocking.
- **Kubernetes pod grace period and liveness probe timeout:** Kubernetes sends SIGTERM to a pod (graceful shutdown). If the pod doesn't exit within `terminationGracePeriodSeconds` (default 30s): SIGKILL. The grace period is a timeout: "I'll wait this long for graceful shutdown, then force-terminate." Without this timeout: a stuck pod blocks the node and prevents new pods from starting.
- **AWS SQS visibility timeout:** When a consumer reads a message: it becomes invisible to other consumers for `visibility_timeout` seconds. If the consumer crashes without deleting the message: after timeout, the message becomes visible again (retried by another consumer). The visibility timeout is a "caller must complete before timeout or the operation is given to another caller" — exactly the timeout principle applied to message queue processing.

---

### 💡 The Surprising Truth

The most common timeout mistake is not setting one at all — but the second most common mistake is setting the timeout in the wrong place. Many engineers correctly set a `readTimeout` on their HTTP client but forget that `readTimeout` is the maximum time between receiving any two bytes — not the total time for the entire response. A response that streams one byte per second indefinitely will never trigger a 30-second `readTimeout` because bytes are arriving. The `callTimeout` (OkHttp) or `request timeout` (Apache HttpClient) is the only bound on total call duration. Without it: a slow server that delivers a large response one byte at a time can hold a connection for hours, regardless of `readTimeout`. This is exactly the Slowloris attack applied to HTTP response bodies (instead of headers). The surprising truth: you need BOTH a read timeout (between bytes) AND a total call timeout (end-to-end). One alone is insufficient.

---

### 🧠 Think About This Before We Continue

**Q1 (A - System Interaction):** Service A calls B calls C calls D. All have timeouts: A=10s, B=8s, C=5s, D=3s. Service D experiences a 6-second slowdown (returns in 6s instead of normal 1s). Trace through the timeout chain: what happens at each service, what error does the user receive, and at what total elapsed time?
_Hint:_ D=3s timeout. D hangs for 6s. After 3s: C's call to D times out (SocketTimeoutException in C). C returns error to B after ~3s. B's 8s timeout: received error in 3s (well within 8s). B returns error to A after ~3s. A's 10s timeout: received error in ~3s (well within 10s). User receives error after ~3s total elapsed time. The timeout chain CORRECTLY propagates failure. Now with gRPC deadline: A sets deadline=T+10s. If D's call starts at T+0.5s (0.5s overhead in A and B): D has 9.5s remaining. With local timeout 3s: D times out in 3s, returns error. Same result in this case. Where gRPC deadline helps: if A is slow and starts B's call at T+9s — deadline has only 1s remaining. With per-hop timeouts: B calls C with 8s timeout, C calls D with 5s timeout — totally ignoring that A already used 9s. Wasted work. With deadline: A calls B only if deadline remaining > min_useful_time, preventing wasted downstream work.

**Q2 (D - Root Cause):** A service has a 2-second timeout on all database calls. P99 latency of queries is 0.8s normally. During a slow database incident: queries take 1.5s (P99). The service shows 35% error rate. But the database team reports the database is "working fine" — all queries complete within 2 seconds. How do you reconcile this?
_Hint:_ Database team: queries complete in < 2s (1.5s P99 — correct, within timeout). Service shows 35% error rate. Possible explanations: (1) The timeout is set correctly for individual queries, but the SERVICE has multiple sequential database calls per request. If each request makes 3 serial DB calls × 1.5s = 4.5s total. Service's total request timeout (if any) may be 3s. The sum of queries exceeds the request timeout. (2) Connection pool is exhausted (not query timeout). At 1.5s per query (vs 0.8s normal), throughput drops: fewer queries per second complete, pool fills. New requests wait for pool connections → timeout waiting for connection (not executing the query). Pool `connectionTimeout` (separate from query timeout) fires. This shows the difference between query-level and connection-pool-level timeouts.

**Q3 (C - Design Trade-off):** An architecture proposal removes per-service timeouts and replaces them with a single gRPC deadline propagated from the edge. Each service simply uses `Math.min(deadline_remaining, local_config_max)` for downstream calls. What are the advantages of this approach vs independent per-service timeouts? What are the failure modes specific to the deadline approach?
_Hint:_ Advantages: (1) No wasted work — downstream calls short-circuit if deadline already passed. (2) Single SLO configuration at edge (users see one consistent timeout). (3) Prevents slow first service from consuming entire budget before downstream calls start. Failure modes specific to deadline: (1) Clock skew — if services have different system clocks, deadline comparison may be incorrect (treat deadline as expired when it isn't, or vice versa). NTP must be in sync across all services. (2) Deadline not propagated — if any service in the chain creates a NEW context without passing the deadline (e.g., new thread, async callback): deadline is lost. All services must be deadline-aware. (3) Tight deadline at edge → all downstream calls get very short remaining time → high false failure rate. With per-service timeouts: each service has its own "floor" (minimum wait time). With deadline: no floor — if edge deadline is 100ms remaining: D's call gets 100ms regardless of its normal 2s timeout. Hybrid: deadline propagation with a local minimum: `max(deadline_remaining, local_minimum_timeout)`.

