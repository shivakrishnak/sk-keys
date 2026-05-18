---
id: OAU-032
title: "OAuth Scopes in Practice"
category: OAuth 2.0 & OpenID Connect
tier: tier-2-networking-security
folder: OAU-oauth
difficulty: ★★☆
depends_on: OAU-008, OAU-011, OAU-019, OAU-023
used_by: OAU-028, OAU-036, OAU-045, OAU-050
related: OAU-011, OAU-019, OAU-023, OAU-027, OAU-028
tags:
  - security
  - oauth
  - scopes
  - authorization
  - api-design
status: complete
version: 5
layout: default
parent: "OAuth 2.0 & OpenID Connect"
grand_parent: "Technical Mastery"
nav_order: 32
permalink: /technical-mastery/oauth/oauth-scopes-in-practice/
---

⚡ TL;DR - OAuth scopes are coarse-grained permission strings
(not roles, not permissions) that the client requests and the
user consents to. The `action:resource` naming pattern is the
industry standard: `read:contacts`, `write:orders`, `delete:
files`. OIDC scopes (`openid`, `profile`, `email`) have fixed
meanings per spec. Key production concerns: incremental consent
(request scopes at the moment they are needed, not all upfront),
scope downgrade (AS may grant fewer scopes than requested),
and per-endpoint scope validation at the Resource Server
(don't validate only at the auth layer - validate at each API).

---

### 🔥 The Problem This Solves

**THE PERMISSION GRANULARITY PROBLEM:**

An API that accepts any valid token without checking scopes
lets any OAuth client do anything the user can do. But
clients should only have the minimum necessary permissions.
A "read your contacts" app should not be able to delete files.
OAuth scopes are the mechanism for clients to declare what
permissions they need and for users to grant (or deny) specific
subsets of those permissions. Correct scope design and validation
is the second layer of API authorization (after token validity).

---

### 📘 Textbook Definition

OAuth 2.0 scopes are strings that represent delegated permissions.
They appear in three places:

1. **Client registration**: The AS admin defines which scopes
   the client is allowed to request (`allowed_scopes` in client
   metadata). The client cannot request scopes not in this list.

2. **Authorization request**: The client includes `scope=...`
   in the `/authorize` request. The AS shows these scopes to
   the user on the consent screen.

3. **Granted access token**: The AS includes the granted scopes
   in the token response (`scope` field) and in the JWT `scope`
   claim. The AS may grant fewer scopes than requested
   (scope downgrade).

**Scope validation at the Resource Server** is the application's
responsibility. The RS must check that the token's scopes match
what the specific endpoint requires. Spring Security maps
`scope` claim to `SCOPE_xxx` authorities and enforces via
`@PreAuthorize`.

---

### ⏱️ Understand It in 30 Seconds

**The naming convention that scales:**

```
Pattern: action:resource  (colon-separated)

READ operations:   read:contacts, read:orders, read:profile
WRITE operations:  write:contacts, write:orders
DELETE operations: delete:files, delete:users
ADMIN operations:  admin:users, admin:billing

OIDC (fixed by spec):
  openid   → enables OIDC (required for ID token)
  profile  → name, picture, birthdate, locale
  email    → email, email_verified
  address  → address claim
  phone    → phone_number, phone_number_verified

Do NOT use:
  admin    ← too broad; breaks least-privilege
  full     ← meaningless to users
  all      ← never grant "everything" as one scope
```

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────────┐
│  SCOPE LIFECYCLE: REQUEST → CONSENT → GRANT → VALIDATE   │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  1. CLIENT REGISTRATION (one-time setup)                  │
│     Client registers with AS:                             │
│       allowed_scopes: "read:contacts write:contacts       │
│                        openid profile email"              │
│     Client cannot request beyond this list.               │
│                                                           │
│  2. AUTHORIZATION REQUEST                                 │
│     GET /authorize?                                       │
│       response_type=code                                  │
│       &client_id=contacts-app                             │
│       &scope=read:contacts+openid+profile                 │
│       &state=...&code_challenge=...                       │
│     AS validates requested scopes are subset of allowed.  │
│                                                           │
│  3. CONSENT SCREEN                                        │
│     User sees: "Contacts App wants to:                    │
│       - Read your contacts (read:contacts)                │
│       - Know who you are (openid, profile)"               │
│     User approves or denies.                              │
│                                                           │
│  4. TOKEN ISSUANCE                                        │
│     Token response includes:                              │
│       scope: "read:contacts openid profile"               │
│     JWT payload:                                          │
│       "scope": "read:contacts openid profile"             │
│     NOTE: scope may be less than requested (downgrade).   │
│                                                           │
│  5. RESOURCE SERVER VALIDATION                            │
│     Per-endpoint:                                         │
│     GET /contacts → requires read:contacts                │
│     POST /contacts → requires write:contacts              │
│     Token has read:contacts but not write:contacts:       │
│       → POST returns 403 insufficient_scope               │
│                                                           │
│  SCOPE DOWNGRADE:                                         │
│     Client requested: read:contacts write:contacts        │
│     User approved only: read:contacts                     │
│     Granted token scope: read:contacts                    │
│     Client MUST check granted scope before attempting     │
│     operations that require write:contacts.               │
│                                                           │
│  INCREMENTAL CONSENT:                                     │
│     App start: request openid profile (not write scopes)  │
│     User opens "export" feature: request write:files      │
│     → smaller consent surface at startup                  │
│     → user understands why each scope is needed           │
└──────────────────────────────────────────────────────────┘
```

```mermaid
flowchart TD
  REG[Client Registration\nallowed_scopes defined] --> REQ

  REQ[/authorize: scope=read:X openid/] --> CONSENT[Consent Screen\n"Read your X, Know who you are"]
  CONSENT -->|User approves| GRANT[Token issued\nscope=read:X openid]
  CONSENT -->|User denies| DENY[access_denied redirect]

  GRANT --> RS[Resource Server Endpoint]
  RS --> CHECK{Token has\nrequired scope?}
  CHECK -->|read:X → GET /x| ALLOW[200 OK]
  CHECK -->|Missing write:X → POST /x| REJECT[403 insufficient_scope]

  GRANT --> DOWNGRADE[Client checks\ngranted_scope vs requested]
  DOWNGRADE -->|write scope granted| ENABLE[Enable write UI feature]
  DOWNGRADE -->|write scope NOT granted| DISABLE[Disable write UI feature]
```

---

### 💻 Code Example

**Example 1 - BAD then GOOD: API scope design:**

```java
// BAD: Single "admin" scope - violates least privilege
// Any client with "admin" can do everything
// User consent is meaningless ("full access")

// POST /admin/users/delete (scope: admin)
// POST /admin/billing/refund (scope: admin)
// GET /admin/reports (scope: admin)
// All require same "admin" scope = zero granularity
```

```java
// GOOD: Granular action:resource scope design
// WHY: User can grant exactly what the client needs.
//   Billing app requests write:billing only; no user data.
//   Analytics app requests read:reports only; no write.

@RestController
@RequestMapping("/api")
public class ApiController {

    // Read-only: request read:contacts at authorization
    @GetMapping("/contacts")
    @PreAuthorize("hasAuthority('SCOPE_read:contacts')")
    public List<Contact> getContacts() { ... }

    // Write: request write:contacts - separate consent item
    @PostMapping("/contacts")
    @PreAuthorize("hasAuthority('SCOPE_write:contacts')")
    public Contact createContact(...) { ... }

    // Admin: only request admin:contacts for admin UIs
    // Never bundle with regular user-facing scopes
    @DeleteMapping("/contacts/{id}")
    @PreAuthorize("hasAuthority('SCOPE_admin:contacts')")
    public void deleteContact(@PathVariable String id) { ... }
}

// Scope hierarchy (documentation-only, not enforced by OAuth):
// admin:contacts implies read:contacts + write:contacts
// But: the RS must check EACH scope explicitly.
// Do NOT assume "write implies read" without explicit check.
```

**Example 2 - Incremental consent implementation:**

```python
# Pattern: Request scopes just-in-time, not all upfront
# Reduces consent screen friction at initial login

SCOPES_AT_STARTUP = "openid profile email"
SCOPES_FOR_EXPORT = "read:data write:files"
SCOPES_FOR_BILLING = "read:billing"

def get_initial_auth_url(state: str, code_verifier: str):
    """Initial login: only request identity scopes."""
    return build_auth_url(
        scope=SCOPES_AT_STARTUP,  # No data scopes yet
        state=state,
        code_challenge=pkce_challenge(code_verifier),
    )

def request_export_permission(
    state: str,
    code_verifier: str,
    current_tokens: dict,
):
    """
    User clicks Export: request additional scopes.
    If already granted (cached), no consent screen shown.
    If not granted, user sees focused consent screen.
    """
    # Check if we already have the export scopes
    current_scope = set(
        current_tokens.get("scope", "").split()
    )
    export_scopes = set(SCOPES_FOR_EXPORT.split())

    if export_scopes.issubset(current_scope):
        # Already have export permission - no auth needed
        return None  # Proceed directly

    # Need to request additional scopes
    # Include prompt=consent to show consent screen again
    return build_auth_url(
        scope=f"{SCOPES_AT_STARTUP} {SCOPES_FOR_EXPORT}",
        state=state,
        code_challenge=pkce_challenge(code_verifier),
        prompt="consent",  # Show consent for new scopes
    )

def handle_scope_downgrade(
    requested_scopes: str,
    granted_scopes: str,
) -> dict:
    """
    After token received, determine what features to enable.
    AS may grant fewer scopes than requested.
    """
    requested = set(requested_scopes.split())
    granted = set(granted_scopes.split())
    downgraded = requested - granted  # Not granted

    features_enabled = {}
    features_enabled['read_contacts'] = (
        'read:contacts' in granted
    )
    features_enabled['write_contacts'] = (
        'write:contacts' in granted
    )
    features_enabled['export'] = (
        'write:files' in granted
    )

    if downgraded:
        # Log which scopes were not granted (for UX decisions)
        import logging
        logging.info(
            "Scope downgrade: requested=%s, not_granted=%s",
            requested_scopes, downgraded
        )

    return features_enabled
```

---

### ⚖️ Comparison Table

| Scope Granularity | Consent UX | Security Posture | API Design Effort |
|---|---|---|---|
| **Single `admin`** | One item | Poor (over-privilege) | Low |
| **`read` / `write`** | Two items | Moderate | Low |
| **`read:resource` / `write:resource`** | Per-resource items | Good | Medium |
| **`action:resource` + incremental** | Contextual, just-in-time | Excellent | High |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Scopes and roles serve the same purpose | Scopes are delegated permissions: what a CLIENT is allowed to do on behalf of the USER. Roles are user attributes: what the USER is allowed to do. An admin user granting access to a contacts app gives it `read:contacts` scope, not the user's admin role. The RS uses both: scope for what the client can do, roles/claims for what the user is allowed to access within that scope. |
| If the user approved a scope, the AS must grant it | The AS can and sometimes will grant fewer scopes than the user approved. AS policies (e.g., scope whitelisting per client, dynamic scope adjustment based on risk) can result in scope downgrade. Clients must always check the granted scope in the token response, not assume they received everything they requested. |
| OIDC scopes (`openid`, `profile`) work the same as custom scopes | OIDC scopes have spec-defined semantics: `openid` is required to enable OIDC and receive an ID token; `profile` returns name/picture/birthdate; `email` returns email/email_verified. Custom scopes (`read:contacts`) have no spec-defined semantics - their meaning is entirely up to the AS and RS operators. Never mix OIDC scope names with custom scope names (e.g., never create a custom `profile` scope). |
| Scope validation at the gateway is sufficient | An API gateway can validate that the token has required scopes before forwarding to the downstream service. But if the downstream service also accepts requests from internal services that bypass the gateway, it must also validate scopes. Defense in depth: validate scopes at every service boundary, not only at the entry point. |

---

### 🚨 Failure Modes & Diagnosis

**Scope Downgrade Not Handled - Feature Available Without Permission**

**Symptom:**
User reports they can see an "Export" button but clicking it
returns 403. Investigation reveals the export scope was not
granted (user denied it on consent screen) but the UI still
shows the button because the app assumed all requested scopes
were granted.

**Root Cause:**
App requests `read:data write:files` at authorization. User
only grants `read:data`. App does not parse the granted `scope`
from the token response. UI is rendered based on "what we
requested" not "what was granted."

**Fix:**
Always parse the granted `scope` field from the token response
(or from the JWT payload) and use it to conditionally show/hide
features that require specific scopes. Disable or hide features
for scopes that were not granted rather than showing them and
failing on use.

---

**Verbose Consent Screen from Too Many Upfront Scopes**

**Symptom:**
User feedback: "The app asked for access to everything on the
first login. I wasn't sure what to do so I cancelled."
Conversion rates on the OAuth consent screen are low (40%).

**Root Cause:**
App requests 15 scopes at initial login: `openid profile email
read:contacts write:contacts read:calendar write:calendar
read:files write:files read:billing admin:billing ...`

**Fix:**
Implement incremental consent. Request only the minimum scopes
at startup (`openid profile email`). Request additional scopes
when the user triggers a feature that requires them. Show
context-specific consent: "To export your contacts, we need
access to write files." This improves consent screen conversion
from ~40% to ~80%+ in production applications.

---

### 🔗 Related Keywords

**Prerequisites:**
- `Scope` - the foundational concept
- `Consent Screen` - where users approve scopes

**Builds On:**
- `OAuth 2.0 with Spring Security` - scope-to-authority mapping
- `OAuth Error Responses` - insufficient_scope (403) handling

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ NAMING       │ action:resource pattern                    │
│ CONVENTION   │ read:contacts, write:orders, admin:users   │
├──────────────┼───────────────────────────────────────────┤
│ OIDC SCOPES  │ openid (required), profile, email,         │
│ (spec-fixed) │ address, phone                             │
├──────────────┼───────────────────────────────────────────┤
│ DOWNGRADE    │ Granted scope may be < requested scope.    │
│              │ Always check token response "scope" field. │
├──────────────┼───────────────────────────────────────────┤
│ INCREMENTAL  │ Request scopes at point-of-need, not all   │
│ CONSENT      │ upfront. Better UX + fewer consent denials.│
├──────────────┼───────────────────────────────────────────┤
│ VALIDATION   │ Validate at each endpoint, not only at GW. │
│              │ 403 insufficient_scope = never retry same  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Scopes = delegated permission strings.    │
│              │  Request least needed. Check what's granted│
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Use `action:resource` naming convention for custom scopes.
   Never use `admin`, `full`, or `all` as a single scope -
   these are security anti-patterns that over-privilege clients.

2. Always check the granted scope in the token response, not
   just the requested scope. Scope downgrade (user grants fewer
   than requested) is a normal AS behavior and must be handled
   by conditionally enabling/disabling features.

3. Incremental consent: request only identity scopes at startup.
   Request data/action scopes when the user first triggers the
   feature. This maximizes consent approval rates and minimizes
   privacy exposure.
