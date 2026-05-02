---
layout: default
title: "Shenandoah GC"
parent: "Java & JVM Internals"
nav_order: 291
permalink: /java/shenandoah-gc/
number: "0291"
category: Java & JVM Internals
difficulty: ★★★
depends_on:
  - G1GC
  - ZGC
  - Stop-The-World (STW)
  - GC Roots
  - Memory Barrier
used_by:
  - GC Tuning
  - GC Pause
  - Throughput vs Latency (GC)
related:
  - ZGC
  - G1GC
  - GC Pause
  - Load Barrier
  - Brooks Pointers
tags:
  - jvm
  - garbage-collection
  - shenandoah
  - java-internals
  - low-latency
---

# 0291 — Shenandoah GC

## 1. TL;DR
> **Shenandoah GC** is a low-latency, concurrent garbage collector developed by Red Hat that achieves **sub-millisecond STW pauses** by performing heap compaction (object relocation) **concurrently** with running application threads. Unlike ZGC which uses colored pointers, Shenandoah uses **Brooks pointers** (forwarding pointers embedded in every object) to handle concurrent relocation. Available in OpenJDK since Java 12.

---

## 2. Visual: How It Fits In

```
Shenandoah GC — Concurrent Compaction via Brooks Pointers

Every heap object has an extra forwarding pointer:
┌──────────────────────────────────────────┐
│  Object Header                           │
│  ┌───────────────────────────────────┐   │
│  │  Brooks Pointer (self-pointer)    │   │ ← normally points to self
│  │  (becomes forwarding ptr on move) │   │   on relocation → new addr
│  └───────────────────────────────────┘   │
│  Class Pointer, fields...                │
└──────────────────────────────────────────┘

Normal access:      ref → Brooks ptr (self) → object data
After relocation:   ref → Brooks ptr (new addr) → moved object

App threads transparently follow forwarding pointers.
No STW needed for "fix all references" phase.
```

---

## 3. Core Concept

Shenandoah's approach to concurrent relocation differs from ZGC:

- **ZGC:** Metadata in pointer bits (colored pointers); requires load barriers on all pointer reads
- **Shenandoah:** Forwarding pointer in every object header (Brooks pointer); barriers intercept both reads AND writes to relocated objects

**Brooks Pointers:**
Each object in the heap has an extra word in its header — a Brooks pointer — that normally points to the object itself. When the GC relocates an object, it:
1. Copies the object to a new location
2. Updates the Brooks pointer in the OLD location to point to the NEW location
3. Application threads following the pointer are transparently redirected

**Result:** Concurrent compaction without STW "pointer fix-up" phase.

---

### Regions:

Like G1GC, Shenandoah uses a region-based heap. The concurrent collector selects a collection set of regions to compact, moves objects out, then marks old regions as free.

---

## 4. Why It Matters

Shenandoah and ZGC are the two production-grade sub-millisecond GC options in the JVM ecosystem. Shenandoah is:
- **Available in all mainstream OpenJDK builds** (Red Hat/Adoptium distributions)
- **The preferred choice** in enterprise Linux environments (RHEL-based JDKs)
- Proof that multiple architectural approaches (Brooks pointers vs colored pointers) can achieve the same latency goal

Understanding Shenandoah vs ZGC helps engineers make informed GC selection decisions.

---

## 5. Key Properties / Behavior Table

| Property | Value |
|----------|-------|
| Available since | Java 12 (OpenJDK) |
| Production status | Generally Available (not experimental) |
| STW pause target | < 1ms |
| Concurrent phases | Mark, Concurrent Evacuation, Concurrent Update References |
| Key mechanism | Brooks Pointers (forwarding pointers in object header) |
| Heap layout | Region-based (similar to G1) |
| Compaction | ✅ Yes (concurrent) |
| JVM flag | `-XX:+UseShenandoahGC` |
| Availability | OpenJDK (Red Hat, Adoptium); NOT in Oracle JDK |
| Barriers | Read + write barriers (heavier than ZGC read barrier only) |
| Throughput impact | ~10-20% vs Parallel GC (similar to ZGC) |

---

## 6. Real-World Analogy

> Shenandoah's approach is like a post office that needs to relocate packages to a new warehouse while deliveries are still happening. Instead of redrawing all delivery routes (updating all references), they leave a forwarding note at the old warehouse (Brooks pointer). Delivery trucks always check the note first — "is this still here or has it moved?" If moved, they follow the note to the new location. This forward-and-follow mechanism means packages can be relocated without stopping deliveries, but every delivery truck must check every note every time, adding slight overhead.

---

## 7. How It Works — Step by Step

```
Shenandoah GC Cycle:

Phase 1: Init Mark (STW < 1ms)
  - Snapshot GC Roots
  - Enable write barriers

Phase 2: Concurrent Mark (no STW)
  - Traverse heap from roots
  - Mark live objects in all regions
  - Track mutations via SATB-like write barriers

Phase 3: Final Mark (STW < 1ms)
  - Drain marking queues
  - Process weak references
  - Select Collection Set (highest garbage density regions)

Phase 4: Concurrent Cleanup (no STW)
  - Immediately reclaim 100% empty regions (no objects)

Phase 5: Concurrent Evacuation (no STW)
  - GC threads copy live objects from Collection Set to free regions
  - Install Brooks pointers at old locations pointing to new addresses
  - App threads accessing old objects → redirected via Brooks pointer

Phase 6: Init Update References (STW < 1ms)
  - Ensure all threads are not in the middle of reference traversal
  - Very short flip

Phase 7: Concurrent Update References (no STW)
  - Update all heap references to point directly to new locations
  - After this, Brooks pointers no longer needed for that cycle

Phase 8: Final Update References (STW < 1ms)
  - Update GC root references
  - Update all remaining roots

Phase 9: Concurrent Cleanup (no STW)
  - Reclaim Collection Set regions (now empty after evacuation)
```

---

## 8. Under the Hood (Deep Dive)

---

### Brooks Pointer overhead

```
Memory cost:
  Every object has an extra word (8 bytes on 64-bit)
  A system with 100M objects: 100M × 8 bytes = 800 MB overhead!
  
  Practical impact: ~5-10% memory overhead for typical workloads
  This is significant for memory-constrained environments

Performance cost:
  Every object access: 2 pointer dereferences instead of 1
  Read: ref → Brooks ptr → object  (1 extra deref)
  Write: must check Brooks ptr, possibly forward

Comparison with ZGC:
  ZGC: 1 extra conditional per READ (load barrier on 64-bit ptr)
  Shenandoah: 1 extra deref per access (Brooks ptr in header)
  Both have similar real-world overhead (~10-15%)
```

---

### Failure mode: Allocation stall

```
If Shenandoah GC cannot keep up with allocation rate:
  1. Pacing: GC asks allocation-heavy threads to slow down
     (adds delays to allocating threads proportional to GC backlog)
  2. Degenerated GC: STW, single-threaded GC of one region
     (similar to G1 evacuation failure, but per-region)
  3. Full GC: STW, complete heap collection
     (last resort, similar to other collectors)

Monitoring: Allocation stalls visible in GC logs
-Xlog:gc+ergo*:file=shenandoah.log:time,uptime
```

---

### Shenandoah traversal mode (experimental)

```
Alternative GC mode for very large heaps with pointer-dense workloads
- Uses a different marking algorithm (traversal, not SATB)
- More CPU-intensive but potentially more concurrent
- Enable: -XX:ShenandoahGCMode=traversal (experimental)
- Most production workloads should use default (passive/satb)
```

---

### Key tuning flags

```bash
-XX:+UseShenandoahGC
-XX:ShenandoahGCMode=satb        # Default mode (SATB marking)
-XX:ShenandoahGCHeuristics=adaptive  # Default heuristics
# Other heuristics: static, compact, aggressive

-XX:ShenandoahInitFreeThreshold=70   # Start GC when free < 70%
-XX:ShenandoahMinFreeThreshold=10    # Emergency GC when free < 10%
-XX:ShenandoahAllocationThreshold=2  # Start GC on 2% allocation spike
```

---

## 9. Comparison Table

| Feature | G1GC | ZGC | Shenandoah |
|---------|------|-----|------------|
| STW pauses | 50–200ms | < 1ms | < 1ms |
| Concurrent relocation | No (evacuation STW) | Yes (colored ptrs) | Yes (Brooks ptrs) |
| Object memory overhead | Low | Low | +8 bytes/object |
| Oracle JDK included | Yes | Yes | No (OpenJDK only) |
| RHEL/Adoptium JDK | Yes | Yes | Yes |
| Generational | Yes | Java 21+ | Experimental |
| Failure mode | Full GC (serial) | Stall | Degenerated/Full GC |

---

## 10. When to Use / Avoid

| Scenario | Guidance |
|----------|----------|
| OpenJDK (Red Hat/Adoptium) environments | ✅ Shenandoah is well-supported |
| Oracle JDK | ❌ Not included; use ZGC |
| Sub-ms latency requirements | ✅ Shenandoah works |
| Memory-constrained environments (< 1 GB heap) | Caution: Brooks ptr overhead |
| Choosing between Shenandoah and ZGC | Benchmark both; similar characteristics |

---

## 11. Common Pitfalls & Mistakes

```
❌ Expecting Shenandoah in Oracle JDK
   → Not included; available only in OpenJDK distributions
   → Use ZGC if on Oracle JDK and need sub-ms pauses

❌ Ignoring allocation stalls
   → Pacing (slowed allocation) is an early warning sign
   → Monitor and tune before degenerated GC occurs

❌ Very high object creation rate with small objects
   → Brooks pointer overhead is proportional to object count
   → Profile memory usage; consider object pooling

❌ Using -XX:ShenandoahGCHeuristics=aggressive in production
   → Aggressive mode triggers GC too frequently, wastes CPU
   → Use default adaptive heuristics
```

---

## 12. Code / Config Examples

```bash
# Basic Shenandoah for production
java -XX:+UseShenandoahGC \
     -Xms4g -Xmx8g \
     -Xlog:gc*:file=shenandoah.log:time,uptime \
     -jar service.jar

# Shenandoah with tuned heuristics
java -XX:+UseShenandoahGC \
     -XX:ShenandoahGCHeuristics=adaptive \
     -XX:ShenandoahInitFreeThreshold=60 \
     -XX:ShenandoahMinFreeThreshold=15 \
     -Xms8g -Xmx16g \
     -jar service.jar

# Checking Shenandoah is active
java -XX:+UseShenandoahGC -XX:+PrintCommandLineFlags -version
# Look for: -XX:+UseShenandoahGC

# Sample log output:
# Pause Init Mark 0.231ms
# Concurrent marking 1234.567ms
# Pause Final Mark 0.456ms
# Concurrent cleanup 45.678ms
# Concurrent evacuation 234.567ms
# Pause Init Update Refs 0.123ms
# Concurrent update references 567.890ms
# Pause Final Update Refs 0.234ms
```

---

## 13. Interview Q&A

**Q: What are Brooks pointers and how do they enable concurrent relocation?**
> A Brooks pointer is an extra word in every object's header that normally points to the object itself. When GC relocates an object, it copies the object to a new location and updates the Brooks pointer at the old location to point to the new location. Any code reading through the old reference transparently follows the Brooks pointer redirect, so the application never sees a stale reference. This allows concurrent object movement without freezing all threads for a "fix all references" phase.

**Q: How does Shenandoah differ from ZGC architecturally?**
> ZGC stores GC metadata in the upper bits of pointer values (colored pointers) and uses load barriers (intercepting reads). Shenandoah stores a forwarding pointer in each object header (Brooks pointer) and uses both read and write barriers. Both achieve sub-ms pauses, but Shenandoah has higher per-object memory overhead (+8 bytes) while ZGC has no per-object overhead. ZGC is available in Oracle JDK; Shenandoah is available in OpenJDK distributions only.

**Q: What is a "degenerated GC" in Shenandoah?**
> A degenerated GC is Shenandoah's intermediate failure mode. When the concurrent cycle cannot keep pace with allocation rate, Shenandoah first tries pacing (slowing allocating threads). If that's insufficient, it performs a degenerated GC — a single-region Stop-The-World collection of the most critical region. This is less severe than a Full GC but still causes an STW pause beyond the normal < 1ms target.

---

## 14. Flash Cards

| Front | Back |
|-------|------|
| What is a Brooks pointer? | Extra word in object header; normally self-pointer, becomes forwarding pointer on relocation |
| Shenandoah available in Oracle JDK? | No — OpenJDK distributions only (Red Hat, Adoptium) |
| Shenandoah failure mode order | Pacing → Degenerated GC → Full GC |
| Memory overhead of Brooks pointers | +8 bytes per object on 64-bit JVM |
| Shenandoah vs ZGC barrier type | Shenandoah: read+write barriers; ZGC: load barriers only |

---

## 15. Quick Quiz

**Question 1:** Which statement best describes Shenandoah GC's approach to concurrent object relocation?

- A) Uses colored bits in pointer values to track relocation
- B) ✅ Uses Brooks pointers (forwarding pointers in object headers) for transparent redirection
- C) Stops application threads briefly for each region evacuation
- D) Delays relocation until application threads are idle

**Question 2:** Shenandoah GC is available in:

- A) Oracle JDK only
- B) All JDK distributions
- C) ✅ OpenJDK distributions (Red Hat, Adoptium); NOT Oracle JDK
- D) Only GraalVM

---

## 16. Anti-Patterns

```
🚫 Anti-Pattern: Choosing Shenandoah without checking JDK distribution
   Problem:  Oracle JDK doesn't include Shenandoah
   Fix:      Verify JDK distribution; use Adoptium/OpenJDK, or switch to ZGC

🚫 Anti-Pattern: Deploying Shenandoah on very object-count-heavy workloads
   Problem:  Brooks pointer +8 bytes/object adds significant memory overhead
   Fix:      Profile memory; if overhead unacceptable, consider ZGC

🚫 Anti-Pattern: Ignoring GC pacing warnings
   Problem:  Pacing = allocation faster than GC; will degrade to STW
   Fix:      Investigate allocation rate; tune heap size or reduce allocations
```

---

## 17. Related Concepts Map

```
Shenandoah GC
├── key mechanism ───► Brooks Pointers (forwarding in headers)
├── compares to ─────► ZGC [#290] (colored pointers approach)
│                  ──► G1GC [#289] (concurrent marking, not relocation)
├── minimizes ───────► Stop-The-World (STW) [#285]
│                  ──► GC Pause [#294]
├── failure modes ───► Degenerated GC → Full GC [#284]
├── deployment ──────► OpenJDK, Red Hat JDK, Adoptium
└── tuned via ───────► GC Tuning [#292]
```

---

## 18. Further Reading

- [Shenandoah GC Wiki — OpenJDK](https://wiki.openjdk.org/display/shenandoah/Main)
- [JEP 189: Shenandoah GC](https://openjdk.org/jeps/189)
- [Shenandoah vs ZGC — Christine Flood (Red Hat)](https://shipilev.net/talks/javazone-Sep2018-shenandoah.pdf)
- [Aleksey Shipilev's Shenandoah deep dives](https://shipilev.net/talks/)

---

## 19. Human Summary

Shenandoah and ZGC are siblings in the low-latency GC space, solving the same problem with different mechanisms. Shenandoah uses Brooks pointers — an extra word per object that becomes a forwarding pointer on relocation — to transparently redirect accesses to moved objects. This is conceptually simpler than ZGC's colored pointer arithmetic but costs 8 bytes per object.

If you're in a Red Hat or Adoptium OpenJDK environment, Shenandoah is a first-class, well-supported option — especially given the deep investment Red Hat has made in it. If you're on Oracle JDK, ZGC is your path to sub-ms pauses. Both are valid answers to "we need GC to stop causing our latency SLA breaches."

---

## 20. Tags

`jvm` `garbage-collection` `shenandoah` `java-internals` `low-latency` `brooks-pointers` `openJDK`

