
---
layout: default
title: "Backpressure"
parent: "Spring & Spring Boot"
nav_order: 138
permalink: /spring/backpressure/
number: "138"
category: Spring & Spring Boot
difficulty: ★★★
depends_on: "Mono / Flux, WebFlux, Reactive Streams, Non-blocking I/O"
used_by: "Flux operators, R2DBC, WebClient streaming, Messaging consumers"
tags: #java, #spring, #advanced, #deep-dive, #performance, #reliability
---

# 138 — Backpressure

`#java` `#spring` `#advanced` `#deep-dive` `#performance` `#reliability`

⚡ TL;DR — The mechanism by which a reactive subscriber controls how fast a publisher produces items — preventing a fast producer from overwhelming a slow consumer with unbounded data.

| #138 | Category: Spring & Spring Boot | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Mono / Flux, WebFlux, Reactive Streams, Non-blocking I/O | |
| **Used by:** | Flux operators, R2DBC, WebClient streaming, Messaging consumers | |

---

### 📘 Textbook Definition

**Backpressure** is the ability of a downstream `Subscriber` in a reactive pipeline to signal to an upstream `Publisher` how many items it can handle at a time, via `Subscription.request(n)`. This prevents unbounded data production that would exhaust memory or overwhelm a slow consumer. The Reactive Streams specification mandates backpressure as a first-class protocol: the publisher MUST NOT emit more items than were requested. Project Reactor implements several backpressure strategies: `onBackpressureBuffer` (queue overflow), `onBackpressureDrop` (discard overflow), `onBackpressureLatest` (keep latest), and `onBackpressureError` (signal error on overflow). When backpressure cannot propagate end-to-end (e.g. WebSocket, user input), explicit overflow strategies must be applied.

---

### 🟢 Simple Definition (Easy)

Backpressure is a consumer telling a producer "slow down, I can only handle 10 items at a time." Without it, a fast producer floods a slow consumer, filling memory until the application crashes.

---

### 🔵 Simple Definition (Elaborated)

In a reactive pipeline, the source might produce data much faster than at the downstream end can process it. A database streaming 100,000 rows per second feeding into a service that can only process 1,000 per second — without backpressure, the remaining 99,000 rows per second must go somewhere: memory queue fills up, then heap overflows, then OutOfMemoryError. Backpressure inverts control: the consumer says "give me 100" (`Subscription.request(100)`), processes them, then says "give me 100 more." The producer pauses between batches. This pull model keeps memory usage bounded regardless of how fast the source can produce.

---

### 🔩 First Principles Explanation

**The producer-consumer speed mismatch:**

```
Without backpressure:
  Producer: emits 100,000 events/second
  Consumer: processes 1,000 events/second
  Buffer fills at 99,000 events/second
  1 second: 99,000 events in queue (~9.9 MB)
  10 seconds: 990,000 events → ~99 MB
  30 seconds: OOM → JVM crash

  Non-reactive solution: block the producer thread
  → defeats non-blocking purpose of reactive

Reactive Streams backpressure protocol:
  Consumer: subscription.request(100)  ← PULL
  Producer: emits exactly 100 items
  Consumer: processes 100
  Consumer: subscription.request(100)  ← PULL again
  Loop: producer never runs ahead of consumer
  Memory: only 100-item buffer needed
```

**The four backpressure strategies:**

```
┌─────────────────────────────────────────────────────┐
│  BACKPRESSURE STRATEGY           USE CASE           │
├─────────────────────────────────────────────────────┤
│  onBackpressureBuffer(size)      Audit log: queue   │
│  → buffer up to N items          events temporarily │
│  → overflow: error               before writing     │
│                                                     │
│  onBackpressureDrop()            Live telemetry:    │
│  → discard items when slow       drop old readings  │
│  → consumer never overwhelmed     accept data loss  │
│                                                     │
│  onBackpressureLatest()          Stock prices:      │
│  → keep only most recent item    only latest quote  │
│  → intermediate items discarded  matters anyway     │
│                                                     │
│  onBackpressureError()           Alerts: must not   │
│  → emit error when overwhelmed   lose any alert     │
│  → fail fast rather than lose    → explicit failure │
└─────────────────────────────────────────────────────┘
```

---

### ❓ Why Does This Exist (Why Before What)

**WITHOUT backpressure in a reactive system:**

```
File export endpoint: read 1M records from DB
  Flux<Row> allRows = r2dbcRepo.findAll(); // no limit
  allRows.map(toDto).subscribe(sendToClient);
  // DB streams 50,000 rows/sec
  // Client TCP buffer fills → writes buffer fills
  // Reactor buffers rows in-memory
  // 1M rows × 500 bytes = 500MB heap
  // OutOfMemoryError mid-export

Kafka consumer → WebClient call for each message:
  flux.flatMap(msg -> httpClient.send(msg))
  // flatMap: default concurrency = 256!
  // 256 simultaneous HTTP calls created immediately
  // Downstream service: 429 Too Many Requests
  // OR: 256 pending futures in memory per burst
```

**WITH backpressure:**

```
→ r2dbcRepo.findAll() honours request(n):
  reads N rows from DB, pauses until request(n) again
  → constant O(n) memory regardless of dataset size

→ flatMap(concurrency=10) limits in-flight requests:
  max 10 simultaneous HTTP calls at any time
  → downstream service not overwhelmed
  → bounded memory usage

→ onBackpressureDrop for live data:
  drop sensor readings when processing slow
  → never OOM, accept graceful data loss
```

---

### 🧠 Mental Model / Analogy

> Backpressure is like a **supermarket self-checkout conveyor belt with a sensor**. The scanning area (consumer) is a fixed size. The conveyor belt (publisher) advances only when the scanning area has space. If you pile items faster than you scan them, the belt stops (backpressure applied). Without the sensor: every item piled onto the belt falls off the end onto the floor (dropped without backpressure), or they queue up behind the register (buffer backpressure), or the system jams (error backpressure).

"Conveyor belt" = reactive Flux (publisher)
"Piling items" = fast data emission
"Scanning area" = consumer processing capacity
"Belt sensing space and stopping" = backpressure signal (request(n))
"Items falling off end" = onBackpressureDrop
"Queue behind register" = onBackpressureBuffer
"System jam" = onBackpressureError

---

### ⚙️ How It Works (Mechanism)

**Reactive Streams protocol deep-dive:**

```java
// The full Reactive Streams interface:
interface Publisher<T> {
  void subscribe(Subscriber<? super T> s);
}
interface Subscriber<T> {
  void onSubscribe(Subscription s); // called once
  void onNext(T item);              // called for each item
  void onError(Throwable t);        // terminal
  void onComplete();                // terminal
}
interface Subscription {
  void request(long n);  // ← BACKPRESSURE: request n items
  void cancel();         // cancel the subscription
}

// How it flows:
// 1. publisher.subscribe(subscriber)
// 2. subscriber.onSubscribe(subscription) called
// 3. subscriber.request(10) ← pull 10 items
// 4. publisher emits ≤10 via subscriber.onNext() × n
// 5. subscriber.request(10) ← pull 10 more
// Repeat until onComplete or onError
```

**Backpressure in Project Reactor:**

```java
Flux<Integer> numbers = Flux.range(1, 1_000_000);

// Strategy 1: Buffer (queue) — bounded safe
numbers
    .onBackpressureBuffer(1000,          // max 1000 buffered
        dropped -> log.warn("Dropped: {}", dropped),
        BufferOverflowStrategy.DROP_OLDEST)
    .subscribe(n -> processSlow(n));     // slow consumer

// Strategy 2: Drop — for lossy-acceptable streams
numbers
    .onBackpressureDrop(n -> dropped.incrementAndGet())
    .subscribe(n -> processSlow(n));

// Strategy 3: Control concurrency with flatMap
Flux.fromIterable(kafka.poll())
    .flatMap(
        msg -> processAsync(msg),
        5,   // max 5 concurrent inner subscriptions
        1    // prefetch 1 at a time
    )
    .subscribe();
```

**Where backpressure breaks — hot sources:**

```
HOT sources cannot honour backpressure:
  User GUI events (can't tell mouse to slow down)
  Real-time sensor data (sensor doesn't wait)
  WebSocket messages (server doesn't wait for you)
  Network packets (network doesn't wait)

Resolution: explicit buffering/dropping strategy
  Flux.create(sink -> {
    sink.onRequest(n -> {    // called when subscriber requests
      // honour n: produce exactly n items
    });
  }, FluxSink.OverflowStrategy.BUFFER);
```

---

### 🔄 How It Connects (Mini-Map)

```
Fast publisher (DB, network, sensor)
        ↓
  BACKPRESSURE (138)  ← you are here
  Subscription.request(n) — consumer controls rate
        ↓
  Strategies:
  Buffer: queue up to N (safe for important data)
  Drop: discard overflow (safe for lossy data)
  Latest: keep newest (safe for real-time data)
  Error: fail fast (safe for critical alerting)
        ↓
  Implemented in: Mono/Flux (137) operators
  Used in: WebFlux streaming endpoints
           R2DBC bulk data reads
           Kafka reactive consumer
        ↓
  Prevents: OOM, 429 cascades, network congestion
```

---

### 💻 Code Example

**Example 1 — Streaming large DB export with backpressure:**

```java
// R2DBC honours backpressure — reads rows on demand
@GetMapping(value = "/reports/export",
            produces = MediaType.APPLICATION_NDJSON_VALUE)
public Flux<ReportRow> exportData() {
  return r2dbcRepo.streamAllByStatus("COMPLETED")
      // Process 50 at a time → constant O(50) in-memory
      .buffer(50)
      .flatMapSequential(
          batch -> Flux.fromIterable(batch)
                       .map(reportMapper::toDto),
          1  // one batch at a time (sequential)
      )
      .limitRate(100);  // subscriber request 100 at a time
  // HTTP client receives NDJSON rows as they stream
  // Server never holds more than 100 rows in memory
}
```

**Example 2 — Backpressure for Kafka reactive consumer:**

```java
// Reactive Kafka consumer with explicit prefetch
@Component
class ReactiveKafkaProcessor {
  private final ReactiveKafkaConsumerTemplate<String, Event>
      kafkaTemplate;
  private final EventProcessor processor;

  @PostConstruct
  void startConsuming() {
    kafkaTemplate.receiveAutoAck()
        .flatMap(
            record -> processor.process(record.value()),
            10,  // max 10 concurrent processing
            1    // prefetch: request 1 at a time from Kafka
        )
        .onBackpressureBuffer(100,
            record -> log.warn("Backpressure drop: {}",
                record.key()))
        .subscribe();
  }
}
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Backpressure automatically prevents all memory issues | Backpressure works end-to-end only if ALL operators in the chain honour it. Hot sources require explicit overflow strategies — backpressure cannot be applied retroactively |
| onBackpressureBuffer is always safe | onBackpressureBuffer without a size limit creates an unbounded in-memory buffer — exactly the OOM scenario backpressure is meant to prevent. Always specify a maximum size |
| flatMap respects backpressure from downstream | flatMap's default concurrency (256) aggressively requests items ignoring downstream pressure. Set explicit concurrency: `flatMap(fn, concurrency, prefetch)` |
| Backpressure is only for streaming/messaging | Any Flux that can produce more items than downstream can process needs backpressure. This includes DB queries, file reads, HTTP response bodies |

---

### 🔥 Pitfalls in Production

**1. Unbounded flatMap causing cascade failure**

```java
// BAD: default flatMap concurrency = 256
// Processing 10,000 Kafka messages in burst:
// → 256 simultaneous HTTP calls created immediately
// → downstream service: 256 TCP connections opened
// → 429 responses flood back → retry storms
flux.flatMap(msg -> httpClient.call(msg)); // DANGEROUS

// GOOD: bounded concurrency
flux.flatMap(
    msg -> httpClient.call(msg)
                     .retryWhen(Retry.backoff(3, Duration.ofMillis(100))),
    10,  // max 10 concurrent
    1    // prefetch 1 (request 1 from Kafka at a time)
);
```

**2. Missing overflow strategy on hot source**

```java
// BAD: hot source with no overflow strategy
// WebSocket messages arrive at 10,000/sec
// Consumer at 100/sec → unbounded buffer growth
Flux<Message> wsMessages = webSocketSession.receive();
wsMessages
    .map(WebSocketMessage::getPayloadAsText)
    .flatMap(this::processSlowly)  // no overflow handling
    .subscribe();
// After 10s: 99,000 × message_size bytes in memory
// After 60s: OutOfMemoryError

// GOOD: explicit strategy matching business requirements
wsMessages
    .onBackpressureDrop(msg ->   // drop old messages
        log.debug("Dropped: {}", msg))
    .map(WebSocketMessage::getPayloadAsText)
    .flatMap(this::processSlowly, 5) // bounded concurrency
    .subscribe();
```

---

### 🔗 Related Keywords

- `Mono / Flux` — the reactive types on which backpressure is applied
- `Reactive Streams` — the specification mandating `request(n)` backpressure protocol
- `WebFlux` — the framework within which backpressure applies to HTTP streaming
- `R2DBC` — reactive database driver that honours backpressure on large queries
- `Project Reactor` — provides `onBackpressureBuffer/Drop/Latest/Error` operators
- `Kafka Reactive` — reactive Kafka consumer where prefetch controls Kafka polling rate

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Consumer controls producer speed via      │
│              │ request(n) — prevents OOM from fast       │
│              │ producer overwhelming slow consumer       │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Buffer: audit/critical; Drop: telemetry;  │
│              │ Latest: real-time prices; Error: alerts   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ onBackpressureBuffer without size limit;  │
│              │ flatMap without concurrency limit         │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The checkout scanner signals the belt —  │
│              │  only advance when there's room to scan." │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Project Reactor internals →               │
│              │ R2DBC → Reactive Kafka → Reactor Debugging│
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Project Reactor's `Flux.flatMap()` with a concurrency argument internally manages a pool of `InnerSubscriber`s. When the `flatMap` requests items from the outer Flux, it uses a `prefetch` parameter (default 32) which pre-fetches from the outer Flux even if only 1 inner subscription slot is free. Explain why this prefetch exists (hint: pipeline efficiency), what happens to the prefetched items if the outer Flux terminates before the inner subscriptions consume them, and how to calculate the peak in-memory backlog size for a `flatMap(fn, concurrency=10, prefetch=32)` where each inner `Mono` takes 500ms to complete and the outer Flux emits 1,000 items per second.

**Q2.** Backpressure works within a single JVM reactive pipeline. When data crosses a network boundary (e.g. from a WebFlux server to a JavaScript browser client consuming Server-Sent Events), there is no Reactive Streams `request(n)` mechanism across the HTTP connection. Describe how WebFlux handles backpressure between the Flux on the server and the actual TCP write buffer — specifically what happens when the client's TCP receive buffer is full, how Netty signals this to the Reactor pipeline, and what `WriteTimeoutHandler` or `responseTimeout` configuration controls this at the WebClient level for reverse scenarios.

