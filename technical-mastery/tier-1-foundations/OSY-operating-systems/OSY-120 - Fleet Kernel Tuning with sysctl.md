---
id: OSY-120
title: Fleet Kernel Tuning with sysctl
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-116, OSY-119
used_by: []
related: OSY-116, OSY-119, OSY-121
tags:
  - sysctl
  - kernel-tuning
  - fleet
  - production
  - configuration
  - network
  - memory
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 120
permalink: /technical-mastery/osy/fleet-kernel-tuning-sysctl/
---

## TL;DR

sysctl provides runtime kernel parameter tuning without
reboot. For Java production fleets: optimize for low
latency (network buffers, scheduling), memory efficiency
(dirty page thresholds, swappiness), and high connection
count (ephemeral ports, TIME_WAIT handling). Always
benchmark before deploying fleet-wide; wrong sysctl
settings can degrade performance or cause instability.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-120 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | sysctl, kernel tuning, fleet management, network performance, Java production |
| **Prerequisites** | OSY-116, OSY-119 |

---

### Understanding sysctl

```bash
# sysctl: interface to /proc/sys kernel parameter tree
# Read a parameter:
sysctl vm.swappiness          # current value
cat /proc/sys/vm/swappiness   # same thing

# Set temporarily (lost on reboot):
sysctl -w vm.swappiness=1

# Set permanently:
echo "vm.swappiness=1" >> /etc/sysctl.d/99-java-prod.conf
sysctl -p /etc/sysctl.d/99-java-prod.conf  # apply without reboot

# Show all parameters:
sysctl -a 2>/dev/null | wc -l  # ~1000+ parameters

# Structure:
# /proc/sys/kernel/  -> kernel-specific settings
# /proc/sys/vm/      -> virtual memory management
# /proc/sys/net/     -> networking stack
# /proc/sys/fs/      -> filesystem settings

# Namespace: parameters NOT adjustable per-container
# (sysctl in containers: some are namespaced, some are host-global)
# Namespaced: net.ipv4.*, net.ipv6.*, net.core.somaxconn (since 4.15)
# NOT namespaced (requires privileged): vm.*, kernel.*, fs.*
```

---

### Canonical Java Production sysctl Profile

```bash
# File: /etc/sysctl.d/99-java-production.conf
# Validated for: RHEL 8/9, Ubuntu 20.04/22.04
# Purpose: Java web service on Linux (general production)
# One change per test; validate with your workload before fleet deploy

# ===== VIRTUAL MEMORY =====

# Swappiness: how aggressively kernel uses swap
# Java: swapping = latency spikes; minimize swap use
vm.swappiness=1
# Not 0: value of 0 can cause OOM instead of swap in emergencies
# 1 = "don't swap unless critical" but keep swap available

# Dirty page ratio: when writeback starts
# Default: background at 10%, forced at 20% of RAM
# Problem: on 64GB system: 20% = 12.8GB dirty at once
#   -> Periodic 12GB flush -> I/O spike -> iowait spike
# Fix: lower threshold for continuous small flushes
vm.dirty_background_ratio=2
vm.dirty_ratio=5
# Or: use absolute values (better for large RAM systems)
# vm.dirty_background_bytes=67108864   # 64MB
# vm.dirty_bytes=134217728             # 128MB

# Writeback interval: how often kernel flushes dirty pages
vm.dirty_writeback_centisecs=500   # default: 3000 (30s)
# Lower: more frequent small flushes; lower iowait spikes

# Overcommit: allow kernel to allocate more virtual than physical
# Java: JVM commits virtual memory ahead of actual use
vm.overcommit_memory=1   # allow overcommit (good for JVM)
# vm.overcommit_ratio not needed when overcommit_memory=1

# Huge pages (transparent): madvise = only when requested
# THP with always: background collapser causes latency spikes
kernel.mm.transparent_hugepage.enabled=madvise
kernel.mm.transparent_hugepage.defrag=defer+madvise
# To set at boot: add to /etc/rc.local or use tuned profile

# ===== NETWORKING =====

# TCP connection backlog: max pending connections before accept()
# Default: 128 (far too low for high-traffic services)
net.core.somaxconn=32768
net.ipv4.tcp_max_syn_backlog=8192

# TCP socket buffers: for high-throughput services
net.core.rmem_default=262144
net.core.rmem_max=16777216      # 16MB max receive buffer
net.core.wmem_default=262144
net.core.wmem_max=16777216      # 16MB max send buffer
net.ipv4.tcp_rmem=4096 87380 16777216
net.ipv4.tcp_wmem=4096 65536 16777216

# TIME_WAIT reuse: allow reuse of TIME_WAIT sockets
net.ipv4.tcp_tw_reuse=1   # safe to enable
# DO NOT set tcp_tw_recycle (removed in Linux 4.12; dangerous with NAT)

# Ephemeral port range: available ports for outbound connections
# Default: 32768-60999 (28231 ports)
# For services making many outbound connections:
net.ipv4.ip_local_port_range=1024 65535

# Max file descriptors per process
# Java services: each socket = 1 fd; need > default 1024
# Set in /etc/security/limits.conf instead for per-process control
# But kernel max:
fs.file-max=2097152

# TCP keepalive: detect dead connections
# Default: 2 hours (too slow for modern apps; load balancers time out)
net.ipv4.tcp_keepalive_time=60    # start keepalive after 60s idle
net.ipv4.tcp_keepalive_intvl=10   # probe every 10s
net.ipv4.tcp_keepalive_probes=3   # close after 3 failed probes

# SYN flood protection:
net.ipv4.tcp_syncookies=1  # should already be enabled by default

# ===== KERNEL / SCHEDULING =====

# Scheduler migration cost: how long before moving thread between CPUs
# Lower: threads migrate more freely (better load balance, worse cache)
# Higher: threads stay on same CPU (better cache, possibly imbalanced)
kernel.sched_migration_cost_ns=5000000   # 5ms (default: 500000)
# For NUMA systems: threads staying on same NUMA node = better

# Min granularity: minimum time slice before preemption
kernel.sched_min_granularity_ns=10000000   # 10ms
kernel.sched_wakeup_granularity_ns=15000000

# ===== FILE SYSTEM =====

# Inotify limits: for services watching many files (config watchers)
fs.inotify.max_user_watches=524288    # default: 8192
fs.inotify.max_user_instances=512

# Max open file descriptors (kernel level):
fs.file-max=2097152
```

---

### Applying sysctl Changes Safely

```bash
# Step 1: Record current baseline metrics
echo "=== BASELINE $(date) ===" > /tmp/sysctl-baseline.txt
vmstat 1 60 >> /tmp/sysctl-baseline.txt &
iostat -x 1 60 >> /tmp/sysctl-baseline.txt &
wait

# Step 2: Apply ONE change at a time
sysctl -w vm.dirty_background_ratio=2

# Step 3: Run load test (same workload as before change)
# Collect metrics during load test

# Step 4: Compare metrics
# Did p99 latency improve?
# Did iowait change?
# Did context switches change?

# Step 5: If improvement: persist the change
echo "vm.dirty_background_ratio=2" \
  >> /etc/sysctl.d/99-java-production.conf

# Step 6: Validate on 1 host before fleet rollout
# Monitor for 24 hours minimum

# Fleet rollout via Ansible:
# ansible-playbook -i inventory sysctl-tuning.yml --limit "10%"
# Wait 1 hour; check metrics
# Then: --limit "50%" ; wait ; --limit "100%"

# Emergency rollback:
# Reboot (sysctl changes are not persistent by default)
# Or: sysctl -w vm.dirty_background_ratio=10  (revert to default)
```

---

### Container sysctl Configuration

```yaml
# Kubernetes: some sysctl are safe (namespaced); others unsafe (host)
# Safe (namespaced - can set per-pod):
#   net.ipv4.tcp_syncookies
#   net.ipv4.tcp_fin_timeout
#   net.ipv4.tcp_keepalive_time
#   net.ipv4.ip_local_port_range
#   net.ipv6.*
#   kernel.shm*
#   net.core.somaxconn (kernel 4.15+)

# Pod spec:
apiVersion: v1
kind: Pod
spec:
  securityContext:
    sysctls:
    - name: net.ipv4.tcp_keepalive_time
      value: "60"
    - name: net.core.somaxconn
      value: "32768"
    # Unsafe sysctls need kubelet --allowed-unsafe-sysctls flag:
    # net.ipv4.tcp_tw_reuse (modifies host network stack)
```

---

### sysctl Quick Reference

| Parameter | Default | Recommended | Effect |
|-----------|---------|-------------|--------|
| `vm.swappiness` | 60 | 1 | Minimize swap |
| `vm.dirty_background_ratio` | 10 | 2 | Smaller flush bursts |
| `vm.dirty_ratio` | 20 | 5 | Prevent huge dirty backlog |
| `net.core.somaxconn` | 128 | 32768 | High connection acceptance |
| `net.ipv4.tcp_tw_reuse` | 0 | 1 | Recycle TIME_WAIT |
| `net.ipv4.ip_local_port_range` | 32768-60999 | 1024-65535 | More ephemeral ports |
| `net.ipv4.tcp_keepalive_time` | 7200 | 60 | Detect dead connections |
| `fs.inotify.max_user_watches` | 8192 | 524288 | Config reload support |
| `THP enabled` | always | madvise | Prevent latency spikes |
| `kernel.sched_migration_cost_ns` | 500000 | 5000000 | Reduce cache thrash |

---

### Monitoring sysctl Drift

```bash
# Detect if current settings differ from intended:
sysctl -a 2>/dev/null > /tmp/current-sysctl.txt
diff /etc/sysctl-expected.txt /tmp/current-sysctl.txt
# If diff is non-empty: drift (manual change, OS update, etc.)

# Ansible task to validate:
- name: Validate kernel parameters
  command: sysctl vm.swappiness
  register: swappiness_val
  failed_when: "'vm.swappiness = 1' not in swappiness_val.stdout"
```
