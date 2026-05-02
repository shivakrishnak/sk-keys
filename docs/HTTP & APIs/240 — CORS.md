---
layout: default
title: "CORS"
parent: "HTTP & APIs"
nav_order: 240
permalink: /http-apis/cors/
number: "0240"
category: HTTP & APIs
difficulty: ★★☆
depends_on: HTTP, Browser Security Model, Same-Origin Policy
used_by: Web APIs, SPA (React/Vue/Angular), API Gateways
related: XSS, CSRF, HTTP Headers, API Gateway
tags:
  - api
  - cors
  - browser
  - security
  - http-headers
  - intermediate
---

# 240 — CORS (Cross-Origin Resource Sharing)

⚡ TL;DR — CORS is a browser security mechanism that controls which cross-origin HTTP requests are allowed; browsers block requests to a different origin by default (Same-Origin Policy), and CORS allows servers to explicitly opt-in by sending `Access-Control-Allow-Origin` and related HTTP response headers — a CORS error means the SERVER's response is missing the right headers, not that the request was blocked by the server.

| #240 | Category: HTTP & APIs | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | HTTP, Browser Security Model, Same-Origin Policy | |
| **Used by:** | Web APIs, SPA (React/Vue/Angular), API Gateways | |
| **Related:** | XSS, CSRF, HTTP Headers, API Gateway | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT (Same-Origin Policy only):**
Browsers implement the Same-Origin Policy (SOP): JavaScript at origin A cannot read
responses from origin B. This blocks: evil-site.com from reading your bank data via
AJAX to bank.com.

**BUT** this also blocked legitimate use cases: your React SPA at
`app.company.com` couldn't call your API at `api.company.com`. Modern web architecture
separates the frontend from the backend across different origins — SOP alone would
block this entirely.

**THE INVENTION MOMENT:**
CORS (Cross-Origin Resource Sharing, W3C spec 2009, now WHATWG Fetch spec) was defined
as a standard way for servers to opt-in to specific cross-origin access. Instead of
SOP being all-or-nothing, CORS lets servers say "I allow requests from app.company.com
specifically, but not from evil-site.com." The browser enforces this: it checks the
response headers from the target server, and only if the origin is explicitly allowed
does the browser expose the response to the JavaScript code.

---

### 📘 Textbook Definition

**CORS (Cross-Origin Resource Sharing)** is a W3C standard mechanism (RFC 6454 for
origins; Fetch specification) allowing servers to declare, via HTTP response headers,
which cross-origin requests they permit. The **Same-Origin Policy (SOP)** governs
browser default behavior: a web page at origin A (scheme + host + port) can only access
resources at origin A. CORS extends SOP to support controlled cross-origin access via
response headers: `Access-Control-Allow-Origin` (which origins are permitted),
`Access-Control-Allow-Methods` (which HTTP methods), `Access-Control-Allow-Headers`
(which request headers), and `Access-Control-Allow-Credentials` (whether cookies and
auth headers are included). For non-"simple" requests (non-GET/POST with custom headers),
the browser first sends an **OPTIONS preflight request** to confirm the server allows
the actual request before sending it.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
CORS is the browser asking the server "can I share your response with my JavaScript?"
— the server answers via response headers; a CORS error means the SERVER didn't
give permission, not that the browser is broken.

**One analogy:**

> CORS is like a doorman at an exclusive club (API server).
> Browsers (patrons) can only enter if they're on the guest list.
> The doorman (CORS headers) announces: "tonight we're accepting guests from
> app.company.com." When your JS at app.company.com tries to call the API, the
> browser checks: is this origin on the doorman's list? If yes: response is shared.
> If no: browser blocks the response (even though the server DID process the request!).

**One insight:**
The most common CORS misunderstanding: CORS errors do NOT mean the server rejected
the request. The server processes the request and returns a response. CORS is
browser enforcement: if the response lacks the correct headers, the browser hides
the response from JavaScript. The request still hit the server. This is why curl works
(no browser = no CORS enforcement) but the browser fails.

---

### 🔩 First Principles Explanation

**SAME-ORIGIN POLICY (SOP):**

```
An origin is defined as: scheme + host + port

https://app.company.com:443  ← origin
  - Different scheme: http://app.company.com = DIFFERENT origin
  - Different host: https://api.company.com = DIFFERENT origin
  - Different port: https://app.company.com:8080 = DIFFERENT origin
  - Same: https://app.company.com/other/path = SAME origin (path ignored)

SOP default: JavaScript at origin A CANNOT read responses from origin B.
CORS: server at origin B can declare "I permit origin A."
```

**TWO TYPES OF REQUESTS:**

```
SIMPLE REQUESTS (no preflight):
  Methods: GET, POST, HEAD
  Headers: only standard safe headers (Content-Type: text/plain, etc.)
  Content-Type: application/x-www-form-urlencoded, multipart/form-data, or text/plain

  Browser sends request immediately.
  CORS check: does response have Access-Control-Allow-Origin matching the requester?

NON-SIMPLE / "PREFLIGHTED" REQUESTS:
  Triggers preflight when ANY of:
  - Method: PUT, DELETE, PATCH
  - Custom header: Authorization, X-API-Key, Content-Type: application/json (!)
  - Content-Type: application/json (note: this triggers preflight!)

  Browser automatically sends OPTIONS request first:
  OPTIONS /api/users
  Origin: https://app.company.com
  Access-Control-Request-Method: DELETE
  Access-Control-Request-Headers: Authorization

  Server must respond to OPTIONS with CORS headers:
  HTTP 204
  Access-Control-Allow-Origin: https://app.company.com
  Access-Control-Allow-Methods: GET, POST, PUT, DELETE
  Access-Control-Allow-Headers: Authorization, Content-Type
  Access-Control-Max-Age: 3600  ← cache preflight for 1 hour

  After successful preflight: browser sends the actual DELETE request
```

**CORS HEADERS CHEAT SHEET:**

```
RESPONSE HEADERS (server → browser):
  Access-Control-Allow-Origin: https://app.company.com
    OR: * (allow all origins — can't be combined with credentials!)

  Access-Control-Allow-Methods: GET, POST, PUT, DELETE, PATCH, OPTIONS

  Access-Control-Allow-Headers: Authorization, Content-Type, X-API-Key

  Access-Control-Allow-Credentials: true
    (needed for cookies + auth headers; cannot combine with Allow-Origin: *)

  Access-Control-Max-Age: 3600
    (how long browser caches preflight result — reduces OPTIONS request overhead)

  Access-Control-Expose-Headers: X-Custom-Header, X-RateLimit-Remaining
    (whitelist additional response headers JavaScript can read)
```

---

### 🧪 Thought Experiment

**SCENARIO:** React SPA calls REST API — CORS configuration decision.

```
Frontend: https://app.company.com
Backend:  https://api.company.com/v1

Request: fetch('https://api.company.com/v1/users', {
           method: 'GET',
           headers: { Authorization: 'Bearer eyJ...' }  ← custom header → PREFLIGHT!
         })

STEP 1 — Browser sends OPTIONS preflight:
  OPTIONS https://api.company.com/v1/users
  Origin: https://app.company.com
  Access-Control-Request-Method: GET
  Access-Control-Request-Headers: Authorization

STEP 2 — Server must respond:
  Access-Control-Allow-Origin: https://app.company.com  ✓
  Access-Control-Allow-Methods: GET, POST, PUT, DELETE  ✓
  Access-Control-Allow-Headers: Authorization           ✓
  Access-Control-Max-Age: 3600

STEP 3 — Browser: preflight OK → sends actual GET request
  GET /v1/users
  Origin: https://app.company.com
  Authorization: Bearer eyJ...

STEP 4 — Server: 200 response with:
  Access-Control-Allow-Origin: https://app.company.com

STEP 5 — Browser: compares response origin to allowed → response exposed to JS ✓

IF MISCONFIGURED (missing headers):
  Preflight: server returns 204 WITHOUT CORS headers
  Browser: CORS policy violation → actual request blocked
  Error in console: "Access to fetch at 'https://api.company.com/v1/users'
  from origin 'https://app.company.com' has been blocked by CORS policy:
  Response to preflight request doesn't pass access control check:
  No 'Access-Control-Allow-Origin' header"

  Developer mistake: "It works with curl! Must be a browser bug."
  Reality: curl doesn't enforce CORS — it's a browser-only enforcement mechanism
```

---

### 🧠 Mental Model / Analogy

> CORS is a whitelist conversation between the browser and the API server.
>
> Browser (on behalf of JavaScript from app.company.com):
> "Hey api.company.com, I have a request from JavaScript code running at
> app.company.com. Is that OK?"
>
> Server (via Access-Control headers): "Yes, I allow app.company.com."
>
> Browser: "Great, here's the response from your API, JavaScript."
>
> Server (no CORS headers): "..."
>
> Browser: "No response for you, JavaScript. The server didn't say you could
> see this response. (The request still happened. The server processed it.
> I'm just not showing you the result.)"
>
> Key: the permission check is at RESPONSE time, by the browser, not by the server.
> This is why adding CORS headers to the response = fixing CORS errors.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
CORS is the rule that says "your JavaScript can only read responses from its own website,
unless the API explicitly says you're allowed." If your React app at one URL calls an
API at a different URL and gets a CORS error, the API server needs to add a permission
header saying your frontend's URL is allowed.

**Level 2 — How to use it (junior developer):**
In Spring Boot: `@CrossOrigin(origins = "https://app.company.com")` on controller, or
global `WebMvcConfigurer.addCorsMappings()`. For `application/json` or custom headers:
must also handle `OPTIONS` preflight. In development: never use `*` with credentials.

**Level 3 — How it works (mid-level engineer):**
Browsers send preflight (`OPTIONS`) for any request with custom headers (including
`Authorization` and `Content-Type: application/json`). The server must respond to
OPTIONS with the CORS headers — if your controller only handles GET/POST, it must
also respond to OPTIONS. `@CrossOrigin` handles this. `Access-Control-Allow-Origin: *`
cannot be combined with `Access-Control-Allow-Credentials: true` — the browser rejects
this combination (security: wildcard + credentials = any site can make credentialed
requests). Use explicit origins list for credentialed requests. Set `Access-Control-Max-Age`
to reduce preflight overhead (cache for up to 24 hours in modern browsers).

**Level 4 — Why it was designed this way (senior/staff):**
CORS is the standard mechanism for the browser to enforce the principle that the
server, not the browser vendor, decides what cross-origin access is permitted for that
server's resources. The preflight mechanism exists because some HTTP requests (DELETE,
PUT, custom headers) were never intended to be made cross-origin in the original web
model — they are "non-simple" and require explicit server opt-in via preflight.
The combination restriction (`Allow-Origin: *` + `Credentials: true`) prevents a
critical attack: if any origin could make credentialed cross-origin requests, any
malicious website could use a victim's browser (with its cookies) to make authenticated
API calls — this is essentially a CSRF attack. The CORS design forces server authors
to be explicit about which trusted origins may make credentialed requests.

---

### ⚙️ How It Works (Mechanism)

```
PREFLIGHT FLOW:

Browser (JavaScript at app.company.com calls api.company.com/data):
  ┌─────────────────────────────────────────────────────┐
  │ 1. JS code: fetch('https://api.company.com/data',   │
  │             { headers: { Authorization: '...' } })  │
  │                                                     │
  │ 2. Browser: detects cross-origin + custom header    │
  │    → sends OPTIONS preflight FIRST:                 │
  │    OPTIONS /data HTTP/1.1                          │
  │    Host: api.company.com                            │
  │    Origin: https://app.company.com                  │
  │    Access-Control-Request-Method: GET               │
  │    Access-Control-Request-Headers: authorization    │
  └─────────────────────────────────────────────────────┘
         ↓
  ┌─────────────────────────────────────────────────────┐
  │ 3. Server responds to OPTIONS:                      │
  │    HTTP/1.1 204 No Content                          │
  │    Access-Control-Allow-Origin: https://app.company.com│
  │    Access-Control-Allow-Methods: GET, POST, DELETE  │
  │    Access-Control-Allow-Headers: Authorization      │
  │    Access-Control-Max-Age: 3600                     │
  └─────────────────────────────────────────────────────┘
         ↓
  ┌─────────────────────────────────────────────────────┐
  │ 4. Browser: preflight OK                           │
  │    → sends actual GET request                      │
  │    GET /data                                       │
  │    Origin: https://app.company.com                 │
  │    Authorization: Bearer eyJ...                    │
  │                                                    │
  │ 5. Server: 200 OK (response body)                  │
  │    Access-Control-Allow-Origin: https://app.company.com│
  │                                                    │
  │ 6. Browser: Allow-Origin matches requester          │
  │    → response exposed to JavaScript ✓              │
  └─────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
React SPA (https://app.company.com) → API (https://api.company.com):

Development (localhost:3000 → localhost:8080):
  Configure CORS in Spring to allow http://localhost:3000
  OR use a dev proxy (Vite/CRA proxy config: all /api/* → port 8080)

Production (app.company.com → api.company.com):
  Spring: allow origins: ["https://app.company.com"]

API Gateway (optional): apply CORS policy at gateway,
  remove from individual services (DRY)
```

---

### 💻 Code Example

```java
// Spring Boot — Global CORS configuration
@Configuration
public class CorsConfig implements WebMvcConfigurer {

    @Value("${cors.allowed-origins}")  // externalized to config
    private List<String> allowedOrigins;

    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/api/**")
            .allowedOrigins(allowedOrigins.toArray(new String[0]))
            // NEVER use allowedOrigins("*") with allowCredentials(true)
            .allowedMethods("GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS")
            .allowedHeaders("Authorization", "Content-Type", "X-API-Key")
            .exposedHeaders("X-RateLimit-Remaining", "X-Total-Count")
            .allowCredentials(true)  // needed for cookies/Authorization header
            .maxAge(3600);           // cache preflight for 1 hour
    }
}

// application.yml:
// cors:
//   allowed-origins:
//     - https://app.company.com
//     - https://staging.company.com

// Per-controller (simpler for specific endpoints):
@CrossOrigin(origins = "https://app.company.com",
             methods = { RequestMethod.GET, RequestMethod.POST },
             allowedHeaders = { "Authorization", "Content-Type" },
             maxAge = 3600)
@RestController
@RequestMapping("/api/v1/users")
public class UserController { ... }
```

---

### ⚖️ Comparison Table

| Setting                         | Effect                         | Security                       |
| ------------------------------- | ------------------------------ | ------------------------------ |
| `Allow-Origin: *`               | Any origin can read response   | ❌ Never with credentials      |
| `Allow-Origin: specific-origin` | Only listed origins            | ✅ Recommended                 |
| `Allow-Credentials: true`       | Cookies/auth headers sent      | Requires specific Allow-Origin |
| `Max-Age: 3600`                 | Cache preflight 1 hour         | Performance                    |
| No CORS headers                 | Browser blocks JS from reading | N/A (default behavior)         |

---

### ⚠️ Common Misconceptions

| Misconception                                         | Reality                                                                                                                                                                                   |
| ----------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| CORS error = server rejected the request              | The server processed the request. CORS is browser enforcement AFTER receiving the response — the server just didn't include permission headers                                            |
| `curl` works but browser fails = CORS issue           | Exactly. curl has no browser enforcement. Fix: add CORS headers to server response                                                                                                        |
| `Access-Control-Allow-Origin: *` always works         | Not with credentialed requests (cookies/Authorization header). Use specific origins                                                                                                       |
| CORS is a security mechanism that protects the server | CORS protects browsers from malicious JavaScript reading cross-origin responses. It doesn't prevent non-browser clients (curl, Postman) from calling your API — still need authentication |

---

### 🚨 Failure Modes & Diagnosis

**Preflight Cached with Wrong Headers**

**Symptom:**
Added `X-Custom-Header` to API requests. Works sometimes, fails others. Works after
hard-reload. Same code in different browsers behaves differently.

**Root Cause:**
Browser cached the previous preflight response (via `Access-Control-Max-Age`).
Old preflight didn't list `X-Custom-Header` in `Access-Control-Allow-Headers`.
Browser uses cached result → blocks actual request.

**Diagnostic:**

```
# Open browser DevTools → Network tab
# Check for OPTIONS preflight request
# Inspect response headers: Access-Control-Allow-Headers
# If header missing: server config issue
# If header present but cached old value: force expire cache

# Chrome: DevTools → Network → "Disable cache" checkbox
# Firefox: Shift+Reload (bypasses cache)
# More permanent: set shorter Access-Control-Max-Age during development

# Verify server returns correct headers:
curl -I -X OPTIONS https://api.company.com/v1/users \
  -H "Origin: https://app.company.com" \
  -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: Authorization, X-Custom-Header"
# Should see: Access-Control-Allow-Headers includes X-Custom-Header
```

---

### 🔗 Related Keywords

- `XSS` — CORS does not protect against XSS; if JS is injected, it can make requests from the same origin
- `CSRF` — CORS is sometimes confused with CSRF protection; they address different threats
- `Same-Origin Policy` — the browser security model that CORS extends
- `API Gateway` — often the right place to centralize CORS configuration

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Server opt-in for cross-origin browser    │
│              │ requests via response headers             │
├──────────────┼───────────────────────────────────────────┤
│ CORS ERROR   │ Server response missing CORS headers —    │
│ MEANS        │ NOT that the server blocked the request   │
├──────────────┼───────────────────────────────────────────┤
│ PREFLIGHT    │ OPTIONS request for: PUT/DELETE, custom   │
│ TRIGGERS     │ headers (incl. Authorization, JSON CT)    │
├──────────────┼───────────────────────────────────────────┤
│ CREDENTIALS  │ allowedOrigins must be explicit (not *)  │
│ + COOKIES    │ allowCredentials: true                   │
├──────────────┼───────────────────────────────────────────┤
│ CURL WORKS?  │ Yes — curl doesn't enforce CORS          │
│              │ Browser fails = CORS headers problem     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Server tells browser: 'I allow you'"   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ XSS → CSRF → Same-Origin Policy          │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q.** Your public API is consumed by: (1) your own SPA at app.company.com using Bearer tokens, (2) third-party developers building their own web apps (multiple unknown origins), (3) mobile apps (no browser, no CORS). Design the CORS policy that satisfies all three with minimal security risk, and explain why using `Access-Control-Allow-Origin: *` for the third-party developer scenario is or isn't acceptable in this specific context.
