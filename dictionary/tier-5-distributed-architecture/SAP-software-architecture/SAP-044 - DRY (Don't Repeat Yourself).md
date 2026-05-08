---
layout: default
title: "DRY (Don't Repeat Yourself)"
parent: "Software Architecture Patterns"
grand_parent: "Technical Dictionary"
nav_order: 44
permalink: /software-architecture/dry/
id: SAP-044
category: Software Architecture Patterns
difficulty: ★☆☆
depends_on: Functions, Abstraction, Refactoring
used_by: All development, Code review, Refactoring decisions
related: SOLID Principles, KISS, YAGNI, Abstraction, Copy-Paste Programming
tags:
  - architecture
  - principles
  - beginner
  - design
---

# SAP-044 - DRY (Don't Repeat Yourself)

⚡ TL;DR - DRY states that every piece of knowledge must have a single, authoritative representation in a system - not that all similar-looking code must be deduplicated, but that business logic, rules, and facts must not exist in multiple places that can drift out of sync.

---

### 📊 Entry Metadata

| #757            | Category: Software Architecture Patterns                           | Difficulty: ★☆☆ |
| :-------------- | :----------------------------------------------------------------- | :-------------- |
| **Depends on:** | Functions, Abstraction, Refactoring                                |                 |
| **Used by:**    | All development, Code review, Refactoring decisions                |                 |
| **Related:**    | SOLID Principles, KISS, YAGNI, Abstraction, Copy-Paste Programming |                 |

---

### 🔥 The Problem This Solves

**THE COPY-PASTE PROBLEM:**
The validation rule "email must contain exactly one @" appears in: the registration form, the profile update form, the admin user creation page, and the email change workflow. Four places. When a new rule is added ("email must not exceed 254 characters"), it must be updated in all four places. One is missed. Production bugs. This is DRY violation.

**THE DRY SOLUTION:**
One `EmailValidator` class with one authoritative implementation of email validation rules. All four places use this one class. When the rule changes, one change, zero missed locations, zero inconsistencies.

---

### 📘 Textbook Definition

DRY - Don't Repeat Yourself - is a principle introduced by Andrew Hunt and David Thomas in "The Pragmatic Programmer" (1999): _"Every piece of knowledge must have a single, unambiguous, authoritative representation within a system."_ The key word is _knowledge_ - not _code_. DRY is about avoiding the duplication of business rules, domain logic, and facts. DRY does not mean never write code that looks similar to other code - two pieces of similar-looking code that represent different business concepts should NOT be merged just because they currently look alike. That would be accidental coupling, not DRY compliance.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Every business rule exists in one place. When it changes, you change one thing in one location.

**One analogy:**

> A company's employee vacation policy is in the HR handbook (one authoritative source). All managers refer to the handbook. When the policy changes, the handbook is updated, and all managers immediately have the new rule. If instead each manager kept their own handwritten copy of the policy, when it changes some managers would have the old version. Same-looking text in different places; different facts over time.

**One insight:**
DRY is not about syntactic code deduplication. Two functions that look alike but represent different business concepts should remain separate. The question is not "does this code look like other code?" but "are these two pieces of code the authoritative representation of the same fact?"

---

### 🔩 First Principles Explanation

**DRY VIOLATION CATEGORIES:**

```
┌──────────────────────────────────────────────────────────┐
│         DRY VIOLATION - THREE CATEGORIES                 │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  1. Code duplication (the obvious type):                 │
│     Same logic copy-pasted in multiple places            │
│     Example: validation rules in controller AND service  │
│     Fix: extract to shared method/class                  │
│                                                          │
│  2. Data duplication (structural):                       │
│     Same data stored in multiple tables/fields           │
│     Example: customer.fullName AND                       │
│     customer.firstName + " " + customer.lastName         │
│     Fix: derive fullName; store only first/last          │
│                                                          │
│  3. Knowledge duplication (most important):              │
│     Same business rule expressed in multiple places      │
│     (even with different code structure)                 │
│     Example: "orders over £100 get free shipping"        │
│     hardcoded in: checkout service, email templates,     │
│     promotional copy generator, and invoice generator    │
│     Fix: single ShippingPolicy class/constant/config     │
└──────────────────────────────────────────────────────────┘
```

**THE WET ANTI-PATTERN:**

```
┌──────────────────────────────────────────────────────────┐
│         WET CODE - "Write Everything Twice"              │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  WET violation: Business logic in multiple layers        │
│                                                          │
│  Controller:                                             │
│    if (order.total > 100) freeShipping = true;           │
│                                                          │
│  Service:                                                │
│    if (cartTotal >= 100.00) applyFreeShipping();         │
│                                                          │
│  Email template:                                         │
│    {% if order.total > 100 %}FREE SHIPPING{% endif %}    │
│                                                          │
│  Rule changed to £150 → must find and update 3 places   │
│  Likely: one place is missed. Inconsistency. Bug.        │
│                                                          │
│  DRY fix:                                                │
│  ShippingPolicy.FREE_SHIPPING_THRESHOLD = 100;           │
│  ShippingPolicy.qualifiesForFree(order) → boolean        │
│  All three places use ShippingPolicy - one source        │
└──────────────────────────────────────────────────────────┘
```

---

### 🧪 Thought Experiment

**THE DANGEROUS MISAPPLICATION:**
You have two functions:

```java
// Creates a user account
void registerUser(String name, String email) {
    validate(name, email);
    User user = new User(name, email);
    userRepo.save(user);
    emailService.sendWelcome(email);
}

// Creates a system service account
void createServiceAccount(String name, String email) {
    validate(name, email);
    ServiceAccount acct = new ServiceAccount(name, email);
    serviceAccountRepo.save(acct);
    // no welcome email for service accounts
}
```

These look similar. A developer decides to DRY them into one method. But they represent DIFFERENT business concepts: user registration and service account creation have different lifecycle rules, audit requirements, and feature flags. Merging them couples two distinct business concepts. Now when user registration changes (add phone verification), the merge accidentally affects service accounts. This is the **DRY misapplication** - unifying code that is coincidentally similar but conceptually distinct.

---

### 🧠 Mental Model / Analogy

> DRY is like a single source of truth for a news story. A journalist writes the article once and it's published. When new facts emerge, the article is updated once, and all readers see the new version. If instead the article existed as different versions in ten different newspapers, updating the facts requires tracking down and updating every copy - and readers with old copies have the wrong information. DRY is having one newspaper, not ten.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone):**
Don't have the same business rule written in multiple places. If it's in one place, when it changes you update one thing. If it's in ten places, when it changes nine of them might stay wrong.

**Level 2 - How to apply it (junior):**
When you find yourself copy-pasting code: stop. Extract the common logic into a function, class, or constant. The caller sites call the extracted method. The logic lives in exactly one place. Key targets: validation rules, business calculations (tax rates, thresholds), configuration values (URLs, limits, timeouts), and formatting logic (date formats, number formats).

**Level 3 - DRY vs code clarity (mid-level):**
The "Rule of Three": tolerate one duplication, refactor when you see three occurrences of the same logic. This guards against premature abstraction. Two similar-looking pieces of code may diverge in the future - premature extraction forces them together. Three occurrences strongly suggest a genuine common concept worth extracting. Also: comments are a DRY violation of code intent. Code that needs a comment to explain what it does can often be refactored so the code is self-explanatory, eliminating the comment-code synchronization risk.

**Level 4 - Systemic DRY (senior/staff):**
At system scale, DRY means single source of truth for: data (normalized schema vs denormalized duplicates in different services), configuration (single config service vs each service hardcoding values), and documentation (code generates documentation - OpenAPI from annotations - vs hand-maintained duplicate docs). Microservices create DRY challenges: when services need the same business logic, should they share a library (DRY via library) or each have their own copy (independent evolution)? The answer depends on whether it's genuinely the same business rule (DRY: share the library) or the same code coincidentally (YAGNI: don't prematurely couple services).

---

### ⚙️ How It Works (Mechanism)

**DRY at different abstraction levels:**

```
┌──────────────────────────────────────────────────────────┐
│         DRY - ABSTRACTION LEVELS                         │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Function level:                                         │
│    Extract repeated logic into a private method          │
│    All callers call the one method                       │
│                                                          │
│  Class level:                                            │
│    Extract domain concept into a class                   │
│    (EmailValidator, ShippingPolicy, TaxCalculator)       │
│                                                          │
│  Module level:                                           │
│    Extract shared library (shared validation JAR)        │
│    Multiple services depend on the library               │
│                                                          │
│  System level:                                           │
│    Single config service, schema registry, API catalog   │
│    All systems read from authoritative source            │
│                                                          │
│  Choose level based on who needs to share the knowledge  │
└──────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture

**Refactoring to DRY:**

```
┌──────────────────────────────────────────────────────────┐
│      BEFORE DRY: Knowledge in 3 places                   │
├──────────────────────────────────────────────────────────┤
│  CartService:    if (total > 100) freeShipping = true    │
│  PromoEngine:    if (cartTotal >= 100) addFreeShipping() │
│  InvoiceGen:     if (amount > 100.0) discount shipping   │
│                                                          │
│      AFTER DRY: Knowledge in 1 place                     │
├──────────────────────────────────────────────────────────┤
│  class ShippingPolicy {                                  │
│    static final BigDecimal FREE_THRESHOLD =              │
│      new BigDecimal("100.00");                           │
│    static boolean qualifiesForFree(BigDecimal total) {   │
│      return total.compareTo(FREE_THRESHOLD) >= 0;        │
│    }                                                     │
│  }                                                       │
│                                                          │
│  CartService:   ShippingPolicy.qualifiesForFree(total)   │
│  PromoEngine:   ShippingPolicy.qualifiesForFree(total)   │
│  InvoiceGen:    ShippingPolicy.qualifiesForFree(total)   │
│                                                          │
│  Rule changes → 1 place to update. Always correct.       │
└──────────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

```java
// BEFORE: DRY violation - same validation in two places
public class RegistrationController {
    public ResponseEntity<?> register(RegistrationRequest req) {
        // Validation logic duplicated here
        if (req.email() == null ||
                !req.email().contains("@")) {
            return badRequest("invalid email");
        }
        if (req.password().length() < 8) {
            return badRequest("password too short");
        }
        // ... register user
    }
}

public class ProfileController {
    public ResponseEntity<?> updateEmail(
            UpdateEmailRequest req) {
        // Same validation logic - copy-pasted
        if (req.email() == null ||
                !req.email().contains("@")) {
            return badRequest("invalid email");
        }
        // ... update email
    }
}

// AFTER: DRY - validation in one place
public class UserInputValidator {
    public void validateEmail(String email) {
        if (email == null || !email.contains("@")) {
            throw new InvalidEmailException(email);
        }
        if (email.length() > 254) {
            throw new InvalidEmailException(
                "email exceeds 254 chars");
        }
    }

    public void validatePassword(String password) {
        if (password.length() < 8) {
            throw new WeakPasswordException();
        }
    }
}

// Both controllers inject and use the validator
// Validation rule changes → one class to update
```

---

### ⚖️ Comparison Table

| Approach                  | Duplication  | Change effort   | Coupling risk                 |
| ------------------------- | ------------ | --------------- | ----------------------------- |
| **DRY (extracted logic)** | None         | Change 1 place  | May couple unrelated concepts |
| WET (copy-paste)          | High         | Change N places | None (isolated copies)        |
| "Rule of Three"           | Tolerates 2x | Refactor at 3x  | Balanced                      |

---

### ⚠️ Common Misconceptions

| Misconception                           | Reality                                                                                                                        |
| --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| DRY means no duplicate lines of code    | DRY means no duplicate knowledge; similar-looking code representing different concepts should stay separate                    |
| Always extract when code looks the same | Only extract if it represents the same concept; premature extraction creates accidental coupling                               |
| DRY applies only to code                | DRY applies to data (normalization), documentation (generated from code), and configuration (single source)                    |
| Violating DRY is always wrong           | Sometimes temporary duplication is acceptable - when concepts might diverge, when sharing would introduce problematic coupling |

---

### 🚨 Failure Modes & Diagnosis

**WET (Write Everything Twice) drift**

**Symptom:** Bug fixed in one place reappears from a different copy. Behavior inconsistent across features using same business rule.

**Root Cause:** Business logic copied-pasted instead of extracted.

**Diagnosis:**

```bash
# Find potential WET violations via git history
git log --all --diff-filter=A -- "*.java" |
  grep "copy\|duplicate\|same as"
# Or search for similar blocks
grep -rn "total > 100" src/
# If found in 3+ files: DRY violation candidate
```

---

### 🔗 Related Keywords

**Prerequisites:**

- `Functions` - the most basic DRY tool (extract to function)
- `Abstraction` - creating the right boundary to extract into

**Related:**

- `YAGNI` - don't add code you don't need; DRY says don't repeat the code you have
- `KISS` - simplicity and DRY often reinforce each other

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ DEFINITION   │ Single, authoritative representation     │
│              │ for every piece of knowledge             │
├──────────────┼───────────────────────────────────────────┤
│ KEY WORD     │ KNOWLEDGE - not code lines               │
├──────────────┼───────────────────────────────────────────┤
│ WHEN TO DRY  │ Same business rule in 2+ places          │
├──────────────┼───────────────────────────────────────────┤
│ WHEN NOT TO  │ Similar code = different concepts        │
│              │ (coincidental similarity)                │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "One newspaper, not ten - one update,    │
│              │  everyone has the correct version"        │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You have two microservices: `OrderService` and `InvoiceService`. Both need to calculate VAT. The calculation is identical: `amount * 0.20`. Should you extract this into a shared library that both services depend on, or keep it duplicated in each service? What factors determine the right answer, and what are the risks of each approach?

**Q2.** Your codebase has a `Customer` class with `firstName`, `lastName`, and `fullName` (stored as a separate column, always equals `firstName + " " + lastName`). Identify the DRY violation. How do you fix it at the code level, and separately, how do you fix it at the database level? Are there any cases where keeping `fullName` stored (not derived) might be acceptable - and why?
