---
layout: default
title: "Reactive Programming"
parent: "CS Fundamentals — Paradigms"
nav_order: 7
permalink: /cs-fundamentals/reactive-programming/
number: "7"
category: CS Fundamentals — Paradigms
difficulty: ★★☆
depends_on: Functional Programming, Event-Driven Programming, Synchronous vs Asynchronous
used_by: Node.js, Microservices, Concurrency vs Parallelism
tags: #pattern, #architecture, #intermediate, #distributed, #performance
---

# 7 — Reactive Programming

`#pattern` `#architecture` `#intermediate` `#distributed` `#performance`

⚡ TL;DR — A paradigm for composing asynchronous data streams using functional operators, where values propagate automatically when upstream data changes.

| #7              | Category: CS Fundamentals — Paradigms                                         | Difficulty: ★★☆ |
| :-------------- | :---------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Functional Programming, Event-Driven Programming, Synchronous vs Asynchronous |                 |
| **Used by:**    | Node.js, Microservices, Concurrency vs Parallelism                            |                 |

---

### 📘 Textbook Definition

**Reactive programming** is a declarative programming paradigm centred on asynchronous data streams and the propagation of change. A reactive system expresses logic as transformations on streams of values over time, using functional operators (map, filter, flatMap, merge, zip) to compose them. When upstream data changes, downstream computations automatically re-evaluate. Foundational implementations include ReactiveX (RxJava, RxJS), Project Reactor (used in Spring WebFlux), and the Java 9 `Flow` API (based on the Reactive Streams specification).

---

### 🟢 Simple Definition (Easy)

Reactive programming means treating data as a river: values flow through, and you describe what to do with each value as it arrives — filtering, transforming, combining — automatically, as the stream changes over time.

---

### 🔵 Simple Definition (Elaborated)

In traditional event-driven code, you write callbacks — "when this event fires, do this." Reactive programming lifts that to a higher level: you define a _pipeline_ of transformations over a _stream of events_, using the same `map`/`filter`/`reduce` operations from functional programming, but applied to values arriving asynchronously over time. A stock price feed, user input events, or HTTP response chunks are all streams. You compose them with operators: filter out low-volume trades, map price to profit margin, merge two streams from different exchanges. The result is a declarative, composable, automatically-updating computation graph.

---

### 🔩 First Principles Explanation

**The problem: callback composition does not scale.**

Event-driven programming solved the blocking I/O problem, but building complex workflows from callbacks is brittle:

```javascript
// Combine two async operations — callback hell
getUserById(id, (err, user) => {
  if (err) handleError(err);
  getOrdersByUser(user.id, (err, orders) => {
    if (err) handleError(err);
    // error handling duplicated at every level
    // impossible to retry or timeout elegantly
  });
});
```

**The constraint:** Real systems must merge streams, debounce inputs, retry on failure, apply backpressure when a consumer is slow, and compose dozens of async operations — all in a readable, maintainable way.

**The insight:** A stream of asynchronous events is mathematically a collection of values over time. The same functional operators that work on lists (`map`, `filter`, `flatMap`) can work on streams — with the difference that values arrive asynchronously.

**The solution — Observable streams with functional operators:**

```java
// RxJava: compose a pipeline over an async stream
Observable.fromCallable(() -> userService.fetchUser(id))
    .subscribeOn(Schedulers.io())           // async, on IO thread
    .flatMap(user -> orderService.fetchOrders(user.getId()))
    .filter(order -> order.getTotal() > 100)
    .map(Order::getSummary)
    .observeOn(AndroidSchedulers.mainThread())
    .subscribe(
        summary -> updateUI(summary),       // onNext
        error   -> showError(error)         // onError — centralised
    );
```

One pipeline, centralised error handling, declarative intent. Compare to the nested callback version above.

The Reactive Manifesto (2013) extended this to system architecture: responsive, resilient, elastic, and message-driven.

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Reactive Programming:

```java
// Combining two async sources with callbacks
userService.findById(id, (user, err) -> {
    if (err != null) { log(err); return; }
    orderService.findByUser(user, (orders, err2) -> {
        if (err2 != null) { log(err2); return; }
        // duplicated error handling, no timeout, no retry
        // if orders is huge, consumer is overwhelmed
    });
});
```

What breaks without it:

1. Error handling is duplicated at every callback nesting level.
2. Backpressure (slow consumer, fast producer) has no standard mechanism.
3. Composing 5+ async sources produces unreadable pyramids of callbacks.
4. Retry, timeout, and circuit-breaker logic must be hand-coded per operation.

WITH Reactive Programming:
→ A single error handler at the end of the pipeline catches all upstream errors.
→ Backpressure operators (`onBackpressureBuffer`, `onBackpressureDrop`) protect slow consumers.
→ `retry(3)`, `timeout(5s)`, `debounce(300ms)` are one-line operator additions.
→ Merging, zipping, and splitting streams is declarative and composable.

---

### 🧠 Mental Model / Analogy

> Think of a water treatment plant. Raw water (events) flows in from multiple rivers (data sources). It passes through a series of filters and treatment stages (operators): sediment removal (filter), chemical dosing (map), quality testing (validation). Multiple streams merge at various points. The plant automatically reacts to whatever volume arrives — no human manually pulls water from one pipe to the next.

"River water flowing in" = asynchronous data stream
"Treatment stage / filter" = operator (map, filter, flatMap)
"Merging rivers" = `merge()` or `zip()` operator
"Output to distribution" = subscriber (terminal consumer)
"Water volume varying" = backpressure management

The key insight: the _flow_ is automatic and declarative. You configure the pipeline once; it processes all future data without manual intervention.

---

### ⚙️ How It Works (Mechanism)

**Observable / Publisher — Subscriber Contract:**

```
┌───────────────────────────────────────────────┐
│         Reactive Stream Pipeline              │
│                                               │
│  ┌─────────────┐                              │
│  │  Producer   │  emits items over time       │
│  │ (Observable)│                              │
│  └──────┬──────┘                              │
│         │                                     │
│         ▼  operator chain                     │
│  ┌──────────────┐  ┌──────────────┐           │
│  │  map(f)      │→ │  filter(p)   │           │
│  └──────────────┘  └──────┬───────┘           │
│                            │                   │
│         ┌──────────────────┤                   │
│         ▼                  ▼                   │
│  ┌──────────────┐  ┌───────────────┐          │
│  │ flatMap(g)   │  │ onError(...)  │          │
│  └──────┬───────┘  └───────────────┘          │
│         │                                      │
│         ▼                                      │
│  ┌─────────────┐                              │
│  │ Subscriber  │  consumes items              │
│  │ (terminal)  │                              │
│  └─────────────┘                              │
└───────────────────────────────────────────────┘
```

**Backpressure — protecting slow consumers:**

```
Fast Producer:    ─── item ─── item ─── item ─── item ──►
                                                        ↓
                                               ┌────────────┐
                                               │ Buffer /   │
                                               │ Drop /     │
                                               │ Error      │
                                               └────────────┘
                                                        ↓
Slow Consumer:    ─────────── item ──────────── item ──►
```

**Key Operators:**

| Operator      | Purpose                                      |
| ------------- | -------------------------------------------- |
| `map(f)`      | Transform each item                          |
| `filter(p)`   | Drop items not matching predicate            |
| `flatMap(f)`  | Expand one item to a stream, merge results   |
| `merge()`     | Interleave two streams                       |
| `zip()`       | Pair items from two streams                  |
| `debounce(t)` | Emit only if silent for duration `t`         |
| `retry(n)`    | Re-subscribe on error, up to `n` times       |
| `timeout(d)`  | Error if no item emitted within duration `d` |

---

### 🔄 How It Connects (Mini-Map)

```
Functional Programming  +  Event-Driven Programming
              │                        │
              └───────────┬────────────┘
                          ▼
               Reactive Programming
               (you are here)
                          │
          ┌───────────────┼──────────────┐
          ▼               ▼              ▼
      RxJava         Project Reactor    RxJS
    (Android)      (Spring WebFlux)  (Angular)
          │               │
          ▼               ▼
   Backpressure     Microservices
                  (non-blocking APIs)
```

---

### 💻 Code Example

**Example 1 — RxJava: compose async operations:**

```java
// Fetch user, then their orders, filter, transform
userRepository.findById(userId)          // Observable<User>
    .flatMap(user ->
        orderRepository.findByUser(user)) // Observable<Order>
    .filter(order -> order.isActive())    // keep active only
    .map(Order::toSummaryDTO)             // transform
    .take(10)                             // first 10 only
    .subscribeOn(Schedulers.io())         // async on IO thread
    .observeOn(Schedulers.computation())  // process on CPU pool
    .subscribe(
        dto   -> results.add(dto),        // onNext
        error -> log.error("Failed", error), // onError
        ()    -> sendResponse(results)    // onComplete
    );
```

**Example 2 — Spring WebFlux (Project Reactor):**

```java
// Non-blocking REST endpoint returning a Flux (stream)
@GetMapping("/orders")
public Flux<OrderDTO> getOrders(@RequestParam String userId) {
    return orderService.findByUser(userId)  // Flux<Order>
        .filter(Order::isActive)
        .map(orderMapper::toDTO)
        .onErrorResume(ex ->
            Flux.error(new ResponseStatusException(
                HttpStatus.INTERNAL_SERVER_ERROR)));
}
```

**Example 3 — Backpressure handling:**

```java
// BAD: no backpressure — subscriber overwhelmed
Observable.range(1, 1_000_000)
    .observeOn(Schedulers.computation())
    .subscribe(n -> Thread.sleep(10)); // too slow — MissingBackpressureException

// GOOD: buffer backpressure — absorb bursts
Flowable.range(1, 1_000_000)
    .onBackpressureBuffer(1000)         // buffer up to 1000 items
    .observeOn(Schedulers.computation())
    .subscribe(n -> Thread.sleep(10));  // safe
```

---

### ⚠️ Common Misconceptions

| Misconception                                            | Reality                                                                                                                                                               |
| -------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Reactive programming is just callbacks with nicer syntax | Reactive programming adds operator composition, backpressure, declarative error handling, and stream merging — qualitatively more powerful                            |
| Reactive systems are always faster                       | Non-blocking adds overhead for CPU-bound tasks; gains appear with I/O-bound workloads where threads would otherwise block                                             |
| `Observable` and `Flowable` are interchangeable          | `Observable` has no backpressure support; `Flowable` implements the Reactive Streams spec with backpressure — use `Flowable` for high-volume or unbounded sources     |
| Reactive programming eliminates all async complexity     | It restructures the complexity into a different model; debugging reactive pipelines requires understanding the operator chain and subscription lifecycle              |
| Spring WebFlux is always better than Spring MVC          | WebFlux shines for I/O-heavy, high-concurrency APIs; for CPU-bound or database-heavy synchronous workloads, Spring MVC with a thread pool is simpler and often faster |

---

### 🔥 Pitfalls in Production

**Blocking calls inside a reactive pipeline**

```java
// BAD: blocking DB call inside reactive pipeline freezes scheduler thread
Mono.fromCallable(() -> userRepository.findByIdBlocking(id)) // BLOCKS
    .subscribeOn(Schedulers.single()) // single-thread scheduler now stalled
    .subscribe(user -> process(user));

// GOOD: use reactive repository or boundedElastic scheduler for blocking
Mono.fromCallable(() -> userRepository.findByIdBlocking(id))
    .subscribeOn(Schedulers.boundedElastic()) // thread pool for blocking ops
    .subscribe(user -> process(user));
```

---

**Forgetting to subscribe — cold observables do nothing until subscribed**

```java
// BAD: pipeline defined but never subscribed — nothing executes
Flux<User> users = userService.findAll()
    .filter(User::isActive)
    .map(User::toDTO);
// No .subscribe() or .block() — this is a declaration, not execution

// GOOD: trigger execution by subscribing
userService.findAll()
    .filter(User::isActive)
    .map(User::toDTO)
    .subscribe(dto -> results.add(dto));
```

---

**Missing error handling causing silent stream termination**

```java
// BAD: unhandled error terminates the stream silently
stream.subscribe(item -> process(item));
// If process() throws, the stream terminates with no error logged

// GOOD: always handle onError
stream.subscribe(
    item  -> process(item),
    error -> log.error("Stream error", error), // onError
    ()    -> log.info("Stream complete")        // onComplete
);
```

---

### 🔗 Related Keywords

- `Functional Programming` — reactive is FP applied to streams over time; operators like `map` and `filter` are direct imports
- `Event-Driven Programming` — the paradigm reactive extends with composable, backpressured stream operators
- `Synchronous vs Asynchronous` — reactive pipelines are inherently asynchronous; understanding this distinction is a prerequisite
- `Backpressure` — the mechanism that protects slow consumers from fast producers; native to the Reactive Streams spec
- `Observer Pattern` — the design pattern underlying the Observable/Subscriber relationship
- `Concurrency vs Parallelism` — reactive achieves high concurrency via non-blocking I/O, not parallelism
- `Microservices` — reactive HTTP clients (WebClient) enable non-blocking microservice communication
- `Node.js` — built on an event loop that embodies reactive principles in JavaScript

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Compose async data streams with           │
│              │ functional operators; change propagates   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ High-concurrency I/O, real-time data,     │
│              │ composing multiple async sources          │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ CPU-bound work; simple request/response   │
│              │ with no fan-out or stream merging         │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Reactive is to callbacks what algebra    │
│              │ is to arithmetic — composition at scale." │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ RxJava → Project Reactor → Backpressure   │
│              │ → Spring WebFlux → Kafka Streams          │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A Spring WebFlux service makes three parallel downstream API calls using `Flux.zip()` and combines the results. One of the three APIs consistently responds in 2 seconds while the others respond in 50ms. Describe exactly what happens to throughput and latency for every request through this endpoint, and what operator strategies exist to mitigate the slow dependency.

**Q2.** A reactive Kafka consumer using Project Reactor processes 100,000 messages per second. The downstream database write takes 5ms per message. With no backpressure configuration, what failure mode occurs at the subscriber, how does the Reactive Streams `Subscription.request(n)` protocol prevent it, and what is the trade-off of setting the request size too low vs too high?
