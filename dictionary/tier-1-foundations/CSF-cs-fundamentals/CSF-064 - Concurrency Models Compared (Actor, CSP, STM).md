---
id: CSF-068
title: Concurrency Models Compared (Actor, CSP, STM)
category: CS Fundamentals - Paradigms
tier: tier-1-foundations
folder: CSF-cs-fundamentals
difficulty: ★★★
depends_on:
used_by:
related:
tags:
  - csf
  - advanced
  - production
  - deep-dive
status: draft
version: 2
layout: default
parent: "CS Fundamentals - Paradigms"
grand_parent: "Technical Dictionary"
nav_order: 64
permalink: /csf/concurrency-models-compared-actor-csp-stm/
---

# CSF-064 - Concurrency Models Compared (Actor, CSP, STM)

⚡ TL;DR - Actor, CSP, and STM are three models that eliminate shared mutable state by different means: actors isolate state; CSP communicates via channels; STM uses atomic transactions. Each trades expressiveness for safety guarantees.

| CSF-064         | Category: CS Fundamentals - Paradigms | Difficulty: ★★★ |
| :-------------- | :------------------------------------ | :-------------- |
| **Depends on:** | CSF-036, CSF-043, CSF-052             |                 |
| **Used by:**    |                                       |                 |
| **Related:**    | CSF-036, CSF-043, CSF-052             |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Shared mutable state with locks is the dominant concurrency model.
It enables data races, deadlocks, and livelocks. As concurrent
systems scale in complexity, reasoning about lock ordering and
protected invariants becomes intractable. The code is correct
only if every developer correctly reasons about every
possible thread interleaving.

**THE BREAKING POINT:**
Erlang (1987) was built for telecom switches: millions of concurrent
calls; no downtime. Shared state with locks was impractical
at that scale. The designers chose the actor model: every entity
is an isolated process communicating by message. This enabled
hot code reloading and fault tolerance impossible with shared state.

**THE INVENTION MOMENT:**
Three distinct responses to shared-state concurrency emerged:
Hoare's CSP (Communicating Sequential Processes, 1978): processes
communicate via synchronous channels. Hewitt's Actor model (1973):
isolated actors communicate via asynchronous messages.
Harris & Peyton Jones STM (2005): software transactional memory
gives ACID-like semantics to in-memory operations.

**EVOLUTION:**
CSP: Go channels, Kotlin Channels/Flow, Clojure core.async.
Actors: Erlang, Elixir, Akka (Scala/Java). STM: Haskell STM,
Clojure's STM. All three models are in production use.
Modern systems blend models: Akka with STM-like cluster state;
Go with channels + mutexes.

---

### 📘 Textbook Definition

**Actor model**: concurrency unit = actor. Each actor has
private state; communicates only via asynchronous messages.
No shared state. **CSP (Communicating Sequential Processes)**:
concurrency unit = process. Processes communicate via
synchronous channels. Emphasis on channel operations over
entity identity. **STM (Software Transactional Memory)**:
shared state is managed with optimistic transactions. Reads
and writes in a transaction are retried atomically if a
conflict is detected. Analogous to database ACID transactions
for in-memory state.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Actor: isolate state per actor, communicate by message; CSP: communicate via typed channels; STM: read/write shared state atomically in retryable transactions.

**One analogy:**

> **Actor**: departments in a company. Each department manages
> its own budget; sends memos (messages) to other departments.
> No department shares a spreadsheet. **CSP**: a factory
> assembly line with conveyor belts (channels). Each station
> takes from one belt, processes, puts on another. Work flows
> through channels, not through shared memory. **STM**: a
> database transaction: read balances, subtract, add; if
> anything changed during the transaction, redo the whole thing.

**One insight:**
All three models achieve the same goal — safe concurrency —
but with different composability, performance, and debuggability
characteristics. CSP is natural for pipelines; actors for
stateful entities; STM for complex shared state invariants.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Actor: no shared state; all communication via message; actor processes one message at a time.
2. CSP: processes synchronise on channel operations; sender waits for receiver (or buffered channel).
3. STM: `atomically { }` block retried if any `TVar` read was modified by another thread.
4. All three eliminate data races: either no sharing (actor/CSP) or optimistic atomic retries (STM).
5. Deadlock: actor model can still deadlock (A waits for B's reply; B waits for A's reply).

**DERIVED DESIGN:**

- **Erlang/Elixir actors**: `send(pid, message)` async; `receive` pattern match; process supervisor trees
- **Akka (Java/Scala)**: typed actors; `ActorRef`; `ask` (request-reply with timeout)
- **Go channels**: `ch <- value` (send); `value := <-ch` (receive); `select` for multiplexing
- **Kotlin channels/flow**: `Channel<T>`, `Flow<T>` for reactive streams
- **Haskell STM**: `atomically $ do { v <- readTVar; writeTVar v (v+1) }`
- **Clojure refs**: `(dosync (alter ref inc))`

**THE TRADE-OFFS:**
**Actor**: natural for stateful entities; hard to compose; potential mailbox overflow.
**CSP**: natural for pipelines; synchronous semantics make backpressure easier.
**STM**: natural for complex invariants; performance cost of retries under contention.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Multiple agents modifying related state require coordination.
**Accidental:** Lock acquisition order bugs (solved by all three models).

---

### 🧪 Thought Experiment

**SETUP:**
Bank transfer: move $100 from Account A to Account B.
Both accounts are accessed concurrently by multiple threads.

**LOCKS (error-prone):**

```java
// Risk: lock A before B; another thread locks B before A -> deadlock
synchronized (accountA) {
    synchronized (accountB) {
        accountA.debit(100);
        accountB.credit(100);
    }
}
```

**ACTOR MODEL:**

```scala
// AccountActor processes messages one at a time (no lock needed)
case class Transfer(amount: Int, to: ActorRef)
class AccountActor extends Actor {
    var balance = 0
    def receive = {
        case Transfer(amount, to) =>
            balance -= amount
            to ! Credit(amount) // async message; no lock
    }
}
// No shared mutable state; no deadlock from lock ordering
```

**STM (Haskell):**

```haskell
transfer :: TVar Int -> TVar Int -> Int -> STM ()
transfer from to amount = do
    fromBal <- readTVar from
    when (fromBal < amount) retry -- retry if insufficient
    writeTVar from (fromBal - amount)
    toBal <- readTVar to
    writeTVar to (toBal + amount)
-- atomically: either both writes happen or neither
atomically $ transfer accountA accountB 100
```

**THE INSIGHT:**
STM gives you composable atomic operations. Two STM
transactions can be composed with `orElse` or `>>`. Lock-based
transactions can't be composed because locks can't be safely
combined without knowing the global lock order.

---

### 🧠 Mental Model / Analogy

> **Actor** is like a post office system: each person has a
> mailbox; they process mail privately; reply by sending new
> mail. Nobody reads your mail except you. **CSP** is like
> a factory with conveyor belts: items flow through channels;
> stations block when the belt is full (backpressure). **STM**
> is like a bank's ledger system: you draft a transaction,
> submit it; the bank checks no balances changed since you
> read them; if not, it commits; if yes, you redo.

**Element mapping:**

- Mailbox = actor inbox
- Processing mail = actor receive loop
- Conveyor belt = CSP channel
- Bank ledger = STM `TVar`
- Transaction commit = `atomically` success
- Redo = STM retry on conflict

Where this analogy breaks down: actor mailboxes can overflow;
CSP channels have configurable backpressure;
STM retries can spin under high contention.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Three ways to write concurrent programs without lock bugs:
Actors: entities communicate by sending messages; nobody
shares memory. CSP: work flows through typed channels.
STM: write transactions that retry if data changed
underneath them.

**Level 2 - How to use it (junior developer):**
Go: use channels for communication between goroutines; use
`sync.Mutex` only for simple counters. Avoid sharing mutable
struct fields between goroutines. Use `select` for multiplexing
multiple channels. Akka: model each domain entity as an actor;
use `ask` pattern with timeout for request-reply.

**Level 3 - How it works (mid-level engineer):**
CSP in Go: a goroutine blocks on channel send/receive.
The Go runtime schedules goroutines on OS threads
(M:N threading). `select` is multiplexing: blocks until any
channel is ready; chooses randomly among multiple ready
channels (prevents starvation). Unbuffered channels enforce
synchronisation: sender blocks until receiver ready.

**Level 4 - Why it was designed this way (senior/staff):**
Haskell's STM is composable because STM transactions are
pure values: `STM a` is a description of a transaction, not
an execution of one. Two `STM` values can be combined with
`>>=` (sequential) or `orElse` (alternative). This means
you can build complex atomic operations from simpler ones
without knowing about each other — something impossible
with locks (you must know the full lock set to avoid deadlock).
This composability is why Haskell STM is the gold standard
for STM design.

**Expert Thinking Cues:**

- When seeing complex lock ordering: could STM or actors simplify this?
- When actor mailbox grows unbounded: is there backpressure? Use bounded mailbox + supervision.
- Go channel `len(ch)` vs `cap(ch)`: if len approaches cap, sender will block; add monitoring.

---

### ⚙️ How It Works (Mechanism)

**Go CSP (channels):**

```go
func producer(ch chan<- int) {
    for i := 0; i < 10; i++ {
        ch <- i // blocks if ch is full
    }
    close(ch)
}
func consumer(ch <-chan int) {
    for v := range ch { // range receives until close
        fmt.Println(v)
    }
}
ch := make(chan int, 5) // buffered: up to 5 items
go producer(ch)
consumer(ch)
```

**Akka actor (Scala/Java):**

```scala
class CounterActor extends AbstractActor {
    private var count = 0
    // State accessed only from this actor's thread
    @Override public Receive createReceive() {
        return receiveBuilder()
            .match(Increment.class, msg -> count++)
            .match(GetCount.class, msg ->
                getSender().tell(count, getSelf()))
            .build();
    }
}
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW (Go pipeline with CSP):**

```
Stage 1: generate numbers  ← YOU ARE HERE
  |-> chan numCh (buffered 100)
Stage 2: filter evens
  |-> reads from numCh
  |-> writes to chan evenCh
Stage 3: double
  |-> reads from evenCh
  |-> writes to chan resultCh
Main: drain resultCh
  |-> all stages run as goroutines
  |-> backpressure: producer blocks when buffer full
  |-> fan-out/fan-in: multiply/merge channels as needed
```

**FAILURE PATH:**

- Actor deadlock: A sends to B; B sends to A while blocked waiting for A's reply
- CSP goroutine leak: goroutine blocked on channel send forever (receiver gone)
- STM contention spiral: high concurrency on same TVar; retries consume all CPU

---

### ⚖️ Comparison Table

| Model                 | State Location | Communication         | Deadlock Risk            | Best For           |
| --------------------- | -------------- | --------------------- | ------------------------ | ------------------ |
| Shared Memory + Locks | Shared         | Synchronous (lock)    | High                     | Simple counters    |
| Actor (Erlang/Akka)   | Per actor      | Async message         | Possible (request-reply) | Stateful entities  |
| CSP (Go channels)     | Per goroutine  | Sync/buffered channel | Possible (unbuffered)    | Pipelines          |
| STM (Haskell/Clojure) | Shared (TVar)  | Atomic transactions   | None (retry)             | Complex invariants |

---

### ⚠️ Common Misconceptions

| Misconception                        | Reality                                                                                                  |
| ------------------------------------ | -------------------------------------------------------------------------------------------------------- |
| "Actor model is deadlock-free"       | Actors can deadlock via request-reply cycles; pattern is less common than with locks                     |
| "Channels replace all mutexes in Go" | Go channels are for communication; `sync.Mutex` is for protecting shared data accessed by same goroutine |
| "STM is slow due to retries"         | Contention-free STM has minimal overhead; retries only occur under actual conflict                       |
| "CSP and actor model are the same"   | CSP emphasises channels (communication primitives); actors emphasise entity identity (message addresses) |
| "Go channels are always synchronous" | Buffered channels (`make(chan T, N)`) are asynchronous up to buffer capacity                             |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Actor Mailbox Overflow**
**Symptom:** `akka.actor.ActorQueue` unbounded growth; OOM.
**Root Cause:** Producer faster than consumer; no backpressure.
**Fix:** Use bounded mailbox + supervision strategy; or switch to Akka Streams (built-in backpressure).

**Mode 2: Goroutine Leak (CSP)**
**Symptom:** goroutine count grows indefinitely (`runtime.NumGoroutine()`).
**Root Cause:** Goroutine blocked on channel receive; sender gone; channel never closed.
**Fix:** Always close channels from the sender; use context for cancellation:

```go
func worker(ctx context.Context, ch <-chan int) {
    select {
    case v := <-ch: process(v)
    case <-ctx.Done(): return // goroutine exits on cancel
    }
}
```

**Mode 3: STM Retry Storm**
**Symptom:** High CPU; transactions not completing; `atomically` spinning.
**Root Cause:** Many threads contending on same `TVar`; retries cascade.
**Fix:** Reduce TVar scope; use per-entity TVars instead of global; add backoff.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[CSF-036 - Immutability]]
- [[CSF-052 - Concurrency Anti-Patterns (Shared State)]]

**Builds On This (learn these next):**

- Reactive Streams (Akka Streams, Project Reactor)
- Distributed actor systems (Akka Cluster, Erlang Distribution)

**Alternatives / Comparisons:**

- Thread pools + shared memory (classic)
- Async/await + event loop (Node.js, Kotlin coroutines)

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────┐
│ WHAT IT IS      Three models: Actor (isolated state),  │
│                 CSP (channels), STM (transactions)     │
│ PROBLEM         Shared mutable state + locks = race    │
│ IT SOLVES       conditions, deadlocks, data corruption │
│ KEY INSIGHT     Actor=isolate state; CSP=flow via chan; │
│                 STM=atomic retry transactions          │
│ USE WHEN        Actor: domain entities; CSP: pipelines; │
│                 STM: complex invariants               │
│ AVOID WHEN      STM: high contention; Actor: tight loops│
│ TRADE-OFF       Safety vs expressiveness vs perf       │
│ ONE-LINER       All three eliminate shared mutable     │
│                 state via different mechanisms        │
│ NEXT EXPLORE    Akka, Go channels, Haskell STM          │
└─────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Actor: each actor has private state; communicates only by async message; natural for stateful entities.
2. CSP: typed channels; processes communicate by passing data through channels; natural for pipelines.
3. STM: `atomically` block retried if any watched variable changed; composable atomic operations.

**Interview one-liner:**
"Actor, CSP, and STM are concurrency models that eliminate shared mutable state: actors isolate state per entity and communicate by message; CSP uses typed channels for pipeline-style communication; STM provides composable atomic transactions with optimistic conflict detection."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Isolation is the key to concurrency safety. If two units of
concurrency never share mutable state, they can never produce
a data race. Actor, CSP, and STM each enforce isolation
differently. The same principle appears at every scale:
microservices (share nothing, communicate via API),
databases (transactions isolate readers from partial writes),
and functional programming (immutable values).

**Where else this pattern appears:**

- **Microservices** — each service owns its data; actors at macro scale
- **Kafka** — producer/consumer model is CSP at distributed scale
- **Database transactions** — ACID semantics are distributed STM

---

### 💡 The Surprising Truth

Erlang's actor model was designed for a specific constraint:
telecom switches must not restart when a single call fails.
The actor model's supervision trees make this possible: each
actor is supervised by a parent; if it crashes, the supervisor
decides whether to restart it or escalate. This "let it crash"
philosophy is counterintuitive to Java developers trained
to catch every exception: in Erlang, you deliberately let
failing actors crash and restart cleanly, rather than
writing defensive code for every error case. This design
achieves "nine nines" reliability (99.9999999% uptime)
in Ericsson's AXD 301 switch — 31ms of downtime per year.

---

### 🧠 Think About This Before We Continue

**Q1 (System Interaction):** Go's CSP is implemented with
goroutines (M:N threading). Java's virtual threads (Project
Loom) also enable millions of concurrent threads. If Java
gets virtual threads and Go has goroutines, what is the
remaining advantage of Go's explicit channel-based CSP over
Java's implicit thread-per-request model?

_Hint:_ Research Project Loom's virtual threads. Both models
enable millions of cheap threads. The difference: Go forces
explicit communication via channels; Java Loom allows shared
mutable state as before (virtual threads don't eliminate
data races).

**Q2 (Scale):** An Akka actor system processes 100,000
messages per second. Each actor processes messages sequentially
(one at a time). If message processing takes 1ms, how many
actors do you need to sustain 100,000 RPS? What limits
the scaling ceiling?

_Hint:_ 1000 messages/sec per actor (1ms each). For 100k RPS:
100 actors minimum. But mailbox queuing latency, GC pauses,
and actor dispatch overhead add up. What happens when one
actor becomes a bottleneck (a supervisor or singleton)?

**Q3 (Design Trade-off):** STM retries transactions when
conflict is detected. Under high contention (1000 threads
all trying to update the same TVar), how does STM perform
compared to a mutex protecting the same value? What does
this imply about when to choose STM vs mutex?

_Hint:_ Under high contention, STM retries multiply: each
retry re-reads, re-writes, then re-checks. A mutex is
fair (FIFO queue). STM favours low-contention scenarios;
mutex favours high-contention. Research the "contention cliff"
in STM performance benchmarks.
