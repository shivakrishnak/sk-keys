---
layout: default
title: "Actor Model"
parent: "Java Concurrency"
nav_order: 370
permalink: /java-concurrency/actor-model/
number: "370"
category: Java Concurrency
difficulty: ★★★
depends_on: Thread (Java), ConcurrentHashMap, BlockingQueue, ExecutorService, Virtual Threads (Project Loom)
used_by: Structured Concurrency
tags:
  - java
  - concurrency
  - advanced
  - pattern
  - deep-dive
---

# 370 — Actor Model

`#java` `#concurrency` `#advanced` `#pattern` `#deep-dive`

⚡ TL;DR — A concurrency model where independent "actors" communicate exclusively via asynchronous message passing rather than shared mutable state, eliminating data races by design.

| #370 | Category: Java Concurrency | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Thread (Java), ConcurrentHashMap, BlockingQueue, ExecutorService, Virtual Threads (Project Loom) | |
| **Used by:** | Structured Concurrency | |

---

### 📘 Textbook Definition

The **Actor Model** is a mathematical model of concurrent computation in which the fundamental unit of computation is an *actor* — an independent entity with private state, a mailbox (message queue), and a behaviour function. Actors communicate exclusively via asynchronous message passing; they never share memory directly. Upon receiving a message, an actor can: send messages to other actors, create new actors, or change its own behaviour for the next message. The Actor Model decouples state from concurrency by ensuring state mutation occurs only within the actor's single-threaded processing loop, while all inter-component communication is inherently asynchronous and non-blocking. In Java, the Actor Model is implemented by frameworks such as Akka, Vert.x, and (with virtual threads) via pattern-based implementations.

### 🟢 Simple Definition (Easy)

The Actor Model is like a company where every employee has their own inbox — you send them a message and move on; they process it when they're ready. Nobody shares a desk, causing no conflicts.

### 🔵 Simple Definition (Elaborated)

Traditional concurrent programming uses shared memory protected by locks. The Actor Model eliminates the shared memory problem entirely: each actor owns its state exclusively and changes it only when processing a message. No two actors touch the same data simultaneously because actors only communicate by passing copies of data in messages. This makes concurrent programs much easier to reason about — you only need to understand what an actor does with the messages it receives, not how multiple threads interleave. The trade-off: message passing has overhead, and debugging asynchronous message flows is harder than debugging sequential code.

### 🔩 First Principles Explanation

**Why shared-memory concurrent programming is hard:**

Any mutable state accessed by multiple threads requires synchronisation. Get it wrong: race conditions, deadlocks, memory visibility bugs. Get it right: performance bottlenecks from lock contention, complex reasoning about invariants.

**Actor Model's solution:**

1. **No shared mutable state.** Actors own their state; no other actor can read or write it directly.
2. **Mailbox serialisation.** Each actor processes one message at a time from its mailbox. No concurrent execution within a single actor = no need for locks on actor-internal state.
3. **Location transparency.** Actors communicate via addresses (actor refs) — whether the actor is local or remote, synchronous or asynchronous is abstracted away.
4. **Failure isolation.** Actor failures are contained — they don't corrupt shared state. Supervisor actors can detect child failures and restart them (Erlang/Akka "let it crash" philosophy).

**In Java with Akka Typed (modern):**

```
ActorRef<Command>  →  send typed message →  Actor's mailbox
                                             │
                                   Actor processes msg
                                   (single-threaded per actor)
                                             │
                                   Update internal state
                                   Send messages to other actors
```

**Mapping to Java threads:**

Actors are not threads — many actors share a small thread pool. Each actor's mailbox is a queue; the dispatcher (thread pool) processes messages from each actor's queue one at a time. This is the same multiplexing concept as virtual threads: lightweight work items mapped onto a fixed thread pool.

**Java's virtual threads and actors:**

Java's virtual threads (Project Loom) allow a simpler actor-like pattern without a dedicated framework. Each active actor runs in its own virtual thread reading from a `LinkedBlockingQueue` — the virtual thread blocks on `queue.take()` and the JVM unmounts/remounts it cheaply between messages.

### ❓ Why Does This Exist (Why Before What)

WITHOUT Actor Model (shared-memory concurrency):

- All shared data requires locks → potential deadlocks, contention, complex reasoning.
- Race conditions in concurrent code are time-sensitive and hard to reproduce.
- Distributed shared state is even harder — network adds failures.

What breaks without it:
1. Lock hierarchies for complex systems become unmaintainable.
2. Horizontal scaling across machines requires distributed locking — expensive and fragile.

WITH Actor Model:
→ Concurrency bugs eliminated by design — no shared state to race on.
→ Natural distribution model — actor message passing works identically across threads, processes, and machines.
→ Fault isolation via supervision hierarchies — crashed actors don't corrupt others.

### 🧠 Mental Model / Analogy

> An actor system is like a company of workers who communicate only by email. Each worker has their own inbox and processes one email at a time — they never share a desk or look at someone else's files. If Worker A wants something from Worker B, A sends an email and continues working. B will process it when ready and may reply asynchronously. Nobody waits for anyone else's approval to continue. The company scales by hiring more workers (actors) — without any need for everyone to gather in a meeting room (shared lock).

"Workers" = actors, "inbox" = mailbox/message queue, "email" = asynchronous message, "no shared desks" = no shared mutable state, "hiring more workers" = creating new actors.

The key insight: concurrency problems arise from sharing, so eliminate sharing. Communication through messages is the only interaction.

### ⚙️ How It Works (Mechanism)

**Message flow diagram:**

```
┌──────────────────────────────────────────┐
│  Actor A                                  │
│  State: {count: 42}                       │
│  Mailbox: [Increment, GetCount, Increment]│
│                                           │
│  Processing Increment:                   │
│    count = count + 1  → {count: 43}      │
│    (single-threaded; no lock needed)     │
└──────────────────────────────────────────┘
        ↑ sends reply to Actor B
Actor B sends ask(GetCount)
        ↓ receives Future<Integer>
```

**Actor lifecycle:**

```
Created → Idle (waiting for message)
          ↓ message arrives
        Processing (one message at a time)
          ↓ done processing
        Idle again (or terminated)
```

**Supervision hierarchy:**

```
Root Supervisor
├── UserSupervisor
│   ├── UserActor(user-1)
│   ├── UserActor(user-2)
│   └── UserActor(user-3)  ← fails → supervisor restarts it
└── OrderSupervisor
    └── OrderActor(order-42)
```

### 🔄 How It Connects (Mini-Map)

```
Traditional: threads + shared memory + locks
                     ↓ alternative model
Actor Model ← you are here
  (actors + private state + message passing)
                     ↓ Java frameworks
Akka (Scala/Java) | Vert.x (Java) | JActors
                     ↓ lightweight alternative
Virtual Threads + LinkedBlockingQueue
  (actor-like pattern without framework)
```

### 💻 Code Example

Example 1 — Minimal actor implementation with virtual threads:

```java
import java.util.concurrent.*;
import java.util.function.Consumer;

// Simple actor using virtual thread + BlockingQueue
public class Actor<T> {
    private final BlockingQueue<T> mailbox =
        new LinkedBlockingQueue<>();
    private Thread thread;

    public Actor(Consumer<T> handler) {
        thread = Thread.ofVirtual().start(() -> {
            try {
                while (!Thread.interrupted()) {
                    T message = mailbox.take(); // unmounts VT
                    handler.accept(message);   // process
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        });
    }

    public void send(T message) {
        mailbox.offer(message); // non-blocking, fire-and-forget
    }

    public void stop() { thread.interrupt(); }
}

// Usage:
Actor<String> actor = new Actor<>(msg ->
    System.out.println("Processing: " + msg));
actor.send("Hello");
actor.send("World");
```

Example 2 — Counter actor with no synchronisation needed:

```java
// No locks needed — single actor owns its state
sealed interface CounterMsg {
    record Increment() implements CounterMsg {}
    record Get(CompletableFuture<Integer> reply)
        implements CounterMsg {}
}

var counter = new Actor<CounterMsg>(new Consumer<>() {
    int count = 0; // actor-private state — no volatile needed!

    public void accept(CounterMsg msg) {
        switch (msg) {
            case CounterMsg.Increment() -> count++;
            case CounterMsg.Get(var reply) ->
                reply.complete(count);
        }
    }
});

// Query actor asynchronously
CompletableFuture<Integer> result = new CompletableFuture<>();
counter.send(new CounterMsg.Get(result));
System.out.println(result.get()); // "2" after 2 increments
```

Example 3 — Akka Typed mini-example (production use):

```java
// Akka Typed Actor (production-grade, Java API)
import akka.actor.typed.*;
import akka.actor.typed.javadsl.*;

public class CounterActor
    extends AbstractBehavior<CounterActor.Command> {

    sealed interface Command {}
    record Increment() implements Command {}
    record GetCount(ActorRef<Integer> replyTo)
        implements Command {}

    private int count = 0;

    private CounterActor(ActorContext<Command> ctx) {
        super(ctx);
    }

    public static Behavior<Command> create() {
        return Behaviors.setup(CounterActor::new);
    }

    @Override
    public Receive<Command> createReceive() {
        return newReceiveBuilder()
            .onMessage(Increment.class,
                msg -> { count++; return this; })
            .onMessage(GetCount.class,
                msg -> { msg.replyTo().tell(count); return this; })
            .build();
    }
}
```

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| One actor = one thread | Actors are multiplexed over a thread pool; thousands of actors can share a small set of threads (similar to virtual threads). |
| Actor Model has no race conditions possible | Actors still face logical races between messages — e.g., two "withdraw" messages arriving in sequence may still cause over-withdrawal if balance not checked between them. The model eliminates data races, not logical races. |
| Akka is the only Actor implementation in Java | Akka is the most popular, but Vert.x, Quasar, JActors, and custom virtual-thread approaches all implement actor-like patterns in Java. |
| Messages are always delivered reliably | Without a message persistence layer, in-memory actor messages can be lost if the actor system crashes. Akka Persistence adds durability via event sourcing. |
| Actor Model is always better than lock-based concurrency | For simple local concurrency, lock-based code (with ConcurrentHashMap etc.) has lower overhead. Actor Model shines for distributed systems and complex state machines. |

### 🔥 Pitfalls in Production

**1. Shared Mutable Objects Passed in Messages — Defeating the Model**

```java
// BAD: Passing a mutable object in a message
List<String> sharedList = new ArrayList<>();
actor.send(sharedList); // actor and caller share the same list!
sharedList.add("mutation after send"); // actor sees this!
// → Data race on sharedList

// GOOD: Pass immutable copies or value types
actor.send(List.copyOf(sharedList)); // defensive copy
// Or: use immutable types (java.util.List.of(), records)
```

**2. Unbounded Mailbox — OOM Under Backpressure**

```java
// BAD: LinkedBlockingQueue with no bound → grows unboundedly
// under load producer sends faster than actor processes
BlockingQueue<Msg> mailbox = new LinkedBlockingQueue<>();

// GOOD: Bound the mailbox and apply backpressure to senders
BlockingQueue<Msg> mailbox =
    new LinkedBlockingQueue<>(10_000); // bounded
// Sender: if mailbox full → offer() returns false → throttle
if (!mailbox.offer(msg)) {
    // apply backpressure: slow down sender or drop message
}
```

**3. Synchronous Ask Pattern Blocking All Threads**

```java
// BAD: Calling actor.ask() inside another actor's message handler
// → blocks the current thread waiting for reply
// → under high load, depletes the actor thread pool
String result = actor.ask(query).toCompletableFuture().get();

// GOOD: Use pipe-to-self pattern or non-blocking ask
actor.ask(query).thenAccept(result ->
    self.tell(new ResultReceived(result)));
// or: use Akka's pipe for async response handling
```

### 🔗 Related Keywords

- `Virtual Threads (Project Loom)` — enable lightweight actor-like patterns without frameworks.
- `BlockingQueue` — the mailbox primitive in manual actor implementations.
- `Structured Concurrency` — shares the "bounded lifetime" philosophy with actor supervision.
- `ConcurrentHashMap` — used for actor registries (looking up actor refs by address/ID).
- `Scoped Values` — context propagation within an actor's message processing scope.

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Actors = private state + mailbox + message│
│              │ passing. No shared state → no data races. │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Complex concurrent state machines; dist-  │
│              │ ributed systems; fault-tolerant systems;  │
│              │ high actor count (Akka, Vert.x).          │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Simple local concurrency — ConcurrentHash │
│              │ Map + VarHandle has far lower overhead;   │
│              │ synchronous request-response flows.       │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Actors: share nothing, message everything│
│              │ — concurrency through isolation."         │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Virtual Threads → Structured Concurrency  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** An e-commerce system models each user's cart as an actor. When a user checks out, the cart actor must coordinate with an inventory actor (to reserve items), a payment actor (to charge the card), and an order actor (to create the order) — all of which can fail independently. Design the message flow for a reliable checkout using actor supervision, explaining how you would handle the case where payment succeeds but order creation fails — specifically, how the failure propagates and what compensating messages are sent.

**Q2.** In the Actor Model, actors should never share mutable state. However, multiple actors in the same JVM process share the same heap. A Java actor framework like Akka uses a dispatcher thread pool to run actor message handlers. Under what circumstances can Java's memory model allow one actor to "see" uncommitted writes from another actor's message handler — even without explicitly sharing object references — and what mechanism does Akka's dispatcher use to prevent this from causing data visibility bugs between actors?

