---
layout: default
title: "Horizontal Scaling"
parent: "System Design"
nav_order: 682
permalink: /system-design/horizontal-scaling/
number: "682"
category: System Design
difficulty: ★☆☆
depends_on: "Vertical Scaling, Load Balancing"
used_by: "Auto Scaling, Sharding"
tags: #foundational, #distributed, #architecture, #performance, #cloud
---

# 682 — Horizontal Scaling

`#foundational` `#distributed` `#architecture` `#performance` `#cloud`

⚡ TL;DR — **Horizontal Scaling** (scale-out) adds more servers/instances to distribute load across multiple machines rather than making one machine bigger.

| #682            | Category: System Design          | Difficulty: ★☆☆ |
| :-------------- | :------------------------------- | :-------------- |
| **Depends on:** | Vertical Scaling, Load Balancing |                 |
| **Used by:**    | Auto Scaling, Sharding           |                 |

---

### 📘 Textbook Definition

**Horizontal Scaling** (scaling out) is the practice of increasing system capacity by adding more machines (nodes, instances, pods) to a pool of resources that serve requests in parallel, distributed by a load balancer. Horizontal scaling is theoretically unbounded — unlike vertical scaling, there is no hardware ceiling on the number of machines added. For horizontal scaling to work, the application must be **stateless** (or externalise state to a shared backing store such as Redis or a database), so any instance can serve any request. Horizontal scaling enables **high availability** (multiple instances mean no single point of failure), **elastic scalability** (instances added and removed dynamically with load), and **fault tolerance** (failed instances are replaced without impacting overall capacity significantly).

---

### 🟢 Simple Definition (Easy)

Horizontal scaling = add more servers instead of upgrading one server. Instead of one powerful server, you have ten normal servers sharing the work. A load balancer distributes requests across all ten. If one fails, nine continue. Need more capacity? Add more servers.

---

### 🔵 Simple Definition (Elaborated)

Your web service handles 10,000 requests/second but needs 50,000 req/s. Vertical option: upgrade to a 5x larger server. Horizontal option: add 4 more identical servers behind a load balancer, handling 10,000 req/s each. Horizontal wins on: cost (cheaper commodity hardware), availability (one server failure = 20% capacity loss, not 100%), and elasticity (auto-scale to 10 servers during peak, back to 2 at night). The requirement: your app must not store state locally (no in-memory sessions, no local files) — all state in shared Redis/DB.

---

### 🔩 First Principles Explanation

**The statelessness requirement — why horizontal scaling demands it:**

```
STATEFUL SERVICE (cannot horizontal scale without sticky sessions):

  Request 1: POST /login → Server A stores session {userId: 42} in memory
  Request 2: GET /profile → load balancer routes to Server B
  Server B: no session for userId 42 → 401 Unauthorized (user logged out!)

  "Fix": sticky sessions → same user always to same server
  Problem: Server A gets 60% of traffic (some users hit A more)
           Server A crashes → all its users logged out
           Uneven distribution → back to single-server bottleneck

STATELESS SERVICE (designed for horizontal scaling):

  Request 1: POST /login → Server A → stores session in Redis
             Returns JWT token to client
  Request 2: GET /profile + JWT → load balancer routes to Server B
  Server B: validates JWT (cryptographic, no external call) → 200 OK

  Any server serves any request. True horizontal scaling.

RULE: Externalise ALL state:
  Sessions: Redis / JWT (client-side)
  User uploads: S3 / object storage (not local /tmp)
  Application config: ConfigMaps / env vars
  Computation state: Redis / DB (not JVM heap)
```

**Amdahl's Law: theoretical limit of horizontal scaling:**

```
Amdahl's Law:
  Speedup = 1 / (s + (1-s)/n)
  where:
    s = fraction of work that MUST be sequential (cannot be parallelised)
    n = number of processors/servers
    (1-s) = fraction that can be parallelised

Example: s = 0.1 (10% of work is sequential — e.g., a global lock)
  n = 2:    speedup = 1 / (0.1 + 0.9/2) = 1.82x
  n = 10:   speedup = 1 / (0.1 + 0.9/10) = 5.26x
  n = 100:  speedup = 1 / (0.1 + 0.9/100) = 9.17x
  n = ∞:    speedup = 1 / 0.1 = 10x MAX

LESSON:
  Even with unlimited horizontal scaling, if 10% of your work is sequential,
  maximum possible speedup = 10x regardless of number of servers.

  The bottleneck:
  - Shared database lock (all writes serialised)
  - Single Kafka partition (all messages from one partition to one consumer)
  - Global counter increment (requires coordination)

  Horizontal scaling ROI diminishes with increasing sequential fraction.
  Identify and eliminate sequential bottlenecks before scaling out.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Horizontal Scaling:

- Single server ceiling: cannot serve traffic beyond one machine's capacity
- Single point of failure: one server down = complete outage
- Expensive vertical headroom: 10x bigger server costs much more than 10x price
- No elastic capacity: cannot quickly add/remove capacity for traffic spikes

WITH Horizontal Scaling:
→ Unlimited theoretical capacity: add more servers for any load
→ High availability: multiple servers, failure of one reduces capacity by 1/N
→ Cost efficiency: commodity hardware, pay for what you use
→ Elasticity: auto-scale up in minutes during peak, back down to save cost

---

### 🧠 Mental Model / Analogy

> A checkout queue at a supermarket. With one cashier (vertical scaling), you make them work faster (scanner upgrade, better training). With multiple cashiers (horizontal scaling), you open more lanes. More customers served simultaneously. If one cashier calls in sick (server failure), other lanes absorb the load. At midnight (low traffic), close most lanes (scale down).

"Cashiers" = server instances
"Lanes" = horizontally scaled endpoints behind load balancer
"Queue manager" = load balancer
"Calling in sick" = instance failure
"Open/close lanes" = auto-scaling up and down

---

### ⚙️ How It Works (Mechanism)

**Kubernetes horizontal pod autoscaling:**

```yaml
# Kubernetes Deployment: horizontal scaling via replicas
apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-service
spec:
  replicas: 3 # start with 3 instances
  selector:
    matchLabels:
      app: order-service
  template:
    spec:
      containers:
        - name: order-service
          image: order-service:v2.0.0
          resources:
            requests:
              cpu: "500m"
              memory: "512Mi"
            limits:
              cpu: "1000m"
              memory: "1Gi"
---
# HorizontalPodAutoscaler: auto-scale based on CPU
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: order-service-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: order-service
  minReplicas: 2 # always at least 2 for availability
  maxReplicas: 20 # cap to control costs
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70 # scale when avg CPU > 70%
```

---

### 🔄 How It Connects (Mini-Map)

```
Vertical Scaling
(scale up: hits ceiling)
        │
        ▼
Horizontal Scaling  ◄──── (you are here)
(scale out: add more servers)
        │
        ├── Load Balancing (distributes requests across instances)
        ├── Auto Scaling (automates horizontal scale decisions)
        └── Sharding (horizontal data partitioning for databases)
```

---

### 💻 Code Example

**Stateless service with externalised session — Spring Boot + Redis:**

```java
// application.yml: externalise sessions to Redis for horizontal scaling
spring:
  session:
    store-type: redis     # sessions in Redis, not JVM memory
    timeout: 30m
  data:
    redis:
      url: ${REDIS_URL}   # e.g. redis://redis.svc.cluster.local:6379

// Result: any pod can serve any request — sessions not tied to a specific pod
// Load balancer: no sticky sessions needed
// Pod failure: users' sessions survive (in Redis, not in failed pod's memory)

// Alternatively: JWT (stateless auth — no server-side session needed)
@RestController
class OrderController {
    @GetMapping("/api/orders")
    ResponseEntity<List<Order>> getOrders(
            @AuthenticationPrincipal JwtAuthenticationToken jwt) {
        // JWT validated cryptographically — no Redis lookup needed
        // Any pod validates the same JWT (shared signing key or public key)
        String userId = jwt.getTokenAttributes().get("sub").toString();
        return ResponseEntity.ok(orderService.getOrdersForUser(userId));
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                              | Reality                                                                                                                                                                                                                        |
| ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Horizontal scaling is always better than vertical          | Databases are often better vertically scaled (simpler, less coordination overhead). Stateless web/API tiers benefit most from horizontal scaling. The right approach depends on workload type                                  |
| Adding more servers always increases throughput linearly   | Amdahl's Law: sequential bottlenecks (shared locks, single-partition queues, synchronised code) limit parallel speedup. Adding 10x servers to a system with a 20% sequential fraction gives at most ~3.5x speedup              |
| Horizontal scaling requires a complete application rewrite | The main requirement is statelessness. For many applications, the primary change is externalising session storage (Redis) and file storage (S3). This is a focused refactor, not a full rewrite                                |
| More instances always means higher cost                    | At peak load, horizontal scaling with auto-scaling is often cheaper than keeping a large vertically-scaled instance idle at low utilisation. Pay-per-use cloud instances benefit significantly from scale-down during off-peak |

---

### 🔥 Pitfalls in Production

**Thundering herd on scale-out event:**

```
PROBLEM:
  Auto-scaler adds 5 new pods during a traffic spike.
  New pods start, register with load balancer.
  Load balancer immediately routes 20% of traffic to each new pod.
  New pods: cold JVM (no JIT warmup), cold cache (no data loaded).
  Result: new pods take 3-5x longer to handle requests than warm pods.
  For 2-3 minutes: overall latency INCREASES as new pods serve traffic slowly.
  Users: experience degraded performance exactly during the scale-up event.

FIX:
  1. Readiness probe with warmup delay:
     initialDelaySeconds: 30  # let JVM/cache warm before receiving traffic

  2. Staged traffic increase (slow ramp):
     Kubernetes: new pods get traffic gradually as readiness probes pass
     (not immediate 100% share — starts at smaller fraction as pool grows)

  3. Pre-warming via synthetic requests:
     postStart lifecycle hook: make internal requests to pre-populate caches

  4. Proactive scaling: scale BEFORE traffic hits (based on schedule/prediction)
     not reactive scaling: wait for CPU to hit 70% then scramble
     KEDA: scale based on Kafka consumer lag → scale before pod is overwhelmed
```

---

### 🔗 Related Keywords

- `Vertical Scaling` — the alternative: scale up one machine vs scale out many machines
- `Load Balancing` — prerequisite: distributes requests across horizontally-scaled instances
- `Auto Scaling` — automates horizontal scale decisions based on metrics
- `Stateless Processes` — Twelve-Factor principle: required for effective horizontal scaling
- `Sharding (System)` — horizontal scaling for databases (partitioning data across nodes)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Add MORE servers, distribute load via LB. │
│              │ Stateless required. Theoretically unbounded│
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Stateless web/API tiers; elastic traffic; │
│              │ high availability required                 │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Stateful workloads with hard partitioning │
│              │ problems (legacy DBs, single-writer apps)  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Ten average chefs beat one superhuman    │
│              │  chef — and if one gets sick, dinner      │
│              │  still gets served."                      │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Load Balancing → Auto Scaling → Sharding  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You have a Java service that maintains an in-memory LRU cache of the 10,000 most-recently accessed products (to reduce DB load). You horizontally scale from 1 to 10 pods. Calculate the cache hit rate change: if the original single pod had a 90% cache hit rate (because it saw all traffic), what is the approximate hit rate for each pod after scaling to 10 pods with round-robin load balancing? What is the impact on database load, and how would you redesign the caching strategy to preserve cache effectiveness after horizontal scaling?

**Q2.** Amdahl's Law says a system with 5% sequential code has a theoretical maximum speedup of 20x regardless of how many servers you add. Your team is horizontally scaling from 1 to 50 pods and observing only 8x throughput improvement. What fractions of your work are likely sequential bottlenecks? Name three specific architectural bottlenecks common in Spring Boot + PostgreSQL applications that create this sequential serialisation effect, and how you would identify each using observability tools.
