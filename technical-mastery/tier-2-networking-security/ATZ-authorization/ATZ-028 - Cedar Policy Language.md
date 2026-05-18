---
id: ATZ-028
title: "Cedar Policy Language"
category: Authorization
tier: tier-2-networking-security
folder: ATZ-authorization
difficulty: ★★☆
depends_on: ATZ-026, ATZ-027
used_by: ATZ-030, ATZ-039, ATZ-058
related: ATZ-026, ATZ-027, ATZ-029
tags:
  - security
  - authorization
  - cedar
  - policy
  - aws
  - intermediate
status: complete
version: 5
layout: default
parent: "Authorization"
grand_parent: "Technical Mastery"
nav_order: 28
permalink: /technical-mastery/authorization/cedar-policy-language/
---

⚡ **TL;DR** - Cedar is AWS's open-source policy language for
authorization, designed for human readability and formal
verification. Cedar powers Amazon Verified Permissions (AVP)
and backs multiple AWS services (e.g., Amazon S3 Access Points,
AWS Verified Access). Unlike Rego (logic programming), Cedar
uses a structured `permit/forbid` syntax that is easier to read
and reason about. Its key differentiator: Cedar policies can be
formally verified for properties like "can user A ever reach
resource B?" - a guarantee Rego cannot easily provide.

---

### 📊 Entry Metadata

| #028 | Category: Authorization | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | ATZ-026 PBAC, ATZ-027 OPA | |
| **Used by:** | ATZ-030, ATZ-039, ATZ-058 | |
| **Related:** | ATZ-026 PBAC, ATZ-027 OPA, ATZ-029 Rego | |

---

### 📘 Textbook Definition

Cedar is an open-source policy language and evaluation engine
developed by AWS (open-sourced 2023). Cedar policies express
authorization rules using a `permit` / `forbid` syntax with
explicit principal, action, resource, and condition fields.
Cedar is used in Amazon Verified Permissions (a managed policy
engine service), AWS Verified Access (zero-trust network access),
and several AWS internal services. Cedar's design goals include:
human-readable policy syntax, formal verification (policies can
be analyzed statically for reachability and contradictions),
and performance at scale (evaluation is near-linear, not
exponential as with some XACML systems).

---

### ⚙️ How It Works (Mechanism)

**Cedar policy structure:**

```
┌────────────────────────────────────────────────────────┐
│         Cedar Policy Anatomy                           │
├────────────────────────────────────────────────────────┤
│                                                        │
│  permit(                                               │
│    principal == User::"alice",    ← who               │
│    action == Action::"read",      ← what action       │
│    resource == Document::"doc1"   ← on what           │
│  );                                                    │
│                                                        │
│  // Role-based: members of group can read              │
│  permit(                                               │
│    principal in Group::"editors", ← group membership  │
│    action in [Action::"read",                          │
│                Action::"write"],                       │
│    resource in Collection::"docs"                      │
│  ) when {                                              │
│    resource.sensitivity <= 2      ← condition          │
│  };                                                    │
│                                                        │
│  // Deny overrides permit                              │
│  forbid(                                               │
│    principal,                                          │
│    action,                                             │
│    resource == Document::"classified"                  │
│  ) unless {                                            │
│    principal.clearance >= 3                            │
│  };                                                    │
│                                                        │
│  Decision: DENY unless at least one permit applies     │
│  AND no forbid applies (default deny)                  │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - Amazon Verified Permissions authorization check (Java)**

```java
@Service
public class CedarAuthorizationService {

    private final VerifiedPermissionsClient avp;
    private final String policyStoreId;

    public boolean isAuthorized(String userId,
                                 String action,
                                 String resourceId) {
        IsAuthorizedRequest request = IsAuthorizedRequest.builder()
            .policyStoreId(policyStoreId)
            .principal(EntityIdentifier.builder()
                .entityType("App::User")
                .entityId(userId)
                .build())
            .action(ActionIdentifier.builder()
                .actionType("App::Action")
                .actionId(action)
                .build())
            .resource(EntityIdentifier.builder()
                .entityType("App::Document")
                .entityId(resourceId)
                .build())
            .build();

        IsAuthorizedResponse response = avp.isAuthorized(request);
        return Decision.ALLOW.equals(response.decision());
    }
}
```

**Example - Cedar vs Rego: readability comparison**

```
Cedar (explicit, human-readable):
  permit(
    principal in Group::"finance",
    action == Action::"read",
    resource in Collection::"finance-reports"
  ) when {
    resource.year >= 2020
  };

Rego equivalent (logic programming style):
  allow {
    data.groups[input.user].name == "finance"
    input.action == "read"
    data.collections[input.resource].name
      == "finance-reports"
    data.resources[input.resource].year >= 2020
  }

Cedar advantage: non-programmers (legal, compliance)
can read and verify Cedar policies directly.
Rego requires understanding logic programming concepts.
```

---

*Authorization category: ATZ | Entry: ATZ-028 | v5.0*