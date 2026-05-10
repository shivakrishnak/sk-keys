---
id: JCC-069
title: "Memory Visibility Diagnostics (jstack, JFR)"
category: Java Concurrency
tier: tier-3-java
folder: JCC-java-concurrency
difficulty: ★★★
depends_on: JCC-067, JCC-068, JCC-066
used_by:
related: JCC-042, JCC-046, JCC-024
tags:
  - java
  - concurrency
  - observability
  - advanced
  - diagnosis
status: complete
version: 2
layout: default
parent: "Java Concurrency"
grand_parent: "Technical Dictionary"
nav_order: 69
permalink: /java-concurrency/memory-visibility-diagnostics-jstack-jfr/
---

# JCC-069 - MEMORY VISIBILITY DIAGNOSTICS (JSTACK, JFR)

⚡ **TL;DR** - Use `jstack` for thread state snapshots and JFR
for continuous concurrent-event recording to diagnose deadlocks,
lock contention, thread pinning, and memory visibility bugs in
production JVMs.

---

| Field      | Value                                              |
|------------|----------------------------------------------------|
| Depends on | JCC-067 JMM Happens-Before, JCC-068 Lock-Free Data Structures, JCC-066 Thread Pinning |
| Used by    | (advanced diagnostics endpoint)                    |
| Related    | JCC-042 Atomic Classes, JCC-046 Thread Dump Analysis, JCC-024 Java Memory Model |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A Java service degrades under load. Threads block, throughput drops,
latency spikes. The developer has no view into which lock is
contended, which thread is holding it, or whether visibility bugs
cause data corruption. `System.out.println` debugging is useless
at production concurrency levels where the observation changes the
behaviour (Heisenberg effect).

**THE BREAKING POINT:**
A service handles 500k requests/second. Occasionally response times
spike to 5 seconds. Adding more threads makes it worse. Thread
dumps taken during a spike show 400 threads BLOCKED on the same
monitor. But which call site holds the lock, and why it occasionally
takes 5 seconds, is invisible without instrumentation.

**THE INVENTION MOMENT:**
`jstack` (JDK 1.5+) dumps all thread states and their stack traces
at a moment in time - revealing which thread holds which lock and
which threads wait for it. Java Flight Recorder (JFR, Java 11+,
originally JDK commercial) records lock events, GC events,
allocation rates, and thread pinning events continuously with <1%
overhead - replacing the need for sampling profilers in many cases.

**EVOLUTION:**
- **JDK 1.5:** `jstack` - thread dump tool
- **JDK 1.6:** `jmap`, `jcmd` - heap dump, JVM diagnostics
- **JDK 11:** JFR open-sourced (previously commercial in JDK 8)
- **JDK 14+:** JFR streaming API - real-time event consumption
- **JDK 21:** New JFR events for virtual threads, pinning, structured
  concurrency

---

### 📘 Textbook Definition

**`jstack`** is a JDK tool that prints a Java thread dump to stdout:
all threads, their states (RUNNABLE, BLOCKED, WAITING, TIMED_WAITING),
their call stacks, and lock ownership/waiting relationships.

**Java Flight Recorder (JFR)** is a low-overhead profiling and
diagnostics framework built into the JVM that continuously records
JVM events (GC, JIT, CPU, threads, locks, I/O, allocations) into
`.jfr` binary files, analysable with JDK Mission Control (JMC).

**Key concurrency events in JFR:**
- `jdk.JavaMonitorWait` - `Object.wait()` calls
- `jdk.JavaMonitorBlocked` - lock acquisition blocked
- `jdk.JavaMonitorInflated` - monitor promoted from thin to fat lock
- `jdk.VirtualThreadPinned` - virtual thread pinning events
- `jdk.ThreadPark` - `LockSupport.park()` calls (ReentrantLock)

---

### ⏱️ Understand It in 30 Seconds

**One line:** `jstack` is a snapshot of all threads right now; JFR
is a continuous recording of everything that happened.

**One analogy:**
> `jstack` is a photograph of a highway taken at one moment - you
> see which cars are stopped and where. JFR is a dashcam recording
> of the entire journey - you can replay exactly when and where
> the traffic jam formed, for how long, and which car caused it.

**One insight:** `jstack` is best for responding to an active
problem (take multiple snapshots 5 seconds apart). JFR is best for
post-mortem analysis of production incidents that resolves itself
before you notice.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. `jstack` attaches to a running JVM via pid or sends a signal;
   the JVM outputs thread states at that instant without stopping
   production traffic.
2. JFR uses a fixed-size circular buffer in the JVM; old events
   are overwritten. Can be dumped on-demand during an incident.
3. JFR's lock event threshold: by default, events are captured when
   blocking exceeds 10ms. Configure down to 1ms for detailed analysis.
4. Thread state at `jstack` snapshot time is authoritative: BLOCKED
   = waiting for monitor; WAITING = `Object.wait()` or `park()`;
   TIMED_WAITING = sleep/timed-wait.
5. Memory visibility bugs (wrong values) are NOT directly visible
   in jstack/JFR - they appear as incorrect behaviour. JFR's
   happens-before violation detection requires JCStress.

**DERIVED DESIGN:**
JFR uses a low-overhead binary event format. The JIT compiler
inserts probes at synchronisation points; most events have zero
overhead when not being consumed. Only events crossing the recording
threshold are written.

**THE TRADE-OFFS:**

**Gain:** Production-safe continuous monitoring; post-mortem
analysis; exact lock ownership chains; JIT compilation details.

**Cost:** JFR file analysis requires JDK Mission Control (GUI);
`jstack` is a momentary snapshot and may miss intermittent issues;
very brief lock contention (sub-millisecond) is invisible at default
thresholds.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

**Essential:** Diagnosing concurrent systems requires observing
thread interaction over time - point-in-time tools miss transient
issues.

**Accidental:** JFR analysis requires learning JMC or scripting
the JFR API; `jstack` output format differs across JVM vendors.

---

### 🧪 Thought Experiment

**SETUP:** A service occasionally hangs for 10 seconds then
recovers. No exception is thrown. RPS drops to zero during the hang.

**WHAT HAPPENS WITHOUT diagnostics:**
The team restarts the service on every hang. Root cause unknown.
It recurs. Customer escalation. Eventually, a developer guesses
it is a GC pause or database lock, but cannot prove it.

**WHAT HAPPENS WITH jstack + JFR:**
```
1. Enable JFR with -XX:StartFlightRecording=settings=default
2. Next hang: jstack <pid> -> shows 200 threads BLOCKED on
   com.example.UserService.getUser()
3. JFR dump shows: 10 second pause for JavaMonitorBlocked on
   UserService$sessionCache (same timestamp)
4. JFR shows GCBefore: GC pause = 0ms (not the cause)
5. Root cause: UserService.getUser() calls an external HTTP API
   inside synchronized with a 10-second timeout.
```

**THE INSIGHT:** The hang was a synchronized block around an HTTP
call - lock held for 10 seconds waiting for a slow external service.
`jstack` showed who was blocking; JFR showed duration and timing.

---

### 🧠 Mental Model / Analogy

> A hospital incident debrief (JFR) vs a snapshot of the ER right
> now (jstack). The debrief reviews every patient admission, every
> nurse movement, every equipment request over 4 hours to find when
> the bottleneck occurred and why. The ER snapshot shows only current
> waiting patients - useful for triage but not for root cause.

**Element mapping:**
- Patient admission records = JFR event records
- Current patient waiting line = thread states in jstack
- Bottleneck nurse = lock-holding thread
- Patient waiting = BLOCKED thread
- Debrief report = JMC flight recording analysis
- Snapshot of ER = `jstack` output

Where this analogy breaks down: jstack has microsecond resolution
for the current instant; JFR events have configurable thresholds -
very short lock waits (sub-ms) are invisible at default settings.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Tools that let you look inside a running Java program to see which
threads are blocked waiting for each other and why.

**Level 2 - How to use it (junior developer):**
```bash
# Get pid
jps -l
# Output: 12345 com.example.MyApp

# Take thread dump
jstack 12345 > thread_dump.txt

# Start JFR recording
jcmd 12345 JFR.start name=diagnosis \
    settings=default duration=60s \
    filename=diag.jfr
```

**Level 3 - How it works (mid-level engineer):**
`jstack` sends a `SIGQUIT` signal (Unix) or uses the JVM's Attach
API (all platforms) to trigger a safe-point dump. The JVM pauses
at a safepoint to collect consistent thread state, then writes the
dump. Safepoint pause usually <5ms.

JFR probes are inserted at bytecode level by the JIT. `monitorenter`
gets a probe that starts a timer; on exit, if elapsed > threshold,
an event is written to the per-thread buffer. Buffers are flushed
to the global ring buffer periodically.

**Level 4 - Why it was designed this way (senior/staff):**
JFR's per-thread buffer design avoids write contention on a shared
event store. Each thread writes to its own buffer; a background
thread periodically merges buffers into the circular file. This is
the same design as high-performance loggers (Log4j AsyncAppender,
SLF4J async), optimised for zero-overhead event production with
bounded-overhead consumption.

**Expert Thinking Cues:**
- Take 3 jstack dumps 5 seconds apart. Threads still BLOCKED in
  all 3 = long contention, not intermittent.
- JFR `jdk.JavaMonitorBlocked` event includes: thread, lock class,
  lock owner thread, duration, stack trace - everything needed.
- `async-profiler` (open source) provides CPU, lock, and allocation
  profiling with flame graph output, often superior to JFR for
  CPU-bound investigation.
- Virtual thread pinning: `jdk.VirtualThreadPinned` event in JFR.
  Threshold default = 20ms; set to 1ms in development.

---

### ⚙️ How It Works (Mechanism)

**`jstack` flow:**
```
jstack <pid>
  |
  Attach to JVM via /proc/<pid>/fd or Windows ToolsAPI
  |
  JVM: trigger safepoint
  JVM: collect thread states (BLOCKED/WAITING/RUNNABLE)
  JVM: collect lock ownership and wait lists
  |
  Write thread dump text to stdout
  |
  Resume JVM (safepoint ends)
```

**JFR event lifecycle:**
```
JIT-compiled monitorenter probe fires
  |
  Event timer starts (CPU timestamp)
  |
monitorenter succeeds (lock acquired)
  |
  Elapsed > threshold (10ms default)?
    NO: discard
    YES: write event to thread-local buffer
  |
Background thread drains buffers -> circular file
  |
jcmd <pid> JFR.dump filename=out.jfr
  |
  Open in JDK Mission Control for analysis
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW (diagnosing contention incident):**
```
Alert: P95 latency > 5s         <- YOU ARE HERE
       |
  jcmd <pid> JFR.start settings=default
       |
  Wait for incident to recur (or use existing recording)
       |
  jcmd <pid> JFR.dump filename=incident.jfr
       |
  Open in JDK Mission Control
       |
  Thread view: filter JavaMonitorBlocked > 1s
       |
  Identify: method, lock class, lock owner, duration
       |
  Cross-ref: GC events same time window?
       |
  Root cause: heavy synchronized + I/O, GC pause, etc.
       |
  Fix and verify: disable contention in JFR recording
```

**FAILURE PATH:**
JFR file not started before incident -> no data captured ->
retroactive diagnosis impossible.

**WHAT CHANGES AT SCALE:**
- Large JFR files (30min at default settings = ~100MB) require JMC
  or scripting. Use `jfr print --events JavaMonitorBlocked`
  CLI for quick triage without JMC.
- In Kubernetes: JFR dump commands must reach the pod; use
  `kubectl exec` + `jcmd` inside the container.

---

### 💻 Code Example

**Using jstack (command line):**
```bash
# 1. Find pid
jps -l
# 42173 com.example.MyApplication

# 2. Take thread dump
jstack -l 42173 2>&1 | tee dump_$(date +%s).txt

# 3. Find BLOCKED threads
grep -A5 "BLOCKED" dump_*.txt

# 4. Find deadlock summary
grep -A20 "Found.*deadlock" dump_*.txt

# Example jstack BLOCKED output:
# "http-nio-8080-exec-1" #24 daemon prio=5 os_prio=0 tid=...
#    java.lang.Thread.State: BLOCKED (on object monitor)
#    at com.example.UserService.getUser(UserService.java:45)
#    - waiting to lock <0x0000000710a2d840> (a java.util.HashMap)
#    - locked by "http-nio-8080-exec-5" at UserService.java:67
```

**Enabling JFR programmatically:**
```java
import jdk.jfr.Recording;
import jdk.jfr.consumer.RecordingStream;

// One-shot recording:
try (Recording rec = new Recording()) {
    rec.enable("jdk.JavaMonitorBlocked")
        .withThreshold(Duration.ofMillis(1));
    rec.enable("jdk.VirtualThreadPinned")
        .withThreshold(Duration.ofMillis(1));
    rec.start();

    // ... run test workload ...

    rec.dump(Path.of("incident.jfr"));
}

// Streaming API - real-time analysis:
try (RecordingStream rs = new RecordingStream()) {
    rs.enable("jdk.JavaMonitorBlocked")
        .withThreshold(Duration.ofMillis(100));
    rs.onEvent("jdk.JavaMonitorBlocked", event -> {
        System.out.printf("BLOCKED: %s on %s for %dms%n",
            event.getThread("eventThread").getJavaName(),
            event.getClass("monitorClass").getName(),
            event.getDuration("duration").toMillis());
    });
    rs.startAsync();
    // Consumes events in background
}
```

**Useful jcmd commands:**
```bash
# Start JFR with lock profiling
jcmd <pid> JFR.start \
    name=lockcheck \
    settings=profile \
    duration=120s \
    filename=lock.jfr

# Dump current recording
jcmd <pid> JFR.dump filename=now.jfr

# Check recording status
jcmd <pid> JFR.check

# Stop recording
jcmd <pid> JFR.stop name=lockcheck

# Analyse from CLI without JMC
jfr print --events JavaMonitorBlocked lock.jfr | head -100

# Thread dump via jcmd (alternative to jstack)  
jcmd <pid> Thread.print -l
```

**How to verify / test:**
```java
@Test
void lockContentionIsDetectedByJFR() throws Exception {
    var lock = new Object();
    CountDownLatch start = new CountDownLatch(1);
    var holder = new Thread(() -> {
        synchronized (lock) {
            try {
                start.countDown();
                Thread.sleep(500); // hold for 500ms
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
    });

    try (Recording rec = new Recording()) {
        rec.enable("jdk.JavaMonitorBlocked")
            .withThreshold(Duration.ofMillis(1));
        rec.start();

        holder.start();
        start.await();

        // Try to acquire while holder holds it
        synchronized (lock) {} // blocks ~500ms

        rec.stop();
        List<RecordedEvent> events =
            RecordingFile.readAllEvents(
                rec.getDestination());

        assertThat(events).anyMatch(e ->
            e.getEventType().getName()
                .equals("jdk.JavaMonitorBlocked"));
    }
    holder.join();
}
```

---

### ⚖️ Comparison Table

| Tool | Type | Overhead | Best for |
|------|------|---------|---------|
| `jstack` | Snapshot | Low (<10ms pause) | Active deadlock, BLOCKED threads |
| JFR | Continuous recording | <1% | Lock events, GC, pinning, post-mortem |
| `jmap` | Heap dump | High (full pause) | OOM, memory leak investigation |
| `async-profiler` | CPU/lock/allocation | Low | CPU hotspots, allocation, flame graphs |
| JMX `ThreadMXBean` | Programmatic | Very low | Self-monitoring, metrics export |
| `jcmd Thread.print` | Snapshot | Low | Same as jstack, better JDK21 support |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "jstack stops the JVM and blocks requests" | jstack causes a brief safepoint (typically <5ms). The JVM does NOT stop handling requests for the duration of the dump. |
| "JFR is only for development" | JFR is designed for production use with <1% overhead when using default or profile settings. Oracle runs JFR on production JVMs internally. |
| "One jstack dump is enough to diagnose contention" | A single snapshot may catch a normal moment. Take 3 dumps 5s apart; threads still BLOCKED in all 3 indicate sustained contention. |
| "JFR shows memory visibility bugs" | JFR records JVM events (GC, locks, I/O). It cannot detect incorrect values seen due to missing happens-before - use JCStress for that. |
| "High RUNNABLE thread count means high CPU usage" | RUNNABLE includes threads waiting on native I/O, not just actively computing. Check CPU metrics separately. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: JFR file never captured before incident resolves**

**Symptom:** Developer reaches production after alert but no JFR
data exists for the incident window.

**Root Cause:** JFR not pre-started; the default circular buffer
overwrites itself.

**Fix:**
```bash
# Start JFR at startup with disk-based circular recording
java -XX:StartFlightRecording=\
    name=continuous,\
    settings=default,\
    maxage=1h,\
    maxsize=200m,\
    dumponexit=true,\
    filename=/tmp/jfr/ \
    -jar app.jar
# JFR constantly writes to disk; files older than 1h are deleted
# Always has last 1h available for dumping
```

---

**Failure Mode 2: Misleading jstack from RUNNABLE threads in I/O**

**Symptom:** jstack shows 200 RUNNABLE threads but CPU is only 5%.

**Root Cause:** RUNNABLE threads may be waiting on native I/O
(socket.read()), which shows RUNNABLE in Java's thread state enum
even though the thread is blocked at OS level.

**Diagnostic:**
```bash
# Check OS-level thread state (Linux)
cat /proc/<pid>/task/<tid>/status | grep State
# S (sleeping) = blocked on I/O, not computing
# R (running) = actually using CPU
```

**Fix:** Correlate jstack (RUNNABLE) with OS thread state to
distinguish true CPU work from native I/O blocking.

---

**Failure Mode 3: JFR event missing because threshold too high**

**Symptom:** JFR shows no contention events but threads are
intermittently slow.

**Root Cause:** Lock contention duration is below the default
threshold (10ms). Brief but frequent contention (1-5ms per
acquisition) is below the reporting threshold.

**Fix:**
```bash
# Lower threshold in custom JFR settings file:
# Create a custom settings XML (copy from $JDK/lib/jfr/default.jfc)
# Modify: <event name="jdk.JavaMonitorBlocked">
#           <setting name="threshold">1 ms</setting>
#         </event>
jcmd <pid> JFR.start settings=/path/to/custom.jfc
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[JCC-067 - JMM Happens-Before - Deep Rules]] - what you're
  diagnosing at the memory level
- [[JCC-068 - Lock-Free Data Structures]] - what lock-free
  monitoring reveals about CAS contention
- [[JCC-046 - Thread Dump Analysis]] - pattern recognition in
  jstack output

**Builds On This (learn these next):**
- (Advanced: JFR streaming API for real-time alerting)
- async-profiler for CPU flame graph correlation with lock events

**Alternatives / Comparisons:**
- `async-profiler` - agent-based, richer allocation/CPU profiling
- Datadog/New Relic APM - application-level, not JVM-deep
- JMX `ThreadMXBean` - programmatic access to thread/lock metrics

---

### 📌 Quick Reference Card

```
+--------------------------------------------------+
| WHAT IT IS   | jstack: thread snapshot;           |
|              | JFR: continuous JVM event recorder |
+--------------+------------------------------------+
| PROBLEM      | Concurrent bugs are invisible      |
|              | without thread and lock visibility |
+--------------+------------------------------------+
| KEY INSIGHT  | jstack shows WHO is blocked NOW;   |
|              | JFR shows WHEN/HOW LONG over time  |
+--------------+------------------------------------+
| USE WHEN     | Deadlock, contention, pinning,     |
|              | GC correlation, incident post-mortem|
+--------------+------------------------------------+
| AVOID WHEN   | Memory value bugs - use JCStress;  |
|              | CPU profiling - use async-profiler |
+--------------+------------------------------------+
| TRADE-OFF    | Low overhead vs limited real-time  |
|              | alerting; JFR analysis needs JMC   |
+--------------+------------------------------------+
| ONE-LINER    | jstack <pid>; jcmd <pid> JFR.start |
|              | then JFR.dump for lock events      |
+--------------+------------------------------------+
| NEXT EXPLORE | async-profiler GitHub,             |
|              | JDK Mission Control (JMC)          |
+--------------------------------------------------+
```

**If you remember only 3 things:**
1. Take 3 jstack dumps 5 seconds apart - sustained BLOCKED threads
   across all 3 = real contention, not transient.
2. Enable JFR before going to production with circular disk-based
   recording - you need data from before the incident, not after.
3. Lower JFR lock threshold to 1ms in development/staging to
   detect brief but frequent contention invisible at default 10ms.

**Interview one-liner:** "`jstack` gives a thread-state snapshot
revealing current deadlocks and lock ownership; JFR continuously
records `JavaMonitorBlocked` events with duration and owner,
enabling post-mortem lock contention analysis with <1% overhead."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Observability must be built in
from the start, not added during incidents. Low-overhead continuous
recording (JFR) enables retroactive forensics - diagnosing what
happened before the alert fired, not just what is happening now.

**Where else this pattern appears:**
- **Distributed tracing (OpenTelemetry):** Continuous span recording
  at <1% overhead to diagnose service interaction patterns after
  an incident. Same design: circular buffer, dump on demand.
- **Flight recorders in aviation:** Continuous black box recording
  of flight parameters. Dumped only when incident occurs. Same
  trade-off: low-overhead continuous write, high-value post-event
  read.
- **Database slow query log:** MySQL's slow query log with a
  threshold captures queries exceeding X milliseconds - the same
  threshold-based event recording philosophy as JFR.

---

### 💡 The Surprising Truth

Java Flight Recorder has existed since JDK 7 but was a paid
commercial feature of Oracle JDK until JDK 11. Many teams running
JDK 8 in production had access to JFR but disabled it to avoid
licensing concerns - then spent years debugging concurrent issues
that JFR would have solved in minutes. Since JDK 11, JFR is fully
open-source and included in all JDK distributions. Many engineers
still believe it requires a licence or a paid Oracle subscription,
leading them to use inferior third-party agents when the best
profiling tool is already built into their JVM.

---

### 🧠 Think About This Before We Continue

**Question 1 (Root Cause):** A jstack dump taken during a latency
spike shows zero BLOCKED threads, zero WAITING threads, and 200
RUNNABLE threads. CPU is at 10%. RPS is at 10% of normal. What
is the most likely cause, and what additional tool or command
would confirm your hypothesis?

*Hint:* Consider that threads WAITING on `LockSupport.park()`
(ReentrantLock, Semaphore, BlockingQueue) show as WAITING, not
BLOCKED. Also consider GC stop-the-world pauses - what do threads
show during and after a GC pause? Check JFR GC events.

---

**Question 2 (Design Trade-off):** You want to add automatic lock
contention alerting to your service: if any lock is held for more
than 100ms, a Slack alert fires. Design this system using JFR's
streaming API. What are the edge cases, and how would you prevent
alert storms during GC pauses (which inflate all lock durations)?

*Hint:* Research `RecordingStream.onEvent()`, the correlation of
`jdk.JavaMonitorBlocked` timestamps with `jdk.GCPhasePause` events,
and how to debounce alerts triggered by GC-induced lock inflation.

---

**Question 3 (Scale):** Your organisation has 500 JVM services
in Kubernetes. You want centralised JFR incident data collection
without pre-configuring each pod. Design a system that can
on-demand trigger JFR dumps from any pod, collect the binary file,
and make it available in an S3 bucket within 30 seconds of an
alert. What components and APIs would you use?

*Hint:* Investigate `jcmd` over SSH/exec in Kubernetes, `kubectl
exec` scripting, the JVM's dynamic attach API for programmatic
JFR triggering, and whether a JFR agent in each pod that watches
for external signals (via a webhook or sidecar) would be simpler.

