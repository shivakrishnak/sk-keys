---
id: DPT-051
title: Boat Anchor Anti-Pattern
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★★☆
depends_on: DPT-042, DPT-049
used_by: DPT-063, DPT-064
related: DPT-042, DPT-049, DPT-050, DPT-072
tags:
  - anti-pattern
  - code-quality
  - intermediate
  - YAGNI
  - dead-code
  - complexity
status: complete
version: 4
layout: default
parent: "Design Patterns"
grand_parent: "Technical Mastery"
nav_order: 51
permalink: /technical-mastery/design-patterns/boat-anchor/
---

⚡ TL;DR - Boat Anchor is retaining code, components, or
infrastructure that is no longer needed "just in case
we need it later" - it adds weight without adding value,
slowing the codebase without benefit.

| #51 | Category: Design Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | DPT-042, DPT-049 | |
| **Used by:** | DPT-063, DPT-064 | |
| **Related:** | DPT-042, DPT-049, DPT-050, DPT-072 | |

---

### 🔥 The Problem This Documents

**THE SETUP:**
A team builds a payment processing system with three
payment gateway integrations: Stripe, PayPal, and
Braintree. After analysis, the business drops Braintree
(low adoption). The developer's response: "We might
re-enable it later. Let me keep the integration code
and just disable the configuration." 

Six months later: PayPal is also dropped. Same response.
A year later: the codebase has two full payment gateway
integrations (4,000 lines each) that are disabled. They
still run in tests (slowly). They still require dependency
updates when the SDKs have vulnerabilities. They still
confuse new developers who wonder "is this Braintree
integration actually used somewhere?"

This is the Boat Anchor: dragging the codebase with
no forward propulsion.

---

### 📘 Definition

The **Boat Anchor** anti-pattern is retaining unused
components - code, classes, services, or infrastructure -
in a system because "we might need it later" or "it
took effort to build, so we should keep it."

Named after the nautical anchor: an anchor held WHILE
a boat is sailing does not help the boat; it is pure
resistance. Keeping unused code "in case we need it"
provides no forward value while slowing development,
increasing maintenance cost, and adding cognitive load.

**Related to, but different from, Lava Flow (DPT-049):**
- Lava Flow: code nobody knows is alive or dead (mystery)
- Boat Anchor: code KNOWN to be unused but DELIBERATELY kept

Both result in dead code in the codebase. The distinction
is intentionality: Lava Flow drifts in; Boat Anchor is
a deliberate decision to retain unused code.

**YAGNI (You Ain't Gonna Need It):**
Boat Anchor is the post-build manifestation of the
YAGNI principle violation: the code WAS built, and
now that it is no longer needed, YAGNI applies to
its retention.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Boat Anchor = keeping unused code "just in case" - it
adds weight, not value.

**One analogy:**
> A hiker who packed a full-size cast iron skillet
> "just in case we cook a large meal." The hiker is
> carrying 3 extra kg for a scenario that never occurred.
> Even if the skillet WAS needed: the cost of carrying it
> the entire trip exceeds the benefit of using it once.
> The correct approach: decide if you'll need the skillet
> BEFORE the trip (YAGNI), not pack it "just in case."
>
> In code: decide if the feature will be needed BEFORE
> building it, not after building it and keeping it unused.

---

### 🔩 Root Causes

**SUNK COST FALLACY:**
"We spent two sprints building the Braintree integration.
Deleting it wastes that effort." The investment is gone
regardless of keeping or deleting. Keeping adds future
cost; deleting does not recover past cost but reduces
future cost.

**YAGNI VIOLATION:**
Planning for "we might need this" features leads to
building AND retaining unused capabilities. The correct
discipline: build only what is needed now. Disable or
delete what is no longer needed.

**GIT MISUNDERSTANDING:**
"What if we need to bring it back?" - Git preserves
all deleted code. `git log -- <deleted-file>` finds
every version. Deletion is never permanent in a version
control system. "Just in case we need it" is always
answerable by "restore from git."

**ORGANIZATIONAL:**
Deleting code feels like destroying work. In some
team cultures, deletion is psychologically difficult
("that was two sprints of work"). This causes Boat
Anchor accumulation.

---

### 🧠 Mental Model

> Boat Anchor is the OPPOSITE of agile code.
> Agile: build what you need now; adapt as requirements
> evolve. Code that no longer serves the current requirements
> should be removed. A codebase should model the CURRENT
> business, not the HISTORICAL business.
>
> A codebase with 20% Boat Anchor code is modeling both
> the current business AND several past versions of the
> business. It answers questions that no longer need answers.
> It defines concepts that no longer exist. It maintains
> integrations with systems that no longer connect.

---

### 📶 Gradual Depth - Two Levels

**Level 1 - Recognition and impact:**
Boat Anchor: code that everyone knows is unused but
nobody removes. Impact:
- Test suite runs disabled Boat Anchor tests (slowness)
- Dependencies must be kept updated even for unused code
  (security patches for unused libraries)
- Cognitive load: every developer asks "is this code
  actually used or is it a Boat Anchor?"
- Compile time, build time, artifact size all increase

**Level 2 - YAGNI discipline:**
YAGNI (You Ain't Gonna Need It) - XP principle by
Ron Jeffries. Applied to retention: "You Ain't Gonna
Need It" means: if it is not needed now, delete it.
It can be rebuilt when needed (or restored from git).
The probability-weighted cost of keeping it (maintenance
cost × probability it is ever used) almost always
exceeds the cost of deleting and rebuilding it
(development time × probability it is actually needed).

---

### ⚙️ Mechanism

```
Boat Anchor Cost Model
┌─────────────────────────────────────────────────────────┐
│                                                         │
│ Scenario: disabled Braintree integration (4000 lines)   │
│                                                         │
│ MONTHLY MAINTENANCE COST OF KEEPING:                    │
│ - 2 hours/month: security patches for Braintree SDK     │
│ - 1 hour/month: keep tests green (compile warnings)     │
│ - 0.5 hr/dev × 4 devs/month: cognitive overhead         │
│ Total: ~5 hours/month                                   │
│                                                         │
│ 12 months: 60 hours of waste                            │
│                                                         │
│ IF BRAINTREE IS RE-ENABLED (scenario: 5% probability):  │
│ Rebuild from git: 1-2 days                              │
│ Expected cost of deletion: 0.05 × 2 days = 0.1 day     │
│                                                         │
│ 60 hours maintenance >> 0.1 day rebuild risk            │
│ YAGNI verdict: DELETE                                   │
└─────────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Boat Anchor (anti-pattern):**

```java
// BAD: Payment service retaining unused gateway integrations
@Service
public class PaymentService {

    // BOAT ANCHOR: Braintree disabled since Q2 2023
    // Kept "just in case we re-enable it"
    @Autowired(required = false)
    private BraintreeGateway braintreeGateway;

    // BOAT ANCHOR: PayPal disabled since Q4 2023
    // "The business might bring PayPal back"
    @Autowired(required = false)
    private PayPalGateway paypalGateway;

    // Active: only Stripe is used
    @Autowired
    private StripeGateway stripeGateway;

    public PaymentResult process(Payment payment) {
        // Commented-out Boat Anchor logic:
        // if (config.isPayPalEnabled()) {
        //     return paypalGateway.charge(payment);
        // }
        // if (config.isBraintreeEnabled()) {
        //     return braintreeGateway.charge(payment);
        // }
        return stripeGateway.charge(payment);
    }
}
// BraintreeGateway and PaypalGateway still compile.
// Their dependencies still require security updates.
// Their tests still run in CI.
// New developers wonder: "are these actually used?"
```

**Example 2 - Clean deletion with git safety net:**

```java
// GOOD: Delete unused integrations; git preserves history

// Step 1: Verify truly unused
// grep -r "BraintreeGateway" src/ → only PaymentService
// grep -r "PayPalGateway" src/ → only PaymentService
// git log --all -- src/.../BraintreeGateway.java
//   → last changed 2023-04-15 "disable braintree integration"

// Step 2: Delete
// rm src/.../BraintreeGateway.java
// rm src/.../PaypalGateway.java
// Remove Braintree + PayPal SDK from pom.xml
// Remove commented-out code from PaymentService

// Step 3: Commit with retrieval instructions
// git commit -m "Remove disabled payment gateway integrations
//   - BraintreeGateway: disabled 2023-04-15, no usages
//   - PayPalGateway: disabled 2023-11-30, no usages
//   - Recoverable: git show 3fa8c12:src/.../BraintreeGateway.java
//   YAGNI: restore from git if business re-enables either gateway"

// RESULT: Clean PaymentService:
@Service
public class PaymentService {
    @Autowired
    private StripeGateway stripeGateway;  // the only gateway

    public PaymentResult process(Payment payment) {
        return stripeGateway.charge(payment);
    }
}
// Focused. Testable. No cognitive load from unused code.
```

---

### ⚖️ Boat Anchor vs Lava Flow

| Aspect | Boat Anchor | Lava Flow |
|---|---|---|
| Developer awareness | KNOWS it's unused | Doesn't know if it's used |
| Retention reason | Deliberate ("might need later") | Fear ("might break if removed") |
| Recoverability | Clear (last disabled by X for reason Y) | Unknown |
| Risk to remove | Low (known unused) | Medium (unknown) |
| Solution | YAGNI discipline + delete | Archaeology + verify then delete |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Keeping code is always safer than deleting it | Unused code requires maintenance (security patches, build compatibility). It adds cognitive load. It slows CI. Keeping has ongoing cost; deleting is a one-time risk that git eliminates |
| "We might need it" justifies keeping it | "Might need it" is almost never realized. The correct calculation: expected maintenance cost > expected value of eventual reuse? If yes: delete. Almost always: yes |
| Boat Anchor only applies to code | Boat Anchor applies to infrastructure too: running idle servers, unused cloud resources, disabled microservices, unused database tables. All carry cost without benefit |
| Boat Anchor is a personal style issue | Boat Anchor accumulation is a team and process issue. Teams without YAGNI discipline, code ownership, and regular cleanup sprints accumulate Boat Anchors systematically |

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Unused code kept "just in case" -        │
│              │ adds weight, not value                   │
├──────────────┼──────────────────────────────────────────┤
│ ROOT CAUSE   │ Sunk cost fallacy; "we might need it";  │
│              │ not trusting git to restore deleted code │
├──────────────┼──────────────────────────────────────────┤
│ YAGNI        │ "You Ain't Gonna Need It" - applies to  │
│              │ retention: if not needed now, delete    │
├──────────────┼──────────────────────────────────────────┤
│ GIT SAFETY   │ Git preserves all deleted code.         │
│              │ Deletion is never permanent.            │
├──────────────┼──────────────────────────────────────────┤
│ FIX          │ Verify unused → delete → commit message │
│              │ with git recovery path                  │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ DPT-052: CQRS Pattern                   │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Boat Anchor = code KNOWN to be unused but DELIBERATELY
   kept "just in case." Unlike Lava Flow, the team knows
   it's unused. YAGNI applies: delete it.
2. Git is the safety net for deletion. "What if we need
   it later?" → restore from git. This eliminates the
   risk justification for keeping Boat Anchors.
3. Real cost of keeping: security patches for unused
   dependencies, slow CI running unused tests, cognitive
   overhead for every developer who wonders "is this used?"
   Delete and save that cost.

