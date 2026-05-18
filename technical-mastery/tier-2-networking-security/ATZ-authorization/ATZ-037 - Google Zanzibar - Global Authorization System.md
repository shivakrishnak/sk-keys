---
id: ATZ-037
title: "Google Zanzibar - Global Authorization System"
category: Authorization
tier: tier-2-networking-security
folder: ATZ-authorization
difficulty: ★★★
depends_on: ATZ-036
used_by: ATZ-038, ATZ-046, ATZ-055
related: ATZ-036, ATZ-038, ATZ-055
tags:
  - security
  - authorization
  - zanzibar
  - google
  - distributed
  - advanced
status: complete
version: 5
layout: default
parent: "Authorization"
grand_parent: "Technical Mastery"
nav_order: 37
permalink: /technical-mastery/authorization/google-zanzibar-global-authorization-system/
---

⚡ **TL;DR** - Google Zanzibar is the authorization system behind
Google Drive, YouTube, Maps, and Cloud. It stores authorization
as relationship tuples in a globally distributed, consistent
database, serves 10M+ authorization checks per second at <10ms
p99, and supports nested permissions (sharing a folder shares its
contents). The Zanzibar paper (2019) introduced the consistency
model "new enemy problem" - you must not grant access based on
stale relationship data when a newer permission revocation exists.
Every modern ReBAC system (SpiceDB, OpenFGA, Permify) is a
Zanzibar implementation.

---

### 📊 Entry Metadata

| #037 | Category: Authorization | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | ATZ-036 ReBAC | |
| **Used by:** | ATZ-038, ATZ-046, ATZ-055 | |
| **Related:** | ATZ-036 ReBAC, ATZ-038 SpiceDB, ATZ-055 Zanzibar Paper | |

---

### 📘 Textbook Definition

Google Zanzibar is a globally distributed authorization system
that stores fine-grained relationship data as tuples of the
form (object, relation, user) and evaluates authorization as
graph reachability queries across these tuples. Published in
2019 (USENIX ATC), Zanzibar stores trillions of access control
tuples across multiple regions, ensures external consistency
(linearizability within a namespace), and provides the `check`
and `expand` APIs. The system introduces the concept of a
"zookie" (a consistency token that ensures authorization checks
use data as fresh as the latest write operation), solving the
"new enemy problem" - ensuring a user cannot gain access based
on data that predates their permissions being revoked.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│         Zanzibar Core Concepts                         │
├────────────────────────────────────────────────────────┤
│                                                        │
│  RELATIONSHIP TUPLES:                                  │
│  {namespace: "doc", object: "doc:123",                 │
│   relation: "editor", user: "user:alice"}              │
│  {namespace: "doc", object: "doc:123",                 │
│   relation: "parent", user: "folder:abc#member"}       │
│                                                        │
│  CHECK API:                                            │
│  check(user:alice, relation:read, object:doc:123)      │
│  -> traverse relation graph                            │
│  -> BFS/DFS from doc:123 via read permission rules     │
│  -> alice is editor? YES -> ALLOW                      │
│                                                        │
│  EXPAND API:                                           │
│  expand(relation:read, object:doc:123)                 │
│  -> return full user-set with read access              │
│  -> useful for UI (show who has access)                │
│                                                        │
│  THE NEW ENEMY PROBLEM:                                │
│  T=0: alice granted access to doc:123                  │
│  T=1: Mallory is removed from alice's group            │
│  T=2: Mallory makes auth request                       │
│  If Zanzibar uses stale T=0 data: Mallory gets access  │
│  Zookie: "use data no older than my write at T=1"      │
│  Zanzibar enforces this -> Mallory denied at T=2       │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - Zanzibar-like namespace config (SpiceDB syntax)**

```
// SpiceDB schema (Zanzibar namespace config equivalent)
definition user {}

definition group {
    relation member: user
}

definition folder {
    relation parent: folder
    relation owner: user | group#member
    relation editor: user | group#member
    relation viewer: user | group#member

    permission view = viewer + editor + owner
    permission edit = editor + owner
    permission admin = owner
}

definition document {
    relation parent: folder
    relation owner: user
    relation editor: user | group#member
    relation viewer: user | group#member

    // Inherits permissions from parent folder
    permission view = viewer + editor + owner
                    + parent->view
    permission edit = editor + owner
                    + parent->edit
    permission delete = owner + parent->admin
}

// Adding a relationship tuple:
// (document:doc-001, editor, user:alice) -> alice can edit
// (document:doc-001, parent, folder:proj-a)
// (folder:proj-a, viewer, group:engineers#member)
// -> all engineers can view doc-001 via folder inheritance
```

---

*Authorization category: ATZ | Entry: ATZ-037 | v5.0*