---
layout: default
title: "API Gateway"
parent: "HTTP & APIs"
nav_order: 231
permalink: /http-apis/api-gateway/
number: "0231"
category: HTTP & APIs
difficulty: ★★☆
depends_on: HTTP, REST, Load Balancer, Networking
used_by: Microservices, API Management, Multi-client Apps
related: Reverse Proxy, Service Mesh, BFF, API Rate Limiting, API Authentication
tags:
  - api
  - gateway
  - microservices
  - routing
  - intermediate
---

# 231 — API Gateway

⚡ TL;DR — An API Gateway is a reverse proxy that sits between clients and backend services, acting as the single entry point for all API traffic; it centralizes cross-cutting concerns — authentication, rate limiting, routing, logging, SSL termination, and request transformation — so individual services don't each need to implement them.

| #231 | Category: HTTP & APIs | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | HTTP, REST, Load Balancer, Networking | |
| **Used by:** | Microservices, API Management, Multi-client Apps | |
| **Related:** | Reverse Proxy, Service Mesh, BFF, API Rate Limiting, API Authentication | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You have 20 microservices. Each service has its own port, URL, and SSL certificate.
Each service independently handles: JWT validation (20 implementations), rate limiting
(20 implementations), CORS headers (20 implementations), access logging (20 log
formats). Clients must know the address of each service. Adding a new service means
updating client configuration in every mobile app version ever shipped. Rotating
an auth secret means a deploy to all 20 services. Every service has slightly different
security behavior because each team implemented it themselves.

**THE INVENTION MOMENT:**
The API Gateway pattern emerged from the API economy (Apigee, AWS API Gateway, Kong).
The insight: instead of distributing infrastructure concerns (auth, rate limiting, SSL)
across every service, extract them into a single edge component. This component:
routes to the right backend, enforces policies before the request reaches the backend,
and exposes a single stable URL to all clients. The single entry point means clients
don't care about your internal topology. The centralized policy layer means you change
auth once, rate limits once, CORS once — applied everywhere.

---

### 📘 Textbook Definition

An **API Gateway** is an infrastructure component acting as the single entry point
for client API requests. It receives all incoming API traffic, applies cross-cutting
policies (authentication, authorization, rate limiting, SSL termination, request
validation, CORS), routes each request to the appropriate backend service, and returns
the backend's response to the client — potentially transforming it along the way.
An API Gateway combines the responsibilities of a reverse proxy, a request router,
and a policy enforcement point. Common implementations include: AWS API Gateway,
Kong, Nginx, Apigee, and Spring Cloud Gateway. Distinct from a Service Mesh: an
API Gateway handles north-south traffic (external clients to backends), while a
service mesh handles east-west traffic (service-to-service).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
An API Gateway is the receptionist for your entire backend — every request comes
through it, it checks credentials, enforces rules, and directs traffic to the right
place.

**One analogy:**

> Imagine a large office building with 20 departments (services). Without a reception
> desk (API Gateway): every visitor must know which floor each department is on,
> each department checks visitor badges separately (20 security checks), and there's
> no central log of who entered. With a reception desk: all visitors check in once,
> show their badge once, get a visitor pass, and are directed to the right floor.
> Central log maintained. Security standardized.

**One insight:**
An API Gateway's power comes from centralizing policy enforcement at the boundary.
Once a request passes through the gateway, backend services can trust that:

- The token was valid (auth done)
- The client hasn't exceeded rate limits (rate limiting done)
- The request came from an allowed origin (CORS done)
- The payload was valid JSON (schema validation done)
  Services become simpler because the gateway handled infrastructure concerns.

---

### 🔩 First Principles Explanation

**WHAT AN API GATEWAY ACTUALLY DOES (layer by layer):**

```
Request arrives at gateway on port 443:

┌─────────────────────────────────────────────────────┐
│ LAYER 1 — SSL/TLS Termination                       │
│   Decrypt HTTPS → HTTP internally                   │
│   Manage SSL certificates centrally (not per service)│
├─────────────────────────────────────────────────────┤
│ LAYER 2 — Authentication                            │
│   Validate JWT: check signature + expiry            │
│   Or: validate API key against key store            │
│   Reject (401) if invalid → backend never sees it  │
├─────────────────────────────────────────────────────┤
│ LAYER 3 — Authorization                             │
│   Does this token have permission for this path?   │
│   Reject (403) if unauthorized                     │
├─────────────────────────────────────────────────────┤
│ LAYER 4 — Rate Limiting                             │
│   Count requests by client/IP/API key in time window│
│   Reject (429) if limit exceeded                   │
├─────────────────────────────────────────────────────┤
│ LAYER 5 — Request Routing                           │
│   Match path/method → upstream service URL          │
│   /api/users/* → user-service:8080                 │
│   /api/orders/* → order-service:8080               │
├─────────────────────────────────────────────────────┤
│ LAYER 6 — Request Transformation (optional)        │
│   Rewrite path, inject headers, modify body        │
│   Add: X-Consumer-ID, X-Client-IP headers         │
├─────────────────────────────────────────────────────┤
│ LAYER 7 — Logging / Tracing                         │
│   Emit access log, trace ID, metrics per request   │
└─────────────────────────────────────────────────────┘
Backend service receives clean, authenticated request
```

**WHY NOT JUST USE NGINX?**
Nginx is a reverse proxy. An API Gateway is Nginx + policy plugins + management API

- developer portal (often). In practice: Kong IS Nginx with a plugin layer on top.
  "API Gateway" is the architecture term; the implementation may well be Nginx.

---

### 🧪 Thought Experiment

**SCENARIO:** Your company has 3 mobile clients (iOS, Android, Web) and 15 backend services. You're introducing API versioning.

**WITHOUT API GATEWAY:**

```
Problem 1: Where does v1 vs v2 routing live?
  → Each service must handle versioning internally
  → 15 services, each running v1 and v2 code paths
  → Deprecating v1 means 15 services to update

Problem 2: Auth token format changes (JWT → expanded claims)
  → 15 services to update their token validation logic
  → 15 deploys, risk of inconsistency during rollout

Problem 3: Blocking an abusive API key
  → Which service do you block it in? The key works on all 15 services.
```

**WITH API GATEWAY:**

```
Version routing: gateway routes /v1/* to old service versions, /v2/* to new
  → Services only know their own versions
  → v1 deprecation: change one gateway routing rule

Auth token change: gateway validates all tokens
  → 1 gateway update, 0 service updates
  → Atomic: one config change, all services protected

Block abusive key: add key to gateway's deny list
  → 1 change, blocks access to ALL 15 services instantly
```

**THE LESSON:** An API Gateway's value multiplies with the number of services.
For 1-3 services, it's overhead. For 10+ services, it's essential.

---

### 🧠 Mental Model / Analogy

> The API Gateway is the bouncer at an exclusive event with 20 rooms.
> The bouncer (gateway) checks your ID (auth), verifies you're on the list (authz),
> notes that you've tried to enter 5 rooms in 10 seconds (rate limiting), and
> directs you to the right room (routing). Each room (service) trusts that
> the bouncer already vetted you.
>
> Without a bouncer: each room has its own door policy, its own ID check, its own
> headcount. The guest (client) must know which room to go to for each activity.
> Security is inconsistent. Overworked hosts let things slip.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
An API Gateway is a single door into your entire backend. All client requests go
through it. It checks who you are, enforces rules, and sends your request to the
right service. Clients only need to know the gateway's address.

**Level 2 — How to use it (junior developer):**
Configure routes in the gateway: path pattern → upstream service. Add plugins/middleware:
JWT validation, rate limiting, CORS, access logging. Expose one domain
(api.yourcompany.com) to clients. Services run internally, not exposed directly.
Use Kong, AWS API Gateway, or Spring Cloud Gateway.

**Level 3 — How it works (mid-level engineer):**
The gateway listens on a public port. On each request: extract auth token → validate
against JWKS endpoint (cached). Check rate limiter (Redis/in-memory token bucket).
Match path/method to routing table. Proxy the request upstream (HTTP proxy with
timeout, retry config). Add upstream headers (X-Consumer-ID, X-Trace-ID). Receive
response, apply response plugins, return to client. The gateway is stateless per
request but stateful for rate limiting (Redis cluster). Circuit breaker integration
prevents cascading backend failures.

**Level 4 — Why it was designed this way (senior/staff):**
API Gateways implement the Single Responsibility Principle at the infrastructure level:
cross-cutting concerns belong at the edge, domain logic belongs in services. This
yields tangible benefits: security surface (auth is one thing to audit), performance
(JWKS caching in gateway vs each service), operability (single source of access
logs). The tradeoffs are real: gateways become SPOFs (need HA deployment), they add
latency (~1–5ms), and complex transformations in the gateway create tight coupling.
The modern evolution — service meshes (Istio, Linkerd) — handle east-west concerns
(mTLS, service-to-service auth, circuit breaking) while the API Gateway handles
north-south. The BFF (Backend for Frontend) pattern extends the gateway concept by
having a purpose-built gateway per client type (mobile BFF, web BFF), each
aggregating and transforming responses optimally for that client.

---

### ⚙️ How It Works (Mechanism)

```
Kong Gateway Architecture:

┌────────────────────────────────────────────────────────────┐
│                       Clients                              │
│              (Mobile, Web, Third-party)                    │
└──────────────────────┬─────────────────────────────────────┘
                       │ HTTPS :443
┌──────────────────────▼─────────────────────────────────────┐
│                    API GATEWAY                             │
│                                                            │
│  [Plugin Chain per Route]:                                 │
│  jwt-auth → rate-limit → cors → request-transform → proxy  │
│                                                            │
│  Route Table:                                              │
│  GET /api/v1/users/*  → user-service:8081                 │
│  POST /api/v1/orders  → order-service:8082                │
│  GET /api/v1/products → product-service:8083              │
│                                                            │
│  Shared State: Redis (rate limit counters, token cache)   │
└──────────┬──────────────┬──────────────┬───────────────────┘
           │              │              │
   user-service    order-service   product-service
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
1. Client: GET https://api.company.com/api/v1/users/42
   Authorization: Bearer eyJhbGci...

2. Gateway: SSL decrypt → extract JWT
   Validate JWT signature (JWKS cache, TTL 5min)
   Check: rate limit for this API key → Redis: 47/100 per minute, OK

3. Gateway: match route "/api/v1/users/*" → upstream: user-service:8081
   Inject headers: X-Consumer-ID: user123, X-Trace-ID: abc-def

4. Gateway: proxy to user-service:8081/api/v1/users/42
   Timeout: 5s, retry: 1 on 502/504

5. user-service responds: 200 { id: 42, name: "Alice" }
   Gateway: apply response plugins (add CORS headers)
   Return 200 to client

6. Gateway: log access record (status, latency, consumer ID)
   Emit metrics to Prometheus
```

---

### 💻 Code Example

```yaml
# Kong declarative configuration (kong.yaml)
_format_version: "3.0"

services:
  - name: user-service
    url: http://user-service:8081
    routes:
      - name: users-route
        paths:
          - /api/v1/users
        methods: [GET, POST, PUT, DELETE]
    plugins:
      - name: jwt
        config:
          claims_to_verify: [exp]
          key_claim_name: kid
      - name: rate-limiting
        config:
          minute: 100
          policy: redis
          redis_host: redis
          redis_port: 6379
      - name: cors
        config:
          origins: ["https://app.company.com"]
          methods: [GET, POST, PUT, DELETE]
          headers: [Authorization, Content-Type]
          max_age: 3600

  - name: order-service
    url: http://order-service:8082
    routes:
      - name: orders-route
        paths:
          - /api/v1/orders
```

```java
// Spring Cloud Gateway — programmatic configuration
@Configuration
public class GatewayConfig {

    @Bean
    public RouteLocator routes(RouteLocatorBuilder builder) {
        return builder.routes()
            // Route: /api/v1/users/** → user-service
            .route("user-service", r -> r
                .path("/api/v1/users/**")
                .filters(f -> f
                    .addRequestHeader("X-Gateway", "spring-cloud-gateway")
                    .retry(config -> config
                        .setRetries(1)
                        .setStatuses(HttpStatus.BAD_GATEWAY, HttpStatus.SERVICE_UNAVAILABLE))
                    .circuitBreaker(config -> config
                        .setName("user-service-cb")
                        .setFallbackUri("forward:/fallback/user")))
                .uri("lb://user-service")) // load balanced
            // Route: /api/v1/orders/** → order-service
            .route("order-service", r -> r
                .path("/api/v1/orders/**")
                .uri("lb://order-service"))
            .build();
    }
}
```

---

### ⚖️ Comparison Table

| Component                 | Layer                | Auth        | Rate Limit | Service Discovery | Best For                   |
| ------------------------- | -------------------- | ----------- | ---------- | ----------------- | -------------------------- |
| **API Gateway**           | Edge (north-south)   | Yes         | Yes        | Often             | External client → services |
| **Reverse Proxy (Nginx)** | Edge                 | No (manual) | Plugin     | No                | Static routing             |
| **Service Mesh (Istio)**  | Internal (east-west) | mTLS        | Limited    | Yes               | Service-to-service         |
| **Load Balancer**         | L4/L7                | No          | No         | Health checks     | Horizontal scaling         |

---

### ⚠️ Common Misconceptions

| Misconception                                   | Reality                                                                                                                              |
| ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| API Gateway replaces a service mesh             | They solve different problems: Gateway = north-south (clients to backends), Mesh = east-west (service-to-service). Use both together |
| API Gateway is always a single point of failure | Deploy in HA mode (multiple instances + Redis cluster for shared state); modern gateways are designed for it                         |
| The gateway should do business logic            | No — transform/route, don't process data. Business logic belongs in services                                                         |
| Add all functionality as gateway plugins        | Complex business rules in plugins create tight coupling to infrastructure; only cross-cutting concerns belong in the gateway         |

---

### 🚨 Failure Modes & Diagnosis

**Gateway Becomes the Bottleneck**

**Symptom:**
All services appear slow. Latency P99 spikes. Gateway CPU at 80%+.

**Root Cause:**
Gateway is the single process handing all traffic AND doing expensive operations
(fetching JWKS on every request, large regex route matching, memory-hungry plugins).

**Diagnostic:**

```bash
# Check gateway plugin latency contribution:
# Kong: Kong access log shows plugin latency breakdown per request
# Prometheus: kong_request_latency_ms{phase="upstream"} vs
#             kong_request_latency_ms{phase="kong"}
# HIGH "kong phase" = gateway plugin overhead is the problem

# Fix 1: Cache JWKS aggressively (TTL: 5 minutes)
# Fix 2: Scale gateway horizontally (stateless, add instances)
# Fix 3: Move expensive operations to async (fire-and-forget audit log)
```

---

### 🔗 Related Keywords

- `Reverse Proxy` — the lower-level mechanism the API Gateway builds upon
- `Rate Limiting` — a primary cross-cutting concern delegated to the API Gateway
- `BFF (Backend for Frontend)` — a specialized API Gateway per client type
- `Service Mesh` — the complementary system for east-west (service-to-service) traffic control

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Single entry point for all API traffic;  │
│              │ handles auth, rate limit, routing         │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ 20 services each implementing auth,       │
│ SOLVES       │ rate limiting, CORS independently         │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Centralize cross-cutting concerns at edge │
│              │ so services focus on domain logic         │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Multiple services behind a shared API,    │
│              │ external clients, microservices           │
├──────────────┼───────────────────────────────────────────┤
│ COMMON TOOLS │ Kong, AWS API GW, Spring Cloud GW, Nginx  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The single door into your backend"      │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ BFF → Service Mesh → Rate Limiting        │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q.** Your API Gateway handles 200,000 req/s. Every request requires JWT validation (RSA-256, ~3ms JWKS fetch). Calculate the theoretical throughput impact of JWKS caching (TTL: 5 minutes, 1 JWKS key per 200K requests in the window). Now design the cache invalidation strategy: when you rotate JWT signing keys, some tokens signed with the old key are still valid for 30 minutes. How does the gateway correctly validate tokens during key rotation?
