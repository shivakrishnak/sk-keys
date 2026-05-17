---
id: MSV-075
title: mTLS in Microservices
category: Microservices
tier: tier-5-distributed-architecture
folder: MSV-microservices
difficulty: ★★★
depends_on:
used_by:
related:
tags:
  - microservices
  - security
  - deep-dive
status: draft
version: 0
layout: default
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 75
permalink: /microservices/mtls-in-microservices/
---

# MSV-075 - mTLS in Microservices

⚡ TL;DR - mTLS (Mutual TLS) in Microservices:
both sides of a connection present X.509 certificates,
so each service VERIFIES the identity of the service
it's talking to. Standard TLS: only server proves
identity. mTLS: BOTH sides present certs. In
microservices: Istio auto-issues SPIFFE/X.509
certificates to every pod and auto-enforces mTLS
for all service-to-service traffic. Result: each
service proves its identity; no service can
impersonate another; traffic is encrypted; no
secrets or tokens needed for service-to-service
auth. Zero Trust Networking at the transport layer.

| #075 | Category: Microservices | Difficulty: ★★★☆ |
|:---|:---|:---|
| **Depends on:** | Sidecar Pattern, Service Mesh, What are Microservices | |
| **Used by:** | Sidecar Pattern, Ambassador Pattern | |
| **Related:** | Sidecar Pattern, Ambassador Pattern, Service Mesh Traffic Management, Service Mesh, Zero Trust Security, Microservices Security Patterns | |

---

### 🔥 The Problem This Solves

**SERVICE IMPERSONATION IN MICROSERVICES:**
30 microservices on a Kubernetes cluster. Network
security: only internal cluster traffic allowed
(NetworkPolicy). But: any pod CAN call any other
pod directly (no authentication). A compromised
pod can call payment-service directly, impersonating
order-service. With mTLS: payment-service verifies
the CERTIFICATE of the caller. Order-service
certificate: issued to `spiffe://cluster/ns/orders/
sa/order-service`. Payment-service: verifies
this SPIFFE identity and REJECTS calls from
any other identity (even if on the same cluster).

---

### 📘 Textbook Definition

**mTLS (Mutual Transport Layer Security) in
Microservices** is the application of mutual
authentication at the TLS handshake level: both
the client AND the server present X.509 certificates
and verify each other's identity. In standard TLS:
only the SERVER presents a certificate. In mTLS:
the CLIENT also presents a certificate (server
knows WHO is calling). In microservices, mTLS
is the foundation of service-to-service authentication
("workload identity").

Implementation approaches:
(1) **Service Mesh (Istio/Linkerd)**: auto-issues
SPIFFE/X.509 certs to each workload, auto-enforces
mTLS for all service-to-service traffic. Zero
developer configuration needed.
(2) **Manual/Application-level**: each service
manages its own client certificate, configures
TLS in the HTTP client. Higher effort, error-prone.
(3) **API Gateway**: mTLS at the edge only.

SPIFFE (Secure Production Identity Framework
For Everyone): standard for workload identity.
SPIFFE ID format: `spiffe://<trust-domain>/
ns/<namespace>/sa/<service-account>`. Istio:
auto-issues SPIFFE/X.509 certs via Citadel/cert-
manager. Certificate rotation: automatic (every
24 hours by default).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
mTLS: both services prove their identity with
certificates. Neither can impersonate the other.
Istio automates this for all pods - zero app code.

**One analogy:**
> Standard TLS is like a bank showing its license
> to the customer. mTLS is like BOTH the bank
> AND the customer showing their ID. In microservices:
> payment-service is the bank; order-service is
> the customer. mTLS: both present certificates.
> Payment-service: verifies order-service's identity
> BEFORE processing any request. No certificate
> = no access, even from within the cluster.

**One insight:**
mTLS solves the flat network problem. Without
mTLS: all services on the same cluster can call
each other freely. A single compromised service:
can reach ALL others (lateral movement). With
mTLS: each service has a cryptographic identity.
Compromised pod: cannot obtain another service's
certificate. Lateral movement: stopped.

---

### 🔩 First Principles Explanation

**MTLS HANDSHAKE vs TLS HANDSHAKE:**

```
STANDARD TLS (one-way):
  Client -> Server: ClientHello
  Server -> Client: ServerCertificate
    (proves: "I am payment-service")
  Client: verifies server cert
  Client -> Server: encrypted data
  Server: does NOT know who the client is
  Problem: any caller (even attacker) can connect

mTLS (mutual):
  Client -> Server: ClientHello
  Server -> Client: ServerCertificate +
                    "Please send your cert"
  Client -> Server: ClientCertificate
    (proves: "I am order-service"
     SPIFFE ID inside the cert)
  Server: verifies client cert against trusted CA
  Server: extracts SPIFFE ID from client cert
  Server: checks AuthorizationPolicy:
    principal: .../ns/orders/sa/order-service
    -> ALLOW -> process request
    (if not in allowed list -> 403 Forbidden)
  
  Result: bidirectional authentication
  + authorization based on verified identity

SPIFFE CERTIFICATE STRUCTURE:
  Subject Alternative Name:
    spiffe://cluster.local/ns/orders/sa/order-service
  Issuer: Istio CA (cluster-internal)
  Valid: 24 hours (auto-rotated by Istio)
  
  SPIFFE ID encodes:
    trust domain: cluster.local
    namespace: orders
    service account: order-service
```

**ISTIO mTLS MODES:**

```yaml
# PERMISSIVE: accepts both mTLS and plaintext
# Migration phase only - NOT production
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: orders
spec:
  mtls:
    mode: PERMISSIVE
---
# STRICT: mTLS required; reject all plaintext
# Production standard
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: orders
spec:
  mtls:
    mode: STRICT
# Migration path:
# 1. PERMISSIVE (all traffic works while enabling)
# 2. Enable Istio injection on all services
# 3. Verify all services use mTLS (Kiali graph)
# 4. Switch to STRICT (reject plaintext)
```

---

### 🧪 Thought Experiment

**ZERO-TRUST: mTLS + AUTHORIZATION POLICY**

```
5 services: order, fraud, customer, inventory, payment
Rule: only order + fraud can call payment
customer/inventory: no reason to call payment

WITHOUT mTLS + AuthorizationPolicy:
  All 5 services: can call payment-service
  Attacker compromises customer-service:
    Calls payment-service directly
    (same network; no identity check)
    Exfiltrates: payment data

WITH Istio mTLS + AuthorizationPolicy:
  AuthorizationPolicy on payment-service:
    allowed principals:
    - .../ns/orders/sa/order-service
    - .../ns/fraud/sa/fraud-service
  
  Attacker compromises customer-service:
    customer-service calls payment-service
    Envoy (payment-service sidecar):
      Verifies: customer-service SPIFFE cert
      ID: .../ns/customers/sa/customer-svc
      NOT in allowed principals -> 403 DENIED
    Lateral movement: blocked
    Exfiltration: prevented
```

---

### 🧠 Mental Model / Analogy

> mTLS is like a high-security office with biometric
> badges. Without mTLS: any employee (service)
> with a keycard (network access) enters any room
> (calls any service). A stolen keycard (compromised
> pod): opens all doors. With mTLS: each employee
> has a unique biometric badge (SPIFFE certificate).
> Each door checks BOTH the badge AND an access
> list (AuthorizationPolicy). Stolen badge: cannot
> be replicated (private key never leaves the pod).

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
mTLS: both services prove their identity with
cryptographic certificates before talking.
Prevents: a malicious service pretending to be
a trusted service.

**Level 2 - Istio basics (junior developer):**
Enable Istio injection on namespace. Istio auto-
issues a certificate to every pod, forces all
traffic to use mTLS. Developer: writes normal
HTTP calls. Envoy sidecar: handles mTLS transparently.
No application code changes.

**Level 3 - Authorization policy (mid-level):**
PeerAuthentication (STRICT): verifies certificates.
AuthorizationPolicy: permits specific source
SPIFFE IDs to call specific operations. Granularity:
namespace-level, service-level, or per-path/method.
Kiali: visualize mTLS status (green padlock = mTLS;
grey open padlock = plaintext).

**Level 4 - Certificate management (senior):**
Istiod (cert-manager): issues SVID (SPIFFE Verifiable
Identity Document) to each pod. Default cert
lifetime: 24 hours. Rotation: automatic (Envoy
re-requests cert 5 min before expiry). Cross-
cluster: SPIFFE federation allows mTLS across
Kubernetes clusters with different trust domains.
Custom CA: integrate with Vault PKI or AWS ACM.

**Level 5 - Production hardening (principal):**
Security audit checklist: (1) All namespaces
have STRICT PeerAuthentication; (2) All services
have explicit AuthorizationPolicy (deny-all +
allow-list); (3) Cert expiry monitoring (alert
if expiry < 6 hours); (4) Audit Envoy access
logs for 403s; (5) RBAC for who can modify
AuthorizationPolicy (CI pipeline that writes
policies = potential bypass of mTLS controls).

---

### ⚙️ How It Works (Mechanism)

```yaml
# Complete mTLS setup for payment namespace

# Step 1: Strict mTLS
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: payments
spec:
  mtls:
    mode: STRICT
---
# Step 2: Deny all by default
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: deny-all
  namespace: payments
spec: {}  # empty = deny all
---
# Step 3: Allow specific callers
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: payment-service-allow
  namespace: payments
spec:
  selector:
    matchLabels:
      app: payment-service
  action: ALLOW
  rules:
  - from:
    - source:
        principals:
        - "cluster.local/ns/orders/sa/order-service"
        - "cluster.local/ns/fraud/sa/fraud-service"
    to:
    - operation:
        methods: ["POST"]
        paths: ["/api/v1/payments"]
  - from:
    - source:
        principals:
        - "cluster.local/ns/monitoring/sa/prometheus"
    to:
    - operation:
        methods: ["GET"]
        paths: ["/actuator/prometheus"]
# Only order + fraud can POST /payments
# Only prometheus can GET /actuator/prometheus
# All others: 403 DENIED at Envoy level
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
mTLS: order-service -> payment-service

1. Certificate issuance (at pod startup):
   Envoy sidecar starts
   Envoy -> Istiod: CSR for order-service identity
   Istiod: verifies K8s ServiceAccount JWT token
   Istiod -> Envoy: SPIFFE certificate
     (spiffe://cluster.local/ns/orders/sa/order-svc)
   Cert stored: in Envoy memory only

2. Request flow:
   OrderService: httpClient.post("/payments")
   iptables: intercepts; routes to Envoy port 15001
   Envoy (caller): initiates mTLS
     - presents: order-service SPIFFE cert
     - verifies: payment-service cert
   Envoy (payment-service):
     - presents: payment-service cert
     - verifies: order-service cert
     - extracts: SPIFFE ID from cert
     - checks: AuthorizationPolicy -> ALLOW
     - forwards: to app on localhost:8080

3. Application sees:
   Plain HTTP on localhost:8080
   No TLS handling in application code
   X-Forwarded-Client-Cert header: available
     (if app needs to log caller identity)
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: no identity auth vs mTLS**

```java
// BAD: no service identity verification
// Any pod on the same network can call this
@PostMapping("/api/v1/payments")
public PaymentResponse processPayment(
        @RequestBody PaymentRequest req) {
    // Who is calling? Completely unknown.
    // Compromised pod on cluster: full access
    return paymentService.process(req);
}
```

```yaml
# GOOD: mTLS + AuthorizationPolicy
# Application code: UNCHANGED
# Envoy: handles all identity verification
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: payment-policy
  namespace: payments
spec:
  selector:
    matchLabels:
      app: payment-service
  action: ALLOW
  rules:
  - from:
    - source:
        principals:
        - "cluster.local/ns/orders/sa/order-service"
    to:
    - operation:
        methods: ["POST"]
        paths: ["/api/v1/payments"]
# PaymentController: zero code changes
# Any other caller: 403 at Envoy level
# Before request even reaches Spring Boot app
```

---

### ⚖️ Comparison Table

| Approach | Identity | Config Effort | Notes |
|---|---|---|---|
| **Istio mTLS STRICT** | Cryptographic SPIFFE | Low (auto-inject) | Zero Trust transport |
| **JWT Bearer Token** | Cryptographic token | Medium (code + keys) | User identity only |
| **Network Policy only** | IP-based (spoofable) | Medium (YAML) | Not true identity |
| **API Key** | Secret-based | Medium (rotation) | Revocable |
| **No auth (flat net)** | None | None | Dangerous |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| mTLS replaces application-level authentication | mTLS provides WORKLOAD identity (this pod is order-service). It does NOT provide USER identity (this request is from user Alice). You still need JWT/OAuth2 for user-level auth. mTLS and user auth are complementary: mTLS secures the transport layer (workload-to-workload), user auth secures the application layer (user-to-application). Use both. |
| PERMISSIVE mode is acceptable for long-term use | PERMISSIVE accepts both mTLS and plaintext. In PERMISSIVE: an attacker's plaintext call is accepted (no cert required). PERMISSIVE is NOT zero-trust. It is ONLY for migration. Set a hard deadline: all namespaces STRICT within 30 days of Istio enablement. Kiali: verify all connections show green padlock before switching to STRICT. |
| Certificate rotation causes downtime | Istio rotates certificates every 24 hours WITHOUT connection interruption. Envoy: proactively fetches new cert 5 minutes before expiry. Active connections: continue using old cert (not interrupted). New connections: use new cert. The only risk: Istiod unavailable at cert expiry (cert expires with no replacement). Mitigation: Istiod HA (2+ replicas), extend cert lifetime to 48h as fallback. |

---

### 🚨 Failure Modes & Diagnosis

**PERMISSIVE left in production: security bypass**

**Symptom:**
Security audit: compliance failure. Penetration
tester bypassed service-to-service auth by calling
payment-service directly from an unauthorized
pod. Payment-service namespace: PeerAuthentication
in PERMISSIVE mode (set during Istio migration,
never flipped to STRICT).

**Root Cause:**
Istio PERMISSIVE: accepts plaintext HTTP. In
PERMISSIVE, AuthorizationPolicy principal checks
only apply to mTLS connections (plaintext has
no SPIFFE cert, principal = "unknown"). If
AuthorizationPolicy doesn't explicitly block
"unknown": any plaintext caller gets through.

**Diagnosis:**
```bash
# Check PeerAuthentication modes:
kubectl get peerauthentication --all-namespaces
# Look for: mode: PERMISSIVE in production ns

# Check Envoy mTLS stats:
kubectl exec -n payments payment-svc-pod \
  -c istio-proxy -- \
  curl -s localhost:15000/stats | \
  grep "ssl.handshake\|ssl_context"
# ssl.handshake > 0: mTLS connections exist
# If all connections are plaintext:
# ssl.handshake = 0 (no mTLS)
```

**Fix:**
```yaml
# 1. Verify all pods have Istio sidecar injected
kubectl get pods -n payments
# Each pod should show 2/2 READY (app + istio-proxy)

# 2. Flip to STRICT:
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: payments
spec:
  mtls:
    mode: STRICT
# 3. Monitor: watch for 503s (plaintext callers)
# 4. Fix remaining plaintext callers
```

---

### 🔗 Related Keywords

**What makes mTLS possible:**
- `Sidecar Pattern` - Envoy sidecar IS the mTLS
  implementation (cert + TLS handshake)

**The bigger security picture:**
- `Zero Trust Security in Microservices` - mTLS
  is the primary mechanism for zero trust networking
- `Microservices Security Patterns` - mTLS is
  one of several security patterns
- `Service Mesh Traffic Management` - same Istio
  setup that enables mTLS also manages traffic

---

### 📌 Quick Reference Card

```
+--------------------------------------------------+
| DEFINITION   | Both sides present X.509 cert;   |
|              | verifies workload identity        |
+--------------+-----------------------------------+
| ISTIO MODES  | PERMISSIVE (migration only);     |
|              | STRICT (production requirement)  |
+--------------+-----------------------------------+
| AUTO ROTATION| Istiod rotates certs every 24h  |
|              | without downtime (proactive)     |
+--------------+-----------------------------------+
| ONE-LINER    | "Cryptographic workload identity;|
|              |  compromised pod blocked by cert"|
+--------------------------------------------------+
```

**If you remember only 3 things:**
1. mTLS: BOTH services present certificates.
   Server knows WHO is calling. No cert = no
   access, even inside the cluster.
2. Istio automates everything: issues SPIFFE
   certs to each pod, enforces mTLS via Envoy
   sidecar, rotates certs every 24h. Zero app code.
3. PERMISSIVE = only for migration. STRICT =
   production. Add deny-all + AuthorizationPolicy
   for true zero-trust (not just mTLS alone).

**Interview one-liner:**
"mTLS in Microservices: both client and server
present X.509 (SPIFFE) certificates during TLS
handshake - each service verifies the WORKLOAD
IDENTITY of its caller, not just a network IP.
Istio auto-issues SPIFFE certs to every pod,
auto-rotates every 24h, enforces via Envoy
sidecar (zero app code changes). AuthorizationPolicy:
specify which SPIFFE principals can call which
endpoints. Key benefit: flat network problem
solved - compromised pod cannot reach unauthorized
services even on same cluster. PERMISSIVE mode:
migration only; STRICT: production requirement."

---

### 💡 The Surprising Truth

The hardest part of mTLS is NOT the TLS handshake
(Istio automates that completely). The hardest
part is writing CORRECT AuthorizationPolicies.
Common mistake: teams deploy Istio, enable STRICT
mTLS, and call it "zero trust". But: they never
write AuthorizationPolicies. Result: all services
are authenticated (have certs) but ANYTHING can
call ANYTHING (Istio's default when no policy
exists AND an identity is present: allow-all).
True zero trust: start with `deny-all` namespace
policies, then add explicit allow policies for
each service-to-service communication pair. In
a 30-service cluster: this means 30+ policy
resources. Most teams skip this. The difference:
"all services have identity documents" vs "only
authorized services can enter each room".

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN** Walk through the mTLS handshake
   step-by-step: what is exchanged, what is
   verified, how SPIFFE ID is extracted, how
   Istio uses it for authorization.
2. **CONFIGURE** Set up Istio mTLS for a 3-service
   cluster: PeerAuthentication STRICT, deny-all
   AuthorizationPolicy, then allow-list specific
   service-to-service calls. Verify using Kiali.
3. **MIGRATE** Plan the migration from PERMISSIVE
   to STRICT for 20 services: order of operations,
   how to detect plaintext callers, rollback plan
   if a flip causes 503s.
4. **DEBUG** Given: order-service gets 403 after
   STRICT was enabled. What 5 things do you check?
   Show the exact kubectl/curl commands.
5. **SCOPE** Explain the difference between mTLS
   (workload auth) and JWT Bearer tokens (user
   auth). For a payment endpoint: what does each
   layer verify, and why do you need both?

---

### 🧠 Think About This Before We Continue

**Q1.** Your platform has 30 services. Security
team mandates: all service-to-service communication
must use mTLS STRICT mode AND explicit
AuthorizationPolicies (deny-all + allow-list)
by end of quarter. 8 weeks, 3 engineers. Create
a project plan: migration sequence, how you test
each step, how you handle 5 legacy services
that don't support Istio injection, and the
rollback plan.

**Q2.** A security researcher reports: a compromised
order-service pod could obtain a valid SPIFFE
certificate (Istiod issues them automatically
to any pod in the cluster). Therefore mTLS doesn't
prevent lateral movement from a compromised pod
(it has a valid cert). How do you respond? Is
this valid? What additional controls mitigate?

**Q3.** Design monitoring and alerting for mTLS
in production: what Envoy metrics do you collect
(cert expiry, handshake failures, TLS errors),
what Prometheus alerts do you create (alert before
cert expires, alert on 403 spike indicating
potential attack), and what Grafana dashboard
panels give the security team real-time mTLS
health visibility?