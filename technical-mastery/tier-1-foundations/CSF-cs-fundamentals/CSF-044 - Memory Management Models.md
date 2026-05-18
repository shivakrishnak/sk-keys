---
id: CSF-044
title: Memory Management Models
category: CS Fundamentals - Paradigms
tier: tier-1-foundations
folder: CSF-cs-fundamentals
difficulty: ★★☆
depends_on: CSF-013, CSF-026
used_by: CSF-045, CSF-046, JVM-001
related: CSF-047, OSY-012
tags: [memory-management, garbage-collection, stack, heap, reference-counting]
status: complete
version: 4
layout: default
parent: "CS Fundamentals - Paradigms"
grand_parent: "Technical Mastery"
nav_order: 44
permalink: /technical-mastery/csf/memory-management-models/
---

⚡ TL;DR - Memory management determines how a program
allocates, uses, and reclaims memory. Models: manual
(C/C++), automatic garbage collection (Java/Go), reference
counting (Swift/Python), and ownership/borrow checker
(Rust). Each trades performance control for safety.

| #044 | Category: CS Fundamentals - Paradigms | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | CSF-013 (OOP), CSF-026 (Imperative Programming) | |
| **Used by:** | CSF-045 (GC Algorithms), CSF-046 (Memory Leak Detection), JVM-001 (JVM Architecture) | |
| **Related:** | CSF-047 (Concurrency vs Parallelism), OSY-012 (Virtual Memory) | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**

In the earliest programming languages and assembly code,
the programmer manages every byte of memory. You allocate
a block with `malloc`, use it, and `free` it when done.
The CPU does not care whether a memory address is valid;
it will write to whatever address you give it. Bugs:
- Use-after-free: access memory after it was freed
- Double-free: free the same memory twice (corruption)
- Memory leak: allocate and never free (process grows until OOM)
- Buffer overflow: write beyond allocated bounds (security exploit)
- Dangling pointer: hold a pointer to freed memory
These bugs cause crashes, data corruption, and security
vulnerabilities. They are the root cause of the majority
of critical security CVEs in C/C++ systems.

**THE BREAKING POINT:**

C programs in the 1970s-80s had entire categories of bugs
that were difficult to detect and reproduce. A use-after-free
in a rarely-executed code path might surface only after
days of uptime. The programmer had to mentally track every
allocation and ensure every code path freed it exactly once.
For large programs with multiple developers, this became
impractical. The cost: security vulnerabilities, crashes,
unreliable software.

**THE INVENTION MOMENT:**

John McCarthy introduced garbage collection in Lisp (1959):
the runtime automatically reclaims memory that is no longer
reachable. This transferred the memory management burden
from the programmer to the runtime. The cost: non-deterministic
pause times (GC runs when the runtime decides), higher
memory usage (GC needs headroom), and reduced control
over exactly when memory is reclaimed. Java (1995) made
GC the default for enterprise software. Rust (2015) took
a different path: an ownership and borrow system that the
COMPILER enforces - no runtime GC, no pauses, but compile-time
rules about who owns what memory. Multiple models exist
because the tradeoffs suit different use cases.

---

### 📘 Textbook Definition

**Memory management model:** The mechanism by which a program
acquires and releases memory during execution. Models:

**Manual management:** The programmer allocates (`malloc`)
and frees (`free`) memory explicitly. Maximum control,
highest risk. (C, C++)

**Garbage Collection (GC):** The runtime tracks which objects
are reachable and automatically reclaims unreachable objects.
No programmer burden, but non-deterministic pauses. (Java, Go, Python, C#)

**Reference Counting:** Each object tracks how many references
point to it. When count reaches zero, memory is freed.
Predictable reclamation; cannot handle reference cycles
without additional mechanism. (Swift ARC, CPython)

**Ownership/Borrow Checking:** Compiler rules track ownership
of memory at compile time. No runtime overhead, no GC
pauses, no dangling pointers - enforced by the compiler.
(Rust)

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Memory management = who is responsible for freeing memory.
Manual = you; GC = the runtime; reference counting = shared
ownership with auto-release; ownership = compiler-enforced one owner.

**One analogy:**

> You rent a conference room (allocate memory).
>
> Manual (C): you must call the front desk to cancel.
> Forget to call? Room is booked forever (memory leak).
> Cancel twice? System crashes (double-free).
>
> GC (Java): the hotel checks every hour if anyone is still
> using the room. If not, they cancel it automatically.
> Sometimes the check happens at an inconvenient moment (GC pause).
>
> Reference counting (Swift): each person who needs the room
> increments a counter. When the last person leaves, the
> room is automatically cancelled. Works unless two people
> agree "I won't leave until you do" (reference cycle - room never released).
>
> Ownership (Rust): one person "owns" the booking. Transferring
> ownership means the old owner cannot enter anymore. The
> compiler enforces this - no accidental double-use.

**One insight:**

Java's GC was designed for THROUGHPUT workloads: scientific
computing, batch processing, applications where total
work per time unit matters more than any individual response
time. GC pauses (stop-the-world) were acceptable. Modern
Java applications (low-latency APIs, trading systems) cannot
accept GC pauses. This drove the development of ZGC and
Shenandoah (near-zero pause GCs). But even with sub-millisecond
pauses, GC remains non-deterministic. Rust and real-time
C++ exist for hard real-time systems where GC is unacceptable.

---

### 🔩 First Principles Explanation

**MEMORY REGIONS:**

```
┌──────────────────────────────────────────────────────┐
│ Process Memory Layout                                │
│                                                      │
│ ┌──────────┐  High address                          │
│ │  Stack   │  - Local variables, method frames      │
│ │          │  - LIFO: allocated on call, freed       │
│ │          │    on return                            │
│ │  (grows  │  - Fixed max size (default: ~1MB-8MB)  │
│ │   down)  │  - Automatic: no programmer action      │
│ ├──────────┤                                         │
│ │   Heap   │  - Objects, dynamically-sized data      │
│ │          │  - Lives until freed (GC / manual)      │
│ │  (grows  │  - Unlimited (up to virtual memory)     │
│ │   up)    │  - Where GC operates (for GC languages) │
│ ├──────────┤                                         │
│ │  Static/ │  - Global variables, class metadata     │
│ │   BSS    │  - Lives for program lifetime           │
│ ├──────────┤                                         │
│ │  Code    │  - Compiled instructions (read-only)    │
│ └──────────┘  Low address                           │
└──────────────────────────────────────────────────────┘
```

**REFERENCE COUNTING AND CYCLES:**

```
┌──────────────────────────────────────────────────────┐
│ Parent -> Child (ref count: Child = 1)               │
│ Child -> Parent (ref count: Parent = 1)              │
│                                                      │
│ Drop Parent reference from outside:                  │
│   External ref to Parent = 0                         │
│   BUT: Child still holds ref to Parent -> count = 1  │
│         Parent still holds ref to Child  -> count = 1 │
│   Neither reaches 0. MEMORY LEAK.                    │
│                                                      │
│ Fix: weak references (Swift: `weak var parent`)      │
│   Weak refs do NOT increment the count.              │
│   When Parent is collected, weak ref becomes nil.    │
└──────────────────────────────────────────────────────┘
```

---

### 🧪 Thought Experiment

**RUST OWNERSHIP AT COMPILE TIME:**

```rust
fn main() {
    let s1 = String::from("hello"); // s1 owns the string
    let s2 = s1;                    // MOVE: s1 no longer owns it
    println!("{}", s1); // COMPILE ERROR: s1 was moved
    // Rust prevented use-after-move at compile time
    // No runtime check needed; no use-after-free possible

    let s3 = String::from("world");
    let s4 = s3.clone();            // CLONE: both own a copy
    println!("{} {}", s3, s4);      // OK: both valid

    // Borrowing (reference without ownership transfer):
    let s5 = String::from("foo");
    let len = calculate_length(&s5); // borrow s5 (read-only)
    println!("{}: {}", s5, len);    // s5 still valid: not moved
}
```

The compiler verifies: at every point, each piece of heap
memory has exactly ONE owner. When the owner goes out of
scope, the memory is freed. No GC. No runtime check.
No possible use-after-free.

**THE LESSON:**

Rust's ownership model eliminates entire categories of
memory bugs AT COMPILE TIME. The trade-off: a steep
learning curve (the borrow checker rejects programs that
LOOK correct to the programmer but would be unsafe).
The reward: a program that compiles is guaranteed to have
no memory safety violations - a guarantee no GC language
can make (GC prevents dangling pointers but not all memory
bugs, e.g., logical leaks).

---

### 🎯 Mental Model / Analogy

**LIBRARY BOOKS:**

Manual: you borrow a book. No one tracks it. If you forget
to return it, it's gone forever (leak). If you return it
twice, chaos (double-free).

GC: the library has a robot that checks every shelf every
night. Books that no one is using are returned to circulation.
The robot check takes a few seconds (GC pause).

Reference counting (Swift ARC): a barcode tracks how many
people checked out the book. When the last person returns it,
it goes back to circulation. If two people "check it out
for each other" (cycle), the book stays checked out forever.

Ownership (Rust): the book is assigned to one person.
To pass it to another person, the first person gives it up.
The compiler ensures at any moment, exactly one person has it.

**MEMORY HOOK:**

"Manual: you own, you free, maximum control.
GC: runtime finds unreachable, frees; pause times.
Reference counting: count to zero = free; cycles = leak.
Ownership (Rust): compiler ensures one owner; no GC, no pauses."

---

### 📊 Gradual Depth - Five Levels

**Level 1 - Child:**
Memory is like desk space. Programs put things on the desk.
When done, they clear them. Sometimes a program forgets
to clear (memory leak). GC is a cleaning robot that clears
things nobody is using. Rust is like having a strict rule:
you can only use one thing at a time, and the teacher
enforces it.

**Level 2 - Student:**
Stack: allocated and freed automatically with method calls.
Heap: allocated explicitly (new, malloc); freed manually
or by GC. Java's `new Object()` allocates on the heap.
When no references point to the object, GC frees it.
The root set (stack variables, static fields) is the starting
point for reachability analysis.

**Level 3 - Professional:**
JVM heap regions: Young Generation (new objects, frequent GC),
Old Generation (long-lived objects, infrequent GC), Metaspace
(class metadata). Minor GC (Young Gen): fast, frequent.
Major GC (Old Gen): slow, infrequent (formerly "Full GC").
GC tuning: `-Xms` (initial heap), `-Xmx` (max heap), GC
algorithm selection (`-XX:+UseG1GC`, `-XX:+UseZGC`).

**Level 4 - Senior Engineer:**
Off-heap memory (Java `ByteBuffer.allocateDirect()`): memory
outside the JVM heap, not subject to GC. Used for large
caches (Apache Ignite, Netty), file I/O buffering, and
memory-mapped files. Faster for I/O (no copy between JVM
and OS). But: must be managed carefully (not freed until
`ByteBuffer` is GC'd, which may be delayed). `Cleaner` API
(Java 9+) provides deterministic off-heap cleanup.

**Level 5 - Expert:**
JVM Project Valhalla: value types (Java 23+ preview). Value
types are allocated on the stack or inline in arrays, not
on the heap. No object header (8-16 bytes per object eliminated).
No GC pressure from value types. For a `Point(x, y)` that
is short-lived, this eliminates allocation entirely.
Arrays of value types become dense (like C struct arrays),
dramatically improving cache efficiency. This is the JVM
catching up to what C++ has had since always. Until Valhalla,
Java's GC operates on a heap with EVERY object (even
`Integer`, `Point`, `Pair`) allocated as a heap object with
a header.

---

### ⚙️ How It Works (Formal Basis)

**REACHABILITY IN GC:**

```
┌──────────────────────────────────────────────────────┐
│ Root Set (GC Roots):                                 │
│   - Local variables on thread stacks                 │
│   - Static fields                                    │
│   - JNI global references                            │
│   - Synchronized objects (monitor references)        │
│                                                      │
│ GC traverses: starting from roots, follow all        │
│ references (object graph). Anything reachable =      │
│ LIVE (keep). Anything not reachable = GARBAGE        │
│ (can reclaim).                                       │
│                                                      │
│ Key insight: "no reference" does NOT mean the object │
│ is gone (as in manual memory); it means the GC MAY   │
│ reclaim it. Finalization allows a last action before  │
│ reclamation (deprecated in Java 18 - use Cleaners).  │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: Memory Leaks in Java**

```java
// BAD #1: Static collection holding references (GC can't reclaim)
class EventRegistry {
    private static final List<EventListener> listeners = new ArrayList<>();
    // listeners grows forever; old listeners never removed
    void register(EventListener listener) {
        listeners.add(listener);  // LEAK: listener can never be GC'd
    }
}

// BAD #2: Unclosed resources (off-heap memory, file handles)
void process() throws Exception {
    InputStream stream = new FileInputStream("data.txt");
    // Exception thrown before close() -> stream never closed
    // Off-heap buffer (OS file handle) leaks
}

// GOOD #1: WeakReference for optional listeners (GC-friendly)
class EventRegistry {
    private final List<WeakReference<EventListener>> listeners = new ArrayList<>();
    void register(EventListener listener) {
        listeners.add(new WeakReference<>(listener));
        // GC can reclaim listener even though registry holds a ref
    }
}

// GOOD #2: try-with-resources (auto-close guaranteed)
void process() throws Exception {
    try (InputStream stream = new FileInputStream("data.txt")) {
        // stream.close() called automatically on exit (even exception)
        process(stream);
    }
}
```

**Example 2 - Memory Monitoring Diagnostic Commands**

```bash
# JVM: check heap usage
jstat -gc <pid> 5s        # GC stats every 5 seconds
jmap -heap <pid>          # heap summary (Java < 17)
jhsdb jmap --heap ...     # heap summary (Java 17+)

# GC logs (add to JVM args):
-Xlog:gc*:file=gc.log:time,uptime,level,tags:filecount=5,filesize=10m

# Heap dump for memory leak analysis:
jmap -dump:format=b,file=heap.hprof <pid>
# Then analyze with Eclipse MAT or VisualVM
```

---

### ⚖️ Comparison Table

| Model | Language | GC Pause | Safety | Latency | Use Case |
|---|---|---|---|---|---|
| Manual (malloc/free) | C, C++ | None | None (unsafe) | Predictable | OS, drivers, embedded |
| Tracing GC | Java, Go, C# | Yes (ms to s) | High | Variable | Enterprise, web |
| Reference Counting | Swift (ARC), CPython | None | High (no cycles) | Predictable | Mobile, scripting |
| Ownership/Borrow | Rust | None | High (compile-time) | Predictable | Systems, embedded |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "GC prevents all memory leaks in Java" | GC prevents dangling pointer bugs (use-after-free). It does NOT prevent LOGICAL memory leaks: objects that are still reachable (held in a collection, a static field, a listener list) but no longer needed. These objects will never be GC'd because they are reachable. Static collections, caches, and event listener registries are common Java memory leak patterns. |
| "Rust has no memory management overhead" | Rust's ownership model eliminates GC overhead but adds compile-time complexity. Reference counting (`Rc<T>`, `Arc<T>`) is available when single ownership is not sufficient. `Arc<T>` (atomic reference count for multi-threading) has runtime overhead similar to C++'s `shared_ptr`. Rust's model is not free - it shifts the cost from runtime to compile time and programmer cognitive overhead. |
| "GC pause times are always noticeable" | Modern GC algorithms (ZGC, Shenandoah, G1) achieve sub-millisecond pauses. ZGC (Java 15+) achieves pauses under 1ms even with multi-terabyte heaps. The "GC pauses make Java unsuitable for low-latency" concern is outdated for most workloads. High-frequency trading (microsecond requirements) still avoids GC; but sub-millisecond is acceptable for most financial and real-time web services. |
| "Stack memory is faster than heap memory" | Both stack and heap memory access is RAM - same hardware speed. The performance difference is due to CACHE LOCALITY and ALLOCATION COST. Stack allocation is a pointer decrement (nanoseconds); heap allocation requires finding free space (more complex). Stack memory is typically in cache (recently used). Heap objects are scattered; accessing many heap objects causes cache misses. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Java Memory Leak from Static Fields**

**Symptom:** Java application's heap usage grows steadily
over time, never decreasing. GC runs frequently but
recovers little memory. Eventually: OutOfMemoryError.

**Root Cause:** Objects accumulate in a static collection
(cache, listener registry, session store) without eviction.
GC cannot reclaim them because they are reachable via
static fields.

**Diagnosis:**
1. Take heap dumps at T0 and T+30min: `jmap -dump:format=b,file=heap.hprof <pid>`
2. Analyze with Eclipse Memory Analyzer (MAT): "Leak Suspects" report
3. Find the dominator tree: what objects hold the most retained heap
4. Trace back to the root reference (usually a static field)

**Failure Mode 2: Off-Heap Memory Leak with Direct ByteBuffers**

**Symptom:** Process memory grows (RSS in `top`) but JVM
heap usage is normal. Eventually: OOM from OS (not JVM).

**Root Cause:** `ByteBuffer.allocateDirect()` allocates
off-heap memory managed by the OS. The `ByteBuffer` object
on the JVM heap is small; the off-heap memory is large.
GC collects the `ByteBuffer` object eventually, triggering
the Cleaner to free off-heap memory. But if `ByteBuffer`
objects pile up faster than GC collects them, off-heap
memory grows unboundedly.

**Fix:** Reuse `ByteBuffer` objects via a pool. Use
`System.gc()` as a hint (not guaranteed) to trigger Cleaner.
Or switch to a buffer pool library (Netty's `ByteBuf`).

---

**Security Note:**

Memory safety vulnerabilities are the root cause of the
majority of critical CVEs in C/C++ codebases. CISA (US
Cybersecurity Agency) recommends "memory-safe languages"
(Rust, Java, Go, Python) for new systems development.
Specific threats: buffer overflow (write beyond buffer
bounds: classic attack vector for code injection),
use-after-free (reuse of freed memory: attacker controls
what is allocated next), heap spray (fill heap with exploit
code, trigger use-after-free to jump to it).
GC languages eliminate dangling pointer and use-after-free
by making memory only reclaimed when unreachable. Rust
eliminates them at compile time. C/C++ with AddressSanitizer
(runtime check) can detect but not prevent. Memory-safe
language choice is a security architecture decision.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `OOP` (CSF-013) - objects live on the heap; object lifetime
  is what GC manages
- `Imperative Programming` (CSF-026) - manual memory management
  is the imperative model; GC is the abstraction above it

**Builds On This (learn these next):**
- `GC Algorithms Overview` (CSF-045) - specific GC algorithms
  (G1, ZGC, Shenandoah, generational GC)
- `Memory Leak Detection` (CSF-046) - tools and techniques
  for diagnosing JVM memory leaks
- `JVM Architecture` (JVM-001) - JVM heap regions and memory model

---

### 📌 Quick Reference Card

```
┌────────────────────────────────────────────────────────┐
│ STACK        │ Local vars, frames. Auto freed on return│
│ HEAP         │ Objects. GC/manual reclaim              │
├──────────────┼─────────────────────────────────────────┤
│ MANUAL       │ malloc/free. Control. No safety. C/C++  │
│ GC (TRACING) │ Runtime tracks reachability. Pauses.   │
│              │ Java, Go, C#, Python, Ruby             │
│ REF COUNT    │ ARC. Count to 0 = free. Cycles = leak. │
│              │ Swift, CPython                          │
│ OWNERSHIP    │ Compiler-enforced. No GC. No pauses.   │
│              │ Rust                                    │
├──────────────┼─────────────────────────────────────────┤
│ JAVA LEAK    │ Reachable but unwanted objects          │
│ PATTERNS     │ Static collections, listener lists,     │
│              │ caches without eviction                 │
├──────────────┼─────────────────────────────────────────┤
│ JVM GC FLAGS │ -Xmx (max heap) -Xms (initial)         │
│              │ -XX:+UseG1GC / UseZGC / UseShenandoah  │
│              │ -Xlog:gc* (GC logging)                  │
├──────────────┼─────────────────────────────────────────┤
│ NEXT EXPLORE │ CSF-045 (GC Algorithms), JVM-001 (JVM) │
└────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. GC languages (Java, Go, Python) prevent dangling pointer
   and use-after-free bugs but NOT logical memory leaks:
   objects reachable via static fields, large collections,
   or event listener registries will never be GC'd even
   if the application no longer needs them. GC handles
   reclamation; the programmer handles retention.
2. The four models trade control against safety against latency:
   manual (max control, no safety), GC (no control, high
   safety, pause latency), reference counting (predictable
   latency, cycle problem), ownership/Rust (compile-time
   safety, no GC, no pauses - at the cost of a steep learning curve).
3. JVM memory consists of stack (automatic, method-local)
   and heap (GC-managed objects). Off-heap (`DirectByteBuffer`,
   native memory) is outside the JVM heap and NOT GC-managed
   directly - requires explicit cleanup via the Cleaner API.
   Off-heap leaks manifest as growing RSS (OS memory) with
   stable JVM heap metrics.

**Interview one-liner:**
"Memory management models trade control for safety and latency.
Manual (C): maximum control, no safety. GC (Java, Go):
automatic reclamation, GC pauses, no use-after-free.
Reference counting (Swift): predictable reclamation but cycle
problem. Ownership (Rust): compile-time safety, no GC pauses.
In Java, GC prevents dangling pointers but not logical leaks
from objects reachable but no longer needed."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Memory management model is a consequence of the OWNERSHIP
principle: who is responsible for a resource throughout
its lifetime? This principle applies beyond memory: connection
pool resources (who closes the connection?), transaction
management (who commits/rolls back?), lock management
(who releases the lock?), temporary file cleanup (who
deletes the file?). In Java: try-with-resources is the
"ownership" pattern for non-memory resources. The resource
owner is the try block; it releases on exit. This is the
same principle as Rust's ownership - the SYNTAX and SCOPE
define the lifetime. Extending this: if every resource has
a clear owner, resource leaks become as obvious as memory
leaks in Rust: the compiler can reason about whether a
resource will be released.

**Where else this pattern appears:**

- **Kubernetes pod lifecycle** - Kubernetes pods allocate
  cluster resources (CPU, memory, storage). When a pod is
  deleted (owner = deployment loses the pod), resources
  are returned to the node. Persistent Volumes are retained
  unless the claim is deleted. This is "memory management
  at the cluster level": who owns a resource, when is it
  released, what happens to data on release. The `ownerReference`
  in Kubernetes is literally an ownership system for cluster objects.
- **Database connection management** - A JDBC connection
  is heap memory + OS socket. If a connection is not closed,
  the connection pool eventually exhausts (connection leak),
  causing new requests to wait indefinitely. The fix is
  the same as for memory: use try-with-resources (or Spring's
  `@Transactional` which manages connection lifecycle).
  Connection leaks = memory leaks for network resources.
- **Browser JavaScript WeakMap/WeakRef** - JavaScript's
  `WeakMap` holds keys as weak references: if the key object
  is no longer referenced elsewhere, the GC may collect it,
  and the WeakMap entry disappears. This is the JavaScript
  equivalent of Java's `WeakReference` - preventing memory
  leaks in caches and event listener registries where
  the key object should not be kept alive just because
  the cache references it.

---

### 💡 The Surprising Truth

The JVM's garbage collector is not one thing; it is a
family of algorithms that have evolved over 30 years.
The original "serial GC" (Java 1.0, 1995) was a single-threaded
stop-the-world collector: during GC, the entire application
paused, and one thread reclaimed garbage. For a 256MB heap,
this was acceptable. For a 32GB heap at 10,000 requests/second,
a multi-second stop-the-world pause is catastrophic.
The G1 GC (Java 7+, default in Java 9) split the heap
into regions and reduced pause times to the tens-of-milliseconds.
ZGC (Java 15+ production) achieves sub-millisecond pauses
on heaps of 16TB by doing almost all work concurrently
with the application, using colored pointers and load barriers
to track object states. The pause times went from SECONDS
in 1995 to sub-MILLISECONDS in 2023 for the same language.
This is 30 years of algorithm improvement in one product.
The JVM's GC is arguably the most sophisticated and
thoroughly engineered runtime system in the history of software.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **[IDENTIFY]** List 3 common Java memory leak patterns
   beyond "forgot to close resources." For each, describe
   what holds the object alive, why GC cannot reclaim it,
   and how to fix it.

2. **[CONFIGURE]** Given a Spring Boot application that
   serves 2,000 requests/second with p99 latency requirement
   of 50ms, recommend the appropriate JVM GC algorithm
   and justify the choice. Configure GC logging to verify
   the pause times meet the requirement.

3. **[DIAGNOSE]** A JVM process's RSS is 12GB but heap
   reports only 4GB in use. Identify what might explain the
   difference (off-heap, native memory, code cache, metaspace,
   mapped files). Use `jcmd <pid> VM.native_memory` to investigate.

4. **[COMPARE]** Explain the memory management model of
   Rust's ownership system. Draw a diagram showing what
   happens when a `String` is moved vs cloned in Rust.
   Explain why Rust can guarantee no use-after-free at
   compile time while Java cannot.

5. **[IMPLEMENT]** Fix a Java memory leak in a Spring
   `@Component` that maintains a `static Map<String, Object>
   cache` with no eviction. Implement LRU eviction using
   `LinkedHashMap.removeEldestEntry()` or a `WeakHashMap`.
   Explain which one to use and why.

---

### 🧠 Think About This Before We Continue

**Q1.** A Java application uses `ByteBuffer.allocateDirect(1024 * 1024 * 1024)`
(1GB) in a loop, creating 10 such buffers and discarding them.
The JVM heap shows normal usage (under 512MB) but the
process RSS grows to 11GB before crashing with an OOM
from the OS. Why does increasing `-Xmx` not help?

*Hint: `ByteBuffer.allocateDirect()` allocates OFF-HEAP memory
(native memory outside the JVM heap). Increasing `-Xmx`
makes the JVM heap bigger, but the off-heap allocation
is already working fine (it gets the native memory it requests).
The problem: the `ByteBuffer` objects themselves are tiny
(on the JVM heap). The GC does not know the off-heap memory
is associated with them. GC runs when the JVM heap is under
pressure (which it isn't). The Cleaner (attached to the
ByteBuffer) only runs when the ByteBuffer is GC'd.
Since the heap is not under pressure, GC doesn't run,
the Cleaners don't run, and the off-heap memory accumulates.
Fix: explicitly track off-heap usage and trigger GC when
off-heap approaches limits. Or: pool and reuse
`ByteBuffer.allocateDirect()` rather than allocating new ones.*

**Q2.** In Swift, `strong` references increment ARC (Automatic
Reference Counting), `weak` references do not. A delegate
pattern is typical in iOS code:
```swift
class Timer { var delegate: TimerDelegate? }
class ViewController: TimerDelegate { var timer: Timer? }
viewController.timer = Timer()
timer.delegate = viewController // strong ref
```
What is the memory lifecycle here? Will either object be freed?

*Hint: Cycle: ViewController (strong) -> Timer (strong) -> ViewController.
`timer.delegate = viewController` is a strong reference from
`Timer` to `ViewController`. `viewController.timer` is a
strong reference from `ViewController` to `Timer`.
They reference each other (cycle). When the navigation
system dismisses ViewController (drops its reference),
ViewController's ref count goes from 1 to 0... wait, no.
Timer still holds a strong reference to ViewController.
ViewController ref count = 1 (from Timer). Timer ref count = 1
(from ViewController). Both stay at 1. Neither is freed.
Fix: declare `weak var delegate: TimerDelegate?` in Timer.
Weak references do NOT increment the ref count.
When ViewController is dismissed (external ref count drops to 0),
ViewController is freed. Swift sets `timer.delegate = nil`
automatically (weak ref becomes nil). Timer ref count: still 1
(from viewController). When viewController is freed, its
`timer` property is freed -> Timer ref count drops to 0 -> Timer freed.*

---

### 🎯 Interview Deep-Dive

**Q1: "What is the difference between stack and heap memory?
How does Java's GC relate to heap memory?"**

*Why they ask:* Fundamental computer science. Frequent JVM
tuning question.

*Strong answer includes:*
- Stack: thread-local, LIFO, allocated on method call, freed
  on return. Fixed size. Holds local variables and method frames.
  Automatic - no programmer action needed.
- Heap: shared across threads, dynamically allocated.
  Objects created with `new` go to heap. Size varies (configured
  by `-Xms`/`-Xmx`). Lives until GC or program end.
- JVM GC: periodically identifies unreachable objects on
  the heap (objects with no path from GC roots: thread stacks,
  static fields). Reclaims their memory. Young Generation
  (new objects): frequent minor GC. Old Generation (long-lived):
  infrequent major GC.

**Q2: "What is a memory leak in Java? Give an example."**

*Why they ask:* Common production issue. Tests whether
candidate understands GC's limitations.

*Strong answer includes:*
- Java memory leak: an object that is still REACHABLE
  (has a reference from a root) but no longer NEEDED.
  GC cannot collect it because it appears live.
- Example 1: Static `Map<String, Object> cache` with no eviction.
  Entries accumulate forever. GC cannot reclaim them
  (static field is a GC root).
- Example 2: Event listener not deregistered. Publisher
  holds a strong reference to listener. Even if the listener's
  owner is discarded, the listener object stays alive via
  the publisher's list.
- Detection: heap dump analysis with Eclipse MAT.
  "Leak Suspects" shows what holds most retained heap.

**Q3: "Compare Java's GC with Rust's ownership model.
When would you choose Rust over Java for a new service?"**

*Why they ask:* Architectural decision-making. Tests awareness
of polyglot options.

*Strong answer includes:*
- Java GC: automatic, no programmer burden, but: GC pauses
  (even ZGC has sub-ms pauses), higher memory usage (GC headroom),
  non-deterministic reclamation. Excellent for most enterprise services.
- Rust ownership: compile-time enforced, no GC, no pauses,
  predictable memory usage, deterministic reclamation.
  Cost: steep learning curve, borrow checker requires explicit
  lifetime management.
- Choose Rust when: hard real-time requirements (no GC pauses),
  memory-constrained environments (embedded, IoT), systems
  programming (OS, networking stack), or when the workload
  requires predictable sub-millisecond memory behavior.
- Java with ZGC is sufficient for most financial, web, and
  API workloads. The choice between Java and Rust is not
  "better" but "appropriate to the constraint."
