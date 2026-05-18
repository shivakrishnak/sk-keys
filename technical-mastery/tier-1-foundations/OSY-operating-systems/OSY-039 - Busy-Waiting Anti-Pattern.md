---
id: OSY-039
title: Busy-Waiting Anti-Pattern
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★☆
depends_on: OSY-009, OSY-017, OSY-029
used_by: OSY-042
related: OSY-009, OSY-025, OSY-056
tags:
  - anti-pattern
  - busy-waiting
  - spin-wait
  - cpu-waste
  - condition-variables
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 39
permalink: /technical-mastery/osy/busy-waiting-anti-pattern/
---

## TL;DR

Busy-waiting (spin-wait): a thread loops checking a
condition instead of sleeping. It wastes 100% of a CPU
core while accomplishing no work. Fix: use
OS-level sleep, condition variables, or blocking I/O
that yields the CPU. Spinlocks are the legitimate
exception in kernel code (< 1 microsecond critical
sections).

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-039 |
| **Difficulty** | ★★☆ Working |
| **Category** | Operating Systems |
| **Tags** | busy-waiting, spin-wait, anti-pattern, CPU waste |
| **Prerequisites** | OSY-009, OSY-017, OSY-029 |

---

### The Anti-Pattern

```java
// BAD: Busy-waiting on a queue
// This thread uses 100% CPU doing nothing useful
public class BusyConsumer {
    private final Queue<Task> queue;
    
    public void run() {
        while (true) {
            Task task = queue.poll();  // returns null if empty
            if (task != null) {
                process(task);
            }
            // If queue empty: loops back immediately
            // CPU: 100% on this loop
            // OS sees: RUNNABLE thread, doesn't know it's idle
            // Other threads get less CPU time
            // Battery drain on laptops/mobile
        }
    }
}
```

```bash
# Diagnosis: busy-waiting thread visible in top
top
# Thread shows: %CPU = 100, state = R (running)
# Even though doing no real work

# Compare to properly blocking thread:
# state = S (sleeping), %CPU ~= 0
```

---

### Fixes

```java
// FIX 1: BlockingQueue (park thread when empty)
public class BlockingConsumer {
    private final BlockingQueue<Task> queue;
    
    public void run() {
        while (true) {
            try {
                // take() parks thread if queue empty
                // OS wakes thread when item is added
                Task task = queue.take();  // BLOCKING
                process(task);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }
    }
}
// CPU: ~0% when queue empty
// Latency: negligible - OS schedules immediately on item add

// FIX 2: Condition variable wait
public class ConditionConsumer {
    private final Queue<Task> queue = new LinkedList<>();
    private final Lock lock = new ReentrantLock();
    private final Condition notEmpty = lock.newCondition();
    
    public void produce(Task task) {
        lock.lock();
        try {
            queue.add(task);
            notEmpty.signal();  // wake waiting consumer
        } finally {
            lock.unlock();
        }
    }
    
    public void consume() throws InterruptedException {
        lock.lock();
        try {
            while (queue.isEmpty()) {
                notEmpty.await();  // SLEEP: releases lock, parks
            }
            process(queue.poll());
        } finally {
            lock.unlock();
        }
    }
}

// FIX 3: Thread.sleep() with backoff (approximate)
// Useful when you can't use blocking APIs
public class PollingConsumer {
    public void run() throws InterruptedException {
        long sleepMs = 10;
        while (true) {
            Task task = queue.poll();
            if (task != null) {
                process(task);
                sleepMs = 10;  // reset backoff after work
            } else {
                Thread.sleep(sleepMs);    // yield CPU
                sleepMs = Math.min(sleepMs * 2, 1000); // backoff
            }
        }
    }
}
// Trade-off: latency increases (sleep delay), but CPU usage normal
```

---

### When Spinlocks ARE Appropriate

```java
// Spinlocks are legitimate in kernel code and some JVM internals:
// - Critical section < ~1 microsecond (faster than context switch)
// - Only one or two iterations expected before success
// - Cannot use OS sleep (interrupt context, atomic sections)

// Example of appropriate spin (Java, lock-free CAS):
// AtomicInteger.compareAndSet() may spin briefly internally:
//   while (!compareAndSet(expected, update)) {
//       expected = get();  // spin a few times, then yield
//   }

// java.util.concurrent uses hybrid approach:
// - Spin a few times (for short holds)
// - Then park (block) if still not available
// This is the "adaptive spin" in HotSpot JVM monitors

// Rule: spin < 1 microsecond (kernel spinlocks, CAS loops)
//        sleep > 1 microsecond (application-level waiting)
```

---

### Comparison Table

| Approach | CPU When Idle | Latency | Use Case |
|----------|--------------|---------|---------|
| Busy-wait | 100% | Minimal | NEVER in user space |
| Thread.sleep(fixed) | ~0% | Up to sleep ms | Simple polling with tolerance |
| sleep + backoff | ~0% | Up to max sleep | Polling without backoff overhead |
| BlockingQueue.take() | ~0% | ~0.1ms wake delay | Standard producer-consumer |
| Condition.await() | ~0% | ~0.1ms wake delay | Custom conditions |
| Spinlock (kernel) | 100% (brief) | <1 microsecond | Kernel critical sections only |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Thread.sleep(0) is the same as yield()" | Thread.sleep(0) hints the OS to reschedule but does NOT guarantee yielding. Thread.yield() is a scheduling hint but also not guaranteed. Neither reliably releases the CPU for a specific duration. Use sleep with positive ms for real delay |
| "Busy-waiting is acceptable for short waits" | "Short wait" in user space is relative. Even 10 microseconds of busy-wait on a server with 100 threads wastes 10% of a CPU core continuously. In production with many threads, this cascades into poor throughput and unfair CPU distribution |

---

### Failure Modes

```
Symptom: One CPU core at 100%, application throughput low
  Other threads get CPU-starved by busy-wait thread
Diagnosis: top -H -p PID shows one thread at 100% CPU
  when it should be idle; jstack shows it in a loop
Fix: Replace polling loop with BlockingQueue or Condition

Symptom: Docker container uses near 100% CPU limit even at idle
  Pod gets throttled; latency spikes due to CPU throttling
Diagnosis: container CPU usage never drops to 0 even with 0 load
  strace shows: sched_yield, nanosleep in rapid succession
Fix: Identify the busy-wait thread; replace with blocking wait
```

---

### Quick Reference Card

| Pattern | Problem | Fix |
|---------|---------|-----|
| `while (queue.isEmpty()) {}` | 100% CPU, starves other threads | BlockingQueue.take() |
| `while (!flag) { Thread.yield(); }` | High CPU, non-deterministic | volatile flag + LockSupport.park() |
| `while (result == null) { Thread.sleep(1); }` | Latency spikes on sleep interval | CompletableFuture or blocking API |
| `while (!lock.tryLock()) {}` | CPU waste on contention | lock.lock() (blocking) |
