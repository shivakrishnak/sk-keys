---
id: OSY-045
title: OS Working Level Self-Assessment
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★☆
depends_on: OSY-026, OSY-027, OSY-028, OSY-029, OSY-030, OSY-031, OSY-032, OSY-033
used_by: []
related: OSY-024, OSY-083, OSY-112
tags:
  - self-assessment
  - working-level
  - retention
  - checklist
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 45
permalink: /technical-mastery/osy/os-working-self-assessment/
---

## TL;DR

Self-assessment for all L2 (working-level) OS topics
covered in OSY-026 to OSY-044. Pass all 8 challenges
to confirm working-level OS mastery. Failed items
point to specific entries for review.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-045 |
| **Difficulty** | ★★☆ Working |
| **Category** | Operating Systems |
| **Tags** | self-assessment, working level, retention |
| **Prerequisites** | OSY-026 through OSY-044 |

---

### Challenge 1: Scheduling Fluency

Without looking up, answer these:
- [ ] What is the convoy effect in FCFS scheduling?
- [ ] Why is SJF optimal but not practical?
- [ ] How does Linux CFS use vruntime to ensure fairness?
- [ ] What is Belady's anomaly in page replacement?

**Check yourself:**
FCFS convoy: short jobs wait behind long CPU burst.
SJF: optimal but needs future CPU burst time.
CFS: smallest vruntime gets CPU next (red-black tree).
Belady's: FIFO may have MORE page faults with MORE frames.

---

### Challenge 2: Deadlock Diagnosis

Given this scenario - identify the deadlock and fix it:

```java
// Thread A                    // Thread B
synchronized(lock1) {          synchronized(lock2) {
  synchronized(lock2) { ... }    synchronized(lock1) { ... }
}                              }
```

- [ ] Identify which Coffman condition is violated
- [ ] Propose the minimum change to prevent deadlock
- [ ] Name the Java tool to detect this at runtime

**Check yourself:**
Violated: circular wait (T_A waits lock2 held by T_B,
T_B waits lock1 held by T_A). Fix: both threads acquire
in same order (lock1 before lock2). Detection: jstack -l.

---

### Challenge 3: Race Condition Recognition

Identify all thread safety issues:

```java
class Counter {
    private int count = 0;
    private boolean active = true;
    
    public void increment() { count++; }
    public void stop() { active = false; }
    public void run() { while (active) { ... } }
}
```

- [ ] List each bug and explain why it's a bug
- [ ] Propose the minimal fix for each

**Check yourself:**
Bug 1: `count++` not atomic -> use AtomicInteger.
Bug 2: `active` without volatile -> visibility race,
while loop may never exit. Fix: volatile boolean active.

---

### Challenge 4: Memory Layout

For a Java process with -Xms512m -Xmx4g:

- [ ] What is the approximate VIRT column in ps?
- [ ] What is the RSS if Java heap is 80% full?
- [ ] Where does class metadata go (post Java 8)?
- [ ] What happens if stack recursion is too deep?

**Check yourself:**
VIRT: ~4GB+ (heap reservation + metaspace + code cache + JVM native code).
RSS: ~3.2GB (80% of committed heap in physical RAM).
Metadata: Metaspace (native memory, not Java heap).
Deep recursion: StackOverflowError.

---

### Challenge 5: I/O Model Choice

For each scenario, choose the right I/O model:

| Scenario | Best Model |
|---------|-----------|
| 10,000 concurrent HTTP connections, Java | ? |
| Reading large file for batch processing | ? |
| Database query from Spring service | ? |
| High-frequency tick data from exchange | ? |

- [ ] Fill in the best model for each

**Check yourself:**
10K HTTP connections: Java 21 virtual threads or NIO Selector.
Large file batch: buffered FileInputStream with large buffer.
Spring DB query: virtual threads (Java 21) or connection pool + blocking.
High-frequency tick: NIO non-blocking or io_uring.

---

### Challenge 6: IPC Selection

Match each use case to the correct IPC mechanism:

| Use Case | IPC Mechanism |
|---------|--------------|
| Spring app spawning shell script, reading output | ? |
| Two JVMs on same host sharing large byte buffer | ? |
| Nginx worker sending request to Java backend | ? |
| Audit events from multiple processes | ? |

**Check yourself:**
Shell script output: ProcessBuilder pipe.
Shared byte buffer: MappedByteBuffer / shared memory.
Nginx to Java: Unix domain socket or TCP socket.
Audit events: named pipe or message queue.

---

### Challenge 7: Diagnosis from Tools

Interpret these `vmstat 1` samples:

```
procs  memory   swap  io    system     cpu
r  b  swpd free  si so  bi bo  in  cs  us sy id wa
8  0   0  4096   0  0  10  5 1000 85000 82 15  0  3
8  0   0  4000   0  0  10  5 1000 85000 83 15  0  2
```

- [ ] What is causing the high cs (context switches)?
- [ ] What does r=8 with 4 cores suggest?
- [ ] Is there a memory problem?

**Check yourself:**
cs=85000/sec: too many threads context switching (likely
200+ threads for a 4-core machine). r=8 with 4 cores:
2x run queue depth, CPU-bound, adding threads won't help.
Memory: swpd=0, no swap in/out -> no memory problem.

---

### Challenge 8: Busy-Waiting Recognition

Identify the busy-wait and fix it:

```java
while (!queue.isEmpty() || !done) {
    Task t = queue.poll();
    if (t != null) process(t);
}
```

- [ ] What is wrong with this code?
- [ ] What CPU usage does it produce when queue is empty?
- [ ] Rewrite using the correct pattern

**Check yourself:**
Problem: when empty, loops doing nothing (busy-wait).
CPU usage: 100% on one core.
Fix: use BlockingQueue.take() (parks thread when empty).

---

### Scoring

| Score | Level |
|-------|-------|
| 8/8 | Working level confirmed - proceed to L3 |
| 6-7/8 | Review missed topics, retry |
| 4-5/8 | Re-read L2 entries (OSY-026 to OSY-044) |
| < 4/8 | Restart from L1 foundations (OSY-001 to OSY-025) |
