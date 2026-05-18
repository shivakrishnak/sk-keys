---
id: SPR-043
title: "Spring Reactive Model (Project Reactor Internals)"
category: Spring Core
tier: tier-3-java
folder: SPR-spring-core
difficulty: ★★★
depends_on: SPR-028, SPR-029, SPR-074, SPR-060
used_by:
related: SPR-082, SPR-084, SPR-010
tags:
  - spring
  - java
  - advanced
  - deep-dive
  - internals
  - first-principles
status: complete
version: 2
layout: default
parent: "Spring Core"
grand_parent: "Technical Mastery"
nav_order: 83
permalink: /technical-mastery/spr/spring-reactive-model-project-reactor-internals/
---

⚡ TL;DR - A Reactor `Flux` or `Mono` is an immutable declaration of computation; nothing executes until `subscribe()` is called, at which point the operator chain assembles and data flows upstream-to-downstream through callbacks.

| Field          | Value                                                                                                                                                                   |
| -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Depends on** | [[SPR-028 - WebFlux Introduction]], [[SPR-029 - Reactive Streams Specification]], [[SPR-074 - Flux and Mono]], [[SPR-060 - Spring Migration Strategy (MVC to WebFlux)]] |
| **Used by**    | -                                                                                                                                                                       |
| **Related**    | [[SPR-082 - Spring Framework Internals Deep Dive]], [[SPR-084 - Spring Native and GraalVM Integration]], [[SPR-010 - Spring WebFlux vs Virtual Threads]]                |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**

Asynchronous Java before Reactor: `CompletableFuture` chains are hard to compose, have no backpressure, and consume a thread from a pool per stage. Callback-based code creates deep nesting. RxJava is an option but is not integrated with the Spring ecosystem. Raw Reactive Streams is too low-level for application developers.

**THE BREAKING POINT:**

An API aggregation service calls 5 downstream services. With `RestTemplate` (blocking), 5 threads are blocked waiting. Under load, the thread pool exhausts. With `CompletableFuture`, the composition is complex and no backpressure mechanism prevents fast producers from overwhelming slow consumers.

**THE INVENTION MOMENT:**

Project Reactor (2016) provided a Reactive Streams implementation that is: composable (operator chain), lazy (nothing runs until subscribe), backpressure-aware (demand flows upstream), and integrated with Spring's event loop model (Netty via WebFlux).

**EVOLUTION:**

- **2013:** Reactive Streams specification published (Publisher/Subscriber/Subscription/Processor)
- **2015:** Project Reactor 2.0 - first Pivotal implementation
- **2016:** Reactor 3.0 - Java 8, `Flux`/`Mono`, full Reactive Streams compliance
- **2017:** Spring WebFlux built on Reactor 3; Spring Data Reactive (R2DBC, MongoDB, Redis)
- **2022:** Reactor 3.5 - virtual thread scheduler; `Flux.parallel()` enhancements
- **2023:** Project Loom virtual threads as an alternative to reactive for I/O concurrency

---

### 📘 Textbook Definition

**Project Reactor** is a Reactive Streams implementation providing two publisher types: `Mono<T>` (0-1 items) and `Flux<T>` (0-N items). Both are **cold publishers** by default: declaring a `Flux` does not start any computation. **Subscription** (calling `.subscribe()`, or implicitly in Spring WebFlux by returning `Mono`/`Flux` from a controller) triggers the **assembly** of the operator chain and begins requesting data upstream. **Backpressure** flows as demand signals from subscriber to publisher through `Subscription.request(n)` - the publisher emits at most `n` items before the subscriber must request more.

---

### ⏱️ Understand It in 30 Seconds

**One line:** A `Flux` is a lazy pipeline blueprint; `subscribe()` is the "build and run" button that connects source to sink and starts data flowing.

> Reactor is like a water pipe system that does not contain water until you open the tap. Declaring a `Flux` is building the pipe network (cold, empty). `subscribe()` is opening the tap. Backpressure is the mechanism that prevents a firehose source from flooding a straw-sized sink - the sink controls how fast water flows by signalling demand.

**One insight:** Every Reactor operator returns a new `Publisher` wrapping the upstream. Nothing is mutable. The chain is an immutable transformation graph - subscribe is what traverses and executes it.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. `Publisher` produces items; `Subscriber` consumes them; `Subscription` mediates demand
2. A publisher MUST NOT emit more items than requested via `Subscription.request(n)`
3. `onNext` × n → `onComplete` | `onError` - a stream terminates with exactly one terminal signal
4. A cold publisher creates a new, independent data source per subscriber
5. A hot publisher shares a single source across all subscribers

**DERIVED DESIGN:**

From invariant 2 → backpressure is not optional; every operator in the chain must honour demand. `Flux.buffer()` and `Flux.limitRate()` exist to adapt demand between fast producers and slow consumers.
From invariant 3 → operator fusion: adjacent operators that can be combined (e.g., `map().filter()`) are fused into a single `ConditionalSubscriber` to avoid intermediate object allocation.
From invariant 4 → `Flux.fromIterable()`, `Mono.fromCallable()` are cold - safe to share as a builder pattern.
From invariant 5 → `Sinks.many().multicast()` is hot - emits to whoever is subscribed at emission time.

**THE TRADE-OFFS:**

**Gain:** Non-blocking I/O with a small thread count; composable async operations; backpressure prevents resource exhaustion; excellent debuggability via `log()` operator.

**Cost:** Steep learning curve; stack traces are unhelpful (operator chain obscures origin); blocking calls in a reactive chain cause event loop starvation; debugging requires `checkpoint()` annotations.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

**Essential:** Asynchronous composition, backpressure, and error handling in a pipeline model are inherently complex.

**Accidental:** Reactor's assembly-time vs subscription-time distinction confuses developers initially. The rule is mechanical: any side effect in a `.map()` or `flatMap()` function runs at subscription time, not at the time the chain is declared.

---

### 🧪 Thought Experiment

**SETUP:** `Flux.range(1, 1_000_000)` piped to a slow subscriber that can only process 10 items per second.

**WITHOUT backpressure (no Reactive Streams):**

The publisher emits all 1,000,000 items immediately. The subscriber's internal buffer fills. Memory explodes. `OutOfMemoryError` or extreme GC pressure.

**WITH Reactor backpressure:**

Subscriber calls `request(10)`. Publisher emits exactly 10 items. Subscriber processes 10, then calls `request(10)` again. Publisher emits 10 more. The buffer never grows beyond 10 items. Memory is bounded regardless of source size.

**Changing the setup:**

Add `Flux.range(1, 1_000_000).onBackpressureBuffer(100)`. The buffer holds up to 100 items; if the subscriber is slower than the source and the buffer fills, `OverflowException` signals the overload condition explicitly rather than silently crashing.

**THE INSIGHT:**

Backpressure converts an implicit crash (OOM) into an explicit signal (`OverflowException`, `DROP`, `LATEST` strategies). The developer chooses the overload handling strategy; it is not decided by the JVM heap.

---

### 🧠 Mental Model / Analogy

> Project Reactor is like an assembly line in a factory. `Flux` is the conveyor belt design specification (blueprint, not running). Each operator (`.map()`, `.filter()`, `.flatMap()`) is a workstation added to the blueprint. `.subscribe()` starts the line. Backpressure is the buffer size between stations - if Station C is slow, it signals Station B to slow down via a production quota (`request(n)`), preventing the in-between buffer from overflowing. Hot publishers are like a news ticker (broadcasts to whoever is watching regardless of who joined when); cold publishers are like a video-on-demand stream (each viewer starts from the beginning).

**Element mapping:**

- Conveyor belt blueprint → `Flux`/`Mono` declaration
- Starting the line → `.subscribe()`
- Workstation → operator (`.map()`, `.filter()`)
- Production quota → `Subscription.request(n)`
- Buffer between stations → internal operator queue
- News ticker → hot `Sink`
- Video on demand → cold `Flux.fromIterable()`

Where this analogy breaks down: in Reactor, items can be transformed, merged, and split in ways a physical conveyor belt cannot support - `flatMap()` starts a new inner `Flux` per item, creating parallel sub-streams.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Reactor lets you describe a multi-step data transformation that runs without blocking threads. You declare the steps, then start it. Data flows through the steps when ready, and the system can handle millions of items without creating millions of threads.

**Level 2 - How to use it (junior developer):**
`Mono.fromCallable(() -> fetchUser(id))` declares an async fetch. `.map(user -> user.name())` transforms the result. `.subscribe(name -> log(name))` starts it. For HTTP: return `Mono<ResponseEntity<User>>` from a `@RestController` - WebFlux calls `subscribe()` for you. Add `.log()` before `.subscribe()` to trace all signals.

**Level 3 - How it works (mid-level engineer):**
Assembly phase: each operator call returns a new `Publisher` object wrapping the upstream operator. The chain is a linked list of publishers. Subscription phase: `subscribe()` traverses the chain from tail to head, creating a `Subscriber` for each operator and calling `onSubscribe()` upward. The source `Publisher` receives the assembled chain and begins emitting via `request(n)`. Data flows downstream through each operator's `onNext()`. Error propagates via `onError()`. `flatMap()` subscribes to each inner publisher concurrently (default 256 inner subscriptions) and merges their outputs.

**Level 4 - Why it was designed this way (senior/staff):**
Reactor's cold publisher model means that every subscription gets its own data source, which is critical for WebFlux request handling: each HTTP request subscribes to the controller's returned `Mono`/`Flux` - no shared mutable state between requests. The operator fusion mechanism (introduced in Reactor 3.1) merges synchronous operator chains into a single loop, eliminating intermediate object allocation for chains like `map().filter().map()`. This is why Reactor benchmarks favourably against alternatives - it is not just a design pattern, it is optimised for JVM object allocation reduction.

**Expert Thinking Cues:**

- `publishOn()` switches the execution thread downstream; `subscribeOn()` switches the source emission thread
- `flatMap()` is concurrent (unordered); `concatMap()` is sequential (ordered); `flatMapSequential()` is concurrent but re-orders output
- `Hooks.onOperatorDebug()` enables assembly-time stack traces - essential for debugging but adds cost to every operator assembly

---

### ⚙️ How It Works (Mechanism)

```
Assembly phase (code execution):
  Flux.fromIterable(list)        <- Source Publisher
    .filter(x -> x > 0)         <- FilterSubscriber
    .map(x -> x * 2)            <- MapSubscriber
    .take(10)                   <- TakeSubscriber
    .subscribe(consumer)        <- Actual Subscriber

Subscription phase (subscribe() called):
  Actual Subscriber.onSubscribe(TakeSubscription)
  TakeSubscription → request(Long.MAX_VALUE)
    → MapSubscription → request(MAX)
      → FilterSubscription → request(MAX)
        → IterableSubscription → request(MAX)
          → emits items one by one

Data flow (downstream):
  IterableSubscription.onNext(item)
    → FilterSubscriber.onNext(item)    [drop if <0]
      → MapSubscriber.onNext(filtered) [x * 2]
        → TakeSubscriber.onNext(mapped) [count to 10]
          → Actual Subscriber.onNext(final)
              [consumer processes item]
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
[HTTP Request arrives at Netty]
     |
     ├─ Netty event loop thread
     |    ├─ Route to @RestController
     |    └─ Controller returns Mono<Response>
     |         ← YOU ARE HERE (assembly complete)
     |
     ├─ WebFlux subscribes to Mono
     |    ├─ flatMap → DB query (R2DBC)
     |    |    └─ subscribeOn(Schedulers.parallel())
     |    └─ map → transform result
     |
     ├─ R2DBC emits result on its thread
     |    └─ publishOn(Schedulers.boundedElastic())
     |
[HTTP Response written to Netty channel]
```

**FAILURE PATH:**

- Blocking call in reactive chain → `BlockingOperationError` (if `BlockHound` enabled) or event loop starvation
- `flatMap` inner publisher throws → `onError` propagates to root; subscriber's error handler invoked
- Unsubscribed publisher → no computation, no side effects (silent failure if `.subscribe()` is forgotten)

**WHAT CHANGES AT SCALE:**

Under high load, `Schedulers.boundedElastic()` thread pool bounds prevent unbounded thread creation. `limitRate(prefetch)` controls how many items are requested at once, reducing buffer memory under high throughput. Hot sources (Kafka consumer via `reactor-kafka`) use `Sinks` to bridge imperative Kafka callbacks to reactive subscribers.

**CONCURRENCY & DISTRIBUTED IMPLICATIONS:**

`Mono.zip()` subscribes to multiple publishers concurrently and combines their results. This is the safe pattern for parallel I/O calls (unlike `CompletableFuture.allOf()`, it is fully backpressure-aware). `Context` (Reactor's equivalent of `ThreadLocal`) propagates correlation IDs and security context through the async chain without thread binding.

---

### 💻 Code Example

**BAD - blocking call inside reactive chain stalls event loop:**

```java
@GetMapping("/order/{id}")
public Mono<Order> getOrder(@PathVariable Long id) {
    return Mono.just(id)
        .map(orderId -> {
            // BLOCKS the event loop thread!
            // RestTemplate is synchronous
            return restTemplate.getForObject(
                "/items/" + orderId, Item.class);
        });
}
```

**GOOD - non-blocking WebClient with proper scheduler use:**

```java
@GetMapping("/order/{id}")
public Mono<Order> getOrder(@PathVariable Long id) {
    return orderRepository.findById(id)  // R2DBC
        .flatMap(order ->
            webClient.get()
                .uri("/items/{id}", order.itemId())
                .retrieve()
                .bodyToMono(Item.class)
                .map(item ->
                    order.withItem(item))
        )
        .switchIfEmpty(
            Mono.error(new NotFoundException(id))
        );
}
```

**Parallel I/O with `Mono.zip()`:**

```java
public Mono<OrderSummary> buildSummary(
        Long orderId) {
    Mono<Order> order =
        orderRepository.findById(orderId);
    Mono<User> user =
        userService.getCurrentUser();
    Mono<Price> price =
        priceService.getPrice(orderId);

    // All three subscribed concurrently
    return Mono.zip(order, user, price)
        .map(tuple -> OrderSummary.of(
            tuple.getT1(),
            tuple.getT2(),
            tuple.getT3()));
}
```

**How to test / verify correctness:**

```java
@Test
void buildSummary_combinesAllSources() {
    // StepVerifier is Reactor's test utility
    StepVerifier.create(
            service.buildSummary(1L))
        .assertNext(summary -> {
            assertThat(summary.orderId())
                .isEqualTo(1L);
            assertThat(summary.userName())
                .isNotBlank();
        })
        .verifyComplete();  // asserts onComplete
}
```

---

### ⚖️ Comparison Table

| Concept             | `Flux.flatMap()`              | `Flux.concatMap()`        | `Flux.flatMapSequential()` |
| ------------------- | ----------------------------- | ------------------------- | -------------------------- |
| Inner subscriptions | Concurrent (256 default)      | Sequential (1 at a time)  | Concurrent                 |
| Output order        | Unordered (first-to-complete) | Ordered (input order)     | Ordered (re-merged)        |
| Throughput          | Highest                       | Lowest                    | Medium                     |
| Use when            | Independent parallel I/O      | Ordered processing needed | Parallel but ordered       |

| Scheduler                     | Thread model                      | Use for               |
| ----------------------------- | --------------------------------- | --------------------- |
| `Schedulers.parallel()`       | CPU-core-count threads            | CPU-bound computation |
| `Schedulers.boundedElastic()` | Bounded thread pool (200 × cores) | Legacy blocking I/O   |
| `Schedulers.single()`         | 1 thread                          | Serialised operations |
| `Schedulers.immediate()`      | Current thread                    | Testing               |

---

### ⚠️ Common Misconceptions

| Misconception                                          | Reality                                                                                                                                                                                  |
| ------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Returning `Mono` from a method executes it"           | Declaring a `Mono` is pure description. Execution only begins when `subscribe()` is called (by WebFlux, `StepVerifier`, or explicit `.subscribe()`).                                     |
| "`subscribeOn()` controls which thread runs operators" | `subscribeOn()` controls the source emission thread. `publishOn()` controls the downstream operator thread. Only one `subscribeOn()` is effective per chain (the closest to source).     |
| "Reactor automatically parallelises work"              | Reactor is single-threaded by default within a chain. Parallelism requires explicit `flatMap` with parallel inner publishers or `Flux.parallel()`.                                       |
| "`flatMap` is always better than `concatMap`"          | `flatMap` is concurrent and unordered - breaks ordering guarantees. Use `concatMap` when order matters (pagination, sequential database writes).                                         |
| "Reactive code is faster than blocking code"           | Reactive code is more _efficient_ under high concurrency (fewer threads). For low concurrency, blocking code is simpler and similar throughput. Virtual threads (Java 21) close the gap. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Event loop starvation from blocking call**

**Symptom:** Application becomes unresponsive under moderate load; all requests time out; CPU near 0%; thread dump shows Netty event loop threads stuck in blocking operations.

**Root Cause:** A blocking call (`JDBC`, `RestTemplate`, `Thread.sleep()`) inside a reactive chain executes on the Netty event loop thread, preventing it from processing other requests.

**Diagnostic:**

```bash
# Install BlockHound (dev dependency)
# It throws BlockingOperationError on first block
# Also: thread dump analysis
jstack <pid> | grep "reactor-http-nio"
# If stuck in non-Reactor code, blocking call found
```

**Fix:**

```java
// BAD: JDBC on event loop thread
.flatMap(id -> Mono.just(jdbcRepo.findById(id)))

// GOOD: offload to bounded elastic
.flatMap(id -> Mono.fromCallable(
        () -> jdbcRepo.findById(id))
    .subscribeOn(
        Schedulers.boundedElastic()))
```

**Prevention:** Enable `BlockHound` in CI tests. Prefer R2DBC over JDBC for database access in reactive services.

---

**Mode 2: Forgotten subscribe - no-op reactive chain**

**Symptom:** A reactive chain is assembled but nothing happens - no database writes, no HTTP calls, no side effects. No error, no log.

**Root Cause:** The `Mono` was returned from an internal method, stored, or passed but never subscribed to.

**Diagnostic:**

```java
// BAD: no subscribe - nothing executes
public void sendNotification(Event event) {
    notificationService.send(event);  // returns Mono<Void>
    // Mono discarded without subscribing
}

// GOOD:
public Mono<Void> sendNotification(Event event) {
    return notificationService.send(event);
    // Caller (WebFlux) subscribes
}
```

**Prevention:** Static analysis rule: any `Mono`/`Flux` returned from a method call that is not `return`-ed or assigned to a subscribed variable is a bug. Enable `reactor.core.publisher.Operators.onOperatorError` to log assembly-time warnings.

---

**Mode 3: Context loss in security (Security failure mode)**

**Symptom:** `SecurityContextHolder.getContext()` returns empty inside a `flatMap`; `@PreAuthorize` fails on service methods called from WebFlux controllers.

**Root Cause:** `SecurityContextHolder` uses `ThreadLocal`; reactive chains switch threads via `publishOn()`/`subscribeOn()`, losing the `ThreadLocal`-bound security context.

**Diagnostic:**

```java
// Check if context propagates
.flatMap(data -> {
    // Will be null on different thread
    Authentication auth =
        SecurityContextHolder.getContext()
            .getAuthentication();
    log.debug("Auth: {}", auth);
    return process(data);
})
```

**Fix:** Use `ReactiveSecurityContextHolder`:

```java
.flatMap(data ->
    ReactiveSecurityContextHolder.getContext()
        .map(ctx -> ctx.getAuthentication())
        .flatMap(auth -> process(data, auth)))
```

**Prevention:** In WebFlux applications, use `ReactiveSecurityContextHolder` exclusively; never `SecurityContextHolder`.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[SPR-028 - WebFlux Introduction]] - the Spring WebFlux web framework built on Reactor
- [[SPR-029 - Reactive Streams Specification]] - the specification Reactor implements
- [[SPR-074 - Flux and Mono]] - Reactor's two core publisher types

**Builds On This (learn these next):**

- [[SPR-010 - Spring WebFlux vs Virtual Threads]] - when Reactor is no longer the right choice
- [[SPR-060 - Spring Migration Strategy (MVC to WebFlux)]] - migration considerations
- [[SPR-084 - Spring Native and GraalVM Integration]] - AOT + Reactor interaction

**Alternatives / Comparisons:**

- RxJava - similar reactive library; older; Android-focused; heavier API
- Java `Flow` API - JDK Reactive Streams implementation; minimal operators; rarely used directly
- Virtual threads (Java 21) - alternative to reactive for I/O concurrency; blocking style with non-blocking behaviour

---

### 📌 Quick Reference Card

```
+----------------------------------------------------------
| WHAT IT IS    | Lazy, backpressure-aware async pipeline
  |
|               | library (Reactive Streams
  implementation)|
| PROBLEM       | I/O-bound blocking thread exhaustion and
  |
|               | composable async code without callbacks
  |
| KEY INSIGHT   | Nothing runs until subscribe(); assembly
  |
|               | and execution are separate phases
  |
| USE WHEN      | I/O-heavy services; streaming data; non-
  |
|               | blocking with Spring WebFlux
  |
| AVOID WHEN    | CPU-bound work; simple CRUD; team lacks
  |
|               | reactive experience (use virtual
  threads)|
| TRADE-OFF     | Thread efficiency vs code complexity
  |
| ONE-LINER     | Flux/Mono = lazy blueprint; subscribe =
  |
|               | execute; request(n) = backpressure
  |
| NEXT EXPLORE  | SPR-010 (Virtual Threads vs Reactor),
  |
|               | SPR-060 (MVC to WebFlux migration)
  |
+----------------------------------------------------------
```

**If you remember only 3 things:**

1. `Mono`/`Flux` are lazy - declaring them does nothing; `subscribe()` starts execution
2. Never block inside a reactive chain - offload blocking I/O to `Schedulers.boundedElastic()`
3. `publishOn()` changes the downstream thread; `subscribeOn()` changes the source thread

**Interview one-liner:** "Project Reactor implements Reactive Streams with two lazy publishers (Mono/Flux) whose operator chains only execute when subscribed to; backpressure flows as demand signals from subscriber to publisher via `Subscription.request(n)`, preventing fast producers from overwhelming slow consumers."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** _Separate declaration from execution._ Describing what to compute (the pipeline) separately from when to compute it (subscription) enables reuse, testability, and composition. A pipeline declared as a value can be passed, stored, and combined - execution starts only when all composition decisions are made.

**Where else this pattern appears:**

- **SQL query builders** (JOOQ, Criteria API) - query is built as an object, executed only on `fetch()`/`getResultList()` - same assembly vs execution separation
- **RxJS (JavaScript)** - `Observable` is a cold source; `.pipe()` builds operator chain; `.subscribe()` executes; same model as Reactor in the browser
- **Spark RDD/Dataset** - transformations are lazy (build DAG); `collect()` / `show()` triggers execution - the reactive pattern applied to distributed data

---

### 💡 The Surprising Truth

Reactor's performance advantage over traditional thread-per-request is not primarily about CPU - it is about _memory_. A Java thread costs 512KB-1MB of stack memory by default. 1,000 concurrent requests = 500MB-1GB of thread stacks alone. A Reactor application handling 1,000 concurrent requests might use 4-8 event loop threads (total ~4-8MB of stacks). The same application with `RestTemplate` needs 1,000 threads (~500MB stacks). In memory-constrained environments (containers with 256MB limits), reactive is not a performance optimisation - it is the only architecture that _fits_. This is why Netflix's migration to reactive in 2016 was driven by container memory costs, not by throughput benchmarks.

---

### 🧠 Think About This Before We Continue

**Question 1 (A - System Interaction):** A Spring WebFlux controller returns `Flux<ServerSentEvent>` for a live dashboard. The source is a Kafka topic consumed via `reactor-kafka`. 500 browser clients connect to the SSE endpoint simultaneously. Describe the thread model: how many threads handle 500 simultaneous SSE connections, and how does Kafka consumer backpressure propagate to the browser clients?

_Hint:_ Consider that Netty event loops handle I/O for all 500 connections; Kafka consumer runs on a separate thread; `Sinks.many()` bridges the Kafka thread to the reactive pipeline; browser clients control SSE flow via HTTP/2 flow control.

**Question 2 (C - Design Trade-off):** `flatMap` has a default concurrency of 256 inner subscriptions. A service uses `flatMap` to call a downstream HTTP API. Under load, 10,000 items arrive per second. Explain what happens to the 256-concurrency limit under this load, and describe two strategies to handle the resulting pressure: one that increases throughput and one that reduces load on the downstream API.

_Hint:_ Consider `flatMap(f, concurrency)` parameter tuning, `limitRate()` before `flatMap`, `onBackpressureBuffer()` with overflow strategy, and batching multiple items into a single downstream call.

**Question 3 (E - First Principles):** Reactor's `Context` is the reactive replacement for `ThreadLocal`. Describe from first principles why `ThreadLocal` fails in a reactive pipeline, and explain the mechanism Reactor uses to propagate `Context` through `flatMap()` boundaries where the thread changes.

_Hint:_ `ThreadLocal` is bound to a thread, not to a logical flow. Reactor's `Context` is attached to the `Subscription` chain (not the thread). `flatMap()` creates a new inner subscription; how does it inherit the parent's `Context`?
