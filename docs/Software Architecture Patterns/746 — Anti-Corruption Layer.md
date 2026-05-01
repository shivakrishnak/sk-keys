---
layout: default
title: "Anti-Corruption Layer"
parent: "Software Architecture Patterns"
nav_order: 746
permalink: /software-architecture/anti-corruption-layer/
number: "746"
category: Software Architecture Patterns
difficulty: ★★★
depends_on: "Bounded Context, Domain Model, Hexagonal Architecture"
used_by: "DDD integration, Legacy system migration, Microservices"
tags: #advanced, #architecture, #ddd, #integration, #patterns
---

# 746 — Anti-Corruption Layer

`#advanced` `#architecture` `#ddd` `#integration` `#patterns`

⚡ TL;DR — An **Anti-Corruption Layer (ACL)** is a translation layer that isolates your domain model from external systems or other bounded contexts — preventing foreign concepts, terminology, and assumptions from "corrupting" your domain model's integrity.

| #746            | Category: Software Architecture Patterns                | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------ | :-------------- |
| **Depends on:** | Bounded Context, Domain Model, Hexagonal Architecture   |                 |
| **Used by:**    | DDD integration, Legacy system migration, Microservices |                 |

---

### 📘 Textbook Definition

The **Anti-Corruption Layer** (Eric Evans, "Domain-Driven Design") is a defensive layer that translates between your domain model and an external system (legacy system, third-party API, or a different bounded context). When integrating with an external system, the ACL: (1) **Translates concepts**: converts the external system's model into your domain's model without exposing external concepts inside your domain. (2) **Isolates**: changes to the external system's API only affect the ACL, not your domain. (3) **Preserves domain integrity**: your domain speaks its own Ubiquitous Language, not the external system's language. (4) **Provides a seam**: makes the external system replaceable — swap the ACL implementation to switch providers. The ACL is needed when two bounded contexts have significantly different models, when one context is legacy or poorly designed, or when you're integrating with a third-party API that imposes its own concepts on your domain.

---

### 🟢 Simple Definition (Easy)

Buying parts from a foreign supplier who uses a different measurement system. Your factory uses metric (meters, kilograms). The foreign supplier uses imperial (inches, pounds). The Anti-Corruption Layer: your receiving department — it converts inches to centimeters, pounds to kilograms, before anything reaches the factory floor. The factory (your domain) only ever works in metric. The supplier can change their units tomorrow; your factory doesn't care. The receiving department (ACL) handles the translation.

---

### 🔵 Simple Definition (Elaborated)

Your Order Management System (OMS) speaks your Ubiquitous Language: `Order`, `Customer`, `Product`, `Money`. A legacy ERP system you must integrate with uses: `TRANSACTION_RECORD`, `CLIENT_CODE`, `SKU_ITEM`, `MONETARY_VALUE_IN_CENTS_STRING`. Without ACL: ERP concepts leak into your domain — `Order` starts having `CLIENT_CODE` field, `Product` has `SKU_ITEM`. Your domain becomes polluted with ERP terminology. With ACL: `ErpIntegrationService` translates ERP `TRANSACTION_RECORD` → your `Order`. ERP concepts never enter your domain. ERP replaced next year: only the ACL changes.

---

### 🔩 First Principles Explanation

**ACL structure, implementation, and when to use it:**

```
ANTI-CORRUPTION LAYER STRUCTURE:

  YOUR DOMAIN:
    Order, Customer, Product, Money, OrderStatus
    (Speaks your Ubiquitous Language)

  ANTI-CORRUPTION LAYER:
    ┌────────────────────────────────────────────────────┐
    │  Domain interface:   ExternalOrderRepository       │
    │                      (your domain's concept)       │
    │                                                     │
    │  Translation logic:  ExternalOrderMapper           │
    │                      (converts between models)     │
    │                                                     │
    │  Client:             LegacyErpClient               │
    │                      (speaks ERP language)         │
    └────────────────────────────────────────────────────┘

  EXTERNAL SYSTEM:
    TRANSACTION_RECORD, CLIENT_CODE, SKU_ITEM, STATUS_CODE
    (Speaks ERP language)

IMPLEMENTATION:

  // 1. Your domain defines the interface it needs (its own language):
  interface ExternalOrderRepository {
      Order findByExternalId(ExternalOrderId id);  // Domain concepts
      void syncOrder(Order order);
  }

  // 2. ACL implementation: translates to/from external system's language:
  class ErpOrderAdapter implements ExternalOrderRepository {
      private final ErpClient erpClient;     // Speaks ERP language
      private final OrderMapper mapper;      // Translates between languages

      @Override
      public Order findByExternalId(ExternalOrderId id) {
          // External system: its own data format
          ErpTransactionRecord erpRecord = erpClient.getTransaction(id.value());

          // ACL: translate to your domain model
          return mapper.toOrder(erpRecord);
      }

      @Override
      public void syncOrder(Order order) {
          // ACL: translate from your domain to external format
          ErpTransactionRecord record = mapper.toErpRecord(order);
          erpClient.updateTransaction(record);
      }
  }

  // 3. Mapper: the actual translation logic:
  class OrderMapper {
      Order toOrder(ErpTransactionRecord record) {
          return new Order(
              OrderId.of(record.TRANSACTION_ID),
              CustomerId.of(record.CLIENT_CODE),            // CLIENT_CODE → CustomerId
              translateStatus(record.STATUS_CODE),          // STATUS_CODE → OrderStatus
              Money.ofCents(Long.parseLong(record.AMOUNT_CENTS_STR), USD), // "19999" → $199.99
              translateItems(record.LINE_ITEMS)
          );
      }

      private OrderStatus translateStatus(String erpCode) {
          return switch (erpCode) {
              case "01" -> OrderStatus.PENDING;
              case "02" -> OrderStatus.CONFIRMED;
              case "03" -> OrderStatus.SHIPPED;
              case "99" -> OrderStatus.CANCELLED;
              default -> throw new UnknownErpStatusException(erpCode);
          };
      }
  }

  // 4. Domain uses only its own language:
  class OrderSyncService {
      void syncFromErp(ExternalOrderId externalId) {
          Order order = externalOrderRepo.findByExternalId(externalId);
          // 'order' is a clean domain Order — no ERP concepts here
          order.validate();
          orderRepo.save(order);
      }
  }

WHEN ACL IS NEEDED:

  ✓ Integrating with a legacy system with a different domain model.
  ✓ Third-party API uses its own terminology (Stripe, Salesforce, SAP).
  ✓ Another bounded context in your company uses different concepts.
  ✓ External system's model is poorly designed — don't want it in your clean domain.
  ✓ You plan to replace the external system eventually.

WHEN ACL IS NOT NEEDED (simpler integrations):

  ✗ Shared Kernel: two bounded contexts share the same model — no translation needed.
  ✗ Conformist: you intentionally adopt the external system's model (Stripe → use Stripe's model).
  ✗ Open Host Service: external system provides a well-designed, stable API that already
    matches your domain needs — adopt their model without translation.

  DDD CONTEXT MAP RELATIONSHIPS:

  CONFORMIST:  Your model conforms to the external model.
               "We use Stripe's API types directly in our code."

  ACL:         You protect your model from the external model.
               "We translate Stripe's types to our domain types."

  OPEN HOST SERVICE: External publishes a well-designed API; you use it.
               "AWS SDK: we use their well-designed API, no ACL needed."

ACL IN MICROSERVICES:

  Each service: has its own bounded context. ACL needed when:

  Order Service → receives event from Inventory Service:
    Inventory event format: { "inventory_item_id": "...", "qty_available": 5 }
    Order Service domain:   InventoryStatus(productId, quantity, isInStock)

    Without ACL: Order Service model has "inventory_item_id" string field. External concept leaks.
    With ACL:   InventoryEventTranslator.translate(inventoryEvent) → InventoryStatus domain object.

  Translation happens at the boundary. Domain stays clean.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Anti-Corruption Layer:

- External system's field names appear in your domain: `clientCode`, `transactionRecord`, `statusCode01`
- External system changes its API: ripples through your entire domain
- Domain experts can't read your code — it uses the external system's language, not yours

WITH Anti-Corruption Layer:
→ Domain stays pure: `Order`, `Customer`, `Money` — your own language throughout
→ External system changes API: only the ACL adapter changes
→ Replace the external system: replace the ACL; domain code unchanged

---

### 🧠 Mental Model / Analogy

> A customs border checkpoint. Goods from foreign countries arrive in foreign packaging, with foreign labels, using foreign measurement standards. The customs border: converts everything to domestic standards before it enters the domestic market. Foreign goods never reach the domestic market in their original foreign format. Your domestic economy (domain model) only works with domestically-standardized products. The customs checkpoint (ACL) handles all translation.

"Customs border" = Anti-Corruption Layer
"Foreign packaging and labels" = external system's data model and terminology
"Converts to domestic standards" = translates external model to domain model
"Domestic economy only sees domestic format" = domain never sees external concepts

---

### ⚙️ How It Works (Mechanism)

```
ACL REQUEST FLOW:

  Domain Service: "Find order by external ID"
      │
      ▼ (domain interface — domain language)
  ExternalOrderRepository.findByExternalId(externalId)
      │
      ▼ (ACL: ErpOrderAdapter translates)
  ErpClient.getTransaction(id.value())     ← ERP protocol/format
      │ ErpTransactionRecord
      ▼
  OrderMapper.toOrder(record)              ← Translate to domain model
      │ Order (domain object)
      ▼
  Returns to Domain Service               ← Clean domain object. No ERP concepts.
```

---

### 🔄 How It Connects (Mini-Map)

```
External System / Legacy System / Other Bounded Context
(has its own model, concepts, language)
        │
        ▼ (protected by)
Anti-Corruption Layer ◄──── (you are here)
(translates external concepts → domain concepts; isolates domain)
        │
        ▼
Your Domain Model
(pure domain language; unaware of external system's model)
        │
        ├── Bounded Context: ACL sits at the boundary between contexts
        ├── Hexagonal Architecture: ACL is an outbound adapter (driving-side port)
        ├── Repository Pattern: ACL often implements a domain repository interface
        └── Domain Model: what ACL protects from external concept pollution
```

---

### 💻 Code Example

```java
// Domain interface (your language):
public interface PaymentGatewayPort {
    PaymentResult charge(PaymentRequest request); // Domain types
    RefundResult refund(RefundRequest request);
}

// ACL: translates between domain and Stripe's API:
@Component
class StripePaymentAdapter implements PaymentGatewayPort {
    private final Stripe stripeClient;

    @Override
    public PaymentResult charge(PaymentRequest request) {
        // Translate domain → Stripe format:
        PaymentIntentCreateParams params = PaymentIntentCreateParams.builder()
            .setAmount(request.amount().inCents())      // Money → long cents
            .setCurrency(request.amount().currency().getCurrencyCode().toLowerCase())
            .setPaymentMethod(request.paymentMethodToken().value()) // Token → String
            .setConfirm(true)
            .build();

        try {
            PaymentIntent intent = PaymentIntent.create(params, stripeClient.options());
            // Translate Stripe → domain:
            return PaymentResult.success(
                PaymentReference.of(intent.getId()),
                request.amount()
            );
        } catch (CardException e) {
            // Translate Stripe error → domain failure:
            return PaymentResult.failure(
                PaymentFailureCode.fromStripe(e.getCode()),
                e.getMessage()
            );
        }
    }
}

// Domain uses only domain types:
class CheckoutService {
    PaymentResult checkout(Order order, PaymentMethodToken token) {
        PaymentRequest req = new PaymentRequest(order.total(), token);
        return paymentGateway.charge(req); // Clean domain types in and out.
        // No Stripe types in this class.
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                            | Reality                                                                                                                                                                                                                                                                                                                                                                      |
| -------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ACL is only for legacy systems                           | ACL applies anywhere two bounded contexts have different models, including modern third-party APIs (Stripe, Salesforce, AWS), other teams' microservices, or other bounded contexts within the same organization. Any time an external model would "corrupt" your domain language if used directly: use an ACL                                                               |
| ACL is the same as Hexagonal Architecture's adapters     | Related but not identical. Hexagonal Architecture (Ports & Adapters): any external interaction uses an adapter. ACL: specifically when translation is needed to protect your domain model from external concepts. All ACLs are adapters in the hexagonal sense; not all adapters are ACLs (some adapters to well-aligned external systems need minimal translation)          |
| ACL adds too much overhead — just use the external model | For simple integrations with well-designed external APIs that match your domain: yes, overhead not worth it. But for complex external systems that would pollute your domain (legacy ERP, poorly designed partner API): the long-term cost of NOT having an ACL is technical debt — your domain gradually adopts external language, making it harder to maintain and replace |

---

### 🔥 Pitfalls in Production

**External model leaks through incomplete ACL:**

```java
// BAD: ACL exposes external model types in domain method signature:
class OrderService {
    Order createFromErp(ErpTransactionRecord erpRecord) { // ErpTransactionRecord in domain!
        // "erpRecord" leaks ERP concept into order service.
        // OrderService now depends on the ERP library.
        ...
    }
}

// BAD: Domain event contains external system ID as string:
record OrderCreatedEvent(String orderId, String erpTransactionId, ...) {}
// "erpTransactionId" — ERP concept in domain event. Other handlers must know about ERP.

// FIX: ACL translates completely before entering domain:
class ErpOrderAdapter implements ExternalOrderPort {
    public Order findByTransactionId(String erpId) {
        ErpTransactionRecord rec = erpClient.get(erpId); // External call
        return mapper.toOrder(rec);                      // Fully translated
        // Returns domain Order — no ErpTransactionRecord beyond this boundary.
    }
}

// Domain event: domain language only:
record OrderCreatedEvent(OrderId orderId, CustomerId customerId, ...) {}
// No ERP ID here. If ERP ID needed: store in separate correlation field in ACL layer.
```

---

### 🔗 Related Keywords

- `Bounded Context` — ACL sits at the boundary between two different bounded contexts
- `Hexagonal Architecture` — ACL is an outbound adapter in Hexagonal/Ports-and-Adapters
- `Domain Model` — what ACL protects: keeps domain model pure from external concepts
- `Strangler Fig Pattern` — ACL often used during migration: wraps legacy system while strangling it
- `Context Map` — DDD tool showing which relationship type connects bounded contexts (ACL, Conformist, etc.)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Translation layer at domain boundary:     │
│              │ external system's model never enters      │
│              │ your domain. Translate at the edge.       │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ External system has different model;      │
│              │ legacy system with poor naming;           │
│              │ 3rd-party API with foreign concepts;      │
│              │ planning to replace external system       │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ External model matches your domain well   │
│              │ (Open Host Service); Conformist approach  │
│              │ is intentional and low risk               │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Customs checkpoint: foreign goods enter  │
│              │  in foreign format; ACL converts them     │
│              │  before your domain ever sees them."      │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Bounded Context → Context Map →           │
│              │ Hexagonal Architecture → Strangler Fig    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your service receives events from a partner company's Kafka topic. The partner uses `customer_external_id` (their internal customer identifier) which you must map to your own `CustomerId`. The mapping is stored in a lookup table. Sometimes the lookup returns null — the partner's customer is unknown in your system. How does the ACL handle this: fail fast (throw exception), create a placeholder customer, or silently skip the event? What are the trade-offs? How does the ACL boundary affect your decision (is this the ACL's responsibility or the domain's)?

**Q2.** Your ACL translates Stripe's `PaymentIntent` model to your `PaymentResult` domain object. Stripe adds a new field: `risk_score` (fraud risk 0-100). Your fraud detection bounded context could use this. Should you: (A) add `riskScore` to your `PaymentResult` domain object, (B) have the ACL publish a separate `StripeRiskAssessmentReceived` domain event, or (C) have the fraud detection bounded context have its own Stripe ACL that handles risk scores independently? Which option best preserves bounded context isolation?
