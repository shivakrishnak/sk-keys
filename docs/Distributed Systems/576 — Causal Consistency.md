---
layout: default
title: "Causal Consistency"
parent: "Distributed Systems"
nav_order: 576
permalink: /distributed-systems/causal-consistency/
number: "576"
category: Distributed Systems
difficulty: ★★★
depends_on: "Consistency Models, Lamport Clock"
used_by: "Distributed Databases, Chat Systems, Social Platforms"
tags: #advanced, #distributed, #consistency, #causality, #ordering
---

# 576 — Causal Consistency

`#advanced` `#distributed` `#consistency` `#causality` `#ordering`

⚡ TL;DR — **Causal Consistency** guarantees that causally related operations are seen by all nodes in their causal order — no node sees a "reply" before the "original post" — while unrelated (concurrent) operations may be seen in any order.

| #576            | Category: Distributed Systems                         | Difficulty: ★★★ |
| :-------------- | :---------------------------------------------------- | :-------------- |
| **Depends on:** | Consistency Models, Lamport Clock                     |                 |
| **Used by:**    | Distributed Databases, Chat Systems, Social Platforms |                 |

---

### 📘 Textbook Definition

**Causal Consistency** is a consistency model that guarantees operations which are causally related — where one operation's result was observed by a process before it performed the next operation — are seen in the same causal order by all processes in the system. Operations that are causally unrelated (concurrent) may be observed in different orders by different processes. Causal consistency is weaker than sequential consistency (which requires a single total order seen by all) and stronger than eventual consistency (which provides no ordering guarantee). Causal relationships are tracked using **vector clocks** or **causal tokens**: each write carries a dependency set specifying which previous writes must be visible before this write can be applied. Systems implementing causal consistency buffer incoming writes and apply them only when all causal dependencies are satisfied. Causal consistency avoids the confusing anomaly where a response appears before the message being responded to, making it the natural consistency level for social media, collaborative tools, and messaging systems.

---

### 🟢 Simple Definition (Easy)

Causal consistency: "You'll never see the answer to a question without first seeing the question." If Alice posts "Who wants pizza?" and Bob replies "Me!", causal consistency ensures that Carol always sees Alice's question before Bob's reply — no matter which server she's reading from. Unrelated posts (Alice's pizza question and Dave's cat photo, posted simultaneously with no relation) can appear in any order.

---

### 🔵 Simple Definition (Elaborated)

Causal consistency lives between eventual consistency and strong consistency on the spectrum. Eventual consistency: the pizza answer might appear before the question (confusing — but legal). Strong consistency: all posts appear in real-time global order (expensive — requires coordination for every write). Causal consistency: only causally linked posts are ordered (question before answer), but independent posts can appear in any order. This is usually sufficient for social media and messaging — most users only care that conversations make sense, not that every post globally is in real-time order.

---

### 🔩 First Principles Explanation

**Causal consistency with vector clocks: detecting and enforcing causal order:**

```
CAUSAL RELATIONSHIPS: DEFINITION

  "A causally precedes B" (A → B) if any of:
  1. A and B are on the SAME process and A happened before B (program order).
  2. A is a SEND and B is the corresponding RECEIVE of the same message.
  3. Transitivity: A → C and C → B implies A → B.

  "A and B are CONCURRENT" if neither A → B nor B → A.
  Concurrent = no causal dependency between the two events.

CAUSAL CONSISTENCY VIOLATION EXAMPLE:

  Setup: 3-node distributed database. Nodes N1, N2, N3.
  Alice's session: connected to N1.
  Bob's session: connected to N2.
  Carol's session: connected to N3.

  Timeline:
    T=1 (N1): Alice writes: post P1 = "Who wants pizza?"
    T=2 (N1 → N2): N1 replicates P1 to N2 (fast path, arrived at T=2)
    T=3 (N2): Bob reads P1 on N2 → sees "Who wants pizza?"
    T=4 (N2): Bob writes: post P2 = "Me!" (B's write carries dependency on P1)
    T=5 (N2 → N3): N3 receives P2 first (P2 → N3 faster than P1 → N3)
    T=6 (N1 → N3): N3 eventually receives P1

  Without causal consistency:
    T=5: Carol reads on N3: sees "Me!" but NOT "Who wants pizza?" yet → confusing!
    T=6: Carol sees "Who wants pizza?" appear AFTER "Me!" → nonsensical conversation.

  With causal consistency:
    T=5: N3 receives P2 with dependency on P1.
    N3: P1 not yet received → BUFFER P2 (cannot apply yet).
    T=6: N3 receives P1 → apply P1, then apply buffered P2.
    Carol now sees P1 before P2 → correct causal order.

VECTOR CLOCK IMPLEMENTATION:

  Vector clock: array of counters, one per process.
  VC = [N1_count, N2_count, N3_count]

  Each operation tagged with the vector clock at the time of write.
  A → B if VC_A ≤ VC_B (all entries of VC_A ≤ corresponding entries of VC_B)
              and VC_A ≠ VC_B (not identical).

  Example:
    Alice writes P1 on N1:
      Before write: VC = [0, 0, 0]
      N1 increments: VC_P1 = [1, 0, 0]
      P1 stamped with VC = [1, 0, 0]

    Bob reads P1 on N2 (N2 receives P1 and merges VC):
      N2 VC after receiving P1: [1, 0, 0]

    Bob writes P2 on N2 (causally after reading P1):
      N2 increments: VC_P2 = [1, 1, 0]
      P2 stamped with VC = [1, 1, 0] (carries causal dependency on VC = [1, 0, 0])

    N3 receives P2 first:
      P2 has VC = [1, 1, 0]
      N3 current VC = [0, 0, 0]
      P2 depends on VC = [1, _, _] (N1 counter must be ≥ 1 before P2 can be applied)
      N3: N1 counter = 0 < 1 (required) → buffer P2 (causal dependency not satisfied)

    N3 receives P1:
      P1 has VC = [1, 0, 0]
      N3 N1 counter = 0 < 1 → apply P1 → N3 VC = [1, 0, 0]
      Check buffered P2: N1 counter = 1 ≥ 1 → causal dependency satisfied → apply P2
      N3 VC = [1, 1, 0]
      Carol reads: sees P1 then P2 → correct causal order ✓

WHAT CAUSAL CONSISTENCY DOES NOT GUARANTEE:

  Alice posts: "P1: Who wants pizza?" (on N1, VC=[1,0,0])
  Dave posts: "P2: I just saw a cool cat!" (on N3, VC=[0,0,1]) — concurrent to P1

  P1 and P2 are CONCURRENT (no causal dependency between them).

  Carol on N2 may see: P1 then P2 (Alice's pizza question first, then Dave's cat)
  Bob on N4 may see: P2 then P1 (Dave's cat first, then Alice's pizza question)

  Both orderings are LEGAL under causal consistency.
  Only if Bob READS P1 and then writes P3 (causally depends on P1) does causal
  consistency impose that others see P1 before P3.

  For total order of all posts: need sequential consistency (more expensive).

CAUSAL CONSISTENCY IN REAL SYSTEMS:

  MongoDB (since 4.0): "causal consistency sessions"
    Client sends "afterClusterTime" token with each read/write.
    Token = logical timestamp of last operation in session.
    Server: will not serve read until it has caught up to that timestamp.
    → Read-your-writes within a session (stronger guarantee than bare eventual consistency).

  DynamoDB (2021): "strongly consistent reads" option per request.
    Not full causal consistency — provides linearisable reads but not causal ordering across ops.

  CosmosDB: configurable consistency levels including "session consistency"
    (read-your-writes + monotonic reads — slightly weaker than full causal consistency).

  Bayou (classic research system): explicit causal dependencies in writes.
    Peer-to-peer sync with anti-entropy. Buffering writes with unmet dependencies.
    Conflict detection and resolution at application level.

PERFORMANCE CHARACTERISTICS:

  Causal consistency overhead vs eventual:
    Vector clock storage: O(N) per message (N = number of nodes).
    Buffering: writes may be delayed if causal predecessor not yet received.
    In practice: buffering delays are rare (fast intra-DC networks).

  Causal consistency vs strong consistency:
    No global coordination required for writes.
    Reads do not need to contact quorum.
    Write latency: same as eventual consistency (local write, async propagation).
    Read latency: same as eventual consistency (local read, may buffer briefly).

  For social media with millions of posts per second:
    Strong consistency: every post requires global coordination → 200ms+ per post.
    Causal consistency: no coordination on writes → 1ms write, occasional brief buffering on read.
    This is why causal consistency is the practical choice for social platforms.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT causal consistency (eventual only):

- Chat messages appear out of order: reply before message, delete before post, like before photo
- Confusing user experience: "I can see Carol liked a photo but the photo doesn't exist yet"
- Developers add application-level retry/delay hacks to work around ordering issues

WITH causal consistency:
→ Conversations always make sense: question before answer, message before reply
→ No application-level ordering hacks needed
→ Better than strong consistency: no global coordination, low write latency

---

### 🧠 Mental Model / Analogy

> An email thread where the mail client guarantees you'll always receive the original email before any reply to it, but two separate email threads (no causal link) might arrive in any order. "Alice's email to the team" → "Bob's reply to Alice" → always delivered in this order to Carol, even if Bob's reply arrived at Carol's mail server before Alice's original. Two separate emails (Alice's team update and Dave's meeting invite, sent independently) may arrive in either order — no causality link means no ordering guarantee.

"Reply always after original email" = causal dependency enforced
"Two unrelated emails in any order" = concurrent operations, no ordering required
"Mail server buffers reply until original received" = causal dependency buffering
"Reply carries reference to original email" = vector clock / causal token

---

### ⚙️ How It Works (Mechanism)

**Causal dependency buffering in distributed message queue:**

```python
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import threading

@dataclass
class Message:
    msg_id: str
    content: str
    vector_clock: Dict[str, int]  # {node_id: counter}

class CausallyConsistentNode:
    """A node that buffers messages until all causal dependencies are satisfied."""

    def __init__(self, node_id: str):
        self.node_id = node_id
        self.local_vc: Dict[str, int] = {}  # Current vector clock of this node
        self.delivered_messages: List[Message] = []
        self.buffer: List[Message] = []  # Messages waiting for causal dependencies
        self._lock = threading.Lock()

    def _vc_le(self, vc1: Dict[str, int], vc2: Dict[str, int]) -> bool:
        """Returns True if vc1 ≤ vc2 (all entries of vc1 ≤ vc2)."""
        all_keys = set(vc1.keys()) | set(vc2.keys())
        return all(vc1.get(k, 0) <= vc2.get(k, 0) for k in all_keys)

    def _causal_deps_met(self, msg: Message) -> bool:
        """Message can be delivered if its causal dependencies are met by local VC."""
        # All entries in message's VC (except sender's) must be ≤ local VC.
        # Sender's entry must be exactly local_vc[sender] + 1.
        sender = next(
            (k for k, v in msg.vector_clock.items()
             if v > self.local_vc.get(k, 0)),
            None
        )
        if not sender:
            return True

        for node, count in msg.vector_clock.items():
            if node == sender:
                if count != self.local_vc.get(node, 0) + 1:
                    return False  # Out of order from this sender
            else:
                if count > self.local_vc.get(node, 0):
                    return False  # Missing causal predecessors from other nodes
        return True

    def receive(self, msg: Message):
        """Receive a message — buffer it if causal dependencies not yet met."""
        with self._lock:
            self.buffer.append(msg)
            self._try_deliver_buffered()

    def _try_deliver_buffered(self):
        """Attempt to deliver all buffered messages in causal order."""
        delivered_any = True
        while delivered_any:
            delivered_any = False
            for msg in list(self.buffer):
                if self._causal_deps_met(msg):
                    self.buffer.remove(msg)
                    self._deliver(msg)
                    delivered_any = True

    def _deliver(self, msg: Message):
        """Actually deliver (apply) a message."""
        # Update local vector clock by taking max of each entry:
        for node, count in msg.vector_clock.items():
            self.local_vc[node] = max(self.local_vc.get(node, 0), count)
        self.delivered_messages.append(msg)
        print(f"[{self.node_id}] Delivered: {msg.content} (VC={msg.vector_clock})")
```

---

### 🔄 How It Connects (Mini-Map)

```
Consistency Models (full spectrum)
        │
        ▼
Causal Consistency ◄──── (you are here)
(between eventual and sequential)
        │
        ├── Lamport Clock (basic logical timestamps — not sufficient for causal ordering)
        ├── Vector Clock (tracks causal dependencies per-node)
        └── Happened-Before (the causal relation being enforced)
```

---

### 💻 Code Example

**MongoDB causal consistency session:**

```java
// MongoDB 4.0+ causal consistency: ensures read-your-writes and causal ordering.

@Service
public class SocialPostService {

    private final MongoClient mongoClient;

    // With causal consistency session: each read/write carries causal token.
    // MongoDB guarantees: within this session, reads see all previous writes.
    public void postAndVerify(String userId, String content) {
        try (ClientSession session = mongoClient.startSession(
                ClientSessionOptions.builder()
                    .causallyConsistent(true)  // Enable causal consistency
                    .build())) {

            MongoCollection<Document> posts = mongoClient
                .getDatabase("social")
                .getCollection("posts")
                .withReadPreference(ReadPreference.secondaryPreferred());  // Prefer replica reads

            // Write post (goes to primary):
            Document post = new Document()
                .append("user_id", userId)
                .append("content", content)
                .append("created_at", new java.util.Date());

            posts.insertOne(session, post);
            // session.getOperationTime() now holds the logical timestamp of this write.

            // Read from REPLICA with causal consistency:
            // MongoDB passes operationTime to replica → replica waits until it has
            // applied all ops up to this time → guarantees we see our own write.
            List<Document> myPosts = posts
                .find(session, new Document("user_id", userId))
                .into(new java.util.ArrayList<>());

            // Guaranteed to include the post we just wrote,
            // even though we're reading from a secondary replica!
            System.out.println("Posts visible: " + myPosts.size());
        }
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                                         | Reality                                                                                                                                                                                                                                                                                                                                                                                                                   |
| --------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Causal consistency is the same as "read-your-writes"                  | Causal consistency is stronger than read-your-writes. Read-your-writes only guarantees that YOU see your OWN writes. Causal consistency guarantees that if you observe write A and then perform write B (causally depending on A), ALL other processes see A before B — regardless of who performed the reads and writes. Causal consistency captures cross-process causal dependencies, not just within a single session |
| Vector clocks are always needed for causal consistency                | Vector clocks are the textbook mechanism, but some systems use lighter-weight alternatives. MongoDB uses a single logical timestamp (cluster time) that advances monotonically — effectively a simplified causal token. Google Spanner uses TrueTime for global causal ordering. Vector clocks scale O(N) with the number of nodes; some systems use hybrid approaches to reduce overhead                                 |
| Causal consistency requires expensive coordination                    | Causal consistency can be implemented with NO global coordination on writes. Writes propagate asynchronously; receiving nodes buffer messages with unmet dependencies. The only overhead vs eventual consistency is the buffering on receivers and the causal token metadata. Write latency is the same as eventual consistency — no synchronous replication round-trip required                                          |
| If two operations are concurrent, causal consistency imposes an order | Concurrent operations (no causal dependency between them) are NOT ordered by causal consistency. Two independent posts made simultaneously on different nodes may be seen in different orders by different observers — this is explicitly allowed. Only causally related operations are ordered. This is what makes causal consistency cheaper than sequential consistency (which orders ALL operations globally)         |

---

### 🔥 Pitfalls in Production

**Causal context lost across service boundaries:**

```
PROBLEM: Two services communicate; causal token not propagated between them.
         Result: reading causally stale data despite causal consistency within each service.

  Order Service writes: order #123 status=COMPLETED at T=logical(500).
  Order Service notifies Notification Service via message queue (Kafka).
  Notification Service receives message.

  Notification Service: reads order #123 from MongoDB → ConsistencyLevel=EVENTUAL.
  MongoDB replica: has not yet seen the status=COMPLETED write (lag = 200ms).
  Notification Service: reads status=PENDING → sends "Your order is pending" email!

  Root cause: the causal token (MongoDB operation time = 500) was NOT included
              in the Kafka message. Notification Service read without causal context.

BAD: Message without causal token:
  // Order Service sends Kafka message:
  kafkaProducer.send(new ProducerRecord<>("order-events",
      new OrderEvent(orderId="123", status="COMPLETED")));
  // Missing: MongoDB operation time for this write

FIX: Include causal token in all cross-service messages:
  // Order Service — after MongoDB write:
  BsonTimestamp operationTime = mongoSession.getOperationTime();  // causal token
  kafkaProducer.send(new ProducerRecord<>("order-events",
      new OrderEvent(
          orderId="123",
          status="COMPLETED",
          causalToken=operationTime.toString()  // include in message
      )));

  // Notification Service — use causal token when reading:
  BsonTimestamp causalToken = BsonTimestamp.parse(event.getCausalToken());
  ClientSession session = mongoClient.startSession(
      ClientSessionOptions.builder().causallyConsistent(true).build());
  session.advanceOperationTime(causalToken);  // catch up to causal context
  session.advanceClusterTime(causalClusterTime);

  // Now read: MongoDB waits until replica has applied up to causalToken:
  Document order = ordersCollection.find(session,
      Filters.eq("_id", orderId)).first();
  // Guaranteed to see status=COMPLETED now.
```

---

### 🔗 Related Keywords

- `Vector Clock` — mechanism for tracking causal dependencies between events
- `Happened-Before` — the formal causal relationship (Lamport's ←)
- `Consistency Models` — causal consistency sits between eventual and sequential
- `Lamport Clock` — logical clock; vector clocks extend Lamport clocks for causal tracking

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Causally related ops seen in causal order;│
│              │ concurrent ops: no ordering required      │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Chat/social systems; replies must follow  │
│              │ posts; collaborative editing; message feeds│
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Financial writes requiring linearisability│
│              │ (use strong consistency instead)          │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "You always receive the email before the  │
│              │  reply to it, but unrelated emails in any │
│              │  order."                                  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Vector Clock → Happened-Before → Lamport  │
│              │ Clock → Distributed Tracing               │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A distributed social network uses causal consistency for post feeds. Alice posts P1: "Going to the gym!" (VC=[1,0,0]). Bob reads P1 and replies P2: "See you there!" (VC=[1,1,0]). Carol posts P3: "Anyone for coffee?" independently (VC=[0,0,1] — no causal dependency on P1 or P2). Node N4 receives P2, then P3, then P1. In what order does N4 deliver these messages? Which messages does it buffer and why?

**Q2.** MongoDB "causal consistency" sessions use a single logical timestamp (cluster time) rather than a full vector clock. This means MongoDB's "causal consistency" actually provides a weaker guarantee than the full causal consistency model. What is the exact difference? Can you construct a scenario where MongoDB's session consistency allows a "causally inconsistent" read that a full vector-clock-based causal consistency implementation would prevent?
