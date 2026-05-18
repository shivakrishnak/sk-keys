---
id: IAM-021
title: "Zero Trust Identity Architecture"
category: "Identity & Access Management"
tier: tier-2-networking-security
folder: IAM-iam-access
difficulty: ★★☆
depends_on: IAM-012, IAM-017, IAM-020
used_by: IAM-026, IAM-027
related: IAM-020, SEC-010, NET-025
tags:
  - iam
  - security
  - identity
  - architecture
  - intermediate
status: complete
version: 5
layout: default
parent: "Identity & Access Management"
grand_parent: "Technical Mastery"
nav_order: 21
permalink: /technical-mastery/iam/zero-trust-identity-architecture/
---

⚡ TL;DR - Zero Trust Identity Architecture replaces
the "trust the network, distrust the outside" model
with "never trust implicitly, always verify" applied
to every access request. Identity is the primary control
plane: every request is authenticated, authorized, and
continuously validated regardless of network location.
Core pillars: strong identity (MFA/phishing-resistant),
device trust (managed device + health check), least
privilege (JIT access), micro-segmentation (no lateral
movement), and continuous verification (risk scoring
every request). NIST SP 800-207 is the reference spec.

---

### 🔥 The Problem This Solves

Traditional network security assumed a trusted internal
network: inside the firewall = trusted; outside = untrusted.
This model fails in the modern threat landscape:

- Attackers who compromise internal devices have
  unrestricted lateral movement within the trusted network
- Remote work erases the inside/outside boundary
- SaaS applications sit outside "the perimeter" entirely
- Cloud environments have no perimeter in the traditional sense
- Phishing + credential theft gives attackers valid credentials
  that network controls cannot distinguish from legitimate users

The 2020 SolarWinds breach: attackers sat inside the
"trusted" Microsoft corporate network for months, moving
laterally using legitimate credentials. A network
perimeter provided no protection.

Zero Trust identity: assume breach is already in progress.
Verify every request as if it originates from an
untrusted network.

---

### 📘 Textbook Definition

Zero Trust is a security model (not a product) based on
the principle that no user, device, or network connection
should be trusted by default - even if inside the corporate
network. Trust must be established dynamically, per
request, based on verifiable signals.

**NIST SP 800-207 Zero Trust Tenets:**

1. All data sources and computing services are resources
2. All communication is secured regardless of network location
3. Access to resources is granted on a per-session basis
4. Access is determined by dynamic policy (multiple signals)
5. All devices are monitored for security posture
6. Authentication and authorization are dynamic and enforced
7. Organization collects data to improve security posture

**Zero Trust Identity pillars (Gartner/CISA):**

**Identity:** Strong authentication (MFA, phishing-resistant),
continuous identity verification, identity risk scoring.

**Device:** Device managed by MDM (Intune, Jamf), device
health check (patch level, disk encryption, EDR running),
device trust certificate, device posture as access signal.

**Network:** Micro-segmentation, zero implicit trust of
network location, BeyondCorp model (all resources treated
as internet-accessible regardless of network path).

**Application:** Least-privilege access per application
(not per network zone), application-level authentication
(not just network-level), JIT access for privileged actions.

**Data:** Data classification + access controls per
classification level, data loss prevention, encryption
at rest and in transit.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Zero Trust means "prove who you are, from what device,
and why you need access" for EVERY request -
not just the first login.

**One analogy:**
> Airport security vs. an office building:
>
> **Traditional model (office building):**
> - Show ID once at the front desk (authenticate)
> - Receive building badge (establish session trust)
> - Move freely to any floor, any room, indefinitely
>
> **Zero Trust model (airport terminal security):**
> - Show ID + boarding pass at the entrance (authenticate)
> - Show boarding pass again at every gate (re-verify)
> - Your gate checks your destination + seat (authorize)
> - Random security checks anywhere (continuous verify)
> - Cannot enter without boarding pass at each checkpoint
> - Different gates have different security requirements

**One insight:**
Zero Trust does not mean zero convenience. It means
that trust is earned from verifiable signals at each
access decision, not assumed from network location or
a stale session cookie.

---

### 🔩 First Principles Explanation

**Why identity-centric is the right model:**

Network-centric security (firewall, VPN) controls
what path a packet takes. Identity-centric security
controls what a principal can do. An attacker with
stolen credentials bypasses network controls. An attacker
with a compromised device is inside the network. But
strong identity verification, device trust, and JIT
access significantly raise the bar even when the
attacker has one compromised component.

**The "continuous verification" component:**

Session tokens are typically long-lived (hours to days).
A stolen session token provides attacker access for
the full session lifetime. Continuous verification
re-evaluates trust signals throughout the session:
IP geolocation anomaly (impossible travel), device
health degradation (EDR detects malware after session
start), user behavior anomaly (querying data at 3am
from a new location). If risk score exceeds threshold:
step-up authentication required or session terminated.

**Zero Trust for internal services:**

Zero Trust is not only for user-to-application access.
Service-to-service calls inside a Kubernetes cluster
should also be zero-trust: each service has a workload
identity (SPIFFE SVID), mTLS is required between all
services, and authorization is per-service-account
(not per network namespace). This prevents lateral
movement when one service is compromised.

---

### 🧪 Thought Experiment

**BeyondCorp-style rollout for a 1000-person company:**

```
Current state:
  - Corporate VPN required for all internal apps
  - Once on VPN: trusted to reach all internal services
  - VPN credential = master key to everything internal

Target state: Zero Trust
  - No VPN required
  - Every app accessible from internet
  - Every request authenticated + device-checked at app layer

Migration plan:

Phase 1: Identity foundation
  - Enforce MFA for all accounts (TOTP minimum; FIDO2 target)
  - Deploy identity provider (Okta or Entra ID)
  - Implement SSO for all 50 internal apps

Phase 2: Device trust
  - Deploy MDM (Intune or Jamf) to all endpoints
  - Issue device health certificates
  - Configure conditional access: managed device required
    for production data access

Phase 3: Access Proxy
  - Deploy BeyondCorp/ZTA proxy (Cloudflare Access,
    Zscaler Private Access, or Google BeyondCorp Enterprise)
  - Route internal apps through proxy
  - Proxy evaluates: user identity + MFA + device trust
    + risk score for every request

Phase 4: App-layer authorization
  - Each app implements per-resource authz
    (not just authentication at the proxy)
  - JIT for privileged operations (admin panels,
    production DB access)

Phase 5: Micro-segmentation
  - Service-to-service mTLS (Istio or Envoy)
  - Remove VPN entirely
  - Monitor: lateral movement attempts, anomalous access

Measurement:
  - Mean time to detect lateral movement: reduced from
    days to minutes (no free lateral movement inside network)
  - MFA coverage: target 100% for all users
  - Device trust coverage: target 95%+ managed devices
```

---

### 🧠 Mental Model / Analogy

> Think of Zero Trust as a zero-credit banking system:
>
> **Traditional model (overdraft credit):**
> - You open an account once (login to network)
> - Bank extends ongoing trust: spend freely from any ATM
> - Credit remains until explicitly revoked
>
> **Zero Trust model (prepaid only):**
> - Every transaction requires explicit balance check
> - Spending limit is set per transaction category
>   (JIT/least privilege)
> - Suspicious pattern: transaction blocked until
>   identity re-verified (step-up auth)
> - No overdraft allowed: deny by default
> - Audit record for every transaction
>
> The bank does not trust that "you have a card"
> (network credential). It validates every purchase
> individually.

---

### 📶 Gradual Depth - Five Levels

**Level 1 (anyone):**
Zero Trust means the security system checks who you
are and what device you're using for every access
request - not just when you first log in. Being on
the office network does not automatically mean you
are trusted.

**Level 2 (junior developer):**
Zero Trust in practice for a developer: corporate
laptop must be enrolled in MDM (managed). Login to
apps requires MFA. Sensitive apps require step-up
auth (hardware key). Production access requires JIT
approval. No VPN means the same security controls
apply from home and from office.

**Level 3 (mid engineer):**
Conditional access policies in Entra ID (Azure AD):
rule = "access to GitHub Enterprise requires:
MFA verified within last 1 hour AND managed device
AND sign-in risk level = None." If any condition
fails: block access or require step-up. This is
per-session Zero Trust: continuous evaluation of
access conditions.

**Level 4 (senior/staff):**
Workload Zero Trust with SPIFFE/SPIRE in Kubernetes:
each pod gets an SPIFFE identity (e.g., spiffe://
cluster.local/ns/payments/sa/payment-service). mTLS
between all services: the payment service can call
the database service only if its SVID is in the database
service's allowed principals list. No pod can reach
the database service without a valid workload SVID.
Compromising one pod does not grant access to adjacent
services (lateral movement blocked at the service layer).

**Level 5 (distinguished):**
Continuous Adaptive Risk and Trust Assessment (CARTA)
- Gartner's extension of Zero Trust: trust scores are
continuously computed from behavioral signals:
user behavior analytics (UEBA), device posture telemetry,
network flow analysis, and application-level telemetry.
A user's trust score degrades if: anomalous API query
patterns, accessing data from a new country, device
EDR detecting a new process. Low trust score triggers
step-up MFA or session termination without waiting for
an access denial event. This is proactive identity
security, not reactive.

---

### ⚙️ How It Works (Mechanism)

```
Zero Trust Access Decision Flow:

Request: alice@company.com from device
         accessing app: payments-dashboard

Policy Engine evaluation:
  1. Identity: authenticate alice
     - SSO token present? Yes
     - MFA completed? Yes (TOTP 15 min ago)
     - Identity risk score: Low (normal location,
       normal time, no recent password change)

  2. Device: check device posture
     - Device managed by MDM? Yes (Intune enrolled)
     - Disk encryption: Enabled
     - EDR (CrowdStrike): Running, no active alerts
     - OS patch level: Current (last patch: 3 days ago)
     - Device trust score: High

  3. Network: check access path
     - From: 203.0.113.50 (corporate residential IP pool)
     - TLS: Verified
     - Network risk: Low

  4. Application: check request context
     - Resource: /admin/refund-processor
     - Resource sensitivity: HIGH (requires JIT approval)
     - JIT approval status: Not present
     -> Deny: request JIT approval before access
        (redirect to approval workflow)

  5. Alternative (lower-sensitivity resource):
     - Resource: /dashboard/reports
     - Resource sensitivity: MEDIUM
     - All signals: Low risk
     -> Allow + log: {user, device, time, resource}

  6. Continuous monitoring during session:
     - IP change detected after 30 min:
       New IP: 185.220.101.x (Tor exit node)
     -> Immediate session termination
        Force re-authentication

Google BeyondCorp Access Proxy (simplified):
  Client -> BeyondCorp Proxy -> Internal App
  At proxy: evaluate {user identity, device cert, policy}
  Pass/block before proxying to internal app
  Internal app has no public IP - not accessible directly
```

---

### ⚖️ Comparison Table

| Aspect | Traditional VPN | Zero Trust (BeyondCorp) |
|:---|:---|:---|
| Trust model | Network location trusted | Identity + device + context verified |
| Lateral movement | Free (once on VPN) | Blocked (per-resource authz) |
| Remote work | VPN required | No VPN; same security everywhere |
| Granularity | Network-level | Application/resource-level |
| Session duration | VPN session (hours/days) | Per-request evaluation |
| Insider threat | VPN = trusted, minimal control | Continuous behavioral monitoring |
| Cloud native | Poor (tunnel all traffic) | Native (identity-centric) |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| "Zero Trust is a product you buy" | Zero Trust is an architecture and security model, not a product. ZTNA products (Cloudflare Access, Zscaler, Palo Alto Prisma) are tools that implement parts of Zero Trust. |
| "Zero Trust means zero trust of employees" | Zero Trust means zero implicit trust based on network location. Trust is still extended to employees - but it must be earned from verifiable signals per request. |
| "Zero Trust is only for network security" | Identity, device, application, and data are all Zero Trust pillars. Network is one layer. A company can be Zero Trust on identity (MFA+JIT) without being Zero Trust on network. |
| "VPN + MFA = Zero Trust" | VPN + MFA is better than VPN alone, but it is not Zero Trust. VPN still grants broad network access after authentication. Zero Trust requires per-resource authorization with continuous verification. |

---

### 🚨 Failure Modes & Diagnosis

**Device trust check blocking legitimate users**

```bash
# User reports: cannot access internal app after OS update
# Likely: device compliance policy failing post-update

# Intune: check device compliance status
# Entra ID admin portal: Devices -> find device
# Check compliance policies: which rule is failing

# Common after OS updates:
# - New OS version not yet in approved list
# - Security baseline check temporarily failing
#   (settings reset by OS update, re-applied by Intune)

# Immediate fix: manual compliance exception (1 hour)
# Root cause: update Intune approved OS version list
# Prevent: test OS updates on a canary device pool first
```

**Impossible travel false positive blocking executive**

```bash
# CEO logged in from London, then from New York 2h later
# (used a VPN to appear in New York)
# Zero Trust: impossible travel alert -> session blocked

# Okta / Entra ID: check sign-in logs
# London signin: 203.0.113.10 -> New York: 198.51.100.20
# 2 hours between locations: physically impossible

# Resolution:
# If legitimate: executive traveling + VPN usage
# 1. Confirm with user via out-of-band channel (call/text)
# 2. Allow session + add VPN IP to "trusted locations"
# 3. Coach user: disable VPN during SSO sign-in

# Root cause: VPN changing apparent location during travel
# Policy fix: add corporate VPN exit IPs to trusted named
#             locations to reduce false positives
```

---

### 🔗 Related Keywords

**Prerequisites:**
- `IAM-012` - Principle of Least Privilege
- `IAM-017` - Identity Attack Vectors: the threat model
- `IAM-020` - Just-in-Time Access: core ZT pattern

**Builds On This:**
- `IAM-026` - Enterprise IAM Architecture
- `IAM-027` - IAM Platform Design at Scale

**Related:**
- `SEC-010` - Defense in Depth: ZT as defense layer
- `NET-025` - Micro-segmentation: ZT network layer

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────┐
│ ZERO TRUST IDENTITY - MATURITY LADDER               │
├─────────┬────────────────────────────────────────────┤
│ Level 1 │ MFA enforced for all users                 │
│         │ (basic identity assurance)                 │
├─────────┼────────────────────────────────────────────┤
│ Level 2 │ MFA + SSO + device management              │
│         │ (managed device required for access)       │
├─────────┼────────────────────────────────────────────┤
│ Level 3 │ Conditional access policies                │
│         │ (per-app: identity + device + risk)        │
├─────────┼────────────────────────────────────────────┤
│ Level 4 │ JIT access + session monitoring            │
│         │ (no standing privilege)                    │
├─────────┼────────────────────────────────────────────┤
│ Level 5 │ Continuous verification + UEBA             │
│         │ + workload identity (SPIFFE)               │
└─────────┴────────────────────────────────────────────┘
```

**Interview one-liner:**
"Zero Trust Identity Architecture applies 'never trust,
always verify' to every access request regardless of
network location. Identity is the primary control plane:
strong MFA, device trust, JIT access, per-resource
authorization, and continuous behavioral verification.
NIST SP 800-207 is the reference. BeyondCorp is Google's
production implementation."

---

### 💎 Transferable Wisdom

Zero Trust Identity is the security application of
a deep systems principle: eliminate global mutable
state. In software, global mutable state is a bug
magnet (any code can modify it, non-deterministic
behavior). In security, global session trust is a
vulnerability (any compromised component has session
trust, non-deterministic access). The Zero Trust
equivalent: per-request access decisions replace
persistent session trust. Each decision is local,
explicit, and based on current state - not inherited
from a past authentication event. This is safer
(no stale trust), more auditable (every decision
is logged), and more composable (decisions can
incorporate new signals).

---

### ✅ Mastery Checklist

1. **DIFFERENTIATE** Explain the specific security
   gaps in a VPN + MFA model that Zero Trust Identity
   Architecture addresses. Give a concrete attack
   scenario that VPN + MFA fails against but Zero Trust
   would contain.

2. **DESIGN** A Zero Trust access policy for a payments
   processing application. Define the specific identity
   signals, device trust requirements, and continuous
   verification rules for: regular employee read access,
   engineer write access, and admin break-glass access.

3. **EVALUATE** A startup is building their first
   Zero Trust implementation with 100 employees. Which
   two Zero Trust pillars would you implement first and
   why? What measurable security outcomes would you
   use to validate the investment?

---

*Identity & Access Management | IAM-021 | v5.0*