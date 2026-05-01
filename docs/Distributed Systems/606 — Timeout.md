---
layout: default
title: "Timeout"
parent: "Distributed Systems"
nav_order: 606
permalink: /distributed-systems/timeout/
number: "606"
category: Distributed Systems
difficulty: ★★☆
depends_on: "Failure Modes, Circuit Breaker"
used_by: "HTTP clients, gRPC, JDBC, Redis clients, Kafka consumers"
tags: #intermediate, #distributed, #resilience, #latency, #availability
---

# 606 — Timeout

`#intermediate` `#distributed` `#resilience` `#latency` `#availability`

⚡ TL;DR — **Timeout** terminates a waiting operation after a maximum duration, preventing resource exhaustion from indefinitely blocking calls — the most fundamental resilience mechanism in distributed systems, required for all network I/O.

| #606            | Category: Distributed Systems                            | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------------- | :-------------- |
| **Depends on:** | Failure Modes, Circuit Breaker                           |                 |
| **Used by:**    | HTTP clients, gRPC, JDBC, Redis clients, Kafka consumers |                 |

---

### 📘 Textbook Definition

**Timeout** is a resilience mechanism that limits the maximum time a caller waits for an operation to complete before abandoning it with an error. In distributed systems, without timeouts: a single slow dependency causes indefinite thread blocking → thread pool exhaustion → cascading failures. **Types of timeouts**: (1) **Connection timeout** — maximum time to establish a TCP connection (typically 1-5s); (2) **Read/Response timeout** — maximum time to receive the complete response after connection (typically 5-30s for business APIs); (3) **Write timeout** — time to send the full request body; (4) **Idle timeout** — time to keep an idle connection before closing (connection pool maintenance). **Timeout value selection**: timeout should be set to the maximum acceptable response time for 99.9th percentile — not the mean. If P99 response time = 200ms: timeout = 500ms–1s provides safety margin without being too conservative. Too short: false timeouts on legitimate slow requests. Too long: thread exhaustion on slow/failing dependencies. **Deadline propagation**: timeout set at the edge (API gateway: 5s) should propagate to downstream services as shorter deadlines (payment: 2s, fraud check: 1s) to ensure the aggregate call fits within the top-level deadline.

---

### 🟢 Simple Definition (Easy)

Timeout: "I'll wait at most N seconds for an answer. If no answer: give up." Without timeout: your app's thread waits forever for a slow database → all threads busy waiting → app completely unresponsive → users see spinning wheel forever. With timeout: wait 5 seconds. No response → throw exception → handle gracefully (return error, use cache, try different service). Thread freed. Other requests can proceed.

---

### 🔵 Simple Definition (Elaborated)

Three types of timeouts you need to know: Connection timeout: "I give up trying to establish a connection after N ms." Read timeout: "I give up waiting for the response after the connection is made after N ms." Idle connection timeout: "I close this unused connection in the pool after N ms." All three are necessary: connection timeout prevents blocked TCP handshakes. Read timeout prevents blocked threads on slow API responses. Idle timeout prevents resource leaks from abandoned connections. Most HTTP clients (OkHttp, Apache HC, RestTemplate) let you configure all three separately.

---

### 🔩 First Principles Explanation

**Timeout types, deadline propagation, and the timeout paradox:**

```
WHY TIMEOUTS ARE MANDATORY IN DISTRIBUTED SYSTEMS:

  Without timeout (blocking call):
    Thread A: calls Service B. B is hung (deadlock, OOM, GC pause for 10 minutes).
    Thread A: suspended. Occupies 1 thread from pool.
    Over 10 minutes: 100 requests arrive. Each blocked.
    At 50 threads: thread pool exhausted. New requests: rejected.
    Service A: completely unresponsive. For 10 MINUTES.

  With timeout (5s read timeout):
    Thread A: calls B. B is hung.
    After 5 seconds: SocketTimeoutException.
    Thread A: handle exception → return fallback response. Thread freed in 5s.
    50 threads: each freed in max 5s. Thread pool stays available.
    Service A: degraded (returns fallback) but responsive.

TIMEOUT TYPES AND CONFIGURATION:

  1. CONNECTION TIMEOUT (TCP handshake):
     Time to complete TCP 3-way handshake (SYN → SYN-ACK → ACK).
     If server is unreachable: OS retransmits SYN multiple times (default: 3-7 retries = 75s!).
     Custom connection timeout: override OS default. Typical: 1-5s.

     OkHttp: .connectTimeout(5, TimeUnit.SECONDS)
     JDBC: connectionTimeout=5000 (HikariCP)

  2. READ TIMEOUT / RESPONSE TIMEOUT:
     Time from connection established to complete response received.
     This is the most important timeout for preventing thread exhaustion.

     OkHttp: .readTimeout(30, TimeUnit.SECONDS)
     Spring RestTemplate: requestFactory.setReadTimeout(30000)
     JDBC: socketTimeout=30000 (MariaDB), queryTimeout

  3. WRITE TIMEOUT:
     Time to fully send the request body.
     Usually less critical (you control the sending, not the remote).
     Important for large uploads to slow receivers.

     OkHttp: .writeTimeout(30, TimeUnit.SECONDS)

  4. CALL TIMEOUT (end-to-end):
     Total time from start to finish: includes connect + write + read.
     More useful than separate timeouts for overall SLA enforcement.

     OkHttp: .callTimeout(60, TimeUnit.SECONDS)

  5. POOL TIMEOUT / BORROW TIMEOUT:
     Time to wait for a connection from the pool when pool is exhausted.

     HikariCP: connectionTimeout=30000 (wait 30s for pool slot — usually set much lower)

  6. IDLE TIMEOUT:
     Time to keep idle connection in pool before closing.
     Prevents holding connections to DB/service that the server has already closed.

     HikariCP: idleTimeout=600000 (10 minutes default)

TIMEOUT VALUE SELECTION:

  FORMULA: timeout = percentile_response_time × safety_multiplier

  Where: percentile = 99th or 99.9th (not mean/median).
         safety_multiplier = 2-3×.

  Example:
    Service B: P50=50ms, P99=200ms, P999=800ms.
    Acceptable user-visible latency: < 5 seconds.
    Internal service timeout: 500ms (2.5× P99).
    External API timeout: 2000ms (2.5× P999, higher for rare spikes).

  COMMON MISTAKES:
    Too loose: timeout=30s. P99=200ms.
      Wait: 30s ÷ 200ms = 150 slow responses in progress simultaneously.
      Thread pool of 50: exhausted after 50 slow responses. Why have timeout at all?

    Too tight: timeout=100ms. P99=200ms.
      50% of P99+ responses → unnecessary timeout errors → poor availability.

  RULE: timeout should be ≥ 99th percentile of NORMAL response time.
        If P99=500ms: timeout ≥ 500ms (preferably 1-2s with safety margin).

DEADLINE PROPAGATION:

  Problem: top-level request has 5s SLA. Calls: Payment (2s) → Fraud Check (1s) → DB (0.5s).
           Total: 3.5s. Within 5s SLA.

  Without deadline propagation:
    Payment timeout: 5s. Fraud timeout: 5s. DB timeout: 5s.
    Payment: slow → takes 4.9s. Fraud: slow → takes 4.9s. Total: 9.8s.
    Top-level: times out at 5s. But payment and fraud: still running (using resources).
    Wasted work: payment and fraud complete at 9.8s (results discarded by timeout).

  With deadline propagation:
    Top-level request: starts at T=0. Deadline: T=5s.
    Payment call: timeout=min(2s, remaining_time - 0.1s overhead).
      At T=0: remaining=5s. Payment timeout=min(2s, 4.9s)=2s.
    Fraud call: timeout=min(1s, remaining_time - 0.1s).
      At T=2: remaining=3s. Fraud timeout=min(1s, 2.9s)=1s.
    DB call: timeout=min(0.5s, remaining_time - 0.1s).
      At T=3: remaining=2s. DB timeout=min(0.5s, 1.9s)=0.5s.

    If payment takes 4.9s (slow): payment times out at T=2s.
    Top-level: returns error at T=2s. Fraud and DB: never called. Resources conserved.

  IMPLEMENTATION: pass deadline in context / header.
    gRPC: deadline passed in Context. Each service: creates child Context with shorter timeout.
    HTTP: custom header X-Request-Deadline (Unix timestamp).
          Each service: check if deadline passed → reject immediately.

  gRPC deadline propagation example:
    // Client (edge): set 5-second deadline.
    Deadline deadline = Deadline.after(5, TimeUnit.SECONDS);
    stub.withDeadline(deadline).processOrder(request);

    // Server (payment): extract remaining deadline from gRPC context.
    // gRPC automatically propagates remaining deadline to downstream calls.
    // If remaining deadline < 50ms: fail fast (not enough time to complete).

TIMEOUT AND IDEMPOTENCY:

  Timeout + non-idempotent operation:
    Client sends request. Server: processes. Timeout fires on client.
    Client: "failed." Server: "done."
    Client retries (same UUID idempotency key): gets cached result.
    Safe.

  Without idempotency key: client retries → double execution.
  RULE: timeout triggers retry ONLY if operation is idempotent.

TIMEOUT IN CONTEXT OF RESILIENCE PATTERNS:

  Timeout is the foundation; others build on top:

  Timeout → detects slow calls (count timeout as "failure" in CB metrics).
  Circuit Breaker → if timeout rate > threshold: opens circuit.
  Retry with Backoff → retries after timeout (only if idempotent).
  Bulkhead → limits concurrent calls so timeouts don't exhaust all threads.

  Without timeout: Circuit Breaker never sees failures (threads blocked, not erroring).
  CB requires timeout to detect slow calls. Set CB timeLimiterConfig.timeoutDuration.

  Resilience4j TimeLimiter:
    @TimeLimiter(name = "service-b", fallbackMethod = "fallback")
    public CompletableFuture<Response> callServiceB(Request req) {
        return CompletableFuture.supplyAsync(() -> serviceB.call(req));
    }
    // timeLimiter.instances.service-b.timeoutDuration=5s
    // If serviceB.call() takes > 5s: TimeoutException → fallback called.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT timeouts:

- Single slow dependency: all threads blocked indefinitely → service completely unresponsive
- Network partition: TCP connections never error (kernel retransmits) → application sees hang
- Wasted work: downstream services completing requests after upstream already gave up

WITH timeouts:
→ Bounded blocking time: threads freed after max T seconds regardless of downstream state
→ Cascade prevention: timeouts trigger circuit breaker tracking → fast fail for systemic failures
→ Deadline enforcement: SLAs propagated as deadlines prevent budget overrun in call chains

---

### 🧠 Mental Model / Analogy

> A restaurant waiter sets a kitchen timer when taking your order. After 30 minutes: if the food hasn't arrived, the waiter apologetically informs you the order is cancelled (timeout) and offers you a free appetizer (fallback). Without the timer: you'd wait indefinitely. The restaurant: keeps the kitchen order in flight, tying up kitchen resources, while you've already left.

"Kitchen timer" = timeout value
"Cancelled order after 30 minutes" = timeout exception + fallback
"Kitchen still working on the order" = server-side work continuing after client timeout (wasted work)

---

### ⚙️ How It Works (Mechanism)

```
HTTP Read Timeout (OkHttp internal):

  Client: schedules background timer when request is sent.
  Timer duration: readTimeout value.

  If response completes before timer: timer cancelled. Return response.
  If timer fires before response:
    Socket: forcibly closed.
    Throw: SocketTimeoutException ("Read timed out").
    Thread: unblocked. Handles exception (retry, fallback, error).

  Server-side: response body generation may continue until server notices closed socket.
  Server: writes to closed socket → IOException → server-side processing stops.
```

---

### 🔄 How It Connects (Mini-Map)

```
Failure Modes (slow calls as omission failures; need bounded wait)
        │
        ▼
Timeout ◄──── (you are here)
(bound maximum wait time for all network calls)
        │
        ├── Circuit Breaker: tracks timeout rate → opens circuit on systemic slowness
        ├── Retry with Backoff: triggered by timeout exception (only for idempotent ops)
        └── Bulkhead: limits concurrent timed-out calls (prevents thread exhaustion)
```

---

### 💻 Code Example

**Spring Boot timeout configuration across layers:**

```java
// application.yaml:
spring:
  datasource:
    hikari:
      connection-timeout: 5000      # 5s: wait for pool connection
      idle-timeout: 600000          # 10min: close idle connections
      max-lifetime: 1800000         # 30min: rotate connections

  # Feign HTTP client timeouts:
feign:
  client:
    config:
      default:
        connectTimeout: 2000        # 2s: TCP connect
        readTimeout: 10000          # 10s: response read

// Resilience4j TimeLimiter (for reactive/async calls):
resilience4j:
  timelimiter:
    instances:
      payment-service:
        timeoutDuration: 3s
        cancelRunningFuture: true   # Cancel the underlying future on timeout

// WebClient (reactive) timeout:
@Bean
public WebClient paymentWebClient() {
    HttpClient httpClient = HttpClient.create()
        .option(ChannelOption.CONNECT_TIMEOUT_MILLIS, 2000)  // 2s connect
        .responseTimeout(Duration.ofSeconds(5))               // 5s read
        .doOnConnected(conn ->
            conn.addHandlerLast(new ReadTimeoutHandler(5, TimeUnit.SECONDS))
                .addHandlerLast(new WriteTimeoutHandler(5, TimeUnit.SECONDS)));

    return WebClient.builder()
        .clientConnector(new ReactorClientHttpConnector(httpClient))
        .baseUrl("https://payment-service")
        .build();
}

// gRPC deadline propagation:
@GrpcService
public class OrderService extends OrderServiceGrpc.OrderServiceImplBase {

    @Override
    public void processOrder(OrderRequest request, StreamObserver<OrderResponse> observer) {
        // Check if deadline already passed before doing expensive work:
        Context context = Context.current();
        if (context.getDeadline() != null && context.getDeadline().isExpired()) {
            observer.onError(Status.DEADLINE_EXCEEDED.asRuntimeException());
            return;
        }

        // Propagate remaining deadline to downstream payment call:
        // gRPC stub automatically inherits context deadline.
        PaymentResult payment = paymentStub
            .withDeadline(context.getDeadline())  // Pass remaining deadline
            .processPayment(PaymentRequest.newBuilder()
                .setOrderId(request.getOrderId())
                .build());

        observer.onNext(buildResponse(payment));
        observer.onCompleted();
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                                  | Reality                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| -------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A timeout means the operation failed                           | A timeout means YOU stopped waiting — the server may have succeeded. This is the fundamental timeout ambiguity: the server processed the request and committed, but the network dropped the response. This is why timeouts on non-idempotent operations are dangerous (retry → double-execution). Timeout = "I don't know what happened," not "the server failed."                                                                                             |
| Setting a long timeout is safer than a short one               | Long timeouts hold threads/connections longer, increasing the risk of resource exhaustion under load. A 30-second timeout on a service with 50 threads means a 30-second outage in a downstream service exhausts the thread pool (50 requests × 30s ÷ 10s arrival rate = 50 concurrent blocked threads). Short timeouts free resources faster and enable faster circuit breaker trips. The risk of long timeouts is usually higher than the risk of short ones |
| Network socket errors happen fast (no timeout needed)          | TCP connections to unreachable hosts don't fail fast. The OS sends SYN, waits for SYN-ACK, retransmits SYN after 1s, 3s, 7s, 15s, 31s... Default TCP connect timeout: 75 seconds on Linux. Without a custom connect timeout, your application will appear hung for 75 seconds. Always set custom connect timeout (1-5s) for all outbound connections                                                                                                           |
| Database queries don't need timeouts (they run on the DB side) | Database queries run on the server, but the client thread waits for the result. A slow query (full table scan, deadlock wait, lock contention) holds the client thread and the DB connection. With HikariCP: a 50-thread pool with 30s query timeout = up to 50 × 30s = 1500 thread-seconds of blocked capacity. Set queryTimeout (JDBC) and socketTimeout (driver) to bound maximum query wait time                                                           |

---

### 🔥 Pitfalls in Production

**Default timeout causing silent hang in production:**

```
SCENARIO: Spring Boot app with default RestTemplate (no timeout set).
  Downstream service: load balancer accepts TCP connection (SYN-ACK) but never sends response
  (upstream app crashed, LB doesn't know).

  Default RestTemplate: no read timeout.
  Thread: blocked waiting for response.
  20 RPS incoming. Each request: allocates thread, blocks.
  After 2.5 minutes: all 50 threads blocked. New requests: rejected with 503.
  App: unresponsive. No error logs (threads are waiting, not erroring).

BAD: RestTemplate without timeout (Spring Boot default):
  // This creates an HTTP client with NO timeout:
  @Bean
  public RestTemplate restTemplate() {
      return new RestTemplate(); // No timeout configured!
  }

  // OR: RestTemplate with wrong timeout configuration:
  RestTemplate restTemplate = new RestTemplate();
  restTemplate.setRequestFactory(new SimpleClientHttpRequestFactory());
  // SimpleClientHttpRequestFactory: default connectTimeout=-1, readTimeout=-1 (infinite!)

FIX: Always configure explicit timeouts:
  @Bean
  public RestTemplate restTemplate() {
      SimpleClientHttpRequestFactory factory = new SimpleClientHttpRequestFactory();
      factory.setConnectTimeout(2000);  // 2s connection timeout
      factory.setReadTimeout(10000);    // 10s read timeout
      return new RestTemplate(factory);
  }

  // OR with Apache HttpClient (more configurable):
  @Bean
  public RestTemplate restTemplate() {
      RequestConfig config = RequestConfig.custom()
          .setConnectTimeout(2000)
          .setSocketTimeout(10000)      // Read timeout
          .setConnectionRequestTimeout(5000)  // Pool borrow timeout
          .build();

      CloseableHttpClient client = HttpClientBuilder.create()
          .setDefaultRequestConfig(config)
          .build();

      return new RestTemplate(new HttpComponentsClientHttpRequestFactory(client));
  }

  // VERIFY: test that timeout is actually applied:
  // Use WireMock with fixed delay longer than timeout → confirm SocketTimeoutException.
  // Unit test:
  @Test
  void shouldTimeoutAfter2Seconds() {
      wireMock.stubFor(get("/api").willReturn(
          aResponse().withFixedDelay(3000))); // 3s delay

      assertThrows(ResourceAccessException.class, () ->
          restTemplate.getForObject(wireMock.baseUrl() + "/api", String.class));
      // Must throw in < 2.5s (2s timeout + small overhead)
  }
```

---

### 🔗 Related Keywords

- `Circuit Breaker` — timeout rate feeds into CB failure rate; CB uses TimeLimiter for timeout-based failure detection
- `Retry with Backoff` — timeout exception triggers retry (only for idempotent operations)
- `Bulkhead` — limits concurrent timed-out calls; prevents timeout storm from exhausting thread pool
- `Deadline Propagation` — top-level timeout divided into per-service budgets across a call chain

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Terminate waiting after max duration.   │
│              │ Prevents indefinite blocking → thread   │
│              │ exhaustion → cascade. Most basic safety.│
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ ALWAYS for all outbound network calls:  │
│              │ HTTP, gRPC, DB, Redis, Kafka, etc.       │
│              │ No exceptions. No defaults.             │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Never avoid. Configure deliberately.    │
│              │ Infinite timeout (timeout=-1) is an     │
│              │ explicit ticking time bomb.             │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Kitchen timer: 30 minutes and the      │
│              │  order is cancelled — don't wait forever."│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Circuit Breaker → Retry with Backoff →  │
│              │ Bulkhead → Deadline Propagation → gRPC  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You have a 5-service chain: A → B → C → D → E. Each service has a 5-second read timeout. A slow E takes 4.9 seconds. What is the worst-case total latency for a request through the chain? How does this compare to the user's expected 5-second SLA? How should you configure per-service timeouts to ensure the end-to-end SLA is met, accounting for network overhead and processing time at each hop?

**Q2.** A gRPC call with a 3-second deadline reaches Service B at T=2.8s (0.2s already elapsed on the wire). Service B starts processing but the operation takes 500ms. What happens? Does Service B's gRPC framework automatically cancel the operation when the deadline expires? What happens to resources (threads, DB connections) that Service B has already acquired? How should service-level code check for deadline expiry to avoid wasted work?
