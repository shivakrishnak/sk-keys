---
layout: default
title: "Bounded Context"
parent: "Software Architecture Patterns"
nav_order: 747
permalink: /software-architecture/bounded-context/
number: "747"
category: Software Architecture Patterns
difficulty: ★★★
depends_on: "Domain Model, Ubiquitous Language, Microservices"
used_by: "DDD, Microservices design, Context Map, Anti-Corruption Layer"
tags: #advanced, #architecture, #ddd, #domain, #microservices
---

# 747 — Bounded Context

`#advanced` `#architecture` `#ddd` `#domain` `#microservices`

⚡ TL;DR — A **Bounded Context** is an explicit boundary within which a domain model applies — inside the boundary, terms have precise meanings; outside the boundary, the same word may mean something different, requiring explicit translation.

| #747 | Category: Software Architecture Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Domain Model, Ubiquitous Language, Microservices | |
| **Used by:** | DDD, Microservices design, Context Map, Anti-Corruption Layer | |

---

### 📘 Textbook Definition

**Bounded Context** (Eric Evans, "Domain-Driven Design") is a central pattern in DDD that defines the explicit boundaries within which a particular domain model is valid and consistent. Within a bounded context: (1) **Ubiquitous Language**: every term has a single, precise meaning agreed upon by the team and domain experts. (2) **Domain Model ownership**: one team owns the bounded context and its model. (3) **Internal consistency**: all concepts within the bounded context are coherently defined relative to each other. (4) **Explicit boundaries**: the boundary is explicitly recognized — it may be a service, a module, a package, or even a subdomain within a monolith. Across boundaries: the same word may mean different things. "Customer" in the Sales context (prospect, lead, contract value) ≠ "Customer" in the Shipping context (delivery address, shipping history, preferred carrier). The boundary forces explicit translation rather than implicit, error-prone conflation.

---

### 🟢 Simple Definition (Easy)

The word "bank." In different contexts: a river bank (geography), a blood bank (medicine), a money bank (finance), a data bank (computing). Each field uses "bank" with a precise, agreed-upon meaning within that field. Confusion happens when the context isn't explicit: "I went to the bank" — which one? Bounded Context: explicitly declaring which "bank" you mean and ensuring everyone in that context uses the word with the same meaning.

---

### 🔵 Simple Definition (Elaborated)

An e-commerce company has multiple teams: Sales, Orders, Shipping, Billing, Customer Support. "Order" means different things: to Sales, an order is a revenue opportunity; to Shipping, an order is items to pack and ship; to Billing, an order is an invoice; to Customer Support, an order is a problem to resolve. One giant "Order" class that satisfies all four teams: bloated, contradictory, impossible to maintain. Four bounded contexts, each with their own "Order": Sales context has `SalesOrder` (revenue, discount, sales rep). Shipping context has `ShipmentOrder` (items, addresses, carrier). Each model is precise within its context. At boundaries: explicit translation.

---

### 🔩 First Principles Explanation

**Why bounded contexts exist, what they contain, how they integrate:**

```
THE PROBLEM BOUNDED CONTEXTS SOLVE:

  Large software systems: multiple subdomains, multiple teams, multiple models.
  
  Single shared model (the "big ball of mud"):
  
    class Customer {
        // Sales team needs:
        String salesRepId;
        BigDecimal lifetimeValue;
        String leadSource;
        String contractTier;
        
        // Shipping team needs:
        Address defaultShippingAddress;
        String preferredCarrier;
        Boolean signatureRequired;
        
        // Billing team needs:
        String paymentMethodId;
        String billingAddress;
        Integer netPaymentTerms;
        
        // Support team needs:
        String preferredContactMethod;
        String supportTierId;
        List<Ticket> openTickets;
    }
    
    Problems:
    - Every team changes this class → constant merge conflicts
    - Sales doesn't understand shipping fields; shipping doesn't need billing fields
    - "Customer" means different things to each team
    - Invariants impossible: sales wants "contractTier" required; support doesn't care
    - God class grows without bound
    
  Bounded Contexts (explicit separation):
  
    Sales Context:
      Customer = { id, name, salesRepId, lifetimeValue, contractTier }
      Order = { id, customerId, proposalDate, totalValue, discount, salesperson }
      
    Shipping Context:
      Customer = { id, name, defaultAddress, preferredCarrier, signatureRequired }
      Order = { id, customerId, items, weight, dimensions, carrier, trackingNumber }
      
    Billing Context:
      Customer = { id, name, billingAddress, paymentMethod, netPaymentTerms, creditLimit }
      Invoice = { id, customerId, lineItems, total, dueDate, status }
      
    Each context: consistent, focused model. Each team: owns their context.
    
  BOUNDED CONTEXT CONTENTS:

    A bounded context contains:
    - Domain model (entities, value objects, domain services)
    - Ubiquitous Language (the agreed vocabulary within this boundary)
    - Application services (use cases specific to this context)
    - Repository interfaces (for loading/saving the context's aggregates)
    - Domain events (published by this context)
    
    A bounded context does NOT contain:
    - Another bounded context's domain model (cross-context: explicit integration)
    
BOUNDED CONTEXT IDENTIFICATION HEURISTICS:

  1. TEAM BOUNDARY:
     One team → one bounded context. Conway's Law: system architecture mirrors
     communication structure. Each team owns and is responsible for one bounded context.
     
  2. LINGUISTIC BOUNDARY:
     When the same word means different things in different conversations:
     "Order" (sales opportunity) vs "Order" (fulfillment task) → likely two contexts.
     
  3. INVARIANT BOUNDARY:
     What needs to be consistent together? 
     Sales order consistency: discount ≤ max allowed for customer tier.
     Shipping order consistency: all items must have valid shipping dimensions.
     Different invariants → different contexts.
     
  4. RATE-OF-CHANGE BOUNDARY:
     Sales model changes when sales process changes (frequently).
     Shipping model changes when carrier integrations change.
     Different change drivers → different contexts.
     
BOUNDED CONTEXT RELATIONSHIPS:

  DDD Context Map: visualizes how bounded contexts relate.
  
  PARTNERSHIP: Two contexts evolve together. Teams coordinate.
  
  SHARED KERNEL: Two contexts share a small, carefully maintained subset of domain model.
  
  CUSTOMER-SUPPLIER:
    Upstream: Supplier publishes API.
    Downstream: Customer uses the API.
    Customer: relies on supplier not breaking the interface.
    
  CONFORMIST: Downstream adopts upstream model without translation.
    "We'll use the ERP's model as-is." Simplest but gives up domain purity.
    
  ANTI-CORRUPTION LAYER: Downstream protects its model from upstream's model.
    "We translate ERP concepts to our domain concepts." Protects domain purity.
    
  OPEN HOST SERVICE: Upstream publishes a well-designed, stable API.
    "We publish a formal API; downstream integrates without modification."
    
  PUBLISHED LANGUAGE: Formal shared language for integration (e.g., domain events).
    "We publish events in a standard schema; anyone can consume."
    
BOUNDED CONTEXT ≠ MICROSERVICE:

  Common misconception: 1 bounded context = 1 microservice.
  
  Reality: 1 bounded context may be:
    - A microservice (ideal for independent deployment)
    - A module within a monolith (Modular Monolith)
    - A package within a monorepo
    - A subdomain within a large service
    
  Start: bounded context as a module in a monolith.
  If deployment independence needed: extract to microservice.
  
  Rule: define bounded context first (model boundary); deployment unit is separate decision.
  
  Starting with microservices without clear bounded contexts:
  → Distributed monolith (services coupled across context boundaries)
  → Wrong service decomposition (too fine-grained or too coarse-grained)
  
  Correct order: Bounded Context first → decide if it needs to be its own service.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Bounded Contexts:
- Single shared "Customer" class: 50 fields, impossible to understand, constant team conflicts
- Same word used for different concepts: "Order" in five different ways across the codebase
- Teams block each other: changing one field for one team breaks another team's invariants

WITH Bounded Contexts:
→ Each team owns their precise model: no conflicts, no god classes
→ Ubiquitous Language within context: everyone uses the same words with the same meaning
→ Explicit integration: cross-context interaction is explicit (ACL, events) not implicit (shared class)

---

### 🧠 Mental Model / Analogy

> A hospital with specialized departments. Each department (Radiology, Cardiology, Emergency) has its own precise vocabulary: "film" means an X-ray in Radiology, a liver function measurement in Pathology, a medical record in Administration. Each department has its own tools, processes, and specialist language that is precise and consistent within the department. Cross-department communication: explicit referrals, standardized reports, discharge summaries — explicit translation between departments. Bounded Context = hospital department (precise within its walls; explicit translation at the boundary).

"Hospital department" = bounded context
"Department's specialist vocabulary" = ubiquitous language within the context
"X-ray 'film' ≠ pathology 'film'" = same word different meaning across contexts
"Referral letter / discharge summary" = explicit integration (ACL, events) at boundary

---

### ⚙️ How It Works (Mechanism)

```
BOUNDED CONTEXT IN A CODEBASE:

  com.company.sales/              ← Sales Bounded Context
      domain/
          Customer.java           (sales concept of Customer)
          SalesOrder.java
          Discount.java
      application/
          CreateQuoteService.java
      
  com.company.shipping/           ← Shipping Bounded Context
      domain/
          Customer.java           (shipping concept of Customer — DIFFERENT class)
          Shipment.java
          DeliveryAddress.java
      application/
          ScheduleShipmentService.java
          
  com.company.integration/        ← Integration (ACL)
      SalesOrderToShipmentTranslator.java
      (translates Sales context order → Shipping context shipment)
```

---

### 🔄 How It Connects (Mini-Map)

```
Domain Model (context-specific model within the boundary)
        │
        ▼ (boundary defines where the model applies)
Bounded Context ◄──── (you are here)
(explicit boundary; precise language inside; translation at the edge)
        │
        ├── Anti-Corruption Layer: pattern for integrating across bounded context boundaries
        ├── Context Map: visualization of how bounded contexts relate to each other
        ├── Ubiquitous Language: the shared vocabulary within one bounded context
        └── Microservices: one potential deployment unit for a bounded context
```

---

### 💻 Code Example

```java
// Same concept "Customer" — two different bounded contexts, two different models:

// Sales Bounded Context:
package com.company.sales.domain;
public record Customer(
    CustomerId id,
    String fullName,
    CustomerTier tier,           // Sales cares: Bronze, Silver, Gold, Platinum
    Money lifetimeValue,         // Sales cares: revenue potential
    SalesRepId assignedSalesRep  // Sales cares: who manages this account
) {
    public boolean qualifiesForEnterpriseDiscount() {
        return tier == CustomerTier.GOLD || tier == CustomerTier.PLATINUM;
    }
}

// Shipping Bounded Context — different Customer model!
package com.company.shipping.domain;
public record Customer(
    CustomerId id,               // Same identifier — allows cross-context lookup
    String displayName,          // Shipping only needs display name
    List<ShippingAddress> addresses,  // Shipping cares: where to ship
    String preferredCarrierId,        // Shipping cares: which carrier
    boolean signatureRequired         // Shipping cares: delivery confirmation
) {
    public ShippingAddress defaultAddress() {
        return addresses.stream()
            .filter(ShippingAddress::isDefault)
            .findFirst().orElseThrow(NoDefaultAddressException::new);
    }
}

// Integration: Sales order → Shipping request (ACL translates):
class SalesOrderFulfillmentAdapter {
    ShipmentRequest createShipmentRequest(SalesOrder salesOrder) {
        // Load customer from SHIPPING context (not sales context):
        shipping.Customer shippingCustomer = shippingCustomerRepo.findById(salesOrder.customerId());
        
        // Translate Sales model → Shipping model:
        return new ShipmentRequest(
            ShipmentId.generate(),
            shippingCustomer.defaultAddress(),
            salesOrder.items().stream().map(this::toShipmentItem).toList(),
            shippingCustomer.preferredCarrierId()
        );
        // SalesOrder: never passed to shipping context. Translated at the boundary.
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Bounded Context = Microservice | Not necessarily. A bounded context defines a model boundary; a microservice is a deployment unit. A monolith can have multiple well-defined bounded contexts as modules. Microservices are one way to enforce context boundaries (separate deployment = separate code), but you can also use packages, modules, or namespaces in a monolith |
| Each entity belongs to only one bounded context | An entity may exist in multiple bounded contexts with different representations. `Customer` in Sales context has one structure; in Shipping context, a different structure. They share the same `CustomerId` (cross-context identifier), but the model is context-specific. The KEY (CustomerId) is shared; the VALUE (attributes and behavior) is context-specific |
| Bounded contexts must communicate via APIs | Not necessarily. Integration options: synchronous API calls, asynchronous events, shared database with bounded table ownership (less ideal but sometimes pragmatic), or in-process calls in a monolith. The bounded context defines the MODEL boundary, not necessarily the deployment or communication boundary |

---

### 🔥 Pitfalls in Production

**Context boundary violation — importing another context's model directly:**

```java
// BAD: Shipping context imports and uses Sales context's domain model:
package com.company.shipping.application;

import com.company.sales.domain.SalesOrder;  // VIOLATION: importing across context boundary
import com.company.sales.domain.Customer;    // VIOLATION: sales Customer in shipping code

class ShipmentCreationService {
    void createShipment(SalesOrder salesOrder) {  // Sales model leaked into Shipping!
        // Shipping now coupled to Sales model. Sales changes: shipping breaks.
        Address address = salesOrder.getCustomer().getBillingAddress(); // Using Sales concept
    }
}

// FIX: Shipping context receives its own input (translated at boundary):
package com.company.shipping.application;

class ShipmentCreationService {
    void createShipment(ShipmentRequest request) {  // Shipping's own type
        // ShipmentRequest: shipping-specific concept.
        // Created by integration layer (ACL) that translates SalesOrder → ShipmentRequest.
        shipping.Customer customer = customerRepo.findById(request.customerId());
        // Uses SHIPPING's Customer, not Sales Customer.
    }
}
```

---

### 🔗 Related Keywords

- `Anti-Corruption Layer` — pattern for translating across bounded context boundaries
- `Context Map` — DDD tool visualizing how bounded contexts relate and integrate
- `Ubiquitous Language` — the precise vocabulary shared within one bounded context
- `Microservices` — one deployment strategy for bounded contexts (1 context = 1 service)
- `Modular Monolith` — bounded contexts as modules within a single deployable unit

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Explicit boundary where a domain model   │
│              │ applies. Inside: precise language.        │
│              │ Outside: translation required.            │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Large domain with multiple subdomains;    │
│              │ multiple teams; same words mean different │
│              │ things in different parts of the system   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Small system with one team, one clear     │
│              │ domain — over-partitioning adds           │
│              │ complexity without benefit                │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Hospital departments: 'film' means       │
│              │  X-ray in Radiology, medical record in   │
│              │  Admin — precise within each department." │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Context Map → Anti-Corruption Layer →     │
│              │ Ubiquitous Language → Microservices       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A company has three bounded contexts: Orders, Inventory, and Shipping. An order is placed, which requires checking inventory and scheduling shipping — a cross-context workflow. Option A: Orders context calls Inventory and Shipping synchronously (REST calls within the same transaction). Option B: Orders context publishes an `OrderPlaced` event; Inventory and Shipping react asynchronously. Compare these approaches from the perspective of bounded context isolation: which option better maintains context independence, and what does each approach imply about coupling, consistency, and failure handling?

**Q2.** Your team identifies a potential bounded context boundary: "should Product Catalog and Inventory be separate bounded contexts, or one?" The Product Catalog team cares about: product descriptions, images, SEO attributes, categories, pricing. The Inventory team cares about: stock levels, warehouse locations, reorder points, supplier lead times. Both use the concept "Product." What criteria would you use to decide if these should be one or two bounded contexts? What are the integration costs of separating them vs. the model-clarity costs of keeping them together?
