---
layout: default
title: "CountDownLatch"
parent: "Java Concurrency"
nav_order: 357
permalink: /java-concurrency/countdownlatch/
number: "357"
category: Java Concurrency
difficulty: ★★☆
depends_on: Thread, ExecutorService, Thread Lifecycle
used_by: Test Synchronisation, Startup Barriers, Fan-in
tags: #java, #concurrency, #synchronizer, #coordination
---

# 357 — CountDownLatch

`#java` `#concurrency` `#synchronizer` `#coordination`

⚡ TL;DR — CountDownLatch makes one (or more) threads wait until a countdown of N events reaches zero — it is a single-use gate: once open, it stays open and cannot be reset.

| #357 | category: Java Concurrency
|:---|:---|:---|
| **Depends on:** | Thread, ExecutorService, Thread Lifecycle | |
| **Used by:** | Test Synchronisation, Startup Barriers, Fan-in | |

---

### 📘 Textbook Definition

`java.util.concurrent.CountDownLatch` is a synchronization aid initialised with a count N. Threads call `await()` to block until the count reaches zero. Other threads (or the same threads) call `countDown()` to decrement the count. When the count reaches zero, all waiting threads are released. The latch is **one-shot** — the count cannot be reset; use `CyclicBarrier` if you need repeatable rendezvous.

---

### 🟢 Simple Definition (Easy)

Picture a race starting gate that opens only after N bolts are removed. Each worker removes one bolt (`countDown()`). The racers (`await()`) wait at the gate. The moment the last bolt is removed, the gate swings open and all racers go.

---

### 🔵 Simple Definition (Elaborated)

CountDownLatch is the answer to "don't start until N things have finished." Common uses: wait for all services to initialise before accepting requests; coordinate parallel test setup; fan-in multiple async results before processing. The key property: calling `countDown()` never blocks — it is a decrement operation. Only `await()` blocks. Once zero is reached, subsequent `await()` calls return immediately (the gate stays permanently open).

---

### 🔩 First Principles Explanation

```
Pattern: wait for N independent events before proceeding

Without CountDownLatch:
  Manually track count in volatile int + synchronized notify → error-prone

With CountDownLatch:
  CountDownLatch latch = new CountDownLatch(N);
  
  // N workers each call:
  latch.countDown();    // decrement
  
  // Coordinator calls:
  latch.await();        // block until count == 0

Internal: a volatile int counter + AbstractQueuedSynchronizer
  countDown() → decrements; if reaches 0 → releases all waiters
  await()     → enters AQS wait queue if count > 0; released when count hits 0
```

---

### ❓ Why Does This Exist — Why Before What

```
Without CountDownLatch:
  Option: join() each thread → only works for the thread itself, not events
  Option: shared volatile flag → only works for one event (no count)
  Option: wait/notifyAll loop → verbose, error-prone boilerplate

With CountDownLatch:
  ✅ Clean N-event wait with one line: latch.await()
  ✅ Non-blocking countDown() can be called from anywhere
  ✅ Thread-safe by design — no manual synchronization needed
  ✅ Timed await: latch.await(5, TimeUnit.SECONDS)
```

---

### 🧠 Mental Model / Analogy

> A spaceship launch countdown. Ground control (`await()`) waits until all N systems check in (`countDown()`). When the last system confirms, launch (proceed) happens. But the countdown only runs once — it's not a recurring event.

---

### ⚙️ How It Works

```
CountDownLatch latch = new CountDownLatch(3);
                                              ↑ count = 3

Thread A: latch.countDown()  → count = 2
Thread B: latch.countDown()  → count = 1
Thread C: latch.countDown()  → count = 0 → releases all awaiters

Main: latch.await()          → blocks until count == 0
      latch.await(5, SECONDS) → blocks up to 5s; returns false on timeout

Key methods:
  new CountDownLatch(int count)
  void  countDown()                 → decrement count; never blocks
  void  await()                     → block until count == 0
  boolean await(long, TimeUnit)     → timed await; returns false on timeout
  long  getCount()                  → inspect current count (diagnostic)
```

---

### 🔄 How It Connects

```
CountDownLatch
  │
  ├─ One-shot gate  → cannot be reset (use CyclicBarrier for repeatable)
  ├─ Asymmetric     → N workers count down, M waiters wait (can differ)
  ├─ vs CyclicBarrier → all threads meet at barrier; reusable; same count
  ├─ vs Semaphore    → Semaphore controls resource access; latch is one-shot
  └─ Uses AQS (AbstractQueuedSynchronizer) internally
```

---

### 💻 Code Example

```java
// Pattern 1: Wait for N services to start
CountDownLatch startLatch = new CountDownLatch(3);
ExecutorService pool = Executors.newFixedThreadPool(3);

String[] services = {"Database", "Cache", "MessageQueue"};
for (String svc : services) {
    pool.submit(() -> {
        initService(svc);           // slow initialisation
        startLatch.countDown();     // signal: I'm ready
    });
}

startLatch.await();                 // wait until all 3 are ready
System.out.println("All services up — accepting requests");
```

```java
// Pattern 2: Coordinated test — all threads start simultaneously
int threads = 10;
CountDownLatch ready = new CountDownLatch(threads); // workers signal ready
CountDownLatch go    = new CountDownLatch(1);        // starter fires gun
CountDownLatch done  = new CountDownLatch(threads); // coordinator waits for finish

for (int i = 0; i < threads; i++) {
    pool.submit(() -> {
        ready.countDown();       // "I'm ready"
        go.await();              // wait for start signal
        performWork();
        done.countDown();        // "I'm finished"
    });
}

ready.await();   // wait until all threads ready
go.countDown();  // fire the starting gun — all threads released simultaneously
done.await();    // wait for all to complete
```

```java
// Timed await — don't wait forever
if (!latch.await(10, TimeUnit.SECONDS)) {
    System.err.println("Timed out waiting for services; starting anyway");
}
```

---

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| countDown() blocks if count is 0 | countDown() never blocks; calling it after 0 is safely ignored |
| CountDownLatch can be reset for reuse | Single-use only; construct a new instance for each round |
| Only one thread can await() | Multiple threads can call await() simultaneously — all released when count reaches 0 |
| countDown() and await() must be in different threads | Can be in the same thread (unusual but valid) |

---

### 🔥 Pitfalls in Production

**Pitfall 1: countDown() not called on exception — await() waits forever**

```java
pool.submit(() -> {
    try {
        riskyOperation();
    } finally {
        latch.countDown();  // ✅ always in finally — ensures latch decrements even on exception
    }
});
latch.await(30, TimeUnit.SECONDS); // ✅ always use timed await as safety net
```

**Pitfall 2: Reusing a CountDownLatch — creates a new one instead**

```java
// ❌ Wrong: same latch in a loop — after count reaches 0, it stays 0 forever
for (int round = 0; round < 5; round++) {
    tasks.forEach(t -> pool.submit(t));
    latch.await();  // latch is already 0 after round 1 — never blocks again
}
// ✅ Create fresh latch each round, or use CyclicBarrier
```

---

### 🔗 Related Keywords

- **[CyclicBarrier](./079 — CyclicBarrier.md)** — reusable N-thread rendezvous
- **[Semaphore](./080 — Semaphore.md)** — controls access to N resources
- **[ExecutorService](./074 — ExecutorService.md)** — countDown() typically called in pool tasks
- **[Future & CompletableFuture](./075 — Future and CompletableFuture.md)** — alternative for async fan-in

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ One-shot gate: await() blocks until N         │
│              │ countDown() calls reduce count to zero        │
├──────────────┼───────────────────────────────────────────────┤
│ USE WHEN     │ Wait for N parallel init events; start N      │
│              │ threads simultaneously; fan-in results        │
├──────────────┼───────────────────────────────────────────────┤
│ AVOID WHEN   │ Need reusable barrier → CyclicBarrier;        │
│              │ need resource control → Semaphore             │
├──────────────┼───────────────────────────────────────────────┤
│ ONE-LINER    │ "N bolts on a gate — remove them all          │
│              │  and the gate opens forever"                  │
├──────────────┼───────────────────────────────────────────────┤
│ NEXT EXPLORE │ CyclicBarrier → Semaphore → Phaser →          │
│              │ CompletableFuture.allOf()                     │
└──────────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You have a latch of count 3, and 3 workers each call `countDown()` in a finally block. A 4th thread calls `await()`. Is it possible for `await()` to never return? What condition would cause this?

**Q2.** How would you implement a start-gun pattern (all threads start at the same instant) without CountDownLatch, using only `Object.wait/notifyAll`?

**Q3.** `CompletableFuture.allOf(f1, f2, f3)` and `CountDownLatch(3)` can both coordinate fan-in of 3 async tasks. What are the key differences in threading model and exception handling?

