---
id: ATZ-043
title: "Insecure Direct Object Reference (IDOR)"
category: Authorization
tier: tier-2-networking-security
folder: ATZ-authorization
difficulty: ★★★
depends_on: ATZ-019, ATZ-025, ATZ-042
used_by: ATZ-044, ATZ-054
related: ATZ-042, ATZ-044, ATZ-019
tags:
  - security
  - authorization
  - idor
  - owasp
  - advanced
status: complete
version: 5
layout: default
parent: "Authorization"
grand_parent: "Technical Mastery"
nav_order: 43
permalink: /technical-mastery/authorization/insecure-direct-object-reference-idor/
---

⚡ **TL;DR** - IDOR (Insecure Direct Object Reference) occurs when
an API endpoint exposes a direct reference to an object (database
ID, filename) without verifying whether the requesting user is
authorized to access that specific object. Change `/api/invoices/1001`
to `/api/invoices/1002` and you read someone else's invoice. Fix:
every read/write to a resource must verify ownership or permission,
not just authentication. Alternatively, use opaque IDs (UUID or
HMAC-signed references) that are unguessable - but still add the
ownership check.

---

### 📊 Entry Metadata

| #043 | Category: Authorization | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | ATZ-019 Row-Level Security, ATZ-025 Testing, ATZ-042 Broken Access | |
| **Used by:** | ATZ-044, ATZ-054 | |
| **Related:** | ATZ-042 Broken Access, ATZ-044 Forced Browsing, ATZ-019 Row-Level Security | |

---

### 📘 Textbook Definition

Insecure Direct Object Reference (IDOR) is a specific type
of broken access control where an application uses user-
controlled input to directly access objects (database records,
files, functions) without authorization validation. The object
reference can be an auto-incrementing integer (1001, 1002),
a filename, a URL path, a hidden form field, or any other
identifier. IDOR attacks succeed when the API trusts the
requested ID without verifying "does this user have the right
to access object with ID X?" IDOR is horizontal privilege
escalation - accessing resources owned by another user at the
same privilege level.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│         IDOR Attack Flow                               │
├────────────────────────────────────────────────────────┤
│                                                        │
│  SETUP:                                                │
│  User Alice has: account_id=1001                       │
│  User Bob has:   account_id=1002                       │
│                                                        │
│  VULNERABLE API:                                       │
│  GET /api/accounts/1001                                │
│  Authentication check: is user logged in? YES          │
│  Authorization check: MISSING                          │
│  Response: Alice's account data (status 200)           │
│                                                        │
│  ATTACK:                                               │
│  Alice (attacker) changes ID in request:               │
│  GET /api/accounts/1002                                │
│  Authentication check: is user logged in? YES          │
│  Authorization check: MISSING                          │
│  Response: Bob's account data (status 200)             │
│  Alice reads Bob's private data                        │
│                                                        │
│  FIXES (must use BOTH):                                │
│  1. Ownership check:                                   │
│     if (account.owner != currentUser) throw 403        │
│  2. Use UUIDs or HMACs instead of sequential IDs       │
│     (unguessable IDs reduce enumeration - NOT a fix   │
│      for missing auth checks)                          │
│                                                        │
│  DATABASE-LEVEL FIX (PostgreSQL RLS):                  │
│  CREATE POLICY account_owner ON accounts               │
│    USING (owner_id = current_user_id());               │
│  Every query: WHERE owner_id = current_user auto-added │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - IDOR vulnerability and fix**

```java
// BAD: no ownership check - classic IDOR
@GetMapping("/api/documents/{id}")
public Document getDocument(@PathVariable Long id) {
    // Returns ANY document if you know the ID
    // Integer IDs are trivially guessable/enumerable
    return documentRepository.findById(id)
        .orElseThrow(NotFoundException::new);
}

// GOOD: ownership check on every resource access
@GetMapping("/api/documents/{id}")
public Document getDocument(@PathVariable Long id,
                              Authentication auth) {
    String currentUserId = auth.getName();
    Document doc = documentRepository.findById(id)
        .orElseThrow(NotFoundException::new);

    // Check: does THIS user own THIS document?
    if (!doc.getOwnerId().equals(currentUserId)
            && !hasAdminAccess(auth)) {
        // Return 404, not 403:
        // 403 tells attacker "resource exists but denied"
        // 404 gives no information about resource existence
        throw new NotFoundException();
    }
    return doc;
}

// ALSO GOOD: query already scoped to current user
@GetMapping("/api/documents/{id}")
public Document getDocument(@PathVariable Long id,
                              Authentication auth) {
    // findByIdAndOwnerId: if ID exists but wrong owner:
    // returns empty -> 404 (no info leak)
    return documentRepository
        .findByIdAndOwnerId(id, auth.getName())
        .orElseThrow(NotFoundException::new);
}
```

---

*Authorization category: ATZ | Entry: ATZ-043 | v5.0*