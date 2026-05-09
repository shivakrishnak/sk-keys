---
id: SPR-060
title: "Spring Migration Strategy (MVC to WebFlux)"
category: Spring Core
tier: tier-3-java
folder: SPR-spring-core
difficulty: ★★★
depends_on: SPR-047, SPR-048, SPR-052, SPR-053
used_by:
related: SPR-059, SPR-065
tags:
  - spring
  - java
  - advanced
  - architecture
  - reactive
  - bestpractice
status: complete
version: 1
layout: default
parent: "Spring Core"
grand_parent: "Technical Dictionary"
nav_order: 60
permalink: /spr/spring-migration-strategy-mvc-webflux/
---

# SPR-060 - Spring Migration Strategy (MVC to WebFlux)

⚡ TL;DR - Migrating from Spring MVC to WebFlux is not a simple swap; it requires replacing every blocking call, dependency, and mental model with reactive equivalents.

| Field          | Value                                                                                                                    |
| -------------- | ------------------------------------------------------------------------------------------------------------------------ |
| **Depends on** | [[SPR-047 - WebFlux / Reactive]], [[SPR-048 - Mono / Flux]], [[SPR-052 - WebFlux / Reactive]], [[SPR-053 - Mono / Flux]] |
| **Used by**    | -                                                                                                                        |
| **Related**    | [[SPR-059 - Spring Architecture at Scale]], [[SPR-065 - Spring Reactive Model (Project Reactor Internals)]]              |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**

A Spring MVC service handles 500 concurrent requests using 500 threads. Each thread blocks waiting for database or downstream HTTP responses. Under peak load the thread pool exhausts, new requests queue, latency spikes, and the service fails. The fix - more threads - hits OS limits around 10,000 threads and consumes 200MB-1GB RAM just for thread stacks.

**THE BREAKING POINT:**

I/O-bound microservices (HTTP fan-out, database queries, cache lookups) spend 90% of their thread time blocking. Reactive programming eliminates idle thread blocking by using event-loop threads and callbacks. But migrating is not trivial: any single blocking call on a reactive thread deadlocks the entire event loop.

**THE INVENTION MOMENT:**

Spring WebFlux (Spring 5, 2017) provides a reactive web stack built on Project Reactor and Netty. It uses the same familiar annotation model (`@RestController`, `@GetMapping`) but returns `Mono<T>` and `Flux<T>` instead of `T` and `List<T>`. The migration strategy determines how to bridge the two worlds safely.

**EVOLUTION:**

- **2017:** Spring WebFlux released with Spring 5; completely separate from Spring MVC
- **2018:** Spring Data reactive repositories (`ReactiveCrudRepository`) enable non-blocking data access
- **2020:** Spring Cloud Gateway replaces Zuul; built on WebFlux
- **2023:** Spring Boot 3.2 virtual thread support gives MVC near-reactive throughput without reactive code

---

### 📘 Textbook Definition

**Spring MVC to WebFlux migration** is the process of replacing Spring MVC's synchronous, thread-per-request model with Spring WebFlux's asynchronous, event-loop model. The migration must be **total** (every I/O call must be non-blocking) or **hybrid** (blocking calls wrapped with `subscribeOn(Schedulers.boundedElastic())`). A _partial_ migration - reactive controllers calling blocking repositories - provides no throughput benefit and risks event-loop deadlocks.

---

### ⏱️ Understand It in 30 Seconds

**One line:** You cannot add WebFlux to a blocking application and call it reactive - every layer must be non-blocking or the event loop stalls.

> Migrating to WebFlux is like converting a relay race to a bicycle courier network. You cannot just swap the final runner - every hand-off in the chain must change, or the couriers still wait at every stop.

**One insight:** Spring Boot 3.2 virtual threads may make this migration unnecessary for many services - virtual threads give thread-per-request blocking code reactive-level throughput by making blocking cheap.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. An event-loop thread that blocks starves all other requests on that thread - the cascade is immediate
2. Reactive code provides backpressure; blocking code does not; mixing them loses backpressure guarantees
3. Every I/O boundary (DB, HTTP, cache) must have a reactive driver for a true non-blocking pipeline
4. Testing reactive code requires `StepVerifier` - `assertThat` cannot observe async completion
5. Error handling in reactive code uses `.onErrorResume()`, not try/catch

**DERIVED DESIGN:**

From invariant 1 → any blocking call must use `Schedulers.boundedElastic()` to offload to a bounded thread pool.
From invariant 3 → migration feasibility checklist: does your DB have an R2DBC driver? Does your message broker have a reactive client?
From invariant 4 → test strategy must change completely alongside the production code.

**THE TRADE-OFFS:**

**Gain:** Higher throughput for I/O-bound workloads under high concurrency; lower thread count and memory; built-in backpressure.

**Cost:** Steeper learning curve; harder to debug (non-linear stack traces); not all libraries have reactive support; cognitive overhead of composing pipelines.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

**Essential:** Non-blocking I/O genuinely requires a different execution model.

**Accidental:** Much of the migration complexity comes from non-reactive libraries (JDBC, some HTTP clients) requiring wrapping rather than native async support. Spring Boot virtual threads reduce this accidental complexity significantly.

---

### 🧪 Thought Experiment

**SETUP:** A Spring MVC service makes 3 serial downstream HTTP calls per request, each taking 100ms. Thread pool size: 200.

**WHAT HAPPENS with MVC:**

200 concurrent requests use 200 threads. Each thread blocks 300ms (3 × 100ms). Throughput ceiling: 200 threads / 0.3s = ~667 req/s. Thread memory: 200 × 1MB = 200MB just for stacks.

**WHAT HAPPENS with WebFlux (fully reactive):**

2 event-loop threads. Requests are non-blocking. 3 HTTP calls are parallelised with `Mono.zip()` → total latency 100ms per request (not 300ms). Same throughput ceiling but now CPU-limited, not thread-limited. 10,000 concurrent slow connections handled without extra threads.

**WHAT HAPPENS with partial migration (reactive controller, blocking JDBC):**

Controller is reactive, but `jdbcTemplate.query()` blocks the event-loop thread. Event loop stalls. The system performs _worse_ than pure MVC because the event loop thread is starved while JDBC waits, and other requests cannot proceed.

**THE INSIGHT:**

A partial migration to WebFlux is not a 50% improvement - it is often a 100% regression. Commit fully or use virtual threads instead.

---

### 🧠 Mental Model / Analogy

> Spring MVC is like a restaurant with 200 waiters (threads). Each waiter takes an order, goes to the kitchen, and stands there waiting until the food is ready before returning. WebFlux is like 2 waiters with a buzzer system: they take orders, give the kitchen a buzzer, serve other tables, and return when the buzzer rings.

**Element mapping:**

- Waiters → threads
- Standing in the kitchen → blocking I/O wait
- Buzzer system → event loop + callbacks / reactive pipelines
- Food being prepared → DB query / HTTP call
- Restaurant capacity → throughput ceiling

Where this analogy breaks down: unlike a restaurant, WebFlux's "buzzers" can compose - you can wait for multiple buzzers simultaneously with `Mono.zip()`, which has no direct restaurant equivalent.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
MVC uses one thread per request and makes that thread wait for database and API calls. WebFlux uses far fewer threads and never makes them wait - instead, it sets up callbacks that run when the data arrives. Moving from one to the other means changing every part of the code that does any waiting.

**Level 2 - How to use it (junior developer):**
Replace `@RestController` return types (`String`, `List<T>`) with `Mono<String>`, `Flux<T>`. Replace `JdbcTemplate` with R2DBC repositories. Replace `RestTemplate` with `WebClient`. Replace `Thread.sleep()` / blocking waits with `Mono.delay()`. Use `StepVerifier` in tests instead of direct assertions.

**Level 3 - How it works (mid-level engineer):**
WebFlux registers the controller method as a Netty pipeline handler. The handler returns a `Mono` (a lazy publisher). Netty subscribes when the HTTP connection is ready. The `Mono` chain executes operator by operator without allocating a dedicated thread. When a database call is made via R2DBC, the R2DBC driver registers a callback with the database connection pool. When data arrives, the Netty event loop resumes the pipeline on the I/O thread. No thread blocks at any point.

**Level 4 - Why it was designed this way (senior/staff):**
Project Reactor implements the Reactive Streams specification, which mandates backpressure: a subscriber can signal how many items it can handle (`request(n)`). This prevents unbounded buffering and memory pressure when producers are faster than consumers. Spring MVC has no equivalent - it allocates threads to provide implicit backpressure (thread exhaustion = slow down). WebFlux's explicit backpressure is more precise but requires the entire pipeline to participate, which is why partial migration breaks the model.

**Expert Thinking Cues:**

- `Schedulers.boundedElastic()` is the escape hatch for legacy blocking code; it caps threads to prevent unbounded growth
- `block()` on a reactive pipeline in a WebFlux handler is a runtime error (`IllegalStateException: block()/blockFirst()/blockLast() are blocking, which is not supported in thread reactor-http-nio`)
- `@Blocking` annotation (Project Loom / virtual threads) is the MVC equivalent of `subscribeOn(Schedulers.boundedElastic())`

---

### ⚙️ How It Works (Mechanism)

Migration checklist by layer:

```
Layer           MVC (blocking)         WebFlux (non-blocking)
──────────────────────────────────────────────────────────
Web layer       @RestController T      @RestController Mono<T>
                ResponseEntity<T>      Mono<ResponseEntity<T>>

HTTP client     RestTemplate           WebClient
                                       or HttpInterface (Boot 3)

Data layer      JpaRepository<T,ID>    ReactiveCrudRepository<T,ID>
                JdbcTemplate           R2dbcEntityTemplate

Cache           @Cacheable (sync)      ReactiveRedisTemplate

Messaging       KafkaTemplate.send()   ReactiveKafkaProducerTemplate

Tests           MockMvc + assertThat   WebTestClient + StepVerifier

Error handling  try/catch              .onErrorResume()
                                       .onErrorMap()
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW (fully reactive):**

```
[HTTP Request arrives on Netty event loop]
     |
     ├─ Router maps to WebFlux handler
     |        ← YOU ARE HERE
     ├─ Handler returns Mono<Response>
     |    (no thread allocated yet)
     |
     ├─ Mono chain assembled (lazy)
     |    ├─ R2DBC query → Mono<Order>
     |    └─ WebClient HTTP call → Mono<Price>
     |
     ├─ Netty subscribes to Mono
     |    ├─ R2DBC connection pool notified
     |    └─ HTTP connection pool notified
     |
     ├─ DB responds → event loop resumes pipeline
     ├─ HTTP responds → event loop resumes pipeline
     |
[Response written to Netty channel]
(Zero dedicated threads held during I/O waits)
```

**FAILURE PATH:**

- Blocking call on event loop → `IllegalStateException` + event loop stall → cascading timeouts
- Reactive cold source subscribed multiple times → side effects executed multiple times (cache writes, emails)
- Backpressure not handled → `OutOfMemoryError` when `Flux` produces faster than subscriber consumes

**WHAT CHANGES AT SCALE:**

At scale, WebFlux's advantage is resource density: 10 WebFlux pods handle the same traffic as 50 MVC pods. The saving is real but requires fully reactive stack. With virtual threads (Spring Boot 3.2), MVC pods need only 20 pods - a middle ground without reactive complexity.

---

### 💻 Code Example

**BAD - partial migration (reactive controller, blocking repository):**

```java
// Controller is "reactive" but blocks event loop
@RestController
public class OrderController {
    private final OrderRepository repo; // JPA - BLOCKING

    @GetMapping("/orders/{id}")
    public Mono<Order> getOrder(@PathVariable Long id) {
        // DANGER: repo.findById() blocks the event loop!
        return Mono.just(repo.findById(id).orElseThrow());
    }
}
```

**GOOD - fully reactive stack:**

```java
// Reactive controller with reactive repository
@RestController
public class OrderController {
    private final ReactiveOrderRepository repo;

    @GetMapping("/orders/{id}")
    public Mono<Order> getOrder(@PathVariable Long id) {
        return repo.findById(id)
            .switchIfEmpty(Mono.error(
                new OrderNotFoundException(id)));
    }
}

// application.yml - R2DBC instead of JPA
// spring.r2dbc.url=r2dbc:postgresql://db:5432/orders

// Interface uses reactive base
public interface ReactiveOrderRepository
    extends ReactiveCrudRepository<Order, Long> {}
```

**ACCEPTABLE - wrapping unavoidable blocking code:**

```java
@GetMapping("/legacy/{id}")
public Mono<LegacyResult> getLegacy(@PathVariable Long id) {
    // Offload blocking call to bounded thread pool
    return Mono.fromCallable(
            () -> legacyService.blockingCall(id))
        .subscribeOn(Schedulers.boundedElastic());
}
```

**How to test / verify correctness:**

```java
@WebFluxTest(OrderController.class)
class OrderControllerTest {
    @Autowired WebTestClient client;
    @MockBean ReactiveOrderRepository repo;

    @Test
    void getOrder_returnsOrder() {
        given(repo.findById(1L))
            .willReturn(Mono.just(
                new Order(1L, "PLACED")));

        client.get().uri("/orders/1")
            .exchange()
            .expectStatus().isOk()
            .expectBody(Order.class)
            .value(o -> assertThat(o.status())
                .isEqualTo("PLACED"));
    }
}
```

---

### ⚖️ Comparison Table

| Aspect                | Spring MVC                     | Spring WebFlux            | MVC + Virtual Threads         |
| --------------------- | ------------------------------ | ------------------------- | ----------------------------- |
| Concurrency model     | Thread-per-request             | Event loop + callbacks    | Thread-per-request (virtual)  |
| I/O blocking          | Blocks OS thread               | Non-blocking              | Blocks virtual thread (cheap) |
| Max concurrency       | ~10,000 threads                | Millions of connections   | Millions of virtual threads   |
| Memory per conn       | ~1MB (thread stack)            | ~100 bytes                | ~few KB (virtual thread)      |
| Code complexity       | Low                            | High                      | Low (same as MVC)             |
| Library compatibility | Universal                      | Reactive drivers required | Universal                     |
| Migration cost        | -                              | High (full rewrite)       | Low (config flag)             |
| Backpressure          | No (thread pool acts as limit) | Yes (Reactive Streams)    | No                            |

---

### ⚠️ Common Misconceptions

| Misconception                                          | Reality                                                                                                                                    |
| ------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------ |
| "Adding WebFlux to existing code improves performance" | Only a fully non-blocking stack benefits. Blocking calls on event-loop threads are worse than MVC.                                         |
| "WebFlux is always faster than MVC"                    | For CPU-bound or low-concurrency workloads, MVC is equally fast and simpler. WebFlux wins on I/O-bound, high-concurrency workloads.        |
| "`block()` is fine inside a `@Service`"                | `block()` inside a WebFlux request pipeline deadlocks the event loop. Only safe in non-reactive contexts.                                  |
| "Virtual threads replace WebFlux"                      | Virtual threads eliminate WebFlux's main _concurrency_ advantage. WebFlux still provides backpressure and streaming.                       |
| "R2DBC is just JDBC with callbacks"                    | R2DBC is a fundamentally different spec. No JDBC compatibility; schema evolution tools (Flyway, Liquibase) still need JDBC for migrations. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Event loop deadlock from blocking call**

**Symptom:** All requests hang after a short burst; no response ever returned; `reactor-http-nio` threads stuck.

**Root Cause:** Blocking call (`JDBC`, `Thread.sleep()`, `block()`) executed on Netty event-loop thread.

**Diagnostic:**

```bash
# Take a thread dump and look for reactor-http-nio threads
jstack <PID> | grep -A 20 "reactor-http-nio"
# If they show WAITING or TIMED_WAITING on JDBC/sleep: deadlock
```

**Fix:** Wrap blocking call with `Schedulers.boundedElastic()` or replace with reactive equivalent.

**Prevention:** Add a Blockhound integration test (`BlockHound.install()` + `@Test`) to detect blocking calls on reactive threads at test time.

---

**Mode 2: Cold `Mono` subscribed multiple times causes duplicate side effects**

**Symptom:** Payment processed twice; email sent twice; no apparent cause in single-threaded test.

**Root Cause:** A `Mono` that creates a new subscription per call (cold source) was subscribed twice: once in production code, once in a retry or test re-run.

**Diagnostic:**

```java
// Mono.fromCallable(() -> paymentService.charge(...))
// Every subscription triggers a new charge!
```

**Fix:** Use `Mono.defer()` intentionally; use `.cache()` if a single execution should be shared; document cold vs hot semantics.

**Prevention:** Code review policy: flag any `Mono.fromCallable()` that produces a side effect without explicit idempotency guarantee.

---

**Mode 3: R2DBC connection pool exhausted (Security / Reliability failure mode)**

**Symptom:** `Connection pool has been exhausted, giving up on obtaining a connection` under moderate load.

**Root Cause:** R2DBC pool size not tuned; long-running queries hold connections; pool defaults to 10 connections.

**Diagnostic:**

```bash
curl http://localhost:8080/actuator/metrics/\
r2dbc.pool.acquired
curl http://localhost:8080/actuator/metrics/\
r2dbc.pool.pending
```

**Fix:**

```yaml
spring:
  r2dbc:
    pool:
      max-size: 50
      initial-size: 10
      max-idle-time: 30m
```

**Prevention:** Load test before production; alert on `r2dbc.pool.pending > 0` sustained for more than 30 seconds.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[SPR-047 - WebFlux / Reactive]] - the reactive web stack
- [[SPR-048 - Mono / Flux]] - the reactive types
- [[SPR-054 - Backpressure (Spring)]] - the backpressure model

**Builds On This (learn these next):**

- [[SPR-065 - Spring Reactive Model (Project Reactor Internals)]] - the internals of the reactive model
- [[SPR-059 - Spring Architecture at Scale]] - where reactive fits in large systems

**Alternatives / Comparisons:**

- Spring MVC + Virtual Threads - lower migration cost alternative for I/O-bound services
- Micronaut Reactive - compile-time DI with reactive HTTP
- Vert.x - fully reactive alternative to Spring with no legacy blocking model

---

### 📌 Quick Reference Card

```
+----------------------------------------------------------+
| WHAT IT IS    | Strategy for moving Spring MVC to WebFlux|
| PROBLEM       | Thread exhaustion under high I/O concurr. |
| KEY INSIGHT   | Partial migration is worse than no migration|
| USE WHEN      | High I/O concurrency; streaming; WebSocket |
| AVOID WHEN    | CPU-bound; low concurrency; team unfamiliar|
|               | with reactive; consider virtual threads   |
| TRADE-OFF     | Throughput/memory vs code complexity      |
| ONE-LINER     | Go all-in or use virtual threads instead  |
| NEXT EXPLORE  | SPR-065 (Reactor Internals), SPR-054      |
|               | (Backpressure)                            |
+----------------------------------------------------------+
```

**If you remember only 3 things:**

1. Any blocking call on the event loop starves all other requests - partial migration is worse than no migration
2. The migration checklist: web layer → data layer (R2DBC) → HTTP client (WebClient) → tests (StepVerifier)
3. Spring Boot 3.2 virtual threads may make this migration unnecessary for many I/O-bound services

**Interview one-liner:** "Migrating to WebFlux requires replacing every blocking I/O call with reactive equivalents; a partial migration where reactive controllers call blocking repositories is worse than remaining on MVC."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** _Async boundaries must be total, not partial._ In any system where non-blocking I/O provides benefit, a single blocking call at any point in the chain negates the benefit and can cause cascading failures. This applies to Node.js event loops, Python asyncio, and Go goroutines equally.

**Where else this pattern appears:**

- **Node.js** - a synchronous `fs.readFileSync()` in a request handler blocks the entire event loop for all clients
- **Python asyncio** - `time.sleep()` inside an `async def` function blocks the event loop; `await asyncio.sleep()` does not
- **Go goroutines** - `syscall.Read()` blocks a goroutine but not the scheduler; the equivalent of virtual threads, not reactive

---

### 💡 The Surprising Truth

Spring WebFlux and Spring MVC can run in the same application - but doing so provides no performance benefit for the MVC portions. What is genuinely surprising is that Netflix, one of the highest-traffic users of reactive Java, began migrating _away_ from fully reactive code in 2023 toward virtual threads, citing dramatically reduced developer cognitive load and equivalent throughput for their workloads. The reactive model solves a real problem; virtual threads solve the same problem with less complexity for most use cases. The migration from MVC to WebFlux may be partially reversed by the migration from WebFlux back to MVC-with-virtual-threads.

---

### 🧠 Think About This Before We Continue

**Question 1 (C - Design Trade-off):** Both WebFlux and virtual threads claim to solve the "blocking thread" problem for I/O-bound services. For a new service in 2025, what specific characteristics would make you choose WebFlux over virtual threads, and vice versa?

_Hint:_ Consider streaming responses (`Flux`), backpressure requirements, library ecosystem compatibility, and the team's existing reactive experience.

**Question 2 (D - Root Cause):** A WebFlux service that worked perfectly in load testing suddenly deadlocks in production after a dependency was upgraded. The new dependency added a `ThreadLocal`-based context propagation mechanism. Why would this cause deadlocks in WebFlux?

_Hint:_ Think about what happens when an event-loop thread resumes a reactive pipeline after an I/O callback - which thread does it resume on, and what is that thread's `ThreadLocal` state?

**Question 3 (B - Scale):** A fully reactive WebFlux service with 2 event-loop threads handles 10,000 concurrent connections. What happens when one downstream service starts responding in 30 seconds instead of 200ms, and how does WebFlux's backpressure model protect the service from cascading failure?

_Hint:_ Consider how `WebClient` timeout configuration, `Mono.timeout()`, and circuit breakers interact with backpressure in [[SPR-015 - Spring Cloud Circuit Breaker]].
