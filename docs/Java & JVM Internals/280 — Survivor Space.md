---
layout: default
title: "Survivor Space"
parent: "Java & JVM Internals"
nav_order: 280
permalink: /java/survivor-space/
number: "0280"
category: Java & JVM Internals
difficulty: ★★☆
depends_on: Young Generation, Eden Space, Minor GC, JVM
used_by: Old Generation, Minor GC, Object Header
related: Eden Space, Old Generation, Young Generation, Minor GC
tags:
  - java
  - jvm
  - gc
  - memory
  - intermediate
---

# 280 — Survivor Space

⚡ TL;DR — Survivor Space is the Young Generation's transitional area where objects are aged across multiple Minor GC cycles before being promoted to the Old Generation.

| #280 | Category: Java & JVM Internals | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Young Generation, Eden Space, Minor GC, JVM | |
| **Used by:** | Old Generation, Minor GC, Object Header | |
| **Related:** | Eden Space, Old Generation, Young Generation, Minor GC | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Imagine Eden Space and Old Generation with nothing in between. Every object that survives one Minor GC would have to go directly to Old Generation. But Old Generation is collected infrequently and expensively (Major GC). If every temporarily-long-lived object (living through 2–3 GC cycles and then dying) goes to Old Generation, it fills the Old Gen with "medium-life" objects that should have died in Young Gen, triggering expensive Major GC far too frequently.

**THE BREAKING POINT:**
Objects that survive one GC cycle are not necessarily long-lived. A temporary connection wrapper might live for 5 requests before being released (surviving ~5 Minor GC cycles). If it goes directly to Old Gen after the first survival, it joins the long-lived objects and accelerates Old Gen fill. The GC needs a staging area to confirm that an object is truly long-lived before committing it to the expensive-to-collect Old Generation.

**THE INVENTION MOMENT:**
Survivor Space is the staging area — the "quarantine zone" where objects prove their longevity by surviving multiple Minor GC cycles before being promoted. This is exactly why Survivor Space exists: to filter out medium-life objects from polluting the Old Generation.

---

### 📘 Textbook Definition

Survivor Spaces (S0 and S1) are two equally sized subregions of the Young Generation that serve as the intermediate staging area for objects that survive Minor GC but have not yet reached the age threshold for promotion to Old Generation. At each Minor GC, objects from Eden and the active Survivor space (S0 or S1) that are still live are copied to the inactive Survivor space (the other one), with their age incremented by 1 in their Object Header. When an object's age reaches `MaxTenuringThreshold` (default: 15 for most GCs), it is promoted to Old Generation. The two Survivor spaces alternate roles ("From" and "To") after each GC. Only one Survivor is in use at any time; the other is always empty.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Survivor Space is an age filter — objects bounce between S0 and S1 until they've proven they're long-lived enough for the Old Generation.

**One analogy:**
> A hotel has a "temporary guest" register for check-ins of uncertain duration. Guests who stay more than a week are transferred to "long-term residents" wing. Survivor Space is the temporary register: guests (objects) are logged on each weekly audit (Minor GC). After enough weekly audits (MaxTenuringThreshold GC cycles), they transfer to the residents' wing (Old Generation).

**One insight:**
The two-Survivor design is elegant: it eliminates fragmentation in the Young Generation entirely. Rather than tracking free holes in Eden, the copying collector moves live objects from one Survivor to the other, leaving the source compact and fully recyclable. The "empty" Survivor's presence means there is always a defragmented destination for the next GC cycle.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Objects need multiple GC cycle opportunities to prove long-lived status (avoid premature Old Gen promotion).
2. The collecting region (Survivor) must always have a clean, empty destination for copying live objects.
3. Age must be tracked per-object to implement the promotion threshold correctly.

**DERIVED DESIGN:**
Invariant 1 requires multiple survival opportunities — hence the age counter and configurable threshold. Invariant 2 requires two Survivor spaces: one active (containing objects currently living there), one empty (target for the next copy). After each GC, the roles swap. Invariant 3 is implemented via age bits in the Object Header (GC age bits, typically 4 bits, max age 15).

**THE TRADE-OFFS:**
**Gain:** Filters medium-life objects from Old Generation; prevents unnecessary Major GC; clean compaction via copying.
**Cost:** Two Survivor spaces means 50% waste in the Survivor area (one is always empty); if Survivor space is too small, objects are promoted before they would naturally die (premature promotion).

---

### 🧪 Thought Experiment

**SETUP:**
Object P is a "medium-life" object. It's created for a user session (lives ~5 seconds). Minor GC runs every 2 seconds. MaxTenuringThreshold = 15.

WITHOUT SURVIVOR SPACE (Eden directly to Old Gen):
P created in Eden. At Minor GC (2s): P is alive → promoted to Old Gen immediately. Old Gen now holds P alongside truly long-lived objects (cache entries, singletons). Major GC runs to collect Old Gen — expensive. P dies after 5 seconds during a Major GC cycle. But the Major GC was triggered prematurely because of medium-life objects like P flooding Old Gen.

WITH SURVIVOR SPACE:
P created in Eden. GC 1: P alive → copy from Eden to S1 (age=1). GC 2: P alive → copy from S1 to S0 (age=2). GC 3 (7 seconds, P is now dead): P NOT reachable → NOT copied. P's memory in S0 abandoned. No Old Gen involvement at all. Major GC frequency unchanged.

**THE INSIGHT:**
Survivor Space acts as filter: objects that die young are reclaimed in Young Gen; objects that die medium-term are reclaimed in Young Gen; only truly long-lived objects reach Old Gen. This dramatically reduces Old Gen fill rate and major GC frequency.

---

### 🧠 Mental Model / Analogy

> The two Survivor spaces (S0, S1) are like a revolving door between Eden (the lobby) and Old Generation (the office building). Objects enter through Eden and wait in S0 (the first waiting room). At each GC cycle, the waiting rooms flip: everyone in S0 moves to S1, everyone in S1 moves to S0 (if they've waited long enough: out the door to Old Gen). Anyone who finishes their business during the cycle doesn't get moved — they disappear.

- "First waiting room (S0)" → active Survivor space
- "Second waiting room (S1)" → passive (empty) Survivor space
- "Flipping the rooms" → S0/S1 role swap after Minor GC
- "Waiting long enough" → reaching MaxTenuringThreshold
- "Out the door to Old Gen" → promotion
- "Finishing business and disappearing" → dying before threshold, collected in Young Gen

Where this analogy breaks down: unlike a revolving door where objects physically move, the JVM copies objects' bytes to the new Survivor space — the old copy in the source space is abandoned.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Most objects Java creates die very quickly. Some live a little longer. To avoid cluttering the expensive long-term memory area, the JVM puts temporary survivors in a "waiting room" (Survivor Space). Only after an object survives many cleanup cycles does it get moved to long-term storage. It's like a waiting room that proves whether you really should be admitted to the hospital vs. just resting before you recover.

**Level 2 — How to use it (junior developer):**
Monitor via `jstat`: `S0U`/`S1U` shows current usage; `S0C`/`S1C` shows capacity. If one Survivor is always at 100% and objects are frequently promoted to Old Gen, Survivor may be too small. Tune with `-XX:SurvivorRatio` (default 8, meaning Eden is 8× each Survivor's size in the Young Gen) or `-XX:MaxTenuringThreshold` (default 15, lower to promote sooner).

**Level 3 — How it works (mid-level engineer):**
Each Minor GC: the "From" Survivor (active one, containing aged objects) and Eden are processed together. GC Roots are traced. Live objects found in Eden and From-Survivor are evaluated: age > `MaxTenuringThreshold` → Old Gen; else → copy to To-Survivor with age+1. Then From and Eden are reset (pointer move). S0/S1 roles swap (old To becomes new From). If To-Survivor fills up before all survivors are copied, remaining live objects are promoted to Old Gen directly (regardless of age) — "emergency promotion" or "overflow."

**Level 4 — Why it was designed this way (senior/staff):**
The dual Survivor design is a semi-space copying collector applied to a subregion. The "always empty" space overhead (1 Survivor is always empty, wasting Young Gen space) was accepted as the cost of fragment-free compaction. Original HotSpot tuning of `SurvivorRatio=8` was determined empirically to balance Eden throughput against Survivor capacity for typical server workloads. The G1GC evolution abandoned fixed-size Survivor regions in favour of dynamically-sized "survivor regions" within the region pool, adapting Survivor capacity to measured survival rates — eliminating the need to manually tune `SurvivorRatio`.

---

### ⚙️ How It Works (Mechanism)

**Surviving Object Lifecycle:**

```
┌─────────────────────────────────────────────┐
│      SURVIVOR SPACE LIFECYCLE               │
├─────────────────────────────────────────────┤
│  Minor GC 1:                                │
│  Eden: [A(age0) B(age0) C(age0)]            │
│  S0 (from): []                              │
│  S1 (to):   []                              │
│                                             │
│  After GC 1:                                │
│  - A: reachable → copy to S1, age=1         │
│  - B: unreachable → abandoned             │
│  - C: reachable → copy to S1, age=1         │
│  Eden: [] (reset)                           │
│  S0: [] (now empty = "To" space)            │
│  S1: [A(age1) C(age1)] (now "From")         │
│                                             │
│  Minor GC 2:                                │
│  - A: reachable → copy to S0, age=2         │
│  - C: unreachable → abandoned             │
│  - New Eden objects processed               │
│  S1: [] (empty = new "To")                  │
│  S0: [A(age2)] (now "From")                 │
│                                             │
│  ... (repeat until age = MaxTenuring) ...   │
│                                             │
│  GC 15: A(age15) → PROMOTE to Old Gen       │
└─────────────────────────────────────────────┘
```

**Survivor Overflow (Premature Promotion):**

```
┌─────────────────────────────────────────────┐
│     SURVIVOR OVERFLOW                       │
├─────────────────────────────────────────────┤
│  "To" Survivor fills before all survivors   │
│  can be copied:                             │
│                                             │
│  Remaining live objects from Eden/From →    │
│  PROMOTED to Old Generation                 │
│  (regardless of age!)                       │
│                                             │
│  Symptom: Old Gen grows faster than         │
│  expected; jstat S0/S1 at 100%             │
│  Fix: increase SurvivorRatio or NewSize     │
└─────────────────────────────────────────────┘
```

**Age Distribution Tracking:**
The JVM tracks age distribution statistics (`-XX:+PrintTenuringDistribution`) after each Minor GC, showing how many bytes of each age survived. G1GC uses this to dynamically set `MaxTenuringThreshold` to the age where the cumulative survivor size exceeds 50% of the desired Survivor space size.

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Object created in Eden (age 0)
  → GC 1: alive → S1 (age 1)
    ← YOU ARE HERE (object in Survivor, aging)
  → GC 2: alive → S0 (age 2)
  → GC 3: dead → abandoned in S0, NOT copied
    (collected for free — no trace in Old Gen)

  OR:
  → GC 1 → GC 2 → ... → GC 15: alive → Old Generation
```

**FAILURE PATH:**
```
Survivor overflow:
  → Survivor too small for surviving objects
  → Objects promoted early to Old Gen (age 0–5)
  → Old Gen fills prematurely
  → Major GC triggered too often
  → Observable: high OGC (Full GC count) in jstat
  → Fix: -XX:SurvivorRatio=4 (larger Survivor relative to Eden)
```

**WHAT CHANGES AT SCALE:**
At high object survival rates (e.g., a workload with many medium-lived objects like 1-minute HTTP sessions), Survivor space becomes the bottleneck. Objects continuously bounce between S0 and S1, consuming CPU for copying. If survival rate is genuinely high, lowering `MaxTenuringThreshold` (e.g., to 5) promotes objects faster, reducing Young Gen copying overhead. The trade-off: fewer Major GCs caught early vs. slightly faster Old Gen fill.

---

### 💻 Code Example

Example 1 — Monitor Survivor space:
```bash
# Monitor GC with Survivor stats every 2 seconds
jstat -gc <pid> 2000
# Key columns:
#   S0C: S0 Capacity (KB), S1C: S1 Capacity
#   S0U: S0 Used (KB),     S1U: S1 Used
#   (Only one of S0U/S1U will be > 0 at a time)
#   TT: Tenuring threshold (adaptive max)
#   MTT: MaxTenuringThreshold configured value
```

Example 2 — Print tenuring distribution:
```bash
java -XX:+PrintGCDetails \
     -XX:+PrintTenuringDistribution \
     -Xlog:gc+age=trace \
     -jar myapp.jar

# Output example:
# Desired survivor size 26738688 bytes, new threshold 8
# - age   1:   4,096,512 bytes, 4,096,512 total
# - age   2:   2,048,256 bytes, 6,144,768 total
# - age   3:     512,064 bytes, 6,656,832 total
# - age   8:     123,456 bytes, 6,780,288 total
# (objects mostly die by age 3 — threshold at 8 is fine)
```

Example 3 — Tune Survivor ratio and threshold:
```bash
# BAD: tiny Survivor (default SurvivorRatio=8
# means Survivor = Eden/8, potentially too small)
java -Xmx2g -jar myapp.jar

# GOOD: increase Survivor size for high-survival workloads
java -Xmx2g \
     -XX:NewSize=512m \
     -XX:SurvivorRatio=4 \           # Eden = 4x each Survivor
     -XX:MaxTenuringThreshold=10 \   # Promote after 10 GCs
     -XX:+PrintTenuringDistribution \
     -jar myapp.jar
```

Example 4 — G1GC adaptive tenuring:
```bash
# G1GC automatically adapts MaxTenuringThreshold
# based on measured survival rates
java -XX:+UseG1GC \
     -XX:MaxGCPauseMillis=200 \
     -Xlog:gc+age=debug \
     -jar myapp.jar
# G1 output: "New desired survivor size XXmb,
#             new threshold Y (max N)"
# Y: dynamically computed by G1 based on survival rate
```

---

### ⚖️ Comparison Table

| Config Scenario | Effect on Survivor | Effect on Old Gen | Best For |
|---|---|---|---|
| Small Survivor (SurvivorRatio=16) | Overflows; premature promotion | Fills faster | High-throughput, mostly short-lived objs |
| **Default Survivor (SurvivorRatio=8)** | Balanced | Moderate fill | General purpose |
| Large Survivor (SurvivorRatio=4) | More capacity; less overflow | Fills slower | Many medium-life objects |
| Low MaxTenuringThreshold (e.g., 5) | Objects promoted quickly | Fills moderately | Confirmed long-lived-at-5-cycles workload |
| G1GC adaptive | Dynamic | Adaptive | Production services (recommended) |

How to choose: For most applications, use G1GC defaults (adaptive). Only tune SurvivorRatio and MaxTenuringThreshold if `jstat` shows consistent Survivor overflow (S0U/S1U always 100%) or premature Old Gen filling.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "S0 and S1 are both in use simultaneously" | Only ONE Survivor space is in use at any time. The other is always empty (the "To" space). Both being non-zero in jstat briefly happens during GC itself. |
| "Larger Survivor means better performance" | Larger Survivor reduces premature promotion but comes at the cost of smaller Eden (smaller Eden → more frequent Minor GC). It's a trade-off. |
| "Objects always survive exactly MaxTenuringThreshold GC cycles" | Survivor OVERFLOW promotes objects regardless of age. Adaptive tenuring (G1) changes the threshold dynamically. |
| "G1GC uses Eden/Survivor layout like Parallel GC" | G1GC uses individual equal-sized heap regions that are dynamically assigned as Eden, Survivor, or Old — no fixed contiguous spaces. The concept of Survivor is preserved but implemented differently. |

---

### 🚨 Failure Modes & Diagnosis

**1. Survivor Space Overflow → Premature Promotion**

**Symptom:** Old Generation fills rapidly; `jstat` shows `TT` (tenuring threshold) consistently at 1 or 2; `S0U` or `S1U` always at nearly 100%.

**Root Cause:** Too many objects surviving Minor GC relative to Survivor capacity. Objects promoted early (age 1–2) instead of ageing to 15.

**Diagnostic:**
```bash
java -XX:+PrintTenuringDistribution -jar myapp.jar
# If age 1 objects already exceed Survivor size → overflow

jstat -gc <pid> 1000
# TT < MTT and S0/S1 at 100% consistently → overflow
```

**Fix:**
```bash
# Increase Survivor size (decrease ratio)
java -XX:SurvivorRatio=4 -jar myapp.jar
# OR: increase Young Gen total
java -XX:NewSize=1g -XX:MaxNewSize=1g -jar myapp.jar
```

**Prevention:** Use `PrintTenuringDistribution` in testing to understand survival rates before production sizing.

**2. Long Minor GC from Large Survivor (Object Copying Overhead)**

**Symptom:** Minor GC takes 20–50ms instead of expected <10ms; large amount of data copied per Minor GC.

**Root Cause:** Large Survivor contains many surviving objects — each must be copied. More bytes to copy → longer pause.

**Diagnostic:**
```bash
jstat -gcutil <pid> 1000
# If S0 or S1 near 100% after GC AND YGC pause long
# → too many survivors being copied

java -Xlog:gc+heap=debug -jar myapp.jar
# Shows bytes copied per Minor GC
```

**Fix:**
```java
// Application-level fix: reduce medium-life object creation
// Cache using bounded Caffeine instead of unbounded Map
// Close resources promptly to reduce Survivor fill rate
```

**Prevention:** Keep object lifetimes bimodal: either die in Eden or live long enough to warrant Old Gen. Medium-life objects are the Survivor's worst enemy.

**3. Incorrect Tenuring Threshold (TT=1 always)**

**Symptom:** Objects promoted after only 1 GC cycle; Old Gen pressure; `TT` column in `jstat` always shows 1.

**Root Cause:** Adaptive tenuring algorithm calculates that threshold should be 1 (Survivor already more than half full at age 1). Either Survivor is genuinely too small, or there are many unexpectedly long-lived objects.

**Diagnostic:**
```bash
# Check what's surviving to Survivor:
java -XX:+PrintTenuringDistribution \
     -XX:+PrintGCDetails -jar myapp.jar
# Large age-1 retention = genuinely high survival rate
# → Fix: application-level (fewer medium-life objects)
# OR: Survivor too small → increase Young Gen
```

**Prevention:** Profile application object lifetimes with async-profiler allocation profiling before production deployment sizing.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Eden Space` — where objects are born; Survivor Space is where they age after first survival
- `Young Generation` — Survivor Space is a sub-region of the Young Generation
- `Minor GC` — the collection cycle that triggers Survivor copy and age increment
- `Object Header` — the GC age bits in the header record each object's survival count

**Builds On This (learn these next):**
- `Old Generation` — the destination for objects that graduate from Survivor Space
- `G1GC` — uses dynamic regions to implement the Survivor concept adaptively
- `Minor GC` — describes the full process including Survivor role assignment and copying

**Alternatives / Comparisons:**
- `Old Generation` — what Survivor objects eventually become; understanding Old Gen explains why the Survivor filter is needed
- `Eden Space` — Survivor's sibling: Eden for new objects, Survivor for ageing objects

---

### 📌 Quick Reference Card

```text
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Two alternating Young Gen spaces for      │
│              │ ageing objects between Eden and Old Gen   │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Without staging, all survivors go to      │
│ SOLVES       │ Old Gen, filling it with medium-life      │
│              │ objects that then cause premature Major GC│
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ One Survivor is always empty — this 50%   │
│              │ waste is the cost of fragment-free        │
│              │ compaction via copying                    │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always present. Tune SurvivorRatio if     │
│              │ Survivor overflows (premature promotion)  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Do not place large objects in paths that  │
│              │ make them survive GC cycles unnecessarily │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Prevents premature Old Gen fill vs 50%    │
│              │ Survivor space always pre-reserved empty  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Survivor Space: the waiting room that    │
│              │ proves you're a permanent resident        │
│              │ before you get your office"               │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Old Generation → Minor GC → G1GC          │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Adaptive tenuring in G1GC dynamically calculates `MaxTenuringThreshold` based on the current survival rate: specifically, it sets the threshold to the age at which the cumulative survivor bytes would exceed 50% of the Survivor region capacity. A web service handles 10,000 requests/second, each creating a `RequestContext` object that lives exactly for 200ms. Minor GC runs every 150ms. How many Minor GC cycles does a RequestContext survive before dying? Does it make it to Old Generation? And what change in request handling time would cause it to start reaching Old Generation?

**Q2.** The Survivor Space design uses 50% of the Survivor area as dead weight (always empty). The JVM cannot reclaim this space for any other purpose. An alternative approach would be: allocate objects in Eden, and on Minor GC, record the objects that survived in an age table (no separate Survivor space needed). Why does the JVM NOT use this approach — what property of the copying collector design is enabled by the empty Survivor space that would be lost with an age table approach?

