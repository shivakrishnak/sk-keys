---
layout: default
title: "CMS (Concurrent Mark Sweep)"
parent: "Java & JVM Internals"
nav_order: 288
permalink: /java/cms-concurrent-mark-sweep/
number: "288"
category: Java & JVM Internals
difficulty: ★★★
depends_on: Old Generation, GC Roots, Stop-The-World (STW), Minor GC, Heap Memory
used_by: GC Tuning, GC Logs, GC Pause, Throughput vs Latency (GC)
tags:
  - java
  - jvm
  - gc
  - memory
  - internals
  - deep-dive
---

# 288 — CMS (Concurrent Mark Sweep)

`#java` `#jvm` `#gc` `#memory` `#internals` `#deep-dive`

⚡ TL;DR — A low-pause Old Generation collector that performs most of its work concurrently with application threads, at the cost of CPU overhead and fragmentation.

| #288 | Category: Java & JVM Internals | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Old Generation, GC Roots, Stop-The-World (STW), Minor GC, Heap Memory | |
| **Used by:** | GC Tuning, GC Logs, GC Pause, Throughput vs Latency (GC) | |

---

### 📘 Textbook Definition

**CMS (Concurrent Mark Sweep)** is a JVM garbage collector for the Old Generation that minimises stop-the-world pauses by performing the marking and sweeping phases concurrently with the running application. It uses a tri-colour marking algorithm with two short STW phases (initial mark and remark) and two long concurrent phases (concurrent mark and concurrent sweep). CMS was deprecated in Java 9 and removed in Java 14, superseded by G1GC and ZGC.

### 🟢 Simple Definition (Easy)

CMS is a garbage collector that cleans up old objects mostly while your program keeps running, so your application barely notices the cleanup.

### 🔵 Simple Definition (Elaborated)

Traditional garbage collectors stop all application threads while they clean up memory. CMS instead does most of the work in the background while your application continues to run — only pausing briefly twice: once to take a snapshot of which objects are "root" objects, and once more to catch any changes made during the concurrent scan. This dramatically reduces pause times for latency-sensitive applications. The trade-off is CPU overhead and the inability to compact memory, which eventually leads to fragmentation.

### 🔩 First Principles Explanation

**Problem:** The Old Generation can grow to multiple gigabytes. Collecting it with a stop-the-world mark-compact algorithm (like Serial or Parallel GC) causes pauses of seconds — unacceptable for interactive or SLA-bound services.

**Constraint:** You can't scan the entire heap concurrently with zero synchronisation — application threads modify object references while the collector scans, potentially missing live objects (floating garbage) or, worse, collecting live objects (fatal).

**Insight:** The tri-colour invariant provides correctness for concurrent marking. Colour objects White (not yet seen), Grey (seen but children not scanned), or Black (fully processed). The invariant: a Black object must never point directly to a White object without a Grey object in the path. Application threads can create new references, but as long as the invariant is maintained via write barriers, the collector won't miss live objects.

**Solution (CMS Phases):**
1. **Initial Mark (STW):** Mark GC roots and direct references from Young Gen. Short pause — only scans roots.
2. **Concurrent Mark:** Traverse the object graph from grey objects. Application runs concurrently. Write barriers track mutations.
3. **Concurrent Preclean:** Process cards dirtied during Concurrent Mark to reduce Remark work.
4. **Remark (STW):** Re-scan objects modified during Concurrent Mark. Pause proportional to mutation rate.
5. **Concurrent Sweep:** Reclaim dead objects. No compaction — free space added to a free list.
6. **Concurrent Reset:** Prepare internal structures for next cycle.

The lack of compaction means free memory is fragmented. CMS uses a free-list allocator for Old Gen, making allocation slower and creating the risk of "promotion failure" when no contiguous free block is large enough, triggering a fallback Full GC with compaction.

### ❓ Why Does This Exist (Why Before What)

WITHOUT CMS (using Parallel Old GC):

- Old Generation collection causes 1–5 second STW pauses on multi-GB heaps.
- P99 latency SLAs (100ms) become impossible to meet.
- Batch spikes cause cascading timeout failures in microservice calls.

What breaks without it:
1. Latency-sensitive services (APIs, real-time bidding, financial transactions) miss SLAs during GC.
2. Load balancers may mark instances as unhealthy during long pauses, causing cascading failures.

WITH CMS:
→ P99 GC pauses typically drop from seconds to tens of milliseconds.
→ Application throughput available during concurrent phases (at ~20% CPU overhead cost).
→ Young Gen (Minor GC) still used; CMS only handles Old Gen.

### 🧠 Mental Model / Analogy

> Imagine cleaning a busy restaurant kitchen while cooks are still working. You can't stop the whole kitchen (that's a full STW GC). Instead: briefly announce "I'm starting cleaning, note where everything is" (Initial Mark), then clean most surfaces while cooks keep working (Concurrent Mark), then briefly shout "freeze!" again to catch anything moved since you started (Remark), then sweep without anyone stopping (Concurrent Sweep). The kitchen stays operational, but you can't rearrange the entire layout (no compaction) because cooks rely on items being where they are.

"Kitchen" = Old Generation, "cleaning" = GC, "rearranging layout" = compaction, "brief freeze" = STW pause, "working normally" = concurrent phase.

The analogy exposes CMS's core tension: concurrent clean is possible but compaction requires a full stop.

### ⚙️ How It Works (Mechanism)

**Write Barrier (Card Table):** When an application thread modifies an object reference, it marks the corresponding card (512-byte heap region) as dirty. During Remark, CMS scans dirty cards to find missed references.

```
CMS Phases Timeline
┌──────────────────────────────────────────────┐
│  [STW] Initial Mark  → very short            │
│  Concurrent Mark     → long, app runs        │
│  Concurrent Preclean → app runs              │
│  [STW] Remark        → short-medium          │
│  Concurrent Sweep    → long, app runs        │
│  Concurrent Reset    → app runs              │
└──────────────────────────────────────────────┘
```

**Fragmentation Problem:**
```
Before CMS sweep:
[LIVE][dead][LIVE][LIVE][dead][dead][LIVE]

After CMS sweep (no compact):
[LIVE][    ][LIVE][LIVE][         ][LIVE]

After many cycles (fragmented free list):
[LIVE][4B][LIVE][LIVE][8B][LIVE][LIVE][2B]
→ Request for 16B contiguous block FAILS
→ Promotion failure → Full GC STW compaction
```

**Enabling CMS (Java 8):**
```bash
java -XX:+UseConcMarkSweepGC \
     -XX:CMSInitiatingOccupancyFraction=70 \
     -XX:+UseCMSInitiatingOccupancyOnly \
     -XX:+CMSParallelRemarkEnabled \
     MyApp
```

`CMSInitiatingOccupancyFraction=70`: Start CMS when Old Gen is 70% full, leaving buffer for concurrent allocation before sweep completes.

### 🔄 How It Connects (Mini-Map)

```
Minor GC (Young Gen) → Promotion → Old Generation
                                        ↓
                              CMS Collector ← you are here
                              ┌─────────────────┐
                              │ Initial Mark STW │
                              │ Concurrent Mark  │
                              │ Remark STW       │
                              │ Concurrent Sweep │
                              └─────────────────┘
                                        ↓
                        Fragmentation → Promotion Failure
                                        ↓
                               Fallback Full GC
```

### 💻 Code Example

Example 1 — CMS configuration for a latency-sensitive service (Java 8):

```bash
java -Xms4g -Xmx4g \
     -XX:NewRatio=2 \
     -XX:+UseConcMarkSweepGC \
     -XX:CMSInitiatingOccupancyFraction=68 \
     -XX:+UseCMSInitiatingOccupancyOnly \
     -XX:+CMSParallelRemarkEnabled \
     -XX:+CMSScavengeBeforeRemark \
     -XX:ConcGCThreads=4 \
     -Xlog:gc*:file=gc.log:time,uptime \
     MyApp
```

Example 2 — Detecting CMS Concurrent Mode Failure in GC logs:

```
# BAD: This log line means CMS didn't finish before Old Gen filled
[GC (Allocation Failure) ...
[Full GC (Concurrent Mode Failure) ...]
# → Fallback to Serial Full GC = multi-second pause

# Root cause: CMSInitiatingOccupancyFraction set too high
# OR promotion rate too fast for concurrent sweep to keep up
```

Example 3 — Diagnosing fragmentation with jcmd:

```bash
# Check Old Gen usage and free list fragmentation
jcmd <pid> GC.heap_info

# Force histogram of live objects (careful in prod)
jcmd <pid> GC.class_histogram

# Better: use async-profiler or JFR for non-invasive analysis
jcmd <pid> JFR.start duration=60s filename=cms_diag.jfr
```

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| CMS is fully concurrent with zero STW pauses | CMS has two mandatory STW phases: Initial Mark and Remark. Only the long marking and sweeping phases are concurrent. |
| CMS is still recommended for new projects | CMS was deprecated in Java 9 and removed in Java 14. Use G1GC (default since Java 9) or ZGC/Shenandoah for low latency. |
| Concurrent Mode Failure means CMS is broken | It means the occupancy threshold was set too high or the allocation rate is too fast — it's a configuration problem, not a CMS bug. |
| CMS compacts memory like other collectors | CMS never compacts during a normal cycle. Only the emergency fallback Full GC compacts, which is far slower. |
| Increasing heap size fixes CMS fragmentation | Larger heaps delay but don't prevent fragmentation buildup; eventually promotion failure still occurs. |
| CMS and Parallel GC can be combined for Young Gen | Young Gen is always collected by ParNew (parallel minor GC) when CMS is enabled; the two are paired automatically. |
| The Remark pause is always short | Remark pause duration scales with the mutation rate and the number of dirty cards — high-churn applications can have significant Remark pauses. |

### 🔥 Pitfalls in Production

**1. Concurrent Mode Failure → Multi-Second Full GC**

```bash
# BAD: CMSInitiatingOccupancyFraction too high
-XX:CMSInitiatingOccupancyFraction=92
# → CMS starts too late, Old Gen fills before sweep completes
# → Falls back to STW Concurrent Mode Failure Full GC

# GOOD: Start early enough for concurrent sweep to complete
-XX:CMSInitiatingOccupancyFraction=68
-XX:+UseCMSInitiatingOccupancyOnly
# Rule of thumb: 70% is a common starting point;
# lower if promotion rate is high
```

**2. Fragmentation-Induced Promotion Failure**

```bash
# Symptom: Old Gen usage is below threshold but Full GC fires
# "promotion failed" in GC logs = no contiguous free block

# Mitigation 1: Reduce long-lived object count
# Mitigation 2: Run a manual Full GC during low-traffic window
# jcmd <pid> GC.run
# Mitigation 3: Migrate to G1GC which avoids fragmentation
-XX:+UseG1GC  # removes CMS fragmentation problem entirely
```

**3. Young Gen Promotion Rate Overwhelming Concurrent Sweep**

```bash
# Symptom: Frequent Concurrent Mode Failures despite low occupancy
# Root cause: Objects promoted from Young Gen faster than CMS sweeps

# GOOD: Slow down promotion by increasing Young Gen size
-XX:NewRatio=1  # equal Young and Old sizes
# Or: Use -XX:+CMSScavengeBeforeRemark to reduce floating garbage
-XX:+CMSScavengeBeforeRemark
```

**4. Remark Pause Spike Under High Write Rate**

```bash
# High-mutation apps (e.g., caches, message queues) dirty many cards
# → Remark must scan entire dirty card table → long STW

# GOOD: Enable parallel remark and preclean
-XX:+CMSParallelRemarkEnabled
-XX:+CMSPrecleaningEnabled
-XX:CMSPrecleaningMaxWaitDurationMs=200
```

### 🔗 Related Keywords

- `G1GC` — the replacement for CMS; region-based, concurrent, compacting.
- `ZGC` — sub-millisecond pause collector; full replacement for CMS in modern JVMs.
- `Stop-The-World (STW)` — the pause phases CMS minimises but cannot eliminate.
- `Old Generation` — the heap region CMS is responsible for collecting.
- `Throughput vs Latency (GC)` — the fundamental trade-off CMS optimises for (latency).
- `GC Pause` — the metric CMS targets for reduction.
- `GC Logs` — essential diagnostic tool for understanding CMS cycle behaviour.
- `Write Barrier` — the mechanism CMS uses to track mutations during concurrent marking.

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Concurrent Old Gen collector:             │
│              │ low pause, no compaction, deprecated.     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Maintaining Java 8 legacy systems         │
│              │ requiring low-latency GC understanding.   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ New projects — use G1GC or ZGC instead;   │
│              │ CMS removed in Java 14.                   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "CMS trades CPU for pause time,           │
│              │ then trades correctness for fragmentation."|
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ G1GC → ZGC → Shenandoah GC → GC Tuning   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A Java 8 service using CMS experiences Concurrent Mode Failure exactly once per day, always between 2–3 AM when batch jobs run. The Old Generation occupancy is at 85% before the failure. Lowering `CMSInitiatingOccupancyFraction` to 60% reduced failures for a week, but they returned. What two separate phenomena could explain why lowering the threshold helped initially but stopped working, and what would you investigate next?

**Q2.** CMS sweeps without compacting, while G1GC evacuates live objects to compact regions. Given that both run concurrently with application threads, why can G1GC compact while CMS cannot? What invariant does compaction violate when application threads are simultaneously updating object references, and how does G1GC's region-based approach work around it?

