---
layout: default
title: "Anti-Corruption Layer"
parent: "Microservices"
nav_order: 13
permalink: /microservices/anti-corruption-layer/
number: "MSV-013"
category: Microservices
difficulty: ★★★
depends_on: Bounded Context, Domain-Driven Design, Service Decomposition
used_by: Strangler Fig Pattern, Service Decomposition, Modular Monolith
related: Strangler Fig Pattern, Bounded Context, Adapter Pattern
tags:
  - microservices
  - architecture
  - pattern
  - deep-dive
  - distributed
---

# MSV-013 — Anti-Corruption Layer

⚡ TL;DR — An Anti-Corruption Layer is a translation boundary that shields your clean domain model from pollution by a poorly designed or legacy external system's model.

| #633 | Category: Microservices | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Bounded Context, Domain-Driven Design, Service Decomposition | |
| **Used by:** | Strangler Fig Pattern, Service Decomposition, Modular Monolith | |
| **Related:** | Strangler Fig Pattern, Bounded Context, Adapter Pattern | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A new microservice integrates with a 20-year-old ERP system. The ERP uses cryptic field names: `CUST_TYP_CD`, `ACCNT_BAL_AMT_01`, `SLS_REP_NM`. Your new service imports the ERP's Java client library, and to avoid rewriting the integration, developers use the ERP's naming conventions directly in the domain model. Over six months, your "clean" new service's codebase fills with `custTypCd` variables, `accntBalAmt01` fields, and logic that only makes sense in the ERP's context. The new service has become as hard to maintain as the legacy system it was meant to replace.

**THE BREAKING POINT:**
External system concepts have leaked into the new domain model. Renaming the ERP's fields requires changing core domain classes. New developers cannot understand the code without knowing the ERP internals. When the ERP is eventually replaced, the migration touches hundreds of files.

**THE INVENTION MOMENT:**
This is exactly why the Anti-Corruption Layer (ACL) pattern was created — to install a translation boundary between systems so each side can evolve in its own model, with an explicit, testable conversion layer in between.

---

### 📘 Textbook Definition

An **Anti-Corruption Layer (ACL)** is a boundary layer placed between two bounded contexts (or between a bounded context and an external system) that translates the models of each side into the other's language. The ACL lives in the downstream context (the one being protected) and contains adapters, translators, and facades. It presents the downstream context's clean domain model inward, while dealing with the upstream context's messy model at its outer edge. The "corruption" being prevented is the contamination of the local domain model by an external model's concepts, naming, and structure.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A translation layer that protects your clean code from inheriting the mess of a legacy or external system.

**One analogy:**
> An embassy in a foreign country is an Anti-Corruption Layer. Inside the embassy walls, everything follows your home country's laws, language, and processes. Outside the walls, the host country's rules apply. The embassy staff translate: they receive documents in the host language, translate them to home language internally, and respond in home language. The ambassador never has to think in the foreign system's language to do their job.

**One insight:**
The ACL is not just an adapter class. It is an explicit architectural decision that says: "this external model is not worthy of existing inside our domain." The more different (or worse) the external model is from your model, the more valuable the ACL.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. An external system's model should never be imported into the core domain model directly.
2. The ACL is the only code that knows about the external system's types and naming conventions.
3. The ACL exposes only your bounded context's domain model on its inward-facing surface.

**DERIVED DESIGN:**
The ACL consists of three layers:

- **Facade**: presents a clean interface to the domain (what the domain calls the external system)
- **Adapter**: implements the facade against the external system's actual client API
- **Translator**: converts external types/structures to domain types/structures

This three-part structure ensures that if the external system changes its API, only the Adapter changes — the Translator and Facade (and all domain code) are unaffected.

**Context Map relationship — Conformist vs ACL:**
If the downstream context can afford to model itself after the upstream (e.g., using a well-designed third-party API), it is a "Conformist." If the upstream's model is poorly designed or legacy, the downstream installs an ACL to translate rather than conform.

**THE TRADE-OFFS:**
**Gain:** Domain model purity, external system isolation, testability (can mock the ACL facade), easier future replacement of external system.
**Cost:** Additional code layer to maintain, translation logic can become complex, potential latency from transformation overhead.

---

### 🧪 Thought Experiment

**SETUP:**
Your Payments bounded context must integrate with a legacy billing system that uses `PYMNT_STAT_CD = 1` to mean "paid" and `PYMNT_STAT_CD = 2` to mean "pending." It also uses a custom epoch timestamp in milliseconds since 1980.

**WITHOUT ACL:**
Domain code directly calls the legacy client: `if (legacyBilling.getPymntStatCd() == 1)`. This code now exists in 15 places. The legacy system "upgrades" and changes `PYMNT_STAT_CD = 3` to also mean "paid" (for a new payment type). You must find and update all 15 places. One is missed. A payment is incorrectly marked as unpaid. Customer support receives 300 tickets.

**WITH ACL:**
```
LegacyBillingAcl.getPaymentStatus(orderId)
  → calls legacy API, gets PYMNT_STAT_CD
  → translates {1,3} → PAID, {2} → PENDING
  → returns domain enum PaymentStatus.PAID
```
When legacy changes, only the ACL's translation logic changes. Domain code `if (status == PaymentStatus.PAID)` is unchanged. One file to update. Zero tickets.

**THE INSIGHT:**
An ACL turns an external system change from a domain-wide search-and-replace into a single-file update. The investment in the ACL pays back with every external system evolution.

---

### 🧠 Mental Model / Analogy

> An ACL is like a customs office at a border crossing. Goods and people enter from the foreign country (external system). The customs office inspects them, re-labels them with domestic standards, and only releases items that meet domestic requirements. If the foreign country changes its labelling system, the customs rules change — but the domestic supply chain (your domain) is unaffected.

- "Customs office" → the ACL translation layer
- "Foreign labelling system" → external system's model and naming conventions
- "Domestic standards" → your bounded context's domain model
- "Goods re-labelled for domestic use" → translation of external types to domain types

Where this analogy breaks down: a customs office introduces real delay at the border. An in-process ACL has negligible overhead. The delay analogy applies only if the ACL involves an extra network call.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
An Anti-Corruption Layer is a translator that sits between your clean new system and a messy old system. Your code talks to the translator in clean language; the translator deals with the old system's mess.

**Level 2 — How to use it (junior developer):**
Create a package or module named `acl` or `integration` in your service. Inside, create an interface that expresses what your domain needs in clean domain terms. Implement that interface using the external system's client. Convert external DTOs to domain objects inside the implementation. Never use the external system's types outside this package.

**Level 3 — How it works (mid-level engineer):**
The ACL has three responsibilities: (1) protocol adaptation (e.g., converting a SOAP call to a domain-friendly method call), (2) model translation (field renaming and type conversion), and (3) error translation (converting external error codes to domain exceptions). Each responsibility can be a separate class. The facade interface owned by the domain lets you swap implementations (e.g., stub for tests, ERP adapter for production) without the domain knowing.

**Level 4 — Why it was designed this way (senior/staff):**
Evans introduced the ACL pattern in "Domain-Driven Design" (2003) specifically for legacy integration scenarios. The key observation was that legacy systems accumulate technical debt in their models over decades — their APIs are shaped by the database schema, not the business domain. Without an ACL, every new service that touches legacy becomes legacy-shaped over time. The ACL is the architectural seam that enables the Strangler Fig migration pattern: you can replace the legacy system incrementally, updating only the ACL adapter for each replaced component, while the domain remains stable throughout the migration.

---

### ⚙️ How It Works (Mechanism)

**ACL structure:**

```
┌─────────────────────────────────────────────┐
│          Your Bounded Context               │
│                                             │
│  ┌───────────────────┐                      │
│  │   Domain Model    │                      │
│  │  (clean language) │                      │
│  └─────────┬─────────┘                      │
│            │ calls                          │
│  ┌─────────▼─────────┐                      │
│  │  ACL Facade       │ ← domain interface   │
│  │  (your language)  │                      │
│  └─────────┬─────────┘                      │
│            │ implemented by                 │
│  ┌─────────▼─────────┐                      │
│  │  ACL Adapter      │ ← translation code   │
│  │  (knows both)     │                      │
│  └─────────┬─────────┘                      │
└────────────┼────────────────────────────────┘
             │ calls external API
┌────────────▼────────────────────────────────┐
│       External / Legacy System              │
│      (CUST_TYP_CD, ACCNT_BAL_AMT_01)        │
└─────────────────────────────────────────────┘
```

**Full ACL implementation example:**

```java
// 1. Domain-facing facade (lives in domain layer)
//    — uses only domain types
public interface CustomerRepository {
    Customer findByEmail(Email email);
    void save(Customer customer);
}

// 2. ACL Adapter (lives in integration/acl package)
//    — only class that knows about legacy client
@Component
public class LegacyCrmCustomerRepository
    implements CustomerRepository {

    private final LegacyCrmClient legacyClient;
    private final CustomerTranslator translator;

    @Override
    public Customer findByEmail(Email email) {
        // Call legacy system (cryptic names)
        LegacyCrmRecord record =
            legacyClient.findByCustEmail(email.value());
        if (record == null) return null;
        // Translate to domain model
        return translator.toDomain(record);
    }

    @Override
    public void save(Customer customer) {
        LegacyCrmRecord record = translator.toLegacy(customer);
        legacyClient.upsertCustRecord(record);
    }
}

// 3. Translator (pure mapping logic — easy to test)
@Component
public class CustomerTranslator {
    public Customer toDomain(LegacyCrmRecord r) {
        return Customer.of(
            CustomerId.of(r.getCUST_ID()),
            r.getFIRST_NM() + " " + r.getLAST_NM(),
            Email.of(r.getEMAIL_ADDR()),
            CustomerType.fromCode(r.getCUST_TYP_CD())
        );
    }

    public LegacyCrmRecord toLegacy(Customer c) {
        LegacyCrmRecord r = new LegacyCrmRecord();
        r.setCUST_ID(c.getId().value());
        r.setFIRST_NM(c.getName().firstName());
        r.setLAST_NM(c.getName().lastName());
        r.setEMAIL_ADDR(c.getEmail().value());
        r.setCUST_TYP_CD(c.getType().toCode());
        return r;
    }
}
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
Domain Service calls `customerRepository.findByEmail(email)` → ACL Facade receives call ← YOU ARE HERE → ACL Adapter calls legacy CRM → Legacy returns `LegacyCrmRecord` → Translator converts to `Customer` domain object → Domain Service receives clean `Customer` type → Business logic runs on clean domain object

**FAILURE PATH:**
Legacy CRM is unavailable → ACL Adapter receives HTTP 503 → ACL translates to domain exception `CustomerLookupUnavailableException` → Domain Service handles known exception → Fallback logic (cached customer or error response) → No legacy model types leak into the failure handling path

**WHAT CHANGES AT SCALE:**
At 10x call volume, the ACL's translation overhead (deserialisation + field mapping) becomes measurable. Introduce a caching layer within the ACL (e.g., cache translated domain objects by ID with a short TTL). At 100x, the legacy system itself becomes the bottleneck — the ACL's value increases because you can swap the legacy backend for a new system behind the facade without changing the domain.

---

### 💻 Code Example

**Example 1 — BAD: Legacy model leaking into domain:**

```java
// BAD: domain service uses legacy types directly
@Service
public class OrderService {
    @Autowired
    private ErpOrderClient erpClient;  // legacy client

    public void processOrder(String orderId) {
        // CUST_TYP_CD is a legacy concept — NOT a domain concept
        ErpOrderRecord raw = erpClient.getOrder(orderId);
        if ("Y".equals(raw.getPREM_CUST_FLG())) {  // cryptic flag
            // Legacy-shaped logic in our domain
            applyPremiumDiscount(raw.getORDR_TOTL_AMT_BD());
        }
    }
}
```

**Example 2 — GOOD: Domain service uses ACL facade:**

```java
// GOOD: domain service uses clean domain types
@Service
public class OrderService {
    private final OrderRepository orders; // domain facade

    public void processOrder(OrderId orderId) {
        Order order = orders.findById(orderId);
        if (order.customer().isPremium()) {  // domain language
            order.applyPremiumDiscount();    // domain method
        }
        orders.save(order);
    }
}
// Legacy knowledge is entirely inside the ACL implementation
```

**Example 3 — Testing the ACL translator in isolation:**

```java
@Test
void translatesPremiumFlagToCustomerType() {
    // Test the translation logic without a running legacy system
    LegacyCrmRecord record = new LegacyCrmRecord();
    record.setCUST_TYP_CD("PREM");
    record.setFIRST_NM("Alice");
    record.setLAST_NM("Smith");
    record.setEMAIL_ADDR("alice@example.com");

    Customer customer = translator.toDomain(record);

    assertThat(customer.getType()).isEqualTo(PREMIUM);
    assertThat(customer.getName()).isEqualTo("Alice Smith");
}
// Fast unit test — no network, no legacy system running
```

---

### ⚖️ Comparison Table

| Integration Approach | Model Protection | Maintainability | Complexity | Best For |
|---|---|---|---|---|
| **Anti-Corruption Layer** | Highest | Highest | Medium | Poorly designed or legacy external systems |
| Conformist | None | Low | Low | Well-designed external API you can safely adopt |
| Shared Kernel | Shared | Medium | Low | Closely related contexts with trusted upstream |
| Direct Integration | None | Low | Very Low | AVOID — leads to model corruption |

How to choose: use ACL when external system quality is low, the external API changes frequently, or you anticipate replacing the external system in the future. Use Conformist for high-quality, stable third-party APIs where adoption is a reasonable strategy.

---

### 🔁 Flow / Lifecycle

```
┌────────────────────────────────────────────────┐
│   ACL in Strangler Fig Migration               │
├────────────────────────────────────────────────┤
│ Phase 1 — Legacy-only                          │
│   New service → ACL → Legacy System (all)      │
├────────────────────────────────────────────────┤
│ Phase 2 — Partial migration                    │
│   New service → ACL → New Module (partial)     │
│                     → Legacy System (rest)     │
├────────────────────────────────────────────────┤
│ Phase 3 — Fully migrated                       │
│   New service → ACL → New System (all)         │
│   ← ACL facade is unchanged throughout →       │
├────────────────────────────────────────────────┤
│ Phase 4 — Legacy decommissioned                │
│   New service → ACL → New System               │
│   ACL adapter for legacy deleted               │
│   Domain code untouched throughout             │
└────────────────────────────────────────────────┘
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| The ACL is just an Adapter pattern | The ACL is a strategic DDD decision about context boundaries; the Adapter is a GoF pattern that implements part of the ACL. The ACL is broader in scope and intent |
| ACL is only for legacy systems | Any poorly designed external API justifies an ACL — including modern third-party SaaS APIs with unstable models |
| The ACL adds significant latency | In-process translation adds microseconds. The value of model isolation far outweighs negligible transformation overhead |
| Once built, the ACL never changes | The ACL Adapter changes whenever the external system changes. The Facade and Translator should change rarely |
| You can skip the ACL if the external API is "good enough" | "Good enough today" becomes technical debt. A Conformist approach (no ACL) should be a deliberate choice, not a default |

---

### 🚨 Failure Modes & Diagnosis

**1. ACL Used but Domain Types Still Leak**

**Symptom:** ACL package exists but other services still import `LegacyOrderRecord` directly "just for the ID field."

**Root Cause:** Partial ACL implementation — adapter was created but not enforced architecturally.

**Diagnostic:**
```bash
# Check for direct imports of external client types outside the ACL
grep -rn "import com.legacy\|import com.external" \
  src/main/java --include="*.java" | \
  grep -v "acl\|integration\|adapter"
# Any result = ACL boundary violated
```

**Fix:** Add an ArchUnit test that forbids imports of external client packages outside the ACL. Refactor violations.

**Prevention:** Set up the ArchUnit rule on day one — run it in every build.

**2. ACL Grows Logic — Becomes a Hidden Service**

**Symptom:** The ACL adapter has grown to 3,000 lines with conditional business logic, caching decisions, and retry policies. It is no longer a translation layer.

**Root Cause:** Developers added logic to the "convenient" ACL rather than the appropriate domain service. The ACL is closest to the external system so it "made sense" to add retry logic there.

**Diagnostic:**
```bash
# Check size of ACL classes
find src -path "*/acl/*.java" | \
  xargs wc -l | sort -rn | head -10
# Classes > 200 lines = probably contain business logic
```

**Fix:** Extract retry logic to an infrastructure concern (e.g., Resilience4j policy on the client). Move any business logic to the appropriate domain service. The translator should contain only field mapping.

**Prevention:** Enforce a rule: ACL classes contain only protocol adaptation, field translation, and error mapping — no business logic, no caching, no retry beyond infrastructure-level policies.

**3. ACL Not Tested — Silent Translation Bugs**

**Symptom:** A legacy system status code `7` (a new status added six months ago) silently maps to `null` in the ACL. Orders in status 7 disappear from reports.

**Root Cause:** The translator had no default case for unknown status codes and no exhaustive test coverage.

**Diagnostic:**
```bash
# Check ACL translator test coverage
./mvnw jacoco:report
# Open target/site/jacoco/index.html
# Check coverage for all ACL translator classes
```

**Fix:**
```java
// BAD: translator silently returns null for unknown codes
public OrderStatus toStatus(int code) {
    return switch (code) {
        case 1 -> PENDING;
        case 2 -> CONFIRMED;
        default -> null;  // silent failure!
    };
}

// GOOD: fail loudly for unknown codes
public OrderStatus toStatus(int code) {
    return switch (code) {
        case 1 -> PENDING;
        case 2 -> CONFIRMED;
        case 3 -> SHIPPED;
        default -> throw new AclTranslationException(
            "Unknown order status code: " + code
        );
    };
}
```

**Prevention:** Write exhaustive mapping tests for every value of every translated enum. Alert on `AclTranslationException` in production with a separate high-priority alert.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Bounded Context` — the ACL lives at the boundary between two bounded contexts; you must understand what a context is before designing its protection
- `Domain-Driven Design` — the ACL is a DDD strategic pattern; its purpose is to maintain model purity within a bounded context

**Builds On This (learn these next):**
- `Strangler Fig Pattern` — the ACL is the primary mechanism enabling the Strangler Fig migration: its stable facade allows the backend implementation to be swapped incrementally
- `Adapter Pattern (Microservices)` — the GoF Adapter pattern is the structural implementation of one layer within the ACL

**Alternatives / Comparisons:**
- `Conformist` — a DDD integration pattern where the downstream context adopts the upstream model wholesale — appropriate only when the upstream model is high quality and stable

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ A translation boundary that shields your  │
│              │ domain from external system model mess    │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Legacy/external system models corrupting  │
│ SOLVES       │ the clean bounded context model           │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ The ACL is the architectural seam that    │
│              │ makes the external system replaceable —   │
│              │ change the adapter, not the domain        │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Integrating with poorly designed, legacy, │
│              │ or third-party systems you cannot change  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Upstream is a well-designed, stable API   │
│              │ (Conformist is more appropriate)          │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Model purity and replaceability vs extra  │
│              │ translation code to maintain              │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Build a wall with a well-staffed         │
│              │  customs window."                         │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Strangler Fig Pattern →                   │
│              │ Adapter Pattern → Bounded Context         │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your team implements an ACL between a new Payments bounded context and a legacy SAP billing system. The ACL works perfectly for 6 months. Then the business acquires a second company with a different SAP version. You now need the Payments context to talk to two different SAP systems simultaneously. What changes in your ACL's structure to support multiple upstream implementations, and how do you route calls to the correct implementation without the domain service knowing which SAP version it is talking to?

**Q2.** An ACL translates between your domain's `CustomerStatus` enum (ACTIVE, SUSPENDED, CLOSED) and the legacy CRM's numeric status codes (1, 2, 3, 4, 5). The legacy system adds a new status code 6 meaning "temporarily frozen" — distinct from your SUSPENDED. You have two options: (A) map code 6 to SUSPENDED (losing fidelity), or (B) add a new FROZEN status to your domain model. What are the downstream implications of each choice across your API consumers, event subscribers, and downstream bounded contexts, and which would you choose in a system where payments are blocked for suspended accounts?

