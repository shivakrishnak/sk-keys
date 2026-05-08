---
layout: default
title: "Backpressure (Spring)"
parent: "Spring Core"
nav_order: 54
permalink: /spring/backpressure-spring/
id: SPR-054
category: Spring Core
difficulty: ★★★
depends_on: Reactive Streams, Mono / Flux, WebFlux / Reactive
used_by: Flow Control, Rate Limiting, Stream Processing
related: Bounded Queues, Circuit Breaker, Rate Limiting
tags:
  - spring
  - java
  - performance
  - reliability
  - reactive
---

# SPR-054 — Backpressure (Spring)

⚡ TL;DR — Backpressure is the mechanism by which a slow consumer signals a fast producer to slow down, preventing unbounded memory growth — `Flux` implements it via the Reactive Streams `request(n)` protocol.

| #406            | Category: Spring Core                             | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------ | :-------------- |
| **Depends on:** | Reactive Streams, Mono / Flux, WebFlux / Reactive |                 |
| **Used by:**    | Flow Control, Rate Limiting, Stream Processing    |                 |
| **Related:**    | Bounded Queues, Circuit Breaker, Rate Limiting    |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A producer emits stock price updates at 100,000 events/second. A subscriber processes each event by writing to a database that handles 1,000 writes/second. Without backpressure, the 99,000 events/second surplus must go somewhere — they're buffered in memory. After 10 seconds: 990,000 buffered events × ~500 bytes each = ~495MB buffer. After 30 seconds: heap exhausted, `OutOfMemoryError`. The application crashes.

**THE BREAKING POINT:**
Any push-based system where producers and consumers operate at different speeds hits this wall. The producer doesn't know the consumer is overwhelmed — it keeps pushing. Memory is the only buffer, and memory is finite.

**THE INVENTION MOMENT:**
"This is exactly why backpressure was invented."

---

### 📘 Textbook Definition

**Backpressure** (in the context of reactive streams) is a flow control mechanism that allows a downstream consumer (subscriber) to signal to an upstream producer (publisher) how many items it's prepared to receive. In Project Reactor / Spring WebFlux, backpressure is implemented via the Reactive Streams `Subscription.request(n)` protocol: the subscriber calls `request(n)` to demand n items; the publisher emits at most n items before waiting for the next `request()`. When the upstream source cannot comply with backpressure (e.g., a hot source like a socket or Kafka topic that emits regardless of demand), Reactor provides explicit overflow strategies: `onBackpressureBuffer()` (buffer excess), `onBackpressureDrop()` (drop excess), `onBackpressureError()` (fail fast), and `onBackpressureLatest()` (keep only most recent).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Backpressure lets a slow subscriber tell a fast publisher "I'm only ready for 10 more, hold the rest."

**One analogy:**

> Backpressure is like a restaurant where the kitchen only starts cooking the next dish when the server signals "table is ready for the next course." Without backpressure: the kitchen prepares all 6 courses simultaneously, the server is overwhelmed carrying plates, and the table can't eat fast enough. The food piles up (memory buffer) and eventually falls on the floor (OOM crash).

**One insight:**
Backpressure is not about slowing down the producer permanently — it's about the producer respecting the consumer's processing capacity in real time. When the consumer speeds up, it requests more. When it slows, it requests fewer.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. The Reactive Streams `request(n)` protocol: a publisher may not emit more items than the subscriber has requested. This invariant is enforced by the `Subscription` contract.
2. Backpressure operates in-process between pipeline operators. Once data crosses an asynchronous boundary (network, Kafka, WebSocket), the `request(n)` protocol cannot directly throttle the external source.
3. At asynchronous boundaries, overflow strategies are required: buffer, drop, error, or latest.

**DERIVED DESIGN:**
Within a single Reactor pipeline (same JVM, same thread context), backpressure is automatic: each operator requests items from its upstream based on its own demand. For example, `Flux.range(1, 1000).map(i -> process(i)).subscribe(item -> slowConsumer(item))` will naturally pace the emission because the subscriber's `onNext` must complete before `request(1)` is issued for the next item.

The challenge arises at source boundaries: a Kafka consumer, a WebSocket, or a hot `Flux.interval()` emits regardless of downstream demand. These require explicit bridging:

- `Sinks.Many` with bounded buffer: producers fail when buffer is full
- `onBackpressureBuffer(maxSize, overflow strategy)`: control what happens when buffer is exceeded
- `limitRate(n)`: subscriber requests items in batches of n

**THE TRADE-OFFS:**
**Gain:** Bounded memory usage under load; system stays stable under bursts; prevents cascade failures from overwhelming downstream services.
**Cost:** Complexity — you must choose and configure overflow strategies correctly; the cost of slowing producers may be dropped events or increased latency; debugging backpressure issues requires understanding the entire pipeline's demand chain.

---

### 🧪 Thought Experiment

**SETUP:**
A WebFlux endpoint streams 1 million records from a database to an HTTP client. The client reads responses at 1,000 records/second. The database can emit 10,000 records/second. With backpressure:

**WHAT HAPPENS:**

1. HTTP client requests a chunk of data (e.g., reads 8KB TCP window).
2. WebFlux reads 8KB into TCP buffer; once buffer is full, TCP stops reading.
3. Netty's NIO selector: no more room to write to socket → Flux stops requesting from database.
4. Database cursor pauses; no new records fetched.
5. Client reads 8KB → TCP window opens → Netty writes more → Flux requests more from DB.
6. Memory footprint: constant ~8KB TCP buffer. NOT 1 million records in heap.

**WITHOUT BACKPRESSURE (collecting all to list first):**

1. JPA `findAll()` loads all 1 million records into `List<User>` — potentially GBs of memory.
2. All loaded before sending a single byte to the client.
3. OutOfMemoryError possible before the stream even starts.

**THE INSIGHT:**
Backpressure enables constant-memory streaming of arbitrarily large datasets by flowing data through the pipeline at the rate the slowest consumer can accept.

---

### 🧠 Mental Model / Analogy

> Backpressure is like a water pipe with a pressure regulator. The water company (producer) has infinite water pressure. Your home pipes (consumer) can only handle 60 PSI. Without a pressure regulator: pipes burst (OOM crash). With a pressure regulator: the regulator signals the supply to maintain exactly 60 PSI at the tap. When you open more taps (demand increases), the regulator allows more flow. When all taps close, the regulator shuts off supply.

- "Water company with infinite pressure" → fast producer (database, Kafka)
- "Pipe pressure limit" → consumer's processing capacity
- "Pressure regulator" → Reactive Streams `request(n)` / backpressure operator
- "Opening taps" → subscriber calling `request(n)` for more items
- "Pipes burst" → OutOfMemoryError from unbounded buffer

Where this analogy breaks down: unlike a pressure regulator which continuously adjusts, Reactive Streams backpressure operates in discrete batches — `request(n)` asks for n items, and the publisher emits up to n before waiting.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Backpressure is a way for a slow receiver to tell a fast sender "slow down — I'm not ready for more yet." In reactive streams, it prevents fast data producers from overwhelming slow consumers and crashing the application with memory overflow.

**Level 2 — How to use it (junior developer):**
In Spring WebFlux, backpressure is mostly automatic within a properly composed Reactor pipeline — don't use `Flux.collectList()` (defeats backpressure by loading everything), use `flatMap` with concurrency limits, and use `onBackpressureBuffer(size)` when you have a hot source. Use `limitRate(prefetch)` to control batch request sizes. Use `StepVerifier.withVirtualTime()` in tests to verify backpressure behavior.

**Level 3 — How it works (mid-level engineer):**
When a subscriber calls `subscription.request(n)`, this demand flows up through the operator chain — each operator translates demand from downstream into demand for its upstream. `flatMap(f, concurrency=10)` translates "subscriber wants 1 item" into "subscribe to up to 10 inner publishers simultaneously, request 1 from each." `buffer(100)` translates "subscriber wants 1 batch" into "request 100 items from upstream and group them." At hot-cold boundaries (e.g., `Sinks.Many.tryEmitNext()` returns `FAIL_OVERFLOW` when the buffer is full), the producer must decide: block, drop, or fail.

**Level 4 — Why it was designed this way (senior/staff):**
The Reactive Streams specification was born from a collaboration at the JVM reactive ecosystem's "pain point": every reactive library had its own approach to flow control, and when you connected two different libraries in a pipeline, you had an impedance mismatch. The `request(n)` protocol is the minimum necessary API to enable cross-library backpressure. The decision to use pull (subscriber requests) rather than push (producer checks consumer capacity) was deliberate: pull is composable — operators can combine demand signals without violating producer assumptions. Reactor's `limitRate(prefetch)` is an optimization that reduces the "request-one, get-one" overhead by pre-fetching in batches while maintaining the backpressure contract.

---

### ⚙️ How It Works (Mechanism)

```
BACKPRESSURE REQUEST(N) PROTOCOL FLOW:

Subscriber ← Subscription ← Operator ← Operator ← Publisher

1. subscriber.subscribe(publisher)
   → publisher.subscribe(subscriber) [sets up Subscription]

2. subscriber.onSubscribe(subscription)
   → subscriber calls: subscription.request(10)
   ← upstream request propagates: each operator requests from its upstream

3. publisher emits: onNext(item1), onNext(item2)... (up to 10)
   → subscriber.onNext(item1): processes item
   → subscriber.onNext(item2): processes item...
   (publisher STOPS after 10 items, waits for next request)

4. subscriber processes 10 items → calls subscription.request(10) again
   → publisher emits next 10 items

── HOT SOURCE BOUNDARY (cannot honor request(n)): ──

   Kafka consumer emits at 1000/sec regardless of request(n)
     ↓
   onBackpressureBuffer(500)
     → buffers up to 500 items
     → if buffer full: OVERFLOW STRATEGY:
        - DROP: newest items dropped (data loss)
        - ERROR: Flux errors immediately
        - LATEST: keep only most recent item
        - BUFFER with overflow handler callback
     ↓
   Downstream pipeline at its own pace
```

---

### 💻 Code Example

**Example 1 — Automatic backpressure in cold Flux:**

```java
// Cold Flux: backpressure automatic — subscriber drives the pace
Flux<User> users = userRepository.findAll()
    // reactive repo returns Flux<User> with native backpressure
    .map(user -> enrichUser(user))        // sync transform
    .flatMap(user -> auditService         // async, max 5 concurrent
        .log(user), 5);                  // respects downstream demand

// WebFlux controller streams to HTTP client with backpressure
@GetMapping(value = "/users/stream",
    produces = MediaType.APPLICATION_NDJSON_VALUE)
public Flux<User> streamUsers() {
    return users; // framework subscribes and honors HTTP backpressure
}
```

**Example 2 — Explicit backpressure strategies for hot sources:**

```java
// Hot source: emits regardless of downstream demand
Flux<StockPrice> priceStream = marketDataService.getPriceStream();
// priceStream emits 10,000 prices/second

// Strategy 1: buffer up to 1000, error on overflow
Flux<StockPrice> withBuffer = priceStream
    .onBackpressureBuffer(1000,
        dropped -> log.warn("Dropped: {}", dropped),
        BufferOverflowStrategy.DROP_OLDEST);

// Strategy 2: drop excess, keep latest
Flux<StockPrice> withDrop = priceStream
    .onBackpressureLatest(); // only most recent if can't keep up

// Strategy 3: sample — take one value per interval
Flux<StockPrice> sampled = priceStream
    .sample(Duration.ofMillis(100)); // one price per 100ms max

// Strategy 4: limitRate — request in batches (default 256)
Flux<StockPrice> batched = priceStream
    .limitRate(64); // request 64 at a time, replenish at 75%
```

**Example 3 — Sinks for producer-side backpressure:**

```java
// Sinks: bridge between imperative producers and reactive consumers
// Bounded buffer: producer gets feedback when buffer full
Sinks.Many<Order> sink = Sinks.many()
    .multicast()
    .onBackpressureBuffer(1000);

// Producer side (e.g., from a legacy callback)
eventListener.onOrder(order -> {
    Sinks.EmitResult result = sink.tryEmitNext(order);
    if (result == Sinks.EmitResult.FAIL_ZERO_SUBSCRIBER) {
        log.warn("No subscribers — order buffered");
    } else if (result == Sinks.EmitResult.FAIL_OVERFLOW) {
        log.error("Buffer full — order dropped: {}", order.id());
        // Could also: retry, persist to queue, circuit break
    }
});

// Consumer side: gets backpressure automatically
Flux<Order> orderStream = sink.asFlux();
orderStream
    .flatMap(order -> processOrder(order), 10)
    .subscribe();
```

---

### ⚖️ Comparison Table

| Strategy                  | Memory            | Data Loss Risk        | Latency             | Use When                                   |
| ------------------------- | ----------------- | --------------------- | ------------------- | ------------------------------------------ |
| `onBackpressureBuffer(n)` | Bounded (n items) | On buffer overflow    | Adds queue latency  | Temporary bursts acceptable                |
| `onBackpressureDrop()`    | O(1)              | Yes — newest dropped  | Minimal             | Lossy data OK (metrics, telemetry)         |
| `onBackpressureError()`   | O(1)              | Error on overflow     | Minimal             | Strict: overflow = failure                 |
| `onBackpressureLatest()`  | O(1)              | Yes — old values lost | Minimal             | Only latest value matters (prices, status) |
| `limitRate(n)`            | O(n)              | None                  | Batch overhead      | Tuning request batch size                  |
| `sample(duration)`        | O(1)              | Yes — between samples | Add sample interval | High-freq telemetry, dashboards            |

---

### ⚠️ Common Misconceptions

| Misconception                                         | Reality                                                                                                                                        |
| ----------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| Backpressure prevents data loss                       | Backpressure bounds memory usage; data loss depends on the overflow strategy chosen — `DROP` loses data, `BUFFER` does not (until buffer full) |
| Backpressure works automatically for Kafka/WebSocket  | External sources are hot — they push regardless of demand; explicit `onBackpressure*` operators are required at the source boundary            |
| `Flux.collectList()` preserves backpressure           | `collectList()` requests all items from upstream before emitting — it defeats backpressure by loading everything into memory                   |
| `limitRate(n)` limits the publisher's emission rate   | `limitRate` optimizes the `request(n)` batch size; it does not cap the publisher's emission rate as a rate limiter would                       |
| Backpressure is only relevant for streaming endpoints | Any reactive pipeline with a mismatch between producer and consumer speeds needs backpressure consideration                                    |

---

### 🚨 Failure Modes & Diagnosis

**1. OutOfMemoryError from Unbounded Buffer**

**Symptom:** Application runs fine initially; under sustained load, heap grows unbounded; eventually `OutOfMemoryError`; heap dump shows large byte arrays or object arrays.

**Root Cause:** A Flux is buffered without a size limit — often `onBackpressureBuffer()` with no maxSize, or `collectList()`, or an unbounded `Sinks.many().replay()`.

**Diagnostic:**

```bash
# Heap dump analysis
jmap -dump:format=b,file=heap.hprof <pid>
# Analyze with Eclipse MAT or VisualVM
# Look for: large arrays in char[]/ byte[], Flux internal queues

# Monitor live heap via Actuator
curl http://localhost:8080/actuator/metrics/jvm.memory.used

# Enable GC logging to watch growth
-XX:+PrintGCDetails -XX:+PrintGCDateStamps
```

**Fix:**

```java
// BAD: unbounded buffer
hotSource.onBackpressureBuffer(); // no limit!

// GOOD: bounded with explicit overflow handling
hotSource.onBackpressureBuffer(
    10_000,                    // max 10k items
    item -> log.warn("Dropped: {}", item),
    BufferOverflowStrategy.DROP_OLDEST);
```

---

**2. Subscriber Too Slow — Cascading Backpressure**

**Symptom:** Response times increase across the pipeline; upstream services slow down; throughput drops uniformly; metrics show `request(1)` patterns (no batching).

**Root Cause:** `limitRate` not configured; each subscriber requests one item at a time — high overhead from frequent demand requests; or a slow `flatMap` inner publisher holds up the entire pipeline.

**Diagnostic:**

```java
// Add .log() to see request(n) patterns
myFlux.log("pipeline") // prints: request(1), request(1), request(1)...
// Should see: request(256) for efficient batching
```

**Fix:**

```java
// GOOD: configure prefetch for efficient batching
myFlux
    .limitRate(256)    // request 256 at a time
    .flatMap(item -> process(item), 10); // max 10 concurrent
```

---

**3. Backpressure Lost at ThreadScheduler Boundary**

**Symptom:** Memory grows despite `onBackpressureBuffer`; the buffer seems to be growing unbounded.

**Root Cause:** `publishOn()` or `subscribeOn()` adds an asynchronous boundary with its own internal queue. If the queue is unbounded and the downstream is slower than the scheduler queue, items pile up in the scheduler's queue, not the `onBackpressureBuffer`.

**Diagnostic:**

```java
// publishOn uses an internal queue with default prefetch 256
// If producer is much faster, items fill publishOn's queue
flux.publishOn(Schedulers.boundedElastic()) // has internal queue
    .onBackpressureBuffer(100); // this buffer may never fill
    // items are in publishOn's queue instead
```

**Fix:**

```java
// Set publishOn's prefetch to control its internal queue size
flux.publishOn(Schedulers.boundedElastic(), 64) // prefetch=64
    .onBackpressureBuffer(100);
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Reactive Streams` — backpressure is defined by the Reactive Streams `Subscription.request(n)` protocol
- `Mono / Flux` — the Reactor types that implement backpressure
- `WebFlux / Reactive` — the Spring context in which backpressure operates

**Builds On This (learn these next):**

- `Rate Limiting` — related concept at the HTTP/API layer; backpressure is internal flow control, rate limiting is external
- `Circuit Breaker` — handles failure at overloaded downstream; complementary to backpressure
- `Kafka / Messaging` — at Kafka source boundaries, backpressure requires explicit acknowledgment control (max.poll.records, consumer pause)

**Alternatives / Comparisons:**

- `Bounded Queues (BlockingQueue)` — the synchronous analogue of backpressure; `LinkedBlockingQueue(maxSize)` blocks the producer when full
- `Rate Limiter (Resilience4j)` — limits requests per time unit; operates at API level, not stream operator level
- `TCP Flow Control` — the network-level analogue; TCP's receive window controls data transmission rate between endpoints

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Slow consumer signals fast producer to    │
│              │ slow down via request(n) protocol         │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Fast producer + slow consumer =           │
│ SOLVES       │ unbounded buffer growth → OOM             │
├──────────────┼───────────────────────────────────────────┤
│ AUTO IN      │ Cold Flux pipelines in same JVM — works   │
│              │ automatically via request(n)              │
├──────────────┼───────────────────────────────────────────┤
│ NEEDED FOR   │ Hot sources (Kafka, WebSocket, intervals) │
│              │ — use onBackpressure*() operators         │
├──────────────┼───────────────────────────────────────────┤
│ STRATEGIES   │ BUFFER (bounded), DROP (lose items),      │
│              │ LATEST (keep newest), ERROR (fail fast)   │
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ collectList() — loads all into memory,    │
│              │ defeats backpressure entirely             │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "request(n) lets the consumer set the     │
│              │  producer's speed — bounded by design"    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Rate Limiting → Circuit Breaker →         │
│              │ Kafka reactive integration                │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE B — Scale) A WebFlux service receives a `Flux<byte[]>` from a file upload endpoint. The client uploads at 100MB/s. The service writes each chunk to S3 via a reactive S3 client that accepts 1 chunk at a time with 50ms latency. Calculate the maximum upload throughput this pipeline can sustain. What specific backpressure configuration ensures stable memory usage regardless of upload speed, and what happens to the client's upload experience when the S3 write rate falls below the upload rate?

**Q2.** (TYPE E — Architecture) A team proposes handling a Kafka topic with 50,000 events/second using Spring WebFlux with `onBackpressureBuffer(100)`. Another team says "Kafka already has its own flow control via `max.poll.records` and consumer pause — you don't need Reactor backpressure." Both teams are partially correct. Describe exactly what each mechanism controls, where they operate in the stack, and why a production system needs both.
