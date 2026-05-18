---
id: CSF-050
title: "Continuation-Passing Style (CPS)"
category: CS Fundamentals - Paradigms
tier: tier-1-foundations
folder: CSF-cs-fundamentals
difficulty: ★★★
depends_on: CSF-024, CSF-027, CSF-028
used_by: CSF-049, JCC-015
related: CSF-049, CSF-028, CSF-027
tags: [cps, continuations, callbacks, async, tail-call-optimization]
status: complete
version: 4
layout: default
parent: "CS Fundamentals - Paradigms"
grand_parent: "Technical Mastery"
nav_order: 50
permalink: /technical-mastery/csf/continuation-passing-style/
---

⚡ TL;DR - CPS = passing "what to do next" as an explicit
callback argument. Every function receives its continuation
(the rest of the program) and calls it with the result
instead of returning. Java's `CompletableFuture.thenApply`
is structured CPS. Callback hell is unstructured CPS.
Async/await is CPS with compiler-generated continuations.

| #050 | Category: CS Fundamentals - Paradigms | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | CSF-024 (Higher-Order Functions), CSF-027 (Recursion), CSF-028 (Tail Recursion) | |
| **Used by:** | CSF-049 (Monads/Functors), JCC-015 (Virtual Threads Internals) | |
| **Related:** | CSF-049 (Monads), CSF-028 (Tail Recursion), CSF-027 (Recursion) | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**

Direct-style (normal) programming: functions return values.
A computation:
```java
int result = step3(step2(step1(input)));
```
This is synchronous: step1 must finish before step2 starts.
No ability to pause step2 in the middle and resume it later.
No ability to run step1 asynchronously and be notified
when it finishes. The call stack is the ONLY mechanism for
"where to return." The stack is implicit: "after `step1`
finishes, return the value up the stack to `step2`."
In asynchronous systems, "returning up the stack" breaks down:
the original stack frame no longer exists by the time the
async operation completes (a different thread, or a future
OS callback invocation, will receive the result).

**THE BREAKING POINT:**

JavaScript in 2010 with AJAX: async operations (network
requests, timers) return results by calling callback functions
(because the original call site's stack no longer exists).
This led to callback hell: three sequential async operations
produce three levels of nesting. Error handling must be
duplicated at each callback level. Refactoring is painful.
The shape of the code mirrors the sequential logic but
as inverted, nested, inside-out callbacks.

**THE INVENTION MOMENT:**

CPS was formalized by Gerald Sussman and Guy Steele in
their work on Scheme (1975) and later by Appel and others
in compiler theory. A CPS transform converts any program
into a form where no function ever returns - instead, every
function receives an explicit continuation (a callback) and
calls it. This form:
(1) Enables compilers to optimize tail calls (because all
calls are tail calls in CPS).
(2) Makes the "rest of the computation" a first-class value
(the continuation can be stored, passed around, resumed multiple times).
(3) Is the formal basis for coroutines, async/await, generators,
and delimited continuations.
`CompletableFuture.thenApply(f)` IS structured CPS: instead
of returning a value, it passes the value to the next function
in the chain (the continuation) when ready.

---

### 📘 Textbook Definition

**Continuation:** The "rest of the computation." At any point
in a program, the continuation is everything that will happen
after the current expression is evaluated - the entire future
of the computation from that point.

**CPS (Continuation-Passing Style):** A programming style
where functions do not return values. Instead, every function
takes an additional argument - the continuation (a function/callback)
- and calls it with the result instead of returning it.
In CPS, the call stack is replaced by explicit continuation
closures.

**CPS transform:** An algorithm that converts any direct-style
program into CPS form. All recursive calls become tail calls
(the CPS-transformed function calls the continuation as
the LAST action). This enables:
- Tail call optimization (no stack growth)
- First-class continuations (call/cc in Scheme)
- Coroutines, generators, async/await (all are continuations)

---

### ⏱️ Understand It in 30 Seconds

**One line:**
CPS = instead of "return the result to the caller," call
a provided callback with the result. The callback is the
continuation (the rest of the program). Every async framework
is built on this idea.

**One analogy:**

> Direct style: you call a restaurant and ORDER. You wait
> on hold. The restaurant makes your food. They say the
> total. You hear it. You pay. Done. (Sequential, blocking,
> return-value-based.)

> CPS: you call a restaurant and ORDER, but also give them
> your phone number (the continuation). You hang up.
> You do other things. When food is ready, the restaurant
> CALLS YOUR NUMBER with the total. You pay. Done. (Non-blocking,
> callback-based, continuation-based.)

> The "phone number to call back" is the continuation.
> `CompletableFuture.thenApply(handler)` = "when done,
> call handler with the result" = passing a continuation.

**One insight:**

`CompletableFuture.thenApply(f)` does NOT call `f(result)`
immediately (unless the future is already complete). It
stores `f` as the continuation. When the computation completes,
the framework calls `f(result)` - this is continuation-passing.
`thenCompose` is flatMap - chaining continuations. A chain
of `thenApply` + `thenCompose` calls is a structured CPS
pipeline. The "async/await" syntax in JavaScript/Kotlin/C#
desugars to exactly this CPS machinery (the compiler generates
the continuation closures).

---

### 🔩 First Principles Explanation

**DIRECT STYLE vs CPS TRANSFORM:**

```
┌──────────────────────────────────────────────────────┐
│ DIRECT STYLE:                                        │
│ int factorial(int n) {                               │
│     if (n == 0) return 1;                            │
│     return n * factorial(n - 1); // stack grows      │
│ }                                                    │
│ // factorial(5) -> 5 * factorial(4) -> 4 * ...      │
│ // Stack depth: O(n)                                 │
│                                                      │
│ CPS TRANSFORM:                                       │
│ void factorialCPS(int n, Consumer<Integer> k) {      │
│     if (n == 0) { k.accept(1); return; }             │
│     // Pass a NEW continuation that multiplies       │
│     // n * (result from recursive call)              │
│     factorialCPS(n - 1, result -> k.accept(n * result));│
│ }                                                    │
│ // Usage:                                            │
│ factorialCPS(5, result -> System.out.println(result));│
│ // All calls are TAIL CALLS (no work after call)     │
│ // Stack: O(1) with TCO (or O(n) closures in Java)   │
│                                                      │
│ KEY INSIGHT: The continuation `k` captures "what to  │
│ do with the result" - it's the return address made   │
│ explicit and first-class.                            │
└──────────────────────────────────────────────────────┘
```

**CALLBACK HELL = UNSTRUCTURED CPS:**

```
┌──────────────────────────────────────────────────────┐
│ // Unstructured CPS (JavaScript callback hell):      │
│ fetchUser(id, function(user) {                       │
│     fetchAddress(user.id, function(addr) {           │
│         fetchCity(addr.cityId, function(city) {      │
│             updateUI(city.name); // finally!          │
│             // Error handling? Must be in each level │
│         });                                          │
│     });                                              │
│ });                                                  │
│                                                      │
│ // Structured CPS (CompletableFuture):               │
│ fetchUser(id)                                        │
│     .thenCompose(user -> fetchAddress(user.getId())) │
│     .thenCompose(addr -> fetchCity(addr.getCityId()))│
│     .thenApply(City::getName)                        │
│     .thenAccept(this::updateUI);                     │
│     // Error handling: .exceptionally(e -> fallback) │
└──────────────────────────────────────────────────────┘
```

---

### 🧪 Thought Experiment

**ASYNC/AWAIT IS COMPILER-GENERATED CPS:**

Kotlin coroutine (or JavaScript async/await):
```kotlin
suspend fun getCityName(userId: String): String {
    val user = fetchUser(userId)     // suspends here
    val addr = fetchAddress(user.id) // suspends here
    val city = fetchCity(addr.cityId)// suspends here
    return city.name
}
```
This LOOKS like direct-style (return value, sequential steps).
Under the hood, the Kotlin compiler TRANSFORMS it to CPS:
- `fetchUser` is called with a continuation that captures
  the rest of `getCityName` (storing `addr`, `city`, `city.name`).
- The continuation is stored as a `Continuation` object (a closure).
- When `fetchUser` completes on another coroutine dispatcher,
  it CALLS the stored continuation with the result.
- The "state machine" generated by the compiler handles
  the multiple suspension points.
This is exactly CPS: every suspension point is a CPS-transformed
call where the continuation is explicitly constructed and stored.
The `suspend` keyword tells the compiler: "apply CPS transform here."

---

### 🎯 Mental Model / Analogy

**RETURN ADDRESS MADE EXPLICIT:**

In direct-style code, the "return address" (where to go
after the current function) is implicit in the call stack
frame. When a function returns, the CPU pops the stack
and jumps to the saved return address. This is low-level CPS.

CPS makes the return address EXPLICIT: instead of the stack
frame saving "return to line 42 of the caller," the caller
explicitly passes `line42Handler` (a function). The callee
calls it directly. This is equivalent - but the continuation
is now a first-class value that can be stored, passed to
other threads, invoked multiple times, or invoked from
completely different parts of the program (generators,
continuations, call/cc).

**MEMORY HOOK:**

"CPS = explicit 'what to do next' passed as argument.
Direct style: function returns value to caller.
CPS: function calls continuation with value.
CompletableFuture.thenApply = structured CPS.
Callbacks = unstructured CPS (no linear reading).
Async/await = compiler-generated CPS (syntactic sugar).
Coroutines = resumable continuations.
CPS enables: TCO, generators, coroutines, call/cc."

---

### 📊 Gradual Depth - Five Levels

**Level 1 - Child:**
Direct: "Get milk, THEN come home." You go, get milk, come home.
CPS: "Get milk, THEN call me and I'll tell you what to do next."
You go, get milk, call mom. Mom says "come home." You go home.
CPS: you hand the continuation to the function instead
of the function returning to you.

**Level 2 - Student:**
```java
// Direct style:
int add(int a, int b) { return a + b; }
int result = add(3, 4); // 7

// CPS:
void addCPS(int a, int b, Consumer<Integer> k) { k.accept(a + b); }
addCPS(3, 4, result -> System.out.println(result)); // prints 7
```

**Level 3 - Professional:**
`CompletableFuture` chain as structured CPS:
```java
// Each thenApply/thenCompose stores the continuation
// to be called when the previous stage completes.
orderService.placeOrder(cart)          // CF<Order>
    .thenCompose(paymentService::charge) // CF<Receipt>
    .thenCompose(emailService::sendConfirmation) // CF<Email>
    .thenApply(Email::getMessageId)    // CF<String>
    .exceptionally(ex -> "error-" + ex.getMessage());
```

**Level 4 - Senior Engineer:**
CPS enables TRAMPOLINING: a technique to avoid stack overflow
in deeply recursive CPS programs. Instead of calling the
continuation directly (which may overflow the stack), return
a thunk (a zero-argument lambda that WOULD call the continuation).
A "trampoline" loop calls the thunk, gets back another thunk,
calls it, etc. No stack growth. Java's virtual threads
effectively implement this via cooperative scheduling (each
virtual thread is a coroutine; the scheduler is the trampoline).

**Level 5 - Expert:**
`call/cc` (call with current continuation) in Scheme:
a function that captures the CURRENT continuation as a
first-class value. This first-class continuation can be:
- Stored and invoked later (resumable computation)
- Invoked multiple times (branching computation)
- Passed to another function (coroutine)
`call/cc` can implement: exceptions (`catch` captures the
continuation at the try site), coroutines (two continuations
passed to each other), generators (capture continuation
at yield point), backtracking (invoke an old continuation
to undo progress). `call/cc` is the universal control-flow
abstraction. Java does not have `call/cc` natively; virtual
threads implement a limited version via thread parking.

---

### ⚙️ How It Works (Formal Basis)

**KOTLIN COROUTINE STATE MACHINE (CPS UNDER THE HOOD):**

```
┌──────────────────────────────────────────────────────┐
│ suspend fun example(): String {                      │
│     val a = asyncA() // suspension point 0           │
│     val b = asyncB() // suspension point 1           │
│     return a + b                                     │
│ }                                                    │
│                                                      │
│ // Compiler generates (conceptually):                │
│ class ExampleContinuation(                           │
│     val completion: Continuation<String>             │
│ ) : Continuation<Any?> {                             │
│     var label = 0  // which suspension point         │
│     var a: String? = null                            │
│                                                      │
│     override fun resumeWith(result: Result<Any?>) {  │
│         when (label) {                               │
│             0 -> { // first call                     │
│                 label = 1                            │
│                 asyncA(this)  // pass `this` as cont │
│             }                                        │
│             1 -> { // resumed after asyncA           │
│                 a = result.getOrThrow() as String    │
│                 label = 2                            │
│                 asyncB(this)  // pass `this` as cont │
│             }                                        │
│             2 -> { // resumed after asyncB           │
│                 val b = result.getOrThrow() as String│
│                 completion.resume(a!! + b) // done   │
│             }                                        │
│         }                                            │
│     }                                                │
│ }                                                    │
│ // The Continuation object IS the CPS callback.      │
│ // label = which continuation are we at.             │
│ // resumeWith = "call the continuation with result"  │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: Callback Hell vs Structured CPS**

```java
// BAD: unstructured callbacks (callback hell)
class OrderService {
    void processOrder(Cart cart, Callback<Void> done) {
        paymentService.charge(cart.getTotal(), paymentResult -> {
            if (paymentResult.isSuccess()) {
                inventoryService.reserve(cart.getItems(), invResult -> {
                    if (invResult.isSuccess()) {
                        emailService.sendConfirmation(
                            cart.getUserEmail(),
                            emailResult -> {
                                if (emailResult.isSuccess()) {
                                    done.onSuccess(null);
                                } else {
                                    done.onFailure(emailResult.getError());
                                    // Need to undo payment & inventory!
                                    // Hard to add compensation here
                                }
                            }
                        );
                    } else {
                        done.onFailure(invResult.getError());
                        // Need to undo payment!
                    }
                });
            } else {
                done.onFailure(paymentResult.getError());
            }
        });
    }
}
// Problems: 4 levels of nesting, error handling repeated and fragile,
// compensation logic (rollbacks) nearly impossible to add correctly.

// GOOD: structured CPS with CompletableFuture
class OrderService {
    CompletableFuture<Void> processOrder(Cart cart) {
        return paymentService.chargeAsync(cart.getTotal())
            .thenCompose(receipt ->
                inventoryService.reserveAsync(cart.getItems())
                    .whenComplete((r, ex) -> {
                        if (ex != null) paymentService.refund(receipt);
                    }))
            .thenCompose(reservation ->
                emailService.sendConfirmationAsync(cart.getUserEmail()))
            .exceptionally(ex -> {
                log.error("Order failed: {}", ex.getMessage());
                throw new OrderException("Order failed", ex);
            });
    }
}
// Linear reading, error propagation automatic,
// compensation logic in whenComplete (runs on success and failure).
```

**Example 2 - CPS Transform Enables Tail Call Optimization**

```java
// Direct recursive fibonacci - stack overflow for large n
long fibonacci(int n) {
    if (n <= 1) return n;
    return fibonacci(n - 1) + fibonacci(n - 2); // two recursive calls
}

// CPS transform - tail recursive (but Java has no TCO; use loop)
// Key insight: CPS makes the "rest of computation" explicit
void fibonacciCPS(int n, long a, long b, Consumer<Long> k) {
    if (n == 0) { k.accept(a); return; }
    if (n == 1) { k.accept(b); return; }
    fibonacciCPS(n - 1, b, a + b, k); // TAIL CALL
    // In a language with TCO (Scheme, Kotlin with tailrec):
    // this call replaces the current stack frame (O(1) space)
}
// fibonacciCPS(10, 0, 1, result -> System.out.println(result));

// Java alternative: trampoline pattern (avoids TCO requirement)
interface Thunk<T> { T call(); } // lazy evaluation
// return a Thunk instead of calling directly, loop calls thunks
```

---

### ⚖️ Comparison Table

| Style | How result is delivered | Stack usage | Composition |
|---|---|---|---|
| Direct style | return value | O(n) depth | Method calls (sequential) |
| CPS (manual) | callback argument | O(n) closures (or O(1) with TCO) | Callback nesting |
| CompletableFuture | thenApply/thenCompose | O(chain length) on heap | Linear chain (structured CPS) |
| Async/await | syntactic sugar | O(suspension points) heap | Sequential-looking CPS |
| Coroutines | resumable continuation | O(local vars) per coroutine | Sequential-looking CPS |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "CPS is only about async programming" | CPS is a general code transformation. It originated in compiler theory (to enable tail call optimization and code analysis) long before async programming was common. CPS is used for: TCO, continuation capture (call/cc), exception handling implementation, generators, and formal program analysis. Async programming uses CPS because async operations naturally "call back" when done - but CPS is broader. |
| "CompletableFuture.thenApply calls the function immediately" | `thenApply` does NOT immediately call the function. It REGISTERS the function as a continuation to be called when the future completes. If the future is already complete at the time of `thenApply` registration, the continuation is scheduled (may be called synchronously or on a thread pool). If not complete, it is stored and called when the future completes (on the completing thread or the specified executor). Understanding this is critical for debugging: print statements inside `thenApply` may execute on a different thread, at a different time, than the surrounding code. |
| "Callbacks are always bad (callback hell)" | Callbacks ARE the CPS mechanism - they're not inherently bad. The problem with "callback hell" is UNSTRUCTURED callbacks: deeply nested, each with its own error handling, no composition. `CompletableFuture`, Promises (JavaScript), and Reactor's `Mono` are all callback-based but STRUCTURED: the continuation is passed via explicit API (`thenApply`, `.then`, `flatMap`) in a readable linear chain. Structured CPS is excellent. Unstructured nesting is the problem, not callbacks per se. |
| "Async/await eliminates the need to understand continuations" | Async/await is SYNTACTIC SUGAR over continuations. Understanding continuations helps explain: why `async` functions must be awaited (the continuation is not called without `await`); why unawaited coroutines may not run (no continuation to resume them); why deadlock occurs in `CompletableFuture.get()` inside `thenApply` (calling `get()` inside a continuation blocks the thread that would complete the future, creating a cycle); why `thenApply(result -> cf.join())` deadlocks on `ForkJoinPool`. Continuations explain the semantics that async/await hides. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: CompletableFuture Deadlock via Blocking**

**Symptom:** A `CompletableFuture` chain hangs forever.
The thread dump shows a thread in `WAITING` state at
`CompletableFuture.join()` inside a `thenApply`.

**Root Cause:** A continuation (inside `thenApply`) calls
`.join()` or `.get()` on ANOTHER `CompletableFuture` that
is scheduled to complete on the SAME thread pool. If the
pool has one thread: that thread is blocking in `.join()`,
and the other CF's completion is queued waiting for the
SAME thread. Deadlock.

```java
// BAD: blocking inside a continuation
CompletableFuture<String> future1 = CompletableFuture.supplyAsync(
    () -> "hello", singleThreadPool);
CompletableFuture<String> future2 = CompletableFuture.supplyAsync(
    () -> "world", singleThreadPool);

// This deadlocks on a single-thread pool:
future1.thenApply(s -> s + " " + future2.join()); // DEADLOCK!
// thenApply runs on singleThreadPool (the completing thread)
// future2.join() blocks that thread
// future2 needs singleThreadPool to complete -> blocked
// Circular wait -> deadlock

// FIX: never block inside continuations
future1.thenCombine(future2, (s1, s2) -> s1 + " " + s2); // correct
```

---

**Security Note:**

CPS and continuations create security challenges around
context propagation. When a continuation is stored and
later invoked on a different thread, the security context
(e.g., Spring Security's `SecurityContextHolder`,
which uses `ThreadLocal`) may not be present on the new
thread. A service that authorizes based on `SecurityContextHolder.getContext().getAuthentication()`
will find null authentication inside a `CompletableFuture`
continuation running on a different thread, causing either
an authorization bypass (if null is treated as "allow")
or an unexpected 401 (if null is treated as "deny").
Fix: Spring Security provides `DelegatingSecurityContextExecutorService`
to wrap executor services and propagate `SecurityContext`
to continuations. Always propagate security context explicitly
when using CPS-style async code.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Higher-Order Functions` (CSF-024) - continuations are
  higher-order functions (functions as arguments)
- `Recursion` (CSF-027) - CPS transform applies to recursive
  functions to enable tail call optimization
- `Tail Recursion` (CSF-028) - CPS transforms all calls
  to tail calls; TCO requires tail calls

**Builds On This (learn these next):**
- `Monads and Functors` (CSF-049) - CompletableFuture monad
  is structured CPS; thenCompose is monadic bind
- `Java Concurrency Advanced` (JCC-015) - virtual threads
  and structured concurrency build on continuation concepts

---

### 📌 Quick Reference Card

```
┌────────────────────────────────────────────────────────┐
│ CPS          │ Pass "what to do next" as callback arg  │
│              │ Function calls callback vs returning     │
├──────────────┼─────────────────────────────────────────┤
│ DIRECT->CPS  │ add(a,b): return a+b                    │
│              │ addCPS(a,b,k): k.accept(a+b)            │
├──────────────┼─────────────────────────────────────────┤
│ STRUCTURED   │ CompletableFuture.thenApply (sync fn)   │
│ CPS (Java)   │ CompletableFuture.thenCompose (async fn)│
│              │ .exceptionally for error CPS             │
├──────────────┼─────────────────────────────────────────┤
│ UNSTRUCTURED │ Callback hell: nested callbacks          │
│ CPS          │ No linear readability, error hell        │
├──────────────┼─────────────────────────────────────────┤
│ ASYNC/AWAIT  │ Compiler-generated CPS (sugar)          │
│              │ Continuation stored at each await point  │
├──────────────┼─────────────────────────────────────────┤
│ DANGER       │ Never block (.join/.get) inside          │
│              │ thenApply/thenCompose (deadlock risk)    │
├──────────────┼─────────────────────────────────────────┤
│ SECURITY     │ SecurityContext not propagated to        │
│              │ continuation threads by default          │
├──────────────┼─────────────────────────────────────────┤
│ NEXT EXPLORE │ CSF-049 (Monads), CSF-028 (TCO)          │
└────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. CPS = passing "what to do next" as an explicit function argument
   (the continuation). Instead of `return value`, the function
   calls `continuation(value)`. This makes the "rest of the
   computation" a first-class value that can be stored, passed
   around, and called at any time (even asynchronously, on
   a different thread). Every async framework uses CPS:
   `CompletableFuture.thenApply(f)` registers `f` as the
   continuation to be called when the future completes.
2. `CompletableFuture.thenApply` vs `thenCompose`: `thenApply`
   is for synchronous transformations (function returns `T`).
   `thenCompose` is for async transformations (function returns
   `CompletableFuture<T>`). Using `thenApply` where `thenCompose`
   is needed gives `CompletableFuture<CompletableFuture<T>>`.
   Same rule as `Optional.map` vs `flatMap`: the function's
   return type tells you which to use.
3. NEVER block inside a `CompletableFuture` continuation
   (`thenApply`, `thenCompose`, etc.). Calling `.join()` or
   `.get()` on ANOTHER `CompletableFuture` inside a continuation
   can deadlock if the completing thread pool also needs to
   complete that other future. Use `thenCombine` for combining
   two independent futures, or ensure different executor pools
   for the continuation and the awaited future.

**Interview one-liner:**
"CPS = passing the continuation (rest of computation) as
an explicit callback argument. `CompletableFuture.thenApply`
(sync transformation) and `thenCompose` (async transformation
returning CF) implement structured CPS. Async/await desugars
to compiler-generated CPS state machines. Never block inside
continuations: calling `.join()` inside `thenApply` risks
deadlock if the same thread pool must complete both futures."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
CPS is the underlying structure of all asynchronous programming.
Whether it is callbacks in Node.js, Promises in JavaScript,
`CompletableFuture` in Java, `Mono`/`Flux` in Reactor,
coroutines in Kotlin, or `async`/`await` in C#: all are
syntactic or library-level presentations of CPS. The mental
model is always: "this function does not return a value;
instead, it will call a provided function with the value
when the computation is complete." Understanding this mental
model explains:
- Why you cannot `return` from inside a callback in non-CPS code.
- Why errors must be propagated through the continuation chain
  (they cannot "throw" up a non-existent stack).
- Why context (SecurityContext, MDC trace IDs) does not
  propagate automatically to continuations.
- Why circular dependencies between continuations cause deadlocks.

**Where else this pattern appears:**

- **JavaScript Promises and async/await** - Promises are
  continuation objects. `promise.then(f)` registers `f` as
  the continuation to call when the promise resolves.
  `promise.catch(f)` registers the error continuation.
  `async function` desugars to a function that returns a Promise
  and transforms the function body into a CPS state machine
  at each `await` point. The event loop is the trampoline:
  it calls pending continuations (microtasks = resolved Promise
  callbacks) in a loop. Understanding CPS explains why `async`
  functions "run" in two parts: synchronously up to the first
  `await`, then asynchronously via the continuation.
- **Spring WebFlux / Project Reactor** - `Mono<T>` is a
  lazy continuation: it does nothing until subscribed.
  `subscribe(callback)` registers the terminal continuation.
  `map(f)` and `flatMap(f)` build up a chain of continuations
  (like a linked list of closures). When subscribed, the
  chain is executed from left to right, each stage calling
  the next as its continuation. `onErrorResume` is the
  error continuation. Backpressure in `Flux` is implemented
  by making the continuation (downstream subscriber) control
  how many elements are requested from the upstream (demand-driven CPS).
- **Compiler CPS for optimization** - Modern compilers
  (including GraalVM, LLVM, and GHC) internally convert
  programs to CPS or SSA (Static Single Assignment) form
  for optimization. In CPS form: every computation is a
  tail call (no "returning"), enabling dead code elimination
  (unreachable continuations), continuation inlining
  (eliminating closure allocation), and escape analysis
  (determining if a continuation escapes the local scope
  to decide stack vs heap allocation). CPS is not just a
  programming style - it's a compiler intermediate representation.

---

### 💡 The Surprising Truth

JavaScript's `async`/`await` syntax (introduced in ES2017)
was celebrated as making asynchronous code "look synchronous."
The dirty secret: under the hood, the JavaScript engine
performs a CPS transform on every `async` function. Each
`await` point becomes a "suspension point" where the engine:
(1) captures the current state (local variables, instruction
pointer) as a continuation closure, (2) stores it, (3) returns
control to the event loop. When the awaited promise resolves,
the event loop retrieves the continuation and calls it with
the resolved value. The "synchronous-looking" code is compiled
to a state machine (exactly like the Kotlin coroutine example).
This is why `await` can ONLY be used inside `async` functions:
the `async` keyword tells the compiler "transform this function
to CPS." You cannot use `await` in a regular function because
regular functions have no CPS machinery. Async/await did not
eliminate CPS - it made CPS invisible to the programmer.
The CPS is still there, generated by the compiler. This is
the same reason Java `suspend` functions can only be called
from other `suspend` functions or coroutines.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **[TRANSFORM]** Convert this direct-style function to CPS:
   ```java
   int addThenDouble(int a, int b) {
       return (a + b) * 2;
   }
   ```
   Write `addThenDoubleCPS(int a, int b, Consumer<Integer> k)`.

2. **[IDENTIFY]** Identify three uses of CPS in a Spring Boot
   application that uses `CompletableFuture` for database calls.
   For each: name the continuation, name what triggers it,
   and name what thread it runs on by default.

3. **[DIAGNOSE]** Given a `CompletableFuture` that hangs,
   take a thread dump and interpret the `WAITING` states.
   Determine if it is a deadlock (one CF waiting for another
   that is waiting for the first's thread).

4. **[COMPARE]** Show the CPS equivalent of a `try-catch-finally`
   block using `CompletableFuture`:
   - `try` body: `supplyAsync(task)`
   - `catch (Exception e)`: `exceptionally(e -> ...)`
   - `finally`: `whenComplete((result, ex) -> cleanup())`

5. **[EXPLAIN]** Why does calling `CompletableFuture.join()`
   inside a `thenApply` callback potentially deadlock on a
   single-threaded executor? Draw the wait graph and name
   the Coffman condition that is violated.

---

### 🧠 Think About This Before We Continue

**Q1.** `CompletableFuture.thenApplyAsync(f)` vs
`CompletableFuture.thenApply(f)`: what is the difference
in how the continuation `f` is called?

*Hint:
`thenApply(f)`: the continuation `f` is called on the thread
that completes the future. If a thread pool thread completes
the future, `f` runs on THAT thread. If the future is already
complete when `thenApply` is registered (in the calling thread),
`f` runs on the calling thread (sync call). This means `f`
runs in the same context as the completing computation -
efficient (no thread switch), but risky if `f` is long-running
(blocks the completing thread, which may be shared).
`thenApplyAsync(f)`: the continuation is ALWAYS submitted
to the default executor (ForkJoinPool) as a new task, even
if the future is already complete. Guarantees the continuation
runs on a pool thread, not the calling thread. Adds thread
switch overhead. Use when: the continuation is long-running,
the completing thread is precious (e.g., Netty I/O thread),
or you want predictable threading behavior.*

**Q2.** Explain why generators (Python `yield`, JavaScript
`function*`) are a form of CPS.

*Hint: A generator function has a "suspension point" at each
`yield`. When it yields a value, it must "remember where it
left off" and be resume-able. This is exactly what a continuation
is: the state of the computation at a suspension point.
The generator's `next()` call is "calling the continuation":
it resumes execution from the last yield. Under the hood,
compilers transform `yield` exactly like `await` - into
a CPS state machine where each yield captures the local
state as a continuation object. The generator object IS
the continuation: it holds the suspended state. The caller
controls when the continuation is invoked (via `next()`).
This is "delimited continuation": the continuation is bounded
by the scope of the generator function, unlike `call/cc`
which can capture the entire rest of the program.*

---

### 🎯 Interview Deep-Dive

**Q1: "What is the difference between `thenApply`, `thenCompose`, and `thenCombine` in CompletableFuture?"**

*Why they ask:* Tests practical knowledge of Java async programming.
These are the most commonly confused CF methods.

*Strong answer includes:*
- `thenApply(Function<T,U>)`: synchronous transformation.
  Takes the result of the future, applies a function, returns
  a new `CompletableFuture<U>`. The function returns a plain value.
  Analogous to `Optional.map`.
- `thenCompose(Function<T, CompletableFuture<U>>)`: chains
  another async operation. The function returns `CompletableFuture<U>`.
  Result is `CompletableFuture<U>` (not `CF<CF<U>>`).
  Use when the next step is also async. Analogous to `Optional.flatMap`.
- `thenCombine(CF<U>, BiFunction<T,U,V>)`: combines two
  INDEPENDENT futures. Both run in parallel; when BOTH complete,
  the BiFunction is called with both results. Use for parallel
  independent async tasks (no sequencing). Not a monad operation
  (applicative functor).
- Rule of thumb: sequential dependency = `thenCompose`. Parallel
  independent = `thenCombine`. Sync transformation = `thenApply`.

**Q2: "What is callback hell and how does CompletableFuture solve it?"**

*Why they ask:* Tests understanding of why modern async APIs exist.

*Strong answer includes:*
- Callback hell: nested callbacks where each async step's
  continuation is nested inside the previous step's callback.
  Results in: deep nesting, duplicated error handling at each
  level, inability to compose (extract a step into a method
  without changing all surrounding code), difficult debugging
  (stack traces do not show the logical chain, only the current
  callback).
- `CompletableFuture` solution: structured CPS. Each step
  is registered as a continuation via `thenApply`/`thenCompose`.
  Continuations form a LINEAR chain (not nested). Error handling
  is done ONCE at the end via `exceptionally`. The chain is
  readable top-to-bottom. Individual steps can be extracted
  as methods (`userService::fetchAsync`) and composed without
  restructuring.

**Q3: "Why does async/await not eliminate the need to understand continuations?"**

*Why they ask:* Tests depth of understanding. Senior+ question.

*Strong answer includes:*
- Async/await is syntactic sugar over continuations. The compiler
  transforms `await expr` into "store current state as continuation,
  resume when expr completes." This transformation is invisible
  to the programmer but produces concrete runtime behavior.
- Understanding continuations explains:
  1. Why `async` "infects" callers (called function must `await`,
     requiring the caller to be `async`).
  2. Why `await` inside a `synchronized` block can deadlock
     (the lock is held across the continuation; if resumption
     needs the same lock, deadlock).
  3. Why `SecurityContext` (ThreadLocal) is not present in
     resuming threads.
  4. Why `await` inside `forEach` does not work as expected
     (the lambda is not `suspend`/`async`, so the continuation
     cannot be created for it).
  The rule: understand the abstraction under the sugar to
  correctly use the sugar in all edge cases.
