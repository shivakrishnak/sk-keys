---
layout: default
title: "Round Robin"
parent: "System Design"
nav_order: 684
permalink: /system-design/round-robin/
number: "684"
category: System Design
difficulty: ★☆☆
depends_on: "Load Balancing"
used_by: "Sticky Sessions, Session Affinity"
tags: #foundational, #distributed, #networking, #algorithm, #architecture
---

# 684 — Round Robin

`#foundational` `#distributed` `#networking` `#algorithm` `#architecture`

⚡ TL;DR — **Round Robin** is the simplest load balancing algorithm: requests are distributed to backend servers in sequential circular order — server 1, server 2, server 3, back to server 1.

| #684 | Category: System Design | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Load Balancing | |
| **Used by:** | Sticky Sessions, Session Affinity | |

---

### 📘 Textbook Definition

**Round Robin** is a load distribution algorithm where each new incoming request is forwarded to the next server in a cyclical sequence. Given a pool of N servers, request 1 goes to server[0], request 2 to server[1], ... request N to server[N-1], request N+1 back to server[0]. **Weighted Round Robin** extends the algorithm by assigning proportional weights to servers: a server with weight 3 receives 3 requests for every 1 request sent to a server with weight 1. Round Robin assumes equal request cost — it distributes connection count evenly but not necessarily processing load. It is stateless (no memory of past requests beyond the current index), deterministic, and has O(1) time complexity per routing decision.

---

### 🟢 Simple Definition (Easy)

Round Robin distributes requests like dealing cards: first card to player 1, second card to player 2, third card to player 3, fourth card back to player 1. Every server gets its turn in order. Simple, fair, no bias — but doesn't account for how long each server takes to process its "card."

---

### 🔵 Simple Definition (Elaborated)

Three backend servers. Requests come in: request 1 → Server A, request 2 → Server B, request 3 → Server C, request 4 → Server A again. With equal-capacity servers handling equal-cost requests, this distributes load evenly. Problems appear when: requests vary in cost (one takes 10ms, the next takes 10 seconds), or servers vary in capacity. Weighted Round Robin addresses capacity differences. Least Connections addresses variable request duration.

---

### 🔩 First Principles Explanation

**Round Robin algorithm — implementation and limitations:**

```java
// Simple Round Robin implementation:
public class RoundRobinLoadBalancer {
    private final List<String> backends;
    private final AtomicInteger index = new AtomicInteger(0);
    
    public RoundRobinLoadBalancer(List<String> backends) {
        this.backends = List.copyOf(backends);
    }
    
    public String nextBackend() {
        // Atomically increment and wrap:
        int i = index.getAndIncrement() % backends.size();
        return backends.get(i);
    }
    // Thread-safe: AtomicInteger handles concurrent access
    // Time complexity: O(1)
    // Space complexity: O(1) extra (just the counter)
}

// WEIGHTED round robin (servers have different capacities):
// Server A: weight=3 (handles 3x more than B)
// Server B: weight=1
// Sequence: A, A, A, B, A, A, A, B, ...
// Implementation: expand to list [A, A, A, B] and apply regular RR
// Or: interleaved weight scheduling for more even distribution

// ROUND ROBIN FAILS WHEN:
// Request 1 (→ Server A): simple lookup, takes 5ms
// Request 2 (→ Server B): complex report, takes 30,000ms (30s)
// Request 3 (→ Server C): simple lookup, takes 5ms
// Request 4 (→ Server A): ...A is now idle, B is saturated
//
// After 100 requests: Server B has 33 active requests (all slow)
//                     Server A/C: each at 0-1 active requests
// This is why Least Connections > Round Robin for mixed workloads
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT any load balancing algorithm:
- No systematic distribution — all requests to one server

WITH Round Robin:
→ Even distribution by request count across homogeneous servers
→ Zero state tracking overhead: O(1) routing decision
→ Simple, predictable, deterministic behaviour

---

### 🧠 Mental Model / Analogy

> Dealing cards in a card game. The dealer deals one card to each player in turn, cycling back to the first player after the last. It's fair in the sense that everyone gets the same number of cards. But if players process cards at different speeds (some think faster), the "load" of unprocessed cards is uneven.

"Dealer" = load balancer
"Cards" = requests
"Players" = backend servers
"Players thinking at different speeds" = variable request processing time

---

### ⚙️ How It Works (Mechanism)

**nginx weighted round robin configuration:**

```nginx
upstream backend {
    # Weighted round robin:
    server backend1.example.com:8080 weight=5;  # gets 5/8 of requests
    server backend2.example.com:8080 weight=2;  # gets 2/8 of requests
    server backend3.example.com:8080 weight=1;  # gets 1/8 of requests
    # Use case: backend1 is on a 4x larger instance
    
    # Default (no weight) = weight=1 each = standard round robin
}

# DNS round robin (simpler, no dedicated LB):
# Configure multiple A records for same hostname:
# api.example.com → 10.0.1.1
# api.example.com → 10.0.1.2
# api.example.com → 10.0.1.3
# DNS clients cycle through returned IPs
# Limitation: no health checks, no sticky sessions, TTL delays
```

---

### 🔄 How It Connects (Mini-Map)

```
Load Balancing
(the parent concept)
        │
        ▼
Round Robin  ◄──── (you are here)
(sequential distribution algorithm)
        │
        ├── Least Connections (better for mixed workload duration)
        ├── Consistent Hashing (better for cache affinity)
        └── Sticky Sessions (adds state to round robin for session affinity)
```

---

### 💻 Code Example

**Testing round robin distribution with curl:**

```bash
# Deploy 3 backends, verify round-robin distribution:
for i in $(seq 1 9); do
  curl -s http://api.example.com/health | jq -r '.instance_id'
done
# Expected output (round-robin):
# backend-1
# backend-2
# backend-3
# backend-1
# backend-2
# backend-3
# backend-1
# backend-2
# backend-3
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Round Robin ensures equal load on all servers | It ensures equal request count, not equal CPU/memory load. A server handling one 30-second request is more loaded than a server that handled ten 1ms requests — but round-robin distributed these evenly by count |
| DNS round robin is equivalent to load balancer round robin | DNS round-robin has no health checks (routes to dead servers), no persistence, variable TTL caching (clients may reuse one IP for minutes), and no session affinity. Software load balancers are superior for production traffic |
| Weighted round robin is complex to configure | Most load balancers support weight as a simple integer in server configuration. The complexity is only in determining correct weight values (capacity benchmarking) |
| Round Robin is outdated and shouldn't be used | Round Robin is appropriate for homogeneous workloads (similar request cost, equal-capacity servers). It's the default in many systems for good reason — it's simple, fast, and predictable |

---

### 🔥 Pitfalls in Production

**Round robin + slow backend = uneven load distribution:**

```
PROBLEM:
  5 backends, round-robin. Backend 3 running on degraded hardware.
  Backend 3: responds in 800ms (normal: 50ms for others).
  Round-robin: sends 20% of requests to Backend 3.
  Backend 3: builds up 100 active connections (all waiting for slow responses).
  Other backends: each at 5-10 active connections.
  
  Clients: 20% of requests take 800ms instead of 50ms.
  P99 latency: dramatically elevated by the slow backend.
  
FIX:
  Switch to least_conn or least_time (nginx):
  upstream backend {
    least_conn;          # route to backend with fewest active connections
    # OR:
    # least_time header; # route to fastest backend by response time
    
    server backend1:8080;
    server backend2:8080;
    server backend3:8080;  # naturally gets fewer requests when slow
  }
  
  ALSO: set max_fails + fail_timeout to remove consistently slow backend:
    server backend3:8080 max_fails=3 fail_timeout=30s;
    # 3 failures within 30s → remove from rotation for 30s
    # Slow (not failing) backend: not removed — use passive health checks
```

---

### 🔗 Related Keywords

- `Load Balancing` — the parent concept; Round Robin is one of many LB algorithms
- `Least Connections` — better algorithm when request duration varies significantly
- `Weighted Round Robin` — extends Round Robin for heterogeneous server capacities
- `Sticky Sessions` — adds session affinity on top of Round Robin
- `Consistent Hashing (Load Balancing)` — hash-based alternative for cache affinity

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Sequential cyclic distribution:           │
│              │ req1→S1, req2→S2, req3→S3, req4→S1...    │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Homogeneous servers, similar request cost,│
│              │ simple stateless API workloads            │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Variable request duration; heterogeneous  │
│              │ server capacities; cache affinity needed   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Dealing cards evenly — fair by count,    │
│              │  not by processing time."                 │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Least Connections → Consistent Hashing    │
│              │ → Sticky Sessions                         │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You have a REST API with two endpoint types: `GET /products/{id}` (10ms avg) and `POST /reports/generate` (45 second avg). All go to the same backend pool of 5 servers using round-robin. Over 10 minutes, 10,000 GET requests and 100 POST requests arrive uniformly. Calculate the approximate number of active report-generation connections on each server at any given moment. At what point does a server's active report-generation connections become a capacity problem, and how would you architect the system to separate these two traffic patterns?

**Q2.** A distributed cache cluster uses Round Robin to distribute cache read requests across 5 nodes. Each node caches different data independently (no replication). Cache hit rate per node: 80%. You add 2 more nodes (now 7 total). What happens to the overall cache hit rate immediately after adding nodes (before data is cached on new nodes), and how does this differ from what would happen with Consistent Hashing? Calculate the hit rate impact for both algorithms.
