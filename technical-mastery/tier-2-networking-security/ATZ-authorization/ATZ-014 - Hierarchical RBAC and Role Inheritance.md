---
id: ATZ-014
title: "Hierarchical RBAC and Role Inheritance"
category: Authorization
tier: tier-2-networking-security
folder: ATZ-authorization
difficulty: ★★☆
depends_on: ATZ-013
used_by: ATZ-036, ATZ-050
related: ATZ-006, ATZ-013, ATZ-015
tags:
  - security
  - authorization
  - rbac
  - role-hierarchy
  - intermediate
status: complete
version: 5
layout: default
parent: "Authorization"
grand_parent: "Technical Mastery"
nav_order: 14
permalink: /technical-mastery/authorization/hierarchical-rbac-and-role-inheritance/
---

⚡ **TL;DR** - Hierarchical RBAC (RBAC1 in the NIST model) allows roles
to inherit permissions from parent roles, mirroring organizational
hierarchies. A "Senior Editor" inherits all "Editor" permissions plus
gains additional ones. Inheritance reduces redundancy in role
definitions but adds complexity: a user's effective permissions are
the union of all inherited permissions from all assigned roles. This
union must be computed correctly - and can surprise you when a path
grants more than intended.

---

### 📊 Entry Metadata

| #014 | Category: Authorization | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | ATZ-013 | |
| **Used by:** | ATZ-036, ATZ-050 | |
| **Related:** | ATZ-006 RBAC, ATZ-013 RBAC Impl, ATZ-015 ABAC | |

---

### 📘 Textbook Definition

Hierarchical RBAC (NIST RBAC1) extends Core RBAC with role
inheritance: a role can have one or more parent roles, and
inherits all permissions of its ancestors. A user assigned
a child role automatically receives all permissions of the
role hierarchy above it. Effective permissions for a user
are the union of permissions from all directly assigned roles
and all ancestors in the role hierarchy. Hierarchical RBAC
models organizational structures (team member → lead →
manager → director) without requiring permission duplication
at each level.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│         Role Hierarchy Example                         │
├────────────────────────────────────────────────────────┤
│                                                        │
│  ADMIN                                                 │
│    owns: user:delete, system:config, all below         │
│    └─ EDITOR                                           │
│         owns: content:write, content:publish, all below│
│         └─ AUTHOR                                      │
│              owns: content:write (own), content:draft  │
│              └─ VIEWER                                 │
│                   owns: content:read                   │
│                                                        │
│  USER assigned role AUTHOR:                            │
│  Effective permissions =                               │
│    AUTHOR's own + VIEWER (parent):                     │
│    content:write(own) + content:draft + content:read   │
│                                                        │
│  USER assigned role EDITOR:                            │
│  Effective permissions =                               │
│    EDITOR's own + AUTHOR (parent) + VIEWER (grandparent│
│    content:write + content:publish + content:write(own)│
│    + content:draft + content:read                      │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - Role hierarchy in database**

```sql
-- Role hierarchy table
CREATE TABLE role_hierarchy (
    child_role_id  BIGINT REFERENCES roles(id),
    parent_role_id BIGINT REFERENCES roles(id),
    PRIMARY KEY (child_role_id, parent_role_id)
);

-- Recursive CTE: get all ancestors of a role
WITH RECURSIVE role_ancestors AS (
    -- Base: direct roles of the user
    SELECT role_id FROM user_roles WHERE user_id = $1
    UNION
    -- Recursive: parent roles
    SELECT rh.parent_role_id
    FROM role_hierarchy rh
    JOIN role_ancestors ra ON ra.role_id = rh.child_role_id
)
-- Get effective permissions from all roles in hierarchy
SELECT DISTINCT p.action, p.resource_type
FROM role_ancestors ra
JOIN role_permissions rp ON rp.role_id = ra.role_id
JOIN permissions p ON p.id = rp.permission_id;
```

**Example - BAD: unintended inheritance grants excess permissions**

```
Role hierarchy:
  PLATFORM_ADMIN
    └─ ORG_ADMIN
         └─ TEAM_LEAD
              └─ MEMBER

Scenario:
  "TEAM_LEAD" is assigned to Alice for Team A.
  Someone adds "export:all_orgs" permission to ORG_ADMIN
  (intending it only for org admins).
  
  Alice's effective permissions now include export:all_orgs
  via inheritance: TEAM_LEAD → ORG_ADMIN → export:all_orgs.
  
  Alice can now export all organizations' data even though
  she is only a team lead.

Fix:
  1. Permission changes must validate inheritance impact
  2. Use a "dry run" tool: show effective permissions for
     each role level before applying changes
  3. Constrained RBAC: block certain permissions from
     being inherited (use "direct only" flag on permissions)
  4. Quarterly audit: report effective permissions per user
```

**Example - Spring Security: checking inherited roles**

```java
// Spring Security automatically handles role hierarchy
// when configured with a RoleHierarchy bean

@Bean
public RoleHierarchy roleHierarchy() {
    RoleHierarchyImpl hierarchy = new RoleHierarchyImpl();
    hierarchy.setHierarchy(
        "ROLE_ADMIN > ROLE_EDITOR\n" +
        "ROLE_EDITOR > ROLE_AUTHOR\n" +
        "ROLE_AUTHOR > ROLE_VIEWER"
    );
    return hierarchy;
}

// With this hierarchy configured:
// A user with ROLE_ADMIN passes all of these:
//   hasRole('ADMIN') ✓
//   hasRole('EDITOR') ✓ (inherited)
//   hasRole('VIEWER') ✓ (inherited via chain)
// A user with ROLE_AUTHOR passes:
//   hasRole('AUTHOR') ✓
//   hasRole('VIEWER') ✓ (inherited)
//   hasRole('EDITOR') ✗ (AUTHOR is child of EDITOR,
//                         not parent - does not inherit up)
```

---

*Authorization category: ATZ | Entry: ATZ-014 | v5.0*