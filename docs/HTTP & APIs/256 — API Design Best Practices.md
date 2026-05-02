---
layout: default
title: "API Design Best Practices"
parent: "HTTP & APIs"
nav_order: 256
permalink: /http-apis/api-design-best-practices/
number: "0256"
category: HTTP & APIs
difficulty: ★★☆
depends_on: REST, HTTP, JSON
used_by: API Design, Backend Development, Platform Engineering
related: REST, OpenAPI/Swagger, API Versioning, API Documentation
tags:
  - api-design
  - rest
  - best-practices
  - naming-conventions
  - intermediate
---

# 256 — API Design Best Practices

⚡ TL;DR — API design best practices are the set of conventions that make REST APIs intuitive, consistent, and evolvable: use nouns for resources (not verbs), plural resource names, correct HTTP methods (GET/POST/PUT/PATCH/DELETE), meaningful status codes, versioning in the URL, consistent error response shapes, and design for backward compatibility — following these reduces integration friction and support burden.

┌──────────────────────────────────────────────────────────────────────────┐
│ #256         │ Category: HTTP & APIs              │ Difficulty: ★★☆      │
├──────────────┼────────────────────────────────────┼──────────────────────┤
│ Depends on:  │ REST, HTTP, JSON                   │                      │
│ Used by:     │ API Design, Backend Dev,           │                      │
│              │ Platform Engineering               │                      │
│ Related:     │ REST, OpenAPI/Swagger,             │                      │
│              │ API Versioning, API Documentation  │                      │
└──────────────────────────────────────────────────────────────────────────┘

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Your company has 5 backend teams, each building APIs independently. Team A: `POST /createUser`.
Team B: `GET /user/getAll`. Team C: `DELETE /removeOrder?orderId=5`.
Team D: errors return `{"errorCode": 42, "errMsg": "bad"}`. Team E: returns `200 OK` for
everything including failures (puts error in body). Every consumer integrates differently
with every team. The company's APIs form an inconsistent, unpredictable landscape.
Partners need 4-week integration time per API.

---

### 📘 Textbook Definition

**API Design Best Practices** are the conventions and principles for creating REST APIs
that are consistent, predictable, versioned, and developer-friendly. Core principles:
(1) Resource-oriented design: URLs identify resources (nouns, plural: `/users`, `/orders/{id}`).
(2) Correct HTTP method semantics: GET (read), POST (create), PUT (replace), PATCH (partial update),
DELETE (remove). (3) Meaningful HTTP status codes: 201 for creation, 400 for client error,
404 for not found, 409 for conflict, 422 for validation failure, 429 for rate limit, 500
for server error. (4) Structured error responses: consistent `{code, message, details}`.
(5) Versioning: `/api/v1/` in URL path. (6) Idempotency: PUT/DELETE are idempotent;
POST idempotency via `Idempotency-Key` header. (7) Pagination for list endpoints.
(8) Consistent naming: `snake_case` or `camelCase` uniformly throughout all APIs.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
API best practices are the grammar rules for REST APIs — follow them and developers understand
your API intuitively; break them and every caller needs to read your docs twice to not get it wrong.

**One analogy:**
> API design is like road traffic conventions.
> Drive on the right (or left) — as long as EVERYONE does the same thing.
> Stop at red lights (HTTP status codes mean what they mean).
> Highways have speed limits (rate limits).
> Road names make sense (resource paths).
> When convention is followed, driving in any city feels familiar.
> When conventions are ignored, every intersection is a potential accident.

---

### 🔩 First Principles — Key Rules

```
1. NOUNS NOT VERBS in URLs:
   ❌ POST /createUser
   ❌ GET /getUsers
   ❌ DELETE /deleteOrder?id=5
   ✅ POST /users           (create user)
   ✅ GET /users            (list users)
   ✅ DELETE /orders/{id}   (delete order)
   
   Exception: actions that don't map to CRUD:
   POST /payments/{id}/refund   → action on resource
   POST /orders/{id}/cancel     → state transition

2. PLURAL RESOURCE NAMES:
   ✅ /users, /orders, /products
   ❌ /user, /order, /product    (inconsistent: /user/5 is one user, /users is all)

3. CORRECT HTTP METHODS:
   GET    /users       → list (safe, idempotent)
   GET    /users/{id}  → read one (safe, idempotent)
   POST   /users       → create (NOT idempotent by default)
   PUT    /users/{id}  → replace entire resource (idempotent)
   PATCH  /users/{id}  → partial update (idempotent if implemented correctly)
   DELETE /users/{id}  → remove (idempotent: delete twice = same result as once)

4. MEANINGFUL STATUS CODES:
   200 OK              → success (GET, PUT, PATCH)
   201 Created         → resource created (POST); Location header with new resource URL
   204 No Content      → success, no body (DELETE, PATCH with no return)
   400 Bad Request     → malformed request (missing required fields, wrong JSON)
   401 Unauthorized    → not authenticated (no/invalid token)
   403 Forbidden       → authenticated but not authorized (wrong permissions)
   404 Not Found       → resource doesn't exist
   409 Conflict        → state conflict (e.g., email already registered)
   410 Gone            → resource permanently deleted (clients can clean up bookmarks)
   422 Unprocessable   → valid JSON but fails business validation
   429 Too Many Req    → rate limited; add Retry-After
   500 Internal Server → server bug (never expose stack traces)

5. CONSISTENT ERROR RESPONSE:
   {
     "code": "USER_EMAIL_TAKEN",       ← machine-readable code
     "message": "Email already exists",← human-readable message
     "details": [                       ← per-field errors for validation
       {"field": "email", "issue": "Already registered"}
     ],
     "requestId": "req-abc123"         ← for support tracing
   }

6. VERSIONING:
   /api/v1/users   ← version in path (most common, most discoverable)

7. NAMING CONSISTENCY:
   Pick camelCase OR snake_case and use it EVERYWHERE.
   JSON fields: camelCase (JS-friendly) or snake_case (databases)
   URLs: lowercase kebab-case: /payment-methods, /order-items

8. IDEMPOTENCY FOR SAFE RETRY:
   POST /payments + Idempotency-Key: {uuid}
   Same UUID → returns same response, does not create duplicate payment
```

---

### 🧪 Thought Experiment

**SCENARIO:** Audit 5 bad API decisions.

```
BAD: GET /api/deleteUser?id=5
FIX: DELETE /api/users/5
WHY: GET is cacheable and must be safe. Deleting via GET is a security risk 
     (CSRF: a link/image tag can trigger GET).

BAD: POST /api/orders → 200 OK {success: false, error: "Out of stock"}
FIX: POST /api/orders → 409 Conflict {code: "OUT_OF_STOCK", ...}
WHY: HTTP status code is how clients detect failure programmatically.
     Clients checking `response.ok` will miss the error.

BAD: GET /api/users → 200 OK with ALL 5 million users
FIX: GET /api/users?page=1&size=20 → paginated response
WHY: Unbounded list responses crash clients and servers.

BAD: Error response: {errorCode: 5, err: "bad input"}
FIX: {code: "VALIDATION_ERROR", message: "...", details: [{field: "email"}]}
WHY: Numeric codes require consulting a separate error code table.
     Inconsistent field names (err vs error vs message) break client code.

BAD: DELETE /api/orders/5 → 500 "Order does not exist"
FIX: DELETE /api/orders/5 → 404 Not Found (or 204 if idempotent delete)
WHY: DELETE should be idempotent. If the order is already gone: 
     404 (strict) or 204 (idempotent — didn't exist already = still deleted).
```

---

### 🧠 Mental Model / Analogy

> API design best practices are like postal address format conventions.
> Street address has a standard format: [house number] [street name], [city], [state] [zip].
> Deviating: "California 94102 Market St 100 SF" — technically contains all info,
> but breaks every address parser, mail sorter, and GPS system.
> The convention exists not because one format is inherently better — 
> but because consistency enables automated processing without custom handling per sender.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Use nouns in URLs, correct HTTP methods, and meaningful status codes. This covers 80% of API design correctness.

**Level 2:** Add consistent error response shape, versioning, pagination, `Location` header on POST 201, `Idempotency-Key` for POST. Document with OpenAPI.

**Level 3:** Design for idempotency, backward compatibility, and graceful deprecation. Apply HATEOAS links for discoverability. Design validation error responses per-field. Use problem details (RFC 7807) for structured errors. Separate authentication (401) from authorization (403) errors explicitly.

**Level 4:** View API design as a product. REST is a style, not a rigid spec — the goal is developer experience clarity, not theological REST purity. The most consequential decisions: naming consistency, error response shape, versioning strategy, and backward compatibility policy. These create long-term maintenance costs or benefits proportional to the number of consumers. Google's API Design Guide and AWS API Design principles are the industry-level codifications.

---

### ⚙️ How It Works (Mechanism)

```
RFC 7807 — PROBLEM DETAILS FOR HTTP APIs (structured errors):

  Standard error response body:
  Content-Type: application/problem+json
  {
    "type": "https://api.example.com/errors/validation-error",  ← URI for error type
    "title": "Validation Error",                                  ← human summary
    "status": 422,                                               ← mirrors HTTP status
    "detail": "Email address is invalid",                        ← detailed explanation
    "instance": "/api/v1/users",                                 ← which resource failed
    "errors": [                                                   ← extension: field errors
      {"field": "email", "message": "Not a valid email format"}
    ],
    "requestId": "req-9a8b7c"                                    ← for support lookup
  }
  
  ✅ Consistent (any client can parse any RFC 7807 error)
  ✅ Machine-readable (type URI identifies error category)
  ✅ Extensible (add application-specific fields)
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
WELL-DESIGNED CRUD RESOURCE (complete example):

  POST /api/v1/orders
  Content-Type: application/json
  Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000
  Body: {"productId": "PROD-123", "quantity": 2}
  ← 201 Created
     Location: /api/v1/orders/ORD-789
     Body: {"id": "ORD-789", "status": "pending", ...}

  GET /api/v1/orders/ORD-789
  ← 200 OK
     Cache-Control: private, max-age=60
     ETag: "v3"

  PATCH /api/v1/orders/ORD-789
  Body: {"quantity": 3}
  ← 200 OK (updated)

  DELETE /api/v1/orders/ORD-789
  ← 204 No Content

  DELETE /api/v1/orders/ORD-789 (again — idempotent)
  ← 404 Not Found (or 204 if idempotent soft-delete policy)
```

---

### 💻 Code Example

```java
// Well-designed Spring Boot REST controller following best practices
@RestController
@RequestMapping("/api/v1/orders")
@Validated
public class OrderController {

    @PostMapping
    public ResponseEntity<OrderResponse> createOrder(
            @RequestHeader(value = "Idempotency-Key", required = false) String idempotencyKey,
            @RequestBody @Valid CreateOrderRequest request) {

        Order order = orderService.create(request, idempotencyKey);

        URI location = URI.create("/api/v1/orders/" + order.getId());
        return ResponseEntity
            .created(location)  // 201 + Location header
            .body(toResponse(order));
    }

    @GetMapping("/{id}")
    public ResponseEntity<OrderResponse> getOrder(@PathVariable String id) {
        return orderService.findById(id)
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build()); // 404 (not 200 with empty body)
    }

    @PatchMapping("/{id}")
    public ResponseEntity<OrderResponse> updateOrder(
            @PathVariable String id,
            @RequestBody @Valid UpdateOrderRequest request) {
        return orderService.update(id, request)
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build());
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteOrder(@PathVariable String id) {
        orderService.delete(id);
        return ResponseEntity.noContent().build(); // 204 (not 200)
    }
}

// Consistent validation error response handler
@ExceptionHandler(MethodArgumentNotValidException.class)
public ResponseEntity<ProblemDetail> handleValidation(MethodArgumentNotValidException ex) {
    ProblemDetail problem = ProblemDetail.forStatusAndDetail(
        HttpStatus.UNPROCESSABLE_ENTITY, "Request validation failed");
    problem.setType(URI.create("https://api.example.com/errors/validation-error"));
    problem.setProperty("errors", ex.getBindingResult().getFieldErrors().stream()
        .map(fe -> Map.of("field", fe.getField(), "message", fe.getDefaultMessage()))
        .collect(Collectors.toList()));
    return ResponseEntity.unprocessableEntity().body(problem);
}
```

---

### ⚖️ Comparison Table

| Decision | Recommended | Common Mistake | Impact |
|---|---|---|---|
| URL design | Nouns, plural: `/users/{id}` | Verbs: `/getUser`, `/deleteOrder` | Breaking consumer code on every change |
| HTTP methods | GET/POST/PUT/PATCH/DELETE semantics | GET for delete, POST for everything | Caching failures, security vulnerabilities |
| Status codes | 201/204/404/422/409/429 precisely | Always 200, errors in body | Clients can't detect failure programmatically |
| Error shape | `{code, message, details, requestId}` | `{error: 5}` or plain string | Integration debug time multiplied |
| Versioning | `/api/v1/` in path | No versioning, or header-only | Can't make breaking changes safely |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| 200 OK with error in body is fine | Status code is the primary signal for success/failure. Clients use `response.ok` or status-code checks; a 200 with `{error: true}` bypasses standard HTTP error handling |
| PUT and PATCH are interchangeable | PUT replaces the entire resource (fields not provided → cleared). PATCH updates only provided fields. Using PUT for partial update silently clears fields |
| REST requires HATEOAS | HATEOAS (Hypermedia links in responses) is a REST constraint but almost no production APIs implement it fully. Practical REST = resources, correct methods, status codes |

---

### 🚨 Failure Modes & Diagnosis

**200 OK for Errors — Monitoring Blind Spot**

Symptom:
Payment failure rate: 0% (monitoring looks clean). Support tickets: "payments keep failing."
Root cause: API returns `200 OK {"success": false, "error": "Card declined"}`.
Monitoring alerts on 4xx/5xx only — failures are invisible.

Fix:
```java
// ❌ Before:
return ResponseEntity.ok(Map.of("success", false, "error", "Card declined"));

// ✅ After:
return ResponseEntity.status(HttpStatus.PAYMENT_REQUIRED)  // 402
    .body(new ErrorResponse("CARD_DECLINED", "Card declined by issuer"));

// Monitoring now automatically detects 402 responses as failures
```

---

### 🔗 Related Keywords

- `REST` — the architectural style these practices refine
- `OpenAPI/Swagger` — tool for documenting and validating API design decisions
- `API Versioning` — the versioning practice within API design
- `RFC 7807` — Problem Details standard for error responses

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ URLs         │ Nouns, plural: /users, /orders/{id}       │
│ METHODS      │ GET=read, POST=create, PUT=replace,       │
│              │ PATCH=partial, DELETE=remove              │
│ STATUS CODES │ 200/201/204/400/401/403/404/409/422/429   │
│ ERRORS       │ {code, message, details, requestId}       │
│ VERSIONING   │ /api/v1/ in path                          │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Consistent URLs, codes, errors = DX wins"│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ REST → OpenAPI/Swagger → API Versioning   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q.** You're reviewing an API design where `DELETE /api/users/{id}` returns `200 OK`
with the deleted user's body. Your colleague argues this is more useful than `204 No Content`
because callers can see what was deleted. The API design guide says use `204`. Who is
right and under what circumstances? What HTTP caching, client behavior, and idempotency
implications does returning a body with DELETE have, and when might the Google API
Design Guide allow exceptions to the `204` rule?
