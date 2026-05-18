---
id: ATZ-048
title: "Zero Trust Authorization Patterns"
category: Authorization
tier: tier-2-networking-security
folder: ATZ-authorization
difficulty: ★★★
depends_on: ATZ-015, ATZ-030, ATZ-040, ATZ-047
used_by: ATZ-049, ATZ-050, ATZ-053
related: ATZ-040, ATZ-049, ATZ-050
tags:
  - security
  - authorization
  - zero-trust
  - advanced
status: complete
version: 5
layout: default
parent: "Authorization"
grand_parent: "Technical Mastery"
nav_order: 48
permalink: /technical-mastery/authorization/zero-trust-authorization-patterns/
---

⚡ **TL;DR** - Zero Trust rejects the "trusted network perimeter"
assumption. Inside a zero trust architecture, every request -
even from internal services on the same subnet - is treated as
untrusted until explicitly authorized. Authorization in ZTA is
continuous (every request is evaluated, not just at login) and
uses all available context: user identity, device posture, network
location, resource sensitivity, and behavioral signals. The access
decision is: "at this moment, with this context, is this specific
action on this specific resource authorized?"

---

### 📊 Entry Metadata

| #048 | Category: Authorization | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | ATZ-015 ABAC, ATZ-030 Externalized Authz, ATZ-040 Distributed Authz, ATZ-047 Multi-Tenant | |
| **Used by:** | ATZ-049, ATZ-050, ATZ-053 | |
| **Related:** | ATZ-040 Distributed Authz, ATZ-049 Microservices Fleet, ATZ-050 Enterprise Authz | |

---

### 📘 Textbook Definition

Zero Trust Architecture (ZTA, NIST SP 800-207) eliminates the
implicit trust granted based on network location ("if it's
inside the firewall, trust it"). In ZTA, every access decision
requires explicit authorization based on multiple signals:
identity (who is the principal - user or service?), device
(is it managed and compliant?), network context (on-prem,
VPN, internet?), resource classification (public, internal,
confidential?), and behavioral context (is this unusual
activity for this principal?). Authorization decisions are
made by a Policy Decision Point (PDP) for every request and
are not cached indefinitely - risk signals can trigger
immediate re-evaluation.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│         Zero Trust Authorization Framework             │
├────────────────────────────────────────────────────────┤
│                                                        │
│  TRADITIONAL (perimeter model):                        │
│  Inside network -> trusted -> full access              │
│  VPN connected -> act like internal employee           │
│  One breach -> attacker has full lateral movement      │
│                                                        │
│  ZERO TRUST model:                                     │
│  Every request -> PDP evaluates:                       │
│  1. Identity: is JWT valid? which user/service?        │
│  2. Device: is device MDM-managed? posture compliant?  │
│  3. Location: on corp network, VPN, or internet?       │
│  4. Resource sensitivity: public / internal / secret   │
│  5. Action: read vs write vs admin                     │
│  6. Risk signals: anomaly score from risk engine       │
│                                                        │
│  Decision matrix:                                      │
│  High trust + low risk + low sensitivity = allow       │
│  Low trust + medium risk + high sensitivity = MFA step-up│
│  Any critical risk signal = deny + alert               │
│                                                        │
│  Session re-evaluation:                                │
│  Not just at login - re-evaluate on:                   │
│  - Access to higher-sensitivity resources              │
│  - Risk score increase mid-session                     │
│  - Device posture change (MDM compliance lapse)        │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - Zero Trust policy in OPA (Rego)**

```rego
# Zero trust authorization policy
# Evaluates: identity + device + resource sensitivity
package authz.zerotrust

default allow = false

# Allow if all conditions met
allow {
    valid_identity
    device_compliant
    sufficient_trust_for_resource
    not anomaly_detected
}

# Identity must be verified user or service
valid_identity {
    input.principal.type == "user"
    input.principal.verified == true
}

valid_identity {
    input.principal.type == "service"
    input.principal.spiffe_id != ""
}

# Device posture check
device_compliant {
    # For non-sensitive resources: any device
    input.resource.sensitivity == "public"
}

device_compliant {
    # For sensitive resources: must be MDM-managed
    input.resource.sensitivity != "public"
    input.device.mdm_managed == true
    input.device.os_patched == true
}

# Trust level must match resource sensitivity
sufficient_trust_for_resource {
    input.resource.sensitivity == "internal"
    input.principal.trust_level >= 50
}

sufficient_trust_for_resource {
    input.resource.sensitivity == "confidential"
    input.principal.trust_level >= 80
    input.principal.mfa_verified == true
}

# Anomaly detection integration
anomaly_detected {
    input.risk_score > 70
}
```

---

*Authorization category: ATZ | Entry: ATZ-048 | v5.0*