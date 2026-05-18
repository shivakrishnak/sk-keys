---
id: SEC-008
title: "Authentication vs Authorization vs Auditing"
category: "Security"
tier: tier-2-networking-security
folder: SEC-security
difficulty: ★☆☆
depends_on: SEC-001, SEC-002, SEC-007
used_by: SEC-009, SEC-028, SEC-029, SEC-036, SEC-037
related: SEC-001, SEC-002, SEC-007, SEC-009, SEC-028, SEC-029, SEC-036, SEC-037, SEC-021
tags:
  - security
  - authentication
  - authorization
  - auditing
  - aaa
  - access-control
status: complete
version: 4
layout: default
parent: "Security"
grand_parent: "Technical Mastery"
nav_order: 8
permalink: /technical-mastery/sec/authentication-vs-authorization-vs-auditing/
---

⚡ TL;DR - The AAA model defines three distinct security
functions: Authentication (who are you? - verify identity),
Authorization (what are you allowed to do? - verify
permission for this specific action), Auditing (what did
you do? - tamper-evident record of every action). These
are often confused and often implemented incorrectly.
The critical distinction: authentication confirms identity,
but identity alone does not imply permission. Authenticated
user X is allowed to read their own profile - but are
they allowed to read user Y's profile? That is authorization.
IDOR (Insecure Direct Object Reference) - the #1 OWASP
2021 finding - is almost always "authentication without
authorization." Auditing enables detection (what happened?),
incident response (what did the attacker access?), and
regulatory compliance (prove who accessed what when).
All three are required for a secure system. Missing any
one creates a critical gap.

---

| #008 | Category: Security | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Security Problem, CIA Triad, Defense in Depth | |
| **Used by:** | Password Storage, JWT, OAuth 2.0, CORS, Session Security | |
| **Related:** | CIA Triad, Defense in Depth, JWT, OAuth, IDOR, Least Privilege | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT CLEAR AAA DISTINCTION:**
Developer builds an API. Adds authentication: every endpoint
requires a valid JWT. Feels secure. Ships it.
Security researcher submits bug bounty: "Your API returns
any user's order history when I provide my own valid JWT
and change the user_id parameter. I accessed 40,000 users'
order histories."
Developer: "But I added authentication - you need a valid
token."
Researcher: "Yes - authentication checks you have a token.
You never check whether the token permits access to THAT
SPECIFIC user_id."
This is the authentication/authorization confusion that
makes IDOR the #1 finding in security audits. Knowing the
distinction is the prerequisite to implementing both correctly.

---

### 📘 Textbook Definition

**Authentication (AuthN) - "Who are you?"**
The process of verifying that an entity is who they claim
to be. Mechanisms: password + username (knowledge factor),
OTP/TOTP (possession factor), biometric (inherence factor),
certificate (cryptographic identity). Outcome: an identity
claim is confirmed or rejected. Post-authentication: the
system knows the identity of the requester.

**Authorization (AuthZ) - "What are you allowed to do?"**
The process of verifying that an authenticated identity
has permission to perform a specific action on a specific
resource. Requires: an authenticated identity (who) + a
resource (what) + an action (read/write/delete/admin).
Mechanism: RBAC (Role-Based Access Control), ABAC
(Attribute-Based Access Control), ACL (Access Control List).
Authorization must be checked for EVERY action, not just
at login. An authenticated session's permissions can change
(role revoked, resource ownership changed).

**Auditing (Accounting) - "What did you do?"**
A tamper-evident record of all authentication events,
authorization decisions, and actions taken by authenticated
users. Audit logs must be: complete (no gaps), accurate
(timestamps, identity, action, resource), immutable
(cannot be deleted or modified by anyone including admins),
and searchable (forensically useful). Audit logs enable:
incident response (what did the attacker access?),
compliance (prove PCI-DSS/GDPR requirements), anomaly
detection (user accessed 10,000 records at 2 AM - alert).

**The AAA Stack:**
```
Request arrives → Authentication → Authorization → Action
                       |                |
                  "Who are you?"    "May you do this?"
                       ↓                ↓
                  Identity          Permission
                   stored            checked
                       ↓                ↓
                  Audit: identity + permission result + action
```

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Authentication = verify identity (who you are).
Authorization = verify permission (what you may do).
Auditing = record what happened (evidence, detection).
All three are required; missing authorization is IDOR (#1 OWASP).

**One analogy:**
> Hotel key card:
> Authentication: card is valid (magnetic strip passes reader)
> Authorization: card is authorized for ROOM 304 specifically
>   (not just any room, not the penthouse)
> Auditing: door log records card ID, room, timestamp
> An authentication-only check: any valid card opens any room.
> That is the developer who checks "valid JWT" but not
> "this JWT is authorized for this specific resource."

---

### 🔩 First Principles Explanation

**Why authorization must be checked per-request, not just at login:**

```
SCENARIO: User logs in at 9 AM. Gets valid session token.
  Role at login: "standard user"
  Session expiry: 24 hours

11 AM: Admin revokes user's access (security incident).
  Action taken in identity provider: role removed.

2 PM: User uses their still-valid 24-hour session token.
  Authentication check: token is cryptographically valid.
    (Token was issued legitimately, signature checks out)
  WRONG authorization check: "user is authenticated = allowed"
  CORRECT authorization check: "does this identity currently
    have permission for this specific action?"
    → Check current role from identity store.
    → Role was revoked at 11 AM.
    → Action: 403 Forbidden.

IMPLEMENTATION IMPACT:
  Stateless JWT: token validity ≠ current permissions.
    JWT contains claims (including roles) encoded AT ISSUE TIME.
    If roles change: JWT still contains old claims until expiry.
    Solution: short JWT expiry (15-60 min) + token refresh.
    OR: use opaque tokens (check current permissions on every call).

  Stateful sessions: session revocation propagates instantly.
    Session store lookup on every request = current permission check.
    Cost: session store lookup per request (Redis lookup ~1ms).

LESSON: Authorization is not "is this user logged in?"
  It is "does this user CURRENTLY have permission for
  EXACTLY this action on EXACTLY this resource?"
  Those are very different questions.
```

---

### 🧪 Thought Experiment

**SCENARIO: What does each of A/AuthN/AuthZ/Audit catch?**

```
ATTACK: Disgruntled employee (valid credentials) 
        accesses colleague's private messages over 2 weeks,
        then exports customer database to personal email.

AUTHENTICATION check (at login):
  Valid credentials → authenticated. PASSES.
  (Attack succeeds through authentication - credentials are valid)

AUTHORIZATION check (per-request):
  Employee's role: "standard developer"
  Action: read private messages of user_id 456 (colleague)
  Authorization: developer role NOT authorized for other users'
    private messages. → 403 Forbidden.
  IF authorization was implemented: attack stopped at step 1.

  Action: SELECT * FROM customers (full export)
  Authorization: developer role authorized for SELECT on customers
    table (for debugging purposes). → ALLOWED.
  Authorization gap: export privilege too broad.
  FIX: Principle of Least Privilege - developers need
    SELECT on specific test data, not all customer records.

AUDITING (if authorization wasn't enough):
  Week 1: employee accesses 200 private message pairs (abnormal)
  Audit log exists: every access recorded.
  SIEM anomaly detection: 200 private message accesses in 1 day,
    by someone whose role doesn't normally access this data.
  → Alert to security team. Investigation begins.

  Employee sends 500MB email to personal Gmail.
  DLP rule: large email to external personal domain → alert.
  Audit log: email send event recorded with metadata.
  → Immediate response: account suspended, forensics begin.

LESSON: Authentication fails (valid credentials).
  Authorization WOULD have stopped private message access.
  Auditing detected the customer data export.
  All three layers are necessary because each catches
  what the other does not.
```

---

### 🧠 Mental Model / Analogy

> Authentication is the bouncer checking your ID.
> Authorization is the VIP list checking you're on it
> (and which areas you can access: general admission,
> VIP lounge, backstage).
> Auditing is the security camera + incident log that
> records what you did and where you went.
> A club with only a bouncer (authentication) but no VIP
> list (authorization): everyone with a valid ID can access
> the backstage area. A club with ID + VIP list but no
> cameras (auditing): if something goes missing, no one
> knows who was in the backstage area.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Three separate security checks: Authentication (are you
really who you say you are?), Authorization (are you
allowed to do THIS specific thing?), and Auditing (we're
recording everything you do). Most security problems happen
because developers check authentication but forget
authorization.

**Level 2 - How to use it (junior developer):**
For every API endpoint: (1) authentication check (valid
token?), (2) authorization check (is this identity
permitted to access THIS specific resource?), (3) audit
log (record who accessed what). The authorization check
must include the resource ID - not just "is this user
logged in" but "is this user allowed to access ORDER #12345?"

**Level 3 - How it works (mid-level engineer):**
Authentication: JWT validation (signature, expiry, issuer).
Authorization: RBAC (role permits action type) + resource
ownership (identity matches resource owner OR has admin
role). Auditing: structured log entry with: who (user_id,
IP, session_id), what (action + resource_id), when
(timestamp), outcome (success/failure), context (request_id).

**Level 4 - Why it was designed this way (senior/staff):**
RBAC (Role-Based Access Control) emerged from US military
access control models in the 1990s. Before RBAC:
every application managed its own user-to-permission
mapping. RBAC abstracted this: roles aggregate permissions,
users are assigned roles. When permission needs change:
update the role, all role members are automatically affected.
This administrative simplicity scales to millions of users.
ABAC (Attribute-Based Access Control) extends RBAC with
dynamic context: permissions based on user attributes
(department=finance), resource attributes (classification=internal),
and environmental attributes (time=business-hours, network=VPN).
Policy language: XACML, OPA (Open Policy Agent), AWS IAM
conditions.

**Level 5 - Mastery (distinguished engineer):**
Audit log integrity is the most underengineered aspect.
If an attacker can delete or modify audit logs after a
breach, the forensic capability is destroyed. Immutable
audit logs require: (1) separate log storage that application
cannot write to or delete from (log aggregation service
with write-only permissions for the application), (2)
cryptographic chaining (each log entry includes HMAC of
previous entry - modification breaks the chain), (3)
write-once storage (AWS CloudTrail + S3 Object Lock,
Splunk SmartStore with WORM). Additionally: audit log
completeness must be verified - an attacker who can
suppress logging (stop the log agent) can operate silently.
Alerting on log gaps (source X has not sent logs in > 5
minutes) is as important as alerting on log content.

---

### ⚙️ How It Works (Mechanism)

**AAA implementation in a typical Spring Boot API:**

```
REQUEST: GET /api/orders/12345
Headers: Authorization: Bearer eyJhbGc...

1. AUTHENTICATION FILTER (OncePerRequestFilter):
   - Extract JWT from Authorization header
   - Validate signature with public key (RS256)
   - Check expiry (exp claim)
   - Check issuer (iss claim matches expected)
   - Extract claims: sub (user_id), roles
   - Store in SecurityContext: authentication = {user_id: 456, roles: ["STANDARD_USER"]}
   - If validation fails → 401 Unauthorized

2. CONTROLLER METHOD:
   @GetMapping("/orders/{orderId}")
   public Order getOrder(@PathVariable Long orderId,
                         Authentication auth) {
     // AUTHORIZATION CHECK:
     Order order = orderService.findById(orderId);
     // Resource ownership check: is this user's order?
     if (!order.getUserId().equals(auth.getUserId())
         && !auth.getAuthorities().contains("ADMIN")) {
       throw new AccessDeniedException(); // → 403 Forbidden
     }
     return order;
   }

3. AUDIT ASPECT (Spring AOP):
   @AfterReturning(pointcut = "@annotation(Audited)")
   public void audit(JoinPoint jp, Object result) {
     AuditEvent event = AuditEvent.builder()
       .userId(SecurityContext.getUserId())
       .action("GET_ORDER")
       .resourceId(extractOrderId(jp))
       .outcome("SUCCESS")
       .timestamp(Instant.now())
       .ipAddress(RequestContext.getRemoteAddr())
       .build();
     auditLogService.record(event); // write-only to audit store
   }
```

---

### 💻 Code Example

**The IDOR vulnerability and fix:**

```python
# BAD: Authentication without Authorization (IDOR)
# OWASP A01: Broken Access Control
# Authenticated user can access ANY order by changing order_id.
@app.get("/api/orders/{order_id}")
async def get_order(order_id: int, current_user = Depends(get_current_user)):
    # Authentication: get_current_user validates JWT. OK.
    # Authorization: MISSING. Any authenticated user can access
    # any order_id. Order #1 through #999999999 = accessible.
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404)
    return order  # Returns ANY user's order. IDOR vulnerability.

# GOOD: Authentication + Authorization + Audit
@app.get("/api/orders/{order_id}")
async def get_order(
    order_id: int,
    current_user = Depends(get_current_user),
    audit: AuditLogger = Depends(get_audit_logger)
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404)

    # AUTHORIZATION: is this user permitted to access THIS order?
    if (order.user_id != current_user.id
            and "ADMIN" not in current_user.roles):
        audit.record(current_user.id, "GET_ORDER", order_id,
                     "FORBIDDEN")  # AUDIT: record denied attempt
        raise HTTPException(status_code=403,
                            detail="Not authorized")

    # AUDIT: record successful access
    audit.record(current_user.id, "GET_ORDER", order_id, "SUCCESS")
    return order
```

---

### ⚖️ Comparison Table

| Aspect | Authentication | Authorization | Auditing |
|:---|:---|:---|:---|
| **Question** | Who are you? | What may you do? | What did you do? |
| **Timing** | At session start | Per request, per resource | After every action |
| **Failure result** | 401 Unauthorized | 403 Forbidden | Breach undetected |
| **Missing = OWASP** | A07 Auth Failures | A01 Broken Access Control | A09 Logging Failures |
| **Mechanism** | Password, JWT, cert | RBAC, ABAC, ownership check | Structured logs, SIEM |
| **Can change mid-session?** | No (re-login required) | Yes (role revocation) | N/A (continuous) |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| If a user is authenticated, they are authorized | Authentication confirms identity; authorization confirms permission for a specific resource + action. A user authenticated with valid credentials is authorized to do NOTHING until specific permissions are granted. The two are completely orthogonal. An admin is authenticated and authorized for everything. A standard user is authenticated and authorized for only their own resources. A deactivated user is not authenticated and authorized for nothing. |
| Audit logs are only needed for compliance | Audit logs are the primary tool for incident response: "what did the attacker access during the 72-hour unauthorized period?" Without audit logs: you cannot answer this question, you must assume all data was compromised (notify all users), and you cannot prove to regulators what was or was not accessed. With detailed audit logs: you notify only the users whose data was accessed (proportionate response), reduce remediation scope, and satisfy regulatory requirements for evidence. Audit logs are an operational security tool, not just a compliance checkbox. |

---

### 🚨 Failure Modes & Diagnosis

**Failure: Privilege escalation via authorization gap**

**Symptom:** API endpoint allows user to update their own profile.
A user discovers that by modifying the `role` field in the
request body, they can upgrade their own role to "ADMIN."

**Root cause:** Mass assignment vulnerability (OWASP A04) +
authorization gap. The endpoint:
- Authenticated: yes (required)
- Authorized: checked that user updates THEIR OWN profile
- Did NOT check: is the user allowed to modify the `role` field?

**Diagnosis:**
```python
# Vulnerable pattern:
@app.put("/users/{user_id}")
async def update_user(user_id: int, update_data: dict,
                      current_user = Depends(get_current_user)):
    if current_user.id != user_id:
        raise HTTPException(403)
    # VULNERABLE: blindly applies all fields from update_data
    # including 'role', 'is_admin', 'credit_balance', etc.
    db.query(User).filter(User.id == user_id).update(update_data)

# Fix: explicit allowlist of updatable fields
ALLOWED_USER_UPDATE_FIELDS = {"name", "email", "phone", "bio"}

@app.put("/users/{user_id}")
async def update_user(user_id: int, update_data: dict,
                      current_user = Depends(get_current_user)):
    if current_user.id != user_id:
        raise HTTPException(403)
    # SAFE: only fields in allowlist are applied
    safe_update = {k: v for k, v in update_data.items()
                   if k in ALLOWED_USER_UPDATE_FIELDS}
    if not safe_update:
        raise HTTPException(400, "No valid fields to update")
    db.query(User).filter(User.id == user_id).update(safe_update)
```

---

### 🔗 Related Keywords

**Goes deeper:**
- `JWT` - authentication token mechanism
- `OAuth 2.0 Basics` - authorization framework
- `IDOR` - the most common authorization failure
- `Principle of Least Privilege` - limits authorization scope
- `Security Logging and Monitoring` - auditing in depth

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ AuthN       │ Who are you? → 401 if fails                │
│             │ Mechanisms: password, JWT, cert, OAuth      │
├─────────────┼─────────────────────────────────────────── │
│ AuthZ       │ May you do this to THIS resource? → 403    │
│             │ Mechanisms: RBAC, ABAC, ownership check     │
├─────────────┼─────────────────────────────────────────── │
│ Audit       │ Record who/what/when/outcome (write-only)  │
│             │ Immutable, HMAC-chained, SIEM-ingested      │
├─────────────┼─────────────────────────────────────────── │
│ OWASP MAP   │ AuthN fail → A07 | AuthZ fail → A01       │
│             │ No audit → A09                             │
├─────────────┼─────────────────────────────────────────── │
│ ONE-LINER   │ "Login once (AuthN). Check permission for  │
│             │  every resource (AuthZ). Log everything    │
│             │  (Audit). Missing any one = a breach."     │
└──────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
"Identity is not entitlement." Just because a user is
authenticated (their identity is confirmed) does not mean
they are entitled to access any specific resource. This
principle extends beyond security: in multi-tenant SaaS,
an authenticated user from tenant A must not access tenant
B's data - even though both users are legitimately
authenticated. In healthcare: a doctor is authenticated
(licensed MD, verified identity) but not authorized to
access any patient's records - only patients under their
care. The separation of "who you are" from "what you may
do" is fundamental to any access-controlled system.

---

### 💡 The Surprising Truth

Authorization checking is missing far more often than
authentication. In a 2023 analysis of bug bounty submissions
across 500 programs, 62% of "High" or "Critical" severity
findings were authorization failures (IDOR, privilege
escalation, unauthorized resource access), while only 8%
were authentication failures (credential bypass, session
fixation). Developers learn "add authentication" from
tutorials and frameworks. Authorization is checked once
per page/endpoint in traditional server-rendered apps
(does this user's role permit this page?). In the API era:
authorization must be checked per request AND per specific
resource ID. The mental shift required: from "can this role
access this endpoint?" to "can this specific user access
this specific row in the database right now?"

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **DISTINGUISH** authentication from authorization with
   a code example showing each failure mode (401 vs 403).
2. **IDENTIFY** an IDOR vulnerability in a code review
   (authentication present, authorization missing).
3. **DESIGN** an audit log schema that includes: who
   (user_id, session_id, IP), what (action, resource_id),
   when (timestamp), outcome (success/failure).
4. **EXPLAIN** why JWT roles can be stale and how to
   handle mid-session permission revocation.

---

### 🎯 Interview Deep-Dive

**Q: What is the difference between authentication and
authorization? Give an example of each failing independently.**

*Why they ask:* This is the single most important security
distinction for developers. Correct answer = security awareness.
Wrong answer = likely to introduce IDOR vulnerabilities.

*Strong answer includes:*
- Authentication failure example: user guesses admin password
  through brute force (no rate limiting/lockout) → gains
  admin identity. This is a failure of the "who are you?"
  verification (password was not adequately protected).
- Authorization failure example (IDOR): user changes
  order_id=123 to order_id=124 in API request, gets another
  user's order. User was legitimately authenticated (valid
  token). The failure was: no check that THIS authenticated
  user is permitted to access THIS specific order. This is
  the most common bug bounty finding.
- Combined failure: attacker uses credential stuffing to
  gain authenticated access as user X. User X is a standard
  user. Attacker then exploits IDOR to access admin endpoints
  that should require admin role (authorization failure
  after authentication succeeded).
- Audit role: if authentication and authorization both fail,
  audit logs tell incident responders what the attacker
  accessed. Without logs: must assume worst case (all data
  compromised).