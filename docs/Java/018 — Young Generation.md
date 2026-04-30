---
layout: default
title: "Young Generation"
parent: "Java & JVM Internals"
nav_order: 18
permalink: /java/young-generation/
number: "018"
category: JVM Internals
difficulty: ★★☆
depends_on: JVM, Heap Memory, GC Roots, Object Allocation
used_by: GC, Minor GC, Object Promotion, TLAB, G1GC
tags: #java, #jvm, #memory, #gc, #internals, #intermediate
---

# 018 — Young Generation

`#java` `#jvm` `#memory` `#gc` `#internals` `#intermediate`

⚡ TL;DR — The heap region where all new objects are born, divided into Eden and two Survivor spaces, designed around the observation that most objects die young — enabling fast, frequent, cheap garbage collection.

| #018 | Category: JVM Internals | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | JVM, Heap Memory, GC Roots, Object Allocation | |
| **Used by:** | GC, Minor GC, Object Promotion, TLAB, G1GC | |

---

### 📘 Textbook Definition

The Young Generation is the **heap region allocated for newly created objects**, subdivided into Eden space (~80%) and two equal Survivor spaces (S0 and S1, ~10% each). Objects are allocated in Eden via TLAB. When Eden fills, a **Minor GC** is triggered — live objects are copied to a Survivor space, dead objects are reclaimed. Objects that survive enough Minor GCs (default threshold: 15) are promoted to the Old Generation.

---

### 🟢 Simple Definition (Easy)

Young Generation is the heap's **nursery** — where every new object starts life. Most objects die here quickly and cheaply. The few that survive long enough get promoted to a more permanent region.

---

### 🔵 Simple Definition (Elaborated)

When you write `new Order()`, it goes to the Young Generation — specifically the Eden space. When Eden fills up, a Minor GC sweeps through: dead objects (the majority) are instantly reclaimed, survivors are copied to a Survivor space and age-stamped. Objects that survive repeatedly get promoted to Old Generation. This design is intentional — keeping short-lived objects in a small, frequently-collected space makes GC fast and cheap for the most common case.

---

### 🔩 First Principles Explanation

**The empirical observation that drives the design:**

```
Profiling real Java applications shows:
  ~98% of objects die within milliseconds of creation
  ~1-2% survive long-term

Examples of short-lived objects:
  • Loop iteration variables
  • Builder/factory intermediate objects
  • DTO objects in request processing
  • String concatenation temporaries
  • Stream pipeline intermediate objects
  • Exception objects that are caught immediately
```

**The naive GC approach — collect everything equally:**

```
Collect entire heap on every GC
  → Must scan ALL objects every time
  → Most objects are long-lived → less reclaimed
  → Pause time proportional to entire heap size
  → For 16GB heap → seconds of pause time
  → Unacceptable for any production system
```

**The generational insight:**

> "Don't collect all objects equally.
>  Segregate by age. Collect young ones
>  frequently (cheap), old ones rarely (expensive)."

```
Young Gen: small (256MB - 2GB typical)
  → fills fast (lots of allocation)
  → collect frequently (every few seconds)
  → mostly garbage (cheap to collect)
  → pause: milliseconds

Old Gen: large (2GB - 30GB typical)
  → fills slowly (only survivors promoted)
  → collect rarely (every minutes/hours)
  → mostly live (expensive to collect)
  → pause: tens of milliseconds to seconds
```

---

### ❓ Why Does This Exist — Why Before What

**Without Young Generation:**

```
Single-region heap:
  All objects compete for same space
  GC must scan entire heap every cycle
  Most objects already dead but still
  mixed in with long-lived objects
  → Cannot do cheap partial collections
  → Every GC is a Full GC
  → Pause time = proportional to heap size
  → 32GB heap → potentially seconds of pause
  → Unusable for latency-sensitive applications

Without generational hypothesis exploitation:
  → Throughput: 40-70% lower (GC overhead)
  → Latency: 10-100× worse pause times
  → Memory: higher fragmentation
  → Scalability: doesn't scale with heap size
```

**With Young Generation:**
```
→ 98% of GC work done in small space
→ Minor GC pause: 1-50ms vs seconds
→ Old Gen collected only when needed
→ Throughput dramatically higher
→ Scales as heap grows
→ Foundation for all modern GC algorithms
```

---

### 🧠 Mental Model / Analogy

> Think of a busy restaurant kitchen (your application):
>
> **Eden** is the **prep counter** — everything starts here. Most prep containers (objects) are used and discarded within minutes.
>
> **Survivor spaces** are the **short-term shelf** — things that survived the immediate prep rush. Still being used, kept nearby.
>
> **Old Generation** is the **storage room** — long-term supplies that have proven they're needed regularly.
>
> The **dishwasher (Minor GC)** runs frequently and quickly — mostly washing the same prep containers that get used and discarded constantly. It rarely touches the storage room.
>
> A full deep-clean of the storage room (Major GC) happens rarely — and takes much longer.

---

### ⚙️ How It Works — Eden and Survivor Spaces

| #018 | Category: JVM Internals | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | JVM, Heap Memory, GC Roots, Object Allocation | |
| **Used by:** | GC, Minor GC, Object Promotion, TLAB, G1GC | |

**The Minor GC cycle — step by step:**

```
BEFORE Minor GC:
  Eden: 80% full (allocation triggered GC)
  S0 (From): has survivors from last GC (age 1-N)
  S1 (To): EMPTY

MINOR GC RUNS:
  Step 1: Find live objects in Eden + S0
          (trace from GC roots)

  Step 2: COPY live objects from Eden → S1
          Increment their age by 1

  Step 3: COPY live objects from S0 → S1
          (if age < threshold)
          Increment their age by 1

  Step 4: Objects age >= threshold
          → Copy to OLD GENERATION
          (promotion)

  Step 5: Eden + S0 → completely wiped
          (all dead objects reclaimed instantly)
          S0 and S1 SWAP roles

AFTER Minor GC:
  Eden: EMPTY (ready for new allocations)
  S0 (now "To"): EMPTY
  S1 (now "From"): contains survivors, age 1-N
  Old Gen: received promoted objects
```

---

### 🔄 How It Connects

```
new Object()
      ↓
TLAB in Eden Space
      ↓
Eden fills up
      ↓
Minor GC triggered
      ↓
GC Roots traced → live objects found
      ↓
┌─────────────────────────────────┐
│  Live object age < threshold?   │
│  YES → copy to Survivor space   │
│  NO  → promote to Old Gen       │
└─────────────────────────────────┘
      ↓
Dead objects → Eden wiped clean
      ↓
Allocation resumes in fresh Eden
      ↓
Old Gen fills over time →
Major GC / Full GC triggered
```

---

### 💻 Code Example

**Observing Young Generation with GC logging:**
```bash
java -Xms512m -Xmx512m \
     -XX:NewRatio=2 \
     -Xlog:gc*:file=gc.log:time,uptime,level,tags \
     MyApp

# NewRatio=2 means: Old:Young = 2:1
# So for 512MB heap:
#   Young Gen = ~170MB
#   Old Gen   = ~340MB
```

```
# GC log output (Minor GC):
[0.523s][info][gc] GC(3) Pause Young (Allocation Failure)
[0.523s][info][gc] GC(3) DefNew: 139776K->17472K(157248K)
#                         Eden+S0 before → after (total Young)
[0.523s][info][gc] GC(3) Tenured: 0K->0K(349568K)
#                         Old Gen before → after (unchanged)
[0.523s][info][gc] GC(3) Pause Young 136M->17M(497M) 4.231ms
#                         Total heap: before→after, pause time
```

**Tuning Young Generation size:**
```bash
# Default: Young Gen = heap / (NewRatio + 1)
# NewRatio=2 → Young = 1/3 of heap

# Explicit sizing:
java -XX:NewSize=256m \       # initial Young Gen size
     -XX:MaxNewSize=512m \    # max Young Gen size
     MyApp

# Or as ratio:
java -XX:NewRatio=3 \         # Old:Young = 3:1
     MyApp                    # Young = 25% of heap

# High allocation rate apps (microservices, streaming):
# Larger Young Gen = less frequent Minor GC
# But: larger Young Gen = longer Minor GC pause
java -XX:NewSize=1g -XX:MaxNewSize=2g MyApp
```

**Observing object promotion:**
```bash
# Print tenuring distribution
java -XX:+PrintTenuringDistribution MyApp

# Output:
# Desired survivor size 8388608 bytes, new threshold 7 (max 15)
# - age   1:   4832472 bytes,   4832472 total
# - age   2:   1284632 bytes,   6117104 total
# - age   3:    189832 bytes,   6306936 total
# ...
# threshold = 7 means: survive 7 Minor GCs → promote to Old Gen

# If many objects hit max age quickly:
# → Young Gen too small, increase it
# If objects promoted too fast (low threshold):
# → Premature promotion, Old Gen fills too fast
```

**Allocation rate measurement:**
```java
import com.sun.management.GarbageCollectionNotificationInfo;
import javax.management.*;
import java.lang.management.*;

// Monitor allocation rate via GC notifications
for (GarbageCollectorMXBean gc :
        ManagementFactory.getGarbageCollectorMXBeans()) {

    if (gc instanceof NotificationEmitter ne) {
        ne.addNotificationListener((notif, handback) -> {
            var info = GarbageCollectionNotificationInfo
                .from((CompositeData) notif.getUserData());

            String cause = info.getGcCause();
            long duration = info.getGcInfo().getDuration();

            System.out.printf(
                "GC: %s, cause: %s, duration: %dms%n",
                info.getGcName(), cause, duration
            );
        }, null, null);
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Both Survivor spaces are used simultaneously" | One is always **empty** — they swap roles each GC |
| "Minor GC is always fast" | Usually fast, but can be slow if **many live objects** in Young Gen |
| "Objects always start in Eden" | Large objects may go **directly to Old Gen** bypassing Young Gen entirely |
| "NewRatio controls total Young Gen size" | NewRatio = **Old:Young ratio** — actual size depends on total heap |
| "Promotion threshold is always 15" | Default is 15 but JVM may **dynamically adjust** based on Survivor space pressure |
| "Young Gen size is fixed" | JVM can **dynamically resize** Young Gen based on GC ergonomics |

---

### 🔥 Pitfalls in Production

**1. Young Gen too small — GC thrashing**
```bash
# Symptom: Minor GC every 100ms, 5ms pause each
# 50ms/sec spent in GC = 5% throughput loss
# Plus: objects promoted prematurely → Old Gen fills fast

# Diagnosis:
jstat -gcutil <pid> 1000
# Output every 1 second:
#  S0  S1   E    O    M  CCS   YGC  YGCT  FGC  FGCT   GCT
#   0  45  76   23   96   93   124  0.834   2  0.278  1.112
# YGC=124 in short time → too frequent

# Fix: increase Young Gen
java -XX:NewSize=512m -XX:MaxNewSize=512m MyApp
```

**2. Humongous objects bypassing Young Gen (G1GC)**
```java
// G1GC: objects > region_size/2 go to Old Gen directly
// Default region size: 1-32MB depending on heap

// This large array bypasses Young Gen entirely:
byte[] large = new byte[2 * 1024 * 1024]; // 2MB

// G1GC region size 4MB → 2MB > 2MB threshold
// → Allocated directly in Old Gen
// → Old Gen fills faster → more frequent Mixed/Full GC

// Diagnosis:
-Xlog:gc+humongous=debug
// Shows humongous allocations

// Fix: increase region size if legitimate large objects
java -XX:G1HeapRegionSize=8m MyApp
// Or: redesign to avoid large allocations in hot paths
```

**3. Survivor space overflow — premature promotion**
```bash
# Symptom: objects promoted to Old Gen at age 1 or 2
# (should survive to age 15)

# Why: Survivor space too small to hold all survivors
# Overflow → objects go directly to Old Gen
# Old Gen fills fast → frequent Major GC

# Diagnosis:
-XX:+PrintTenuringDistribution
# If age 1 shows very large bytes:
#   age 1: 157286400 bytes ← nearly all survivors age 1
# Survivor space too small

# Fix: increase Survivor space ratio
java -XX:SurvivorRatio=6 MyApp
# SurvivorRatio=6 → Eden:S0:S1 = 6:1:1
# Default = 8 → Eden:S0:S1 = 8:1:1
# Lower ratio → larger Survivor spaces
```

---

### 🔗 Related Keywords

- `Heap Memory` — Young Generation is a region within it
- `Eden Space` — birth place of all new objects
- `Survivor Space` — temporary aging area between Eden and Old Gen
- `Minor GC` — collects Young Generation
- `Old Generation` — destination for long-lived promoted objects
- `TLAB` — per-thread fast allocation buffer in Eden
- `Object Promotion` — moving aged survivors to Old Gen
- `G1GC` — modern GC with different Young Gen implementation
- `GC Ergonomics` — JVM's automatic Young Gen sizing
- `Tenuring Threshold` — age at which objects get promoted

---

### 📌 Quick Reference Card

| #018 | Category: JVM Internals | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | JVM, Heap Memory, GC Roots, Object Allocation | |
| **Used by:** | GC, Minor GC, Object Promotion, TLAB, G1GC | |

---
### 🧠 Think About This Before We Continue

**Q1.** A high-throughput REST API processes 10,000 requests/second. Each request creates ~500 short-lived objects (DTOs, builders, strings). Minor GC runs every 2 seconds with a 15ms pause. The team wants to reduce GC pause impact. What are the two opposite directions they could tune Young Generation size — and what are the exact trade-offs of each direction?

**Q2.** In G1GC, the Young Generation is not a contiguous memory region — it's a collection of non-contiguous heap regions. How does this change the Minor GC mechanics compared to the classic Eden+Survivor model? What advantage does this give G1GC for meeting pause time targets?

---