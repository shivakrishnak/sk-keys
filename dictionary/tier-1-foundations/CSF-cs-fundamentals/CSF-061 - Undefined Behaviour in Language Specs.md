---
id: CSF-061
title: Undefined Behaviour in Language Specs
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
version: 1
layout: default
parent: "CS Fundamentals - Paradigms"
grand_parent: "Technical Dictionary"
nav_order: 61
permalink: /csf/undefined-behaviour-in-language-specs/
---

# CSF-061 - Undefined Behaviour in Language Specs

⚡ TL;DR - Undefined behaviour (UB) in C/C++ gives the compiler permission to assume UB never occurs, enabling aggressive optimisations that silently delete safety checks and produce catastrophically wrong code.

| CSF-061         | Category: CS Fundamentals - Paradigms | Difficulty: ★★★ |
| :-------------- | :------------------------------------ | :-------------- |
| **Depends on:** | CSF-023, CSF-057                      |                 |
| **Used by:**    | CSF-077                               |                 |
| **Related:**    | CSF-057, CSF-077                      |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
If a language fully defined the behaviour of every program,
compilers couldn't optimise as aggressively. "What happens
when you access memory out of bounds?" must have an answer.
Defining it as "trap" costs performance. Defining it as
"return garbage" is observable and constrains optimisation.
Undefined behaviour is the language spec's opt-out: "we
never promise what happens, so the compiler can assume
it never occurs."

**THE BREAKING POINT:**
A Linux kernel security patch (CVE-2009-1897) was silently
removed by GCC's optimiser. The code: `if (ptr + len < ptr)`
(overflow check). GCC's UB-based reasoning: signed integer
overflow is UB, therefore `ptr + len` can never overflow,
therefore `ptr + len < ptr` is always false, therefore the
entire security check is dead code. GCC deleted it.
The kernel shipped without the security check.

**THE INVENTION MOMENT:**
C's original rationale (DMR, 1974-1978): leave hardware-specific
behaviour unspecified to enable portable code. Different
machines handled signed overflow differently. Rather than
picking one behaviour (and breaking other machines), the spec
declared it "undefined." Over decades, compilers evolved
to treat UB not as "leave implementation-defined" but as
"this can never happen; exploit the assumption for optimisation."

**EVOLUTION:**
UndefinedBehaviourSanitizer (`-fsanitize=undefined`) catches
most UB at runtime. Rust's design goal was to eliminate UB
in safe code entirely. Go, Java, and most modern languages
have fully defined semantics for integer overflow and array
access. The C++ Core Guidelines and security hardening
flags (`-ftrapv`, `-fwrapv`) are backfills for decades of UB
in production C++ code.

---

### 📘 Textbook Definition

**Undefined behaviour (UB)** in a programming language
specification is a category of program behaviour where the
spec places no requirements on what the compiler or runtime
does. The compiler is free to: emit any code, crash, produce
wrong results, or delete the offending code entirely.
In C/C++, UB enables aggressive compiler optimisations but
also creates subtle, often security-critical bugs when code
inadvertently exercises UB. **Unspecified behaviour** is
a weaker form: one of several defined outcomes, but the
spec doesn't say which. **Implementation-defined behaviour**:
outcome defined but platform-specific.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Undefined behaviour tells the compiler "this never happens" — so the compiler deletes the code that checks for it.

**One analogy:**

> You promise your employer you'll never work overtime.
> Your employer builds a work schedule assuming no overtime.
> You then work overtime anyway. Your employer's schedule
> is now wrong. UB is that promise to the compiler. If you
> break the promise (invoke UB), the compiler's optimised
> code is wrong. The compiler didn't do anything incorrect;
> you broke the contract.

**One insight:**
UB is a contract between programmer and compiler. The
programmer promises "I will never do X." The compiler
assumes X never happens and optimises accordingly. When X
happens in production, the compiler's generated code is wrong
— but the spec says this is the programmer's fault.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. UB is _not_ a runtime error; it's a specification hole that the compiler exploits.
2. UB-based optimisations are _correct_ given the contract: UB never occurs.
3. When UB does occur at runtime, any behaviour may result: crash, wrong answer, security hole, no effect.
4. Signed integer overflow in C/C++ is UB; unsigned integer overflow wraps (defined).
5. The compiler proof: "if UB never happens, then X is always true, therefore I can eliminate the check."

**DERIVED DESIGN:**

- **Signed overflow**: `INT_MAX + 1` is UB in C (wraps in many implementations, but not guaranteed)
- **Null pointer dereference**: UB (may crash, may return garbage, may delete check)
- **Out-of-bounds array access**: UB (reads adjacent memory; corrupts heap)
- **Unsequenced expressions**: `a[i] = i++` is UB in C (evaluation order unspecified)
- **Data race**: UB in C++11 (concurrent write+read without synchronisation)

**THE TRADE-OFFS:**
**Gain:** Enables aggressive loop vectorisation, null dereference elimination, overflow proof.
**Cost:** Security vulnerabilities; Defensive checks silently removed; programmer must be vigilant.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Hardware has diverse behaviour for overflow and unaligned access.
**Accidental:** C/C++ UB creating security vulnerabilities in security-critical code.

---

### 🧪 Thought Experiment

**SETUP:**
Security check in C: "is this a valid pointer dereference?"

**CODE:**

```c
void processBuffer(int* ptr, int offset) {
    // Security check: detect integer overflow in offset calculation
    if (ptr + offset < ptr) { // overflow check
        return; // reject invalid offset
    }
    *ptr = buffer[offset]; // dereference only if check passes
}
```

**COMPILER REASONING (with -O2):**

```
ptr + offset < ptr
  -> if offset >= 0: ptr + offset >= ptr -> false
  -> if offset < 0: unsigned comparison might work, but
     signed arithmetic: ptr + offset is ptr arithmetic (ptrdiff)
     Pointer arithmetic overflow is UB
     -> compiler assumes overflow never occurs
     -> ptr + offset < ptr is always false
     -> dead code: if block eliminated
     -> no security check generated
```

**RESULT:**

```c
// Compiled as:
void processBuffer(int* ptr, int offset) {
    *ptr = buffer[offset]; // no check!
}
// Security check removed by compiler legally
```

**THE INSIGHT:**
The compiler didn't do anything wrong. The programmer
wrote code that relied on UB behaviour. The compiler
exploited the UB contract to remove the check.

---

### 🧠 Mental Model / Analogy

> UB is a signed contract with the compiler: "I promise
> my code never does X." The compiler uses this promise
> to optimise away checks for X. If you ever do X in
> practice, you've broken the contract — and the
> optimised code is wrong. The compiler is not lying;
> you are. The issue: in a 100,000-line program, it's
> nearly impossible to verify you've never done X.

**Element mapping:**

- Contract = language specification
- Promise = "my code has no UB"
- Compiler optimisation = assuming UB never happens
- Breaking the contract = invoking UB at runtime
- Wrong code = UB-based optimisation producing unexpected behaviour

Where this analogy breaks down: the contract is implicit,
not signed; most C programmers don't know the full list
of UB in C.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Undefined behaviour is when C code does something the
language rules say it shouldn't. Instead of crashing or
correcting it, the compiler assumes it never happens.
Sometimes this means safety checks are silently deleted.

**Level 2 - How to use it (junior developer):**
In C/C++: compile with `-fsanitize=undefined` in development.
This adds runtime checks for common UB (overflow, shift,
out-of-bounds). Never use signed overflow intentionally.
Use unsigned arithmetic for bitwise operations.
In Java/Go/Rust: these languages mostly don't have UB;
arithmetic is defined (wrap or panic).

**Level 3 - How it works (mid-level engineer):**
Modern C/C++ compilers (GCC, Clang) actively use UB as an
optimisation signal. Key examples:

- `if (ptr == NULL) return;` after `*ptr` access: null-check
  eliminated (ptr must not be null because deref is UB; therefore
  null check is always false; compiler removes it)
- Loop: `for (int i=0; i < INT_MAX; i++)` never wraps (signed
  overflow is UB, so `i` always increases; loop always terminates)

**Level 4 - Why it was designed this way (senior/staff):**
The C standard committee's reasoning: defining every hardware
behaviour would require the spec to cover every architecture.
UB is the escape hatch: the spec says "we don't require any
behaviour here" so that hardware vendors can do what's
native and fast. The problem: over 40 years, compiler
technology advanced from "implement UB as hardware-native"
to "actively exploit UB as optimisation axioms." The original
rationale became a security catastrophe.

**Expert Thinking Cues:**

- In C/C++ code reviews: every arithmetic operation on signed integers is a potential UB.
- Security-critical C code: enable `-fsanitize=undefined,address` in CI, not just debug.
- When reviewing "defensive" null checks after dereference: compiler may have removed them.

---

### ⚙️ How It Works (Mechanism)

**Common UB examples:**

```c
// 1. Signed integer overflow (UB)
int x = INT_MAX;
int y = x + 1; // UB! Compiler: x+1 > x always (no overflow)

// 2. Null pointer dereference after check (optimised away)
if (ptr) { // this check may be removed!
    *ptr = 5; // dereference is UB if ptr is null
              // compiler: if we get here, ptr != null,
              // therefore the check above is redundant
}

// 3. Out-of-bounds array read
int arr[10];
int x = arr[10]; // UB! Reads adjacent memory

// 4. Unsequenced evaluation
int i = 0;
arr[i] = i++; // UB! Order of i evaluation unspecified
```

**UBSan detection:**

```bash
# Compile with UBSan
clang -fsanitize=undefined -g overflow.c -o overflow
./overflow
# overflow.c:5:15: runtime error: signed integer overflow:
# 2147483647 + 1 cannot be represented in type 'int'
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW (UB in security check):**

```
Programmer writes overflow check  ← YOU ARE HERE
  if (ptr + len < ptr) { security check; return; }
Compiler with -O2:
  |-> Observes: ptr + len < ptr
  |-> Pointer arithmetic overflow is UB
  |-> Assumption: UB never occurs
  |-> ptr + len < ptr is always false
  |-> Dead code elimination: removes if block
Produced code:
  |-> No security check
  |-> Buffer processed without validation
Attacker:
  |-> Sends oversized payload
  |-> Buffer overflow (check was silently removed)
  |-> Arbitrary code execution
```

**FAILURE PATH:**

- UB in test: may not be triggered (tests pass; production fails)
- UBSan in CI: catches UB at test time if code path is exercised
- Production UB: silent data corruption; delayed crash; security vulnerability

---

### ⚖️ Comparison Table

| Behaviour               | C/C++             | Java                            | Rust (safe)                    | Go              |
| ----------------------- | ----------------- | ------------------------------- | ------------------------------ | --------------- |
| Signed integer overflow | UB                | Wraps (defined)                 | Panic (debug) / Wrap (release) | Wraps (defined) |
| Array out-of-bounds     | UB                | ArrayIndexOutOfBoundsException  | Panic                          | Panic           |
| Null dereference        | UB                | NullPointerException            | Won't compile (Option)         | Panic           |
| Data race               | UB                | Race condition (defined, wrong) | Compile error                  | Race condition  |
| Unaligned access        | UB / impl-defined | N/A (JVM managed)               | Defined (safe ptr)             | Defined         |

---

### ⚠️ Common Misconceptions

| Misconception                      | Reality                                                                                                    |
| ---------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| "UB means crash"                   | UB means anything: crash, wrong result, security hole, or seemingly correct behaviour                      |
| "My tests pass so there's no UB"   | UB may only be triggered by specific inputs or under optimisation; tests may not cover it                  |
| "Compilers are being sneaky"       | Compilers are correct per spec; the spec gives them permission to assume UB never occurs                   |
| "UBSan finds all UB"               | UBSan only finds UB that's exercised at runtime; uninstrumented UB paths are not checked                   |
| "Java has undefined behaviour too" | Java has unspecified behaviour (e.g., finalisation order) but not UB in the C sense; arithmetic is defined |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Security Check Removed by Compiler**
**Symptom:** Security audit shows a check; exploitation still works.
**Root Cause:** Compiler optimised away the check based on UB reasoning.
**Diagnostic:**

```bash
gcc -O2 -S check.c -o check.asm
grep -c 'jl\|jb' check.asm  # count branch instructions
# Fewer than expected: check may have been removed
```

**Fix:** Use `-fno-strict-overflow`; or rewrite using unsigned arithmetic.

**Mode 2: Integer Overflow in Calculation**
**Symptom:** Incorrect large-input results; no crash.
**Diagnostic:**

```bash
clang -fsanitize=integer -g overflow.c
./a.out  # reports integer overflow location
```

**Fix:** Use `__builtin_add_overflow` (GCC/Clang); or use `uint64_t` for large values.

**Mode 3: Null Dereference Check Removed**
**Symptom:** Service crashes; null check was present but didn't fire.
**Root Cause:** Compiler saw dereference before null check; optimised check away.
**Fix:** Move null check before first dereference; use `-fno-delete-null-pointer-checks`.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[CSF-023 - Stack vs Heap Memory]]
- [[CSF-057 - Memory Safety Vulnerabilities in Lang Design]]

**Builds On This (learn these next):**

- [[CSF-077 - Language Design Rationale (Rust, Go, Kotlin)]]

**Alternatives / Comparisons:**

- Rust (eliminates most UB in safe code)
- Java (defines all arithmetic behaviour)

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────┐
│ WHAT IT IS      C/C++ spec hole: compiler assumes UB   │
│                 never occurs; may delete safety checks │
│ PROBLEM         Defensive security checks silently     │
│ IT SOLVES       removed by optimiser                  │
│ KEY INSIGHT     UB = compiler contract: "this never    │
│                 happens"; if it does, anything results │
│ USE WHEN        C/C++: compile with -fsanitize=undefined│
│ AVOID           Signed integer overflow; null check    │
│                 after dereference                    │
│ TRADE-OFF       Optimisation power vs correctness      │
│ ONE-LINER       UB doesn't mean crash; it means the   │
│                 compiler can assume anything          │
│ NEXT EXPLORE    CSF-077, UBSan, Rust safe subset       │
└─────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. UB gives the compiler permission to assume the undefined case never happens; it may delete the code that handles it.
2. Signed integer overflow is UB in C/C++; use `-fsanitize=undefined` to catch it at runtime.
3. Rust's safe subset eliminates UB by design; Java and Go define all arithmetic behaviour.

**Interview one-liner:**
"Undefined behaviour in C/C++ is a spec contract that gives compilers permission to assume UB never occurs, enabling aggressive optimisations; when UB does occur at runtime, any outcome is possible including silently deleted security checks, which is why 70%+ of high-severity CVEs in C/C++ code involve UB."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Optimisations based on assumptions are dangerous when those
assumptions can be violated by runtime data. UB is the
extreme case: the compiler assumes a condition never occurs
and eliminates the guard for it. The same anti-pattern
appears in database query planners (plan based on statistics;
wrong when data distribution changes) and caches (assume
cache hit; slow when miss rate spikes). Defensive code
that guards against "impossible" cases must never rely on
optimiser removal of those guards.

**Where else this pattern appears:**

- **Database query plans** — plan assumes index selectivity; wrong statistics cause wrong plan; no safety check
- **CPU speculative execution** — Spectre/Meltdown: CPU speculates based on assumptions; UB-like side effects leak data
- **Protocol state machines** — assuming "client always sends X before Y" is a spec UB; real clients break it

---

### 💡 The Surprising Truth

The C standard has 191 enumerated undefined behaviours in
C11. Almost every program a beginner writes invokes at least
one of them. The most surprising: returning from `main()
 without a `return 0;`in C89 is UB. Accessing a global
variable from a signal handler is UB (unless`volatile
sig_atomic_t`). Comparing pointers from different objects
with `<`or`>` is UB. The C standard committee didn't
intend these to be security vulnerabilities; they intended
them as latitude for implementations. Modern compiler
aggressiveness turned that latitude into an attack surface.

---

### 🧠 Think About This Before We Continue

**Q1 (Security):** A C library's TLS handshake uses signed
arithmetic for a length calculation: `int remaining = total -
processed;`. If `processed` somehow exceeds `total` (due
to a bug), `remaining` becomes negative. The code then does
`if (remaining > 0) { ... }`. GCC with `-O2` might elide
this check. What exact UB is involved, and how does it
create a security vulnerability?

_Hint:_ Signed underflow (below INT_MIN) is UB. The compiler
may reason: `total - processed` never overflows (UB assumption),
therefore `remaining > 0` is always true for positive `total`,
therefore the check is removed.

**Q2 (Scale):** A codebase has 1 million lines of C. UBSan
reports 500 unique UB occurrences in the test suite.
How many actual security vulnerabilities does this represent?
What is the process for triaging which are exploitable?

_Hint:_ Not all UB is exploitable. Overflow in a hash function
may produce wrong hash (not a security issue). Overflow in
a length calculation before a `malloc` is exploitable (integer
wrap -> small allocation -> buffer overflow). Triage by:
is the UB on an attacker-controlled value? Does it affect
pointer arithmetic or allocation sizes?

**Q3 (Design Trade-off):** Rust's safe subset has no UB.
But `unsafe` Rust can have UB. Unsafe is required for FFI,
certain low-level operations, and some performance-critical
code. How does Rust's approach to `unsafe` compare to C's
approach to UB, and what is the safety advantage of Rust
even with `unsafe` code?

_Hint:_ In C, all code can have UB anywhere. In Rust,
UB can only occur in `unsafe` blocks. The rest of the
codebase is provably safe. The unsafe surface area is
limited, auditable, and explicitly marked.
