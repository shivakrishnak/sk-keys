---
id: ATZ-009
title: "Resource-Based vs Identity-Based Policies"
category: Authorization
tier: tier-2-networking-security
folder: ATZ-authorization
difficulty: ★☆☆
depends_on: ATZ-007, ATZ-008
used_by: ATZ-013, ATZ-019, ATZ-022, ATZ-033
related: ATZ-007, ATZ-008, ATZ-010
tags:
  - security
  - authorization
  - iam
  - policies
  - foundational
status: complete
version: 5
layout: default
parent: "Authorization"
grand_parent: "Technical Mastery"
nav_order: 9
permalink: /technical-mastery/authorization/resource-based-vs-identity-based-policies/
---

⚡ **TL;DR** - Identity-based policies are attached to a principal
(user, role, group) and say "this identity can do X." Resource-based
policies are attached to a resource and say "these identities can do
X to me." AWS IAM uses both. Understanding the difference determines
whether cross-account access, public access, or service delegation
is possible and how to configure it correctly.

---

### 📊 Entry Metadata

| #009 | Category: Authorization | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | ATZ-007, ATZ-008 | |
| **Used by:** | ATZ-013, ATZ-019, ATZ-022, ATZ-033 | |
| **Related:** | ATZ-007 Permissions, ATZ-008 Allow/Deny, ATZ-010 ACL | |

---

### 📘 Textbook Definition

Identity-based policies (also called principal-based or
subject-based policies) are attached to a security principal
and define what actions that principal may perform. Resource-based
policies are attached to a resource and define which principals
may perform which actions on that resource. Many systems support
both: a request must satisfy both the identity policy and the
resource policy for access to be granted (intersection semantics),
except for cross-account access where both policies must
independently grant permission.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Identity policy: "I am allowed to go there." Resource policy:
"Only these people are allowed to come here."

**One analogy:**
> Employee badge system. Your badge (identity policy) says
> what buildings you can enter. But the server room
> (resource policy) has a sign: "Authorized personnel only
> - must be on this list." You need both: your badge must
> permit server rooms AND you must be on the server room's
> list.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────────────┐
│     Identity-Based vs Resource-Based Policies       │
├─────────────────────────────────────────────────────┤
│                                                     │
│  IDENTITY-BASED POLICY (attached to principal):     │
│  {                                                  │
│    "Effect": "Allow",                               │
│    "Action": "s3:GetObject",                        │
│    "Resource": "arn:aws:s3:::my-bucket/*"           │
│  }                                                  │
│  Attached to: IAM role "app-server-role"            │
│  Means: this role can GET objects from my-bucket    │
│                                                     │
│  RESOURCE-BASED POLICY (attached to bucket):        │
│  {                                                  │
│    "Effect": "Allow",                               │
│    "Principal": {                                   │
│      "AWS": "arn:aws:iam::123:role/app-server-role" │
│    },                                               │
│    "Action": "s3:GetObject",                        │
│    "Resource": "arn:aws:s3:::my-bucket/*"           │
│  }                                                  │
│  Attached to: S3 bucket "my-bucket"                 │
│  Means: this bucket accepts GET from app-server-role│
│                                                     │
│  SAME-ACCOUNT: identity policy OR resource policy   │
│               is sufficient                         │
│  CROSS-ACCOUNT: BOTH policies must grant permission │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**Cross-account access - why both policies are needed:**

```
Account A (identity): "role-A can access bucket-B"
Account B (resource): "role-A is allowed in bucket-B"

Both must be present. Account A cannot unilaterally
grant access to Account B's resources. Account B must
also explicitly permit the cross-account principal.
This mutual grant prevents Account A from granting
itself access to any resource in any other account.
```

---

### 💻 Code Examples

**Example - S3 bucket policy (resource-based)**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::data-bucket/*",
      "Condition": {
        "ArnLike": {
          "aws:SourceArn":
            "arn:aws:lambda:us-east-1:123:function:processor"
        }
      }
    }
  ]
}
```

**Example - BAD vs GOOD: public access via resource policy**

```json
// BAD: resource policy with public principal
// This makes the entire S3 bucket publicly readable
{
  "Effect": "Allow",
  "Principal": "*",
  "Action": "s3:GetObject",
  "Resource": "arn:aws:s3:::sensitive-bucket/*"
}
// Principal: "*" = any entity, including unauthenticated
// anyone on the internet can GET objects from this bucket

// GOOD: specific principal only
{
  "Effect": "Allow",
  "Principal": {
    "AWS": "arn:aws:iam::123456789:role/data-processor"
  },
  "Action": "s3:GetObject",
  "Resource": "arn:aws:s3:::sensitive-bucket/*"
}
```

**Example - Application resource owner policy (custom)**

```java
// Application-level "resource-based" policy simulation
// Check if accessing user is either the owner OR an admin
@Service
public class DocumentAuthzService {

    public boolean canRead(User user, Document doc) {
        // Identity-based: is user an admin? (role check)
        if (user.hasRole("ADMIN")) return true;

        // Resource-based: is user the document owner?
        // (policy attached to the resource, not identity)
        if (doc.getOwnerId().equals(user.getId())) {
            return true;
        }

        // Resource-based: is user in the document's ACL?
        return doc.getSharedWith().contains(user.getId());
    }
}
```

---

### ⚠️ Common Failure Modes

**Resource policy grants access; identity policy missing:**

```
AWS same-account: resource policy alone is sufficient.
But in cross-account: access silently denied with no
clear error message (access denied, not "missing identity
policy" - the error message does not tell you which
policy is missing).

Debug:
  aws sts get-caller-identity  # confirm which account
  aws s3api get-bucket-policy --bucket my-bucket  # resource
  # Check identity policy in IAM console for the role
  # Both must grant the requested action for cross-account
```

---

*Authorization category: ATZ | Entry: ATZ-009 | v5.0*