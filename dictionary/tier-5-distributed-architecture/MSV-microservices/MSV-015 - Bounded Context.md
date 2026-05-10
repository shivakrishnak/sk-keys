---
layout: default
title: "Bounded Context"
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 15
permalink: /microservices/bounded-context/
id: MSV-015
category: Microservices
difficulty: ★★★
depends_on: Domain-Driven Design, Service Decomposition, Ubiquitous Language
used_by: Anti-Corruption Layer, Aggregate, Service Decomposition
related: Aggregate, Context Map, Anti-Corruption Layer
tags:
  - microservices
  - architecture
  - pattern
  - deep-dive
  - distributed
status: complete
version: 2
---

# MSV-015 - Bounded Context

⚡ TL;DR - A Bounded Context is a DDD strategic pattern that defines an explicit boundary within which a specific domain model and its Ubiquitous Language apply, preventing model corruption across context lines.

| #630 | Category: Microservices | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Domain-Driven Design, Service Decomposition, Ubiquitous Language | |
| **Used by:** | Anti-Corruption Layer, Aggregate, Service Decomposition | |
| **Related:** | Aggregate, Context Map, Anti-Corruption Layer | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An e-commerce platform has a single `Product` class used everywhere. In the Catalog microservice it has fields for description, images, SEO keywords, and categories. In the Inventory service it has warehouse bin locations and reorder thresholds. In the Pricing service it has promotional rules, VAT codes, and cost price. All these fields live in one god-class `Product` with 60 fields. When the Catalog team changes the `description` field type, the Pricing service breaks even though it doesn't use `description`. Every schema migration requires all four teams to synchronise.

**THE BREAKING POINT:**
A shared model that tries to satisfy all contexts satisfies none of them well. Null fields proliferate. The class becomes a god-object. Teams step on each other's changes. The "shared product schema" becomes the single biggest source of inter-team coupling and production incidents.

**THE INVENTION MOMENT:**
This is exactly why Eric Evans introduced the Bounded Context concept - to give each part of the system the freedom to model the same real-world concept differently, within an explicitly defined boundary where that model is coherent and consistent.


**EVOLUTION:**
Bounded Context was introduced by Eric Evans in "Domain-Driven Design" (2003) as the solution to shared models that mean different things to different teams. As microservices became mainstream (2013-2016), Bounded Context became the primary tool for defining service boundaries - providing a theoretical foundation that naive "one service per entity" decomposition had lacked. The discipline evolved from an OO design concept to the principal architecture pattern for distributed systems: a Bounded Context defines not just the language boundary but the ownership boundary, the deployment boundary, and the consistency boundary of a microservice.

**EVOLUTION:**
Bounded Context was introduced by Eric Evans in "Domain-Driven Design" (2003) as the solution to shared models that mean different things to different teams. As microservices became mainstream (2013-2016), Bounded Context became the primary tool for defining service boundaries - providing a theoretical foundation that naive "one service per entity" decomposition had lacked. The discipline evolved from an OO design concept to the principal architecture pattern for distributed systems: a Bounded Context defines not just the language boundary but the ownership boundary, the deployment boundary, and the consistency boundary of a microservice.
---

### 📘 Textbook Definition

A **Bounded Context** is an explicit boundary within which a particular domain model is defined and applicable. Within a Bounded Context, every term in the Ubiquitous Language has a precise, unambiguous meaning. Outside the boundary, the same word may mean something entirely different. Bounded Contexts communicate with each other through well-defined integration points (APIs, events, anti-corruption layers), translating between their respective models as needed. In microservices architecture, Bounded Contexts naturally map to service boundaries.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A bounded context is a fenced area where one team's model is king and no one else's definitions interfere.

**One analogy:**
> Think of different countries using the same word in their official language but with different legal meanings. "Employee" in France means a worker with specific legal protections. "Employee" in the US means something different. Each country has its own legal context - the boundaries are explicit (borders), and if you move from one country to another, you need a translator to re-interpret the concept.

**One insight:**
A Bounded Context is not just a naming convention - it is an explicit architectural decision backed by code, deployment, and team ownership. The boundary must be enforced, not just documented.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Within a Bounded Context, a term has exactly one meaning. No ambiguity is permitted.
2. Models exist to solve domain problems. A model that tries to satisfy multiple contexts solves each slightly less well.
3. Changes within one context should never require changes in unrelated contexts.

**DERIVED DESIGN:**
Given Invariant 1, Bounded Contexts must be separated by hard boundaries - at minimum separate packages/modules, ideally separate services with different databases. Within the boundary, the model is free to be as deep and precise as needed. Outside the boundary, a lighter representation (DTO, projection, or shared identifier) is used.

Given Invariant 3, each context owns its own persistence. No cross-context database table sharing. Integration happens through APIs or events, not SQL JOINs.

**Context Map Integration Patterns (how contexts relate):**

| Pattern | Description | Use When |
|---|---|---|
| Shared Kernel | Both contexts share a common model subset | Two closely related teams with high trust |
| Customer-Supplier | Upstream context provides API for downstream | Formal upstream/downstream relationship |
| Conformist | Downstream adopts upstream's model wholesale | Integrating with a system you cannot change |
| Anti-Corruption Layer | Downstream translates upstream model | Upstream model is poorly designed or legacy |
| Open Host Service | Context publishes a public, stable API | Many consumers needing the same data |
| Published Language | Shared common language (e.g., OpenAPI, Protobuf) | Open integration across organisational boundaries |

**THE TRADE-OFFS:**
**Gain:** Model purity in each context, true team autonomy, schema independence, easier evolution.
**Cost:** Duplication of domain concepts across contexts (same "customer" appears in multiple contexts), explicit translation code between contexts.

---

### 🧪 Thought Experiment

**SETUP:**
Three bounded contexts all deal with a "Customer":
- **Sales Context:** Customer = lead with deal pipeline stage and sales rep assignment
- **Support Context:** Customer = ticket submitter with SLA tier and support history
- **Billing Context:** Customer = billing account with payment method and invoice history

**WHAT HAPPENS WITHOUT BOUNDED CONTEXTS:**
One shared `Customer` class with fields from all three contexts. The Support team adds a `slaLevel` field. The Sales team runs a migration that renames `customerId` to `accountId`. The Billing service crashes. All three teams must be in the same planning meeting to discuss every schema change. A search for "Customer" in the codebase returns 2,400 occurrences across all three contexts.

**WHAT HAPPENS WITH BOUNDED CONTEXTS:**
Each context has its own `Customer` model. They share only a `customerId` (a shared kernel or correlation ID). Support adds `slaLevel` to their model - Sales and Billing are unaffected. The Billing team renames their fields freely. Translation happens at context boundaries when data must cross: the Sales `Customer` DTO is translated to a `BillingAccountCreationRequest` at the API boundary.

**THE INSIGHT:**
Duplication in bounded contexts is intentional and healthy. Three `Customer` classes each serving their context perfectly is better than one `Customer` class serving all three contexts poorly.

---

### 🧠 Mental Model / Analogy

> Bounded Contexts are like different departments in a large company using the same acronym - "PM" means Project Manager in Engineering, Product Manager in Product, and Post Meridiem to HR's shift schedulers. Each department's context wall prevents these meanings from bleeding across. If HR needs to talk to Engineering about a "PM," they translate: "the person managing the software project."

- "Department wall" → explicit bounded context boundary (package, module, service boundary)
- "'PM' meaning within a department" → ubiquitous language specific to that context
- "Translation meeting between departments" → Anti-Corruption Layer or agreed API mapping
- "The company org chart" → Context Map showing how bounded contexts relate

Where this analogy breaks down: in companies, department walls are cultural and approximate. In DDD, the boundary must be enforced technically - shared databases, shared code, or direct cross-context imports violate the boundary even if teams claim they have one.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
A bounded context is a zone in which one specific meaning applies. Like how "bar" means a counter where drinks are served in one context, and a metallurgy term in another - each context keeps its definition clear and separate.

**Level 2 - How to use it (junior developer):**
Identify your business domains and where the same word means different things. Create separate packages (or services) for each. Each context gets its own classes with its own field names, even if they represent the "same" real-world thing. Pass only IDs across context boundaries - reconstruct the full object within the recipient context.

**Level 3 - How it works (mid-level engineer):**
In microservices, each bounded context typically becomes its own service (or a small group of related services). The context boundary is enforced by network and database boundaries. Integration is via API calls or domain events. When a context needs data from another context, it either calls the other context's API or subscribes to its events and maintains its own projection of external data. Context Maps document the integration strategy between every pair of communicating contexts.

**Level 4 - Why it was designed this way (senior/staff):**
Evans identified that large-scale modelling failures almost always come from attempting to build a single unified enterprise data model. The Bounded Context concept explicitly rejects that approach in favour of intentional duplication and context-local optimisation. The Context Map patterns (Customer-Supplier, Conformist, ACL, Shared Kernel) name the different power dynamics and integration constraints between teams - a crucial tool for organisational design in large engineering orgs. Vernon's "Implementing Domain-Driven Design" extended this with concrete patterns for integrating contexts via messaging, which directly enables the event-driven microservices architecture.

---

### ⚙️ How It Works (Mechanism)

**Identifying Bounded Contexts with Event Storming:**

```
Event Storming output (simplified for e-commerce):

OrderPlaced ─────► PaymentProcessed ─────► OrderShipped
   (Orders)            (Payments)           (Fulfillment)

CatalogItemAdded ──────────────────────────────────────
   (Catalog)

CustomerRegistered ────────────────────────────────────
   (Identity)

Clusters of events with shared vocabulary = BC candidates
```

**Context Map (how contexts integrate):**

```
┌──────────────────────────────────────────────────┐
│              Context Map                         │
│                                                  │
│  [Catalog]──OpenHostService──►[Search]           │
│                                                  │
│  [Orders]──CustomerSupplier──►[Fulfillment]      │
│                                                  │
│  [Identity]──AntiCorruptionLayer──►[Orders]      │
│   (legacy)                       (new system)    │
│                                                  │
│  [Payments]──PublishedLanguage──►[Orders]        │
│              (PaymentCompleted event)            │
└──────────────────────────────────────────────────┘
```

**Cross-context integration via event:**

```java
// Orders context publishes minimal event (its own model)
public record OrderPlacedEvent(
    String orderId,        // Orders' identifier
    String customerId,     // Shared kernel ID
    List<OrderItemDto> items,
    BigDecimal total
) {}

// Fulfillment context subscribes and builds its OWN model
@EventHandler
public void on(OrderPlacedEvent event) {
    // Translate into Fulfillment context model
    FulfillmentOrder fo = FulfillmentOrder.create(
        FulfillmentOrderId.fromOrderId(event.orderId()),
        event.items().stream()
            .map(FulfillmentItem::from)
            .toList()
    );
    fulfillmentRepo.save(fo);
}
// Fulfillment never imports Orders' domain classes directly
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
Customer places order → Orders Context processes → Publishes `OrderPlaced` event ← YOU ARE HERE → Payments Context subscribes → Payment processed → `PaymentCompleted` event → Orders Context updates status → Fulfillment Context subscribes → Ships order

**FAILURE PATH:**
Orders Context publishes `OrderPlaced` but message broker is down → Event is not delivered to Payments Context → Order stuck in `PENDING_PAYMENT` state → Alert fires on stale `PENDING_PAYMENT` orders → Ops team investigates broker health → Replay mechanism retries event delivery

**WHAT CHANGES AT SCALE:**
At 1000x load, the event-driven integration between bounded contexts creates event lag. Each context subscribes asynchronously - a downstream context may be seconds or minutes behind the upstream context. This eventual consistency must be designed for: the UI shows "processing" states, idempotency keys prevent double-processing of replayed events, and dead letter queues capture events that cannot be processed.

---

### 💻 Code Example

**Example 1 - BAD: God-class spanning multiple contexts:**

```java
// BAD: single Product class used in all contexts
// - 60 fields, many nullable, no clear owner
public class Product {
    private Long id;
    private String name;
    private String description;  // Catalog
    private String imageUrl;     // Catalog
    private String seoTitle;     // Catalog
    private Integer stockLevel;  // Inventory
    private String warehouseBin; // Inventory
    private BigDecimal costPrice;// Pricing
    private BigDecimal vatCode;  // Pricing
    // 50 more fields...
}
```

**Example 2 - GOOD: Separate models per context:**

```java
// GOOD: each bounded context has its own Product model

// Catalog Context
package com.example.catalog.domain;
public class CatalogProduct {
    private ProductId id;
    private String name;
    private String description;
    private List<String> imageUrls;
    private Category category;
}

// Inventory Context
package com.example.inventory.domain;
public class StockItem {
    private ProductId productId; // shared ID only
    private int availableQuantity;
    private String warehouseBinCode;
    private int reorderThreshold;
}

// Pricing Context
package com.example.pricing.domain;
public class PriceList {
    private ProductId productId; // shared ID only
    private Money listPrice;
    private VatCode vatCode;
    private List<PromotionRule> promotionRules;
}
```

**Example 3 - Anti-Corruption Layer (translating legacy model):**

```java
// Legacy system has a badly named, poorly designed CustomerDTO
// ACL translates it into our clean domain model
public class LegacyCustomerAcl {
    private final LegacyCustomerClient legacyClient;

    public Customer translate(String legacyId) {
        LegacyCustomerDTO legacy = legacyClient.find(legacyId);
        // Translate legacy naming conventions into our language
        return Customer.create(
            CustomerId.of(legacy.getCustNo()),  // rename
            legacy.getFullName(),               // map
            Email.of(legacy.getEmailAddr())     // validate + wrap
        );
    }
}
```

---

### ⚖️ Comparison Table

| Integration Pattern | Coupling | Complexity | Autonomy | Best For |
|---|---|---|---|---|
| Shared Kernel | High | Low | Low | Two closely related, trusted teams |
| **Anti-Corruption Layer** | Low | Medium | High | Integrating legacy or poorly designed upstream |
| Customer-Supplier | Medium | Low | Medium | Clear upstream/downstream relationship |
| Conformist | High | Low | Low | Cannot change upstream (SaaS, third party) |
| Published Language | Low | Medium | High | Many contexts consuming one provider |

How to choose: use ACL when upstream model is messy or external (you cannot change it); use Customer-Supplier when there is a clear owner relationship with the ability to negotiate the API.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| One Bounded Context = One Microservice (always) | Bounded Contexts and services are related but not the same. A context may start as a module in a monolith and later become a service |
| Duplication across bounded contexts is bad | Intentional model duplication across contexts is a feature, not a bug - it preserves context autonomy |
| Bounded Contexts must be documented and then implemented | Context boundaries emerge through Event Storming and iterative discovery - they are rarely obvious upfront |
| A Context Map is a system diagram | A Context Map also captures team relationships, trust levels, and integration strategies - it is as much an organisational tool as a technical one |
| The Bounded Context and the Aggregate are the same thing | Aggregates are tactical (within a context); Bounded Contexts are strategic (between contexts). A context can contain dozens of aggregates |

---

### 🚨 Failure Modes & Diagnosis

**1. Context Boundary Violated via Shared Database**

**Symptom:** Changing the Order table schema breaks the Fulfillment service even though they are "separate bounded contexts."

**Root Cause:** Both contexts query the same database tables - the database is the de facto integration point, bypassing the context boundary entirely.

**Diagnostic:**
```bash
# Check if multiple services connect to the same DB schema
grep -rn "jdbc:postgresql" services/*/src --include="*.yml" | \
  sort | uniq  # same DB URL in multiple services = violation
```

**Fix:** Migrate to separate schemas or databases per context. Replace direct DB reads with event subscriptions or API calls. Initially use database views to provide backward-compatible access during migration.

**Prevention:** Assign a single service as the owner of each database schema; all other services access data through that service's API.

**2. Missing Context Map - No Integration Strategy**

**Symptom:** Three teams are building services that need to share customer data. Each builds a different integration approach. One uses direct DB access, one uses REST calls, one has no integration yet.

**Root Cause:** No Context Map was created. Teams independently decided how to integrate without a shared strategy.

**Diagnostic:**
```bash
# Look for signs of inconsistent integration:
grep -rn "direct.db\|shared.schema\|internal.api" \
  docs/architecture/ --include="*.md"
# Check ADRs for integration decisions
ls docs/adr/ | grep -i "integration\|context\|bounded"
```

**Fix:** Facilitate a Context Mapping workshop with all team tech leads. Document each context pair's relationship type and agreed integration pattern. Encode the pattern choices in ADRs.

**Prevention:** Make Context Map review a mandatory step in new service design. Update it whenever integration patterns change.

**3. Ubiquitous Language Drift**

**Symptom:** Code reviews show developers using terms not aligned with the business. Meetings between dev and business take 30 minutes of just making sure everyone means the same thing.

**Root Cause:** No glossary was maintained. New developers learned terms from the code (which used old or incorrect names) rather than from domain experts.

**Diagnostic:**
```bash
# Look for business term inconsistencies
grep -rn "client\|user\|account\|customer" \
  src/orders/ --include="*.java" | \
  grep -v "test" | awk '{print $NF}' | sort | uniq -c | sort -rn
# Multiple synonyms for same concept = language drift
```

**Fix:** Hold a ubiquitous language workshop. Create a glossary per bounded context. Rename code classes and methods to match agreed terms. Update documentation and OpenAPI specs.

**Prevention:** Make each bounded context's glossary visible in the repo (`docs/ubiquitous-language.md`) and include language adherence in code reviews.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Domain-Driven Design` - the strategic pattern container within which Bounded Context is defined
- `Service Decomposition` - bounded contexts are the premier guide for where to draw service lines
- `Ubiquitous Language` - the shared vocabulary that is precisely defined within each bounded context

**Builds On This (learn these next):**
- `Anti-Corruption Layer` - the translation mechanism when integrating two bounded contexts with different models
- `Aggregate` - the tactical pattern that manages consistency within a bounded context
- `Event-Driven Microservices` - the preferred integration mechanism between bounded contexts at scale

**Alternatives / Comparisons:**
- `Shared Kernel` - a DDD integration pattern where two bounded contexts deliberately share a common subset of their model

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ An explicit boundary within which a       │
│              │ domain model has a single, clear meaning  │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Same word meaning different things in     │
│ SOLVES       │ different parts of the system, causing    │
│              │ coupling and model corruption             │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Intentional model duplication across      │
│              │ contexts is healthy - it preserves each   │
│              │ context's freedom to evolve independently │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Multiple teams share domain vocabulary    │
│              │ but use terms differently across areas   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Small team, simple domain with truly      │
│              │ uniform language throughout               │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Model purity per context vs explicit      │
│              │ translation overhead at context borders  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Model duplication is cheaper than        │
│              │  model corruption."                       │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Aggregate → Anti-Corruption Layer →       │
│              │ Ubiquitous Language                       │
└──────────────────────────────────────────────────────────┘
```


---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Explicit boundaries enable implicit communication. When boundaries are undefined, every team has different assumptions about shared concepts - "customer" means something different to billing, fulfillment, and support without anyone knowing there is a disagreement. When boundaries are explicit, each team can evolve its model independently while exposing a clear contract at the boundary. Making implicit assumptions explicit is the core value of Bounded Contexts.

**Where else this pattern appears:**
- **API versioning:** An API version boundary is a Bounded Context at the temporal dimension. Different versions coexist without breaking changes because each version is an explicit boundary with its own contract and its own consumer set.
- **Data warehousing:** A dimensional model (star schema) is a separate Bounded Context from the operational transactional model. The warehouse has its own concept of "customer" (a denormalised dimension table) distinct from the OLTP model - this is correct and expected.
- **Organisational design:** A team's scope of responsibility is a Bounded Context at the organisational level. Teams with unbounded responsibilities ("everything customer-related") become bottlenecks because all other teams need their approval to change anything in that domain.

---

### 💡 The Surprising Truth

The most common misconception about Bounded Contexts is that they map 1:1 with microservices. Eric Evans explicitly stated that Bounded Contexts and microservices are independent concepts: a single microservice can implement multiple Bounded Contexts, and a single Bounded Context can span multiple microservices. The confusion arose because microservices practitioners adopted Bounded Context as their decomposition tool without reading Evans' nuance. The result: teams create one microservice per Bounded Context as a rigid rule, producing either too many tiny services (if contexts are small) or incorrectly bounded services (if contexts are forced to match service granularity).

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Explicit boundaries enable implicit communication. When boundaries are undefined, every team has different assumptions about shared concepts - "customer" means something different to billing, fulfillment, and support without anyone knowing there is a disagreement. When boundaries are explicit, each team can evolve its model independently while exposing a clear contract at the boundary. Making implicit assumptions explicit is the core value of Bounded Contexts.

**Where else this pattern appears:**
- **API versioning:** An API version boundary is a Bounded Context at the temporal dimension. Different versions coexist without breaking changes because each version is an explicit boundary with its own contract and its own consumer set.
- **Data warehousing:** A dimensional model (star schema) is a separate Bounded Context from the operational transactional model. The warehouse has its own concept of "customer" (a denormalised dimension table) distinct from the OLTP model - this is correct and expected.
- **Organisational design:** A team's scope of responsibility is a Bounded Context at the organisational level. Teams with unbounded responsibilities ("everything customer-related") become bottlenecks because all other teams need their approval to change anything in that domain.

---

### 💡 The Surprising Truth

The most common misconception about Bounded Contexts is that they map 1:1 with microservices. Eric Evans explicitly stated that Bounded Contexts and microservices are independent concepts: a single microservice can implement multiple Bounded Contexts, and a single Bounded Context can span multiple microservices. The confusion arose because microservices practitioners adopted Bounded Context as their decomposition tool without reading Evans' nuance. The result: teams create one microservice per Bounded Context as a rigid rule, producing either too many tiny services (if contexts are small) or incorrectly bounded services (if contexts are forced to match service granularity).
---

### 🧠 Think About This Before We Continue

**Q1.** An enterprise has 15 microservices, each claiming to be a "Bounded Context." In reality, 7 of these services all share a central "customer" database table - they only access it via separate repository classes but the schema is shared. A consultant says this is not truly a bounded context implementation. What specific evidence would you gather to determine whether this is a context boundary violation or an acceptable shared kernel? What would you change if it is a violation?

*Hint:* Think about what distinguishes a Shared Kernel (deliberate, governed joint ownership) from a boundary violation (accidental shared access with no governance process). Explore what specific evidence to gather: Is there a joint schema change approval process? Do both teams attend the same schema review meetings? Is the sharing documented as an intentional architectural decision? Absence of any of these suggests an accidental violation, not a shared kernel.

*Hint:* Think about what distinguishes a Shared Kernel (deliberate, governed joint ownership) from a boundary violation (accidental shared access with no governance process). Explore what specific evidence to gather: Is there a joint schema change approval process? Do both teams attend the same schema review meetings? Is the sharing documented as an intentional architectural decision? Absence of any of these suggests an accidental violation, not a shared kernel.

**Q2.** The Orders bounded context publishes `OrderPlaced` domain events that the Notifications and Fulfillment contexts subscribe to. Six months later, the Orders team needs to add a new required field to `OrderPlaced`. What are all the ways this change could break (or silently corrupt data in) downstream contexts, and what versioning strategy for domain events would prevent this failure while allowing the Orders context to evolve?

*Hint:* Think about how domain event schema changes break downstream consumers silently: a new required field causes old consumers to receive an event with a missing field they don't know to check for; a renamed field causes old consumers to silently miss the data. Explore whether schema evolution strategies (semantic versioning on event type names, backward-compatible additions only, consumer-driven contract testing via Pact) would prevent the failure modes, and what a schema registry would add to the solution.

**Q3 (Design Trade-off):** Two Bounded Contexts need to share a concept: the Orders context and the Loyalty context both have a "Customer," but with different models. A product requirement says that when a customer places an order, the Loyalty context must update their points balance in real time - visible on the same confirmation screen. How do you implement near-real-time cross-context consistency without coupling the contexts?

*Hint:* Think about what "real time" means from the user's perspective: does the points balance need to update within the same HTTP response (requiring synchronous coupling between Orders and Loyalty contexts) or is an update within 2-3 seconds acceptable after order confirmation (enabling async domain events)? Explore whether an `OrderPlaced` domain event published by Orders and consumed by Loyalty can satisfy the UI requirement if the confirmation screen polls for the updated loyalty balance after displaying the order confirmation.

*Hint:* Think about how domain event schema changes break downstream consumers silently: a new required field causes old consumers to receive an event with a missing field they don't know to check for; a renamed field causes old consumers to silently miss the data. Explore whether schema evolution strategies (semantic versioning on event type names, backward-compatible additions only, consumer-driven contract testing via Pact) would prevent the failure modes, and what a schema registry would add to the solution.

**Q3 (Design Trade-off):** Two Bounded Contexts need to share a concept: the Orders context and the Loyalty context both have a "Customer," but with different models. A product requirement says that when a customer places an order, the Loyalty context must update their points balance in real time - visible on the same confirmation screen. How do you implement near-real-time cross-context consistency without coupling the contexts?

*Hint:* Think about what "real time" means from the user's perspective: does the points balance need to update within the same HTTP response (requiring synchronous coupling between Orders and Loyalty contexts) or is an update within 2-3 seconds acceptable after order confirmation (enabling async domain events)? Explore whether an `OrderPlaced` domain event published by Orders and consumed by Loyalty can satisfy the UI requirement if the confirmation screen polls for the updated loyalty balance after displaying the order confirmation.
