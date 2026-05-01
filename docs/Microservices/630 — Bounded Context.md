---
layout: default
title: "Bounded Context"
parent: "Microservices"
nav_order: 630
permalink: /microservices/bounded-context/
number: "630"
category: Microservices
difficulty: ★★★
depends_on: "Domain-Driven Design (DDD), Ubiquitous Language, Service Decomposition"
used_by: "Anti-Corruption Layer, Aggregate, Service Registry, Database per Service"
tags: #advanced, #architecture, #microservices, #pattern, #deep-dive
---

# 630 — Bounded Context

`#advanced` `#architecture` `#microservices` `#pattern` `#deep-dive`

⚡ TL;DR — A **Bounded Context** is the explicit boundary within which a specific domain model and its Ubiquitous Language apply. It is the primary DDD tool for defining microservice boundaries — one Bounded Context typically maps to one microservice.

| #630            | Category: Microservices                                                  | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Domain-Driven Design (DDD), Ubiquitous Language, Service Decomposition   |                 |
| **Used by:**    | Anti-Corruption Layer, Aggregate, Service Registry, Database per Service |                 |

---

### 📘 Textbook Definition

A **Bounded Context** is a linguistic boundary — a context within which the terms and concepts of the Ubiquitous Language have a specific, unambiguous meaning. The same word ("Customer," "Order," "Product") can mean entirely different things in different Bounded Contexts — and that divergence is intentional and correct. Each Bounded Context has its own domain model, its own data store (in microservices), its own team ownership, and its own deployment unit. Bounded Contexts interact via a **Context Map** — a diagram showing the relationships between contexts (Shared Kernel, Customer/Supplier, Conformist, Open/Host Service, Anti-Corruption Layer, Separate Ways). The relationship type determines integration patterns: Conformist = downstream adopts upstream's model; ACL = downstream translates the upstream model behind a protective layer; Shared Kernel = two contexts share a small, explicitly agreed-upon model fragment (dangerous, high coordination cost). In microservices architecture, the Bounded Context is the primary tool for identifying service boundaries: one context = one service (or a small cluster of tightly related services).

---

### 🟢 Simple Definition (Easy)

A Bounded Context is a clearly defined area of the system where a specific set of concepts and rules apply. Inside this boundary, everyone uses the same language. Outside this boundary, the same word might mean something different — and that is OK.

---

### 🔵 Simple Definition (Elaborated)

"Customer" means different things to different departments. To Sales, a customer is a prospect with a purchase history. To Support, a customer is a ticket owner with an SLA. To Billing, a customer is an account with payment methods and invoices. In a traditional monolith, all these meanings are crammed into one "Customer" class — a bloated compromise that satisfies no one well. Bounded Contexts say: each department gets its own "Customer" model, optimised for their needs. They share the customer's ID (to reference the same real-world person), but their models evolve independently. This is the core insight that enables microservices to be independently deployable.

---

### 🔩 First Principles Explanation

**Context Map patterns — how bounded contexts relate:**

```
┌─────────────────────────────────────────────────────────────────────┐
│ CONTEXT MAP RELATIONSHIP PATTERNS                                   │
│                                                                     │
│ SHARED KERNEL:                                                      │
│   Two contexts share a model fragment                               │
│   Context A ◄──SHARED MODEL──► Context B                           │
│   Risk: any change to shared model requires both teams to agree    │
│   Use: sparingly, only for stable, core identifiers                │
│                                                                     │
│ CUSTOMER/SUPPLIER:                                                  │
│   Upstream (supplier) defines the API                              │
│   Downstream (customer) must use it                                │
│   [ProductContext] ──upstream──► [OrderContext]                    │
│   Product team defines ProductAPI; Order team uses it              │
│                                                                     │
│ CONFORMIST:                                                         │
│   Downstream conforms to upstream's model, no translation          │
│   OrderContext uses ProductContext's model as-is                   │
│   Risk: OrderContext is tightly coupled to ProductContext's design  │
│                                                                     │
│ ANTI-CORRUPTION LAYER:                                              │
│   Downstream wraps upstream with a translation layer               │
│   [OrderContext] → [ACL] → [LegacyERP]                            │
│   Order context's model is protected from the legacy model         │
│                                                                     │
│ OPEN/HOST SERVICE + PUBLISHED LANGUAGE:                            │
│   Upstream publishes a well-defined, versioned API (like REST)    │
│   Many downstream contexts consume it                              │
│   [ProductService REST API] → N downstream consumers              │
│                                                                     │
│ SEPARATE WAYS:                                                      │
│   Two contexts have no integration — fully independent             │
│   [AuditContext] ◄── no connection ──► [RecommendationContext]    │
└─────────────────────────────────────────────────────────────────────┘
```

**Context isolation — the "Account" example across three contexts:**

```
BANKING DOMAIN — same concept "Account" in three contexts:

LENDING CONTEXT:
  Account = {loanId, principalAmount, interestRate, repaymentSchedule,
             missedPayments, delinquentStatus}
  Operations: applyForLoan(), makeRepayment(), issueDefault()

RETAIL BANKING CONTEXT:
  Account = {accountNumber, balance, transactionHistory, overdraftLimit}
  Operations: deposit(), withdraw(), transfer()

CUSTOMER RELATIONSHIP CONTEXT:
  Account = {customerId, contactInfo, productHoldings, lastInteractionDate}
  Operations: updateContactInfo(), recordInteraction(), assignAdvisor()

INTEGRATION:
  All three share AccountId (the customer's unique identifier)
  Cross-context queries go through APIs, not shared tables
  "Get all products for customer X" = CustomerRelationship asks Lending + Retail
  via their Open/Host Service APIs, not shared joins

Each context:
  - Has its own Account table (or no Account table, just the relevant fields)
  - Has its own team and deployment
  - Evolves independently: Lending adds 'delinquencyFlag', doesn't affect Retail
```

**Bounded Context sizing — how big should one context be?**

```
TOO FINE-GRAINED:
  Separate context for: OrderCreation, OrderModification, OrderCancellation
  → All three change together for every order feature
  → Chatty integration: OrderCreation calls OrderModification for every creation
  SIGN: contexts always deploy together, always change together

TOO COARSE-GRAINED:
  One "Commerce" context: orders + products + inventory + pricing + shipping
  → Large team required, many subdomain concerns in one model
  → "Product" means something different for inventory vs pricing
  SIGN: context has "God Object" entities, multiple teams working inside it

JUST RIGHT:
  One context per coherent subdomain:
  OrderManagement: one team, one subdomain, all order lifecycle logic
  Inventory: one team, stock levels, reservations, reorder triggers
  Pricing: one team, price calculation rules, promotions, discounts
  SIGN: single team can own the whole context, one team's changes rarely affect others
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Bounded Contexts:

What breaks without it:

1. Shared domain models grow without bound — every team adds their concerns to shared entities.
2. A database schema change for one team breaks other teams' queries.
3. No team has clear ownership — everyone must coordinate on shared models.
4. In a microservices context: services share databases, creating a distributed monolith.

WITH Bounded Contexts:
→ Each team owns a model that is exclusively theirs — no coordination needed for internal changes.
→ Integration is through stable, versioned APIs — not shared internal models.
→ "Product" can evolve differently in the Catalog context vs the Inventory context.
→ Service boundaries are principled, not arbitrary — grounded in the actual structure of the business domain.

---

### 🧠 Mental Model / Analogy

> A Bounded Context is like a sovereign nation's legal jurisdiction. Within France, French law applies. Within the UK, UK law applies. Both have a concept called "contract" — but a contract in French law and a contract in UK law are similar concepts with different specific meanings, rules, and enforcement mechanisms. A multinational corporation must translate between jurisdictions (Anti-Corruption Layer). There is no single global "contract" definition that satisfies both. Trying to create one (shared domain model across contexts) would be an oversimplification that satisfies neither jurisdiction perfectly.

"Sovereign nation's legal jurisdiction" = Bounded Context (own model, own rules)
"French law / UK law" = different domain models for the same concept
"Contract in French vs UK law" = "Order" in OrderContext vs BillingContext
"Translate between jurisdictions" = Anti-Corruption Layer
"Single global contract definition" = shared domain model anti-pattern

---

### ⚙️ How It Works (Mechanism)

**Translating between contexts with an ACL:**

```java
// OrderContext needs product information but must not depend on ProductContext's model
// Anti-Corruption Layer translates ProductContext's model to OrderContext's model

// ProductContext's model (owned by Product team):
record ProductDto(Long id, String sku, String name, BigDecimal listPrice,
                  String category, boolean active) {}

// OrderContext's internal model (what orders cares about):
record ProductSummary(ProductId id, String displayName, Money price) {}

// Anti-Corruption Layer in OrderContext:
@Component
class ProductContextAdapter {
    private final ProductServiceClient productClient; // generated from Product API

    public ProductSummary getProductForOrder(ProductId productId) {
        ProductDto externalDto = productClient.findById(productId.value());

        // Translation: ProductContext's model → OrderContext's model
        // Order context does NOT care about SKU, category, or active flag
        return new ProductSummary(
            productId,
            externalDto.name(),           // OrderContext calls it 'displayName'
            Money.of(externalDto.listPrice(), Currency.USD) // OrderContext uses Money VO
        );
    }
}

// OrderContext NEVER imports ProductDto — it only uses ProductSummary
// If Product team renames 'listPrice' to 'basePrice', only the ACL changes
// OrderContext's domain model is fully insulated
```

---

### 🔄 How It Connects (Mini-Map)

```
Domain-Driven Design (DDD)
        │
        ▼
Bounded Context  ◄──── (you are here)
(boundary where a specific model and language apply)
        │
        ├── Ubiquitous Language  → the language that applies within this context
        ├── Aggregate            → consistency boundaries within this context
        ├── Anti-Corruption Layer → protects this context from external models
        ├── Context Map          → documents how this context relates to others
        └── Database per Service → each context has its own data store
```

---

### 💻 Code Example

**Context Map as configuration — OpenAPI + code generation:**

```yaml
# openapi.yaml — Product Context's Published Language (Open/Host Service)
# This is the stable API contract that downstream contexts consume
openapi: "3.0.0"
info:
  title: "Product Catalog API"
  version: "2.1.0" # versioned for backward compatibility
paths:
  /products/{id}:
    get:
      operationId: getProduct
      parameters:
        - name: id
          in: path
          required: true
          schema: { type: integer, format: int64 }
      responses:
        "200":
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/ProductResponse"
components:
  schemas:
    ProductResponse:
      type: object
      properties:
        id: { type: integer }
        name: { type: string }
        listPrice: { type: number } # THIS is what downstream ACLs translate from
```

```java
// Order context generates client from Product's OpenAPI spec (never edits it)
// Order context's ACL wraps the generated client
// When Product team changes their API: regenerate client, update ACL translator only
```

---

### ⚠️ Common Misconceptions

| Misconception                                                       | Reality                                                                                                                                                                                                                                                                                     |
| ------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| One Bounded Context always equals exactly one microservice          | In practice, a very large Bounded Context may be split into 2-3 microservices for scalability, or a very small one may be grouped with a related context. The principle is: one bounded context should not SPAN multiple microservices (shared logic is a coupling smell)                   |
| Shared databases can still be used if contexts use separate schemas | Separate schemas in one database provide logical isolation but allow database-level joins (crossing the boundary). Cross-schema joins are a boundary violation. Separate databases are the strict enforcement; separate schemas are a pragmatic middle ground that can work with discipline |
| The Context Map is a one-time document                              | Context Maps evolve as the system grows. Contexts that start as Customer/Supplier relationships may become Separate Ways as they become more independent. Regular "re-mapping" sessions are part of DDD governance                                                                          |
| Bounded Contexts are only relevant for microservices                | Bounded Contexts are equally valuable in a modular monolith — they define module boundaries. DDD was designed for complex domain modelling regardless of deployment topology                                                                                                                |

---

### 🔥 Pitfalls in Production

**Shared Kernel creep — the hidden coupling**

```
INITIAL STATE: OrderContext and PaymentContext share a "Money" value object
  SharedKernel: Money {amount: BigDecimal, currency: Currency}

OVER TIME:
  Payment team adds: Money.toLedgerEntry() // for accounting
  Order team adds:   Money.applyDiscount() // for promotions
  Now SharedKernel.Money has dual concerns from two teams

  Payment team wants to change currency precision to 4 decimal places
  Order team relies on 2 decimal places for UI display
  → CONFLICT: shared kernel requires both teams to coordinate every change

BETTER APPROACH: Separate Money definitions per context
  OrderContext.Money: 2 decimal places, formatting for display
  PaymentContext.Money: 4 decimal places, accounting precision
  Integration: they exchange amounts as strings in API calls
               each context parses/formats per its own rules
```

---

### 🔗 Related Keywords

- `Domain-Driven Design (DDD)` — the philosophy that introduced Bounded Context as a strategic pattern
- `Ubiquitous Language` — the shared vocabulary that is bounded within a context
- `Anti-Corruption Layer` — the pattern for integrating between bounded contexts
- `Aggregate` — the tactical consistency boundary within a bounded context
- `Service Decomposition` — uses bounded contexts as the primary criterion for service boundaries

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ DEFINITION   │ Boundary where a specific domain model   │
│              │ and ubiquitous language apply            │
├──────────────┼───────────────────────────────────────────┤
│ MAPS TO      │ One microservice (usually)               │
│              │ One team ownership                        │
│              │ One data store                            │
├──────────────┼───────────────────────────────────────────┤
│ CONTEXT MAP  │ ACL (protect from external model)        │
│ PATTERNS     │ Conformist (adopt upstream model)        │
│              │ Open/Host Service (publish stable API)   │
│              │ Shared Kernel (shared fragment, risky)   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Boundary where 'Customer' means OUR     │
│              │  customer, not THEIR customer."         │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Eric Evans identifies "Context Map" smells that indicate a boundary is in the wrong place. Describe the two most common smells: (1) "Leaky abstraction" — when a downstream context imports and uses internal types from an upstream context directly (not via a published API) — what does this indicate about boundary health and what is the fix? (2) "Chatty contexts" — when Context A makes 5-10 API calls to Context B to complete a single operation — what does this indicate (A and B may be one context incorrectly split) and how do you diagnose whether to merge the contexts or add a Facade/BFF layer?

**Q2.** Bounded Contexts require each context to own its data — no cross-context database joins. But reporting and analytics often require data from multiple contexts (e.g., "revenue per product category" joins OrderContext and ProductContext data). Describe three architectural patterns for cross-context reporting: (1) the read model / CQRS approach where events from all contexts populate a reporting database, (2) the API composition approach where the reporting service calls multiple context APIs and joins in-memory, and (3) the data warehouse / data lake approach. For each, identify the consistency trade-off: when is the reporting data stale relative to operational data?
