---
id: MSV-042
title: Envoy Proxy
category: Microservices
tier: tier-5-distributed-architecture
folder: MSV-microservices
difficulty: ★★★
depends_on: MSV-040, MSV-041
used_by: MSV-040, MSV-041
related: MSV-040, MSV-041, MSV-039, MSV-075
tags:
  - microservices
  - infrastructure
  - deep-dive
  - proxy
status: complete
version: 4
layout: default
parent: "Microservices"
grand_parent: "Technical Mastery"
nav_order: 42
permalink: /technical-mastery/microservices/envoy-proxy/
---

⚡ TL;DR - Envoy is a high-performance, open-source
edge and service proxy designed for cloud-native
applications. Originally built at Lyft. It is the
data plane for Istio (and many other service meshes).
Key capabilities: dynamic configuration via xDS API
(no restart needed to update routes/clusters),
HTTP/2 and gRPC first-class support, L7 load balancing,
circuit breaking, retries, distributed tracing
(Zipkin/Jaeger headers), health checking, TLS termination,
and detailed statistics. Used as: sidecar proxy in
service meshes, edge proxy/API gateway, and per-service
outbound proxy.

| #042 | Category: Microservices | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Service Mesh, Istio | |
| **Used by:** | Service Mesh, Istio | |
| **Related:** | Service Mesh, Istio, Client-Side vs Server-Side Discovery, mTLS in Microservices | |

---

### 🔥 The Problem This Solves

Microservices need a network proxy that: (1) can be
configured at runtime without restarts (dynamic config
for Kubernetes scale events), (2) understands HTTP/2
and gRPC (not just TCP), (3) provides detailed per-request
observability, (4) has first-class distributed tracing
support, and (5) can handle retries, circuit breaking,
and load balancing at the proxy level. NGINX is
configured via files (requires reload). HAProxy:
Limits HTTP/2 support. Envoy was designed from scratch
for dynamic, cloud-native microservices workloads.

---

### 📘 Textbook Definition

**Envoy Proxy** is an open-source, high-performance
L4/L7 proxy written in C++ and designed for cloud-native
environments. Key design principles: (1) Out-of-process
architecture: runs alongside applications, language-agnostic.
(2) Dynamic configuration: xDS API allows real-time
configuration updates without restarts. (3) Observability-first:
built-in statistics for every operation (request count,
latency histogram, error counts). (4) HTTP/2 and gRPC
native: first-class support for modern protocols.
Used as: sidecar in Istio/Linkerd/AWS App Mesh, API
Gateway (Envoy Gateway, Contour), standalone proxy,
and edge proxy.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Envoy = L7-aware, dynamically configurable proxy with
built-in observability; the foundational component
for modern service meshes.

**One analogy:**
> Envoy is like a highly intelligent post office worker
> (proxy) that: routes letters by their content (L7
> routing by HTTP headers), knows the addresses of all
> other offices dynamically (xDS discovery), tracks
> every letter sent/received (statistics), stamps every
> letter with a tracking number (distributed tracing),
> retries delivery on failure (retries), and refuses
> to route to an office that's overwhelmed (circuit
> breaker). All without the letter writer (application)
> knowing any of this happens.

**One insight:**
Envoy's xDS API is its most important innovation:
Listeners, Routes, Clusters, and Endpoints can all
be updated via gRPC streaming API without any proxy
restart. This makes Envoy suitable as a Kubernetes
sidecar: when pods scale up/down, istiod pushes EDS
(Endpoint Discovery Service) updates to all Envoy
instances in sub-second time. Static-config proxies
(NGINX) require reloads on every route change.

---

### 🔩 First Principles Explanation

**ENVOY CORE CONCEPTS:**

```
LISTENERS (LDS - Listener Discovery Service):
  What port Envoy listens on and with what filters
  Example: listen on :15001 for outbound traffic
           with HTTP connection manager filter

ROUTES (RDS - Route Discovery Service):
  For a given HTTP request, which cluster to send to
  Example: /api/orders -> orders-service cluster
           /api/payments -> payment-service cluster
           header x-canary=true -> payment-v2 cluster

CLUSTERS (CDS - Cluster Discovery Service):
  A group of endpoints (service instances)
  Load balancing policy for the cluster
  Health checking configuration
  Circuit breaker settings (outlier detection)

ENDPOINTS (EDS - Endpoint Discovery Service):
  The actual IP:port instances in a cluster
  Updated dynamically as pods scale up/down
  Kubernetes: EDS receives pod IPs from Kubernetes
    endpoints

xDS API:
  All of the above (LDS/RDS/CDS/EDS) are distributed
  via gRPC streaming from the control plane (istiod)
  Envoy subscribes at startup
  Control plane pushes incremental updates (delta xDS)
  No restart required for any configuration change
```

**ENVOY FILTER CHAIN:**

```
INCOMING REQUEST:
  Network -> Listener -> Filter Chain
  
  Filters (applied in order):
  1. TLS Inspector: detect TLS
  2. HTTP Connection Manager:
     a. Router: match route -> select cluster
     b. Retry filter: retry on failure
     c. Circuit breaker: check circuit state
  3. Transport Socket: mTLS handshake
  
  OUTGOING:
  Same chain, reverse direction
  
  HTTP Filters (pluggable):
  - JWT Authentication (validate JWT tokens)
  - Rate limiting (local or global rate limits)
  - WASM filters (custom logic via WebAssembly)
  - External Authorization (call external auth service)
```

---

### 🧪 Thought Experiment

**ENVOY vs NGINX FOR KUBERNETES SIDECAR:**

```
SCENARIO: Kubernetes pod scales from 3 to 10 instances

NGINX SIDECAR (hypothetical):
  - New pod IPs: 10.0.0.58, 10.0.0.59, 10.0.0.60
  - NGINX config: upstream block with static IPs
  - Config reload required: NGINX sends SIGHUP
  - Reload: drops in-flight connections (brief)
  - Frequency: every scale event = every reload
  - At 1000 services with frequent scaling:
    1000s of NGINX reloads per minute

ENVOY SIDECAR (actual):
  - New pod IPs: 10.0.0.58, 10.0.0.59, 10.0.0.60
  - istiod: pushes EDS update via xDS gRPC stream
  - Envoy: hot-patches endpoint table in memory
  - No restart. No connection drops.
  - Propagation time: < 1 second
  - Scale to 1000 services: same behavior
```

---

### 🧠 Mental Model / Analogy

> Envoy's architecture is like a real-time navigation
> system vs a printed map. NGINX uses a printed map
> (config file): to update routes, reprint and reload.
> Envoy uses Google Maps live traffic (xDS API): the
> map updates continuously via streaming. New roads
> (new pods), road closures (pod failures), traffic
> redirections (routing changes) all update in real
> time without reprinting. The navigation system
> (control plane: istiod) broadcasts updates to all
> cars (Envoy sidecars) simultaneously.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Envoy is a proxy program that sits between microservices.
It routes requests, handles retries if a service is
down, and reports everything that passes through it.
It's the network layer that Istio runs on.

**Level 2 - How to use it (junior developer):**
As a developer: you typically don't configure Envoy
directly when using Istio. You configure Istio CRDs
(VirtualService, DestinationRule); Istio translates
these to Envoy config and pushes via xDS. You interact
with Envoy for debugging: `kubectl exec -it pod -c
istio-proxy -- curl localhost:15000/stats` for metrics,
or `istioctl proxy-config routes pod` to see routes.

**Level 3 - How it works (mid-level engineer):**
Envoy starts and connects to the xDS server (istiod)
via gRPC. It subscribes to LDS (listeners), CDS
(clusters), RDS (routes), EDS (endpoints). istiod
sends the current configuration. Envoy applies it.
On updates: istiod sends delta (only changed resources).
Envoy applies in-memory, no restart. For a request:
Envoy matches the listener (port 15001 for outbound),
applies the filter chain (HTTP connection manager),
matches the route (VirtualService rules), selects a
cluster (DestinationRule subsets), selects an endpoint
(EDS load balancing), opens/reuses connection, forwards
request, applies circuit breaker, emits metrics and
trace spans.

**Level 4 - Why it was designed this way (senior/staff):**
Envoy's xDS API was designed by the Envoy team and
became a CNCF standard. Multiple service mesh control
planes (Istio, Consul, Gloo) use the same xDS API.
This standardization means Envoy can be the data plane
for any compliant control plane. The Envoy Gateway
project extends this to edge proxy use. The extensibility
via WASM (WebAssembly) filters allows custom logic
(custom auth, request transformation) to be deployed
to Envoy sidecars as WASM modules without recompiling
Envoy. This makes Envoy a platform, not just a proxy.

**Level 5 - Mastery (distinguished engineer):**
Envoy's thread model: Envoy is event-driven with a
main thread + N worker threads. Each worker thread runs
an independent event loop (libevent). Connections are
assigned to worker threads (consistent hashing). All
configuration updates are applied via "TLS" (Thread
Local Storage) updates: main thread updates the config
and notifies workers via a post-to-thread mechanism.
This allows configuration updates while worker threads
continue processing requests without locking. High
throughput: Envoy handles millions of requests per
second with consistent low latency due to this
architecture. For sidecar use: the cost is 2-5ms
added latency per hop (TLS handshake + proxy overhead).
At 10 hops in a complex call chain: 20-50ms total.
Use tracing to identify the most expensive hops for
optimization.

---

### ⚙️ How It Works (Mechanism)

**ENVOY ADMIN API:**

```bash
# Access Envoy admin (from within pod)
kubectl exec -it payment-pod-xxx -c istio-proxy -- sh

# View all clusters (upstream services Envoy knows)
curl localhost:15000/clusters
# Output: cluster name, endpoints, health status
# Use to verify payment-service endpoints are registered

# View routing table
curl localhost:15000/config_dump | \
  python3 -m json.tool | \
  grep -A 10 '"name": "8080"'

# View live statistics
curl localhost:15000/stats | \
  grep -E 'upstream_rq_total|upstream_rq_5xx|cx_active'

# Key metrics:
# envoy_cluster_upstream_rq_total: total requests
# envoy_cluster_upstream_rq_5xx: 5xx responses
# envoy_cluster_upstream_cx_active: active connections
# envoy_cluster_outlier_detection_ejections_active:
#   circuit broken instances

# Check xDS synchronization
curl localhost:15000/ready
# LIVE = ready; INITIALIZING = still syncing from istiod
```

**ENVOY STATISTICS FOR CIRCUIT BREAKER:**

```bash
# Check if circuit breaker is active
curl localhost:15000/stats | grep \
  'payment-service.*outlier_detection'

# envoy_cluster_outlier_detection_ejections_active: 1
# -> 1 instance is currently ejected (circuit broken)

# envoy_cluster_upstream_rq_pending_overflow: 42
# -> 42 requests rejected due to connection pool overflow
# (circuit breaker at connection pool level)

# Reset ejected instance manually (for testing)
curl -X POST localhost:15000/reset_counters
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
ENVOY REQUEST PROCESSING:

1. App calls http://payment-service/payments
2. iptables: redirect to Envoy port 15001 (outbound)
3. Envoy: match listener on port 15001
4. HTTP Connection Manager filter: parse HTTP
5. Router filter: match route "payment-service/payments"
   -> cluster: outbound|8080||payment-service.default.svc
6. Load balance: select endpoint (round-robin or
  least-conn)
   -> endpoint: 10.0.1.5:8080
7. Circuit breaker check: is connection pool full? No.
8. TLS: initiate mTLS handshake with 10.0.1.5:8080
   Envoy A presents SPIFFE cert (order-service identity)
   Envoy B verifies cert, presents payment-service cert
9. Forward request to 10.0.1.5:8080 (Envoy B inbound)
10. Envoy B: check AuthorizationPolicy (order-service
    allowed to call /payments? Yes)
11. Deliver to app via port 15006 redirect
12. Response: reverse path
13. Envoy A emits:
    - Metric: upstream_rq_total++, duration histogram
    - Trace span: traceparent header from app
      + Envoy start/end timestamps
    - Access log: request details
```

---

### 💻 Code Example

**Example 1 - Envoy admin for circuit breaker investigation**

```bash
# BAD: Guessing why service is returning 503s
# restart the pod (unnecessary, doesn't fix circuit breaker)
kubectl delete pod payment-pod-xxx
```

```bash
# GOOD: Investigate via Envoy admin API

# Step 1: Check if circuit breaker is active
kubectl exec -it order-pod-xxx -c istio-proxy -- \
  curl -s localhost:15000/stats | \
  grep 'payment-service.*outlier_detection.ejections_active'
# payment-service.outlier_detection.ejections_active: 2
# -> 2 of 3 instances are ejected (circuit tripped)

# Step 2: Check connection pool overflow
kubectl exec -it order-pod-xxx -c istio-proxy -- \
  curl -s localhost:15000/stats | \
  grep 'payment-service.*pending_overflow'
# payment-service.upstream_rq_pending_overflow: 156
# -> 156 requests dropped; pool is full

# Step 3: Check endpoint health
kubectl exec -it order-pod-xxx -c istio-proxy -- \
  curl -s localhost:15000/clusters | \
  grep payment-service | grep -E 'health_flags|cx_active'
# /failed_active_hc -> health check failing
# cx_active: 0 -> no active connections

# Conclusion: 2 of 3 instances failed health check
# Outlier detection ejected them
# Fix: check what's causing 5xx on payment-service pods
kubectl logs -l app=payment-service --tail=50 | \
  grep -E 'ERROR|Exception'
```

---

### ⚖️ Comparison Table

| Proxy | Config Model | HTTP/2 | Dynamic Config | Observability | Use Case |
|---|---|---|---|---|---|
| **Envoy** | xDS API | Native | Yes (no restart) | Rich | Service mesh, edge proxy |
| **NGINX** | File-based | Partial | Reload required | Basic | Web server, reverse proxy |
| **HAProxy** | File-based | Yes | Reload required | Good | L4/L7 LB, edge |
| **Traefik** | Dynamic | Native | Yes | Good | Kubernetes ingress |
| **Linkerd Proxy** | xDS | Native | Yes | Good | Linkerd mesh (lower overhead) |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Envoy is only for Istio | Envoy is used by: Istio, AWS App Mesh, Consul Connect, Gloo Edge (API Gateway), Contour (K8s Ingress), Envoy Gateway (standalone). It's a general-purpose proxy. Its xDS API is a CNCF standard. |
| Envoy configuration is simple YAML like NGINX | Envoy's static YAML configuration is verbose and complex (listeners -> filter chains -> HTTP connection manager -> route config). This is why Istio exists: it generates Envoy config from simpler VirtualService/DestinationRule abstractions. Direct Envoy config is for advanced edge proxy use cases. |
| The Envoy sidecar is transparent to the application | Almost: iptables redirect means the app doesn't change. But trace header propagation (B3/W3C traceparent) requires the app to forward headers from incoming to outgoing requests for end-to-end tracing. This is the only place where Envoy's presence requires application awareness. |

---

### 🚨 Failure Modes & Diagnosis

**Envoy NOT sending traffic to healthy pods**

**Symptom:**
Kubernetes shows 5 pods RUNNING for payment-service.
`kubectl get endpoints payment-service` shows 5 pod
IPs. But `istioctl proxy-config endpoints` shows only
3 endpoints for payment-service. 2 pods are not
receiving any traffic. Error rate is high because
only 3 pods handle full load.

**Root Cause:**
Envoy's active health checking (configured in
DestinationRule) or passive outlier detection marked
2 pods as unhealthy and ejected them from the load
balancing pool. The pods are RUNNING in Kubernetes
but Envoy has decided they are unhealthy based on
recent failures.

**Diagnostic:**
```bash
# Check Envoy endpoints for payment-service
istioctl proxy-config endpoints order-pod-xxx | \
  grep payment-service
# HEALTHY 10.0.1.5:8080
# HEALTHY 10.0.1.6:8080
# HEALTHY 10.0.1.7:8080
# /failed_active_hc 10.0.1.8:8080  <- unhealthy
# /failed_active_hc 10.0.1.9:8080  <- unhealthy

# Check what's wrong with the unhealthy pods
kubectl exec -it payment-pod-8 -- curl localhost:8080/health
# Should return 200 if truly healthy

# Check Envoy outlier detection stats
kubectl exec -it order-pod-xxx -c istio-proxy -- \
  curl localhost:15000/stats | grep \
  'payment.*outlier_detection'
```

**Fix:**
1. If pods are truly unhealthy: fix the application issue.
2. If pods are healthy but Envoy thinks they're not:
   check DestinationRule health check endpoint config
   (incorrect health check path).
3. Temporary: force-reload endpoints by restarting
   one unhealthy pod (Kubernetes replacement pod
   will re-register in EDS).
4. Tune outlier detection: increase
   `baseEjectionTime` if flapping, or reduce
   `consecutive5xxErrors` threshold.

---

### 🔗 Related Keywords

**Foundation:**
- `Service Mesh` - Envoy is the data plane for most
  service mesh implementations
- `Istio` - uses Envoy as its sidecar proxy; istiod
  configures Envoy via xDS

**Related:**
- `Client-Side vs Server-Side Discovery` - Envoy
  implements transparent client-side discovery as sidecar
- `mTLS in Microservices` - Envoy handles TLS
  termination and certificate management for mTLS

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ xDS API      │ LDS/RDS/CDS/EDS via gRPC stream         │
│              │ Dynamic config, zero restart            │
├──────────────┼──────────────────────────────────────────┤
│ ADMIN API    │ localhost:15000/stats /clusters         │
│              │ /config_dump for debugging              │
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "L7 proxy with dynamic xDS config;      │
│              │  data plane for Istio service mesh"     │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Envoy is the data plane for Istio (and most service
   meshes). istiod configures it via xDS API.
2. xDS = dynamic config without restart: LDS (listeners),
   RDS (routes), CDS (clusters), EDS (endpoints).
3. Debug via Envoy admin API (port 15000) for:
   `/stats` (metrics), `/clusters` (endpoints),
   `istioctl proxy-config` (route/cluster/endpoint config).

**Interview one-liner:**
"Envoy is a high-performance L7 proxy used as Istio's
data plane sidecar. Key innovation: xDS API (Listener/
Route/Cluster/Endpoint Discovery Service via gRPC
streaming) allows real-time configuration without
restarts. Handles: mTLS, retries, circuit breaking
(outlier detection), load balancing, distributed tracing
header injection. Debug via admin API port 15000:
/stats, /clusters, /config_dump; or `istioctl
proxy-config` for higher-level view."

---

### 💡 The Surprising Truth

Envoy's most underused feature in production:
the admin API's `/config_dump` endpoint. When Istio
behavior doesn't match expectations (routing rule
not taking effect, circuit breaker not triggering),
most engineers restart pods, re-apply CRDs, and wait.
The faster path: `kubectl exec -it pod -c istio-proxy
-- curl localhost:15000/config_dump | python3 -m
json.tool` shows the exact Envoy configuration that
Istiod pushed. If your VirtualService rule isn't in
the config dump: istiod hasn't pushed it yet, or
there's a validation error. If it IS in the config
dump but routing doesn't match: route priority issue
(more specific routes must come before catch-all routes
in VirtualService). The config dump is the source of
truth for what Envoy is actually doing.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **CONCEPTS** Explain the four xDS APIs (LDS/RDS/
   CDS/EDS) and what each configures in Envoy.
2. **DEBUG** Use `istioctl proxy-config routes/endpoints/
   clusters` and `localhost:15000/stats` to diagnose
   why traffic isn't routing as expected.
3. **METRICS** Identify the key Envoy stats for:
   circuit breaker state, connection pool overflow,
   upstream error rate, and request latency p99.
4. **ARCHITECTURE** Explain why Envoy can update
   configuration without restarts (xDS streaming +
   in-memory update) and why this matters for
   Kubernetes scale events.
5. **TRACING** Explain the one application requirement
   for end-to-end distributed tracing with Envoy
   (trace header propagation) and why Envoy can't
   do this automatically.

---

### 🧠 Think About This Before We Continue

**Q1.** You are building an API Gateway using Envoy
directly (not Istio). You need to: validate JWT tokens,
route to 5 backend services based on path, add rate
limiting per user, and inject correlation IDs. List
the Envoy filter chain components needed. What is
the order of filters and why?

**Q2.** An Envoy sidecar is consuming 400MB of memory
in a pod. The service only handles 100 req/sec. Normal
Expected memory is 50-100MB. What could cause this?
(Hint: consider xDS configuration size). How do you
diagnose and fix it?

**Q3.** Your distributed traces show gaps: spans from
service A appear, then spans from service C appear,
but there is no span for service B in between. Service
B is in the mesh and Envoy is logging the requests.
Why do the trace spans not appear in Jaeger? What
is the application-level fix?