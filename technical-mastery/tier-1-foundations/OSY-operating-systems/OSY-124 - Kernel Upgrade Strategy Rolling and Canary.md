---
id: OSY-124
title: Kernel Upgrade Strategy Rolling and Canary
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-108, OSY-120, OSY-121
used_by: []
related: OSY-108, OSY-120, OSY-123
tags:
  - kernel-upgrade
  - rolling-update
  - canary
  - live-patch
  - production
  - strategy
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 124
permalink: /technical-mastery/osy/kernel-upgrade-strategy/
---

## TL;DR

Kernel upgrades in production require: canary deployment
(1-5% of fleet first), automated rollback on regression,
and blue/green draining for stateful workloads. For critical
CVEs: use live patching (ksplice/livepatch) to avoid reboots.
For planned upgrades: rolling maintenance with cordon/drain
in Kubernetes. Never upgrade an entire fleet simultaneously
without validation.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-124 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | kernel upgrade, canary deployment, rolling update, live patching, kernel CVE |
| **Prerequisites** | OSY-108, OSY-120, OSY-121 |

---

### Why Kernel Upgrades Are Risky

```
Kernel upgrade risks:
  
  1. Behavioral changes:
     Scheduler algorithm changes: different thread priorities
     Memory management changes: OOM killer behavior
     sysctl defaults changed: different network behavior
     Example: Linux 5.0 changed tcp_wmem defaults; some
     services lost throughput until reconfigured
     
  2. Driver/module compatibility:
     Custom kernel modules: may not compile for new kernel
     DKMS modules: auto-recompile (can fail silently)
     Out-of-tree drivers: common in enterprise/GPU hardware
     
  3. Regression in specific workloads:
     CFS scheduler changes can affect latency-sensitive Java
     THP changes can cause GC pause regressions
     io_uring changes can affect async-heavy apps
     
  4. Reboot requirement:
     Live patching cannot cover all changes
     Most kernel upgrades require reboot
     Reboot = downtime (for non-HA), failover, reconnections
     
  5. glibc/libc changes:
     Major OS updates (Ubuntu 18 -> 20 -> 22): new glibc
     Java native code: may be linked against specific glibc version
```

---

### Canary Strategy

```
Phase 1: Development/Staging Validation (1-2 weeks)
  
  Target: non-production hosts only
  Steps:
    1. Upgrade staging cluster to new kernel
    2. Run full test suite (unit, integration, load)
    3. Compare: response latency, GC pause, CPU utilization
    4. Check: startup time, memory footprint
    5. Soak test: 48+ hours under realistic load
    
  Success criteria:
    - No test regressions
    - p99 latency within +5% of baseline
    - No unexpected OOM events
    - No sysctl parameter needs changes

Phase 2: Canary Production (1-5% of fleet, 1 week)
  
  Target: 1-5 production hosts (lowest-traffic, non-critical)
  Steps:
    1. Select canary hosts (not stateful, not primary shard)
    2. Upgrade and reboot during low-traffic window
    3. Monitor intensively:
       - CPU, memory, network metrics
       - Application p50/p99 latency
       - Error rates
       - GC behavior
    4. Compare: canary hosts vs rest of fleet (A/B comparison)
    
  Automated rollback triggers:
    - p99 latency increases > 20% for 10 minutes
    - Error rate increases > 0.1%
    - Any OOM event
    - CPU utilization increases > 15% (same load)

Phase 3: Gradual Rollout (10% -> 25% -> 50% -> 100%)
  
  Each wave:
    Wait: 24-48 hours between waves
    Monitor: same metrics as canary
    Gate: pass success criteria before next wave
    
  Rollback plan per wave:
    Wave 1 rollback: restore from snapshot
    Wave 2+: may need to re-image (faster)
    Kubernetes: node drain, remove from pool, rebuild

Phase 4: Full Rollout
  
  Use maintenance windows for remaining hosts
  Drain and reboot node by node (Kubernetes: cordon + drain)
  Never reboot all hosts simultaneously
```

---

### Kubernetes Node Upgrade Procedure

```bash
# 1. Identify nodes to upgrade
kubectl get nodes -o wide | grep old-kernel-version

# 2. Cordon node (no new pods scheduled here)
kubectl cordon node-01

# 3. Drain node (evict all pods with grace period)
kubectl drain node-01 \
  --ignore-daemonsets \  # don't evict daemonsets
  --delete-emptydir-data \  # delete emptyDir volumes
  --grace-period=60  # wait 60s for graceful shutdown

# Drain may fail if: pod with PodDisruptionBudget cannot be evicted
# Check: kubectl get pdb -A

# 4. SSH to node; perform upgrade
ssh node-01
apt-get update
apt-get upgrade -y linux-image-5.15.0-91-generic
# or for RHEL: yum update kernel

# 5. Reboot
reboot

# 6. Wait for node to rejoin cluster
kubectl wait --for=condition=Ready node/node-01 --timeout=5m

# 7. Verify new kernel
kubectl get node node-01 -o jsonpath='{.status.nodeInfo.kernelVersion}'

# 8. Uncordon (allow pods to be scheduled again)
kubectl uncordon node-01

# 9. Monitor for 10 minutes before doing next node
watch kubectl get pods -A | grep -v Running

# Rollback if issues:
# kubectl cordon node-01
# kubectl drain node-01 --force --ignore-daemonsets
# Boot from old kernel (GRUB: select previous kernel)
# grub2-set-default "Previous kernel entry name"
# kubectl uncordon node-01
```

---

### Live Patching (No Reboot Required)

```
Live patching: apply security fixes to running kernel
WITHOUT rebooting. Limited scope: cannot change kernel
interfaces or data structures.

Tools:
  Canonical Livepatch (Ubuntu):
    sudo snap install canonical-livepatch
    sudo canonical-livepatch enable $TOKEN
    canonical-livepatch status
    
  Red Hat Kernel Live Patching:
    # RHEL 8/9:
    yum install kpatch-patch-$(uname -r | tr -d '-')
    systemctl enable kpatch
    kpatch list  # show applied patches
    
  Oracle Ksplice:
    # Enterprise; supports RHEL, Ubuntu
    uptrack-install  # install updates to running kernel
    uptrack-show     # show pending updates

What live patching covers:
  Critical CVEs in kernel networking, memory management
  Privilege escalation fixes
  Remote code execution fixes
  
What live patching cannot cover:
  New kernel features (io_uring, new cgroup behavior)
  ABI-breaking changes
  Major subsystem rewrites
  
Strategy: use live patching for CVE response (critical/high);
use planned reboots for kernel version upgrades.

Monitoring live patch status fleet-wide:
  # Prometheus + custom exporter:
  uptrack-uname -r  # shows "effective kernel version"
  # If behind: alert team for patch application
```

---

### CVE Response vs Planned Upgrade Matrix

| Scenario | Approach | Urgency | Method |
|----------|----------|---------|--------|
| Critical CVE (CVSS 9+) | Live patch first; reboot later | Immediate | Livepatch + scheduled reboot |
| High CVE (CVSS 7-9) | Schedule reboot within 7 days | 1 week | Canary -> rolling |
| Medium CVE | Include in next planned upgrade | 30 days | Canary -> rolling |
| New kernel feature needed | Planned upgrade cycle | Quarterly | Full canary + rolling |
| LTS end-of-life | Major OS upgrade | Before EOL | Extended process |

---

### Rollback Planning

```
Before any upgrade: document rollback procedure
  
Option 1: GRUB kernel selection (fastest rollback)
  Previous kernel remains installed by default
  On rollback: select previous kernel in GRUB
  # Or set as default:
  grub2-set-default "$(grub2-editenv list | grep 'saved_entry' | head -1)"
  Requires: console/bastion access to reboot with GRUB selection
  
Option 2: Snapshot/AMI-based rollback (cloud)
  Before upgrade: take AMI/snapshot of host
  On rollback: launch from snapshot
  Requires: immutable infra; terminate and replace
  
Option 3: Blue/Green host pools (safest for Kubernetes)
  Blue pool: current kernel; serving production traffic
  Green pool: new kernel; canary/warmup
  Switch: traffic routed from blue to green gradually
  Rollback: route all traffic back to blue pool
  
Rollback success criteria:
  Metrics return to pre-upgrade baseline within 10 minutes
  No data loss
  All services operational
```
