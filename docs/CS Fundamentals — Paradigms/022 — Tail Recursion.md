---
layout: default
title: "Tail Recursion"
parent: "CS Fundamentals — Paradigms"
nav_order: 22
permalink: /cs-fundamentals/tail-recursion/
number: "22"
category: CS Fundamentals — Paradigms
difficulty: ★★★
depends_on: Recursion, Stack Memory, Stack Frame, Functional Programming
used_by: Functional Programming, Scala, Kotlin, Compiler Optimisation
tags: #advanced, #optimization, #functional, #deep-dive
---

# 22 — Tail Recursion

`#advanced` `#optimization` `#functional` `#deep-dive`

⚡ TL;DR — A recursive call is in _tail position_ when it is the **last operation** in a function; a compiler can then replace the current stack frame instead of pushing a new one, making recursion as memory-efficient as a loop.

| #22             | Category: CS Fundamentals — Paradigms                        | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------------------- | :-------------- |
| **Depends on:** | Recursion, Stack Memory, Stack Frame, Functional Programming |                 |
| **Used by:**    | Functional Programming, Scala, Kotlin, Compiler Optimisation |                 |

---

### 📘 Textbook Definition

**Tail Recursion** is a special form of recursion in which the recursive call is the _tail call_ — the final action performed by a function before returning. When a call is in tail position, the current stack frame is not needed after the call executes, because there is no pending computation waiting on its return value. A compiler or runtime that implements _Tail Call Optimisation_ (TCO) can therefore overwrite the current frame rather than pushing a new one, reducing stack space usage from O(n) to O(1). This allows deep or infinite recursion without stack overflow. Not all languages or runtimes implement TCO: Scala (`@tailrec`) and Kotlin (`tailrec` modifier) guarantee it; the JVM specification does not require it for Java; most functional languages (Haskell, Erlang, Clojure with `recur`) implement it natively.

---

### 🟢 Simple Definition (Easy)

Tail recursion is when a function calls itself as the very last thing it does — no work is pending after the call — so the computer can reuse the same memory slot instead of adding a new one to the stack.

---

### 🔵 Simple Definition (Elaborated)

Normal recursion leaves pending work in each stack frame. Computing `factorial(5)` the standard way leaves "multiply by 5" pending while waiting for `factorial(4)`, which leaves "multiply by 4" pending, and so on. All five frames must stay alive simultaneously. Tail recursion moves the pending work _into the arguments_: instead of "return n × factorial(n-1)", you write "return factHelper(n-1, accumulator × n)" — the multiplication happens before the call, not after. Now the current frame has no pending work; it can be discarded and the recursive call runs in its place. A tail-call optimising compiler converts this into a loop: no extra stack frames are pushed. Ten million recursive calls use no more stack space than one.

---

### 🔩 First Principles Explanation

**Why non-tail recursion accumulates frames:**

```
factorial(5)  calls factorial(4)
                  — frame for factorial(5) must stay alive
                  — because it needs to compute: result × 5

factorial(4)  calls factorial(3)
                  — frame for factorial(4) must stay alive
                  — because it needs to compute: result × 4
                  ...
```

Each frame _waits_ because there is a pending operation (`n ×`). The call is not the last operation — the multiplication is.

**Converting to tail-recursive form using an accumulator:**

```java
// Non-tail-recursive (pending multiplication after each call)
int factorial(int n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);  // multiplication AFTER the call ← not tail
}

// Tail-recursive (accumulator carries the work forward)
int factorial(int n) {
    return factHelper(n, 1); // kick off with accumulator = 1
}

int factHelper(int n, int acc) {
    if (n <= 1) return acc;             // base case: return accumulated result
    return factHelper(n - 1, acc * n); // multiply BEFORE the call ← tail call
    //    ^^^ this is the LAST thing done — no pending work
}
```

**What TCO does with the tail call:**

```
Without TCO:
  factHelper(5, 1)
    factHelper(4, 5)      ← new frame pushed
      factHelper(3, 20)   ← new frame pushed
        factHelper(2, 60) ← new frame pushed
          factHelper(1, 120) ← returns 120

With TCO (compiler converts to loop):
  acc = 1, n = 5
  acc = 5, n = 4   ← same frame reused
  acc = 20, n = 3  ← same frame reused
  acc = 60, n = 2  ← same frame reused
  acc = 120, n = 1 ← returns 120
// Identical result, O(1) stack space
```

**Why the JVM does not guarantee TCO for Java:**

The JVM security model uses the call stack to determine code permissions (stack inspection). Eliminating stack frames could remove security context from the stack. Additionally, the JVM bytecode specification does not include a tail-call instruction. Scala compiles `@tailrec` functions into JVM loops (via `goto`) to work around this limitation; the recursion is eliminated at the Scala compiler level before the JVM ever sees it.

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Tail Recursion (naive recursion at scale):

```java
// BAD: iterating over a linked list of 100,000 elements recursively
int listSum(Node node) {
    if (node == null) return 0;
    return node.value + listSum(node.next); // pending addition: NOT tail call
}
// listSum(100_000_node_list) → StackOverflowError at ~500–1000 frames
```

What breaks without TCO:

1. Deep recursion on linked lists, large datasets, or infinite streams is impossible.
2. Functional languages that use recursion instead of loops would be unusable for large inputs.
3. Algorithms naturally expressed as recursion (state machine loops, interpreters) must be rewritten manually as loops with explicit state, losing clarity.

WITH Tail Recursion + TCO:

```scala
// Scala with @tailrec — guaranteed O(1) stack
@tailrec
def listSum(node: Node, acc: Int = 0): Int =
    if node == null then acc                          // base case
    else listSum(node.next, acc + node.value)         // tail call — no pending op
// Works for 1,000,000-element lists — zero stack overflow risk
```

---

### 🧠 Mental Model / Analogy

> Think of handing off a relay baton versus waiting for the previous runner to finish. In normal recursion, each runner (stack frame) _waits_ at the finish line to add their lap time to the total before passing it on — so everyone must stay on the track simultaneously. In tail recursion with an accumulator, each runner _adds their lap time to the baton_ before handing it off, then immediately leaves the track. Only one runner is ever on the track at a time.

"Baton carrying the total" = accumulator parameter
"Adding time before handing off" = multiplying before the recursive call
"One runner on the track" = O(1) stack frames with TCO
"All runners waiting on the track" = O(n) stack frames without TCO

---

### ⚙️ How It Works (Mechanism)

**Tail call position — exactly what qualifies:**

```java
// TAIL CALL — last operation is the call itself
return helper(n - 1, acc * n); // ✓ nothing after this

// NOT a tail call — operation pending after the call
return n * helper(n - 1, acc); // ✗ multiplication pending
return helper(n - 1) + 1;      // ✗ addition pending
return helper(helper(n - 1));  // ✗ outer call pending on inner result
```

**Scala's `@tailrec` annotation:**

```scala
import scala.annotation.tailrec

// @tailrec causes COMPILE ERROR if function is not actually tail-recursive
@tailrec
def factorial(n: Int, acc: Long = 1L): Long =
    if n <= 1 then acc
    else factorial(n - 1, acc * n)  // tail call — compiler converts to loop

// Compiler output (pseudo-JVM bytecode):
// LOOP:
//   if n <= 1: return acc
//   acc = acc * n
//   n   = n - 1
//   goto LOOP
```

**Kotlin's `tailrec` modifier:**

```kotlin
tailrec fun factorial(n: Int, acc: Long = 1L): Long =
    if (n <= 1) acc
    else factorial(n - 1, acc * n)  // Kotlin compiler unrolls to loop
```

**Java without TCO — workaround using a loop:**

```java
// Java: manually convert tail recursion to iteration
long factorial(int n) {
    long acc = 1;
    while (n > 1) {
        acc *= n;
        n--;
    }
    return acc;
}
// Equivalent to tail recursion, but Java requires explicit manual transformation
```

---

### 🔄 How It Connects (Mini-Map)

```
Recursion
  │  ← what is its tail-call form? →
  ▼
Tail Recursion  ◄──── (you are here)
  │
  ├──────────────────────────────────────────────────┐
  ▼                                                  ▼
Tail Call Optimisation (TCO)              Accumulator Pattern
(compiler/runtime transforms to loop)     (carry state as argument)
  │                                                  │
  ▼                                                  ▼
Functional Languages                      Continuation-Passing Style
(Scala, Haskell, Erlang, Clojure)         (advanced: callbacks as args)
```

---

### 💻 Code Example

**Example 1 — Fibonacci tail-recursive:**

```scala
// Standard Fibonacci — exponential WITHOUT memoisation
// NOT tail-recursive (two recursive calls)
def fib(n: Int): Int =
    if n <= 1 then n
    else fib(n-1) + fib(n-2)  // TWO calls, NOT tail

// Tail-recursive Fibonacci with accumulator
@tailrec
def fib(n: Int, prev: Long = 0L, curr: Long = 1L): Long =
    if n == 0 then prev
    else fib(n - 1, curr, prev + curr)   // tail call

fib(1000000) // works without stack overflow
```

**Example 2 — Tail-recursive list sum in Kotlin:**

```kotlin
tailrec fun sumList(node: ListNode?, acc: Long = 0L): Long =
    if (node == null) acc
    else sumList(node.next, acc + node.value)

// With a 1,000,000-element list — stack never exceeds 1 frame
val total = sumList(head)
```

**Example 3 — Trampolining in Java (simulating TCO without compiler support):**

```java
// Trampoline: return a thunk (lambda) instead of calling recursively
// The trampoline loop evaluates thunks until a final value is returned
interface Trampoline<T> {
    boolean isDone();
    T result();
    Trampoline<T> bounce();  // next step

    static <T> T run(Trampoline<T> trampoline) {
        while (!trampoline.isDone()) {
            trampoline = trampoline.bounce(); // iterative "call"
        }
        return trampoline.result();
    }
}

// Tail-recursive factorial as a trampoline
Trampoline<Long> factTrampoline(long n, long acc) {
    if (n <= 1) return done(acc);                           // base case
    return () -> factTrampoline(n - 1, acc * n);            // deferred call
}

long result = Trampoline.run(factTrampoline(1_000_000L, 1L)); // no SO
```

---

### ⚠️ Common Misconceptions

| Misconception                                                           | Reality                                                                                                                                                                                    |
| ----------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Java supports tail call optimisation                                    | The JVM specification does not mandate TCO. Java code with tail calls still pushes frames. Only Scala (via compiler loop conversion) and languages like Kotlin/Clojure provide guarantees  |
| `@tailrec` in Scala optimises the function                              | `@tailrec` causes a compile error if the function is NOT tail-recursive; the optimisation is always performed by the compiler regardless of the annotation — it just validates correctness |
| Tail recursion is always more readable                                  | The accumulator pattern hides the "why" of the parameter. Sometimes a comment explaining the accumulator role is necessary; non-tail-recursive versions are often easier to read           |
| Mutual tail recursion (A calls B, B calls A) is automatically optimised | Direct self tail-calls are optimised by Scala/Kotlin; mutual tail recursion requires trampolining or explicit CPS transformation in most languages                                         |

---

### 🔥 Pitfalls in Production

**Applying `@tailrec` to a function that is NOT actually tail-recursive — compile error**

```scala
// BAD: looks tail-recursive but the multiplication is AFTER the call
@tailrec  // COMPILE ERROR: "could not optimise @tailrec annotated method"
def badFactorial(n: Int): Int =
    if n <= 1 then 1
    else n * badFactorial(n - 1)  // multiplication pending ← NOT tail call

// GOOD: move the pending work into the accumulator
@tailrec
def factorial(n: Int, acc: Int = 1): Int =
    if n <= 1 then acc
    else factorial(n - 1, acc * n) // tail call ✓
```

---

**Java code assuming TCO — production StackOverflowError**

```java
// BAD: developer from Scala background writes "tail-recursive" Java
int countDown(int n) {
    if (n == 0) return 0;
    return countDown(n - 1); // appears to be tail call, but JVM pushes frame
}
countDown(100_000); // StackOverflowError — JVM does NOT do TCO for Java

// GOOD: use a loop in Java when deep iteration is needed
int countDown(int n) {
    while (n > 0) n--;
    return 0;
}
```

---

**Accumulator overflow when type is too narrow**

```java
// BAD: accumulator is int — overflows at 13!
@tailrec
def factorial(n: Int, acc: Int = 1): Int =
    if n <= 1 then acc
    else factorial(n - 1, acc * n)  // factorial(14) overflows Int

// GOOD: use Long (or BigInteger for arbitrary precision)
@tailrec
def factorial(n: Long, acc: BigInt = BigInt(1)): BigInt =
    if n <= 1 then acc
    else factorial(n - 1, acc * n)
```

---

### 🔗 Related Keywords

- `Recursion` — the general technique; tail recursion is its stack-safe specialisation
- `Stack Frame` — the memory unit eliminated by TCO; understanding it explains why TCO works
- `Stack Memory` — the resource that tail call optimisation conserves from O(n) to O(1)
- `Functional Programming` — languages in this paradigm rely on tail recursion to replace loops
- `Accumulator Pattern` — the standard technique for converting non-tail recursion to tail form
- `Continuation-Passing Style (CPS)` — an advanced transformation that makes all calls tail calls
- `Trampolining` — a technique that simulates TCO in languages/runtimes without native support
- `Scala` — JVM language that guarantees tail call optimisation via `@tailrec`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Recursive call is the last operation;     │
│              │ compiler reuses current frame → O(1) stack│
├──────────────┼───────────────────────────────────────────┤
│ TAIL CALL    │ return f(n-1, acc*n)  ← last op is call   │
│ NOT TAIL     │ return n * f(n-1)     ← mult is last op   │
├──────────────┼───────────────────────────────────────────┤
│ JVM SUPPORT  │ Scala (@tailrec), Kotlin (tailrec): YES   │
│              │ Java: NO (convert to loop manually)       │
├──────────────┼───────────────────────────────────────────┤
│ ACCUMULATOR  │ Carry state as a parameter so no pending  │
│              │ computation remains after the call        │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ CPS → Trampolining → Functional Prog →    │
│              │ Scala/Haskell recursion idioms            │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A Scala service processes a stream of financial events by folding over them recursively. The production dataset has 2,000,000 events. The developer adds `@tailrec` to the fold function and sees a compile error. When they inspect the function, they see: `def fold(events: List[Event], acc: State): State = if events.isEmpty then acc else fold(events.tail, process(acc, events.head))`. The annotation still fails. Why might this be, and what specific change would make the annotation succeed and the function stack-safe? Consider both the function's structure and the compiler's requirements for `@tailrec`.

**Q2.** Trampolining is described as a way to achieve stack-safe mutual recursion. In a trampoline, instead of directly calling the next recursive step, a function returns a _thunk_ (a zero-argument lambda wrapping the next call), and an external loop evaluates each thunk sequentially. Explain the trade-off between trampolining and using an explicit iterative loop with an explicit stack for the same problem — comparing code complexity, heap memory usage (thunk allocations vs stack allocations), JIT-friendliness, and debuggability.
