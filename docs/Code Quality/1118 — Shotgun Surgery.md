---
layout: default
title: "Shotgun Surgery"
parent: "Code Quality"
nav_order: 1118
permalink: /code-quality/shotgun-surgery/
number: "1118"
category: Code Quality
difficulty: ★★★
depends_on: Code Smell, Divergent Change, Refactoring
used_by: Refactoring, Technical Debt, Code Review
related: Divergent Change, Code Smell, Feature Envy
tags:
  - antipattern
  - advanced
  - bestpractice
  - architecture
---

# 1118 — Shotgun Surgery

⚡ TL;DR — Shotgun surgery is a code smell where a single logical change requires making many small edits to many different classes — the opposite of a cohesive, localised change.

| #1118 | Category: Code Quality | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Code Smell, Divergent Change, Refactoring | |
| **Used by:** | Refactoring, Technical Debt, Code Review | |
| **Related:** | Divergent Change, Code Smell, Feature Envy | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
The team needs to add a new field `businessCategory` to orders. This requires changes to: `Order.java`, `OrderDto.java`, `OrderMapper.java`, `OrderRepository.java`, `OrderController.java`, `OrderSearchService.java`, `OrderReportService.java`, `OrderExportService.java`, and 3 different database migration files. A developer makes the change in 11 places. Misses one: `OrderSearchService.java`. The search index doesn't include `businessCategory`. The field is searchable everywhere except in the main search UI. Bug ships.

**THE BREAKING POINT:**
When a single logical change requires many separate physical changes in many separate files, the probability of missing one change approaches certainty as the number of changes grows. Eleven changes to complete one logical feature isn't a complexity of the feature — it's a symptom of poor cohesion.

**THE INVENTION MOMENT:**
This is exactly why **Shotgun Surgery** is named as a smell: like a shotgun blast that scatters pellets everywhere, this type of change scatters its effects across many files — and missing any one pellet leaves the system in an inconsistent state.

---

### 📘 Textbook Definition

**Shotgun Surgery** is a code smell (Fowler, "Refactoring") describing the situation where a single logical change requires making small modifications to many different classes. Each change is small, but the sum of changes needed is large — and missing any one creates inconsistent behaviour. Shotgun Surgery is the inverse of **Divergent Change**: Divergent Change describes one class that changes too often for many reasons (too much concentration); Shotgun Surgery describes one logical change requiring changes in too many classes (too much dispersion). Shotgun Surgery typically manifests when cross-cutting concerns (logging, caching, security, event publishing) are implemented inline in many classes rather than centralised. Refactoring: **Move Method / Move Field** (consolidate scattered changes into the class most responsible for the concept), **Inline Class** (if the shotgun changes are in tiny classes that can be merged), **Introduce Domain Event** (if the pattern is "add X and notify all dependents" — a domain event decouples the addition from the notification).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
One change, many files — a symptom of scattered responsibility.

**One analogy:**
> Shotgun Surgery is like updating a phone book where every person's name appears in a different section with a different formatting convention. To rename "John Smith" to "John A. Smith" you must update: the white pages (section A-K), the business pages, the emergency contacts, the school directory, and the neighbourhood registry. Each update is small. Missing one leaves "John Smith" and "John A. Smith" coexisting as if they're different people. One identity, scattered representation.

**One insight:**
Shotgun Surgery indicates that a concept is not encapsulated. If changing one concept requires changing many places, the concept doesn't have one home — it has many fragmentary representations.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. A single logical concept should have a single physical home (encapsulation). Changes to the concept should be localised to that home.
2. When a concept's implementation is scattered across N classes, every change to the concept requires N edits — and missing any one creates a partially-updated system.
3. Cross-cutting concerns (logging, auditing, caching) that appear inline in many classes are the canonical source of shotgun surgery.

**DERIVED DESIGN:**
Since cohesion requires related code to be near related code, solving shotgun surgery requires consolidating scattered concept pieces into a single location. Aspect-Oriented Programming (AOP) addresses the cross-cutting concern case: logging/caching/security scattered across all services can be centralised in aspects that apply automatically.

**THE TRADE-OFFS:**
Gain: One change in one place to change the concept; no missed updates; reduced debugging of inconsistent states.
Cost: Consolidation requires refactoring existing code; AOP has its own debugging complexity; some consolidations require deeper architectural restructuring.

---

### 🧪 Thought Experiment

**SETUP:**
Requirement: "Add audit logging to all financial operations." Without centralised design: this change touches 25 methods across 8 classes. With AOP: this change touches 1 aspect file.

**WITHOUT CONSOLIDATION:**
Developer adds `auditLog.record(...)` to 25 financial operation methods. Adds 19 of 25. Misses 6. Six financial operations are not audited. Compliance audit fails. Finding the 6 missing calls requires reading all financial code.

**WITH AOP:**
```java
@Aspect
public class FinancialAuditAspect {
    @Around("@annotation(FinancialOperation)")
    public Object auditFinancialOp(ProceedingJoinPoint jp) {
        auditLog.record(jp.getSignature(), jp.getArgs());
        return jp.proceed();
    }
}
```
One file. Every method annotated `@FinancialOperation` is automatically audited. Adding new financial operations: add `@FinancialOperation` annotation. Zero shotgun surgery.

**THE INSIGHT:**
The requirement changed from 25-file update to 1-file update by recognising the cross-cutting concern and centralising it.

---

### 🧠 Mental Model / Analogy

> Shotgun Surgery is like running a franchise restaurant where each location stores the "chicken recipe" on paper inside the location. When corporate updates the recipe, they must physically visit (or call) each location. Miss one location: inconsistent food. The solution: centralize the recipe. All locations fetch the recipe from headquarters — one update, one location, consistent everywhere. Code consolidation is the same: move the scattered recipe (concept) to headquarters (a single class or AOP aspect).

---

### 📶 Gradual Depth — Four Levels

**Level 1:** When one change requires editing many files, something is wrong. The fix is usually to find the one place this concept should live and put it there.

**Level 2:** Look for: "every time we add a new field to X, we touch 10 files" or "adding a new payment method requires editing 8 classes." This pattern indicates the concept (field lifecycle, payment processing) is not encapsulated. Consolidate: find the class most responsible for the concept and move the scattered pieces there.

**Level 3:** Shotgun Surgery has two forms: **Data dispersion** (same data structure scattered across DTOs, entities, mappers — solved by code generation or a mapper class) and **Behaviour dispersion** (same logic pattern in many methods — solved by Extract Method + delegation, or AOP for cross-cutting concerns). Detecting it: git blame + search for "same change touches N files in N commits" or use code change coupling analysis tools (CodeScene identifies "change coupling" — files that always change together).

**Level 4:** Shotgun Surgery and Divergent Change are opposite manifestations of the same underlying disease: **poor cohesion**. Divergent Change = one class, too many reasons to change (high internal dispersion of concerns). Shotgun Surgery = one reason to change, too many classes affected (high external dispersion of responsibility). Both are violations of SRP, but in different directions. The cure is the same: identify the concept's natural home and consolidate. The smell pair is used in architecture reviews: if Divergent Change is present, split the class; if Shotgun Surgery is present, consolidate scattered classes.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────┐
│  SHOTGUN SURGERY PATTERN                           │
├────────────────────────────────────────────────────┤
│                                                    │
│  Change: "add rate limiting to all API methods"    │
│                                                    │
│  WITHOUT CENTRALISATION:                           │
│  UserController:    add rate limit check           │
│  OrderController:   add rate limit check           │
│  PaymentController: add rate limit check           │
│  ProductController: add rate limit check           │
│  SearchController:  add rate limit check           │
│  ... (12 more controllers)                         │
│  → 17 files changed, miss 2 → security gap       │
│                                                    │
│  WITH AOP CENTRALISATION:                          │
│  @Around("execution(* *Controller.*(..))")         │
│  → apply rate limiting automatically               │
│  → 1 file changed, 0 missed, complete coverage    │
└────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW (consolidated):**
```
Requirement: "add new payment method"
  → PaymentMethodRegistry: add new provider class
  → PaymentMethodFactory: add case (or strategy pattern)
  → That's it — 2 changes [← YOU ARE HERE]
  → All existing payment flows pick up new method
    via strategy pattern / factory
```

**FAILURE PATH (shotgun surgery):**
```
Requirement: "add new payment method"
  → PaymentService.java: add case
  → CheckoutController.java: add case
  → RefundService.java: add case
  → ReportingService.java: add case
  → AdminController.java: add case
  → ReconciliationJob.java: missed!
  → Production: refunds fail for new payment type
  → Bug: missing sixth location
```

---

### 💻 Code Example

```java
// SMELL: Adding "audit" requires touching every service
public class OrderService {
    public Order create(Order order) {
        Order saved = repo.save(order);
        auditLog.record("CREATE", "ORDER", saved.getId()); // inline!
        return saved;
    }
}
public class PaymentService {
    public Payment process(Payment payment) {
        Payment processed = process(payment);
        auditLog.record("PROCESS", "PAYMENT", processed.getId()); // inline!
        return processed;
    }
}
// Every new service needs manual audit logging

// REFACTORED: Centralise with AOP
@Aspect
@Component
public class AuditAspect {
    @Around("@annotation(Audited)")
    public Object audit(ProceedingJoinPoint pjp) throws Throwable {
        Object result = pjp.proceed();
        auditLog.record(
            pjp.getSignature().getName(),
            pjp.getTarget().getClass().getSimpleName(),
            extractId(result));
        return result;
    }
}

// Now every method just needs @Audited — no inline code
public class OrderService {
    @Audited
    public Order create(Order order) {
        return repo.save(order); // clean; audit is automatic
    }
}
```

---

### ⚖️ Comparison Table

| Smell | Description | Direction | Remedy |
|---|---|---|---|
| **Shotgun Surgery** | 1 change → N files | Responsibility too dispersed | Consolidate into 1 class/aspect |
| Divergent Change | 1 class → N reasons to change | Concerns too concentrated | Split class by reason |
| Duplicate Code | Same logic in multiple places | Logic not extracted | Extract Method |
| Feature Envy | Method uses another's data | Misplaced behaviour | Move Method |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Many files changed = shotgun surgery | Large features legitimately touch many files. Shotgun Surgery is when ONE LOGICAL CHANGE requires MANY small edits. A feature that adds a new screen, new service, and new database table legitimately touches many files — that's a feature, not a smell. |
| Shotgun Surgery is always fixed by AOP | AOP solves the cross-cutting concern case. Shotgun Surgery from data dispersion (same fields in Entity, DTO, Mapper, Repository) is solved by code generation or better abstraction, not AOP. |

---

### 🚨 Failure Modes & Diagnosis

**1. Missing One of the Scattered Changes**

**Symptom:** Feature ships. One code path behaves differently from others — the one where the developer missed the update.

**Root Cause:** Shotgun Surgery's inherent partial-update risk.

**Diagnostic:**
```bash
# Find code patterns that should all have same structure
# e.g., all controllers should have @RateLimited
grep -r "@Controller" src/ | while read file; do
    grep -L "@RateLimited" "$file" && echo "MISSING: $file"
done
```

**Prevention:** Consolidate the concept first; then any controller missing it is a compile-time failure, not a runtime miss.

---

### 🔗 Related Keywords

**Prerequisites:** `Code Smell`, `Divergent Change`
**Builds On This:** `Technical Debt`, AOP, Strategy Pattern
**Alternatives / Comparisons:** `Divergent Change` — opposite concentration/dispersion problem

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ One logical change → many scattered edits │
│              │ across many different classes             │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Missing one of N edits leaves system in   │
│ SOLVES       │ inconsistent state — inevitable at scale  │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ If N classes change for one reason, the   │
│              │ reason's code belongs in one class        │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ "This change required editing 8 files"    │
│              │ should trigger consolidation              │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Changes that legitimately touch many      │
│              │ layers (features crossing multiple    domains)│
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ One-place change safety vs. architectural │
│              │ restructuring needed to consolidate       │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Phone book in 7 directories: update in   │
│              │  all or someone finds the old entry."     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Divergent Change → AOP → Strategy Pattern │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A payment system requires that every financial transaction be logged to a compliance audit trail. Currently this is implemented inline in every service method that touches money. There are 80 such methods across 20 service classes. You are evaluating two approaches: (A) AOP-based audit logging via `@FinancialOperation` annotation + aspect, (B) explicit audit service injection + manual `auditService.logTransaction()` in every method. What are the specific failure modes and testing challenges of each? Under what circumstances would you prefer (B) over (A)?

**Q2.** Shotgun Surgery and Divergent Change are complementary bad smells. A codebase analysis shows: `OrderService` has Divergent Change (changes for 6 different reasons), and adding a new "order type" causes Shotgun Surgery (6 files change). How do these two smells relate to each other in this scenario? Design the specific refactoring sequence that eliminates both simultaneously.

