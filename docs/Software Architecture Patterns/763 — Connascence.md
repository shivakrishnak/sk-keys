---
layout: default
title: "Connascence"
parent: "Software Architecture Patterns"
nav_order: 763
permalink: /software-architecture/connascence/
number: "763"
category: Software Architecture Patterns
difficulty: ★★★
depends_on: "Cohesion and Coupling, Law of Demeter, SOLID Principles"
used_by: "Architecture review, Code quality, Refactoring, Software design"
tags: #advanced, #architecture, #coupling, #design, #refactoring
---

# 763 — Connascence

`#advanced` `#architecture` `#coupling` `#design` `#refactoring`

⚡ TL;DR — **Connascence** is a taxonomy of coupling types that classifies HOW two components are coupled and HOW STRONGLY — providing a precise vocabulary for discussing coupling beyond just "tight" or "loose," from the weakest (name) to the strongest (identity) connascence.

| #763 | Category: Software Architecture Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Cohesion and Coupling, Law of Demeter, SOLID Principles | |
| **Used by:** | Architecture review, Code quality, Refactoring, Software design | |

---

### 📘 Textbook Definition

**Connascence** (Meilir Page-Jones, "What Every Programmer Should Know About Object-Oriented Design," 1992; refined by Jim Weirich): a metric of coupling between two software components describing the kind of change that would need to be made to both if either is changed. Two components are connascent if a change to one would require a change to the other to preserve correctness. Connascence is characterized by: **type** (what they share), **degree** (how many elements are coupled), and **locality** (how close they are — connascence within a module is acceptable; across modules is a concern). Forms range from weak (Connascence of Name — easiest to refactor) to strong (Connascence of Identity — hardest). The taxonomy gives developers precise language to discuss and reason about coupling quality.

---

### 🟢 Simple Definition (Easy)

Two gears in a clock. If you change one gear's tooth count: you must also change its partner gear's tooth count — or the clock breaks. The gears are "connascent" — they share knowledge about each other (tooth count). Some forms of connascence are easy to fix (rename one: rename the other). Some are hard (change the interface contract: many callers must update). Connascence gives you a vocabulary to say precisely WHAT kind of coupling exists and how bad it is.

---

### 🔵 Simple Definition (Elaborated)

Two classes are connected in different ways: they both know a method is named `getOrder` (weak — rename refactoring tool fixes it); they both depend on the ORDER of parameters in a method (stronger — change order, must fix all callers); they both depend on the same numerical constant `0.10` for a discount rate (strong — change the rate, find all uses); they both hold a reference to the SAME object instance (strongest — they share mutable state). Connascence names these precisely: Name, Position, Value, Identity. Weaker = better. Refactoring: move from strong to weak connascence.

---

### 🔩 First Principles Explanation

**The full connascence taxonomy:**

```
CONNASCENCE TAXONOMY (weakest → strongest):

STATIC CONNASCENCE (detectable at compile/analysis time — generally safer):

  1. CONNASCENCE OF NAME (CoN) — weakest:
  
     Two components agree on the NAME of an entity.
     
     class Order {
         String getOrderNumber() { ... }  // defines name
     }
     class OrderPrinter {
         String num = order.getOrderNumber();  // uses same name
     }
     
     Change getName → getOrderId: update all callers.
     ✓ IDEs and compilers detect this. Refactoring tools can auto-fix.
     ✓ The weakest connascence. Acceptable everywhere.
     
  2. CONNASCENCE OF TYPE (CoT):
  
     Two components agree on the TYPE of an entity.
     
     void process(Order order) { ... }  // expects Order type
     process(new Order(...));           // caller provides Order type
     
     If Order becomes OrderV2: update all method signatures + callers.
     ✓ Type systems and compilers detect/enforce this.
     
  3. CONNASCENCE OF MEANING (CoM) / CONVENTION:
  
     Two components agree on the MEANING of values.
     
     // "1" means active, "0" means inactive — but where is this documented?
     if (user.getStatus() == 1) { ... }  // caller knows "1" means active
     void setStatus(int status) { ... }  // setter accepts any int
     
     Change meaning of "1": find every place that uses this value.
     ✗ No type system enforcement. Subtle bugs.
     Fix: use named enum (User.Status.ACTIVE) → reduces to CoN.
     
  4. CONNASCENCE OF POSITION (CoP):
  
     Two components agree on the POSITION of values.
     
     // Method expects (firstName, lastName) — positional:
     void createUser(String first, String last) { ... }
     createUser("John", "Doe");  // caller must know ORDER of params
     
     Swap parameters in signature: all callers break silently (String, String — type safe but wrong).
     ✗ Type systems can't detect order swap for same-type params.
     Fix: named parameters (record/builder pattern) → reduces to CoN.
     
     createUser(new UserName(first: "John", last: "Doe"));
     
  5. CONNASCENCE OF ALGORITHM (CoA):
  
     Two components must use the SAME algorithm.
     
     // Password hashing: client hashes with SHA-256, server validates SHA-256.
     // Both must agree on: algorithm, salt strategy, encoding.
     
     class PasswordHasher {
         String hash(String pw) { return sha256(salt + pw); }
     }
     class PasswordValidator {
         boolean validate(String pw, String hash) {
             return sha256(salt + pw).equals(hash);  // SAME algorithm
         }
     }
     
     Change hashing algorithm: must update BOTH. Missed one: auth breaks.
     Fix: encapsulate algorithm in single class; both use it (→ CoN).

DYNAMIC CONNASCENCE (detectable only at runtime — generally dangerous):

  6. CONNASCENCE OF EXECUTION ORDER (CoO):
  
     Two components must be called in a specific ORDER to work correctly.
     
     init();           // MUST be called before
     process(data);    // this
     cleanup();        // MUST be called after process
     
     // If cleanup() called before process(): state corruption.
     // If init() omitted: NullPointerException.
     
     ✗ Compiler cannot enforce order. Fragile API.
     Fix: template method or builder that enforces order structurally.
     
  7. CONNASCENCE OF TIMING (CoTm):
  
     Two components must happen within a certain TIME WINDOW.
     
     // Race condition: both threads must read BEFORE either writes.
     // Or: request must arrive within 30-second session timeout.
     
     ✗ Hardest to detect. Timing-dependent bugs are intermittent.
     
  8. CONNASCENCE OF VALUE (CoV):
  
     Multiple components share a VALUE that must stay consistent.
     
     // ORDER_LIMIT = 100 defined in 3 places:
     class OrderValidator { static final int MAX = 100; }
     class CartCalculator  { static final int MAX = 100; }
     class BatchProcessor  { static final int LIMIT = 100; }
     
     Change limit to 150: find all 3. Miss one: inconsistent behavior.
     ✗ DRY violation. Fix: single constant in one place (→ CoN for consumers).
     
  9. CONNASCENCE OF IDENTITY (CoI) — strongest:
  
     Two components reference the SAME OBJECT INSTANCE (shared mutable state).
     
     List<Order> orders = new ArrayList<>();
     serviceA.setOrders(orders);  // serviceA holds reference
     serviceB.setOrders(orders);  // serviceB holds SAME reference!
     
     serviceA.add(new Order());   // modifies shared list
     // serviceB.orders now contains the new Order — surprise!
     
     ✗ Any mutation through one reference: invisible side effect through the other.
     Fix: defensive copies; immutable collections; avoid shared mutable state.
     
CONNASCENCE STRENGTH × LOCALITY:

  KEY INSIGHT: Connascence strength matters relative to LOCALITY.
  
  Strong connascence WITHIN a method/class: acceptable.
    Method calling its own private methods: any form of connascence is fine.
    
  Strong connascence ACROSS module/package boundaries: BAD.
    Two microservices with Connascence of Value (shared magic constants): very bad.
    
  REFACTORING DIRECTION:
  
    Goal: move from strong connascence to weak connascence.
    Or: move strong connascence INWARD (within a single module where it's safer).
    
    CoValue across services: move constant to shared library (→ CoName for consumers).
    CoPosition in public API: introduce named parameter object (→ CoName).
    CoIdentity: introduce immutable value objects or defensive copies (→ CoName).
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT connascence vocabulary:
- "This code is tightly coupled" — what does that mean? Can't target the fix
- "We have coupling" — which kind? Name? Value? Identity? Each requires different fix

WITH connascence vocabulary:
→ "These services have Connascence of Value on the order limit constant — extract to shared config"
→ Precise diagnosis → precise fix → measurable improvement

---

### 🧠 Mental Model / Analogy

> Radio stations and radios. Both must be "connascent" on frequency: the station broadcasts at 98.5 FM, your radio tunes to 98.5 FM. This is Connascence of Value — they share the value 98.5. If the station changes to 99.1: you must change your radio (re-tune). AM/FM format is Connascence of Type — both must agree on the modulation protocol. "Name" connascence: the station has a call sign (KXYZ) — if the name changes, your presets break. Each connascence type describes a DIFFERENT kind of coordination required.

"Both must agree on frequency 98.5" = Connascence of Value (shared constant)
"Both must use FM modulation" = Connascence of Type (protocol agreement)
"Station call sign in presets" = Connascence of Name (naming agreement)
"Change one: must update the other" = the definition of connascence itself

---

### ⚙️ How It Works (Mechanism)

```
REFACTORING CONNASCENCE:

  DIAGNOSE:
    CoIdentity (shared mutable object)
    → Most dangerous. Affects runtime state.
    
  REDUCE:
    Replace shared mutable state with immutable values or copies.
    CoIdentity → CoName (they both reference by name, not same instance)
    
  LOCALIZE:
    Can't eliminate CoAlgorithm between hasher and validator?
    Move BOTH into one class. CoAlgorithm is now INTRA-class (acceptable).
    
  WEAKEN:
    CoPosition (param order): introduce request object → CoName.
    CoMeaning (magic int): introduce enum → CoName.
    CoValue (constant in 3 places): extract to single constant → CoName for all consumers.
```

---

### 🔄 How It Connects (Mini-Map)

```
Coupling between components (various types and strengths)
        │
        ▼ (classify and measure coupling precisely)
Connascence ◄──── (you are here)
(taxonomy: what kind of coupling, how strong, how to fix)
        │
        ├── Cohesion and Coupling: connascence gives coupling a precise vocabulary
        ├── Law of Demeter: LoD violations are often CoIdentity or CoPosition connascence
        ├── DRY Principle: CoValue violations are often DRY violations (constant in N places)
        └── Refactoring: moving from strong connascence to weak is a refactoring goal
```

---

### 💻 Code Example

```java
// CONNASCENCE OF POSITION (weak but fixable):
// Caller must know ORDER of params — same type, easy to mix up:
void createUser(String firstName, String lastName, String email) { ... }

createUser("Smith", "John", "john@example.com"); // WRONG order! Both Strings. Compiles.

// FIX: Replace with named parameter object (reduces to CoName):
record UserRegistration(String firstName, String lastName, String email) {}
void createUser(UserRegistration reg) { ... }
createUser(new UserRegistration("John", "Smith", "john@example.com")); // Named, explicit.

// ────────────────────────────────────────────────────────────────────

// CONNASCENCE OF VALUE (strong — DRY violation):
class OrderValidator {
    private static final int MAX_ITEMS = 50; // defined here
    boolean validate(Order o) { return o.items().size() <= MAX_ITEMS; }
}
class CartUI {
    private static final int MAX_ITEMS = 50; // SAME value, different place
    void showWarning(Cart c) { if (c.size() >= MAX_ITEMS) warn("Cart nearly full"); }
}
class BatchImporter {
    private static final int ORDER_LIMIT = 50; // SAME value, yet another place
}

// Change to 100 items: must find all 3. Miss one: inconsistency.

// FIX: single source of truth (reduces to CoName):
public final class OrderConstraints {
    public static final int MAX_ITEMS_PER_ORDER = 50;
    private OrderConstraints() {}
}
// All three classes use OrderConstraints.MAX_ITEMS_PER_ORDER — CoName only.
// Change: one place. Done.
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Connascence and coupling are the same thing | Connascence is a taxonomy OF coupling. It gives coupling precision and vocabulary. "Coupling" is the general concept; connascence provides the specific vocabulary to say what KIND of coupling exists, how strong it is, and how to fix it. It makes coupling a measurable, discussable, refineable concern |
| Stronger connascence is always bad | Connascence strength matters relative to LOCALITY. Strong connascence within a single class or method is acceptable — that's just internal implementation. The concern is strong connascence across module or service boundaries, where it impacts team autonomy, deployment independence, and change cascade. Strengthen it (localize it within a class); don't eliminate all coupling |
| Connascence only applies to code within a service | Connascence applies at all levels: class-to-class, module-to-module, service-to-service. Microservices with a shared database have Connascence of Value (same schema). Services sharing event schemas have Connascence of Type. Distributed connascence is generally the most dangerous form — it crosses team and deployment boundaries |

---

### 🔥 Pitfalls in Production

**Connascence of Execution Order in an SDK API:**

```java
// ANTI-PATTERN: Connascence of Execution Order (users must call in right sequence):
class EmailBuilder {
    void setSubject(String s) { this.subject = s; }    // must be called
    void setBody(String b) { this.body = b; }           // must be called
    void addRecipient(String r) { this.recipients.add(r); }
    Email build() {
        // NPE if setSubject/setBody were not called:
        return new Email(subject.toUpperCase(), body, recipients);
    }
}

// User forgets setSubject(): NullPointerException at build() time.
// Order dependency: setSubject before build. No compile-time enforcement.

// FIX: Constructor forces required dependencies (eliminates CoO):
record Email(String subject, String body, List<String> recipients) {
    Email {  // compact constructor validates:
        Objects.requireNonNull(subject, "subject required");
        Objects.requireNonNull(body, "body required");
        if (recipients.isEmpty()) throw new IllegalArgumentException("At least one recipient");
    }
}
// Or: builder pattern with compile-time-enforced required fields using type state.
// Required params: constructor. Optional params: builder methods.
// No "must call in order" — required params structurally enforced.
```

---

### 🔗 Related Keywords

- `Cohesion and Coupling` — connascence is a precise vocabulary for coupling analysis
- `DRY Principle` — Connascence of Value violations are typically DRY violations
- `Law of Demeter` — LoD violations create Connascence of Position/Identity
- `Refactoring` — moving from strong to weak connascence is the refactoring direction
- `API Design` — Connascence of Position (parameter order) is a key API design concern

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Taxonomy of coupling types from weakest   │
│              │ (Name) to strongest (Identity). Name the │
│              │ connascence to target the right fix.     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Architecture review; discussing coupling; │
│              │ justifying refactoring priority; designing│
│              │ public APIs and inter-service contracts  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Don't force the vocabulary into every    │
│              │ code review — use when precision about   │
│              │ coupling type genuinely adds value       │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Radio and station: both tuned to 98.5 —  │
│              │  Connascence of Value. Change frequency:  │
│              │  both must update or no signal."          │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Cohesion and Coupling → DRY Principle →   │
│              │ Refactoring → API Design                 │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Two microservices: Order Service and Shipping Service both check `if (orderStatus == 2)` meaning "ready for shipping" — a magic number hardcoded in both. Identify the connascence type. What's the risk if the Order team changes what status code 2 means? Propose a fix that reduces this to Connascence of Name. Does the fix require a shared library, or can it be handled with a Published Language (event schema)?

**Q2.** REST APIs often have Connascence of Position in their JSON payloads (field order, parameter order). When a REST API evolves from `POST /orders` accepting `{customerId, items, shippingAddress}` to adding an optional `promoCode` field — which connascence type is this? Is it a forward/backward compatibility break? Contrast this with adding a required `deliveryDate` field — which connascence type changes, and why is it a breaking change?
