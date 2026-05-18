---
id: ATZ-010
title: "Access Control Lists (ACL)"
category: Authorization
tier: tier-2-networking-security
folder: ATZ-authorization
difficulty: ★☆☆
depends_on: ATZ-003, ATZ-007
used_by: ATZ-019, ATZ-034, ATZ-036
related: ATZ-006, ATZ-007, ATZ-009
tags:
  - security
  - authorization
  - acl
  - foundational
status: complete
version: 5
layout: default
parent: "Authorization"
grand_parent: "Technical Mastery"
nav_order: 10
permalink: /technical-mastery/authorization/access-control-lists-acl/
---

⚡ **TL;DR** - An Access Control List (ACL) is a per-resource list
of (subject, permissions) entries. It is the oldest and most direct
access control mechanism: "for this resource, who can do what?"
ACLs are used in UNIX file permissions, network firewalls, and
cloud storage. They scale poorly to complex policies but are optimal
for owner-defined sharing (Google Drive, Dropbox) where each resource
has its own bespoke access list.

---

### 📊 Entry Metadata

| #010 | Category: Authorization | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | ATZ-003, ATZ-007 | |
| **Used by:** | ATZ-019, ATZ-034, ATZ-036 | |
| **Related:** | ATZ-006 RBAC, ATZ-007 Permissions, ATZ-009 Resource Policies | |

---

### 📘 Textbook Definition

An Access Control List (ACL) is an ordered list of access
control entries (ACEs), each specifying a subject (user,
group, or role) and the operations permitted (or denied) on
the associated resource. The resource owns its ACL; when
an access request arrives, the system traverses the ACL
entries in order until a matching entry is found or the list
is exhausted (with implicit deny on no match). ACLs implement
discretionary access control (DAC): the resource owner can
modify the ACL.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
An ACL is the "people allowed to enter" list pinned to each
resource, not to the person.

**One analogy:**
> A Google Doc's sharing settings. The document has a list:
> "Alice - can view; Bob - can comment; Carol - can edit;
> anyone with the link - can view." This list lives with the
> document, not the users. Each document has its own list.
> The owner (you) decide who to add or remove. This is
> precisely an ACL: a resource-attached list of (subject,
> permission) pairs.

---

### ⚙️ How It Works (Mechanism)

**ACL structures across systems:**

```
┌─────────────────────────────────────────────────────┐
│              ACL Across Different Systems           │
├─────────────────────────────────────────────────────┤
│                                                     │
│  UNIX FILE PERMISSIONS (simplified ACL):            │
│  -rwxr-xr-- report.pdf                             │
│  Owner (alice):  rwx (read, write, execute)         │
│  Group (staff):  r-x (read, execute)               │
│  Others:         r-- (read only)                   │
│                                                     │
│  POSIX ACL (extended):                              │
│  user:alice:rwx                                     │
│  user:bob:r--                                       │
│  group:staff:r-x                                    │
│  other::---                                         │
│                                                     │
│  NETWORK FIREWALL ACL:                              │
│  Rule 1: PERMIT tcp 10.0.0.0/24 any port 443       │
│  Rule 2: PERMIT tcp 10.0.1.0/24 10.0.0.5 port 5432 │
│  Rule 3: DENY   any any any                         │
│  (Processed top-to-bottom; first match wins)        │
│                                                     │
│  APPLICATION-LEVEL ACL (e.g., Google Drive):        │
│  Document "Q4-Report.pdf":                          │
│    alice@corp.com:  EDITOR                          │
│    bob@corp.com:    VIEWER                          │
│    carol@corp.com:  COMMENTER                       │
│    *@corp.com:      VIEWER                          │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**ACL vs RBAC comparison:**

| Characteristic | ACL | RBAC |
|---|---|---|
| Policy stored | With resource | With role/group |
| Owner control | Resource owner | System admin |
| Scalability | Poor at many users | Good (roles) |
| Flexibility | High (per-object) | Lower (role granularity) |
| Best for | Sharing (docs, files) | Org-wide access |

---

### 💻 Code Examples

**Example - Database ACL table pattern**

```sql
-- ACL pattern: per-resource sharing table
CREATE TABLE document_acl (
    document_id BIGINT NOT NULL,
    principal_type VARCHAR(20) NOT NULL, -- USER, GROUP, ROLE
    principal_id BIGINT NOT NULL,
    permission VARCHAR(20) NOT NULL,     -- READ, WRITE, OWNER
    granted_at TIMESTAMP DEFAULT NOW(),
    granted_by BIGINT REFERENCES users(id),
    PRIMARY KEY (document_id, principal_type, principal_id)
);

-- Check if user can read a document
SELECT 1
FROM document_acl
WHERE document_id = $1
  AND (
    (principal_type = 'USER' AND principal_id = $2)
    OR (principal_type = 'GROUP' 
        AND principal_id IN (
          SELECT group_id FROM user_groups WHERE user_id = $2
        ))
  )
  AND permission IN ('READ', 'WRITE', 'OWNER')
LIMIT 1;
```

**Example - BAD vs GOOD: ACL traversal**

```java
// BAD: loading entire ACL into memory for every check
// (O(n) where n = number of ACL entries per resource)
public boolean canRead(User user, Document doc) {
    List<AclEntry> acl = aclRepo.findAll(doc.getId());
    // Loading potentially thousands of entries per request
    for (AclEntry entry : acl) {
        if (entry.matches(user)) return true;
    }
    return false;
}

// GOOD: single targeted query (O(1) with proper index)
public boolean canRead(User user, Document doc) {
    // Check user directly, then via groups in one query
    return aclRepo.existsPermission(
        doc.getId(),
        user.getId(),
        user.getGroupIds(),
        List.of("READ", "WRITE", "OWNER")
    );
}
// Index: (document_id, principal_id) - makes O(1) lookup
```

---

### 🔭 At Scale

ACLs scale poorly with large user sets. A document shared
with 50,000 users has 50,000 ACL rows. Checking a user's
permission requires joining against their groups or scanning
the list. Alternatives at scale:

1. **ACL + group indirection**: share with groups, not users.
   One ACL entry per group; group membership is elsewhere.

2. **ACL + RBAC hybrid**: "everyone with VIEWER role can see
   this" = one ACL entry per role rather than per user.

3. **ReBAC (Relation-Based)**: Google Zanzibar generalizes
   ACLs into relationship tuples at planetary scale. See ATZ-036.

---

*Authorization category: ATZ | Entry: ATZ-010 | v5.0*