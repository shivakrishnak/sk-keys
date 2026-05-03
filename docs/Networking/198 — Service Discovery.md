---
layout: default
title: "Service Discovery"
parent: "Networking"
nav_order: 198
permalink: /networking/service-discovery/
number: "0198"
category: Networking
difficulty: ★★★
depends_on: DNS, Load Balancer L4_L7, Microservices
used_by: Kubernetes, Distributed Systems, Spring Core, Service Mesh
related: DNS, East-West vs North-South Traffic, Load Balancer L4_L7, Network Policies, Overlay Networks
tags:
  - networking
  - service-discovery
  - consul
  - eureka
  - kubernetes-dns
  - client-side
  - server-side
---

# 198 — Service Discovery

⚡ TL;DR — Service Discovery solves the dynamic addressing problem: in microservices, service instances start, stop, and scale constantly — you can't hardcode IPs. Services register themselves (service registry) and clients discover available instances at request time. Two patterns: **client-side** (client queries registry, picks instance, calls directly — e.g., Eureka + Ribbon) and **server-side** (client calls load balancer, LB queries registry — e.g., Kubernetes Service + kube-dns).

---

### 🔥 The Problem This Solves

In static infrastructure, a config file maps service names to IPs: `payment-service=10.0.1.5`. This breaks completely when: (a) service scales to 10 instances with 10 different IPs; (b) Kubernetes assigns new pod IPs every restart; (c) Auto-scaling adds/removes instances in seconds; (d) Blue-green deployments change which instances are "active". Service Discovery provides a dynamic registry where services announce themselves and clients query real-time instance lists.

---

### 📘 Textbook Definition

**Service Discovery:** The mechanism by which services in a distributed system locate each other dynamically, without relying on static IP addresses or configuration. Consists of: (1) **Service Registry**: a database of available service instances and their locations (IP:port, health status); (2) **Service Registration**: services register on startup and deregister on shutdown; (3) **Health Checking**: registry monitors instance health, removes unhealthy instances; (4) **Service Lookup**: clients query registry to find healthy instances.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Service Discovery = dynamic phone book for microservices. Services register their address on startup; clients look up addresses at request time. No hardcoded IPs.

**One analogy:**

> Service discovery is like a hotel concierge service. When a new restaurant opens nearby, it registers with the concierge (service registry). When you need a restaurant recommendation (service lookup), the concierge tells you which restaurants are currently open and available (health checking). You don't need to know the addresses in advance — the concierge maintains the current list.

---

### 🔩 First Principles Explanation

**CLIENT-SIDE DISCOVERY:**

```
Classic: Netflix Eureka + Ribbon (Spring Cloud)

  Service A starts:
    → Register with Eureka: "payment-service @ 10.0.1.15:8080"
    → Eureka stores registry entry
    → Heartbeat every 30s to maintain registration

  Service B wants to call payment-service:
    → Query Eureka: "give me all instances of payment-service"
    → Eureka returns: [10.0.1.15:8080, 10.0.1.22:8080, 10.0.1.31:8080]
    → Ribbon (client-side LB): pick one (round-robin or weighted)
    → Service B calls 10.0.1.22:8080 directly

  Advantages:
    - Client can implement sophisticated LB logic
    - No extra hop through server-side LB
    - Client knows all instances; can route by metadata (version, region)

  Disadvantages:
    - Each client must implement discovery logic
    - Registry client code in every service (polyglot problem)
    - Client cache of instances can be stale (TTL issue)
```

**SERVER-SIDE DISCOVERY:**

```
Modern: Kubernetes DNS + kube-proxy (Services)

  Service A starts (Kubernetes Pod):
    → Kubernetes creates pod with IP (e.g., 192.168.1.50)
    → Pod added to Service's Endpoints object
    → kube-dns entry: payment-service.production.svc.cluster.local

  Service B wants to call payment-service:
    → DNS query: payment-service.production.svc.cluster.local
    → kube-dns returns: ClusterIP (e.g., 10.96.45.100) — VIRTUAL IP
    → kube-proxy (iptables/eBPF) intercepts traffic to ClusterIP
    → DNAT (Destination NAT) to one of the actual pod IPs
    → Traffic reaches pod directly

  Client doesn't know about multiple instances!
  Load balancing hidden by kube-proxy.

  Advantages:
    - No discovery logic in client code
    - Works for any language/framework
    - Kubernetes manages registration/deregistration automatically

  Disadvantages:
    - Less sophisticated LB (kube-proxy = round-robin by default)
    - No client-side awareness of instance metadata
    - For advanced LB: need service mesh (Istio/Linkerd)
```

**SERVICE MESH SERVICE DISCOVERY (ENVOY/XDS):**

```
Istio uses xDS (Discovery Service) APIs:
  - EDS (Endpoint Discovery Service): dynamic endpoint lists
  - CDS (Cluster Discovery Service): cluster configs
  - RDS (Route Discovery Service): HTTP routing rules
  - LDS (Listener Discovery Service): listener configs

Flow:
  1. Istiod (control plane) watches Kubernetes API
     → Service A pods added/removed: Istiod notified
  2. Envoy sidecars receive xDS updates (endpoint lists)
  3. When Service B calls Service A:
     → Envoy intercepts (iptables redirect)
     → Envoy has up-to-date endpoint list from xDS
     → Envoy applies LB policy (round-robin, least-request, etc.)
     → Direct pod-to-pod call (via Envoy sidecars)

Advantage: Envoy knows all endpoints AND health; sophisticated LB
  (outlier detection: auto-remove endpoints with high error rates)
```

**CONSUL SERVICE DISCOVERY:**

```
HashiCorp Consul: multi-platform, supports K8s and VMs

  Registration (service-side):
    consul.register(service="payment-service", port=8080, tags=["v2"])

  Discovery (client):
    instances = consul.health.service("payment-service", passing=True)
    # Returns only healthy instances

  Health checking:
    Consul performs active health checks (HTTP GET /health every 10s)
    Unhealthy instance: removed from DNS/API results immediately

  DNS interface:
    payment-service.service.consul
    → returns A records for all healthy instances
    → Standard DNS; any client can use it

  Service Mesh (Consul Connect):
    Similar to Istio: sidecar proxies, mTLS, intentions (authz policies)
```

---

### 🧪 Thought Experiment

**THE STALE CACHE PROBLEM:**
Eureka client caches instance list for 30 seconds. Service B cached 3 instances of payment-service. Instance 10.0.1.15 crashes. In the next 30s, Service B's cache still shows all 3 instances. 33% of requests to payment-service will fail until cache expires. Mitigation: (a) implement retry logic (if one instance fails, try another from cache); (b) reduce TTL (more load on Eureka); (c) use Kubernetes Services (kube-proxy handles health tracking and removes crashed pods immediately via endpoint watch).

---

### 🧠 Mental Model / Analogy

> Service Discovery is like the DNS system itself, but for internal services. DNS translates human-readable names (google.com) to IP addresses. Service Discovery translates service names (payment-service) to dynamic instance addresses. Kubernetes DNS is literally DNS — it's just serving internal Kubernetes service records. The key difference from external DNS: these records change every few seconds as pods scale up/down, and clients need the changes reflected immediately (short TTLs, watch-based updates).

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Service Discovery = dynamic name-to-address lookup for microservices. Kubernetes handles it automatically: when you create a Service, kube-dns creates a DNS record. Other pods call services by name (e.g., `payment-service`) and Kubernetes resolves it.

**Level 2:** Two patterns: client-side (Eureka/Ribbon — client picks instance, more complex but more control) vs server-side (Kubernetes Services — automatic, simpler, less control). Health checking ensures stale/dead instances are removed from the registry before clients try to call them.

**Level 3:** Kubernetes endpoint resolution: DNS → ClusterIP → iptables DNAT → Pod IP. For each Service, kube-proxy maintains iptables rules: packets to ClusterIP are DNAT'd to one of the ready pod IPs. EndpointSlice controller watches pod readiness and updates endpoint lists. Pods not in Ready state are removed from endpoint lists (and thus from DNS rotation). For headless services (clusterIP: None), DNS returns pod IPs directly (no ClusterIP proxy) — used for stateful sets where clients need to address specific pods (Kafka brokers, Cassandra nodes).

**Level 4:** xDS protocol (used by Envoy, Istio, and Google Traffic Director): Envoy proxies receive endpoint updates via streaming gRPC. When a pod crashes, Kubernetes updates EndpointSlice → Istiod watches this via API server → Istiod pushes xDS update to all Envoy sidecars in ~1-2 seconds. Comparison: iptables updates are also fast (< 1s via kube-proxy), but iptables doesn't do health-checking at the connection level. Envoy does: if an endpoint returns 5xx errors, outlier detection ejects it from the pool immediately (before the DNS TTL expires). This is why service mesh provides more sophisticated health tracking than pure DNS/iptables service discovery.

---

### ⚙️ How It Works (Mechanism)

```bash
# Kubernetes Service Discovery in practice

# Create internal service (East-West, ClusterIP)
kubectl apply -f - << 'EOF'
apiVersion: v1
kind: Service
metadata:
  name: payment-service
  namespace: production
spec:
  selector:
    app: payment
  ports:
  - port: 8080
    targetPort: 8080
  # No type field = ClusterIP (default) — internal only
EOF

# Verify DNS record created
kubectl run debug --image=busybox --rm -it -- \
  nslookup payment-service.production.svc.cluster.local
# Returns: ClusterIP (e.g., 10.96.45.100)

# View endpoints (actual pod IPs)
kubectl get endpoints payment-service -n production
# NAME              ENDPOINTS                          AGE
# payment-service   192.168.1.5:8080,192.168.1.6:8080  10m

# Headless service: returns pod IPs directly (stateful workloads)
kubectl apply -f - << 'EOF'
apiVersion: v1
kind: Service
metadata:
  name: kafka-headless
spec:
  clusterIP: None  # headless
  selector:
    app: kafka
  ports:
  - port: 9092
EOF
# DNS: kafka-0.kafka-headless.namespace.svc.cluster.local → pod IP

# View iptables rules set by kube-proxy
iptables-save | grep payment-service
# KUBE-SVC-xxx: probabilistic DNAT rules for each pod endpoint
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
Kubernetes Service Discovery — full flow when pod scales up:

1. Deployment scaled: kubectl scale deployment payment --replicas=3
2. Kubernetes Scheduler places 3 pods on nodes
3. Pods start, pass readiness probe (/health returns 200)
4. Endpoint Controller: adds pod IPs to EndpointSlice
   payment-service endpoints: [192.168.1.5, 192.168.1.6, 192.168.1.7]
5. kube-proxy (on each node) watches EndpointSlice via API server
6. kube-proxy updates iptables:
   ClusterIP 10.96.45.100:8080 → DNAT to one of [.5, .6, .7] randomly
7. kube-dns automatically serves A record:
   payment-service.production.svc.cluster.local → 10.96.45.100

Client calls payment-service:
DNS query → ClusterIP → iptables DNAT → pod IP → actual container

Pod crashes:
Readiness fails → removed from EndpointSlice → iptables updated
Client gets no more traffic to crashed pod (< 5s propagation)
```

---

### 💻 Code Example

```python
# Spring Cloud Eureka equivalent in Python using Consul
import consul
import random
import httpx

class ServiceDiscoveryClient:
    """Client-side service discovery using Consul."""

    def __init__(self, consul_host: str = "consul.service.consul"):
        self.consul = consul.Consul(host=consul_host)
        self._cache: dict = {}

    def get_healthy_instances(self, service_name: str) -> list[dict]:
        """Query Consul for healthy service instances."""
        index, services = self.consul.health.service(
            service_name,
            passing=True  # Only return health-checked instances
        )
        return [
            {
                "host": svc["Service"]["Address"] or svc["Node"]["Address"],
                "port": svc["Service"]["Port"],
            }
            for svc in services
        ]

    def call_service(self, service_name: str, path: str) -> dict:
        """Discover service and call it with client-side load balancing."""
        instances = self.get_healthy_instances(service_name)

        if not instances:
            raise RuntimeError(f"No healthy instances of {service_name}")

        # Client-side LB: random selection (could be round-robin, weighted)
        instance = random.choice(instances)
        url = f"http://{instance['host']}:{instance['port']}{path}"

        resp = httpx.get(url, timeout=5.0)
        resp.raise_for_status()
        return resp.json()

# In Kubernetes: no discovery code needed
# Just use the service DNS name directly:
import httpx
resp = httpx.get("http://payment-service.production.svc.cluster.local:8080/pay")
# Kubernetes DNS + kube-proxy handles discovery transparently
```

---

### ⚖️ Comparison Table

| Mechanism                   | Discovery Type        | Health Checking                      | Sophistication    | Best For                         |
| --------------------------- | --------------------- | ------------------------------------ | ----------------- | -------------------------------- |
| Kubernetes DNS + kube-proxy | Server-side           | Via readiness probes                 | Low (round-robin) | Standard K8s workloads           |
| Istio + xDS                 | Server-side (sidecar) | Active + passive (outlier detection) | High              | K8s + service mesh               |
| Consul                      | Both patterns         | Active HTTP/TCP checks               | Medium            | Multi-platform, VMs + K8s        |
| Eureka (Spring Cloud)       | Client-side           | Heartbeat + client-side LB           | Medium            | Java microservices               |
| Headless Service            | Client-side (DNS)     | Via readiness probes                 | Low               | Stateful sets (Kafka, Cassandra) |

---

### ⚠️ Common Misconceptions

| Misconception                                                | Reality                                                                                                                                                                                                              |
| ------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Kubernetes Service = load balancer                           | Kubernetes Service is a stable virtual IP + port mapping. Load balancing is done by kube-proxy (iptables/eBPF) — round-robin, not connection-aware. For L7 load balancing: use Ingress or service mesh               |
| DNS caching breaks Kubernetes discovery                      | Kubernetes DNS TTL is typically 5-30s. kube-proxy updates iptables synchronously when EndpointSlice changes. Pod IP removal propagates in seconds. DNS caching is a concern for external DNS, less so for in-cluster |
| Service mesh is required for service discovery in Kubernetes | Kubernetes has built-in service discovery (DNS + kube-proxy). Service mesh adds advanced features (mTLS, traffic policies, observability) ON TOP of basic discovery                                                  |

---

### 🚨 Failure Modes & Diagnosis

**Stale Endpoints: Traffic to Terminated Pods**

```bash
# Symptom: intermittent connection refused errors after pod restarts

# Check endpoint health
kubectl get endpoints payment-service -n production
# If shows IPs of pods that no longer exist: stale endpoints

# Check pod readiness
kubectl get pods -n production -l app=payment -o wide
# Cross-reference: are all endpoint IPs from running pods?

# Check readiness probe configuration
kubectl describe deployment payment -n production | grep -A 10 Readiness

# If pods don't have readiness probes: they're added to endpoints
# immediately at start, before they're ready to serve traffic
# Fix: add readiness probe
kubectl patch deployment payment -n production --type=json -p='[{
  "op": "add",
  "path": "/spec/template/spec/containers/0/readinessProbe",
  "value": {
    "httpGet": {"path": "/health", "port": 8080},
    "initialDelaySeconds": 5,
    "periodSeconds": 10
  }
}]'

# Check for slow DNS propagation (if using external Consul)
dig payment-service.service.consul @consul-server:8600
# Verify returns only healthy instances
```

---

### 🔗 Related Keywords

**Prerequisites:** `DNS`, `Load Balancer L4/L7`, `Microservices`

**Related:** `East-West vs North-South Traffic`, `Network Policies`, `Overlay Networks`, `mTLS`, `DNS`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ CLIENT-SIDE  │ Client queries registry, picks instance   │
│              │ Eureka, Consul (direct); more LB control  │
├──────────────┼───────────────────────────────────────────┤
│ SERVER-SIDE  │ Client calls VIP; infra does discovery    │
│              │ K8s Service (ClusterIP); simpler           │
├──────────────┼───────────────────────────────────────────┤
│ K8S BUILT-IN │ DNS: svc.namespace.svc.cluster.local      │
│              │ kube-proxy: ClusterIP → pod DNAT          │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Dynamic phone book for microservices —   │
│              │ no hardcoded IPs in cloud-native systems" │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Design service discovery for a hybrid multi-cloud environment: services running in AWS EKS, GCP GKE, and on-premise VMs all need to discover and call each other. (a) Explain why Kubernetes-native DNS (svc.cluster.local) doesn't work across clusters (cluster-local DNS, not globally routable). (b) Design a Consul federation: Consul agents in each environment, WAN gossip pool connecting them, DNS-based discovery with cross-datacenter fallback. (c) Describe how Istio multi-cluster discovery works: Istio east-west gateway for cross-cluster traffic, ServiceEntry resources to register external services, and how remote endpoints are discovered via Istio's multi-cluster API. (d) Address the latency implications: a service in AWS us-east-1 discovering and calling a service in GCP us-central1 adds 40-60ms cross-region latency — how do you design topology-aware service discovery that prefers local instances while falling back to remote instances only when local capacity is exhausted?
