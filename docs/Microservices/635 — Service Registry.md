---
layout: default
title: "Service Registry"
parent: "Microservices"
nav_order: 635
permalink: /microservices/service-registry/
number: "635"
category: Microservices
difficulty: ★★☆
depends_on: "Monolith vs Microservices, Service Discovery"
used_by: "Service Discovery, Client-Side vs Server-Side Discovery, Health Check Patterns"
tags: #intermediate, #microservices, #networking, #distributed
---

# 635 — Service Registry

`#intermediate` `#microservices` `#networking` `#distributed`

⚡ TL;DR — A **Service Registry** is a database of service instances and their network locations (host + port). Services register themselves on startup and deregister on shutdown. Clients query the registry to discover where to send requests. Eureka, Consul, and Kubernetes Service Discovery are common implementations.

| #635            | Category: Microservices                                                        | Difficulty: ★★☆ |
| :-------------- | :----------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Monolith vs Microservices, Service Discovery                                   |                 |
| **Used by:**    | Service Discovery, Client-Side vs Server-Side Discovery, Health Check Patterns |                 |

---

### 📘 Textbook Definition

A **Service Registry** is a central database that maintains an up-to-date directory of all available service instances and their network addresses (IP + port). It is the foundation for dynamic service discovery in microservices environments where instances are constantly created and destroyed by auto-scaling, container orchestration, and deployments. Services interact with the registry through two mechanisms: **self-registration** — a service instance registers its own address with the registry on startup (via REST call or SDK) and sends periodic heartbeats to signal it is still alive; **third-party registration** — an external agent (e.g., Kubernetes controller, Consul agent) monitors deployments and updates the registry. Clients discover services by querying the registry for available instances of the desired service. The registry maintains health status by tracking heartbeat intervals — instances that miss heartbeats are removed from the registry (evicted). Common implementations: Netflix Eureka (Spring Cloud), HashiCorp Consul, Apache ZooKeeper, etcd (Kubernetes backend), and Kubernetes' built-in Service DNS (CoreDNS).

---

### 🟢 Simple Definition (Easy)

A Service Registry is the phone book of microservices. Every service registers its current address when it starts. When Service A wants to talk to Service B, it looks up Service B's current address in the registry. If B moves (new IP, new port), only the registry is updated — A always finds the latest address.

---

### 🔵 Simple Definition (Elaborated)

In a microservices environment, services are constantly starting and stopping — auto-scaling adds new instances, deployments replace old ones, failures restart containers. You cannot hardcode IP addresses. The Service Registry solves this: when `OrderService` starts on IP `10.0.1.23:8080`, it registers itself as "order-service" at that address. When `PaymentService` needs to call `OrderService`, it asks the registry: "where is order-service?" and gets back `10.0.1.23:8080`. If a second `OrderService` instance starts at `10.0.1.24:8080`, both are in the registry — the client can load balance between them. If an instance crashes and misses its heartbeat, it is automatically removed.

---

### 🔩 First Principles Explanation

**Service Registry lifecycle — registration, heartbeat, eviction:**

```
STARTUP:
  OrderService starts at 10.0.1.23:8080
  → Registers: POST /eureka/apps/ORDER-SERVICE
               body: {ipAddr:"10.0.1.23", port:8080, status:"UP"}
  Eureka stores: ORDER-SERVICE → [10.0.1.23:8080 (UP)]

HEARTBEAT:
  Every 30 seconds (default):
  → OrderService: PUT /eureka/apps/ORDER-SERVICE/10.0.1.23:8080
  → Eureka: last heartbeat = now (instance is alive)

SCALING:
  Auto-scaler adds second instance at 10.0.1.24:8080
  → 10.0.1.24 registers: PUT /eureka/apps/ORDER-SERVICE
  Eureka stores: ORDER-SERVICE → [10.0.1.23:8080 (UP), 10.0.1.24:8080 (UP)]

FAILURE:
  10.0.1.23 crashes — stops sending heartbeats
  After 90 seconds (3 missed × 30s): Eureka evicts 10.0.1.23:8080
  Eureka stores: ORDER-SERVICE → [10.0.1.24:8080 (UP)]

GRACEFUL SHUTDOWN:
  OrderService stops gracefully:
  → DELETE /eureka/apps/ORDER-SERVICE/10.0.1.23:8080
  Eureka immediately removes entry — no waiting for heartbeat timeout

DISCOVERY:
  PaymentService wants to call OrderService:
  → GET /eureka/apps/ORDER-SERVICE
  ← [10.0.1.24:8080] (only healthy instance)
  PaymentService caches this for 30 seconds, then refreshes
```

**Eureka's self-preservation mode:**

```
EUREKA PROBLEM: Network partition
  Scenario: 50 service instances are all running fine.
  Network failure isolates Eureka from all of them.
  Eureka receives 0 heartbeats → starts evicting ALL instances.
  Client queries Eureka → gets empty list → all service calls fail!

SELF-PRESERVATION SOLUTION:
  If Eureka receives < 85% of expected heartbeats in a time window:
  → It stops evicting instances (assumes network partition, not service failure)
  → Stale entries remain in the registry (instances that were healthy might be listed)
  → Clients may call dead instances (should have circuit breakers to handle this)

Trade-off: availability vs consistency
  Self-preservation: Available (clients have some addresses) but may have stale data
  Without self-preservation: Consistent (only live instances) but may be empty
```

**Kubernetes Service Discovery — built-in registry:**

```
Kubernetes eliminates the need for a separate registry:
  Service "order-service":
    spec.selector: {app: order-service}  ← matches pods with this label
    → Kubernetes creates: Endpoints resource with all matching pod IPs
    → CoreDNS resolves: order-service.default.svc.cluster.local → ClusterIP
    → kube-proxy routes ClusterIP → one of the healthy pod IPs

  Client calls: http://order-service:8080/api/orders
  → CoreDNS resolves to ClusterIP: 10.96.0.1
  → kube-proxy load balances to pod: 10.244.0.5:8080
  → No Spring Eureka client needed in Kubernetes!

  Service deregistration: when a pod is deleted or fails health check,
  Kubernetes removes it from Endpoints automatically → no stale entries
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT a Service Registry:

What breaks without it:

1. Hardcoded IP addresses in configuration files — every deployment change requires config updates.
2. Cannot scale horizontally — new instances have new IPs that clients do not know about.
3. Cannot handle failures transparently — a crashed instance's IP remains in all clients' configs.
4. Health status is unknown — clients send requests to instances that are starting up or shutting down.

WITH a Service Registry:
→ Service instances are discovered dynamically — IPs are never hardcoded.
→ Load balancing across multiple instances is automatic.
→ Unhealthy instances are removed from the registry — clients only get live endpoints.
→ Zero-downtime deployments: new instances register before old ones deregister.

---

### 🧠 Mental Model / Analogy

> A Service Registry is an airport arrivals board — it shows all gates (service instances) and their current status (up, down, loading). Passengers (client services) check the board to know which gate to go to. When a flight (service instance) gates out of service (crashes), it disappears from the board automatically — no passenger is directed to a closed gate. When a new gate opens (new instance starts), it appears on the board immediately — passengers can use it right away. The board does not care about individual passengers; it only maintains accurate gate availability.

"Airport arrivals board" = Service Registry (central directory)
"Gate number and status" = service instance IP:port + health status
"Passenger checking the board" = client service querying the registry
"Flight gating out" = service instance crashed, registry evicts it
"New gate opening" = new service instance starts, registers itself

---

### ⚙️ How It Works (Mechanism)

**Spring Cloud Eureka — setup:**

```java
// EUREKA SERVER (the registry):
@SpringBootApplication
@EnableEurekaServer
class ServiceRegistryApp {
    public static void main(String[] args) { SpringApplication.run(...); }
}
// application.yml:
// server.port: 8761
// eureka.client.registerWithEureka: false  ← Eureka server doesn't register itself
// eureka.client.fetchRegistry: false

// EUREKA CLIENT (a microservice that registers):
@SpringBootApplication
@EnableDiscoveryClient
class OrderServiceApp { ... }
// application.yml:
// spring.application.name: order-service
// eureka.client.serviceUrl.defaultZone: http://eureka-server:8761/eureka/
// eureka.instance.preferIpAddress: true

// DISCOVERING AND CALLING A SERVICE:
@Service
class OrderServiceClient {
    @Autowired DiscoveryClient discoveryClient;

    public List<ServiceInstance> getOrderServiceInstances() {
        return discoveryClient.getInstances("order-service");
        // Returns: [ServiceInstance{host="10.0.1.23", port=8080},
        //           ServiceInstance{host="10.0.1.24", port=8080}]
    }
}

// BETTER: Use Spring Cloud LoadBalancer (replaces Ribbon):
@Bean
@LoadBalanced  // annotated RestTemplate resolves "order-service" via registry
RestTemplate restTemplate() {
    return new RestTemplate();
}

restTemplate.getForObject("http://order-service/api/orders", OrderResponse[].class);
// "order-service" is resolved via Eureka → load balanced across instances
```

---

### 🔄 How It Connects (Mini-Map)

```
Microservices (many instances, dynamic IPs)
        │
        ▼
Service Registry  ◄──── (you are here)
(central directory: service name → healthy instances)
        │
        ├── Service Discovery → the process of using the registry to find services
        ├── Client-Side Discovery → client queries registry, picks instance, calls it
        ├── Server-Side Discovery → load balancer queries registry, routes to instance
        ├── Health Check Patterns → registry uses health checks to maintain accurate data
        └── API Gateway → uses registry to route requests to correct service instances
```

---

### 💻 Code Example

**Health check integration — Registry only returns healthy instances:**

```java
// Custom health indicator to affect registry status
@Component
class DatabaseHealthIndicator implements HealthIndicator {

    @Autowired DataSource dataSource;

    @Override
    public Health health() {
        try (Connection conn = dataSource.getConnection()) {
            if (conn.isValid(2)) {
                return Health.up()
                    .withDetail("database", "reachable")
                    .build();
            }
        } catch (SQLException e) {
            return Health.down()
                .withDetail("error", e.getMessage())
                .build();
        }
        return Health.down().withDetail("database", "unreachable").build();
    }
}
// When database is down:
// 1. /actuator/health → DOWN
// 2. Eureka receives DOWN status in next heartbeat
// 3. Eureka marks instance OUT_OF_SERVICE
// 4. Other services no longer receive this instance from registry
// 5. When database recovers: instance re-registers as UP → traffic resumes
```

---

### ⚠️ Common Misconceptions

| Misconception                                                    | Reality                                                                                                                                                                                                                                                     |
| ---------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| You need a separate Service Registry (like Eureka) in Kubernetes | Kubernetes provides built-in service discovery via DNS and kube-proxy. Adding Spring Cloud Eureka to a Kubernetes deployment is redundant and adds unnecessary complexity. Use Kubernetes-native service discovery unless running outside Kubernetes        |
| The Service Registry eliminates the need for circuit breakers    | The registry only contains instances that have sent recent heartbeats. An instance can be "registered as UP" but experiencing high latency or errors. Circuit breakers handle actual call failures; the registry handles address discovery. Both are needed |
| Service registration is always self-registration                 | In containerised environments (Docker, Kubernetes), services rarely self-register. Instead, the orchestration platform or a sidecar (Consul agent, registrator) handles registration — the service itself doesn't know it's in a registry                   |
| Registry data is always consistent across all nodes              | Eureka is designed for availability over consistency (AP in CAP theorem) — registry data may be slightly stale across Eureka server replicas. Consul uses Raft consensus (CP) — stronger consistency but more sensitive to network partitions               |

---

### 🔥 Pitfalls in Production

**Stale registry entries — calling dead instances**

```
SCENARIO: OrderService instance crashes but Eureka still lists it for 90 seconds
  PaymentService queries registry → gets stale IP → calls crashed instance
  Connection times out after 30s (default)

MITIGATION STACK:
  1. Decrease heartbeat interval: eureka.instance.leaseRenewalIntervalInSeconds=10
     (eviction lag: 3 missed × 10s = 30s instead of 90s)

  2. Circuit Breaker (Resilience4j):
     @CircuitBreaker(name = "order-service", fallbackMethod = "fallback")
     If 5 consecutive calls fail → circuit OPEN → fast fail instead of timeout

  3. Retry with instance selection:
     On connection failure → pick DIFFERENT instance from registry
     (Spring Cloud LoadBalancer supports this with RetryLoadBalancer)

  4. Readiness probe (Kubernetes):
     New instance only receives traffic when readiness probe passes
     → registry entry added only when service is ready
```

---

### 🔗 Related Keywords

- `Service Discovery` — the process that uses the Service Registry to find service instances
- `Client-Side vs Server-Side Discovery` — who queries the registry: the client or the load balancer
- `Health Check Patterns` — how the registry determines if an instance is healthy
- `API Gateway (Microservices)` — queries the registry to route requests to correct service instances
- `Circuit Breaker (Microservices)` — handles calls to registered-but-failing instances

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ PURPOSE      │ Directory: service name → instance IPs   │
├──────────────┼───────────────────────────────────────────┤
│ REGISTER     │ Self-registration (Eureka) or            │
│ HOW          │ Third-party (Kubernetes controller)      │
├──────────────┼───────────────────────────────────────────┤
│ HEALTH       │ Heartbeats (Eureka: 30s interval)        │
│              │ Miss 3 heartbeats → evicted (90s default)│
├──────────────┼───────────────────────────────────────────┤
│ TOOLS        │ Eureka (Spring Cloud), Consul, etcd,     │
│              │ Kubernetes CoreDNS (built-in)            │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Service Registry = phone book of        │
│              │  microservices, auto-updated on          │
│              │  startup, shutdown, and failure."       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Eureka is designed as an AP system (Availability over Consistency in CAP theorem) — it prioritises serving data (even stale) over refusing to serve when network partitions occur. Consul uses Raft consensus and is a CP system — it refuses to serve data if a quorum cannot be reached. Describe a concrete scenario where the choice between AP and CP registries affects system behaviour: during a network partition that isolates a subset of service instances, what does each registry serve to clients, and which behaviour is preferable for which type of service (stateless vs stateful, critical vs non-critical)?

**Q2.** In Kubernetes, service discovery uses CoreDNS and kube-proxy — entirely transparent to the application. But the DNS TTL for Kubernetes services is typically very short (5-30 seconds). Describe the `Pod` vs `Service` DNS resolution: why does a client calling `order-service.default.svc.cluster.local` always reach a healthy pod (assuming pod readiness probes pass), even without any application-level service registry? Explain the role of `Endpoints` resource, `EndpointSlice`, and the kube-proxy `iptables`/`ipvs` rules in routing ClusterIP traffic to individual pods.
