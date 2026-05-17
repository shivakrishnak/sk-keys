---
id: MSV-039
title: Client-Side vs Server-Side Discovery
category: Microservices
tier: tier-5-distributed-architecture
folder: MSV-microservices
difficulty: ★★★
depends_on: MSV-015, MSV-016
used_by: MSV-040, MSV-041
related: MSV-015, MSV-016, MSV-040, MSV-041, MSV-042
tags:
  - microservices
  - distributed
  - deep-dive
  - service-discovery
status: complete
version: 4
layout: default
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 39
permalink: /microservices/client-side-vs-server-side-discovery/
---

# MSV-039 - Client-Side vs Server-Side Discovery

⚡ TL;DR - Service Discovery solves: how does service A
find service B's address when instances scale up/down
dynamically? Two approaches: (1) Client-Side Discovery -
the calling service queries a Service Registry (Eureka,
Consul) for instance addresses, picks one using a
load-balancing algorithm, and calls it directly.
(2) Server-Side Discovery - the calling service calls
a load balancer/API Gateway, which queries the registry
and routes to an instance. Client-side: service is
smarter but more coupled. Server-side: simpler service,
but depends on load balancer infrastructure.

| #039 | Category: Microservices | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Service Registry, Load Balancing in Microservices | |
| **Used by:** | Service Mesh, Istio | |
| **Related:** | Service Registry, Load Balancing in Microservices, Service Mesh, Istio, Envoy Proxy | |

---

### 🔥 The Problem This Solves

**THE HARDCODED ADDRESS PROBLEM:**
In a monolith: `http://payment-server:8080`. One server.
In microservices: payment-service has 3 instances behind
an EKS node group. During peak: scales to 12 instances.
At night: scales to 1. IP addresses change with every
scale event. `http://10.0.0.55:8080` is gone after
scale-in. Hardcoded addresses break constantly.

Service Discovery: services register themselves in a
Service Registry on startup. Other services find them
by name, not by IP. Name: `payment-service`. Registry:
"payment-service has instances at 10.0.0.55, 10.0.0.56,
10.0.0.57". Client uses the name; the discovery
mechanism resolves to a live instance. When instances
scale: the registry is updated. Callers always find
a healthy instance.

---

### 📘 Textbook Definition

**Client-Side Discovery:** The calling service (client)
queries the Service Registry directly to get available
instances of the target service. The client applies
a load balancing algorithm (round-robin, least connections,
weighted) to select one instance and calls it directly.
Examples: Netflix Ribbon + Eureka (classic Spring Cloud),
Spring Cloud LoadBalancer + Consul.

**Server-Side Discovery:** The calling service sends
requests to a load balancer or API Gateway. The load
balancer queries the Service Registry and routes the
request to a target instance. The calling service knows
only the load balancer address, not individual instances.
Examples: AWS ALB + ECS Service Discovery, Kubernetes
Service (kube-proxy + DNS), Istio (Envoy sidecar handles
discovery), AWS API Gateway.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Client-side: the caller finds the target and calls
directly. Server-side: the caller calls a proxy, the
proxy finds the target.

**One analogy:**
> Client-Side = Self-driving car. The car queries Google
> Maps (Registry), picks a route (load balancing), drives
> itself. The car must have navigation software.

> Server-Side = Taxi. You call a dispatcher (load balancer).
> The dispatcher knows all available taxis (Registry)
> and assigns one. Your phone doesn't need navigation.
> You just say "get me to downtown".

**One insight:**
Kubernetes uses server-side discovery by default:
`ClusterIP` Service is the load balancer. `kube-proxy`
routes to pods. Services call `http://payment-service`;
DNS resolves to the ClusterIP; kube-proxy routes to
a pod. No client needs a Service Registry SDK. This
is why client-side discovery (Eureka/Ribbon) is less
common in modern Kubernetes environments - Kubernetes
provides server-side discovery natively.

---

### 🔩 First Principles Explanation

**CLIENT-SIDE DISCOVERY FLOW:**

```
  OrderService              ServiceRegistry    PaymentService
       |                         |              (3 instances)
       |  1. GET /services/      |                    |
       |     payment-service     |                    |
       |-----------------------> |                    |
       |                         |                    |
       |  2. [{ip: 10.0.0.55,    |                    |
       |     {ip: 10.0.0.56,     |                    |
       |     {ip: 10.0.0.57}]    |                    |
       | <---------------------- |                    |
       |                         |                    |
       |  3. Pick: 10.0.0.56     |                    |
       |     (round-robin)       |                    |
       |                         |                    |
       |  4. POST /payments      |                    |
       |-------------------------------------------> |
       |                         |                    |
       |  5. 200 OK              |                    |
       | <------------------------------------------ |

CLIENT IS RESPONSIBLE FOR:
- Registry query
- Health check filtering (exclude unhealthy instances)
- Load balancing algorithm
- Retry on failure (pick next instance)
```

**SERVER-SIDE DISCOVERY FLOW:**

```
  OrderService  LoadBalancer/Gateway  ServiceRegistry    PaymentService
       |               |                    |              (3 instances)
       |  1. POST       |                    |                    |
       |  /payments     |                    |                    |
       |-------------> |                    |                    |
       |               |  2. GET /services/ |                    |
       |               |     payment-service|                    |
       |               |-------------------> |                    |
       |               |                    |                    |
       |               |  3. [instances]    |                    |
       |               | <----------------- |                    |
       |               |                    |                    |
       |               |  4. Route to       |                    |
       |               |     10.0.0.57      |                    |
       |               |-------------------------------------------> |
       |               |                    |                    |
       |  5. 200 OK    |                    |                    |
       | <------------ |                    |                    |

LOAD BALANCER IS RESPONSIBLE FOR:
- Registry query
- Health check filtering
- Load balancing
- Retry on failure
CLIENT ONLY KNOWS: load balancer address
```

---

### 🧪 Thought Experiment

**KUBERNETES: WHICH DISCOVERY MODE?**

```
In Kubernetes:
  payment-service deployed as Deployment (3 replicas)
  Kubernetes Service: ClusterIP (server-side LB)
  DNS: payment-service.default.svc.cluster.local

  Order-service calls: http://payment-service/payments
  kube-dns resolves payment-service -> ClusterIP 10.96.0.10
  kube-proxy: iptables rules route 10.96.0.10 -> one of 3 pods
  
  ORDER-SERVICE HAS NO:
  - Eureka/Consul SDK
  - Load balancing code
  - Instance list management
  
  SERVER-SIDE DISCOVERY: Kubernetes handles all of it

WHEN WOULD YOU STILL USE CLIENT-SIDE?
  Service Mesh (Istio): Envoy sidecar = sophisticated
  client-side discovery per pod. But Envoy is injected
  automatically - application code still just calls
  http://payment-service (same as server-side from
  application developer perspective). Service mesh:
  best of both worlds.
  
  Legacy Spring Cloud (pre-Kubernetes):
  Ribbon + Eureka: true client-side discovery.
  Still exists in large enterprise Java environments.
```

---

### 🧠 Mental Model / Analogy

> Client-side discovery is like a traveller who books
> their own flights, hotels, and transfers directly.
> They have maximum control: pick the cheapest flight,
> the best hotel. But they do all the work. If an airline
> goes bankrupt: they call each airline directly.

> Server-side discovery is like using a travel agency.
> Tell the agency: "I need to get to Paris". The agency
> handles everything: finds flights, books hotels, arranges
> transfers. The traveller just shows up. The agency
> handles disruptions. Trade-off: less control, less
> effort, depends on the agency.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Services in microservices scale up and down. Their
addresses change. Service Discovery: services register
their address when they start. Other services find
addresses by name. Client-side: caller looks it up
directly. Server-side: a router looks it up for the
caller.

**Level 2 - How to use it (junior developer):**
In Spring Boot + Kubernetes: server-side is automatic.
Annotate: `@Service`, define a `Service` resource. Done.
In Spring Cloud + Eureka (legacy): add
`spring-cloud-starter-netflix-eureka-client`; annotate
`@EnableDiscoveryClient`. Use `@LoadBalanced RestTemplate`.
The template queries Eureka automatically.

**Level 3 - How it works (mid-level engineer):**
Kubernetes server-side: kube-dns + kube-proxy.
`payment-service` DNS resolves to ClusterIP. kube-proxy
maintains iptables/IPVS rules mapping ClusterIP to
pod IPs. Rules updated on pod creation/deletion.
No application code involved. Spring Cloud Eureka:
client registers `http://payment-service/eureka` on
startup with heartbeat every 30s. Ribbon queries
Eureka every 30s for instance list. Client-side round-robin
between instances. Ribbon uses Hystrix for failure
isolation and retry.

**Level 4 - Why it was designed this way (senior/staff):**
Client-side discovery (Eureka/Ribbon) emerged pre-Kubernetes,
when infrastructure-level load balancing was not available.
Netflix invented it for their AWS EC2 environment where
EC2 instances had dynamic IPs. The trade-off: client
become smarter (can implement custom load balancing like
AWS-zone-aware routing) but more complex (each client
must include discovery library). Kubernetes' server-side
discovery makes client-side obsolete for greenfield
projects. But client-side knowledge is still valuable
because service meshes (Istio) use Envoy as a per-pod
client-side proxy: the application is protected by the
sidecar, which does client-side discovery on its behalf.

**Level 5 - Mastery (distinguished engineer):**
Service Discovery in production at scale: the registry
is a critical path dependency. If Eureka/Consul is down:
clients can't discover new instances (but existing
cached instances still work for some time). Design:
client-side cache with TTL (Ribbon: 30s cache). Server-side
Kubernetes: kube-proxy caches iptables rules; partial
resistance to kube-dns failure. Service mesh (Istio
Pilot/istiod): pushes endpoint updates to all Envoy
sidecars proactively (push-based rather than pull-based
discovery). This "xDS protocol" means Envoy has current
instance list even if istiod is temporarily unavailable.
For sub-second scale events: Kubernetes endpoint
controllers + Envoy xDS gives sub-second discovery
convergence.

---

### ⚙️ How It Works (Mechanism)

**SPRING CLOUD CLIENT-SIDE DISCOVERY:**

```java
// Client-side discovery with Spring Cloud LoadBalancer
// (Replaces Ribbon in Spring Cloud 2020+)

// 1. Add dependency: spring-cloud-starter-loadbalancer
// 2. Enable discovery client
@SpringBootApplication
@EnableDiscoveryClient  // Register with Consul/Eureka
public class OrderServiceApplication { ... }

// 3. Use @LoadBalanced RestTemplate
@Configuration
public class RestTemplateConfig {
    @Bean
    @LoadBalanced  // Intercepts calls; resolves service names
    public RestTemplate restTemplate() {
        return new RestTemplate();
    }
}

// 4. Call by service name (not IP)
@Service
public class PaymentClient {
    @Autowired
    private RestTemplate restTemplate;

    public PaymentResult charge(PaymentRequest req) {
        // "payment-service" resolved via Consul/Eureka
        // LoadBalancer intercepts; selects instance
        return restTemplate.postForObject(
            "http://payment-service/payments",
            req, PaymentResult.class);
    }
}
```

**KUBERNETES SERVER-SIDE DISCOVERY:**

```yaml
# Server-side discovery: Kubernetes Service
apiVersion: v1
kind: Service
metadata:
  name: payment-service
spec:
  selector:
    app: payment-service
  ports:
    - port: 8080
      targetPort: 8080
  type: ClusterIP
# kube-proxy routes ClusterIP -> pod IPs automatically
# order-service calls http://payment-service:8080
# No discovery SDK needed in application code
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
CLIENT-SIDE DISCOVERY (Eureka + Ribbon):
  startup: payment-service registers in Eureka
  order-service start: pulls instance list from Eureka
  every 30s: order-service refreshes instance list
  every 30s: payment-service heartbeat to Eureka
  call time: Ribbon selects instance from local cache
  instance failure: Ribbon detects (CircuitBreaker)
                   removes from rotation; retry next

SERVER-SIDE DISCOVERY (Kubernetes):
  startup: payment pod starts; Endpoint controller
           adds pod IP to payment-service Endpoints
  kube-proxy: updates iptables rules on every node
  call time: DNS lookup payment-service -> ClusterIP
             iptables routes to one pod IP
  pod failure: kubelet marks pod unhealthy
               Endpoint controller removes from Endpoints
               kube-proxy updates iptables (< 1 second)
```

---

### 💻 Code Example

**Example 1 - Failure: stale registry cache**

```java
// BAD: Calling a stale instance (client-side cache)
// Eureka cache: payment-service at 10.0.0.55, 10.0.0.56
// Reality: 10.0.0.55 was replaced 20 seconds ago
// New instance: 10.0.0.58 (not yet in cache)
// Ribbon picks 10.0.0.55 -> connection refused
// No retry configured -> 500 error to customer
```

```java
// GOOD: Resilient client-side discovery
@Configuration
public class FeignConfig {
    @Bean
    public Retryer retryer() {
        // Retry with different instance on connection failure
        return new Retryer.Default(
            100,   // initial interval ms
            1000,  // max interval ms
            3      // max attempts
        );
    }
}

// With Spring Cloud LoadBalancer: configure retry
// spring.cloud.loadbalancer.retry.enabled=true
// spring.cloud.loadbalancer.retry.maxRetriesOnSameServiceInstance=1
// spring.cloud.loadbalancer.retry.maxRetriesOnNextServiceInstance=2

// With Resilience4j retry + Feign:
@FeignClient(
    name = "payment-service",
    configuration = FeignConfig.class
)
@Retry(name = "paymentRetry")
public interface PaymentClient {
    @PostMapping("/payments")
    PaymentResult charge(PaymentRequest request);
}
// On connection failure: retries pick next instance
// (LoadBalancer selects fresh instance each retry)
```

---

### ⚖️ Comparison Table

| Aspect | Client-Side Discovery | Server-Side Discovery |
|---|---|---|
| **Client complexity** | High (SDK needed) | Low (call LB address) |
| **Load balancing flexibility** | High (custom algorithms) | LB-dependent |
| **Single point of failure** | Registry (client caches) | Load Balancer |
| **Language support** | Must have SDK per language | Language-agnostic |
| **Kubernetes native** | Not built-in | Built-in (kube-proxy) |
| **Examples** | Eureka + Ribbon, Consul | AWS ALB, K8s Service, Istio |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Kubernetes doesn't do service discovery | Kubernetes has built-in server-side discovery: ClusterIP Service + kube-proxy + DNS. It's so transparent that many developers don't realize it IS service discovery. |
| Client-side discovery is obsolete | Not with service meshes. Envoy (Istio's sidecar) is a sophisticated client-side discovery proxy. Application code doesn't need SDK, but the pattern is client-side. |
| Service Registry is a single point of failure | With caching: clients cache instance lists. If Eureka is down for 30 seconds, existing instances are still routable. But NEW instances added during the outage won't be discovered until Eureka recovers. |

---

### 🚨 Failure Modes & Diagnosis

**Eureka split-brain: instances keep appearing/disappearing**

**Symptom:**
Production: order-service intermittently fails to
call payment-service. Logs show: `No instances available
for payment-service`. But payment-service pods are
running. Errors come and go every 30 seconds.

**Root Cause:**
Eureka server is operating in "self-preservation mode".
Eureka detected fewer heartbeats than expected (network
glitch). To prevent cascading deregistration: enters
self-preservation mode and STOPS evicting instances.
But the clients have stale instance lists that include
instances that have scaled down. Some calls hit
deregistered instances -> connection refused.

**Diagnostic:**
```bash
# Check Eureka self-preservation mode
curl http://eureka-server:8761/eureka/apps/ | grep -i selfPreservation

# Check instance list from client perspective
curl http://eureka-server:8761/eureka/apps/PAYMENT-SERVICE
# Look for instance status: UP vs OUT_OF_SERVICE vs DOWN

# Check client cache refresh interval
# spring.cloud.loadbalancer.cache.ttl: 35s (default)
# Stale cache = stale instances
```

**Fix:**
1. Increase heartbeat frequency for network-sensitive
   environments. Default: 30s. Aggressive: 5s.
2. Enable Ribbon/LoadBalancer retry (retry on different
   instance on connection failure).
3. Reduce Eureka server response cache (eureka.server
   .responseCacheUpdateIntervalMs: 30000 -> 5000).
4. In Kubernetes: migrate to server-side discovery
   (kube-proxy). Eliminate Eureka complexity entirely.

---

### 🔗 Related Keywords

**Prerequisites:**
- `Service Registry` - the registry that both discovery
  patterns depend on
- `Load Balancing in Microservices` - client-side applies
  LB algorithms; server-side relies on LB

**Applied In:**
- `Service Mesh` - service mesh implements server-side
  discovery transparently via sidecar proxy
- `Istio` - istiod distributes endpoint info via xDS;
  Envoy sidecars handle actual routing
- `Envoy Proxy` - Envoy is a sophisticated client-side
  discovery proxy in service mesh

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ CLIENT-SIDE  │ Caller queries registry, picks instance  │
│              │ SDK per language, Eureka+Ribbon example  │
├──────────────┼───────────────────────────────────────────┤
│ SERVER-SIDE  │ Caller -> LB -> registry -> instance      │
│              │ Language-agnostic, K8s default, Istio     │
├──────────────┼───────────────────────────────────────────┤
│ KUBERNETES   │ Server-side by default (ClusterIP + DNS) │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Client-side: SDK in caller. Server-side:  │
│              │  transparent LB. K8s: built-in server-side"│
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Client-side discovery: caller queries registry and
   picks instance (SDK required). Server-side: caller
   calls load balancer; LB handles discovery.
2. Kubernetes uses server-side discovery by default
   (ClusterIP Service + kube-proxy + DNS). Most modern
   Spring Boot on K8s doesn't need Eureka.
3. Service Mesh (Istio/Envoy) is a transparent client-side
   discovery proxy: the app calls by name; Envoy sidecar
   does client-side discovery on app's behalf.

**Interview one-liner:**
"Client-Side Discovery: the calling service queries a
Service Registry (Eureka/Consul) for target instances
and applies its own load balancing (Ribbon). Server-Side:
the caller calls an intermediary (AWS ALB, Kubernetes
Service, Istio sidecar) that handles registry lookup
and routing. Kubernetes uses server-side by default:
kube-proxy + DNS. Trade-off: client-side is more
flexible (custom LB algorithms, zone-aware routing)
but requires a discovery SDK in every service in every
language. Server-side is language-agnostic."

---

### 💡 The Surprising Truth

The most common question: "Do I need Eureka if I use
Kubernetes?" Answer: almost never. Kubernetes provides
server-side service discovery out of the box. Eureka
in Kubernetes is usually a legacy migration artifact:
teams that migrated to Kubernetes still have Eureka
because it was already in the codebase. The Eureka
server itself must be deployed as a Kubernetes
Deployment, adding operational overhead with no benefit
over kube-proxy. The migration path: replace `@LoadBalanced
RestTemplate` with a standard RestTemplate calling
kubernetes service names, and decommission Eureka.
Most teams that complete this migration report: simpler
architecture, fewer moving parts, and no loss of
functionality.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **DIAGRAM** Draw the request flow for both client-side
   and server-side discovery, showing the registry
   interaction at each step.
2. **K8S** Explain exactly how a Spring Boot service in
   Kubernetes discovers other services without Eureka:
   DNS lookup, ClusterIP, kube-proxy, iptables rules.
3. **DEBUG** Given logs showing `No instances available
   for payment-service`: distinguish between registry
   sync lag, self-preservation mode, and network partition.
4. **MIGRATE** Design the migration plan from Eureka
   client-side discovery to Kubernetes server-side
   discovery without downtime.
5. **MESH** Explain how Istio/Envoy sidecar implements
   discovery: what protocol (xDS), what component
   pushes updates (istiod/Pilot), where instance lists
   are cached (Envoy xDS cache).

---

### 🧠 Think About This Before We Continue

**Q1.** Your Spring Boot application on Kubernetes is
using Eureka for service discovery. Performance testing
shows a 30ms latency added for Eureka registry queries.
Propose a migration to Kubernetes-native service
discovery. What changes are required in code, YAML,
and infrastructure? What are the risks?

**Q2.** In a multi-cloud setup (AWS + GCP), services
in AWS must discover services in GCP. Neither cloud's
native service discovery (AWS Service Discovery vs
GCP Service Directory) is compatible with the other.
What service discovery strategy would you use?

**Q3.** A new team member says: "We should use Consul
for service discovery because it also provides
configuration management, health checking, and key-value
store - it's a one-stop shop." Evaluate this argument
in a Kubernetes environment. What does K8s already
provide? When would Consul actually add value?