---
layout: default
title: "Envoy Proxy"
parent: "Microservices"
nav_order: 645
permalink: /microservices/envoy-proxy/
number: "645"
category: Microservices
difficulty: ★★★
depends_on: "Service Mesh (Microservices), Istio"
used_by: "Sidecar Pattern (Microservices), Ambassador Pattern"
tags: #advanced, #microservices, #networking, #distributed, #performance
---

# 645 — Envoy Proxy

`#advanced` `#microservices` `#networking` `#distributed` `#performance`

⚡ TL;DR — **Envoy** is a high-performance **L7 proxy and communications bus** written in C++. It is the data plane of Istio and most modern service meshes. As a sidecar, it intercepts all pod traffic, handles: mTLS, load balancing, retries, circuit breaking, observability (traces/metrics/logs), and protocol translation — configured via the **xDS API**.

| #645            | Category: Microservices                             | Difficulty: ★★★ |
| :-------------- | :-------------------------------------------------- | :-------------- |
| **Depends on:** | Service Mesh (Microservices), Istio                 |                 |
| **Used by:**    | Sidecar Pattern (Microservices), Ambassador Pattern |                 |

---

### 📘 Textbook Definition

**Envoy Proxy** is a high-performance, open-source L7 (application layer) proxy originally developed by Lyft and donated to the CNCF. Envoy is designed for cloud-native, service-mesh, and edge environments. Its architecture is built around: a **non-blocking I/O event-driven threading model** (similar to nginx, based on libevent) that handles thousands of concurrent connections with minimal resources; the **xDS (Discovery Service) API** — a gRPC-based control plane API through which Envoy dynamically receives routing and policy configuration without restarts; and a **filter chain architecture** — pluggable HTTP, network, and listener filters that implement capabilities (JWT auth, rate limiting, fault injection, header manipulation). Envoy is the proxy of choice for service meshes (Istio, Consul Connect) and API Gateways (Contour, Ambassador, Emissary, AWS App Mesh). Its key differentiator from traditional proxies (HAProxy, Nginx) is first-class gRPC/HTTP2 support, dynamic configuration via xDS, and rich observability (structured access logs, OpenTelemetry traces, Prometheus-compatible metrics).

---

### 🟢 Simple Definition (Easy)

Envoy is the actual proxy program that runs as a sidecar in every pod when you use Istio or another service mesh. Think of it as a highly intelligent traffic controller embedded in every service. It handles encryption, retry logic, load balancing, and records metrics — while your application code stays unaware of its existence.

---

### 🔵 Simple Definition (Elaborated)

When Istio says "all traffic between services is mTLS encrypted and retried on 5xx," it is Envoy that actually does it. Istio's control plane (`istiod`) sends configuration to every Envoy proxy via the xDS gRPC API. Envoy intercepts your service's outbound HTTP call, wraps it in TLS, records the call in Prometheus metrics, adds a Zipkin trace span, retries if the first attempt returns 500, and circuit-breaks if too many attempts fail — all without your Java code knowing any of this happened. Envoy is written in C++ for high performance — it adds only ~1ms overhead per request even in a busy service mesh.

---

### 🔩 First Principles Explanation

**Envoy's internal architecture — Listener → Filter Chain → Cluster:**

```
ENVOY CONCEPTS:
  Listener: network socket that Envoy listens on (e.g., 0.0.0.0:15001)
  Filter Chain: ordered list of network/HTTP filters applied to traffic
  Cluster: group of upstream endpoints (e.g., all instances of PaymentService)
  Endpoint: individual backend instance (IP:port)
  Route: rules for matching requests to clusters

INBOUND TRAFFIC FLOW (request arriving at this pod):
  External → Envoy port 15006 (inbound capture)
    → HCM (HttpConnectionManager) filter
    → JWT AuthN filter (verify caller's mTLS certificate)
    → RBAC filter (check AuthorizationPolicy)
    → Application port 8080
    → Application processes request

OUTBOUND TRAFFIC FLOW (request leaving this pod):
  Application → Envoy port 15001 (outbound capture)
    → HCM filter
    → TLS origination (connect to upstream with mTLS)
    → Circuit breaker check (is cluster healthy?)
    → Load balancer (pick specific endpoint)
    → Retry filter (retry on 5xx)
    → Upstream service (actual target)

DYNAMIC CONFIG (no restart needed):
  istiod → xDS gRPC stream → Envoy
  LDS (Listener Discovery Service): listener config pushed
  CDS (Cluster Discovery Service): cluster/upstream config pushed
  RDS (Route Discovery Service): routing rules pushed
  EDS (Endpoint Discovery Service): individual endpoint IPs pushed
  → Change a VirtualService YAML → istiod translates → pushes to all Envoys
  → All proxies update config in seconds, zero-downtime
```

**Envoy filter architecture — extensibility:**

```
HTTP FILTER CHAIN (applied to every HTTP request):

  1. fault           → inject delays/errors for testing
  2. cors            → CORS headers
  3. jwt_authn       → JWT token validation
  4. ext_authz       → external authorisation service call
  5. ratelimit       → rate limit check against ratelimit service
  6. router          → final routing to upstream cluster (always last)

NETWORK FILTER CHAIN (applied before HTTP parsing):
  1. tcp_proxy       → TCP pass-through
  2. http_connection_manager (HCM) → parses HTTP, runs HTTP filters
  3. thrift_proxy    → Thrift protocol support
  4. mongo_proxy     → MongoDB protocol awareness (for observability)
  5. redis_proxy     → Redis protocol awareness

CUSTOM FILTERS (WASM extensions):
  Envoy supports WebAssembly filters (compiled from C++, Rust, Go)
  → Deploy custom logic without forking Envoy binary
  → Example: custom authentication, request transformation, telemetry
```

**Envoy observability — what it automatically emits:**

```
PROMETHEUS METRICS (subset):
  envoy_cluster_upstream_rq_total{cluster_name="payment-service"} 12345
  envoy_cluster_upstream_rq_5xx{cluster_name="payment-service"} 23
  envoy_cluster_upstream_rq_time_bucket{le="100"} 11000   ← p95 latency
  envoy_cluster_upstream_cx_active{cluster_name="payment-service"} 5

ZIPKIN/JAEGER TRACES:
  Envoy automatically creates trace spans for every request:
  Span: {
    service: "order-service" → "payment-service",
    duration: 127ms,
    status: 200,
    trace_id: "abc123",
    parent_span_id: "def456"
  }
  → Distributed traces assembled without application code changes
  → REQUIREMENT: application must propagate trace headers (B3/W3C) between calls

ACCESS LOGS (structured):
  {
    "method": "POST", "path": "/api/payments",
    "response_code": 200, "duration": "127ms",
    "upstream_host": "10.244.0.5:8080",
    "upstream_cluster": "outbound|8080||payment-service.default.svc.cluster.local",
    "bytes_received": 256, "bytes_sent": 1024
  }
```

---

### ❓ Why Does This Exist (Why Before What)

Traditional proxies (Nginx, HAProxy) were designed for static configuration (config files, reloads). Microservices need dynamic configuration: services scale up/down every second, routing rules change during deployments, and certificates rotate every 24 hours. Envoy was built from the ground up for dynamic configuration (xDS API) and cloud-native protocols (HTTP/2, gRPC, gRPC-Web, WebSocket). Its C++ implementation handles the performance demands of being in the network path of every service call.

---

### 🧠 Mental Model / Analogy

> Envoy is like a fully programmable smart router at every seat in a stadium (each pod). The stadium control room (istiod/xDS control plane) remotely configures every router simultaneously — routing rules, security policies, traffic weights. Each router independently handles its local traffic, records what it sees, and applies the rules it received. The control room never touches the actual traffic — it just pushes configuration. The routers handle everything in real time.

"Stadium control room" = istiod (control plane)
"Smart router at every seat" = Envoy sidecar
"Remote configuration push" = xDS API (LDS/CDS/RDS/EDS)
"Handling local traffic" = Envoy processing actual network packets
"Recording what it sees" = Envoy emitting metrics and traces

---

### ⚙️ How It Works (Mechanism)

**Envoy admin interface — inspecting live config and stats:**

```bash
# Envoy exposes admin endpoint on port 15000 (Istio) or 9901 (standalone):

# View all active listeners (ports Envoy is listening on):
kubectl exec -it order-service-pod -c istio-proxy -- \
  curl localhost:15000/listeners

# View upstream cluster config and health:
kubectl exec -it order-service-pod -c istio-proxy -- \
  curl localhost:15000/clusters

# View Envoy stats (Prometheus-compatible):
kubectl exec -it order-service-pod -c istio-proxy -- \
  curl localhost:15000/stats/prometheus | grep payment_service

# Inspect Envoy config dump (full xDS state):
kubectl exec -it order-service-pod -c istio-proxy -- \
  curl localhost:15000/config_dump > envoy_config.json
# Useful for debugging: "why is my VirtualService not being applied?"

# istioctl proxy-status: check all proxies are synced with istiod:
istioctl proxy-status
# NAME                          CLUSTER    CDS    LDS    EDS    RDS    ISTIOD
# order-service-pod.default     Kubernetes SYNCED SYNCED SYNCED SYNCED istiod-xxx
```

---

### 🔄 How It Connects (Mini-Map)

```
Service Mesh (Microservices)
(infrastructure layer for east-west traffic)
        │
        ▼
Envoy Proxy  ◄──── (you are here)
(the actual data plane proxy — sidecar in every pod)
        │
        ├── Istio → configures Envoy via xDS API (istiod)
        ├── Sidecar Pattern → the deployment pattern that places Envoy in the pod
        ├── Ambassador Pattern → Envoy as an API Gateway/ingress
        └── Observability → Envoy emits the raw telemetry data
```

---

### 💻 Code Example

**Application requirement: trace header propagation:**

```java
// Envoy creates trace spans but applications must PROPAGATE trace headers
// between service calls — otherwise Envoy creates disconnected spans

// Spring Boot with Spring Cloud Sleuth (or Micrometer Tracing):
// Automatically propagates B3 trace headers (X-B3-TraceId, X-B3-SpanId, etc.)

// BUT: if you use manual HTTP clients, you must propagate headers:
@Service
class OrderService {

    @Autowired RestTemplate restTemplate;

    public void processOrder(HttpServletRequest incomingRequest, Long productId) {
        HttpHeaders headers = new HttpHeaders();
        // Propagate trace context (Envoy will link spans if these headers are present):
        String traceId = incomingRequest.getHeader("x-b3-traceid");
        String spanId = incomingRequest.getHeader("x-b3-spanid");
        String sampled = incomingRequest.getHeader("x-b3-sampled");

        if (traceId != null) headers.add("x-b3-traceid", traceId);
        if (spanId != null) headers.add("x-b3-parentspanid", spanId);  // current span becomes parent
        if (sampled != null) headers.add("x-b3-sampled", sampled);

        HttpEntity<Void> entity = new HttpEntity<>(headers);
        restTemplate.exchange(
            "http://inventory-service/api/inventory/" + productId,
            HttpMethod.GET, entity, InventoryResponse.class);
    }
}
// Without header propagation: Envoy creates 2 disconnected traces
// With header propagation: Envoy links them into one distributed trace
```

---

### ⚠️ Common Misconceptions

| Misconception                                   | Reality                                                                                                                                                                                                                                                                                                                     |
| ----------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Envoy replaces Nginx                            | Envoy and Nginx serve overlapping but distinct use cases. Nginx is a battle-hardened reverse proxy/web server excellent for static content and simple HTTP routing. Envoy is designed for dynamic service mesh and L7 traffic management. Many organisations use both: Nginx for static web serving, Envoy for service mesh |
| Envoy adds significant latency to every request | Envoy's C++ event-driven architecture adds approximately 0.5–2ms per proxy hop. For a service with 100ms response time, this is 1–2% overhead — typically acceptable. Envoy is significantly faster than JVM-based proxies like Spring Cloud Gateway for raw proxying                                                       |
| Envoy configuration is only managed by Istio    | Envoy can be used standalone with a static YAML configuration (envoy.yaml) or integrated with other control planes (Consul, xDS-compatible custom control planes). Istio is the most common control plane, but Envoy is independent                                                                                         |
| Envoy handles application-level errors          | Envoy handles HTTP protocol errors (5xx, connection failures, timeouts). Application business errors (validation failures, not-found responses) are 4xx and typically not retried by Envoy — configure retryOn carefully                                                                                                    |

---

### 🔥 Pitfalls in Production

**Trace headers not propagated — broken distributed traces**

```
SYMPTOM: Jaeger shows single-hop traces for every service.
  Order 12345 trace: shows only OrderService span.
  Missing: InventoryService span, PaymentService span.
  → Cannot trace end-to-end request flow
  → Cannot identify which service is causing latency

ROOT CAUSE:
  OrderService calls InventoryService using new RestTemplate (no header propagation).
  Envoy creates a new trace ID for the InventoryService call → disconnected span.

FIX (Spring Boot + Micrometer Tracing with Brave):
  # spring boot 3.x:
  implementation("io.micrometer:micrometer-tracing-bridge-brave")
  implementation("io.zipkin.reporter2:zipkin-reporter-brave")

  # Micrometer auto-configures B3 header propagation for:
  # - Spring RestTemplate (inject RestTemplateBuilder bean, @Autowired it)
  # - WebClient (inject WebClient.Builder bean, @Autowired it)
  # - Kafka (micrometer-tracing-kafka)
  # - Feign clients (auto-configured with micrometer-tracing)

  MANUAL CHECK: verify all HTTP clients in your service are Spring-managed beans:
  @Bean RestTemplate restTemplate(RestTemplateBuilder builder) {
    return builder.build();  // ← builder injects trace headers
  }
  // NOT: new RestTemplate()  ← no trace header injection
```

---

### 🔗 Related Keywords

- `Service Mesh (Microservices)` — Envoy is the data plane of a service mesh
- `Istio` — the control plane that manages Envoy via xDS
- `Sidecar Pattern (Microservices)` — the deployment pattern for Envoy as a sidecar
- `Ambassador Pattern` — using Envoy as an intelligent gateway/ingress

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ L7 proxy — data plane of service meshes  │
│ LANGUAGE     │ C++ (high performance, ~1ms overhead)     │
├──────────────┼───────────────────────────────────────────┤
│ CONFIG API   │ xDS: LDS/CDS/RDS/EDS — dynamic, no restart│
│ FILTERS      │ JWT, RBAC, fault, rate limit, router (L7) │
├──────────────┼───────────────────────────────────────────┤
│ EMITS        │ Prometheus metrics, Zipkin traces,        │
│              │ structured access logs — automatically    │
├──────────────┼───────────────────────────────────────────┤
│ TRACE NOTE   │ App must propagate B3/W3C headers for     │
│              │ distributed tracing to work end-to-end    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Envoy implements circuit breaking via `outlierDetection` in `DestinationRule` (Istio). This works at the load balancing level — unhealthy pods are temporarily removed from the load balancing pool. Compare this to Resilience4j's circuit breaker which operates at the service call level (CLOSED/OPEN/HALF-OPEN state machine). Describe a failure scenario where Envoy's outlierDetection is NOT sufficient and Resilience4j is still needed: for example, when all pods of `PaymentService` are healthy (no outlier) but the service is degraded due to database query performance — returning 200 OK but taking 10 seconds. How would you detect and handle this in (a) Envoy configuration and (b) Resilience4j configuration?

**Q2.** Envoy's filter chain is applied in order. If you have filters: [jwt_authn, ext_authz, ratelimit, router], describe what happens if `ext_authz` is unavailable (the external authorisation service is down). Should Envoy fail open (allow requests through) or fail closed (reject all requests)? What is the security implication of each choice? How does `ext_authz`'s `failure_mode_allow` configuration option affect this, and in what situations would you use `failure_mode_allow: true` vs `failure_mode_allow: false`?
