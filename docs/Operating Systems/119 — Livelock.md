---
layout: default
title: "Livelock"
parent: "Operating Systems"
nav_order: 119
permalink: /operating-systems/livelock/
number: "0119"
category: Operating Systems
difficulty: ★★★
depends_on: Deadlock, Mutex, Thread
used_by: Retry Logic, Network Backoff, Lock-Free Algorithms
related: Deadlock, Starvation, Backoff Strategy, CAS Loop
tags:
  - os
  - concurrency
  - synchronization
  - edge-cases
---

# 119 — Livelock

⚡ TL;DR — Livelock is when threads are active (not blocked) but repeatedly cancel each other's progress — like two people in a hallway endlessly mirroring each other's sidestep.

| #0119           | Category: Operating Systems                        | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------- | :-------------- |
| **Depends on:** | Deadlock, Mutex, Thread                            |                 |
| **Used by:**    | Retry Logic, Network Backoff, Lock-Free Algorithms |                 |
| **Related:**    | Deadlock, Starvation, Backoff Strategy, CAS Loop   |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You implement a deadlock avoidance strategy: if Thread A can't acquire Lock B, it releases Lock A and retries. Thread B does the same — releases Lock B if it can't get Lock A. This prevents deadlock (Coffman condition 2 broken). But under certain timing conditions, both threads continuously acquire their first lock, detect the other is held, release, then retry — in perfect synchronisation. They're both active but neither ever holds both locks simultaneously.

**THE BREAKING POINT:**
The retry logic that prevents deadlock can introduce livelock if both threads react to each other's presence symmetrically and at the same rate. CPU spikes to 100% for both threads. No exception, no blocked state, no progress. From the OS perspective, both threads are RUNNABLE and consuming CPU — making it harder to diagnose than deadlock.

**THE INVENTION MOMENT:**
The solution (randomised exponential backoff) was formalised for network protocols in Ethernet's CSMA/CD (1976): when two stations detect a collision, each waits a random period before retrying. The randomisation breaks symmetry — both stations are unlikely to retry at exactly the same time. The same principle applies to lock retry loops.

---

### 📘 Textbook Definition

**Livelock** is a concurrency failure mode in which two or more threads repeatedly change their state in response to each other without making forward progress. Unlike deadlock (where threads are blocked and not executing), in livelock threads are continuously executing — they consume CPU cycles — but their combined state oscillates rather than converging to completion. Livelock typically arises in deadlock-avoidance mechanisms (retry-on-failure) when multiple threads react to each other's presence with identical, symmetric responses and identical timing.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Livelock = busy but stuck; threads keep reacting to each other, burning CPU, and making no progress.

**One analogy:**

> Two people walking toward each other in a narrow corridor. Person A steps left to let B pass. Person B also steps left. They're face to face again. Both step right. Again face to face. Neither is frozen (not deadlock) — both are actively moving — but neither gets past. Randomise the direction and they'll eventually pass.

**One insight:**
Livelock is harder to diagnose than deadlock: threads are RUNNABLE in the OS scheduler (not BLOCKED), so thread dumps don't reveal a clear "waiting for" relationship. You see CPU at 100% with zero progress — which looks like an infinite loop, not a concurrency bug.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Threads are executing (not sleeping/blocked).
2. Each thread's actions cause the other to undo theirs.
3. The combined state cycles — no terminal condition is ever reached.
4. Typically requires symmetric response with identical timing.

**DERIVED DESIGN:**
**Minimal livelock example:**

```
Thread A:                     Thread B:
acquire(lockA)                acquire(lockB)
  tryAcquire(lockB) → fail      tryAcquire(lockA) → fail
  release(lockA)                release(lockB)
  [retry]                       [retry]
```

If both threads always retry at the same interval, they always collide:

```
t=0: A acquires lockA; B acquires lockB
t=1: A tries lockB (fail); B tries lockA (fail)
t=2: A releases lockA; B releases lockB
t=3: A acquires lockA; B acquires lockB  [cycle repeats]
```

FIX — randomised backoff:

```
t=0: A acquires lockA; B acquires lockB
t=1: A tries lockB (fail); B tries lockA (fail)
t=2: A releases lockA, sleeps 17ms; B releases lockB, sleeps 3ms
t=5: B acquires lockB, acquires lockA (free!) → proceeds
t=22: A retries → acquires lockA, lockB → proceeds
```

Randomisation breaks symmetry → threads proceed at different times.

**THE TRADE-OFFS:**
**Gain:** Avoids deadlock without risk of livelock (with proper backoff).
**Cost:** Randomised backoff adds latency; must tune range (too short: livelock persists; too long: unnecessary delay).

---

### 🧪 Thought Experiment

**SETUP:**
Two database clients both implementing "optimistic retry on deadlock". Both update rows in different order. The database detects deadlock and rolls back one. The rolled-back client immediately retries. They immediately deadlock again. The database rolls back the other. It immediately retries. They deadlock again.

SYMPTOMS:

```
Client A: 100% CPU
Client B: 100% CPU
Database: deadlock detection runs continuously at 100% CPU
Transaction committed: 0
```

This is a livelock between clients at the application level, even though each individual deadlock is resolved by the database.

FIX (exponential backoff with jitter):

```python
import random, time

def retry_with_backoff(operation, max_retries=5):
    for attempt in range(max_retries):
        try:
            return operation()
        except DeadlockError:
            if attempt == max_retries - 1:
                raise
            sleep_time = (2 ** attempt * 0.1) + random.uniform(0, 0.1)
            time.sleep(sleep_time)  # 100ms + jitter, 200ms + jitter, ...
```

**THE INSIGHT:**
The randomisation ("jitter") is the critical ingredient. Without jitter, both clients apply the same backoff (e.g., sleep 100ms) and collide again at t=100ms.

---

### 🧠 Mental Model / Analogy

> Two robots cleaning a floor with sensors: if they detect another robot approaching, they back up one step and try a different direction. Both robots are always moving — fully operational. But their identical sensor response logic means they mirror each other's movements: any path Robot A tries, Robot B also backs away from, clearing that path, then resetting to a blocking position. The floor never gets cleaned.

> Fix: randomise the "backing away" direction. Eventually one robot gets to a position the other doesn't immediately mirror, and they diverge.

Where the analogy breaks down: livelock in software can involve more than two parties and can manifest across distributed systems (microservice retry storms). The "corridor symmetry" intuition scales but the diagnosis is harder.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Livelock is when threads are active and running but never make progress — each thread's actions cause the others to undo theirs. Like two people at a door who each keep holding it open for the other and neither walks through.

**Level 2 — How to use it (junior developer):**
Use exponential backoff with random jitter in any retry loop: `sleep = base * 2^attempt + random(0..base)`. This is the standard for database deadlock retries, network connection retries (TCP, HTTP), and lock acquisition retries. Avoid fixed-interval retries in shared concurrent systems. AWS, Google Cloud, and all distributed system clients use jitter in their retry logic for exactly this reason.

**Level 3 — How it works (mid-level engineer):**
Livelock can occur in CAS-based lock-free data structures under high contention. A CAS loop: read value → compute new value → CAS (if fails, retry). If two threads repeatedly fail CAS on the same variable, both retrying at the same rate, their retry cycles can align. The CAS loop itself is a potential livelock source: both threads read the same value, compute, both CAS fail, both re-read... Under low contention this rarely aligns. Under very high contention with identical timing (tight CPU loops), it can. Fix: add `Thread.onSpinWait()` (emits PAUSE instruction) or a brief randomised sleep after failure.

**Level 4 — Why it was designed this way (senior/staff):**
The Ethernet CSMA/CD backoff used a binary exponential backoff: on the first collision, wait 0 or 1 slot times (random). On the second, 0–3 slots. On the kth: 0 to 2^min(k,10)–1 slots. The ceiling at 10 prevents infinite backoff (avoids starvation). The exponential growth ensures that at high load, different stations are unlikely to collide again. This algorithm (802.3 section 4.2.3.2) was derived from the ALOHA protocol (1970) analysis showing that pure random backoff achieves 37% channel efficiency, while CSMA/CD achieves 90%+ at low load. The same mathematical principle — variance in retry timing → reduced collision probability — applies directly to software livelock prevention.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│              LIVELOCK TIMELINE                         │
├────────────────────────────────────────────────────────┤
│  Thread A              Thread B              Lock State │
│  ──────────────────────────────────────────────────    │
│  acquire(A) ────────────────────────────── A=A, B=free │
│                        acquire(B) ──────── A=A, B=B    │
│  tryAcquire(B) fail ─────────────────────── A=A, B=B  │
│                        tryAcquire(A) fail ── A=A, B=B  │
│  release(A) ──────────────────────────────── A=free   │
│                        release(B) ──────── both free   │
│  acquire(A) ───────────────────────────── A=A          │
│                        acquire(B) ──────── A=A, B=B    │
│  [CYCLE REPEATS INDEFINITELY]                          │
│                                                        │
│  With randomised backoff (A sleeps 23ms, B sleeps 7ms):│
│  t=0: same as above through first release              │
│  t+7ms: B acquires B, then A (free) → completes ✓     │
│  t+23ms: A acquires A, then B (now free) → completes ✓ │
└────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

REAL-WORLD RETRY STORM (microservices livelock):

```
Service A (auth): rate-limited at 500ms → retry
Service B (product): dependent on auth → also waits
Service C (order): depends on product → also waits
All services retry simultaneously every 500ms
→ Every 500ms: all services hammer auth → rate limit hit
→ Rate limit hit → all services retry after 500ms (uniform)
→ Next 500ms: same storm
→ Auth never gets below rate limit
→ All services: healthy (RUNNABLE), zero progress

FIX: Add jitter to each service's backoff
Service A: 500ms + rand(0–100ms) = 537ms
Service B: 500ms + rand(0–100ms) = 512ms
Service C: 500ms + rand(0–100ms) = 589ms
→ Services retry at different times → auth load spreads
→ Auth serves retries without hitting rate limit
→ System recovers
```

---

### 💻 Code Example

Example 1 — Livelock with uniform retry:

```java
// LIVELOCK PRONE: uniform retry interval
void transferLivelock(Account a, Account b) {
    while (true) {
        if (a.lock.tryLock()) {
            try {
                if (b.lock.tryLock()) {
                    try {
                        // Critical section
                        return;
                    } finally { b.lock.unlock(); }
                }
            } finally { a.lock.unlock(); }
        }
        Thread.sleep(100);  // FIXED interval — both retry together!
    }
}
```

Example 2 — Exponential backoff with jitter (fix):

```java
// LIVELOCK SAFE: exponential backoff + jitter
void transferSafe(Account a, Account b, double amount)
        throws InterruptedException {
    Random rand = ThreadLocalRandom.current();
    int attempt = 0;
    while (true) {
        if (a.lock.tryLock(10, MILLISECONDS)) {
            try {
                if (b.lock.tryLock(10, MILLISECONDS)) {
                    try {
                        a.balance -= amount;
                        b.balance += amount;
                        return;  // success
                    } finally { b.lock.unlock(); }
                }
            } finally { a.lock.unlock(); }
        }
        // Exponential backoff with jitter
        long backoffMs = (long) Math.pow(2, Math.min(attempt++, 6));
        long jitter = (long)(rand.nextDouble() * backoffMs);
        Thread.sleep(backoffMs + jitter);  // 1–2ms, 2–4ms, 4–8ms...
    }
}
```

Example 3 — Database retry with jitter (Spring/Java):

```java
@Service
public class OrderService {
    private static final int MAX_RETRIES = 5;

    @Transactional
    public void processOrder(Order order) {
        // Called internally with retry logic below
        doProcessOrder(order);
    }

    public void processOrderWithRetry(Order order) {
        for (int attempt = 0; attempt < MAX_RETRIES; attempt++) {
            try {
                processOrder(order);
                return;  // success
            } catch (DeadlockLoserDataAccessException e) {
                if (attempt == MAX_RETRIES - 1) throw e;
                long backoff = (long) Math.pow(2, attempt) * 50  // 50,100,200ms
                             + ThreadLocalRandom.current().nextLong(50);
                log.warn("Deadlock on attempt {}; backoff={}ms", attempt, backoff);
                try { Thread.sleep(backoff); }
                catch (InterruptedException ie) { Thread.currentThread().interrupt(); }
            }
        }
    }
}
```

---

### ⚖️ Comparison Table

| Condition          | Threads Running? | CPU Used?  | Detectable by jstack?                 | Fix                        |
| ------------------ | ---------------- | ---------- | ------------------------------------- | -------------------------- |
| **Deadlock**       | No (BLOCKED)     | No         | Yes ("Found one Java-level deadlock") | Lock ordering, tryLock     |
| **Livelock**       | Yes (RUNNABLE)   | Yes (100%) | No                                    | Randomised backoff, jitter |
| **Starvation**     | Mixed            | Varies     | Partial (threads waiting)             | Fair locks, priority       |
| **Race Condition** | Yes              | Varies     | No                                    | Synchronization            |

---

### ⚠️ Common Misconceptions

| Misconception                               | Reality                                                                                                         |
| ------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| "Livelock is a type of deadlock"            | No — deadlock = blocked threads; livelock = running threads; opposite symptoms                                  |
| "100% CPU with no progress = infinite loop" | Could be livelock (two threads) or a spin loop; check thread interaction                                        |
| "tryLock prevents livelock"                 | tryLock prevents deadlock; without backoff, it CAUSES livelock                                                  |
| "Livelock only happens with locks"          | Also in message-based systems (request-reject-retry cycles), network protocols (collision retry), and CAS loops |

---

### 🚨 Failure Modes & Diagnosis

**1. Livelock in Microservice Retry Storm**

**Symptom:** All services show high CPU; zero successful transactions; each service's metrics show high retry rate; downstream service (auth, database) sees request flood at regular intervals.

**Root Cause:** All services retry with fixed intervals aligned to same period; each retry wave saturates the downstream service which rejects, causing another retry wave.

**Diagnostic:**

```bash
# Check retry pattern timing
grep "retry" service.log | awk '{print $1}' | uniq -c
# If retries cluster at same seconds → uniform backoff → potential livelock

# Monitor downstream service RPS
curl http://service/metrics | grep http_request_rate
# Spike every N seconds = uniform retry pattern
```

**Fix:** Add full jitter: `sleep = random(0, base * 2^attempt)` (AWS recommendation).

**Prevention:** Use circuit breaker with randomised reset time; separate retry timing per instance.

---

**2. CAS Livelock in Lock-Free Structure**

**Symptom:** Lock-free queue shows 100% CPU on multiple threads, near-zero throughput under high contention.

**Root Cause:** All threads CAS-fail simultaneously, all immediately retry, all fail again.

**Diagnostic:**

```bash
perf stat -e instructions,cpu-cycles,cache-misses ./benchmark
# Extremely high cycles/instruction ratio (> 10) = lots of retries
# Low cache-misses but high cycles = CAS contention not cache misses
```

**Fix:** Add `Thread.onSpinWait()` after CAS failure; or add small random sleep; or switch to a lock-based implementation under extreme contention.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Deadlock` — livelock is the dynamic counterpart of deadlock; understand deadlock first
- `Mutex` — livelock arises in lock-release-retry patterns
- `Thread` — requires multiple threads reacting to each other

**Builds On This (learn these next):**

- `Starvation` — a thread that is perpetually passed over, related but distinct from livelock
- `Exponential Backoff` — the standard fix for livelock in retry-based systems
- `Circuit Breaker Pattern` — prevents retry storms in microservices

**Alternatives / Comparisons:**

- `Deadlock` — both are progress failures; deadlock: blocked, no CPU; livelock: running, CPU consumed
- `Starvation` — indefinite postponement without a cycle; one thread is perpetually bypassed
- `Thundering Herd` — many threads wake simultaneously and compete; similar to livelock in effect but different cause

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Threads active (not blocked) but making  │
│              │ no progress — reacting to each other     │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Retry logic that prevents deadlock can   │
│ SOLVES       │ cause livelock with uniform timing        │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Randomised jitter breaks symmetry;       │
│              │ threads retry at different times          │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Diagnosing 100% CPU with no progress;    │
│              │ designing retry logic for concurrent code │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ "Avoid" = add jitter to all retry loops; │
│              │ never use fixed retry intervals under load│
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Deadlock prevention (retry) vs livelock  │
│              │ risk (without jitter)                     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Both active, zero progress — randomise  │
│              │  retry timing to break the cycle"        │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Starvation → Circuit Breaker → Backoff    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** AWS's retry recommendations include "full jitter" (`sleep = random(0, cap * 2^attempt)`) vs "equal jitter" (`sleep = cap/2 + random(0, cap/2)`). Equal jitter prevents very short retries (ensuring some minimum backoff) while full jitter allows near-zero sleeps. For a system with 1000 clients all simultaneously hitting a rate limit: at what load does equal jitter outperform full jitter (fewer total retries before success), and at what load does full jitter win? Derive the answer by modeling the expected number of collisions per retry round as a function of client count and jitter strategy.

**Q2.** The `ConcurrentLinkedQueue` (Java) uses a lock-free algorithm based on Michael-Scott queue (1996) with CAS operations. The offer() method's CAS loop is theoretically livelock-free because CAS makes at least one thread progress on each "round" (at least one CAS succeeds). However, under extreme contention (1000 threads all calling offer() simultaneously), the constant CAS failures cause a different problem. Describe what "obstruction-free" vs "lock-free" vs "wait-free" means in this context, identify which guarantee Michael-Scott queue provides, and explain why even lock-free algorithms can exhibit livelock-like throughput collapse under extreme contention.
