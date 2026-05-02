---
layout: default
title: "Method Inlining"
parent: "Java & JVM Internals"
nav_order: 300
permalink: /java/method-inlining/
number: "0300"
category: Java & JVM Internals
difficulty: ★★★
depends_on: JIT Compiler, C1 / C2 Compiler, Tiered Compilation
used_by: Deoptimization, OSR (On-Stack Replacement), Escape Analysis
related: Deoptimization, Escape Analysis, Loop Unrolling
tags:
  - java
  - jvm
  - internals
  - performance
  - deep-dive
---

# 300 — Method Inlining

⚡ TL;DR — Method Inlining copies a called method's body directly into the caller, eliminating function call overhead and enabling a cascade of further optimizations.

┌─────────────────────────────────────────────────────────────────────────────────┐
│ #300 │ Category: Java & JVM Internals │ Difficulty: ★★★ │
├──────────────┼──────────────────────────────────────┼──────────────────────────┤
│ Depends on: │ JIT Compiler, C1 / C2 Compiler, │ │
│ │ Tiered Compilation │ │
│ Used by: │ Deoptimization, OSR, │ │
│ │ Escape Analysis │ │
│ Related: │ Deoptimization, Escape Analysis, │ │
│ │ Loop Unrolling │ │
└─────────────────────────────────────────────────────────────────────────────────┘

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Every method call in Java involves significant overhead: saving the current
stack frame, pushing arguments onto the call stack, jumping to the callee's
code, executing, then returning and restoring the caller's state. For small
utility methods like `getLength()`, `isEmpty()`, `add(a, b)`, this overhead can
dwarf the actual work. Worse, virtual dispatch adds a pointer dereference through
the vtable before the call can even begin. A tight loop calling small helpers
thousands of times per second is an overhead machine.

**THE BREAKING POINT:**
A high-frequency trading system calls `order.getPrice()` 50 million times per
second inside a pricing loop. The method contains one line: `return this.price;`.
Without inlining, every call costs: vtable lookup (3ns) + stack frame setup (2ns)

- field access (0.5ns) + stack tear-down (2ns) = 7.5ns. The actual work is 0.5ns.
  The overhead is 15× the work — 93% of CPU time is pure call machinery.

**THE INVENTION MOMENT:**
This is exactly why **Method Inlining** was created: pull the callee's body
into the caller so the call machinery disappears — and expose the combined code
to further optimizations that only make sense when both methods are visible together.

---

### 📘 Textbook Definition

Method Inlining is a JIT compiler optimization that substitutes a method call
with a copy of the called method's body at the call site. The JVM's C2 compiler
selects inlining candidates based on bytecode size, call frequency, call depth,
and type profile data. For virtual (polymorphic) calls, C2 can perform speculative
inlining — inlining the most common receiver type with a guard, enabling devirtualization.
Inlining is the enabling optimization: it expands the JIT's optimization scope,
allowing constant folding, dead code elimination, escape analysis, and field
access elimination to operate across what were previously method boundaries.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Inlining pastes the called method's code directly at the call site, making the call disappear.

**One analogy:**

> Instead of calling a chef to cook your meal (travel time, setup, cleanup),
> you read the recipe yourself and cook it inline. No travel, no setup — and
> now that YOU know what ingredients are needed, you can optimize the whole meal
> for your specific pantry.

**One insight:**
Inlining's true power isn't the call elimination itself — it's that it creates
larger optimization contexts. After inlining `getPrice()` into a loop, the JIT
sees `this.price` accessed directly inside the loop, can hoist it out (it's
loop-invariant), and fold the field access to a single register read. Without
inlining, none of that was visible.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Method call overhead is proportional to call frequency × per-call cost.
2. Optimization scope is limited by what the compiler can "see" — i.e., a single method body.
3. Small methods have high overhead-to-work ratios.
4. Combined code has more optimization opportunities than isolated code.

**DERIVED DESIGN:**
Given invariant 2 and 4, the optimizer must enlarge its view by merging
bodies. The process:

1. Identify a call site: `int result = order.getPrice();`
2. Check inlining eligibility:
   - Callee `getPrice` bytecode size ≤ MaxInlineSize (default: 35 bytes)
   - Call frequency above threshold
   - Inlining depth ≤ MaxInlineLevel (default: 9)
3. Copy callee body into caller IR.
4. Substitute parameters with actual arguments.
5. Apply constant folding, dead code elimination across merged code.
6. The call instruction vanishes — replaced by field access.

**For virtual calls** (most Java calls):
C2 reads the type profile from C1: "97% of calls pass `OrderImpl`, 3% other."
C2 inserts a guard: `if (order.getClass() != OrderImpl.class) { uncommonTrap(); }`
Then inlines `OrderImpl.getPrice()` directly. In 97% of cases, the guard passes
and no virtual dispatch occurs. In 3% — uncommon trap fires, falls back to
regular dispatch.

**THE TRADE-OFFS:**

- Gain: call overhead eliminated; larger optimization context.
- Cost: Code size grows (code bloat); instruction cache pressure increases.
- Gain: enables escape analysis, constant folding, loop-invariant hoisting.
- Cost: speculative inlines create deoptimization risk when type assumptions fail.

---

### 🧪 Thought Experiment

**SETUP:**
A loop processes 10 million items. Each iteration calls `validator.isValid(item)`.
`isValid()` checks one boolean field: `return item.active && item.price > 0`.

**WHAT HAPPENS WITHOUT INLINING:**
Each iteration: push args → vtable lookup → jump to isValid → check conditions
→ return boolean → pop stack. The optimizer sees the loop body as `callsite`,
opaque. It cannot hoist `item.active` check out of the loop. Cannot eliminate the
boolean return value boxing. Cannot see that the method is pure (no side effects).
10 million calls × 8ns overhead = 80ms of pure call machinery.

**WHAT HAPPENS WITH INLINING:**
C2 inlines `isValid()`. The loop body is now:
`if (item.active && item.price > 0) { process(item); }`.
C2 sees that `item.active` is loop-invariant (assuming no writes inside the loop),
hoists the check outside: `if (!item.active) continue outerLoop;`. Inside the loop,
only `item.price > 0` is checked per iteration. The 80ms collapses to ~5ms.

**THE INSIGHT:**
Inlining is not just call elimination — it's the key that unlocks every other
optimization. The compiler must see combined code to reason about what can be
simplified across boundaries.

---

### 🧠 Mental Model / Analogy

> Think of inlining as macro expansion in a recipe book. Instead of "see recipe
> on page 47," the recipe is printed right here. Now the author can see that
> the step requiring "30 grams of already-chopped onion" overlaps with the
> previous step's "30 grams of chopped onion" — and eliminate the duplication.
> The efficiency gain isn't in flipping fewer pages; it's in seeing the full
> picture.

- "See page 47" → method call (indirect)
- "Recipe printed here" → inlined method body
- "Overlapping ingredients spotted" → constant folding, dead code elimination
  across the combined body
- "Pages saved" → call overhead eliminated

**Where this analogy breaks down:** Unlike a recipe, inlining can also be
speculative — the JVM may inline a version it thinks is often used (with a
guard), but must handle the case where the assumption is wrong at runtime.
Recipes don't deoptimize.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Method inlining means the JVM puts the code of a small method directly inside
the code that calls it, instead of jumping back and forth. Fewer jumps = faster code.

**Level 2 — How to use it (junior developer):**
Inlining is automatic. You can influence it by keeping hot methods small (under
35 bytecodes — roughly 20–30 lines of simple code). Avoid deep call chains in
performance-critical paths — the JVM's inlining depth is limited to 9 levels by default.
Prefer concrete types over interfaces at hot call sites to enable devirtualization.

**Level 3 — How it works (mid-level engineer):**
C2 uses several heuristics: `MaxInlineSize` (default 35 bytecodes) for normal inlining,
`FreqInlineSize` (default 325 bytecodes) for very hot methods. The JVM tracks call
depth and won't inline deeper than `MaxInlineLevel` (9). For virtual calls, C2
checks the type profile from C1: if one type accounts for > 90% of calls, it
inlines that type's implementation with a guard (speculative devirtualization).
If two types share calls (bimorphic), C2 sometimes inlines both with two guards.
Three or more types (megamorphic) — no inlining.

**Level 4 — Why it was designed this way (senior/staff):**
The size threshold limits were determined empirically to balance code growth vs
optimization benefit. Too aggressive: instruction cache thrashing hurts performance
(L1i misses become the bottleneck). Too conservative: hot utility methods aren't
inlined, leaving performance on the table. The 35-byte threshold roughly corresponds
to methods that fit inside one CPU cache line worth of native code. The
`MaxInlineLevel` of 9 prevents unbounded code growth from recursive-like call
chains in deeply layered frameworks (Spring, Hibernate). Open JDK engineers have
found that increasing beyond 9 provides minimal gains while causing code bloat.

---

### ⚙️ How It Works (Mechanism)

```
┌───────────────────────────────────────────────────────┐
│          METHOD INLINING — STEP BY STEP               │
├───────────────────────────────────────────────────────┤
│  BEFORE INLINING:                                     │
│                                                       │
│  void process(Order order) {                          │
│    int price = order.getPrice();  // call site        │
│    ...                                                │
│  }                                                    │
│                                                       │
│  int getPrice() { return this.price; }                │
│                     ↓ C2 inlining                     │
│  AFTER INLINING:                                      │
│                                                       │
│  void process(Order order) {                          │
│    int price = order.price;  // field access, no call │
│    ...                                                │
│  }                                                    │
│                                                       │
│  INLINING DECISION TREE:                             │
│                                                       │
│  Is caller hot? (invokes > threshold)                │
│       ↓ YES                                           │
│  Is callee bytecode ≤ MaxInlineSize (35)?            │
│       ↓ YES                                           │
│  Is call depth < MaxInlineLevel (9)?                 │
│       ↓ YES                                           │
│  Is call monomorphic? (profile check)                │
│       ↓ YES / BIMORPHIC                               │
│    ═══ INLINE ═══                                    │
│       ↓ MEGAMORPHIC                                  │
│    ═══ SKIP — virtual dispatch remains ═══           │
└───────────────────────────────────────────────────────┘
```

**Speculative devirtualization flow:**

```java
// Original bytecode: virtual call
result = validator.validate(item);

// After C2 speculative inlining (pseudo-representation):
if (validator.getClass() == ConcreteValidator.class) {
    // Inlined ConcreteValidator.validate body here
    result = item.value > 0 && item.active; // direct code
} else {
    // Uncommon trap: deoptimize and re-dispatch
    result = uncommonTrap_virtualDispatch(validator, item);
}
```

Guards are extremely cheap (1 comparison + unpredicted branch taken ~0% of time).
The cost is nearly zero on the happy path.

---

### 🔄 The Complete Picture — End-to-End Flow

```
┌───────────────────────────────────────────────────────┐
│     METHOD INLINING IN JIT PIPELINE                   │
├───────────────────────────────────────────────────────┤
│  Bytecode arrives at C2                               │
│       ↓                                               │
│  Build IR (sea of nodes)                              │
│       ↓                                               │
│  Inline Phase: examine each call site                 │
│    ├── Static call? → always inline if size ok        │
│    ├── Virtual + mono? → speculative inline           │
│    ├── Virtual + bi? → maybe inline both             │
│    └── Virtual + mega? → skip                        │
│  ← YOU ARE HERE                                       │
│       ↓                                               │
│  Optimization Phase (sees merged IR):                 │
│    - Constant folding across inlined bodies          │
│    - Dead code elimination                           │
│    - Escape analysis                                  │
│    - Loop-invariant code motion                      │
│       ↓                                               │
│  Code generation → native instructions               │
└───────────────────────────────────────────────────────┘
```

**FAILURE PATH:**
Type assumption fails → uncommon trap fires → deoptimization at the guard →
method falls back to interpreter → re-profiled → eventually re-inlined with
updated type assumptions.

**WHAT CHANGES AT SCALE:**
At 1000× call frequency, inlining becomes critical — every method on the
hot path must be inlinable. Frameworks using proxies (Spring AOP, Hibernate)
break inlining chains by injecting megamorphic call sites. This is a significant
source of production performance gaps between benchmarks and real applications.

---

### 💻 Code Example

```java
// Example 1 — Method inlining eligibility
// GOOD: small method, easily inlined by C2
public int getSize() {
    return this.size; // 1-2 bytecodes — always inlined
}

// BAD: large method, won't be inlined
public void processAll() {
    // 50+ lines of logic — exceeds MaxInlineSize
    // C2 will not inline this even if called frequently
}

// FIX: extract hot inner path to small inlinable method
public void processAll() {
    for (Item item : items) {
        processItem(item); // small — C2 inlines this
    }
}
private void processItem(Item item) {
    // ≤ 20 lines of actual logic
}
```

```java
// Example 2 — Megamorphic call site (prevents inlining)
interface Processor { int process(int x); }

// BAD: 5 different implementations → megamorphic
List<Processor> processors = List.of(
    new A(), new B(), new C(), new D(), new E()
);
for (Processor p : processors) {
    total += p.process(value); // NEVER inlined
}

// GOOD: single concrete type → monomorphic → C2 inlines
ProcessorImpl impl = new ProcessorImpl();
for (int i = 0; i < N; i++) {
    total += impl.process(value); // inlined
}
```

```java
// Example 3 — Check what JIT is inlining
// Run with: java -XX:+PrintInlining MyApp
// Output:
//   @ 4   com.example.Order::getPrice (2 bytes)   inline (hot)
//   @ 12  com.example.Validator::validate (89 bytes)   too big
// "inline (hot)" — successfully inlined
// "too big" — exceeded MaxInlineSize

// Force-increase for specific hot large methods:
// -XX:FreqInlineSize=500  (for very hot methods only)
// Use carefully — code bloat hurts i-cache
```

---

### ⚖️ Comparison Table

| Call Type                 | Inlining           | Guard Required | Megamorphic Risk | Best For                         |
| ------------------------- | ------------------ | -------------- | ---------------- | -------------------------------- |
| **Static/final**          | Always             | No             | None             | Utility methods, private methods |
| Virtual (monomorphic)     | Yes (speculative)  | Yes (1 check)  | None             | Common case: 1 impl              |
| Virtual (bimorphic)       | Sometimes          | Yes (2 checks) | Low              | 2-impl polymorphism              |
| Virtual (megamorphic, 3+) | No                 | N/A            | High             | Frameworks, plugin systems       |
| Interface default         | Depends on profile | Yes            | High             | Spring beans, DI proxies         |

**How to choose:** Make hot path code use concrete types, not interfaces.
Reserve interface polymorphism for non-hot code paths. Hotspot will handle
the rest automatically.

---

### ⚠️ Common Misconceptions

| Misconception                                              | Reality                                                                                                              |
| ---------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| Inlining always improves performance                       | Excessive inlining causes code bloat and L1 instruction cache thrashing — it can hurt performance                    |
| Private methods are always inlined                         | Private methods avoid vtable dispatch but C2 still checks bytecode size — large private methods are not inlined      |
| `final` keyword forces inlining                            | `final` enables monomorphic dispatch but C2 inlines based on size and hotness, not just finality                     |
| Inlining depth can be increased safely                     | Increasing `MaxInlineLevel` beyond 9 risks severe code bloat; the default balances optimization vs cache pressure    |
| Framework code (Spring proxies) is as fast as direct calls | Proxy-based AOP creates megamorphic call sites at every `@Transactional`/`@Cacheable` boundary — inlining is blocked |

---

### 🚨 Failure Modes & Diagnosis

**Framework Proxy Megamorphism**

Symptom:
Production throughput is 40% below JMH benchmark results. Both appear to
use the same code. The difference isn't GC, network, or DB.

Root Cause:
JMH benchmarks use direct concrete classes. Production uses Spring-managed beans
wrapped in CGLIB proxies. Every call site at a proxy boundary becomes megamorphic
— C2 cannot inline. The 40% gap is pure call overhead that JMH never sees.

Diagnostic Command / Tool:

```bash
java -XX:+PrintInlining -XX:+PrintCompilation MyApp 2>&1 \
  | grep -E "(megamorphic|virtual)" | head -30
# Shows all call sites C2 decided not to inline due to megamorphism
```

Fix:
For performance-critical inner loops, inject the concrete implementation
rather than the Spring proxy. Or use Spring's `@Component` classes with
`@Scope("singleton")` to ensure at most one proxy level.

Prevention:
Profile with `PrintInlining` in pre-production. Identify megamorphic hot
spots early and break them with concrete types or `final` classes.

---

**Inlining Depth Exceeded**

Symptom:
A deep call chain (A→B→C→D→E→F→G→H→I→J) results in poor performance.
`-XX:+PrintInlining` shows `inlining too deep` for the deepest methods.

Root Cause:
Call chain exceeds `MaxInlineLevel` (default 9). Methods beyond depth 9
revert to virtual dispatch — losing all inlining benefits.

Diagnostic Command / Tool:

```bash
java -XX:+PrintInlining 2>&1 | grep "too deep"
# Identifies which methods exceed inlining depth
```

Fix:
Flatten the call hierarchy by merging small delegation methods. Avoid
builder chains and decorator patterns on the hot path.

Prevention:
Keep hot-path method depth ≤ 5 levels. Use `MaxInlineLevel` increase
as last resort only after measuring code cache impact.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `JIT Compiler` — inlining is a JIT optimization; requires JIT to be active
- `C1 / C2 Compiler` — specifically C2 performs aggressive inlining; C1 inlines minimally
- `Tiered Compilation` — C1 gathers type profiles that enable C2's speculative inlining

**Builds On This (learn these next):**

- `Deoptimization` — speculative inlining can be undone when type guards fail
- `Escape Analysis` — unlocked by inlining; can allocate objects on stack instead of heap
- `OSR (On-Stack Replacement)` — method hot-swap that may trigger re-inlining

**Alternatives / Comparisons:**

- `Escape Analysis` — another C2 optimization that inlining enables
- `Loop Unrolling` — a peer optimization that reduces loop-control overhead

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Copy callee body into caller at call site  │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Call overhead dominates small-method work  │
│ SOLVES       │ and limits optimizer's view               │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Inlining enables other optimizations —    │
│              │ it's the prerequisite, not the destination│
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Automatic — keep hot methods small (≤35b) │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Forcing inline of large methods causes     │
│              │ I-cache pressure exceeding the benefit    │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Code size grows vs call overhead shrinks  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Call what you can see; see what you inline"│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Escape Analysis → Deoptimization           │
│              │ → OSR (On-Stack Replacement)               │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You have a hot loop that calls a method through a Spring `@Transactional`
proxy. The proxy adds around 200 bytecodes of boilerplate per execution. C2 cannot
inline through the proxy boundary. The business logic inside the transaction is a
5-line method. What are the exact performance implications, and list three
architectural changes — at different levels of invasiveness — that would restore
C2 inlining without removing transactional semantics.

**Q2.** If inlining always enlarges the optimization scope, why doesn't the JVM
have an unlimited inlining budget? Derive from first principles the exact point
at which more inlining becomes harmful, and explain what physical hardware
characteristic makes this an inherently bounded problem.
