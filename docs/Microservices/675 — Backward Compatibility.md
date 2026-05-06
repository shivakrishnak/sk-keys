---
layout: default
title: "Backward Compatibility"
parent: "Microservices"
nav_order: 675
permalink: /microservices/backward-compatibility/
number: "0675"
category: Microservices
difficulty: ★★★
depends_on: Service Contract, Versioning Strategy, Zero-Downtime Deployment
used_by: Zero-Downtime Deployment, Versioning Strategy, Consumer-Driven Contract Testing
related: Versioning Strategy, Service Contract, Expand-Contract Pattern
tags:
  - microservices
  - api-design
  - compatibility
  - design
  - deep-dive
---

# 675 — Backward Compatibility

⚡ TL;DR — Backward compatibility means a new version of a service or schema can still be used correctly by consumers built against an older version, without requiring those consumers to change.

| #675            | Category: Microservices                                                         | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------------------------------ | :-------------- |
| **Depends on:** | Service Contract, Versioning Strategy, Zero-Downtime Deployment                 |                 |
| **Used by:**    | Zero-Downtime Deployment, Versioning Strategy, Consumer-Driven Contract Testing |                 |
| **Related:**    | Versioning Strategy, Service Contract, Expand-Contract Pattern                  |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Order Service calls Payment Service v1.3. Payment Service team releases v1.4 and renames `amount` to `totalAmount`. Order Service (still calling with `amount`) now sends requests the new Payment Service doesn't understand. Payment Service returns 422 (Unprocessable Entity). Every payment fails until Order Service is updated and deployed. Two services that should be independently deployable are now tightly coupled through implicit interface dependencies.

**THE BREAKING POINT:**
Microservices are supposed to be independently deployable. If every API change requires all consumers to be updated and deployed simultaneously, you don't have microservices — you have a distributed monolith with extra network hops.

**THE INVENTION MOMENT:**
Backward compatibility is the discipline of making changes to APIs and data schemas in such a way that old consumers continue to work without modification. It's the enabling condition for independent deployability.

---

### 📘 Textbook Definition

**Backward compatibility** (also: backwards compatibility) means that a newer version of a system (API, schema, protocol, binary) can be used by a client designed for an older version, without requiring any changes to that client. In microservices, backward compatibility is required at multiple levels: (1) **API level** — HTTP/gRPC interface changes that don't require consumers to update; (2) **Schema level** — database and message schema changes that don't break existing readers/writers; (3) **Binary level** — serialisation format changes (Protobuf, Avro, JSON Schema) that can be read by older deserializers. The counterpart is **forward compatibility**: an older consumer can read data written by a newer producer.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
New version works with old callers — no forced updates required.

**One analogy:**

> USB backward compatibility. USB-C devices work with USB-A hubs (with an adapter). USB 3.0 is backward-compatible with USB 2.0 ports. When you buy a new laptop with USB-C, your old USB peripherals still work. The hardware designers preserved backward compatibility so you don't have to throw away all your devices when you upgrade the laptop.

**One insight:**
Backward compatibility is the technical foundation of independent deployability. If your API changes are always backward-compatible, you can deploy Service A without requiring Service B to deploy simultaneously. This is what makes microservices architecturally sound.

---

### 🔩 First Principles Explanation

**WHAT IS A BREAKING CHANGE? (API level)**

| Change                         | Breaking? | Why                                               |
| ------------------------------ | --------- | ------------------------------------------------- |
| Add optional field to request  | No        | Old consumers don't send it; service uses default |
| Add field to response          | No        | Old consumers ignore unknown fields               |
| Remove required request field  | No\*      | Old consumers sending it — it's just ignored      |
| Remove response field          | **YES**   | Old consumers expecting it — NPE or error         |
| Rename request field           | **YES**   | Old consumers send old name — field missing       |
| Change field type (string→int) | **YES**   | Old consumers send string — parse error           |
| Add new required request field | **YES**   | Old consumers don't send it — validation error    |
| Change HTTP status codes       | **YES**   | Old consumers handle specific codes               |
| Change error response shape    | **YES**   | Old consumers parse specific error format         |

\*Removing a required field makes it effectively optional — usually safe if consumers were sending it.

**WHAT IS BACKWARD-COMPATIBLE? (Schema level)**

```
Protobuf / Avro rules:
  ✅ Add new optional field (old readers ignore unknown fields)
  ✅ Remove field (old readers have default for missing fields)
  ❌ Change field type (breaks serialisation)
  ❌ Rename field (Protobuf uses field numbers; rename of tag ID breaks)
  ❌ Change field from optional to required (old producers don't send it)

JSON Schema rules:
  ✅ Add new properties to an object (if using additionalProperties: true or ignore)
  ✅ Make a required field optional
  ❌ Remove properties consumers depend on
  ❌ Change property types
  ❌ Make optional field required (old senders may omit it)

Database column rules:
  ✅ Add column with default
  ✅ Add nullable column
  ❌ Remove column
  ❌ Rename column
  ❌ Change column type (may be safe if implicit cast works)
  ❌ Add NOT NULL constraint to existing column (breaks old inserts)
```

**THE ROBUSTNESS PRINCIPLE (Postel's Law):**

> "Be conservative in what you send, be liberal in what you accept."

For backward compatibility:

- Producer (provider): only add fields; never remove or rename existing fields
- Consumer: ignore unknown fields in responses; use defaults for missing optional fields

**THE TRADE-OFFS:**
**Gain:** Independent deployability; no coordinated multi-service deployments; consumers don't need to upgrade immediately; zero-downtime rolling deployments.
**Cost:** API and schema accumulate legacy fields (tech debt); old code paths must be maintained until all consumers migrate; some changes that would simplify the API can't be made without a major version; testing burden (must test old and new consumers).

---

### 🧪 Thought Experiment

**SETUP:**
You have a Kafka message: `{"orderId": "123", "amount": 49.99}`. 5 consumers subscribe to this topic. You want to add a `currency` field.

**BREAKING CHANGE (naive):**
New producer sends: `{"orderId": "123", "totalAmount": 49.99, "currency": "USD"}`.
Old consumers: reading `amount` → null. Calculation fails.

**BACKWARD-COMPATIBLE CHANGE:**
New producer sends: `{"orderId": "123", "amount": 49.99, "totalAmount": 49.99, "currency": "USD"}`.
Old consumers: reading `amount` → 49.99 ✅. New consumers: reading `totalAmount` ✅.
After all consumers are updated: stop sending `amount`.

**THE LESSON:**
In event streaming, backward compatibility is even more important because: (a) events are stored permanently (event sourcing); (b) consumers may read old events at any time; (c) coordinating simultaneous consumer updates across 5 teams is impractical. The solution: dual-write the old and new fields during the migration period.

---

### 🧠 Mental Model / Analogy

> Backward compatibility is like a car that can run on both old and new fuel formulations. The car manufacturer introduces a new, cleaner fuel (new API field). But they don't simultaneously remove all old fuel stations (old API field). For a transition period, the car runs on both. When all fuel stations have upgraded, old fuel formulation is phased out. No car was stranded during the transition because it couldn't find the right fuel.

- "Old fuel formulation" → old API field
- "New fuel formulation" → new API field
- "Car runs on both" → service handles both field names
- "Phase out old fuel" → remove old field after consumers migrate
- "Stranded car" → consumer receiving breaking change

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
When you update an app or API, people who haven't updated yet can still use it without errors. Like how a new Word document format can still be opened by an older version of Word — maybe with limitations, but not crashing.

**Level 2 — Practical rules for API changes (junior developer):**
Rule of thumb: you can only ADD to a contract, never REMOVE or CHANGE. Adding new endpoints, new optional request fields, new response fields — all backward-compatible. Removing anything, renaming anything, making optional fields required — all breaking. When you must make a breaking change: bump major version (`/v2/`); run both `/v1/` and `/v2/` simultaneously; sunset `/v1/` after all consumers migrate.

**Level 3 — Schema evolution patterns (mid-level engineer):**
For Avro/Protobuf schemas: use schema registry with compatibility checks (`BACKWARD`, `FORWARD`, `FULL`). For database: use expand-contract migration pattern. For JSON APIs: use `@JsonIgnoreProperties(ignoreUnknown = true)` (Jackson) to tolerate unknown response fields from newer providers; use `@JsonInclude(NON_NULL)` to tolerate missing optional fields from older providers.

**Level 4 — Backward compatibility as a culture (senior/staff):**
Truly backward-compatible systems require it as an engineering culture, not just a technical checklist. This means: API design reviews that pre-approve field names and types before implementation (renaming later is expensive); automated breaking change detection in CI (openapi-diff, buf breaking for Protobuf, Confluent Schema Registry); explicit compatibility SLAs in service contracts; deprecation notices in API responses (`Deprecation` header, `sunset` field). The most mature organisations treat backward compatibility violations as P1 defects — not "things to coordinate between teams".

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────────────────┐
│ Backward Compatibility at Multiple Layers               │
└─────────────────────────────────────────────────────────┘

Layer 1: HTTP API (REST)
  Provider v1 response: {paymentId, status}
  Provider v2 response: {paymentId, status, processingFee}
  Old consumer (v1): reads paymentId, status → OK (ignores processingFee)
  New consumer (v2): reads paymentId, status, processingFee → OK

Layer 2: Kafka Messages
  Old message: {orderId, amount}
  New message: {orderId, amount, currency}
  Old consumer: reads orderId, amount → OK (ignores currency)
  New consumer: reads orderId, amount, currency → OK

Layer 3: Database Schema
  Old schema: orders(id, total, status)
  New schema: orders(id, total, status, discount_code DEFAULT NULL)
  Old writer: INSERT (id, total, status) → OK (discount_code = NULL)
  New writer: INSERT (id, total, status, discount_code) → OK
  Old reader: SELECT id, total, status → OK (ignores discount_code)

Layer 4: Protobuf
  message Order { string orderId = 1; double amount = 2; }
  NEW:
  message Order { string orderId = 1; double amount = 2;
                  optional string currency = 3; }
  Old binary (no currency field): old reader → OK (field 3 ignored)
  New binary (has currency field): old reader → OK (field 3 unknown, ignored)
```

---

### 💻 Code Example

**Jackson: tolerate unknown fields (backward-compatible consumer):**

```java
@JsonIgnoreProperties(ignoreUnknown = true)  // ignore new fields from newer provider
public class PaymentResponse {
    private String paymentId;
    private String status;
    // processingFee not here — that's fine, will be ignored

    // getters/setters...
}
```

**Jackson: backward-compatible producer (don't serialize null optional fields):**

```java
@JsonInclude(JsonInclude.Include.NON_NULL)  // don't send null fields to old consumers
public class PaymentRequest {
    private String amount;
    private String currency;      // new field — null if not set
    private String discountCode;  // new field — null if not set
}
```

**OpenAPI: mark deprecated field (sunset notice):**

```yaml
components:
  schemas:
    PaymentResponse:
      properties:
        paymentId:
          type: string
        amount:
          type: number
          deprecated: true # ← mark as deprecated
          description: "Deprecated. Use totalAmount instead. Sunset: 2025-12-01"
        totalAmount:
          type: number
          description: "Replaces amount. Available from v1.4+"
```

**Avro schema: backward-compatible field addition:**

```json
{
  "type": "record",
  "name": "OrderEvent",
  "fields": [
    { "name": "orderId", "type": "string" },
    { "name": "amount", "type": "double" },
    { "name": "currency", "type": ["null", "string"], "default": null }
  ]
}
// 'currency' is nullable with null default → backward-compatible:
// old producers don't send it (null default); old consumers ignore it
```

---

### ⚖️ Comparison Table

| Change Type        | API         | DB Schema                 | Protobuf              | Kafka Message             |
| ------------------ | ----------- | ------------------------- | --------------------- | ------------------------- |
| Add optional field | ✅ Safe     | ✅ (nullable, default)    | ✅ (optional field)   | ✅ (default null)         |
| Add required field | ❌ Breaking | ❌ (NOT NULL, no default) | ❌ (required)         | ❌                        |
| Remove field       | ❌ Breaking | ❌ (if consumers read it) | ✅\* (old readers ok) | ❌ (if consumers read it) |
| Rename field       | ❌ Breaking | ❌                        | ❌                    | ❌                        |
| Change type        | ❌ Breaking | ❌ (usually)              | ❌                    | ❌                        |
| Relax validation   | ✅ Safe     | ✅                        | ✅                    | ✅                        |
| Tighten validation | ❌ Breaking | ❌                        | ❌                    | ❌                        |

\*Protobuf field removal is safe for binary compatibility; semantic compatibility depends on consumers.

---

### ⚠️ Common Misconceptions

| Misconception                                                   | Reality                                                                                                            |
| --------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| Optional fields are always backward-compatible to add           | Adding a new optional field to a REQUEST is safe; adding to RESPONSE is safe only if consumers use `ignoreUnknown` |
| Backward compatibility only matters for external APIs           | Internal microservice APIs have the same requirements; internal breaking changes cause internal outages            |
| We can break the contract and just update all consumers at once | This requires coordinated deployment of multiple services — the antithesis of independent deployability            |
| Deprecation warnings are sufficient notice                      | Deprecation needs a clear sunset date + active communication; warnings alone don't drive migration                 |

---

### 🚨 Failure Modes & Diagnosis

**Silent Null — Field Renamed, Old Consumer Reads Null**

**Symptom:** Payment amounts are 0 after payment service deployment; no errors logged.

**Root Cause:** Payment Service renamed `amount` to `totalAmount`; Order Service reads `amount` → null → defaults to 0.

**Prevention:**

```bash
# In CI: openapi-diff to detect field renames
openapi-diff previous-api.yaml current-api.yaml --fail-on-incompatible
```

**Fix:** Keep both `amount` and `totalAmount` fields; deprecate `amount`; remove only after all consumers migrated.

---

### 🔗 Related Keywords

**Prerequisites:** `Service Contract`, `Versioning Strategy`, `Zero-Downtime Deployment`

**Builds On This:** `Zero-Downtime Deployment`, `Versioning Strategy`, `Consumer-Driven Contract Testing`

**Related Patterns:** `Versioning Strategy`, `Expand-Contract Pattern`, `Service Contract`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ New version works with old callers —      │
│              │ no consumer changes required              │
├──────────────┼───────────────────────────────────────────┤
│ SAFE CHANGES │ Add optional fields; relax validation     │
├──────────────┼───────────────────────────────────────────┤
│ BREAKING     │ Remove/rename fields; add required fields;│
│              │ change types; tighten validation          │
├──────────────┼───────────────────────────────────────────┤
│ POSTEL'S LAW │ Conservative in send; liberal in accept   │
├──────────────┼───────────────────────────────────────────┤
│ CI ENFORCE   │ openapi-diff, buf breaking, schema registry│
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Add freely; remove only after migration" │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A consumer reads a JSON response: `{"orderId": "123", "amount": 49.99, "status": "COMPLETED"}`. The provider wants to change `status` from a string (`"COMPLETED"`) to an integer enum (`3`). Is this a breaking change? What if the provider adds a new status value `"PARTIALLY_REFUNDED"` (string, new value)? What if the provider removes the `"PENDING"` status value?

**Q2.** You maintain a Kafka message schema for `OrderPlaced` events. The schema currently has `amount` (double). You need to support multi-currency: `amount` becomes insufficient (needs a `currency` field too). You can't break the 8 existing consumers who read `amount`. Design the full migration: what you send during transition, what consumers must do to be compatible, when you can remove the old field, and what schema format you'd use to enforce this.
