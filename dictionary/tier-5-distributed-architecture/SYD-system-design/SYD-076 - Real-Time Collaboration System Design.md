---
id: SYD-076
title: Real-Time Collaboration System Design
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★★
depends_on: SYD-006, SYD-025
used_by: ""
related: SYD-006, SYD-025, SYD-057, SYD-013, SYD-072
tags:
  - architecture
  - collaboration
  - real-time
  - websocket
  - design
  - advanced
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 76
permalink: /syd/real-time-collaboration-system-design/
---

# SYD-076 - Real-Time Collaboration System Design

⚡ TL;DR - Real-time collaboration (Google Docs, Figma,
collaborative code editors) lets multiple users edit
the same document simultaneously. The core algorithm
challenge: two users edit the same location concurrently,
and both must see a coherent result. Two approaches:
(1) Operational Transformation (OT) - operations are
transformed against concurrent operations to ensure
convergence; (2) CRDT (Conflict-free Replicated Data
Type) - data structure designed so any merge order
produces the same result. Infrastructure: WebSockets
for real-time bidirectional communication, operational
log for edit history, presence awareness (who is
currently viewing/editing). Operational complexity
is high; most teams use a library (Yjs, Automerge,
ShareDB) rather than implementing from scratch.

| #076 | Category: System Design | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | WebSocket Design, Pub/Sub Messaging | |
| **Related:** | WebSocket Design, Pub/Sub Messaging, Event-Driven Architecture, Rate Limiter Design, File Storage System Design | |

---

### 🔥 The Problem This Solves

Two users, Alice and Bob, both have Google Doc open.
Alice types "Hello" at position 0.
Bob simultaneously types "World" at position 0.
Both see each other's edits in real time.
Without a convergence algorithm: the document might
show "HWorldello" for Alice and "WorldHello" for Bob
(inconsistent state). With Operational Transformation:
both users converge to the same document state, typically
"HelloWorld" or "WorldHello" (deterministically chosen
order), regardless of which edit arrived first at which
client.

---

### 📘 Textbook Definition

**Real-time collaboration:** Multiple users simultaneously
editing a shared document with changes immediately
visible to all participants, while maintaining a
consistent document state.

**Operational Transformation (OT):** An algorithm that
transforms an operation based on concurrent operations
that have already been applied, such that the result
is commutative: applying operations in any order
produces the same document state.

**CRDT (Conflict-free Replicated Data Type):** A data
structure designed so that concurrent updates can be
merged automatically without conflict. Any merge order
produces the same result (strong eventual consistency).

**Presence:** Awareness of who is currently viewing or
editing a document, and what position their cursor is at.
"Alice and Bob are here." "Alice is editing paragraph 2."

**Operational log:** An append-only record of all edit
operations (insertions, deletions, formatting changes)
applied to a document. The document state can be
reconstructed by replaying all operations from the log.

**Version vector:** A set of counters per-user tracking
which operations each user has seen. Used to detect
concurrent operations and determine which operations
to transform against each other.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
WebSockets carry operations (not document state).
OT or CRDT ensures all clients converge to the same
state regardless of operation arrival order.

**One analogy:**
> Two people editing the same whiteboard via phone:
>
> Without OT: Alice says "write Hello." Bob says
> "write World at the start." Alice's whiteboard:
> "HelloWorld". Bob's whiteboard: "WorldHello".
> Different results. Inconsistent collaboration.
>
> With OT: both edits are broadcast. Alice's client
> transforms Bob's "insert at position 0" to
> "insert at position 5" (after "Hello" which was
> already inserted). Both whiteboards converge to
> the same state: deterministic merge.

**One insight:**
The core insight of OT is that an operation's intent
(insert "Hello" after the cursor) must be preserved
when transforming against a concurrent operation.
"Insert X at position 5" becomes "Insert X at position 10"
if a concurrent insert of 5 characters happened at
position 0 first. The position shifts but the intent
is preserved: X goes after the text that was at
position 5 when the user made the edit.

---

### 🔩 First Principles Explanation

**OPERATIONAL TRANSFORMATION (OT):**
```
Document: "ABCDE"
Alice: insert "X" at position 2 → "ABXCDE"
Bob:   insert "Y" at position 3 → "ABCYDE"  (concurrent)

Without OT (both apply without transformation):
  Alice receives Bob's op: insert "Y" at position 3.
  Alice's document: "ABXCYDE" → X inserted at 2, Y at 3.
  
  Bob receives Alice's op: insert "X" at position 2.
  Bob's document: "ABXCYDE" → X at 2, Y at 3+1=4? No.
  Bob applied Y first at 3 → "ABCYDE"
  Now receives X at 2 → "ABXCYDE"?
  
  If Bob applies ops in different order: different result.
  Document diverges. Inconsistent state.

With OT:
  Central server orders all operations: 
  Op1 = Alice: insert "X" at position 2
  Op2 = Bob:   insert "Y" at position 3
  
  Server sends both to all clients:
  - For Alice: already has Op1. Receives transformed Op2:
    transform(insert Y at 3, insert X at 2)
    = insert Y at 4 (shifted by +1 because X is at 2 < 3)
  - For Bob: receives Op1, applies it, then applies Op2:
    After Op1: "ABXCDE"
    Op2 was against "ABCDE" at position 3.
    Transform Op2 against Op1: position 3+1=4.
    Apply: "ABXCYDE" → wait, ABXCDE then insert Y at 4:
    "ABXCYDE"
  
  Both clients: "ABXCYDE". Converged!

Transform function (for insert-insert):
  transform(op_a, op_b):
    if op_b.position < op_a.position:
      return op_a with position += length(op_b.insert)
    else:
      return op_a unchanged
```

**CRDT APPROACH (Yjs):**
```
CRDT: each character has a unique ID (site_id, clock).
Character ordering: deterministic by ID.

Alice's insert: character X with ID (Alice, 3) at 
                after character (doc, 2).
Bob's insert:   character Y with ID (Bob, 3) at
                after character (doc, 3).

Both clients receive both operations.
Merge: each character placed by its unique anchor.
Order of application doesn't matter: result is same.

Yjs uses a CRDT called YATA (Yet Another Transformation
Approach). Sequences of characters are represented as
linked lists with unique IDs. Insertions are idempotent:
inserting the same character twice (same ID) is a no-op.

Pros over OT:
  No need for a central server to order operations.
  Peer-to-peer collaboration is possible.
  Simpler to reason about (no transformation needed).
  
Cons:
  Tombstones: deleted characters kept as markers.
  Memory grows over time (tombstones accumulate).
  Complex to implement correctly (especially for
  rich-text with formatting).
  
Libraries: Yjs, Automerge, diamond-types.
```

**INFRASTRUCTURE ARCHITECTURE:**
```
WebSocket Connection:
  Client → WebSocket server (long-lived connection).
  Client sends: {op: insert, pos: 3, text: "X", v: 5}
  Server broadcasts to all other clients for same doc.
  
Connection management:
  10M users. Each has 1 WebSocket connection.
  WebSocket servers: stateful (connections pinned).
  A document's collaborators are spread across servers.
  Pub/Sub (Redis) to broadcast across servers:
  
  Client1 (WS server 1) → op arrives
  WS server 1 → publish to Redis channel "doc:123"
  WS server 2 → subscribed to "doc:123"
                → delivers op to Client2, Client3
  
Document state (source of truth):
  Operations DB: append-only log of all ops.
  Snapshot: periodically computed current state.
  
  Document state at any time:
  = snapshot + replay of ops since snapshot.
  
  Compaction: after N ops, compute new snapshot.
  Prune old ops (or keep for version history).

Presence (cursor tracking):
  Ephemeral data: "Alice's cursor is at position 45."
  Short-lived (disappears when user disconnects).
  Storage: Redis (TTL = connection lifetime).
  Broadcast: same pub/sub as operations.
```

**CONFLICT RESOLUTION FOR RICH TEXT:**
```
Text conflicts are simple (insert/delete).
Rich text (bold, italics, headers) is complex:

Alice: make characters 5-10 bold.
Bob:   make characters 8-15 italic.

OT must handle: bold and italic both apply to 8-10.
Intent: characters 8-10 should be bold AND italic.
Most OT implementations handle formatting as separate
operations (formatting and text are independent).

Even harder: delete a character that's being formatted.
Alice: delete character 7.
Bob: apply bold to characters 5-10 (including 7).

OT must transform Bob's range:
Characters 5-6, 8-10 are bold (character 7 deleted).

Google Docs uses OT. Quill.js (Delta format) uses OT.
Notion uses operational transforms with a custom format.
Figma uses CRDTs for design element merges.
```

---

### 🧪 Thought Experiment

**OT vs. CRDT for Different Use Cases**

Text document (Google Docs):
  OT: well-suited. Linear text has clear position
  semantics. Central server orders operations.
  Proven at scale (Google uses OT in Google Docs).
  
Code editor (VS Code Live Share):
  OT with language server integration.
  Must handle syntax-aware merges.
  
Design tool (Figma):
  CRDT: design elements are objects (not linear text).
  Objects have UUIDs. Concurrent edits to different
  objects: always non-conflicting (different IDs).
  Concurrent edits to same object: last-write-wins for
  each property (position, color, size = independent).
  
Spreadsheet (Google Sheets):
  Hybrid: cells are independent (CRDT-like per cell).
  Formulas: re-computed on merge.
  Concurrent formula and value edit to same cell:
  OT or last-write-wins (with notification to users).

Conclusion: there is no universal best choice.
Text → OT. Structured objects → CRDT.
Most collaborative editors use existing libraries
rather than custom implementations.

---

### 🧠 Mental Model / Analogy

> Real-time collaboration is like editing a shared
> recipe card with a friend over the phone:
>
> Without algorithm: both make changes simultaneously.
> When you compare cards later: different, inconsistent.
>
> With OT (central server): there's an arbitrator
> (the server) who orders all changes. Everyone gets
> the same ordered change list. Each applies them
> in the same order. Cards always match.
>
> With CRDT (peer-to-peer): each ingredient has a
> unique sticky note. New ingredients are new notes.
> Everyone can add notes simultaneously. When you
> compare cards: merge all the sticky notes. Same
> result regardless of who goes first.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Real-time collaboration means multiple people can edit
the same document simultaneously, like Google Docs. The
challenge: when two people type at the same time, the
system must decide how to merge their changes so
everyone sees the same final document.

**Level 2 - How to use it (junior developer):**
Use a library: Yjs + WebSocket, Automerge, or ShareDB.
These handle the hard CRDT/OT algorithms for you. Your
job: manage WebSocket connections, propagate operations
between clients, persist the operation log to a database.
Track user presence (cursor position) using Redis with
short TTL.

**Level 3 - How it works (mid-level engineer):**
OT: operations include version/vector clock. Server
orders operations. Client transforms incoming ops against
local concurrent ops before applying. Central server
is the arbiter of operation order. CRDT (Yjs): each
character has a unique anchor. Merging is commutative
(order doesn't matter). Pub/Sub (Redis) for broadcasting
ops across WebSocket servers. Operation log: append-only,
compacted periodically into snapshots. Presence: Redis
with TTL per user per document.

**Level 4 - Why it was designed this way (senior/staff):**
Google chose OT for Google Docs because: (1) in 2006,
when they built it, CRDT theory was not yet mature for
rich text; (2) OT gives strong consistency guarantees
with a central server - simpler to reason about at scale;
(3) Google had a central server infrastructure (not
peer-to-peer). Figma chose CRDTs because design elements
(objects with properties) are more naturally modeled as
independent items with unique IDs than linear text. The
choice of OT vs. CRDT is fundamentally a data model
decision: linear sequences → OT is well-understood;
graph/object structures → CRDTs are more natural.

**Level 5 - Mastery (distinguished engineer):**
Martin Kleppmann's research (2022) on the Diamond Types
CRDT (a successor to Automerge) achieved O(N) time for
merging concurrent insertions at the same position
(compared to Yjs's O(N log N) and previous CRDTs' O(N^2)).
The key insight: if you maintain each client's state
as an interleaved timeline of operations, detecting
concurrent insertions becomes a linear scan instead of
a quadratic comparison. This matters at scale: Figma's
collaborative canvas with thousands of concurrent
element insertions per second. The practical implication
for system design: the choice between OT and CRDT is
often secondary to the choice of which library to use
and how to scale the operational log storage and
broadcast infrastructure.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ REAL-TIME COLLABORATION FLOW                        │
│                                                      │
│ User A (WS server 1) types "X" at position 3:     │
│  Client: generate op {type: insert, pos: 3,       │
│          text: "X", clock: 5}                     │
│  Apply op locally (optimistic update)             │
│  Send to WS server 1                             │
│                                                      │
│ WS server 1:                                        │
│  Assign server-side sequence number                │
│  Persist op to operation_log DB                   │
│  Publish to Redis channel: doc:123                │
│                                                      │
│ Redis pub/sub → WS server 2, WS server 3:          │
│  Each broadcasts to their connected clients        │
│                                                      │
│ User B (WS server 2) receives op:                  │
│  Transform against any concurrent local ops       │
│  Apply to local document                          │
│                                                      │
│ Presence (cursor tracking):                         │
│  Each client sends cursor position every 200ms     │
│  Redis: SETEX cursor:doc:123:userA 30 "pos:42"   │
│  Broadcast: all collaborators see cursor move     │
│                                                      │
│ Document snapshot (compaction):                    │
│  Every 1,000 ops: compute snapshot                │
│  Store: snapshots DB                              │
│  Prune: ops older than current snapshot           │
│         (or keep for version history)             │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Yjs collaborative editor (Node.js)**
```javascript
// Server-side: Yjs with WebSocket using y-websocket
const Y = require('yjs')
const { WebsocketProvider } = require('y-websocket')
const { setupWSConnection } = require('y-websocket/bin/utils')
const http = require('http')
const WebSocket = require('ws')

// Create HTTP and WebSocket server
const server = http.createServer()
const wss = new WebSocket.Server({ server })

// y-websocket handles: connection management,
// CRDT sync between clients, document persistence.
// You provide: getPersistence (how to store the doc).

const persistence = {
  provider: 'postgres',
  bindState: async (docName, ydoc) => {
    // Load document state from DB on first connection
    const saved = await db.query(
      'SELECT state FROM docs WHERE name = $1', [docName])
    if (saved.rows.length > 0) {
      // Restore Y.Doc state from saved binary
      const update = Buffer.from(
        saved.rows[0].state, 'base64')
      Y.applyUpdate(ydoc, update)
    }
  },
  writeState: async (docName, ydoc) => {
    // Persist document state to DB
    const state = Y.encodeStateAsUpdate(ydoc)
    await db.query(
      'INSERT INTO docs (name, state) VALUES ($1, $2) '
      + 'ON CONFLICT (name) DO UPDATE SET state=$2',
      [docName, Buffer.from(state).toString('base64')]
    )
  }
}

wss.on('connection', (ws, req) => {
  // setupWSConnection: handles CRDT sync automatically
  setupWSConnection(ws, req, { persistence })
})

server.listen(3000)

// Client-side: React + Yjs + Quill editor
// (React component simplified)
/*
import * as Y from 'yjs'
import { WebsocketProvider } from 'y-websocket'
import { QuillBinding } from 'y-quill'
import Quill from 'quill'

const ydoc = new Y.Doc()
const provider = new WebsocketProvider(
  'ws://server:3000', 'my-document', ydoc)
const ytext = ydoc.getText('quill')  // Shared text type

const quill = new Quill('#editor', { theme: 'snow' })
const binding = new QuillBinding(ytext, quill,
  provider.awareness)  // Awareness = presence tracking

// That's it. Y.js handles all OT/CRDT internally.
// Presence: cursor positions shared via awareness.
*/
```

**Example 2 - Simple OT implementation (educational)**
```python
from dataclasses import dataclass
from typing import List, Literal

@dataclass
class InsertOp:
    type: Literal["insert"]
    position: int
    text: str

@dataclass
class DeleteOp:
    type: Literal["delete"]
    position: int
    length: int

def transform_insert_against_insert(
        op: InsertOp, prev: InsertOp) -> InsertOp:
    """
    Transform op to apply after prev was already applied.
    If prev inserted before op's position: shift right.
    """
    if prev.position <= op.position:
        return InsertOp(
            type="insert",
            position=op.position + len(prev.text),
            text=op.text
        )
    return op  # prev was after op's position: no change

def apply_op(document: str, op) -> str:
    """Apply an operation to a document."""
    if op.type == "insert":
        return (document[:op.position]
                + op.text
                + document[op.position:])
    elif op.type == "delete":
        return (document[:op.position]
                + document[op.position + op.length:])
    return document

class SimpleOTServer:
    """
    Minimal OT server: orders ops and transforms
    concurrent ops for each client.
    
    Production: use ShareDB or similar library.
    """
    def __init__(self, initial: str = ""):
        self.document = initial
        self.history: List = []  # All applied ops
    
    def apply(self, op, client_version: int) -> tuple:
        """
        Apply op, transforming against ops since
        client_version.
        
        Returns: (transformed_op, server_version)
        """
        # Transform op against all ops the client
        # hasn't seen yet
        transformed_op = op
        for past_op in self.history[client_version:]:
            if (op.type == "insert"
                    and past_op.type == "insert"):
                transformed_op = (
                    transform_insert_against_insert(
                        transformed_op, past_op))
            # ... handle insert-delete, delete-insert, etc.
        
        # Apply transformed op to server document
        self.document = apply_op(
            self.document, transformed_op)
        self.history.append(transformed_op)
        
        return transformed_op, len(self.history)

# DEMONSTRATION:
server = SimpleOTServer("ABCDE")

# Alice: insert "X" at position 2 (at version 0)
# Bob:   insert "Y" at position 3 (at version 0)
alice_op = InsertOp("insert", 2, "X")
bob_op = InsertOp("insert", 3, "Y")

# Server applies Alice's op first:
xf_alice, v1 = server.apply(alice_op, client_version=0)
print(f"After Alice: {server.document}")  # ABXCDE

# Server receives Bob's op (still at client version 0):
# Must transform against [alice_op]:
xf_bob, v2 = server.apply(bob_op, client_version=0)
print(f"After Bob:   {server.document}")  # ABXCYDE

# Both clients converge to: ABXCYDE
```

**Example 3 - Presence with Redis**
```python
import redis
import json

r = redis.Redis(host='redis.internal',
                decode_responses=True)

CURSOR_TTL = 30  # seconds

def update_presence(doc_id: str, user_id: int,
                    position: int, selection: dict):
    """Update user's cursor position (ephemeral state)."""
    key = f"presence:{doc_id}:{user_id}"
    data = {
        "user_id": user_id,
        "position": position,
        "selection": selection,
        "updated_at": "now"
    }
    # Expire after 30s (cleared on disconnect/inactivity)
    r.setex(key, CURSOR_TTL, json.dumps(data))

def get_document_presence(doc_id: str) -> list:
    """Get all active users in a document."""
    pattern = f"presence:{doc_id}:*"
    keys = r.scan_iter(pattern)
    presence = []
    for key in keys:
        data = r.get(key)
        if data:
            presence.append(json.loads(data))
    return presence

def on_user_disconnect(doc_id: str, user_id: int):
    """Remove presence on disconnect."""
    r.delete(f"presence:{doc_id}:{user_id}")
```

---

### ⚖️ Comparison Table

| Approach | Consistency | P2P Support | Complexity | Best For |
|---|---|---|---|---|
| **OT (server-ordered)** | Strong (all converge) | No (central server) | High | Linear text (Google Docs) |
| **CRDT (Yjs)** | Strong eventual | Yes | Medium (library) | Rich objects, offline-first |
| **Last-write-wins** | Weak (data loss) | Yes | Low | Simple properties (color) |
| **Lock-based** | Strong (exclusive) | No | Low | Non-collaborative editing |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| OT and CRDT are interchangeable | OT requires a central server to order operations. CRDT is peer-to-peer (no central ordering needed). OT is well-studied for linear text (Google Docs uses it). CRDT is better for structured data (objects, trees) and offline-first applications. Choosing between them depends on your data model and infrastructure constraints. Most teams should use an existing library rather than implementing either from scratch. |
| Real-time collaboration needs a single global server | WebSocket connections should be handled by multiple servers for availability and scale. Use Redis Pub/Sub to broadcast operations across WebSocket servers. Each WebSocket server handles its connected clients; Redis propagates operations between servers. A document's operations still have a logical order (assigned by the server that first receives each op), but the infrastructure is distributed. |
| Presence tracking is trivial | Presence (cursor positions, user awareness) creates high-frequency updates: a user's cursor moves on every keystroke. At 100 active users in one document, each sending cursor updates 10 times per second: 1,000 broadcasts per second just for presence. Use sampling (send every 200ms, not every keystroke), debouncing, and short TTLs in Redis. Also: presence data is ephemeral and lossy - it's acceptable to miss a cursor update or two. |

---

### 🚨 Failure Modes & Diagnosis

**Operation Log Out of Sync: Document Divergence**

**Symptom:**
User A and User B see different document content.
Editing continues normally for both, but their
documents are different. "Why does Alice's document
say X but mine says Y? We're on the same document."

**Root Cause:**
An operation was lost (not persisted to the op log due
to a server crash or network error) and not retried.
Subsequent operations from other users were transformed
against the wrong base state. Documents diverged.

**Diagnosis and Fix:**
```python
# Prevention 1: acknowledge-retry protocol
# Client does not consider an op "applied" until ACK.

class ReliableOpSender:
    def __init__(self, ws, doc_id, user_id):
        self.ws = ws
        self.pending_ops = {}
        
    def send_op(self, op: dict) -> str:
        op_id = str(uuid.uuid4())
        op['op_id'] = op_id
        
        # Track as pending until ACK received
        self.pending_ops[op_id] = op
        
        self.ws.send(json.dumps(op))
        
        # Schedule retry if no ACK in 3s
        asyncio.get_event_loop().call_later(
            3.0, self._retry_if_pending, op_id)
        
        return op_id
    
    def on_ack(self, op_id: str):
        """Called when server ACKs the operation."""
        self.pending_ops.pop(op_id, None)
    
    def _retry_if_pending(self, op_id: str):
        if op_id in self.pending_ops:
            # Re-send the unacknowledged op
            self.ws.send(json.dumps(
                self.pending_ops[op_id]))

# Prevention 2: client version vector reconciliation
# Periodically, client sends its version vector.
# Server checks if any ops are missing.
# Server re-sends missing ops.
# This detects and recovers from divergence.

# Prevention 3: document state hash check
# Hourly: compute SHA-256 of document state.
# Broadcast to all clients.
# Client compares its local hash.
# Mismatch: trigger full document reload.
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `WebSocket Design` - real-time collaboration requires
  persistent bidirectional connections (WebSocket)
- `Pub/Sub Messaging` - broadcasting operations across
  WebSocket servers uses Redis Pub/Sub

**Builds On This (learn these next):**
- `Event-Driven Architecture` - operations are events
  flowing through the system
- `Rate Limiter Design` - prevent abuse: one user
  sending thousands of ops per second
- `File Storage System Design` - document versioning
  and history storage patterns apply here

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ OT          │ Server orders ops. Transform against       │
│             │ concurrent ops. All clients converge.    │
├─────────────┼──────────────────────────────────────────  │
│ CRDT        │ Unique IDs per character/element.         │
│             │ Any merge order = same result.           │
│             │ P2P-friendly. Use Yjs/Automerge.        │
├─────────────┼──────────────────────────────────────────  │
│ INFRA       │ WebSocket → Redis Pub/Sub → broadcast.   │
│             │ Op log: append-only. Compaction: snapshots│
├─────────────┼──────────────────────────────────────────  │
│ PRESENCE    │ Redis SETEX with TTL. 200ms debounce.    │
│             │ Ephemeral: OK to lose cursor updates.   │
├─────────────┼──────────────────────────────────────────  │
│ RELIABILITY │ ACK-retry on ops. Server re-sends missed.│
│             │ Hash check hourly for divergence detect.│
├─────────────┼──────────────────────────────────────────  │
│ ONE-LINER   │ "Use Yjs or ShareDB. Don't implement   │
│             │  OT/CRDT from scratch."                │
├─────────────┼──────────────────────────────────────────  │
│ NEXT        │ Global Key-Value Store Design            │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Use a library: Yjs (CRDT), ShareDB (OT), or Automerge.
   Implementing OT or CRDT correctly from scratch is
   extremely difficult. Even Google's OT implementation
   had bugs. Production-ready libraries have been
   battle-tested across millions of users.
2. Infrastructure: WebSocket connections (stateful,
   long-lived) + Redis Pub/Sub to broadcast operations
   across multiple WebSocket servers. All clients
   subscribed to a document receive all operations
   regardless of which server they connected to.
3. Operation acknowledgment: clients must retry unacknowledged
   operations (ACK-retry protocol). A single lost operation
   causes document divergence that's hard to recover from.
   The server must assign a global sequence number to
   each operation and clients must track which sequence
   they've received.

**Interview one-liner:**
"Real-time collaboration: WebSocket connections + Redis Pub/Sub to broadcast ops
across servers. Algorithm: OT (server-ordered ops, transform position against
concurrent ops, all converge) or CRDT (unique IDs per character, any merge order
= same result, P2P-friendly). In practice: use Yjs (CRDT) or ShareDB (OT). Op log:
append-only, compacted into snapshots every 1K ops. Presence: Redis SETEX TTL=30s
per cursor position, debounced to 200ms. Reliability: ACK-retry protocol (client
retries until server ACKs); periodic state hash check between server and clients
to detect/recover from divergence."
