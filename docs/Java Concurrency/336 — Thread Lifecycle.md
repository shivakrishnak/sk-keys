---
layout: default
title: "Thread Lifecycle"
parent: "Java Concurrency"
nav_order: 68
permalink: /java-concurrency/thread-lifecycle/
---
# 068 — Thread Lifecycle

`#java` `#concurrency` `#threading` `#lifecycle`

⚡ TL;DR — A Java thread moves through six states: NEW → RUNNABLE → (BLOCKED | WAITING | TIMED_WAITING) → TERMINATED; understanding each state and what causes transitions is essential for diagnosing deadlocks, starvation, and thread dumps.

| #068 | Category: Java Concurrency | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Thread, synchronized, Object.wait, Thread.sleep | |
| **Used by:** | Deadlock, Thread Monitoring, ExecutorService | |

---

### 📘 Textbook Definition

The `Thread.State` enum in Java defines six lifecycle states for a thread:
- **NEW** — created but `start()` not yet called
- **RUNNABLE** — executing or ready to execute (OS scheduling decides)
- **BLOCKED** — waiting to acquire a monitor lock held by another thread
- **WAITING** — waiting indefinitely for another thread to notify it
- **TIMED_WAITING** — waiting with a timeout
- **TERMINATED** — `run()` has completed or thrown an uncaught exception

---

### 🟢 Simple Definition (Easy)

Think of thread states as a job application process:
- **NEW**: Application submitted, not started yet
- **RUNNABLE**: Working (or queued ready to work)
- **BLOCKED**: Waiting at a locked door (another thread holds the key)
- **WAITING**: Waiting for someone to call your name — no timeout
- **TIMED_WAITING**: Waiting 10 minutes, then giving up
- **TERMINATED**: Job done (or left the building)

---

### 🔵 Simple Definition (Elaborated)

Most threads spend their time in RUNNABLE (actively running CPU work). When two threads try to enter a `synchronized` block at the same time, the loser goes BLOCKED until the winner exits and releases the lock. WAITING and TIMED_WAITING happen when a thread deliberately pauses — waiting for a condition (`Object.wait()`), joining another thread (`join()`), or sleeping (`Thread.sleep()`). Thread dumps in production show every thread's state — BLOCKED chains reveal deadlocks; many threads WAITING reveals a starved thread pool.

---

### 🔩 First Principles Explanation

**State machine:**

```
          start()
NEW ──────────────→ RUNNABLE ←──────────────────────────────┐
                       │                                     │
           ┌───────────┼───────────┐                        │
           ↓           ↓           ↓                        │
       BLOCKED      WAITING   TIMED_WAITING                 │
           │           │           │                        │
           │  lock      │ notify/   │ timeout/              │
           │  acquired  │ interrupt │ notify/interrupt       │
           └───────────┴───────────┘                        │
                       │                                     │
                       └────────────────────────────────────┘
                                   │
                             run() returns or
                           uncaught exception
                                   ↓
                              TERMINATED
```

**What causes each transition:**

```
NEW → RUNNABLE
   thread.start() called

RUNNABLE → BLOCKED
   thread tries to enter synchronized block/method
   but another thread holds that monitor

BLOCKED → RUNNABLE
   the holding thread exits the synchronized block
   lock becomes available; blocked thread competes for it

RUNNABLE → WAITING
   obj.wait()              (releases lock, waits for obj.notify())
   thread.join()           (waits for that thread to terminate)
   LockSupport.park()      (waits for permit)

WAITING → RUNNABLE
   obj.notify() / notifyAll() called
   the joined thread terminates
   LockSupport.unpark(thread)

RUNNABLE → TIMED_WAITING
   Thread.sleep(ms)
   obj.wait(ms)
   thread.join(ms)
   LockSupport.parkNanos/Until()

TIMED_WAITING → RUNNABLE
   timeout expires, OR notified/interrupted before timeout

RUNNABLE → TERMINATED
   run() method returns (normally or via exception)
```

---

### ❓ Why Does This Exist — Why Before What

```
Without understanding thread states, you can't diagnose:

Deadlock:
  Thread A: BLOCKED waiting for lock held by B
  Thread B: BLOCKED waiting for lock held by A
  → Both BLOCKED forever → jstack shows it instantly

Starvation:
  Thread pool threads all in WAITING
  → work queue processed, but tasks arrive faster than submitted
  → or: high-priority threads prevent low-priority from running

Livelock:
  Threads not BLOCKED or WAITING — they're all RUNNABLE
  but making no progress (respawn/retry loop)

Thread leak:
  Thread count growing → RUNNABLE or WAITING threads never terminate
  → identify via jstack + thread state audit

With thread state knowledge:
  jstack / VisualVM / jcmd → show all thread states
  → diagnose BLOCKED chains → deadlock candidates
  → diagnose WAITING threads → starved consumers
  → diagnose TIMED_WAITING → sleeping/retry loops
```

---

### 🧠 Mental Model / Analogy

> Thread lifecycle is like a **worker's workday at a shared workshop**:
> - **NEW**: Worker hired, hasn't shown up yet
> - **RUNNABLE**: Working at their bench (or in line for a free bench)
> - **BLOCKED**: Standing at the door of a locked tool room — waiting for the key
> - **WAITING**: Sitting in the break room waiting for a colleague to call them
> - **TIMED_WAITING**: Sleeping an alarm — will wake up in 5 minutes regardless
> - **TERMINATED**: Clocked out, gone home

---

### ⚙️ How It Works — Key Methods Per State

| Transition | Method/Action | Lock released? |
|---|---|---|
| → BLOCKED | Enter `synchronized` | N/A (can't get lock) |
| → WAITING | `obj.wait()` | ✅ Yes |
| → WAITING | `thread.join()` | ❌ No |
| → TIMED_WAITING | `Thread.sleep(ms)` | ❌ No |
| → TIMED_WAITING | `obj.wait(ms)` | ✅ Yes |
| → RUNNABLE | `obj.notify()` | Must re-acquire lock |

**Critical: `wait()` vs `sleep()`**

```
Thread.sleep(1000):
  → TIMED_WAITING for 1 second
  → does NOT release any held locks
  → wakes up after timeout (or interrupt)

obj.wait():
  → WAITING (or TIMED_WAITING with wait(ms))
  → RELEASES the monitor lock on 'obj'
  → wakes only when notified or interrupted
  → must own the lock before calling wait()
```

---

### 🔄 How It Connects

```
Thread Lifecycle
  │
  ├─ BLOCKED → Deadlock analysis (two BLOCKED threads waiting for each other)
  ├─ WAITING → Consumer-Producer pattern (wait/notify)
  ├─ TIMED_WAITING → Retry loops, health checks, backoff strategies
  ├─ TERMINATED → Thread pool recycles the thread for a new task
  │
  ├─ jstack / jcmd thread dump → shows state of ALL threads
  └─ Thread.getState() → programmatic access to current state
```

---

### 💻 Code Example

```java
// Observing thread states programmatically
Thread t = new Thread(() -> {
    try { Thread.sleep(2000); }
    catch (InterruptedException e) { Thread.currentThread().interrupt(); }
});

System.out.println(t.getState()); // NEW

t.start();
System.out.println(t.getState()); // RUNNABLE (or TIMED_WAITING if fast enough)

Thread.sleep(100);
System.out.println(t.getState()); // TIMED_WAITING (sleeping for 2s)

t.join();
System.out.println(t.getState()); // TERMINATED
```

```java
// WAITING state via wait/notify
Object lock = new Object();

Thread waiter = new Thread(() -> {
    synchronized (lock) {
        try {
            System.out.println("Waiter: waiting...");
            lock.wait();   // → WAITING, releases lock
            System.out.println("Waiter: notified!");
        } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
    }
});

Thread notifier = new Thread(() -> {
    try { Thread.sleep(500); } catch (InterruptedException ignored) {}
    synchronized (lock) {
        System.out.println("Notifier: notifying...");
        lock.notify(); // → waiter becomes RUNNABLE
    }
});

waiter.start();
notifier.start();
```

```java
// BLOCKED state
Object sharedLock = new Object();

Thread holder = new Thread(() -> {
    synchronized (sharedLock) {
        System.out.println("Holder has the lock");
        try { Thread.sleep(3000); } catch (InterruptedException ignored) {}
    }
});

Thread contender = new Thread(() -> {
    System.out.println("Contender: waiting for lock...");
    synchronized (sharedLock) { // → BLOCKED until holder releases
        System.out.println("Contender: got the lock");
    }
});

holder.start();
Thread.sleep(100);
contender.start();

Thread.sleep(100);
System.out.println("Contender state: " + contender.getState()); // BLOCKED
```

---

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| RUNNABLE means the thread is using CPU | RUNNABLE = "eligible to run" — OS scheduler decides if CPU is actually assigned |
| WAITING and BLOCKED are the same | BLOCKED: waiting for a lock; WAITING: paused until notified — different mechanisms |
| `Thread.sleep()` releases held locks | sleep() does NOT release locks — use `wait()` to release |
| A TERMINATED thread can be restarted | Once TERMINATED, a thread cannot be started again — create a new Thread |
| Thread.getState() is expensive | getState() is efficient and safe to call for monitoring |

---

### 🔥 Pitfalls in Production

**Pitfall 1: Calling `wait()` without owning the lock**

```java
// ❌ IllegalMonitorStateException
lock.wait(); // must be inside synchronized(lock) { ... }

// ✅ Correct
synchronized (lock) {
    while (!condition) { lock.wait(); } // own lock, then wait
}
```

**Pitfall 2: Using `notify()` instead of `notifyAll()`**

```java
// ❌ Risk: notifying the wrong thread (spurious wakeup handling)
// If multiple threads wait → notify() wakes only ONE unpredictably
lock.notify();

// ✅ Use notifyAll() when multiple threads may be waiting on the same condition
lock.notifyAll(); // wakes all; each re-checks condition in their while loop
```

**Pitfall 3: Using `if` instead of `while` for wait condition (spurious wakeup)**

```java
// ❌ Spurious wakeup — thread wakes without being notified
synchronized (lock) {
    if (!ready) lock.wait(); // may wake spuriously → ready still false!
    process();               // processes prematurely
}

// ✅ Always use while loop
synchronized (lock) {
    while (!ready) lock.wait(); // re-checks condition after each wakeup
    process();
}
```

---

### 🔗 Related Keywords

- **[Thread](./066 — Thread.md)** — the unit whose lifecycle this describes
- **[synchronized](./069 — synchronized.md)** — causes BLOCKED state when contended
- **[Deadlock](./071 — Deadlock.md)** — two threads permanently BLOCKED on each other
- **[ExecutorService](./074 — ExecutorService.md)** — manages thread lifecycle within a pool
- **jstack** — tool to dump all thread states in a running JVM

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ 6 states: NEW→RUNNABLE→(BLOCKED|WAITING|      │
│              │ TIMED_WAITING)→TERMINATED                     │
├──────────────┼───────────────────────────────────────────────┤
│ USE WHEN     │ Reading thread dumps: BLOCKED = lock wait,    │
│              │ WAITING = condition wait, TIMED = sleep/join  │
├──────────────┼───────────────────────────────────────────────┤
│ AVOID WHEN   │ Don't call wait() outside synchronized block; │
│              │ don't use if() for wait condition (use while) │
├──────────────┼───────────────────────────────────────────────┤
│ ONE-LINER    │ "Thread dump tells the whole story:           │
│              │  BLOCKED = lock contention,                   │
│              │  WAITING = needs a signal to wake up"         │
├──────────────┼───────────────────────────────────────────────┤
│ NEXT EXPLORE │ synchronized → Deadlock → wait/notify →       │
│              │ ExecutorService → CompletableFuture           │
└──────────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A thread dump shows 50 threads all in BLOCKED state, all waiting on a lock held by thread "main". Thread "main" is in TIMED_WAITING. What is almost certainly happening? How would you fix this?

**Q2.** What is a spurious wakeup and why does the Java memory model permit it? How does the `while` pattern protect against it?

**Q3.** Thread A calls `t.join()` on Thread B. What state is Thread A in while waiting? Does Thread A release any locks it holds during this wait?

