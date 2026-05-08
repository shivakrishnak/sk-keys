---
layout: default
title: "Service Mesh on K8s"
parent: "Kubernetes"
nav_order: 62
permalink: /kubernetes/service-mesh-on-k8s/
id: K8S-062
category: "Kubernetes"
difficulty: "★★★"
depends_on: ["Kubernetes Networking (CNI)", "Ingress", "Pod", "Service (K8s)"]
used_by: ["K8s Multi-Cluster", "K8s Observability", "K8s Security Hardening"]
related:
  [
    "Kubernetes Networking (CNI)",
    "Calico / Cilium",
    "Ingress Controller",
    "K8s Multi-Cluster",
  ]
tags:
  [
    kubernetes,
    service-mesh,
    istio,
    linkerd,
    envoy,
    mtls,
    traffic-management,
    k8s,
  ]
---

# Service Mesh on K8s

## ⚡ TL;DR

A **Service Mesh** provides: mTLS between services (zero-trust), traffic management (canary, retry, circuit breaker), and observability (L7 metrics, traces) — without changing application code. Implemented via sidecar proxies (Istio/Envoy, Linkerd/Linkerd-proxy) or eBPF (Cilium Service Mesh). Powerful but adds operational complexity.

---

## 🔥 Problem This Solves

In microservices: each service needs TLS, retries, circuit breaking, timeout handling, distributed tracing injection, and traffic splitting. Implementing all this in every service = code duplication. A service mesh handles it at the infrastructure layer for all services uniformly.

---

## 📘 Textbook Definition

A service mesh is a dedicated infrastructure layer that handles service-to-service communication. It provides features like mutual TLS, traffic management, load balancing, circuit breaking, and observability through proxies deployed alongside services (sidecars) or eBPF-based approaches, without requiring application code changes.

---

## ⏱️ 30 Seconds

```
With service mesh (Istio):
  1. mTLS: all service-to-service calls automatically encrypted + authenticated
  2. Traffic: route 10% to v2, 90% to v1 (canary)
  3. Retry: auto-retry on 503 (up to 3 times)
  4. Circuit breaker: stop sending to unhealthy pods
  5. Metrics: p99 latency per service-to-service path
  6. Traces: distributed trace across all microservices

Zero application code changes needed.
```

---

## 🔩 First Principles

- **Sidecar pattern**: Envoy/Linkerd-proxy runs alongside every Pod, intercepting all network traffic
- **Control plane**: Istio (istiod) / Linkerd (linkerd-control-plane) pushes config to sidecars
- **mTLS**: each sidecar has a certificate (SVID/SPIFFE); traffic is encrypted and authenticated between sidecars
- **Traffic management**: sidecar proxies implement VirtualService rules (canary %, retries, timeouts)
- **Observability**: sidecars emit L7 metrics and trace spans automatically

---

## 🧪 Thought Experiment

You have 20 microservices. Each needs: TLS certs (rotated), retry logic, timeouts, circuit breakers, and distributed tracing. Without mesh: 20 services × 5 features = 100 implementations, each potentially different. With Istio: one `DestinationRule` for circuit breaking, one `PeerAuthentication` for mTLS, one `VirtualService` for retries. Consistent, centrally managed, no code changes.

---

## 🧠 Mental Model / Analogy

Service mesh is like **hiring a dedicated communications team for a large organization**: every employee (service) has a personal communications specialist (sidecar proxy) who handles all their calls (network traffic). The specialist handles encryption, retries, reporting — the employee just does their core job. The communications team leadership (control plane) sets policies for all specialists.

---

## 📶 Gradual Depth

**Level 1 — Beginner**: Service mesh adds mTLS, retries, and metrics to all services without code changes. Istio and Linkerd are the two main options.

**Level 2 — Practitioner**: Istio: label namespace for sidecar injection (`istio-injection: enabled`). Configure `VirtualService` for traffic splitting. `PeerAuthentication` for mTLS mode. `DestinationRule` for circuit breaker. Linkerd: simpler, lighter, but less feature-rich.

**Level 3 — Advanced**: Istio Ambient Mode (no sidecars): ztunnel DaemonSet provides L4 mTLS; waypoint proxy handles L7. Reduces pod overhead from 2 containers to 0 sidecar overhead. `AuthorizationPolicy`: fine-grained L7 RBAC (only frontend can call backend's GET /api). Traffic mirroring: shadow traffic to v2 without affecting v1.

**Level 4 — Expert**: Istio multi-cluster: `ServiceEntry` + east-west gateway for cross-cluster mTLS. SPIFFE/SPIRE for cross-cluster certificate management. Istio and JWT validation: validate JWT tokens at proxy level (AuthorizationPolicy). Progressive delivery with Istio: Flagger controller uses VirtualService weight-shifting for automated canary based on Prometheus error rate. eBPF-based mesh (Cilium Service Mesh): mTLS + L7 observability without sidecars, using eBPF + Envoy as node-level proxy instead.

---

## ⚙️ How It Works

### Istio Architecture

```
Control Plane (istiod):
  - Pilot: service discovery, VirtualService/DestinationRule distribution
  - Citadel: certificate management (SVID issuance, rotation)
  - Galley: config validation

Data Plane:
  - Envoy sidecar in every Pod
  - Intercepts ALL inbound/outbound traffic via iptables
  - Reports metrics/traces to Prometheus/Zipkin
```

### mTLS Flow

```
Pod A (Envoy sidecar) → Pod B (Envoy sidecar):
  1. Pod A app sends to Pod B service IP
  2. iptables redirects to Pod A's Envoy (port 15001)
  3. Pod A's Envoy:
     - Resolves Pod B endpoint
     - TLS: presents Pod A's SVID certificate
     - Verifies Pod B's SVID certificate
  4. Encrypted mTLS connection to Pod B's Envoy
  5. Pod B's Envoy:
     - Terminates TLS
     - Forwards to Pod B's app (port 8080)
     - Applies AuthorizationPolicy

Result: Pod A app ↔ Pod B app via automatic mTLS, no code changes
```

### Istio VirtualService (Traffic Management)

```yaml
# Canary: 10% traffic to v2
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: my-service
spec:
  hosts:
    - my-service
  http:
    - route:
        - destination:
            host: my-service
            subset: v1
          weight: 90
        - destination:
            host: my-service
            subset: v2
          weight: 10
      timeout: 5s
      retries:
        attempts: 3
        perTryTimeout: 2s
        retryOn: gateway-error,connect-failure,retriable-4xx

---
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: my-service
spec:
  host: my-service
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
    outlierDetection: # circuit breaker
      consecutiveGatewayErrors: 5
      interval: 30s
      baseEjectionTime: 30s
      maxEjectionPercent: 100
  subsets:
    - name: v1
      labels:
        version: v1
    - name: v2
      labels:
        version: v2
```

### mTLS Policy

```yaml
# Require mTLS in namespace
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: production
spec:
  mtls:
    mode: STRICT # PERMISSIVE allows both mTLS and plaintext

---
# L7 Authorization
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: backend-policy
  namespace: production
spec:
  selector:
    matchLabels:
      app: backend
  action: ALLOW
  rules:
    - from:
        - source:
            principals: ["cluster.local/ns/production/sa/frontend"]
      to:
        - operation:
            methods: ["GET", "POST"]
            paths: ["/api/*"]
```

### Linkerd (Simpler Alternative)

```bash
# Install Linkerd
linkerd install --crds | kubectl apply -f -
linkerd install | kubectl apply -f -
linkerd check

# Inject namespace
kubectl annotate namespace my-app linkerd.io/inject=enabled

# Observe
linkerd viz install | kubectl apply -f -
linkerd viz dashboard     # opens web UI

# Per-route metrics
linkerd viz top deployment/my-service
```

---

## 🔄 E2E Flow: Canary Deployment with Istio

```
Initial: 100% traffic → my-service:v1

Deploy v2:
  kubectl apply -f deployment-v2.yaml  (replicas: 1)

Shift 10% traffic:
  kubectl apply -f virtualservice-10pct.yaml

Flagger (or manual) monitors:
  - Prometheus: error_rate(v2) < 1% for 5 min? ✅
  - p99 latency(v2) < 500ms? ✅

Shift 25% traffic to v2:
  kubectl apply -f virtualservice-25pct.yaml

Continue monitoring...

100% traffic to v2:
  kubectl apply -f virtualservice-100pct.yaml

Decommission v1:
  kubectl delete deployment my-service-v1
```

---

## ⚖️ Comparison Table

|                          | Istio          | Linkerd                | Cilium Service Mesh       |
| ------------------------ | -------------- | ---------------------- | ------------------------- |
| **Architecture**         | Envoy sidecars | Linkerd-proxy sidecars | eBPF + Envoy (node-level) |
| **Complexity**           | High           | Low                    | Medium                    |
| **Features**             | Full           | Core subset            | L4 + L7 growing           |
| **Performance overhead** | ~5ms p99       | ~2ms p99               | ~0ms (eBPF L4)            |
| **mTLS**                 | ✅             | ✅                     | ✅                        |
| **Traffic management**   | ✅ Full        | Basic                  | Growing                   |
| **CNCF status**          | Graduated      | Graduated              | Graduated                 |

---

## ⚠️ Common Misconceptions

| Misconception                         | Reality                                                                     |
| ------------------------------------- | --------------------------------------------------------------------------- |
| "Service mesh replaces NetworkPolicy" | Mesh provides mTLS + L7 RBAC; NetworkPolicy provides L3/L4 — use both       |
| "Service mesh is free overhead"       | Adds ~5-10% CPU, ~50-100MB RAM per sidecar — significant at scale           |
| "Mesh is required for microservices"  | Many successful microservices platforms run without a mesh; add when needed |
| "Linkerd is just a smaller Istio"     | Different architecture; Linkerd is Rust-based proxy, Istio uses Envoy (C++) |

---

## 🚨 Failure Modes

| Failure                            | Symptom                      | Fix                                                |
| ---------------------------------- | ---------------------------- | -------------------------------------------------- |
| Sidecar injection disabled         | mTLS not applied             | Check namespace label: `istio-injection=enabled`   |
| VirtualService misconfigured       | Traffic drops after applying | Use `istioctl analyze`; check VirtualService hosts |
| mTLS STRICT breaks legacy services | Legacy service can't connect | Use PERMISSIVE mode during migration               |
| Envoy sidecar resource starvation  | Application pods OOM         | Set sidecar resource limits in `ProxyConfig`       |

---

## 🔗 Related Keywords

- [Kubernetes Networking (CNI)](/kubernetes/kubernetes-networking-cni/) — CNI provides L3/L4; mesh adds L7
- [Calico / Cilium](/kubernetes/calico-cilium/) — Cilium is extending into mesh territory
- [K8s Multi-Cluster](/kubernetes/k8s-multi-cluster/) — mesh enables cross-cluster mTLS
- [K8s Security Hardening](/kubernetes/k8s-security-hardening/) — mTLS is zero-trust networking

---

## 📌 Quick Reference Card

```bash
# Istio installation
istioctl install --set profile=default
istioctl verify-install

# Check injection
kubectl get namespace -L istio-injection

# Analyze config issues
istioctl analyze -n production

# Check proxy status
istioctl proxy-status

# Debug traffic
istioctl proxy-config route deploy/my-service
istioctl proxy-config clusters deploy/my-service

# Linkerd check
linkerd check
linkerd viz tap deploy/my-service --namespace production

# View traffic stats
linkerd viz stat deployments -n production
```

---

## 🧠 Think About This

Should you use a service mesh? The honest answer depends on your pain: if you're struggling with L7 observability (which service is slow?), cross-service authentication (is this really my frontend calling my backend?), or complex traffic routing (canary deployments), a mesh solves real problems. But the overhead is real: 2 sidecar containers per Pod, 5-10% CPU overhead, complex CRDs. Many teams start without a mesh and add it when specific pain points emerge. Cilium Service Mesh is emerging as a compelling alternative: eBPF-based with minimal overhead, no sidecars, available as a feature upgrade from your CNI plugin. For new greenfield clusters, evaluate Cilium Service Mesh before committing to Istio.
