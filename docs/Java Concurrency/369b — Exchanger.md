---
layout: default
title: "Exchanger"
parent: "Java Concurrency"
nav_order: 369
permalink: /java-concurrency/exchanger/
number: "369"
category: Java Concurrency
difficulty: ★★☆
depends_on: Thread, BlockingQueue, Semaphore
used_by: Pipeline Stages, Double Buffering, Genetic Algorithms
tags: #java, #concurrency, #synchronizer, #exchanger, #handoff
---

# 369 — Exchanger

`#java` `#concurrency` `#synchronizer` `#exchanger` `#handoff`

⚡ TL;DR — Exchanger is a two-thread rendezvous point where both threads swap a data object atomically — each thread gives and receives one item; both block until the partner arrives, ensuring simultaneous handoff.

| #369 | Category: Java Concurrency | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Thread, BlockingQueue, Semaphore | |
| **Used by:** | Pipeline Stages, Double Buffering, Genetic Algorithms | |

---

### 📘 Textbook Definition

`java.util.concurrent.Exchanger<V>` enables two threads to exchange objects at a synchronisation point. Thread A calls `exchange(objectA)` and blocks. Thread B calls `exchange(objectB)` and blocks. When both have called `exchange()`, each receives the other's object, and both are released simultaneously. A timed variant `exchange(obj, timeout, unit)` prevents deadlock if a partner never arrives.

---

### 🟢 Simple Definition (Easy)

Two people meet at a designated spot and swap bags. Person A waits until Person B arrives; Person B waits until Person A arrives. The moment both are there, they swap — both get the other's bag and both leave at the same instant.

---

### 🔵 Simple Definition (Elaborated)

Exchanger solves a niche but useful problem: a pipeline stage producing data while the consuming stage is working — the moment the consumer finishes, they swap buffers. This is the classic **double-buffering** or **fill-then-drain** pattern. Producer fills a buffer; consumer drains it. When both are done, they `exchange()` buffers — producer gets the empty one, consumer gets the full one. Both immediately start the next cycle with zero wait.

---

### 🔩 First Principles Explanation

```
Without Exchanger (naive double buffer):
  shared volatile DataBuffer buffer;
  synchronized handoff → one thread always blocked waiting

With Exchanger:
  Thread A (producer):
    fill(myBuffer);
    myBuffer = exchanger.exchange(myBuffer); // give full, get empty

  Thread B (consumer):
    drain(myBuffer);
    myBuffer = exchanger.exchange(myBuffer); // give empty, get full

  Synchronization: both block until BOTH call exchange()
  Then both resume simultaneously — zero handoff latency

Flow:
  Producer: fill buffer → exchange → fill buffer → exchange ...
  Consumer:              drain ← exchange → drain ← exchange ...
  Meeting point: each exchange is a simultaneous swap
```

---

### 🧠 Mental Model / Analogy

> Two runners in a relay race who hand off a baton at the same time — but this relay, BOTH runners are giving AND receiving. Runner A has the loaded baton; Runner B has the empty one. They meet, swap simultaneously, and both sprint off in opposite directions. If one doesn't show up, the other waits indefinitely (or times out).

---

### ⚙️ How It Works

```
Exchanger<V> exchanger = new Exchanger<>();

V exchange(V item)
  → If no partner waiting: block until partner arrives
  → If partner waiting: swap items, both released simultaneously
  → Returns: partner's item

V exchange(V item, long timeout, TimeUnit unit)
  → Timed version: throws TimeoutException if partner doesn't arrive in time

Characteristics:
  Exactly 2 threads per exchange
  Both block until both have called exchange()
  Atomically swaps objects between threads
  Thread-safe by design (no external synchronization needed)
```

---

### 🔄 How It Connects

```
Exchanger
  ├─ Purpose     → two-thread atomic data swap
  ├─ vs BlockingQueue → queue is one-directional; Exchanger is bidirectional swap
  ├─ vs SynchronousQueue → SQ passes item one-way; Exchanger is two-way swap
  ├─ Use cases   → double buffering, pipeline handoffs, genetic crossover
  └─ Limitation  → exactly 2 threads; for N-way rendezvous use CyclicBarrier
```

---

### 💻 Code Example

```java
// Double-buffer exchange: producer fills, consumer drains
Exchanger<List<Integer>> exchanger = new Exchanger<>();

// Producer thread
Thread producer = new Thread(() -> {
    List<Integer> buffer = new ArrayList<>();
    try {
        for (int cycle = 0; cycle < 5; cycle++) {
            // Fill buffer
            for (int i = 0; i < 10; i++) buffer.add(produce());
            System.out.println("Producer: filled buffer with " + buffer.size() + " items");

            // Swap: give full buffer, receive empty buffer
            buffer = exchanger.exchange(buffer);
            // buffer is now the empty list returned by consumer
        }
    } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
});

// Consumer thread
Thread consumer = new Thread(() -> {
    List<Integer> buffer = new ArrayList<>(); // starts with empty buffer
    try {
        for (int cycle = 0; cycle < 5; cycle++) {
            // Swap: give empty buffer, receive full buffer
            buffer = exchanger.exchange(buffer);
            // buffer is now full list from producer
            System.out.println("Consumer: draining " + buffer.size() + " items");
            for (int item : buffer) consume(item);
            buffer.clear(); // empty it for next exchange
        }
    } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
});

producer.start();
consumer.start();
```

```java
// Timed exchange — prevent indefinite wait if partner never arrives
try {
    DataPacket received = exchanger.exchange(myPacket, 5, TimeUnit.SECONDS);
    process(received);
} catch (TimeoutException e) {
    System.err.println("Partner didn't show up within 5 seconds");
} catch (InterruptedException e) {
    Thread.currentThread().interrupt();
}
```

---

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| Exchanger supports more than 2 threads | Exactly 2 threads per exchange — for 3+ use CyclicBarrier or BlockingQueue |
| Exchange is non-blocking | Both threads block until both call exchange() — inherently blocking rendezvous |
| You can use the same Exchanger for multiple concurrent pairs | Second pair must wait until first completes — Exchanger matches exactly one pair at a time |

---

### 🔗 Related Keywords

- **[BlockingQueue](./081 — BlockingQueue.md)** — one-directional transfer; Exchanger is two-way
- **[CyclicBarrier](./079 — CyclicBarrier.md)** — N-thread rendezvous without data exchange
- **[Semaphore](./080 — Semaphore.md)** — permit transfer; exchanger transfers typed objects

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Two threads meet and atomically swap objects  │
│              │ — both block until the partner arrives        │
├──────────────┼───────────────────────────────────────────────┤
│ USE WHEN     │ Double buffering pipeline; producer/consumer  │
│              │ buffer swap; two-party genetic crossover      │
├──────────────┼───────────────────────────────────────────────┤
│ AVOID WHEN   │ Need more than 2 parties → CyclicBarrier;     │
│              │ one-way transfer → BlockingQueue              │
├──────────────┼───────────────────────────────────────────────┤
│ ONE-LINER    │ "Two runners meet and swap batons —           │
│              │  both wait until both are there"              │
├──────────────┼───────────────────────────────────────────────┤
│ NEXT EXPLORE │ BlockingQueue → CyclicBarrier → Phaser →      │
│              │ SynchronousQueue                              │
└──────────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** In the double-buffer pattern, if the producer is always faster than the consumer, what happens at the `exchanger.exchange()` call? Does the producer accumulate data or block?

**Q2.** Could you implement the Exchanger pattern using two `SynchronousQueue` instances? What would the code look like, and how does it compare to using Exchanger directly?

**Q3.** What happens if three threads all call `exchange()` on the same Exchanger? Two will meet and swap — what happens to the third?

