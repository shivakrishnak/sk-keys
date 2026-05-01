---
layout: default
title: "Anti-Corruption Layer"
parent: "Microservices"
nav_order: 633
permalink: /microservices/anti-corruption-layer/
number: "633"
category: Microservices
difficulty: ★★★
depends_on: "Domain-Driven Design (DDD), Bounded Context, Service Decomposition"
used_by: "Strangler Fig Pattern, Service Decomposition, Bounded Context"
tags: #advanced, #architecture, #microservices, #pattern
---

# 633 — Anti-Corruption Layer

`#advanced` `#architecture` `#microservices` `#pattern`

⚡ TL;DR — An **Anti-Corruption Layer (ACL)** is a translation layer that protects a service's domain model from being "corrupted" by an external system's model. It translates between the external model and your internal model, so your domain remains clean even when integrating with messy legacy systems or third-party APIs.

| #633            | Category: Microservices                                            | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------------------------- | :-------------- |
| **Depends on:** | Domain-Driven Design (DDD), Bounded Context, Service Decomposition |                 |
| **Used by:**    | Strangler Fig Pattern, Service Decomposition, Bounded Context      |                 |

---

### 📘 Textbook Definition

An **Anti-Corruption Layer (ACL)** is a design pattern (introduced in Eric Evans's DDD) that isolates a Bounded Context from the model of an external system or upstream Bounded Context by providing a translation layer. Without an ACL, integrating with an external system requires importing its model into your domain — gradually "corrupting" your clean domain model with foreign concepts, naming conventions, and data structures. The ACL acts as a bidirectional translator: inbound — it transforms external DTOs/responses into your internal domain model; outbound — it transforms your domain commands into the format the external system expects. It is typically implemented as an Adapter (wrapping the external client), a Gateway (encapsulating all communication with an external system), or a Repository implementation (abstracting data access from an external source). The ACL is particularly valuable when: (1) integrating with a legacy system with a poor model, (2) integrating with a third-party SaaS API you cannot control, (3) a downstream context must not be forced to adopt an upstream context's model (Conformist would be the alternative).

---

### 🟢 Simple Definition (Easy)

An Anti-Corruption Layer is a protective wrapper around an external system. When your code needs data from a messy external API, the ACL translates that data into your clean internal format — your domain never knows about the external system's weird structure.

---

### 🔵 Simple Definition (Elaborated)

You are building an e-commerce platform and need to integrate with a legacy ERP system that was designed in the 1990s with cryptic field names: `CUST_NO`, `ORD_DT`, `ITM_CD`. If you use these names directly in your domain code, your codebase gradually looks like the ERP system — confusing, unmaintainable, and coupled to the ERP's design decisions. An ACL wraps the ERP integration: external code calls `ErpGateway.getCustomer("CUST-001")`, which internally calls `LEGACY_ERP_API(CUST_NO="CUST-001")` and translates the response into your domain object `Customer(id, name, email, address)`. Your domain is clean; only the ACL layer knows about `CUST_NO`.

---

### 🔩 First Principles Explanation

**ACL structure — the three roles:**

```
┌─────────────────────────────────────────────────────────────────────┐
│ YOUR DOMAIN (clean, uses Ubiquitous Language)                       │
│                                                                     │
│  OrderFulfilmentService.fulfil(Order order)                        │
│    → needs: ShipmentQuote (YOUR model)                             │
│    → needs: ShipmentId (YOUR model)                                │
│                                                                     │
│ ─ ─ ─ ─ ─ ─ ANTI-CORRUPTION LAYER ─ ─ ─ ─ ─ ─ ─ ─ ─ ─           │
│                                                                     │
│  FedExShippingGateway (ACL implementation)                         │
│    getQuote(Order order) → translates to FedEx format              │
│      → YOUR Order → FedEx CreateShipmentRequest                   │
│    shipOrder(Order order) → calls FedEx API                        │
│      → FedEx response → YOUR ShipmentId                           │
│                                                                     │
│ ─ ─ ─ ─ ─ ─ EXTERNAL SYSTEM ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─          │
│                                                                     │
│  FedEx REST API                                                     │
│    POST /v1/rates/quotes                                            │
│    requestBody: {shipper:{..}, recipient:{..}, packages:[..]}      │
│    response: {shipmentId:"794...", totalNetCharge:{amount:..}}     │
└─────────────────────────────────────────────────────────────────────┘
```

**Three ACL implementation roles:**

```
1. GATEWAY: encapsulates all communication with ONE external system
   interface ShippingGateway {
     ShipmentQuote getQuote(Order order);
     ShipmentId ship(Order order);
     ShipmentStatus track(ShipmentId id);
   }
   → Single interface for everything FedEx-related
   → Swap FedEx for UPS: rewrite ShippingGateway, domain is untouched

2. TRANSLATOR: pure translation between models (no I/O)
   class FedExOrderTranslator {
     FedExShipmentRequest toFedExRequest(Order order) { ... }
     ShipmentId fromFedExResponse(FedExShipmentResponse response) { ... }
   }
   → Separated from I/O for testability

3. ADAPTER: wraps an external client, matches an internal interface
   class StripePaymentAdapter implements PaymentGateway {
     @Override
     public PaymentResult authorise(PaymentRequest req) {
       StripeChargeParams params = toStripeParams(req); // translate
       StripeCharge charge = stripeClient.charges.create(params); // call Stripe
       return fromStripeCharge(charge); // translate back
     }
   }
```

**ACL for a legacy system — full translation example:**

```java
// Legacy ERP returns this (the "external model"):
// {
//   "CUST_NO": "00123",
//   "ORD_DT": "20240115",
//   "ITM_CD": "PROD-456",
//   "QTY": 3,
//   "UNIT_PRC": "29.99",
//   "DISC_PCT": "10",
//   "SHIP_ADDR_LN1": "123 Main St",
//   "SHIP_CITY": "Springfield",
//   "SHIP_ST": "IL",
//   "SHIP_ZIP": "62701"
// }

// ACL translates this into the domain model:
@Component
class LegacyErpOrderAdapter implements LegacyOrderPort {

    @Autowired LegacyErpClient erpClient;

    @Override
    public LegacyOrderData getOrderData(OrderId orderId) {
        ErpOrderRecord erp = erpClient.fetchOrder(orderId.value());

        // All the ugly translation is HERE — never in the domain:
        return new LegacyOrderData(
            new CustomerId(erp.getCUST_NO()),
            parseDate(erp.getORD_DT()),              // "20240115" → LocalDate
            new ProductId(erp.getITM_CD()),
            new Quantity(Integer.parseInt(erp.getQTY())),
            Money.of(new BigDecimal(erp.getUNIT_PRC()), USD),
            Percentage.of(new BigDecimal(erp.getDISC_PCT())),
            Address.builder()
                .streetLine1(erp.getSHIP_ADDR_LN1())
                .city(erp.getSHIP_CITY())
                .state(erp.getSHIP_ST())
                .postalCode(erp.getSHIP_ZIP())
                .build()
        );
    }
}
// The domain NEVER sees CUST_NO, ORD_DT, ITM_CD, DISC_PCT...
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT an Anti-Corruption Layer:

What breaks without it:

1. Domain model is polluted with external system's concepts — `CUST_NO` in your domain model.
2. Changing the external API requires changes throughout your domain layer.
3. Unit testing your domain requires mocking the external API's complex types.
4. Two teams using the same external system develop independently but both accumulate coupling — each change in the external system requires coordinating two teams.

WITH an Anti-Corruption Layer:
→ External system can change its model/API; only the ACL adapts — domain is unchanged.
→ Swap from FedEx to DHL: implement a new `DhlShippingGateway`, keep `ShippingGateway` interface.
→ Test the domain with a `MockShippingGateway` — no real HTTP calls, no FedEx test account.
→ Legacy migration: as the legacy system is replaced, only the ACL changes.

---

### 🧠 Mental Model / Analogy

> An ACL is like a language interpreter at a diplomatic conference. The ambassador (your domain) speaks only in your country's official language (Ubiquitous Language). The foreign delegation (external system) speaks in their language (the external model). The interpreter (ACL) translates in real-time — the ambassador never learns the foreign language, never adjusts their speech for the foreign delegation's dialect. If the foreign delegation changes their terminology, only the interpreter adapts. The conference (your domain) proceeds in your language throughout.

"Ambassador speaking your language" = your domain model using Ubiquitous Language
"Foreign delegation" = external system with its own model
"Language interpreter" = Anti-Corruption Layer (translates both directions)
"Interpreter adapts to dialect changes" = ACL updated when external API changes
"Conference proceeds in your language" = domain stays clean regardless of external changes

---

### ⚙️ How It Works (Mechanism)

**ACL for the Strangler Fig migration pattern:**

```
STRANGLER FIG + ACL:
  Legacy monolith handles all requests.
  New microservice is gradually built alongside.
  Proxy routes some requests to new service, others to legacy.

  PHASE 1: New service reads from legacy via ACL
    [New OrderService] → [ACL] → [Legacy Monolith API]
    ACL translates legacy order format → new domain model

  PHASE 2: New service writes to new DB, reads from both
    [New OrderService] → writes to [New Orders DB]
                      → reads via [ACL] → [Legacy DB] (for historical data)

  PHASE 3: Legacy reads from new service via reverse ACL
    [Legacy System] → [Reverse ACL] → [New OrderService API]

  PHASE 4: ACL removed, legacy decommissioned
    [New OrderService] → [New Orders DB] (direct, no ACL)
```

---

### 🔄 How It Connects (Mini-Map)

```
Bounded Context
(your clean domain)
        │
        ▼
Anti-Corruption Layer  ◄──── (you are here)
(translation between your model and external model)
        │
        ├── Strangler Fig Pattern → ACL enables incremental legacy migration
        ├── Context Map → ACL is the "Customer with ACL" relationship type
        └── Service Decomposition → ACL protects each new service from legacy model
        │
        ▼
External System
(legacy ERP, third-party API, upstream microservice)
```

---

### 💻 Code Example

**ACL with interface + two implementations (production + mock):**

```java
// The port (interface in your domain) — no external types:
public interface PaymentGateway {
    PaymentAuthorisation authorise(PaymentIntent intent);
    PaymentRefund refund(PaymentAuthorisationId authorisationId, Money amount);
    PaymentStatus getStatus(PaymentAuthorisationId id);
}

// ACL implementation for Stripe (production):
@Profile("!test")
@Component
class StripePaymentAdapter implements PaymentGateway {

    @Autowired StripeClient stripe;  // Stripe's SDK client

    @Override
    public PaymentAuthorisation authorise(PaymentIntent intent) {
        try {
            PaymentIntentCreateParams params = PaymentIntentCreateParams.builder()
                .setAmount(intent.amount().toCents())  // Stripe uses cents
                .setCurrency(intent.amount().currency().getCode().toLowerCase())
                .setPaymentMethod(intent.paymentMethodId().value())
                .setConfirm(true)
                .build();

            com.stripe.model.PaymentIntent stripeIntent =
                com.stripe.model.PaymentIntent.create(params);

            return new PaymentAuthorisation(
                new PaymentAuthorisationId(stripeIntent.getId()),
                AuthorisationStatus.fromStripeStatus(stripeIntent.getStatus()),
                intent.amount()
            );
        } catch (StripeException e) {
            throw new PaymentGatewayException("Stripe authorisation failed", e);
            // Domain gets PaymentGatewayException, not StripeException
            // Stripe library is not exposed to domain layer
        }
    }
}

// ACL implementation for tests (no Stripe dependency):
@Profile("test")
@Component
class InMemoryPaymentAdapter implements PaymentGateway {
    private final Map<PaymentAuthorisationId, PaymentAuthorisation> authorisations
        = new ConcurrentHashMap<>();

    @Override
    public PaymentAuthorisation authorise(PaymentIntent intent) {
        PaymentAuthorisation auth = new PaymentAuthorisation(
            new PaymentAuthorisationId(UUID.randomUUID().toString()),
            AuthorisationStatus.AUTHORISED, intent.amount()
        );
        authorisations.put(auth.id(), auth);
        return auth;
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                                     | Reality                                                                                                                                                                                                                                                                                                        |
| ----------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| An ACL is only needed for legacy systems                          | ACLs are equally valuable for modern third-party APIs (Stripe, Salesforce, AWS services). Any external model you do not control should be wrapped with an ACL — external APIs change without your input and must not pollute your domain                                                                       |
| An ACL is just a DTO mapper                                       | A DTO mapper only converts data structures. An ACL translates semantic meaning — it converts `DISC_PCT=10` into `Percentage.of(10)` (a domain Value Object), handles error translation, and enforces your domain's invariants on incoming data. It may also handle retry, circuit breaking, and fallback logic |
| Every method in the external API needs a corresponding ACL method | The ACL exposes only what your domain needs from the external system. If FedEx has 50 API methods but you only need quoting and shipping, the `ShippingGateway` interface has 3 methods. This is the interface segregation principle applied to external integrations                                          |
| The ACL is the same as a Facade                                   | A Facade simplifies an interface (fewer methods, simpler API). An ACL specifically translates between two distinct domain models. A Facade could exist within one domain; an ACL always bridges two distinct models                                                                                            |

---

### 🔥 Pitfalls in Production

**Exception leakage — external exceptions polluting the domain**

```java
// WRONG: external exception escapes the ACL boundary
class ShippingGateway {
    public ShipmentId ship(Order order) throws FedExApiException { // ← external type!
        return fedExClient.ship(toFedExRequest(order));
    }
}

// Domain must catch FedExApiException — now domain knows about FedEx:
public void fulfil(Order order) {
    try {
        shippingGateway.ship(order);
    } catch (FedExApiException e) {  // WRONG: domain depends on FedEx type
        // ...
    }
}

// CORRECT: ACL translates exceptions too
class FedExShippingAdapter implements ShippingGateway {
    public ShipmentId ship(Order order) { // no checked external exception
        try {
            return toShipmentId(fedExClient.ship(toFedExRequest(order)));
        } catch (FedExApiException e) {
            // Translate to domain exception:
            throw new ShippingServiceUnavailableException("Carrier unavailable", e);
        }
    }
}
// Domain catches ShippingServiceUnavailableException — no FedEx dependency
```

---

### 🔗 Related Keywords

- `Domain-Driven Design (DDD)` — introduced the ACL as a Context Map relationship pattern
- `Bounded Context` — the ACL protects a bounded context from external model contamination
- `Strangler Fig Pattern` — uses ACL as the integration bridge during incremental migration
- `Service Decomposition` — each new service extracted from a monolith uses ACL to interface with the old system

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ PURPOSE      │ Protect domain from external model        │
│              │ corruption                                │
├──────────────┼───────────────────────────────────────────┤
│ IMPLEMENTS   │ Gateway (all comms with one external sys) │
│ AS           │ Adapter (wraps external client)           │
│              │ Translator (pure model conversion)        │
├──────────────┼───────────────────────────────────────────┤
│ EXPOSES      │ Port interface using your domain types    │
│              │ (no external types in the interface)      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "ACL = interpreter between your domain    │
│              │  and the external world. Domain speaks    │
│              │  your language; ACL handles the rest."   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** The ACL pattern requires that no external types (DTOs from the external API, exceptions from the external SDK) cross the ACL boundary into the domain. In practice with Java, this requires careful control over `import` statements. Describe the architectural enforcement mechanism: how can ArchUnit tests verify that classes in the domain layer (`com.example.domain.*`) never import from the external adapter packages (`com.example.infrastructure.stripe.*`, `com.example.infrastructure.fedex.*`)? Write an example ArchUnit rule and explain what it catches.

**Q2.** An ACL translating from a third-party payment API (Stripe) must handle two categories of errors: transient errors (network timeout, temporary unavailability — should be retried) and permanent errors (invalid card, insufficient funds — should propagate immediately as domain exceptions). Describe how the ACL should classify these: given that Stripe returns HTTP 402 for card errors and HTTP 503 for service unavailability, how does the ACL map these to domain exceptions? And how does a Resilience4j `@CircuitBreaker` on the ACL method interact with transient vs permanent exceptions — should the circuit breaker count permanent errors (card decline) toward the failure threshold?
