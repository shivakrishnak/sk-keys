---
layout: default
title: "HTTP Methods (GET, POST, PUT, PATCH, DELETE)"
parent: "HTTP & APIs"
nav_order: 209
permalink: /http-apis/http-methods/
number: "209"
category: HTTP & APIs
difficulty: ★☆☆
depends_on: HTTP/1.1, REST
used_by: RESTful Constraints, Idempotency in HTTP, API Design Best Practices
tags:
  - networking
  - protocol
  - http
  - rest
  - foundational
---

# 209 — HTTP Methods (GET, POST, PUT, PATCH, DELETE)

`#networking` `#protocol` `#http` `#rest` `#foundational`

⚡ TL;DR — Standardised verbs that tell a server what action to perform on a resource — GET retrieves, POST creates, PUT replaces, PATCH partially updates, DELETE removes.

| #209 | Category: HTTP & APIs | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | HTTP/1.1, REST | |
| **Used by:** | RESTful Constraints, Idempotency in HTTP, API Design Best Practices | |

---

### 📘 Textbook Definition

**HTTP Methods** (also called HTTP verbs) are tokens in an HTTP request that define the semantic intent of the operation on the identified resource. The primary methods are: `GET` (retrieve a resource representation), `POST` (submit an entity to create a resource or trigger an action), `PUT` (replace a resource entirely with the provided representation), `PATCH` (apply a partial modification to a resource), and `DELETE` (remove the identified resource). Methods are characterised by two properties: **safe** (no server state change: GET, HEAD, OPTIONS) and **idempotent** (repeating produces the same result: GET, PUT, DELETE). POST is neither safe nor idempotent by semantics.

### 🟢 Simple Definition (Easy)

HTTP methods are the action words in a web request: GET (read), POST (create), PUT (replace), PATCH (update partially), DELETE (remove).

### 🔵 Simple Definition (Elaborated)

When you interact with a REST API, you choose an HTTP method to indicate what you're trying to do with a resource. Naming the action separately from the URL (the resource) is what makes REST work. GETting `/users/42` means "give me user 42." POSTing to `/users` means "create a new user." PUTting to `/users/42` means "replace user 42 with this data." PATCHing `/users/42` means "update only the specified fields of user 42." DELETEing `/users/42` means "remove user 42." Each method has defined properties (idempotency, safety) that affect how clients, proxies, and caches should treat them.

### 🔩 First Principles Explanation

**Why separate method from URL?**

Without methods, you'd embed actions in URLs: `/getUser?id=42`, `/deleteUser?id=42`, `/createUser`. This couples action semantics to URL paths, breaks caching (caches can't know if `/getUser` is safe to cache), and prevents uniform treatment of resources.

**Method properties:**

```
Method  | Safe | Idempotent | Body  | Cached
────────┼──────┼────────────┼───────┼────────
GET     |  Yes |    Yes     |  No*  |  Yes
HEAD    |  Yes |    Yes     |  No   |  Yes
POST    |   No |     No     |  Yes  |   No
PUT     |   No |    Yes     |  Yes  |   No
PATCH   |   No |    No*     |  Yes  |   No
DELETE  |   No |    Yes     |  No*  |   No
OPTIONS |  Yes |    Yes     |  No   |   No
```

**Safe:** Reading a resource should not cause side effects. Caches and proxies can feel free to make GET requests on behalf of clients.

**Idempotent:** Making the same request N times has the same effect as making it once. PUT with `{"name":"Alice"}` always results in user having that name — calling it 3 times doesn't create 3 users or set the name 3× times.

**Why POST is not idempotent:** Each POST to `/orders` creates a NEW order. Calling it 3 times creates 3 orders.

**PUT vs PATCH:**
```
Existing user: {"name":"Alice","email":"alice@ex.com","age":30}

PUT /users/42 with {"name":"Alice","email":"alice@ex.com","age":31}
→ Replaces entire document: ALL fields must be sent

PATCH /users/42 with {"age":31}
→ Merges: only specified fields changed
→ Result: {"name":"Alice","email":"alice@ex.com","age":31}
```

### ❓ Why Does This Exist (Why Before What)

WITHOUT standardised HTTP methods:

- URL-encoded actions: `/api?action=delete&id=42` — non-uniform, not cacheable.
- Caches can't distinguish read from write operations.
- No semantic meaning for retrying a failed request safely.

What breaks without it:
1. Retrying a POST after network failure creates duplicate resources.
2. GET requests with side effects are incorrectly cached by CDNs and proxies.

WITH HTTP Methods:
→ Clients know: "safe to retry GET; never auto-retry POST; idempotent to retry PUT/DELETE."
→ CDNs cache GET/HEAD automatically; POST/PUT/DELETE bypass cache.
→ Browser can pre-fetch (GET) links speculatively without causing side effects.

### 🧠 Mental Model / Analogy

> Think of HTTP methods as actions on a filing cabinet with labelled folders. GET = "read the document in folder 42." POST = "add a new document to the cabinet" (cabinet assigns it a new ID). PUT = "replace the entire contents of folder 42 with this new document." PATCH = "update only the highlighted section of folder 42." DELETE = "remove folder 42 from the cabinet." The folder path (URL) is the "what" and the method is the "how."

"Filing cabinet" = server, "folder" = resource (URL path), "actions on the folder" = HTTP methods.

The key insight: separating WHAT (resource URL) from HOW (method) enables uniform interfaces, caching, and idempotency reasoning.

### ⚙️ How It Works (Mechanism)

**Method semantics and response codes:**

```
GET    /users        → 200 OK + list of users
GET    /users/42     → 200 OK + user 42 | 404 Not Found
POST   /users        → 201 Created + Location: /users/43
PUT    /users/42     → 200 OK | 204 No Content | 201 Created
PATCH  /users/42     → 200 OK + updated resource | 204 No Content
DELETE /users/42     → 204 No Content | 404 Not Found
OPTIONS /users       → 200 OK + Allow: GET, POST, OPTIONS
HEAD   /users/42     → 200 OK (same as GET but no body)
```

**Idempotency key table:**

```
Request → Expected behaviour
──────────────────────────────────────────────────
GET /users/42        → always returns same user (if exists)
DELETE /users/42 ×3  → 1st: 204, 2nd+: 404 (still idempotent!)
PUT /users/42 ×3     → user 42 always in same state after each call
POST /orders ×3      → 3 separate orders created (NOT idempotent!)
PATCH user age ×3    → age set to 31 ×3 times = 31 (idempotent if absolute)
PATCH age += 1 ×3    → age 30→31→32→33 (NOT idempotent — relative patch)
```

### 🔄 How It Connects (Mini-Map)

```
HTTP/1.1 (defines methods in request line)
           ↓
HTTP Methods ← you are here
  GET | POST | PUT | PATCH | DELETE
           ↓ constraints defined by
Idempotency in HTTP | RESTful Constraints
           ↓ implemented via
REST API Design | API Best Practices
           ↓ tested with
cURL | Postman | REST Assured
```

### 💻 Code Example

Example 1 — All 5 methods with Spring Boot:

```java
@RestController
@RequestMapping("/users")
public class UserController {

    // GET /users → list all users
    @GetMapping
    public List<User> getAll() {
        return userService.findAll();
    }

    // GET /users/{id} → get single user
    @GetMapping("/{id}")
    public ResponseEntity<User> getOne(@PathVariable Long id) {
        return userService.findById(id)
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build());
    }

    // POST /users → create new user; returns 201 Created
    @PostMapping
    public ResponseEntity<User> create(@RequestBody User user) {
        User saved = userService.save(user);
        URI location = URI.create("/users/" + saved.getId());
        return ResponseEntity.created(location).body(saved);
    }

    // PUT /users/{id} → replace user entirely
    @PutMapping("/{id}")
    public ResponseEntity<User> replace(
            @PathVariable Long id, @RequestBody User user) {
        user.setId(id);
        return ResponseEntity.ok(userService.replace(user));
    }

    // PATCH /users/{id} → partial update
    @PatchMapping("/{id}")
    public ResponseEntity<User> update(
            @PathVariable Long id,
            @RequestBody Map<String, Object> updates) {
        return ResponseEntity.ok(
            userService.patch(id, updates));
    }

    // DELETE /users/{id} → remove user
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable Long id) {
        userService.deleteById(id);
        return ResponseEntity.noContent().build();
    }
}
```

Example 2 — cURL examples:

```bash
# GET - retrieve
curl -X GET https://api.example.com/users/42 \
     -H "Accept: application/json"

# POST - create
curl -X POST https://api.example.com/users \
     -H "Content-Type: application/json" \
     -d '{"name":"Alice","email":"alice@example.com"}'

# PUT - full replace
curl -X PUT https://api.example.com/users/42 \
     -H "Content-Type: application/json" \
     -d '{"id":42,"name":"Alice","email":"new@example.com"}'

# PATCH - partial update
curl -X PATCH https://api.example.com/users/42 \
     -H "Content-Type: application/json" \
     -d '{"email":"updated@example.com"}'

# DELETE - remove
curl -X DELETE https://api.example.com/users/42
```

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| PATCH is always idempotent | PATCH is idempotent only if the update is absolute (set age=31). Relative patches (increment age by 1) are not idempotent. RFC 5789 explicitly states PATCH need not be idempotent. |
| DELETE must return 404 if already deleted | By idempotent design, DELETE /users/42 can return 404 on second call since the result (user 42 doesn't exist) is the same. Both 204 and 404 are acceptable. |
| POST is always for creating resources | POST is for any non-idempotent action: creating a resource, triggering a process (POST /invoices/42/send), form submission. |
| GET requests cannot have a body | HTTP/1.1 technically allows it but it has undefined semantics. Avoid GET with body — use query parameters instead. |
| PUT and PATCH are interchangeable | PUT replaces the entire representation (omitted fields are deleted/nulled). PATCH applies only specified changes. Mix-up causes unintended data loss. |
| HTTP methods are case-insensitive | HTTP methods are case-sensitive and must be uppercase: GET not get or Get. |

### 🔥 Pitfalls in Production

**1. Using GET for State-Changing Operations**

```bash
# BAD: GET with side effects — caches, bots, link prefetchers trigger it
GET /users/42/delete  # accidentally deletes user via browser prefetch!
GET /emails/send?to=all # Googlebot indexes this and sends emails!

# GOOD: Use appropriate method
DELETE /users/42          # explicit semantic
POST /emails/campaigns/1/send # action endpoint
```

**2. POST Instead of PUT for Idempotent Updates**

```bash
# BAD: POST for idempotent update — double-click creates duplicates
POST /orders/42/confirm  # if retried: two confirmations!

# GOOD: PUT for idempotent state change
PUT /orders/42/status
  body: {"status": "confirmed"}
# Retrying is safe — result always same
```

**3. Returning 200 Instead of 201 for POST**

```java
// BAD: POST returns 200 with body but no Location header
@PostMapping
public User create(@RequestBody User user) {
    return userService.save(user); // returns 200 by default
}

// GOOD: 201 Created with Location header
@PostMapping
public ResponseEntity<User> create(@RequestBody User user) {
    User saved = userService.save(user);
    return ResponseEntity
        .created(URI.create("/users/" + saved.getId()))
        .body(saved);
}
```

### 🔗 Related Keywords

- `HTTP/1.1` — defines the protocol within which methods are transmitted.
- `Idempotency in HTTP` — the property of PUT/DELETE/GET methods that clients rely on for safe retry.
- `RESTful Constraints` — the constraints that define how methods should map to resources.
- `HTTP Status Codes` — the response status codes that indicate the result of a method call.
- `API Design Best Practices` — conventions for which method to use for different resource operations.

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ GET    │ Read resource. Safe + Idempotent. Cached.       │
│ POST   │ Create/action. NOT safe/idempotent.             │
│ PUT    │ Replace entire resource. Idempotent.            │
│ PATCH  │ Partial update. Not always idempotent.          │
│ DELETE │ Remove resource. Idempotent.                    │
├──────────────────────────────────────────────────────────┤
│ ONE-LINER │ "Method = the verb; URL = the noun;         │
│            combine them for a uniform interface."       │
├──────────────────────────────────────────────────────────┤
│ NEXT EXPLORE │ HTTP Status Codes → REST → RESTful        │
│              │ Constraints → Idempotency in HTTP         │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A mobile payment app sends `POST /payments` to charge a customer. The network drops the connection after the payment is processed on the server side but before the 201 response reaches the client. The client retries. What specific mechanism would you implement to make this POST effectively idempotent, what HTTP header is the standard way to do this, and how does the server use this header to distinguish a retry from a new request?

**Q2.** The HTTP specification says GET must be "safe" (no side effects). However, every GET request on a real web application does have side effects: access logs are written, analytics counters increment, cache miss penalties are incurred. Explain the distinction between "safe" in the HTTP specification sense and "side-effect free" in the strict computer science sense, and why this distinction is important for how browsers, CDNs, and web crawlers treat GET requests.

