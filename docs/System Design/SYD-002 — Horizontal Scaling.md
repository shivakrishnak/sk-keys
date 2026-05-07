---
layout: default
title: "Horizontal Scaling"
parent: "System Design"
nav_order: 2
permalink: /system-design/horizontal-scaling/
number: "SYD-002"
category: System Design
difficulty: ★☆☆
depends_on: Load Balancing, Vertical Scaling, Stateless Design
used_by: Auto Scaling, Microservices, Distributed Systems
related: Vertical Scaling, Load Balancing, Sharding
tags:
  - scaling
  - distributed
  - performance
  - infrastructure
  - foundational
---

# SYD-002 — Horizontal Scaling

⚡ TL;DR — Adding more machines to distribute load across many nodes instead of maxing out one powerful machine—the foundation of modern cloud systems.

| #682            | Category: System Design                          | Difficulty: ★☆☆ |
| :-------------- | :----------------------------------------------- | :-------------- |
| **Depends on:** | Load Balancing, Vertical Scaling                 |                 |
| **Used by:**    | Auto Scaling, Microservices, Distributed Systems |                 |
| **Related:**    | Vertical Scaling, Load Balancing, Sharding       |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Your system has maxed out vertical scaling. You bought the biggest machine on Earth. But traffic keeps growing—your largest instance still hits 100% CPU at peak. You're stuck. You can't buy a bigger machine. You can't add code—code runs on the same hardware. You need a way to spread the load across MULTIPLE machines.

**THE BREAKING POINT:**
A single machine has a ceiling. Once you hit it, there's nowhere to go. No matter how much money you throw at it, one box can't absorb infinite traffic. The only escape: stop trying to fit everything on one machine. Instead, run many machines in parallel.

**THE INVENTION MOMENT:**
"This is why horizontal scaling was created—because at some point, you need to stop scaling UP and start scaling OUT."

---

### 📘 Textbook Definition

Horizontal scaling (or scale-out) is the process of adding more machines (nodes) to a distributed system to handle increased load. Unlike vertical scaling, which increases the resources of a single machine, horizontal scaling distributes workload across multiple machines, potentially indefinitely. It requires stateless application design, a load balancer to route traffic, and careful handling of session state and database coordination.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Instead of one huge machine, use many smaller machines working together.

**One analogy:**

> A restaurant's kitchen has one brilliant chef. During rush hour, 200 customers arrive. The chef can cook faster (vertical scale—upgrade skills), but eventually hits a wall—one person can only work so fast. The smarter move: hire four normal chefs. They divide the orders. Work gets done 4x faster because now it's parallel, not a bottleneck.

**One insight:**
Horizontal scaling is harder than vertical scaling because now your machines must coordinate—they share data, must handle session state, and the load balancer decides who handles each request. But once you solve that complexity, you can scale indefinitely.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Adding machines (linearly) increases throughput linearly, unlike vertical scaling which has diminishing returns
2. A load balancer is mandatory—it decides which machine handles each request
3. Applications must be stateless or have shared state (sessions, cache) accessible to all machines

**DERIVED DESIGN:**
You start with one machine hitting its ceiling. You decide to add a second identical machine. Traffic routes through a load balancer: 50% to machine A, 50% to machine B. Each machine is now at 50% capacity. Add a third machine, each handles 33% of traffic. This compounds indefinitely—add 100 machines, each handles 1% of traffic. The system is now horizontally scalable: as load increases, add more machines.

**THE TRADE-OFFS:**
**Gain:** Theoretically unlimited scalability. Your system can handle 10x, 100x, 1000x growth by adding machines. No hardware ceiling. Cost grows linearly with traffic, not exponentially.

**Cost:** Complexity explodes. Now you have distributed systems problems: session management, data consistency, request routing, failure handling. One machine fails, traffic routes to others—but is that data replicated? What if the database becomes the bottleneck instead?

---

### 🧪 Thought Experiment

**SETUP:**
A payment processing API receives 1000 requests/second. It runs on a single `c5.4xlarge` machine (16 CPUs). CPU is maxed at 100%.

**WHAT HAPPENS WITHOUT HORIZONTAL SCALING:**
That single machine processes exactly 1000 req/sec. It cannot go faster—it's at full capacity. Any traffic spike causes queuing. Requests timeout. Customers get 503 errors. Revenue lost. You're stuck at 1000 req/sec forever (on that hardware).

**WHAT HAPPENS WITH HORIZONTAL SCALING:**
Deploy the same application to 4 identical machines. Add a load balancer (NGINX or AWS ELB) in front. Now: each machine handles 250 req/sec. CPU on each is 25%. Plenty of headroom. Traffic spikes to 1500 req/sec? Fine—machines go to 37.5% CPU. Spike to 2000 req/sec? Add a 5th machine. Instant. Automatic if you use auto-scaling. The system now scales with demand.

**THE INSIGHT:**
Vertical scaling is additive (1 big machine). Horizontal scaling is multiplicative (N small machines). Multiplicative is vastly superior at scale, but requires solving harder distributed systems problems first.

---

### 🧠 Mental Model / Analogy

> A car (vertical scaling) can only go so fast—max engine power limits it. A fleet of cars (horizontal scaling) can move infinitely more cargo by having many vehicles working in parallel. The challenge: you need a dispatcher (load balancer) to send each delivery to an available car, and all cars must follow the same route (API contracts).

- "One car going faster" → one machine upgraded with better CPU
- "A fleet of cars" → multiple identical machines
- "Dispatcher assigning deliveries" → load balancer routing requests
- "All cars must follow the same route" → all app servers must implement the same API
- "Delivery success depends on any car succeeding" → request succeeds if any server succeeds, others are redundant

**Where this analogy breaks down:** Unlike cars, adding a 100th machine to a system with a single database bottleneck doesn't help—the database remains the bottleneck, no matter how many app servers you add.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Instead of one super-fast computer, use ten normal computers all working at the same time. A load balancer (like a receptionist) sends each incoming request to an available computer. If one computer gets sick, the others keep working.

**Level 2 — How to use it (junior developer):**
Write your application so it doesn't store any data locally (stateless). Every request is independent—it doesn't rely on memory from the previous request. Requests to `/api/user/123` should get the same answer no matter which machine handles it. Deploy this same application to 3, 5, or 10 machines. Put a load balancer in front (AWS ELB, NGINX, HAProxy). The load balancer distributes traffic round-robin or least-connections. Test that requests work from any server.

**Level 3 — How it works (mid-level engineer):**
Machines are deployed in an auto-scaling group (e.g., AWS ASG). When average CPU across the group exceeds 70%, the ASG launches new instances. When CPU drops below 30%, it terminates underutilized instances. The load balancer health-checks each machine periodically (every 5 seconds). If a machine fails health checks, it's removed from the pool automatically. The database layer may become the bottleneck instead—horizontally scaling app servers doesn't help if the database can't handle the query load. You'd then scale the database (read replicas, sharding) separately.

**Level 4 — Why it was designed this way (senior/staff):**
Horizontal scaling emerged as cloud computing commoditized small machines (EC2). It became cheaper to rent 10 small instances than 1 huge instance with the same total power. Stateless application design (REST APIs, 12-factor app) made this tractable. The tradeoff: you trade simplicity (one machine) for scalability (many machines) and must solve problems like session affinity, circuit breakers, and graceful shutdown. This design philosophy dominates modern cloud-native systems.

---

### ⚙️ How It Works (Mechanism)

Horizontal scaling works in these phases:

1. **Application Design (Stateless):**
   - Each request is independent; no local data stored on a machine
   - All state in external systems: database, cache, session store
   - If machine A handles request 1 and machine B handles request 2, same data is available to both

2. **Deployment (Identical Replicas):**
   - Deploy the same application code to multiple machines
   - Each has same config, same database connection strings, same environment variables
   - No "special" machines; all are interchangeable

3. **Load Balancer Setup:**
   - Place load balancer in front (NGINX, HAProxy, AWS ELB, Azure LB)
   - Configure health checks: load balancer calls `/health` endpoint every 5 seconds
   - If machine doesn't respond, remove from pool; add back when healthy
   - Route traffic using algorithm: round-robin, least-connections, IP-hash (sticky)

4. **Request Flow:**
   - Client sends request to load balancer's IP/hostname
   - Load balancer picks an available machine (using algorithm)
   - Machine processes request, queries shared database/cache
   - Response returned to client

5. **Scaling Decisions:**
   - Monitor metrics: CPU, memory, request count
   - If metrics exceed threshold (70% CPU for 5 minutes), launch new machines
   - If metrics drop below threshold (20% CPU for 10 minutes), terminate machines
   - No human intervention needed (if auto-scaling configured)

```
  Client 1 ──┐
  Client 2 ──┼──→ LOAD BALANCER ──→ App Server 1 ──┐
  Client 3 ──┤    (Decides which      App Server 2 ──→ Shared Database
  ...        │     server handles      App Server 3 ──┐
  Client 1000─     each request)       App Server 4 ──┘
```

**In Happy Path:**
Request arrives → Load balancer picks server 2 (least connections) → Server 2 queries database → Response returns → Load balancer forwards to client. All servers handle traffic in parallel.

**When Something Goes Wrong:**
Server 2 crashes → Load balancer health check fails → Server 2 removed from pool → Future requests go to servers 1, 3, 4 → System continues working. No downtime, no user impact.

---

### 🔄 The Complete Picture — End-to-End Flow

```
Traffic Arrives
    ↓
LOAD BALANCER (YOU ARE HERE)
Chooses an available server
    ↓
Request → Server 1 / Server 2 / Server 3 (parallel)
    ↓
Each server queries SHARED DATABASE
    ↓
Response sent back through load balancer
    ↓
User gets result

FAILURE PATH:
    Server 2 dies (crash)
        ↓
    Load balancer detects no response
        ↓
    Server 2 removed from pool
        ↓
    New requests go to Servers 1, 3
        ↓
    Auto-scaler launches replacement Server 4
        ↓
    System continues, user unaffected
```

**WHAT CHANGES AT SCALE:**
At 10x traffic, horizontal scaling is straightforward—add more servers. At 100x traffic, the database becomes bottleneck (can't handle queries from 100 servers). You must then scale the database (read replicas, sharding, caching layer) separately. At 1000x traffic, the network, DNS, and load balancer become bottlenecks. You need multi-region setup, DNS failover, and potentially CDN for static content.

---

### 💻 Code Example

Horizontal scaling requires stateless application design. Here's the pattern:

**Example 1 — Stateless API (GOOD):**

```python
# app.py - stateless
from flask import Flask, request
import redis

app = Flask(__name__)
cache = redis.Redis(host='shared-cache.internal', port=6379)

@app.route('/api/user/<user_id>')
def get_user(user_id):
    # Check shared cache first
    cached = cache.get(f'user:{user_id}')
    if cached:
        return cached

    # Query shared database
    user = db.query('SELECT * FROM users WHERE id = ?', user_id)
    cache.set(f'user:{user_id}', user, ex=3600)  # Cache 1 hour
    return user

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

Deploy this to machines A, B, C. Load balancer sends requests. Each handles requests independently. Database and cache are shared.

**Example 2 — Stateful API (BAD):**

```python
# BAD: in-memory session store
sessions = {}  # This is local to ONE machine!

@app.route('/login', methods=['POST'])
def login():
    user_id = request.json['user_id']
    sessions[user_id] = {'logged_in': True, 'time': now()}
    return {'status': 'ok'}

@app.route('/profile')
def profile():
    user_id = request.headers['User-Id']
    if user_id not in sessions:  # BROKEN if different machine handled login!
        return {'error': 'not logged in'}
    return {'user_id': user_id}
```

If Machine A handles /login, Machine B handles /profile, session lookup fails—each machine has different in-memory state.

**Example 3 — Production Pattern (Stateless with Load Balancer):**

```python
# app.py (same on all servers)
from flask import Flask, session
from flask_session import Session
import redis

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis.from_url('redis://shared-redis.internal:6379')
Session(app)

@app.route('/login', methods=['POST'])
def login():
    session['user_id'] = request.json['user_id']  # Stored in SHARED redis
    session['ip'] = request.remote_addr
    return {'status': 'ok'}

@app.route('/profile')
def profile():
    user_id = session.get('user_id')  # Fetched from SHARED redis
    if not user_id:
        return {'error': 'not logged in'}, 401
    return {'user_id': user_id}
```

Now /login can be handled by Machine A, /profile by Machine B—session data is in shared Redis, accessible to both.

---

### ⚖️ Comparison Table

| Approach               | Scalability                               | Complexity                                    | Cost            | Latency                             | Best For                                     |
| ---------------------- | ----------------------------------------- | --------------------------------------------- | --------------- | ----------------------------------- | -------------------------------------------- |
| **Vertical Scaling**   | Limited (hw ceiling ~448 CPUs, 700GB RAM) | Low                                           | High per unit   | Low (single machine)                | Startups, small systems <100K users          |
| **Horizontal Scaling** | Unlimited (add 1000s of machines)         | High (load balancer, session mgmt, data sync) | Medium per unit | Slightly higher (LB + network hops) | Large systems, social networks, payment APIs |
| **Hybrid (Both)**      | Unlimited                                 | Very high                                     | Very high       | Low-medium                          | Enterprises, critical systems                |

**How to choose:** Start with vertical scaling (simplicity). As traffic grows, add more machines gradually (horizontal). Eventually use both: multiple large machines + load balancing = sweet spot between simplicity and unlimited scale.

---

### 🔁 Flow / Lifecycle

Horizontal scaling is continuous as traffic changes:

```
START: 1 Application Server
  ↓
MONITOR: Track CPU, connections, response time
  ↓
TRAFFIC INCREASES
  ├─ CPU avg = 75% for 5 min? → LAUNCH new server
  │
  ├─ CPU avg = 85% for 3 min? → LAUNCH 2 new servers
  │
  └─ CPU avg = 50% for 15 min? → TERMINATE underutilized server
       ↓
    New servers: BOOT
      (30s–60s for instance launch + app startup)
       ↓
    Health check: VERIFY new servers responding
       ↓
    Load balancer: ADD to pool
       ↓
    TRAFFIC ROUTES to new servers
       ↓
    LOOP back to MONITOR
```

---

### ⚠️ Common Misconceptions

| Misconception                                                            | Reality                                                                                                                                       |
| ------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------- |
| "Horizontal scaling solves all performance problems"                     | It scales the app layer. If database or cache is bottleneck, adding more app servers doesn't help.                                            |
| "Horizontal scaling means zero-downtime deployment"                      | You can do rolling deploys with minimal downtime, but you must drain connections gracefully. Not truly zero.                                  |
| "Horizontal scaling costs less than vertical"                            | Not always. 10 small machines may cost more than 1 large machine with same total power, but small machines have better hourly rates per unit. |
| "Any stateful application can be horizontally scaled by adding sessions" | Requires external session store (Redis, memcached). Adds latency and another component to fail. Not free.                                     |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Database Becomes Bottleneck**

**Symptom:**
You added 10 app servers. CPU on each is 20%. But response times remain slow (2 seconds instead of 100ms). Database CPU is 100%.

**Root Cause:**
App servers are fine; they're not the bottleneck. But they all query the single database, which can't keep up.

**Diagnostic Command:**

```bash
# Check app server CPU
top -b -n 1 | grep "Cpu(s)"
# Expected: 20–30% if scaled correctly

# Check database CPU
ssh db-server
top -b -n 1 | grep "Cpu(s)"
# If 100%: database is bottleneck

# Check query latency
mysql> SELECT AVG(Query_time) FROM mysql.slow_log;
# If > 0.5s: queries are slow
```

**Fix:**
Bad approach: Add more app servers (won't help, database is bottleneck).
Good approach: Scale database. Add read replicas, enable caching (Redis), optimize slow queries, or partition data (sharding).

**Prevention:**
Monitor database metrics separately from app servers. Have separate auto-scaling rules for database tier. If database CPU > 80%, scale database first, app second.

---

**Failure Mode 2: Load Balancer Is Single Point of Failure**

**Symptom:**
Load balancer crashes. All traffic stops. 100% downtime. Users see connection refused.

**Root Cause:**
You set up horizontal scaling with ONE load balancer. If it dies, no requests route anywhere, even though all app servers are healthy.

**Diagnostic Command:**

```bash
# Check load balancer health
curl -i http://load-balancer.internal/health
# If connection refused or timeout: LB is down

# Check app servers (bypass LB)
curl -i http://app-server-1.internal/health
# If healthy: app servers are OK, problem is LB
```

**Fix:**
Bad approach: Hope load balancer doesn't crash.
Good approach: Run multiple load balancers in active-active or active-passive mode. Use DNS failover or keepalived to switch if primary LB dies. Make LB highly available.

**Prevention:**
Assume load balancer will fail. Design for it: redundant load balancers, health checks on LB itself, automatic failover to backup LB.

---

**Failure Mode 3: Uneven Traffic Distribution (Hotspot)**

**Symptom:**
Round-robin load balancing sends 10 requests to each server. But Server 1 consistently slower than Servers 2–4. Response times spike randomly.

**Root Cause:**
Machine hardware is heterogeneous (Server 1 is an older instance type). Or Server 1 is co-located with other noisy neighbors (resource contention). Or load balancer algorithm (round-robin) doesn't account for actual server capacity.

**Diagnostic Command:**

```bash
# Check response time per server
tail -f /var/log/nginx/access.log | \
  awk '{print $1, $10}' | sort | uniq -c
# If Server 1 consistently slower: investigate

# Check server specs
aws ec2 describe-instances --query 'Reservations[].Instances[].InstanceType' | sort | uniq -c
# If mixed types: upgrade Server 1 or use least-connections algorithm
```

**Fix:**
Bad approach: Ignore and accept slow responses from Server 1.
Good approach: (1) Use least-connections or least-latency algorithm instead of round-robin. (2) Replace Server 1 with same spec as others. (3) Move other workloads off Server 1 to reduce contention.

**Prevention:**
Use homogeneous instance types. Use adaptive load balancing (least-connections/latency, not round-robin). Monitor response time per server. Alert if variance > 20%.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Vertical Scaling` — the single-machine approach; understand before comparing to horizontal
- `Load Balancing` — the infrastructure that makes horizontal scaling possible
- `Stateless Design` — required for horizontal scaling to work correctly

**Builds On This (learn these next):**

- `Auto Scaling` — automate horizontal scaling based on metrics
- `Microservices` — architecture designed for horizontal scaling
- `Database Replication` — scale database layer horizontally via read replicas

**Alternatives / Comparisons:**

- `Vertical Scaling` — opposite strategy; upgrade one machine instead of adding more
- `Caching` — improve performance without scaling machines (addresses throughput differently)
- `Sharding` — distribute data across machines instead of replicating to all machines

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Adding more machines to handle        │
│              │ load in parallel, with a load         │
│              │ balancer routing requests             │
├──────────────┼────────────────────────────────────────┤
│ PROBLEM IT   │ Single machine hits ceiling;          │
│ SOLVES       │ need unlimited scalability            │
├──────────────┼────────────────────────────────────────┤
│ KEY INSIGHT  │ Requires stateless design;            │
│              │ all servers must be identical         │
│              │ and state must be external            │
├──────────────┼────────────────────────────────────────┤
│ USE WHEN     │ Traffic > largest single machine      │
│              │ can handle; need automatic scaling    │
├──────────────┼────────────────────────────────────────┤
│ AVOID WHEN   │ Application has heavy local state;    │
│              │ load balancer becomes bottleneck;     │
│              │ database can't handle query storm     │
├──────────────┼────────────────────────────────────────┤
│ TRADE-OFF    │ [Unlimited scale] vs [complex,        │
│              │ distributed systems problems]         │
├──────────────┼────────────────────────────────────────┤
│ ONE-LINER    │ "Many small machines beat one big     │
│              │ one—if you solve coordination."       │
├──────────────┼────────────────────────────────────────┤
│ NEXT EXPLORE │ Load Balancing → Auto Scaling →       │
│              │ Microservices                         │
└──────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You have 10 app servers behind a load balancer, all querying a single database. Traffic increases 5x. You add 50 more app servers. Response times stay slow (2s instead of 100ms). Why didn't adding more servers help, and what should you have done instead?

**Q2.** Your application stores user sessions in a local in-memory dictionary. You want to horizontally scale it to 10 servers. What architectural changes must you make, and what new failure modes do you introduce by centralizing session state in Redis?
