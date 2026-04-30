---
layout: default
title: "Survivor Space"
parent: "Java & JVM Internals"
nav_order: 20
permalink: /java/survivor-space/
number: "020"
category: JVM Internals
difficulty: ★★☆
depends_on: JVM, Young Generation, Eden Space, GC Roots, Minor GC
used_by: GC, Minor GC, Object Aging, Object Promotion, Young Generation
tags: #java, #jvm, #memory, #gc, #internals, #intermediate
---

# 020 — Survivor Space

`#java` `#jvm` `#memory` `#gc` `#internals` `#intermediate`

⚡ TL;DR — The two equal Young Generation regions (S0 and S1) that act as a temporary aging buffer between Eden and Old Generation — objects bounce between them, gaining age on each Minor GC until promoted.

| #020 | Category: JVM Internals | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | JVM, Young Generation, Eden Space, GC Roots, Minor GC | |
| **Used by:** | GC, Minor GC, Object Aging, Object Promotion, Young Generation | |

---

### 📘 Textbook Definition

Survivor Spaces are **two equal-sized regions (S0 and S1) within the Young Generation** that serve as a staging area between Eden and Old Generation. At any time, one Survivor space is "From" (holds current survivors) and one is "To" (empty, ready to receive). During Minor GC, live objects from Eden and the From space are copied to the To space with incremented age. Objects exceeding the tenuring threshold are promoted to Old Generation. The roles of S0 and S1 swap after each GC.

---

### 🟢 Simple Definition (Easy)

Survivor spaces are the Young Generation's **waiting room** — objects that survived one GC move here, get older each cycle, and eventually either get promoted to Old Gen or die before reaching the threshold.

---

### 🔵 Simple Definition (Elaborated)

Not all objects in Eden die at the first Minor GC — some are still referenced and must survive. But they're not proven long-lived enough for Old Generation yet. Survivor spaces hold this middle category — objects that passed one GC but haven't earned permanent residency. The two-space design (always one empty) enables the copy-collect algorithm: copy live objects into the empty space, then discard the source entirely. Each copy increments the object's age counter until it crosses the promotion threshold.

---

### 🔩 First Principles Explanation

**The problem — what to do with Eden survivors:**

```
After Eden collection:
  Dead objects → reclaimed (easy, bulk wipe)
  Live objects → must go somewhere

Options:
  A) Promote all Eden survivors to Old Gen immediately
     Problem: Old Gen fills fast with short-lived objects
     → Old Gen = mix of truly long-lived + accidental survivors
     → Major GC triggered frequently
     → Most expensive GC type runs too often

  B) Keep survivors in Eden
     Problem: Eden can't be bulk-wiped if it has live objects
     → Must individually identify and preserve survivors
     → Loses the key Eden performance property

  C) Copy survivors to a separate staging area
     → Eden can still be bulk-wiped ✅
     → Survivors given another chance to die ✅
     → Only truly long-lived objects reach Old Gen ✅
     This is Survivor Space
```

**Why TWO spaces (not one):**

```
Copy-collect algorithm requires:
  Source region (has objects to collect)
  Destination region (empty, receives survivors)

If only one Survivor space:
  Can't copy "from Survivor" and "to Survivor" simultaneously
  (would overwrite objects being read)

With two Survivor spaces:
  S0 = From (current survivors, being collected)
  S1 = To   (empty, receiving new survivors)
  After GC: S0 wiped, roles swap
  → S1 = From (just filled), S0 = To (empty)
  Perfect ping-pong
```

---

### ❓ Why Does This Exist — Why Before What

**Without Survivor Spaces:**

```
Without staging area between Eden and Old Gen:
  Every Eden survivor promoted immediately

  Real-world impact:
    Request comes in → creates 500 objects
    499 die in Eden → collected cheaply ✅
    1 survives Minor GC (still referenced)
    → Promoted to Old Gen immediately
    Next GC cycle: that object also dies
    → Now OLD GEN has garbage
    → Requires Major GC to collect it
    → Major GC: 10-100× more expensive than Minor GC

  At 10,000 req/sec × 1 premature promotion each:
    10,000 objects/sec promoted to Old Gen
    Most die within 1-2 GC cycles
    Old Gen fills with short-lived garbage
    Major GC every few seconds
    Multi-second stop-the-world pauses
    → System unusable
```

**With Survivor Spaces:**
```
→ Objects get multiple chances to die in Young Gen
→ Only truly long-lived objects reach Old Gen
→ Old Gen stays clean, fills slowly
→ Major GC rare (minutes/hours not seconds)
→ System latency stable and predictable
```

---

### 🧠 Mental Model / Analogy

> Think of Survivor spaces as a **two-stage job interview process** at a company:
>
> **Eden** = Application inbox. Most applicants (objects) screened out immediately.
>
> **Survivor S0/S1** = Interview rounds. Survivors bounce between Round 1 (S0) and Round 2 (S1) on each GC cycle. Each round = +1 year of "experience" (age counter). Most candidates eventually drop out (die) during interview rounds.
>
> **Old Generation** = Permanent staff. Only candidates who completed ALL interview rounds (age ≥ threshold) get permanent positions.
>
> The ping-pong between S0 and S1 is the interviewing process — the two rooms ensure you can always evaluate from one room into the other cleanly.

---

### ⚙️ How It Works — The Ping-Pong Cycle

| #020 | Category: JVM Internals | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | JVM, Young Generation, Eden Space, GC Roots, Minor GC | |
| **Used by:** | GC, Minor GC, Object Aging, Object Promotion, Young Generation | |

**Object age tracking in Mark Word:**

```
Object Header Mark Word contains 4 bits for GC age
  → Maximum representable age: 15 (2^4 - 1)
  → Default tenuring threshold: 15

Each Minor GC: age++
Age >= threshold → promote to Old Gen

JVM can dynamically adjust threshold:
  If Survivor space > 50% full after GC:
    threshold-- (promote faster)
  If Survivor space < 25% full after GC:
    threshold++ (keep longer, up to MaxTenuringThreshold)
```

---

### 🔄 How It Connects

```
Minor GC triggered (Eden full)
      ↓
GC traces from roots
      ↓
Live objects in Eden → copy to Survivor (To)
Live objects in From → copy to Survivor (To)
      ↓
Age check on each copied object:
  age < threshold → increment age, stay in Survivor
  age >= threshold → promote to Old Generation
      ↓
Eden wiped (bulk reset)
From space wiped (bulk reset)
      ↓
S0/S1 roles swapped
      ↓
New From = just-filled Survivor
New To   = empty, ready for next GC
```

---

### 💻 Code Example

**Observing Survivor space and tenuring:**
```bash
# Print tenuring distribution after each Minor GC
java -XX:+PrintTenuringDistribution \
     -XX:+PrintGCDetails \
     -Xmx512m \
     MyApp
```

```
# Output:
Desired survivor size 5570560 bytes,
  new threshold 7 (max 15)
- age   1:   4521304 bytes,   4521304 total
- age   2:    892408 bytes,   5413712 total
- age   3:    156832 bytes,   5570544 total

# Interpretation:
# threshold = 7 (dynamic — adjusted by JVM)
# age 1: 4.5MB of objects that just survived Eden
# age 2: 892KB that survived 2 GCs
# age 3: 156KB that survived 3 GCs
# Exponential drop-off = healthy (most die young)
```

**Tuning Survivor space and tenuring threshold:**
```bash
# Default SurvivorRatio = 8
# Means: Eden:S0:S1 = 8:1:1
# For 100MB Young Gen:
#   Eden = ~80MB, S0 = ~10MB, S1 = ~10MB

# Reduce SurvivorRatio for larger Survivor spaces:
java -XX:SurvivorRatio=4 MyApp
# Eden:S0:S1 = 4:1:1 → S0=S1=20% of Young Gen each

# Force promotion threshold:
java -XX:MaxTenuringThreshold=5 MyApp
# Objects promoted after 5 GC cycles max
# Useful when you know objects are medium-lived

# Disable aging (promote after 1 GC):
java -XX:MaxTenuringThreshold=1 MyApp
# Extreme: promotes immediately after surviving Eden
# Use only if most survivors ARE long-lived
```

**Detecting Survivor space overflow:**
```bash
jstat -gcnew <pid> 1000
# S0C  S1C   S0U    S1U   TT MTT
# 512  512   0.0  512.0    1  15
#
# S1U = 512 = S1C (completely full!)
# TT = 1 (threshold dropped to 1 — overflow handling)
# Objects being promoted at age 1 → premature promotion
# Old Gen will fill faster than expected

# Fix: increase Survivor space
java -XX:SurvivorRatio=4 MyApp  # larger S0/S1
# Or increase Young Gen overall:
java -XX:NewSize=512m MyApp
```

**Visualising object lifecycle:**
```java
public class ObjectLifecycle {

    // This object will be promoted to Old Gen
    // — held by static ref (long-lived)
    static List<byte[]> longLived = new ArrayList<>();

    public static void main(String[] args) throws Exception {
        // Short-lived: die in Eden
        for (int i = 0; i < 1_000_000; i++) {
            byte[] temp = new byte[100]; // created in Eden
            // temp goes out of scope → dies in Eden ✅
        }

        // Medium-lived: survive a few GCs, then die in Survivor
        List<byte[]> medium = new ArrayList<>();
        for (int i = 0; i < 100; i++) {
            medium.add(new byte[1024]); // survives 1-2 GCs
        }
        Thread.sleep(500); // survives during sleep
        medium = null;     // now unreachable → dies in Survivor

        // Long-lived: survives threshold → promoted to Old Gen
        for (int i = 0; i < 10; i++) {
            longLived.add(new byte[1024]); // held by static
        }
        // After enough Minor GCs, longLived contents
        // reach tenuring threshold → promoted to Old Gen
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Both Survivor spaces hold objects" | One is **always empty** — it's the copy destination |
| "Survivor space is large" | Default ~10% of Young Gen each — intentionally small |
| "Tenuring threshold is always 15" | JVM **dynamically adjusts** based on Survivor fill level |
| "Objects in Survivor space are safe from GC" | They die in Survivor if **no GC root path** exists to them |
| "Survivor overflow promotes all objects" | Only overflowing objects promoted — not all Survivor contents |
| "S0 is always From, S1 is always To" | Roles **swap every GC** — which is From/To changes each cycle |

---

### 🔥 Pitfalls in Production

**1. Survivor space too small — premature promotion**
```bash
# Symptom: Old Gen fills faster than expected
# Major GC runs more frequently than it should
# jstat shows TT (tenuring threshold) = 1 or 2

# Cause: Survivor overflow
# More survivors than S0/S1 can hold
# → Excess promoted to Old Gen immediately
# → Old Gen fills with medium-lived objects

# Diagnosis:
-XX:+PrintTenuringDistribution
# If age 1 bytes ≈ total Survivor size → overflow

# Fix: increase Survivor space
-XX:SurvivorRatio=4    # from default 8 → double Survivor size
# OR increase Young Gen total (more room for all spaces)
-XX:NewSize=1g
```

**2. Survivor space too large — wasted space**
```bash
# Opposite problem:
# Survivor spaces allocated 20% each of Young Gen
# But only 2% of objects survive → 18% wasted

# Diagnosis:
jstat -gcnew <pid> 1000
# S0U and S1U always tiny relative to S0C/S1C
# → Survivor space mostly unused

# Fix: increase SurvivorRatio (smaller Survivor spaces)
-XX:SurvivorRatio=12   # smaller Survivor, more Eden
# More Eden = less frequent Minor GC
```

**3. Age distribution cliff — hidden promotion storm**
```java
// Subtle: objects created at app startup
// survive all GCs during warmup period
// → all reach tenuring threshold simultaneously
// → mass promotion to Old Gen
// → Old Gen suddenly fills → Major GC spike

// Common in Spring Boot:
// Bean initialisation creates many objects at t=0
// All age together during warmup
// After ~15 Minor GCs: all promoted simultaneously
// → One large Old Gen fill → latency spike

// Mitigation: stagger startup work
// OR use G1GC which handles this more smoothly
// OR increase MaxTenuringThreshold to spread promotions
```

---

### 🔗 Related Keywords

- `Young Generation` — Survivor spaces live within it
- `Eden Space` — source of objects entering Survivor space
- `Minor GC` — triggers Survivor copy and role swap
- `Object Promotion` — Survivor → Old Gen when threshold exceeded
- `Old Generation` — receives promoted objects from Survivor
- `Tenuring Threshold` — age at which objects are promoted
- `SurvivorRatio` — controls Survivor space size relative to Eden
- `Copy Collector` — GC algorithm that Survivor space enables
- `Mark Word` — stores object's GC age (4 bits, max 15)
- `G1GC` — replaces fixed Survivor spaces with flexible regions

---

### 📌 Quick Reference Card

| #020 | Category: JVM Internals | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | JVM, Young Generation, Eden Space, GC Roots, Minor GC | |
| **Used by:** | GC, Minor GC, Object Aging, Object Promotion, Young Generation | |

---
### 🧠 Think About This Before We Continue

**Q1.** The copy-collect algorithm used in Survivor spaces has a fundamental space overhead — you always need one empty Survivor space as the copy destination. This means 50% of total Survivor capacity is always unused. For a 512MB Young Gen with SurvivorRatio=8: calculate exactly how much memory is permanently reserved but unusable — and explain why this trade-off is worth it compared to the alternative (mark-and-sweep in-place).

**Q2.** Objects carry a 4-bit age counter in their Mark Word — maximum value 15. This limits MaxTenuringThreshold to 15. Now consider: what would happen to the JVM's memory model if objects could age indefinitely (no promotion to Old Gen ever)? Why is promotion to a separate region (Old Gen) architecturally necessary rather than just keeping everything in Survivor spaces forever?

---