---
id: MSV-012
title: API Gateway
category: Microservices
tier: tier-5-distributed-architecture
folder: MSV-microservices
difficulty: ★★☆
depends_on: MSV-010, MSV-007, MSV-015
used_by: MSV-013, MSV-019, MSV-077
related: MSV-013, MSV-015, MSV-016, MSV-019, MSV-040
tags:
  - microservices
  - api
  - intermediate
  - patterns
status: complete
version: 4
layout: default
parent: "Microservices"
grand_parent: "Technical Mastery"
nav_order: 12
permalink: /technical-mastery/microservices/api-gateway/
---

⚡ TL;DR - An API Gateway is the single entry point for all
external client requests to a microservices system. It
handles cross-cutting concerns - routing, auth, rate
limiting, SSL termination - centrally rather than in
every service.

| #012 | Category: Microservices | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Inter-Service Communication, Service Discovery, Rate Limiting | |
| **Used by:** | Backend for Frontend (BFF), API Composition Pattern, Microservices Security Patterns | |
| **Related:** | Backend for Frontend, Rate Limiting, Timeout Strategy, API Composition Pattern, Service Mesh | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You have 20 microservices. Each is directly exposed to
external clients. Each client must know the URL of every
service it uses. Mobile app calls User Service, then Order
Service, then Product Service - three separate connections,
three separate auth checks, three separate rate limits (or
none). A new requirement: add logging to all external
calls. You add it to all 20 services. Another requirement:
JWT validation. You add it to 20 services, with 20 separate
implementations that drift over time.

**THE BREAKING POINT:**
Cross-cutting concerns (auth, logging, rate limiting, SSL,
CORS, tracing) cannot be maintained consistently across
20 independent services. Clients cannot be shielded from
the internal service topology. A refactor that splits
Order Service into Order and Fulfilment breaks all mobile
clients that call Order Service directly.

**THE INVENTION MOMENT:**
This is why the API Gateway was designed: a reverse proxy
that sits in front of all services, handles all external
traffic, and applies cross-cutting concerns centrally.
Internal service topology becomes invisible to external
clients.

**EVOLUTION:**
Traditional reverse proxies (Nginx, Apache httpd). AWS API
Gateway (2015) - fully managed, REST/WebSocket. Netflix
Zuul (2013) - JVM-based, programmatic routing. Spring
Cloud Gateway (2017) - reactive, Spring ecosystem.
Kong (2015) - plugin-based, Lua extensions. Istio gateway
(2017) - service mesh ingress, mTLS. AWS App Mesh, GCP
Cloud Endpoints - cloud-native gateways.

---

### 📘 Textbook Definition

An **API Gateway** is a server that acts as the single
entry point for client requests to a microservices system.
It sits between external clients and internal services,
and is responsible for request routing (forwarding to the
appropriate downstream service), cross-cutting concerns
(authentication, rate limiting, logging, SSL termination,
CORS), and optionally API composition (aggregating
responses from multiple services into one response).

The API Gateway implements the **Facade pattern** at
the system level: it presents a unified, stable API
surface to external clients while the internal service
topology can evolve freely.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
The API Gateway is your system's front door - one address
for clients, routing to the right internal service with
all cross-cutting concerns handled centrally.

**One analogy:**
> An API Gateway is like the reception desk at a large
> office building. Visitors (clients) all enter through one
> door (gateway URL). Reception checks credentials (auth),
> logs arrivals (access logging), and directs visitors
> to the right floor and person (routing). The visitor
> doesn't know how the building is internally organised -
> they just go to reception.

**One insight:**
The gateway is a seam between "external world" and "internal
system". Changes to internal service topology (splitting,
merging, renaming services) can be absorbed by the gateway
config without breaking external clients.

---

### 🔩 First Principles Explanation

**CORE CONCERNS THE GATEWAY OWNS:**

```
ROUTING:          /api/orders/* → Order Service
                  /api/users/*  → User Service
                  /api/products/* → Product Service

AUTH/AUTHZ:       Validate JWT, extract user context
                  Pass user claims as headers downstream
                  Services don't need auth logic

RATE LIMITING:    100 req/min per API key
                  Applied once at gateway, not per service

SSL TERMINATION:  HTTPS at gateway → HTTP internally
                  Services don't manage TLS certificates

LOGGING/TRACING:  Assign correlation ID at gateway
                  Log all requests (method, path, status)

CORS:             Handle preflight requests centrally
                  Services don't need CORS headers

CIRCUIT BREAKING: Gateway can open circuit for a service
                  Return fallback response to caller
```

**THE SINGLE POINT OF FAILURE RISK:**
The gateway is critical infrastructure. All external traffic
flows through it. Gateway downtime = system-wide outage.
Mitigation: multiple gateway instances behind a load
balancer, active-active, with health checks.

**THE PERFORMANCE TRADE-OFF:**
Every request adds one network hop (client → gateway →
service). For high-throughput, low-latency APIs, this
adds 1-5ms. At 10,000 requests/second, the gateway must
handle 10,000 connections/second. Reactive gateways
(Spring Cloud Gateway, Envoy) handle this with async
non-blocking I/O.

---

### 🧪 Thought Experiment

**SCENARIO: Mobile app migration**
Your mobile app calls 5 services directly:
GET /users/123, GET /orders?userId=123,
GET /products/{orderId}, GET /shipping/{orderId},
GET /loyalty/points/123

Each call requires auth, resulting in 5 JWT validations
per page load.

**WITH API GATEWAY:**
Gateway: single auth check at entry. Downstream services
receive user context as trusted headers (no JWT validation
needed per service).

**WITH BFF (Backend for Frontend) PATTERN AT GATEWAY:**
New endpoint: GET /api/mobile/dashboard/{userId}
Gateway (or BFF) fans out to all 5 services, aggregates
the response. Mobile app: 1 request, 1 auth check,
1 round trip.

**THE INSIGHT:**
The gateway is not just a router - it can be the composition
point that reduces mobile network round trips from 5 to 1.
This matters critically on mobile networks (high latency,
limited connections).

---

### 🧠 Mental Model / Analogy

> Think of the API Gateway as an airport customs and
> immigration checkpoint:
> - All incoming traffic must pass through it (no bypass)
> - Identity is verified (auth)
> - Capacity is managed (rate limiting = passenger quotas)
> - You are directed to the right terminal (routing)
> - The airport layout (internal services) is opaque
>   to passengers - they just go where directed

Where this analogy breaks down: customs is sequential
and adds significant delay. A well-designed gateway
adds only 1-5ms latency for cross-cutting concerns -
far less than customs (which can take hours).

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
The API Gateway is the single URL clients call. It
checks authentication, controls traffic rate, and
forwards requests to the right internal service. Clients
don't know or care how many services exist internally.

**Level 2 - How to use it (junior developer):**
Spring Cloud Gateway: configure routes in YAML.
`spring.cloud.gateway.routes[0].id=order-service`
`spring.cloud.gateway.routes[0].uri=lb://ORDER-SERVICE`
`spring.cloud.gateway.routes[0].predicates[0]=Path=/api/orders/**`
Add `TokenRelayGatewayFilter` for JWT forwarding. Add
`RequestRateLimiterGatewayFilter` for rate limiting.

**Level 3 - How it works (mid-level engineer):**
Spring Cloud Gateway is reactive (WebFlux). Requests
arrive on Netty's event loop. The route predicate is
evaluated (path matching). Filters are applied in order
(pre-filters: auth, rate limit; post-filters: response
headers). The request is forwarded to the backend via
a `WebClient` (reactive HTTP client). The response is
streamed back. No threads are blocked - all I/O is event-
driven. This allows handling of 50,000+ concurrent
connections on a single gateway instance.

**Level 4 - Why it was designed this way (senior/staff):**
The gateway pattern emerged from the Netflix microservices
architecture (Zuul) because cross-cutting concerns in
100+ services created inconsistency and operational overhead.
The gateway solves the "once, not everywhere" principle
for concerns that apply to all services. The reactive
design was chosen for performance: a blocking gateway
would need 1 thread per connection (like a traditional
servlet container), limiting to ~2000 connections per
instance. Reactive allows 100,000 connections with
much fewer threads.

**Level 5 - Mastery (distinguished engineer):**
Staff engineers understand the gateway as a policy
enforcement point and the boundary between trust zones.
Inside the gateway (the "east-west" traffic between
services), different security assumptions apply: services
can trust user headers passed by the gateway. Outside
(north-south), all claims are untrusted. The gateway
is where zero-trust security stops being zero-trust and
becomes role-trusted: after JWT validation, downstream
services receive `X-User-Id` and `X-User-Roles` headers
from the gateway - they trust the gateway, not the
original caller. This is the "security boundary" role
of the gateway.

---

### ⚙️ How It Works (Mechanism)

**SPRING CLOUD GATEWAY REQUEST FLOW:**

```
External Client → HTTPS → API Gateway (Netty)
  │
  ▼
Route Matching:
  /api/orders/** → matches ORDER-SERVICE route
  │
  ▼
Pre-filter chain (in order):
  1. RequestRateLimiterFilter (check token bucket)
  2. AuthFilter (validate JWT, extract claims)
  3. AddRequestHeaderFilter (X-User-Id: 12345)
  4. CircuitBreakerFilter (check state)
  │
  ▼
Forward to downstream:
  WebClient.get()
    .uri("lb://ORDER-SERVICE/orders/456")
    .header("X-User-Id", "12345")
    .retrieve()
  │
  ▼
Post-filter chain:
  5. ResponseHeaderFilter (add CORS headers)
  6. LoggingFilter (log response status, latency)
  │
  ▼
Return response to client
```

**YAML ROUTE CONFIGURATION:**

```yaml
spring:
  cloud:
    gateway:
      routes:
        - id: order-service
          uri: lb://ORDER-SERVICE  # Eureka service name
          predicates:
            - Path=/api/orders/**
          filters:
            - StripPrefix=1  # /api/orders → /orders
            - name: CircuitBreaker
              args:
                name: orderCircuitBreaker
                fallbackUri: forward:/fallback/orders
            - name: RequestRateLimiter
              args:
                redis-rate-limiter.replenishRate: 100
                redis-rate-limiter.burstCapacity: 200
                key-resolver: "#{@userKeyResolver}"
```

---

### 🔄 The Complete Picture - End-to-End Flow

**AUTHENTICATED REQUEST FLOW:**

```
Mobile App → POST https://api.example.com/api/orders
  │
  ▼
API Gateway (TLS termination, HTTPS → HTTP internally)
  │ Check: Authorization: Bearer <JWT>
  │ Validate JWT signature, expiry
  │ Extract: userId=12345, roles=[USER, PREMIUM]
  │ Check rate limit: 100 req/min for userId 12345
  │ Add headers: X-User-Id: 12345, X-Roles: USER,PREMIUM
  ▼
Order Service (HTTP, internal network)
  │ Reads X-User-Id: 12345 (trusts gateway)
  │ Does NOT validate JWT (gateway already did)
  │ Creates order for userId 12345
  ▼
201 Created {orderId: "ORD-789"}
  │
  ▼
API Gateway (post-filter)
  │ Adds: X-Correlation-Id: abc-123
  │ Logs: POST /api/orders → 201 in 234ms
  ▼
Mobile App receives response
```

**FAILURE PATH:**
```
Order Service returns 503:
  → CircuitBreaker at gateway opens after 5 failures
  → Subsequent requests: return 503 immediately (no
    forwarding)
  → After timeout: half-open, try 1 request
  → If succeeds: circuit closes, normal routing resumes
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: auth in every service**

```java
// BAD: JWT validation duplicated in every service
// 20 services = 20 implementations, inconsistencies
@RestController
public class OrderController {

    @GetMapping("/orders")
    public List<Order> getOrders(
        @RequestHeader("Authorization") String authHeader) {
        // Each service validates JWT independently
        // Token secret must be shared to all services
        // Any vulnerability affects all 20 services
        String token = authHeader.replace("Bearer ", "");
        Claims claims = jwtParser.parse(token);
        String userId = claims.getSubject();
        return orderService.getByUser(userId);
    }
}
```

```java
// GOOD: auth at gateway only, trust headers downstream
// Gateway validates JWT, passes userId as trusted header
@RestController
public class OrderController {

    @GetMapping("/orders")
    public List<Order> getOrders(
        // Trust header set by gateway after JWT validation
        @RequestHeader("X-User-Id") String userId,
        @RequestHeader("X-Roles") String roles) {
        // Service logic: no JWT parsing needed
        // JWT secret not needed in this service
        return orderService.getByUser(userId);
    }
}
// Gateway AuthFilter (single implementation):
// 1. Parse and validate JWT
// 2. Add X-User-Id header to forwarded request
// 3. Remove Authorization header (optional, defense in depth)
```

**Example 2 - Custom gateway filter for correlation ID**

```java
@Component
public class CorrelationIdFilter
    implements GlobalFilter, Ordered {

    private static final String HEADER = "X-Correlation-Id";

    @Override
    public Mono<Void> filter(ServerWebExchange exchange,
                             GatewayFilterChain chain) {
        String correlationId = exchange.getRequest()
            .getHeaders().getFirst(HEADER);
        if (correlationId == null) {
            correlationId = UUID.randomUUID().toString();
        }

        String finalId = correlationId;
        return chain.filter(exchange.mutate()
            .request(r -> r.header(HEADER, finalId))
            .response(r -> r.headers(
                h -> h.add(HEADER, finalId)))
            .build());
    }

    @Override
    public int getOrder() {
        return -1;  // Run first
    }
}
```

---

### ⚖️ Comparison Table

| Gateway | Type | Performance | Features | Best For |
|---|---|---|---|---|
| **Spring Cloud Gateway** | JVM, reactive | High (WebFlux) | Spring ecosystem, extensible | Spring Boot microservices |
| Kong | Nginx-based, Lua | Very high | Rich plugin ecosystem | Language-agnostic, enterprise |
| AWS API Gateway | Managed | High | AWS-native, serverless | AWS deployments |
| Nginx | Reverse proxy | Highest | Manual config, less features | High-performance, simple routing |
| Istio Gateway | Envoy-based | High | Service mesh integration | Kubernetes + service mesh |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| API Gateway is the same as a load balancer | Load balancer distributes traffic to instances of the SAME service. API Gateway routes to DIFFERENT services based on path. They are different concerns (though modern gateways often include LB). |
| Gateway eliminates the need for service-level auth | The gateway handles external-to-internal trust. Service-to-service (east-west) trust still requires mTLS or service mesh. |
| One gateway for all clients is optimal | Large systems often use BFF: separate gateway instances optimised for mobile, web, and partner APIs. Reduces coupling between client type and backend API shape. |

---

### 🚨 Failure Modes & Diagnosis

**Gateway becomes a bottleneck under load**

**Symptom:**
P99 latency increases from 50ms to 800ms under peak load.
CPU on gateway instances is at 95%.

**Root Cause:**
Blocking I/O (Spring MVC, Zuul 1.x) rather than reactive
I/O. Under 10,000 concurrent requests, all 200 Tomcat
threads are occupied. New requests queue in the accept
queue, adding latency.

**Diagnostic Command:**
```bash
# Check thread pool utilisation
curl http://gateway:8080/actuator/metrics/\
  tomcat.threads.busy
curl http://gateway:8080/actuator/metrics/\
  tomcat.threads.config.max

# Thread dump to see blocked threads
curl http://gateway:8080/actuator/threaddump \
  | grep -c "BLOCKED"
```

**Fix:**
Migrate to Spring Cloud Gateway (WebFlux/Reactor). Check
for blocking code in custom filters - DB calls in filters
require reactive DB clients, not JPA.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Inter-Service Communication` - gateway handles external
  → internal communication entry point
- `Service Discovery` - gateway uses service discovery
  to route to backend services

**Builds On This (learn these next):**
- `Backend for Frontend (BFF)` - specialised gateway for
  different client types
- `API Composition Pattern` - gateway-level response
  aggregation from multiple services

**Alternatives / Comparisons:**
- `Service Mesh` - handles east-west traffic; gateway handles
  north-south (external-to-internal)
- `Load Balancer` - distributes to instances of one service;
  gateway routes to different services by domain

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Single entry point for external traffic  │
│              │ Handles cross-cutting concerns centrally │
├──────────────┼──────────────────────────────────────────┤
│ OWNS         │ Auth, rate limiting, routing, SSL,       │
│              │ CORS, logging, circuit breaking          │
├──────────────┼──────────────────────────────────────────┤
│ DOES NOT OWN │ Business logic, data access,             │
│              │ East-west service auth                   │
├──────────────┼──────────────────────────────────────────┤
│ SPF RISK     │ Gateway is critical infra - must be HA   │
│              │ (active-active, multiple instances)      │
├──────────────┼──────────────────────────────────────────┤
│ PERF         │ Use reactive (WebFlux/Netty), not blockin│
│              │ Reactive: 50,000+ connections/instance   │
├──────────────┼──────────────────────────────────────────┤
│ SECURITY     │ Gateway = trust boundary. Downstream     │
│              │ services trust headers set by gateway    │
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "Front door: one URL in, right service   │
│              │  out, auth/rate-limit/log once"          │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Backend for Frontend → API Composition   │
│              │ → Rate Limiting → Service Mesh           │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Auth once at the gateway, not in every service. Pass
   userId as a trusted header downstream.
2. Use reactive (WebFlux) not blocking (servlet) - a blocking
   gateway becomes the bottleneck under any real load.
3. Gateway is a single point of failure - run 3+ instances
   active-active behind a network load balancer.

**Interview one-liner:**
"An API Gateway is the single entry point for external
clients. It handles cross-cutting concerns (auth, rate
limiting, SSL, logging) centrally so individual services
don't need to. It routes requests to the correct downstream
service and shields clients from internal service topology.
Critical concern: it is a SPOF - must be highly available.
Security concern: it is the trust boundary between external
callers and internal services."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Cross-cutting concerns belong at the edge, not the core.
Authentication, rate limiting, and logging are infrastructure
concerns, not business concerns. Moving them to the gateway
keeps service code focused on business logic and avoids
20 inconsistent implementations drifting over time.

**Where else this pattern appears:**
- Operating systems: system call interface = the "gateway"
  between user space and kernel space - a trust boundary
- Corporate network perimeter: firewall/proxy as the single
  entry point for all external traffic

---

### 💡 The Surprising Truth

A common mistake is adding business logic to the API
Gateway. Teams start with routing and auth (correct), then
add data transformation, then service orchestration. The
gateway becomes an orchestration engine with business rules
and downstream dependencies. The original benefit (stable,
simple routing layer) is gone. Rule: the gateway handles
infrastructure concerns; business orchestration belongs in
an orchestration service or the BFF layer.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **DESIGN** Configure a Spring Cloud Gateway that routes
   to 5 services by path, validates JWT, and passes userId.
2. **DEBUG** Given increasing P99 latency under load,
   identify blocking I/O vs downstream slowness from
   actuator metrics and thread dumps.
3. **DECIDE** Choose between a single gateway and BFF for
   a system with mobile, web, and partner API clients.
4. **IMPLEMENT** Write a custom GlobalFilter that adds
   a correlation ID to all requests and logs latency.
5. **OPERATE** Design a zero-downtime gateway deployment
   during a routing config update on an active path.

---

### 🧠 Think About This Before We Continue

**Q1.** An API Gateway validates JWT tokens for every
request. At 50,000 requests/second, JWT validation (RSA
signature check) takes 0.5ms per request on a single CPU
core. Calculate the CPU required just for JWT validation
at peak. How do you optimise without sacrificing security?
(Hint: JWT caching by JTI or sub+iat, asymmetric vs
symmetric signing.)

**Q2.** The Order Service has a breaking API change. Both
old and new versions must be supported for 3 months. Design
the gateway routing that serves v1 clients on the old API
and v2 clients on the new API simultaneously, including
how to manage routing rules during migration.

**Q3.** Design a multi-region, active-active gateway
topology that: (a) routes traffic to the nearest region,
(b) fails over if one region is unavailable, (c) maintains
consistent rate limits across regions. What infrastructure
(DNS, CDN, distributed cache) is required for each property?