---
id: CSF-078
title: "Therac-25 Incident (1985)"
category: CS Fundamentals - Paradigms
tier: tier-1-foundations
folder: CSF-cs-fundamentals
difficulty: ★★☆
depends_on: CSF-072, CSF-073
used_by:
related: CSF-072, CSF-079, CSF-073, CSF-077
tags: [therac-25, software-safety, race-condition, safety-critical-systems, historical-case-study]
status: complete
version: 4
layout: default
parent: "CS Fundamentals - Paradigms"
grand_parent: "Technical Mastery"
nav_order: 78
permalink: /technical-mastery/csf/therac-25-incident-1985/
---

⚡ TL;DR - Therac-25 (1985-1987): a radiation therapy machine that gave
massive overdoses to at least 6 patients, killing 3. Root cause: a race
condition in the operator interface software. When the operator typed fast
enough (switching modes rapidly): the machine entered electron beam mode but
with X-ray power level (100x overdose). Contributing factors: hardware safety
interlocks REMOVED (software-only safety), cryptic error messages ("MALFUNCTION
54"), operators trained to ignore error messages, AECL denied bugs for months.
Lessons: hardware interlocks as independent safety layer, meaningful error
messages, race conditions in concurrent code, independent safety review.

| #078 | Category: CS Fundamentals - Paradigms | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | CSF-072 (Undefined Behaviour), CSF-073 (Memory Safety) | |
| **Used by:** | (referenced in safety-critical systems design, software ethics) | |
| **Related:** | CSF-072 (UB/Race Conditions), CSF-079 (Ariane 5), CSF-073 (Safety Bugs), CSF-077 (Correctness) | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**

Safety-critical software in 1985: the assumption was that software was reliable if it
worked "most of the time." The Therac-25 worked correctly in thousands of treatments.
The race condition: triggered only when the operator typed faster than ~8 characters
per second in a specific sequence (switch mode from X-ray to electron beam quickly).
Probability of triggering: low. But with enough patients: certainty.
The developers and AECL (Atomic Energy of Canada Limited) responded to patient injury
reports with "we cannot reproduce the error" and "the machine is safe." They trusted
their own testing (which never triggered the race condition) over patient injury reports.
The result: 6 overdoses over 2 years, before the race condition was identified and the
machines were recalled.

The Therac-25 incident CHANGED HOW THE SOFTWARE INDUSTRY THINKS ABOUT:
1. Race conditions in safety-critical systems
2. Hardware interlocks as independent safety layers (not optional)
3. Error message design (cryptic codes are dangerous)
4. Incident response (denying possible bugs delays fixes and kills people)
5. Software as a direct safety device (not just "it affects safety indirectly")

**EVOLUTION:**

Pre-Therac-25: software safety = "software that doesn't crash." If it runs without
exception: it's safe. Hardware safety mechanisms were considered redundant if software
was "working." AECL removed Therac-20's hardware safety interlocks from Therac-25 because
they trusted the software. Cost reduction. Simpler design.

Post-Therac-25: software safety = "software with provably correct behavior in all states,
including concurrent failure states." DO-178C (avionics), IEC 62304 (medical device software),
ISO 26262 (automotive): formal safety standards requiring analysis of failure modes,
independent verification, hardware-software co-design, separate safety monitors.
The Therac-25 incident is in the IEEE computer engineering curriculum, the ACM code of ethics
case studies, and every serious software safety textbook (Leveson, "Safeware"). It is the
canonical example of WHY software safety engineering is a distinct discipline.

---

### 📘 Textbook Definition

**Therac-25:** A radiation therapy machine manufactured by AECL (Atomic Energy of Canada Limited)
from 1983. Used for cancer treatment. Two modes: X-ray mode (photon beam, metal beam flattener in
place, low electron beam current -> filters to X-ray, high dose rate) and electron beam mode
(direct electron beam, no metal flattener, much lower dose rate). Catastrophic overdoses occurred
when the machine entered electron beam mode but with X-ray beam current: ~100x the intended dose.

**Race Condition (in this context):** A software bug where program behavior depends on the
relative timing or interleaving of events. In Therac-25: the race was between the operator
interface task (resetting a shared variable to the mode after editing) and the machine setup
task (reading the shared variable to configure hardware). If the operator typed fast enough:
both tasks operated on the shared variable simultaneously, with no synchronization.

**Hardware Safety Interlock:** A physical mechanism that enforces a safety constraint
INDEPENDENTLY of the software. Example: a physical beam flattener that CANNOT be absent
when X-ray beam current is selected (requires hardware to be in position). Even if the software
is buggy: hardware interlocks prevent dangerous configurations.

**Fail-Safe Design:** A design where, in the event of any failure (hardware, software,
operator error): the system defaults to a safe state (no beam), not a dangerous state
(beam at wrong parameters). Therac-25 failed unsafe: a race condition caused it to
enter the most dangerous state (high current, no flattener) rather than a safe state (no beam).

**MALFUNCTION 54:** The cryptic error message displayed by Therac-25 when a malfunction was
detected. No description. No actionable information. Operators were trained (based on experience
with previous machines that had many false-positive error messages) to dismiss error messages
and press "P" to proceed. This training turned a safety warning into a danger amplifier.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Therac-25: a radiation therapy machine where software race condition allowed X-ray power
in electron beam mode (100x overdose). Hardware safety interlocks had been removed ("software
handles it"). Cryptic error messages + trained operators to ignore them = 6 overdoses, 3 deaths.
Changed how the industry thinks about software safety.

**One analogy:**

> Imagine an elevator that can go very fast (for express mode) or very slow (for normal mode).
> The express mode requires special heavy brakes to stop safely. Normal mode uses light brakes.
> Previous elevator model: physical interlock - if you select express mode, the heavy brakes
> physically lock in. Cannot have express speed without heavy brakes physically.
> New elevator model (Therac-25 equivalent): software selects which brakes to engage.
> Cheaper! No mechanical interlock needed. Software is reliable, right?
>
> Race condition: operator presses "switch from normal to express" quickly.
> Software reads mode: still normal (race: hasn't updated yet).
> Software engages: light brakes (normal mode).
> Elevator: moves at express speed. Light brakes: insufficient. Crash.
>
> The physical interlock (hardware) would have PREVENTED this:
> you cannot physically have express speed AND light brakes simultaneously.
> The software interlock: could be in inconsistent state during the race.

**One insight:**

The Therac-25 has TWO root causes, not one. Most analyses focus on the race condition.
But the deeper cause: SINGLE POINT OF FAILURE in safety. The race condition was the
technical failure mode. The system design failure: relying on SOFTWARE ALONE for safety.
Every safety-critical system design principle says: safety must be LAYERED (defense in depth).
No single component - software, hardware, operator - should be the SOLE safety barrier.
Therac-25 removed the hardware safety layer (cost saving) and added a single software layer.
That single layer had a race condition. Result: no protection.
The lesson engineers should internalize: SAFETY IS A SYSTEM PROPERTY, not a software property.
No matter how good the software: it should not be the only safety mechanism.

---

### 🔩 First Principles Explanation

**THE RACE CONDITION MECHANICS:**

```
┌──────────────────────────────────────────────────────┐
│ THERAC-25 RACE CONDITION (simplified):               │
│                                                      │
│ Shared variable: mode_flag                          │
│   = 0: electron beam mode (low power, no flattener) │
│   = 1: X-ray mode (high power, with flattener)     │
│                                                      │
│ Two concurrent tasks:                                │
│ TASK A: Operator Interface (runs on operator input) │
│ TASK B: Machine Setup (runs on timer: configures hw)│
│                                                      │
│ NORMAL (SLOW OPERATOR):                              │
│ T=0ms:  Operator selects X-ray mode                 │
│ T=1ms:  Task A: mode_flag = 1 (X-ray)               │
│ T=5ms:  Task B: reads mode_flag = 1 (X-ray)         │
│         -> positions flattener, sets high current   │
│ T=6ms:  Operator changes to electron mode           │
│ T=7ms:  Task A: mode_flag = 0 (electron)            │
│ T=10ms: Task B: reads mode_flag = 0                 │
│         -> removes flattener, sets low current. OK. │
│                                                      │
│ RACE CONDITION (FAST OPERATOR):                      │
│ T=0ms:  Operator selects X-ray mode                 │
│ T=1ms:  Task A: mode_flag = 1 (X-ray)               │
│ T=2ms:  Task B starts: begins reading mode_flag...  │
│         (reads: mode_flag = 1, X-ray setup)         │
│ T=2.5ms: Operator quickly changes to electron       │
│           Task A: mode_flag = 0 (electron)          │
│ T=3ms:  Task B finishes setup:                      │
│         mode = 0 (electron): BEAM TYPE = electron   │
│         BUT: hardware already configured for X-ray! │
│         Current = HIGH (X-ray level)                │
│         Flattener = IN POSITION (or: X-ray beam     │
│                     current without flattener       │
│                     = 100x electron dose)           │
│ PATIENT: receives ~100x the intended dose.          │
└──────────────────────────────────────────────────────┘
```

**MISSING HARDWARE INTERLOCK:**

```
┌──────────────────────────────────────────────────────┐
│ THERAC-20 (predecessor): HARDWARE INTERLOCK          │
│                                                      │
│ Physical requirement: beam flattener must be in     │
│ position before X-ray beam current can be applied.  │
│ Implemented as: physical interlock switch on        │
│ the collimator. Cannot close the switch unless     │
│ flattener is physically in position.                │
│ RACE CONDITION EFFECT: ZERO.                        │
│ Even with wrong software: cannot have high current  │
│ without flattener physically in place.              │
│                                                      │
│ THERAC-25: REMOVED the hardware interlock.          │
│ Reason: "Software handles this. Interlock redundant."│
│ Cost: reduced manufacturing cost.                   │
│ Consequence: software race condition -> fatal dose. │
│                                                      │
│ THE LESSON: hardware interlocks are NOT redundant.  │
│ They are INDEPENDENT safety layers.                 │
│ Software and hardware can BOTH have bugs.           │
│ The bugs should be INDEPENDENT (different failure   │
│ modes) so both must fail simultaneously for an      │
│ accident. This is DEFENSE IN DEPTH for safety.     │
└──────────────────────────────────────────────────────┘
```

---

### 🧪 Thought Experiment

**IF THE ERROR MESSAGE HAD BEEN HELPFUL:**

MALFUNCTION 54 (actual Therac-25 message):
```
MALFUNCTION 54
TREATMENT PAUSE
```

No description. No actionable information. Operator: presses "P" (proceed). Beam fires.

**Alternative (meaningful error message):**
```
SAFETY INTERLOCK: Beam configuration inconsistent
  Beam type:    ELECTRON
  Beam current: X-RAY LEVEL (HIGH)
  Flattener:    NOT IN POSITION

MACHINE STOPPED. DO NOT PROCEED.
Call service engineer before next treatment.
Patient has NOT received treatment.
```

With this error message: the operator CANNOT assume it's a false positive.
The message says exactly what is wrong. The operator CANNOT proceed
(machine stopped, no "proceed" option) without a service engineer review.

**Why Therac-25 operators ignored MALFUNCTION errors:**
The previous Therac-20 machine had many false-positive hardware interlock alarms
(hardware interlocks would trigger when everything was fine). Operators learned:
alarms = false positives. Press "P" to proceed. This behavior was reinforced by
training and experience. The Therac-25 used the same philosophy (alarm codes, no
description, proceed option). The operators applied the same learned behavior.
The error message design TRAINED the operators to be dangerous.

**LESSON:** Error messages in safety-critical systems:
1. DESCRIBE the safety condition clearly (not a code)
2. Indicate the SEVERITY (informational vs critical vs do-not-proceed)
3. BLOCK dangerous actions for critical errors (no "proceed" option)
4. LOG with enough detail for post-incident analysis

---

### 🎯 Mental Model / Analogy

**THERAC-25 ROOT CAUSES (5 LEVELS):**

```
┌──────────────────────────────────────────────────────┐
│ ROOT CAUSE ANALYSIS (5-WHY):                        │
│                                                      │
│ SYMPTOM: Patient received 100x radiation dose.      │
│                                                      │
│ WHY 1: Machine applied X-ray beam current in        │
│         electron beam mode.                         │
│                                                      │
│ WHY 2: Race condition. Mode flag set to electron    │
│         while hardware configured for X-ray.        │
│                                                      │
│ WHY 3: No synchronization between operator          │
│         interface task and machine setup task.      │
│                                                      │
│ WHY 4: No hardware interlock to prevent X-ray       │
│         current without flattener position.         │
│         (Hardware interlock was removed.)           │
│                                                      │
│ WHY 5: System design: SINGLE LAYER OF SAFETY.       │
│         Software was the sole safety mechanism.     │
│         No independent verification layer.          │
│         No independent safety monitor.              │
│                                                      │
│ CONTRIBUTING FACTORS:                               │
│ - Cryptic error messages -> operators ignore alarms │
│ - AECL denial of bugs for months after incidents    │
│ - No independent safety review of software          │
│ - Concurrent software with no concurrency analysis  │
│ - Reuse of Therac-20 code without re-verifying     │
│   assumptions (operator speed assumptions changed)  │
└──────────────────────────────────────────────────────┘
```

**MEMORY HOOK:**

"Therac-25: 1985-1987. Radiation therapy machine. Race condition: electron mode + X-ray power = 100x overdose.
6 overdoses. 3 deaths. Root causes: (1) Race condition in mode switching (shared variable, no sync).
(2) Hardware safety interlocks REMOVED (software-only safety = single point of failure).
(3) Error message 'MALFUNCTION 54' (cryptic, no description, operators trained to ignore).
(4) AECL denied bugs for months (delayed remediation).
Lessons: defense in depth (hardware + software safety), meaningful error messages, race conditions in concurrent code, independent safety review, NEVER rely on software alone for safety.
In IEEE curriculum, ACM ethics case studies, every safety-critical software textbook."

---

### 📊 Gradual Depth - Five Levels

**Level 1 - Child:**
A machine that should give a small amount of medicine gave 100 times too much because the
computer had a timing mistake. People were hurt. The lesson: important machines should have
extra safety switches that work EVEN IF the computer has a bug.

**Level 2 - Student:**
Race condition in code:
```java
// Simplified: shared state, no synchronization (Therac-25 pattern)
class TherapyMachine {
    int mode = 0; // 0=electron, 1=xray
    int beamCurrent = LOW;

    // Task A: operator interface (called when operator changes mode)
    void setMode(int newMode) {
        this.mode = newMode; // race: another task reads mode simultaneously
    }

    // Task B: machine setup (called on timer, configures hardware)
    void configureHardware() {
        if (mode == ELECTRON) {
            beamCurrent = LOW; // safe for electron beam
            removeFlattener();
        } else if (mode == XRAY) {
            beamCurrent = HIGH;  // high current for X-ray
            installFlattener();  // MUST have flattener at high current
        }
        // BUG: if mode changes between the read and the configure:
        // could have HIGH current with no flattener installed.
    }
}
// Fix: synchronize the entire read-and-configure operation.
// Better: hardware interlock independent of software.
```

**Level 3 - Professional:**
Defense in depth applied to software safety:
```
THERAC-25 LESSON: SAFETY LAYERS

For any safety-critical system:

LAYER 1: Algorithm Correctness
  - Race condition analysis
  - Formal verification of safety-critical state machines
  - Code review by independent reviewers

LAYER 2: Software Safety Monitor
  - Independent software process that monitors hardware state
  - Not the same code path as control software
  - If inconsistency detected: HALT (fail-safe default)

LAYER 3: Hardware Safety Interlock
  - Physical mechanism independent of software
  - Prevents dangerous configurations regardless of software state
  - Example: physical beam current limiter tied to flattener position

LAYER 4: Operator Training
  - Understand error messages and their severity
  - Know when to STOP and call service (vs proceed)
  - Clear escalation path for anomalies

LAYER 5: Incident Reporting and Analysis
  - All incidents: reported, investigated, root-caused
  - Never: "cannot reproduce, probably false alarm"
  - AECL failure: dismissed patient injury reports for months

The Therac-25 had: inadequate LAYER 1 (race condition), no LAYER 2, no LAYER 3, weak LAYER 4.
```

**Level 4 - Senior Engineer:**
State machine with safety invariant and mutual exclusion:
```java
// CORRECT: Atomic state transition with hardware interlock check
class SafeTherapyMachine {
    // State machine with ATOMIC transitions.
    // Using ReentrantLock to prevent race condition between mode set and hw configure.
    private final ReentrantLock configLock = new ReentrantLock();
    private volatile TreatmentMode currentMode = ELECTRON;

    // Atomic: set mode AND configure hardware together (no race window).
    public TreatmentResult setModeAndArm(TreatmentMode newMode)
            throws SafetyException {
        configLock.lock();
        try {
            // Read hardware state (independent of software state):
            HardwareState hw = hardwareMonitor.readCurrentState();

            // SAFETY CHECK: verify hardware is consistent with requested mode.
            if (!isSafeConfiguration(newMode, hw)) {
                // FAIL SAFE: halt, do not proceed.
                emergencyHalt();
                throw new SafetyException(
                    "Unsafe configuration: mode=" + newMode +
                    " but hardware=" + hw +
                    ". Machine halted. Call service engineer.");
            }
            // Only if hardware is consistent: apply mode.
            this.currentMode = newMode;
            configureHardware(newMode); // atomic within lock
            return TreatmentResult.ARMED;
        } finally {
            configLock.unlock();
        }
    }

    private boolean isSafeConfiguration(TreatmentMode mode, HardwareState hw) {
        if (mode == XRAY && !hw.isFlattenerInPosition()) return false;
        if (mode == XRAY && hw.getBeamCurrent() != HIGH_CURRENT_LEVEL) return false;
        if (mode == ELECTRON && hw.getBeamCurrent() != LOW_CURRENT_LEVEL) return false;
        return true;
    }
    // Remaining: hardware safety interlock (independent, not in this code path).
}
```

**Level 5 - Expert:**
IEC 62304 and DO-178C: how industry responded to Therac-25:
```
IEC 62304 (Medical Device Software, 2006):
  - Software safety classification: A (no harm), B (reversible harm), C (serious harm or death)
  - Therac-25 would be: Class C (direct patient harm possible)
  - Class C requirements: software development plan, architecture design,
    unit testing, integration testing, system testing, risk management
    (IEC 14971 FMEA: Failure Mode and Effects Analysis)
  - Key: INDEPENDENT REVIEW at each stage. Not the developer reviewing their own code.

DO-178C (Avionics Software, 2011):
  - Levels A-E based on criticality (A = catastrophic failure possible)
  - Level A requirements: condition coverage in testing (all branch conditions),
    modified condition/decision coverage (MCDC), independence in testing
    (test designed by someone who didn't write the code)
  - All safety-critical code paths formally verified

BOTH STANDARDS: require what Therac-25 lacked:
1. FMEA (Failure Mode and Effects Analysis): explicitly analyze what happens when
   software has a bug in each component. Design to detect+handle all failure modes.
2. Independent safety review: the developers cannot self-certify safety.
3. Concurrency analysis: all shared variables must be explicitly analyzed for race conditions.
4. Fail-safe default: any unhandled state -> safe state (no beam), not dangerous state.
5. Error message standards: actionable messages with severity. No "MALFUNCTION NN."
```

---

### ⚙️ How It Works

**THE INCIDENT TIMELINE:**

```
┌──────────────────────────────────────────────────────┐
│ THERAC-25 INCIDENT TIMELINE:                        │
│                                                      │
│ Jun 1985: First known overdose (Marietta, GA).      │
│   Operator: "I set it to electron, got an error,   │
│   pressed proceed, beam fired, patient screamed."  │
│   AECL response: "Cannot reproduce. Machine safe." │
│                                                      │
│ Jul 1985: Second overdose (same hospital).          │
│   AECL: "Probably operator error. No bug found."   │
│                                                      │
│ Mar 1986: Third overdose (Yakima, WA). Patient dies.│
│   AECL: Conducted investigation. Still no bug found.│
│   (Testing did not reproduce the race condition.)  │
│                                                      │
│ Apr 1986: Fourth overdose (Tyler, TX).              │
│                                                      │
│ Jan 1987: Fifth and sixth overdoses.                │
│   Physicist at Tyler, TX: notices correlation.     │
│   Fast operator entry -> MALFUNCTION -> proceed    │
│   -> overdose. Documents the pattern.              │
│                                                      │
│ Mar 1987: AECL finally identifies race condition.   │
│   All Therac-25 machines: recalled/suspended.      │
│                                                      │
│ 2 YEARS of overdoses before the race condition was  │
│ identified and remediated.                          │
│                                                      │
│ KEY FACTOR IN DELAY: AECL's refusal to accept       │
│ that a software bug existed despite patient injury  │
│ reports. "Cannot reproduce" ≠ "no bug."            │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: Race Condition in Mode Setting**

```java
// BAD: Therac-25 pattern - shared variable, no synchronization
class TreatmentSetup {
    // SHARED VARIABLE: accessed by both operator interface and timer task
    int mode = ELECTRON_BEAM; // 0=electron, 1=x-ray

    // Called by operator interface thread (user input driven)
    void operatorSetMode(int newMode) {
        this.mode = newMode;
        // No lock. Timer task can read mode simultaneously.
    }

    // Called by timer task thread (periodic hardware configuration)
    void applyMachineSettings() {
        // RACE: if operatorSetMode runs between these two operations:
        int currentMode = this.mode; // reads mode (may be inconsistent)
        // -- operator changes mode here --
        configureBeamCurrent(currentMode); // configures based on stale read
        // configureBeamCurrent(ELECTRON) but hardware might be set to XRAY
        // (if another timer call already set currentMode=XRAY and configured)
    }
}

// GOOD: Atomic mode change with hardware verification
import java.util.concurrent.locks.ReentrantLock;

class SafeTreatmentSetup {
    private final ReentrantLock modeLock = new ReentrantLock();
    private volatile TreatmentMode mode = TreatmentMode.ELECTRON;

    // Operator changes mode: acquires lock, verifies hardware, applies.
    boolean operatorSetMode(TreatmentMode newMode) {
        modeLock.lock();
        try {
            // Read hardware state first (cannot be faked by software race)
            PhysicalState hw = physicalStateReader.readHardware();
            if (!validateSafeTransition(this.mode, newMode, hw)) {
                // FAIL SAFE: reject the mode change if hardware is inconsistent.
                // Do NOT proceed. Require operator to confirm hardware state.
                return false; // mode not changed
            }
            this.mode = newMode;
            return true;
        } finally {
            modeLock.unlock();
        }
    }

    // Timer task: ALSO acquires lock before reading and applying mode.
    void applyMachineSettings() {
        modeLock.lock();
        try {
            // Within the same lock: mode and hardware configuration are atomic.
            // No race possible: only one task in this critical section at a time.
            TreatmentMode currentMode = this.mode;
            PhysicalState hw = physicalStateReader.readHardware();
            if (!validateSafeConfiguration(currentMode, hw)) {
                emergencyStop(); // FAIL SAFE: inconsistent state = halt
                return;
            }
            configureBeamCurrent(currentMode);
        } finally {
            modeLock.unlock();
        }
    }
}
```

**Example 2 - Meaningful Error Messages vs Cryptic Codes**

```java
// BAD: Therac-25 style error message (cryptic, no action guidance)
enum MachineError {
    MALFUNCTION_17, MALFUNCTION_54, MALFUNCTION_9
}
void handleError(MachineError error) {
    display("MALFUNCTION " + error.ordinal() + "\nTREATMENT PAUSE");
    // Operator: no idea what's wrong. Training: press P to proceed.
    // No severity indication. No recommended action. No block on proceed.
}

// GOOD: Safety-critical error message standard
record SafetyError(
    String code,
    String humanDescription,
    SafetyLevel level,    // INFO, WARNING, CRITICAL, FATAL
    String recommendedAction,
    boolean allowProceed  // false for CRITICAL/FATAL
) {}

void handleError(SafetyError error) {
    displayMessage(
        "[" + error.level() + "] " + error.code() + "\n" +
        error.humanDescription() + "\n\n" +
        "Recommended action: " + error.recommendedAction()
    );

    if (!error.allowProceed()) {
        disableProceedButton(); // physically block proceeding
        logIncident(error, patientId, timestamp, operatorId);
        // Cannot dismiss without service engineer override.
    }
}

// Example usage:
var error = new SafetyError(
    "BEAM-MODE-INCONSISTENT",
    "Beam type is ELECTRON but beam current is at X-RAY level. " +
    "This configuration is unsafe and cannot deliver treatment.",
    FATAL,
    "Stop treatment. Do NOT press Proceed. " +
    "Contact service engineer before treating any patient.",
    false // cannot proceed
);
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "The Therac-25 was caused by incompetent software engineers" | The Therac-25 software was written by skilled engineers. The race condition was subtle: it only triggered at specific operator speeds (>8 chars/sec in a specific sequence). The race condition required a specific timing window in a multi-tasking system without a real-time OS scheduler. Many capable engineers reviewed the software and found no bug. The CAUSATION: (1) lack of concurrency analysis tooling (1985: race condition detection tools were academic), (2) lack of a formal concurrent code review process, (3) overconfidence in "software that works most of the time." The lesson is NOT "use better engineers." The lesson is "use better PROCESSES": require formal concurrency analysis for safety-critical concurrent code, require independent safety review, and DO NOT remove hardware safety interlocks regardless of software confidence. |
| "Modern software development practices would have prevented this" | Modern practices HELP but are not sufficient. (1) Race condition: would be caught by ThreadSanitizer (TSan) if the exact timing was triggered in testing. But the race window required a specific operator speed - standard automated tests would likely use programmatic input (not human-speed input). TSan would catch it IF the race-triggering scenario was in the test suite. (2) Hardware interlock removal: this is a DESIGN DECISION, not a software bug. Modern requirements engineering would flag "removing a hardware safety interlock" as a high-risk design change requiring safety analysis. (3) Error message quality: still poor in many modern systems. (4) Denial of bugs: still happens (Toyota's initial denial of unintended acceleration software bugs in 2009-2010 is a modern parallel). The practices help: testing, code review, static analysis. But the FUNDAMENTAL lessons (hardware interlocks are not redundant, error messages must be actionable, bugs reported by affected parties must be taken seriously) are process and culture issues that modern tooling doesn't automatically solve. |
| "This could only happen in medical devices, not in regular software" | The race condition pattern (shared mutable state accessed by multiple threads without synchronization) appears in EVERY concurrent software system. The Therac-25 race condition in Java would be a textbook Java Memory Model violation (non-volatile, non-synchronized shared variable). In 2024: race conditions are still common in production software. The difference: in most software, the consequence is incorrect display (benign) or data corruption (serious but not lethal). In the Therac-25: incorrect beam delivery (lethal). The race condition TYPE is identical. The CONSEQUENCE depends on the domain. Every Java service with a HashMap accessed by multiple threads (not a ConcurrentHashMap) has a Therac-25-like race condition. It just hasn't caused visible harm yet. Toyota's unintended acceleration lawsuit (2013): expert witnesses found race conditions and stack overflow vulnerabilities in Toyota's engine control software. Not a 1985 medical device: a 2009-2010 automotive system. Race conditions kill in any safety-critical domain. |
| "If AECL had better bug tracking, they would have fixed it faster" | The problem wasn't bug tracking. The problem was AECL's institutional response: they didn't BELIEVE there was a software bug. Six patient injury reports, "cannot reproduce" response each time. This is a CULTURE problem: the engineers were confident their software was safe (it had been tested extensively). When a test doesn't reproduce the bug: it's easy to conclude "no bug, operator error, patient psychological reaction." The Therac-25 case established a principle now in software safety standards: in safety-critical systems, INJURY REPORTS ARE BUG REPORTS, even if the bug cannot be immediately reproduced. FDA guidance now requires medical device manufacturers to have adverse event reporting processes and investigation procedures. Any patient injury associated with a device: investigated as a potential device malfunction, not assumed to be user error. This is a regulatory and cultural requirement, not a technical one. Technology alone cannot fix institutional denial. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Race Condition in Safety-Critical State Machine**

**Symptom:** System behavior is correct in all normal testing but produces dangerous output
under specific timing conditions (high-speed input, specific interleaving).

**Diagnosis framework:**
```
CONCURRENCY ANALYSIS CHECKLIST for safety-critical software:

1. IDENTIFY ALL SHARED STATE:
   List every variable, buffer, or data structure accessed
   by more than one task/thread/interrupt handler.

2. IDENTIFY ALL ACCESSES:
   For each shared variable: list all reads and writes.
   Who reads? Who writes? What is the task/priority?

3. IDENTIFY ALL UNSAFE WINDOWS:
   For each pair (read, write) to the same shared variable:
   Is there a time window where the read sees inconsistent state?
   Example: read in Task B, write in Task A.
   Can Task A write BETWEEN two reads in Task B? -> race.

4. VERIFY ATOMICITY:
   Every compound operation (read-modify-write, check-then-act,
   configure-hardware-based-on-mode): must be ATOMIC.
   If not atomic in the hardware model: add synchronization.

5. VERIFY FAIL-SAFE DEFAULT:
   For every UNHANDLED state/error: does the system default
   to a safe state (no beam) or dangerous state (wrong beam)?
   MUST default to safe state.

TOOLS (modern):
- ThreadSanitizer (-fsanitize=thread for C/C++, runtime for Java)
- Java race detector: DRD (Valgrind-based), or -Xss flags in Java VMs
- Formal concurrency verification: SPIN model checker, TLA+
- Code review checklist: every shared variable reviewed for synchronization
```

---

**Security Note:**

The Therac-25 lessons directly apply to SECURITY-CRITICAL software:

1. RACE CONDITION as SECURITY VULNERABILITY (TOCTOU: Time-of-Check Time-of-Use):
   ```c
   // Same race condition pattern, security context:
   if (access("/tmp/file", W_OK) == 0) { // CHECK
       // Attacker replaces /tmp/file with symlink to /etc/passwd HERE
       open("/tmp/file", O_WRONLY);       // USE (opens /etc/passwd)
   }
   // Fix: use O_NOFOLLOW flag, or avoid the check-then-act pattern entirely.
   ```
   The Therac-25 race: CHECK mode, then USE mode to configure hardware.
   TOCTOU race: CHECK file permissions, then USE file for I/O.
   Same pattern. Different domain. Both fatal if in the wrong context.
2. ERROR MESSAGE INFORMATION DISCLOSURE: Security-critical error messages
   should NOT reveal implementation details (stack traces, internal paths, SQL errors).
   But they ALSO should not be so cryptic that security events are silently ignored
   (like MALFUNCTION 54). Balanced design: log all details internally, show minimal
   information to the user, alert security team for critical security events.
3. DEFENSE IN DEPTH: no single software control should be the sole security boundary.
   Same principle as hardware interlocks. Authentication + authorization + rate limiting
   + WAF + network segmentation = multiple independent layers. Each layer can have bugs.
   Only all layers simultaneously: an incident.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Undefined Behaviour in Language Specs` (CSF-072) - race conditions as UB
- `Memory Safety Vulnerabilities` (CSF-073) - software bugs with physical-world consequences

**Builds On This (learn these next):**
- `Ariane 5 Overflow Bug (1996)` (CSF-079) - another landmark software safety incident
- `Software Correctness and Proof` (CSF-077) - formal correctness to prevent incidents like this

---

### 📌 Quick Reference Card

```
┌────────────────────────────────────────────────────────┐
│ WHAT       │ Radiation therapy machine, 1985-1987.     │
│            │ Software race condition -> 100x overdose. │
│            │ 6 overdoses. 3 deaths.                   │
├────────────┼─────────────────────────────────────────┤
│ ROOT CAUSE │ Race condition in mode switch (shared var │
│            │ between operator task and machine task).  │
│            │ No synchronization. No hw interlock.     │
├────────────┼─────────────────────────────────────────┤
│ REMOVED    │ Hardware safety interlock from Therac-20 │
│ INTERLOCK  │ removed in Therac-25. "Software handles." │
│            │ Single point of failure.                 │
├────────────┼─────────────────────────────────────────┤
│ ERROR MSG  │ "MALFUNCTION 54" - cryptic, no description│
│            │ Operators trained to ignore. Danger amplified.│
├────────────┼─────────────────────────────────────────┤
│ AECL DELAY │ 2 years of overdoses before bug found.  │
│            │ "Cannot reproduce" = "no bug" = WRONG.  │
├────────────┼─────────────────────────────────────────┤
│ LESSONS    │ Defense in depth (hw + sw safety).      │
│            │ Meaningful error messages + block proceed│
│            │ Concurrency analysis for safety code.   │
│            │ Injury reports ARE bug reports.         │
├────────────┼─────────────────────────────────────────┤
│ STANDARDS  │ IEC 62304 (medical), DO-178C (avionics) │
│            │ IEEE curriculum, ACM ethics case study  │
├────────────┼─────────────────────────────────────────┤
│ NEXT       │ CSF-079 (Ariane 5), CSF-077 (Correctness)│
└────────────┴─────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. The Therac-25 race condition: a shared mode variable was written by the operator interface
   task and read by the machine setup task, with no synchronization. When the operator typed
   fast enough: the machine setup task read the mode (electron beam) but the hardware was
   still configured for X-ray power. Result: electron beam mode with X-ray current = ~100x
   dose. The same race condition pattern (shared mutable state, concurrent access, no
   synchronization) is a textbook concurrency bug. In Java: a non-volatile, non-synchronized
   field accessed by multiple threads. The Therac-25's distinction: the consequence was lethal,
   not just a wrong count in a UI. The bug TYPE is universal.
2. Hardware safety interlocks are NOT redundant. Therac-25 removed the hardware interlock
   (from Therac-20) that physically prevented high beam current without the flattener in position.
   The justification: "software handles it." The result: when software had a race condition,
   nothing prevented the dangerous configuration. Defense in depth: software AND hardware
   safety layers. EACH layer can fail. BOTH must fail simultaneously for a catastrophic outcome.
   This principle applies to all safety-critical and security-critical systems: no single
   control should be the sole safety mechanism. Authentication + authorization + rate limiting.
   Not authentication alone.
3. Error messages in safety-critical systems must be ACTIONABLE and must BLOCK dangerous
   actions for critical errors. "MALFUNCTION 54" trained operators to ignore alarms. A well-designed
   error message would have: described the safety condition (beam inconsistency), indicated
   severity (FATAL), stated the recommended action (stop, call service engineer), and PREVENTED
   the operator from proceeding (disabled the proceed button). This design principle extends to
   all software: error messages should tell the user WHAT is wrong, HOW SERIOUS it is, and WHAT TO DO.
   The Therac-25's error messages were a failure of UX design with lethal consequences.

**Interview one-liner:**
"Therac-25 (1985-87): radiation therapy machine. Race condition: operator mode switch + fast input = electron mode with X-ray power = 100x dose. 6 overdoses, 3 deaths.
Root causes: (1) race condition (shared variable, no synchronization), (2) hardware safety interlocks removed (software-only safety = single point of failure), (3) cryptic error 'MALFUNCTION 54' trained operators to ignore alarms, (4) AECL denied bugs 2 years.
Lessons: defense in depth (hw+sw), meaningful error messages that block dangerous actions, concurrency analysis for safety-critical code, injury reports = bug reports. IEC 62304, DO-178C standards require these practices today."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
IN SAFETY-CRITICAL SYSTEMS, FAIL SAFE BY DEFAULT.
Therac-25 failed UNSAFE: the race condition caused it to enter the most dangerous state.
The correct design principle: any unexpected, unhandled, or error state -> SAFE STATE.
In Therac-25: any mode inconsistency -> NO BEAM (safe state). Not: proceed with inconsistent configuration.
This principle generalizes: authentication failure -> DENY (not allow). Unknown network packet
-> DROP (not forward). DB write failure -> ROLLBACK (not partial commit). Unrecognized user input
-> REJECT (not process). The default should ALWAYS be the safe action. Exceptions to safety
should be explicitly permitted, not accidentally caused by failure.

**Where else this pattern appears:**

- **Toyota unintended acceleration (2009-2010): modern Therac-25 parallel** - Toyota faced lawsuits
  alleging that software bugs in the engine control unit (ECU) caused unintended acceleration.
  2013 NASA/embedded systems expert Michael Barr testified: he found race conditions in Toyota's
  ECU software (Barr Group, Expert Witness). The software: 11,000 global variables (massive shared
  state). Race conditions between interrupt service routines and main loop. No watchdog timer
  to detect software hang states. Stack overflow possible (recursive calls, no stack guard).
  Toyota's initial response: "cannot be a software problem, driver error." The Therac-25 response
  exact parallel. Barr's findings: similar race condition patterns to Therac-25, 24 years later.
  Toyota eventually settled for $1.1 billion. The engineering lesson: automotive ECU software in
  2009 had Therac-25-class safety issues. Race conditions + global mutable state + lack of formal
  concurrency analysis = unsafe software regardless of decade. IEC 62304 was finalized 2006.
  ISO 26262 (automotive functional safety) was published 2011 - after the Toyota incidents.
  Standards lag incidents; incidents drive standards. Learn from Therac-25 before the incident.
- **The WHO medication error model and software safety** - The World Health Organization's
  "Swiss Cheese Model" of accident causation (James Reason, 1990): accidents occur when holes in
  multiple defensive layers align simultaneously. Each layer: a barrier to accidents. No single layer
  is perfect (has holes). Normally: one layer blocks the hazard even if another has a hole. Accident:
  all holes align (rare but possible). Therac-25 as Swiss Cheese Model: Layer 1 (software correctness)
  had a hole (race condition). Layer 2 (hardware interlock) was REMOVED - the layer was eliminated,
  not just holey. Layer 3 (error message design) had a hole (operators ignored alarms). Layer 4
  (incident response) had a hole (AECL denial). All layers simultaneously: 6 overdoses. This model
  is directly applicable to software system design. Defense in depth: multiple layers, each imperfect.
  The question is not "is this layer perfect?" (nothing is) but "are there enough independent layers
  that all failing simultaneously is sufficiently unlikely?" Removing a layer (as AECL did with the
  hardware interlock) increases the probability of all remaining layers simultaneously failing.
  Swiss Cheese Model thinking: design multiple independent layers, never remove a layer, never rely
  on any single layer for safety.

---

### 💡 The Surprising Truth

The Therac-25 software was REUSED from the Therac-20 (the previous model). The Therac-20
had hardware safety interlocks that prevented the dangerous configuration. The race condition
ALSO EXISTED in the Therac-20 software - it was just NEVER DANGEROUS because the hardware
interlock prevented the unsafe state regardless of the software bug. The race condition was
latent in the software for years, through the Therac-20 era, without causing harm because
the hardware protected against it. When the Therac-25 removed the hardware interlocks:
the pre-existing race condition in the reused software became lethal. This is the deepest
irony: the Therac-25 did not introduce a new software bug. It introduced a new ASSUMPTION
(software handles safety alone) that made a pre-existing latent bug lethal. The lesson:
when you CHANGE ASSUMPTIONS about safety layers, you must re-verify the entire system under
the new assumptions. The Therac-20 code had been validated under the assumption of hardware
interlocks. Removing the interlocks changed the threat model. The software was not re-verified
under the new assumption. This is the code reuse danger: the original code worked in its
original context. The new context changed the safety assumptions. The code was not re-evaluated
for correctness under the new context. EVERY TIME you reuse code in a new context: verify that
the original code's assumptions still hold in the new context. The Ariane 5 (CSF-079) made
the same mistake, one decade later.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **[RACE CONDITION]** Explain the exact Therac-25 race condition in technical terms: what shared
   variable, which tasks accessed it, what is the unsafe window, and what hardware state results
   from the race. Describe the fix (synchronization approach).

2. **[ROOT CAUSE]** The Therac-25 race condition was the PROXIMATE cause. Name the SYSTEMIC causes
   (at the design and process level). Which would have been sufficient to prevent the incident
   if addressed alone?

3. **[ERROR DESIGN]** Write the Therac-25 error message the way it SHOULD have been designed.
   What are the minimum fields a safety-critical error message must contain? What behavior should
   the system enforce when a CRITICAL safety error is detected?

4. **[SAFETY ARCHITECTURE]** Apply the Therac-25 lessons to a modern IoT medical device:
   an insulin pump controlled by a smartphone app. Identify 3 hardware safety interlocks
   and 3 software safety controls you would design. What is the fail-safe state?

5. **[STANDARDS]** What does IEC 62304 require for medical device software that would have
   caught the Therac-25 issues? Specifically: concurrency analysis, error message standards,
   and incident reporting.

---

### 🧠 Think About This Before We Continue

**Q1.** The Therac-25 race condition was only triggered at specific operator speeds
(fast typist). How should testing for safety-critical concurrent systems address
timing-dependent bugs that rarely appear in normal use?

*Hint: TIMING-DEPENDENT BUGS (race conditions) are among the hardest to find by testing alone.

TRADITIONAL TESTING LIMITATIONS for race conditions:
Standard test suite: calls functions in sequence. No real concurrency.
Integration tests: real concurrency but: (1) deterministic input timing (not human-speed
variability), (2) test runs are fast (race window may be microseconds in a context requiring
human-speed input), (3) race conditions need specific interleaving to trigger (testing doesn't
control scheduling).

MODERN APPROACHES:

1. RACE DETECTORS (instrumented runtime):
   ThreadSanitizer (-fsanitize=thread for C/C++, Java race detector):
   Instruments memory accesses. Reports: "thread A read X while thread B wrote X
   without synchronization." Does not require the race to produce wrong output:
   reports the POTENTIAL race. Requires: exercising the code paths in testing.
   Therac-25 race would be detected if: test exercised both tasks concurrently.

2. STRESS TESTING WITH TIMING VARIATIONS:
   Run tests with varying thread priorities, sleep injections, and multiple CPU cores.
   Increase the probability that the race window is hit.
   Tools: "chaos engineering for threading" - inject artificial delays at specific points
   to force interleaving. RaceFuzzer (Microsoft Research): fuzzing for race conditions.

3. FORMAL CONCURRENCY ANALYSIS (model checking):
   TLA+ or SPIN: model the concurrent tasks and verify properties for all interleavings.
   No need to "trigger" the race: the model checker explores all possible interleavings.
   This would have DEFINITELY found the Therac-25 race in a TLA+/SPIN model.

4. CODE REVIEW: CONCURRENCY CHECKLIST:
   Review every shared variable: who reads, who writes, is it synchronized?
   This is a manual process but catches races that tools miss (subtle semantic races).

LESSON: For safety-critical concurrent systems, ALL FOUR approaches should be used:
runtime detection, stress testing, formal analysis, and manual review.
The Therac-25 would have been caught by any of the last three.
None of these techniques were standard practice in 1985. All are available today.*

---

### 🎯 Interview Deep-Dive

**Q1: "What was the Therac-25 incident and what are its lessons for software engineers?"**

*Why they ask:* Tests safety awareness and ability to learn from historical incidents.
Common for safety-critical domain roles (medical, automotive, avionics) and senior engineering.

*Strong answer includes:*
- Therac-25: radiation therapy machine, 1985-87. Software race condition caused X-ray power in electron beam mode = ~100x dose. 6 overdoses, 3 deaths.
- Technical root cause: shared mode variable, two concurrent tasks, no synchronization. Fast operator input triggered the race window.
- Systems root cause: hardware safety interlocks removed (Therac-20 had them). Software was the sole safety mechanism. Single point of failure.
- Error message design: "MALFUNCTION 54" - cryptic, no description, trained operators to ignore.
- AECL response: denied bugs for 2 years. "Cannot reproduce" treated as "no bug."
- Lessons: defense in depth (hw+sw), meaningful error messages with actionable guidance, fail-safe defaults, concurrency analysis for safety-critical code, injury reports = bug reports, independent safety review.
- Modern standards response: IEC 62304 (medical), DO-178C (avionics) require formal safety analysis, concurrency analysis, independent review.

**Q2: "How would you design a concurrent system to prevent Therac-25-style race conditions?"**

*Why they ask:* Tests practical concurrency knowledge and safety design. Expected for senior Java/systems engineers.

*Strong answer includes:*
- Identify all shared state: every variable accessed by multiple threads.
- Synchronize compound operations: mode read + hardware configuration must be atomic (ReentrantLock or synchronized).
- Fail-safe default: if any validation fails: halt (no beam), not proceed.
- Independent hardware safety check: read hardware state independently of software state. Verify they are consistent before proceeding.
- ThreadSanitizer in CI: detect races in testing.
- Formal analysis: TLA+ or SPIN model of the concurrent state machine to verify safety properties for all interleavings.
- Error messages: describe the problem, indicate severity, block dangerous actions for critical errors.
- Defense in depth: software safety + hardware interlock (independent failure modes).
