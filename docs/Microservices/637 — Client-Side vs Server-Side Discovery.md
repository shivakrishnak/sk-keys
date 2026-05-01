---
layout: default
title: "Client-Side vs Server-Side Discovery"
parent: "Microservices"
nav_order: 637
permalink: /microservices/client-side-vs-server-side-discovery/
number: "637"
category: Microservices
difficulty: ★★★
depends_on: "Service Discovery, Service Registry"
used_by: "API Gateway (Microservices), Service Mesh (Microservices)"
tags: #advanced, #microservices, #networking, #distributed, #pattern
---

# 637 — Client-Side vs Server-Side Discovery

`#advanced` `#microservices` `#networking` `#distributed` `#pattern`

⚡ TL;DR — **Client-Side Discovery**: the calling service queries the Service Registry directly and picks an instance (Eureka + Spring Cloud LoadBalancer). **Server-Side Discovery**: the client sends to a load balancer/API Gateway which queries the registry and routes (Kubernetes, AWS ALB). Trade-off: client control vs operational simplicity.

| #637            | Category: Microservices                                   | Difficulty: ★★★ |
| :-------------- | :-------------------------------------------------------- | :-------------- |
| **Depends on:** | Service Discovery, Service Registry                       |                 |
| **Used by:**    | API Gateway (Microservices), Service Mesh (Microservices) |                 |

---

### 📘 Textbook Definition

**Client-Side Discovery** and **Server-Side Discovery** are the two fundamental patterns for resolving service locations in a microservices architecture. In **Client-Side Discovery**, the service consumer is responsible for querying the Service Registry, selecting an available instance using a client-embedded load-balancing algorithm (round-robin, random, weighted, least-connections), and making the request directly to the chosen instance's IP:port. In **Server-Side Discovery**, the consumer sends requests to a well-known intermediary — an API Gateway, load balancer, or DNS name — which then queries the registry and routes requests. The consumer has no knowledge of instance addresses. Each pattern has distinct implications for operational complexity, coupling, language support, and load balancing sophistication. Most cloud-native environments use server-side discovery via Kubernetes Service DNS; Spring Cloud ecosystems traditionally use client-side discovery via Eureka + Ribbon/Spring Cloud LoadBalancer.

---

### 🟢 Simple Definition (Easy)

Client-Side: ServiceA looks up ServiceB's address itself, picks one, and calls it directly. Server-Side: ServiceA sends to a load balancer, which looks up ServiceB's address and forwards the call. Client-side: the caller knows who it's calling. Server-side: the caller just sends to an intermediary.

---

### 🔵 Simple Definition (Elaborated)

Think of two ways to get a restaurant recommendation: Client-Side is you opening Yelp yourself, reading reviews, picking a restaurant, and going there directly — you made all the decisions. Server-Side is calling a concierge who checks availability, picks a restaurant with open tables, and books you a table — the concierge made the routing decision. Both get you to a restaurant. Client-side gives you more control but requires you to have the Yelp app (registry client library). Server-side requires you to trust the concierge (load balancer), but works with any language or framework.

---

### 🔩 First Principles Explanation

**Client-Side Discovery — full request lifecycle:**

```
[OrderService] (has Eureka client + Spring Cloud LoadBalancer embedded)

Step 1: startup
  → fetch all registry entries from Eureka
  → cache locally: {
      "inventory-service": ["10.0.1.1:8080", "10.0.1.2:8080"],
      "payment-service":   ["10.0.2.1:8080"]
    }
  → background thread refreshes every 30 seconds

Step 2: making a call
  restTemplate.getForObject("http://inventory-service/api/inventory/123", ...)
  → Spring Cloud LoadBalancer intercepts "inventory-service"
  → queries local cache: ["10.0.1.1:8080", "10.0.1.2:8080"]
  → applies round-robin: picks 10.0.1.1:8080 (first call)
  → next call picks 10.0.1.2:8080
  → actual HTTP call: http://10.0.1.1:8080/api/inventory/123

  KEY: No extra network hop. Client calls instance directly.

Step 3: instance failure
  10.0.1.1 crashes
  → Cache still has 10.0.1.1 for up to 30s (until next Eureka refresh)
  → OrderService may call 10.0.1.1 → connection refused
  → Spring Cloud LoadBalancer retry: picks 10.0.1.2 instead
  → After 30s: Eureka has evicted 10.0.1.1, cache refreshed
```

**Server-Side Discovery — Kubernetes implementation:**

```
[OrderService] (no registry library, no IP knowledge)

Step 1: DNS resolution
  HTTP call: http://inventory-service:8080/api/inventory/123
  → CoreDNS resolves: inventory-service.default.svc.cluster.local
  → Returns: ClusterIP 10.96.0.100 (virtual, stable IP)

Step 2: kube-proxy routing
  Packet arrives at 10.96.0.100:8080
  → kube-proxy iptables/ipvs rules: ClusterIP is NOT a real IP
  → iptables DNAT rule rewrites destination to one of:
    [10.244.0.5:8080, 10.244.0.6:8080, 10.244.0.7:8080]
    (probabilities: 1/3 each — stateless random load balancing)
  → Actual packet goes to pod at 10.244.0.5:8080

Step 3: pod removal
  Pod 10.244.0.5 fails readiness probe
  → Kubernetes removes from Endpoints resource
  → kube-proxy updates iptables rules: probabilities now 1/2 each
  → Future packets: only [10.244.0.6, 10.244.0.7]
  → No change in OrderService code or config
```

**Comparison matrix:**

```
                    CLIENT-SIDE          SERVER-SIDE
Registry query by:  Client service       Load balancer / Gateway
Load balancing:     Client-embedded      Load balancer
Extra network hop:  No (direct call)     Yes (→ LB → instance)
Language support:   Registry client      Language-agnostic
                    per language needed
Sophistication:     Complex (Round       Simple (iptables random)
                    robin, health-aware  or complex (Envoy WASM)
                    retries)
Coupling:           Client coupled to    Client coupled only to
                    registry (library)   LB address / DNS name
Kubernetes fit:     Redundant (Eureka +  Native (CoreDNS +
                    K8s both managing)   kube-proxy)
Examples:           Spring Cloud Eureka  Kubernetes Services,
                    + LoadBalancer       AWS ALB, Envoy, Nginx
```

---

### ❓ Why Does This Exist (Why Before What)

Two valid engineering approaches to the same problem — neither is universally correct:

Client-Side: evolved from Netflix's microservices architecture (Eureka, Ribbon) before Kubernetes existed. When you control the client-side libraries and teams use JVM languages, embedding discovery logic in the client is powerful and reduces infrastructure dependencies.

Server-Side: evolved with the rise of container orchestration (Kubernetes) and polyglot architectures (Python, Go, Node.js services all need discovery). Centralising discovery logic in the load balancer eliminates the need for per-language registry clients and simplifies services.

Trade-off: client-side gives you control and eliminates an extra hop; server-side gives you simplicity and language independence.

---

### 🧠 Mental Model / Analogy

> Client-Side Discovery is like Google Maps in your own phone: you look up the route yourself, pick the best option, and navigate independently. Server-Side Discovery is like a taxi driver who knows all the routes: you say the destination name and sit back — they figure out the optimal route. Google Maps gives you more control (avoid tolls, pick shortest). The taxi driver handles the complexity for you — and works even if you don't have a phone.

"Google Maps in your phone" = embedded registry client (Eureka client)
"Looking up the route yourself" = client querying registry
"Taxi driver" = load balancer / Kubernetes kube-proxy
"Saying the destination name" = calling `http://service-name/`
"Works even without a phone" = language-agnostic (no client library needed)

---

### ⚙️ How It Works (Mechanism)

**Spring Cloud LoadBalancer (client-side) — custom strategy:**

```java
// Custom load balancing strategy for client-side discovery:
@Bean
ReactorLoadBalancer<ServiceInstance> customLoadBalancer(
    Environment env,
    LoadBalancerClientFactory factory) {

    String name = env.getProperty(LoadBalancerClientFactory.PROPERTY_NAME);
    return new RoundRobinLoadBalancer(
        factory.getLazyProvider(name, ServiceInstanceListSupplier.class),
        name
    );
}
// Spring Cloud LoadBalancer supports: RoundRobinLoadBalancer, RandomLoadBalancer
// Custom: implement ReactorServiceInstanceLoadBalancer for custom strategies
// (e.g., least-connections, latency-weighted, zone-aware)
```

---

### 🔄 How It Connects (Mini-Map)

```
Service Registry
(stores instance locations)
        │
        ├──────────────────────────────────┐
        ▼                                  ▼
CLIENT-SIDE DISCOVERY          SERVER-SIDE DISCOVERY
(client queries registry)      (LB queries registry)
Client-Side vs Server-Side ◄── (you are here)
        │                                  │
        ├── Spring Cloud LoadBalancer       ├── Kubernetes kube-proxy
        ├── OpenFeign (Eureka)              ├── API Gateway
        └── Ribbon (deprecated)            └── Service Mesh (Envoy)
```

---

### 💻 Code Example

**Server-Side in Kubernetes — service definition:**

```yaml
# Server-Side Discovery: Kubernetes Service
# OrderService just calls http://inventory-service:8080 — no registry library needed
apiVersion: v1
kind: Service
metadata:
  name: inventory-service
spec:
  selector:
    app: inventory-service # routes to pods with this label
  ports:
    - port: 8080
      targetPort: 8080
  type: ClusterIP # virtual stable IP for server-side routing


# Client code (no Spring Cloud Eureka, no registry library):
# restTemplate.getForObject("http://inventory-service:8080/api/inventory/123", ...)
# CoreDNS resolves → kube-proxy routes → pod receives request
# New pods added by HPA: automatically included in routing (Endpoints updated)
# Failed pods removed from readiness: automatically excluded (Endpoints updated)
```

---

### ⚠️ Common Misconceptions

| Misconception                                                                     | Reality                                                                                                                                                                                                             |
| --------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Client-Side Discovery is more efficient because it eliminates a network hop       | The "extra hop" in server-side is typically within the same data center (microseconds). The added operational simplicity and language independence of server-side usually outweigh this marginal latency benefit    |
| In Kubernetes, client-side discovery (Eureka) is needed for proper load balancing | Kubernetes' kube-proxy provides basic load balancing. For more advanced balancing (circuit breaking, retries, observability), use a Service Mesh (Istio/Envoy) — still server-side, but with sophisticated features |
| Client-Side Discovery means only one pattern — round-robin                        | Spring Cloud LoadBalancer supports round-robin, random, and custom strategies. Ribbon (deprecated) supported zone-aware load balancing. Client-side can be very sophisticated                                       |
| Server-Side Discovery only means Kubernetes                                       | AWS ALB (Application Load Balancer) with target groups, NGINX Plus, Consul with Envoy, and API Gateways all implement server-side discovery outside of Kubernetes                                                   |

---

### 🔥 Pitfalls in Production

**Running Eureka + Kubernetes — double discovery, split-brain**

```
ANTI-PATTERN: Deploying Spring Cloud Eureka inside Kubernetes
  Services register with Eureka (client-side)
  AND Kubernetes creates its own Service endpoints (server-side)
  → Two discovery systems competing
  → Eureka may have stale data during Kubernetes rolling updates
  → Debugging requires checking both Eureka dashboard AND kubectl
  → Unnecessary infrastructure complexity

BETTER APPROACH for K8s environments:
  Option 1: Remove Spring Cloud Eureka — use only K8s DNS
    spring.cloud.discovery.enabled=false
    spring.cloud.kubernetes.discovery.enabled=true (optional — uses K8s API)

  Option 2: If you need client-side features (custom LB, circuit breaking):
    Use Service Mesh (Istio + Envoy) — server-side but with full features
    → Istio handles discovery, load balancing, retries, circuit breaking
    → Application code remains simple (no embedded library)
```

---

### 🔗 Related Keywords

- `Service Discovery` — the parent concept that both patterns implement
- `Service Registry` — the registry both patterns query (directly or via LB)
- `API Gateway (Microservices)` — typically implements server-side discovery for ingress
- `Service Mesh (Microservices)` — advanced server-side discovery with circuit breaking, observability

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ CLIENT-SIDE  │ Client queries registry directly         │
│              │ Client picks instance + load balances    │
│              │ Examples: Spring Eureka + LoadBalancer   │
├──────────────┼───────────────────────────────────────────┤
│ SERVER-SIDE  │ Client → LB (well-known DNS/IP)          │
│              │ LB queries registry + routes             │
│              │ Examples: Kubernetes, API Gateway        │
├──────────────┼───────────────────────────────────────────┤
│ CHOOSE       │ Client-side: Java-only, fine-grained LB  │
│              │ Server-side: polyglot, K8s-native,       │
│              │ simpler services                         │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** In client-side discovery, the client caches registry data and applies its own load balancing. This means each service instance has its own view of the registry and its own load balancing state. Describe a scenario where 3 instances of `OrderService` each have slightly different cached views of the `InventoryService` registry (one has stale data, two have current data), and explain how this leads to uneven load distribution across `InventoryService` instances. How does zone-aware load balancing (prefer instances in the same availability zone) improve this?

**Q2.** Kubernetes kube-proxy uses iptables rules to implement server-side load balancing. The default strategy is random (probabilistic using iptables statistics module). Compare this to IPVS mode (explicit kernel-level load balancer with round-robin, least-connections, etc.). Why is iptables mode the default, and what is the threshold of services/endpoints at which iptables mode starts to degrade performance? What does Istio's Envoy sidecar add on top of kube-proxy for load balancing?
