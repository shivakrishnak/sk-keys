---
layout: default
title: "Anti-Corruption Layer"
parent: "Software Architecture Patterns"
nav_order: 747
permalink: /software-architecture/anti-corruption-layer/
number: "0747"
category: Software Architecture Patterns
difficulty: ★★★
depends_on: Bounded Context, Domain Model, Adapter Pattern, Facade Pattern
used_by: Microservices integration, Legacy migration, Third-party APIs, DDD
related: Bounded Context, Context Map, Adapter Pattern, Strangler Fig Pattern, Facade
tags:
  - architecture
  - ddd
  - pattern
  - integration
  - deep-dive
  - advanced
---

# 747 — Anti-Corruption Layer

⚡ TL;DR — An Anti-Corruption Layer (ACL) is a translation layer that isolates your domain model from external systems by translating their foreign concepts and models into your own domain language — preventing their messy or alien model from corrupting yours.

---

### 📊 Entry Metadata

| #747            | Category: Software Architecture Patterns                                     | Difficulty: ★★★ |
| :-------------- | :--------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Bounded Context, Domain Model, Adapter Pattern, Facade Pattern               |                 |
| **Used by:**    | Microservices integration, Legacy migration, Third-party APIs, DDD           |                 |
| **Related:**    | Bounded Context, Context Map, Adapter Pattern, Strangler Fig Pattern, Facade |                 |

---

### 🔥 The Problem This Solves

**THE CORRUPTION SCENARIO:**
Your clean, well-designed `Order` domain model needs to integrate with a legacy ERP system that has its own concept of an "order" — it's called a "sales transaction," uses numeric status codes (1=open, 2=processing, 7=cancelled, 12=shipped), has split address fields in a different format, and uses a product catalog with numeric IDs that don't match your string SKUs.

**WITHOUT AN ACL:**
Your domain model starts importing the ERP's concepts: status code `7` appears in your code, `salesTransactionId` appears in your `Order`, and conversion logic is scattered everywhere. The ERP's messy, legacy model bleeds into your clean domain — corrupting it.

**WITH AN ACL:**
The ACL sits at the boundary between your domain and the ERP. Your domain knows nothing about status codes or sales transactions — it speaks its own language. The ACL translates ERP responses into your domain types before they enter your system, and translates your domain objects into ERP formats when sending data out.

---

### 📘 Textbook Definition

The Anti-Corruption Layer, introduced by Eric Evans in "Domain-Driven Design," is an isolating layer that provides clients with functionality in terms of their own domain model. The ACL translates between the client's domain model and the model of a foreign system (a legacy system, third-party service, or another bounded context with a different model). The name reflects its purpose: without this layer, the foreign model's concepts, terminology, and structure would "corrupt" the client's own domain model by forcing the client to use the foreign model's vocabulary and structure.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A translation layer at the boundary of your system that prevents foreign models from infecting your domain.

**One analogy:**

> A customs officer at the border. Imports arrive in foreign packaging with foreign labels. The customs officer translates, repackages, and certifies them according to domestic standards before they enter the country. The domestic market (your domain) never sees the foreign packaging — it only sees goods conforming to domestic standards. If foreign standards change, only the customs officer (ACL) needs to update — domestic businesses are unaffected.

**One insight:**
ACL is not about hiding bad code — it's about protecting your domain model's integrity. Even a well-designed external system uses different concepts and vocabulary. The ACL ensures your domain speaks its own consistent language, not a mixture of dialects.

---

### 🔩 First Principles Explanation

**WHAT THE ACL TRANSLATES:**

```
┌──────────────────────────────────────────────────────────┐
│            ANTI-CORRUPTION LAYER TRANSLATIONS            │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Naming (vocabulary):                                    │
│    External "SalesTxn" → Your "Order"                    │
│    External "Client"   → Your "Customer"                 │
│    External status 7   → Your OrderStatus.CANCELLED      │
│                                                          │
│  Structure (model shape):                                │
│    External flat SalesTxn → Your Order with OrderItems   │
│    External split address → Your PostalAddress VO        │
│                                                          │
│  IDs (reference systems):                                │
│    External productCode "P-12345" → Your SKU "ABC-001"   │
│    External customerId 99871 → Your CustomerId UUID      │
│                                                          │
│  Semantics (meaning):                                    │
│    External "confirmed" = billing complete               │
│    Your "CONFIRMED" = customer confirmed order           │
│    → Different meanings for same word!                   │
└──────────────────────────────────────────────────────────┘
```

**ACL POSITION:**

```
┌──────────────────────────────────────────────────────────┐
│           ACL IN THE ARCHITECTURE                        │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Your Domain (clean model)                               │
│       ↕                                                  │
│  ┌─── ACL ──────────────────────────────────────────┐   │
│  │  Facade (one interface for each integration)     │   │
│  │  Service/Adapter (calls external APIs)           │   │
│  │  Translator (maps external types to yours)       │   │
│  └──────────────────────────────────────────────────┘   │
│       ↕                                                  │
│  External System (legacy ERP / third-party / other BC)   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧪 Thought Experiment

**STRIPE PAYMENT INTEGRATION:**
Stripe has its own model: `PaymentIntent`, `PaymentMethod`, `Charge`, `Refund`. Your domain has: `Payment`, `PaymentMethod`, `Refund`.

Without ACL: Your domain code calls Stripe's SDK directly, your `Payment` has `stripePaymentIntentId`, your service classes handle Stripe's error codes.

With ACL: Your domain calls `PaymentGateway.charge(Payment)`. The ACL implementation calls Stripe, handles Stripe-specific errors, maps `PaymentIntent.status` to your `PaymentStatus`, and returns your domain types. Your domain has zero knowledge of Stripe. Replace Stripe with another gateway → replace the ACL implementation, touch nothing in your domain.

---

### 🧠 Mental Model / Analogy

> An ACL is like a universal power adapter for travel. Different countries have different plug shapes and voltages. Your laptop (domain) has one plug. The power adapter (ACL) handles all the conversions — 110V/220V, two-prong/three-prong, European/British/American. Your laptop doesn't need to know about all the world's electrical standards — it just knows its own plug. If you travel to a new country with a new socket standard, you buy a new adapter, not a new laptop.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone):**
A translator between your application and an external system. Your application speaks its own language; the ACL translates to and from whatever language the external system uses.

**Level 2 — How to build it (junior):**
Create an interface in your domain that describes what you need in your domain language: `interface PaymentGateway { PaymentResult charge(Money amount, PaymentMethod method); }`. Create an implementation class that calls the external system and maps the results to your domain types. Your domain depends only on the interface — never on the external system's types directly.

**Level 3 — Design patterns (mid-level):**
The ACL typically combines three patterns: 1) **Facade** — a simplified interface hiding the complexity of the external system; 2) **Adapter** — translates the external system's interface to your domain's interface; 3) **Translator** — the actual data mapping logic. For read operations, the Translator maps external responses to your domain types. For write operations, the Translator maps your domain objects to external request formats.

**Level 4 — Strategic DDD (senior/staff):**
In the DDD Context Map, the ACL represents one specific relationship type between Bounded Contexts: "Customer/Supplier with ACL." You (Downstream) receive concepts from an Upstream system but refuse to let those concepts corrupt your model — you install an ACL. This is contrasted with "Conformist" (you adopt the upstream model as-is, no ACL, your model becomes theirs) and "Partnership" (two teams coordinate and keep models compatible). The ACL is the appropriate strategy when the upstream model is poorly designed, represents a different domain, or when you need independence from the upstream team's decisions.

---

### ⚙️ How It Works (Mechanism)

**ACL structure with all components:**

```
┌──────────────────────────────────────────────────────────┐
│              ACL INTERNAL STRUCTURE                      │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Domain Layer:                                           │
│    interface InventoryService {                          │
│      StockLevel checkStock(ProductId, int qty)           │
│      void reserveStock(ProductId, int qty, OrderId)      │
│    }                                                     │
│    // Domain only knows this interface                   │
│                                                          │
│  ACL Layer (Infrastructure):                             │
│    class LegacyWarehouseACL implements InventoryService{ │
│                                                          │
│      // Facade: simplified view of legacy API            │
│      private LegacyWarehouseFacade warehouseFacade;      │
│                                                          │
│      // Adapter: calls legacy system                     │
│      public StockLevel checkStock(ProductId id, int qty){│
│        // Translate: ProductId → legacy item code        │
│        String itemCode = translator.toItemCode(id);      │
│                                                          │
│        // Call external system (legacy API)              │
│        LegacyStockResponse resp =                        │
│            warehouseFacade.queryStock(itemCode);         │
│                                                          │
│        // Translate response to your domain type         │
│        return translator.toStockLevel(resp, qty);        │
│      }                                                   │
│    }                                                     │
└──────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture

```
┌──────────────────────────────────────────────────────────┐
│            ACL — COMPLETE INTEGRATION FLOW               │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Order Service (domain):                                 │
│    order.submit()                                        │
│    → calls InventoryService.reserveStock(...)            │
│    → (injected via DI: LegacyWarehouseACL)               │
│                                                          │
│  LegacyWarehouseACL (ACL):                               │
│    1. Translates ProductId → legacy item code            │
│    2. Calls legacy SOAP endpoint /reserveItems           │
│    3. Receives legacy XML response                       │
│    4. Maps XML to your StockReservationResult            │
│    5. Maps legacy error codes to your domain exceptions  │
│    6. Returns your domain type                           │
│                                                          │
│  Order Service receives: StockReservationResult          │
│  (knows nothing about SOAP, XML, or legacy item codes)   │
└──────────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**ACL for a payment gateway:**

```java
// Domain interface — in your domain layer
// Uses only your domain types
public interface PaymentGateway {
    PaymentResult charge(Money amount,
                          PaymentMethodToken token,
                          OrderId orderReference);
    RefundResult refund(PaymentId paymentId, Money amount);
}

// ACL Implementation — in infrastructure layer
// Calls Stripe; your domain never imports Stripe's SDK
@Component
public class StripePaymentGatewayACL
        implements PaymentGateway {

    private final StripeClient stripeClient;
    private final StripeTranslator translator;

    @Override
    public PaymentResult charge(Money amount,
                                 PaymentMethodToken token,
                                 OrderId reference) {
        try {
            // Translate: your domain types → Stripe types
            PaymentIntentCreateParams params =
                translator.toStripeParams(
                    amount, token, reference);

            // Call external system
            PaymentIntent intent =
                stripeClient.paymentIntents()
                             .create(params);

            // Translate: Stripe response → your domain types
            return translator.toPaymentResult(intent);

        } catch (CardException e) {
            // Translate Stripe error to your domain exception
            throw new PaymentDeclinedException(
                translator.toDeclineReason(e.getCode()));
        } catch (StripeException e) {
            // Translate technical error to domain exception
            throw new PaymentGatewayException(
                "Payment processing failed", e);
        }
    }

    @Override
    public RefundResult refund(PaymentId paymentId,
                                Money amount) {
        String stripePaymentIntentId =
            translator.toStripeId(paymentId);
        // ... similar translation and ACL logic
    }
}

// Translator — the actual mapping logic
@Component
class StripeTranslator {
    PaymentIntentCreateParams toStripeParams(
            Money amount, PaymentMethodToken token,
            OrderId reference) {
        return PaymentIntentCreateParams.builder()
            .setAmount(amount.amountInMinorUnits())  // pence
            .setCurrency(amount.currency()
                               .code().toLowerCase())
            .setPaymentMethod(token.value())
            .putMetadata("order_id",
                          reference.value().toString())
            .setConfirm(true)
            .build();
    }

    PaymentResult toPaymentResult(PaymentIntent intent) {
        PaymentStatus status = switch (intent.getStatus()) {
            case "succeeded" -> PaymentStatus.SUCCEEDED;
            case "processing" -> PaymentStatus.PROCESSING;
            case "requires_action" ->
                PaymentStatus.REQUIRES_ACTION;
            default -> PaymentStatus.FAILED;
        };
        return new PaymentResult(
            PaymentId.of(intent.getId()),
            status,
            Instant.ofEpochSecond(intent.getCreated()));
    }
}
```

---

### ⚖️ Comparison Table

| Integration Approach | Domain Isolation            | Coupling | Flexibility                  | Effort |
| -------------------- | --------------------------- | -------- | ---------------------------- | ------ |
| **ACL**              | High — full translation     | Loose    | Easy to swap external system | High   |
| Direct integration   | None                        | Tight    | Hard to change               | Low    |
| Conformist           | None (adopt upstream model) | Tight    | Upstream model = your model  | Lowest |
| Shared Kernel        | Partial (shared types)      | Medium   | Shared types must be agreed  | Medium |

---

### ⚠️ Common Misconceptions

| Misconception                  | Reality                                                                                                                |
| ------------------------------ | ---------------------------------------------------------------------------------------------------------------------- |
| ACL is only for legacy systems | ACL is appropriate for any external system with a different model — modern APIs, other microservices, third-party SaaS |
| ACL makes systems slower       | ACL adds translation logic, but this is usually negligible compared to network I/O                                     |
| One ACL per external system    | Yes — one ACL per integration point; each external system has its own adapter and translator                           |
| ACL is an anti-pattern         | ACL is a strategic DDD pattern for domain model protection — it's a solution, not a problem                            |

---

### 🚨 Failure Modes & Diagnosis

**Leaky ACL — external types penetrating domain**

**Symptom:** Your domain service classes import external SDK classes (Stripe's `PaymentIntent`, AWS SDK types). Domain types contain fields like `stripeCustomerId` or `salesforceContactId`.

**Root Cause:** ACL not fully implemented — external types are passed through instead of being translated.

**Diagnostic Check:**

```bash
# Find domain classes importing external SDKs
grep -rn "import com.stripe\|import software.amazon\|import com.twilio" \
  src/main/java/com/yourcompany/domain/ --include="*.java"
# Any result = ACL has a leak
```

**Fix:** Ensure all external types are translated at the ACL boundary. The domain layer should have zero imports from external system packages.

---

### 🔗 Related Keywords

**Prerequisites:**

- `Bounded Context` — the context boundary that ACL protects
- `Domain Model` — what the ACL protects from corruption

**Builds On This:**

- `Context Map` — shows ACL relationships between contexts
- `Strangler Fig Pattern` — migration strategy that uses ACL during legacy replacement

**Related Patterns:**

- `Adapter Pattern` — the design pattern the ACL uses internally
- `Facade Pattern` — another component of the ACL implementation

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Translation layer protecting your domain  │
│              │ from external model corruption            │
├──────────────┼───────────────────────────────────────────┤
│ IMPLEMENTS   │ Facade + Adapter + Translator             │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Integrating with systems using different  │
│              │ domain vocabulary and model               │
├──────────────┼───────────────────────────────────────────┤
│ KEY RULE     │ Domain layer has zero imports from        │
│              │ external system packages                  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The customs officer: nothing enters      │
│              │ without being translated to your standards"│
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You're building an ACL to integrate with an ERP system that returns product data. The ERP has 200 fields per product. Your domain only needs 8 of them. How do you handle this in your translator: do you map all 200 fields (future-proofing), or only the 8 you need (YAGNI)? What are the implications of each choice if the ERP adds a field you later need?

**Q2.** Your system uses an ACL to integrate with a legacy warehouse system. The legacy system is being replaced over 2 years by a new WMS platform. Both systems will run in parallel during the migration. How does the ACL pattern help you manage this migration, and what changes are needed in your application code (domain layer) when the new WMS is fully deployed?
