---
id: LNX-052
title: "/proc Filesystem (process info, kernel parameters)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★☆
depends_on: LNX-015, LNX-046
used_by: LNX-086, LNX-082
related: LNX-053, LNX-086, LNX-046
tags: [/proc, procfs, process-info, kernel-parameters, sysctl, /proc/sys, /proc/net]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 52
permalink: /technical-mastery/lnx/proc-filesystem/
---

## TL;DR

`/proc` is a virtual filesystem (no disk I/O) that exposes kernel data
structures as readable files. `/proc/PID/` has per-process information:
`cmdline` (command), `status` (state, memory, signals), `fd/` (open file
descriptors), `maps` (memory mappings), `net/` (network info). `/proc/sys/`
exposes tunable kernel parameters - readable with `sysctl -a` and writable
with `sysctl -w` or `echo value > /proc/sys/path`. Persistent parameters
go in `/etc/sysctl.conf` or `/etc/sysctl.d/*.conf`. `/proc/cpuinfo`,
`/proc/meminfo`, `/proc/net/`, and `/proc/diskstats` are common sources
for monitoring tools.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-052 |
| **Difficulty** | ★★☆ Intermediate |
| **Category** | Linux |
| **Tags** | /proc, procfs, process info, kernel parameters, sysctl, /proc/sys |
| **Prerequisites** | LNX-015, LNX-046 |

---

### The Problem This Solves

**Problem 1**: A performance tuning guide says to set `net.ipv4.ip_forward=1`.
Where is this setting? How do you apply it now AND make it persist after
reboot? Understanding `/proc/sys/` and `sysctl` lets you answer both.

**Problem 2**: An application opens thousands of file descriptors. You need
to know WHICH files a specific PID has open, right now. `ls /proc/PID/fd/`
shows all open file descriptors with their targets.

**Problem 3**: You see a Java process consuming 8 GB of memory in `top`.
But is that heap, mapped files, or shared memory? `/proc/PID/status` and
`/proc/PID/maps` reveal exactly what memory is mapped.

---

### Textbook Definition

**/proc filesystem (procfs)**: A virtual filesystem mounted at `/proc` that
the kernel populates on-demand. No data is stored on disk. Reading a file
in `/proc` triggers a kernel function to generate the data. Writing to
writable `/proc/sys/` files modifies kernel state. Mounted automatically
by the kernel during boot; listed in `/proc/mounts` and `/proc/self/mounts`.

**Kernel parameters (sysctl)**: Tunable values in `/proc/sys/` that control
kernel behavior. Organized by subsystem: `kernel/`, `net/`, `vm/`, `fs/`.
`sysctl` is the userspace tool for reading and writing these. Persistent
configuration in `/etc/sysctl.conf` and `/etc/sysctl.d/`.

**Per-process files**: `/proc/<PID>/` directories exist for each running
process. Disappear when the process exits. Contain: process state, memory
maps, file descriptors, signal state, namespace information.

---

### Understand It in 30 Seconds

```bash
# === Process information ===
ls /proc/                    # numeric dirs = PIDs, plus global files
ls /proc/$$                  # current shell's proc directory
cat /proc/$$/cmdline | tr '\0' ' '  # command that started this process
cat /proc/$$/status          # process state, PID, PPID, memory, signals
ls -la /proc/$$/fd/          # open file descriptors (symlinks to targets)
cat /proc/$$/maps            # virtual memory mappings
cat /proc/$$/environ | tr '\0' '\n'  # environment variables

# Useful per-PID files:
PID=1234
cat /proc/$PID/cmdline       # null-separated arguments
cat /proc/$PID/status        # state, memory, signals, cgroups
cat /proc/$PID/stat          # raw numeric stats (used by ps/top)
cat /proc/$PID/smaps         # detailed memory breakdown per mapping
cat /proc/$PID/net/tcp       # TCP connections (network namespace)
cat /proc/$PID/cgroup        # cgroup membership
cat /proc/$PID/oom_score     # OOM killer score (higher = more likely killed)
cat /proc/$PID/limits        # process resource limits (ulimit)
cat /proc/$PID/io            # I/O statistics for this process

# Find what a process is doing:
readlink /proc/$PID/exe      # path to executable
ls -la /proc/$PID/fd/        # open file descriptors
cat /proc/$PID/wchan          # kernel function process is waiting in
cat /proc/$PID/syscall        # current system call (if in kernel)

# === Global /proc files ===
cat /proc/cpuinfo            # CPU details (model, cores, flags)
cat /proc/meminfo            # detailed memory stats
cat /proc/uptime             # system uptime in seconds
cat /proc/loadavg            # load average (1, 5, 15 min)
cat /proc/net/dev            # network interface statistics
cat /proc/net/tcp            # active TCP connections (hex format)
cat /proc/diskstats          # disk I/O statistics (source for iostat)
cat /proc/filesystems        # supported filesystem types
cat /proc/mounts             # current mounts
cat /proc/modules            # loaded kernel modules (same as lsmod)
cat /proc/version            # kernel version string
cat /proc/cmdline            # kernel boot command line

# === /proc/sys - kernel parameters ===
sysctl -a                    # list ALL kernel parameters
sysctl -a | grep ipv4        # filter by subsystem
sysctl net.ipv4.ip_forward   # read specific parameter
sysctl -w net.ipv4.ip_forward=1  # set parameter NOW (not persistent)
echo 1 > /proc/sys/net/ipv4/ip_forward  # equivalent to sysctl -w

# Make persistent:
echo "net.ipv4.ip_forward = 1" >> /etc/sysctl.conf
sysctl -p                    # apply /etc/sysctl.conf
# OR: sysctl.d/ drop-in (preferred):
echo "net.ipv4.ip_forward = 1" > /etc/sysctl.d/99-ipforward.conf
sysctl --system              # apply all /etc/sysctl.d/ files

# === /proc/sys subsystems ===
ls /proc/sys/kernel/         # kernel behavior
ls /proc/sys/net/ipv4/       # IPv4 networking
ls /proc/sys/vm/             # virtual memory
ls /proc/sys/fs/             # filesystem limits
ls /proc/sys/net/core/       # network core settings
```

---

### First Principles

**Why /proc exists:**
```
Traditional approach: separate utility per thing
  ps: reads /proc to get process info
  top: reads /proc to get memory info
  netstat: reads /proc/net to get connections
  iostat: reads /proc/diskstats

/proc is the unified kernel data export interface:
  Applications don't need special system calls to get system info
  They just read files - the most portable interface possible
  The kernel generates data on-demand (no disk I/O)

/proc/PID/status example:
Name:   java
State:  S (sleeping)         <- S=sleeping R=running D=disk wait Z=zombie
Tgid:   12345                <- thread group ID (process PID)
Pid:    12345                <- thread ID
PPid:   1234                 <- parent PID
Threads: 42                  <- number of threads
VmSize: 8192000 kB           <- virtual memory size (includes mapped files)
VmRSS:  4096000 kB           <- resident set size (actual RAM used)
VmSwap: 0 kB                 <- memory swapped out
SigBlk: 0000000000000000     <- blocked signals (hex bitmask)
SigCgt: 0000000180014202     <- caught (handled) signals
voluntary_ctxt_switches: 12000   <- voluntary context switches (syscalls, sleep)
nonvoluntary_ctxt_switches: 500  <- preempted by kernel (CPU competition)
```

**Key kernel parameters in /proc/sys:**
```
vm/ - Virtual Memory:
  vm.swappiness (0-100): how aggressively to use swap
    0: use swap only when absolutely necessary
    60: default (balance between swapping and dropping cache)
    100: swap aggressively (good for dedicated databases on RAM)

  vm.dirty_ratio: % RAM that can be dirty (unsaved to disk)
    15: at 15% dirty: processes slow down (background flush not enough)
  vm.dirty_background_ratio: % RAM where background flush starts
    10: start flushing when 10% dirty

  vm.overcommit_memory:
    0: heuristic (default)
    1: always allow overcommit (dangerous)
    2: never overcommit (total mapped <= RAM + swap)

  vm.max_map_count: max virtual memory areas per process
    65530: default. Java: needs 262144+ for large heaps

net/ipv4/ - Networking:
  net.ipv4.ip_forward: enable IP forwarding (for routing, containers)
  net.ipv4.tcp_syncookies: SYN flood protection
  net.ipv4.tcp_fin_timeout: TIME_WAIT timeout (default 60s)
  net.core.somaxconn: max listen backlog (default 128 -> set 1024+)
  net.ipv4.tcp_max_syn_backlog: SYN queue size

fs/ - Filesystem:
  fs.file-max: system-wide max open files
  fs.inotify.max_user_watches: max inotify watches (increase for IDEs)
  fs.suid_dumpable: allow core dumps of SUID processes

kernel/ - Kernel behavior:
  kernel.pid_max: max PID number (default 32768)
  kernel.panic: seconds before auto-reboot after kernel panic
  kernel.dmesg_restrict: restrict non-root dmesg access
```

---

### Thought Experiment

Diagnosing a high memory process using /proc:

```bash
# Scenario: java process (PID 5678) shows 16 GB in top but heap is 8 GB

# Step 1: Get basic memory breakdown:
cat /proc/5678/status | grep -E "Vm(Size|RSS|Swap|Shared)|Threads"
# VmSize:  16000000 kB  <- virtual address space (includes unmapped)
# VmRSS:    8000000 kB  <- resident (actually in RAM)
# VmSwap:        0 kB  <- not swapped
# Threads:        42   <- 42 threads (each has stack)

# VmSize >> VmRSS is NORMAL for Java:
# Java maps many files (JARs, native libs) but only some are in RAM

# Step 2: Detailed memory breakdown via smaps:
cat /proc/5678/smaps_rollup
# Private_Clean:   200000 kB  <- private pages not modified (code, libs)
# Private_Dirty:  7000000 kB  <- private modified pages (heap, stack)
# Shared_Clean:    800000 kB  <- shared pages not modified
# Rss:            8000000 kB  <- total resident

# Step 3: What is mapped?
grep -E "heap|stack|anon" /proc/5678/maps | head -20
# 7f0000000000-7f0300000000 rw-p 00000000 00:00 0  [heap]
# The heap: 3 GB (0x7f0000000000 to 0x7f0300000000 = 3GB range)
# 7fffc0000000-7fffde000000 rw-p ... [stack:5679]
# Thread stacks: each thread has 8MB default

# Step 4: List all mapped files (JARs, native libs):
cat /proc/5678/maps | grep "\.jar\|\.so" | awk '{print $6}' | sort -u
# /usr/lib/jvm/java-17-openjdk/...
# /app/myapp.jar
# /app/lib/dependency.jar
# ... lots of JARs

# Step 5: How many file descriptors?
ls /proc/5678/fd | wc -l
# 2048  <- lots of FDs! Check ulimits:
cat /proc/5678/limits | grep "open files"
# Max open files: 4096 soft limit, 65536 hard

# Conclusion:
# 16 GB virtual = normal for JVM (maps all JARs)
# 8 GB RSS = actual RAM = matches heap setting + thread stacks + mapped files
# Not a memory problem - just Java's memory model
```

---

### Mental Model / Analogy

```
/proc = the hospital's patient monitoring system
  (all patient data available through a unified interface)

/proc/PID/ = patient's individual chart
  /proc/1234/status = vital signs: pulse (CPU state), weight (memory)
  /proc/1234/fd/ = what equipment is attached (open files/sockets)
  /proc/1234/maps = what medications/nutrients are being delivered (memory maps)
  /proc/1234/cmdline = admission reason (what command started this process)
  /proc/1234/oom_score = triage priority (higher = treated first, or in OOM: killed first)

/proc/sys/ = hospital settings and protocols
  /proc/sys/vm/swappiness = protocol for when to use emergency blood bank (swap)
  /proc/sys/net/ = communication protocols (how to handle network traffic)
  /proc/sys/kernel/ = hospital-wide policies

sysctl -w = update protocol right now (doesn't survive hospital restructuring/reboot)
/etc/sysctl.conf = written hospital policy (survives restructuring)
sysctl -p = "please re-read the policy book"

/proc/cpuinfo = doctor's credentials (how fast can you work?)
/proc/meminfo = current ICU bed availability (how much RAM is free?)
/proc/net/ = hospital communication log (network connections)
```

---

### Gradual Depth - Five Levels

**Level 1:**
Know: `/proc/PID/` (per-process info), `/proc/sys/` (kernel parameters),
`sysctl -a` (list all), `sysctl -w param=value` (set), persistent in
`/etc/sysctl.conf`. Key files: `/proc/cpuinfo`, `/proc/meminfo`,
`/proc/PID/fd/`, `/proc/PID/status`.

**Level 2:**
`/proc/PID/maps` vs `/proc/PID/smaps` (aggregate vs per-mapping memory).
`/proc/net/tcp` (hex-encoded connection table). `/proc/PID/net/tcp` (connections
in process's network namespace). `/proc/PID/ns/` (namespace symlinks - for
understanding container isolation). `/proc/PID/cgroup` (cgroup membership).

**Level 3:**
`/proc/PID/pagemap`: physical address of each virtual page (root only).
`/proc/sysvipc/`: System V IPC (shared memory, semaphores, message queues).
`/proc/buddyinfo`: memory allocator state (buddy allocator). `/proc/slabinfo`:
kernel slab allocator usage (object caches). `/proc/zoneinfo`: NUMA memory
zones. `/proc/PID/oom_adj` and `oom_score_adj`: tune OOM killer behavior
per-process (`-1000` = never kill, `1000` = kill first).

**Level 4:**
`/proc/PID/mem`: process's memory, readable if you have the right ptrace
permissions (used by debuggers). `/proc/kcore`: the entire kernel's address
space as an ELF file (for kernel debugging with gdb). `/proc/kallsyms`:
kernel symbol table with addresses (for crash analysis). `/proc/iomem`:
I/O memory regions. `/proc/ioports`: I/O port regions. `/proc/interrupts`:
interrupt counts per CPU per IRQ.

**Level 5:**
`/proc` and container isolation: each container has its own PID namespace.
Inside a container, `/proc/` shows only that container's processes. But the
HOST's `/proc/` shows all processes from all containers (with host PIDs).
This is why `ps aux` inside a Docker container (without --pid=host) shows
only container processes. Security: unprivileged access to `/proc/PID/mem`
(CVE-2012-0056), `/proc/sysrq-trigger` (privileged), kernel parameter
restrictions. `/proc/sys/kernel/yama/ptrace_scope` controls ptrace-based
debugging. seccomp (LNX-078) uses `/proc/sys/kernel/ngroups_max` and similar.

---

### Code Example

**BAD - incorrect kernel parameter management:**
```bash
# BAD 1: Editing /proc/sys directly without sysctl:
echo 1 > /proc/sys/net/ipv4/ip_forward
# Works but: not persistent! Lost on reboot
# No logging or audit trail of the change
# No validation of the value

# BAD 2: Using sysctl -w without persistence:
sysctl -w net.ipv4.ip_forward=1
# Same problem: lost on reboot

# GOOD: Set now AND persist:
sysctl -w net.ipv4.ip_forward=1          # apply immediately
echo "net.ipv4.ip_forward = 1" > /etc/sysctl.d/99-ip-forward.conf
# Verify the file is formatted correctly:
sysctl --system   # apply all sysctl.d files (should show the new value)
# Confirm:
sysctl net.ipv4.ip_forward    # should show: net.ipv4.ip_forward = 1

# BAD 3: Reading /proc/net/tcp directly (hex format):
cat /proc/net/tcp
# 0: 00000000:0016 00000000:0000 0A 00000000:00000000 00:00000000 00000000  0  0 0 1 0000000000000000 10 0 0 10 0
# Completely unreadable - hex local/remote addresses

# GOOD: Use ss or netstat for human-readable output:
ss -tlnp     # human-readable TCP listeners
ss -tunap    # all connections with process info

# Or decode /proc/net/tcp with python if needed:
python3 -c "
import socket, struct
with open('/proc/net/tcp') as f:
    for line in f.readlines()[1:]:
        fields = line.split()
        local = fields[1]
        host, port = local.split(':')
        host_ip = socket.inet_ntoa(struct.pack('<L', int(host, 16)))
        port_num = int(port, 16)
        if fields[3] == '0A':  # LISTEN state
            print(f'LISTEN {host_ip}:{port_num}')
" 2>/dev/null | head -10
```

**GOOD - /proc for operational tasks:**
```bash
#!/bin/bash
# proc-health-check.sh

echo "=== System Info from /proc ==="
echo "Kernel: $(cat /proc/version | awk '{print $3}')"
echo "Uptime: $(awk '{printf "%.0f days %.0f hours\n", $1/86400, ($1%86400)/3600}' /proc/uptime)"
echo "Load: $(cat /proc/loadavg)"

echo ""
echo "=== Memory (from /proc/meminfo) ==="
awk '
/MemTotal:/ {total=$2}
/MemAvailable:/ {avail=$2}
/SwapTotal:/ {stotal=$2}
/SwapFree:/ {sfree=$2}
END {
    printf "RAM: %.1f GB total, %.1f GB available\n", total/1024/1024, avail/1024/1024
    if (stotal > 0) printf "Swap: %.1f GB total, %.1f GB free\n", stotal/1024/1024, sfree/1024/1024
}' /proc/meminfo

echo ""
echo "=== Key Kernel Parameters ==="
params=(
    "net.ipv4.ip_forward"
    "vm.swappiness"
    "fs.file-max"
    "net.core.somaxconn"
    "vm.max_map_count"
)
for p in "${params[@]}"; do
    val=$(sysctl -n "$p" 2>/dev/null)
    printf "  %-35s = %s\n" "$p" "$val"
done

echo ""
echo "=== Top Processes by Open FDs ==="
for pid in /proc/[0-9]*/fd; do
    count=$(ls "$pid" 2>/dev/null | wc -l)
    pidnum="${pid%/fd}"
    pidnum="${pidnum#/proc/}"
    echo "$count $pidnum $(cat /proc/$pidnum/comm 2>/dev/null)"
done | sort -rn | head -5

echo ""
echo "=== CPU Info ==="
grep -E "^(model name|cpu cores|siblings)" /proc/cpuinfo | head -3
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "/proc files are real files on disk" | `/proc` is a virtual filesystem. No data is written to disk. Reading a file in `/proc` triggers a kernel function to generate the output. `df -h` shows `/proc` as 0 bytes. The kernel generates the content on-demand when you `cat` it. Writing to `/proc/sys/` immediately modifies kernel state. |
| "`sysctl -w` change persists across reboots" | No. `sysctl -w` modifies the running kernel's parameter via `/proc/sys/` but is NOT persistent. Rebooting resets all parameters to defaults (or values set in `/etc/sysctl.conf`). Persistent configuration requires adding the parameter to `/etc/sysctl.d/` or `/etc/sysctl.conf` and running `sysctl --system`. |
| "`/proc/PID/` exists for all processes" | `/proc/PID/` exists only for currently running processes. The moment a process exits, its `/proc/PID/` directory disappears. A zombie process (state Z) DOES have a `/proc/PID/` directory (that's how `ps` reports it), but only the minimal fields remain. |
| "VmSize in /proc/PID/status shows actual RAM usage" | VmSize is virtual address space - it includes: code, heap, stack, memory-mapped files (including all jar files, shared libraries), and unmapped-but-reserved regions. For Java, VmSize is typically 3-10x VmRSS (actual RAM). VmRSS (Resident Set Size) is actual RAM. For Java tuning, use VmRSS, or better: use JVM's own `-Xmx` heap size plus the process stats from `jstat`. |
| "`/proc/sys/` parameters are the only way to tune the kernel" | Multiple ways to tune kernel behavior: (1) `/proc/sys/` (sysctl) = general parameters. (2) `ulimit` / `/etc/security/limits.conf` = per-process resource limits. (3) cgroups (`/sys/fs/cgroup/`) = resource limits per process group. (4) Kernel boot parameters in GRUB (`/proc/cmdline`). (5) Module parameters (`/etc/modprobe.d/`, `modprobe options`). Each addresses different aspects. |

---

### Failure Modes & Diagnosis

**Application crashes with "Too many open files":**
```bash
# Symptom: Java app: "java.io.IOException: Too many open files"

# Step 1: Find the PID and current FD count:
PID=$(pgrep java | head -1)
fd_count=$(ls /proc/$PID/fd 2>/dev/null | wc -l)
echo "PID $PID has $fd_count open file descriptors"

# Step 2: Check current limits:
cat /proc/$PID/limits | grep "open files"
# Max open files: 1024 (soft)  4096 (hard)

# Step 3: See what files are open:
ls -la /proc/$PID/fd/ | awk '{print $NF}' | sort | uniq -c | sort -rn | head
# 2048 /var/log/myapp.log  <- only one file? No - 2048 open connections?
ls -la /proc/$PID/fd/ | grep socket | wc -l  # how many sockets?

# Step 4: Increase limit for running process (TEMPORARY):
# Can't increase soft limit beyond hard limit without root
# With root: cat /proc/$PID/limits | ...
# Better: use prlimit:
prlimit --pid $PID --nofile=65536:65536

# Step 5: Permanent fix:
# In /etc/security/limits.d/myapp.conf:
echo "myapp_user soft nofile 65536" >> /etc/security/limits.d/myapp.conf
echo "myapp_user hard nofile 65536" >> /etc/security/limits.d/myapp.conf
# OR in systemd service file:
# [Service]
# LimitNOFILE=65536

# Step 6: Fix the root cause (file descriptor leak):
# Watch FD count over time:
watch -n 5 "ls /proc/$PID/fd | wc -l"
# If steadily growing -> FD leak in application code
```

---

### Related Keywords

**Foundational:**
LNX-015 (Process Management), LNX-046 (Filesystem Internals)

**Builds on this:**
LNX-086 (Kernel Parameters), LNX-082 (System Call Interface)

**Related:**
LNX-053 (/sys Filesystem), LNX-016 (System Monitoring)

---

### Quick Reference Card

| File | Contents |
|------|---------|
| `/proc/cpuinfo` | CPU model, cores, features |
| `/proc/meminfo` | Memory stats |
| `/proc/PID/status` | Process state, memory, signals |
| `/proc/PID/fd/` | Open file descriptors |
| `/proc/PID/maps` | Virtual memory mappings |
| `/proc/PID/cmdline` | Process command line |
| `/proc/PID/limits` | Per-process resource limits |
| `/proc/net/tcp` | TCP connections (hex) |
| `/proc/sys/` | Tunable kernel parameters |

**3 things to remember:**
1. `/proc` is virtual - no disk storage; data generated on-demand by kernel
2. `sysctl -w` sets parameters NOW but NOT persistent; add to `/etc/sysctl.d/` for persistence
3. `VmSize` = virtual memory (huge for Java); `VmRSS` = actual RAM used

---

### Transferable Wisdom

`/proc/sys/` parameters appear in: Docker (`--sysctl` option passes kernel
params into containers), Kubernetes (`sysctls` in pod securityContext for
safe or unsafe sysctls), Ansible (`sysctl` module writes to `/etc/sysctl.d/`
and applies), Terraform cloud-init (writes sysctl params during VM init).
The patterns learned here: read /proc for insight, write /proc/sys (via
sysctl) for tuning.

`/proc/PID/fd/` appears in: debugging Java (find which files/sockets a JVM
has open), finding "deleted but open" files consuming disk space (shows as
deleted in ls output), Docker container debugging (`ls /proc/$(docker
inspect --format '{{.State.Pid}}' CONTAINER)/fd/`). Kubernetes: use
`kubectl exec pod -- ls /proc/1/fd/` to inspect container's file descriptors
without tools installed in the container.

---

### The Surprising Truth

`/proc/PID/mem` is the entire address space of a process, readable and
writable by root (with ptrace permission). This file is how debuggers (gdb,
strace) read and modify process memory without the process knowing - they open
`/proc/PID/mem`, seek to a virtual address, and read/write. This is also
how Python's `pymalloc` can be debugged: read heap from `/proc/PID/mem`.
Security implication: if an attacker has root, they can inject arbitrary code
into any running process by writing to `/proc/PID/mem`. This is used by
rootkits. Mitigation: `kernel.yama.ptrace_scope=1` (sysctl) prevents a
process from ptrace-attacking another unless it's an ancestor. Docker limits
this with `--cap-drop=SYS_PTRACE`. This is why security-hardened environments
restrict `CAP_SYS_PTRACE`: without it, you can't use traditional debuggers,
but also can't be debugged/injected by other processes. The trade-off between
debuggability and security is why Kubernetes defaults to `ptrace_scope=1`
on most distributions but needs it relaxed for performance profiling tools
like perf and async-profiler.

---

### Mastery Checklist

- [ ] Can read key per-process files from /proc/PID/ (status, fd, maps)
- [ ] Can list and set kernel parameters with sysctl
- [ ] Knows how to make sysctl changes persistent via /etc/sysctl.d/
- [ ] Can diagnose "too many open files" using /proc/PID/fd and limits
- [ ] Understands that /proc is virtual (no disk I/O when reading)

---

### Think About This

1. An application is reporting "connection refused" errors even though
   `netstat -tlnp` shows the service is listening. You check
   `/proc/net/tcp` and find the listening socket but also notice the
   queue is full (the Recv-Q column). What kernel parameter in
   `/proc/sys/net/` controls the maximum connection backlog? What
   is the default, why is it too small for modern applications, and
   what value should you set?

2. You need to determine if a Java application has a file descriptor
   leak without restarting it. Describe the exact sequence: (a) which
   `/proc` files to read, (b) how to identify which file types are leaking,
   (c) how to set a temporary FD limit increase, and (d) how to watch
   for the leak growing in real-time.

3. After enabling `vm.swappiness=0` in `/proc/sys/vm/swappiness`, a DBA
   claims database performance improved dramatically because the system
   stopped swapping. But the next day after a reboot, the system is
   slow again. The DBA blames the kernel. What is the actual issue?
   Write the complete fix including the command, the file to edit,
   and the command to verify persistence.

---

### Interview Deep-Dive

**Foundational:**
Q: What is /proc/sys/ and how do you use it to tune kernel parameters?
A: `/proc/sys/` is the kernel's parameter interface exposed through the virtual `/proc` filesystem. Parameters are organized by subsystem: `kernel/` (kernel behavior), `net/` (networking), `vm/` (virtual memory), `fs/` (filesystem limits). To read: `cat /proc/sys/net/ipv4/ip_forward` or `sysctl net.ipv4.ip_forward`. To set immediately: `echo 1 > /proc/sys/net/ipv4/ip_forward` or `sysctl -w net.ipv4.ip_forward=1`. Both modify the running kernel - NOT persistent. To make persistent: create a file in `/etc/sysctl.d/`: `echo "net.ipv4.ip_forward = 1" > /etc/sysctl.d/99-ip-forward.conf`. Apply without reboot: `sysctl --system` (reads all sysctl.d files). Verify: `sysctl net.ipv4.ip_forward`. Common production settings: `net.core.somaxconn=1024` (increases listen backlog for web servers), `vm.swappiness=10` (reduce swap on database servers), `fs.file-max=2000000` (system-wide FD limit for high-connection servers), `net.ipv4.ip_forward=1` (required for Docker/Kubernetes networking), `vm.max_map_count=262144` (required for Elasticsearch/JVM large heaps).

**Expert:**
Q: A microservice team reports random "connection reset" errors. You suspect the kernel's connection queue is full. How do you diagnose this using /proc and what parameters would you tune?
A: Connection queue overflow causes "connection reset" from the kernel before the application even sees the connection. Diagnosis: (1) Check current listen backlog settings: `sysctl net.core.somaxconn` (max queue size). Default 128 on most distros - severely undersized for modern services. (2) Check SYN queue: `sysctl net.ipv4.tcp_max_syn_backlog`. SYN half-open connections before completing handshake. (3) Check for queue overflows: `netstat -s | grep -i "listen\|overflow\|reset"`. Specifically: "listen queue overflows" counter - if incrementing, queue is definitely full. (4) Check actual queue depth per socket: `ss -tlnp` shows Recv-Q (current queue depth) and Send-Q (max queue depth). If Recv-Q approaches Send-Q: queue filling up. (5) `/proc/net/tcp` column 4 hex: local port, column 5: Recv-Q. (6) Check if application has backlog set: Java Tomcat's `acceptCount`, Spring Boot's `server.tomcat.accept-count`. The application's `listen(fd, backlog)` call sets the kernel queue size UP TO `somaxconn`. Fixes: `sysctl -w net.core.somaxconn=1024` (kernel max), configure application to use backlog=1024 in listen() call. Persistent: `/etc/sysctl.d/99-network.conf` with `net.core.somaxconn=1024` and `net.ipv4.tcp_max_syn_backlog=2048`. Additional: `net.ipv4.tcp_syncookies=1` (SYN flood protection - allows connections even when SYN queue full by using crypto cookies).
