---
id: OSY-142
title: Resource Starvation to Queuing Theory
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-085, OSY-141
used_by: []
related: OSY-140, OSY-141, OSY-143
tags:
  - queuing-theory
  - starvation
  - Little's-Law
  - connection-pool
  - Erlang-C
  - META
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 142
permalink: /technical-mastery/osy/resource-starvation-queuing-theory/
---

## TL;DR

OS resource starvation is queuing theory made concrete. When
more requests arrive than can be processed, a queue forms.
Little's Law (N = L * W) governs this in every system -
from thread pool queues to database connection pools to API
gateway queues. Understanding queuing theory turns "system
is slow" from guesswork into mathematical prediction.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-142 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | queuing theory, Little's Law, starvation, throughput, latency, connection pool |
| **Prerequisites** | OSY-085, OSY-141 |

---

### Little's Law (The Foundation)

```
Little's Law: N = L * W

  N = average number of items in the system (queue + service)
  L = throughput (items per second)
  W = average time an item spends in the system (latency)
  
  Equivalently: W = N / L
  -> Average latency = queue depth / throughput
  
Constraints:
  - Steady state (arrival rate = departure rate)
  - Applies to any queuing system (OS, network, distributed)
  - Does NOT require specific distribution of arrival/service times
  
Example: Java thread pool
  Thread pool: 10 threads; each request takes 100ms to process
  Throughput (L): 10 threads / 0.1s = 100 req/s
  If requests arrive at 80 req/s: N = 80 * 0.1 = 8 (always 8 in-flight)
  If requests arrive at 100 req/s: N = 100 * 0.1 = 10 (all threads busy)
  If requests arrive at 110 req/s: QUEUE GROWS without bound
  -> 10 threads can process 100 req/s max
  -> 110 req/s arrives: 10/s accumulate in queue
  -> After 10 seconds: 100 requests queued; latency = 10s + processing
```

---

### M/M/c Queue Model

```
The M/M/c model describes most OS and distributed queuing systems:
  M: Poisson (memoryless) arrival process
  M: Exponential (memoryless) service time
  c: number of servers (threads/connections/cores)
  
Key formula - utilization (rho):
  rho = arrival_rate / (c * service_rate)
  
  rho < 1: system stable; queue length stays bounded
  rho = 1: system at capacity; queue length grows slowly
  rho > 1: system overloaded; queue length grows without bound
  
  Java connection pool sizing:
    DB can handle 100 connections; each query takes 10ms
    service_rate per connection = 1/0.01 = 100 queries/second per connection
    Total service rate (100 connections) = 10,000 queries/second
    
    App receives 8,000 queries/second:
    rho = 8000 / (100 * 100) = 0.8 (80% utilization, stable)
    
    App receives 10,000 queries/second:
    rho = 10000 / (100 * 100) = 1.0 (at capacity; queue builds)
    
    App receives 11,000 queries/second:
    rho = 1.1 -> system unstable; queue grows indefinitely
    
Key insight:
  At rho = 0.9 (90% utilization): latency already much higher than rho=0.5
  Queuing theory predicts: average queue length = rho^2 / (1 - rho)
  
  rho=0.5: queue = 0.25/0.5 = 0.5 items (short queue)
  rho=0.8: queue = 0.64/0.2 = 3.2 items (noticeable)
  rho=0.9: queue = 0.81/0.1 = 8.1 items (significant latency)
  rho=0.95: queue = 0.90/0.05 = 18 items (severe latency)
  
  THIS is why "90% CPU is fine" is wrong for latency-sensitive services
  -> Aim for rho < 0.7 for low-latency services (headroom matters)
```

---

### Erlang C Formula

```
The Erlang C formula: probability of waiting in an M/M/c queue

  Used for: call centers, connection pool sizing, thread pool sizing
  
  Erlang C gives: P(waiting) = probability new arrival must wait
  
  Practical interpretation:
    If Erlang C gives 20%: 1 in 5 requests waits in queue before served
    
  For Java HikariCP connection pool sizing:
    Goal: P(waiting) < 5%
    Input: arrival_rate, avg_query_time, desired P(waiting)
    Output: minimum number of connections needed
    
  Example:
    Arrival: 500 queries/second
    Avg query time: 20ms (0.02s)
    Offered load (Erlang): A = 500 * 0.02 = 10 Erlangs
    
    Find c (connections) such that Erlang_C(c, 10) < 0.05:
    c=10: Erlang_C = 1.0 (definitely wait, rho=1.0, unstable)
    c=12: Erlang_C = 0.48 (48% chance of waiting, too high)
    c=15: Erlang_C = 0.12 (12% chance of waiting)
    c=20: Erlang_C = 0.02 (2% chance of waiting - acceptable)
    
    -> Need at least 20 connections for these workload parameters
    
  Practical application:
    HikariCP default maximumPoolSize: 10
    For many production apps: this is TOO small
    Calculate using: Erlang C with your actual RPS and query latency
```

---

### OS Starvation = Classical Queuing Saturation

```
OS resource starvation situations - with queuing theory framing:

  CPU starvation (too many threads):
    Arrival rate: new runnable threads/second
    Service rate: 1 thread every (time_slice = 4ms)
    c: number of CPU cores
    
    With 8 cores and 100 RUNNABLE threads:
    rho >> 1: severe starvation
    vmstat r > 8: run queue > CPU count = overloaded
    
  Memory starvation (page reclaim pressure):
    Arrival: page fault rate (new pages needed per second)
    Service: page reclaim rate (physical pages freed per second)
    If page fault rate > reclaim rate: memory pressure grows
    kswapd runs continuously: system swaps; latency spikes
    
  Disk I/O starvation:
    Arrival: I/O requests per second
    Service: disk IOPS capacity
    Queue: I/O scheduler queue
    At saturation: iostat shows await >> svctm (high queue wait)
    
  Network starvation:
    Arrival: packets per second
    Service: NIC processing capacity (PPS)
    At saturation: RX drops visible in ethtool statistics
    
  All follow the same queuing model:
    Identify: arrivals, servers (c), service rate
    Calculate: rho (utilization)
    If rho > 0.7 for latency-sensitive: already degrading
    If rho > 1.0: mathematically guaranteed to fail
```

---

### Java Thread Pool: Complete Queuing Analysis

```java
// ThreadPoolExecutor as M/M/c queue
ThreadPoolExecutor pool = new ThreadPoolExecutor(
    10,           // corePoolSize = c (servers)
    10,           // maximumPoolSize = c (keep fixed for analysis)
    0L, TimeUnit.MILLISECONDS,
    new LinkedBlockingQueue<>(50)  // queue capacity = 50
    // M/M/c/K: bounded queue (K = 50 + c = 60 total)
);

// Measurement: extract queuing theory parameters at runtime
ScheduledExecutorService monitor = Executors.newScheduledThreadPool(1);
monitor.scheduleAtFixedRate(() -> {
    int activeCount = pool.getActiveCount();
    int queueSize = pool.getQueue().size();
    double utilization = (double) activeCount / pool.getCorePoolSize();
    
    System.out.printf(
        "Utilization: %.1f%% | Active: %d | Queue: %d%n",
        utilization * 100, activeCount, queueSize
    );
    
    // ALERT conditions based on queuing theory:
    if (utilization > 0.7) {
        System.out.println("WARN: >70% utilization; latency increasing");
    }
    if (utilization > 0.9) {
        System.out.println("ALERT: >90% utilization; latency severe");
    }
    if (queueSize > 0) {
        System.out.println("ALERT: Queue forming; check arrival vs service rate");
    }
}, 0, 1, TimeUnit.SECONDS);
```

---

### Summary: The Queuing Theory Toolkit

| Concept | Formula | Java Application |
|---------|---------|-----------------|
| Little's Law | N = L * W | queue_depth = rps * avg_latency |
| Utilization | rho = arrival / (c * service_rate) | active_threads / max_threads |
| Stable condition | rho < 1.0 | Always required |
| Low latency target | rho < 0.7 | For p99 headroom |
| Queue length at rho | rho^2 / (1-rho) | Expected queue depth |
| Erlang C | P(wait) given c, A | Connection pool sizing |
| Saturation point | arrival = c * service_rate | Max throughput |
