---
id: SAP-028
title: Shared Kernel
category: Software Architecture Patterns
tier: tier-5-distributed-architecture
folder: SAP-software-architecture
difficulty: ★★★
depends_on: SAP-071
used_by: SAP-071
related: SAP-071, SAP-073, SAP-074
tags:
  - architecture
  - ddd
  - pattern
status: complete
version: 1
layout: default
parent: "Software Architecture Patterns"
grand_parent: "Technical Dictionary"
nav_order: 58
permalink: /software-architecture/shared-kernel/
  - advanced
  - strategic
---

# SAP-072 - Shared Kernel

⚡ TL;DR - A Shared Kernel is a deliberate, bounded subset of the domain model that is shared between two Bounded Contexts - any change to this shared model requires explicit coordination and agreement between both teams.

| Field          | Value                     |
| -------------- | ------------------------- |
| **Depends on** | SAP-071                   |
| **Used by**    | SAP-071                   |
| **Related**    | SAP-071, SAP-073, SAP-074 |

---

### 🔥 The Problem This Solves

**THE DUPLICATION VS COUPLING DILEMMA:**
Two Bounded Contexts - `Order Management` and `Catalog` - both need to work with `ProductId` and basic `Product` information. If each defines its own `Product` type, they're duplicating code. If one depends on the other, they're coupling. If they share a common library, who owns it and who can change it?

**THE SHARED KERNEL SOLUTION:**
Explicitly define a small, shared domain model fragment that both contexts agree on. Both teams commit to keeping it stable and coordinating changes. The Shared Kernel is small by design - only the minimum concepts that genuinely must be shared.

**EVOLUTION:**
Eric Evans documented the Shared Kernel as one of the Context Map relationship patterns in "Domain-Driven Design" (2003). The pattern predated DDD in the form of shared libraries and common utility packages, but Evans gave it formal governance: shared code must be agreed upon by both teams and cannot be changed unilaterally. In the microservices era (2014+), the Shared Kernel typically manifests as a Maven/npm library published to a private package registry. The key evolution is the recognition that Shared Kernel creates a team coupling that is often more expensive than the code duplication it prevents - Vaughn Vernon and other DDD practitioners advocate using it sparingly, preferring ACL over Shared Kernel in most cases.

---

### 📘 Textbook Definition

A Shared Kernel, as defined by Eric Evans in "Domain-Driven Design," is an arrangement where two teams that are closely coupled designate a specific subset of their domain model to share. The designated subset includes code, database designs, or whatever else they are sharing. They agree to keep this kernel small, and they agree not to change it without first consulting the other team. They will integrate frequently - often multiple times per day. The Shared Kernel is explicitly marked as shared; anything not in the Shared Kernel is the exclusive domain of each team.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A small, co-owned piece of domain model that two contexts agree to share - with mutual change coordination.

**One analogy:**

> A property boundary fence shared by two neighbors. Both agree on where the fence sits, both have a responsibility to maintain it, and neither can move it without the other's agreement. The fence is the Shared Kernel - small, explicit, and jointly owned.

**One insight:**
Shared Kernel is a trade-off: less duplication in exchange for less autonomy. The smaller the Shared Kernel, the less coordination overhead. Most shared kernels start small and grow - that growth is a warning sign.

---

### 🔩 First Principles Explanation

**SHARED KERNEL CHARACTERISTICS:**

```
┌──────────────────────────────────────────────────────────┐
│          SHARED KERNEL PROPERTIES                        │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ✅ Deliberately small:                                  │
│     Only concepts that truly must be shared              │
│     NOT a catch-all utilities library                    │
│                                                          │
│  ✅ Explicitly bounded:                                  │
│     Clear list of what IS and IS NOT in the kernel       │
│     Documented, versioned, named                         │
│                                                          │
│  ✅ Change by mutual agreement:                          │
│     Neither team changes it unilaterally                 │
│     Changes go through both teams' review                │
│                                                          │
│  ✅ Frequent integration:                                │
│     Both contexts integrate with the kernel continuously │
│     NOT: integrate once every 6 months                   │
│                                                          │
│  ⚠️  Danger signs:                                       │
│     Kernel growing larger than a few key types           │
│     One team making changes without telling the other    │
│     "Let's just add this to the shared kernel"           │
└──────────────────────────────────────────────────────────┘
```

---

### 🧪 Thought Experiment

**APPROPRIATE SHARED KERNEL:**
`Order Management` and `Shipping` share a Shared Kernel containing: `OrderId`, `CustomerId`, `ProductId`. Just typed UUID wrappers. These are stable identifiers that both contexts use. Changes to these types are extremely rare and would require coordination anyway. This is a good Shared Kernel - small, stable, genuinely shared.

**INAPPROPRIATE SHARED KERNEL:**
Someone adds `Order`, `Customer`, `Product` to the kernel because "both contexts need them." Now the kernel IS both contexts. Any change to the `Order` model requires coordinating with the Shipping team. The whole purpose of having separate Bounded Contexts is undermined.

---

### 🧠 Mental Model / Analogy

> The Shared Kernel is like the interface specification of a physical connector standard (USB, HDMI). Both manufacturers know exactly what the connector must look like and what signals it carries. Neither can change this unilaterally - any change requires an industry consortium agreement (mutual coordination). The internal design of the device on each end is independent. The connector standard (Shared Kernel) is just the minimum needed to plug in.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone):**
A small, agreed-upon set of types and concepts that two domain areas both use and both maintain together.

**Level 2 - How to implement (junior):**
Create a separate Maven module or package for the Shared Kernel. Put only the agreed shared concepts there. Both services depend on this module. Write tests that validate the shared types. Treat the module as a contract - changes need approval from both teams.

**Level 3 - When to use vs alternatives (mid-level):**
Use Shared Kernel when: 1) Two closely collaborating teams have genuinely shared domain concepts. 2) The overhead of translation (ACL) outweighs the coupling cost. 3) The shared concepts are genuinely stable. Prefer ACL when: 1) Teams are less tightly coordinated. 2) Upstream model is poorly designed. 3) You need freedom to evolve independently. Prefer duplication when: 1) The shared concept is simple (a string constant). 2) The contexts are evolving independently and shared changes would be disruptive.

**Level 4 - Organizational dynamics (senior/staff):**
The Shared Kernel is a strategic decision as much as a technical one. It creates organizational coupling: both teams must coordinate on a shared asset. This works well for small, stable teams that communicate frequently. It works poorly for geographically distributed teams, teams with different release cadences, or teams that have diverging domain understanding. Shared Kernels often grow over time as it becomes "convenient" to add more things. A governance process is needed: who reviews proposed additions? What's the deprecation process for removing concepts? Without this, the Shared Kernel becomes an accretion of technical debt that couples everything.

---

### ⚙️ How It Works (Mechanism)

**Shared Kernel as Maven module:**

```
┌──────────────────────────────────────────────────────────┐
│           SHARED KERNEL MODULE STRUCTURE                 │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  shared-kernel/ (Maven module)                           │
│    pom.xml                                               │
│    src/main/java/com/acme/shared/                        │
│      identity/                                           │
│        OrderId.java     (record OrderId(UUID value))     │
│        CustomerId.java  (record CustomerId(UUID value))  │
│        ProductId.java   (record ProductId(UUID value))   │
│      money/                                              │
│        Money.java       (amount + currency VO)           │
│        Currency.java    (currency enum)                  │
│    src/test/java/...                                     │
│      (tests validate the shared types)                   │
│                                                          │
│  order-service/ depends on shared-kernel               │
│  shipping-service/ depends on shared-kernel             │
│  billing-service/ depends on shared-kernel              │
│                                                          │
│  Change governance:                                      │
│    → PR to shared-kernel requires review from all teams  │
│    → Semantic versioning (breaking changes = major bump) │
└──────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture

```
┌──────────────────────────────────────────────────────────┐
│       SHARED KERNEL vs SEPARATE MODELS DECISION          │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Order Context needs:   Shipping Context needs:          │
│    Order (complex)        Shipment (different model)     │
│    Customer (full)        Customer (address only)        │
│    OrderId                OrderId ← SHARED               │
│    CustomerId             CustomerId ← SHARED            │
│    Money                  Money ← SHARED                 │
│    Product catalog data   ProductId ← SHARED             │
│                                                          │
│  Shared Kernel contains: OrderId, CustomerId, Money,     │
│  ProductId - just the reference types                    │
│                                                          │
│  NOT in Shared Kernel: Order, Customer, Product models   │
│  → each context defines its own version of these         │
└──────────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Shared Kernel - minimal, stable types:**

```java
// shared-kernel module - jointly owned by both teams

// Typed IDs - rarely change, genuinely shared
public record OrderId(UUID value) {
    public static OrderId generate() {
        return new OrderId(UUID.randomUUID());
    }
    public static OrderId of(String value) {
        return new OrderId(UUID.fromString(value));
    }
}

public record CustomerId(UUID value) {
    public static CustomerId of(String value) {
        return new CustomerId(UUID.fromString(value));
    }
}

// Money Value Object - both contexts do financial calculations
public record Money(BigDecimal amount, Currency currency) {
    public Money {
        Objects.requireNonNull(amount);
        Objects.requireNonNull(currency);
        amount = amount.setScale(2, RoundingMode.HALF_EVEN);
    }
    public Money add(Money other) { ... }
    public Money subtract(Money other) { ... }
}

// Order Management context uses:
// OrderId from shared kernel + its own Order class
public class Order {
    private final OrderId id;       // shared kernel
    private final CustomerId cid;   // shared kernel
    private Money total;            // shared kernel
    private List<OrderItem> items;  // own context
}

// Shipping context uses:
// OrderId from shared kernel + its own Shipment class
public class Shipment {
    private final ShipmentId id;    // own context
    private final OrderId orderId;  // shared kernel reference
    private ShipmentStatus status;  // own context
    private PostalAddress address;  // own context
}
```

---

### ⚖️ Comparison Table

| Relationship      | Coupling | Autonomy | Coordination       | Best For                              |
| ----------------- | -------- | -------- | ------------------ | ------------------------------------- |
| **Shared Kernel** | Medium   | Reduced  | Required (mutual)  | Small, stable, genuinely shared       |
| Separate Ways     | None     | Full     | None               | Simple concepts; low integration need |
| ACL               | Low      | High     | Minimal            | Protecting your model from external   |
| Conformist        | High     | None     | None (you conform) | No leverage over upstream             |

---

### ⚠️ Common Misconceptions

| Misconception                                            | Reality                                                                                                                                         |
| -------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| Shared Kernel is a utilities library                     | Utilities are non-domain code; Shared Kernel is domain concepts - different things                                                              |
| Bigger Shared Kernel = less duplication = good           | Bigger Shared Kernel = more coupling = bad. Keep it tiny                                                                                        |
| Shared Kernel eliminates the need for ACL                | ACL is for external/foreign systems; Shared Kernel is for closely related internal contexts - different use cases                               |
| Any code used by two services should be in Shared Kernel | Only domain concepts that are genuinely the same concept belong there. Infrastructure code, utilities, and framework code are not Shared Kernel |

---

### 🚨 Failure Modes & Diagnosis

**Shared Kernel Bloat**

**Symptom:** The shared-kernel module grows to hundreds of classes. PRs to it are reviewed by 4+ teams. Changes to it are delayed because everyone must approve. Version conflicts emerge.

**Root Cause:** Teams adding to the Shared Kernel instead of defining context-specific models.

**Diagnostic Check:**

```bash
# Check Shared Kernel size and growth
git log --oneline shared-kernel/src/ | wc -l  # commit count
find shared-kernel/src/main/java -name "*.java" | wc -l
# If > 20-30 files, likely bloated
```

**Fix:** Audit the Shared Kernel. Move types used by only one context into that context. For types where contexts have diverging needs, create context-specific versions with an ACL or translation if they need to exchange data.

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Shared ownership is the most expensive form of ownership. Every concept, module, or library that two independent teams must both agree to change creates a coordination tax. Minimize the surface area of what is shared.

**Where else this pattern appears:**

- **Shared custody legal frameworks:** When two parties jointly own something (property, custody), changes require agreement from both. Joint ownership works only when changes are rare and coordination is feasible - which is why courts minimize jointly owned assets in divorce settlements.
- **Open-source core libraries:** Java's `java.lang` package is a Shared Kernel for the entire Java ecosystem. Nobody changes it unilaterally - any change requires the JCP process and broad consensus. The extreme stability of `java.lang` is the price of it being universally shared.
- **Database schemas for multiple applications:** A database schema shared by three applications is a Shared Kernel at the persistence level. Any schema change requires all three applications to be updated, tested, and deployed together - the classic multi-application coupling problem.

---

### 💡 The Surprising Truth

Most DDD practitioners recommend AGAINST using Shared Kernel as a first-choice pattern, despite it seeming like the obvious solution to code duplication. The reason: Shared Kernel creates a formal team coupling that is harder to remove than the duplication it prevents. Once two teams share a kernel, the kernel tends to grow (because sharing is cheaper than duplicating), and the coupling deepens over time. Evans himself noted that Shared Kernel requires a high level of discipline from both teams; without that discipline, it becomes a unstructured shared library that everyone depends on and nobody owns.

---

### �🔗 Related Keywords

**Prerequisites (understand these first):**

- SAP-071 - Context Map (the Shared Kernel is one of the relationship patterns on a Context Map; understanding Context Map provides the strategic picture within which Shared Kernel is a specific choice)

**Builds On This (learn these next):**

- SAP-071 - Context Map (after understanding Shared Kernel as a pattern, the Context Map shows where to use it versus ACL, OHS, or Separate Ways)

**Alternatives / Comparisons:**

- SAP-070 - Anti-Corruption Layer (alternative for isolation: instead of sharing a kernel, each context defines its own model and translates at the boundary; more work upfront, more independence long-term)
- SAP-073 - Open Host Service (alternative for sharing: instead of sharing a library, one context publishes a stable service API; other contexts consume the API, not the source code)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Small co-owned domain fragment shared     │
│              │ between two Bounded Contexts              │
├──────────────┼───────────────────────────────────────────┤
│ KEY RULE     │ Keep it tiny; change by mutual agreement  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Closely collaborating teams, stable types │
├──────────────┼───────────────────────────────────────────┤
│ WARNING      │ Growing Shared Kernel = growing coupling  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The shared fence: small, joint ownership,│
│              │  neither can move it alone"               │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your Shared Kernel currently contains `OrderId`, `CustomerId`, and `Money`. A new team wants to integrate with your system. They suggest adding their `SubscriptionId` and `InvoiceId` to the Shared Kernel because they'll need to reference orders and customers. Should these be added to the Shared Kernel? What criteria should guide this decision?

_Hint:_ Research Evans's criterion for the Shared Kernel boundary: "Include in the kernel only concepts that are genuinely shared between the teams and that both teams use in the same way." The key test: do BOTH existing teams (Order Management AND the new team) need `SubscriptionId`, or only the new team? If only the new team needs it, it belongs in their bounded context, not the shared kernel. Research the "gravitational pull" problem: shared kernels tend to grow because adding to the kernel is cheaper than creating an ACL, but growth increases coordination cost.

**Q2.** The Shared Kernel between `Order Management` and `Shipping` contains `OrderId`. Both teams agree. But now `Order Management` needs to change `OrderId` from a `UUID` to a 10-character alphanumeric code for human readability. How do you manage this breaking change to the Shared Kernel without disrupting the `Shipping` service that's in production?

_Hint:_ Research semantic versioning applied to shared library releases - specifically the strategy of publishing `shared-kernel:2.0.0` with the new `OrderId` type, running `shared-kernel:1.x.x` and `2.0.0` in parallel during a migration period, updating Shipping to use `2.0.0`, then deprecating `1.x.x`. Also research "expand and contract" migration pattern: first expand (add `alphanumericOrderId` alongside existing `uuidOrderId`), migrate consumers, then contract (remove `uuidOrderId`).

**Q3.** A team discovers that their Shared Kernel has grown to 47 classes across 15 packages and is now a 500KB JAR that every service depends on. Three services have different sub-sets of needs: Service A needs IDs only, Service B needs domain events only, Service C needs both plus value objects. How do you decompose the bloated Shared Kernel to minimize coupling while preserving the shared vocabulary benefits?

_Hint:_ Research the concept of "nano-libraries" and specifically the Module System (Java 9 JPMS) approach to fine-grained modularization. The technique: split the Shared Kernel into multiple small, focused libraries (`shared-ids:1.0.0`, `shared-events:1.0.0`, `shared-value-objects:1.0.0`). Each service depends only on the sub-library it needs. This reduces coupling without abandoning shared vocabulary. Research how Spring Framework achieves this with its many fine-grained `spring-*` modules.
