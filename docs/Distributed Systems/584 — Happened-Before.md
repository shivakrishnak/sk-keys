---
layout: default
title: "Happened-Before"
parent: "Distributed Systems"
nav_order: 584
permalink: /distributed-systems/happened-before/
number: "584"
category: Distributed Systems
difficulty: ★★★
depends_on: "Lamport Clock, Vector Clock"
used_by: "Causal Consistency, Distributed Debugging, Event Ordering"
tags: #advanced, #distributed, #causality, #ordering, #theory
---

# 584 — Happened-Before

`#advanced` `#distributed` `#causality` `#ordering` `#theory`

⚡ TL;DR — **Happened-Before** (→) is Lamport's formal causal relation: event A happened-before event B if A could have caused B — establishing the theoretical foundation for all logical clocks, causal consistency, and distributed event ordering.

| #584            | Category: Distributed Systems                             | Difficulty: ★★★ |
| :-------------- | :-------------------------------------------------------- | :-------------- |
| **Depends on:** | Lamport Clock, Vector Clock                               |                 |
| **Used by:**    | Causal Consistency, Distributed Debugging, Event Ordering |                 |

---

### 📘 Textbook Definition

**Happened-Before** (→), defined by Leslie Lamport in "Time, Clocks, and the Ordering of Events in a Distributed System" (1978), is a strict partial order on events in a distributed system capturing potential causal influence. The relation is defined by three rules: (1) if events A and B are on the same process and A occurs before B in process order, then A → B; (2) if A is the sending of a message and B is the receipt of that same message, then A → B; (3) if A → B and B → C, then A → C (transitivity). Two events that are NOT related by → are **concurrent** (written A ∥ B) — neither could have influenced the other. The happened-before relation induces a **partial order** (not a total order) because concurrent events are incomparable. The key insight: happened-before captures potential causality — if A → B, information from A could have influenced B; if A ∥ B, they executed independently. Lamport clocks preserve this relation (A → B implies L(A) < L(B)); vector clocks fully characterise it (A → B if and only if VC_A ≤ VC_B).

---

### 🟢 Simple Definition (Easy)

Happened-before: a formal way to say "event A could have caused event B." Not about wall-clock time — about communication. If A sent a message that B received: A happened-before B. If they had no way to communicate (no messages, different processes): they're concurrent — neither happened before the other. It's a partial order: some events are ordered (causally linked), some are not (concurrent).

---

### 🔵 Simple Definition (Elaborated)

"Happened-before" is about information flow, not time. Example: Alice sends Bob an email at 2pm. Bob reads it at 3pm and replies at 4pm. Alice sending (2pm) happened-before Bob reading (3pm) — because the email IS the causal link. Bob reading (3pm) happened-before his reply (4pm) — same process, program order. Therefore Alice sending (2pm) happened-before Bob's reply (4pm) — transitive. Carol sends Dave a separate email at the same time (no communication with Alice/Bob chain): Carol's email is CONCURRENT with all of Alice-Bob's events.

---

### 🔩 First Principles Explanation

**Formal definition, construction, and use of happened-before:**

```
FORMAL DEFINITION:

  Let E = set of all events in a distributed computation.
  → is the smallest relation satisfying:

  Rule HB1 (Process Order):
    If a and b are events on the SAME PROCESS P_i, and a occurs before b in P_i's execution:
    a → b

  Rule HB2 (Message Passing):
    If a = send(m) on process P_i, and b = receive(m) on process P_j (same message m):
    a → b

  Rule HB3 (Transitivity):
    If a → b and b → c, then a → c.

  Definition of CONCURRENCY:
    a ∥ b (a and b are concurrent) iff NOT (a → b) AND NOT (b → a)

  Properties:
    Irreflexive: a ↛ a (no event before itself)
    Antisymmetric: a → b implies NOT (b → a)
    Transitive: (see Rule HB3)
    → is a strict partial order on E.

CONSTRUCTION FROM EXECUTION TRACE:

  System: 3 processes P1, P2, P3. Events: a, b, c, d, e, f, g.

  Process P1 events (in order): a, b, e
  Process P2 events (in order): c, d, f
  Process P3 events (in order): g

  Messages:
    P1 sends to P2 after event b (so: b → receive_at_P2, which happens between c and d)
    P2 sends to P3 after event f (so: f → g)

  Constructing → relation:
    By HB1 (process order):
      P1: a → b → e
      P2: c → d → f
      P3: (only g)

    By HB2 (message passing):
      b → (receive at P2, between c and d, let's call it d' = receive):
      Actually: message receipt IS one of the events. So:
      b → [receipt event on P2], and [receipt event on P2] → f (by P2 process order)
      f → g (P2 sends to P3; g = receipt)

    By HB3 (transitivity):
      a → b (HB1), b → [recv_P2] (HB2) → a → [recv_P2] (HB3)
      [recv_P2] → f → a → f (trans)
      f → g → a → g (trans)

    Concurrent events:
      a ∥ c: P1 and P2 events before any message between them.
      a ∥ g: P1 has no causal path to P3 (P1→P2→P3 path? Let's check:
             a → [recv_P2] → f → g? Yes! a → g (transitively). NOT concurrent.
      e ∥ g: e is on P1 after the P1→P2 message. Does P1→P2→P3 reach g?
             If e happens after b (message send), and g is after P2→P3 message (after f):
             b → [recv_P2] → f → g, and b → e (? no: e is after b on P1, not after [recv_P2]).
             Is there any path from e to g? e is on P1 after the send to P2. No message from e.
             e ∥ g if no message from e reaches g's process. Likely concurrent.

HAPPENED-BEFORE AND CAUSALITY:

  Key insight: happened-before captures POTENTIAL causality, not definite causality.

  "a → b" means: information from a COULD HAVE influenced b.
    It does NOT mean: b was caused by a (a might have had no effect on b's outcome).

  Example:
    P1: roll a dice (event a, result=6) → sends message → P2
    P2: receive message (event b) → decide to buy coffee (event c, result: coffee purchased)

    a → b → c (by HB1+HB2+HB3).
    a →* c: dice roll COULD HAVE influenced coffee decision.
    In reality: coffee decision had nothing to do with dice result.
    But: happened-before doesn't know that. It only tracks potential influence (communication).

  This is the correct interpretation: happened-before = potential causal influence.
  Use it for: building systems that COULD be causally consistent.
  Don't use it as proof of actual causation.

APPLICATIONS:

1. LAMPORT CLOCKS preserve → :
   a → b ⟹ L(a) < L(b)
   Converse NOT guaranteed: L(a) < L(b) does NOT imply a → b.

   Use: if L(a) > L(b), then DEFINITELY a ↛ b (a did not happen before b).
   If L(a) < L(b): MAYBE a → b or MAYBE a ∥ b. Can't tell.

2. VECTOR CLOCKS characterise → completely:
   a → b ⟺ VC(a) < VC(b) (strictly less component-wise)
   a ∥ b ⟺ VC(a) and VC(b) are incomparable

   Use: for any two events, vector clock comparison tells you which of the three cases:
        a → b, b → a, or a ∥ b.

3. CAUSAL CONSISTENCY:
   Guarantees: if a → b and a is visible on some node, then before b is visible,
               a must also be visible.
   Implementation: buffer b until all events a where a → b are delivered.
   Mechanism: vector clocks track which events must precede delivery.

4. DISTRIBUTED DEBUGGING (with Lamport/Vector timestamps in logs):
   If L(a) < L(b): a happened-before b (or concurrent — can't tell with Lamport).
   If VC(a) < VC(b): a happened-before b (definite, with vector clock).
   If VC(a) incomparable VC(b): concurrent (independent events).

   Use: reconstruct execution order from distributed logs with vector timestamps.
        Find: "which events could have caused this bug event?"
        Answer: all events with vector clock ≤ bug event's vector clock.

5. CONSISTENT GLOBAL STATE (Chandy-Lamport snapshot):
   A "consistent cut" in a distributed execution is a set of events S such that:
   if b ∈ S and a → b, then a ∈ S.
   (If you include an event in your snapshot, include all its happened-before predecessors.)
   Violating this: "seeing a response without the request" — causally inconsistent state.
   Chandy-Lamport algorithm uses happened-before to record consistent global snapshots.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT happened-before:

- No formal definition of "ordering" in distributed systems (physical clocks unreliable)
- No rigorous foundation for logical clocks, causal consistency, or distributed debugging
- Impossible to reason formally about concurrency or causal relationships between events

WITH happened-before:
→ Formal foundation: all logical clock algorithms derive from this relation
→ Causal reasoning: define "this event could have caused that event" precisely
→ Consistent global snapshots: Chandy-Lamport algorithm based on happened-before cuts

---

### 🧠 Mental Model / Analogy

> A rumor spreading through a network of friends. If Alice told Bob the rumor, Bob "knew" about it before he told Carol. Alice telling Bob (A) happened-before Bob telling Carol (C). Dave, who is in a completely different city and never got the rumor, is concurrent with Alice-Bob-Carol's chain — Dave never received any information from that chain. Happened-before = the potential information flow. If there's a chain of "told" relationships from A to C: A happened-before C. If two people were in separate information-isolated groups: they're concurrent.

"Alice told Bob the rumor" = message send → message receive (HB2)
"Bob tells Carol after Alice told Bob" = process order (HB1) + transitivity (HB3)
"Dave in isolated city" = concurrent (no communication link to Alice-Bob-Carol chain)
"Potential information flow" = happened-before tracks if information COULD have spread

---

### ⚙️ How It Works (Mechanism)

**Happened-before in OpenTelemetry distributed tracing:**

```
OpenTelemetry trace: happened-before is encoded in span parent-child relationships.

Trace structure:
  Root span (Gateway): receives HTTP request
    │
    ├── Child span (Auth Service): authenticate user
    │     │
    │     └── Child span (DB): check session token
    │
    └── Child span (Order Service): process order
          │
          ├── Child span (Inventory Service): check stock
          └── Child span (Payment Service): charge card

Happened-before encoded:
  Gateway:start → Auth:start (Gateway sent message to Auth)
  Auth:start → DB:start (Auth sent message to DB)
  DB:end → Auth:end (DB responded to Auth — Auth cannot end before DB)
  Auth:end → Order:start (simplified: after auth, order starts)
  Order:start → Inventory:start AND Order:start → Payment:start

  Concurrent: Inventory and Payment (both children of Order, running in parallel).
  Inventory ∥ Payment (no causal link between them — they don't communicate directly).

Debug question: "Payment failed — what happened before?"
  Answer: all spans in the transitive closure of happened-before of Payment:
    Gateway:request → Auth:authenticate → DB:check_session → Order:process → Payment:charge
  These are ALL events that could have caused the payment failure.
  Inventory: concurrent → its state could NOT have directly caused Payment failure.
```

---

### 🔄 How It Connects (Mini-Map)

```
Events in distributed system (on processes, sent/received via messages)
        │
        ▼
Happened-Before (→) ◄──── (you are here)
(formal partial order: causal predecessor relation)
        │
        ├── Lamport Clock (preserves →; A→B ⟹ L(A)<L(B))
        ├── Vector Clock (characterises →; bidirectional)
        └── Causal Consistency (enforces → for reads/writes)
```

---

### 💻 Code Example

**Verifying happened-before from distributed logs using vector clock comparison:**

```python
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class LogEntry:
    process_id: str
    event_name: str
    vector_clock: Dict[str, int]

def happened_before(a: LogEntry, b: LogEntry) -> bool:
    """Returns True if a → b (a happened-before b) using vector clock comparison."""
    all_nodes = set(a.vector_clock.keys()) | set(b.vector_clock.keys())
    # a ≤ b: all entries of a ≤ entries of b
    all_le = all(a.vector_clock.get(n, 0) <= b.vector_clock.get(n, 0) for n in all_nodes)
    # and at least one strictly less:
    any_lt = any(a.vector_clock.get(n, 0) < b.vector_clock.get(n, 0) for n in all_nodes)
    return all_le and any_lt

def is_concurrent(a: LogEntry, b: LogEntry) -> bool:
    """Returns True if a ∥ b (concurrent)."""
    return not happened_before(a, b) and not happened_before(b, a)

def find_causes(event: LogEntry, all_events: List[LogEntry]) -> List[LogEntry]:
    """Find all events that happened-before the given event (potential causes)."""
    return [e for e in all_events if happened_before(e, event) and e != event]

# Example: distributed trace analysis
logs = [
    LogEntry("gateway", "REQUEST_RECEIVED", {"gateway": 1, "auth": 0, "order": 0}),
    LogEntry("auth", "AUTH_START", {"gateway": 1, "auth": 1, "order": 0}),
    LogEntry("auth", "AUTH_SUCCESS", {"gateway": 1, "auth": 2, "order": 0}),
    LogEntry("order", "ORDER_PROCESSING", {"gateway": 1, "auth": 2, "order": 1}),
    LogEntry("payment", "PAYMENT_FAILED", {"gateway": 1, "auth": 2, "order": 1, "payment": 1}),
    LogEntry("inventory", "STOCK_CHECKED", {"gateway": 1, "auth": 2, "order": 1, "inventory": 1}),
]

payment_failed = logs[4]
causes = find_causes(payment_failed, logs)
print(f"Events that happened-before PAYMENT_FAILED:")
for e in causes:
    print(f"  - {e.process_id}: {e.event_name} @ VC={e.vector_clock}")

# Check if inventory and payment are concurrent:
inventory = logs[5]
print(f"\nInventory ∥ Payment? {is_concurrent(inventory, payment_failed)}")  # True
```

---

### ⚠️ Common Misconceptions

| Misconception                                 | Reality                                                                                                                                                                                                                                                                                                                                                                                              |
| --------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Happened-before means earlier wall-clock time | Happened-before is about information flow (communication), NOT wall-clock time. Two events on the same machine have happened-before ordering even if they occur within nanoseconds. Two events on different machines might be concurrent even if their wall-clock times differ by minutes — if no message was exchanged between them                                                                 |
| If A happened-before B, A caused B            | Happened-before captures POTENTIAL causality. A → B means the information from A COULD have reached B (there's a communication path). It does NOT mean A actually influenced B's outcome. The dice roll example: the roll (event A) happened-before the coffee purchase (event C, after receiving a message from A's process), but the roll didn't cause the coffee purchase                         |
| Happened-before defines a total order         | Happened-before is a STRICT PARTIAL ORDER — only some pairs of events are related. Concurrent events (A ∥ B) are incomparable in the happened-before order. A total order requires all pairs to be comparable. Lamport's paper shows you can EXTEND the partial order to a total order (by tie-breaking), but this extension is not unique — many total orders are consistent with the partial order |
| Lamport clocks implement happened-before      | Lamport clocks PRESERVE but do not fully CHARACTERISE happened-before. They guarantee: A → B ⟹ L(A) < L(B). But the converse is NOT guaranteed: L(A) < L(B) does not necessarily mean A → B. Lamport clocks can only tell you "A definitely did NOT happen-before B" when L(A) ≥ L(B). Vector clocks fully characterise happened-before bidirectionally                                              |

---

### 🔥 Pitfalls in Production

**Distributed tracing causality chain broken by missing context propagation:**

```
PROBLEM: Service calls another service but doesn't propagate trace context.
         Happened-before chain broken in observability tools.
         Cannot debug: "what events caused this error?"

  OrderService → (HTTP call) → InventoryService → (DB query) → DB

  OrderService: starts Span("process_order"), VC = {order: 5, auth: 3}.
  HTTP call: should propagate VC to InventoryService (via traceparent header).

  Bug: developer added HTTP client manually (forgot to use instrumented client):
    HttpURLConnection conn = new URL(inventoryServiceUrl).openConnection();
    // Missing: conn.setRequestProperty("traceparent", tracing.currentSpan().context().toW3cHeader());
    // Missing: conn.setRequestProperty("X-B3-TraceId", ...);

  InventoryService: receives HTTP call WITHOUT trace context.
  InventoryService: starts NEW root span (VC = {inventory: 1, db: 0}).
  DB query: child of InventoryService span.

  Result in Jaeger/Zipkin:
    OrderService trace: [process_order → payment → ...] (no inventory span)
    InventoryService: SEPARATE trace (orphaned) — not connected to order trace.

  Debug: "InventoryService returned 404 — what caused it?"
  Without trace propagation: cannot find the OrderService event that triggered it.
  Happened-before chain: BROKEN between OrderService and InventoryService.

BAD: Missing trace context propagation:
  // Manual HTTP client without trace propagation:
  HttpURLConnection conn = (HttpURLConnection) new URL(url).openConnection();
  // No context headers → new trace started at InventoryService → orphaned.

FIX: Use OpenTelemetry instrumented client (automatic context propagation):
  // Spring Boot: use RestTemplate or WebClient with OpenTelemetry auto-instrumentation.
  // OTel Java agent automatically adds traceparent header to all outbound HTTP calls.

  // Manual: extract and inject context:
  TextMapPropagator propagator = GlobalOpenTelemetry.getPropagators().getTextMapPropagator();
  propagator.inject(Context.current(), requestHeaders, HttpHeadersSetter.INSTANCE);
  // ↑ Adds W3C traceparent header: "00-{traceId}-{spanId}-{flags}"
  // InventoryService receives it, extracts parent context, creates CHILD span.
  // Happened-before chain maintained in tracing system.
```

---

### 🔗 Related Keywords

- `Lamport Clock` — preserves happened-before (A→B ⟹ L(A)<L(B)); doesn't fully characterise
- `Vector Clock` — fully characterises happened-before (A→B ⟺ VC(A)<VC(B))
- `Causal Consistency` — consistency model that enforces the happened-before ordering on reads
- `Distributed Tracing` — observability tool that encodes happened-before in span parent-child links

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ A→B if: same process order, or message    │
│              │ send→receive, or transitivity;            │
│              │ otherwise: concurrent (A∥B)               │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Building logical clocks; defining causal  │
│              │ consistency; distributed snapshot/debug   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Assuming happened-before = actual wall    │
│              │ clock time or actual causation            │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Rumor network: A→B if information from A │
│              │  could have reached B via communication." │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Lamport Clock → Vector Clock → Causal     │
│              │ Consistency → Distributed Tracing          │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** The Chandy-Lamport distributed snapshot algorithm records a "consistent global state" based on the happened-before relation. The algorithm uses markers (checkpoint messages) to capture local state of each process. What makes a global state "consistent" in terms of happened-before? Can you construct an example of an INCONSISTENT global state (a "cut" of the execution where you've included an event but excluded an event that happened-before it) and explain why it's problematic?

**Q2.** In microservices, a "saga" pattern coordinates a multi-step transaction across services. Each step produces an event. If Step 3 fails and triggers a compensating transaction, the compensating event must be "seen after" Step 3's failure event. How does happened-before apply to saga rollback ordering? What happens if a compensating transaction is delivered BEFORE the failure event it's compensating for, and how do modern saga implementations prevent this?
