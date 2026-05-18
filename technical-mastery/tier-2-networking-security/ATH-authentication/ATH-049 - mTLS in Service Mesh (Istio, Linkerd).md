---
id: ATH-049
title: "mTLS in Service Mesh (Istio, Linkerd)"
category: Authentication
tier: tier-2-networking-security
folder: ATH-authentication
difficulty: ★★★
depends_on: ATH-039, ATH-047, ATH-048
used_by: ATH-053, ATH-054, ATH-056
related: ATH-039, ATH-048, ATH-053
tags:
  - security
  - authentication
  - mtls
  - service-mesh
  - istio
  - linkerd
  - advanced
status: complete
version: 5
layout: default
parent: "Authentication"
grand_parent: "Technical Mastery"
nav_order: 49
permalink: /technical-mastery/authentication/mtls-in-service-mesh-istio-linkerd/
---

⚡ **TL;DR** - Service meshes automate mTLS at the infrastructure
layer so application code does not need to handle certificates.
An Envoy (Istio) or Linkerd proxy sidecar intercepts all traffic
on the loopback interface and negotiates mTLS transparently. Both
sidecar proxies present SPIFFE SVIDs (X.509 certs with SPIFFE IDs
in the SAN) as their workload identity. The benefit: every
service-to-service call in the mesh is mutually authenticated and
encrypted with zero application code changes. The tradeoff:
latency overhead from sidecar hops (typically 1-3ms per hop).

---

### 📊 Entry Metadata

| #049 | Category: Authentication | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | ATH-039 mTLS, ATH-047 Distributed Auth, ATH-048 Service Identity | |
| **Used by:** | ATH-053, ATH-054, ATH-056 | |
| **Related:** | ATH-039 mTLS, ATH-048 Service Identity, ATH-053 Auth Server Arch | |

---

### 📘 Textbook Definition

In a service mesh, mutual TLS (mTLS) is implemented by the
data-plane proxy (Envoy in Istio, Linkerd-proxy in Linkerd)
as a transparent layer between workloads. Each proxy holds
a short-lived X.509 certificate issued by the mesh's CA (Istiod
in Istio, the Linkerd identity component). Certificates use
SPIFFE IDs in the Subject Alternative Name (SAN) field as
the workload identity. The control plane (Istiod, Linkerd
control plane) distributes CA root bundles to each proxy,
enabling mutual certificate validation. PeerAuthentication
(Istio) or Server policy (Linkerd) can enforce STRICT mode
(deny all non-mTLS traffic) or PERMISSIVE mode (allow both
mTLS and plaintext, for migration periods).

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│         Istio Automatic mTLS                           │
├────────────────────────────────────────────────────────┤
│                                                        │
│  Control Plane (Istiod):                               │
│  - Runs SPIFFE-compatible CA                           │
│  - Signs cert requests from Envoy sidecars             │
│  - Issues: spiffe://cluster.local/ns/X/sa/Y            │
│  - Cert validity: 24 hours (default), auto-rotated     │
│  - Distributes root bundle to all Envoy proxies        │
│                                                        │
│  Data Plane (Envoy sidecar, per pod):                  │
│  - Intercepts all inbound/outbound TCP on port 15001   │
│  - Terminates/initiates mTLS with peer Envoy           │
│  - Application talks to sidecar on 127.0.0.1 (plain)  │
│  - Sidecar-to-sidecar traffic: fully mTLS              │
│  - Application: never sees certificates                │
│                                                        │
│  STRICT mode (production):                             │
│  Non-mTLS request from outside mesh -> rejected 403    │
│                                                        │
│  PERMISSIVE mode (migration):                          │
│  Both mTLS and plaintext accepted (shows warnings)     │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - Istio PeerAuthentication STRICT mode**

```yaml
# Enforce mTLS for all services in namespace "prod"
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: prod
spec:
  mtls:
    mode: STRICT
  # mode: STRICT  = reject non-mTLS requests
  # mode: PERMISSIVE = accept both (migration use only)
---
# Verify mTLS is working:
# istioctl proxy-config endpoints payment-svc-xxx.prod \
#   --cluster "outbound|8080||order-svc.prod.svc.cluster.local"
# Should show TLS mode: ISTIO_MUTUAL
```

**Example - Linkerd mTLS status verification**

```bash
# Check if mTLS is active between two pods
linkerd viz edges deployment -n prod

# Expected output (mTLS active):
# CLIENT          SERVER        SECURED
# order-svc       payment-svc   True (mTLS)
# payment-svc     db-svc        True (mTLS)

# If a pod is NOT in the mesh (no sidecar):
# order-svc       legacy-svc    False (no mTLS)
# Action: inject Linkerd sidecar or enable STRICT mode

# Inspect certificate for a specific pod:
linkerd check --proxy -n prod
# Shows: certificate valid until, SAN, issuing CA
```

---

*Authentication category: ATH | Entry: ATH-049 | v5.0*