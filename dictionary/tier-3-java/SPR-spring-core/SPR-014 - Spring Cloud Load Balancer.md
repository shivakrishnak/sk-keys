---
layout: default
title: "Spring Cloud Load Balancer"
parent: "Spring Core"
grand_parent: "Technical Dictionary"
nav_order: 14
permalink: /spring/spring-cloud-load-balancer/
id: SPR-014
category: Spring Core
difficulty: ★★★
depends_on: Spring Cloud Service Discovery (Eureka), Spring Cloud Overview, Load Balancing
used_by: Spring Cloud Gateway, Microservices
related: Ribbon (deprecated), Kubernetes Load Balancer, AWS ALB
tags:
  - java
  - spring
  - microservices
  - networking
  - advanced
---

# SPR-014 - Spring Cloud Load Balancer

⚡ TL;DR - Spring Cloud Load Balancer distributes outbound HTTP calls across discovered service instances using pluggable strategies with automatic retry support.

| Field | Value |
|---|---|
| **Depends on** | Spring Cloud Service Discovery (Eureka), Spring Cloud Overview, Load Balancing |
| **Used by** | Spring Cloud Gateway, Microservices |
| **Related** | Ribbon (deprecated), Kubernetes Load Balancer, AWS ALB |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** Your `order-service` discovers 4 instances of `inventory-service` via Eureka. You call `http://inventory-service/check`. Which instance handles it? Without a load balancer, the answer is "whichever one the DNS resolver returns" - typically always the first one. Three instances sit idle while one drowns.

**THE BREAKING POINT:** Client-side discovery exposes all available instances to the caller, but calling all of them simultaneously is wrong. You need to *choose* one, *track* success rates, *retry* on failure, and *favour* nearby instances. None of that is in Eureka; Eureka only provides the list.

**THE INVENTION MOMENT:** Netflix's **Ribbon** library filled this gap from 2013. When Spring Cloud deprecated Ribbon in 2020 (unmaintained, blocking I/O, incompatible with reactive stacks), the Spring team built **Spring Cloud Load Balancer** - a lightweight, reactive-first replacement integrated directly into `WebClient` and `RestClient`.

---

### 📘 Textbook Definition

**Spring Cloud Load Balancer (SCLB)** is a client-side load-balancing abstraction in the Spring Cloud Commons library. It integrates with service discovery (Eureka, Consul, Kubernetes) to retrieve live instance lists, applies a configurable algorithm to select one instance per request, and optionally retries on transient failures. It supports both blocking (`RestTemplate`) and non-blocking (`WebClient`, `RestClient`) HTTP clients via `@LoadBalanced` qualifier injection.

---

### ⏱️ Understand It in 30 Seconds

**One line:** A client-embedded router that picks one healthy instance from a discovered list for every outbound call.

> "SCLB is the traffic controller at a toll plaza: it knows exactly how many booths are open (instance list from Eureka), counts the cars in each queue (active connections), and waves each new car to the shortest queue."

**One insight:** Unlike server-side load balancers (AWS ALB, Nginx), SCLB runs inside the calling JVM. This eliminates a network hop and lets the algorithm use call-result history the central LB cannot see.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. A load balancer must have an up-to-date list of available instances.
2. Selection must be deterministic enough to be predictable but distributed enough to spread load.
3. Failed instances must be detected through call results, not just heartbeats.
4. Retries must avoid the same failed instance to prevent amplifying failures.

**DERIVED DESIGN:**
- `ServiceInstanceListSupplier` - pulls instance lists from any discovery source.
- `ReactorLoadBalancer<ServiceInstance>` - stateless function: list → one instance.
- `@LoadBalanced` `WebClient.Builder` - wraps every HTTP call with `ReactorLoadBalancerExchangeFilterFunction`.
- Caching supplier with a configurable TTL prevents per-request registry polls.

**THE TRADE-OFFS:**

**Gain:** No extra network hop; algorithm has access to per-call telemetry; reactive-first design; zero dependency on legacy Ribbon.

**Cost:** Every JVM carries its own load-balancer state. If 50 instances of `order-service` each make independent choices, aggregate load distribution may be less uniform than a centralised balancer with global visibility.

---

### 🧪 Thought Experiment

**SETUP:** You have `payment-service` with 3 instances. Instance 3 is running on a degraded host - it responds in 2 s instead of 20 ms. Without a load balancer, all 3 IPs are returned by Eureka. Your caller picks one at random each time.

**WHAT HAPPENS WITHOUT SCLB:** 33% of requests hit instance 3 and stall for 2 s. The caller's connection pool fills with in-flight requests. Thread exhaustion follows. The degraded single instance cascades into a full outage for the caller.

**WHAT HAPPENS WITH SCLB:** With `HealthCheckServiceInstanceListSupplier`, instance 3 fails active health checks and is filtered from the list. Round-robin distributes across the healthy 2. When zone-aware routing is enabled, instances in the same AZ are preferred - latency drops further. With retry configured, a first call to a slow instance triggers a retry on a different instance, capping worst-case latency.

**THE INSIGHT:** Client-side load balancing turns discovery (a list) into routing (a choice based on health and locality). The discovery layer alone cannot do this.

---

### 🧠 Mental Model / Analogy

> "SCLB is an Uber driver app that knows which drivers are available (Eureka list), filters out drivers with bad ratings (health check), picks the nearest one (zone-affinity), and if that driver cancels, immediately books the next best without asking you again (retry with backoff)."

- **Uber app = SCLB embedded in WebClient** - logic lives with the caller.
- **Available drivers = ServiceInstance list from Eureka** - polled periodically.
- **Driver rating filter = HealthCheckServiceInstanceListSupplier** - removes sick instances.
- **Nearest driver = zone-affinity selector** - prefers same-AZ instances.
- **Cancellation retry = Spring Retry / Resilience4j retry** - transparent re-attempt on different instance.

Where this analogy breaks down: Uber has global visibility across all passengers; SCLB in each JVM has only per-process call history - aggregate distribution may be uneven under bursty load.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
When your code calls `http://payment-service/charge`, SCLB asks Eureka "who is payment-service?", gets a list of 3 servers, picks one, and makes the real call. Next request, it might pick a different one. This prevents any single server from being overwhelmed.

**Level 2 - How to use it (junior developer):**
Add `spring-cloud-starter-loadbalancer` to `pom.xml`. Annotate your `WebClient.Builder` bean with `@LoadBalanced`. Use service names in URLs: `http://payment-service/charge`. The balancer resolves the name to a real IP automatically. Configure retries in `application.yml` via `spring.cloud.loadbalancer.retry`.

**Level 3 - How it works (mid-level engineer):**
`@LoadBalanced` registers `ReactorLoadBalancerExchangeFilterFunction` (RLBEFF) as an exchange filter. On each request, RLBEFF extracts the service name from the URL host, calls `ReactorLoadBalancer.choose(request)`, which delegates to the registered `ServiceInstanceListSupplier` for the live list and applies the algorithm (default: `RoundRobinLoadBalancer`). The chosen `ServiceInstance` URL replaces the logical URL. The modified request proceeds through the filter chain to the actual HTTP transport.

**Level 4 - Why it was designed this way (senior/staff):**
SCLB is intentionally minimal and composable. The `ServiceInstanceListSupplier` chain is a decorator pattern: `DiscoveryClientServiceInstanceListSupplier` → `CachingServiceInstanceListSupplier` (TTL 35 s) → `HealthCheckServiceInstanceListSupplier` → `ZonePreferenceServiceInstanceListSupplier`. Each decorator adds one concern. This allows teams to swap out individual layers without reimplementing the whole stack. The `ReactorLoadBalancer` interface is a single method returning `Mono<Response<ServiceInstance>>` - making it trivially testable and mockable. This design reflects the Spring Cloud team's lesson from Ribbon: monolithic libraries age poorly.

---

### ⚙️ How It Works (Mechanism)

```
WebClient call: POST http://payment-service/charge
        │
        ▼
ReactorLoadBalancerExchangeFilterFunction
        │
        ├─► Extract service name: "payment-service"
        │
        ├─► ServiceInstanceListSupplier chain:
        │     DiscoveryClientSupplier
        │       └─ CachingSupplier (TTL 35 s)
        │           └─ HealthCheckSupplier
        │               └─ ZonePreferenceSupplier
        │     Returns: [inst-A:8081, inst-B:8081]
        │
        ├─► RoundRobinLoadBalancer.choose()
        │     Counter: 7 → 7 % 2 = 1 → inst-B
        │
        ├─► Reconstruct URL:
        │     http://10.0.1.22:8081/charge
        │
        └─► Forward to HTTP transport layer
```

**RoundRobinLoadBalancer internals:**
```
AtomicInteger position = new AtomicInteger(random.nextInt(1000))
chosen = instances.get(Math.abs(pos.incrementAndGet()) % instances.size())
```

**Zone-affinity:** `ZonePreferenceServiceInstanceListSupplier` reads `eureka.instance.metadata-map.zone` from both the local instance and each candidate, filtering to same-zone first with a fallback to all instances if no same-zone instances exist.

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
order-service (startup)
  │
  ├─► Fetch instance list from Eureka (via DiscoveryClient)
  ├─► Cache for 35 s (CachingSupplier)
  │
order-service handles HTTP request
  │
  ├─► WebClient POST http://payment-service/charge
  │     │
  │     ├─► RLBEFF intercepts              ← YOU ARE HERE
  │     ├─► Supplier returns [inst-A, inst-B]
  │     ├─► RoundRobin selects inst-A
  │     ├─► Rewrites URL → http://10.0.1.21:8081/charge
  │     └─► Real HTTP call to inst-A
  │
  └─► Response flows back through filter chain
```

**FAILURE PATH:**
- inst-A returns 500 or connection refused.
- If `spring.cloud.loadbalancer.retry.enabled=true`, SCLB retries on inst-B (next-instance retry).
- If all instances fail, `ReactorLoadBalancer` returns `Response.failed()`.
- `WebClient` propagates the exception; circuit breaker upstream catches it.

**WHAT CHANGES AT SCALE:**
- Cache TTL (35 s default) becomes critical: too short → registry flood; too long → stale instances routed.
- Health-check supplier adds one extra HTTP call per instance per interval - at 500+ instances this creates probe overhead.
- Zone-affinity is mandatory in multi-AZ deployments to avoid cross-AZ data transfer costs and latency.

---

### 💻 Code Example

**BAD - no load balancing, single hardcoded instance:**
```java
@Configuration
public class WebClientConfig {
    @Bean
    public WebClient webClient() {
        // No @LoadBalanced - bypasses SCLB entirely
        return WebClient.builder()
            .baseUrl("http://10.0.1.21:8081")
            .build();
    }
}
```

**GOOD - load-balanced WebClient with retry and zone-affinity:**
```java
// Build configuration
@Configuration
public class WebClientConfig {

    @Bean
    @LoadBalanced
    public WebClient.Builder loadBalancedWebClientBuilder() {
        return WebClient.builder();
    }
}

// Service using logical service name
@Service
public class OrderService {
    private final WebClient.Builder webClientBuilder;

    public Mono<PaymentResult> charge(Order order) {
        return webClientBuilder.build()
            .post()
            .uri("http://payment-service/charge")
            .bodyValue(order)
            .retrieve()
            .bodyToMono(PaymentResult.class);
    }
}
```
```yaml
# application.yml - SCLB configuration
spring:
  cloud:
    loadbalancer:
      retry:
        enabled: true
        max-retries-on-same-service-instance: 0
        max-retries-on-next-service-instance: 2
        retryable-status-codes: 500, 502, 503
      cache:
        ttl: 35s
        capacity: 256
      zone-preferences:
        enabled: true

# Declare instance zone in metadata
eureka:
  instance:
    metadata-map:
      zone: us-east-1a
```
```java
// Custom weighted load balancer (advanced)
public class WeightedLoadBalancer
        implements ReactorServiceInstanceLoadBalancer {

    private final ServiceInstanceListSupplier supplier;

    @Override
    public Mono<Response<ServiceInstance>> choose(Request request) {
        return supplier.get(request)
            .next()
            .map(instances -> {
                if (instances.isEmpty()) {
                    return new EmptyResponse();
                }
                // Weight by metadata: weight=2 gets 2x traffic
                List<ServiceInstance> weighted = instances.stream()
                    .flatMap(i -> Collections.nCopies(
                        Integer.parseInt(
                          i.getMetadata().getOrDefault("weight","1")),
                        i).stream())
                    .collect(toList());
                int idx = ThreadLocalRandom.current()
                    .nextInt(weighted.size());
                return new DefaultResponse(weighted.get(idx));
            });
    }
}

// Register the custom balancer
@Configuration
@LoadBalancerClient(
    name = "payment-service",
    configuration = WeightedLoadBalancerConfig.class
)
public class AppConfig {}

@Configuration
class WeightedLoadBalancerConfig {
    @Bean
    ReactorServiceInstanceLoadBalancer weightedBalancer(
            Environment env,
            LoadBalancerClientFactory factory) {
        String name = env.getProperty(
            LoadBalancerClientFactory.PROPERTY_NAME);
        return new WeightedLoadBalancer(
            factory.getLazyProvider(name,
                ServiceInstanceListSupplier.class));
    }
}
```

---

### ⚖️ Comparison Table

| Feature | Spring Cloud LB | Ribbon (deprecated) | Nginx (server-side) | AWS ALB |
|---|---|---|---|---|
| **Placement** | Client JVM | Client JVM | Sidecar/server | Network |
| **Reactive** | Yes (Reactor) | No (blocking) | N/A | N/A |
| **Discovery** | Pluggable | Eureka-only | Static upstream | Target group |
| **Algorithms** | Round-robin, custom | Round-robin, weighted | RR, least-conn, IP hash | RR, least-outstanding |
| **Health check** | Active HTTP probe | Passive (ping) | Active + passive | ALB health check |
| **Retry** | Yes, configurable | Yes | Yes | No (re-route on fail) |
| **Zone-affinity** | Yes | Yes | Manual | AZ-aware routing |
| **Maintenance** | Active | Abandoned (2020) | Active | Managed (AWS) |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "SCLB replaces Ribbon feature-for-feature" | SCLB is intentionally simpler. Features like per-server stats tracking and dynamic rule evaluation from Ribbon were not ported - use Resilience4j for those concerns. |
| "@LoadBalanced works on any bean" | It only works on `WebClient.Builder`, `RestTemplate` (blocking), and `RestClient.Builder`. The annotation registers the RLBEFF filter; it is meaningless on other beans. |
| "Retry on same instance is safe" | Retrying the same instance that just returned 500 is almost always counterproductive. Always set `max-retries-on-same-service-instance=0` and retry only on next instances. |
| "SCLB and API Gateway load balancers conflict" | They operate at different scopes. SCLB balances service-to-service calls inside the cluster. An API gateway balances external → service-tier traffic. Both can coexist. |
| "Zone-affinity breaks cross-zone redundancy" | It doesn't. Zone preference is a soft preference: if no same-zone instances are healthy, SCLB falls back to all instances. Redundancy is preserved. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1 - All traffic goes to one instance (no balancing)**

**Symptom:** Metrics show one instance at 100% CPU; others idle. Logs show all requests from `order-service` hitting the same IP.

**Root Cause:** `@LoadBalanced` was not applied to the `WebClient.Builder` bean; or the bean is constructed via `new WebClient.Builder()` instead of injected - bypassing Spring's AOP enhancement.

**Diagnostic:**
```bash
# Confirm filter is registered on the WebClient
curl -s http://order-service:8080/actuator/beans \
  | jq '.. | .aliases? // empty' | grep -i loadbalancer

# Check which IPs requests actually reach
curl -s http://order-service:8080/actuator/metrics \
  | jq '.names[]' | grep http.client
```

**Fix:**
```java
// BAD - bypasses spring injection; no @LoadBalanced
WebClient client = WebClient.builder()
    .baseUrl("http://payment-service").build();

// GOOD - inject the @LoadBalanced builder
@Autowired
private WebClient.Builder loadBalancedBuilder;

WebClient client = loadBalancedBuilder
    .baseUrl("http://payment-service").build();
```

**Prevention:** Enforce via ArchUnit: assert no `new WebClient.Builder()` call exists in service classes.

---

**Mode 2 - Retries amplify load on a degraded service**

**Symptom:** A downstream service is at 90% capacity. Enabling retries causes request volume to spike 3×, crashing the downstream service.

**Root Cause:** `max-retries-on-next-service-instance=2` means each failed request triggers 2 extra attempts. Under load, this multiplies traffic by 3×.

**Diagnostic:**
```bash
# Observe retry counter in actuator metrics
curl -s http://order-service:8080/actuator/metrics/\
spring.cloud.loadbalancer.requests.failed
# Watch HTTP client request counts trend
```

**Fix:**
```yaml
# BAD - aggressive retry with no backoff
spring.cloud.loadbalancer.retry:
  enabled: true
  max-retries-on-next-service-instance: 3

# GOOD - conservative retry with circuit breaker integration
spring.cloud.loadbalancer.retry:
  enabled: true
  max-retries-on-same-service-instance: 0
  max-retries-on-next-service-instance: 1
  retryable-status-codes: 502, 503
# Pair with circuit breaker to stop retrying after threshold
```

**Prevention:** Always pair SCLB retry with a circuit breaker. Retry handles transient failures; circuit breaker prevents retry storms.

---

**Mode 3 - Cross-AZ latency spikes (zone-affinity not configured)**

**Symptom:** p99 latency is 3× higher than expected. Traces show service-to-service calls going cross-region.

**Root Cause:** Zone-affinity is disabled (default). In a multi-AZ cluster, round-robin distributes evenly across all instances regardless of AZ. 33% of calls cross AZ boundaries, adding 10–30 ms network latency.

**Diagnostic:**
```bash
# Inspect instance zones from Eureka dashboard
curl -s http://localhost:8761/eureka/apps/PAYMENT-SERVICE \
  | grep -E 'zone|ipAddr|hostName'

# Check SCLB zone config
curl -s http://order-service:8080/actuator/env \
  | jq '.propertySources[] | .properties
    | to_entries[] | select(.key | contains("zone"))'
```

**Fix:**
```yaml
spring:
  cloud:
    loadbalancer:
      zone: ${AVAILABILITY_ZONE:us-east-1a}  # inject from env
eureka:
  instance:
    metadata-map:
      zone: ${AVAILABILITY_ZONE:us-east-1a}
```

**Prevention:** Inject AZ from instance metadata in Kubernetes (`spec.env[].valueFrom.fieldRef`) or EC2 instance metadata endpoint.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- Spring Cloud Service Discovery (Eureka) - provides the instance list SCLB routes across
- Load Balancing - the general pattern: algorithms, session affinity, health checking
- Spring Cloud Overview - umbrella project context

**Builds On This (learn these next):**
- Spring Cloud Circuit Breaker - wraps the load-balanced call with fault tolerance
- Spring Cloud Gateway - uses SCLB internally for route-to-service resolution
- Observability & SRE - measure p50/p99 per instance to detect load imbalance

**Alternatives / Comparisons:**
- Ribbon (deprecated) - predecessor; blocking I/O; no reactive support
- Kubernetes Load Balancer - kube-proxy iptables rules; works at the network level
- AWS ALB - server-side; no service discovery integration; works well for external traffic

---

### 📌 Quick Reference Card

```
╔══════════════════════════════════════════════════╗
║  WHAT IT IS      Client-side HTTP load balancer  ║
║  PROBLEM         Discovered list needs a chooser ║
║  KEY INSIGHT     Lives in caller JVM, no hop     ║
║  USE WHEN        Service-to-service in Spring    ║
║  AVOID WHEN      External traffic (use ALB/APIG) ║
║  TRADE-OFF       Per-JVM state vs global view    ║
║  ONE-LINER       "@LoadBalanced + service name"  ║
║  NEXT EXPLORE    Spring Cloud Circuit Breaker    ║
╚══════════════════════════════════════════════════╝
```

---

### 🧠 Think About This Before We Continue

1. **(B - Scale)** At 500 instances of `order-service`, each running its own SCLB, every instance independently caches the `payment-service` instance list with a 35 s TTL. During a rolling deploy of `payment-service`, how long is the aggregate window during which some `order-service` instances might route to old instances while others route to new ones? What are the implications for API contract compatibility?

2. **(C - Design Trade-off)** SCLB's zone-affinity prefers same-AZ instances for latency reasons, but AWS charges for cross-AZ traffic, not same-AZ. What failure scenario does zone-affinity make *more dangerous*, and how would you design a health-aware zone-affinity policy that gracefully handles AZ-wide failures?

3. **(E - First Principles)** Round-robin assumes all instances are homogeneous. In a canary deployment where the new version handles 20% of traffic, round-robin would give it 50% (1 out of 2 instances). How would you implement a weight-aware balancer, and what discovery metadata contract would you establish between deployer and load balancer?
