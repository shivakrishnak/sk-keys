---
layout: default
title: "Deadlock"
parent: "Java Concurrency"
nav_order: 368
permalink: /java-concurrency/deadlock/
---
# 368 — Deadlock

`#java` `#concurrency` `#threading` `#locks` `#diagnosis`

⚡ TL;DR — Deadlock occurs when two or more threads permanently block each other, each holding a lock the other needs — diagnosed via thread dumps (jstack) and prevented by consistent lock ordering or tryLock with timeout.

| #368 | category: Java Concurrency
|:---|:---|:---|
| **Depends on:** | Thread, synchronized, Thread Lifecycle, ReentrantLock | |
| **Used by:** | Lock Ordering, tryLock, Deadlock Detection, jstack | |

---

### 📘 Textbook Definition

A **deadlock** is a condition where two or more threads are permanently blocked, each waiting for a resource (typically a lock) held by another thread in the cycle. Java deadlocks require four **Coffman conditions** to hold simultaneously: (1) mutual exclusion — resources are non-shareable; (2) hold and wait — threads hold resources while requesting more; (3) no preemption — resources cannot be forcibly taken; (4) circular wait — a circular chain of threads each waiting on the next. Deadlocks never self-resolve — the threads remain BLOCKED forever.

---

### 🟢 Simple Definition (Easy)

Thread A has key 1 and needs key 2. Thread B has key 2 and needs key 1. Both wait forever — neither will release what they have until they get what they need. Nobody moves. That's a deadlock.

---

### 🔵 Simple Definition (Elaborated)

Deadlocks are the classic concurrency trap. They're invisible during normal operation and only manifest at runtime under specific timing. Once deadlocked, the affected threads are stuck permanently in BLOCKED state — they don't crash, they don't log errors, they just stop making progress. The application appears to hang. In production, you detect them via thread dumps (`jstack`, `jcmd`, or VisualVM), which show the circular wait chain explicitly.

---

### 🔩 First Principles Explanation

**The four Coffman conditions (ALL must hold for deadlock):**

```
1. MUTUAL EXCLUSION
   A resource (lock) can only be held by one thread at a time
   → Java synchronized / ReentrantLock is non-shareable

2. HOLD AND WAIT
   A thread holds one lock and waits for another
   → Thread A holds lock1, blocked waiting for lock2
   → Thread B holds lock2, blocked waiting for lock1

3. NO PREEMPTION
   Locks cannot be forcibly taken — a thread must voluntarily release
   → JVM cannot steal a monitor from a thread

4. CIRCULAR WAIT
   A cycle exists: A waits for B, B waits for A
   (or A→B→C→A in multi-thread deadlocks)
```

**Minimal deadlock example:**

```
Lock1 = new Object()
Lock2 = new Object()

Thread A:
  synchronized(Lock1) {        // acquires Lock1
      synchronized(Lock2) {    // BLOCKS — Lock2 held by B
      }
  }

Thread B:
  synchronized(Lock2) {        // acquires Lock2
      synchronized(Lock1) {    // BLOCKS — Lock1 held by A
      }
  }

STATE:
  Thread A: BLOCKED (waiting for Lock2)  ←────┐
  Thread B: BLOCKED (waiting for Lock1)  ──────┘
  Circular wait → neither ever continues
```

---

### ❓ Why Does This Exist — Why Before What

```
Deadlock is an emergent property of correct-looking code:

  transferMoney(account1, account2, amount):
    synchronized(account1) {
      synchronized(account2) { ... }  // seems fine
    }

  Thread 1: transfer(acc1, acc2)  → locks acc1, waits for acc2
  Thread 2: transfer(acc2, acc1)  → locks acc2, waits for acc1
  → Deadlock at runtime under concurrent load

Why it's hard to prevent:
  ✗ No compile-time detection — code looks correct
  ✗ Only manifests under specific thread interleaving
  ✗ Timing-dependent — works in test, deadlocks in production
  ✗ Silent — no exception, no log, just a hung application

Why understanding it matters:
  ✅ Lock ordering eliminates circular wait condition
  ✅ tryLock breaks hold-and-wait
  ✅ jstack identifies deadlock within seconds
  ✅ Thread.holdsLock() enables defensive assertions
```

---

### 🧠 Mental Model / Analogy

> Two neighbours each borrow one of the other's tools. Neighbour A has the ladder and needs the drill. Neighbour B has the drill and needs the ladder. Neither will lend what they have until they get what they need. Both stand in their driveways forever. Classic deadlock — the only solution is for one to give up their tool without getting the other first.

---

### ⚙️ How It Works

```
Deadlock detection in JVM:
  ThreadMXBean.findDeadlockedThreads() → returns IDs of deadlocked threads
  jstack <pid>                         → prints all thread states + deadlock report
  jcmd <pid> Thread.print              → same as jstack

jstack output for a deadlock:
  Found one Java-level deadlock:
  =============================
  "Thread-A":
    waiting to lock monitor 0x... (object Lock2)
    which is held by "Thread-B"
  "Thread-B":
    waiting to lock monitor 0x... (object Lock1)
    which is held by "Thread-A"

  Java stack information for the threads listed above:
  "Thread-A":
    at DeadlockDemo.methodA(DeadlockDemo.java:12)
    - waiting to lock <0x...> (Lock2)
    - locked <0x...> (Lock1)
```

---

### 🔄 How It Connects

```
Deadlock
  │
  ├─ Caused by ──→ Circular lock acquisition order
  ├─ Detected  ──→ jstack / jcmd / ThreadMXBean / VisualVM
  ├─ Prevented ──→ Consistent lock ordering (global lock order)
  ├─ Broken    ──→ tryLock(timeout) — give up rather than wait forever
  ├─ Designed away → single lock per operation; lock-free structures
  │
  └─ Related bugs:
      Livelock   — threads active but making no progress (retry loops)
      Starvation — thread never gets CPU/lock due to priority/fairness
```

---

### 💻 Code Example

```java
// Classic deadlock
public class DeadlockDemo {
    private static final Object LOCK_A = new Object();
    private static final Object LOCK_B = new Object();

    public static void main(String[] args) throws InterruptedException {
        Thread t1 = new Thread(() -> {
            synchronized (LOCK_A) {
                System.out.println("T1 acquired A");
                try { Thread.sleep(50); } catch (InterruptedException ignored) {}
                synchronized (LOCK_B) {   // ← BLOCKS: T2 holds B
                    System.out.println("T1 acquired B");
                }
            }
        }, "Thread-T1");

        Thread t2 = new Thread(() -> {
            synchronized (LOCK_B) {
                System.out.println("T2 acquired B");
                try { Thread.sleep(50); } catch (InterruptedException ignored) {}
                synchronized (LOCK_A) {   // ← BLOCKS: T1 holds A
                    System.out.println("T2 acquired A");
                }
            }
        }, "Thread-T2");

        t1.start();
        t2.start();
        // Program hangs — both threads BLOCKED forever
    }
}
```

```java
// Prevention 1: consistent lock ordering
// Always acquire locks in the SAME ORDER regardless of which thread

public void transfer(Account from, Account to, double amount) {
    // Order locks by account ID — always smaller ID first
    Account first  = from.getId() < to.getId() ? from : to;
    Account second = from.getId() < to.getId() ? to   : from;

    synchronized (first) {
        synchronized (second) {
            from.debit(amount);
            to.credit(amount);
        }
    }
    // Both threads always acquire locks in same order → no circular wait
}
```

```java
// Prevention 2: tryLock with timeout (ReentrantLock)
ReentrantLock lockA = new ReentrantLock();
ReentrantLock lockB = new ReentrantLock();

public boolean doWork() throws InterruptedException {
    if (lockA.tryLock(100, TimeUnit.MILLISECONDS)) {
        try {
            if (lockB.tryLock(100, TimeUnit.MILLISECONDS)) {
                try {
                    performWork();
                    return true;
                } finally {
                    lockB.unlock();
                }
            }
        } finally {
            lockA.unlock();
        }
    }
    return false; // failed to acquire both — caller can retry with backoff
}
```

```java
// Detection at runtime
ThreadMXBean bean = ManagementFactory.getThreadMXBean();
long[] deadlockedIds = bean.findDeadlockedThreads();
if (deadlockedIds != null) {
    ThreadInfo[] infos = bean.getThreadInfo(deadlockedIds, true, true);
    for (ThreadInfo info : infos) {
        System.out.println("Deadlocked: " + info.getThreadName());
        System.out.println("Waiting for: " + info.getLockName());
        System.out.println("Held by: " + info.getLockOwnerName());
    }
}
```

---

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| Deadlock throws an exception | Threads silently BLOCK forever — no exception, no error |
| Deadlock only happens with 2 threads | Can involve 3+ threads in a cycle: A→B→C→A |
| synchronized can't deadlock if used carefully | Any nested lock acquisition can deadlock if ordering is inconsistent |
| JVM automatically resolves deadlocks | JVM only detects, never resolves — you must redesign the locking |
| More threads → more deadlocks | Deadlock requires the circular wait; number of threads isn't the root cause |

---

### 🔥 Pitfalls in Production

**Pitfall 1: Acquiring locks in different orders in different methods**

```java
// Method A: Lock1 then Lock2
// Method B: Lock2 then Lock1
// Called concurrently → deadlock

// Fix: establish a global lock acquisition order and document it
// Use object identity (System.identityHashCode) as a consistent order
```

**Pitfall 2: Calling external / unknown code while holding a lock**

```java
synchronized (this) {
    // 'listener' is external — could try to acquire our lock!
    listener.onEvent(event);   // ← potential deadlock if listener synchronizes on same object
}

// Fix: copy reference and notify outside lock (open call)
EventListener local;
synchronized (this) { local = this.listener; }
local.onEvent(event);  // called without holding lock — safe
```

**Pitfall 3: Database deadlocks (not just Java)**

```
Transaction A: UPDATE table1 WHERE id=1, then UPDATE table2 WHERE id=2
Transaction B: UPDATE table2 WHERE id=2, then UPDATE table1 WHERE id=1
→ Database-level deadlock — DB detects and rolls back one victim
→ Application must retry on deadlock exception (SQLException state 40001)
```

---

### 🔗 Related Keywords

- **[synchronized](./069 — synchronized.md)** — the mechanism deadlocks occur in
- **[Thread Lifecycle](./068 — Thread Lifecycle.md)** — deadlocked threads are in BLOCKED state
- **[ReentrantLock](./076 — ReentrantLock.md)** — tryLock to avoid blocking forever
- **[Race Condition](./072 — Race Condition.md)** — the other major threading hazard
- **jstack** — diagnose deadlocks instantly with a thread dump

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Circular lock wait — each thread holds what   │
│              │ the other needs; both BLOCKED forever         │
├──────────────┼───────────────────────────────────────────────┤
│ USE WHEN     │ Diagnosing hung applications: run jstack,     │
│              │ look for "Found one Java-level deadlock"      │
├──────────────┼───────────────────────────────────────────────┤
│ AVOID WHEN   │ Prevent via: consistent lock ordering, single │
│              │ lock per operation, tryLock with timeout,     │
│              │ lock-free data structures (ConcurrentHashMap) │
├──────────────┼───────────────────────────────────────────────┤
│ ONE-LINER    │ "Each thread holds what the other needs —     │
│              │  nobody moves, nobody ever will"              │
├──────────────┼───────────────────────────────────────────────┤
│ NEXT EXPLORE │ ReentrantLock → tryLock → Lock Ordering →     │
│              │ ThreadMXBean → Livelock → Starvation          │
└──────────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** `tryLock(timeout)` avoids deadlock but introduces **livelock** risk — both threads keep retrying and backing off, never succeeding. How would you design the retry strategy to prevent livelock (hint: think about randomised backoff)?

**Q2.** A deadlock involves three threads: A waits for B, B waits for C, C waits for A. Draw the wait-for graph. How does `jstack` represent this? How does `ThreadMXBean.findDeadlockedThreads()` detect the cycle?

**Q3.** In a database context, deadlocks are automatically resolved by rolling back one transaction. Why can't the JVM do the same for thread deadlocks? What would be required to support automatic deadlock resolution at the JVM level?

