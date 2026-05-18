---
id: ATZ-053
title: "Policy-as-Code in CI/CD"
category: Authorization
tier: tier-2-networking-security
folder: ATZ-authorization
difficulty: ★★★
depends_on: ATZ-026, ATZ-027, ATZ-028, ATZ-029, ATZ-051
used_by: ATZ-054, ATZ-062
related: ATZ-027, ATZ-051, ATZ-054
tags:
  - security
  - authorization
  - policy-as-code
  - cicd
  - advanced
status: complete
version: 5
layout: default
parent: "Authorization"
grand_parent: "Technical Mastery"
nav_order: 53
permalink: /technical-mastery/authorization/policy-as-code-in-cicd/
---

⚡ **TL;DR** - Policy-as-Code (PaC) treats authorization policies
as code: they live in Git, are reviewed via pull requests, tested
automatically, versioned, and deployed via CI/CD. This gives
authorization policies the same engineering rigor as application
code: no policy change without a review, every policy change has
a test, and broken policies are caught before they reach production.
OPA with Rego is the dominant policy-as-code stack; Conftest and
`opa test` are the testing tools.

---

### 📊 Entry Metadata

| #053 | Category: Authorization | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | ATZ-026 PBAC, ATZ-027 OPA, ATZ-028 Cedar, ATZ-029 Rego, ATZ-051 Central vs Dist | |
| **Used by:** | ATZ-054, ATZ-062 | |
| **Related:** | ATZ-027 OPA, ATZ-051 Central vs Distributed, ATZ-054 Observability | |

---

### 📘 Textbook Definition

Policy-as-Code (PaC) is the practice of managing authorization
policies using software engineering tools and practices: version
control (Git), code review (pull requests), automated testing
(unit tests for every policy decision), packaging (bundles),
and continuous deployment (CI/CD pipeline that builds and
deploys policy bundles). PaC with OPA uses the Rego policy
language for human-readable, testable policies. Testing uses
`opa test` with `.rego` test files. Conftest extends this to
validate Kubernetes manifests, Terraform, Dockerfile, and other
infrastructure files against policy rules - shifting access
control enforcement left into the development workflow.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│         Policy-as-Code CI/CD Pipeline                  │
├────────────────────────────────────────────────────────┤
│                                                        │
│  GIT (policy repo):                                    │
│  policies/authz/allow.rego                             │
│  policies/authz/allow_test.rego                        │
│  policies/infra/k8s_security.rego (infra policies)     │
│  policies/infra/k8s_security_test.rego                 │
│                                                        │
│  CI PIPELINE (on PR merge):                            │
│  1. opa fmt --diff (format check)                      │
│  2. opa check policies/ (syntax validation)            │
│  3. opa test policies/ -v (unit tests, must all pass)  │
│  4. opa build -b policies/ -o bundle.tar.gz            │
│  5. Sign bundle (optional, for supply chain security)  │
│  6. Push bundle to bundle server                       │
│  7. Notify OPA agents: new bundle available            │
│                                                        │
│  OPA AGENTS:                                           │
│  - Pull new bundle within 30-60s                       │
│  - Validate bundle signature                           │
│  - Load into memory, start serving decisions           │
│                                                        │
│  ROLLBACK:                                             │
│  - Revert Git commit                                   │
│  - CI rebuilds and publishes previous bundle           │
│  - All agents revert within 30-60s                     │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - OPA policy with unit tests**

```rego
# policies/authz/allow.rego
package authz

default allow = false

# Allow read access for any authenticated user
allow {
    input.method == "GET"
    input.principal.authenticated == true
}

# Allow write access only for owners and admins
allow {
    input.method in ["POST", "PUT", "DELETE"]
    some role in input.principal.roles
    role in ["owner", "admin"]
}

# Deny access to deleted resources for non-admins
deny_deleted_to_non_admin {
    input.resource.status == "deleted"
    not "admin" in input.principal.roles
}

# Combined: allow only if no explicit deny
allow_final {
    allow
    not deny_deleted_to_non_admin
}
```

```rego
# policies/authz/allow_test.rego
package authz_test

import future.keywords.if

test_allow_get_authenticated if {
    allow with input as {
        "method": "GET",
        "principal": {"authenticated": true, "roles": []}
    }
}

test_deny_get_unauthenticated if {
    not allow with input as {
        "method": "GET",
        "principal": {"authenticated": false, "roles": []}
    }
}

test_allow_post_admin if {
    allow with input as {
        "method": "POST",
        "principal": {"authenticated": true,
                       "roles": ["admin"]}
    }
}

test_deny_post_viewer if {
    not allow with input as {
        "method": "POST",
        "principal": {"authenticated": true,
                       "roles": ["viewer"]}
    }
}
# Run: opa test policies/ -v
# All tests must pass before PR can merge
```

---

*Authorization category: ATZ | Entry: ATZ-053 | v5.0*