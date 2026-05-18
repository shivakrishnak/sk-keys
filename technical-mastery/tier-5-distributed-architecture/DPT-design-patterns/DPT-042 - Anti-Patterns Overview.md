---
id: DPT-042
title: Anti-Patterns Overview
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★★☆
depends_on: DPT-001, DPT-003, DPT-005
used_by: DPT-043, DPT-044, DPT-045, DPT-046, DPT-047,
  DPT-048, DPT-049, DPT-050, DPT-051, DPT-064, DPT-081,
  DPT-082, DPT-083
related: DPT-003, DPT-043, DPT-044, DPT-045, DPT-063
tags:
  - concept
  - anti-patterns
  - intermediate
  - code-quality
  - refactoring
  - technical-debt
status: complete
version: 4
layout: default
parent: "Design Patterns"
grand_parent: "Technical Mastery"
nav_order: 42
permalink: /technical-mastery/design-patterns/anti-patterns-overview/
---

⚡ TL;DR - Anti-patterns are recurring solutions that seem
reasonable, are widely used, but consistently produce
bad outcomes - they are documented to be recognized and
avoided, not just to catalog bad code.

| #42 | Category: Design Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | DPT-001, DPT-003, DPT-005 | |
| **Used by:** | DPT-043 through DPT-051, DPT-064, DPT-081-DPT-083 | |
| **Related:** | DPT-003, DPT-043, DPT-044, DPT-045, DPT-063 | |

---

### 🔥 Why Anti-Patterns Matter

Patterns tell you what WORKS. Anti-patterns tell you what
LOOKS LIKE IT WORKS but consistently fails.

The danger of anti-patterns: they are not obviously bad.
If they were obviously bad, experienced developers would
not use them. They appear reasonable, sometimes even
elegant, in small systems. They become destructive at
scale, over time, or as systems grow.

**The billion-dollar mistakes are not random bugs - they
are systematic application of anti-patterns by experienced
developers who did not recognize them as anti-patterns.**

---

### 📘 Definition

An **anti-pattern** is a commonly used approach to a
recurring problem that appears to be an appropriate solution
but actually produces bad results. The key characteristics:
1. It is a RECURRING practice (not an accidental mistake).
2. It appears PLAUSIBLE or beneficial on the surface.
3. It consistently produces BAD OUTCOMES.
4. It has been DOCUMENTED so it can be named and recognized.

The term was coined by Andrew Koenig (1995) and popularized
by the book "AntiPatterns" (Brown, Malveau, McCormick,
Mowbray, 1998).

**Anti-pattern vs bug:** a bug is an accidental mistake.
An anti-pattern is a deliberate design choice that is
systematically wrong.

**Anti-pattern vs pattern:** a pattern is a recurring
GOOD solution. An anti-pattern is a recurring BAD solution.
Both are documented precisely because they recur.

---

### ⏱️ Anti-Pattern Taxonomy

**CATEGORIES:**

**Development Anti-Patterns** (bad coding practices):
- God Object - one class that does everything
- Spaghetti Code - tangled, unstructured code
- Copy-Paste Programming - duplication by copying
- Magic Numbers - hard-coded unexplained values
- Lava Flow - dead code that cannot safely be removed
- Boat Anchor - unused code kept "just in case"

**Architecture Anti-Patterns** (bad structural decisions):
- Golden Hammer - applying one solution to every problem
- Cargo Cult Programming - following practices without understanding
- Premature Optimization - optimizing before measuring

**Project Management Anti-Patterns** (process failures):
- Analysis Paralysis, Death March, Feature Creep
(outside scope of this dictionary's focus)

**Code Smell Indicators:**
- Shotgun Surgery - one change requires many small edits
- Feature Envy - a method more interested in another class's data
- Circular Dependencies - modules that depend on each other cyclically

---

### 🔩 The Three-Part Anti-Pattern Structure

Every well-documented anti-pattern has three parts:

**1. The Problem Context:**
What circumstance makes this anti-pattern tempting?
Example (God Object): "System grows quickly; one team owns
all the business logic; it's faster to add to the existing
class than to design a new one."

**2. The Anti-Pattern Solution:**
What does the bad solution look like?
Example: One `OrderManager` class with 5,000 lines handling
orders, customers, inventory, invoicing, and shipping.

**3. The Refactored Solution:**
What is the correct approach?
Example: Separate `OrderService`, `CustomerService`,
`InventoryService`, `InvoiceService`, `ShippingService`
with single responsibilities.

---

### 🧠 How to Recognize an Anti-Pattern in Production

**THE KEY QUESTION:** Is a recurring practice causing
consistent pain - hard to change, hard to test, hard
to debug, hard to extend?

**INDICATORS:**
- "We're afraid to change that class"
  → God Object, Lava Flow, or Spaghetti Code
- "We have to change 20 files every time we add a feature"
  → Shotgun Surgery or tight coupling
- "This worked in the prototype but is causing issues now"
  → premature shortcut that is now technical debt
- "I don't know why this configuration is here but removing
  it breaks everything"
  → Lava Flow
- "We always use [technology X] regardless of the problem"
  → Golden Hammer

**THE NAMING POWER:**
Naming an anti-pattern is a communication tool. "This
module has a God Object problem" communicates more
precisely than "this module is messy." Named anti-patterns
allow teams to have specific conversations about technical
debt rather than vague ones.

---

### 📶 Anti-Patterns vs Technical Debt

Technical debt is the cost of past shortcuts. Anti-patterns
are how that debt is accumulated.

Not all technical debt comes from anti-patterns:
- Deliberate debt: "We'll clean this up after launch"
  (conscious choice).
- Accidental debt: "We didn't know about this anti-pattern
  when we wrote it."

The cost of anti-patterns grows non-linearly:
- Small codebase: God Object manageable (one developer
  can hold it all in their head).
- Medium codebase: God Object slows development (merge
  conflicts, hard-to-test code).
- Large codebase: God Object creates complete development
  gridlock (changes risky, refactoring impossible without
  full system knowledge).

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What they are (anyone can understand):**
Anti-patterns are bad habits in programming that look
reasonable but cause problems. The important thing is
they are documented so you can recognize and name them.
"That's a God Object" is more useful than "that class
is too big."

**Level 2 - How to use this knowledge (junior developer):**
Learn the names. When reviewing code or receiving a PR,
if you see: one class with 20+ methods spanning multiple
concerns (God Object), or code copied in 3 places
(Copy-Paste Programming), name it. Use the anti-pattern
name in your review comment. Learn the refactoring.

**Level 3 - How anti-patterns emerge (mid-level engineer):**
Most anti-patterns emerge from correct practices applied
past their useful boundary:
- Singleton (correct for truly unique resources) → God Object
  (singleton holding all state)
- DRY ("don't repeat yourself") → over-abstraction
  (abstract everything, even things that coincidentally
  look similar)
- "Get it working first" → Lava Flow (dead code that
  cannot be removed)
- "Reuse existing infrastructure" → Golden Hammer
  (using a database where a message queue is needed)

**Level 4 - Anti-pattern roots in organizational structure (senior/staff):**
Conway's Law: "Organizations which design systems are
constrained to produce designs which are copies of the
communication structures of those organizations."
Many anti-patterns have organizational causes:
- God Object: happens when one team owns "the system"
  and has no clear domain boundaries.
- Shotgun Surgery: happens when a concern is split across
  multiple teams with no coordination mechanism.
- Golden Hammer: happens when a team has deep expertise
  in one technology and applies it universally.
Technical solutions (modularization, domain separation)
must address the organizational root cause or the anti-pattern
will re-emerge.

**Level 5 - Anti-patterns as institutional memory (distinguished engineer):**
The value of naming anti-patterns is not just individual
code quality - it is collective knowledge transfer.
When a new engineer joins a team and hears "we had a God
Object problem in the order module, which is why we split
it into these five services," they gain years of
institutional learning in one sentence. Anti-pattern
names are a shared vocabulary for technical debt discussions
with stakeholders. "We accumulated a significant Lava Flow
in the authentication module" is a statement a CTO and
a developer can both understand and reason about (scope,
risk, refactoring cost). This is the meta-value of the
anti-pattern documentation project: it creates a shared
technical vocabulary across experience levels.

---

### ⚙️ How It Works (Mechanism)

```
Anti-Pattern Recognition Framework
┌─────────────────────────────────────────────────────────┐
│                                                         │
│ SYMPTOM OBSERVED:                                       │
│   "Changing feature X requires touching 15 files"       │
│                                                         │
│ PATTERN MATCH:                                          │
│   → Shotgun Surgery (anti-pattern)                      │
│   → or Circular Dependencies (anti-pattern)             │
│   → or God Object (all change requests go through       │
│      the same mega-class)                               │
│                                                         │
│ ROOT CAUSE:                                             │
│   → Responsibility leakage (code in wrong layers)       │
│   → Missing domain boundary (no clear ownership)        │
│   → Copy-paste instead of abstraction                   │
│                                                         │
│ REFACTORED SOLUTION:                                    │
│   → Identify cohesive groups of related functions       │
│   → Extract to separate classes/services                │
│   → Apply appropriate design pattern (SRP, etc.)        │
└─────────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Anti-pattern identification grid:**

```java
// RECOGNIZING ANTI-PATTERNS IN CODE

// GOD OBJECT INDICATOR:
class OrderManager {         // 5000 lines
    void processOrder() {}   // order processing
    void sendEmail() {}      // notification
    void updateInventory() {}// inventory
    void generateInvoice() {}// billing
    void scheduleShipping() {}// logistics
    void applyDiscount() {}  // pricing
    void validateCustomer() {}// customer mgmt
    // Doing everything: SRP violated massively
}

// SPAGHETTI CODE INDICATOR:
void processUserInput(String input, int flag) {
    if (flag == 1) {
        if (input.contains("X")) {
            for (int i = 0; i < input.length(); i++) {
                if (input.charAt(i) == 'Y') {
                    // 50 more lines of nested conditions
                }
            }
        } else {
            // duplicate path...
        }
    } else if (flag == 2) {
        // completely different logic...
    }
}
// No structure, no names, no abstraction

// MAGIC NUMBERS INDICATOR:
double price = basePrice * 1.23;        // what is 1.23?
if (retries > 3) { ... }                // why 3?
Thread.sleep(500);                      // why 500ms?
```

**Example 2 - Refactored versions:**

```java
// REFACTORED: God Object → Single Responsibility

@Service class OrderService     { void processOrder(Order o) {} }
@Service class NotificationSvc { void sendConfirmation(Order o) {} }
@Service class InventoryService { void reduceStock(Order o) {} }
@Service class InvoiceService   { void generateInvoice(Order o) {} }
@Service class ShippingService  { void scheduleDelivery(Order o) {} }

// REFACTORED: Magic Numbers → named constants
private static final double TAX_RATE = 0.23; // 23% VAT
private static final int MAX_RETRY_ATTEMPTS = 3;
private static final long RETRY_DELAY_MS = 500;

double price = basePrice * TAX_RATE;
if (retries > MAX_RETRY_ATTEMPTS) { ... }
Thread.sleep(RETRY_DELAY_MS);
```

---

### ⚖️ Most Common Anti-Patterns Quick Reference

| Anti-Pattern | Core Symptom | Root Cause | DPT Entry |
|---|---|---|---|
| God Object | 1 class does everything | Missing SRP | DPT-043 |
| Spaghetti Code | Untraceable control flow | No structure | DPT-044 |
| Golden Hammer | One tech for every problem | Expertise bias | DPT-045 |
| Cargo Cult | Copying practices without understanding | No first principles | DPT-046 |
| Premature Optimization | Optimizing unmeasured code | Fear without data | DPT-047 |
| Magic Numbers | Unexplained numeric/string literals | Laziness/haste | DPT-048 |
| Lava Flow | Dead code that cannot be removed | Fear of deletion | DPT-049 |
| Copy-Paste Programming | Duplicated logic blocks | "Faster to copy" | DPT-050 |
| Boat Anchor | Unused code kept "just in case" | YAGNI violation | DPT-051 |
| Shotgun Surgery | One change hits N files | Missing abstraction | DPT-081 |
| Feature Envy | Method obsesses over other class's data | Wrong location | DPT-082 |
| Circular Dependencies | Module A depends on B, B on A | Missing layering | DPT-083 |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Anti-patterns are just bad code | Anti-patterns are bad PRACTICES that look reasonable. Many anti-patterns are written by experienced developers who were trying to do the right thing in the short term |
| Naming an anti-pattern solves the problem | Naming creates shared understanding of the problem. Solving requires refactoring, which takes time and risk. Naming is the first step; refactoring is the work |
| Anti-patterns always require immediate refactoring | Technical debt (anti-patterns included) should be prioritized against feature work. Not all anti-patterns are equally costly. A God Object in rarely-touched legacy code may cost less to maintain than to refactor |
| "Clean code" is the absence of all anti-patterns | Pragmatic clean code means no anti-patterns in the hot path, critical modules, or frequently changed code. Perfect elimination of all anti-patterns in all legacy code is usually not worth the risk/cost |

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Recurring practice that looks reasonable │
│              │ but consistently produces bad outcomes   │
├──────────────┼──────────────────────────────────────────┤
│ THREE PARTS  │ 1. Problem context (why it's tempting)   │
│              │ 2. Bad solution (what it looks like)     │
│              │ 3. Refactored solution (what to do)      │
├──────────────┼──────────────────────────────────────────┤
│ KEY VALUE    │ Naming creates shared vocabulary for     │
│              │ technical debt discussions               │
├──────────────┼──────────────────────────────────────────┤
│ RECOGNITION  │ Pain signals: "afraid to change it",    │
│              │ "N files for every feature", "mystery"  │
├──────────────┼──────────────────────────────────────────┤
│ NEXT ENTRIES │ DPT-043: God Object                      │
│              │ DPT-044: Spaghetti Code                  │
│              │ DPT-045: Golden Hammer                   │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Anti-patterns are NOT random bugs - they are recurring
   practices that look reasonable but consistently fail.
   The documentation purpose: give them names so teams
   can recognize and discuss them.
2. Most anti-patterns emerge from good practices applied
   past their boundary: Singleton → God Object; DRY →
   over-abstraction; "get it working" → Lava Flow.
3. The value of anti-pattern vocabulary is communication:
   "we have a God Object problem in the order module"
   conveys scope, risk, and refactoring approach in one
   phrase that everyone on the team understands.

