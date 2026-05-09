---
id: SAP-035
title: Context Map
category: Software Architecture Patterns
tier: tier-5-distributed-architecture
folder: SAP-software-architecture
difficulty: ★★★
depends_on: SAP-034, SAP-036, SAP-037
used_by: SAP-034, SAP-036, SAP-037
related: SAP-034, SAP-036, SAP-037, SAP-038
tags:
  - architecture
  - ddd
  - pattern
status: complete
version: 1
layout: default
parent: "Software Architecture Patterns"
grand_parent: "Technical Dictionary"
nav_order: 35
permalink: /software-architecture/context-map/
  - deep-dive
  - advanced
  - strategic
---

# SAP-035 - Context Map

⚡ TL;DR - A Context Map is a diagram that documents the relationships between Bounded Contexts in a system - showing how they integrate, which team is upstream vs downstream, and what integration patterns are used at each boundary.

| Field          | Value                              |
| -------------- | ---------------------------------- |
| **Depends on** | SAP-034, SAP-036, SAP-037          |
| **Used by**    | SAP-034, SAP-036, SAP-037          |
| **Related**    | SAP-034, SAP-036, SAP-037, SAP-038 |

---

### 🔥 The Problem This Solves

**THE LARGE SYSTEM PROBLEM:**
A large organization runs 12 microservices with 5 teams. Each service has its own model of "Customer" - slightly different. The billing service and the shipping service both have an `Order` concept but they model it differently. Nobody has a clear picture of how all these services relate, which teams influence which, or where the integration pain points are. When a change is needed, nobody knows which services will be affected.

**THE CONTEXT MAP SOLUTION:**
Draw a map. Show every Bounded Context (service/domain area). Show how they connect. Label each connection with the relationship type (upstream/downstream, ACL, partnership, etc.). Now anyone can see the big picture - who depends on whom, where the riskiest integration points are, and where future changes will have the most impact.

**EVOLUTION:**
Eric Evans introduced the Context Map as a strategic DDD tool in "Domain-Driven Design" (2003), documenting relationship patterns including Shared Kernel, Customer/Supplier, Conformist, Anti-Corruption Layer, Open Host Service, and Separate Ways. The concept evolved with the microservices movement (2014+) - suddenly every team was effectively drawing Context Maps as service topology diagrams, but without Evans's relationship vocabulary. Nick Tune and Scott Millett's "Patterns, Principles, and Practices of Domain-Driven Design" (2015) and Vaughn Vernon's work expanded the Context Map into a practitioner tool. Today, tools like Context Mapper (context-mapper.org) allow Context Maps to be written as code (DSL) and generate architectural diagrams automatically, making the "living document" goal more achievable.

---

### 📘 Textbook Definition

A Context Map, as defined by Eric Evans in "Domain-Driven Design," is a document or diagram that describes the contact points between Bounded Contexts - the translation layers between them, and the nature of any sharing between teams. The Context Map shows, in a coarse-grained way, the overall relationship between the different Bounded Contexts in a project, identifying how the various parts of the system fit together, what language is used in each context, and how models are kept consistent across context boundaries.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
The big-picture map showing how your system's different domain areas relate, integrate, and influence each other.

**One analogy:**

> A political map of countries with borders and relationship indicators. Some borders have free-trade agreements (Shared Kernel), some have strict customs controls (Anti-Corruption Layer), some have one country dominating the other (Upstream/Downstream). The map doesn't describe what happens inside each country - it shows how they relate to each other at their borders.

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
│    No integration - contexts operate independently       │
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

> A Context Map is to software architecture what an org chart is to a company - but showing the information flow and dependencies between teams and systems, not just reporting lines. It answers: "When team A makes a change, who else is affected?" It makes the invisible dependencies visible.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone):**
A diagram showing all the domain areas of your system, how they connect, and what kind of relationship each connection is.

**Level 2 - How to create one (junior):**

1. Identify each Bounded Context (each service, each domain area with its own model). 2. Draw a box for each one. 3. Draw lines for every integration point. 4. Label each line with the relationship type (U/D for upstream/downstream, ACL, SK for Shared Kernel, etc.). 5. Show which team owns each context.

**Level 3 - Using it for decisions (mid-level):**
The Context Map drives architectural decisions: Which integrations need ACLs? Where is the upstream/downstream power dynamic? Which teams need to coordinate most tightly? Where is there too much coupling (Shared Kernels that have grown)? The map is a living document - it should be updated as the architecture evolves.

**Level 4 - Strategic DDD (senior/staff):**
The Context Map is a strategic tool, not just a diagram. It reveals organizational and political dynamics: teams that are Conformists are typically in a position of low leverage (they can't influence the upstream team). Teams with ACLs have invested in their independence. Shared Kernels require the most inter-team coordination. When designing system evolution, the Context Map helps identify where to invest in decoupling (build ACLs), where to establish cleaner team interfaces (Customer/Supplier), and where Bounded Context boundaries should be redrawn. Conway's Law connects the Context Map to the organizational structure - often the best Context Map design mirrors (or deliberately counters) the team structure.

---

### ⚙️ How It Works (Mechanism)

**Context Map notation:**

```
┌──────────────────────────────────────────────────────────┐
│         CONTEXT MAP - E-COMMERCE EXAMPLE                 │
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
│    [Everything] - no boundaries, implicit relationships  │
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

**Context Map expressed in code structure - package boundaries:**

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
| One-time artifact                                 | Context Map is a living document - update it as the system evolves                                      |
| Every context pair needs an explicit relationship | Separate Ways is a valid choice - not all contexts need to integrate                                    |
| Context Map shows implementation details          | Context Map shows relationships and patterns, not internal implementation                               |

---

### 🚨 Failure Modes & Diagnosis

**Missing Context Map → Integration Surprises**

**Symptom:** A change in one service unexpectedly breaks another. Teams don't know who depends on their API. Integration bugs discovered late.

**Root Cause:** No explicit map of context relationships - dependencies are implicit and unknown.

**Fix:** Create a Context Map. Even a rough one on a whiteboard is valuable. Identify the downstream consumers of each context's published API.

---

**Shared Kernel Growth**

**Symptom:** The "shared kernel" package grows and grows. Every team adds their types to it. Changes to it require coordination across all teams.

**Root Cause:** Shared Kernel used as a catch-all instead of a small, carefully bounded shared concept.

**Fix:** Audit the Shared Kernel. Anything that's only used by one context should be moved into that context. Reduce the Shared Kernel to the smallest set of truly shared concepts.

---

### � Transferable Wisdom

**Reusable Engineering Principle:** Make dependencies between systems visible, explicit, and named before they become the invisible constraints that prevent independent change. An unmapped dependency is an unknown risk.

**Where else this pattern appears:**
- **Org chart dependency maps:** Team topology diagrams (Team Topologies) show which teams depend on which platform teams, which enabling teams exist, and what kind of interactions they have (collaboration, X-as-a-Service, facilitating). This is a Context Map for the organization.
- **Infrastructure dependency graphs:** Terraform dependency graphs show which resources depend on which, which must be created first, and what the blast radius of a change is. This is a Context Map for infrastructure.
- **Package dependency trees:** `npm ls` or Maven dependency trees show which packages depend on which, revealing circular dependencies and version conflicts. A dependency tree is a Context Map for software libraries.

---

### 💡 The Surprising Truth

Context Maps are the most underused DDD artifact because they require organizational knowledge that no single engineer possesses, and they become outdated the moment they are drawn. Evans intended the Context Map to be a "living document" - updated whenever integration patterns change, new contexts are added, or team boundaries shift. In practice, most DDD projects draw a Context Map at the start, present it in the architecture kickoff, and then never update it as the system evolves. Six months later, the actual system has three new contexts, two old relationships have changed, and the map shows a system that no longer exists. The discipline of maintaining a Context Map is harder than drawing it, and that maintenance discipline is what separates organizations that actually benefit from DDD from those that just use DDD terminology.

---

### �🔗 Related Keywords

**Prerequisites (understand these first):**
- SAP-034 - Anti-Corruption Layer (one of the core relationship patterns shown on a Context Map; understanding ACL is required to understand what the map is documenting when it shows an ACL relationship)
- SAP-036 - Shared Kernel (another core relationship pattern; understanding Shared Kernel and ACL gives you the two most important integration patterns the map documents)
- SAP-037 - Open Host Service (the third major pattern; a context map is largely a picture of which contexts use ACL, Shared Kernel, OHS, or other relationship patterns)

**Builds On This (learn these next):**
- SAP-034 - Anti-Corruption Layer (the Context Map shows WHERE ACLs are needed; ACL is the implementation of the "Protected" relationship shown on the map)
- SAP-036 - Shared Kernel (the Context Map shows where Shared Kernel exists; Shared Kernel requires governance to maintain)
- SAP-037 - Open Host Service (the Context Map shows which contexts publish OHS; the Published Language formalizes the contract)

**Alternatives / Comparisons:**
- Service dependency graphs (show technical call dependencies but not the conceptual model relationships; do not capture Upstream/Downstream, Conformist, or Shared Kernel semantics)
- Team Topologies diagrams (show team relationships rather than model relationships; complementary to Context Map, not an alternative)

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

*Hint:* Research Evans's criteria for Shared Kernel: the concept must be used by both teams, both teams must agree to joint ownership, and change to the shared concept must require coordination between teams. The key question: how often does `RevenueMetric` change, and can both teams coordinate those changes? Research the "Conformist" pattern as an alternative: Analytics conforms to Order Management's model, eliminating the shared kernel overhead at the cost of Analytics's independence.

**Q2.** Conway's Law states that systems mirror the communication structures of the organizations that design them. If your company has 5 teams and the Context Map shows 12 contexts, what does that tell you about the likely integration challenges? How can you use the Context Map to deliberately design the team structure to reduce coordination overhead?

*Hint:* Research the "Inverse Conway Maneuver" from Team Topologies - specifically the technique of designing the desired system architecture first (Context Map), then organizing teams to mirror those boundaries (rather than letting the org structure dictate the architecture). If 12 contexts are maintained by 5 teams, some teams own multiple contexts, increasing cognitive load and integration risk. Research how identifying "natural" context boundaries that map to single-team ownership reduces the coordination tax.

**Q3.** A Context Map reveals a "Big Ball of Mud" - one central context that every other context depends on, and that depends on many external systems. This context has grown organically over 10 years and has no clear boundary. How do you use the Context Map to plan a decomposition of this monolithic context without a big-bang rewrite?

*Hint:* Research the "Strangler Fig" pattern applied to bounded context decomposition - specifically: identify which downstream contexts depend on which capabilities of the Big Ball of Mud, then extract those capabilities into new bounded contexts one at a time. The Context Map becomes the TARGET architecture; each Strangler Fig extraction moves one relationship from the Big Ball to a new context. Research how the ACL pattern enables the extraction: the new context provides the same interface as the old one, so other contexts don't need to change when the implementation moves.
