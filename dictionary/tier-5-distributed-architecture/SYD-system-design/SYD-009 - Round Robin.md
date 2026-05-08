---
layout: default
title: "Round Robin"
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 9
permalink: /system-design/round-robin/
id: SYD-009
category: System Design
difficulty: ★☆☆
depends_on: Load Balancing, Horizontal Scaling
used_by: Load Balancing, Stateless Services
related: Least Connections, Consistent Hashing, Weighted Round Robin
tags:
  - algorithm
  - load-balancing
  - scaling
  - distribution
  - foundational
---

# SYD-009 - Round Robin

⚡ TL;DR - A simple load balancing algorithm that distributes requests to servers in a repeating cycle (first request to Server 1, second to Server 2, etc.)-fair and simple, but assumes all servers are identical.

| #684            | Category: System Design                                     | Difficulty: ★☆☆ |
| :-------------- | :---------------------------------------------------------- | :-------------- |
| **Depends on:** | Load Balancing, Horizontal Scaling                          |                 |
| **Used by:**    | Load Balancing, Stateless Services                          |                 |
| **Related:**    | Least Connections, Consistent Hashing, Weighted Round Robin |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You have 5 identical servers behind a load balancer. How does the LB decide which server gets the next request? If it's random, some servers might get lucky and handle more traffic (bursty). If it's always Server 1, Server 1 becomes the bottleneck. You need a deterministic, fair way to divide requests.

**THE BREAKING POINT:**
Without a predictable algorithm, traffic distribution becomes unpredictable. Some servers starve while others overflow.

**THE INVENTION MOMENT:**
"This is why round robin was created-the simplest fair algorithm: rotate through servers in order."

---

### 📘 Textbook Definition

Round robin is a load balancing algorithm that distributes requests sequentially across a pool of servers in a circular order. The load balancer maintains a pointer to the current server; each incoming request increments the pointer to the next server (wrapping around when reaching the end of the pool). Round robin assumes all servers are identical in capacity and performance; it provides no consideration for current server load, connection count, or latency.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Take turns: Server 1, then Server 2, then Server 3, repeat.

**One analogy:**

> A teacher calls on students in a classroom. Instead of always asking Alice, the teacher rotates: Alice, Bob, Carol, Diana, then back to Alice. Everyone gets a fair turn.

**One insight:**
Round robin works great when all servers are identical. It breaks horribly when one server is much slower than others-it still gets the same share of traffic, causing bottlenecks.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. All servers are assumed identical in capacity
2. All requests are assumed equivalent (same processing cost)
3. Distribution must be deterministic and fair (every server gets equal traffic)

**DERIVED DESIGN:**
The load balancer keeps an index: initially 0. When a request arrives, send it to server[index], then increment index. When index reaches the pool size, wrap back to 0. This ensures every server gets exactly one request before any server gets a second. It's simple to implement (single counter) and predictable.

**THE TRADE-OFFS:**
**Gain:** Simplicity. A single integer counter. No state about server health, load, or latency. Works for homogeneous servers. Deterministic behavior (good for testing).

**Cost:** Ignores server state. If Server 1 is slow, LB still sends it requests at the same rate as others. If Server 2 crashes, LB sends requests to it anyway (relying on separate health checks to remove it). If server pools are heterogeneous (different specs), some servers are underutilized.

---

### 🧪 Thought Experiment

**SETUP:**
5 identical app servers, each handling 100 requests/second max. Total capacity: 500 req/s. Load balancer uses round robin. 500 requests arrive simultaneously.

**WHAT HAPPENS WITHOUT ROUND ROBIN:**
If LB sends all 500 to Server 1 (no algorithm): Server 1 overflows (100 req/s capacity), queues form, requests timeout. Servers 2–5 idle. Disaster.

**WHAT HAPPENS WITH ROUND ROBIN:**
LB distributes: Reqs 1–100 to Server 1, 101–200 to Server 2, 201–300 to Server 3, 301–400 to Server 4, 401–500 to Server 5. Each server gets 100 req/s (its max capacity). All requests succeed. System is fair and balanced.

**THE INSIGHT:**
Round robin ensures no single server is starved of work and no single server is overwhelmed-if all servers are identical.

---

### 🧠 Mental Model / Analogy

> A deli has 4 cashiers. Customers arrive and line up. Instead of all going to Cashier 1, the deli routes customers round-robin: Customer 1 to Cashier 1, Customer 2 to Cashier 2, Customer 3 to Cashier 3, Customer 4 to Cashier 4, Customer 5 back to Cashier 1. All cashiers are equally busy. Fair.

- "Customer arrival" → incoming request
- "Cashiers" → backend servers
- "Round-robin routing" → rotating pointer
- "Next cashier in sequence" → next server in pool

**Where this analogy breaks down:** Unlike cashiers, if one server becomes slow (checkout takes 5 minutes instead of 2), round robin doesn't adapt-it still sends traffic equally, causing a bottleneck at that cashier.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
The load balancer alternates between servers: request 1 goes to Server 1, request 2 to Server 2, request 3 to Server 3, etc. Then it loops back. Everyone gets a fair turn.

**Level 2 - How to use it (junior developer):**
Configure your load balancer (NGINX, AWS ELB) to use round-robin algorithm. Ensure all backend servers are identical (same CPU, RAM, same app version). Deploy and send traffic. Monitor that traffic is roughly equal across servers. If one server is consistently slower, investigate why (code issue, resource contention) and fix it, not the LB algorithm.

**Level 3 - How it works (mid-level engineer):**
The LB maintains a counter (next_server) starting at 0. For each request: server_to_use = servers[next_server % pool_size]; next_server++. The counter increments atomically (thread-safe) for each request. In multi-threaded LBs, a mutex protects the counter. CPU cost is negligible-one increment and one modulo operation. Stateless: no memory needed beyond the counter.

**Level 4 - Why it was designed this way (senior/staff):**
Round robin is the oldest, simplest load balancing algorithm-dating to early NTP round-robin and DNS round-robin. It requires zero knowledge about server state, making it robust and failure-safe. Modern LBs use more sophisticated algorithms (least-connections, weighted), but round robin remains the default in many systems because of its simplicity and predictability. Its weakness (ignoring server health) is mitigated by separate health checks.

---

### ⚙️ How It Works (Mechanism)

Round robin operation:

```
LB State: next_server = 0, pool_size = 5

Request 1 arrives
  → Assign to: pool[0 % 5] = Server 1
  → next_server = 1

Request 2 arrives
  → Assign to: pool[1 % 5] = Server 2
  → next_server = 2

Request 3 arrives
  → Assign to: pool[2 % 5] = Server 3
  → next_server = 3

Request 4 arrives
  → Assign to: pool[3 % 5] = Server 4
  → next_server = 4

Request 5 arrives
  → Assign to: pool[4 % 5] = Server 5
  → next_server = 5

Request 6 arrives
  → Assign to: pool[5 % 5] = Server 1 (wrap around)
  → next_server = 6

→ Pattern repeats
```

**In Happy Path:**
Requests 1–100 evenly distributed. Each server gets ~20 requests. All servers 20% CPU. Done.

**When Something Goes Wrong:**
Server 2 crashes. LB still sends requests to it (next_server counter keeps rotating). Health check detects Server 2 down. Server 2 removed from pool (now 4 servers). Future requests rotate among remaining 4. Existing connections to Server 2 fail; clients retry; retry hits healthy server. Recovery: ~30 seconds (one health check cycle).

---

### 🔄 The Complete Picture - End-to-End Flow

```
Requests Arrive (1000/sec)
    ↓
ROUND ROBIN ALGORITHM (YOU ARE HERE)
next_server = 0, 1, 2, 3, 4, 0, 1, 2...
    ↓
Request routed to Server[next_server % 5]
    ↓
Server processes
    ↓
Response returned

Health Check Path (Every 5 seconds):
    ↓
LB calls /health on each server
    ├─ Server 1: 200 OK → healthy, stays in pool
    ├─ Server 2: timeout → unhealthy, remove from pool
    ├─ Server 3: 200 OK → healthy
    ├─ Server 4: 200 OK → healthy
    └─ Server 5: 200 OK → healthy

New Request arrives:
    ↓
Pool is now [1, 3, 4, 5] (Server 2 removed)
    ↓
Rotate among remaining 4
```

**WHAT CHANGES AT SCALE:**
At 1000 req/s with round robin, distribution is perfect-each of 10 servers gets 100 req/s. At 1 million req/s, the LB CPU handling round-robin increments becomes negligible (modern CPUs do billions of ops/sec). The algorithm scales linearly forever-round robin is O(1), no degradation at scale.

---

### 💻 Code Example

Round robin is simple. Here's implementation:

**Example 1 - NGINX Round Robin Config:**

```nginx
upstream backend {
    server app-1.internal:5000;
    server app-2.internal:5000;
    server app-3.internal:5000;
    # Default is round-robin
}

server {
    listen 80;
    location / {
        proxy_pass http://backend;
    }
}
```

**Example 2 - Pseudocode Implementation:**

```python
class RoundRobinLB:
    def __init__(self, servers):
        self.servers = servers
        self.next_server = 0
        self.lock = threading.Lock()

    def get_next_server(self):
        with self.lock:  # Thread-safe
            server = self.servers[self.next_server % len(self.servers)]
            self.next_server += 1
        return server

    # Usage:
    lb = RoundRobinLB(['server1', 'server2', 'server3'])
    for request in incoming_requests:
        server = lb.get_next_server()
        forward_request(request, server)
        # Request 1 → server1
        # Request 2 → server2
        # Request 3 → server3
        # Request 4 → server1 (wrap)
```

**Example 3 - Go Implementation (High-Performance):**

```go
type RoundRobinLB struct {
    servers   []string
    nextIdx   int
    mu        sync.Mutex
}

func (lb *RoundRobinLB) GetNextServer() string {
    lb.mu.Lock()
    defer lb.mu.Unlock()

    server := lb.servers[lb.nextIdx%len(lb.servers)]
    lb.nextIdx++
    return server
}

// Usage in HTTP handler:
func handleRequest(w http.ResponseWriter, r *http.Request) {
    server := lb.GetNextServer()
    proxy.Director = func(req *http.Request) {
        req.URL.Scheme = "http"
        req.URL.Host = server
    }
    proxy.ServeHTTP(w, r)
}
```

---

### ⚖️ Comparison Table

| Algorithm             | CPU Usage      | Fairness                 | Adapts to Load | Best For                                |
| --------------------- | -------------- | ------------------------ | -------------- | --------------------------------------- |
| **Round Robin**       | Minimal (O(1)) | Perfect (identical load) | No             | Identical servers, simple systems       |
| **Least Connections** | Low            | Good (adapts to latency) | Yes            | Mixed workloads, varying request times  |
| **IP Hash**           | Minimal        | Not guaranteed           | No             | Sticky sessions, cache locality         |
| **Weighted RR**       | Low            | Good (manual tuning)     | No             | Heterogeneous servers (different specs) |
| **Random**            | Minimal        | Good over time           | No             | Simplicity, low overhead                |

**How to choose:** Use round robin if servers are truly identical and requests are quick. Use least-connections if request times vary. Use IP-hash if you need session stickiness. Use weighted if servers have different capacity.

---

### 🔁 Flow / Lifecycle

Round robin is stateless-just a counter:

```
START: LB initialized, next_server = 0
  ↓
CONTINUOUS:
  Request arrives
    → next_server = next_server % pool_size
    → Forward to servers[next_server]
    → next_server += 1
    → Loop

Server Added:
  → Pool size increases
  → Round-robin continues, now includes new server automatically

Server Removed:
  → Pool size decreases
  → Future rotations skip removed server
```

---

### ⚠️ Common Misconceptions

| Misconception                                          | Reality                                                                                                            |
| ------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------ |
| "Round robin is the best algorithm"                    | It's best only for identical servers with quick requests. Other algorithms outperform it for heterogeneous setups. |
| "Round robin guarantees all servers get equal traffic" | It does IF the counter increments fairly. Bugs in thread-safety can cause skew.                                    |
| "Round robin has latency overhead"                     | Negligible-one modulo operation per request. < 1 microsecond.                                                      |
| "Round robin can detect slow servers"                  | No. Health checks are separate. RR keeps sending traffic to slow servers even if they're bottlenecks.              |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: One Server Much Slower Than Others**

**Symptom:**
Round robin across 5 servers. Server 3 is consistently slower. Total throughput is now capped by Server 3's slowness-becomes the bottleneck even though 4 other servers have idle capacity.

**Root Cause:**
Round robin doesn't adapt to server performance. It assumes all servers are identical. Server 3 may be older hardware, CPU-constrained, or running a slow code path (bad SQL query, memory leak).

**Diagnostic Command:**

```bash
# Check response time per server
tail -f /var/log/nginx/access.log | \
  awk '{split($9, a, "."); print a[1], $10}' | \
  sort | uniq -c

# If Server 3 avg response time > 2x others: investigate
# Check Server 3 CPU
ssh server-3
top -b -n 1 | grep "Cpu(s)"

# Check Server 3 logs
tail -100 /var/log/app.log | grep -i "slow\|error"
```

**Fix:**
Bad approach: Keep using round robin and accept slower throughput.
Good approach: (1) Fix Server 3 (upgrade hardware, optimize code, clear cache). (2) Switch algorithm to least-connections. (3) Use weighted round-robin (give Server 3 half weight).

**Prevention:**
Before production, load-test all servers to verify identical performance. Use least-connections algorithm by default (more robust). Monitor response time per server; alert if any server > 20% slower than average.

---

**Failure Mode 2: Uneven Distribution Due to Connection Pooling**

**Symptom:**
Client uses connection pooling: 10 persistent connections to LB. All 10 connections route to Server 1 (sticky due to first request routing). Servers 2–5 get no traffic.

**Root Cause:**
Round robin increments per request, not per connection. With connection pooling, the first request on a connection determines routing for all future requests on that connection. Depending on LB implementation, may not rebalance.

**Diagnostic Command:**

```bash
# Check connection count per server
netstat -an | grep ESTABLISHED | awk '{print $5}' | sort | uniq -c
# If Server 1 has way more connections: connection stickiness

# Check if LB is rebalancing per request
tcpdump -i eth0 -n | grep "destination" | awk '{print $5}' | sort | uniq -c
```

**Fix:**
Bad approach: Accept uneven connection distribution.
Good approach: (1) LB should rebalance on each request, not per-connection (requires HTTP-aware LB, not TCP). (2) Use DNS round-robin + connection pooling (pools to different IPs). (3) Use least-connections algorithm to prefer less-connected servers.

**Prevention:**
Use Layer 7 (HTTP) load balancing, not Layer 4 (TCP). Layer 7 LBs rebalance per HTTP request even if connections are pooled. Monitor connections per server; alert if skew > 50%.

---

**Failure Mode 3: Counter Overflow in Long-Lived LB**

**Symptom:**
LB has been running for months. Next_server counter reaches max int (2 billion). Counter overflows, wraps to 0 or negative. Routing becomes erratic.

**Root Cause:**
Integer overflow. In languages without bounds checking (C, C++), incrementing past INT_MAX causes undefined behavior. In Python/Java, rarely happens because of automatic big integers.

**Diagnostic Command:**

```bash
# Check LB uptime and request count
ps aux | grep nginx
# uptime: months
# At 1 million req/s, counter hits 2^31 in ~2000 seconds = 30 minutes
# For 1000 req/s, hits 2^31 in ~25 days

# Check if any errors in LB logs
tail -f /var/log/nginx/error.log | grep "overflow\|negative"
```

**Fix:**
Bad approach: Ignore and hope it doesn't happen.
Good approach: (1) Use 64-bit counter (instead of 32-bit). (2) Modulo the counter periodically: `next_server = next_server % pool_size`. (3) Use modulo in each iteration (modern LBs do this).

**Prevention:**
Use 64-bit integers for counters. In C++, use `uint64_t` instead of `int`. In modern NGINX/HAProxy, not an issue (they handle it).

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Load Balancing` - the context where round robin is used
- `Horizontal Scaling` - why you need a load balancing algorithm

**Builds On This (learn these next):**

- `Least Connections` - more sophisticated algorithm that adapts to server state
- `Consistent Hashing` - advanced algorithm for distributed systems
- `Weighted Round Robin` - variant that accounts for server capacity differences

**Alternatives / Comparisons:**

- `Least Connections` - better for varying request times
- `IP Hash` - for sticky sessions
- `Random` - similar simplicity, different distribution

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Rotate requests through servers     │
│              │ in a circle: Server 1, 2, 3, 1, 2, 3│
├──────────────┼────────────────────────────────────────┤
│ PROBLEM IT   │ Need a fair, simple way to          │
│ SOLVES       │ distribute traffic when servers     │
│              │ are identical                        │
├──────────────┼────────────────────────────────────────┤
│ KEY INSIGHT  │ Ignores server state-works great    │
│              │ for identical servers, breaks       │
│              │ when one server is slow             │
├──────────────┼────────────────────────────────────────┤
│ USE WHEN     │ All servers identical; requests     │
│              │ quick; load light; simplicity > HA  │
├──────────────┼────────────────────────────────────────┤
│ AVOID WHEN   │ Servers heterogeneous (different    │
│              │ capacity); request times vary       │
│              │ widely; need adaptive balancing     │
├──────────────┼────────────────────────────────────────┤
│ TRADE-OFF    │ [Simple, fast O(1)] vs [no          │
│              │ adaptation to actual load]          │
├──────────────┼────────────────────────────────────────┤
│ ONE-LINER    │ "Fair and simple, but blind to the  │
│              │ real state of servers."             │
├──────────────┼────────────────────────────────────────┤
│ NEXT EXPLORE │ Least Connections → Consistent      │
│              │ Hashing → Weighted Algorithms       │
└──────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Round robin sends equal traffic to 5 servers. Server 3 has a memory leak-every request leaks 10 MB. After 1 hour, Server 3 is out of memory and crashes. Round robin kept sending it 20% of traffic despite the problem. Should you have used a different algorithm? What would it catch?

**Q2.** A client opens 10 persistent TCP connections and uses them for all future requests (connection pooling). With round robin at the TCP level, these 10 connections might all land on one server (sticky). What's the architectural solution-should you change the algorithm or change how clients connect?
