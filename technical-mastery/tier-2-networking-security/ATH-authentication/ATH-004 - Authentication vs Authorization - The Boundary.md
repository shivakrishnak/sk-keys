---
id: ATH-004
title: "Authentication vs Authorization - The Boundary"
category: Authentication
tier: tier-2-networking-security
folder: ATH-authentication
difficulty: ★☆☆
depends_on: ATH-001, ATH-002
used_by: ATH-022, ATH-047, ATH-056
related: ATH-002, ATZ-001, ATZ-003
tags:
  - security
  - authentication
  - authorization
  - foundational
  - mental-model
status: complete
version: 5
layout: default
parent: "Authentication"
grand_parent: "Technical Mastery"
nav_order: 4
permalink: /technical-mastery/authentication/authentication-vs-authorization-the-boundary/
---

⚡ **TL;DR** - Authentication answers "who are you?" Authorization
answers "what are you allowed to do?" They are separate systems
with separate data, separate logic, and separate failure modes.
Every IDOR vulnerability - OWASP's historically most common finding -
traces to treating authentication as a substitute for authorization.

---

### 📊 Entry Metadata

| #004 | Category: Authentication | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | ATH-001, ATH-002 | |
| **Used by:** | ATH-022, ATH-047, ATH-056 | |
| **Related:** | ATH-002 What Auth Proves, ATZ-001 The Authorization Problem, ATZ-003 | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**

A developer builds a REST API. They add authentication:
users log in, receive a JWT. The developer thinks "security
done." Every endpoint checks `if (!token) return 401`.

Alice logs in and gets a valid token. She requests her
invoice: `GET /api/invoices/1001`. Works fine. Then she
changes the ID: `GET /api/invoices/1002`. Also works - that
is Bob's invoice. The developer implemented authentication,
not authorization. Alice is authenticated. She is not
authorized to read Bob's data. The system cannot tell
the difference because it never asked the authorization
question.

**THE BREAKING POINT:**

"Is the user logged in?" and "may this user do this specific
thing?" are completely different questions with completely
different answers. Answering only the first question and
treating it as the second is the cause of most data exposure
incidents in web applications.

**THE INVENTION MOMENT:**

The distinction was always necessary but was not widely
understood by developers until the rise of REST APIs made
"check the token" a common pattern - and OWASP's research
showed it was being systematically misapplied.

---

### 📘 Textbook Definition

Authentication is the process of verifying that a claimed
identity is genuine. Authorization is the process of
determining whether a verified identity is permitted to
perform a specific operation on a specific resource. The
two processes are sequential and complementary: authentication
produces a verified principal; authorization evaluates that
principal against a policy to produce an access decision.
Authentication failure produces a 401 Unauthorized response;
authorization failure produces a 403 Forbidden response.
These are distinct HTTP status codes for a reason.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Authentication = who you are. Authorization = what you may do.

**One analogy:**
> A nightclub bouncer checks your ID at the door (authentication).
> A VIP host checks whether your name is on the VIP list once
> you are inside (authorization). Passing the door check does
> not automatically grant VIP access - those are two separate
> people with two separate lists.

**One insight:**
The HTTP status codes encode this distinction: 401 means
"you have not proven who you are" (authentication failure);
403 means "I know who you are but you are not allowed"
(authorization failure). If your API returns 401 for all
security failures, you are conflating the two.

---

### 🔩 First Principles Explanation

**THE FUNDAMENTAL DISTINCTION:**

| Dimension | Authentication | Authorization |
|---|---|---|
| Question answered | Who are you? | What may you do? |
| Input | Credential (password, token, cert) | Identity + action + resource |
| Output | Verified identity principal | Allow / Deny decision |
| HTTP response on failure | 401 Unauthorized | 403 Forbidden |
| Data used | Credential store (hashes, keys) | Policy store (roles, rules) |
| When evaluated | Once per session/login | Every request, every resource |
| Can it change without re-login? | No (session is stable) | Yes (role change takes effect immediately) |

**THE TWO-STEP MODEL:**

Every access control system follows this exact sequence:

```
Step 1: Authentication
  Client presents credential
  System verifies credential
  System produces: verified identity (user ID, roles, claims)

Step 2: Authorization
  System receives: (identity, action, resource)
  System evaluates: policy(identity, action, resource)
  System produces: ALLOW or DENY
```

They must happen in this order. Authorization cannot run
without a verified identity. Authentication is not access
control - it is the prerequisite for access control.

**THE TRADE-OFFS:**

**Gain:** Clean separation enables independent evolution -
change auth mechanisms (add FIDO2) without touching authz
policies; change permissions without requiring re-auth.

**Cost:** More code, more systems, more complexity. Developers
who understand only auth must learn authz separately.

---

### 🧠 Mental Model / Analogy

> Think of a corporate office building. Badge swipe at the
> main entrance = authentication (proves you are an employee).
> Access control on the server room, executive floor, and
> finance area = authorization (proves you have specific
> permission for that specific area). Every employee can
> swipe into the building. Not every employee can enter the
> server room.

- "Badge swipe" → credential verification (JWT, session)
- "Access granted to building" → authenticated session
- "Server room badge reader" → per-resource authz check
- "Access log" → audit trail of both auth and authz events

**Where this analogy breaks down:** Physical access control
is often slow (badge readers, human guards). Digital authz
must happen in microseconds on every request.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Logging in (authentication) is proving who you are. Being
allowed to do something specific (authorization) is a
separate check that happens after. Logging in does not
automatically give you access to everything.

**Level 2 - How to use it (junior developer):**
Always perform TWO checks on sensitive endpoints: (1) is
the user authenticated (valid token)? and (2) is this
specific user authorized to access this specific resource?
Never skip the second check.

**Level 3 - How it works (mid-level engineer):**
Authentication middleware runs first: it validates the JWT
signature and expiry, extracts the identity claims, and
attaches them to the request context. Authorization
middleware runs second: it evaluates whether the attached
identity has permission for the requested route and resource.
Both must pass; either can fail independently.

**Level 4 - Why it was designed this way (senior/staff):**
The separation exists because they have different caching,
consistency, and change-management needs. Authentication is
cached in the session/token lifetime. Authorization decisions
may need to be evaluated fresh (role changes take effect
immediately, not on next login). Separating them allows
each to have appropriate TTLs and invalidation strategies.

**Level 5 - Mastery (distinguished engineer):**
At system design scale, auth and authz are different services
with different data models. The auth service holds credentials
and issues tokens. The authz service holds policies and
evaluates decisions. For microservices: each service
authenticates the request (by verifying the JWT signature),
then authorizes it locally or via a policy sidecar. A
compromise of the auth service does not compromise authz
policies; a policy misconfiguration does not break the
ability to log in. This separation is a security principle:
fail in different ways, isolate blast radius.

---

### ⚙️ How It Works (Mechanism)

The two steps in a Spring Boot API:

```
┌───────────────────────────────────────────────────────┐
│     Authentication + Authorization in Request Flow    │
├───────────────────────────────────────────────────────┤
│                                                       │
│  Incoming: GET /api/invoices/1002                     │
│  Header: Authorization: Bearer eyJ...                 │
│      │                                                │
│      ▼                                                │
│  STEP 1: Authentication Filter                        │
│  - Parse JWT                                          │
│  - Verify signature (RS256 / HS256)                   │
│  - Check expiry                                       │
│  - Extract: userId=alice, roles=[viewer]              │
│  - Set SecurityContext with authenticated principal   │
│  Result: 401 if any check fails                       │
│      │                                                │
│      ▼                                                │
│  STEP 2: Authorization Check                          │
│  - GET /invoices/{id}: does alice own invoice 1002?   │
│  - Query: SELECT 1 FROM invoices                      │
│            WHERE id=1002 AND org_id=alice.org_id      │
│  - Not found: invoice exists but wrong org            │
│  Result: 403 Forbidden                                │
│      │                                                │
│      ▼                                                │
│  Business logic (only reached if both pass)           │
│                                                       │
└───────────────────────────────────────────────────────┘
```

```mermaid
sequenceDiagram
    participant C as Client
    participant AF as Auth Filter
    participant AZ as Authz Check
    participant BL as Business Logic
    C->>AF: GET /invoices/1002 + JWT
    AF->>AF: Validate JWT; extract identity
    alt Invalid token
        AF-->>C: 401 Unauthorized
    end
    AF->>AZ: Pass request + identity
    AZ->>AZ: Does alice own invoice 1002?
    alt Not authorized
        AZ-->>C: 403 Forbidden
    end
    AZ->>BL: Proceed with authorized request
    BL-->>C: 200 OK + invoice data
```

---

### 💻 Code Examples

**Example - BAD: authentication without authorization**

```java
// BAD: only checks "is the user logged in?"
// Any authenticated user reads any invoice
@GetMapping("/invoices/{id}")
public Invoice getInvoice(@PathVariable Long id,
                          @AuthUser User user) {
    return invoiceRepo.findById(id)
        .orElseThrow(() -> new NotFoundException(id));
}
```

**Example - GOOD: authentication AND authorization**

```java
// GOOD: checks both identity and ownership
@GetMapping("/invoices/{id}")
public Invoice getInvoice(@PathVariable Long id,
                          @AuthUser User user) {
    Invoice invoice = invoiceRepo
        .findByIdAndOrgId(id, user.getOrgId())  // ownership filter
        .orElseThrow(() -> new ForbiddenException(
            "Invoice not found or access denied"  // don't leak which
        ));
    return invoice;
}
```

**Example - FAILURE: IDOR exposed via predictable IDs**

```
Test: log in as Alice, capture request to GET /invoices/1001
Change 1001 to 1002 (Bob's invoice)
Expected: 403 Forbidden
Actual: 200 OK with Bob's invoice data

This is IDOR (Insecure Direct Object Reference).
The API authenticated Alice but never asked:
"Is invoice 1002 Alice's to read?"

Fix sequence:
  1. Add ownership filter to every data query
  2. Write authorization tests:
       bobClient.get("/invoices/" + aliceInvoiceId)
               .andExpect(status().isForbidden());
  3. Return 404 (not 403) for resources the user
     should not know exist (prevents enumeration)
```

---

### ⚠️ Common Failure Modes

**Returning 401 for authorization failures:**

```
Problem: API returns 401 for "user does not own this resource"
instead of 403.

Impact:
  - Leaks information: 401 means "try logging in differently"
    which tells attacker the resource exists
  - Breaks client error handling (clients retry 401 with new
    tokens, creating infinite loops)

Correct semantics:
  401: "I don't know who you are - please authenticate"
  403: "I know who you are - you're not allowed"
  404: "I won't tell you whether this exists" (preferred for
       resources the user should not know about at all)
```

---

### 🔭 At Scale

In microservices: every service boundary is an opportunity
to forget the authz check. The auth token propagates across
services; each service must independently verify the token
AND check authorization for its own resources. Common failure:
service B trusts that service A already performed the authz
check. If A is compromised or A's check is wrong, B is
exposed. Defense: every service is its own trust boundary.

---

### 🎓 Interview Deep-Dive

**Q: What HTTP status code should an API return when an
   authenticated user tries to access a resource they
   don't own?**

403 Forbidden. The server knows who they are (authentication
succeeded) but refuses the action (authorization failed).

401 Unauthorized would be incorrect - that signals the
client should attempt authentication (include/refresh a
token). A 403 signals that re-authentication will not help;
the user simply lacks permission.

For resources whose existence should be hidden from the
requesting user, 404 Not Found is preferred - it prevents
resource enumeration. A user requesting `DELETE /admin/config`
should receive 404 if they are not an admin, not 403 (which
reveals that the admin endpoint exists).

---

*Authentication category: ATH | Entry: ATH-004 | v5.0*