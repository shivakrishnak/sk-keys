---
layout: default
title: "GC Logs"
parent: "Java & JVM Internals"
nav_order: 293
permalink: /java/gc-logs/
number: "0293"
category: Java & JVM Internals
difficulty: ★★☆
depends_on:
  - G1GC
  - Full GC
  - Minor GC
  - Stop-The-World (STW)
  - GC Tuning
used_by:
  - GC Pause
  - GC Tuning
  - Throughput vs Latency (GC)
related:
  - GC Tuning
  - GC Pause
  - Throughput vs Latency (GC)
  - Observability
  - Safepoint
tags:
  - jvm
  - garbage-collection
  - observability
  - logging
  - java-internals
---

# 0293 — GC Logs

## 1. TL;DR
> **GC Logs** are the primary observability mechanism for JVM garbage collection. They record every GC event — pause durations, heap before/after, cause, throughput — and are essential for diagnosing performance problems, memory leaks, and GC policy violations. In Java 9+, unified logging (`-Xlog:gc*`) replaced the legacy `-XX:+PrintGCDetails` flags.

---

## 2. Visual: How It Fits In

```
Application → JVM → GC Events Occur → GC Logs Written
                                              │
              ┌───────────────────────────────┘
              ▼
   GC Log File (gc.log)
   [timestamp][level][tag] GC(N) Event Description metrics
              │
              ├──► Manual analysis (text grep)
              ├──► GCEasy (online analyzer)
              ├──► GCViewer (desktop app)
              └──► JVM Mission Control (JMC)
              └──► Prometheus/Grafana via jmx_exporter
```

---

## 3. Core Concept

GC logs provide a timestamped, structured record of:
- **What collection occurred** (Minor, Mixed, Full, Concurrent phases)
- **When** (timestamp from JVM start)
- **How long** the STW pause lasted
- **Heap usage** before and after (in MB)
- **Total heap size**
- **The cause** (Allocation Failure, GC Ergonomics, Explicit GC, etc.)

Starting Java 9, HotSpot uses **Unified Logging** (`-Xlog`), which provides consistent formatting, file rotation, and granular tag-based filtering across all GC algorithms.

---

## 4. Why It Matters

Without GC logs, diagnosing JVM performance is guesswork. With GC logs:
- Identify exact pause durations and their frequency
- Detect memory leaks (Old Gen trending upward over time)
- Diagnose Full GC storms (many Full GCs in a short window)
- Correlate GC events with application latency spikes
- Measure GC overhead (% of time in GC vs application)
- Validate that GC tuning changes had the desired effect

GC logs should be **always enabled in production** — the overhead is negligible (< 1%), and the diagnostic value is enormous.

---

## 5. Key Properties / Behavior Table

| Property | Value |
|----------|-------|
| Java 9+ flag | `-Xlog:gc*:file=gc.log:time,uptime,level,tags` |
| Legacy Java 8 flags | `-XX:+PrintGCDetails -XX:+PrintGCDateStamps -Xloggc:gc.log` |
| Log overhead | < 1% performance impact |
| File rotation | `-Xlog:gc*:file=gc.log:time:filecount=10,filesize=50m` |
| Log levels | `trace`, `debug`, `info`, `warning`, `error` |
| Useful tags | `gc`, `gc*` (all GC tags), `safepoint`, `gc+heap`, `gc+phases` |
| Analysis tools | GCEasy, GCViewer, JMC, gceasy CLI |
| Should be enabled in production? | Yes — always |

---

## 6. Real-World Analogy

> GC logs are like an airplane's black box flight recorder — lightweight and unobtrusive during normal operations, but invaluable when something goes wrong. You wouldn't fly a commercial aircraft without a flight recorder; you shouldn't run a production Java service without GC logs. They're small files that can prevent hours of production debugging.

---

## 7. How It Works — Step by Step

```
GC Log Generation:
1. Developer adds -Xlog:gc* flag at JVM startup
2. JVM initializes log file writer
3. For each GC event:
   a. JVM records timestamp
   b. Records GC type, cause, heap sizes, duration
   c. Writes log entry to file (async, low overhead)
4. Log file grows until rotation threshold
5. On rotation: gc.log.0, gc.log.1, ... gc.log.9 (ring buffer)

Log Analysis Workflow:
1. Download GC log from production server
2. Upload to GCEasy.io (or open in GCViewer/JMC)
3. Review: pause time distribution, GC type breakdown,
   heap utilization trend, GC overhead percentage
4. Identify bottleneck (frequent Minor GC? Long Full GC? Memory leak?)
5. Make targeted tuning change
6. Compare new log against baseline
```

---

## 8. Under the Hood (Deep Dive)

### Java 9+ Unified Logging format

```
Format: [timestamp][uptime][level][tag] GC(N) phase description sizes duration

[2025-05-02T10:15:32.123+0000][4.567s][info ][gc] GC(12) Pause Young (Normal) (G1 Evacuation Pause) 512M->128M(2048M) 45.234ms
│                               │       │      │   │                              │                     │                └ pause duration
│                               │       │      │   │                              │                     └ heap: before->after(total)
│                               │       │      │   │                              └ GC cause
│                               │       │      │   └ GC number (sequential)
│                               │       │      └ log tag
│                               │       └ log level
│                               └ JVM uptime
└ wall-clock timestamp
```

### Useful -Xlog tag combinations

```bash
# All GC info (most common)
-Xlog:gc*:file=gc.log:time,uptime

# Include safepoint events (diagnose TTSP)
-Xlog:gc*,safepoint*:file=gc.log:time,uptime

# G1 detailed phases
-Xlog:gc+phases=debug:file=gc.log:time,uptime

# Heap utilization after each GC
-Xlog:gc+heap=debug:file=gc.log:time,uptime

# All details (verbose — use for debugging, not production)
-Xlog:gc*=trace:file=gc.log:time,uptime

# File rotation (10 files, 50 MB each = max 500 MB)
-Xlog:gc*:file=gc.log:time,uptime:filecount=10,filesize=50m
```

### Legacy Java 8 equivalent flags

```bash
# Java 8 GC logging (legacy, not recommended)
-XX:+PrintGC
-XX:+PrintGCDetails
-XX:+PrintGCDateStamps
-XX:+PrintGCTimeStamps
-XX:+PrintTenuringDistribution
-Xloggc:/opt/logs/gc.log
-XX:+UseGCLogFileRotation
-XX:NumberOfGCLogFiles=10
-XX:GCLogFileSize=50m

# Note: These flags are REMOVED in Java 9+
# Use -Xlog:gc* instead
```

### Interpreting key log entries

```
G1GC Normal Collection:
[info][gc] GC(5) Pause Young (Normal) (G1 Evacuation Pause) 512M->64M(2048M) 35.456ms
Meaning: Minor GC #5; evacuated 512MB→64MB in 2048MB heap; 35ms pause

G1GC Concurrent Marking:
[info][gc] GC(6) Concurrent Mark Cycle
[info][gc] GC(6) Pause Remark 64M->64M(2048M) 5.123ms
Meaning: Concurrent marking happening (no pause), then brief Remark (5ms STW)

Full GC (bad!):
[info][gc] GC(42) Pause Full (Allocation Failure) 2040M->512M(2048M) 4567.890ms
Meaning: Full GC #42 due to allocation failure; collected 2040→512MB; 4.5 SECOND pause!

Memory Leak Signal (Old Gen trending up):
GC(10): 200M->180M old
GC(20): 300M->280M old
GC(30): 400M->380M old
← each GC reclaims same amount but baseline grows = memory leak
```

### GC log analysis metrics

```
Key metrics to extract from GC logs:

1. Pause time distribution:
   - Min/Avg/Max/P99/P999
   - Distribution: how many < 50ms, 50-100ms, > 100ms

2. GC frequency:
   - Minor GC rate (per minute)
   - Full GC rate (should be 0 or near-0)

3. GC overhead:
   - Total time in GC / total elapsed time
   - Alert threshold: > 5%

4. Heap utilization trend:
   - After each GC: is Old Gen steady or growing?
   - Growing = memory leak

5. Allocation rate:
   - Bytes allocated between GC events / time
   - High rate → consider allocation profiling
```

---

## 9. Comparison Table

| Setting | Java 8 | Java 9+ |
|---------|--------|---------|
| Basic GC logging | `-XX:+PrintGC` | `-Xlog:gc` |
| Detailed GC | `-XX:+PrintGCDetails` | `-Xlog:gc*` |
| Timestamps | `-XX:+PrintGCDateStamps` | `:time,uptime` decorators |
| File rotation | `-XX:+UseGCLogFileRotation` | `:filecount=N,filesize=Nm` |
| All-in-one | Multiple flags | `-Xlog:gc*:file=gc.log:time,uptime` |
| Available in Java 17? | ❌ Removed in Java 9 | ✅ |

---

## 10. When to Use / Avoid

| Scenario | Guidance |
|----------|----------|
| Production services | ✅ Always enable GC logging (< 1% overhead) |
| Load testing | ✅ Essential for performance baseline |
| Development | Optional; enable when debugging GC behavior |
| Container environments | Write to `/dev/stdout` or a mounted volume |
| Microservices | Short-lived pods: log to stdout for aggregation |

---

## 11. Common Pitfalls & Mistakes

```
❌ Not enabling GC logging in production
   → When GC problems cause incidents, no forensic data available

❌ Using Java 8 -XX:PrintGC* flags on Java 11+
   → Flags silently ignored on Java 9+; use -Xlog:gc*

❌ Not configuring file rotation
   → GC log grows unbounded → disk exhaustion

❌ Logging too much (gc*=trace) in production
   → Excessive I/O; logging overhead becomes significant

❌ Analyzing raw GC logs manually instead of using tools
   → Error-prone; miss patterns; use GCEasy/GCViewer

❌ Treating GC log gaps as "no GC events"
   → Gaps may indicate log file rotation or disk full
```

---

## 12. Code / Config Examples

```bash
# Production-ready GC logging configuration (Java 11+)
-Xlog:gc*:file=/opt/logs/gc.log:time,uptime,level,tags:filecount=10,filesize=50m

# Development / debugging (more verbose)
-Xlog:gc*=debug:file=gc-debug.log:time,uptime,level,tags

# Container environment (log to stdout)
-Xlog:gc*::time,uptime

# Add safepoint logging
-Xlog:gc*,safepoint*:file=/opt/logs/gc.log:time,uptime,level,tags:filecount=10,filesize=50m

# Analyze logs with GCEasy CLI (https://github.com/GCeasy/gceasy-command-line-tool)
gceasy analyze gc.log

# Download analysis from GCEasy API
curl -X POST https://api.gceasy.io/analyzeGC \
  -H "Content-Type: multipart/form-data" \
  -F "file=@gc.log" \
  -F "apiKey=YOUR_API_KEY"
```

```java
// JMX-based GC monitoring programmatically
import java.lang.management.*;
import java.util.*;

public class GCMonitor {
    public static void printGCStats() {
        List<GarbageCollectorMXBean> gcBeans =
            ManagementFactory.getGarbageCollectorMXBeans();
        
        for (GarbageCollectorMXBean gc : gcBeans) {
            System.out.println("GC Name: " + gc.getName());
            System.out.println("  Collection Count: " + gc.getCollectionCount());
            System.out.println("  Collection Time (ms): " + gc.getCollectionTime());
        }
    }
}
```

---

## 13. Interview Q&A

**Q: How do you enable GC logging in Java 11+?**
> Use the Unified Logging syntax: `-Xlog:gc*:file=gc.log:time,uptime,level,tags`. For production with rotation: `-Xlog:gc*:file=gc.log:time,uptime:filecount=10,filesize=50m`. The legacy Java 8 flags (`-XX:+PrintGCDetails`, etc.) are not available in Java 9+.

**Q: How do you detect a memory leak from GC logs?**
> Look at Old Gen size after each GC. In healthy applications, Old Gen usage is stable or slightly oscillating. A memory leak shows a consistent upward trend: each GC leaves more live objects in Old Gen than the previous one. The baseline keeps rising until OOM.

**Q: What's the overhead of enabling GC logging in production?**
> Negligible — typically < 1% of application throughput and latency. GC log entries are written asynchronously. The benefit of having diagnostic data when problems occur far outweighs the cost. Always enable GC logging in production.

---

## 14. Flash Cards

| Front | Back |
|-------|------|
| Java 9+ GC logging flag | `-Xlog:gc*:file=gc.log:time,uptime` |
| Java 8 GC details flag (NOT for Java 9+) | `-XX:+PrintGCDetails -Xloggc:gc.log` |
| Free GC log analysis tool | GCEasy (gceasy.io), GCViewer |
| Memory leak indicator in GC logs | Old Gen baseline rising after each GC |
| How to detect Full GC in logs | `Pause Full` in log entry |

---

## 15. Quick Quiz

**Question 1:** You notice in GC logs that after every Full GC, Old Gen usage is: 200MB, 240MB, 280MB, 320MB. What does this indicate?

- A) G1GC is working correctly
- B) Young Gen is too small
- C) ✅ Memory leak — Old Gen baseline is increasing each cycle
- D) Full GC frequency is too high

**Question 2:** Which JVM flag collects comprehensive GC data including phase-level detail in Java 17?

- A) `-XX:+PrintGCDetails`
- B) `-verbose:gc`
- C) ✅ `-Xlog:gc*:file=gc.log:time,uptime`
- D) `-XX:+PrintGCDateStamps`

---

## 16. Anti-Patterns

```
🚫 Anti-Pattern: Missing GC logs during production incident
   Problem:  Can't determine if GC caused the latency spike
   Fix:      Always enable GC logging; treat it as mandatory production config

🚫 Anti-Pattern: Writing GC logs to a slow NFS mount
   Problem:  Log I/O competes with application I/O; inflates GC overhead
   Fix:      Use local SSD or tmpfs for GC log directory

🚫 Anti-Pattern: Unbounded GC log file
   Problem:  Log fills disk over hours/days → OOM or disk full killing JVM
   Fix:      Always configure: filecount=10,filesize=50m (or similar)
```

---

## 17. Related Concepts Map

```
GC Logs
├── records ─────────► Minor GC [#282]
│                  ──► Major GC [#283]
│                  ──► Full GC [#284]
├── configured for ──► G1GC [#289]
│                  ──► ZGC [#290]
│                  ──► Shenandoah GC [#291]
├── analyzed by ─────► GCEasy, GCViewer, JMC
├── feeds into ──────► GC Tuning [#292]
│                  ──► GC Pause [#294]
└── part of ─────────► Observability & SRE
```

---

## 18. Further Reading

- [JEP 158: Unified JVM Logging](https://openjdk.org/jeps/158)
- [Java 11 Unified Logging Reference](https://docs.oracle.com/en/java/javase/11/tools/java.html#GUID-3B1CE181-CD30-4178-9602-230B800D4FAE)
- [GCEasy — Free GC Log Analyzer](https://gceasy.io)
- [GCViewer GitHub](https://github.com/chewiebug/GCViewer)
- [JVM Mission Control](https://www.oracle.com/java/technologies/jdk-mission-control.html)

---

## 19. Human Summary

GC logs are the black box of your JVM. They answer "what actually happened during that latency spike at 3 AM?" without requiring you to be present. Enabling them costs essentially nothing — but not having them costs enormously when things go wrong.

The shift from Java 8's scattered `-XX:+PrintGC*` flags to Java 9+'s unified `-Xlog:gc*` syntax cleaned up a decade of flag proliferation. Modern GC logging gives you one flag, one format, file rotation, and consistent output across all collectors. Use it always, configure rotation, and have GCEasy or GCViewer bookmarked for the inevitable "something is slow and we need to understand why."

---

## 20. Tags

`jvm` `garbage-collection` `observability` `logging` `java-internals` `gc-analysis` `monitoring`

