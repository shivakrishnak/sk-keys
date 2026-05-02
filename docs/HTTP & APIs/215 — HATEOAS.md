---
layout: default
title: "HATEOAS"
parent: "HTTP & APIs"
nav_order: 215
permalink: /http-apis/hateoas/
number: "0215"
category: HTTP & APIs
difficulty: ★★★
depends_on: REST, RESTful Constraints, HTTP Methods, Hypermedia, HTTP Headers
used_by: API Design Best Practices, Hypermedia, API Discoverability
related: REST, RESTful Constraints, Hypermedia, OpenAPI, GraphQL
tags:
  - api
  - rest
  - architecture
  - hypermedia
  - deep-dive
---

# 215 — HATEOAS

⚡ TL;DR — HATEOAS is REST's most radical constraint: responses include links to all legal next actions, so clients never need to hardcode API URLs or workflow logic—they navigate the API like a website, following links the server provides.

| #215            | Category: HTTP & APIs                                             | Difficulty: ★★★ |
| :-------------- | :---------------------------------------------------------------- | :-------------- |
| **Depends on:** | REST, RESTful Constraints, HTTP Methods, Hypermedia, HTTP Headers |                 |
| **Used by:**    | API Design Best Practices, Hypermedia, API Discoverability        |                 |
| **Related:**    | REST, RESTful Constraints, Hypermedia, OpenAPI, GraphQL           |                 |

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A REST API documents its endpoints in a PDF or OpenAPI spec. Clients hardcode those
URLs: `/orders/{id}/cancel`, `/orders/{id}/return`. Now the business adds a rule:
you can only cancel an order if it's `PENDING`; you can only return it if it's
`DELIVERED`. Clients must replicate this state machine logic — checking order status,
deciding which URL to call. When the business rule changes (cancellation now only
within 15 minutes), every client must update its logic. The API documentation is
out of sync. A mobile app in production is trying to cancel a DELIVERED order and
getting 422 errors it doesn't understand.

**THE BREAKING POINT:**
Clients that hardcode API URLs and workflow state machines are tightly coupled to
the server's internal business rules. Every business logic change requires a client
update, a documentation update, and a coordinated release. At scale, with 10 client
teams, this coordination cost becomes the primary bottleneck.

**THE INVENTION MOMENT:**
This is exactly why HATEOAS was invented. If the server communicates available
actions AS LINKS in the response body, clients follow links rather than construct
URLs. The server controls which links appear — and therefore which actions are
available. Business rule changes are reflected immediately in which links appear,
without any client code change.

---

### 📘 Textbook Definition

**HATEOAS** (Hypermedia As The Engine Of Application State) is the fourth
sub-constraint of REST's uniform interface, formalised by Roy Fielding. It
specifies that REST responses must contain hypermedia controls — links and forms
describing the actions available from the current state. Clients interact with the
application entirely through dynamically provided hypermedia, without needing
out-of-band knowledge of URL structures or business logic. Common hypermedia formats
include **HAL** (Hypertext Application Language, RFC draft), **JSON:API**, and
**Spring HATEOAS** representations. HATEOAS establishes a state machine driven by
the server: the set of links in a response IS the set of legal transitions from the
current state. Fielding considers HATEOAS mandatory for a system to be REST; its
absence means the system is an "HTTP API" but not truly RESTful.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
HATEOAS means your API response tells the client what it can do next, just like a
webpage tells users where they can click — no URL hardcoding needed.

**One analogy:**

> Using a REST API without HATEOAS is like navigating a city by memorising a list
> of all street addresses. Using HATEOAS is like navigating the same city using
> Google Maps — at every step, the map shows you which roads are currently open
> and where they lead. If a road closes (business rule changes), the map automatically
> stops showing it. You never need to update your list of addresses.

**One insight:**
HATEOAS eliminates the hidden coupling in "documented" APIs: the coupling between
the client's hardcoded URL construction and the server's URL structure. The web has
used HATEOAS since 1991 (with HTML `<a href>` links). Every time you browse a
website, you follow server-provided links without knowing URL patterns — and every
website can change its URL structure without updating your browser. HATEOAS applies
the same model to APIs.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. The current state of a resource determines which actions are available. The
   server knows this state; the client should not duplicate this knowledge.
2. Links embedded in responses are the API's state machine, made explicit.
   A link's presence = the transition is legal. A link's absence = it is not.
3. Clients start from a single well-known entry point (the API root, e.g.,
   `GET /api`) and navigate entirely through links. No out-of-band URL knowledge.

**THE STATE MACHINE AS LINKS:**

```
┌──────────────────────────────────────────────────────┐
│    Order State Machine — HATEOAS Links vs Code       │
├──────────────────────────────────────────────────────┤
│                     Without HATEOAS:                 │
│                                                      │
│  Client code:                                        │
│  if (order.status == "PENDING") {                    │
│    allow("cancel", "/orders/" + id + "/cancel")      │
│    allow("pay",    "/orders/" + id + "/pay")         │
│  } else if (order.status == "PAID") {                │
│    allow("ship",   "/orders/" + id + "/ship")        │
│  } else if (order.status == "SHIPPED") {             │
│    allow("return", "/orders/" + id + "/return")      │
│  }                                                   │
│  // Business logic duplicated in client!             │
│                                                      │
│                      With HATEOAS:                   │
│                                                      │
│  // Server response for PENDING order:               │
│  { "id": 123, "status": "PENDING",                   │
│    "_links": {                                       │
│      "self":   { "href": "/orders/123" },            │
│      "cancel": { "href": "/orders/123/cancel" },     │
│      "pay":    { "href": "/orders/123/pay" }         │
│    }                                                 │
│  }                                                   │
│                                                      │
│  // Server response for DELIVERED order:             │
│  { "id": 123, "status": "DELIVERED",                 │
│    "_links": {                                       │
│      "self":   { "href": "/orders/123" },            │
│      "return": { "href": "/orders/123/return" }      │
│    }                                                 │
│  }                                                   │
│  // cancel link ABSENT = cancel not available        │
│  // Client reads links — no state machine knowledge  │
└──────────────────────────────────────────────────────┘
```

**LINK RELATIONS (rel):**
Each link has a `rel` (relation type) that names the semantic of the link:

- `self` — the resource's own URL (canonical identifier)
- `next`, `prev` — pagination links
- `edit`, `delete` — CRUD operations
- Custom rels: `cancel`, `approve`, `ship`, etc.
- IANA-registered rels: `alternate`, `author`, `collection`, `item`

**HYPERMEDIA FORMATS:**

**HAL (Hypertext Application Language):**

```json
{
  "id": 123,
  "total": 49.99,
  "status": "PENDING",
  "_links": {
    "self": { "href": "/orders/123" },
    "cancel": { "href": "/orders/123/cancel", "method": "DELETE" },
    "pay": { "href": "/orders/123/payments", "method": "POST" },
    "customer": { "href": "/customers/456" }
  },
  "_embedded": {
    "items": [
      {
        "productId": 789,
        "qty": 1,
        "price": 49.99,
        "_links": { "self": { "href": "/products/789" } }
      }
    ]
  }
}
```

**THE TRADE-OFFS:**

- Gain: clients decouple from URL structure; server controls state machine;
  API evolvable without coordinated client updates
- Cost: responses larger (links add payload); client implementation more complex
  (must follow links, not construct URLs); caching harder (dynamic link hrefs
  with IDs); tooling (OpenAPI) doesn't natively model HATEOAS; few REST
  frameworks enforce it

---

### 🧪 Thought Experiment

**SETUP:**
An e-commerce API has 4 client teams: Web (React), iOS, Android, and a 3rd-party
partner API. The business adds a rule: orders over $500 require manager approval
before shipping. URL involved: `POST /orders/{id}/ship`.

**WHAT HAPPENS WITHOUT HATEOAS:**

1. Developer adds the rule: orders > $500 are PUT in `AWAITING_APPROVAL` state
2. `POST /orders/{id}/ship` returns 422 for unapproved high-value orders
3. All 4 client teams scramble to update their code to check `total > 500`
4. iOS and Android need app store releases (2-week delay)
5. 3rd-party partner keeps sending ship requests, failing silently
6. Coordinating releases across 4 teams delays shipping for 2 weeks

**WHAT HAPPENS WITH HATEOAS:**

1. Developer adds the rule: orders > $500 get `approval` link instead of `ship` link
2. `GET /orders/{id}` response changes automatically:
   - For `total < 500`: `_links.ship` present
   - For `total >= 500`: `_links.approve` present, `_links.ship` absent
3. All 4 clients check `_links.ship` — if present, show "Ship" button; if absent, hide it
4. The business rule change is live immediately for all clients
5. Zero coordinated releases. Zero client code changes.

**THE INSIGHT:**
HATEOAS moves the state machine from client code to server responses. In the without-
HATEOAS scenario, every business logic change requires N client code releases. With
HATEOAS: one server change, zero client releases. The larger the number of clients,
the bigger this benefit. At 100 client integrations, HATEOAS becomes a coordination
cost multiplier from 100× to 1×.

---

### 🧠 Mental Model / Analogy

> HATEOAS is like how a website works: you go to amazon.com (one entry point),
> and every page you see has links and buttons for what you can do NEXT from THIS
> page. Amazon's servers decide which buttons appear — "Add to Cart" appears on
> in-stock items, not on out-of-stock ones. You never need to know the URL for the
> "Add to Cart" action; the button IS the action. Amazon can change every URL on
> the site and your browsing still works — because you follow links, not memorised
> addresses.

**Mapping:**

- "amazon.com home page" → API entry point (`GET /api`)
- "page links and buttons" → `_links` in HATEOAS response
- "Add to Cart button absent on out-of-stock" → cancel link absent on non-cancellable
- "You follow links" → client reads `_links.cancel.href` before calling
- "Amazon changes URLs" → server changes link hrefs → client unaffected

**Where this analogy breaks down:**
Websites serve HTML which renders naturally in a browser. APIs serve JSON — "links"
in HAL are just JSON properties. Clients must actively choose to follow them rather
than hardcode URLs. Unlike browsers, which naturally navigate HTML links, API clients
require deliberate engineering discipline to use HATEOAS links. This is why HATEOAS
adoption in practice is much lower than Fielding intended.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
HATEOAS means every API response tells you what you can do next. Instead of reading
documentation to know that you must go to `/orders/123/cancel` to cancel an order,
the response itself contains a link called "cancel" with the exact URL. If cancellation
isn't allowed (order already shipped), the "cancel" link simply isn't in the response.
Your code never needs to know the rules — you just follow the links you're given.

**Level 2 — How to use it (junior developer):**
In Spring HATEOAS, use `EntityModel.of(resource)` and `.add(linkTo(methodOn(...)))`
to attach links. Return `EntityModel<T>` instead of `T` from controllers. Client-side:
never hardcode API URLs except the root entry point. Always navigate to URLs by
reading them from `_links` in responses. Parse `_links.xxx.href` to get the URL
for action `xxx`. Check if a link exists before showing the corresponding UI button.

**Level 3 — How it works (mid-level engineer):**
Full HATEOAS implementation has three layers: (1) link generation on the server
(URL must be absolute, including host, so clients can use it without context);
(2) client navigation (follow `_links`, never construct URLs); (3) link relation
semantics (use IANA-registered `rel` values where possible; define custom rels in
a profile document at a stable URL). Caching HATEOAS responses is complex: links
contain resource IDs and state-dependent paths. `Cache-Control: private` is
common for HATEOAS responses. The `Link` HTTP header can carry HATEOAS links for
responses where the body format can't carry them (redirects, 204s).

**Level 4 — Why it was designed this way (senior/staff):**
Fielding's argument for HATEOAS was motivated by the observed failure mode of
"REST" APIs that required extensive out-of-band documentation: if you need
documentation to use an API, the API is not self-descriptive, and HATEOAS is not
implemented. He argued that the HTML web required zero documentation for browsers —
browsers simply followed whatever links HTML pages provided. HATEOAS extends this
to machine clients. The practical rejection of HATEOAS in industry reflects a real
tension: HATEOAS requires clients to write more complex link-following code vs
simpler URL-constructing code, and the decoupling benefit only pays off when the
API evolves rapidly with many independent clients. Most enterprise APIs use only
`self` links for resource identity and ignore HATEOAS otherwise — a pragmatic but
non-purist approach.

---

### ⚙️ How It Works (Mechanism)

**Spring HATEOAS Implementation:**

```
┌──────────────────────────────────────────────────────┐
│    Spring HATEOAS — Response Assembly                │
├──────────────────────────────────────────────────────┤
│ 1. Controller returns EntityModel:                   │
│    EntityModel.of(order)                             │
│      .add(linkTo(methodOn(OrderCtrl.class)           │
│              .getOrder(id)).withSelfRel())           │
│      .add(linkTo(methodOn(OrderCtrl.class)           │
│              .cancelOrder(id)).withRel("cancel"))    │
│                                                      │
│ 2. Conditional links based on state:                 │
│    if (order.isCancellable()) {                      │
│      model.add(cancelLink);                          │
│    }                                                 │
│    if (order.isReturnable()) {                       │
│      model.add(returnLink);                          │
│    }                                                 │
│                                                      │
│ 3. Serialised response:                              │
│   {                                                  │
│     "id": 123,                                       │
│     "status": "PENDING",                             │
│     "_links": {                                      │
│       "self":   {"href":"/orders/123"},              │
│       "cancel": {"href":"/orders/123/cancel"}        │
│     }                                               │
│   }                                                  │
└──────────────────────────────────────────────────────┘
```

**Pagination via HATEOAS (standard pattern):**

```json
GET /orders?page=2&size=10
{
  "content": [...],
  "page": { "size": 10, "number": 2, "total": 157 },
  "_links": {
    "self":  { "href": "/orders?page=2&size=10" },
    "first": { "href": "/orders?page=0&size=10" },
    "prev":  { "href": "/orders?page=1&size=10" },
    "next":  { "href": "/orders?page=3&size=10" },
    "last":  { "href": "/orders?page=15&size=10" }
  }
}
```

Client never constructs pagination URLs — it follows `next` and `prev` links.

**Link in HTTP Header (for responses without body):**

```
HTTP/1.1 204 No Content
Link: </orders/123>; rel="self"
Link: </orders/123/ship>; rel="ship"
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**

```
┌──────────────────────────────────────────────────────┐
│            HATEOAS API Interaction Flow              │
├──────────────────────────────────────────────────────┤
│ 1. Client: GET /api                                  │
│    Response: {"_links": {"orders": {                 │
│      "href": "/orders"}}}                            │
│         ↓                                            │
│ 2. Client: GET /orders                               │
│    Response: list + "_links": {next, prev}           │
│         ↓                                            │
│ 3. Client: GET /orders/123 (from _links.orders.href) │
│    [HATEOAS ← YOU ARE HERE]                          │
│    Response: order + conditional action links        │
│         ↓                                            │
│ 4. Client reads _links: cancel link present?         │
│    YES → shows "Cancel" button                       │
│    NO  → hides "Cancel" button                       │
│         ↓                                            │
│ 5. User clicks Cancel → client POSTs to              │
│    _links.cancel.href (never hardcoded URL)          │
│         ↓                                            │
│ 6. Server changes order state                        │
│    Response: updated order + new set of _links       │
│    (cancel link now absent, return link now absent,  │
│     refund link present)                             │
└──────────────────────────────────────────────────────┘
```

**FAILURE PATH:**
Business rule added: cancellation disabled during flash sales. Without HATEOAS:
all clients fail with 422 and must be patched. With HATEOAS: server removes
`cancel` link from responses, all UI clients stop showing the cancel button
immediately — no client code changes.

**WHAT CHANGES AT SCALE:**
At scale (100s of API clients), HATEOAS pays dividends in API governance:
changing a URL structure, adding state machine transitions, or modifying
business rules requires zero coordinated client releases. The server is the
single source of truth for which operations are available. This governance
benefit is the primary reason large platforms (Paypal, GitHub API) implement
HATEOAS even when it adds response payload overhead.

---

### 💻 Code Example

**Example 1 — Spring HATEOAS: conditional, state-aware links:**

```java
@RestController
@RequestMapping("/orders")
public class OrderController {

    @GetMapping("/{id}")
    public EntityModel<OrderDto> getOrder(@PathVariable Long id) {
        OrderDto order = orderService.findById(id);

        // Base model with self-link (always present):
        EntityModel<OrderDto> model = EntityModel.of(order,
            linkTo(methodOn(OrderController.class)
                .getOrder(id)).withSelfRel()
        );

        // Conditional links based on order state:
        if (order.getStatus() == Status.PENDING) {
            model.add(
                linkTo(methodOn(OrderController.class)
                    .cancelOrder(id)).withRel("cancel"),
                linkTo(methodOn(OrderController.class)
                    .payOrder(id)).withRel("pay")
            );
        }
        if (order.getStatus() == Status.PAID) {
            model.add(
                linkTo(methodOn(OrderController.class)
                    .shipOrder(id)).withRel("ship")
            );
        }
        if (order.getStatus() == Status.DELIVERED) {
            model.add(
                linkTo(methodOn(OrderController.class)
                    .returnOrder(id)).withRel("return")
            );
        }
        return model;
    }
}
```

**Example 2 — Pagination collection with HATEOAS:**

```java
@GetMapping
public CollectionModel<EntityModel<OrderDto>> listOrders(
        @RequestParam(defaultValue = "0") int page,
        @RequestParam(defaultValue = "20") int size) {

    Page<OrderDto> orders = orderService.findAll(
        PageRequest.of(page, size));

    List<EntityModel<OrderDto>> content = orders.stream()
        .map(o -> EntityModel.of(o,
            linkTo(methodOn(OrderController.class)
                .getOrder(o.getId())).withSelfRel()))
        .collect(Collectors.toList());

    Link selfLink = linkTo(methodOn(OrderController.class)
        .listOrders(page, size)).withSelfRel();

    CollectionModel<EntityModel<OrderDto>> model =
        CollectionModel.of(content, selfLink);

    // Add pagination links:
    if (orders.hasNext()) {
        model.add(linkTo(methodOn(OrderController.class)
            .listOrders(page + 1, size)).withRel(IanaLinkRelations.NEXT));
    }
    if (orders.hasPrevious()) {
        model.add(linkTo(methodOn(OrderController.class)
            .listOrders(page - 1, size)).withRel(IanaLinkRelations.PREV));
    }
    return model;
}
```

**Example 3 — Client consuming HATEOAS links (JavaScript):**

```javascript
// GOOD: Client follows links, never constructs URLs
async function cancelOrder(orderId) {
  // Get order with its current links:
  const order = await fetch(`/api/orders/${orderId}`).then((r) => r.json());

  // Check if cancel is available in current state:
  const cancelLink = order._links?.cancel;
  if (!cancelLink) {
    throw new Error("Cancellation not available for this order");
  }

  // Follow the link — URL from server, not hardcoded:
  const result = await fetch(cancelLink.href, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });
  return result.json();
}

// BAD: Hardcoded URL — breaks when server changes URL structure
async function cancelOrder_BAD(orderId) {
  // This will break if server renames the endpoint:
  return fetch(`/api/orders/${orderId}/cancel`, { method: "POST" }).then((r) =>
    r.json(),
  );
}
```

---

### ⚖️ Comparison Table

| Approach          | Client-Server Coupling   | API Evolution          | Tooling Support | Complexity |
| ----------------- | ------------------------ | ---------------------- | --------------- | ---------- |
| **HATEOAS**       | Minimal (follows links)  | Server-driven          | Limited         | High       |
| OpenAPI-only      | Moderate (URL contracts) | Client + Server coord. | Excellent       | Low        |
| GraphQL           | Low (query-driven)       | schema-versioned       | Very Good       | Medium     |
| Strict RPC (gRPC) | High (generated stubs)   | Proto versioning       | Excellent       | Medium     |

**How to choose:** Implement full HATEOAS when you have many independent clients
and business rules that change frequently (payment workflows, approval chains,
e-commerce state machines). Use OpenAPI-documented REST for stable CRUD APIs with
few clients. The `self` link is universally recommended even without full HATEOAS.

---

### ⚠️ Common Misconceptions

| Misconception                         | Reality                                                                                                                                        |
| ------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| HATEOAS is optional in REST           | Fielding considers it mandatory for the uniform interface constraint. Its absence technically means the system is an "HTTP API" not a REST API |
| Adding \_links to responses is enough | HATEOAS requires clients to FOLLOW links rather than constructing URLs. Adding links that clients ignore provides no benefit                   |
| HATEOAS makes APIs self-documenting   | HATEOAS makes API workflows navigable without URL knowledge, but link relation semantics still need documentation                              |
| HATEOAS is impractical for production | PayPal, GitHub, AWS HAL APIs, and Spring HATEOAS use it at scale. The challenge is client adoption, not server implementation                  |
| Every link must be an absolute URL    | RFC 5988 (Web Linking) allows both absolute and relative URIs in links. Best practice: use absolute URIs to avoid base URL ambiguity           |

---

### 🚨 Failure Modes & Diagnosis

**Client Hardcoding URLs (HATEOAS Anti-Pattern)**

Symptom: API URL structure changes → clients break with 404s; no benefit from
HATEOAS despite server implementation; mobile app needs emergency release.

Root Cause: Client teams ignored `_links` and hardcoded URL patterns anyway,
defeating the entire purpose of HATEOAS. Common when HATEOAS isn't enforced
by API contract tests.

Diagnostic Command / Tool:

```bash
# Search client code for hardcoded API URL patterns:
grep -r '"/orders/' frontend-src/ | grep -v "_links"
# Find: '/orders/' + id + '/cancel'  ← HARDCODED, not using _links

# Contract test: verify link values match server:
curl -s https://api.example.com/orders/123 | jq '._links'
```

Fix: Code review policy: all API URLs must come from parsed `_links`.
Add a linting rule that flags URL string construction for API paths.

Prevention: Provide a client SDK that wraps HATEOAS navigation. Teams use
the SDK, not raw `fetch`, preventing URL hardcoding at the source.

---

**Missing Self Link (Resource Identity)**

Symptom: Clients cannot bookmark or reference specific resources; after a POST
201 response, client doesn't know the canonical URL of the created resource.

Root Cause: Responses missing the `self` link. The `self` `rel` is the minimum
viable HATEOAS — it provides the resource's canonical URL for bookmarking,
caching, and subsequent operations.

Diagnostic Command / Tool:

```bash
# Check if responses include self links:
curl -s https://api.example.com/orders/123 | jq '._links.self'
# null ← missing self link

# POST and check Location header + self link:
curl -s -D - -X POST -H "Content-Type: application/json" \
  -d '{"item":"book"}' https://api.example.com/orders \
  | grep -E "Location|self"
```

Fix: Always include `self` link in every resource response. Minimum viable
HATEOAS: just `self`. In Spring HATEOAS, add `.withSelfRel()` to every
`EntityModel.of()` call.

Prevention: Add an API contract test asserting `_links.self` is present on
all 200/201 responses returning entity resources.

---

**Circular Links (HATEOAS Self-Reference Loops)**

Symptom: Client enters infinite navigation loop; memory exhaustion in
recursive link-following implementations; response payloads grow exponentially
when `_embedded` resources include full HATEOAS representations.

Root Cause: Embedded sub-resources include their full HATEOAS links, which
include their parent's URL, which includes the sub-resources...

Diagnostic Command / Tool:

```bash
# Check response size for circular embedding:
curl -s https://api.example.com/orders/123 | wc -c
# If > 50KB for a simple order, likely has circular _embedded references
```

Fix: In `_embedded` resources, include only `self` links — not full HATEOAS
representations. Top-level resources include full action links;
embedded references include only their canonical URL.

Prevention: Define a response shape contract in API design review: embedded
resources use minimal representation (`id` + `self` link only).

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `REST` — HATEOAS is the fourth sub-constraint of REST's uniform interface;
  REST must be understood before HATEOAS
- `RESTful Constraints` — HATEOAS is one of the six RESTful constraints; context
  of all constraints is needed to understand where HATEOAS fits
- `Hypermedia` — HATEOAS is hypermedia applied to APIs; HTML links are the
  original hypermedia — the same concept applied to machine clients

**Builds On This (learn these next):**

- `Hypermedia` — the broader concept that links connect resources across the
  internet; HATEOAS applies hypermedia to API state transitions
- `API Design Best Practices` — practical guidance on when to implement full
  HATEOAS vs pragmatic "self-link only" approaches

**Alternatives / Comparisons:**

- `OpenAPI` — documents API contracts statically (URL structure, parameters,
  schemas) — the practical alternative to HATEOAS for API discoverability
- `GraphQL` — self-descriptive via introspection query; clients discover available
  fields and operations through `__schema` — a different approach to API
  discoverability that doesn't use hypermedia links

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ REST constraint: responses include links  │
│              │ to available next actions (server-driven  │
│              │ state machine)                            │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Clients hardcode API URLs and business    │
│ SOLVES       │ rule logic — coupling to server internals │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ A link's ABSENCE = action not available   │
│              │ A link's PRESENCE = action is available   │
│              │ Server controls state machine via links   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Many independent clients, complex business│
│              │ state machines, frequent rule changes     │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Simple CRUD APIs with stable URL structure│
│              │ and few clients; adds payload overhead    │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Zero coordinated client releases on rule  │
│              │ changes vs larger payloads + more complex │
│              │ client code                              │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Follow links, don't memorise addresses   │
│              │  — the server shows you the way."        │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Hypermedia → API Design Best Practices → │
│              │ OpenAPI → RESTful Constraints            │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A client team argues: "We already use OpenAPI to document all available
endpoints and their states — this is equivalent to HATEOAS because every developer
reads the spec before coding." Evaluate this claim against Fielding's fundamental
rationale for HATEOAS. Specifically: what is the structural difference between static
OpenAPI documentation and dynamic HATEOAS links in terms of coupling, runtime
adaptation, and the information each provides when a business rule changes from
"any user can cancel" to "only premium users can cancel"?

**Q2.** You are designing a HATEOAS-based payment checkout API. The checkout flow
has states: `CART` → `ADDRESS_ENTERED` → `PAYMENT_ADDED` → `CONFIRMED` → `FULFILLED`.
Each state transition has preconditions (address must be verified, payment method
must be valid, inventory must be reserved). Design the exact link structure for
each state — which `rel` names appear in which state — and explain how a client
that has never seen documentation would navigate from `CART` to `CONFIRMED` using
only the links in responses. What happens when inventory runs out between `PAYMENT_ADDED`
and `CONFIRMED`, and how does HATEOAS communicate this state change to the client?
