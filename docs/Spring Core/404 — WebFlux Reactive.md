---
layout: default
title: "WebFlux / Reactive"
parent: "Spring Core"
nav_order: 404
permalink: /spring/webflux-reactive/
number: "404"
category: Spring Core
difficulty: ★★★
depends_on: "Reactor, Non-blocking I/O, Event Loop, Mono, Flux, Backpressure"
used_by: "Mono, Flux, R2DBC, WebClient, Backpressure, Reactive Streams"
tags: #java, #spring, #springboot, #advanced, #deep-dive, #performance, #nodejs
---

# 404 — WebFlux / Reactive

`#java` `#spring` `#springboot` `#advanced` `#deep-dive` `#performance` `#nodejs`

⚡ TL;DR — Spring's reactive web framework built on Project Reactor and Netty — handles concurrent requests with a small, fixed thread pool using non-blocking I/O instead of one-thread-per-request.

| #404 | category: Spring Core
|:---|:---|:---|
| **Depends on:** | Reactor, Non-blocking I/O, Event Loop, Mono, Flux, Backpressure | |
| **Used by:** | Mono, Flux, R2DBC, WebClient, Backpressure, Reactive Streams | |

---

### 📘 Textbook Definition

**Spring WebFlux** is Spring Framework's reactive-stack web framework, introduced in Spring 5. It is built on **Project Reactor** and runs on non-blocking servers (Netty by default, or reactive Tomcat/Jetty/Undertow). Unlike Spring MVC where each request occupies a thread for its duration, WebFlux uses an event-loop model: a small number of threads handle all I/O events, delegating blocking work to worker pools. Handlers return **`Mono<T>`** (0 or 1 value) or **`Flux<T>`** (0 to N values) — reactive types representing future values with backpressure support. WebFlux follows the **Reactive Streams** specification (`Publisher`, `Subscriber`, `Subscription`, `Processor`).

---

### 🟢 Simple Definition (Easy)

WebFlux is Spring's non-blocking web framework. Instead of a thread waiting for each database call to finish, WebFlux frees that thread to handle other requests while waiting — allowing fewer threads to handle many more concurrent connections.

---

### 🔵 Simple Definition (Elaborated)

Traditional Spring MVC allocates one thread per HTTP request. If that request waits 200ms for a database query, the thread is blocked and unavailable for other work. At 1,000 concurrent requests: 1,000 threads — each consuming 1MB stack = 1GB RAM just for threads. WebFlux breaks this: I/O is non-blocking, so a thread submits the database query and returns to the event loop immediately. When the query completes (event fires), the same or another thread resumes processing. Result: 10–20 event-loop threads handle thousands of concurrent requests.

---

### 🔩 First Principles Explanation

**The thread-per-request problem:**

```
Spring MVC thread model:
  1 HTTP request → 1 thread blocked for entire duration
  thread 1: waiting for DB        (200ms blocked)
  thread 2: waiting for Redis     (15ms blocked)
  thread n: waiting for HTTP call (500ms blocked)

  300 concurrent users × (1 thread × 1MB stack) = 300MB
  Tomcat default max threads = 200
  201st user: queue → latency spike

WebFlux event-loop model:
  1 - N HTTP requests → event loop (2-8 threads)
  All I/O non-blocking: submit call → thread freed
  DB completes → event fires → next handler scheduled
  10,000 connections, 8 event-loop threads
  Cost: reactive programming model complexity
```

**Reactive Streams protocol:**

```
┌─────────────────────────────────────────────────────┐
│  REACTIVE STREAMS HANDSHAKE                         │
│                                                     │
│  Publisher (data source)                            │
│    ↓ subscriber.onSubscribe(subscription)           │
│  Subscriber (data consumer)                         │
│    ↓ subscription.request(n) ← BACKPRESSURE         │
│  Publisher emits ≤ n items                          │
│    ↓ subscriber.onNext(item) × n                    │
│    ↓ subscriber.onComplete()  (or onError)          │
│                                                     │
│  Backpressure: consumer controls production rate    │
│  "Send me only as fast as I can process"            │
└─────────────────────────────────────────────────────┘
```

---

### ❓ Why Does This Exist (Why Before What)

**WITHOUT WebFlux:**

```
Spring MVC under high concurrency:

  10,000 concurrent HTTP requests:
    Tomcat maxThreads default: 200
    → 9,800 requests queued
    → Latency: 9,800 / 200 × avg_service_time

  Microservice calling 5 downstream services:
    5 × 100ms sequential = 500ms total
    Each call: thread blocked waiting
    5 threads held per request × 1,000 users = 5,000 threads

  Streaming large files:
    1 thread for entire file transfer
    → Thread exhaustion during large uploads/downloads
```

**WITH WebFlux:**

```
→ 10,000 concurrent connections on 8 event-loop threads
→ Memory: 8 × 1MB thread stack vs. 10,000 × 1MB
→ Parallel HTTP calls: zip(call1, call2, call3) = max latency
  not 300ms + 300ms + 300ms = 100ms parallel
→ SSE / WebSocket streaming: single connection, many events
→ Backpressure: consumer controls stream rate
→ R2DBC: reactive database access (no blocking JDBC)
```

---

### 🧠 Mental Model / Analogy

> WebFlux is like a **single barista serving 200 customers** using an espresso machine timer instead of waiting. Traditional MVC: one barista per customer — barista stands idle while espresso pulls (2 minutes). WebFlux: one barista starts espresso for customer 1, immediately takes customer 2's order, starts their espresso, takes customer 3's — then checks the timer and serves espresso in order as they finish. Same person, 200× more capacity, but must manage multiple tasks simultaneously (reactive complexity).

"One barista waiting per customer" = thread-per-request blocking model
"Barista checking the timer" = event loop checking I/O completion
"Multiple simultaneous espressos" = multiple concurrent non-blocking I/O
"Managing order sequencing" = reactive operator chaining
"Barista confusion with too many orders" = blocking code in reactive pipeline

---

### ⚙️ How It Works (Mechanism)

**WebFlux annotated controller:**

```java
@RestController
@RequestMapping("/api/orders")
public class OrderController {
  private final OrderService orderService;
  private final InventoryClient inventoryClient;

  // Returns immediately — Mono is a Future, not the value
  @GetMapping("/{id}")
  public Mono<Order> getOrder(@PathVariable String id) {
    return orderService.findById(id);  // non-blocking
  }

  // Parallel calls: zip waits for BOTH to complete
  @PostMapping
  public Mono<OrderConfirmation> placeOrder(
      @RequestBody Mono<OrderRequest> request) {
    return request.flatMap(req ->
        Mono.zip(
            inventoryClient.checkStock(req.getProductId()),
            orderService.calculatePrice(req)
        ).flatMap(tuple -> {
          Stock stock   = tuple.getT1();
          Price price   = tuple.getT2();
          return orderService.create(req, stock, price);
        })
    );
  }

  // Streaming responses (SSE)
  @GetMapping(value = "/events",
              produces = MediaType.TEXT_EVENT_STREAM_VALUE)
  public Flux<OrderEvent> orderEvents() {
    return orderService.liveOrderStream()
        .delayElements(Duration.ofMillis(500));
  }
}
```

**Composing reactive pipelines:**

```java
@Service
public class OrderService {
  private final R2dbcOrderRepository orderRepo;
  private final ReactiveRedisTemplate<String, Order> redis;

  public Mono<Order> findById(String id) {
    return redis.opsForValue().get("order:" + id)
        .switchIfEmpty(                    // cache miss
            orderRepo.findById(id)         // DB lookup (R2DBC)
                .doOnNext(order ->         // populate cache
                    redis.opsForValue()
                         .set("order:" + id, order)
                         .subscribe())
        )
        .switchIfEmpty(Mono.error(         // not found
            new OrderNotFoundException(id)));
  }
}
```

---

### 🔄 How It Connects (Mini-Map)

```
HTTP request arrives at Netty event loop
        ↓
  WEBFLUX / REACTIVE (136)  ← you are here
  (DispatcherHandler — reactive equivalent of DS)
        ↓
  RouterFunctions or @RequestMapping
        ↓
  Handlers return Mono<T> / Flux<T>
        ↓
  Reactor schedules on event-loop threads
  Non-blocking I/O: R2DBC, WebClient, Redis
        ↓
  Mono (137) — 0 or 1 value asynchronously
  Flux (137) — 0-N values as stream
  Backpressure (138) — consumer controls rate
        ↓
  vs Spring MVC:
  Thread-per-request → WebFlux non-blocking
```

---

### 💻 Code Example

**Example 1 — WebClient for non-blocking HTTP calls:**

```java
// WebClient: non-blocking HTTP (WebFlux equivalent of RestTemplate)
@Service
public class ProductClient {
  private final WebClient webClient;

  public ProductClient(WebClient.Builder builder) {
    this.webClient = builder
        .baseUrl("https://catalog-service")
        .defaultHeader("Accept", "application/json")
        .build();
  }

  public Mono<Product> getProduct(String id) {
    return webClient.get()
        .uri("/products/{id}", id)
        .retrieve()
        .onStatus(HttpStatusCode::is4xxClientError,
            resp -> Mono.error(new ProductNotFoundException(id)))
        .bodyToMono(Product.class)
        .timeout(Duration.ofSeconds(3))
        .retryWhen(Retry.backoff(3, Duration.ofMillis(200)));
  }

  public Flux<Product> getAllProducts() {
    return webClient.get()
        .uri("/products")
        .retrieve()
        .bodyToFlux(Product.class);
  }
}
```

**Example 2 — NEVER block in WebFlux:**

```java
// CATASTROPHIC: blocking inside reactive pipeline
@GetMapping("/orders/{id}")
public Mono<Order> getOrder(@PathVariable String id) {
  // BAD: .block() inside Mono pipeline
  // Blocks the event-loop thread → defeats entire purpose
  Order order = legacyService.findOrder(id).block();
  return Mono.just(order);

  // ALSO BAD: any blocking I/O
  String result = Files.readString(Path.of("/data/order.json"));
  Thread.sleep(100); // NEVER in reactive code!

  // GOOD: wrap blocking calls in separate scheduler
  return Mono.fromCallable(() -> legacyService.findOrderSync(id))
      .subscribeOn(Schedulers.boundedElastic()); // offload to bounded pool
}
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| WebFlux is always faster than Spring MVC | WebFlux wins under HIGH concurrency with I/O-bound workloads. For low-concurrency or CPU-bound work, Spring MVC's simpler model is equally fast and easier to reason about |
| @Transactional works in WebFlux just like in MVC | @Transactional with `JpaTransactionManager` is ThreadLocal-based — incompatible with reactive. WebFlux requires R2DBC + `ReactiveTransactionManager` for transactions |
| You can use JPA/JDBC in WebFlux | JDBC is blocking. Using JPA in WebFlux without offloading to `boundedElastic` scheduler blocks the event-loop threads and can cause request starvation |
| WebFlux eliminates the need for async design | WebFlux requires ALL code in the pipeline to be non-blocking. One blocking call in the chain blocks the event-loop thread and negates the concurrency benefit |

---

### 🔥 Pitfalls in Production

**1. Accidentally blocking the event loop**

```java
// BAD: JPA/JDBC call directly in reactive handler
@GetMapping("/orders/{id}")
public Mono<OrderDto> getOrder(@PathVariable Long id) {
  // jpaRepo.findById() is BLOCKING JDBC
  // Called on Netty event-loop thread → BLOCKS IT
  return Mono.just(jpaRepo.findById(id).orElseThrow());
  // All other requests on this thread stall!
}

// GOOD: offload to boundedElastic scheduler
return Mono.fromCallable(() -> jpaRepo.findById(id)
                                      .orElseThrow())
           .subscribeOn(Schedulers.boundedElastic());
// OR: migrate to R2DBC for true reactive DB access
```

**2. Not subscribing — nothing executes**

```java
// BAD: Mono created but never subscribed
// → database query NEVER runs!
@PostMapping("/orders")
public void placeOrder(@RequestBody OrderRequest req) {
  orderService.save(req); // Mono returned — but never subscribed!
  // void return: framework doesn't subscribe → NO-OP
}

// GOOD: return the Mono — framework subscribes
@PostMapping("/orders")
public Mono<Order> placeOrder(@RequestBody Mono<OrderRequest> req) {
  return req.flatMap(orderService::save);
  // WebFlux subscribes to the returned Mono
}
```

---

### 🔗 Related Keywords

- `Mono` — Project Reactor type for 0 or 1 asynchronous value
- `Flux` — Project Reactor type for 0 to N asynchronous values
- `Backpressure` — the mechanism consumers use to control production rate
- `Event Loop` — the threading model underlying reactive I/O (like Node.js)
- `R2DBC` — Reactive Relational Database Connectivity (non-blocking JDBC)
- `WebClient` — Spring's non-blocking HTTP client (replaces RestTemplate in reactive apps)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Non-blocking event-loop model — few       │
│              │ threads handle many concurrent I/O-bound  │
│              │ requests via Mono/Flux pipelines          │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ High concurrency, I/O-bound workloads,    │
│              │ streaming, microservice fan-out           │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ CPU-bound work, blocking libraries (JPA), │
│              │ teams unfamiliar with reactive semantics  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "One barista, 200 espressos —             │
│              │  don't wait at the machine."              │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Mono / Flux (137) → Backpressure (138) →  │
│              │ R2DBC → Reactor debugging                 │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** WebFlux uses `Schedulers.boundedElastic()` for blocking I/O operations within a reactive pipeline. `boundedElastic` has a maximum thread count (default: 10× CPU cores) and a maximum queue. Describe the failure mode when 1,000 concurrent requests each call a blocking JDBC operation offloaded to `boundedElastic`, the pool reaches maximum threads, and the queue fills: what exception is thrown, what happens to the in-flight Mono, and how does this differ from HikariCP connection pool exhaustion in terms of where the failure surface appears.

**Q2.** Reactor's `Mono.zip()` combines multiple publishers and emits when all complete. If one of the zipped Monos never completes (hangs indefinitely), `zip()` will also hang indefinitely — no timeout is applied automatically. Describe the full diagnostic sequence for a production WebFlux endpoint that intermittently hangs: how would you identify which Mono in the zip is hanging using Reactor's `checkpoint()` operator and Reactor Debug Agent, what JVM tooling can show Netty event-loop thread states, and how to apply `timeout()` defensively to each upstream Mono.

