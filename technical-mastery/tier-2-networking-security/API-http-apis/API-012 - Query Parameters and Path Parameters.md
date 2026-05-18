---
id: API-012
title: "Query Parameters and Path Parameters"
category: "HTTP & APIs"
tier: tier-2-networking-security
folder: API-http-apis
difficulty: ★☆☆
depends_on: API-009, API-007
used_by: API-015, API-019, API-027
related: API-008, API-013, API-026
tags:
  - http
  - rest
  - url
  - routing
  - foundational
status: complete
version: 4
layout: default
parent: "HTTP & APIs"
grand_parent: "Technical Mastery"
nav_order: 12
permalink: /technical-mastery/api/query-parameters-and-path-parameters/
---

⚡ TL;DR - Path parameters (`/users/{id}`) identify which
resource you are acting on; query parameters (`?status=active`)
filter, sort, or paginate that resource - understanding the
distinction is the foundation of clean REST API design.

---

| #012 | Category: HTTP & APIs | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | URL and URI Structure, HTTP Methods | |
| **Used by:** | API Endpoint Design, Pagination Patterns, RESTful Design | |
| **Related:** | HTTP Status Codes, JSON Format, Request Validation | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
If every API used only POST with all parameters in the body,
URLs would all be the same (e.g., `/api`). There would be
no way to share a URL that links to a specific resource.
Browser history would not show which resource was accessed.
CDN caching would be impossible (all POST to same URL).
Load balancers could not route specific resources to
specific servers without parsing the body. API documentation
would not be able to show a simple "make a GET request to
this URL" example.

**THE BREAKING POINT:**
URL-based resource addressing requires a way to embed
resource identity into the URL and a way to add optional
filters without changing the resource address. These are
different concerns: "which user" vs "which subset of that
user's data." Embedding both in the URL path is valid but
makes URLs ambiguous. Embedding both in query parameters
makes resource identity non-canonical.

**THE INVENTION MOMENT:**
REST's resource-oriented design established the pattern:
path parameters for resource identity (the noun), HTTP
method for the operation (the verb), query parameters for
optional modifiers (the adjectives). This separation creates
a clean URL hierarchy where `/users/42` always means "user
42" regardless of what query parameters follow.

**EVOLUTION:**
Early CGI scripts used only query parameters (`?action=view&id=42`).
Rails (2004) popularized path parameters for resource IDs
(`/users/:id`). REST evangelism (2005+) established the
path-for-identity, query-for-filter convention. Modern
frameworks (Express, Spring MVC, FastAPI) implement both
with declarative route annotations.

---

### 📘 Textbook Definition

A path parameter is a variable segment embedded in the URL
path, typically enclosed in curly braces in route definitions
(`/users/{id}`), where the value in the actual URL
(`/users/42`) identifies a specific resource. A query
parameter is a key-value pair in the URL query string
(`?key=value`), separated from the path by `?` and from
each other by `&`, used for optional filtering, sorting,
pagination, and non-resource-identity parameters. The
distinction determines URL canonicality, cacheability,
and REST resource identity.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Path parameters identify the resource (`/users/42`);
query parameters modify how you interact with it
(`?sort=name&page=2`).

**One analogy:**
> Think of a library catalog system. The call number
> (path parameter) tells you exactly which shelf and
> which book: `/library/shelf-5/book-42`. The search
> filters (query parameters) tell the librarian how to
> present the results: `?language=english&available=true`.
> The call number uniquely identifies one specific book.
> The filters narrow down which books from a collection
> you want. You would never encode "available=true" as
> part of a book's permanent call number - it changes
> daily. And you would never look up a specific book by
> filter alone without knowing its call number.

**One insight:**
The key test: "Is this value part of the resource's
identity?" If yes, path parameter. If no (it is a filter,
sort order, page number, or option), query parameter.
The resource `/users/42` has the same identity regardless
of `?include=orders`. But `/users/alice` and `/users/bob`
are different resources.

---

### 🔩 First Principles Explanation

**PATH PARAMETER:**

```
Route definition: GET /users/{user_id}/orders/{order_id}
Actual URL:       GET /users/42/orders/ord_789

user_id = 42
order_id = ord_789
```

**Characteristics:**
- Required: a path with a missing parameter is a different URL
  (usually 404)
- Identifies a specific resource or sub-resource
- Part of the canonical URL - the same resource always has
  the same path
- Cached by CDN as part of the URL
- Typically a UUID, integer ID, or slug

**QUERY PARAMETER:**

```
URL: GET /users?status=active&sort=name&page=2&limit=20

status = active
sort   = name
page   = 2
limit  = 20
```

**Characteristics:**
- Optional: resource still exists without the parameter
- Filters, sorts, paginates, or modifies the response
- Does not change which resource is being addressed
- Multiple values: `?tag=a&tag=b` or `?tags=a,b`
- Can be repeated: `?id=1&id=2&id=3` for bulk operations

**DECISION RULE:**

```
Is this value part of the resource's unique identity?
  YES → path parameter:  /resources/{id}
  NO  → query parameter: /resources?filter=value

Is this value required to identify the resource at all?
  YES → path parameter
  NO  → query parameter (optional modifier)

Is the URL canonical (should it be bookmarkable/shareable)?
  YES → path parameters create stable canonical URLs
  Query params can change without changing the resource
```

---

### 🧪 Thought Experiment

**SETUP:**
You are designing an API for a blog. A post has a URL.
You want to support filtering by status (published, draft)
and getting a single post by its slug.

**TWO OPTIONS:**
Option A: `/posts/{slug}` for single post, `/posts?status=published`
for list.
Option B: `/posts?slug=my-post-title` for single post,
`/posts?status=published` for list.

**WHAT HAPPENS WITH OPTION B (query params for ID):**
- CDN cannot cache `/posts?slug=my-post-title` separately
  from `/posts?slug=other-post` as efficiently as URL paths
- URL `https://blog.com/posts?slug=hello-world` is ugly
  and non-canonical - different query param order
  (`?slug=hello-world&` vs `&slug=hello-world`) could be
  treated as different URLs
- Social sharing shows URL with `?slug=` - less readable
- Routes cannot be typed: `/posts/:slug` gives you a
  simple pattern match

**WHAT HAPPENS WITH OPTION A (path params for ID):**
- `/posts/hello-world` is canonical, bookmarkable, human-readable
- CDN caches efficiently by URL path
- `/posts?status=published` is clearly a filtered collection
- Each post has a unique, stable URL independent of filters

**THE INSIGHT:**
Path parameters create canonical, bookmarkable resource
addresses. Query parameters create filtered views.
Mixing them (using query params for identity) creates
non-canonical URLs that are harder to cache, share, and reason about.

---

### 🧠 Mental Model / Analogy

> Path parameters are the address of a house. Query parameters
> are the instructions for when you arrive. "123 Main Street,
> Apt 4B" is the canonical address - it identifies one specific
> place. "Enter from the back door, skip the lobby" are
> instructions that modify how you interact with that address.
> The address does not change based on which door you use.
> The door you use does not change the address.

Mapping:
- "House address" → path parameter (`/users/42`)
- "Apt 4B" → nested path parameter (`/users/42/orders`)
- "Enter from the back door" → query parameter (`?view=summary`)
- "Instructions change" → different query params, same resource
- "Different address" → different path parameter value

Where this analogy breaks down: REST APIs sometimes use
both paths AND query params together meaningfully. The
analogy suggests they are completely independent, but in
practice, `GET /users/42?include=orders` is a common
pattern combining both.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
In a URL like `/users/42?status=active`, the `42` is part
of the path (identifying which user) and `status=active`
is a filter (limiting which results come back). Path
tells you which thing. Query tells you how to filter or sort it.

**Level 2 - How to use it (junior developer):**
Put the resource identifier in the path. Use `/users/{id}`.
Put optional filters and options in the query string.
`?page=2` for pagination. `?sort=name` for sorting.
`?include=orders` for related resources. Required parameters
that identify a resource go in the path. Optional parameters
that modify the response go in the query.

**Level 3 - How it works (mid-level engineer):**
Route matching reads path parameters from URL segments.
Express: `app.get('/users/:id', ...)` → `req.params.id`.
Spring: `@PathVariable String id`. FastAPI: `def get(id: int):`.
Query parameters are parsed from the URL query string.
Express: `req.query.status`. Spring: `@RequestParam`.
FastAPI: `def list(status: str = None):`. Frameworks
handle URL decoding of both automatically.

**Level 4 - Why it was designed this way (senior/staff):**
REST's uniform interface constraint requires resources
to be addressable by a canonical identifier. The path
provides that canonical address - `/users/42` is always
user 42. Query parameters do not affect resource identity
under REST semantics - the same resource at `/users/42`
with different query params (`?format=json` vs `?format=xml`)
is still the same resource being represented differently.
CDN caching models treat path + method as the primary
cache key and query params as secondary (configurable).
This is why query parameters for resource identity (SOAP
style: `/api?action=getUser&id=42`) breaks CDN cache
efficiency - the "same resource" has multiple URL forms.

**Level 5 - Mastery (distinguished engineer):**
The path-vs-query distinction has non-obvious interactions
with HTTP caching at scale. CDNs can be configured to
normalize (sort, strip) query parameters for cache key
purposes. A CDN configured to strip `?utm_source=...`
parameters will serve the same cached response regardless
of marketing campaign source - useful for analytics params
that do not affect content. The dangerous version: if a
CDN incorrectly strips a query param that DOES affect the
response (e.g., `?format=json` vs `?format=csv`), users
get the wrong format from cache. The rule: path parameters
are always part of the cache key; query parameter inclusion
in the cache key is configurable and must be intentionally
designed for each API.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│        Path vs Query - URL Component Breakdown       │
├──────────────────────────────────────────────────────┤
│                                                      │
│  GET /v1/users/42/orders?status=pending&page=2       │
│                                                      │
│  Route template: /v1/users/{user_id}/orders          │
│  Path params:    user_id = "42"                      │
│  Query params:   status  = "pending"                 │
│                  page    = "2"                       │
│                                                      │
│  Framework routing:                                  │
│  1. Match URL path against route templates           │
│  2. Extract path variable values from matching       │
│     segments                                         │
│  3. Parse query string into key-value map            │
│  4. Inject both into request handler                 │
│                                                      │
└──────────────────────────────────────────────────────┘
```

```mermaid
flowchart TD
    URL["GET /users/42/orders?status=pending&page=2"]
    URL --> PATH[Path: /users/42/orders]
    URL --> QUERY[Query: status=pending, page=2]
    PATH --> ROUTE{Route match<br/>/users/{id}/orders}
    ROUTE --> PP[user_id = 42]
    QUERY --> QP1[status = pending]
    QUERY --> QP2[page = 2]
    PP --> DB[Query DB for user 42 orders]
    QP1 --> FILTER[Filter: status = pending]
    QP2 --> PAGE[Offset: page 2]
    DB --> FILTER --> PAGE --> RESP[Response]
```

**Multi-value query parameters:**

```
# Comma-separated (common but non-standard):
GET /orders?status=pending,processing,shipped
status = ["pending", "processing", "shipped"]

# Repeated key (RFC 3986 compliant):
GET /orders?status=pending&status=processing
status = ["pending", "processing"]

# Array notation (PHP/form convention):
GET /orders?status[]=pending&status[]=processing
Frameworks handle differently - specify your convention
```

---

### 🔄 The Complete Picture - End-to-End Flow

**Nested resources with path + query:**

```
Collection:    GET /users
               → all users (default page 1)

Filtered:      GET /users?role=admin&active=true
               → users filtered by role and status

Resource:      GET /users/42
               → user with ID 42

Sub-resource:  GET /users/42/orders
               → all orders for user 42

Filtered sub:  GET /users/42/orders?status=pending
               → pending orders for user 42

Nested:        GET /users/42/orders/ord_789
               → specific order for user 42
```

**URL design antipatterns vs correct:**

```
BAD:  GET /getUser?id=42        (verb in path, ID in query)
GOOD: GET /users/42             (noun in path, ID in path)

BAD:  GET /users/active         (state in path like an ID)
GOOD: GET /users?status=active  (state in query filter)

BAD:  GET /users/42/sort/name   (sort in path)
GOOD: GET /users?sort=name      (sort in query)

BAD:  GET /users?user_id=42     (ID in query)
GOOD: GET /users/42             (ID in path)
```

---

### 💻 Code Example

**Example 1 - Path and query in Express.js**

```javascript
const express = require("express");
const app = express();

// Path parameter: identifies the specific user
// Query parameters: filter the user's orders
app.get(
  "/users/:userId/orders",
  async (req, res) => {
    const userId = req.params.userId;  // path param

    // Query params with defaults and validation
    const status  = req.query.status || "all";
    const page    = parseInt(req.query.page)  || 1;
    const limit   = parseInt(req.query.limit) || 20;
    const sortBy  = req.query.sort || "created_at";

    // Validate path param type
    if (!/^\d+$/.test(userId)) {
      return res.status(400).json({
        error: "user_id must be an integer"
      });
    }

    const orders = await db.orders.findByUser({
      userId: parseInt(userId),
      status,
      offset: (page - 1) * limit,
      limit,
      sortBy
    });

    res.json({ data: orders, page, limit });
  }
);
```

---

**Example 2 - Path and query in FastAPI (Python)**

```python
from fastapi import FastAPI, Query, Path
from typing import Optional, List

app = FastAPI()

@app.get("/users/{user_id}/orders")
async def list_user_orders(
    user_id: int = Path(
        ...,  # ... = required
        gt=0,  # must be > 0
        description="The user's numeric ID"
    ),
    status: Optional[str] = Query(
        None,
        regex="^(pending|processing|shipped|all)$"
    ),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sort: str = Query("created_at")
):
    # user_id is validated as int > 0 automatically
    # status regex validated by FastAPI
    orders = await db.orders.find(
        user_id=user_id,
        status=status,
        offset=(page - 1) * limit,
        limit=limit,
        sort=sort
    )
    return {"data": orders, "page": page, "limit": limit}
```

---

**Example 3 - BAD: Query param injection**

```python
# BAD: query param directly in SQL - SQL injection risk

@app.route("/users")
def list_users():
    sort_by = request.args.get("sort", "id")

    # DANGER: user controls sort column name
    # ?sort=id; DROP TABLE users --
    sql = f"SELECT * FROM users ORDER BY {sort_by}"
    results = db.execute(sql)  # SQL injection!
    return jsonify(results)

# GOOD: validate against allowlist
ALLOWED_SORT_FIELDS = {"id", "name", "email", "created_at"}

@app.route("/users")
def list_users():
    sort_by = request.args.get("sort", "id")

    if sort_by not in ALLOWED_SORT_FIELDS:
        return jsonify({
            "error": f"sort must be one of: "
                     f"{', '.join(ALLOWED_SORT_FIELDS)}"
        }), 400

    # Safe: sort_by can only be a known column name
    users = db.users.find_all(sort_by=sort_by)
    return jsonify(users)
```

---

### ⚖️ Comparison Table

| Criterion | Path Parameter | Query Parameter |
|:---|:---|:---|
| **Purpose** | Identify a specific resource | Filter, sort, paginate a resource |
| **Required?** | Yes (missing = different URL or 404) | No (has defaults or is optional) |
| **Canonical?** | Yes - part of resource's stable identity | No - same resource, different views |
| **CDN caching** | Always part of cache key | May or may not be in cache key |
| **Bookmarkable?** | Yes - permanent resource address | Depends on whether it is meaningful |
| **URL encoding** | Full percent-encoding needed | Full percent-encoding needed |
| **Typical content** | ID, UUID, slug, version | Filters, sort, page, include, format |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| Query params are less secure than path params | Both appear in server logs and Referer headers; neither is more secure than the other for sensitive values |
| Path params must be integers | Path params can be any string - UUIDs, slugs, version strings. `/users/alice`, `/users/u_abc123`, `/v2/users/42` are all valid. |
| Query params can only have string values | All URL parameters arrive as strings; frameworks parse to int/float/bool based on route annotation. Validate types explicitly. |
| Missing query params cause 404 | Query params are typically optional; missing them returns the default behavior, not 404. Missing path params cause 404 (different route). |
| You can use query params instead of path params for resource identity | Technically valid but breaks CDN cache efficiency, REST semantics, and URL canonicality |

---

### 🚨 Failure Modes & Diagnosis

**SQL injection via unsanitized query parameter**

**Symptom:** Application is vulnerable to SQL injection.
Security scan reports injection in sort/filter parameters.
Data is being exfiltrated via UNION-based injection.

**Root Cause:** Query parameter value used directly in
SQL string construction without parameterization or
allowlist validation.

**Diagnostic Command / Tool:**

```bash
# Test for SQL injection in sort parameter
curl "https://api.example.com/users?sort=id;SELECT+1"

# If response is different from normal sort:
curl "https://api.example.com/users?sort=id"
# → SQL injection present
```

**Fix:** Validate against an allowlist of known column
names. Never interpolate user input into SQL strings.

---

**Path traversal via path parameter**

**Symptom:** Attacker accesses files outside the intended
directory. Server logs show paths like `/../../../etc/passwd`
in URLs.

**Root Cause:** Path parameter used to construct a file
path without sanitization. `../` sequences traverse up
the directory tree.

**Diagnostic Command / Tool:**

```bash
# Test for path traversal
curl "https://api.example.com/files/%2E%2E%2F%2E%2E%2Fetc%2Fpasswd"
# %2E%2E%2F = ../ URL-encoded
```

**Fix:**

```python
import os
from pathlib import Path

BASE_DIR = Path("/app/uploads")

@app.route("/files/<path:filename>")
def serve_file(filename):
    # Resolve full path and check it stays within base dir
    file_path = (BASE_DIR / filename).resolve()

    if not str(file_path).startswith(str(BASE_DIR)):
        # Path traversal attempt
        return jsonify({"error": "forbidden"}), 403

    if not file_path.exists():
        return jsonify({"error": "not found"}), 404

    return send_file(file_path)
```

---

**Unexpected 404 from missing optional query param**

**Symptom:** API returns 404 for requests missing a
filter parameter that was supposed to be optional.

**Root Cause:** Route definition mixes path param
syntax with query params, or query param handler raises
404 when parameter is missing instead of using default.

**Diagnostic Command / Tool:**

```bash
# Test with and without the query param
curl -v "https://api.example.com/users"
curl -v "https://api.example.com/users?status=active"
# Compare - both should return 200 (not 404)
```

**Fix:**

```python
# BAD: raising 404 for missing optional param
status = request.args.get("status")
if not status:
    return jsonify({"error": "not found"}), 404  # WRONG

# GOOD: optional params have defaults
status = request.args.get("status", "all")
# or: return all users if status not specified
users = db.users.find(
    status=status if status != "all" else None
)
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `URL and URI Structure` - the structure that contains
  both path and query components
- `HTTP Methods` - the verb that combines with path to
  define an endpoint

**Builds On This (learn these next):**
- `API Endpoint Design Basics` - how to design clean
  URL hierarchies using path and query parameters
- `Pagination Patterns` - cursor, offset, and page-based
  pagination are all query parameter patterns
- `RESTful API Design Patterns` - the full REST resource
  model that path parameters enable

**Alternatives / Comparisons:**
- `GraphQL Query Language` - uses POST body for all
  parameters; path/query distinction is irrelevant
- `gRPC and Protocol Buffers` - parameters are typed
  message fields, not URL components

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Path params identify resources; query     │
│              │ params filter, sort, and paginate them    │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ REST needs canonical, bookmarkable URLs   │
│ SOLVES       │ with optional modifiers                   │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ "Is this part of the resource's identity?"│
│              │ YES → path. NO → query.                   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Path: IDs, slugs, resource hierarchy      │
│              │ Query: filters, sort, page, format, flags │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Never put sensitive values in either      │
│              │ (both appear in logs)                     │
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ ?id= for resource identity, sort=field in │
│              │ path, user input directly in SQL ORDER BY │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Path params = canonical, bookmarkable,    │
│              │ CDN-friendly. Query = flexible, optional. │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Path = which resource. Query = how."     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ API Endpoint Design → Pagination →        │
│              │ RESTful API Design Patterns               │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Path parameters identify the specific resource being
   acted on. Query parameters modify how you view or filter
   it. The test: "Is this part of the resource's identity?"
2. Always validate path parameters (type, format, range).
   Always validate query parameters against allowlists
   when used in database queries. SQL injection via
   query params is a real, common vulnerability.
3. Query parameters appear in server logs and Referer headers
   - never put secrets, tokens, or PII in query parameters.

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Separate resource identity from resource modification.
A resource has a stable, canonical identity (the path)
and multiple possible views or transformations (query
parameters). This separation appears in every successful
addressing system: database primary keys are the stable
identity; SQL WHERE clauses are the modifiers. S3 object
keys are the stable identity; S3 URL parameters are the
modifiers (presigned URL expiry, response headers).
Conflating identity and modification creates brittle,
non-canonical addresses.

**Where else this pattern appears:**
- S3 URLs: bucket + object key (path) are the canonical
  identity; query parameters (`?X-Amz-Expires=3600`) are
  presigned URL expiry modifiers
- CSS selectors: element type + ID (stable identity) +
  class (modifier) - parallel to path + query
- SQL: table + primary key (identity) + WHERE clause (filter)

**Industry applications:**
- Stripe API: all resources have path-based IDs
  (`/charges/ch_abc`, `/customers/cus_xyz`). All
  pagination and filtering use query parameters
  (`?limit=10&starting_after=ch_xyz`). Stripe's API
  design is considered the gold standard for REST
  parameter design.

---

### 💡 The Surprising Truth

The rule "path params for identity, query params for
filters" is a REST convention, not an HTTP requirement.
HTTP itself does not distinguish between path and query
in terms of routing or semantics - both are just parts
of the URL. The convention exists entirely because of
REST architecture's resource model and practical
caching/routing reasons. A perfectly valid HTTP API
could put everything in query params (as SOAP-over-GET
did) or everything in path segments (as some hypermedia
APIs do). The convention is valuable precisely because
it is widely followed - it creates predictable, readable
APIs that developers can navigate without documentation.
When you break the convention, you lose the readability
benefit even if the API technically works.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN** Given the URL `/products/electronics?brand=Sony&sort=price&page=2`,
   identify which parts are path params, which are query
   params, and explain the REST design rationale for each.
2. **DEBUG** Given a report that `/users?sort=email` is
   returning all users in arbitrary order instead of sorted,
   trace the bug to the SQL query and identify whether it
   is a missing ORDER BY or an injection issue.
3. **DECIDE** For each API parameter - user ID, order
   status filter, response format (JSON/CSV), page number,
   API version - decide whether it should be a path or
   query parameter, with reasoning.
4. **BUILD** Implement a route handler with a path parameter
   for resource ID, query parameters for filtering and
   pagination, input validation for all parameters, and
   SQL injection prevention for any database-bound values.
5. **EXTEND** Explain how CDN cache key configuration
   interacts with query parameters, and give an example
   of a query parameter that should be excluded from the
   cache key vs one that must be included.

---

### 🎯 Interview Deep-Dive

**Q1: When would you use a path parameter vs a query
parameter? Give a concrete example of a case where
the choice matters.**

*Why they ask:* REST API design basics - tests whether
the candidate has a principled model or just guesses.

*Strong answer includes:*
- Path: resource identity - the value uniquely identifies
  which resource; missing it means a different URL
- Query: optional modifier - the resource exists without it;
  it filters, sorts, or configures the response
- Concrete example: `/users/42` vs `/users?id=42` - the
  first is the REST-idiomatic canonical URL for user 42;
  the second is non-canonical (CDN may not cache efficiently,
  not bookmarkable in the same way)
- Design signal: if you would put it in a database `WHERE`
  clause as a filter, it is likely a query param; if it
  is the primary key lookup, it is a path param

**Q2: What is the security risk of using an unsanitized
query parameter in a database query?**

*Why they ask:* SQL injection via query parameters is
extremely common - tests security awareness.

*Strong answer includes:*
- SQL injection: user controls the value that becomes
  part of a SQL statement (ORDER BY, WHERE, LIMIT, etc.)
- Example: `?sort=id; DROP TABLE users--` if interpolated
  into `ORDER BY {sort}` executes the DROP TABLE
- Allowlist validation is the fix: check that `sort` is
  in `["id", "name", "created_at"]` before using it
- Parameterized queries for WHERE clause values, allowlist
  for structural elements (column names, table names,
  sort direction - `ASC`/`DESC`)
- Sort direction: `?order=ASC` must be validated:
  `if order not in ["ASC", "DESC"]: raise error`

**Q3: A client sends `GET /users?sort=email&sort=name`.
How should your API handle multiple values for the same
query parameter?**

*Why they ask:* Multi-value query parameters are a real
design decision that frameworks handle differently.

*Strong answer includes:*
- Multiple values for the same key are valid per RFC 3986
- Framework behavior varies: `request.args.get("sort")`
  returns the first value in most frameworks; use
  `request.args.getlist("sort")` to get all values
- Design decision: decide whether to support multi-value
  sort, and document it explicitly
- If only one value is expected: validate that exactly one
  is provided, return 400 if multiple are sent
- If multi-value is supported: define semantics (sort by
  email first, then name as tiebreaker) and document it
