---
id: SEC-043
title: "Insecure Direct Object Reference (IDOR)"
category: "Security"
tier: tier-2-networking-security
folder: SEC-security
difficulty: ★★☆
depends_on: SEC-013, SEC-014, SEC-016, SEC-018, SEC-040
used_by: SEC-067, SEC-086
related: SEC-013, SEC-014, SEC-016, SEC-018, SEC-040, SEC-067, SEC-086
tags:
  - security
  - idor
  - bola
  - authorization
  - owasp
  - access-control
  - broken-access-control
status: complete
version: 4
layout: default
parent: "Security"
grand_parent: "Technical Mastery"
nav_order: 43
permalink: /technical-mastery/sec/insecure-direct-object-reference-idor/
---

⚡ TL;DR - IDOR (Insecure Direct Object Reference) = accessing
another user's resource by changing an object identifier in
the request. OWASP calls this BOLA (Broken Object Level
Authorization) and it's the #1 API vulnerability.

**The core problem:** Developers check authentication
("is the user logged in?") but forget authorization
("does this user own THIS specific object?").

```
# VULNERABLE: checks auth, not ownership
def get_invoice(invoice_id):
    if not current_user:
        return 401
    return db.get_invoice(invoice_id)  # Returns ANY invoice

# FIXED: checks both auth AND ownership
def get_invoice(invoice_id):
    if not current_user:
        return 401
    invoice = db.get_invoice(invoice_id)
    if invoice.user_id != current_user.id:
        return 403
    return invoice
```

**Scope:** IDOR affects any resource accessed by user-controlled
identifier: integers, GUIDs, filenames, usernames, email addresses,
order numbers, ticket IDs, API keys - any reference to a specific
object.

---

| #043 | Category: Security | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Authentication, Authorization, Security Fundamentals, Access Control, API Security | |
| **Used by:** | Business Logic, Advanced XSS | |
| **Related:** | BOLA, Broken Access Control, API Security, OWASP Top 10, Business Logic | |

---

### 🔥 The Problem This Solves

**IDOR IS EVERYWHERE - REAL EXAMPLES:**
- **Facebook (2013):** Change photo album ID in request URL to
  access any user's private photos without being their friend.
- **Venmo (2019):** Transaction IDs were sequential integers.
  Combined with public-by-default setting: enumerate all transactions.
- **Parler (2021):** Post IDs were sequential. Combined with no auth
  on public posts: bulk download of all 70 million+ posts before site shutdown.
- **Healthcare EHR (2020, unnamed):** Patient portal exposed
  medical records - change `patient_id` parameter to access
  any patient's records.
- **Airlines (multiple):** Change booking reference in URL to access
  other passengers' booking details.

**WHY IT KEEPS HAPPENING:**
1. Authentication and authorization are conflated in many developers' minds.
   "The user is authenticated, so they can access this page" misses
   the per-resource ownership check.
2. Sequential integer IDs are easy to enumerate.
3. Authorization checks are easy to forget in busy feature development.
4. IDOR typically shows a 200 OK response (not an error) during development,
   making it invisible until someone deliberately tests for it.

---

### 📘 Textbook Definition

**IDOR (Insecure Direct Object Reference):** A vulnerability
where an application uses user-controllable input to access
objects (database records, files, functions) without verifying
that the user is authorized to access the specific requested object.

**BOLA (Broken Object Level Authorization):** OWASP API Security
Top 10 #1 (2019 and 2023). Same as IDOR, specifically in API
contexts. The term highlights that authorization must be checked
at the object level (per-record), not just at the route level
(per-endpoint).

**Direct Object Reference:** Any time a client-submitted value
directly maps to a server-side resource:
- URL path: `/api/orders/12345`
- Query parameter: `?invoice_id=12345`
- Request body: `{"document_id": "abc-xyz"}`
- Cookie value: `user_token=<JWT sub claim as user reference>`

**Indirect Object Reference:** A mapping layer that converts
client-visible references to server-side references. Example:
client sees reference `1` (first item in user's list),
server maps `user_42_ref_1` → `global_id_9847`. The mapping
is user-scoped: reference `1` for user 42 is a different
object than reference `1` for user 43. Not a replacement for
authorization checks - a defense-in-depth layer.

**Horizontal vs Vertical Privilege Escalation:**
- **Horizontal:** User A accesses User B's data (same privilege
  level, different ownership). Classic IDOR.
- **Vertical:** Regular user accesses admin data/functionality.
  "Function level" IDOR / Broken Function Level Authorization.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Change the ID in the URL and see if you can access data
belonging to another user. If yes: IDOR. Fix: after fetching
the resource, verify that `resource.owner == current_user`.

**One analogy:**
> IDOR is like a hotel room key that opens any room.
> You're authenticated (have a valid key card for the hotel),
> but the system doesn't check whether the room you're opening
> is YOUR room. A key that opens room 101 should only open
> room 101 (the room assigned to you at check-in) - but if
> the system only validates "is this a valid guest?" without
> checking "is this room assigned to this guest?", you can
> use your key card to open any room. The front desk
> (authentication server) validated your identity; the
> room lock (authorization check) failed to enforce room ownership.

---

### 🔩 First Principles Explanation

**Four IDOR patterns and their fixes:**

```
IDOR PATTERN 1: Integer ID in URL path

  VULNERABLE:
    GET /api/orders/1234
    
    def get_order(order_id: int):
        order = db.get(Order, order_id)
        return order  # Returns any order to any authenticated user
  
  FIX:
    def get_order(order_id: int, current_user: User):
        order = db.get(Order, order_id)
        if not order:
            raise NotFound()
        if order.user_id != current_user.id:
            raise Forbidden()  # Or NotFound() to avoid confirming existence
        return order

IDOR PATTERN 2: GUID/UUID (still needs auth check!)

  MISCONCEPTION: "We use UUIDs, so IDOR is impossible - they're unguessable."
  REALITY: UUIDs can be leaked (URLs in emails, browser history, logs).
    A UUID is a harder-to-enumerate ID, but once known, still exploitable
    if there's no ownership check.
  
  VULNERABLE:
    GET /api/documents/550e8400-e29b-41d4-a716-446655440000
    (UUID was in an email link shared between departments)
    
    def get_document(doc_id: UUID):
        return db.get(Document, doc_id)  # UUID doesn't help without auth check
  
  FIX: Same as integer pattern - check ownership regardless of ID type.

IDOR PATTERN 3: Filename / file path

  VULNERABLE:
    GET /api/files/report_user_42_q3.pdf
    (filename encodes user ID and is guessable)
    
    def download_file(filename: str):
        return serve_file(f"/uploads/{filename}")
  
  FIX:
    1. Store files with opaque names (UUID): file_abc123.pdf
    2. Map filenames to ownership in database
    3. Check ownership before serving:
    
    def download_file(file_id: str, current_user: User):
        file_record = db.get(FileRecord, file_id)
        if not file_record:
            raise NotFound()
        if file_record.user_id != current_user.id:
            raise Forbidden()
        return serve_file(file_record.storage_path)

IDOR PATTERN 4: Action on resource (not just read)

  IDOR also affects: update, delete, send, export operations.
  
  VULNERABLE:
    DELETE /api/messages/789
    
    def delete_message(message_id: int):
        db.delete(Message, message_id)  # Deletes anyone's message!
  
  FIX: Check ownership before any mutation:
    def delete_message(message_id: int, current_user: User):
        message = db.get(Message, message_id)
        if not message:
            raise NotFound()
        if message.sender_id != current_user.id:
            raise Forbidden()
        db.delete(message)

MULTI-TENANT IDOR (organizational ownership):

  In SaaS apps: resources belong to organizations, not just users.
  User may be authorized within their org but not across orgs.
  
  VULNERABLE:
    GET /api/contracts/{contract_id}
    
    def get_contract(contract_id: int, current_user: User):
        contract = db.get(Contract, contract_id)
        if contract.user_id == current_user.id:  # User check only
            return contract
        # Missing: what if user is from same org but different permission?
        # What if user is from a different org?
  
  FIX: Check org membership AND permission:
    def get_contract(contract_id: int, current_user: User):
        contract = db.get(Contract, contract_id)
        if not contract:
            raise NotFound()
        if contract.org_id != current_user.org_id:
            raise Forbidden()
        # Optional: check user's role within org for this resource
        if not has_contract_read_permission(current_user, contract):
            raise Forbidden()
        return contract
```

---

### 🧪 Thought Experiment

**SCENARIO: Bug bounty hunter testing a medical portal for IDOR**

```
CONTEXT: Patient portal for a hospital network.
  Login: patients authenticate with patient ID.
  Profile URL: /portal/patient/34521/records
  
TESTING METHODOLOGY:

Step 1: Authenticate and baseline
  Login as patient (patient_id=34521)
  Access: GET /portal/patient/34521/records → 200 OK (own records)
  Note: URL contains own patient_id.

Step 2: Horizontal IDOR test
  Request: GET /portal/patient/34520/records (adjacent ID)
  Expected (secure): 403 Forbidden or 404 Not Found
  Found (vulnerable): 200 OK → another patient's medical records!

Step 3: Enumerate
  Loop patient_id from 1 to 99999
  Many IDs return medical records: diagnoses, medications,
    lab results, billing information.
  
  At this point: STOP testing. This is a critical finding.
  Document: one example is sufficient. No mass data download.
  Report immediately to hospital security team (responsible disclosure).

IMPACT ASSESSMENT:
  Confidentiality: all patient records (HIPAA violation)
  Integrity: attacker could also modify medical records (if PUT also vulnerable)
  Regulatory: HIPAA breach notification required for each affected patient
  Legal: significant liability

WHAT THE FIX REQUIRES:
  1. Add ownership check to ALL patient record endpoints
     (not just the one tested - assume all are vulnerable)
  2. Audit access logs for any unusual pattern
     (lots of sequential ID access from one user)
  3. Determine if any unauthorized access has already occurred
  4. Notify affected patients (if breach confirmed)
  5. Implement IDOR tests in security test suite
```

---

### 🧠 Mental Model / Analogy

> IDOR is the equivalent of a library system that checks
> whether you have a library card (authentication) but not
> whether the books you're checking out belong to your
> reservation list (authorization). Any cardholder can
> check out books reserved by any other cardholder - just
> by knowing the book's catalog number (the ID).
> 
> The librarian's job is two-fold:
> 1. Verify your card is valid (authentication)
> 2. Verify the book you're requesting is on YOUR reservation (authorization)
> 
> IDOR happens when librarians are trained only to check cards,
> not to check whether the reservation belongs to the cardholder.
> With a sequential catalog numbering system (integer IDs), an
> attacker can check out every reservation in the system.
> With random catalog numbers (UUIDs), they can still check out
> any reservation they somehow learn the number for.
> The ownership check (step 2) is non-optional.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
IDOR means: you can see other people's data by changing a
number in the URL. For example, if your order is at
`/orders/1234`, can you change it to `/orders/1235` and
see someone else's order? If yes, that's IDOR. The fix:
after fetching any record, check that it belongs to the
currently logged-in user before returning it.

**Level 2 - How to use it (junior developer):**
For every endpoint that fetches a resource by ID:
`order = get_order(order_id); if order.user_id != current_user.id: return 403`.
Apply this check to GET, PUT, PATCH, DELETE - any operation
on a specific resource. Don't trust that the user-provided ID
is valid for that user. Fetch first, verify ownership, then return.
Use UUIDs instead of sequential integers for IDs - harder to enumerate,
though still requires the ownership check.

**Level 3 - How it works (mid-level engineer):**
IDOR is a subset of Broken Access Control (OWASP A01:2021).
Two dimensions of access control: vertical (role-based: admin vs
user) and horizontal (ownership: User A vs User B's data).
Most access control systems implement vertical checks (role-based
authorization) but miss horizontal checks (ownership). The fix
pattern: after fetching any record, assert ownership. For multi-tenant
apps: assert org membership first, then role-within-org.
Automated testing: write an authorization test suite that
authenticates as User B and attempts to access User A's resources.
Positive test: User B should get 403/404. If 200: IDOR exists.

**Level 4 - Why it was designed this way (senior/staff):**
IDOR persists as the #1 API vulnerability because the authorization
check requires application-specific business logic knowledge.
A generic middleware cannot enforce "does this user own this invoice?"
without understanding the data model. The developer building
the invoice endpoint must implement the check explicitly.
Contrast with authentication: a generic JWT middleware can
handle authentication for all endpoints. Authorization at
the object level requires per-resource knowledge. Framework
patterns that help: repository pattern with user-scoped queries
(always filter by user_id in the repository layer), so the
application code structurally cannot retrieve other users' data:
`UserOrderRepository.get(order_id)` implicitly appends
`WHERE user_id = current_user.id`.

**Level 5 - Mastery (distinguished engineer):**
ABAC (Attribute-Based Access Control) formalizes object-level
authorization: policy rules operate on resource attributes
(resource.owner == subject.id) evaluated at access time.
Policy engines (Open Policy Agent, Casbin, AWS Cedar) externalize
authorization logic from application code - reducing the chance
of forgetting a check. The "zanzibar" model (Google's authorization
system, now open-sourced as SpiceDB/Permify/Ory Keto) represents
ownership as a relationship graph: User A → owner → Order 12345.
Authorization check: "does User A have 'owner' relationship to Order 12345?"
This graph model naturally handles complex multi-level ownership
(user → member → org → owner → contract) and is the foundation
for many modern fine-grained authorization systems.

---

### ⚙️ How It Works (Mechanism)

**IDOR exploitation and remediation flow:**

```
IDOR EXPLOIT FLOW:

Attacker authenticated as user_id=99:

  Request 1: GET /api/profile/99 (own profile)
  Response: { "id": 99, "name": "Attacker", "email": "..." }
  
  Observation: URL contains user's own ID.
  
  Request 2: GET /api/profile/1 (admin?)
  Response: { "id": 1, "name": "Admin User", "email": "admin@company.com",
              "role": "admin", "ssn": "123-45-6789" }
  
  Attacker: now has admin's PII and email for phishing/escalation.
  
  Request 3: PUT /api/profile/1 { "email": "attacker@evil.com" }
  Response: 200 OK
  
  Attacker: changed admin's email. Can now trigger password reset
  to attacker's email → account takeover.

REMEDIATION ARCHITECTURE:

LAYER 1: Ownership filter in database query (prevents data leakage)
  Instead of:
    SELECT * FROM profiles WHERE id = ?
  Use:
    SELECT * FROM profiles WHERE id = ? AND user_id = current_user.id
  
  If wrong ID: query returns no rows → 404 (not an error, just not found)
  Advantage: no data is ever loaded for unauthorized access.

LAYER 2: Post-fetch ownership check (defense in depth)
  Even with Layer 1, explicit check in business logic:
    if profile.user_id != current_user.id:
        raise Forbidden()
  Catches cases where Layer 1 was accidentally bypassed.

LAYER 3: Automated security tests
  # In your test suite:
  def test_profile_idor(client, user_a_token, user_b_token):
      # Create profile as User A
      profile = create_profile(user_a_token)
      
      # Attempt to access as User B
      response = client.get(
          f"/api/profile/{profile.id}",
          headers={"Authorization": f"Bearer {user_b_token}"}
      )
      
      assert response.status_code in [403, 404], \
          f"IDOR: User B accessed User A's profile ({response.status_code})"
  
  This test runs in CI/CD and catches IDOR regressions.
```

---

### 💻 Code Example

**Repository pattern preventing IDOR structurally:**

```python
# Structural IDOR prevention: user-scoped repository

from sqlalchemy.orm import Session
from typing import Optional
from models import Order, User

class OrderRepository:
    """
    All queries are automatically scoped to the owning user.
    Structural prevention: cannot accidentally return another user's order.
    """
    
    def __init__(self, db: Session, current_user: User):
        self.db = db
        self.user_id = current_user.id
    
    def get_by_id(self, order_id: int) -> Optional[Order]:
        """
        Returns order only if it belongs to current user.
        Returns None (not 403) if not found or wrong owner.
        Caller converts None → 404.
        """
        return (
            self.db.query(Order)
            .filter(
                Order.id == order_id,
                Order.user_id == self.user_id  # ← ALWAYS scoped to user
            )
            .first()
        )
    
    def list_all(self) -> list[Order]:
        """All orders for current user only. No cross-user access possible."""
        return (
            self.db.query(Order)
            .filter(Order.user_id == self.user_id)  # ← Always scoped
            .all()
        )
    
    def update(self, order_id: int, data: dict) -> Optional[Order]:
        """Update only if belongs to current user."""
        order = self.get_by_id(order_id)
        if not order:
            return None  # Not found OR not owned by user
        for key, value in data.items():
            setattr(order, key, value)
        self.db.commit()
        return order
    
    def delete(self, order_id: int) -> bool:
        """Delete only if belongs to current user."""
        order = self.get_by_id(order_id)
        if not order:
            return False
        self.db.delete(order)
        self.db.commit()
        return True

# API layer uses the repository (IDOR is impossible via this class)
from fastapi import Depends

@app.get("/api/orders/{order_id}")
async def get_order(order_id: int, current_user=Depends(get_current_user)):
    repo = OrderRepository(db, current_user)
    order = repo.get_by_id(order_id)  # Always user-scoped
    if not order:
        raise HTTPException(404, "Order not found")  # Not 403 (avoids ID enumeration)
    return order

@app.delete("/api/orders/{order_id}")
async def delete_order(order_id: int, current_user=Depends(get_current_user)):
    repo = OrderRepository(db, current_user)
    deleted = repo.delete(order_id)  # Only deletes user's own orders
    if not deleted:
        raise HTTPException(404, "Order not found")
    return {"status": "deleted"}
```

---

### ⚖️ Comparison Table

| Defense | Effectiveness | Complexity | Notes |
|:---|:---|:---|:---|
| **Post-fetch ownership check** | High | Low | Required: minimum viable defense |
| **User-scoped DB query** | High | Low-Medium | Structural prevention; recommended |
| **UUIDs instead of integers** | Low (by itself) | Low | Reduces enumerability; NOT a substitute for auth check |
| **Indirect references** | Medium | Medium | User-scoped mapping layer; additional complexity |
| **ABAC policy engine (OPA)** | High | High | Scales to complex policies; overkill for simple apps |
| **Automated IDOR tests** | High (regression) | Medium | Catches future regressions |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| UUIDs prevent IDOR | UUIDs prevent brute-force enumeration because the ID space is too large to iterate. But UUIDs can be leaked: they appear in emails, browser history, server logs, Referer headers. Once an attacker knows a UUID (e.g., from a shared link or phishing victim's history), they can use it to access the resource without an ownership check. UUID IDs provide a defense-in-depth layer against enumeration; they are NOT a substitute for ownership verification. Both are needed: UUID IDs (reduces attack surface) AND ownership checks (prevents access with known IDs). |
| 403 Forbidden is the correct response for IDOR | Returning 403 for unauthorized object access confirms that the object EXISTS at that ID. An attacker can enumerate objects by looking for 403 (exists but forbidden) vs 404 (doesn't exist). OWASP recommends returning 404 for objects the caller should not know exist. This trades some debuggability (developer sees 404 instead of 403 when they make access control mistakes) for security (attacker cannot distinguish "object doesn't exist" from "object exists but you can't access it"). High-security applications should prefer 404 for unauthorized access to sensitive objects. |

---

### 🚨 Failure Modes & Diagnosis

**Finding IDOR vulnerabilities:**

```
IDOR TESTING METHODOLOGY:

MANUAL TESTING:
  1. Note all IDs in responses as User A: order IDs, doc IDs, etc.
  2. Authenticate as User B
  3. Attempt to access User A's IDs as User B
     GET /api/orders/USER_A_ORDER_ID with User B credentials
  4. Check: 200 OK (IDOR) vs 403/404 (protected)

BURP SUITE APPROACH:
  1. Use Burp Suite to capture all requests as User A
  2. Switch to User B's session cookie/token
  3. Use Burp Repeater to replay User A's requests with User B's auth
  4. Observe responses: 200 = IDOR vulnerability

AUTOMATED APPROACH (Authorization Testing):
  Use Autorize Burp extension:
  - Configure User B's session
  - Autorize automatically replays every request with User B's credentials
  - Flags responses where User B gets the same data as User A

HORIZONTAL vs VERTICAL:
  Horizontal IDOR: User A → User B's data (same role, different user)
  Vertical IDOR: Regular user → Admin data (different role)
  
  Test vertical: find admin endpoints from API docs, JS source,
    or fuzzing with admin-looking paths: /admin/, /api/admin/,
    /internal/, /manage/, /superuser/
  Test with regular user credentials → expect 403

MASS ASSIGNMENT IDOR:
  POST /api/profile { "name": "Attacker", "is_admin": true }
  Does setting is_admin in request body actually escalate privilege?
  Fix: use explicit field allowlist in request schemas.
```

---

### 🔗 Related Keywords

**Prerequisites:**
- `Authentication Fundamentals` - authentication vs authorization distinction
- `Authorization and Access Control` - role-based access control
- `API Security Basics` - BOLA as #1 API vulnerability

**Builds on this:**
- `Business Logic Vulnerabilities` - IDOR as business logic abuse
- `Advanced XSS` - IDOR combined with XSS for chained attacks

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ THE PATTERN  │ GET /api/X/{id} → check: X.owner_id ==   │
│              │ current_user.id AFTER fetching X          │
├──────────────┼───────────────────────────────────────────┤
│ ALL METHODS  │ GET, POST, PUT, PATCH, DELETE - all need  │
│              │ ownership checks, not just read            │
├──────────────┼───────────────────────────────────────────┤
│ RESPONSE     │ 404 (preferred) or 403 on unauthorized    │
│              │ 403 confirms object exists (enumerable)   │
├──────────────┼───────────────────────────────────────────┤
│ STRUCTURAL   │ Scoped repository: filter by user_id in   │
│              │ EVERY query (structural, not just manual) │
├──────────────┼───────────────────────────────────────────┤
│ TEST         │ Authenticate as User B, access User A's  │
│              │ object IDs → expect 403/404               │
└──────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
"Data access must enforce ownership at every layer."
The defense-in-depth approach to IDOR uses multiple layers:
database queries scoped to current user (Layer 1), post-fetch
ownership check in business logic (Layer 2), automated tests
that verify cross-user access fails (Layer 3). Any single
layer can have bugs; multiple layers reduce the chance that
all fail simultaneously. The repository pattern that always
filters by user_id in the query is the strongest form because
it's structural: the code literally cannot return another user's
data, regardless of what the caller passes in. This "impossible
to get wrong" design is the highest form of security: not
"developers must remember to check ownership" but "the code
structure prevents cross-user access by construction."

---

### 💡 The Surprising Truth

The Uber 2016 bug bounty disclosure revealed that Uber's
receipt endpoint was vulnerable to IDOR: any authenticated
Uber user could download any other user's trip receipt by
changing the receipt ID in the request. Receipt data included:
origin and destination addresses, trip duration, cost, driver
information, and pickup/dropoff times. For a user's entire trip
history: complete location history. This is particularly sensitive
because location data reveals home address (frequent pickup),
work address (frequent dropoff), medical appointments, religious
services, and other behavioral patterns. The entire dataset
was accessible to any authenticated user - authentication
without authorization. This is not a rare or edge-case mistake;
it's the single most common API vulnerability. The fix is five
lines of code. The risk is catastrophic privacy exposure.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **IDENTIFY** IDOR in code review: any endpoint that fetches
   a resource by ID without checking `resource.owner_id == current_user.id`.
2. **TEST** for IDOR: authenticate as User B, access User A's
   resource IDs, verify 403/404 response.
3. **IMPLEMENT** a user-scoped repository that structurally
   prevents cross-user data access.
4. **EXPLAIN** why UUIDs are not a substitute for ownership checks
   and provide a scenario where UUID IDs can be leaked.

---

### 🎯 Interview Deep-Dive

**Q: What is IDOR (or BOLA)? How do you find it and fix it?
Walk me through an example.**

*Why they ask:* Top-ranked API vulnerability. Tests whether
the candidate distinguishes authentication from authorization
and has practical implementation knowledge.

*Strong answer includes:*
- IDOR: accessing another user's resource by changing the identifier.
  Example: `GET /orders/1234` works (your order). Try `/orders/1235`:
  if it returns another user's order, that's IDOR.
- Root cause: authentication check ("is user logged in") exists
  but ownership check ("does this user OWN this order") is missing.
  Show the vulnerable vs fixed code: `order.user_id != current_user.id`
  check after fetching.
- Applies to: all HTTP methods (GET, PUT, DELETE), all ID types
  (int, UUID, filename), all object types (orders, files, messages,
  profiles, medical records).
- Finding it: authenticate as User B, try all IDs from User A's
  session. 200 OK with User A's data = IDOR.
- Advanced fix: user-scoped repository with user_id in every query
  (structural prevention). Automated authorization tests in CI/CD.
- OWASP API Security Top 10 #1 (BOLA). Affects most applications
  built without explicit authorization checks per resource.
  One of the highest-impact, easiest-to-fix vulnerabilities.