---
layout: default
title: "HATEOAS"
parent: "HTTP & APIs"
nav_order: 215
permalink: /http-apis/hateoas/
number: "215"
category: HTTP & APIs
difficulty: ★★★
depends_on: RESTful Constraints, REST, HTTP Headers, HTTP Status Codes
used_by: API Design Best Practices, API Backward Compatibility, Hypermedia
tags:
  - networking
  - protocol
  - http
  - rest
  - architecture
  - deep-dive
---

# 215 — HATEOAS

`#networking` `#protocol` `#http` `#rest` `#architecture` `#deep-dive`

⚡ TL;DR — The REST constraint requiring API responses to include hypermedia links to available actions, so clients navigate the API dynamically rather than hardcoding URLs.

| #215 | Category: HTTP & APIs | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | RESTful Constraints, REST, HTTP Headers, HTTP Status Codes | |
| **Used by:** | API Design Best Practices, API Backward Compatibility, Hypermedia | |

---

### 📘 Textbook Definition

**HATEOAS (Hypermedia As The Engine Of Application State)** is one of the four sub-constraints of REST's Uniform Interface requirement, defined by Roy Fielding. It requires that API responses include hypermedia controls — links or forms — that describe available actions in the current application state. Clients discover available operations from the server's responses rather than having them hardcoded in the client. This mirrors how browsers navigate the web: you visit a page (resource) and the page tells you what you can do next (links and forms). When a client follows links from the entry-point without prior knowledge of other URLs, it is said to be "hypertext-driven." HATEOAS is the most debated and least implemented REST constraint in practice.

### 🟢 Simple Definition (Easy)

HATEOAS means an API response includes links telling you what you can do next — like a web page with clickable links — so you don't need to know the API upfront.

### 🔵 Simple Definition (Elaborated)

When you browse a website, each page shows you links to related pages. You start at the home page and navigate wherever you want without memorising every URL. HATEOAS applies this to APIs: a response for a user resource includes links for "view orders," "update details," "delete account." The client doesn't hardcode these URLs — it reads them from each response. The benefit: if the server changes a URL, the client still works because it follows the links the server provides. The drawback: it's complex to implement correctly, clients must understand the link semantics, and most frontend JavaScript clients don't actually use the hypermedia controls.

### 🔩 First Principles Explanation

**Fielding's concern — why he defined HATEOAS:**

Standard "REST" APIs require clients to have out-of-band knowledge: the client knows that `GET /users/{id}/orders` lists orders for a user, that `DELETE /users/{id}` removes a user, and what all the URL patterns are. This knowledge is hardcoded in the client. When the server changes a URL, or when new operations become available, every client must be updated.

Fielding argued that a truly REST API should function like the web: a client starts with one known entry-point URL and discovers everything else from hypermedia controls embedded in responses. The server has full control over navigation — changing URLs or adding/removing operations requires no client updates.

**State machine interpretation:**

"Engine of Application State" means the application's current state determines what transitions are available. An ORDER resource in "pending" state offers "confirm" and "cancel" links; in "shipped" state, only "track" is offered. The current state drives what the client can do next — the server encodes this in the response links.

**Implementation formats:**

```
HAL (Hypertext Application Language):
{
  "_links": {
    "self": {"href": "/orders/42"},
    "user":  {"href": "/users/7"},
    "cancel": {"href": "/orders/42/cancellations",
               "type": "POST"}
  },
  "id": 42,
  "status": "pending",
  "total": 99.99
}

JSON:API:
{
  "data": {
    "id": "42", "type": "orders",
    "attributes": {"status": "pending", "total": 99.99},
    "relationships": {
      "user": {"links": {"related": "/users/7"}}
    },
    "links": {"self": "/orders/42"}
  }
}

Spring HATEOAS EntityModel:
{
  "id": 42,
  "status": "pending",
  "_links": {
    "self": {"href": "http://api.example.com/orders/42"},
    "cancel": {"href": "http://api.example.com/orders/42/cancel"}
  }
}
```

**The discoverability principle:**

```
Client Entry Point: GET https://api.example.com/
→ Response:
{
  "_links": {
    "users":  {"href": "/users"},
    "orders": {"href": "/orders"},
    "products": {"href": "/products"}
  }
}
→ Client discovers ALL API resources from the root
→ Never hardcodes /users or /orders
```

### ❓ Why Does This Exist (Why Before What)

WITHOUT HATEOAS:

- Client hardcodes URL templates: `/users/{id}`, `/orders/{id}/cancel`.
- Server URL refactoring breaks all deployed clients.
- Client must consult documentation to know available states/transitions for a resource.
- Adding new operations requires coordinated client+server deployments.

What breaks without it:
1. URL changes break all clients — "URL as public API contract" makes servers inflexible.
2. Clients can't dynamically adapt to a resource's current state without server-side knowledge.

WITH HATEOAS:
→ Clients discover operations from responses — URL changes require only server updates.
→ State-appropriate links automatically guide clients through valid transitions.
→ Self-documenting responses for generic hypermedia clients.

### 🧠 Mental Model / Analogy

> HATEOAS is how you navigate an unfamiliar city without a map. You start at the airport (entry-point URL), find signs to the train station (embedded links), take the train, see signs to the hotel district (more links), walk to your hotel, and find the check-in desk signs (following links to sub-resources). Each location tells you where to go next — you never memorised the city layout upfront. Compare this to hardcoding routes: writing down every street address before departure and following only that list (no HATEOAS).

"Airport" = entry-point URL, "signs" = hypermedia links in responses, "navigating" = following links, "pre-written address list" = hardcoded client URL knowledge.

### ⚙️ How It Works (Mechanism)

**State-driven link availability:**

```
Order Resource — State Machine:
PENDING   → links: {confirm, cancel, update}
CONFIRMED → links: {ship, cancel}
SHIPPED   → links: {track, deliver}
DELIVERED → links: {return, review}
CANCELLED → links: {}  (no transitions from cancelled)

Response for PENDING order:
{
  "id": 42, "status": "PENDING", "total": 99.99,
  "_links": {
    "self":    {"href": "/orders/42"},
    "confirm": {"href": "/orders/42/confirm", "method":"POST"},
    "cancel":  {"href": "/orders/42/cancel",  "method":"POST"},
    "update":  {"href": "/orders/42",          "method":"PUT"}
  }
}

Response for SHIPPED order:
{
  "id": 42, "status": "SHIPPED",
  "_links": {
    "self":  {"href": "/orders/42"},
    "track": {"href": "/orders/42/tracking"}
    // "cancel" NOT present — can't cancel a shipped order
  }
}
```

**Client logic with HATEOAS:**

```java
// GOOD: Client follows links, doesn't hardcode
OrderResponse order = apiClient.get("/orders/42");
Link cancelLink = order.getLinks().getLink("cancel");
if (cancelLink.isPresent()) {
    apiClient.post(cancelLink.getHref()); // follows server-provided URL
} else {
    log.info("Order cannot be cancelled in current state");
}

// BAD: Client hardcodes URL — coupled to server URL structure
apiClient.post("/orders/42/cancel"); // breaks if URL changes
```

### 🔄 How It Connects (Mini-Map)

```
REST (Architectural style)
        ↓ 4th sub-constraint of Uniform Interface
HATEOAS ← you are here
  (hypermedia links drive application state)
        ↓ implemented by
HAL | JSON:API | Spring HATEOAS
        ↓ enables
API Backward Compatibility
Hypermedia API design
        ↓ often skipped in favour of
OpenAPI / Swagger (documentation replaces discoverability)
```

### 💻 Code Example

Example 1 — Spring HATEOAS implementation:

```java
import org.springframework.hateoas.*;
import static org.springframework.hateoas.server.mvc.WebMvcLinkBuilder.*;

@RestController
@RequestMapping("/orders")
public class OrderController {

    @GetMapping("/{id}")
    public EntityModel<OrderDto> getOrder(
            @PathVariable Long id) {
        Order order = orderService.findById(id);
        OrderDto dto = toDto(order);

        EntityModel<OrderDto> model =
            EntityModel.of(dto);
        model.add(
            linkTo(methodOn(OrderController.class)
                .getOrder(id)).withSelfRel()
        );

        // State-conditional links
        if (order.getStatus() == PENDING) {
            model.add(
                linkTo(methodOn(OrderController.class)
                    .cancelOrder(id, null))
                    .withRel("cancel"),
                linkTo(methodOn(OrderController.class)
                    .confirmOrder(id))
                    .withRel("confirm")
            );
        }
        if (order.getStatus() == SHIPPED) {
            model.add(
                linkTo(methodOn(TrackingController.class)
                    .getTracking(id))
                    .withRel("tracking")
            );
        }
        return model;
    }
}
```

Example 2 — HAL response format:

```json
{
  "id": 42,
  "status": "PENDING",
  "total": 99.99,
  "createdAt": "2026-05-02T10:00:00Z",
  "_links": {
    "self": {
      "href": "https://api.example.com/orders/42"
    },
    "user": {
      "href": "https://api.example.com/users/7"
    },
    "confirm": {
      "href": "https://api.example.com/orders/42/confirm",
      "title": "Confirm this order"
    },
    "cancel": {
      "href": "https://api.example.com/orders/42/cancellations",
      "title": "Cancel this order"
    }
  }
}
```

Example 3 — API entry-point discovery:

```java
@GetMapping("/")
public RepresentationModel<?> entryPoint() {
    RepresentationModel<?> model = new RepresentationModel<>();
    model.add(
        linkTo(UserController.class).withRel("users"),
        linkTo(OrderController.class).withRel("orders"),
        linkTo(ProductController.class).withRel("products")
    );
    return model;
}
// Response: {"_links":{"users":{"href":"/users"},
//             "orders":{"href":"/orders"},...}}
```

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| HATEOAS is optional in a RESTful API | Fielding explicitly stated HATEOAS is part of the Uniform Interface constraint — required for true REST. However, most practitioners treat it as optional due to implementation complexity. |
| HATEOAS means clients never need documentation | HATEOAS enables navigation without URL knowledge, but clients need to understand link relation names (semantics like "cancel", "confirm") which require documentation or standards. |
| Including links in responses automatically makes an API RESTful | HATEOAS is one of four Uniform Interface sub-constraints and one of six total REST constraints. Adding links doesn't make an API REST-compliant without the other constraints. |
| HATEOAS is only useful for Level 3 Richardson APIs | HATEOAS is most valuable for APIs with complex state machines (e.g., orders, workflows) where available operations change with state. Simple CRUD APIs benefit less. |
| Spring HATEOAS implements full HATEOAS | Spring HATEOAS provides link-building utilities but doesn't enforce that clients use the links — client-side adoption is required for the contract benefit. |

### 🔥 Pitfalls in Production

**1. Static Links Regardless of Resource State**

```java
// BAD: Same links for all states — includes invalid transitions
EntityModel<Order> model = EntityModel.of(order);
model.add(linkTo(...cancelOrder(id)).withRel("cancel"));
model.add(linkTo(...confirmOrder(id)).withRel("confirm"));
// Both links shown even for CANCELLED orders → client calls fail

// GOOD: Only add state-appropriate links
if (order.canBeCancelled()) {
    model.add(linkTo(...cancelOrder(id)).withRel("cancel"));
}
if (order.canBeConfirmed()) {
    model.add(linkTo(...confirmOrder(id)).withRel("confirm"));
}
```

**2. Including Absolute URLs with Hardcoded Hostname**

```java
// BAD: Hardcoded URL in links breaks in multiple environments
Link link = Link.of("https://prod.example.com/orders/42");

// GOOD: Use Spring HATEOAS link builders (request-relative)
Link link = linkTo(methodOn(OrderController.class)
    .getOrder(id)).withSelfRel();
// Generates correct URL based on current request's host
```

**3. Implementing HATEOAS Without a Standard Format (Inventing Your Own)**

```json
// BAD: Invented link format — no tooling support
{
  "actions": [
    {"type": "cancel", "endpoint": "/cancel/42", "verb": "POST"}
  ]
}

// GOOD: Use HAL, JSON:API, or Siren standards
{
  "_links": {
    "cancel": {"href": "/orders/42/cancel"}
  }
}
// HAL is well-supported in Spring HATEOAS, clients, and API explorers
```

### 🔗 Related Keywords

- `RESTful Constraints` — HATEOAS is one of four Uniform Interface sub-constraints.
- `REST` — the architectural style HATEOAS is a core part of.
- `Hypermedia` — the broader concept of which HATEOAS is one application.
- `API Backward Compatibility` — HATEOAS reduces breaking changes by decoupling clients from URLs.
- `OpenAPI / Swagger` — the documentation-centric alternative to HATEOAS for API discoverability.
- `API Design Best Practices` — whether to implement HATEOAS is a frequent design discussion.

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Response links drive navigation: clients  │
│              │ follow links rather than hardcoding URLs. │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Complex state machines (orders, workflows)│
│              │ where available ops vary by current state.│
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Simple CRUD APIs; no budget for full      │
│              │ implementation; clients ignore links.     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "HATEOAS: the server gives you a map;    │
│              │ you follow signs, not memorised routes."  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Hypermedia → API Backward Compatibility → │
│              │ OpenAPI / Swagger                         │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A flight booking API implements HATEOAS. A flight search result response includes `"book": {"href": "/flights/LAX-LHR/20260710/seats/23A/booking", "method": "POST"}`. The client stores this link and attempts to use it 20 minutes later, but the seat was sold to another user and the link now returns 409 Conflict. Does this behaviour violate or fulfil the HATEOAS contract? What does it reveal about the interaction between HATEOAS, temporal validity of hypermedia controls, and the need for client-side link expiry handling?

**Q2.** Fielding wrote that without HATEOAS, "what you have is not REST" yet the vast majority of production APIs called "RESTful" don't implement it. Analyse the practical adoption barrier: what would a JavaScript SPA framework need to implement to be a true hypermedia client, why this conflicts with how modern frontend frameworks (React, Next.js) think about data fetching, and describe a specific real-world API domain (not e-commerce) where HATEOAS provides irreplaceable value that static documentation cannot replicate.

