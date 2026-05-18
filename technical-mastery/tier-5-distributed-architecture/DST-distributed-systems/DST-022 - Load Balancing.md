---
id: DST-022
title: Load Balancing
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★☆☆
depends_on: DST-008, DST-011, DST-021
used_by: DST-022, DST-062
related: DST-011, DST-021, DST-023, DST-062
tags:
  - distributed
  - networking
  - scalability
  - foundational
status: complete
version: 4
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Mastery"
nav_order: 22
permalink: /technical-mastery/distributed-systems/load-balancing/
---

⚡ TL;DR - Load balancing distributes incoming requests
across multiple server instances to prevent any single
instance from being overwhelmed; it is the primary mechanism
for horizontal scaling and combines with health checks
to route around failed instances automatically.

---

### 📋 Entry Metadata

| #022 | Category: Distributed Systems | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Node, Fault Tolerance, Service Discovery | |
| **Used by:** | Service Mesh, API Gateway | |
| **Related:** | Fault Tolerance, Service Discovery, Latency vs Throughput | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A web application serves all requests from a single server.
A viral marketing campaign sends 10x normal traffic. The
server CPU hits 100%. Response times climb from 50ms to
10 seconds. Requests time out. The site is effectively
unavailable. Adding a second server doesn't help - users
are still going to the original server. Without load
balancing, horizontal scaling (adding servers) does not
distribute the load - it just adds idle capacity.

**THE SCALING MATH:**
A single server handles 1,000 requests/second. Load
doubles to 2,000 req/s. Adding a second server without
load balancing: server 1 still receives 2,000 req/s
(saturated), server 2 receives 0 req/s (idle). With a
load balancer: each server receives 1,000 req/s (balanced).
The load balancer is the mechanism that makes horizontal
scaling effective.

---

### 📘 Textbook Definition

A **load balancer** is a component that distributes incoming
requests across a pool of backend servers (the "upstream"
or "pool") to maximize throughput, minimize response time,
and ensure no single server is overwhelmed. Load balancers
operate at different network layers: **Layer 4 (L4)**
operates on TCP/UDP and distributes based on IP and port;
**Layer 7 (L7)** operates on HTTP and can distribute
based on URL path, headers, or request content. Load
balancers implement **routing algorithms** (round-robin,
weighted round-robin, least connections, IP hash, random)
and combine with **health checks** to automatically remove
unhealthy backends from the pool. They are a central
component in every production architecture, deployed as
hardware appliances, software reverse proxies (nginx,
HAProxy), cloud services (AWS ALB, Google Cloud Load
Balancing), or service meshes (Envoy, Istio).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A load balancer is a traffic director that spreads requests
across multiple servers so no one server gets overwhelmed.

**One analogy:**
> A restaurant host who seats customers. Without a host,
> customers choose their own table and everyone crowds
> the same section. With a host, customers are spread
> evenly across all sections. If a waiter calls in sick,
> the host stops seating customers in their section.
> Load balancing is the host: distribute traffic evenly,
> route around unavailable servers.

**One insight:**
Load balancing has two purposes that are often conflated:
(1) performance - distributing load for maximum throughput,
and (2) reliability - detecting and routing around failed
backends. Both are equally important. A load balancer that
balances perfectly but routes to failed servers is useless.
A load balancer that avoids failed servers but concentrates
load on one server defeats horizontal scaling.

---

### 🔩 First Principles Explanation

**LOAD BALANCING ALGORITHMS:**

**Round-Robin:**
Each backend receives requests in rotating order: 1, 2, 3,
1, 2, 3. Assumes all backends are equally capable.
Problem: if backends have different processing times,
"hot" backends accumulate more in-flight requests.

**Weighted Round-Robin:**
Each backend has a weight proportional to its capacity:
backend A (weight 3) receives 3x more requests than
backend B (weight 1). Used when backends have different
hardware capacities or when canary deployments route
a small percentage to a new version.

**Least Connections:**
Each new request goes to the backend with fewest active
connections. Better for workloads with variable request
duration (some requests take 1ms, others take 1 second).
Round-robin would overload slow-request backends.

**IP Hash (Sticky Sessions):**
The client's IP is hashed to determine the backend.
The same client always routes to the same backend.
Used for stateful applications where session state
lives on the server (not in a shared session store).
Problem: defeats load balancing if most traffic comes
from one IP.

**Random with Two Choices (Power of Two):**
Pick two random backends; send to the one with fewer
connections. Near-optimal distribution without tracking
all backends' states. Used by Nginx, Facebook's Proxygen.

**L7 ROUTING (Content-Based):**
```
GET /api/users     → user-service backends
GET /api/payments  → payment-service backends
GET /assets/*.js   → CDN / static asset servers

POST /api/v1/*     → v1 backends (stable)
POST /api/v2/*     → v2 backends (new, 10% traffic)
```

---

### 🧠 Mental Model / Analogy

> Load balancing is water flowing through pipes. A single
> pipe (single server) has limited capacity. Multiple
> parallel pipes (multiple servers) handle more flow.
> The load balancer is the junction that splits the flow
> across all pipes evenly. If one pipe narrows or clogs
> (server under load or failed), the junction reduces
> or stops flow to that pipe and increases flow to others.

**Mapping:**
- "Water flow" - request rate
- "Pipe capacity" - server throughput
- "Multiple parallel pipes" - server pool
- "Junction" - load balancer
- "Clogged pipe" - unhealthy or overloaded server

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
A load balancer is a router that sends each incoming
request to one of several servers. By spreading requests
evenly, no single server is overwhelmed. When a server
fails, the load balancer stops sending requests to it.

**Level 2 - How to use it (junior developer):**
In AWS: use an Application Load Balancer (ALB) in front
of EC2 instances or ECS tasks. Configure a target group,
add your instances, configure health checks (HTTP 200 on
/health every 30 seconds). ALB routes traffic to healthy
instances using round-robin.

**Level 3 - How it works (mid-level engineer):**
An L7 load balancer terminates TCP connections from clients.
It reads the HTTP request (URL, headers, body). It selects
a backend using the configured algorithm (round-robin,
least connections). It establishes a new TCP connection
to the backend and forwards the HTTP request. When the
backend responds, the load balancer forwards the response
to the client. Connection state is maintained between
the load balancer and each backend.

**Level 4 - Why it was designed this way (senior/staff):**
L4 vs L7 is a capability vs performance trade-off. L4
load balancers pass through TCP/UDP without reading content
- extremely fast (hardware can wire-speed L4 routing),
but no content-based routing. L7 load balancers read
HTTP (more CPU), but enable URL routing, header inspection,
SSL termination, and request modification. Cloud-native
architectures prefer L7 because it integrates with
authentication (JWT validation), observability (request
tracing), and traffic management (retries, timeouts,
circuit breakers).

**Level 5 - Mastery (distinguished engineer):**
Modern service meshes (Envoy, Istio, Linkerd) implement
load balancing at the sidecar proxy level. Every pod has
an Envoy proxy that intercepts all outbound traffic and
applies L7 load balancing, circuit breaking, and retry
logic without requiring a central load balancer. This
eliminates the load balancer as a single point of failure
and reduces latency (no extra network hop). The trade-off:
CPU and memory overhead per pod (Envoy sidecars), increased
system complexity, and harder debugging when traffic is
intercepted and modified by every proxy.

---

### ⚙️ Mechanism - Load Balancer Health Check and Failover

```
┌────────────────────────────────────────────────────────┐
│  STEADY STATE: 3 backends, all healthy                 │
│  Backend A: GET /health → 200 ✓                        │
│  Backend B: GET /health → 200 ✓                        │
│  Backend C: GET /health → 200 ✓                        │
│  Traffic: A: 33%, B: 33%, C: 33%                      │
│                                                        │
│  t=0: Backend B crashes                                │
│  t=5s: Health check to B times out (1st failure)      │
│  t=10s: Health check to B times out (2nd failure)     │
│  t=10s: Load balancer marks B as UNHEALTHY             │
│  t=10s: B removed from rotation                       │
│  Traffic: A: 50%, C: 50%                              │
│                                                        │
│  t=120s: Backend B restarts, health check passes       │
│  t=130s: After 2 consecutive passing checks:           │
│           B marked as HEALTHY                         │
│  Traffic: A: 33%, B: 33%, C: 33%                      │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Nginx Load Balancer Configuration (Wrong vs Right)**

```nginx
# BAD: Round-robin with no health checks
upstream backend {
    server 10.0.1.1:8080;
    server 10.0.1.2:8080;
    server 10.0.1.3:8080;
    # No health checks!
    # If any server crashes, requests still route there
    # Users get errors until the crash is detected passively
    # (by failed requests)
}
```

```nginx
# GOOD: Least-connections with active health checks
upstream backend {
    least_conn;  # route to server with fewest connections
    
    server 10.0.1.1:8080 max_fails=3 fail_timeout=30s;
    server 10.0.1.2:8080 max_fails=3 fail_timeout=30s;
    server 10.0.1.3:8080 max_fails=3 fail_timeout=30s;
    # After 3 failures, server is excluded for 30 seconds
    
    keepalive 32;  # connection pool to backends
}

server {
    # Active health checks (Nginx Plus or open-source with
    # nginx_upstream_check_module):
    location /health {
        proxy_pass http://backend;
        health_check interval=5 fails=2 passes=1;
    }
}
```

**Python Client with Client-Side Load Balancing**

```python
import random
from typing import Optional

class ClientSideLoadBalancer:
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.backends: list[str] = []
        self.failures: dict[str, int] = {}
        self.MAX_FAILURES = 3

    def refresh_backends(self) -> None:
        """Query service registry for current backends"""
        self.backends = service_registry.lookup(
            self.service_name,
            healthy_only=True
        )

    def get_backend(self) -> Optional[str]:
        """Power-of-two-choices: pick better of 2 random"""
        healthy = [
            b for b in self.backends
            if self.failures.get(b, 0) < self.MAX_FAILURES
        ]
        if not healthy:
            self.refresh_backends()  # registry may have updates
            return None
        if len(healthy) == 1:
            return healthy[0]
        # Power of two: pick 2 random, return the one with
        # fewer cached failures
        a, b = random.sample(healthy, 2)
        return a if self.failures.get(a, 0) <=\
            self.failures.get(b, 0) else b

    def record_failure(self, backend: str) -> None:
        self.failures[backend] = self.failures.get(backend, 0) + 1

    def record_success(self, backend: str) -> None:
        self.failures[backend] = 0
```

---

### ⚖️ Comparison Table

| Algorithm | Best For | Avoid When |
|---|---|---|
| **Round-Robin** | Equal-capacity backends, equal request duration | Variable request duration |
| Weighted Round-Robin | Mixed-capacity backends, canary deploys | Dynamic load variation |
| Least Connections | Variable request duration, long-running requests | Very high request rate (connection count overhead) |
| IP Hash | Stateful sessions (session affinity) | Clients from few IPs (unbalanced) |
| Random (Power of Two) | Very high throughput, simple backends | Need strict ordering guarantees |

| Layer | Implementation | Use When |
|---|---|---|
| **L4** | AWS NLB, HAProxy TCP mode | Low latency, non-HTTP protocols |
| **L7** | AWS ALB, nginx, Envoy | HTTP routing, header inspection, tracing |
| Service Mesh | Envoy sidecar, Linkerd | Per-pod routing, mTLS, observability |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Load balancing only matters at high traffic" | Load balancing also provides fault tolerance: a single-instance deployment has no failover. Even at low traffic, having 2 instances behind a load balancer provides resilience. |
| "Round-robin always distributes evenly" | Round-robin distributes requests evenly but not load evenly if requests have variable duration. Use least-connections for workloads with variable request processing time. |
| "The load balancer is always the single point of failure" | Modern cloud load balancers are HA by design (ALB, NLB). Self-managed load balancers (nginx) require an HA pair with shared virtual IP (keepalived) to eliminate the SPOF. |

---

### 🚨 Failure Modes & Diagnosis

**Hot Spot - One Backend Receiving Disproportionate Traffic**

**Symptom:** One backend pod has CPU at 90% while others
are at 20%. Users on the overloaded pod experience high
latency. Other pods are underutilized.

**Root Cause:** Round-robin is configured but requests
have highly variable duration. One request type takes
2 seconds; others take 10ms. The 2-second requests
accumulate on one pod, creating a hot spot.

**Diagnosis:**
```bash
# Check per-backend request count in nginx:
cat /var/log/nginx/access.log |
  awk '{print $NF}' |  # extract upstream server
  sort | uniq -c | sort -rn

# If counts are equal but one pod shows high CPU:
# → Variable request duration, not distribution issue
# → Switch from round-robin to least_conn in nginx config
```

**Fix:** Switch to least-connections algorithm. This
routes new requests to the backend with fewest in-flight
connections, naturally distributing both count and load.

---

### 🔗 Related Keywords

**Prerequisites:**
- `Node`, `Fault Tolerance`, `Service Discovery`

**Builds On This:**
- `Service Mesh` - Distributed load balancing at sidecar level
- `Latency vs Throughput` - Metrics used to evaluate LB performance

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Distribute requests across backend pool  │
├──────────────┼──────────────────────────────────────────┤
│ L4 vs L7     │ L4: TCP/UDP, fast, no content inspection │
│              │ L7: HTTP, routing by URL/headers, slower │
├──────────────┼──────────────────────────────────────────┤
│ ALGORITHMS   │ Round-robin: even counts                 │
│              │ Least-conn: even load (variable durations│
│              │ IP hash: session affinity                │
├──────────────┼──────────────────────────────────────────┤
│ HEALTH CHECK │ Mandatory. Remove unhealthy backends     │
│              │ before users see errors.                 │
├──────────────┼──────────────────────────────────────────┤
│ ANTI-PATTERN │ Single load balancer without HA          │
│              │ (SPOF - defeats the purpose)             │
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "Even traffic distribution + automatic   │
│              │  failure routing = horizontal scaling."  │
└─────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

The routing algorithm of a load balancer is the same class
of problem as any work distribution algorithm in computing:
thread pools, connection pools, and task queues all face
the same challenge - how to distribute work evenly when
tasks have variable duration. Least-connections (and its
equivalent in thread pools: work-stealing) is the universal
solution for variable-duration work distribution.

---

### 💡 The Surprising Truth

NGINX's default round-robin algorithm was so simple that
Netflix replaced it with their own weighted load balancing
called "Power of Two Choices with Random" for their
internal load balancer (Ribbon). The insight: even a simple
improvement to round-robin (pick 2 random backends, choose
the less loaded one) reduces the variance in load
distribution dramatically - from O(n) worst case to O(log
log n) - a mathematical result from Mitzenmacher (2001).
This is why all modern load balancers use some variant of
"power of two choices" rather than pure round-robin.

---

### ✅ Mastery Checklist

1. [CONFIGURE] Set up nginx with a pool of 3 backends
   using least-connections, passive health checks, and
   keepalive connections.
2. [SELECT] Given a workload (mix of 10ms and 2-second
   requests), choose and justify the appropriate load
   balancing algorithm.
3. [DEBUG] Diagnose a hot spot: one backend at 90% CPU,
   others at 20%, all receiving equal request counts.
4. [DESIGN] Design a load balancing architecture for a
   stateful websocket application where each user's
   messages must go to the same backend.
5. [EXPLAIN] Why a load balancer without health checks
   can cause more failures than having no load balancer.
