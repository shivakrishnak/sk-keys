---
id: JCC-075
title: Reactive Streams Specification
category: Java Concurrency
tier: tier-3-java
folder: JCC-java-concurrency
difficulty: ★★★
depends_on: JCC-059, JCC-073, JCC-029
used_by:
related: JCC-014, JCC-060, JCC-044
tags:
  - java
  - concurrency
  - async
  - advanced
  - protocol
status: complete
version: 2
layout: default
parent: "Java Concurrency"
grand_parent: "Technical Dictionary"
nav_order: 75
permalink: /java-concurrency/reactive-streams-specification/
---

# JCC-075 - REACTIVE STREAMS SPECIFICATION

⚡ **TL;DR** - Reactive Streams is the standard protocol for async
stream processing with non-blocking backpressure - the specification
behind `java.util.concurrent.Flow`, Project Reactor, and RxJava.

---

| Field      | Value                                              |
|------------|----------------------------------------------------|
| Depends on | JCC-059 CompletableFuture Composition, JCC-073 Project Loom, JCC-029 ExecutorService |
| Related    | JCC-014 CompletableFuture, JCC-060 Parallel Streams, JCC-044 Structured Concurrency |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Async I/O can produce data faster than a consumer can process it.
Without flow control, the producer fills an unbounded queue until
`OutOfMemoryError`. The only alternative - blocking the producer -
negates async benefits. Different libraries (Netflix RxJava,
Typesafe Akka Streams, Pivotal Project Reactor) each invented
their own incompatible backpressure protocols.

**THE BREAKING POINT:**
A microservice calls a streaming API via RxJava, pipes it through
an Akka Streams processing stage, and writes to a Reactor-based
database client. Each stage uses a different backpressure interface.
Integration requires adapter layers, defeating stream composability.
The ecosystem is fragmented.

**THE INVENTION MOMENT:**
Engineers from Netflix, Pivotal, Red Hat, Twitter, and other
organisations formed the Reactive Streams initiative (2013-2015),
defining a single 4-interface specification that all reactive
libraries must implement. Java 9 incorporated it as
`java.util.concurrent.Flow`.

**EVOLUTION:**
- **2013-2015:** Reactive Streams community specification (4 interfaces)
- **2017 / Java 9:** `java.util.concurrent.Flow` adopts the spec
- **Now:** Project Reactor (Spring), RxJava 3, Akka Streams, Vert.x
  all interoperate via the spec
- **2024:** Virtual threads offer a simpler model for many async cases

---

### 📘 Textbook Definition

**Reactive Streams** is a specification defining 4 interfaces for
asynchronous stream processing with non-blocking backpressure:

```java
// Publisher: source of elements
interface Publisher<T> {
    void subscribe(Subscriber<? super T> subscriber);
}

// Subscriber: consumer of elements
interface Subscriber<T> {
    void onSubscribe(Subscription s); // first callback
    void onNext(T item);              // each element
    void onError(Throwable t);        // terminal error
    void onComplete();                // terminal success
}

// Subscription: demand and cancellation control
interface Subscription {
    void request(long n); // request n more elements
    void cancel();        // stop receiving elements
}

// Processor: both Publisher and Subscriber (transformation)
interface Processor<T, R> extends Subscriber<T>, Publisher<R> {}
```

**Laws:** 107 rules in the spec ensuring correctness (e.g., signals
must be sequential, `onError`/`onComplete` are terminal).

---

### ⏱️ Understand It in 30 Seconds

**One line:** A standard protocol for streaming data where the
consumer controls how fast the producer sends - preventing
overwhelming a slow consumer.

**One analogy:**
> A water pipe with a valve. The subscriber opens the valve to
> request water (demand). The publisher pushes water only when
> the valve is open. If the subscriber is full, it closes the valve.
> The pipe never overflows. The valve is `Subscription.request(n)`.

**One insight:** Backpressure flows *upstream* - the consumer
tells the producer its capacity. This is the opposite of traditional
push APIs where producers push at will.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. A `Publisher` may only send elements in response to `request(n)`
   from the `Subscriber`. It must never send more than requested.
2. Signals (`onNext`, `onError`, `onComplete`) must be sequential -
   the spec forbids concurrent signals to the same `Subscriber`.
3. `onError` and `onComplete` are terminal - no signals after them.
4. `cancel()` on the `Subscription` tells the publisher to stop;
   the publisher SHOULD stop, but may send a few more `onNext`
   signals before stopping (they MUST be ignored by the subscriber).
5. `request(Long.MAX_VALUE)` effectively disables backpressure
   (unbounded demand).

**DERIVED DESIGN:**
The pull-push hybrid: publisher pushes elements, subscriber pulls
by declaring demand. This prevents both overflow (unbounded push)
and deadlock (purely synchronous pull blocking queues).

**THE TRADE-OFFS:**

**Gain:** Memory-safe streaming; standard interoperability between
libraries; composable pipelines from different vendors.

**Cost:** Complex to implement correctly (107 rules); stack space
from deep operator chains (operator fusion addresses this); debugging
reactive pipelines is non-trivial.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

**Essential:** Any async stream protocol must address the slow-
consumer problem. Backpressure is the standard solution.

**Accidental:** 107 rules is much higher than necessary for a simple
protocol. Some rules exist because of historical implementation
edge cases in specific libraries.

---

### 🧪 Thought Experiment

**SETUP:** A fast file reader publishes 1 million lines, but the
consumer writes each to a slow database (100ms per line).

**WITHOUT backpressure:**
```
Publisher sends all 1M lines immediately
Consumer receives them faster than it can write
Buffer fills: 1M * ~200 bytes = 200MB queue
OOM at ~500k lines
OR: producer blocked (sync) negating async benefit
```

**WITH Reactive Streams:**
```
Consumer: request(10) -- "I can handle 10 at a time"
Publisher: send 10 lines
Consumer: writes 10 to DB (100ms each = 1 second)
Consumer: request(10) -- "ready for more"
Publisher: send 10 lines
... 
Memory: only 10 lines buffered at any time
Total memory: ~2KB regardless of total file size
```

**THE INSIGHT:** Demand flows upstream. Memory is bounded by
`request(n)` regardless of data source size.

---

### 🧠 Mental Model / Analogy

> Reactive Streams is like a restaurant's kitchen-to-table protocol.
> The table (subscriber) signals the waiter (subscription) "we're
> ready for the next course." The kitchen (publisher) holds dishes
> until signalled. Courses arrive at the pace the table eats, not
> the kitchen cooks. The kitchen never stacks 10 courses on the table
> at once.

**Element mapping:**
- Kitchen = Publisher (produces elements)
- Table = Subscriber (consumes elements)
- "Ready for next course" signal = `Subscription.request(1)`
- Dish delivered = `onNext(item)`
- "No more courses" = `onComplete()`
- Allergic reaction = `onError(exception)`
- Leaving the restaurant = `cancel()`

Where this analogy breaks down: `request(n)` allows the kitchen
to batch multiple dishes (n > 1); real course-by-course delivery
is always n=1.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
A standard way for two components to stream data where the receiver
tells the sender "send me 10 items" rather than the sender pushing
as fast as it can.

**Level 2 - How to use it (junior developer):**
```java
// Use an implementation like Project Reactor:
Flux.fromIterable(largeList)
    .flatMap(item -> Mono.fromCallable(() -> process(item)))
    .subscribe(
        result -> save(result),
        error  -> log.error(error),
        ()     -> log.info("Done")
    );
// Reactor handles backpressure protocol internally
```

**Level 3 - How it works (mid-level engineer):**
When you call `subscribe()`, the `Publisher` calls `onSubscribe(subscription)`.
Your `Subscriber.onSubscribe()` implementation calls `subscription.request(n)`.
The publisher may immediately begin calling `onNext(item)` up to n
times. When done responding to demand, it stops calling `onNext`.
Your `onNext()` can call `request(1)` again to get the next item.
This demand protocol flows synchronously in the simplest case, or
asynchronously via a `Scheduler` (executor).

**Level 4 - Why it was designed this way (senior/staff):**
The pull-push hybrid avoids two extremes: pure push overflows slow
consumers; pure pull blocks the caller. The demand `n` design
allows batching (request 128, get 128 items in a burst) which is
critical for performance - one `request()` per `onNext()` is too
slow for high-throughput streams. Operator fusion (combining
adjacent operators into a single operator) further reduces the
overhead of the request/onNext ping-pong protocol.

**Expert Thinking Cues:**
- `subscribeOn(scheduler)` changes which thread calls `subscribe()`.
  `publishOn(scheduler)` changes which thread calls `onNext()`.
  Many bugs result from confusing these.
- `Flux.create()` (with sink) vs `Flux.generate()`: create allows
  multiple emissions per subscriber request; generate is pull-based
  (one emission per request).
- Default buffer size in Reactor operators: 256. Configurable.
  Affects how many items are fetched ahead.
- Java 9's `Flow` API: identical to Reactive Streams but in JDK.
  `java.util.concurrent.SubmissionPublisher` is the JDK publisher.

---

### ⚙️ How It Works (Mechanism)

**Signal sequence:**
```
Subscriber --subscribe()--> Publisher
Publisher  --onSubscribe(sub)--> Subscriber

Subscriber --sub.request(n)--> Publisher
Publisher  --onNext(item1)--> Subscriber
Publisher  --onNext(item2)--> Subscriber
...up to n times...

Subscriber --sub.request(n)--> Publisher
...repeats...

Publisher  --onComplete()--> Subscriber  [happy path]
Publisher  --onError(t)---> Subscriber  [failure path]
```

**Operator chain (Reactor Flux):**
```
source.map(f).filter(p).take(10).subscribe(s)

Wired as:
  source -> MapOperator -> FilterOperator -> TakeOperator -> s

request(10) flows UPSTREAM from s to source:
  s.request(10)
  -> TakeOperator.request(10)
  -> FilterOperator.request(10)
  -> MapOperator.request(10)
  -> source.request(10)

onNext(item) flows DOWNSTREAM from source to s
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
Subscriber.subscribe(publisher)      <- YOU ARE HERE
       |
Publisher: onSubscribe(subscription)
       |
Subscriber: subscription.request(10)
       |
Publisher: emit 10 x onNext()
       |
Subscriber: processes 10 items
Subscriber: subscription.request(10) [repeat]
       |
Publisher: source exhausted -> onComplete()
       |
Subscriber: onComplete() -> done
```

**FAILURE PATH:**
```
Publisher encounters error
  -> onError(throwable)
  -> subscriber handles in onError() handler
  -> subscription is terminal (no more signals)
```

**WHAT CHANGES AT SCALE:**
- Hot vs cold publishers: cold publishers replay from the start
  per subscriber; hot publishers emit regardless of subscribers
  (e.g., event bus). Most DB query publishers are cold.
- Multicasting: `publish()` + `refCount()` or `share()` allow
  multiple subscribers to share one upstream subscription.

---

### 💻 Code Example

**BAD - unbounded push without backpressure:**
```java
// BAD: producer ignores consumer capacity
Observable<Data> obs = Observable.create(emitter -> {
    while (hasData()) {
        emitter.onNext(nextData()); // pushes at full speed
    }
    emitter.onComplete();
});
obs.subscribe(data -> slowProcess(data)); // OOM risk
```

**GOOD - Reactor Flux with controlled demand:**
```java
// GOOD: Reactor handles backpressure internally
Flux<Data> source = Flux.create(sink -> {
    while (hasData() && !sink.isCancelled()) {
        sink.next(nextData());
    }
    sink.complete();
});

source
    .publishOn(Schedulers.boundedElastic()) // off main thread
    .map(this::transform)
    .flatMap(data ->
        Mono.fromCallable(() -> dbClient.save(data)),
        8) // max 8 concurrent saves
    .subscribe(
        saved -> log.info("Saved: {}", saved),
        error -> log.error("Failed", error),
        ()    -> log.info("All done")
    );
```

**GOOD - Java 9 Flow API:**
```java
// GOOD: JDK built-in Reactive Streams
SubmissionPublisher<String> publisher =
    new SubmissionPublisher<>();

publisher.subscribe(new Flow.Subscriber<>() {
    private Flow.Subscription sub;
    public void onSubscribe(Flow.Subscription s) {
        sub = s;
        s.request(10); // request 10 items to start
    }
    public void onNext(String item) {
        process(item);
        sub.request(1); // request one more after each
    }
    public void onError(Throwable t) { handle(t); }
    public void onComplete() { cleanup(); }
});

// Publish items:
publisher.submit("item1");
publisher.submit("item2");
publisher.close(); // triggers onComplete
```

**How to verify:**
```java
@Test
void backpressureLimitsMemory() {
    AtomicInteger maxBuffered = new AtomicInteger(0);
    AtomicInteger currentBuffered = new AtomicInteger(0);

    Flux.range(1, 1_000_000)
        .doOnNext(i -> {
            int current = currentBuffered.incrementAndGet();
            maxBuffered.accumulateAndGet(current, Math::max);
        })
        .flatMap(i -> Mono.fromCallable(() -> {
            Thread.sleep(1); // simulate slow consumer
            currentBuffered.decrementAndGet();
            return i;
        }), 16) // concurrency 16
        .blockLast();

    // Max buffered should be bounded by concurrency + buffer
    assertThat(maxBuffered.get()).isLessThan(300);
}
```

---

### ⚖️ Comparison Table

| Library | Reactive Streams | Java version | Main use case |
|---------|-----------------|-------------|--------------|
| `java.util.concurrent.Flow` | Yes (is the spec) | Java 9+ | JDK stdlib integration |
| Project Reactor | Yes (`Flux`, `Mono`) | Java 8+ | Spring WebFlux |
| RxJava 3 | Yes | Java 8+ | Android, general reactive |
| Akka Streams | Yes | Java 8+ (Scala/Java) | Akka actor ecosystem |
| Mutiny (Quarkus) | Yes | Java 11+ | Quarkus framework |
| `CompletableFuture` | No (single value) | Java 8+ | Single async result |
| Parallel Streams | No (no backpressure) | Java 8+ | Batch CPU processing |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Reactive Streams is faster than blocking code" | It enables higher concurrency, not lower per-request latency. A reactive pipeline for a single request is often SLOWER than blocking due to operator overhead. |
| "Project Reactor and RxJava are Reactive Streams implementations, not the spec" | Correct: Reactive Streams IS the 4-interface spec. Project Reactor and RxJava are implementations that add rich operator APIs on top. |
| "`subscribe()` is synchronous" | By default with cold publishers, it may be synchronous. With `publishOn()` or `subscribeOn()`, it runs on a separate scheduler thread. |
| "Backpressure prevents all OOM errors" | It prevents producer-driven OOM. OOM can still happen from unbounded `flatMap` concurrency (`flatMap(f)` with default 256 concurrency buffers 256 elements per upstream item). |
| "`java.util.concurrent.Flow` = Project Reactor" | `Flow` is the standard 4-interface API in the JDK. Reactor uses it as its interop layer but provides a completely separate, rich `Flux/Mono` API. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: OOM from unbounded flatMap concurrency**

**Symptom:** OOM from many `Flux` items with high `flatMap` concurrency.

**Root Cause:** `flatMap(f)` default concurrency = 256. For 1M
items, up to 256 are in-flight simultaneously, each potentially
with an internal buffer.

**Fix:**
```java
// Limit concurrency:
flux.flatMap(f, 8) // max 8 concurrent inner publishers
// Or use concatMap for sequential (no concurrency):
flux.concatMap(f) // one at a time, ordered
```

---

**Failure Mode 2: Subscriber never receives items**

**Symptom:** `subscribe()` called, no `onNext()` triggered.

**Root Cause:** `request(n)` never called. The `onSubscribe` method
either forgot to call `request()` or the first request is delayed
by a condition that never becomes true.

**Diagnostic:**
```java
// Add doOnRequest to trace demand:
source.doOnRequest(n ->
    log.debug("Downstream requested: {}", n))
    .subscribe(...);
// If never logs, subscriber isn't requesting
```

---

**Failure Mode 3: publishOn/subscribeOn confusion**

**Symptom:** I/O operations block the event loop; or operations
run on wrong threads.

**Root Cause:** `subscribeOn` affects where the subscribe/upstream
runs; `publishOn` affects where downstream operators run. Using
wrong one causes I/O on event loop thread.

**Fix:**
```java
// I/O intensive upstream: subscribeOn
Flux.fromCallable(() -> readFile())   // I/O
    .subscribeOn(Schedulers.boundedElastic()) // run on I/O thread
    .map(data -> transform(data))     // runs on I/O thread too
    .publishOn(Schedulers.parallel()) // switch to CPU thread
    .map(data -> cpuProcess(data))    // runs on CPU thread
    .subscribe(result -> save(result));
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[JCC-059 - CompletableFuture Composition Patterns]] - single-
  value async; Reactive Streams extends to multi-value streams
- [[JCC-029 - ExecutorService]] - the thread pool that schedulers
  wrap

**Builds On This (learn these next):**
- Spring WebFlux documentation - Reactor applied to web
- Project Reactor reference guide - operators and backpressure

**Alternatives / Comparisons:**
- [[JCC-073 - Project Loom Design Rationale]] - virtual threads
  as a simpler model for many reactive use cases
- [[JCC-060 - Parallel Streams]] - CPU-bound batch processing
  with no backpressure

---

### 📌 Quick Reference Card

```
+--------------------------------------------------+
| WHAT IT IS   | 4-interface spec for async streams |
|              | with non-blocking backpressure     |
+--------------+------------------------------------+
| PROBLEM      | Fast publishers OOM slow consumers;|
|              | incompatible reactive library APIs |
+--------------+------------------------------------+
| KEY INSIGHT  | request(n) signals demand upstream;|
|              | publisher sends MAX n items        |
+--------------+------------------------------------+
| USE WHEN     | Streaming data with variable rates,|
|              | Spring WebFlux, Kafka consumers    |
+--------------+------------------------------------+
| AVOID WHEN   | Simple single-value async (use CF);|
|              | CPU-bound batch (use parallelStream)|
+--------------+------------------------------------+
| TRADE-OFF    | Memory-safe streaming / complexity;|
|              | hard to debug; stack overflow risk |
+--------------+------------------------------------+
| ONE-LINER    | Publisher -> Subscription.request(n)|
|              | -> onNext * n -> onComplete        |
+--------------+------------------------------------+
| NEXT EXPLORE | Project Reactor Flux/Mono guide,   |
|              | java.util.concurrent.Flow          |
+--------------------------------------------------+
```

**If you remember only 3 things:**
1. `request(n)` is how the subscriber controls flow - the publisher
   must NOT send more than `n` items.
2. `onError` and `onComplete` are terminal - no more signals after
   either.
3. `subscribeOn` controls the upstream thread; `publishOn` controls
   the downstream thread - confusing them causes I/O on event loops.

**Interview one-liner:** "Reactive Streams defines the 4-interface
pull-push backpressure protocol (Publisher, Subscriber, Subscription,
Processor) where subscribers declare demand via `request(n)`,
preventing producers from overwhelming slow consumers - standardised
in Java 9 as `java.util.concurrent.Flow`."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** In any producer-consumer
pipeline, explicit demand flow is more robust than implicit
buffering with overflow handling. Declaring capacity requirements
upstream prevents overflow; reactive systems handle this at the
protocol level rather than the application level.

**Where else this pattern appears:**
- **TCP flow control:** TCP's receive window (similar to `request(n)`)
  tells the sender how much data the receiver can accept. Same
  pull-push hybrid preventing sender from flooding receiver.
- **Kafka consumer `poll(maxRecords)`:** The consumer controls
  how many records it fetches per poll. The broker holds records
  until requested. This is Reactive Streams backpressure at the
  messaging layer.
- **gRPC streaming:** Client-side streaming gRPC uses flow control
  based on HTTP/2 WINDOW_UPDATE frames - the exact same mechanism
  as Reactive Streams `request(n)` translated to network protocol.

---

### 💡 The Surprising Truth

Despite being the foundation of Spring WebFlux and virtually every
modern Java streaming library, the Reactive Streams specification
contains only 4 interfaces and 107 rules - and the entire spec
fits in a few hundred lines of Java. Its designers deliberately
kept the interfaces minimal (no utility methods, no convenient
defaults) to ensure maximum implementability across different
programming languages. The same 4 interfaces were implemented in
JavaScript (rxjs), Scala (Akka), Kotlin (kotlinx.coroutines Flow),
and eventually Java (Flow). But the technology choice has a
consequence: every time you use a rich Reactor or RxJava API, you
are using an enormous operator library built on top of a 4-interface
specification thin enough to fit on a single page.

---

### 🧠 Think About This Before We Continue

**Question 1 (System Interaction):** A Reactor `Flux` pipeline
reads records from Kafka (unbounded), applies a CPU-heavy
transformation, and writes to a database. The Kafka consumer is
faster than the DB writer. Describe exactly which Reactor operator
applies backpressure between the three stages, and what happens
if no backpressure is applied and the DB is 10x slower than Kafka.

*Hint:* Explore `flatMap` concurrency limits, `limitRate()`,
and how Reactor's `FluxFlatMap` internal buffer size interacts
with DB write latency. Research what `MissingBackpressureException`
means and when it is thrown.

---

**Question 2 (Design Trade-off):** After Java 21's virtual threads,
your team debates whether to replace Reactor `Mono/Flux` pipelines
with blocking code on virtual threads. The service has 5,000
concurrent requests, each spending 80ms on DB and 20ms on CPU.
Quantify the memory and throughput difference between reactive and
virtual threads approaches and identify one scenario where reactive
still wins.

*Hint:* Calculate reactor operator chain memory overhead (each
operator has state) vs virtual thread continuation overhead (~2-4KB
each). Identify backpressure as the remaining reactive advantage
for scenarios where fast producers must not overwhelm slow consumers
even with virtual threads.

---

**Question 3 (Root Cause):** A `Flux` pipeline processes events
from 100 upstream publishers merged with `Flux.merge()`. Under
normal load (100 events/sec total), memory is stable. Under spike
load (10,000 events/sec), memory grows unbounded and OOM occurs
after 2 minutes. The pipeline uses `flatMap(processEvent)`. What
is the exact memory accumulation mechanism, and what operator change
resolves it?

*Hint:* `Flux.merge()` aggregates 100 publishers with no concurrency
limit. `flatMap` has default concurrency = 256 with an internal
`SpscLinkedArrayQueue`. Calculate: 100 publishers * 256 internal
buffers * event size. Explore `merge(maxConcurrency)` and
`flatMap(f, maxConcurrency, prefetch)` to bound memory.

