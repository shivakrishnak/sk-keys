---
id: SYD-056
title: API Gateway Design
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★★
depends_on: SYD-008, SYD-028
used_by: ""
related: SYD-008, SYD-028, SYD-057, SYD-060
tags:
  - architecture
  - api-gateway
  - microservices
  - design
  - advanced
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 56
permalink: /syd/api-gateway-design/
---

# SYD-056 - API Gateway Design

⚡ TL;DR - An API gateway is the single entry point
for all client requests in a microservices architecture.
It handles cross-cutting concerns: authentication, rate
limiting, SSL termination, request routing, and response
transformation - so individual microservices do not have
to. Think of it as the "front door" of your backend. Key
design questions: how to route requests (path-based,
header-based), how to handle auth (validate JWT once at
the gateway vs. forward to auth service), and how to
avoid making the gateway a bottleneck or single point
of failure.

| #056 | Category: System Design | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Caching, Rate Limiting | |
| **Related:** | Caching, Rate Limiting, Event-Driven Architecture, Circuit Breaker | |

---

### 🔥 The Problem This Solves

A mobile app calling a microservices backend hits
20 different services: auth, user profile, product,
cart, orders, notifications, etc. Without a gateway:
- The client must know the address of every service
- Every service implements auth, rate limiting, logging
  independently - inconsistently, at 10x the effort
- The client makes 20 separate requests to show one
  screen (high latency, battery drain)
- Adding a new service requires updating the client
  (all mobile versions in the field)

---

### 📘 Textbook Definition

**API gateway:** A reverse proxy that sits between
external clients and internal microservices. Handles
cross-cutting concerns: authentication, authorization,
rate limiting, SSL termination, request/response
transformation, routing, load balancing, and observability.
Clients call one endpoint; the gateway routes to the
appropriate service.

**Backend For Frontend (BFF):** A pattern where a
separate gateway instance is created per client type
(mobile BFF, web BFF, partner BFF). Each BFF aggregates
and transforms data optimally for its client's needs.
A mobile BFF returns compact JSON with only the fields
the mobile app needs; the web BFF may return richer data.

**Request aggregation:** A gateway feature where one
client request triggers multiple downstream service calls,
and the responses are merged before returning to the
client. Reduces client-to-server round trips.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
One entry point for all clients. Route, authenticate,
rate-limit, transform at the edge - before requests
reach microservices.

**One analogy:**
> A hotel concierge desk:
> Every guest request (book a room, order food, get taxi)
> goes through the concierge - not directly to housekeeping,
> the kitchen, or the garage. The concierge authenticates
> the guest (verifies room key), decides which internal
> department handles the request, and returns the result.
> The guest never knows how many internal teams were involved.

**One insight:**
The gateway is a horizontal concern: every microservice
needs auth, rate limiting, and logging. Centralizing them
in the gateway means:
- Implement once, not N times (DRY)
- One place to update auth logic when JWT algorithm changes
- One place to enforce rate limits (consistent across services)
- Microservices become simpler (no security boilerplate)
But: the gateway is now a bottleneck and single point
of failure. It MUST be highly available (multiple instances,
circuit breakers on downstream service calls).

---

### 🔩 First Principles Explanation

**GATEWAY RESPONSIBILITIES:**
```
1. SSL Termination:
   Client → HTTPS → Gateway → HTTP → Internal Services
   Internal traffic can be unencrypted (private network).
   Offloads TLS from individual services.

2. Authentication:
   Validate JWT signature at the gateway.
   If valid: forward request with user context header.
   If invalid: return 401. Services trust the gateway.
   
   Alternative: forward token to Auth Service for validation.
   Pro: centralized auth logic. Con: extra hop per request.

3. Authorization:
   Coarse-grained: is this user allowed to call /admin/*?
   Fine-grained authorization stays in the service.
   
4. Rate Limiting:
   Per API key, per user, per IP.
   Counters stored in Redis (shared across gateway instances).
   Return 429 Too Many Requests when limit exceeded.

5. Request Routing:
   /api/v1/users/* → User Service
   /api/v1/products/* → Product Service
   Path-based: most common.
   Header-based: route by X-API-Version for A/B testing.
   
6. Load Balancing:
   Multiple instances of Product Service: round-robin.
   Health checks: remove unhealthy instances.
   
7. Request Transformation:
   Rewrite paths: /api/v1/items → /items (legacy service)
   Add headers: X-User-Id, X-Request-Id, X-Trace-Id
   Remove internal headers before returning to client.
   
8. Response Aggregation:
   GET /api/v1/dashboard:
     Calls User Service + Product Service + Order Service
     Merges responses into one JSON
     Returns one response to client
```

**ROUTING CONFIGURATION:**
```yaml
# Kong / NGINX style routing config
routes:
  - path: /api/v1/users
    strip_prefix: true
    upstream: user-service:8080
    plugins:
      - name: jwt-auth
      - name: rate-limit
        config:
          per_user: 1000/minute

  - path: /api/v1/products
    upstream: product-service:8080
    plugins:
      - name: jwt-auth
      - name: cache
        config:
          ttl: 60  # seconds

  - path: /health
    upstream: health-aggregator:8080
    plugins: []  # no auth on health endpoint
```

**CIRCUIT BREAKER AT GATEWAY:**
```
Without circuit breaker:
  Product Service is down.
  Every request to /api/v1/products takes 30s to timeout.
  Gateway threads pile up waiting for the timeout.
  Gateway itself becomes unresponsive.
  All services are now unreachable (not just Product).

With circuit breaker:
  Product Service is down.
  Gateway detects: 10+ failures in 30 seconds.
  Circuit opens: immediately return 503 for Product calls.
  No threads blocked waiting.
  Other services (User, Order) continue working.
  After 60 seconds: try one request to Product Service.
  If success: circuit closes. Normal operation resumes.
```

---

### 🧪 Thought Experiment

**SIZING: 500K requests/second through one gateway**

500K req/sec through a single gateway node:
CPU: ~$1M$ req/sec on modern hardware for simple routing.
Memory: JWT validation = ~$5\mu s$/request. SSL $\approx$ $1ms$ (but re-use sessions).
Network: 500K req × 10KB average = 5GB/sec throughput.
Single node: 10Gbps NIC = saturates at ~1M req/sec.
For 500K req/sec with headroom: 2-3 gateway nodes, load
balanced by a hardware LB or DNS round-robin.

**Bottleneck: Downstream service outage**
Without circuit breaker: gateway connections exhaust.
With circuit breaker: gateway isolates the failure.
The circuit breaker is the most important resilience
feature in a gateway under real production load.

**JWT vs Auth Service:**
JWT at gateway: 0 extra network hops. ~$1\mu s$ CPU per
request (HMAC-SHA256 verify). Can be done at 500K req/sec.
Auth service: 1 extra network hop per request.
At 500K req/sec: Auth service needs to handle 500K/sec
- this is a significant separate system to maintain.
Recommendation: JWT validation at gateway for performance;
only call Auth service for complex authorization decisions.

---

### 🧠 Mental Model / Analogy

> An API gateway is like airport security:
>
> Every passenger (request) goes through security before
> boarding (reaching the service). Security handles:
> - Identity check (authentication): is this a valid ticket holder?
> - Screening (authorization): does this person have access to First Class?
> - Routing: Gate A1 (microservice A), Gate B7 (microservice B)
> - Flow control: only N passengers through per minute (rate limiting)
>
> The plane crew (microservices) do not need to check
> tickets or screen passengers - security handles it.
>
> If the security line breaks down (gateway outage):
> nobody can board any plane. This is why the gateway
> must be highly available - it is the single point of
> failure for all traffic.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
An API gateway is the front door to your backend services.
Clients only talk to the gateway; the gateway figures out
which service to forward the request to, checks that the
user is logged in, and prevents abuse.

**Level 2 - How to use it (junior developer):**
Configure routes: "requests to /api/users go to
user-service:8080". Configure plugins: JWT auth, rate
limiting, logging. Run gateway behind a load balancer.
Popular gateways: Kong, NGINX, AWS API Gateway, Traefik.

**Level 3 - How it works (mid-level engineer):**
Request arrives → TLS termination → JWT validation
(verify signature, check expiry) → rate limit check
(Redis counter per user/IP) → route matching → forward
to upstream → add context headers (X-User-Id) → upstream
responds → strip internal headers → return to client.
Circuit breaker tracks upstream failure rate; opens if
failure rate exceeds threshold.

**Level 4 - Why it was designed this way (senior/staff):**
The gateway pattern exists because cross-cutting concerns
(auth, rate limiting, observability) duplicate across N
services if not centralized. The trade-off: the gateway
becomes a critical dependency. To mitigate: run multiple
gateway instances (horizontal scale), use circuit breakers
for all upstream services, set aggressive timeouts (reject
slow upstreams to prevent thread exhaustion). JWT validation
at the gateway is preferred over forwarding to an auth
service because it eliminates a network hop on every
request (at 500K req/sec, one extra hop = 500K extra
requests to the auth service). The BFF pattern extends
this: different clients have different data needs; a single
gateway trying to serve mobile and web can become complex.
BFFs give each client a tailored, simpler gateway.

**Level 5 - Mastery (distinguished engineer):**
Netflix's Zuul gateway processes billions of requests
daily. Key insights from their architecture: (1) Filters
are the primary abstraction - pre-routing filters (auth,
rate limit), routing filters (upstream selection), post-routing
filters (response transform, logging). New behaviors are
added as filters, not code changes to the core. (2) Zuul 2
is asynchronous (non-blocking I/O) - handles 10x more
concurrent connections on the same hardware vs. Zuul 1
(synchronous/thread-per-request). (3) The gateway is also
the canary deployment controller: route 1% of traffic to
the new version of a service; monitor error rates; promote
if healthy. This makes the gateway a deployment orchestration
tool, not just a proxy.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ API GATEWAY REQUEST FLOW                            │
│                                                      │
│ Client                                              │
│  │ HTTPS POST /api/v1/orders                       │
│  ▼                                                  │
│ Load Balancer (HAProxy/NLB)                        │
│  │ (distributes to gateway instances)              │
│  ▼                                                  │
│ API Gateway Instance                               │
│  │ 1. TLS termination                              │
│  │ 2. Extract JWT from Authorization header        │
│  │ 3. Verify JWT signature + expiry               │
│  │    Invalid → 401                               │
│  │ 4. Rate limit check (Redis INCR per user)      │
│  │    Over limit → 429                            │
│  │ 5. Route match: /api/v1/orders →               │
│  │    order-service:8080                          │
│  │ 6. Forward: POST /orders                       │
│  │    Headers: X-User-Id, X-Request-Id, X-Trace   │
│  │ 7. Circuit breaker: healthy? → proceed         │
│  │    Open → 503 immediately                      │
│  ▼                                                  │
│ Order Service                                      │
│  │ Trusts X-User-Id header (set by gateway)       │
│  │ Processes order logic                          │
│  │ Returns 201 Created                            │
│  ▼                                                  │
│ API Gateway                                        │
│  │ Strip internal headers                         │
│  │ Add CORS headers                               │
│  │ Return 201 to client                           │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Lightweight gateway in Python (FastAPI)**
```python
from fastapi import FastAPI, HTTPException, Request, Response
import httpx
import redis
import time
import jwt as pyjwt

app = FastAPI()
r = redis.Redis()
SECRET_KEY = "your-secret-key"

ROUTES = {
    "/users": "http://user-service:8080",
    "/products": "http://product-service:8080",
    "/orders": "http://order-service:8080",
}

RATE_LIMIT = 100  # requests per minute

def validate_jwt(token: str) -> dict:
    try:
        payload = pyjwt.decode(
            token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except pyjwt.ExpiredSignatureError:
        raise HTTPException(status_code=401,
                             detail="Token expired")
    except pyjwt.InvalidTokenError:
        raise HTTPException(status_code=401,
                             detail="Invalid token")

def check_rate_limit(user_id: str) -> bool:
    key = f"rate:{user_id}:{int(time.time() // 60)}"
    count = r.incr(key)
    r.expire(key, 120)  # TTL = 2 min (current + prev minute)
    return count <= RATE_LIMIT

@app.api_route(
    "/{full_path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
)
async def gateway(full_path: str, request: Request):
    # 1. Authentication
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401,
                             detail="Missing token")
    token = auth_header.split(" ", 1)[1]
    user = validate_jwt(token)
    user_id = str(user["sub"])

    # 2. Rate limiting
    if not check_rate_limit(user_id):
        raise HTTPException(status_code=429,
                             detail="Rate limit exceeded")

    # 3. Route matching
    service_url = None
    for prefix, upstream in ROUTES.items():
        if f"/{full_path}".startswith(prefix):
            service_url = upstream + "/" + full_path
            break
    if not service_url:
        raise HTTPException(status_code=404,
                             detail="No route found")

    # 4. Forward request with user context
    headers = dict(request.headers)
    headers["X-User-Id"] = user_id
    headers.pop("Authorization", None)  # Strip auth header

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.request(
                method=request.method,
                url=service_url,
                headers=headers,
                content=await request.body(),
            )
        except httpx.TimeoutException:
            raise HTTPException(status_code=504,
                                 detail="Upstream timeout")
        except httpx.ConnectError:
            raise HTTPException(status_code=503,
                                 detail="Service unavailable")

    # 5. Return response (strip internal headers)
    response_headers = {
        k: v for k, v in resp.headers.items()
        if k.lower() not in ("x-internal", "x-trace")
    }
    return Response(
        content=resp.content,
        status_code=resp.status_code,
        headers=response_headers,
    )
```

**Example 2 - No gateway (BAD pattern)**
```python
# BAD: Each microservice implements auth independently
# - Inconsistent JWT validation logic across services
# - Product service handles auth differently to User service
# - Rate limiting not enforced globally
# - Client must know addresses of all services

# product_service.py
@app.get("/products/{id}")
def get_product(id: int, token: str = Header()):
    # Duplicated auth logic
    user = validate_jwt_v1(token)  # Old JWT library
    # ... business logic

# user_service.py
@app.get("/users/{id}")
def get_user(id: int, authorization: str = Header()):
    # Different auth implementation
    user = validate_jwt_v2(authorization)  # New JWT library
    # ... business logic

# Result: auth bugs affect some services but not others.
# Rotating JWT keys requires updating every service.

# GOOD: Single gateway validates JWT once.
# Services trust the X-User-Id header set by the gateway.
# Rotating JWT keys: update in one place (the gateway).
```

---

### ⚖️ Comparison Table

| Pattern | Auth | Rate Limit | Routing | Complexity | Best For |
|---|---|---|---|---|---|
| **No gateway (direct)** | Per-service | Per-service | Client-side | Low (initially) | Single-service or prototype |
| **Reverse proxy (NGINX)** | None | Basic | Path-based | Low | Simple proxying |
| **API Gateway** | Centralized | Centralized | Rich (path, header) | Medium | Microservices |
| **BFF (per client)** | Centralized | Centralized | Client-optimized | High | Different client needs |
| **Service Mesh (Istio)** | mTLS | Per-service | Service-to-service | Very High | Large microservice fleets |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| The gateway handles all authorization | The gateway handles coarse-grained authorization (is this user allowed to access this API at all?). Fine-grained authorization (can this user edit THIS specific record?) belongs in the service, which has the business context (e.g., is this user the owner of the resource?). Putting fine-grained logic in the gateway creates tight coupling between gateway and business rules. |
| Add all microservice logic to the gateway | The gateway should only handle cross-cutting concerns (auth, rate limiting, routing). Business logic belongs in services. A gateway that aggregates data from 10 services for every request becomes a "God Gateway" - a centralized bottleneck that defeats the purpose of microservices. Use the BFF pattern for aggregation, and keep it thin. |
| The gateway eliminates the need for service-to-service auth | External traffic goes through the gateway (auth enforced). Internal traffic between services does NOT go through the gateway. Internal calls can be spoofed (a compromised service impersonates another). Service mesh (mutual TLS) or an internal auth token solves this. Never assume internal network traffic is trusted. |

---

### 🚨 Failure Modes & Diagnosis

**Gateway Becomes a Bottleneck**

**Symptom:**
P99 latency for all APIs increases simultaneously.
CPU on gateway instances is high. Downstream services
are healthy and fast. New service deployments take
minutes to propagate (gateway config reload causes
brief traffic drops).

**Root Cause:**
Too much logic in the gateway (heavy response
transformation, calling auth service per request,
aggregating data from many services). Single gateway
processes all traffic; it becomes the throughput ceiling.

**Fix - Lightweight gateway + async offloading:**
```python
# BAD: Synchronous auth service call per request
# Adds 10ms per request = 100 extra calls per second
async def authenticate(token: str) -> dict:
    resp = await auth_service.post("/validate",
                                    json={"token": token})
    return resp.json()

# GOOD: JWT validation at the gateway (no network hop)
import jwt as pyjwt

def authenticate(token: str) -> dict:
    # Local cryptographic verification: ~0.001ms
    # No network call, no extra service to scale
    return pyjwt.decode(token, PUBLIC_KEY,
                         algorithms=["RS256"])

# For heavy response transformation:
# Offload to a BFF layer (separate service),
# not the main gateway.
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Caching` - gateway-level response caching for
  read-heavy endpoints (product catalog, public data)
- `Rate Limiting (System)` - gateway is the primary
  enforcement point for rate limits

**Builds On This (learn these next):**
- `Event-Driven Architecture` - gateway publishes
  access logs to Kafka for real-time analytics
- `Circuit Breaker (System)` - gateway uses circuit
  breakers to isolate failed downstream services

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ RESPONSIBILITIES│ TLS termination, JWT auth, rate limit, │
│                │ routing, load balance, response transform│
├────────────────┼─────────────────────────────────────────│
│ AUTH           │ JWT validation at gateway (no hop).     │
│                │ Add X-User-Id to forwarded request.     │
├────────────────┼─────────────────────────────────────────│
│ RATE LIMIT     │ Redis INCR per user/IP per minute.      │
│                │ Shared across gateway instances.        │
├────────────────┼─────────────────────────────────────────│
│ CIRCUIT BREAKER│ Track failures per upstream.            │
│                │ Open: return 503 immediately.           │
├────────────────┼─────────────────────────────────────────│
│ BFF PATTERN    │ Separate gateway per client type.       │
│                │ Mobile gets compact JSON; web gets full.│
├────────────────┼─────────────────────────────────────────│
│ FAILURE MODE   │ Heavy gateway → bottleneck.             │
│                │ Fix: JWT at gateway, not auth service.  │
├────────────────┼─────────────────────────────────────────│
│ ONE-LINER      │ "Single entry point: auth, rate limit, │
│                │  route, transform before services"     │
├────────────────┼─────────────────────────────────────────│
│ NEXT           │ Event-Driven Architecture → CQRS        │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. The gateway centralizes cross-cutting concerns: auth,
   rate limiting, routing, SSL termination. Services
   become simpler - they trust the X-User-Id header set
   by the gateway and implement only business logic.
2. Validate JWT at the gateway using local cryptographic
   verification - no network hop to an auth service.
   This is O(1) CPU work vs. O(network latency) for
   external auth service calls on every request.
3. Add circuit breakers for every downstream service.
   Without them, a slow/failed service causes gateway
   threads to pile up waiting for timeouts, making
   the gateway unresponsive for ALL services.

**Interview one-liner:**
"API gateway: single entry point for all client traffic. Handles TLS termination,
JWT validation (local, no auth service hop), rate limiting (Redis INCR per user
per minute, shared across instances), path-based routing to upstreams, circuit
breaker per upstream (open on 10+ failures in 30s → immediate 503). Microservices
trust X-User-Id header set by gateway. BFF pattern: separate gateway per client
type (mobile/web). Avoid heavy logic (response aggregation) in the gateway - that
creates a bottleneck and a 'God Gateway'."
