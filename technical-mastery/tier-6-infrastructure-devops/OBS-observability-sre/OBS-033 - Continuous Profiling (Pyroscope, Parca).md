---
id: OBS-033
title: "Continuous Profiling (Pyroscope, Parca)"
category: Observability & SRE
tier: tier-6-infrastructure-devops
folder: OBS-observability-sre
difficulty: ★★★
depends_on: OBS-001, OBS-002, OBS-006, OBS-008
used_by: OBS-044, OBS-045
related: OBS-006, OBS-034, OBS-029, OBS-030, OBS-044
tags:
  - observability
  - profiling
  - performance
  - production
  - advanced
  - deep-dive
status: complete
version: 4
layout: default
parent: "Observability & SRE"
grand_parent: "Technical Mastery"
nav_order: 33
permalink: /technical-mastery/obs/continuous-profiling-pyroscope-parca/
---

⚡ TL;DR - Continuous profiling captures CPU, memory,
and goroutine call-stack data from running production
services at low overhead (< 3% CPU), stored with
timestamps so you can compare profiles "before and
after an incident" or "last week vs this week."
It answers the question that metrics and traces cannot:
"which function is consuming the CPU during this
latency spike?"

| #033            | Category: Observability & SRE                                     | Difficulty: ★★★ |
| :-------------- | :---------------------------------------------------------------- | :-------------- |
| **Depends on:** | Observability Fundamentals, Three Pillars, Metrics Types, Tracing |                 |
| **Used by:**    | Platform Observability, Observability System Design               |                 |
| **Related:**    | Metrics Types, eBPF Observability, RED Method, USE Method         |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A checkout service has P99 latency increasing gradually:
150ms → 200ms → 280ms → 350ms over 3 weeks. No obvious
errors. No sudden incidents. RED metrics show the drift
but not the cause. The SLO burn rate alert fires at
week 3 (P99 > 300ms threshold).

The on-call engineer has: traces (which show all
spans are slow, not one specific slow span), metrics
(which show CPU utilization 40% - normal), and logs
(which show no errors). The problem is diffuse: every
request is slightly slower. This is the "invisible
regression" - a code change or data growth pattern
that made many operations marginally more expensive.

With only metrics and traces, the investigation takes
3-5 hours. The engineer suspects: a database index
degradation, a code change that added expensive work,
a library update, GC pressure. Each hypothesis requires
a different investigation approach.

**THE INVENTION:**
Continuous profiling stores the call stack distribution
of every 10-second window for the last 30 days. The
engineer opens Pyroscope, selects "3 weeks ago" vs
"today," and sees a flame graph diff: one function
`CartService.computeShippingOptions()` grew from 5%
of CPU time to 35% of CPU time. Git blame shows the
function changed 3 weeks ago. Root cause found in
5 minutes.

---

### 📘 Textbook Definition

**Continuous profiling** is the practice of periodically
capturing CPU, memory, and concurrency profiles from
production services and storing them with timestamps,
enabling historical comparison and regression detection.

**Profile types:**

- **CPU profile**: which functions consume CPU time.
  Captured by statistical sampling (e.g., SIGPROF
  signal at 100 Hz, recording the current call stack).
  Shows where CPU cycles are spent.
- **Heap profile (memory allocation)**: which call
  sites allocate the most memory. Tracks cumulative
  allocations, not just current live objects.
- **Goroutine/thread profile**: how many concurrent
  goroutines/threads exist and what they are doing.
  Detects goroutine leaks or thread pool saturation.
- **Mutex profile**: where goroutines are blocked
  waiting for mutex locks. Detects lock contention.
- **Block profile**: where goroutines block on any
  synchronisation primitive (channel, mutex, I/O).

**The flame graph:**
The primary visualisation for profiles. Each horizontal
bar = a function in the call stack. Width = proportion
of time/memory consumed. Widest bars at the bottom
of the stack are the dominant consumers. The "hottest"
(widest) bars near the leaves of the stack = the
functions where optimisation effort will be most
effective.

**Key tools:**

- **Pyroscope** (Grafana Labs): language-agnostic
  continuous profiling server, stores profiles with
  tags, flame graph UI, diff mode
- **Parca** (Polar Signals): eBPF-based system profiling,
  open source, no code instrumentation required
- **Datadog Continuous Profiler**: commercial option
  with APM integration
- **Google Cloud Profiler**: managed service for GCP

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Continuous profiling is like adding a frame-by-frame
recording to your logs and traces: it shows you
exactly which code is running and for how long,
stored historically so you can compare "today" vs
"last week."

> Traditional profiling is like taking a single
> photograph of your application mid-run. Continuous
> profiling is like recording a time-lapse video.
> The time-lapse lets you see: this function grew from
> 5% to 35% of the frame between Tuesday and Friday.
> The single photograph only shows you the current
> state. When diagnosing a gradual performance
> regression, you need the time-lapse to see what
> changed.

---

### 🔩 First Principles Explanation

**HOW STATISTICAL PROFILING WORKS:**

```
Traditional (deterministic) profiling:
  Record EVERY function call + duration
  Overhead: 10-100x normal execution time
  Result: precise call counts and durations
  Problem: cannot run in production (too slow)

Statistical (sampling) profiling:
  Every 10ms (100 Hz): interrupt the process
  Record the current call stack (which function
    is executing, and its callers)
  After 1000 samples: functions appear in the
    stack in proportion to their CPU usage

Example:
  processRequest() appears in 800/1000 stacks
  → ~80% of CPU time is in processRequest()

  parseJSON() appears in 600/1000 stacks
  → ~60% of CPU time is in parseJSON()
  (called within processRequest())

  compressResponse() appears in 50/1000 stacks
  → ~5% of CPU time in compressResponse()

Overhead: ~1-3% CPU for 100 Hz sampling
Can run continuously in production safely
```

**THE PPROF FORMAT (Go/Java standard):**

```
pprof is the de facto profiling format:
  - Used by Go runtime natively
  - Used by Java via async-profiler
  - Used by Pyroscope and other tools

Structure:
  Profile {
    samples: [
      {
        stack: [
          "processPayment",
          "validateCard",
          "luhnCheck"
        ],
        value: 450  // 4.5 seconds of CPU time in this
          stack
      },
      ...
    ],
    period: 10000000  // 10ms sampling interval (ns)
  }

Flame graph from pprof:
  - Bottom of flame: entry point (main, handleRequest)
  - Top of flame: hottest function (most CPU time)
  - Width of bar: % of CPU time
  - Click bar: drill into that call chain
```

**THE DIFF PROFILE:**

```
Before: profileA (taken at t=0, or "1 week ago")
After:  profileB (taken at t=now)

Diff = profileB - profileA
  Functions that GREW (appear wider in diff):
    → Code changes or data growth made these slower
  Functions that SHRANK (appear narrower):
    → Optimisations or reduced load
  New functions in profile:
    → New code path introduced

Pyroscope diff view:
  Red  = function grew (more CPU now)
  Blue = function shrank (less CPU now)
  Width = absolute time difference
```

---

### 🧪 Thought Experiment

**THE INVISIBLE REGRESSION:**

A Java payment service shows P99 latency growing from
150ms to 350ms over 3 weeks. The engineering team
debates: "Is it the database? The new ORM library?
The added validation logic? GC pressure from the
new feature?"

**Without continuous profiling:**
3 hypotheses tested over 2 days:

1. Run database slow query logs → no slow queries found
2. Revert ORM library version in staging → no difference
3. Profile with JVM flight recorder → snapshot shows
   current state but cannot compare to 3 weeks ago

Result: team cannot identify root cause. Incident
escalates to engineering manager.

**With continuous profiling (Pyroscope):**

1. Open Pyroscope. Select service: payment-api.
2. Select "diff" mode. Baseline: 3 weeks ago.
   Compare: today.
3. Flame graph diff shows:
   - `PaymentValidator.validateAddress()` grew from
     2% to 28% of CPU time (RED in diff)
   - Drill in: calls `ExternalAddressVerifier.verify()`
   - `ExternalAddressVerifier` is a new third-party
     library added 3 weeks ago
4. Root cause found: the new address validation library
   makes a synchronous HTTP call on every payment.
   At 50ms per call in staging, now 180ms per call
   in production (external rate limit applied).
5. Fix: add address validation result caching (LRU,
   TTL 1 hour per address). P99 returns to 155ms.

Total investigation time: 12 minutes.

---

### 🧠 Mental Model / Analogy

> Continuous profiling is like a building's HVAC
> energy audit. Traditional monitoring tells you the
> electricity bill (CPU utilization metric). Traces
> tell you which rooms are occupied (which services
> are being called). But neither tells you which
> specific equipment is consuming the most energy.
>
> The continuous profiler is a sensor on every circuit
> breaker, recording per-circuit power draw every
> 10 seconds. When the bill spikes, you can compare
> "last month vs this month" per circuit: the HVAC
> compressor grew from 30% to 65% of total draw.
> It was running more often because a refrigerant
> leak reduced efficiency. The compressor circuit
> is the `processPayment()` function in your code.
>
> Without per-circuit monitoring, you can only say
> "the bill is higher." With it, you say "the HVAC
> compressor is inefficient and here is why."

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone):**
Continuous profiling is a tool that records which
functions in your code are using the most CPU or
memory in production, and saves those records over
time. When the service gets slow, you can look back
and see which function got slower.

**Level 2 - How to add it (junior):**
Add the Pyroscope agent to your service. For Java:
add `pyroscope-agent.jar` as a Java agent. For Go:
add `github.com/grafana/pyroscope-go` and call
`pyroscope.Start()`. The agent samples the call stack
every 10ms and sends aggregated profiles to the
Pyroscope server every 10 seconds. Overhead: < 1%
CPU for most services. Profiles are stored with
timestamp and service tags.

**Level 3 - How to use it in incidents (mid-level):**
When RED metrics show a latency spike: open Pyroscope,
select the service, select the time range of the
incident, view the CPU flame graph. The widest bars
are the dominant CPU consumers. Compare with the
baseline (before the incident) using diff mode.
Functions that grew (red) are the regression candidates.
Drill into the widest red function to find the
specific code path.

**Level 4 - Correlate with traces and metrics (senior):**
Pyroscope 2.0+ integrates with Grafana: a Grafana
dashboard can show a trace with high latency → click
a slow span → view the CPU profile from the same
time window → see which function in that service
was hot during that span. This triad (trace + metric

- profile) is the complete picture: trace shows
  WHERE the latency is (which service, which operation),
  profile shows WHAT CODE is consuming the CPU in
  that service at that time.

**Level 5 - Platform strategy (staff):**
Continuous profiling is the fourth pillar of
observability (after metrics, logs, traces). Platform
strategy: deploy Pyroscope/Parca as a platform service.
Auto-instrument all services via Java agent injection
(Kubernetes admission webhook) or sidecar. Store
profiles for 30 days (compressed, ~50 MB/service/day
at 100 Hz sampling). Integrate with Grafana for
unified dashboards. Use continuous profiling for:
cost attribution (which services use the most CPU
at which times), performance regression detection
(automated diff alert when a function grows > 20%
week-over-week), capacity planning (CPU consumption
profile shape = right-sizing of pod requests).

---

### ⚙️ How It Works (Mechanism)

**PYROSCOPE - JAVA INSTRUMENTATION:**

```bash
# Add Pyroscope Java agent to JVM startup
java \
  -javaagent:/opt/pyroscope/pyroscope-agent.jar \
  -Dpyroscope.server.address=http://pyroscope:4040 \
  -Dpyroscope.application.name=payment-api \
  -Dpyroscope.profiles.interval=10s \
  -Dpyroscope.format=jfr \
  -Dpyroscope.java.stack.depth.max=64 \
  -jar payment-api.jar

# Tags for filtering in Pyroscope UI:
# Automatically adds: hostname, container, version
# Add custom: -Dpyroscope.tags=env=prod,team=payments
```

**PYROSCOPE - GO INSTRUMENTATION:**

```go
package main

import (
  "github.com/grafana/pyroscope-go"
  "os"
)

func initProfiling() {
  _, err := pyroscope.Start(pyroscope.Config{
    ApplicationName: "checkout-api",
    ServerAddress:   "http://pyroscope:4040",

    // Profile types to collect
    ProfileTypes: []pyroscope.ProfileType{
      pyroscope.ProfileCPU,
      pyroscope.ProfileAllocObjects,
      pyroscope.ProfileAllocSpace,
      pyroscope.ProfileInuseObjects,
      pyroscope.ProfileInuseSpace,
      pyroscope.ProfileGoroutines,
      pyroscope.ProfileMutexCount,
    },

    // Tags for filtering in UI
    Tags: map[string]string{
      "version":     os.Getenv("APP_VERSION"),
      "environment": os.Getenv("ENV"),
      "pod":         os.Getenv("POD_NAME"),
    },
  })
  if err != nil {
    log.Printf("Warning: profiling init failed: %v", err)
    // Non-fatal: profiling failure should not stop service
  }
}

// Dynamic profiling labels for per-request context
// (use sparingly - do not add high-cardinality labels)
func handleCheckout(w http.ResponseWriter,
    r *http.Request) {

  pyroscope.TagWrapper(r.Context(),
    pyroscope.Labels("endpoint", "/checkout"),
    func(ctx context.Context) {
      // Code inside has "endpoint=/checkout" label
      // in the profiler - useful for filtering hot paths
      checkoutService.Process(ctx, r)
    },
  )
}
```

**PARCA - EBPF SYSTEM-WIDE PROFILING:**

```yaml
# parca-agent DaemonSet - profiles all pods without code changes
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: parca-agent
spec:
  template:
    spec:
      hostPID: true # Required: access host process IDs
      containers:
        - name: parca-agent
          image: ghcr.io/parca-dev/parca-agent:latest
          args:
            - --node=$(NODE_NAME)
            - --remote-store-address=parca.monitoring:7070
            - --remote-store-bearer-token-file=/var/run/secrets/kubernetes.io/serviceaccount/token
          securityContext:
            privileged: true # Required for eBPF
            capabilities:
              add:
                - SYS_ADMIN # eBPF map creation
                - SYS_PTRACE # Process inspection
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 300m
              memory: 256Mi
```

---

### 🔄 The Complete Picture - End-to-End Flow

**PROFILING-DRIVEN INCIDENT INVESTIGATION:**

```
[Alert: P99 latency > 500ms for 5 minutes]
  ↓
[Check RED metrics]
  Rate: normal. Errors: 0.1%. P99: 520ms. P50: 90ms.
  → Tail latency issue (P50 fine, P99 bad)
  ↓
[Check distributed traces (Jaeger)]
  Filter: duration > 400ms
  Finding: all slow traces have a slow span
    in "recommendation-service.getRecommendations()"
  Span duration: 380-490ms
  → Slow span identified. But WHY is it slow?
  ↓
[Check continuous profiling (Pyroscope)]
  Service: recommendation-api
  Time: incident window (last 30 min)
  Profile type: CPU
  Finding: `MatrixFactorization.computeSimilarity()`
  takes 45% of CPU (was 12% 2 hours ago)
  Diff vs 2 hours ago: this function grew 4x
  ↓
[Root cause]
  `computeSimilarity()` is called for each request.
  The user-item matrix grew from 10,000 items to
  40,000 items after a batch data import completed
  2 hours ago. O(n²) algorithm: 10k²=100M operations
  vs 40k²=1.6B operations → 16x slower computation.
  ↓
[Fix]
  Short-term: add result cache (LRU, 1-hour TTL)
  Long-term: switch to approximate nearest-neighbor
    algorithm (FAISS/ScaNN) for O(n log n) scaling
  ↓
[Resolution]
  Cache deployed. P99 drops to 85ms within 5 min.
  Investigation + fix total time: 22 minutes.
  Without profiling: estimated 4-6 hours.
```

---

### 💻 Code Example

**Example 1 - BAD: One-off profiling only:**

```bash
# BAD: enabling pprof endpoint without continuous profiling
# Only works for debugging if you know WHEN to capture
# Cannot compare "before" and "after" a regression

# Go: pprof HTTP endpoint (NOT continuous profiling)
import _ "net/http/pprof"
http.ListenAndServe(":6060", nil)

# Usage: curl http://service:6060/debug/pprof/profile?seconds=30
# Problem 1: you must know to capture NOW
# Problem 2: no historical comparison available
# Problem 3: the regression happened 3 weeks ago - no data
# Problem 4: one-time capture misses intermittent issues
```

**Example 2 - GOOD: Continuous profiling with diff:**

```go
// GOOD: continuous profiling via Pyroscope
// Stores profiles every 10s, 30-day retention
// Enables diff between any two time windows

func main() {
  // Start continuous profiling
  // This runs in background, < 1% overhead
  profiler, err := pyroscope.Start(pyroscope.Config{
    ApplicationName: "recommendation-api",
    ServerAddress:   "http://pyroscope:4040",
    ProfileTypes:    []pyroscope.ProfileType{
      pyroscope.ProfileCPU,
      pyroscope.ProfileInuseSpace,
      pyroscope.ProfileGoroutines,
    },
    Tags: map[string]string{
      "version": version.String(),
    },
  })
  if err != nil {
    // Log but do not fail: profiling is non-critical
    log.Warnf("Profiling init failed: %v", err)
  } else {
    defer profiler.Stop()
  }

  // Normal application startup continues...
  startHTTPServer()
}

// Using Pyroscope UI after an incident:
// 1. Open: http://pyroscope:4040
// 2. Select: recommendation-api
// 3. Select: "Compare" mode
// 4. Left: time range BEFORE regression
//    Right: time range DURING regression
// 5. Flame graph diff shows which functions grew
```

**Example 3 - Goroutine leak detection:**

```go
// Goroutine leaks are invisible to metrics until the
// service runs out of memory. Profile shows them instantly.

// BAD: goroutine leak (channel never read)
func processEvents(events <-chan Event) {
  for event := range events {
    go func() {
      // This goroutine blocks if notifyUpstream is slow
      // New goroutines accumulate faster than they finish
      err := notifyUpstream(event)
      if err != nil {
        // Error ignored, goroutine exits normally
        return
      }
    }()
  }
}

// In Pyroscope goroutine profile (after 1 hour):
// goroutine profile shows:
//   50,000 goroutines blocked on notifyUpstream()
//   (vs expected 10-20 concurrent)
//   → goroutine leak confirmed

// GOOD: bounded goroutine pool
func processEvents(events <-chan Event) {
  sem := make(chan struct{}, 20) // max 20 concurrent
  for event := range events {
    sem <- struct{}{}
    go func(e Event) {
      defer func() { <-sem }()
      if err := notifyUpstream(e); err != nil {
        log.Warn("upstream notify failed", "err", err)
      }
    }(event)
  }
}
// Goroutine profile now shows: max 20 concurrent
// Memory leak eliminated
```

---

### ⚖️ Comparison Table

| Tool                 | Approach             | Languages                    | Code change? | Overhead   | Best for                             |
| -------------------- | -------------------- | ---------------------------- | ------------ | ---------- | ------------------------------------ |
| Pyroscope            | SDK/agent sampling   | Java, Go, Python, Ruby, .NET | Agent or SDK | < 1% CPU   | Service-level profiling with tags    |
| Parca                | eBPF kernel sampling | Any (kernel-level)           | None         | < 1% CPU   | System-wide, no-code profiling       |
| async-profiler       | Java agent           | Java/JVM                     | Agent only   | < 2% CPU   | Deep JVM profiling (JIT, GC)         |
| Go pprof (on-demand) | HTTP endpoint        | Go                           | Import only  | 0% at rest | On-demand debugging (not continuous) |
| Datadog Profiler     | Agent                | Java, Go, Python             | Agent        | ~2% CPU    | Integrated with Datadog APM          |
| JVM Flight Recorder  | JVM built-in         | Java                         | JVM flag     | < 1%       | Java production profiling            |

**Profile types and use cases:**

| Profile type     | Detects                                      | Primary tool                  |
| ---------------- | -------------------------------------------- | ----------------------------- |
| CPU              | Slow functions, inefficient algorithms       | Pyroscope CPU, async-profiler |
| Heap allocation  | Memory-heavy code paths, allocation pressure | Pyroscope Alloc, Go pprof     |
| Goroutine/thread | Goroutine leaks, thread pool saturation      | Pyroscope Goroutines          |
| Mutex contention | Lock contention causing latency              | Pyroscope Mutex, JVM JFR      |
| Block profile    | I/O blocking, channel waits                  | Go pprof block, JVM JFR       |

---

### ⚠️ Common Misconceptions

| Misconception                                    | Reality                                                                                                                                                                                                                                                                                                                       |
| ------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Profiling in production slows the service"      | Continuous (statistical) profiling at 100 Hz has < 1% CPU overhead. This is the standard for Pyroscope, Parca, async-profiler in production mode. Deterministic profiling (records every call) is different - never use that in production.                                                                                   |
| "Metrics are sufficient to find CPU regressions" | Metrics show that CPU utilization is 80% (high). They do not show which function is consuming the CPU. Profiling shows the function. Without profiling, CPU regression investigation is guesswork.                                                                                                                            |
| "I can use traces to find hot code paths"        | Traces show which service is slow and which operation type is slow. They do not show which specific function within the service is consuming CPU. A trace span "RecommendationService.getRecommendations" at 400ms is slow - but which of the 50 functions called within that span is the bottleneck? Profiling answers this. |
| "One-off profiling is sufficient"                | Gradual regressions are invisible without historical comparison. A function that grew from 5% to 35% over 3 weeks is impossible to identify with a one-time profile (it shows 35% but you have no baseline to compare).                                                                                                       |
| "Continuous profiling is complex to set up"      | Adding a Pyroscope Java agent requires one JVM flag. Adding the Go SDK requires 5 lines of code. Parca requires no code changes. The operational overhead of running the Pyroscope server is comparable to running Prometheus.                                                                                                |

---

### 🚨 Failure Modes & Diagnosis

**Missing the gradual performance regression**

**Symptom:**
SLO burn rate fires after 3 weeks of gradual latency
degradation. Post-mortem: "We had no visibility into
when the regression started or which code change
caused it." Time to root cause: 4 hours. Time to
fix: 2 hours. Total incident duration: 6 hours.
Without continuous profiling, the team had to:
(1) bisect recent deployments, (2) reproduce the
issue in staging, (3) run one-off profiles.

**Root Cause:**
No continuous profiling. The team relies on
metrics (shows "something is slow") and traces
(shows "this service is slow") but cannot identify
which function regressed.

**Fix:**
Deploy Pyroscope and instrument all services.
Configure 30-day profile retention. The next gradual
regression will be found in minutes via the diff
view.

---

**Profiler causing GC pressure (Java anti-pattern)**

**Symptom:**
After adding Pyroscope to a Java service, GC pause
duration increases from 50ms to 200ms. The profiler
is causing GC pressure worse than the problem it
was added to detect.

**Root Cause:**
Pyroscope in `spy` mode for Java creates intermediate
objects during stack frame serialisation at each
sampling interval. At 100 Hz with many threads, the
allocation rate from the profiler can be significant.

**Diagnosis:**

```bash
# Check Pyroscope allocation overhead
# Look for pyroscope in heap allocation profile:
# If pyroscope-related classes appear in top-N allocators:
# reduce sampling rate or switch to JFR mode

-Dpyroscope.profiles.interval=20s  # Reduce from 10s to 20s
-Dpyroscope.format=jfr              # JFR mode: lower overhead
# JFR (Java Flight Recorder) mode uses built-in JVM
# profiling infrastructure - lower overhead than
# Pyroscope's default spy mode
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `What Is Observability` - profiling as the fourth
  pillar beyond logs, metrics, and traces
- `Distributed Tracing Fundamentals` - traces show
  WHERE the latency is (which service, which span);
  profiling shows WHAT CODE causes it

**Builds On This (learn these next):**

- `eBPF for Observability` - the kernel-level mechanism
  that Parca uses for zero-code profiling
- `Platform Observability Engineering` - deploying
  continuous profiling as a platform service across
  all production services

**Alternatives / Comparisons:**

- `JVM Flight Recorder` (Java-only): built into the
  JVM, very low overhead, excellent for Java. Pyroscope
  can use JFR as its backend. Use JFR for Java; Pyroscope
  for language-agnostic continuous storage and UI.
- `Linux perf / async-profiler`: one-off profiling
  tools. Lower overhead than JVM agents but no
  continuous storage or historical comparison.

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ DEFINITION   │ Statistical sampling of call stacks at   │
│              │ 100 Hz, stored continuously with time    │
│              │ → historical comparison via diff mode    │
├──────────────┼──────────────────────────────────────────┤
│ OVERHEAD     │ < 1% CPU for sampling profilers          │
│              │ Safe to run continuously in production   │
├──────────────┼──────────────────────────────────────────┤
│ PROFILE TYPES│ CPU: which function consumes cycles      │
│              │ Heap: which code allocates memory        │
│              │ Goroutine: concurrency leaks             │
│              │ Mutex: lock contention                   │
├──────────────┼──────────────────────────────────────────┤
│ TOOLS        │ Pyroscope: language-agnostic, SDK/agent  │
│              │ Parca: eBPF, no code changes required    │
│              │ async-profiler: Java-specific, deep JVM  │
├──────────────┼──────────────────────────────────────────┤
│ FLAME GRAPH  │ Width = % CPU/memory. Widest = bottleneck│
│              │ Diff mode: red = grew, blue = shrunk     │
├──────────────┼──────────────────────────────────────────┤
│ ANSWERS WHAT │ "Which function consumed the CPU         │
│ METRICS CANT │  during this latency spike?"             │
│              │ "Which code change caused regression?"   │
├──────────────┼──────────────────────────────────────────┤
│ 4TH PILLAR   │ Logs + Metrics + Traces + Profiles       │
│              │ Profiles = the missing production debug  │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ eBPF for Observability, Platform Obs.    │
└─────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Historical comparison is the key to detecting gradual
regressions that point-in-time observations miss.
This principle applies beyond profiling: capacity
trend dashboards (growth this week vs last week),
test coverage trends (coverage has been declining
2% per sprint for 10 sprints), build time trends
(build 3 minutes slower per quarter = test suite
growth without cleanup), code complexity trends
(cyclomatic complexity growing in specific modules).
A metric without a historical baseline can only tell
you the current state. A metric compared to its
past tells you the direction, velocity, and inflection
points. Design your observability system to support
historical comparison, not just current-state display.

---

### 💡 The Surprising Truth

The most counterintuitive continuous profiling insight:
adding continuous profiling to production typically
reveals that the bottleneck everyone assumed (database,
network, external API) is not the actual bottleneck.
Teams that add Pyroscope often discover that 40-60%
of their CPU is consumed by serialisation/deserialisation
(JSON marshaling, protobuf encoding) or by logging
(expensive string formatting in DEBUG logs left enabled
in production). These are not the hypotheses engineers
test first during a latency investigation - they check
the database first. The profiler skips the guessing
and points directly at the actual call stack. In one
documented case (Cloudflare), continuous profiling
revealed that a single `time.Now()` call in a hot
path (called on every request for logging) was consuming
3% of all CPU in production due to OS kernel syscall
overhead. No metric or trace would ever have pointed
to `time.Now()` as a bottleneck. The profiler did.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **[EXPLAIN]** Describe how statistical sampling
   profiling works and why it has < 1% overhead
   compared to deterministic profiling.
2. **[INSTRUMENT]** Add Pyroscope continuous profiling
   to a Java or Go service, including the correct
   profile types and tags for Kubernetes deployment.
3. **[USE]** Describe the investigation process for
   a gradual latency regression using the Pyroscope
   diff view. What steps do you take and what do
   you look for in the flame graph?
4. **[COMPARE]** Explain what traces show, what profiles
   show, and why you need both. Give a concrete
   example where traces identify a slow service but
   only profiles identify the specific function.
5. **[DESIGN]** Architect a continuous profiling
   deployment for 50 services on Kubernetes. Include:
   storage estimate, Kubernetes deployment approach,
   integration with Grafana, and profile retention
   policy.

---

### 🧠 Think About This Before We Continue

**Q1.** A CPU flame graph shows that `processRequest()`
is 85% wide (85% of CPU time), and within it:
`validateInput()` is 60% wide, within that
`regexMatcher.match()` is 55% wide. What does this
tell you? Which function should you optimise first?
Is the problem definitively `regexMatcher.match()`?
_Hint: The flame graph shows the call stack distribution.
processRequest() being 85% wide means 85% of CPU is
spent in processRequest() and its callees. Within that,
validateInput() is 60% wide = 60% of processRequest()'s
CPU is in validateInput(). Within validateInput(),
regexMatcher.match() is 55% wide = 55% of validateInput()'s
CPU. So: 85% x 60% x 55% = ~28% of total CPU is in
regexMatcher.match(). This is the leaf - the actual hot
function. Optimise regexMatcher.match() first: pre-compile
the regex pattern instead of compiling on every call.
Or: cache the validation results if the same inputs appear
frequently._

**Q2.** After a large data import, your service's
heap allocation profile shows that
`DataNormalizer.normalize()` grew from 2 MB/s to
200 MB/s of allocation rate. GC pauses increased
from 20ms to 800ms. What does this pattern tell you?
What are the two most likely root causes? How do you
confirm each?
_Hint: High allocation rate → many short-lived objects
created → frequent GC → long GC pauses. Root cause 1:
the new data is larger per record (10,000 items → 1M
items after import). The same O(n) allocation code
now allocates 100x more. Confirm: trace the data size
and compare allocation per record (profile with trace_id
tag to isolate specific request types). Root cause 2:
a code path that was rare is now frequent (e.g.,
DataNormalizer.normalize() was called for edge-case
records that were < 1% of data; now they are 50%
of data). Confirm: add a counter with record_type label
to see which types are processed. Fix: reduce allocations
in the hot path: pool and reuse objects (sync.Pool in
Go, object pooling in Java) or move to streaming
processing to avoid holding all data in memory._

**Q3 (TYPE G):** You are the platform observability
lead. Continuous profiling is not deployed anywhere.
Make the case to the VP of Engineering for deploying
Pyroscope across all 100 services in production.
Include: (a) the observable gap it fills, (b) the
cost (infrastructure, engineering time), (c) the
incident ROI based on two specific incident types
it prevents or shortens, (d) the deployment plan,
(e) the success metrics.
_Hint: (a) Gap: metrics show WHAT is slow (CPU 80%,
P99 high). Traces show WHERE the latency is (which
service, span). But WHICH CODE FUNCTION is causing
it? Only profiling answers this. Without it: 4-6h
of bisection and guesswork per CPU regression incident.
(b) Cost: Pyroscope server: 2 vCPU, 8 GB RAM, 500
GB SSD (30 days, 100 services at ~5 MB/service/day).
~$300/month cloud cost. Engineering: 2 weeks to deploy
agent to all services + Grafana integration. (c) ROI:
(i) Gradual regression (happens 2x/year): without profiling
6h investigation. With profiling: 20 min. Saves 11.5h
x engineer hourly rate x 2 = $2,300/year. (ii) Memory
leak detection: without profiling: OOM crash, 2h
incident, root cause unclear. With profiling: memory
allocation spike visible before OOM, 15 min to diagnose.
Saves 1h x 12 oncall incidents/year x rate = $6,000/year.
Total ROI: $8,300/year vs $3,600/year cost = 2.3x ROI,
not counting customer impact prevention. (d) Deploy:
week 1 Pyroscope server. Weeks 2-3 Java agent to top-20
critical services. Week 4-6 remaining services. (e)
Success metrics: 90% service coverage (profiling data
available), MTTI (mean time to identify root cause)
for CPU-related incidents decreases from 4h to 30min,
profiling-assisted root cause cited in > 80% of
CPU/memory-related post-mortems._

---

### 🎯 Interview Deep-Dive

**Q1: "What is continuous profiling and how does it
differ from on-demand profiling?"**
_Why they ask:_ Tests whether the engineer understands
the fourth pillar of observability.
_Strong answer includes:_

- On-demand: capture a profile now, see current state.
  Cannot show historical regression. Must know to
  capture at the right moment.
- Continuous: profile stored every 10-30 seconds with
  timestamps for 30 days. Historical comparison via
  diff view. Shows gradual regressions over weeks.
- Why it matters: gradual regressions (a function
  growing from 5% to 35% CPU over 3 weeks) are
  invisible without historical data. No alert fires
  until SLO breach. Continuous profiling shows the
  regression immediately in the diff view.
- Overhead: < 1% CPU via statistical sampling. Safe
  for production use.

**Q2: "You have a service where P99 latency increased
from 150ms to 350ms over 3 weeks. No errors, no
infrastructure changes. What is your investigation
approach using continuous profiling?"**
_Why they ask:_ Tests ability to apply the tool to a
real investigation scenario.
_Strong answer includes:_

- Open Pyroscope, select the service, use diff mode:
  baseline = 3-4 weeks ago, comparison = today.
- Examine the CPU flame graph diff. Functions in red
  (grew) are regression candidates.
- Identify the widest red function at the leaf level
  (the actual hot function, not the parent caller).
- Check the git history: was there a code change to
  that function 3 weeks ago?
- Alternatives if no code change: check data volume
  growth (O(n) algorithm with growing n), dependency
  version change (library update), configuration
  change (new feature flag enabling expensive path).
- The diff mode gives a specific function to investigate
  in minutes, not hours.

**Q3: "What is a flame graph and how do you read it?"**
_Why they ask:_ Baseline technical knowledge for
profiling discussions.
_Strong answer includes:_

- Horizontal bars, each representing a function.
- Width = proportion of CPU time (or memory) consumed
  by that function and all its callees.
- Bottom = entry points (main, handleRequest, etc.).
- Top = leaf functions (actual CPU-consuming code).
- The widest leaf bar = the hottest function = the
  best target for optimisation.
- Diff mode: red = grew since baseline, blue = shrunk.
  The widest red bar at the leaf = the function that
  regressed.
- Practical insight: optimising a wide bar at the
  MIDDLE of the flame graph (a function that calls
  many sub-functions) is less effective than optimising
  the wide leaf (the actual expensive operation).
  The leaf is where CPU is actually consumed; the
  middle bar is wide because of what it calls.

---

## OBS-028 - Continuous Profiling (Pyroscope, Parca)

> Entry stub. Generate full content using Master Prompt v3.0.
