---
layout: default
title: "GC Logs"
parent: "Java & JVM Internals"
nav_order: 293
permalink: /java/gc-logs/
number: "293"
category: Java & JVM Internals
difficulty: ★★☆
depends_on: G1GC, ZGC, Stop-The-World (STW), GC Pause, Heap Memory
used_by: GC Tuning, Throughput vs Latency (GC)
tags:
  - java
  - jvm
  - gc
  - observability
  - internals
---

# 293 — GC Logs

`#java` `#jvm` `#gc` `#observability` `#internals`

⚡ TL;DR — Structured JVM-generated logs recording every GC event, pause duration, and heap usage — essential for diagnosing memory and latency problems.

| #293 | Category: Java & JVM Internals | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | G1GC, ZGC, Stop-The-World (STW), GC Pause, Heap Memory | |
| **Used by:** | GC Tuning, Throughput vs Latency (GC) | |

---

### 📘 Textbook Definition

**GC Logs** are time-stamped diagnostic records emitted by the JVM for each garbage collection event, capturing information such as the collector type, collection cause, pause duration, heap occupancy before and after collection, and concurrent phase timings. In Java 9+, GC logging is controlled via the unified logging framework (`-Xlog:gc*`), which replaced the older `-verbose:gc` and `-XX:+PrintGCDetails` flags. GC logs are the primary observability tool for diagnosing GC-related latency spikes, memory leaks, and configuration issues.

### 🟢 Simple Definition (Easy)

GC logs are the JVM's diary of every memory cleanup event — recording when it happened, how long it took, and how much memory was freed.

### 🔵 Simple Definition (Elaborated)

Every time the JVM's garbage collector runs, it records what it did in GC logs. For each event you can see: the timestamp, which type of GC ran (Minor, Major, Full, concurrent), how long the application was paused, and how much memory was used before and after. With these logs you can tell whether your application has a memory leak, why latency spikes happen on a schedule, whether your heap sizing is correct, and whether Full GC is being triggered too often. GC log analysis is always step zero of any GC tuning effort.

### 🔩 First Principles Explanation

**Without GC logs:** GC problems manifest as P99 latency spikes, OOM crashes, and gradual performance degradation. Without logs, you're guessing at root causes. Changing GC flags without data is as useful as adjusting medicine dosage without knowing the patient's symptoms.

**What GC logs provide:**
- **Timing correlation:** A latency spike at 14:23:47 matches a Full GC pause at exactly 14:23:47 → root cause confirmed.
- **Heap occupancy trend:** If heap after GC increases by 1 MB per minute, you have a 1 MB/min leak.
- **Promotion rate:** How fast objects age from Young to Old Gen reveals whether tenuring threshold and Eden size are correct.
- **GC overhead:** `total_gc_time / elapsed_time × 100%` tells you what fraction of CPU is wasted on GC.
- **Concurrent mode failures:** Logged explicitly — tells you CMS/G1 didn't finish collecting before running out of space.

**Java 9+ Unified Logging:** The `-Xlog` framework replaced a dozen individual flags. The format is:
```
-Xlog:<what>:<where>:<decorators>:<output-options>
```
- `what`: tag/level selectors (e.g., `gc*`, `gc+heap=debug`)
- `where`: `stdout`, `file=path`
- `decorators`: `time`, `uptime`, `level`, `tags`

### ❓ Why Does This Exist (Why Before What)

WITHOUT GC Logs:

- GC events are invisible — you can only see their symptoms (latency, OOM).
- Tuning becomes trial-and-error — JVM flags changed without verification.
- Production incidents from GC take hours to diagnose because there's no evidence.

What breaks without it:
1. Memory leaks silently fill the heap over hours/days, undetected until OOM.
2. GC pause spikes in monitoring appear as "random latency events" without root cause.

WITH GC Logs:
→ Every pause correlated with a specific GC event in < 1 minute.
→ Heap occupancy trend detects leaks before they cause production incidents.
→ Tuning decisions validated with before/after data.

### 🧠 Mental Model / Analogy

> GC logs are the vital signs monitor in an ICU. Each time the JVM's GC runs, it writes an entry: time, event type, duration, and patient status (heap usage). Just as a doctor wouldn't change a patient's medication without checking vitals, you shouldn't change GC flags without reading the logs. The monitor doesn't intervene — it records.

"Vital signs" = heap usage and pause times, "ICU monitor" = GC log file, "doctor" = performance engineer, "medication change" = GC flag tuning.

Without the monitor running continuously, by the time you notice a problem, the evidence of its cause has already been overwritten.

### ⚙️ How It Works (Mechanism)

**Enabling GC Logging (Java 11+):**

```bash
# Comprehensive GC logging (recommended baseline)
-Xlog:gc*:file=gc-%t.log:time,uptime,level,tags:filecount=5,filesize=50m

# Breakdown:
# gc*          → all gc-related log entries
# file=gc-%t   → rotate by timestamp
# time,uptime  → wall-clock + JVM uptime timestamps
# filecount=5  → keep 5 rotated files
# filesize=50m → rotate at 50 MB
```

**Reading a G1GC Log Entry:**

```
[2025-05-02T10:00:01.234+0000][5.432s][info][gc,start]
  GC(42) Pause Young (Normal) (G1 Evacuation Pause)
[2025-05-02T10:00:01.289+0000][5.487s][info][gc     ]
  GC(42) Pause Young (Normal) 512M->180M(1024M) 54.3ms

Breakdown:
  GC(42)         → GC event number 42
  Pause Young    → Minor GC (Young Gen only)
  Normal         → routine collection
  512M->180M     → heap before→after collection
  (1024M)        → total heap capacity
  54.3ms         → stop-the-world pause duration
```

**Reading a Full GC Log Entry (Warning Sign):**

```
[10:05:23.456][info][gc] GC(100) Pause Full (Allocation Failure)
  2048M->1920M(2048M) 3234.7ms

→ Full GC: 3.2 second pause!
→ Only freed 128 MB from 2 GB heap → nearly full after GC
→ Root cause: memory leak or heap too small
```

**ZGC Log Entry:**

```
[0.500s][info][gc,start] GC(0) Garbage Collection (Warmup)
[0.500s][info][gc,task ] GC(0) Using 4 workers
[0.501s][info][gc      ] GC(0) Pause Mark Start 0.012ms
[0.512s][info][gc      ] GC(0) Concurrent Mark 10.234ms
[0.512s][info][gc      ] GC(0) Pause Mark End 0.018ms
[0.513s][info][gc      ] GC(0) Pause Relocate Start 0.015ms
[0.528s][info][gc      ] GC(0) Concurrent Relocate 15.1ms
```

### 🔄 How It Connects (Mini-Map)

```
Application running
       ↓
GC event triggers (Eden full, Old Gen threshold, etc.)
       ↓
   GC Logs ← you are here
   (records all events to file)
       ↓
Analysis tools:
  GCViewer | GCEasy.io | JDK Mission Control
       ↓
Insights → GC Tuning decisions
       ↓
Changed JVM flags → redeployment
```

### 💻 Code Example

Example 1 — Production-ready GC logging setup:

```bash
java \
  -Xms4g -Xmx4g \
  -XX:+UseG1GC \
  -XX:MaxGCPauseMillis=200 \
  -Xlog:gc*:file=/var/log/app/gc-%t.log:time,uptime,level,tags:filecount=10,filesize=100m \
  -XX:+HeapDumpOnOutOfMemoryError \
  -XX:HeapDumpPath=/var/log/app/heap.hprof \
  -jar app.jar
```

Example 2 — Parsing GC logs for pause distribution (bash):

```bash
# Extract all pause durations from G1GC log
grep "Pause" gc.log | awk '{print $(NF-0)}' | \
  sed 's/ms//' | sort -n | \
  awk '
    BEGIN {count=0; sum=0; max=0}
    {count++; sum+=$1; if($1>max) max=$1}
    END {
      print "Count:", count
      print "Avg:", sum/count "ms"
      print "Max:", max "ms"
    }'

# Count Full GC events (should be 0 in healthy service)
grep -c "Pause Full" gc.log
```

Example 3 — Using JFR for low-overhead GC monitoring:

```bash
# Java Flight Recorder: lower overhead than verbose GC logs
jcmd <pid> JFR.start \
  duration=300s \
  settings=profile \
  filename=/tmp/app_gc.jfr

# Analyse in JDK Mission Control (jmc)
# or command line:
jfr print --events GCHeapSummary,GarbageCollection app_gc.jfr
```

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| GC logs have significant performance overhead | In Java 9+ with async logging, GC log overhead is < 1%. Always enable them in production. |
| -verbose:gc gives detailed enough information | `-verbose:gc` is minimal and deprecated style; `-Xlog:gc*` gives far more diagnostic information. |
| Only Full GC events indicate problems | Excessive Minor GC or very high promotion rates visible in Young GC entries also indicate tuning needs. |
| GC logs are only useful during an incident | Continuous GC log collection enables trend analysis, proactive leak detection, and baseline establishment. |
| A large pause in GC logs always means Full GC | Long Young GC pauses can also occur with large Eden sizes or large evacuation sets in G1. |
| GCViewer/GCEasy can parse any JVM's GC format | GC log formats differ by JVM vendor and version; always specify the correct parser format. |

### 🔥 Pitfalls in Production

**1. Not Enabling GC Logs — Flying Blind**

```bash
# BAD: No GC logging — common in "default" microservice setups
java -jar app.jar

# GOOD: Always enable GC logging in production
java -Xlog:gc*:file=/logs/gc.log:time,uptime,level,tags \
     -jar app.jar
# Cost: < 1% overhead. Benefit: every GC incident diagnosable.
```

**2. GC Log Rotation Not Configured — Disk Full**

```bash
# BAD: Unbounded GC log file
-Xlog:gc*:file=/logs/gc.log

# GOOD: Rotate GC log files
-Xlog:gc*:file=/logs/gc.log:time,uptime:filecount=10,filesize=50m
# Keeps 10 files of 50 MB = max 500 MB disk usage
```

**3. Using Old-Style GC Flags on Java 11+**

```bash
# BAD: Java 8 style (ignored or errors on Java 11+)
-XX:+PrintGCDetails
-XX:+PrintGCDateStamps
-Xloggc:/logs/gc.log

# GOOD: Unified logging syntax (Java 9+)
-Xlog:gc*:file=/logs/gc.log:time,uptime,level,tags
```

### 🔗 Related Keywords

- `GC Tuning` — the activity that uses GC logs as its primary data source.
- `GC Pause` — the metric extracted and analysed from GC log entries.
- `G1GC` — the default collector whose log format to learn for most services.
- `ZGC` — produces a different (and simpler) log format reflecting its concurrent model.
- `Stop-The-World (STW)` — all pause durations in GC logs represent STW events.
- `Throughput vs Latency (GC)` — GC logs quantify exact throughput and latency trade-offs.

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ JVM event log for every GC: when, how    │
│              │ long, how much heap freed.                │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always — enable in production from day 1; │
│              │ essential for any GC diagnosis.           │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Synchronous logging on embedded/perf-     │
│              │ critical systems — use async mode or JFR. │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "GC logs are the black box recorder       │
│              │ of JVM memory health."                    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ GC Pause → GC Tuning → Safepoint → JFR   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your monitoring shows P99 request latency spikes to 500ms exactly every 4 minutes. GC logs show a Full GC with 3-second pause every 4 minutes, but heap-after-GC is consistently 1.2 GB out of a 2 GB max. Why is Full GC being triggered if heap is only 60% full after collection, and what three specific log entries would you look for to narrow down the root cause?

**Q2.** A DevOps teammate argues that GC logs should be disabled in production because they introduce latency overhead and increase container log volume. You know modern GC logging has < 1% overhead. Beyond the overhead argument, construct the strongest possible business case for always enabling GC logs in production, citing specific incident types where GC logs have been the only path to root cause.

