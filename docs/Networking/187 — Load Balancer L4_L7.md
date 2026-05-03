---
layout: default
title: "Load Balancer L4/L7"
parent: "Networking"
nav_order: 187
permalink: /networking/load-balancer-l4-l7/
number: "0187"
category: Networking
difficulty: ★★☆
depends_on: TCP, HTTP & APIs, IP Addressing, Socket, Port & Ephemeral Port
used_by: Microservices, Cloud — AWS, Distributed Systems, System Design
related: Proxy vs Reverse Proxy, CDN, Anycast, Firewall, Service Discovery
tags:
  - networking
  - load-balancer
  - l4
  - l7
  - nginx
  - haproxy
  - aws-alb
  - aws-nlb
---

# 187 — Load Balancer L4/L7

⚡ TL;DR — An **L4 (Layer 4) load balancer** distributes TCP/UDP connections by IP and port without inspecting content — fast, low-latency, handles millions of connections. An **L7 (Layer 7) load balancer** inspects HTTP content (URL, headers, cookies) and routes intelligently — enables path-based routing, session stickiness, A/B testing, and health checks at the application level. AWS ALB = L7; AWS NLB = L4.

---

### 🔥 The Problem This Solves

**THE SCALE PROBLEM:**
A single web server handles 10,000 requests/second. Traffic grows to 100,000 req/s. One server can't handle it. You add 9 more servers — but how does traffic reach all 10? If DNS resolves to one IP, all requests go to one server. A load balancer solves this: one IP, N servers behind it, traffic distributed.

**THE INTELLIGENCE PROBLEM:**
Simple TCP load balancing routes any connection to any server. But HTTP applications need more: route `/api` requests to API servers and `/static` to a CDN origin; route requests with a `session_id` cookie to the same server (sticky sessions); health check by actually making HTTP requests (not just TCP ping); route traffic to different server groups in blue/green deployment. L7 understands HTTP and enables all of this.

---

### 📘 Textbook Definition

**L4 Load Balancer (Transport Layer):** Routes traffic based on network-layer information (IP addresses, TCP/UDP ports). Does NOT inspect HTTP content. Creates a TCP proxy: client connects to LB, LB connects to backend, LB forwards raw TCP bytes. Advantages: very fast (no HTTP parsing), works for any TCP/UDP protocol, handles millions of connections. AWS NLB, HAProxy (TCP mode), LVS (Linux Virtual Server).

**L7 Load Balancer (Application Layer):** Terminates the client's TCP+TLS connection, parses HTTP, makes routing decisions based on URL path, headers, cookies, or request body. Forwards a new HTTP request to the selected backend. Advantages: rich routing, health checks at HTTP level, SSL termination, request manipulation. AWS ALB, Nginx, HAProxy (HTTP mode), Envoy, Traefik.

**Load balancing algorithms:** Round-robin (sequential), Least connections (backend with fewest active connections), IP hash (consistent — same client IP → same backend), Weighted (proportion-based), Random with two choices (power of two choices — pick min of 2 random backends).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
L4 balances TCP connections blindly (fast, dumb). L7 reads HTTP content and routes intelligently (smart, slightly slower). Use L4 for raw throughput; use L7 for application-aware routing.

**One analogy:**

> L4 is like a roundabout that distributes cars to parallel roads without looking inside the car. L7 is like a traffic controller who checks your destination and vehicle type: "Trucks go to lane 1 (API servers), passenger cars to lane 2 (web servers), VIP badges to lane 3 (premium tier)."

---

### 🔩 First Principles Explanation

**L4 LOAD BALANCING:**

```
Client TCP connection: src=client:54321 dst=LB:443

L4 LB options:
  NAT mode: LB rewrites dst IP to backend IP
    LB: src=client:54321 dst=backend-2:443
    Backend sees client's real IP as source

  Proxy mode: LB terminates TCP, opens new connection to backend
    Backend connection: src=LB:62345 dst=backend-2:443
    Backend sees LB IP as source (client IP lost unless PROXY protocol)

DSR (Direct Server Return): LB changes dst MAC only, backend responds
  directly to client (bypasses LB on response — very high throughput)
```

**L7 LOAD BALANCING:**

```
Client HTTPS connection → L7 LB
  TLS termination (LB holds certificate)
  HTTP/2 connection terminated
  Request parsed:
    Method: GET
    Path: /api/v2/users
    Headers: Host, Cookie, X-Tenant-ID

  Routing decision:
    /api/* → api-server pool
    /admin/* → require auth header; → admin pool
    Cookie: session_id=abc → backend server-3 (sticky session)
    Header: X-Tenant-ID=enterprise → enterprise-tier pool

  New backend request (HTTP/1.1 or HTTP/2):
    src=LB dst=api-server-2:8080
    Adds headers: X-Forwarded-For, X-Request-ID

L7 Health Checks (vs L4):
  L4: TCP connect to :8080 → success (port open, app may be broken)
  L7: GET /health → expect 200 OK with {"status":"ok"}
      → actually validates the application is functioning
```

**AWS ALB vs NLB:**

```
ALB (Application Load Balancer) = L7
  - HTTP/HTTPS/gRPC aware
  - Path-based rules (/api → target-group-1)
  - Host-based routing (api.example.com → tg-1, app.example.com → tg-2)
  - WAF integration
  - Sticky sessions (cookie-based)
  - Lambda, ECS, EC2, IP targets
  - Latency: ~1-5ms additional per request

NLB (Network Load Balancer) = L4
  - TCP/UDP/TLS
  - Preserves client source IP (unlike ALB)
  - Millions of connections/second
  - Static IP (Elastic IP) — useful for whitelisting
  - Latency: <1ms additional
  - Good for: gaming, IoT, custom TCP protocols, source IP preservation
```

---

### 🧪 Thought Experiment

**MICROSERVICES ROUTING DESIGN:**

```
Request: GET api.example.com/v2/orders/123
              api.example.com/v1/users/456
              api.example.com/admin/dashboard
              api.example.com/websocket/chat

ALB Rules (in priority order):
  1. Path /admin/*  AND  Header: X-Admin-Token → admin-target-group
  2. Path /websocket/* → websocket-target-group
     (different idle timeout: 3600s vs default 60s)
  3. Path /v1/* → api-v1-target-group (old version)
  4. Path /v2/* → api-v2-target-group (new version)
  5. Default → api-v2-target-group

Blue/Green Deployment:
  Shift traffic: start 0% → blue, 100% → green
  ALB weighted routing:
    api-v2-blue: weight=100, api-v2-green: weight=0
  Canary:
    api-v2-blue: weight=90, api-v2-green: weight=10
  Full cutover:
    api-v2-blue: weight=0, api-v2-green: weight=100
```

---

### 🧠 Mental Model / Analogy

> L4 = postal sorting by zip code (looks at envelope only — no need to open the letter). Fast, handles any mail. L7 = a specialist mail room that opens letters, reads the content, and routes to the right department: "This letter mentions 'invoice' → Finance department. This letter is marked 'urgent' → Executive assistant. This letter has a VIP stamp → Premium handling."

---

### 📶 Gradual Depth — Four Levels

**Level 1:** A load balancer distributes incoming requests across multiple servers so no single server gets overwhelmed. L4 routes by IP/port; L7 routes by HTTP content.

**Level 2:** Configure an AWS ALB: create a target group with EC2 instances, set up a listener on port 443, add rules (path-based, host-based), configure health checks (HTTP GET /health, expect 200). ALB terminates HTTPS for you.

**Level 3:** L7 connection flow: client → TLS (LB cert) → HTTP/2 multiplexed; LB → HTTP/1.1 or HTTP/2 to backend (separate connection pool). LB maintains connection pools to backends — reuses persistent connections. This is connection multiplexing: many client connections → fewer LB-to-backend connections (backend gets less connection overhead). Sticky sessions: ALB inserts `AWSALB` cookie; subsequent requests with that cookie routed to same target.

**Level 4:** The fundamental tension in load balancing: uniform distribution vs session affinity. Round-robin gives even distribution but breaks stateful applications. IP hash gives consistency but causes hot spots (office NAT: 1000 users behind one IP → all go to same backend). Consistent hashing with virtual nodes (used by Nginx `hash` directive) distributes load while maintaining per-key consistency, used in distributed caches (where you need the same cache node for the same key). For stateless services: least-connections is generally optimal (routes new connections to the backend with the most capacity).

---

### ⚙️ How It Works (Mechanism)

```bash
# HAProxy config (L7 HTTP mode)
frontend http_front
    bind *:80
    default_backend http_back

backend http_back
    balance roundrobin
    option httpchk GET /health
    http-check expect status 200
    server web1 10.0.0.1:8080 check inter 5s
    server web2 10.0.0.2:8080 check inter 5s
    server web3 10.0.0.3:8080 check inter 5s

# Check HAProxy stats
echo "show stat" | socat stdio /var/run/haproxy/admin.sock | \
  cut -d',' -f1,2,5,6,18,19 | head -20

# AWS ALB: check target group health
aws elbv2 describe-target-health \
  --target-group-arn arn:aws:elasticloadbalancing:...
# State: healthy | unhealthy | draining | initial

# Check active connections on LB
netstat -ant | grep :443 | awk '{print $6}' | sort | uniq -c
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
L7 Load Balancer — Request Flow:

Client → [TLS handshake] → ALB :443
ALB:
  Parse HTTP: GET /api/orders, Host: api.example.com
  Match rule: /api/* → api-target-group
  Pick backend: api-server-3 (least connections)
  Health: api-server-3 is healthy (last check 3s ago)
  Forward: HTTP/1.1 GET to 10.0.1.3:8080
  Headers: X-Forwarded-For, X-Forwarded-Proto: https
Backend → response 200
ALB → forward response to client (same TLS connection)

Connection pooling:
  1000 client connections → 50 persistent connections to backends
  (HTTP/2 multiplexing / keepalive reuse)
```

---

### 💻 Code Example

```python
import random
import time
from dataclasses import dataclass, field
from typing import List

@dataclass
class Backend:
    host: str
    port: int
    active_connections: int = 0
    healthy: bool = True
    weight: int = 1

class LeastConnectionsLB:
    """Simple L4/L7 load balancer using least-connections algorithm."""

    def __init__(self, backends: List[Backend]):
        self.backends = backends

    def pick_backend(self) -> Backend | None:
        """Pick backend with fewest active connections (healthy only)."""
        healthy = [b for b in self.backends if b.healthy]
        if not healthy:
            return None
        return min(healthy, key=lambda b: b.active_connections)

    def handle_request(self, path: str) -> str:
        """Route request and simulate response."""
        backend = self.pick_backend()
        if not backend:
            return "503 Service Unavailable"

        backend.active_connections += 1
        try:
            # Simulate forwarding request
            time.sleep(0.001)  # 1ms processing
            return f"200 OK from {backend.host}:{backend.port}"
        finally:
            backend.active_connections -= 1

# Usage
backends = [
    Backend("api-1", 8080),
    Backend("api-2", 8080),
    Backend("api-3", 8080),
]
lb = LeastConnectionsLB(backends)

# Simulate 10 concurrent requests
for i in range(10):
    result = lb.handle_request(f"/api/request-{i}")
    print(result)
```

---

### ⚖️ Comparison Table

| Feature                | L4 (NLB/HAProxy TCP)      | L7 (ALB/Nginx)                  |
| ---------------------- | ------------------------- | ------------------------------- |
| Protocol awareness     | IP/TCP/UDP only           | HTTP/HTTPS/gRPC                 |
| Routing logic          | IP, port                  | URL, headers, cookies           |
| TLS termination        | Pass-through or terminate | Terminates                      |
| Health checks          | TCP connect               | HTTP request/response           |
| Latency overhead       | <1ms                      | 1-5ms                           |
| Source IP preservation | Yes (NAT mode)            | Requires X-Forwarded-For        |
| Connections/sec        | Millions                  | Thousands-hundreds of thousands |
| Use case               | Gaming, IoT, raw TCP      | Web apps, APIs, microservices   |

---

### ⚠️ Common Misconceptions

| Misconception                          | Reality                                                                                                                                                               |
| -------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| L7 LB is always slower                 | L7 adds 1-5ms of latency due to HTTP parsing — negligible for most web applications where backend processing takes 10-500ms                                           |
| Load balancer = scale                  | LB distributes load but doesn't create capacity. If all backends are at 100% CPU, adding a LB doesn't help — add more backend instances                               |
| Sticky sessions solve all statefulness | Sticky sessions break when a backend fails (user session lost) or during scaling events. Design stateless services (session in Redis, JWT auth) for better resilience |

---

### 🚨 Failure Modes & Diagnosis

**Uneven Load Distribution — Hot Spot on One Backend**

```bash
# Check per-backend request counts (HAProxy stats socket)
echo "show stat" | socat stdio /var/run/haproxy/admin.sock | \
  awk -F',' 'NR>2 && $2=="BACKEND" {print $1, $48}'

# AWS ALB: CloudWatch metrics per target
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApplicationELB \
  --metric-name RequestCountPerTarget \
  --dimensions Name=TargetGroup,Value=targetgroup/xxx \
  --period 60 --statistics Sum

# Root causes:
# 1. IP hash with office NAT (1000 users → 1 backend)
#    Fix: switch to round-robin or least-connections
# 2. Sticky sessions with imbalanced users
#    Fix: reduce sticky session TTL, or make service stateless
# 3. Slow backend dragging connections
#    Fix: least-connections (automatically avoids slow backends)
```

---

### 🔗 Related Keywords

**Prerequisites:** `TCP`, `HTTP & APIs`, `IP Addressing`

**Related:** `Proxy vs Reverse Proxy`, `CDN`, `Service Discovery`, `Anycast`, `Firewall`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ L4           │ TCP/UDP; fast; IP+port routing; AWS NLB   │
│ L7           │ HTTP; smart routing; TLS term; AWS ALB    │
├──────────────┼───────────────────────────────────────────┤
│ ALGORITHMS   │ Round-robin, Least-conn, IP Hash, Weighted│
├──────────────┼───────────────────────────────────────────┤
│ L7 FEATURES  │ Path routing, host routing, canary deploy,│
│              │ sticky sessions, WAF, header manipulation  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "L4: dumb but fast traffic cop;           │
│              │  L7: intelligent HTTP request router"     │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Design the load balancing architecture for a large-scale video streaming service serving 100M users. (a) Why does the ingress use L4 (NLB) instead of L7 for the first hop — what does the L4 LB route to, and what L7 features are needed at the next tier? (b) How does consistent hashing enable "session affinity" at the CDN edge (same user's requests to the same edge cache node, improving cache hit rate)? (c) For HLS streaming: each video segment is a separate HTTP GET — why is L7 routing needed to route different quality levels to different backend transcoding tiers? (d) WebSocket connections for live chat alongside HTTP requests — how does the ALB handle WebSocket upgrades (HTTP Upgrade header, then persistent TCP), and should they be separate target groups? (e) Calculate the load balancer capacity needed: 100M users, 5% concurrent, 1 Mbps average = 5 Tbps aggregate — how many ALB instances does AWS provision (managed, scales automatically), and what's the PrivateLink architecture for internal service LBs?
