---
id: CSF-071
title: Therac-25 Incident (1985) - Software Fails
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
version: 2
layout: default
parent: "CS Fundamentals - Paradigms"
grand_parent: "Technical Dictionary"
nav_order: 67
permalink: /csf/therac-25-incident-1985-software-fails/
---

# CSF-067 - Therac-25 Incident (1985) - Software Fails

⚡ TL;DR - The Therac-25 radiation therapy machine killed six patients because software race conditions removed hardware safety interlocks; it is the canonical case study in why software cannot replace hardware safety mechanisms.

| CSF-067         | Category: CS Fundamentals - Paradigms | Difficulty: ★★★ |
| :-------------- | :------------------------------------ | :-------------- |
| **Depends on:** | CSF-043, CSF-052                      |                 |
| **Used by:**    | CSF-068                               |                 |
| **Related:**    | CSF-052, CSF-068                      |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Before Therac-25, concurrent software failure modes in
safety-critical systems were treated as theoretical. The
prevalence of concurrent access bugs in medical devices was
unknown. Developers trusted that "the software was tested"
was sufficient assurance for safety-critical systems.

**THE BREAKING POINT:**
Between June 1985 and January 1987, the Therac-25 radiation
therapy machine overdosed at least six patients with
massive radiation doses. Three patients died. The machine
reported no error and showed "MALFUNCTION 54" — a generic
message. Operators reset and continued treatment. The root
cause: a race condition invisible in single-threaded testing.

**THE INVENTION MOMENT:**
The Therac-25 investigation (Nancy Leveson, Clark Turner, 1993)
became the seminal paper in software safety engineering.
It established principles: software cannot replace hardware
safety interlocks; concurrent race conditions require explicit
testing; error messages must be unambiguous; safety-critical
software needs independent review.

**EVOLUTION:**
Therac-25 influenced: DO-178 (aviation software certification),
IEC 62304 (medical device software), ISO 26262 (automotive).
These standards mandate independent safety review, fail-safe
design, and hardware safety interlocks independent of software.
Every safety-critical software standard today traces to
lessons from Therac-25.

---

### 📘 Textbook Definition

The **Therac-25** was a radiation therapy machine (AECL,
1982-1987) that used a PDP-11 software control system to
position a turret selecting between therapy modes. A **race
condition** in the operator interface allowed the turret to
remain in the wrong position while the machine fired. The
software-only safety interlock (replacing hardware interlocks
from the Therac-20) was defeated by the race condition.
Patients received 100x the intended radiation dose.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A race condition in medical device software removed safety checks when operators typed quickly, causing overdoses that killed patients.

**One analogy:**

> The Therac-25 is like a nuclear power plant where the
> emergency shutdown switch works only if you don't press
> two buttons within 8 seconds of each other. Nobody tested
> that combination. An operator who worked fast enough
> triggered the exact sequence. The emergency shutdown
> was bypassed. The reactor overheated.

**One insight:**
Software testing in normal conditions doesn't find timing-dependent
bug. The Therac-25 bug required operator actions within
a specific timing window of approximately 8 seconds. This
only occurred with experienced, fast operators — the people
most trusted to operate the machine.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Hardware interlocks are physically independent of software; software bugs can't defeat them.
2. Software safety checks can be defeated by race conditions, UB, or simple bugs.
3. "Tested" software is not the same as "verified" software for safety-critical applications.
4. Error messages must identify actionable root causes, not generic codes.
5. Concurrent systems require explicit concurrency testing, including timing variations.

**THE RACE CONDITION:**

```
Operator types 'X' (X-ray mode), then quickly edits to 'E' (electron mode)

Thread 1 (display): shows cursor at parameters position
Thread 2 (setup): checks turret position
Shared flag: editFlag (set when editing, cleared when done)

Bug: if operator edits parameter within ~8 sec of mode change:
  Thread 2 checks editFlag = 1 (still editing) -> skips turret check
  Thread 2 fires beam -> turret still in high-power X-ray position
  Beam fires at 100x intensity through wrong aperture
  Patient receives lethal dose
```

**DERIVED LESSON:**

- Hardware interlock: turret physically prevented from being in wrong position
- Software interlock: checks a flag; race can bypass the check
- Never replace hardware safety mechanisms with software-only checks
- Safety must be fail-safe: default to safe state on any anomaly

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Radiation therapy requires precise control; timing is inherently complex.
**Accidental:** Removing hardware interlocks; using a shared flag without synchronisation.

---

### 🧪 Thought Experiment

**SETUP:**
Two threads share a `safeToFire` flag:

```c
// Thread 1 (operator interface)
void processInput() {
    editFlag = 1;           // start editing
    updateParameters();     // user edits
    editFlag = 0;           // done editing
    // Notify Thread 2 that mode is confirmed
}

// Thread 2 (beam controller)
void checkAndFire() {
    if (editFlag == 0) {    // if not editing
        verifyTurretPosition(); // check hardware
        fireBuf();              // fire beam
    }
    // BUG: if editFlag changes between check and fire:
    // editFlag = 0 (check passes)
    // Thread 1: editFlag = 1 (start editing)
    // Thread 2: fire! (but parameters are being modified)
}
```

**THE INSIGHT:**
The flag is a classic check-then-act race condition.
`synchronized` (Java) or a hardware interlock would prevent
this. The Therac-25 PDP-11 OS had no atomic test-and-set;
the programmer relied on timing that worked in testing
but failed with fast operators.

---

### 🧠 Mental Model / Analogy

> A level crossing without automatic barriers. A human
> guard waves a flag when a train is coming. If the guard
> is distracted for 2 seconds, a car can pass. Hardware
> interlocks are automatic barriers: they work regardless
> of what anyone does. Software interlocks are the guard:
> reliable when working normally; bypassed when something
> goes wrong.

**Element mapping:**

- Level crossing = Therac-25 beam aperture
- Human guard = software safety check
- Distraction = race condition
- Automatic barrier = hardware interlock
- Car passing = beam firing in wrong mode

Where this analogy breaks down: software bugs are
deterministic (given the same state); hardware failures
are probabilistic. Both require defence-in-depth.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
A radiation machine had a bug: if operators typed commands
too fast, a safety check was skipped. The machine overdosed
patients. Nobody knew because the error message was cryptic.
This taught the world that software bugs in safety-critical
machines kill people.

**Level 2 - How to use it (junior developer):**
Lesson: never use "check then act" with shared mutable state.
`if (safeToFire) { fireBufer(); }` is a race condition if
`safeToFire` can change between the check and the act.
Use `synchronized` blocks, atomic operations, or hardware
interlocks for safety-critical conditions.

**Level 3 - How it works (mid-level engineer):**
The PDP-11 was a single-CPU machine. The Therac-25 used
cooperative multitasking: tasks yielded control voluntarily.
The operator interface task and the beam control task ran
on the same CPU. The race existed because the operator
task could modify shared state between the controller
task's check and its action. This is a classic
time-of-check to time-of-use (TOCTOU) race condition.

**Level 4 - Why it was designed this way (senior/staff):**
The Therac-25 was a redesign of the Therac-20, which had
hardware safety interlocks. The Therac-25 design team
believed that software was more reliable than hardware
interlocks (which could fail mechanically). They removed
the hardware interlocks and replaced them with software
checks. This was the fundamental design error: hardware
failure is detectable and probabilistic; software bugs can
create systematic failures that affect every unit in the field.

**Expert Thinking Cues:**

- Safety-critical system: are hardware and software safety mechanisms independent?
- Error message: does it identify the root cause, or is it a generic code?
- Race condition in safety code: is every check-then-act protected by an atomic operation?

---

### ⚙️ How It Works (Mechanism)

**TOCTOU Race (Time-Of-Check To Time-Of-Use):**

```java
// Classic TOCTOU - same pattern as Therac-25
if (file.exists()) {         // check
    file.delete();           // use - may fail if another
                             // thread deleted between check+use
}

// Safe version: atomic operation
boolean deleted = file.delete(); // atomic: checks and deletes
if (!deleted) { /* handle: file didn't exist */ }
```

**Hardware interlock (conceptual):**

```
Hardware: physical relay
  -> Turret position sensor -> relay coil
  -> If turret not in correct position: relay open
  -> Relay open: beam circuit broken
  -> Beam CANNOT fire regardless of software state
  -> Software bug: irrelevant (hardware prevents firing)
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW (Therac-25 failure sequence):**

```
Operator: type 'X' (X-ray), then quickly edit to 'E'
  |                                    ← YOU ARE HERE
  | Thread 1 (UI): processing edit
  | editFlag set to 1 (editing)
  | Thread 2 (beam ctrl): checks editFlag
  |   editFlag = 1? -> normally skips to wait
  |   BUT: timing window: editFlag = 0 (edit just finished)
  |   Thread 2: check turret position (check passes: stale)
  |   Thread 1: modifies turret command (race!)
  |   Thread 2: fires beam at wrong setting
Patient receives 100x dose
Machine: MALFUNCTION 54 (generic code)
Operator: "just a glitch"; press 'P' to proceed
Second dose fired: lethal
```

**FAILURE PATH (systemic):**

- Generic error code: operator doesn't know severity
- No hardware interlock: software bug is not blocked
- Machine proceeds after reset: no fail-safe behaviour
- No logging of parameters: investigation delayed weeks

---

### ⚖️ Comparison Table

| Safety Mechanism          | Therac-25                  | Best Practice                        |
| ------------------------- | -------------------------- | ------------------------------------ |
| Interlock type            | Software-only              | Hardware + software (independent)    |
| Error message             | "MALFUNCTION 54" (generic) | Specific, actionable description     |
| Race condition protection | None                       | Atomic operations / mutex            |
| Fail-safe behaviour       | Resume on reset            | Stop until explicit re-authorisation |
| Code review               | No independent review      | Mandatory safety review              |
| Testing                   | Functional only            | Concurrent + stress + timing tests   |

---

### ⚠️ Common Misconceptions

| Misconception                                                          | Reality                                                                                                          |
| ---------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| "Therac-25 was software used by untrained operators"                   | The overdoses were caused by experienced, fast operators                                                         |
| "The bug would have been obvious in code review"                       | The race required precise timing; a code reader couldn't see it without analysing timing                         |
| "Software is more reliable than hardware"                              | Hardware interlocks fail in bounded, detectable ways; software bugs can cause systematic, undetectable failures  |
| "Testing would have caught this"                                       | Functional testing (slow operation) never triggered the race; only fast operation in a specific window caused it |
| "This is a historical problem; modern systems don't have these issues" | Toyota unintended acceleration (2009-2010), Boeing MCAS (2018-2019) are modern equivalents                       |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: TOCTOU Race in Safety Check**
**Symptom:** Safety condition bypassed under specific timing.
**Diagnostic:** Thread analysis; add logging with timestamps; stress-test with concurrent operations.
**Fix:** Replace "check then act" with atomic hardware interlock or atomic software primitive.

**Mode 2: Ambiguous Error Messages**
**Symptom:** Operator cannot determine severity; may proceed when should stop.
**Fix:** Error messages must: identify the specific failure, state the severity, and prescribe the action ("DO NOT PROCEED; contact service").

**Mode 3: Missing Fail-Safe Default**
**Symptom:** System resumes dangerous operation after reset.
**Fix:** Safety systems must fail to the safe state; require explicit positive authorisation to resume after any safety anomaly.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[CSF-052 - Concurrency Anti-Patterns (Shared State)]]
- [[CSF-043 - Concurrency Models Introduction]]

**Builds On This (learn these next):**

- [[CSF-068 - Ariane 5 Overflow Bug (1996)]]

**Alternatives / Comparisons:**

- IEC 62304 (medical device software standard)
- DO-178C (aviation software certification)

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────┐
│ WHAT IT IS      Race condition in medical device removed │
│                 safety interlock; patients overdosed    │
│ PROBLEM         Software race defeats safety check;     │
│ IT SOLVES       hardware interlocks are immune         │
│ KEY INSIGHT     Never replace hardware safety with      │
│                 software-only checks                  │
│ USE WHEN        Designing safety-critical systems;      │
│                 reviewing safety interlocks            │
│ AVOID           Software-only safety interlocks        │
│ TRADE-OFF       Hardware interlocks add cost;           │
│                 removing them adds fatal risk          │
│ ONE-LINER       Race condition + no hardware fallback = │
│                 patients die                          │
│ NEXT EXPLORE    CSF-068, IEC 62304, DO-178C             │
└─────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Software safety interlocks can be defeated by race conditions; hardware interlocks are independent.
2. "Tested" means tested in the conditions tested; timing-dependent bugs require concurrent stress testing.
3. Error messages in safety-critical systems must be specific, actionable, and prescribe the correct response.

**Interview one-liner:**
"The Therac-25 killed six patients via a race condition that bypassed the software safety interlock because hardware safety mechanisms had been removed; the lessons: hardware and software safety must be independent, fail-safe defaults are mandatory, and concurrent timing bugs require specific concurrent testing."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Safety mechanisms must be independent of the systems they
protect. A circuit breaker that's controlled by the same
software that controls the thing it protects isn't a
safety mechanism; it's part of the same failure domain.
Independence, not redundancy, is the safety principle.

**Where else this pattern appears:**

- **Kubernetes `PodDisruptionBudget`** — independent of deployment; protects availability even if deployment is broken
- **Database read replica** — independent of write path; available even if primary is degraded
- **Financial circuit breaker** — independent of trading system; trips even if main system is compromised

---

### 💡 The Surprising Truth

The Therac-25 software was also used in the Therac-6 and
Therac-20 — but those machines had hardware interlocks.
The Therac-25 race condition therefore existed in earlier
machines but never caused harm because hardware prevented the
that combination of states from firing the beam. When AECL
removed hardware interlocks in the Therac-25 to reduce cost,
they exposed a latent race condition that had been dormant
for years. This reveals a dangerous pattern: a latent
software bug that is harmless when protected by an independent
mechanism becomes catastrophic when that mechanism is removed.
The bug didn't change; the protection layer did.

---

### 🧠 Think About This Before We Continue

**Q1 (Root Cause):** The Therac-25 investigation found that
AECL's management stated the software was "tested" and
"therefore safe." What does this reveal about the limits
of functional testing for concurrent systems, and what
additional testing methods would have found the race condition?

_Hint:_ The race required specific timing. Functional tests
were run at human typing speed. The race manifested only
with fast, experienced operators. Research stress testing,
concurrency testing, and model checking for concurrent systems.

**Q2 (Scale):** The Boeing 737 MAX MCAS system (2018-2019)
caused 346 deaths. MCAS over-relied on a single angle-of-attack
sensor and had no independent hardware check. What are the
parallels to Therac-25, and what do they suggest about the
status of software safety engineering 30 years later?

_Hint:_ Research the MCAS accident reports. MCAS had a
single sensor input with no hardware redundancy. The Therac-25
had a single software path with no hardware interlock.
Are these the same design error?

**Q3 (Design Trade-off):** IEC 62304 and DO-178C require
independent safety review, formal testing, and specific
documentation for safety-critical software. These standards
add significant development time and cost. For a startup
building medical device software, how do you balance the
cost of compliance with the safety value?

_Hint:_ Consider: what is the cost of a single patient death
due to a software bug vs the cost of IEC 62304 compliance?
What are the legal, regulatory, and ethical implications?
