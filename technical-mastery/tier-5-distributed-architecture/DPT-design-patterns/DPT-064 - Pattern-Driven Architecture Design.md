---
id: DPT-064
title: Pattern-Driven Architecture Design
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★★★
depends_on: DPT-001, DPT-061, DPT-063
used_by: DPT-065
related: DPT-061, DPT-065, DPT-052, DPT-054
tags:
  - concept
  - architecture
  - advanced
  - system-design
  - distributed-systems
  - decision-making
status: complete
version: 4
layout: default
parent: "Design Patterns"
grand_parent: "Technical Mastery"
nav_order: 64
permalink: /technical-mastery/design-patterns/pattern-driven-architecture-design/
---

⚡ TL;DR - Pattern-driven architecture uses design patterns
as named, communicable building blocks for expressing
architectural decisions - transforming architecture from
informal diagrams to explicit, validated design choices
with known trade-offs.

| #64 | Category: Design Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | DPT-001, DPT-061, DPT-063 | |
| **Used by:** | DPT-065 | |
| **Related:** | DPT-061, DPT-065, DPT-052, DPT-054 | |

---

### 🔥 The Problem This Solves

**THE INFORMAL ARCHITECTURE PROBLEM:**
A team designs a system. They draw boxes and arrows.
Each box represents a service or module. Each arrow
represents some kind of communication. The diagram shows
WHAT the system looks like. It does NOT say:
- Why was this service boundary chosen?
- Why is this communication synchronous vs asynchronous?
- What happens when service B is unavailable?
- How is consistency maintained across this boundary?

**THE CONSEQUENCE:**
The architecture is a black box. New team members cannot
understand the decisions. When the system fails at a
boundary: the team cannot diagnose it because the design
intent was never explicit. When requirements change: the
team does not know which patterns to change vs preserve.

**THE SHIFT:**
Pattern-driven architecture: every significant structural
decision is expressed as a named pattern. "Service A
and Service B are connected by the Outbox Pattern (DPT-053)
because we need exactly-once delivery with at-least-once
semantics." This single sentence communicates the design
intent, the delivery guarantee, and the failure mode.

---

### 📘 Textbook Definition

**Pattern-Driven Architecture Design** is an approach
to system architecture where structural and behavioral
decisions are expressed using named patterns from a
shared vocabulary. The architect identifies the architectural
tensions (the competing forces at the system boundary level)
and selects patterns that resolve each tension. The resulting
architecture is documented as a set of named patterns
with explicit trade-off justifications.

**Three levels of pattern-driven architecture:**
1. **Module level**: GoF patterns (Singleton, Factory,
   Strategy, Observer) - design decisions within a module.
2. **Service level**: Architectural patterns (CQRS, Outbox,
   Saga, Repository) - design decisions within a service.
3. **System level**: Distributed patterns (Circuit Breaker,
   Bulkhead, Sidecar, Strangler Fig) - design decisions
   across service boundaries and infrastructure.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Architecture = a set of named pattern decisions with
explicit trade-offs, not a diagram of boxes and arrows.

**One analogy:**
> Architecture blueprint vs construction plan.
> A blueprint shows the final structure.
> A construction plan shows: which TECHNIQUES are used,
> WHY (load-bearing wall requires steel beam, not wood),
> and what CONSTRAINTS apply (earthquake zone requires
> reinforced foundation).
>
> Pattern-driven architecture = the construction plan.
> "This service uses CQRS because it has 100x more reads
> than writes and we need independent scaling."
> That sentence is more valuable than an arrow from
> "API" to "database" in a box diagram.

---

### 🔩 First Principles Explanation

**THE PATTERN VOCABULARY AS ARCHITECTURE LANGUAGE:**
A shared pattern vocabulary lets a team communicate
complex architectural decisions in one word:
- "We use the Saga Pattern here" → implies: distributed
  transaction, compensating transactions, eventual consistency,
  orchestrated or choreographed steps, failure handling.
- "The reads go through a CQRS read model" → implies:
  denormalized view, eventual consistency acceptable,
  read optimized, possibly cached.
- "The async communication uses the Outbox Pattern" →
  implies: transactional guarantees, at-least-once delivery,
  message relay process, database-level atomicity.

Without this vocabulary: these same concepts require
paragraphs of prose to explain, and the explanation
may still be ambiguous.

**ARCHITECTURAL TENSION TYPES:**

At the system level, the common tensions are:

| Tension | Pattern Candidates |
|---|---|
| Distributed consistency | Saga, Outbox, 2PC, eventual consistency |
| Read/write scaling | CQRS, read replicas, cache |
| Service failure isolation | Circuit Breaker, Bulkhead, Retry |
| Legacy migration | Strangler Fig, Anti-Corruption Layer |
| Cross-cutting concerns | Sidecar, Ambassador |
| Service discovery | Service Locator, service mesh |

---

### 🧪 Thought Experiment

**ARCHITECTURE REVIEW: PATTERN VS NON-PATTERN DOCUMENTATION**

**Non-pattern architecture document:**
> "When an order is placed, the Order Service writes to
> the database and sends a message to the Payment Service.
> The Inventory Service is notified. If payment fails,
> the order is cancelled."

Questions this leaves unanswered:
- Is the message sent before or after the DB write?
- What if the message send fails? Is the DB rolled back?
- What delivery guarantee does the message have?
- How is the order cancellation guaranteed to succeed?

**Pattern-driven architecture document:**
> "Order placement uses the Outbox Pattern (atomic DB write
> + message relay). Payment processing uses the Saga Pattern
> (choreography-based, compensating transaction on failure).
> Payment Service is protected by a Circuit Breaker (50%
> failure rate threshold, 30s wait). Inventory notification
> is eventually consistent (Observer via event bus, no
> compensation required)."

Every sentence communicates: the structural decision,
the delivery guarantee, and the failure handling approach.
No questions remain about consistency or failure modes.

---

### 🧠 Mental Model / Analogy

> Pattern-driven architecture = the "music notation" model.
> A musician who hears a chord can write it as: "the bass
> player plays G, the pianist plays G-B-D in the right hand,
> the guitarist plays the same chord voicing..."
> OR they write: "G major chord."
>
> "G major chord" = the pattern name. Both descriptions
> convey the same information; the pattern name is faster,
> less ambiguous, and requires no translation for musicians.
>
> Architecture patterns are the "G major chord" of system
> design. "Uses the Outbox Pattern" = precise, shared,
> unambiguous for engineers who know the vocabulary.
> The alternative = many paragraphs of ambiguous prose.

---

### 📶 Gradual Depth - Three Levels

**Level 1 - Naming patterns in existing systems:**
Even without introducing new patterns, name the patterns
already present in the codebase: "This is a Repository
Pattern," "This is a Circuit Breaker," "This is an Outbox."
Naming existing patterns immediately improves communication.

**Level 2 - Pattern selection at architecture design time:**
When designing a new service boundary: identify the
tension first (delivery guarantee, consistency model,
failure isolation), select candidate patterns, evaluate
trade-offs, document the decision.

**Level 3 - Architecture Decision Records (ADR) as pattern decisions:**
Formalize pattern choices as ADRs: "ADR-007: Use Saga
Pattern for Order Processing. Context: need distributed
consistency across Order, Payment, and Inventory.
Decision: Choreography-based Saga with compensating
transactions. Consequences: eventual consistency in read
model, no 2-phase commit, retry events required."
The ADR is the pattern decision made explicit, reviewable,
and reversible.

---

### ⚙️ How It Works (Mechanism)

```
Pattern-Driven Architecture Process
┌─────────────────────────────────────────────────────────┐
│ 1. IDENTIFY ARCHITECTURAL TENSION                       │
│    "We need atomic order creation + payment call.       │
│     Two services, two databases."                       │
│                                                         │
│ 2. CLASSIFY TENSION TYPE                               │
│    Distributed consistency:                            │
│    atomic write + async notification across services   │
│                                                         │
│ 3. LIST CANDIDATE PATTERNS                             │
│    2-Phase Commit (2PC) / Saga / Outbox               │
│                                                         │
│ 4. EVALUATE TRADE-OFFS IN CONTEXT                      │
│    2PC: synchronous, tight coupling, XA transactions   │
│      → rejected (service coupling, performance)        │
│    Saga: distributed transactions, compensation        │
│      → viable for multi-step flows                     │
│    Outbox: atomic local write + async relay            │
│      → best for write + notify pattern                 │
│                                                         │
│ 5. DOCUMENT THE DECISION (ADR)                         │
│    "Use Outbox Pattern for order→payment notification. │
│     Consequence: at-least-once delivery, relay process. │
│     Trade-off: delayed notification (< 1s typical),    │
│     accepted for this use case."                       │
└─────────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Architecture decision as named patterns:**

```
SYSTEM: E-commerce order processing platform
SERVICES: OrderService, PaymentService, InventoryService,
          NotificationService

ARCHITECTURAL DECISIONS (pattern-driven):

1. ORDER CREATION → PAYMENT NOTIFICATION:
   Pattern: Outbox (DPT-053)
   Tension: atomic DB write + guaranteed delivery to
     payment service
   Trade-off: at-least-once delivery, relay process
     overhead
   Rejected: direct HTTP call (tight coupling, failure mode
     is silent data loss)

2. ORDER → PAYMENT → INVENTORY SAGA:
   Pattern: Saga / Choreography (DPT-054)
   Tension: multi-service transaction atomicity
   Trade-off: eventual consistency in read model,
     compensating transactions needed
   Rejected: 2PC (XA transaction coupling)

3. PAYMENT SERVICE FAILURE HANDLING:
   Pattern: Circuit Breaker (DPT-057) + Bulkhead (DPT-056)
   Tension: payment service downtime → order service
     downtime
   Trade-off: degraded order flow when payment is down
     (orders accepted, payment deferred)
   Rejected: no isolation (payment downtime = order
     downtime)

4. READ MODEL FOR ORDERS:
   Pattern: CQRS (DPT-052)
   Tension: 100x more reads than writes;
     different query patterns for different consumers
   Trade-off: eventual consistency in read model (< 500ms)
   Rejected: single model (complex queries on write model)

5. CROSS-CUTTING OBSERVABILITY:
   Pattern: Sidecar (DPT-058)
   Tension: distributed tracing, metrics collection across
     all services (polyglot: Java + Python + Node.js)
   Trade-off: Envoy sidecar overhead (~1ms per hop, ~100MB)
   Rejected: per-language SDK (100 services × SDK update
     cost)
```

---

### ⚖️ Pattern Decisions at Architecture Level

| Architectural Challenge | Pattern | Key Trade-off |
|---|---|---|
| Distributed consistency | Saga, Outbox | Eventual consistency vs strong consistency |
| Read/write scaling | CQRS | Read model staleness vs query flexibility |
| Failure isolation | Circuit Breaker, Bulkhead | Fast failure vs delayed notification |
| Legacy migration | Strangler Fig | Incremental vs big-bang migration risk |
| Cross-cutting concerns | Sidecar, Ambassador | Container overhead vs code coupling |
| Event ordering | Outbox, Event Sourcing | Ordering guarantee vs throughput |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Patterns are only for code, not architecture | Patterns exist at every level: code (GoF), service (Repository, CQRS), system (Circuit Breaker, Saga, Sidecar). Architectural patterns are as well-defined as code patterns |
| Using patterns makes the design rigid | Named patterns make the design EXPLICIT, not rigid. Explicit decisions are easier to change than implicit ones: "We chose Outbox here because of delivery guarantee. If we move to Kafka, the Outbox is replaced by Kafka's delivery guarantee." Clear decision → clear change path |
| Pattern-driven design requires all patterns to be applied upfront | Patterns are applied as tensions arise, not upfront. "You Aren't Gonna Need It" (YAGNI) applies to patterns too. Apply the simplest design; add patterns when the specific tension appears |
| Architecture documentation is for stakeholders, not engineers | Architecture documentation expressed as named patterns is the most useful for engineers: it communicates design intent, failure modes, and trade-offs in a dense, precise vocabulary |

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ APPROACH     │ Every significant structural decision =  │
│              │ named pattern + explicit trade-off       │
├──────────────┼──────────────────────────────────────────┤
│ VOCABULARY   │ Module (GoF) / Service (CQRS, Repo) /    │
│              │ System (CB, Bulkhead, Sidecar, Saga)     │
├──────────────┼──────────────────────────────────────────┤
│ PROCESS      │ Tension → candidates → evaluate →        │
│              │ decide → document (ADR)                  │
├──────────────┼──────────────────────────────────────────┤
│ VALUE        │ Names = precise communication.           │
│              │ "Outbox Pattern" = more than paragraphs  │
│              │ of prose about consistency guarantees    │
├──────────────┼──────────────────────────────────────────┤
│ ANTI-PATTERN │ Boxes-and-arrows without named patterns  │
│              │ = undocumented implicit decisions        │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ DPT-065: Patterns in Distributed Systems │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Patterns provide a vocabulary for architecture decisions.
   "Uses the Outbox Pattern" conveys more precisely than
   3 paragraphs of prose about delivery guarantees and
   atomicity. The shared vocabulary reduces communication overhead.
2. Three levels of patterns: module (GoF), service (CQRS,
   Repository), system (Circuit Breaker, Saga, Sidecar).
   Apply patterns at the appropriate level for the tension.
3. Architecture Decision Records (ADRs) formalize pattern
   choices: context (the tension), decision (the pattern),
   trade-offs (what is gained and sacrificed), alternatives
   rejected (and why). Named patterns make ADRs precise.

