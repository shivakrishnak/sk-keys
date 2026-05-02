---
layout: default
title: "HTTP Headers"
parent: "HTTP & APIs"
nav_order: 211
permalink: /http-apis/http-headers/
number: "211"
category: HTTP & APIs
difficulty: ★★☆
depends_on: HTTP/1.1, HTTP Status Codes, TLS/SSL
used_by: Keep-Alive / Connection Pooling, API Authentication, CORS, Content Negotiation, ETag / Cache-Control
tags:
  - networking
  - protocol
  - http
  - intermediate
---

# 211 — HTTP Headers

`#networking` `#protocol` `#http` `#intermediate`

⚡ TL;DR — Key-value metadata fields in HTTP requests and responses controlling caching, content negotiation, authentication, encoding, and connection behaviour.

| #211 | Category: HTTP & APIs | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | HTTP/1.1, HTTP Status Codes, TLS/SSL | |
| **Used by:** | Keep-Alive / Connection Pooling, API Authentication, CORS, Content Negotiation, ETag / Cache-Control | |

---

### 📘 Textbook Definition

**HTTP Headers** are name-value pairs transmitted in both HTTP requests and responses, providing metadata about the message, the sender, or the resource being transferred. Headers are case-insensitive, separated from the message body by a blank line, and follow the format `Header-Name: value CRLF`. Headers are categorised as: General (applicable to both requests and responses), Request (client-to-server metadata), Response (server-to-client metadata), and Entity (body-related metadata). HTTP/2 uses HPACK binary compression for headers. Custom headers use the `X-` prefix convention (now deprecated for new headers per RFC 6648).

### 🟢 Simple Definition (Easy)

HTTP headers are like the sticky notes attached to a package: they tell the delivery system and recipient how to handle the contents, what it is, who sent it, and how long to keep it.

### 🔵 Simple Definition (Elaborated)

When a browser or API client sends a request, it includes headers that tell the server many things beyond the URL: what content formats it accepts (Accept), how to authenticate (Authorization), whether to reuse the connection (Connection), what language to respond in (Accept-Language), and whether it already has a cached copy (If-None-Match). The server's response includes headers telling the client: what type the response content is (Content-Type), how long to cache it (Cache-Control), where a new resource was created (Location), and which cross-origin requests to allow (Access-Control-Allow-Origin). Headers are how HTTP protocols layer security, performance, and content negotiation on top of a simple request-response.

### 🔩 First Principles Explanation

**Why headers exist as a separate concern from the body:**

Headers serve as the "envelope" of an HTTP message. Separating them from the body allows:
1. Processing decisions before reading the (potentially large) body.
2. Proxy/CDN/load-balancer decisions based on headers without touching body.
3. Uniform handling of cross-cutting concerns (auth, caching, encoding) independent of body format.

**Key headers and their purposes:**

**Request headers — client instructs server:**

```
Host: api.example.com          → required; virtual hosting
Authorization: Bearer eyJ...   → authentication token
Content-Type: application/json → body format (for POST/PUT)
Accept: application/json       → acceptable response format
Accept-Encoding: gzip, br      → accepted compression algorithms
Accept-Language: en-US, en;q=0.9 → language preference
Cache-Control: no-cache        → don't use cached response
If-None-Match: "etag-value"    → conditional GET
If-Modified-Since: date        → conditional GET by date
Connection: keep-alive         → connection persistence
User-Agent: Mozilla/5.0...     → client identification
```

**Response headers — server instructs client:**

```
Content-Type: application/json;charset=UTF-8
Content-Length: 1234           → body size in bytes
Content-Encoding: gzip         → body compression used
Cache-Control: max-age=3600    → cache this for 1 hour
ETag: "33a64df551425fcc55e4"   → entity tag for caching
Last-Modified: Mon, 01 May 2026 → modification date
Location: /users/42             → created resource URL
Set-Cookie: sessionid=abc; Secure; HttpOnly; SameSite=Strict
Access-Control-Allow-Origin: * → CORS permission
Retry-After: 60                → rate limit retry wait
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

**Hop-by-hop vs. end-to-end headers:**

- **End-to-end:** Forwarded through all proxies to the final destination (Authorization, Content-Type).
- **Hop-by-hop:** For a single connection segment only; NOT forwarded (Connection, Transfer-Encoding, Keep-Alive).

### ❓ Why Does This Exist (Why Before What)

WITHOUT HTTP Headers:

- No way to specify body content type — receiver must guess (XML? JSON? HTML?).
- No caching mechanism — every request fetches fresh data.
- No authentication mechanism — no standard way to send credentials.
- No content negotiation — server can't know client's capabilities.

What breaks without it:
1. Cross-cutting concerns (auth, caching) embedded in every body format.
2. Proxies and CDNs can't make caching/routing decisions without metadata.

WITH HTTP Headers:
→ Content negotiation enables one endpoint to serve different formats.
→ Cache-Control/ETag enable efficient caching at browser, CDN, and proxy levels.
→ CORS headers enable secure cross-origin resource sharing.

### 🧠 Mental Model / Analogy

> HTTP headers are like the information form attached to an international package shipment. The form includes: what's inside (Content-Type), how to handle it (Cache-Control = "keep refrigerated"), who sent it (Authorization), what languages to use in documentation (Accept-Language), when it expires (Cache-Control max-age), and any customs declarations (CORS). The form is read before opening the package — and by every middleman (proxy, CDN) along the way.

"Package" = HTTP body, "form/label" = HTTP headers, "middlemen" = proxies and CDNs, "customs" = CORS and security headers.

### ⚙️ How It Works (Mechanism)

**Security headers reference:**

```
# HTTPS enforcement
Strict-Transport-Security: max-age=31536000; includeSubDomains

# XSS prevention
Content-Security-Policy: default-src 'self'; script-src 'self'

# Prevent MIME sniffing
X-Content-Type-Options: nosniff

# Clickjacking prevention
X-Frame-Options: DENY

# All modern equivalents in Permissions-Policy header
Permissions-Policy: camera=(), microphone=(), geolocation=()
```

**Custom headers (application-specific):**

```
X-Request-ID: 550e8400-e29b-41d4-a716-446655440000  # tracing
X-Correlation-ID: req-abc123                         # correlation
X-Rate-Limit-Remaining: 95                           # rate limit info
X-Rate-Limit-Reset: 1714600000                       # reset timestamp
```

### 🔄 How It Connects (Mini-Map)

```
HTTP Request/Response
        ↓ contains
HTTP Headers ← you are here
    ↓ type-specific headers enable:
Cache-Control + ETag  → HTTP Caching
Authorization         → API Authentication
CORS headers          → Cross-Origin management
Content-Negotiation   → Accept / Content-Type
Connection headers    → Keep-Alive / Pooling
```

### 💻 Code Example

Example 1 — Reading and setting headers in Spring Boot:

```java
@GetMapping("/secure-resource")
public ResponseEntity<Resource> getResource(
        @RequestHeader("Authorization") String token,
        @RequestHeader(value = "Accept-Language",
                       defaultValue = "en") String lang,
        @RequestHeader(value = "If-None-Match",
                       required = false) String etag) {

    if (!authService.validate(token)) {
        return ResponseEntity.status(401)
            .header("WWW-Authenticate", "Bearer")
            .build();
    }

    String currentEtag = resourceService.getEtag();
    if (currentEtag.equals(etag)) {
        return ResponseEntity.status(304).build(); // Not Modified
    }

    Resource resource = resourceService.get(lang);
    return ResponseEntity.ok()
        .header("ETag", currentEtag)
        .header("Cache-Control", "max-age=3600")
        .header("Content-Language", lang)
        .body(resource);
}
```

Example 2 — Security headers in Spring Security:

```java
@Bean
public SecurityFilterChain filterChain(HttpSecurity http) {
    http.headers(headers -> headers
        .contentSecurityPolicy(csp ->
            csp.policyDirectives(
                "default-src 'self';" +
                "script-src 'self'"))
        .frameOptions(HeadersConfigurer.FrameOptionsConfig::deny)
        .xssProtection(xss ->
            xss.headerValue(
                XXssProtectionHeaderWriter.HeaderValue.ENABLED_MODE_BLOCK))
        .httpStrictTransportSecurity(hsts ->
            hsts.maxAgeInSeconds(31536000)
                .includeSubDomains(true))
    );
    return http.build();
}
```

Example 3 — Inspecting headers with curl:

```bash
# Show only response headers
curl -sI https://api.example.com/

# Show both request and response headers
curl -v https://api.example.com/ 2>&1 | grep -E "^[<>]"
# > GET / HTTP/2         → request headers
# < HTTP/2 200           → response headers
# < content-type: application/json

# Include custom headers in request
curl -H "Authorization: Bearer my-token" \
     -H "Accept: application/json" \
     -H "X-Request-ID: $(uuidgen)" \
     https://api.example.com/users
```

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| HTTP headers are case-sensitive | Header names are case-insensitive per HTTP spec. `content-type` and `Content-Type` are the same. HTTP/2 uses lowercase canonically. |
| X- prefix means a header is private/safe | The X- prefix convention is deprecated (RFC 6648). Formerly meant "experimental"; now just a historical naming habit. |
| Setting Authorization header is always sufficient for auth | Some auth mechanisms require additional steps (PKCE flow, refresh tokens, signature verification). A single Authorization header is not always the full auth picture. |
| Content-Type is only needed for POST/PUT | Content-Type should be set on any response with a body. Omitting it causes browsers to MIME-sniff, which is a security vulnerability. |
| Headers are not visible to JavaScript | Request headers set via JavaScript (except Cookie and some forbidden headers) are visible to server-side code. Response headers marked without CORS `Access-Control-Expose-Headers` are NOT accessible to cross-origin JavaScript. |

### 🔥 Pitfalls in Production

**1. Missing Content-Type in API Response**

```java
// BAD: Response without Content-Type → MIME sniffing vulnerability
return new ResponseEntity<>(body, HttpStatus.OK);
// Browser may treat JSON as HTML → XSS risk

// GOOD: Always set Content-Type explicitly
return ResponseEntity.ok()
    .contentType(MediaType.APPLICATION_JSON)
    .body(body);
```

**2. Logging Authorization Headers in Access Logs**

```bash
# BAD: Nginx logging all headers including Authorization tokens
log_format detailed '$remote_addr - $request - $http_authorization';
# → Authorization: Bearer eyJhbGc... in log files → credential leak

# GOOD: Never log sensitive headers
log_format safe '$remote_addr - $request - $status';
# Or mask in log filter: replace Bearer token with [REDACTED]
```

**3. Missing HSTS Header — Downgrade Attack Risk**

```bash
# BAD: HTTPS service without HSTS allows downgrade attack
# → attacker can intercept initial HTTP request

# GOOD: Enable HSTS
response.addHeader("Strict-Transport-Security",
    "max-age=31536000; includeSubDomains; preload");
# After adding to HSTS preload list:
# browsers connect HTTPS-only for your domain, always
```

### 🔗 Related Keywords

- `Keep-Alive / Connection Pooling` — controlled by `Connection` and `Keep-Alive` headers.
- `ETag / Cache-Control` — the primary headers controlling HTTP caching behaviour.
- `API Authentication` — `Authorization` header carries credentials (Bearer tokens, API keys).
- `CORS` — `Access-Control-*` headers enable/restrict cross-origin requests.
- `Content Negotiation` — `Accept` / `Content-Type` headers negotiate response format.

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Name-value metadata controlling caching, │
│              │ auth, encoding, CORS, and connection.     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always — every HTTP request/response has  │
│              │ critical headers for correct behaviour.   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Never skip security headers (HSTS, CSP,   │
│              │ X-Content-Type-Options) on public APIs.   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Headers: the envelope that tells every   │
│              │ middleman how to handle the package."     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Keep-Alive → CORS → ETag → Cache-Control  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A mobile API server responds with `Cache-Control: no-store` on all API responses. A performance review shows this causes 40% more backend requests and 60ms higher average API latency compared to a competitor using `Cache-Control: max-age=5, stale-while-revalidate=10`. Explain the exact semantic difference between these two strategies, identify which response content types should NEVER use the second strategy, and describe one security scenario where `no-store` is the only correct choice.

**Q2.** HTTP/2 uses HPACK header compression with a shared dynamic table between client and server. An attacker can perform a CRIME attack — repeating small variations of a secret (like a CSRF token) in a request alongside attacker-controlled data, then measuring compressed response sizes to infer the secret. Explain step by step how compression ratio leaks secret information, and why this attack is partially mitigated by TLS but not fully prevented by it.

