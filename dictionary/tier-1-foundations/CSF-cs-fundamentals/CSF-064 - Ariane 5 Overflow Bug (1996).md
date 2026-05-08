---
id: CSF-064
title: Ariane 5 Overflow Bug (1996)
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
nav_order: 64
permalink: /csf/ariane-5-overflow-bug-1996/
---

# CSF-064 - Ariane 5 Overflow Bug (1996)

⚡ TL;DR - The Ariane 5 rocket exploded 37 seconds into its maiden flight because code reused from Ariane 4 caused a 64-bit float to 16-bit integer overflow that triggered a diagnostic exception — which the flight computer interpreted as trajectory data and destroyed the rocket.

| CSF-064         | Category: CS Fundamentals - Paradigms | Difficulty: ★★★ |
| :-------------- | :------------------------------------ | :-------------- |
| **Depends on:** | CSF-012, CSF-036, CSF-061             |                 |
| **Used by:**    |                                       |                 |
| **Related:**    | CSF-036, CSF-061, CSF-063             |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Before Ariane 5, code reuse was universally praised as a
best practice: reuse tested code from working systems.
The failure to validate reused code's assumptions about
input ranges was not a widely-recognised failure mode.
Integer overflow was treated as an implementation detail,
not a safety risk.

**THE BREAKING POINT:**
June 4, 1996: Ariane 501 launched. After 37 seconds, the
rocket self-destructed. Loss: $370 million in rocket +
payload. Root cause: a diagnostic module from Ariane 4
calculated a 64-bit float (horizontal velocity) that, when
converted to a 16-bit integer, overflowed. This raised an
exception in Ada (which Ariane 4's slower velocity never
triggered). The backup computer treated the exception
handler's diagnostic output as flight data. The rocket
thought it was 180° off course; fired full lateral
thrusters; aerodynamic forces disintegrated it.

**THE INVENTION MOMENT:**
The Ariane 5 investigation report (Lions et al., 1996) is
one of the most thorough software failure analyses ever
published. It established: reused code must be validated
against new inputs; numeric ranges must be documented and
checked; exception handlers in safety-critical systems
must be designed for fail-safe; diagnostic data and flight
data must be strictly separated.

**EVOLUTION:**
Ariane 5 directly influenced DO-178C (aviation software)
and ESA's software engineering standards. Modern practice:
fuzz testing for integer boundaries, contract-based programming
(preconditions on numeric inputs), and formal verification
for critical numeric calculations.

---

### 📘 Textbook Definition

An **integer overflow** occurs when an arithmetic operation
produces a value outside the representable range of the
target type. In Ada, overflow raises an exception; in C,
signed overflow is undefined behaviour; in Java, integer
wraps silently. The **Ariane 5 flight software bug** was a
numeric conversion overflow: a 64-bit floating-point
horizontal bias velocity was narrowed to a 16-bit signed
integer. Ariane 5's higher acceleration (3-5x Ariane 4)
produced values that exceeded the 16-bit range, triggering
an Ada overflow exception in the inertial reference system.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Ariane 5 exploded because reused code from a slower rocket overflowed when fed the faster rocket's velocity data, turning an integer overflow into a catastrophic crash.

**One analogy:**

> Imagine reusing a speedometer from a bicycle in a sports
> car. The speedometer reads up to 60 mph; the car can do
> 200 mph. At 61 mph, the needle wraps to 0. The car's
> cruise control reads "0 mph" and floors the accelerator.
> The car crashes. The speedometer wasn't wrong for a bicycle;
> but its assumptions didn't hold for the sports car.

**One insight:**
Reused code carries implicit assumptions about input ranges.
Code that is "tested" and "reliable" in one context may be
dangerously wrong in a new context with different inputs.
Context-change is one of the most dangerous forms of technical debt.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Integer types have bounded ranges; values outside the range overflow or raise exceptions.
2. Narrowing conversion (64-bit float to 16-bit int) can silently lose precision or raise exceptions.
3. Reused code's preconditions (valid input range) must be verified for the new context.
4. Exception handlers must not produce output that is misinterpreted as valid data by callers.
5. Diagnostic data and operational data must be strictly separated in safety-critical systems.

**THE BUG:**

```ada
-- Inertial Reference System (IRS) code reused from Ariane 4
declare
    BH: Float64;           -- horizontal bias velocity
    BH_Word: Integer16;    -- 16-bit register
begin
    -- BH within Ariane 4 range: -32768 to +32767
    -- Ariane 5 BH: much larger (5x faster acceleration)
    BH_Word := Integer16(BH); -- OVERFLOW EXCEPTION!
exception
    when others =>
        BH_Word := 16#7FFF#; -- Exception handler: outputs 32767
        -- This value is sent to flight computer as "IRS data"
        -- Flight computer interprets 32767 as trajectory offset
        -- Rocket fires lateral thrusters -> aerodynamic failure
end;
```

**DERIVED LESSON:**

- Validate input preconditions before narrowing conversion
- Exception handlers should fail safe (shut down the module), not produce substitute data
- Reused components must be re-validated for new input envelopes

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** High-performance rockets generate larger velocity values.
**Accidental:** Reused code without range validation; exception output mistaken for valid data.

---

### 🧪 Thought Experiment

**SETUP:**
Function converts velocity (float) to a hardware register (16-bit int).

**BUGGY (Ariane 4 style):**

```java
// Works for Ariane 4 velocity range (<32767)
short velocityRegister(double velocity) {
    return (short) velocity; // silent wrap in Java!
    // Java: (short) 40000.0 = -25536 (wrong!)
    // Ada: overflow exception (caught but mishandled)
}
```

**SAFE VERSION:**

```java
short velocityRegister(double velocity) {
    if (velocity < Short.MIN_VALUE || velocity > Short.MAX_VALUE) {
        // Fail safe: return error code; shut down module
        throw new ArithmeticException(
            "Velocity " + velocity + " exceeds 16-bit range");
    }
    return (short) velocity;
}
// Or: use precondition annotation (Design by Contract)
```

**THE INSIGHT:**
Validate inputs before narrowing conversions. The check
costs 2 instructions. The absence of the check cost a
$370M rocket and its payload.

---

### 🧠 Mental Model / Analogy

> A 16-bit integer is a container with a fixed capacity.
> Pouring more liquid than it holds overflows onto the floor
> (wraps in C) or triggers an alarm (exception in Ada).
> The problem isn't the container's size; it's using a small
> container when the liquid grew larger. Reuse without
> validation is using last year's container for this year's
> larger batch.

**Element mapping:**

- Container = integer type (16-bit)
- Capacity = `MAX_VALUE` / `MIN_VALUE`
- Overflow = value exceeding capacity
- Last year's container = Ariane 4 code
- Larger batch = Ariane 5 velocity range

Where this analogy breaks down: integer overflow wraps silently
(Java) or raises exception (Ada); liquid overflow is always
physically visible.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Numbers have maximum values in computers. Ariane 5 used old
code that assumed a smaller maximum speed. When Ariane 5
went faster than the old code expected, a number overflowed.
This caused a crash that blew up the rocket.

**Level 2 - How to use it (junior developer):**
Whenever you narrow a type (long to int, float to short):
add a range check. Never assume old code's input range
still applies. When reusing code: re-read its preconditions
and verify they still hold in the new context. Use
`Math.toIntExact()` in Java: throws on overflow.

**Level 3 - How it works (mid-level engineer):**
Java silently wraps integer overflow: `(int) Long.MAX_VALUE = -1`.
Ada raises `Constraint_Error`. C/C++: signed overflow is UB;
unsigned wraps. The diagnostic failure: the Ariane 5 exception
handler caught the overflow and substituted a diagnostic
value (32767) that was then relayed to the flight computer.
The flight computer had no way to distinguish diagnostic
data from real trajectory data.

**Level 4 - Why it was designed this way (senior/staff):**
The inertial reference system was designed to be self-contained
with its own exception handling. The decision to continue
operating (with substituted diagnostic data) was made for
redundancy: keep the backup computer alive even if the
realignment function fails. This was a design trade-off
(availability vs correctness) that was reasonable for Ariane 4
(where the overflow couldn't occur) but catastrophic for
Ariane 5. The system continued operating, but with wrong data.

**Expert Thinking Cues:**

- When reusing code: re-document input ranges; verify for new context
- When catching exceptions in safety code: is the fallback value safe or could it be misinterpreted?
- Integer overflow in financial code: `Math.toIntExact()`; checked arithmetic libraries

---

### ⚙️ How It Works (Mechanism)

**Java safe narrowing conversion:**

```java
// Unsafe: silent wrap
long bigValue = 40000L;
short unsafe = (short) bigValue; // = -25536, wrong!

// Safe: Math.toIntExact throws on overflow
long bigValue = 40000L;
try {
    int safe = Math.toIntExact(bigValue);
} catch (ArithmeticException e) {
    // Handle overflow: fail safe
    log.error("Value {} exceeds int range", bigValue);
    return ErrorCode.OVERFLOW;
}

// Safe: explicit bounds check
if (bigValue < Short.MIN_VALUE || bigValue > Short.MAX_VALUE) {
    throw new OverflowException(bigValue);
}
short safe = (short) bigValue;
```

**Design by Contract (Ariane 4 -> 5 migration):**

```java
/**
 * @param velocity horizontal velocity in m/s
 * @pre -32767 <= velocity <= 32767 (Ariane 4 envelope)
 * @throws ArithmeticException if velocity exceeds 16-bit range
 */
short encodeVelocity(double velocity) {
    assert velocity >= Short.MIN_VALUE
        && velocity <= Short.MAX_VALUE
        : "velocity out of range: " + velocity;
    return (short) velocity;
}
// Ariane 5 audit: does max velocity stay <= 32767? NO -> fix before flight
```

---

### 🔄 The Complete Picture - End-to-End Flow

**ARIANE 5 FAILURE SEQUENCE:**

```
T+0: Ariane 501 launches           ← YOU ARE HERE
T+37s: Inertial Reference System (IRS)
  |-> Calculates horizontal velocity (BH) as float64
  |-> BH value: ~45000 (Ariane 5 faster than Ariane 4)
  |-> Converts to int16: OVERFLOW -> Ada exception
  |-> Exception handler: BH_Word = 32767 (diagnostic fill)
  |-> Sends 32767 to flight computer as "trajectory data"
Flight computer:
  |-> Receives 32767 as trajectory offset
  |-> Interprets: 180deg off course
  |-> Commands: full lateral thrusters
T+39s:
  |-> Aerodynamic forces exceed structural limits
  |-> Self-destruct activated
  |-> Rocket disintegrates
  |-> Loss: $370M
```

**FAILURE PATH:**

- Exception handler substitutes valid-looking but wrong data
- Flight computer can't distinguish diagnostic from flight data
- No range validation on reused module
- Both backup and primary IRS fail identically (same code, same bug)

---

### ⚖️ Comparison Table

| Language     | Integer Overflow Behaviour   | Safety                |
| ------------ | ---------------------------- | --------------------- |
| C (signed)   | Undefined behaviour          | Dangerous             |
| C (unsigned) | Wraps modulo 2^n             | Predictable but wrong |
| Java         | Wraps silently               | Silent errors         |
| Ada          | `Constraint_Error` exception | Detectable            |
| Rust         | Debug: panic; Release: wrap  | Configurable          |
| Python       | Arbitrary precision          | Never overflows       |

---

### ⚠️ Common Misconceptions

| Misconception                                   | Reality                                                                                                                              |
| ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| "Ada's exception handling prevented the crash"  | Ada's exception was caught but the handler produced wrong data; exceptions are not the solution                                      |
| "The bug was in the hardware"                   | The bug was entirely in the software; hardware performed correctly with the data it received                                         |
| "Testing would have found this"                 | The test suite validated Ariane 4 inputs; Ariane 5's larger velocity envelope was not retested                                       |
| "Reused code is safe code"                      | Reused code is safe in its original context; revalidation is required for new input envelopes                                        |
| "This can't happen today with better languages" | Integer overflow exists in every language; Rust's checked arithmetic and Haskell's arbitrary precision help but require explicit use |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Silent Integer Overflow (Java)**
**Symptom:** Wrong numeric result; no exception.
**Diagnostic:**

```java
// Enable integer overflow checking in tests
assert result == Math.toIntExact((long) a + b)
    : "overflow: " + a + " + " + b;
```

**Fix:** Use `Math.toIntExact()`; checked arithmetic libraries; property tests with boundary values.

**Mode 2: Exception Handler Producing Wrong Data**
**Symptom:** System continues running with corrupted state.
**Root Cause:** Exception handler substitutes data instead of failing safe.
**Fix:** Exception handler should: log the error, set a failure flag, stop producing data, and wait for explicit reset.

**Mode 3: Reused Module with Wrong Preconditions**
**Symptom:** Calculation wrong only for certain input ranges.
**Root Cause:** Preconditions not re-validated after context change.
**Fix:** Document preconditions explicitly; add range-check assertions; re-validate on every reuse.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[CSF-012 - Type Systems (Static vs Dynamic)]]
- [[CSF-036 - Exception Handling Patterns]]

**Builds On This (learn these next):**

- [[CSF-063 - Therac-25 Incident (1985) - Software Fails]]

**Alternatives / Comparisons:**

- Checked arithmetic (Rust, Python)
- Formal specification (Ada SPARK, JML)

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────┐
│ WHAT IT IS      Float-to-int overflow in reused code    │
│                 destroyed a $370M rocket in 1996       │
│ PROBLEM         Reused code's input range assumptions   │
│ IT SOLVES       not revalidated for new context        │
│ KEY INSIGHT     Tested code is safe only in its tested  │
│                 input envelope; context change = risk  │
│ USE WHEN        Any numeric narrowing conversion        │
│ AVOID           Silent narrowing without bounds check   │
│ TRADE-OFF       Defensive range checks add overhead    │
│                 vs catastrophic failure without       │
│ ONE-LINER       Always validate input range on reuse;  │
│                 use checked arithmetic                │
│ NEXT EXPLORE    CSF-061 (UB), Math.toIntExact, SPARK   │
└─────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Integer overflow caused Ariane 5 to self-destruct; reused code from Ariane 4 without re-validating input ranges.
2. Tested code is only safe in the input envelope it was tested in; context change requires revalidation.
3. Exception handlers in safety-critical systems must fail safe; never substitute data that looks like valid output.

**Interview one-liner:**
"The Ariane 5 rocket exploded because code reused from Ariane 4 overflowed a 16-bit integer conversion when fed Ariane 5's higher velocities; the exception handler produced diagnostic data the flight computer interpreted as trajectory data, demonstrating that reused code must be revalidated for new input envelopes and exception handlers must fail safe."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Code is correct in a context, not in the abstract. When
you move code to a new context (different load, different
scale, different input range), you must re-examine its
assumptions. Preconditions are the contract; a context
change is a contract renegotiation that must be explicitly
verified.

**Where else this pattern appears:**

- **Database migration** — code using `INT` for ID assumes <2 billion rows; fails when table grows past 2^31
- **Y2K bug** — code using 2-digit year assumed 19xx; broke in 2000
- **Unix 2038 problem** — code using 32-bit timestamps breaks January 19, 2038 at 03:14:08 UTC

---

### 💡 The Surprising Truth

The investigation committee found that both the primary and
backup inertial reference systems contained the same bug —
because they were identical software units (for redundancy
against hardware failures). The decision to use identical
software for both primary and backup was deliberate: it
guaranteed consistent behaviour. But it meant that a software
bug would affect both simultaneously. This is _common-cause
failure_: independent-looking systems sharing a common
design flaw. True redundancy for software requires _diverse_
implementations, not copies. Ariane 501 had perfect software
redundancy against hardware failures and zero software
redundancy against software bugs.

---

### 🧠 Think About This Before We Continue

**Q1 (Root Cause):** The Ariane 5 overflow would not have
caused a catastrophe if the exception handler had failed
safe (shut down the inertial reference system) instead of
substituting a diagnostic value. What would have happened
to the rocket if the IRS had shut down at T+37s instead
of sending wrong data?

_Hint:_ Research the Ariane 501 investigation report. Was there
a fallback navigation mode? What was the prescribed procedure
for IRS failure during flight? Could the flight have continued
safely without IRS data?

**Q2 (Scale):** A financial system uses `int` (32-bit) for
transaction amounts in cents. The maximum is 21 million
dollars ($2,147,483,647 cents). The system processes
International transactions that can exceed this. What is
the exact failure mode, and what is the safest migration
strategy?

_Hint:_ Integer overflow in Java wraps silently. A $21M+
transaction would produce a negative amount. Overdraft,
misrouting, financial loss. Migration: use `long` (64-bit);
but where is the boundary? Add input validation at all
entry points.

**Q3 (Design Trade-off):** Ada was chosen for Ariane 5 partially
because it raises exceptions on integer overflow (unlike C).
But the exception was caught and the system continued with
wrong data. Does a language that raises overflow exceptions
make safety-critical systems safer, if exception handlers can
still produce wrong data?

_Hint:_ Compare Ada's `Constraint_Error` to Rust's
`checked_add` which returns `Option<T>` (None on overflow).
Rust forces you to handle the overflow case explicitly.
Ada allows you to catch and continue. Which design is safer?
