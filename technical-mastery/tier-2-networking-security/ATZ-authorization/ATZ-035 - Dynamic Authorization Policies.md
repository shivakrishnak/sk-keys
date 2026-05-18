---
id: ATZ-035
title: "Dynamic Authorization Policies"
category: Authorization
tier: tier-2-networking-security
folder: ATZ-authorization
difficulty: ★★☆
depends_on: ATZ-015, ATZ-026, ATZ-030
used_by: ATZ-040, ATZ-046, ATZ-048, ATZ-050
related: ATZ-015, ATZ-026, ATZ-050
tags:
  - security
  - authorization
  - dynamic-policy
  - context-aware
  - intermediate
status: complete
version: 5
layout: default
parent: "Authorization"
grand_parent: "Technical Mastery"
nav_order: 35
permalink: /technical-mastery/authorization/dynamic-authorization-policies/
---

⚡ **TL;DR** - Dynamic authorization evaluates real-time context at
decision time: the user's current location, device health, time of
day, and risk signals - not just static roles. A CISO can access
payroll data from the corporate network but not from a coffee shop
Wi-Fi with an unmanaged device. The access control model changes
based on environmental context, not just identity. This is the
foundation of zero-trust access control: trust is continuously
evaluated, never assumed.

---

### 📊 Entry Metadata

| #035 | Category: Authorization | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | ATZ-015 ABAC, ATZ-026 PBAC, ATZ-030 Externalized Auth | |
| **Used by:** | ATZ-040, ATZ-046, ATZ-048, ATZ-050 | |
| **Related:** | ATZ-015 ABAC, ATZ-026 PBAC, ATZ-050 Enterprise Architecture | |

---

### 📘 Textbook Definition

Dynamic authorization policies evaluate real-time contextual
attributes at the moment of every access request, rather than
relying solely on pre-assigned static roles. Contextual
attributes include: network location (corporate vs. external),
device compliance state (MDM managed, patched), time (business
hours vs. off-hours), user risk score (anomaly detection signal),
recent authentication strength (MFA completed within the last
hour), and resource sensitivity. Dynamic policies can step up
authentication requirements (require MFA for sensitive operations),
restrict access to compliance-verified devices, or block access
during anomalous conditions.

---

### ⚙️ How It Works (Mechanism)

**Dynamic policy decision inputs:**

```
┌────────────────────────────────────────────────────────┐
│         Dynamic Authorization Context                  │
├────────────────────────────────────────────────────────┤
│                                                        │
│  Request context (evaluated at decision time):         │
│  {                                                     │
│    user:     {id: alice, roles: [FINANCE]},            │
│    resource: {id: payroll-2024, sensitivity: HIGH},    │
│    action:   "read",                                   │
│    context: {                                          │
│      ip:              "10.0.0.1",                      │
│      network:         "corporate-vpn",  ← dynamic     │
│      device_managed:  true,             ← dynamic     │
│      device_patched:  true,             ← dynamic     │
│      auth_age_minutes: 5,               ← dynamic     │
│      user_risk_score: 12,               ← dynamic     │
│      time_of_day:     "14:30 UTC",      ← dynamic     │
│      geo:             "US-NY"           ← dynamic     │
│    }                                                   │
│  }                                                     │
│                                                        │
│  Dynamic policy rules:                                 │
│  ALLOW: user.roles has FINANCE                         │
│    AND context.network in [corporate, vpn]             │
│    AND context.device_managed = true                   │
│    AND context.auth_age_minutes < 60                   │
│  STEP_UP_MFA: if auth_age_minutes > 60                 │
│  DENY: if user_risk_score > 50 (anomaly detected)      │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - Dynamic policy with OPA + real-time context**

```rego
package authz.dynamic

import future.keywords.if

default allow := false

# Deny high-risk users regardless of role
deny if {
    data.user_risk[input.user_id].score > 50
}

# High-sensitivity resources require strict context
allow if {
    not deny
    input.resource.sensitivity == "HIGH"
    input.user_roles[_] == "FINANCE"
    # Must be on corporate network or VPN
    input.context.network_type in ["corporate", "vpn"]
    # Device must be managed and compliant
    input.context.device_managed == true
    # MFA must be recent (within 1 hour)
    input.context.auth_age_minutes < 60
}

# Low-sensitivity resources: standard role check
allow if {
    not deny
    input.resource.sensitivity == "LOW"
    input.user_roles[_] in data.allowed_roles[input.action]
}

# Step-up authentication required (signal to PEP)
step_up_required if {
    input.resource.sensitivity == "HIGH"
    input.context.auth_age_minutes >= 60
}
```

---

*Authorization category: ATZ | Entry: ATZ-035 | v5.0*