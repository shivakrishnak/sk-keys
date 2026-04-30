---
layout: default
title: "Minor GC"
parent: "Java & JVM Internals"
nav_order: 21
permalink: /java/minor-gc/
---
# 021 — Minor GC

`#java` `#jvm` `#memory` `#gc` `#internals` `#intermediate`

⚡ TL;DR — The frequent, fast garbage collection that reclaims dead objects exclusively from the Young Generation — triggered by Eden filling up, typically pausing for 1–50ms.

| #021 | Category: Java & JVM Internals | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | JVM, Young Generation, Eden Space, Survivor Space, GC Roots | |
| **Used by:** | GC, Object Promotion, Old Generation, JVM Performance | |

---

### 📘 Textbook Definition

Minor GC is a **garbage collection event that collects only the Young Generation** (Eden + Survivor spaces). It is triggered when Eden space is exhausted. The collector traces from GC roots into Young Gen, copies live objects to a Survivor space (incrementing their age), promotes objects exceeding the tenuring threshold to Old Generation, and bulk-reclaims all dead objects in Eden and the From Survivor space. Minor GC is a Stop-The-World event but is typically short (1–50ms) due to the small Young Gen size and high death rate of young objects.

---

### 🟢 Simple Definition (Easy)

Minor GC is the **quick, frequent cleanup** of the Young Generation — triggered when Eden fills, takes milliseconds, reclaims the vast majority of objects created since the last collection.

---

### 🔵 Simple Definition (Elaborated)

Minor GC is the workhorse of Java garbage collection. It runs frequently (every few seconds in busy applications), collects only the small Young Generation (not the entire heap), and is fast because most objects it encounters are already dead. The entire stop-the-world pause is typically under 50ms. It's designed to be called thousands of times per day without significantly impacting application throughput — but when tuned poorly, its frequency and pause accumulation can become a real performance issue.

---

### 🔩 First Principles Explanation

**The design goal:**

```
Handle the common case (young object death)
as cheaply as possible:
  → Trigger often (Eden fills fast)
  → Pause briefly (small region, high death rate)
  → Reclaim maximally (98%+ of young objects dead)
  → Promote minimally (only threshold survivors)
```

**Why it can be fast:**

```
Three properties make Minor GC fast:

1. SMALL REGION
   Young Gen: 256MB - 2GB (fraction of total heap)
   Full heap: 4GB - 32GB
   Scanning 256MB vs 32GB = 128× less work maximum

2. HIGH DEATH RATE
   ~98% of Eden objects dead at collection time
   → Most "work" is doing nothing (dead = skip)
   → Only 2% requires copy work (survivors)
   → Collection time ∝ survivors, not total size

3. COPY COLLECTION
   No fragmentation to fix
   No mark-sweep-compact needed
   Just: trace, copy live, reset pointer
   Fast and cache-friendly (sequential writes)
```

**The card table problem — Old Gen references into Young Gen:**

```
Problem: GC roots include ALL references to Young Gen
  Some references come from OLD GEN objects
  Must scan entire Old Gen to find them?
  → Would make Minor GC as slow as Full GC

Solution: Card Table
  Old Gen divided into 512-byte "cards"
  When any Old Gen object is written:
    card containing that object marked "dirty"
  During Minor GC:
    Only scan DIRTY cards for Young Gen refs
    Not entire Old Gen

Result: Minor GC only scans a small fraction
  of Old Gen (only dirty cards)
  → Stays fast even when Old Gen is large
```

---

### ❓ Why Does This Exist — Why Before What

**Without Minor GC (separate from Major):**

```
Only option: Full GC on every collection
  Every GC scans entire heap (4-32GB)
  Every GC pauses for hundreds of milliseconds
  Every GC runs when ANY region fills

  At 100MB/sec allocation rate:
    4GB heap fills in 40 seconds
    Full GC every 40 seconds: 200-500ms pause
    5-12ms/sec in GC = 0.5-1.2% GC overhead

  That sounds acceptable... but:
    Modern apps allocate 500MB-2GB/sec
    Full GC every 2-4 seconds
    500ms pause every 2 seconds = 25% GC overhead
    → Application effectively 25% slower
    → Request latency spikes every 2 seconds
    → Completely unusable
```

**With Minor GC:**
```
Young Gen only: 256MB fills in 0.25 seconds
Minor GC: 5-20ms pause
5-20ms every 0.25 seconds = 2-8% overhead
→ Manageable, tunable, production-viable

Full GC: rare (Old Gen fills slowly)
→ System stable under high allocation load
```

---

### 🧠 Mental Model / Analogy

> Think of Minor GC as **taking out the kitchen trash** — you do it frequently (every day), it takes 2 minutes, and you're emptying a small bin that fills up fast.
>
> Major GC is the **quarterly whole-house deep clean** — rare, thorough, takes hours.
>
> You wouldn't do a whole-house deep clean every day — the kitchen trash can handles the daily volume cheaply. Minor GC is that daily trash run — frequent, fast, targeted at the highest-volume waste source.
>
> The **card table** is your mental note: "I think I left something in the living room (Old Gen) that belongs in the kitchen (Young Gen) — check that specific spot, don't search the whole house."

---

### ⚙️ How It Works — Step by Step

| #021 | Category: Java & JVM Internals | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | JVM, Young Generation, Eden Space, Survivor Space, GC Roots | |
| **Used by:** | GC, Object Promotion, Old Generation, JVM Performance | |

---

### 🔄 How It Connects

```
Eden fills
      ↓
Minor GC triggered (STW pause begins)
      ↓
Roots scanned + card table dirty cards
      ↓
Live objects identified in Young Gen
      ↓
┌─────────────────────────────────┐
│  Live object disposition:       │
│  age < threshold → Survivor     │
│  age >= threshold → Old Gen     │
│  too large → Old Gen directly   │
└─────────────────────────────────┘
      ↓
Eden + From Survivor bulk-wiped
      ↓
STW pause ends → threads resume
      ↓
If Old Gen fills during promotion
→ Concurrent Mode Failure (G1/CMS)
→ Full GC triggered
```

---

### 💻 Code Example

**Reading Minor GC logs:**
```bash
java -Xms512m -Xmx512m \
     -Xlog:gc:file=gc.log:time,uptime \
     MyApp
```

```
# Minor GC log entries (JDK 17+):
[0.267s] GC(0) Pause Young (Allocation Failure)
[0.267s] GC(0) DefNew: 69952K(78656K)->8703K(78656K)
#                Eden+S→ After     Young Total
[0.267s] GC(0) Tenured: 0K(174784K)->0K(174784K)
#                Old Gen: unchanged (no promotion)
[0.267s] GC(0) Pause Young 68M->8M(247M) 5.321ms
#                Heap: before→after  Total    Pause

# Healthy Minor GC:
# • Pause < 50ms
# • Old Gen changes minimally (low promotion)
# • Frequency: every 1-10 seconds
# • Recovery ratio: (before-after)/before > 90%
```

**Triggering and observing Minor GC programmatically:**
```java
public class MinorGCDemo {

    public static void main(String[] args) throws Exception {
        Runtime rt = Runtime.getRuntime();

        System.out.println("Before allocation:");
        printMemory(rt);

        // Allocate many short-lived objects → fills Eden
        for (int i = 0; i < 1_000_000; i++) {
            // Each byte[] goes to Eden via TLAB
            // All unreferenced → die at Minor GC
            byte[] temp = new byte[1024]; // 1KB each → 1GB total
            // temp immediately unreachable after loop iteration
        }

        System.out.println("After allocation loop:");
        printMemory(rt);
        // Heap usage should be LOW → Minor GC ran multiple times
        // All temp arrays collected

        // These survive → will be promoted eventually
        List<byte[]> survivors = new ArrayList<>();
        for (int i = 0; i < 100; i++) {
            survivors.add(new byte[10240]); // 10KB each
        }

        System.out.println("After creating survivors:");
        printMemory(rt);
    }

    static void printMemory(Runtime rt) {
        long used = (rt.totalMemory() - rt.freeMemory())
                     / 1024 / 1024;
        System.out.println("  Used heap: " + used + "MB");
    }
}
```

**Card Table — why Minor GC stays fast with large Old Gen:**
```java
// Scenario: Old Gen object holds reference to Young Gen object
public class CardTableDemo {
    static Object[] oldGenArray = new Object[1000];
    // oldGenArray is static → Old Gen (promoted after warmup)

    public static void main(String[] args) {
        // Writing Young Gen ref into Old Gen object
        // → JVM marks the card containing oldGenArray as dirty
        oldGenArray[0] = new Object(); // ← write barrier fires here
        // JVM internally:
        //   card_table[address_of(oldGenArray) >> 9] = DIRTY

        // During next Minor GC:
        //   Only dirty cards scanned, not all of Old Gen
        //   oldGenArray[0] found → keeps new Object() alive
    }
}

// Write barrier overhead:
// Every object field write = check + potential card mark
// Cost: ~1-3 CPU cycles extra per write
// Worth it: enables fast Minor GC by avoiding full Old Gen scan
```

**Monitoring Minor GC frequency and pause:**
```bash
# Live monitoring with jstat
jstat -gcnew <pid> 1000    # every 1000ms

# Output columns:
# S0C   S1C   S0U   S1U  TT MTT DSS   EC     EU    YGC  YGCT
# 512   512   0.0  412.0  7  15  256  4096  3276    47  0.623
#
# YGC  = total Young GC count (47)
# YGCT = total Young GC time (0.623 seconds)
# Average pause = 0.623/47 = 13.3ms ← healthy
#
# EU = Eden Used (3276KB of 4096KB = 80% full)
# → Minor GC imminent

# Alert thresholds:
# Average Minor GC pause > 100ms → tune Young Gen
# Minor GC frequency > 1/sec → allocation rate too high
# Old Gen growth per Minor GC > 10MB → promotion issue
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Minor GC collects the whole heap" | Only **Young Generation** — Old Gen untouched |
| "Minor GC is not Stop-The-World" | It IS STW — all threads pause, but briefly |
| "Minor GC always takes < 10ms" | Can take 50-200ms if **many live objects** in Young Gen |
| "Minor GC doesn't affect Old Gen" | Minor GC can **fill Old Gen** via promotion — triggering Major GC |
| "Card table is Optional" | Card table is **essential** — without it Minor GC must scan all of Old Gen |
| "Minor GC triggered on schedule" | Triggered by **allocation pressure** (Eden full), not time |

---

### 🔥 Pitfalls in Production

**1. Promotion failure — Minor GC triggers Full GC**
```bash
# Symptom: Minor GC log shows:
# [GC (Allocation Failure) -- 490M->490M(512M)]
# [Full GC (Allocation Failure) 490M->125M(512M)]

# What happened:
# Minor GC tried to promote objects to Old Gen
# Old Gen had no space to accept them
# → Promotion failure
# → JVM falls back to Full GC immediately
# → Much longer pause (hundreds of ms)

# Fix: ensure Old Gen has headroom
# Monitor: jstat -gcold <pid>
# If Old Gen > 70% used → Major GC collection
#   overdue or Old Gen too small
java -Xmx4g -XX:NewRatio=2 MyApp
# 4GB heap: Old=2.6GB, Young=1.3GB
# More Old Gen headroom for promotions
```

**2. Minor GC pause creeping up over time**
```bash
# Healthy: Minor GC 5ms for months
# Then: gradually climbs to 50ms over weeks

# Why: Old Gen filling slowly
# More live objects → more cross-references
# Card table has more dirty cards each GC cycle
# → Minor GC must scan more of Old Gen each time
# → Pause grows proportionally

# Diagnosis:
jstat -gcold <pid> 5000  # check Old Gen growth rate
# If Old Gen grows 50MB/day → memory leak
# Heap dump + MAT → find root path

# Fix: fix the leak OR increase heap
# Temporary: schedule off-peak Full GC
# jcmd <pid> GC.run
```

**3. Allocation rate exceeding Minor GC throughput**
```
Scenario:
  Application allocates 2GB/sec
  Eden size: 512MB
  Eden fills in 0.25 seconds
  Minor GC takes 20ms
  → 20ms pause every 250ms = 8% GC overhead

  Scaling to 4 instances:
    Each instance: 8% GC overhead
    Aggregate: 8% less throughput than raw compute

  Fix priority order:
  1. Reduce allocation rate (object pooling,
     primitives, avoid boxing)
  2. Increase Eden size (less frequent GC)
  3. Use ZGC/Shenandoah (concurrent collection,
     near-zero STW)
```

---

### 🔗 Related Keywords

- `Young Generation` — the region Minor GC collects
- `Eden Space` — fills up to trigger Minor GC
- `Survivor Space` — receives live objects from Minor GC
- `Stop-The-World` — Minor GC is always STW
- `Card Table` — enables fast Old Gen reference scanning
- `Object Promotion` — Minor GC's side effect on Old Gen
- `Major GC` — triggered when Minor GC promotion fills Old Gen
- `GC Roots` — starting points for Minor GC tracing
- `Write Barrier` — maintains card table on every field write
- `G1GC` — reimplements Minor GC with pause time targets

---

### 📌 Quick Reference Card
```
┌─────────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Fast Young Gen collection — copy live objects    │
│              │ out, wipe Eden in bulk; triggers on Eden full    │
├──────────────┼──────────────────────────────────────────────────┤
│ USE WHEN     │ Always — every JVM app does Minor GC             │
├──────────────┼──────────────────────────────────────────────────┤
│ AVOID WHEN   │ Minimise frequency: tune Eden size to balance    │
│              │ GC frequency vs pause length                     │
├──────────────┼──────────────────────────────────────────────────┤
│ ONE-LINER    │ "Fast and frequent — live objects out,           │
│              │  dead Eden wiped in one shot"                    │
├──────────────┼──────────────────────────────────────────────────┤
│ NEXT EXPLORE │ Major GC → Full GC → Stop-The-World → G1GC       │
└─────────────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** The card table uses 512-byte granularity — one card per 512 bytes of Old Gen. A write barrier fires on every object field write, marking the card dirty. At 100 million field writes per second in a busy application — what is the CPU overhead of write barriers — and why is this considered an acceptable trade-off for Minor GC performance?

**Q2.** A Minor GC pause suddenly spikes from 10ms to 150ms after a new deployment. The allocation rate didn't change. Young Gen size didn't change. What are the three most likely causes — and what specific GC log entries and jstat outputs would you look for to distinguish between them?

---