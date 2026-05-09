---
version: 1
layout: default
title: "Spring Cloud Gateway"
parent: "Spring Core"
grand_parent: "Technical Dictionary"
nav_order: 12
permalink: /spring/spring-cloud-gateway/
id: SPR-012
category: Spring Core
difficulty: ★★★
depends_on: Spring Cloud Overview, API Gateway Pattern, Reactive Programming
used_by: Microservices, Spring Cloud Service Discovery (Eureka)
related: API Gateway Patterns, Kong, Apigee
tags:
  - java
  - spring
  - microservices
  - networking
  - advanced
---

# SPR-012 - Spring Cloud Gateway

⚡ **TL;DR -** Spring Cloud Gateway is a reactive, non-blocking API gateway built on Spring WebFlux that routes, filters, and secures traffic across microservices with a declarative route DSL.

| Metadata | Values |
|---|---|
| **Depends on** | Spring Cloud Overview, API Gateway Pattern, Reactive Programming |
| **Used by** | Microservices, Spring Cloud Service Discovery (Eureka) |
| **Related** | API Gateway Patterns, Kong, Apigee |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** Your frontend calls 15 different microservice endpoints directly - different ports, different base paths, different authentication mechanisms. Adding JWT validation means adding it to 15 services. Enabling rate limiting means adding it to 15 services. When Service B moves to a new host, the frontend must be redeployed. CORS headers are configured in 15 places inconsistently.

**THE BREAKING POINT:** A microservices architecture without an API gateway exposes internal service topology to clients, duplicates cross-cutting concerns (auth, rate limiting, logging, CORS) across every service, makes service refactoring require client changes, and provides no centralized control plane for traffic management.

**THE INVENTION MOMENT:** Spring Cloud Gateway (2019, replacing the older Netflix Zuul) was built on Spring WebFlux and Project Reactor to address the performance limitations of Zuul's blocking Servlet model. It handles cross-cutting concerns in a single reactive process: route matching via predicates, request/response manipulation via filters, circuit breaking, rate limiting, and load balancing - all without blocking threads.

---

### 📘 Textbook Definition

**Spring Cloud Gateway** is a reactive API gateway built on Spring WebFlux, Reactor Netty, and Project Reactor. It provides: **route predicates** (conditions that determine if an incoming request matches a route - Path, Method, Header, Host, Query, Weight, etc.); **gateway filters** (per-route or global request/response transformations - RewritePath, AddRequestHeader, CircuitBreaker, RequestRateLimiter, Retry, StripPrefix, etc.); and **global filters** (cross-cutting concerns applied to all routes - authentication, logging, tracing). Routes can resolve upstream URIs as static URLs or via service discovery using the `lb://service-name` scheme.

---

### ⏱️ Understand It in 30 Seconds

**One line:** A single reactive entry point that routes requests to microservices, applying filters for auth, rate limiting, and circuit breaking.

> Think of a hotel concierge: every guest (client request) talks to the concierge (Gateway) rather than wandering the building themselves. The concierge checks ID (auth filter), limits how often a guest can make requests (rate limiter), directs them to the right department (route predicate + load balancer), and has an emergency plan if a department is unavailable (circuit breaker fallback).

**One insight:** Spring Cloud Gateway's reactive model means a gateway instance handling 10,000 concurrent requests uses the same number of threads as one handling 100. Unlike Zuul 1's blocking thread-per-request model, it scales I/O-bound gateway workloads without proportionally scaling thread pools.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **Every request matches at most one route** - routes are evaluated in order; first predicate match wins
2. **Filters form a chain** - pre-filters execute before the proxy call; post-filters execute after the response returns
3. **The gateway is a reverse proxy** - it never returns application logic; it only routes, transforms, and controls
4. **`lb://` prefix = service discovery + load balancing** - the gateway resolves the logical name to an instance via `ReactiveLoadBalancer`
5. **Global filters apply before route-specific filters** - `GlobalFilter` is always in the chain; route filters are additive

**DERIVED DESIGN:**

The predicate-plus-filter architecture separates routing decisions (predicates: match or not match) from request modification (filters: transform the request/response). This allows predicates to be composed (all must match) and filters to be independently configured per route - the gateway routes to Service A with auth and rate limiting, but to Service B with only auth, without any code change.

**THE TRADE-OFFS:**

**Gain:** Centralized cross-cutting concerns (auth, rate limiting, CORS, logging); decouples client from service topology; declarative route configuration via YAML or Java DSL; reactive throughput without thread-per-request scaling; built-in service discovery integration.

**Cost:** Adds network hop (extra latency of ~1–5ms per request); gateway becomes a critical path component requiring HA; WebFlux/Reactor expertise required for custom filter development; debugging reactive filter chains is harder than servlet-based code; not suitable for WebSocket-heavy traffic without specific configuration.

---

### 🧪 Thought Experiment

**SETUP:** You have 8 microservices. The frontend calls all of them directly. You add JWT authentication to protect all endpoints.

**WHAT HAPPENS WITHOUT A GATEWAY:** You add a JWT filter to all 8 services - 8 code changes, 8 separate deployments, 8 places where a misconfiguration could expose an endpoint. A new service is added: the developer forgets the JWT filter - the endpoint is publicly accessible for 3 days before anyone notices.

**WHAT HAPPENS WITH SPRING CLOUD GATEWAY:** Add one `TokenRelayGatewayFilter` to the gateway's global filter chain. All 8 services receive requests only via the gateway. New services added behind the gateway are automatically protected - no per-service JWT code. The JWT validation logic exists in exactly one place. A vulnerability fix is a one-line change in one service.

**THE INSIGHT:** The gateway converts a horizontal cross-cutting concern (auth, rate limiting) from N implementations to 1 implementation. The value grows linearly with the number of microservices - with 50 services, a gateway is not optional, it's essential.

---

### 🧠 Mental Model / Analogy

> An airport security and routing system: every passenger (HTTP request) enters through security (global auth filter), has their ticket checked (route predicate), is directed to the right gate (upstream service), and their boarding pass may be stamped with additional information (response header filter). Some gates have queues with limits (rate limiter). If a gate is closed (circuit breaker OPEN), passengers are redirected to a standby gate (fallback URI).

- **Airport entrance** → Gateway entry point
- **Security check** → Global authentication filter
- **Ticket match** → Route predicate (Path, Method, Header)
- **Gate assignment** → Route URI (`lb://service-name`)
- **Boarding pass stamp** → Response modification filter
- **Queue limit per gate** → `RequestRateLimiter` filter
- **Gate closed → standby** → CircuitBreaker filter + fallback
- **Baggage re-labeling** → `RewritePath` / `StripPrefix` filter

Where this analogy breaks down: Real airports route passengers to a physical location; a gateway routes requests to logical service names that resolve dynamically via service discovery - the "gate" address changes on every deployment without the passenger (client) needing to know.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Spring Cloud Gateway is the single front door to all your microservices. Requests come in, the gateway checks which service should handle them, optionally applies security checks or speed limits, and forwards the request to the right service.

**Level 2 - How to use it (junior developer):**
Add `spring-cloud-starter-gateway` to a Spring Boot project (note: must NOT also have `spring-boot-starter-web` - WebFlux and Servlet stacks conflict). Define routes in `application.yml` with `predicates` (when to match) and `filters` (what to do before/after). Use `lb://service-name` as the route URI to enable service discovery load balancing.

**Level 3 - How it works (mid-level engineer):**
Incoming requests flow through `ReactorHttpHandlerAdapter` into the `DispatcherHandler`. `RoutePredicateHandlerMapping` iterates configured routes in order, evaluating each route's predicate against the `ServerWebExchange`. The first matching route's `FilteringWebHandler` assembles the filter chain: global filters + route-specific filters, sorted by `Ordered` priority. Pre-filters execute in ascending order, the `NettyRoutingFilter` proxies the request to the upstream service via Reactor Netty, then post-filters execute in descending order on the response. The `ReactiveLoadBalancer` resolves `lb://` URIs to actual host:port using cached service registry data.

**Level 4 - Why it was designed this way (senior/staff):**
The reactive foundation was a deliberate response to Zuul 1's blocking model. In a gateway, every proxied request involves two I/O operations (receive + forward). With blocking Servlet, each request occupies a thread during both I/O waits - at 10,000 concurrent requests you need 10,000 threads (GBs of memory). With Reactor Netty's event loop model, a handful of I/O threads handle thousands of concurrent connections via non-blocking callbacks. The predicate-filter separation mirrors the Servlet filter chain pattern familiar to Java developers, but adapted for reactive streams - each filter returns a `Mono<Void>` and can transform the `ServerWebExchange` without blocking.

---

### ⚙️ How It Works (Mechanism)

```
[Client HTTP Request]
        │
        ▼
[ReactorHttpHandlerAdapter]
  (Reactor Netty event loop)
        │
        ▼
[RoutePredicateHandlerMapping]
  evaluate routes in order:
  ┌──────────────────────────────────────┐
  │ Route 1: Path=/api/orders/**         │
  │   predicate match? YES → use Route 1 │
  └──────────────────────────────────────┘
        │
        ▼
[FilteringWebHandler assembles chain]
  Global Filters:
    AuthenticationFilter (order -100)
    LoggingFilter        (order -90)
  Route Filters:
    StripPrefix=1         (order 1)
    CircuitBreaker        (order 2)
    RequestRateLimiter    (order 3)
        │
        ▼ (PRE filters execute in order)
[Filter chain: auth → log → rate limit]
        │
        ▼
[NettyRoutingFilter]
  Resolve lb://order-service
  → ReactiveLoadBalancer → 10.0.1.5:8080
  → HTTP proxy request via Reactor Netty
        │
        ▼ (response arrives)
[POST filters execute in reverse order]
[AddResponseHeader, etc.]
        │
        ▼
[Response returned to client]
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
[Client: GET /api/orders/123]
      │ ← YOU ARE HERE
      ▼
[Gateway: RoutePredicateHandlerMapping]
  Route match: Path=/api/orders/**
  URI: lb://order-service
      │
      ▼
[Global filter: validate JWT Bearer token]
  Token valid → extract userId, add to header
      │
      ▼
[Route filter: StripPrefix=1]
  /api/orders/123 → /orders/123
      │
      ▼
[Route filter: RequestRateLimiter]
  userId=42, bucket has tokens → allow
      │
      ▼
[NettyRoutingFilter: lb://order-service]
  LoadBalancer: pick instance 10.0.1.5:8080
  Proxy: GET http://10.0.1.5:8080/orders/123
      │
      ▼ (response 200 OK)
[Post-filter: AddResponseHeader]
  X-Gateway-Response-Time: 12ms
      │
      ▼
[Client receives 200 OK]
```

**FAILURE PATH:**
```
[Upstream order-service: 5 errors in 10s]
      │
      ▼
[CircuitBreaker filter: OPEN]
[Subsequent requests: immediate fallback]
  → forward: /fallback/orders (fallback controller)
  → or return: 503 + Retry-After header
      │
      ▼ (after waitDurationInOpenState = 30s)
[CircuitBreaker: HALF_OPEN]
[1 probe request to order-service]
  → success → CLOSED → normal routing resumes
  → failure → OPEN again
```

**WHAT CHANGES AT SCALE:**
Rate limiting with `RequestRateLimiter` requires a shared state store - Redis is the standard backend via `spring-cloud-starter-gateway` + `spring-boot-starter-data-redis-reactive`. Without Redis, each gateway instance has its own local rate limit, allowing clients to bypass limits by hitting different gateway instances. For high-traffic gateways, connection pool tuning on Reactor Netty is critical: `spring.cloud.gateway.httpclient.pool.max-connections` controls the upstream connection pool per service.

---

### 💻 Code Example

**BAD - YAML route without authentication or resilience:**
```yaml
# No auth, no rate limiting, no circuit breaker
# Direct service exposure to the internet
spring:
  cloud:
    gateway:
      routes:
        - id: order-route
          uri: http://10.0.1.5:8080  # hardcoded IP!
          predicates:
            - Path=/api/orders/**
```

**GOOD - production-grade gateway configuration:**
```yaml
spring:
  application:
    name: api-gateway
  cloud:
    gateway:
      # Discovery-based routing: all registered services
      discovery:
        locator:
          enabled: true
          lower-case-service-id: true
      routes:
        - id: order-service-route
          uri: lb://order-service        # service discovery
          predicates:
            - Path=/api/orders/**
            - Method=GET,POST,PUT,DELETE
          filters:
            - StripPrefix=1              # /api/orders → /orders
            - name: CircuitBreaker
              args:
                name: orderCircuitBreaker
                fallbackUri: forward:/fallback/orders
            - name: RequestRateLimiter
              args:
                redis-rate-limiter:
                  replenishRate: 100     # tokens/sec
                  burstCapacity: 200     # max burst
                  requestedTokens: 1
                key-resolver: "#{@userKeyResolver}"
            - name: Retry
              args:
                retries: 3
                statuses: BAD_GATEWAY,SERVICE_UNAVAILABLE
                methods: GET
                backoff:
                  firstBackoff: 100ms
                  maxBackoff: 500ms
                  factor: 2
        - id: inventory-service-route
          uri: lb://inventory-service
          predicates:
            - Path=/api/inventory/**
          filters:
            - StripPrefix=1
            - AddRequestHeader=X-Source-Gateway, api-gateway

      # Default filters applied to ALL routes
      default-filters:
        - AddResponseHeader=X-Gateway-Version, 2.0
        - name: RequestSize
          args:
            maxSize: 5MB

resilience4j:
  circuitbreaker:
    instances:
      orderCircuitBreaker:
        slidingWindowSize: 10
        failureRateThreshold: 50
        waitDurationInOpenState: 30s
        permittedNumberOfCallsInHalfOpenState: 3
```

```java
// Global authentication filter
@Component
public class AuthenticationFilter implements GlobalFilter,
        Ordered {

    private final JwtTokenValidator jwtValidator;

    @Override
    public Mono<Void> filter(
            ServerWebExchange exchange,
            GatewayFilterChain chain) {
        String path = exchange.getRequest()
            .getPath().toString();
        // Skip auth for public endpoints
        if (path.startsWith("/public/")
                || path.startsWith("/actuator/")) {
            return chain.filter(exchange);
        }
        String authHeader = exchange.getRequest()
            .getHeaders().getFirst("Authorization");
        if (authHeader == null
                || !authHeader.startsWith("Bearer ")) {
            exchange.getResponse()
                .setStatusCode(HttpStatus.UNAUTHORIZED);
            return exchange.getResponse().setComplete();
        }
        String token = authHeader.substring(7);
        return jwtValidator.validate(token)
            .flatMap(claims -> {
                // Forward userId to downstream services
                ServerHttpRequest mutated =
                    exchange.getRequest().mutate()
                        .header("X-User-Id",
                            claims.getSubject())
                        .build();
                return chain.filter(
                    exchange.mutate()
                        .request(mutated).build());
            })
            .onErrorResume(e -> {
                exchange.getResponse()
                    .setStatusCode(HttpStatus.UNAUTHORIZED);
                return exchange.getResponse().setComplete();
            });
    }

    @Override
    public int getOrder() {
        return -100;  // run before all route filters
    }
}

// Rate limiter key resolver - limits per authenticated user
@Bean
public KeyResolver userKeyResolver() {
    return exchange -> Mono.justOrEmpty(
        exchange.getRequest().getHeaders()
            .getFirst("X-User-Id"))
        .defaultIfEmpty("anonymous");
}

// Fallback controller for circuit breaker
@RestController
public class FallbackController {
    @RequestMapping("/fallback/orders")
    public Mono<ResponseEntity<Map<String, String>>>
            ordersFallback() {
        return Mono.just(ResponseEntity
            .status(HttpStatus.SERVICE_UNAVAILABLE)
            .body(Map.of(
                "message", "Order service unavailable",
                "retryAfter", "30"
            )));
    }
}
```

---

### ⚖️ Comparison Table

| Feature | Spring Cloud Gateway | Kong | Apigee | AWS API Gateway |
|---|---|---|---|---|
| **Model** | Reactive JVM (WebFlux) | Nginx (C, Lua) | Google-managed | AWS-managed |
| **Config** | YAML / Java DSL | Admin API / YAML | UI / Terraform | Console / CDK |
| **Service discovery** | Eureka, Consul, K8s | DNS, Consul, K8s | N/A (managed) | Route53 |
| **Rate limiting** | Redis-backed | Redis-backed | Built-in | Built-in |
| **Circuit breaker** | Resilience4j | Plugin | Built-in | N/A |
| **Custom filters** | Java (reactive) | Lua plugins | JavaScript | Lambda authorizers |
| **Latency overhead** | ~2–5ms | ~1–3ms | ~5–15ms | ~10–30ms |
| **Best for** | Spring Boot ecosystems | Polyglot APIs | Enterprise API mgmt | AWS-native workloads |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Spring Cloud Gateway can use `spring-web`" | Gateway uses WebFlux exclusively. Adding `spring-boot-starter-web` causes a startup conflict. The gateway is a purely reactive application. |
| "Predicates are executed on every request" | Predicates are evaluated in order; execution stops at the first match. Route order in YAML matters - more specific paths must come before wildcard paths. |
| "Rate limiting without Redis works correctly" | Without Redis, each gateway instance maintains its own in-memory rate limit. Clients can bypass limits by distributing requests across gateway instances. Redis provides shared state. |
| "CircuitBreaker filter = Resilience4j CircuitBreaker in services" | They're independent. The Gateway circuit breaker protects the gateway-to-service connection. Service-to-service circuit breakers protect service-to-service calls. Both can exist simultaneously. |
| "StripPrefix=1 removes the first path segment always" | `StripPrefix=1` removes the first segment of the path before forwarding. `/api/orders/123` with `StripPrefix=1` → `/orders/123`. The count is segments, not characters. |
| "The gateway can call microservice business logic" | The gateway is a pure proxy - it routes and transforms HTTP, but contains no business logic. Mixing business logic into the gateway creates a distributed monolith anti-pattern. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Route not matching - 404 for all requests**

**Symptom:** All requests to the gateway return 404; upstream services are healthy.
**Root Cause:** Route predicates are not matching - either path mismatch, case sensitivity, or route order (a wildcard route earlier in the list captures all traffic before the specific route).
**Diagnostic:**
```bash
# Enable gateway actuator routes endpoint
# management.endpoints.web.exposure.include=gateway

curl http://gateway:8080/actuator/gateway/routes
# Lists all configured routes with their predicates

# Enable trace logging for predicate evaluation
logging.level.org.springframework.cloud.gateway=TRACE
# Shows which predicates matched/failed for each request
```
**Fix:**
```yaml
# BAD: wildcard before specific - specific never reached
routes:
  - id: catch-all
    uri: lb://fallback
    predicates:
      - Path=/**                # matches everything first

  - id: orders                  # never reached
    uri: lb://order-service
    predicates:
      - Path=/api/orders/**

# GOOD: specific routes before wildcards
routes:
  - id: orders
    uri: lb://order-service
    predicates:
      - Path=/api/orders/**     # matched first

  - id: catch-all
    uri: lb://fallback
    predicates:
      - Path=/**                # only if no match above
```
**Prevention:** Always define more-specific routes before less-specific (wildcard) routes. Test route configuration via `/actuator/gateway/routes` before deploying.

**Mode 2: Rate limiter not enforcing limits across gateway instances**

**Symptom:** A client is making 500 req/s but the rate limiter (configured at 100 req/s) is not blocking them.
**Root Cause:** Redis is not configured or not reachable - the `RequestRateLimiter` falls back to a no-op (allows all requests) rather than failing closed.
**Diagnostic:**
```bash
# Check Redis connectivity from gateway
redis-cli -h redis-host ping  # should return PONG

# Check gateway logs for Redis connection errors
grep -i "redis\|rate.limit" application.log

# Check rate limiter metrics
curl http://gateway:8080/actuator/metrics/\
  spring.cloud.gateway.requests?tag=status:TOO_MANY_REQUESTS
```
**Fix:**
```yaml
spring:
  data:
    redis:
      host: redis-host
      port: 6379
      connect-timeout: 1000ms
      timeout: 500ms

# Explicitly configure deny-empty-key (fail closed)
spring:
  cloud:
    gateway:
      filter:
        request-rate-limiter:
          deny-empty-key: true   # reject if key resolver fails
```
**Prevention:** Treat Redis as a critical dependency for the gateway. Add Redis health to the gateway's readiness probe. Test rate limiting with distributed load testing (multiple clients, multiple gateway instances).

**Mode 3: Custom `GlobalFilter` causes `StackOverflowError` or memory leak**

**Symptom:** Gateway degrades under load; heap dump shows `ServerWebExchange` objects accumulating; eventually OOM.
**Root Cause:** A custom `GlobalFilter` is blocking (calling `.block()` on a `Mono`) or retaining a reference to the `ServerWebExchange` after the request completes, preventing garbage collection.
**Diagnostic:**
```bash
# Capture heap dump under load
jmap -dump:format=b,file=heap.hprof <pid>
# Analyze with Eclipse MAT: look for ServerWebExchange
# or ServerHttpRequest object accumulation

# Check for blocking calls in filter logs
logging.level.reactor.blockhound=DEBUG
```
**Fix:**
```java
// BAD: blocking in reactive filter
@Override
public Mono<Void> filter(
        ServerWebExchange exchange,
        GatewayFilterChain chain) {
    // NEVER do this - blocks Netty I/O thread
    User user = userService.findUser(userId).block();
    return chain.filter(exchange);
}

// GOOD: fully reactive filter
@Override
public Mono<Void> filter(
        ServerWebExchange exchange,
        GatewayFilterChain chain) {
    return userService.findUser(userId)
        .flatMap(user -> {
            ServerHttpRequest mutated =
                exchange.getRequest().mutate()
                    .header("X-User-Role", user.getRole())
                    .build();
            return chain.filter(
                exchange.mutate().request(mutated).build());
        });
}
```
**Prevention:** Never call `.block()` in any `GlobalFilter` or `GatewayFilter`. Add `BlockHound` to the test classpath to detect blocking calls in reactive chains during testing.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- Spring Cloud Overview (2124) - Spring Cloud ecosystem and service discovery integration
- API Gateway Pattern - the architectural pattern Spring Cloud Gateway implements
- Reactive Programming - Project Reactor and WebFlux model underlying gateway internals

**Builds On This (learn these next):**
- Spring Cloud Service Discovery (Eureka) - how `lb://` URIs are resolved to instances
- Microservices - API gateway as an architectural pattern in distributed systems

**Alternatives / Comparisons:**
- Kong - Nginx-based API gateway; better for polyglot / non-JVM architectures
- Apigee - enterprise API management platform with monetization and developer portal
- AWS API Gateway - managed gateway for AWS-native serverless and REST APIs

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────┐
│ WHAT IT IS   │ Reactive API gateway on WebFlux   │
│ PROBLEM      │ Cross-cutting concerns duplicated │
│              │ across all microservices          │
│ KEY INSIGHT  │ Predicates match; filters act     │
│              │ Pre-filters → proxy → Post-filters│
│ USE WHEN     │ Spring Boot microservices needing │
│              │ single entry point + auth/RL/CB   │
│ AVOID WHEN   │ Mixing with spring-web (Servlet)  │
│ TRADE-OFF    │ Extra latency hop; reactive skill │
│ ONE-LINER    │ Route + Filter = declarative proxy│
│ NEXT EXPLORE │ Service Discovery (Eureka)        │
└──────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

1. **(A - System Interaction)** Your gateway has a `GlobalFilter` that validates JWT tokens. When a downstream service (order-service) also validates JWTs independently, you have double validation. Under what circumstances is this redundancy beneficial versus wasteful, and how does mTLS between gateway and services change the trust model?

2. **(B - Scale)** Your gateway handles 50,000 req/s with Redis-backed rate limiting. The Redis round-trip adds 0.5ms per request. What is the total latency overhead from Redis calls at peak load, and what architectural change would you make to reduce it while maintaining correctness?

3. **(C - Design Trade-off)** Spring Cloud Gateway routes configuration can be defined in YAML (static) or via a `RouteLocator` bean (dynamic/programmatic). For a multi-tenant SaaS platform where tenant routing rules change frequently, which approach would you choose and what mechanism would you use to apply changes without gateway restarts?
