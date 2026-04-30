---
layout: default
title: "Livelock"
parent: "Java Concurrency"
nav_order: 88
permalink: /java-concurrency/livelock/
number: "088"
category: Java Concurrency
difficulty: ★★★
depends_on: Deadlock, Thread, ReentrantLock, Race Condition
used_by: tryLock, Backoff Strategies, Retry Logic
tags: #java, #concurrency, #livelock, #threading, #bugs
---

# 088 — Livelock

`#java` `#concurrency` `#livelock` `#threading` #bugs`

⚡ TL;DR — Livelock is a concurrency hazard where threads are actively running and responding to each other but making zero progress — they continuously react to the other's actions without ever completing their work.

| #088 | Category: Java Concurrency | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Deadlock, Thread, ReentrantLock, Race Condition | |
| **Used by:** | tryLock, Backoff Strategies, Retry Logic | |

---

### 📘 Textbook Definition

**Livelock** is a situation in which two or more threads continuously change their states in response to each other without making progress toward completing their work. Unlike deadlock (threads are BLOCKED and inactive), livelocked threads remain RUNNABLE — they appear active in CPU usage and thread dumps but accomplish nothing. Livelock typically arises in naive retry/backoff implementations where both threads simultaneously back off and retry at identical intervals.

---

### 🟢 Simple Definition (Easy)

Two people in a narrow hallway both step aside to let the other pass — but both step to the SAME side simultaneously. They each try to be polite, step aside, see the other stepping aside, step back… and repeat forever. Nobody passes. Both are active, both are moving, nobody is getting anywhere.

---

### 🔵 Simple Definition (Elaborated)

Livelock is the polite cousin of deadlock. In deadlock, threads are frozen waiting. In livelock, threads are actively moving but in a circle. The most common cause: two threads both implement "if I can't get what I need, release what I have and try again" — but they release and retry at exactly the same moment, perpetually interfering with each other. Distinguishing from deadlock in a thread dump: livelocked threads show RUNNABLE state with high CPU usage.

---

### 🔩 First Principles Explanation

```
Classic livelock: two threads, both polite

Thread A (wants LockX then LockY):
  loop:
    acquire LockX
    try to acquire LockY
    if (can't get LockY):
      release LockX   ← polite: "I'll try again"
      sleep(100ms)
      retry

Thread B (wants LockY then LockX):
  loop:
    acquire LockY
    try to acquire LockX
    if (can't get LockX):
      release LockY   ← polite: "I'll try again"
      sleep(100ms)
      retry

What happens:
  T=0ms:   A acquires LockX,    B acquires LockY
  T=5ms:   A fails LockY,       B fails LockX
  T=5ms:   A releases LockX,    B releases LockY
  T=105ms: A acquires LockX,    B acquires LockY   ← same timing!
  T=110ms: A fails LockY,       B fails LockX
  ... repeat forever ...

CPU: 100% (both threads running)
Progress: 0 (no work ever completes)
```

**Difference from deadlock:**

```
Deadlock:           Livelock:
BLOCKED state       RUNNABLE state
0% CPU              ~100% CPU
Silent hang         Burning CPU, no output
Detected by jstack  jstack shows RUNNABLE but no progress
  "Found deadlock"  No automatic detection
```

---

### ❓ Why Does This Exist — Why Before What

```
Livelock arises from good intentions:
  Retry logic: "if I fail, I'll back off and retry" → can create resonance
  Politeness:  "if we conflict, I'll yield"         → both yield simultaneously

When does it become a problem?
  Both threads use identical retry intervals → always collide
  Symmetric retry logic → mirrors the other's behaviour exactly

Prevention:
  Asymmetric backoff: one thread backs off MORE than the other
  Randomised backoff: random delay breaks the symmetry
  Priority: one thread always has precedence (but risks starvation)
  External lock ordering: prevents the conflict in the first place
```

---

### 🧠 Mental Model / Analogy

> The hallway two-step. Two people approaching each other in a narrow corridor step left simultaneously. They see each other, apologise and step right. Also simultaneously. They step left again. Also simultaneously. Neither makes progress despite being fully "active" and responsive. Fix: one person stops completely and waits while the other passes (asymmetric behaviour breaks the resonance).

---

### ⚙️ How It Works — Detection & Prevention

```
Detection:
  jstack or VisualVM: threads show RUNNABLE state
  High CPU usage with no throughput (metrics show 0 completed tasks)
  Logging shows endless "retry" messages with no success
  ThreadMXBean: NO automatic livelock detection (unlike deadlock)

Prevention strategies:
  1. Randomised exponential backoff:
     Thread.sleep(random.nextInt(100) + delay);
     delay = Math.min(delay * 2, MAX_DELAY);
     → Breaks synchronisation between competing threads

  2. Priority / ordering:
     Always give one thread precedence (Thread.MIN_PRIORITY vs MAX_PRIORITY)
     Or: use global lock ordering (like deadlock prevention)

  3. Avoid symmetric retry:
     Thread A: backs off 50–150ms (random)
     Thread B: backs off 200–400ms (always longer)
     → They will quickly stop colliding
```

---

### 🔄 How It Connects

```
Livelock
  ├─ vs Deadlock   → BLOCKED (deadlock) vs RUNNABLE (livelock)
  ├─ vs Starvation → starvation: one thread never runs; livelock: both run, no progress
  ├─ vs Race Condition → race is wrong output; livelock is no output
  ├─ Caused by     → symmetric retry without randomisation
  └─ Fixed by      → randomised exponential backoff; asymmetric priority
```

---

### 💻 Code Example

```java
// Livelock — symmetric tryLock retry
ReentrantLock lockA = new ReentrantLock();
ReentrantLock lockB = new ReentrantLock();

// Thread A: wants A then B
Runnable taskA = () -> {
    while (true) {
        if (lockA.tryLock()) {
            try {
                Thread.sleep(10);
                if (lockB.tryLock()) {
                    try { doWork(); return; }
                    finally { lockB.unlock(); }
                }
            } catch (InterruptedException ignored) {}
            finally { lockA.unlock(); }
        }
        Thread.sleep(100); // ← both sleep 100ms → always collide!
    }
};

// Thread B: wants B then A — symmetric, same sleep time → LIVELOCK
```

```java
// Fix: randomised backoff breaks the symmetry
Random random = new Random();

Runnable taskA = () -> {
    long backoff = 10;
    while (true) {
        if (lockA.tryLock()) {
            try {
                if (lockB.tryLock()) {
                    try { doWork(); return; }
                    finally { lockB.unlock(); }
                }
            } finally { lockA.unlock(); }
        }
        // ✅ Randomised exponential backoff
        Thread.sleep(backoff + random.nextLong(backoff));
        backoff = Math.min(backoff * 2, 1000);
    }
};
```

---

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| Livelock is easy to detect like deadlock | JVM has no automatic livelock detection; must monitor throughput |
| High CPU means threads are doing work | CPU can be high with zero useful work (livelock spin) |
| Using tryLock prevents all concurrency issues | tryLock prevents deadlock; improper retry creates livelock |
| Adding sleep always fixes livelock | Fixed sleep can still cause livelock if both sleep the same amount |

---

### 🔥 Pitfalls in Production

**Pitfall: Identical retry intervals across distributed services**

```java
// Microservice A and B both retry every 1 second on 503 errors
// A hits B at T=0, gets 503, retries at T=1
// B hits A at T=0, gets 503, retries at T=1
// → Permanent collision — distributed livelock

// Fix: Full Jitter exponential backoff (AWS recommendation)
long delay = (long) (random.nextDouble() * Math.min(CAP, BASE * Math.pow(2, attempt)));
Thread.sleep(delay);
```

---

### 🔗 Related Keywords

- **[Deadlock](./071 — Deadlock.md)** — BLOCKED cousin; detected by JVM
- **[Starvation](./089 — Starvation.md)** — threads don't get CPU; vs livelock (they do get CPU, no progress)
- **[ReentrantLock](./076 — ReentrantLock.md)** — tryLock is the mechanism that creates livelock risk

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Threads RUNNABLE with high CPU but zero       │
│              │ progress — symmetric retry creates resonance  │
├──────────────┼───────────────────────────────────────────────┤
│ USE WHEN     │ Debugging: high CPU + zero throughput + many  │
│              │ "retry" log messages → suspect livelock       │
├──────────────┼───────────────────────────────────────────────┤
│ AVOID WHEN   │ Prevent: randomise retry backoff; use global  │
│              │ lock ordering; add asymmetric retry delays    │
├──────────────┼───────────────────────────────────────────────┤
│ ONE-LINER    │ "Both threads active, both yielding, both     │
│              │  trying — neither ever gets through"          │
├──────────────┼───────────────────────────────────────────────┤
│ NEXT EXPLORE │ Deadlock → Starvation → Exponential Backoff → │
│              │ Jitter → tryLock patterns                    │
└──────────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** How would you distinguish livelock from a genuine performance issue (slow computation) in a production system? What metrics and tools would you use?

**Q2.** Distributed systems (HTTP microservices) can exhibit livelock. Two services retry failed calls on each other at fixed intervals. What technique does AWS recommend to prevent this? How does "full jitter" differ from "equal jitter"?

**Q3.** Could livelock occur with `synchronized` blocks (not tryLock)? Why or why not? Under what mechanism would threads livelock without any explicit retry logic?

