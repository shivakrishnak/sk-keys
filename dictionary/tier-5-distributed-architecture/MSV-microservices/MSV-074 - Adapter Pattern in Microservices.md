---
id: MSV-074
title: Adapter Pattern in Microservices
category: Microservices
tier: tier-5-distributed-architecture
folder: MSV-microservices
difficulty: ★★★
depends_on:
used_by:
related:
tags:
  - microservices
  - pattern
  - deep-dive
status: draft
version: 0
layout: default
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 74
permalink: /microservices/adapter-pattern-in-microservices/
---

# MSV-074 - Adapter Pattern in Microservices

⚡ TL;DR - Adapter Pattern: a translation layer
that converts one interface to another. In microservices:
adapters appear as (1) Anti-Corruption Layer (ACL) -
isolates your domain model from a legacy system's
model; (2) Protocol adapter - REST to gRPC, HTTP
to AMQP; (3) Data format adapter - transform
external API response into your internal domain
model. The key insight: adapters prevent model
bleed - where external service's messy domain
concepts leak into your clean domain model. When
you remove the external service: delete the adapter.
Your domain stays clean.

| #074 | Category: Microservices | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Ambassador Pattern, Sidecar Pattern, What are Microservices | |
| **Used by:** | Ambassador Pattern | |
| **Related:** | Ambassador Pattern, Sidecar Pattern, What are Microservices, API Gateway, Monolith to Microservices Migration, Technology Migration Strategy | |

---

### 🔥 The Problem This Solves

**EXTERNAL MODEL CONTAMINATION:**
Your Order service integrates with a legacy ERP
system. The ERP models a customer as CUST_ENTITY
with fields like CUST_NO, ACCT_FLG, DEPT_CD.
Without adapter: your Order domain object references
CUST_NO and ACCT_FLG. When the ERP is replaced:
every class that references these fields must
change. With adapter (ACL): ERP's CUST_ENTITY
-> adapter translates to your Customer(id, active,
department). Order service: knows nothing of
CUST_NO. ERP replaced: only adapter changes.

---

### 📘 Textbook Definition

**Adapter Pattern in Microservices** is the application
of the Gang of Four Adapter (Wrapper) structural
pattern at the service integration layer. It converts
the interface of one system into the interface
that another system expects. In microservices
architecture, adapters serve three main purposes:
(1) **Anti-Corruption Layer (ACL)** - from Domain-
Driven Design: a translation layer between bounded
contexts that shields your domain model from
corruption by external model concepts. Introduced
by Eric Evans in Domain-Driven Design (2003).
(2) **Protocol Adapter** - converts between
communication protocols (REST to gRPC, HTTP to
MQ message, REST to SOAP/XML). Often implemented
as a sidecar or ambassador container.
(3) **Data Format Adapter** - maps between data
schemas (external API's field naming to your
domain naming, external enum values to your domain
enums, currency/date format normalization).
Adapters are particularly critical during: (a)
Legacy system integration; (b) Third-party API
integration; (c) Microservices migration (wrapping
a monolith while migrating internals).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Adapter: translation layer between incompatible
interfaces. In microservices: converts external
(messy) models to your (clean) domain models.
Prevents external API changes from propagating
through your codebase.

**One analogy:**
> A power adapter (travel plug adapter): your
> laptop charger (your service) works with 2-pin
> US plug. The hotel in Europe (external service)
> has 2-round-pin Schuko sockets. The travel adapter
> accepts US 2-pin on one side, provides Schuko
> on the other. Your charger: unchanged. The wall
> socket: unchanged. Adapter: translates. If the
> hotel upgrades to USB-C wall sockets: buy a
> new adapter. Charger: still unchanged. Same
> principle: your domain model (charger) never
> changes to match the external system (socket).
> The adapter absorbs all changes.

**One insight:**
The most important property of an adapter is
that it defines a STABILITY BOUNDARY. Inside
the adapter: messy external world. Outside: your
clean domain. When the external world changes:
only the adapter changes. Without an adapter:
changes propagate through your entire codebase.

---

### 🔩 First Principles Explanation

**ANTI-CORRUPTION LAYER (ACL) IN DDD:**

```
EXTERNAL SYSTEM (Legacy ERP: SAP R/3)
  Model:
    SalesOrder {
      VBELN: "0000012345"      // Order number
      KUNNR: "0000987654"      // Customer number
      ERDAT: "20240315"        // Creation date YYYYMMDD
      NETWR: 99999             // Net value in cents
      WAERS: "USD"             // Currency
    }

ACL (Anti-Corruption Layer):
  SapOrderAdapter {
    fun translate(sap: SalesOrder): Order {
      return Order(
        id = sap.VBELN.trimStart('0'),
        customerId = sap.KUNNR.trimStart('0'),
        createdAt = LocalDate.parse(
          sap.ERDAT,
          DateTimeFormatter.ofPattern("yyyyMMdd")),
        total = Money(
          BigDecimal(sap.NETWR)
            .divide(BigDecimal(100)),
          Currency.of(sap.WAERS))
      )
    }
  }

YOUR DOMAIN:
  Order {
    id: "12345"                // Clean, no leading zeros
    customerId: "987654"
    createdAt: 2024-03-15      // Proper LocalDate
    total: Money(999.99, USD)  // Proper BigDecimal
  }
  // NO SAP field names in your domain
  // SAP replaced? Only SapOrderAdapter changes
```

---

### 🧪 Thought Experiment

**THIRD-PARTY API CHANGE: ADAPTER SAVES THE DAY**

```
SCENARIO: Your order-service uses Shippo for
shipping. Shippo deprecates v1 API.

v1 API: POST /v1/shipments
  { "address_from": ...,
    "parcels": [{ "length": 10, "width": 8,
                  "distance_unit": "in",
                  "mass_unit": "lb" }] }

v2 API: POST /v2/shipments
  { "origin": ...,
    "packages": [{ "dimensions": {
      "length_cm": 25.4, "width_cm": 20.3 },
      "weight_kg": 0.68 }] }
  (different names + metric units)

WITHOUT ADAPTER:
  Order domain references v1 field names
  Change: update 8 classes, 40 test cases
  Risk: high (domain contaminated)

WITH ADAPTER:
  ShippingAdapter interface (your domain):
    createShipment(origin, destination, package)
  
  ShippoV1Adapter implements ShippingAdapter
  ShippoV2Adapter implements ShippingAdapter
    // Handles: field rename, unit conversion
  
  Swap: inject ShippoV2Adapter in DI config
  Change: 1 adapter class, 1 DI config change
  Domain: ZERO changes
```

---

### 🧠 Mental Model / Analogy

> Adapter pattern is like a diplomatic interpreter.
> When the UN Secretary General (your domain)
> speaks to the French delegate (external API):
> the interpreter converts between languages and
> cultural contexts. The Secretary General speaks
> in their natural concepts. If France changes
> its protocol (API v2): you get a new interpreter
> (new adapter). The Secretary General: unchanged.
> The critical insight: the interpreter is disposable.
> Adapters are MEANT to be replaced.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Adapter: converts one interface to another. Like
a universal plug adapter: your service speaks
your language; external service speaks a different
language; adapter translates between them.

**Level 2 - Basic implementation (junior developer):**
Define a port (interface) in your domain:
`PaymentGateway.charge(amount, currency, card)`.
Implement an adapter: `StripePaymentAdapter
implements PaymentGateway`. The adapter translates
your domain calls to Stripe API calls. Your domain:
never imports Stripe SDK directly.

**Level 3 - Anti-Corruption Layer (mid-level):**
ACL in DDD: a complete translation boundary between
bounded contexts. When integrating with a legacy
monolith: create an ACL service that exclusively
handles all communication with the monolith. This
service translates the monolith's model to your
domain model. Other services: call the ACL, never
call the monolith directly. Monolith changes:
only the ACL changes.

**Level 4 - Strangler Fig + Adapter (senior):**
Strangler Fig Migration: adapter's role:
(1) Facade adapter: new services present old
monolith API to legacy clients while calling
new microservices internally; (2) ACL adapter:
new microservices call monolith through an ACL
(new domain stays clean); (3) Data sync adapter:
bidirectional sync between monolith DB and
microservice DB during migration. The adapter
layer is migration scaffolding - remove when
migration is complete.

**Level 5 - Anti-patterns to avoid (principal):**
Leaky adapter: exposes the external system's
CONCEPTS through its interface. Example:
`ShippoAdapter.getShippoShipmentId()` leaks
the fact that Shippo is used. Port should be:
`ShippingAdapter.getShipmentTrackingId()`. Logic
creep: adapters accumulate business logic over
time. Adapter's job: pure TRANSLATION. If a
business analyst needs to change this code, it
should NOT be in the adapter.

---

### ⚙️ How It Works (Mechanism)

```java
// PORT: domain interface (in your package)
// No external dependencies
public interface ShippingPort {
    ShipmentQuote getQuote(
        Address origin,
        Address destination,
        PackageDimensions pkg);
    
    TrackingInfo getTracking(String shipmentId);
}

// ADAPTER: external library dependency here only
// Only this class imports Shippo SDK
@Component
@ConditionalOnProperty(
    name = "shipping.provider",
    havingValue = "shippo")
public class ShippoShippingAdapter
        implements ShippingPort {
    
    @Override
    public ShipmentQuote getQuote(
            Address origin,
            Address destination,
            PackageDimensions pkg) {
        // TRANSLATE: your domain -> Shippo API
        var req = new ShippoShipmentRequest();
        req.setAddressFrom(toShippoAddress(origin));
        req.setAddressTo(toShippoAddress(destination));
        req.setParcels(List.of(toShippoParcel(pkg)));
        
        // CALL: external API
        var resp = shippoClient.createShipment(req);
        
        // TRANSLATE: Shippo response -> your domain
        return ShipmentQuote.builder()
            .provider("SHIPPO")
            .estimatedDays(resp.getEstimatedDays())
            .rates(resp.getRates().stream()
                .map(this::toRate)
                .collect(toList()))
            .build();
    }
    // All Shippo field names CONTAINED here only
    // Domain classes: never reference Shippo fields
}
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
HEXAGONAL ARCHITECTURE WITH ADAPTERS:

  EXTERNAL            ADAPTER LAYER       DOMAIN CORE
  ___________         _____________       ___________
  
  REST Client  ---->  InboundAdapter  --> OrderService
  (HTTP/JSON)         (HTTP -> domain)    (pure logic)
  
  SAP ERP      ---->  SapOrderACL     --> OrderService
  (BAPI/RFC)          (SAP -> domain)     (uses clean
                                           Order model)
  
  Stripe API   <----  StripeAdapter   <-- PaymentSvc
  (REST+SDK)          (domain->Stripe)    (uses Port)
  
  Kafka        <----  KafkaAdapter    <-- OrderService
  (Avro events)       (domain->Avro)      (publishes
                                           DomainEvents)
  
  Key insight:
  Domain core: ZERO imports of Stripe, SAP, Kafka.
  Adapter replacement: one class, no domain changes.
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: domain contaminated vs clean adapter**

```java
// BAD: external model bleeds into domain
import com.stripe.model.PaymentIntent; // LEAKED

@Entity
public class Order {
    // LEAKED: Stripe IDs in domain model
    private String stripePaymentIntentId;
    private String stripeCustomerId;
    // Stripe replaced: Order.java must change
    // All Order tests: must mock Stripe
    // Kafka events: Stripe IDs leak to all consumers
    
    public void processPayment(
            PaymentIntent paymentIntent) { // LEAKED
        this.stripePaymentIntentId =
            paymentIntent.getId();
        this.status = OrderStatus.PAID;
    }
}
```

```java
// GOOD: adapter isolates domain from Stripe
@Entity
public class Order {
    private String paymentId;       // provider-agnostic
    private String paymentProvider; // "STRIPE", "PAYPAL"
    // Stripe replaced with PayPal: Order.java UNCHANGED
    
    public void markPaid(
            String paymentId, String provider) {
        this.paymentId = paymentId;
        this.paymentProvider = provider;
        this.status = OrderStatus.PAID;
    }
}

// ADAPTER: all Stripe-specific code here
@Component
public class StripePaymentAdapter
        implements PaymentPort {
    
    @Override
    public PaymentResult charge(
            Money amount, PaymentMethod method) {
        // Build Stripe request
        PaymentIntentCreateParams params =
            PaymentIntentCreateParams.builder()
                .setAmount(amount.toCents())
                .setCurrency(
                    amount.getCurrency()
                        .getCode().toLowerCase())
                .setPaymentMethod(
                    method.getProviderToken())
                .setConfirm(true)
                .build();
        
        PaymentIntent intent =
            PaymentIntent.create(params);
        
        // TRANSLATE Stripe response to domain
        return new PaymentResult(
            intent.getId(),  // opaque to domain
            "STRIPE",
            intent.getStatus().equals("succeeded")
                ? PaymentStatus.SUCCESS
                : PaymentStatus.FAILED
        );
    }
}
// Domain: paymentPort.charge(amount, method)
// No Stripe imports or concepts in domain
// Stripe replaced: delete StripePaymentAdapter,
//   add PayPalPaymentAdapter, update DI config
// Domain classes: ZERO changes
```

---

### ⚖️ Comparison Table

| Pattern | Focus | Direction | Location |
|---|---|---|---|
| **Adapter (ACL)** | Model translation | In/Out | Application module |
| **Ambassador** | Outbound proxy | Outbound | Sidecar container |
| **Facade** | Simplify interface | Inbound | API layer |
| **Proxy** | Add behavior | Transparent | Infrastructure |
| **Strangler Fig** | Incremental migration | Both | Architecture |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Adapter is just a mapper (DTO conversion) | The adapter pattern is more than field mapping. A proper ACL: (1) translates CONCEPTS not just fields: external `CUST_ACCT_FLG = 1` becomes your domain `customer.active = true`, not `customer.custAcctFlg = 1`; (2) handles domain-level validation of external data; (3) provides a stability boundary. A simple DTO mapper is a tactical detail; an ACL is a strategic architecture boundary. |
| Once you have an adapter, you are safe from external changes | Adapters protect against INTERFACE changes. They do NOT protect against SEMANTIC changes: if Stripe changes what "succeeded" means, the behavior change might not be caught at the adapter level. You still need: end-to-end contract tests (Pact), monitoring for semantic changes, and changelog reviews when external systems release new versions. Adapters handle syntax; semantics require testing. |
| Logic creep is obvious and easy to prevent | In practice, adapters grow silently. Every new feature that touches the external system: "let's add it to the adapter." After 2 years: the adapter contains 800 lines with carrier selection algorithms, caching, feature flags. The rule: if a business analyst needs to change this code, it should NOT be in the adapter. Schedule quarterly adapter reviews. |

---

### 🚨 Failure Modes & Diagnosis

**Logic creep: adapter becomes a service**

**Symptom:**
`ShippoShippingAdapter` started as 50 lines of
translation code. Now: 800 lines. Contains:
shipping cost calculation, carrier selection
logic based on package weight + destination,
retry with custom backoff, caching of rates,
feature flags for carrier availability. Business
analysts ask to change carrier selection: they
must go through the adapter (hidden business logic).

**Root Cause:**
Adapter is the only place the team touches shipping.
Every new feature: "let's add it to the adapter".
No architecture review: drift goes unnoticed.
After 2 years: the adapter IS the shipping domain.

**Fix:**
```
Review: count if-statements in the adapter
  0-5: pure translation (healthy)
  50+: logic creep (refactor needed)
  
Extract domain logic OUT of adapter:
  ShipmentCostCalculator (domain service)
  CarrierSelectionStrategy (domain service)
  
Keep in adapter ONLY:
  Shippo API field translation
  HTTP call to Shippo
  Response field mapping
  
Rule: if a business analyst must change this,
  it MUST NOT be in the adapter
```

---

### 🔗 Related Keywords

**The general pattern:**
- `Ambassador Pattern` - ambassador = sidecar
  adapter for outbound traffic

**Where adapters are most critical:**
- `Monolith to Microservices Migration` - ACL
  protects new microservices from monolith model
- `Technology Migration Strategy` - adapter
  enables incremental technology replacement

---

### 📌 Quick Reference Card

```
+--------------------------------------------------+
| DEFINITION   | Translates between incompatible   |
|              | interfaces; shields domain        |
+--------------+-----------------------------------+
| FORMS        | ACL (DDD), Protocol adapter,      |
|              | Data format adapter               |
+--------------+-----------------------------------+
| KEY RULE     | Pure translation only; domain     |
|              | never imports external SDK        |
+--------------+-----------------------------------+
| ONE-LINER    | "External change = 1 adapter      |
|              |  class, 0 domain class changes"  |
+--------------------------------------------------+
```

**If you remember only 3 things:**
1. Adapter = translation layer. External model
   stays OUTSIDE your domain. Domain objects:
   never import external SDK types.
2. ACL (Anti-Corruption Layer) = DDD concept.
   Protects your domain from being contaminated
   by external model concepts.
3. Anti-pattern: logic creep. Adapter = pure
   translation. Business logic in adapter =
   invisible business service.

**Interview one-liner:**
"Adapter Pattern in Microservices: translation
layer between your domain and external systems.
Three forms: (1) ACL (Anti-Corruption Layer) -
DDD concept, shields domain from legacy/external
model contamination; (2) Protocol adapter - REST
to gRPC, HTTP to AMQP; (3) Data format adapter -
maps external field names to your domain model.
Key rule: domain classes NEVER import external
SDK types. External system changes: only adapter
changes. Anti-pattern: logic creep - keep adapters
as pure translation, zero business logic."

---

### 💡 The Surprising Truth

The most valuable adapter you'll ever write is
not between external APIs - it's between YOUR
OWN services' bounded contexts. When `order-service`
consumes events from `payment-service`: should
`order-service` use `payment-service`'s domain
objects directly? No. `order-service` should have
an adapter that translates `PaymentService`'s
PAYMENT_COMPLETED event into `order-service`'s
OWN `PaymentConfirmed` event. Why: (1) `payment-service`
events might contain data irrelevant to orders;
(2) `payment-service` might change its event schema;
(3) `order-service` unit tests should not need
`payment-service` types. Internal ACLs between
your own microservices: the difference between
a well-architected system and a distributed monolith.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **IDENTIFY** Review `order-service` and find
   5 places where external model concepts have
   leaked into the domain. For each: propose
   the adapter refactoring.
2. **IMPLEMENT** Given: SAP ERP BAPI response
   with 15 SAP-specific fields. Implement an
   ACL in Java: translate to your `Order` domain
   model. Ensure: no SAP types in `Order` or
   any class that uses `Order`.
3. **HEXAGONAL** Draw the hexagonal architecture
   for `order-service`: show all ports (interfaces)
   and adapters (implementations). What lives
   in domain core vs adapter layer?
4. **REFACTOR** Given the 800-line `ShippoShippingAdapter`:
   move business logic to domain services, leave
   only translation in adapter. Show before/after
   line counts and class responsibilities.
5. **INTERNAL ACL** `order-service` consumes
   `PaymentCompleted` events from `payment-service`.
   Design the internal ACL: adapter interface,
   translation logic, and what the `order-service`
   domain calls instead of the raw Kafka message.

---

### 🧠 Think About This Before We Continue

**Q1.** You are migrating from a monolith to
microservices using the Strangler Fig pattern.
The monolith has a Customer entity with 50 fields
(many legacy: LEGACY_FLG, OLD_ACCT_NO, DEPR_CODE).
New `customer-service` uses a clean 12-field model.
Design the bidirectional adapter: how does the
new service expose data to the monolith, and how
does it consume data FROM the monolith, without
importing the monolith's model in either direction?

**Q2.** Your team decides to replace Stripe with
Adyen. You have: (a) an existing `StripePaymentAdapter`,
(b) 3 microservices that call `PaymentPort`. Using
the adapter pattern: what is the exact migration
plan? List all files changed, the deployment
sequence, and how you verify no Stripe API calls
happen after the migration.

**Q3.** Debate: every microservice should have
an adapter layer for ALL inter-service communication,
even between your own services. Arguments for
and against. At what team size or service count
does the overhead of internal ACLs pay off vs
become a maintenance burden?