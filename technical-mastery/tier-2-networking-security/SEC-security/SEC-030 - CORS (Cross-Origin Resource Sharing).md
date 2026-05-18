---
id: SEC-030
title: "CORS (Cross-Origin Resource Sharing)"
category: "Security"
tier: tier-2-networking-security
folder: SEC-security
difficulty: ★★☆
depends_on: SEC-013, SEC-014, SEC-019, SEC-020
used_by: SEC-088, SEC-108
related: SEC-013, SEC-019, SEC-020, SEC-029, SEC-088, SEC-108
tags:
  - security
  - cors
  - same-origin-policy
  - browser-security
  - http-headers
status: complete
version: 4
layout: default
parent: "Security"
grand_parent: "Technical Mastery"
nav_order: 30
permalink: /technical-mastery/sec/cors-cross-origin-resource-sharing/
---

⚡ TL;DR - CORS is the mechanism by which a server grants
permission for browsers to make cross-origin requests.
It's a relaxation of the Same-Origin Policy (SOP), controlled
by HTTP response headers.

SOP by default: browser blocks JavaScript from reading
responses to cross-origin requests. CORS: server says
"I allow origin X to read my responses."

**Key headers:**
- `Access-Control-Allow-Origin`: which origin can read responses.
  `*` = everyone, but cannot be used with `Allow-Credentials: true`.
- `Access-Control-Allow-Credentials: true`: tells browser to
  include cookies in cross-origin requests (requires explicit origin,
  not `*`).
- `Access-Control-Allow-Methods`, `Access-Control-Allow-Headers`:
  used in preflight (OPTIONS) response.

**Critical misconfiguration:** reflecting the `Origin` request header
back unchanged in `Access-Control-Allow-Origin` → any origin can
make credentialed cross-origin requests → equivalent to no CORS.

**CORS does NOT prevent CSRF.** CORS restricts what JavaScript can
READ cross-origin. CSRF is about the server acting on a request.
Browser sends the request before CORS response is checked.

---

| #030 | Category: Security | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | CSRF, HTTPS, Security Headers (HTTP), Same-Origin Policy | |
| **Used by:** | CORS Misconfiguration, Advanced XSS | |
| **Related:** | Same-Origin Policy, CSRF Prevention, Security Headers | |

---

### 🔥 The Problem This Solves

**THE LEGITIMATE CROSS-ORIGIN NEED:**
Same-Origin Policy is browser security. But modern web
architecture is inherently cross-origin: a SPA at
`app.example.com` must call APIs at `api.example.com`.
A CDN serves fonts from `fonts.googleapis.com`. A payment
widget loads from `js.stripe.com`. Without any mechanism
to relax SOP: all cross-origin API calls would fail in
the browser. Every web application would need to be served
from a single origin.

**WHAT CORS ENABLES:**
CORS allows servers to explicitly declare which origins
are permitted to read their responses. `api.example.com`
can declare: "allow `app.example.com` to read my responses."
This is a server-controlled relaxation: the server decides,
not the browser and not the client JavaScript. Malicious
sites cannot grant themselves access to your API - only
your server can grant access.

**THE MISCONFIGURATION RISK:**
Developers encountering CORS errors often "fix" them
by reflecting the Origin header back or setting `*`.
This effectively disables the protection. The result:
any website can make credentialed requests to your API
and read the responses - defeating the security model
CORS was designed to enforce.

---

### 📘 Textbook Definition

**CORS (Cross-Origin Resource Sharing):** A W3C specification
(now WHATWG Fetch standard) implemented by browsers to
relax the Same-Origin Policy in a controlled manner.
The server uses HTTP response headers to declare which
origins are permitted to read its responses.

**Origin:** The combination of scheme, host, and port.
`https://app.example.com:443` and `http://app.example.com:80`
are different origins.

**Simple Requests vs Preflighted Requests:**

**Simple Requests:** Requests that meet specific criteria
(method is GET, POST, or HEAD; only safe headers; content-type
is text/plain, application/x-www-form-urlencoded, or multipart/form-data).
No preflight. Browser makes the request directly.

**Preflighted Requests:** Most API requests (JSON body,
Authorization header, custom headers, PUT/DELETE/PATCH).
Browser first sends `OPTIONS` request to ask: "do you
allow this?" Only proceeds if server responds with matching
CORS headers.

**Key CORS Headers:**

**`Access-Control-Allow-Origin`:** The origin permitted
to read the response. Value: specific origin
(`https://app.example.com`) or `*` (any origin, but
cannot combine with `Allow-Credentials: true`).

**`Access-Control-Allow-Credentials`:** If `true`, browser
includes cookies and HTTP auth in cross-origin requests.
Requires explicit origin in `Allow-Origin` (not `*`).

**`Access-Control-Allow-Methods`:** Methods permitted
in cross-origin requests (in preflight response).

**`Access-Control-Allow-Headers`:** Request headers permitted
in cross-origin requests (in preflight response).

**`Access-Control-Expose-Headers`:** Response headers that
JavaScript can read (default: only safe headers are exposed).

**`Access-Control-Max-Age`:** How long the preflight
response can be cached (seconds).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
CORS = server tells browsers "origin X is allowed to read
my responses." Without matching CORS headers, browser
blocks JavaScript from reading cross-origin responses
(requests still go, JavaScript just can't read the response).

**One analogy:**
> Same-Origin Policy is a border checkpoint: by default,
> content from one country (origin) cannot freely cross to
> another. CORS is a visa program: the destination country
> (server) issues visas (CORS headers) for specific countries
> (origins). When you arrive at the checkpoint with a valid visa:
> you're allowed through. Without a visa: turned away.
> The checkpoint (browser) enforces the rules, but the
> destination country (server) sets the visa policy.
> CORS misconfiguration = issuing visas to everyone without
> checking who they are (reflecting Origin header) = open borders.

---

### 🔩 First Principles Explanation

**How browsers enforce CORS:**

```
SAME-ORIGIN POLICY (SOP) - what CORS relaxes:

  SOP RULE: JavaScript at origin A cannot READ responses
    from requests to origin B.
  
  Note: SOP does NOT prevent making the request.
    The request goes to origin B.
    The response arrives at the browser.
    But JavaScript is blocked from reading the response body.
  
  WHY CORS HEADERS ARE ON RESPONSES, NOT REQUESTS:
    Browser makes the request regardless.
    Browser checks the response headers BEFORE
    letting JavaScript read the response.
    If CORS headers permit: JavaScript reads response.
    If CORS headers deny (or absent): browser blocks
    JavaScript from reading the response body.
    The request already happened.
  
  IMPLICATION FOR SECURITY:
    CORS does NOT prevent requests from being received by the server.
    It only controls what JavaScript can READ.
    Therefore CORS does NOT prevent CSRF.
    CSRF is the server acting on a request.
    CSRF happens even if CORS blocks JavaScript from reading
    the response (the action was already performed).
    CSRF protection requires CSRF tokens or SameSite cookies.

PREFLIGHT FLOW:

  Browser is about to send:
    PUT /api/user/123 (with Authorization header)
    from origin: https://app.example.com
  
  PREFLIGHT:
  Browser → Server:
    OPTIONS /api/user/123
    Origin: https://app.example.com
    Access-Control-Request-Method: PUT
    Access-Control-Request-Headers: Authorization, Content-Type
  
  Server → Browser:
    HTTP/1.1 204 No Content
    Access-Control-Allow-Origin: https://app.example.com
    Access-Control-Allow-Methods: GET, POST, PUT, DELETE
    Access-Control-Allow-Headers: Authorization, Content-Type
    Access-Control-Allow-Credentials: true
    Access-Control-Max-Age: 600
  
  Browser checks: does Allow-Origin match current origin?
    If yes: proceed with actual PUT request.
    If no: block. Error in browser console.
  
  ACTUAL REQUEST:
  Browser → Server:
    PUT /api/user/123
    Origin: https://app.example.com
    Authorization: Bearer eyJ...
    (cookies included if Allow-Credentials: true)
  
  Server → Browser:
    HTTP/1.1 200 OK
    Access-Control-Allow-Origin: https://app.example.com
    Access-Control-Allow-Credentials: true
    [response body]
  
  Browser: Allow-Origin matches → JavaScript can read response.
```

---

### 🧪 Thought Experiment

**SCENARIO: Debugging and securing CORS for a real application**

```
SYSTEM:
  Frontend: https://app.example.com (SPA)
  API:      https://api.example.com (REST API)
  Auth:     Uses cookies (session cookie) for authentication

STEP 1: Developer sees CORS error in browser console:
  "Access to fetch at 'https://api.example.com/profile'
   from origin 'https://app.example.com' has been blocked
   by CORS policy: No 'Access-Control-Allow-Origin' header
   is present on the requested resource."

WRONG FIX 1 (dangerous):
  Add: Access-Control-Allow-Origin: *
  Problem: * cannot be combined with Allow-Credentials: true.
    If they try to add credentials: browser rejects (inconsistency).
    If they don't add credentials: cookies are not sent,
    so authentication fails.

WRONG FIX 2 (critical vulnerability):
  Code: response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin')
  This reflects whatever Origin the request sends.
  Effect: ANY origin can make credentialed requests.
  Attack: evil.com sends requests with cookies to api.example.com.
    → api.example.com sends back the response with Allow-Origin: evil.com.
    → evil.com JavaScript reads the response including authenticated data.
    → Complete authentication bypass.

CORRECT FIX:
  Maintain an allowlist of valid origins.
  
  ALLOWED_ORIGINS = {
    "https://app.example.com",
    "https://staging.example.com",   # if needed
  }
  
  origin = request.headers.get("Origin")
  if origin in ALLOWED_ORIGINS:
      response.headers["Access-Control-Allow-Origin"] = origin
      response.headers["Access-Control-Allow-Credentials"] = "true"
  else:
      # Don't set CORS headers for unknown origins
      # Browser will block access to response
      pass
  
  Result:
    https://app.example.com → gets CORS headers → can read responses
    https://evil.com → no CORS headers → JavaScript cannot read responses
    
  Security: attacker site cannot read authenticated responses
    because CORS headers are not issued for unknown origins.
```

---

### 🧠 Mental Model / Analogy

> CORS is like caller ID for API responses. The browser
> is the receptionist. A call comes in (HTTP request) from
> an unknown number (cross-origin JavaScript). The receptionist
> puts the call through (browser makes the request). When
> the called party answers (server sends response), they
> tell the receptionist "only transfer calls from our main
> office number (allowed origin)." If the caller ID matches:
> the call is put through to the JavaScript. If it doesn't match:
> the receptionist says "sorry, this call can't be connected"
> (browser blocks the response read). The key: the call was
> made, the party answered. Only the reading of the answer
> is controlled. CORS misconfiguration = accepting calls from
> everyone regardless of caller ID.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
CORS decides whether a website can read the answers from
a different website's server. If you're on app.example.com
and your code tries to read data from api.example.com,
the browser checks whether api.example.com gave permission.
If the API says "yes, app.example.com is allowed": data
flows. If it says nothing or "no": the browser blocks
your code from reading the data (the request was still
made, but your code can't see the answer).

**Level 2 - How to use it (junior developer):**
If you see CORS errors in the browser: add CORS headers
in your API server, not your frontend. The frontend can't
fix CORS - it's a server configuration. Add the specific
origin of your frontend to the `Access-Control-Allow-Origin`
header in your API responses. If using credentials (cookies):
set `Access-Control-Allow-Credentials: true` AND use a
specific origin (not `*`). Most frameworks have CORS
middleware - configure it with an explicit allowlist of
origins.

**Level 3 - How it works (mid-level engineer):**
Preflight (OPTIONS) requests cache under `Access-Control-Max-Age`.
High-traffic APIs: set Max-Age to reduce preflight overhead
(each complex request generates two HTTP calls without caching).
Common: `Access-Control-Max-Age: 86400` (24 hours). CORS
validation is browser-enforced only: server-to-server
API calls (curl, backend services) are not subject to CORS.
If your API serves both browsers and backend services:
CORS headers are needed for browser clients, but backend
services ignore CORS headers (they're not browsers). Design
accordingly.

**Level 4 - Why it was designed this way (senior/staff):**
CORS was designed as a browser-enforced extension of
SOP. The browser is the security enforcement point because
it's the context where malicious JavaScript runs. Server-to-server
requests: the requester is a trusted program (curl, your backend),
not potentially-malicious browser JavaScript. The design
correctly separates concerns: CORS protects browser users
from malicious websites reading their data from APIs via
cross-origin requests. It provides no protection against
server-to-server attacks (which require different controls:
authentication, network security, IP allowlisting). The
common confusion: developers add CORS headers thinking
it provides API security. CORS provides browser-context
security for cross-origin reads, nothing more.

**Level 5 - Mastery (distinguished engineer):**
Advanced CORS security includes: the `Origin` header
cannot be spoofed by JavaScript (browser enforces this).
However, server-to-server requests CAN set an arbitrary
Origin header. If your API uses Origin for access control
(relying solely on CORS for API security): backend services
(and server-side SSRF) can bypass it. CORS complements,
but does not replace, proper API authentication. Vary: Origin
response header: if your server reflects the correct CORS
headers based on the request origin, CDNs must be told
to vary caching by Origin (otherwise: CDN returns the
CORS response from one origin to all origins). `Vary: Origin`
tells CDNs to cache separately per request origin. Missing
this causes either CORS failures for non-cached origins
or CORS bypass for origins that receive another origin's
cached response.

---

### ⚙️ How It Works (Mechanism)

**CORS header decision flow in an API server:**

```
CORS DECISION FLOW (server-side logic):

Request arrives at API server:
  Origin: https://app.example.com
  Method: PUT
  Headers: Authorization, Content-Type

1. Is this a preflight OPTIONS request?
   Yes → check requested method and headers
       → respond with Allow-Origin, Allow-Methods, Allow-Headers
       → status 204 (no body needed)
   No → continue to actual request handling

2. Is Origin in allowlist?
   if origin in ALLOWED_ORIGINS:
     Set: Access-Control-Allow-Origin: <origin>
     Set: Access-Control-Allow-Credentials: true  (if using cookies)
     Set: Vary: Origin  (important for CDN caching)
   else:
     Do NOT set CORS headers
     Browser will block the response read

3. Response includes CORS headers → browser allows read
   Response missing CORS headers → browser blocks read

IMPORTANT: The response is always sent.
  CORS headers only control if JavaScript can READ it.
  Server processes the request regardless of CORS.
  This is why CORS doesn't protect against CSRF.

COMPLETE IMPLEMENTATION CHECKLIST:
  ✓ Maintain explicit origin allowlist
  ✓ Never reflect Origin header unconditionally
  ✓ Never use * with Allow-Credentials: true
  ✓ Handle preflight OPTIONS correctly
  ✓ Return Vary: Origin header
  ✓ Validate allowlist on every request (not cached)
  ✓ Log origin rejections for monitoring
  ✗ Don't use CORS as sole API security mechanism
  ✗ Don't add credentials blindly to wildcard responses
```

---

### 💻 Code Example

**Secure CORS middleware (Python FastAPI):**

```python
from fastapi import FastAPI, Request
from fastapi.responses import Response
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# SECURE CORS - explicit allowlist
# Load from environment in production
ALLOWED_ORIGINS = {
    "https://app.example.com",
    "https://staging.app.example.com",
}

# For local development only
DEVELOPMENT_ORIGINS = {
    "http://localhost:3000",
    "http://localhost:5173",
}

# In production: only ALLOWED_ORIGINS
# In development: ALLOWED_ORIGINS | DEVELOPMENT_ORIGINS
import os
if os.getenv("ENVIRONMENT") == "production":
    CORS_ALLOWED_ORIGINS = ALLOWED_ORIGINS
else:
    CORS_ALLOWED_ORIGINS = ALLOWED_ORIGINS | DEVELOPMENT_ORIGINS

app = FastAPI()

@app.middleware("http")
async def cors_middleware(request: Request, call_next):
    origin = request.headers.get("Origin")
    
    # Preflight OPTIONS request
    if request.method == "OPTIONS" and origin:
        if origin in CORS_ALLOWED_ORIGINS:
            return Response(
                status_code=204,
                headers={
                    "Access-Control-Allow-Origin": origin,
                    "Access-Control-Allow-Credentials": "true",
                    "Access-Control-Allow-Methods": (
                        "GET, POST, PUT, PATCH, DELETE, OPTIONS"
                    ),
                    "Access-Control-Allow-Headers": (
                        "Authorization, Content-Type, X-CSRF-Token"
                    ),
                    "Access-Control-Max-Age": "86400",
                    "Vary": "Origin",
                }
            )
        else:
            # Unknown origin - reject preflight
            logger.warning(f"CORS preflight rejected from: {origin}")
            return Response(status_code=403)
    
    # Actual request
    response = await call_next(request)
    
    if origin and origin in CORS_ALLOWED_ORIGINS:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        # CRITICAL: Vary header for CDN caching correctness
        response.headers["Vary"] = "Origin"
    elif origin:
        # Origin not in allowlist - no CORS headers
        # Browser will block JavaScript from reading response
        logger.info(f"CORS headers not set for origin: {origin}")
        # Do NOT set CORS headers - browser enforces the block
    
    return response


# BAD PATTERNS - never do these:

# BAD 1: Reflect any origin (wildcard equivalent)
# headers["Access-Control-Allow-Origin"] = request.headers.get("Origin")
# ↑ Any origin can make credentialed requests and read responses.

# BAD 2: Wildcard with credentials
# headers["Access-Control-Allow-Origin"] = "*"
# headers["Access-Control-Allow-Credentials"] = "true"
# ↑ Browsers reject this combination.
# But some misconfigured code tries to work around it in
# ways that create vulnerabilities.

# BAD 3: null origin allowed
# if origin == "null" or origin in allowed: set headers
# ↑ null origin: sandboxed iframes, file:// URIs, some redirects.
# Attackers use sandboxed iframes to set Origin: null.
# Never add "null" to your allowlist.
```

---

### ⚖️ Comparison Table

| Scenario | SOP Behavior | CORS Fix |
|:---|:---|:---|
| SPA at app.com → api.app.com | Blocked (cross-origin) | Allow-Origin: https://app.com |
| fetch with cookies cross-origin | Blocked (credentials) | Allow-Origin: explicit + Allow-Credentials: true |
| PUT/DELETE/custom headers | Preflight OPTIONS first | Handle OPTIONS, return Allow-Methods + Allow-Headers |
| `*` as Allow-Origin | Allows all origins to READ | Never use * with credentials |
| Backend service → API | Not subject to CORS (not browser) | No CORS config needed (use API auth) |
| `null` origin in Allow-Origin | Sandboxed iframes bypass SOP | Never allowlist `null` |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| CORS prevents CSRF attacks | CORS controls whether JavaScript can READ cross-origin responses. CSRF is about the server ACTING on a cross-origin request. The browser still sends the request (with cookies) before checking CORS. The CSRF action occurs server-side regardless. CORS does not prevent state changes caused by cross-origin requests. CSRF requires dedicated protection: CSRF tokens, or SameSite=Lax/Strict cookie attribute. |
| CORS is security for APIs | CORS is browser-specific security for cross-origin reads. Server-to-server requests (curl, Postman, your backend code) are not browsers and do not enforce CORS. If you rely on CORS for API security: any non-browser client bypasses all CORS restrictions. API security requires proper authentication (JWT, OAuth, API keys) verified server-side on every request, regardless of CORS headers. |

---

### 🚨 Failure Modes & Diagnosis

**Diagnosing CORS issues:**

```
SYMPTOM: CORS error in browser console
  "Cross-Origin Request Blocked: The Same Origin Policy
   disallows reading the remote resource..."

DIAGNOSIS CHECKLIST:
  1. Inspect the failing request in DevTools → Network tab.
  2. Look at the OPTIONS preflight (if present).
     Does the response have CORS headers?
  3. If preflight is missing or 404:
     → Your server isn't handling OPTIONS requests.
     → Most frameworks: configure CORS middleware to handle OPTIONS.
  4. If preflight is present but origin doesn't match:
     → Your server's allowlist doesn't include the requesting origin.
     → Check: is your frontend URL exactly in the allowlist?
       (protocol, subdomain, port ALL must match exactly)
  5. If Allow-Origin is * but you need credentials:
     → Browser rejects: wildcard + credentials are incompatible.
     → Use explicit origin instead of *.
  
COMMON EXACT-MATCH ISSUES:
  Allowlist:  "https://app.example.com"  (no trailing slash)
  Request:    "https://app.example.com/" (trailing slash)
  Result: MISMATCH → CORS blocked
  
  Allowlist:  "https://app.example.com"
  Request:    "http://app.example.com"   (HTTP not HTTPS)
  Result: MISMATCH → CORS blocked
  
  Always use exact values as seen in browser's Origin header.
  Inspect with: request.headers.get("Origin") and log it.

SECURITY MISCONFIGURATION CHECK:
  Is your server reflecting Origin back without checking allowlist?
  Test: send request with Origin: https://evil.com
  If response has: Access-Control-Allow-Origin: https://evil.com
  → CRITICAL: origin reflection vulnerability.
  → Any site can make credentialed requests and read responses.
  → Fix: implement allowlist check.
```

---

### 🔗 Related Keywords

**Prerequisites:**
- `CSRF` - what CORS doesn't prevent
- `Security Headers (HTTP)` - CORS headers are security headers
- `Same-Origin Policy` - what CORS relaxes

**Builds on this:**
- `CORS Misconfiguration` - deeper attack scenarios
- `Advanced XSS` - how XSS bypasses SOP/CORS

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ CORS         │ Server controls which origins can READ    │
│              │ cross-origin responses in browsers        │
├──────────────┼───────────────────────────────────────────┤
│ KEY HEADERS  │ Allow-Origin: <specific origin> OR *      │
│              │ Allow-Credentials: true (with specific)   │
│              │ Vary: Origin (CDN cache safety)           │
├──────────────┼───────────────────────────────────────────┤
│ PREFLIGHT    │ OPTIONS request sent before complex reqs  │
│              │ Server must respond with Allow-* headers  │
├──────────────┼───────────────────────────────────────────┤
│ CRITICAL RULE│ NEVER reflect Origin header unconditionally│
│              │ ALWAYS use explicit allowlist             │
│              │ null origin is NOT safe to allow          │
├──────────────┼───────────────────────────────────────────┤
│ MISCONCEPTION│ CORS ≠ CSRF protection                    │
│              │ CORS ≠ API authentication                 │
│              │ CORS = browser read control only          │
└──────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
"Security controls that rely on the requester's environment
are weak." CORS is browser-enforced: it works perfectly
in browsers. Server-to-server requests bypass it completely.
This pattern appears throughout security: client-side
validation (user can bypass), CORS (backend bypasses),
JavaScript obfuscation (decompile and bypass). For any
security control: ask "can the attacker bypass this by
not using the expected client?" If yes: the control must
also be enforced server-side. CORS is valid as a browser-focused
control because its threat model is specifically browser-based
(malicious JavaScript at another origin). But it must be
combined with server-side auth for complete API security.

---

### 💡 The Surprising Truth

CORS errors are one of the most Googled issues by web
developers, and the most common "solution" found online
is to set `Access-Control-Allow-Origin: *`. This eliminates
the developer's CORS error - and simultaneously removes
all read protection from the API for browser clients.
The advice works because it solves the immediate technical
problem (browser error goes away) while creating a security
problem that's invisible during development (developers
test their own site, which would have been allowed anyway).
The security flaw only manifests when an attacker site
tries to read the API response - and that test doesn't
happen during development. This gap between "it works
for me" and "it's secure" is why CORS misconfiguration
appears in OWASP's security risks. The lesson: security
configurations that fail silently on the happy path but
fail dangerously on adversarial paths require deliberate
security testing, not just "does it work" development testing.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN** why CORS is on response headers (not request
   headers), and why the request is still sent even if CORS
   will block the response read.
2. **CONFIGURE** a secure CORS policy with an origin allowlist,
   including handling of preflight OPTIONS and the Vary header.
3. **IDENTIFY** the origin reflection vulnerability: a server
   that echoes `Origin` back unconditionally in `Allow-Origin`.
4. **EXPLAIN** why CORS doesn't prevent CSRF and what does.

---

### 🎯 Interview Deep-Dive

**Q: How would you diagnose and fix a CORS error, and what
security considerations apply?**

*Why they ask:* CORS errors are common but frequently "fixed"
insecurely. Tests both debugging skill and security awareness.

*Strong answer includes:*
- Diagnosis: open DevTools → Network tab → find the failing
  request. Is there a preflight OPTIONS? Did it succeed (204)?
  Is the `Access-Control-Allow-Origin` header present in the
  response? Does it match the requesting origin exactly?
- Root causes: (a) no CORS headers at all (middleware not configured),
  (b) wrong origin in allowlist (typo, protocol mismatch, port missing),
  (c) OPTIONS request not handled, (d) wildcard with credentials.
- Security-correct fix: explicit allowlist of known origins,
  compare against allowlist (not reflecting), set `Vary: Origin`
  for CDN safety.
- What NOT to do: wildcard (`*`) if credentials needed, reflecting
  the Origin header unconditionally, allowing `null` origin.
- Clarify the misconceptions: CORS doesn't prevent CSRF (server
  still acts on the request before CORS check). CORS doesn't
  secure APIs from non-browser clients. It's a browser-specific
  read control.
- Common scenario: API serves browsers AND backend services.
  CORS headers needed for browsers. Backend services: no CORS
  enforcement (not browsers). API authentication (JWT) is
  required for both, independently of CORS.