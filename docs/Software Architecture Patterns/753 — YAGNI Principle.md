---
layout: default
title: "YAGNI Principle"
parent: "Software Architecture Patterns"
nav_order: 753
permalink: /software-architecture/yagni-principle/
number: "753"
category: Software Architecture Patterns
difficulty: ★★☆
depends_on: "KISS Principle, DRY Principle, Agile"
used_by: "Code quality, System Design, Clean Code, Technical Debt"
tags: #intermediate, #architecture, #principles, #agile, #clean-code
---

# 753 — YAGNI Principle

`#intermediate` `#architecture` `#principles` `#agile` `#clean-code`

⚡ TL;DR — **YAGNI (You Aren't Gonna Need It)** is the Extreme Programming principle that says never add functionality until it is actually needed — implementing speculative features creates unnecessary cost: design, code, test, document, maintain, and explain code that may never be used.

| #753 | Category: Software Architecture Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | KISS Principle, DRY Principle, Agile | |
| **Used by:** | Code quality, System Design, Clean Code, Technical Debt | |

---

### 📘 Textbook Definition

**YAGNI — You Aren't Gonna Need It** (Ron Jeffries, Extreme Programming, late 1990s): always implement things when you actually need them, never when you just foresee that you might need them. The statement is declarative not prescriptive — "You Aren't GONNA Need It" (not "you won't ever need it"). It acknowledges developers' tendency to predict future requirements and pre-build solutions for them. YAGNI's argument: the cost of building X now (before X is needed) is almost always greater than the cost of building X later (when X is actually needed), because: (1) requirements will change; (2) you now fully understand X's requirements instead of guessing; (3) you don't pay maintenance cost for unused code while waiting for the requirement. YAGNI is an XP principle but applies broadly to any iterative/incremental development.

---

### 🟢 Simple Definition (Easy)

You're packing for a 3-day camping trip. YAGNI: pack what you need for 3 days — clothes, food, tent, sleeping bag. Anti-YAGNI: "I might need scuba gear if there's a lake... I might need snowshoes if it snows... I might need a power generator if my phone dies..." You pack for every scenario. The bag weighs 80 kg. You can barely walk. It never snowed. There was no lake. You never used 90% of what you packed.

---

### 🔵 Simple Definition (Elaborated)

A developer implementing an order API adds `placeOrder()`. Then thinks: "Maybe we'll need bulk ordering someday" — adds `placeBulkOrder()`. "Maybe we'll need order templates" — adds `createOrderTemplate()`. "Maybe we'll need order subscriptions" — adds `createSubscription()`. All speculative. None requested. Each: time to write, time to test, time to document, time to maintain. Three months later: bulk orders never needed, templates removed, subscriptions implemented differently. All that code: wasted effort and now a maintenance liability.

---

### 🔩 First Principles Explanation

**The economics of speculative features:**

```
YAGNI COST MODEL:

  "The cost of a speculative feature":
  
    Cost of BUILDING NOW (when not needed):
    ┌───────────────────────────────────────────────┐
    │ 1. Design cost: thinking through architecture │
    │ 2. Implementation cost: writing the code      │
    │ 3. Testing cost: writing and maintaining tests│
    │ 4. Documentation cost: explaining the feature │
    │ 5. Review cost: code review time              │
    │ 6. Maintenance cost: keeping it working       │
    │    as other code changes (ongoing)            │
    │ 7. Cognitive cost: everyone reading code      │
    │    must understand feature that isn't used    │
    │ 8. Risk cost: speculative code has bugs too.  │
    │    Bugs in unused code: production issues.    │
    └───────────────────────────────────────────────┘
    
    PLUS: Often built wrong — requirements are guessed.
    When it IS actually needed: must refactor anyway.
    
  Cost of BUILDING LATER (when actually needed):
    1. Design: now you have real requirements (cheaper, more accurate)
    2. Implementation: build exactly what's needed (no waste)
    3. Testing: test actual use cases (no guess-tests)
    4. Review: reviewers understand the requirement context
    
  YAGNI ROI: Most speculative features are never used.
  Studies suggest 45-65% of enterprise software features are rarely or never used.
  (Standish Group Chaos Report, 2002 data.)
  
WHAT YAGNI IS NOT:

  1. YAGNI ≠ "Don't design ahead":
     Good design anticipates CHANGE (interfaces, abstractions, boundaries).
     YAGNI: don't BUILD unused features. Do DESIGN for changeability.
     
     YAGNI violation: implementing PayPalPaymentProcessor + StripePaymentProcessor +
     SquarePaymentProcessor when only Stripe is ever going to be used.
     
     Not a YAGNI violation: defining PaymentProcessor interface that Stripe implements.
     If PayPal is needed: add a new class without changing existing code.
     The interface is there for CURRENT clean code, not for speculative future providers.
     
  2. YAGNI ≠ "Write throwaway code":
     Build what you need, build it WELL. YAGNI removes SCOPE; it doesn't reduce QUALITY.
     
  3. YAGNI ≠ "No infrastructure code":
     Logging, error handling, security, health checks: NEEDED NOW.
     These aren't speculative — they serve real, present requirements (operational requirements).
     
  4. YAGNI ≠ Never refactor:
     You refactor to accommodate new requirements (which you DID need).
     
COMMON YAGNI VIOLATIONS:

  1. Plugin/extension points for unknown plugins:
     Adding registry, hooks, lifecycle callbacks "for future extensibility"
     when the feature will never be extended.
     
  2. Generics where a concrete type suffices:
     List<AbstractOrderProcessor<? super BaseOrder, T>> when List<Order> works.
     
  3. Feature flags for non-existent features:
     ENABLE_NEW_CHECKOUT_FLOW=false — never enabled, stays for 2 years.
     
  4. Database columns for future data:
     spare1, spare2, spare3 columns "just in case."
     
  5. API versioning from v1 when v2 has no requirements:
     /api/v1/orders — v2 never created.
     
  6. Caching before proving there's a performance problem:
     Added Redis + cache layer. Service handles 50 req/day. Latency was fine.
     
  7. Abstract factories before multiple implementations exist:
     AbstractAnimalFactory → CatFactory, DogFactory...
     when only Dog is needed and Cat never materializes.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT YAGNI:
- Developers build features "someone might ask for later" — codebase bloats with unused code
- Unused code: still requires maintenance, causes confusion, may have bugs

WITH YAGNI:
→ Build only what's needed now: smaller, focused, maintainable codebase
→ When requirement actually arrives: fuller understanding, better implementation

---

### 🧠 Mental Model / Analogy

> Building a house and pre-installing underground pipes for a swimming pool that's not in the plans. "I'll probably want a pool eventually." The pipes cost time, money, and effort. They sit unused for 10 years. When a pool IS built: different contractor, different pool location, different piping requirements. The pre-installed pipes don't fit. They're in the way. They have to be removed. The "preparation" created extra cost both when installed AND when removed.

"Pre-installed pipes for a maybe-pool" = speculative feature code
"Different pool location when finally built" = requirements changed; code written wrongly
"Pipes in the way/must be removed" = unused code is a liability, not an asset

---

### ⚙️ How It Works (Mechanism)

```
YAGNI DECISION FILTER:

  Feature/code idea arrives:
  
         ┌─────────────────────────────────────┐
         │ Is this feature in current sprint   │
         │ requirements / acceptance criteria? │
         └──────────────┬──────────────────────┘
                        │
               ┌────────▼─────────┐
               │ YES               │ NO
               │                   │
               ▼                   ▼
       Build it now.        Add to backlog.
       Build it well.       If it's ever
       Test it.             prioritized:
       Ship it.             build it then.
```

---

### 🔄 How It Connects (Mini-Map)

```
Speculative feature thinking ("we'll probably need X")
        │
        ▼ (YAGNI filter)
YAGNI Principle ◄──── (you are here)
(build only what's needed now, defer everything else)
        │
        ├── KISS: YAGNI is KISS applied to features (don't add complexity not needed)
        ├── Agile: YAGNI is a core XP practice; aligns with "just in time" development
        ├── Refactoring: build simple now; refactor toward better design when requirements arrive
        └── Technical Debt: speculative features ARE a form of technical debt
```

---

### 💻 Code Example

```java
// YAGNI VIOLATION — implementing multi-tenant support when current requirement is
// a single-tenant app for one customer:
interface TenantAwareRepository<T> {
    T findById(TenantId tenantId, EntityId entityId);
    List<T> findByTenant(TenantId tenantId, Pageable pageable);
    T save(TenantId tenantId, T entity);
}

class MultiTenantOrderRepository implements TenantAwareRepository<Order> {
    // complex tenant-scoped queries, tenant isolation logic...
    // 200 lines for multi-tenancy that will never be used
}

// ────────────────────────────────────────────────────────────────────

// YAGNI-compliant — build for current requirement (single tenant):
interface OrderRepository {
    Optional<Order> findById(OrderId id);
    List<Order> findAll(Pageable pageable);
    Order save(Order order);
}

class JpaOrderRepository implements OrderRepository {
    // straightforward JPA implementation
    // 30 lines. Clean. Correct. Tested.
}

// When multi-tenancy is actually required: refactor then.
// By then: you know if it needs row-level security, separate schemas, or separate DBs.
// You build the RIGHT solution with REAL requirements.
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| YAGNI means don't plan ahead architecturally | YAGNI applies to IMPLEMENTATION, not to DESIGN. Good architecture creates extensible designs (e.g., interfaces for dependencies). YAGNI says don't CREATE the second implementation of an interface until it's actually needed. The interface itself isn't a YAGNI violation — it serves the current code cleanly |
| YAGNI violates DRY (you end up duplicating when you do need the feature) | YAGNI and DRY operate at different stages. DRY: eliminate existing duplication. YAGNI: don't pre-build future features. They don't conflict — apply YAGNI to decide scope, apply DRY when implementing what IS in scope |
| If you practice YAGNI, you'll constantly refactor and rewrite | If requirements frequently invalidate current code, the problem is poor requirements definition, not YAGNI. Well-applied YAGNI + good design (clean interfaces, separation of concerns) means adding a new feature typically extends the existing design rather than rewrites it |

---

### 🔥 Pitfalls in Production

**YAGNI violation: generic event system for one event type:**

```java
// ANTI-YAGNI: building generic event infrastructure for 1 event:
interface Event { String type(); Instant timestamp(); }
interface EventHandler<T extends Event> { void handle(T event); Class<T> eventType(); }

class EventBus {
    private Map<Class<?>, List<EventHandler<?>>> handlers = new HashMap<>();
    <T extends Event> void subscribe(EventHandler<T> handler) { ... }
    <T extends Event> void publish(T event) { ... }
}
// Used once: OrderPlacedEvent → EmailHandler.

// YAGNI FIX (current requirement: one event, one handler):
class OrderPlacedEventHandler {
    void handle(OrderPlacedEvent event) {
        emailService.sendOrderConfirmation(event.customerId(), event.orderId());
    }
}

// Direct call from OrderService:
orderPlacedEventHandler.handle(new OrderPlacedEvent(order.id(), customer.id()));

// When there are 5+ event types and 10+ handlers: THEN build the event bus.
// You'll also know by then: sync vs. async? ordering guarantees? dead letter queue?
// YAGNI lets you answer those with REAL experience, not guesses.
```

---

### 🔗 Related Keywords

- `KISS Principle` — YAGNI is KISS at the feature level; related but different scope
- `DRY Principle` — DRY removes existing duplication; YAGNI prevents premature generalization
- `Agile` — YAGNI is a core XP practice; aligned with iterative, just-in-time development
- `Technical Debt` — speculative code is technical debt (maintenance without value)
- `Refactoring` — the answer to YAGNI: when requirements arrive, refactor toward the design needed

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Implement features when needed, never when │
│              │ you just predict they might be needed.     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Developer wants to add "for future use"   │
│              │ code; adding abstraction layers for        │
│              │ hypothetical extensibility                │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Not an excuse to skip known operational   │
│              │ needs: logging, security, health checks,  │
│              │ known performance requirements            │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Pack for the trip you're taking, not the │
│              │  trips you might someday take."           │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ KISS Principle → DRY Principle →          │
│              │ Technical Debt → Refactoring              │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A developer argues: "YAGNI says I shouldn't add caching now, since we don't have performance problems yet. But once we do, adding Redis will require refactoring the entire data access layer." How do you evaluate this? Is deferring caching a YAGNI-correct decision or is this a case where architectural preparation is justified? What would you need to know about the system to decide?

**Q2.** A team is building a payment processing system. They decide to implement a `PaymentGateway` interface with only one implementation: `StripePaymentGateway`. The PM says: "We'll definitely add PayPal in Q3." Is defining the interface a YAGNI violation? Does the PM's statement change your answer? What probability threshold (how certain does "Q3 PayPal" need to be) justifies adding the interface vs. just hardcoding Stripe?
