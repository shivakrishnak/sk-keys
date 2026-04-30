---
layout: default
title: "Mono / Flux"
parent: "Spring Core"
nav_order: 405
permalink: /spring/mono-flux/
number: "405"
category: Spring Core
difficulty: ★★☆
depends_on: "WebFlux, Reactive Streams, Project Reactor, Non-blocking I/O"
used_by: "WebFlux controllers, WebClient, R2DBC, reactive service layer"
tags: #java, #spring, #intermediate, #performance
---

# 405 — Mono / Flux

`#java` `#spring` `#intermediate` `#performance`

⚡ TL;DR — Project Reactor's two types for async, non-blocking data: `Mono<T>` for 0 or 1 item, `Flux<T>` for 0 to N items — lazy pipelines that produce values only when subscribed.

| #405 | category: Spring Core
|:---|:---|:---|
| **Depends on:** | WebFlux, Reactive Streams, Project Reactor, Non-blocking I/O | |
| **Used by:** | WebFlux controllers, WebClient, R2DBC, reactive service layer | |

---

### 📘 Textbook Definition

**`Mono<T>`** and **`Flux<T>`** are Project Reactor's core reactive types implementing the Reactive Streams `Publisher<T>` specification. `Mono<T>` emits at most one item, then completes or errors. `Flux<T>` emits zero to N items, then completes or errors. Both are **cold publishers by default** — the pipeline is not executed until a subscriber subscribes. Operators such as `map`, `flatMap`, `filter`, `zip`, `switchIfEmpty`, `onErrorResume`, and `retryWhen` compose pipelines lazily. Backpressure is controlled via `Subscription.request(n)`. In Spring WebFlux, controller methods return `Mono<T>` or `Flux<T>` — WebFlux subscribes and streams the response.

---

### 🟢 Simple Definition (Easy)

`Mono` is a box that will contain zero or one item in the future. `Flux` is a stream that will produce zero or many items over time. Nothing actually runs until something subscribes to them.

---

### 🔵 Simple Definition (Elaborated)

`Mono` and `Flux` are like pipelines with all the valves closed — defining all the processing steps (transform, filter, fallback) before any data flows. The pipeline is assembled and then "subscribed to," which opens the first valve and lets data flow through. `Mono.just("hello").map(String::toUpperCase)` is just a description of work until `.subscribe()` executes it. This lazy evaluation is what allows WebFlux to chain network calls, transformations, and error handlers without blocking threads — each step fires only when the previous data arrives.

---

### 🔩 First Principles Explanation

**Cold vs hot publishers:**

```
COLD publisher (Mono/Flux default):
  Each subscriber triggers a new execution
  orderRepo.findById(id) → new DB query per subscriber
  Like a video recording: each viewer plays from start

HOT publisher (Subjects, Sinks):
  Emits regardless of subscribers; late subscribers
  miss past items (unless replayed)
  Like a live TV broadcast: join late → miss what happened

Most Reactor pipelines are COLD — safe by default
```

**Assembly time vs subscription time:**

```java
// ASSEMBLY TIME: operators are chained (no DB query yet)
Mono<Order> pipeline = orderRepo.findById(42L)
    .map(Order::summarise)
    .doOnNext(s -> log.info("Got: {}", s))
    .onErrorResume(e -> Mono.just(Order.empty()));

// Nothing has happened. No DB call. Just a description.

// SUBSCRIPTION TIME: execution begins
pipeline.subscribe(
    order  -> sendResponse(order),     // onNext
    error  -> sendError(error),        // onError
    ()     -> log.info("complete")    // onComplete
);
// NOW the DB query fires.
// WebFlux calls subscribe() automatically for you.
```

---

### ❓ Why Does This Exist (Why Before What)

**WITHOUT Mono/Flux (callback hell):**

```java
// Traditional async callbacks — nested, unreadable:
orderService.findById(id, order -> {
  inventoryService.checkStock(order.getProductId(),
      stock -> {
        if (stock > 0) {
          paymentService.charge(order, payment -> {
            notificationService.notify(order, notification -> {
              // Pyramid of doom: 4 levels deep
              // Error handling duplicated at each level
            }, error -> handle(error));
          }, error -> handle(error));
        }
      }, error -> handle(error));
}, error -> handle(error));
```

**WITH Mono/Flux (linear, composable):**

```java
Mono<Confirmation> confirmed =
    orderService.findById(id)
        .zipWith(inventoryService.checkStock(productId))
        .filter(tuple -> tuple.getT2() > 0)
        .flatMap(tuple -> paymentService.charge(
            tuple.getT1()))
        .flatMap(payment -> notificationService.notify(
            payment.getOrderId()))
        .onErrorResume(PaymentException.class,
            e -> Mono.just(Confirmation.pending()));
// Linear, composable, single error handler,
// parallel calls via zip — readable
```

---

### 🧠 Mental Model / Analogy

> `Mono` is a **sealed FedEx envelope** — it will contain one document (or be empty, or report delivery failure). `Flux` is a **conveyor belt from a warehouse** — items arrive one by one, the belt runs at the speed the receiver requests (backpressure). Both are the DESCRIPTION of the delivery, not the delivery itself. FedEx starts delivering only when you place the order (subscribe). You can attach processing steps to the conveyor belt before it moves: sort, filter, repackage — all lazy until the belt starts.

"Sealed FedEx envelope" = Mono (0 or 1 item)
"Conveyor belt from warehouse" = Flux (0-N items)
"Description before FedEx starts" = assembly time (lazy)
"Placing the order" = subscribe() (subscription time)
"Processing steps on the belt" = map, filter, flatMap operators
"Belt speed" = backpressure (request(n))

---

### ⚙️ How It Works (Mechanism)

**Most commonly used operators:**

```java
// MONO OPERATORS
Mono<String> m = Mono.just("hello");

m.map(s -> s.toUpperCase());           // sync transform
m.flatMap(s -> dbRepo.findByName(s));  // async transform (returns Mono)
m.filter(s -> s.length() > 3);        // emits empty if predicate fails
m.defaultIfEmpty("default");           // value if empty
m.switchIfEmpty(Mono.just("fallback")); // publisher if empty
m.onErrorResume(e -> Mono.just("err")); // recover on error
m.timeout(Duration.ofSeconds(3));      // error if no item in 3s
m.retry(3);                            // retry on error up to 3 times
m.doOnNext(s -> log.info(s));         // side-effect (doesn't alter value)
m.doOnError(e -> metrics.increment()); // side-effect on error
m.subscribeOn(Schedulers.boundedElastic()); // thread for subscription

// FLUX OPERATORS (all Mono operators + collection ops)
Flux<Integer> f = Flux.range(1, 10);
f.filter(n -> n % 2 == 0);            // [2,4,6,8,10]
f.map(n -> n * 2);                     // transform each
f.take(3);                             // first 3 items only
f.skip(2);                             // skip first 2
f.buffer(3);                           // emit List<Integer> in batches of 3
f.collectList();                       // Mono<List<Integer>> when done
f.reduce(0, Integer::sum);             // Mono<Integer> accumulated
f.flatMap(n -> dbRepo.findById(n));    // async expand each element
f.concatMap(n -> dbRepo.findById(n));  // async, order-preserving
f.zipWith(Flux.range(10, 10));         // combine two Fluxes pair-wise
f.onBackpressureDrop();               // drop if consumer too slow
```

**Mono.zip for parallel calls:**

```java
// Call services in PARALLEL, combine results
Mono<OrderSummary> summary = Mono.zip(
    userService.findById(userId),           // call 1
    inventoryService.getStock(productId),   // call 2 (concurrent)
    pricingService.getPrice(productId)      // call 3 (concurrent)
).map(tuple -> new OrderSummary(
    tuple.getT1(), tuple.getT2(), tuple.getT3()
));
// Total time = max(call1, call2, call3) not sum
// e.g. max(50ms, 80ms, 30ms) = 80ms vs 160ms sequential
```

---

### 🔄 How It Connects (Mini-Map)

```
Reactive Streams Publisher<T> spec
        ↓
  MONO / FLUX (137)  ← you are here
  (Project Reactor implementations)
        ↓
  Operators compose lazy pipelines:
  map, flatMap, filter, zip, onError
        ↓
  Consumed by:
  WebFlux controllers (return Mono/Flux)
  WebClient (returns Mono/Flux)
  R2DBC repositories (return Mono/Flux)
        ↓
  Backpressure (138):
  Subscription.request(n) controls emission rate
        ↓
  Execution on:
  Netty event-loop / Schedulers.boundedElastic()
```

---

### 💻 Code Example

**Example 1 — Cache-aside pattern with Mono:**

```java
@Service
class ProductService {
  private final R2dbcProductRepository dbRepo;
  private final ReactiveRedisTemplate<String, Product> redis;

  public Mono<Product> findById(String id) {
    String cacheKey = "product:" + id;

    return redis.opsForValue().get(cacheKey)
        .doOnNext(p -> log.debug("Cache hit: {}", id))
        .switchIfEmpty(                   // cache miss
            dbRepo.findById(id)
                .switchIfEmpty(Mono.error(
                    new ProductNotFoundException(id)))
                .flatMap(product ->       // cache + return
                    redis.opsForValue()
                         .set(cacheKey, product,
                              Duration.ofMinutes(15))
                         .thenReturn(product))
        );
  }
}
```

**Example 2 — Flux for streaming large result sets:**

```java
@GetMapping(value = "/products/export",
            produces = MediaType.APPLICATION_NDJSON_VALUE)
public Flux<Product> exportProducts() {
  return r2dbcRepo.findAll()  // R2DBC streams rows reactively
      .filter(Product::isActive)
      .map(productMapper::toDto)
      .delayElements(Duration.ofMillis(1))  // rate limiting
      .doOnError(e -> log.error("Export error", e));
  // Client receives newline-delimited JSON as rows stream in
  // No need to load all products into memory
}
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Mono/Flux execute when created | Both are COLD publishers — nothing executes until subscribed. Just creating a Mono.just("x").map(...) chain does zero work |
| flatMap and map are interchangeable | map applies a sync function returning T; flatMap applies an async function returning Mono<T>/Flux<T>. Using map when the function returns a Mono gives Mono<Mono<T>> — a wrapped type |
| Mono<Void> means the operation succeeded | Mono<Void> completes when the underlying operation finishes. An empty Mono<Void> means completion with no result — NOT that nothing happened |
| .subscribe() is always needed | In WebFlux controllers, the framework subscribes to the returned Mono/Flux. Calling .subscribe() manually in a handler creates an extra uncoupled subscription — a double-execution bug |

---

### 🔥 Pitfalls in Production

**1. map returning Mono creates Mono<Mono<T>>**

```java
// BAD: map with async function → Mono<Mono<Order>>
Mono<Mono<Order>> wrong = orderId.map(id ->
    orderRepo.findById(id)  // returns Mono<Order>
);
// wrong.subscribe(inner -> inner.subscribe(...)) — nested!

// GOOD: flatMap unwraps the inner Mono
Mono<Order> correct = orderId.flatMap(id ->
    orderRepo.findById(id)  // flatMap unwraps Mono<Order>
);
```

**2. Ignoring the return value — silent no-op**

```java
// BAD: reactive call result discarded
@PostMapping("/orders")
public void placeOrder(@RequestBody OrderRequest req) {
  orderService.save(req); // Mono returned but IGNORED
  // Nothing executes! No subscription → no DB write!
}
// No error, no log, silent data loss.

// GOOD: return or subscribe explicitly
@PostMapping("/orders")
public Mono<ResponseEntity<Order>> placeOrder(
    @RequestBody Mono<OrderRequest> req) {
  return req.flatMap(orderService::save)
            .map(order -> ResponseEntity.ok(order));
}
```

---

### 🔗 Related Keywords

- `WebFlux` — the framework that consumes Mono/Flux from controller methods
- `Backpressure` — the mechanism for controlling Flux emission rate via request(n)
- `Project Reactor` — the library providing Mono, Flux, and all operators
- `WebClient` — Spring's HTTP client returning Mono/Flux
- `R2DBC` — reactive database driver returning Mono/Flux from queries
- `Reactive Streams` — the specification Mono/Flux implement (Publisher<T>)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Mono = async 0-1 item; Flux = async 0-N;  │
│              │ both lazy — execute only on subscribe     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Mono: single async result (DB, HTTP call) │
│              │ Flux: streams, collections, paginated data│
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Blocking I/O inside map/flatMap without   │
│              │ subscribeOn(boundedElastic)               │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Mono is a sealed envelope; Flux is a     │
│              │  conveyor belt — nothing moves until you  │
│              │  place the order."                        │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Backpressure (138) → Project Reactor docs │
│              │ → R2DBC → Reactive debugging              │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** `Flux.flatMap()` subscribes to inner publishers concurrently (up to `concurrency` parameter, defaulting to 256 parallel inner subscriptions). `Flux.concatMap()` subscribes to each inner publisher one at a time, preserving order. For a Flux of 10,000 user IDs that each require a database lookup, describe the performance and ordering trade-offs between using `flatMap(concurrency=50)` vs `concatMap()` — and explain the specific failure mode where `flatMap` with default concurrency=256 causes database connection pool exhaustion on a pool of 20.

**Q2.** Reactor's `StepVerifier` is the testing utility for reactive pipelines. A developer writes a test using `StepVerifier.create(mono).expectNext("expected").verifyComplete()` — but the test passes even when the underlying mock returns an incorrect value. Explain why this can happen — specifically how Reactor's `StepVerifier` interacts with cold vs hot publishers, and what happens if the mock returns a `Mono.empty()` when the test expects `expectNext("expected")` followed by `verifyComplete()`.

