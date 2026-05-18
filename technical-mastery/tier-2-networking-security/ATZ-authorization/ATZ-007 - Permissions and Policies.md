---
id: ATZ-007
title: "Permissions and Policies"
category: Authorization
tier: tier-2-networking-security
folder: ATZ-authorization
difficulty: ★☆☆
depends_on: ATZ-003, ATZ-006
used_by: ATZ-008, ATZ-009, ATZ-013, ATZ-015, ATZ-026
related: ATZ-006, ATZ-008, ATZ-009
tags:
  - security
  - authorization
  - permissions
  - policies
  - foundational
status: complete
version: 5
layout: default
parent: "Authorization"
grand_parent: "Technical Mastery"
nav_order: 7
permalink: /technical-mastery/authorization/permissions-and-policies/
---

⚡ **TL;DR** - A permission is a specific allowed operation on a
specific resource (e.g., `orders:read`). A policy is a collection
of permission rules with conditions - it specifies who can do what,
to which resources, under what conditions. Permissions are atoms;
policies are molecules. Understanding this distinction is essential
for reading AWS IAM, GCP IAM, OPA, and any modern authorization
framework.

---

### 📊 Entry Metadata

| #007 | Category: Authorization | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | ATZ-003, ATZ-006 | |
| **Used by:** | ATZ-008, ATZ-009, ATZ-013, ATZ-015, ATZ-026 | |
| **Related:** | ATZ-006 RBAC, ATZ-008 Allow/Deny, ATZ-009 Policy Types | |

---

### 📘 Textbook Definition

A permission is an authorization tuple: (subject, action,
resource) - defining what a subject is allowed to do to a
resource. A policy is a document containing one or more
permission rules, optionally with conditions (time-of-day,
IP range, MFA status, resource tags) that must be satisfied
for the permission to apply. Policies are the unit of
administration: they are created, versioned, attached, and
audited as complete documents rather than individual
permission bits.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Permission = one rule (do this thing); policy = a set of
rules about who can do what under which conditions.

**One analogy:**
> A rulebook for an apartment building. A single rule is:
> "Residents may use the gym between 6 AM and 10 PM."
> That is one permission. The full rulebook (all rules for
> all residents and staff, all facilities, all conditions)
> is the policy. You manage the rulebook as a whole document,
> not one rule at a time.

---

### ⚙️ How It Works (Mechanism)

**Permission structure:**

```
┌─────────────────────────────────────────────────────┐
│        Permission and Policy Anatomy                │
├─────────────────────────────────────────────────────┤
│                                                     │
│  PERMISSION (one rule):                             │
│    Principal: Alice (who)                           │
│    Action:    orders:read (what)                    │
│    Resource:  /orders/* (on what)                   │
│    Effect:    Allow                                 │
│                                                     │
│  POLICY (collection of rules + conditions):         │
│    Rule 1: Allow Alice to read orders               │
│    Rule 2: Allow Alice to create orders             │
│             if MFA_verified = true                  │
│    Rule 3: Deny Alice to delete orders              │
│             (explicit deny; overrides any Allow)    │
│                                                     │
│  POLICY ATTACHMENT:                                 │
│    Policy attached to: role EDITOR                  │
│    → all EDITOR users inherit these rules           │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**AWS IAM policy structure:**

| Field | Meaning |
|---|---|
| `Effect` | Allow or Deny |
| `Action` | Operation(s): `s3:GetObject`, `ec2:*` |
| `Resource` | ARN of resource(s) |
| `Condition` | Optional: time, IP, tags, MFA |
| `Principal` | Who (in resource policies only) |

---

### 💻 Code Examples

**Example - AWS IAM policy anatomy**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowReadOrders",
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:Query",
        "dynamodb:Scan"
      ],
      "Resource": "arn:aws:dynamodb:us-east-1:123:table/orders",
      "Condition": {
        "StringEquals": {
          "dynamodb:LeadingKeys": ["${aws:userid}"]
        }
      }
    },
    {
      "Sid": "DenyDeleteAlways",
      "Effect": "Deny",
      "Action": "dynamodb:DeleteItem",
      "Resource": "*"
    }
  ]
}
```

**Example - BAD vs GOOD: action granularity**

```json
// BAD: wildcard actions on all resources
{
  "Effect": "Allow",
  "Action": "dynamodb:*",
  "Resource": "*"
}
// Grants: CreateTable, DeleteTable, ExportTableToPointInTime,
// PurchaseReservedCapacityOfferings, and 60+ more actions
// Most applications need only 4-5 DynamoDB actions

// GOOD: specific actions only, specific resource
{
  "Effect": "Allow",
  "Action": [
    "dynamodb:GetItem",
    "dynamodb:PutItem",
    "dynamodb:UpdateItem",
    "dynamodb:Query"
  ],
  "Resource": "arn:aws:dynamodb:us-east-1:123:table/orders"
}
```

**Example - Application permission definition**

```java
// Spring Security method security with SpEL permissions
@Service
public class OrderService {

    @PreAuthorize(
        "hasPermission(#orderId, 'Order', 'read')")
    public Order getOrder(Long orderId) {
        return orderRepo.findById(orderId).orElseThrow();
    }

    @PreAuthorize(
        "hasPermission(#order, 'create') " +
        "&& @mfaService.isVerified(authentication)")
    public Order createOrder(OrderDto order) {
        return orderRepo.save(order.toEntity());
    }
}

// Permission evaluator wired to policy engine
@Component
public class OrderPermissionEvaluator {
    public boolean hasPermission(
            Authentication auth, Object targetId,
            String targetType, Object permission) {
        // Evaluate against policy: check role, ownership,
        // org membership, resource attributes
        return policyEngine.evaluate(
            auth.getName(), permission.toString(),
            targetType, targetId);
    }
}
```

---

### ⚠️ Common Failure Modes

**Permissions checked in application but not at DB:**

```
Symptom:
  API returns 403 for unauthorized users. But: direct database
  access (DB client, read replica) has no permission checks.
  An attacker with DB credentials reads all data regardless
  of application-level permissions.

Fix: Enforce at both layers:
  - Application layer: permission checks (speed, context)
  - Database layer: row-level security, column-level grants
    (defense in depth; DB access without application does
     not bypass the policy)
```

---

*Authorization category: ATZ | Entry: ATZ-007 | v5.0*