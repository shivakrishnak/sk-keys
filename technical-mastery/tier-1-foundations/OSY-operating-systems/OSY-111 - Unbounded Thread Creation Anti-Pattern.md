---
id: OSY-111
title: Unbounded Thread Creation Anti-Pattern
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-022, OSY-085, OSY-099, OSY-109
used_by: []
related: OSY-109, OSY-110, OSY-112
tags:
  - anti-pattern
  - thread-creation
  - unbounded
  - OOM
  - production
  - Java
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 111
permalink: /technical-mastery/osy/unbounded-thread-creation/
---

## TL;DR

Unbounded thread creation - creating a new OS thread for every
task without limits - causes gradual memory exhaustion and
eventual OOM kill. Each OS thread uses 512KB-2MB of native
stack memory. 10,000 threads = 5-20GB of native memory.
Symptoms: RSS grows linearly with load; OutOfMemoryError:
"unable to create native thread". Fix: bounded thread pool,
async I/O, or virtual threads (Java 21).

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-111 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | unbounded threads, thread creation, OOM, native memory, anti-pattern |
| **Prerequisites** | OSY-022, OSY-085, OSY-099, OSY-109 |

---

### The Anti-Pattern

```java
// BAD: new thread per task (common in legacy code)

// Pattern 1: explicit new Thread per request
@RestController
class OrderController {
    @PostMapping("/orders")
    public Response processOrder(Order order) {
        // WRONG: creates a new OS thread per request
        new Thread(() -> {
            sendEmailNotification(order);  // I/O-bound
        }).start();
        return Response.ok(order.getId());
    }
}

// Problem:
//   Each Thread.start() -> clone() syscall -> new OS thread
//   OS thread: 512KB-2MB stack (default -Xss)
//   1000 concurrent requests: 1000 extra threads
//   5000 req/s: 5000 threads created per second
//   Thread lifecycle: short (email send takes 100ms)
//   But under burst: 5000 req/s * 100ms = 500 active threads
//   Memory: 500 * 1MB = 500MB native memory just for thread stacks
//   Plus: 500 context switches on each completion

// Pattern 2: CachedThreadPool (no upper bound)
ExecutorService pool = Executors.newCachedThreadPool();
// CachedThreadPool: creates new thread for every queued task
// Under sustained load: N tasks in flight -> N threads
// Gradually fills native memory -> OOM
// dmesg: "unable to create native thread"
```

---

### How to Detect It

```bash
# Observation 1: Thread count growing with load
jcmd $PID Thread.count
# Run under increasing load; count should stabilize
# If growing linearly: unbounded thread creation

# Observation 2: Native memory growing
watch -n 5 'cat /proc/$(pgrep java)/status | grep VmRSS'
# If RSS grows with request count: thread stack memory

# Observation 3: OOM with "unable to create native thread"
grep "unable to create native thread" /var/log/app.log

# Observation 4: OS thread count
ps huH p $PID | wc -l  # Count all threads of JVM process
# Healthy: CPU*2 + constant (GC + JVM internals)
# Problematic: growing proportionally to load

# Observation 5: NMT (Native Memory Tracking)
java -XX:NativeMemoryTracking=detail -jar app.jar
jcmd $PID VM.native_memory detail | grep Thread
# Thread section: growing -> unbounded thread creation

# Cause correlation: check thread creation rate
jcmd $PID VM.native_memory baseline
# ... run under load ...
jcmd $PID VM.native_memory detail.diff | grep Thread
# "Thread (reserved=2048000KB +1500000KB, ...)"
# +1500000KB: 1.5GB of new thread stack created since baseline
```

---

### The Fix

```java
// GOOD: Bounded thread pool for fire-and-forget tasks

// Option 1: Fixed thread pool (bounded, simple)
private final ExecutorService emailExecutor =
    Executors.newFixedThreadPool(
        Runtime.getRuntime().availableProcessors() * 2,
        new ThreadFactory() {
            private final AtomicInteger count = new AtomicInteger();
            public Thread newThread(Runnable r) {
                Thread t = new Thread(r);
                t.setName("email-worker-" + count.incrementAndGet());
                t.setDaemon(true);
                return t;
            }
        }
    );

// Option 2: ThreadPoolExecutor with proper queue and rejection
// Queue capacity = max tasks to buffer (not unbounded)
private final ExecutorService emailExecutor =
    new ThreadPoolExecutor(
        4,                           // core threads
        4,                           // max threads (bounded!)
        0L, TimeUnit.MILLISECONDS,
        new LinkedBlockingQueue<>(1000),  // bounded queue
        Executors.defaultThreadFactory(),
        new ThreadPoolExecutor.CallerRunsPolicy()  // backpressure
    );

// Option 3: Virtual threads (Java 21)
// Use for I/O-bound fire-and-forget tasks
private final ExecutorService emailExecutor =
    Executors.newVirtualThreadPerTaskExecutor();
// Virtual threads: no OS thread per task; safe for many tasks
// Each virtual thread: small (~few KB), not 1MB OS thread stack
// 10000 virtual threads: ~10MB (not 10GB)

// Usage (same for all options):
@PostMapping("/orders")
public Response processOrder(Order order) {
    emailExecutor.submit(() -> sendEmailNotification(order));
    return Response.ok(order.getId());
}
```

---

### Thread Stack Memory Deep Dive

```
Java thread stack size:
  Default (JVM): depends on OS and JVM version
    Linux 64-bit: 512KB to 1MB
    macOS: 512KB default
    
  Configuration:
    -Xss256k: 256KB stack per thread (minimum reasonable)
    -Xss512k: 512KB (default-ish)
    -Xss2m: 2MB (for deeply recursive code)
    
  Memory per thread:
    -Xss512k + thread overhead (~32KB): ~544KB per thread
    1000 threads: 544MB native memory
    10000 threads: 5.4GB native memory!
    
  This memory is NOT in the JVM heap:
    Not counted by -Xmx
    Not tracked by GC
    Uses native (off-heap) memory
    Can exceed container cgroup memory limit
    
  Finding thread count limits:
    OS limit: cat /proc/sys/kernel/threads-max
    Per-process: ulimit -u  (processes/threads limit)
    JVM default: limited by native memory and OS limits
    
  Stack overflow (different from OOM):
    Too-deep recursion: each frame on stack
    Stack grows to Xss limit: StackOverflowError
    Not OOM; just specific to that thread's stack depth
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Using Executors.newCachedThreadPool() is safe because threads are reused" | CachedThreadPool reuses threads only if they're idle. Under sustained load, new tasks keep arriving before threads finish, so new threads keep being created. The "cache" only helps for bursts followed by idle periods. For production with sustained load: always use newFixedThreadPool or bounded ThreadPoolExecutor. |
| "Virtual threads are just like coroutines and use no memory" | Virtual thread continuations are stored on the Java heap. Each virtual thread continuation: a few KB (vs 1MB for OS thread stack). 1M virtual threads: a few GB of heap (manageable). But continuation objects DO count against -Xmx. For truly memory-constrained environments: still need to limit virtual thread concurrency. |
| "OutOfMemoryError means the heap is full" | OOM can mean: (1) Java heap full (most common), (2) native memory for thread stacks exhausted ("unable to create native thread"), (3) Metaspace full, (4) direct buffer exhaustion. The OOM message tells you which. "unable to create native thread" = OS/native memory issue, NOT related to -Xmx heap. |

---

### Quick Reference Card

| Question | Answer |
|----------|--------|
| Default OS thread stack | 512KB-1MB (JVM default) |
| 10K threads memory | 5-10GB native (not heap!) |
| Safe thread pool size | N_CPU * 2 to N_CPU * 10 (I/O) |
| Detect unbounded creation | `ps huH p $PID \| wc -l` growing |
| Fix with Java 21 | `Executors.newVirtualThreadPerTaskExecutor()` |
| OOM message for thread limits | "unable to create native thread" |
| Monitor native thread memory | NMT Thread section |
