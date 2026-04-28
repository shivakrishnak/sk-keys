---
layout: default
title: "Escape Analysis"
parent: "Java Fundamentals"
nav_order: 13
permalink: /java/escape-analysis/
---
âš¡ TL;DR â€” A JIT compiler optimisation that determines if an object's lifetime is confined to a method, allowing stack allocation or scalar replacement â€” eliminating heap allocation and GC pressure entirely.

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ #013         â”‚ Category: JVM Internals              â”‚ Difficulty: â˜…â˜…â˜…          â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ Depends on:  â”‚ [[JVM]] [[Heap Memory]]              â”‚                          â”‚
â”‚              â”‚ [[Stack Memory]] [[JIT Compiler]]    â”‚                          â”‚
â”‚ Used by:     â”‚ [[GC]] [[JIT Compiler]] [[Stack Frame]]                         â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---
### ðŸ“˜ Textbook Definition

Escape Analysis is a **compile-time optimisation performed by the JIT compiler** that determines whether an object's reference can "escape" the scope in which it was created â€” either by being returned, stored in a field, or passed to another thread. If the JIT proves an object does NOT escape, it can apply three optimisations: **stack allocation** (put object on stack instead of heap), **scalar replacement** (decompose object into primitive variables), and **lock elision** (remove synchronization on unescaped objects).

---
### ðŸŸ¢ Simple Definition (Easy)

Escape Analysis is the JVM asking: **"Does this object ever leave the method that created it?"** If the answer is no â€” it never leaves â€” the JVM can avoid putting it on the heap entirely, making allocation and cleanup essentially free.

---
### ðŸ”µ Simple Definition (Elaborated)

Every `new` object normally goes to the heap and eventually needs GC. But if the JIT can prove that an object is only used within one method and never handed to anything outside â€” no return, no field store, no other thread â€” it can allocate that object on the stack instead, where cleanup is instant and free. Even better, it can decompose the object into plain variables, eliminating the object entirely. This happens silently, automatically, with no code changes from you.

---
### ðŸ”© First Principles Explanation

**The problem:**

Every heap allocation has costs:

```
1. Allocation cost   â†’ bump TLAB pointer (fast, but adds up)
2. GC cost           â†’ object must be traced, aged, collected
3. Cache cost        â†’ heap objects scattered â†’ cache misses
4. Header overhead   â†’ 12-16 bytes per object regardless of size
```

For short-lived objects (the majority), this is pure waste â€” they die before the next GC anyway.

**The key observation:**

```java
public int computeDistance(int x1, int y1, int x2, int y2) {
    Point delta = new Point(x2 - x1, y2 - y1); // created here
    return Math.abs(delta.x) + Math.abs(delta.y); // used here
    // delta never leaves this method
}
// delta could have been two local ints â€” Point was unnecessary
```

The `Point` object is semantically useful (readable code) but physically wasteful (heap allocation for something that dies immediately).

**The insight:**

> "If the JIT can prove an object never escapes its creation scope, the object's fields are logically equivalent to local variables â€” treat them as such."

```
Before escape analysis:
  new Point(dx, dy) â†’ heap allocation â†’ GC pressure

After escape analysis (scalar replacement):
  int point_x = dx;  // just two local variables
  int point_y = dy;  // no object, no heap, no GC
```

The abstraction (object) is preserved in source code. The cost (heap allocation) is eliminated at runtime.

---

### â“ Why Does This Exist â€” Why Before What

**Without Escape Analysis:**

```
Every 'new' = heap allocation = GC candidate

Reality of typical Java code:
  â€¢ Builder objects           â†’ die immediately after .build()
  â€¢ Iterator objects          â†’ die after loop
  â€¢ Entry objects in forEach  â†’ die after each iteration
  â€¢ Point/Range/Pair wrappers â†’ die after computation
  â€¢ StringBuilder in concat   â†’ dies after toString()

Without escape analysis:
  â†’ ALL of these hit the heap
  â†’ ALL trigger TLAB fills
  â†’ ALL increase GC frequency
  â†’ ALL add GC pause time
  â†’ Writing clean OOP code = performance penalty
```

**The philosophical problem it solves:**

> Without escape analysis, developers face a cruel choice:
> 
> - Write clean, object-oriented code â†’ pay heap/GC cost
> - Write fast code â†’ use primitives, avoid objects, ugly code

**With Escape Analysis:**

```
â†’ Write clean OOP code freely
â†’ JIT proves objects don't escape
â†’ Objects eliminated or stack-allocated automatically
â†’ Clean code AND fast code â€” not a tradeoff
â†’ GC pressure reduced without developer effort
```

**What breaks without it:**

```
1. Short-lived object GC pressure   â†’ explodes
2. Minor GC frequency               â†’ increases dramatically
3. Clean OOP patterns               â†’ become performance liabilities
4. Lock overhead on thread-local objects â†’ unnecessary OS calls
5. Throughput of allocation-heavy code   â†’ significantly lower
```

---
### ðŸ§  Mental Model / Analogy

> Imagine you're cooking a meal (executing a method).
> 
> You grab a mixing bowl (create an object), mix ingredients in it, pour the result onto a plate, and wash the bowl immediately â€” it never leaves the kitchen.
> 
> **Without escape analysis:** Every bowl must be stored in a warehouse (heap), tracked in an inventory system (GC), and a cleanup crew comes periodically to collect unused bowls (GC pause).
> 
> **With escape analysis:** The JVM sees the bowl never leaves the kitchen. It hands you a disposable surface (stack allocation) instead â€” use it, discard it instantly, no warehouse, no inventory, no cleanup crew.
> 
> **With scalar replacement:** The JVM goes further â€” "you don't even need a bowl, just put the ingredients directly on the counter (local variables) and slide them onto the plate."

---
### âš™ï¸ How It Works â€” Three Optimisations

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚              ESCAPE ANALYSIS OUTCOMES                           â”‚
â”‚                                                                 â”‚
â”‚  JIT analyses object reference flow:                           â”‚
â”‚                                                                 â”‚
â”‚  Does the reference:                                            â”‚
â”‚    â€¢ Get returned from the method?          â†’ ESCAPES           â”‚
â”‚    â€¢ Get stored in a field/static?          â†’ ESCAPES           â”‚
â”‚    â€¢ Get passed to an unknown method?       â†’ ESCAPES           â”‚
â”‚    â€¢ Get stored where another thread reads? â†’ ESCAPES           â”‚
â”‚                                                                 â”‚
â”‚  If NONE of the above â†’ object DOES NOT ESCAPE                 â”‚
â”‚                                                                 â”‚
â”‚  Three possible optimisations:                                  â”‚
â”‚                                                                 â”‚
â”‚  1. STACK ALLOCATION                                            â”‚
â”‚     Object allocated on stack frame instead of heap            â”‚
â”‚     Freed instantly when method returns                         â”‚
â”‚     No GC involvement                                           â”‚
â”‚                                                                 â”‚
â”‚  2. SCALAR REPLACEMENT (most powerful)                          â”‚
â”‚     Object decomposed into primitive local variables            â”‚
â”‚     Object ceases to exist entirely                             â”‚
â”‚     Fields become slots in Local Variable Table                 â”‚
â”‚     No allocation whatsoever                                    â”‚
â”‚                                                                 â”‚
â”‚  3. LOCK ELISION                                                â”‚
â”‚     If object doesn't escape â†’ no other thread can access it   â”‚
â”‚     â†’ synchronized block on it is useless                      â”‚
â”‚     â†’ JIT removes the lock entirely                             â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---
### ðŸ”„ How It Connects

```
Java source: new Point(x, y)
      â†“
javac â†’ bytecode: NEW Point, invokespecial <init>
      â†“
JIT detects method is HOT
      â†“
JIT runs Escape Analysis on all allocations
      â†“
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ Does Point reference escape?        â”‚
â”‚                                     â”‚
â”‚ NO  â†’ Scalar Replacement            â”‚
â”‚       Point.x â†’ local var           â”‚
â”‚       Point.y â†’ local var           â”‚
â”‚       No allocation at all          â”‚
â”‚                                     â”‚
â”‚ YES â†’ Normal heap allocation        â”‚
â”‚       TLAB bump pointer             â”‚
â”‚       GC tracks it                  â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
      â†“
Native code generated
(with or without allocation)
```

---
### ðŸ’» Code Example

**Example 1 â€” Scalar Replacement in action:**

```java
public class EscapeDemo {

    static class Point {
        final int x, y;
        Point(int x, int y) { this.x = x; this.y = y; }
    }

    // DOES NOT ESCAPE â€” Point never leaves this method
    public static int manhattanDistance(int x1, int y1,
                                         int x2, int y2) {
        Point delta = new Point(x2 - x1, y2 - y1);
        // delta is used only here â€” never returned, stored, or passed
        return Math.abs(delta.x) + Math.abs(delta.y);
    }

    // ESCAPES â€” Point returned to caller
    public static Point createPoint(int x, int y) {
        return new Point(x, y); // â† escapes: returned
    }

    // ESCAPES â€” Point stored in field
    private Point cached;
    public void cachePoint(int x, int y) {
        cached = new Point(x, y); // â† escapes: field store
    }
}
```

```
JIT analysis of manhattanDistance():
  new Point(dx, dy) â†’ does reference escape?
    - returned?  NO
    - stored?    NO
    - passed to unknown method? Math.abs takes int, not Point â†’ NO
  â†’ SCALAR REPLACEMENT applied:
    delta.x â†’ local int variable
    delta.y â†’ local int variable
    new Point() â†’ eliminated entirely
    
Effective native code equivalent:
  int delta_x = x2 - x1;
  int delta_y = y2 - y1;
  return Math.abs(delta_x) + Math.abs(delta_y);
```

**Example 2 â€” Lock Elision:**

```java
public class LockElision {

    public static String buildMessage(String name) {
        // StringBuffer is synchronized on every operation
        // But 'sb' never escapes this method
        // JIT elides ALL locks on sb
        StringBuffer sb = new StringBuffer();
        sb.append("Hello, ");  // lock elided
        sb.append(name);       // lock elided
        sb.append("!");        // lock elided
        return sb.toString();  // lock elided
        // sb itself escapes (returned string), but
        // the StringBuffer object does NOT escape
    }
}
```

```
Without lock elision:
  append() â†’ acquire lock â†’ write â†’ release lock (Ã—3)
  â†’ 3 CAS operations minimum

With lock elision:
  append() â†’ write directly (Ã—3)
  â†’ 0 CAS operations
  â†’ Effectively as fast as StringBuilder
```

**Example 3 â€” Verifying with JVM flags:**

```bash
# Enable escape analysis (default since Java 8):
java -XX:+DoEscapeAnalysis MyApp

# Disable to measure the difference:
java -XX:-DoEscapeAnalysis MyApp

# See escape analysis decisions:
java -XX:+PrintEscapeAnalysis MyApp

# See eliminated allocations:
java -XX:+PrintEliminateAllocations MyApp
```

**Example 4 â€” Benchmarking the difference (JMH):**

```java
import org.openjdk.jmh.annotations.*;

@BenchmarkMode(Mode.Throughput)
@Warmup(iterations = 5)
@Measurement(iterations = 10)
public class EscapeBenchmark {

    // JIT will scalar-replace Point â€” no heap allocation
    @Benchmark
    public int withEscapeAnalysis() {
        Point p = new Point(3, 4);   // eliminated by EA
        return p.x + p.y;
    }

    // Force heap allocation by making object escape
    @Benchmark
    public Point withoutEscapeAnalysis() {
        return new Point(3, 4);      // escapes â†’ heap allocated
    }
}
```

```
Typical results:
  withEscapeAnalysis:    ~2,000,000 ops/ms  â† near-zero allocation
  withoutEscapeAnalysis: ~  800,000 ops/ms  â† heap + GC pressure
  
Speedup: ~2.5Ã— just from eliminating one small object allocation
```

**Example 5 â€” When EA breaks â€” subtle escape:**

```java
public int process(List<Point> results) {
    Point p = new Point(3, 4);

    // This LOOKS like p stays local...
    int val = p.x + p.y;

    // BUT: passing p to an external method = potential escape
    // JIT cannot prove what externalMethod() does with p
    externalMethod(p);      // â† p ESCAPES here

    return val;
}

// Fix: if you don't want escape, don't pass the object out
public int processFast(List<Point> results) {
    Point p = new Point(3, 4);
    int val = p.x + p.y;
    // p never passed anywhere â†’ EA applies
    return val;
}
```

---
### ðŸ” EA Interaction with Inlining

```
CRITICAL: Escape Analysis depends on inlining

If method is NOT inlined:
  JIT can't see inside it
  â†’ Assumes any object passed to it ESCAPES
  â†’ EA cannot apply

If method IS inlined:
  JIT sees the full picture
  â†’ Can prove object doesn't escape
  â†’ EA applies

Example:
  computeDistance(new Point(x,y))
  â†’ if computeDistance() is inlined into caller:
     JIT sees Point never escapes the combined code
     â†’ scalar replacement applies âœ…
  â†’ if computeDistance() is NOT inlined:
     JIT sees Point passed to unknown code
     â†’ assumes escape â†’ heap allocation âŒ

This is why:
  Small methods + EA = multiplicative benefit
  Large methods that prevent inlining = EA lost
```

---

### âš ï¸ Common Misconceptions

|Misconception|Reality|
|---|---|
|"EA always eliminates heap allocations"|Only when JIT **proves** no escape â€” any doubt = heap|
|"EA works on all objects"|Only on objects the JIT has **fully analysed** â€” not all code is JIT compiled|
|"Scalar replacement = stack allocation"|Different optimisations â€” SR eliminates the object entirely; SA puts it on stack|
|"EA is always on"|On by default Java 8+ but JIT must first decide to compile the method|
|"EA works immediately on startup"|Only after JIT **warmup** â€” interpreter phase has no EA|
|"Passing to inlined method = escape"|If callee is **inlined**, JIT sees through the call â€” may not escape|

---

### ðŸ”¥ Pitfalls in Production

**1. EA silently disabled by large methods**

```java
// BAD: massive method â€” JIT may not inline callees
// EA analysis becomes conservative â†’ more heap allocations
public void massiveMethod() {
    // 500 lines of code
    // JIT struggles to analyse escape paths
    // Many small objects that COULD be eliminated â†’ aren't
}

// GOOD: small focused methods
// JIT inlines aggressively â†’ EA sees full picture
public void smallMethod() {
    // 20 lines
    // JIT inlines dependencies
    // EA eliminates short-lived objects
}
// Rule of thumb: methods > 325 bytecodes won't be inlined
// Check with: -XX:+PrintInlining
```

**2. Reflection breaks EA**

```java
// Reflection = JIT can't see what happens to your object
Point p = new Point(3, 4);
method.invoke(target, p);   // â† p escapes â€” JIT has no idea
                             //   what reflective call does with it

// Fix: avoid reflection in hot paths
// Use direct calls, interfaces, or method handles instead
MethodHandle mh = lookup.findVirtual(...);
mh.invoke(target, p);  // JIT can sometimes analyse MH calls
```

**3. Assuming EA without verification**

```bash
# Never assume EA is working â€” always verify in perf-critical code

# Step 1: Check if allocation is eliminated
java -XX:+PrintEliminateAllocations -XX:+UnlockDiagnosticVMOptions \
     MyApp 2>&1 | grep "Scalar"

# Step 2: Measure allocation rate
# Use JFR (Java Flight Recorder):
java -XX:StartFlightRecording=filename=recording.jfr MyApp
# Check allocation profiling in JDK Mission Control

# Step 3: Micro-benchmark with JMH
# Measure ops/sec with and without EA
# -XX:+/-DoEscapeAnalysis
```

**4. EA and virtual threads**

```java
// Virtual threads (Java 21) store stack frames on heap
// when thread is unmounted (parked/waiting)
// Objects in those frames that "escaped to heap stack"
// are not eligible for EA in the same way

// For CPU-bound code on virtual threads:
// EA still applies normally during active execution
// The difference appears only during suspension points
// (blocking I/O, sleep, etc.)
```

---

### ðŸ”— Related Keywords

- `JIT Compiler` â€” performs escape analysis during compilation
- `Stack Memory` â€” where stack-allocated objects land
- `Heap Memory` â€” what EA helps avoid
- `Scalar Replacement` â€” strongest EA optimisation â€” eliminates object entirely
- `Lock Elision` â€” EA-enabled removal of unnecessary synchronization
- `Method Inlining` â€” prerequisite for effective EA across method boundaries
- `GC` â€” directly benefited by EA reducing heap allocation pressure
- `TLAB` â€” the fast heap allocation path EA bypasses
- `Object Header` â€” eliminated entirely under scalar replacement
- `JMH` â€” tool to benchmark and verify EA effectiveness
- `Project Valhalla` â€” value types that guarantee no-escape semantics at language level

---

### ðŸ“Œ Quick Reference Card

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ KEY IDEA     â”‚ JIT proves object doesn't leave its       â”‚
â”‚              â”‚ method â†’ eliminates heap allocation and   â”‚
â”‚              â”‚ GC entirely via scalar replacement        â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ USE WHEN     â”‚ Write clean OOP freely â€” EA works best    â”‚
â”‚              â”‚ with small methods, no reflection,        â”‚
â”‚              â”‚ no unnecessary object sharing             â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ AVOID WHEN   â”‚ Don't rely on EA for correctness â€”        â”‚
â”‚              â”‚ it's an optimisation hint, not a          â”‚
â”‚              â”‚ guarantee; always verify with JMH + JFR  â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ ONE-LINER    â”‚ "EA = the JVM's promise: write clean      â”‚
â”‚              â”‚  objects freely, I'll make them free      â”‚
â”‚              â”‚  if they never leave home"                â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ NEXT EXPLORE â”‚ JIT Compiler â†’ Method Inlining â†’          â”‚
â”‚              â”‚ Scalar Replacement â†’ Lock Elision â†’       â”‚
â”‚              â”‚ Project Valhalla â†’ JMH Benchmarking       â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

### ðŸ§  Think About This Before We Continue

**Q1.** Escape Analysis depends heavily on method inlining â€” if the JIT can't inline a method, it assumes objects passed to it escape. The JIT stops inlining methods larger than ~325 bytecodes. What does this mean for your code design strategy â€” specifically around large service methods, utility helpers, and inner loops in performance-critical paths?

**Q2.** Consider this pattern common in Spring applications:

```java
@Transactional
public OrderDTO processOrder(OrderRequest request) {
    Order order = new Order(request);      // line A
    orderRepository.save(order);           // line B
    return new OrderDTO(order);            // line C
}
```

Apply escape analysis mentally to each object created. Which escape, which don't, and why? What optimisations can the JIT apply â€” and which are blocked by Spring's proxy mechanism?

---

Next up: **014 â€” Memory Barrier** â€” the invisible synchronisation primitive that prevents CPU and compiler reordering, why it exists at the hardware level, and how Java's `volatile`, `synchronized`, and `happens-before` are built on top of it.

Shall I continue?
