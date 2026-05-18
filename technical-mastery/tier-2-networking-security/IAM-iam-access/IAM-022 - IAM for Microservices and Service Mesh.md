---
id: IAM-022
title: "IAM for Microservices and Service Mesh"
category: "Identity & Access Management"
tier: tier-2-networking-security
folder: IAM-iam-access
difficulty: ★★☆
depends_on: IAM-006, IAM-015, IAM-020
used_by: IAM-026, IAM-027
related: IAM-021, OAU-015, NET-020
tags:
  - iam
  - security
  - microservices
  - service-mesh
  - intermediate
status: complete
version: 5
layout: default
parent: "Identity & Access Management"
grand_parent: "Technical Mastery"
nav_order: 22
permalink: /technical-mastery/iam/iam-for-microservices-and-service-mesh/
---

⚡ TL;DR - In microservice architectures, each service
needs its own identity (workload identity) for service-
to-service authentication and fine-grained authorization.
SPIFFE/SPIRE provides cryptographic workload identities
(SVIDs - X.509 certificates with TTL). Service meshes
(Istio, Linkerd) use these identities to enforce mTLS
between all services and apply authorization policies
(only payment-service can call database-service).
For external-to-service authorization, OAuth 2.0/JWT
Bearer tokens propagated through call chains carry
the end-user's identity and permission scopes.

---

### 🔥 The Problem This Solves

A monolithic application authenticates once at the
edge (API gateway) and has full access to its own
database internally. Microservices break this model:

- Service A calls Service B calls Service C
- Who is the caller of Service C? Service B? The original
  user who triggered the chain? Both?
- How does Service C authenticate that the request
  actually came from Service B and not an attacker
  inside the cluster?
- If Service B is compromised, can it call Service C
  with arbitrary permissions? Or does Service C enforce
  its own authorization?

Without microservice IAM: any service inside the
cluster can call any other service freely. A compromised
service = unrestricted lateral movement. With workload
identity + service mesh mTLS + authorization policies:
each service-to-service call is authenticated, and
each service enforces its own access control policy.

---

### 📘 Textbook Definition

**Workload Identity:** A cryptographic identity issued
to a workload (pod, container, VM, function) rather
than a human. Used for service-to-service authentication.
SPIFFE (Secure Production Identity Framework For Everyone)
is the standard; SPIRE is the reference implementation.

**SPIFFE SVID:** A SPIFFE Verifiable Identity Document.
An X.509 certificate (or JWT) with:
- Subject Alternative Name (SAN): spiffe://trust-domain/path
- Short TTL (typically 1 hour, auto-renewed)
- Issued by SPIRE workload API

**Service Mesh mTLS:** Mutual TLS (mTLS) authenticates
both client and server. In a service mesh, each sidecar
proxy (Envoy in Istio) presents the service's SVID
certificate. Both sides verify the other's SVID. This
proves identity cryptographically: Service A knows it
is talking to Service B (not an attacker).

**Authorization Policy:** After mTLS establishes identity,
service-level authorization decides whether the call
is allowed. Istio AuthorizationPolicy: "only
payment-service may call database-service on POST /tx."

**JWT Propagation:** End-user identity (from OAuth/OIDC)
is carried in JWT Bearer tokens in HTTP Authorization
headers. In a microservice call chain, the original
JWT is forwarded or a new internal token is minted
at each hop. Services validate the JWT to determine
the end-user's identity and permitted scopes.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Microservice IAM uses cryptographic workload identities
for service-to-service authentication (SPIFFE/mTLS)
and JWT tokens for end-user identity propagation
through service call chains.

**One analogy:**
> A hospital has patient wristbands and staff badges:
>
> **Patient wristband (JWT):** carries patient identity
> and consent through every department. Each department
> (service) reads the wristband to know who the patient
> is and what procedures are authorized.
>
> **Staff badge (SPIFFE SVID):** each staff member
> (service) has a badge proving their role. Before
> entering the pharmacy (database), the pharmacist
> (database service) checks: "Is this staff badge
> from our hospital trust domain? Is this staff role
> (service identity) authorized to access controlled
> substances (sensitive data)?"

**One insight:**
Human IAM has a single authentication event (login).
Service IAM has continuous authentication: every
service-to-service call is a fresh TLS handshake
with SVID verification. This is Zero Trust applied
to the service layer - not just the user layer.

---

### 🔩 First Principles Explanation

**Why static service API keys fail at scale:**

Traditional service-to-service auth: Service A has
a static API key. Service B accepts the key and allows
access. Problems:
- Keys are long-lived: key compromise = persistent breach
- Keys stored in environment variables or config maps:
  one misconfigured permissions = all keys exposed
- Key rotation is painful: must update every service
  that holds the key
- No automatic revocation on service termination

SPIFFE SVIDs solve this: certificates are short-lived
(1 hour), auto-renewed by SPIRE agent, tied to
workload identity (not a static secret), and
immediately revocable by removing the SPIRE
registration entry. No long-lived secrets.

**JWT propagation in call chains:**

When a user makes a request:
Edge -> Service A -> Service B -> Service C

Option 1: Pass-through JWT
Service A forwards the original JWT to Service B.
Service B forwards to Service C. Each validates the
same JWT. Simple but: if the original JWT is short-lived
and Service C is called much later, it may expire.

Option 2: Token exchange (RFC 8693)
Service A exchanges the user JWT for a new service-
specific token (different audience, possibly different
claims). More complex but allows each service to
issue tokens with appropriate lifetimes and scopes.

Option 3: Nested/inner JWT
Service A creates a new JWT with the user claims
plus a "caller" claim. Each hop adds context.
Used in some enterprise patterns.

---

### 🧪 Thought Experiment

**Compromised service lateral movement scenario:**

```
Without workload identity + authorization:
  payment-service has credential for db-service
  notification-service has no credential for db-service
  
  Attacker compromises notification-service:
  -> Attacker discovers db-service URL from env vars
  -> Attacker calls db-service directly (no authz!)
  -> Full database access: all customer payment data

With SPIFFE + Istio AuthorizationPolicy:
  db-service policy:
    allowedPrincipals: [
      "spiffe://cluster.local/ns/payments/sa/payment-svc"
    ]
    allowedPaths: ["/query", "/transaction"]
    allowedMethods: [GET, POST]

  Attacker compromises notification-service:
  -> Has SVID: spiffe://.../ns/notify/sa/notification-svc
  -> Calls db-service: mTLS handshake presents notification SVID
  -> Istio sidecar checks AuthorizationPolicy:
     notification-service NOT in allowedPrincipals
  -> Request DENIED (403)
  -> Lateral movement blocked at service boundary

  Alert fired: unauthorized service-to-service call
  Incident response: isolate notification-service pod
```

---

### 🧠 Mental Model / Analogy

> Microservice IAM is like a hospital security system
> with role-specific access cards:
>
> - Each department (service) has an RFID reader
> - Each staff member (service) has an access card
>   with their role encoded (SPIFFE SVID)
> - The pharmacy (database) only opens for pharmacists
>   (payment service)
> - If a janitor (notification service) tries to enter
>   the pharmacy: RFID reader rejects the card
> - Patient wristband (JWT): carried through all
>   departments; each department reads it to know
>   what procedures the patient is authorized for
> - Cards expire every hour and are auto-renewed
>   at the badge office (SPIRE)

---

### 📶 Gradual Depth - Five Levels

**Level 1 (anyone):**
Microservice IAM means each service has its own ID
card (workload identity) and proves who it is before
every inter-service call, and each service enforces
its own access rules.

**Level 2 (junior developer):**
For Kubernetes: annotate the service account with an
AWS IAM role ARN (IRSA) or GCP service account email.
The pod gets credentials injected automatically for
accessing cloud APIs. For service-to-service: if using
Istio, mTLS is enabled by default in strict mode - all
calls between pods are authenticated via SVID.

**Level 3 (mid engineer):**
Istio AuthorizationPolicy example: restrict database
service to only receive calls from payment-service:
```yaml
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: db-service-policy
  namespace: payments
spec:
  selector:
    matchLabels:
      app: database-service
  rules:
  - from:
    - source:
        principals:
        - cluster.local/ns/payments/sa/payment-service
    to:
    - operation:
        methods: ["POST"]
        paths: ["/query", "/transaction"]
```
Any other service trying to call database-service
on any other path or method is denied.

**Level 4 (senior/staff):**
Token exchange in microservice chains: the payment
gateway receives an OIDC JWT from the mobile client
(user: alice, scope: payment:write). Payment gateway
calls fraud detection service. Fraud service needs
to know the user is alice but should not receive
the original payment:write scoped token. Gateway
exchanges the token via STS (RFC 8693):
POST /token, grant_type=urn:ietf:params:oauth:grant-type:token-exchange,
requested_token_type=access_token, audience=fraud-service.
Fraud service receives a new token (scope: fraud:read,
audience: fraud-service). Each service gets minimum
necessary claims.

**Level 5 (distinguished):**
SPIFFE federation across clusters and organizations:
SPIFFE trust domains can federate (trust-domain-A
trusts trust-domain-B's CA). This enables mTLS across
Kubernetes clusters (multi-cluster service mesh) or
even across organizations (service mesh with a vendor's
API). SPIRE supports bundle federation endpoints
where each trust domain publishes its root certificate
bundle. Other domains poll the endpoint to refresh
trust. This enables zero-standing-secret
service-to-service auth across organization boundaries
without API keys or shared secrets.

---

### ⚙️ How It Works (Mechanism)

```
SPIFFE/SPIRE Workload Identity in Kubernetes:

1. SPIRE Server: runs in k8s (or external)
   Registers: "pods with label app=payment-service in
   namespace payments get SPIFFE ID:
   spiffe://cluster.local/ns/payments/sa/payment-service"

2. SPIRE Agent: DaemonSet on each k8s node
   Attests workload via k8s node attestation
   Issues SVID (X.509 cert) via Unix domain socket:
   /run/spire/sockets/agent.sock

3. Istio Pilot (control plane):
   Reads SVID from SPIRE agent via SDS (Secret Discovery)
   Distributes SVID to Envoy sidecar

4. Service-to-service call (payment -> database):
   Envoy (payment side): presents SVID cert in mTLS handshake
   Envoy (database side): validates cert:
     - Trust domain: cluster.local (trusted)
     - SVID SAN: .../payments/sa/payment-service
     - TTL valid (< 1 hour old)
   Envoy (database side): evaluates AuthorizationPolicy:
     - payment-service principal is allowed
     -> forward request to database service

5. SVID renewal (automatic):
   SPIRE agent renews SVID when TTL is 50% consumed
   No interruption to running services

JWT Bearer Token Propagation:
  Mobile App -> Edge Gateway -> Payment Service
                                  |
                                  JWT forwarded in header:
                                  Authorization: Bearer <jwt>
                                  |
                                  -> Fraud Detection Service
                                     (token exchange or forward)
                                  -> Database Service
                                     (workload auth only; no JWT needed)
```

---

### ⚖️ Comparison Table

| Approach | Auth Mechanism | Rotation | Complexity | Best For |
|:---|:---|:---|:---|:---|
| Static API keys | Bearer token | Manual | Low | Legacy systems |
| mTLS with cert bundle | X.509 cert | Manual rotation | Medium | Simple clusters |
| SPIFFE/SPIRE | X.509 SVID auto-rotated | Automatic (1h TTL) | High | K8s/cloud native |
| Service mesh (Istio) | mTLS + AuthzPolicy | Auto (via SPIRE/Citadel) | Medium-High | Polyglot microservices |
| JWT propagation | Bearer JWT | Per-token TTL | Low-Medium | User identity in chains |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| "mTLS is enough for microservice security" | mTLS authenticates the caller. Authorization (what the authenticated caller is allowed to do) must be separately enforced. mTLS + AuthorizationPolicy = both. |
| "JWT propagation to every service is safe" | Propagating a full-scope user JWT to every service is over-privilege. Use token exchange (RFC 8693) to issue minimal-scope tokens per service. |
| "SPIFFE/SPIRE is only for Kubernetes" | SPIFFE/SPIRE works for VMs, containers, serverless, and on-premises workloads. The K8s integration is the most mature, but the specification is universal. |
| "Istio mTLS is on by default" | Istio PERMISSIVE mode (default in some versions) allows both mTLS and plaintext. STRICT mode is required to enforce mTLS everywhere. Always set STRICT in production. |

---

### 🚨 Failure Modes & Diagnosis

**SVID expiry causing service call failure**

```bash
# Service starts returning TLS errors to callers
# "certificate has expired" in Envoy access log

# Check SVID TTL on the affected pod:
kubectl exec -n payments payment-service-pod -- \
  cat /run/spire/sockets/svid.pem | \
  openssl x509 -noout -dates
# notAfter: check if in the past

# SPIRE agent not renewing SVIDs:
kubectl logs -n spire \
  $(kubectl get pod -n spire -l app=spire-agent -o name \
    --field-selector spec.nodeName=$(kubectl get pod \
      -n payments payment-service-pod \
      -o jsonpath='{.spec.nodeName}'))
# Look for: failed to renew SVID, attestation errors

# Fix: restart SPIRE agent on the affected node
# Root cause: SPIRE agent unable to reach SPIRE server
```

**Istio AuthorizationPolicy blocking legitimate calls**

```bash
# Logs show: "RBAC: access denied" for inter-service call

# Check Istio access logs:
kubectl logs -n payments database-service-pod \
  -c istio-proxy | grep "RBAC" | tail -20

# Identify: source principal from the denied request
# Compare: the AuthorizationPolicy allowedPrincipals list

# Check the actual SVID principal of the calling service:
kubectl exec -n payments payment-service-pod \
  -c istio-proxy -- pilot-agent request GET /config_dump | \
  python3 -m json.tool | grep "spiffe"

# If principal format mismatch (e.g., trailing slash):
# Fix: update AuthorizationPolicy to match exact format
```

---

### 🔗 Related Keywords

**Prerequisites:**
- `IAM-006` - IAM Principals: service accounts and workload identity
- `IAM-015` - Cloud IAM: IRSA and workload identity
- `IAM-020` - JIT Access: SPIFFE SVIDs are JIT workload credentials

**Builds On This:**
- `IAM-026` - Enterprise IAM Architecture: microservice IAM at scale
- `IAM-027` - IAM Platform Design at Scale

**Related:**
- `IAM-021` - Zero Trust: service mesh as Zero Trust implementation
- `OAU-015` - OAuth Token Introspection: validating JWTs in services
- `NET-020` - Service Mesh Architecture

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────┐
│ MICROSERVICE IAM PATTERNS                            │
├────────────────────┬─────────────────────────────────┤
│ Service identity   │ SPIFFE SVID (X.509, TTL 1h)    │
│ (who is the caller)│ Issued by SPIRE; auto-renewed   │
├────────────────────┼─────────────────────────────────┤
│ Service auth       │ mTLS (Istio STRICT mode)        │
│ (prove identity)   │ Both sides verify SVID cert     │
├────────────────────┼─────────────────────────────────┤
│ Service authz      │ Istio AuthorizationPolicy       │
│ (is caller allowed)│ Per-service, per-path, per-method│
├────────────────────┼─────────────────────────────────┤
│ User identity      │ JWT Bearer token forwarded      │
│ (who is end user)  │ or token-exchanged per service  │
├────────────────────┼─────────────────────────────────┤
│ Cloud API identity │ IRSA (EKS) / Workload Identity  │
│ (cloud resources)  │ Federation (GKE/AKS)            │
└────────────────────┴─────────────────────────────────┘
```

**Interview one-liner:**
"Microservice IAM uses SPIFFE/SPIRE for workload identity
(short-lived X.509 SVIDs, auto-renewed), service mesh
mTLS (Istio STRICT) for service-to-service authentication,
Istio AuthorizationPolicy for per-service access control,
and JWT Bearer tokens forwarded through call chains for
end-user identity propagation."

---

### 💎 Transferable Wisdom

SPIFFE SVIDs demonstrate the principle that identity
should be cryptographically bound to the runtime
context, not distributed as a shared secret. The same
principle drives: SSH host certificates (identity bound
to server key, not shared known_hosts entries), client
TLS certificates (identity bound to key, not shared
password), and hardware security tokens (identity bound
to hardware device, not replicable credential). Wherever
you see a shared secret providing identity, ask: can
this be replaced with a cryptographic binding to
the runtime context? That replacement eliminates the
secret rotation problem and reduces the blast radius
of any single compromise.

---

### ✅ Mastery Checklist

1. **DESIGN** A payment microservice on Kubernetes
   needs to authenticate to a database service and
   an external fraud detection API. Describe the SPIFFE/
   SPIRE setup, the Istio AuthorizationPolicy, and how
   the end-user JWT flows through the call chain.

2. **CONFIGURE** Write an Istio AuthorizationPolicy
   that restricts a database service to only accept
   calls from payment-service (POST /transaction) and
   analytics-service (GET /reports). Deny all other
   access explicitly.

3. **DIAGNOSE** After a Kubernetes rolling deployment,
   new payment-service pods are getting TLS errors when
   calling database-service. Old pods work fine. Walk
   through the diagnosis to determine whether the issue
   is SVID rotation, SPIRE registration, or Istio policy.

---

*Identity & Access Management | IAM-022 | v5.0*