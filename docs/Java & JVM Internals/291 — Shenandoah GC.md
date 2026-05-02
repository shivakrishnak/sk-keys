---
layout: default
title: "Shenandoah GC"
parent: "Java & JVM Internals"
nav_order: 291
permalink: /java/shenandoah-gc/
number: "291"
category: Java & JVM Internals
difficulty: ★★★
depends_on: G1GC, ZGC, Stop-The-World (STW), Heap Memory, GC Roots
used_by: GC Tuning, GC Pause, Throughput vs Latency (GC)
tags:
  - java
  - jvm
  - gc
  - memory
  - internals
  - deep-dive
---

# 291 — Shenandoah GC

`#java` `#jvm` `#gc` `#memory` `#internals` `#deep-dive`

⚡ TL;DR — A concurrent, low-pause GC from Red Hat that uses Brooks forwarding pointers to relocate objects concurrently, decoupling pause time from heap size.

| #291 | Category: Java & JVM Internals | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | G1GC, ZGC, Stop-The-World (STW), Heap Memory, GC Roots | |
| **Used by:** | GC Tuning, GC Pause, Throughput vs Latency (GC) | |

---

### 📘 Textbook Definition

**Shenandoah GC** is an ultra-low-pause garbage collector developed by Red Hat, available in OpenJDK since Java 12. It achieves concurrent compaction by placing a *Brooks forwarding pointer* — an extra machine-word prepended to every object — that allows concurrent relocation without colored pointers. Shenandoah performs all major work (marking, evacuation, reference updating) concurrently with the application, targeting pause times under 10 milliseconds regardless of heap and live-set size.

### 🟢 Simple Definition (Easy)

Shenandoah GC moves objects around to compact memory while your application is still running, using an extra "forwarding address" stored with each object.

### 🔵 Simple Definition (Elaborated)

When the GC needs to move an object to defragment memory, it normally has to stop the whole application so no one reads the old location. Shenandoah adds a tiny pointer to the front of each object — pointing to the object's current location. When the GC has moved an object, it updates this forwarding pointer to the new address. Meanwhile, any application thread that reads the object checks the forwarding pointer first and automatically gets redirected. This lets the GC compact memory while the application keeps running, causing only brief pauses at the very start and end of each cycle.

### 🔩 First Principles Explanation

**The problem:** ZGC solves concurrent relocation via colored pointers in 64-bit addresses. But colored pointers only work on 64-bit platforms and require OS-level virtual memory tricks. Shenandoah takes a different approach that works on both 32-bit and 64-bit systems.

**Brooks Forwarding Pointer:** Every Java object in Shenandoah has an extra word prepended to the standard object layout. During normal operation, this word points to the object itself (a self-reference). When the GC relocates the object to a new address, the forwarding pointer at the old location is atomically updated to point to the new location.

```
Object before relocation:
Old address: [fwd→self][header][fields...]
               ↑ points to itself

Object after relocation:
Old address: [fwd→NEW][header][fields...]  (still accessible)
New address: [fwd→self][header][fields...] (new canonical home)
```

**Read barrier:** Unlike ZGC's load barrier (which fires on every pointer load), Shenandoah injects a read check on every object field access. Access goes through the forwarding pointer. Modern JITs optimise this to near-zero overhead for non-relocating phases.

**Concurrent Evacuation:** When a region is chosen for compaction, live objects are copied to new regions. While the evacuation is in progress, the old location's forwarding pointer is updated. Any subsequent access to the old address automatically redirects to the new copy. Multiple threads may race to copy an object, but only one wins via a CAS (Compare-And-Swap) on the forwarding pointer.

**Shenandoah vs ZGC comparison:**

| Aspect | Shenandoah | ZGC |
|---|---|---|
| Mechanism | Brooks forwarding pointer | Colored pointers |
| Overhead location | Per-object (extra word) | Per-reference read |
| Memory overhead | +1 word per object (~3-8%) | Pointer bit metadata |
| Platform | 32-bit and 64-bit | 64-bit only |
| Generational | Shenandoah 3.0 (experimental) | Java 21 (GA) |

### ❓ Why Does This Exist (Why Before What)

WITHOUT Shenandoah (using G1GC):

- Evacuation pauses scale with live-set size; at 32 GB live data, pauses reach 500ms+.
- Heap-size-dependent pause unpredictability violates P99 SLAs in batch+interactive mixed workloads.

What breaks without it:
1. Systems running mixed latency/throughput workloads can't use ZGC's colored pointer model on some platforms.
2. Applications that can't afford ZGC's throughput overhead (load barrier on every read) need an alternative.

WITH Shenandoah:
→ Pause times decoupled from heap size; typically < 10ms.
→ Works where ZGC's colored pointers are unavailable (some 32-bit or OS-constrained environments).
→ Available in OpenJDK standard builds; no special configuration needed.

### 🧠 Mental Model / Analogy

> Imagine you're forwarding mail for a friend who moved houses. You put a redirect sticker on their old mailbox (forwarding pointer). Mail carriers check the sticker first; if it says "now at new address," they deliver there instead. No mail is lost, and the post office didn't need to close (no stop-the-world) while you moved your friend's stuff to the new house.

"Old mailbox" = old object location, "redirect sticker" = Brooks forwarding pointer, "mail carriers checking sticker" = read barrier, "moving stuff" = concurrent evacuation.

The extra sticker on every mailbox has a small cost (memory overhead per object) but eliminates the need to stop the postal service during relocation.

### ⚙️ How It Works (Mechanism)

**Shenandoah Cycle Phases:**

```
Shenandoah GC Cycle
┌──────────────────────────────────────────────┐
│ [STW] Init Mark         → scan GC roots       │
│ Concurrent Mark         → traverse object graph│
│ [STW] Final Mark        → drain mark queues    │
│ Concurrent Cleanup      → account live data   │
│ Concurrent Evacuation   → copy objects         │
│ [STW] Init Update Refs  → ensure all see fwds │
│ Concurrent Update Refs  → update all pointers │
│ [STW] Final Update Refs → finalize             │
│ Concurrent Cleanup      → free old regions    │
└──────────────────────────────────────────────┘
STW phases: 4 pauses, each typically < 5ms
```

**Read Barrier Detail:**
```java
// Pseudo-code: what Shenandoah read barrier does
Object readField(Object obj, int fieldOffset) {
    Object ref = obj[fieldOffset];
    Object fwd = ref.forwardingPointer;
    if (fwd != ref) {
        // Object was relocated; use new location
        return fwd;
    }
    return ref; // fast path: object not relocated
}
```

### 🔄 How It Connects (Mini-Map)

```
CMS (no compaction, fragmentation)
        ↓ evolution
G1GC (regional, compaction during STW)
        ↓ parallel evolution
Shenandoah ← you are here  ←→  ZGC
(Brooks fwd pointer,              (colored pointers,
 concurrent evacuation)            load barriers)
        ↓
Future: Generational Shenandoah
```

### 💻 Code Example

Example 1 — Enabling Shenandoah GC:

```bash
# OpenJDK 12+ with Shenandoah
java -XX:+UseShenandoahGC \
     -Xms8g -Xmx8g \
     -XX:ShenandoahGCMode=normal \
     -Xlog:gc*:file=shen.log:time,uptime,level,tags \
     MyApp

# Shenandoah heuristic modes:
# normal  - default, balanced
# compact - more aggressive, higher CPU for lower footprint
# iu      - incremental update (alternative to SATB marking)
```

Example 2 — Shenandoah GC log interpretation:

```
[2.000s] GC(0) Pause Init Mark 1.234ms      ← brief STW
[2.001s] GC(0) Concurrent Mark 15.432ms     ← app running
[2.017s] GC(0) Pause Final Mark 2.100ms     ← brief STW
[2.019s] GC(0) Concurrent Evacuation 20.5ms ← app running
[2.040s] GC(0) Pause Init Update Refs 0.8ms ← brief STW
[2.041s] GC(0) Concurrent Update Refs 12.1ms← app running
[2.053s] GC(0) Pause Final Update Refs 1.2ms← brief STW
# Total STW: ~5ms. App pause: 4 brief interruptions
```

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Shenandoah and ZGC are the same collector | They solve the same problem with different techniques: Shenandoah uses Brooks forwarding pointers; ZGC uses colored pointers. They have different memory/throughput trade-offs. |
| Shenandoah is only available in Red Hat JDK | Shenandoah has been in mainline OpenJDK since Java 12 and is available in most OpenJDK distributions. |
| Brooks forwarding pointer doubles memory overhead | The overhead is one additional word (8 bytes) per object. Average Java objects are 32–128 bytes, so overhead is 5–25%. |
| Shenandoah is slower than G1GC overall | For latency-sensitive workloads, Shenandoah's P99 is dramatically better. For pure throughput batch, G1/Parallel GC may outperform it. |
| Shenandoah eliminates all GC pauses | It has 4 brief STW phases per cycle, but they're bounded by thread count and root count, not heap or live-set size. |

### 🔥 Pitfalls in Production

**1. Allocation Pacing Under High Allocation Rate**

```bash
# Shenandoah throttles allocation if GC can't keep pace
# Symptom: "Allocation Stall" or application slowdown

# GOOD: Provide ample heap headroom
-Xmx16g  # for a service with 6 GB live data

# Monitor: ShenandoahPacing* counters via JMX or JFR
```

**2. Write-Heavy Workloads Hit Concurrent Update Refs Phase Hard**

```bash
# Concurrent Update Refs must update every reference
# Heavy object mutation means more work in this phase
# Mitigation: use Shenandoah's "iu" (incremental update) mode
-XX:ShenandoahGCMode=iu
# Trades SATB for incremental update marking;
# better for high-mutation workloads
```

**3. Memory Overhead Underestimated for Object-Rich Workloads**

```bash
# Each object has +8 bytes forwarding pointer overhead
# 100 million small objects = +800 MB unexpected overhead
# Monitor actual heap with: jcmd <pid> GC.heap_info
```

### 🔗 Related Keywords

- `ZGC` — parallel development; similar latency goals, different mechanism.
- `G1GC` — regional predecessor that Shenandoah improves upon for latency.
- `Brooks Forwarding Pointer` — the core innovation enabling concurrent relocation.
- `GC Pause` — the metric Shenandoah targets to sub-10ms.
- `Stop-The-World (STW)` — minimised to 4 brief phases per Shenandoah cycle.
- `GC Tuning` — selecting between Shenandoah modes and heap sizing.

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Concurrent compaction via Brooks fwd ptr; │
│              │ pause time independent of heap/live size. │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Low-latency on mixed 32/64-bit platforms; │
│              │ alternative to ZGC on constrained envs.  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Memory-constrained systems (ptr overhead);│
│              │ pure throughput batch (use Parallel GC).  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Shenandoah puts a forwarding label on   │
│              │ every object so moving it is invisible."  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ ZGC → GC Tuning → GC Pause → GC Logs     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Shenandoah's Brooks forwarding pointer is updated via CAS (Compare-And-Swap) when an object is relocated. If two GC threads simultaneously try to evacuate the same object to different target addresses, only one CAS wins. What happens to the losing thread's copy of the object, and why is this race safe from a correctness standpoint?

**Q2.** Shenandoah adds one extra word to every object. ZGC encodes metadata in pointer bits. For a service with 500 million live short-lived objects averaging 40 bytes each, calculate the approximate memory overhead difference between the two approaches, and explain which workload characteristic would make you choose Shenandoah over ZGC despite the higher per-object overhead.

