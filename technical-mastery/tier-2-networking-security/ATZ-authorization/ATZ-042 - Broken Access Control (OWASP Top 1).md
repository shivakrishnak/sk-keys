---
id: ATZ-042
title: "Broken Access Control (OWASP Top 1)"
category: Authorization
tier: tier-2-networking-security
folder: ATZ-authorization
difficulty: ★★★
depends_on: ATZ-006, ATZ-015, ATZ-025, ATZ-041
used_by: ATZ-043, ATZ-044, ATZ-050, ATZ-054
related: ATZ-041, ATZ-043, ATZ-044
tags:
  - security
  - authorization
  - broken-access-control
  - owasp
  - advanced
status: complete
version: 5
layout: default
parent: "Authorization"
grand_parent: "Technical Mastery"
nav_order: 42
permalink: /technical-mastery/authorization/broken-access-control-owasp-top-1/
---

⚡ **TL;DR** - Broken Access Control (OWASP A01:2021) is the most
prevalent web security failure. It occurs when authorization
checks are missing, incomplete, or only on the client side. An
attacker can read any user's data (change the ID in the URL),
access admin functions (know the URL, bypass the hidden menu),
or escalate privileges (modify a role parameter). The root cause
is almost always trusting the client to enforce access control.
Every API endpoint needs an explicit server-side authorization
check - no exceptions.

---

### 📊 Entry Metadata

| #042 | Category: Authorization | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | ATZ-006 RBAC, ATZ-015 ABAC, ATZ-025 Testing, ATZ-041 PrivEsc | |
| **Used by:** | ATZ-043, ATZ-044, ATZ-050, ATZ-054 | |
| **Related:** | ATZ-041 PrivEsc, ATZ-043 IDOR, ATZ-044 Forced Browsing | |

---

### 📘 Textbook Definition

Broken Access Control is OWASP's #1 web application security
risk. It encompasses any failure of access control enforcement:
vertical (accessing higher-privilege functions), horizontal
(accessing another user's resources), insecure direct object
references (predictable IDs expose any user's data), missing
function-level checks (admin panel accessible to all
authenticated users), path traversal, metadata manipulation
(JWT/cookie tampering), CORS misconfigurations, and forced
browsing to authenticated pages. The common thread: access
control logic implemented on the client side or checked
inconsistently across endpoints.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│         Broken Access Control Patterns                 │
├────────────────────────────────────────────────────────┤
│                                                        │
│  1. IDOR - change user ID in URL/body                  │
│  GET /api/orders/123    <- your order                  │
│  GET /api/orders/124    <- someone else's order        │
│  No ownership check: 200 OK with their data            │
│                                                        │
│  2. MISSING FUNCTION LEVEL CHECK                       │
│  POST /api/admin/users   <- admin endpoint             │
│  Only UI hides this from non-admins                    │
│  Any authenticated user calling directly: works        │
│                                                        │
│  3. URL MANIPULATION                                   │
│  GET /dashboard/user    <- normal user view            │
│  GET /dashboard/admin   <- discovered by fuzzing       │
│  No server-side role check on /dashboard/admin         │
│                                                        │
│  4. METHOD OVERRIDE                                    │
│  GET /api/items/123     <- allowed (read)              │
│  DELETE /api/items/123  <- should require admin        │
│  Only GET checked for auth; DELETE not checked         │
│                                                        │
│  PREVENTION:                                           │
│  - Explicit check on EVERY endpoint                    │
│  - Deny by default (if not explicitly allowed: deny)   │
│  - Log all access denials                              │
│  - Regular access control audits                       │
│  - Automated tests for authorization rules             │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - Missing function-level access control**

```java
// BAD: only checks authentication, not authorization
@PostMapping("/admin/users/{id}/promote")
@Authenticated  // checks: is user logged in? YES.
public ResponseEntity<Void> promoteToAdmin(
        @PathVariable Long id) {
    // No check: is the CALLER an admin?
    // Any logged-in user can call this endpoint
    userService.setRole(id, Role.ADMIN);
    return ResponseEntity.ok().build();
}

// GOOD: explicit role requirement on every sensitive op
@PostMapping("/admin/users/{id}/promote")
@PreAuthorize("hasRole('ADMIN')")  // Spring Security
public ResponseEntity<Void> promoteToAdmin(
        @PathVariable Long id,
        Authentication auth) {
    // Auth checked before method invocation
    // Non-admins get 403 Forbidden before reaching here
    // Also: audit this action
    auditLog.record("PROMOTE_USER", auth.getName(), id);
    userService.setRole(id, Role.ADMIN);
    return ResponseEntity.ok().build();
}
```

---

*Authorization category: ATZ | Entry: ATZ-042 | v5.0*