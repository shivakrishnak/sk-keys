---
id: OSY-066
title: Real-Time Scheduling SCHED_FIFO and SCHED_RR
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-009, OSY-065
used_by: []
related: OSY-065, OSY-064, OSY-120
tags:
  - real-time
  - SCHED_FIFO
  - SCHED_RR
  - SCHED_DEADLINE
  - latency
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 66
permalink: /technical-mastery/osy/real-time-scheduling/
---

## TL;DR

SCHED_FIFO and SCHED_RR are POSIX real-time schedulers
with priorities 1-99 (above all CFS threads). SCHED_FIFO
runs until it blocks or yields; SCHED_RR has a timeslice.
Real-time threads can monopolize CPUs and starve all CFS
tasks. Use for: audio processing, network packet I/O,
low-latency trading. Requires `CAP_SYS_NICE` capability.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-066 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | SCHED_FIFO, SCHED_RR, SCHED_DEADLINE, real-time, CAP_SYS_NICE |
| **Prerequisites** | OSY-009, OSY-065 |

---

### Real-Time Scheduling Classes

```
Linux scheduling classes (highest to lowest priority):
  
  1. SCHED_DEADLINE  (highest among real-time)
     Earliest Deadline First (EDF)
     Parameters: runtime, deadline, period
     "This task needs X microseconds every Y period"
     Kernel enforces: if guaranteed, always meets deadline
     
  2. SCHED_FIFO      (real-time, priority 1-99)
     No timeslice within same priority
     Runs until: voluntarily yields, blocks on I/O, or higher-priority preempts
     Priority 99 can STARVE ALL other tasks indefinitely!
     Use: audio processing, network I/O (low latency bursts)
     
  3. SCHED_RR        (real-time, priority 1-99)
     Like SCHED_FIFO but with timeslice (default 100ms / RT_SCHED_RR_TIMESLICE)
     Multiple tasks at same RT priority: time-share in round-robin
     Still preempts all CFS tasks
     
  4. SCHED_OTHER (CFS) (normal tasks)
  5. SCHED_BATCH
  6. SCHED_IDLE     (lowest)
     
Priority numbering:
  SCHED_FIFO/RR: 1 (lowest RT) to 99 (highest RT)
  HIGHER number = HIGHER priority (opposite of nice values!)
  
Setting real-time priority:
  chrt -f 50 java -jar app.jar    # SCHED_FIFO, priority 50
  chrt -r 50 java -jar app.jar    # SCHED_RR, priority 50
  Requires: root or CAP_SYS_NICE capability
```

---

### RT Throttling: Safety Net

```
Problem: runaway RT task can lock up the entire system
  (SCHED_FIFO busy-loop at priority 99 = no other task runs)

Linux RT throttling (SAFETY NET):
  /proc/sys/kernel/sched_rt_runtime_us   (default: 950000 = 950ms)
  /proc/sys/kernel/sched_rt_period_us    (default: 1000000 = 1s)
  
  Meaning: RT tasks can use at most 950ms per 1000ms period
  Remaining 50ms: reserved for CFS tasks (SSH login, recovery)
  
  This prevents RT tasks from completely locking up the system
  
  For dedicated RT system (all CPUs for RT):
    echo -1 > /proc/sys/kernel/sched_rt_runtime_us
    (disable throttling - dangerous, only for truly dedicated RT CPUs)
    
  In containers: RT scheduling requires privileged mode
  In Kubernetes: RT threads in containers require:
    securityContext:
      privileged: true
    Or: set CAP_SYS_NICE
```

---

### Real-Time in Java

```java
// Java thread at real-time priority:
// Requires JNI or ProcessBuilder to set Linux RT scheduling

// Method 1: Launch JVM with chrt (simplest):
// $ chrt -f 50 java -jar app.jar
// All threads inherit SCHED_FIFO until changed

// Method 2: Per-thread via JNI (for specific threads):
// sched_setscheduler() via JNI
// (see LMAX Disruptor's SettableThreadFactory)

// Method 3: ProcessBuilder with rt priority:
public static void setRealTimePriority(int priority, String policy) 
        throws IOException, InterruptedException {
    long pid = ProcessHandle.current().pid();
    // "f" = SCHED_FIFO, "r" = SCHED_RR
    ProcessBuilder pb = new ProcessBuilder(
        "chrt", "--set", "--" + policy, 
        String.valueOf(priority), String.valueOf(pid));
    pb.inheritIO();
    Process p = pb.start();
    if (p.waitFor() != 0) {
        throw new IOException(
            "Failed to set RT priority (need CAP_SYS_NICE)");
    }
}

// Use cases for RT in Java:
//   Audio synthesis (JACK, PortAudio via JNI)
//   Low-latency trading (market data processing thread)
//   Network packet capture (DPDK via JNI)
//   Robotics control loops
```

---

### SCHED_DEADLINE: EDF Scheduling

```
SCHED_DEADLINE: most advanced Linux RT policy
  "Every period P, I need exactly R microseconds of CPU"
  Kernel guarantees this if admission control passes
  
  Parameters:
    runtime  (R): CPU time needed per period
    deadline (D): must complete within D after start of period
    period   (P): how often this budget repeats
    
  Example: audio thread needing 2ms every 10ms:
    runtime  = 2000000 ns  (2ms)
    deadline = 5000000 ns  (5ms - finish before half of period)
    period   = 10000000 ns (10ms - 100Hz rate)
    
  Admission control:
    Kernel checks: sum of all (runtime/period) <= 1.0
    If sum > 1.0 (overcommitted): sched_setattr() fails
    This prevents deadline tasks from oversubscribing CPU
    
  EDF algorithm:
    Among multiple deadline tasks: run the one with earliest deadline
    Provably optimal for single-processor EDF scheduling
    (optimal = meets all deadlines if any scheduler can)
    
Java: SCHED_DEADLINE requires sched_setattr() syscall (JNI)
  Not commonly used in pure Java; used in native RT frameworks
  sched_setattr() for main JVM thread: affects all Java threads
    -> Be careful: main JVM thread affected means GC threads too!
```

---

### Practical: Low-Latency Java Configuration

```bash
# For low-latency Java (not full real-time):
# 1. Use high scheduling priority (nice, not RT)
renice -n -15 -p $(pgrep java)  # nice -15 (elevated, no root for -20)

# 2. Isolate CPUs for Java process:
isolcpus=2,3,4,5  # add to /proc/cmdline (reboot required)
# Isolated CPUs: no other tasks scheduled there (no CFS competition)
taskset -c 2-5 java -jar app.jar

# 3. Pin IRQ affinity away from Java CPUs:
# All network/disk interrupts go to CPU 0,1
# Java runs on 2-5 without interrupt interference
for irq in $(ls /proc/irq/); do
  echo 3 > /proc/irq/$irq/smp_affinity 2>/dev/null  # CPUs 0 and 1
done

# 4. Disable energy saving (turbo boost inconsistency):
echo performance > /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# 5. Reduce JVM GC pause impact:
# -XX:+UseZGC or -XX:+UseShenandoahGC (sub-1ms pauses)
# -XX:MaxGCPauseMillis=5

# Result: Java service with p99 latency < 1ms (without full RT)
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "SCHED_FIFO priority 99 is the highest possible in Linux" | Priority 99 is the highest within SCHED_FIFO/RR. SCHED_DEADLINE tasks use a separate mechanism and are always selected before even SCHED_FIFO tasks when they need to run. Kernel threads also run at effective priorities above RT user-space tasks when necessary |
| "Using RT scheduling in a JVM is straightforward" | Setting RT scheduling on the JVM process affects ALL JVM threads, including GC threads. GC threads at SCHED_FIFO can starve every other process. The correct approach: set RT on specific native threads via JNI, or use dedicated RT-capable frameworks like LMAX Disruptor with RT thread factories |

---

### Quick Reference Card

| Concept | Key Fact |
|---------|---------|
| SCHED_FIFO priority | 1-99; higher number = higher priority (opposite of nice) |
| SCHED_FIFO runs until | Blocks, yields, or higher RT priority preempts |
| RT throttle | Default: RT tasks get 950ms/1s; 50ms reserved for CFS |
| SCHED_DEADLINE | EDF; specify runtime+deadline+period; admission control |
| Enable RT | `chrt -f 50 PID` or `chrt -f 50 java ...`; needs CAP_SYS_NICE |
| RT in container | Requires `privileged: true` or `CAP_SYS_NICE` |
