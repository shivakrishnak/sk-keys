---
layout: default
title: "Minor GC"
parent: "Java & JVM Internals"
nav_order: 282
permalink: /java/minor-gc/
number: "0282"
category: Java & JVM Internals
difficulty: ★★☆
depends_on: Young Generation, Eden Space, Survivor Space, GC Roots, JVM
used_by: Old Generation, Major GC, Stop-The-World, GC Tuning
related: Major GC, Full GC, Stop-The-World, G1GC
tags:
  - java
  - jvm
  - gc
  - performance
  - intermediate
---

# 282 — Minor GC

⚡ TL;DR — Minor GC collects the Young Generation, reclaiming short-lived objects from Eden and Survivor spaces in typically milliseconds — the most frequent but cheapest GC event.

| #282 | Category: Java & JVM Internals | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Young Generation, Eden Space, Survivor Space, GC Roots, JVM | |
| **Used by:** | Old Generation, Major GC, Stop-The-World, GC Tuning | |
| **Related:** | Major GC, Full GC, Stop-The-World, G1GC | |

---

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
Without targeted Young Generation collection, the only option is Full GC — scanning the entire heap. For an application with 4 GB of live Old Gen objects and 50 MB of short-lived Eden objects dying every second, a full 4 GB scan every second is catastrophically expensive. The entire heap must be paused, marked, swept, and compacted — all for the purpose of reclaiming 50 MB of Eden garbage that could be identified in a targeted 50 MB scan.

THE BREAKING POINT:
Collecting the entire heap when only 1% of heap objects are candidates is a 100× inefficiency. The GC must be able to scope its work to only the region where garbage is dense — the Young Generation.

THE INVENTION MOMENT:
Minor GC is the targeted, fast, frequent collection of only the Young Generation — skipping the vast, mostly-live Old Generation entirely. This is why Minor GC exists as a distinct event from full heap collection.

---

### 📘 Textbook Definition

A Minor GC (also called Young GC) is a garbage collection event that collects only the Young Generation of the JVM heap: Eden Space and both Survivor Spaces. It is triggered when Eden Space fills up. Minor GC is a stop-the-world event: all application threads pause while the GC traces object reachability from GC Roots (including the card table for Old→Young references), copies live objects from Eden and active Survivor to the inactive Survivor (or promotes to Old Gen), and resets Eden. Minor GC typically completes in <10ms for well-tuned applications and occurs every few hundred milliseconds to several seconds depending on allocation rate.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Minor GC is a fast, frequent cleanup of new objects — typically finishing in a few milliseconds.

**One analogy:**
> A restaurant clears tables between diners (Minor GC) rather than deep-cleaning the entire facility every time (Full GC). Clearing a table takes 30 seconds; deep-cleaning takes 4 hours. The table clearing happens 50× per day; the deep-clean happens once a month. Getting the frequency right makes both affordable.

**One insight:**
Minor GC is fast not because the JVM is clever, but because of the Generational Hypothesis: 95–99% of Eden is dead garbage by the time Eden fills. The copying collector only copies the 1–5% that's live. It never touches the 95% that's dead. The bigger and deader Eden is, the faster Minor GC runs (relative to surviving volume).

---

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. Minor GC must be scoped to only the Young Generation to be fast.
2. Old Generation objects can reference Young Generation objects (cross-gen refs must be handled).
3. The collection result must be equivalent to a full heap collection (no object incorrectly collected).

DERIVED DESIGN:
Invariant 1 means Minor GC cannot scan Old Gen — but invariant 2 means some Old Gen references are GC Roots for Young Gen objects. The Card Table solves this: a compact summary of which Old Gen regions have references into Young Gen. Only these card-table-marked regions are scanned during Minor GC, not the entire Old Gen. Invariant 3 is satisfied by combining stack GC Roots with card table Old-Gen-to-Young-Gen roots.

THE TRADE-OFFS:
Gain: O(Young Gen live objects) collection cost rather than O(full heap live objects); frequency tunable via Eden size.
Cost: Stop-the-world pause (typically 1–20ms); card table maintenance overhead on every Old→Young reference write (write barrier); promotion fills Old Gen over time, eventually requiring expensive Major GC.

---

### 🧪 Thought Experiment

SETUP:
Application allocates 100 MB in Eden in 2 seconds. 98 MB dies, 2 MB survives.

WITHOUT MINOR GC (only Full GC available):
Every 2 seconds (when Eden fills), a Full GC scans the entire 4 GB heap. 4 GB of live objects must be traced. Pause = 2 seconds of GC work. Application processes 2 seconds, pauses 2 seconds, processes 2 seconds, pauses 2 seconds... throughput = 50%.

WITH MINOR GC:
Every 2 seconds (when Eden fills), Minor GC scans only Young Gen. 2 MB of live objects are traced and copied. 98 MB is abandoned. Pause = a few milliseconds. Application processes 2 seconds, pauses 5ms, processes 2 seconds, pauses 5ms... throughput = 99.75%.

THE INSIGHT:
The "most of the heap is live objects that are never garbage" observation justifies skipping Old Gen in Minor GC. If you must scan 4 GB to collect 100 MB, you're paying too much. Minor GC targets where the garbage is dense.

---

### 🧠 Mental Model / Analogy

> Minor GC is like sorting your desk mail drawer at the end of each day. 95% is junk mail (dead objects) — discard instantly. 5% are papers to keep — move to the filing cabinet (Survivor/Old Gen). The whole operation takes 2 minutes. You don't re-examine every file in the entire office (Old Gen) every day — just the drawer where today's mail landed.

"Desk mail drawer" → Eden Space (daily new allocations)
"Junk mail" → dead objects (not reachable from GC Roots)
"Papers to keep" → surviving objects (reachable)
"Filing cabinet" → Survivor Space / Old Generation
"2-minute sort" → Minor GC pause (few ms to ~20ms)
"Not re-examining office files" → skipping Old Gen during Minor GC

Where this analogy breaks down: unlike humans who know which mail is junk by reading it, the JVM determines liveness by tracing reference chains — it doesn't look at the content of objects.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Java regularly cleans up its memory. Minor GC is the quick daily cleanup — it only handles the area where new, short-lived objects live. Because most short-lived objects are already unused by cleanup time, Minor GC runs very fast (a few milliseconds) and often (every few seconds).

**Level 2 — How to use it (junior developer):**
Monitor Minor GC with `jstat -gc <pid>`: `YGC` = count, `YGCT` = total time. A healthy application has `YGCT/elapsed` <1% (GC uses <1% of time). If `YGC` is very frequent (every few hundred ms), Eden may be too small. Use `-Xlog:gc:file=/tmp/gc.log` to log all GC events with timing.

**Level 3 — How it works (mid-level engineer):**
1. Eden fills → Minor GC trigger. 2. All threads reach a safepoint and pause. 3. GC Roots enumeration: stack locals + JNI + statics + dirty cards in card table (Old→Young refs). 4. Object graph traced from these roots in Young Gen. 5. Live objects from Eden and active Survivor copied to inactive Survivor (incrementing age) or promoted. 6. Eden and active Survivor reset (pointer move). S0/S1 swap. 7. Card table dirty bits cleared. 8. Threads resume.

**Level 4 — Why it was designed this way (senior/staff):**
The minor/major split in GC is JVM implementation of the "generation scavenging" algorithm first described by Cheney (1970) and popularised by Ungar in the Berkeley Smalltalk system (1984). The key insight that enabled Minor GC to skip Old Gen entirely: the card table and remembered sets are maintained incrementally by write barriers on every reference store. This amortises the cost of tracking cross-generational references over all pointer updates, making the Minor GC's Old-Gen scanning bounded and cheap (only dirty cards, not the full Old Gen).

---

### ⚙️ How It Works (Mechanism)

**Minor GC Step-by-Step:**

```
┌─────────────────────────────────────────────┐
│          MINOR GC STEPS                     │
├─────────────────────────────────────────────┤
│  Trigger: Eden fills (EU ≈ EC)              │
│  ↓                                          │
│  1. STW: All threads reach safepoint        │
│  ↓                                          │
│  2. Enumerate GC Roots (Young Gen scope):   │
│     a. Thread stacks (locals/params in Young)│
│     b. JNI local/global refs in Young       │
│     c. Static refs pointing to Young        │
│     d. Card Table: dirty cards in Old Gen   │
│        → these are cross-gen refs           │
│  ↓                                          │
│  3. Trace object graph from these roots     │
│     within Young Gen only                   │
│  ↓                                          │
│  4. For each live object found:             │
│     age < MaxTenuringThreshold              │
│       → copy to inactive Survivor (age+1)   │
│     age >= MaxTenuringThreshold             │
│       → promote to Old Gen                  │
│     Survivor overflow                       │
│       → promote all remaining to Old Gen    │
│  ↓                                          │
│  5. Reset Eden + active Survivor (pointer)  │
│     Swap S0/S1 roles                        │
│  ↓                                          │
│  6. Clear dirty card table entries          │
│  ↓                                          │
│  7. Resume all threads                      │
└─────────────────────────────────────────────┘
```

**Card Table (Cross-Gen Reference Tracking):**

```
Old Generation:
  [  region0  ][  region1  ][  region2  ][  region3  ]
      ↕ ref to         ↕ ref to
Card Table:
  [ clean ]   [ DIRTY ]    [ clean ]   [ DIRTY ]
                ↑ has ref to Young Gen   ↑

During Minor GC:
  Only scan dirty card regions (1 and 3) for Young refs
  Not the entire Old Gen (far cheaper)
```

**Minor GC Impact on Application Threads:**

```
Timeline:
  Thread A ──────|pause|─────────────────────
  Thread B ──────|pause|─────────────────────
  Thread C ──────|pause|─────────────────────
  GC Thread      ────────|GC work|────────────
                 ↑ STW                       ↑ resume
```

---

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW:
```
Allocation rate fills Eden every Δt seconds
  → Minor GC triggered ← YOU ARE HERE
  → STW pause begins (all threads frozen)
  → Young Gen collected (typically 1–20ms)
  → 95%+ Eden objects collected
  → 5% survivors aged/promoted
  → Eden reset, Survivor swapped
  → STW pause ends (threads resume)
  → Processing continues for Δt seconds
  → Repeat
```

FAILURE PATH:
```
Minor GC cannot complete in <MaxGCPauseMillis:
  → Too many surviving objects (large Survivor copy)
  → Survivor overflow → many promotions to Old Gen
  → Old Gen fills → triggers Major/Full GC
  → Latency spike from cascaded GC events
  → Diagnosis: jstat shows YGCT increasing and FGC
    increasing together
```

WHAT CHANGES AT SCALE:
At 1M requests/sec, allocation rate is enormous. Eden fills faster, Minor GC runs more frequently. At 100k req/sec with 1KB/request allocation: 100 MB/s → 256 MB Eden fills in 2.56 seconds. Minor GC frequency = 0.4/second. With 5ms average pause: 0.2% time in Minor GC — excellent. At 1M req/sec: frequency = 4/second, still manageable. The Young Generation handles high throughput well; it's the promotion rate that causes problems at scale.

---

### 💻 Code Example

Example 1 — Monitor Minor GC frequency and duration:
```bash
# Real-time GC monitoring
jstat -gc <pid> 1000    # every 1 second
# YGC = Young GC count (increases by 1 per Minor GC)
# YGCT = Total Young GC time (cumulative seconds)
# Per-GC average: YGCT / YGC

# GC log with timestamps
java -Xlog:gc:file=/tmp/gc.log:time,level -jar myapp.jar
grep "Pause Young" /tmp/gc.log | \
  awk '{print $1, $NF}' | tail -30
# Shows: timestamp and pause duration for each Minor GC
```

Example 2 — Reduce Minor GC frequency by increasing Eden:
```bash
# BAD: small Eden → frequent short GC pauses
java -Xmx2g -XX:NewSize=128m -jar myapp.jar
# If EU fills every 200ms = 5 GCs/second

# BETTER: larger Eden → less frequent but same length
java -Xmx2g -XX:NewSize=512m -jar myapp.jar
# EU fills every 800ms = 1.25 GCs/second (4× less frequent)
# Each GC same duration but 75% less pause overhead total

# BEST (G1GC): let GC adapt to meet pause target
java -Xmx2g -XX:+UseG1GC \
     -XX:MaxGCPauseMillis=100 -jar myapp.jar
```

Example 3 — GC pause histogram (p99/p999):
```bash
# Collect GC pause data and compute percentiles
java -Xlog:gc:file=/tmp/gc.log:time -jar myapp.jar &
# (run workload)
grep "Pause Young" /tmp/gc.log | \
  awk '{print $NF}' | \
  grep -o '[0-9.]*ms' | \
  sed 's/ms//' | \
  sort -n | \
  awk '{a[NR]=$1} END {
    print "p50:",a[int(NR*0.5)],
    "p99:",a[int(NR*0.99)],
    "p999:",a[int(NR*0.999)]
  }'
```

Example 4 — Check if app has long Minor GC tail latency:
```bash
# Good: p99 < 20ms, p999 < 50ms → Minor GC is healthy
# Problem: p99 > 100ms → investigate cause:
#   1. Survivor overflow: increase SurvivorRatio
#   2. Large live set in Young Gen: audit object lifetimes
#   3. JNI local reference processing: minimize JNI usage

# Find root cause of long Minor GC pauses:
java -Xlog:gc+phases=debug:file=/tmp/gc.log \
     -jar myapp.jar
# Shows each phase's duration within Minor GC
# "Object Copy" vs "Root Processing" breakdown visible
```

---

### ⚖️ Comparison Table

| GC Event | Region | Frequency | Typical Pause | Triggered By |
|---|---|---|---|---|
| **Minor GC** | Young Gen only | High (every 1–10s) | 1–20ms | Eden fills |
| Major GC | Old Gen (+ Young) | Low (every min–hrs) | 100ms–10s | Old Gen fills |
| Full GC | Entire heap | Very low (ideally rare) | 1s–minutes | Major GC failure, System.gc() |
| G1 Concurrent Mark | Old Gen | Background | 0ms (concurrent) | Heap occupancy threshold |
| ZGC Cycle | Entire heap | Regular | <1ms (mostly concurrent) | Allocation pressure |

How to choose: Minor GC: tune Eden size and Survivor to minimise frequency and overflow. Major GC: tune Old Gen size and GC algorithm. Aim for 0 Full GCs in production.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Minor GC is always fast (< 10ms)" | Minor GC duration depends on surviving object count. If many objects survive (large Survivor), it can take 50–100ms. "Minor" refers to scope (Young Gen only), not guaranteed duration. |
| "Minor GC doesn't affect application latency" | Minor GC is stop-the-world — all threads pause. p99 Minor GC pauses directly appear in request latency tail. |
| "Minor GC collects only dead objects" | Minor GC identifies and COPIES live objects; dead objects are collected implicitly by Eden reset (never explicitly touched). |
| "Card table scanning checks the entire Old Gen" | Only dirty cards (512-byte regions that had reference stores since last clean) are scanned. The card table is maintained by write barriers, keeping Minor GC's Old-Gen scanning bounded. |

---

### 🚨 Failure Modes & Diagnosis

**1. Excessive Minor GC Frequency**

Symptom: YGC increases many times per second; application sees periodic latency spikes matching GC frequency.

Root Cause: Eden too small for the allocation rate; refilling every few hundred milliseconds.

Diagnostic:
```bash
jstat -gcutil <pid> 500
# E% filling to 100% every few samples → Eden too small
# Plot EU over time: should be sawtooth, not rapid zigzag
```

Prevention: Increase Eden/Young Gen size. Use G1GC and set `MaxGCPauseMillis` to let GC adapt.

**2. Long Minor GC Pause (Survivor Working Set Too Large)**

Symptom: Minor GC pauses are 50–200ms; p99 request latency is high; short GC pauses are fine but long tail is problematic.

Root Cause: Too many objects surviving Minor GC — large amount of data being copied from Eden to Survivor and from Survivor to Survivor. Common in apps with many medium-life objects.

Diagnostic:
```bash
java -Xlog:gc+phases=debug -jar myapp.jar
# "Object Copy" phase duration shows copy volume

java -XX:+PrintTenuringDistribution -jar myapp.jar
# High age-distribution bytes = many surviving objects
```

Prevention: Reduce medium-life objects (those surviving 2–10 GC cycles); lower MaxTenuringThreshold to promote them out of Young Gen sooner.

**3. Minor GC Triggering Full GC (Promotion Failure)**

Symptom: Every Minor GC is immediately followed by a Full GC; `jstat` shows FGC incrementing with every YGC.

Root Cause: Minor GC cannot promote surviving objects to Old Gen (Old Gen full). This causes "promotion failure," triggering a Full GC.

Diagnostic:
```bash
jstat -gcutil <pid> 1000
# FGC incrementing with YGC = promotion failure

java -Xlog:gc:file=/tmp/gc.log:time -jar myapp.jar
grep "Promotion failed\|Evacuation Failure" /tmp/gc.log
```

Prevention: Increase Old Gen size (increase `-Xmx` or decrease `-XX:NewRatio`); fix memory leaks to reduce Old Gen fill rate.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Young Generation` — Minor GC operates exclusively on this heap region
- `Eden Space` — the trigger: Eden filling causes Minor GC
- `Survivor Space` — the destination for objects surviving Minor GC
- `GC Roots` — the starting points for Minor GC's liveness analysis

**Builds On This (learn these next):**
- `Old Generation` — the destination for promoted objects; fills over many Minor GC cycles
- `Major GC` — the expensive counterpart to Minor GC, collecting Old Generation
- `Stop-The-World` — the pause mechanism that Minor GC requires
- `G1GC` — modern collector with adaptive Young Gen sizing to optimise Minor GC frequency

**Alternatives / Comparisons:**
- `Major GC` — same basic algorithm but applied to Old Generation; far more expensive
- `Full GC` — collects both Young and Old Generations; should be avoided in production

---

### 📌 Quick Reference Card

┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Short, frequent GC collecting only Young  │
│              │ Generation — triggered by Eden filling    │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Full heap collection too expensive for    │
│ SOLVES       │ frequent short-lived object reclamation   │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Cost proportional to SURVIVING objects,   │
│              │ not all objects — 95% dead Eden is nearly │
│              │ free to collect by abandonment            │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always — automatic. Tune Eden size to     │
│              │ control frequency vs duration trade-off   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Reduce promotion failures by sizing Old   │
│              │ Gen correctly to absorb Minor GC promotions│
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Fast/frequent vs slow/infrequent: larger  │
│              │ Eden = rarer but same-duration Minor GC   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Minor GC: the daily desk-clearing — fast │
│              │ because 95% of the mail is already junk"  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Major GC → Stop-The-World → G1GC          │
└──────────────────────────────────────────────────────────┘

---

### 🧠 Think About This Before We Continue

**Q1.** The card table records which 512-byte Old Gen regions have written a reference to Young Gen since the last Minor GC. A write barrier runs on every reference store anywhere in the heap. An application performs 1 billion reference stores per second across a 4 GB Old Gen. What is the maximum number of dirty cards that can exist at the start of a Minor GC, and why does the card-table approach remain faster than scanning all of Old Gen even when most of the 4 GB heap has been written to — what mathematical property of card bytes vs heap bytes explains this?

**Q2.** In G1GC, the Young Generation is a set of "Eden regions" rather than a single contiguous space. When a Minor GC occurs in G1, it collects ALL Eden regions plus ALL Survivor regions simultaneously rather than being able to collect them selectively. What constraint makes G1GC unable to collect only the most garbage-dense Eden regions and skip the others — and how does this constraint compare to why G1GC CAN selectively collect only the garbage-densest Old Gen regions in mixed GC?

