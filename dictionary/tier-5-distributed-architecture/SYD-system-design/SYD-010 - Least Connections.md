---
id: SYD-010
title: Least Connections
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★☆
depends_on: SYD-008
used_by: ""
related: SYD-008, SYD-009, SYD-011, SYD-014
tags:
  - architecture
  - networking
  - performance
  - distributed-systems
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 10
permalink: /syd/least-connections/
---

# SYD-010 - Least Connections

⚡ TL;DR - Least connections routes each new request
to the backend server with the fewest active connections
at that moment, dynamically distributing load based
on actual server utilization rather than blind rotation.

| #010 | Category: System Design | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Load Balancing | |
| **Used by:** | (none - foundational algorithm) | |
| **Related:** | Load Balancing, Round Robin, Consistent Hashing, Auto Scaling | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You have 5 API servers behind a round-robin load balancer.
Your service handles two types of requests: fast reads
(5ms) and slow report generation (30 seconds). By chance,
Server 2 receives 5 report-generation requests in a row.
It now has 5 long-running jobs consuming all its
threads. Meanwhile, the round-robin balancer keeps
sending 1/5 of all new requests to Server 2. Each of
those requests joins a queue behind the report jobs.
Server 2's p99 latency climbs to 35+ seconds. Other
servers are at 20% CPU. Round-robin created a hot
server while others are idle.

**THE BREAKING POINT:**
Round robin is fair by request count, not by server
load. When request cost varies (some are 1ms, some
are 30s), request count fairness is the wrong metric.
You need load fairness: route each new request to the
server that has the most capacity to handle it right now.

**THE INVENTION MOMENT:**
Least connections was introduced as a direct fix for
round robin's weakness with non-uniform request costs.
The insight: a server's current active connection count
is a real-time proxy for its current load. Route to the
server with the lowest count, and you distribute work
more evenly for mixed workloads.

---

### 📘 Textbook Definition

Least connections (also called "least busy" or "minimum
connections") is a load balancing algorithm that
routes each new incoming request to the backend server
with the fewest currently active connections. The load
balancer maintains a count of open connections per
backend and updates it atomically on each connection
open and close. This algorithm self-adjusts to server
load: slow servers naturally accumulate higher
connection counts and receive fewer new requests, while
fast servers complete connections quickly and continue
to receive a proportional share of new load. The
weighted variant (Least Connections Weighted) divides
connection count by server weight, enabling proportional
distribution across servers of different capacities.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Always send the next request to whichever server is
currently handling the fewest requests.

**One analogy:**
> A supermarket manager who watches all checkout
> queues and signals each new customer to the
> shortest queue. If Queue 3 has 8 people and
> Queue 1 has 2, the next customer always goes
> to Queue 1. The queues self-balance naturally.

**One insight:**
Least connections is "work-aware" where round robin
is "count-aware." When requests have variable
processing cost, work-awareness is what matters.
The active connection count is the load balancer's
real-time approximation of how much work each server
currently has in flight.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Every open connection is counted; every closed
   connection is decremented.
2. On each new request, scan all healthy backends and
   route to the one with the minimum connection count.
3. If multiple backends are tied at the minimum, use
   a tiebreaker (often round-robin among the tied
   backends, or random selection).

**THE MECHANISM:**
The load balancer maintains a concurrent data structure
mapping server → active_connection_count. This count
is updated atomically: +1 when a connection is
forwarded to a backend, -1 when the backend closes
the connection. The lookup for minimum requires reading
N values (for N backends), which is O(N) per request.

**TRADE-OFFS vs ROUND ROBIN:**
- **More accurate distribution** for variable-cost
  requests (the key benefit).
- **O(N) selection overhead** vs O(1) for round robin.
  At very high request rates (> 500k RPS) this matters.
- **More coordination overhead** - the connection count
  map requires atomic operations across concurrent
  request dispatching threads.

**WHEN IT IS OPTIMAL:**
- Requests have high cost variance (reads + writes +
  batch jobs on same pool of servers)
- Long-lived connections (WebSocket, gRPC streaming,
  database connections)
- Server pool is heterogeneous in capacity (use
  Weighted Least Connections)

**WHEN ROUND ROBIN IS BETTER:**
- Extremely uniform, short requests (< 10ms, low
  variance) and very high request rate - round robin's
  O(1) overhead wins.
- When the O(N) scan becomes a bottleneck (very large
  server pools, N > 1000).

---

### 🧪 Thought Experiment

**SCENARIO:**
3 servers, least-connections, same workload as the
round-robin failure mode:
- Fast requests: 5ms
- Slow requests (report generation): 30 seconds

**WHAT HAPPENS:**

```
t=0ms:  RQ1 (slow) → A (A=1, B=0, C=0)
t=1ms:  RQ2 (fast) → B (B has 0 < A has 1)
t=2ms:  RQ3 (fast) → C (C has 0 < A,B)
t=3ms:  RQ4 (fast) → B (B completed RQ2: B=0)
t=4ms:  RQ5 (slow) → C (C=0 now after RQ3 done)
t=5ms:  RQ6 (slow) → B (B=0)

At t=100ms:
  A = 1 connection (still running RQ1, 30s request)
  B = 1 connection (running RQ6, 30s request)
  C = 1 connection (running RQ5, 30s request)

All slow requests are isolated. No server gets two
slow requests simultaneously. Fast requests fill
the remaining capacity evenly.
```

**THE INSIGHT:**
Least connections automatically "sees" that a server
is busy (high connection count) and avoids piling
work onto it. Round robin would have continued routing
to the busy server at 1/3 the rate regardless.

---

### 🧠 Mental Model / Analogy

> Least connections is like a smart checkout manager
> who constantly monitors all checkout queue lengths.
> A new customer always joins the shortest queue.
> If a cashier is slow (like a slow server), their
> queue grows, and the manager stops sending new
> customers there. The slow cashier's queue drains
> naturally as their customers complete their
> transactions.

- "Queue length" → active connection count
- "Slow cashier" → server processing long-running requests
- "Manager redirects customers" → LB routes to min-count server
- "Queue draining" → long-running requests completing,
  freeing the server to accept more traffic

**Where this analogy breaks down:**
Unlike queue length at a supermarket (visible to the
customer), connection counts are invisible to clients
and are tracked internally by the load balancer. Clients
cannot choose - only the LB makes the routing decision.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
When a request arrives, the load balancer looks at
how busy each server is and sends the request to the
least busy one.

**Level 2 - How to use it (junior developer):**
In nginx: add `least_conn;` to the upstream block.
In AWS ALB: configure the target group to use the
"least outstanding requests" routing algorithm.

**Level 3 - How it works (mid-level engineer):**
The LB maintains an atomic counter per backend.
On each request: select the backend with the lowest
counter, increment that counter, forward the request.
When the backend response is complete, decrement
the counter.

**Level 4 - Why it was designed this way (senior/staff):**
The connection count approximates server busyness with
no server-side instrumentation needed. Alternative
approaches (routing based on CPU utilization reported
by the server) require a feedback mechanism between
server and LB and add latency. Connection count is
already tracked by the LB for connection management;
using it for routing is essentially free. The
approximation is imperfect (connection count misses
CPU-bound tasks with few open connections) but is
"good enough" for the most common patterns.

**Level 5 - Mastery (distinguished engineer):**
Modern alternatives to Least Connections for
sophisticated traffic management include:
- **EWMA (Exponentially Weighted Moving Average of
  latency)**: route to the server with the best
  recent latency, not connection count. Used in
  Envoy and some Linkerd configurations. Better
  than Least Connections because it accounts for
  server-side latency variation even when connection
  counts are similar.
- **Power of Two Choices (P2C)**: pick 2 random
  backends, route to the one with fewer connections.
  Achieves ~80% of the benefit of global least
  connections at O(1) lookup cost (vs O(N) full scan).
  Used in Netflix's Ribbon and Finagle clients.

---

### ⚙️ How It Works (Mechanism)

**Selection algorithm:**

```
┌──────────────────────────────────────────────────┐
│ LEAST CONNECTIONS SELECTION                      │
│                                                  │
│ backends = {A: 3 conns, B: 1 conn, C: 5 conns}  │
│                                                  │
│ 1. Scan all backends: find min count             │
│    A=3, B=1, C=5 → min = B (1 connection)       │
│ 2. Increment B's counter: B → 2                  │
│ 3. Forward request to B                          │
│ 4. When B's response completes: B → 1            │
│                                                  │
│ Next request: A=3, B=1, C=5 → B again           │
│ Or if B just got a new connection: B=2           │
│   A=3, B=2, C=5 → B again (still lowest)        │
└──────────────────────────────────────────────────┘
```

**Power of Two Choices (P2C) - production alternative:**

```
┌──────────────────────────────────────────────────┐
│ POWER OF TWO CHOICES                             │
│                                                  │
│ backends = [A, B, C, D, E, ... (100 servers)]   │
│                                                  │
│ Instead of scanning all 100:                     │
│ 1. Pick 2 at random: say C and G                 │
│ 2. Route to whichever of {C, G} has fewer conns  │
│                                                  │
│ Result: nearly as good as full least-connections │
│ but O(1) instead of O(N) lookup.                 │
│                                                  │
│ Proof: E[queue length] of P2C ≈ ln(ln(N))       │
│        vs round robin: Θ(ln(N)/ln(ln(N)))        │
│ P2C wins substantially for large N.              │
└──────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
[Request arrives at LB]
  → [Read connection counts for all healthy backends]
  → [Select backend with minimum count]
  → [Atomically increment that backend's count]
  → [Forward request]
  → [Backend processes request]
  → [Backend sends response]
  → [LB receives response, relays to client]
  → [Atomically decrement backend's count]
```

**CONCURRENT REQUEST HANDLING:**
```
Thread 1: reads counts (A=2, B=1, C=3) → selects B
Thread 2: reads counts (A=2, B=2, C=3) → selects A
  (B was incremented by Thread 1 before Thread 2 reads)
Thread 3: reads counts (A=3, B=2, C=3) → selects B
  (A was incremented by Thread 2 before Thread 3 reads)
```
Note: concurrent threads may pick the same server if
they read the counter simultaneously before either
increment. This is acceptable - the distribution will
still be more even than round-robin.

**AT SCALE:**
For 10 backends: O(10) scan per request is negligible.
For 1,000 backends: O(1,000) scan per request could
be meaningful at 100k+ RPS. Use P2C (Power of Two
Choices) instead.

---

### 💻 Code Example

**Example 1 - nginx: Least connections**
```nginx
# BAD: Round robin (ignores current server load)
upstream backend {
    server 10.0.1.1:8080;
    server 10.0.1.2:8080;
    server 10.0.1.3:8080;
}

# GOOD: Least connections for variable-cost requests
upstream backend {
    least_conn;
    server 10.0.1.1:8080;
    server 10.0.1.2:8080;
    server 10.0.1.3:8080;
    keepalive 32;
}

# Weighted least connections for unequal servers:
upstream backend_weighted {
    least_conn;
    server 10.0.1.1:8080 weight=4;  # 8-core server
    server 10.0.1.2:8080 weight=1;  # 2-core server
    server 10.0.1.3:8080 weight=1;  # 2-core server
}
```

**Example 2 - Java: Least connections implementation**
```java
// Thread-safe least connections balancer
public class LeastConnBalancer {
    private final List<AtomicInteger> connCounts;
    private final List<String> servers;

    public LeastConnBalancer(List<String> servers) {
        this.servers = Collections.unmodifiableList(servers);
        this.connCounts = servers.stream()
            .map(s -> new AtomicInteger(0))
            .collect(toList());
    }

    public String acquire() {
        // Find server with minimum connections
        int minIdx = 0;
        int minCount = Integer.MAX_VALUE;
        for (int i = 0; i < connCounts.size(); i++) {
            int count = connCounts.get(i).get();
            if (count < minCount) {
                minCount = count;
                minIdx = i;
            }
        }
        // Increment before returning (reserve the slot)
        connCounts.get(minIdx).incrementAndGet();
        return servers.get(minIdx);
    }

    public void release(String server) {
        int idx = servers.indexOf(server);
        if (idx >= 0) {
            connCounts.get(idx).decrementAndGet();
        }
    }
}

// Usage - must call release() after request completes
// Use try-finally to guarantee release
String server = balancer.acquire();
try {
    return sendRequest(server, request);
} finally {
    balancer.release(server);
}
```

**Example 3 - AWS ALB: Least outstanding requests**
```bash
# AWS ALB supports "least outstanding requests" algorithm
# (equivalent to least connections for HTTP requests)
aws elbv2 modify-target-group-attributes \
  --target-group-arn arn:aws:elasticloadbalancing:... \
  --attributes Key=load_balancing.algorithm.type,\
Value=least_outstanding_requests

# Verify the change
aws elbv2 describe-target-group-attributes \
  --target-group-arn arn:aws:... \
  --query 'Attributes[?Key==`load_balancing.algorithm.type`]'
# Expected: "least_outstanding_requests"

# Useful diagnostic: check RequestCountPerTarget in CloudWatch
# High variance across targets = round-robin + slow requests
# Low variance across targets = least-connections working
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApplicationELB \
  --metric-name RequestCountPerTarget \
  --dimensions Name=TargetGroup,Value=... \
  --period 60 --statistics Sum \
  --start-time ... --end-time ...
```

---

### ⚖️ Comparison Table

| Scenario | Round Robin | Least Connections | Winner |
|---|---|---|---|
| Uniform short requests (5ms ±1ms) | Even distribution | Near-identical in practice | Round Robin (simpler) |
| Mixed fast/slow (5ms + 30s) | Hot server emerges | Load distributes evenly | Least Connections |
| Long-lived WebSocket connections | Uneven at scale | Self-balances naturally | Least Connections |
| Very high RPS (500k+) | O(1), fast | O(N) scan overhead | Round Robin |
| Unequal server capacity | Weighted RR | Weighted Least Conn | Depends on workload |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Least connections is always better than round robin | For short, uniform requests, both perform nearly identically. Round robin has lower overhead at extreme request rates. |
| More active connections always means more load | A server with many small open connections (websocket idle) has lower load than a server with few but CPU-intensive requests. Connection count is a proxy, not an exact measure. |
| Least connections eliminates hot servers entirely | It reduces hot servers but does not eliminate them. If one server is simply slower (GC pause, degraded hardware), its connection count will stay high longer but new requests still arrive during the pause window. |

---

### 🚨 Failure Modes & Diagnosis

**Connection Count Leak - Stuck Counters**

**Symptom:**
One server's active connection count climbs to 500+
and never decreases, even though clients report normal
response times. The LB stops routing to this server
(its count is highest). The 2 remaining servers become
overloaded.

**Root Cause:**
A bug in the load balancer or connection tracking code
fails to decrement the counter when connections close.
This is a "counter leak." The server appears permanently
overloaded even though it is healthy.

**Diagnostic:**
```bash
# Check nginx active connections vs upstream connections
curl localhost/nginx_status
# Active connections: 150
# Active: should match sum of connections to all upstreams
# If nginx reports 150 active but upstream stats show
# one server at 500 - the counter is stale

# Check actual TCP connections on the overloaded server
# (SSH in or use SSM)
ss -tn state established | grep :8080 | wc -l
# Compare to LB's tracked count for this server
# If LB count >> actual connections: counter leak
```

**Fix:**
Reset the connection count for the affected upstream
(nginx: reload config to reset state). Find and fix
the counter management bug. Ensure connection tracking
uses try-finally semantics so counters always decrement
on completion, timeout, or error.

**Prevention:**
Use timeout-based connection expiry: if a tracked
connection has been open > max_request_duration,
force-decrement the counter and log a warning.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Load Balancing` - least connections is an algorithm
  used by load balancers; understand the full LB context
- `Round Robin` - the baseline algorithm that least
  connections improves upon for variable-cost requests

**Builds On This (learn these next):**
- `Consistent Hashing` - for cache/shard-aware routing
  (a different optimization goal than connection count)
- `Auto Scaling` - least connections helps when fixed
  server count can handle the load; auto scaling is
  needed when total capacity is insufficient

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Route each request to the backend with    │
│              │ the fewest active connections currently   │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Round robin creates hot servers when      │
│ SOLVES       │ request costs vary (fast reads + slow     │
│              │ writes on same server pool)               │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Connection count is a real-time proxy     │
│              │ for server busyness, visible to the LB    │
│              │ without any server-side instrumentation   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Mixed fast/slow requests; long-lived      │
│              │ connections; request cost has high        │
│              │ variance (reads vs. batch jobs)           │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Very high RPS with uniform short requests │
│              │ (round robin's O(1) wins); very large     │
│              │ server pools (use P2C instead)            │
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ Tracking connections but leaking the      │
│              │ decrement on error/timeout - server looks │
│              │ permanently overloaded to the LB          │
├──────────────┼───────────────────────────────────────────┤
│ ALGORITHM    │ O(N) scan, select min count backend,      │
│              │ atomically increment. Decrement on close. │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Send to the least busy server: fixes     │
│              │  round robin's blind spot for variable    │
│              │  request cost."                           │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Consistent Hashing → Sticky Sessions →   │
│              │ Auto Scaling                              │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Routes to the server with fewest active connections -
   self-adjusts to server load in real time.
2. Better than round robin for variable-cost requests -
   prevents hot-server buildup on slow tasks.
3. Connection count is a proxy - not perfect, but
   good enough for most mixed workloads.

**Interview one-liner:**
"Least connections routes each request to the backend
server currently handling the fewest active connections.
This makes it self-adjusting for variable-cost requests:
a server processing a slow 30-second job accumulates
more connections and automatically receives fewer new
requests, while a fast server drains its connections
quickly and continues receiving a proportional share.
It is the standard choice over round-robin when request
cost varies significantly."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Work-distribution problems require work-aware metrics.
Round robin is count-aware; least connections is
work-proxied-aware (using connection count as a proxy
for work). The general lesson: when distributing
variable-cost work, the distribution mechanism must
have visibility into actual load, not just request
arrival rate. This principle applies to thread pools
(work stealing), Kafka partition assignment (lag-aware
rebalancing), and database connection pools (connection
weight based on query time).

**Where else this pattern appears:**
- **Kubernetes Scheduler:** When assigning pods to nodes,
  the scheduler considers each node's current resource
  utilization (memory, CPU requests). This is "least
  connections" applied to infrastructure resource
  allocation, not request routing.
- **Work Stealing in Thread Pools:** Java's
  ForkJoinPool uses work stealing - threads with
  empty queues steal tasks from threads with the
  most work. This is least-connections at the
  thread level.
- **Kafka Consumer Rebalancing:** The sticky partition
  assignor attempts to give each consumer an equal
  number of partitions (similar to least connections
  for partition assignment), while minimizing
  rebalancing disruption.

---

### 🎯 Interview Deep-Dive

**Q1: An API server handles two types of requests:
simple GET requests averaging 10ms and complex report
generation averaging 45 seconds. The team uses round-
robin load balancing across 4 servers. What problem
will they experience at scale and how would you fix it?**
*Why they ask:* Direct test of when to use least
connections vs round robin.
*Strong answer includes:*
- Problem: round robin distributes by count. Servers
  that randomly receive report requests fill up with
  long-running connections. 1/4 of new requests keep
  going to the busy server, queueing behind 45-second
  jobs. p99 latency spikes.
- Fix: switch to least connections. Servers with report
  jobs have high connection counts; the LB stops routing
  new requests there until jobs complete.
- Better fix: separate the report generation workload
  into a different pool entirely (separate endpoint,
  separate server group). Isolate slow operations
  from fast operations at the routing level.

**Q2: What is Power of Two Choices and when would
you prefer it over standard least connections?**
*Why they ask:* Tests knowledge of advanced LB algorithms.
*Strong answer includes:*
- P2C: pick 2 random backends, route to the one with
  fewer connections. O(1) lookup instead of O(N) scan.
- Mathematical result: P2C achieves queue length of
  O(ln(ln(N))) vs round-robin's O(ln(N)/ln(ln(N)));
  dramatically better than round-robin and nearly
  as good as full least-connections.
- Use when: server pool is large (> 100 backends),
  request rate is very high (full O(N) scan is
  measurably expensive), and the slight accuracy
  reduction vs full scan is acceptable.
- Used by: Netflix Ribbon, Twitter Finagle, Envoy
  (as an option for large clusters).

**Q3: How does least connections behave during a
rolling deploy where one server is replaced?**
*Why they ask:* Tests operational depth.
*Strong answer includes:*
- When a server is drained (removed from pool):
  existing connections complete, LB decrements count
  to 0, server leaves pool. No impact on least-conn
  algorithm.
- When a new server joins (after deploy):
  new server has 0 connections. It will receive ALL
  new requests until its connection count equals the
  rest of the pool (because it always wins the
  "minimum count" check). This is actually beneficial:
  the new server gets a burst of traffic to warm up
  its caches quickly. But for cold-cache services,
  this can temporarily cause high latency on the
  new server - consider a slow start policy
  (nginx: `slow_start=30s`) that gradually increases
  the new server's connection limit instead of
  instantly allowing full load.
