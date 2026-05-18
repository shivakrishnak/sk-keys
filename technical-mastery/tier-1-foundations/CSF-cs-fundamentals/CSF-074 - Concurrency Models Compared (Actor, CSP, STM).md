---
id: CSF-074
title: "Concurrency Models Compared (Actor, CSP, STM)"
category: CS Fundamentals - Paradigms
tier: tier-1-foundations
folder: CSF-cs-fundamentals
difficulty: ★★★
depends_on: CSF-030, CSF-043
used_by:
related: CSF-030, CSF-043, CSF-025, CSF-072
tags: [concurrency-models, actor-model, csp, software-transactional-memory, message-passing]
status: complete
version: 4
layout: default
parent: "CS Fundamentals - Paradigms"
grand_parent: "Technical Mastery"
nav_order: 74
permalink: /technical-mastery/csf/concurrency-models-compared/
---

⚡ TL;DR - Three high-level concurrency models: (1) Actor Model
(Erlang, Akka): isolated actors communicate via ASYNC message passing,
no shared state; (2) CSP (Communicating Sequential Processes, Go channels):
synchronized synchronous channel communication between concurrent processes;
(3) STM (Software Transactional Memory, Haskell STM, Clojure atoms):
atomic transactions on shared memory, optimistic concurrency with rollback.
Shared-memory threading (Java synchronized, ReentrantLock): baseline -
powerful, error-prone. Each model trades coordination complexity for
different expressiveness, fault tolerance, and performance characteristics.

| #074 | Category: CS Fundamentals - Paradigms | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | CSF-030 (Concurrency Basics), CSF-043 (Concurrency Primitives) | |
| **Used by:** | (foundation for Akka, Erlang OTP, Go channels, Clojure STM architecture decisions) | |
| **Related:** | CSF-030 (Concurrency), CSF-043 (Primitives), CSF-025 (Parallelism), CSF-072 (Undefined Behaviour - data races) | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**

Shared-memory threading (Java): multiple threads, shared heap, explicit
synchronization via `synchronized`, `ReentrantLock`, `volatile`. Problems:
(1) Deadlock: two threads each waiting for a lock held by the other.
(2) Race conditions: undetected concurrent access to shared data.
(3) Livelock: threads continually changing state in response to each other
but never making progress.
(4) Priority inversion: high-priority thread blocked on lock held by low-priority thread.
(5) Lock granularity tradeoff: coarse-grained lock = low parallelism, fine-grained = deadlock risk.
Correct concurrent code with shared-memory threading requires understanding EVERY shared variable
and its synchronization. One mistake: months-long intermittent bug.

**THE BREAKING POINT:**

WhatsApp (before acquisition): 2 million connected users per server, written in Erlang.
The Erlang Actor model: each WhatsApp connection is an ACTOR (lightweight process).
No shared state between actors. If an actor fails: other actors unaffected.
Erlang's OTP supervision trees: supervisors restart failed actors automatically.
Fault tolerance: designed in at the model level. Java thread-based approach: one thread
exception crashes the whole server (without careful management). Erlang's model made
WhatsApp's extreme per-server user count possible. The choice of concurrency model
IS a scalability and fault-tolerance decision.

**THE INVENTION MOMENT:**

Actor model: Carl Hewitt (1973, MIT). "Laws for Communicating Parallel Entities."
Actors as fundamental computation units: receive messages, create actors, send messages.
No shared state. Erlang (Joe Armstrong, 1986): first production Actor model language,
designed for telecoms (fault tolerant, concurrent, distributed).
CSP: Tony Hoare (1978). "Communicating Sequential Processes." Mathematical model of
concurrent processes communicating over channels. Go (2009): channels as first-class
CSP-inspired concurrency primitive.
STM: Tim Harris et al. (2005, Haskell). Transactional memory as an alternative to locks.
Compose transactions atomically without deadlock risk.

---

### 📘 Textbook Definition

**Actor Model:** A concurrency model where the fundamental unit is an ACTOR: an independent
entity that encapsulates state, processes messages one at a time from a mailbox, and communicates
ONLY via message passing. No shared state between actors. State is private. Messages are immutable.

**CSP (Communicating Sequential Processes):** A formal model of concurrent computation
(Tony Hoare, 1978) where processes communicate by SYNCHRONIZING ON CHANNELS. A channel
communication happens when BOTH the sender and receiver are ready (synchronous rendezvous).
Go channels: buffered (async, up to buffer capacity) or unbuffered (synchronous, both parties
must be ready simultaneously).

**STM (Software Transactional Memory):** Transactions for memory: multiple memory reads/writes
grouped into an atomic, isolated transaction. If no conflict: commit. If conflict (another transaction
modified the same memory): rollback and retry. Optimistic: assumes conflicts are rare. Composable:
transactions can be combined atomically.

**Shared-Memory Threading (mutex/lock model):** The traditional concurrent programming model.
Multiple threads share a heap. Synchronization via mutual exclusion (mutex/lock). The programmer
is responsible for correct lock acquisition and release. Prone to deadlock, race conditions,
and livelock.

**Green Threads / Virtual Threads:** Lightweight threads managed by the language runtime
(not OS threads). Java 21 Virtual Threads: millions of virtual threads on a few OS threads.
Erlang processes: each actor is a lightweight process (green thread). CSP goroutines (Go):
multiplexed onto OS threads. Allows writing synchronous-looking code with high concurrency.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Three models for avoiding shared-state concurrency complexity: Actors (no shared state,
async messages, fault-isolated), CSP/channels (synchronized message passing between processes),
STM (atomic transactions on shared memory, composable, no deadlock). All eliminate some class
of shared-memory threading bug. Trade different things: latency, throughput, fault tolerance,
composability.

**One analogy:**

> ACTORS: A company where each employee (actor) works independently on their own desk (private state).
> Employees communicate only by passing notes (messages) via the mail system (mailbox).
> No employee can read another's desk directly. If an employee goes home sick: others continue.
>
> CSP: A factory with assembly line conveyors (channels). Workers hand parts directly from
> one to the next (synchronous handoff). Both must be at the conveyor simultaneously.
> Buffer: a conveyor belt (buffered channel): producer can put parts without waiting for consumer.
>
> STM: A bank teller (STM transaction). Before performing any update: reads the current state
> (optimistic). After all reads/writes: tries to commit. If someone else modified the same
> account while we worked: transaction is rolled back, started over. No explicit locks; just
> automatic conflict detection.

**One insight:**

The fundamental question every concurrency model answers differently:
"HOW DO WE PREVENT CONCURRENT ACCESS TO SHARED MUTABLE STATE?"
Actors: eliminate shared state entirely (everything is message-passed).
CSP: synchronize at communication points (channel handoffs force coordination).
STM: allow optimistic concurrent access, detect conflicts, retry.
Shared-memory threading: leave it to the programmer (locks, volatiles, atomics).
The Actor and CSP models follow Go's maxim: "Do not communicate by sharing memory;
instead, share memory by communicating." STM: keep shared memory but make access transactional.
Threading: keep shared memory, manual synchronization. The model choice determines
what bugs are possible, what tools are available, and what scale is achievable.

---

### 🔩 First Principles Explanation

**ACTOR MODEL MECHANICS:**

```
┌──────────────────────────────────────────────────────┐
│ ACTOR LIFECYCLE:                                     │
│                                                      │
│ 1. Created (by another actor or the system)          │
│ 2. Has a MAILBOX: bounded or unbounded queue         │
│ 3. PROCESSES ONE MESSAGE AT A TIME (no concurrency   │
│    within the actor itself)                          │
│ 4. Message processing: can                           │
│    - Change internal state                           │
│    - Create new actors                               │
│    - Send messages to known actors (by reference)    │
│ 5. No direct access to other actor's state           │
│                                                      │
│ FAILURE HANDLING (Erlang/Akka):                      │
│ "Let it crash" philosophy.                           │
│ Supervisor actor monitors child actors.             │
│ If child crashes: supervisor restarts it.            │
│ Crash is isolated: other actors unaffected.         │
│                                                      │
│ CSP MECHANICS:                                       │
│ Goroutine A:  ch <- data  // send (blocks if full)  │
│ Goroutine B:  data := <-ch // receive (blocks if empty)│
│ Unbuffered: both must be ready simultaneously.      │
│ Buffered(n): producer can lead by n items.          │
│ Select: non-deterministically pick from multiple     │
│ channels (Go select statement).                     │
└──────────────────────────────────────────────────────┘
```

**STM MECHANICS:**

```
┌──────────────────────────────────────────────────────┐
│ STM TRANSACTION (Haskell/Clojure):                   │
│                                                      │
│ atomically $ do                -- begin transaction  │
│   balance <- readTVar acct     -- read (records ver) │
│   if balance >= amount                               │
│     then writeTVar acct (balance - amount)           │
│         -- write (tentative, not committed yet)     │
│     else retry                 -- block, retry later │
│                                                      │
│ COMMIT PROTOCOL:                                     │
│ At commit time: check if any TVar was modified      │
│ since our last read. If YES: conflict detected.     │
│ ROLLBACK: discard all writes, re-execute from start.│
│ If NO conflict: commit all writes atomically.       │
│                                                      │
│ ADVANTAGES:                                          │
│ - No deadlock (no locks held across transactions)   │
│ - Composable: txnA `orElse` txnB = atomic composite │
│ - No priority inversion                             │
│                                                      │
│ DISADVANTAGES:                                       │
│ - High contention: many rollbacks/retries           │
│ - No IO inside transactions (rollback can't undo IO)│
│ - Implementation overhead                           │
└──────────────────────────────────────────────────────┘
```

---

### 🧪 Thought Experiment

**SAME PROBLEM: BANK TRANSFER IN EACH MODEL:**

Transfer $100 from account A to account B atomically.

**Shared-memory threading (Java):**
```java
synchronized(lock) {
    if (a.getBalance() >= 100) {
        a.debit(100);
        b.credit(100);
    }
}
// Risk: lock ordering. If another code path locks b then a: deadlock.
// Need: always acquire locks in same order (a < b) or use tryLock with timeout.
```

**Actor model (Akka):**
```scala
// One actor "owns" each account. Transfer via message.
// Transfer Actor sends: Debit(100, transferId) to AccountActorA
// AccountActorA processes: debits, sends DebitSuccess(transferId)
// Transfer Actor receives DebitSuccess: sends Credit(100) to AccountActorB
// No shared state. No locks. But: two-phase commit required for atomicity.
// Saga pattern: compensating transaction if credit fails after debit succeeds.
```

**CSP (Go channels):**
```go
// Serialize access to accounts via a single goroutine that owns both.
type TransferReq struct { amount int; from, to *Account; done chan error }
transferChan := make(chan TransferReq)
go func() { // single goroutine owns both accounts
    for req := range transferChan {
        if req.from.balance >= req.amount {
            req.from.balance -= req.amount
            req.to.balance += req.amount
            req.done <- nil
        } else {
            req.done <- errors.New("insufficient funds")
        }
    }
}()
// Single ownership: no races. The channel serializes all transfers.
```

**STM (Haskell/Clojure):**
```haskell
transfer :: TVar Int -> TVar Int -> Int -> STM ()
transfer from to amount = do
    bal <- readTVar from
    if bal < amount then retry  -- block until more funds
    else do
        writeTVar from (bal - amount)
        modifyTVar' to (+amount)
-- Usage (atomic):
atomically (transfer accountA accountB 100)
-- Atomic: both reads and writes committed together or not at all.
-- No deadlock: no locks held. Composable: can combine transactions.
```

---

### 🎯 Mental Model / Analogy

**DECISION FRAMEWORK:**

```
┌──────────────────────────────────────────────────────┐
│ CHOOSE BASED ON DOMINANT CONCERN:                    │
│                                                      │
│ FAULT TOLERANCE + DISTRIBUTED SCALE:                │
│  -> Actor Model (Erlang/OTP, Akka)                  │
│  Crash isolation, supervision trees, location       │
│  transparency (actors on different machines).       │
│  WhatsApp, telecoms, high-availability services.   │
│                                                      │
│ PIPELINE PROCESSING + FLOW CONTROL:                 │
│  -> CSP / Channels (Go, Kotlin coroutines)         │
│  Data pipelines, producer-consumer, fan-out.       │
│  ETL pipelines, service meshes, stream processing. │
│                                                      │
│ COMPOSABLE ATOMIC UPDATES (IN-MEMORY):              │
│  -> STM (Haskell STM, Clojure refs/atoms)          │
│  Composable transactions without deadlock.          │
│  In-memory databases, financial calculations.       │
│                                                      │
│ MAXIMUM PERFORMANCE + FINE-GRAINED CONTROL:         │
│  -> Shared-memory + lock-free data structures       │
│  OS kernels, game engines, HPC, low-latency trading│
│                                                      │
│ MOST JAVA APPLICATIONS:                             │
│  -> Java 21 Virtual Threads + structured concurrency│
│  Looks like sequential code, scales like async.    │
└──────────────────────────────────────────────────────┘
```

**MEMORY HOOK:**

"Actor: isolated state, async message mailbox, let-it-crash + supervisor. Erlang/Akka. Fault isolation.
CSP: channels for synchronization. Unbuffered = rendezvous, buffered = async up to N. Go. Pipelines.
STM: atomic transactions on TVars, optimistic, rollback on conflict. Haskell, Clojure. Composable.
Shared-memory threading: the hard way. Locks, races, deadlocks. Java synchronized. Control.
Go maxim: 'Share memory by communicating, not communicate by sharing memory.'
Actor maximism: 'Let it crash.' Supervision handles recovery.
STM maxim: 'No locks, no deadlock. But no IO in transactions.'
Virtual Threads (Java 21): OS thread pool + M:N scheduling -> millions of blocking calls scale."

---

### 📊 Gradual Depth - Five Levels

**Level 1 - Child:**
Actors: people passing notes (messages). Can't touch each other's stuff.
If someone makes a mistake, their boss (supervisor) fixes it without bothering others.
CSP: walkie-talkies: both must press the button at the same time to talk (synchronous).
STM: sticky note on a whiteboard: read, edit on paper, put back if no one changed it while you were writing.

**Level 2 - Student:**
Go channels (CSP in practice):
```go
package main

import "fmt"

func producer(ch chan<- int) {
    for i := 0; i < 5; i++ {
        ch <- i // send; blocks if channel full
    }
    close(ch)
}

func consumer(ch <-chan int) {
    for v := range ch { // receive until closed
        fmt.Println("Got:", v)
    }
}

func main() {
    ch := make(chan int, 2) // buffered: up to 2 items without blocking
    go producer(ch)
    consumer(ch) // main goroutine consumes
}
// Producer and consumer run concurrently.
// No shared variables. No locks. No races.
// The channel synchronizes coordination.
```

**Level 3 - Professional:**
Akka actor (Scala) for fault-tolerant counter:
```scala
import akka.actor._

class CounterActor extends Actor {
    var count = 0
    def receive = {
        case "increment" => count += 1
        case "get"       => sender() ! count
        case "crash"     => throw new RuntimeException("crash!")
    }
    override def preRestart(reason: Throwable, msg: Option[Any]) = {
        // reset state on restart
        count = 0
        super.preRestart(reason, msg)
    }
}
// Supervisor (default OneForOneStrategy):
class Supervisor extends Actor {
    override val supervisorStrategy = OneForOneStrategy(maxNrOfRetries = 3) {
        case _: RuntimeException => SupervisorStrategy.Restart
    }
    val child = context.actorOf(Props[CounterActor], "counter")
    def receive = { case msg => child forward msg }
}
// If CounterActor throws: Supervisor restarts it (max 3 times).
// Other actors: unaffected. State: reset to 0 on restart.
// No need to handle failure at the actor level: supervisors handle it.
```

**Level 4 - Senior Engineer:**
Haskell STM for composable transactions:
```haskell
import Control.Concurrent.STM

-- Semaphore using STM:
data Semaphore = Sem (TVar Int)

newSemaphore :: Int -> STM Semaphore
newSemaphore n = Sem <$> newTVar n

acquire :: Semaphore -> STM ()
acquire (Sem tv) = do
    n <- readTVar tv
    if n == 0 then retry  -- BLOCKS until n > 0 (STM retry)
    else writeTVar tv (n - 1)

release :: Semaphore -> STM ()
release (Sem tv) = modifyTVar' tv (+1)

-- Compose: acquire TWO semaphores atomically (no deadlock possible)
acquireBoth :: Semaphore -> Semaphore -> STM ()
acquireBoth s1 s2 = acquire s1 >> acquire s2
-- This is IMPOSSIBLE to do without deadlock risk using locks.
-- STM: no locks held = no deadlock. Both acquired atomically or neither.
```

**Level 5 - Expert:**
Virtual Threads (Java 21) vs Actor model vs CSP:
```java
// Java 21 Virtual Threads: million-scale concurrency without explicit message passing:
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    // 1,000,000 virtual threads: each makes an HTTP call (blocking I/O)
    for (int i = 0; i < 1_000_000; i++) {
        executor.submit(() -> {
            var result = httpClient.get("https://api.example.com/resource");
            // Blocking call: virtual thread parks, OS thread released.
            // When response arrives: virtual thread unparked, OS thread acquired.
            return processResult(result);
        });
    }
} // waits for all, automatically closes executor
// CODE LOOKS SEQUENTIAL. Scales to 1M concurrent tasks.
// No channels. No actors. No explicit async/callback.
// The runtime (JVM) provides the concurrency.
// Trade-off: no built-in fault isolation (need try/catch per task).
// For fault isolation: Structured Concurrency (JEP 453) provides scope + error handling.
```

---

### ⚙️ How It Works

**HOW GO'S SELECT STATEMENT IMPLEMENTS CSP CHOICE:**

```
┌──────────────────────────────────────────────────────┐
│ GO SELECT: wait for any of multiple channel ops:     │
│                                                      │
│ select {                                             │
│ case msg1 := <-ch1:                                  │
│     // ch1 was ready: process msg1                  │
│ case msg2 := <-ch2:                                  │
│     // ch2 was ready: process msg2                  │
│ case ch3 <- data:                                    │
│     // ch3 was ready to receive: data sent          │
│ case <-time.After(timeout):                          │
│     // none ready after timeout: handle timeout     │
│ default:                                             │
│     // none ready right now: non-blocking behavior  │
│ }                                                    │
│                                                      │
│ SELECT SEMANTICS:                                    │
│ If multiple cases ready simultaneously: chosen       │
│ UNIFORMLY AT RANDOM (fairness).                     │
│ Not ready: goroutine PARKS (suspends without OS     │
│ thread). Woken when any case becomes ready.         │
│                                                      │
│ This implements CSP's EXTERNAL CHOICE ([] operator) │
│ directly in the language.                           │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: Shared State vs Channel Communication**

```go
// BAD: Shared state with mutex (error-prone Go pattern)
type Counter struct {
    mu    sync.Mutex
    count int
}
func (c *Counter) Increment() {
    c.mu.Lock()
    c.count++ // critical section
    c.mu.Unlock()
}
func (c *Counter) GetCount() int {
    c.mu.Lock()
    defer c.mu.Unlock()
    return c.count
}
// Problems: must remember to lock/unlock.
// Forget once: data race. Lock in wrong order: deadlock.
// Coarse lock: bottleneck. Fine-grained locks: complexity.

// GOOD: Single goroutine owns the counter (CSP ownership)
type CounterService struct {
    incCh  chan struct{}
    getCh  chan chan int
    doneCh chan struct{}
}
func NewCounter() *CounterService {
    cs := &CounterService{
        incCh:  make(chan struct{}, 100),
        getCh:  make(chan chan int),
        doneCh: make(chan struct{}),
    }
    go cs.run() // single goroutine owns the state
    return cs
}
func (cs *CounterService) run() {
    count := 0
    for {
        select {
        case <-cs.incCh:   count++
        case r := <-cs.getCh:  r <- count
        case <-cs.doneCh:  return
        }
    }
}
func (cs *CounterService) Increment() { cs.incCh <- struct{}{} }
func (cs *CounterService) Get() int {
    r := make(chan int)
    cs.getCh <- r
    return <-r
}
// State owned by one goroutine. No races. No locks.
// All access serialized by channel communication.
```

**Example 2 - Failure: Deadlock in Java Lock Ordering**

```java
// BAD: Classic deadlock (transfer between two accounts, wrong lock order)
class Account {
    final int id;
    private double balance;
    final Object lock = new Object();

    void transfer(Account to, double amount) {
        synchronized (this.lock) {           // acquire: this
            synchronized (to.lock) {         // acquire: to
                this.balance -= amount;
                to.balance += amount;
            }
        }
    }
}

// Thread 1: a.transfer(b, 100)  -> lock a, then lock b
// Thread 2: b.transfer(a, 200)  -> lock b, then lock a
// -> DEADLOCK: Thread 1 holds a, waits for b.
//              Thread 2 holds b, waits for a.
// Java: no deadlock detection. Both threads park forever.

// GOOD: Lock ordering (always lock smaller ID first)
void transfer(Account to, double amount) {
    Account first  = id < to.id ? this : to;
    Account second = id < to.id ? to : this;
    synchronized (first.lock) {
        synchronized (second.lock) {
            first.balance  -= (first == this ? amount : -amount);
            second.balance -= (second == this ? amount : -amount);
        }
    }
}
// Lock order: always smaller ID first -> no circular wait -> no deadlock.

// BETTER: STM (no locks = no deadlock):
// Transfer via atomic update of both TVars in one STM transaction.
```

---

### ⚖️ Comparison Table

| Model | State sharing | Synchronization | Deadlock risk | Fault isolation | Languages |
|---|---|---|---|---|---|
| Actors | No shared state | Async mailbox | No (no locks) | High (per-actor crash) | Erlang, Akka (Scala/Java), Elixir |
| CSP | No shared state | Channel rendezvous | No (no locks) | Medium (goroutine panic) | Go, Kotlin coroutines, Clojure |
| STM | Shared TVars | Transactional | No (no locks) | Low | Haskell STM, Clojure refs |
| Shared-memory | Shared heap | Mutex/lock/atomic | Yes | Low | Java, C++, Rust unsafe |
| Virtual Threads | Shared heap | Structured concurrency | Yes (locks) | Medium (scoped) | Java 21, Kotlin coroutines |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Actors prevent all concurrency bugs" | Actors prevent shared-state races because there IS no shared state. But Actor-based systems have their own bug classes: (1) MAILBOX OVERFLOW: if a slow actor receives messages faster than it processes them, the mailbox grows without bound -> OutOfMemoryError. (2) MESSAGE ORDERING: messages between two actors may not arrive in send order if routed through multiple nodes. (3) LOST MESSAGES: in distributed systems, a message to a crashed actor is lost (fire-and-forget). (4) DEADLOCK via REQUEST-RESPONSE: actor A sends to B and WAITS for reply; B sends to A and waits for reply -> circular wait (same as lock deadlock, but with messages). (5) STARVATION: one actor floods another's mailbox, starving other senders. Actors solve the shared-memory concurrency problem. They introduce the distributed-system problem set. |
| "Go channels make concurrent code easy and correct" | Go channels provide a cleaner abstraction than locks, but concurrent Go code is still complex and bug-prone. Common Go concurrency bugs: (1) GOROUTINE LEAK: goroutine blocked on channel send/receive that never proceeds (channel was never closed or receiver exited). Goroutine leaks are the Go equivalent of thread leaks in Java. (2) CLOSURE VARIABLE CAPTURE: goroutine captures loop variable by reference, loop continues. All goroutines see the same final value (classic bug). (3) CHANNEL CLOSE PANIC: sending to a closed channel panics. (4) SELECT WITH DEFAULT: a select with a default case never blocks, can busy-wait in a loop. (5) UNBUFFERED CHANNEL DEADLOCK: both goroutines send before either receives. Go provides tooling (race detector: `go test -race`) to catch races. Use it in CI. Channel-based code has fewer RACES but goroutine lifecycle bugs are common. |
| "STM is always better than locks because no deadlock" | STM eliminates deadlock but has its own limitations. (1) CONTENTION COST: under high contention (many concurrent transactions modifying the same TVar), STM causes many rollbacks and retries. Each retry re-executes the transaction body. For high-write-contention workloads: STM can be slower than a single lock. (2) NO IO IN TRANSACTIONS: STM transactions must be pure (no side effects). Cannot do IO (print, network call, database write) inside an STM transaction because if the transaction is rolled back, the IO cannot be undone. This is a significant practical constraint. (3) MEMORY OVERHEAD: STM must track read/write sets per transaction. More memory than a simple lock. (4) STARVATION: a transaction that always conflicts may never commit (livelock). STM is best for: in-memory data structures, rarely contested shared state, composable transactions. STM is NOT a silver bullet for all concurrency. |
| "Erlang Actors are just Java threads with a different API" | Erlang processes are MUCH lighter than Java threads. A Java thread: typically ~0.5-1MB stack. Erlang process: ~1-2KB initial heap, growing as needed. An Erlang node routinely runs MILLIONS of processes. Java: thousands of OS threads is impractical (memory, scheduling). Java 21 Virtual Threads narrow the gap significantly (VT initial stack: small, growing as needed). But: Erlang's key differentiator is not just lightweight processes - it's the FAULT TOLERANCE MODEL. Erlang OTP supervision trees: supervisor/child structure with restart strategies. If a child crashes: supervisor restarts it. No manual recovery code needed in most cases. Erlang's "let it crash" philosophy: don't write defensive recovery code. Write simple correct code; let the supervisor handle recovery. Java Virtual Threads: concurrency model without the fault-tolerance model. For Erlang-level fault tolerance in the JVM: Akka (actor framework, supervision trees) provides the missing piece. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Goroutine Leak (Go)**

**Symptom:** Go service memory grows slowly over time. `goroutine` count in `pprof` grows without bound. Eventually: OOM.

**Diagnosis:**
```bash
# Enable pprof endpoint in Go service:
import _ "net/http/pprof"
go http.ListenAndServe(":6060", nil)

# Check goroutine count:
curl http://localhost:6060/debug/pprof/goroutine?debug=1
# If goroutines stuck on: "chan receive", "chan send", "select":
# -> goroutine leak. Channel communication blocked forever.

# Full goroutine stack dump:
curl http://localhost:6060/debug/pprof/goroutine?debug=2 > goroutines.txt
grep -A5 "chan receive\|chan send" goroutines.txt
# Find: which function is the goroutine stuck in.
# Common cause: goroutine started, passes result to channel, but receiver exited.
```

**Fix:** Every goroutine that blocks on a channel must have a CANCELLATION path (context.Context).
Use `context.WithCancel` or `context.WithTimeout` for goroutines that may block:
```go
func worker(ctx context.Context, ch <-chan Work) {
    for {
        select {
        case w, ok := <-ch:
            if !ok { return } // channel closed: exit
            process(w)
        case <-ctx.Done():
            return // context cancelled: exit
        }
    }
}
```

---

**Security Note:**

Concurrency bugs are increasingly exploited for security vulnerabilities:

1. RACE CONDITION as TOCTOU (Time-of-Check Time-of-Use):
   ```java
   // BAD: check then use with window for race
   if (file.exists() && file.canWrite()) {
       // Window here: attacker replaces file with symlink to /etc/passwd
       file.write(data); // writes to /etc/passwd via symlink
   }
   // Fix: atomic operations, or assume-then-handle-error (EAFP style).
   ```
2. Actor model: message validation. Actors receive messages from any sender.
   Validate message structure and access control INSIDE the actor's receive handler.
   Don't trust the sender identity (in distributed Actor systems: sender can be spoofed).
3. STM and secret leakage: if an STM transaction reads a secret (key, password) and
   the transaction is rolled back, the secret MAY have been observed by the retry logic.
   Avoid reading secrets in frequently-retried STM transactions; or ensure the retry
   does not leak the intermediate read.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Concurrency Basics` (CSF-030) - threads, shared state, and the problems that motivate these models
- `Concurrency Primitives` (CSF-043) - mutex, semaphore, monitor: the baseline tools that the higher-level models improve upon

**Builds On This (learn these next):**
- Java Concurrency (JCC category): deep dive on Java concurrent collections, CompletableFuture, Virtual Threads
- Reactive Programming (Flux/Mono): CSP-inspired reactive streams in Java

---

### 📌 Quick Reference Card

```
┌────────────────────────────────────────────────────────┐
│ ACTOR       │ Isolated state, async mailbox            │
│             │ Let-it-crash + supervisor (Erlang, Akka) │
│             │ No shared state, fault isolated          │
├─────────────┼──────────────────────────────────────────┤
│ CSP         │ Channels, synchronous rendezvous         │
│             │ Go: buffered or unbuffered               │
│             │ select for multiple channels             │
├─────────────┼──────────────────────────────────────────┤
│ STM         │ Atomic transactions on TVars             │
│             │ Optimistic, rollback on conflict         │
│             │ No locks = no deadlock. No IO in txn.   │
├─────────────┼──────────────────────────────────────────┤
│ SHARED MEM  │ Mutex, lock-free atomics, volatile       │
│             │ Java synchronized, ReentrantLock         │
│             │ Deadlock risk, race conditions           │
├─────────────┼──────────────────────────────────────────┤
│ VIRTUAL THR │ Java 21: M:N scheduling, sync code style │
│             │ Not message-passing but scales to 1M     │
├─────────────┼──────────────────────────────────────────┤
│ CHOOSE      │ Fault isolation -> Actor                 │
│             │ Pipelines -> CSP/channels                │
│             │ Composable atomic -> STM                 │
│             │ Max performance -> lock-free             │
├─────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE│ JCC (Java Concurrency category)          │
└────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. The fundamental insight behind Actors, CSP, and STM: avoid SHARED MUTABLE STATE.
   Actors: no sharing (private state, async messages). CSP: share by communicating
   (channels are the synchronization point, not shared memory). STM: share by making
   access transactional (atomic reads and writes, optimistic, rollback on conflict).
   Shared-memory threading: share memory, manage access with locks (error-prone).
   The Go maxim: "Do not communicate by sharing memory; instead, share memory by
   communicating." This phrase captures the Actor and CSP approach in one sentence.
2. Actor model distinguishing features: (1) Message-passing only (no direct state access).
   (2) Async mailbox (sender never blocks waiting for recipient to process).
   (3) Let-it-crash + supervision trees (fault tolerance baked in, not handled at the
   actor level). Erlang and Akka implement this. Key use case: distributed, highly
   available systems (WhatsApp, telecoms, real-time systems). Limitation: no shared
   state means complex state sharing requires message-based coordination (saga pattern
   for distributed transactions). Mailbox overflow is a failure mode: bounded mailboxes
   + back-pressure required for production.
3. CSP (Go channels): unbuffered channel = rendezvous (both sender and receiver must
   be ready simultaneously). Buffered channel = sender can lead by N items. `select`
   statement: wait for any of multiple channels (or the default case for non-blocking).
   Goroutine leak: goroutine blocked on channel operation with no cancellation path.
   Fix: always use `context.Context` for goroutine cancellation. `go test -race`:
   Go's race detector, use in CI for all concurrent code.

**Interview one-liner:**
"Three concurrency models beyond shared-memory threading:
Actor (Erlang/Akka): isolated state + async mailbox + supervision. No shared state, fault isolated. Let-it-crash.
CSP (Go channels): synchronize on channel communication. Unbuffered = rendezvous, buffered = async-N. Select for multiple channels.
STM (Haskell/Clojure): atomic transactions on TVars. No locks = no deadlock. No IO in transactions. Rollback on conflict.
Each eliminates locks but with different constraints. Choose: Actor for fault tolerance, CSP for pipelines, STM for composable atomic in-memory. Java 21 Virtual Threads: sync code style, M:N scaling, not message-passing."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
CHOOSE THE ABSTRACTION LEVEL THAT MATCHES YOUR COORDINATION PROBLEM.
Shared-memory + locks: low-level, powerful, error-prone.
CSP channels: higher-level (communication as first-class), less error-prone.
Actors: even higher (message passing as the only mechanism), built-in fault tolerance.
STM: different axis (transactions, not messages), composable.
The mistake: defaulting to the lowest-level tool (locks) for every concurrency problem.
The right question: what is the COORDINATION PATTERN in my system?
Pipeline (stages processing data): CSP. Fault-isolated independent state: Actors.
Composable atomic updates: STM. Maximum performance, expert team: locks + atomics.
Abstractions have costs (overhead, learning curve, constraints) but the bugs they PREVENT
are usually worth more than the overhead they add. A deadlock-free design at the model
level is worth more than a 10% performance gain from raw locks.

**Where else this pattern appears:**

- **Kafka producers/consumers as CSP with durable channels** - Apache Kafka's architecture
  is essentially CSP with DURABLE, DISTRIBUTED channels (topics). A Kafka topic is a channel:
  producers write to it, consumers read from it. Unlike Go's ephemeral channels: Kafka topics
  are durable (messages persist for configurable retention period), distributed (replicated
  across brokers), and many-to-many (multiple producer groups, multiple consumer groups).
  Kafka's consumer groups implement a CSP SELECT-like operation: multiple consumers each
  own a partition of the topic, processing their partition independently. This is "fan-out
  with partitioned parallelism." The coordination mechanism: partition assignment (one consumer
  owns one partition at a time, enforcing ordering within the partition). No shared mutable
  state between consumers (each reads its own partition). This is CSP's no-shared-state
  principle applied at the distributed systems level. Backpressure: producer blocks when
  topic is full (like a full buffered channel). This CSP design allows Kafka to scale to
  millions of messages per second without coordination between consumers.
- **Erlang's influence on microservices architecture** - Erlang's actor model and OTP
  supervision trees directly inspired microservices architecture patterns. "Each service
  is an actor": isolated state, communicates via messages (HTTP/gRPC/events), supervised
  by an orchestrator (Kubernetes restart policies). "Let it crash" = fail fast (crash the
  service pod rather than catching all exceptions) + Kubernetes restart policy (supervisor).
  Service mesh health checks = Erlang process monitoring. Circuit breaker = Erlang's supervision
  with restart strategies (one-for-one, all-for-one). The conceptual mapping is direct.
  Netflix's resilience engineering: chaos monkey (crash random services) + automatic recovery
  is the microservices equivalent of Erlang's let-it-crash + supervision trees. Understanding
  the Actor model explains WHY these microservices patterns work: they apply the same
  fault-isolation and recovery principles that Erlang proved in telecoms (9-nines availability)
  to distributed service architectures.

---

### 💡 The Surprising Truth

WhatsApp, before its $19 billion acquisition by Facebook in 2014, served 450 million users
with a team of just 55 engineers. Critical infrastructure: 2 million concurrent TCP connections
per Erlang server. This density - 2 million connections per server - was possible BECAUSE of the
Erlang Actor model. Each connection is a lightweight Erlang process (~2KB RAM). 2 million
connections * 2KB = 4GB RAM per server. Achievable. Compare: 2 million Java threads * 1MB stack
= 2 TERABYTES of stack memory. Impossible. WhatsApp's engineering blog (before acquisition) noted
that they routinely ran millions of Erlang processes per node. The Actor model's lightweight
process design (not the concurrency abstraction) was the technical secret. The concurrency model
DICTATED the business model: 55 engineers could serve 450M users because the language's concurrency
model let them use hardware efficiently. One language design decision (lightweight processes,
actor isolation) produced a competitive moat worth $19 billion. This is perhaps the most
financially consequential programming language choice in software engineering history.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **[ACTOR-DESIGN]** Design an Actor-based system for processing incoming orders:
   each order must be validated (ValidatorActor), persisted (PersistenceActor), and
   notified (NotificationActor). Draw the supervision tree. What restart strategy
   for each supervisor? How do you handle partial failure (persist succeeds, notify fails)?

2. **[CSP-CHANNELS]** Implement a Go pipeline: stage 1 generates URLs, stage 2 fetches them
   (10 concurrent fetchers), stage 3 parses the HTML, stage 4 writes to a database.
   Implement with channels. Explain: how do you limit concurrency in stage 2? How do you
   handle errors without goroutine leaks?

3. **[STM-COMPOSE]** Explain why this is impossible with locks but trivial with STM:
   "transfer from account A to account B ONLY IF account C has balance > 0 - atomically."
   Implement in Haskell STM (or pseudocode).

4. **[DEADLOCK-IDENTIFY]** Thread A holds lockX, tries to acquire lockY.
   Thread B holds lockY, tries to acquire lockX. Thread C holds lockZ, tries lockX.
   Which pairs can deadlock? Which cannot? How do you fix the deadlock potential?

5. **[COMPARE]** A system needs to: process 100K events/second, each event updates a
   shared in-memory cache, and 1% of events trigger an email notification. Compare
   Actor, CSP, and STM approaches for this system. Which would you choose and why?

---

### 🧠 Think About This Before We Continue

**Q1.** The Actor model says "no shared state." But in practice, Akka clusters have
shared state: actors on different nodes need to agree on who owns which data (distributed state management).
How do real Akka systems handle distributed shared state?

*Hint: Akka Cluster Sharding: allows "virtual actors" that represent domain entities.
The entity (e.g., ShoppingCart-1234) is an actor with state. At any time, only ONE node
hosts this actor (location transparency: other nodes send messages to it, cluster routing delivers).
State is LOCAL to the actor on its current node.
On failure/rebalancing: the actor migrates to another node, state may be:
(1) Re-initialized from persistent storage (Akka Persistence: event sourcing with Journal).
(2) Re-created from scratch (ephemeral state).
Akka Persistence: actor state is persisted as an event log. On recovery: replay events.
This is EVENT SOURCING at the actor level.

Shared state across actors (genuinely shared data):
Akka Distributed Data (CRDTs): Conflict-free Replicated Data Types.
CRDTs allow distributed state that can be updated on any node and merged without conflict.
Examples: counter (increment on any node, merge = sum), set (add on any node, merge = union).
Not all data is CRDT-compatible (last-write-wins conflicts are a problem).

The Actor model's "no shared state" is correct at the SINGLE ACTOR level.
At the cluster level: shared state is handled through:
(1) Message passing to a "authority" actor (one canonical owner).
(2) Persistent event logs (replayed on recovery).
(3) CRDTs for commutative/associative operations.
The fundamental insight: shared state in a distributed Actor system is EXPLICIT and
INTENTIONAL - you design HOW state is shared. In shared-memory threading, sharing is
IMPLICIT and ACCIDENTAL - any field on a shared object is potentially shared.
The explicitness of Actor-model state sharing is what makes it manageable.*

**Q2.** Java Virtual Threads (Java 21) allow writing synchronous-looking blocking code
at high concurrency. In what ways are Virtual Threads similar to and different from Go goroutines?

*Hint: SIMILARITIES:
1. M:N SCHEDULING: Both Virtual Threads (Java 21) and Go goroutines are multiplexed
   onto a smaller number of OS threads. Many lightweight threads -> few OS threads.
2. BLOCKING I/O YIELDS: When a virtual thread blocks on I/O, the underlying OS thread is
   released to run another virtual thread. Same for goroutines: when a goroutine blocks,
   the runtime parks it and runs another goroutine on the OS thread.
3. SYNCHRONOUS CODE STYLE: Both allow writing sequential, blocking-style code that performs
   as well as callback/async code. No callback hell.
4. CHEAP CREATION: Creating 100K virtual threads or goroutines: low overhead. Creating 100K
   OS threads: impractical.

DIFFERENCES:
1. STRUCTURED CONCURRENCY:
   Java 21: StructuredTaskScope (JEP 453) provides hierarchical cancellation and error handling.
   Go: no built-in structured concurrency (use sync.WaitGroup + error channels manually or errgroup library).
2. CHANNEL COMMUNICATION:
   Go goroutines: first-class channel communication (CSP).
   Java VT: uses blocking queues, CompletableFuture, or shared-memory synchronization. No built-in channels.
3. PINNING:
   Java VT: a virtual thread that calls synchronized or native code can be PINNED to the carrier OS thread.
   While pinned: cannot yield. Heavy synchronized blocks = virtual thread pinning = reduced scalability.
   Go goroutines: no pinning concept (Go uses runtime-level mechanisms to handle preemption).
4. INTEGRATION:
   Java VT: works with existing Java concurrent code (synchronized, locks, thread-locals).
   Go goroutines: native Go constructs.
5. LANGUAGE DESIGN:
   Java VT: retrofitted onto existing thread model. Works with existing thread-blocking APIs.
   Go goroutines: designed from the start with CSP communication in mind.

PRACTICAL IMPLICATION:
Java VT: ideal for migrating existing Java codebases to high concurrency without refactoring.
Go goroutines: designed for CSP-style channel communication from day one.
For new concurrent code: Go's channel-first design is cleaner. For Java codebases: VT provides
comparable performance without rewriting existing code to async.*

---

### 🎯 Interview Deep-Dive

**Q1: "What is the Actor model and how does it solve concurrent programming problems?"**

*Why they ask:* Tests knowledge of concurrency models and Akka/Erlang. Common for distributed systems roles.

*Strong answer includes:*
- Actor: isolated state + async mailbox + single-threaded processing per actor.
- No shared state: actors communicate ONLY via message passing. Races impossible (no shared state).
- Fault tolerance: let-it-crash + supervisors. If actor crashes: supervisor restarts. Other actors unaffected.
- Lightweight: Erlang processes ~2KB. Java threads ~1MB. Millions of actors per node.
- Akka (JVM): actors as the primitive. ActorRef = typed message endpoint. Messages: immutable objects.
- Limitation: distributed state still needs message-based protocols. Mailbox overflow possible. UAF-equivalent: sending to dead actor (becomes dead letter).
- Use case: WhatsApp 2M connections/server. Telecoms (Erlang 9-nines availability). Event-driven microservices.

**Q2: "How do Go channels compare to Java's blocking queues?"**

*Why they ask:* Tests understanding of CSP concurrency model and Go vs Java idioms.

*Strong answer includes:*
- Go channels: language-level construct, supports `select` for multiple channels, unbuffered = rendezvous (both parties must be ready), buffered = asynchronous up to N items. Closing a channel signals completion (range-over-channel idiom). Type-safe (generic since Go 1.18).
- Java BlockingQueue: library construct, put/take block. No language-level multiplexing (no `select`). Must use separate threads per queue for multi-queue patterns (complex). No built-in close signal.
- Go's `select`: the key differentiator. Non-deterministic selection from multiple ready channels. Implements CSP's external choice. No Java equivalent without complex polling or additional synchronization.
- Java alternative for select: CompletableFuture.anyOf() (non-blocking, but different semantics). Project Loom's StructuredTaskScope: closer to structured concurrency but not channel-multiplexing.
- Best for: Go channels + select = clean pipeline and fan-out patterns. Java BlockingQueue + thread pools = producer-consumer patterns. Java 21 VT + BlockingQueue = high-concurrency producer-consumer without actor model overhead.
