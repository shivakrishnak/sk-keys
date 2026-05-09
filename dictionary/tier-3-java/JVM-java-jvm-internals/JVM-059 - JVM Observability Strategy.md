---
id: JVM-059
title: JVM Observability Strategy
category: Java & JVM Internals
tier: tier-3-java
folder: JVM-java-jvm-internals
difficulty: ★★★
depends_on: JVM-037, JVM-051, JVM-055
used_by:
related: JVM-056, JVM-058, JVM-064
tags:
  - jvm
  - java
  - observability
  - production
status: complete
version: 1
layout: default
parent: "Java & JVM Internals"
grand_parent: "Technical Dictionary"
nav_order: 59
permalink: /jvm/jvm-observability-strategy/
---

# JVM-059 - JVM Observability Strategy

**⚡ TL;DR** - JVM observability requires four complementary layers: GC logs (GC health), JFR continuous profiling (low-overhead forensics), JMX metrics (operational dashboards), and heap dumps (OOM diagnosis).

| Field | Value |
|---|---|
| **Depends on** | [[JVM-037 - GC Logs]], [[JVM-051 - Safepoint]], [[JVM-055 - GC Tuning Strategy for Production JVMs]] |
| **Used by** | (none - terminal observability entry) |
| **Related** | [[JVM-056 - JVM Architecture Decisions at Scale]], [[JVM-058 - Heap Sizing and Memory Planning Strategy]], [[JVM-064 - JVM-First Debugging Mental Model]] |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An engineer receives a PagerDuty alert: "API p99 latency: 8 seconds." They SSH into the pod. `top` shows 90% CPU. The GC logs: not enabled. JFR: not enabled. Heap dump: cannot take without restarting (OOM already happened). They know something is wrong with the JVM but have no forensic data. They restart the pod. Incident closes. Root cause: unknown. Problem recurs in 3 days.

**THE BREAKING POINT:**
JVM production issues have three characteristics that make blind debugging impossible: (1) they are often transient (the problem passes by the time you look), (2) the evidence is in JVM-internal state (GC pauses, JIT deoptimisations, thread contention) not in application logs, (3) symptoms (high latency, high CPU) map to multiple root causes (GC storm, memory leak, safepoint stall, lock contention) that require different fixes. Without observability infrastructure, root cause analysis is guesswork.

**THE INVENTION MOMENT:**
Java Flight Recorder (JFR), originally a JRockit commercial feature, was open-sourced in JDK 11 (JEP 328). Combined with JDK Mission Control (JMC) for analysis, JFR provides continuous, low-overhead (1-2% CPU) profiling of all JVM subsystems. This made always-on JVM observability economically viable in production.

**EVOLUTION:**
- JDK 5: JConsole - basic JMX monitoring
- JDK 6: VisualVM - GUI profiling (high overhead, dev only)
- JDK 11: JFR open-sourced - production-safe continuous recording
- JDK 14: JFR Event Streaming API - real-time event consumption
- JDK 17-21: JFR extended to virtual threads, GC improvements, more default events

---

### 📘 Textbook Definition

**JVM observability** is the practice of instrumenting, collecting, and analysing signals from all JVM subsystems to enable understanding of application health, performance, and failure root causes in production. A complete JVM observability strategy comprises four layers: (1) **GC Logs**: continuous record of garbage collection events, pause durations, heap occupancy, and GC algorithm decisions. (2) **Java Flight Recorder (JFR)**: low-overhead (1-2%) continuous profiling of CPU, memory allocation, lock contention, I/O, class loading, JIT compilation, and GC in a circular buffer. (3) **JMX Metrics**: real-time operational metrics (heap usage, thread count, GC count/time) exposed via JMX and scraped by Prometheus/Micrometer. (4) **On-Demand Diagnostics**: heap dumps (`jmap`, JFR OOM triggers), thread dumps (`jstack`, `jcmd`), and native memory tracking for incident response.

---

### ⏱️ Understand It in 30 Seconds

**One line:** JVM observability needs GC logs (always on), JFR (continuous low-overhead), JMX metrics (dashboards), and heap dumps (OOM diagnosis).

> Like an aircraft's flight recorder and instruments: the flight recorder (JFR) runs continuously and captures everything for post-incident analysis; the cockpit instruments (JMX) give the pilot real-time operational visibility; the flight log (GC logs) records specific system events; the crash recorder (heap dump) captures the state at the moment of failure.

**One insight:** JFR at 1-2% overhead is the only profiling mechanism safe for continuous production use. VisualVM-style profiling adds 10-20% overhead and changes performance characteristics. JFR captures data passively through JVM instrumentation points, not through sampling interruption.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Transient JVM problems cannot be debugged reactively without always-on recording
2. JVM internal state (GC, JIT, safepoints) is invisible to application-level APM
3. Sampling profilers add overhead that changes the behaviour being measured
4. Different problem classes require different observability tools

**DERIVED DESIGN:**
From invariant 1: JFR must be enabled from JVM startup, not after the problem manifests.
From invariant 2: application-level metrics (request count, error rate) are necessary but insufficient. JVM metrics (GC pause, Code Cache, thread states) are required for JVM-layer diagnosis.
From invariant 3: JFR uses JVM safepoints and async-event mechanisms, not sampling. It records actual events with minimal perturbation.
From invariant 4: GC log analysis identifies GC-layer problems; JFR identifies CPU/allocation/contention problems; heap dumps identify memory-layer problems; thread dumps identify liveness problems (deadlocks, blocked threads).

**THE TRADE-OFFS:**
**Gain:** Forensic capability for all JVM incidents; no blind spots in the JVM layer
**Cost:** JFR: 1-2% CPU overhead + disk for recordings; GC logging: minimal; heap dump: stop-the-world snapshot (avoid on latency-critical paths)

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Different JVM problem classes require different diagnostic artifacts. One signal cannot cover all scenarios.
**Accidental:** Multiple separate tools (jmap, jstack, jstat, JFR, JMX) with different interfaces and formats. JFR consolidates most of these into a single recording format.

---

### 🧪 Thought Experiment

**SETUP:** Your service has random latency spikes to 5 seconds, occurring 3 times per hour. They last exactly 3-4 seconds. The rest of the time, latency is 20ms. Your APM shows nothing unusual except the latency spike itself.

**WHAT HAPPENS WITHOUT JVM OBSERVABILITY:**
You search application logs: no errors. Dependency health checks: all green. You add more heap hoping it is GC. The spikes continue. You throttle incoming requests. Spikes continue but shorter. You suspect a bug and review code for weeks. The spikes are safepoint-induced GC pauses from a Full GC event. Without GC logs, you cannot see this.

**WHAT HAPPENS WITH JVM OBSERVABILITY:**
GC logs show: `[Full GC (Ergonomics) 10240M->4096M(16384M), 3.421 secs]` exactly matching the latency spikes. JFR shows: Old Gen occupancy was at 97% before each Full GC. The root cause: allocation rate spike during report generation causes Old Gen overflow. Fix: incremental heap increase + G1GC tuning to trigger concurrent collection at 70% Old Gen. Spikes eliminated in 30 minutes of incident investigation.

**THE INSIGHT:**
GC pauses stop all application threads. A 3-second GC pause looks exactly like a 3-second application bug from outside the JVM. Only GC logs can distinguish these. Without GC logs, every 3-second pause investigation starts from zero.

---

### 🧠 Mental Model / Analogy

> Think of JVM observability as a hospital's ICU monitoring system. GC logs are the continuous heart rate recorder - always running, captures every event. JFR is the full-body sensor array capturing hundreds of vital signs in a circular buffer. JMX metrics are the bedside monitors showing current readings to nurses. Heap dumps are emergency MRI scans taken when something critical happens. You need all four for different phases of patient care: ongoing monitoring, retrospective analysis, real-time visibility, and emergency diagnosis.

Element mapping:
- Continuous heart rate recorder = GC logs
- Full-body sensor array = JFR continuous recording
- Bedside monitors = JMX metrics (Prometheus/Grafana)
- Emergency MRI = heap dump on OOM
- ICU patient = production JVM process
- On-call doctor = on-call engineer with forensic tools

Where this analogy breaks down: in a hospital, patients are humans and equipment is dedicated. JVM observability tools must share CPU and memory with the application they monitor. The overhead budget is real: JFR at 1-2% is acceptable; heap dump snapshots at 100% stop-the-world are for emergencies only.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
JVM observability means having the right tools in place so you can understand what is happening inside your Java application. Some tools record what the garbage collector is doing. Some tools record what your code is spending time on. When something goes wrong, you use these recordings to find the cause.

**Level 2 - How to use it (junior developer):**
Minimum viable JVM observability setup for any production service:
1. Enable GC logging: `-Xlog:gc*:file=/var/log/gc.log:time,uptime,level,tags:filecount=5,filesize=20m`
2. Enable JFR continuous: `-XX:StartFlightRecording=disk=true,maxage=24h,settings=default`
3. Enable heap dump on OOM: `-XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/var/log/heap.hprof`
4. Expose JMX metrics via Micrometer + Prometheus (standard for Spring Boot)

**Level 3 - How it works (mid-level engineer):**
JFR records data to a circular buffer on disk. When you need to analyse an incident, retrieve the recording covering the incident window with `jcmd <pid> JFR.dump filename=/tmp/incident.jfr`. JFR records: method profiling (CPU hotspots), GC events (identical to GC log but with more context), allocation profiling (which methods allocate most), lock contention (which locks are blocking threads), I/O events (slow file/network operations), class loading events, JIT compilation events, and more. JDK Mission Control (JMC) analyses `.jfr` files with drill-down views for each event type. For real-time streaming, `JFR.stream()` in JDK 14+ exposes events via a Java API.

**Level 4 - Why it was designed this way (senior/staff):**
JFR's circular buffer design is a deliberate trade-off between coverage and storage cost. A 24-hour recording at default settings consumes approximately 500MB-2GB depending on event rate. The buffer is written to disk continuously in rolling files, so old data is automatically evicted. This design means JFR is always capturing the last N hours of JVM behaviour. When an incident occurs at 3am, the 24-hour JFR recording contains the complete pre-incident profile. The 1-2% CPU overhead is achieved through: (1) async event writing (events written on a background thread, not the application thread), (2) safepoint-based chunk finalisation, (3) selective event enablement (only events with non-zero subscribers are recorded). The combination makes JFR the only profiling technology safe for continuous production use.

**Expert Thinking Cues:**
- JFR dump taken after incident: `jcmd <pid> JFR.dump filename=/tmp/post-incident.jfr`
- JFR with custom events: `@Label("My Event") class MyJFREvent extends Event {...}` - add business events to JFR timeline
- For real-time GC alerting: parse GC log with log4j/Logback appender; alert on `Full GC` patterns

---

### ⚙️ How It Works (Mechanism)

**JFR Architecture:**
```
  Application threads
       |
  JFR event points (built-in to JVM)
       |
  Per-thread event buffers (low contention)
       |
  JFR global buffer (background flush)
       |
  Disk: rotating .jfr chunks (circular)
       |
  jcmd JFR.dump -> retrieve .jfr file
       |
  JDK Mission Control (analysis)
  or programmatic JFR.stream()
```

**JMX Metrics Architecture:**
```
  JVM MBeans (GC, Memory, Thread, Runtime)
       |
  JMX server (port 9010 or localhost)
       |
  Micrometer (Spring Boot actuator)
       |
  Prometheus endpoint /actuator/prometheus
       |
  Prometheus scrape (every 15s)
       |
  Grafana dashboard
       |
  Alertmanager rules
```

**Four Observability Layers Summary:**
| Layer | Tool | Overhead | When to Use |
|---|---|---|---|
| GC events | GC logs | <1% | Always - standard mandatory flag |
| Deep profiling | JFR | 1-2% | Always - continuous production recording |
| Operational metrics | JMX/Micrometer | <1% | Always - Prometheus scrape |
| OOM forensics | Heap dump | High (STW) | On OOM event - automated |

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
  JVM starts with observability flags  <- YOU ARE HERE
       |
  GC logs writing to /var/log/gc.log
  JFR recording to /tmp/jfr/ (rolling)
  JMX metrics exposed on :9010
       |
  Prometheus scrapes JMX every 15s
       |
  Grafana: heap, GC count/time,
  thread count, CPU dashboards
       |
  Incident: latency spike
       |
  Alertmanager fires
       |
  Engineer: check Grafana (JMX)
  -> Correlate with GC log
  -> Dump JFR for deep analysis
  -> jcmd JFR.dump filename=.jfr
       |
  JMC analysis: find root cause
       |
  Fix deployed; validate with
  new JFR recording
```

**FAILURE PATH:**
- GC logging not enabled: incident investigation impossible; restart required
- JFR disk full: recording stops silently; no forensic data for next incident
- Heap dump too large: takes 60+ seconds STW; kills pod during dump
- No alerting on GC metrics: incidents discovered by customers, not engineers

**WHAT CHANGES AT SCALE:**
At scale, centralise JFR analysis. Use JFR streaming to publish events to a central Kafka topic. Build dashboards that aggregate JFR events across the fleet. Netflix Hollow and LinkedIn's similar tools do this at massive scale.

---

### 💻 Code Example

**BAD - no JVM observability:**
```bash
# Zero observability flags
java -Xmx4g -jar app.jar
# When OOM occurs: no heap dump, no GC log, no forensics
# When latency spikes: no GC data to correlate
```

**GOOD - full JVM observability baseline:**
```bash
java \
  # Heap sizing
  -XX:MaxRAMPercentage=75.0 \
  -XX:+UseZGC \
  \
  # GC logging
  -Xlog:gc*:file=/var/log/gc.log:time,uptime,level,tags:filecount=5,filesize=20m \
  \
  # JFR continuous recording
  -XX:StartFlightRecording=\
    disk=true,\
    maxage=24h,\
    settings=default,\
    path=/var/log/jfr/ \
  \
  # OOM forensics
  -XX:+HeapDumpOnOutOfMemoryError \
  -XX:HeapDumpPath=/var/log/heap.hprof \
  -XX:+ExitOnOutOfMemoryError \
  \
  # JMX for Prometheus
  -Dcom.sun.management.jmxremote \
  -Dcom.sun.management.jmxremote.port=9010 \
  -Dcom.sun.management.jmxremote.authenticate=false \
  -Dcom.sun.management.jmxremote.ssl=false \
  \
  -jar app.jar
```

**Triggering JFR dump from running JVM:**
```bash
# List active recordings
jcmd <pid> JFR.check

# Dump current recording (get last 5 minutes)
jcmd <pid> JFR.dump \
  filename=/tmp/incident-$(date +%Y%m%d-%H%M%S).jfr \
  maxage=5m

# Start new recording (if not started at JVM launch)
jcmd <pid> JFR.start \
  duration=60s \
  filename=/tmp/oneshot.jfr \
  settings=default
```

**Custom JFR event for business context:**
```java
import jdk.jfr.*;

@Label("Payment Processing")
@Category("Business")
@StackTrace(false)
public class PaymentEvent extends Event {
    @Label("Payment ID")
    public String paymentId;

    @Label("Amount")
    public double amount;

    @Label("Processing Time (ms)")
    public long processingTimeMs;
}

// Usage:
PaymentEvent event = new PaymentEvent();
event.paymentId = paymentId;
event.begin();
// ... process payment ...
event.amount = amount;
event.processingTimeMs = duration;
event.commit();
// Event appears in JFR recording with full JVM context
```

**How to test / verify correctness:**
```bash
# Verify JFR recording is active
jcmd <pid> JFR.check
# Output: Recording 1: name=... disk=true running

# Verify GC logging is active
tail -20 /var/log/gc.log
# Should show recent GC events

# Verify JMX is accessible
jcmd <pid> VM.flags | grep "jmxremote"
```

---

### ⚖️ Comparison Table

| Tool | Overhead | Data | Use Case |
|---|---|---|---|
| GC logs | <1% | GC events only | Always-on; GC-layer diagnosis |
| JFR (continuous) | 1-2% | Full JVM profile | Always-on forensics; incident replay |
| JFR (on demand) | 1-2% | Full JVM profile | Targeted investigation |
| Async-profiler | 2-5% | CPU + allocation | Deep perf investigation (dev/staging) |
| JMX/Micrometer | <1% | Operational metrics | Real-time dashboards, alerting |
| Heap dump | STW | Heap object graph | OOM forensics |
| Thread dump | <1ms | Thread state snapshot | Deadlock/liveness diagnosis |
| VisualVM attach | 10-20% | GUI profile | Development only - never production |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "JFR is too expensive for production" | JFR overhead is 1-2% CPU - the same as a JVM flag like `-XX:+UseG1GC`. It is explicitly designed and tested for continuous production use. |
| "GC logs slow down the JVM" | GC logging overhead is sub-1% in production. The alternative - no visibility into GC - is far more expensive in incident resolution time. |
| "APM (Datadog, New Relic) replaces JVM observability" | APM agents instrument application code. JVM observability instruments JVM internals. They are complementary: APM for distributed tracing and business metrics; JVM tools for GC, JIT, safepoint, and memory diagnosis. |
| "I can take a heap dump any time during an incident" | Heap dump triggers a stop-the-world pause proportional to heap size. For a 10GB heap, this is 20-60 seconds of full application freeze - unacceptable in most production scenarios. Use only on OOM with auto-trigger, not reactively. |
| "JMX monitoring is sufficient for JVM health" | JMX provides operational metrics (current heap, GC count). JFR provides forensic history (what happened in the last 24 hours). Both are needed. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: JFR disk exhaustion stops recording**
**Symptom:** JFR recording stops after several days; `jcmd <pid> JFR.check` shows no active recording
**Root Cause:** `/var/log/jfr/` filesystem fills up; JFR stops writing silently
**Diagnostic:**
```bash
df -h /var/log/jfr/
ls -lh /var/log/jfr/*.jfr | tail -10
jcmd <pid> JFR.check
```
**Fix:** Configure JFR rolling retention: `maxsize=2g` or `maxage=48h`; mount JFR directory on ephemeral volume with adequate size
**Prevention:** Monitor `/var/log/jfr/` disk usage; alert at 80%; configure `maxsize` explicitly

**Failure Mode 2: Heap dump fails or never triggers**
**Symptom:** OOM occurred but no `.hprof` file found in heap dump path
**Root Cause:** JVM OOMKilled by Kubernetes before heap dump completes; or path does not exist; or pod read-only filesystem
**Diagnostic:**
```bash
ls -la /var/log/heap.hprof
kubectl describe pod <pod> | grep OOMKilled
# If OOMKilled: heap dump incomplete; pod restarted before dump finished
```
**Fix:** Mount `/var/log/` as a writable volume (not ephemeral pod storage); ensure container has write permission; consider smaller heap dump: `-XX:OnOutOfMemoryError='kill -9 %p'` + separate heap dump via JFR OOM event
**Prevention:** Test heap dump path writability in startup scripts

**Failure Mode 3: JMX port conflict in Kubernetes**
**Symptom:** Prometheus cannot scrape JMX metrics; scraper shows connection refused on port 9010
**Root Cause:** JMX remote port set to fixed value; multiple pods on same node conflict; or missing service port configuration
**Diagnostic:**
```bash
kubectl exec -it <pod> -- netstat -tlnp | grep 9010
kubectl describe service <svc> | grep 9010
```
**Fix:** Use JMX over Unix domain socket for local Prometheus exporter; or use Micrometer Prometheus directly (HTTP endpoint) avoiding JMX remote port entirely:
```yaml
# Spring Boot: expose /actuator/prometheus instead of JMX
management:
  endpoints:
    web:
      exposure:
        include: prometheus,health
  metrics:
    export:
      prometheus:
        enabled: true
```
**Prevention:** Use Micrometer/actuator Prometheus endpoint instead of JMX remote for Kubernetes

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[JVM-037 - GC Logs]] - GC log format and interpretation
- [[JVM-051 - Safepoint]] - Safepoint impact on application threads
- [[JVM-055 - GC Tuning Strategy for Production JVMs]] - Using GC log data for tuning

**Builds On This (learn these next):**
- [[JVM-064 - JVM-First Debugging Mental Model]] - Using observability data to debug incidents

**Alternatives / Comparisons:**
- [[JVM-056 - JVM Architecture Decisions at Scale]] - Fleet-level observability standardisation
- [[JVM-058 - Heap Sizing and Memory Planning Strategy]] - Memory metrics interpretation

---

### 📌 Quick Reference Card

```
+--------------------------------------------------+
| WHAT IT IS    | Four-layer JVM observability:    |
|               | GC logs + JFR + JMX + heap dump  |
+--------------------------------------------------+
| PROBLEM       | Blind JVM incidents; no forensic |
|               | data when problems occur          |
+--------------------------------------------------+
| KEY INSIGHT   | JFR at 1-2% overhead is safe for |
|               | continuous production use          |
+--------------------------------------------------+
| USE WHEN      | Every production JVM service,    |
|               | from day one                      |
+--------------------------------------------------+
| AVOID WHEN    | Heap dumps: only on OOM event;   |
|               | never interactively in production |
+--------------------------------------------------+
| TRADE-OFF     | 2-3% total overhead vs complete  |
|               | forensic visibility               |
+--------------------------------------------------+
| ONE-LINER     | -Xlog:gc* + JFR.start(disk=true)|
|               | + HeapDumpOnOOM = minimum viable |
+--------------------------------------------------+
| NEXT EXPLORE  | JVM-064 debugging mental model,  |
|               | JVM-056 fleet observability       |
+--------------------------------------------------+
```

**If you remember only 3 things:**
1. Enable GC logging and JFR from JVM startup - not after the incident
2. JFR at 1-2% overhead is the only profiler safe for continuous production use
3. Heap dump on OOM is automated (`-XX:+HeapDumpOnOutOfMemoryError`); never take manually in production

**Interview one-liner:** "Production JVM observability requires four layers: GC logs for GC health, JFR for low-overhead continuous profiling, JMX/Micrometer for operational metrics, and automated heap dump on OOM for forensics."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Observability infrastructure must be deployed before incidents occur, not provisioned in response to them. The window between "incident starts" and "observability deployed" is dark. Retrospective root-cause analysis is impossible if the evidence was never captured.

**Where else this pattern appears:**
- Kernel oops analysis: `crash` dump and `vmcore` enabled in production kernels; enabled before the crash happens
- Database slow query log: enabled always, not when queries first become slow
- Distributed tracing: Jaeger/Zipkin sampling enabled from deployment day one; not added after first latency complaint

---

### 💡 The Surprising Truth

JFR was originally developed by BEA Systems for their JRockit JVM in 2003, not by Sun Microsystems. When Oracle acquired BEA in 2008, JFR was ported to HotSpot as a commercial Oracle JDK feature requiring a paid licence. It remained proprietary for nine years. In 2018 (JDK 11), Oracle open-sourced JFR under the same GPLv2 as OpenJDK (JEP 328). The result: the industry's best production JVM profiler - previously a paid enterprise feature - became available free for everyone, in every distribution, forever. Most developers using JFR today do not know they are using a tool with a 20-year history and a commercial origin. The open-sourcing of JFR fundamentally changed production Java observability, making capabilities previously reserved for enterprise Oracle support customers available to every developer.

---

### 🧠 Think About This Before We Continue

**Q1 (Root Cause):** Your service shows p99 latency spikes of exactly 200ms every 45 seconds like clockwork. GC logs show no GC events during these spikes. JFR shows safepoint operations (not GC) taking 200ms. What class of JVM operation causes regular safepoint pauses unrelated to GC, and which JFR event category reveals the specific cause?
*Hint:* Research safepoint operations beyond GC in [[JVM-051 - Safepoint]]; specifically look at JFR's `jdk.SafepointStatisticsLog` events and what operations trigger them.

**Q2 (Scale):** You have 500 services each with JFR writing to local ephemeral storage (30-day rolling). A P0 incident requires analysing JFR data from 50 services simultaneously to find a distributed causality chain. What infrastructure change enables cross-service JFR correlation at this scale?
*Hint:* Research JFR Event Streaming API (JDK 14+) and how it enables real-time JFR event forwarding to centralised systems like Kafka or Elasticsearch.

**Q3 (Design Trade-off):** GraalVM Native Image services have no JFR (JIT events, safepoints, and GC events do not exist in the native binary's execution model). What JVM observability signals are lost when migrating to Native Image, and what must replace them to maintain equivalent production debuggability?
*Hint:* Consider what signals GC logs, JFR, and JIT events provide; then consider what native binary equivalents exist (perf, async-profiler in native mode, OS-level memory tracking) for each signal type.
