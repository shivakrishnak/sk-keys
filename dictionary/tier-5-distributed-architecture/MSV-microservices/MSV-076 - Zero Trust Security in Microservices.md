---
id: MSV-076
title: Zero Trust Security in Microservices
category: Microservices
tier: tier-5-distributed-architecture
folder: MSV-microservices
difficulty: ★★★
depends_on: MSV-075, MSV-077, MSV-020
used_by: MSV-075
related: MSV-075, MSV-077, MSV-078, MSV-010, MSV-020, MSV-065
tags:
  - microservices
  - security
  - deep-dive
  - architecture
status: complete
version: 4
layout: default
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 76
permalink: /microservices/zero-trust-security-in-microservices/
---

# MSV-076 - Zero Trust Security in Microservices

⚡ TL;DR - Zero Trust in Microservices: "Never
trust, always verify." Discard the perimeter
security model ("everything inside the cluster
is trusted"). Replace with: every request is
authenticated (mTLS for workload identity, JWT
for user identity) + authorized (RBAC per resource)
+ audited (access logs, distributed tracing).
Five pillars: (1) workload identity (mTLS/SPIFFE);
(2) least-privilege authorization (AuthorizationPolicy);
(3) network segmentation (NetworkPolicy);
(4) encrypted traffic (mTLS end-to-end);
(5) continuous verification (OPA, admission
controllers). Implementation: Istio (mTLS +
AuthzPolicy) + OPA/Gatekeeper (policy as code)
+ Vault (secrets, never env vars).

| #076 | Category: Microservices | Difficulty: ★★★☆ |
|:---|:---|:---|
| **Depends on:** | mTLS in Microservices, Microservices Security Patterns, Service Mesh | |
| **Used by:** | mTLS in Microservices | |
| **Related:** | mTLS in Microservices, Microservices Security Patterns, Service Mesh Traffic Management, API Gateway, Service Mesh, OpenTelemetry in Microservices | |

---

### 🔥 The Problem This Solves

**PERIMETER SECURITY IS DEAD IN MICROSERVICES:**
Traditional security model: "castle and moat".
Fire wall protects the perimeter. Inside: trusted.
30 microservices inside the perimeter: once an
attacker breaches the perimeter (compromised pod,
SSRF, supply chain attack), they can reach EVERYTHING
inside. Zero Trust: assumes breach ALWAYS. Every
service-to-service call: verified independently.
Every API call: authenticated and authorized.
Breach: contained to what the compromised service
is explicitly authorized to access.

---

### 📘 Textbook Definition

**Zero Trust Security in Microservices** is a
security architecture model based on the principle
"never trust, always verify" - first articulated
by John Kindervag at Forrester Research (2010)
and formalized in NIST SP 800-207 (2020). In
microservices, Zero Trust replaces the perimeter
model ("trust everything inside the cluster")
with continuous verification of every request.

Five pillars of Zero Trust in microservices:
(1) **Verify Identity** - every workload has a
cryptographic identity (SPIFFE/mTLS); every user
request carries a verified JWT/OAuth2 token;
(2) **Least-Privilege Access** - services only
access what they explicitly need (Istio
AuthorizationPolicy, Kubernetes RBAC, Vault
policies with narrow scope);
(3) **Assume Breach** - design as if the attacker
is already inside; segment microscopically
(Kubernetes NetworkPolicy to namespace level);
(4) **Encrypt Everything** - mTLS for service-
to-service; TLS for external; secrets in Vault
(never plaintext in env vars or ConfigMaps);
(5) **Continuous Verification** - OPA/Gatekeeper
for admission control (no deployment without
security labels); audit logs for all API calls;
alerts on anomalous access patterns.

Key technical controls: Istio (mTLS + AuthorizationPolicy),
OPA/Gatekeeper (policy as code for K8s admission),
Vault (dynamic secrets), SPIFFE/SPIRE (workload
identity), Kubernetes RBAC + NetworkPolicy.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Zero Trust: assume attackers are already inside.
Every request must prove identity AND be explicitly
authorized. No "trusted network" concept.

**One analogy:**
> Traditional security: a medieval castle. Thick
> walls (firewall), drawbridge (perimeter). Inside:
> anyone can walk anywhere. Once the drawbridge
> is breached: free movement everywhere. Zero Trust:
> a high-security government building. No perimeter
> assumption. EVERY door requires: badge scan (mTLS
> cert), purpose declaration (JWT scope), and logs
> every entry (audit). Even an employee who already
> got past the front door: cannot enter a classified
> room without specific clearance. Breach of one
> room: cannot spread to other rooms.

**One insight:**
Zero Trust is not a product you buy; it's a
property you achieve by layering controls. The
implementations: mTLS (who are you?), AuthorizationPolicy
(what can you do?), NetworkPolicy (what can you
reach at all?), Vault (what secrets do you get?),
OPA (what deployments are allowed?). No single
tool implements Zero Trust; the combination of
all layers achieves it.

---

### 🔩 First Principles Explanation

**ZERO TRUST CONTROL LAYERS:**

```
LAYER 1: NETWORK LAYER (Kubernetes NetworkPolicy)
  Who can connect to whom at TCP level
  
  Example:
  apiVersion: networking.k8s.io/v1
  kind: NetworkPolicy
  metadata:
    name: payment-network-policy
    namespace: payments
  spec:
    podSelector:
      matchLabels:
        app: payment-service
    policyTypes: [Ingress, Egress]
    ingress:
    - from:
      - namespaceSelector:
          matchLabels:
            name: orders  # Only orders ns allowed
      - namespaceSelector:
          matchLabels:
            name: fraud   # Only fraud ns allowed
    egress:
    - to:
      - namespaceSelector:
          matchLabels:
            name: databases  # DB namespace only
      ports:
      - port: 5432  # PostgreSQL only
  # All other ingress/egress: DENIED at TCP level
  # Even if Istio AuthzPolicy would allow it:
  # NetworkPolicy blocks first

LAYER 2: TRANSPORT LAYER (Istio mTLS)
  Who am I? (workload identity via SPIFFE certs)
  PeerAuthentication STRICT: no plaintext
  Envoy: verifies cert on every request

LAYER 3: APPLICATION LAYER (Istio AuthorizationPolicy)
  What can you do? (verb + resource)
  Deny-all default + allow-list
  Granularity: per method + path

LAYER 4: USER/APPLICATION LAYER (JWT/RBAC)
  Who is the user? (JWT in Authorization header)
  What can this user do? (RBAC roles)
  Istio RequestAuthentication + OPA rules

LAYER 5: SECRETS LAYER (HashiCorp Vault)
  What credentials does this service get?
  Dynamic short-lived secrets
  No plaintext secrets in env vars
  No secrets in ConfigMaps or K8s Secrets (base64)
  Vault Agent: injects credentials as files
  TTL: 1 hour (auto-rotation)
  Breach: attacker has credentials for max 1 hour
```

---

### 🧪 Thought Experiment

**SUPPLY CHAIN ATTACK: ZERO TRUST LIMITS BLAST RADIUS**

```
SCENARIO: Compromised npm package in
customer-service (Log4j-like vulnerability)
Attacker: executes code inside customer-service pod

WITHOUT ZERO TRUST (perimeter model):
  Attacker (inside customer-service):
    Calls payment-service: SUCCESS (no auth)
    Reads DB credentials from env var: SUCCESS
    Calls external C2 server: SUCCESS
    Lateral movement to all 29 other services: SUCCESS
  Impact: FULL CLUSTER COMPROMISE
  Recovery: replace entire cluster

WITH ZERO TRUST:
  Attacker (inside customer-service):
  
  Calls payment-service:
    NetworkPolicy: orders ns only -> DENIED (TCP block)
  
  Reads DB credentials:
    credentials not in env vars
    Vault Agent file: /vault/secrets/db (memory only)
    TTL: 1 hour (rotates automatically)
    Attacker: has customer-service DB creds only
    customer-service DB: only customer data (not payments)
  
  Calls external C2 server:
    Egress NetworkPolicy: only databases ns allowed
    External internet: DENIED
  
  Calls other internal services:
    customer-service SPIFFE identity:
      authorized for: customer-service -> orders ns only
    Any other service: 403 (AuthorizationPolicy)
  
  Impact: customer data access only
  (customer-service DB, nothing else)
  Recovery: rotate customer-service's Vault credentials
  Blast radius: CONTAINED
```

---

### 🧠 Mental Model / Analogy

> Zero Trust is like the principle of compartmentalization
> in nuclear submarines. Each compartment: sealed
> doors. A fire in compartment 3: cannot spread
> to compartment 4 automatically (doors seal).
> Every movement between compartments: requires
> explicit authorization and creates a log. A
> crew member who is supposed to be in compartment
> 3: cannot enter compartment 5 (the reactor room)
> even though they're already inside the submarine.
> Applied to microservices: a compromised pod in
> the customer namespace: sealed off from the
> payment namespace (NetworkPolicy). Even if it
> somehow reaches payment-service: it has no
> valid cert (mTLS blocks). Even if it somehow
> gets a cert: it's not in the allowed principals
> (AuthzPolicy blocks).

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Zero Trust: don't assume anything is safe inside
your network. Every service must prove who it is
before being allowed to do anything. An attacker
who gets inside can't freely roam.

**Level 2 - Basic implementation (junior developer):**
(1) Enable Istio, set PeerAuthentication STRICT
(mTLS everywhere); (2) Add deny-all AuthorizationPolicy
and explicit allow rules; (3) Add Kubernetes
NetworkPolicy per namespace; (4) Use Vault (or
K8s External Secrets) - never put secrets in
env vars or ConfigMaps.

**Level 3 - Policy as code (mid-level):**
OPA/Gatekeeper: admission controller that enforces
policies on every Kubernetes resource creation.
Examples: (1) All pods MUST have `istio-injection:
enabled` label (enforce sidecar injection); (2)
All Deployments MUST have resource limits (prevent
DoS); (3) No privileged containers allowed; (4)
All images must be from approved registries. OPA
policies: checked before any resource lands in
the cluster.

**Level 4 - Defense in depth (senior):**
Zero Trust is not a single wall but multiple
overlapping layers. Attack has to break through:
NetworkPolicy (L3/L4), mTLS (L4 + workload
identity), AuthorizationPolicy (L7 + RBAC), JWT
validation (user identity), OPA policy (admission
time), Vault TTL (time-limited credentials), audit
logs (detection + forensics). Breaking one layer
is not sufficient. This is defense in depth.

**Level 5 - Zero Trust maturity model (principal):**
Zero Trust Maturity Model (CISA 2023): 5 pillars
(Identity, Devices, Networks, Applications, Data)
at 3 maturity levels (Traditional, Advanced,
Optimal). "Traditional": manual mTLS config,
static secrets. "Advanced": automated cert
rotation, dynamic secrets (Vault), OPA policies.
"Optimal": continuous risk scoring (UEBA: user
behavior analytics), just-in-time access (Vault
dynamic secrets with 1-min TTL for sensitive
operations), all access decisions driven by real-
time risk score. Most organizations: target
"Advanced". "Optimal" for top-tier financial
services.

---

### ⚙️ How It Works (Mechanism)

```yaml
# ZERO TRUST IMPLEMENTATION CHECKLIST

# 1. WORKLOAD IDENTITY (mTLS)
# [See MSV-075 for full detail]
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: global-strict-mtls
  namespace: istio-system  # applies cluster-wide
spec:
  mtls:
    mode: STRICT
---
# 2. AUTHORIZATION (deny-all + allow-list)
# Pattern: set deny-all per namespace,
# then add allows for each service
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: deny-all
  namespace: payments  # repeat per namespace
spec: {}
---
# 3. USER IDENTITY (JWT validation)
apiVersion: security.istio.io/v1beta1
kind: RequestAuthentication
metadata:
  name: jwt-auth
  namespace: payments
spec:
  selector:
    matchLabels:
      app: payment-service
  jwtRules:
  - issuer: "https://auth.company.com"
    jwksUri: "https://auth.company.com/.well-known/jwks.json"
---
# 4. NETWORK SEGMENTATION (NetworkPolicy)
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: payment-isolation
  namespace: payments
spec:
  podSelector: {}
  policyTypes: [Ingress, Egress]
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: orders
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: data
    ports:
    - port: 5432  # DB only
---
# 5. OPA/GATEKEEPER: Admission control
# (enforce security requirements at deploy time)
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: RequireIstioSidecar
metadata:
  name: require-istio-injection
spec:
  match:
    kinds:
    - apiGroups: ["apps"]
      kinds: ["Deployment"]
  # Rejects any Deployment in a non-injected namespace
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
ZERO TRUST REQUEST VERIFICATION
(user triggers order payment)

User JWT -> API Gateway
  Gateway: validates JWT signature
  Gateway: checks scope (payments:write allowed?)
  Gateway: adds verified user info to header
  Gateway -> order-service (mTLS)

Order-service receives:
  Istio (Envoy): verifies gateway mTLS cert
  Istio: checks AuthzPolicy (gateway allowed?)
  App: validates JWT (user identity in request)
  App: checks user's RBAC (can Alice do this?)
  App -> payment-service

Payment-service receives:
  NetworkPolicy: is order-service namespace
    allowed to connect? YES (TCP passes)
  Istio: verifies order-service mTLS cert (TLS)
  Istio: checks AuthzPolicy
    (order-service allowed to POST /payments?)
  RequestAuthentication: validates user JWT
    (did this come from an authenticated user?)
  AuthzPolicy: JWT claim check
    (does user have payment permission?)
  App: processes payment
  App -> Vault (get payment gateway credentials)
    Vault: verifies payment-service K8s SA token
    Vault: checks policy (can payment-svc access
      payment-gateway secret path?)
    Vault: returns 1-hour TTL API key
  App: calls payment gateway with dynamic key

Audit log: every hop authenticated + logged
Breach containment: at each verification layer
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: perimeter model vs Zero Trust**

```java
// BAD: trusting network location
// "If it's calling from inside the cluster,
//  we trust it" - perimeter model
@PostMapping("/api/v1/payments")
public PaymentResponse pay(
        @RequestBody PaymentRequest req,
        HttpServletRequest httpReq) {
    // Check: is this from internal network?
    String callerIp = httpReq.getRemoteAddr();
    if (callerIp.startsWith("10.") ||
            callerIp.startsWith("172.")) {
        // "Internal IP = trusted"
        return process(req); // BAD
    }
    throw new UnauthorizedException();
    // Problem: IP spoofing, SSRF from any internal pod
}
```

```yaml
# GOOD: Zero Trust - verify identity, not network location
# 1. Enforce mTLS (verify workload identity)
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: payments
spec:
  mtls:
    mode: STRICT
---
# 2. Allow only specific callers (not just any internal IP)
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: payment-allow
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
        requestPrincipals:
        - "https://auth.company.com/*"  # valid JWT
    to:
    - operation:
        methods: ["POST"]
        paths: ["/api/v1/payments"]
    when:
    - key: request.auth.claims[scope]
      values: ["payments:write"]
# Payment controller: ZERO code changes
# Verified: (1) workload identity via SPIFFE cert
# Verified: (2) user identity via JWT issuer
# Verified: (3) JWT scope (payments:write)
# Network location (IP): completely irrelevant
```

---

### ⚖️ Comparison Table

| Security Model | Trust Assumption | Attack Blast Radius | Implementation Complexity |
|---|---|---|---|
| **Perimeter (Castle)** | Anything inside is trusted | Full cluster on breach | Low (firewall only) |
| **Network Policy only** | Inside namespace is trusted | Single namespace on breach | Medium |
| **mTLS only** | Valid cert = trusted | All cert-authorized services | Medium-High |
| **Zero Trust (all layers)** | Nothing trusted by default | Single service on breach | High |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Zero Trust means "trust nothing" (no trust ever) | Zero Trust means "never trust implicitly based on network location." It does NOT mean you never grant trust. It means: trust is EARNED through explicit verification (cert, JWT, policy check) and re-verified on every request. After verification: the request IS trusted (for the specific operation it's authorized for). Zero Trust is about HOW trust is granted (verification), not about having no trust at all. |
| mTLS is sufficient for Zero Trust | mTLS provides workload identity (Layer 4). It does NOT provide: user identity (need JWT), fine-grained authorization (need AuthorizationPolicy), network isolation (need NetworkPolicy), secret management (need Vault), or admission control (need OPA). mTLS is one layer of Zero Trust; Zero Trust requires all five pillars. A cluster with STRICT mTLS but no AuthorizationPolicies: all authenticated services can still call each other freely. |
| Zero Trust slows down every request significantly | The overhead is mostly at connection establishment (TLS handshake: ~1-2ms). Once the mTLS connection is established: subsequent requests on the same connection have near-zero overhead. JWT validation: done by Envoy (0.1-0.5ms per request). AuthorizationPolicy check: Envoy in-memory (~0.1ms). NetworkPolicy: kernel-level (~0.01ms). Total overhead at p99: 2-5ms per request. For services with p99 > 50ms: Zero Trust overhead is below 5% and acceptable. |

---

### 🚨 Failure Modes & Diagnosis

**Overly permissive AuthorizationPolicy bypasses Zero Trust**

**Symptom:**
Security audit: penetration tester from a compromised
pod (in any namespace) can reach payment-service
and execute payment-related operations. All Zero
Trust controls appear to be in place (STRICT mTLS,
AuthorizationPolicy exists).

**Root Cause:**
AuthorizationPolicy was set to allow all authenticated
workloads (any valid SPIFFE cert) rather than
specific SPIFFE principals:
```yaml
# WRONG: allows ANY authenticated workload
rules:
- from:
  - source:
      notPrincipals: []  # empty = anyone
```
Team intended: "only authenticated callers".
Effect: any pod with Istio injection (any service
in the cluster) can call payment-service. The
identity IS verified (mTLS), but authorization
is not restrictive enough.

**Fix:**
```yaml
# CORRECT: explicit allow-list
rules:
- from:
  - source:
      principals:
      - "cluster.local/ns/orders/sa/order-service"
      - "cluster.local/ns/fraud/sa/fraud-service"
# No wildcard; no empty list
# Only these TWO specific SPIFFE identities allowed
```

**Detection:**
```bash
# Check for overly-permissive policies:
kubectl get authorizationpolicy -A -o yaml | \
  grep -A5 "principals:"
# Look for: empty principals list
# or: wildcard "*" in principals
```

---

### 🔗 Related Keywords

**Core mechanism:**
- `mTLS in Microservices` - workload identity
  layer of Zero Trust

**The security toolkit:**
- `Microservices Security Patterns` - collection
  of all security patterns including Zero Trust
- `Service Mesh Traffic Management` - Istio
  traffic management + security controls

---

### 📌 Quick Reference Card

```
+--------------------------------------------------+
| PRINCIPLE    | Never trust, always verify;       |
|              | assume breach already occurred    |
+--------------+-----------------------------------+
| 5 PILLARS    | (1) Workload identity (mTLS)      |
|              | (2) Least privilege (AuthzPolicy) |
|              | (3) Network segment (NetPolicy)   |
|              | (4) Encrypted traffic (mTLS)      |
|              | (5) Continuous verify (OPA/audit) |
+--------------+-----------------------------------+
| BLAST RADIUS | Breach contained to 1 service     |
|              | (vs full cluster in perimeter)    |
+--------------+-----------------------------------+
| ONE-LINER    | "Every request verified by        |
|              |  identity, not network location" |
+--------------------------------------------------+
```

**If you remember only 3 things:**
1. Zero Trust: trust is earned per-request by
   cryptographic verification, never assumed from
   network location (IP = not identity).
2. Five layers: mTLS (workload ID), AuthzPolicy
   (what you can do), NetworkPolicy (what you
   can reach), Vault (secrets), OPA (admission).
3. mTLS alone is NOT Zero Trust. Without
   AuthorizationPolicies: all authenticated
   services can call each other freely.

**Interview one-liner:**
"Zero Trust in Microservices: replace perimeter
security ('inside cluster = trusted') with
continuous per-request verification. Five pillars:
(1) workload identity via mTLS/SPIFFE - every
service has cryptographic identity; (2) least-
privilege AuthorizationPolicy - deny-all + explicit
allow-list; (3) NetworkPolicy - network segmentation;
(4) Vault - dynamic short-lived secrets, never
env vars; (5) OPA/Gatekeeper - policy as code
at admission time. Benefit: compromised pod
cannot do lateral movement (blast radius contained
to explicitly authorized operations only)."

---

### 💡 The Surprising Truth

The most common Zero Trust failure is NOT a
technical gap - it's a PROCESS gap: teams implement
Zero Trust controls for new services but legacy
services slowly accumulate "exceptions" to the
policies. After 2 years: 60% of the cluster has
proper Zero Trust, and 40% has exception NetworkPolicies
("this old service needs to call everything"),
wildcard AuthorizationPolicies ("we don't know
all the callers"), and secrets in ConfigMaps
("the legacy service can't read Vault files").
The attacker targets the legacy services (weakest
link). Zero Trust requires: a CULTURE of continuous
enforcement, not a one-time implementation project.
OPA/Gatekeeper: prevents NEW services from
excepting themselves. But: the 40% legacy exception
zones must be tracked and eliminated with
dedicated engineering time.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **AUDIT** Enumerate all Zero Trust controls
   for a Kubernetes cluster: what kubectl commands
   show the state of PeerAuthentication, AuthorizationPolicy,
   NetworkPolicy, and OPA constraints?
2. **THREAT MODEL** For a supply-chain attack
   on customer-service: trace the attacker's
   lateral movement with vs without Zero Trust
   controls. What does the attacker access in
   each scenario?
3. **FIX** Given the overly-permissive AuthzPolicy
   failure above: write the specific fix and
   explain how to detect this misconfiguration
   using kubectl.
4. **COST-BENEFIT** Your CTO asks: "Zero Trust
   will add 2-3ms to every request. Is it worth
   it?" Prepare a 5-minute executive explanation
   with concrete business risk reduction numbers.
5. **MATURITY** Assess your current organization
   against the CISA Zero Trust Maturity Model.
   For each of the 5 pillars: what is the current
   maturity level and what are the next 3 steps
   to advance?

---

### 🧠 Think About This Before We Continue

**Q1.** Your security team says: "We have Istio
with STRICT mTLS and deny-all AuthorizationPolicy
- we have Zero Trust." Your penetration tester
demonstrates they can still exfiltrate data.
How? (Hint: think about secrets, audit logs,
and admission control.) List 5 gaps that remain
after mTLS + AuthzPolicy alone.

**Q2.** You need to onboard a new team that is
building a payment fraud detection service. Design
the Zero Trust onboarding checklist for their
new namespace: what NetworkPolicies, PeerAuthentication,
AuthorizationPolicies, Vault policies, and OPA
constraints do they need before their service
goes to production?

**Q3.** Zero Trust requires continuous verification.
But service-to-service calls can be thousands
per second. Design the performance optimization
strategy: which verifications are done per-
connection (TLS handshake: once per connection),
which are per-request (JWT validation), and
which are pre-computed (policy evaluation cached
for N seconds)? At 10,000 RPS: what is the CPU
overhead of Zero Trust verification?