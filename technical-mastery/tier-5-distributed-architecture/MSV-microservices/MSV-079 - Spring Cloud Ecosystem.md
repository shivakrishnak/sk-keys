---
id: MSV-079
title: Spring Cloud Ecosystem
category: Microservices
tier: tier-5-distributed-architecture
folder: MSV-microservices
difficulty: ★★★
depends_on: MSV-001, MSV-010, MSV-020
used_by: MSV-001, MSV-020
related: MSV-010, MSV-020, MSV-025, MSV-030, MSV-001, MSV-072, MSV-078
tags:
  - microservices
  - spring
  - deep-dive
  - java
status: complete
version: 4
layout: default
parent: "Microservices"
grand_parent: "Technical Mastery"
nav_order: 79
permalink: /technical-mastery/microservices/spring-cloud-ecosystem/
---

⚡ TL;DR - Spring Cloud Ecosystem: the set of
Spring Framework projects that solve common
microservices infrastructure problems for Java
services. Core components: Spring Cloud Gateway
(API Gateway), Spring Cloud Eureka (service
discovery), Spring Cloud Config (centralized
configuration), Spring Cloud OpenFeign (declarative
REST clients), Spring Cloud LoadBalancer (client-
side load balancing), Resilience4j (circuit
breaker). Context: Spring Cloud was the "pre-
Kubernetes" answer to microservices infrastructure.
With Kubernetes + Istio: many Spring Cloud components
become redundant. Key skill: know which Spring
Cloud components are still needed in 2025 vs
replaced by Kubernetes/Istio.

| #079 | Category: Microservices | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | What are Microservices, API Gateway, Service Mesh | |
| **Used by:** | What are Microservices, Service Mesh | |
| **Related:** | API Gateway, Service Mesh, Circuit Breaker, Service Discovery, What are Microservices, Sidecar Pattern, Service Mesh Traffic Management | |

---

### 🔥 The Problem This Solves

**MICROSERVICES INFRASTRUCTURE FOR JAVA TEAMS:**
Pre-2018 (before Kubernetes became mainstream):
Java teams building microservices needed: service
discovery (how does service A find service B?),
configuration management (12 services, each needs
DB URL for 3 environments), API gateway (routing,
authentication at the edge), circuit breaking
(don't cascade failures), and client-side load
balancing (round-robin calls to service instances).
Spring Cloud: addressed all of these with
Spring-native annotations and auto-configuration.

---

### 📘 Textbook Definition

**Spring Cloud Ecosystem** is the collection of
Spring projects (under the `spring-cloud-*` umbrella)
that provide infrastructure patterns for distributed
systems and microservices, primarily for Java
Spring Boot applications.

**Core components:**
- **Spring Cloud Gateway**: reactive API gateway
  (replaces Netflix Zuul). Route definitions,
  predicates (path, header, method), filters
  (rate limiting, authentication, circuit breaking).
- **Spring Cloud Eureka**: service registry and
  discovery (Netflix OSS). Services: register
  with Eureka on startup. Callers: look up service
  instances by name (no hardcoded URLs).
- **Spring Cloud Config**: externalized configuration
  server. Stores config in Git; services: fetch
  config at startup or at runtime (hot reload
  via Spring Cloud Bus + Kafka/RabbitMQ).
- **Spring Cloud OpenFeign**: declarative HTTP
  client. Define interface with annotations;
  Spring: generates implementation. Integrated
  with Eureka (load-balanced calls), Resilience4j
  (circuit breaking per interface method).
- **Spring Cloud LoadBalancer**: client-side
  load balancing. Replaces Ribbon (deprecated).
  Used by Feign for distributing calls across
  service instances.
- **Resilience4j**: circuit breaker, retry,
  rate limiter, bulkhead. Spring Boot integration:
  `@CircuitBreaker`, `@Retry`, `@Bulkhead` annotations.
- **Spring Cloud Sleuth** (now Micrometer Tracing):
  distributed tracing. Auto-injects trace + span
  IDs into all requests and logs.
- **Spring Cloud Bus**: message bus for broadcasting
  config refresh events across service instances.

**Spring Cloud vs Kubernetes (2025 perspective):**
Many Spring Cloud components are now redundant
when running on Kubernetes + Istio. Understanding
which components to keep vs replace is a senior
skill.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Spring Cloud: infrastructure plumbing for Java
microservices. Gateway, service discovery, config,
circuit breaker. Much of it replaced by Kubernetes
+ Istio in modern deployments.

**One analogy:**
> Spring Cloud is like the original Swiss Army
> knife for Java microservices. Before Kubernetes
> became mainstream: Spring Cloud provided every
> tool needed. With Kubernetes: you now have a
> dedicated professional tool for each job (K8s
> DNS for service discovery, Istio for circuit
> breaking, ConfigMaps for config, Ingress for
> routing). The Swiss Army knife (Spring Cloud)
> still works, but professional tools (K8s + Istio)
> do each job better. You might keep some blades
> (Feign, Resilience4j) while replacing others.

**One insight:**
The most important Spring Cloud component to
keep in 2025 is Spring Cloud OpenFeign (with
Resilience4j). Why: Feign gives Java developers
a clean, testable HTTP client interface (no
boilerplate RestTemplate/WebClient code). The
most important to REPLACE is Eureka (service
discovery) - Kubernetes DNS does this better
(`http://customer-service.namespace.svc.cluster.local`).
And Spring Cloud Config - Kubernetes ConfigMaps
+ External Secrets Operator does this better.

---

### 🔩 First Principles Explanation

**SPRING CLOUD vs KUBERNETES: WHAT TO KEEP**

```
COMPONENT MIGRATION DECISION MATRIX:

Spring Cloud Eureka (service discovery)
  Pre-K8s: services register, others discover
  K8s replacement: Kubernetes DNS
    http://order-service -> resolves via K8s DNS
    http://order-service.orders.svc.cluster.local
  VERDICT: REMOVE (Kubernetes DNS is better)
  Spring Cloud LoadBalancer: also remove
    (K8s Services + Istio do load balancing)

Spring Cloud Config Server
  Pre-K8s: config stored in Git, served by Config Server
  K8s replacement:
    ConfigMaps: non-sensitive config
    External Secrets Operator + Vault: secrets
    ArgoCD: GitOps for all config
  VERDICT: REMOVE (K8s-native config management)

Spring Cloud Gateway
  Still useful: edge routing, rate limiting,
  auth token enrichment, request transformation
  K8s alternative: Ingress + Istio Gateway
  VERDICT: KEEP (more flexible than Istio Gateway
    for complex routing logic; Spring native)
  OR REPLACE: with Kong, AWS API Gateway, Istio
    (team preference)

Spring Cloud OpenFeign
  No K8s replacement (language-specific HTTP client)
  Still useful: declarative HTTP client interface
    + Resilience4j circuit breaker integration
    + easy mock in tests (just mock the interface)
  VERDICT: KEEP (no equivalent in K8s layer)

Resilience4j (circuit breaker, retry)
  K8s alternative: Istio VirtualService + DestinationRule
  Difference: Istio handles HTTP-level retry
  Resilience4j: handles application-level logic
    (retry on business exception, bulkhead per
     feature, rate limit per user)
  VERDICT: KEEP both (different layers)

Spring Cloud Sleuth
  Migrated to: Micrometer Tracing
    (Spring Boot 3.x default)
  VERDICT: KEEP as Micrometer Tracing
    (not "Spring Cloud Sleuth" anymore)
```

---

### 🧪 Thought Experiment

**OPENFEIGN WITH RESILIENCE4J: DECLARATIVE REST CLIENT**

```java
// SCENARIO: order-service calls inventory-service
// and payment-service with circuit breaking

// STEP 1: Define Feign interfaces

@FeignClient(
    name = "inventory-service",
    // Service name = K8s service DNS name
    // Feign + Spring Cloud LoadBalancer:
    // resolves to Kubernetes service
    fallback = InventoryClientFallback.class
)
public interface InventoryClient {
    
    @GetMapping("/api/v1/inventory/{sku}")
    @CircuitBreaker(
        name = "inventoryService",
        fallbackMethod = "getInventoryFallback")
    InventoryResponse getInventory(
        @PathVariable String sku);
}

// STEP 2: Fallback implementation
@Component
public class InventoryClientFallback
        implements InventoryClient {
    
    @Override
    public InventoryResponse getInventory(String sku) {
        // Default: assume 0 quantity when
        // inventory-service is unavailable
        // Order: can proceed with "limited stock" warning
        return InventoryResponse.defaultUnavailable(sku);
    }
}

// STEP 3: Use in service
@Service
public class OrderService {
    private final InventoryClient inventoryClient;
    
    public Order createOrder(CreateOrderRequest req) {
        // Simple call - circuit breaker is transparent
        // If inventory-service fails 5 times: circuit opens
        // Fallback: called; order proceeds
        InventoryResponse inventory =
            inventoryClient.getInventory(req.getSku());
        // ...
    }
}

// STEP 4: Resilience4j config
// (application.yaml)
//resilience4j:
//  circuitbreaker:
//    instances:
//      inventoryService:
//        slidingWindowSize: 10
//        failureRateThreshold: 50
//        waitDurationInOpenState: 30s
//  retry:
//    instances:
//      inventoryService:
//        maxAttempts: 3
//        waitDuration: 200ms
```

---

### 🧠 Mental Model / Analogy

> Spring Cloud is like an older generation of
> home appliances. In 2010: you needed separate
> devices for each function (VCR, DVD player,
> cable box, stereo). Spring Cloud: all-in-one
> for microservices (discovery, config, gateway,
> circuit breaker). In 2024: a smart TV does most
> of this (Kubernetes + Istio). But your VCR
> (Feign + Resilience4j) still plays tapes that
> nothing else can play (Java-level HTTP client
> abstraction and application-level circuit
> breaking). Keep what's still useful; replace
> what has a better modern equivalent.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Spring Cloud: pre-built solutions for common
microservices problems in Java. Saves developers
from implementing service discovery, centralized
configuration, and circuit breaking from scratch.

**Level 2 - Getting started (junior developer):**
`spring-cloud-starter-openfeign` + `resilience4j-
spring-boot-starter`. Define `@FeignClient`
interface + configure circuit breaker in `application.yaml`.
That's the minimum useful Spring Cloud setup for
modern Kubernetes deployments.

**Level 3 - Spring Cloud Gateway (mid-level):**
Define routes with predicates and filters:
```yaml
spring:
  cloud:
    gateway:
      routes:
      - id: order-service
        uri: lb://order-service  # load balanced
        predicates:
        - Path=/api/v1/orders/**
        filters:
        - StripPrefix=2          # remove /api/v1
        - name: CircuitBreaker
          args:
            name: orders
            fallbackUri: forward:/fallback
        - name: RequestRateLimiter
          args:
            redis-rate-limiter.replenishRate: 100
            redis-rate-limiter.burstCapacity: 200
```

**Level 4 - Config hot reload (senior):**
Spring Cloud Config + `@RefreshScope`: beans
reload config without restart when `POST /actuator/
refresh` is called. Combined with Spring Cloud
Bus (Kafka/RabbitMQ): one event triggers refresh
on all instances simultaneously. Use case: feature
flags in Config Server that can be toggled in
production without deployment. Tradeoff: state
mutation at runtime is hard to debug and audit.
Kubernetes alternative: ConfigMap + `kubectl
rollout restart` is more predictable.

**Level 5 - Spring Cloud evolution (principal):**
Spring Cloud 2024: many components deprecated
or merged. Key changes: (1) Sleuth -> Micrometer
Tracing (in Spring Boot 3.x); (2) Ribbon ->
Spring Cloud LoadBalancer (Ribbon deprecated);
(3) Hystrix -> Resilience4j (Hystrix deprecated).
For new projects: Spring Boot 3.x + Micrometer
Tracing + Resilience4j + Feign + Kubernetes.
Skip: Eureka, Spring Cloud Config Server, Zuul
(all have better K8s-native alternatives).

---

### ⚙️ How It Works (Mechanism)

```java
// SPRING CLOUD GATEWAY: complete security + routing config
@Configuration
public class GatewayConfig {
    
    @Bean
    public RouteLocator routeLocator(
            RouteLocatorBuilder builder) {
        return builder.routes()
            
            // Order service routes
            .route("order-service", r -> r
                .path("/api/v1/orders/**")
                // JWT authentication filter
                .filters(f -> f
                    .filter(jwtAuthFilter())
                    // Forward JWT to downstream
                    .addRequestHeader(
                        "X-Authenticated", "true")
                    .circuitBreaker(config ->
                        config.setName("orders")
                              .setFallbackUri(
                                "forward:/service-down"))
                    .requestRateLimiter(config ->
                        config.setRateLimiter(
                            redisRateLimiter())
                              .setKeyResolver(
                                userKeyResolver()))
                )
                // lb://: uses Spring Cloud LoadBalancer
                // Resolves Kubernetes service: order-service
                .uri("lb://order-service")
            )
            .build();
    }
    
    @Bean
    public RedisRateLimiter redisRateLimiter() {
        // 100 requests/second per user
        // burst: 200 (allows short spikes)
        return new RedisRateLimiter(100, 200, 1);
    }
}
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
SPRING CLOUD ECOSYSTEM IN 2025 K8S DEPLOYMENT:

  External Client
      |
      v
  Spring Cloud Gateway (edge)
    - JWT validation (Spring Security)
    - Rate limiting (Redis)
    - Route to services (lb:// = K8s DNS)
    - Circuit breaker (Resilience4j filter)
      |
      v
  Kubernetes Service (DNS: order-service)
    - K8s replaces Eureka (no registration needed)
    - K8s replaces Spring Cloud LoadBalancer for
      basic round-robin (Istio for advanced)
      |
      v
  order-service (Spring Boot 3.x)
    - Feign client calls inventory/payment-service
    - Resilience4j: circuit breaker + retry
    - Micrometer Tracing: distributed trace
    - Actuator: /health, /metrics, /info
      |
      v
  inventory-service (K8s DNS resolution)
  payment-service  (K8s DNS resolution)
  
  WHAT'S NOT USED (replaced by K8s):
  - Eureka: K8s DNS replaces it
  - Spring Cloud Config: ConfigMaps + Vault
  - Ribbon: K8s Services + Istio
  - Spring Cloud Sleuth: Micrometer Tracing
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: RestTemplate boilerplate vs Feign**

```java
// BAD: verbose RestTemplate + manual error handling
// Must repeat this pattern for every service call
@Service
public class OrderService {
    private final RestTemplate restTemplate;
    
    public InventoryResponse checkInventory(String sku) {
        try {
            String url = "http://inventory-service"
                + "/api/v1/inventory/" + sku;
            ResponseEntity<InventoryResponse> response =
                restTemplate.exchange(
                    url, HttpMethod.GET,
                    null, InventoryResponse.class);
            return response.getBody();
        } catch (HttpClientErrorException e) {
            // Manual error handling per call
            log.error("Inventory error: {}", e.getMessage());
            throw new ServiceException("Inventory unavailable");
        }
        // No circuit breaker
        // No retry
        // No timeout configurable per-endpoint
    }
}
```

```java
// GOOD: Feign with Resilience4j
// Declarative: interface defines the contract
// Resilience4j: circuit breaker + retry from config
@FeignClient(
    name = "inventory-service",
    configuration = FeignConfig.class
)
public interface InventoryClient {
    
    @GetMapping("/api/v1/inventory/{sku}")
    InventoryResponse getInventory(
        @PathVariable("sku") String sku);
}

@Service
public class OrderService {
    private final InventoryClient inventoryClient;
    
    @CircuitBreaker(
        name = "inventoryService",
        fallbackMethod = "getInventoryFallback")
    @Retry(name = "inventoryService")
    public InventoryResponse checkInventory(String sku) {
        // One line. Feign generates the HTTP call.
        // Circuit breaker: from @CircuitBreaker
        // Retry: from @Retry
        // Timeout: from application.yaml
        return inventoryClient.getInventory(sku);
    }
    
    private InventoryResponse getInventoryFallback(
            String sku, Exception e) {
        log.warn("Inventory unavailable for {}", sku, e);
        return InventoryResponse.defaultUnavailable(sku);
    }
}
// Test: mock InventoryClient (just a Java interface)
// Production: Feign calls real service
// Circuit open: fallback called transparently
```

---

### ⚖️ Comparison Table

| Spring Cloud Component | Modern K8s Alternative | Keep or Replace |
|---|---|---|
| **Eureka** | Kubernetes DNS | Replace |
| **Ribbon** | K8s Service + Istio | Replace |
| **Spring Cloud Config** | ConfigMap + Vault/ESO | Replace |
| **Zuul (old gateway)** | Spring Cloud Gateway / Kong | Replace Zuul |
| **Spring Cloud Gateway** | Istio Gateway / Kong | Keep (if Spring-native preferred) |
| **OpenFeign** | None (language-specific) | Keep |
| **Resilience4j** | Istio DestinationRule (partial) | Keep (app-level) |
| **Sleuth** | Micrometer Tracing | Keep (updated) |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Spring Cloud and Kubernetes service discovery are compatible and complementary | Eureka (Spring Cloud) and Kubernetes DNS are redundant. If both are active: Feign resolves service names through Eureka (separate registry), ignoring Kubernetes DNS. On Kubernetes: if a pod restarts and re-registers with Eureka, there's a brief period where Eureka has the old IP. Kubernetes DNS: updated by the K8s control plane immediately. Keep one system: on Kubernetes, use K8s DNS (remove Eureka). Set `eureka.client.enabled=false` in Kubernetes deployments. |
| Resilience4j in the application replaces Istio circuit breaking | They operate at different layers and are complementary. Resilience4j: application-level, knows about business exceptions (retry on `InsufficientInventoryException`?), executes fallback logic (business-specific). Istio DestinationRule: network-level, knows about HTTP status codes (retry on 503), no business logic, applies uniformly. Use Resilience4j for: business-level retries, bulkhead per feature, application-level circuit breaking. Use Istio for: network-level retries (transparent), circuit breaking at transport layer. |
| Spring Cloud Config hot reload is the recommended approach for feature flags | Spring Cloud Config `@RefreshScope` + `/actuator/refresh`: works but has risks: (1) partial refresh (some instances refreshed, others not, until bus propagation completes); (2) refresh mutates state in running pods (harder to audit than immutable deployments); (3) not GitOps-compatible (config change not in a PR). Better: use a dedicated feature flag service (LaunchDarkly, Unleash) for runtime feature flags, and deploy-time config changes via GitOps (ArgoCD + ConfigMaps). |

---

### 🚨 Failure Modes & Diagnosis

**Eureka and K8s DNS conflict: stale service URLs**

**Symptom:**
After pod restart: some requests to order-service
fail with "Connection refused". The OLD pod IP
is in use. After 30 seconds: requests succeed
again. Pattern: pod restarts cause ~30 second
inconsistency window.

**Root Cause:**
Eureka and Kubernetes both active. Feign: uses
Eureka for service discovery (not K8s DNS). Eureka
cache: TTL 30 seconds. Pod restarts: Kubernetes
updates DNS immediately. But Eureka: keeps old
IP for up to 30 seconds (eviction timer). Feign:
routes to old IP -> connection refused.

**Fix:**
```yaml
# Disable Eureka on Kubernetes deployments
# application-kubernetes.yaml:
eureka:
  client:
    enabled: false  # use K8s DNS instead
  instance:
    prefer-ip-address: false

# Spring Cloud LoadBalancer: use K8s DNS
spring:
  cloud:
    loadbalancer:
      ribbon:
        enabled: false  # ensure ribbon is disabled
    discovery:
      enabled: false    # disable Eureka discovery
```

---

### 🔗 Related Keywords

**What Spring Cloud Gateway replaces:**
- `API Gateway` - Spring Cloud Gateway is an
  implementation of the API Gateway pattern

**What Spring Cloud complements:**
- `Service Mesh` - Istio operates at infrastructure
  level; Spring Cloud Resilience4j at app level
- `Circuit Breaker` - Resilience4j is the
  Spring implementation of the circuit breaker
- `Service Discovery` - Eureka (replaced by K8s
  DNS) is the Spring Cloud service registry

---

### 📌 Quick Reference Card

```
+--------------------------------------------------+
| KEEP (2025)  | OpenFeign (declarative REST)      |
|              | Resilience4j (app-level CB/retry) |
|              | Spring Cloud Gateway (if Spring)  |
|              | Micrometer Tracing (was Sleuth)   |
+--------------+-----------------------------------+
| REPLACE      | Eureka -> K8s DNS                 |
| WITH K8s     | Ribbon -> K8s Service + Istio     |
|              | Config Server -> ConfigMap + Vault|
+--------------+-----------------------------------+
| ONE-LINER    | "Pre-K8s microservices toolkit;   |
|              |  keep Feign+Resilience4j,         |
|              |  replace discovery+config"        |
+--------------------------------------------------+
```

**If you remember only 3 things:**
1. Keep in 2025: Spring Cloud Gateway (edge),
   OpenFeign (declarative HTTP client), Resilience4j
   (app-level circuit breaker). These have no
   equivalent in Kubernetes layer.
2. Replace with Kubernetes: Eureka (K8s DNS),
   Ribbon (K8s Services), Spring Cloud Config
   (ConfigMaps + Vault), Sleuth (Micrometer Tracing).
3. Feign + Resilience4j: the minimum useful Spring
   Cloud setup for new microservices on Kubernetes.
   `@FeignClient` interface + `@CircuitBreaker`
   annotation. Nothing else needed.

**Interview one-liner:**
"Spring Cloud Ecosystem: pre-K8s microservices
infrastructure for Java. Key components: Gateway
(API gateway with routing, rate limiting), OpenFeign
(declarative REST client - define interface with
@FeignClient, Spring generates implementation),
Resilience4j (circuit breaker + retry via @CircuitBreaker
+ @Retry annotations), Eureka (service registry -
replaced by K8s DNS in modern deployments). 2025
strategy: keep OpenFeign + Resilience4j + Gateway;
replace Eureka/Ribbon/Config Server with K8s-native
alternatives (DNS, Istio, ConfigMaps + Vault)."

---

### 💡 The Surprising Truth

The most valuable thing about OpenFeign is not
the HTTP client generation - it's the TESTABILITY.
With RestTemplate: to test a service that calls
order-service, you need to mock HTTP (WireMock,
MockWebServer). With Feign: the calling code
depends on `InventoryClient` (an interface). In
unit tests: just mock the interface (`Mockito.
when(inventoryClient.getInventory("SKU-1"))
.thenReturn(...)`). No HTTP server required. Test
is 10x faster. This testability benefit is available
to ALL Java developers and requires only
`spring-cloud-starter-openfeign` - no Kubernetes,
no Istio, nothing else. Even for teams not using
any other Spring Cloud component: Feign alone
is worth adding.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **FEIGN** Create a `@FeignClient` interface
   for 3 API calls to inventory-service. Add
   `@CircuitBreaker` + `@Retry` annotations.
   Write unit tests using Mockito to mock the
   Feign interface (no HTTP server needed).
2. **GATEWAY** Configure Spring Cloud Gateway
   with: path routing to 3 services, JWT auth
   filter (validate + reject invalid JWTs), Redis
   rate limiting (100 req/s per user), circuit
   breaker with fallback URL.
3. **RESILIENCE4J** Configure Resilience4j
   for `inventoryService`: circuit breaker (50%
   failure threshold, 10-request sliding window,
   30s wait in open state), retry (3 attempts,
   200ms fixed wait), bulkhead (max 20 concurrent
   calls). Verify behavior with Actuator metrics.
4. **K8S MIGRATION** Given an existing Spring Boot
   app using Eureka + Ribbon + Spring Cloud Config:
   write the migration plan to remove these three
   components and replace with Kubernetes DNS,
   Services, and ConfigMaps respectively.
5. **ARCHITECTURE** For a new Spring Boot microservice
   running on Kubernetes + Istio: decide which
   Spring Cloud components to include and which
   to skip. Justify each decision (Spring Cloud
   vs Kubernetes/Istio responsibility).

---

### 🧠 Think About This Before We Continue

**Q1.** Your team is migrating from a Eureka-based
Spring Cloud setup (15 services) to Kubernetes.
You want to disable Eureka for all 15 services
in one sprint. What is the migration risk? What
is the safer approach: disable Eureka across all
15 services simultaneously, or service by service?
How do you verify each service correctly resolves
other services via K8s DNS after Eureka is disabled?

**Q2.** Resilience4j circuit breaker and Istio
DestinationRule outlierDetection: both implement
circuit breaking. You have both active for
inventory-service calls. What happens when:
(a) inventory-service returns HTTP 503 for 5
consecutive requests; (b) the circuit opens at
both levels simultaneously; (c) inventory-service
recovers. Trace the state machine for both circuit
breakers and explain the interaction.

**Q3.** Your Spring Cloud Config Server stores
feature flags. Developers use `@RefreshScope` +
`/actuator/refresh` to toggle features without
redeployment. The CTO asks: "Is this a good
practice?" List 5 risks of this approach and
propose an alternative architecture that provides
runtime feature toggle capability with better
auditability, consistency, and GitOps compatibility.