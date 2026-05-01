---
layout: default
title: "Ambassador Pattern"
parent: "Microservices"
nav_order: 679
permalink: /microservices/ambassador-pattern/
number: "679"
category: Microservices
difficulty: ★★★
depends_on: "Sidecar Pattern, API Gateway"
used_by: "Cross-Cutting Concerns"
tags: #advanced, #microservices, #distributed, #architecture, #pattern
---

# 679 — Ambassador Pattern

`#advanced` `#microservices` `#distributed` `#architecture` `#pattern`

⚡ TL;DR — The **Ambassador Pattern** is a sidecar proxy that handles outbound communication from a service to external resources, adding retry, circuit breaking, and routing on behalf of the application.

| #679 | Category: Microservices | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Sidecar Pattern, API Gateway | |
| **Used by:** | Cross-Cutting Concerns | |

---

### 📘 Textbook Definition

The **Ambassador Pattern** is a structural pattern where a sidecar container (the ambassador) acts as an out-of-process proxy for outbound network calls made by the primary service. The ambassador intercepts all outbound requests from the application to external services, applying infrastructure-level concerns: connection pooling, retry with backoff, circuit breaking, protocol translation, and telemetry. Unlike the generic sidecar (which handles both inbound and outbound), the ambassador pattern is specifically concerned with representing the service to the outside world — acting as its envoy to external resources. It decouples application code from the specifics of how to communicate with dependencies (discovery, TLS negotiation, load balancing) by wrapping those concerns in the ambassador proxy. The pattern is particularly valuable for legacy applications (brownfield) that cannot be modified but need modern networking capabilities added around them.

---

### 🟢 Simple Definition (Easy)

An ambassador is a sidecar that acts as your service's representative to the outside world. Your service makes a simple HTTP call to `localhost:8000`. The ambassador receives it and handles all the complexity: finding the real destination, retrying on failure, managing certificates, and adding monitoring. Your service code stays simple.

---

### 🔵 Simple Definition (Elaborated)

Order Service needs to call three external services: Payment Gateway (requires OAuth2), Inventory Service (requires retries + circuit breaker), and Notification Service (requires rate limiting). Without ambassador: Order Service's code implements OAuth2, retry logic, circuit breaking, and rate limiting for all three. With ambassador: Order Service calls `localhost:8001/payment`, `localhost:8002/inventory`, `localhost:8003/notify`. The ambassador handles OAuth2 token refresh, retries, circuit breaking, and rate limiting per upstream. Order Service code: plain HTTP to localhost. Ambassador: all the hard parts.

---

### 🔩 First Principles Explanation

**The problem: outbound networking complexity accumulates in application code:**

```
WITHOUT AMBASSADOR:
  Modern service requires when calling external dependencies:
    ✗ TLS/mTLS: load certs, verify against CA, rotate on expiry
    ✗ Authentication: OAuth2 token refresh, JWT signing, API key management
    ✗ Retry: exponential backoff, jitter, max attempts, idempotency check
    ✗ Circuit breaker: track failure rate, open/close circuit
    ✗ Load balancing: discover endpoints, distribute load, detect unhealthy
    ✗ Connection pool: limit open connections, reuse TCP connections
    ✗ Observability: emit metrics per upstream, trace outbound calls
  
  All implemented in application code:
    Java: Resilience4j + OkHttp + OpenTelemetry Java SDK + custom cert loading
    Python: tenacity + requests + certificate pinning
    
  PROBLEMS:
    - Different language teams → inconsistent implementations
    - Security bugs in custom TLS/auth code
    - Upgrade retry library: touch every service in every language
    - Legacy app (C++ binary, no source): cannot add these capabilities

WITH AMBASSADOR:
  Application: curl http://localhost:8000/payment-service/charge
  Ambassador (Envoy/nginx):
    - Discovers payment-service via DNS/service registry
    - Attaches Bearer token (reads from shared secret volume)
    - Retries up to 3 times with exponential backoff
    - Opens circuit if >50% requests fail in 10s
    - Emits metrics: latency_ms, error_rate per upstream
    - mTLS to payment-service's ambassador
  Application: gets response. Zero networking code.
```

**Envoy as ambassador — Lua filter for OAuth2 token injection:**

```yaml
# ambassador-config.yaml:
# Envoy ambassador: handles outbound calls from app to payment-service

static_resources:
  listeners:
  # App calls localhost:8001 → Ambassador → payment-service
  - name: payment_ambassador
    address: {socket_address: {address: 127.0.0.1, port_value: 8001}}
    filter_chains:
    - filters:
      - name: envoy.filters.network.http_connection_manager
        typed_config:
          "@type": type.googleapis.com/.../HttpConnectionManager
          route_config:
            virtual_hosts:
            - name: payment_upstream
              domains: ["*"]
              routes:
              - match: {prefix: "/"}
                route:
                  cluster: payment_service_cluster
                  retry_policy:
                    retry_on: "connect-failure,refused-stream,5xx"
                    num_retries: 3
                    per_try_timeout: 2s
                    retry_back_off:
                      base_interval: 100ms
                      max_interval: 2s
          http_filters:
          # Add Authorization header (reads from file updated by Vault Agent sidecar):
          - name: envoy.filters.http.lua
            typed_config:
              "@type": type.googleapis.com/.../LuaPerRoute
              inline_code: |
                function envoy_on_request(request_handle)
                  local token_file = io.open("/var/run/secrets/oauth-token", "r")
                  if token_file then
                    local token = token_file:read("*all")
                    token_file:close()
                    request_handle:headers():add("Authorization", "Bearer " .. token)
                  end
                end

  clusters:
  - name: payment_service_cluster
    connect_timeout: 1s
    type: STRICT_DNS
    load_assignment:
      cluster_name: payment_service_cluster
      endpoints:
      - lb_endpoints:
        - endpoint:
            address:
              socket_address:
                address: payment-service.production.svc.cluster.local
                port_value: 8080
    circuit_breakers:
      thresholds:
      - max_connections: 50
        max_pending_requests: 25
        max_requests: 100
```

**Ambassador for legacy application — adding retries to a legacy app with no source:**

```yaml
# Legacy C++ billing service — compiled binary, no retry logic.
# Cannot modify source code.
# Deploy ambassador sidecar alongside it:

apiVersion: apps/v1
kind: Deployment
spec:
  template:
    spec:
      containers:
      # PRIMARY: legacy billing service (cannot be modified)
      - name: billing-service
        image: legacy-billing:1.0.0  # 10-year-old binary
        # Makes plain HTTP calls to downstream services
        # Points to localhost:9001, localhost:9002 (its hardcoded config)

      # AMBASSADOR: adds retries/circuit breaker/mTLS to legacy app's outbound
      - name: billing-ambassador
        image: envoy:v1.28.0
        # Listens on localhost:9001, localhost:9002
        # Intercepts legacy app's outbound calls
        # Adds retry, circuit breaker, mTLS without touching legacy code
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Ambassador Pattern:
- Networking concerns (retries, TLS, auth) mixed into business logic
- Language heterogeneity → no shared implementation
- Legacy apps: cannot add modern networking capabilities without source code
- Upgrading retry behavior: requires deploying every service

WITH Ambassador Pattern:
→ Application code calls localhost — networking is the ambassador's job
→ Language-agnostic: works for any app that makes HTTP/gRPC calls
→ Legacy apps gain retries, mTLS, circuit breaking with zero code changes
→ Update retry policy: update ambassador config, no app deployment

---

### 🧠 Mental Model / Analogy

> A diplomat's ambassador. A country (service) wants to communicate with foreign nations (external services). Rather than learning each country's language, customs, and protocols directly, it sends an ambassador who speaks all languages, knows all diplomatic protocols, handles credentials, and reports back. The country just says "tell payment-land we want to pay" — the ambassador handles the rest.

"Country" = application service
"Foreign nations" = external dependencies (payment, inventory services)
"Ambassador" = outbound proxy sidecar
"Languages/protocols" = TLS, OAuth2, gRPC, retries, circuit breakers

---

### ⚙️ How It Works (Mechanism)

**Ambassador vs generic Sidecar — the key difference:**

```
GENERIC SIDECAR: handles BOTH inbound and outbound
  [external] → Envoy:15006 (inbound) → App:8080
  App:8080 → Envoy:15001 (outbound) → [external]
  Used by: service meshes (full traffic management)

AMBASSADOR: handles OUTBOUND only (represents service TO the world)
  App → Ambassador:localhost:8001 → [Payment Service]
  App → Ambassador:localhost:8002 → [Inventory Service]
  Inbound: no ambassador (directly to app, or separate ingress)
  Used by: brownfield apps needing outbound capabilities added

ADAPTER: handles INBOUND only (represents service FOR the world)
  [external: gRPC] → Adapter → [App: REST]
  Protocol translation: adapter translates external protocol to app's protocol
  Used by: adding API compatibility to existing services
```

---

### 🔄 How It Connects (Mini-Map)

```
Sidecar Pattern          API Gateway
(generic co-located      (handles inbound at boundary)
 container pattern)
        │                        │
        └──────────┬─────────────┘
                   ▼
        Ambassador Pattern  ◄──── (you are here)
        (outbound-focused sidecar proxy)
                   │
                   ▼
        Cross-Cutting Concerns
        (retries, TLS, auth, metrics
         handled outside app code)
```

---

### 💻 Code Example

**Testing ambassador locally with Docker Compose:**

```yaml
# docker-compose.yml: local dev with ambassador sidecar
services:
  order-service:
    image: order-service:latest
    environment:
      # App points to ambassador, not directly to services:
      PAYMENT_SERVICE_URL: http://localhost:8001
      INVENTORY_SERVICE_URL: http://localhost:8002
    network_mode: "service:ambassador"  # share ambassador's network

  ambassador:
    image: envoy:v1.28.0
    volumes:
    - ./envoy-ambassador.yaml:/etc/envoy/envoy.yaml
    ports:
    - "8001:8001"   # payment ambassador port
    - "8002:8002"   # inventory ambassador port
    - "9901:9901"   # admin UI: http://localhost:9901
    # Envoy admin: shows circuit breaker state, upstream health, metrics

  # Downstream services (real or mocked):
  payment-service:
    image: wiremock/wiremock:latest
  inventory-service:
    image: wiremock/wiremock:latest
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Ambassador Pattern and API Gateway are the same | API Gateway operates at the cluster/network boundary, handling inbound traffic from clients to services. Ambassador Pattern is service-level, handling outbound calls FROM a service to its dependencies. They are complementary: API Gateway handles north-south traffic, Ambassador handles east-west |
| Every service needs its own ambassador | The ambassador is typically configured per-service based on that service's specific outbound dependencies. A service that only calls one downstream with simple HTTP may not need an ambassador. Apply where the complexity of outbound networking justifies the extra container |
| Ambassador pattern requires Envoy specifically | Any capable proxy can be an ambassador: nginx, HAProxy, Traefik, or a custom Go binary. Envoy is most common due to its xDS API (dynamic reconfiguration) and Istio integration, but the pattern is proxy-implementation-agnostic |
| Ambassador adds latency for every outbound call | The ambassador runs on localhost (loopback), so the network hop is ~0.1ms. For retries (when upstream fails), the ambassador saves the round-trip latency of making the call from application code — it does the retry locally |

---

### 🔥 Pitfalls in Production

**Ambassador retry storms — retrying non-idempotent requests:**

```
PROBLEM:
  Ambassador configured: retry 3 times on 5xx.
  POST /payments (charge $100) → payment service returns 500.
  Ambassador: retries 3 times.
  Payment service was actually slow (not failed) — charged $100 three times.
  
FIX:
  Only retry idempotent operations (GET, PUT with idempotency key).
  For non-idempotent POST: retry ONLY on connection-failure (network level),
  NOT on 5xx (which may mean the request was processed but response lost).
  
  retry_policy:
    # WRONG: retry on all 5xx (may cause duplicate charges)
    retry_on: "5xx"
    
    # CORRECT: retry only on connection-level failures for POST
    retry_on: "connect-failure,refused-stream"
    # NOT "retriable-4xx" or "5xx" for non-idempotent requests
  
  ALSO: add idempotency key to POST requests:
    App generates UUID, passes as X-Idempotency-Key header.
    Ambassador passes header through on retries.
    Payment service: deduplicates using idempotency key.
    Retries: idempotent because payment service rejects duplicate key.
```

---

### 🔗 Related Keywords

- `Sidecar Pattern` — the parent pattern; Ambassador is a specialised sidecar for outbound
- `API Gateway (Microservices)` — handles inbound traffic; Ambassador handles outbound
- `Cross-Cutting Concerns` — retries, TLS, auth: the concerns Ambassador handles
- `Adapter Pattern (Microservices)` — the complementary inbound-focused sidecar
- `Envoy Proxy` — the most common ambassador implementation
- `Circuit Breaker (Microservices)` — applied by the ambassador to outbound calls

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Sidecar proxy for OUTBOUND calls only:    │
│              │ retries, TLS, auth outside app code       │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ App makes complex outbound calls; legacy  │
│              │ apps needing networking capabilities added│
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Simple internal calls with no resilience  │
│              │ requirements; cost of sidecar > benefit   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Your app's diplomat: handles all the     │
│              │  protocol, credentials, and failure."     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Sidecar → Service Mesh → Envoy Proxy      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your legacy Java application (compiled JAR, cannot be modified) makes outbound HTTP calls using hardcoded URLs from a properties file: `payment.url=http://payment-service:8080`. You need to add: mTLS, exponential retry with 3 attempts, and circuit breaking (open after 50% failures in 10s). Design the ambassador deployment: what Kubernetes annotations/labels are needed, how does the ambassador intercept calls made to `http://payment-service:8080` without changing the app's config, and how do you verify the circuit breaker is working in production?

**Q2.** Compare the Ambassador Pattern with implementing retry logic using Resilience4j directly in application code. For a Java microservice team that owns all their services (no legacy, no polyglot), design the criteria for choosing between: (a) Resilience4j annotations in code, (b) Envoy ambassador sidecar, (c) service mesh with global retry policies. What factors — team size, deployment frequency, observability requirements, and latency SLAs — drive the decision?
