---
layout: default
title: "Spring Cloud Service Discovery (Eureka)"
parent: "Spring Core"
grand_parent: "Technical Dictionary"
nav_order: 13
permalink: /spring/spring-cloud-service-discovery-eureka/
id: SPR-013
category: Spring Core
difficulty: ★★★
depends_on: Spring Cloud Overview, Service Discovery, Microservices
used_by: Spring Cloud Load Balancer, Spring Cloud Gateway
related: Consul, Kubernetes Service, DNS-based Discovery
tags:
  - java
  - spring
  - microservices
  - distributed
  - advanced
---

# SPR-013 - Spring Cloud Service Discovery (Eureka)

⚡ TL;DR - Eureka is Netflix's service registry that lets microservices find each other by name without hardcoded addresses.

| Field | Value |
|---|---|
| **Depends on** | Spring Cloud Overview, Service Discovery, Microservices |
| **Used by** | Spring Cloud Load Balancer, Spring Cloud Gateway |
| **Related** | Consul, Kubernetes Service, DNS-based Discovery |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** In a microservices system, `order-service` needs to call `inventory-service`. You hardcode `http://inventory-service-host:8080`. This works on your laptop. On Friday, the ops team scales `inventory-service` to 6 pods on Kubernetes, rotates the IP range, and promotes to prod - your hardcoded URL reaches exactly one dead pod. Incidents start at midnight.

**THE BREAKING POINT:** Dynamic cloud environments make static IP configuration a liability. Instances appear and disappear. Auto-scaling creates ephemeral hosts. Containers restart with new IPs after every deploy. No human can keep a config file up to date with 40 services across 3 environments.

**THE INVENTION MOMENT:** Netflix built **Eureka** to solve their own scaling crisis circa 2012. The insight: instead of callers knowing where services live, services *register themselves* on startup, and callers *ask a registry* at call time. The registry becomes a dynamic phone book that self-updates through heartbeats.

---

### 📘 Textbook Definition

**Spring Cloud Netflix Eureka** is a REST-based service registry for resilient mid-tier load balancing and failover. It consists of two components: the **Eureka Server** (registry) and the **Eureka Client** (embedded in every service). Clients register their metadata (host, port, health URL) on startup, renew registration via periodic heartbeats, and query the registry to discover other services by logical name.

---

### ⏱️ Understand It in 30 Seconds

**One line:** A service registry where microservices advertise their address and discover peers by name - eliminating hardcoded URLs.

> "Eureka is a DNS phone book for microservices: every service checks in when it starts, and any caller dials by name - Eureka routes to a live instance."

**One insight:** Eureka trades strong consistency for availability. It deliberately keeps stale data rather than going dark, because a slightly stale registry is safer than no registry at all.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Services are ephemeral - assume any instance can die at any time.
2. Service location must be resolved at call time, not at deploy time.
3. Registry data consistency can be eventual; availability must be continuous.
4. Clients must cache the registry locally to survive registry outages.

**DERIVED DESIGN:**
- Services push `POST /eureka/apps/{appName}` on startup.
- Services send `PUT /eureka/apps/{appName}/{instanceId}` every 30 s (heartbeat).
- If 3 consecutive heartbeats are missed (90 s), the registry evicts the instance.
- Clients poll `GET /eureka/apps` every 30 s to refresh their local copy.

**THE TRADE-OFFS:**

**Gain:** Near-100% availability - clients survive a full registry outage by serving cached data. Self-preservation prevents mass eviction during network partitions.

**Cost:** Registration-to-discovery latency can reach ~3 minutes in the worst case (30 s registration + 30 s client cache warm + 30 s propagation to peer nodes).

---

### 🧪 Thought Experiment

**SETUP:** You run 3 instances of `payment-service` behind no load balancer. `checkout-service` needs to call one of them. How does `checkout-service` find them?

**WHAT HAPPENS WITHOUT EUREKA:** You maintain a properties file listing all 3 IPs. You deploy a new `payment-service` pod - the IP changes. `checkout-service` still has the old IP. Calls fail. You update the file and redeploy `checkout-service` to pick up the change. You just coupled two services' deployment lifecycles.

**WHAT HAPPENS WITH EUREKA:** `payment-service` registers with Eureka on startup. `checkout-service` calls `http://payment-service/charge` - the Eureka client intercepts, queries the local cache of registered instances, picks one, and substitutes the real IP. When a pod restarts with a new IP, it re-registers in 30 s. The old entry expires in 90 s. `checkout-service` never touched a config file.

**THE INSIGHT:** Eureka converts a deploy-time coupling (static config) into a runtime coupling (registry query). This is a fundamental shift: services no longer need to know *where* their dependencies are, only *what* they're called.

---

### 🧠 Mental Model / Analogy

> "Eureka is the hotel concierge directory: every restaurant in the city sends the concierge an update whenever they open, close, or move. Guests ask the concierge for a restaurant by cuisine, not by street address."

- **Restaurant = microservice instance** - it registers its location and capacity.
- **Cuisine = service name** - callers search by logical name, not IP.
- **Concierge's binder = Eureka server registry** - the live, dynamic map.
- **Guest's pocket card = client-side cache** - works even if the concierge is briefly unavailable.
- **Daily fax to branch offices = peer replication** - all Eureka peers sync their data.

Where this analogy breaks down: the concierge retires stale entries immediately; Eureka's **self-preservation mode** deliberately keeps stale entries during suspected network splits.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Eureka is a contact list for microservices. Instead of coding in the phone number, each service leaves its number at a central desk, and callers look it up by name every time they call.

**Level 2 - How to use it (junior developer):**
Add `spring-cloud-starter-netflix-eureka-server` to the registry project, annotate the main class with `@EnableEurekaServer`, and set `server.port=8761`. Add `spring-cloud-starter-netflix-eureka-client` to every microservice. Set `eureka.client.serviceUrl.defaultZone=http://localhost:8761/eureka/`. The service auto-registers with its `spring.application.name`.

**Level 3 - How it works (mid-level engineer):**
On startup, the Eureka client sends a `POST` registration request carrying an `InstanceInfo` object (appName, hostName, ipAddr, port, vipAddress, statusPageUrl, healthCheckUrl, metadata). The server stores this in an in-memory `ConcurrentHashMap<String, Map<String, Lease<InstanceInfo>>>`. The client starts a heartbeat timer at 30 s intervals sending `PUT`. The server runs a separate eviction timer - if a lease has not been renewed within `duration * 2` (default 90 s), the lease expires. The `ResponseCacheImpl` maintains a read/write cache; clients get a compressed delta on subsequent polls.

**Level 4 - Why it was designed this way (senior/staff):**
Eureka prioritises AP (availability + partition tolerance) over CP (consistency) in the CAP theorem. During a network partition, if more than 15% of expected heartbeats are missing, Eureka enters **self-preservation mode** - it stops evicting registrations. The reasoning: mass evictions during a partition are more harmful than serving stale entries, because a caller can still route to a stale instance and handle a connection error gracefully, whereas no registry means no routing at all. The 3-minute worst-case discovery latency is a deliberate trade-off accepted to achieve this resilience property.

---

### ⚙️ How It Works (Mechanism)

```
EUREKA SERVER INTERNALS
─────────────────────────────────────────────
 Registry Store
 ┌─────────────────────────────────────────┐
 │ app: PAYMENT-SERVICE                    │
 │  └─ instanceId: host1:payment:8081      │
 │      Lease: lastRenewal=T, TTL=90s      │
 │  └─ instanceId: host2:payment:8081      │
 │      Lease: lastRenewal=T-25s, TTL=90s  │
 └─────────────────────────────────────────┘
          ↑ POST register   ↑ PUT heartbeat
          │                 │
 ┌────────────────────────────────────────┐
 │           EUREKA CLIENT                │
 │  - Registration thread (startup)       │
 │  - Heartbeat scheduler (30 s)          │
 │  - Cache refresh scheduler (30 s)      │
 │  - Local registry cache (InstanceInfo) │
 └────────────────────────────────────────┘
          │ GET /apps (delta every 30 s)
          ▼
 ┌────────────────────────────────────────┐
 │         RESPONSE CACHE                 │
 │  ReadWriteMap (TTL 30 s)               │
 │  ReadOnlyMap (sync from ReadWriteMap)  │
 └────────────────────────────────────────┘
```

**Peer-to-peer replication:** Each Eureka server replicates registrations to all other peers. A 3-node cluster tolerates 2 node failures before clients must use cached data.

**Self-preservation mode:** Triggered when `actual_heartbeat_rate < 0.85 × expected_heartbeat_rate`. All evictions halt. The dashboard shows a red warning banner.

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
checkout-service startup
  │
  ├─► GET /eureka/apps → cache PAYMENT-SERVICE instances
  │
checkout-service makes a call
  │
  ├─► RestTemplate / WebClient resolves "payment-service"
  │     │
  │     ├─► Eureka client looks up local cache      ← YOU ARE HERE
  │     ├─► Returns: [host1:8081, host2:8081]
  │     └─► Load balancer picks host1:8081
  │
  └─► HTTP POST http://host1:8081/charge

payment-service1 goes down
  │
  ├─► Misses 3 heartbeats (90 s elapses)
  ├─► Eureka server evicts instance
  ├─► checkout-service polls delta (up to 30 s later)
  └─► Local cache updated; host1:8081 removed
```

**FAILURE PATH:**
- Instance dies without deregistering → 90 s eviction delay + 30 s client refresh = up to 2 min stale entries.
- Eureka server crashes → clients serve local cache. New registrations cannot complete until server recovers.
- Self-preservation active → stale entries persist indefinitely until the mode exits.

**WHAT CHANGES AT SCALE:**
- 100+ services × 3 instances = 300+ `InstanceInfo` objects. Memory is cheap; the concern is replication lag between Eureka peers.
- Multi-region setups require `eureka.client.region` and zone awareness; cross-zone latency affects heartbeat reliability.
- At scale, replace Eureka with Consul (stronger consistency) or Kubernetes Services (DNS, no external dependency).

---

### 💻 Code Example

**BAD - hardcoded URL, no service discovery:**
```java
// Brittle: breaks on any infra change
@Service
public class CheckoutService {
    private final RestTemplate rest;

    public Order checkout(Cart cart) {
        // Hardcoded - dies when payment-service moves
        return rest.postForObject(
            "http://10.0.1.42:8081/charge",
            cart,
            Order.class
        );
    }
}
```

**GOOD - Eureka-backed service discovery:**
```java
// Eureka Server
@SpringBootApplication
@EnableEurekaServer
public class RegistryApplication {
    public static void main(String[] args) {
        SpringApplication.run(RegistryApplication.class, args);
    }
}
```
```yaml
# application.yml - Eureka Server
server:
  port: 8761
eureka:
  instance:
    hostname: localhost
  client:
    register-with-eureka: false
    fetch-registry: false
```
```java
// Eureka Client - payment-service
@SpringBootApplication
@EnableDiscoveryClient          // or just rely on auto-config
public class PaymentApplication {
    public static void main(String[] args) {
        SpringApplication.run(PaymentApplication.class, args);
    }
}
```
```yaml
# application.yml - payment-service
spring:
  application:
    name: payment-service        # registered name in Eureka
eureka:
  client:
    service-url:
      defaultZone: http://localhost:8761/eureka/
  instance:
    prefer-ip-address: true
    lease-renewal-interval-in-seconds: 30
    lease-expiration-duration-in-seconds: 90
```
```java
// Caller - checkout-service uses logical name, not IP
@Configuration
public class WebClientConfig {
    @Bean
    @LoadBalanced                 // activates Eureka-aware resolution
    public WebClient.Builder loadBalancedWebClientBuilder() {
        return WebClient.builder();
    }
}

@Service
public class CheckoutService {
    private final WebClient.Builder webClientBuilder;

    public Mono<Order> checkout(Cart cart) {
        // "payment-service" resolves via Eureka
        return webClientBuilder.build()
            .post()
            .uri("http://payment-service/charge")
            .bodyValue(cart)
            .retrieve()
            .bodyToMono(Order.class);
    }
}
```

---

### ⚖️ Comparison Table

| Feature | Eureka | Consul | Kubernetes Service | DNS-based |
|---|---|---|---|---|
| **Consistency model** | AP (eventual) | CP (Raft) | CP (etcd) | Eventual (TTL) |
| **Health checks** | Heartbeat only | Active HTTP/TCP/script | Liveness/Readiness probes | TTL only |
| **Multi-datacenter** | Manual replication | Built-in | Via federation | DNS delegation |
| **KV store** | No | Yes | Via ConfigMap | No |
| **Spring integration** | First-class | spring-cloud-consul | spring-cloud-kubernetes | Manual |
| **Self-preservation** | Yes (stale entries kept) | No (stricter eviction) | N/A | N/A |
| **Operational burden** | Medium | Medium-high | Low (managed) | Low |
| **Best for** | Spring/Netflix stacks | Heterogeneous services | K8s-native apps | Simple setups |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Deregistration is instant" | By default, eviction takes up to 90 s after the last heartbeat. Client cache refresh adds another 30 s. Total: up to 2 minutes of routing to a dead instance. |
| "Self-preservation mode is a bug" | It's intentional AP behaviour. During a network partition, Eureka prefers stale data over aggressive eviction. Disable it only in non-partitioned environments. |
| "Eureka requires Ribbon for load balancing" | Ribbon is deprecated. Spring Cloud Load Balancer (2127) is the successor and integrates directly with Eureka. |
| "One Eureka server is enough for prod" | A single Eureka node is a SPOF. Production requires 3+ peer nodes with `eureka.client.serviceUrl.defaultZone` pointing to all peers. |
| "Eureka is the best choice for Kubernetes" | On Kubernetes, Service DNS (`payment-service.namespace.svc.cluster.local`) is built-in. Adding Eureka duplicates the registry and complicates health state management. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1 - Ghost instances (routing to dead services)**

**Symptom:** `Connection refused` or timeout errors on calls to a service you know is down but Eureka still lists.

**Root Cause:** The instance crashed without sending a graceful deregister `DELETE`. The 90 s TTL has not elapsed, or self-preservation mode is active.

**Diagnostic:**
```bash
# View all registered instances
curl -s http://localhost:8761/eureka/apps \
  | python -m json.tool | grep -E 'instanceId|status'

# Check self-preservation warning
curl -s http://localhost:8761/actuator/info | grep renewals
```

**Fix:**
```yaml
# BAD - default TTL too long for fast-failing services
eureka:
  instance:
    lease-expiration-duration-in-seconds: 90

# GOOD - reduce TTL in non-partitioned environments
eureka:
  instance:
    lease-renewal-interval-in-seconds: 5
    lease-expiration-duration-in-seconds: 15
  server:
    enable-self-preservation: false   # only if infra is stable
    eviction-interval-timer-in-ms: 3000
```

**Prevention:** Implement `@PreDestroy` shutdown hooks and register `EurekaAutoServiceRegistration` so `spring.lifecycle.timeout-per-shutdown-phase=30s` triggers graceful deregister.

---

**Mode 2 - Eureka server split-brain (peer replication failure)**

**Symptom:** Two Eureka peers disagree on which instances are registered. Clients connected to different peers see different service lists.

**Root Cause:** Network partition between Eureka peers. Both sides enter self-preservation. Each peer stops evicting based only on its own heartbeat data.

**Diagnostic:**
```bash
# Compare instance counts across peers
curl -s http://eureka1:8761/eureka/apps | grep -c '<instanceId>'
curl -s http://eureka2:8761/eureka/apps | grep -c '<instanceId>'
# Different numbers indicate split view

# Check peer replication health
curl -s http://eureka1:8761/actuator/health | jq '.components.eureka'
```

**Fix:** Restore network connectivity. Self-preservation exits automatically when heartbeat rate normalises. Temporarily increase `expected-client-renewal-interval-seconds` if the peer count changed.

**Prevention:** Use 3-node Eureka clusters with dedicated peer interconnects. Monitor `eureka.server.renewals-threshold-update-interval-ms` metrics. Consider Consul for stricter consistency requirements.

---

**Mode 3 - New service instances not discovered for 3+ minutes**

**Symptom:** A freshly deployed instance does not receive traffic. Callers report `No instances available for payment-service`.

**Root Cause:** Cumulative latency: 30 s initial registration backoff + 30 s server cache refresh + 30 s client delta poll = worst-case 90 s. Additional 30 s if the caller was at the start of its poll cycle.

**Diagnostic:**
```bash
# Confirm instance registered on server
curl -s http://localhost:8761/eureka/apps/PAYMENT-SERVICE \
  | python -m json.tool | grep -E 'status|ipAddr|port'

# Trigger immediate client cache refresh (actuator)
curl -X POST http://checkout-service:8080/actuator/refresh
```

**Fix:**
```yaml
# Reduce poll and cache intervals for faster convergence
eureka:
  client:
    registry-fetch-interval-seconds: 5   # default 30
    initial-instance-info-replication-interval-seconds: 5
  server:
    response-cache-update-interval-ms: 5000  # default 30000
```

**Prevention:** Accept the latency in normal operations. Use readiness probes (`/actuator/health/readiness`) so the load balancer only routes traffic once the service is fully warm.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- Service Discovery - the general pattern Eureka implements
- Microservices - the architectural style that creates the need for dynamic discovery
- Spring Cloud Overview - the umbrella project Eureka lives within

**Builds On This (learn these next):**
- Spring Cloud Load Balancer - uses the Eureka instance list to distribute traffic
- Spring Cloud Gateway - uses Eureka to route requests to discovered services
- Spring Cloud Circuit Breaker - wraps calls to discovered services with fault tolerance

**Alternatives / Comparisons:**
- Consul - stronger CP consistency, KV store, multi-datacenter built-in
- Kubernetes Service - DNS-native discovery for K8s workloads, no extra dependency
- DNS-based Discovery - simplest approach, works for stable-instance environments

---

### 📌 Quick Reference Card

```
╔══════════════════════════════════════════════════╗
║  WHAT IT IS      Netflix service registry        ║
║  PROBLEM         Dynamic IPs in cloud infra      ║
║  KEY INSIGHT     AP over CP; cache beats dark    ║
║  USE WHEN        Spring/non-K8s microservices    ║
║  AVOID WHEN      Running on Kubernetes natively  ║
║  TRADE-OFF       ~3 min discovery latency        ║
║  ONE-LINER       "Register by name, find by name"║
║  NEXT EXPLORE    Spring Cloud Load Balancer      ║
╚══════════════════════════════════════════════════╝
```

---

### 🧠 Think About This Before We Continue

1. **(B - Scale)** A payment service runs 200 instances across 3 AWS regions. Eureka self-preservation activates in `us-east-1` during a partial network event. How would you differentiate between a genuine partition (keep self-preservation) and a mass-restart deployment (disable temporarily) at runtime?

2. **(C - Design Trade-off)** Eureka's 3-minute worst-case discovery latency is a consequence of its AP design. In what specific production scenario would you choose to accept this latency, and in what scenario would you switch to a CP registry even at the cost of occasional registry downtime?

3. **(A - System Interaction)** A Eureka client service's `@PreDestroy` shutdown hook fires, but the JVM is killed via `SIGKILL` before the deregister HTTP call completes. Map out every component that will be affected and the exact sequence of recovery events until the dead instance is removed from all clients' caches.
