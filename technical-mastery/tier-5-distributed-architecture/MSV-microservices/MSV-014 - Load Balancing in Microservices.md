---
id: MSV-014
title: Load Balancing in Microservices
category: Microservices
tier: tier-5-distributed-architecture
folder: MSV-microservices
difficulty: ★★☆
depends_on: MSV-006, MSV-007, MSV-008
used_by: MSV-039, MSV-040
related: MSV-006, MSV-007, MSV-039, MSV-040, MSV-044
tags:
  - microservices
  - distributed
  - intermediate
  - networking
status: complete
version: 4
layout: default
parent: "Microservices"
grand_parent: "Technical Mastery"
nav_order: 14
permalink: /technical-mastery/microservices/load-balancing-in-microservices/
---

⚡ TL;DR - Load Balancing in Microservices is the mechanism
for distributing requests across multiple healthy instances
of a service. The choice between client-side and server-side
load balancing, and the algorithm used, directly affects
latency distribution and failure handling.

| #014 | Category: Microservices | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Service Registry, Service Discovery, Health Check Patterns | |
| **Used by:** | Client-Side vs Server-Side Discovery, Service Mesh | |
| **Related:** | Service Registry, Service Discovery, Client-Side vs Server-Side Discovery, Service Mesh, Circuit Breaker | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Order Service has 3 instances. All requests go to instance 1
(hardcoded URL). Instance 1 is overwhelmed: CPU 95%, P99
latency 800ms. Instances 2 and 3 are idle (CPU 5%, latency
20ms). Your system has plenty of capacity, but it is all
going to the wrong place. Scaling up adds more idle capacity.
Instance 1 crashes from overload. All orders fail because
the other two instances are not being used.

**THE BREAKING POINT:**
Without load balancing, horizontal scaling is ineffective.
Adding instances does not help if all traffic goes to one.
The single instance becomes both a performance bottleneck
and a single point of failure.

**THE INVENTION MOMENT:**
Load balancing is the mechanism that makes horizontal
scaling actually work: distributing requests across all
healthy instances so capacity is used proportionally and
no single instance is a bottleneck or single point of failure.

---

### 📘 Textbook Definition

**Load Balancing in Microservices** is the practice of
distributing incoming requests across multiple healthy
instances of a service to prevent any single instance from
being overwhelmed, maximise resource utilisation, and provide
fault tolerance. Load balancing in microservices is
categorised by location: **client-side** (the caller
distributes requests using a local instance list) and
**server-side** (an intermediary proxy or virtual IP
distributes requests on behalf of the caller). The
distribution algorithm (round-robin, least connections,
weighted, consistent hashing) determines how requests
are spread across instances.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Load balancing spreads requests across all healthy instances
so no single instance is overwhelmed and no single failure
stops the service.

**One analogy:**
> A checkout counter in a supermarket. Without load balancing:
one checkout is open, a queue of 50 people. Five checkouts
are open but only one is signed in. Load balancing: all five
checkouts open, a supervisor routes customers to the shortest
queue. Each customer is served faster, the system serves
more customers per hour.

**One insight:**
Load balancing is not just about performance - it is about
fault tolerance. If one of three instances fails, a load
balancer with health checking automatically stops routing
to the failed instance. Without it, one-third of requests
fail permanently until someone manually updates the config.

---

### 🔩 First Principles Explanation

**TWO LOCATIONS:**

```
CLIENT-SIDE LOAD BALANCING:
──────────────────────────────
Service A (caller):
  Has local list: [10.0.0.1, 10.0.0.2, 10.0.0.3]
  Applies round-robin: picks 10.0.0.1, then .2, then .3
  Refreshes list from registry every 30s
  
Advantage: no extra hop, caller controls algorithm
Disadvantage: each caller needs LB library,
              language-specific, list refresh lag

SERVER-SIDE LOAD BALANCING:
──────────────────────────────
Service A (caller):
  Sends to: http://order-service (DNS name)
  ↓
  Load Balancer / kube-proxy / Envoy
  Has instance list: [10.0.0.1, 10.0.0.2, 10.0.0.3]
  Picks one, forwards request

Advantage: language-agnostic, no library needed
Disadvantage: extra hop (1-5ms), LB is critical path
```

**LOAD BALANCING ALGORITHMS:**

```
ROUND-ROBIN: 1→2→3→1→2→3
  Best when: all instances equally capable
  Problem: ignores instance load state

WEIGHTED ROUND-ROBIN: 1(weight:3)→2(weight:1)
  Best when: instances have different capacities
  (larger VM gets more requests)

LEAST CONNECTIONS: pick instance with fewest active
  requests
  Best when: requests have variable processing time
  Problem: requires tracking active connections

CONSISTENT HASHING: hash(userId) % N → same instance
  Best when: sticky sessions needed (user-affinity caching)
  Problem: uneven distribution if hash is poor

RANDOM: pick a random healthy instance
  Best when: stateless, uniform load, simple
```

---

### 🧪 Thought Experiment

**SETUP:**
Payment Service has 3 instances:
- Instance 1: fast SSD-backed, 100ms avg response
- Instance 2: fast SSD-backed, 100ms avg response
- Instance 3: HDD-backed, 400ms avg response

**WITH ROUND-ROBIN:**
One-third of requests go to Instance 3 (400ms).
P99 latency is dominated by Instance 3.
Overall P99: ~400ms.

**WITH LEAST CONNECTIONS:**
Instance 3 accumulates a backlog (slow to complete).
Fewer new requests are routed to it (high active count).
More requests route to Instances 1 and 2 (fast completion).
Overall P99: ~150ms.

**WITH WEIGHTED ROUND-ROBIN:**
Instance 3 given weight=1, Instances 1 and 2 given weight=3.
Only 14% of requests to Instance 3 instead of 33%.
Overall P99: ~120ms.

**THE INSIGHT:**
Algorithm selection matters. Round-robin is the wrong
choice for heterogeneous instance pools. At scale,
the difference between P99=400ms and P99=150ms is
the difference between missing and meeting an SLO.

---

### 🧠 Mental Model / Analogy

> Load balancing is like a traffic director at a busy
> intersection during rush hour. Round-robin = waving
> cars through in strict alternation. Least connections
> = looking at each lane's queue and directing to the
> shortest. Consistent hashing = directing the same
> driver to the same lane every time (for familiarity
> / cache efficiency). The algorithm is the traffic
> director's decision rule.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Load balancing sends each incoming request to a different
server in rotation so no single server gets all the work.
If one server goes down, the others handle all requests.

**Level 2 - How to use it (junior developer):**
In Spring Cloud + Eureka: `@LoadBalanced` on `RestTemplate`
enables client-side LB via Spring Cloud LoadBalancer.
Kubernetes: `ClusterIP` service provides server-side LB
via kube-proxy. No code changes needed - just use the
service DNS name.

**Level 3 - How it works (mid-level engineer):**
Spring Cloud LoadBalancer: maintains an instance cache
(refreshed from Eureka every 30s). On each request, applies
round-robin algorithm across healthy instances. Supports
plugging in custom algorithms. kube-proxy: installs iptables
rules that DNAT (destination NAT) the ClusterIP to a real
pod IP using a round-robin selection per new TCP connection.

**Level 4 - Why it was designed this way (senior/staff):**
Kubernetes kube-proxy's iptables mode does per-connection
load balancing (not per-request). For HTTP keep-alive
connections (gRPC, connection pools), all requests on a
long-lived connection go to the SAME pod. This means gRPC
client to Kubernetes service gets zero load balancing after
the first connection. The fix: use Istio (sidecar Envoy
balances per-request on HTTP/2 streams) or use a headless
Kubernetes service (returns all pod IPs to DNS, client
does client-side LB).

**Level 5 - Mastery (distinguished engineer):**
The P2C (Power of Two Choices) algorithm used by Envoy and
modern load balancers is statistically superior to round-robin
for heterogeneous workloads: pick two random instances,
choose the one with fewer active requests. This provides
near-optimal distribution without the complexity of tracking
all instances' load. Staff engineers also understand
"slow start" mode: newly added instances should receive
less traffic initially (JVM warm-up, connection pool
filling, JIT compilation) - configurable in Envoy and
Nginx as `slow_start` duration.

---

### ⚙️ How It Works (Mechanism)

**SPRING CLOUD LOADBALANCER (client-side):**

```java
// Configuration: custom algorithm
@Configuration
public class LoadBalancerConfig {

    @Bean
    public ReactorLoadBalancer<ServiceInstance>
        roundRobinLoadBalancer(
            Environment env,
            LoadBalancerClientFactory factory) {

        String name = env.getProperty(
            LoadBalancerClientFactory.PROPERTY_NAME);
        return new RoundRobinLoadBalancer(
            factory.getLazyProvider(
                name, ServiceInstanceListSupplier.class),
            name);
    }
}
```

**KUBERNETES IPTABLES LOAD BALANCING:**

```
Service: order-service (ClusterIP: 10.96.0.5)
Endpoints: {10.0.0.1:8080, 10.0.0.2:8080, 10.0.0.3:8080}

iptables rules (simplified):
-A KUBE-SVC-ORDER -m statistic --mode random \
  --probability 0.33 -j KUBE-SEP-ENDPOINT-1
-A KUBE-SVC-ORDER -m statistic --mode random \
  --probability 0.50 -j KUBE-SEP-ENDPOINT-2
-A KUBE-SVC-ORDER -j KUBE-SEP-ENDPOINT-3

-A KUBE-SEP-ENDPOINT-1 -j DNAT \
  --to-destination 10.0.0.1:8080
# etc.

Probability: 1/3, then 1/2, then 1/1
Result: statistically even distribution across 3 pods
Granularity: per new TCP connection (not per HTTP request)
```

**IPVS MODE (more efficient):**
```
IPVS (IP Virtual Server) modes:
  rr:  round-robin
  lc:  least-connection
  dh:  destination hashing
  sh:  source hashing (sticky sessions)
  sed: shortest expected delay
  nq:  never queue

Advantage: O(1) lookup vs O(N) iptables scan
Use for: >1000 services (iptables becomes slow)
```

---

### 🔄 The Complete Picture - End-to-End Flow

**HEALTH-AWARE LOAD BALANCING:**

```
Order Service (3 instances, 1 unhealthy):
  Instance 1: healthy (CPU 30%, latency 80ms)
  Instance 2: healthy (CPU 40%, latency 100ms)
  Instance 3: unhealthy (readiness probe FAIL)

Client-side (Spring Cloud LB):
  Registry cache: [instance 1, instance 2] (3 excluded)
  Round-robin: alternates 1 and 2
  Instance 3 is never sent a request

Server-side (Kubernetes):
  Endpoints: {10.0.0.1:8080, 10.0.0.2:8080}
  (instance 3 removed by endpoints controller)
  kube-proxy: DNAT to 1 or 2 only
```

**WHAT CHANGES AT SCALE:**
```
10 services, 3 instances each:   30 iptables rules
100 services, 10 instances each: 1000 iptables rules
500 services, 20 instances each: 10000 iptables rules
  → kube-proxy update latency increases
  → Consider: IPVS mode, Cilium eBPF, Istio sidecar LB
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: gRPC + kube-proxy LB**

```java
// BAD: gRPC via Kubernetes ClusterIP
// HTTP/2 connection is persistent
// All gRPC streams go to same pod (connection-level LB)
ManagedChannel channel = ManagedChannelBuilder
    .forAddress("order-service", 50051)  // ClusterIP
    .usePlaintext()
    .build();
OrderServiceGrpc.OrderServiceBlockingStub stub =
    OrderServiceGrpc.newBlockingStub(channel);
// Problem: channel connects to ONE pod and stays there
// Other pods idle; first pod overwhelmed
```

```java
// GOOD: headless service for gRPC client-side LB
// Kubernetes headless service: ClusterIP: None
// DNS returns all pod IPs, gRPC round-robins across them
ManagedChannel channel = ManagedChannelBuilder
    .forTarget("dns:///order-service-headless:50051")
    .defaultLoadBalancingPolicy("round_robin")
    .usePlaintext()
    .build();
// gRPC's built-in LB distributes streams across all pods
// via DNS-resolved IP list (client-side LB)
```

**Example 2 - Kubernetes headless service YAML**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: order-service-headless
spec:
  clusterIP: None  # Makes it headless
  selector:
    app: order-service
  ports:
    - port: 50051
      name: grpc
# DNS: order-service-headless → [10.0.0.1, 10.0.0.2, 10.0.0.3]
# All pod IPs returned to DNS client
# gRPC client-side LB distributes per stream
```

---

### ⚖️ Comparison Table

| Type | Location | Granularity | Health-aware | Best For |
|---|---|---|---|---|
| **Client-side (Ribbon)** | In caller | Per request | Yes (via registry) | Spring Cloud, non-K8s |
| **kube-proxy iptables** | Node | Per TCP connection | Yes (Endpoints) | HTTP/1.1 on K8s |
| **kube-proxy IPVS** | Node | Per TCP connection | Yes (Endpoints) | Large K8s clusters |
| **Istio Envoy** | Sidecar | Per HTTP request | Yes (Envoy health) | gRPC, advanced algorithms |
| **AWS ALB** | Cloud | Per request | Yes (target health) | External traffic |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Kubernetes service does per-request load balancing | kube-proxy iptables does per-NEW-CONNECTION. Existing connections (HTTP keep-alive, gRPC streams) are not rebalanced. Istio or client-side LB is needed for per-request granularity. |
| More instances always means better load balancing | More instances only help if the LB algorithm distributes to them. Round-robin with 10 instances but one being 10x slower = 10% of requests at worst latency. Least-connections or P2C adapts to instance speed. |
| Load balancer removes the need for circuit breakers | LB removes healthy routing to a known-down instance. Circuit breaker stops cascading failure when an instance is slow but not down. Both are needed. |

---

### 🚨 Failure Modes & Diagnosis

**Uneven load distribution (hot spots)**

**Symptom:**
Grafana shows one pod at 90% CPU, others at 15%. Load is
not evenly distributed despite round-robin configuration.

**Root Cause:**
HTTP keep-alive or connection pooling (Feign/WebClient)
establishes persistent connections. Round-robin only fires
on new connections. The caller established 1 connection
per pod at startup (even distribution), but connection
reuse means all subsequent requests use existing connections.
If one caller has a disproportionate load, all its requests
go to one pod.

**Diagnostic Command:**
```bash
# Check connection count per pod (TCP ESTABLISHED)
kubectl exec -it order-service-xxx -- \
  ss -tn state established | wc -l

# Check request rate per pod
# (Prometheus + Kubernetes pod labels)
rate(http_server_requests_total{app="order-service"}[1m])
  by (pod)

# Istio per-pod request distribution (if service mesh)
istioctl proxy-stats order-service-xxx.default | \
  grep upstream_rq_total
```

**Fix:**
For HTTP/1.1 clients: reduce keepalive timeout to force
connection recycling. For gRPC: use headless service or
Istio sidecar (per-stream LB). For HTTP/2: use Istio
or configure connection pool limits.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Service Registry` - provides the instance list that
  client-side LB uses
- `Service Discovery` - the mechanism by which callers find
  the list of instances to load balance across
- `Health Check Patterns` - defines which instances are
  eligible for load balancing

**Builds On This (learn these next):**
- `Client-Side vs Server-Side Discovery` - deep dive on the
  two patterns
- `Service Mesh` - handles load balancing (plus much more)
  at the infrastructure layer

**Alternatives / Comparisons:**
- `Circuit Breaker` - complements LB: LB distributes healthy
  routing; circuit breaker stops cascading failures from
  slow-but-not-dead instances

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ CLIENT-SIDE  │ Caller holds instance list, picks one    │
│              │ Algorithm: round-robin, least-conn, P2C  │
├──────────────┼──────────────────────────────────────────┤
│ SERVER-SIDE  │ Proxy/VIP picks instance transparently   │
│              │ kube-proxy: per-connection (iptables/IPVS│
├──────────────┼──────────────────────────────────────────┤
│ gRPC TRAP    │ kube-proxy ClusterIP = per-connection LB │
│              │ Use headless service or Istio for gRPC   │
├──────────────┼──────────────────────────────────────────┤
│ ALGORITHM    │ Homogeneous fleet: round-robin           │
│ CHOICE       │ Variable latency: least-conn or P2C      │
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "Spread requests across healthy instances│
│              │  so no single pod is the bottleneck"     │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Client-Side vs Server-Side Discovery     │
│              │ → Service Mesh → Circuit Breaker         │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. kube-proxy load balances per TCP connection, not per
   HTTP request. gRPC over a Kubernetes ClusterIP service
   does NOT get per-request load balancing.
2. Least-connections or P2C outperforms round-robin when
   instance response times vary (heterogeneous hardware,
   JVM GC pauses, varying query complexity).
3. Load balancing + circuit breaking are complementary:
   LB avoids known-bad instances; circuit breaker handles
   degraded (slow but alive) instances.

**Interview one-liner:**
"Load balancing distributes requests across healthy service
instances. Client-side (Spring Cloud LB, Ribbon) does it
in the caller using a registry-sourced instance list.
Server-side (kube-proxy, Nginx, Istio) does it transparently
in a proxy. Key production gotcha: Kubernetes kube-proxy
load balances per TCP connection, not per request - gRPC
streams and HTTP keep-alive connections stick to one pod.
Istio sidecar proxies fix this with per-request routing."

---

### 💡 The Surprising Truth

Round-robin is statistically the worst load balancing
algorithm for microservices with JVM garbage collection.
During a GC pause (50-500ms for G1GC, up to several seconds
for old-gen collection), an instance cannot respond.
Round-robin continues sending requests to it, which queue
up and timeout. Least-connections would detect the high
active-connection count on the GC-paused instance and
route away from it during the pause. P2C (Power of Two
Choices) achieves near-optimal distribution by sampling
two random instances and choosing the less loaded one -
statistically proven to be within a constant factor of
optimal, O(log log N) maximum load vs O(log N / log log N)
for round-robin under adversarial load patterns.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN** Why gRPC over Kubernetes ClusterIP service
   does not get per-request load balancing and the two
   correct solutions (headless service or Istio sidecar).
2. **CHOOSE** Select the correct LB algorithm for: (a) a
   homogeneous fleet of stateless services, (b) a fleet
   with mixed instance sizes, (c) a stateful service
   requiring user affinity.
3. **DEBUG** Given a hot-spot where one pod handles 80%
   of load, identify from metrics whether the cause is
   connection reuse, algorithm misconfiguration, or a
   sticky-session bug.
4. **CONFIGURE** Set up IPVS mode in Kubernetes for a
   cluster with 500+ services, and enable least-connections
   algorithm.
5. **EXTEND** Design a global load balancing strategy for
   a multi-region deployment that considers geographic
   latency, region capacity, and failover behaviour.

---

### 🧠 Think About This Before We Continue

**Q1.** A service has 3 pods: 2 on fast nodes (100ms
avg), 1 on a slow node (400ms avg). Round-robin sends
33% to the slow node. Calculate: (a) overall P50 latency,
(b) P99 latency. Then design a weighted round-robin
configuration that limits slow-node traffic to 10%
and recalculate P50 and P99.

**Q2.** You have a gRPC OrderService with 5 pods behind
a Kubernetes ClusterIP service. A load test shows one
pod receiving 80% of requests, others nearly idle. The
client uses a single gRPC channel. Trace the technical
reason for this distribution, then enumerate ALL the
correct solutions in order of operational complexity.

**Q3.** A connection pool in Service A connects to
Service B (3 instances). Pool size: 30 connections.
kube-proxy iptables mode, random probability per connection.
Calculate the expected distribution of connections across
the 3 instances. What is the probability that all 30
connections end up on the same instance? How does
increasing the pool size affect the distribution?
(Hint: use the birthday problem / balls-in-bins model.)