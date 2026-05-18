---
id: NET-030
title: "HTTP and HTTPS Basics"
category: Networking
tier: tier-2-networking-security
folder: NET-networking
difficulty: ★★☆
depends_on: NET-003, NET-020
used_by: NET-031, NET-032, NET-038, NET-039, NET-040, NET-044
related: NET-020, NET-031, NET-038, NET-044
tags:
  - networking
  - http
  - https
  - web
  - tls
  - request-response
status: complete
version: 4
layout: default
parent: "Networking"
grand_parent: "Technical Mastery"
nav_order: 30
permalink: /technical-mastery/net/http-and-https-basics/
---

**⚡ TL;DR** - HTTP is a stateless request-response
application protocol over TCP: client sends a request
(method + path + headers + optional body), server sends
a response (status + headers + optional body). HTTPS
is HTTP over TLS - same protocol, encrypted and
authenticated transport. HTTP/1.1 reuses connections
(keep-alive), HTTP/2 multiplexes requests on one
connection, HTTP/3 uses QUIC (UDP) to eliminate
head-of-line blocking.

| #030 | Category: Networking | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Client-Server Model, TCP | |
| **Used by:** | Load Balancer Basics, Reverse Proxy, HTTP/2 Multiplexing, HTTP/3 and QUIC, WebSocket Protocol, TLS Handshake Deep Dive | |
| **Related:** | TCP, Load Balancer Basics, HTTP/2 Multiplexing, TLS Handshake Deep Dive | |

---

### 🔥 The Problem This Solves

The web needed a simple, stateless protocol for fetching
documents and resources. HTTP solves this with a
request-response model: every interaction is: "I want
this resource" → "Here it is (or here's the error)." The
statelessness (each request is independent) enables
horizontal scaling - any server can handle any request
without shared session state. HTTPS adds confidentiality
and authentication: you know you're talking to the right
server and no one in between can read or modify the content.

---

### 📘 Textbook Definition

**HTTP (HyperText Transfer Protocol)** is defined in
RFC 9110 (semantics) and RFC 9112 (HTTP/1.1). It is a
stateless, request-response, application-layer protocol
using TCP as transport. An HTTP **request** has: method
(GET/POST/PUT/DELETE/PATCH/HEAD/OPTIONS), request-target
(path + query), HTTP version, headers (name:value pairs),
and optional body. An HTTP **response** has: status code
(100-599), reason phrase, headers, and optional body.
**HTTPS** is HTTP over TLS (RFC 8446 for TLS 1.3), which
provides encryption (confidentiality), authentication
(server certificate), and integrity (MAC prevents tampering).

---

### ⏱️ Understand It in 30 Seconds

**HTTP request/response anatomy:**

```
HTTP Request:
  GET /api/users?page=2 HTTP/1.1       ← method + path
  Host: api.example.com                ← required header
  Accept: application/json
  Authorization: Bearer eyJ0...        ← auth token
  [blank line]                         ← end of headers
  [no body for GET]

HTTP Response:
  HTTP/1.1 200 OK                      ← status line
  Content-Type: application/json       ← type of body
  Content-Length: 1234                 ← body size
  Cache-Control: max-age=300           ← caching hint
  [blank line]                         ← end of headers
  {"users": [...]}                     ← response body
```

**Status code families (must memorize):**

```
1xx - Informational (100 Continue, 101 Switching)
2xx - Success       (200 OK, 201 Created, 204 No Content)
3xx - Redirect      (301 Permanent, 302 Temp, 304 Not Modified)
4xx - Client Error  (400 Bad Req, 401 Unauth, 403 Forbidden,
                     404 Not Found, 429 Too Many Requests)
5xx - Server Error  (500 Internal, 502 Bad Gateway,
                     503 Unavailable, 504 Gateway Timeout)
```

---

### 🔩 First Principles Explanation

**HTTP methods and their semantics:**

```
┌──────────────────────────────────────────────────────────┐
│  HTTP Methods                                            │
├──────────┬──────────┬──────────┬───────────────────────  │
│  Method  │  Safe?   │ Idempot? │  Meaning               │
├──────────┼──────────┼──────────┼───────────────────────  │
│  GET     │  Yes     │  Yes     │  Retrieve resource     │
│  HEAD    │  Yes     │  Yes     │  GET without body       │
│  OPTIONS │  Yes     │  Yes     │  Query supported methods│
│  POST    │  No      │  No      │  Create/submit data    │
│  PUT     │  No      │  Yes     │  Replace resource      │
│  PATCH   │  No      │  No      │  Partial update        │
│  DELETE  │  No      │  Yes     │  Remove resource       │
└──────────┴──────────┴──────────┴───────────────────────  │
Safe = no side effects. Idempotent = same result on repeat.
```

**Safe:** GET/HEAD can be retried freely (no mutation).

**Idempotent:** PUT/DELETE can be retried on failure
without risk (PUT twice = same final state; DELETE twice
= second returns 404, same final state).

**NOT idempotent:** POST (creates new resource each time).
Retry logic must check for POST responses - a 504 timeout
could mean the POST succeeded on the server before timing
out, so retrying creates a duplicate.

**HTTP headers you must know:**

```
┌──────────────────────────────────────────────────────────┐
│  Critical HTTP Headers                                   │
├─────────────────────┬────────────────────────────────────┤
│  Content-Type       │  Body format (application/json,    │
│                     │  text/html, multipart/form-data)   │
├─────────────────────┼────────────────────────────────────┤
│  Content-Length     │  Body size in bytes. Enables       │
│                     │  message framing over TCP stream   │
├─────────────────────┼────────────────────────────────────┤
│  Transfer-Encoding: │  Send body in chunks (no need to  │
│  chunked            │  know total size beforehand)       │
├─────────────────────┼────────────────────────────────────┤
│  Authorization      │  Credentials (Bearer token, Basic) │
├─────────────────────┼────────────────────────────────────┤
│  Cache-Control      │  Caching directives (max-age,     │
│                     │  no-cache, no-store, must-revalid) │
├─────────────────────┼────────────────────────────────────┤
│  Connection:        │  HTTP/1.1: keep TCP connection     │
│  keep-alive         │  alive after response              │
├─────────────────────┼────────────────────────────────────┤
│  Location           │  Redirect target (in 3xx responses)│
├─────────────────────┼────────────────────────────────────┤
│  X-Request-Id       │  Request correlation ID for tracing│
├─────────────────────┼────────────────────────────────────┤
│  Retry-After        │  When to retry after 429/503       │
└─────────────────────┴────────────────────────────────────┘
```

---

### 🧪 Thought Experiment

**SETUP: POST idempotency problem**

Your payment API receives a POST /payments request.
The server processes the payment (charges the card)
and returns 200 OK. But the response is lost in transit.
The client receives a TCP timeout error.

**Problem:** Should the client retry?

If YES: the client retries the POST. The server creates
a second payment. Customer is charged twice. 😱

If NO: the client gives up. If the first payment
actually failed (server error before charging), customer
gets no service.

**Solution:**
Idempotency keys. Client generates a unique key (UUID)
and includes it in the request header:
`Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000`

Server checks if this key has been processed:
- Not seen before: process payment, store result with key
- Seen before: return the SAME stored result, don't charge again

This is how Stripe, Braintree, and all serious payment
APIs work. The key is stored in a distributed cache with
TTL (usually 24h). The client can safely retry any number
of times.

**THE INSIGHT:**
HTTP statelessness doesn't prevent state management at
the application level. Idempotency keys give POST the
safety of idempotent operations when you need retry logic.

---

### 🧠 Mental Model / Analogy

> HTTP is a very sophisticated vending machine protocol:
>
> You press a button (GET /resource or POST /action)
> The machine dispenses (200 OK with body)
> Or says "wrong button" (400 Bad Request)
> Or "out of stock" (404 Not Found)
> Or "please pay" (401 Unauthorized)
> Or "machine broken" (500 Internal Server Error)
> Or "see other machine" (301 Redirect)
>
> The machine doesn't remember you from last time
> (stateless). Each button press is independent.
> The button meaning is defined by convention
> (GET = read, POST = create, DELETE = remove).
>
> HTTPS puts the vending machine in a tamper-proof,
> locked booth so no one can see what you're buying
> or put fake candy in the slot.

---

### ⚙️ How It Works (Mechanism)

**HTTP vs HTTPS connection setup:**

```
HTTP:
  TCP 3-way handshake (1 RTT)
  → Send HTTP request immediately

HTTPS (TLS 1.3):
  TCP 3-way handshake (1 RTT)
  TLS 1.3 handshake (1 RTT)
  → Send HTTP request (total: 2 RTT before first byte)

HTTPS (TLS 1.3, 0-RTT resume):
  TCP 3-way handshake (1 RTT)
  TLS 1.3 0-RTT (with early data): 0 RTT
  → Send HTTP request with TLS handshake
  Total: 1 RTT for established session
```

**curl for HTTP debugging:**

```bash
# Full request/response verbose
curl -v https://api.example.com/users

# Show only timing breakdown
curl -o /dev/null -w "\
DNS: %{time_namelookup}s\n\
TCP connect: %{time_connect}s\n\
TLS: %{time_appconnect}s\n\
TTFB: %{time_starttransfer}s\n\
Total: %{time_total}s\n\
HTTP code: %{http_code}\n\
" https://api.example.com/users

# Test specific HTTP method
curl -X POST https://api.example.com/users \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"name": "Alice"}' \
  -v

# Follow redirects
curl -L https://short.url/abc

# Include response headers
curl -I https://api.example.com  # HEAD request (no body)
# or
curl -D - https://api.example.com  # GET + dump headers
```

**Wrong vs Right - HTTP error handling:**

```python
# BAD: only check for network errors
import requests

def get_user(user_id):
    try:
        response = requests.get(f'/api/users/{user_id}')
        return response.json()   # may be 404, 500 response!
    except requests.ConnectionError:
        return None

# GOOD: check HTTP status code explicitly
def get_user(user_id):
    try:
        response = requests.get(f'/api/users/{user_id}',
                                timeout=5.0)
        response.raise_for_status()   # raises on 4xx/5xx
        return response.json()
    except requests.HTTPError as e:
        if e.response.status_code == 404:
            return None    # not found is expected
        elif e.response.status_code == 429:
            retry_after = int(
                e.response.headers.get('Retry-After', 60))
            raise RateLimitError(retry_after)
        else:
            raise   # unexpected error: propagate
    except requests.Timeout:
        raise ServiceUnavailableError("API timeout")
    except requests.ConnectionError:
        raise ServiceUnavailableError("API unreachable")
```

**HTTP versions comparison:**

```
┌──────────────────────────────────────────────────────────┐
│  HTTP Version Comparison                                 │
├─────────────┬────────────────────────────────────────────┤
│  HTTP/1.0   │  One connection per request. No keep-alive │
│             │  by default. 1995. Obsolete.               │
├─────────────┼────────────────────────────────────────────┤
│  HTTP/1.1   │  Keep-alive by default. Pipelining (rarely │
│             │  used). One request at a time per          │
│             │  connection. HOL blocking. Still dominant. │
├─────────────┼────────────────────────────────────────────┤
│  HTTP/2     │  Binary framing. Multiplexing (multiple    │
│             │  requests on one TCP connection). Header   │
│             │  compression (HPACK). Server push. Still  │
│             │  has TCP HOL blocking.                     │
├─────────────┼────────────────────────────────────────────┤
│  HTTP/3     │  QUIC (UDP base). Per-stream reliability.  │
│             │  No TCP HOL blocking. TLS 1.3 integrated.  │
│             │  0-RTT on resume. ~30% of web traffic now. │
└─────────────┴────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**A complete HTTPS request, step by step:**

```
┌──────────────────────────────────────────────────────────┐
│  HTTPS Request Lifecycle                                 │
├──────────────────────────────────────────────────────────┤
│  1. DNS: api.example.com → 93.184.216.34 (if uncached)  │
│  2. TCP 3-way handshake to 93.184.216.34:443            │
│  3. TLS 1.3 handshake (1 RTT):                         │
│     - ClientHello (cipher suites, SNI: api.example.com) │
│     - ServerHello + Certificate + Finished             │
│     - Client verifies cert chain to trusted CA         │
│     - Session keys derived                             │
│  4. HTTP/1.1 request sent (encrypted):                  │
│     GET /api/users HTTP/1.1                            │
│     Host: api.example.com                              │
│     Authorization: Bearer eyJ0...                      │
│  5. Server processes request:                           │
│     Auth check → DB query → serialize response         │
│  6. HTTP response received (encrypted):                 │
│     HTTP/1.1 200 OK                                    │
│     Content-Type: application/json                     │
│     {"users": [...]}                                   │
│  7. Application reads response JSON                     │
│  8. TCP connection kept alive (keep-alive default)      │
│     Next request skips steps 1-3                       │
└──────────────────────────────────────────────────────────┘
```

**WHAT CHANGES AT SCALE:**
At 10,000 requests/second, HTTP keep-alive (connection
reuse) is critical - without it, 10K TCP+TLS handshakes/sec
would consume significant server CPU and add 100ms+ latency
to every request. At 100K rps, HTTP/2 multiplexing reduces
client-side connections from 6 (HTTP/1.1 browser limit)
to 1 per origin, reducing server connection memory. At
1M rps, HTTP/3's 0-RTT resume becomes significant:
mobile users reconnecting (new IP after network switch)
resume instantly without re-handshake latency.

---

### ⚖️ Comparison Table

| | HTTP/1.1 | HTTP/2 | HTTP/3 |
|---|---|---|---|
| **Transport** | TCP | TCP | QUIC (UDP) |
| **Connections** | 6 per origin | 1 per origin | 1 per origin |
| **Multiplexing** | No | Yes | Yes |
| **HOL blocking** | Per-connection | TCP level | None |
| **Header compression** | No | HPACK | QPACK |
| **TLS** | Separate | Separate | Integrated (1.3) |
| **0-RTT** | No | No | Yes |
| **Server Push** | No | Yes (deprecated) | No |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| 200 OK means success | HTTP 200 OK means the server returned a response. The response body might contain `{"error": "User not found"}`. Always validate the response BODY in addition to the status code. |
| HTTPS prevents all attacks | HTTPS encrypts the channel and authenticates the server certificate. It does NOT prevent: SQL injection in the request body, XSS in the response, broken access control, IDOR, or any application-level vulnerability. HTTPS is transport security only. |
| POST is for creating, GET is for reading | GET is for safe read operations (should never mutate state). POST is for non-idempotent operations (can mean "create" or "process" or "submit"). REST conventions define how methods map to CRUD, but HTTP itself only defines safety and idempotency. |
| HTTPS is slower than HTTP | With TLS 1.3 session resumption and HTTP/2, HTTPS can actually be FASTER than HTTP (multiplexing eliminates HTTP/1.1's 6-connection browser limit). The handshake overhead is paid once per session, then amortized over many requests. |

---

### 🚨 Failure Modes & Diagnosis

**502 Bad Gateway - Upstream Connection Failed**

**Symptom:** Load balancer or reverse proxy returns
502 Bad Gateway. Application server logs show nothing.
Network connectivity looks fine.

**Root Cause:** The load balancer connected to the
upstream server and got an unexpected response - typically:
(a) upstream closed the connection during request
(keep-alive connection expired), (b) upstream returned
a malformed response, (c) upstream port is unreachable
(server starting up), (d) upstream TLS certificate expired.

**Diagnosis:**
```bash
# Check if upstream is responding
curl -v http://upstream-server:8080/health
# 000 = connection refused (server down)
# 200 = server healthy

# Check load balancer logs for specific error
# nginx: /var/log/nginx/error.log
grep "upstream" /var/log/nginx/error.log | tail -20
# "connect() failed (111: Connection refused)"
# "upstream timed out (110: Connection timed out)"
# "upstream prematurely closed connection"

# 502 vs 504:
# 502 = LB connected to upstream but got bad response
# 504 = LB never got a response (upstream timeout)
```

**Fix:**
- If "prematurely closed": check keepalive_requests limit
  on upstream server. Nginx upstream keepalive pool
  settings. Adjust `proxy_read_timeout`.
- If "connection refused": upstream server is down.
  Check process, port, and health check endpoints.

---

### 🔗 Related Keywords

**Prerequisites:**
- `Client-Server Model` - HTTP IS the client-server model
- `TCP` - HTTP runs on TCP (or QUIC for HTTP/3)

**Builds On This:**
- `Load Balancer Basics` - LBs terminate and forward HTTP
- `Reverse Proxy` - proxies HTTP on behalf of clients
- `HTTP/2 Multiplexing` - HTTP/2 improvements
- `HTTP/3 and QUIC Protocol` - HTTP/3 improvements
- `TLS Handshake Deep Dive` - the S in HTTPS

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ METHODS      │ GET(safe+idempotent), POST(neither),      │
│              │ PUT(idempotent), DELETE(idempotent)        │
├──────────────┼───────────────────────────────────────────┤
│ STATUS CODES │ 2xx success, 3xx redirect, 4xx client err,│
│              │ 5xx server err. 502=bad upstream,         │
│              │ 504=upstream timeout                      │
├──────────────┼───────────────────────────────────────────┤
│ HTTPS        │ HTTP + TLS. Adds 1 RTT for TLS 1.3       │
│              │ handshake (0-RTT on resume)               │
├──────────────┼───────────────────────────────────────────┤
│ VERSIONS     │ 1.1=keep-alive, 2=multiplex over TCP,    │
│              │ 3=QUIC (UDP, no TCP HOL blocking)         │
├──────────────┼───────────────────────────────────────────┤
│ DEBUG        │ curl -v, curl -w timing, -I for headers  │
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ Retrying POST without idempotency key:    │
│              │ causes duplicate operations               │
│              │ Not setting request timeout: hangs forever│
├──────────────┼───────────────────────────────────────────┤
│ STATELESS    │ Each request independent. Server state    │
│              │ managed via session tokens, not HTTP conn │
└──────────────────────────────────────────────────────────┘
```

**Interview one-liner:**
"HTTP is a stateless request-response protocol over TCP:
method + path + headers → status + headers + body. Key
properties: GET is safe+idempotent (retry freely), POST
is neither (retry requires idempotency keys), statelessness
enables horizontal scaling. HTTPS adds TLS for encryption
and server authentication (1 RTT overhead per TLS 1.3
session, 0-RTT on resume). HTTP/2 multiplexes multiple
requests over one TCP connection eliminating HTTP/1.1's
6-connection limit; HTTP/3 uses QUIC (UDP) to eliminate
TCP head-of-line blocking. The most important operational
distinction: 4xx = client error (don't retry immediately),
5xx = server error (retry with backoff), 502 = upstream
connection issue, 504 = upstream timeout."