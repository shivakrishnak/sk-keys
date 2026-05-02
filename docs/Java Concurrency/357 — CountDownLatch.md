---
layout: default
title: "CountDownLatch"
parent: "Java Concurrency"
nav_order: 357
permalink: /java-concurrency/count-down-latch/
number: "0357"
category: Java Concurrency
difficulty: ★★☆
depends_on: Thread (Java), Semaphore (Java), ExecutorService
used_by: CyclicBarrier, Phaser, CompletableFuture
related: CyclicBarrier, Semaphore (Java), Phaser
tags:
  - java
  - concurrency
  - synchronization
  - intermediate
  - coordination
---

# 0357 — CountDownLatch

⚡ TL;DR — `CountDownLatch` is a one-shot barrier: initialised with count N, calling threads wait at `await()` until N other threads each call `countDown()` — enabling one thread to wait for N tasks to complete, or N threads to wait for one signal.

| #0357 | Category: Java Concurrency | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Thread (Java), Semaphore (Java), ExecutorService | |
| **Used by:** | CyclicBarrier, Phaser, CompletableFuture | |
| **Related:** | CyclicBarrier, Semaphore (Java), Phaser | |

---

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
A service starts five parallel initialisation tasks (database, cache, config, auth, messaging). The server should not accept requests until ALL five are ready. With `Object.wait()/notify()`, the coordinator must track which tasks finished — boilerplate involving counts, flags, and synchronised checks. Any scheduling mistake breaks the startup.

THE INVENTION MOMENT:
**`CountDownLatch`** provides a standard, simple "wait for N tasks" coordination primitive without manual counter management.

---

### 📘 Textbook Definition

**`CountDownLatch`** is a one-time synchronisation aid in `java.util.concurrent`. Initialised with a count `N`. `await()` blocks until count reaches 0. `countDown()` decrements count by 1; when it reaches 0, all waiting threads are released. Once 0, the latch cannot be reset — it's a one-shot gate. Multiple threads can await the same latch.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
`CountDownLatch(N)` = wait for N events to happen, then unblock.

**One analogy:**
> A rocket launch controller waits for N systems to give green-light. Each system calls `countDown()`. When all N are green (count = 0), the launch controller's `await()` returns and the rocket launches. Cannot be reset — one launch, one countdown.

**One insight:**
Two usage patterns: (1) **One waits for N** — service awaits N workers; (2) **N wait for one** — `CountDownLatch(1)` used as a starting gun: N threads `await()` until the controller calls `countDown(1)` to release all simultaneously.

---

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. Count starts at N, decrements-only — never increases after construction.
2. `await()` returns immediately if count already 0.
3. ONE-SHOT: once count reaches 0, it stays 0 forever — cannot reuse the latch.

```
Usage pattern 1: one waits for many
  latch = new CountDownLatch(3)
  worker1: work() → latch.countDown()  // count: 3→2
  worker2: work() → latch.countDown()  // count: 2→1
  worker3: work() → latch.countDown()  // count: 1→0 → RELEASE
  controller: latch.await() → UNBLOCKED

Usage pattern 2: many wait for one
  latch = new CountDownLatch(1)
  worker1: latch.await() → BLOCKED
  worker2: latch.await() → BLOCKED
  worker3: latch.await() → BLOCKED
  controller: latch.countDown() → ALL THREE UNBLOCKED
```

THE TRADE-OFFS:
Gain: Simple, clear, thread-safe counter-down coordination; reusable across many waiters (all blocked on same latch); no manual synchronisation.
Cost: One-shot — cannot reset; if `countDown()` never reaches 0 (due to exception), `await()` blocks forever without a timeout.

---

### 🧪 Thought Experiment

SETUP: Integration test that starts 5 services and waits for all to be "ready".

```java
CountDownLatch ready = new CountDownLatch(5);
for (Service svc : services) {
    executor.submit(() -> {
        svc.start();
        ready.countDown(); // when started
    });
}
ready.await(30, TimeUnit.SECONDS); // wait up to 30s
if (!ready.await(0, SECONDS)) {
    throw new StartupTimeoutException();
}
startAcceptingRequests();
```

THE INSIGHT: Any service throwing during `start()` without calling `countDown()` will cause `await()` to block for the full timeout. Always call `countDown()` in `finally` if the count must decrement even on failure.

---

### 🧠 Mental Model / Analogy

> A group photo: everyone must arrive before the photographer presses the shutter. Each person arriving = `countDown()`. Photographer waiting = `await()`. When all N people arrive (count = 0), photo is taken. No one arrives after the photo — latch is exhausted.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Wait for N things to finish, then proceed — once only.

**Level 2:** `new CountDownLatch(N)`. Workers: `latch.countDown()` (should be in `finally`). Coordinators: `latch.await()` or `latch.await(timeout, unit)`. Check `latch.getCount()` for monitoring. Not reusable — use `CyclicBarrier` for repeating barriers.

**Level 3:** Implemented via AQS shared mode. `State = N`. `countDown()` decrements state via CAS. When state reaches 0, `releaseShared(1)` calls `doReleaseShared()` which unparks all waiting `await()` threads (SHARED lock mode — all awaiters are unblocked simultaneously). Unlike exclusive AQS mode, SHARED mode can release all waiters at once.

**Level 4:** `CountDownLatch` uses AQS SHARED mode — all waiting threads are released when state = 0. This contrasts with `ReentrantLock` exclusive mode (only one waiter released per `unlock()`). The difference is architectural: CountDownLatch models "N events trigger global unblock" while locks model "one thread at a time".

---

### ⚙️ How It Works (Mechanism)

```java
// Pattern 1: Wait for N parallel tasks
CountDownLatch latch = new CountDownLatch(N);
for (int i = 0; i < N; i++) {
    final int taskId = i;
    executor.submit(() -> {
        try {
            processTask(taskId);
        } finally {
            latch.countDown(); // ALWAYS decrement
        }
    });
}
// Wait up to 60 seconds:
if (!latch.await(60, TimeUnit.SECONDS)) {
    throw new TimeoutException("Not all tasks completed");
}
// All N tasks have finished

// Pattern 2: Starting gun for N threads simultaneously
CountDownLatch startSignal = new CountDownLatch(1);
for (int i = 0; i < N; i++) {
    executor.submit(() -> {
        try {
            startSignal.await(); // all wait here
            doWork(); // all start simultaneously
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    });
}
// When ready to start all N threads:
startSignal.countDown(); // releases all
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
[CountDownLatch(3) created: count=3]
    → [3 workers submitted to executor]
    → [main thread: latch.await()]              ← YOU ARE HERE
    → [AQS: main thread state=WAITING]
    → [Worker 1 completes: countDown() → count=2]
    → [Worker 2 completes: countDown() → count=1]
    → [Worker 3 completes: countDown() → count=0]
    → [AQS: releaseShared → main thread UNPARKED]
    → [main thread: await() returns]
```

---

### 💻 Code Example

```java
// Application startup coordinator:
@Component
class StartupCoordinator {
    private final CountDownLatch servicesReady =
        new CountDownLatch(3); // DB, cache, auth

    @EventListener
    void onDatabaseReady(DatabaseReadyEvent e) {
        servicesReady.countDown();
    }
    @EventListener
    void onCacheReady(CacheReadyEvent e) {
        servicesReady.countDown();
    }
    @EventListener
    void onAuthReady(AuthReadyEvent e) {
        servicesReady.countDown();
    }

    void waitForStartup() throws InterruptedException {
        if (!servicesReady.await(60, SECONDS)) {
            throw new StartupFailedException("Startup timed out");
        }
    }
}
```

---

### ⚖️ Comparison Table

| Mechanism | Reset | Multiple Waiters | Count Direction | Best For |
|---|---|---|---|---|
| **CountDownLatch** | No (one-shot) | Yes | N→0 | One-time startup sync |
| CyclicBarrier | Yes | Yes (all arrive) | Arrives N times | Repeated phases |
| Phaser | Yes | Yes | Flexible | Multi-phase coordination |
| Semaphore | No (manual) | Yes | Any | Resource counting |

How to choose: `CountDownLatch` for one-time "wait for N" or "signal N simultaneously". `CyclicBarrier` for repeated phases where all threads must arrive before continuing.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| CountDownLatch can be reset and reused | NO — it's one-shot. Once count = 0, it stays 0. Use `CyclicBarrier` for reusable barriers |
| Exception in a task automatically calls countDown | NO — you must explicitly call `countDown()` in a `finally` block, or the main thread blocks until timeout |
| Only one thread can await | Multiple threads can all call `await()` and all are released when count = 0 |

---

### 🚨 Failure Modes & Diagnosis

**Await blocked forever (exception swallowed, countDown skipped):**

Fix: Always `countDown()` in `finally`:
```java
try {
    doWork();
} catch (Exception e) {
    log.error("Task failed", e);
} finally {
    latch.countDown(); // even on failure
}
```

**Awaiting too long without a timeout:**

Fix: Always use `latch.await(timeout, unit)` and handle the `false` return.

---

### 🔗 Related Keywords

**Prerequisites:** `Thread (Java)`, `ExecutorService`
**Builds on:** `CyclicBarrier` (reusable), `Phaser` (multi-phase)
**Related:** `CyclicBarrier`, `Semaphore`, `CompletableFuture.allOf()`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ One-shot gate: await blocks until N       │
│              │ countDown() calls reach zero              │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ ONE-SHOT — cannot reset. Always countDown │
│              │ in finally. Use timeout in await().       │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Wait for N things — fire once, stays open"│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ CyclicBarrier → Phaser → CompletableFuture│
└──────────────────────────────────────────────────────────┘
```

---
### 🧠 Think About This Before We Continue

**Q1.** `CountDownLatch` and `CompletableFuture.allOf(cf1, cf2, cf3).join()` both wait for N tasks to complete. Describe two scenarios where `CountDownLatch` is the better choice and two where `CompletableFuture.allOf()` is better — specifically considering: exception propagation, result retrieval, cancellation, and whether the "N tasks" are independent or require result composition.

