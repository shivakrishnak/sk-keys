---
layout: default
title: "HTTP Status Codes"
parent: "HTTP & APIs"
nav_order: 210
permalink: /http-apis/http-status-codes/
number: "210"
category: HTTP & APIs
difficulty: ★☆☆
depends_on: HTTP/1.1, HTTP Methods (GET, POST, PUT, PATCH, DELETE)
used_by: REST, API Design Best Practices, API Authentication, CORS
tags:
  - networking
  - protocol
  - http
  - rest
  - foundational
---

# 210 — HTTP Status Codes

`#networking` `#protocol` `#http` `#rest` `#foundational`

⚡ TL;DR — Three-digit numeric codes in HTTP responses indicating the outcome of a request — grouped by 1xx (informational), 2xx (success), 3xx (redirection), 4xx (client error), 5xx (server error).

| #210 | Category: HTTP & APIs | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | HTTP/1.1, HTTP Methods (GET, POST, PUT, PATCH, DELETE) | |
| **Used by:** | REST, API Design Best Practices, API Authentication, CORS | |

---

### 📘 Textbook Definition

**HTTP Status Codes** are three-digit integer codes returned in the first line of an HTTP response, providing the client with the result of its request. The first digit defines the response class: 1xx (Informational — request received, continuing process), 2xx (Success — request successfully received, understood, and accepted), 3xx (Redirection — further action needed), 4xx (Client Error — request contains bad syntax or cannot be fulfilled), 5xx (Server Error — server failed to fulfil an apparently valid request). Status codes are accompanied by a reason phrase and standardised in RFC 7231 (and individual RFCs for specific codes).

### 🟢 Simple Definition (Easy)

HTTP status codes are the server's short answer to your request: 200 means "here's what you asked for," 404 means "that doesn't exist," 500 means "something broke on my end."

### 🔵 Simple Definition (Elaborated)

Every HTTP response starts with a status code that tells the client whether the request succeeded and what to do next. The code's first digit groups them: 2xx is success, 3xx means "go somewhere else," 4xx means "you made a mistake," 5xx means "we made a mistake." API clients use these codes to decide whether to retry a request, handle an error, or follow a redirect. Returning the wrong status code (like 200 OK when an error occurred) is a common API design mistake that confuses clients and breaks error monitoring.

### 🔩 First Principles Explanation

**The need for standardised outcome signalling:**

Without status codes, the only way to know if a request succeeded would be to parse the response body — requiring knowledge of every API's specific response format. Status codes provide a universal machine-readable outcome signal, independent of response body format.

**Important codes by category:**

**1xx — Informational:**
- `100 Continue` — server received headers, client can send body (large upload protocol).
- `101 Switching Protocols` — server accepts upgrade (e.g., WebSocket handshake).

**2xx — Success:**
- `200 OK` — standard success response.
- `201 Created` — resource created (POST); should include `Location` header.
- `202 Accepted` — request accepted for async processing; not yet complete.
- `204 No Content` — success with no response body (DELETE, PUT without body response).
- `206 Partial Content` — response to Range request; body contains partial content.

**3xx — Redirection:**
- `301 Moved Permanently` — resource permanently at new URL; browser caches redirect.
- `302 Found` — temporary redirect; don't cache.
- `304 Not Modified` — cached resource still valid (conditional GET response).
- `307 Temporary Redirect` — same as 302 but method must not change.
- `308 Permanent Redirect` — same as 301 but method must not change.

**4xx — Client Error:**
- `400 Bad Request` — malformed request syntax.
- `401 Unauthorized` — authentication required (misnaming — should be "unauthenticated").
- `403 Forbidden` — authenticated but not authorised.
- `404 Not Found` — resource doesn't exist.
- `405 Method Not Allowed` — HTTP method not supported for this resource.
- `409 Conflict` — conflict with current state (e.g., duplicate creation, optimistic lock fail).
- `410 Gone` — resource permanently deleted (vs 404 which is ambiguous).
- `422 Unprocessable Entity` — validation errors in syntactically valid request.
- `429 Too Many Requests` — rate limit exceeded; include `Retry-After` header.

**5xx — Server Error:**
- `500 Internal Server Error` — generic unhandled exception.
- `502 Bad Gateway` — upstream server returned invalid response.
- `503 Service Unavailable` — server temporarily unavailable (overloaded, maintenance).
- `504 Gateway Timeout` — upstream server didn't respond in time.

### ❓ Why Does This Exist (Why Before What)

WITHOUT standardised status codes:

- Every API invents its own success/error signalling in the response body.
- Load balancers, CDNs, and proxies can't intelligently route failures.
- Retry logic must parse body content — tightly coupled to every API format.
- Monitoring tools can't automatically detect API errors without custom parsing.

What breaks without it:
1. `if (response.body().contains("error"))` is fragile and API-specific.
2. CDNs can't cache responses correctly without knowing success vs. redirect codes.

WITH HTTP Status Codes:
→ Universal signal: client knows outcome before parsing body.
→ CDNs/proxies handle redirects (3xx) and errors (4xx, 5xx) uniformly.
→ Alerting on `5xx rate > 0.1%` works for any HTTP service without custom parsing.

### 🧠 Mental Model / Analogy

> Status codes are like the traffic lights of the web. Green (2xx) = proceed, your request succeeded. Yellow (3xx) = go to a different place. Red — your fault (4xx) = check what you asked for. Red — our fault (5xx) = try again later, we have a problem. The light (code) is visible immediately without reading the road sign (parsing the body). Traffic signals are universal — the same light means the same thing everywhere.

"Traffic lights" = status codes, "green" = 2xx success, "yellow" = 3xx redirect, "red-your-fault" = 4xx, "red-our-fault" = 5xx.

### ⚙️ How It Works (Mechanism)

**Response structure:**

```
HTTP/1.1 404 Not Found
Content-Type: application/problem+json
Content-Length: 89

{
  "type": "https://api.example.com/errors/not-found",
  "title": "User not found",
  "status": 404,
  "detail": "User with id 42 does not exist"
}
```

**Retry semantics by status code:**

```
Code  | Retry?  | Notes
──────┼─────────┼─────────────────────────────────────
200   |   No    | Success
201   |   No    | Created — no retry
400   |   No    | Fix the request first
401   |   No    | Get a new token first
403   |   No    | Different credentials won't help
404   |   No    | Resource doesn't exist
409   |   No    | Resolve conflict first
429   |  Later  | Retry after Retry-After header
500   |  Maybe  | Server bug — may succeed later
502   |  Yes    | Upstream issue — retry is safe
503   |  Yes    | Retry after Retry-After
504   |  Yes    | Timeout — retry
```

### 🔄 How It Connects (Mini-Map)

```
HTTP Request → Server processes
                    ↓
            HTTP Status Codes ← you are here
                    ↓
   Client interprets:
     2xx → success path
     3xx → follow redirect
     4xx → handle client error (don't retry blindly)
     5xx → retry / fallback / alert
                    ↓
API Design Best Practices (use correct codes)
Circuit Breaker (monitors 5xx rates)
```

### 💻 Code Example

Example 1 — Implementing correct status codes in Spring Boot:

```java
@RestController
@RequestMapping("/users")
public class UserController {

    @PostMapping
    public ResponseEntity<User> create(@RequestBody @Valid User u) {
        User saved = service.save(u);
        return ResponseEntity
            .status(HttpStatus.CREATED)  // 201
            .location(URI.create("/users/" + saved.getId()))
            .body(saved);
    }

    @GetMapping("/{id}")
    public ResponseEntity<User> get(@PathVariable Long id) {
        return service.findById(id)
            .map(ResponseEntity::ok)      // 200
            .orElseThrow(() -> new ResponseStatusException(
                HttpStatus.NOT_FOUND,     // 404
                "User " + id + " not found"));
    }

    // Global exception handler
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ProblemDetail> handleValidation(
            MethodArgumentNotValidException e) {
        ProblemDetail pd = ProblemDetail
            .forStatus(HttpStatus.UNPROCESSABLE_ENTITY); // 422
        pd.setDetail("Validation failed: " +
            e.getBindingResult().getAllErrors());
        return ResponseEntity.unprocessableEntity().body(pd);
    }
}
```

Example 2 — Client-side retry logic based on status codes:

```java
HttpResponse<String> response = client.send(request, bodyHandler);

return switch (response.statusCode()) {
    case 200, 201, 204 -> response; // success
    case 301, 308 -> {
        // Permanent redirect — update bookmark and retry
        String newUrl = response.headers()
            .firstValue("Location").orElseThrow();
        yield client.send(redirect(newUrl), bodyHandler);
    }
    case 429 -> {
        long delay = response.headers()
            .firstValueAsLong("retry-after").orElse(60);
        Thread.sleep(delay * 1000);
        yield retry(request);
    }
    case 503, 504 -> retry(request); // transient; safe to retry
    default -> throw new ApiException(response.statusCode(),
                                      response.body());
};
```

Example 3 — 401 vs 403 distinction:

```java
// 401 Unauthorized = authentication required but not provided
// (despite the name "unauthorized", it means "unauthenticated")
if (token == null || !tokenService.isValid(token)) {
    throw new ResponseStatusException(
        HttpStatus.UNAUTHORIZED,  // 401
        "Authentication required");
}

// 403 Forbidden = authenticated but not authorised for this action
if (!user.hasRole("ADMIN")) {
    throw new ResponseStatusException(
        HttpStatus.FORBIDDEN,     // 403
        "Insufficient permissions");
}
```

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| 401 means "not authorised" (permissions) | 401 means "not authenticated" (no valid credentials). 403 means "not authorised" (authenticated but lacks permission). The HTTP spec naming is confusing. |
| 404 and 410 are interchangeable | 404 means "not found — may exist elsewhere or in future." 410 means "permanently deleted — stop asking." 410 tells crawlers to remove from index. |
| 200 OK is always the right success response | 201 for creation, 202 for async acceptance, 204 for no-body responses are more precise and help clients understand context. |
| 500 should be returned for validation errors | 400 (Bad Request) or 422 (Unprocessable Entity) for validation failures. 500 is for unexpected server bugs only. |
| 302 and 307 are equivalent | 302 allows the client to change method (POST → GET) on redirect. 307 requires the same method to be used. For API redirects, 307/308 are correct. |

### 🔥 Pitfalls in Production

**1. Returning 200 for Error Responses ("200 with error body")**

```java
// BAD: Anti-pattern — 200 status with error in body
@GetMapping("/users/{id}")
public Map<String, Object> getUser(@PathVariable Long id) {
    if (!exists(id)) {
        return Map.of("success", false, "error", "not found");
        // Status: 200 OK — clients, monitors, and CDNs don't detect errors!
    }
    return Map.of("success", true, "data", findUser(id));
}

// GOOD: Return correct status code
@GetMapping("/users/{id}")
public ResponseEntity<User> getUser(@PathVariable Long id) {
    return findUser(id)
        .map(ResponseEntity::ok)
        .orElse(ResponseEntity.notFound().build()); // 404
}
```

**2. Not Returning Retry-After with 429**

```java
// BAD: Rate limiting without telling client when to retry
throw new ResponseStatusException(HttpStatus.TOO_MANY_REQUESTS);

// GOOD: Include Retry-After header
HttpHeaders headers = new HttpHeaders();
headers.set("Retry-After", "60"); // seconds
return ResponseEntity
    .status(HttpStatus.TOO_MANY_REQUESTS)
    .headers(headers)
    .body(new ErrorResponse("Rate limit exceeded"));
```

**3. Using 500 for Business Logic Errors**

```java
// BAD: Catching business exception and returning 500
try {
    order.cancel();
} catch (OrderAlreadyShippedException e) {
    throw new ResponseStatusException(
        HttpStatus.INTERNAL_SERVER_ERROR, e.getMessage());
    // This triggers PagerDuty alerts and is misleading!
}

// GOOD: 409 Conflict for business state conflict
throw new ResponseStatusException(
    HttpStatus.CONFLICT,
    "Cannot cancel: order already shipped");
```

### 🔗 Related Keywords

- `HTTP Methods (GET, POST, PUT, PATCH, DELETE)` — the request methods that determine which codes are appropriate.
- `REST` — the architectural style with conventions for which codes to use for which operations.
- `API Design Best Practices` — guidelines including correct status code usage.
- `Circuit Breaker` — monitors 5xx error rates to determine when to open the circuit.
- `API Rate Limiting` — uses 429 Too Many Requests to signal rate limit violation.

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ 2xx Success  │ 200 OK | 201 Created | 204 No Content    │
│ 3xx Redirect │ 301 Perm | 302 Temp | 304 Not Modified   │
│ 4xx Client   │ 400 Bad | 401 Unauth | 403 Forbidden     │
│              │ 404 Not Found | 409 Conflict | 429 Limit │
│ 5xx Server   │ 500 Error | 502 Gateway | 503 Unavail    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Status code = the server's quick answer  │
│              │ before the body explains the details."    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ HTTP Headers → REST → RESTful Constraints │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A public REST API returns `200 OK` for all responses, including errors, putting error information in the JSON body (`{"success":false,"error":"not found"}`). This API gets significant traffic from CDNs. Describe at least three specific problems this design causes for CDN behaviour, client retry logic, and API monitoring infrastructure — and explain why each is caused specifically by the incorrect status code rather than the error message content.

**Q2.** Design the complete set of HTTP status codes for a distributed payment processing API that must handle: successful payment, insufficient funds, temporarily unavailable payment provider, idempotent retry of an already-processed payment, and an unauthenticated request. For each status code you choose, justify why alternatives were rejected and specify what additional headers or body information the response must include for the client to recover correctly.

