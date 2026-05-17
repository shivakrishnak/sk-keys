---
id: OBS-030
title: "USE Method (Utilization, Saturation, Errors)"
category: Observability & SRE
tier: tier-6-infrastructure-devops
folder: OBS-observability-sre
difficulty: ★☆☆
depends_on: OBS-006, OBS-001, OBS-002
used_by: OBS-031, OBS-010, OBS-038
related: OBS-006, OBS-029, OBS-031, OBS-038
tags:
  - observability
  - metrics
  - sre
  - devops
  - foundational
  - pattern
  - mental-model
status: complete
version: 4
layout: default
parent: "Observability & SRE"
grand_parent: "Technical Dictionary"
nav_order: 30
permalink: /obs/use-method-utilization-saturation-errors/
---

# OBS-030 - USE Method (Utilization, Saturation, Errors)

⚡ TL;DR - USE is a three-metric framework for
monitoring resources (CPUs, disks, memory, network
interfaces, connection pools): Utilization (how busy),
Saturation (how much is queued/waiting), Errors (how
many failures). It answers "is this resource a
bottleneck?" and complements RED (which answers "are
users affected?").

| #030 | Category: Observability & SRE | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Metrics -- Types, What Is Observability, Three Pillars | |
| **Used by:** | Golden Signals, Dashboards, Capacity Planning | |
| **Related:** | Metrics Types, RED Method, Golden Signals, Capacity Planning | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An engineer monitors 50 metrics for a database server:
CPU, memory, disk read IOPS, disk write IOPS, disk
read latency, disk write latency, disk throughput,
network bytes in, network bytes out, network packets
in, network packets out, network errors, TCP connection
count, TCP retransmits, JVM heap, GC count, GC time,
thread pool active, thread pool queued... When
performance degrades, which of these 50 metrics is
the bottleneck? Each metric is plausible but the
engineer cannot know which to investigate first.

**THE INVENTION:**
Brendan Gregg formalised the USE Method: for every
resource, collect exactly three metrics - Utilization,
Saturation, Errors. These three metrics determine
whether the resource is a bottleneck. The method
provides a systematic checklist that prevents both
missing a real bottleneck and wasting time on metrics
that cannot reveal bottlenecks.

---

### 📘 Textbook Definition

**USE Method** - a performance analysis methodology
for resource-based systems (created by Brendan Gregg
at Sun Microsystems):

- **Utilization** (U): the percentage of time the
  resource was busy, or the fraction of capacity used.
  Answers: "How much of this resource is being consumed?"
  ```
  CPU utilization: cpu_usage_percent
  Disk utilization: disk_io_time_seconds / total_seconds
  Connection pool: active_connections / max_connections
  ```

- **Saturation** (S): the degree to which the resource
  has extra work it cannot service yet - a queue.
  High saturation = resource is overloaded.
  Answers: "Is work piling up waiting for this resource?"
  ```
  CPU run queue: node_load1 (1-minute load average)
  Disk queue depth: disk_io_queue_length
  Thread pool queue: thread_pool_queued_tasks
  ```

- **Errors** (E): the count of error events for
  the resource (separate from application errors -
  these are hardware/OS/system-level errors).
  Answers: "Is this resource experiencing failures?"
  ```
  Disk errors: disk_io_errors_total
  Network errors: network_transmit_errs_total
  Memory errors: memory_edac_correctable_errors_total
  ```

**Origin:** Brendan Gregg, "Systems Performance" book
and blog. Method for structured resource performance
analysis. Complements RED Method (for services).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
USE tells you if a resource (CPU, disk, memory,
network) is a bottleneck: how busy it is (Utilization),
whether work is queuing up (Saturation), and whether
it is failing (Errors).

> A toll booth: Utilization = how often the booth
> is occupied (70% busy). Saturation = how many cars
> are queued waiting (5 cars in line). Errors = how
> many transactions failed (credit card declined 3 times).
> At 70% utilization with 5 cars queuing: near saturation.
> At 30% utilization with 0 cars queuing: healthy.
> At 99% utilization with 50 cars queuing: bottleneck.
> The three numbers together tell you whether to
> add more toll booths (capacity) or investigate
> transaction failures (errors).

---

### 🔩 First Principles Explanation

**WHAT MAKES A RESOURCE A BOTTLENECK:**

```
A resource becomes a bottleneck when it cannot serve
all requests in time. This is characterised by:

Stage 1 - Approaching capacity (Utilization high):
  Resource busy most of the time.
  Work starts to queue occasionally.
  Latency rises slightly under load.
  U: 70-90%. S: low (short queues). E: 0

Stage 2 - Saturated (Saturation high):
  Resource at 100% utilization for extended periods.
  Queue grows: work arrives faster than it is served.
  Response times increase proportionally to queue length.
  U: 90-100%. S: HIGH (long queues). E: maybe

Stage 3 - Failing (Errors):
  Resource experiencing hardware/OS-level failures.
  Can cause saturation (failed operations retried).
  Can cause data loss or corruption.
  U: varies. S: varies. E: HIGH

Key insight: HIGH UTILIZATION alone is not a bottleneck.
  80% CPU with 0 saturation = efficient usage, no bottleneck.
  90% disk IO with 0 queue = healthy, near capacity.

HIGH SATURATION = bottleneck.
  A resource with 50% utilization but a queue of 100
  tasks is already a bottleneck for those 100 tasks.
```

**THE USE CHECKLIST (per resource):**

```
Resource: CPU
  Utilization: cpu_usage_percent per core + overall
    Warning: > 70% sustained. Critical: > 90%.
  Saturation: node_load1 / nproc (normalised run queue)
    Warning: > 1.0 (more threads runnable than cores)
    Critical: > 4.0 (severe CPU saturation)
  Errors: machine_check_exceptions_total (hardware faults)
    Critical: any value > 0 (hardware failure)

Resource: Memory
  Utilization: 1 - (free + cached) / total
    Warning: > 80%. Critical: > 95%.
  Saturation: vmstat si/so (swap I/O per second)
    Critical: any swap activity = memory pressure
  Errors: memory_edac_correctable/uncorrectable
    Critical: uncorrectable errors > 0

Resource: Network Interface
  Utilization: bytes_transmitted / link_speed
    Warning: > 60% (TCP performance degrades)
    Critical: > 80%
  Saturation: network_transmit_drop_total (drops)
    Critical: increasing drops = TX queue full
  Errors: network_transmit_errs_total
    Critical: any increasing error count

Resource: Disk
  Utilization: disk_io_time_seconds (% time in IO)
    Warning: > 60%. Critical: > 80% (queue building)
  Saturation: disk_io_queue_length
    Warning: > 1. Critical: > 8 (severe queue)
  Errors: disk_io_errors_total, smart_device_errors
    Critical: SMART errors indicate hardware failure

Resource: Connection Pool (application-level)
  Utilization: active / max_connections
    Warning: > 70%. Critical: > 90%.
  Saturation: pending_connection_waits
    Critical: any pending waits (clients blocked)
  Errors: connection_errors_total (timeouts, refused)
    Warning: any rate > 0
```

---

### 🧪 Thought Experiment

**THE USE DIAGNOSIS PROTOCOL:**

A checkout service is slow. RED shows P99 latency
elevated to 3 seconds. Now USE the USE method to
find which resource is the bottleneck:

```
Step 1: CPU
  Utilization: 45% average across 4 cores → Normal
  Saturation: load1/nproc = 0.8 → Normal
  Errors: 0 → Normal
  Verdict: CPU is NOT the bottleneck.

Step 2: Memory
  Utilization: 72% → Elevated but not critical
  Saturation: swap = 0 → No swap → Normal
  Errors: 0 → Normal
  Verdict: Memory is NOT the bottleneck.

Step 3: Network
  Utilization: 35% of 1 Gbps → Normal
  Saturation: drops = 0 → Normal
  Errors: 0 → Normal
  Verdict: Network is NOT the bottleneck.

Step 4: Disk
  Utilization: 95% → CRITICAL
  Saturation: queue depth = 12 → CRITICAL (> 8)
  Errors: 0 → Normal
  Verdict: Disk IS the bottleneck.
  Action: Check disk I/O patterns. Is a
    background job doing excessive writes?
    Is the WAL write-ahead log filling the disk?
    Is the index rebuild happening?
```

Three numbers per resource. Systematic elimination.
The bottleneck found in minutes, not hours.

---

### 🧠 Mental Model / Analogy

> A highway system: Utilization = what fraction of
> road capacity is being used (70% = moderate traffic).
> Saturation = the backup: how many cars are stopped
> in traffic jams (long queues = saturation). Errors =
> accidents that close lanes (hardware failures that
> reduce capacity).
>
> A highway with 70% utilization and no traffic jams
> is healthy. A highway with 50% utilization but 10
> miles of backup (saturation) is a bottleneck - the
> backup is caused by a lane closure (maybe an error)
> or a merge point creating a throughput constraint.
>
> USE tells you to check all three dimensions. A low-
> utilization highway with high saturation signals
> a structural problem, not a capacity problem.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone):**
USE helps you check whether a computer resource (CPU,
disk, memory, network) is causing a performance
problem. Three questions for each resource: how busy
is it? Is work queuing up? Are there failures?

**Level 2 - How to use it (junior):**
When a service is slow, run through the USE checklist
for each major resource. Start with CPU (check
`cpu_usage_percent` and `node_load1`), then memory
(check free memory and swap activity), then disk
(check `disk_io_queue`), then network (check bandwidth
utilization and drops). The resource with high
saturation (queue) is the bottleneck.

**Level 3 - Dashboard design (mid-level):**
Create a USE dashboard alongside your RED dashboard.
RED row 1: service health (user perspective). USE
row 2: CPU, memory, disk, network for the service
host/container. For each resource: utilization panel
(gauge), saturation panel (time series), error panel
(counter). Use consistent thresholds: utilization
> 80% = yellow, saturation > 0 = yellow, errors > 0
= red. The USE dashboard is for diagnosis; RED is
for alerting.

**Level 4 - Capacity planning (senior):**
USE metrics drive capacity planning decisions. CPU
utilization trend (monthly): if growing 5% per month
from 40% baseline, you have ~12 months before hitting
80% threshold. Disk utilization trend: if growing
2 GB/day, you have N days before disk full. Combine
USE saturation trends with traffic growth projections
to predict when additional capacity will be needed.
Create "headroom" dashboards: current utilization
vs capacity limit vs projected growth rate.

**Level 5 - Platform (staff):**
USE as the infrastructure layer of the observability
hierarchy. Platform SLO: every service's host resources
must have USE metrics available to the platform
team. The infrastructure capacity SLO: maintain
< 60% CPU utilization headroom, < 70% memory, < 50%
disk across all production hosts (allowing 2x capacity
burst without hitting saturation). Alert on saturation,
not utilization: a CPU saturation alert fires when
run queue depth > 4 for 5 minutes, not when CPU > 70%.
This prevents false positives from legitimate CPU bursts
that resolve before causing saturation.

---

### ⚙️ How It Works (Mechanism)

**PROMETHEUS - USE METRICS FOR LINUX HOST:**

```promql
# ===== CPU =====
# Utilization: % of time CPU is not idle
100 - (avg by (instance) (
  rate(node_cpu_seconds_total{mode="idle"}[5m])
) * 100)

# Saturation: normalized load average (load1 / nproc)
node_load1
  / count without(cpu, mode) (
      node_cpu_seconds_total{mode="idle"}
    )
# > 1.0 = CPUs overloaded (work queuing)

# Errors: machine check exceptions (hardware)
node_edac_uncorrectable_errors_total

# ===== Memory =====
# Utilization: used fraction (excluding cache/buffers)
1 - (
  node_memory_MemAvailable_bytes
  / node_memory_MemTotal_bytes
)
# > 0.85 = warning

# Saturation: swap activity (any swap = memory pressure)
rate(node_vmstat_pswpin[5m])  # pages swapped in/s
rate(node_vmstat_pswpout[5m]) # pages swapped out/s
# > 0 = memory saturation

# ===== Disk =====
# Utilization: fraction of time disk was busy
rate(node_disk_io_time_seconds_total{
  device="sda"}[5m])
# > 0.8 = near saturation

# Saturation: average IO queue depth
rate(node_disk_io_time_weighted_seconds_total{
  device="sda"}[5m])
# / rate(node_disk_io_time_seconds_total{device="sda"}[5m])
# > 1 = queue building

# ===== Network =====
# Utilization: bandwidth as fraction of link capacity
# (link capacity must be configured manually)
rate(node_network_transmit_bytes_total{
  device="eth0"}[5m]) * 8
  / 1_000_000_000   # divide by link speed in bits

# Saturation: TX drops (queue overflow)
rate(node_network_transmit_drop_total{
  device="eth0"}[5m])
# > 0 = saturation (TX queue full, packets dropped)

# Errors
rate(node_network_transmit_errs_total{
  device="eth0"}[5m])
```

**CONNECTION POOL (application-level USE):**

```java
// Expose HikariCP connection pool USE metrics
// Auto-exposed with Spring Boot Actuator + Micrometer

// Utilization: active / max
hikaricp_connections_active / hikaricp_connections_max

// Saturation: pending acquisition waits
hikaricp_connections_pending
// > 0 = connection pool saturation (threads blocked)

// Errors: timeouts and acquisition failures
rate(hikaricp_connections_timeout_total[5m])
// Any rate > 0 = connection pool errors
// (requests failing due to pool exhaustion)
```

---

### 🔄 The Complete Picture - End-to-End Flow

**USE + RED COMBINED DIAGNOSIS:**

```
[User reports: checkout is slow]
  ↓
[Check RED (service perspective)]
  Rate: normal (500 req/s)
  Errors: 0.2% (slightly elevated)
  Duration P99: 4,500ms (18x normal of 250ms)
  Verdict: service is slow, some errors.
  Infrastructure investigation needed.
  ↓
[USE checklist - run in order of likelihood]

1. Connection Pool (most common for database-backed services)
   Utilization: 95% (WARNING - near max)
   Saturation: 28 pending waits (CRITICAL)
   Errors: 3 timeouts/s (CRITICAL)
   → BOTTLENECK FOUND: Connection pool saturated
   → Requests are waiting up to 3s for a DB connection
   → Some requests timeout waiting (0.2% error rate)
  ↓
[Root cause analysis]
  Why is the connection pool saturated?
  - Connection pool max too small for current load?
  - Database query latency high (connections held longer)?
  - Connection leak (connections not returned)?
  ↓
[USE checklist - database server]
2. CPU (database server):
   Utilization: 35% → Normal
   Saturation: 0.4 (normalized) → Normal
   Verdict: DB CPU not the bottleneck
3. Disk (database server):
   Utilization: 88% (WARNING)
   Saturation: queue depth = 6 (WARNING)
   Errors: 0
   → DB disk is under pressure
   → Queries are slow because disk IO is queuing
  ↓
[Diagnosis complete]
  Root cause: disk I/O saturation on DB host
  → queries take longer
  → connections held longer
  → connection pool saturates
  → requests queue for connections
  → P99 latency 18x normal
  Fix: identify the disk-intensive queries,
    add indexes, or upgrade to faster storage.
```

---

### 💻 Code Example

**Example 1 - BAD: Alerting on utilization alone:**

```yaml
# BAD: alert fires at 80% CPU even if there is
# no saturation (no queuing, no user impact)
# This generates false positives constantly during
# normal traffic spikes

- alert: HighCPUUtilization
  expr: cpu_usage_percent > 80
  # A 5-minute traffic burst pushes CPU to 85%.
  # Run queue stays at 0.8 (below 1.0 threshold).
  # No requests queuing. No user impact.
  # Alert fires. Engineer wakes up. It resolves.
  # This is not a bottleneck - it is efficient usage.
```

**Example 2 - GOOD: Alert on saturation, not utilization:**

```yaml
# GOOD: alert on saturation (queuing)
# CPU at 90% utilization but no saturation = OK
# CPU at 60% utilization with saturation = bottleneck

- alert: CPUSaturation
  expr: |
    node_load1
    / count without (cpu, mode) (
        node_cpu_seconds_total{mode="idle"}
      ) > 2.0
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "CPU saturated on {{ $labels.instance }}"
    description: |
      Normalized load average > 2.0 for 5+ minutes.
      Threads are queuing for CPU time.
      Investigate: high-CPU processes, inefficient queries,
      or capacity insufficient for current load.
    runbook: "https://wiki.internal/runbooks/cpu-saturation"

- alert: ConnectionPoolSaturation
  expr: hikaricp_connections_pending > 0
  for: 2m
  labels:
    severity: page
  annotations:
    summary: "DB connection pool saturated: {{ $value }} waiting"
    description: |
      Threads are blocked waiting for database connections.
      This directly causes request latency spikes.
      Check: slow queries holding connections,
      pool max_size too small, connection leaks.
```

**Example 3 - USE capacity headroom dashboard:**

```promql
# CPU headroom: how far from saturation threshold
# (saturation at load_avg/nproc = 1.0)
# Show "headroom" as remaining until saturation

1.0 - (
  node_load1
  / count without (cpu, mode) (
      node_cpu_seconds_total{mode="idle"}
    )
)
# 0.5 = 50% headroom before CPU saturation
# 0.0 = at saturation point
# Negative = already saturated (CPU overloaded)

# Memory headroom to saturation (swap onset):
node_memory_MemAvailable_bytes
  / node_memory_MemTotal_bytes
# How much available memory remains before swap starts

# Disk headroom: time until disk full at current growth rate
# (based on prediction linear extrapolation)
predict_linear(
  node_filesystem_avail_bytes{mountpoint="/"}[7d],
  86400 * 30   # predict 30 days ahead
)
# Negative value = disk full within 30 days
```

---

### ⚖️ Comparison Table

| Method | Focus | Metrics | Target | Alert? |
|---|---|---|---|---|
| USE | Resources | Utilization, Saturation, Errors | CPU, disk, memory, network, pools | On saturation and errors |
| RED | Services | Rate, Errors, Duration | HTTP APIs, microservices, queues | On errors and duration |
| Golden Signals | Both | Latency, Traffic, Errors, Saturation | Any system | On all four |

**USE per resource summary:**

| Resource | Utilization | Saturation | Errors |
|---|---|---|---|
| CPU | `cpu_usage_percent` | `node_load1 / nproc` | EDAC errors |
| Memory | `1 - available/total` | Swap pages/s | EDAC uncorrectable |
| Disk | `disk_io_time` | `io_queue_length` | SMART errors |
| Network | `bytes / link_capacity` | `transmit_drop_total` | `transmit_errs_total` |
| Connection pool | `active / max` | `pending_waits` | `timeout_total` |
| Thread pool | `active / max` | `queued_tasks` | `rejected_tasks` |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "High utilization = bottleneck" | High utilization means the resource is being used efficiently. Saturation = bottleneck. A CPU at 80% utilization with zero run queue is healthy. A CPU at 40% utilization with a run queue of 8 is a bottleneck. |
| "USE is for servers only" | USE applies to any resource: database connection pools (U=active/max, S=pending, E=timeouts), thread pools (U=active/max, S=queue depth, E=rejected tasks), message queue consumer groups (U=consumer utilization, S=consumer lag, E=consumer errors). |
| "Errors in USE means application errors" | USE Errors are hardware/system/resource-level errors: disk I/O errors, network packet errors, memory hardware errors, connection timeout errors. Application-level business errors are measured in RED. |
| "USE is old-fashioned (just for bare metal)" | USE is the correct framework for any finite-capacity resource. In Kubernetes: CPU request/limit utilization, memory request/limit utilization, pod OOM kills. In cloud: service quota utilization, API rate limit consumption. |
| "I need all 50 metrics from my server" | No. Three metrics per resource. The other 47 metrics may be useful for deep diagnosis of a specific bottleneck, but they are not needed for initial triage. Start with USE. |

---

### 🚨 Failure Modes & Diagnosis

**Memory saturation: swap storm**

**Symptom:**
Service latency suddenly spikes 100x. The RED metrics
show P99 latency going from 100ms to 10 seconds.
CPU utilization is 45% (normal). Disk utilization
suddenly spikes to 90%. The engineer is confused -
why is disk high when it was fine an hour ago?

**Root Cause:**
Memory utilization crossed 95%. The Linux kernel
started swapping memory pages to disk. The "disk
utilization" spike is not disk I/O from the application
- it is the memory subsystem writing (swap out) and
reading (swap in) pages constantly. Every application
memory access that touches a swapped-out page causes
a disk read. A 100ms operation that accesses 10
swapped-out memory pages now takes: 100ms + 10 x
10ms disk latency = 200ms. For cold memory access
patterns: 100ms + 10 x 50ms = 600ms. 10x latency
increase from swap.

**USE Diagnosis:**
```bash
# Check memory USE on the server:
free -h
# Swap: 0/0 total/used = no swap configured
# If: Swap: 4.0G/3.8G = 95% swap used → CRISIS

# Real-time: vmstat 1
# procs: r=run queue, b=blocked on IO
# swap: si=swap-in pages/s, so=swap-out pages/s
# If si or so > 0: memory saturation
vmstat 1 10

# PromQL: swap activity
rate(node_vmstat_pswpin[5m])   # pages swapped in
rate(node_vmstat_pswpout[5m])  # pages swapped out
# Any nonzero value = memory under pressure
```

**Fix:**
1. Immediate: identify and kill the memory-heavy
   process (or add swap-prefetching if intentional)
2. Short term: increase pod memory limit, add more
   RAM, or reduce memory-heavy background jobs
3. Long term: set `vm.swappiness=10` (Linux parameter
   to prefer OOM kill over swap), add memory USE
   saturation alert before swap onset

---

**Disk saturation: IO queue building slowly**

**Symptom:**
Over 3 weeks, P99 database query latency has been
gradually increasing. No incidents. No alarms.
The engineering manager raises concern that P99
has gone from 50ms to 400ms over the past month.

**USE Diagnosis:**
```promql
# Historical disk saturation trend
avg_over_time(
  rate(node_disk_io_time_weighted_seconds_total{
    device="nvme0n1", instance="db-primary"}[5m])
[30d:1h])
# Increasing trend confirms growing disk pressure

# Current queue depth:
rate(node_disk_io_time_weighted_seconds_total[5m])
# / rate(node_disk_io_time_seconds_total[5m])
# If > 2.0: significant queue depth
```

**Root Cause:**
Database has grown. Full table scans that used to
read 10 GB of data now read 40 GB. The nvme disk's
sustained read bandwidth is 3 GB/s. A 40 GB scan
takes 13 seconds (vs 3 seconds at 10 GB). During
this scan, other queries queue behind it.

**Fix:**
Add a missing index (eliminates the full scan),
or partition the table (reduces scan size), or
upgrade to faster storage (higher bandwidth nvme).

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Metrics -- Types (Counter, Gauge, Histogram)` -
  USE metrics use gauges (utilization, saturation)
  and counters (error events)
- `What Is Observability` - USE is the resource-
  monitoring layer of the observability hierarchy

**Builds On This (learn these next):**
- `Golden Signals` - extends USE + RED into a unified
  four-metric framework for any system
- `Capacity Planning with Metrics` - uses USE
  utilization and saturation trends for capacity
  forecasting

**Alternatives / Comparisons:**
- `RED Method` - complementary, for services (user
  experience layer). Use RED + USE together for full
  coverage.
- `Golden Signals` - adds Latency and Traffic to
  create a combined service+resource framework from
  Google SRE Book.

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ USE TARGET   │ Resources: CPU, memory, disk, network,    │
│              │ connection pools, thread pools            │
├──────────────┼───────────────────────────────────────────┤
│ UTILIZATION  │ How busy: cpu_usage%, active/max pool     │
│              │ Warning: > 70-80% sustained               │
├──────────────┼───────────────────────────────────────────┤
│ SATURATION   │ Work queued: load_avg, queue_depth        │
│              │ Critical: > 0 (connections), > 1.0 (CPU) │
│ KEY INSIGHT  │ SATURATION = bottleneck (not utilization) │
├──────────────┼───────────────────────────────────────────┤
│ ERRORS       │ System-level: disk errors, NIC errors,   │
│              │ memory ECC, pool timeouts                 │
│              │ Alert: any rate > 0                       │
├──────────────┼───────────────────────────────────────────┤
│ DIAGNOSIS    │ 1. CPU: usage + load1/nproc + EDAC        │
│ ORDER        │ 2. Memory: avail% + swap_pages/s          │
│              │ 3. Disk: io_time% + queue_depth           │
│              │ 4. Network: bandwidth% + drops + errors   │
│              │ 5. Pools: active/max + pending + timeouts │
├──────────────┼───────────────────────────────────────────┤
│ COMPLEMENT   │ USE = resources (infrastructure layer)    │
│              │ RED = services (user experience layer)    │
│              │ Alert on RED; diagnose with USE           │
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ Alerting on utilization (not saturation)  │
│              │ Confusing swap disk IO with app disk IO   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Golden Signals, Capacity Planning         │
└──────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
High utilization is good (efficient). Saturation is
the problem (queuing = latency). This principle
applies beyond infrastructure: a software team at
80% utilization (most hours productive) is healthy.
A software team at 60% utilization but with a backlog
growing 20% per sprint (saturation) is a bottleneck.
A customer support team answering 90% of tickets
on time (70% utilization) is healthy. The same team
with growing ticket queue (saturation) despite low
utilization is a structural problem (not enough agents,
or each ticket is too complex). In databases: a slow
query at 0.001% of queries can cause I/O saturation
that slows all other queries. 99.999% efficiency
in one bottleneck. The USE pattern: find the saturated
resource; fix the bottleneck; measure again.

---

### 💡 The Surprising Truth

The most counterintuitive USE insight: a system can
have very low utilization on all resources and still
be completely saturated. This happens with synchronous
blocking architectures. Example: a service makes
synchronous database calls. Each call takes 500ms.
With 4 threads and 4-core CPU: CPU utilization = 1%
(threads are sleeping, waiting for the database).
Disk utilization = 2% (only 4 concurrent queries).
Memory utilization = 30%. But the thread pool has
a queue of 200 tasks waiting for those 4 threads.
Every USE utilization metric looks healthy. The
saturation metric (thread pool queue = 200) is the
only indicator of the actual bottleneck: the 4-thread
synchronous architecture. The fix is not more CPU
or disk - it is more threads, or async I/O. USE
saturation catches bottlenecks that utilization
cannot.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **[EXPLAIN]** Explain why high CPU utilization
   (90%) without saturation is not a bottleneck,
   while low CPU utilization (40%) with saturation
   (load average 8 on a 4-core host) is a severe
   bottleneck.
2. **[APPLY]** Given a slow service with P99 latency
   10x normal, run through the USE checklist for
   CPU, memory, disk, and connection pool. Write
   the specific Prometheus queries you would use.
3. **[INSTRUMENT]** Write PromQL queries for the
   USE framework for a Linux host (CPU utilization,
   CPU saturation, memory utilization, memory
   saturation, disk utilization, disk saturation).
4. **[DESIGN]** Design USE-based alerts for a database
   server that avoid false positives from normal
   traffic bursts (alert on saturation, not utilization).
5. **[COMPARE]** Explain the relationship between
   RED and USE and when you would use each. Describe
   a scenario where RED shows a problem but USE
   identifies the actual resource bottleneck.

---

### 🧠 Think About This Before We Continue

**Q1.** A server running a Java service has: CPU 85%
utilization, load average 1.2/4 cores (normalised:
0.3), 0 swap pages, no disk errors, disk IO time 45%.
Is any resource a bottleneck? What is the health
interpretation?
*Hint: CPU at 85% with normalised load 0.3 (below 1.0)
= no saturation. Threads are not queuing for CPU.
The high utilization is efficient use. Memory: 0 swap
= no saturation. Disk: 45% utilization = within range,
check queue depth (not given). Overall: no obvious
bottleneck from the available USE data. If P99 latency
is elevated, the bottleneck is likely not on this host
- check downstream dependencies (database, cache).*

**Q2.** A service has 20 database connection pool
connections (max). Current state: active=18 (90%),
pending=5, timeouts=0.5/second. Describe the USE
state of the connection pool. What is the immediate
impact? What caused it? What are the two fastest fixes?
*Hint: U=90% (near critical). S=5 pending (CRITICAL -
requests are blocked). E=0.5/s (timeouts - requests
are failing). Impact: requests waiting up to connection
acquisition timeout (e.g., 3s), then failing. Causes:
(a) queries are slow (connections held longer), (b)
max_pool_size too small for current traffic, (c)
connection leak (connections not returned). Fast fixes:
(1) increase max_pool_size to 30-40 immediately (minutes
to deploy), (2) identify slow queries holding connections
(check slow query log on DB). Root fix: optimize slow
queries so connections are returned faster.*

**Q3 (TYPE G):** A platform team is responsible for
infrastructure health across 200 services. They need
to build a USE-based capacity dashboard and alerting
system. Design: (a) which resources to monitor for
each service's host, (b) which metrics to expose,
(c) how to normalise across hosts with different
specs (4-core vs 32-core, HDD vs SSD), (d) what
alerting thresholds to apply, (e) how to produce
a "capacity headroom" report for each service used
in quarterly capacity planning.
*Hint: (a) All services: CPU, memory, disk, network,
connection pool. Database services: + disk IOPs, WAL
rate. Cache services: + eviction rate, memory used/max.
(b) Normalised metrics: cpu_saturation=load1/nproc,
mem_saturation=swap_pages/s, disk_saturation=io_queue_depth,
pool_saturation=pending/max. (c) Normalisation: CPU
saturation is already normalised (load/nproc). Disk:
io_time% is hardware-agnostic. Pool: active/max is
already normalised. Network: bytes/link_speed_bits. (d)
Alert thresholds: cpu_saturation > 1.0 for 5m = warning,
> 2.0 = page. disk_saturation > 2 for 5m = warning.
pool_pending > 0 for 2m = warning, > 5 for 5m = page.
(e) Quarterly report: for each service, show 90-day
trend of each USE metric. Predict time to saturation
(regression on saturation metric trend). Flag services
projected to saturate within 90 days for capacity
planning.*

---

### 🎯 Interview Deep-Dive

**Q1: "What is the USE method and how does it differ from RED?"**
*Why they ask:* Tests understanding of the two foundational
monitoring frameworks and their relationship.
*Strong answer includes:*
- USE = Utilization, Saturation, Errors. For resources
  (CPU, memory, disk, network, connection pools).
- RED = Rate, Errors, Duration. For services (APIs,
  microservices, queues).
- Key difference: USE measures infrastructure health
  (is this resource a bottleneck?). RED measures user
  experience (are users affected?).
- Use together: RED identifies a problem exists (P99
  latency elevated). USE identifies the bottleneck
  (connection pool saturated → queries slow → latency high).
- Alert on RED (user impact). Diagnose with USE (find
  bottleneck).

**Q2: "What is the difference between utilization and
saturation? Why does it matter for alerting?"**
*Why they ask:* Discriminates engineers who understand
the method from those who just name the letters.
*Strong answer includes:*
- Utilization: how busy the resource is. High utilization
  = efficient usage. Not necessarily a problem.
- Saturation: work queuing up because the resource
  cannot serve it immediately. Any saturation = bottleneck.
- Why it matters for alerting: alerting on "CPU > 80%"
  fires during normal traffic spikes with zero user
  impact (high utilization, no saturation). Alerting
  on "CPU normalized load > 1.5 for 5 minutes" fires
  only when CPU is actually causing threads to queue
  (saturation = user impact).
- Concrete example: 4-core server, CPU 85%, load
  average 0.8. No saturation. Efficient usage, no alert.
  vs CPU 60%, load average 6.0 (saturation). Threads
  queuing. Alert should fire.

**Q3: "A service is slow. How do you use USE to find the bottleneck?"**
*Why they ask:* Tests ability to apply the method to
a real incident, not just recite the acronym.
*Strong answer includes:*
- Step 1: Check RED (P99 latency elevated, error rate
  normal → pure latency issue, not failures).
- Step 2: USE checklist. Start with most common
  bottlenecks for the service type:
  - Database-backed: check connection pool saturation
    first (pending > 0 = immediate bottleneck)
  - IO-heavy: check disk saturation (io_queue_depth)
  - Compute-heavy: check CPU saturation (load/nproc)
  - Memory-heavy: check memory saturation (swap activity)
- Step 3: Trace the chain. If connection pool saturated:
  why? Check query duration. If queries slow: why?
  Check DB host USE (disk saturation?).
- Each USE finding points to the next USE check
  until the root resource bottleneck is found.

# OBS-025 - USE Method (Utilization, Saturation, Errors)

> Entry stub. Generate full content using Master Prompt v3.0.
