---
id: DPT-005
title: The Design Patterns Ecosystem Map
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★☆☆
depends_on:
used_by:
related:
tags:
  - dpt
  - foundational
  - mental-model
status: complete
version: 1
layout: default
parent: "Design Patterns"
grand_parent: "Technical Dictionary"
nav_order: 5
permalink: /dpt/the-design-patterns-ecosystem-map/
---

# DPT-005 - The Design Patterns Ecosystem Map

⚡ TL;DR - The design patterns ecosystem spans five levels (architectural, design, concurrency, distributed, cloud-native) and three scopes (creational, structural, behavioural) — understanding the map lets you navigate to the right pattern tier for any design problem.

| DPT-005         | Category: Design Patterns                   | Difficulty: ★☆☆ |
| :-------------- | :------------------------------------------ | :-------------- |
| **Depends on:** | DPT-001, DPT-002, DPT-003, DPT-004          |                 |
| **Used by:**    | DPT-006, DPT-007, DPT-008, DPT-009, DPT-010 |                 |
| **Related:**    | DPT-001, DPT-002, DPT-004, DPT-061          |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Engineers know "design patterns" as a monolithic category.
They don't know that Observer (in-process OOP pattern)
is categorically different from Saga (distributed
transaction pattern). They apply OOP patterns to
distributed contexts and distributed patterns to
single-class problems. The ecosystem map provides
the orientation layer that tells you which set of
patterns to look in for a given problem.

**THE BREAKING POINT:**
An engineer tries to apply the GoF Facade pattern
to handle eventual consistency across microservices.
Facade is a structural pattern for hiding complexity
behind a single interface — it doesn't address
distributed state. The correct pattern is Saga or
CQRS. Without the ecosystem map, the engineer looks
in the wrong drawer.

**THE INVENTION MOMENT:**
Fowler's "Patterns of Enterprise Application Architecture"
(2002) and Hohpe's "Enterprise Integration Patterns"
(2004) established that patterns exist at multiple
levels. The concept of a "pattern language" (Christopher
Alexander) implies a hierarchical system where higher-level
patterns constrain and complement lower-level patterns.

**EVOLUTION:**
Cloud-native patterns (2015+): Circuit Breaker, Sidecar,
Ambassador, Bulkhead emerged for Kubernetes/microservices
contexts. AI/ML patterns (2020+): emerging for ML
pipelines, prompt engineering, RAG architectures.
The ecosystem grows as new contexts create new recurring
problems.

---

### 📘 Textbook Definition

The **design patterns ecosystem** is the complete
landscape of named, proven solutions organised by
level of abstraction (architectural, design, concurrency,
distributed, cloud-native) and scope (creational,
structural, behavioural). Each level addresses recurring
problems at a specific granularity; higher-level patterns
constrain the context within which lower-level patterns
are applied. An ecosystem map provides orientation:
given a problem, which level and scope of patterns
should be consulted?

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Patterns exist at five levels; the level is determined by the problem's granularity — architectural problems need architectural patterns, not GoF patterns.

**One analogy:**

> The patterns ecosystem is a city map organised by
> district. You don't use the neighbourhood street
> map to navigate between cities; you use the interstate
> map. Similarly: don't use an in-process OOP pattern
> to solve a cross-service distributed consistency problem.
> Navigate to the right district first.

**One insight:**
The GoF 23 patterns are the most famous but the
smallest fraction of the ecosystem. Engineers who know
only GoF are navigating with only the street-level
map. The ecosystem map shows the full territory.

---

### 🔩 First Principles Explanation

**FIVE-LEVEL ECOSYSTEM:**

```
Level 5: Cloud-Native / Infrastructure Patterns
  Sidecar, Ambassador, Adapter (container),
  Circuit Breaker, Bulkhead, Retry, Timeout,
  Service Mesh, Operator
  -> Problems: container orchestration; cloud resilience

Level 4: Distributed Systems Patterns
  Saga, CQRS, Outbox, Event Sourcing, Two-Phase Commit,
  Leader Election, Consistent Hashing
  -> Problems: cross-service consistency; distributed state

Level 3: Concurrency Patterns
  Thread Pool, Producer-Consumer, Read-Write Lock,
  Active Object, Double-Checked Locking, Reactor
  -> Problems: thread safety; parallel execution

Level 2: GoF Design Patterns (23 patterns)
  Creational: Singleton, Factory, Builder, Prototype
  Structural: Adapter, Decorator, Proxy, Facade...
  Behavioural: Observer, Strategy, Command...
  -> Problems: in-process object structure and communication

Level 1: Architectural Patterns
  Layered, Event-Driven, Hexagonal, CQRS, Microservices,
  Event Sourcing, Pipe-and-Filter
  -> Problems: system-level organisation and structure
```

**SCOPES WITHIN LEVEL 2 (GoF):**

```
Creational (HOW objects are made):
  Singleton, Factory Method, Abstract Factory,
  Builder, Prototype

Structural (HOW objects are composed):
  Adapter, Bridge, Composite, Decorator,
  Facade, Flyweight, Proxy

Behavioural (HOW objects communicate):
  Chain of Responsibility, Command, Interpreter,
  Iterator, Mediator, Memento, Observer, State,
  Strategy, Template Method, Visitor
```

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Problems at different granularities require different pattern sets; a map is needed to orient.
**Accidental:** Treating all patterns as equivalent regardless of their level and applying them interchangeably.

---

### 🧪 Thought Experiment

**SETUP:**
Apply the ecosystem map to five design problems.
For each, identify the correct level and pattern.

```
Problem 1: "How do I create a family of related
  objects without specifying their concrete classes?"
  Level: GoF (object creation problem)
  Scope: Creational
  Pattern: Abstract Factory

Problem 2: "How do I maintain data consistency
  across 5 microservices after a user action?"
  Level: Distributed Systems Patterns
  Pattern: Saga (choreography or orchestration)

Problem 3: "How do I make my service call resilient
  to downstream failures in a Kubernetes context?"
  Level: Cloud-Native Patterns
  Pattern: Circuit Breaker + Bulkhead

Problem 4: "How do I decouple my UI update logic
  from state changes in a model object?"
  Level: GoF
  Scope: Behavioural
  Pattern: Observer

Problem 5: "How do I organise my application's
  layers to separate UI from business logic?"
  Level: Architectural Patterns
  Pattern: Layered Architecture (3-tier)
```

---

### 🧠 Mental Model / Analogy

> The patterns ecosystem is a toolbox with five drawers.
> Drawer 1 (architectural): hand tools for building
> the frame. Drawer 2 (GoF): precision tools for
> in-process object structure. Drawer 3 (concurrency):
> synchronisation tools. Drawer 4 (distributed):
> tools for working across service boundaries.
> Drawer 5 (cloud-native): tools for container
> orchestration. When you need to fix a problem,
> identify which drawer it belongs in; don't use
> a precision screwdriver to drive a structural bolt.

**Element mapping:**

- Toolbox = pattern ecosystem
- Drawer = pattern level
- Tool = specific pattern
- Problem type = which drawer to open

Where this analogy breaks down: patterns at different
levels interact; an architectural choice (microservices)
creates the need for distributed patterns (Saga); the
drawers are not fully independent.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Patterns come in different varieties for different
sizes of problem. Some patterns are for organising
whole systems; some are for organising individual
classes; some are for distributed services.

**Level 2 - How to use it (junior developer):**
When you have a design problem, classify it first:
is it a single-class / object problem (GoF), a
multi-service / distributed problem (distributed
patterns), or a system-level organisation problem
(architectural)? Then look in the right set.

**Level 3 - How it works (mid-level engineer):**
Higher-level patterns constrain lower-level ones.
Microservices architecture (Level 1) requires
distributed patterns (Level 4: Saga, CQRS). A layered
architecture constrains where GoF patterns appear
(Factory in the service layer; Repository in the data
layer). Always set the architectural context first.

**Level 4 - Why it was designed this way (senior/staff):**
The pattern ecosystem reflects the evolution of
software complexity. GoF (1994) addressed OOP; enterprise
patterns (2002) addressed application integration;
distributed patterns (2010s) addressed microservices;
cloud-native patterns (2015+) addressed container
orchestration. Each level emerged when that context
became prevalent enough that recurring problems were
identifiable and nameable. The ecosystem will continue
to grow as AI/ML patterns solidify.

**Expert Thinking Cues:**

- Identify the problem level before selecting a pattern catalogue.
- Architectural patterns are constraints; GoF patterns are implementations within those constraints.
- Cloud-native patterns (Circuit Breaker, Sidecar) are often implemented by infrastructure (Istio, Envoy), not application code.

---

### ⚙️ How It Works (Mechanism)

**Ecosystem navigation decision tree:**

```
What scope is the problem?
  |
  +-- System structure / organisation
  |     -> Level 1: Architectural Patterns
  |        (Layered, Event-Driven, Hexagonal)
  |
  +-- Single service / in-process objects
  |     -> Level 2: GoF Design Patterns (23)
  |        Creational / Structural / Behavioural
  |
  +-- Thread safety / concurrent execution
  |     -> Level 3: Concurrency Patterns
  |        (Thread Pool, Producer-Consumer)
  |
  +-- Cross-service consistency / events
  |     -> Level 4: Distributed Patterns
  |        (Saga, CQRS, Outbox, Event Sourcing)
  |
  +-- Container / cloud resilience / mesh
        -> Level 5: Cloud-Native Patterns
           (Sidecar, Circuit Breaker, Bulkhead)
```

---

### 🔄 The Complete Picture - End-to-End Flow

**Using the ecosystem map to design an e-commerce checkout:**

```
Architectural decision:             <- YOU ARE HERE
  Microservices (Level 1: architectural pattern)
  |
Distributed decisions (Level 4):
  Multi-service checkout transaction
  -> Saga pattern for distributed transaction
  Order write + read separation -> CQRS
  Reliable event publishing -> Outbox Pattern
  |
Cloud-native decisions (Level 5):
  Payment service downstream failures
  -> Circuit Breaker
  Inventory service overload isolation
  -> Bulkhead
  |
In-process design (Level 2: GoF):
  Payment provider selection at runtime
  -> Strategy (PaymentProvider interface)
  Order status change notifications
  -> Observer (OrderStatusListener)
  Order object creation
  -> Builder (complex Order construction)
  |
Result: Each level's patterns address
its specific recurring problems without
crossing into other levels' territory
```

---

### ⚖️ Comparison Table

| Level         | Catalogue                   | Year      | Problem Scope     | Examples                   |
| ------------- | --------------------------- | --------- | ----------------- | -------------------------- |
| Architectural | Fowler PEAA; Buschmann POSA | 2002      | System structure  | Layered, Hexagonal         |
| GoF Design    | GoF book                    | 1994      | In-process object | Observer, Strategy         |
| Concurrency   | Java CPiA; POSA vol 2       | 2000/2006 | Thread safety     | Thread Pool, Active Object |
| Distributed   | Richardson MSP; Kleppmann   | 2015+     | Cross-service     | Saga, CQRS, Outbox         |
| Cloud-Native  | Richardson; Kubernetes docs | 2016+     | Container/mesh    | Sidecar, Circuit Breaker   |

---

### ⚠️ Common Misconceptions

| Misconception                                             | Reality                                                                                        |
| --------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| "Design patterns = GoF 23"                                | GoF is Level 2; four other levels exist                                                        |
| "Cloud-native patterns are just ops"                      | Sidecar, Circuit Breaker, Outbox have significant development implications                     |
| "Architectural patterns and design patterns are the same" | Architectural patterns organise systems; design patterns organise in-process objects           |
| "All patterns are language/framework independent"         | Cloud-native patterns (Sidecar) are Kubernetes-specific; concurrency patterns vary by language |
| "The ecosystem is complete"                               | New patterns emerge as new contexts arise (AI/ML patterns are forming now)                     |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Wrong Level Pattern for Problem**
**Symptom:** GoF Facade used to "hide" distributed consistency complexity; the system still has eventual consistency bugs.
**Root Cause:** Facade is a structural pattern for interface simplification; it does not address distributed state consistency (Level 4 problem).
**Fix:** Identify the correct level (distributed); apply Saga or CQRS for the actual consistency problem.

**Mode 2: Missing Architectural Context**
**Symptom:** GoF patterns applied inconsistently across a codebase; Observer in one layer, Strategy everywhere, no cohesion.
**Root Cause:** Level 2 patterns applied without Level 1 architectural context to constrain them.
**Fix:** Define architectural pattern (Hexagonal, Layered) first; apply GoF patterns consistently within each layer's role.

**Mode 3: Implementing Cloud-Native Patterns in Application Code**
**Symptom:** Custom Circuit Breaker implementation in application code that doesn't integrate with service mesh.
**Root Cause:** Cloud-native patterns are often implemented by infrastructure (Istio, Envoy, Resilience4j); reimplementing in application duplicates and diverges.
**Fix:** Use existing implementations (Resilience4j for Java; Istio Circuit Breaker for mesh); don't reinvent cloud-native patterns in application code.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[DPT-001 - What Are Design Patterns and Why They Exist]]
- [[DPT-002 - The Gang of Four -- Origin and Philosophy]]
- [[DPT-004 - How to Recognize When a Pattern Applies]]

**Builds On This (learn these next):**

- [[DPT-006 - Singleton]]
- [[DPT-052 - CQRS Pattern]]
- [[DPT-057 - Circuit Breaker Pattern]]

**Alternatives / Comparisons:**

- [[DPT-061 - Pattern Selection Framework]]

---

### 📌 Quick Reference Card

```
+-----------------------------------------------------+
| WHAT IT IS      Five-level map: architectural,      |
|                 GoF, concurrency, distributed,      |
|                 cloud-native patterns               |
| PROBLEM         Wrong-level pattern applied;        |
| IT SOLVES       navigating pattern catalogues       |
| KEY INSIGHT     Level = problem granularity;        |
|                 GoF is only one of five levels      |
| USE WHEN        Before choosing a pattern catalogue |
| AVOID WHEN      Treating all patterns as equivalent |
| TRADE-OFF       Orientation time vs jumping to      |
|                 first familiar pattern              |
| ONE-LINER       Navigate to the right level first  |
| NEXT EXPLORE    DPT-006 through DPT-060 per level   |
+-----------------------------------------------------+
```

**If you remember only 3 things:**

1. Five levels: architectural, GoF (design), concurrency, distributed, cloud-native. Match problem granularity to level.
2. GoF patterns are in-process; distributed patterns are cross-service; architectural patterns are system-wide. Never cross levels for a problem.
3. Architectural patterns set context; GoF patterns implement within that context; cloud-native patterns are often handled by infrastructure, not application code.

**Interview one-liner:**
"The design patterns ecosystem has five levels: architectural (Layered, Hexagonal), GoF design (23 OOP patterns), concurrency (Thread Pool, Producer-Consumer), distributed (Saga, CQRS, Outbox), and cloud-native (Circuit Breaker, Sidecar) — matching the problem granularity to the level is the first step in pattern selection."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Every complex domain has a hierarchical structure
where different-level problems require different-level
solutions. Applying a solution at the wrong level
solves the wrong problem. This principle applies to:
networking (application-layer vs transport-layer
problems), database design (schema-level vs query-level
optimisation), team organisation (org-level vs team-
level process problems).

**Where else this pattern appears:**

- **OSI model** -- seven levels; each level solves its level's specific problem; application layer does not route packets
- **Domain-Driven Design** -- strategic design (bounded contexts) sets context; tactical design (aggregates, entities) implements within it
- **Security** -- network-level security (firewalls) vs application-level security (input validation); each level handles its own threats

---

### 💡 The Surprising Truth

The most impactful modern patterns (Saga, CQRS, Event
Sourcing, Outbox) were not invented in academia or
books. Saga was described by Hector Garcia-Molina in
a 1987 database paper for long-running transactions.
CQRS and Event Sourcing were popularised by Greg Young
in blog posts and conference talks (2010-2012). Outbox
Pattern emerged from practical microservices engineering
(Chris Richardson, 2015+). The most useful patterns
emerge from production engineering, not from theory
-- just as the GoF authors derived their patterns from
studying production frameworks, not from inventing
solutions top-down.

---

### 🧠 Think About This Before We Continue

**Q1 (System Interaction):** A team decides to use
Event-Driven Architecture (Level 1: architectural
pattern). What Level 2 (GoF), Level 4 (distributed),
and Level 5 (cloud-native) patterns does this
architectural choice naturally call for? Describe the
cascade of pattern decisions.

*Hint:_ Level 1 -> event-driven. Level 4: events crossing
service boundaries -> Outbox Pattern (reliable event
publishing); consumers -> Dead Letter Queue. Level 2:
processing handler per event type -> Command Pattern
or Strategy. Level 5: broker failure -> Circuit Breaker;
consumer overload -> Bulkhead. Architectural choice
creates a pattern cascade across levels.

**Q2 (Design Trade-off):** Istio (service mesh) implements
Circuit Breaker and Retry at the infrastructure level.
Resilijence4j implements them at the application level
in Java code. When would you choose Resilience4j over
Istio Circuit Breaker, and vice versa?

*Hint:_ Istio Circuit Breaker: uniform policy across all
services; no code changes; works for any language;
but limited to HTTP/gRPC. Resilience4j: fine-grained
per-method control; works for non-HTTP calls (DB calls,
cache calls); more tunable; language-coupled. Choose
Istio for cross-cutting HTTP resilience; Resilience4j
for method-level or non-HTTP resilience.

**Q3 (First Principles):** The Saga pattern (Level 4)
uses compensating transactions to undo partial operations
when a distributed transaction fails. Why can't a
GoF pattern (Level 2) solve this problem? What specific
limitation of GoF patterns makes them insufficient?

*Hint:_ GoF patterns assume in-process execution: shared
memory, synchronous calls, ACID transactions via the
DB. Saga is needed when operations span multiple services
with separate databases (no shared ACID transaction).
GoF patterns have no mechanism for cross-service
rollback; they assume a single failure domain. Saga
explicitly models the compensation logic that reverses
partially completed distributed operations -- a problem
that literally cannot exist in a single process.
