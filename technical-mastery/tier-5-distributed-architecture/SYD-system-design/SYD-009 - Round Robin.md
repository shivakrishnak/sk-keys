---
id: SYD-009
title: Round Robin
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★☆☆
depends_on: SYD-008
used_by: ""
related: SYD-008, SYD-010, SYD-011
tags:
  - architecture
  - foundational
  - networking
  - performance
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Mastery"
nav_order: 9
permalink: /technical-mastery/syd/round-robin/
---

⚡ TL;DR - Round robin distributes requests to backend
servers in sequential rotation, giving each server
an equal share of requests. It is the simplest load
balancing algorithm and the right default for stateless
services with uniform request cost.

| #009 | Category: System Design | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Load Balancing | |
| **Used by:** | (none - foundational algorithm) | |
| **Related:** | Load Balancing, Least Connections, Consistent Hashing | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You have 3 backend servers and a load balancer. Without
any algorithm, the load balancer must decide which server
gets each request. Random selection leads to uneven
distribution by chance. Always picking the first server
makes it the bottleneck. You need a simple, fair
policy that distributes requests evenly without any
state or overhead.

**THE BREAKING POINT:**
When adding horizontal scale, the distribution strategy
matters. The simplest possible fair distribution rule
is: give Server 1 the first request, Server 2 the
second, Server 3 the third, and then start over.
This is round robin.

**THE INVENTION MOMENT:**
Round robin scheduling predates computer networking -
it was a well-known fairness algorithm in operating
systems CPU schedulers (each process gets a time slice
in rotation). Applied to load balancing, it was the
natural first algorithm: simple, stateless, provably
fair.

---

### 📘 Textbook Definition

Round robin is a load balancing algorithm that distributes
requests to backend servers in a sequential, circular
order. Given servers [A, B, C], request 1 → A,
request 2 → B, request 3 → C, request 4 → A again.
The algorithm is stateless beyond tracking "which
server is next in the sequence." It distributes requests
evenly (each server gets exactly 1/N of all requests)
but ignores the current load on each server and the
actual cost of each request.

**Weighted round robin** extends this: if A has weight 3
and B has weight 1, the rotation is [A, A, A, B],
repeating. This proportionally distributes requests
by server capacity.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Take turns: Server A gets request 1, Server B gets
request 2, Server C gets request 3, Server A gets
request 4, repeat.

**One analogy:**
> Dealing cards around a table. The dealer gives one
> card to each player in order, cycling back to the
> first when they reach the last. Every player gets
> exactly the same number of cards.

**One insight:**
Round robin is optimal when all requests cost the
same and all servers have equal capacity. It breaks
down when some requests take much longer than others
(slow requests accumulate on whichever server they
land on, making that server slower).

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Each server receives exactly 1/N of all requests
   (for N equally-weighted servers).
2. No request-level state is needed - only the index
   of the last selected server.
3. The algorithm makes no assumption about request
   cost or current server load.

**WHEN IT IS OPTIMAL:**
- Requests are short-lived and approximately equal
  in processing cost (HTTP API calls, ~5-50ms each)
- Servers are homogeneous in capacity (same instance type)
- The service is stateless (any server can handle any
  request without prior context)

**WHEN IT BREAKS DOWN:**
- Requests vary widely in cost: some take 1ms, some
  take 10 seconds. A server that receives several
  10-second requests in a row is overloaded while
  others are idle.
- Servers have different capacities: a 2-core server
  and an 8-core server both receive 1/N of requests,
  but the 2-core server gets overloaded 4x faster.

**DERIVED DESIGN:**
For variable-cost requests → use Least Connections.
For servers of different capacities → use Weighted
Round Robin. For cache/shard affinity → use Consistent
Hashing. Round robin is the right default for the
most common case (uniform, stateless, equal servers).

---

### 🧪 Thought Experiment

**SCENARIO:**
3 servers. Round robin. Two request types: quick (1ms)
and slow (5 seconds).

**WHAT HAPPENS:**
```
Request 1 (slow, 5s) → Server A
Request 2 (quick)    → Server B (completes in 1ms)
Request 3 (quick)    → Server C (completes in 1ms)
Request 4 (quick)    → Server A (still busy with req 1)
Request 5 (slow, 5s) → Server B
...
```

Server A receives requests while still processing req 1.
After 10 slow requests, Server A could have 3+ in-flight
simultaneously. B and C handle quick requests and
stay responsive. Server A becomes a hot spot.

**THE INSIGHT:**
Round robin distributes request *count* equally.
It does not distribute request *work* equally.
For uniform workloads, these are the same.
For non-uniform workloads, they diverge - and Least
Connections or a work-stealing algorithm is better.

---

### 🧠 Mental Model / Analogy

> Round robin is like a revolving door that lets one
> person through at a time, cycling through all doors
> equally. Everyone waits in one queue, and each
> successive person goes through the next door.
> If one door is slow (sticky), the people assigned
> to it back up while other doors flow freely.

- "Doors" → servers
- "People" → requests
- "Sticky door" → a server handling a long-running request
- "Everyone waits in one queue" → global request queue
  before the LB dispatches

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Each new request goes to the next server in line. When
you reach the last server, you start over from the first.
Simple, predictable, fair.

**Level 2 - How to use it (junior developer):**
In nginx: `upstream { }` uses round-robin by default.
No special directive needed. Each request goes to the
next server in the list.

**Level 3 - How it works (mid-level engineer):**
The LB keeps an atomic counter (index % N). Each request
increments the counter and routes to server[counter % N].
For weighted round robin, the sequence is pre-computed
as an expanded list: weight 3 for A, weight 1 for B →
sequence [A, A, A, B, A, A, A, B, ...].

**Level 4 - Why it was designed this way (senior/staff):**
Round robin is O(1) in time complexity - no state to
inspect beyond a single counter. This matters at very
high request rates (millions per second) where even
Least Connections (which must inspect connection counts
per server) has overhead. For most API services where
request cost variance is low, round robin's simplicity
beats Least Connections' accuracy.

**Level 5 - Mastery (distinguished engineer):**
The choice between round robin and least connections is
often irrelevant in practice because modern load
balancers use keep-alive connections and connection
pools, which smooth out the differences between
algorithms for short-lived HTTP requests. The algorithm
choice matters most for long-lived connections (WebSocket,
gRPC streaming) or highly variable request costs
(fast reads vs slow writes, small queries vs large
file transfers). For these cases, least connections
or even exponentially-weighted moving average of
recent latency per server is significantly better.

---

### ⚙️ How It Works (Mechanism)

**Round robin selection logic:**

```
┌──────────────────────────────────────────────────┐
│ ROUND ROBIN ALGORITHM                            │
│                                                  │
│ servers = [A, B, C]                              │
│ counter = 0 (atomic, shared across threads)      │
│                                                  │
│ def select_server():                             │
│     idx = counter.fetch_and_increment()          │
│     return servers[idx % len(servers)]           │
│                                                  │
│ Request 1: idx=0, 0%3=0 → Server A              │
│ Request 2: idx=1, 1%3=1 → Server B              │
│ Request 3: idx=2, 2%3=2 → Server C              │
│ Request 4: idx=3, 3%3=0 → Server A              │
└──────────────────────────────────────────────────┘
```

**Weighted round robin (Smooth Weighted, nginx implementation):**

```
┌──────────────────────────────────────────────────┐
│ SMOOTH WEIGHTED ROUND ROBIN                      │
│                                                  │
│ A: weight=5, B: weight=3, C: weight=2            │
│ (total weight = 10)                              │
│                                                  │
│ Each server has current_weight, starts at 0      │
│ Each round: current_weight += own_weight         │
│             select max current_weight server     │
│             selected server -= total_weight      │
│                                                  │
│ Round 1: A=5, B=3, C=2 → A wins (5 is max)     │
│          A becomes: 5-10=-5. Others stay.        │
│ Round 2: A=-5+5=0, B=3+3=6, C=2+2=4 → B wins  │
│ Round 3: A=5, B=6-10=-4, C=6 → C wins (6>5)   │
│ Round 4: A=10, B=-1, C=8 → A wins              │
│ ...                                              │
│                                                  │
│ Result: distributed as A,B,C,A,A,B,A,C,B,A...  │
│ Smooth: no server is served consecutively many   │
│ times in a row despite high weight.              │
└──────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - nginx: Round robin (default)**
```nginx
# Round robin is the DEFAULT in nginx upstream block
# No algorithm directive needed for basic round robin

upstream app_backend {
    # Default: round robin
    server 10.0.1.1:8080;
    server 10.0.1.2:8080;
    server 10.0.1.3:8080;
}

# Weighted round robin: server A gets 3x the requests
upstream app_backend_weighted {
    server 10.0.1.1:8080 weight=3;  # large instance
    server 10.0.1.2:8080 weight=1;  # small instance
    server 10.0.1.3:8080 weight=1;  # small instance
}
```

**Example 2 - Java: Simple round robin implementation**
```java
// BAD: Not thread-safe - concurrent requests can
// get the same server
public class RoundRobinBalancer {
    private int index = 0;  // not thread-safe
    private final List<String> servers;

    public String nextServer() {
        return servers.get(index++ % servers.size());
    }
}

// GOOD: Thread-safe with AtomicInteger
public class RoundRobinBalancer {
    private final AtomicInteger counter = new AtomicInteger(0);
    private final List<String> servers;

    public RoundRobinBalancer(List<String> servers) {
        this.servers = Collections.unmodifiableList(servers);
    }

    public String nextServer() {
        // getAndIncrement: atomic fetch-then-increment
        int idx = counter.getAndIncrement();
        // % size to wrap around; abs() handles overflow
        return servers.get(Math.abs(idx % servers.size()));
    }
}
```

**Example 3 - DNS round robin (what NOT to use)**
```bash
# BAD: DNS round-robin - no health checking, stale cache
# If one A record fails, clients still try it for TTL duration
dig api.example.com
# api.example.com    60  IN  A  10.0.1.1
# api.example.com    60  IN  A  10.0.1.2
# api.example.com    60  IN  A  10.0.1.3
# Each DNS response rotates the order.
# Problem: client caches first IP for 60 seconds.
# If 10.0.1.2 dies, clients keep trying it for ~60s.

# GOOD: Single load balancer IP behind DNS
dig api.example.com
# api.example.com  300  IN  A  10.0.0.100  ← one LB IP
# Health checking and rotation happen in the LB,
# not in DNS. Failed backends are removed in <30s.
```

---

### ⚖️ Comparison Table

| Algorithm | Distributes By | Best For | Weakness |
|---|---|---|---|
| **Round Robin** | Request count (equal) | Uniform short requests | Long/variable requests |
| Weighted RR | Request count (weighted) | Unequal server capacity | Still ignores current load |
| Least Connections | Active connections | Variable request duration | Overhead of tracking connections |
| IP Hash | Client IP hash | Session affinity | Uneven if few clients |
| Consistent Hash | Key hash | Cache/shard affinity | Rehashing on change |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Round robin distributes load evenly | It distributes REQUEST COUNT evenly. Load (CPU, memory, time) is only evenly distributed if all requests are equal cost. |
| Round robin is always the worst choice | For homogeneous requests (~5ms API calls), round robin has the same practical outcome as least connections but with zero overhead. It is often the correct choice. |
| Weighted round robin automatically adapts to server health | Weights are static configuration. A slow server still receives its weight-proportional share. Dynamic load balancing requires algorithms that observe real-time server state. |

---

### 🚨 Failure Modes & Diagnosis

**Hot Server from Long-Running Requests**

**Symptom:**
One of 3 servers shows 90% CPU, while the others are
at 30%. All servers receive the same number of requests
per minute. Users routed to the hot server experience
high latency.

**Root Cause:**
Some requests trigger expensive database queries that
take 10-30 seconds. Round robin directed several of
these expensive requests to Server A by chance. Server A
is now processing 5 long-running queries simultaneously
while still receiving 1/3 of all new requests.

**Diagnostic:**
```bash
# Check active connections per server (from LB)
# AWS ALB: check ActiveConnectionCount metric per target
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApplicationELB \
  --metric-name ActiveConnectionCount \
  --dimensions Name=TargetGroup,Value=... \
  --period 60 --statistics Average \
  --start-time ... --end-time ...

# Better: look at TargetResponseTime by target
# A server with long-running requests will show
# higher average response time, indicating round
# robin is concentrating work unfairly
```

**Fix:**
Switch to `least_conn` algorithm in nginx, or configure
least connections in the ALB target group. This
automatically sends fewer new requests to the server
with the most active connections.

**Prevention:**
Use round robin only when you can verify that request
duration variance is low (p50/p99 ratio < 5x). For
APIs with both quick reads and slow writes, use least
connections from the start.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Load Balancing` - round robin is one of multiple
  algorithms used by load balancers; understand the
  broader concept before studying individual algorithms

**Builds On This (learn these next):**
- `Least Connections` - the practical upgrade over
  round robin for variable-cost requests
- `Consistent Hashing` - the algorithm for shard/cache
  affinity across a pool of servers

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Sequential rotation: request 1→A, 2→B,   │
│              │ 3→C, 4→A, 5→B, 6→C, repeat              │
├──────────────┼──────────────────────────────────────────┤
│ PROBLEM IT   │ Simple, fair distribution with no        │
│ SOLVES       │ state or overhead                        │
├──────────────┼──────────────────────────────────────────┤
│ KEY INSIGHT  │ Fair by request count, not by work.      │
│              │ Only optimal when all requests are       │
│              │ equal cost and all servers equal capacity│
├──────────────┼──────────────────────────────────────────┤
│ USE WHEN     │ Short, uniform-cost requests; homogeneous│
│              │ server pool; no session affinity needed  │
├──────────────┼──────────────────────────────────────────┤
│ AVOID WHEN   │ High request cost variance (reads vs     │
│              │ heavy computations); unequal servers     │
├──────────────┼──────────────────────────────────────────┤
│ ALGORITHM    │ index = atomic_counter % server_count    │
│              │ O(1) time, O(1) state (one counter)      │
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "Take turns. Simple. Fair by count, not  │
│              │  by work. Good default for uniform loads.│
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Least Connections → Consistent Hashing   │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Distributes by request count, not by request cost.
2. Best default for short, uniform API calls.
3. Switch to Least Connections when request duration
   varies significantly.

**Interview one-liner:**
"Round robin distributes requests to servers in sequential
rotation - A, B, C, A, B, C. Each server gets an equal
share by request count. It is optimal for uniform
short requests but breaks down when some requests
are much more expensive than others, in which case
least connections is more appropriate."

---

### 💎 Transferable Wisdom

**Where else this pattern appears:**
- **OS CPU scheduler:** Each process or thread gets
  a time slice in round-robin rotation. The process
  does not get to run forever; after its time slice,
  the scheduler moves to the next process.
- **Database connection pools:** HikariCP distributes
  connections to waiting threads in a queue; the
  conceptual model is similar (take the next available).
- **Kafka consumer groups:** Partitions are distributed
  to consumers in a round-robin-like assignment by
  default, so each consumer handles an equal number
  of partitions.
- **DNS TTL rotation:** Multiple A records in DNS are
  returned in rotating order (a poor-man's load
  balancing, with the caveats discussed in the failure
  modes above).

---

### 🎯 Interview Deep-Dive

**Q1: When is round robin a better choice than least
connections for a production load balancer?**
*Why they ask:* Tests nuanced algorithm knowledge.
*Strong answer includes:*
- Short-lived HTTP requests (< 100ms) with low cost
  variance: round robin and least connections produce
  nearly identical results because connections complete
  quickly, so the count difference is tiny
- Very high request rate (> 100k RPS per LB): round
  robin's O(1) overhead is meaningfully better than
  least connections' need to atomically read and
  compare connection counts per server
- When the backend pool has uniform capacity and
  similar request patterns

**Q2: How would you implement weighted round robin
if Server A has 8 cores and Server B has 2 cores?**
*Why they ask:* Tests practical application of
the algorithm.
*Strong answer includes:*
- Set weights proportional to capacity: A=4, B=1
- Every 5 requests: A receives 4, B receives 1
- nginx: `server A weight=4; server B weight=1;`
- AWS ALB: registered targets in the target group
  do not support weights at the ALB level (as of 2024);
  would need to run more instances of the large server
  or use a custom LB
- Important caveat: static weights do not adapt
  to runtime performance differences (GC pauses,
  slow dependencies). Monitoring and adjusting weights
  must be done manually or via automation.
