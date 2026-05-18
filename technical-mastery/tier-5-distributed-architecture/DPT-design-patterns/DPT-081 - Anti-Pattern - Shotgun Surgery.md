---
id: DPT-081
title: "Anti-Pattern: Shotgun Surgery"
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★★☆
depends_on: DPT-001, DPT-074
used_by: []
related: DPT-074, DPT-082, DPT-083, DPT-063
tags:
  - anti-pattern
  - code-smell
  - intermediate
  - cohesion
  - refactoring
status: complete
version: 4
layout: default
parent: "Design Patterns"
grand_parent: "Technical Mastery"
nav_order: 81
permalink: /technical-mastery/design-patterns/shotgun-surgery/
---

⚡ TL;DR - Shotgun Surgery is a code smell where a single
change in behavior requires making many small changes
across many different classes or files. The opposite
of divergent change: one responsibility is scattered
across many locations instead of one change requiring
many modifications to one class.

| #81 | Category: Design Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | DPT-001, DPT-074 | |
| **Used by:** | N/A | |
| **Related:** | DPT-074, DPT-082, DPT-083, DPT-063 | |

---

### 🔥 The Problem This Solves

**THE SCATTERED RESPONSIBILITY:**
A business rule: "all prices must include VAT."
This is currently checked in:
- `OrderController.calculateTotal()`
- `InvoiceService.generateInvoice()`
- `QuoteService.calculateQuote()`
- `CartService.addItem()`
- `ReportService.salesReport()`
- `ApiController.getPriceList()`

When the VAT rate changes from 20% to 22%:
change MUST be made in 6 different files.
Miss one: inconsistency in production.

**THE CONSEQUENCE:**
Every "simple" change requires hunting through the codebase
to find ALL places where the scattered logic lives.
The developer must know in advance WHERE all the copies
are. Miss one: bug. The mental overhead of tracking
scattered logic grows with codebase size.

---

### 📘 Textbook Definition

**Shotgun Surgery** (Martin Fowler, "Refactoring", 1999)
is a code smell - the antipattern of scattered cohesion:

> "You whiff this when every time you make a kind of
> change, you have to make a lot of little changes to
> a lot of different classes."

**The naming:** Like a shotgun blast - one conceptual
change scatters modifications across many targets.

**Contrast with Divergent Change:**
- **Divergent Change**: one class changes for many different
  reasons. One CLASS, many REASONS to change.
- **Shotgun Surgery**: many classes change for one reason.
  Many CLASSES, one REASON to change.

**Root cause:** Low cohesion. A single responsibility
(VAT calculation, timestamp formatting, authorization
checking) is not encapsulated in one place. Its logic
is duplicated or scattered across many classes.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
One logical change = many file changes. The responsibility
is scattered; find and change it everywhere instead
of in one place.

**One analogy:**
> Changing the color of a car's logo.
>
> Without shotgun surgery: one design file has the logo.
> Change it once. Done.
>
> With shotgun surgery: the logo is painted by hand
> on every individual part: the hood, the doors, the
> trunk, the steering wheel, the floor mats, the manual.
> Changing the color: repaint every individual part.
> Miss the floor mats: inconsistency.
>
> The design file = a cohesive, single-responsibility class.
> The hand-painted copies = the scattered anti-pattern.

---

### 🔩 First Principles Explanation

**WHY SHOTGUN SURGERY EMERGES:**
1. **Copy-paste development**: a requirement is implemented
   in one place, then copied as "it's basically the same"
   to other places. Over time, the copies diverge.
2. **Cross-cutting concerns not extracted**: logging, security
   checks, validation, formatting logic spread across
   all classes that need them instead of being centralized.
3. **No single abstraction for the concept**: the "VAT calculation"
   is never given its own class. It is implemented inline
   wherever prices are computed.

**THE COUPLING STRUCTURE:**
In shotgun surgery: many classes are IMPLICITLY coupled
by sharing the same scattered logic. They are "coupled
by logic" (they all implement the same rule) but not
structured to reflect this coupling (they are independent
classes with no shared extraction).

**THE SOLUTION - MOVE METHOD / EXTRACT CLASS:**
Identify the scattered concept. Extract it into a single
cohesive class or function. Replace all the scattered
copies with calls to the extracted implementation.

For VAT: create `VatCalculator` with `applyVat(price)`.
All 6 classes call `vatCalculator.applyVat(price)`.
VAT rate change: edit `VatCalculator`. One file. Done.

---

### 🧪 Thought Experiment

**TIMESTAMP FORMATTING AS SHOTGUN SURGERY:**
System audit requirement: all timestamps must be in
ISO-8601 format with UTC timezone.
Current state: `new SimpleDateFormat("yyyy-MM-dd HH:mm:ss")`
appears in:
- 14 `@RestController` classes (response formatting)
- 7 service classes (log messages)
- 3 repository classes (query parameters)
- 5 report generator classes

Audit requirement update: use milliseconds precision.
Files to change: 29. Risk: miss any → inconsistent timestamps.

**After refactoring:**
```java
class AuditTimestamp {
    static String format(Instant instant) {
        return DateTimeFormatter.ISO_INSTANT.format(instant);
    }
}
```
All 29 usages replaced with `AuditTimestamp.format(instant)`.
Requirement changes: 1 file.

---

### 🧠 Mental Model / Analogy

> Shotgun Surgery = "The Update Spreadsheet" problem.
>
> A spreadsheet with a hardcoded interest rate (3.5%)
> in 47 different cells (C12, D25, F8, ...).
> Interest rate changes to 4.0%: find and update 47 cells.
> Miss one: wrong calculation somewhere in the model.
>
> The fix: put 3.5% in ONE named cell (interest_rate = B2).
> All 47 cells reference B2. Rate change: edit B2. Done.
>
> The named cell = the cohesive single-responsibility class.
> The 47 hardcoded values = the shotgun surgery anti-pattern.
> "Don't Repeat Yourself" (DRY) is the design principle
> that prevents this pattern.

---

### 📶 Gradual Depth - Three Levels

**Level 1 - Detecting shotgun surgery:**
Find it with grep/search: the same literal value or
pattern appears in many unrelated places. Common examples:
- Magic numbers (tax rates, timeout values) duplicated
- The same validation logic in many methods
- The same error handling code repeated
- The same date/format string in many classes

**Level 2 - Refactoring strategies:**
- **Extract Method**: centralize in one method, call from all sites
- **Extract Class**: create a dedicated class for the concept
  (`VatCalculator`, `DateFormatter`, `TimeoutConfig`)
- **Move Method**: move all scattered logic to the most
  appropriate class that owns the concept
- **Inline Class**: if the scatter is from a class that
  has been too fragmented

**Level 3 - Architectural shotgun surgery:**
At architecture level: cross-cutting concerns (logging,
security, caching, retry logic) scattered across services
instead of extracted to AOP aspects (Java's `@Aspect`)
or middleware. Every service manually logs, validates,
retries instead of getting it from a common mechanism.
Spring AOP (`@Around`, `@Before`) addresses cross-cutting
concerns that would otherwise cause architectural-level
shotgun surgery.

---

### ⚙️ How It Works (Mechanism)

```
Shotgun Surgery Anti-Pattern
┌─────────────────────────────────────────────────────────┐
│ SYMPTOM: "Change VAT rate"                              │
│   → edit OrderController.java    [VAT calc here]       │
│   → edit InvoiceService.java     [VAT calc here]       │
│   → edit QuoteService.java       [VAT calc here]       │
│   → edit CartService.java        [VAT calc here]       │
│   → edit ReportService.java      [VAT calc here]       │
│   → edit ApiController.java      [VAT calc here]       │
│   6 files for 1 business rule change.                  │
│   Miss 1 = bug in production.                          │
├─────────────────────────────────────────────────────────┤
│ SOLUTION: Extract + Centralize                          │
│   Create: VatCalculator.java                           │
│   All 6 classes: call VatCalculator.applyVat()         │
│   "Change VAT rate" → edit VatCalculator.java: 1 file. │
└─────────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Shotgun Surgery detection and refactoring:**

```java
// BAD: Timeout scattered across every service.
// Changing timeout requires editing every class.

class UserService {
    void fetchUser(long id) {
        HttpClient client = HttpClient.newBuilder()
            .connectTimeout(Duration.ofSeconds(5)) // duplicated
            .build();
        // ...
    }
}

class OrderService {
    void fetchOrder(long id) {
        HttpClient client = HttpClient.newBuilder()
            .connectTimeout(Duration.ofSeconds(5)) // duplicated
            .build();
        // ...
    }
}

class PaymentService {
    void processPayment(Payment p) {
        HttpClient client = HttpClient.newBuilder()
            .connectTimeout(Duration.ofSeconds(5)) // duplicated
            .build();
        // ...
    }
}
// Changing timeout to 10s: edit 3 (or 30) files.
// Adding read timeout: 30 files.
```

```java
// GOOD: Centralized configuration, injected where needed.

class HttpClientConfig {
    private static final Duration CONNECT_TIMEOUT =
        Duration.ofSeconds(5);
    private static final Duration READ_TIMEOUT =
        Duration.ofSeconds(30);

    static HttpClient buildClient() {
        return HttpClient.newBuilder()
            .connectTimeout(CONNECT_TIMEOUT)
            .build();
    }
}

class UserService {
    private final HttpClient client;
    UserService() { client = HttpClientConfig.buildClient(); }
    void fetchUser(long id) { /* uses client */ }
}

class OrderService {
    private final HttpClient client;
    OrderService() { client = HttpClientConfig.buildClient(); }
    void fetchOrder(long id) { /* uses client */ }
}
// Changing timeout: edit HttpClientConfig. 1 file.
// Adding read timeout: edit HttpClientConfig. 1 file.
```

---

### ⚖️ Shotgun Surgery vs DRY Principle

| DRY violation | Shotgun Surgery |
|---|---|
| Code duplicated in 2+ places | The specific case where duplication is scattered logic that must all change together |
| Detected by code review / static analysis | Detected when a change requires touching many files |
| Fix: extract and reuse | Fix: extract class, extract method, move method |
| Principle: Don't Repeat Yourself | Pattern: scattered responsibility |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Having the same method in multiple classes is always shotgun surgery | If the same method name has DIFFERENT appropriate implementations per class (polymorphism), this is not shotgun surgery. Shotgun surgery is when the same LOGIC is duplicated with no semantic distinction |
| Extracting to a shared class always fixes it | Over-extraction creates artificial coupling. Only extract to a shared class when the scattered code genuinely represents ONE concept that belongs together. Random utility classes that accumulate unrelated methods are their own problem |
| Shotgun surgery only happens in large codebases | It starts in small codebases too. The first "copy-paste to save time" is the seed. Each copy makes the next change more expensive |

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ DEFINITION   │ One logical change = many file changes.  │
│              │ Responsibility scattered across classes. │
├──────────────┼──────────────────────────────────────────┤
│ ROOT CAUSE   │ Low cohesion. Logic duplicated in-line  │
│              │ instead of extracted to one owner.      │
├──────────────┼──────────────────────────────────────────┤
│ DETECTION    │ grep same value/pattern across files.   │
│              │ Change request → many unrelated files.  │
├──────────────┼──────────────────────────────────────────┤
│ FIX          │ Extract Class / Extract Method.         │
│              │ All callers reference the single owner. │
├──────────────┼──────────────────────────────────────────┤
│ DRY LINK     │ Shotgun Surgery = DRY violation at scale│
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ DPT-082: Anti-Pattern - Feature Envy    │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Shotgun Surgery = one logical change scatters changes
   across many files. The responsibility is not owned
   by one class; it is duplicated everywhere it is needed.
   "Change the VAT rate in 6 places" = classic shotgun surgery.
2. Fix: give the scattered concept a home (Extract Class).
   All callers use the owner. Change the concept: one file.
   The cost of the change drops from O(N) to O(1).
3. Contrast with Divergent Change: Divergent Change = one
   class changes for many reasons (too many responsibilities
   in one class). Shotgun Surgery = many classes change
   for one reason (one responsibility in too many classes).
   DRY prevents both.

