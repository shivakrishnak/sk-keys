---
layout: default
title: "Reactive Programming"
parent: "CS Fundamentals — Paradigms"
nav_order: 7
permalink: /cs-fundamentals/reactive-programming/
number: "0007"
category: CS Fundamentals — Paradigms
difficulty: ★★☆
depends_on: Event-Driven Programming, Functional Programming, Asynchronous Programming
used_by: Spring WebFlux, RxJava, Reactive Streams
related: Event-Driven Programming, Functional Programming, Actor Model
tags:
  - intermediate
  - pattern
  - architecture
  - java
  - concurrency
  - streaming
---

# 007 — Reactive Programming

⚡ TL;DR — Reactive programming treats data as streams of events that you compose and transform with functional operators, automatically propagating changes through the pipeline.

| #007 | Category: CS Fundamentals — Paradigms | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Event-Driven Programming, Functional Programming, Asynchronous Programming | |
| **Used by:** | Spring WebFlux, RxJava, Reactive Streams | |
| **Related:** | Event-Driven Programming, Functional Programming, Actor Model | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A microservice must: fetch user data from a database (50ms),
simultaneously call three external APIs (100-200ms each), combine
the results, filter, and stream 10,000 items to the client.
Without reactive programming, you'd either block a thread per
I/O operation (expensive at scale), or hand-wire callbacks for
every async combination — merging three concurrent callbacks into
one result is 50 lines of error-prone Promise coordination code.
Adding backpressure (not overwhelming a slow consumer) means
inventing your own flow control.

**THE BREAKING POINT:**
Modern systems require: concurrency (multiple I/O sources),
composition (combining streams), transformation (functional
operators), and flow control (backpressure). Callback-based
event-driven code handles one source at a time; combining
multiple async sources with error handling and backpressure
produces unmaintainable code.

**THE INVENTION MOMENT:**
This is exactly why Reactive Programming was created. Instead
of wiring callbacks manually, you declare: "this stream is
userEvents merged with apiResults, filtered by X, batched by Y,
with a 500ms timeout." The reactive library handles threading,
backpressure, error propagation, and cancellation automatically.

---

### 📘 Textbook Definition

Reactive programming is a paradigm for building asynchronous,
non-blocking programs around observable data streams. It extends
event-driven programming with a composable, functional API for
transforming and combining streams. Core abstractions include:
Observable/Publisher (a source of zero or more events),
Observer/Subscriber (a consumer of those events), and Operators
(functional transformations: `map`, `filter`, `merge`, `flatMap`,
`zip`). Backpressure — the ability of a slow consumer to signal
a fast producer to slow down — is a first-class concern.
Implementations include RxJava, Project Reactor (Spring WebFlux),
RxJS, and the JDK's `java.util.concurrent.Flow`.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Data arrives as streams; you declare transformations on those streams, not step-by-step procedures.

**One analogy:**

> Reactive programming is like a spreadsheet. When cell A1
> changes, B2 (which depends on A1) automatically updates.
> You declare the relationship once — `B2 = A1 * 2` — and
> changes propagate automatically. You never manually "push"
> updates; the dependency graph does it for you.

**One insight:**
The spreadsheet insight is the essence: you declare WHAT
depends on WHAT, not HOW to propagate changes. When a new
HTTP request arrives, the entire pipeline from "request received"
to "response sent" is already declared. The library wires it.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Everything is a stream — a sequence of events over time.
   A database result set, an HTTP response body, user clicks,
   a timer — all are streams of one or more items.
2. Streams are composed with operators — map, filter, flatMap,
   merge, zip transform and combine streams without manual
   callback wiring.
3. Backpressure is first-class — a slow subscriber can signal
   the publisher to pause, preventing out-of-memory crashes
   from fast producers overwhelming slow consumers.

**DERIVED DESIGN:**
Given invariant 1, I/O operations return streams (Mono<T> for
0 or 1 result, Flux<T> for N results in Reactor) rather than
blocking values or callbacks. Given invariant 2, complex async
workflows are declarative pipelines — no shared mutable state
between operators. Given invariant 3, `Flux.buffer(100)` or
`onBackpressureDrop()` are built-in, not hand-coded.

**THE TRADE-OFFS:**
**Gain:** High throughput on I/O-bound workloads (non-blocking,
no thread-per-request); composable async pipelines;
built-in backpressure; automatic error propagation.
**Cost:** Steep learning curve; debugging requires understanding
the subscription model; stack traces are unreadable
(operators, not your code, appear at the top); not
appropriate for CPU-bound work.

---

### 🧪 Thought Experiment

**SETUP:**
Fetch 3 user profiles concurrently, filter those with premium
accounts, enrich each with purchase history, then stream results
to the client as they arrive.

**WHAT HAPPENS WITH CALLBACKS:**

```javascript
fetchProfile(1, (p1) => {
  fetchProfile(2, (p2) => {
    fetchProfile(3, (p3) => {
      const premium = [p1, p2, p3].filter((p) => p.premium);
      let done = 0;
      premium.forEach((p) => {
        fetchHistory(p.id, (history) => {
          p.history = history;
          done++;
          if (done === premium.length) sendAll(premium);
        });
      });
    });
  });
}); // 4 levels deep, no backpressure, no error handling
```

**WHAT HAPPENS WITH REACTIVE:**

```java
Flux.just(1, 2, 3)
    .flatMap(id -> fetchProfile(id))   // concurrent fetch
    .filter(p -> p.isPremium())        // synchronous filter
    .flatMap(p -> enrichWithHistory(p))// concurrent enrich
    .subscribe(client::send);          // stream to client
// Linear, composable, backpressure built in
```

3 lines of declarative pipeline vs. 15 lines of nested callbacks.

**THE INSIGHT:**
Reactive programming makes concurrent async workflows look as
simple as synchronous ones — the complexity is absorbed by the
library's operator implementations.

---

### 🧠 Mental Model / Analogy

> Reactive programming is a factory assembly line. Raw materials
> (events) enter at one end. Each station on the line transforms
> the item (map, filter). Some stations merge two lines into one
> (zip, merge). The line moves at the speed of the slowest
> station — backpressure ensures items don't pile up and overflow
> the floor. You design the line layout; the factory runs it.

- "Raw materials entering" → events emitted by the source
- "Each assembly station" → an operator (map, filter, flatMap)
- "Merging two conveyor lines" → merge() or zip() operators
- "Line speed matching the slowest station" → backpressure
- "Factory running automatically" → reactive library execution

Where this analogy breaks down: unlike a physical assembly line,
reactive streams can fork (one source to multiple subscribers)
and have hot vs. cold semantics that have no physical equivalent.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Reactive programming is a way of writing code where you describe
what should happen to data as it arrives, rather than waiting
for all data to arrive before processing. Like a water slide
— as soon as water enters the top, it flows through every
turn and arrives at the bottom without waiting.

**Level 2 — How to use it (junior developer):**
In Spring WebFlux, return `Mono<T>` for single async results
and `Flux<T>` for streams. Use `.map()` to transform, `.filter()`
to remove items, `.flatMap()` for async operations, `.zip()` to
combine two streams. Subscribe at the end to trigger execution —
the pipeline is lazy until subscribed. Use `.subscribe(onNext,
onError, onComplete)` or return from a controller method.

**Level 3 — How it works (mid-level engineer):**
A Reactor `Flux` is a lazy publisher — nothing executes until
`subscribe()` is called. The subscription propagates UP the
operator chain, each operator wrapping the previous as a
subscriber. When the source emits an item, it flows DOWN the
chain through each operator. `flatMap` launches a new inner
stream for each item, concurrently, merging results as they
complete. Backpressure is implemented via `request(n)` calls:
a subscriber requests N items; the publisher only emits N.

**Level 4 — Why it was designed this way (senior/staff):**
The Reactive Streams specification (2013, led by Lightbend,
Netflix, Pivotal) standardised the `Publisher`/`Subscriber`/
`Subscription` interfaces — solved by defining `request(n)`
for backpressure. Project Reactor (Spring Reactor) builds on
this spec. The design chose operator fusion (compile adjacent
operators into one iteration) for performance. Spring WebFlux
adopted Reactor to solve the N+1 thread problem in Spring MVC:
with Reactor's event loop (Netty), 1 thread serves thousands of
concurrent requests vs. 1 thread per request in Tomcat. The
cost: reactive code doesn't compose with imperative `try/catch`
or standard Java generics — you must stay inside the reactive
context (no `Mono.block()` in production).

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────┐
│         REACTIVE PIPELINE EXECUTION              │
├──────────────────────────────────────────────────┤
│                                                  │
│  Flux.fromIterable([1,2,3])  ← Source            │
│       ↓ subscribe() propagates UP                │
│  .map(n -> n * 2)            ← Operator 1        │
│       ↓                                          │
│  .filter(n -> n > 2)         ← Operator 2        │
│       ↓                                          │
│  .subscribe(System.out::println) ← Subscriber    │
│                                                  │
│  EXECUTION (flows DOWN after subscribe):         │
│  Source emits 1 → map(1)=2 → filter(2>2)? NO    │
│  Source emits 2 → map(2)=4 → filter(4>2)? YES   │
│                → subscriber.onNext(4)            │
│  Source emits 3 → map(3)=6 → filter(6>2)? YES   │
│                → subscriber.onNext(6)            │
│  Source completes → subscriber.onComplete()      │
└──────────────────────────────────────────────────┘
```

**Subscription assembly:** Calling `.subscribe()` triggers
assembly — each operator wraps the downstream as a Subscriber.
The chain is: Source → MapSubscriber → FilterSubscriber →
your Subscriber. Nothing runs yet.

**Item emission:** The source calls `onNext(item)` on the first
subscriber in the chain. The item flows through each operator
synchronously on the calling thread (unless a `subscribeOn`/
`publishOn` changes the scheduler).

**flatMap:** Launches a new inner stream per item and subscribes
to it. Results arrive in completion order (not emission order).
Concurrency is limited by `flatMap(fn, concurrency)` parameter.

**Backpressure:** A subscriber calls `subscription.request(n)`.
The source only emits `n` items. `Flux.onBackpressureDrop()`
drops items if the subscriber can't keep up.

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**

```
[HTTP request arrives on Netty thread]
  → [Router matches, calls controller]
  → [Controller returns Flux<Product>]
  → [Spring subscribes to Flux ← YOU ARE HERE]
  → [DB driver emits results non-blocking]
  → [map/filter operators transform each item]
  → [Items streamed to HTTP response as they arrive]
  → [onComplete: HTTP response finished]
```

**FAILURE PATH:**
[DB connection fails → onError(ex)]
→ [Propagates down the operator chain]
→ [Spring maps to HTTP 500 response]
→ [Observable: error in HTTP response, logs with stack trace]

**WHAT CHANGES AT SCALE:**
At 10x load, a Netty+WebFlux server handles it with the same
thread count — non-blocking I/O scales with concurrency, not
threads. At 100x, the bottleneck shifts to DB connection pool
size (R2DBC). At 1000x, backpressure prevents OOM when DB is
slower than the producer; without it, `Flux` buffers grow
unboundedly and cause heap exhaustion.

---

### 💻 Code Example

**Example 1 — Spring WebFlux reactive REST endpoint:**

```java
// BAD (blocking MVC — thread-per-request)
@GetMapping("/products")
List<Product> getProducts() {
    return productRepository.findAll();  // blocks thread
}

// GOOD (reactive WebFlux — non-blocking)
@GetMapping(value = "/products",
    produces = MediaType.TEXT_EVENT_STREAM_VALUE)
Flux<Product> getProducts() {
    // Returns immediately; items stream as DB emits them
    return productRepository.findAll(); // returns Flux<Product>
}
```

**Example 2 — Combining concurrent async calls:**

```java
// Fetch user and their orders CONCURRENTLY, then combine
Mono<UserProfile> profile = userService.findById(userId);
Mono<List<Order>> orders  = orderService.findByUserId(userId);

// zip waits for BOTH to complete, then combines:
Mono<UserDashboard> dashboard = Mono.zip(profile, orders)
    .map(tuple -> new UserDashboard(
        tuple.getT1(),    // user profile
        tuple.getT2()     // orders list
    ));
// Both HTTP calls fire simultaneously — not sequentially
```

**Example 3 — Backpressure control:**

```java
// BAD: no backpressure — fast source overwhelms slow consumer
Flux.range(1, 1_000_000)
    .subscribe(item -> {
        slowProcess(item);  // takes 10ms each → OOM
    });

// GOOD: control flow with limitRate
Flux.range(1, 1_000_000)
    .limitRate(100)         // request 100 at a time
    .subscribe(item -> {
        slowProcess(item);  // consumer sets the pace
    });
```

**Example 4 — Error handling in reactive pipeline:**

```java
userService.findById(id)
    .flatMap(user -> orderService.getOrders(user.getId()))
    .onErrorResume(UserNotFoundException.class,
        ex -> Mono.just(Collections.emptyList()))  // fallback
    .onErrorMap(DatabaseException.class,
        ex -> new ServiceUnavailableException(ex)) // remap
    .timeout(Duration.ofSeconds(5))
    .subscribe(
        orders -> sendResponse(orders),
        error  -> sendError(error)
    );
```

---

### ⚖️ Comparison Table

| Approach                      | Concurrency | Backpressure | Composability | Best For                    |
| ----------------------------- | ----------- | ------------ | ------------- | --------------------------- |
| **Reactive (Reactor/RxJava)** | Very high   | Built-in     | High          | I/O-heavy microservices     |
| CompletableFuture (Java)      | High        | None         | Medium        | Simple async tasks          |
| Thread pool (blocking)        | Medium      | Manual       | Low           | CPU-bound work              |
| Event callbacks               | High        | None         | Low           | Simple single-source events |

How to choose: Use reactive for I/O-heavy microservices needing
high throughput and stream processing. Use CompletableFuture
for simpler async coordination. Use blocking threads for CPU-bound
computation or when the reactive learning curve isn't justified.

---

### ⚠️ Common Misconceptions

| Misconception                             | Reality                                                                                                                       |
| ----------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| Reactive means faster for everything      | Reactive only wins for I/O-bound workloads; for CPU-bound tasks, thread pools are more appropriate                            |
| Calling .block() is a safe escape hatch   | `Mono.block()` inside a reactive pipeline deadlocks on the event loop thread — never use in production code                   |
| reactive = concurrent by default          | Reactor executes on a single thread unless you explicitly add `subscribeOn`/`publishOn` with a scheduler                      |
| Reactive programming is RxJava or Reactor | Reactive programming is the paradigm; RxJava, Reactor, RxJS, and Akka Streams are implementations of different specifications |

---

### 🚨 Failure Modes & Diagnosis

**1. Blocking Call Inside Reactive Pipeline**

**Symptom:**
Request latency spikes under load; all requests slow down
simultaneously; thread dump shows Netty threads blocked.

**Root Cause:**
A blocking JDBC call, `Thread.sleep()`, or `.block()` inside
a reactive operator monopolises the event loop thread.

**Diagnostic:**

```bash
# Reactor: enable BlockHound to detect blocking calls
BlockHound.install();
# Throws BlockingOperationError when blocking detected in reactor thread

# Thread dump to see what's blocking
jstack <pid> | grep -A 10 "reactor-http-nio"
```

**Fix:**

```java
// BAD: blocking JDBC inside reactive pipeline
Flux<User> users = Flux.fromIterable(
    jdbcTemplate.queryForList("SELECT * FROM users") // BLOCKS!
);

// GOOD: use R2DBC (reactive database driver)
Flux<User> users = r2dbcTemplate.select(User.class).all();
// OR: wrap blocking call with boundedElastic scheduler
Mono<List<User>> users = Mono.fromCallable(
    () -> jdbcTemplate.queryForList("SELECT * FROM users")
).subscribeOn(Schedulers.boundedElastic()); // off-loop thread
```

**Prevention:** Never call blocking APIs on reactor-http threads;
use R2DBC for databases, reactive HTTP clients for downstream.

**2. Missing Backpressure → OOM**

**Symptom:**
Heap exhaustion under load; `OutOfMemoryError` when producer
is faster than consumer; growing buffer in heap dumps.

**Root Cause:**
A fast producer emits items faster than the subscriber can
process. Without backpressure, items buffer in memory unboundedly.

**Diagnostic:**

```bash
# Monitor heap growth under load
jstat -gcutil <pid> 1000
# Look for: Old Gen growing steadily

# Heap dump analysis
jmap -dump:live,format=b,file=heap.hprof <pid>
# Look for large internal Reactor queue arrays
```

**Fix:**

```java
// BAD: no backpressure strategy
Flux<Event> stream = kafkaConsumer.receive()
    .map(this::processEvent);  // if slow, buffer grows

// GOOD: explicit backpressure strategy
Flux<Event> stream = kafkaConsumer.receive()
    .onBackpressureBuffer(10_000)   // bounded buffer
    .onBackpressureDrop(event ->    // drop if full
        log.warn("Dropped: {}", event.id()))
    .map(this::processEvent);
```

**Prevention:** Always define a backpressure strategy; set buffer
bounds explicitly; monitor queue depth as a key metric.

**3. Context Loss Across Async Boundaries**

**Symptom:**
MDC (logging context), security context, or tracing IDs missing
in logs; `NullPointerException` from context values that were
set before the reactive pipeline.

**Root Cause:**
`ThreadLocal` values don't cross async boundaries — the reactive
pipeline runs on different threads, and the original ThreadLocal
values are absent.

**Diagnostic:**

```bash
# Check logs — tracing IDs or user IDs missing in async ops
# Compare log output between sync and async paths
grep "traceId" application.log | grep "null"
```

**Fix:**

```java
// BAD: ThreadLocal context lost across flatMap
MDC.put("userId", userId);
Mono.fromCallable(() -> fetchUser(userId))
    .flatMap(user -> {
        log.info("User: {}", MDC.get("userId")); // null here!
        return processUser(user);
    });

// GOOD: use Reactor Context for cross-thread context
return Mono.deferContextual(ctx -> {
        String uid = ctx.get("userId");
        log.info("User: {}", uid);  // available here
        return fetchUser(uid);
    })
    .contextWrite(Context.of("userId", userId));
```

**Prevention:** Use Reactor Context (not ThreadLocal) for values
that must survive across async boundaries; configure MDC with
Reactor's MDC support hooks.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Event-Driven Programming` — reactive builds a composable API on top of EDP
- `Functional Programming` — reactive operators are pure functional transforms
- `Synchronous vs Asynchronous` — reactive is fundamentally async

**Builds On This (learn these next):**

- `Spring WebFlux` — Spring's reactive web framework built on Reactor
- `Reactive Streams` — the JVM standard spec reactive libraries implement
- `Backpressure` — the flow control mechanism first-class in reactive systems

**Alternatives / Comparisons:**

- `Event-Driven Programming` — reactive's predecessor; less composable
- `Actor Model` — Akka's alternative: isolated actors with message passing
- `CompletableFuture` — Java's simpler async primitive; no backpressure

---

### 📌 Quick Reference Card

```text
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS │ Composable async data streams with │
│ │ functional operators and backpressure │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT │ Concurrent async I/O composition with │
│ SOLVES │ backpressure; callback hell; thread waste │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT │ The spreadsheet model: declare │
│ │ dependencies, changes propagate auto │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN │ I/O-heavy microservices, streaming APIs, │
│ │ high-concurrency non-blocking systems │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN │ CPU-bound work; small codebases where │
│ │ blocking code is simpler and sufficient │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF │ High throughput + composability vs. │
│ │ debugging complexity + steep learning │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER │ "A spreadsheet: declare relationships, │
│ │ changes flow automatically downstream." │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Spring WebFlux → Reactor Core │
│ │ → Reactive Streams spec │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A Spring WebFlux service uses `flatMap` to call an
external HTTP API for each item in a `Flux` of 10,000 product
IDs. The external API rate-limits to 100 requests/second.
Without any concurrency control, what happens to the external
API and the service's memory? Design the exact operator chain
that respects the rate limit, and explain which operator provides
backpressure vs. which provides concurrency limiting.

**Q2.** A developer migrates a Spring MVC endpoint to WebFlux
for performance. In testing, the WebFlux version is actually
SLOWER than the MVC version for a workload of 10 concurrent
requests, each requiring a 50ms computation. Explain exactly
why this happens — and define the precise workload characteristic
that determines whether WebFlux will be faster or slower than
MVC.
