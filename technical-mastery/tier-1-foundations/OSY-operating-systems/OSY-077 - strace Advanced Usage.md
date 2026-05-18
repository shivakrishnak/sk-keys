---
id: OSY-077
title: strace Advanced Usage
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-017, OSY-047
used_by: OSY-078, OSY-079
related: OSY-047, OSY-078, OSY-048
tags:
  - strace
  - system-calls
  - debugging
  - performance
  - profiling
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 77
permalink: /technical-mastery/osy/strace-advanced/
---

## TL;DR

strace intercepts and records system calls made by a
process. Advanced usage: `-T` shows time per syscall,
`-c` gives a sorted summary, `-e trace=network` filters
by category, `-f` follows forks. Used to diagnose:
"why is this slow?", "what files is it reading?",
"what network calls is it making?", "why does it fail?"

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-077 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | strace, system calls, -T, -c, -e, -f, debugging |
| **Prerequisites** | OSY-017, OSY-047 |

---

### strace Advanced Flags

```bash
# -T: show time spent in each syscall (in seconds):
strace -T java -jar app.jar 2>&1 | grep -v '0\.000'
# Output:
#   openat(AT_FDCWD, "/etc/resolv.conf", O_RDONLY) = 5 <0.000234>
#   read(5, ...) = 512 <0.001205>
# Lines showing > 0.001s: potentially slow syscalls

# -c: collect statistics; print summary at exit:
strace -c java -jar app.jar
# Output:
#   % time  seconds  usecs/call  calls errors  syscall
#   ------  -------  ----------  ----- ------  -------
#   40.00  1.00000      10000      100         futex
#   30.00  0.75000       5000      150         read
#   15.00  0.37500       2500      150         write
# Identify: which syscall dominates the time?

# -e trace=TYPE: filter by category:
strace -e trace=network java -jar app.jar  # only network syscalls
strace -e trace=file java -jar app.jar     # only file syscalls
strace -e trace=process java -jar app.jar  # only process syscalls
strace -e trace=openat,read,write java -jar app.jar  # specific calls

# -f: follow forked children:
strace -f java -jar app.jar  # trace all threads (JVM spawns many)

# -p: attach to running process:
strace -p $(pgrep java) -T -e trace=futex 2>&1 | head -50
# Attach without restarting the process (non-invasive)
# Note: adds ~30% overhead; don't leave attached in production

# -o: write output to file (instead of stderr):
strace -T -c -o strace_output.txt java -jar app.jar
# Useful when output is large
```

---

### Diagnosing Performance with strace -c

```bash
# Scenario: application seems slow, CPU is low, IO is low
# Hypothesis: blocking on something kernel-related

# Step 1: collect strace summary
strace -c -p $(pgrep java) &
STRACE_PID=$!
sleep 30
kill $STRACE_PID

# Step 2: interpret output
# If futex dominates: thread contention (lock fighting)
#   futex: Java synchronized / ReentrantLock = OS mutex
#   High futex % = lock hot spot
#   
# If nanosleep/clock_nanosleep dominates: Thread.sleep() calls
#   Expected if scheduled work; investigate if too many
#   
# If epoll_wait dominates (high count, low time): healthy event loop
#   epoll_wait: Netty/NIO event loop waiting for I/O
#   
# If read/pread64 dominates: disk I/O bound
#   Check: iostat to correlate
#   
# If sendto/recvfrom dominates: network I/O bound
#   Check: netstat, ss -s

# Scenario: mysterious "too many open files" error
strace -e trace=openat,close -p $(pgrep java) 2>&1 | head -100
# Watch for: openat() calls without matching close()
# Count: strace -e trace=openat -c -p PID
# Leak: openat count >> close count
```

---

### strace for Security Auditing

```bash
# See exactly what files an application opens:
strace -e trace=openat -p $(pgrep java) 2>&1 | awk '{print $NF}' | \
  grep -v "^=" | sort -u
# Lists: every file the JVM opens
# Look for: unexpected files, /etc/passwd, /etc/shadow access

# See network connections established:
strace -e trace=connect,accept4 -p $(pgrep java) 2>&1
# Shows: every TCP connection attempt
# Verify: no unexpected external connections

# See if process reads environment variables:
strace -e trace=openat -p $(pgrep java) 2>&1 | grep "/proc/self/environ"
# /proc/self/environ: process's own environment (expected)
# Another process's /proc/PID/environ: suspicious

# Full syscall log for audit:
strace -f -T -o /var/log/audit/strace-$(date +%s).log java -jar app.jar
# Captures all syscalls with timing
# Useful for: security review, compliance, incident investigation
```

---

### strace Internals and Overhead

```
How strace works:
  Uses ptrace() syscall to intercept the target process
  Before each syscall: kernel calls strace's handler
  strace logs the syscall name + arguments
  After syscall completes: kernel calls strace handler again
  strace logs the return value + time
  
Overhead:
  ptrace adds ~30-50% overhead to the traced process
  NOT suitable for sustained production use
  Short-term profiling (1-5 minutes): acceptable for diagnosis
  
Alternatives with less overhead:
  perf trace: uses kernel tracing (BPF), ~5-10% overhead
    perf trace -p $(pgrep java)  # similar to strace but faster
    
  sysdig: user-space agent + kernel module, ~5% overhead
    sysdig -c topprocs_syscalls
    
  eBPF/BCC tools: near-zero overhead for production
    bpftrace -e 'tracepoint:syscalls:sys_enter_openat {printf("%s\n", comm);}'
    # Trace openat() calls from any process, near-zero overhead
    
  Java-specific: Java Flight Recorder (JFR)
    jcmd PID JFR.start
    Lower overhead than strace, Java-level events
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "strace -c gives exact profiling of where the application spends time" | strace -c only measures time spent INSIDE kernel syscalls. Time in userspace (CPU-bound computation, JIT code, library code between syscalls) is not captured. If strace shows 0.1 second in syscalls but the program ran 10 seconds: 99% of time is in userspace - strace won't diagnose that. Use perf or JFR for userspace profiling |
| "strace is safe to run on production services" | strace with ptrace() adds 30-50% latency overhead to the traced process. In production, this can cause: SLA violations, request timeouts, cascading failures. Run strace on production only in emergencies and for short durations (< 5 minutes). Prefer perf trace, eBPF tools, or sysdig for production profiling |

---

### Quick Reference Card

| Flag | Purpose |
|------|---------|
| `-T` | Show time spent in each syscall |
| `-c` | Collect + print syscall time summary |
| `-e trace=X` | Filter to syscall category (file, network, process) |
| `-f` | Follow forked children/threads |
| `-p PID` | Attach to running process |
| `-o file` | Write output to file |
| Overhead | ~30-50%; use perf trace/eBPF for production |
