---
layout: default
title: "Load Balancing"
parent: "System Design"
nav_order: 683
permalink: /system-design/load-balancing/
number: "683"
category: System Design
difficulty: ★★☆
depends_on: "Horizontal Scaling"
used_by: "Round Robin, Least Connections, Consistent Hashing, Sticky Sessions"
tags: #intermediate, #distributed, #networking, #architecture, #reliability
---

# 683 — Load Balancing

`#intermediate` `#distributed` `#networking` `#architecture` `#reliability`

⚡ TL;DR — **Load Balancing** distributes incoming traffic across multiple backend servers to prevent any single server from becoming a bottleneck, enabling horizontal scaling and high availability.

| #683            | Category: System Design                                             | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------------------------ | :-------------- |
| **Depends on:** | Horizontal Scaling                                                  |                 |
| **Used by:**    | Round Robin, Least Connections, Consistent Hashing, Sticky Sessions |                 |

---

### 📘 Textbook Definition

A **Load Balancer** is a network component (hardware appliance or software service) that distributes incoming client requests across a pool of backend servers according to a configured algorithm, with the goals of maximising throughput, minimising response latency, preventing server overload, and providing fault tolerance. Load balancers operate at different OSI layers: **Layer 4 (Transport)** load balancers distribute based on IP/TCP/UDP connection properties, forwarding packets without inspecting the payload (e.g., AWS NLB); **Layer 7 (Application)** load balancers inspect HTTP headers, URLs, cookies, and payload to make intelligent routing decisions (e.g., AWS ALB, nginx, HAProxy). Load balancers perform health checks on backends and remove unhealthy instances from rotation, providing fault tolerance. Modern cloud-native systems use software load balancers (kube-proxy, Envoy, nginx) extensively at multiple layers: edge (internet → cluster), service mesh (service → service), and database (application → read replicas).

---

### 🟢 Simple Definition (Easy)

A load balancer is a traffic director: it receives all incoming requests and sends each one to a different server in a pool. Server A gets request 1, Server B gets request 2, Server C gets request 3, back to Server A. No single server gets all the traffic. If Server B dies, the load balancer stops sending it traffic.

---

### 🔵 Simple Definition (Elaborated)

Without a load balancer: all 10,000 requests/second hit your one server — it maxes out at 3,000 req/s and returns errors. With a load balancer in front of three servers: each server gets ~3,333 req/s, within capacity. Server 2 fails health check → load balancer routes its share to servers 1 and 3 (each now at ~5,000 req/s). Still handling load without manual intervention. This is the foundation of horizontal scaling: the load balancer makes multiple servers look like one endpoint to clients.

---

### 🔩 First Principles Explanation

**L4 vs L7 load balancing — what each can and cannot do:**

```
LAYER 4 (TCP/UDP) LOAD BALANCING:
  Operates at: IP addresses + TCP/UDP ports (no HTTP awareness)
  Sees: source IP, dest IP, source port, dest port, TCP flags
  Cannot see: HTTP headers, URL paths, cookies, request body

  How it works:
    Client → TCP SYN to LB IP:443
    LB: selects backend (e.g., round-robin by connection count)
    LB: forwards entire TCP stream to selected backend
    Connection: client ↔ backend (LB is transparent pass-through)

  Use cases:
    - Non-HTTP protocols (MySQL, PostgreSQL, gRPC)
    - Lowest latency (no packet inspection overhead)
    - TLS passthrough (LB doesn't decrypt; backend holds certificate)

  Tools: AWS NLB, HAProxy TCP mode, iptables DNAT

LAYER 7 (HTTP/HTTPS) LOAD BALANCING:
  Operates at: HTTP request headers, method, URL, cookies, body
  Can do: path-based routing, header-based routing, cookie affinity

  How it works:
    Client → TLS terminated at LB (LB has certificate)
    LB: reads HTTP request fully
    LB: routing decision based on URL/headers/cookies
    LB: new HTTP connection to selected backend (not original client TCP)

  Use cases:
    - HTTP/HTTPS web traffic (most modern services)
    - Path-based routing: /api/ → backend A, /static/ → CDN
    - A/B testing (route 10% by header to canary backend)
    - Session affinity (route by cookie to same backend)
    - Request manipulation (add headers, rewrite URLs)

  Tools: AWS ALB, nginx, HAProxy HTTP mode, Traefik, Envoy

```

**Health checks — how LB detects and removes unhealthy backends:**

```
PASSIVE HEALTH CHECK:
  LB monitors actual request failures.
  If backend returns 5xx or connection refused → mark unhealthy.
  Cons: requires real traffic to detect failure → some user requests fail first.

ACTIVE HEALTH CHECK (preferred):
  LB sends periodic probe requests to backend health endpoint.
  Backend: /actuator/health or /health/live → 200 if healthy, 503 if not.
  LB: if 3 consecutive probes fail → remove backend from rotation.
  LB: if 3 consecutive probes succeed → re-add backend.
  Cons: extra traffic overhead (usually negligible: 1 req/5s per backend).

  AWS ALB health check config:
    Health check path: /actuator/health
    Interval: 30 seconds
    Healthy threshold: 2 (2 successes → re-add)
    Unhealthy threshold: 3 (3 failures → remove)
    Timeout: 5 seconds

  Kubernetes readiness probe (same concept, pod-level):
    readinessProbe:
      httpGet:
        path: /actuator/health/readiness
        port: 8080
      periodSeconds: 10
      failureThreshold: 3
      successThreshold: 1
```

**Comparing load balancing algorithms:**

```
ROUND ROBIN:
  Backend 1 → Backend 2 → Backend 3 → Backend 1 → ...
  Simple, even distribution assuming equal request cost.
  Problem: if some requests take 10x longer, backends become uneven.

WEIGHTED ROUND ROBIN:
  Backend 1 (weight 3) → Backend 2 (weight 1) → ...
  Backend 1 gets 3x more requests.
  Use: heterogeneous servers (different capacities).

LEAST CONNECTIONS:
  Route to backend with fewest active connections.
  Better for variable request duration (long + short requests mixed).

LEAST RESPONSE TIME:
  Route to backend with lowest average response time.
  Best for latency-sensitive applications.

IP HASH:
  backend = hash(client_ip) % num_backends
  Same client IP always → same backend (sticky without cookies).
  Problem: if one backend fails, all its clients reassigned → cache miss storm.

CONSISTENT HASHING:
  client or request identifier → hash ring → backend
  Minimises reshuffling when backends added/removed.
  Use: cache proxies, distributed caching (memcached cluster).
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Load Balancing:

- All traffic to one server: single point of failure, capacity ceiling
- Server failure: complete outage
- Cannot benefit from horizontal scaling (multiple servers) without a distributor

WITH Load Balancing:
→ Multiple servers look like one endpoint to clients
→ Horizontal scaling: add servers to pool, load automatically distributed
→ Health checks: unhealthy servers removed from rotation automatically
→ Zero-downtime deployments: drain server, update, re-add (rolling update)

---

### 🧠 Mental Model / Analogy

> A traffic officer at a busy intersection directing cars to different parking lots. When lot A fills up or breaks down, the officer stops sending cars there. The officer can be smart (send trucks to lot C with higher ceilings), basic (round-robin: car 1 to A, car 2 to B), or adaptive (send to whichever lot has the fewest cars waiting). Drivers don't know which lot they'll end up in — they just follow the officer's direction.

"Traffic officer" = load balancer
"Cars" = requests
"Parking lots" = backend server instances
"Full/broken lot" = unhealthy backend (removed from rotation)

---

### ⚙️ How It Works (Mechanism)

**nginx as Layer 7 load balancer with path routing:**

```nginx
# nginx.conf: L7 load balancer with multiple backends
upstream order_service {
    # Least connections algorithm:
    least_conn;

    server order-service-1:8080 weight=1;
    server order-service-2:8080 weight=1;
    server order-service-3:8080 weight=1;

    # Health check:
    keepalive 32;  # keep 32 connections warm to each backend
}

upstream static_assets {
    server cdn.example.com:443;
}

server {
    listen 443 ssl;
    ssl_certificate     /etc/nginx/certs/server.crt;
    ssl_certificate_key /etc/nginx/certs/server.key;

    # Path-based routing (L7 capability):
    location /api/ {
        proxy_pass http://order_service;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Request-ID $request_id;
        proxy_connect_timeout 2s;
        proxy_read_timeout 30s;
    }

    location /static/ {
        proxy_pass https://static_assets;
    }
}
```

---

### 🔄 How It Connects (Mini-Map)

```
Horizontal Scaling
(multiple backend instances)
        │
        ▼
Load Balancing  ◄──── (you are here)
(distributes traffic across instances)
        │
  ┌─────┼──────────┬──────────────┐
  ▼     ▼          ▼              ▼
Round  Least     Consistent    Sticky
Robin  Connections Hashing     Sessions
(algorithms: how LB chooses a backend)
```

---

### 💻 Code Example

**AWS ALB with path-based routing via Terraform:**

```hcl
# ALB with path-based routing to different backend services:
resource "aws_lb_listener_rule" "order_api" {
  listener_arn = aws_lb_listener.https.arn
  priority     = 100

  condition {
    path_pattern { values = ["/api/orders*"] }
  }
  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.order_service.arn
  }
}

resource "aws_lb_target_group" "order_service" {
  name     = "order-service-tg"
  port     = 8080
  protocol = "HTTP"
  vpc_id   = var.vpc_id

  health_check {
    path                = "/actuator/health"
    interval            = 30
    healthy_threshold   = 2
    unhealthy_threshold = 3
    timeout             = 5
    matcher             = "200"
  }

  # Deregistration delay: give instances time to drain in-flight requests
  deregistration_delay = 30
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                                | Reality                                                                                                                                                                                                    |
| ------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Load balancers eliminate single points of failure completely | The load balancer itself can be a SPOF. Production systems run LBs in active-active or active-passive HA pairs. Cloud-managed LBs (AWS ALB/NLB) are inherently HA across multiple AZs                      |
| More backends always means better performance                | Adding backends improves throughput, but if the bottleneck is the database (all backends share one DB), adding app servers just shifts the bottleneck. Profile to find the actual constraint               |
| Round-robin ensures perfectly even distribution              | Round-robin distributes connections evenly, but if some requests take 100x longer than others (long-polling, file uploads), backends become very uneven. Least-connections handles this better             |
| Load balancers work only at the network edge                 | Modern architectures use load balancing at multiple layers: edge LB (internet→cluster), service mesh (service→service), connection pooling (app→DB replicas), message partitioning (Kafka consumer groups) |

---

### 🔥 Pitfalls in Production

**Deregistration delay too short — dropping in-flight requests:**

```
PROBLEM:
  AWS ALB: deregistration_delay = 5 seconds (AWS default: 300s, team reduced it)
  Rolling deployment: instance deregistered from target group
  ALB: 5 seconds later, stops routing new requests to instance
  But: instance has 15-second requests in-flight (file upload, report generation)
  Those 15-second requests: connection reset by ALB after 5 seconds → 502

FIX:
  deregistration_delay = 60  # >= max expected request duration

  AND: application graceful shutdown drain timeout >= deregistration_delay:
  server:
    shutdown: graceful
  spring:
    lifecycle:
      timeout-per-shutdown-phase: 55s  # slightly less than 60s ALB delay

  SEQUENCE:
    ALB: deregisters instance → waits 60s → cuts connection
    App: receives SIGTERM → drains requests for 55s → exits
    60s > 55s → app finishes draining before ALB cuts connection
    Result: zero in-flight request drops
```

---

### 🔗 Related Keywords

- `Horizontal Scaling` — load balancing enables horizontal scaling by distributing across instances
- `Round Robin` — the simplest load balancing algorithm
- `Least Connections` — algorithm for variable-duration request workloads
- `Consistent Hashing (Load Balancing)` — algorithm minimising redistribution on server changes
- `Sticky Sessions` — session-based routing for stateful applications
- `Auto Scaling` — adjusts backend pool size; load balancer routes to current pool

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Distribute requests across server pool.  │
│              │ L4=TCP/UDP; L7=HTTP-aware routing        │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Multiple backend instances; need HA;      │
│              │ path/header-based routing required        │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Single-instance, low-traffic internal     │
│              │ services where LB adds unnecessary hops   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The traffic officer making sure no one   │
│              │  parking lot is ever full."               │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Round Robin → Least Connections           │
│              │ → Consistent Hashing                      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You are designing a load balancing strategy for a service that handles two types of requests: (a) fast API calls averaging 50ms, (b) slow report generation averaging 45 seconds. Both go to the same backend pool of 5 servers. Explain why round-robin fails for this workload mix. What algorithm would you use, how would you configure it, and would you consider separating the two request types into different backend pools?

**Q2.** Your AWS ALB routes traffic to 3 backend instances across 3 Availability Zones. AZ-b's backend fails its health check. ALB immediately removes AZ-b's instance, routing all traffic to AZ-a and AZ-c instances (now at 150% of original load). AZ-a's instance struggles under the increased load and starts timing out. Describe the cascading failure mechanism (hint: this is the "thundering herd" / cascade failure pattern). What ALB and auto-scaling configuration prevents this failure cascade from occurring?
