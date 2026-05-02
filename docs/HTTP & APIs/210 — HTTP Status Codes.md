---
layout: default
title: "HTTP Status Codes"
parent: "HTTP & APIs"
nav_order: 210
permalink: /http-apis/http-status-codes/
number: "0210"
category: HTTP & APIs
difficulty: ★☆☆
depends_on: HTTP/1.1, HTTP Methods
used_by: REST, API Design Best Practices, API Error Handling, Client Retry Logic
related: HTTP Methods, HTTP Headers, REST, API Design Best Practices
tags:
  - http
  - api
  - rest
  - protocol
  - foundational
---

# 210 — HTTP Status Codes

⚡ TL;DR — HTTP status codes are 3-digit machine-readable responses that tell the client exactly what happened to its request — success, redirection, client error, or server fault — enabling automated retry, routing, and error reporting without parsing response bodies.

| #210            | Category: HTTP & APIs                                                   | Difficulty: ★☆☆ |
| :-------------- | :---------------------------------------------------------------------- | :-------------- |
| **Depends on:** | HTTP/1.1, HTTP Methods                                                  |                 |
| **Used by:**    | REST, API Design Best Practices, API Error Handling, Client Retry Logic |                 |
| **Related:**    | HTTP Methods, HTTP Headers, REST, API Design Best Practices             |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Imagine every API returning `200 OK` with a body like `{"success": false, "message":
"User not found"}`. Now every HTTP client, load balancer, retry library, monitoring
tool, and CDN must parse JSON to understand whether the request worked. A circuit
breaker cannot distinguish a business-level "invalid input" from a server crash.
A cache cannot know whether the response is worth storing. Retry logic must parse
every response body to decide whether to retry. The result: massive coupling between
infrastructure components and application-specific error formats.

**THE BREAKING POINT:**
Without standardised status codes, every proxy, gateway, and monitoring tool would
need to understand the application's custom success/failure format — making generic
HTTP infrastructure impossible.

**THE INVENTION MOMENT:**
This is exactly why HTTP status codes were invented. They are a machine-readable
classification system that lets every layer of the HTTP stack act intelligently
without knowing anything about the application domain.

---

### 📘 Textbook Definition

**HTTP status codes** are 3-digit integers returned in the HTTP response status line
(`HTTP/1.1 200 OK`), grouped into five classes identified by the first digit:
**1xx** (Informational), **2xx** (Success), **3xx** (Redirection), **4xx** (Client
Error), and **5xx** (Server Error). Each code carries defined semantics specified
in RFC 7231 and related RFCs, enabling HTTP infrastructures (caches, proxies,
retry logic, load balancers, circuit breakers) to make routing, caching, and
retry decisions without inspecting response bodies. The status code is accompanied
by a human-readable reason phrase (`OK`, `Not Found`, `Internal Server Error`)
that adds no machine-readable meaning.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
HTTP status codes are a standardised 3-digit vocabulary that tells every machine
in the network what happened to a request — without reading the response body.

**One analogy:**

> Status codes are like traffic lights combined with road signs: 2xx is a green
> light (proceed, you got what you wanted), 3xx is a detour sign (go that way
> instead), 4xx is a "wrong road" sign (you drove incorrectly, fix your route),
> and 5xx is a "road closed" sign (it's our fault, not yours). The first digit
> tells every driver what category of situation they're in, even before they
> read the details.

**One insight:**
The most important thing about status codes is the 4xx vs 5xx distinction.
A 4xx error means the _client_ made a mistake — retrying the same request
will produce the same error. A 5xx error means the _server_ failed — the
same request might succeed if retried. This distinction drives all retry
logic in distributed systems.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. The first digit determines the category — always. Never return 200 with an
   error payload; always return the appropriate error status.
2. 4xx = client is wrong; 5xx = server is wrong. This is the fundamental
   retry/no-retry decision point in distributed systems.
3. Status codes are a machine-readable contract — they must be accurate, because
   automated infrastructure acts on them without human oversight.

**THE FIVE CLASSES:**

```
┌──────────────────────────────────────────────────────┐
│          HTTP Status Code Class Reference            │
├─────────┬──────────────────────────────────────────  │
│ 1xx     │ Informational — request received, continue │
│ 2xx     │ Success — understood and accepted          │
│ 3xx     │ Redirection — further action needed        │
│ 4xx     │ Client Error — bad request, caller's fault │
│ 5xx     │ Server Error — server failed, not caller   │
└─────────┴──────────────────────────────────────────  │
```

**KEY CODES WITH EXACT SEMANTICS:**

**2xx Success:**

- `200 OK` — generic success. Response body contains the result.
- `201 Created` — POST succeeded. `Location` header points to new resource.
- `202 Accepted` — async: request queued, not yet processed (fire-and-forget).
- `204 No Content` — success with no response body (DELETE, PATCH complete).
- `206 Partial Content` — range request fulfilled (video streaming).

**3xx Redirection:**

- `301 Moved Permanently` — resource moved; update bookmarks. Cached forever.
- `302 Found` — temporary redirect; do NOT update bookmarks. Not cached.
- `304 Not Modified` — conditional GET hit; client cache is fresh. No body.
- `307 Temporary Redirect` — like 302 but method preserved (POST → POST).
- `308 Permanent Redirect` — like 301 but method preserved.

**4xx Client Error:**

- `400 Bad Request` — malformed request, invalid input. Don't retry.
- `401 Unauthorized` — unauthenticated. Provide credentials.
- `403 Forbidden` — authenticated but unauthorised. Don't retry same auth.
- `404 Not Found` — resource doesn't exist. Don't retry.
- `405 Method Not Allowed` — method not supported at this URL.
- `408 Request Timeout` — client too slow sending request. May retry.
- `409 Conflict` — state conflict (e.g., version mismatch, duplicate).
- `410 Gone` — resource permanently deleted (stronger than 404).
- `422 Unprocessable Entity` — syntactically valid but semantically wrong.
- `429 Too Many Requests` — rate limit hit. Retry after `Retry-After`.

**5xx Server Error:**

- `500 Internal Server Error` — server crashed / unhandled exception.
- `502 Bad Gateway` — upstream server returned invalid response.
- `503 Service Unavailable` — server overloaded or in maintenance.
- `504 Gateway Timeout` — upstream server timed out.

**THE TRADE-OFFS:**

- Gain: machine-readable, universal, infrastructure-operable contract
- Cost: requires discipline to return correct codes; "200 with error body"
  anti-pattern is common and breaks all infrastructure assumptions

---

### 🧪 Thought Experiment

**SETUP:**
A payment service calls an inventory service. The request fails. The caller
must decide: retry immediately? retry later? fail permanently?

**WHAT HAPPENS WITH "200 OK" FOR EVERYTHING (anti-pattern):**

1. Inventory service is down; its load balancer returns custom JSON body:
   `{"error": "service unavailable", "code": "SVC_DOWN"}`
2. But status code is 200 OK (developer mistakenly used it for all responses)
3. Client's retry library sees 200 OK — interprets as success
4. Client parses body, finds "SVC_DOWN" — must implement custom retry logic
5. Circuit breaker sees all 200s — never opens (doesn't know service is down)
6. Monitoring alerts only on non-200 — shows 0 errors while service is down

**WHAT HAPPENS WITH CORRECT STATUS CODES:**

1. Inventory service is down; load balancer returns `503 Service Unavailable`
2. Client's retry library recognises 5xx = server error → retries with backoff
3. Circuit breaker tracks 503 rate → opens after 5 consecutive 503s
4. Monitoring: 503 spike triggers alert immediately
5. Zero custom code needed: retry, circuit breaking, and alerting all work
   from the status code alone

**THE INSIGHT:**
When status codes are accurate, every layer of infrastructure (retry libraries,
circuit breakers, CDN, API gateways, monitoring) makes correct decisions
automatically. When they're wrong (`200 OK` for errors), you must re-implement
all that intelligence yourself, in every client.

---

### 🧠 Mental Model / Analogy

> HTTP status codes are like the triage system in an emergency room. A patient
> walks in and the nurse immediately assigns a category: "stable" (2xx), "needs
> redirect to right department" (3xx), "patient filled out wrong form" (4xx),
> "equipment failure on our end" (5xx). The category label tells every staff
> member how to respond — no one has to examine the patient before knowing
> whether to call a specialist (retry) or send the patient home (fail).

**Mapping:**

- "emergency room triage" → HTTP status code classification
- "stable patient" → 2xx success
- "wrong department form" → 4xx client error (patient's fault)
- "equipment failure" → 5xx server error (hospital's fault)
- "staff's automated response by category" → retry libraries, circuit breakers

**Where this analogy breaks down:**
A patient can be both — symptoms correctly described (valid request) but beyond
treatment capability (server lacks the capacity). HTTP somewhat models this with
429 (rate limit) but the division is sometimes blurry in the 400 range.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
When your browser loads a website or an app calls an API, the server sends back
a number that summarises what happened: 200 means "here's what you asked for,"
404 means "this thing doesn't exist," 500 means "something crashed on our end,"
and 401 means "you need to log in first." These numbers let software understand
outcomes without reading long text descriptions.

**Level 2 — How to use it (junior developer):**
Return the correct status for every response: 200 for successful GET/PUT/PATCH,
201 (with Location) for successful POST creates, 204 for DELETE/no-body responses,
400 for validation errors, 401 for missing/invalid authentication, 403 for
authorisation failures, 404 for not-found resources, and 500 for unhandled
exceptions. Never return 200 with an error body — it breaks every automated tool
that relies on status codes. Always include `Retry-After` with 429 responses.

**Level 3 — How it works (mid-level engineer):**
Retry libraries (Resilience4j, OkHttp, Feign) are typically configured to retry
on 5xx and connectionReset errors, never on 4xx (because retrying a 400 Bad
Request wastes resources with the same invalid data). CDN cache policy is driven
by status: 200/206 responses with `Cache-Control` are stored; 4xx/5xx are not
cached by default (though 404 errors can be short-term cached to prevent stampedes).
`304 Not Modified` is a critical performance optimisation: the response has no
body — the cache serves its stored copy. Understanding conditional request headers
(`If-None-Match`, `If-Modified-Since`) that trigger 304 is essential for API
performance at scale.

**Level 4 — Why it was designed this way (senior/staff):**
The 5-class design reflects the fundamental actors in HTTP: 1xx are for the
network layer (proxies, streaming), 2xx-3xx for successful application-layer
interactions, 4xx for caller-correctable errors, and 5xx for server-side issues.
The `451 Unavailable For Legal Reasons` (a Fahrenheit 451 reference) shows the
spec's deliberate extensibility — anyone can define custom codes in ranges (e.g.,
Nginx uses 499 for "client disconnected"). The persistent confusion between 401
and 403 stems from HTTP's original definition: "Unauthorized" (401) means
"unauthenticated" — a naming error that the RFC's authors acknowledged but never
corrected for backward compatibility. Understanding these historical warts prevents
mis-implementing auth flows.

---

### ⚙️ How It Works (Mechanism)

**Status Line Structure:**

```
HTTP/1.1 201 Created\r\n
```

Three components: HTTP version, 3-digit code, reason phrase. Only the 3-digit
code has machine-readable meaning. The reason phrase is ignored by code.

**Decision Tree for Common Codes:**

```
┌──────────────────────────────────────────────────────┐
│         Status Code Selection Decision Tree          │
├──────────────────────────────────────────────────────┤
│ Request arrived?                                     │
│  No  → 408 Request Timeout                          │
│  Yes → authenticated?                               │
│    No  → 401 Unauthorized                           │
│    Yes → authorised?                                │
│      No  → 403 Forbidden                            │
│      Yes → resource exists?                         │
│        No  (GET/PUT/PATCH/DELETE) → 404 Not Found   │
│        Yes → valid input?                           │
│          No  → 400 Bad Request / 422 Unprocessable  │
│          Yes → action succeeded?                    │
│            No  → 500 (or 503 if overload)           │
│            Yes + created → 201 Created              │
│            Yes + returns body → 200 OK              │
│            Yes + no body → 204 No Content           │
└──────────────────────────────────────────────────────┘
```

**Retry-After Header (critical for 429):**

```
HTTP/1.1 429 Too Many Requests
Retry-After: 30
Content-Type: application/json

{"error": "rate_limit_exceeded", "retry_in_seconds": 30}
```

The `Retry-After` value is either an integer (seconds) or an HTTP date.
Well-behaved clients MUST respect this value.

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**

```
┌──────────────────────────────────────────────────────┐
│        Status Code in the Request Lifecycle          │
├──────────────────────────────────────────────────────┤
│ Client sends request                                 │
│   ↓                                                  │
│ Load balancer: 503 → don't route to sick node       │
│   ↓                                                  │
│ Cache: 304 → serve cached response, skip origin     │
│   ↓                                                  │
│ [HTTP STATUS CODE ← YOU ARE HERE]                   │
│ Server processes request, determines outcome        │
│   ↓                                                  │
│ Server returns status code + headers + body         │
│   ↓                                                  │
│ Retry library: 5xx → retry with backoff             │
│              4xx → fail immediately                 │
│   ↓                                                  │
│ Circuit breaker: 50% 5xx rate → open circuit        │
│   ↓                                                  │
│ Monitoring: 5xx spike → fire alert                  │
└──────────────────────────────────────────────────────┘
```

**FAILURE PATH:**
Server throws unhandled NullPointerException → framework catches → returns
`500 Internal Server Error` → client's retry policy kicks in → retries
3× with 1s/2s/4s backoff → all return 500 → circuit breaker records 4 failures
→ client returns fallback response.

**WHAT CHANGES AT SCALE:**
At very high scale, 429 and 503 rate limiting become the primary load management
tool. Correct implementation of `Retry-After` prevents thundering herd: if 10,000
clients all receive 429 with `Retry-After: 30`, they ALL retry 30 seconds later.
Use jitter: return randomised `Retry-After: 25–35` to spread the retry burst.

---

### 💻 Code Example

**Example 1 — Correct status codes in Spring Boot:**

```java
@RestController
@RequestMapping("/orders")
public class OrderController {

    @PostMapping
    public ResponseEntity<Order> createOrder(@RequestBody @Valid OrderDto dto) {
        Order order = orderService.create(dto);
        URI location = URI.create("/orders/" + order.getId());
        return ResponseEntity.created(location).body(order); // 201
    }

    @GetMapping("/{id}")
    public ResponseEntity<Order> getOrder(@PathVariable Long id) {
        return orderService.findById(id)
            .map(ResponseEntity::ok)          // 200
            .orElseThrow(() ->
                new ResponseStatusException(
                    HttpStatus.NOT_FOUND,      // 404
                    "Order " + id + " not found"));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteOrder(@PathVariable Long id) {
        orderService.delete(id);
        return ResponseEntity.noContent().build(); // 204
    }

    @ExceptionHandler(ConstraintViolationException.class)
    public ResponseEntity<ErrorDto> handleValidation(
            ConstraintViolationException ex) {
        return ResponseEntity.badRequest()  // 400
            .body(new ErrorDto(ex.getMessage()));
    }
}
```

**Example 2 — Client retry based on status code:**

```java
// BAD: Retrying on 400 wastes resources — bad request won't fix itself
RetryConfig config = RetryConfig.custom()
    .retryOnResult(response -> response.getStatus() >= 400)
    .build();

// GOOD: Only retry on 5xx and specific recoverable 4xx (429):
RetryConfig config = RetryConfig.custom()
    .retryOnResult(response -> {
        int status = response.getStatus();
        return status == 429        // rate limit: retry after backoff
            || status == 503        // server unavailable: retry
            || status == 502        // bad gateway: retry
            || status >= 500;       // server errors: retry
        // 4xx (not 429) = client error: don't retry, fail fast
    })
    .build();
```

**Example 3 — Correct 401 vs 403 usage:**

```java
// 401 Unauthorized = "Tell me who you are first"
// Use when: no valid auth token present
if (token == null || !tokenValidator.validate(token)) {
    throw new ResponseStatusException(HttpStatus.UNAUTHORIZED);
}

// 403 Forbidden = "I know who you are; you can't do this"
// Use when: valid token, but insufficient permissions
if (!authzService.canDelete(user, resource)) {
    throw new ResponseStatusException(HttpStatus.FORBIDDEN);
}
```

---

### ⚖️ Comparison Table

| Code | Class | Cacheable | Retriable          | Meaning                         |
| ---- | ----- | --------- | ------------------ | ------------------------------- |
| 200  | 2xx   | Yes       | N/A                | Success with body               |
| 201  | 2xx   | No        | N/A                | Created — check Location header |
| 204  | 2xx   | No        | N/A                | Success, no body                |
| 304  | 3xx   | N/A       | N/A                | Cache hit — no body             |
| 400  | 4xx   | No        | No                 | Bad input — fix request         |
| 401  | 4xx   | No        | No                 | Login first                     |
| 403  | 4xx   | No        | No                 | Authorised but blocked          |
| 429  | 4xx   | No        | Yes (after delay)  | Rate limited                    |
| 500  | 5xx   | No        | Yes (with backoff) | Server crashed                  |
| 503  | 5xx   | No        | Yes (with backoff) | Server overloaded               |

**How to choose retry strategy:** Never retry 4xx except 429 (rate limit) and
occasionally 408 (request timeout). Always retry 5xx with exponential backoff
and jitter. Never retry without a finite maximum attempts count.

---

### ⚠️ Common Misconceptions

| Misconception                                            | Reality                                                                                                                                  |
| -------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| 200 OK can be returned with an error message in the body | This is the most dangerous anti-pattern in API design. It breaks retry logic, circuit breakers, and monitoring entirely                  |
| 401 means "you don't have permission"                    | 401 means unauthenticated ("please send credentials"). 403 means authenticated but forbidden                                             |
| 404 means the endpoint doesn't exist                     | 404 means the _resource_ at that URL doesn't exist. The endpoint may be fine; the specific resource ID is missing                        |
| 500 should be the default for all errors                 | 500 is only for unexpected server errors. Validation errors → 400. Auth → 401/403. Not found → 404. Each has a precise meaning           |
| Returning 204 means "completed successfully"             | 204 specifically means success with no body. If your operation has a result to return, use 200. Use 204 for DELETE and body-less updates |

---

### 🚨 Failure Modes & Diagnosis

**200-for-Errors Anti-pattern (Monitoring Blindness)**

Symptom: Monitoring shows 0% error rate while users report failures; custom
error parsing logic duplicated in every client; circuit breakers never open.

Root Cause: API returns `200 OK` for all responses, including errors, with
error details only in response body. All HTTP infrastructure treats responses
as successful.

Diagnostic Command / Tool:

```bash
# Find 200 responses that contain error indicators:
cat access.log | awk '$9 == 200' | grep '"error"' | wc -l

# Test specific endpoint:
curl -s https://api.example.com/users/NONEXISTENT | jq .
# Returns {"status": "error", "message": "not found"} ... with 200 HTTP
```

Fix: Map all error conditions to correct 4xx/5xx codes. Use Spring's
`@ResponseStatus` or `@ExceptionHandler` to ensure consistent mapping.

Prevention: Add an integration test asserting that error conditions return
non-2xx codes. Include HTTP status code in API contract tests.

---

**Incorrect 403 vs 404 Leaking Resource Existence**

Symptom: Attackers enumerate valid resource IDs by observing which IDs return
403 (exists but forbidden) vs 404 (doesn't exist) — leaking sensitive data.

Root Cause: Server returns 403 for authenticated-but-unauthorised access to
existing resources, revealing that the resource exists.

Diagnostic Command / Tool:

```bash
# Security test: compare responses for own vs other user's resource:
curl -H "Authorization: Bearer alice_token" \
  https://api.example.com/documents/12345 # could return 403
curl -H "Authorization: Bearer alice_token" \
  https://api.example.com/documents/99999 # returns 404
# Difference reveals 12345 exists and alice can't access it
```

Fix: For sensitive resources, return 404 instead of 403 when the caller
shouldn't even know the resource exists (security through obscurity, but
legitimate here).

Prevention: Decide intentionally per endpoint: is resource existence itself
sensitive? If yes, use 404 for all unauthorised accesses.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `HTTP/1.1` — status codes are part of the HTTP response status line; the
  full semantics are defined in RFC 7231
- `HTTP Methods` — each method has specific expected success status codes;
  GET→200, POST→201, DELETE→204

**Builds On This (learn these next):**

- `REST` — REST APIs rely on correct status codes as the uniform interface
  for communicating operation outcomes
- `API Design Best Practices` — status code selection is a core API design
  skill; choosing the right code is part of building a good contract
- `Circuit Breaker` — circuit breaker patterns track 5xx rates to decide when
  to open the circuit

**Alternatives / Comparisons:**

- `gRPC Status Codes` — gRPC defines its own status code set (OK, NOT_FOUND,
  INTERNAL, etc.) with similar 5-class semantics but different integer values
- `GraphQL errors` — GraphQL always returns 200 OK and puts errors in a
  top-level `errors` array — a deliberate departure from HTTP status semantics

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ 3-digit machine-readable outcome codes   │
│              │ in every HTTP response status line       │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Without status codes, all HTTP infra     │
│ SOLVES       │ (caches, retries, CBs) is blind to       │
│              │ success vs failure                       │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ 4xx = caller's fault (don't retry);      │
│              │ 5xx = server's fault (do retry)          │
│              │ — this one rule drives distributed       │
│              │ resilience                               │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Every HTTP response — always use correct │
│              │ code, never 200-for-errors               │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Never use 200 to signal errors in body   │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Accurate codes enable free infrastructure │
│              │ intelligence vs requiring developer      │
│              │ discipline to use them correctly         │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "2xx = success, 4xx = your fault,        │
│              │  5xx = my fault — retry accordingly."    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ HTTP Headers → REST → API Design →       │
│              │ Circuit Breaker                          │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A distributed system has three services: Gateway → Order Service →
Inventory Service. A request to create an order results in the Inventory Service
returning `503 Service Unavailable`. The Order Service catches this and wraps it
as `500 Internal Server Error`. The Gateway logs `502 Bad Gateway`. The monitoring
alert fires on the Gateway's 502 rate. From an operations perspective, what
information is lost at each transformation step, and how would you design the
error propagation strategy differently to preserve root-cause diagnostics without
leaking internal service details to external clients?

**Q2.** An e-commerce API returns `200 OK` with a body `{"in_stock": false}` for
product availability checks. A CDN caches all 200 responses for 60 seconds. Ten
thousand users check the last unit of a product simultaneously. Describe step-by-step
what happens to inventory accuracy, CDN cache hit rates, and user experience —
then redesign the API response strategy using correct status codes and cache headers
to maintain both performance and accuracy.
