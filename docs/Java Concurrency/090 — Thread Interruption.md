---
layout: default
title: "Thread Interruption"
parent: "Java Concurrency"
nav_order: 90
permalink: /java-concurrency/thread-interruption/
number: "090"
category: Java Concurrency
difficulty: ★★☆
depends_on: Thread, Thread Lifecycle, InterruptedException, ExecutorService
used_by: Cancellation, Shutdown, Timeouts, Task Cancellation
tags: #java, #concurrency, #threading, #interruption, #cancellation
---

# 090 — Thread Interruption

`#java` `#concurrency` `#threading` `#interruption` `#cancellation`

⚡ TL;DR — Thread interruption is Java's cooperative cancellation mechanism: `thread.interrupt()` sets a flag; the thread must periodically check `isInterrupted()` or respond to `InterruptedException` from blocking methods to stop cleanly.

| #090 | Category: Java Concurrency | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Thread, Thread Lifecycle, InterruptedException, ExecutorService | |
| **Used by:** | Cancellation, Shutdown, Timeouts, Task Cancellation | |

---

### 📘 Textbook Definition

Thread interruption is a cooperative asynchronous signalling mechanism. `thread.interrupt()` sets the thread's **interrupt status flag** to `true`. If the thread is blocked in a method that declares `throws InterruptedException` (`sleep`, `wait`, `join`, `BlockingQueue.take`, `Lock.lockInterruptibly`, etc.), an `InterruptedException` is thrown immediately and **the interrupt flag is cleared**. If the thread is not blocked, only the flag is set — the thread must check `Thread.currentThread().isInterrupted()` to detect it.

---

### 🟢 Simple Definition (Easy)

`thread.interrupt()` is a polite knock on the door: "Please stop when you get a chance." The thread doesn't stop immediately — it's just notified. The thread must either check `isInterrupted()` periodically or be in a blocking state where the JVM auto-delivers the interruption as an exception.

---

### 🔵 Simple Definition (Elaborated)

Java has no Thread.stop() (deprecated, unsafe — leaves objects in inconsistent state). The correct way to stop a thread is cooperation: the requester sets the interrupt flag; the target thread checks and handles it. Blocking methods (`sleep`, `wait`, `take`, `join`) check the interrupt flag — if set, they throw `InterruptedException` and clear the flag. Non-blocking loops must check `isInterrupted()` manually. The golden rule: **never swallow InterruptedException** — either rethrow it, or set the flag back with `Thread.currentThread().interrupt()`.

---

### 🔩 First Principles Explanation

```
Why not Thread.stop()?  (deprecated)
  Thread.stop() forcibly terminates, releasing all monitors
  → Object left in inconsistent state mid-update
  → Data corruption, silent bugs
  Removed in Java 21

Why cooperative interruption?
  Only the target thread knows safe stopping points
  → "I'll stop when I'm done with this unit of work"
  → Consistent state guaranteed

Interrupt mechanism:
  thread.interrupt()
    → if thread blocked in sleep/wait/join:
       throws InterruptedException (flag CLEARED)
    → if thread not blocked:
       flag = true (must poll isInterrupted())

  Thread.currentThread().isInterrupted()  → poll flag (does NOT clear)
  Thread.interrupted()                    → poll flag AND CLEAR (static method)
```

---

### 🧠 Mental Model / Analogy

> A sticky note on a colleague's monitor: "Please wrap up and come to a meeting." The colleague finishes their current task (safe stopping point), reads the note, and comes. They weren't forcibly dragged away mid-sentence — they chose when to stop. The meeting organiser (interrupt caller) just left the note (`interrupt()`); the colleague (thread) must check it (`isInterrupted()`) or be in a state where it's delivered automatically (blocking methods).

---

### ⚙️ How It Works

```
thread.interrupt() → sets interrupt flag = true

If thread currently in:
  Thread.sleep(ms)           → throws InterruptedException (flag cleared)
  Object.wait()              → throws InterruptedException (flag cleared)
  Thread.join()              → throws InterruptedException (flag cleared)
  BlockingQueue.take()       → throws InterruptedException (flag cleared)
  Lock.lockInterruptibly()   → throws InterruptedException (flag cleared)
  Socket/NIO blocking I/O    → SocketException / ClosedByInterruptException

If thread NOT blocked:
  flag set to true, thread continues running
  thread must check: Thread.currentThread().isInterrupted()

After InterruptedException is caught:
  flag is CLEARED automatically
  ✅ Rethrow: throw e;  OR  throw new RuntimeException(e);
  ✅ Restore: Thread.currentThread().interrupt();
  ❌ Swallow: catch (InterruptedException e) {}  ← NEVER do this
```

---

### 🔄 How It Connects

```
Thread Interruption
  │
  ├─ Mechanism for ──→ graceful shutdown, task cancellation, timeout
  ├─ Used in       ──→ ExecutorService.shutdownNow() (interrupts running tasks)
  ├─ Used in       ──→ Future.cancel(true) (interrupts the thread running the task)
  ├─ Related       ──→ Thread Lifecycle (interrupted thread unblocks from WAITING/TIMED_WAITING)
  └─ Never         ──→ Thread.stop() (removed), unsafe
```

---

### 💻 Code Example

```java
// Interruptible loop — check flag regularly
Runnable task = () -> {
    while (!Thread.currentThread().isInterrupted()) {
        processNextItem();   // one unit of work
    }
    System.out.println("Stopped cleanly");
};

Thread worker = new Thread(task);
worker.start();
Thread.sleep(5000);
worker.interrupt();   // politely stop the thread
```

```java
// Handling InterruptedException — two correct patterns

// Pattern 1: RETHROW (if method declares throws InterruptedException)
public void doWork() throws InterruptedException {
    while (!Thread.currentThread().isInterrupted()) {
        String item = queue.take();  // throws InterruptedException
        process(item);
    }
}

// Pattern 2: RESTORE FLAG (if can't rethrow — e.g. Runnable.run())
public void run() {
    try {
        while (!Thread.currentThread().isInterrupted()) {
            String item = queue.take();
            process(item);
        }
    } catch (InterruptedException e) {
        Thread.currentThread().interrupt(); // ✅ restore flag
        System.out.println("Worker interrupted, exiting");
    }
}
```

```java
// ❌ BAD — swallowing InterruptedException
try {
    Thread.sleep(1000);
} catch (InterruptedException e) {
    // do nothing — WRONG!
    // interrupt flag cleared, thread continues as if nothing happened
    // cancellation request silently ignored
}
```

```java
// ExecutorService shutdown — interrupts running tasks
ExecutorService pool = Executors.newFixedThreadPool(4);
pool.submit(() -> {
    try {
        while (!Thread.currentThread().isInterrupted()) {
            processTask();
        }
    } catch (InterruptedException e) {
        Thread.currentThread().interrupt();
    }
});

pool.shutdownNow(); // → calls thread.interrupt() on all running threads
pool.awaitTermination(5, TimeUnit.SECONDS);
```

---

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| `interrupt()` immediately stops the thread | It sets a flag; thread stops only when it checks the flag or hits a blocking operation |
| After catching `InterruptedException`, the flag is still set | Catching InterruptedException CLEARS the flag — must restore with `Thread.currentThread().interrupt()` |
| `Thread.interrupted()` is the same as `isInterrupted()` | `interrupted()` is static, returns flag AND clears it; `isInterrupted()` is instance, does NOT clear |
| `synchronized` blocks respond to interruption | `synchronized` IGNORES interruption while blocking; use `lockInterruptibly()` for responsiveness |

---

### 🔥 Pitfalls in Production

**Pitfall 1: Swallowing InterruptedException — cancellation silently ignored**

```java
// ❌ Most common bug in concurrency code
try { Thread.sleep(1000); } catch (InterruptedException e) { /* ignore */ }
// Thread continues; the interrupt request is lost; shutdown blocks forever

// ✅ Always restore or rethrow
catch (InterruptedException e) { Thread.currentThread().interrupt(); }
```

**Pitfall 2: Infinite loop not checking interrupt flag**

```java
// ❌ Thread can never be stopped by interrupt
Runnable r = () -> {
    while (true) { doWork(); } // flag never checked; InterruptedException never thrown
};
// Fix: check isInterrupted() in the loop condition
while (!Thread.currentThread().isInterrupted()) { doWork(); }
```

---

### 🔗 Related Keywords

- **[Thread Lifecycle](./068 — Thread Lifecycle.md)** — interruption moves threads from WAITING to RUNNABLE
- **[ExecutorService](./074 — ExecutorService.md)** — `shutdownNow()` uses interruption
- **[Future & CompletableFuture](./075 — Future and CompletableFuture.md)** — `cancel(true)` interrupts the running thread
- **ReentrantLock.lockInterruptibly()** — interruptible lock acquisition

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Cooperative cancellation via flag; blocking   │
│              │ methods throw InterruptedException when set   │
├──────────────┼───────────────────────────────────────────────┤
│ USE WHEN     │ Stopping long-running tasks; implementing     │
│              │ cancellable operations; graceful shutdown     │
├──────────────┼───────────────────────────────────────────────┤
│ AVOID WHEN   │ Never swallow InterruptedException; never use │
│              │ Thread.stop(); don't use deprecated methods   │
├──────────────┼───────────────────────────────────────────────┤
│ ONE-LINER    │ "A polite knock, not a forced exit —          │
│              │  the thread decides when it's safe to stop"  │
├──────────────┼───────────────────────────────────────────────┤
│ NEXT EXPLORE │ ExecutorService.shutdownNow() → Future.cancel │
│              │ → lockInterruptibly → Structured Concurrency  │
└──────────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You call `future.cancel(true)` on a running task. The task is currently inside a `synchronized` block waiting for a monitor. Will the task respond to the interruption? What if it were in `lock.lockInterruptibly()`?

**Q2.** `Thread.interrupted()` (static) vs `Thread.currentThread().isInterrupted()` (instance) — both check the interrupt flag, but one clears it. Give a scenario where calling the wrong one causes a subtle bug.

**Q3.** A task catches `InterruptedException` but needs to continue processing the current item before stopping. Write the correct pattern to: (1) finish the current item, (2) then exit cleanly using the interrupt flag.

