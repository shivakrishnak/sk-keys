---
id: ATZ-017
title: "OAuth Scopes as Authorization"
category: Authorization
tier: tier-2-networking-security
folder: ATZ-authorization
difficulty: ★★☆
depends_on: ATZ-016
used_by: ATZ-018, ATZ-022, ATZ-030
related: ATZ-016, ATZ-018, ATZ-022
tags:
  - security
  - authorization
  - oauth
  - scopes
  - intermediate
status: complete
version: 5
layout: default
parent: "Authorization"
grand_parent: "Technical Mastery"
nav_order: 17
permalink: /technical-mastery/authorization/oauth-scopes-as-authorization/
---

⚡ **TL;DR** - OAuth 2.0 scopes are coarse-grained authorization tokens
embedded in access tokens: they say what the client application is
allowed to do, not what the user is allowed to do. Scope `read:emails`
means this app can read emails on behalf of the user - even if the user
granted consent. Scopes protect against over-privileged third-party
apps; they do not replace user-level authorization (which must still
be enforced server-side per request).

---

### 📊 Entry Metadata

| #017 | Category: Authorization | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | ATZ-016 | |
| **Used by:** | ATZ-018, ATZ-022, ATZ-030 | |
| **Related:** | ATZ-016 Claims-Based, ATZ-018 JWT Claims, ATZ-022 Delegated Authorization | |

---

### 📘 Textbook Definition

OAuth 2.0 scopes are strings that define the authorized
operations a client application may perform using an access
token. Scopes are requested by the client, granted by the
resource owner (user consent) or server policy, and embedded
in the issued access token. Resource servers validate that
the token contains the required scope before fulfilling a
request. Scopes implement delegated authorization: they
represent the intersection of (user's permissions) AND
(client's requested capabilities). A scope never grants
more than the user possesses, but it can restrict the client
to less than the user's full permission set.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│          OAuth Scope Authorization Model               │
├────────────────────────────────────────────────────────┤
│                                                        │
│  User Alice has: read emails, send emails, delete emails│
│                                                        │
│  Third-party app requests: scope=read:emails           │
│  Alice consents to: read:emails only                   │
│                                                        │
│  Token issued with scope: ["read:emails"]              │
│                                                        │
│  API call: GET /api/messages                           │
│  Token scope includes read:emails → OK                 │
│                                                        │
│  API call: DELETE /api/messages/123                    │
│  Token scope does NOT include delete:emails → 403      │
│  Even though Alice has delete permission:              │
│  SCOPE limits the client, not the user                 │
│                                                        │
│  This is delegated authorization:                      │
│  App can do: INTERSECTION(Alice's perms, granted scopes)│
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - Spring Security OAuth2 scope enforcement**

```java
// Resource server: enforce scope requirements
@RestController
public class EmailController {

    @GetMapping("/api/emails")
    @PreAuthorize(
        "hasAuthority('SCOPE_read:emails')")
    public List<Email> listEmails() {
        // Spring Security maps OAuth scope to authority:
        // scope "read:emails" → SCOPE_read:emails
        return emailService.list();
    }

    @DeleteMapping("/api/emails/{id}")
    @PreAuthorize(
        "hasAuthority('SCOPE_delete:emails')")
    public void deleteEmail(@PathVariable Long id) {
        emailService.delete(id);
    }
}
```

**Example - BAD vs GOOD: over-broad scopes**

```
BAD: apps request * or all-access scope
  Client requests: scope=*   (all operations)
  Or:              scope=admin (admin-level access)
  
  User consents; app gets full account access.
  If app is malicious or compromised: full account damage.
  
  Rule: reject wildcard scopes in authorization server policy.
  Each scope must be explicit and meaningful.

GOOD: minimal necessary scopes with user-visible names
  scope=calendar:read   (Read your calendar events)
  scope=contacts:read   (Read your contact list)
  
  NOT scope=*
  NOT scope=admin
  NOT scope=full_access
  
  Each scope shows in the consent screen with clear
  description of what it allows. Users can revoke per-scope.
```

**Example - Scope design for an API**

```yaml
# API scope design principles:
# 1. Resource:action format (resource:verb)
# 2. Separate read and write scopes
# 3. Separate user and admin scopes

scopes:
  orders:read:     "View your orders"
  orders:write:    "Create and update orders"
  orders:delete:   "Delete orders"
  profile:read:    "View your profile information"
  profile:write:   "Update your profile"
  admin:users:     "Manage users (requires admin role)"
  
# Resource server validates:
# 1. Token has required scope (client-level check)
# 2. User has permission for this specific resource (row-level)
# Both checks required: scope alone is insufficient for
# object-level authorization (user:42 reading user:99's orders)
```

---

### ⚠️ Common Failure Modes

**Confusing scope check for user permission check:**

```
Mistake: "If the token has scope orders:read, the user can
          read any order."

Correct: scope orders:read means the APP is allowed to
         read orders. The server must STILL check:
         - Does user 42 own this order?
         - Is order 9999 in user 42's organization?

Code that fails:
  if (token.hasScope("orders:read")) {
      return orderRepo.findById(orderId); // IDOR BUG
      // Returns ANY order to ANY user with this scope
  }

Correct:
  if (token.hasScope("orders:read")) {
      return orderRepo.findByIdAndUserId(
          orderId, token.getSubject()); // user-owned only
  }
```

---

*Authorization category: ATZ | Entry: ATZ-017 | v5.0*