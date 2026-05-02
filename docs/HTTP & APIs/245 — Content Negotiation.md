---
layout: default
title: "Content Negotiation"
parent: "HTTP & APIs"
nav_order: 245
permalink: /http-apis/content-negotiation/
number: "0245"
category: HTTP & APIs
difficulty: ★★☆
depends_on: HTTP, MIME Types, REST
used_by: REST APIs, Web Applications, Multi-format APIs
related: REST, HTTP Headers, OpenAPI/Swagger, API Versioning
tags:
  - api
  - http
  - content-negotiation
  - mime-types
  - rest
  - intermediate
---

# 245 — Content Negotiation

⚡ TL;DR — Content negotiation is the HTTP mechanism by which a client and server agree on the format of the response; the client declares preferences via the `Accept` header (e.g., `application/json` vs `application/xml`) and the server responds in the best-matched format or returns `406 Not Acceptable` — enabling a single endpoint to serve JSON, XML, CSV, or other formats based on what the client requests.

┌──────────────────────────────────────────────────────────────────────────┐
│ #245 │ Category: HTTP & APIs │ Difficulty: ★★☆ │
├──────────────┼────────────────────────────────────┼──────────────────────┤
│ Depends on: │ HTTP, MIME Types, REST │ │
│ Used by: │ REST APIs, Web Apps, Multi-format │ │
│ Related: │ REST, HTTP Headers, OpenAPI, │ │
│ │ API Versioning │ │
└──────────────────────────────────────────────────────────────────────────┘

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You build a REST API that returns JSON. Now a legacy enterprise customer needs XML.
A mobile team wants a compact binary format (Protocol Buffers). A data team wants CSV
for direct spreadsheet import. Without content negotiation: you create separate endpoints
for each format (`/api/users.json`, `/api/users.xml`, `/api/users.csv`) — the same
resource, multiplied by the number of formats needed. Every new format means new endpoints,
duplicated routing, and competing versioning strategies.

**THE INVENTION MOMENT:**
HTTP content negotiation (RFC 7231) was designed as part of HTTP/1.1 to solve the
"one resource, multiple representations" problem elegantly. The resource (`/api/users`)
is conceptually singular — what varies is the REPRESENTATION (JSON, XML, CSV). The client
declares format preferences in the `Accept` header. The server picks the best match
and responds with it, indicating the actual format via `Content-Type`. One endpoint,
multiple formats, clean separation of concerns.

---

### 📘 Textbook Definition

**Content Negotiation** is the HTTP mechanism (RFC 7231) that allows a client and server
to agree on the format (MIME type), language (`Accept-Language`), encoding
(`Accept-Encoding`), and character set of an HTTP response. The primary mechanism is
**proactive (server-driven) negotiation**: the client sends `Accept`, `Accept-Language`,
`Accept-Encoding` headers expressing preferences; the server selects the best-matching
representation and responds with it, setting `Content-Type`, `Content-Language`, and
`Content-Encoding` accordingly. If no acceptable representation is available, the server
returns `406 Not Acceptable`. The `Vary` header declares which request headers affected
the response (enabling correct caching). **Reactive negotiation** is an alternative:
server returns `300 Multiple Choices` with a list of available representations; client
selects. In practice, proactive negotiation is standard for REST APIs.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Content negotiation is client saying "I prefer JSON but can accept XML" and the server
responding in the best format it supports — all through standard HTTP headers on the same endpoint.

**One analogy:**

> Content negotiation is like ordering at a multilingual restaurant.
> You tell the waiter (server) your language preferences: "French preferred,
> English acceptable, no Italian." The waiter brings the same dish (resource) but
> the menu card (representation) is in French. There's one kitchen (endpoint),
> one dish (resource), but multiple presentation options (formats).

**One insight:**
The key insight is separating RESOURCE IDENTITY (the URL: `/api/users`) from
REPRESENTATION (the format: JSON, XML, CSV). REST purists argue the URL should
identify the resource only, not the format — content negotiation is the proper
REST way to select representation. This keeps URLs clean and makes the same endpoint
serve multiple consumers.

---

### 🔩 First Principles Explanation

**ACCEPT HEADER SYNTAX — Q-VALUES:**

```
Accept header anatomy:
  Accept: application/json;q=1.0, application/xml;q=0.8, */*;q=0.1

  q=<value>: quality factor, 0.0 (refuse) to 1.0 (prefer)
  Default if omitted: q=1.0
  */*: wildcard — accept anything with lowest preference

  Parsed:
  1st choice: application/json (q=1.0)
  2nd choice: application/xml (q=0.8)
  Last resort: any format (q=0.1)

More examples:
  Accept: application/json                          → want only JSON
  Accept: */*                                       → accept anything (browser default)
  Accept: text/html,application/xhtml+xml,*/*;q=0.8 → browser requesting a page
  Accept: application/vnd.company.v2+json          → versioned media type
```

**CONTENT TYPE RESPONSE:**

```
Server responses:
  GET /api/users + Accept: application/json
  → 200 OK
     Content-Type: application/json; charset=utf-8
     Vary: Accept
     Body: [{"id":1,"name":"Alice"},...]

  GET /api/users + Accept: application/xml
  → 200 OK
     Content-Type: application/xml
     Vary: Accept
     Body: <users><user><id>1</id><name>Alice</name></user></users>

  GET /api/users + Accept: text/csv
  → (if not supported) 406 Not Acceptable
     Body: (list of supported types)

WHY Vary: Accept?
  CDN/proxy caches the response.
  Without Vary: Accept, a proxy might cache the JSON response and return it
  to a client requesting XML (same URL!).
  With Vary: Accept: "this response varies by the Accept header —
  cache separately per Accept value."
```

**CONTENT NEGOTIATION FOR API VERSIONING:**

```
Vendor media types combine content type + version:
  Accept: application/vnd.company.api+json;version=2
  OR:
  Accept: application/vnd.company.apiv2+json

This allows:
  Same URL: /api/users
  v1 response: { "name": "Alice Smith" }          (flat name)
  v2 response: { "first": "Alice", "last": "Smith" } (structured name)

  Pros: REST-pure versioning via content type
  Cons: awkward for developers, not visible in URL, harder to route in gateways
  Industry: GitHub uses X-GitHub-Api-Version header instead (custom header, not Accept)
  Most APIs: use URI versioning (/v1/, /v2/) in practice over media type versioning
```

---

### 🧪 Thought Experiment

**SCENARIO:** API serving both browsers and programmatic clients.

```
BROWSER REQUEST (no Accept header customization):
  GET /api/users
  Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8

  Server options:
  a. Detect browser (check Accept includes text/html with higher priority)
     → respond with HTML (redirect to UI, or return rendered HTML table)
  b. Return JSON anyway (application/json) — browser shows raw JSON
  c. API: ignore browser behavior, always return JSON (common for REST APIs)

MOBILE APP (explicit):
  GET /api/users
  Accept: application/json

  → Clean, unambiguous: returns JSON

ENTERPRISE INTEGRATION (needs XML):
  GET /api/users
  Accept: application/xml

  → Returns XML (if server supports it)
  → 406 if server only supports JSON

CSV EXPORT CLIENT:
  GET /api/users
  Accept: text/csv, application/json;q=0.5

  → Server: supports CSV → 200 CSV
  → Server: only supports JSON → returns JSON (client will accept with lower preference)
```

---

### 🧠 Mental Model / Analogy

> Content negotiation is like asking Google Maps for directions.
> You say: "I prefer walking, but will accept cycling, and if those aren't possible,
> car is OK (lowest preference)." Google Maps (server) checks which modes are available
> for that route and gives you the best match for your preferences.
> The destination (URL/resource) is the same — the format (walking/cycling/driving
> route = JSON/XML/CSV) varies based on your preference declaration.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Content negotiation means the client tells the API server "I prefer JSON, but I can
handle XML." The server then picks the best format it can provide that matches what
the client wants — all through HTTP headers, no URL changes needed.

**Level 2 — How to use it (junior developer):**
In Spring MVC: use `produces` in `@RequestMapping`. Multiple formats: add Jackson
XML dependency + configure `WebMvcConfigurer`. Client sends `Accept: application/json`
or `Accept: application/xml`. Spring auto-selects the right `HttpMessageConverter`.
Always set `Vary: Accept` in responses to ensure correct cache behavior.

**Level 3 — How it works (mid-level engineer):**
Spring MVC content negotiation order: (1) path extension (deprecated in Spring 5.3),
(2) query parameter (`?format=json`), (3) Accept header. For REST APIs: disable path
extension and query param — use only Accept header. Configure `ContentNegotiationConfigurer`
to set `favorParameter(false)` and `ignoreAcceptHeader(false)`. If endpoint has
`produces = {"application/json", "application/xml"}`, Spring's `HttpMessageConverter`
chain is invoked — Jackson for JSON, Jackson Dataformat XML for XML, or custom
converters. The `406 Not Acceptable` is returned automatically when no converter can
fulfill the Accept header.

**Level 4 — Why it was designed this way (senior/staff):**
Content negotiation is one of HTTP's most academically correct features — and one of
the most underused in practice. Roy Fielding's REST dissertation specifically mentions
conneg as a REST constraint: resources should have multiple representations available.
In practice, most APIs serve only JSON (simplicity wins over purity). The real-world
value emerges in: multi-protocol APIs serving legacy XML clients and modern JSON clients
on the same endpoint, bi-directional content type handling (request body type via
`Content-Type`, response type via `Accept`), and format-based versioning (Accept:
application/vnd.api+json;version=2). The `Vary` header is often forgotten: a missing
`Vary: Accept` causes CDN caches to serve the wrong format to a different client for
the same URL — a subtle but impactful caching bug.

---

### ⚙️ How It Works (Mechanism)

```
CONTENT NEGOTIATION IN SPRING MVC:

Request:
  GET /api/users
  Accept: application/xml

Spring MVC processing:
  1. HandlerMapping: routes to UserController.getUsers()
  2. Method has @RequestMapping(produces = {"application/json", "application/xml"})
  3. ContentNegotiationStrategy:
     Parse Accept header: [application/xml;q=1.0]
     Compare with produces: ["application/json", "application/xml"]
     Best match: application/xml ✓
  4. Return value processing:
     HttpMessageConverter chain: MappingJackson2HttpMessageConverter → skip (JSON only)
     MappingJackson2XmlHttpMessageConverter → supports XML → SELECTED
  5. Jackson XML serializes User list → XML response
  6. Add Content-Type: application/xml; charset=utf-8
     Add Vary: Accept

  If Accept: text/csv (not in produces):
     No matching converter → 406 Not Acceptable
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
Multi-format REST endpoint:

  @GetMapping(value = "/api/users",
              produces = { APPLICATION_JSON_VALUE,
                           APPLICATION_XML_VALUE,
                           "text/csv" })
  public ResponseEntity<UserList> getUsers(
          @RequestHeader(value = "Accept", defaultValue = APPLICATION_JSON_VALUE) String accept) {
      List<User> users = userService.findAll();
      return ResponseEntity.ok()
          .header("Vary", "Accept")
          .body(new UserList(users));
  }

Variations by Accept header:
  Accept: application/json → [{...}, {...}]
  Accept: application/xml  → <userList><user>...</user></userList>
  Accept: text/csv         → id,name,email\n1,Alice,alice@example.com
  Accept: text/plain       → 406 Not Acceptable
```

---

### 💻 Code Example

```java
// Spring MVC — Content Negotiation configuration
@Configuration
public class WebConfig implements WebMvcConfigurer {

    @Override
    public void configureContentNegotiation(ContentNegotiationConfigurer configurer) {
        configurer
            .favorPathExtension(false)      // Deprecated; don't use /users.json
            .favorParameter(false)          // Don't use ?format=json (use Accept header)
            .ignoreAcceptHeader(false)      // Use Accept header (default)
            .defaultContentType(MediaType.APPLICATION_JSON);  // fallback if no Accept
    }

    @Override
    public void extendMessageConverters(List<HttpMessageConverter<?>> converters) {
        // Jackson JSON: included by default in Spring Boot
        // Jackson XML: add dependency + it auto-registers
        // Custom CSV converter:
        converters.add(new CsvHttpMessageConverter());
    }
}

// Controller supporting multiple formats
@RestController
@RequestMapping("/api/v1/users")
public class UserController {

    @GetMapping(produces = {
        MediaType.APPLICATION_JSON_VALUE,
        MediaType.APPLICATION_XML_VALUE,
        "text/csv"
    })
    public ResponseEntity<UserList> getUsers(HttpServletResponse response) {
        response.setHeader("Vary", "Accept");  // critical for CDN caching
        List<User> users = userService.findAll();
        return ResponseEntity.ok(new UserList(users));
    }
}

// Custom CSV message converter
public class CsvHttpMessageConverter extends AbstractHttpMessageConverter<UserList> {

    public CsvHttpMessageConverter() {
        super(MediaType.parseMediaType("text/csv"));
    }

    @Override
    protected void writeInternal(UserList users, HttpOutputMessage output)
            throws IOException {
        output.getHeaders().setContentType(MediaType.parseMediaType("text/csv"));
        PrintWriter writer = new PrintWriter(output.getBody());
        writer.println("id,name,email");
        users.getUsers().forEach(u ->
            writer.printf("%d,%s,%s%n", u.getId(), u.getName(), u.getEmail()));
        writer.flush();
    }
}
```

---

### ⚖️ Comparison Table

| Approach                               | URL Cleanliness | REST-Pure | CDN Caching     | Versioning      |
| -------------------------------------- | --------------- | --------- | --------------- | --------------- |
| **Accept Header (conneg)**             | ✅ Clean        | ✅        | Needs Vary      | Via vendor MIME |
| **URL extension** (`/users.json`)      | ❌ Polluted     | ❌        | Simple          | By path         |
| **Query param** (`?format=json`)       | Polluted        | ❌        | Varies by param | By param        |
| **Separate endpoints** (`/json/users`) | ❌ Duplicated   | ❌        | Simple          | By path         |

---

### ⚠️ Common Misconceptions

| Misconception                                            | Reality                                                                                                                                                                            |
| -------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Content negotiation is only about JSON vs XML            | Also covers: language (Accept-Language), encoding (Accept-Encoding: gzip), charset, and can be used for API versioning via vendor MIME types                                       |
| Missing Vary header is harmless                          | Caches (CDN, proxies) may serve a JSON response to XML-requesting clients on the same URL. Always set `Vary: Accept` when there are multiple representations                       |
| 406 Not Acceptable means the server rejected the request | It means the server can't provide any representation matching the client's Accept preferences. Solution: client should use `*/*` as fallback q-value or use a supported media type |
| Content-Type and Accept are the same                     | Content-Type: what format THIS request body is in. Accept: what format I want the RESPONSE in. Different directions                                                                |

---

### 🚨 Failure Modes & Diagnosis

**CDN Serving Wrong Format**

Symptom:
Some clients receive XML responses even when sending `Accept: application/json`.
Reproducible on first request to a URL after cache expiry.

Root Cause:
`Vary` header missing from responses. CDN caches the first response (XML from a
legacy client) and serves it to all subsequent requests for that URL, regardless
of Accept header.

Diagnostic:

```bash
# Check if Vary: Accept is in responses:
curl -I https://api.company.com/v1/users \
  -H "Accept: application/json"
# Look for: Vary header in response. If absent: CDN caching bug

# Test with CDN bypass (Cache-Control: no-cache):
curl -H "Accept: application/json" \
     -H "Cache-Control: no-cache" \
     https://api.company.com/v1/users
# If this works but regular request returns wrong format: CDN cache issue

# Fix in Spring:
response.setHeader("Vary", "Accept");
# Or globally via SecurityHeaders filter / WebMvcConfigurer
```

---

### 🔗 Related Keywords

- `REST` — the architectural style that promotes content negotiation for representations
- `MIME Types` — the format identifiers used in Content-Type and Accept headers
- `API Versioning` — content negotiation via vendor MIME types is one versioning strategy
- `HTTP Caching` — the `Vary` header interaction with CDN and proxy caches

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Client declares format preference via    │
│              │ Accept header; server responds in best   │
│              │ matching format (or 406)                 │
├──────────────┼───────────────────────────────────────────┤
│ ACCEPT       │ Accept: application/json;q=1.0,          │
│ SYNTAX       │           application/xml;q=0.8, */*;q=0.1│
├──────────────┼───────────────────────────────────────────┤
│ KEY HEADERS  │ Request: Accept                          │
│              │ Response: Content-Type + Vary: Accept    │
├──────────────┼───────────────────────────────────────────┤
│ CRITICAL     │ Always set Vary: Accept when serving    │
│ REMEMBER     │ multiple formats (for CDN correctness)   │
├──────────────┼───────────────────────────────────────────┤
│ 406          │ No matching representation available     │
│              │ → return 406 Not Acceptable              │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Same URL, best-matched representation" │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ REST → API Versioning → HTTP Caching     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q.** A public REST API currently returns only JSON. A major enterprise customer requires XML for their legacy integration. Their contract requires this within 30 days. Three junior developers propose different approaches: (A) add separate `/xml/` URL prefix routes, (B) add `?format=xml` query parameter support, (C) implement proper `Accept` header content negotiation. Your staff engineer advises (C). However, your API Gateway doesn't support Vary-aware caching. Walk through the tradeoffs, identify the actual technical risks with each approach given the CDN constraint, and make a recommendation with justification.
