---
layout: default
title: "Hypermedia / HATEOAS"
parent: "HTTP & APIs"
nav_order: 257
permalink: /http-apis/hypermedia-hateoas/
number: "0257"
category: HTTP & APIs
difficulty: ★★★
depends_on: REST, HTTP, API Design Best Practices
used_by: REST APIs, Self-Describing APIs, Workflow APIs
related: REST, API Design Best Practices, Richardson Maturity Model
tags:
  - hypermedia
  - hateoas
  - rest
  - self-describing-api
  - advanced
---

# 257 — Hypermedia / HATEOAS

⚡ TL;DR — HATEOAS (Hypermedia as the Engine of Application State) is a REST constraint where API responses include links describing what actions are available next — similar to how a web browser follows links without needing to know URLs in advance; in practice, clients discover and navigate API capabilities dynamically from response links rather than hardcoding URL structures, enabling APIs to evolve without breaking clients.

┌──────────────────────────────────────────────────────────────────────────┐
│ #257         │ Category: HTTP & APIs              │ Difficulty: ★★★      │
├──────────────┼────────────────────────────────────┼──────────────────────┤
│ Depends on:  │ REST, HTTP, API Design Best Prctcs │                      │
│ Used by:     │ REST APIs, Self-Describing APIs,   │                      │
│              │ Workflow APIs                      │                      │
│ Related:     │ REST, API Design Best Practices,  │                      │
│              │ Richardson Maturity Model          │                      │
└──────────────────────────────────────────────────────────────────────────┘

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Client SDKs hardcode URL patterns: `"/api/v1/orders/" + orderId + "/cancel"`. API team
renames the endpoint to `/api/v1/orders/{id}/cancellations`. SDK breaks. All clients need
updates. Or: a client must download the OpenAPI spec and know every URL in advance to build
functionality — there's no "follow the API" approach. Workflow state machines are especially
fragile: clients hardcode which actions are available for which order statuses, duplicating
logic that lives on the server.

---

### 📘 Textbook Definition

**HATEOAS** (Hypermedia as the Engine of Application State) is one of Roy Fielding's
original REST constraints (from his 2000 dissertation). It requires that API responses
include hypermedia links describing what transitions (actions) are available from the
current resource state. The client begins with a known entry point (the API root) and
follows links discovered in responses — never constructing URLs from templates or
hardcoding them. Analogous to browsing the web: users don't know every URL in advance;
they follow hyperlinks. Standard hypermedia formats: **HAL** (Hypertext Application
Language — `_links` and `_embedded`), **JSON:API** (resources + relationships + links),
and **Siren**. Spring HATEOAS implements this pattern with `EntityModel`, `CollectionModel`,
and the `WebMvcLinkBuilder`. The **Richardson Maturity Model** defines four levels:
Level 0 (plain HTTP, like SOAP), Level 1 (resources), Level 2 (HTTP verbs + status codes),
Level 3 (HATEOAS) — "truly RESTful."

---

### ⏱️ Understand It in 30 Seconds

**One line:**
HATEOAS means API responses contain links to available next actions — clients follow
links instead of constructing URLs, making APIs self-documenting and evolvable.

**One analogy:**
> HATEOAS is like a choose-your-own-adventure book.
> You don't read the whole book upfront and memorize every page number.
> Each page tells you: "If you go left, turn to page 47. If you go right, turn to page 92."
> You follow the options presented on the current page — the book itself guides navigation.
> API responses work the same: "from this Order resource, you can: [cancel], [track], [return]."
> The client doesn't need to know the order cancel URL — the response provides it *when applicable*.

**One insight:**
The most important practical benefit of HATEOAS isn't URL flexibility — it's **conditional
links**. A PENDING order response includes a `cancel` link. A SHIPPED order does NOT
include `cancel` but includes `track` instead. Clients never need to check `if order.status == 'PENDING' { show cancel button }` — the server controls available actions by presence/absence of links. Business logic stays server-side.

---

### 🔩 First Principles Explanation

**HAL FORMAT:**

```json
// HAL (Hypertext Application Language) Response:
// GET /api/v1/orders/ORD-789
{
  "id": "ORD-789",
  "status": "PENDING",
  "total": 99.99,
  "_links": {
    "self": {
      "href": "/api/v1/orders/ORD-789"
    },
    "cancel": {
      "href": "/api/v1/orders/ORD-789/cancellations",
      "method": "POST"
    },
    "track": {
      "href": null  ← or omit entirely: not yet shipped
    },
    "customer": {
      "href": "/api/v1/customers/CUST-123"
    },
    "items": {
      "href": "/api/v1/orders/ORD-789/items"
    }
  }
}

// Same order after shipping:
{
  "id": "ORD-789",
  "status": "SHIPPED",
  "_links": {
    "self": { "href": "/api/v1/orders/ORD-789" },
    "track": { "href": "/api/v1/shipments/SHIP-456" },
    "return": { "href": "/api/v1/orders/ORD-789/returns", "method": "POST" }
    // cancel link ABSENT: order is shipped, cannot cancel
  }
}

CLIENT CODE (state-driven by links):
  if (order._links.cancel) {
    showCancelButton();  // server told us this is available
  }
  // NOT: if (order.status === 'PENDING') { showCancelButton() }
  // The server owns the business rule about when cancel is available
```

**RICHARDSON MATURITY MODEL:**

```
Level 0: HTTP as transport tunnel (SOAP/XML-RPC)
  POST /paymentService
  Body: <soap:Envelope>...</soap:Envelope>
  → One endpoint, all verbs, no resource identity

Level 1: Resources (URLs per resource)
  POST /orders
  GET /orders/5
  → Resources have identity, but HTTP methods not respected

Level 2: HTTP Verbs + Status Codes
  GET /orders → 200
  POST /orders → 201
  DELETE /orders/5 → 204 or 404
  → "Practical REST" — most real-world APIs reach this level

Level 3: HATEOAS (true REST)
  GET /orders/5 response includes _links
  → Fully self-describing, client navigates by links
  → Almost no production REST API fully implements Level 3
```

---

### 🧪 Thought Experiment

**SCENARIO:** Order workflow without vs with HATEOAS.

```
WITHOUT HATEOAS:
  Client has hardcoded URL: POST /api/v2/orders/{id}/cancel
  API updates to: POST /api/v2/orders/{id}/cancellations (RESTful noun)
  Client breaks: 404 on every cancel attempt
  SDK update required. All consumers re-release.

WITH HATEOAS:
  Client gets order: links.cancel = "/api/v2/orders/{id}/cancellations"
  API changes URL: response still includes correct href in _links.cancel
  Client follows link from response — zero update needed
  URL changed, client unaware, zero breakage

CONDITIONAL ACTION EXAMPLE:
  WITHOUT HATEOAS:
  Client has: if (order.status === 'PENDING') { show Cancel }
                if (order.status === 'SHIPPED') { show Return }
  Business rule changes: orders that are "AWAITING_PAYMENT" can also be cancelled
  → All clients must update their state machine logic
  → Business logic duplicated in every client

  WITH HATEOAS:
  Client: show Cancel button IF links.cancel exists (regardless of status)
  Server adds cancel link for AWAITING_PAYMENT orders
  → Client automatically shows Cancel for AWAITING_PAYMENT (no change needed)
  → Business logic centralized on server
```

---

### 🧠 Mental Model / Analogy

> HATEOAS is like a GPS navigation system vs a paper map.
> Paper map: you memorize all routes upfront, construct the path yourself, 
> and must re-buy the map when roads change.
> GPS: you enter the destination. The GPS dynamically discovers the route 
> from your current position and road conditions. Road changes: GPS reroutes automatically.
> API links (HATEOAS) are the GPS: client says "I want next steps from here,"
> and the API dynamically provides the available routes from the current state.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** HATEOAS means every API response includes links to "what you can do next," like a web page with hyperlinks. Clients follow links instead of building URLs.

**Level 2:** Use Spring HATEOAS: `EntityModel.of(order, linkTo(methodOn(OrderController.class).getOrder(id)).withSelfRel(), linkTo(methodOn(OrderController.class).cancelOrder(id)).withRel("cancel"))`. Add conditional links based on resource state. Return with `produces = "application/hal+json"`.

**Level 3:** Separate "affordances" from representation. Link building is conditional on state machine transitions (cancel only if PENDING). Use `Affordances.of(link).afford(HttpMethod.POST).withInput(CancelRequest.class).toLink()` for form-like descriptions. Distinguish link relations: IANA-registered (`self`, `next`, `prev`) vs application-specific (`cancel`, `approve`). `profile` link points to schema/documentation.

**Level 4:** Fielding's original REST constraint is often misunderstood. The goal isn't to include links for clever URL changes — it's to enable EVOLVABLE systems where the server drives client behavior. In practice: most teams find HATEOAS overhead high and benefits limited for well-known stable APIs. It shines for: workflow APIs with complex state machines, APIs with many optional actions driven by server-side rules, HAL-based discovery for machine-to-machine integration. Trade-off: coupling shifts from URL hardcoding to link-relation hardcoding — clients still need to know what "cancel" means. The argument that HATEOAS eliminates all coupling is philosophically correct but pragmatically overstated.

---

### ⚙️ How It Works (Mechanism)

```
SPRING HATEOAS:

@RestController
@RequestMapping("/api/v1/orders")
public class OrderController {

    @GetMapping("/{id}")
    public EntityModel<OrderDto> getOrder(@PathVariable String id) {
        Order order = orderService.findById(id);
        OrderDto dto = toDto(order);
        
        // Always add self link
        List<Link> links = new ArrayList<>();
        links.add(linkTo(methodOn(OrderController.class).getOrder(id)).withSelfRel());
        
        // Conditional links based on current state
        if (order.isCancellable()) {
            links.add(linkTo(methodOn(OrderController.class)
                .cancelOrder(id, null)).withRel("cancel"));
        }
        if (order.isShipped()) {
            links.add(Link.of("/api/v1/shipments/" + order.getShipmentId(), "track"));
        }
        if (order.isReturnable()) {
            links.add(linkTo(methodOn(OrderController.class)
                .returnOrder(id, null)).withRel("return"));
        }
        
        return EntityModel.of(dto, links);
    }
}

// Response (HAL format):
// Accept: application/hal+json
// {
//   "id": "ORD-789",
//   "status": "PENDING",
//   "_links": {
//     "self": { "href": "http://api.example.com/api/v1/orders/ORD-789" },
//     "cancel": { "href": "http://api.example.com/api/v1/orders/ORD-789/cancellations" }
//   }
// }
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
HATEOAS CLIENT NAVIGATION:

  1. GET /api/v1  (entry point)
     ← { _links: { orders: "/api/v1/orders", customers: "/api/v1/customers" }}

  2. GET /api/v1/orders (from link.orders)
     ← { _embedded: { orders: [...] }, _links: { self, next, create }}

  3. POST /api/v1/orders (from _links.create)
     ← 201 Created: { id: "ORD-999", status: "PENDING",
                       _links: { self, cancel, payment }}

  4. POST (cancel link from response) if order needs to be cancelled
     ← 200 OK { id: "ORD-999", status: "CANCELLED",  _links: { self }}

  Client never hardcoded: "/api/v1/orders/ORD-999/cancellations"
  All URLs came from server responses.
```

---

### 💻 Code Example

```java
// Collection resource with pagination links (HATEOAS + Pagination)
@GetMapping
public CollectionModel<EntityModel<OrderDto>> listOrders(
        @RequestParam(defaultValue = "0") int page,
        @RequestParam(defaultValue = "20") int size) {

    Page<Order> orders = orderService.findAll(PageRequest.of(page, size));

    List<EntityModel<OrderDto>> orderModels = orders.getContent().stream()
        .map(order -> EntityModel.of(toDto(order),
            linkTo(methodOn(OrderController.class).getOrder(order.getId())).withSelfRel()
        ))
        .collect(Collectors.toList());

    List<Link> collectionLinks = new ArrayList<>();
    collectionLinks.add(linkTo(methodOn(OrderController.class)
        .listOrders(page, size)).withSelfRel());

    if (orders.hasNext()) {
        collectionLinks.add(linkTo(methodOn(OrderController.class)
            .listOrders(page + 1, size)).withRel("next"));
    }
    if (orders.hasPrevious()) {
        collectionLinks.add(linkTo(methodOn(OrderController.class)
            .listOrders(page - 1, size)).withRel("prev"));
    }

    return CollectionModel.of(orderModels, collectionLinks);
}
```

---

### ⚖️ Comparison Table

| Approach | URL Coupling | Server Controls State | Client Complexity | Industry Adoption |
|---|---|---|---|---|
| **HATEOAS (Level 3 REST)** | Low (follows links) | ✅ Full | Higher (must follow links) | Low |
| **Level 2 REST (no HATEOAS)** | Medium (knows URL patterns) | ❌ Client duplicates state | Lower | Very high |
| **GraphQL** | None | Partial (schema-driven) | Medium | Medium |
| **RPC (gRPC)** | High (hardcoded methods) | ❌ | Low | High (microservices) |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| HATEOAS eliminates all coupling | Clients still need to know link relation names (e.g., "cancel", "approve"). Coupling shifts from URL-coupling to rel-coupling — still coupling, just more stable |
| Most REST APIs are Level 3 RESTful | Almost none. Most production "REST APIs" are Level 2 (resources + HTTP verbs). HATEOAS is academically pure REST but rarely implemented fully in practice |
| HATEOAS is only about URLs | The deeper benefit is server-controlled state transitions: which actions are available is driven by server-side business rules, not client-side conditionals |

---

### 🚨 Failure Modes & Diagnosis

**Client Hardcodes Link URL Instead of Following Rel**

Symptom:
HATEOAS API deployed. Client team "follows links" but hardcodes the href value from
the first API call: `const cancelUrl = "/api/v1/orders/" + id + "/cancellations"`.
URL changes. Client breaks. HATEOAS provided no benefit.

Root Cause:
Team didn't follow the HATEOAS philosophy. Links must be treated as OPAQUE — client
follows `_links.cancel.href`, not constructs it independently.

Fix:
```javascript
// ❌ Hardcoding the pattern:
const cancelUrl = `/api/v1/orders/${orderId}/cancellations`;

// ✅ Following the link from response:
const orderResponse = await fetch(`/api/v1/orders/${orderId}`);
const order = await orderResponse.json();
if (order._links?.cancel) {
    const cancelResponse = await fetch(order._links.cancel.href, {method: 'POST'});
}
// URL can change server-side; client is unaffected
```

---

### 🔗 Related Keywords

- `REST` — Roy Fielding's original constraints include HATEOAS as a requirement for "true REST"
- `Richardson Maturity Model` — levels 0-3 with HATEOAS at level 3
- `API Design Best Practices` — most practical REST APIs stop at Level 2
- `HAL` — Hypertext Application Language: standard format for HATEOAS links

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ API responses include _links for available│
│              │ next actions; clients follow, not construct│
├──────────────┼───────────────────────────────────────────┤
│ HAL FORMAT   │ _links: { self, cancel, track, return }   │
│              │ href + conditional presence = state control│
├──────────────┼───────────────────────────────────────────┤
│ KEY BENEFIT  │ Server controls available actions via     │
│              │ conditional link inclusion                │
├──────────────┼───────────────────────────────────────────┤
│ SPRING       │ EntityModel.of(dto, links) → HAL response │
├──────────────┼───────────────────────────────────────────┤
│ REALITY CHECK│ Level 3 REST — academically pure,        │
│              │ rarely fully implemented in production    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "API as hypertext: follow links, not URLs"│
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q.** Fielding famously wrote "What needs to be done to make the REST architectural style
clear on the notion that hypertext is a constraint? What part of 'hypertext as the engine
of application state' was unclear?" in a 2008 blog post criticizing APIs being called REST
without HATEOAS. Yet virtually no production API implements HATEOAS fully. Is this because
the industry is wrong, or because Fielding's purity constraint doesn't align with practical
engineering economics? Argue both sides, then make a specific recommendation: when in
a real product should a team invest in HATEOAS, and when is Level 2 REST sufficient?
