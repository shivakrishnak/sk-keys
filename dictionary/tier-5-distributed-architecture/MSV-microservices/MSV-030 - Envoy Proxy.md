---
layout: default
title: "Envoy Proxy"
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 30
permalink: /microservices/envoy-proxy/
id: MSV-030
category: Microservices
difficulty: ★★★
depends_on: Service Mesh, Networking, HTTP & APIs
used_by: Istio, Service Mesh, API Gateway
related: Istio, nginx, HAProxy
tags:
  - microservices
  - networking
  - distributed
  - deep-dive
  - pattern
status: complete
---

# MSV-030 - Envoy Proxy

⚡ TL;DR - Envoy is a high-performance open-source proxy designed for cloud-native applications that handles service-to-service traffic with built-in observability, load balancing, and protocol support.

| #645 | Category: Microservices | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Service Mesh, Networking, HTTP & APIs | |
| **Used by:** | Istio, Service Mesh, API Gateway | |
| **Related:** | Istio, nginx, HAProxy | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Lyft ran a large microservices platform in 2015. Their polyglot services needed: connection pooling, circuit breaking, retries, rate limiting, and distributed tracing - all consistently across Java, Python, and Go services. Implementing each of these in language-specific libraries (Hystrix for Java, custom Python library, Go middleware) produced inconsistent behaviour. The Java services had circuit breaking; the Go services didn't. Tracing was available in 40% of services. When the platform had cascading failures, engineers couldn't diagnose which service was the bottleneck because observability data was incomplete.

**THE BREAKING POINT:**
A single network-level failure cascaded because only some services had circuit breaking. The inconsistency wasn't a bug - it was an architecture flaw. Solving it required the same solution in every language.

**THE INVENTION MOMENT:**
This is exactly why Lyft created Envoy in 2016 - a language-agnostic, high-performance proxy that handles all networking concerns at the process boundary, so every service gets circuit breaking, tracing, and load balancing regardless of its implementation language.


**EVOLUTION:**
Envoy Proxy was created at Lyft in 2015 and open-sourced in 2016 to address the failure modes of managing a microservices network without a unified proxy layer. Before Envoy, each service at Lyft had custom retry/timeout/circuit breaking logic in application code. The xDS (Discovery Service) API (formalised 2017) made Envoy dynamically configurable without restarts. Envoy became the universal data plane for Istio, Consul Connect, and AWS App Mesh - the single infrastructure component that all modern service meshes are built on.
---

### 📘 Textbook Definition

**Envoy** is an open-source, high-performance L4/L7 proxy and communication bus designed for cloud-native microservices architectures. Originally built by Lyft and donated to the CNCF in 2017, Envoy is written in C++ for performance-critical networking operations. Its core design philosophy is: network should be transparent to the application. Envoy is used both as a sidecar proxy (intercepting all traffic for a single service) and as an edge proxy (acting as an API Gateway or ingress controller). It is the data plane for Istio but is widely used independently.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Envoy is the smart proxy that sits next to your service and handles all the networking complexity so your service code doesn't have to.

**One analogy:**
> Envoy is the personal assistant of a busy executive (your service). The assistant intercepts all incoming calls (traffic), screens them (auth checks), keeps a log of all calls (access logs/metrics), puts callers on hold if the executive is overwhelmed (circuit breaking), and automatically tries again if a call drops (retry). The executive just focuses on their work.

**One insight:**
Envoy's design insight was to make the proxy API-driven - not config-file-driven. The xDS API (Discovery Service) enables Envoy's behaviour to be changed dynamically at runtime without restarts. This makes it possible for a control plane (Istio) to reconfigure thousands of Envoy instances simultaneously.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. All traffic passes through Envoy - no request reaches the application without going through the proxy.
2. Envoy is stateless for routing decisions - all state (route tables, cluster health, rate limit counters) comes from xDS or external systems.
3. Envoy observes every request and response - it emits metrics, logs, and traces for 100% of traffic without application instrumentation.

**DERIVED DESIGN:**

Envoy's internal architecture:

```
┌──────────────────────────────────────────────┐
│              Envoy Architecture              │
│                                              │
│  Downstream → [Listener] → [Filter Chain]   │
│                              │               │
│                         [Router Filter]      │
│                              │               │
│                         [Cluster Manager]    │
│                              │               │
│                         [Load Balancer]      │
│                              ↓               │
│                         Upstream Service     │
└──────────────────────────────────────────────┘
```

- **Listener**: what port/protocol Envoy accepts (e.g., TCP 15001)
- **Filter Chain**: ordered list of filters applied to each connection/request
- **HTTP Filters**: applied per-request (auth, rate limit, retry, circuit break)
- **Cluster**: upstream service definition (IPs, health checks, LB policy)
- **xDS Server**: dynamic configuration source (replaces static config files)

**THE TRADE-OFFS:**
**Gain:** Language-agnostic networking, automatic observability, dynamic reconfiguration via xDS, extensive protocol support (HTTP/1.1, HTTP/2, gRPC, WebSocket, TCP).
**Cost:** Memory overhead per sidecar (~50–100MB), ~1ms latency per proxy hop, C++ codebase requires expertise to debug deeply.

---

### 🧪 Thought Experiment

**SETUP:**
A Python service needs to call a Java service. The Python service has no circuit breaking or retry logic. The Java service is occasionally slow (3-second response times).

**WITHOUT ENVOY:**
Python calls Java directly. Java is slow → Python's HTTP library blocks for 3 seconds → Python thread pool exhausts → Python service starts failing → Cascade begins.

**WITH ENVOY:**
Python sends request to local Envoy (localhost:15001, sub-millisecond overhead). Envoy applies:
- Timeout: abort if Java takes > 500ms
- Retry: retry once on 503 with 50ms backoff
- Circuit Breaker: after 5 consecutive timeouts, stop calling Java for 30s

Python's code is unchanged. Python now has full circuit breaking and retries against the Java service - implemented at the proxy layer, not the application layer.

**THE INSIGHT:**
By intercepting traffic at the network layer, Envoy adds resilience capabilities to services that haven't implemented them, while keeping the application code clean and language-independent.

---

### 🧠 Mental Model / Analogy

> Envoy is like a Swiss Army knife postal service. Every letter (request) passes through the postal service (Envoy). The post office: stamps the letter with a tracking number (trace ID), tells the sender if delivery failed and tries again (retry), won't accept new letters if the recipient's mailbox is full (circuit breaking), and generates daily reports on all mail delivered (metrics). The letter writer (application developer) just writes the letter.

- "Postal service stamp" → trace ID injected into request headers
- "Retry attempted delivery" → configurable retry policy
- "Mailbox full → stop accepting letters" → circuit breaker (outlier detection)
- "Monthly delivery report" → Prometheus metrics, access logs

Where this analogy breaks down: a postal service adds significant latency (days). Envoy operates at sub-millisecond latency within a Kubernetes cluster's local network - the overhead is negligible relative to service processing time.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Envoy is a helper program that sits next to your service. All network traffic goes through it. Envoy handles retries, security, and tracking - your service code doesn't need to.

**Level 2 - How to use it (junior developer):**
In Istio environments: Envoy is automatically injected as a sidecar - you don't configure it directly. In standalone use: write a YAML config defining listeners and clusters. Use `envoy -c config.yaml` to start it. Docker Compose: put Envoy as a sidecar service next to your app, configure it to forward to `localhost:8080`.

**Level 3 - How it works (mid-level engineer):**
Envoy's filter chain architecture allows composable per-request processing. For HTTP: the filter chain runs: `ext_authz` (auth) → `lua` (custom logic) → `ratelimit` (rate limiting) → `router` (forward to upstream). Each filter can modify the request, reject it, or pass it on. The `router` filter selects a cluster (upstream), picks an endpoint using the configured LB policy (round-robin / least-connections / consistent hash), and makes the upstream call. Metrics are emitted as Prometheus or StatsD counters/gauges per listener, cluster, and virtual host.

**Level 4 - Why it was designed this way (senior/staff):**
Envoy's xDS API design was the key engineering innovation. Traditional proxies (nginx, HAProxy) reload config by reading a file and restarting workers - causing seconds of downtime. Envoy accepts dynamic configuration via gRPC streaming APIs, applying changes to individual clusters or routes without any traffic disruption. This made Envoy the unique solution to large-scale dynamic microservices routing. The filter chain composability (vs monolithic nginx modules) enables arbitrary extension without forking the codebase. The WASM filter extension mechanism (Istio WebAssembly plugins) allows custom logic to be deployed into Envoy without recompiling C++.

---

### ⚙️ How It Works (Mechanism)

**Envoy static configuration (standalone):**

```yaml
static_resources:
  listeners:
    - name: listener_0
      address:
        socket_address:
          address: 0.0.0.0
          port_value: 10000    # Envoy listens here
      filter_chains:
        - filters:
            - name: envoy.filters.network.http_connection_manager
              typed_config:
                "@type": type.googleapis.com/envoy.extensions.filters
                  .network.http_connection_manager.v3.HttpConnectionManager
                stat_prefix: ingress_http
                http_filters:
                  - name: envoy.filters.http.router
                    typed_config:
                      "@type": type.googleapis.com/envoy.extensions
                        .filters.http.router.v3.Router
                route_config:
                  name: local_route
                  virtual_hosts:
                    - name: backend
                      domains: ["*"]
                      routes:
                        - match:
                            prefix: "/"
                          route:
                            cluster: payments_cluster
                            timeout: 2s
                            retry_policy:
                              retry_on: "5xx,reset"
                              num_retries: 3

  clusters:
    - name: payments_cluster
      connect_timeout: 1s
      lb_policy: ROUND_ROBIN
      load_assignment:
        cluster_name: payments_cluster
        endpoints:
          - lb_endpoints:
              - endpoint:
                  address:
                    socket_address:
                      address: payments-service
                      port_value: 8080
      circuit_breakers:
        thresholds:
          - max_connections: 100
            max_pending_requests: 50
            max_retries: 3
```

**Envoy admin API (built-in):**

```bash
# Check cluster health and stats
curl http://localhost:9901/clusters

# Check active connections
curl http://localhost:9901/stats | grep connection

# View current routing config
curl http://localhost:9901/config_dump | python3 -m json.tool

# Trigger a config reload (hot restart)
curl -X POST http://localhost:9901/quitquitquit
```

**Circuit breaker stats:**

```bash
# Check if circuit breaker is open
curl http://envoy:9901/stats | grep \
  "cluster.payments_cluster.circuit_breakers"
# upstream_cx_overflow = connections rejected due to CB
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
App process calls payments (localhost:15001) → Envoy Sidecar intercepts ← YOU ARE HERE → Envoy applies filters (auth, rate limit) → Envoy selects endpoint from cluster (LB) → TLS handshake with destination Envoy → Request forwarded → Response path: destination Envoy → source Envoy → App

**FAILURE PATH:**
Upstream returns 503 → Envoy retries (per retry_policy) → After max retries: circuit breaker tracks consecutive failures → Circuit opens (outlier detection ejects endpoint) → Envoy returns 503 to app with `x-envoy-overloaded: true` header → App handles gracefully → After ejection timeout: Envoy re-probes endpoint

**WHAT CHANGES AT SCALE:**
At 100,000 req/s per pod, Envoy's C++ non-blocking I/O architecture handles this with a few worker threads - no thread-per-connection overhead. Under extreme scale, the stats collection (every counter/timer emits metrics) becomes CPU-intensive. Solution: reduce stats flushing frequency and use metric sampling. At 10,000 pod sidecars, Istiod's xDS push latency becomes the config propagation bottleneck.

---

### 💻 Code Example

**Example 1 - Envoy as standalone API Gateway (Docker Compose):**

```yaml
# docker-compose.yml
services:
  envoy:
    image: envoyproxy/envoy:v1.29-latest
    volumes:
      - ./envoy.yaml:/etc/envoy/envoy.yaml
    ports:
      - "8080:8080"   # public port
      - "9901:9901"   # admin interface
    command: /usr/local/bin/envoy -c /etc/envoy/envoy.yaml

  order-service:
    image: myapp/order-service:latest
    # Only accessible through Envoy - not exposed to host

  payment-service:
    image: myapp/payment-service:latest
```

**Example 2 - Debug Envoy sidecar in Kubernetes:**

```bash
# Check Envoy's view of upstream clusters
kubectl exec -it order-service-xxx \
  -c istio-proxy -- \
  curl -s http://localhost:15000/clusters | \
  grep "payments_service"

# Check circuit breaker stats
kubectl exec -it order-service-xxx \
  -c istio-proxy -- \
  curl -s http://localhost:15000/stats | \
  grep "circuit_breakers"

# Check if any endpoints are ejected (circuit open)
kubectl exec -it order-service-xxx \
  -c istio-proxy -- \
  curl -s http://localhost:15000/clusters | \
  grep "ejected_via_outlier"

# Full proxy config dump
istioctl proxy-config all order-service-xxx.production
```

**Example 3 - Custom Envoy WASM filter (advanced):**

```rust
// Rust WASM filter for custom header manipulation
// Compiled to .wasm and loaded into Envoy without recompile
use proxy_wasm::traits::*;
use proxy_wasm::types::*;

struct HeaderFilter;

impl HttpContext for HeaderFilter {
    fn on_http_request_headers(&mut self, _: usize, _: bool)
        -> Action {
        // Add custom header to every request
        self.set_http_request_header(
            "x-custom-header", Some("injected-by-envoy")
        );
        Action::Continue
    }
}
```

---

### ⚖️ Comparison Table

| Proxy | Performance | Dynamic Config | Observability | Best For |
|---|---|---|---|---|
| **Envoy** | Very High | xDS (dynamic) | Excellent | Service mesh, cloud-native |
| nginx | High | File reload | Good | Web serving, static config |
| HAProxy | Very High | Runtime API | Good | TCP/HTTP load balancing |
| Traefik | High | Dynamic | Good | Docker/K8s native, auto-config |
| Linkerd-proxy | Very High | Destination API | Excellent | Lighter service mesh alternative |

How to choose: use Envoy when dynamic reconfiguration, gRPC support, or service mesh integration is required. Use nginx for simple reverse proxy with heavy HTTP caching use cases.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Envoy is only for microservices | Envoy is used as an edge proxy (API Gateway replacement), ingress controller, and egress proxy - not just as a sidecar |
| Envoy configuration is simple | Envoy's YAML configuration is notoriously verbose and complex. Istio exists partly because direct Envoy config management at scale is impractical |
| Envoy adds significant latency | P50 latency overhead is 0.2–1ms. At 95th percentile it can reach 3ms - negligible compared to typical service processing times |
| You must use Istio to use Envoy | Envoy is used independently at Lyft, Dropbox, Stripe, and others without Istio. Istio is just one control plane option |
| Envoy is only an HTTP proxy | Envoy supports TCP, UDP, gRPC, WebSocket, Redis, MongoDB, and Kafka protocols natively via filters |

---

### 🚨 Failure Modes & Diagnosis

**1. Envoy Sidecar Memory Leak**

**Symptom:** Pod memory usage grows over hours/days. OOMKill occurs on the `istio-proxy` container (not the app container).

**Root Cause:** Envoy accumulates stats counters indefinitely if stats are not flushed. Large cluster configurations create memory pressure.

**Diagnostic:**
```bash
# Check memory split between app and sidecar
kubectl top pod order-service-xxx --containers
# High memory in istio-proxy container = Envoy issue

# Check Envoy stats count
kubectl exec order-service-xxx -c istio-proxy -- \
  curl -s http://localhost:15000/stats | wc -l
# Very high count = excessive stats accumulation
```

**Fix:** Set memory limits on the Envoy sidecar container. Tune stats flushing interval. Upgrade Envoy version (many memory improvements in recent versions).

**Prevention:** Monitor Envoy memory separately from app memory. Set resource limits in Istio's MeshConfig for sidecar defaults.

**2. HTTP/1.1 vs HTTP/2 Mismatch**

**Symptom:** `GRPC_STATUS_14 (UNAVAILABLE)` errors between services. gRPC calls fail intermittently.

**Root Cause:** Envoy receives gRPC (HTTP/2) from the app but forwards as HTTP/1.1 to the upstream. gRPC requires HTTP/2 end-to-end.

**Diagnostic:**
```bash
# Check Envoy cluster protocol
istioctl proxy-config cluster order-service-xxx.production \
  | grep payments-service
# Should show: payments-service HTTP2
```

**Fix:**
```yaml
# Annotate Kubernetes Service to declare HTTP/2
kind: Service
metadata:
  annotations:
    # Tell Istio: use HTTP/2 for this service
    service.istio.io/canonical-name: payments-service
spec:
  ports:
    - name: grpc    # name must start with 'grpc' for H2
      port: 8080
```

**Prevention:** Name Kubernetes Service ports with protocol prefix: `grpc-*` or `http2-*` for Istio protocol detection.

**3. Circuit Breaker Open - Envoy Rejects All Requests**

**Symptom:** Service returns 503 immediately with `x-envoy-overloaded: true` header. Upstream service is healthy.

**Root Cause:** Envoy's circuit breaker `max_pending_requests` or `max_connections` threshold exceeded - too many requests queued waiting for slow upstream.

**Diagnostic:**
```bash
# Check circuit breaker stats
kubectl exec order-service-xxx -c istio-proxy -- \
  curl -s http://localhost:15000/stats | \
  grep "upstream_rq_pending_overflow"
# Non-zero = circuit breaker is shedding load
```

**Fix:** Tune circuit breaker thresholds to match upstream capacity. Increase Envoy connection pool size only if upstream can handle it. Add backpressure in the calling service.

**Prevention:** Load test Envoy circuit breaker thresholds in staging with realistic upstream latency profiles. Set thresholds based on measured upstream capacity.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Service Mesh (Microservices)` - Envoy is the data plane of all major service meshes; understanding the service mesh concept contextualises Envoy's role
- `Networking` - L4/L7 networking concepts (TCP, HTTP, TLS) are foundational for understanding what Envoy operates on

**Builds On This (learn these next):**
- `Istio` - the most widely deployed control plane for Envoy; Istio's CRDs translate to Envoy xDS config
- `Circuit Breaker (Microservices)` - Envoy implements circuit breaking via outlier detection; understanding the pattern contextualises the config

**Alternatives / Comparisons:**
- `nginx` - the traditional reverse proxy; simpler to configure for static HTTP scenarios but lacks Envoy's dynamic API and native observability
- `Linkerd-proxy` - a lighter-weight Rust sidecar proxy used in Linkerd service mesh; simpler but fewer features than Envoy

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ High-performance C++ proxy used as a      │
│              │ sidecar in service meshes and as a        │
│              │ standalone API gateway                    │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Networking concerns (retry, CB, observ.)  │
│ SOLVES       │ reimplemented inconsistently per language │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ xDS API enables dynamic reconfiguration   │
│              │ of thousands of Envoy instances without   │
│              │ restarts - this is what makes service     │
│              │ meshes at scale possible                  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Service mesh data plane, polyglot envs,   │
│              │ dynamic routing, gRPC, high observability │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Simple static HTTP reverse proxy - nginx  │
│              │ is simpler to configure and operate       │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Rich dynamic features vs operational      │
│              │ complexity and C++ debugging expertise    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Every service's personal bodyguard,      │
│              │  secretary, and accountant in one."       │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Istio → Circuit Breaker →                 │
│              │ Distributed Logging                       │
└──────────────────────────────────────────────────────────┘
```


---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Infrastructure logic belongs in infrastructure, not application code. Envoy externalised retry, timeout, circuit breaking, observability, and TLS from every service into a single consistent proxy. When each service implements these independently, bugs in one service's resilience logic do not benefit other services. A centralised, consistently configured proxy is the correct place for cross-service infrastructure behaviour.

**Where else this pattern appears:**
- **Kubernetes:** Kubernetes externalised container lifecycle management (previously Puppet/Ansible/init scripts), networking (CNI), and service discovery (previously Eureka in application code) - the same externalisation principle.
- **Managed databases:** RDS externalised backup, replication, and failover from each team's custom database management scripts into managed infrastructure.
- **CDN:** Content delivery networks externalised caching, geographic routing, and SSL termination from each application's custom code into managed infrastructure.

---

### 💡 The Surprising Truth

Envoy's configuration API (xDS) is a distributed systems protocol more complex than most distributed systems it manages. A full Envoy configuration involves five separate gRPC streams (LDS, RDS, CDS, EDS, SDS), each with its own consistency model and failure mode. When Envoy is misconfigured (a common occurrence during control plane issues), traffic can be silently black-holed - all responses appear to succeed at the proxy level but no traffic reaches the upstream service. Debugging Envoy misconfiguration requires understanding xDS at a level of detail that most engineers take weeks to develop, making Envoy expertise one of the highest-value skills in modern platform engineering.
---

### 🧠 Think About This Before We Continue

**Q1.** An Envoy sidecar is configured with a circuit breaker: eject any upstream endpoint that returns 5 consecutive 5xx errors. Your payments service has 3 pods. All 3 return 503 simultaneously because an external payment gateway (not in the mesh) is down. Envoy ejects all 3 pods. Describe exactly what happens to traffic for the next 30 seconds while pods are ejected, how Envoy detects when they should be put back in rotation, and what application-level response (fallback vs error) is most appropriate when all endpoints are ejected.

*Hint:* Think about what happens when all endpoints are ejected: Envoy enters 'panic mode' and routes to all endpoints regardless of ejection status to prevent total blackout. This is configurable via `panic_threshold`. Explore whether the correct configuration for a payment service with no fallback is to return 503 (circuit open) rather than routing to ejected endpoints in panic mode, and what the application should do when all Envoy endpoints are ejected (return a clear payment-unavailable response, not attempt a payment that will fail).

**Q2.** You are migrating from a monolithic nginx configuration (3000 lines, static, requires reload) to Envoy with dynamic xDS configuration. Your nginx config has complex rewrite rules, multiple SSL certificates with different SNI configurations, and custom Lua request manipulation scripts. Design the migration strategy: which Envoy components replace each nginx capability, how you achieve zero-downtime migration of the SSL certificates to Envoy's SDS (Secret Discovery Service), and what the operational runbook looks like for rolling back to nginx if Envoy exhibits unexpected behaviour in production.

*Hint:* Think about what nginx capabilities need Envoy equivalents: complex rewrite rules (Envoy route matchers + header manipulation actions), SNI-based SSL (Envoy FilterChainMatch on `server_names`), Lua scripts (Envoy lua filter or ext_proc for external processing). Explore whether migrating endpoint-by-endpoint (one virtual host at a time, splitting traffic between nginx and Envoy at the load balancer level) is safer than an all-at-once cutover, and what the zero-downtime SDS certificate migration looks like (add to Envoy SDS while nginx still serves, shift DNS to Envoy, decommission nginx).

**Q3 (Design Trade-off):** A security CVE in Envoy requires upgrading all 500 Envoy sidecars in your cluster within 24 hours. Your current process (update Istio, roll all 500 deployments) takes 72 hours. Design a process that meets the 24-hour SLA for Envoy security upgrades.

*Hint:* Think about what the 72-hour upgrade time is composed of: time to build a patched Istio release with the new Envoy (often hours after CVE disclosure), time to roll 500 deployments at your current rollout rate, and time to validate each service. Explore whether a dedicated Envoy image tag (independent of the Istio release cycle) allows security patches to be applied to Envoy without waiting for a full Istio release, and whether automated rolling with automated health checks can parallelise the validation step across all 500 services.
