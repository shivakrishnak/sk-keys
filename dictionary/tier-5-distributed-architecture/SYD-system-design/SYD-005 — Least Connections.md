---
layout: default
title: "Least Connections"
parent: "System Design"
nav_order: 5
permalink: /system-design/least-connections/
number: "SYD-005"
category: System Design
difficulty: ★★☆
depends_on: Load Balancing, Round Robin, Connection Pooling
used_by: Load Balancing, Distributed Systems
related: Round Robin, Weighted Round Robin, Consistent Hashing
tags:
  - algorithm
  - load-balancing
  - adaptive
  - intermediate
  - distribution
---

# SYD-005 — Least Connections

⚡ TL;DR — A load balancing algorithm that routes each new request to whichever server currently has the fewest active connections—adapts to actual server load instead of blindly alternating.

| #685            | Category: System Design                                | Difficulty: ★★☆ |
| :-------------- | :----------------------------------------------------- | :-------------- |
| **Depends on:** | Load Balancing, Round Robin                            |                 |
| **Used by:**    | Load Balancing, Microservices                          |                 |
| **Related:**    | Round Robin, Weighted Round Robin, Adaptive Algorithms |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You're using round robin. Traffic arrives at 1000 req/sec. But requests have varying duration: some finish in 1ms (quick query), others take 500ms (slow report generation). Round robin treats all requests as equal—sends 200 to each server. But the slow requests pile up. Server 1 has 100 fast requests (100ms total). Server 2 has 100 slow requests (50,000ms total). Server 2 becomes the bottleneck. One server is drowning while others are idle.

**THE BREAKING POINT:**
Round robin doesn't account for how long requests take. When request times vary, equal distribution by count doesn't mean equal load by time.

**THE INVENTION MOMENT:**
"This is why least connections was created—pick the server with fewest active requests, so slower servers get fewer requests."

---

### 📘 Textbook Definition

Least connections is a load balancing algorithm that maintains a count of active connections to each server. When a new request arrives, the load balancer forwards it to the server with the smallest active connection count. This adapts to varying request durations—servers processing slow requests naturally accumulate more pending requests, so new traffic avoids them. Requires active connection tracking on the load balancer.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Send the next customer to the cashier with the shortest line.

**One analogy:**

> A grocery store has 5 cashiers. Instead of assigning customers round-robin (cashier 1, 2, 3, 4, 5, repeat), assign to the cashier with fewest customers in line. If Cashier 2 has 3 people and everyone else has 1, route the next customer to Cashier 1 (or anyone else with 1). The system self-balances as fast cashiers work through lines quickly and slow cashiers accumulate customers.

**One insight:**
Least connections is a form of "adaptive" load balancing—it responds to actual server state in real time. It outperforms round robin when request times vary, but adds overhead (tracking connections).

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Servers process requests sequentially or concurrently (but connection count = active work)
2. Connection count is visible/trackable by load balancer
3. Shorter-lived connections = server available sooner for new work

**DERIVED DESIGN:**
The load balancer maintains a counter for each server: connections[server_id]. When a request arrives, the LB looks at all counters and picks the server with the minimum count. It increments that server's counter, forwards the request, and waits for the response. When the response completes, it decrements the counter. Over time, servers with fast processing have low counts (connections drain quickly), so they get more new requests. Servers with slow requests accumulate (higher counts), so they get fewer new requests. Self-regulating.

**THE TRADE-OFFS:**
**Gain:** Adapts to actual load. Doesn't punish slow servers with equal traffic. Better throughput than round robin when request times vary.

**Cost:** Must track connections per server. O(N) to find minimum (can optimize with priority queue). More complex. May create "stickiness" (slow server serves same connection longer, gets routed fewer new requests correctly, but may cause cascading if one server is much slower).

---

### 🧪 Thought Experiment

**SETUP:**
5 servers, each with max capacity 100 connections. Requests have variable duration: 90% are 1ms fast queries, 10% are 1000ms slow reports. Total traffic: 1000 requests/second.

**WHAT HAPPENS WITH ROUND ROBIN:**
RR distributes 200 req/s to each server (equal count). After 1 second: Server 1 has 1800 fast (1ms each) + 200 slow (1000ms each). At any moment: ~200 connections pending (some finishing, some starting). Server 2 same. All servers equally overloaded. System is balanced by count, but imbalanced by actual processing time. Total latency: P99 = 1500ms (stuck behind slow requests).

**WHAT HAPPENS WITH LEAST CONNECTIONS:**
LC sends requests to server with minimum active connections. Initially: all 5 servers have 0 connections. Request 1 → Server 1 (0 connections). Request 2 → Server 2 (0 connections). As fast requests finish quickly, their connections drop. As slow requests accumulate, their servers' connection counts rise. After a while: Server 1 has 5 active (fast); Server 2 has 8 active (mix); Server 3 has 150 active (many slow requests pending). New request → routed to Server 1 (minimum). Slower servers naturally get fewer new requests. System self-balances. P99 latency: 200ms (fast requests never queue behind many slow ones).

**THE INSIGHT:**
Least connections is adaptive. It doesn't need to know request duration—just connection count reveals it implicitly.

---

### 🧠 Mental Model / Analogy

> At a bank with 5 tellers: Instead of routing customers round-robin, route to the teller with fewest people waiting. If one teller handles complex transactions (takes 10 minutes), their line grows. New customers avoid that line, going to faster tellers. The queue lengths self-adjust to teller speed.

- "Customer" → request
- "Teller" → server
- "People in line" → active connections
- "Complex vs simple transactions" → slow vs fast requests
- "Route to fewest people" → least connections algorithm

**Where this analogy breaks down:** A customer chooses their teller based on line length. Here, the load balancer makes the choice, and the choice is transparent to clients.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Send the next request to whichever server is currently handling the fewest requests. Busy servers get a break; idle servers get more work. Self-adjusts automatically.

**Level 2 — How to use it (junior developer):**
Configure your load balancer to use "least connections" algorithm instead of round robin. NGINX: `upstream backend { least_conn; ... }`. AWS ELB: select "least outstanding requests". Deploy and monitor. Verify that requests are routed fairly. If one server is consistently slower, it will naturally get fewer requests.

**Level 3 — How it works (mid-level engineer):**
The LB maintains a map: {server_id → connection_count}. For each incoming request: idx = argmin(connection_count.values()). Forward request to servers[idx]. connection_count[idx]++. When request completes (response sent), connection_count[idx]--. This is O(N) to find minimum each time. Modern LBs optimize: use a min-heap (O(log N) per operation) or track minimum explicitly. The challenge: tie-breaking (if two servers have same count, pick randomly or by ID).

**Level 4 — Why it was designed this way (senior/staff):**
Least connections emerged in the 1990s as people realized round robin's weakness. It's more sophisticated than round robin but simpler than stateful load balancing (session stickiness). The tradeoff is acceptable complexity for significant throughput improvements in real workloads where request times vary. Modern cloud LBs use even more sophisticated algorithms (weighted LC, latency-aware), but LC is the standard.

---

### ⚙️ How It Works (Mechanism)

Least connections operation:

```
LB State:
  connections = {Server1: 0, Server2: 0, Server3: 0}

Request 1 arrives
  → Min connections: all tied at 0, pick Server 1
  → connections[Server1] = 1
  → Forward to Server 1

Request 2 arrives
  → Min connections: Server 2 or 3 at 0, pick Server 2
  → connections[Server2] = 1
  → Forward to Server 2

Request 3 arrives (fast, completes in 1ms)
  → Response from Server 1
  → connections[Server1] = 0

Request 4 arrives
  → Min connections: Server 1 at 0, pick Server 1
  → connections[Server1] = 1
  → Forward to Server 1

Request 5 arrives (slow, takes 500ms)
  → Forward to Server 3 (currently 0)
  → connections[Server3] = 1, but stays 1 for 500ms

Request 6 arrives (after 100ms)
  → Min connections: Server 2 at 0, pick Server 2
  → connections[Server2] = 1

Request 7 arrives (after 200ms)
  → Connections: {1, 1, 1} all tied
  → Pick Server 1 (arbitrary)

...

Server 1 fast, processes requests 1, 4, 7: 3/10 requests
Server 2 fast, processes requests 2, 6: 2/10 requests
Server 3 slow, processes request 5 (long): 1/10 requests
```

**In Happy Path:**
Fast servers drain connections quickly → low counts → get routed more requests → high throughput.
Slow servers accumulate connections → high counts → get routed fewer requests → still serving their backlog.
System self-balances.

**When Something Goes Wrong:**
Server 1 crashes. LB still tracks it (connections[Server1] = 5). Health check fails. Server 1 removed from pool. Future requests avoid it. Existing connections timeout and retry. Recovery: 30 seconds.

---

### 🔄 The Complete Picture — End-to-End Flow

```
Request Arrives
    ↓
LEAST CONNECTIONS ALGORITHM (YOU ARE HERE)
Find server with min(active_connections)
    ↓
Forward to that server
    ↓
increment connection_count[server]
    ↓
Server processes request
    ↓
Response returned
    ↓
decrement connection_count[server]
    ↓
Client receives response

Parallel: Server Comparison
    ↓
If Server 1: 5 connections (slow requests stuck)
   Server 2: 0 connections (fast, idle)
   Server 3: 2 connections (busy but not overloaded)
    ↓
Next request → Server 2 (minimum)
    ↓
No request → Server 1 (would overload further)
```

**WHAT CHANGES AT SCALE:**
At 1 million req/s, finding min connection count becomes expensive (1 million iterations per request in O(N) implementation). Mitigation: use data structures like heaps (O(log N)) or track min in real-time. Modern LBs handle this. At scale, connection counts become large (millions of active), but the algorithm's logic remains the same.

---

### 💻 Code Example

Least connections requires connection tracking:

**Example 1 — NGINX Config:**

```nginx
upstream backend {
    least_conn;  # Enable least connections algorithm

    server app-1.internal:5000;
    server app-2.internal:5000;
    server app-3.internal:5000;
}

server {
    listen 80;
    location / {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Connection "";  # Enable connection pooling
    }
}
```

**Example 2 — Python Implementation:**

```python
import heapq
from collections import defaultdict

class LeastConnectionsLB:
    def __init__(self, servers):
        self.servers = servers
        self.connection_count = defaultdict(int)
        # Min-heap: (count, server_id)
        self.heap = [(0, i) for i in range(len(servers))]
        heapq.heapify(self.heap)

    def get_least_connected_server(self):
        # Pop until we find a fresh min
        while self.heap:
            count, server_id = heapq.heappop(self.heap)
            if count == self.connection_count[server_id]:
                # Valid; use this server
                self.connection_count[server_id] += 1
                heapq.heappush(self.heap,
                    (self.connection_count[server_id], server_id))
                return self.servers[server_id]
        return None  # All servers dead

    def release_connection(self, server_id):
        self.connection_count[server_id] -= 1
        heapq.heappush(self.heap,
            (self.connection_count[server_id], server_id))

# Usage:
lb = LeastConnectionsLB(['server1', 'server2', 'server3'])
server = lb.get_least_connected_server()  # → server1 (all 0, first)
server = lb.get_least_connected_server()  # → server2 (second, count 0)
lb.release_connection(0)
server = lb.get_least_connected_server()  # → server1 (count now 0)
```

**Example 3 — Simulating Variable Request Times:**

```python
import threading
import time

class RequestHandler:
    def handle_request(self, server_id, duration_ms):
        self.lb.connection_count[server_id] += 1
        print(f"Request sent to {server_id}, connections: {dict(self.lb.connection_count)}")

        time.sleep(duration_ms / 1000.0)  # Simulate processing

        self.lb.connection_count[server_id] -= 1
        print(f"Request completed on {server_id}, connections: {dict(self.lb.connection_count)}")

# Simulate:
# Request 1: Server 1, 500ms (slow)
# Request 2: Server 2, 1ms (fast)
# Request 3: Should go to Server 2 (count=1) instead of Server 1 (count=1 but will be stuck)
```

---

### ⚖️ Comparison Table

| Algorithm             | Fairness                  | Adapts to Load | Complexity       | CPU Cost   | Best For                          |
| --------------------- | ------------------------- | -------------- | ---------------- | ---------- | --------------------------------- |
| **Round Robin**       | Perfect (equal count)     | No             | O(1)             | Minimal    | Identical servers, quick requests |
| **Least Connections** | Good (adapts to duration) | Yes            | O(N) or O(log N) | Low-Medium | Varying request times             |
| **Weighted LC**       | Good (manual tuning)      | Yes            | O(N) or O(log N) | Low-Medium | Heterogeneous servers             |
| **IP Hash**           | Depends on IPs            | No             | O(1)             | Minimal    | Sticky sessions                   |
| **Random**            | Good over time            | No             | O(1)             | Minimal    | Simple, unpredictable             |

**How to choose:** Use least connections by default—it's robust and handles most workloads. Round robin only if all requests are quick and identical. Weighted LC if servers have different specs.

---

### 🔁 Flow / Lifecycle

Least connections is continuous:

```
START: All servers, 0 active connections
  ↓
CONTINUOUS:
  Request arrives
    → Find min connection_count
    → Forward to that server
    → connection_count[server]++

  Request completes
    → connection_count[server]--

  Server slow → accumulates connections
    → Next requests go to other servers
    → Self-regulating

  New server added
    → connection_count = 0
    → Immediately gets routed requests (lowest count)

  Server fails
    → Connection count stales
    → Health check removes server
    → Connections rebalance among remaining
```

---

### ⚠️ Common Misconceptions

| Misconception                                         | Reality                                                                                                                               |
| ----------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| "Least connections is always better than round robin" | Not for identical, quick requests (overhead not justified). Only beneficial when request times vary.                                  |
| "Connection count = request processing time"          | Not exactly. One long request = high connection count (correct). But cached requests or pipelined requests confuse the metric.        |
| "Least connections eliminates queueing"               | No. Queues still exist if all servers are busy. LC just minimizes imbalance.                                                          |
| "Least connections is free"                           | Costs O(N) or O(log N) per request (find minimum), vs O(1) for round robin. Negligible at scale but measurable for millions of req/s. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Cascading Overload on Slow Server**

**Symptom:**
Server 1 becomes slow (due to GC pause, network hiccup). Its connection count rises from 50 to 200. LC avoids routing new requests to it (correct). But Server 1 is overloaded and takes even longer to recover. Backlog keeps growing. Eventually Server 1 crashes or is removed.

**Root Cause:**
Least connections doesn't have a "circuit breaker." It still sends requests to slow servers if they have fewer connections than a crashed server (connection count never decreases).

**Diagnostic Command:**

```bash
# Check connection count per server
netstat -an | grep ESTABLISHED | awk '{print $5}' | sort | uniq -c

# Check response time per server
tail -f /var/log/app.log | grep "response_time:" | awk -F, '{print $1, $2}' | sort | uniq -c

# Check Server 1 GC activity (Java)
jstat -gc <pid> 1000  # JVM GC stats
```

**Fix:**
Bad approach: Accept overload and hope server recovers.
Good approach: (1) Set connection count limits per server. (2) Add health checks that measure latency, not just /health endpoint. (3) Use circuit breaker (mark server down if response time > threshold). (4) Implement backpressure (reject requests if overloaded, instead of queueing forever).

**Prevention:**
Monitor not just connection count but also response time per server. Set alerts for response time > 2x average. Implement adaptive algorithms that consider latency, not just connection count.

---

**Failure Mode 2: Imbalance Due to Connection Pooling**

**Symptom:**
Clients use connection pooling (persistent connections). First connection lands on Server 1. All future requests on that connection go to Server 1 (TCP-level routing). Server 1 gets 10% of connections, others get 90%. Connection count is imbalanced.

**Root Cause:**
Least connections tracks active connections but doesn't rebalance within a connection (HTTP/1.1 keep-alive or connection pooling). The first request determines routing for all future requests on that connection.

**Diagnostic Command:**

```bash
# Check connections per server
netstat -an | grep ESTABLISHED | awk -F: '{print $NF}' | sort | uniq -c

# If one server has 90% of connections: imbalance

# Check load (requests/sec) per server
tail -f /var/log/nginx/access.log | \
  awk '{print $9}' | sort | uniq -c
```

**Fix:**
Bad approach: Ignore and accept imbalance.
Good approach: (1) Use Layer 7 (HTTP) load balancer that rebalances per HTTP request (not per connection). (2) Implement connection draining—close pooled connections periodically to force reconnection. (3) Use DNS round-robin + client-side load balancing.

**Prevention:**
Use HTTP-aware LB (Layer 7), not TCP-aware (Layer 4). Ensure LB can rebalance requests within a persistent connection.

---

**Failure Mode 3: Thundering Herd Cascading**

**Symptom:**
Database server goes down. Connections to it queue up infinitely (trying to reconnect). Connection count rises to millions. Least connections stops routing to it (count is highest). But eventually all servers are stuck retrying dead database. System cascades into failure.

**Root Cause:**
Least connections doesn't account for the cause of high connection counts. It assumes high counts = server is busy but working. If connections are stuck retrying dead resources, LC can't help.

**Diagnostic Command:**

```bash
# Check if requests are making progress
tail -f /var/log/app.log | grep "response_time:" | tail -10
# If response times are all huge (30s+): requests are stuck, not processing

# Check for retry loops
tail -f /var/log/app.log | grep "retry\|reconnect" | wc -l
# If high: cascading retries
```

**Fix:**
Bad approach: Let cascading fail.
Good approach: Implement circuit breaker. If a server fails health checks, mark it as "down" and stop sending requests entirely (don't queue retries indefinitely). Add timeout to retries.

**Prevention:**
Health checks must detect unavailable backends (not just /health endpoint up, but database connectivity up). Use circuit breaker pattern. Implement backpressure—reject requests if backend is down, don't queue forever.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Load Balancing` — the context where this is used
- `Round Robin` — the simpler algorithm to compare against
- `Connection Pooling` — how clients maintain connections

**Builds On This (learn these next):**

- `Weighted Round Robin` — for heterogeneous servers
- `Adaptive Load Balancing` — even more sophisticated (considers latency, not just connections)
- `Circuit Breaker` — to handle cascading failures in LC

**Alternatives / Comparisons:**

- `Round Robin` — simpler but less adaptive
- `IP Hash` — for sticky sessions
- `Weighted Algorithms` — for heterogeneous servers

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Route to server with fewest active   │
│              │ connections; adapts to actual load   │
├──────────────┼────────────────────────────────────────┤
│ PROBLEM IT   │ Round robin treats all requests      │
│ SOLVES       │ equally; fails when request times    │
│              │ vary widely                           │
├──────────────┼────────────────────────────────────────┤
│ KEY INSIGHT  │ Connection count implicitly reveals  │
│              │ server busyness without knowing      │
│              │ request duration                     │
├──────────────┼────────────────────────────────────────┤
│ USE WHEN     │ Requests have variable duration;     │
│              │ servers heterogeneous; need          │
│              │ adaptive balancing                   │
├──────────────┼────────────────────────────────────────┤
│ AVOID WHEN   │ All requests are quick & identical;  │
│              │ overhead of tracking counts not      │
│              │ justified                            │
├──────────────┼────────────────────────────────────────┤
│ TRADE-OFF    │ [Adaptive, good throughput] vs       │
│              │ [more complex, slightly higher       │
│              │ CPU cost]                            │
├──────────────┼────────────────────────────────────────┤
│ ONE-LINER    │ "Send to whoever's least busy,       │
│              │ not who's next in line."             │
├──────────────┼────────────────────────────────────────┤
│ NEXT EXPLORE │ Round Robin → Weighted LC →          │
│              │ Adaptive Algorithms                  │
└──────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Least connections routes to server with minimum active connections. If Server 1 becomes unresponsive (hanging connections never close), its connection count rises indefinitely. LC stops routing to it (good), but those hanging connections never drain. How is this problem solved in practice—what mechanism closes them?

**Q2.** Connection pooling: Client opens 10 persistent connections to the LB. Each goes to a different server initially (round-robin by TCP 4-tuple). Now all future requests on each connection stick to that server. Is LC broken, or is this the correct behavior? Should the LB rebalance mid-connection?
