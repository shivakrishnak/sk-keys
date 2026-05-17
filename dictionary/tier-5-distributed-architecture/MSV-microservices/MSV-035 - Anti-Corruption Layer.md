---
id: MSV-035
title: Anti-Corruption Layer
category: Microservices
tier: tier-5-distributed-architecture
folder: MSV-microservices
difficulty: ★★★
depends_on: MSV-031, MSV-032, MSV-034
used_by: MSV-085, MSV-074
related: MSV-031, MSV-032, MSV-034, MSV-085, MSV-074, MSV-036
tags:
  - microservices
  - pattern
  - deep-dive
  - ddd
status: complete
version: 4
layout: default
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 35
permalink: /microservices/anti-corruption-layer/
---

# MSV-035 - Anti-Corruption Layer

⚡ TL;DR - Anti-Corruption Layer (ACL) is a DDD Context
Map pattern: a translation layer between two Bounded
Contexts that prevents one context's model from leaking
into another. The ACL translates the external model
into your domain's model, acting as an adapter/facade.
In microservices: used when integrating legacy systems,
external APIs, or upstream services whose models are
poor fits for your domain. The ACL absorbs external
changes, protecting your domain from "corruption".

| #035 | Category: Microservices | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Domain-Driven Design (DDD), Bounded Context, Ubiquitous Language | |
| **Used by:** | Monolith to Microservices Migration, Adapter Pattern in Microservices | |
| **Related:** | Domain-Driven Design (DDD), Bounded Context, Ubiquitous Language, Monolith to Microservices Migration, Adapter Pattern in Microservices, Strangler Fig Pattern | |

---

### 🔥 The Problem This Solves

**THE CORRUPTION SCENARIO:**
Order Service integrates with a legacy ERP system from
2003. The ERP's concept of "item" has 47 fields and uses
codes like `ITEM_TYPE=P` (P = physical product). The
ERP uses numeric IDs (1234567) with specific format
rules. In-stock status is: `QTY_ON_HAND > QTY_RESERVED`
(calculation, not a field).

Without ACL: the Order Service domain starts using ERP
concepts. Classes named after ERP: `ErpItem`,
`ErpItemType`, `ErpInventoryCalculator`. All Order
Service developers must understand ERP's data model.
Bugs in ERP format handling leak into Order domain.
The ERP's design decisions (from 2003) now govern
your 2024 service.

With ACL: Order Service defines its own Product model
(`ProductId`, `ProductName`, `InStockStatus`). The ACL
translates ERP's response to Order Service's model.
ERP changes only require updating the ACL, not the
domain.

---

### 📘 Textbook Definition

**Anti-Corruption Layer (ACL)** is a DDD Context Map
pattern: an isolation layer between two Bounded Contexts
that translates models and protocols between them, preventing
the downstream context from being "corrupted" by the
upstream context's model. The ACL is placed in the
downstream context, owned by the downstream team. It
converts the upstream context's language, model, and
protocol into the downstream context's Ubiquitous Language
and domain model. The upstream is unaware of the ACL.
In microservices: ACL is typically implemented as an
Adapter, Facade, or Gateway class within a service.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
ACL is a translation layer that converts an external
system's messy model into your clean domain model,
so external complexity doesn't contaminate your code.

**One analogy:**
> A UN interpreter at an international conference.
World leaders speak their native languages; the interpreter
> translates in real time. The interpreter absorbs the
> complexity of the different languages. The world leaders
> communicate in their own language as if the other
> languages don't exist. The interpreter IS the ACL.
> If a new leader joins speaking a new language: update
> the interpreter (ACL), not the other leaders (your domain).

**One insight:**
The ACL is where the messy external world meets your
clean internal world. The messiness stays in the ACL.
Your domain remains clean. When the external API
changes: update the ACL. Your domain model is shielded
from external API churn. This is especially valuable
during legacy system migration: the ACL can mock the
legacy system for testing without the legacy system
being deployed.

---

### 🔩 First Principles Explanation

**WHERE ACL IS NEEDED:**

```
SCENARIO 1 - LEGACY SYSTEM INTEGRATION:
  Upstream: ERP system (2003, SOAP/XML, numeric IDs,
            cryptic field names, status codes like P/A/D)
  Downstream: order-service (2024, REST/JSON, UUID IDs,
              descriptive names, enum statuses)
  
  ACL responsibilities:
  - SOAP XML -> Java objects
  - Numeric ERP ID -> UUID ProductId
  - "ITEM_TYPE=P" -> ProductType.PHYSICAL
  - QTY_ON_HAND - QTY_RESERVED calculation -> InStockStatus.IN_STOCK
  - Error codes -> domain exceptions

SCENARIO 2 - EXTERNAL PARTNER API:
  Upstream: shipping carrier API (FedEx, UPS)
  Downstream: shipping-service
  
  ACL responsibilities:
  - Carrier-specific status codes -> ShipmentStatus enum
  - Carrier's address format -> your Address value object
  - Authentication (API key, OAuth) -> transparent
  - Rate limiting, retry -> handled inside ACL
  - Version changes in carrier API -> absorbed in ACL

SCENARIO 3 - POOR UPSTREAM MICROSERVICE:
  Upstream: payment-service with a poorly designed API
            (uses old naming, different model)
  Downstream: order-service
  
  ACL responsibilities:
  - Map payment-service's "payment_approval_code" to
    order-service's PaymentConfirmationId
  - Map payment-service's "amount_in_cents" to Money value object
  - Map payment-service's status codes to your domain statuses
```

**ACL vs CONFORMIST:**

```
CONFORMIST (no ACL):
  Downstream adopts upstream model as-is.
  Use when: upstream model is well-designed and
  compatible with your domain.
  Trade-off: simpler code, tight coupling to upstream.

ANTI-CORRUPTION LAYER:
  Downstream translates upstream model.
  Use when: upstream model is poor, external, or
  would require adopting non-domain concepts.
  Trade-off: more code (translation layer), but
  domain is protected from external changes.

DECISION RULE:
  Is the upstream model a good fit for your domain?
  Yes: Conformist (simplicity wins)
  No: ACL (protection wins)
  External system: ALWAYS use ACL
  Legacy system: ALWAYS use ACL
  Well-maintained internal API: usually Conformist
  Poorly designed internal API: ACL
```

---

### 🧪 Thought Experiment

**WHAT GETS CORRUPTED WITHOUT ACL:**

```
Legacy ERP has:
  getItemById(int itemId)  // returns ErpItemDto
  ErpItemDto {
    int ITEM_ID;
    String ITEM_TYPE;    // P=physical, V=virtual, S=service
    int QTY_ON_HAND;
    int QTY_RESERVED;
    String AVAIL_FLAG;   // Y/N
    BigDecimal UNIT_COST;
    String ITEM_STATUS;  // A=active, D=discontinued
  }

WITHOUT ACL:
  Order service code:
    ErpItemDto item = erpClient.getItemById(12345);
    if (item.ITEM_TYPE.equals("P")) {  // ERP concept!
      if (item.QTY_ON_HAND > item.QTY_RESERVED) {
        // ERP calculation
        cart.add(item.ITEM_ID, price);  // ERP numeric ID
      }
    }
  Corruption: ERP concepts (ITEM_TYPE=P, QTY calc) in
  Order domain. New developer must understand ERP to
  understand Order code.

WITH ACL:
  Order service code:
    Product product = productACL.findById(productId);
    if (product.isPhysical() && product.isInStock()) {
      cart.add(product.getId(), product.getUnitPrice());
    }
  Clean! ERP concepts are ONLY in the ACL.
  Changing to a new inventory system:
  update ACL only. Order domain unchanged.
```

---

### 🧠 Mental Model / Analogy

> The ACL is like a power adapter when travelling
> internationally. Your laptop (domain) expects a specific
> plug type and voltage. Foreign outlets (external systems)
> have different plug types and voltages. The adapter
> (ACL) converts the foreign interface to what your
> laptop needs. Your laptop doesn't know or care that
> it's in a different country. If you visit a third
> country: get a different adapter, laptop unchanged.
> The adapter absorbs the international variety so
> your laptop works everywhere without modification.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
ACL is a translator class. External system returns data
in its own format. ACL translates it into your system's
format. Your service only talks to the ACL, not directly
to the external system's format.

**Level 2 - How to use it (junior developer):**
In Spring Boot: create an interface in your domain:
`ProductPort.findById(ProductId id)`. Create an ACL
class: `ErpProductAdapter implements ProductPort`.
The adapter calls the ERP and translates the response.
Your service depends on `ProductPort`, not `ErpClient`.
In tests: mock `ProductPort`, not `ErpClient`.

**Level 3 - How it works (mid-level engineer):**
In hexagonal architecture (Ports and Adapters): the
ACL IS the adapter. The domain port (interface) is
defined by the domain. The adapter implements the port
and talks to the external system. This is standard
hexagonal architecture. The domain is independent of
the infrastructure (external systems). Tests: use
in-memory or stub adapters. Production: use the ACL
adapter. The ACL also handles: authentication, retry
logic, error mapping, and protocol translation.

**Level 4 - Why it was designed this way (senior/staff):**
ACL is critical during legacy migration. Strangler Fig
Pattern: gradually replace a legacy monolith with
microservices. Each new microservice integrates with
the legacy system via an ACL. When the legacy feature
is migrated: the ACL either: (a) is deleted (new
microservice serves the capability), or (b) is inverted
(legacy is now the downstream, ACL translates from new
microservice back to legacy format for remaining legacy
code). The ACL makes the migration incremental and
reversible.

**Level 5 - Mastery (distinguished engineer):**
ACL design for high-throughput: external API calls
through ACL can be a bottleneck. Two patterns:
(1) ACL with cache: cache external responses (avoid
redundant API calls for same external ID). Cache TTL
based on data volatility. (2) ACL with pre-fetching:
batch-fetch external data asynchronously, store in
local read model. ACL serves from local model, not
external call. Eventual consistency with the external
system, but high availability and no dependency on
external system uptime. Useful when external system
has poor SLA (legacy ERP: 99.5% uptime, 500ms latency).

---

### ⚙️ How It Works (Mechanism)

**HEXAGONAL ARCHITECTURE ACL IMPLEMENTATION:**

```java
// DOMAIN PORT: interface defined by the domain
// In domain layer (no infrastructure dependencies)
public interface ProductPort {
    Optional<Product> findById(ProductId productId);
    List<Product> findByIds(Set<ProductId> ids);
}

// DOMAIN MODEL (clean, no ERP concepts)
public record Product(
    ProductId id,
    String name,
    ProductType type,  // PHYSICAL, VIRTUAL, SERVICE
    Money unitPrice,
    boolean inStock
) {}

// ACL ADAPTER: infrastructure layer
// Implements domain port, depends on external client
@Component
@Primary
public class ErpProductAdapter implements ProductPort {

    private final ErpClient erpClient;  // SOAP/HTTP client

    @Override
    public Optional<Product> findById(ProductId productId) {
        try {
            // External call: ERP numeric ID format
            int erpId = Integer.parseInt(
                productId.getValue().replace("PROD-", ""));
            ErpItemDto erpItem = erpClient.getItem(erpId);

            // Translate ERP model -> domain model
            return Optional.of(toProduct(erpItem));
        } catch (ErpItemNotFoundException e) {
            return Optional.empty();
        } catch (ErpException e) {
            // Translate ERP exception -> domain exception
            throw new ProductLookupException(
                "Failed to lookup product: " + productId, e);
        }
    }

    private Product toProduct(ErpItemDto dto) {
        return new Product(
            new ProductId("PROD-" + dto.getItemId()),
            dto.getItemDescription(),
            translateType(dto.getItemType()),
            Money.of(dto.getUnitCost(), Currency.USD),
            // Calculate in-stock from ERP formula
            dto.getQtyOnHand() > dto.getQtyReserved()
        );
    }

    private ProductType translateType(String erpType) {
        return switch (erpType) {
            case "P" -> ProductType.PHYSICAL;
            case "V" -> ProductType.VIRTUAL;
            case "S" -> ProductType.SERVICE;
            default -> throw new UnknownProductTypeException(
                "Unknown ERP item type: " + erpType);
        };
    }
}

// DOMAIN SERVICE: depends on port, not adapter
@Service
public class CartService {
    private final ProductPort productPort;  // not ErpClient!

    public void addItem(CartId cartId, ProductId productId,
            int quantity) {
        Product product = productPort.findById(productId)
            .orElseThrow(() -> new ProductNotFoundException(
                productId));
        if (!product.inStock()) {
            throw new ProductOutOfStockException(productId);
        }
        // Clean domain code, no ERP concepts anywhere
    }
}
```

---

### 🔄 The Complete Picture - End-to-End Flow

**ACL IN MIGRATION (STRANGLER FIG + ACL):**

```
PHASE 1: New service talks to legacy via ACL
  New order-service -> [ACL] -> Legacy ERP
  ACL translates: ERP item model -> Product domain model
  Both systems operational

PHASE 2: New inventory-service replaces ERP inventory
  New order-service -> [ACL] -> Inventory Service (new)
  ACL updated: now calls inventory-service API instead of ERP
  Domain model unchanged (still uses Product)
  Legacy ERP: inventory module bypassed

PHASE 3: ACL fully evolved or removed
  If inventory-service API matches domain model well:
  ACL becomes thin (almost no translation needed)
  May be simplified to a direct client wrapper
  
  If significant mismatch remains:
  ACL stays as permanent adapter between contexts

KEY INSIGHT:
  At no point does domain code change due to
  infrastructure changes. The ACL absorbs ALL external
  changes (ERP -> new service, API version changes,
  authentication changes). Domain stability enabled
  by ACL.
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: no ACL vs with ACL**

```java
// BAD: no ACL - external model leaks into domain
@Service
public class OrderService {

    private final ShippingCarrierApiClient upsClient;

    public TrackingInfo getTracking(String orderId) {
        // UPS model leaks into Order domain:
        UPSTrackingResponse upsResponse =
            upsClient.track(orderId);
        // UPS-specific: "I" = in transit, "D" = delivered
        // (external knowledge required to understand this)
        if ("I".equals(upsResponse.getActivityCode())) {
            return new TrackingInfo(orderId, "IN_TRANSIT",
                upsResponse.getLastUpdateTime());
        }
        // If carrier changes: all of OrderService changes
    }
}
```

```java
// GOOD: ACL protects domain from carrier model
// Domain port:
public interface ShipmentPort {
    ShipmentStatus getStatus(ShipmentId shipmentId);
}

// ACL Adapter (UPS-specific knowledge stays here)
@Component
public class UPSShipmentAdapter implements ShipmentPort {
    private final UPSApiClient upsClient;

    @Override
    public ShipmentStatus getStatus(ShipmentId id) {
        UPSTrackingResponse r =
            upsClient.track(id.getValue());
        return switch (r.getActivityCode()) {
            case "I" -> ShipmentStatus.IN_TRANSIT;
            case "D" -> ShipmentStatus.DELIVERED;
            case "X" -> ShipmentStatus.EXCEPTION;
            default -> ShipmentStatus.UNKNOWN;
        };
    }
}

// Domain service: clean, no carrier concepts
@Service
public class OrderService {
    private final ShipmentPort shipmentPort;

    public ShipmentStatus getShipmentStatus(
            ShipmentId shipmentId) {
        return shipmentPort.getStatus(shipmentId);
        // Carrier can change (UPS -> FedEx): update adapter only
        // OrderService unchanged
    }
}
```

---

### ⚖️ Comparison Table

| Context Map Pattern | Coupling | Translation | When to Use |
|---|---|---|---|
| **Conformist** | High | None | Upstream model is good; simple integration |
| **Anti-Corruption Layer** | Low | Full | External system, legacy, or poor upstream model |
| **Shared Kernel** | Medium | None | Small shared value objects |
| **Customer-Supplier** | Medium | Partial | Internal services with planned coordination |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| ACL = extra code that adds no value | ACL adds translation code but removes domain complexity. Without ACL: domain code contains external concepts (ERP item types, carrier status codes). The total code volume is often similar; the ACL version has all external complexity in one predictable place. |
| Every external service needs a full ACL | For well-designed external services whose model fits your domain, a thin Adapter (mapping class) may suffice without a full translation layer. "ACL" scales from a single mapper class to a full facade+translator. Use the level of translation needed. |
| ACL solves data quality problems | ACL translates data format, not data quality. If the external system returns wrong data (incorrect prices, stale inventory), the ACL faithfully translates the wrong data. Data quality requires validation in the ACL and fallback strategies. |

---

### 🚨 Failure Modes & Diagnosis

**ACL becomes the bottleneck under load**

**Symptom:**
Order Service performance degrades at peak. ACL calls
to the ERP take 400ms average. Order creation latency
= 500ms (400ms is ERP call via ACL). At 500 orders/second:
ERP becomes the bottleneck. ACL queue fills up.

**Root Cause:**
ACL is synchronous: every order creation calls ERP
to look up product details. ERP's P99 latency is 800ms.
At scale, this doesn't work.

**Diagnostic:**
```bash
# Trace ACL call timing
# (with OpenTelemetry, ACL calls are separate spans)
jaeger-query traces \
  --service order-service \
  --operation ErpProductAdapter.findById
# Shows: 60% of order latency is ERP lookup

# Check ERP call frequency
curl http://localhost:8080/actuator/metrics/
  http.client.requests?tag=uri:/erp-service
# Count: > 0.9 * total order creation requests
# (every order = one ERP call)
```

**Fix:**
1. Cache in ACL: cache product lookups for 5 minutes
   (products change rarely; stale data acceptable)
   `@Cacheable(value="products", key="#productId")`
2. Pre-load: at service startup, load and cache
   all active products from ERP
3. Async pre-fetch: ACL maintains local read model
   (product cache DB), refreshed from ERP every hour.
   Order Service reads from local cache, not ERP directly.
4. Final solution: migrate product catalog to internal
   catalog-service (Strangler Fig), remove ERP dependency

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Domain-Driven Design (DDD)` - ACL is a DDD Context
  Map pattern
- `Bounded Context` - ACL sits at the boundary between
  two contexts
- `Ubiquitous Language` - ACL preserves your UL by
  translating external terms

**Applied In:**
- `Monolith to Microservices Migration` - ACL is used
  when new services integrate with legacy monolith
- `Adapter Pattern in Microservices` - ACL is implemented
  using the Adapter pattern

**Migration:**
- `Strangler Fig Pattern` - ACL enables incremental
  migration; the ACL absorbs the current state of
  the legacy integration

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ PURPOSE      │ Translate external model -> your domain  │
│              │ External complexity stays in the ACL    │
├──────────────┼───────────────────────────────────────────┤
│ WHEN         │ Always for external systems and legacy   │
│              │ Poor upstream domain models              │
├──────────────┼───────────────────────────────────────────┤
│ IMPL         │ Port (domain interface) + Adapter (ACL)  │
│              │ Hexagonal Architecture pattern           │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Adapter that shields your domain from    │
│              │  external model concepts"               │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Strangler Fig → Monolith to Microservices │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. ACL = a translation layer between two contexts.
   External model stays in the ACL; your domain model
   stays clean.
2. Use it whenever: integrating external/legacy systems,
   or when the upstream domain model doesn't fit yours.
3. Implement as: domain Port (interface) + ACL Adapter
   (implementation). Domain depends on Port, not on
   the external client directly.

**Interview one-liner:**
"Anti-Corruption Layer (ACL) is a DDD pattern that
translates an external system's model into your bounded
context's model, preventing the external model from
'corrupting' your domain. Implemented as a domain Port
(interface) + Adapter (ACL class that calls external
API and translates the response). Used whenever integrating
legacy systems, external APIs, or poorly designed upstream
services. The ACL absorbs all external changes: API
versions, carrier changes, ERP upgrades - only the ACL
changes, domain model is stable."

---

### 💡 The Surprising Truth

The ACL pattern is one of the most underused DDD tools
in microservices. Most teams that integrate external
systems do it the "easy" way: create a DTO matching the
external API and use it directly in the domain. This
works until the external API changes or until a second
consumer of the external API appears. The second consumer
also creates their own DTO matching the external API.
Now two services are coupled to the same external API.
When the API changes: update two services. With an ACL:
one external client, one domain port. Multiple services
depend on the domain port (through dependency injection
or module import). External API changes: update one ACL.
The ACL is the single integration point. This is the
hexagonal architecture dividend: one seam, managed
change, multiple beneficiaries.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **IDENTIFY** Given a service that calls an external
   API directly, identify which external model concepts
   have leaked into the domain and should be in an ACL.
2. **IMPLEMENT** Refactor a service to use hexagonal
   architecture: extract a domain Port interface and
   create an ACL Adapter that calls the external API.
3. **TEST** Write unit tests for the domain service using
   a mock Port (no external dependency), and integration
   tests for the ACL Adapter with a WireMock stub of
   the external API.
4. **CACHE** Add caching to the ACL for a slow external
   API call, with appropriate TTL based on data volatility.
5. **MIGRATE** Design a migration using Strangler Fig
   + ACL: initial ACL calls legacy system; incremental
   migration moves calls to new service; ACL is the
   seam that makes migration reversible.

---

### 🧠 Think About This Before We Continue

**Q1.** You are integrating with a third-party payment
gateway (Stripe). Stripe's API is well-designed. Does
your payment-service domain need a full ACL, or is a
thin adapter sufficient? What factors influence this
decision? (Consider: what if you switch from Stripe
to Adyen in 2 years?)

**Q2.** Your service integrates with three external
shipping carriers (UPS, FedEx, DHL). Each has a different
API, different authentication, different status codes.
Design the ACL architecture: one ACL per carrier, or
one unified ShipmentPort with three adapters? What is
the domain model for shipment status?

**Q3.** An ACL is adding 200ms to every API call
(translation overhead + external call). The business
requires < 100ms latency. What architectural changes
to the ACL can reduce this latency without removing
the ACL pattern? (Consider caching, async pre-loading,
local read model, event-driven synchronisation.)