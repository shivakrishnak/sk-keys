---
layout: default
title: "Happened-Before"
parent: "Distributed Systems"
nav_order: 584
permalink: /distributed-systems/happened-before/
number: "0584"
category: Distributed Systems
difficulty: ★★★
depends_on: Distributed Systems, Concurrency vs Parallelism, Causality
used_by: Lamport Clock, Vector Clock, Causal Consistency, Total Order, CRDT
related: Lamport Clock, Vector Clock, Total Order, Causal Consistency, Linearizability
tags:
  - distributed
  - concurrency
  - algorithm
  - deep-dive
  - first-principles
---

# 584 — Happened-Before

⚡ TL;DR — The "happened-before" relation (→) is the formal definition of causality in distributed systems: event A happened-before B if A could have influenced B through any chain of events or messages, regardless of physical clock time.

| #584            | Category: Distributed Systems                                                 | Difficulty: ★★★ |
| :-------------- | :---------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Distributed Systems, Concurrency vs Parallelism, Causality                    |                 |
| **Used by:**    | Lamport Clock, Vector Clock, Causal Consistency, Total Order, CRDT            |                 |
| **Related:**    | Lamport Clock, Vector Clock, Total Order, Causal Consistency, Linearizability |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A distributed chat app. User A sends "Hello" at physical time T1. User B replies
"Hi back!" at physical time T2. But due to network lag, the reply arrives at the
display server before "Hello" does. Users see the reply first. This is not just
a display bug — it's a fundamental causality violation: a system has allowed an
effect to appear before its cause. Without a formal definition of "A causes B,"
no algorithm can prevent or detect this class of error.

**THE INVENTION MOMENT:**
Leslie Lamport formalised happened-before in his landmark 1978 paper. By precisely
defining what "A could have influenced B" means in terms of events and messages,
he gave distributed systems a rigorous foundation for reasoning about causality —
independent of physical time, network delays, or machine speeds.

---

### 📘 Textbook Definition

The **happened-before** relation (→), defined by Lamport on events in a distributed system, satisfies three rules: (1) **Process order**: if A and B are events in the same process and A occurred before B, then A → B. (2) **Message passing**: if A is the sending of a message and B is the receipt of that message, then A → B. (3) **Transitivity**: if A → B and B → C, then A → C. Two events A and B are **concurrent** (written A ∥ B) if neither A → B nor B → A. Happened-before is a strict partial order (irreflexive, asymmetric, transitive) on the set of events in a distributed computation. It captures exactly the potential causal influence between events.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
"A happened before B" means A could have sent a message that influenced B, directly or through intermediaries.

**One analogy:**

> Happened-before is like a paper trail of who cc'd whom on an email chain.
> If Alice sent Bob an email, and Bob forwarded to Carol, then Alice's message
> happened before Carol's response — even if the calendar times are wrong.
> Two emails on completely separate threads have no happened-before relation
> — they're concurrent. The email chain IS the causality graph.

**One insight:**
Happened-before is not about physical time — it's about information flow. "A happened before B" means information from A _could_ have arrived at B before B occurred. Two events are concurrent if neither could have informed the other. This purely logical definition is what makes it robust across arbitrary network delays, clock skews, and machine failures.

---

### 🔩 First Principles Explanation

**THE THREE RULES (explicit):**

```
System: N processes, each performing events.
Events: local computations + send/receive of messages.

Rule 1 (Process Order):
  Events a, b in same process p:
  If a appears before b in p's execution sequence → a → b

Rule 2 (Message Causality):
  send(m) in process p, receive(m) in process q:
  send(m) → receive(m)
  (the send of a message causally precedes its receipt)

Rule 3 (Transitivity):
  a → b AND b → c → a → c

CONCURRENT: ¬(a → b) AND ¬(b → a)
  Neither could have influenced the other.
  "A ∥ B" means no information flow between them.
```

**CAUSAL GRAPH EXAMPLE:**

```
Process P1:   A ──────→ C ──────→ E
               \send m1    \send m2
                ↓            ↓
Process P2:    B ←recv m1   D ─────→ F
               send m3↗          ↗send m4
                      ↓         ↓
Process P3:           X ──────→ Y ←recv m4

Happens-before chains:
  A → C  (process order)
  A → B  (via message m1? No — A is send of m1, so A → B?
          Actually: the send event for m1 at P1 is → receive at P2)
  Let's say A is the send of m1: A → B (message rule)
  B → D? Only if D receives B's message. Let's say B sends m3 to C: B → C (via m3 receive)
  C → E, C → D (via m2 receive), E, D are then ordered.

The key structure: solid arrows = happened-before; dashed = concurrent.
A ∥ X  (no message path between them)
E ∥ Y  (if no message from E ever reaches Y's precursor)
```

**RELATING TO REAL CONSISTENCY BUGS:**

```
Causal consistency violation:
  Op A: User posts photo (P → database-write)
  Op B: Database-write propagates to replica (A → B by message)
  Op C: Friend queries replica for user's photos

  If C happens on a replica that hasn't received B yet:
    Query C returns without the photo
    C sees state that IGNORES A, even though A → B → ?C

  Causal consistency says: if A → B and A "potentially" → C,
  then C must see A's effect.

  This is violated when C is served by a stale replica.
  Detecting "C should see A's effect" requires tracking
  happened-before via vector clocks.
```

---

### 🧪 Thought Experiment

**THE BANK TRANSFER CAUSALITY:**
Alice transfers $100 from her savings to her checking account.
Operation 1: `DEBIT savings -100` (on node S)
Operation 2: `CREDIT checking +100` (on node C)
These operations are sent in sequence: Op1 → Op2 (happened-before by process order).

A third user, Bob, reads both accounts at "the same time."

**SCENARIO A:** Bob reads BOTH accounts AFTER both ops are applied. Balance consistent.

**SCENARIO B:** Bob reads checking (before Op2) and savings (after Op1).
Bob sees: $100 missing from savings AND not in checking — $100 has vanished.

**WHY THIS IS A CAUSALITY VIOLATION:**
Bob's reads are concurrent with Op2. But because Op1 happened-before Op2, and
Op1 happened-before Bob's savings read, causal consistency requires Bob to see a
world consistent with Op1. Allowing Bob to see savings-deducted WITHOUT checking-credited
is a causal violation — an effect (visible debit) without its cause being visible.

**THE FIX:** Causal consistency + read-your-writes ensures that if a client C
has observed Op1 transitively (because it saw the state after Op1), it will only
read from replicas that have also applied Op2.

---

### 🧠 Mental Model / Analogy

> Happened-before is the "could have known about" relation.
> A → B means: "by the time B happened, B could have received information
> about A through some chain of messages."
>
> A ∥ B means: "A and B happened in complete ignorance of each other — neither
> could have received information from the other before completing."
>
> This is NOT about physical timing. It's about information reachability.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** "A happened before B" means A could have sent a message that reached B before B completed. Two events are concurrent if neither could have known about the other.

**Level 2:** Happened-before is the foundation of Lamport Clocks (which use it to order events) and Vector Clocks (which detect it precisely). If you can track happened-before, you can build causally consistent distributed systems that never show an effect before its cause.

**Level 3:** The relation is a strict partial order on system events — irreflexive, asymmetric, transitive. Building a consistent total order that extends happened-before (without contradicting it) is what Lamport's clock construction achieves. Any total ordering that respects → is a valid linearisation of the partial order.

**Level 4:** Happened-before is the formal basis for all consistency models in distributed systems. Causal consistency requires all replicas to apply operations in any order that extends happened-before. Sequential consistency requires a single total order consistent with per-process happened-before. Linearizability adds the constraint that the total order must also be consistent with real-time intervals (each operation's real-time invocation must precede its real-time return in the linearised order). The hierarchy: Sequential < Causal < Eventual; Linearizability is orthogonal to these (adds real-time constraint). Happened-before is the shared formal foundation.

---

### ⚙️ How It Works (Mechanism)

**Happens-Before Tracking (distributed event logging):**

```java
// Attach Lamport timestamp to every event:
// If ts(A) < ts(B) AND same process or message path → A likely → B
// For exact detection: use Vector Clocks

// Example: distributed tracing span causality
Span childSpan = tracer.buildSpan("operation")
    .asChildOf(parentSpanContext)  // parent's vector clock propagated
    .start();                       // in HTTP headers

// The parent span A → child span B (parent → child injection)
// All spans in a trace form a partial order (happened-before tree)
// The trace UI renders this as a causal graph
```

---

### ⚖️ Comparison Table

| Relation            | Definition                | Detectable By | Application                      |
| ------------------- | ------------------------- | ------------- | -------------------------------- |
| Happened-Before (→) | Causal influence possible | Vector Clock  | Causally consistent reads        |
| Concurrent (∥)      | No causal link            | Vector Clock  | Conflict detection               |
| Physical Before     | Wall clock comparison     | NTP time      | Human-readable logs (unreliable) |
| Logical Before      | Lamport timestamp         | Lamport Clock | Total order (partial causality)  |

---

### ⚠️ Common Misconceptions

| Misconception                                           | Reality                                                                                                                                |
| ------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| A → B means A physically happened first                 | A → B means information COULD have flowed from A to B — it's about potential influence, not physical time                              |
| Concurrent means simultaneous                           | Concurrent means NEITHER influenced the other — they could have happened at very different physical times                              |
| Happened-before is transitive but not reflexive         | Correct — it's a strict partial order (irreflexive: nothing happened before itself)                                                    |
| All events in a distributed system are causally related | Most real events in large distributed systems are concurrent with most other events — only events in the same causal chain are related |

---

### 🔗 Related Keywords

- `Lamport Clock` — the algorithm that operationalises happened-before into countable timestamps
- `Vector Clock` — the algorithm that precisely detects happened-before and concurrent events
- `Causal Consistency` — the storage-level consistency model guarantee built on happened-before
- `CRDT` — data structures that handle concurrent (∥) operations via commutative/associative merge

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│  A → B  ("A happened before B"):                         │
│    Same process: A before B in execution order           │
│    Message:      send(m) before recv(m)                   │
│    Transitive:   A → B and B → C → A → C                 │
│  A ∥ B ("concurrent"):                                    │
│    neither A → B nor B → A                               │
│  NOT physical time — it's causal information reachability │
│  Foundation of: Lamport Clock, Vector Clock, Causal Cons. │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Three processes P1, P2, P3. P1 sends m1 to P2. P2 sends m2 to P3. P3 does a local event L. P3 sends m3 to P1. List all happened-before pairs `(A → B)` in this system and identify all pairs of events that are concurrent. Show your reasoning using only the three rules.

**Q2.** Social media platform: a post P is created at time T1. A comment C is made on post P at T2. Another user deletes post P at T3 (where T1 < T2 < T3 in wall-clock time). But due to network partitions, some replicas see the delete before the comment. Using happened-before: define the causal relationship between the delete and the comment, explain what a causally consistent system guarantees about the ordering a user will observe, and describe the observable anomaly that would occur if the system violated causal consistency here.
