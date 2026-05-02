---
layout: default
title: "API Backward Compatibility"
parent: "HTTP & APIs"
nav_order: 249
permalink: /http-apis/api-backward-compatibility/
number: "0249"
category: HTTP & APIs
difficulty: ★★☆
depends_on: REST, API Versioning, JSON Schema
used_by: Public APIs, Microservices, SDK Design
related: API Versioning, OpenAPI/Swagger, API Deprecation Strategy, Breaking Changes
tags:
  - api
  - backward-compatibility
  - breaking-changes
  - versioning
  - intermediate
---

# 249 — API Backward Compatibility

⚡ TL;DR — API backward compatibility means existing consumers continue to work without modification after the provider deploys a change; a **breaking change** (removing a field, renaming an endpoint, changing a data type) requires a new API version, while a **non-breaking change** (adding an optional field, adding a new endpoint) can be deployed without incrementing the version.

| #249 | Category: HTTP & APIs | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | REST, API Versioning, JSON Schema | |
| **Used by:** | Public APIs, Microservices, SDK Design | |
| **Related:** | API Versioning, OpenAPI/Swagger, API Deprecation Strategy, Breaking Changes | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Stripe has 20,000 customer integrations. Engineering wants to rename the `customer_email`
field to `billing_email` for clarity. Without backward compatibility discipline:
deploy the rename → 20,000 integrations break simultaneously. Every single customer
needs to update their code and redeploy before they can use Stripe again. Alternative:
keep both names forever → technical debt accumulates → the API definition becomes
contradictory and inconsistent. The tension: rapid evolution vs. operational safety
for consumers.

**THE INVENTION MOMENT:**
Postel's Law ("be liberal in what you accept, conservative in what you send") from
1980 captures the core insight: APIs should be tolerant of variations in input and
predictable in output. The formalization of breaking vs. non-breaking change taxonomy
emerged from semantic versioning (semver) applied to APIs. Stripe pioneered the
"version pinning" model (each consumer pinned to the API version at their
integration date). Google's API Design Guide codifies explicit rules for what
constitutes a breaking change.

---

### 📘 Textbook Definition

**API Backward Compatibility** means that a new version of an API implementation
can be used by existing consumers written against a previous version without requiring
those consumers to make any changes. Formally: the new API surface is a superset
of the old — every valid request under the old API remains valid under the new API,
and the response for such requests is semantically equivalent. **Breaking changes**
violate backward compatibility: existing consumers fail after provider deploys.
**Non-breaking changes** maintain compatibility: existing consumers continue working
unchanged. Robustness Principle (Postel's Law): "Be conservative in what you do,
be liberal in what you accept from others." Applied to APIs: accept unexpected
fields gracefully (don't error), only promise what you explicitly document.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Backward compatibility means "update the provider without breaking the consumer" —
knowing exactly which changes are safe and which require a version bump.

**One analogy:**

> Backward compatibility is like power outlets.
> Adding a USB-C port to a wall outlet (new endpoint) doesn't break existing
> appliances plugged into standard outlets (existing consumers). But removing
> the standard outlets (removing endpoints) would require every consumer to change
> their plug (update integration). The rule: you can add, you cannot remove or reshape.

**One insight:**
The most common mistake is forgetting that consumers depend on the ABSENCE of fields
too. Client code like `if (response.status == null) { use default; }` can break if
you populate `status` with a value — even though you're "adding" information, not
removing it.

---

### 🔩 First Principles Explanation

**BREAKING vs NON-BREAKING CHANGE TAXONOMY:**

```
NON-BREAKING (safe to deploy without version increment):
  ✅ Add a new optional field to a response
  ✅ Add a new optional request parameter (with default value)
  ✅ Add a new endpoint or operation
  ✅ Add a new HTTP status code that was not previously used (if consumers don't exhaustively check codes)
  ✅ Relax a constraint (was required → now optional)
  ✅ Expand an enum: add a new allowed value
  ✅ Add a new HTTP method to an existing resource

BREAKING (requires new API version):
  ❌ Remove a field from a response
  ❌ Rename a field (functionally equivalent to remove + add)
  ❌ Change a field's data type (string "123" → integer 123)
  ❌ Remove an endpoint
  ❌ Change URL path structure
  ❌ Add a required field to a request
  ❌ Narrow a constraint (was optional → now required)
  ❌ Change HTTP method semantics
  ❌ Change error code mapping (200 → 201 for same operation)
  ❌ Remove an enum value (consumers may have stored/switch on the old value)

GRAY AREA (depends on consumers):
  ⚠️ Change validation (more strict): was accepting → now rejecting same input
  ⚠️ Change behavior semantics (same response shape, different meaning)
  ⚠️ Change ordering of array results (some consumers depend on order)
  ⚠️ Add required field with default: non-breaking for existing calls, potentially surprising
  ⚠️ Expand an enum: if consumers have exhaustive switch statements, new value = unhandled case
```

**ROBUSTNESS PRINCIPLE IN PRACTICE:**

```java
// Fragile consumer (breaks on unknown fields):
class UserDto {
    // Will fail if server adds unknown field 'avatarUrl'
    // (strict Jackson by default does NOT fail on unknown fields, but explicit config might)
    @JsonProperty("id")
    private Long id;
    @JsonProperty("name")
    private String name;
}

// Robust consumer (tolerant reader pattern):
@JsonIgnoreProperties(ignoreUnknown = true)  // ← KEY: tolerate new fields
class UserDto {
    private Long id;
    private String name;
    // Any new fields added by provider are silently ignored — forward compatible
}

// Robust consumer for enums:
@JsonEnumDefaultValue
enum UserStatus {
    ACTIVE, INACTIVE,
    UNKNOWN  // ← fallback for any new enum value added by provider
}
```

---

### 🧪 Thought Experiment

**SCENARIO:** Payment API evolution over 18 months.

```
V1 (Day 0):       GET /payments/{id}
                  Response: {"id": "PAY-001", "amount": 99.99, "status": "completed"}

Month 3 CHANGE:   Add "currency" field → non-breaking
                  Existing consumers: ignore currency (they don't use it)
                  → safe to deploy as-is

Month 6 CHANGE:   Add "metadata" object → non-breaking
                  {"id": "PAY-001", ..., "metadata": {"referenceId": "REF-123"}}
                  → safe to deploy as-is

Month 9 CHANGE:   Rename "amount" to "total_amount" for clarity → BREAKING
                  All consumers using response.amount → break
                  → REQUIRES /v2/payments/{id}
                  Strategy: deploy /v2 endpoint with "total_amount"
                            keep /v1 endpoint serving "amount" (deprecated, sun-set date set)
                            add "Sunset: Sat, 31 Dec 2025 23:59:59 GMT" header to v1 responses

Month 12:         Consumers notified. Migration window.
Month 18:         /v1 endpoint removed per published sunset date.
```

---

### 🧠 Mental Model / Analogy

> Backward compatibility is like a USB standard's rule of "do not remove what exists."
> USB 1.0 devices still work in USB 3.0 ports (backward compatible).
> USB 4 didn't remove USB-A ports from existing devices already shipped.
> The rule: new versions extend, they do not remove.
> When USB-A must eventually be removed: a LONG transition period is announced,
> adapters (compatibility shims) are provided, and a sunset date is published years ahead.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Backward compatibility means "when we update the API, everyone's existing code still works."
Breaking compatibility is when you change the API in a way that forces every user to
update their code — like rearranging all the furniture in someone else's house overnight.

**Level 2 — How to use it (junior developer):**
Follow the rule: "you can add, you cannot remove or rename." When you must make a
breaking change: create a new URL version (`/v2/`) and deprecate the old one with a
`Sunset` date header. On the consumer side: always use `@JsonIgnoreProperties(ignoreUnknown = true)`
in Java DTOs to tolerate provider adding new fields.

**Level 3 — How it works (mid-level engineer):**
API versioning is the mechanism for managing breaking changes. Non-breaking changes
deploy continuously; breaking changes trigger a new version. The key practice is
automated breaking change detection in CI: tools like `openapi-diff` or `oasdiff`
compare the current spec against the previous version and report breaking changes.
This catches unintentional breaking changes before deployment. Consumer-driven contract
tests (Pact) provide an additional safety net: if a field is removed, consumers'
pact files fail provider verification before deployment. The "expand-contract" pattern
(strangler fig for APIs): add new field alongside old field (expand), migrate consumers
to new field, then remove old field (contract) — two deployments, zero downtime.

**Level 4 — Why it was designed this way (senior/staff):**
The fundamental challenge of backward compatibility is that "compatible" is defined
by consumers, not providers. Providers see the API; consumers see their dependencies
on specific aspects of the API. Hyrum's Law (Google, Hyrum Wright): "With a sufficient
number of users of an API, it does not matter what you promise in the contract —
all observable behaviors of your system will be depended upon by somebody." This means
even undocumented implementation details (response ordering, specific error message text)
become de-facto contracts. The solution isn't to promise less — it's to build robust
consumers (tolerant readers) AND enforce explicit contracts via tooling (contract tests).
Stripe's version pinning model takes this to its logical extreme: each consumer is
locked to the API version at their integration date, and Stripe maintains EVERY version
ever released. This maximizes compatibility but creates immense long-term maintenance cost.

---

### ⚙️ How It Works (Mechanism)

```
EXPAND-CONTRACT PATTERN (additive migration):

PROBLEM: Rename field "amount" → "totalAmount"

NAIVE APPROACH (BREAKING):
  Deploy: response changes "amount" → "totalAmount"
  All consumers using "amount" → break simultaneously

EXPAND-CONTRACT (NON-BREAKING MIGRATION):

  Step 1 — EXPAND: Add new field alongside old
    Response: {"amount": 99.99, "totalAmount": 99.99}  ← BOTH fields
    Non-breaking: existing consumers still see "amount"
    Notify: "amount is deprecated, use totalAmount, sunset in 90 days"

  Step 2 — Consumers migrate
    Each consumer: update code to use "totalAmount"
    Deploy their updates
    Pact consumer tests: updated to expect "totalAmount"

  Step 3 — CONTRACT: Remove old field
    After all consumers confirmed migrated + sunset date passed
    Remove "amount" from response
    Breaking change — but all consumers already handle it

AUTOMATED DETECTION IN CI:
  oasdiff breaking-changes \
    --base openapi-previous.yaml \
    --revision openapi-current.yaml
  # Reports: "field 'amount' removed from response schema (breaking change)"
  # Fails build if breaking change not intentional (new version should have been created)
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
LIFECYCLE OF A BREAKING CHANGE:

  1. Provider discovers need: rename field or restructure endpoint

  2. Breaking change impact assessment:
     - oasdiff: detect what's breaking
     - Pact Broker: which consumers depend on affected fields?

  3. Decision: can we use expand-contract pattern?
     If YES: expand phase (add new field alongside old)
     If NO: create /v2/ endpoint

  4. Deprecation notice:
     Add "Deprecated: true" to old field in OpenAPI spec
     Add `Sunset` response header (RFC 8594): "Sunset: Thu, 31 Dec 2026 23:59:59 GMT"
     Add `Deprecation` response header: "Deprecation: @1735689600"

  5. Consumer migration:
     Monitor: track consumers still calling deprecated endpoint
     Notify: email, change log, API changelog RSS

  6. Sunset date: remove old field/endpoint
     Pact verification: all consumer pacts must be updated before this step
```

---

### 💻 Code Example

```java
// Provider: dual-field response during expand phase
@Schema(description = "Payment response")
public class PaymentResponse {

    @Schema(description = "Transaction amount", deprecated = true)
    @Deprecated  // IDE warning for internal callers
    private BigDecimal amount;  // ← keep during transition

    @Schema(description = "Total transaction amount (use this instead of 'amount')")
    private BigDecimal totalAmount;

    // Set both fields for backward compatibility
    public static PaymentResponse from(Payment payment) {
        var response = new PaymentResponse();
        response.setTotalAmount(payment.getAmount());
        response.setAmount(payment.getAmount());  // backward compat: will remove after sunset
        return response;
    }
}

// Sunset header via filter
@Component
public class DeprecationHeaderFilter implements Filter {

    private static final Set<String> DEPRECATED_PATHS = Set.of(
        "/api/v1/payments", "/api/v1/users"
    );

    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain)
            throws IOException, ServletException {
        String path = ((HttpServletRequest) request).getRequestURI();
        if (DEPRECATED_PATHS.stream().anyMatch(path::startsWith)) {
            HttpServletResponse httpResponse = (HttpServletResponse) response;
            httpResponse.setHeader("Deprecation", "@1735689600");
            httpResponse.setHeader("Sunset", "Thu, 31 Dec 2026 23:59:59 GMT");
            httpResponse.setHeader("Link", "</api/v2/payments>; rel=\"successor-version\"");
        }
        chain.doFilter(request, response);
    }
}

// Consumer: robust tolerant reader
@JsonIgnoreProperties(ignoreUnknown = true)
public class PaymentDto {
    private Long id;

    // Use new field if present; tolerates old-format responses with only "amount"
    @JsonProperty("totalAmount")
    private BigDecimal totalAmount;

    @JsonProperty("amount")
    private BigDecimal amount;

    public BigDecimal getEffectiveAmount() {
        return totalAmount != null ? totalAmount : amount;  // graceful fallback
    }
}
```

---

### ⚖️ Comparison Table

| Change Type                 | Breaking? | Migration Required       | Safe to Deploy   |
| --------------------------- | --------- | ------------------------ | ---------------- |
| Add optional response field | No        | No                       | Immediately      |
| Add optional request param  | No        | No                       | Immediately      |
| Remove response field       | Yes       | Consumer update + sunset | New version only |
| Rename field                | Yes       | Consumer update + sunset | New version only |
| Change field type           | Yes       | Consumer update + sunset | New version only |
| Remove endpoint             | Yes       | Consumer migration       | After sunset     |
| Add required request field  | Yes       | Consumer update          | New version only |
| Add new enum value          | Soft      | Consumer handles unknown | Gradually        |

---

### ⚠️ Common Misconceptions

| Misconception                                       | Reality                                                                                                                                                                                                  |
| --------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Adding a field is always safe                       | Adding a required field to a request is BREAKING. Adding to a response is non-breaking only if consumers use `@JsonIgnoreProperties(ignoreUnknown=true)`. Strict deserializers may reject unknown fields |
| Versioning solves all compatibility problems        | Versioning manages breaking changes but creates maintenance burden. Prefer non-breaking changes with expand-contract over quick version increments                                                       |
| Consumers should update immediately when deprecated | Give explicit, generous sunset windows (minimum 6 months for public APIs, 3 months for internal). Forced rapid migrations create trust problems                                                          |
| Enum expansion is non-breaking                      | Adding enum values is a soft-breaking change: Postel's Law says consumers SHOULD handle unknown enum values, but many switch statements don't have a default case                                        |

---

### 🚨 Failure Modes & Diagnosis

**Undetected Breaking Change in Production**

Symptom:
After a "non-breaking" deploy, consumer services report 500 errors. The provider team
insists they only "added" fields. Investigation: one consumer has strict Jackson config
`FAIL_ON_UNKNOWN_PROPERTIES = true` — a new optional response field causes 500s.

Diagnostic:

```java
// Check consumer's Jackson configuration:
ObjectMapper mapper = objectMapper.copy()
    .configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false); // fix

// Detect in CI:
// oasdiff between previous and current openapi.yaml:
// $ oasdiff breaking-changes --base v1.0.yaml --revision v1.1.yaml
// Even for "non-breaking" changes: review if consumers have strict deserializers

// Prevention: @JsonIgnoreProperties(ignoreUnknown = true) on all DTO classes
```

---

### 🔗 Related Keywords

- `API Versioning` — the mechanism for publishing breaking changes without breaking existing consumers
- `API Deprecation Strategy` — the process of retiring old API versions
- `OpenAPI/Swagger` — tooling for detecting breaking changes via spec comparison
- `API Contract Testing` — pact tests surface consumer breakages before deployment

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ New API deploy doesn't break existing    │
│              │ consumers                                │
├──────────────┼───────────────────────────────────────────┤
│ SAFE CHANGES │ Add optional fields/params/endpoints     │
│ BREAKING     │ Remove/rename/change-type — needs v++    │
├──────────────┼───────────────────────────────────────────┤
│ PATTERN      │ Expand-contract: add new → migrate →     │
│              │ remove old (two non-breaking deploys)    │
├──────────────┼───────────────────────────────────────────┤
│ CONSUMER     │ @JsonIgnoreProperties(ignoreUnknown=true)│
│ SAFETY       │ + default enum value for unknown values  │
├──────────────┼───────────────────────────────────────────┤
│ HYRUM'S LAW  │ All observable behaviors become contracts│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ API Versioning → API Deprecation Strategy│
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q.** Your public API has 500 external consumers. Hyrum's Law applies: some consumers depend on your response array always being alphabetically sorted (you never documented this, it's just an artifact of your SQL ORDER BY). Your team needs to change the storage layer, and the new store returns results in insertion order. Examine this through the lens of Postel's Law and Hyrum's Law: is this a breaking change? How do you simultaneously respect the rule "undocumented behavior is not a contract" while maintaining trust with real consumers who will break? Propose a policy for handling implicit behavioral contracts.
