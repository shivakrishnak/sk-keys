---
id: SYD-005
title: Latency vs Throughput
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★☆
depends_on: SYD-002
used_by: SYD-008, SYD-014, SYD-026, SYD-027
related: SYD-002, SYD-026, SYD-008
tags:
  - performance
  - intermediate
  - architecture
  - mental-model
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Mastery"
nav_order: 5
permalink: /technical-mastery/syd/latency-vs-throughput/
---

⚡ TL;DR - Latency is how long one request takes; throughput
is how many requests complete per second - and the two are
in fundamental tension: optimizing one often degrades the other.

| #005 | Category: System Design | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Non-Functional Requirements | |
| **Used by:** | Load Balancing, Auto Scaling, Back-of-Envelope Estimation, Capacity Planning | |
| **Related:** | Non-Functional Requirements, Back-of-Envelope Estimation, Load Balancing | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A team is building a real-time bidding platform. The product
manager says: "make it fast and handle lots of traffic."
The engineering team optimizes for response time: they add
a cache for each user, pre-compute bids, and use synchronous
processing. Response time drops to 5ms per request. But
at 50,000 concurrent users, the system collapses - the
synchronous processing model and per-user caching use too
much memory and CPU per request to sustain high concurrency.
Alternatively, another team optimizes for throughput: they
batch requests, add queues, and use async processing.
Throughput climbs to 200,000 requests/second, but now each
bid request takes 200ms instead of 5ms - too slow for
real-time bidding.

**THE BREAKING POINT:**
Without a framework for understanding the latency-throughput
tension, engineers optimize for whichever metric is measured
that week, inadvertently degrading the other. Systems designed
to be "fast" often cannot scale. Systems designed to be
"high-throughput" are often too slow for interactive use.

**THE INVENTION MOMENT:**
This is exactly why latency and throughput must be defined
and optimized as separate, explicitly traded-off properties.
They are not the same thing. They often conflict. The
architecture must declare which matters more - or how to
satisfy both within defined boundaries.

**EVOLUTION:**
In single-machine systems, latency and throughput were
correlated: a faster CPU served each request faster AND
served more requests per second. Distributed systems
severed this correlation. Adding more servers (scale-out)
improves throughput dramatically but does not reduce the
latency of any individual request. Conversely, adding a
cache (reduce latency) can hurt throughput if cache
contention becomes a bottleneck. These trade-offs became
a core part of distributed systems design in the 2000s.

---

### 📘 Textbook Definition

**Latency** is the time elapsed from when a request is
initiated to when a response is received, typically measured
as percentiles (p50, p95, p99) rather than averages,
because high percentiles capture the tail behavior that
most affects user experience. **Throughput** is the number
of requests completed per unit time, typically expressed
as requests per second (RPS). They are related by Little's
Law: L = λ × W, where L is the number of requests in the
system (concurrency), λ is the arrival rate (throughput),
and W is the average time in the system (latency). At
constant concurrency, reducing latency increases throughput;
increasing throughput without adding capacity increases
latency.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Latency is how fast one request finishes; throughput is
how many requests finish per second - knowing which matters
more for your product determines your architecture.

**One analogy:**
> A highway vs a sports car. A single sports car (low
> latency) gets from A to B in 30 minutes. A highway
> with 8 lanes and 10,000 cars (high throughput) moves
> far more people per hour, even though each individual
> car might take longer due to traffic. You cannot turn
> a highway into a sports car. They solve different problems.

**One insight:**
Most user-facing systems need both to be bounded: latency
must be below a threshold (< 300ms) AND throughput must
exceed a minimum (> 5,000 RPS). The architecture must
satisfy both simultaneously, which requires understanding
where they conflict and how to balance them.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. **Little's Law:** Concurrency = Throughput × Latency.
   At fixed concurrency, lower latency → higher throughput.
   At fixed latency, more concurrent capacity → higher
   throughput. You cannot violate this relationship.
2. Latency has a physical floor: the speed of light in
   fiber plus the minimum processing time. Below some
   threshold, you cannot go faster regardless of cost.
3. Throughput scales with resources (more servers =
   more throughput) but latency does not scale with
   resources (more servers does not make one request faster).

**DERIVED DESIGN:**
Given Little's Law and the resource scaling properties:
- To improve latency: reduce processing time per request
  (caching, algorithmic optimization, co-location of
  data with compute)
- To improve throughput: add capacity (horizontal scaling,
  queueing to absorb bursts, parallelism)
- To satisfy BOTH within bounds: define the acceptable
  latency target first, then scale capacity to meet
  the throughput target within that latency budget

**THE TRADE-OFFS:**

**Gain:** Explicit separation of latency and throughput
requirements leads to architectures that satisfy both.

**Cost:** Most optimizations target one or the other;
satisfying both requires more complex architectures
(async processing with tight SLAs, admission control).

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

**Essential:** Little's Law is inescapable. At fixed
concurrency, you cannot independently improve both
latency and throughput without adding capacity.

**Accidental:** Many systems conflate latency and
throughput requirements, leading to architectures that
accidentally optimize one at the expense of the other.

---

### 🧪 Thought Experiment

**SETUP:**
A database server processes 100 requests/second. Each
request takes 10ms. The server has capacity for 1
concurrent request (unrealistic but illustrative).
Concurrency = 100 × 0.01 = 1 (Little's Law).

**EXPERIMENT 1 - Reduce latency:**
You optimize queries. Now each request takes 5ms.
At same concurrency (1): throughput = 1 / 0.005 = 200 RPS.
Latency improvement doubled throughput at zero hardware cost.

**EXPERIMENT 2 - Increase throughput via scaling:**
You add a second identical server. Now concurrency = 2.
Throughput = 2 / 0.01 = 200 RPS.
Latency is unchanged at 10ms per request.
Throughput doubled but individual requests are no faster.

**EXPERIMENT 3 - The conflict:**
The business wants p99 latency < 5ms AND 1000 RPS.
At 5ms latency, one server handles 200 RPS.
To reach 1000 RPS at 5ms: need 5 servers minimum.
Little's Law: 5 servers × (1000/5) × 0.005 = 5 concurrent.

**THE INSIGHT:**
Latency and throughput scale independently. Reducing
latency multiplies throughput per server. Meeting
throughput targets requires sizing capacity based on
both the target throughput and the target latency.

---

### 🧠 Mental Model / Analogy

> Think of a coffee shop. Latency = how long it takes
> for ONE customer to get their coffee (order to drink
> in hand). Throughput = how many customers get coffee
> per hour. A barista who makes perfect coffee in 2
> minutes has lower latency but lower throughput than
> a barista who makes standard coffee in 1 minute.
> Two baristas have twice the throughput; neither
> individual customer gets served faster.

- "Time to get coffee" → latency (per-request metric)
- "Customers served per hour" → throughput (system metric)
- "Adding a barista" → horizontal scaling (adds throughput)
- "Faster coffee machine" → vertical scaling + optimization
  (reduces latency, improves both)
- "Pre-made coffee waiting" → caching (dramatically reduces
  latency AND increases throughput at cost of freshness)
- "Queue out the door" → queue depth / backpressure
  (throughput demand exceeds capacity)

**Where this analogy breaks down:**
A coffee shop's queue has physical limits (customers leave).
Software queues can grow unbounded, causing OOM errors
rather than natural backpressure.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Latency is the speed of one thing. Throughput is the
volume of things. A slow but popular restaurant has
high latency (long waits) but high throughput
(serves 500 people per night). Understanding both matters.

**Level 2 - How to use it (junior developer):**
When defining system requirements, write both metrics:
"p99 API latency < 300ms AND system must handle 5,000
requests/second." Measure both in production. Add a
cache to improve latency. Add servers to improve
throughput. They require different interventions.

**Level 3 - How it works (mid-level engineer):**
Use Little's Law to reason about capacity: if your
target latency is 100ms and target throughput is
10,000 RPS, you need at least 10,000 × 0.1 = 1,000
concurrent request slots. If each server handles
100 concurrent requests, you need 10 servers minimum.
This is the math-first approach to capacity planning.

**Level 4 - Why it was designed this way (senior/staff):**
The latency-throughput trade-off manifests in every
layer of a distributed system. A database with strong
consistency has higher write latency (due to replication
coordination) and lower write throughput (serialization
through the primary). A database with eventual
consistency has lower write latency (writes return
immediately) and higher write throughput (writes
fan out to replicas asynchronously). The consistency
model is a latency-throughput trade-off.

**Level 5 - Mastery (distinguished engineer):**
At scale, the latency distribution changes: p50 may
be 50ms, but p99 may be 2000ms (40x higher). This
"tail latency" is caused by resource contention,
garbage collection, queue scheduling, and network
jitter. Tail latency at scale is not fixed by hardware -
it is a queue theory problem. At very high throughput
(>70% CPU utilization), queuing theory predicts
explosive latency increase (the "knee" of the
utilization curve). Elite systems run at 30-50% peak
capacity to maintain tail latency SLOs.

---

### ⚙️ How It Works (Mechanism)

**Little's Law applied:**

```
L = λ × W

Where:
  L = average number of requests in the system
      (concurrency / queue depth)
  λ = arrival rate (throughput in requests/second)
  W = average time in the system (latency in seconds)

Examples:
  10 RPS × 0.1s latency = 1 concurrent request
  1000 RPS × 0.5s latency = 500 concurrent requests
  10000 RPS × 0.1s latency = 1000 concurrent requests
```

**The utilization curve:**

```
┌────────────────────────────────────────────────┐
│ LATENCY vs UTILIZATION (USL Model)             │
│                                                │
│ Latency                                        │
│   ^                                            │
│   │                            ╭──── explosive │
│   │                         ╭──╯               │
│   │                    ╭────╯                  │
│   │               ╭────╯                       │
│   │          ╭────╯                            │
│ ──┼──────────╯──────────────────────────►      │
│   0%  20%  40%  60%  80%  100%  Utilization    │
│                  ↑                             │
│             "knee" - latency starts climbing   │
│             steeply above ~70% utilization     │
│                                                │
│ Implication: Don't run systems above 70% CPU   │
│ utilization if latency SLOs must be met        │
└────────────────────────────────────────────────┘
```

**Latency percentiles (why median is misleading):**

```
Imagine 100 requests with these response times:
  p50 = 50ms  (50 fastest requests took ≤50ms)
  p75 = 150ms
  p90 = 300ms
  p95 = 800ms
  p99 = 2000ms
  p999 = 8000ms

The average is ~120ms. But 1% of users wait 2 seconds
and 0.1% wait 8 seconds. For a page with 10 API calls,
the probability of hitting at least one p999 request:
  1 - (1-0.001)^10 = ~1% of page loads are very slow.

This is why services should optimize for p99, not mean.
The mean hides the users having terrible experiences.
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW (measuring both metrics):**
```
[User Request]
  → [LB] (adds ~1ms latency, absorbs throughput)
  → [App Server Pool] ← YOU ARE HERE
     │ Latency: processing time per request
     │ Throughput: concurrency / latency (per server)
  → [Cache] (reduces latency, increases effective
              throughput dramatically)
  → [Database] (highest latency component, limits
                 total throughput)
  → [Response]

Total latency = sum of each component's processing time
Total throughput = min(each component's throughput)
```

**FAILURE PATH:**
```
Database at 95% utilization
  → Latency climbs exponentially (utilization knee)
  → Requests queue in app server connection pool
  → Connection pool exhausted
  → App server returns 503 to LB
  → LB removes overloaded app server (makes it worse)
  → Cascade collapse
```

**WHAT CHANGES AT SCALE:**
At 10x scale, the utilization curve becomes dominant.
A system designed at 30% utilization that now runs at
90% sees 10x latency increase without any code changes.
At 100x, queue theory predicts the system collapses.
The only fix is adding capacity before hitting the knee.

---

### 💻 Code Example

**Example 1 - BAD: Measuring only average latency**
```java
// BAD: Average latency hides tail behavior.
// A cache miss that takes 2s doesn't affect
// the average much but ruins 1% of user sessions.
@Timed(name = "api.request", description =
    "Average request time")  // wrong metric
public Response handleRequest(Request req) {
    return process(req);
}
```

**Example 2 - GOOD: Percentile-based latency monitoring**
```java
// GOOD: Track histogram for percentile analysis.
// Prometheus histogram gives p50/p95/p99 for free.
@Timed(
    name = "api.request.duration",
    description = "Request duration histogram",
    histogram = true,  // enables percentile buckets
    percentiles = {0.5, 0.95, 0.99, 0.999}
)
public Response handleRequest(Request req) {
    return process(req);
}
// Prometheus query for p99:
// histogram_quantile(0.99,
//   rate(api_request_duration_seconds_bucket[5m]))
```

**Example 3 - Production: Admission control**
```java
// GOOD: When throughput demand exceeds capacity,
// fail fast with 429 rather than letting latency
// climb to unacceptable levels.
// This trades throughput (some requests rejected)
// for latency (accepted requests stay within SLO).
@Component
public class AdmissionController {

    private final Semaphore concurrencyLimit;

    public AdmissionController(
            @Value("${max.concurrent.requests:1000}")
            int maxConcurrent) {
        this.concurrencyLimit =
            new Semaphore(maxConcurrent);
    }

    public <T> T execute(Supplier<T> operation)
            throws CapacityExceededException {
        // Try to acquire slot without blocking
        if (!concurrencyLimit.tryAcquire()) {
            // Shed load: fail fast, protect p99
            throw new CapacityExceededException(
                "System at capacity, retry later");
        }
        try {
            return operation.get();
        } finally {
            concurrencyLimit.release();
        }
    }
}
```

**Example 4 - Failure: Throughput-latency collapse**
```
# Scenario: Database at 85% CPU utilization
# Each query takes 100ms normally

# Under load (queueing theory): at 85% utilization,
# expected latency = base_latency / (1 - utilization)
# = 100ms / (1 - 0.85) = 667ms (6.7x increase)

# At 95% utilization: 100ms / 0.05 = 2000ms (20x)
# At 99% utilization: 100ms / 0.01 = 10000ms (100x)

# This is why: run production at max 60-70% utilization
# and alert at 70% to add capacity before hitting the knee.
```

---

### ⚖️ Comparison Table

| Optimization | Latency Impact | Throughput Impact | Cost | Best For |
|---|---|---|---|---|
| **Caching** | **Major reduction** | **Major increase** | Memory | Read-heavy workloads |
| Horizontal scaling | None | Proportional increase | Hardware | Throughput-bound systems |
| Query optimization | Major reduction | Moderate increase | Eng time | DB-bound systems |
| Async processing | Hides latency (queued) | Major increase | Complexity | Decoupled write paths |
| Admission control | Protects p99 | Reduces effective | Complexity | SLO-sensitive services |

**How to choose:**
Cache when reads dominate (90%+ of operations are reads
of cacheable data). Horizontal scale when CPU or memory
is the bottleneck and request processing is stateless.
Async processing when write latency can be deferred.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| More servers reduce latency | Horizontal scaling increases throughput; it does not reduce individual request latency. A request to a single server takes the same time regardless of how many total servers exist. |
| Average latency is the right metric | p99 latency is almost always the right target. Average hides the tail where users are suffering. |
| High throughput means fast system | A system processing 100,000 RPS with p99 of 5 seconds is high-throughput but unusable for interactive users |
| Latency and throughput are always in conflict | They conflict at high utilization. At low utilization, improving latency (e.g., better algorithm) also improves throughput. |
| Adding a queue always improves latency | Queuing hides latency (request returns immediately) but the actual processing still happens. The queue adds latency to processing; it just changes when the client sees it |

---

### 🚨 Failure Modes & Diagnosis

**Throughput Collapse at Utilization Knee**

**Symptom:**
System appears healthy at moderate load. At a specific
traffic level (often during peak hours), p99 latency
jumps from 200ms to 5 seconds with no deployment change.
Error rates climb as timeouts fire.

**Root Cause:**
CPU or database utilization crossed the 70-80% threshold.
Queuing theory predicts exponential latency increase
above this threshold. The system hit the utilization
knee and is now in queue collapse.

**Diagnostic Command:**
```bash
# Check CPU utilization trend vs latency trend
kubectl top pods --sort-by=cpu -n production

# Prometheus: correlate CPU utilization with p99
# Look for the "knee" in the correlation
promtool query range \
  '
  rate(container_cpu_usage_seconds_total[5m])
  /
  (kube_pod_container_resource_limits{resource="cpu"})
  '

# Check connection pool saturation (common bottleneck)
# HikariCP metrics
curl http://app:8080/actuator/metrics/hikaricp.connections.active
```

**Fix:**
Add capacity immediately to drop utilization below
70%. In the medium term, set auto-scaling threshold
to 60% CPU so new instances are added before hitting
the knee.

**Prevention:**
Set auto-scaling trigger at 60% utilization, not 80%.
Run load tests to identify the utilization knee for
your specific system.

---

**Tail Latency from Garbage Collection**

**Symptom:**
p50 latency is 50ms, p95 is 200ms, p99 is 2000ms.
The spikes correlate with 2-second gaps that appear
regularly in the GC logs.

**Root Cause:**
Stop-the-world GC pauses are affecting the p99 latency
tail. All threads pause during GC; requests queued
during the pause are served immediately after but
with the GC pause added to their latency.

**Diagnostic Command:**
```bash
# Enable GC logging
java -Xlog:gc*:file=gc.log:time,uptime:filecount=5,\
filesize=20m ...

# Analyze GC pause distribution
grep "Pause" gc.log | \
  awk '{print $NF}' | \
  sort -n | \
  awk 'NR%int(NR/10)==0'

# Check G1GC pause targets vs actual
jstat -gcutil <pid> 1000 20
```

**Fix:**
Tune G1GC max pause target: `-XX:MaxGCPauseMillis=200`.
Increase heap to reduce GC frequency. Profile allocation
to find and fix allocation hot spots. Consider ZGC
or Shenandoah for sub-millisecond pauses.

**Prevention:**
Measure p99 latency in load tests. If p99 >> p95,
investigate GC pauses as the root cause.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Non-Functional Requirements` - latency and throughput
  are the two most operationally critical NFRs

**Builds On This (learn these next):**
- `Back-of-Envelope Estimation` - uses throughput to
  calculate required server count
- `Load Balancing` - distributes load to keep each
  server below the utilization knee
- `Auto Scaling` - adds capacity when throughput demand
  approaches the utilization knee
- `Capacity Planning` - the formal process for sizing
  based on latency and throughput targets

**Alternatives / Comparisons:**
- `Availability` - orthogonal NFR: a system can be highly
  available but have terrible latency and throughput

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Latency = time per request               │
│              │ Throughput = requests per second         │
├──────────────┼──────────────────────────────────────────┤
│ PROBLEM IT   │ Optimizing one without awareness of the  │
│ SOLVES       │ other causes systems that are fast but   │
│              │ can't scale, or scalable but too slow    │
├──────────────┼──────────────────────────────────────────┤
│ KEY INSIGHT  │ Little's Law: Concurrency = Throughput x │
│              │ Latency. At fixed concurrency, lower     │
│              │ latency directly increases throughput.   │
├──────────────┼──────────────────────────────────────────┤
│ USE WHEN     │ Always define both metrics before        │
│              │ designing any user-facing service        │
├──────────────┼──────────────────────────────────────────┤
│ AVOID WHEN   │ N/A - both always matter; understand the │
│              │ priority order for your specific product │
├──────────────┼──────────────────────────────────────────┤
│ ANTI-PATTERN │ Using average latency as the SLO metric -│
│              │ p99 is the metric that reflects user pain│
├──────────────┼──────────────────────────────────────────┤
│ TRADE-OFF    │ Low latency (fast per-request) vs high   │
│              │ throughput (many requests per second)    │
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "Horizontal scaling buys throughput.     │
│              │  Optimization buys latency. Know which   │
│              │  you need before buying anything."       │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Load Balancing → Auto Scaling → Capacity │
│              │ Planning                                 │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Latency = per-request speed. Throughput = volume per
   second. Adding servers increases throughput, not latency.
2. Measure p99, not average. Average hides the 1% of users
   having terrible experiences. Design for p99.
3. Above 70% utilization, latency climbs exponentially.
   Size capacity to stay below the knee.

**Interview one-liner:**
"Latency is how long one request takes; throughput is
how many requests per second the system handles. They're
related by Little's Law. Caching reduces latency AND
increases throughput. Horizontal scaling increases
throughput but doesn't reduce latency. Always define
both separately and measure p99, not mean."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Speed per unit and volume per unit of time are
independent properties that must be optimized
independently. This distinction appears everywhere:
a factory's cycle time (latency) and units per hour
(throughput) require different interventions. A hospital's
average patient wait time (latency) and patients treated
per day (throughput) are addressed by different changes
(better triage = latency; more staff = throughput).
Confusing the two leads to the wrong intervention.

**Where else this pattern appears:**
- **Database design** - index design reduces read latency;
  connection pooling increases read throughput. They solve
  different bottlenecks.
- **Network design** - bandwidth (throughput) and round-
  trip time (latency) are independent. High bandwidth
  does not reduce the speed-of-light delay for a request
  to a server 200ms away.
- **Supply chain** - lead time (latency from order to
  delivery) vs production volume per day (throughput)
  are solved by different interventions: closer
  warehouses vs more production lines.

**Industry applications:**
- **Financial trading** - high-frequency trading requires
  both: sub-millisecond latency for competitive advantage
  AND high throughput for portfolio-level decisions.
  These require specialized hardware (FPGA) and software
  (lock-free data structures) that serve both needs.
- **Content delivery** - CDNs optimize for both:
  edge caching reduces latency (serve from nearby node),
  content sharding increases throughput (multiple origin
  servers handle parallel requests).

---

### 💡 The Surprising Truth

Google found in 2006 that a 500ms increase in search
results latency caused a 20% decrease in traffic.
Amazon found that every 100ms of latency cost them 1%
in sales. These numbers, when published, changed how
the entire industry thought about latency. But the
counterintuitive flip side: Google also discovered that
aggressively optimizing p50 latency while ignoring p99
led to user churn concentrated in the slowest users -
often the highest-value users on the worst connections
(mobile, rural). The users with the worst p99 latency
had the most to gain from improvements, and they were
disproportionately churning. Optimizing average latency
helped the median user while the tail latency (p99)
continued to drive away the most affected users. The
insight: p99 latency is a proxy for which users the
product is failing, not just which requests are slow.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. [EXPLAIN] Use Little's Law to calculate the number
   of servers needed given a target throughput and
   latency, and explain why adding servers increases
   throughput but not individual request latency.
2. [DEBUG] Given a production latency histogram showing
   p50=50ms, p99=2000ms, explain three possible root
   causes and describe the diagnostic command for each.
3. [DECIDE] A team asks: "should we add more servers
   or optimize the slow database query to handle
   10x more traffic?" Use latency-throughput reasoning
   to answer correctly and explain the trade-off.
4. [BUILD] Add a Prometheus histogram and p99 SLO alert
   to a service you own. Define the alert threshold and
   justify it based on user experience requirements.
5. [EXTEND] Apply Little's Law to a physical system
   (a DMV, a hospital ER) to calculate the concurrency
   required for target throughput and latency. Identify
   which bottleneck is the throughput constraint.

---

### 🧠 Think About This Before We Continue

**Q1.** A payment service has p50 latency of 50ms and
p99 latency of 8 seconds. The team optimizes the
database query and reduces p50 to 30ms. The p99 is
unchanged. What does this tell you about the root
cause of the p99 latency, and what kind of investigation
should you do next?

*Hint: If optimizing the most common code path does
not move p99, the p99 events are caused by something
else entirely - not the common path. Think about what
causes rare, very slow events: GC pauses, lock
contention, external service timeouts, retry storms.*

**Q2.** At 1 million requests/second with p99 latency
of 100ms, calculate the minimum concurrency using
Little's Law. If each server handles 1,000 concurrent
requests, how many servers are needed? Now add the
constraint that servers should run at max 70% utilization
- how does that change the server count?

*Hint: L = λ × W. Then servers = concurrency / server_concurrency.
Then add the utilization margin. The final number will
be larger than the naive calculation by roughly 1.4x.*

**Q3 (Hands-On):** Take a service you work on. Without
changing any code, observe: what is the current p50,
p95, and p99 latency? What is the current throughput
(requests/second)? Using Little's Law, calculate the
implied concurrency. Does that match your actual
connection pool size? If not, what does the mismatch
tell you about your system's bottleneck?

*Hint: If implied concurrency > connection pool size,
your connection pool is undersized and requests are
queuing. If implied concurrency << connection pool size,
you have excess capacity. The math reveals which
resource is the actual constraint.*

---

### 🎯 Interview Deep-Dive

**Q1: How do you determine whether a system is latency-
bound or throughput-bound, and what is the fix for each?**
*Why they ask:* Tests whether the candidate can diagnose
performance problems and prescribe the correct solution.
*Strong answer includes:*
- Latency-bound: p99 latency violates SLO even at low
  traffic. Fix: cache, query optimization, co-location,
  CDN for static assets
- Throughput-bound: p50 latency is fine but server
  CPU/memory maxes out at X RPS. Fix: horizontal
  scaling, stateless design to enable it
- How to tell: load test at increasing RPS. If latency
  stays flat until utilization knee, throughput-bound.
  If latency is high even at 10% utilization, latency-bound.

**Q2: A system has p50 = 50ms but p99 = 3 seconds.
What are the most likely root causes, in priority order,
and how would you diagnose each?**
*Why they ask:* Tests understanding of tail latency and
diagnostic methodology.
*Strong answer includes:*
- GC pauses: check GC logs for pause duration and frequency
- Database slow queries: check slow query log, look for
  queries that appear only at p99 (e.g., full table scans
  on missing indexes for rare queries)
- External service timeouts: check dependent service p99
  latency; the caller's p99 = dependent service's p99
- Lock contention: check for thread pool saturation or
  synchronized method contention

**Q3: How does the decision between synchronous and
asynchronous processing affect latency and throughput
trade-offs?**
*Why they ask:* Tests architectural reasoning about
the sync/async design pattern and its trade-offs.
*Strong answer includes:*
- Synchronous: client waits for result. Latency is
  total processing time. Throughput is bounded by
  concurrency limit / processing time.
- Asynchronous: client receives acknowledgement
  immediately. Perceived latency is tiny. Actual
  processing latency is decoupled from user experience.
  Throughput scales with worker count independently.
- The choice: interactive operations requiring results
  (search, checkout) need sync. Background operations
  (email, report generation, image processing) benefit
  from async because users don't need to wait.
- Risk of async: the queue can grow unbounded if
  consumers can't keep up. Need backpressure.
