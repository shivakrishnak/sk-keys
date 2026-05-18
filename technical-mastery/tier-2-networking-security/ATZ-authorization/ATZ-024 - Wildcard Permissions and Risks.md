---
id: ATZ-024
title: "Wildcard Permissions and Risks"
category: Authorization
tier: tier-2-networking-security
folder: ATZ-authorization
difficulty: ★★☆
depends_on: ATZ-004, ATZ-007, ATZ-023
used_by: ATZ-041, ATZ-042, ATZ-043
related: ATZ-007, ATZ-023, ATZ-041
tags:
  - security
  - authorization
  - wildcard
  - least-privilege
  - intermediate
status: complete
version: 5
layout: default
parent: "Authorization"
grand_parent: "Technical Mastery"
nav_order: 24
permalink: /technical-mastery/authorization/wildcard-permissions-and-risks/
---

⚡ **TL;DR** - Wildcard permissions (`*`, `.*`, `admin:*`) grant
access to everything matching the pattern - including future resources
and actions that didn't exist when the permission was assigned. The
danger is in what you can't see: assigning `s3:*` grants access to
not just GetObject and PutObject, but also DeleteBucket,
PutBucketPolicy, and any new S3 action AWS adds next year.
Wildcards are convenient and almost always overkill. Use explicit
action lists.

---

### 📊 Entry Metadata

| #024 | Category: Authorization | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | ATZ-004 Least Privilege, ATZ-007 Permissions, ATZ-023 Service Accounts | |
| **Used by:** | ATZ-041, ATZ-042, ATZ-043 | |
| **Related:** | ATZ-007 Permissions, ATZ-023 Service Accounts, ATZ-041 Privilege Escalation | |

---

### 📘 Textbook Definition

Wildcard permissions use glob or pattern syntax to grant access
to multiple actions, resources, or principals simultaneously.
Common forms: `s3:*` (all S3 actions), `arn:aws:s3:::*` (all
S3 resources), `role:*` (all roles with any suffix), `admin:*`
(all admin sub-permissions). The risk is permission sprawl:
wildcards grant more than intended, grant future capabilities
automatically, and make it impossible to reason about the actual
access surface. Best practice: never use wildcards on sensitive
resources; use explicit lists of exactly the needed actions.

---

### ⚙️ How It Works (Mechanism)

**What `s3:*` actually means:**

```
┌────────────────────────────────────────────────────────┐
│         Wildcard Permission Expansion                  │
├────────────────────────────────────────────────────────┤
│                                                        │
│  Policy: "Action": "s3:*"                              │
│  Looks like: read/write S3 objects                     │
│  Actually includes:                                    │
│    s3:GetObject           (read files - intended)      │
│    s3:PutObject           (write files - intended)     │
│    s3:DeleteObject        (delete files - maybe not)   │
│    s3:DeleteBucket        (DELETE ENTIRE BUCKET)       │
│    s3:PutBucketPolicy     (override bucket security)   │
│    s3:PutBucketAcl        (make bucket public)         │
│    s3:PutBucketPublicAccessBlock (disable public block)│
│    ... and 60+ more actions                            │
│    ... and any new action AWS adds in the future       │
│                                                        │
│  RISK: an attacker who compromises this service        │
│  account can: delete all data, make all data public,   │
│  or override the bucket policy to grant themselves     │
│  permanent access                                      │
│                                                        │
│  DETECTION: AWS Access Analyzer, Checkov, tfsec        │
│  will flag wildcard permissions as HIGH finding        │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - Terraform: wildcard vs explicit permissions**

```hcl
# BAD: wildcard - grants 60+ S3 actions including destructive
resource "aws_iam_policy" "bad_s3" {
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = "s3:*"          # Wildcard
      Resource = "*"              # Wildcard resource
    }]
  })
}

# GOOD: explicit actions on explicit resources
resource "aws_iam_policy" "good_s3" {
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::my-app-bucket",
          "arn:aws:s3:::my-app-bucket/*"
        ]
      }
    ]
  })
}
# If a future action is needed: add it explicitly.
# This forces review of what access is being granted.
```

**Example - Permission sprawl from Spring Security wildcards**

```java
// BAD: wildcard role implies all sub-permissions
// A ROLE_ADMIN gets everything under admin:*
http.authorizeHttpRequests(auth -> auth
    .requestMatchers("/admin/**")
        .hasRole("ADMIN") // any admin can do anything
    .requestMatchers("/api/**")
        .hasAnyRole("ADMIN", "USER")
    .anyRequest().authenticated()
);

// GOOD: explicit permissions per endpoint
http.authorizeHttpRequests(auth -> auth
    .requestMatchers(HttpMethod.GET, "/admin/users")
        .hasAuthority("PERMISSION_VIEW_USERS")
    .requestMatchers(HttpMethod.DELETE, "/admin/users/**")
        .hasAuthority("PERMISSION_DELETE_USERS")
    .requestMatchers("/admin/system-config")
        .hasAuthority("PERMISSION_SYSTEM_CONFIG")
    .anyRequest().authenticated()
);
// Benefit: a compromised "admin" account that only
// has PERMISSION_VIEW_USERS cannot delete users
```

---

*Authorization category: ATZ | Entry: ATZ-024 | v5.0*