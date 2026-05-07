---
layout: default
title: "Context Map"
parent: "Software Architecture Patterns"
nav_order: 30
permalink: /software-architecture/context-map/
number: "SAP-030"
category: Software Architecture Patterns
difficulty: ★★★
depends_on: Bounded Context, Domain Model, Anti-Corruption Layer, Microservices
used_by: DDD, Microservices Architecture, Enterprise Integration
related: Bounded Context, Anti-Corruption Layer, Shared Kernel, Open Host Service
tags:
  - architecture
  - ddd
  - pattern
  - deep-dive
  - advanced
  - strategic
---

# SAP-030 — Context Map

⚡ TL;DR — A Context Map is a diagram that documents the relationships between Bounded Contexts in a system — showing how they integrate, which team is upstream vs downstream, and what integration patterns are used at each boundary.

---

### 📊 Entry Metadata

| #748            | Category: Software Architecture Patterns                                 | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Bounded Context, Domain Model, Anti-Corruption Layer, Microservices      |                 |
| **Used by:**    | DDD, Microservices Architecture, Enterprise Integration                  |                 |
| **Related:**    | Bounded Context, Anti-Corruption Layer, Shared Kernel, Open Host Service |                 |

---

### 🔥 The Problem This Solves

**THE LARGE SYSTEM PROBLEM:**
A large organization runs 12 microservices with 5 teams. Each service has its own model of "Customer" — slightly different. The billing service and the shipping service both have an `Order` concept but they model it differently. Nobody has a clear picture of how all these services relate, which teams influence which, or where the integration pain points are. When a change is needed, nobody knows which services will be affected.

**THE CONTEXT MAP SOLUTION:**
Draw a map. Show every Bounded Context (service/domain area). Show how they connect. Label each connection with the relationship type (upstream/downstream, ACL, partnership, etc.). Now anyone can see the big picture — who depends on whom, where the riskiest integration points are, and where future changes will have the most impact.

---

### 📘 Textbook Definition

A Context Map, as defined by Eric Evans in "Domain-Driven Design," is a document or diagram that describes the contact points between Bounded Contexts — the translation layers between them, and the nature of any sharing between teams. The Context Map shows, in a coarse-grained way, the overall relationship between the different Bounded Contexts in a project, identifying how the various parts of the system fit together, what language is used in each context, and how models are kept consistent across context boundaries.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
The big-picture map showing how your system's different domain areas relate, integrate, and influence each other.

**One analogy:**

> A political map of countries with borders and relationship indicators. Some borders have free-trade agreements (Shared Kernel), some have strict customs controls (Anti-Corruption Layer), some have one country dominating the other (Upstream/Downstream). The map doesn't describe what happens inside each country — it shows how they relate to each other at their borders.

**One insight:**
You cannot make good architectural decisions about change, team structure, or integration strategy without understanding the Context Map. It's the architectural blueprint for the social and technical boundaries of the system.

---

### 🔩 First Principles Explanation

**CONTEXT MAP RELATIONSHIP TYPES:**

```
┌──────────────────────────────────────────────────────────┐
│           CONTEXT MAP RELATIONSHIP TYPES                 │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Shared Kernel:                                          │
│    Two contexts share a subset of the domain model       │
│    Must be changed by mutual agreement                   │
│    Risk: coupling; Benefit: shared understanding         │
│                                                          │
│  Customer/Supplier (Upstream/Downstream):                │
│    Upstream (supplier) context influences Downstream     │
│    Downstream negotiates what it needs from Upstream     │
│    Upstream changes can break Downstream                 │
│                                                          │
│  Conformist:                                             │
│    Downstream adopts Upstream's model wholesale          │
│    No translation; Downstream loses independence         │
│    Used when Upstream has no incentive to accommodate    │
│                                                          │
│  Anti-Corruption Layer (ACL):                            │
│    Downstream protects itself from Upstream's model      │
│    Translation at the boundary                           │
│    Downstream maintains its own clean model              │
│                                                          │
│  Open Host Service / Published Language:                 │
│    Upstream provides a formal, stable protocol           │
│    Multiple downstreams integrate via this protocol      │
│                                                          │
│  Separate Ways:                                          │
│    No integration — contexts operate independently       │
│    Used when integration cost > benefit                  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧪 Thought Experiment

**READING A CONTEXT MAP:**
An e-commerce system's Context Map might show:

- `Order Management` ← Upstream → `Shipping` (Customer/Supplier: Shipping is downstream, depends on Order)
- `Order Management` ← Upstream → `Billing` (Customer/Supplier: Billing depends on Order)
- `Shipping` integrates with `Carrier API` using ACL (protects against carrier's model)
- `Billing` integrates with `Payment Gateway` using ACL
- `Order Management` and `Catalog` share a Shared Kernel (both use the same `Product` concept)

This map reveals: if `Order Management` changes its model, it affects both `Shipping` and `Billing`. This is a risk hotspot. The ACLs at `Carrier API` and `Payment Gateway` mean those external changes won't propagate inward.

---

### 🧠 Mental Model / Analogy

> A Context Map is to software architecture what an org chart is to a company — but showing the information flow and dependencies between teams and systems, not just reporting lines. It answers: "When team A makes a change, who else is affected?" It makes the invisible dependencies visible.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone):**
A diagram showing all the domain areas of your system, how they connect, and what kind of relationship each connection is.

**Level 2 — How to create one (junior):**

1. Identify each Bounded Context (each service, each domain area with its own model). 2. Draw a box for each one. 3. Draw lines for every integration point. 4. Label each line with the relationship type (U/D for upstream/downstream, ACL, SK for Shared Kernel, etc.). 5. Show which team owns each context.

**Level 3 — Using it for decisions (mid-level):**
The Context Map drives architectural decisions: Which integrations need ACLs? Where is the upstream/downstream power dynamic? Which teams need to coordinate most tightly? Where is there too much coupling (Shared Kernels that have grown)? The map is a living document — it should be updated as the architecture evolves.

**Level 4 — Strategic DDD (senior/staff):**
The Context Map is a strategic tool, not just a diagram. It reveals organizational and political dynamics: teams that are Conformists are typically in a position of low leverage (they can't influence the upstream team). Teams with ACLs have invested in their independence. Shared Kernels require the most inter-team coordination. When designing system evolution, the Context Map helps identify where to invest in decoupling (build ACLs), where to establish cleaner team interfaces (Customer/Supplier), and where Bounded Context boundaries should be redrawn. Conway's Law connects the Context Map to the organizational structure — often the best Context Map design mirrors (or deliberately counters) the team structure.

---

### ⚙️ How It Works (Mechanism)

**Context Map notation:**

```
┌──────────────────────────────────────────────────────────┐
│         CONTEXT MAP — E-COMMERCE EXAMPLE                 │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  [Catalog]─SK─[Order Mgmt]─U/D─[Shipping]               │
│      │             │                  │                  │
│     OHS           U/D               ACL                  │
│      │             │                  │                  │
│  [Mobile App]  [Billing]        [Carrier APIs]           │
│                    │                                     │
│                   ACL                                    │
│                    │                                     │
│             [Payment Gateway]                            │
│                                                          │
│  Legend:                                                 │
│  SK  = Shared Kernel (shared domain model)               │
│  U/D = Upstream/Downstream (customer-supplier)           │
│  ACL = Anti-Corruption Layer                             │
│  OHS = Open Host Service (published API)                 │
└──────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture

**Context Map evolution over time:**

```
┌──────────────────────────────────────────────────────────┐
│         CONTEXT MAP MATURITY EVOLUTION                   │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Early system: One big monolith                          │
│    [Everything] — no boundaries, implicit relationships  │
│                                                          │
│  Growing system: Identified contexts                     │
│    [Orders]─SK─[Inventory]─SK─[Billing]                  │
│    → Shared kernels everywhere = high coupling           │
│                                                          │
│  Mature system: Clear boundaries, right patterns         │
│    [Orders]──U/D──[Shipping]                             │
│        │              │                                  │
│       U/D            ACL                                 │
│        │              │                                  │
│    [Billing]     [Carriers]                              │
│        │                                                 │
│       ACL                                                │
│        │                                                 │
│   [Payments]                                             │
│    → ACLs protect; U/D relationships are explicit        │
└──────────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Context Map expressed in code structure — package boundaries:**

```
// Project structure reflecting Context Map:

src/
  order-context/           ← Order Bounded Context
    domain/
      model/Order.java
      model/OrderItem.java
    application/
      OrderApplicationService.java
    infrastructure/
      // ACL for Inventory context:
      acl/inventory/
        InventoryACL.java
        InventoryTranslator.java
      // ACL for Payment Gateway (external):
      acl/payment/
        StripePaymentACL.java
        StripeTranslator.java

  shipping-context/         ← Shipping Bounded Context
    domain/
      model/Shipment.java   ← Different "Order" concept
    application/
    infrastructure/
      acl/carrier/          ← ACL for carrier APIs
        DHLCarrierACL.java

  // Shared Kernel:
  shared-kernel/            ← Shared by Order + Catalog
    domain/
      product/ProductId.java  ← Shared type
      product/ProductName.java
```

**Context Map documentation (YAML / ADR format):**

```yaml
# context-map.yml
contexts:
  - id: order-management
    team: order-team

  - id: shipping
    team: fulfillment-team

  - id: billing
    team: finance-team

relationships:
  - upstream: order-management
    downstream: shipping
    pattern: CustomerSupplier
    description: "Shipping depends on Order events"

  - upstream: order-management
    downstream: billing
    pattern: CustomerSupplier
    description: "Billing reacts to Order payment events"

  - context: shipping
    external: carrier-apis
    pattern: ACL
    description: "Protects against carrier API model changes"

  - context1: order-management
    context2: catalog
    pattern: SharedKernel
    shared: [ProductId, ProductName]
```

---

### ⚖️ Comparison Table

| Relationship Pattern | Coupling | Control            | When to Use                                          |
| -------------------- | -------- | ------------------ | ---------------------------------------------------- |
| Shared Kernel        | Highest  | Mutual             | Small shared concepts, tight team coordination       |
| Customer/Supplier    | Medium   | Negotiated         | Clear upstream dependency with cooperative teams     |
| Conformist           | Medium   | Upstream decides   | Upstream won't accommodate; you adopt their model    |
| ACL                  | Low      | Downstream         | Upstream model is poor or foreign; you protect yours |
| Open Host Service    | Low      | Upstream publishes | Multiple downstreams; stable public interface needed |
| Separate Ways        | None     | None               | Integration cost > benefit                           |

---

### ⚠️ Common Misconceptions

| Misconception                                     | Reality                                                                                                 |
| ------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| Context Map = microservices map                   | Context Map is a DDD concept; useful for monoliths too where different subdomains have different models |
| One-time artifact                                 | Context Map is a living document — update it as the system evolves                                      |
| Every context pair needs an explicit relationship | Separate Ways is a valid choice — not all contexts need to integrate                                    |
| Context Map shows implementation details          | Context Map shows relationships and patterns, not internal implementation                               |

---

### 🚨 Failure Modes & Diagnosis

**Missing Context Map → Integration Surprises**

**Symptom:** A change in one service unexpectedly breaks another. Teams don't know who depends on their API. Integration bugs discovered late.

**Root Cause:** No explicit map of context relationships — dependencies are implicit and unknown.

**Fix:** Create a Context Map. Even a rough one on a whiteboard is valuable. Identify the downstream consumers of each context's published API.

---

**Shared Kernel Growth**

**Symptom:** The "shared kernel" package grows and grows. Every team adds their types to it. Changes to it require coordination across all teams.

**Root Cause:** Shared Kernel used as a catch-all instead of a small, carefully bounded shared concept.

**Fix:** Audit the Shared Kernel. Anything that's only used by one context should be moved into that context. Reduce the Shared Kernel to the smallest set of truly shared concepts.

---

### 🔗 Related Keywords

**Prerequisites:**

- `Bounded Context` — the boxes on the Context Map

**Builds On This:**

- `Anti-Corruption Layer` — one of the relationship patterns shown on the map
- `Shared Kernel` — another relationship pattern

**Related:**

- `Open Host Service` — a published Language pattern shown on maps
- `Strangler Fig Pattern` — migration pattern that changes the Context Map over time

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Map of relationships between domain areas │
├──────────────┼───────────────────────────────────────────┤
│ PURPOSE      │ Makes cross-context dependencies visible  │
├──────────────┼───────────────────────────────────────────┤
│ KEY PATTERNS │ SK, U/D, Conformist, ACL, OHS, Sep Ways  │
├──────────────┼───────────────────────────────────────────┤
│ LIVING DOC   │ Update as architecture evolves            │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The political map: who depends on whom   │
│              │  and what kind of relationship is it"     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You're designing a new feature that requires two currently separate Bounded Contexts to share a concept: the `Order Management` and `Analytics` contexts both need to work with a `RevenueMetric` concept. You could add it to the Shared Kernel, or you could have each context define its own version. What factors determine which choice is better, and how does the Context Map help you make this decision?

**Q2.** Conway's Law states that systems mirror the communication structures of the organizations that design them. If your company has 5 teams and the Context Map shows 12 contexts, what does that tell you about the likely integration challenges? How can you use the Context Map to deliberately design the team structure to reduce coordination overhead?
