---
id: DPT-061
title: Pattern Selection Framework
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★★★
depends_on: DPT-001, DPT-004, DPT-005
used_by: DPT-064, DPT-070
related: DPT-004, DPT-042, DPT-005, DPT-070
tags:
  - concept
  - framework
  - advanced
  - decision-making
  - software-design
  - architectural-thinking
status: complete
version: 4
layout: default
parent: "Design Patterns"
grand_parent: "Technical Mastery"
nav_order: 61
permalink: /technical-mastery/design-patterns/pattern-selection-framework/
---

⚡ TL;DR - Pattern selection is not memorization - it is
a diagnostic process: identify the design tension, map
it to pattern forces, evaluate cost of each alternative,
and choose the pattern whose forces best match your
specific constraints.

| #61 | Category: Design Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | DPT-001, DPT-004, DPT-005 | |
| **Used by:** | DPT-064, DPT-070 | |
| **Related:** | DPT-004, DPT-042, DPT-005, DPT-070 | |

---

### 🔥 The Problem This Solves

**WHY PATTERN SELECTION FAILS:**
Engineers know 20 patterns. A problem arrives. They pick
the pattern whose NAME sounds closest to the problem.
Result: wrong pattern applied. Structural pattern used
for a behavioral problem. Creational pattern used for
a structural problem. The pattern adds complexity without
solving the real tension.

**THE SYMPTOM:**
"We applied the Decorator Pattern" but now the code is
harder to read than before. "We used the Observer Pattern"
but now the system has memory leaks and unexpected
coupling. The patterns are correct in principle but
wrong for the specific context.

**THE ROOT CAUSE:**
Patterns are selected by name/surface recognition, not
by problem structure. The pattern's NAME is not its
definition. Its FORCES are its definition. Matching
forces to problem structure: correct pattern selection.

---

### 📘 Textbook Definition

A **Pattern Selection Framework** is a systematic
decision process for choosing a design pattern based
on: (1) identifying the design tension (the competing
forces in the problem), (2) mapping the tension to
the pattern vocabulary (which patterns resolve which
tensions), and (3) evaluating trade-offs in the specific
context (constraints, scale, team familiarity).

**The four-step pattern selection process:**
1. **Name the tension**: What are the two forces pulling
   against each other? (flexibility vs simplicity, isolation
   vs coupling, control vs performance)
2. **List candidate patterns**: Which patterns resolve
   this type of tension?
3. **Evaluate in context**: What are the costs of each?
   What are your specific constraints?
4. **Apply and validate**: Apply the chosen pattern.
   Verify that the tension is resolved. Verify no new
   tensions are introduced.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Choose patterns by matching problem FORCES (the tensions),
not by matching problem NAMES to pattern NAMES.

**One analogy:**
> A doctor prescribing medication. The patient says:
> "I have pain." If the doctor prescribes based only
> on "pain" → any pain medication → wrong.
> A good doctor asks: WHERE is the pain? WHAT TYPE?
> WHAT CAUSES IT? These questions identify the forces
> (inflammation vs nerve vs structural). The specific
> diagnosis → the correct treatment.
>
> Pattern selection: identify the design "diagnosis"
> (the specific forces), not just the surface symptom
> (the feature name).

**One insight:**
Every design pattern resolves a specific tension.
Recognizing which tension you have is harder than
knowing the patterns themselves. Most pattern mistakes
are misdiagnosed tensions, not unknown patterns.

---

### 🔩 First Principles Explanation

**FORCES IN PATTERN DOCUMENTATION:**
Every original GoF pattern description includes "Forces" -
the competing design pressures the pattern resolves.
These forces are more important than the pattern name.
When you recognize the forces in your problem: you have
identified the correct pattern, regardless of whether
you remember its name.

**THE TENSION TAXONOMY:**
Most design tensions fall into a small set of categories:

1. **Variability tension**: "I need this behavior to change
   without modifying this class."
   → Patterns: Strategy, Template Method, State, Command
   → Choice driver: is the variability algorithm-level
   (Strategy), structure-level (Template), state-level (State)?

2. **Coupling tension**: "I need A to notify B without
   A knowing about B."
   → Patterns: Observer, Event Bus, Mediator
   → Choice driver: is it one-to-many (Observer), many-to-many
   (Mediator), or asynchronous decoupled (Event Bus)?

3. **Complexity hiding tension**: "I need to hide the
   complexity of a subsystem from its clients."
   → Patterns: Facade, Adapter, Proxy
   → Choice driver: hide subsystem (Facade), adapt interface
   (Adapter), or control access (Proxy)?

4. **Object creation tension**: "I need to decouple object
   creation from object use."
   → Patterns: Factory Method, Abstract Factory, Builder, Prototype
   → Choice driver: single type (Factory Method), families (Abstract
   Factory), step-by-step construction (Builder)?

5. **Resource management tension**: "I need to control
   how many instances exist and how they are shared."
   → Patterns: Singleton, Object Pool, Flyweight
   → Choice driver: one instance (Singleton), bounded pool
   (Pool), shared state (Flyweight)?

---

### 🧪 Thought Experiment

**SAME SYMPTOM, DIFFERENT FORCES:**

**Problem A**: "I need to add logging to my service methods."
Tension: extend behavior without modifying the class.
Forces: Add behavior dynamically, keep single responsibility.
→ Decorator Pattern.

**Problem B**: "I need to add logging, metrics, and auth
checking to all service methods."
Tension: Apply cross-cutting concerns to many methods.
Forces: Apply uniformly, don't repeat in every method.
→ Aspect-Oriented Programming (Proxy-based in Spring)
→ NOT Decorator (Decorator requires explicit wrapping per class)

**Problem C**: "I need to log when a state changes in
my domain object and notify 10 different handlers."
Tension: Notify dependents when object state changes.
Forces: One-to-many notification, loose coupling.
→ Observer Pattern.

Same surface symptom ("I need to add logging").
Three different tensions. Three different patterns.
The pattern selection framework reveals which is correct.

---

### 🧠 Mental Model / Analogy

> Pattern Selection Framework = "triage" model.
> A hospital emergency room triages patients by symptoms
> into categories: cardiac, trauma, respiratory, neurological.
> Each category routes to a different specialist and treatment.
>
> Design pattern triage: categorize the design tension
> into a tension type (variability, coupling, complexity,
> creation, resource). Each tension type has a pattern
> family. Within the family: choose the specific pattern
> that matches the specific sub-forces.
>
> "What is the tension type?" is the triage question.
> Without triage: all symptoms look like they need
> the same treatment ("just use a pattern").

---

### 📶 Gradual Depth - Three Levels

**Level 1 - Simple heuristics:**
Ask two questions: "What is the problem with the current
design?" and "What do I want to be able to change independently?"
The answer often points directly to a pattern family.

**Level 2 - Forces matching:**
Write down the two or three forces in the tension. Compare
them to the forces listed in the pattern documentation.
The pattern whose forces match your forces most closely
is the candidate. Evaluate cost.

**Level 3 - Architectural tension mapping:**
For system-level problems, map the tension to ARCHITECTURAL
patterns: Saga (distributed transaction atomicity), CQRS
(read/write optimization), Strangler Fig (incremental
migration). These tensions operate at the service boundary
level, not the class level. The selection criteria include:
team topology, data ownership, deployment constraints.

---

### ⚙️ How It Works (Mechanism)

```
Pattern Selection Decision Flow
┌─────────────────────────────────────────────────────────┐
│ STEP 1: Identify the tension                            │
│   "What is hard to change?" / "What is coupled          │
│    that should be decoupled?"                           │
│             │                                           │
│             ▼                                           │
│ STEP 2: Classify the tension type                       │
│   Variability? Coupling? Complexity? Creation?          │
│   Resource? Concurrency? Distribution?                  │
│             │                                           │
│             ▼                                           │
│ STEP 3: List candidate patterns for the tension type    │
│   (Pattern family for this tension)                     │
│             │                                           │
│             ▼                                           │
│ STEP 4: Evaluate in your context                        │
│   - Team familiarity with each candidate                │
│   - Complexity cost of each candidate                   │
│   - Runtime cost of each candidate                      │
│   - Future change scenarios: which pattern enables them?│
│             │                                           │
│             ▼                                           │
│ STEP 5: Apply + Validate                               │
│   Apply the pattern. Does it resolve the tension?       │
│   Does it introduce a new tension? If yes: reconsider.  │
└─────────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Pattern selection in practice:**

```
PROBLEM: A notification service must send emails.
         New requirement: also send SMS.
         Future: possibly push notifications, Slack.

STEP 1 - Identify tension:
  "I want to add new notification channels without
   modifying the NotificationService class."

STEP 2 - Classify:
  Variability tension: behavior should vary
  (which channel to use) without modifying the class.

STEP 3 - Candidates:
  Strategy Pattern: encapsulate the "how to notify"
    algorithm and make it substitutable.
  Command Pattern: encapsulate notification as an object
    (useful if notifications need to be queued/undone).
  Template Method: define the skeleton of notification
    in a base class, subclass fills in the channel.

STEP 4 - Evaluate in context:
  - No undo needed → Command overhead not justified
  - Template Method: inheritance, not composition
    (less flexible for runtime selection)
  - Strategy: runtime substitution, composition,
    multiple channels can be combined easily

STEP 5 - Decision:
  Strategy Pattern.
```

```java
// The result of correct pattern selection:
// Clean, extensible, no pattern over-engineering.

interface NotificationChannel {
    void send(Notification n);
}

class EmailChannel implements NotificationChannel {
    public void send(Notification n) { /* email logic */ }
}
class SmsChannel implements NotificationChannel {
    public void send(Notification n) { /* SMS logic */ }
}

class NotificationService {
    private final NotificationChannel channel;
    // Runtime-injected: Strategy Pattern in action
    NotificationService(NotificationChannel channel) {
        this.channel = channel;
    }
    void notify(Notification n) { channel.send(n); }
}
```

---

### ⚖️ Pattern Selection Anti-Patterns

| Anti-Pattern | Description | Correct Approach |
|---|---|---|
| Name matching | Choosing pattern by name similarity to problem | Match forces, not names |
| Resume-driven | Applying complex patterns to demonstrate skill | Use simplest pattern that resolves the tension |
| Pattern stacking | Applying multiple patterns to the same problem | One tension = one pattern. Multiple patterns = multiple tensions |
| Premature abstraction | Applying patterns before the variation actually exists | Apply when the tension is present, not anticipated |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Pattern selection is a memorization exercise | Pattern selection is a diagnostic exercise. Memorizing all 23 GoF patterns is less useful than deeply understanding the tension types they resolve |
| A complex problem needs a complex pattern | Pattern complexity should match tension complexity. A simple variability tension needs a simple Strategy, not an elaborate abstract factory hierarchy |
| Patterns from the GoF catalog are the only options | The GoF catalog is a vocabulary, not a complete list. Architectural patterns (Saga, CQRS, Strangler Fig), concurrency patterns (Thread Pool, Circuit Breaker), and domain patterns (Specification, Repository) are equally valid. Select from the right level |
| Once a pattern is applied, it cannot be changed | If the tension changes or grows, the pattern should evolve. Strategy → Command if the need to queue or undo operations emerges. Observer → Event Bus if the coupling grows too tight. Patterns are design decisions, not permanent structures |

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ STEP 1       │ Name the tension (what is coupled that   │
│              │ should be decoupled?)                    │
├──────────────┼──────────────────────────────────────────┤
│ STEP 2       │ Classify: variability / coupling /       │
│              │ complexity / creation / resource         │
├──────────────┼──────────────────────────────────────────┤
│ STEP 3       │ List pattern family for this tension type│
├──────────────┼──────────────────────────────────────────┤
│ STEP 4       │ Evaluate: team familiarity, complexity   │
│              │ cost, runtime cost, future change needs  │
├──────────────┼──────────────────────────────────────────┤
│ WRONG WAY    │ "This sounds like an Observer problem"   │
│              │ (name-matching, not force-matching)      │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ DPT-062: Pattern Evolution in Modern     │
│              │ Languages                                │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Match FORCES (the design tensions), not NAMES. The
   pattern name is a label; the forces are its definition.
   Identify the tension type first; candidate patterns follow.
2. Tension taxonomy: variability, coupling, complexity
   hiding, creation, resource management, concurrency,
   distribution. Each maps to a pattern family.
3. Diagnostic process: (1) name the tension, (2) classify
   type, (3) list candidates, (4) evaluate in context.
   Pattern selection = diagnosis, not memorization.

