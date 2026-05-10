---
layout: default
title: "Service Discovery"
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 21
permalink: /microservices/service-discovery/
id: MSV-021
category: Microservices
difficulty: ★★☆
depends_on: Service Registry, Networking, Health Check Patterns
used_by: Client-Side vs Server-Side Discovery, API Gateway, Load Balancing
related: Service Registry, Load Balancing, Client-Side vs Server-Side Discovery
tags:
  - microservices
  - networking
  - distributed
  - intermediate
  - pattern
status: complete
version: 2
---

# MSV-021 - Service Discovery

⚡ TL;DR - Service Discovery is the mechanism by which microservices dynamically locate each other's network addresses at runtime, using a live service registry instead of hardcoded configuration.

| #636 | Category: Microservices | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Service Registry, Networking, Health Check Patterns | |
| **Used by:** | Client-Side vs Server-Side Discovery, API Gateway, Load Balancing | |
| **Related:** | Service Registry, Load Balancing, Client-Side vs Server-Side Discovery | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Your order service config file lists `payments.host=10.0.2.5` and `inventory.host=10.0.3.8`. On Monday, a deployment rolls out a new payments image. Kubernetes terminates the old pod and starts a new one at `10.0.2.17`. Nobody updated the config. The order service calls `10.0.2.5`, gets connection refused, and every order attempt fails until someone notices, updates the config, and redeploys. On Tuesday this happens again with the inventory service.

**THE BREAKING POINT:**
In a containerised microservices system, IP addresses change constantly - on every deployment, pod restart, auto-scale event, or failure recovery. Manually maintaining IP-based configuration isn't a management problem, it's architecturally impossible at scale.

**THE INVENTION MOMENT:**
This is exactly why Service Discovery was introduced - to make service-to-service communication self-healing by having clients dynamically look up the current location of any service at runtime.


**EVOLUTION:**
Service discovery evolved from DNS (1983) to purpose-built registries as microservices introduced dynamic scaling and health checking requirements DNS could not meet. DNS TTL (typically 30-300 seconds) was too slow to propagate pod failures in high-traffic systems. Netflix's Eureka (2012), HashiCorp Consul (2014), and Kubernetes' built-in discovery (2015) each addressed different trade-offs between consistency, availability, and operational simplicity. The discipline evolved from 'hard-code service endpoints' to 'name services, discover instances dynamically, health-check continuously.'
---

### 📘 Textbook Definition

**Service Discovery** is the process by which a service client determines the network location of a service instance to call. It involves querying a Service Registry - a database of currently available, healthy service instances - and selecting an appropriate instance. Service Discovery eliminates hardcoded host/port configuration by replacing static addresses with dynamic lookups that reflect the current system state. It is distinct from the Service Registry: the registry is the database; discovery is the process of using it.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Service discovery is asking "where is Service X right now?" and getting the current, live answer.

**One analogy:**
> Imagine calling a taxi company that dispatches dynamically. You don't call a specific car's phone number. You call dispatch (service registry), and they tell you which available taxi is nearest right now. If that taxi breaks down, dispatch assigns another - you don't need to know. Service discovery is the dispatch layer for microservices.

**One insight:**
Service discovery is the difference between a static phone book (hardcoded config) and a live dispatch system (dynamic registry lookup). The value is proportional to how often instances change - which in Kubernetes is continuously.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. A client needs a host:port pair to make a network call.
2. In dynamic environments, this pair changes and clients must adapt without redeployment.
3. Discovery must not add unbounded latency - registry lookups must be fast (sub-millisecond from cache).

**DERIVED DESIGN:**
Given Invariant 2 and 3, pure on-demand registry queries per call are too slow (~5ms round trip). The solution: client-side caching of registry data with a short TTL (30s–60s), combined with background refresh. This gives sub-millisecond lookups from cache while staying within one TTL window of registry accuracy.

**Discovery patterns:**

**Client-Side Discovery:** The client itself queries the registry, picks an instance, and calls it directly. The client is aware of discovery (e.g., Eureka + Ribbon in Spring Cloud).

**Server-Side Discovery:** A router or load balancer queries the registry on behalf of the client. The client just calls a stable address (e.g., Kubernetes Service, nginx, AWS ALB). The client is unaware of discovery.

**THE TRADE-OFFS:**
**Gain:** Self-healing service communication, auto-scale compatible, no config updates needed on deployment.
**Cost:** DNS/registry propagation lag means brief windows of stale data after changes; discovery layer is a new operational concern.

---

### 🧪 Thought Experiment

**SETUP:**
The payments service has 3 instances: A, B, C. Instance B crashes. An auto-scaler starts instance D at a new IP.

**WITHOUT SERVICE DISCOVERY:**
Order service config: `[A, B, C]`. B is gone, D doesn't exist in config. 33% of calls fail (those routed to B). D receives zero traffic even though it is healthy. Manual config update + redeployment required.

**WITH SERVICE DISCOVERY:**
Registry detects B's health check failure → B deregistered (within 15s). D starts → self-registers with registry. Order service's discovery client refreshes registry (within 30s). New instance list: `[A, C, D]`. Traffic distributes evenly. Zero manual intervention required.

**THE INSIGHT:**
Service discovery makes service communication resilient to infrastructure churn by automating the propagation of instance-level changes to all consumers.

---

### 🧠 Mental Model / Analogy

> Service discovery is the DNS of microservices - but live. Standard DNS maps hostnames to IPs and caches for minutes. Service discovery maps service names to healthy instance addresses and refreshes in seconds. It is DNS with awareness of health, load, and metadata.

- "DNS lookup" → registry query for service address
- "DNS cache TTL" → client-side registry cache TTL (shorter: 30s vs 300s)
- "DNS record" → service registry entry with IP + port + health status
- "NXDOMAIN (name not found)" → no healthy instances available in registry

Where this analogy breaks down: DNS is passive - it doesn't check whether the destination is healthy. Service discovery actively health-checks instances and removes unhealthy ones immediately.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Service discovery is the automated system that lets microservices find each other. Instead of memorising each other's addresses, services ask a central directory "where is the payments service?" and get the answer in real time.

**Level 2 - How to use it (junior developer):**
In Spring Cloud + Eureka: add `@EnableEurekaClient`, configure `eureka.client.service-url`. Use `@FeignClient(name = "payments-service")` with the logical name. Spring's discovery client resolves the name to a real IP before each call. No IP addresses needed in your code or configuration.

**Level 3 - How it works (mid-level engineer):**
The Discovery Client queries the registry on startup and refreshes its cache on a background thread (Eureka: every 30 seconds). When the Feign client makes a call, it asks the load balancer (Ribbon / Spring Cloud LoadBalancer) for an instance. The load balancer selects from the cached list using a strategy (round-robin by default). If a call fails, the failed instance is flagged and retried on another instance.

**Level 4 - Why it was designed this way (senior/staff):**
The two competing discovery patterns - client-side and server-side - reflect a fundamental architectural trade-off. Client-side discovery gives the client more control and reduces infrastructure requirements (no smart proxy needed), but couples the client to the discovery technology. Server-side discovery keeps clients dumb (they just call a stable VIP) but requires a smart load balancer aware of the registry. Kubernetes chose server-side discovery via kube-proxy and kube-dns, abstracting discovery entirely from the application. This is now the dominant pattern in containerised environments - your app code literally never calls a discovery API; the platform handles it transparently.

---

### ⚙️ How It Works (Mechanism)

**Client-side discovery flow:**

```
┌──────────────────────────────────────────────┐
│        Client-Side Discovery Flow            │
├──────────────────────────────────────────────┤
│ 1. Order Service needs to call Payments       │
│ 2. Feign Client → asks DiscoveryClient        │
│ 3. DiscoveryClient checks local cache         │
│    Cache hit: returns [A:8080, C:8081, D:8082]│
│    Cache miss: queries Eureka → updates cache │
│ 4. LoadBalancer selects instance (round-robin)│
│    → selects A:8080                          │
│ 5. HTTP call to http://A:8080/payments        │
│ 6. Success → caller gets response            │
│                                              │
│    On failure (connection refused):           │
│ 7. Retry on next instance (C:8081)            │
│ 8. Mark A:8080 as suspect in local stats     │
└──────────────────────────────────────────────┘
```

**Kubernetes server-side discovery:**

```
┌──────────────────────────────────────────────┐
│      Kubernetes Service Discovery            │
├──────────────────────────────────────────────┤
│ 1. Order Service calls payments-service:8080 │
│    (DNS name - no IP knowledge needed)       │
│ 2. kube-dns resolves to ClusterIP (10.0.0.5) │
│ 3. kube-proxy intercepts packet              │
│ 4. kube-proxy consults Endpoints API         │
│    (Endpoints = live healthy pod IPs)        │
│ 5. iptables/IPVS rule routes to a pod IP     │
│ 6. Request reaches healthy pod               │
│ App code never touches a discovery API       │
└──────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
Order Service startup → Discovery Client registers with Eureka → Fetches registry data into local cache → Order placed → Feign call to `payments-service` ← YOU ARE HERE → Load balancer picks instance from cache → HTTP call to selected instance → Response

**FAILURE PATH:**
Selected instance has crashed since last cache refresh → Call fails → Retry on next instance (from same cached list) → Success → Background thread refreshes cache → Crashed instance removed from next refresh

**WHAT CHANGES AT SCALE:**
At 1000 service instances, each client maintaining a full registry cache is expensive (memory and network). Solutions: filtered registry subscriptions (subscribe only to services you call) and regional registries (only replicate within the same availability zone). At 10,000 instances, the gossip-based propagation in Consul/Eureka introduces a few seconds of lag - this is acceptable in most systems but requires circuit breakers to handle the stale-cache window.

---

### 💻 Code Example

**Example 1 - Client-side discovery with Spring Cloud LoadBalancer:**

```java
@Configuration
public class ServiceConfig {
    @Bean
    @LoadBalanced
    public WebClient.Builder loadBalancedWebClientBuilder() {
        return WebClient.builder();
    }
}

@Service
public class OrderService {
    private final WebClient.Builder webClient;

    public PaymentResult processPayment(Order order) {
        // "payments-service" resolved to live IP by discovery
        return webClient.build()
            .post()
            .uri("http://payments-service/payments")
            .bodyValue(order)
            .retrieve()
            .bodyToMono(PaymentResult.class)
            .block();
    }
}
```

**Example 2 - Feign client with discovery (Spring Cloud):**

```java
// Feign resolves "inventory-service" via Eureka automatically
@FeignClient(
    name = "inventory-service",
    fallback = InventoryServiceFallback.class
)
public interface InventoryClient {
    @GetMapping("/inventory/{productId}")
    InventoryStatus getStatus(@PathVariable String productId);
}

@Component
public class InventoryServiceFallback implements InventoryClient {
    @Override
    public InventoryStatus getStatus(String productId) {
        return InventoryStatus.unknown(); // graceful fallback
    }
}
```

**Example 3 - Query Eureka registry directly (diagnostic):**

```bash
# List all registered instances of payments-service
curl -s http://eureka:8761/eureka/apps/PAYMENTS-SERVICE \
  -H "Accept: application/json" | \
  python3 -m json.tool | \
  grep -E "hostName|port|status"
```

---

### ⚖️ Comparison Table

| Discovery Approach | Client Complexity | Infrastructure | Portability | Best For |
|---|---|---|---|---|
| **Client-Side (Eureka/Ribbon)** | High | Low | Medium | Spring Cloud environments |
| Server-Side (Kubernetes Service) | None | Medium | High | K8s-native apps |
| Server-Side (AWS ALB/ECS) | None | Low (managed) | Low | AWS-native deployments |
| DNS SRV Records | Low | Low | High | Multi-cloud or bare metal |

How to choose: use Kubernetes Service (server-side) if running on K8s - it requires zero application code changes. Use client-side discovery (Eureka) only for non-K8s environments or when you need fine-grained client-side routing logic.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Service Discovery and Service Registry are the same thing | The registry is the database; discovery is the process of querying it. A system cannot do discovery without a registry, but they are distinct concerns |
| Kubernetes eliminates the need for service discovery | Kubernetes has built-in server-side service discovery - it doesn't eliminate the need, it fulfills it transparently |
| Service discovery ensures calls always succeed | Discovery finds healthy instances per the last registry sync, but instances can crash between the registry update and the actual call - circuit breakers are still required |
| Client-side discovery is always faster than server-side | Client-side: sub-millisecond cache lookup. Server-side: one extra network hop through a proxy. At high call rates, the proxy hop is measurable but usually acceptable |

---

### 🚨 Failure Modes & Diagnosis

**1. Discovery Cache Staleness After Instance Crash**

**Symptom:** For 30–60 seconds after a service instance crashes, some clients continue routing calls to the dead instance, receiving connection timeouts.

**Root Cause:** Client-side TTL has not expired. Cached instance list still includes the crashed pod.

**Diagnostic:**
```bash
# Check Eureka heartbeat timeout on the crashed instance
curl -s http://eureka:8761/eureka/apps/PAYMENTS-SERVICE | \
  grep -A3 "lastRenewalTimestamp"
# If timestamp > 90s ago: instance should have been evicted
```

**Fix:** Add a circuit breaker (Resilience4J) at the call site. When calls to a specific instance fail, the circuit breaker stops routing to it immediately - before the registry refreshes.

**Prevention:** Combine short registry TTL (30s), active health probes, and client-side circuit breakers for a defence-in-depth approach.

**2. All Instances Return 503 - Registry Not Updated**

**Symptom:** All calls to a service fail even though pods are running. `kubectl get pods` shows all replicas as `Running`.

**Root Cause:** Pods are running but failing their readiness probe - Kubernetes has not added them to the Service Endpoints (the K8s service discovery layer).

**Diagnostic:**
```bash
# Check service endpoints - empty = no healthy pods registered
kubectl get endpoints payments-service -n production
# NAME               ENDPOINTS
# payments-service   <none>  ← problem: no ready pods

# Check pod readiness
kubectl describe pod payments-service-xxx | grep -A5 "Readiness"
```

**Fix:** Fix the readiness probe configuration. The probe must accurately reflect when the pod is ready to serve traffic (database connection established, warm-up complete).

**Prevention:** Always configure both `livenessProbe` and `readinessProbe` in K8s deployments. Readiness gates service discovery inclusion.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Service Registry` - the database that service discovery queries; understanding the registry is prerequisite to understanding how discovery works
- `Health Check Patterns` - registries rely on health checks to decide which instances to include in discovery results

**Builds On This (learn these next):**
- `Client-Side vs Server-Side Discovery` - the two architectural approaches to implementing service discovery, each with different trade-offs
- `Load Balancing` - how a client distributes calls across the instances returned by discovery

**Alternatives / Comparisons:**
- `API Gateway (Microservices)` - performs server-side discovery on behalf of external clients; internal service-to-service discovery uses a different mechanism

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ The process of dynamically resolving a    │
│              │ service name to a live, healthy instance  │
│              │ address at runtime                        │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Dynamic IP addresses in containerised     │
│ SOLVES       │ environments break static configuration   │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Discovery adds a brief staleness window   │
│              │ (TTL) - circuit breakers are the safety   │
│              │ net for the gap between crash and cache   │
│              │ refresh                                   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Service instances have dynamic addresses  │
│              │ (containers, VMs, auto-scaling groups)    │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Services have stable, predictable DNS     │
│              │ names (Kubernetes handles this natively)  │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Self-healing communication vs staleness   │
│              │ window and discovery infrastructure cost  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Ask first, then call - never assume the  │
│              │  address is still valid."                 │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Client-Side vs Server-Side Discovery →    │
│              │ Health Check Patterns → Load Balancing    │
└──────────────────────────────────────────────────────────┘
```


---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Service discovery is the runtime equivalent of a phone book: names are stable, addresses change. The valuable invariant is that callers use names (stable) rather than addresses (ephemeral). When services are called by name, the infrastructure can change what the name resolves to without callers needing to be updated or redeployed.

**Where else this pattern appears:**
- **Database failover:** Connection pool libraries discover the database leader by hostname (db.primary.internal) and reconnect when the name resolves to a new IP after a failover - service discovery for databases.
- **CDN geo-routing:** CDN DNS routes client requests to the nearest edge node by resolving the same hostname to different IPs based on client geography - service discovery applied to content delivery.
- **Email delivery:** MX records in DNS are service discovery for mail servers - a domain name resolves to the mail server responsible for receiving email, changeable without affecting senders.

---

### 💡 The Surprising Truth

The most common service discovery failure mode is not the discovery mechanism itself failing - it is the absence of health checking. A registry that faithfully reports all registered instances (including those that are running but serving incorrectly - deadlocked, out of memory, returning 500s for every request) is worse than no registry: it routes traffic to instances that will fail, consuming request budgets and masking the real problem. Modern service discovery combines registration with continuous health monitoring - a service's registration and its health status are inseparable in correctly designed systems.
---

### 🧠 Think About This Before We Continue

**Q1.** Your payments service has 10 instances. During a rolling deployment, 5 instances are running the old version and 5 are running the new version simultaneously. The new version has a different response structure for payment failures. Service discovery routes calls to both old and new instances. What specific problems does this create for the calling service, and what contract versioning strategy prevents these problems during rolling deployments?

*Hint:* Think about what happens when a caller receives a mix of v1 and v2 responses and parses them with a v1 parser: optional new fields are ignored (backward compatible), required new fields cause parse errors (breaking), removed fields cause null pointer exceptions (breaking). Explore whether the API contract should be versioned at the endpoint URL level (/v2/payments) or at the service instance level (discovery tags indicating API version), and what rolling deployment guarantees that callers never receive a mix of versions simultaneously.

**Q2.** At 3am, your on-call alert fires: "Order service has 40% error rate." You check the service registry and it shows all 3 payments service instances as healthy. But calls to payments are failing. What are the 5 most likely root causes (beyond the registry's knowledge), in order of likelihood, and what specific diagnostic commands would you run to identify which is the actual cause?

*Hint:* Think about what the registry cannot know: instances may be registered as healthy (heartbeats succeeding) but not actually serving requests (thread pool exhausted, deadlocked, dependency down). The 5 most likely causes (in order): (1) payment service thread pools exhausted by slow downstream; (2) network path between order and payment is degraded, not severed; (3) order service timeout shorter than payment response time; (4) payment's database or external API unavailable; (5) TLS certificate expiry on inter-service mTLS. Diagnostic: `kubectl exec -it <pod> -- curl localhost:8080/actuator/health`, check thread pool metrics, test connectivity with nc.

**Q3 (Design Trade-off):** Two microservices in different Kubernetes clusters (different cloud regions) must discover and call each other. Kubernetes DNS-based service discovery does not work across clusters. Design the cross-cluster service discovery strategy.

*Hint:* Think about the three main options: (1) expose via LoadBalancer (external IP, reachable cross-cluster but publicly visible - security risk); (2) service mesh with cross-cluster support (Istio multicluster, Linkerd multicluster - mutual TLS, service-level routing, but operational complexity); (3) centralised registry (Consul) registered in both clusters. Explore what the latency, security, and operational complexity trade-offs are for each, and whether the cross-cluster calls are synchronous (latency-sensitive) or asynchronous (can tolerate retry-level network handling).
