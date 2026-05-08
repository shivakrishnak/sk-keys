---
layout: default
parent: "Security"
grand_parent: "Technical Dictionary"
nav_order: 8
id: SEC-008
title: Authentication vs Authorization
category: Security
tier: tier-2-networking-security
folder: SEC-security
difficulty: ★☆☆
depends_on: SEC-001
used_by: SEC-003, SEC-013, SEC-014, SEC-015
related: SEC-013, SEC-014, SEC-034, SEC-004
tags:
  - security
  - foundational
  - identity
  - access-control
status: complete
version: 1
---

# SEC-008 - Authentication vs Authorization

⚡ **TL;DR** - Authentication proves who you are; authorization decides what you are allowed to do.

| Attribute  | Details                                                                                                                                                   |
| ---------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Depends on | [[SEC-001 - CIA Triad (Confidentiality, Integrity, Availability)]]                                                                                        |
| Used by    | [[SEC-003 - IAAA]], [[SEC-013 - Session-Based Authentication]], [[SEC-014 - Token-Based Authentication]], [[SEC-015 - Access Token]]                      |
| Related    | [[SEC-013 - Session-Based Authentication]], [[SEC-014 - Token-Based Authentication]], [[SEC-034 - OAuth 2.0]], [[SEC-004 - Principle of Least Privilege]] |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** Early applications fused identity and access into a single check: if you knew the password, you could do everything. A single credential unlocked the entire system - read, write, delete, administer. There was no concept of partial access or role-based restriction. One stolen password meant total system compromise.

**THE BREAKING POINT:** As systems grew to serve multiple users with different roles, developers began hardcoding user-specific rules into application logic: `if username == "admin" then allow_delete()`. This produced unmaintainable spaghetti. When a contractor needed read-only access, developers modified code. When an employee was terminated, access removal required finding and removing every hardcoded reference.

**THE INVENTION MOMENT:** Multi-user operating systems (UNIX, late 1960s) introduced the separation of identity (who you are) from permissions (what you can do). This separation enabled fine-grained access control without rewriting application logic for every new user or role.

**EVOLUTION:** The separation has deepened over decades. OAuth 2.0 separates authentication (handled by an identity provider) from authorization (handled by resource servers using tokens). Modern systems like AWS IAM, Kubernetes RBAC, and OPA (Open Policy Agent) treat authorization as a dedicated, independent layer that can be updated without touching application code.

---

### 📘 Textbook Definition

**Authentication** is the process of verifying that a claimed identity is genuine. It answers the question: "Are you who you say you are?" Authentication relies on one or more factors: something you know (password), something you have (hardware token), or something you are (biometric).

**Authorization** is the process of determining what an authenticated identity is permitted to do. It answers the question: "What are you allowed to do?" Authorization policies map identities (or roles) to permitted resources and actions.

The two processes are sequentially dependent: authorization is meaningless without prior authentication. However, they are implemented and managed independently.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Authentication confirms identity; authorization enforces permissions - you must prove who you are before the system decides what you can access.

> Think of a conference: showing your badge to enter (Authentication - "you are a registered attendee") is separate from which sessions your badge lets you into (Authorization - "you have VIP access to the speakers' dinner").

**One insight:** Many of the most serious security vulnerabilities come from skipping authorization even after successful authentication. A logged-in user who can access another user's resources by changing an ID in the URL is an "Insecure Direct Object Reference" - an authorization failure, not an authentication failure. Authenticating well is not enough.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Authentication must precede authorization - you cannot grant permissions to an unknown entity.
2. Authentication and authorization are independent concerns - changing who can log in does not automatically change what they can do.
3. Authorization decisions must be enforced at the resource, not the UI - hiding a button is not authorization.

**DERIVED DESIGN:**

- Authentication: credential verification (password hash comparison, certificate validation, OTP check)
- Session/token issuance: a persistent proof of authenticated identity
- Authorization: policy evaluation against the authenticated identity and the requested resource
- Enforcement: reject unauthenticated requests before processing; reject unauthorized requests after authentication

**THE TRADE-OFFS:**

- **Gain:** Separating the concerns allows independent scaling, auditing, and updating of each layer.
- **Cost:** More components (identity provider, policy engine, token service) means more failure points and integration complexity.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

- **Essential:** The need to verify identity and then determine permissions is inherent to any multi-user system sharing protected resources.
- **Accidental:** JWT libraries, OAuth flows, SAML assertions, and OIDC discovery endpoints are implementation choices driven by ecosystem standardization - the underlying need is simple.

---

### 🧪 Thought Experiment

**SETUP:** A healthcare portal serves patients, nurses, and administrators. Each has different data access needs.

**WHAT HAPPENS WITHOUT THE DISTINCTION:** Every user who logs in with a valid password gets the same access. A patient can read another patient's records. A nurse can delete billing entries. An administrator can export the entire database. Privilege separation requires copying the same code check (`if username == "admin"`) into every endpoint - and attackers only need to find one endpoint where the developer forgot.

**WHAT HAPPENS WITH THE DISTINCTION:** Authentication verifies the user's identity. Authorization, driven by RBAC policies, determines that patients can read only their own records, nurses can read and write clinical notes for assigned patients, and administrators can manage user accounts but not clinical data. A policy change (e.g., nurses can now order lab tests) updates the authorization policy - no application code changes.

**THE INSIGHT:** Authentication is a binary gate (in or out). Authorization is a fine-grained lattice of permissions that should be centrally managed, independently auditable, and enforced as close to the resource as possible.

---

### 🧠 Mental Model / Analogy

> Think of a hotel: checking in at the front desk and receiving a key card is Authentication (you proved your reservation; the hotel confirms your identity). The key card only opening rooms 301 and the gym - not the penthouse or the kitchen - is Authorization (your identity grants specific access rights).

Element mapping:

- Checking in with ID and reservation → Authentication (proving identity)
- Key card encoding → Token issuance (persistent proof of authentication)
- Doors that only open for the right key card → Authorization enforcement (resource checks identity claims against policy)
- Hotel manager's master key → Admin role (broad authorization scope)

Where this analogy breaks down: hotel key cards encode access directly on the card; modern authorization systems often evaluate policy at the resource at runtime, allowing policies to change without re-issuing credentials.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Authentication is proving who you are - like showing your ID. Authorization is what you're allowed to do once inside - like which rooms your key opens. Both happen every time you use a secure system.

**Level 2 - How to use it (junior developer):**
Always check authentication first (is there a valid session/token?), then authorization (does this identity have permission to perform this action on this resource?). Never skip the authorization check just because the user is logged in. A logged-in user should only access their own resources unless explicitly granted broader access.

**Level 3 - How it works (mid-level engineer):**
Authentication typically produces an identity token (JWT, session cookie) containing claims (user ID, roles, expiry). Authorization is a policy evaluation: given the claims in the token, the requested resource, and the requested action, does the policy permit it? The policy can be role-based (RBAC), attribute-based (ABAC), or relationship-based (ReBAC). Enforcement must happen server-side - client-side checks are UI convenience only.

**Level 4 - Why it was designed this way (senior/staff):**
Separating AuthN and AuthZ unlocks independent evolution of each concern. OAuth 2.0 delegates authentication to an identity provider (Google, Okta) while resource servers make authorization decisions using access tokens. This enables SSO, federation, and centralized identity management without coupling authorization policies to the identity store. Modern systems use a dedicated policy engine (OPA, Casbin, AWS IAM) so authorization rules are auditable, testable, and deployable independently of application code. This separation also enables ABAC, where authorization decisions depend on runtime attributes (time of day, user location, resource sensitivity) rather than static role assignments.

**Expert Thinking Cues:**

- If an authorization bug allows user A to access user B's data by changing an ID, that is an Insecure Direct Object Reference - one of the most common web vulnerabilities.
- The most common authorization anti-pattern: checking permissions in the UI (hiding buttons) but not in the API.
- Confused deputy attacks exploit the distinction: a service with elevated authorization is tricked by a lower-privilege user into performing an action on their behalf.

---

### ⚙️ How It Works (Mechanism)

**Authentication flow:**

1. Client presents credentials (password, certificate, OTP, biometric).
2. Authentication service verifies credentials against stored secrets (bcrypt hash, certificate CA, TOTP algorithm).
3. On success, issues a session cookie or signed token (JWT, opaque token).
4. All subsequent requests carry the session/token as proof of authenticated identity.

**Authorization flow:**

1. Request arrives at resource server with session/token.
2. Resource server validates token (signature, expiry, issuer).
3. Extracts identity claims (user ID, roles, attributes).
4. Evaluates policy: `ALLOW if subject.role == "doctor" AND resource.owner == subject.id`.
5. On ALLOW, processes request. On DENY, returns `403 Forbidden`.

**Enforcement points:**

- API gateway (coarse-grained): is any valid token present?
- Service layer (fine-grained): does this token permit this action on this resource?
- Data layer (row-level): does this query filter by identity? (Row-Level Security in PostgreSQL)

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
Client                Auth Service           Resource Server
  |                       |                       |
  |--POST /login--------->|                       |
  |  (credentials)        |                       |
  |                       |--verify credentials   |
  |                       |--issue JWT            |
  |<--200 OK + JWT--------|                       |
  |                                               |
  |--GET /patients/42  (JWT in header)----------->|
  |                       <- YOU ARE HERE         |
  |                                   |--validate JWT
  |                                   |--check: user.role==nurse
  |                                   |--check: patient 42 assigned
  |<--200 OK + patient data-----------|
```

**FAILURE PATH:**

- No token → `401 Unauthorized` (authentication failed)
- Invalid/expired token → `401 Unauthorized`
- Valid token, insufficient permissions → `403 Forbidden` (authorization failed)
- Valid token, authorization check skipped → silent data breach (IDOR vulnerability)

**WHAT CHANGES AT SCALE:**
At scale, authentication is offloaded to a dedicated identity provider (Okta, Auth0, Cognito) with SSO. Authorization policies are centralized in a policy engine (OPA, AWS IAM) evaluated per-request. Token validation must be fast (local signature verification, not a remote call), so JWTs with embedded claims dominate over opaque tokens that require a lookup.

---

### 💻 Code Example

**BAD - Authorization check missing or client-side only:**

```python
@app.route("/patients/<patient_id>")
def get_patient(patient_id):
    # Only checks if logged in, not if authorized for THIS patient
    if not current_user.is_authenticated:
        return 401
    # Missing: does current_user have access to patient_id?
    return db.get_patient(patient_id)  # IDOR vulnerability
```

**GOOD - Explicit server-side authorization check:**

```python
@app.route("/patients/<patient_id>")
@require_authentication        # Step 1: must be logged in
def get_patient(patient_id):
    # Step 2: must be authorized for THIS specific resource
    patient = db.get_patient(patient_id)
    if patient is None:
        abort(404)

    # Authorization: nurse sees only assigned patients
    if current_user.role == "nurse":
        if patient_id not in current_user.assigned_patient_ids:
            abort(403)  # Authenticated but not authorized

    # Authorization: patient sees only own record
    elif current_user.role == "patient":
        if patient.patient_user_id != current_user.id:
            abort(403)

    audit_log.record(current_user.id, "READ", patient_id)
    return patient.to_json(scope=current_user.role)
```

**How to test / verify correctness:**

- Send request with no token → expect `401`
- Send request with valid token for user A, requesting user B's resource → expect `403`
- Send request with valid token for user A, requesting own resource → expect `200`

---

### ⚖️ Comparison Table

| Aspect                         | Authentication           | Authorization                       |
| ------------------------------ | ------------------------ | ----------------------------------- |
| Question answered              | "Who are you?"           | "What can you do?"                  |
| Happens when                   | At login / session start | On every resource request           |
| HTTP response on failure       | `401 Unauthorized`       | `403 Forbidden`                     |
| Managed by                     | Identity Provider (IdP)  | Policy Engine / Resource Server     |
| Changes when                   | User credentials change  | Roles, permissions, policies change |
| Can succeed without the other? | Yes (anonymous auth)     | No (must know identity first)       |

| Protocol/Standard     | Primary Role                             |
| --------------------- | ---------------------------------------- |
| OAuth 2.0             | Authorization framework                  |
| OpenID Connect (OIDC) | Authentication layer on top of OAuth 2.0 |
| SAML 2.0              | Authentication + attribute assertion     |
| JWT                   | Token format used for both               |
| RBAC / ABAC           | Authorization policy models              |

---

### ⚠️ Common Misconceptions

| Misconception                                     | Reality                                                                                                                        |
| ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| "If a user is logged in, they're authorized"      | Authentication and authorization are independent; a logged-in user may not have permission for a specific resource             |
| "OAuth 2.0 is for authentication"                 | OAuth 2.0 is an authorization framework; OpenID Connect (OIDC) adds authentication on top of it                                |
| "Hiding a button means the endpoint is protected" | UI-level hiding is not authorization; the API endpoint must enforce permissions server-side                                    |
| "401 and 403 are interchangeable"                 | 401 means not authenticated (no or invalid credentials); 403 means authenticated but not authorized (insufficient permissions) |
| "SSO solves authorization"                        | SSO centralizes authentication; authorization policies are still the responsibility of each resource server                    |
| "HTTPS makes authorization unnecessary"           | HTTPS provides transport security; it does not determine who can access what resource                                          |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1 - Insecure Direct Object Reference (IDOR)**

- **Symptom:** User A can access User B's data by changing a numeric ID in the URL (e.g., `/orders/12345` → `/orders/12346`).
- **Root Cause:** Authorization check only verifies authentication, not resource ownership.
- **Diagnostic:**

```bash
# Test: authenticated as user A, access user B's resource
curl -H "Authorization: Bearer <user_A_token>" \
  https://api.example.com/orders/USER_B_ORDER_ID
# Expect: 403. If 200 is returned, IDOR vulnerability confirmed.
```

- **Fix:** Add ownership/role check on every resource endpoint, not just at the route level.
- **Prevention:** Automated IDOR tests in CI pipeline; use indirect references (UUIDs not sequential IDs); enforce row-level security in the database.

**Mode 2 - Privilege Escalation**

- **Symptom:** A low-privilege user performs administrative actions (deleting accounts, accessing audit logs, modifying other users' data).
- **Root Cause:** Authorization check uses a role claim that the user can modify (e.g., JWT with role stored in a modifiable cookie, or no server-side role verification).
- **Diagnostic:**

```bash
# Decode JWT payload to check if role is in client-controlled token
echo "<jwt_payload>" | base64 -d | python3 -m json.tool
# Check if role field can be modified client-side
```

- **Fix:** Never trust client-supplied role claims without server-side verification against a trusted store. Sign JWTs with a secret only the server knows.
- **Prevention:** Centralize authorization in a server-side policy engine; never include authorization decisions in client-modifiable tokens.

**Mode 3 - Authorization Bypass via Parameter Tampering**

- **Symptom:** Changing a query parameter (`?admin=true`) or HTTP header grants elevated access.
- **Root Cause:** Application reads access level from request parameters rather than deriving it from the verified token.
- **Diagnostic:**

```bash
curl -H "Authorization: Bearer <regular_user_token>" \
  "https://api.example.com/admin/users?admin=true"
# Also test: adding X-Admin: true header
```

- **Fix:** Derive authorization scope exclusively from the verified token claims, never from request parameters.
- **Prevention:** Code review policy: reject any PR where access level is determined from a request parameter.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[SEC-001 - CIA Triad (Confidentiality, Integrity, Availability)]] - authentication enforces Confidentiality; authorization enforces Confidentiality and Integrity
- What HTTP request/response headers are
- What a session and a cookie are at a high level

**Builds On This (learn these next):**

- [[SEC-013 - Session-Based Authentication]] - one implementation of the authentication step
- [[SEC-014 - Token-Based Authentication]] - modern stateless authentication with embedded claims
- [[SEC-034 - OAuth 2.0]] - the industry-standard authorization delegation framework
- [[SEC-004 - Principle of Least Privilege]] - the authorization design principle that minimizes permission scope

**Alternatives / Comparisons:**

- RBAC vs ABAC - two authorization policy models with different trade-offs in flexibility and complexity
- API Keys - a simple combined authentication+coarse authorization mechanism for machine-to-machine access
- mTLS - mutual authentication using certificates, often replacing token-based auth in service meshes

---

### 📌 Quick Reference Card

```
+----------------------------------------------------------+
| WHAT IT IS   | AuthN = who you are; AuthZ = what you do   |
| PROBLEM      | One credential gave total system access     |
| KEY INSIGHT  | Authorization must be checked server-side   |
|              | on every resource, every request            |
| USE WHEN     | Any system with multiple users or roles     |
| AVOID WHEN   | N/A - always separate these two concerns    |
| TRADE-OFF    | More components; independent auditability   |
| ONE-LINER    | Prove identity first; enforce policy second |
| NEXT EXPLORE | SEC-034 OAuth 2.0, SEC-013 Session Auth     |
+----------------------------------------------------------+
```

**If you remember only 3 things:**

1. Authentication verifies identity (`401` on failure); authorization verifies permissions (`403` on failure).
2. A logged-in user is not automatically authorized for every resource - check per-resource, server-side.
3. Hiding UI elements is not authorization - the API endpoint must enforce permissions independently.

**Interview one-liner:** "Authentication answers 'who are you?' and results in a verified identity; authorization answers 'what are you allowed to do?' and must be enforced server-side on every request - the most common bug is skipping the authorization check for an authenticated user."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Verification of identity and enforcement of permissions are two separable, independently evolvable concerns. Coupling them creates systems where a single compromise grants total access and where permission changes require touching authentication code.

**Where else this pattern appears:**

- **Operating systems:** `login` authenticates (who are you?); `chmod` and `sudo` policies authorize (what can you do?)
- **Physical access:** Badge scan at the entrance authenticates; door-level readers authorize access to specific zones
- **Healthcare systems:** Doctor login authenticates; patient consent records and role assignments authorize which records the doctor may view

---

### 💡 The Surprising Truth

The most dangerous authorization failures are not in admin panels - they are in user-facing APIs that pass resource IDs directly from the client. The OWASP Top 10 has listed "Broken Object Level Authorization" (BOLA/IDOR) as the #1 API security risk for multiple years. The attack requires no special tools: an attacker simply increments an ID in a URL. A majority of reported bug bounty findings are BOLA vulnerabilities in systems that had robust authentication but forgot to check whether the authenticated user was actually permitted to access the specific object they requested.

---

### 🧠 Think About This Before We Continue

1. **[D - Root Cause]** A user calls `GET /invoices/9871` and receives an invoice belonging to another company. Authentication succeeded. What went wrong, and at which layer of the system should this have been caught?
   _Hint:_ Think about where authorization policy is evaluated and what claim in the token should have been checked against the invoice's `company_id` field.

2. **[A - System Interaction]** An API gateway validates JWT tokens and passes requests downstream. A microservice trusts the gateway and skips its own authorization check. What happens if the gateway is bypassed by an internal caller? Which security principle does this violate?
   _Hint:_ Look up "defense in depth" and "confused deputy problem" - consider what happens when authorization is enforced only at the perimeter.

3. **[C - Design Trade-off]** In a microservices architecture, should each service perform its own authorization check, or should a centralized authorization service make all decisions? What are the latency, consistency, and failure mode implications of each approach?
   _Hint:_ Consider what happens if the centralized service is down (availability vs. security), and how eventual consistency in policy propagation affects security guarantees.
