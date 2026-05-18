---
id: OSY-121
title: Observability Platform Design for OS Layer
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-085, OSY-099, OSY-116, OSY-120
used_by: []
related: OSY-116, OSY-120, OSY-122
tags:
  - observability
  - monitoring
  - platform
  - metrics
  - eBPF
  - production
  - architecture
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 121
permalink: /technical-mastery/osy/observability-platform-design/
---

## TL;DR

Designing an OS-layer observability platform for Java fleets:
what to collect (CPU, memory, I/O, network, kernel events),
how to collect it (Prometheus node_exporter, eBPF-based
collectors, JMX), where to store it (time-series DB), and
how to alert (SLO-based). The goal: detect performance
regressions and capacity issues before users notice them.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-121 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | observability, monitoring, Prometheus, eBPF, node_exporter, SLO, Java fleet |
| **Prerequisites** | OSY-085, OSY-099, OSY-116, OSY-120 |

---

### What to Observe at the OS Layer

```
Four signals framework (Google SRE):
  Latency: how long does each operation take?
  Traffic: how many operations per second?
  Errors: how many operations fail?
  Saturation: how full is the system?
  
OS metrics map to four signals:

  CPU:
    Utilization (%us, %sy, %wa) -> saturation signal
    Context switches -> latency signal (overhead)
    Run queue length -> saturation signal
    
  Memory:
    RSS per process -> saturation signal
    Page faults (minor vs major) -> latency signal
    OOM events -> error signal
    Swap usage -> saturation signal
    
  Disk I/O:
    IOPS, throughput -> traffic signal
    Await (latency) -> latency signal
    %util -> saturation signal
    
  Network:
    Packets in/out -> traffic signal
    Retransmits -> error signal
    TCP connection states (ESTABLISHED, TIME_WAIT) -> saturation
    
  JVM-specific (from JMX or JFR):
    GC pause duration/frequency -> latency signal
    Heap usage % -> saturation signal
    Thread count -> saturation signal
    Class loading rate -> traffic signal
```

---

### Prometheus + node_exporter Architecture

```
Fleet observability stack:

  Hosts (each Java service host):
    node_exporter: collects OS metrics
      CPU, memory, disk, network, filesystem, systemd units
      Exposes: /metrics endpoint on port 9100
      
    JMX exporter (Java-specific):
      Sidecar JAR or Prometheus Java agent
      Collects: JVM heap, GC, threads, class loading
      Exposes: /metrics on configurable port
      
    Custom application metrics:
      Micrometer (Spring Boot): auto-instruments REST endpoints
      Exposes: /actuator/prometheus
      
  Prometheus servers:
    Scrape node_exporter every 15s (OS metrics)
    Scrape JMX exporter every 30s (JVM metrics)
    Scrape app metrics every 15s (request metrics)
    Retention: 15 days of raw data
    
  Thanos / Cortex (long-term storage):
    Remote write from Prometheus
    Retention: 1-2 years of aggregated data
    Global query across multiple data centers
    
  Grafana:
    Dashboards: one per tier (OS dashboard, JVM dashboard, app dashboard)
    Alerting: route to PagerDuty / Slack
    
  Alertmanager:
    Deduplication: don't send 1000 alerts for 1 incident
    Routing: critical -> PagerDuty, warning -> Slack
    Silencing: during maintenance windows
```

---

### Key Metrics and Alert Thresholds

```
OS Layer Alerts (Prometheus PromQL):

# CPU saturation (load average vs CPU count)
alert: HighLoadAverage
expr: node_load1 > node_cpu_count * 2
for: 5m
annotations:
  summary: "Host {{$labels.instance}}: load average high"
  
# Iowait (disk I/O blocking CPUs)
alert: HighIOWait  
expr: rate(node_cpu_seconds_total{mode="iowait"}[5m]) > 0.2
for: 5m
annotations:
  summary: "{{$labels.instance}}: 20%+ iowait"

# Disk space running out
alert: DiskSpaceLow
expr: (node_filesystem_avail_bytes / 
       node_filesystem_size_bytes) * 100 < 15
for: 5m
annotations:
  summary: "{{$labels.instance}} {{$labels.mountpoint}}: < 15% free"

# Memory pressure (using swap)
alert: SwapUsageHigh
expr: (node_memory_SwapUsed_bytes / 
       node_memory_SwapTotal_bytes) * 100 > 20
for: 5m
annotations:
  summary: "Swap > 20% on {{$labels.instance}}"

# Network errors / drops
alert: NetworkErrors
expr: rate(node_network_receive_errs_total[5m]) > 10
for: 2m

JVM Layer Alerts:

# GC pause time high (affecting latency)
alert: GCPauseHigh
expr: rate(jvm_gc_pause_seconds_sum[5m]) / 
      rate(jvm_gc_pause_seconds_count[5m]) > 0.1
for: 5m
annotations:
  summary: "GC avg pause > 100ms on {{$labels.instance}}"

# Heap approaching OOM
alert: HeapUsageHigh
expr: (jvm_memory_used_bytes{area="heap"} / 
       jvm_memory_max_bytes{area="heap"}) > 0.85
for: 2m
annotations:
  summary: "JVM heap > 85% on {{$labels.instance}}"

# Thread pool saturation (Micrometer)
alert: ThreadPoolSaturated
expr: executor_pool_size / executor_pool_max >= 1
for: 1m
```

---

### eBPF-Based OS Observability

```
Traditional tools (vmstat, iostat): polling-based
  Read /proc/sys files; aggregated stats; limited detail

eBPF: attach probes to kernel code paths directly
  Per-event data: see individual operations
  Near-zero overhead: kernel-native execution

Tools:

  BCC (BPF Compiler Collection):
    biolatency: histogram of disk I/O latency distribution
    tcpretrans: trace TCP retransmissions with socket info
    execsnoop: trace all process executions on the system
    opensnoop: trace all file opens
    runqlat: CPU run queue latency histogram
    
  bpftrace: high-level eBPF scripting language
    # Disk I/O latency distribution in real time:
    bpftrace -e '
      tracepoint:block:block_rq_insert {
        @start[args->dev, args->sector] = nsecs;
      }
      tracepoint:block:block_rq_complete 
      /@start[args->dev, args->sector]/ {
        @usecs = hist(
          (nsecs - @start[args->dev, args->sector]) / 1000
        );
        delete(@start[args->dev, args->sector]);
      }
      interval:s:10 { print(@usecs); clear(@usecs); }'
    
  async-profiler (Java-specific eBPF):
    # CPU profiling with eBPF-based stack sampling:
    ./profiler.sh -d 60 -f profile.html $PID
    # Generates flamegraph showing actual Java code on CPU
    # Works with: JVM perf-events, eBPF async-profiler

  Beyla (Grafana): eBPF-based auto-instrumentation
    # No JVM agent; instruments at syscall level
    # Traces: HTTP requests, gRPC calls, SQL queries
    # Works across: Java, Go, Python, Node.js
```

---

### Capacity Planning Signals

```
Leading indicators (precede actual problems):
  CPU utilization trending toward 70%: plan capacity increase
  Disk growth rate: X GB/day -> full in N days
  Connection count growing: approaching limit
  GC frequency increasing: heap sizing issue
  
Lagging indicators (problems already occurring):
  p99 latency degrading: users affected
  Error rate increasing: SLO violation
  OOM events: containers being killed
  
Capacity model example:

  Current: 10K req/s on 4 nodes (2.5K/node)
  CPU utilization: 45% at 2.5K req/s
  
  At 100% CPU: 5.5K req/s per node (extrapolated)
  Safety margin: max 70% CPU = 3.85K req/s per node
  
  For 20K req/s: 20000 / 3850 = 5.2 nodes -> 6 nodes
  
  Disk growth: logs at 2GB/day, 30-day retention -> 60GB/node
  Plan: 100GB log volume (buffer for bursts)
```

---

### Observability Quick Reference

| Signal | Tool | Collection | Alert Threshold |
|--------|------|-----------|-----------------|
| CPU utilization | node_exporter | 15s scrape | > 80% sustained 5m |
| Load average | node_exporter | 15s scrape | > N_CPU * 2 |
| Memory | node_exporter | 15s scrape | < 10% free |
| Disk I/O wait | node_exporter | 15s scrape | > 20% 5m |
| Disk space | node_exporter | 15s scrape | < 15% free |
| JVM heap | JMX exporter | 30s scrape | > 85% |
| GC pause | Micrometer | 30s scrape | avg > 100ms |
| Context switches | node_exporter | 15s scrape | > 500K/s |
| Network errors | node_exporter | 15s scrape | > 10/s |
| I/O latency | eBPF/biolatency | Triggered | p99 > 50ms |
