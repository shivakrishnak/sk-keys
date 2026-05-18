---
id: NET-031
title: "Load Balancer Basics"
category: Networking
tier: tier-2-networking-security
folder: NET-networking
difficulty: ★★☆
depends_on: NET-003, NET-030
used_by: NET-046
related: NET-003, NET-032, NET-046
tags:
  - networking
  - load-balancing
  - availability
  - scaling
  - reverse-proxy
status: complete
version: 4
layout: default
parent: "Networking"
grand_parent: "Technical Mastery"
nav_order: 31
permalink: /technical-mastery/net/load-balancer-basics/
---

**⚡ TL;DR** - A load balancer distributes incoming traffic
across multiple backend servers to enable horizontal
scaling and high availability. Layer 4 LBs forward TCP
connections (fast, no content inspection). Layer 7 LBs
inspect HTTP content (path-based routing, SSL termination,
health checks on application responses). Every production
service with more than one server needs a load balancer.

| #031 | Category: Networking | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Client-Server Model, HTTP and HTTPS Basics | |
| **Used by:** | Load Balancing Algorithms | |
| **Related:** | Client-Server Model, Reverse Proxy, Load Balancing Algorithms | |

---

### 🔥 The Problem This Solves

A single server handles requests serially: add more load
than one server can handle and latency spikes or requests
fail. You need multiple servers. But a client can only
connect to one IP address. The load balancer sits in front,
accepts all connections on one IP, and distributes them
across the server pool. When a server dies, the LB stops
sending traffic there. When you add a server, the LB
starts using it immediately. Clients see a single endpoint.

---

### 📘 Textbook Definition

A **load balancer** is a device or software that distributes
network or application traffic across a pool of backend
servers. It acts as the single entry point for clients,
forwarding requests using a routing algorithm (round-robin,
least connections, IP hash, etc.) and performing health
checks to remove unhealthy backends. Load balancers operate
at different layers: **Layer 4 (L4) LB** (transport layer
- forwards TCP/UDP connections based on IP:port) and
**Layer 7 (L7) LB** (application layer - routes based on
HTTP content: URL, headers, cookies).

---

### ⏱️ Understand It in 30 Seconds

**L4 vs L7 in one diagram:**

```
┌──────────────────────────────────────────────────────────┐
│  L4 Load Balancer (TCP/UDP)                             │
│                                                          │
│  Client ──→ LB:443 ──forward TCP──→ Server 1:443       │
│                   ──forward TCP──→ Server 2:443         │
│                   ──forward TCP──→ Server 3:443         │
│  Sees: source IP, dest IP, port. Cannot see HTTP.       │
│  Decision: based on IP/port only.                       │
│                                                          │
│  L7 Load Balancer (HTTP)                                │
│                                                          │
│  Client ──→ LB:443 → TLS terminate → read HTTP         │
│    /api/*  ──→ API Server pool                          │
│    /static/* ──→ CDN or static server                  │
│    /admin/* ──→ Admin server pool (with auth check)    │
│  Sees: full HTTP request. Can route by URL, headers.   │
│  Can add/modify headers, rewrite URLs, check auth.     │
└──────────────────────────────────────────────────────────┘
```

---

### 🔩 First Principles Explanation

**What a load balancer actually does:**

```
┌──────────────────────────────────────────────────────────┐
│  Load Balancer Functions                                 │
├────────────────────┬─────────────────────────────────────┤
│  Traffic           │  Distribute requests across pool    │
│  Distribution      │  using algorithm (RR, LC, IP hash)  │
├────────────────────┼─────────────────────────────────────┤
│  Health Checking   │  Periodic probe to each backend     │
│                    │  (TCP connect, HTTP GET /health)    │
│                    │  Remove failed backends             │
│                    │  Re-add when healthy again          │
├────────────────────┼─────────────────────────────────────┤
│  SSL Termination   │  L7: LB decrypts TLS, forwards      │
│  (L7 only)         │  HTTP to backends.                  │
│                    │  Centralize cert management.        │
├────────────────────┼─────────────────────────────────────┤
│  Session Affinity  │  "Sticky sessions": route same      │
│  (L7 only)         │  client to same backend (by cookie  │
│                    │  or IP). Needed for stateful apps.  │
├────────────────────┼─────────────────────────────────────┤
│  Header Injection  │  L7: add X-Forwarded-For (real     │
│  (L7 only)         │  client IP) to forwarded request.  │
│                    │  Add X-Request-Id for tracing.     │
├────────────────────┼─────────────────────────────────────┤
│  Content Routing   │  L7: route /api/* to API servers,  │
│  (L7 only)         │  /static/* to CDN, /admin/* to     │
│                    │  restricted pool                    │
└────────────────────┴─────────────────────────────────────┘
```

**Load balancing algorithms:**

```
Round Robin: each request → next server in sequence
  1→srv1, 2→srv2, 3→srv3, 4→srv1, 5→srv2...
  Good for: homogeneous servers, short equal-duration requests
  Bad for: mixed request durations (slow requests pile up on one server)

Least Connections: each request → server with fewest active connections
  Best for: mixed request durations (long-running and short requests)
  Cost: must track connection count per server

Weighted Round Robin: servers get proportional traffic by weight
  srv1 weight=3: 3 requests, srv2 weight=1: 1 request
  Good for: heterogeneous servers (different hardware capacity)

IP Hash: hash(client_IP) % servers → sticky by IP
  Same client always → same server (no explicit cookie needed)
  Bad for: server pool changes destroy all mappings (rehashing)
  Bad for: NAT (many clients behind one IP → one overloaded server)

Random: pick random server
  Similar to round-robin in practice. Simple.
```

---

### 🧪 Thought Experiment

**SETUP: Sticky sessions vs stateless backends**

Your e-commerce app uses sticky sessions (IP hash).
User is in the middle of checkout. Their server (Server 2)
crashes. The load balancer detects failure and routes
next request to Server 3.

**Problem:**
User's session is on Server 2 (in memory). Server 3 has no
session state. User loses their cart. They're in the middle
of a payment form. Terrible UX and potentially lost revenue.

**The real fix (not just LB tuning):**
Make backends stateless. Store session state in:
- Redis (fast, shared session store)
- JWT tokens (session state encoded in token, verified
  by any server)
- Database (persistent but slower)

**THE INSIGHT:**
Sticky sessions are a workaround for stateful application
design. They introduce a single point of failure (the
specific server holding your session state). The correct
architecture is stateless backends + shared session store.
Then any server can handle any request, server failures
are transparent to users, and you can add/remove servers
freely. This is a fundamental distributed systems principle.

---

### 🧠 Mental Model / Analogy

> A load balancer is a bank teller queue manager:
>
> Customers (clients) arrive and the queue manager
> (LB) directs each to an available teller (server).
>
> If teller 3 is ill (health check fails), the manager
> stops sending customers there and redirects to others.
> When teller 3 recovers, customers start flowing again.
>
> L4 = the manager just counts people in each queue
>      and picks the shortest (least connections)
>
> L7 = the manager reads each customer's service request
>      and routes VIP customers to special tellers,
>      loan applications to the mortgage desk, etc.
>      (content-based routing)

---

### ⚙️ How It Works (Mechanism)

**nginx as L7 load balancer:**

```nginx
upstream api_servers {
    # Algorithm: least_conn (least connections)
    least_conn;

    server 10.0.1.10:8080 weight=3;   # gets 3x traffic
    server 10.0.1.11:8080 weight=1;
    server 10.0.1.12:8080 backup;     # only if others fail

    # Health check: remove server if 3 failures in 30s
    # Re-add after 1 success
}

server {
    listen 443 ssl;
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location /api/ {
        proxy_pass http://api_servers;
        # Inject real client IP
        proxy_set_header X-Forwarded-For $remote_addr;
        proxy_set_header X-Request-Id $request_id;
        proxy_connect_timeout 5s;
        proxy_read_timeout 30s;
    }

    location /static/ {
        root /var/www/static;
        expires 1y;
    }
}
```

**Wrong vs Right - missing X-Forwarded-For:**

```python
# BAD: log or rate-limit using request.remote_addr
# On load-balanced deployment, remote_addr = LB's IP
# All users appear to come from the same IP!
def handle_request():
    client_ip = request.remote_addr  # WRONG: LB's IP
    rate_limit_check(client_ip)      # Rate limits LB, not user
    log.info(f"Request from {client_ip}")  # All look same

# GOOD: use X-Forwarded-For header (set by LB)
def handle_request():
    # X-Forwarded-For may contain multiple IPs if multiple
    # proxies: "client, proxy1, proxy2"
    # Take the FIRST (leftmost) IP as the real client
    xff = request.headers.get('X-Forwarded-For', '')
    client_ip = xff.split(',')[0].strip() \
        if xff else request.remote_addr
    rate_limit_check(client_ip)   # Correct: real client IP
    log.info(f"Request from {client_ip}")
```

**Health check endpoint (mandatory for LB integration):**

```python
# Every service behind a LB MUST have a /health endpoint
from flask import Flask, jsonify
import psycopg2

app = Flask(__name__)

@app.route('/health')
def health():
    """LB health check endpoint. Returns 200 if healthy."""
    checks = {}

    # Check database connectivity
    try:
        conn = db_pool.getconn()
        conn.execute('SELECT 1')
        db_pool.putconn(conn)
        checks['database'] = 'ok'
    except Exception as e:
        checks['database'] = str(e)

    # Return 200 if all critical checks pass
    all_ok = all(v == 'ok' for v in checks.values())
    return jsonify({
        'status': 'healthy' if all_ok else 'unhealthy',
        'checks': checks
    }), 200 if all_ok else 503

# LB health check config:
# probe: GET /health every 10s
# healthy threshold: 2 consecutive 200s → add to pool
# unhealthy threshold: 3 consecutive non-200s → remove
```

---

### 🔄 The Complete Picture - End-to-End Flow

**AWS load balancer types:**

```
┌──────────────────────────────────────────────────────────┐
│  AWS Load Balancer Types                                 │
├───────────────┬──────────────────────────────────────────┤
│  ALB           │  Application LB. L7. HTTP/HTTPS/gRPC.  │
│  (Application) │  Path/header routing. WAF integration. │
│                │  Target: EC2, ECS, Lambda, IP. Use for │
│                │  web apps and microservices.            │
├───────────────┼──────────────────────────────────────────┤
│  NLB           │  Network LB. L4. TCP/UDP/TLS.          │
│  (Network)     │  Ultra-low latency (<1ms), millions    │
│                │  of rps. Static IP. Use for: real-time  │
│                │  gaming, IoT, financial trading.        │
├───────────────┼──────────────────────────────────────────┤
│  GLB           │  Gateway LB. L3/L4. For inline security │
│  (Gateway)     │  appliances (IDS/IPS/firewalls).       │
└───────────────┴──────────────────────────────────────────┘
```

**WHAT CHANGES AT SCALE:**
At 100K rps, single L7 LB becomes a bottleneck. Solutions:
multiple LBs with DNS-based load balancing (multiple A
records for same domain), or anycast routing (same IP
announced from multiple locations, BGP routes to nearest).
At 1M rps, anycast + multiple regional LBs is standard.
AWS ALB auto-scales transparently. Self-managed nginx
requires horizontal scaling of LBs themselves (LB of LBs).
At internet scale (Google, Cloudflare): L4 anycast → L7
regional → application servers (3-tier LB hierarchy).

---

### ⚖️ Comparison Table

| | L4 LB | L7 LB |
|---|---|---|
| **Operates on** | TCP/UDP (IP:port) | HTTP (URL, headers, body) |
| **SSL termination** | No (passthrough only) | Yes |
| **Content routing** | No | Yes (/api, /static, etc.) |
| **Header injection** | No | Yes (X-Forwarded-For) |
| **Session affinity** | IP-based only | Cookie or header |
| **Performance** | Faster (less processing) | Slightly slower |
| **Use case** | TCP services, raw throughput | Web apps, microservices |
| **AWS example** | NLB | ALB |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| LB guarantees equal load | Round-robin distributes requests equally but NOT equally weighted by duration. 10 short requests on Server 1 vs 1 long request on Server 2 = equal requests, unequal CPU. Use "least connections" for mixed workloads. |
| Sticky sessions are safe for HA | If the "sticky" server dies, the user's session is lost anyway. Sticky sessions are a band-aid for stateful applications, not a HA solution. Fix the app to be stateless. |
| LB removes need for timeouts | If a backend is SLOW (not FAILED), the LB keeps sending traffic to it. Requests queue up. LBs detect server DOWN via health checks, but not server SLOW. Backend request timeouts + circuit breakers are needed in addition to the LB. |

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ L4 LB        │ TCP/UDP forwarding, no content inspection │
│ L7 LB        │ HTTP: path routing, SSL termination,      │
│              │ header injection, content-based routing   │
├──────────────┼───────────────────────────────────────────┤
│ ALGORITHMS   │ Round-robin (equal duration),             │
│              │ Least-conn (mixed duration),              │
│              │ IP-hash (sticky without cookies)          │
├──────────────┼───────────────────────────────────────────┤
│ MUST DO      │ /health endpoint returning 200/503        │
│              │ Read X-Forwarded-For for real client IP   │
│              │ Stateless backends (avoid sticky sessions)│
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ Using remote_addr behind LB (gets LB IP) │
│              │ Sticky sessions instead of stateless arch │
│              │ No /health endpoint (LB can't detect down)│
└──────────────────────────────────────────────────────────┘
```

**Interview one-liner:**
"A load balancer distributes traffic across a server pool
for horizontal scaling and HA. L4 LBs forward TCP/UDP
connections by IP:port (fast, no content inspection). L7
LBs terminate TLS and route by HTTP content (URL, headers,
cookies), enabling path-based routing, header injection,
and application-level health checks. Critical operational
requirements: every backend needs a `/health` endpoint for
LB health checking, and all backends should be stateless
(shared session store) to avoid sticky session dependencies.
Read X-Forwarded-For for real client IP - `remote_addr`
behind an LB returns the LB's IP, not the client's."