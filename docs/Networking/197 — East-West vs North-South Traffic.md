---
layout: default
title: "East-West vs North-South Traffic"
parent: "Networking"
nav_order: 197
permalink: /networking/east-west-vs-north-south-traffic/
number: "0197"
category: Networking
difficulty: ★★★
depends_on: Load Balancer L4_L7, Network Topologies, Microservices
used_by: Kubernetes, Distributed Systems, Service Mesh, System Design
related: Service Discovery, Network Policies, mTLS, Load Balancer L4_L7, Overlay Networks
tags:
  - networking
  - east-west
  - north-south
  - traffic
  - microservices
  - service-mesh
---

# 197 — East-West vs North-South Traffic

⚡ TL;DR — **North-South traffic**: flows between external clients and the datacenter/cluster (client → load balancer → app). **East-West traffic**: flows between services inside the datacenter/cluster (order-service → payment-service → inventory-service). Modern microservices architectures are dominated by East-West traffic (often 80-90% of all traffic). This distinction matters for security (mTLS, network policies), performance (service mesh latency), and observability (internal call tracing).

---

### 🔥 The Problem This Solves

In a monolith, a user request hits the app once. In a microservices architecture, one user request might trigger 10-50 internal service-to-service calls. If you only monitor and secure the front door (North-South), you're blind to 90% of your traffic. Service-level security (mTLS, authorisation policies, rate limiting) and observability (distributed tracing, per-service metrics) exist specifically because East-West traffic is where most failures, latency, and security vulnerabilities actually occur.

---

### 📘 Textbook Definition

**North-South Traffic:** Traffic that crosses the datacenter/cluster boundary. External clients (browsers, mobile apps, external APIs) → ingress (load balancer, API gateway, Ingress Controller) → internal services. Controlled by: load balancers, API gateways, WAF, Ingress Controllers (Kubernetes).

**East-West Traffic:** Traffic between services within the same datacenter/cluster. Service A → Service B → Service C — all internal. Controlled by: service mesh (Istio, Linkerd), network policies, internal load balancers, service discovery.

The metaphor: on a map, North-South = entering/leaving the country (border control); East-West = travelling within the country (internal roads).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
North-South = traffic crossing the cluster boundary (external clients in/out). East-West = service-to-service traffic inside the cluster. Microservices create massive East-West volumes that need their own security, routing, and observability.

**One analogy:**

> Imagine a large hotel. North-South = guests entering and leaving through the front door (managed by reception). East-West = communication between kitchen, housekeeping, maintenance, and reception (walkie-talkies and internal phones). If you only monitor the front door, you have no idea what's happening inside — and most of the hotel's activity is internal coordination.

---

### 🔩 First Principles Explanation

**NORTH-SOUTH IN DETAIL:**

```
External Client (browser, mobile app, external service)
       ↓  HTTPS
   DNS → CDN → WAF → Load Balancer (Layer 7)
       ↓
   Kubernetes Ingress Controller (NGINX, Traefik, Istio Gateway)
       ↓
   Service (ClusterIP) → Pod
       ↓
   Response back to external client

Controls:
  - TLS termination (at load balancer or ingress)
  - Authentication (API keys, OAuth tokens)
  - Rate limiting (protect against abuse)
  - WAF (SQL injection, XSS blocking)
  - DDoS protection (Cloudflare, AWS Shield)
  - Routing (path-based, host-based)
```

**EAST-WEST IN DETAIL:**

```
External Request hits: user-service
user-service calls: auth-service (is this token valid?)
user-service calls: profile-service (get user profile)
user-service calls: notification-service (send welcome email)
notification-service calls: email-template-service
notification-service calls: SMTP-gateway

One user request = 5+ internal calls = East-West traffic

Without service mesh:
  Service A → HTTP → Service B (plaintext, untracked)
  Problems:
    - No authentication (anyone in cluster can call anyone)
    - No encryption (internal traffic can be sniffed)
    - No observability (which calls succeeded? latency?)
    - No retries, circuit breaking (cascading failures)

With service mesh (Istio):
  Service A → [Envoy sidecar] → mTLS → [Envoy sidecar] → Service B
  All East-West traffic:
    - mTLS encrypted and authenticated (Zero Trust)
    - Automatic distributed tracing (via B3/W3C trace headers)
    - Per-route metrics (latency, error rate, throughput)
    - Traffic policies (retries, timeouts, circuit breaking)
    - Authorisation policies ("only order-service can call payment-service")
```

**KUBERNETES INGRESS VS INTERNAL SERVICE:**

```
North-South (Kubernetes):
  Ingress resource → IngressController → Service → Pods
  External IP exposed; TLS at ingress; host/path routing

East-West (Kubernetes):
  Service discovery: my-svc.namespace.svc.cluster.local
  ClusterIP: internal IP, not accessible outside cluster
  Pod-to-pod: directly via pod IP (within same node or cross-node)

Network Policy (East-West enforcement):
  By default: all pods can talk to all pods (flat network)
  Network Policy: whitelist-based — specify allowed ingress/egress
  Example: only allow order-service → payment-service on 8080
```

**TRAFFIC RATIO IN MICROSERVICES:**

```
Monolith:
  1 user request = 1 external hit = 1 database query
  North-South : East-West ≈ 100% : 0%

Microservices:
  1 user request = 1 external hit + 10-50 internal calls
  North-South : East-West ≈ 5% : 95%

Implications:
  - Latency budget: most latency is in East-West calls
  - Network bandwidth: size your internal network for East-West
  - Security: if only securing North-South, 95% of traffic unprotected
  - Observability: distributed tracing needed for East-West call chains
```

---

### 🧪 Thought Experiment

**DIAGNOSING A LATENCY PROBLEM:**
Users report checkout takes 3 seconds. You look at North-South metrics: the load balancer shows p99 = 3s. But looking only at the entry point won't tell you WHERE the latency is. You enable distributed tracing (Jaeger/Zipkin) and look at the East-West call chain: user-service(10ms) → cart-service(20ms) → inventory-service(2800ms) → payment-service(100ms). The inventory-service is the culprit — it's making a slow database call. Without East-West observability, you'd never find this.

---

### 🧠 Mental Model / Analogy

> Think of a city's transportation network. North-South = highways entering and leaving the city (monitored at toll booths, controlled at border). East-West = the city's internal street network (most daily commuting happens here). Building a modern city, you need to design the internal road network (East-West) carefully — traffic lights, one-way streets, throughput — not just the highway on-ramps (North-South). Most traffic jams happen internally, not at the border.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** North-South = traffic in/out of your system (external users). East-West = traffic between your services (internal). Most microservice problems (latency, failures, security) happen in East-West traffic.

**Level 2:** Tools: North-South → Ingress Controllers, API Gateways, WAF, CDN. East-West → Service Mesh (Istio, Linkerd), Network Policies, internal load balancers (Kubernetes Service). Kubernetes: services exposed externally = LoadBalancer/NodePort/Ingress. Internal services = ClusterIP (East-West only).

**Level 3:** Istio handles both North and East-West: North-South via Istio Gateway (replaces Kubernetes Ingress), East-West via Envoy sidecars. VirtualService and DestinationRule configure routing for both. mTLS PeerAuthentication (East-West) vs Gateway TLS (North-South). Service mesh adds ~1-3ms per hop (sidecar overhead) — relevant in high-throughput East-West. Alternatives: eBPF-based service mesh (Cilium) avoids sidecar overhead by implementing networking in kernel.

**Level 4:** Data center network design implications: East-West traffic drives spine-leaf adoption. Traditional three-tier networks were designed for North-South (client → server). Cloud workloads and microservices are dominated by East-West (server → server). This is why modern datacenters use spine-leaf (equal bandwidth in all directions) instead of hierarchical tree (bottleneck at aggregation layer). Same logic in cloud: Transit Gateway routes East-West between VPCs. VPC peering directly routes East-West without traversing the internet. AWS PrivateLink enables East-West between VPCs without routing through the internet.

---

### ⚙️ How It Works (Mechanism)

```yaml
# Kubernetes: North-South — expose service externally
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: api-ingress
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  rules:
    - host: api.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: api-service
                port:
                  number: 80
---
# Kubernetes: East-West — internal service (ClusterIP)
apiVersion: v1
kind: Service
metadata:
  name: payment-service
spec:
  selector:
    app: payment
  ports:
    - port: 8080
  # No type: LoadBalancer — ClusterIP only, East-West only
---
# Istio: East-West mTLS + routing policy
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: production
spec:
  mtls:
    mode: STRICT # All East-West traffic must be mTLS
---
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: payment-service
spec:
  hosts:
    - payment-service # East-West (internal DNS)
  http:
    - retries:
        attempts: 3
        retryOn: 5xx
      timeout: 2s
      route:
        - destination:
            host: payment-service
            port:
              number: 8080
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
E-commerce checkout — full traffic path:

[Browser] → North-South →
  CDN (static assets cached here)
    ↓
  WAF (block SQL injection)
    ↓
  AWS ALB (TLS termination, North-South entry point)
    ↓
  Kubernetes Ingress Controller (route /checkout → checkout-service)

[Inside cluster — all East-West]:
  checkout-service → [mTLS] → cart-service (get cart items)
  checkout-service → [mTLS] → inventory-service (check stock)
  checkout-service → [mTLS] → pricing-service (calculate total)
  checkout-service → [mTLS] → payment-service (charge card)
  checkout-service → [mTLS] → order-service (create order)
  order-service → [mTLS] → notification-service (send confirmation)
  notification-service → [mTLS] → email-service

North-South: 1 request
East-West: 7 internal calls

← Response: order confirmation
← Back through Ingress → ALB → browser (North-South return)
```

---

### 💻 Code Example

```python
# East-West service discovery and call pattern (Python, Kubernetes)
import httpx
import asyncio
from opentelemetry import trace
from opentelemetry.propagate import inject

tracer = trace.get_tracer("checkout-service")

class CheckoutService:
    # East-West: use Kubernetes DNS (service.namespace.svc.cluster.local)
    CART_SERVICE = "http://cart-service.production.svc.cluster.local:8080"
    PAYMENT_SERVICE = "http://payment-service.production.svc.cluster.local:8080"
    INVENTORY_SERVICE = "http://inventory-service.production.svc.cluster.local:8080"

    async def checkout(self, user_id: str, session_id: str) -> dict:
        headers = {}

        with tracer.start_as_current_span("checkout") as span:
            inject(headers)  # Propagate trace context (East-West tracing)
            span.set_attribute("user.id", user_id)

            async with httpx.AsyncClient() as client:
                # Parallel East-West calls (reduce latency)
                cart_task = client.get(
                    f"{self.CART_SERVICE}/cart/{user_id}",
                    headers=headers, timeout=2.0
                )
                # Can parallelise independent calls
                cart_resp = await cart_task
                cart = cart_resp.json()

                # Sequential calls where order matters
                payment_resp = await client.post(
                    f"{self.PAYMENT_SERVICE}/charge",
                    json={"amount": cart["total"], "session": session_id},
                    headers=headers, timeout=5.0
                )

                return {"order_id": payment_resp.json()["order_id"]}
```

---

### ⚖️ Comparison Table

| Aspect                 | North-South                              | East-West                            |
| ---------------------- | ---------------------------------------- | ------------------------------------ |
| Direction              | External → cluster or cluster → external | Service → service inside cluster     |
| Volume (microservices) | ~5-20% of all traffic                    | ~80-95% of all traffic               |
| Controls               | Ingress, API Gateway, WAF, CDN           | Service mesh, Network Policies, mTLS |
| Authentication         | OAuth tokens, API keys                   | mTLS, SPIFFE/SPIRE workload identity |
| Observability          | Load balancer access logs                | Distributed tracing (Jaeger/Zipkin)  |

---

### ⚠️ Common Misconceptions

| Misconception                                         | Reality                                                                                                                                                                          |
| ----------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Securing the API gateway secures all traffic          | API gateway only handles North-South. 95% of microservice traffic (East-West) is still unprotected without mTLS and network policies                                             |
| East-West traffic is all "trusted" (internal network) | Zero Trust: internal traffic should be authenticated and authorised. A compromised internal service can call any other service unless East-West controls are in place            |
| Service mesh is only for large organisations          | Any microservices architecture with >3 services benefits from East-West observability. Even lightweight options (Linkerd) add distributed tracing and mTLS with minimal overhead |

---

### 🚨 Failure Modes & Diagnosis

**East-West Latency Spike: Cascading Failure**

```bash
# Symptom: North-South p99 latency suddenly spikes to 10s
# Cause: one internal East-West dependency is slow

# Step 1: check distributed traces (Jaeger/Zipkin)
# Look at trace spans for recent checkout requests
# Find which internal call has high latency

# Step 2: check Istio metrics per service
kubectl exec -n istio-system deployment/prometheus -- \
  curl -s 'http://localhost:9090/api/v1/query?query=
    histogram_quantile(0.99,
      sum(rate(istio_request_duration_milliseconds_bucket{
        destination_service_name="payment-service"
      }[5m])) by (le)
    )'

# Step 3: check for East-West connection errors
kubectl logs -n production deployment/checkout-service -c istio-proxy | \
  grep -E "UF|UC|UH"  # Upstream Failure/Connection Failure/No Healthy Upstreams

# Step 4: circuit breaker status (if configured)
# If payment-service is failing, circuit breaker should open
# Check Kiali dashboard or Prometheus for circuit breaker state

# Step 5: network policies blocking traffic?
kubectl get networkpolicies -n production
# Test connectivity:
kubectl exec -n production deploy/checkout-service -- \
  curl -v http://payment-service:8080/health
```

---

### 🔗 Related Keywords

**Prerequisites:** `Load Balancer L4/L7`, `Network Topologies`, `Microservices`

**Related:** `Service Discovery`, `Network Policies`, `mTLS`, `Overlay Networks`, `Service Mesh`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ NORTH-SOUTH  │ External ↔ cluster; ingress, API GW, WAF  │
│ EAST-WEST    │ Service ↔ service inside cluster          │
├──────────────┼───────────────────────────────────────────┤
│ VOLUME       │ Microservices: ~5% N-S, ~95% E-W          │
├──────────────┼───────────────────────────────────────────┤
│ E-W TOOLS    │ Service mesh, NetworkPolicy, mTLS, Istio  │
│ N-S TOOLS    │ Ingress, API Gateway, WAF, CDN, ALB       │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Secure the front door AND all internal   │
│              │ corridors — most traffic is internal"     │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You're architecting observability for a 50-service microservices system. (a) Explain why request-level metrics at the load balancer (North-South) are insufficient for diagnosing latency: a p99 spike of 5s could originate from any of 10 services in a call chain. (b) Design a distributed tracing strategy: how do trace context headers (W3C traceparent: 00-traceId-spanId-flags) propagate through East-West HTTP calls, and how do you handle async messaging (Kafka, SQS) where headers can't be passed directly? (c) Explain the difference between RED metrics (Rate, Error rate, Duration) per service vs USE metrics (Utilisation, Saturation, Errors) per infrastructure component — which is better for diagnosing East-West failures? (d) Design a SLO (Service Level Objective) for an internal East-West service that isn't user-facing: what metrics matter, what are appropriate targets (e.g., p99 < 50ms for payment-service), and how do you alert on SLO burn rate without paging teams for every spike?
