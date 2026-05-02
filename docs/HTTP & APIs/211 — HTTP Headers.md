---
layout: default
title: "HTTP Headers"
parent: "HTTP & APIs"
nav_order: 211
permalink: /http-apis/http-headers/
number: "0211"
category: HTTP & APIs
difficulty: ★★☆
depends_on: HTTP/1.1, HTTP Status Codes, HTTP Methods
used_by: CORS, Content Negotiation, API Authentication, ETag, Keep-Alive
related: HTTP Status Codes, CORS, Content Negotiation, ETag, API Authentication
tags:
  - http
  - api
  - networking
  - protocol
  - intermediate
---

# 211 — HTTP Headers

⚡ TL;DR — HTTP headers are key-value metadata fields sent in every request and response that control caching, authentication, content format, connection behaviour, and security policies — entirely separate from the URL, method, and body.

| #211 | Category: HTTP & APIs | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | HTTP/1.1, HTTP Status Codes, HTTP Methods | |
| **Used by:** | CORS, Content Negotiation, API Authentication, ETag, Keep-Alive | |
| **Related:** | HTTP Status Codes, CORS, Content Negotiation, ETag, API Authentication | |

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Imagine if every piece of metadata about an HTTP request — "what format is this
data?", "how long should this response be cached?", "who is making this request?",
"what type of content will I accept back?" — had to be encoded in the URL or the
body. URLs would become unreadably long parameter strings. Request bodies would
need a fixed wrapper format mixing application data with transport metadata.
Caches, proxies, and auth systems would need to understand every application's
body format to extract the metadata they need.

**THE BREAKING POINT:**
Without a standardised metadata channel, every intermediary (proxy, cache, CDN,
load balancer) is blind to the context of a request. It cannot decide whether to
cache, authenticate, compress, or route without parsing the application payload.
The protocol and the application would be tightly coupled.

**THE INVENTION MOMENT:**
This is exactly why HTTP headers were designed. They provide a standardised,
extensible metadata channel that lets the protocol layer carry context that is
completely orthogonal to the request body and URL. Any intermediary can read and
act on headers without understanding the application domain.

---

### 📘 Textbook Definition

**HTTP headers** are case-insensitive key-value pairs (separated by `: `) that
appear in HTTP request and response messages after the start-line, terminated
by a blank line before the optional body. Headers are grouped into: **request
headers** (sent by client: `Host`, `Accept`, `Authorization`, `User-Agent`),
**response headers** (sent by server: `Content-Type`, `Set-Cookie`, `Location`,
`WWW-Authenticate`), **representation headers** (describe body: `Content-Length`,
`Content-Encoding`, `Transfer-Encoding`), and **general headers** (apply to both:
`Connection`, `Cache-Control`, `Date`). RFC 7230 and 7231 define standard headers;
custom headers use the `X-` prefix convention (deprecated in RFC 6648, but still
widely used). HPACK (HTTP/2) and QPACK (HTTP/3) compress headers on the wire.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
HTTP headers are the envelope metadata of an HTTP message — information about
the message itself, separate from its content.

**One analogy:**
> HTTP headers are like the outside of a postal package: the "To" address
> (Host), "Return address" (Origin), "Contents: fragile glassware"
> (Content-Type: application/json), "Store until" date (Cache-Control),
> "Sender's ID" (Authorization), and "Accept only if signed for"
> (Content-Length). The postal system (proxies, caches, CDN) reads the
> envelope without opening the package.

**One insight:**
Headers are the extensibility mechanism of HTTP. Every major HTTP feature —
authentication, caching, compression, CORS, content negotiation, cookies,
security policies, connection management — is implemented via headers, not via
changes to the protocol itself. Understanding headers is understanding HTTP.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Headers appear after the start-line, before the body, separated by CRLF.
   A blank line separates headers from body.
2. Header names are case-insensitive; values are case-sensitive for most
   headers (file paths, base64, tokens) but not all (`Accept: text/HTML` equals
   `Accept: text/html`).
3. Headers are extensible — you can add custom headers without breaking
   existing infrastructure. Unknown headers are forwarded by proxies
   (unless listed in `Connection: header-name` to suppress hop-by-hop removal).

**THE CRITICAL HEADER GROUPS:**

**Authentication:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.eyJ...
WWW-Authenticate: Bearer realm="api.example.com"
```
Request carries credentials; response prompts authentication.

**Content Description:**
```
Content-Type: application/json; charset=UTF-8
Content-Length: 1024
Content-Encoding: gzip
Transfer-Encoding: chunked
Accept: application/json, text/xml;q=0.9
```

**Caching:**
```
Cache-Control: max-age=3600, public
ETag: "abc123def"
If-None-Match: "abc123def"
Last-Modified: Mon, 01 May 2024 12:00:00 GMT
Vary: Accept-Encoding, Accept-Language
```

**Security:**
```
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
Content-Security-Policy: default-src 'self'
X-Frame-Options: DENY
```

**Connection Management:**
```
Connection: keep-alive
Keep-Alive: timeout=60, max=1000
Upgrade: websocket
```

**DERIVED DESIGN — Hop-by-Hop vs End-to-End:**
HTTP distinguishes two classes of headers:
- **End-to-end** headers: forwarded by all proxies to the final destination
  (e.g., `Authorization`, `Content-Type`)
- **Hop-by-hop** headers: consumed by the next intermediary and NOT forwarded
  (e.g., `Connection`, `Transfer-Encoding`, `Keep-Alive`, `Upgrade`). When a
  proxy receives a request with `Connection: X-Custom`, it must remove `X-Custom`
  before forwarding.

**THE TRADE-OFFS:**
- Gain: universal extensibility, protocol/application decoupling,
  infrastructure-readable metadata
- Cost: header bloat (HTTP/1.1 sends headers verbatim on every request;
  HPACK in HTTP/2 compresses repetition); security risks if headers are
  logged verbatim (Authorization tokens in logs); injection vulnerabilities
  from unvalidated header values

---

### 🧪 Thought Experiment

**SETUP:**
A REST API serves JSON to web apps and CSV to reporting tools. Both consumers
call `GET /reports/sales`. Without headers, how would the server know which format
to return?

**WHAT HAPPENS WITHOUT ACCEPT HEADERS:**
1. Server must use a different URL per format: `/reports/sales.json`, `/reports/sales.csv`
2. Or use a query param: `/reports/sales?format=csv`
3. CDN now caches two different URLs for the same logical resource
4. URL bookmarks are format-coupled — a bookmark to `.json` cannot be changed
   to `.csv` without the URL breaking
5. The server cannot transparently add new formats without changing URLs

**WHAT HAPPENS WITH ACCEPT HEADERS:**
1. Web app sends: `Accept: application/json`
2. Reporting tool sends: `Accept: text/csv`
3. Both use the same URL: `GET /reports/sales`
4. Server reads `Accept`, returns appropriate format with matching `Content-Type`
5. CDN uses the `Vary: Accept` response header to cache both formats
   independently under the same URL
6. Server can add `Accept: application/parquet` support without changing any URL

**THE INSIGHT:**
Headers let the same URL serve multiple representations of the same resource.
This is content negotiation in action — a single canonical URL, many possible
forms, all driven purely by headers. No URL pollution, no client-server coupling
on URL structure.

---

### 🧠 Mental Model / Analogy

> HTTP headers are the metadata layer that HTTP uses to talk about itself.
> If the body is the letter you're sending, headers are the instructions you
> give the postal carrier: "deliver express" (Connection: upgrade), "check ID"
> (WWW-Authenticate), "keep refrigerated" (Cache-Control: no-store), "this is
> a manuscript" (Content-Type: text/plain). The carrier acts on these
> instructions without needing to read the letter.

**Mapping:**
- "postal carrier" → HTTP proxy / CDN / gateway
- "check ID" → `WWW-Authenticate` / `Authorization`
- "keep refrigerated" → `Cache-Control: no-store`
- "this is a manuscript" → `Content-Type: text/plain`
- "deliver express" → `Connection: upgrade`
- "return receipt requested" → `ETag` / `If-None-Match`

**Where this analogy breaks down:**
Unlike postal metadata, HTTP headers can be read by every hop in the chain —
including eavesdroppers on HTTP (non-TLS). Sensitive headers (`Authorization`,
`Cookie`) must be transmitted over HTTPS to prevent interception.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
When your browser sends a request to a website and the website sends a response,
both include a set of labels that describe the message: "I understand JSON"
(Accept), "here's my login token" (Authorization), "this response expires in
an hour" (Cache-Control). These labels are HTTP headers — they're how the
browser and server coordinate without hard-coding every possible scenario into
the URLs.

**Level 2 — How to use it (junior developer):**
Always set `Content-Type` when sending a request body (`application/json`,
`multipart/form-data`). Read `Content-Type` from responses before parsing.
Use `Authorization: Bearer <token>` for API authentication. Set `Accept:
application/json` to tell the server what you can handle. Never log
`Authorization` or `Cookie` headers — they are credentials. Understand that
`Cache-Control: no-cache` does NOT mean "don't cache" — it means "revalidate
before using the cache." Use `Cache-Control: no-store` to truly prevent caching.

**Level 3 — How it works (mid-level engineer):**
The `Vary` response header is critical for caching correctness: `Vary: Accept-Encoding`
tells the CDN to store separate cached versions for `gzip` and `br` (Brotli)
encodings. Without `Vary`, a CDN might serve a gzip-compressed response to a
client that only supports identity encoding and can't decompress it. The `ETag`
header enables conditional requests: client sends `If-None-Match: "etag-value"`,
server returns 304 Not Modified (no body, just header) if the ETag matches —
saving full response transfer. Understanding `Transfer-Encoding` vs `Content-Encoding`
distinction is essential: `Transfer-Encoding` is hop-by-hop (each proxy handles
it) while `Content-Encoding` is end-to-end (the origin applied it, the client
must undo it).

**Level 4 — Why it was designed this way (senior/staff):**
The case-insensitivity of header names was a pragmatic choice for maximum
interoperability across systems with different case conventions (Windows =
case-insensitive, Unix = case-sensitive). The `X-` prefix convention for custom
headers was deprecated in RFC 6648 (2012) because it caused "custom" headers
to de-facto standardise (X-Forwarded-For, X-Request-ID) and then become
awkward to formally adopt. The fundamental tension in header design is between
richness (more headers = more expressiveness) and overhead (every header adds
bytes to every request). HPACK's dynamic table compression in HTTP/2 was the
engineering answer: compress repeated headers to near zero overhead while
allowing arbitrary extensibility.

---

### ⚙️ How It Works (Mechanism)

**Wire Format:**
```
┌──────────────────────────────────────────────────────┐
│              HTTP/1.1 Request Headers                │
├──────────────────────────────────────────────────────┤
│ Host: api.example.com\r\n                            │
│ Authorization: Bearer eyJhbGc...\r\n                 │
│ Content-Type: application/json\r\n                   │
│ Content-Length: 47\r\n                               │
│ Accept-Encoding: gzip, br\r\n                        │
│ Connection: keep-alive\r\n                           │
│ \r\n                          ← blank line           │
│ [body follows]                                       │
└──────────────────────────────────────────────────────┘
```

**Cache-Control directives:**
```
┌──────────────────────────────────────────────────────┐
│       Cache-Control Directives Quick Reference       │
├────────────────────┬─────────────────────────────────┤
│ no-store           │ Never cache (sensitive data)    │
│ no-cache           │ Cache but always revalidate     │
│ max-age=3600       │ Cache valid for 3600 seconds    │
│ public             │ CDN + browser can cache         │
│ private            │ Browser only, not CDN           │
│ must-revalidate    │ Revalidate after max-age        │
│ s-maxage=60        │ CDN max-age (overrides max-age) │
└────────────────────┴─────────────────────────────────┘
```

**Security headers every API should set:**
```
Strict-Transport-Security: max-age=63072000; includeSubDomains; preload
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Content-Security-Policy: default-src 'self'
Referrer-Policy: strict-origin-when-cross-origin
```

**Forwarding headers (proxy chain):**
```
┌──────────────────────────────────────────────────────┐
│         Request Header Propagation through Proxy     │
├──────────────────────────────────────────────────────┤
│ Client → Proxy → Origin                              │
│                                                      │
│ Client adds:                                         │
│   X-Forwarded-For: 192.168.1.1 (client's IP)        │
│   X-Forwarded-Proto: https                           │
│                                                      │
│ Proxy adds/appends:                                  │
│   X-Forwarded-For: 192.168.1.1, 10.0.0.5           │
│   Via: 1.1 proxy.example.com                        │
│                                                      │
│ Origin reads X-Forwarded-For to get real client IP  │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
┌──────────────────────────────────────────────────────┐
│       HTTP Headers in the Request/Response Cycle     │
├──────────────────────────────────────────────────────┤
│ Browser prepares request headers:                    │
│   Host, Accept, Accept-Encoding, Authorization...   │
│               ↓                                      │
│ TLS negotiation (ALPN adds HTTP version)             │
│               ↓                                      │
│ [HTTP HEADERS ← YOU ARE HERE]                        │
│ CDN reads Cache-Control, ETag, If-None-Match:        │
│   Hit? Return 304, no body                          │
│   Miss? Forward to origin                           │
│               ↓                                      │
│ Load balancer reads X-Forwarded-For, Host           │
│               ↓                                      │
│ App server: reads Authorization, Content-Type       │
│   → auth filter → content parser → handler         │
│               ↓                                      │
│ Response headers: Content-Type, Cache-Control,      │
│   ETag, Security headers, CORS headers              │
│               ↓                                      │
│ CDN stores response keyed on URL + Vary values      │
└──────────────────────────────────────────────────────┘
```

**FAILURE PATH:**
Missing `Content-Type` header → server uses default or sniffs MIME type →
may misparse body → `400 Bad Request` or silent data corruption in parser.

**WHAT CHANGES AT SCALE:**
At scale, header overhead in HTTP/1.1 becomes significant: a 800-byte set of
headers on 10,000 requests/second = 8 MB/s of pure header overhead, often 5× the
actual response payload for small API calls. HTTP/2 HPACK reduces this to ~50 bytes
for repeated headers. At 1M req/s, this is the difference between 800 MB/s and
50 MB/s of header bandwidth — a real infrastructure cost.

---

### 💻 Code Example

**Example 1 — Setting response headers in Spring Boot:**
```java
@GetMapping("/reports/sales")
public ResponseEntity<byte[]> getSalesReport(
        @RequestHeader(value = "Accept",
                       defaultValue = "application/json") String accept) {

    byte[] data;
    String contentType;

    if (accept.contains("text/csv")) {
        data = reportService.exportCsv();
        contentType = "text/csv; charset=UTF-8";
    } else {
        data = reportService.exportJson();
        contentType = "application/json";
    }

    return ResponseEntity.ok()
        .header("Content-Type", contentType)
        .header("Cache-Control", "private, max-age=300")
        .header("Vary", "Accept")  // CRITICAL: CDN must cache per-format
        .header("ETag", '"' + reportService.getEtag() + '"')
        .body(data);
}
```

**Example 2 — Reading and validating incoming headers:**
```java
@PostMapping("/webhooks/payment")
public ResponseEntity<Void> receiveWebhook(
        @RequestBody String body,
        @RequestHeader("X-Stripe-Signature") String signature,
        @RequestHeader(
            value = "Content-Type",
            required = true) String contentType) {

    // Validate Content-Type before parsing:
    if (!contentType.contains("application/json")) {
        return ResponseEntity.unsupportedMediaType().build(); // 415
    }

    // Validate signature header (HMAC verification):
    if (!stripeValidator.verify(body, signature)) {
        return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
    }

    webhookService.process(body);
    return ResponseEntity.ok().build();
}
```

**Example 3 — Security headers via Spring Security:**
```java
@Bean
public SecurityFilterChain securityFilterChain(HttpSecurity http)
        throws Exception {
    http.headers(headers -> headers
        .strictTransportSecurity(hsts -> hsts
            .includeSubDomains(true)
            .maxAge(Duration.ofDays(365)))
        .frameOptions(frame -> frame.deny())
        .contentTypeOptions(Customizer.withDefaults())
        .xssProtection(Customizer.withDefaults())
    );
    return http.build();
}
```

---

### ⚖️ Comparison Table

| Header Category | Key Headers | Controlled By | Impact |
|---|---|---|---|
| **Authentication** | Authorization, WWW-Authenticate | Server/Client | API access control |
| **Caching** | Cache-Control, ETag, Vary | Server | CDN/browser cache efficiency |
| **Content** | Content-Type, Accept, Encoding | Both | Parsing correctness |
| **Security** | HSTS, CSP, X-Frame-Options | Server | Browser protection |
| **Connection** | Connection, Keep-Alive, Upgrade | Both | TCP reuse, ws upgrade |
| **Forwarding** | X-Forwarded-For, Via, Host | Proxy | Request routing, rate limiting |

**How to choose:** Always set security headers on all responses (they're free).
Always set `Content-Type` and `Cache-Control` explicitly — never rely on defaults,
which vary by framework and may be incorrect.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Cache-Control: no-cache means "don't cache" | no-cache means "cache but always revalidate before serving." Use no-store to truly prevent caching |
| X-Forwarded-For is always the client's real IP | X-Forwarded-For can be spoofed by the client. Only trust it if set by your own trusted proxy, not the value the client provided |
| Content-Type and Content-Encoding are the same thing | Content-Type is the media type of the data; Content-Encoding is a transformation applied (gzip). A gzipped JSON response is Content-Type: application/json + Content-Encoding: gzip |
| Custom headers should start with X- | RFC 6648 deprecated the X- prefix convention. New custom headers should use descriptive names without prefix |
| Headers are private because HTTPS encrypts them | TLS encrypts headers from observation, but the server, any intermediary handling TLS termination, and logging systems can see them. Never log Authorization or Cookie headers |

---

### 🚨 Failure Modes & Diagnosis

**Missing Content-Type Header (Body Misparse)**

Symptom: `400 Bad Request` with "incorrect content type" or body parsed as
empty; server logs show "Content type 'application/octet-stream' not supported."

Root Cause: Client sends POST/PUT without `Content-Type` header. Framework
defaults to `application/octet-stream` and refuses to parse as JSON.

Diagnostic Command / Tool:
```bash
# Test with explicit Content-Type:
curl -X POST https://api.example.com/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice"}'

# Without Content-Type (reproduces the bug):
curl -X POST https://api.example.com/users \
  -d '{"name": "Alice"}'
```

Fix: Always include `Content-Type: application/json` on all POST/PUT requests
that send JSON bodies.

Prevention: Add server-side validation that rejects missing Content-Type
with `415 Unsupported Media Type`. Document required headers in OpenAPI spec.

---

**Broken CORS — Missing Vary:Origin Header**

Symptom: CDN serves a cached response without `Access-Control-Allow-Origin`
header to cross-origin clients; browser blocks request with CORS error even
though the server is correctly configured.

Root Cause: The API's CORS handler adds `Access-Control-Allow-Origin: https://app.example.com`
for cross-origin requests but `Vary: Origin` is not set. The CDN caches the
first response (which might have been from a same-origin request, with no
CORS headers) and serves it to cross-origin clients.

Diagnostic Command / Tool:
```bash
# Check if Vary: Origin is present:
curl -s -I -H "Origin: https://app.example.com" \
  https://api.example.com/users | grep -i "vary\|access-control"
# Should see both Vary: Origin AND Access-Control-Allow-Origin
```

Fix: Always include `Vary: Origin` when conditionally setting CORS headers.
In Spring, `CorsConfiguration` sets this automatically when CORS is properly configured.

Prevention: Test CORS behaviour through the CDN, not just directly to origin.
Verify `Vary` headers are preserved by CDN configuration.

---

**Large Headers — Request Entity Too Large**

Symptom: Requests with large JWT tokens or many cookies fail with `431 Request
Header Fields Too Large`; Nginx logs show "large_client_header_buffers overflow."

Root Cause: HTTP servers have configurable limits on header size. Nginx defaults
to 8 KB for request headers. JWT tokens containing many claims, multiple large
cookies, or verbose `Authorization` headers can exceed this.

Diagnostic Command / Tool:
```bash
# Measure total header size of a request:
curl -v -H "Authorization: Bearer $(cat large-jwt.txt)" \
  https://api.example.com/test 2>&1 | grep -c "^>"
# Count header bytes:
echo "Authorization: Bearer $(cat large-jwt.txt)" | wc -c
```

Fix: Increase buffer sizes for APIs that use large tokens:
```nginx
large_client_header_buffers 4 32k;
client_header_buffer_size 4k;
```

Prevention: Minimise JWT claims — don't store large payloads in tokens.
Use access tokens (small) + separate user info endpoint rather than embedding
all user data in the token.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `HTTP/1.1` — headers are defined as core HTTP message components; understanding
  the request/response format is required before working with headers
- `HTTP Status Codes` — response headers accompany status codes; understanding
  what headers are valid for which codes is essential

**Builds On This (learn these next):**
- `Content Negotiation` — the `Accept`, `Content-Type`, and `Vary` headers
  enable content negotiation; headers are the mechanism
- `CORS` — cross-origin resource sharing is entirely implemented via headers
  (`Origin`, `Access-Control-Allow-Origin`, etc.)
- `ETag / Cache-Control` — the caching subsystem is entirely header-driven

**Alternatives / Comparisons:**
- `gRPC Metadata` — gRPC's equivalent of HTTP headers: key-value pairs sent
  with each RPC call, but binary-encoded in Protobuf frames
- `HTTP Trailers` — like headers but sent at the end of a chunked response body;
  used for checksums and final metadata computed after streaming

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Key-value metadata in every HTTP message, │
│              │ orthogonal to URL, method, and body      │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Protocol metadata (auth, caching,         │
│ SOLVES       │ content type) needs a channel separate    │
│              │ from the application payload              │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Every major HTTP feature (auth, caching,  │
│              │ CORS, compression) IS a header — headers  │
│              │ are the protocol's extensibility layer    │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Every HTTP request and response — always  │
│              │ set Content-Type, Cache-Control, and      │
│              │ Security headers explicitly               │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Never put secrets in URLs; always use     │
│              │ Authorization header over HTTPS           │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Rich expressiveness vs header overhead    │
│              │ (solved by HPACK in HTTP/2)               │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The body is what you're sending;         │
│              │  headers are the instructions."           │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ CORS → Content Negotiation →              │
│              │ ETag / Cache-Control → API Authentication │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** An API gateway sits between clients and 20 microservices. It adds these
headers to every request it proxies: `X-Request-ID`, `X-Trace-ID`, `X-Gateway-Version`,
`Authorization: Bearer <validated-token>`, and `X-Client-IP`. Three of these headers
are hop-by-hop and should not be forwarded; two are end-to-end and should reach
the microservice. Which are which, and what HTTP mechanism—beyond simple developer
convention—would allow a microservice to know which headers were added by the gateway
versus originating from the client?

**Q2.** A CDN caches API responses. The same endpoint `/api/products/123` returns
JSON for `Accept: application/json` requests and CSV for `Accept: text/csv` requests.
The CDN is configured to cache all 200 responses for 60 seconds. After correctly
setting `Vary: Accept`, analyse what happens when 1,000 clients send mixed JSON
and CSV requests simultaneously — what the CDN stores, how many origin hits occur,
and whether any configuration change would cause a security vulnerability where
Client A receives Client B's cached data.
