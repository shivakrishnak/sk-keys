---
layout: default
title: "Service Registry"
parent: "Microservices"
nav_order: 15
permalink: /microservices/service-registry/
number: "MSV-015"
category: Microservices
difficulty: ★★☆
depends_on: Monolith vs Microservices, Networking, HTTP & APIs
used_by: Service Discovery, Client-Side vs Server-Side Discovery, Health Check Patterns
related: Service Discovery, Load Balancing, API Gateway
tags:
  - microservices
  - networking
  - distributed
  - intermediate
  - pattern
---

# MSV-015 — Service Registry

⚡ TL;DR — A Service Registry is a central database of running service instances and their network locations, enabling services to find each other dynamically without hardcoded addresses.

| #635 | Category: Microservices | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Monolith vs Microservices, Networking, HTTP & APIs | |
| **Used by:** | Service Discovery, Client-Side vs Server-Side Discovery, Health Check Patterns | |
| **Related:** | Service Discovery, Load Balancing, API Gateway | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Your microservices configuration files hardcode IP addresses: `payments.service.host=192.168.10.45`. This worked fine until your Kubernetes cluster auto-scaled during a traffic spike — new payment service pods started at different IP addresses. Worse, the 192.168.10.45 pod crashed and was replaced with 192.168.10.182. Your order service is still calling a dead IP. Orders fail with connection refused. The on-call alert fires at 2am.

**THE BREAKING POINT:**
In a containerised microservices environment, IP addresses are ephemeral. A pod restart, an auto-scale event, a rolling deployment — any of these changes the IP. Hardcoded IPs are maintained configuration lies that cause production failures.

**THE INVENTION MOMENT:**
This is exactly why Service Registries were created — to provide a live, authoritative directory of which service instances are healthy and reachable right now, so clients always have current network locations.

---

### 📘 Textbook Definition

A **Service Registry** is a centralised, highly available key-value store that maps logical service names to the current network locations (host, port, and potentially metadata) of healthy service instances. Services register themselves on startup and deregister on shutdown — or are deregistered automatically when health checks fail. Clients (or load balancers) query the registry to resolve a service name to a specific instance before making a call. The registry is the foundation of dynamic service discovery in microservices architectures.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A live phone book for microservices — lists which services are available and where to find them right now.

**One analogy:**
> Think of a hotel concierge. Guests (services) don't carry a map of every restaurant in the city. They ask the concierge (service registry) for a recommendation. The concierge records which restaurants are currently open (registered, healthy) and directs guests accordingly. If a restaurant closes midday (service crashes), the concierge stops recommending it immediately.

**One insight:**
The key word is "live." A service registry isn't DNS (which caches stale entries). It is a near-real-time directory that reflects the actual current state of the system — including which instances just crashed two seconds ago.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Service instances have dynamic, ephemeral IP addresses in containerised environments.
2. A client must know the current IP of a service before making a call.
3. The registry must be at least as available as the services that depend on it — if the registry goes down, service discovery fails.

**DERIVED DESIGN:**
Given Invariant 1 and 2, discovery must be dynamic — a static mapping is invalidated by every deployment or crash. The registry solves this by becoming the source of truth for current instance locations.

Given Invariant 3, the registry itself is deployed with high availability (3-node cluster minimum for Consul, peer-based replication for Eureka). Clients typically cache registry data locally, so brief registry outages don't immediately break service calls.

**Registration patterns:**
- **Self-registration**: the service registers itself on startup and deregisters on shutdown (Spring Cloud with Eureka)
- **Third-party registration**: a deployment system (Kubernetes) registers/deregisters services automatically (sidecar agent)

**THE TRADE-OFFS:**
**Gain:** Dynamic discovery of healthy instances, support for auto-scaling and rolling deployments, health-based routing.
**Cost:** The registry is a new critical dependency — if it fails and caches expire, service discovery breaks; additional operational complexity to deploy and maintain the registry.

---

### 🧪 Thought Experiment

**SETUP:**
Three payment service pods are running. The order service needs to call payments. Without a registry, it has 3 hardcoded IPs.

**WITHOUT SERVICE REGISTRY:**
Pod `payments-2` crashes and Kubernetes starts `payments-4` at a new IP. The order service's config still has the old IP for `payments-2`. 33% of order service requests fail with "connection refused." The order service is not down, but its call success rate is 67%.

**WITH SERVICE REGISTRY:**
Pod `payments-2` fails its health check → registry deregisters `payments-2` within 10 seconds → order service queries registry → registry returns only the 2 healthy pod IPs → order service distributes calls across healthy instances → call success rate stays near 100%

**THE INSIGHT:**
A service registry gives clients a continuously accurate view of the available service landscape. Without it, clients carry stale knowledge and make calls into the void.

---

### 🧠 Mental Model / Analogy

> A Service Registry is like a traffic management centre that tracks which roads are currently open. Cars (service calls) don't decide their route based on a map printed last year. They query the traffic centre (registry) for the current best path. When a road is blocked (service instance crashes), the traffic centre (registry) removes it from available routes within seconds, before any more cars use that road.

- "Traffic management centre" → service registry (Consul, Eureka, etcd)
- "Roads" → service instance network endpoints
- "Cars checking traffic" → clients querying the registry before each call
- "Blocked road removed from routes" → failed health check → deregistration

Where this analogy breaks down: most service clients cache registry data and don't query on every single call — so there is a brief stale window after a service fails before all clients know about it.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A service registry is a shared address book that microservices update when they start or stop. Other services look up this address book to find where to send their requests.

**Level 2 — How to use it (junior developer):**
In a Spring Boot application with Eureka: add `spring-cloud-starter-netflix-eureka-client` to your dependencies. Add `@EnableEurekaClient` to your app, configure the Eureka server URL, and the app registers itself on startup. Use `@LoadBalanced RestTemplate` or Feign clients with just the service name — Spring resolves the address via Eureka at call time.

**Level 3 — How it works (mid-level engineer):**
Service registry implementations (Eureka, Consul, etcd/Kubernetes) store service records as `{serviceName → [instance1:8080, instance2:8081]}`. Each instance sends periodic heartbeats (every 30s in Eureka). If three consecutive heartbeats are missed, the instance is deregistered. Clients cache the registry locally (typically for 30–60 seconds) to avoid a registry call on every API call. The client-side load balancer selects an instance from the cached list using a strategy (round-robin, least-connections).

**Level 4 — Why it was designed this way (senior/staff):**
Netflix developed Eureka when migrating to AWS around 2012. AWS instances had dynamic IPs that changed with every auto-scale event — hardcoded IP configs became unmaintainable at their scale (hundreds of services). Eureka's design prioritised availability over consistency (AP over CP in CAP theorem terms): if the registry loses network contact with some instances, it continues returning potentially stale data rather than refusing to respond. This "self-preservation mode" trades accuracy for availability. Consul, by contrast, uses Raft consensus (CP), providing consistency at the cost of availability during network partitions. The choice between AP and CP registries depends on whether stale discovery or failed discovery is more harmful for your services.

---

### ⚙️ How It Works (Mechanism)

**Registration and discovery flow:**

```
┌──────────────────────────────────────────────┐
│        Service Registry Flow                 │
├──────────────────────────────────────────────┤
│ 1. Service starts → registers with registry  │
│    POST /register {name: "payments",         │
│                    host: "10.0.1.5",         │
│                    port: 8080,               │
│                    healthCheck: "/health"}   │
├──────────────────────────────────────────────┤
│ 2. Registry records instance                 │
│    Registry: {payments → [10.0.1.5:8080]}   │
├──────────────────────────────────────────────┤
│ 3. Registry polls health check               │
│    GET http://10.0.1.5:8080/health           │
│    200 → instance healthy                    │
│    Connection refused → deregister           │
├──────────────────────────────────────────────┤
│ 4. Caller queries registry                   │
│    GET /discover/payments                    │
│    ← [{host: 10.0.1.5, port: 8080}]          │
├──────────────────────────────────────────────┤
│ 5. Caller selects instance (load balance)    │
│    calls http://10.0.1.5:8080/api/pay        │
├──────────────────────────────────────────────┤
│ 6. Service shuts down → deregisters          │
│    DELETE /register/payments/10.0.1.5:8080   │
└──────────────────────────────────────────────┘
```

**Spring Boot + Eureka registration:**

```java
// pom.xml dependency
// spring-cloud-starter-netflix-eureka-client

// application.yml
spring:
  application:
    name: payments-service          # logical name in registry
eureka:
  client:
    service-url:
      defaultZone: http://eureka:8761/eureka/
  instance:
    prefer-ip-address: true
    lease-renewal-interval-in-seconds: 10  # heartbeat
    lease-expiration-duration-in-seconds: 30
```

**Client-side lookup with Feign:**

```java
@FeignClient(name = "payments-service")  // logical name, not IP
public interface PaymentsClient {
    @PostMapping("/payments")
    PaymentResult charge(@RequestBody ChargeRequest request);
}
// Spring resolves "payments-service" to a real IP via Eureka
```

**Consul service registration (alternative):**

```hcl
# consul service definition
service {
  name = "payments-service"
  port = 8080
  check {
    http = "http://localhost:8080/health"
    interval = "10s"
    timeout = "2s"
  }
}
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
Service A needs to call Service B → Queries Service Registry ← YOU ARE HERE → Registry returns healthy instances of B → Client load balancer picks one instance → HTTP call made to selected instance → Response returned to A

**FAILURE PATH:**
Service B instance crashes → Health check fails → Registry deregisters B instance (within 10–30s TTL) → Client's cached registry entry expires → Client re-queries registry → Updated list returned (no crashed instance) → Calls route to remaining healthy instances

**WHAT CHANGES AT SCALE:**
At 1000 services with 10 instances each, the registry stores 10,000 entries. Health check polling becomes significant load — Consul uses a gossip protocol to distribute health check responsibility. At 10,000 instances, the registry's write throughput (constant heartbeats) requires a distributed registry (Consul cluster, Kubernetes etcd cluster) rather than a single-node Eureka. Client-side caching with appropriate TTLs is mandatory at this scale.

---

### 💻 Code Example

**Example 1 — BAD: Hardcoded service URL:**

```java
// BAD: hardcoded IP fails when service restarts
@Service
public class OrderService {
    private final RestTemplate rest = new RestTemplate();

    public PaymentResult pay(Order order) {
        // Will break on service restart / pod replacement
        return rest.postForObject(
            "http://192.168.10.45:8080/payments",
            order, PaymentResult.class
        );
    }
}
```

**Example 2 — GOOD: Service name resolved via registry:**

```java
// GOOD: logical name resolved to live IP via Eureka
@Configuration
public class RestConfig {
    @Bean
    @LoadBalanced  // enables registry-based resolution
    public RestTemplate restTemplate() {
        return new RestTemplate();
    }
}

@Service
public class OrderService {
    private final RestTemplate rest;

    public PaymentResult pay(Order order) {
        // "payments-service" resolved to live IP at call time
        return rest.postForObject(
            "http://payments-service/payments",
            order, PaymentResult.class
        );
    }
}
```

**Example 3 — Consul health check configuration:**

```yaml
# Service with health check in Docker Compose
payments-service:
  image: payments:latest
  labels:
    - "consul.service.name=payments-service"
    - "consul.check.http=/health"
    - "consul.check.interval=10s"
  # Consul agent watches this container and registers it
  # when healthy, deregisters when health check fails
```

---

### ⚖️ Comparison Table

| Registry | Consistency | Availability | Protocol | Best For |
|---|---|---|---|---|
| **Eureka** | AP (eventual) | High | HTTP | Spring Cloud; tolerates network partitions |
| Consul | CP (strong) | Medium | HTTP + DNS + gRPC | Strong consistency; service mesh integration |
| etcd | CP (Raft) | Medium | gRPC | Kubernetes native; config + discovery |
| Kubernetes DNS | Eventual | High | DNS | K8s environments; simple hostname resolution |
| Zookeeper | CP | Medium | Custom | Legacy; prefer Consul for new systems |

How to choose: use Eureka for Spring Cloud systems that need high availability; use Consul for multi-cloud or strong consistency requirements; rely on Kubernetes DNS if running in K8s (built-in).

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| A service registry replaces DNS | DNS is coarse-grained and caches TTLs of minutes; a registry syncs in seconds and carries health status and metadata beyond just IP addresses |
| If the registry goes down, all service calls fail | Clients cache registry data locally — brief registry outages are masked by cached entries; only extended outages (exceeding TTL) break resolution |
| Service registry is only needed for microservices | Any system where service instances start/stop dynamically (containers, serverless) benefits from dynamic service discovery |
| Kubernetes doesn't need a service registry | Kubernetes provides its own service registry via kube-dns and the Endpoints API — it is a built-in registry, not absent |
| Self-registration is always better than third-party registration | Self-registration is simpler to implement; third-party (e.g., Kubernetes watching pods) is more reliable because the service doesn't need to handle its own registration on crash |

---

### 🚨 Failure Modes & Diagnosis

**1. Stale Registry Cache — Calls to Crashed Instance**

**Symptom:** After a service pod is terminated, some clients still receive connection refused errors for 30–60 seconds.

**Root Cause:** Client-side cache TTL has not expired. Clients are still calling the deregistered instance's IP.

**Diagnostic:**
```bash
# Check Eureka registry for stale instances
curl http://eureka:8761/eureka/apps/PAYMENTS-SERVICE | \
  python3 -m json.tool | grep -A5 "instanceId"
# Shows registered instances and their lastRenewalTimestamp
```

**Fix:** Reduce client-side cache TTL (Ribbon: `ribbon.ServerListRefreshInterval=5000`) and registry heartbeat window. Accept a slightly higher registry query rate in exchange for faster convergence.

**Prevention:** Design clients with circuit breakers — even with stale cache, a circuit breaker detects dead instances quickly and opens to stop routing to them.

**2. Registry as Single Point of Failure**

**Symptom:** Eureka server crashes. All service discovery fails. New service instance deployments cannot register. Services with expired caches start returning "no instances available."

**Root Cause:** Single Eureka instance with no peer replication configured.

**Diagnostic:**
```bash
# Check Eureka cluster health
curl http://eureka1:8761/eureka/status
curl http://eureka2:8761/eureka/status
# Should show peer replication working
```

**Fix:**
```yaml
# Eureka peer configuration — at least 2 instances
eureka:
  client:
    service-url:
      defaultZone: >
        http://eureka1:8761/eureka/,
        http://eureka2:8761/eureka/
  server:
    enable-self-preservation: true
```

**Prevention:** Deploy registry with minimum 3 nodes across different availability zones. Never deploy a single-instance registry.

**3. Services Registering with Wrong Health Status**

**Symptom:** Registry shows a service as healthy, but calls to it fail with 500 errors. The health check endpoint returns 200 even when the service is in a broken state.

**Root Cause:** Health check endpoint (`/actuator/health`) reports UP regardless of actual application state (e.g., database is unreachable but the health endpoint doesn't check it).

**Diagnostic:**
```bash
# Check what the health endpoint actually reports
curl http://payments-service:8080/actuator/health | python3 -m json.tool
# Look for: db, rabbit, redis sub-health contributors
```

**Fix:**
```yaml
# Spring Boot: include dependency health checks
management:
  health:
    db:
      enabled: true       # check DB connectivity
    rabbit:
      enabled: true       # check RabbitMQ connectivity
  endpoint:
    health:
      show-details: always
# Service reports DOWN if DB unreachable → registry deregisters
```

**Prevention:** Health check endpoints must check all mission-critical dependencies, not just whether the process is running.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Monolith vs Microservices` — service registries exist because microservices have multiple dynamic instances; a monolith doesn't need one
- `Networking` — understanding TCP/IP, DNS, and port-based addressing is foundational for understanding why registries are needed
- `Health Check Patterns` — registries rely on health checks to know which instances to include in their directory

**Builds On This (learn these next):**
- `Service Discovery` — the process of using a service registry to find available instances before making a call
- `Client-Side vs Server-Side Discovery` — the two patterns for how clients use registry data to route requests
- `Load Balancing` — how clients or proxies distribute calls across the instances returned by the registry

**Alternatives / Comparisons:**
- `Kubernetes DNS` — the built-in service registry for Kubernetes deployments using stable DNS names per Service
- `API Gateway (Microservices)` — can act as a registry-aware load balancer, abstracting registry queries from individual service clients

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ A live directory mapping service names    │
│              │ to healthy instance network addresses     │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Dynamic IP addresses in containerised     │
│ SOLVES       │ envs make hardcoded configs unworkable    │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ The registry must be more available than  │
│              │ the services that use it — it is critical │
│              │ infrastructure                            │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Services have dynamic IP addresses or     │
│              │ auto-scale, making static config fragile  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Services run with stable DNS names (e.g., │
│              │ Kubernetes services) — DNS is sufficient  │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Dynamic accurate discovery vs registry    │
│              │ as a new critical dependency              │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "A live phone book that hangs up on       │
│              │  dead numbers automatically."             │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Service Discovery → Health Check Patterns │
│              │ → Client-Side vs Server-Side Discovery    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your service registry (Eureka) enters "self-preservation mode" during a network partition — it stops deregistering instances that haven't sent heartbeats, to avoid falsely removing healthy instances that are merely temporarily unreachable. During this mode, your order service continues receiving the deregistered (but still-alive-network-wise) instances in its call rotation. Some of those instances have a memory leak and should have been replaced. Explain the exact trade-off Eureka is making in self-preservation mode, and design a client-side circuit breaker strategy that protects the calling service even when the registry is providing stale data.

**Q2.** You are migrating from Eureka (client-side discovery, AP) to Consul (server-side discovery, CP) across 80 services. During the migration, some services use Eureka and some use Consul. A service using Eureka needs to call a service that has already migrated to Consul. Design the coexistence strategy — including any bridge components or dual-registration approach — that allows both discovery systems to work simultaneously without requiring an all-or-nothing cutover.

