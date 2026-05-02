---
layout: default
title: "Backpressure Pattern"
parent: "Design Patterns"
nav_order: 814
permalink: /design-patterns/backpressure-pattern/
number: "814"
category: Design Patterns
difficulty: ★★★
depends_on: "Throttling Pattern, Bulkhead Pattern, Reactive Programming, Event-Driven Pattern"
used_by: "Reactive systems, streaming pipelines, message queues, flow control"
tags: #advanced, #design-patterns, #reactive, #streaming, #flow-control, #resilience
---

# 814 — Backpressure Pattern

`#advanced` `#design-patterns` `#reactive` `#streaming` `#flow-control` `#resilience`

⚡ TL;DR — **Backpressure** is a flow control mechanism where a consumer signals to the producer how much data it can handle — preventing the consumer from being overwhelmed by a faster producer, ensuring stable throughput without memory exhaustion or data loss.

| #814            | Category: Design Patterns                                                        | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Throttling Pattern, Bulkhead Pattern, Reactive Programming, Event-Driven Pattern |                 |
| **Used by:**    | Reactive systems, streaming pipelines, message queues, flow control              |                 |

---

### 📘 Textbook Definition

**Backpressure** (hydraulic engineering term applied to distributed systems; formalized in Reactive Streams specification, 2014; implemented in Project Reactor, RxJava, Akka Streams): a feedback mechanism in a data processing pipeline where a downstream consumer signals upstream producers how much data it can process. Without backpressure: a fast producer overwhelms a slow consumer, causing buffer overflow, memory exhaustion, or data loss. With backpressure: the consumer requests (`request(N)` in Reactive Streams API) exactly as many items as it can process; the producer sends no more. The Reactive Streams specification (Java 9 Flow API, Project Reactor, RxJava 2+) standardizes backpressure as a core contract.

---

### 🟢 Simple Definition (Easy)

Water filling a bottle: if you pour too fast, the bottle overflows. Backpressure: the bottle signals "I can only accept 1 cup per second." The pourer slows down to match. No overflow. In software: a message processor signals "I can handle 100 messages per second." The publisher sends no more than 100/second. No queue overflow, no memory exhaustion. Backpressure: the consumer controls the flow rate, not the producer.

---

### 🔵 Simple Definition (Elaborated)

A streaming ETL pipeline: data source produces 10,000 records/second; each record requires a database write taking 5ms; database can handle 200 writes/second. Without backpressure: 10,000 records/second accumulate in memory → JVM heap fills → OutOfMemoryError → pipeline crash → data loss. With backpressure: database write stage signals "I can accept 200 records/second." The buffer between stages grows to a configured limit and then the upstream is signaled to pause. Producer pauses until the consumer catches up. Memory: stable. Throughput: 200 records/second (the actual bottleneck). No data loss.

---

### 🔩 First Principles Explanation

**Reactive Streams backpressure protocol and Project Reactor implementation:**

```
REACTIVE STREAMS SPECIFICATION (Backpressure Contract):

  4 interfaces (Java 9 java.util.concurrent.Flow):

  Publisher<T>:     void subscribe(Subscriber<? super T> s)
  Subscriber<T>:    void onSubscribe(Subscription s)
                    void onNext(T item)
                    void onError(Throwable t)
                    void onComplete()
  Subscription:     void request(long n)     ← BACKPRESSURE SIGNAL
                    void cancel()
  Processor<T,R>:   implements Publisher<R> + Subscriber<T>

  PROTOCOL:
  1. Subscriber.onSubscribe(subscription) called by Publisher
  2. Subscriber calls subscription.request(N) — "send me N items"
  3. Publisher sends at most N items via onNext()
  4. Subscriber processes N items, calls request(N) again when ready
  5. cycle continues until onComplete() or onError()

  KEY: Publisher MUST NOT send more items than requested.

PROJECT REACTOR BACKPRESSURE:

  Flux (0..N items): supports backpressure by default.

  BACKPRESSURE STRATEGIES (when downstream can't keep up):

  1. BUFFER (default): buffer all items — risk of OOM on sustained overload
     Flux.just(items).onBackpressureBuffer(1000)  // buffer up to 1000

  2. DROP: drop new items when buffer full — data loss but no OOM
     Flux.just(items).onBackpressureBuffer(1000, item -> log.warn("Dropped: {}", item))
     // Or:
     source.onBackpressureDrop()

  3. LATEST: keep only the most recent item in buffer — appropriate for UI updates
     source.onBackpressureLatest()   // old unprocessed items replaced by newer

  4. ERROR: fail immediately when consumer can't keep up
     source.onBackpressureError()    // throws OverflowException

  5. REQUEST CONTROL (pull-based): subscriber explicitly controls rate
     // Spring WebFlux example:
     source
         .publishOn(Schedulers.boundedElastic())
         .flatMap(item -> processItem(item), 10)   // max 10 concurrent
         // flatMap concurrency = backpressure control

QUEUE-BASED BACKPRESSURE (Kafka):

  Kafka consumer: explicitly controls fetch rate.
  consumer.poll(Duration.ofMillis(100)):
    - Polls Kafka for records
    - Returns records batch of up to max.poll.records (default: 500)
    - Consumer processes batch, then polls again

  If consumer processes < 500 records in max.poll.interval.ms:
  → Consumer group rebalance (consumer too slow)

  Backpressure tuning:
  max.poll.records=100     // reduce if processing is slow
  max.poll.interval.ms=300000  // 5 minutes: time to process a batch

  The consumer PULLS messages (backpressure built-in to Kafka's pull model).
  Unlike HTTP push: consumer controls exactly how many records to fetch.

BACKPRESSURE IN SPRING WEBFLUX:

  @RestController
  class StreamController {
      @GetMapping(value = "/events", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
      Flux<ServerSentEvent<OrderEvent>> streamEvents() {
          return orderEventSource.getFlux()
              // Backpressure: limit to 50 events concurrently processed per subscriber:
              .onBackpressureBuffer(1000, dropped -> log.warn("Dropped event: {}", dropped))
              .flatMap(event -> enrichEvent(event), 50);  // max 50 concurrent enrichments
      }
  }
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Backpressure:

- Fast producer overwhelms slow consumer → queue/buffer fills → OOM → crash or data loss
- System performance degrades unpredictably under load

WITH Backpressure:
→ Consumer controls the flow rate. Memory usage bounded. System stable under sustained overload. Throughput matches the slowest stage's capacity. No data loss (or explicit, controlled drop strategy).

---

### 🧠 Mental Model / Analogy

> A factory assembly line: machines at each stage pass parts to the next. If the painting station (stage 3) is slower than the welding station (stage 2): parts accumulate between stages. Without backpressure: parts pile up on the floor → fire hazard → factory shuts down (OutOfMemoryError). With backpressure: painting station signals "I can only accept 10 parts per minute." Welding station slows to 10 parts/minute. Buffer between stages: bounded. Factory: stable. Output: 10 parts/minute (limited by the actual bottleneck — painting).

"Welding station (fast) sending parts to painting station (slow)" = fast producer, slow consumer
- "Parts piling up on the floor" = unbounded buffer overflow → OOM
"Painting station signals 10 parts/minute" = `subscription.request(10)` in Reactive Streams
"Welding station slows to match" = publisher sends no more than requested
"Factory: stable, output: 10 parts/min" = stable memory, throughput = bottleneck capacity

---

### ⚙️ How It Works (Mechanism)

```
BACKPRESSURE STRATEGIES COMPARISON:

  Strategy     │ Memory   │ Data Loss │ Use Case
  ─────────────┼──────────┼───────────┼──────────────────────────────
  Buffer       │ Risk OOM │ None      │ Transient spikes, bounded burst
  Drop         │ Bounded  │ Yes       │ Real-time streaming where latest > complete
  Latest       │ Bounded  │ Yes       │ UI updates (only latest state matters)
  Error        │ Bounded  │ Exception │ Strict: no tolerance for overload
  Request ctrl │ Bounded  │ None      │ Database writes, external API calls

  RULE: use Request Control (pull-based) for data-critical pipelines.
  Use Drop/Latest for real-time non-critical streams (metrics, dashboard).
  Never use unbounded Buffer for sustained high-throughput pipelines.
```

---

### 🔄 How It Connects (Mini-Map)

```
Fast producer + slow consumer → buffer overflow → OOM or data loss
        │
        ▼
Backpressure Pattern ◄──── (you are here)
(consumer signals demand; producer respects it; memory bounded; throughput stable)
        │
        ├── Throttling Pattern: Throttling = rate limit at entry; Backpressure = flow control between stages
        ├── Reactive Programming: Backpressure is a core feature of reactive streams
        ├── Kafka: pull-based consumer model = built-in backpressure
        └── Bulkhead Pattern: concurrency limit = a form of backpressure per dependency
```

---

### 💻 Code Example

```java
// Spring WebFlux reactive pipeline with backpressure — database write stage:

@Service @RequiredArgsConstructor
public class OrderIngestionService {

    private final OrderRepository repository;    // blocking R2DBC (reactive)

    // Reactive pipeline with explicit backpressure control:
    public Flux<OrderResult> processOrderStream(Flux<OrderEvent> eventStream) {
        return eventStream
            // Backpressure strategy: buffer up to 10,000 events
            // If buffer full: drop oldest (FIFO eviction with warning)
            .onBackpressureBuffer(10_000,
                dropped -> log.warn("Backpressure: dropped order event {}", dropped.getOrderId()),
                BufferOverflowStrategy.DROP_OLDEST)

            // Process on bounded elastic thread pool (I/O operations):
            .publishOn(Schedulers.boundedElastic())

            // flatMap concurrency = MAX 20 concurrent DB writes:
            // This IS the backpressure: only 20 events in-flight at any time
            .flatMap(event -> processEvent(event), 20)

            // Handle processing errors without terminating the stream:
            .onErrorContinue((error, event) ->
                log.error("Failed to process event {}: {}", event, error.getMessage()));
    }

    private Mono<OrderResult> processEvent(OrderEvent event) {
        return Mono.fromSupplier(() -> validateEvent(event))
            .flatMap(valid -> repository.save(valid.toOrder()))
            .map(saved -> OrderResult.success(saved.getId()))
            .onErrorReturn(OrderResult.failed(event.getOrderId()));
    }
}

// Demonstrating request(N) backpressure explicitly:
@Test
void backpressurePullExample() {
    Flux<Integer> source = Flux.range(1, 100)
        .doOnRequest(n -> log.info("Downstream requested {} items", n));

    // BaseSubscriber: explicitly control demand:
    source.subscribe(new BaseSubscriber<Integer>() {
        @Override
        protected void hookOnSubscribe(Subscription subscription) {
            request(10);    // Request first 10 items
        }

        @Override
        protected void hookOnNext(Integer value) {
            log.info("Processing: {}", value);
            if (value % 10 == 0) {
                request(10);    // Request next 10 after processing current batch
            }
        }
    });
}
// Output:
// "Downstream requested 10 items" → 1,2,3...10 processed
// "Downstream requested 10 items" → 11,12...20 processed
// etc.
// Publisher never sends more than 10 items without explicit request.
```

---

### ⚠️ Common Misconceptions

| Misconception                                 | Reality                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| --------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Backpressure is only for reactive programming | Backpressure exists in many non-reactive forms: Kafka's pull-based consumption (consumer controls fetch rate), TCP's flow control window (receiver signals buffer space to sender), Unix pipe buffering (process blocks when pipe buffer full). The Reactive Streams specification formalized backpressure as an explicit API, but the concept predates reactive programming by decades.                                                                               |
| Backpressure prevents data loss               | Backpressure prevents buffer overflow and OOM. Whether it prevents data loss depends on the chosen strategy. `onBackpressureDrop()`: data loss is explicit and intentional. `onBackpressureBuffer()` with bounded buffer: data loss when buffer is full. `request(N)` pull-based: no data loss (publisher waits), but increased end-to-end latency. Data loss vs. latency is a tradeoff: choose explicitly based on requirements.                                      |
| flatMap concurrency parameter is backpressure | `flatMap(f, concurrency)` limits the maximum number of in-flight inner publishers — this IS a form of backpressure (bounded concurrency). But it's applied at the flatMap stage, not at the subscription level. The source Flux may still emit more items than `concurrency` allows processing; the items queue internally in flatMap's internal buffer. For complete backpressure: combine `flatMap(concurrency)` with `onBackpressureBuffer(bounded)` on the source. |

---

### 🔥 Pitfalls in Production

**Reactive pipeline with unbounded buffer causing OOM under sustained overload:**

```java
// ANTI-PATTERN — Flux without backpressure strategy in a streaming ingestion service:

@Service
public class EventIngestionService {

    public Flux<ProcessingResult> ingest(Flux<RawEvent> eventStream) {
        return eventStream
            // NO backpressure strategy — default behavior:
            // Flux will buffer ALL unemitted items in memory if downstream is slow
            .flatMap(event -> slowDatabaseWrite(event))  // 50ms per write
            .map(ProcessingResult::success);
    }

    private Mono<DbResult> slowDatabaseWrite(RawEvent event) {
        return reactiveRepository.save(event.toEntity());
    }
}

// Source: Kafka topic producing 10,000 events/sec
// Database write: 50ms each → max throughput 20 events/sec
// Gap: 10,000 produced - 20 processed = 9,980 events/sec accumulating in memory
// After 10 seconds: ~100,000 buffered events × ~1KB each = 100MB heap
// After 100 seconds: ~1GB heap → OOM → pod crash → events LOST

// FIX — explicit backpressure strategy:
public Flux<ProcessingResult> ingest(Flux<RawEvent> eventStream) {
    return eventStream
        // Explicit bounded buffer: max 1,000 events in memory
        .onBackpressureBuffer(1_000,
            dropped -> log.warn("Ingestion buffer full — dropping event: {}", dropped.getId()),
            BufferOverflowStrategy.DROP_OLDEST)

        // Control concurrent DB writes (backpressure via concurrency):
        .flatMap(event -> slowDatabaseWrite(event), 20)   // max 20 concurrent writes
        .map(ProcessingResult::success);
}
// Memory: bounded (max ~1,000 events buffered = ~1MB)
// Under sustained overload: events dropped with warning (visible in logs/metrics)
// Throughput: stable at max 20 × (1000ms/50ms) = 400 events/second
// OOM: prevented. Pod: stable. Trade-off: explicit, monitored data loss.
```

---

### 🔗 Related Keywords

- `Throttling Pattern` — related: Throttling = entry rate limit; Backpressure = internal flow control between stages
- `Reactive Programming` — Backpressure is a first-class citizen of Reactive Streams / Project Reactor
- `Kafka` — pull-based consumer model provides built-in backpressure
- `Bulkhead Pattern` — concurrency limits are a form of backpressure per downstream
- `Event-Driven Pattern` — backpressure is critical for reliable event processing at scale

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Consumer signals demand to producer.     │
│              │ Producer sends no more than requested.  │
│              │ Memory bounded. No OOM from fast source. │
├──────────────┼───────────────────────────────────────────┤
│ STRATEGIES   │ Buffer (bounded!); Drop; Latest;         │
│              │ Error; Request control (pull-based)      │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Fast producer + slow consumer;           │
│              │ streaming pipelines; reactive systems;  │
│              │ any unbounded input source              │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Assembly line: painting station signals │
│              │  '10 parts/min.' Welding slows down.   │
│              │  No parts pile up on the floor."        │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Reactive Streams → Project Reactor →     │
│              │ Kafka Consumer Config → Throttling →     │
│              │ Bulkhead                                  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** TCP implements backpressure via the flow control window: the receiver advertises its available buffer space in the TCP ACK header (`rwnd` — receiver window size). The sender must not send more bytes than the receiver's window allows. This is the same principle as Reactive Streams `request(N)`. TCP also has congestion control (`cwnd` — congestion window), which reduces the send rate when packet loss is detected. How do TCP's flow control window and congestion control together form a two-layered backpressure system? How does this compare to Reactive Streams' `request(N)` mechanism?

**Q2.** Project Reactor's `flatMap` operator has a `concurrency` parameter: `flatMap(f, 16)` means at most 16 inner publishers in flight simultaneously. But each inner publisher may itself produce multiple items. Under sustained load, `flatMap(concurrency=16)` does NOT provide true backpressure to the source — the source can still emit items faster than they're processed, and those items queue in `flatMap`'s internal buffer. `concatMap` provides serial, backpressure-aware processing. How does `concatMap` differ from `flatMap` in terms of backpressure semantics and throughput? When does `flatMap(concurrency)` provide "good enough" backpressure, and when must you use pull-based `request(N)`?
