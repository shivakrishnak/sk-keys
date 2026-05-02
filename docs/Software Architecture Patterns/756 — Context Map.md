---
layout: default
title: "Context Map"
parent: "Software Architecture Patterns"
nav_order: 756
permalink: /software-architecture/context-map/
number: "756"
category: Software Architecture Patterns
difficulty: ★★★
depends_on: "Bounded Context, Domain-Driven Design, Microservices"
used_by: "DDD strategy, Integration design, Service decomposition, Architecture review"
tags: #advanced, #architecture, #ddd, #integration, #strategy
---

# 756 — Context Map

`#advanced` `#architecture` `#ddd` `#integration` `#strategy`

⚡ TL;DR — A **Context Map** is a DDD strategic tool that explicitly documents how bounded contexts relate to each other — naming the relationship type (Partnership, Shared Kernel, Customer-Supplier, Conformist, ACL, Open Host, Published Language, Separate Ways) to make integration contracts and team dynamics visible.

| #756            | Category: Software Architecture Patterns                                     | Difficulty: ★★★ |
| :-------------- | :--------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Bounded Context, Domain-Driven Design, Microservices                         |                 |
| **Used by:**    | DDD strategy, Integration design, Service decomposition, Architecture review |                 |

---

### 📘 Textbook Definition

**Context Map** (Eric Evans, "Domain-Driven Design," 2003): a strategic design artifact in DDD that gives a global view of the project's bounded contexts and the relationships between them. A Context Map documents: (1) which bounded contexts exist in the system; (2) how they integrate (shared APIs, event contracts, shared databases); (3) the relationship TYPE between each pair of contexts — which determines the translation strategy, the team dynamic, and the risk of change propagation. The Context Map is not a UML diagram — it is a named, documented catalogue of integration relationships, each with an explicit pattern name and its implications for team autonomy and model translation.

---

### 🟢 Simple Definition (Easy)

A city's neighborhood map + diplomatic relations. Each neighborhood (bounded context) has its own laws (domain model). The map shows which neighborhoods border each other, and the NATURE of the relationship: allies (both change together), landlord/tenant (one controls, one conforms), foreign territory (we translate at the border). Without a map: developers assume everything integrates cleanly. With the map: "Order context and Shipping context have a Customer/Supplier relationship — Order is the supplier, Shipping conforms" — that tells you who can demand API changes.

---

### 🔵 Simple Definition (Elaborated)

An e-commerce platform has contexts: Order, Payment, Inventory, Shipping, Customer, Reporting. The Context Map documents: Order ↔ Payment: Partnership (teams coordinate closely). Order → Inventory: Customer/Supplier (Order demands inventory checks, Inventory provides API). Order → Shipping: Customer/Supplier. Order → CRM (external): Conformist (we adopt CRM's model as-is — we have no leverage). Order → Reporting: Published Language (Order publishes well-defined events; Reporting consumes them). Order ↔ Payment via ACL (Anti-Corruption Layer): Payment uses a different currency model — we translate at the boundary. This map makes integration risks, team autonomy, and model translation decisions explicit and visible.

---

### 🔩 First Principles Explanation

**The seven Context Map relationship patterns:**

```
CONTEXT MAP RELATIONSHIP PATTERNS (Evans):

1. PARTNERSHIP (both up-stream):
   ┌──────────┐  partnership  ┌──────────┐
   │  Order   │◄────────────►│  Payment │
   └──────────┘               └──────────┘

   Both teams coordinate closely. If Order changes its model, Payment must adapt
   simultaneously — and vice versa. Mutual dependence. Both succeed or both fail.

   Use when: two bounded contexts are so closely related that separate evolution
   is impossible without coordination. Typically: same team, or very close teams.

   Risk: tight coordination overhead. Both contexts evolve at the same pace.
   If teams lose alignment, partnership degrades.

2. SHARED KERNEL:
   ┌──────────┐  shared  ┌──────────┐
   │  Order   │◄─kernel─►│ Billing  │
   └──────────┘           └──────────┘
        shared: Money, CustomerId (explicit shared subdomain)

   A small, explicitly agreed-upon subset of the domain model is shared.
   Both teams own it jointly. Neither can change it without the other's agreement.

   Use when: duplication is clearly worse than the coordination cost.
   Risk: shared kernel becomes a bottleneck; changes require consensus.

3. CUSTOMER / SUPPLIER (upstream/downstream):
   ┌──────────┐  U/D  ┌──────────────┐
   │Inventory │──────►│   Order      │
   │(supplier)│       │  (customer)  │
   └──────────┘       └──────────────┘

   Upstream (supplier) provides an API. Downstream (customer) uses it.
   Downstream has NEGOTIATING POWER: can request changes to the upstream API.
   Upstream prioritizes downstream's needs.

   Use when: downstream has legitimate ability to influence upstream.
   Risk: upstream feels "owned" by downstream; multiple downstream customers
   with conflicting demands.

4. CONFORMIST:
   ┌──────────┐  conforms to  ┌──────────────────┐
   │  Portal  │──────────────►│  CRM (external)  │
   └──────────┘               └──────────────────┘

   Downstream adopts upstream's model as-is. No translation. No ACL.
   Downstream team has NO leverage to request changes (external vendor, legacy system).
   They simply accept whatever model the upstream provides.

   Use when: upstream won't/can't change; downstream cost of translation
   is higher than cost of adopting upstream model.
   Risk: upstream's model pollutes downstream's domain language.

5. ANTI-CORRUPTION LAYER (ACL):
   ┌──────────┐  ACL  ┌───────────────────┐  ┌──────────────────┐
   │  Order   │──────►│  OrderToSAP       │─►│  SAP (legacy)    │
   └──────────┘       │  Translator       │  └──────────────────┘
                      └───────────────────┘

   Downstream creates a translation layer (ACL) to protect its model from
   the upstream's model. The ACL converts upstream concepts to downstream concepts.

   Use when: upstream model would corrupt downstream if adopted directly
   (legacy system, different paradigm, external vendor).
   The ACL is an INVESTMENT: it adds complexity but preserves downstream model integrity.

6. OPEN HOST SERVICE + PUBLISHED LANGUAGE:
   ┌──────────┐  events  ┌──────────┐  events  ┌──────────────┐
   │  Order   │─────────►│Reporting │  event   │  Analytics   │
   └──────────┘          └──────────┘  schema  └──────────────┘
   (Open Host Service with Published Language)

   Upstream defines a well-documented, stable integration protocol (REST API, event schema).
   Multiple downstreams consume it without special negotiation.
   Published Language: the shared schema/vocabulary used in the integration.

   Use when: upstream serves many downstream consumers; API must be stable and generic.

7. SEPARATE WAYS:
   ┌──────────┐           ┌──────────────────┐
   │  Order   │  ✗ no    │  HR System        │
   └──────────┘  integration └──────────────────┘

   Two bounded contexts have no integration. Teams work completely independently.
   If needs overlap: each implements its own solution, no sharing.

   Use when: integration cost > duplication cost; contexts are truly independent.
   Risk: duplicate logic, data sync issues if they DO interact later.

DRAWING A CONTEXT MAP:

  Step 1: List all bounded contexts (rectangles).
  Step 2: Draw integration lines between contexts that communicate.
  Step 3: Label each line with the pattern name (e.g., "C/S", "ACL", "PL").
  Step 4: Mark upstream (U) and downstream (D) direction on each line.
  Step 5: Note team ownership for each context.
  Step 6: Highlight problematic relationships (Conformist = team pain point; Shared Kernel = coordination burden).

EXAMPLE:

  [Order] ─────────── Partnership ─────────── [Payment]
  [Order] ─── C/S (Order=Customer) ────────── [Inventory]
  [Order] ─── ACL ──────────────────────────► [Legacy ERP]
  [Order] ─── Open Host / Published Lang ───► [Reporting]
  [Order] ─── Separate Ways ────────────────  [HR System]
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Context Map:

- Teams assume "all services integrate cleanly" — surprise when Shipping can't change an API Order depends on
- "Why does Order have so many fields we don't use?" — unknown Conformist relationship polluting the model

WITH Context Map:
→ Integration relationships explicitly named: teams know negotiating power, translation needs, and change risks
→ New team member reads the map: understands the whole system's integration strategy in 20 minutes

---

### 🧠 Mental Model / Analogy

> International diplomacy between countries. The Context Map is the diplomatic relations register: Country A and Country B: allies (Partnership). Country C: trade partner with treaty (Customer/Supplier). Country D: economic colonizer whose currency we must use (Conformist). Country E: we trade via embassy translators (ACL). Country F: we broadcast press releases they can subscribe to (Open Host/Published Language). Country G: we have no diplomatic ties (Separate Ways). Without the register: someone assumes we can demand Country D change its currency. The register shows: we have no leverage — we conform.

"Countries" = bounded contexts
"Diplomatic relations register" = Context Map
"Allies" = Partnership
"Economic colonizer — must use their currency" = Conformist
"Embassy translators" = Anti-Corruption Layer

---

### ⚙️ How It Works (Mechanism)

```
CONTEXT MAP NOTATION:

  [ContextA] ──U────────D── [ContextB]
                C/S

  U = upstream (supplier), D = downstream (customer)
  C/S = Customer/Supplier relationship

  [ContextA] ──U── ACL ──D── [ContextB]
  ACL owned by [ContextB] team to protect their model.

  [ContextA] ──── SK ───── [ContextB]
  SK = Shared Kernel (dotted boundary shared subdomain)

  Common context map colors/symbols:
    Red border: Conformist (pain point — team has no control)
    Orange: Shared Kernel (coordination overhead)
    Green: Open Host (well-managed, stable integration)
    Blue: Partnership (close collaboration required)
```

---

### 🔄 How It Connects (Mini-Map)

```
Bounded Contexts (DDD building blocks — each with own model)
        │
        ▼ (document relationships between them)
Context Map ◄──── (you are here)
(strategic DDD artifact: documents integration pattern between all bounded contexts)
        │
        ├── Anti-Corruption Layer: specific pattern used in Conformist/ACL relationships
        ├── Shared Kernel: specific pattern for shared subdomain
        ├── Domain Events: Open Host Service often uses events as Published Language
        └── Team Topologies: Context Map relationship types map to team interaction modes
```

---

### 💻 Code Example

```java
// Context Map manifested in code — ACL protecting Order from Legacy ERP model:

// ---- LEGACY ERP MODEL (upstream — we can't change it) ----
class ErpOrderRecord {  // terrible model from ERP system
    String ord_num;      // order number as string
    String cust_id;      // customer ID
    double tot_amt;      // total as double
    String stat_code;    // "01"=pending, "02"=confirmed, "99"=cancelled
    String currency_cd;  // "USD", "EUR"
}

// ---- ANTI-CORRUPTION LAYER (owned by Order context team) ----
@Component
class ErpOrderTranslator {
    Order translate(ErpOrderRecord erp) {
        return Order.builder()
            .id(OrderId.of(erp.ord_num))
            .customerId(CustomerId.of(erp.cust_id))
            .total(Money.of(BigDecimal.valueOf(erp.tot_amt), Currency.of(erp.currency_cd)))
            .status(translateStatus(erp.stat_code))  // "01" → OrderStatus.PENDING
            .build();
    }

    private OrderStatus translateStatus(String erpCode) {
        return switch (erpCode) {
            case "01" -> OrderStatus.PENDING;
            case "02" -> OrderStatus.CONFIRMED;
            case "99" -> OrderStatus.CANCELLED;
            default -> throw new IllegalArgumentException("Unknown ERP status: " + erpCode);
        };
    }
}

// ---- ORDER CONTEXT (protected model, clean domain language) ----
class OrderService {
    // Uses ErpOrderTranslator via ACL — never touches ErpOrderRecord directly.
    // ERP's terrible model (double for money, magic strings) stays outside the ACL.
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                           | Reality                                                                                                                                                                                                                                                                                                          |
| ------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A Context Map is a system architecture diagram          | A Context Map is a RELATIONSHIP map, not a deployment diagram. It shows how bounded contexts relate (integration pattern, team dynamics) — not how they are deployed (containers, services, databases). Two bounded contexts can share a process (monolith) and still have a C/S relationship                    |
| ACL is always the right choice between bounded contexts | ACL is an investment that adds complexity. If the upstream model is clean and compatible with downstream, a Conformist or C/S relationship (with minimal translation) might be simpler. ACL is justified when upstream model would genuinely corrupt downstream domain language — not just as a reflex           |
| Partnership means sharing code between bounded contexts | Partnership is a RELATIONSHIP TYPE that describes close team coordination, not necessarily shared code. Two teams with a Partnership relationship coordinate their development (deploy together, plan together), but each bounded context maintains its own model. Shared Kernel is the pattern for sharing code |

---

### 🔥 Pitfalls in Production

**Unrecognized Conformist relationship polluting the domain model:**

```java
// PROBLEM: Order context unknowingly becomes Conformist to Salesforce CRM.
// Salesforce uses "Account" for what Order calls "Customer".
// Over time, Order's code starts using Salesforce terminology:

class OrderService {
    // "Account" leaks in from CRM — Order should call this "Customer":
    Order create(SalesforceAccount account, List<OrderItem> items) {
        // We're now passing Salesforce's Account model directly
        // into our Order logic — model corruption!
        order.setAccountId(account.getId());           // Salesforce field name
        order.setAccountType(account.getRecordType()); // Salesforce concept
    }
}

// FIX: Make the relationship explicit on the Context Map (Conformist or ACL).
// If ACL chosen: build a CustomerTranslator that converts SalesforceAccount → Customer.

class SalesforceToCustomerTranslator {
    Customer translate(SalesforceAccount acc) {
        return new Customer(
            CustomerId.of(acc.getId()),
            acc.getName(),
            CustomerTier.from(acc.getRecordType())  // Our enum, not Salesforce's string
        );
    }
}
// OrderService now uses Customer — CRM model quarantined in the ACL.
```

---

### 🔗 Related Keywords

- `Bounded Context` — the units connected on a Context Map
- `Anti-Corruption Layer` — specific pattern used in Context Map for legacy/foreign contexts
- `Shared Kernel` — specific Context Map pattern for explicitly shared subdomain models
- `Domain Events` — Open Host Services often use events as their Published Language
- `Team Topologies` — Context Map relationship types map to team interaction modes (collaboration, X-as-a-Service, facilitation)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Names the relationship between every pair │
│              │ of bounded contexts: who has leverage,   │
│              │ how models translate, what team dynamic  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Designing or auditing integration between │
│              │ services/teams; making implicit           │
│              │ dependencies explicit; DDD strategy work │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ No substitute: if you have bounded        │
│              │ contexts and integrations, you need a    │
│              │ Context Map (it reveals what's already  │
│              │ true, whether documented or not)         │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Diplomatic relations register: know your │
│              │  leverage before negotiating a change    │
│              │  across a context boundary."             │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Bounded Context → Anti-Corruption Layer →│
│              │ Shared Kernel → Domain Events            │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your company uses Salesforce as the customer system of record, an internal Order service built in-house, and SAP for financial reporting. Map the relationships: what pattern describes Order ↔ Salesforce? What about Order ↔ SAP? For the Order ↔ Salesforce relationship, how do you decide between Conformist (adopt Salesforce's model) and ACL (translate at the boundary)? What factors tip the balance?

**Q2.** A Context Map shows three bounded contexts in a triangle: Catalog → Order (C/S), Order → Fulfillment (C/S), and Catalog → Fulfillment (Conformist). What does this map tell you about team dynamics? If the Catalog team decides to rename a product field, trace the change propagation across all three relationships. How does the Conformist relationship between Catalog and Fulfillment create a different kind of problem than the C/S relationships?
