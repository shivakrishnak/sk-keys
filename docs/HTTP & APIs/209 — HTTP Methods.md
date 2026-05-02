---
layout: default
title: "HTTP Methods (GET, POST, PUT, PATCH, DELETE)"
parent: "HTTP & APIs"
nav_order: 209
permalink: /http-apis/http-methods/
number: "0209"
category: HTTP & APIs
difficulty: ★☆☆
depends_on: HTTP/1.1, REST, URLs
used_by: RESTful Constraints, API Design Best Practices, Idempotency in HTTP
related: HTTP Status Codes, REST, Idempotency in HTTP, HTTP Headers
tags:
  - http
  - api
  - rest
  - protocol
  - foundational
---

# 209 — HTTP Methods (GET, POST, PUT, PATCH, DELETE)

⚡ TL;DR — HTTP methods declare the *intent* of a request — what the client wants to DO to the resource — giving servers, proxies, and caches semantic meaning beyond just "send me bytes."

| #209 | Category: HTTP & APIs | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | HTTP/1.1, REST, URLs | |
| **Used by:** | RESTful Constraints, API Design Best Practices, Idempotency in HTTP | |
| **Related:** | HTTP Status Codes, REST, Idempotency in HTTP, HTTP Headers | |

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Imagine a web where every action is a POST to a different URL. Want to read a
user? `POST /getUserById` with a JSON body. Want to delete one? `POST /deleteUser`.
Want to update? `POST /updateUser`. Now imagine caches, load balancers, and proxies
in between. A cache sees `POST /getUserById` — should it cache this? It has no
way to know this is a safe read operation. The load balancer routes a retry of
`POST /deleteUser` — is it safe to retry? Again, unknowable. Without semantic
method labels, every intermediate in the network is blind to intent.

**THE BREAKING POINT:**
Early RPC-style APIs (SOAP, XML-RPC) used only POST for everything and lost all
the infrastructure benefits HTTP was designed to provide. Caches couldn't cache,
retries were unsafe, and API contracts were implicit rather than machine-readable.

**THE INVENTION MOMENT:**
This is exactly why HTTP methods were standardised. RFC 7231 defines a vocabulary
of methods, each with precisely specified safety and idempotency properties —
allowing every layer of infrastructure to make intelligent decisions about caching,
retrying, and routing without understanding the application content.

---

### 📘 Textbook Definition

**HTTP methods** (also called **HTTP verbs**) are tokens in the HTTP request
start-line that indicate the desired action the client wants to perform on the
identified resource. RFC 7231 defines the core methods: **GET** (retrieve),
**HEAD** (retrieve headers only), **POST** (create/process), **PUT** (replace
entirely), **PATCH** (partial update), **DELETE** (remove), **OPTIONS** (discover
supported methods), and **TRACE** (diagnostic loop-back). Each method has two
key properties: **safety** (does the request modify server state?) and
**idempotency** (can the request be repeated with the same effect?). These
properties allow caches, proxies, and clients to make safe retry, caching,
and preflight decisions.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
HTTP methods tell the server what you want to do to a resource — read, create,
replace, update, or delete — using standardised verbs with defined safety rules.

**One analogy:**
> Think of HTTP methods as verbs on a file cabinet: GET = "let me read this
> folder," POST = "add a new document," PUT = "replace this entire document,"
> PATCH = "change just the address on page 2," DELETE = "shred this document."
> The labels aren't just helpful — they tell the filing clerk which operations
> can be safely repeated (GET) and which are one-shot (POST).

**One insight:**
The most important thing to understand about HTTP methods is not *what* they do
but *what properties they guarantee*: GET, HEAD, PUT, DELETE, and OPTIONS are
**idempotent** (repeating them has the same net effect), while GET, HEAD, and
OPTIONS are also **safe** (they don't modify state). These guarantees — not the
names — are what make HTTP infrastructure intelligent.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. A **safe** method does not modify server state. Clients, caches, and proxies
   can call safe methods freely without worrying about side effects.
2. An **idempotent** method can be repeated N times and produce the same result
   as calling it once. Network retries are safe for idempotent methods.
3. **Not all methods are both** — POST is neither safe nor idempotent; PUT is
   idempotent but not safe.

**THE PROPERTY TABLE:**

```
┌──────────────────────────────────────────────────────┐
│          HTTP Method Properties Matrix               │
├────────────┬────────────┬───────────────────────────┤
│ Method     │ Safe?      │ Idempotent?                │
├────────────┼────────────┼───────────────────────────┤
│ GET        │ Yes        │ Yes                       │
│ HEAD       │ Yes        │ Yes                       │
│ OPTIONS    │ Yes        │ Yes                       │
│ PUT        │ No         │ Yes                       │
│ DELETE     │ No         │ Yes                       │
│ POST       │ No         │ No                        │
│ PATCH      │ No         │ Conditionally (by design) │
└────────────┴────────────┴───────────────────────────┘
```

**DERIVED DESIGN:**
- **GET**: Retrieve a resource. No body. Response cacheable by default.
  The URL is the complete identifier.
- **HEAD**: Like GET but returns only headers (no body). Used to check
  existence, ETag, or Content-Length without downloading the resource.
- **POST**: Submit data to be processed. Creates a new resource or triggers
  an action. Not cacheable by default. Response may return 201 (created) or
  200 (processed). Body describes the new resource.
- **PUT**: Replace the *entire* resource at the URI with the request body.
  If it doesn't exist, creates it. Client supplies the complete representation.
- **PATCH**: Partially modify a resource using a patch document (RFC 5789).
  Only changes specified fields. Idempotency is NOT guaranteed by the spec —
  a PATCH containing `increment counter by 1` is not idempotent when sent twice.
- **DELETE**: Remove the resource. After success, subsequent DELETEs may
  return 404 (resource gone) or 204 (idempotent no-op). Both are correct.

**THE TRADE-OFFS:**
- Gain: Infrastructure intelligence (caching, retry safety), machine-readable
  contract, standardised routing
- Cost: Developers must think carefully about method semantics and not just
  use POST for everything; PATCH semantics require a defined patch format
  (JSON Patch, JSON Merge Patch)

---

### 🧪 Thought Experiment

**SETUP:**
A REST API for a to-do app. A user submits a "create task" request. The network
glitches and the client doesn't receive the response. The client must decide:
retry or not?

**WHAT HAPPENS WITH POST (no retry guarantee):**
1. Client sends `POST /tasks` with body `{"title": "Buy milk"}`
2. Server creates task ID=42, sends `201 Created`
3. Network drops the response — client never receives it
4. Client retries: sends `POST /tasks` again
5. Server creates ANOTHER task ID=43: `{"title": "Buy milk"}`
6. User now has a duplicate task — and no way to know without querying all tasks

**WHAT HAPPENS WITH PUT (idempotent):**
1. Client generates a client-side UUID: `00f3-abc1`
2. Client sends `PUT /tasks/00f3-abc1` with body `{"title": "Buy milk"}`
3. Server creates task at that ID, sends `201 Created`
4. Network drops the response
5. Client retries: sends `PUT /tasks/00f3-abc1` again
6. Server finds ID exists, replaces with same data, sends `200 OK`
7. Result: exactly one task — no duplicate

**THE INSIGHT:**
Idempotency is a distributed systems contract, not just an API design preference.
When the network is unreliable (it always is), idempotent methods allow safe
retries without coordination. Real-world payment APIs use this pattern with
Idempotency-Key headers to make POST idempotent even where the method is not.

---

### 🧠 Mental Model / Analogy

> HTTP methods are like the buttons on a vending machine, each with defined
> semantics: "See what's available" (GET), "Buy an item" (POST — creates a new
> transaction), "Replace item in slot 3 with different item" (PUT), "Fix the
> price label on slot 3" (PATCH), "Remove item from slot 3" (DELETE). The machine
> (server) and the maintenance system (caches/proxies) all know what each button
> implies — pressing "See what's available" a hundred times is always safe.

**Mapping:**
- "vending machine" → web resource / API endpoint
- "See what's available" → GET
- "Buy an item" → POST (creates new resource, not idempotent)
- "Replace item in slot" → PUT (replace entire resource)
- "Fix the label" → PATCH (partial update)
- "Remove item" → DELETE

**Where this analogy breaks down:**
The analogy implies that DELETE always results in empty state, but HTTP DELETE
on an already-absent resource is defined as idempotent — the second DELETE
returns 204 or 404, not an error. The "item is gone" state is the same regardless.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
HTTP methods are action words: GET means "give me this thing," POST means
"create something new," PUT means "replace this thing entirely," PATCH means
"change just part of this thing," and DELETE means "remove this thing." Servers
use these words to understand what you want to do, not just where you're sending
the request.

**Level 2 — How to use it (junior developer):**
GET for reads, POST for creates, PUT for full replace, PATCH for partial update,
DELETE for removes. Always return appropriate status codes: GET returns 200,
POST returns 201 (with Location header), PUT returns 200 or 204, PATCH returns
200 or 204, DELETE returns 204. Never use GET with a body — many caches and
proxies strip it. Use POST when the resource identity is server-assigned;
use PUT when the client controls the resource URI.

**Level 3 — How it works (mid-level engineer):**
Caches (CDN, browser, Nginx proxy cache) use method safety to decide what to
cache: safe methods are cacheable candidates; unsafe methods invalidate cached
representations. Retry logic in HTTP clients (OkHttp, Apache HttpClient) only
auto-retries idempotent methods on connection failure — never POST. `OPTIONS`
is used for CORS preflight: the browser asks "which methods and headers does
this cross-origin endpoint accept?" before sending the actual request. `HEAD`
is used for efficient size checks and ETags before conditional requests.

**Level 4 — Why it was designed this way (senior/staff):**
The safety/idempotency properties in RFC 7231 are the HTTP specification's
way of enabling layered, distributed infrastructure. They make HTTP a
self-describing protocol for intermediaries. The controversial choice was PATCH
(added in RFC 5789, 2010) — the committee debated whether to extend PUT semantics
or add a new verb. PATCH won because it correctly captures "delta update" semantics
that PUT cannot express. However, PATCH introduces a new question: what is the
*format* of the patch? RFC 6902 (JSON Patch) and RFC 7396 (JSON Merge Patch)
answered this — two competing standards that still cause API design debates.

---

### ⚙️ How It Works (Mechanism)

**Wire Format for Each Method:**

```
GET /users/123 HTTP/1.1
Host: api.example.com
Accept: application/json
```
No body allowed for GET. The resource is identified entirely by the URL.

```
POST /users HTTP/1.1
Host: api.example.com
Content-Type: application/json
Content-Length: 42

{"name":"Alice","email":"alice@example.com"}
```
Body contains the new resource representation. Server assigns ID.

```
PUT /users/123 HTTP/1.1
Host: api.example.com
Content-Type: application/json
Content-Length: 52

{"id":123,"name":"Alice","email":"updated@example.com"}
```
Complete resource representation. Server replaces the resource at /users/123.

```
PATCH /users/123 HTTP/1.1
Host: api.example.com
Content-Type: application/json-patch+json

[{"op":"replace","path":"/email","value":"new@example.com"}]
```
Only the specified fields change. Uses JSON Patch (RFC 6902) format.

```
DELETE /users/123 HTTP/1.1
Host: api.example.com
```
No body. Server removes the resource and returns 204 No Content.

**Method Routing in Spring Boot:**
```
┌──────────────────────────────────────────────────────┐
│         HTTP Method → Spring Handler Mapping         │
├──────────────────────────────────────────────────────┤
│ GET    /users/{id}  → @GetMapping("/users/{id}")    │
│ POST   /users       → @PostMapping("/users")        │
│ PUT    /users/{id}  → @PutMapping("/users/{id}")    │
│ PATCH  /users/{id}  → @PatchMapping("/users/{id}")  │
│ DELETE /users/{id}  → @DeleteMapping("/users/{id}") │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
┌──────────────────────────────────────────────────────┐
│       HTTP Method Request Lifecycle                  │
├──────────────────────────────────────────────────────┤
│ Client selects method based on intent                │
│   ↓                                                  │
│ GET? → Check cache → Cache HIT? Return cached       │
│   ↓ (miss)                                           │
│ [HTTP METHOD ← YOU ARE HERE]                         │
│ Request reaches server with method in start-line     │
│   ↓                                                  │
│ Server router matches method + path → handler        │
│   ↓                                                  │
│ Handler executes business logic                      │
│   ↓                                                  │
│ Response with status code (200/201/204/404/405)      │
│   ↓                                                  │
│ GET response: cache stores it                        │
│ POST response: cache INVALIDATES related GET URLs    │
└──────────────────────────────────────────────────────┘
```

**FAILURE PATH:**
Client sends POST to an endpoint that only accepts GET → server returns
`405 Method Not Allowed` with `Allow: GET, HEAD` header listing what IS allowed.

**WHAT CHANGES AT SCALE:**
At high volume, correct method usage has cache-level impact: an API that exposes
reads as GET allows CDN caching of millions of read requests; an API using POST
for reads bypasses all caches and hits the origin for every request. A wrongly-
designed "search via POST" endpoint forced to origin is a silent scalability bomb.

---

### 💻 Code Example

**Example 1 — REST controller in Java/Spring:**
```java
@RestController
@RequestMapping("/users")
public class UserController {

    // GET: safe + idempotent. Return 200 OK.
    @GetMapping("/{id}")
    public ResponseEntity<User> getUser(@PathVariable Long id) {
        return ResponseEntity.ok(userService.findById(id));
    }

    // POST: not safe, not idempotent. Return 201 + Location.
    @PostMapping
    public ResponseEntity<User> createUser(@RequestBody UserDto dto) {
        User created = userService.create(dto);
        URI location = URI.create("/users/" + created.getId());
        return ResponseEntity.created(location).body(created);
    }

    // PUT: replace entire resource. Return 200 or 204.
    @PutMapping("/{id}")
    public ResponseEntity<User> replaceUser(
            @PathVariable Long id,
            @RequestBody User user) {
        user.setId(id);
        return ResponseEntity.ok(userService.replace(user));
    }

    // PATCH: partial update. Return 200 or 204.
    @PatchMapping(value = "/{id}",
        consumes = "application/merge-patch+json")
    public ResponseEntity<User> patchUser(
            @PathVariable Long id,
            @RequestBody Map<String, Object> patch) {
        return ResponseEntity.ok(userService.patch(id, patch));
    }

    // DELETE: remove. Return 204 No Content.
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteUser(@PathVariable Long id) {
        userService.delete(id);
        return ResponseEntity.noContent().build();
    }
}
```

**Example 2 — Client-side method selection (fetch API):**
```javascript
// BAD: Using POST for a read operation — not cacheable, not safe
const res = await fetch('/api/users/123', { method: 'POST' });

// GOOD: GET for reads — CDN/browser cache can serve this
const res = await fetch('/api/users/123'); // default method = GET

// GOOD: PATCH for partial update (not PUT which requires full body)
const res = await fetch('/api/users/123', {
  method: 'PATCH',
  headers: { 'Content-Type': 'application/merge-patch+json' },
  body: JSON.stringify({ email: 'new@example.com' })
});
```

---

### ⚖️ Comparison Table

| Method | Safe | Idempotent | Body? | Success Code | Best For |
|---|---|---|---|---|---|
| **GET** | Yes | Yes | No | 200 | Read resource |
| HEAD | Yes | Yes | No | 200 | Check existence/ETag |
| **POST** | No | No | Yes | 201/200 | Create resource |
| **PUT** | No | Yes | Yes | 200/204 | Replace full resource |
| **PATCH** | No | Conditional | Yes | 200/204 | Partial update |
| **DELETE** | No | Yes | No | 204/404 | Remove resource |
| OPTIONS | Yes | Yes | No | 200/204 | CORS preflight |

**How to choose:** Use GET for reads, POST when creating a server-assigned
resource, PUT when the client controls the resource URI and sends the full
representation, PATCH for partial updates where sending the full resource
is impractical.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| PUT and PATCH are interchangeable | PUT replaces the ENTIRE resource; PATCH changes only specified fields. Sending a partial body to PUT silently clears omitted fields |
| POST is always for creates | POST can also trigger actions (POST /payments/123/capture) or process data without creating persistent resources |
| DELETE is always idempotent | Conceptually yes (deleting a deleted resource leaves it deleted), but servers may return 404 on second call — which is still correct and idempotent by definition |
| GET can have a body for search queries | While technically possible, many caches, proxies, and servers strip or ignore GET bodies. Use POST or query parameters for complex searches |
| PATCH is always idempotent | NOT guaranteed by spec. An `increment-by-1` PATCH applied twice produces a different state than once. Design PATCH bodies carefully |

---

### 🚨 Failure Modes & Diagnosis

**Using POST for Idempotent Operations (Duplicate Creates)**

Symptom: Duplicate records in database after network retries; race conditions
visible in database unique constraint violations; users report seeing duplicate
orders/payments.

Root Cause: POST is not idempotent. When a mobile client retries a failed
POST (network timeout), the server may have processed the first request but
failed to return the response.

Diagnostic Command / Tool:
```bash
# Check for duplicate records in database:
SELECT email, COUNT(*) FROM users
GROUP BY email HAVING COUNT(*) > 1;

# Check server access logs for duplicate POST request IDs:
grep "POST /users" access.log | awk '{print $10}' | sort | uniq -d
```

Fix:
```java
// Use Idempotency-Key header to detect duplicates:
@PostMapping("/orders")
public ResponseEntity<Order> createOrder(
        @RequestHeader("Idempotency-Key") String idempotencyKey,
        @RequestBody OrderDto dto) {
    // Check if we've seen this key before:
    return idempotencyStore.getOrCreate(idempotencyKey,
        () -> orderService.create(dto));
}
```

Prevention: Accept an `Idempotency-Key` header on all POST endpoints.
Cache server responses keyed by that value for 24–48 hours.

---

**PUT vs PATCH Confusion (Silent Data Loss)**

Symptom: User updates only their email, but their phone number disappears;
partial PUT calls silently clear fields not included in the request body.

Root Cause: Client sends PUT with only changed fields instead of full resource.
Server replaces the entire resource, setting unspecified fields to null.

Diagnostic Command / Tool:
```bash
# Compare before/after state:
curl -s https://api.example.com/users/123 | jq .
# Send partial PUT and check result:
curl -X PUT -H "Content-Type: application/json" \
  -d '{"email":"new@example.com"}' \
  https://api.example.com/users/123
curl -s https://api.example.com/users/123 | jq .phone
# Result: null  ← data loss
```

Fix: Use PATCH for partial updates. If you must use PUT, always send the
complete resource representation (fetch current state first, then modify).

Prevention: Document method semantics clearly in OpenAPI spec. Return 400
for PUT requests that are missing required fields.

---

**405 Method Not Allowed — CORS Preflight Failure**

Symptom: Browser shows CORS error; DevTools shows a `405 Method Not Allowed`
on an OPTIONS request; the actual API request never fires.

Root Cause: The server does not handle `OPTIONS` requests for CORS preflight.
Browsers automatically send OPTIONS before cross-origin POST/PUT/PATCH/DELETE.

Diagnostic Command / Tool:
```bash
# Simulate CORS preflight manually:
curl -X OPTIONS \
  -H "Origin: https://frontend.example.com" \
  -H "Access-Control-Request-Method: POST" \
  -v https://api.example.com/users 2>&1 | grep "< HTTP"
# Should return 200 or 204, not 405
```

Fix: Configure CORS globally in Spring Boot:
```java
@Bean
public CorsConfigurationSource corsConfigurationSource() {
    CorsConfiguration config = new CorsConfiguration();
    config.setAllowedMethods(List.of("GET","POST","PUT","PATCH","DELETE"));
    // OPTIONS handled automatically
    UrlBasedCorsConfigurationSource source = new ...();
    source.registerCorsConfiguration("/**", config);
    return source;
}
```

Prevention: Always register OPTIONS as an allowed method in any HTTP framework
or API gateway CORS configuration.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `HTTP/1.1` — HTTP methods are defined as part of the HTTP/1.1 request format;
  understanding the request-line structure is required
- `URLs` — the resource being acted upon is identified by the URL; method +
  URL = a complete operation identifier

**Builds On This (learn these next):**
- `REST` — REST uses HTTP methods as the uniform interface for resource manipulation
- `Idempotency in HTTP` — the practical implications of method idempotency for
  distributed system retry safety
- `HTTP Status Codes` — each method has expected success status codes; GET→200,
  POST→201, DELETE→204

**Alternatives / Comparisons:**
- `gRPC` — defines operations via Protobuf service definitions rather than HTTP
  methods; RPC semantics replace REST method semantics
- `GraphQL` — uses POST exclusively; sidesteps HTTP method semantics entirely
  in favor of operation type fields (`query`, `mutation`, `subscription`)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Semantic verbs that declare client intent │
│              │ (read/create/replace/update/delete)       │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Without method semantics, caches and      │
│ SOLVES       │ proxies cannot safely cache, retry, or    │
│              │ route requests                            │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Safety and idempotency are the real       │
│              │ properties that matter — not the names    │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Designing any HTTP API — always assign    │
│              │ methods based on their properties         │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Never use GET with side effects; never    │
│              │ use POST when PUT/PATCH is more precise   │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Strict semantics enable infrastructure    │
│              │ intelligence vs requiring discipline in   │
│              │ API design                                │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "GET is safe to repeat forever. POST is a │
│              │  one-shot with consequences."             │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ HTTP Status Codes → REST →                │
│              │ Idempotency in HTTP                       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A search API at `POST /search` accepts a complex JSON query body (5 nested
filters, sort fields, and pagination). A developer argues this should be `GET /search`
with query parameters instead. List the specific infrastructure capabilities (CDN
caching, retry safety, browser history, bookmarkability) that each approach enables
or disables, and identify the precise technical constraint that forces the developer
to choose POST over GET for very complex search queries.

**Q2.** A client and server are behind different load balancers with 30-second idle
TCP timeouts. A client sends `PUT /files/upload123` with a 50 MB body. The body
upload takes 45 seconds. The TCP connection drops at second 35 due to the idle
timeout. The client retries. What is the correct server behaviour when it receives
the retry PUT — and how does the idempotency guarantee of PUT change the required
server implementation compared to a retry of POST?
