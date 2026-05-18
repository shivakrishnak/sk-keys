---
id: OSY-102
title: Meltdown and Spectre (2018)
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-009, OSY-010, OSY-011, OSY-054, OSY-055
used_by: []
related: OSY-101, OSY-103, OSY-104
tags:
  - Meltdown
  - Spectre
  - side-channel
  - CPU
  - security
  - speculative-execution
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 102
permalink: /technical-mastery/osy/meltdown-spectre/
---

## TL;DR

Meltdown (2018) exploited CPU speculative execution to let
user processes read kernel memory. Spectre exploits branch
predictor to leak data across process boundaries. Both are
hardware-level side-channel attacks. Mitigations (KPTI for
Meltdown, retpoline for Spectre) added to Linux and Windows
with 5-30% performance cost on I/O-heavy workloads.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-102 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | Meltdown, Spectre, speculative execution, side-channel, KPTI |
| **Prerequisites** | OSY-009, OSY-010, OSY-011, OSY-054, OSY-055 |

---

### Meltdown: Reading Kernel Memory from User Space

```
Background: Speculative Execution
  Modern CPUs execute instructions BEFORE knowing if they're allowed.
  
  Example:
    1. Load kernel_address into register (PROTECTED - should fail)
    2. CPU: starts loading kernel_address speculatively
       (assumes it might be allowed, loads into pipeline)
    3. Use the loaded value to access user-space array:
       user_array[secret_byte * 4096]
    4. CPU realizes: access was not allowed! Exception raised.
    5. CPU rolls back register state (undoes the "fault")
    
  But: the cache line for user_array[secret_byte * 4096]
       was LOADED into CPU cache during speculation!
    
  Cache timing attack:
    For byte_guess in 0..255:
      measure time to access user_array[byte_guess * 4096]
      if fast (cache hit): this is the secret byte!
    One cache line per guess value: 256 probes
    Each probe: ~1ns (hit) vs ~100ns (miss)
    Result: 1 byte of kernel memory leaked per measurement cycle
    
  Full exploit:
    Repeat: read entire kernel address space
    Read: passwords, keys, other processes' data
    
  Why this worked:
    CPU isolation (kernel vs user) = only in SOFTWARE (permission bits)
    CPU hardware: speculatively executes before checking permissions
    CPU cache: side effect that persists after permission check
    Side-channel: timing of cache access reveals the secret
```

---

### Spectre: Cross-Process Branch Misprediction

```
Spectre variant 1 (bounds check bypass):
  
  Code pattern (victim process):
    if (index < array1_size) {
        value = array1[index];           // bounds-checked access
        value2 = array2[value * 4096];   // second access
    }
    
  Normal execution:
    index >= array1_size: branch not taken; no second access
    
  Spectre attack:
    1. Attacker trains the CPU's branch predictor:
       Call this code many times with VALID index values
       Predictor learns: "this branch is usually taken"
    2. Attacker passes an OUT-OF-BOUNDS index:
       index = (pointer to secret data - array1)
    3. CPU's branch predictor predicts: "branch is taken" (wrong!)
    4. Speculatively executes BOTH lines:
       value = memory[secret_address]  (speculative!)
       array2[value * 4096] loaded into cache  (speculative!)
    5. CPU detects: index >= array1_size; flushes speculation
    6. But: cache effect remains!
    7. Timing attack on array2: reveals secret byte
    
  Why harder to fix than Meltdown:
    Meltdown: fix the kernel's page table (KPTI)
    Spectre: the VICTIM'S code uses a legitimate pattern
    Spectre: attacker controls the CPU's branch predictor
    Fix requires: software changes in EVERY vulnerable code pattern
```

---

### Mitigations and Performance Impact

```
Meltdown mitigation: KPTI (Kernel Page Table Isolation)
  
  Before KPTI:
    Kernel virtual address space mapped in every process's page table
    (marked not-present in user mode, but still in page table)
    Speculative execution could access these
    
  After KPTI:
    User-mode page table: NO kernel mappings at all
    Syscall: switch to kernel page table (TOTALLY separate)
    Return to user: switch back to user page table
    
  Cost:
    Every syscall: 2 TLB flushes (switch page tables)
    TLB flush: re-populate on next memory access = 100-1000 ns
    Impact: syscall-heavy workloads (Redis, Postgres, nginx):
      5-30% performance regression on patched kernels
    Impact: compute-bound workloads: minimal effect
    
  Mitigation: PCID (Process Context ID)
    CPU feature: separate TLB entries per process (address space ID)
    With PCID: page table switch does NOT fully flush TLB
    Partial tags: old entries stay, marked with old PCID
    Cost reduced: 1-5% instead of 5-30% for most workloads
    Requires: CPU support (Intel Sandy Bridge+, most modern CPUs)
    
Spectre mitigation: Retpoline (Return Trampoline)
  
  Retpoline: replaces indirect jumps/calls with:
    A return-based trampoline that "traps" speculative execution
    CPU can't speculatively execute the return target
    
  Cost:
    Every indirect function call: slightly more expensive
    JIT-compiled code (JVM): re-JIT with retpoline patterns
    Impact: 1-5% for most workloads
    
Production impact summary:
  Redis (many small commands = many syscalls): up to 15-20% slower
  PostgreSQL (checkpoint I/O patterns): up to 10-15% slower
  Kafka (I/O + syscalls): up to 10% slower
  Java REST APIs (CPU-bound business logic): 1-3% slower
  Compute-bound (ML, compression): near zero impact
```

---

### Checking Mitigation Status

```bash
# Check which vulnerabilities the CPU has and mitigations status:
cat /sys/devices/system/cpu/vulnerabilities/*
# Output:
# /sys/devices/system/cpu/vulnerabilities/meltdown:
#   "Mitigation: PTI"
# /sys/devices/system/cpu/vulnerabilities/spectre_v1:
#   "Mitigation: usercopy/swapgs barriers and __user pointer sanitization"
# /sys/devices/system/cpu/vulnerabilities/spectre_v2:
#   "Mitigation: Enhanced IBRS, IBPB: conditional, RSB filling"
# /sys/devices/system/cpu/vulnerabilities/spec_store_bypass:
#   "Mitigation: Speculative Store Bypass disabled via prctl"
# /sys/devices/system/cpu/vulnerabilities/l1tf:
#   "Mitigation: PTE Inversion"

# Check if PCID is supported (reduces KPTI overhead):
grep -o 'pcid' /proc/cpuinfo | head -1
# Output: "pcid" = supported; blank = not supported

# Verify KPTI is active:
dmesg | grep 'page table isolation'
# "Kernel/User page table isolation: enabled"

# Performance benchmark before/after mitigations:
# (documentation reference, not for production testing)
# Redis: redis-benchmark -n 1000000 -q
# Postgres: pgbench -c 10 -j 2 -T 60
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Meltdown and Spectre are the same vulnerability" | They are related but distinct. Meltdown (CVE-2017-5754): user process reads kernel memory via speculative execution across privilege boundaries. Spectre (CVE-2017-5753, CVE-2017-5715): cross-process data leak via branch predictor manipulation. Different mitigations: Meltdown uses KPTI; Spectre uses retpoline + microcode updates. |
| "The vulnerabilities were patched and are now gone" | Hardware is not patched. The CPU silicon still has the flaw. Software mitigations (KPTI, retpoline, microcode) reduce the attack surface but some Spectre variants remain exploitable in some configurations. AMD CPUs were less affected by Meltdown. Intel CPUs require more aggressive mitigations. New speculative execution vulnerabilities continue to be discovered (MDS, RIDL, ZombieLoad). |
| "These only matter for cloud providers" | Any system running untrusted code is potentially vulnerable: web browsers (JavaScript can exploit Spectre via SharedArrayBuffer timing), multi-tenant clouds, any system where you run code written by others. Browsers reduced timer resolution and disabled SharedArrayBuffer temporarily as mitigations. |

---

### Quick Reference Card

| Vulnerability | CVE | Attack | Mitigation | Cost |
|---------------|-----|--------|------------|------|
| Meltdown | CVE-2017-5754 | User reads kernel memory | KPTI | 5-30% (I/O) |
| Spectre V1 | CVE-2017-5753 | Bounds check bypass | Compiler barriers | 1-2% |
| Spectre V2 | CVE-2017-5715 | Branch predictor injection | Retpoline + IBRS | 1-5% |
| L1TF | CVE-2018-3646 | L1 cache side-channel | L1D Flush | 2-8% |
| Check status | - | - | `cat /sys/devices/system/cpu/vulnerabilities/*` | - |
