---
layout: default
title: "Spring Cloud"
parent: "Spring Core"
grand_parent: "Technical Dictionary"
nav_order: 57
permalink: /spring/spring-cloud/
id: SPR-057
category: Spring Core
difficulty: ★★★
depends_on: Microservices, Service Discovery, Load Balancing
used_by: Distributed Systems, Cloud Deployments, API Gateway
related: Kubernetes, Consul, Eureka, Ribbon
tags:
  - spring
  - cloud
  - distributed
  - deep-dive
---

# SPR-057 - Spring Cloud

⚡ TL;DR - Spring Cloud provides building blocks for distributed systems - config server, service discovery, circuit breakers, distributed tracing, and API gateway - letting Spring Boot services compose into resilient microservices architectures.

| #409            | Category: Spring Core                               | Difficulty: ★★★ |
| :-------------- | :-------------------------------------------------- | :-------------- |
| **Depends on:** | Microservices, Service Discovery, Load Balancing    |                 |
| **Used by:**    | Distributed Systems, Cloud Deployments, API Gateway |                 |
| **Related:**    | Kubernetes, Consul, Eureka, Ribbon                  |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Your monolith is split into 20 microservices. Service A needs to call Service B, but B's IP changes on every deployment. You hardcode `http://10.0.1.45:8080` - it breaks after the next deploy. Solution: maintain a properties file per service with all downstream URLs. Now there are 20 × 19 = 380 service-to-service URLs to maintain. A configuration change requires redeployment of 20 services. When B is slow, A waits, causing cascading timeouts through the chain. There's no central configuration, no tracing across service boundaries, no intelligent routing.

**THE BREAKING POINT:**
Distributed systems have fundamentally different failure modes than monoliths: services come and go, IPs change, network partitions occur, partial failures cascade. Each of these requires dedicated infrastructure - not ad-hoc per-service solutions.

**THE INVENTION MOMENT:**
"This is exactly why Spring Cloud was created."

---

### 📘 Textbook Definition

**Spring Cloud** is an umbrella project providing tools and patterns for building distributed systems and microservices with Spring Boot. It integrates with service registries (Eureka, Consul, Kubernetes), provides externalized configuration (`Spring Cloud Config`), implements resilience patterns (`Spring Cloud Circuit Breaker` via Resilience4j), API gateway routing (`Spring Cloud Gateway`), client-side load balancing (`Spring Cloud LoadBalancer`), and distributed tracing (`Micrometer Tracing` / Zipkin). Spring Cloud builds on Spring Boot's auto-configuration model - each component activates by adding the corresponding starter and minimal configuration. The project has evolved significantly: Netflix OSS components (Ribbon, Hystrix, Zuul) are now in maintenance mode, replaced by Spring-native alternatives.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Spring Cloud gives your Spring Boot microservices the infrastructure they need to find each other, talk resiliently, share config, and be observable.

**One analogy:**

> Spring Cloud is like the logistics infrastructure of a city: postal addresses (service discovery), a city-wide announcement board for rules changes (config server), traffic signals and roundabouts (load balancer), roadblocks when streets are flooded (circuit breaker), and GPS tracking for every delivery truck (distributed tracing). Without this infrastructure, a city of 20 buildings can't communicate reliably.

**One insight:**
Spring Cloud doesn't replace Kubernetes or cloud-native infrastructure - it complements it by providing application-level patterns (circuit breakers, config propagation, trace context) that infrastructure alone cannot provide.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Service discovery decouples service location from IP/port - clients ask the registry "where is Service B?" rather than hardcoding addresses.
2. Externalized configuration separates config from code - all services read from one config server; a property change requires no redeployment.
3. Circuit breakers prevent cascading failures - if Service B fails, Service A fails fast rather than queuing up thread-blocking waits.

**DERIVED DESIGN:**
Service discovery solves the dynamic IP problem: services register their address at startup (Eureka, Consul, Kubernetes Service) and clients query the registry. The registry handles deregistration on shutdown. Combined with client-side load balancing (`LoadBalancerClient`), a client resolves "service-b" to one of its healthy instances and distributes load across them.

The Config Server solves config management across 20 services: one Git repository holds all `application.yml` files; services fetch their config on startup (and optionally refresh without restart via `/actuator/refresh`). This centralizes audit, versioning, and environment-specific overrides.

Circuit breakers (Resilience4j) solve the cascading failure problem: after N failures in a window, the circuit opens - subsequent calls fail immediately (fast failure) rather than waiting for timeout. The circuit attempts to half-open after a cooldown period to check if the downstream recovered.

**THE TRADE-OFFS:**
**Gain:** Resilient service-to-service communication; centralized config; distributed tracing across service boundaries; standardized patterns across all microservices.
**Cost:** Operational complexity - the infrastructure services (config server, service registry, gateway) must themselves be highly available; distributed tracing requires all services to propagate trace headers; misconfigurations in centralized config can affect all services simultaneously.

---

### 🧪 Thought Experiment

**SETUP:**
A payment service depends on a fraud-check service. Fraud-check starts responding slowly (2s per check, normal is 50ms). Your load: 100 requests/second to payment service, each spawning 1 fraud-check call. Thread pool: 50 threads.

**WITHOUT CIRCUIT BREAKER:**
Each of the 100 req/s spawns a fraud-check call that takes 2s. 100 req/s × 2s = 200 requests waiting concurrently. 50 thread pool fills in <1s. Subsequent requests queue up or fail with thread pool exhaustion. Payment service becomes completely unresponsive even though the fraud-check slowdown doesn't affect 80% of orders. Cascading failure: payment service is now DOWN because fraud-check is SLOW.

**WITH CIRCUIT BREAKER:**
After 5 failures/slowness events, circuit opens. Subsequent fraud-check calls fail immediately (configured fallback: "approve order, flag for manual review later"). Payment service continues processing. Resilience4j checks fraud-check every 30s (half-open). Once recovered, circuit closes - fraud checks resume. System degraded gracefully; not down.

**THE INSIGHT:**
Failing fast is better than waiting forever. A circuit breaker converts "slow downstream" into "fast failure with fallback" - saving threads and response time budget throughout the call chain.

---

### 🧠 Mental Model / Analogy

> Spring Cloud is like the control tower and infrastructure of an airline hub. The flight registry (service discovery) knows where all planes (services) are parked. The centralized operations manual (config server) governs all gates - update the manual once, all gates adjust. When a runway is flooded (service down), the control tower diverts flights to another runway (load balancing) or tells aircraft to hold short (circuit breaker). Flight trackers log every aircraft's path across all airports (distributed tracing).

- "Flight registry" → service discovery (Eureka/Consul/K8s)
- "Centralized operations manual" → Spring Cloud Config Server
- "Diverting to another runway" → client-side load balancing
- "Hold short during runway closure" → circuit breaker open state
- "Flight tracking across airports" → distributed tracing (Zipkin/Micrometer)

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Spring Cloud is a collection of tools that helps Spring Boot services find each other, share settings, handle failures gracefully, and track requests as they flow through many services.

**Level 2 - How to use it (junior developer):**
Add `spring-cloud-starter-*` dependencies for the features you need. For Kubernetes-native service discovery: use Kubernetes `Service` resources and `spring-cloud-starter-kubernetes-client`. For config: add `spring-cloud-starter-config` and point to your Config Server URL. For circuit breakers: add `spring-cloud-starter-circuitbreaker-resilience4j` and annotate service calls with `@CircuitBreaker`. For gateway: configure routes in `application.yml` with `spring.cloud.gateway.routes`.

**Level 3 - How it works (mid-level engineer):**
`Spring Cloud LoadBalancer` (replacement for Netflix Ribbon) integrates with `WebClient` and `RestTemplate` via a `ReactiveLoadBalancer` or `BlockingLoadBalancer`. When a request is made to a logical service name (e.g., `http://fraud-service/check`), the `LoadBalancerInterceptor` intercepts the call, queries the `ServiceInstanceListSupplier` (backed by the service registry), applies the load balancing strategy (round-robin by default), resolves to a concrete IP:port, and sends the request. Resilience4j circuit breaker state is tracked per service pair using a `CircuitBreakerRegistry`; state changes publish events that can be monitored via Micrometer. Distributed tracing works by propagating `traceId` and `spanId` headers (`traceparent` in W3C format) through every outbound HTTP call via `WebClient` filters or `RestTemplate` interceptors.

**Level 4 - Why it was designed this way (senior/staff):**
Spring Cloud's architectural pivot from Netflix OSS (Ribbon, Hystrix, Zuul, Eureka) to Spring-native and Kubernetes-native components reflects a fundamental shift in deployment target. Netflix OSS was designed for AWS EC2 in 2012 - static IP VMs, no Kubernetes, no container orchestration. By 2020, most new deployments are Kubernetes where service discovery, load balancing, and health-checking are handled by the platform. Spring Cloud's response: lean on Kubernetes for infrastructure concerns and provide application-level patterns (circuit breaking, distributed tracing, config) that the platform doesn't provide. Spring Cloud Gateway (Netty-based, non-blocking) replaced Zuul (servlet-based, blocking) to handle the scale requirements of modern API gateways without dedicated thread pools.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────────────────┐
│ SPRING CLOUD: KEY COMPONENT INTERACTIONS                │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Config Server (Git-backed)                             │
│    ↑ fetch config at startup                            │
│    ↑ refresh config on demand                           │
│  All Microservices ────────────────────────────────────┤
│                                                         │
│  Service Registry (Eureka / Consul / K8s)               │
│    ← register on startup, heartbeat every 30s           │
│    ← deregister on shutdown                             │
│    → query registry for service instances              │
│                                                         │
│  Payment Service calls Fraud Service:                   │
│    1. WebClient("http://fraud-service/check")           │
│    2. LoadBalancerInterceptor intercepts                │
│    3. ServiceInstanceListSupplier queries registry      │
│       → [fraud-service:10.0.1.5:8080,                  │
│           fraud-service:10.0.1.6:8080]                  │
│    4. RoundRobin selects 10.0.1.5:8080                  │
│    5. CircuitBreakerFilter checks state                 │
│       → CLOSED: execute call                            │
│       → OPEN: fail fast, call fallback                  │
│    6. TracingFilter adds traceparent header             │
│    7. Actual HTTP call to 10.0.1.5:8080                │
│                                                         │
│  Distributed Tracing:                                   │
│    traceId=abc123 propagated to all downstream calls   │
│    → collected by Zipkin / Jaeger / Grafana Tempo       │
└─────────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Spring Cloud Config Server setup:**

```java
// Config Server application
@SpringBootApplication
@EnableConfigServer
public class ConfigServerApplication {
    public static void main(String[] args) {
        SpringApplication.run(
            ConfigServerApplication.class, args);
    }
}
```

```yaml
# Config Server: application.yml
spring:
  cloud:
    config:
      server:
        git:
          uri: https://github.com/myorg/app-config
          default-label: main
          search-paths: "{application}"
server:
  port: 8888
```

```yaml
# Client microservice: bootstrap.yml (or application.yml)
spring:
  config:
    import: "configserver:http://config-server:8888"
  application:
    name: payment-service # loads payment-service.yml from Git
```

**Example 2 - Circuit breaker with Resilience4j:**

```java
@Service
public class PaymentService {

    private final WebClient webClient;
    private final CircuitBreakerFactory cbFactory;

    public PaymentService(WebClient.Builder builder,
            CircuitBreakerFactory cbFactory) {
        this.webClient = builder
            .baseUrl("http://fraud-service").build();
        this.cbFactory = cbFactory;
    }

    public FraudCheckResult checkFraud(Order order) {
        CircuitBreaker cb =
            cbFactory.create("fraud-check-cb");

        return cb.run(
            // Primary call
            () -> webClient.post()
                .uri("/check")
                .bodyValue(order)
                .retrieve()
                .bodyToMono(FraudCheckResult.class)
                .block(),
            // Fallback when circuit is open
            throwable -> {
                log.warn("Fraud check unavailable: {}",
                    throwable.getMessage());
                return FraudCheckResult.FLAG_FOR_REVIEW;
            }
        );
    }
}
```

```yaml
# application.yml - circuit breaker config
resilience4j:
  circuitbreaker:
    instances:
      fraud-check-cb:
        sliding-window-size: 10
        failure-rate-threshold: 50 # open at 50% failure
        wait-duration-in-open-state: 30s
        permitted-calls-in-half-open-state: 3
```

**Example 3 - Spring Cloud Gateway routing:**

```yaml
# API Gateway: application.yml
spring:
  cloud:
    gateway:
      routes:
        - id: payment-route
          uri: lb://payment-service # lb:// = load balanced
          predicates:
            - Path=/api/payments/**
          filters:
            - StripPrefix=1
            - name: CircuitBreaker
              args:
                name: paymentCB
                fallbackUri: forward:/fallback/payment

        - id: order-route
          uri: lb://order-service
          predicates:
            - Path=/api/orders/**
          filters:
            - AddRequestHeader=X-Request-Source, gateway
            - name: RequestRateLimiter
              args:
                redis-rate-limiter.replenishRate: 100
                redis-rate-limiter.burstCapacity: 200
```

---

### ⚖️ Comparison Table

| Component             | Netflix OSS (Legacy) | Spring Cloud (Current)    | Cloud-Native K8s    |
| --------------------- | -------------------- | ------------------------- | ------------------- |
| **Service Discovery** | Eureka               | Kubernetes Service        | Kubernetes Service  |
| **Load Balancing**    | Ribbon               | Spring Cloud LoadBalancer | kube-proxy          |
| **Circuit Breaker**   | Hystrix (deprecated) | Resilience4j              | Istio (sidecar)     |
| **API Gateway**       | Zuul (deprecated)    | Spring Cloud Gateway      | Ingress / API GW    |
| **Config**            | Config Server        | Config Server             | ConfigMap / Secrets |
| **Tracing**           | Sleuth (deprecated)  | Micrometer Tracing        | OpenTelemetry       |

How to choose: On Kubernetes, prefer Kubernetes-native service discovery and load balancing over Spring Cloud's registry-based approach. Use Spring Cloud for application-level concerns (circuit breakers, config management, distributed tracing) that Kubernetes doesn't provide natively.

---

### ⚠️ Common Misconceptions

| Misconception                                                    | Reality                                                                                                                                                                                 |
| ---------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Spring Cloud replaces Kubernetes                                 | They're complementary: K8s handles infrastructure concerns (scheduling, networking, scaling); Spring Cloud handles application concerns (circuit breaking, distributed tracing, config) |
| Netflix OSS components (Ribbon, Hystrix) are actively maintained | Netflix OSS is in maintenance mode; Resilience4j replaces Hystrix; Spring Cloud LoadBalancer replaces Ribbon                                                                            |
| `lb://service-name` works without service discovery configured   | It requires a `ServiceInstanceListSupplier` - either Eureka client, Consul client, or Kubernetes client on the classpath                                                                |
| Config Server changes apply immediately                          | By default, `@RefreshScope` beans refresh on `/actuator/refresh` POST; for auto-refresh use Spring Cloud Bus with a message broker                                                      |
| Spring Cloud Gateway is just a proxy                             | Spring Cloud Gateway is a full reactive API gateway with filters, rate limiting, circuit breaking, authentication, and routing - far beyond a reverse proxy                             |

---

### 🚨 Failure Modes & Diagnosis

**1. Circuit Breaker Permanently Open (Cascading)**

**Symptom:** All calls to Service B from Service A fail immediately with `CallNotPermittedException`; even when Service B is healthy, the circuit stays open.

**Root Cause:** `wait-duration-in-open-state` is too long, or the half-open trial calls also fail (Service B is partially healthy), keeping the circuit open. Or the circuit was manually opened and not reset.

**Diagnostic:**

```bash
# Check circuit breaker state via Actuator
curl http://localhost:8080/actuator/circuitbreakers | \
  python -m json.tool

# Check Resilience4j metrics
curl http://localhost:8080/actuator/metrics/\
  resilience4j.circuitbreaker.state

# Manually force close (emergency)
curl -X POST http://localhost:8080/actuator/\
  circuitbreakers/fraud-check-cb/disable
```

**Fix:**

```yaml
# Tune retry and half-open parameters
resilience4j:
  circuitbreaker:
    instances:
      fraud-check-cb:
        permitted-calls-in-half-open-state: 5 # more trials
        wait-duration-in-open-state: 10s # shorter wait
        slow-call-duration-threshold: 2s # define "slow"
        slow-call-rate-threshold: 80 # 80% slow = open
```

---

**2. Config Server Single Point of Failure**

**Symptom:** Config Server goes down; all new pod startups fail with `Could not resolve placeholder` or `Connection refused to config server`; existing running pods are unaffected.

**Root Cause:** Services configured to fail-fast on config server unavailability and no fallback local config.

**Diagnostic:**

```bash
kubectl get pods | grep config-server
kubectl logs config-server-xxx
```

**Fix:**

```yaml
# Client: tolerate config server unavailability at startup
spring:
  cloud:
    config:
      fail-fast: false # don't crash on unavail
      retry:
        initial-interval: 1000
        max-attempts: 6
        max-interval: 2000

# Provide local fallback in src/main/resources/
# application.yml will be used if config server unreachable
```

**Prevention:** Run Config Server as HA (multiple replicas behind a load balancer); use local config files as fallback.

---

**3. Service Discovery Stale Registration**

**Symptom:** Load balancer routes requests to an IP that returns connection refused; the service instance was terminated but still registered in the registry.

**Root Cause:** Service shutdown without graceful deregistration (SIGKILL instead of graceful stop), or Eureka's heartbeat deregistration lag (up to 90 seconds by default).

**Diagnostic:**

```bash
# Check registered instances in Eureka
curl http://eureka:8761/eureka/apps/PAYMENT-SERVICE

# Compare with actual running pods
kubectl get pods -l app=payment-service

# Check deregistration timeout
# eureka.instance.lease-expiration-duration-in-seconds (default 90)
```

**Fix:**

```yaml
# Reduce deregistration lag (dev/test)
eureka:
  instance:
    lease-renewal-interval-in-seconds: 10
    lease-expiration-duration-in-seconds: 30
  client:
    registry-fetch-interval-seconds: 10

# Better solution: use Kubernetes service discovery
# K8s endpoints update within ~1s of pod termination
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Microservices` - Spring Cloud is the Spring ecosystem's answer to microservices infrastructure challenges
- `Service Discovery` - the foundational pattern Spring Cloud builds on for dynamic service location
- `Load Balancing` - Spring Cloud LoadBalancer implements client-side load balancing

**Builds On This (learn these next):**

- `Distributed Systems` - Spring Cloud implements patterns (circuit breaker, distributed tracing) described in distributed systems theory
- `Kubernetes` - the deployment platform that handles many of the infrastructure concerns Spring Cloud also addresses
- `Observability & SRE` - distributed tracing (Spring Cloud's Micrometer Tracing integration) is central to SRE practice

**Alternatives / Comparisons:**

- `Istio service mesh` - infrastructure-level circuit breaking, load balancing, and tracing via sidecar proxies; complements but doesn't replace Spring Cloud
- `Netflix OSS (legacy)` - the predecessor; Eureka and Hystrix still work but are in maintenance mode
- `Quarkus SmallRye` - Quarkus ecosystem equivalent for microservices patterns

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Building blocks for Spring Boot           │
│              │ distributed systems / microservices       │
├──────────────┼───────────────────────────────────────────┤
│ KEY          │ Config Server: central config in Git      │
│ COMPONENTS   │ LoadBalancer: lb://service-name routing   │
│              │ Circuit Breaker: Resilience4j integration │
│              │ Gateway: reactive API gateway + routing   │
│              │ Tracing: Micrometer → Zipkin/Tempo        │
├──────────────┼───────────────────────────────────────────┤
│ MODERN       │ Resilience4j (not Hystrix)                │
│ CHOICES      │ Spring Cloud LoadBalancer (not Ribbon)    │
│              │ Gateway (not Zuul)                        │
│              │ Micrometer Tracing (not Sleuth)           │
├──────────────┼───────────────────────────────────────────┤
│ K8s PATTERN  │ Use K8s for network/discovery; use        │
│              │ Spring Cloud for app-level resilience     │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Resilience and observability vs.          │
│              │ operational complexity of infra services  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Spring Cloud is the city infrastructure  │
│              │  that lets microservices work together"   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Distributed Systems → Kubernetes →        │
│              │ Observability & SRE                       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE B - Scale) Your organization runs 50 microservices, all reading configuration from a Spring Cloud Config Server backed by a single Git repository. A DevOps engineer commits an invalid YAML file to the config repo. Describe the exact blast radius: which services are immediately affected, which services are affected only on their next restart, and which services are fully immune. What governance mechanism prevents this from happening?

**Q2.** (TYPE E - Architecture) An Istio service mesh is installed in your Kubernetes cluster, providing circuit breaking, load balancing, and distributed tracing at the infrastructure level. A team lead proposes removing Spring Cloud Circuit Breaker (Resilience4j) from all 30 microservices, arguing "Istio does the same thing." Is this safe? Identify the one scenario where Istio circuit breaking cannot protect you but Resilience4j can - specifically related to connection vs. application-level failure semantics.
