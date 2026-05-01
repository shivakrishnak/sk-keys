---
layout: default
title: "Least Connections"
parent: "System Design"
nav_order: 685
permalink: /system-design/least-connections/
number: "685"
category: System Design
difficulty: ★★☆
depends_on: "Load Balancing, Round Robin"
used_by: "Auto Scaling"
tags: #intermediate, #distributed, #networking, #algorithm, #architecture
---

# 685 — Least Connections

`#intermediate` `#distributed` `#networking` `#algorithm` `#architecture`

⚡ TL;DR — **Least Connections** routes each new request to the backend server with the fewest currently active connections, dynamically balancing load when request durations vary.

| #685 | Category: System Design | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Load Balancing, Round Robin | |
| **Used by:** | Auto Scaling | |

---

### 📘 Textbook Definition

**Least Connections** (also called Least Active Connections) is a dynamic load balancing algorithm where the load balancer routes each incoming request to the backend server that currently has the fewest active (open, in-progress) connections. Unlike Round Robin which is static (ignoring server state), Least Connections is adaptive: it observes the real-time connection count of each backend and makes routing decisions based on actual load rather than turn order. **Weighted Least Connections** extends the algorithm: new requests go to the server with the lowest ratio of active connections to weight (`active_connections / weight`), accommodating servers with different capacities. Least Connections is particularly effective when request duration varies significantly (mix of fast API calls and slow long-running operations), because it prevents slow backends from accumulating a backlog while fast backends sit idle.

---

### 🟢 Simple Definition (Easy)

Least Connections sends each new request to whichever server is currently the least busy (fewest ongoing requests). Instead of a fixed turn order, the load balancer always picks the server with the shortest queue right now. Dynamic and fair for workloads where some requests take much longer than others.

---

### 🔵 Simple Definition (Elaborated)

Three servers. Server A: processing 2 requests. Server B: processing 8 requests (has some slow ones). Server C: processing 1 request. New request arrives: round-robin would pick Server A (next in rotation), but Least Connections picks Server C (only 1 active). Server B has accumulated a backlog of slow requests but won't receive new traffic until its count drops. Naturally adapts to server speed differences: faster servers finish requests sooner → lower connection count → more new requests routed to them.

---

### 🔩 First Principles Explanation

**Why Round Robin fails for variable-duration workloads:**

```
WORKLOAD: 70% fast API calls (10ms), 30% slow report calls (10,000ms)
SERVERS: 3 backends, each can handle 100 active connections

ROUND ROBIN (timestamp: T=0 to T=60s):
  T=0: 1000 requests arrive, round-robin distributes ~333 to each server.
       333 × 30% = ~100 slow requests per server (each taking 10 seconds)
       All 3 servers: 100 slow active connections from T=0 to T=10
       Fast requests queue: have to wait for slow connections to free up
       
  T=5: User waits for fast API call — it's queued behind slow reports
  P99: 5+ seconds for a 10ms API call (blocked by slow connections)

LEAST CONNECTIONS (same workload):
  T=0: Fast requests: complete in 10ms → connection released immediately
       Connection count: fast-request servers stay at low count
       Slow requests: 10+ seconds → accumulate on whichever server got them
  
  T=1: Server B has 30 slow connections. Server A/C: 2 active each.
       New request → Least Connections picks Server A or C (count=2)
       Not Server B (count=30)
  
  Result: slow requests are isolated to servers that received them.
          Fast requests naturally distributed to servers with low count.
          Fast request users: still get sub-50ms responses.
  
  NOTE: Least Connections doesn't separate the workloads —
        it still mixes fast and slow on the same pool.
  BETTER: separate pools (fast pool + slow pool) with path-based routing.
```

**Algorithm variants:**

```
LEAST CONNECTIONS:
  Route to: argmin(active_connections[i] for all backends i)
  State: load balancer tracks active_connections[] array
  Update: connection opened → count++, connection closed → count--
  Thread-safe: requires atomic increment/decrement per backend
  
WEIGHTED LEAST CONNECTIONS:
  Route to: argmin(active_connections[i] / weight[i])
  Example:
    Server A: 10 connections, weight=4 → score = 10/4 = 2.5
    Server B:  5 connections, weight=1 → score =  5/1 = 5.0
    Server C:  8 connections, weight=2 → score =  8/2 = 4.0
    → Route to Server A (lowest score 2.5), despite most connections
    → Correct: Server A is a 4x larger instance, so 10 connections = low relative load

LEAST RESPONSE TIME (HAProxy: leastconn + http-check):
  Route to: server with lowest weighted combination of:
    - Active connections (current load)
    - Average response time (historical performance)
  More sophisticated: accounts for both current backlog and server speed
  
  nginx: least_time header;
    # Routes to server with smallest header_time × num_conns value
    # header_time: time until first byte of response
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Least Connections (Round Robin only):
- Variable-duration requests accumulate on some servers, leaving others idle
- Fast requests queued behind slow ones → unpredictable latency
- Degraded backends receive same traffic as healthy ones → cascading failure

WITH Least Connections:
→ Naturally load-balances based on actual server busy-ness
→ Faster servers receive proportionally more new requests (they free up faster)
→ Degraded/slow server: accumulates connections → naturally receives less new traffic
→ Better P99 latency for mixed workload types

---

### 🧠 Mental Model / Analogy

> A supermarket with multiple checkout lanes. A smart queue manager directs each new customer to the shortest lane (fewest people in queue). If Lane 3 has 8 people with full carts and Lane 1 has 2 people with baskets, new customers go to Lane 1 — even if Lane 3 is "next in rotation." The queue manager continuously monitors and routes to the least-busy lane.

"Checkout lanes" = backend servers
"People in queue" = active connections
"Queue manager" = load balancer with Least Connections algorithm
"Customers with carts vs baskets" = slow vs fast requests

---

### ⚙️ How It Works (Mechanism)

**HAProxy Least Connections configuration:**

```
# haproxy.cfg: least connections with health checks and weights
backend order_service_pool
    balance leastconn                    # Least Connections algorithm
    option http-server-close             # close connections after each request
    option forwardfor                    # pass client IP in X-Forwarded-For
    option httpchk GET /actuator/health  # active health checks
    http-check expect status 200
    
    # Weighted: server1 handles 3x, server2 handles 1x relative load
    server order-svc-1 10.0.1.1:8080 weight 3 check inter 10s fall 3 rise 2
    server order-svc-2 10.0.1.2:8080 weight 1 check inter 10s fall 3 rise 2
    server order-svc-3 10.0.1.3:8080 weight 2 check inter 10s fall 3 rise 2
    
    # Observing active connections (HAProxy stats endpoint):
    # haproxy_backend_active_servers{backend="order_service_pool"}
    # haproxy_backend_current_sessions{backend="order_service_pool"}
```

---

### 🔄 How It Connects (Mini-Map)

```
Round Robin
(static, by connection count)
        │
        ▼ (upgrade for variable request duration)
Least Connections  ◄──── (you are here)
(dynamic, by current load)
        │
        ├── Weighted Least Connections (capacity-aware variant)
        ├── Least Response Time (also considers latency history)
        └── Auto Scaling (uses connection depth as scale-up signal)
```

---

### 💻 Code Example

**nginx upstream with least_conn:**

```nginx
upstream api_backends {
    least_conn;   # Enable Least Connections (default: round-robin)
    
    server api-1.internal:8080;
    server api-2.internal:8080;
    server api-3.internal:8080;
    
    keepalive 64;  # keep 64 idle connections per worker per backend
                   # important: Least Connections + keepalive: the LB
                   # must count long-lived keepalive connections too
}

server {
    listen 80;
    location / {
        proxy_pass http://api_backends;
        proxy_http_version 1.1;         # required for keepalive
        proxy_set_header Connection ""; # clear Connection header
        proxy_read_timeout 60s;
    }
}

# Monitoring: check connection distribution per backend:
# curl http://nginx_host/nginx_status
# Active connections: 847
# server accepts handled requests
#  3145728 3145728 4194304
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Least Connections is always better than Round Robin | For homogeneous requests (similar duration, equal server capacity), Round Robin and Least Connections perform nearly identically. Least Connections adds state tracking overhead. For truly uniform workloads, Round Robin's simplicity wins |
| Least Connections counts total connections, not active ones | Least Connections counts ACTIVE (in-progress) connections, not total established TCP connections including idle keepalives. Some implementations count all connections including keepalive — this can skew the algorithm for HTTP/1.1 with persistent connections |
| Least Connections prevents hotspots | If one server becomes slow (network degradation, CPU throttling), it accumulates connections and stops receiving new ones — partially protecting it. But the remaining servers absorb its share and may themselves become overloaded. Least Connections mitigates but doesn't eliminate hotspots |
| Weighted Least Connections needs manual weight tuning | Weights should match actual server capacity. Start with benchmark ratios (throughput test per instance type). In homogeneous fleets (all same instance type), all weights=1 is correct |

---

### 🔥 Pitfalls in Production

**Least Connections with long-lived WebSocket connections:**

```
PROBLEM:
  WebSocket connections: stay open for 30+ minutes.
  HTTP REST calls: 50-200ms.
  
  Server A gets 100 WebSocket connections (long-lived, low CPU).
  Server A: active_connections = 100 → Least Connections routes AWAY from A.
  Server B/C: get all new REST traffic despite Server A being mostly idle.
  Server B: overloaded with REST requests (actual CPU at 90%).
  Server A: idle (100 WebSocket connections open but sleeping).
  
  Least Connections counts connections, not CPU load.
  WebSocket connections inflate count without contributing load.

FIX 1: Separate pools — WebSocket and REST on different backend groups.
  upstream websocket_pool { least_conn; server ws-1:8080; server ws-2:8080; }
  upstream rest_pool { least_conn; server rest-1:8080; server rest-2:8080; }
  
  # Path-based routing:
  location /ws/ { proxy_pass http://websocket_pool; }
  location /api/ { proxy_pass http://rest_pool; }

FIX 2: Use least_time (nginx plus) or custom metric-based routing.
  Prometheus: scrape CPU/memory from backends.
  Custom LB logic: route based on CPU utilisation, not connection count.
  KEDA: scale based on CPU metrics, not just connection counts.
```

---

### 🔗 Related Keywords

- `Load Balancing` — the parent concept
- `Round Robin` — the simpler algorithm Least Connections improves upon
- `Consistent Hashing (Load Balancing)` — alternative for cache affinity use cases
- `Auto Scaling` — connection depth metric triggers scale-out decisions
- `Session Affinity` — sometimes conflicts with Least Connections (sticky sessions override dynamic routing)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Route to server with fewest active        │
│              │ connections right now (dynamic, adaptive) │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Mixed workloads (fast + slow requests);   │
│              │ heterogeneous backend speeds              │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ WebSockets / long-lived connections skew  │
│              │ count; homogeneous workloads (use RR)     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Always join the shortest checkout queue, │
│              │  not the one whose turn it is."           │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Consistent Hashing → Sticky Sessions      │
│              │ → Auto Scaling                            │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You have 4 backend servers behind a Least Connections load balancer. Server 4 starts experiencing high GC pauses (Java G1GC full GC, 2-3 second stop-the-world pauses every 30 seconds). During each GC pause, Server 4's connections accumulate (requests queued, not completing). Describe exactly how Least Connections behaves during a GC pause cycle: what happens to Server 4's connection count, how does the LB respond, and what happens immediately after the GC pause ends (connection count drops suddenly)?

**Q2.** You are designing a load balancing strategy for a service that has three tiers of request priority: P1 (SLA: 50ms, 10% of traffic), P2 (SLA: 500ms, 60% of traffic), P3 (SLA: 5s, 30% of traffic). The requests arrive on the same HTTP endpoint distinguished by a header `X-Priority`. Evaluate whether Least Connections alone achieves the SLA requirements. Design an architecture using backend pools, load balancing algorithm, and optionally queue-based processing to guarantee P1 SLA regardless of P3 backlog.
