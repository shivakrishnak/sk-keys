---
layout: default
title: "Scheduler / Preemption"
parent: "Operating Systems"
nav_order: 96
permalink: /operating-systems/scheduler-preemption/
number: "0096"
category: Operating Systems
difficulty: ★★☆
depends_on: Process, Thread, Context Switch, Timer Interrupt
used_by: Thread Pool, Real-Time Systems, Java Thread Priority
related: Context Switch, Starvation, Priority Inversion
tags:
  - os
  - internals
  - performance
  - intermediate
---

# 096 — Scheduler / Preemption

⚡ TL;DR — The scheduler decides which process/thread runs next on the CPU; preemption forcibly interrupts a running task to give the CPU to a higher-priority or time-sliced task.

| #096 | Category: Operating Systems | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Process, Thread, Context Switch, Timer Interrupt | |
| **Used by:** | Thread Pool, Real-Time Systems, Java Thread Priority | |
| **Related:** | Context Switch, Starvation, Priority Inversion | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Without a scheduler, programs must voluntarily give up the CPU. One
cooperative program that runs an infinite loop (or a tight computation)
holds the CPU forever. All other programs — including the user interface
— freeze. On Windows 3.1, a badly written application could lock the
entire system. This is cooperative multitasking, and it relied on every
program being polite.

For any system running untrusted code (browser tabs, user applications,
server workloads), relying on programs to be polite is catastrophically
fragile. One buggy — or malicious — program can render the entire system
unresponsive.

**THE BREAKING POINT:**
Cooperative multitasking means one hung program blocks every other
program. For multi-user systems, this is a security and reliability
catastrophe.

**THE INVENTION MOMENT:**
This is exactly why the **Preemptive Scheduler** was invented — a hardware
timer fires at regular intervals, the OS takes control regardless of what
the current program is doing, and fairly distributes CPU time.

---

### 📘 Textbook Definition

The **scheduler** is the OS component that selects which runnable
process or thread executes on a CPU core at any given moment, using a
scheduling algorithm (e.g., CFS, FIFO, Round-Robin) based on priorities,
fairness criteria, and CPU affinity. **Preemption** is the scheduler's
ability to forcibly interrupt an executing process (via a timer interrupt)
and switch to another without the running process's cooperation. Modern
schedulers are preemptive, ensuring that no single process can monopolize
the CPU indefinitely. The Linux Completely Fair Scheduler (CFS) uses a
red-black tree keyed on virtual runtime to select the task that has run
the least.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
The scheduler is the CPU's traffic controller, deciding who drives next.

**One analogy:**

> Imagine a teacher managing a classroom. Cooperative scheduling: students
> raise their hand when they're done speaking. Preemptive scheduling: the
> teacher has a timer — when it rings, the current speaker MUST stop,
> and the teacher decides who speaks next. The teacher is the scheduler.
> The timer is the hardware interrupt.

**One insight:**
Preemption is not just a performance feature — it is a security and
reliability mechanism. Without preemption, any program can deny service
to all other programs. Preemption is what makes "fair time-sharing"
enforceable rather than just requested.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **Fairness**: every runnable process must eventually get CPU time — no
   process runs forever while others starve.
2. **Preemption**: the scheduler can interrupt any running process at any
   time; no process can prevent this.
3. **Responsiveness vs throughput trade-off**: shorter time slices mean
   faster response time but more context switches; longer slices mean
   better throughput but slower responsiveness.

**DERIVED DESIGN:**
A hardware timer (programmable interrupt timer, PIT) fires every N
milliseconds. When it fires, the CPU jumps to the kernel timer interrupt
handler. The scheduler runs, examines all runnable tasks, picks the best
one, and does a context switch. The "best" depends on the scheduling
algorithm.

**THE TRADE-OFFS:**
**Gain:** fairness, responsiveness, protection against runaway processes.
**Cost:** timer interrupt overhead (1,000 interrupts/second at HZ=1000),
context switch cost on each preemption, reduced throughput for
CPU-bound tasks (time sliced away unnecessarily).

---

### 🧪 Thought Experiment

**SETUP:**
Three threads: T1 (video rendering, CPU-intensive), T2 (UI event handler,
needs fast response), T3 (background backup, low priority).

**WHAT HAPPENS WITH COOPERATIVE SCHEDULING:**
T1 runs its rendering loop — never yields. T2 waits to handle a mouse
click. The click feels laggy — 500ms delay. T3 never runs. The backup
fails to complete.

**WHAT HAPPENS WITH PREEMPTIVE PRIORITY SCHEDULING:**
T1 gets a time slice and runs 4ms. Timer fires → T2 is runnable (high
priority, mouse event pending) → immediate context switch to T2. T2
processes the mouse event in 1ms → marks complete. Next timer: T1
resumes. T3 gets CPU during T1's blocked periods (disk IO). All three
make progress. Mouse click response: <5ms.

**THE INSIGHT:**
Priority-based preemption turns CPU scheduling from "who holds the
token" into "who needs it most right now." Interactive tasks get the
CPU when they need it; background tasks get leftovers.

---

### 🧠 Mental Model / Analogy

> The scheduler is an air traffic controller. Planes (threads) are
> all in the air (runnable). The controller decides who lands (gets CPU)
> next. Emergency planes (high priority) jump the queue. If a plane
> has been circling too long (fairness), it gets priority.
> The timer is the controller's radio — they can interrupt any pilot.

**Analogy mapping:**

- "Air traffic controller" → OS scheduler
- "Plane in the air (runnable)" → thread in READY queue
- "Landing (gets CPU)" → thread selected to run
- "Emergency plane (high priority)" → real-time or high-priority thread
- "Circling too long (fairness)" → virtual runtime in CFS
- "Radio interrupt" → hardware timer interrupt

Where this analogy breaks down: planes choose their own speed and route
(some autonomy); threads have no autonomy — the scheduler is absolute.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
The scheduler is the part of the OS that decides which program runs on
the CPU right now. It switches between programs so fast that everything
appears to run at once.

**Level 2 — How to use it (junior developer):**
You rarely interact with the scheduler directly. Set thread priority
(`Thread.setPriority()` in Java, `nice` in Linux). Avoid CPU-bound loops
that hog the core — call `Thread.yield()` or `Thread.sleep(0)` in tight
loops to give other threads a chance. Use `Executors.newFixedThreadPool`
to let the OS schedule a reasonable number of threads.

**Level 3 — How it works (mid-level engineer):**
Linux's CFS maintains a red-black tree of runnable tasks sorted by
`vruntime` (virtual runtime = actual CPU time weighted by priority).
The leftmost node (least vruntime = ran the least) is always chosen next.
New tasks start with vruntime = current_min_vruntime so they get immediate
CPU. The time slice is `sysctl_sched_min_granularity` × log2(nr_tasks).
At high thread counts, time slices shrink, increasing context switch rate.

**Level 4 — Why it was designed this way (senior/staff):**
The O(1) scheduler (Linux 2.6.0–2.6.22) used two priority arrays
(active/expired) for O(1) scheduling. Its problem: interactive tasks
could lose out to batch tasks depending on array flip timing. CFS
(Linux 2.6.23+) replaced it with the red-black tree model, achieving
O(log n) scheduling that is naturally fair without heuristics. The
`nice` value maps to a weight in the CFS weight table — `nice 0` = 1024,
`nice -20` = 88761. The ratio of weights determines CPU share proportion.

---

### ⚙️ How It Works (Mechanism)

**CFS Scheduling decision:**

```
┌──────────────────────────────────────────────────┐
│              LINUX CFS RUN QUEUE                 │
├──────────────────────────────────────────────────┤
│  Red-Black Tree (sorted by vruntime):            │
│                                                  │
│         Thread C                                 │
│        (vruntime=5ms)                            │
│       /             \                            │
│  Thread A          Thread D                      │
│ (vruntime=3ms)   (vruntime=8ms)                  │
│       /                                          │
│  Thread B                                        │
│ (vruntime=1ms) ← leftmost = NEXT TO RUN          │
│                                                  │
│  Scheduler picks Thread B (lowest vruntime)      │
│  Thread B runs for time_slice ms                 │
│  Thread B's vruntime increases                   │
│  Thread B re-inserted into tree                  │
└──────────────────────────────────────────────────┘
```

**Preemption flow:**

```
Timer interrupt fires (every 1ms at HZ=1000)
  → CPU switches to kernel mode
  → Calls scheduler_tick()
  → Updates current task's vruntime
  → Checks if another task has lower vruntime
  → If yes: sets TIF_NEED_RESCHED flag
  → On return to user mode: context switch triggered
  → New task runs
```

**Priority mapping (Linux nice to weight):**

```
nice -20  → weight 88761  (gets ~88x more CPU than nice +19)
nice   0  → weight  1024  (default)
nice +10  → weight   110
nice +19  → weight     1
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**

```
Thread A running (user mode)
  → Timer interrupt fires
  → Kernel: scheduler_tick() increments vruntime
  → Thread B has lower vruntime → needs preemption
  → [SCHEDULER RUNS ← YOU ARE HERE]
  → Thread A context saved, Thread B context loaded
  → Thread B runs its time slice
  → Thread A eventually selected again (fair turn)
```

**FAILURE PATH:**

```
Thread with real-time priority (SCHED_FIFO) runs infinite loop
  → Never preempted (SCHED_FIFO: no time slice limit)
  → All other threads starved
  → System becomes unresponsive
  → Only another SCHED_FIFO thread with higher priority
    or a kernel interrupt can interrupt it
```

**WHAT CHANGES AT SCALE:**
With 1,000 runnable threads on 4 cores, each thread gets
`time_slice / 1000 × 4` = ~16µs per second on a 4ms total time slice.
The context switch rate hits 1000/4ms × 4 cores = 250,000 switches/sec.
This saturates scheduler overhead. Solution: reduce runnable thread count
(async IO) or use CPU affinity to partition work.

---

### 💻 Code Example

Example 1 — Checking scheduler policy and observing preemption:

```bash
# View scheduling policy of a process
chrt -p <pid>
# Output: pid X's scheduling policy: SCHED_OTHER
#         pid X's scheduling priority: 0

# Set a thread to real-time FIFO (careful — can starve system)
sudo chrt -f -p 50 <pid>

# Observe context switches per thread
cat /proc/<pid>/status | grep ctxt
# voluntary_ctxt_switches: 12034
# nonvoluntary_ctxt_switches: 892
# High nonvoluntary = being preempted frequently
```

Example 2 — Java thread priority (maps to OS priority):

```java
// BAD: default priority for time-sensitive work
Thread workerThread = new Thread(this::processCriticalAlerts);
// Scheduled with same priority as all other threads

// GOOD: explicit priority for time-sensitive work
Thread alertThread = new Thread(this::processCriticalAlerts);
alertThread.setPriority(Thread.MAX_PRIORITY); // 10 on JVM
alertThread.start();

Thread bulkThread = new Thread(this::runBulkJob);
bulkThread.setPriority(Thread.MIN_PRIORITY); // 1 on JVM
bulkThread.start();
// Note: JVM maps to OS nice values; exact behavior is OS-dependent
```

---

### ⚖️ Comparison Table

| Algorithm     | Fairness  | Latency   | Throughput | Best For           |
| ------------- | --------- | --------- | ---------- | ------------------ |
| **CFS**       | High      | Good      | Good       | General-purpose OS |
| FIFO (RT)     | None      | Excellent | High       | Real-time tasks    |
| Round Robin   | Perfect   | Medium    | Medium     | Time-sharing       |
| Priority      | Variable  | Very good | Good       | Mixed workloads    |
| Deadline (DL) | Guarantee | Exact     | Limited    | Hard real-time     |

How to choose: use CFS (default) for most workloads; use SCHED_FIFO or
SCHED_DEADLINE only for hardware control, audio/video with strict deadlines.

---

### ⚠️ Common Misconceptions

| Misconception                                          | Reality                                                                                                                                               |
| ------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Higher thread priority always means faster execution" | Higher priority means more CPU time when competing; if the thread is blocked on IO, priority doesn't help at all                                      |
| "Thread.yield() guarantees another thread runs"        | yield() is a hint to the scheduler; the same thread may immediately be re-selected, especially if no other runnable threads exist                     |
| "Java thread priorities directly map to OS priorities" | JVM maps Java priorities 1–10 to OS-specific values; on Linux, SCHED_OTHER threads all have the same priority — `nice` value is used instead          |
| "The scheduler runs every millisecond"                 | Timer interrupt fires every 1ms at HZ=1000, but the scheduler only does a context switch if a higher-priority task became runnable                    |
| "Preemptive scheduling prevents starvation"            | Preemption prevents CPU monopoly but priority inversion can still cause starvation if a low-priority thread holds a lock a high-priority thread needs |

---

### 🚨 Failure Modes & Diagnosis

**1. Starvation of low-priority threads**

**Symptom:**
Background task (backup, reporting) never makes progress. `ps` shows
it's in RUNNABLE state but vruntime keeps growing without execution.

**Root Cause:**
High-priority threads always have lower vruntime than the low-priority
thread, so CFS always picks them first. The low-priority thread is
technically runnable but never selected.

**Diagnostic:**

```bash
# Check if a process is being scheduled
pidstat -u -p <pid> 1 10
# If %CPU stays near 0 for a runnable process: starvation likely
# Check nice value
ps -o pid,nice,cmd -p <pid>
```

**Fix:** increase low-priority thread's nice value to 0 (default) or use
cgroups CPU shares to guarantee minimum CPU allocation.

**Prevention:** use cgroups `cpu.shares` to give every process group a
minimum guaranteed CPU fraction.

**2. Real-time thread starves system**

**Symptom:**
System becomes unresponsive. SSH impossible. `top` shows one process
at 100% CPU with RT scheduling policy.

**Root Cause:**
SCHED_FIFO thread with high priority runs indefinitely without blocking.
All non-RT threads are starved because SCHED_FIFO bypasses normal CFS.

**Diagnostic:**

```bash
chrt -p <pid>    # check scheduling policy
# ps shows state R (running) for the RT process continuously
ps -eo pid,stat,policy,pri,cmd | grep -v -e 'S ' -e 'I '
```

**Fix:** Linux has a safety valve — `kernel.sched_rt_runtime_us` (default
950ms/s) limits RT task CPU to 95%, leaving 5% for non-RT.

```bash
sysctl kernel.sched_rt_runtime_us    # check current value
sysctl -w kernel.sched_rt_runtime_us=950000  # 95% for RT max
```

**Prevention:** never deploy SCHED_FIFO threads without testing the worst-case
runtime; always set `sched_rt_runtime_us` as a safety limit.

**3. Scheduler overhead from too many threads**

**Symptom:**
`top` shows high `sy` (system) CPU%. `perf record -e sched:sched_switch`
shows thousands of scheduler events per second consuming CPU cycles.

**Root Cause:**
More runnable threads than CPU cores. Scheduler spends all its time
evaluating the red-black tree and performing context switches rather than
running useful work.

**Diagnostic:**

```bash
# Measure scheduler overhead with perf
perf stat -e sched:sched_switch,sched:sched_wakeup \
  -p <pid> sleep 5
# High sched_switch count relative to useful work = overhead issue
```

**Fix:** reduce thread pool size; move IO-bound threads to async/virtual
threads; increase time slice via `kernel.sched_min_granularity_ns`.

**Prevention:** set thread pool size = 2 × CPU cores for CPU-bound; use
async IO for IO-bound tasks.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Process` — the scheduler manages processes
- `Thread` — the scheduler manages threads within processes
- `Context Switch` — the scheduler triggers context switches

**Builds On This (learn these next):**

- `Starvation` — what happens when low-priority threads never get scheduled
- `Deadlock` — when threads are blocked waiting for each other
- `Thread Pool` — the production pattern that manages scheduling overhead

**Alternatives / Comparisons:**

- `Fiber / Coroutine` — user-space scheduling, bypasses OS scheduler
- `Real-Time Scheduling` — SCHED_FIFO/DEADLINE for hard time constraints

---

### 📌 Quick Reference Card

```text
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS │ OS component deciding which task runs next │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT │ Multiple tasks compete for one CPU; │
│ SOLVES │ cooperative yielding is not reliable │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT │ Preemption is a security feature, not │
│ │ just a performance one │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN │ Always active — tune by adjusting thread │
│ │ count, priorities, and nice values │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN │ Avoid SCHED_FIFO for non-RT workloads — │
│ │ it bypasses fairness guarantees │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF │ Responsiveness (short slices) vs │
│ │ throughput (long slices) │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER │ "The scheduler is the invisible hand that │
│ │ keeps every program from starving" │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Context Switch → Starvation → Deadlock │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Linux CFS guarantees fairness based on `vruntime`. But a thread
that blocks on IO for 5 seconds gets its `vruntime` artificially reduced
when it wakes up (it looks like it has run less). This means an IO-bound
thread gets a CPU boost after waking from IO. Why was this design choice
made? What problem does it solve? What pathological scenario could this
create if you had 100 threads that all woke from IO simultaneously?

**Q2.** A Java web server uses a thread pool of 200 threads to handle
HTTP requests. Under normal load (100 req/s), response time is 5ms.
Under spike load (10,000 req/s), response time jumps to 800ms despite
CPU utilization being only 40%. Given what you know about the scheduler,
context switching, and the relationship between runnable thread count and
time slices, explain the exact mechanism causing the latency spike and
describe two architectural changes that would prevent it.
