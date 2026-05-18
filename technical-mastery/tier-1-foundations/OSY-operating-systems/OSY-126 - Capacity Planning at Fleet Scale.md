---
id: OSY-126
title: Capacity Planning at Fleet Scale
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-121, OSY-123, OSY-125
used_by: []
related: OSY-121, OSY-123, OSY-127
tags:
  - capacity-planning
  - fleet
  - scaling
  - metrics
  - forecasting
  - production
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 126
permalink: /technical-mastery/osy/capacity-planning-fleet-scale/
---

## TL;DR

Fleet-scale capacity planning: combining OS-level resource
metrics (CPU, memory, disk I/O) with application load patterns
to predict when you'll run out of capacity. Key inputs: current
utilization rates, growth rate, seasonal patterns, and headroom
requirements. Output: a capacity budget with provisioning
triggers before degradation begins.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-126 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | capacity planning, fleet management, scaling, resource forecasting, CPU memory disk |
| **Prerequisites** | OSY-121, OSY-123, OSY-125 |

---

### Capacity Planning Methodology

```
Step 1: Establish current utilization baseline
  
  For each resource dimension:
    CPU: average and peak utilization per host
    Memory: working set RSS, not just heap
    Disk I/O: throughput and IOPS utilization %
    Network: ingress/egress bandwidth % of NIC capacity
    
  Measure: 30-day baseline (captures weekly patterns)
  Capture: p50, p95, p99, max for each metric
  
  Tools:
    Prometheus queries for historical data:
    
    # CPU p99 over 30 days:
    quantile_over_time(0.99,
      rate(node_cpu_seconds_total{mode!="idle"}[5m])[30d:5m]
    )
    
    # Memory high watermark:
    max_over_time(
      node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes
      [30d:5m]
    )

Step 2: Identify headroom (current capacity reserve)

  CPU headroom: 100% - current_p99_utilization
    If p99 = 65%: headroom = 35%
    Safe threshold: maintain 30% headroom
    Headroom remaining for growth: 5%
    
  Memory headroom: (total - max_RSS) / total
    If 64GB host, max RSS = 50GB: headroom = 14GB (22%)
    Safe threshold: maintain 20% headroom
    
  When headroom falls below threshold: provision more capacity

Step 3: Measure growth rate
  
  Request growth rate (weekly):
    This week: 12K req/s
    Last week: 11K req/s
    Growth: 9% weekly
    
  Resource growth follows request growth (approximately):
    CPU: grows proportionally (if not limited by other bottleneck)
    Memory: may grow sublinearly if caches saturate early
    
  Extrapolate using linear regression or exponential smoothing:
    Week +4: 12K * (1.09)^4 = 16.9K req/s
    At 16.9K req/s: CPU hits threshold (when?)

Step 4: Calculate time-to-capacity

  Current CPU p99: 65%
  Threshold: 70% (30% headroom goal; currently at 35%)
  Growth: 9% weekly request volume
  
  CPU grows proportionally:
    Each 9% request growth -> 9% CPU growth (approximately)
    
  Weeks to threshold:
    65% * (1.09)^n = 70%
    (1.09)^n = 70/65 = 1.077
    n = log(1.077) / log(1.09) = 0.85 weeks
    
  Conclusion: needs more capacity in ~1 week!
  Action: provision now (provisioning lead time: 2-3 days)
```

---

### OS-Level Capacity Signals

```
CPU Capacity Signals:

  Warning: load average > N_CPU * 1.5 for > 5 minutes
  Critical: p99 CPU utilization > 80%
  Action trigger: p95 utilization > 70% sustained 1 week
  
  Run queue saturation (better signal than utilization):
    vmstat: r column (processes waiting for CPU)
    If r > N_CPU consistently: CPU is oversubscribed
    
  Context switch rate growing:
    Increasing cs rate without request volume growth:
    -> Lock contention growing (needs code fix, not hardware)

Memory Capacity Signals:

  Warning: available memory < 20% of total
  Critical: swap usage > 0
  Action trigger: working set RSS growing at > 5%/week
  
  Memory growth categories:
    Legitimate (growing cache to working set): OK, reaches plateau
    Linear unbounded growth: leak; fix in code, don't provision hardware
    
  Separate: application RSS growth vs OS page cache growth
    Application: /proc/$PID/status VmRSS
    Page cache: free -h "buff/cache" column
    
  Only provision hardware for APPLICATION memory growth
  Page cache: grows/shrinks automatically; not a capacity issue

Disk Capacity Signals:

  Disk space:
    Warning: < 20% free
    Critical: < 10% free
    Action: provision more storage
    
  Disk I/O (throughput/IOPS):
    Warning: sustained > 70% device utilization
    Critical: sustained > 90% (queuing builds)
    
  Log growth (common Java issue):
    logrotate configured? Check retention = daily, keep=30
    Log volume: estimate from current log rate * retention days
    Alert: if projected disk usage hits 80% in 30 days

Network Capacity:

  Typical NIC: 10Gbps or 25Gbps in cloud
  Warning: > 50% of NIC bandwidth utilized
  (network I/O sharing NIC with kernel operations)
  
  For services with high egress (video, large payloads):
    Plan: CDN offload before NIC saturation
```

---

### Capacity Budget Model

```
Production host specification:
  CPU: 32 vCPU
  RAM: 128GB
  Disk: 2TB NVMe
  Network: 25Gbps NIC

Running: Java API service, 20 containers per host

Current per-container allocation:
  CPU request: 1 vCPU, limit: 2 vCPU
  Memory request: 4GB, limit: 6GB
  JVM: -Xmx4g (75% of 6GB limit)

Current host utilization (at 100K req/s fleet-wide):
  CPU: 24 vCPU consumed (75% of 32)
  Memory: 96GB RSS (75% of 128GB)
  Disk I/O: 30% utilization
  Network: 5Gbps (20% of 25Gbps)

Bottleneck: CPU and Memory both at 75% (too high)
Current headroom: 25% (below 30% target)

At target 30% headroom:
  CPU: 32 * 0.70 = 22.4 vCPU max workload
  But current: 24 vCPU -> ALREADY over target
  
Action needed: provision additional hosts
  Required: reduce workload per host to 22 vCPU
  Current: 20 containers, 2 vCPU each = 40 vCPU potential load
  Active at peak: 24 vCPU (12 containers fully active)
  Solution: add 20% more hosts; reduce containers per host
  Or: scale the number of hosts in fleet by 20%
  
Forecast: 9% weekly request growth
  Week 1: 100K -> 109K req/s
  Week 2: 109K -> 119K
  ...
  Week 8: ~200K req/s (near 2x)
  Required hosts: 2x current fleet
  Provisioning lead time: 2 weeks (cloud: auto-scaling faster)
```

---

### Automation: Capacity Alerts

```yaml
# Prometheus alerting rules for capacity management

groups:
- name: capacity-planning
  rules:
  
  # Time-to-disk-full prediction
  - alert: DiskWillFillIn7Days
    expr: >
      predict_linear(
        node_filesystem_avail_bytes{mountpoint="/"}[7d],
        7 * 24 * 3600
      ) < 0
    for: 1h
    labels:
      severity: warning
    annotations:
      summary: >
        Host {{$labels.instance}} disk will fill within 7 days.
        Current: {{ printf "%.1f" $value }}GB available.
  
  # CPU trending toward saturation
  - alert: CPUCapacityTrend
    expr: >
      predict_linear(
        rate(node_cpu_seconds_total{mode!="idle"}[1h])[24h:1h],
        7 * 24 * 3600
      ) > 0.80
    for: 2h
    labels:
      severity: warning
    annotations:
      summary: >
        Host {{$labels.instance}} CPU utilization predicted
        to reach 80% within 7 days at current growth rate.
  
  # Memory trending toward exhaustion
  - alert: MemoryCapacityTrend
    expr: >
      predict_linear(
        (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes)
        [24h:1h],
        7 * 24 * 3600
      ) > node_memory_MemTotal_bytes * 0.90
    for: 2h
    labels:
      severity: warning
```

---

### Capacity Planning Pitfalls

| Pitfall | Problem | Prevention |
|---------|---------|------------|
| Planning only for average load | Peak load (sales events, end-of-month) overwhelms capacity | Plan for p95 load + 30% buffer |
| Using heap for memory planning | Ignores native memory (threads, Metaspace) | Plan for full RSS, not just heap |
| Linear CPU scaling assumption | Lock contention creates superlinear CPU growth at scale | Profile under load to find contention hotspots |
| Ignoring startup time | Auto-scaling can't keep up with burst if startup = 120s | Optimize or pre-warm JVM instances |
| Disk planning without log growth | Log files fill disk gradually and silently | Include log volumes in capacity model |
