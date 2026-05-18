---
version: 1
layout: default
title: "Mono  Flux"
parent: "Spring Core"
grand_parent: "Technical Mastery"
nav_order: 73
permalink: /technical-mastery/spring/mono-flux/
id: SPR-033
category: Spring Core
difficulty: ★★★
depends_on: Reactor, Reactive Streams, WebFlux / Reactive
used_by: WebFlux, Spring Data Reactive, WebClient
related: CompletableFuture, Observable (RxJava), Publisher
tags:
  - spring
  - java
  - performance
  - deep-dive
  - reactive
---

⚡ TL;DR - `Mono<T>` represents a single asynchronous value (or empty), `Flux<T>` represents an asynchronous stream of 0-N values - they're the return types of all reactive Spring operations, executing lazily when subscribed.

| #405            | Category: Spring Core                             | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------ | :-------------- |
| **Depends on:** | Reactor, Reactive Streams, WebFlux / Reactive     |                 |
| **Used by:**    | WebFlux, Spring Data Reactive, WebClient          |                 |
| **Related:**    | CompletableFuture, Observable (RxJava), Publisher |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Asynchronous Java before reactive: you call a service, it returns a `CompletableFuture<T>`. You want to transform the result, combine with another future, handle errors differently, and retry on failure. You chain `.thenApply()`, `.thenCompose()`, `.exceptionally()`. Combining two futures requires `CompletableFuture.allOf()` which returns `CompletableFuture<Void>` - losing the actual values. Streaming 10,000 items from a database through transformation and filtering into an HTTP response means loading all into memory, then streaming.

**THE BREAKING POINT:**
`CompletableFuture` handles one item. It has no concept of streams, backpressure, or operator composition. Streaming scenarios (real-time events, large database result sets, server-sent events) require building custom infrastructure.

**THE INVENTION MOMENT:**
"This is exactly why `Mono` and `Flux` were created."

---

### 📘 Textbook Definition

**`Mono<T>`** is a Reactor type representing an asynchronous computation that produces at most one value (`T`), an empty result, or an error signal - semantically equivalent to `CompletableFuture<Optional<T>>` but with a rich operator library. **`Flux<T>`** is a Reactor type representing an asynchronous computation that produces 0 to N values followed by either a completion or an error signal - semantically equivalent to `Publisher<T>` from Reactive Streams. Both are **cold** by default - nothing executes until `.subscribe()` is called. Both implement the Reactive Streams `Publisher<T>` interface, making them interoperable with any Reactive Streams-compatible library. Both support backpressure: subscribers can signal how many items they're ready to receive via the `Subscription.request(n)` protocol.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
`Mono` is a promise for one thing; `Flux` is a stream of things - both lazy, both composable, both async.

**One analogy:**

> `Mono` is an Amazon order confirmation: you'll receive exactly one package (or an error notification). `Flux` is a subscription box service: packages arrive over time until the subscription ends. In both cases, the order (subscription) must be placed before anything ships.

**One insight:**
Both `Mono` and `Flux` are **descriptions of computation**, not executions. Calling `.map()`, `.flatMap()`, `.filter()` assembles a pipeline. The pipeline executes only when `.subscribe()` is called. This laziness is by design - it enables operator composition before execution.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. `Mono`/`Flux` are **lazy**: pipeline operators (map, filter, flatMap) build a description; `.subscribe()` or a terminal operator triggers execution.
2. Each subscriber gets an independent execution of the pipeline - unless the publisher is **hot** (shared, multicasting).
3. Backpressure is cooperative: `Flux` emits items only as fast as the subscriber requests them via `Subscription.request(n)`.

**DERIVED DESIGN:**
Why laziness? Enabling operator composition. If `Mono.fromCallable(() -> dbCall())` executed immediately, you couldn't attach error handling, retry, or timeout before the DB call runs. Laziness lets you build the full processing pipeline first:

```
Mono.fromCallable(() -> dbCall())
    .timeout(Duration.ofSeconds(3))    // add timeout
    .retry(2)                          // add retry
    .onErrorReturn(defaultValue)       // add fallback
    .subscribe(result -> ...)          // NOW execute
```

This is the **decorator pattern** applied to async computation: each operator wraps the previous, adding behavior without modifying the original.

**THE TRADE-OFFS:**

**Gain:** Rich operator library (100+ operators for transformation, filtering, combining, error handling); built-in backpressure; composable; lazy - enables adding cross-cutting concerns (retry, timeout, logging) without modifying source code.

**Cost:** Cold/hot distinctions are subtle; operator ordering matters; debugging requires `checkpoint()` and `log()` operators; the laziness can surprise - if you never subscribe, nothing happens and you get no error.

---

### 🧪 Thought Experiment

**SETUP:**
You write `Mono<User> result = userRepository.findById("123")`. You log "fetching user". You return `result` from a method. Does the database query execute?

**ANSWER:**
No. The database query does NOT execute. You've assembled the pipeline but haven't subscribed. The `log("fetching user")` message also doesn't appear if it's inside the Mono pipeline (it fires only during execution).

The query executes when:

1. You call `result.subscribe(user -> ...)` explicitly, OR
2. You return `result` from a WebFlux controller method (WebFlux subscribes on your behalf), OR
3. You call a blocking "bridge" method like `result.block()` (blocking - should only be used in tests or non-reactive entry points).

**THE INSIGHT:**
Returning a `Mono` from a method does not execute the computation. It schedules the computation. This is the single most important fact to internalize about reactive programming.

---

### 🧠 Mental Model / Analogy

> `Mono` and `Flux` are like cooking recipes, not cooked food. Writing `.map()`, `.flatMap()`, `.filter()` is writing steps in the recipe. Calling `.subscribe()` is actually cooking the recipe. The same recipe can be cooked multiple times (multiple subscribers), each time producing a fresh result.

- "Writing a recipe" → composing operators on a Mono/Flux
- "Cooking the recipe" → calling `.subscribe()`
- "Two people cooking the same recipe" → two subscribers, two independent executions
- "Recipe step: add seasoning" → `.map(result -> enhance(result))`
- "Sub-recipe: make sauce from scratch" → `.flatMap(item -> callService(item))` which returns a new Mono

Where this analogy breaks down: unlike a recipe that always produces the same dish, `Mono`/`Flux` pipelines produce results asynchronously and may produce different results depending on timing (e.g., a DB query returning different data).

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
`Mono<User>` means "you'll get a User asynchronously (or nothing, or an error)." `Flux<User>` means "you'll get a stream of Users asynchronously." Think of them as async containers - like a `Future` that knows how to chain operations and handle errors cleanly.

**Level 2 - How to use it (junior developer):**
Use `Mono` when a service returns one item (findById), use `Flux` when it returns many (findAll). Transform with `.map()` (synchronous transform), `.flatMap()` (async transform returning another Mono/Flux). Handle errors with `.onErrorReturn(defaultValue)` or `.onErrorResume(e -> fallback)`. Add timeouts with `.timeout(Duration.ofSeconds(3))`. In tests: use `StepVerifier` to assert reactive pipelines.

**Level 3 - How it works (mid-level engineer):**
`Mono` and `Flux` are implementations of `CorePublisher<T>`. Each operator creates a new publisher wrapping the previous. When `.subscribe(Subscriber<T> s)` is called on the outermost publisher, it calls `.subscribe()` on its upstream, which calls `.subscribe()` on its upstream - this propagation of subscription is the "assembly line" being connected. Once connected, the source calls `subscriber.onNext(item)` for each item, `subscriber.onComplete()` when done, or `subscriber.onError(t)` on failure. `flatMap` subscribes to inner publishers concurrently (up to `concurrency` limit). `concatMap` subscribes sequentially. These operator semantics drive most performance trade-offs.

**Level 4 - Why it was designed this way (senior/staff):**
`Mono` is technically a `Flux` of at most 1 element - the type split is for API clarity and optimization. `Mono`'s implementation can skip backpressure mechanics (since there's at most 1 element, demand management is trivial) and can be optimized with fewer allocations. The design choice to follow the Reactive Streams specification (Publisher/Subscriber protocol) rather than building a proprietary API makes Reactor interoperable with RxJava, Akka Streams, and any other RS-compliant library. The `onBackpressureBuffer` / `onBackpressureDrop` operators exist because the `request(n)` backpressure protocol breaks down at the network boundary - bridging between a push-based external source (network bytes) and a pull-based reactive pipeline requires explicit overflow strategies.

---

### ⚙️ How It Works (Mechanism)

```
PIPELINE ASSEMBLY (subscribe not yet called):

  Mono.fromCallable(() -> db.findUser(id))  // Source
    .timeout(Duration.ofSeconds(3))          // Wrapper 3
    .retry(2)                                // Wrapper 2
    .map(user -> toDto(user))                // Wrapper 1
    ← No execution yet ←

SUBSCRIPTION PHASE (.subscribe() called):

  subscribe() propagates DOWN through wrappers:
    Wrapper1.subscribe(consumerSubscriber)
      → Wrapper2.subscribe(mapSubscriber)
        → Wrapper3.subscribe(retrySubscriber)
          → Wrapper4.subscribe(timeoutSubscriber)
            → Source.subscribe(timeoutInnerSub)
              → Callable.call() → db.findUser(id) ←
                EXECUTES HERE

DATA FLOW PROPAGATES UP:
  Source.onNext(user) → timeout → retry → map → consumer
  (or error → timeout enforces → retry retries → onError
    propagates)
```

---

### 💻 Code Example

**Example 1 - Mono creation and operators:**

```java
// Creating Monos
Mono<User> fromValue = Mono.just(new User("alice"));
Mono<User> fromCallable = Mono.fromCallable(
    () -> userRepository.findById("123"));
    // blocking - use with subscribeOn
Mono<User> fromFuture = Mono.fromFuture(
    userServiceClient.getUserAsync("123"));
Mono<User> empty = Mono.empty();
Mono<User> error = Mono.error(
    new UserNotFoundException("123"));

// Transforming
Mono<UserDto> transformed = fromValue
    .map(user -> new UserDto(user.name())) // sync transform
    .flatMap(dto -> enrichmentService     // async transform
        .enrich(dto))                     // returns Mono<UserDto>
    .filter(dto -> dto.active())          // filter (empty if false)
    .defaultIfEmpty(UserDto.ANONYMOUS);   // fallback if empty
```

**Example 2 - Flux creation and operators:**

```java
// Creating Fluxes
Flux<User> fromList = Flux.fromIterable(userList);
Flux<Long> interval = Flux.interval(Duration.ofSeconds(1));
Flux<User> fromRepo = userRepository.findAll(); // reactive repo

// Transforming a stream
Flux<UserDto> result = userRepository.findByRegion("EU")
    .filter(user -> user.active())
    .map(user -> new UserDto(user))
    .take(100)                        // take first 100
    .distinct(UserDto::email)         // deduplicate
    .sort(Comparator.comparing(
        UserDto::lastName));
```

**Example 3 - Combining and error handling:**

```java
// Parallel outbound calls - zip when both complete
Mono<Dashboard> dashboard = Mono.zip(
    webClient.get().uri("/profile/" + id)
        .retrieve().bodyToMono(Profile.class)
        .timeout(Duration.ofSeconds(2)),
    webClient.get().uri("/orders/" + id)
        .retrieve().bodyToMono(Orders.class)
        .timeout(Duration.ofSeconds(2)),
    (profile, orders) -> new Dashboard(profile, orders)
);

// Error handling with fallback
Mono<User> resilient = userRepository.findById(id)
    .timeout(Duration.ofSeconds(3))
    .retry(2)
    .onErrorResume(TimeoutException.class,
        e -> Mono.just(User.GUEST))    // fallback on timeout
    .onErrorMap(DbException.class,
        e -> new ServiceException(e)); // map error type

// Testing with StepVerifier
@Test
void testUserFound() {
    Mono<User> result = userService.findUser("alice");

    StepVerifier.create(result)
        .expectNextMatches(u -> u.name().equals("alice"))
        .verifyComplete();
}

@Test
void testUserNotFound() {
    StepVerifier.create(userService.findUser("unknown"))
        .expectNextCount(0)
        .verifyComplete(); // or verifyError()
}
```

---

### ⚖️ Comparison Table

| Type                   | Items     | Spring Usage           | Java Equivalent                  |
| ---------------------- | --------- | ---------------------- | -------------------------------- |
| `Mono<T>`              | 0 or 1    | findById, save, delete | `CompletableFuture<Optional<T>>` |
| `Flux<T>`              | 0 to N    | findAll, stream, SSE   | `Flow.Publisher<T>` / stream     |
| `CompletableFuture<T>` | Exactly 1 | Spring MVC async       | N/A (compare: no backpressure)   |
| `Optional<T>`          | 0 or 1    | Spring MVC sync        | N/A (blocking)                   |
| `List<T>`              | 0 to N    | Spring MVC sync        | N/A (blocking, all in memory)    |

| Operator                 | Effect                        | Sync Equivalent                      |
| ------------------------ | ----------------------------- | ------------------------------------ |
| `.map(f)`                | Transform each item (sync)    | `stream().map(f)`                    |
| `.flatMap(f → Mono)`     | Async transform, concurrent   | `stream().flatMap()`                 |
| `.concatMap(f → Mono)`   | Async transform, sequential   | `stream().flatMap()` in order        |
| `.filter(pred)`          | Keep items matching predicate | `stream().filter()`                  |
| `.take(n)`               | Take first N items            | `stream().limit(n)`                  |
| `.zip(mono1, mono2, fn)` | Combine when both complete    | `CompletableFuture.allOf()` + values |

---

### ⚠️ Common Misconceptions

| Misconception                                                       | Reality                                                                                                                                  |
| ------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| `Mono.just(value)` executes the computation eagerly                 | `Mono.just(value)` wraps an already-computed value; the computation (DB call etc.) must be in `Mono.fromCallable()` to be lazy           |
| `map()` and `flatMap()` are interchangeable                         | `map()` takes `T → R` (sync); `flatMap()` takes `T → Mono<R>` (async); using map when flatMap is needed returns `Mono<Mono<R>>`          |
| Each subscriber to the same Mono gets the same cached result        | No - cold publishers re-execute for each subscriber. Use `.cache()` to cache the result for multiple subscribers.                        |
| `Flux` sends all items before the subscriber processes any          | Flux and subscriber coordinate via `request(n)` backpressure - items are emitted as fast as the subscriber accepts them, not all upfront |
| You can use a reactive repository method result without subscribing | In WebFlux, the framework subscribes. In non-reactive code or tests, you must subscribe or call `.block()` or use `StepVerifier`         |

---

### 🚨 Failure Modes & Diagnosis

**1. Silent No-Op - Pipeline Not Subscribed**

**Symptom:** A method assembles a `Mono` pipeline (with DB calls, HTTP calls) and nothing happens - no DB queries, no HTTP calls, no output. No exception thrown.

**Root Cause:** The pipeline was assembled but `.subscribe()` was never called. Reactive pipelines are cold and lazy - no subscription = no execution.

**Diagnostic:**

```java
// Enable Reactor debug mode to trace pipeline assembly
// (heavy overhead - dev/test only)
Hooks.onOperatorDebug(); // add to application startup

// Add .log() to pipeline to see what's happening
userRepository.findById(id)
    .log("findById") // prints: subscribe, onNext, onComplete
    .map(user -> user.name());
```

**Fix:**

```java
// BAD: assembled but not subscribed
Mono<Void> deleteOp = userRepository.deleteById(id);
// Nothing deleted!

// GOOD: subscribe to execute
userRepository.deleteById(id)
    .subscribe(); // fire-and-forget
    // OR: return Mono<Void> from controller and let WebFlux subscribe
```

---

**2. `map()` Returning `Mono<Mono<T>>`**

**Symptom:** Type error `Mono<Mono<User>>` or unexpected behavior where inner `Mono` values are not extracted.

**Root Cause:** Using `.map()` where `.flatMap()` is required - when the transform function returns another `Mono`.

**Diagnostic:**

```java
// This compiles but is semantically wrong:
Mono<Mono<User>> wrong = userRepository.findById(id)
    .map(user -> enrichService.enrich(user));
    // enrich() returns Mono<User> → map wraps it in another Mono
```

**Fix:**

```java
// GOOD: flatMap unwraps the inner Mono
Mono<User> correct = userRepository.findById(id)
    .flatMap(user -> enrichService.enrich(user));
    // flatMap subscribes to the inner Mono and flattens
```

---

**3. ConcatMap vs FlatMap Order Bug**

**Symptom:** Results arrive in unexpected order; some items are missing or processed out of sequence.

**Root Cause:** Using `flatMap` when order matters - `flatMap` subscribes to inner publishers concurrently; if inner publishers complete at different times, results arrive out of order.

**Diagnostic:**

```java
// flatMap: concurrent, unordered
Flux<User> unordered = Flux.range(1, 10)
    .flatMap(id -> fetchUser(id)); // ids 1-10 fetched concurrently
    // results arrive as each fetch completes - not in id order

// concatMap: sequential, ordered - each fetch waits for previous
Flux<User> ordered = Flux.range(1, 10)
    .concatMap(id -> fetchUser(id));
    // ids fetched 1,2,3...10 in order
    // much slower if each fetch takes 100ms (1s total vs. 100ms
    // total)
```

**Fix:** Use `concatMap` when order matters. Use `flatMap(id, concurrency=5)` when parallel but concurrency-limited.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Reactive Streams` - the specification (Publisher/Subscriber/Subscription) that Mono/Flux implement; understand the protocol
- `WebFlux / Reactive` - the Spring framework layer that uses Mono/Flux as its core return types
- `Reactor` - the specific library (Project Reactor) that provides Mono and Flux implementations

**Builds On This (learn these next):**

- `Backpressure (Spring)` - how `Flux` handles consumers slower than producers; the `request(n)` protocol in action
- `WebClient` - Spring's non-blocking HTTP client that returns `Mono`/`Flux`
- `Spring Data Reactive` - reactive repositories that return `Mono`/`Flux` instead of blocking results

**Alternatives / Comparisons:**

- `CompletableFuture<T>` - the Java standard for single async values; simpler but no streaming, no backpressure, fewer operators
- `Observable<T>` (RxJava) - similar concept; RxJava's `Single` = `Mono`, `Observable` = `Flux`; Reactive Streams makes them interoperable
- `Flow.Publisher<T>` (Java 9+) - the Java standard library Reactive Streams types; lower-level, fewer operators than Reactor

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ Mono<T>      │ 0 or 1 item, async; like                 │
│              │ CompletableFuture<Optional<T>>           │
├──────────────┼──────────────────────────────────────────┤
│ Flux<T>      │ 0 to N items, async stream with          │
│              │ backpressure                             │
├──────────────┼──────────────────────────────────────────┤
│ KEY RULE     │ LAZY - nothing executes until subscribed │
├──────────────┼──────────────────────────────────────────┤
│ map()        │ sync T → R transform                     │
│ flatMap()    │ async T → Mono<R>/Flux<R> transform      │
│ zip()        │ combine when all complete                │
├──────────────┼──────────────────────────────────────────┤
│ ERROR OPS    │ .onErrorReturn() .onErrorResume()        │
│              │ .timeout() .retry()                      │
├──────────────┼──────────────────────────────────────────┤
│ TESTING      │ StepVerifier.create(mono).expectNext(...)│
│              │ .verifyComplete()                        │
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "Mono = async optional;                  │
│              │  Flux = async stream - both lazy"        │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Backpressure → WebClient → Spring Data R │
└─────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE A - System Interaction) You have a `Flux<Order>` that emits 1,000 orders per second from a database. Each order must be enriched via a REST API call that takes 50ms. You use `.flatMap(order -> enrichApi.enrich(order))`. Calculate the maximum throughput this pipeline can achieve. How does `flatMap`'s concurrency parameter affect this - and at what concurrency level does the enrichment API become the bottleneck?

**Q2.** (TYPE C - Design Trade-off) A team wraps legacy blocking JDBC calls in `Mono.fromCallable(() -> jdbcTemplate.query(...)).subscribeOn(Schedulers.boundedElastic())`. Another team says "just use Spring MVC with Virtual Threads - same result." Are they equivalent? Identify the one scenario where the reactive approach has a genuine advantage that the Virtual Threads approach cannot match natively.
