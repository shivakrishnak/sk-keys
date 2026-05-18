---
id: ATZ-021
title: "Permission Inheritance and Propagation"
category: Authorization
tier: tier-2-networking-security
folder: ATZ-authorization
difficulty: ★★☆
depends_on: ATZ-013, ATZ-014
used_by: ATZ-047, ATZ-050
related: ATZ-013, ATZ-014, ATZ-022
tags:
  - security
  - authorization
  - permissions
  - inheritance
  - rbac
  - intermediate
status: complete
version: 5
layout: default
parent: "Authorization"
grand_parent: "Technical Mastery"
nav_order: 21
permalink: /technical-mastery/authorization/permission-inheritance-and-propagation/
---

⚡ **TL;DR** - Permission inheritance lets child entities (subfolder,
sub-resource, child organization) automatically receive permissions
from their parents, reducing manual assignment overhead. The failure
modes are subtle: inheritance makes "deny" semantics critical (a
parent deny must override child allows), cycles can emerge in graph
models, and permissions can silently expand when a new parent is
added. Every inheritance system needs an explicit rule for what
breaks inheritance and what the default behavior is.

---

### 📊 Entry Metadata

| #021 | Category: Authorization | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | ATZ-013 RBAC Patterns, ATZ-014 Hierarchical RBAC | |
| **Used by:** | ATZ-047, ATZ-050 | |
| **Related:** | ATZ-013 RBAC, ATZ-014 Hierarchical RBAC, ATZ-022 Delegated Auth | |

---

### 📘 Textbook Definition

Permission inheritance is the mechanism by which a resource or
role automatically receives the permissions of its parent in a
hierarchy. In folder/file systems, a file inherits its parent
folder's ACL unless overridden. In RBAC, a child role inherits
all permissions of its parent roles. In organization hierarchies,
a child team inherits the parent org's resource policies.
Propagation refers to how permission changes cascade through
the hierarchy: updating a parent's permission must trigger
re-evaluation (or cache invalidation) for all descendants.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│         Permission Inheritance Models                  │
├────────────────────────────────────────────────────────┤
│                                                        │
│  MODEL 1: Additive (Google Drive)                      │
│  Parent: Alice can read /project                       │
│  Child: Alice inherits read on /project/code           │
│  Explicit grant: Alice gets write on /project/code     │
│  Result: Alice has read+write on /project/code         │
│                                                        │
│  MODEL 2: Deny override (Windows NTFS)                 │
│  Parent: Alice can read /project (allow)               │
│  Parent: Alice DENY read /project/secret               │
│  Child: DENY beats any allow, even explicit            │
│  Result: Alice cannot read /project/secret             │
│                                                        │
│  MODEL 3: Inheritance break (explicit assignment)      │
│  AWS S3: bucket policy default: deny all               │
│  Must explicitly grant per-object if needed            │
│  No automatic inheritance from bucket to object        │
│                                                        │
│  PROPAGATION PROBLEM:                                  │
│  Organization: 10k users, 1M files, 5-deep hierarchy   │
│  Admin updates /root ACL                               │
│  Naive: recalculate 1M effective permissions           │
│  Smart: lazy propagation + version token               │
│  (recompute only on next access check)                 │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - Hierarchical ACL check with inheritance**

```java
@Service
public class HierarchicalAclService {

    public boolean hasPermission(String userId,
                                  String resourcePath,
                                  String permission) {
        // Walk up the resource tree to find effective perm
        List<String> pathSegments = getPathHierarchy(
            resourcePath);

        String effectiveDecision = "not_set";

        // From root to leaf: last explicit setting wins
        // (except DENY which always wins - see below)
        for (String path : pathSegments) {
            AclEntry entry = aclRepo
                .findByUserAndResource(userId, path);
            if (entry == null) continue;

            if (entry.isDeny(permission)) {
                return false; // DENY always wins
            }
            if (entry.isAllow(permission)) {
                effectiveDecision = "allow";
            }
        }
        return "allow".equals(effectiveDecision);
    }

    private List<String> getPathHierarchy(String path) {
        // Returns ["/", "/project", "/project/code"]
        // for input "/project/code"
        List<String> result = new ArrayList<>();
        String[] parts = path.split("/");
        StringBuilder current = new StringBuilder();
        result.add("/");
        for (int i = 1; i < parts.length; i++) {
            current.append("/").append(parts[i]);
            result.add(current.toString());
        }
        return result;
    }
}
```

**Example - BAD: no deny semantics in inheritance**

```java
// BAD: additive inheritance with no deny override
// A child permission grant always wins
public boolean hasPermission(String userId,
                              String resource,
                              String permission) {
    // Check resource first, then parent, then grandparent
    for (String path : getPathFromLeafToRoot(resource)) {
        AclEntry e = aclRepo.find(userId, path);
        if (e != null && e.isAllow(permission)) {
            return true; // FIRST allow wins
        }
    }
    return false;
}
// Problem: Admin sets DENY on /hr/salaries at root
// HR junior gets explicit ALLOW on /hr/salaries/2024
// Junior can access /hr/salaries/2024 despite root deny

// GOOD: deny at ANY level blocks access
// Check ALL levels for deny FIRST, then allow
```

---

*Authorization category: ATZ | Entry: ATZ-021 | v5.0*