---
id: MSV-006
title: Service Registry
category: Microservices
tier: tier-5-distributed-architecture
folder: MSV-microservices
difficulty: ★★☆
depends_on: MSV-001, MSV-002, MSV-003
used_by: MSV-007, MSV-014, MSV-039
related: MSV-007, MSV-014, MSV-039, MSV-040
tags:
  - microservices
  - distributed
  - intermediate
  - pattern
status: complete
version: 4
layout: default
parent: "Microservices"
grand_parent: "Technical Mastery"
nav_order: 6
permalink: /technical-mastery/microservices/service-registry/
---

⚡ TL;DR - A Service Registry is a database of live service
instances and their network addresses, enabling services to
discover each other dynamically without hardcoded endpoints.

| #006 | Category: Microservices | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Monolith vs Microservices, Microservices Architecture, Stateless Services | |
| **Used by:** | Service Discovery, Load Balancing in Microservices, Client-Side vs Server-Side Discovery | |
| **Related:** | Service Discovery, Load Balancing in Microservices, Client-Side vs Server-Side Discovery, Service Mesh | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You have 30 services. Each service calls 4-5 others. You hardcode
the IP addresses: `payment-service: 10.0.0.42:8080`. You deploy.
The IP changes because the container was restarted on a different
node. Everything breaks. You update the config. It breaks again.
You try DNS hostnames - they work until the DNS record is stale
and the service scaled from 2 to 10 instances but DNS still returns
the old 2. Requests pile on the 2 original instances while 8 new
instances sit idle.

**THE BREAKING POINT:**
In a dynamic environment (Kubernetes, cloud VMs, containerised
services), network addresses are ephemeral. A service can be
rescheduled to a different IP on every restart. Static config
is not just inconvenient - it is fundamentally incompatible
with elastic scaling.

**THE INVENTION MOMENT:**
This is exactly why the Service Registry was invented: a live,
self-updating directory that services register with on startup
and deregister on shutdown. Callers query the registry to get
current, healthy instance addresses, enabling discovery that
stays accurate even as the fleet changes dynamically.

**EVOLUTION:**
Early service registries: Apache Zookeeper (2008, originally
for Hadoop coordination). Netflix Eureka (2012) was purpose-built
for microservices. Consul (2014, HashiCorp) added health checking
and a key-value store. In the Kubernetes era (2015+), the
Kubernetes service DNS system largely replaced application-level
registries for internal service discovery, with the control
plane acting as the registry.

---

### 📘 Textbook Definition

A **Service Registry** is a centralised or distributed data store
that maintains a real-time catalogue of service instances: their
names, network locations (host:port), metadata (version, zone),
and health status. Services register on startup (self-registration)
or are registered by an external observer (third-party registration).
Callers query the registry at request time to obtain the current
set of healthy instances for a target service.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A Service Registry is the phone book for your microservices fleet
- updated in real-time as services start and stop.

**One analogy:**
> A hotel front desk is a Service Registry. When a guest arrives
> (service registers), they check in and get a room assignment
> (network address). When they leave (service deregisters), the
> room is removed from the available list. A visitor (caller)
> asks the front desk "where is John?" and gets the current
> room - not a stale address from a printed brochure.

**One insight:**
The registry solves the fundamental tension between elastic
infrastructure (IPs change) and service communication (need
stable addresses). The registry is the indirection layer that
absorbs infrastructure churn without exposing it to service code.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. The registry must reflect the current live state of the fleet -
   stale entries cause calls to dead instances.
2. Registration must be automatic (on startup) and deregistration
   must be automatic (on shutdown or health failure).
3. The registry itself must not be a single point of failure -
   it must be highly available (clustered).

**DERIVED DESIGN:**
From invariant 1: health checks are required. The registry must
actively probe each registered instance and remove unhealthy ones
rather than trusting self-reported status alone.
From invariant 2: a heartbeat mechanism: registered services
send heartbeats periodically. If heartbeats stop (crash, network
partition), the registry expires the entry after a TTL.
From invariant 3: registry clusters use consensus protocols
(Raft in Consul, ZAB in Zookeeper) to maintain consistent state
across nodes.

**THE TRADE-OFFS:**

**Gain:** Dynamic infrastructure support, accurate load balancing,
automatic failure detection, zero-touch routing updates.

**Cost:** Registry is now a critical infrastructure component;
its downtime impacts the entire fleet. Every service startup/
shutdown requires a registry interaction. Consistency lag (TTL
expiry) means some staleness is unavoidable.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

**Essential:** Any dynamic fleet needs a discovery mechanism.
The registry's core complexity (registration, heartbeat, query)
is inherent.

**Accidental:** In Kubernetes, the registry is built into the
control plane (kube-dns + endpoints controller). Application
teams don't write Eureka clients - the platform provides it.

---

### 🧪 Thought Experiment

**SETUP:**
Three instances of Order Service are running at 10.0.0.1,
10.0.0.2, and 10.0.0.3. Instance at 10.0.0.2 crashes. A
caller has a hardcoded list of the three addresses.

**WHAT HAPPENS WITHOUT SERVICE REGISTRY:**
Caller round-robins across all three. One in three requests
goes to 10.0.0.2 (dead). Caller gets connection refused.
Error rate is 33%. Caller must be manually updated with the
new IP after the dead instance is replaced.

**WHAT HAPPENS WITH SERVICE REGISTRY:**
Instance 10.0.0.2 misses 3 consecutive heartbeats. Registry
marks it unhealthy and removes it from the active list. Caller
queries registry: gets only 10.0.0.1 and 10.0.0.3. All requests
route to healthy instances. When a replacement starts at
10.0.0.4, it self-registers. Registry returns all three healthy
instances. Zero manual updates.

**THE INSIGHT:**
The registry turns infrastructure events (instance crash,
scale-up, redeploy) into routing updates automatically.
The fleet is self-healing because the registry closes the loop
between what is running and what is routable.

---

### 🧠 Mental Model / Analogy

> A Service Registry is like a live bus schedule board
> at a train station. Static bus route maps (hardcoded IPs)
> show you the planned routes but don't reflect cancellations
> or new services. The live board (registry) shows you
> which buses are actually running right now. You only board
> a bus shown as "on time" on the live board.

- "Static bus map" - hardcoded IP configuration
- "Live board" - the service registry
- "Bus on time" - healthy, registered instance
- "Cancelled bus" - unhealthy instance (removed from board)
- "New service added" - instance self-registers on startup

Where this analogy breaks down: a bus board is read-only for
travellers. In microservices, each service writes to the
registry when it starts (self-registration) - the sources
of truth are the services themselves.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
A Service Registry is a live list of all running services
and their addresses. When a service starts, it adds itself.
When it stops, it removes itself. Other services look up
the list to find where to send requests.

**Level 2 - How to use it (junior developer):**
With Spring Boot + Eureka: add `spring-cloud-starter-netflix-
eureka-client` to dependencies. Add `@EnableEurekaClient` to
the main class. Set `eureka.client.service-url.defaultZone`
to the registry URL. The service automatically registers on
startup and deregisters on shutdown.

**Level 3 - How it works (mid-level engineer):**
Registration: on startup, the service POSTs its metadata
(host, port, health URL, app name) to the registry.
Heartbeat: the service sends a PUT to the registry every
30 seconds (configurable). If 3 consecutive heartbeats are
missed (90 seconds), the registry marks the instance as
unhealthy and removes it from the list returned to callers.
Query: callers fetch the instance list (locally cached with
a 30-second refresh) and choose a target using client-side
load balancing.

**Level 4 - Why it was designed this way (senior/staff):**
The 30-second heartbeat and cache TTL create an inherent
discovery lag. An instance that just crashed may still appear
as healthy for up to 90 seconds. This is a deliberate
availability-vs-accuracy trade-off: a faster TTL (5 seconds)
would increase load on the registry from thousands of services.
Netflix Eureka explicitly chose availability over consistency
(AP in CAP terms): if the registry loses quorum, it keeps
serving stale data rather than refusing queries. Callers
must implement circuit breakers to handle the stale-entry
window.

**Level 5 - Mastery (distinguished engineer):**
In Kubernetes environments, the application-level registry
(Eureka, Consul) is largely replaced by the platform-level
registry: Kubernetes Endpoints objects (live IP list per
service), kube-dns for resolution, and the Kubernetes Endpoint
Slice controller for efficient updates. Staff engineers know
when application-level registries add value (multi-cloud,
multi-cluster, cross-namespace routing) vs when they add
unnecessary complexity on top of the platform's built-in
mechanism.

---

### ⚙️ How It Works (Mechanism)

**REGISTRATION LIFECYCLE:**

```
Service Instance Startup:
  1. Instance starts, initialises application
  2. POST /eureka/apps/ORDER-SERVICE
     {host: "10.0.0.5", port: 8080,
      healthCheckUrl:
        "http://10.0.0.5:8080/actuator/health"}
  3. Registry stores entry, marks as STARTING
  4. After first health check passes: marks as UP
  5. Instance appears in caller's instance list

Heartbeat (every 30s):
  PUT /eureka/apps/ORDER-SERVICE/10.0.0.5:8080
  → Registry updates lastUpdatedTimestamp

No heartbeat for 90s:
  → Registry marks instance as DOWN
  → Removes from the active instance list

Service Shutdown (graceful):
  DELETE /eureka/apps/ORDER-SERVICE/10.0.0.5:8080
  → Registry immediately removes instance
```

**QUERY AND CACHING:**

```
Caller (Payment Service):
  1. On startup: fetch full registry (all services)
     → cached locally
  2. Every 30s: delta fetch (only changes)
     → merge into local cache
  3. On request: look up ORDER-SERVICE in local cache
     → get list of healthy instances
     → client-side load balance (round-robin or ribbon)
     → call chosen instance
```

**KUBERNETES ALTERNATIVE:**

```
Without Eureka (Kubernetes-native):
  1. Service starts, kube-proxy registers endpoint
  2. Endpoints object: {10.0.0.5:8080, 10.0.0.6:8080}
  3. kube-dns: ORDER-SERVICE → ClusterIP (virtual IP)
  4. iptables/IPVS routes ClusterIP to real IPs
  5. Caller: HTTP GET http://order-service/orders/1
     → DNS resolves to ClusterIP
     → kube-proxy routes to healthy endpoint

No application code needed - platform handles everything
```

---

### 🔄 The Complete Picture - End-to-End Flow

**FULL DISCOVERY FLOW:**

```
Payment Service starts up
  │
  ▼
Eureka Client (embedded in Payment Service)
  │ POST registration
  ▼
┌─────────────────────┐
│  Eureka Registry    │  ← YOU ARE HERE
│  (clustered, HA)    │
└──────┬──────────────┘
       │ heartbeat every 30s
       │ delta fetch by callers every 30s
       ▼
Payment Service (caller)
  │ local cache: {ORDER-SERVICE: [10.0.0.5, 10.0.0.6]}
  │ chooses 10.0.0.5 (round-robin)
  ▼
Order Service instance at 10.0.0.5
```

**FAILURE PATH:**
```
Order Service instance 10.0.0.6 crashes
  → No heartbeat received by Eureka for 90s
  → Eureka marks 10.0.0.6 as DOWN
  → Next delta fetch by callers removes 10.0.0.6
  → All calls go to 10.0.0.5

GAP WINDOW: up to 90+30 = 120 seconds of potential
calls to dead instance before removal + cache expiry.
Circuit breaker must absorb this window.
```

**WHAT CHANGES AT SCALE:**
At 1000 instances registering 1 heartbeat every 30s = 33
registrations/second. At 10,000 instances = 333/sec. Delta
fetch from 500 callers every 30s adds read pressure. Eureka
uses a local cache per registry node to handle this. At 50,000
service instances, Kubernetes Endpoint Slices (chunked
endpoint lists) replace Endpoints objects for scalability.

---

### 💻 Code Example

**Example 1 - Wrong vs Right: hardcoded vs registry-based**

```java
// BAD: hardcoded service URL in configuration
@Service
public class OrderClient {
    // Breaks on any redeploy, scale-up, or IP change
    private static final String ORDER_URL =
        "http://10.0.0.42:8080";

    public OrderDTO getOrder(String id) {
        return restTemplate.getForObject(
            ORDER_URL + "/orders/" + id,
            OrderDTO.class);
    }
}
```

```java
// GOOD: service name used, resolved by registry
// Spring Cloud + Eureka auto-resolves ORDER-SERVICE
@Service
public class OrderClient {

    // @LoadBalanced tells Spring to resolve via registry
    private final RestTemplate restTemplate;

    public OrderDTO getOrder(String id) {
        // "ORDER-SERVICE" → Eureka → real IP:port
        return restTemplate.getForObject(
            "http://ORDER-SERVICE/orders/" + id,
            OrderDTO.class);
    }
}

@Configuration
public class RestTemplateConfig {
    @Bean
    @LoadBalanced  // REQUIRED: enables Eureka lookup
    public RestTemplate restTemplate() {
        return new RestTemplate();
    }
}
```

**Example 2 - Kubernetes service (no Eureka needed)**

```yaml
# Kubernetes Service - acts as built-in registry
apiVersion: v1
kind: Service
metadata:
  name: order-service  # DNS name for discovery
  namespace: production
spec:
  selector:
    app: order-service  # matches pod labels
  ports:
    - port: 80
      targetPort: 8080
  # Kubernetes handles: IP assignment, health filtering,
  # load balancing - no Eureka client needed
```

```java
// Caller in Kubernetes: use DNS name directly
@Value("${ORDER_SERVICE_URL:http://order-service}")
private String orderServiceUrl;

// "order-service" resolves to ClusterIP via kube-dns
// kube-proxy load-balances to healthy pods automatically
```

**How to test / verify correctness:**
In a test environment, start two instances of the target
service and one instance of the caller. Kill one target
instance. Verify all subsequent caller requests succeed
(no 503 errors) within 120 seconds (registry propagation
+ cache expiry window). Log which instance handles each
request to verify routing shifts entirely to the healthy
instance.

---

### ⚖️ Comparison Table

| Registry | Consistency | HA Model | Kubernetes-native | Best For |
|---|---|---|---|---|
| **Eureka** | AP (eventual) | Peer replication | No | Spring Cloud, AWS |
| Consul | CP/AP (tunable) | Raft consensus | Via operator | Multi-cloud, K/V store |
| Zookeeper | CP | ZAB consensus | No | Legacy Hadoop-adjacent |
| K8s Endpoints | Strong (etcd) | Built-in | Yes | Kubernetes-only fleets |
| K8s + Istio | Strong | Built-in | Yes | Service mesh + discovery |

**How to choose:** For Kubernetes deployments, use native
Kubernetes Service + DNS - no Eureka/Consul needed. For
multi-cloud or cross-cluster discovery, Consul is the mature
choice. Eureka is appropriate for Spring Cloud applications
on non-Kubernetes infrastructure.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Service Registry is necessary in Kubernetes | Kubernetes has a built-in registry (Endpoints + kube-dns). Application-level registries (Eureka) add redundant complexity in pure Kubernetes environments. |
| Registry removal is instant on instance crash | There is a 90-second heartbeat timeout + 30-second client cache = up to 120 seconds of stale entries. Circuit breakers must handle this window. |
| The registry solves load balancing | It provides the instance list. Load balancing is a separate concern (client-side ribbon or server-side load balancer). |
| Self-registration is always safe | A service can report as UP while its DB is down (false positive). Health checks must verify actual dependency health. |

---

### 🚨 Failure Modes & Diagnosis

**Split-brain: stale registry after network partition**

**Symptom:**
After a network partition, callers get 503 or connection
refused errors even though service instances are healthy.
The registry shows instances as DOWN that are actually UP.

**Root Cause:**
Registry nodes lost quorum during the partition. In
CP-mode (Consul), the registry refused writes/reads to
maintain consistency. In AP-mode (Eureka), stale data was
served. Services that re-registered after the partition
may not be visible to all registry nodes.

**Diagnostic Command:**
```bash
# Check Consul cluster health
consul operator raft list-peers
consul members | grep -v alive

# Check Eureka instances
curl http://eureka-server:8761/eureka/apps \
  | grep -E "<status>|<ipAddr>"

# Check if healthy instances are in registry
kubectl get endpoints order-service -o yaml
```

**Fix:**
For Eureka: restart Eureka servers to force full registry
re-sync. For Consul: follow Consul's split-brain recovery
procedure (rejoin lost members). In Kubernetes: `kubectl
rollout restart deployment order-service` forces pods to
re-register endpoints.

**Prevention:**
Run 3+ registry nodes for quorum. Monitor registry node
count in alerts. Health check registry availability
alongside service health.

---

**Health check passes but service is not ready**

**Symptom:**
New service instances appear in registry immediately after
startup but return 503 for the first 10-15 seconds. Users
see intermittent errors during deployments.

**Root Cause:**
Health endpoint returns HTTP 200 before the application
is fully warmed up (connection pools initialised, caches
populated, JIT compilation complete). Registry promotes
instance before it is ready to handle production traffic.

**Diagnostic Command:**
```bash
# Check time from registration to first request error
kubectl get events --field-selector \
  reason=Unhealthy -n production

# Check if readiness probe delays are configured
kubectl get pod order-service-xxx -o yaml \
  | grep -A10 readinessProbe
```

**Fix:**
```yaml
# Kubernetes: separate readiness from liveness
# Readiness gate: don't register until fully ready
readinessProbe:
  httpGet:
    path: /actuator/health/readiness
    port: 8080
  initialDelaySeconds: 30  # wait for JVM warmup
  periodSeconds: 5
  failureThreshold: 3

livenessProbe:
  httpGet:
    path: /actuator/health/liveness
    port: 8080
  initialDelaySeconds: 60  # allow for crash recovery
  periodSeconds: 10
```

**Prevention:**
Always distinguish readiness (ready to serve traffic) from
liveness (process is running). Readiness controls registry
inclusion; liveness controls container restart.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Microservices Architecture` - the context in which dynamic
  service discovery is required
- `Stateless Services` - services must be stateless for
  multiple registry entries to be interchangeable

**Builds On This (learn these next):**
- `Service Discovery` - how callers use the registry to find
  and route to services
- `Load Balancing in Microservices` - what happens with the
  instance list after discovery
- `Client-Side vs Server-Side Discovery` - the two patterns
  for how callers use the registry

**Alternatives / Comparisons:**
- `Service Mesh` - handles discovery (and much more) at the
  infrastructure layer; Istio eliminates the need for
  Eureka/Consul in Kubernetes environments
- `DNS-based discovery` - simpler, lower operational overhead,
  but lacks real-time health status and rich metadata

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Live database of healthy service instance│
│              │ and their network addresses              │
├──────────────┼──────────────────────────────────────────┤
│ PROBLEM IT   │ Dynamic IPs in elastic infrastructure -  │
│ SOLVES       │ hardcoded endpoints break on every restar│
├──────────────┼──────────────────────────────────────────┤
│ KEY INSIGHT  │ There is a 30-120s staleness window -    │
│              │ circuit breakers must absorb it          │
├──────────────┼──────────────────────────────────────────┤
│ USE WHEN     │ Non-Kubernetes service fleets; multi-clou│
│              │ or cross-cluster routing requirements    │
├──────────────┼──────────────────────────────────────────┤
│ AVOID WHEN   │ Pure Kubernetes - kube-dns + Endpoints   │
│              │ replaces Eureka/Consul at the platform   │
├──────────────┼──────────────────────────────────────────┤
│ ANTI-PATTERN │ Registry reports service UP while its DB │
│              │ is down - health checks must check deps  │
├──────────────┼──────────────────────────────────────────┤
│ TRADE-OFF    │ Dynamic routing + failure detection vs   │
│              │ critical infra dependency + staleness lag│
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "Your services' live phone book - always │
│              │  current, never stale for more than ~2min│
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Service Discovery → Load Balancing       │
│              │ → Client-Side vs Server-Side Discovery   │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Always verify actual dependency health in the health
   endpoint - a service with a dead DB should return DOWN,
   not UP.
2. There is a 90-second heartbeat + 30-second cache lag
   between instance death and removal from caller's view -
   circuit breakers must bridge this gap.
3. In Kubernetes, use native Service + kube-dns instead of
   Eureka/Consul unless you have cross-cluster or multi-cloud
   requirements.

**Interview one-liner:**
"A Service Registry is a live catalogue of healthy service
instances. Services register on startup, send heartbeats, and
deregister on shutdown. Callers query the registry to get
current healthy instances. In Kubernetes, the platform provides
this natively via Endpoints + kube-dns; application-level
registries like Eureka are only needed for non-Kubernetes or
multi-cloud scenarios."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Any system with dynamic membership needs an indirection layer
between addresses and identities. The identity (service name)
is stable; the address (IP:port) is ephemeral. The registry
is the mapping between them, and it must be as live as the
infrastructure.

**Where else this pattern appears:**
- DNS itself - maps stable domain names to changing IPs; TTL
  is the staleness trade-off parameter
- Load balancer backends - the LB's backend pool is a
  simpler form of service registry (no heartbeats, manual
  updates)
- Peer discovery in distributed systems (Kafka brokers,
  Elasticsearch nodes, Cassandra gossip protocol)

**Industry applications:**
- Netflix: Eureka was built in-house to solve this exact
  problem for their AWS microservices fleet; open-sourced
  as part of Netflix OSS
- HashiCorp Consul: used in large enterprise multi-cloud
  deployments where Kubernetes-native discovery is
  insufficient for cross-cluster routing

---

### 💡 The Surprising Truth

Netflix Eureka, one of the most widely deployed service
registries, was deliberately designed to be eventually
consistent (AP in CAP terms) rather than strongly consistent
(CP). During a network partition, Eureka continues serving
stale registry data rather than refusing requests. Netflix
engineers made this decision because, in their experience,
a slightly stale service list was recoverable (circuit
breakers handle dead instances), but a registry that went
unavailable during a partition caused cascading failures
across the entire fleet. Availability trumped accuracy.
This is an explicit, studied design decision - not a bug.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN** Describe to a junior engineer why hardcoded
   IPs break in Kubernetes and what the Service Registry
   provides that fixes this.
2. **DEBUG** Given an error log showing intermittent 503
   errors during a rolling deployment, determine whether
   the cause is registry staleness, failed health checks,
   or missing readiness probe delay.
3. **DECIDE** Choose between Eureka, Consul, and native
   Kubernetes Service discovery for: (a) a pure AWS EKS
   deployment, (b) a multi-cloud fleet spanning AWS and
   GCP, (c) a legacy VM-based fleet being migrated to containers.
4. **BUILD** Configure a Spring Boot application to register
   with Eureka including a health endpoint that checks
   database connectivity and returns DOWN if the DB
   is unreachable.
5. **EXTEND** Apply the Service Registry pattern to a WebRTC
   media server fleet where clients need to find the nearest
   server by geographic region. How would you extend the
   registry metadata to support this?

---

### 🧠 Think About This Before We Continue

**Q1.** An Eureka registry cluster has 3 nodes. Node 3
becomes partitioned from nodes 1 and 2. Callers connected
to Node 3 continue to operate with the cached registry
state. A new service instance registers via Node 1.
Trace: which callers see the new instance, when, and what
happens to requests that go to stale registry data on Node 3?
*Hint: Eureka is AP - it serves stale data rather than
refusing service during partitions.*

**Q2.** Your team is moving from a VM-based fleet using
Consul to a Kubernetes cluster. A consultant recommends
keeping Consul as the registry alongside Kubernetes. Your
senior engineer says to use only kube-dns. Walk through
the technical argument for each position and identify
the specific conditions that would make the consultant
correct.
*Hint: Consider cross-cluster routing, service mesh
capabilities, and operational overhead.*

**Q3.** Design a high-availability registry for a fleet
of 5000 services across 3 AWS regions, with the requirement
that no service registration is lost during an AWS regional
outage. What consistency model do you choose, how many
registry nodes per region, and how do you handle split-brain
scenarios?
*Hint: Think about the CAP theorem trade-off and what
"availability" means for a registry used by 5000 services.*

---

### 🎯 Interview Deep-Dive

**Q1: "What is the difference between a Service Registry
and DNS for service discovery?"**

*Why they ask:* Tests understanding of why specialised
registry systems exist rather than using existing DNS.

*Strong answer includes:*
- DNS TTL: typically 30-300s, slow to reflect instance
  failures (health-unaware)
- Registry: heartbeat-based, typically 90s failure detection,
  returns only healthy instances
- Registry provides rich metadata (version, zone, weights)
  that DNS does not natively support
- DNS is simpler operationally; registry adds features
  at the cost of another infrastructure component
- In Kubernetes, kube-dns + Endpoints bridges the gap:
  endpoints are updated by the platform in seconds

**Q2: "A service deployment fails halfway - 3 old instances
and 2 new instances are running. How does the registry
affect traffic routing?"**

*Why they ask:* Tests understanding of registry + rolling
deploys interaction.

*Strong answer includes:*
- All 5 instances are registered (both old and new versions)
- Callers receive all 5 from the registry and load-balance
  across them
- This means 40% of traffic goes to new (potentially
  incompatible) instances during rollout
- Mitigation: canary deployment (route 10% to new first),
  version labels in registry metadata for version-aware
  routing, or Kubernetes rolling deploy which manages this

**Q3: "How does the Service Registry interact with circuit
breakers?"**

*Why they ask:* Tests understanding of registry staleness
and the resilience patterns that compensate for it.

*Strong answer includes:*
- Registry has up to 120s staleness window (90s heartbeat
  + 30s client cache)
- During this window, callers can receive dead instances
  from the registry
- Circuit breaker detects consecutive failures to a specific
  instance and opens (stops routing to it) immediately
- Circuit breaker provides sub-second failure detection;
  registry provides eventual consistency
- The two patterns are complementary: registry for discovery,
  circuit breaker for runtime failure isolation