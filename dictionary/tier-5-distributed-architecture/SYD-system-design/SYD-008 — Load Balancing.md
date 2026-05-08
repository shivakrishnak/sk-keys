---
layout: default
title: "Load Balancing"
parent: "System Design"
nav_order: 8
permalink: /system-design/load-balancing/
id: SYD-008
category: System Design
difficulty: ★★☆
depends_on: Horizontal Scaling, Networking, HTTP & APIs
used_by: Auto Scaling, High Availability, Distributed Systems
related: Round Robin, Least Connections, Consistent Hashing
tags:
  - scaling
  - distributed
  - networking
  - infrastructure
  - intermediate
---

# SYD-008 — Load Balancing

⚡ TL;DR — A system that distributes incoming traffic across multiple servers to prevent any single machine from becoming a bottleneck—essential for horizontal scaling and high availability.

| #683            | Category: System Design                            | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------- | :-------------- |
| **Depends on:** | Horizontal Scaling, Networking                     |                 |
| **Used by:**    | Auto Scaling, High Availability, Microservices     |                 |
| **Related:**    | Round Robin, Least Connections, Consistent Hashing |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You deployed your app to 10 servers. But clients don't know about all 10—they only know one IP address. Which server gets which request? If you tell all clients "connect to Server 1", then Server 1 becomes the bottleneck—it's handling all traffic while the other 9 servers sit idle. You haven't scaled at all.

**THE BREAKING POINT:**
Horizontal scaling requires a way to split traffic fairly across all machines. Without it, adding more servers is useless. One machine still gets all the requests.

**THE INVENTION MOMENT:**
"This is why load balancers were invented—to stand between clients and servers, distributing traffic intelligently so all servers share the work."

---

### 📘 Textbook Definition

A load balancer is a system (hardware device or software) that sits between clients and a pool of backend servers, receiving incoming requests and forwarding them to an available server based on a scheduling algorithm. Load balancers enable horizontal scaling by distributing work across multiple machines, improving throughput and reducing latency. They also provide health checking (removing failed servers) and connection management (draining connections gracefully).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A traffic cop that stands at an intersection and directs each car to the least-congested lane.

**One analogy:**

> A restaurant has one phone line (the load balancer) that takes reservations. Instead of all callers hitting the same host station directly, they call one number, and a receptionist assigns them to available servers. The receptionist knows when servers are full and routes new calls to open ones. If a server crashes, the receptionist stops sending calls there.

**One insight:**
The load balancer itself can become a bottleneck if not designed carefully. That's why modern systems use highly optimized load balancers (NGINX, HAProxy, cloud LBs) and sometimes multiple load balancers in parallel.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Clients must connect to a single point (load balancer), not multiple servers
2. Load balancer must intelligently choose which server handles each request (algorithm)
3. Load balancer must remove failed servers from the pool (health checks)
4. All servers must be stateless or have shared state (same database/cache)

**DERIVED DESIGN:**
Clients send requests to the load balancer's IP/hostname. The LB receives the request, consults its algorithm (round-robin, least-connections, etc.), and picks a backend server. The LB forwards the request to that server. The server responds; the LB forwards the response back to the client. The client doesn't know which backend server handled it (transparent). If you add a new server, the LB includes it in the pool automatically. If a server crashes, health checks detect it and remove it.

**THE TRADE-OFFS:**
**Gain:** Horizontal scaling is now possible. Traffic distributes fairly. One server failure doesn't bring down the system. You can add/remove servers without restarting.

**Cost:** The load balancer itself becomes infrastructure you must maintain. If it fails, all traffic stops (unless you have redundant LBs). There's added latency (extra network hop through LB). You need health checks, which add complexity.

---

### 🧪 Thought Experiment

**SETUP:**
An API receives 1000 requests/second. You have 5 identical app servers. Without a load balancer, all requests go to Server 1 (by default—clients only know one IP). With a load balancer, traffic should distribute evenly: ~200 req/s to each server.

**WHAT HAPPENS WITHOUT A LOAD BALANCER:**
Server 1: 1000 req/s (100% CPU—maxed out, requests timeout)
Servers 2–5: 0 req/s (idle, unused)
Users see 50% of requests fail (timeouts). System is useless despite having 5x capacity. Horizontal scaling doesn't work.

**WHAT HAPPENS WITH A LOAD BALANCER:**
Load balancer: 1000 req/s arrives → Routes 200 to each server using round-robin
Server 1: 200 req/s (20% CPU—healthy, fast responses)
Server 2: 200 req/s (20% CPU—healthy, fast responses)
... Servers 3–5: same
All requests succeed. System is now using all available capacity. Response times are fast.

**THE INSIGHT:**
Without a load balancer, horizontal scaling is theater—you added servers that do nothing. With a load balancer, horizontal scaling works: adding servers adds capacity.

---

### 🧠 Mental Model / Analogy

> A bank has multiple tellers. Without a queuing system (load balancer), all customers would go to Teller 1 because they don't know about Tellers 2–5. Teller 1 would be swamped; others would be idle. With a queue (load balancer), customers take a number and the system routes them to the next available teller. All tellers stay busy. New tellers can be added to the queue without customers noticing.

- "One teller overwhelmed" → single server without load balancer
- "Queue system routing customers" → load balancer
- "Next available teller" → load balancing algorithm
- "Teller is sick (not responding)" → health check removes failed server
- "New teller added to system" → scale-up transparent to customers

**Where this analogy breaks down:** Tellers handle customers sequentially; servers process requests in parallel. A server can handle 1000 requests/second simultaneously; a teller cannot.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A load balancer is a machine in the middle that receives traffic and sends it to different servers fairly. Like a toll booth that directs cars to different lanes, so one lane doesn't get all the traffic.

**Level 2 — How to use it (junior developer):**
Deploy your application to multiple identical servers. Configure them as a backend pool in your load balancer (AWS ELB, NGINX, HAProxy). Test that requests work from the load balancer's IP. Monitor that traffic distributes fairly. If response times are slow, add more servers to the backend pool.

**Level 3 — How it works (mid-level engineer):**
The load balancer receives an incoming request (TCP connection or HTTP request). It applies an algorithm (round-robin, least-connections, IP-hash) to pick a backend server from its pool. It establishes a new connection to that server, forwards the request, waits for the response, and sends it back to the client. It periodically health-checks each backend (HTTP GET /health) every 5 seconds; if a backend fails checks, it's marked as down and removed from the routing pool. Client IP is preserved or tunneled depending on configuration (to support logging on backends).

**Level 4 — Why it was designed this way (senior/staff):**
Early systems didn't have load balancers—they had one big server. As traffic grew, operators discovered they could split work across multiple servers if they had a router (LB). Modern load balancers are optimized for extreme throughput (NGINX handles millions of connections, AWS ELB is distributed cloud-native). The design decision is: single-point-of-failure risk vs. simplicity of scaling. Mitigated by running redundant LBs or cloud-managed LBs (highly available by default).

---

### ⚙️ How It Works (Mechanism)

Load balancing happens in these steps:

1. **Client Connects:**
   - Client sends request to load balancer's IP/hostname
   - LB listens on port 80 (HTTP) or 443 (HTTPS)

2. **Algorithm Chooses Server:**
   - LB applies algorithm to select backend from pool
   - Algorithm options: round-robin, least-connections, IP-hash, random, weighted

3. **Connection Forwarding:**
   - LB establishes connection to chosen backend
   - LB forwards request headers and body
   - LB waits for backend response

4. **Response Forwarding:**
   - Backend processes request, sends response to LB
   - LB forwards response to client
   - Connection closes

5. **Health Checking (Continuous):**
   - LB periodically (every 5s) sends health check to each backend
   - Typical health check: HTTP GET /health endpoint
   - If backend responds with 200 OK: marked healthy
   - If backend times out or returns 500: marked unhealthy, removed from pool

```
Clients              Load Balancer          Backend Pool
  │                      │                 ┌─────────┐
  ├─ Req 1 ──────────→ LB │ ─────────────→ │ Server1 │
  │                   Algorithm:           │ (20%CP) │
  ├─ Req 2 ──────────→ LB │ Round-Robin    └─────────┘
  │                      │
  ├─ Req 3 ──────────→ LB │ ─────────────→ ┌─────────┐
  │                      │ ─────────────→ │ Server2 │
  └─ Req 4 ──────────→ LB │                 │ (20%CP) │
                         │ ◄───────────── └─────────┘
                      Health check
                    (every 5 seconds)
```

**In Happy Path:**
Client 1 → LB picks Server 1 → Response fast → Client 1 satisfied
Client 2 → LB picks Server 2 → Response fast → Client 2 satisfied
Both servers share load equally.

**When Something Goes Wrong:**
Server 1 crashes → LB health check fails → Server 1 marked down → Client 3 arrives → LB picks Server 2 (only healthy option) → Response still succeeds. Downtime: 0 seconds.

---

### 🔄 The Complete Picture — End-to-End Flow

```
Incoming Request
    ↓
LOAD BALANCER RECEIVES
(YOU ARE HERE)
    ↓
Algorithm picks a backend server
    ↓
Request forwarded to backend
    ↓
Backend processes, returns response
    ↓
LB forwards response to client
    ↓
Client receives response

PARALLEL: Health Checking
    ↓
Every 5 seconds: LB → Backend /health endpoint
    ↓
Is backend responding?
    ├─ YES: Keep in pool
    └─ NO: Remove from pool, log failure

Scale-Up Path:
    New server added to backend pool
    ↓ (No client restart needed)
    LB includes it in round-robin
    ↓
    Immediately starts receiving traffic
```

**WHAT CHANGES AT SCALE:**
At 1000 req/s with 10 servers, LB is simple—routes 100 req/s per server. At 1 million req/s, a single LB becomes the bottleneck. Solutions: (1) Use cloud-managed LB (AWS ELB is auto-scaled), (2) multiple LBs in active-active, (3) DNS round-robin across LBs, (4) anycast routing to distribute LB instances globally.

---

### 💻 Code Example

Load balancers are operational/infrastructure, not code. But here's how they're configured:

**Example 1 — NGINX Load Balancer Config:**

```nginx
# /etc/nginx/nginx.conf
upstream backend {
    server app-server-1.internal:5000 weight=1;
    server app-server-2.internal:5000 weight=1;
    server app-server-3.internal:5000 weight=1;

    # Health check
    check interval=5000 rise=2 fall=5 timeout=2000 type=http;
    check_http_send "GET /health HTTP/1.0\r\n\r\n";
    check_http_expect_alive http_2xx;
}

server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://backend;  # Round-robin by default
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Requests to `api.example.com` are distributed round-robin across the 3 backends.

**Example 2 — AWS ELB Health Check + Auto Scaling:**

```python
# Infrastructure-as-code: Terraform
resource "aws_lb" "api" {
    name = "api-load-balancer"
    internal = false
    load_balancer_type = "application"

    # Health check configuration
    health_check {
        healthy_threshold = 2
        unhealthy_threshold = 2
        timeout = 3
        interval = 30
        path = "/health"
        matcher = "200"
    }
}

resource "aws_autoscaling_group" "api" {
    name = "api-asg"
    min_size = 3
    max_size = 10
    desired_capacity = 5

    # Scale up when CPU > 70%
    target_group_arns = [aws_lb_target_group.api.arn]
}
```

Auto-scaling automatically adds/removes servers from the load balancer's pool.

**Example 3 — Client-Side Health Check (detecting unhealthy LB):**

```python
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Retry logic: if LB is temporarily down, retry
session = requests.Session()
retry_strategy = Retry(
    total=3,
    backoff_factor=0.5,
    status_forcelist=[500, 502, 503, 504]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)

# If LB returns 502 (Bad Gateway), retry to different backend
response = session.get("http://api.example.com/users")
```

---

### ⚖️ Comparison Table

| Load Balancer Type | Throughput                | Latency                   | Cost                  | HA Built-in                    | Best For                               |
| ------------------ | ------------------------- | ------------------------- | --------------------- | ------------------------------ | -------------------------------------- |
| **AWS ELB**        | Very high (cloud-managed) | Low (optimized)           | Medium (pay per hour) | Yes (multi-AZ)                 | Production, high-traffic systems       |
| **NGINX**          | High (open-source)        | Very low (efficient)      | Low (free)            | No (must replicate manually)   | Startups, on-premise, fine control     |
| **HAProxy**        | Very high (optimized)     | Very low                  | Low (free)            | No (must configure redundancy) | High-performance systems               |
| **Layer 4 (TCP)**  | Very high                 | Very low                  | Medium                | Varies                         | Non-HTTP protocols, maximum throughput |
| **Layer 7 (HTTP)** | Medium                    | Higher (inspects content) | Medium                | Varies                         | HTTP APIs, routing by path/hostname    |

**How to choose:** Use cloud-managed LB (AWS ELB) for simplicity and HA. Use NGINX or HAProxy if you need fine control or low cost. Layer 4 (TCP) for maximum throughput; Layer 7 (HTTP) for routing intelligence.

---

### 🔁 Flow / Lifecycle

Load balancing is continuous:

```
START: LB running, 3 backends healthy
  ↓
CONTINUOUS: Receive requests, route to backends
  ├─ Request arrives → Apply algorithm → Pick backend → Forward
  │
  ├─ Every 5 seconds: Health check all backends
  │ ├─ Backends 1, 2, 3 respond OK: Continue routing
  │ └─ Backend 2 timeout: Mark down, remove from pool
  │
  ├─ New backend added to pool
  │ ├─ Health check: new backend responds OK: Add to rotation
  │
  └─ Backend fails health check 5 times → Permanent removal
       ↓
    New server launched (auto-scaling)
       ↓
    Health check: new server OK
       ↓
    Added to pool
       ↓
    Immediately starts receiving traffic
```

---

### ⚠️ Common Misconceptions

| Misconception                                       | Reality                                                                                                             |
| --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| "Load balancer eliminates single points of failure" | It IS a single point of failure. Redundant LBs are needed for true HA.                                              |
| "All load balancers use the same algorithm"         | Different algorithms (round-robin, least-connections, IP-hash) produce different results. Choose based on workload. |
| "Load balancer adds significant latency"            | Modern LBs add <1ms latency. Cloud LBs are optimized to microseconds. Negligible for most workloads.                |
| "Load balancer knows about your application logic"  | Layer 4 LBs don't. Layer 7 (HTTP) LBs can route by path/header, but don't execute your code.                        |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Uneven Traffic Distribution**

**Symptom:**
5 servers behind load balancer. Server 1 CPU: 80%. Servers 2–5 CPU: 20%. Traffic is unbalanced.

**Root Cause:**
Load balancer algorithm is round-robin or random, but backends are heterogeneous (Server 1 older/weaker hardware). Or Server 1 has a long-running request holding a connection (sticky session).

**Diagnostic Command:**

```bash
# Check LB algorithm
grep "upstream backend" /etc/nginx/nginx.conf
# If no specific algorithm: round-robin (default)

# Check server specs
aws ec2 describe-instances | grep InstanceType
# If different types: heterogeneous hardware

# Check response time per server
tail -f /var/log/nginx/access.log | \
  awk '{split($9, a, "."); print a[1], $10}' | \
  sort | uniq -c
```

**Fix:**
Bad approach: Accept imbalance.
Good approach: Switch to least-connections or latency-based algorithm. Ensure all servers are same spec. Or weight servers by capacity (high-spec gets 2x weight).

**Prevention:**
Use least-connections algorithm (not round-robin). Keep all backend servers identical. Monitor CPU per server. Alert if any server > 30% more CPU than average.

---

**Failure Mode 2: Health Check Flakiness**

**Symptom:**
Healthy servers are marked down and removed from pool. Requests bounce around. Recovery takes 5–10 minutes.

**Root Cause:**
Health check is too strict (short timeout, low threshold). One slow request or minor glitch causes server removal. Or backend app has startup lag (not responding to /health for 30 seconds after restart).

**Diagnostic Command:**

```bash
# Simulate health check manually
curl -v http://app-server-1.internal:5000/health
# If slow or not present: server fails health check

# Check LB health check config
grep -A5 "health_check" /etc/nginx/nginx.conf
# Check: timeout, interval, rise, fall thresholds

# Check app startup logs
tail -f /var/log/app.log | grep "health check"
```

**Fix:**
Bad approach: Ignore failures and hope they auto-recover.
Good approach: (1) Increase health check timeout (5s instead of 3s). (2) Increase rise threshold (need 3 successful checks before adding back). (3) Lower fall threshold (2 failures before removing). (4) Make /health endpoint fast (< 10ms).

**Prevention:**
Health check configuration is operational. Tune based on app startup time. Implement /health endpoint that returns fast (no heavy DB queries). Log every health check result. Alert on sudden health check failures.

---

**Failure Mode 3: Load Balancer Itself Becomes Bottleneck**

**Symptom:**
Added 10 more servers. Traffic still doesn't increase proportionally. LB CPU is 100%.

**Root Cause:**
Load balancer is processing all requests and can't keep up. It's the new bottleneck instead of servers.

**Diagnostic Command:**

```bash
# Check LB CPU
ssh load-balancer
top -b -n 1 | grep "Cpu(s)"

# Check network throughput on LB
iftop -i eth0
# If close to 10 Gbps (max NIC): LB maxed out
```

**Fix:**
Bad approach: Add more servers (doesn't help if LB is bottleneck).
Good approach: (1) Use cloud-managed LB (AWS auto-scales). (2) Add multiple LBs in parallel, split traffic via DNS. (3) Use Layer 4 LB (faster than Layer 7). (4) Enable connection multiplexing/keep-alive to reuse connections.

**Prevention:**
Monitor LB CPU and network utilization. When LB CPU > 70%, scale LB capacity. Use cloud-native LBs that auto-scale. Performance test LB before production to know its limits.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Horizontal Scaling` — the use case that makes load balancers necessary
- `Networking` — TCP/IP, ports, connections
- `HTTP & APIs` — Layer 7 load balancing uses HTTP semantics

**Builds On This (learn these next):**

- `Round Robin` — one load balancing algorithm
- `Least Connections` — alternative algorithm for uneven load
- `Consistent Hashing` — advanced algorithm for distributed caches/databases

**Alternatives / Comparisons:**

- `DNS Round-Robin` — poor-man's load balancing using DNS; doesn't monitor health
- `Sticky Sessions` — keeping one client's requests on same server (works with LB)
- `Session Affinity` — similar to sticky sessions; LB aware

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────┐
│ WHAT IT IS   │ A system that distributes traffic     │
│              │ across multiple servers fairly        │
├──────────────┼────────────────────────────────────────┤
│ PROBLEM IT   │ Without LB, horizontal scaling is     │
│ SOLVES       │ useless—traffic goes to one server    │
├──────────────┼────────────────────────────────────────┤
│ KEY INSIGHT  │ LB itself can become bottleneck if    │
│              │ not designed for throughput you       │
│              │ need; watch its metrics closely       │
├──────────────┼────────────────────────────────────────┤
│ USE WHEN     │ Scaling to multiple servers;          │
│              │ need high availability; want to       │
│              │ add/remove servers dynamically        │
├──────────────┼────────────────────────────────────────┤
│ AVOID WHEN   │ Workload fits on single machine;      │
│              │ cost-sensitive and can tolerate       │
│              │ downtime; static server pool (never   │
│              │ changes)                              │
├──────────────┼────────────────────────────────────────┤
│ TRADE-OFF    │ [Fair traffic distribution] vs        │
│              │ [added infrastructure, potential      │
│              │ single point of failure]              │
├──────────────┼────────────────────────────────────────┤
│ ONE-LINER    │ "The traffic cop that ensures all     │
│              │ servers get their fair share."        │
├──────────────┼────────────────────────────────────────┤
│ NEXT EXPLORE │ Round Robin → Least Connections →     │
│              │ Consistent Hashing                    │
└──────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A load balancer distributes requests round-robin across 10 servers. One server becomes 10x slower (due to a memory leak). The load balancer still sends it 10% of traffic. What algorithm should you use instead, and why does it solve the problem?

**Q2.** Your load balancer is the single point of failure—if it crashes, all traffic stops. You want HA. Design a redundant load balancing setup. What happens if Primary LB crashes while a request is mid-flight?
