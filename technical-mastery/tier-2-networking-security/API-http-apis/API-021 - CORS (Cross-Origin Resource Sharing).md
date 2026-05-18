---
id: API-021
title: "CORS (Cross-Origin Resource Sharing)"
category: "HTTP & APIs"
tier: tier-2-networking-security
folder: API-http-apis
difficulty: ★★☆
depends_on: API-007, API-008, API-010
used_by: API-057, API-060
related: API-016, API-022, API-023
tags:
  - cors
  - security
  - http
  - browser
  - same-origin-policy
status: complete
version: 4
layout: default
parent: "HTTP & APIs"
grand_parent: "Technical Mastery"
nav_order: 21
permalink: /technical-mastery/api/cors-cross-origin-resource-sharing/
---

⚡ TL;DR - CORS is the browser security mechanism that
controls which cross-origin HTTP requests are permitted;
the server communicates its policy via `Access-Control-*`
response headers, and the browser enforces it - not the
server. Preflight OPTIONS requests carry the heavy lifting
for non-simple requests.

---

| #021 | Category: HTTP & APIs | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Request Headers, HTTP Status Codes, Request/Response | |
| **Used by:** | OWASP API Top 10, CSRF and SSRF in APIs | |
| **Related:** | API Key Auth, Authentication Schemes, JWT | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
In 1994, browsers implemented the Same-Origin Policy (SOP):
JavaScript can only make HTTP requests to the same origin
(scheme + host + port) as the page it runs on. This is
a fundamental browser security control that prevents a
malicious site from reading your banking data.

**THE BREAKING POINT:**
The web became a platform for SPAs and microservices.
A React app served from `app.example.com` needs to call
`api.example.com`. These are different origins (different
subdomain). SOP blocks the request. Without a mechanism
to relax SOP selectively, every API has to be served from
the exact same origin as the UI - operationally impossible
at scale.

**THE INVENTION MOMENT:**
CORS (2009, later standardized in Fetch spec) lets servers
declare which foreign origins they trust. The server
returns `Access-Control-Allow-Origin: https://app.example.com`
and the browser permits the cross-origin response to be
read by JavaScript. SOP is still enforced by the browser -
CORS only expands which origins are trusted for specific
requests.

---

### 📘 Textbook Definition

CORS (Cross-Origin Resource Sharing) is a browser
mechanism that uses HTTP headers to allow or deny cross-
origin requests made by JavaScript. An origin is the
combination of scheme, host, and port. When JavaScript
at `https://app.example.com` makes a request to
`https://api.example.com`, the browser enforces CORS.
The server signals its policy using `Access-Control-*`
response headers. For "non-simple" requests (PUT, DELETE,
any request with custom headers or non-plain-text body),
the browser first sends an OPTIONS preflight request.
The server must respond with the correct allow headers,
or the browser blocks the actual request before sending it.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
CORS lets a server say "I trust `app.example.com` to
read my responses" - the browser then allows that foreign
JavaScript to access the API response.

**One analogy:**
> SOP is a security guard who blocks everyone entering
> from a different building. CORS is the signed guest
> list: the server tells the guard "let in anyone from
> `app.example.com`." The guard (browser) still controls
> access - the guest list only changes who is permitted.
> The preflight OPTIONS request is checking the guest
> list before the real guest (the actual API call) arrives.

**One insight:**
CORS is enforced by the browser, not the server. Server-
side code returning `Access-Control-Allow-Origin: *` does
not protect the server. It tells the browser it is safe
for any JavaScript to read the response. Non-browser
clients (curl, Postman, other servers) ignore CORS
completely - they never had SOP restrictions.

---

### 🔩 First Principles Explanation

**ORIGIN = scheme + host + port:**
```
https://app.example.com:443  ← origin
https://api.example.com:443  ← DIFFERENT origin
http://app.example.com:443   ← DIFFERENT (scheme differs)
https://app.example.com:8080 ← DIFFERENT (port differs)
```

**SIMPLE REQUESTS (no preflight needed):**
```
Methods: GET, HEAD, POST only
Headers: only safe headers (Accept, Content-Language,
         Content-Type with value
         application/x-www-form-urlencoded,
         multipart/form-data, or text/plain)
→ Browser sends request directly with Origin header
→ Server responds with Access-Control-Allow-Origin
→ Browser checks; if header present and origin matches:
  JavaScript can read the response
```

**NON-SIMPLE REQUESTS (preflight required):**
```
Methods: PUT, DELETE, PATCH
Headers: Authorization, Content-Type: application/json,
         any custom header (X-Request-Id, etc.)

Step 1: Browser sends OPTIONS preflight
  OPTIONS /api/users HTTP/1.1
  Origin: https://app.example.com
  Access-Control-Request-Method: DELETE
  Access-Control-Request-Headers: Authorization

Step 2: Server responds
  HTTP/1.1 204 No Content
  Access-Control-Allow-Origin: https://app.example.com
  Access-Control-Allow-Methods: GET, POST, PUT, DELETE
  Access-Control-Allow-Headers: Authorization, Content-Type
  Access-Control-Max-Age: 86400

Step 3: Browser sends actual DELETE request
  DELETE /api/users/42
  Origin: https://app.example.com
  Authorization: Bearer eyJ...
```

**KEY HEADERS:**

| Header | Direction | Purpose |
|:---|:---|:---|
| `Origin` | Request | Browser sets; the requesting origin |
| `Access-Control-Allow-Origin` | Response | Which origins permitted |
| `Access-Control-Allow-Methods` | Response | Allowed methods |
| `Access-Control-Allow-Headers` | Response | Allowed request headers |
| `Access-Control-Allow-Credentials` | Response | Allow cookies/auth |
| `Access-Control-Max-Age` | Response | Preflight cache TTL |
| `Access-Control-Expose-Headers` | Response | Headers JS can read |
| `Access-Control-Request-Method` | Preflight | Method requested |
| `Access-Control-Request-Headers` | Preflight | Headers requested |

---

### 🧪 Thought Experiment

**SETUP:**
React app at `https://app.acme.com` calls
`https://api.acme.com/users` with `Authorization: Bearer`.

**WITHOUT CORS headers on the API:**
- Browser sends OPTIONS preflight
- Server returns 200 with no CORS headers
- Browser blocks the actual request
- Console: "CORS policy: No 'Access-Control-Allow-Origin'
  header is present"
- curl and Postman work fine (no SOP)

**WITH CORS headers:**
- Server returns:
  `Access-Control-Allow-Origin: https://app.acme.com`
  `Access-Control-Allow-Headers: Authorization`
  `Access-Control-Allow-Methods: GET, POST, PUT, DELETE`
- Browser permits the actual request
- JavaScript can read the response body

**WILDCARD AND CREDENTIALS CONFLICT:**
- `Access-Control-Allow-Origin: *` with
  `Access-Control-Allow-Credentials: true`
- Browser BLOCKS this combination
- Cannot use wildcard when credentials (cookies/auth) are included
- Must specify exact origin(s) when credentials are sent

---

### 🧠 Mental Model / Analogy

> CORS is like an international visitor visa system.
> Your browser is the immigration officer at the border.
> Same-Origin Policy says: "citizens only, no foreign
> visitors." CORS is the visa system: the API country
> (server) issues visas to specific countries
> (Access-Control-Allow-Origin). The immigration officer
> (browser) checks whether the visitor's country is on
> the visa list. If yes, the visitor can enter. If no,
> the visitor is turned away - even if the visitor has
> perfectly valid business. The visa is issued by the
> destination country (server), not the origin country.

Key mappings:
- "Immigration officer" → browser
- "Border" → the Same-Origin Policy check
- "Visitor's home country" → Origin header value
- "Visa list" → Access-Control-Allow-Origin header
- "Preflight" → advance visa application check

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Your browser will not let JavaScript on one website read
responses from a different website. CORS is the system
that lets a server say "it is OK for JavaScript from
`app.example.com` to read my responses." Without CORS,
your bank's website could not load data from a separate
`api.bank.com` domain in JavaScript.

**Level 2 - How to use it (junior developer):**
Add CORS headers to your API responses. At minimum:
`Access-Control-Allow-Origin: https://your-frontend.com`.
For APIs that receive PUT/DELETE or custom headers (like
Authorization), also handle OPTIONS preflight: return 204
with `Access-Control-Allow-Methods` and
`Access-Control-Allow-Headers`. Use framework middleware
instead of setting headers manually.

**Level 3 - How it works (mid-level engineer):**
Browser classifies requests as simple or non-simple.
Non-simple requests trigger a preflight: OPTIONS request
with `Access-Control-Request-Method` and
`Access-Control-Request-Headers`. Server must respond
with allow headers. Browser caches preflight results
for `Access-Control-Max-Age` seconds, reducing OPTIONS
overhead. Credentials (cookies, auth headers) require
both `Access-Control-Allow-Credentials: true` AND
explicit (non-wildcard) origin in allow header.

**Level 4 - Why it was designed this way (senior/staff):**
CORS is a browser-enforced policy. The server declares
its policy; the browser enforces it. This design means
server-side CORS headers are advisory to browsers - they
have no effect on server-to-server calls or non-browser
clients. The threat model is: malicious JavaScript on
`evil.com` trying to read your authenticated response
from `api.bank.com`. CORS defends against this.
CSRF (Cross-Site Request Forgery) is a different attack
that CORS does NOT prevent: a request can be SENT cross-
origin by browser without CORS (e.g., HTML form POST);
the response is just not readable by JavaScript.

**Level 5 - Mastery (distinguished engineer):**
CORS applies only to browser `fetch`/`XMLHttpRequest`.
Server-to-server calls are unaffected. The
`Access-Control-Allow-Origin` header is checked against
the `Origin` request header - not the `Referer`. The
`Vary: Origin` response header is critical: if a CDN
caches a CORS response without `Vary: Origin`, it may
serve a cached response with the wrong
`Access-Control-Allow-Origin` to a different origin,
causing either security issues (over-permission) or
CORS failures (under-permission). Never use
`Access-Control-Allow-Origin: *` with authentication
credentials. For multi-origin APIs: maintain a whitelist,
check `Origin` header against the list, return the exact
matching origin in `Access-Control-Allow-Origin` (not
all origins), and always include `Vary: Origin`.

---

### ⚙️ How It Works (Mechanism)

**Preflight flow:**

```
Browser                          Server
  |                                |
  |  OPTIONS /api/users            |
  |  Origin: https://app.acme.com  |
  |  Access-Control-Request-Method: DELETE
  |  Access-Control-Request-Headers: Authorization
  |-------------------------------->|
  |                                |
  |  204 No Content                |
  |  Access-Control-Allow-Origin: https://app.acme.com
  |  Access-Control-Allow-Methods: GET,POST,PUT,DELETE
  |  Access-Control-Allow-Headers: Authorization
  |  Access-Control-Max-Age: 86400 |
  |<--------------------------------|
  |                                |
  | [preflight passes; send actual request]
  |                                |
  |  DELETE /api/users/42          |
  |  Origin: https://app.acme.com  |
  |  Authorization: Bearer eyJ... |
  |-------------------------------->|
  |  200 OK                        |
  |  Access-Control-Allow-Origin: https://app.acme.com
  |<--------------------------------|
  | [JS can read response]         |
```

```mermaid
sequenceDiagram
    participant B as Browser JS
    participant S as API Server
    B->>S: OPTIONS /api/users (preflight)
    Note right of B: Origin + Request-Method + Request-Headers
    S-->>B: 204 + Access-Control-Allow-* headers
    Note left of S: Max-Age caches preflight result
    B->>S: DELETE /api/users/42 + Authorization
    S-->>B: 200 OK + Access-Control-Allow-Origin
    Note right of B: Browser checks header; JS can read response
```

---

### 🔄 The Complete Picture - End-to-End Flow

**Production CORS middleware (Python/FastAPI):**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

ALLOWED_ORIGINS = [
    "https://app.example.com",
    "https://staging.example.com",
]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
    max_age=86400,
)
```

---

### 💻 Code Example

**Example 1 - BAD: Wildcard with credentials**

```python
# BAD: wildcard + credentials = browser blocks it
@app.after_request
def add_cors_headers_bad(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    # Browser REJECTS this when credentials are sent:
    response.headers[
        "Access-Control-Allow-Credentials"
    ] = "true"
    return response

# GOOD: explicit origin whitelist for credentialed
ALLOWED_ORIGINS = {
    "https://app.example.com",
    "https://admin.example.com",
}

@app.after_request
def add_cors_headers_good(response):
    origin = request.headers.get("Origin", "")
    if origin in ALLOWED_ORIGINS:
        response.headers[
            "Access-Control-Allow-Origin"
        ] = origin
        response.headers[
            "Access-Control-Allow-Credentials"
        ] = "true"
        # Vary: Origin tells CDN to cache per-origin
        response.headers["Vary"] = "Origin"
    return response
```

---

**Example 2 - Preflight handler in Flask**

```python
from flask import Flask, request, jsonify, make_response

ALLOWED_ORIGINS = {
    "https://app.example.com",
    "https://admin.example.com",
}

@app.route("/api/users", methods=["OPTIONS"])
def preflight():
    origin = request.headers.get("Origin", "")
    if origin not in ALLOWED_ORIGINS:
        return make_response("", 403)
    resp = make_response("", 204)
    resp.headers["Access-Control-Allow-Origin"] = origin
    resp.headers["Access-Control-Allow-Methods"] = \
        "GET, POST, PUT, DELETE"
    resp.headers["Access-Control-Allow-Headers"] = \
        "Authorization, Content-Type"
    resp.headers["Access-Control-Max-Age"] = "86400"
    resp.headers["Vary"] = "Origin"
    return resp
```

---

**Example 3 - Diagnosing CORS failures**

```bash
# Simulate browser preflight with curl
curl -v -X OPTIONS https://api.example.com/users \
  -H "Origin: https://app.example.com" \
  -H "Access-Control-Request-Method: DELETE" \
  -H "Access-Control-Request-Headers: Authorization"

# Check response headers:
# < access-control-allow-origin: https://app.example.com
# < access-control-allow-methods: GET, POST, PUT, DELETE
# < access-control-allow-headers: Authorization
# < access-control-max-age: 86400

# If MISSING access-control-allow-origin: CORS blocked
# If DIFFERENT origin in header: CORS blocked
# If OPTIONS returns 405 Method Not Allowed:
#   Server not handling preflight → CORS blocked
```

---

### ⚖️ Comparison Table

| Scenario | Preflight? | Key Headers Needed |
|:---|:---|:---|
| Simple GET, no auth | No | `Access-Control-Allow-Origin` only |
| GET with `Authorization` header | Yes | `ACAO` + `ACAH: Authorization` |
| POST with JSON body | Yes | `ACAO` + `ACAH: Content-Type` |
| DELETE any resource | Yes | `ACAO` + `ACAM: DELETE` |
| Credentialed request (cookies) | Yes | `ACAO` (exact) + `ACAC: true` |

ACAO = Access-Control-Allow-Origin,
ACAH = Access-Control-Allow-Headers,
ACAM = Access-Control-Allow-Methods,
ACAC = Access-Control-Allow-Credentials

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| CORS is a server security feature | CORS is a browser security feature. The server publishes a policy; the browser enforces it. Non-browser clients (curl, server-to-server) are never subject to CORS. |
| `ACAO: *` is safe for public APIs | True for read-only public APIs. Dangerous if the API relies on cookies for authentication - the wildcard allows any origin to trigger authenticated requests. Use explicit origins for authenticated endpoints. |
| CORS prevents CSRF | CORS does NOT prevent CSRF. A cross-origin form POST can be sent without triggering CORS restrictions (it is a simple request). CSRF tokens or `SameSite` cookies are the correct defense. |
| Setting `ACAO: *` fixes all CORS errors | It fixes the header error but breaks credentialed requests. `*` and `allow-credentials: true` are mutually exclusive. |

---

### 🚨 Failure Modes & Diagnosis

**CORS error despite correct headers (CDN caching issue)**

**Symptom:** API works from some origins but not others.
Random CORS failures, not consistent.

**Root Cause:** CDN caches the first response's
`Access-Control-Allow-Origin` header and serves it to
all subsequent requests regardless of their `Origin`.
Response for `app.example.com` is cached and served to
`staging.example.com` - wrong ACAO header.

**Diagnostic:**

```bash
# Check Vary header on response
curl -I https://api.example.com/users \
  -H "Origin: https://app.example.com"
# MUST see: vary: Origin
# If missing: CDN may cache wrong ACAO header
```

**Fix:** Add `Vary: Origin` to all CORS responses.
This tells CDN to cache separate versions per Origin.

---

**Preflight failing with 405 Method Not Allowed**

**Symptom:** API returns 405 for OPTIONS requests.
All non-simple requests blocked.

**Root Cause:** API framework route not configured to
handle OPTIONS method; server returns 405.

**Diagnostic:**
```bash
curl -X OPTIONS https://api.example.com/users -v
# Response: 405 Method Not Allowed
# Missing: CORS middleware or OPTIONS route handler
```

**Fix:** Add CORS middleware that intercepts OPTIONS
requests before routing. In Flask: use `flask-cors`.
In Spring: use `@CrossOrigin` or `WebMvcConfigurer`.
In Nginx: handle preflight at the proxy level.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Request Headers and Response Headers` - CORS is
  implemented entirely through HTTP headers
- `HTTP Status Codes` - 204 for successful preflight,
  403 for rejected origins
- `HTTP Methods` - OPTIONS method is the preflight
  mechanism

**Builds On This (learn these next):**
- `OWASP API Security Top 10` - CORS misconfiguration
  is a common API security vulnerability
- `CSRF and SSRF in APIs` - CORS does not prevent CSRF;
  understanding the distinction is essential
- `JWT` and `OAuth 2.0` - CORS interacts with auth
  headers and cookie-based auth

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Browser mechanism to allow controlled     │
│              │ cross-origin JS requests                  │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Same-Origin Policy blocks SPAs from       │
│ SOLVES       │ calling APIs on different subdomains      │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ CORS is enforced by the browser, not the  │
│              │ server. curl and server-to-server calls   │
│              │ are never subject to CORS.                │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ API is called from browser JS on a        │
│              │ different origin                          │
├──────────────┼───────────────────────────────────────────┤
│ AVOID        │ ACAO: * with credentials (browser blocks) │
│ PATTERNS     │ Missing Vary: Origin (CDN caching bugs)   │
├──────────────┼───────────────────────────────────────────┤
│ PREFLIGHT    │ OPTIONS sent for: non-GET/POST, custom    │
│ TRIGGERS     │ headers (Authorization), JSON body        │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Permissive CORS (wider * allowed origins) │
│              │ vs tight CORS (explicit whitelist)        │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The server posts the guest list; the     │
│              │ browser is the bouncer."                  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Authentication Schemes → JWT → OAuth 2.0  │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. CORS is enforced by the browser. curl, Postman, and
   server-to-server calls are never affected by CORS.
2. `Access-Control-Allow-Origin: *` and
   `Access-Control-Allow-Credentials: true` cannot be
   used together - browser blocks this combination.
3. Always add `Vary: Origin` to CORS responses so CDNs
   do not serve the wrong origin's cached header.

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
CORS is an example of the "policy-separated-from-enforcement"
pattern. The server publishes a policy (headers), and
an independent party (browser) enforces it. This is
the same pattern as Content Security Policy (CSP) and
Certificate Transparency. The benefit: the enforcer
(browser) cannot be manipulated by the policy publisher
(server) to over-enforce or under-enforce.

**Where else this pattern applies:**
- Content Security Policy (CSP): server declares script/
  resource load policy; browser enforces
- HTTP Public Key Pinning (HPKP): server declares valid
  certificate pins; browser enforces
- Transport Layer Security (HSTS): server declares HTTPS-
  only requirement; browser enforces

---

### 💡 The Surprising Truth

CORS does not protect your API from unauthorized access.
A malicious server (not a browser) can call your API
from any origin freely - CORS never applies. CORS only
protects the end user from being victimized: it prevents
`evil.com` JavaScript from reading responses from
`your-bank.com` while the user is logged in. Your API
still needs authentication (`Authorization` header,
API keys, OAuth tokens) to protect the actual resources.
CORS is "protect the user's browser from being weaponized"
not "protect the server from unauthorized requests."

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN** Describe what CORS protects against, who
   enforces it, and why server-to-server calls are unaffected.
2. **DEBUG** Given a CORS failure in the browser console,
   identify whether the problem is a missing preflight
   handler, missing ACAO header, or CDN caching issue.
3. **DECIDE** For a credentialed API request with
   Authorization header, specify the complete set of
   response headers needed for both preflight and actual
   requests.
4. **BUILD** Implement an origin whitelist CORS handler
   that returns the exact matching origin (not `*`),
   includes `Vary: Origin`, and correctly handles OPTIONS
   preflight.
5. **EXPLAIN** Why `ACAO: *` with `ACAC: true` is blocked
   by browsers, and what the correct alternative is.

---

### 🎯 Interview Deep-Dive

**Q1: What is CORS and why does it exist?**

*Why they ask:* Tests fundamental web security understanding.
Candidate must distinguish SOP from CORS.

*Strong answer includes:*
- Same-Origin Policy: browsers block JS from reading
  cross-origin responses by default (security protection
  against malicious sites reading your bank data).
- CORS: mechanism for servers to opt into allowing
  specific cross-origin reads. Server returns
  `Access-Control-Allow-Origin`; browser checks and
  permits or blocks JS reading the response.
- CORS is browser-enforced. curl, Postman, server-to-server
  calls are completely unaffected.
- Preflight: for non-simple requests, browser sends OPTIONS
  first to check server's CORS policy before the actual
  request.

**Q2: Why can't you use `Access-Control-Allow-Origin: *`
with `Access-Control-Allow-Credentials: true`?**

*Why they ask:* Tests precise knowledge of CORS spec,
common gotcha.

*Strong answer includes:*
- Wildcard `*` means "any origin can read this response."
- Credentials (cookies, auth headers) mean the request
  is authenticated.
- Allowing any origin to read authenticated responses
  = security vulnerability (any site can read user data).
- The browser spec explicitly forbids the combination:
  `*` + `credentials: true` = browser blocks the response.
- Fix: specify exact trusted origins in an origin whitelist.
  Return the exact matching `Origin` value in ACAO header.
  Include `Vary: Origin` for CDN correctness.

**Q3: A developer reports "my API works in Postman but
gets CORS errors in the browser." What do you check?**

*Why they ask:* Tests understanding that CORS is browser-only.

*Strong answer includes:*
- CORS is browser-enforced. Postman (non-browser) ignores
  CORS completely → normal result.
- Browser has SOP. Cross-origin fetch requires correct
  CORS headers → missing or wrong headers = CORS error.
- Diagnostic steps: (1) check browser Network tab for
  failed OPTIONS preflight; (2) check response for
  `Access-Control-Allow-Origin` header; (3) verify header
  value matches the exact request `Origin`; (4) check
  for `Vary: Origin` if behind CDN.
- Common root causes: server not handling OPTIONS,
  ACAO header not set, ACAO value is `*` but request
  sends credentials, missing `Vary: Origin` causing CDN
  to serve wrong cached ACAO.
