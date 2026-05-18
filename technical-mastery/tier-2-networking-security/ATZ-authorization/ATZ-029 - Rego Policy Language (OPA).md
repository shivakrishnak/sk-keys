---
id: ATZ-029
title: "Rego Policy Language (OPA)"
category: Authorization
tier: tier-2-networking-security
folder: ATZ-authorization
difficulty: ★★☆
depends_on: ATZ-026, ATZ-027
used_by: ATZ-027, ATZ-030, ATZ-039, ATZ-053
related: ATZ-027, ATZ-028, ATZ-039
tags:
  - security
  - authorization
  - rego
  - opa
  - policy
  - intermediate
status: complete
version: 5
layout: default
parent: "Authorization"
grand_parent: "Technical Mastery"
nav_order: 29
permalink: /technical-mastery/authorization/rego-policy-language-opa/
---

⚡ **TL;DR** - Rego is the policy language for Open Policy Agent.
It is a declarative logic language: you describe conditions that
make a statement true, and OPA evaluates whether they hold given
the input and data. The most important concept to internalize:
Rego is not imperative - there are no if/else branches. You define
what is `allow = true` by expressing what conditions must hold.
Every condition on the same line is ANDed. Multiple `allow` rules
with different bodies are ORed. Forgetting this leads to policies
that are more permissive than intended.

---

### 📊 Entry Metadata

| #029 | Category: Authorization | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | ATZ-026 PBAC, ATZ-027 OPA | |
| **Used by:** | ATZ-027, ATZ-030, ATZ-039, ATZ-053 | |
| **Related:** | ATZ-027 OPA, ATZ-028 Cedar, ATZ-039 Policy Evaluation | |

---

### 📘 Textbook Definition

Rego is a declarative, logic-based query language used to write
policies for Open Policy Agent (OPA). Rego is inspired by Datalog
and evaluates policies as truth queries: given input and data, is
a particular output expression true? Rego policies consist of
rules (named boolean or structured expressions), which OPA
evaluates to produce authorization decisions. Key Rego semantics:
AND within a rule body (all conditions must hold), OR across
multiple rules with the same name, set/object comprehensions for
data transformation, and built-in functions for string manipulation,
time, JWT decoding, and cryptographic operations.

---

### ⚙️ How It Works (Mechanism)

**Rego evaluation model:**

```
┌────────────────────────────────────────────────────────┐
│            Rego Logic Model                            │
├────────────────────────────────────────────────────────┤
│                                                        │
│  Input:  {"user": "alice", "action": "read",           │
│            "resource": "doc-001"}                      │
│  Data:   {"roles": {"alice": ["editor"]},              │
│            "permissions": {"editor": ["read", "write"]}│
│           }                                            │
│                                                        │
│  Policy:                                               │
│  package authz                                         │
│                                                        │
│  allow {                                               │
│    user_role := data.roles[input.user][_]  ← get role  │
│    allowed := data.permissions[user_role]  ← get perms │
│    input.action == allowed[_]              ← match?   │
│  }                                                     │
│                                                        │
│  Evaluation:                                           │
│  alice's role = "editor"                               │
│  editor's permissions = ["read", "write"]              │
│  "read" in ["read", "write"] = true                    │
│  allow = true                                          │
│                                                        │
│  IMPORTANT: multiple allow rules = OR                  │
│  allow { condition1 }  ← if this is true...            │
│  allow { condition2 }  ← OR if this is true = allow   │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - Rego policies: common patterns**

```rego
package authz

import future.keywords.in
import future.keywords.if

# Default deny: unless allow matches, deny
default allow := false

# Allow: user is in owners of the resource
allow if {
    input.user in data.resources[input.resource].owners
}

# Allow: user's role has the required permission
allow if {
    some role in data.user_roles[input.user]
    input.action in data.role_permissions[role]
}

# Deny always overrides (separate forbid rule)
# If any forbid matches, result is deny even if allow=true
default forbid := false

forbid if {
    data.resources[input.resource].confidential == true
    not "security-officer" in data.user_roles[input.user]
}

# Final decision
final_decision := "allow" if {
    allow
    not forbid
}
final_decision := "deny" if {
    not allow
}
final_decision := "deny" if {
    forbid
}
```

**Example - BAD: accidentally permissive OR semantics**

```rego
# BAD: missing default deny
# If neither rule matches: OPA returns undefined (not false)
# Some clients treat undefined as "allow"
allow {
    input.user == "alice"
}
allow {
    input.action == "read"
}

# RISK: input.action == "read" makes allow true
# regardless of who the user is.
# ANY authenticated user can read because the second rule
# has no user constraint.

# GOOD: always add user constraint to every rule
default allow := false
allow {
    input.user == "alice"
    input.action == "read"   # AND (same rule = AND)
}
allow {
    # Separate rule = OR, but add user check
    input.user in data.admins
    input.action == "read"
}
```

---

*Authorization category: ATZ | Entry: ATZ-029 | v5.0*