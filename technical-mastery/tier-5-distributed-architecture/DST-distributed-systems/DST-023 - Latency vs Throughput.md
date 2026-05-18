---
id: DST-023
title: Latency vs Throughput
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★☆☆
depends_on: DST-001, DST-005, DST-022
used_by: DST-060
related: DST-001, DST-005, DST-015, DST-022
tags:
  - distributed
  - performance
  - foundational
  - measurement
status: complete
version: 4
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Mastery"
nav_order: 23
permalink: /technical-mastery/distributed-systems/latency-vs-throughput/
---

⚡ TL;DR - Latency measures how long one operation takes;
throughput measures how many operations complete per second;
they are related but independent dimensions of system
performance that often trade off against each other, and
optimizing one without measuring the other leads to
misleading conclusions.

---

### 📋 Entry Metadata

| #023 | Category: Distributed Systems | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | The Distribution Problem, The Cost of Distribution, Load Balancing | |
| **Used by:** | Performance Trade-offs, Benchmarking | |
| **Related:** | The Cost of Distribution, Availability, Load Balancing | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A team optimizes their API for throughput by batching
requests together. Each batch waits 500ms to collect
requests before processing. Throughput improves from
10,000 to 50,000 req/s. The team declares success.
Users report the application feels slow. P99 latency
jumped from 50ms to 600ms. The team optimized throughput
without considering latency. A user-facing API needs
both. By measuring only throughput, they made the user
experience worse.

**THE CORE INSIGHT:**
Latency and throughput are both necessary measurements
of system performance, but they measure different things
and often conflict. An application may have excellent
throughput (processes many requests) but terrible latency
(each request takes a long time) - or vice versa. Without
measuring both in context, performance optimization is
incomplete.

---

### 📘 Textbook Definition

**Latency** is the time elapsed from when a request is
sent to when the response is received, measured for a
single operation. It is expressed in time units (ms, µs)
and typically reported as percentiles (P50, P95, P99,
P99.9) to capture the distribution of response times,
not just the average.

**Throughput** is the number of operations completed
per unit of time (requests per second, messages per
second, transactions per second). It measures the system's
capacity to handle volume.

**Little's Law** relates both: in a stable system,
the average number of requests in the system (L) equals
the average arrival rate (λ) times the average time
in the system (W): `L = λ × W`. A system processing
100 req/s with average latency of 200ms has on average
20 requests in-flight at any time.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Latency = how fast a single request completes; throughput
= how many requests complete per second. A fast postal
service (low latency) can still have low throughput if
only one truck runs. Many slow trucks (high throughput)
can still deliver late packages (high latency).

**The key numbers to always report:**
```
ALWAYS report: P50, P95, P99 latency + throughput (RPS)
NEVER report: average latency alone
WHY: average hides outliers; P99 reveals user experience
```

**Little's Law mental model:**
```
Throughput = Concurrency / Latency

If latency doubles: either concurrency must double
(more threads, more connections) to maintain throughput,
or throughput halves.
```

---

### 🔩 First Principles Explanation

**WHY AVERAGE LATENCY LIES:**

```
10 requests: [5ms, 5ms, 5ms, 5ms, 5ms,
              5ms, 5ms, 5ms, 5ms, 950ms]

Average: 101ms  ← misleading
P50:       5ms  ← typical experience
P99:     950ms  ← the one user who suffered

"Average latency is 101ms" masks that 10% of users
experienced 950ms. P99 = 950ms tells the truth.
```

**THE LATENCY-THROUGHPUT TRADE-OFF:**

Batching is the canonical example. Processing requests
individually minimizes latency (each processed immediately)
but limits throughput (sequential processing). Batching
requests increases throughput (process 100 at once) but
adds batching delay to every request (latency increases
by the batch wait time).

```
┌────────────────────────────────────────────────────────┐
│  NO BATCHING:                                          │
│  Latency:    10ms/request                             │
│  Throughput: 100 req/s (limited by processing speed)  │
│                                                        │
│  BATCHING (batch of 100, 50ms collection wait):        │
│  Latency:    50ms + 10ms = 60ms/request               │
│  Throughput: 10,000 req/s (100x improvement)           │
│                                                        │
│  TRADE-OFF: 6x worse latency, 100x better throughput  │
│                                                        │
│  CORRECT ANSWER: depends on the application's SLO     │
│  User-facing API: choose low latency                   │
│  Batch analytics: choose high throughput              │
└────────────────────────────────────────────────────────┘
```

**THE PERCENTILE IMPERATIVE:**

| Metric | What it tells you |
|---|---|
| P50 (median) | Half of requests are faster than this |
| P95 | 95% of requests are faster than this |
| P99 | 99% of users have latency below this |
| P99.9 ("three nines") | 99.9% of users are faster than this |

For a service handling 1,000,000 requests/day:
- P99 = 500ms means 10,000 requests/day experience 500ms+
- P99.9 = 500ms means 1,000 requests/day experience 500ms+

At high volume, even P99.9 failures affect many users.
Always optimize the latency percentile that matches the
number of affected users.

---

### 🧠 Mental Model / Analogy

> A highway has a speed limit (latency) and a capacity
> (throughput). Cars travel at 100km/h (latency = time
> to travel distance). The highway handles 5,000 cars
> per hour (throughput). Adding more lanes increases
> throughput without changing individual car speed
> (latency). A traffic jam increases latency for
> individual cars (queuing) and also reduces throughput.
> The highway is "saturated" when arrival rate exceeds
> capacity - latency and throughput both degrade.

**Saturation** is the key concept: when a system is near
saturation (at capacity), latency increases dramatically
while throughput plateaus. This is the "knee of the curve"
- the point where adding more load increases latency far
more than it increases throughput.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Latency is how long you wait for a response (one request).
Throughput is how many requests the system handles per
second. Both matter: a fast system that handles few
requests is not scalable; a system that handles many
requests but each takes a long time is not responsive.

**Level 2 - How to use it (junior developer):**
Always measure both when benchmarking. Use percentiles
(P50, P95, P99) for latency, not averages. Report
throughput as requests per second. When optimizing,
define which metric is the priority for the use case:
user-facing APIs optimize P99 latency; batch jobs
optimize throughput.

**Level 3 - How it works (mid-level engineer):**
The relationship: `Throughput = Concurrency / Latency`
(Little's Law). If a system has 100 concurrent requests
in flight and P50 latency is 100ms, throughput is 1,000
req/s. To double throughput without improving latency:
double concurrency (more threads, connections). To halve
latency without adding concurrency: reduce processing
time per request.

**Level 4 - Why it was designed this way (senior/staff):**
Latency percentiles map to different user experience
impacts. P99 latency corresponds to "the user who
occasionally has a bad day." P99.9 corresponds to "the
user who frequently has a bad experience (if they make
frequent requests)." For a user sending 10 requests
per page load, P99 latency will be experienced on every
page load (1 of 10 requests will be at P99 or worse).
This is why Google's RAIL model recommends targeting
P99 latency for interactive applications.

**Level 5 - Mastery (distinguished engineer):**
Gil Tene (Azul Systems) popularized the "coordinated
omission" problem in latency benchmarks. In most benchmark
tools, when the system is slow, the tool sends fewer
requests (because it waits for each response before
sending the next). This hides the queueing delay that
real users experience under load. Under real load,
requests queue up. A benchmark with coordinated omission
measures "how long did each request take when the system
was lightly loaded" not "how long did requests wait
AND process when the system was under load." HdrHistogram
and wrk2 are designed to avoid coordinated omission.

---

### ⚙️ Why It Holds True

**LITTLE'S LAW:**

$$L = \lambda \times W$$

Where:
- $L$ = average number of requests in the system
- $\lambda$ = average arrival rate (req/s)
- $W$ = average time in the system (latency)

This law applies to any stable queuing system. Implications:

1. If arrival rate (throughput) increases with latency
   held constant: more requests are in-flight. System
   needs more concurrency capacity.

2. If latency increases with arrival rate held constant:
   more requests accumulate in queue. Queue grows
   unboundedly unless bounded by rejection.

3. The "saturation point" is where L exceeds system
   capacity. After this point, latency grows rapidly
   while throughput plateaus - because additional
   requests wait in queue.

**THE LATENCY COMPONENTS:**

```
Total Latency = Queueing Latency + Processing Latency
                + Network Latency + Serialization Latency

Under load: Queueing Latency dominates
At rest:    Processing + Network + Serialization dominate

Optimization target changes based on load level:
  Low load:  reduce processing time (algorithm, caching)
  High load: reduce queueing (more concurrency,
    backpressure)
```

---

### 💻 Code Example

**Measuring Latency Correctly (Wrong vs Right)**

```python
# BAD: Measuring average latency
import time
import requests

def benchmark_average(url: str, iterations: int) -> float:
    total = 0
    for _ in range(iterations):
        start = time.perf_counter()
        requests.get(url)
        total += time.perf_counter() - start
    return total / iterations  # AVERAGE - hides outliers

# Example output: "average latency: 45ms"
# Hides: P99 may be 800ms, skewing averages
```

```python
# GOOD: Measure latency with percentiles
import time
import requests
import statistics

def benchmark_percentiles(
    url: str,
    iterations: int
) -> dict:
    latencies = []
    for _ in range(iterations):
        start = time.perf_counter()
        requests.get(url)
        latencies.append(
            (time.perf_counter() - start) * 1000  # ms
        )

    latencies.sort()
    n = len(latencies)
    return {
        "p50_ms":   latencies[int(n * 0.50)],
        "p75_ms":   latencies[int(n * 0.75)],
        "p95_ms":   latencies[int(n * 0.95)],
        "p99_ms":   latencies[int(n * 0.99)],
        "p999_ms":  latencies[int(n * 0.999)],
        "min_ms":   latencies[0],
        "max_ms":   latencies[-1],
        "mean_ms":  statistics.mean(latencies),
        # Report mean last and never use it for decisions
    }

# Example output:
# p50:  12ms, p95: 45ms, p99: 180ms, p99.9: 850ms
# This tells you: 1% of users wait 180ms+, 0.1% wait 850ms+
```

**Latency-Throughput Trade-off in Practice**

```python
# Trade-off example: database batch writes
# Individual inserts: low latency, low throughput
# Batch inserts: higher latency, much higher throughput

class DatabaseWriter:
    def write_immediate(self, record: dict) -> None:
        """
        Latency: ~5ms (one DB round trip)
        Throughput: ~200 writes/s (bottleneck: DB IOPS)
        Use for: user-facing writes requiring confirmation
        """
        db.execute("INSERT INTO events ...", record)
        db.commit()  # Wait for durability confirmation

    def write_batched(
        self,
        records: list[dict],
        batch_size: int = 500
    ) -> None:
        """
        Latency: 5ms + batch_wait (50-500ms)
        Throughput: ~50,000 writes/s (pipeline to DB)
        Use for: analytics events, logs, non-critical data
        """
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            db.executemany("INSERT INTO events ...", batch)
        db.commit()  # One commit for entire batch
```

---

### ⚖️ Comparison Table

| Metric | Unit | Use When Optimizing For |
|---|---|---|
| **P50 (Median)** | ms | Typical user experience |
| **P95** | ms | Most users' experience |
| **P99** | ms | SLA definition, user-facing APIs |
| **P99.9** | ms | Tail latency, high-request-rate users |
| **Throughput** | req/s | System capacity, batch processing |

| Trade-off Pattern | Latency | Throughput | Use Case |
|---|---|---|---|
| Individual processing | Low | Limited | User-facing, real-time |
| Batching | Higher | Much Higher | Analytics, bulk processing |
| Caching | Very Low | Very High | Read-heavy workloads |
| Synchronous replication | Higher | Same | Durability guarantees |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Average latency is a good metric" | Average latency hides outliers. P99 latency tells you what most users actually experience. Always use percentiles. |
| "High throughput means good performance" | A system can have high throughput (many requests/second) with terrible latency (each takes 10 seconds). The user experience is poor. Measure both. |
| "Latency and throughput always trade off" | At low load, improving processing efficiency reduces latency AND increases throughput. The trade-off is specific to architectures like batching, not universal. |
| "Optimizing P50 is sufficient" | For a service handling 10M requests/day, P99 failures = 100,000 users/day having bad experiences. At scale, P99 and P99.9 matter enormously. |

---

### 🚨 Failure Modes & Diagnosis

**Latency Spike Under Load (Saturation)**

**Symptom:** At 5,000 req/s, P99 latency is 50ms.
At 8,000 req/s, P99 latency jumps to 2,000ms. At 10,000
req/s, the service starts dropping requests entirely.

**Root Cause:** System is saturated. The thread pool
(or connection pool, or CPU) is fully utilized. Additional
requests queue. Queue grows linearly. Queuing delay
dominates latency at saturation.

**Diagnosis:**
```bash
# Check thread pool saturation (Spring Boot):
curl http://service/actuator/metrics/executor.pool.size
curl http://service/actuator/metrics/executor.active
# If active ≈ pool size: saturated

# Check JVM GC pause impact on latency spikes:
jstat -gcutil <pid> 1000 30 | awk '{print $6,$7}'
# YGCT + FGCT: GC time. Spikes = GC causing latency spikes

# Calculate service utilization:
# If avg latency = 10ms, concurrency = 100 threads
# Throughput at saturation = 100 / 0.010 = 10,000 req/s
# Service saturates at 10,000 req/s
```

**Fix:** Add backpressure (reject requests when queue
is full rather than letting latency grow unboundedly).
Increase pool size proportionally. Profile to find
processing bottleneck and reduce average latency.

---

### 🔗 Related Keywords

**Prerequisites:**
- `The Distribution Problem`, `The Cost of Distribution`, `Load Balancing`

**Builds On This:**
- Performance benchmarking, capacity planning, SLO definition

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ LATENCY      │ Time per single request (ms)             │
│ THROUGHPUT   │ Requests completed per second (req/s)    │
├──────────────┼──────────────────────────────────────────┤
│ MEASURE      │ Percentiles (P50, P95, P99), never avg   │
├──────────────┼──────────────────────────────────────────┤
│ LITTLE'S LAW │ Throughput = Concurrency / Latency       │
├──────────────┼──────────────────────────────────────────┤
│ TRADE-OFF    │ Batching: worse latency, better throughpu│
│              │ Caching: better both (under cache hit)   │
│              │ Sync replication: worse latency, durable │
├──────────────┼──────────────────────────────────────────┤
│ SATURATION   │ When utilization → 100%: latency spikes  │
│              │ Add backpressure before this point       │
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "Report P99 latency AND throughput.      │
│              │  Average lies; percentiles reveal."      │
└─────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

The latency/throughput distinction applies everywhere
in computing: disk I/O (seek time vs bandwidth), network
(RTT vs bandwidth), CPU (clock speed vs instruction
throughput). The universal pattern: latency measures
the cost of one unit of work; throughput measures the
rate of work completion. They are related (via Little's
Law at the system level) but independently optimizable.
Always specify which you are optimizing for.

---

### 💡 The Surprising Truth

Jeff Dean (Google) documented the "tail latency amplification"
problem in 2013: a service making 100 parallel requests
to backend services experiences the P99 latency of the
SLOWEST backend, not the typical backend. If each backend
has P99 = 10ms, the parallel call has P99 = 10ms (the
slowest). But if each has P99.9 = 100ms, the parallel
call's P99 is: 1 - (1 - 0.001)^100 = 9.5% chance that
at least one backend is slow. The parallel call's P90
becomes the individual backend's P99.9. This is why Google
introduced "hedged requests": send the same request to
two backends, take the first response, cancel the second.
This trades a small throughput overhead for dramatically
reduced tail latency in parallel fan-out architectures.

---

### ✅ Mastery Checklist

1. [MEASURE] Implement a latency benchmark using percentiles
   (P50, P95, P99) and calculate what P99 means in terms
   of users affected at your service's request rate.
2. [APPLY] Use Little's Law to calculate required concurrency
   given a target throughput of 5,000 req/s and measured
   P99 latency of 200ms.
3. [DECIDE] Given a data pipeline requiring 100x throughput
   improvement and acceptable 200ms additional latency,
   determine if batching is the right solution.
4. [DEBUG] P99 latency spikes to 2 seconds at 70% load
   while P50 remains normal. Identify whether this is
   a GC pause, thread saturation, or database bottleneck.
5. [EXPLAIN] Why tail latency amplification is the primary
   performance concern in fan-out microservice architectures,
   and two mitigation strategies.
