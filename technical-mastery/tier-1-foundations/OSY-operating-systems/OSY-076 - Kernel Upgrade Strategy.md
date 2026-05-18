---
id: OSY-076
title: Kernel Upgrade Strategy
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-028, OSY-030
used_by: OSY-124
related: OSY-071, OSY-107, OSY-124
tags:
  - kernel-upgrade
  - patch-management
  - kpatch
  - kexec
  - rolling-upgrade
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 76
permalink: /technical-mastery/osy/kernel-upgrade-strategy/
---

## TL;DR

Kernel upgrades require system reboot in most cases.
Strategy: test in staging, canary deploy to production,
monitor for regressions. Live patching (kpatch, kGraft)
applies security patches without reboot for CVEs.
Kubernetes: drain node before upgrade, cordon to prevent
new pods, then uncordon. Never upgrade all nodes at once.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-076 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | kernel upgrade, kpatch, live patching, canary, node drain |
| **Prerequisites** | OSY-028, OSY-030 |

---

### Kernel Upgrade Process

```
Traditional kernel upgrade (with reboot):
  
  1. Check current kernel:
     uname -r                    # running kernel version
     ls /boot/vmlinuz-*          # installed kernels
     
  2. Install new kernel package:
     apt-get update
     apt-get install linux-image-$(uname -r)   # same version (not new)
     apt-get install linux-image-6.5.0-generic # specific version
     # or: unattended-upgrades for automatic security patches
     
  3. Verify new kernel is default:
     grep GRUB_DEFAULT /etc/default/grub
     update-grub  # regenerate grub config
     
  4. Test in staging:
     reboot
     uname -r    # verify new kernel loaded
     
  5. Validate: services start, performance baseline
  
  6. Production: canary -> rolling -> fleet
  
Kernel version types (Ubuntu LTS example):
  linux-image-generic:      latest upstream kernel
  linux-image-aws:          AWS-optimized kernel
  linux-image-generic-hwe:  Hardware Enablement (newer kernel on older OS)
  
  For stability: stick to distro LTS kernel
    Security patches backported to LTS version
    No new features (risk of regression)
```

---

### Live Kernel Patching (No Reboot)

```
Problem: security CVE requires kernel update but rebooting
  production cluster is expensive (SLA, coordination, time)

kpatch (Red Hat) and kGraft (SUSE):
  Apply patches to running kernel without reboot
  Method: function-level hot-patching
    1. New patched function compiled
    2. Original function's first bytes replaced with jump to new function
    3. All new calls: go to patched version
    4. Old calls in-flight: complete normally
    
  Limitations:
    Cannot change kernel data structures
    Cannot patch very complex code paths
    Temporary fix: still need reboot eventually for full kernel update
    
  Commercial: AWS provides kernel live patching for EC2
    aws configure kernel-live-patching --state enabled
    
  RHEL/CentOS: subscription required
    dnf install kpatch-patch
    
  Ubuntu livepatch:
    canonical-livepatch enable <token>
    livepatch status

kexec: fast reboot (swap kernel without hardware init)
  kexec -l /boot/vmlinuz --initrd=/boot/initrd
  kexec -e  # immediate kernel swap (no hardware reinit)
  
  Cuts reboot time: 60 seconds -> 5-10 seconds
  Skips: BIOS/UEFI POST, hardware detection
  Used in: cloud instances for fast kernel upgrades
```

---

### Kubernetes Node Kernel Upgrade

```bash
# Kubernetes node upgrade procedure (zero-downtime):

# Step 1: Identify target node
NODE="node-01"
kubectl get node $NODE -o wide   # verify current state

# Step 2: Mark as unschedulable (no new pods)
kubectl cordon $NODE
# Node is now "SchedulingDisabled" but existing pods keep running

# Step 3: Drain (evict all pods gracefully)
kubectl drain $NODE \
  --ignore-daemonsets \       # DaemonSets stay on node
  --delete-emptydir-data \    # allow pods with emptyDir volumes
  --grace-period=60           # give pods 60s to terminate

# Drain does:
#   For each pod: delete Pod object -> kubelet terminates it
#   Deployment/StatefulSet: controller schedules pod on another node
#   Waits until all pods are gone from node
#   DaemonSet pods: stay (--ignore-daemonsets)

# Step 4: SSH to node and upgrade kernel
ssh $NODE "sudo apt-get upgrade linux-image-aws && sudo reboot"
# Wait for node to come back...

# Step 5: Verify node is Ready
kubectl wait --for=condition=Ready node/$NODE --timeout=120s

# Step 6: Uncordon (allow new pods)
kubectl uncordon $NODE
# Node: "Ready" (not SchedulingDisabled)

# Step 7: Monitor for issues
kubectl get events --field-selector involvedObject.name=$NODE
kubectl top node $NODE

# Repeat for next node (one at a time or small batches)
```

---

### Rolling Upgrade Strategy

```
Fleet upgrade strategy (production):
  
  Stage 0: Staging environment
    Upgrade all staging nodes
    Run full test suite
    Monitor for 24-48 hours
    
  Stage 1: Canary (1-5% of fleet)
    Upgrade 1-3 nodes in production
    Monitor: error rates, latency, CPU, memory
    Wait: at least 1-2 hours
    
  Stage 2: Early adopters (20% of fleet)
    Upgrade a larger subset
    Include all geographic regions
    Monitor 2-4 hours
    
  Stage 3: Full rollout (remaining nodes)
    Upgrade in batches of 20-25%
    30 minute pause between batches
    Automated rollback if error rate increases
    
  Rollback trigger:
    Error rate > baseline + 5%
    p99 latency > baseline + 20%
    Any node with kernel panic (dmesg or /var/log/kern.log)
    
  Post-upgrade monitoring (48 hours):
    Watch for: memory leaks, performance regressions
    OOM kill events: dmesg | grep "Killed process"
    Kernel warnings: dmesg -l warn
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "kpatch/live patching means you never need to reboot" | Live patching handles SECURITY patches for critical CVEs without reboot. It is temporary. Data structure changes, driver updates, and major kernel version upgrades still require a reboot. Live patching extends the window between reboots but does not eliminate the need for them |
| "Kubernetes node drain guarantees zero downtime" | Drain is graceful but not zero-downtime guaranteed. If a Pod has PodDisruptionBudget violations, drain may timeout. If pods don't properly handle SIGTERM, they may be force-killed. If the deployment has only 1 replica, drain = downtime. Always configure: replicas > 1, PodDisruptionBudget, proper SIGTERM handling |

---

### Quick Reference Card

| Concept | Key Fact |
|---------|---------|
| uname -r | Current running kernel version |
| kpatch | Live security patching; no reboot; temporary fix only |
| kexec | Fast reboot (5-10s vs 60s); skips hardware init |
| kubectl cordon | Mark node unschedulable; existing pods keep running |
| kubectl drain | Evict all pods gracefully before node maintenance |
| Canary strategy | 1% -> 20% -> 100% with monitor+pause between stages |
