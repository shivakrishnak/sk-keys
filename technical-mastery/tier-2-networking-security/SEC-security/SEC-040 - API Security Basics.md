---
id: SEC-040
title: "API Security Basics"
category: "Security"
tier: tier-2-networking-security
folder: SEC-security
difficulty: ★★☆
depends_on: SEC-013, SEC-014, SEC-016, SEC-017, SEC-028, SEC-029, SEC-030, SEC-038, SEC-039
used_by: SEC-043, SEC-063, SEC-067, SEC-086
related: SEC-013, SEC-014, SEC-016, SEC-017, SEC-028, SEC-029, SEC-030, SEC-038, SEC-039, SEC-043, SEC-063, SEC-067
tags:
  - security
  - api-security
  - authentication
  - authorization
  - rate-limiting
  - owasp-api-top10
  - input-validation
  - rest
status: complete
version: 4
layout: default
parent: "Security"
grand_parent: "Technical Mastery"
nav_order: 40
permalink: /technical-mastery/sec/api-security-basics/
---

⚡ TL;DR - API security requires: authentication (who are you?),
authorization (what can you do?), input validation (is this
data valid?), and rate limiting (prevent abuse). OWASP API
Security Top 10 is the canonical reference; BOLA/IDOR (#1)
is the most common and impactful API vulnerability.

**The five API security non-negotiables:**
1. **Authentication on every endpoint** - no unauthenticated access
   to sensitive data (implement, not just plan)
2. **Authorization checked server-side** - never trust the client
   to decide what data they can see
3. **Input validation** - validate schema, type, range, length
4. **Rate limiting** - prevent brute force and DoS
5. **HTTPS-only** - reject HTTP, no exceptions

**OWASP API Security Top 10 - most critical:**
1. **BOLA** (Broken Object Level Authorization) = IDOR:
   Can user A access user B's data by changing the object ID?
   This is the #1 API vulnerability.
2. **Broken Authentication:** Weak tokens, missing expiry,
   no brute force protection
3. **Excessive Data Exposure:** API returns more fields than
   the client needs; client filters on frontend only

---

| #040 | Category: Security | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Authentication, Security Fundamentals, Input Validation, JWT, OAuth, CORS, HTTPS, Session Security | |
| **Used by:** | IDOR, Business Logic, Advanced XSS, CORS Misconfiguration | |
| **Related:** | OWASP API Top 10, JWT, OAuth, CORS, IDOR | |

---

### 🔥 The Problem This Solves

**BOLA/IDOR IS THE #1 API VULNERABILITY (AND MOST MISUNDERSTOOD):**
Many developers implement authentication (login required)
but forget authorization (can this SPECIFIC user access THIS
SPECIFIC resource?). A secure auth check:

```
# INCOMPLETE (authentication only):
def get_order(order_id):
    if not current_user:  # Authenticated?
        return 401
    return db.get_order(order_id)  # Returns ANY order!

# COMPLETE (authentication + authorization):
def get_order(order_id):
    if not current_user:
        return 401
    order = db.get_order(order_id)
    if order.user_id != current_user.id:  # Owner?
        return 403
    return order
```

An attacker enumeration: `GET /api/orders/1`, `/orders/2`,
`/orders/3` - if the API returns orders for ANY authenticated
user without checking ownership, every order in the system
is exposed. This is BOLA. It's the top API vulnerability
because the fix is a one-line authorization check that many
developers simply forget.

**APIs ARE EXPOSED BY DESIGN:**
Web application UIs limit what users can do. APIs expose
operations directly. A developer might assume the mobile app
only calls the documented endpoints - but an attacker using
Burp Suite or curl can call ANY endpoint with ANY parameters.
"The UI doesn't have a button for that" is not authorization.
Every API endpoint must enforce authorization independently.

---

### 📘 Textbook Definition

**API Security:** Protecting the interfaces that allow systems
to communicate - ensuring only authorized parties can access
authorized operations on authorized data.

**OWASP API Security Top 10 (2023):**
1. **BOLA (Broken Object Level Authorization):** User A accesses
   User B's object by manipulating object IDs in requests.
2. **Broken Authentication:** Weak/missing token validation,
   no expiry, brute force possible.
3. **Broken Object Property Level Authorization:** API returns
   more properties than the caller should see; or accepts
   more properties than intended (mass assignment).
4. **Unrestricted Resource Consumption:** No rate limiting,
   large payload acceptance, expensive operations exposed.
5. **Broken Function Level Authorization:** Regular user can
   call admin endpoints.
6. **Unrestricted Access to Sensitive Business Flows:** Critical
   flows (checkout, OTP request) not rate-limited per resource.
7. **Server-Side Request Forgery (SSRF):** API fetches URLs
   from user input, reaching internal services.
8. **Security Misconfiguration:** CORS too permissive, debug
   modes enabled, missing security headers.
9. **Improper Inventory Management:** Old/deprecated API versions
   still accessible, shadow APIs, unversioned internal APIs.
10. **Unsafe Consumption of APIs:** Downstream APIs trusted
    implicitly without input validation.

**API Authentication Options:**
- **JWT Bearer token** (`Authorization: Bearer <JWT>`): Stateless,
  widely used for REST APIs. No CSRF (custom header, not cookie).
- **API Keys** (`X-API-Key: <key>`): For server-to-server or
  developer access. Must be long, random, stored hashed in DB.
- **OAuth 2.0 Access Tokens:** Delegated authorization. Short-lived.
- **mTLS (Mutual TLS):** Client presents a certificate. Used for
  service-to-service (zero-trust, high-security).
- **Session cookies:** Traditional web app sessions. Require CSRF
  protection (SameSite=Lax or CSRF tokens).

**Rate Limiting:**
Controls the number of requests a client can make in a time window.
Dimensions: per-user, per-IP, per-endpoint, per-key.
Algorithms: token bucket, leaky bucket, fixed window, sliding window.
HTTP response: 429 Too Many Requests with Retry-After header.
Purpose: prevent brute force (login, OTP), DoS, expensive query abuse.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Check auth on every request, check authorization per object
(not just authentication), validate all input, limit request
rates, use HTTPS, and never return more data than needed.

**One analogy:**
> An API is a bank teller window.
> Authentication: verify the ID card (who are you?).
> Authorization: verify the account number on the form
> belongs to the person with that ID card (can you access THIS?).
> Input validation: the teller checks that the withdrawal
> form is filled out correctly before processing.
> Rate limiting: the bank limits how many transactions
> per minute at each window to prevent a single customer
> from monopolizing service.
> Excessive data exposure: the teller gives you your account
> balance, not all customer balances (server-side filtering,
> not client-side filtering).

---

### 🔩 First Principles Explanation

**BOLA/IDOR: why authorization is checked per-object, not per-endpoint:**

```
BOLA VULNERABILITY - FULL ANALYSIS:

ENDPOINT: GET /api/v1/orders/{order_id}

CODE PATTERN 1 (VULNERABLE - No authorization):
  def get_order(order_id: int):
      order = db.query(Order).filter(Order.id == order_id).first()
      if not order:
          return 404
      return order  # Returns ANY order to ANY authenticated user
  
  Attack: attacker authenticates as user@evil.com
    GET /api/v1/orders/1   → returns order of user 1 (not attacker)
    GET /api/v1/orders/2   → returns order of user 2
    GET /api/v1/orders/100 → returns order of user N
    Loop: GET /api/v1/orders/{1..999999} → all orders exposed

CODE PATTERN 2 (CORRECT - Object-level authorization):
  def get_order(order_id: int, current_user: User):
      order = db.query(Order).filter(Order.id == order_id).first()
      if not order:
          return 404
      if order.user_id != current_user.id:  ← ownership check
          return 403  # Don't reveal whether the order exists
      return order
  
  Attack: attacker authenticates as user@evil.com (user_id=42)
    GET /api/v1/orders/1
    Server: order.user_id=1 != current_user.id=42 → 403
    Attacker cannot see other users' orders.
  
  IMPORTANT: Return 403, not 404, for authorization failures
    against existing resources? OWASP recommends consistency:
    return 404 for resources the caller should not know exist
    (prevents enumeration of whether the ID exists at all).
    For resources the user knows exist but can't access: 403.
    Choose one approach consistently.

INDIRECT OBJECT REFERENCE MITIGATION (additional layer):
  Problem: sequential integer IDs (1, 2, 3) are easily enumerable.
  
  Option 1: Use UUIDs (unpredictable, not enumerable)
    GET /api/v1/orders/550e8400-e29b-41d4-a716-446655440000
    Attacker cannot enumerate: UUID space is too large to guess.
    NOT a substitute for authorization (UUIDs can be leaked),
    but adds a layer of obscurity.
  
  Option 2: Use indirect references (user-scoped)
    GET /api/v1/orders/1  ← "1" is user's 1st order, not global ID 1
    Map: user-scoped reference → global ID at API layer
    User 42's order 1 → global ID 9847
    Attacker manipulating "1" gets their own order (wrong global ID)

BOLA IN THE WILD:
  - Facebook 2013: manipulate photo album ID to access private albums
  - Venmo 2019: transaction IDs were sequential, public by default
  - Parler 2021: sequential post IDs without authentication allowed
    bulk download of entire public post archive
```

---

### 🧪 Thought Experiment

**SCENARIO: Securing a REST API that serves multiple tenants**

```
CONTEXT: SaaS application, multiple companies use the same API
  Company A users cannot see Company B data.
  
NAIVE APPROACH (common mistake):
  API endpoints accept company_id parameter:
  GET /api/data?company_id=1  → Company A data
  GET /api/data?company_id=2  → Company B data
  
  Validation:
  def get_data(company_id: int, current_user: User):
      if current_user.is_authenticated:  ← Only auth check
          return db.get_company_data(company_id)
  
  Attack: Company B user changes company_id=1 in request.
    Gets Company A data. BOLA.

CORRECT APPROACH: Trust user's identity, not request parameters

  PATTERN 1: Derive company from token
    current_user.company_id comes from the JWT/session
    (set by server at login, cannot be forged by client)
    
    def get_data(current_user: User):
        # No company_id parameter: always use current user's company
        return db.get_company_data(current_user.company_id)
    
    Attack: Company B user CANNOT specify company_id.
      API always uses company_id from their authenticated identity.
  
  PATTERN 2: If cross-company access needed (admin use case)
    Explicitly model cross-company access:
    
    def get_company_data(company_id: int, current_user: User):
        # Is user from the requested company?
        if current_user.company_id == company_id:
            return db.get_company_data(company_id)
        # Is user a super-admin with cross-company access?
        elif current_user.is_super_admin:
            audit_log(current_user, 'cross-company-access', company_id)
            return db.get_company_data(company_id)
        else:
            return 403
    
    All cross-company access is explicit, modeled, and audited.

RATE LIMITING FOR TENANT FAIRNESS:
  Without rate limiting: one tenant can flood the API,
    impacting all other tenants (noisy neighbor problem).
  
  Rate limit by: tenant_id (not just IP)
  IP-based: proxy/NAT may share IP across all users.
  tenant_id rate limit: fair quota per company.
  
  429 response includes: Retry-After header
    Retry-After: 30  (try again in 30 seconds)
```

---

### 🧠 Mental Model / Analogy

> API security is like layers of access control at a hospital.
> 
> Authentication: ID badge to enter the building.
> Without it: you can't even get in.
> 
> Function-level authorization (OWASP API #5): only doctors
> can enter the operating theater. A nurse badge doesn't
> allow admin access to billing systems.
> 
> Object-level authorization (BOLA): Dr. Smith can only view
> records for Dr. Smith's patients. Showing a valid doctor
> badge doesn't grant access to every patient record.
> 
> Input validation: the pharmacy doesn't dispense whatever
> quantity a prescription says - it validates dosage ranges.
> 
> Rate limiting: one patient can't monopolize all doctor
> appointments (resource quota). Emergency protocols exist
> for urgent cases.
> 
> Excessive data exposure: the receptionist tells callers
> whether a patient is admitted or not - not the patient's
> full medical history. Minimum necessary information per role.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
APIs are like automated service windows. Security means:
checking ID at the door (authentication), checking which
services the person can use (authorization), limiting how
fast people can make requests (rate limiting), and only
telling people what they need to know (minimal data exposure).
The biggest mistake: checking that someone has a valid ID
card but not checking if the service they're requesting
is actually theirs to use.

**Level 2 - How to use it (junior developer):**
For every API endpoint: check authentication (JWT or session)
and check authorization (does this user own this resource?).
Add rate limiting to login/OTP/sensitive endpoints. Use HTTPS.
Return 401 for unauthenticated, 403 for unauthorized, 429 for
rate-limited. Validate request bodies against a schema (Pydantic,
JSONSchema). Don't return passwords/internal IDs/fields the
caller doesn't need. Read the OWASP API Security Top 10.

**Level 3 - How it works (mid-level engineer):**
BOLA is the critical pattern: every endpoint accessing a resource
by ID must verify ownership (resource.user_id == current_user.id
or equivalent). OpenAPI/Swagger security section documents auth
requirements per endpoint. Rate limiting with Redis: token bucket
per user/IP using `redis-py-ratelimit` or Kong/nginx-based.
Versioning: deprecated API versions (v1) must still be secured
even if officially deprecated - attackers use old versions
specifically because they're less maintained. Shadow APIs: undocumented
internal endpoints that developers expose accidentally; API
inventory requires discovery scans.

**Level 4 - Why it was designed this way (senior/staff):**
OWASP Web Application Top 10 and OWASP API Top 10 are separate
lists because API vulnerabilities differ from web app
vulnerabilities. Web apps have a browser as a thin client
with limited functionality. APIs expose business logic
directly. BOLA dominates API vulnerabilities because:
APIs are designed to be called programmatically (easy enumeration),
object IDs are often visible in requests (unlike session-managed
web forms), and authorization at the object level is a design
concern that emerges late in development. API gateways (Kong,
AWS API Gateway, Apigee) centralize rate limiting, auth,
and logging - reducing the burden on individual services
to implement these correctly.

**Level 5 - Mastery (distinguished engineer):**
GraphQL APIs have unique security challenges: field-level
authorization (not endpoint-level), introspection exposure
(disable in production), query complexity attacks (deeply
nested queries exhaust server), and batching attacks
(N+1 through aliases). API contract testing (Dredd,
Schemathesis) can be extended to test authorization:
"call every endpoint with a different user's credentials
and verify 403 responses." Rate limiting strategies:
sliding window (fairer distribution) vs fixed window
(burst at window reset). Leaky bucket (smooth rate enforcement)
vs token bucket (burst-tolerant with sustained limit).
API security posture management tools (Salt Security, Traceable)
use behavioral analysis to detect BOLA/IDOR attacks that bypass
parameter-level controls by analyzing access patterns.

---

### ⚙️ How It Works (Mechanism)

**JWT authentication middleware and authorization pattern:**

```
REQUEST PROCESSING PIPELINE:

Incoming Request
     │
     ▼
┌────────────────────────────────────┐
│  1. Authentication Middleware      │
│                                    │
│  Extract: Authorization header     │
│  Format: Bearer <token>           │
│                                    │
│  Validate JWT:                     │
│  - Signature (HS256/RS256)         │
│  - Expiry (exp claim)              │
│  - Audience (aud claim)            │
│  - Issuer (iss claim)              │
│                                    │
│  If invalid: return 401            │
│  If valid: attach user to request  │
└────────────────────────────────────┘
     │
     ▼
┌────────────────────────────────────┐
│  2. Rate Limiting Middleware       │
│                                    │
│  Key: user_id or IP                │
│  Window: sliding 1-minute          │
│  Limit: 100 requests/min           │
│                                    │
│  Redis: INCR/EXPIRE per key        │
│  If over limit: return 429         │
│  Retry-After: seconds until reset  │
└────────────────────────────────────┘
     │
     ▼
┌────────────────────────────────────┐
│  3. Route Handler                  │
│                                    │
│  Input validation:                 │
│  - Schema validation (Pydantic)    │
│  - Type/range/length checks        │
│  - If invalid: return 400          │
│                                    │
│  Business logic:                   │
│  - Fetch resource by ID            │
│  - Authorization check:            │
│    resource.user_id == request.user.id?  │
│  - If not authorized: return 403   │
│                                    │
│  Response:                         │
│  - Only return needed fields       │
│  - No internal IDs, passwords,     │
│    implementation details          │
└────────────────────────────────────┘
     │
     ▼
Response to Client

REDIS RATE LIMITING IMPLEMENTATION:
  def check_rate_limit(user_id: str, limit: int, window: int) -> bool:
      key = f"ratelimit:{user_id}"
      pipe = redis.pipeline()
      pipe.incr(key)
      pipe.expire(key, window)
      count, _ = pipe.execute()
      return count <= limit  # True = OK, False = rate limited
```

---

### 💻 Code Example

**FastAPI with authentication, authorization, and rate limiting:**

```python
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
import jwt
import redis
from pydantic import BaseModel, constr
from typing import Optional
import time

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
r = redis.Redis(host='localhost', port=6379, db=0)

# Request schema with validation
class OrderRequest(BaseModel):
    item_id: int
    quantity: int  # Pydantic validates type (not str, not float)
    notes: Optional[constr(max_length=500)] = None  # Length limit

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """JWT authentication: validates token, returns user."""
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=["RS256"],
            options={"require": ["exp", "sub", "iss"]},
        )
        user_id = payload["sub"]
        return get_user_by_id(user_id)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def check_rate_limit(identifier: str, limit: int = 60,
                     window: int = 60):
    """Sliding window rate limiter using Redis."""
    now = time.time()
    key = f"ratelimit:{identifier}"
    
    # Remove expired entries
    r.zremrangebyscore(key, 0, now - window)
    
    # Count requests in window
    count = r.zcard(key)
    if count >= limit:
        raise HTTPException(
            status_code=429,
            headers={"Retry-After": str(window)},
            detail="Rate limit exceeded"
        )
    
    # Add current request
    r.zadd(key, {str(now): now})
    r.expire(key, window)

@app.get("/api/v1/orders/{order_id}")
async def get_order(
    order_id: int,
    request: Request,
    current_user = Depends(get_current_user)
):
    # Rate limiting per user
    check_rate_limit(f"user:{current_user.id}")
    
    # Fetch resource
    order = db.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404)
    
    # AUTHORIZATION: object-level check
    # BAD: if not current_user: raise 401  (auth only)
    # GOOD: check ownership
    if order.user_id != current_user.id:
        # OWASP: return 404 to avoid confirming order exists
        raise HTTPException(status_code=404)
    
    # Return only necessary fields
    # BAD: return order  (all fields including internal ones)
    # GOOD: explicit field selection
    return {
        "id": order.id,
        "items": order.items,
        "total": order.total,
        "status": order.status,
        "created_at": order.created_at,
        # Not returning: order.internal_cost, order.user_id, etc.
    }

@app.post("/api/v1/orders")
async def create_order(
    order: OrderRequest,
    current_user = Depends(get_current_user)
):
    # Input validation handled by Pydantic schema above
    # quantity is int (Pydantic), notes is max 500 chars
    check_rate_limit(f"user:{current_user.id}")
    
    # Never trust user-supplied user_id
    # BAD: db.create_order(user_id=order.user_id, ...)
    # GOOD: use authenticated user's ID
    new_order = db.create_order(
        user_id=current_user.id,  # From token, not request body
        item_id=order.item_id,
        quantity=order.quantity,
        notes=order.notes,
    )
    return {"id": new_order.id, "status": "created"}
```

---

### ⚖️ Comparison Table

| OWASP API Risk | Category | Mitigation |
|:---|:---|:---|
| **BOLA (#1)** | Authorization | Object-level ownership check on every resource access |
| **Broken Auth (#2)** | Authentication | Strong JWT validation, expiry, brute force protection |
| **Broken Property Auth (#3)** | Authorization | Explicit response schema, denylist write fields |
| **Resource Consumption (#4)** | Rate Limiting | Per-user/IP limits, request size limits, pagination |
| **Function-Level Auth (#5)** | Authorization | Role-based checks on admin/sensitive endpoints |
| **Sensitive Flows (#6)** | Rate Limiting | Per-user OTP/checkout rate limits |
| **SSRF (#7)** | Input Validation | Validate/allowlist URLs in API params |
| **Security Misconfig (#8)** | Configuration | CORS policy, debug off, security headers |
| **Inventory (#9)** | Governance | API catalog, sunset old versions |
| **Unsafe Consumption (#10)** | Input Validation | Validate downstream API responses |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| API keys in request parameters are secure | API keys in URL parameters (`?api_key=...`) are logged by every web server, proxy, CDN, and API gateway. They appear in browser history and server access logs. API keys must be in headers (`Authorization: Bearer` or `X-API-Key`), never in URLs. Additionally: API keys must be long (256+ bit random), stored hashed in the database (same as passwords - `select where hashed_key == bcrypt(submitted_key)`), and revocable immediately without reissuing to other clients. |
| Rate limiting at the application level is sufficient | Application-level rate limiting (Redis, in-memory) can be bypassed if an attacker floods the server with requests before the rate limiter processes them (race conditions, multiple application instances without shared state). Infrastructure-level rate limiting (API gateway, nginx, AWS WAF, CloudFront) provides rate limiting before requests reach the application. Defense in depth: infrastructure-level rate limiting blocks volumetric attacks; application-level catches cases that bypass infrastructure (authenticated user quotas). Both layers together are more reliable than either alone. |

---

### 🚨 Failure Modes & Diagnosis

**Testing API authorization:**

```
BOLA TESTING METHODOLOGY:

1. Authenticate as User A, capture session/JWT
2. Create a resource as User A (e.g., POST /orders → order_id=123)
3. Authenticate as User B (different account)
4. Attempt: GET /orders/123 with User B credentials
   Expected: 403 or 404 (not User B's order)
   Vulnerable: 200 OK with User A's order data

AUTOMATED BOLA TESTING (simple script):
  user_a_token = get_jwt("userA@test.com", "password")
  user_b_token = get_jwt("userB@test.com", "password")
  
  # Create order as User A
  order = create_order(user_a_token, item="laptop", qty=1)
  order_id = order["id"]
  
  # Attempt to access as User B
  response = requests.get(
    f"/api/orders/{order_id}",
    headers={"Authorization": f"Bearer {user_b_token}"}
  )
  
  assert response.status_code in [403, 404], \
    f"BOLA VULNERABILITY: User B accessed User A's order"

FUNCTION-LEVEL AUTHORIZATION TEST:
  Regular user token:
  1. Find admin endpoints (from API docs, JS source, or fuzzing)
     Common patterns: /admin/, /api/admin/, /internal/, /manage/
  2. Call admin endpoint with regular user token
     Expected: 403 Forbidden
     Vulnerable: 200 OK or 500 error (endpoint exists, processes request)

RATE LIMITING TEST:
  for i in range(200):
    response = requests.post("/api/login", 
      json={"username": "test@example.com", "password": f"wrong{i}"})
    if response.status_code == 429:
      print(f"Rate limited after {i} attempts")
      break
  else:
    print("No rate limiting on login endpoint")
```

---

### 🔗 Related Keywords

**Prerequisites:**
- `Authentication Fundamentals` - who is calling the API
- `JWT` - token format for API authentication
- `OAuth 2.0` - delegated API authorization
- `CORS` - browser API cross-origin access
- `Input Validation vs Output Encoding` - API input validation

**Builds on this:**
- `IDOR` - detailed BOLA/IDOR coverage
- `CORS Misconfiguration` - API CORS attacks
- `Business Logic Vulnerabilities` - API-level business logic flaws

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ BOLA (IDOR)  │ Check ownership on EVERY object access    │
│ (#1 threat)  │ resource.user_id == current_user.id       │
├──────────────┼───────────────────────────────────────────┤
│ AUTH         │ 401 = unauthenticated                     │
│              │ 403 = unauthorized (authenticated, no perm)│
│              │ JWT in header (not cookie) = no CSRF      │
├──────────────┼───────────────────────────────────────────┤
│ INPUT        │ Validate schema/type/range (Pydantic)     │
│              │ Reject unknown fields (no mass assignment) │
├──────────────┼───────────────────────────────────────────┤
│ RATE LIMIT   │ Per-user AND per-IP (use Redis)           │
│              │ 429 + Retry-After for rate-limited resp   │
├──────────────┼───────────────────────────────────────────┤
│ DATA         │ Return only needed fields (explicit list)  │
│              │ Never: return ORM model directly           │
└──────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
"Authorization is a per-resource concern, not a per-endpoint concern."
Many developers think about authorization at the endpoint level:
"is this endpoint accessible to this role?" But BOLA happens
within an accessible endpoint: the endpoint is accessible,
but the specific OBJECT is not. Authorization must be checked
at both levels: "can this user call this endpoint?" (function
level) AND "does this user have access to this specific resource?"
(object level). This two-level authorization model appears
everywhere: file system permissions (can the user execute this
program? AND can the program read this file?), database access
(can this role SELECT from this table? AND does the row's
tenant_id match the user's tenant?). Never collapse these two
concerns into one check.

---

### 💡 The Surprising Truth

The Venmo API was publicly accessible without authentication
for years. In 2019, a researcher demonstrated scraping millions
of public transactions - names, amounts, and emoji-message
descriptions of payments ("rent", "drugs", "therapy") - all
publicly visible and accessible via the API without any
authentication. Venmo's design decision (transactions public
by default) combined with a public API that lacked auth
created a privacy database that researchers and journalists
mined for behavior analysis. The lesson: "publicly accessible
by design" is not the same as "should be bulk-accessible via
API without any controls." Even public data benefits from
rate limiting (to prevent bulk harvesting), pagination enforcement
(no unbounded dumps), and authentication (to establish accountability
for who is accessing what). OWASP API #9 (Improper Inventory
Management) and #4 (Resource Consumption) apply even to
"publicly intended" APIs.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **IDENTIFY** BOLA/IDOR vulnerabilities in code review:
   look for endpoint handlers that don't compare object owner
   to current user.
2. **IMPLEMENT** JWT authentication middleware with expiry,
   signature, and claims validation in your framework.
3. **ADD** Redis-based rate limiting to a login endpoint
   with 429 responses and Retry-After headers.
4. **TEST** API authorization by authenticating as User B
   and attempting to access User A's resources.

---

### 🎯 Interview Deep-Dive

**Q: What is BOLA/IDOR and how do you prevent it in an API?
Walk me through the fix.**

*Why they ask:* BOLA is the #1 OWASP API vulnerability.
Tests whether the candidate understands why auth alone is
insufficient and can implement the correct authorization check.

*Strong answer includes:*
- BOLA (Broken Object Level Authorization) = same as IDOR: user A
  accesses user B's data by changing the object ID in the request
  (e.g., `GET /api/orders/123` where 123 belongs to another user).
- The root cause: authentication check (is the user logged in?)
  is not the same as authorization check (does this user own
  this specific object?). Many developers implement authentication
  but skip the per-object authorization check.
- Fix: every endpoint that retrieves a resource by ID must verify:
  `resource.user_id == current_user.id` (or equivalent ownership/
  permission check). One line of code per handler.
- Prevention patterns: derive the user's resources from their
  identity (SELECT * FROM orders WHERE user_id = current_user.id),
  not from user-supplied IDs. Use UUIDs to reduce enumerability
  (not a fix - still need the auth check, but reduces attack
  surface). Automated testing: authenticate as User B, try to
  access User A's objects, assert 403/404.
- OWASP API Security Top 10 item #1. Example code shown.