---
id: JCC-032
title: Busy-Wait vs Blocking
category: Java Concurrency
tier: tier-3-java
folder: JCC-java-concurrency
difficulty: ★★★
depends_on: JCC-076, JCC-081, JCC-040
used_by:
related: JCC-047, JCC-057, JCC-027
tags:
  - java
  - concurrency
  - performance
  - advanced
  - tradeoff
status: complete
version: 2
layout: default
parent: "Java Concurrency"
grand_parent: "Technical Dictionary"
nav_order: 82
permalink: /java-concurrency/busy-wait-vs-blocking/
---

# JCC-082 - BUSY-WAIT VS BLOCKING

⚡ **TL;DR** - Busy-wait burns CPU spinning for a condition; blocking
parks the thread and yields the CPU. Choose busy-wait only for
ultra-low latency where the expected wait is shorter than a context
switch (~10 microseconds).

---

| Field      | Value                                              |
|------------|----------------------------------------------------|
| Depends on | JCC-076 Amdahl's Law, JCC-081 False Sharing, JCC-040 ReentrantLock |
| Used by    | (foundational performance trade-off)               |
| Related    | JCC-047 CAS (Compare-And-Swap), JCC-057 BlockingQueue, JCC-027 Condition Interface |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A developer must wait for a shared variable to reach a target value.
Two options exist: continuously re-read it (busy-wait), or sleep/park
and be woken when the value changes (blocking). Choosing wrong costs
CPU cores (busy-wait in wrong context) or adds latency (blocking
when response time is critical).

**THE BREAKING POINT:**
A low-latency market data handler uses `BlockingQueue.take()`,
adding 10-50 microsecond latency per message from thread context
switches. Under normal load this is fine. At peak, 50 microsecond
jitter causes market orders to arrive after the arbitrage window
closes. Competing systems using busy-wait ring buffers react in
under 1 microsecond.

**THE INVENTION MOMENT:**
The LMAX Disruptor (2010) popularised busy-wait in Java for extreme
low-latency scenarios. Its `BusySpinWaitStrategy` dedicates a full
CPU core to spinning on the ring buffer cursor - trading core for
microseconds.

**EVOLUTION:**
- **Java 5:** `Thread.yield()` as cooperative spin hint
- **Java 9:** `Thread.onSpinWait()` - CPU-level hint (`PAUSE`
  instruction on x86) to optimise spin loops without false sharing
  on spin variable
- **LMAX Disruptor:** Popularised busy-spin in Java HFT
- **Java 21:** Virtual threads make blocking cheap enough that
  busy-wait is rarely justified outside HFT/embedded contexts

---

### 📘 Textbook Definition

**Busy-wait (spin-wait):** A thread continuously checks a condition
in a loop without sleeping or yielding. It consumes 100% of its
CPU core while waiting.

**Blocking wait:** A thread parks itself (via `park()`, `Object.wait()`,
`Condition.await()`, `LockSupport.park()`), releasing the CPU
until another thread explicitly unparks/signals it.

**Key distinction:**

| Aspect | Busy-wait | Blocking |
|--------|-----------|---------|
| CPU during wait | 100% (one core consumed) | 0% (thread parked) |
| Wake latency | Microseconds (already running) | 10-100 microseconds (context switch) |
| Scalability | Poor (N spinners = N cores wasted) | Good (thread parks, scheduler reuses core) |
| Use case | Sub-millisecond, HFT, real-time | All other concurrent Java code |

---

### ⏱️ Understand It in 30 Seconds

**One line:** Busy-wait is a guard dog that never sleeps; blocking
is a pager that wakes you only when something happens.

**One analogy:**
> Waiting for someone to arrive at a train station.
> Busy-wait: you stare at the platform entrance without blinking,
> seeing them the instant they appear, but exhausting yourself
> (using 100% CPU).
> Blocking: you sit, set a phone alarm, and receive a text when
> they arrive - slightly delayed but you can read while waiting.

**One insight:** The context switch (~5-50 microseconds) is the
break-even point. If your expected wait is shorter, busy-wait wins.
If longer, blocking wins every time.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. A parked thread (blocking) cannot respond faster than the OS
   scheduler latency: typically 5-50 microseconds on Linux with
   standard kernel, <10 microseconds with `PREEMPT_RT` kernel.
2. A busy-waiting thread responds in nanoseconds - it is already
   running and checks the condition on the next loop iteration.
3. Busy-wait consumes exactly one CPU core 100% during the wait.
   With N spinning threads, N cores are fully consumed.
4. `Thread.onSpinWait()` emits a CPU `PAUSE` instruction: reduces
   power, reduces memory ordering pressure, and prevents the
   speculative execution stall that tight loops cause.
5. Hybrid spinning: spin briefly, then block. Reduces latency while
   capping CPU waste. Used in many lock implementations.

**DERIVED DESIGN:**
`synchronized` and `ReentrantLock` use hybrid spinning: they spin
for a few hundred nanoseconds before inflating the lock and calling
`park()`. This handles the common case (lock released quickly)
without wasting CPU for the long case.

**THE TRADE-OFFS:**

**Busy-wait gain:** Sub-microsecond latency; no syscall; no context
switch; no wake-up scheduling delay.

**Busy-wait cost:** One core permanently occupied; bad for latency
if the wait is long; causes CPU power/heat.

**Blocking gain:** CPU freed for other work; scales to any wait
duration; no wasted power.

**Blocking cost:** Wake-up latency (5-100 microseconds); involves
OS scheduler; kernel context switch.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

**Essential:** OS scheduling introduces irreducible latency for
blocked threads. This is fundamental to time-sharing operating
systems.

**Accidental:** Many Java developers use blocking where busy-wait
would be appropriate (nanosecond response required), and vice versa.

---

### 🧪 Thought Experiment

**SETUP:** A message is produced every 100 nanoseconds. The consumer
must process each within 500 nanoseconds. Both producer and consumer
run on a 16-core machine.

**WITH BLOCKING (`BlockingQueue.take()`):**
```
Message arrives
Consumer notified (wakeup latency: ~20 microseconds)
Consumer processes message: 50ns
Total: 20,050ns per message - MISSES 500ns requirement
Benefit: 15 free cores for other tasks
```

**WITH BUSY-WAIT (ring buffer + spin):**
```
Message arrives
Consumer sees it on next spin iteration: ~10ns
Consumer processes message: 50ns
Total: 60ns per message - meets 500ns requirement
Cost: 1 core fully consumed by spinning consumer
Benefit: none (core otherwise idle in this HFT scenario)
```

**THE INSIGHT:** When the wait duration is shorter than the wake-up
latency, busy-wait delivers orders of magnitude better response
time at the cost of one CPU core. When wait duration is longer,
the consumed core is wasted.

---

### 🧠 Mental Model / Analogy

> Busy-wait is Formula 1 pit crew: standing ready at full attention,
> immediately springing into action the instant the car arrives.
> Blocking is a mechanic on call: off duty until paged, arriving
> 5-30 minutes later (the OS scheduling latency).

**Element mapping:**
- Car arrives = condition becomes true / message available
- Pit crew standing ready = spinning thread checking condition
- Paged mechanic driving in = OS wakeup + context switch
- Pit crew reaction time (<1s) = busy-wait latency (~nanoseconds)
- Paged mechanic arrival (5-30min) = blocking wake-up (micro-sec)
- Full pit crew deployed 24/7 = CPU core consumed 100%

Where this analogy breaks down: a real F1 pit crew is expensive
in money; a spinning thread is expensive in CPU cycles that could
serve other requests in a general-purpose service.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Busy-wait: check, check, check in a fast loop until the condition
is true. Blocking: tell the OS "wake me up when this happens" and
go to sleep. The first is instant but wastes power; the second
saves power but is slower to respond.

**Level 2 - How to use it (junior developer):**
```java
// Blocking: prefer for most cases
BlockingQueue<Message> queue = new LinkedBlockingQueue<>();
Message msg = queue.take(); // yields CPU, woken when message arrives

// Busy-wait: only for known sub-microsecond waits
AtomicInteger flag = new AtomicInteger(0);
while (flag.get() == 0) {
    Thread.onSpinWait(); // CPU hint: spin efficiently
}
```

**Level 3 - How it works (mid-level engineer):**
Blocking: `LockSupport.park()` calls `pthread_mutex_lock` (Linux)
or `WaitForSingleObject` (Windows) -> kernel context switch
-> thread moved to wait queue -> CPU core released -> on signal:
thread moved to run queue -> scheduler picks it up -> context
switch back. Total: 10-200 microseconds depending on OS and load.

Busy-wait: a RUNNABLE thread executes a tight loop reading a shared
variable. On x86, `PAUSE` instruction (from `onSpinWait()`) delays
1 loop iteration ~40 cycles, reducing memory order speculation stalls
and allowing other hyper-threads to make progress.

**Level 4 - Why it was designed this way (senior/staff):**
The OS scheduler's granularity of ~1-10ms on Windows and ~0.1-4ms
on Linux (configurable for real-time kernels) is the fundamental
blocking latency. Java's `park()` maps to OS primitives, inheriting
this latency. For sub-millisecond response requirements, OS-managed
blocking is architecturally incompatible with the latency budget.
The PAUSE instruction hint was added to Intel CPUs specifically to
make spin loops efficient in virtualised and hyper-threaded
environments where tight loops without PAUSE cause interference
with co-running threads.

**Expert Thinking Cues:**
- Hybrid approach: spin for ~1000ns, then park - covers the common
  case without wasting a full core for long waits.
- `Thread.yield()` is weaker than park: it hints to schedule another
  thread but is not a blocking call. Still consumes CPU.
- Dedicated cores: pin a busy-waiting thread to an isolated CPU
  (`taskset` on Linux) to prevent OS time-slicing from starving
  the spinner.
- Virtual threads: `LockSupport.park()` on a virtual thread releases
  the carrier (cheap); busy-wait on a virtual thread pins the carrier
  (expensive). Never use busy-wait inside virtual thread code.

---

### ⚙️ How It Works (Mechanism)

**Blocking call sequence (Linux):**
```
Thread calls LockSupport.park()
  -> JNI: pthread_cond_wait() or futex(FUTEX_WAIT)
  -> kernel: thread moved from run queue to wait queue
  -> kernel: CPU core freed, other threads scheduled
  -> signal: LockSupport.unpark(thread)
  -> kernel: thread moved back to run queue
  -> next scheduler tick: thread resumed
  -> JNI returns
  -> Java execution resumes in park() call
Total latency: 5-200+ microseconds
```

**Busy-wait sequence:**
```
Thread enters spin loop
while (!condition.get()) {
    Thread.onSpinWait(); // emits PAUSE instruction
}
  -> CPU: executes PAUSE, waits ~10-40 cycles
  -> CPU: reads cached value of condition
  -> No kernel involvement
  -> Condition true: exits loop immediately
Total latency: 10-1000 nanoseconds (condition + cache refresh)
```

**Hybrid spin-then-block (modern lock implementation):**
```
lockInterruptibly():
  [spin up to ~200ns]
  if (CAS succeeds): return (fast path)
  else:
  [park() - blocking path]
  -> wake on unpark
  -> retry CAS
```

---

### 🔄 The Complete Picture - End-to-End Flow

**DECISION FLOW:**
```
Need to wait for condition?        <- YOU ARE HERE
       |
  Expected wait duration?
  |              |
< 10 microseconds  > 10 microseconds
  |              |
Busy-wait OK   Use blocking
  |              |
Available dedicated core?  Thread pool? VT?
  YES: spin    USE: park/await/queue.take()
  NO: block    |
               Normal concurrent Java code
```

**FAILURE PATH:**
Busy-wait in a general-purpose web request handler:
- 100 concurrent requests = 100 cores spinning simultaneously
- Server has 16 cores; 84 requests starved
- Throughput collapses

**WHAT CHANGES AT SCALE:**
- Cloud/containerised environments: no CPU isolation; spinning
  threads compete with other containers on the host.
- Virtual threads: park is cheap (releases carrier); spin wastes
  carrier even for virtual threads. Never spin inside virtual thread.

---

### 💻 Code Example

**BAD - busy-wait in high-concurrency service (wastes cores):**
```java
// BAD: each request handler spins waiting for DB result
// 1000 concurrent requests = 1000 cores spinning
@GetMapping("/api/data")
public Data getData() {
    AtomicReference<Data> result = new AtomicReference<>();
    executor.submit(() -> result.set(fetch()));

    // BAD: busy-wait for async result
    while (result.get() == null) {
        Thread.onSpinWait(); // burns a core per request
    }
    return result.get();
}
```

**BAD - blocking in HFT critical path:**
```java
// BAD: 50-microsecond wake-up latency breaks nanosecond budget
class SlowConsumer {
    private final BlockingQueue<MarketData> queue;

    void consume() throws InterruptedException {
        while (true) {
            MarketData data = queue.take(); // 10-50us wake-up!
            processOrder(data);
        }
    }
}
```

**GOOD - blocking for normal concurrent code:**
```java
// GOOD: correct for 99% of Java concurrent code
class MessageConsumer {
    private final BlockingQueue<Message> queue;

    void consume() throws InterruptedException {
        while (!Thread.currentThread().isInterrupted()) {
            Message msg = queue.take(); // blocks, releases CPU
            process(msg);
        }
    }
}
```

**GOOD - busy-wait for HFT with isolation:**
```java
// GOOD: dedicated core, short expected wait, VT-free
class HFTConsumer implements Runnable {
    private final RingBuffer<MarketData> ring;
    private final AtomicLong cursor;

    @Override public void run() {
        // Pin this thread to a CPU core via OS (taskset)
        long nextSeq = 0;
        while (true) {
            while (cursor.get() < nextSeq) {
                Thread.onSpinWait(); // PAUSE hint
            }
            processEntry(ring.get(nextSeq));
            nextSeq++;
        }
    }
}
```

**GOOD - hybrid (spin briefly then park):**
```java
// GOOD: handles both fast (sub-ms) and slow (ms+) waits
class HybridLatch {
    private volatile boolean done = false;

    void await() throws InterruptedException {
        // Spin for 1000 iterations (~1-2 microseconds on modern CPU)
        for (int i = 0; i < 1000; i++) {
            if (done) return;
            Thread.onSpinWait();
        }
        // Fall back to blocking if not done after spin budget
        synchronized (this) {
            while (!done) wait();
        }
    }

    void complete() {
        done = true;
        synchronized (this) { notifyAll(); }
    }
}
```

---

### ⚖️ Comparison Table

| Criteria | Busy-wait | Hybrid spin-then-block | Blocking |
|---------|-----------|----------------------|---------|
| Wake-up latency | ~nanoseconds | ~100ns - 10us | ~10-200 microseconds |
| CPU during wait | 100% (one core) | 100% briefly, then 0% | 0% |
| Scalability | Poor (N threads = N cores) | Fair | Excellent |
| JVM support | `Thread.onSpinWait()` | Manual or in locks | `park()`, queues |
| Use case | HFT, embedded, <10us waits | Lock acquisition, NIO | Everything else |
| Virtual thread safe? | No (pins carrier) | Avoid | Yes |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "`Thread.yield()` is equivalent to parking" | `yield()` hints to the OS to reschedule but the thread remains RUNNABLE and may immediately be rescheduled back. It is NOT equivalent to `park()`, which actually suspends the thread. |
| "Busy-wait is always bad practice" | For sub-microsecond response requirements (HFT, LMAX Disruptor, real-time systems), busy-wait is the correct architecture. The LMAX Disruptor specifically recommends `BusySpinWaitStrategy` for throughput-critical paths. |
| "`Thread.onSpinWait()` is a no-op on JVMs that don't recognise it" | `Thread.onSpinWait()` returns a `void` and was added in Java 9. On JVMs that support it (x86 HotSpot), it emits the PAUSE instruction. On others it is indeed a no-op - which is safe (just not optimised). |
| "Blocking is always safer than busy-wait" | Blocking can cause priority inversion in real-time systems. Busy-wait (with core isolation) provides more predictable latency in real-time environments. |
| "Virtual threads make busy-wait efficient" | Virtual threads still map to carrier threads. Busy-wait in a virtual thread pins the carrier; 1,000 spinning virtual threads = 1,000 pinned carriers = same as 1,000 platform thread spinners. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: CPU saturation from accidental busy-wait**

**Symptom:** CPU at 100% during low-traffic periods; application
logic seems idle; no requests in flight.

**Root Cause:** A background thread spins on a condition that is
rarely (or never) met.

**Diagnostic:**
```bash
# Find which Java thread consumes CPU:
top -H -p <pid>
# Shows per-thread CPU usage sorted by %
# Correlate thread ID (TID) with jstack output:
jstack <pid> | grep -A5 "tid=0x$(printf '%x' <TID>)"
```

**Fix:** Replace spin with `Condition.await()`, `BlockingQueue.poll(timeout)`,
or `park(timeout)`.

---

**Failure Mode 2: Latency spikes from OS jitter on spinning threads**

**Symptom:** Busy-waiting thread sees 1ms+ latency spikes randomly.

**Root Cause:** The OS scheduler occasionally preempts the spinning
thread for another process. The spin loop is interrupted for one
scheduler tick (1-10ms on standard Linux).

**Diagnostic:**
```bash
# Check scheduler preemptions:
cat /proc/<tid>/schedstat
# "preempted" field shows OS preemptions

# Use OS isolation (Linux):
# isolcpus=2,3,4,5 in GRUB kernel parameters
# taskset -c 2 java -jar app.jar
```

**Fix:** Isolate CPU cores for spinning threads using `isolcpus`
and `taskset`. Prevents OS from using those cores for other tasks.

---

**Failure Mode 3: Virtual thread carrier exhaustion from busy-wait**

**Symptom:** Virtual thread workload stalls; carrier thread pool
all at 100%; no progress despite low throughput.

**Root Cause:** Virtual threads contain busy-wait loops that pin
carrier threads. With 8 carriers and 8 spinning virtual threads,
the pool is exhausted.

**Diagnostic:**
```bash
# Check carrier thread state:
jstack <pid> | grep -A5 "ForkJoinPool"
# All workers RUNNABLE in spin loops = carrier exhaustion
```

**Fix:** Replace busy-wait with `LockSupport.park()` inside virtual
threads. Park releases the carrier; spin does not.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[JCC-076 - Amdahl's Law]] - quantifies the CPU core cost of
  busy-wait as serial work unavailable to other tasks
- [[JCC-081 - False Sharing (Java Context)]] - busy-wait on shared
  variables causes false sharing
- [[JCC-040 - ReentrantLock]] - uses hybrid spin internally

**Builds On This (learn these next):**
- LMAX Disruptor documentation - canonical Java busy-wait case study
- Linux `PREEMPT_RT` kernel - for sub-microsecond blocking latency

**Alternatives / Comparisons:**
- [[JCC-047 - CAS (Compare-And-Swap)]] - the update atomic in
  busy-wait retry loops
- [[JCC-057 - BlockingQueue]] - canonical Java blocking pattern
- [[JCC-027 - Condition Interface]] - blocking with selective wakeup

---

### 📌 Quick Reference Card

```
+--------------------------------------------------+
| WHAT IT IS   | Busy-wait: spin checking condition;|
|              | Blocking: park, yield CPU, be woken|
+--------------+------------------------------------+
| PROBLEM      | Choosing wrong degrades latency OR |
|              | wastes entire CPU cores            |
+--------------+------------------------------------+
| KEY INSIGHT  | Break-even: context switch ~10us   |
|              | < 10us wait: busy-wait wins        |
|              | > 10us wait: blocking wins         |
+--------------+------------------------------------+
| USE WHEN     | Busy-wait: HFT, <10us, isolated core|
|              | Blocking: everything else          |
+--------------+------------------------------------+
| AVOID WHEN   | Busy-wait in VT, web servers,      |
|              | shared cores, long waits           |
+--------------+------------------------------------+
| TRADE-OFF    | Nanosecond latency / 1 core burned |
|              | vs 10us+ latency / 0 CPU wasted   |
+--------------+------------------------------------+
| ONE-LINER    | while(!ready) Thread.onSpinWait(); |
|              | vs queue.take() (blocking)         |
+--------------+------------------------------------+
| NEXT EXPLORE | LMAX Disruptor ring buffer (HFT),  |
|              | JCC-027 Condition Interface        |
+--------------------------------------------------+
```

**If you remember only 3 things:**
1. Context switch costs ~5-50 microseconds. Busy-wait only wins if
   expected wait is shorter than this threshold.
2. Never busy-wait inside a virtual thread - it pins the carrier,
   exhausting the pool.
3. Use `Thread.onSpinWait()` (Java 9+) in all spin loops - it
   emits the CPU PAUSE instruction, improving hyper-threading and
   power efficiency.

**Interview one-liner:** "Busy-wait consumes 100% CPU for nanosecond
response; blocking parks the thread, adding 5-50 microsecond wake-up
latency but freeing the core. Choose busy-wait only for sub-10
microsecond HFT/real-time workloads on dedicated isolated cores."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Latency and throughput optimise
on different axes. Minimising latency (busy-wait) wastes resources
that maximise throughput (blocking). Choosing the wrong model for
the workload delivers neither: a busy-waiting web server has high
latency (core starvation) AND low throughput.

**Where else this pattern appears:**
- **NIC polling (DPDK):** User-space network drivers busy-poll
  NIC ring buffers instead of using kernel interrupts, achieving
  <1 microsecond packet processing vs ~10 microsecond interrupt-
  driven latency. The same trade-off: one core consumed, sub-
  microsecond response.
- **Database spin locks (PostgreSQL):** PostgreSQL's lightweight
  spin locks (`LWLocks`) spin briefly then block. The spin handles
  the common (sub-microsecond) contention case; blocking handles
  rare long waits.
- **GPU synchronisation (CUDA):** `__syncthreads()` is a barrier
  that spins until all threads in a block reach it - the GPU
  equivalent of busy-wait, where blocking is not an option because
  GPUs have no OS context-switch mechanism.

---

### 💡 The Surprising Truth

The `Thread.sleep(0)` call, commonly believed to be a no-op that
"briefly yields", actually behaves differently across operating
systems in ways that matter for concurrency. On Windows,
`sleep(0)` yields to another SAME-priority thread only and does
not help higher-priority threads. On Linux, `sleep(0)` translates
to `sched_yield()` which moves the thread to the tail of the
run queue allowing ANY other runnable thread. `Thread.yield()` has
similar OS-dependent semantics. This means "spin with yield" code
that appears to behave correctly on Linux may starve other threads
on Windows, and vice versa - a portability hazard in spin-loop
designs that is invisible in unit tests.

---

### 🧠 Think About This Before We Continue

**Question 1 (Design Trade-off):** You are building a low-latency
messaging library that must support both: (a) HFT mode (busy-wait,
dedicated core, <1us latency) and (b) general mode (blocking, shared
pool, any latency). Design a `WaitStrategy` interface that cleanly
supports both modes. What methods should it have, and how would
you implement a hybrid spin-then-block strategy as a third option?

*Hint:* Study LMAX Disruptor's `WaitStrategy` interface and its
`BusySpinWaitStrategy`, `BlockingWaitStrategy`, and
`SleepingWaitStrategy` implementations as a reference design.

---

**Question 2 (System Interaction):** A trading system's data
consumer uses busy-wait on a ring buffer with a dedicated CPU core.
The server also runs a garbage collector. GC stop-the-world pauses
suspend the busy-waiting thread while the ring buffer continues
filling. When the GC pause ends, the consumer resumes and must
catch up. What happens to the ring buffer fill level, what is the
maximum tolerable GC pause for a ring buffer of capacity C with
producer rate R, and how would you tune GC to minimise this risk?

*Hint:* Model the ring buffer as a fixed-capacity queue: overflow
occurs at pause_duration * R messages. Research GC algorithms with
bounded pause times: ZGC (<1ms pauses) and Shenandoah, and whether
they are compatible with CPU-intensive trading workloads.

---

**Question 3 (Root Cause):** A service migrates from platform
threads to virtual threads. Before migration: P99 latency 5ms.
After migration: P50 latency 0.5ms (improved!) but P99 latency
50ms (degraded!). Thread dump after migration shows 8 virtual
threads in RUNNABLE state in tight loops. What is the root cause
of the P99 degradation, and how does it relate to busy-wait and
carrier thread coverage?

*Hint:* The 8 spinning virtual threads pin 8 carrier threads. Under
P99 traffic spikes, those 8 carriers are fully consumed by spinning
virtual threads, starving the remaining 100+ virtual threads that
need carriers to handle the P99 outlier requests. Research
ForkJoinPool compensation threads and their limits.

