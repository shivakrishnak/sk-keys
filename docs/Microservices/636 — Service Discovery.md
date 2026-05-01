---
layout: default
title: "Service Discovery"
parent: "Microservices"
nav_order: 636
permalink: /microservices/service-discovery/
number: "636"
category: Microservices
difficulty: ★★☆
depends_on: "Service Registry, Monolith vs Microservices"
used_by: "Client-Side vs Server-Side Discovery, API Gateway (Microservices), Health Check Patterns"
tags: #intermediate, #microservices, #networking, #distributed
---

# 636 — Service Discovery

`#intermediate` `#microservices` `#networking` `#distributed`

⚡ TL;DR — **Service Discovery** is the mechanism by which microservices locate each other at runtime. The Service Registry stores instance locations; discovery is the act of querying it. Two patterns: **client-side** (client queries registry, picks instance) or **server-side** (load balancer queries registry, routes request).

| #636            | Category: Microservices                                                                  | Difficulty: ★★☆ |
| :-------------- | :--------------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Service Registry, Monolith vs Microservices                                              |                 |
| **Used by:**    | Client-Side vs Server-Side Discovery, API Gateway (Microservices), Health Check Patterns |                 |

---

### 📘 Textbook Definition

**Service Discovery** is the automated process by which a service locates other services in a dynamic environment where instances are constantly being created, destroyed, and moved. In contrast to traditional environments where service addresses are configured statically, service discovery dynamically resolves service names to current network addresses. It relies on a **Service Registry** as the source of truth. Service discovery operates in two modes: **Client-Side Discovery** — the client (caller) queries the registry directly, receives a list of available instances, applies a load-balancing strategy (round-robin, random, least-connections), and makes the call directly; **Server-Side Discovery** — the client sends the request to a load balancer or API Gateway, which queries the registry and routes the request to an instance. Spring Cloud provides client-side discovery via `@LoadBalanced` RestTemplate / OpenFeign + Spring Cloud LoadBalancer. Kubernetes provides server-side discovery via CoreDNS + kube-proxy transparently.

---

### 🟢 Simple Definition (Easy)

Service Discovery answers: "where is ServiceB right now?" Instead of a hardcoded IP address, the calling service looks up the current address at runtime. The Service Registry provides the answer. Discovery is the lookup process; the Registry is the database.

---

### 🔵 Simple Definition (Elaborated)

In a Kubernetes cluster, `OrderService` needs to call `InventoryService`. Instead of knowing the IP, `OrderService` sends an HTTP request to the hostname `inventory-service`. Kubernetes' internal DNS (CoreDNS) resolves this to a virtual IP, and kube-proxy routes the request to one of the healthy `InventoryService` pods. No application code changes if `InventoryService` scales from 3 to 10 pods — discovery is fully automatic. This is server-side discovery. In Spring Cloud with Eureka, the client itself queries Eureka for `inventory-service` instances and picks one — that is client-side discovery. Both achieve the same goal through different mechanisms.

---

### 🔩 First Principles Explanation

**Client-Side vs Server-Side Discovery — the key difference:**

```
CLIENT-SIDE DISCOVERY:
  [ServiceA] → query ServiceRegistry → [10.0.1.1, 10.0.1.2]
  [ServiceA] → picks 10.0.1.1 (round-robin)
  [ServiceA] → HTTP call to 10.0.1.1:8080/api/resource

  Components:
    - Client must embed registry client library (Eureka client, Consul client)
    - Client must embed load balancing logic (Spring Cloud LoadBalancer)
    - Client caches registry data (refreshed every 30s)

  Pros: client controls load balancing strategy
  Cons: registry library must be in every service, language-specific

SERVER-SIDE DISCOVERY:
  [ServiceA] → HTTP call to load-balancer/inventory-service
  [LoadBalancer] → query ServiceRegistry → [10.0.1.1, 10.0.1.2]
  [LoadBalancer] → routes to 10.0.1.1:8080/api/resource

  Components:
    - Client sends to a well-known endpoint (LB address or DNS name)
    - Load balancer handles registry query and routing
    - Client needs no registry library

  Pros: language-agnostic, client is simple, centralized control
  Cons: load balancer is a required dependency, added hop latency

KUBERNETES (server-side discovery built-in):
  [ServiceA] → http://inventory-service:8080/api/resource
  [CoreDNS] → resolves "inventory-service" → ClusterIP 10.96.0.10
  [kube-proxy iptables] → routes ClusterIP → pod IP 10.244.0.5
  No registry library needed in application code
```

**Service discovery caching — the staleness trade-off:**

```
CLIENT-SIDE (Eureka):
  Client fetches registry every 30s (default)
  → Between refreshes, registry data may be stale
  → A crashed instance may be in cache for up to 30s after eviction from Eureka
  → Always combine with circuit breaker to handle stale entries

SERVER-SIDE (Kubernetes):
  CoreDNS TTL: 5–30 seconds (configurable)
  kube-proxy updates iptables rules as soon as Endpoints resource changes
  → Near-real-time: pod removed → Endpoints updated within seconds
  → DNS TTL may still serve old IP for up to TTL seconds
  → JVM DNS caching (networkaddress.cache.ttl) can further delay updates!

JVM DNS CACHING FIX:
  # In your JVM startup flags or java.security file:
  networkaddress.cache.ttl=5       # cache DNS for 5 seconds (not forever)
  networkaddress.cache.negative.ttl=0
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Service Discovery:

What breaks without it:

1. Service B's IP changes on every deployment/restart — Service A has wrong config.
2. New Service B instances added by auto-scaling are unknown to Service A.
3. Failed Service B instances remain in Service A's configuration, causing timeouts.
4. Blue-green deployments require manual config changes in all calling services.

WITH Service Discovery:
→ Service A always calls the current, healthy instances of Service B.
→ Auto-scaling and deployments are transparent — no configuration changes needed.
→ Load balancing is automatic across all available instances.
→ Health-based routing: only healthy instances are returned from the registry.

---

### 🧠 Mental Model / Analogy

> Service Discovery is like a taxi dispatch system. A passenger (calling service) doesn't know individual taxi locations — they call dispatch (Service Registry) and say "I need a taxi at location X." Dispatch checks current taxi availability (registry) and assigns the nearest available driver (load balancing). If a taxi breaks down (instance crashes), dispatch removes it from the available pool (eviction). The passenger never needs to know any specific taxi's phone number — dispatch handles all the routing.

"Taxi dispatch" = Service Registry + discovery mechanism
"Passenger calling dispatch" = client service querying the registry
"Taxi availability" = registered, healthy service instances
"Nearest available" = load balancing strategy
"Broken down taxi removed" = unhealthy instance evicted from registry

---

### ⚙️ How It Works (Mechanism)

**Spring Cloud + Feign client (client-side discovery):**

```java
// Feign client with client-side discovery via Spring Cloud LoadBalancer:
@FeignClient(name = "inventory-service") // name = service registered in Eureka
interface InventoryClient {
    @GetMapping("/api/inventory/{productId}")
    InventoryResponse getInventory(@PathVariable Long productId);
}
// Spring resolves "inventory-service" via Spring Cloud LoadBalancer:
// 1. LoadBalancer queries Eureka for "inventory-service" instances
// 2. Applies round-robin across available instances
// 3. Makes HTTP call to selected instance
// No IP addresses in code anywhere
```

---

### 🔄 How It Connects (Mini-Map)

```
Service Registry
(the database of service instances)
        │
        ▼
Service Discovery  ◄──── (you are here)
(the process of querying the registry)
        │
        ├── Client-Side vs Server-Side Discovery
        ├── API Gateway → server-side discovery for incoming traffic
        ├── Health Check Patterns → only healthy instances served by discovery
        └── Circuit Breaker → handles stale discovery data (dead instances)
```

---

### 💻 Code Example

**Manual service discovery + load balancing (illustrative):**

```java
@Service
class InventoryServiceClient {

    @Autowired DiscoveryClient discoveryClient;
    private final RestTemplate restTemplate = new RestTemplate();
    private final Random random = new Random();

    public InventoryResponse getInventory(Long productId) {
        List<ServiceInstance> instances =
            discoveryClient.getInstances("inventory-service");

        if (instances.isEmpty()) {
            throw new ServiceUnavailableException("inventory-service has no available instances");
        }

        // Simple random load balancing:
        ServiceInstance instance = instances.get(random.nextInt(instances.size()));
        String url = "http://" + instance.getHost() + ":" + instance.getPort()
            + "/api/inventory/" + productId;

        return restTemplate.getForObject(url, InventoryResponse.class);
    }
}
// Better: use @LoadBalanced RestTemplate or @FeignClient which do this automatically
```

---

### ⚠️ Common Misconceptions

| Misconception                                                | Reality                                                                                                                                                                                             |
| ------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Service Discovery and Service Registry are the same thing    | The Registry is the database; Discovery is the process of querying it. Like the difference between a phone book (registry) and looking up a number (discovery)                                      |
| Service discovery eliminates the need for circuit breakers   | Discovery provides addresses; it does not guarantee those addresses are responsive. Stale registry entries and instances under extreme load still need circuit breakers to prevent cascade failures |
| Kubernetes replaces the need to understand service discovery | Kubernetes abstracts the mechanism, but developers need to understand DNS resolution, connection pooling, and the JVM DNS cache to debug discovery-related production issues                        |

---

### 🔥 Pitfalls in Production

**JVM DNS caching causing discovery misses**

```java
// PROBLEM: JVM caches DNS resolutions by default
// In some JVMs, successful DNS resolutions are cached FOREVER (ttl=-1)
// Consequence: if a Kubernetes Service's ClusterIP changes (rare but possible),
//              or if you rely on DNS-based load balancing (multiple A records),
//              JVM never re-resolves — always uses cached (possibly stale) IP

// FIX: set networkaddress.cache.ttl to a short value at startup:
static {
    java.security.Security.setProperty("networkaddress.cache.ttl", "5");
    java.security.Security.setProperty("networkaddress.cache.negative.ttl", "0");
}
// OR in JVM flags: -Dnetworkaddress.cache.ttl=5

// Also verify: Feign/OkHttp/HttpClient connection pools hold connections
// to specific IPs — even with DNS refresh, existing pool connections
// still go to the old IP until the pool connection expires
```

---

### 🔗 Related Keywords

- `Service Registry` — the database that Service Discovery queries
- `Client-Side vs Server-Side Discovery` — the two patterns for implementing service discovery
- `Health Check Patterns` — ensure registry only returns healthy instances to discovery queries
- `API Gateway (Microservices)` — implements server-side discovery for external clients

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ CLIENT-SIDE  │ Client queries registry → picks instance  │
│              │ Spring Cloud Eureka + LoadBalancer/Feign  │
├──────────────┼───────────────────────────────────────────┤
│ SERVER-SIDE  │ Client → LB → LB queries registry        │
│              │ Kubernetes: CoreDNS + kube-proxy          │
│              │ API Gateway + Consul/Eureka               │
├──────────────┼───────────────────────────────────────────┤
│ STALENESS    │ Cache TTL: 30s (Eureka), 5-30s (K8s DNS) │
│              │ JVM DNS cache: set ttl=5 to avoid issues  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Client-side service discovery with Eureka caches registry data for 30 seconds by default. During this 30-second window, a crashed service instance may still appear in the client's cache. Describe the full failure handling stack: (a) client picks stale instance → connection refused; (b) Spring Cloud LoadBalancer's retry mechanism — how does it pick a different instance on retry; (c) how Resilience4j circuit breaker interacts with this — does the circuit breaker open on the first failure or after N failures? What is the recommended retry + circuit breaker combination?

**Q2.** In Kubernetes, `Service` resources use label selectors to route traffic to pods. Describe the exact sequence from a pod crash to that pod being removed from service discovery: (a) kubelet detects container exit; (b) pod transitions to `Failed` state; (c) Endpoints controller removes pod IP from `Endpoints` resource; (d) kube-proxy updates iptables rules; (e) new connections stop being routed to crashed pod. What is the typical end-to-end latency for this sequence, and during this window, how many requests may hit the crashed pod?
