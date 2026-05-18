---
id: OSY-083
title: OS L3 Self-Assessment
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-054, OSY-059, OSY-061, OSY-065, OSY-068, OSY-070
used_by: []
related: OSY-082, OSY-084, OSY-112
tags:
  - self-assessment
  - practice
  - L3
  - quiz
  - mastery-check
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 83
permalink: /technical-mastery/osy/os-l3-self-assessment/
---

## TL;DR

Self-assessment for OS L3 mastery. 15 questions covering
virtual memory, lock-free, epoll, CFS, OOM, cache lines,
NUMA, zero-copy, and signals. Score yourself: 12-15 correct
= L3 mastery; < 10 = review the specific topics. These are
real interview questions at mid-senior level.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-083 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | self-assessment, L3, OS mastery, quiz, interview prep |
| **Prerequisites** | OSY-054, OSY-059, OSY-061, OSY-065, OSY-068, OSY-070 |

---

### Assessment Questions

**Q1: Virtual Memory**
You have a 4GB JVM process. `ps` shows VIRT=12GB but RSS=4.5GB.
Explain what each number means and why VIRT > RSS.

> **Answer:** VIRT = total virtual address space claimed: heap reservation
> (even if not used), JVM code+libs, thread stacks, metaspace, code cache,
> guard pages. RSS = pages actually in physical RAM. VIRT > RSS because
> Java heap is reserved (mmap'd) but pages are only allocated as objects
> are created and GC touches them. Also: JVM reserves space for potential
> growth (-Xmx) even if not using it.

---

**Q2: Cache Lines and False Sharing**
Two threads each increment their own `volatile long` counter.
Performance is terrible - only 100M increments/sec vs expected 1B/sec.
What's likely wrong and how do you fix it?

> **Answer:** False sharing. Both `volatile long` fields likely share
> a 64-byte cache line. Every increment from Thread A invalidates the
> cache line in Thread B's L1, and vice versa. Fix: use `@Contended`
> annotation with `-XX:-RestrictContended`, or manually pad 7 additional
> `long` fields after each counter. Better: use `LongAdder` which has
> built-in cell padding.

---

**Q3: epoll**
Compare `select()`, `poll()`, and `epoll()` for a server handling
50,000 concurrent connections. Which do you use and why?

> **Answer:** epoll. select() is limited to 1024 FDs. poll() has no
> FD limit but O(N) scan per call - 50K connections = 50K checks
> every poll cycle. epoll() registers FDs once (O(1) per registration)
> and returns only ready FDs (O(M) where M = active connections).
> For 50K connections with 1% active at once = epoll processes 500,
> not 50K. Use level-triggered for safety.

---

**Q4: CFS Scheduler**
Explain what `vruntime` is in CFS and why it exists.

> **Answer:** vruntime is each task's "virtual runtime" - how long
> the task HAS run, weighted by its priority (nice value). CFS always
> runs the task with the LOWEST vruntime (least served). Higher priority
> tasks accumulate vruntime more slowly (niceness adjustment via weight),
> so they naturally get more CPU time while maintaining global fairness.
> vruntime enables O(log N) selection via red-black tree with O(1) minimum.

---

**Q5: OOM Killer**
Your Redis server resets every night at 3am. Logs show nothing.
`dmesg | grep "Killed process"` shows the Redis process was killed.
Explain what happened and how to prevent it.

> **Answer:** OOM killer killed Redis. Redis uses BGSAVE (fork) for
> persistence. The fork() COW commit check plus memory growth at night
> exceeded available RAM. The OOM killer selected Redis (high RSS).
> Fix: 1) set `vm.overcommit_memory=1` so fork() always succeeds,
> 2) lower `oom_score_adj` for Redis to -500 so other processes die
> first, 3) ensure Redis has enough RAM headroom for BGSAVE amplification.

---

**Q6: Lock-Free Data Structures**
What is the ABA problem and when does it occur?

> **Answer:** ABA: Thread 1 reads pointer value A, gets pre-empted.
> Thread 2 changes A -> B -> A (value returns to A). Thread 1 resumes:
> CAS(A, A, newValue) succeeds even though data changed! This can cause
> use-after-free bugs in lock-free stacks/queues where node addresses
> are reused. Fix: AtomicStampedReference (adds version counter to CAS).

---

**Q7: NUMA**
Your application is running on a 2-socket server (2 NUMA nodes).
`numastat` shows 45% `other_node` accesses. What's happening
and what do you do?

> **Answer:** 45% of memory accesses are remote NUMA (cross-socket),
> adding ~2x memory latency for nearly half of all operations.
> Cause: Java heap allocated on Node 0 (startup thread on Node 0),
> but half of threads run on Node 1. Fix: `-XX:+UseNUMA` to interleave
> heap allocation per thread/region, or `numactl --interleave=all java`
> for even round-robin allocation across both nodes.

---

**Q8: Demand Paging**
You restart a Java service and the first request takes 10x longer
than normal. After the first request, latency is normal. Explain.

> **Answer:** Cold start page faults. JVM heap and code cache pages
> were evicted from RAM during restart (or weren't loaded yet).
> First request: JIT code execution + GC = many page faults
> (loading from disk/page cache). After first request: pages warm.
> Fix: `-XX:+AlwaysPreTouch` (touch all heap pages at startup),
> warm-up requests before sending production traffic, or keep at
> least one instance running during deploys (rolling update).

---

**Q9: Signals**
Your Java service receives SIGTERM but takes > 30 seconds to shut down.
Docker waits 10 seconds then sends SIGKILL. No graceful shutdown.
What went wrong and how do you fix it?

> **Answer:** JVM received SIGTERM which triggers shutdown hooks,
> but the hook is taking > 10s (Docker default timeout). Fix:
> 1) Inspect what shutdown hook is doing (JFR or thread dump at shutdown),
> 2) Add timeout to shutdown hook operations,
> 3) Increase Docker stop timeout: `docker stop --time 60 container`
> or in Kubernetes: `terminationGracePeriodSeconds: 60`.

---

**Q10: epoll Edge-Triggered**
You switched from level-triggered to edge-triggered epoll.
Now some clients randomly hang indefinitely. Explain why and the fix.

> **Answer:** Edge-triggered fires ONCE when new data arrives.
> If you read less than all available data (partial read), no new
> event fires until MORE data arrives - but that data may never come.
> The unread data causes a hang. Fix: with ET, you MUST read until
> EAGAIN (no more data) on every event. Use a non-blocking loop:
> `while ((n = read(fd, buf, size)) > 0) { process(buf, n); }
> if (errno == EAGAIN) return to epoll_wait;`

---

### Scoring

| Score | Level |
|-------|-------|
| 9-10 correct | L3 mastery; ready for senior-level OS interview questions |
| 7-8 correct | Good foundation; review the missed topics |
| < 7 correct | Review L3 entries before attempting L4 content |

---

### Quick Reference Card

| Topic | Key Entry |
|-------|----------|
| Virtual memory | OSY-054, OSY-055 |
| False sharing | OSY-060 |
| epoll | OSY-068 |
| CFS vruntime | OSY-065 |
| OOM killer | OSY-070 |
| ABA problem | OSY-061 |
| NUMA | OSY-058 |
