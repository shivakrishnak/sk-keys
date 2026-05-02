---
layout: default
title: "Ambassador Pattern"
parent: "Design Patterns"
nav_order: 811
permalink: /design-patterns/ambassador-pattern/
number: "811"
category: Design Patterns
difficulty: ★★★
depends_on: "Sidecar Pattern, Microservices, Kubernetes, Circuit Breaker Pattern"
used_by: "Service mesh, outbound traffic management, legacy service modernization"
tags: #advanced, #design-patterns, #microservices, #proxy, #outbound, #service-mesh
---

# 811 — Ambassador Pattern

`#advanced` `#design-patterns` `#microservices` `#proxy` `#outbound` `#service-mesh`

⚡ TL;DR — **Ambassador Pattern** is a Sidecar variant that acts as an outbound proxy for the application — handling retries, circuit breaking, authentication, and protocol translation for ALL outbound calls, so the application only calls `localhost`.

| #811 | Category: Design Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Sidecar Pattern, Microservices, Kubernetes, Circuit Breaker Pattern | |
| **Used by:** | Service mesh, outbound traffic management, legacy service modernization | |

---

### 📘 Textbook Definition

**Ambassador Pattern** (Brendan Burns, "Designing Distributed Systems", 2018): a Sidecar Pattern specialization where the sidecar proxies all outbound traffic from the application — acting as an "ambassador" (representative) to the outside world. The application calls a local endpoint (`localhost:port`) for every external dependency; the Ambassador container handles routing, retry, circuit breaking, authentication, TLS, and protocol adaptation. Unlike the general Sidecar (which handles both inbound and outbound), the Ambassador is explicitly focused on outbound (egress) concerns. Enables legacy applications to gain modern resilience capabilities (retries, circuit breaking) without code modification.

---

### 🟢 Simple Definition (Easy)

A company's ambassador in a foreign country: speaks the local language, knows local customs, negotiates on your behalf, reports back in your language. You (the application) don't need to know how to negotiate in Japanese — the ambassador handles it and returns you a result. Ambassador Pattern: the application calls `localhost:9090/inventory` (simple HTTP); the Ambassador proxies the call to `inventory-service.cluster.svc:8080`, adds auth headers, retries on failure, and implements circuit breaking — all transparent to the application.

---

### 🔵 Simple Definition (Elaborated)

A legacy application written in 2012 has no retry logic, no circuit breaking, no distributed tracing. Rewriting it: 6-month project. Ambassador Pattern: deploy Envoy or HAProxy as an Ambassador sidecar. Configure: retry for 5xx, circuit break on sustained failures, add Authorization headers, inject trace headers. The legacy app calls `localhost:8080/api` — the Ambassador intercepts, applies all the resilience policies, and forwards to the real service. Legacy app gains modern resilience in one afternoon of Kubernetes config, without touching a single line of its code.

---

### 🔩 First Principles Explanation

**Ambassador vs. Sidecar distinction and implementation:**

```
AMBASSADOR vs. SIDECAR:

  Sidecar:     handles BOTH inbound AND outbound traffic
               Examples: Envoy (Istio), Linkerd proxy — full mesh proxy
  
  Ambassador:  focused on OUTBOUND (egress) traffic only
               Examples: HAProxy ambassador, Envoy as egress-only proxy
               The application still receives inbound requests directly.
  
  USE AMBASSADOR (not full sidecar) when:
  ✓ You need outbound resilience for a legacy application
  ✓ Inbound is handled elsewhere (API Gateway, Nginx)
  ✓ You want a lighter-weight proxy (not full service mesh)
  ✓ Multi-language services with varying outbound patterns

AMBASSADOR PATTERN MECHANICS:

  Without Ambassador:
  App → (direct HTTP + custom retry + custom circuit breaker) → External Service
  
  With Ambassador:
  App → localhost:9000 (Ambassador) → (retry + CB + auth + TLS) → External Service
  
  ENVOY AS AMBASSADOR (Kubernetes pod):
  
  spec:
    containers:
    - name: legacy-app
      image: legacy-app:3.2.1
      env:
      - name: INVENTORY_URL
        value: http://localhost:9000  # Calls Ambassador, not external service
    
    - name: ambassador-proxy
      image: envoyproxy/envoy:v1.28.0
      ports:
      - containerPort: 9000         # App calls this
      volumeMounts:
      - name: envoy-config
        mountPath: /etc/envoy
  
  Envoy config (envoy.yaml — ambassador for inventory service):
  
  static_resources:
    listeners:
    - name: listener_0
      address:
        socket_address: { address: 0.0.0.0, port_value: 9000 }
      filter_chains:
      - filters:
        - name: envoy.filters.network.http_connection_manager
          typed_config:
            route_config:
              virtual_hosts:
              - name: local_service
                domains: ["*"]
                routes:
                - match: { prefix: "/" }
                  route:
                    cluster: inventory_service
                    timeout: 5s
                    retry_policy:
                      retry_on: "5xx,connect-failure,reset"
                      num_retries: 3
                      per_try_timeout: 2s
  
    clusters:
    - name: inventory_service
      connect_timeout: 0.5s
      type: LOGICAL_DNS
      load_assignment:
        cluster_name: inventory_service
        endpoints:
        - lb_endpoints:
          - endpoint:
              address:
                socket_address:
                  address: inventory-service.production.svc.cluster.local
                  port_value: 8080
      circuit_breakers:
        thresholds:
        - priority: DEFAULT
          max_connections: 100
          max_pending_requests: 1000
          max_requests: 1000

AMBASSADOR FOR PROTOCOL TRANSLATION:

  Legacy app: only speaks REST HTTP/1.1
  New internal service: gRPC (HTTP/2)
  
  Ambassador: receives REST from app → translates to gRPC → sends to service
  → receives gRPC response → translates to REST → returns to app
  
  Application: zero gRPC code. Ambassador handles protocol translation.
  
  Envoy supports: REST-to-gRPC transcoding via grpc-json transcoder filter.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Ambassador:
- Each application must implement: retry logic, circuit breaking, auth header injection, TLS, tracing
- Legacy apps cannot gain these capabilities without code changes
- Multi-language fleet: each language implements differently (varying quality)

WITH Ambassador:
→ Resilience and cross-cutting concerns implemented once in the Ambassador proxy. All applications — legacy or modern, any language — call `localhost` and gain uniform behavior.

---

### 🧠 Mental Model / Analogy

> A diplomatic ambassador: represents your country in a foreign nation. You (the application/government) send a message to the ambassador ("please request more grain"). The ambassador translates it into the local diplomatic language, navigates cultural protocols, retries if the foreign official is unavailable, escalates if communication breaks down, and returns a translated response to you. You never had to speak Japanese, navigate foreign protocol, or handle diplomatic failures directly.

"Your government sends a message to the ambassador" = application calls `localhost:9000/inventory`
"Ambassador translates to local diplomatic language" = protocol translation (REST → gRPC)
"Retries if foreign official unavailable" = retry policy on 5xx or connection failure
"Escalates if communication breaks down" = circuit breaking on sustained failures
"Returns translated response to you" = returns REST response to the application
"You never needed to speak Japanese" = application has zero retry/circuit-breaker/auth code

---

### ⚙️ How It Works (Mechanism)

```
AMBASSADOR TRAFFIC FLOW:

  ┌─────────────────────────────────────────────────────────┐
  │  Pod                                                    │
  │                                                         │
  │  ┌──────────────────┐      ┌─────────────────────────┐  │
  │  │  Application     │      │  Ambassador Proxy       │  │
  │  │  (legacy or new) │      │  (Envoy / HAProxy)      │  │
  │  │                  │ HTTP │                         │  │
  │  │  GET localhost:  │─────►│  - TLS termination      │  │
  │  │  9000/inventory  │      │  - Auth header inject   │  │
  │  │                  │      │  - Retry (3x on 5xx)    │  │
  │  │  ← Response      │◄─────│  - Circuit breaker      │  │
  │  └──────────────────┘      │  - Tracing headers      │  │
  │                            └────────────┬────────────┘  │
  └─────────────────────────────────────────┼───────────────┘
                                            │ OUTBOUND ONLY
                                            ▼
                               inventory-service:8080
                               (actual downstream service)
```

---

### 🔄 How It Connects (Mini-Map)

```
Outbound resilience and protocol adaptation without application code changes
        │
        ▼
Ambassador Pattern ◄──── (you are here)
(outbound-focused sidecar; app calls localhost; ambassador handles the rest)
        │
        ├── Sidecar Pattern: parent pattern — Ambassador is a Sidecar specialization
        ├── Circuit Breaker: implemented in the Ambassador proxy (Envoy)
        ├── Service Mesh: Istio/Linkerd combines Ambassador + inbound proxy
        └── API Gateway: Gateway handles INBOUND; Ambassador handles OUTBOUND
```

---

### 💻 Code Example

```java
// Application code using Ambassador Pattern:
// The application is completely unaware of the Ambassador proxy.
// It just calls localhost:9000 for ALL external services.

@Service
@RequiredArgsConstructor
public class InventoryClient {
    
    private final RestTemplate restTemplate;
    
    // Application configuration:
    // inventory.url = http://localhost:9000   ← points to Ambassador
    @Value("${inventory.url}")
    private String inventoryUrl;
    
    public InventoryStatus checkStock(Long productId) {
        // Application calls localhost — no retry, no circuit breaker code here.
        // ALL resilience handled by Ambassador proxy.
        return restTemplate.getForObject(
            inventoryUrl + "/inventory/{id}",
            InventoryStatus.class,
            productId
        );
    }
}

// What the Ambassador proxy does on this call (transparent to the app):
// 1. Receives GET http://localhost:9000/inventory/123
// 2. Adds Authorization: Bearer <service-account-token>
// 3. Adds X-Request-ID: <trace-id>
// 4. Forwards to https://inventory-service.production.svc.cluster.local:8443/inventory/123
// 5. If 500: retry up to 3 times with 500ms backoff
// 6. If circuit open: return 503 immediately (no upstream call)
// 7. Returns response to application on localhost:9000

// Application code: 3 lines. Zero resilience code. Zero TLS code. Zero auth code.
// Ambassador: handles all of it declaratively via Envoy config YAML.
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Ambassador Pattern and API Gateway are the same | API Gateway handles INBOUND traffic (client → gateway → service). Ambassador handles OUTBOUND traffic (service → ambassador → downstream). They are complementary: a Gateway at the edge handles external traffic; an Ambassador in the pod handles inter-service outbound calls. Both can implement routing, retries, and auth — but at different network positions. |
| Service Mesh (Istio) is the only way to implement Ambassador | Service mesh is one implementation. You can implement Ambassador with: HAProxy sidecar, Nginx sidecar, custom Envoy config — without a full service mesh. Service mesh adds: control plane, mTLS, traffic management UI, global policy. Ambassador without a service mesh: simpler, fewer features, less operational overhead. Choose based on complexity needs. |
| Ambassador Pattern creates a single point of failure | The Ambassador is co-located with the application in the same pod. If the Ambassador fails, the pod is restarted (Kubernetes liveness probe). The Ambassador doesn't add a network hop outside the pod — it's on localhost. The failure domain of the Ambassador = the failure domain of the pod itself. It doesn't create a network-level SPOF. |

---

### 🔥 Pitfalls in Production

**Ambassador adding latency without proper resource allocation:**

```yaml
# ANTI-PATTERN — Ambassador proxy with no resource limits in high-throughput pod:

containers:
- name: high-throughput-service
  image: payment-processor:1.0
  # 10,000 requests/second, each processed in < 5ms
  resources:
    requests: { cpu: "2000m", memory: "2Gi" }
    limits:   { cpu: "4000m", memory: "4Gi" }

- name: ambassador
  image: envoyproxy/envoy:v1.28.0
  # NO resource limits set!
  
# Under load: Envoy CPU saturates (10,000 req/s × proxy overhead)
# Envoy starts queuing requests
# P99 latency: 5ms → 250ms (proxy queue buildup)
# Payment processor: healthy. Envoy: bottleneck.

# FIX 1: Profile Envoy CPU usage at peak throughput BEFORE production.
# FIX 2: Set appropriate Envoy resource limits based on measured usage.
# FIX 3: For ultra-high-throughput (>10K rps): evaluate if per-pod proxy overhead
#         justifies the benefits. At extreme scale: consider service mesh at
#         node level (DaemonSet) instead of per-pod sidecar.

- name: ambassador
  image: envoyproxy/envoy:v1.28.0
  resources:
    requests: { cpu: "500m", memory: "128Mi" }
    limits:   { cpu: "1000m", memory: "256Mi" }
# FIX 4: tune Envoy worker threads: `--concurrency 4` (matching CPU limit)
```

---

### 🔗 Related Keywords

- `Sidecar Pattern` — parent pattern: Ambassador is a Sidecar specialization for outbound traffic
- `Circuit Breaker Pattern` — Ambassador implements circuit breaking in the proxy layer
- `Retry Pattern` — Ambassador implements retry logic declaratively
- `API Gateway` — complementary: Gateway handles inbound; Ambassador handles outbound
- `Service Mesh (Istio)` — full implementation combining inbound + outbound proxies

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Outbound-focused sidecar proxy. App calls │
│              │ localhost. Ambassador handles: retry,     │
│              │ circuit breaking, TLS, auth, tracing.    │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Legacy app needs resilience without code  │
│              │ changes; multi-language fleet needs       │
│              │ uniform outbound behavior                  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Simple low-volume service; overhead       │
│              │ exceeds benefits; full service mesh       │
│              │ already providing the same capability     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Diplomatic ambassador: you send a message│
│              │  in English; they negotiate in Japanese,  │
│              │  handle protocol, and report back."       │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Sidecar → Service Mesh → API Gateway →    │
│              │ Envoy Config → Circuit Breaker             │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** The Ambassador Pattern is often described as a way to "modernize legacy applications without code changes." But there's a nuance: if the application doesn't propagate trace context headers (e.g., `traceparent`, `X-B3-TraceId`), the Ambassador can inject the initial trace headers but cannot propagate a parent trace from an incoming request. For distributed tracing to work end-to-end, the application must READ the incoming trace headers and PASS THEM through to the Ambassador on outbound calls. How does this "propagation gap" limit the Ambassador Pattern's tracing capability for legacy applications, and what options exist to address it?

**Q2.** Envoy's circuit breaking configuration uses two concepts: connection pool limits (maxConnections, maxPendingRequests, maxRequests) and outlier detection (consecutive5xxErrors, interval, baseEjectionTime). These are different mechanisms: connection pool limits control concurrency (similar to Bulkhead); outlier detection identifies and ejects unhealthy endpoints from the load balancer pool. How do connection pool limits and outlier detection work together in Envoy to provide both Bulkhead isolation AND Circuit Breaker behavior through a single proxy configuration?
