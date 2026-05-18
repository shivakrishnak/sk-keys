---
id: DST-007
title: "Core Vocabulary - Nodes, Processes, Messages"
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★☆☆
depends_on: DST-001, DST-004
used_by: DST-008, DST-009, DST-010, DST-011
related: DST-003, DST-006
tags:
  - distributed
  - foundational
  - vocabulary
  - mental-model
status: complete
version: 4
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Mastery"
nav_order: 7
permalink: /technical-mastery/distributed-systems/core-vocabulary-nodes-processes-messages/
---

⚡ TL;DR - Distributed systems has precise vocabulary that
defines the computational model: nodes execute processes,
processes communicate via messages, and the combination
determines what is possible and what is provably impossible.

---

### 📋 Entry Metadata

| #007 | Category: Distributed Systems | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | The Distribution Problem, Distributed Systems Landscape | |
| **Used by:** | Node, Message Passing, Network Partition, Fault Tolerance | |
| **Related:** | The Network Is Unreliable, Real-World Distributed Systems | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Two engineers discuss a system design. One says "the process
failed." The other says "which process - the OS process or
the logical process?" One says "the node went down." The other
asks "what's the difference between a node and a server?" One
says "the message was received." The other asks "received by
the network stack or by the application?" Without precise
vocabulary, distributed systems discussions are ambiguous and
the ambiguity produces bugs.

**THE BREAKING POINT:**
The Paxos algorithm's correctness proof depends on precise
definitions of "process," "message," and "failure." A developer
who does not share these definitions cannot correctly implement
Paxos - or debug why their implementation is incorrect.

**THE INVENTION MOMENT:**
This is why distributed systems formalizes its vocabulary before
defining algorithms. The vocabulary is the foundation on which
all subsequent reasoning is built.

---

### 📘 Textbook Definition

The distributed systems computational model defines: a **node**
as an autonomous computing entity with its own state and
computation; a **process** as a sequential program executing
at a node, with local state, an input queue of messages,
and transitions based on messages received; a **message** as
the sole mechanism of communication between processes, transmitted
via a network with no shared memory access between processes;
and **failure** as a process stopping (crash failure), behaving
incorrectly (Byzantine failure), or becoming slow (partial failure).
These definitions form the formal model within which impossibility
results (FLP, CAP) and algorithm correctness proofs are stated.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Nodes are machines, processes are programs running on machines,
and messages are the only way processes communicate.

**One analogy:**
> Nodes are office buildings. Processes are employees working
> in those buildings. Messages are letters sent between
> employees. An employee can only know what they are told
> in letters - they cannot peek into another building's room.
> A letter might get lost. An employee might stop working
> (crash). An employee might lie (Byzantine failure).

**One insight:**
The "no shared memory" constraint is what makes distributed
systems hard. On a single machine, shared memory lets two
threads instantly see each other's writes. Across machines,
the only way to share information is a message - which may
be lost, delayed, or arrive out of order. This single
constraint is responsible for the CAP theorem, the FLP
impossibility result, and every coordination algorithm.

---

### 🔩 First Principles Explanation

**KEY VOCABULARY:**

```
┌───────────────────────────────────────────────────────┐
│  DISTRIBUTED SYSTEMS CORE VOCABULARY                  │
├───────────────────────────────────────────────────────┤
│  NODE         A physical or virtual machine.          │
│               Has CPU, memory, persistent storage.    │
│               May host one or more processes.         │
├───────────────────────────────────────────────────────┤
│  PROCESS      A sequential program at a node.         │
│               Has local state only.                   │
│               Transitions: receive message ->         │
│                 update state -> send messages.        │
├───────────────────────────────────────────────────────┤
│  MESSAGE      Data sent from one process to another.  │
│               The ONLY way processes communicate.     │
│               May be: lost, delayed, duplicated,      │
│               reordered (depending on channel model). │
├───────────────────────────────────────────────────────┤
│  CHANNEL      The network link between processes.     │
│               Reliable channel: messages arrive,      │
│                 possibly reordered, never lost.       │
│               Fair-loss channel: messages lost with   │
│                 non-zero probability.                 │
│               Arbitrary channel: Byzantine behavior.  │
├───────────────────────────────────────────────────────┤
│  CRASH FAILURE  Process stops and sends no more msgs  │
│                 ("fail-stop" - detectable by silence) │
├───────────────────────────────────────────────────────┤
│  BYZANTINE    Process behaves arbitrarily: sends      │
│ FAILURE       wrong values, selectively ignores msgs, │
│               or actively lies. Harder to tolerate.   │
├───────────────────────────────────────────────────────┤
│  PARTIAL FAIL Process is slow, not stopped. Hardest   │
│               to handle - indistinguishable from      │
│               Byzantine in message-passing model.    │
└───────────────────────────────────────────────────────┘
```

**THE NODE vs PROCESS DISTINCTION:**
These terms are often used interchangeably in informal
discussion but have distinct formal meanings. A node is a
physical or virtual machine. A process is a program instance.
Multiple processes can run on one node (e.g., a Kafka broker
and ZooKeeper on the same VM). The distinction matters because:
- A node failure takes down all processes on it
- A process crash does not take down the node
- Replication is per-process, not per-node

**THE MESSAGE MODEL - WHY IT MATTERS:**
The message model is not an implementation detail - it is
a formal model that determines what algorithms are possible.
Shared memory (single machine) admits atomic test-and-set
operations. Message passing (distributed systems) requires
multi-round protocols to achieve the same effect. This is
why distributed locking is fundamentally harder than
single-machine locking.

---

### 🧠 Mental Model / Analogy

> Imagine a spy network with agents in different cities (nodes).
> Each agent has their own notes (local state) and can only
> share information by sending couriers (messages). Couriers
> can be intercepted (message loss), delayed by weather
> (message delay), or send copies of the same message twice
> (duplication). An agent who stops responding might be
> captured (crash failure) or might be a double agent sending
> false information (Byzantine failure). The spy master must
> design protocols that work correctly even when agents go
> silent or lie.

Mapping:
- "Agents in different cities" - processes at different nodes
- "Agent's notes" - local process state
- "Couriers" - messages
- "Intercepted courier" - message loss
- "Delayed by weather" - message delay
- "Captured agent" - crash failure
- "Double agent" - Byzantine failure

**Where this analogy breaks down:** Spy networks tolerate
uncertainty by giving agents local authority to act. Many
distributed systems instead require waiting for consensus -
a constraint that spy networks avoid by design.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Nodes are computers. Processes are programs running on them.
Messages are how programs on different computers communicate,
since they cannot directly access each other's memory.

**Level 2 - How to use it (junior developer):**
In your application: your server process is one process, your
database server is another process (potentially on another node).
They communicate via messages (SQL queries over TCP, HTTP
requests). When you deploy two instances of your server behind
a load balancer, you have two processes - they share no state
unless it is stored in the shared database.

**Level 3 - How it works (mid-level engineer):**
The formal distinction between crash failure and Byzantine
failure determines which algorithms are needed. Systems that
assume only crash failures (the majority of commercial
distributed systems) use simpler algorithms (Raft, ZAB).
Systems that must tolerate Byzantine failures (public
blockchains, military/avionics) use PBFT or similar protocols
with dramatically higher message complexity: O(N^2) messages
per consensus round vs O(N) for crash-only protocols.

**Level 4 - Why it was designed this way (senior/staff):**
The message-passing model was chosen for formal distributed
systems theory precisely because it is the most general model:
any algorithm designed for message passing can also run on
shared memory (by simulating messages with shared variables).
The reverse is not true - shared-memory algorithms often cannot
be directly ported to message-passing without fundamental
redesign. This generality makes the message-passing model the
correct abstraction for reasoning about what is possible.

**Level 5 - Mastery (distinguished engineer):**
The boundaries of the formal model reveal where practical
systems violate it. Most production distributed systems are
not purely asynchronous message-passing systems - they have
shared infrastructure (a ZooKeeper ensemble, a shared NFS,
a shared DNS server) that introduces implicit shared state.
A distinguished engineer identifies these hidden shared-state
points and evaluates their failure modes explicitly, because
the formal proofs do not apply to systems with any shared
state, and real systems always have some.

---

### ⚙️ Why It Holds True (Formal Basis)

The FLP impossibility theorem is stated in terms of this
exact vocabulary: "In an asynchronous system where processes
communicate only by message passing and where one process
may fail (crash), no deterministic algorithm exists that
guarantees consensus." Changing any single term in that
sentence changes the result:
- "Asynchronous" → "Partially synchronous": solvable (Raft, Paxos)
- "May fail" → "Cannot fail": solvable (trivial agreement)
- "Crash failure" → "Byzantine failure": still impossible
  in async model, solvable in synchronous model (PBFT)
- "Deterministic" → "Randomized": solvable with probability 1

Understanding the vocabulary is not academic - it tells you
exactly which conditions make which algorithms possible.

---

### ⚖️ Comparison Table

| Failure Model | Real-World Example | Algorithms Needed | Message Complexity |
|---|---|---|---|
| Crash-stop | Server crash, process killed | Raft, Paxos, ZAB | O(N) per round |
| Crash-recovery | Server restarts with disk | Viewstamped Replication | O(N) + state transfer |
| **Byzantine** | Malicious node, hardware bug | PBFT, Tendermint | O(N^2) per round |
| Partial failure | Slow GC, CPU throttle | Treated as crash with timeout | Same as crash |

**How to choose:**
Assume crash-stop for services you control. Assume Byzantine
only when you cannot trust the nodes (public blockchain,
multi-party computation). Partial failures are typically
handled by treating slow = failed with a timeout.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Node and server are the same thing" | A node is a logical participant in the distributed system. A server is a physical or virtual machine. One server can host multiple nodes (e.g., in a test cluster). |
| "Message loss means packet loss" | In the formal model, message loss means the application message was not delivered - which can happen even if TCP delivered the bytes (e.g., the application crashed after receiving but before processing). |
| "Crash failure is the worst kind" | Byzantine failure is harder than crash failure. A crashed process sends no messages. A Byzantine process sends incorrect messages that look valid - they actively mislead other processes. |
| "All distributed systems are asynchronous" | Real systems are partially synchronous: they have bounded message delays in normal operation. Pure asynchrony is a theoretical worst case for proving impossibility results. |

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `The Distribution Problem` - Why the formal model exists
- `Distributed Systems Landscape` - Where this vocabulary
  fits in the overall field

**Builds On This (learn these next):**
- `Node` - Detailed treatment of the node concept
- `Message Passing` - Detailed treatment of the message
  communication model
- `Fault Tolerance` - How systems survive process failures
- `Byzantine Fault Tolerance` - Algorithms for the hardest
  failure model

**Alternatives / Comparisons:**
- `Shared Memory (Concurrent Systems)` - The alternative
  communication model for single-machine concurrency,
  where atomic operations replace message passing

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ The precise vocabulary: nodes, processes,│
│              │ messages, channels, and failure types    │
├──────────────┼──────────────────────────────────────────┤
│ PROBLEM IT   │ Ambiguous language produces ambiguous cod│
│ SOLVES       │ and incorrect algorithm implementations  │
├──────────────┼──────────────────────────────────────────┤
│ KEY INSIGHT  │ "No shared memory" between processes is  │
│              │ the single constraint that makes all othe│
│              │ distributed systems challenges necessary │
├──────────────┼──────────────────────────────────────────┤
│ USE WHEN     │ Discussing, designing, or debugging any  │
│              │ distributed system                       │
├──────────────┼──────────────────────────────────────────┤
│ AVOID WHEN   │ N/A - vocabulary is always needed        │
├──────────────┼──────────────────────────────────────────┤
│ ANTI-PATTERN │ Using "node" and "process" interchangeabl│
│              │ when hosting multiple processes per node │
├──────────────┼──────────────────────────────────────────┤
│ TRADE-OFF    │ Formal precision vs informal speed;      │
│              │ use precision when correctness matters   │
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "No shared memory forces message passing;│
│              │  message passing forces all the hard work│
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Message Passing → Network Partition →    │
│              │ Fault Tolerance                          │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Nodes are machines, processes are programs. One node
   can host multiple processes.
2. Messages are the only communication - no shared memory
   exists between processes on different nodes.
3. Crash failure (process stops) is different from Byzantine
   failure (process lies) - they require different algorithms.

**Interview one-liner:**
"In the formal distributed systems model: a node is a machine,
a process is a program at that machine with only local state,
and the only communication is messages. This 'no shared memory'
constraint is why consensus is so hard - you cannot just read
a shared variable to know what others think."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
The boundary of what is shared determines the coordination
model required. No shared state: only message passing is possible.
Shared memory: atomic operations are possible. Shared nothing:
true independence is possible. Every system has some sharing;
understanding exactly what is shared and what is not determines
the correct algorithm to use.

**Where else this pattern appears:**
- **Microservices** - Services with separate databases (shared-
  nothing) are the closest to the formal model. Services that
  share a database are in a hybrid model that inherits some
  properties of both shared-memory and message-passing systems.
- **Programming languages** - Erlang/Elixir's actor model
  directly implements the formal distributed systems process
  model at the language level: every "process" has isolated
  state and communicates only via messages.

**Industry applications:**
- **Blockchain** - Public blockchains assume Byzantine failures
  (any node may be malicious) and use Byzantine fault-tolerant
  consensus. This is why their consensus algorithms (Nakamoto
  consensus, PBFT variants) require much more communication
  than crash-only systems like Raft.

---

### 💡 The Surprising Truth

The formal model of distributed systems (nodes communicating
via messages with no shared memory) was not invented for
distributed computers - it was first formalized to model
concurrent programs on a single machine. Tony Hoare's
Communicating Sequential Processes (CSP, 1978) and Robin
Milner's Calculus of Communicating Systems (CCS, 1980) described
single-machine concurrency using message passing. The distributed
systems community later adopted this model because it was more
general than shared memory - it could describe both single-
machine and multi-machine systems. The vocabulary you use to
reason about a Kafka consumer cluster is the same vocabulary
invented to reason about threads on a single CPU.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. [EXPLAIN] Given a specific real-world system (three-tier
   web app, Kafka cluster, ZooKeeper ensemble), identify each
   node, each process, each communication channel, and classify
   the failure model the system assumes.
2. [DEBUG] A "node" is described as "down" in an alert. Identify
   the three possible meanings (node hardware failure, process
   crash, process slowdown) and explain what diagnostic approach
   differs for each.
3. [DECIDE] A system must tolerate Byzantine failures from
   untrusted nodes. Explain what algorithm class is needed
   and why crash-only algorithms (Raft, Paxos) are insufficient.
4. [BUILD] Write the formal state transition for a simple
   process in the message-passing model: given current state S
   and incoming message M, produce next state S' and outgoing
   messages.
5. [EXTEND] Map the formal vocabulary (node, process, message,
   crash failure, Byzantine failure) to a non-computing domain
   such as an organization's decision-making process.

---

### 🧠 Think About This Before We Continue

**Q1.** A Kubernetes pod runs three containers, and a Kubernetes
node (VM) hosts 10 pods. Using the distributed systems
vocabulary, how many nodes and processes are in this picture?
What happens when the VM's OS crashes vs when one container
crashes?
*Hint: Think about which "node" concept maps to the VM and
which to the pod or container in different contexts.*

**Q2.** A system assumes crash-stop failures. A bug causes
a process to enter an infinite loop and stop responding to
messages without actually crashing. From the perspective of
other processes, how does this look - and why does it matter
that "partial failure" is formally treated as crash in many
algorithms?
*Hint: Think about how failure detectors use timeouts and
what they declare.*

**Q3.** Design a two-process protocol where process A sends
a value to process B, and B must confirm receipt. In a crash-
stop model (messages can be lost, B can crash), what is the
minimum number of message exchanges needed to guarantee
A knows B received the value - and is this actually achievable?
*Hint: Consider the Two Generals Problem and what it says
about this question.*
