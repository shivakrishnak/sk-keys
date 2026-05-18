---
id: ATZ-036
title: "Relationship-Based Access Control (ReBAC)"
category: Authorization
tier: tier-2-networking-security
folder: ATZ-authorization
difficulty: ★★★
depends_on: ATZ-013, ATZ-015, ATZ-034
used_by: ATZ-037, ATZ-038, ATZ-047, ATZ-050
related: ATZ-037, ATZ-038, ATZ-057
tags:
  - security
  - authorization
  - rebac
  - zanzibar
  - graph-based
  - advanced
status: complete
version: 5
layout: default
parent: "Authorization"
grand_parent: "Technical Mastery"
nav_order: 36
permalink: /technical-mastery/authorization/relationship-based-access-control-rebac/
---

⚡ **TL;DR** - Relationship-Based Access Control (ReBAC) bases
authorization decisions on the graph of relationships between users
and resources, not just roles or attributes. "Can Alice read
doc-001?" becomes a graph reachability query: "Is there a path from
Alice to doc-001 via `editor` or `owner` relationships?" ReBAC
naturally models Google Drive sharing, Notion pages, and GitHub repo
permissions. It scales to billions of relationships (Google Zanzibar
serves 10M+ authorization decisions per second) but requires a
specialized relationship database (SpiceDB, OpenFGA).

---

### 📊 Entry Metadata

| #036 | Category: Authorization | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | ATZ-013 RBAC, ATZ-015 ABAC, ATZ-034 Capabilities | |
| **Used by:** | ATZ-037, ATZ-038, ATZ-047, ATZ-050 | |
| **Related:** | ATZ-037 Zanzibar, ATZ-038 SpiceDB, ATZ-057 Formal Models | |

---

### 📘 Textbook Definition

Relationship-Based Access Control (ReBAC) is an authorization
model in which access decisions are derived from a graph of
relationships between principals (users, groups) and resources.
The model stores relationships as triples: (object, relation,
subject), e.g., (doc-001, editor, alice) or (doc-001, parent,
folder-A). Authorization questions are expressed as path queries:
"Does a path from user to resource exist via the allowed
relations?" ReBAC handles hierarchical sharing naturally (sharing
a folder shares all documents within it) and supports tuple-
to-userset expansion (a user inherits permissions from groups
they belong to). The canonical ReBAC system is Google Zanzibar.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│         ReBAC Relationship Graph                       │
├────────────────────────────────────────────────────────┤
│                                                        │
│  Relationship tuples (stored):                         │
│  (folder-A, parent, folder-B)                          │
│  (folder-B, editor, alice)                             │
│  (doc-001, parent, folder-A)                           │
│  (doc-002, owner, alice)                               │
│                                                        │
│  Permission schema (defined separately):               │
│  document#read: owner OR editor OR viewer              │
│  document#editor: directly assigned                    │
│    OR parent/folder#editor (inherited from parent)     │
│                                                        │
│  Question: can alice read doc-001?                     │
│  doc-001 -> parent -> folder-A                         │
│  folder-A -> parent -> folder-B                        │
│  folder-B -> editor -> alice                           │
│  alice has editor on folder-B which is an ancestor     │
│  of doc-001 -> ALLOW                                   │
│                                                        │
│  This is a graph traversal (BFS/DFS)                   │
│  At Google scale: 10^12 tuples, 10^7 QPS              │
│  Requires: distributed, consistent relationship DB     │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - SpiceDB relationship check (Java)**

```java
@Service
public class SpiceDbAuthorizationService {

    private final PermissionsServiceGrpc.PermissionsServiceBlockingStub
        permissionsStub;

    public boolean canUserReadDocument(String userId,
                                        String docId) {
        CheckPermissionRequest request =
            CheckPermissionRequest.newBuilder()
                .setConsistency(Consistency.newBuilder()
                    .setMinimizeLatency(true) // or fully_consistent
                    .build())
                .setResource(ObjectReference.newBuilder()
                    .setObjectType("document")
                    .setObjectId(docId)
                    .build())
                .setPermission("read")
                .setSubject(SubjectReference.newBuilder()
                    .setObject(ObjectReference.newBuilder()
                        .setObjectType("user")
                        .setObjectId(userId)
                        .build())
                    .build())
                .build();

        CheckPermissionResponse response =
            permissionsStub.checkPermission(request);
        return response.getPermissionship()
            == CheckPermissionResponse.Permissionship
                .PERMISSIONSHIP_HAS_PERMISSION;
    }

    public void writeRelationship(String objectType,
            String objectId, String relation,
            String subjectType, String subjectId) {
        WriteRelationshipsRequest request =
            WriteRelationshipsRequest.newBuilder()
                .addUpdates(RelationshipUpdate.newBuilder()
                    .setOperation(
                        RelationshipUpdate.Operation
                        .OPERATION_CREATE)
                    .setRelationship(Relationship.newBuilder()
                        .setResource(ObjectReference.newBuilder()
                            .setObjectType(objectType)
                            .setObjectId(objectId).build())
                        .setRelation(relation)
                        .setSubject(SubjectReference.newBuilder()
                            .setObject(ObjectReference.newBuilder()
                                .setObjectType(subjectType)
                                .setObjectId(subjectId).build())
                            .build())
                        .build())
                    .build())
                .build();
        permissionsStub.writeRelationships(request);
    }
}
```

---

*Authorization category: ATZ | Entry: ATZ-036 | v5.0*