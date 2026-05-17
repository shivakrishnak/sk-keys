---
id: MSV-007
title: Service Discovery
category: Microservices
tier: tier-5-distributed-architecture
folder: MSV-microservices
difficulty: ★★☆
depends_on: MSV-006, MSV-002
used_by: MSV-014, MSV-039, MSV-040
related: MSV-006, MSV-039, MSV-014, MSV-040
tags:
  - microservices
  - distributed
  - intermediate
  - networking
status: complete
version: 4
layout: default
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 7
permalink: /microservices/service-discovery/
---

# MSV-007 - Service Discovery

⚡ TL;DR - Service Discovery is the mechanism by which a
service finds the network address of another service at
runtime, using a registry lookup or DNS instead of a
hardcoded endpoint.

| #007 | Category: Microservices | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Service Registry, Microservices Architecture | |
| **Used by:** | Load Balancing in Microservices, Client-Side vs Server-Side Discovery, Service Mesh | |
| **Related:** | Service Registry, Client-Side vs Server-Side Discovery, Load Balancing in Microservices, Service Mesh | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You need Service A to call Service B. You write `http://10.0.1.5:8080`
in the configuration. That address is valid today. Tomorrow,
Service B is redeployed to a new container with IP 10.0.1.9.
Your config is wrong. You update it. You deploy Service A. Fifteen
minutes later Service B scales to 3 instances. Your config still
points to one IP. Two-thirds of Service B's capacity is invisible
to Service A.

**THE BREAKING POINT:**
In a dynamic cloud environment, service instances come and go,
scale up and down, and move across nodes. A static IP or DNS
hostname that is not dynamically updated is not a location -
it is a liability. The system works by accident, not by design.

**THE INVENTION MOMENT:**
This is exactly why Service Discovery was formalised: the
separation of service identity (what you want to reach: "the Order
Service") from service location (where it currently is: which
IP:port) with an automatic mechanism to bridge the gap.

**EVOLUTION:**
Early approaches: Zookeeper (2008) for leader election and
registration. Netflix Eureka + Ribbon (2012) introduced
client-side discovery with client-side load balancing. Consul
(2014) added DNS-based discovery. Kubernetes service proxy
(2015+) moved discovery into the platform. Service meshes
(Istio 2017) moved discovery to sidecar proxies, eliminating
application code entirely.

---

### 📘 Textbook Definition

**Service Discovery** is the process by which a service
dynamically determines the network location of another service
at request time, rather than relying on static configuration.
There are two primary patterns: **client-side discovery**,
in which the caller queries the service registry and performs
load balancing itself, and **server-side discovery**, in which
an intermediary (load balancer, service mesh proxy, or
Kubernetes service) performs registry lookup and routing
on behalf of the caller. Both patterns decouple service
identity from service location.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Service Discovery is how a service finds another service's
current address without knowing it in advance.

**One analogy:**
> Looking up a restaurant on Google Maps is service discovery.
> You know the restaurant's name (identity), not its address.
> Maps does a lookup and gives you the current location.
> If the restaurant moves, Maps updates its data - you always
> get the current address without changing your search.

**One insight:**
Service Discovery separates the concern of "who do I want
to call" (identity, stable) from "where do I call it"
(location, ephemeral). This separation is what makes
elastic infrastructure possible.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Service identity (name) must be stable and independent
   of physical location.
2. Location must be resolved at call time, not at deploy
   time, to reflect the current fleet state.
3. The discovery mechanism must not itself be a performance
   bottleneck on every request.

**THE TWO PATTERNS:**

```
CLIENT-SIDE DISCOVERY:
─────────────────────
Caller → query Service Registry
       ← {10.0.0.1:8080, 10.0.0.2:8080}
Caller → load balance → calls 10.0.0.1:8080

Pros: caller controls load-balancing algorithm,
      no intermediary network hop
Cons: each service needs a registry client library,
      language-specific, tight coupling to registry API

SERVER-SIDE DISCOVERY:
──────────────────────
Caller → "http://order-service/orders/1"
       → Load Balancer / Service Mesh Proxy / k8s Service
       → queries registry internally
       → routes to 10.0.0.1:8080

Pros: caller is unaware of discovery, any language/framework
Cons: load balancer becomes critical path infrastructure
```

**THE TRADE-OFFS:**
**Gain:** Any pattern gives location transparency - services
find each other without hardcoded addresses.
**Cost:** Discovery adds latency (registry lookup) or
infrastructure dependency (load balancer, service mesh).

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Any dynamic fleet needs location transparency.
The registry lookup is essential.
**Accidental:** Application-code registry clients (Eureka
Spring client) add complexity that Kubernetes Endpoints +
kube-dns eliminates at the platform level.

---

### 🧪 Thought Experiment

**SETUP:**
You have Order Service (caller) and Inventory Service (target).
Three instances of Inventory are running. A fourth starts.
A fifth crashes.

**WITH HARDCODED DISCOVERY (none):**
Order Service has `INVENTORY_URL=http://10.0.0.3:8080`.
Fourth instance starts at 10.0.0.6 - Order ignores it.
Fifth instance crashes - if it was at 10.0.0.3, all
inventory calls fail. Manual intervention required.

**WITH SERVICE DISCOVERY:**
Order Service resolves `inventory-service` at call time.
Discovery returns {10.0.0.4, 10.0.0.5, 10.0.0.6} (health-
filtered list). Order Service load-balances across all three
healthy instances. The crashed instance is removed from the
list within 30-90 seconds. No manual intervention.

**THE INSIGHT:**
Discovery is not just about finding an address - it is about
continuously tracking a fleet that changes beneath you. The
discovery mechanism is the contract between the ephemeral
infrastructure layer and the stable application layer.

---

### 🧠 Mental Model / Analogy

> Service Discovery is like directory assistance for services.
> You know the name of who you want to call. You ask the
> operator (registry/DNS). The operator looks up the current
> number. You call. If the person moved and updated their
> listing, you get the new number next time without knowing
> anything changed.

- "Directory assistance" - the registry or DNS
- "Name" - the service name (stable identity)
- "Current number" - the IP:port (ephemeral location)
- "Updated listing" - instance registration/heartbeat
- "You call" - the actual HTTP/gRPC request

Where this analogy breaks down: directory assistance gives
one number. Service discovery returns multiple healthy
instances. Load balancing (choosing which one to call)
is a second step.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Service Discovery is how one service finds another. Instead
of using a fixed address that breaks when things move, it
asks "where is the Order Service right now?" and gets the
current answer.

**Level 2 - How to use it (junior developer):**
In Spring Cloud, add `@LoadBalanced` to `RestTemplate` and
use `http://SERVICE-NAME/path` URLs. Spring Cloud's load
balancer automatically resolves the service name via Eureka.
In Kubernetes, use the service DNS name `http://order-service.
namespace.svc.cluster.local` - kube-dns resolves it.

**Level 3 - How it works (mid-level engineer):**
Client-side: the caller fetches the instance list from the
registry (or uses a local cache refreshed every 30s). It
applies a load-balancing algorithm (round-robin, least-conn)
to select one instance. It makes the HTTP call directly to
that instance. If the call fails, it can retry with another
instance.
Server-side: the caller uses a service name that a
load balancer or service mesh proxy resolves. The proxy
queries the registry, balances, and forwards. The caller
is completely abstracted from the routing.

**Level 4 - Why it was designed this way (senior/staff):**
Client-side discovery (Netflix Ribbon pattern) was the first
approach because it required no changes to load balancer
infrastructure - just a client library. But it created
tight coupling between application code and the specific
registry client (Eureka client API). Server-side discovery
(Kubernetes services, Istio sidecar) moved the coupling to
the platform, making application code registry-agnostic.
The modern recommendation is server-side discovery for this
reason.

**Level 5 - Mastery (distinguished engineer):**
In a Kubernetes environment with Istio, discovery has three
layers: (1) Kubernetes Endpoints (where pods are), (2) Istio
pilot/Envoy (service mesh routing with weights, retries,
circuit breakers), (3) kube-dns (name to ClusterIP resolution).
Staff engineers understand which layer to configure for
traffic management vs health-based routing vs A/B testing.
Debugging a discovery failure requires tracing through all
three layers, not just checking DNS.

---

### ⚙️ How It Works (Mechanism)

**CLIENT-SIDE DISCOVERY FLOW (Eureka + Ribbon):**

```
Order Service (caller)
  │
  ▼
Ribbon Load Balancer (local to caller)
  │ 1. Check local cache: is INVENTORY-SERVICE list fresh?
  │    (refresh every 30s from Eureka)
  │ 2. If stale: GET http://eureka/eureka/apps/INVENTORY-SERVICE
  │ 3. Filter to status=UP instances
  │ 4. Apply round-robin: pick 10.0.0.2:8081
  ▼
HTTP GET http://10.0.0.2:8081/inventory/SKU-123
  │
  ▼ (response)
Order Service continues processing
```

**SERVER-SIDE DISCOVERY FLOW (Kubernetes):**

```
Order Service (caller)
  │
  ▼
HTTP GET http://inventory-service/inventory/SKU-123
  │ kube-dns resolves "inventory-service" to ClusterIP 10.96.0.5
  │
  ▼
iptables / IPVS (kube-proxy)
  │ ClusterIP 10.96.0.5 → endpoint list
  │ {10.0.0.2:8081, 10.0.0.3:8081, 10.0.0.4:8081}
  │ select one (round-robin)
  ▼
HTTP GET http://10.0.0.2:8081/inventory/SKU-123
```

**DISCOVERY WITH ISTIO SIDECAR:**

```
Order Service → HTTP request
  ↓
Envoy Sidecar (intercepted locally)
  │ Queries Pilot (istiod) for inventory-service endpoints
  │ Applies routing rules (virtual service, destination rule)
  │ Applies circuit breaker, retry, timeout
  ↓
HTTP forwarded to healthy Inventory Service instance
```

---

### 🔄 The Complete Picture - End-to-End Flow

**FULL REQUEST WITH DISCOVERY:**

```
Client HTTP Request → API Gateway
  │
  ▼
API Gateway discovers Order Service via DNS
  → routes to Order Service pod
  │
  ▼
Order Service  ← YOU ARE HERE
  │ needs inventory check
  │ discovery: resolve "inventory-service" → 3 instances
  │ load balance: choose instance 2
  ▼
Inventory Service instance 2
  │ returns stock level
  ▼
Order Service continues, creates order in own DB
  ▼
Returns order confirmation to client
```

**FAILURE PATH:**
```
Instance 2 returns 503
  → If client-side: Ribbon marks instance 2 as
    temporarily unavailable, retries with instance 3
  → If server-side: kube-proxy removes instance 2
    from endpoint list after failed health check
```

**WHAT CHANGES AT SCALE:**
At 10,000 service instances, kube-proxy iptables rules grow
to O(n^2) for each endpoint. Kubernetes switched to IPVS
mode for O(1) endpoint selection at scale. Client-side
discovery at scale means each caller maintains a local
cache of up to thousands of endpoints per service, with
30-second refresh cycles consuming significant memory.

---

### 💻 Code Example

**Example 1 - Wrong vs Right: hardcoded vs discovered**

```java
// BAD: hardcoded service location
@Service
public class InventoryClient {
    // Breaks on deploy, scale, or container restart
    private static final String URL =
        "http://10.0.1.5:8080/inventory/";

    public Stock check(String sku) {
        return restTemplate.getForObject(
            URL + sku, Stock.class);
    }
}
```

```java
// GOOD: discovered via Kubernetes DNS (server-side)
@Service
public class InventoryClient {
    // "inventory-service" resolved by kube-dns at call time
    @Value("${inventory.service.url:http://inventory-service}")
    private String serviceUrl;

    public Stock check(String sku) {
        return restTemplate.getForObject(
            serviceUrl + "/inventory/" + sku, Stock.class);
    }
}
// No registry client needed in Kubernetes
// Platform handles discovery transparently
```

**Example 2 - Spring Cloud client-side discovery (non-K8s)**

```java
// Client-side: caller resolves and load-balances
@Configuration
public class DiscoveryConfig {

    @Bean
    @LoadBalanced  // Enable Eureka-backed resolution
    public RestTemplate restTemplate() {
        return new RestTemplate();
    }
}

@Service
public class InventoryClient {

    @Autowired
    private RestTemplate restTemplate; // @LoadBalanced

    public Stock check(String sku) {
        // INVENTORY-SERVICE resolved via Eureka
        // Ribbon picks one instance from the list
        return restTemplate.getForObject(
            "http://INVENTORY-SERVICE/inventory/" + sku,
            Stock.class);
    }
}
```

**How to test / verify correctness:**
Test discovery works across instance lifecycle: start two
instances of the target service, verify the caller routes
to both. Kill one instance. Wait 120 seconds. Verify all
subsequent requests succeed (routing only to surviving instance).
Scale to 3 instances. Verify load is distributed across all 3.

---

### ⚖️ Comparison Table

| Pattern | Location | Advantages | Limitations | Best For |
|---|---|---|---|---|
| **Client-Side** | In the caller | Direct control, no hop | Library per language | Non-K8s, Spring Cloud |
| Server-Side (LB) | Load balancer | Language-agnostic | LB is critical path | Traditional infra |
| Server-Side (K8s) | kube-proxy | Platform-native | K8s only | Kubernetes fleets |
| Sidecar (Istio) | Envoy proxy | Full traffic control | Operational overhead | Complex routing |

**How to choose:** In Kubernetes, use native service DNS
(server-side, zero code). For non-Kubernetes, use client-side
with Spring Cloud or a service mesh agent. Only build
client-side with custom registry clients as a last resort.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Service Discovery and load balancing are the same thing | Discovery finds which instances exist. Load balancing chooses which one to call. They are separate concerns that are often combined. |
| DNS is sufficient for microservices discovery | Standard DNS doesn't include health filtering or rich metadata. Kubernetes Endpoints + kube-dns is an enhanced version that does. |
| Client-side discovery is more performant | It avoids one network hop but adds a local cache and registry refresh overhead. At scale, server-side with a sidecar proxy is often faster. |

---

### 🚨 Failure Modes & Diagnosis

**DNS resolution returning stale endpoints**

**Symptom:**
Requests to `http://payment-service` fail with connection
refused even though new pods are healthy. Rollout happened
10 minutes ago.

**Root Cause:**
DNS TTL (default 5s in kube-dns but some clients cache longer).
Old pods were terminated but DNS still resolves to old IPs
because the calling service's JVM has a JDK DNS cache with
TTL=infinity by default.

**Diagnostic Command:**
```bash
# Check JVM DNS cache configuration
kubectl exec -it order-service-xxx -- \
  jcmd 1 VM.system_properties | grep networkaddress.cache.ttl

# Should be: networkaddress.cache.ttl=5
# BAD:       networkaddress.cache.ttl=-1 (cache forever)

# Verify endpoints are updated in K8s
kubectl get endpoints payment-service -o yaml
```

**Fix:**
```java
// In JVM-based services: set DNS TTL to 5 seconds
// Add to JVM startup args or security.properties
-Dnetworkaddress.cache.ttl=5
-Dnetworkaddress.cache.negative.ttl=0
```

**Prevention:**
Configure JVM DNS TTL in all Docker images via the base
image entrypoint script.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Service Registry` - the underlying data store that
  discovery queries
- `Microservices Architecture` - why dynamic discovery
  is needed in a microservices context

**Builds On This (learn these next):**
- `Load Balancing in Microservices` - what happens after
  discovery returns a list of instances
- `Client-Side vs Server-Side Discovery` - deep dive on
  the two patterns
- `Service Mesh` - how modern platforms handle discovery
  plus traffic management in one layer

**Alternatives / Comparisons:**
- `Service Registry` - the mechanism; discovery is the
  usage pattern on top of the registry
- `API Gateway` - performs server-side discovery on behalf
  of external callers

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Runtime mechanism to find another         │
│              │ service's current network address         │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Hardcoded IPs break in dynamic            │
│ SOLVES       │ infrastructure where addresses change     │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Two patterns: caller resolves (client-    │
│              │ side) vs platform resolves (server-side)  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always - any service calling another      │
│              │ service in a dynamic environment          │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ N/A - static config is never correct      │
│              │ for production microservices              │
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ JVM DNS cache with TTL=-1 (infinity)      │
│              │ causes stale resolution for hours         │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Location transparency vs registry/DNS     │
│              │ as critical infrastructure dependency     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Ask where a service is at call time -    │
│              │  never assume it stayed where it was"     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Load Balancing → Client-Side vs Server-   │
│              │ Side Discovery → Service Mesh             │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. In Kubernetes, use native service DNS - no Eureka client
   needed. `http://service-name` just works.
2. Set JVM DNS TTL to 5 seconds in all services - the default
   (-1, cache forever) causes stale discovery after deploys.
3. Discovery finds instances; load balancing chooses among
   them - they are separate concerns often combined in tooling.

**Interview one-liner:**
"Service Discovery is how a service dynamically finds another
service's address at call time. Client-side: caller queries
the registry and load-balances itself. Server-side: a proxy
or load balancer resolves and routes transparently. In
Kubernetes, server-side is built in via kube-dns and Endpoints
- no registry client code needed."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Separate stable identity from ephemeral location. This
applies at every level: service discovery (name vs IP),
DNS (domain vs IP), load balancer VIP (stable IP vs
backend IPs), and even object-oriented design (interface
vs implementation). Stability comes from indirection.

**Where else this pattern appears:**
- DNS: the original service discovery for the internet
- LDAP / Active Directory: directory service for human
  identities and their locations (email, phone)
- Service mesh xDS protocol: Envoy discovers routes
  and endpoints via Pilot's control plane API

**Industry applications:**
- Netflix invented client-side discovery (Eureka + Ribbon)
  because their AWS VMs had short lifespans and IPs changed
  frequently - the pattern was born from real operational pain
- HashiCorp Consul extended discovery to include health
  checks, ACL-based segmentation, and multi-datacenter
  replication for global service meshes

---

### 💡 The Surprising Truth

Kubernetes kube-proxy does not actually use standard DNS
for load balancing between pods. The DNS name resolves to
a ClusterIP (a stable virtual IP that never changes), and
kube-proxy uses iptables or IPVS rules to intercept packets
to the ClusterIP and DNAT them to a real pod IP. This means
TCP connections to a service are load-balanced at the
connection level (per new connection), not the request level
(per HTTP request). For long-lived HTTP/1.1 connections (like
database connection pools), this can result in all requests
going to one pod because only one connection was established.
The fix: use HTTP/2 or a service mesh that balances per
request, not per connection.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN** Describe the difference between client-side
   and server-side discovery to a team deciding which to
   use for a new Spring Boot service on Kubernetes.
2. **DEBUG** Given intermittent 503 errors after a rolling
   deployment, determine within 5 minutes whether the cause
   is DNS staleness (JVM cache), registry propagation lag,
   or readiness probe misconfiguration.
3. **DECIDE** Choose between client-side (Eureka+Ribbon) and
   server-side (Kubernetes service) discovery for: a mixed
   Java and Python fleet, and justify the choice for each
   language.
4. **BUILD** Configure a Spring Boot application to use
   Kubernetes-native service discovery (no Eureka client)
   with a fallback URL for local development.
5. **EXTEND** Apply the discovery pattern to a WebSocket
   service where clients need long-lived connections to
   the same instance. How does this change the discovery
   and routing requirements?

---

### 🧠 Think About This Before We Continue

**Q1.** In Kubernetes, kube-proxy uses iptables to DNAT
packets to a ClusterIP. When a pod is removed (crashed or
redeployed), the Endpoints controller updates the endpoint
list. Trace the chain of events: from pod failure to the
moment iptables rules no longer route to the dead pod.
What is the window where traffic can still reach the dead pod?
*Hint: Consider the propagation chain: kubelet → API server
→ Endpoints controller → kube-proxy → iptables update.*

**Q2.** Service A has 100 instances. Service B calls Service A
via client-side discovery (Eureka + Ribbon). Each Service B
instance refreshes the registry cache every 30 seconds.
There are 200 Service B instances. Calculate the read
request rate on the Eureka server from registry cache
refreshes. At what scale does this become a problem and
what architectural change reduces the load?
*Hint: Calculate refreshes/second. Consider delta fetch
vs full fetch. Consider server-side discovery as the
alternative.*

**Q3.** You are building a real-time bidding platform where
service calls must complete in < 5ms. Service discovery
adds 0.5-2ms for a registry lookup on each call. Design
a discovery strategy that keeps end-to-end latency under
5ms while still handling instance failures within 30 seconds.
What are the consistency trade-offs you are accepting?
*Hint: Think about local caching with async refresh vs
synchronous registry queries.*

---

### 🎯 Interview Deep-Dive

**Q1: "Explain client-side vs server-side service discovery.
Which would you use and why?"**

*Why they ask:* Core microservices architecture question that
tests practical decision-making.

*Strong answer includes:*
- Client-side: caller queries registry, selects instance,
  calls directly. More control, language coupling.
- Server-side: intermediary (LB/proxy/K8s service) handles
  discovery transparently. Language-agnostic.
- Modern recommendation: server-side via Kubernetes services
  or service mesh - no registry code in applications
- When client-side is still appropriate: non-Kubernetes infra,
  Spring Cloud apps where Ribbon provides fine-grained control

**Q2: "How does service discovery work in Kubernetes?
What actually happens when you call http://order-service?"**

*Why they ask:* Tests depth of Kubernetes knowledge.

*Strong answer includes:*
- DNS: kube-dns resolves `order-service` to ClusterIP
- ClusterIP: stable virtual IP that never changes
- kube-proxy: watches Endpoints object, writes iptables/IPVS
  rules to DNAT ClusterIP to real pod IPs
- Health: only Ready pods appear in Endpoints (via readiness
  probe)
- Load balancing: per-connection (iptables) or per-request
  (IPVS/Istio)

**Q3: "You are seeing intermittent connection refused errors
to a service after a deployment. Service is healthy in
monitoring. How do you debug this?"**

*Why they ask:* Tests debugging skills for discovery issues.

*Strong answer includes:*
- Check: is the request going to old pod IPs that no longer
  exist? `kubectl get endpoints`
- Check: JVM DNS cache TTL - `networkaddress.cache.ttl` may be -1
- Check: readiness probe - new pods may be registered before
  they are ready
- Check: timing - does the error correlate with the rollout
  window (deployment-time issue) or is it ongoing?
- Fix path: set DNS TTL to 5s, add readiness probe delay,
  ensure health endpoint reflects real state