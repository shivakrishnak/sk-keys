---
id: OSY-093
title: CPU Affinity and Pinning
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-020, OSY-021, OSY-057, OSY-065
used_by: []
related: OSY-088, OSY-092, OSY-094, OSY-116
tags:
  - CPU-affinity
  - taskset
  - pinning
  - NUMA
  - latency
  - real-time
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 93
permalink: /technical-mastery/osy/cpu-affinity-pinning/
---

## TL;DR

CPU affinity pins threads or processes to specific CPU cores.
Eliminates cross-NUMA accesses, improves cache utilization
(L1/L2 stay warm), and reduces context switch overhead.
Essential for latency-sensitive workloads (HFT, real-time),
NUMA optimization, and container isolation. Can harm
performance if used incorrectly (artificially starving CPUs).

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-093 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | CPU affinity, taskset, numactl, NUMA pinning, cache warmth |
| **Prerequisites** | OSY-020, OSY-021, OSY-057, OSY-065 |

---

### What Is CPU Affinity?

```
CPU affinity: kernel attribute controlling which CPU cores
a thread or process is ALLOWED to run on.
  
  Affinity mask: bitmap of allowed CPUs
    0b00001111 = CPUs 0-3 only
    0b11110000 = CPUs 4-7 only
    0b11111111 = all CPUs (default)
    
  Why pin to specific CPUs?
  
  1. Cache warmth:
     Thread pinned to CPU 3: its data stays in CPU 3's L1/L2 cache
     Without pinning: OS may migrate thread to CPU 5
       -> CPU 3's L1/L2 must be re-populated (cold cache)
       -> First accesses after migration: DRAM latency (70ns)
       
  2. NUMA-local execution:
     CPU 0-7 on NUMA Node 0; CPU 8-15 on NUMA Node 1
     Pin thread to CPU 0-7: always accesses Node 0 memory locally
     Without pinning: thread may migrate to CPU 8-15
       -> All memory accesses remote (120ns vs 70ns)
       
  3. Isolation:
     Containers: pin to isolated CPU set
     Critical processes: guaranteed CPU access (no sharing)
     Interrupt processing: pin hardware interrupts to specific CPU
     (isolcpus= kernel parameter: remove CPUs from scheduler)
```

---

### CPU Affinity Commands

```bash
# View CPU topology
lscpu | grep -E 'NUMA|Core|Thread|CPU'
numactl --hardware   # shows NUMA node-to-CPU mapping

# Set CPU affinity with taskset
# Pin process to CPUs 0-3:
taskset -c 0-3 java -jar application.jar

# Pin existing process by PID:
taskset -pc 0-3 $PID

# View current affinity of a process:
taskset -pc $PID
# Output: pid 12345's current affinity list: 0-15 (all CPUs)

# NUMA-aware pinning:
# Pin to CPUs AND memory on NUMA Node 0:
numactl --cpunodebind=0 --membind=0 java -jar app.jar

# Pin to CPUs 0-7 (Node 0) with interleaved memory:
numactl --cpunodebind=0 --interleave=all java -jar app.jar

# Java thread-level affinity (requires JNA or JNI):
# Process Affinity API (not built into JDK):
# Library: Java Thread Affinity by Peter Lawrey
# https://github.com/OpenHFT/Java-Thread-Affinity
# AffinityLock.acquireCore(); // acquires an isolated core

# Linux kernel isolation (prevent ANY non-critical work):
# In /etc/default/grub:
# GRUB_CMDLINE_LINUX="isolcpus=4-7 nohz_full=4-7 rcu_nocbs=4-7"
# After grub-update + reboot: CPUs 4-7 excluded from scheduler
# Only threads explicitly pinned to them run there
# Achieves near-deterministic latency for real-time tasks
```

---

### CPU Pinning and NUMA Interaction

```
2-socket server:
  CPU 0-7:  NUMA Node 0 (128GB RAM)
  CPU 8-15: NUMA Node 1 (128GB RAM)
  
BAD: JVM with no affinity (default)
  
  JVM starts: main thread on CPU 0 (Node 0)
  JVM allocates heap: pages on Node 0 (first-touch)
  Worker threads: distributed across CPUs 0-15
  Workers 8-15 (Node 1): ALL object accesses are remote
  Result: 50% of threads run 1.7x slower
  
GOOD: NUMA-pinned JVM
  
  Option A: Pin entire JVM to Node 0
    numactl --cpunodebind=0 --membind=0 java -jar app.jar
    
    Advantage: all accesses local
    Disadvantage: wastes Node 1 CPUs and memory
    Best for: 1 or 2 services per server
    
  Option B: Two JVM instances, one per node
    numactl --cpunodebind=0 --membind=0 java -jar app.jar &
    numactl --cpunodebind=1 --membind=1 java -jar app.jar &
    
    Load balancer: distribute requests between instances
    Advantage: uses all CPUs and RAM
    Best for: stateless services with horizontal scaling
    
  Option C: UseNUMA (JVM-managed interleaving)
    java -XX:+UseNUMA -jar app.jar
    
    JVM allocates TLAB regions per-CPU-local-NUMA-node
    Advantage: automatic; no pinning needed
    Best for: single large JVM instance
```

---

### Interrupt Affinity (IRQ Pinning)

```
Network packets arrive -> NIC generates hardware interrupt
Linux: by default, all NIC interrupts to CPU 0
  CPU 0: interrupt handling + application work
  CPUs 1-N: idle for interrupt work
  Result: CPU 0 saturated; others underutilized
  
Spreading interrupts (RSS: Receive Side Scaling):
  Modern NICs: multiple interrupt queues
  Each queue: map to a different CPU
  
  # Show NIC interrupt mapping:
  cat /proc/interrupts | grep eth0
  
  # Map NIC queue interrupts to specific CPUs:
  # (script: set_irq_affinity.sh from network driver package)
  echo 1 > /proc/irq/56/smp_affinity   # queue 0 -> CPU 0
  echo 2 > /proc/irq/57/smp_affinity   # queue 1 -> CPU 1
  echo 4 > /proc/irq/58/smp_affinity   # queue 2 -> CPU 2
  
  # For NUMA: align NIC queues with NUMA node:
  # NIC on PCIe of NUMA Node 0: IRQs to CPUs 0-7
  # Application threads on CPUs 0-7: data arrives to local cache
  # Reduces cross-socket data transfer
  
  ethtool -L eth0 combined 8  # Set 8 RX/TX queues
  # Then map each to a CPU for optimal locality
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "CPU pinning always improves performance" | Pinning eliminates migration overhead but limits flexibility. If pinned to 4 CPUs and workload spikes, those 4 CPUs saturate while other CPUs idle. For variable workloads: NUMA-aware scheduling (-XX:+UseNUMA) is better than strict pinning. Strict pinning is for ultra-low latency (HFT) where predictability > throughput. |
| "taskset is sufficient for real-time latency" | taskset sets affinity but doesn't prevent other threads from sharing those CPUs. For true isolation: `isolcpus` kernel parameter removes CPUs from the scheduler entirely. Plus: set SCHED_FIFO priority for the critical thread. Plus: disable interrupts on isolated CPUs (irqbalance stop). |
| "All cores on a multi-core CPU are equal" | Modern CPUs have asymmetric cores: P-cores (performance) and E-cores (efficiency) on Intel Alder Lake/Raptor Lake. P-cores have L1/L2 cache; E-cores share L2. Hyperthreads share execution units. For low-latency: pin to a physical P-core, one HT only (use odd or even HT IDs consistently). |

---

### Failure Modes & Diagnosis

| Failure | Symptom | Diagnosis | Fix |
|---------|---------|-----------|-----|
| Over-pinning | CPUs saturated; others idle | `top -1`: pinned CPUs 100%, others 0% | Pin to enough CPUs; use NUMA binding not strict affinity |
| NUMA mismatch | Persistent high latency | `numastat -p PID`: other_node > 20% | `numactl --cpunodebind=N --membind=N` |
| Missing IRQ affinity | CPU 0 saturated with NIC interrupts | `top`: CPU 0 hi% >> others | Spread NIC IRQs across CPUs |
| Hyperthreading interference | Inconsistent latency on pinned core | Monitor sibling HT usage | Pin to HT pair or isolate both siblings |

---

### Quick Reference Card

| Goal | Command |
|------|---------|
| Pin process to CPUs 0-3 | `taskset -c 0-3 <command>` |
| Pin to NUMA node 0 | `numactl --cpunodebind=0 --membind=0 <cmd>` |
| View process CPU affinity | `taskset -pc $PID` |
| Isolate CPUs at boot | `isolcpus=4-7` in kernel cmdline |
| JVM NUMA-aware | `-XX:+UseNUMA` |
| Check NUMA balance | `numastat -p <PID>` |
| Spread NIC IRQs | `echo N > /proc/irq/NNN/smp_affinity` |
| Check CPU topology | `lscpu` or `numactl --hardware` |
