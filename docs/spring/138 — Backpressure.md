---
layout: default
title: "Backpressure"
parent: "Spring Framework"
nav_order: 138
permalink: /spring/backpressure/
---
# 138 — Backpressure

`#spring` `#distributed` `#performance` `#reliability` `#advanced`

⚡ TL;DR — Backpressure is the mechanism in reactive streams where a slow consumer signals the producer to slow down or buffer — preventing overwhelm when data arrives faster than it can be processed.

| #138 | Category: Spring & Spring Boot | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Reactive Streams, Mono Flux | |
| **Used by:** | Reactive pipelines, WebFlux, flow control | |

---

### 📘 Textbook Definition

Backpressure is a flow control mechanism defined in the Reactive Streams specification. A subscriber communicates to the publisher how many items it can currently handle via `Subscription.request(n)`. The publisher emits at most `n` items, preventing the subscriber from being overwhelmed. Project Reactor's `Flux` and `Mono` implement the full Reactive Streams protocol including backpressure.

### 🟢 Simple Definition (Easy)

Imagine a water hose filling a bucket. If the hose is too fast, the bucket overflows (OutOfMemoryError). Backpressure is the bucket saying "I'm almost full, slow down!" to the hose. In reactive systems, the consumer tells the producer how many items to send at a time.

### 🔵 Simple Definition (Elaborated)

In a reactive pipeline, a fast producer can emit faster than a slow consumer can process. Without backpressure, this means unbounded buffering (memory explosion) or dropped messages. Reactive Streams' backpressure protocol lets the subscriber pull items at its own pace. Operators like `onBackpressureBuffer()`, `onBackpressureDrop()`, and `limitRate()` let you choose the backpressure strategy.

### 🔩 First Principles Explanation

**Reactive Streams protocol:**
```
Publisher → (on subscribe) → Subscriber
Subscriber → request(10) → Publisher
Publisher → emit 10 items → Subscriber
Subscriber → processes 10 → request(10) more
Publisher → emit 10 more ...
```
Producer never emits more than requested — **pull model** not push model.

### 💻 Code Example
```java
// ── Demonstrating backpressure strategies ─────────────────────────────────────
Flux<Integer> fastProducer = Flux.range(1, 1_000_000)
    .publishOn(Schedulers.parallel());
// Strategy 1: Buffer — queue items when consumer is slow
fastProducer
    .onBackpressureBuffer(1000,  // max buffer size
                          item -> log.warn("Buffer overflow, dropping: " + item),
                          BufferOverflowStrategy.DROP_LATEST)
    .subscribe(this::slowProcess);
// Strategy 2: Drop — discard items when consumer can't keep up
fastProducer
    .onBackpressureDrop(dropped -> log.warn("Dropped: " + dropped))
    .subscribe(this::slowProcess);
// Strategy 3: Latest — only keep most recent value
fastProducer
    .onBackpressureLatest()  // always have latest; old values dropped
    .subscribe(this::slowProcess);
// Strategy 4: limitRate — request N items at a time (explicit pull)
fastProducer
    .limitRate(10)  // consumer requests 10 items at a time
    .subscribe(this::process);
// Server-Sent Events — WebFlux uses backpressure to pace streaming
@GetMapping(value = "/stream", produces = TEXT_EVENT_STREAM_VALUE)
public Flux<Long> stream() {
    return Flux.interval(Duration.ofMillis(100))  // 10 events/sec
        .take(100)
        .onBackpressureDrop();  // if client is slow, drop events
}
```

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| Backpressure only matters for disk/network I/O | It matters for any producer-consumer imbalance — CPU, DB, external API |
| Backpressure is automatic with Flux | Backpressure is available; you must choose the right strategy for your use case |
| All reactive operators preserve backpressure | Some operators (e.g., `flatMap` with too many concurrent tasks) can break backpressure |

### 🔗 Related Keywords

- **[Mono / Flux](./137 — Mono Flux.md)** — reactive types that implement backpressure
- **[WebFlux / Reactive](./136 — WebFlux Reactive.md)** — framework that uses backpressure-aware streams

### 📌 Quick Reference Card
```
+------------------------------------------------------------------+
| KEY IDEA    | Consumer controls how fast producer emits            |
+------------------------------------------------------------------+
| STRATEGIES  | buffer / drop / latest / limitRate                  |
+------------------------------------------------------------------+
| PROTOCOL    | Subscriber.request(n) → Publisher emits max n items  |
+------------------------------------------------------------------+
| ONE-LINER   | "Flow control in reactive streams"                   |
+------------------------------------------------------------------+
```

### 🧠 Think About This Before We Continue

**Q1.** What happens in Reactor when a `Flux` is created from a synchronous source (like a List) and subscribed to with a slow subscriber? Is backpressure respected?
**Q2.** `flatMap` in Reactor can break backpressure by spawning concurrent inner publishers. How does `concatMap` differ?
**Q3.** How does Netty integrate with Reactor backpressure for TCP write pressure — what happens when the client's TCP receive buffer is full?
