---
layout: default
title: "API Documentation"
parent: "HTTP & APIs"
nav_order: 255
permalink: /http-apis/api-documentation/
number: "0255"
category: HTTP & APIs
difficulty: ★☆☆
depends_on: OpenAPI/Swagger, REST
used_by: API Consumers, Developer Portals, SDK Generation
related: OpenAPI/Swagger, API Design Best Practices, API Contract Testing
tags:
  - api
  - documentation
  - developer-experience
  - swagger-ui
  - beginner
---

# 255 — API Documentation

⚡ TL;DR — API documentation is the written and interactive material that tells developers how to use an API: what endpoints exist, what parameters they accept, what responses they return, how to authenticate, and what errors to expect — ranging from auto-generated OpenAPI/Swagger UI to hand-crafted guides, code samples, and developer portals.

┌──────────────────────────────────────────────────────────────────────────┐
│ #255 │ Category: HTTP & APIs │ Difficulty: ★☆☆ │
├──────────────┼────────────────────────────────────┼──────────────────────┤
│ Depends on: │ OpenAPI/Swagger, REST │ │
│ Used by: │ API Consumers, Developer Portals, │ │
│ │ SDK Generation │ │
│ Related: │ OpenAPI/Swagger, API Design Best │ │
│ │ Practices, API Contract Testing │ │
└──────────────────────────────────────────────────────────────────────────┘

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A developer wants to integrate with your API. They find the endpoint URL but no docs.
They email your team: "What parameters does `/api/orders` accept?" Three days later
they get a partial reply. They still don't know what `status` field values are possible,
what the error response body looks like, or whether the endpoint is paginated.
They write fragile integration code based on guesswork. It fails in production with
a 422 they didn't handle. Integration takes 2 weeks instead of 2 hours.
Bad API documentation is consistently ranked as the top developer experience complaint.

---

### 📘 Textbook Definition

**API Documentation** is the set of materials — reference documentation, conceptual
guides, tutorials, code examples, and interactive tools — that enable developers to
understand, integrate, and use an API effectively. It encompasses:
(1) **Reference documentation**: auto-generated or manually authored list of endpoints,
request/response schemas, authentication requirements (often via OpenAPI/Swagger UI).
(2) **Conceptual guides**: tutorials, "getting started" flows, authentication flows,
use-case walkthroughs. (3) **Code examples**: working snippets in multiple languages
(Java, Python, JavaScript, curl). (4) **Interactive console**: (Swagger UI, Postman,
Redoc Try-it-now) enabling developers to make live API calls from the documentation.
(5) **Changelog**: history of API changes, deprecations, and breaking change notices.
Good API documentation is accurate (matches implementation), discoverable, current,
and example-rich.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
API documentation is the instruction manual for your API — without it, developers
can't integrate, and with poor documentation, they integrate incorrectly.

**One analogy:**

> API documentation is like IKEA assembly instructions.
> Without them: customers stare at a pile of parts (endpoints, headers, JSON fields)
> with no idea how they fit together.
> Good instructions: step-by-step, with pictures (code examples), diagrams (authentication flows),
> and what to do when part B won't fit slot C (error handling guide).
> The product (API) might be great — but documentation determines whether customers successfully
> build what they want.

**One insight:**
The most impactful improvement to developer time-to-first-successful-API-call is not
performance — it's documentation quality. Stripe (widely regarded as best-in-class API)
is often cited not for technical superiority but because their documentation is exceptional:
live code samples, every language, every error code explanations, tutorials for every use case.

---

### 🔩 First Principles Explanation

**DOCUMENTATION LAYERS:**

```
PYRAMID OF API DOCUMENTATION:

  1. REFERENCE (foundation):
     Auto-generated from OpenAPI spec:
     - All endpoints listed
     - Request parameters (name, type, required, example)
     - Response schemas (all fields, types, examples)
     - HTTP status codes (200, 201, 400, 401, 403, 422, 429, 500)
     - Authentication requirements
     Tools: Swagger UI, Redoc, Stoplight Elements

  2. CONCEPTUAL GUIDES:
     Written by humans:
     - "Getting Started in 5 minutes"
     - "Authentication guide" (OAuth2 flow diagrams)
     - "Handling errors" (what each error code means + how to respond)
     - "Webhooks guide" (setup, verification, retry behavior)
     - "Pagination guide" (with examples)

  3. TUTORIALS / RECIPES:
     Use-case-driven examples:
     - "Process a payment end-to-end" (3-step walkthrough)
     - "Import 10,000 products" (bulk import with pagination)
     - "Subscribe to real-time events" (webhook registration + handling)

  4. CODE EXAMPLES:
     In every major language (Java, Python, JS/Node, Go, Ruby):
     - "Create a customer" in 6 languages
     - SDKs are generated from OpenAPI spec

  5. CHANGELOG + DEPRECATION NOTICES:
     - Every version change documented
     - Deprecated fields marked + migration guide
     - Breaking changes: prominent notice + migration steps
```

**OPENAPI → BEAUTIFUL DOCS:**

```
OpenAPI YAML spec
       │
       ├──→ Swagger UI (interactive, try-it-now console)
       │                  └── /swagger-ui.html in Spring Boot app
       │
       ├──→ Redoc (read-only, professionally styled, left-nav)
       │                  └── Better for public developer portals
       │
       ├──→ Stoplight Elements (embeddable, modern UI)
       │
       └──→ Postman Collection import (OpenAPI → Postman workspace)
                          └── Team shares ready-to-use requests
```

---

### 🧪 Thought Experiment

**SCENARIO:** Two APIs with identical functionality. Compare developer experience.

```
API A (poor documentation):
  - Reference page lists endpoints, no examples
  - Authentication section: "Use Bearer token" (no flow diagram, no code example)
  - Errors: "Returns standard HTTP errors"
  - No changelog
  - No SDK

  Developer experience:
  → How do I get a token? (asks on Slack, waits 1 day)
  → What does 422 look like? (trial and error, 2 hours)
  → What fields are required? (sends request, reads error, repeat)
  → Time-to-first-call: 3 days

API B (excellent documentation — Stripe-level):
  - Interactive console (Swagger UI / live try-it)
  - Authentication: OAuth2 flow diagram + curl example + Java snippet
  - Every endpoint: example request + example response (realistic data)
  - Every error code: name, description, what it means, how to handle
    "422 INVALID_CARD_NUMBER: The card number failed Luhn check.
     Prompt user to re-enter card details."
  - Getting started guide: working end-to-end example in 15 minutes
  - Changelog with migration guides
  - SDK: stripe-java, stripe-python auto-generated from spec

  Developer experience:
  → Follows Getting Started guide, first call works in 30 minutes
  → Time-to-production-integration: 2 hours
```

---

### 🧠 Mental Model / Analogy

> API documentation is the developer onboarding contract.
> It promises: "If you follow these steps, you'll succeed."
> Every gap in the documentation is a broken promise:
> a developer's time wasted figuring out what should have been written down.
> The best API docs make the developer feel guided and successful fast —
> with examples so clear that copying a snippet gets them to their first working call
> in under 15 minutes.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is:**
API documentation tells developers how to use your API: what to call, what to send,
and what to expect back. Without it, no one can use the API correctly.

**Level 2 — How to use it:**
Spring Boot + Springdoc: auto-generates Swagger UI at `/swagger-ui.html`. Add
`@Operation(summary = "...")`, `@Schema(description = "...", example = "...")` annotations
to enrich the auto-generated docs. Write `README.md` and conceptual guides separately.
Expose realistic examples in your OpenAPI spec's `example` fields.

**Level 3 — How it works:**
Springdoc scans Spring MVC annotations → builds OpenAPI 3.x spec → serves JSON at
`/v3/api-docs`. Swagger UI fetches this spec and renders interactive UI. Redoc renders
a read-only styled view better suited for external developer portals. For accuracy:
keep the spec as the single source of truth — test example code snippets in CI to
prevent them from going stale. Developer portals (Stoplight, Readme.com, Mintlify)
layer conceptual content and tutorials above the raw OpenAPI spec.

**Level 4 — Why it was designed this way:**
API documentation ROI is asymmetric: good docs reduce support burden, accelerate
partner integrations, and reduce bugs from misuse. Stripe reports that documentation
investment correlates directly with developer satisfaction scores and time-to-integrated.
The OpenAPI spec is the foundation because it's machine-readable (enables SDK generation,
contract testing, linting) AND human-readable. The split between reference docs (from spec)
and conceptual docs (human-written) reflects the two jobs: "what is this parameter?" (spec)
vs. "how do I accomplish X?" (guide). The biggest operational risk: documentation drift
— spec says one thing, implementation does another. Contract testing (Pact, Dredd) in CI
is the mechanism to prevent drift. Developer portal products (Readme.com, Mintlify)
have evolved to host both spec-generated reference AND versioned conceptual content
with integrated changelog management.

---

### ⚙️ How It Works (Mechanism)

```
SPRING BOOT DOCUMENTATION PIPELINE:

  Code + Annotations
        │
        ├── @Tag, @Operation, @ApiResponse, @Schema in controllers/models
        │
        ▼
  Springdoc-OpenAPI (at startup): scans → builds OpenAPI 3.x object
        │
        ├── GET /v3/api-docs → raw OpenAPI JSON
        │
        ├── GET /swagger-ui.html → Swagger UI (interactive)
        │
        └── GET /v3/api-docs.yaml → OpenAPI YAML (for Redoc, Postman import)

  External Developer Portal:
  openapi.yaml → Redoc → public developer portal page
             → Postman workspace (import collection)
             → SDK generation (openapi-generator)
             → Contract tests (Dredd runs spec against live API)
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
DOCUMENTATION WORKFLOW (design-first):

  1. Write openapi.yaml spec (reviewed by team)

  2. Generate: Swagger UI (internal dev)
               Redoc    (external partners)
               SDK (openapi-generator: Java, Python, TypeScript)

  3. Write conceptual docs:
     README.md → "Getting Started"
     AUTHENTICATION.md → OAuth2 flow diagram + curl examples
     ERRORS.md → all error codes + handling guides
     CONCEPTS.md → "how pagination works" + examples
     CHANGELOG.md → all changes, breaking + non-breaking, migration guide

  4. Host on developer portal (Readme.com / Mintlify / Stoplight):
     Spec reference + conceptual docs + changelog → single searchable portal

  5. CI validation:
     Spectral: lint spec quality (all ops have summary, all 4xx documented)
     Dredd: examples in spec match live API behavior
     → Documentation accuracy enforced in CI
```

---

### 💻 Code Example

```java
// Rich Springdoc annotations for complete documentation
@RestController
@Tag(name = "Payments", description = "Payment processing endpoints")
@RequestMapping("/api/v1/payments")
public class PaymentController {

    @Operation(
        summary = "Create a payment",
        description = """
            Creates a new payment transaction.
            Idempotent: include `Idempotency-Key` header to safely retry.
            Returns 201 on success; 402 if payment declined.
            """
    )
    @ApiResponses({
        @ApiResponse(responseCode = "201", description = "Payment created successfully",
            content = @Content(schema = @Schema(implementation = PaymentResponse.class))),
        @ApiResponse(responseCode = "402", description = "Payment declined",
            content = @Content(schema = @Schema(implementation = ErrorResponse.class),
                examples = @ExampleObject(value = """
                    {"code": "CARD_DECLINED", "message": "Insufficient funds",
                     "declineCode": "insufficient_funds"}
                """))),
        @ApiResponse(responseCode = "422", description = "Validation error"),
        @ApiResponse(responseCode = "429", description = "Rate limit exceeded")
    })
    @PostMapping
    public ResponseEntity<PaymentResponse> createPayment(
            @Parameter(description = "Idempotency key for safe retries",
                       example = "550e8400-e29b-41d4-a716-446655440000")
            @RequestHeader(value = "Idempotency-Key", required = false) String idempotencyKey,
            @RequestBody @Valid CreatePaymentRequest request) {
        // implementation
    }
}

@Schema(description = "Payment creation request")
public class CreatePaymentRequest {

    @Schema(description = "Payment amount in smallest currency unit (cents)",
            example = "9999",
            minimum = "1")
    @NotNull @Min(1)
    private Long amount;

    @Schema(description = "ISO 4217 currency code",
            example = "USD",
            allowableValues = {"USD", "EUR", "GBP"})
    @NotBlank
    private String currency;
}
```

---

### ⚖️ Comparison Table

| Tool                   | Best For              | Interactive   | Styling      | Hosting     |
| ---------------------- | --------------------- | ------------- | ------------ | ----------- |
| **Swagger UI**         | Development/internal  | ✅ Try-it-now | Basic        | Self-hosted |
| **Redoc**              | External/public docs  | ❌ Read-only  | Professional | Self-hosted |
| **Stoplight Elements** | Embeddable            | ✅            | Modern       | Self-hosted |
| **Readme.com**         | Developer portal      | ✅            | Custom       | SaaS        |
| **Mintlify**           | Modern developer docs | ✅            | Excellent    | SaaS        |
| **Postman**            | API testing + docs    | ✅            | Good         | Cloud       |

---

### ⚠️ Common Misconceptions

| Misconception                         | Reality                                                                                                                                                        |
| ------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Auto-generated docs are sufficient    | Auto-generated reference covers WHAT. Developers also need WHY and HOW: guides, tutorials, error handling explanations — all human-written                     |
| Documentation can be added at the end | Docs written after the fact are always incomplete. Design-first (spec → implementation) produces better documentation because the contract is reviewed upfront |
| Only public APIs need documentation   | Internal APIs need documentation too. If another team can't understand your API without asking you directly, documentation is missing                          |

---

### 🚨 Failure Modes & Diagnosis

**Documentation Drift (Stale Docs)**

Symptom:
Swagger UI shows `amount` as a string. Real API returns `amount` as an integer (numeric).
Consumer writes `Long.parseLong(response.getAmount())` → works in test, breaks with
actual integer response.

Diagnostic:

```bash
# Use Dredd to validate spec examples match live API:
dredd openapi.yaml http://localhost:8080

# Output: PASS or FAIL for each operation
# FAIL: GET /api/payments/1
#   Expected: {"amount": "9999"} (spec example)
#   Actual:   {"amount": 9999}   (live response)
# → Fix: update schema type from string to integer in spec

# Spectral: check for missing examples in spec:
spectral lint openapi.yaml
# Warning: operation GET /payments/{id} missing response example
# → Add `example:` fields to all response properties
```

---

### 🔗 Related Keywords

- `OpenAPI/Swagger` — the specification standard that powers reference documentation generation
- `API Design Best Practices` — documentation is part of API design quality
- `API Contract Testing` — validates that documentation matches implementation
- `Developer Experience (DX)` — documentation is the highest-impact DX factor

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Reference + guides + examples enabling    │
│              │ developers to integrate successfully      │
├──────────────┼───────────────────────────────────────────┤
│ LAYERS       │ 1. Reference (auto from OpenAPI spec)     │
│              │ 2. Conceptual guides (human-written)      │
│              │ 3. Tutorials / use-case examples          │
│              │ 4. Error code explanations                │
│              │ 5. Changelog + migration notices          │
├──────────────┼───────────────────────────────────────────┤
│ SPRING BOOT  │ Springdoc → /swagger-ui.html             │
│              │ /v3/api-docs (machine-readable)           │
├──────────────┼───────────────────────────────────────────┤
│ QUALITY GATE │ Dredd (spec vs live) in CI               │
│              │ Spectral (spec linting) in CI             │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "If devs ask how to use it, docs failed" │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ OpenAPI/Swagger → API Design Best Prctcs │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q.** Your company is launching a public API. The developer experience team argues for
investing 40% of the launch sprint in documentation and developer tooling (portal, SDKs,
tutorials). The engineering manager says "write it later, ship the API first."
Using Stripe as a reference example, make the business and technical case for documentation-
first thinking. What is the measurable cost of poor documentation (support tickets,
integration time, partner churn), and what is the minimum viable documentation
set required to ship a public API responsibly?
