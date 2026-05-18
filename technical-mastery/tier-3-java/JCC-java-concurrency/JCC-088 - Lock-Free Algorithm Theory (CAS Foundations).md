---
id: JCC-092
title: "Lock-Free Algorithm Theory (CAS Foundations)"
category: Java Concurrency
tier: tier-3-java
folder: JCC-java-concurrency
difficulty: ★★★
depends_on: JCC-079, JCC-083, JCC-047
used_by:
related: JCC-061, JCC-078, JCC-060
tags:
  - java
  - concurrency
  - advanced
  - algorithm
  - deep-dive
status: complete
version: 2
layout: default
parent: "Java Concurrency"
grand_parent: "Technical Mastery"
nav_order: 88
permalink: /technical-mastery/java-concurrency/lock-free-algorithm-theory-cas-foundations/
---

⚡ **TL;DR** - Lock-free algorithms guarantee system-wide progress
using CAS hardware primitives; theory provides correctness proofs
(linearisability), progress proofs, and the limits of what CAS can
express.

---

| Field      | Value                                              |
|------------|----------------------------------------------------|
| Depends on | JCC-079 Lock-Free Data Structures, JCC-083 JSR 133, JCC-047 CAS (Compare-And-Swap) |
| Related    | JCC-061 VarHandle, JCC-078 JMM Happens-Before, JCC-060 Atomic Classes |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Engineers implement "lock-free" data structures that have logical
errors (incorrect linearisation points, ABA vulnerabilities, memory
reclamation races) because they lack a formal framework for proving
correctness. Testing finds some bugs but cannot prove absence of
bugs in the face of all possible interleavings.

**THE BREAKING POINT:**
A lock-free queue with a subtle CAS ordering bug passes all tests
at 4 threads but fails at 64 threads in production because an
interleaving that never occurred in testing becomes likely at scale.
Without linearisability theory, the developer cannot prove whether
the algorithm is correct or just untested.

**THE INVENTION MOMENT:**
Maurice Herlihy and Jeannette Wing published "Linearizability: A
Correctness Condition for Concurrent Objects" (1990). Herlihy
followed with "Wait-Free Synchronization" (1991) introducing
consensus numbers - a formal measure of how powerful a synchronisation
primitive is. These gave concurrent algorithm developers a rigorous
correctness framework.

**EVOLUTION:**
- **1990:** Linearisability (Herlihy & Wing)
- **1991:** Wait-free synchronisation, consensus numbers (Herlihy)
- **1993:** Treiber stack (first lock-free Java structure)
- **1996:** Michael & Scott non-blocking queue (basis for `ConcurrentLinkedQueue`)
- **2004:** Hazard pointers (memory reclamation for lock-free in GC-less languages)
- **Now:** VarHandle (Java 9), formal model checking with TLA+

---

### 📘 Textbook Definition

**Linearisability** (Herlihy & Wing 1990): A concurrent execution
of operations is linearisable if each operation appears to take
effect atomically at some single point in time (*linearisation point*)
between its invocation and completion. Linearisability is the gold
standard for concurrent object correctness.

**Progress guarantees (hierarchy):**
- **Deadlock-free:** If some thread completes, the system makes
  progress (but others may starve)
- **Starvation-free:** Every thread eventually completes (fairness)
- **Lock-free:** At least one thread makes progress per "step"
  (system-wide progress; individual starvation possible)
- **Wait-free:** Every thread completes in bounded steps (strongest)

**Consensus number** of a primitive = the maximum number of threads
for which it can solve the consensus problem (agree on one value).
- Read/Write register: consensus number = 1 (cannot do 2-thread consensus)
- CAS: consensus number = ∞ (can solve consensus for any N threads)
- `getAndSet`: consensus number = 2

---

### ⏱️ Understand It in 30 Seconds

**One line:** Linearisability proves a concurrent algorithm is
equivalent to some sequential execution; consensus numbers prove
what synchronisation primitives can theoretically do.

**One analogy:**
> Linearisability is like a video replay test. Slow down the video
> of concurrent operations: if you can find a single moment where
> each operation "snapped into existence" atomically (in the order
> consistent with what each thread observed), the execution is
> linearisable.

**One insight:** CAS has consensus number infinity - it can
implement ANY concurrent algorithm correctly for any number of
threads. This makes CAS the universal building block for lock-free
concurrent data structures.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **Linearisability:** An operation's linearisation point is a
   single moment between its invocation and response where it appears
   atomically to occur. For CAS: the linearisation point is when
   the CAS instruction executes.
2. **CAS as consensus:** CAS can solve consensus (agreement among N
   threads on a single value) for any N. No read-modify-write
   sequence without CAS can solve consensus for N > 2.
3. **Universal construction:** Using only CAS, any sequential object
   can be transformed into a lock-free concurrent object (Herlihy's
   universal construction, 1991).
4. **Obstruction-freedom vs lock-freedom:** A CAS retry loop is
   obstr-free (one thread in isolation makes progress). Multiple
   threads with a single CAS can all fail simultaneously (livelock).
   Lock-free requires that SOME thread succeed ALWAYS.
5. **Memory reclamation:** Java GC handles this automatically. In C++,
   hazard pointers or epoch-based reclamation prevent ABA and
   use-after-free in lock-free structures.

**DERIVED DESIGN:**
The Michael-Scott queue proves lock-free progress because: when one
thread fails to complete an enqueue (CAS fails), another thread
either completes its OWN enqueue OR helps complete the failing
thread's partial enqueue ("helping" technique). At least one thread
always makes complete progress.

**THE TRADE-OFFS:**

**Gain:** Formal proofs of correctness; formal proofs of progress;
language for describing algorithm properties precisely.

**Cost:** High academic prerequisite; model checking tools (TLA+,
Alloy) required for complex algorithms; proofs don't automatically
translate to working code without discipline.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

**Essential:** Concurrent algorithm correctness requires reasoning
about all interleavings of concurrent operations. This is irreducibly
complex - informal reasoning fails.

**Accidental:** Theory papers use mathematical notation that is
inaccessible to most practitioners. TLA+ provides a more
engineering-friendly specification language.

---

### 🧪 Thought Experiment

**SETUP:** Prove the Treiber stack is linearisable.

```java
void push(T item) {
    Node<T> node = new Node<>(item);
    Node<T> current;
    do {
        current = top.get();
        node.next = current;
    } while (!top.compareAndSet(current, node)); // <-- LP
}
```

**LINEARISATION POINT ANALYSIS:**
- The linearisation point of `push` = the successful `compareAndSet`.
- At this exact instruction, `top` atomically changes from `current`
  to `node`. To any observing thread, the push appears to have
  happened in that single instant.
- `pop` LP = the successful CAS that changes `top` from `current`
  to `current.next`.
- If CAS fails, the operation did not yet "happen" - it retries
  until it finds a moment where it can atomically take effect.

**LOCK-FREE PROOF:**
- At each iteration, either THIS thread's CAS succeeds (progress
  for this thread), OR another thread's CAS succeeded (progress
  globally). Not all can fail simultaneously: exactly one CAS per
  winning instruction cycle succeeds. Therefore: some thread always
  makes progress.

**THE INSIGHT:** The linearisation point is WHY CAS works. Each
CAS is an atomic "time stamp" that makes an entire structural
change appear instantaneous.

---

### 🧠 Mental Model / Analogy

> Linearisability is the "observer test" for concurrent algorithms.
> Imagine a scientist observing the concurrent execution and slowing
> down time to find the exact nanosecond each operation "happened."
> If the scientist can always find such a nanosecond consistent
> with what each thread reported, the algorithm passes. If not,
> the algorithm is broken.

**Element mapping:**
- Observer slowing down time = correctness proof of linearisability
- "Exact nanosecond operation happened" = linearisation point (LP)
- "Consistent with what threads reported" = matching the sequential
  spec (sequential consistency of the data structure)
- CAS instruction = the LP for most lock-free operations

Where this analogy breaks down: in real algorithms, finding the LP
requires formal proof, not observation - the LP may be at different
instructions depending on the execution path.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Theory that proves concurrent algorithms are correct - not just
"works in most tests" but mathematically proven to work for all
possible interleavings of all threads.

**Level 2 - How to use it (junior developer):**
You likely won't implement lock-free algorithms from scratch. The
theory tells you which JDK classes are lock-free and why:
- `ConcurrentLinkedQueue`: lock-free (Michael-Scott queue)
- `LongAdder`: lock-free (Striped64 cells)
- `AtomicInteger.compareAndSet()`: lock-free (single CAS)

**Level 3 - How it works (mid-level engineer):**

**Linearisability verification steps:**
1. Identify all operation invocation/response pairs in a concurrent execution
2. For each operation, find a single "snap" moment (LP) where it
   appears to take effect
3. Show that the resulting sequential order satisfies the data
   structure's sequential specification
4. Show LPs are between invocation and response for each operation

**Consensus numbers** tell you what primitives you need:
- To solve consensus for N threads: need a primitive with consensus
  number >= N
- Read/Write: cannot do 2-thread consensus (consensus # = 1)
- CAS: can do infinity-thread consensus (consensus # = inf)

**Level 4 - Why it was designed this way (senior/staff):**
The consensus number hierarchy (Herlihy 1991) established that
hardware synchronisation primitives are not equal. Before this,
computer architects debated which primitives to include in CPUs.
The theory proved that any machine with CAS (and memory fences) can
implement any concurrent algorithm. This justified the hardware
decision to include `CMPXCHG` on x86 and `LDXR/STXR` on ARM as
the universal synchronisation primitives, which remain the
foundation of all concurrent software today.

**Expert Thinking Cues:**
- TLA+ (lamport's Temporal Logic of Actions) is the practical
  tool for specifying and model-checking lock-free algorithms.
  AWS uses TLA+ to verify DynamoDB and S3 algorithms.
- Hazard pointers (`std::hazard_pointer` in C++23): the formal
  theory behind safe memory reclamation in lock-free C++ code.
- Java GC eliminates the memory reclamation problem entirely -
  a major practical advantage of lock-free Java vs C++.
- C++ `std::atomic::compare_exchange_weak` vs `strong`:
  `weak` may fail spuriously (ARM `STXR` can fail without reason);
  `strong` retries internally. Java's `compareAndSet` uses `strong`.

---

### ⚙️ How It Works (Mechanism)

**Consensus number proof sketch (read/write cannot do 2-thread consensus):**
```
Theorem: Registers (read/write) have consensus number 1.
Proof sketch (by contradiction):
  Suppose R/W protocol agrees on one value for any
    2-thread start.
  Consider a bivalent configuration (both 0 and 1 still
    possible).
  - Thread 1 reads R: reading never changes state -> still
    bivalent
  - Thread 2 writes R: writes don't communicate read values
  - After any sequence of R/W: still bivalent
  ... [formal argument: cannot reach univalent state with
    only R/W]
  Therefore: cannot solve 2-thread consensus.
```

**CAS consensus number = infinity (intuition):**
```java
// 2-thread consensus via CAS:
int decide(int proposal) {
    // First thread to CAS wins; both get the winner's value
    memory.compareAndSet(EMPTY, proposal);
    return memory.get(); // both threads see the same value
}
```
CAS allows either thread to "claim" the common memory in one atomic
step. The winner's CAS succeeds; the loser's fails. Both then read
the same (winner's) value. Generalises to N threads.

**The "helping" technique (why Michael-Scott queue is lock-free):**
```
Thread 1 starts enqueue: CAS tail.next from null to newNode
  -> succeeds: partial state (tail.next != null but tail
    != newNode)

Thread 2 starts enqueue: observes tail.next != null
  -> "helps" Thread 1: CAS this.tail from old to tail.next
    (advance tail)
  -> now state is consistent
  -> Thread 2 can proceed with its own enqueue

Result: both Thread 1's partial work AND Thread 2's work
  progress.
System advances even when threads interleave at worst
  possible points.
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW (verifying lock-freedom):**
```
Implement candidate lock-free algorithm    <- YOU ARE HERE
       |
Identify CAS locations (LP candidates)
       |
Model in TLA+ specification
       |
Run TLC model checker: verify no invariant violation
  (safety: linearisability, correctness)
  (liveness: lock-freedom)
       |
Prove manually for publication:
  - Show CAS is the LP for each operation
  - Show "helping" ensures some thread always progresses
       |
Implement in Java using VarHandle / AtomicReference
       |
Verify with JCStress (exhaustive concurrent testing)
```

**FAILURE PATH:**
If model checking finds a counterexample: execution trace showing
an interleaving where all threads fail a CAS simultaneously -> the
algorithm is livelock-prone, not lock-free.

**WHAT CHANGES AT SCALE:**
- NUMA: multi-socket CAS operations are 5-10x slower than single-
  socket. Algorithms proven lock-free remain correct but may perform
  poorly due to coherence traffic.
- C++ vs Java: Java GC eliminates ABA for references; C++ requires
  hazard pointers or epoch-based reclamation to achieve the same
  safety guarantee.

---

### 💻 Code Example

**Annotated lock-free stack with linearisation points:**
```java
public class LFStack<T> {
    private final AtomicReference<Node<T>> top =
        new AtomicReference<>(null);

    private record Node<T>(T value, Node<T> next) {}

    // push() LP: the successful compareAndSet
    public void push(T item) {
        Node<T> node;
        Node<T> current;
        do {
            current = top.get();   // read: not yet linearised
            node = new Node<>(item, current);
        } while (!top.compareAndSet(current, node));
        // ^ LP: at this instruction, push atomically "happens"
    }

    // pop() LP: the successful compareAndSet
    public T pop() {
        Node<T> current;
        do {
            current = top.get();            // read: not yet LP
            if (current == null) return null; // LP: the read (empty)
        } while (!top.compareAndSet(current, current.next()));
        // ^ LP: at this instruction, pop atomically "happens"
        return current.value();
    }
}
```

**Using TLA+ specification (pseudocode - actual TLA+ is ASCII math):**
```
VARIABLES top, threads

INIT == top = {}  (* empty stack *)

Push(tid, item) ==
  /\ LET node = [value |-> item, next |-> top]
     IN top' = node    (* atomic CAS: LP of push *)
  /\ UNCHANGED threads

Pop(tid) ==
  /\ top /= {}
  /\ top' = top.next   (* atomic CAS: LP of pop *)
  /\ UNCHANGED threads

(* Invariant: at every state, stack contains exactly
  pushed - popped items *)
```

**Using JCStress (concurrent testing):**
```java
// JCStress tests exhaustively find interleavings conventional tests
// miss
@JCStressTest
@Outcome(id = "1, 0", expect = ACCEPTABLE,
    desc = "T1 popped item, T2 popped empty")
@Outcome(id = "0, 1", expect = ACCEPTABLE,
    desc = "T2 popped item, T1 popped empty")
@Outcome(id = "1, 1", expect = FORBIDDEN,
    desc = "Both cannot pop same item - stack corrupted")
@State
public class LFStackTest {
    LFStack<Integer> stack = new LFStack<>();

    @Actor public void actor1(I_Result r) {
        stack.push(1);
        Integer v = stack.pop();
        r.r1 = v != null ? 1 : 0;
    }
    @Actor public void actor2(I_Result r) {
        Integer v = stack.pop();
        r.r2 = v != null ? 1 : 0;
    }
}
```

---

### ⚖️ Comparison Table

| Correctness level | Definition | Java examples |
|------------------|-----------|--------------|
| Sequential consistency | Operations appear sequential (weaker than linearisability) | Some GPU operations |
| Linearisability | Each op has an atomic LP between invocation/response | `ConcurrentLinkedQueue`, `AtomicInteger.CAS` |
| Serializability | DB-level: transactions ordered as if sequential | Database ACID transactions |
| Quiescent consistency | All ops complete before observing | Some relaxed concurrent counters |

| Progress level | Guarantees | Example |
|---------------|-----------|---------|
| Deadlock-free | Some thread eventually progresses | `synchronized` |
| Starvation-free | Every thread progresses | `ReentrantLock(fair=true)` |
| Lock-free | Some thread progresses at every step | `ConcurrentLinkedQueue` |
| Wait-free | Every thread progresses in bounded steps | `AtomicInteger.get()` |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Lock-free means no synchronisation" | Lock-free uses the strongest synchronisation: CAS with full memory barriers. It eliminates mutual exclusion locks, not synchronisation. |
| "Linearisability is easy to verify by testing" | No concurrent test can enumerate all interleavings. Testing gives confidence; only formal verification (TLA+, Coq proofs) gives mathematical certainty. |
| "Any CAS-based algorithm is lock-free" | No. CAS retry loops can livelock if all threads' CAS always fail simultaneously (e.g., two-thread stack where neither can consistently win). Proving lock-freedom requires the "helping" or "some thread succeeds" argument. |
| "Java's GC makes all lock-free algorithms correct" | GC eliminates ABA for references. But ABA is still possible with integer-typed atomics. Use `AtomicStampedReference` when ABA threatens correctness. |
| "Wait-free is always better than lock-free" | Wait-free algorithms are typically much more complex and have higher constant-factor overhead. For most workloads, lock-free is the better trade-off. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: CAS livelock (all threads perpetually fail)**

**Symptom:** 100% CPU, zero throughput. Threads run without progress.

**Root Cause:** Algorithm not truly lock-free - a livelock exists
where all threads can simultaneously fail their CAS operations.

**Diagnostic:**
With JCStress: a liveness test that never terminates.
With TLA+: model checker reports a liveness violation ("deadlock"
in TLA+ = no thread makes progress).

**Fix:** Add "helping" mechanism: before retrying, the failing
thread completes any partial operations left by other threads.

---

**Failure Mode 2: ABA corrupts lock-free structure**

**Symptom:** Intermittent data corruption (incorrect dequeue results,
missing elements) in a lock-free queue implemented with C++/
object pool.

**Root Cause:** ABA: pointer A appears to be unchanged (CAS succeeds)
but the node at address A was freed and reallocated to a different
logical position.

**Diagnostic:** Java: this is virtually impossible with GC.
C++: add memory address tracking in stress test.

**Fix (Java preemptive):** Use `AtomicStampedReference` for
algorithms where integer counters could ABA (e.g., a lock-free
freelist with manual memory management).

---

**Failure Mode 3: Incorrect linearisation point assumed**

**Symptom:** JCStress `FORBIDDEN` outcome observed for cases that
"should be impossible."

**Root Cause:** The actual linearisation point is not where the
developer assumed, leading to a gap where another thread observes
an inconsistent intermediate state.

**Diagnostic:** 
```bash
# Run JCStress with verbose mode:
java -jar jcstress.jar -v -t YourTest
# Outputs the specific execution trace causing FORBIDDEN outcome
# Trace shows which thread ran which instruction at each step
```

**Fix:** Re-analyse the algorithm's linearisation points.
Use TLA+ to model and verify.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[JCC-079 - Lock-Free Data Structures]] - practical Java implementations
- [[JCC-083 - JSR 133 - Java Memory Model Specification]] - the
  memory model that defines when CAS results are visible
- [[JCC-047 - CAS (Compare-And-Swap)]] - the hardware primitive

**Builds On This (learn these next):**
- Herlihy & Wing (1990) - "Linearizability" paper (ACM TOPLAS)
- Herlihy (1991) - "Wait-Free Synchronization" paper
- TLA+ toolbox - model checking lock-free algorithms

**Alternatives / Comparisons:**
- [[JCC-061 - VarHandle]] - Java 9 access mode API implementing
  different memory ordering levels

---

### 📌 Quick Reference Card

```
+--------------------------------------------------+
| WHAT IT IS   | Formal theory for concurrent alg   |
|              | correctness via linearisability    |
+--------------+------------------------------------+
| PROBLEM      | Lock-free code correctness cannot  |
|              | be verified by testing alone       |
+--------------+------------------------------------+
| KEY INSIGHT  | CAS has consensus# = infinity;     |
|              | LP makes each op appear atomic     |
+--------------+------------------------------------+
| USE WHEN     | Implementing lock-free structures, |
|              | proving concurrent alg correctness |
+--------------+------------------------------------+
| AVOID WHEN   | Using existing JDK concurrent      |
|              | classes (already proven correct)   |
+--------------+------------------------------------+
| TRADE-OFF    | Mathematical certainty / requires  |
|              | formal methods expertise           |
+--------------+------------------------------------+
| ONE-LINER    | LP(CAS) = the instruction; if some |
|              | thread always wins -> lock-free    |
+--------------+------------------------------------+
| NEXT EXPLORE | TLA+ toolbox, JCStress,            |
|              | Herlihy & Wing 1990 paper          |
+--------------------------------------------------+
```

**If you remember only 3 things:**
1. Linearisation point: the exact moment a concurrent operation
   appears to take effect atomically. For CAS-based ops, the LP
   is the successful CAS instruction.
2. CAS consensus number = infinity: CAS can implement any concurrent
   data structure correctly for any number of threads.
3. "Helping": in lock-free algorithms, a failing thread completes
   another thread's partial operation - ensuring system-wide progress.

**Interview one-liner:** "Lock-free algorithm theory (Herlihy) proves
correctness via linearisability (each operation has an atomic
linearisation point) and lock-freedom via CAS's consensus number
infinity - guaranteeing that some thread always progresses without
mutual exclusion."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** For any system where formal
correctness matters, informal reasoning ("seems right") is
insufficient. Formal specification (TLA+, Alloy, type systems)
catches subtle invariant violations that exhaustive testing cannot,
because testing samples a finite subset of an exponential space
of interleavings.

**Where else this pattern appears:**
- **AWS DynamoDB:** Amazon published a TLA+ specification of
  DynamoDB's replication protocol before implementation. Model
  checking found subtle distributed race conditions that engineers
  missed in code review.
- **Paxos/Raft consensus algorithms:** These are proven lock-free
  at the distributed level - at least one node always makes progress
  as long as a majority is alive. The proof technique mirrors
  Herlihy's progress proofs for shared-memory algorithms.
- **CPU microarchitecture:** Modern out-of-order CPUs use formal
  methods to verify that instruction reorderings satisfy the
  architecture's memory model specification. Intel and ARM publish
  formal litmus tests for their memory models.

---

### 💡 The Surprising Truth

Herlihy's 1991 proof that read-modify-write instructions (`getAndSet`)
have a consensus number of only 2 - not infinity like CAS - had
an unexpected practical consequence: it proved that the `fetch-and-add`
instruction (increment and return old value, common in pre-CAS CPUs)
cannot solve consensus for 3 or more threads. This meant that any
concurrent algorithm requiring agreement among 3+ CPUs needed CAS
or an equivalent, not just any atomic instruction. Some CPUs of the
1970s-1980s that had `test-and-set` or `fetch-and-add` but not CAS
were, in a formal sense, computationally weaker for concurrent
programming than modern CPUs. This is one of the only cases where
a theoretical computer science result directly influenced which
hardware instructions CPU designers chose to include in their ISA.

---

### 🧠 Think About This Before We Continue

**Question 1 (First Principles):** Prove (informally) that a
stack implemented with a single atomic `top` reference and CAS
is lock-free. Find the exact interleaving where Thread A's `push`
CAS fails and show that Thread B's `push` CAS succeeds in the
same instruction cycle - and that this satisfies the lock-free
definition.

*Hint:* The key is "exactly one CAS winner per CMPXCHG bus cycle."
At the hardware level, two simultaneous CAS operations on the same
address cannot both succeed: the bus arbitration protocol ensures
one wins. This is the physical basis for lock-freedom.

---

**Question 2 (Design Trade-off):** You need a lock-free FIFO queue
that supports multiple producers and multiple consumers (MPMC)
with bounded capacity for a high-frequency trading system. Compare
`ConcurrentLinkedQueue` (unbounded, lock-free) vs LMAX Disruptor
(bounded ring buffer, wait-free reads, single-writer principle).
When does each win, and what linearisability guarantee does
Disruptor sacrifice for performance?

*Hint:* Research whether Disruptor is linearisable (it isn't,
strictly - it uses a weaker correctness condition called
"sequentially consistent" with its single-writer constraint).
Quantify the throughput difference in published benchmarks.

---

**Question 3 (Root Cause):** A colleague implements a lock-free
bounded counter (count from 0 to MAX, never exceed) using
`AtomicInteger` and a CAS loop. Under 100 threads all incrementing
simultaneously, the counter occasionally exceeds MAX by a few units.
Identify the linearisability violation, explain exactly which
interleaving causes the bug, and provide the correct implementation.

*Hint:* The bug: thread reads count < MAX, then thread is delayed,
another thread takes count to MAX, then original thread CAS sets
MAX+1 (despite its outdated read showing < MAX). The fix: the CAS
must include the bound check atomically. Research how `AtomicInteger`'s
`updateAndGet(prev -> prev < MAX ? prev + 1 : prev)` solves this.

