---
id: LNX-089
title: "Linux Real-Time (PREEMPT_RT, latency, deadline scheduling)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★★
depends_on: LNX-046, LNX-047
used_by: LNX-093
related: LNX-046, LNX-047, LNX-086, LNX-091
tags: [preempt-rt, real-time-linux, cyclictest, sched-fifo, sched-deadline, cpu-isolation, isolcpus, nohz-full, irq-affinity, latency, jitter, rtla, tuned-realtime, tuna, latency-sources, deterministic]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 89
permalink: /technical-mastery/lnx/linux-real-time-preempt-rt/
---

## TL;DR

Real-time Linux achieves deterministic, low-latency task execution.
**PREEMPT_RT** (now mainline since kernel 5.15) makes all kernel code
preemptible (spinlocks become sleeping locks, IRQ handlers run in threaded
context). Latency sources: interrupt handling (set IRQ affinity away from
RT CPUs), kernel code non-preemption, memory allocation (use `mlockall`),
scheduler jitter. Measure latency: `cyclictest -m -S -p 99 -i 1000` (measures
max wake-up latency in microseconds). Real-time scheduling policies:
`SCHED_FIFO` (run until done or preempted by higher priority), `SCHED_RR`
(round-robin with time quantum), `SCHED_DEADLINE` (CBS - Constant Bandwidth
Server: specify deadline/period/runtime). CPU isolation: `isolcpus=2-7
nohz_full=2-7 rcu_nocbs=2-7` in kernel cmdline. Tool: `tuned-adm profile
realtime` applies all best-practice RT settings.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-089 |
| **Difficulty** | ★★★ Advanced |
| **Category** | Linux |
| **Tags** | PREEMPT_RT, real-time Linux, cyclictest, SCHED_FIFO, SCHED_DEADLINE, CPU isolation, isolcpus, latency measurement, IRQ affinity |
| **Prerequisites** | LNX-046 (Linux scheduler), LNX-047 (Process management) |

---

### The Problem This Solves

**Problem 1**: An industrial robot controller needs to respond to a sensor
input within 1ms, every 1ms, forever. With a standard Linux kernel: the
system call that reads the sensor might normally return in 100 microseconds,
but occasionally (every few minutes): a kernel lock, a network interrupt, or
a memory allocator path takes 10ms. The robot jerks. With PREEMPT_RT + CPU
isolation + cyclictest validation: worst-case latency measured at 47 microseconds
over 24 hours of testing - well within the 1ms requirement.

**Problem 2**: An audio production workstation (JACK audio server) produces
audio glitches ("xruns") every few minutes. The audio thread needs to process
and output audio within 5ms of its scheduled time. Standard kernel: periodic
softirq processing blocks the audio thread for 8ms. With PREEMPT_RT kernel +
`SCHED_FIFO` priority + `mlockall`: xruns eliminated.

---

### Textbook Definition

**Real-time Linux**: A set of kernel configurations and patches that ensure
bounded worst-case latency for high-priority tasks. "Real-time" does NOT mean
"fast" - it means DETERMINISTIC: the system guarantees a maximum response time.

**PREEMPT_RT**: A kernel configuration (originally a patchset, mainline since
Linux 5.15 LTS) that makes the Linux kernel fully preemptible. Changes:
- Spinlocks replaced with sleeping (rt_mutex-based) locks -> lower-priority tasks can sleep while holding locks, allowing preemption
- Interrupt handlers converted to threaded IRQ handlers -> interrupt processing runs as kernel threads, schedulable by RT scheduler
- `BH` (bottom halves) and softirqs made fully preemptible
- Timer interrupt (jiffies) replaced with high-resolution timers

**Real-time scheduling policies (from Linux scheduler):**
| Policy | Behavior | Priority |
|--------|---------|---------|
| `SCHED_NORMAL` | CFS (Completely Fair Scheduler) | nice values |
| `SCHED_FIFO` | Run until done or preempted by higher RT priority | 1-99 (static) |
| `SCHED_RR` | SCHED_FIFO but with round-robin time quantum | 1-99 (static) |
| `SCHED_DEADLINE` | EDF (Earliest Deadline First): specify period, deadline, runtime | - |

**Latency sources (to be eliminated for RT):**
1. Interrupt latency: IRQ fires, CPU handles it before RT task
2. Scheduler latency: RT task becomes runnable, delayed by scheduler overhead
3. Lock contention: RT task waits for non-RT task holding a kernel lock
4. Memory allocation: `kmalloc` may sleep (use `mlockall` to pre-allocate)
5. CPU power management: C-state wakeup latency (deep C-states add 100-1000us)
6. TLB shootdowns: multi-processor TLB flushes stop all CPUs briefly

---

### Understand It in 30 Seconds

```bash
# === Measure system latency with cyclictest ===

# Install cyclictest (part of rt-tests):
dnf install rt-tests    # RHEL/CentOS/Fedora
apt install rt-tests    # Debian/Ubuntu

# Run cyclictest: measure worst-case wake-up latency
# -m: lock all memory (mlockall), -S: SMP mode, -p 99: RT priority 99
# -i 1000: interval 1000us (1ms), run for 60 seconds
cyclictest -m -S -p 99 -i 1000 -t 4 -D 60
# T: 0 (  0: 234)    Avg:    5 Max:     47
# T: 1 (  1: 234)    Avg:    4 Max:     52
# T: 2 (  2: 234)    Avg:    4 Max:     38
# T: 3 (  3: 234)    Avg:    5 Max:     44
# Max: 52 microseconds -> good RT performance

# Without RT kernel: Max might be 5000-50000 microseconds!
# For robotics/industrial: typically need Max < 100us

# Run with load (stress test):
# Terminal 1: apply load
stress --cpu 4 --io 4 --vm 2 --timeout 60 &
# Terminal 2: run cyclictest
cyclictest -m -S -p 99 -i 1000 -t 4 -D 60
# Check if Max latency increases under load

# === Check if PREEMPT_RT is active ===
uname -a
# Linux hostname 6.1.55-rt15 #1 SMP PREEMPT_RT ...
#                             ^^^  PREEMPT_RT in uname!

cat /proc/version
# Linux version 6.1.55-rt15 (gcc ...) PREEMPT_RT

# Check kernel config:
grep -E "PREEMPT_RT|CONFIG_PREEMPT" /boot/config-$(uname -r) | \
    grep -v "^#"
# CONFIG_PREEMPT_RT=y   <- Full PREEMPT_RT enabled

# === Set real-time scheduling for a process ===

# Run a program with SCHED_FIFO priority 99:
chrt -f 99 my_realtime_app

# Change a running process to RT scheduling:
chrt -f -p 99 $(pidof my_realtime_app)

# View scheduling policy for a process:
chrt -p $(pidof my_realtime_app)
# pid 1234's current scheduling policy: SCHED_FIFO
# pid 1234's current scheduling priority: 99

# === CPU isolation for real-time ===
# Add to kernel command line (/etc/default/grub):
# isolcpus=2-7 nohz_full=2-7 rcu_nocbs=2-7

# isolcpus: prevents scheduler from assigning normal tasks to CPUs 2-7
# nohz_full: disables timer ticks on isolated CPUs (no tick jitter)
# rcu_nocbs: offloads RCU callbacks from isolated CPUs

# After reboot with isolcpus:
# Check what's running on isolated CPUs:
ps -eo pid,psr,comm | awk '$2 >= 2 && $2 <= 7'
# Only shows processes explicitly pinned to those CPUs

# Pin an RT process to isolated CPU 2:
taskset -c 2 chrt -f 99 my_realtime_app

# === IRQ affinity - keep interrupts off RT CPUs ===

# List all IRQs with their CPU affinity:
for i in /proc/irq/*/smp_affinity_list; do
    irq=$(echo $i | grep -oP '\d+')
    echo "IRQ $irq: CPUs $(cat $i)"
done | head -20
# IRQ 0: CPUs 0-7   <- timer interrupt (all CPUs)
# IRQ 24: CPUs 0-7  <- NIC (eth0) interrupts on all CPUs

# Move NIC IRQ to CPU 0 only (keep CPUs 2-7 free for RT):
echo 0 > /proc/irq/24/smp_affinity_list   # CPU 0 only

# Enable IRQ affinity for all non-RT IRQs to CPU 0-1:
for irq_dir in /proc/irq/*/; do
    irq_num=$(basename $irq_dir)
    [ "$irq_num" = "0" ] && continue  # skip timer
    echo 0-1 > $irq_dir/smp_affinity_list 2>/dev/null
done

# === mlockall - prevent memory from being swapped ===
# In the RT application:
#include <sys/mman.h>
# mlockall(MCL_CURRENT | MCL_FUTURE);
# MCL_CURRENT: lock all current pages
# MCL_FUTURE: lock all future allocations

# Or in Python:
import ctypes
MCL_CURRENT = 1; MCL_FUTURE = 2
ctypes.CDLL("libc.so.6").mlockall(MCL_CURRENT | MCL_FUTURE)

# === tuned-adm for automatic RT tuning ===
# Apply best-practice RT settings automatically:
dnf install tuned    # if not installed
systemctl start tuned
tuned-adm profile realtime
# Applies: CPU governor performance, disabled idle states,
# IRQ affinity, disk scheduler tuning, sysctl tuning

# Verify active profile:
tuned-adm active
# Current active profile: realtime

# === SCHED_DEADLINE example ===
# A task that runs for 5ms every 10ms with 8ms deadline:
# Using sched_setattr(2) syscall or deadline_sched utility:
deadline_sched --period 10000000 --deadline 8000000 \
               --runtime 5000000 my_rt_program
# period=10ms, deadline=8ms, runtime=5ms

# Check:
chrt -p $(pidof my_rt_program)
# pid XXXX's current scheduling policy: SCHED_DEADLINE
# pid XXXX's current scheduling priority: 0  (EDF, not static)
```

---

### First Principles

**What PREEMPT_RT changes and why:**
```
Standard Linux kernel (PREEMPT default):
  Some kernel code sections are non-preemptible:
  - Spinlock-protected regions
  - Interrupt handlers (hardware and software IRQs)
  - Bottom halves (tasklets, softirqs)
  
  Spinlock on standard kernel:
    spin_lock(&some_lock):
      disable preemption (no task switch!)
      disable interrupts (no interrupt can preempt!)
      spin (busy-wait) if lock held
    critical section...
    spin_unlock(&some_lock):
      re-enable preemption + interrupts
    
    Problem: if RT task (high priority) needs to run,
    but kernel is in a spin_lock section for a LOW priority task:
    RT task CANNOT run until spin_lock is released!
    Priority inversion! (real-time task blocked by low-priority one)

PREEMPT_RT kernel:
  Spinlocks become rt_mutex (sleeping mutexes):
    rt_mutex_lock(&some_lock):
      If lock held by LOW priority task:
        boost that task's priority to CURRENT RT priority
        (priority inheritance - prevents inversion)
        sleep (schedule out, allow RT task to run!)
      If lock not held: acquire immediately
    critical section...
    rt_mutex_unlock(&some_lock):
      restore previous priority of holder
  
  Interrupt handlers become threaded:
    Hardware interrupt fires:
      Short ISR: acknowledge hardware, wake up IRQ thread
      IRQ thread: RT-schedulable kernel thread
      Normal RT task at priority 99 can preempt IRQ thread at priority 50
    
    Before PREEMPT_RT: IRQ handler ran before ANY task, including RT
    After PREEMPT_RT: IRQ thread is schedulable -> RT priority controls order
  
  Result:
    RT task at priority 99: always preempts anything at lower priority
    Including IRQ threads, softirq threads, kernel workers
    PREEMPT_RT trades throughput for determinism

Latency sources in detail:
  1. C-state wakeup latency:
     Modern CPUs: power-saving idle states
     C0: active, C1: halt (< 1us wakeup), C2: deeper (1-10us),
     C6: package sleep (100-1000us wakeup!)
     
     A CPU in C6 receiving an interrupt: 500us to wake up
     That's 500us added to RT response time!
     
     Fix: disable deep C-states
       Kernel cmdline: intel_idle.max_cstate=1 (C1 max)
       Or: tuned-adm profile realtime (does this automatically)
  
  2. TLB shootdowns:
     When kernel modifies page tables (mmap, munmap, exec):
     Must invalidate TLB on all CPUs (IPI: inter-processor interrupt)
     All CPUs pause to process IPI -> RT task paused
     
     Fix: CPU isolation (isolcpus) prevents TLB shootdowns
     on isolated CPUs (no new processes -> no new page tables)
  
  3. RCU (Read-Copy-Update) callbacks:
     Kernel's lock-free synchronization: defers work to "quiescent state"
     Periodic RCU callbacks: run on every CPU, preempt RT tasks
     
     Fix: rcu_nocbs (offload RCU callbacks to dedicated kthread,
     not on isolated CPUs)
  
  4. Timer ticks (jiffies):
     Default: tick fires every 1ms (HZ=1000) or 4ms (HZ=250)
     Even with PREEMPT_RT: tick processing adds ~10-50us jitter
     
     Fix: nohz_full (adaptive tick, tick disabled when only 1 runnable task)
     On isolated CPU running RT task: tick suppressed
     Residual tick: only forced at ~1/second (Linux still needs some)
  
  5. Memory allocation at runtime:
     malloc/new -> brk/mmap -> page fault -> kernel page allocation
     kmalloc may take 10-100us on contention
     
     Fix: pre-fault all memory before real-time period begins
     mlockall(MCL_CURRENT | MCL_FUTURE) = lock all pages in RAM
     Pre-allocate all needed memory before entering RT loop
     No page faults during RT execution
```

---

### Thought Experiment

Setting up a real-time control loop for an industrial motor controller:

```bash
# Requirements: respond to encoder event within 500us, every 1ms

# Step 1: Check current latency (before optimization):
cyclictest -m -S -p 99 -i 1000 -t 1 -D 30 2>&1 | tail -5
# T: 0 (  0:  0)   Avg:   45 Max:  4532
# Max 4532us on standard kernel! 4.5ms >> 500us requirement

# Step 2: Install PREEMPT_RT kernel:
# RHEL: enable RT subscription and install
dnf install kernel-rt kernel-rt-devel
# Ubuntu: 
apt install linux-image-rt-amd64
# Reboot to RT kernel
reboot

# Step 3: Verify RT kernel:
uname -r
# 5.14.21-150500.13.73.1.rt7  <- RT kernel active

# Step 4: Apply CPU isolation:
# Edit /etc/default/grub:
# GRUB_CMDLINE_LINUX="... isolcpus=2,3 nohz_full=2,3 rcu_nocbs=2,3"
grub2-mkconfig -o /boot/grub2/grub.cfg   # RHEL
# or: update-grub                          # Ubuntu
reboot

# Step 5: Apply RT tuning profile:
tuned-adm profile realtime

# Step 6: Move IRQs to CPU 0-1:
# Check current IRQ placement:
cat /proc/interrupts | head -20
# Move all to CPU 0:
for irq in $(cat /proc/interrupts | awk '{print $1}' | tr -d ':'); do
    echo 1 > /proc/irq/$irq/smp_affinity 2>/dev/null  # CPU 0 = 0x1
done

# Step 7: Test latency under load:
# Run system load:
stress --cpu 2 --io 2 &

# Test on isolated CPU 2:
taskset -c 2 cyclictest -m -S -p 99 -i 1000 -t 1 -D 300
# T: 0 (  2: 0)    Avg:    4 Max:     42
# Max 42us! Well within 500us requirement

# Step 8: Write RT application:
cat > motor_controller.c << 'EOF'
#include <stdio.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <pthread.h>
#include <time.h>
#include <errno.h>

#define NSEC_PER_SEC 1000000000L
#define INTERVAL_US  1000          // 1ms interval
#define PRIORITY     99

void *rt_thread(void *arg) {
    struct timespec ts;
    struct timespec next;
    
    // Get current time:
    clock_gettime(CLOCK_MONOTONIC, &next);
    
    while (1) {
        // Calculate next wake time (absolute):
        next.tv_nsec += INTERVAL_US * 1000;  // add 1ms
        if (next.tv_nsec >= NSEC_PER_SEC) {
            next.tv_nsec -= NSEC_PER_SEC;
            next.tv_sec++;
        }
        
        // Sleep until next period:
        // Use CLOCK_MONOTONIC with absolute time for precise timing
        clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &next, NULL);
        
        // Real-time control logic here (< 500us required):
        read_encoder();
        calculate_pid();
        set_motor_output();
    }
    return NULL;
}

int main() {
    struct sched_param sp = { .sched_priority = PRIORITY };
    pthread_t thread;
    pthread_attr_t attr;
    
    // Lock all memory (prevent page faults during RT execution):
    if (mlockall(MCL_CURRENT | MCL_FUTURE)) {
        perror("mlockall"); return 1;
    }
    
    // Pre-fault stack pages:
    char stack_waste[64*1024];
    memset(stack_waste, 0, sizeof(stack_waste));
    
    // Create RT thread:
    pthread_attr_init(&attr);
    pthread_attr_setschedpolicy(&attr, SCHED_FIFO);
    pthread_attr_setschedparam(&attr, &sp);
    pthread_attr_setinheritsched(&attr, PTHREAD_EXPLICIT_SCHED);
    pthread_create(&thread, &attr, rt_thread, NULL);
    
    pthread_join(thread, NULL);
    return 0;
}
EOF

# Compile and run on isolated CPU:
gcc -O2 -lrt -lpthread -o motor_controller motor_controller.c
taskset -c 2 ./motor_controller
```

---

### Mental Model / Analogy

```
Real-time Linux = emergency services in a city (preemption hierarchy)

Standard city (non-RT Linux):
  Police, fire, ambulance (RT tasks) share roads with cars
  Sometimes: stuck behind a traffic jam (spinlock held by normal task)
  Traffic jam cleared by normal driver at their pace (no priority)
  Emergency vehicle: BLOCKED! (priority inversion)
  
  Old Linux spinlock = traffic system that can't give way
  Emergency vehicle honks but cars can't move (spinlock in critical section)

PREEMPT_RT city (PREEMPT_RT kernel):
  All roads have emergency "pull-over" lanes
  Any car can pull over when emergency vehicle approaches (rt_mutex)
  Emergency vehicle passes within 10-50 microseconds (guaranteed)
  
  Even city infrastructure (interrupt handlers = utility trucks)
  now YIELDS to emergency vehicles (threaded IRQs, RT-schedulable)

CPU isolation = dedicated emergency corridor:
  CPUs 0-1: normal city traffic (IRQs, normal processes)
  CPUs 2-7: dedicated emergency routes (isolated CPUs)
  No normal traffic ever enters CPUs 2-7
  Emergency vehicles (RT tasks) have private highway
  
  isolcpus: lock the highway entrance (no normal tasks enter)
  nohz_full: no traffic lights (timer ticks) on the highway
  rcu_nocbs: no toll booths (RCU callbacks) on the highway

C-states = traffic light wakeup time:
  C1 (shallow sleep): traffic light already yellow, turns green in 1us
  C6 (deep sleep): traffic light is off, needs to power on = 500us!
  
  Emergency call comes in: officer sleeping at station (CPU in C6)
  Wakeup: turn on lights, get dressed, drive out = 500us
  Too slow for 500us requirement!
  
  Fix: keep officer in C1 (dozing at desk, ready to run immediately)
  intel_idle.max_cstate=1: no deep sleep states

mlockall = emergency kit always in pocket:
  Without mlockall: equipment (pages) stored in warehouse (swap)
  When needed: retrieve from warehouse (page fault) = 1-100ms delay
  
  With mlockall: all equipment on person at all times
  Instant access, no retrieval time
  Pre-fault: "check your pockets before going on duty" (touch all pages)

cyclictest = timing exercise:
  Set alarm for every 1ms, measure actual wakeup time
  "Alarm went off at T+0, actually woke up at T+47us: latency=47us"
  Run for 24 hours: max latency over ALL measurement = worst case
  "In 24 hours, worst latency was 52us" = system reliable for 500us deadline
```

---

### Gradual Depth - Five Levels

**Level 1:**
Concept of real-time vs regular OS. "Real-time" = deterministic (bounded latency),
NOT fast. Hard vs soft real-time. `cyclictest` to measure latency.
`SCHED_FIFO` priority concept. `chrt` to set scheduling policy.

**Level 2:**
PREEMPT_RT kernel and how it differs from standard. Scheduling policies:
SCHED_FIFO, SCHED_RR, SCHED_DEADLINE. `mlockall` to prevent page faults.
CPU isolation basics (`isolcpus`). IRQ affinity. `tuned-adm profile realtime`.
`taskset` to pin processes to CPUs. Latency sources overview.

**Level 3:**
Priority inversion problem and priority inheritance (rt_mutex). Threaded IRQ
handlers (PREEMPT_RT change). C-state wakeup latency (`intel_idle.max_cstate`).
Timer tick jitter and `nohz_full`. RCU (Read-Copy-Update) and `rcu_nocbs`.
TLB shootdowns and isolation. `SCHED_DEADLINE` parameters (runtime/period/
deadline). `cyclictest` histogram and interpretation. `rtla` tool (Real-Time
Linux Analysis).

**Level 4:**
Priority inheritance chain analysis. `pi_futex` (process-shared priority
inheritance). Real-time kernel patch history (Ingo Molnar, Thomas Gleixner,
now mainline). OSADL (Open Source Automation Development Lab) RT testing.
Memory management for RT: huge pages eliminate TLB misses, `madvise(MADV_HUGEPAGE)`.
`membarrier()` syscall for efficient cross-CPU memory visibility. Numa-aware
memory allocation in RT contexts. `clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME)`:
why absolute timing is better than relative sleep for periodic tasks.

**Level 5:**
Xenomai (RT framework on top of Linux with dual kernel). EVL (Embedded
Versatile Library): single kernel RT approach. RTAI (Real-Time Application
Interface): another dual-kernel approach. `Linux+Xenomai` vs `PREEMPT_RT`:
Xenomai achieves sub-10us latency (hardware interrupt co-processor), PREEMPT_RT
achieves 10-100us. Industries: hard real-time (< 100us: robotics, CNC, audio
cards); soft real-time (< 1ms: audio applications, industrial HMI). Kernel
latency tracing: `cyclictest --latency` creates histogram. `ftrace` with `hwlat`
tracer: measures hardware-induced latency. SMI (System Management Interrupt):
firmware-level interrupts that bypass the OS entirely, can add ms of latency.
Detection: `hwlat_detector` kernel module.

---

### Code Example

**BAD - RT application without proper setup:**
```c
// BAD: RT thread without memory locking or pre-faulting
void bad_rt_thread() {
    // BAD 1: No mlockall -> page faults during RT period
    // When accessing a page for the first time: page fault
    // Kernel allocates page: might take 10-100ms!
    
    // BAD 2: malloc() inside RT loop
    while (running) {
        // malloc allocates new pages lazily:
        char *buf = malloc(4096);  // may trigger page fault!
        
        // BAD 3: printf() -> write() syscall with locks
        printf("processing...\n");  // stdio locks -> non-RT
        
        // BAD 4: relative sleep
        usleep(1000);  // sleep 1ms, but wakeup is imprecise
        // Actual wakeup: 1000us + scheduler latency + OS overhead
        // May be 1ms, may be 5ms - unpredictable!
        
        free(buf);
    }
}

// GOOD: proper RT thread
void good_rt_thread() {
    struct timespec next;
    char fixed_buf[4096];  // stack allocation, pre-faulted with mlockall
    
    // Pre-touch all needed data before RT loop:
    memset(fixed_buf, 0, sizeof(fixed_buf));
    
    clock_gettime(CLOCK_MONOTONIC, &next);
    
    while (running) {
        // GOOD: absolute sleep for precise periodic timing
        next.tv_nsec += 1000000;  // +1ms
        if (next.tv_nsec >= 1000000000L) {
            next.tv_nsec -= 1000000000L;
            next.tv_sec++;
        }
        clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &next, NULL);
        
        // GOOD: pre-allocated buffers, no malloc
        process_data(fixed_buf, sizeof(fixed_buf));
        // No printf: log to pre-allocated ring buffer for later
    }
}

int main() {
    // GOOD: mlockall before creating RT thread
    mlockall(MCL_CURRENT | MCL_FUTURE);
    
    // Pre-fault all stack pages (typically 8MB):
    char prefault_stack[8 * 1024 * 1024];
    memset(prefault_stack, 0, sizeof(prefault_stack));
    
    // Set RT scheduling BEFORE starting work:
    struct sched_param sp = { .sched_priority = 90 };
    sched_setscheduler(0, SCHED_FIFO, &sp);
    
    good_rt_thread();
    return 0;
}
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "Real-time Linux means the system responds faster on average" | Real-time means DETERMINISTIC (bounded worst-case latency), not faster average performance. A standard Linux kernel might respond in 50 microseconds on average to an RT task, but occasionally spikes to 50 milliseconds (0.1% of the time). A PREEMPT_RT kernel might respond in 60 microseconds on average, but NEVER spikes above 200 microseconds. The AVERAGE is higher, but the WORST CASE is bounded. For systems where average latency matters (web servers, databases): standard Linux is often better. For systems where worst-case latency matters (industrial control, audio): PREEMPT_RT is required. Many engineers confuse "fast" with "real-time" - they are orthogonal concepts. |
| "isolcpus guarantees zero OS overhead on isolated CPUs" | CPU isolation (`isolcpus`) removes isolated CPUs from the general scheduler's runqueue - normal tasks won't be placed there. However, some OS overhead remains: (1) Timer interrupts still fire periodically (use `nohz_full` to suppress most ticks, but not all - one tick per second may still occur). (2) RCU callbacks may still run (use `rcu_nocbs` to offload). (3) SMI (System Management Interrupts) from firmware: completely bypass the OS and can take 1-100ms - only detectable with `hwlat_detector`. (4) TLB shootdowns from non-isolated CPUs can still interrupt isolated ones in some scenarios. The combination `isolcpus=N nohz_full=N rcu_nocbs=N` gives the best isolation, but perfection requires also: disabling SMI (BIOS setting), using NUMA-local memory, and careful driver configuration. |
| "SCHED_FIFO priority 99 means the task runs first, always" | SCHED_FIFO priority 99 means: (1) Preempts any task with lower RT priority or any SCHED_NORMAL task. (2) NEVER preempts another SCHED_FIFO task with priority 99 (equal priority = cooperative). (3) On non-PREEMPT_RT kernels: kernel code in non-preemptible sections (spinlocks, IRQ handlers) STILL runs before the SCHED_FIFO task. On PREEMPT_RT: threaded IRQ handlers can be preempted by SCHED_FIFO 99. (4) Hardware interrupts (NMI, SMI) still bypass all scheduling. (5) A runaway SCHED_FIFO 99 task that never sleeps will starve ALL other tasks on that CPU - including other RT tasks at lower priority. Safeguard: `kernel.sched_rt_runtime_us = -1` disables the RT throttle (which limits RT tasks to 95% of CPU time by default). For safety: leave RT throttle enabled in development. |
| "cyclictest passing means the application will meet its deadline" | cyclictest measures the kernel scheduler's wake-up latency for a simple periodic thread. An application's deadline depends on BOTH scheduler latency AND the application's execution time. If `cyclictest` max = 50us and your application COMPUTATION takes 950us: you have 1000us (1ms) total budget with zero margin. Real applications: the critical path includes reading hardware registers, computation, and writing outputs. Additionally: cyclictest uses `clock_nanosleep` - other sleep primitives (poll, select, pthread_cond_timedwait) may have different characteristics. Test your ACTUAL application with instrumentation (`clock_gettime` before/after deadline-critical section) in addition to cyclictest. cyclictest is necessary but not sufficient for real-time validation. |

---

### Failure Modes & Diagnosis

**RT latency diagnosis:**
```bash
# === Failure: cyclictest shows high max latency ===
cyclictest -m -S -p 99 -i 1000 -t 1 -D 60
# T: 0 (  0:  0)   Avg:    5 Max:   4532
# 4.5ms max! Way too high for < 500us requirement

# Diagnosis 1: Check if PREEMPT_RT kernel:
uname -a | grep -i rt
# If no "rt" in uname: not running RT kernel!
# Fix: install and boot RT kernel

# Diagnosis 2: Check C-states:
# High latency often due to CPU deep sleep states
cat /sys/devices/system/cpu/cpu0/cpuidle/state*/disable
# 0   <- not disabled -> C-states active!

# Disable C-states:
for state in /sys/devices/system/cpu/cpu*/cpuidle/state[2-9]/disable; do
    echo 1 > $state
done
# Or: cpupower idle-set --disable-by-latency 10  # disable states > 10us

# Diagnosis 3: Check if RT profile applied:
tuned-adm active
# Current active profile: throughput-performance  <- wrong!
tuned-adm profile realtime

# Diagnosis 4: Check IRQ distribution:
# If NIC IRQs on same CPU as RT task -> interrupt latency!
cat /proc/interrupts | grep eth0
# 24:    45234      0      0      0   eth0  <- all on CPU 0
# If RT task on CPU 0: those NIC IRQs preempt it!
echo 0 > /proc/irq/24/smp_affinity_list   # move to CPU 0 only

# Diagnosis 5: Check for SMI (System Management Interrupts):
# SMIs are BIOS-level interrupts that bypass the OS completely
dmesg | grep -i smi
# If not visible: use hwlat_detector
modprobe hwlat_detector
echo 1 > /sys/kernel/debug/hwlat_detector/enable
cat /sys/kernel/debug/hwlat_detector/max
# 1234  <- 1.2ms hardware-level latency!
# This is BIOS SMI - cannot be fixed in OS
# Solution: BIOS settings to disable SMI (vendor-specific)

# Diagnosis 6: Check if nohz_full active:
cat /sys/devices/system/cpu/cpu2/nohz_full
# bash: No such file or directory
# OR: check boot cmdline:
grep nohz_full /proc/cmdline
# If not present: timer ticks causing jitter
# Fix: add nohz_full=2-7 to kernel cmdline, reboot

# Diagnosis 7: Memory not locked (page faults):
# Use perf to count page faults during RT period:
perf stat -e minor-faults,major-faults \
    cyclictest -m -S -p 99 -i 1000 -t 1 -D 10
# If major-faults > 0: pages being swapped in during RT
# Fix: ensure mlockall() in RT app + sufficient RAM
```

---

### Related Keywords

**Foundational:**
LNX-046 (Linux scheduler), LNX-047 (Process management)

**Builds on this:**
LNX-093 (Performance troubleshooting)

**Related:**
LNX-086 (Kernel parameters), LNX-091 (Traffic control - also uses scheduling)

---

### Quick Reference Card

| Command | Purpose |
|---------|---------|
| `cyclictest -m -S -p 99 -i 1000 -t 4 -D 60` | Measure RT latency (60s, 4 threads) |
| `chrt -f 99 ./app` | Run app with SCHED_FIFO priority 99 |
| `tuned-adm profile realtime` | Apply RT tuning (C-states, IRQ, sysctl) |
| `taskset -c 2 ./app` | Pin process to CPU 2 |
| `echo 1 > /proc/irq/24/smp_affinity_list` | Move IRQ 24 to CPU 1 |
| `mlockall(MCL_CURRENT \| MCL_FUTURE)` | Lock all pages in RAM |
| `uname -a \| grep rt` | Verify RT kernel |

**3 things to remember:**
1. Real-time = DETERMINISTIC (bounded worst-case latency), NOT fast average - a 100us max matters more than a 5us average
2. Three pillars: (a) PREEMPT_RT kernel, (b) CPU isolation (`isolcpus` + `nohz_full` + `rcu_nocbs`), (c) `mlockall` to prevent page faults during RT execution
3. C-states are a hidden latency killer: CPU in C6 can take 500us to wake up - disable deep C-states for RT systems

---

### Transferable Wisdom

The real-time scheduling concept (guarantee worst-case, not optimize average)
applies to: SLAs in distributed systems (p99 latency matters more than average),
Kubernetes QoS classes (Guaranteed vs Burstable vs BestEffort - same guarantee
model), real-time databases (guaranteed query latency for trading systems),
Kafka consumer lag SLOs (maximum latency, not average). CPU isolation (dedicate
resources for predictable performance) maps to: Kubernetes CPU pinning with
`cpuManagerPolicy: static` (dedicated CPU cores for Guaranteed pods), database
connection pool isolation, NUMA-aware memory allocation. The PREEMPT_RT priority
inheritance mechanism (boost low-priority task that holds needed lock) is the
same as: database lock escalation, OS priority boosting for GUI applications,
real-time task promotion in Java concurrent queues. The mlockall pattern (pre-
allocate all resources before the real-time period) is a universal real-time
principle: pre-flight checks, connection pool warm-up, JVM class loading at
startup (not first request), lambda function cold start optimization. The
difference between soft real-time (best effort, < 1ms most of the time) and
hard real-time (guaranteed < 1ms, always) is the same as SLA vs SLO vs SLI:
different levels of commitment and consequence.

---

### The Surprising Truth

PREEMPT_RT spent 17 years as an external patch before being mainlined into
the Linux kernel in 2021 (kernel 5.15 LTS). During those 17 years: Linux
with PREEMPT_RT was powering medical devices (ventilators, surgical robots),
industrial controllers (CNC machines, automotive assembly), professional audio
equipment (recording studios), and financial trading systems - all running on
non-upstream, custom-patched kernels. The patch was maintained by Thomas
Gleixner, Ingo Molnar, and Sebastian Siewior for nearly two decades. The
reason for delay: mainlining required completely rearchitecting Linux's locking
primitives (converting spinlocks to sleeping mutexes) - a massive change with
broad impact. In 2015: the OSADL (Open Source Automation Development Lab)
ran a continuous cyclictest measurement for 8+ years on the same system,
accumulating the longest-running RT latency dataset in history. Their results
showed consistent sub-100us maximum latency. The second surprise: SMI (System
Management Interrupt) - firmware-level interrupts that completely bypass the
Linux kernel - remains the biggest real-time latency source that Linux cannot
control. On some server hardware with vendor firmware: SMI can introduce 10ms+
latency spikes. The only fixes are BIOS configuration changes (vendor-specific)
or running on hardware specifically validated for real-time (OSADL's hardware
qualification program). Even the perfect PREEMPT_RT setup fails if SMI
latency exceeds the deadline requirement.

---

### Mastery Checklist

- [ ] Can run cyclictest and interpret max latency results against real-time requirements
- [ ] Understands the difference between SCHED_FIFO, SCHED_RR, and SCHED_DEADLINE policies
- [ ] Knows the three main latency sources: C-states, IRQ affinity, and timer ticks
- [ ] Can apply CPU isolation (isolcpus, nohz_full, rcu_nocbs) and IRQ affinity configuration
- [ ] Understands why mlockall and memory pre-faulting are essential for RT applications

---

### Think About This

1. You're deploying a robotic assembly line controller that needs 500us worst-case
   response to encoder signals. The server has 8 CPU cores, 64GB RAM, Intel
   Xeon processor. Design the complete RT stack: which kernel, which kernel
   cmdline parameters, which CPUs for RT task vs system, what cyclictest command
   to validate, and what application code changes (scheduling policy, priority,
   mlockall). Calculate: with C6 disabled (max C1 latency: 5us), PREEMPT_RT
   overhead (typically 10-30us), what is your expected worst-case latency and
   safety margin?

2. An audio production workstation is getting "xruns" (audio buffer underruns)
   every 20 minutes. The JACK audio server uses a 5ms buffer at 48KHz. cyclictest
   shows max 350us normally but spikes to 8ms during xruns. dmesg shows no errors.
   Work through the diagnosis: check C-states, IRQ distribution, the PREEMPT_RT
   kernel status, and memory locking. What tool reveals whether the 8ms spike
   is from SMI (hardware) vs kernel scheduling vs IRQ handling vs memory paging?
   Design the complete investigation and fix.

3. Compare `SCHED_FIFO` with `SCHED_DEADLINE` for a control loop that runs
   every 10ms and requires 2ms of CPU time within 8ms of its period start.
   For SCHED_FIFO: what priority level is appropriate if there are other RT
   tasks running at priorities 50, 60, and 80? What happens if the control
   loop computation takes 15ms (overruns)? For SCHED_DEADLINE: write the
   correct `sched_setattr` parameters. What does the kernel do if the task
   overruns its 2ms runtime budget?

---

### Interview Deep-Dive

**Foundational:**
Q: What does "real-time" mean in the context of Linux, and what is PREEMPT_RT?
A: Real-time in Linux means DETERMINISTIC response: the system guarantees a bounded worst-case latency for high-priority tasks. It does NOT mean "fast" on average - it means the maximum latency is predictable and bounded. Standard Linux kernel: average latency might be 50 microseconds, but occasionally spikes to 50+ milliseconds due to non-preemptible kernel sections (spinlocks, interrupt handlers). PREEMPT_RT addresses this: it's a kernel configuration (mainlined in kernel 5.15, previously an external patch for 17 years) that makes the Linux kernel fully preemptible. KEY CHANGES: (1) Spinlocks replaced with rt_mutex (sleeping locks with priority inheritance): a high-priority RT task can preempt a low-priority task holding a kernel lock, which gets its priority boosted to prevent priority inversion. (2) Hardware interrupt handlers converted to threaded IRQ handlers: interrupt processing runs as schedulable kernel threads, not in the hard interrupt context. An RT task at SCHED_FIFO priority 99 can preempt an IRQ thread at lower priority. (3) Softirqs and bottom halves made fully preemptible. RESULT: worst-case latency with PREEMPT_RT on isolated CPUs: typically 10-100 microseconds. Standard kernel: can be milliseconds or more. MEASUREMENT: `cyclictest -m -S -p 99 -i 1000 -t 4 -D 3600` - runs a periodic thread at RT priority 99 and measures actual wake-up times over an hour. Max value is the worst-case latency. USE CASES: industrial control (CNC, robots), audio production (JACK), medical devices, automotive ADAS.

**Expert:**
Q: Explain priority inversion, why it's particularly dangerous in real-time systems, and how PREEMPT_RT solves it.
A: PRIORITY INVERSION: Occurs when a high-priority RT task is blocked waiting for a resource held by a low-priority task. Classic example with three tasks (H=high, M=medium, L=low priority): (1) L acquires spinlock protecting shared resource. (2) H tries to acquire spinlock: BLOCKED (spinlock held by L). (3) M becomes runnable: preempts L (M has higher priority than L). (4) M runs for a long time (M has no priority constraints). (5) L cannot run (preempted by M), cannot release spinlock. (6) H waits indefinitely - blocked by M despite H having highest priority! H is effectively running at the priority of L. This caused the Mars Pathfinder rover reset in 1997: high-priority "bus manager" task starved by lower-priority tasks in a classic priority inversion. PREEMPT_RT SOLUTION - PRIORITY INHERITANCE: When H tries to acquire an rt_mutex held by L: the kernel temporarily boosts L's priority to H's priority. Now L can preempt M (L has H's priority). L completes its critical section, releases the mutex, its priority is restored to original. H acquires the mutex and continues. CHAIN INHERITANCE: If L holds another mutex needed by M, and M holds the mutex H needs: priority inheritance chains through all dependencies. L gets boosted to H's priority. IMPLEMENTATION: `rt_mutex` in PREEMPT_RT uses a priority inheritance chain. Standard spinlocks don't support this (can't sleep). PREEMPT_RT's conversion of spinlocks to rt_mutex is what enables priority inheritance throughout the kernel. The Mars Pathfinder mission: the actual fix was enabling priority inheritance on the VxWorks RTOS's mutex that was already there but not enabled. Lesson: priority inheritance must be explicitly designed-in, it doesn't happen automatically with standard locks.
