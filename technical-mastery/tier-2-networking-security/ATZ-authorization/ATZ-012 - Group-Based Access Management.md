---
id: ATZ-012
title: "Group-Based Access Management"
category: Authorization
tier: tier-2-networking-security
folder: ATZ-authorization
difficulty: ★☆☆
depends_on: ATZ-006, ATZ-007
used_by: ATZ-013, ATZ-014, ATZ-050
related: ATZ-006, ATZ-007, ATZ-013
tags:
  - security
  - authorization
  - groups
  - access-management
  - foundational
status: complete
version: 5
layout: default
parent: "Authorization"
grand_parent: "Technical Mastery"
nav_order: 12
permalink: /technical-mastery/authorization/group-based-access-management/
---

⚡ **TL;DR** - Groups aggregate users for access management: assign
permissions to a group, add users to the group. This is the practical
middle layer between assigning permissions directly to users (does
not scale) and full RBAC with multiple permission layers (complex).
Groups work well in LDAP, Active Directory, and cloud IAM. The failure
mode: groups accumulate members and permissions indefinitely without
review - the same drift problem as individual permissions.

---

### 📊 Entry Metadata

| #012 | Category: Authorization | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | ATZ-006, ATZ-007 | |
| **Used by:** | ATZ-013, ATZ-014, ATZ-050 | |
| **Related:** | ATZ-006 RBAC, ATZ-007 Permissions, ATZ-013 RBAC Implementation | |

---

### 📘 Textbook Definition

Group-based access management is a technique where users are
organized into named groups, and permissions or roles are
assigned to groups rather than individual users. Access
decisions are made based on group membership. Groups provide
a practical scaling mechanism: provisioning a new employee
requires only adding them to appropriate groups (not
enumerating individual permissions). Groups map naturally
to organizational structures (teams, departments, job functions)
and are natively supported by LDAP, Active Directory, AWS IAM,
GCP IAM, and most enterprise directory services.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Instead of giving permissions to each person individually,
give permissions to a team; add people to the team.

**One analogy:**
> A contractor building permit. Rather than issuing permits
> to each worker individually (which changes weekly), the
> city issues the permit to the company. All workers employed
> by that company are covered. Adding a new worker = they
> are automatically covered by the company permit.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│          Group-Based Access: Three Models              │
├────────────────────────────────────────────────────────┤
│                                                        │
│  MODEL 1: Groups = Roles (simple)                      │
│  Group: "engineers"                                    │
│    Members: alice, bob, carol                          │
│    Permissions: code:read, code:write, deploy:staging  │
│                                                        │
│  MODEL 2: Groups nest in RBAC (enterprise)             │
│  Group "engineering" assigned to Role "developer"      │
│    Role "developer" has: code:read, code:write         │
│    Group "engineering-leads" → Role "senior-developer" │
│                                                        │
│  MODEL 3: AD/LDAP groups synced to application        │
│  LDAP group "CN=AppAdmins,OU=Groups,DC=corp,DC=com"    │
│    Synced to application role "ADMIN"                  │
│    HR adds Alice to AD group → Alice gets app ADMIN    │
│    provisioning is automatic                           │
│                                                        │
└────────────────────────────────────────────────────────┘
```

**AWS IAM groups:**

```json
{
  "GroupName": "Developers",
  "Policies": [{
    "PolicyArn": "arn:aws:iam::aws:policy/AWSCodeCommitFullAccess"
  }]
}
// Adding a developer to the group grants CodeCommit access
// Removing them from the group revokes it
// No individual IAM policy changes needed
```

---

### 💻 Code Examples

**Example - LDAP group to application role mapping**

```java
@Service
public class LdapGroupSyncService {

    // Map LDAP group memberships to application roles
    private static final Map<String, String> GROUP_ROLE_MAP =
        Map.of(
            "CN=AppAdmins,OU=Groups,DC=corp,DC=com", "ADMIN",
            "CN=AppEditors,OU=Groups,DC=corp,DC=com", "EDITOR",
            "CN=AppViewers,OU=Groups,DC=corp,DC=com", "VIEWER"
        );

    @Override
    public Collection<GrantedAuthority> getAuthorities(
            String username, DirContextOperations ctx) {
        String[] groups = ctx.getStringAttributes(
            "memberOf");
        return Arrays.stream(groups)
            .map(GROUP_ROLE_MAP::get)
            .filter(Objects::nonNull)
            .map(role -> new SimpleGrantedAuthority(
                "ROLE_" + role))
            .collect(Collectors.toList());
    }
}
```

**Example - BAD vs GOOD: group sprawl vs governed groups**

```
BAD: ungoverned group creation
  Any team lead can create groups.
  3 years later:
    CN=dev-team-1        (7 members, unknown permissions)
    CN=dev-team-1-bak    (created by accident, 3 members)
    CN=dev-team-2        (15 members)
    CN=dev-2-temp        (2 members, 18 months old "temp")
    CN=frontend-guys     (informal name, all permissions)
    CN=api-team          (overlaps with dev-team-2)
  Nobody knows the diff between "dev-team-1" and "api-team".

GOOD: governed group lifecycle
  - Groups created by request with: name, owner, purpose,
    expiry date for temp groups
  - Naming convention: DEPT-FUNCTION (e.g., ENG-BACKEND)
  - Quarterly membership review required by group owner
  - Unused groups (no access events in 90 days) auto-archived
  - Group permissions documented in central registry
```

---

*Authorization category: ATZ | Entry: ATZ-012 | v5.0*