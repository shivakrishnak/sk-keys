---
layout: default
title: "API Versioning"
parent: "HTTP & APIs"
nav_order: 232
permalink: /http-apis/api-versioning/
number: "0232"
category: HTTP & APIs
difficulty: ★★☆
depends_on: HTTP, REST, API Design
used_by: Public APIs, Mobile Apps, Enterprise Integrations
related: API Deprecation Strategy, API Gateway, OpenAPI/Swagger, Backward Compatibility
tags:
  - api
  - versioning
  - rest
  - backward-compatibility
  - intermediate
---

# 232 — API Versioning

⚡ TL;DR — API versioning is the practice of maintaining multiple coexisting versions of an API so that existing clients continue working while new capabilities are introduced; the primary strategies are URL path versioning (/v1/), header versioning (Accept: application/vnd.api+json;version=2), and query parameter versioning (?api-version=2).

┌──────────────────────────────────────────────────────────────────────────┐
│ #232         │ Category: HTTP & APIs              │ Difficulty: ★★☆      │
├──────────────┼────────────────────────────────────┼──────────────────────┤
│ Depends on:  │ HTTP, REST, API Design             │                      │
│ Used by:     │ Public APIs, Mobile Apps, Enterprise│                     │
│ Related:     │ API Deprecation, API GW, OpenAPI,  │                      │
│              │ Backward Compatibility             │                      │
└──────────────────────────────────────────────────────────────────────────┘

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You release a REST API. 100 mobile apps integrate with it. Six months later, you
discover the response format for `/users/{id}` needs to change: the address field
must be split from a flat string to a structured object with street, city, country.
If you change the response format directly, all 100 mobile apps break immediately —
especially older versions still in the app store that users haven't updated.
Without versioning, you're forced to either freeze the API forever (preventing
improvement) or break all existing integrations on every change.

**THE INVENTION MOMENT:**
API versioning emerged from the practical reality that APIs outlive their initial
design. The insight: treat your API as a contract. Each version is a separate
contract. Introduce breaking changes in new versions while keeping old versions
running until clients migrate. This allows API evolution without forced upgrades —
a major enabler of public API ecosystems (Twitter, Google, Stripe).

---

### 📘 Textbook Definition

**API Versioning** is the practice of maintaining multiple stable, coexisting interfaces
to a service, allowing clients to specify which version of the API they intend to use.
A breaking change (removing fields, renaming endpoints, changing data types, altering
behavior) is implemented in a new version while the previous version remains available
for a defined deprecation period. Non-breaking changes (adding optional fields, adding
new endpoints, relaxing constraints) can be made to existing versions without requiring
a new version. The primary versioning strategies are: URI path versioning, HTTP header
versioning (using Accept header or custom headers), and query parameter versioning.
Each strategy offers different tradeoffs in discoverability, cacheability, and REST
purity.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
API versioning lets you change your API without breaking clients by running multiple
versions simultaneously and letting each client choose which contract it speaks.

**One analogy:**
> Versioning an API is like publishing a new edition of a textbook. Students who
> already bought the 1st edition can still use it. New students get the 2nd edition
> with corrections. Both editions exist simultaneously. You announce "1st edition
> will be unsupported after Dec 2025 — please migrate." Nobody is forced to upgrade
> overnight.

**One insight:**
The key decision is: when is a change "breaking"? A change is breaking if it
causes a client that was working to fail or produce wrong results:
- Removing a field: breaking
- Renaming a field: breaking
- Changing a field's type: breaking
- Adding a required request field: breaking
- Adding an optional response field: NON-breaking (Postel's Law: be liberal in what you accept, conservative in what you send — clients should ignore unknown fields)

---

### 🔩 First Principles Explanation

**VERSIONING STRATEGY COMPARISON:**

```
STRATEGY 1 — URI Path Versioning
  GET /v1/users/42
  GET /v2/users/42

  Pros:
  ✅ Visible in URL — easy to route in browsers, curl, logs, API Gateway
  ✅ Cacheable (different URLs = different cache entries)
  ✅ Easy to route at gateway/load balancer level
  Cons:
  ❌ "Not pure REST" (URI should identify resource, not API version)
  ❌ URL leakage into bookmarks/client code
  Industry use: Stripe, Twilio, most APIs in practice

STRATEGY 2 — HTTP Header Versioning (Accept/Custom Header)
  GET /users/42
  Accept: application/vnd.api.v2+json
  OR:
  API-Version: 2

  Pros:
  ✅ Cleaner URLs — same path, different representation
  ✅ REST-pure: URI identifies resource, header specifies representation
  Cons:
  ❌ Not visible in URL — hard to test in browser/curl without flags
  ❌ Not cacheable by default (need Vary: Accept header)
  ❌ Awkward in API Gateway routing rules
  Industry use: GitHub (X-GitHub-Api-Version), Azure (api-version: query/header)

STRATEGY 3 — Query Parameter Versioning
  GET /users/42?api-version=2
  OR:
  GET /users/42?v=2

  Pros:
  ✅ Visible in URL
  ✅ Easy to add/change in any HTTP client
  Cons:
  ❌ Pollutes query parameters (separates version from path routing concerns)
  ❌ Often omitted accidentally
  Industry use: Google APIs (v=2), Amazon (Version=2012-08-10)
```

**BREAKING VS NON-BREAKING:**

```
NON-BREAKING changes (safe in current version):
  + Add optional request field (with default)
  + Add new response fields (clients ignore unknown)
  + Add new endpoints
  + Relax constraints (widen accepted values)

BREAKING changes (require new version):
  - Remove response fields
  - Rename fields
  - Change field type (string → number)
  - Add required request fields
  - Change semantics of existing fields
  - Change status codes for existing scenarios
  - Remove endpoints
  - Tighten constraints
```

---

### 🧪 Thought Experiment

**SCENARIO:** Designing a public payment API.

```
v1 design (2020):
  POST /v1/charges
  Request: { amount: 1000, currency: "USD", card_token: "..." }
  Response: { id: "ch_123", status: "paid", amount: 1000 }

Problem discovered in 2022:
  The "status" field needs more granularity:
  v1 "paid" actually means 3 different states: authorized, captured, settled
  Also: "amount" needs to be split into amount + fee + net
  Also: "card_token" field is renamed to "payment_method_id"

Option A: Change v1 in-place:
  → Breaks all 10,000 integrations
  → Not acceptable

Option B: Create v2:
  v2: POST /v2/charges
  Request: { amount: 1000, currency: "USD", payment_method_id: "..." }
  Response: { id: "ch_123", status: "authorized|captured|settled",
              amount: 1000, fee: 30, net: 970 }
  v1 remains: maps v1 fields to v2 internally, returns v1 format
  v1 deprecation: announced "v1 EOL: Dec 31, 2024"

→ Result: existing integrations not broken
→ New integrations use v2
→ Migration timeline gives everyone 2 years
```

---

### 🧠 Mental Model / Analogy

> API versioning is version control for your interface contract, not your code.
> Your code can change entirely; your contract says "if you call me with THIS shape,
> I'll respond with THAT shape." Versioning means: "v1 contract is still honored.
> v2 contract is the new one. v1 will be retired in 12 months."
>
> It's like a rental agreement: tenants (clients) have a signed lease (API contract).
> You can't change lease terms mid-tenancy without violating the contract. You create
> a new lease template (v2) for new tenants. Existing tenants stay on v1 until their
> lease expires (deprecation deadline).

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
When an API changes in ways that break existing clients, you start a new version (v2)
and keep v1 running. Old clients use v1. New clients use v2. Eventually v1 is retired.

**Level 2 — How to use it (junior developer):**
Use URL versioning: /v1/resource, /v2/resource. It's visible, easy to route, and
browser/curl friendly. Decide what counts as breaking and write it in your API changelog.
When a breaking change is needed, create a new version. Keep v1 alive for a migration
window (6–24 months for public APIs). Announce deprecation early with sunset headers.

**Level 3 — How it works (mid-level engineer):**
In the codebase, versioning strategies: (a) route to separate controllers by version
prefix, (b) use a versioning facade with adapters for each version, (c) use content
negotiation with `@RequestMapping(produces = "application/vnd.api.v2+json")`. At the
API Gateway, route `/v1/*` and `/v2/*` to different service instances or different
route configurations. Use the `Sunset` HTTP response header (RFC 8594) and `Deprecation`
header to indicate when a version is being retired. Track per-version usage in metrics
to make deprecation decisions.

**Level 4 — Why it was designed this way (senior/staff):**
API versioning is fundamentally a backward compatibility management strategy. The
granularity of versioning (major/minor/patch, integer increments, date-based) reflects
the maturity and scale of the API. Stripe uses major integer versions (2023-09-01
date-versioned headers); Google uses major path segments (/v1/, /v2beta/). The tradeoff
is: maintaining N versions costs 2x–Nx the maintenance burden while preventing client
disruption. The optimal strategy depends on your client type: SDK-based clients (mobile
apps) need longer migration windows because app updates are user-triggered; server-side
clients can often be upgraded in hours. Modern API design practices ("additive only"
policies, using nullable optional fields, JSON Merge Patch) aim to minimize breaking
changes, reducing the frequency of major version bumps.

---

### ⚙️ How It Works (Mechanism)

```
URL VERSIONING — SERVER ROUTING EXAMPLE (Spring Boot):

GET /v1/users/42 → UserControllerV1.getUser(42) → V1UserResponse
GET /v2/users/42 → UserControllerV2.getUser(42) → V2UserResponse

SHARED SERVICE LAYER:
Both controllers call UserService.getById(42) → User domain object
V1 controller: maps User → V1UserResponse (flat address string)
V2 controller: maps User → V2UserResponse (structured address object)

DEPRECATION HEADERS (RFC 8594):
HTTP/1.1 200 OK
Deprecation: true
Sunset: Sat, 31 Dec 2025 00:00:00 GMT
Link: <https://api.example.com/v2/users>; rel="successor-version"
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
Mobile App v1.x:  → GET /api/v1/users/me
                    → V1Controller → UserService → V1Response { address: "123 Main St" }

Mobile App v2.x:  → GET /api/v2/users/me
                    → V2Controller → UserService → V2Response { address: { street: "123 Main", city: "NYC" }}

API Gateway routes:
  /api/v1/* → user-service (V1 endpoints enabled)
  /api/v2/* → user-service (V2 endpoints enabled)

Deprecation timeline:
  Year 1: v1 and v2 both active
  Year 2: v1 shows Deprecation + Sunset headers
  Year 2 EOL: v1 returns 410 Gone with migration guide URL
```

---

### 💻 Code Example

```java
// Spring Boot — URI versioning with separate controllers

// V1 API (legacy, deprecated)
@RestController
@RequestMapping("/api/v1/users")
@Deprecated
public class UserControllerV1 {

    @GetMapping("/{id}")
    public ResponseEntity<UserResponseV1> getUser(
            @PathVariable Long id, HttpServletResponse response) {
        // Add deprecation headers (RFC 8594)
        response.addHeader("Deprecation", "true");
        response.addHeader("Sunset", "Sat, 31 Dec 2025 00:00:00 GMT");
        response.addHeader("Link",
            "<https://api.example.com/api/v2/users/" + id + ">; rel=\"successor-version\"");

        User user = userService.findById(id);
        return ResponseEntity.ok(UserResponseV1.from(user)); // flat address string
    }
}

// V2 API (current)
@RestController
@RequestMapping("/api/v2/users")
public class UserControllerV2 {

    @GetMapping("/{id}")
    public ResponseEntity<UserResponseV2> getUser(@PathVariable Long id) {
        User user = userService.findById(id);
        return ResponseEntity.ok(UserResponseV2.from(user)); // structured address
    }
}

// V1 and V2 response models
record UserResponseV1(Long id, String name, String address) {
    static UserResponseV1 from(User u) {
        return new UserResponseV1(u.getId(), u.getName(),
            u.getStreet() + " " + u.getCity()); // flatten to string for v1
    }
}

record UserResponseV2(Long id, String name, AddressV2 address) {
    record AddressV2(String street, String city, String country) {}

    static UserResponseV2 from(User u) {
        return new UserResponseV2(u.getId(), u.getName(),
            new AddressV2(u.getStreet(), u.getCity(), u.getCountry()));
    }
}
```

---

### ⚖️ Comparison Table

| Strategy | Example | Visible | Cacheable | REST-Pure | Routing Ease |
|---|---|---|---|---|---|
| **URI Path** | `/v1/users` | ✅ | ✅ | ❌ | Very Easy |
| **Query Param** | `/users?v=2` | ✅ | ✅ (with varying) | ❌ | Easy |
| **Accept Header** | `Accept: application/vnd.api.v2+json` | ❌ | Needs Vary | ✅ | Harder |
| **Custom Header** | `API-Version: 2` | ❌ | Needs Vary | ✅ | Harder |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| All API changes require a new version | Only *breaking* changes require new versions; adding optional fields or new endpoints is non-breaking |
| URI versioning violates REST principles | It does in theory, but in practice it's the most widely adopted and understood approach |
| You must support old versions forever | No — announce a sunset date, track adoption, and retire when traffic is below a threshold |
| Versioning is the same as backward compatibility | Versioning is one tool for managing backward compatibility; others include field aliasing, nullable migration fields, graceful schema evolution |

---

### 🚨 Failure Modes & Diagnosis

**Version Proliferation — Too Many Active Versions**

Symptom:
Engineers must test changes in v1, v2, v3, v4, v5 simultaneously. Bug in v1 mapping
class causes a v1-only outage undetected for days. 40% of traffic still on v1 from 2020.

Root Cause:
No systematic deprecation enforcement. Sunset dates were set but never enforced.
v1 was kept available because "some important client might still be using it."

Diagnostic:
```
# Measure usage per version via access logs or metrics
Prometheus: http_requests_total{path=~"/api/v1/.*"}
  → if < 1% of traffic after sunset date: safe to retire
  → if 10%+ of traffic: need outreach to identified clients

# Identify clients still on old versions:
Access logs: grep v1 calls for User-Agent header → identify client types
Add version-usage metrics per API key / JWT subject claim
```

Fix:
Enforce sunset dates. 90 days before: email all API key holders still on v1.
30 days before: return 400 with migration guide for test environments.
0 days: return 410 Gone.

---

### 🔗 Related Keywords

- `API Deprecation Strategy` — the process of retiring old versions after migration
- `OpenAPI/Swagger` — the specification format for documenting all API versions
- `Backward Compatibility` — the property that old clients continue working
- `Semantic Versioning` — a related versioning scheme for software libraries

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Multiple simultaneous API contracts so    │
│              │ clients migrate on their own timeline      │
├──────────────┼───────────────────────────────────────────┤
│ BREAKING     │ Remove field, rename field, change type,  │
│ CHANGES      │ add required param, change status codes   │
├──────────────┼───────────────────────────────────────────┤
│ NON-BREAKING │ Add optional field, new endpoint, relax   │
│ CHANGES      │ constraints, add optional param           │
├──────────────┼───────────────────────────────────────────┤
│ BEST STRATEGY│ URI path versioning: /v1/, /v2/           │
│ IN PRACTICE  │ (visible, cacheable, easy to route)       │
├──────────────┼───────────────────────────────────────────┤
│ RETIRE VIA   │ Deprecation + Sunset HTTP headers         │
│              │ (RFC 8594) → traffic tracking → 410 Gone  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Breaking change? New version contract"  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ API Deprecation → OpenAPI → BFF           │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q.** You provide a public API used by 5,000 third-party integrations. Your v1 was released 3 years ago. Analysis shows 40% of traffic is still on v1 (3 years after announcing v2). Some integrations are dormant webhooks from inactive accounts. Some are from companies that have since been acquired. Design a complete version retirement plan that minimizes disruption, handles the dormant client problem, and gives you clear go/no-go criteria for flipping the v1 sunset switch.
