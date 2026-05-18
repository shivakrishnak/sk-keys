---
id: LNX-086
title: "Linux Kernel Parameters (sysctl, /proc/sys tuning)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★★
depends_on: LNX-003, LNX-035
used_by: LNX-084, LNX-093, LNX-100
related: LNX-083, LNX-084, LNX-093, LNX-035
tags: [sysctl, proc-sys, kernel-parameters, vm-tuning, net-tuning, dirty-ratio, vm-swappiness, inotify, file-max, overcommit, hugepages, pid-max, kernel-panic, sysctl-d, runtime-tuning]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 86
permalink: /technical-mastery/lnx/linux-kernel-parameters-sysctl/
---

## TL;DR

`sysctl` reads/writes Linux kernel parameters at runtime via `/proc/sys/`.
Key categories: **kernel** (`kernel.pid_max`, `kernel.core_pattern`,
`kernel.panic`), **vm** (`vm.swappiness`, `vm.overcommit_memory`,
`vm.dirty_ratio`, `vm.nr_hugepages`), **net** (`net.core.somaxconn`,
`net.ipv4.tcp_*`), **fs** (`fs.file-max`, `fs.inotify.max_user_watches`).
Temporary change: `sysctl -w vm.swappiness=10`. Persistent: write to
`/etc/sysctl.d/*.conf`, apply with `sysctl -p`. Production tuning examples:
`fs.inotify.max_user_watches=524288` (for containers/IDEs that hit the
default 8192 limit), `vm.dirty_ratio=10` (flush dirty pages earlier),
`net.core.somaxconn=32768` (listen backlog). `sysctl -a 2>/dev/null` lists
all 1000+ parameters.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-086 |
| **Difficulty** | ★★★ Advanced |
| **Category** | Linux |
| **Tags** | sysctl, /proc/sys, kernel parameters, vm tuning, dirty ratio, swappiness, inotify, file-max, hugepages |
| **Prerequisites** | LNX-003 (Linux filesystem hierarchy), LNX-035 (Memory management) |

---

### The Problem This Solves

**Problem 1**: A containerized application fails with "ENOSPC: no space left
on device" but `df -h` shows 80GB free. `dmesg | grep inotify` reveals:
"inotify watch limit hit". The default `fs.inotify.max_user_watches=8192`
limits how many filesystem watches can be created. Modern IDEs (VS Code,
IntelliJ), container runtimes (containerd), and logging agents (Filebeat)
each create thousands of watches. Fix: `sysctl -w fs.inotify.max_user_watches=524288`.

**Problem 2**: A database server with 256GB RAM shows high disk I/O at
random intervals, causing latency spikes. `vmstat 1` shows periodic bursts
of disk writes (pdflush). Default `vm.dirty_ratio=20%` lets 51GB of RAM
fill with dirty pages before writeback starts. During the flush: I/O
bandwidth saturated for seconds. Fix: `vm.dirty_ratio=5` (flush when 12.8GB
dirty), `vm.dirty_background_ratio=2` (background writeback at 5GB).
Smoother I/O, fewer latency spikes.

---

### Textbook Definition

**sysctl**: A system call and corresponding userspace utility for reading
and writing Linux kernel parameters. The kernel exposes parameters via a
virtual filesystem mounted at `/proc/sys/`. Each parameter is a "file" in
this hierarchy. `sysctl -w` writes immediately (runtime, lost on reboot).
Files in `/etc/sysctl.d/` are read by `sysctl -p` or `systemd-sysctl.service`
at boot to make changes persistent.

**Parameter namespaces:**
| Namespace | Prefix | Coverage |
|-----------|--------|---------|
| Kernel | `kernel.*` | PID limits, core dumps, panic behavior, scheduling |
| Virtual Memory | `vm.*` | Memory management, swapping, dirty page policy |
| Network | `net.*` | TCP/IP, socket buffers, interface queues |
| Filesystem | `fs.*` | File descriptor limits, inotify, aio |
| Cryptography | `crypto.*` | Kernel crypto algorithms |

---

### Understand It in 30 Seconds

```bash
# === sysctl basics ===

# List ALL kernel parameters (1000+):
sysctl -a 2>/dev/null | head -20
# kernel.pid_max = 32768
# kernel.panic = 0
# vm.swappiness = 60
# vm.dirty_ratio = 20
# ...

# Read a specific parameter:
sysctl vm.swappiness
# vm.swappiness = 60

# Write a parameter (runtime only, lost on reboot):
sysctl -w vm.swappiness=10
# vm.swappiness = 10

# Alternative: write directly to /proc/sys/:
# sysctl parameter 'vm.swappiness' -> /proc/sys/vm/swappiness
echo 10 > /proc/sys/vm/swappiness   # direct write
cat /proc/sys/vm/swappiness          # direct read

# === Persistent configuration ===

# Create a tuning file:
cat > /etc/sysctl.d/99-production.conf << 'EOF'
# --- vm tuning ---
vm.swappiness = 10                 # prefer RAM over swap
vm.dirty_ratio = 10                # flush dirty pages > 10% RAM
vm.dirty_background_ratio = 3     # background writeback > 3% RAM

# --- fs tuning ---
fs.file-max = 2097152             # max open files system-wide
fs.inotify.max_user_watches = 524288   # inotify limit
fs.inotify.max_user_instances = 1024   # inotify instances

# --- net tuning ---
net.core.somaxconn = 32768        # listen() backlog
net.core.netdev_max_backlog = 5000
net.ipv4.tcp_tw_reuse = 1
net.ipv4.ip_local_port_range = 1024 65535

# --- kernel ---
kernel.pid_max = 4194304          # max PIDs (for containers)
kernel.core_pattern = /var/crash/core.%e.%p.%t
EOF

# Apply immediately (without reboot):
sysctl -p /etc/sysctl.d/99-production.conf
# Outputs each parameter applied

# Apply ALL sysctl.d files:
sysctl --system

# Verify:
sysctl vm.dirty_ratio vm.dirty_background_ratio
# vm.dirty_ratio = 10
# vm.dirty_background_ratio = 3

# === Key vm parameters ===
sysctl vm.swappiness        # 0=no swap, 60=default, 100=aggressive swap
sysctl vm.overcommit_memory # 0=heuristic, 1=always allow, 2=strict
sysctl vm.nr_hugepages      # pre-allocated 2MB hugepages
sysctl vm.dirty_ratio       # % of RAM: start flushing dirty pages
sysctl vm.dirty_background_ratio # % of RAM: background writeback starts

# === Key fs parameters ===
sysctl fs.file-max          # system-wide FD limit
sysctl fs.nr_open           # per-process FD limit max
# Current FDs in use:
cat /proc/sys/fs/file-nr    # used / 0 / max
# 3456 0 2097152

sysctl fs.inotify.max_user_watches   # default 8192 (very low!)
sysctl fs.aio-max-nr                 # max async I/O requests

# === Key kernel parameters ===
sysctl kernel.pid_max              # max PID (default 32768)
sysctl kernel.threads-max          # max threads
sysctl kernel.panic                # seconds to reboot on panic (0=no)
sysctl kernel.panic_on_oops        # panic on kernel oops (0=warn, 1=panic)
sysctl kernel.core_pattern         # core dump path pattern
sysctl kernel.perf_event_paranoid  # perf permissions (2=unprivileged denied)
sysctl kernel.kptr_restrict        # hide kernel addresses (2=strict)

# === View parameters that changed from defaults ===
diff <(sysctl -a 2>/dev/null | sort) \
     <(sysctl --system 2>/dev/null | sort) | head -20
```

---

### First Principles

**How sysctl parameters work internally:**
```
/proc/sys/ is a virtual filesystem (procfs/sysctl subsystem):
  Not stored on disk - kernel generates content on read
  Reading /proc/sys/vm/swappiness:
    VFS lookup -> sysctl handler for vm.swappiness
    Reads current value from kernel variable (vm_swappiness)
    Returns ASCII representation
  
  Writing /proc/sys/vm/swappiness:
    VFS write -> sysctl handler
    Validates value (range check, type check)
    Updates kernel variable (vm_swappiness)
    Takes effect immediately (next scheduler/mm decision)

Kernel implementation (simplified):
  // vm.swappiness registered:
  static struct ctl_table vm_table[] = {
      {
          .procname = "swappiness",
          .data     = &vm_swappiness,
          .maxlen   = sizeof(vm_swappiness),
          .mode     = 0644,
          .proc_handler = proc_dointvec_minmax,
          .extra1   = SYSCTL_ZERO,
          .extra2   = SYSCTL_ONE_HUNDRED,
      },
  };
  // proc_dointvec_minmax: validates value in [0,100]
  
  // Used by kernel memory management:
  static unsigned long get_scan_count(...) {
      // vm_swappiness controls ratio of
      // anon vs file page eviction:
      anon_prio = vm_swappiness;    // high = swap more aggressively
      file_prio = 200 - vm_swappiness;
  }

vm.dirty_ratio and write buffering:
  Linux buffers all file writes in the page cache (dirty pages):
    write("file", buf, len):
      page cache updated (in RAM)
      page marked "dirty" (needs to be written to disk)
      syscall returns (very fast!)
      disk write happens LATER (asynchronously)
  
  Two thresholds control when writeback happens:
    dirty_background_ratio = 3% of RAM:
      Background pdflush thread starts writing
      Application NOT blocked - writeback in background
    
    dirty_ratio = 10% of RAM:
      Application-level throttling begins
      ANY process calling write() that produces dirty page
      is forced to wait while writeback happens
      (this is what causes application latency spikes)
  
  With 256GB RAM:
    dirty_background_ratio=3%: background writeback at 7.7GB
    dirty_ratio=10%: app blocking at 25.6GB
  
  Default dirty_ratio=20%: blocking at 51.2GB!
  Even NVMe SSDs can't flush 51GB quickly -> long pauses

kernel.pid_max and container density:
  Default pid_max=32768: max 32768 processes system-wide
  Modern containerized hosts run 100+ containers, each with
    multiple processes/threads (Java apps alone: 100+ threads)
  At 100 containers * 200 threads = 20,000 threads
  A single GC event: fork() 2 processes -> pid = 32769 -> EAGAIN!
  "Resource temporarily unavailable" = pid exhaustion
  
  Fix: sysctl -w kernel.pid_max=4194304 (max on 64-bit: 4M)
  Also check: /proc/sys/kernel/threads-max

net.core.somaxconn and connection backlog:
  listen(fd, backlog) creates two queues:
    SYN queue: half-open connections (after SYN, before ACK)
    ACCEPT queue: fully established connections waiting for accept()
  
  somaxconn: max size of ACCEPT queue (kernel-enforced cap)
  If backlog > somaxconn: kernel silently caps at somaxconn
  
  Default somaxconn=4096 (was 128 until kernel 5.4!)
  Under high connection rate: backlog fills -> new connections dropped
  
  Fix: net.core.somaxconn=32768
  Also: application must call listen(fd, backlog) with large backlog
  Java Netty: channel.option(ChannelOption.SO_BACKLOG, 1024)
  Spring Boot: server.tomcat.accept-count=100 (Tomcat queue)
```

---

### Thought Experiment

Comprehensive production tuning for a high-traffic Java application server:

```bash
# System: 128GB RAM, 32 CPUs, NVMe SSD, 10Gbps NIC
# App: Spring Boot with 100 concurrent threads, 10K connections/sec

# === Step 1: Diagnose current limits ===

# Check open file descriptors:
cat /proc/sys/fs/file-nr
# 45678 0 65536   <- using 45678 of 65536 max -> approaching limit!

# Check inotify:
ls /proc/*/fd 2>/dev/null | wc -l   # rough FD count
sysctl fs.inotify.max_user_watches  # default 8192

# Check dirty page writeback:
cat /proc/meminfo | grep -E "Dirty|Writeback"
# Dirty:     12582912 kB  <- 12GB dirty pages!
# Writeback: 0 kB         <- nothing being written right now

# This means: dirty_ratio or dirty_background_ratio not reached yet
# With 128GB * 20% = 25.6GB dirty_ratio: we have 12GB, not blocked
# But when a write burst pushes to 25.6GB: big pause

# === Step 2: Apply comprehensive tuning ===
cat > /etc/sysctl.d/99-java-server.conf << 'EOF'
# --- File descriptor limits ---
# System-wide open FD max:
fs.file-max = 2097152

# inotify limits (for JVM file watching, IDEs, agents):
fs.inotify.max_user_watches = 524288
fs.inotify.max_user_instances = 4096
fs.inotify.max_queued_events = 32768

# --- Memory management ---
# Reduce swap usage (prefer RAM for JVM heap):
vm.swappiness = 1   # Almost never swap (0 can cause OOM issues)

# Dirty page writeback - prevent large I/O spikes:
# 128GB RAM: background at 2.5GB, blocking at 6.4GB
vm.dirty_ratio = 5
vm.dirty_background_ratio = 2

# Writeback timing:
vm.dirty_expire_centisecs = 500   # pages dirty > 5s: writeback
vm.dirty_writeback_centisecs = 100  # writeback thread interval: 1s

# Huge pages for JVM (if using -XX:+UseHugePages):
# Pre-allocate: 16GB / 2MB = 8192 hugepages
vm.nr_hugepages = 8192

# Transparent hugepages (THP) - controversial for JVM:
# Some JVMs benefit, some have issues with THP allocation stalls
# echo madvise > /sys/kernel/mm/transparent_hugepage/enabled
# (not a sysctl - set separately)

# Overcommit: Java allocates large virtual address space
# heuristic (0) = reasonable, strict (2) = may fail Java startup
vm.overcommit_memory = 0

# --- Process/thread limits ---
kernel.pid_max = 4194304      # max PIDs (containers need more)
kernel.threads-max = 2097152  # max threads

# Core dumps: store in /var/crash with info in filename
kernel.core_pattern = /var/crash/core.%e.%p.%t
kernel.core_uses_pid = 1

# Panic behavior: auto-reboot after 30s (not recommended for debugging)
kernel.panic = 0               # don't auto-reboot (debug first)
kernel.panic_on_oops = 1      # panic on oops (usually want this)

# --- Network tuning ---
# Connection backlog (for high-connection-rate servers):
net.core.somaxconn = 65536
net.core.netdev_max_backlog = 5000

# TCP TIME_WAIT recycling:
net.ipv4.tcp_tw_reuse = 1

# Ephemeral port range:
net.ipv4.ip_local_port_range = 1024 65535

# TCP keepalive (detect dead connections sooner):
net.ipv4.tcp_keepalive_time = 120     # start probes after 2min idle
net.ipv4.tcp_keepalive_intvl = 30    # probe interval: 30s
net.ipv4.tcp_keepalive_probes = 3    # drop after 3 missed probes

# Backlog of SYN requests (SYN flood protection):
net.ipv4.tcp_max_syn_backlog = 4096
net.ipv4.tcp_syncookies = 1          # SYN cookies when backlog full

# --- BBR congestion control ---
net.ipv4.tcp_congestion_control = bbr
net.core.default_qdisc = fq
EOF

# Apply:
sysctl -p /etc/sysctl.d/99-java-server.conf

# === Step 3: Per-process limits (ulimit) ===
# sysctl fs.file-max = system-wide max
# But each process has its own limit:
ulimit -n   # current process limit (default 1024!)
# 1024  <- way too low for a busy server

# Set per-process limit in /etc/security/limits.d/:
cat > /etc/security/limits.d/99-java-server.conf << 'EOF'
*       soft    nofile  65536
*       hard    nofile  1048576
root    soft    nofile  65536
root    hard    nofile  1048576
# Note: also set in systemd service if using systemd:
# [Service]
# LimitNOFILE=1048576
EOF

# For systemd services (ulimit ignored by systemd):
# systemctl edit my-app.service:
# [Service]
# LimitNOFILE=1048576
# LimitNPROC=65536
```

---

### Mental Model / Analogy

```
sysctl parameters = tuning knobs on a complex machine

Linux kernel = massive factory floor with 1000+ dials/knobs
sysctl = the control panel (adjust while running)
/etc/sysctl.d/*.conf = the "factory settings" loaded at startup

vm.swappiness = thermostat dial for memory:
  60 (default): "prefer to use RAM, but swap at moderate temperature"
  10: "only swap when RAM is really hot"
  0: "never touch the swap freezer"
  
  For databases and JVMs: turn it cold (1-10)
  Reason: GC pauses are terrible if part of heap is swapped out
  One GC pause that needs to page in 4GB of swapped heap = multi-second GC

vm.dirty_ratio = bathtub fill level:
  Water = dirty page data (writes not yet on disk)
  Faucet = application write rate
  Drain = writeback to disk
  
  dirty_background_ratio=3%: when 3% full, drain opens (background)
  dirty_ratio=10%: when 10% full, faucet is THROTTLED (app blocked)
  
  Default (20%): bathtub fills to 51GB before throttling!
  Big bathtub: applications write fast, then sudden big drain needed
  
  Production fix: small bathtub (5%/2%)
    Drain opens early, keeps level low
    Applications never get throttled (no latency spike)

fs.inotify.max_user_watches = how many store alarms:
  Each inotify watch = one motion detector in a store
  8192 watches = 8192 motion detectors
  VS Code + containerd + Filebeat can each need 2000-4000 watches
  Total needed: 8000+ but limit is 8192 -> "alarm system full, no more"
  Fix: increase to 524288 (524K detectors -> enough for all)

kernel.pid_max = how many employee badges:
  Default 32768: factory can have 32768 employees (processes)
  Container platform: 100 containers, each with 200 threads = 20K
  During spike (GC fork, build tools): PID 32769 requested -> DENIED
  "Resource temporarily unavailable" = no badges left!
  Fix: increase to 4194304 (4M badges)

net.core.somaxconn = waiting room size:
  TCP clients knock on door (SYN)
  3-way handshake completes -> client in "waiting room" (accept queue)
  App calls accept() -> client pulled from waiting room
  
  somaxconn = size of waiting room
  128 (old default) -> 128 clients max before others turned away
  32768 = much larger waiting room for busy servers
```

---

### Gradual Depth - Five Levels

**Level 1:**
`sysctl` command basics: read and write parameters. `/proc/sys/` filesystem.
Persistence via `/etc/sysctl.conf` or `/etc/sysctl.d/`. Common parameters:
`vm.swappiness`, `fs.file-max`, `net.core.somaxconn`. `sysctl -a` to list all.

**Level 2:**
vm namespace: dirty page policy (dirty_ratio, dirty_background_ratio),
overcommit modes, hugepages (nr_hugepages). fs namespace: file-max,
inotify limits, aio-max-nr. net namespace: TCP keepalive, syncookies,
tcp_tw_reuse, somaxconn. kernel namespace: pid_max, core_pattern, panic.

**Level 3:**
Relationship between `fs.file-max` (system-wide) vs ulimit/LimitNOFILE
(per-process). systemd service limits override ulimit. Dirty page writeback
mechanics: pdflush/kworker, dirty_expire_centisecs, dirty_writeback_centisecs.
vm.overcommit modes in depth (0: heuristic, 1: always, 2: strict with
vm.overcommit_ratio). THP (transparent hugepages) vs static hugepages.
`/proc/meminfo` fields that correspond to sysctl parameters.

**Level 4:**
Kernel sysctl implementation: `struct ctl_table`, `proc_handler` callbacks.
Security implications: `kernel.kptr_restrict` (hide kernel addresses),
`kernel.perf_event_paranoid`, `kernel.dmesg_restrict`. Network namespace
sysctl: parameters under `net.*` are namespace-scoped (each network namespace
can have different values). Container implications: containers share kernel
sysctl with host (except network namespace params). Seccomp profile interaction
with sysctl. `sysctl -n` vs `-w` atomicity. SystemTap and sysctl override
detection.

**Level 5:**
eBPF programs that can read/modify kernel behavior without sysctl (replacing
sysctl in modern systems for some use cases). `io_uring` and how it reduces
need for some sysctl tuning (fewer context switches). Kubernetes sysctl
support: `allowedUnsafeSysctls` in PodSecurityPolicy/SecurityContext. Safe
vs unsafe sysctls in Kubernetes (namespaced safe: `kernel.shm_rmid_forced`,
`net.ipv4.ip_local_port_range`; unsafe: `kernel.msgmax`, `vm.swappiness`).
`systemd-sysctl.service` vs `rc.local` vs `sysctl -p` loading order.
Parameters that interact: `vm.max_map_count` for Java NIO applications (too
low = "Cannot allocate memory" for mmap). `kernel.randomize_va_space` and
security vs performance.

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "sysctl -w changes are persistent" | `sysctl -w` changes are runtime-only and lost on reboot. To persist: write to a file under `/etc/sysctl.d/` (recommended, any file ending in `.conf`), then run `sysctl -p /etc/sysctl.d/yourfile.conf`. The file `/etc/sysctl.conf` is the legacy location but still works. On systemd systems: `systemd-sysctl.service` runs at boot and applies all `/etc/sysctl.d/*.conf` files. Do NOT add sysctl commands to `/etc/rc.local` as a crutch - use proper sysctl.d files for maintainability and idempotency. For containers: sysctl.d files apply to the host; Kubernetes pods can set their own sysctls via `securityContext.sysctls` for safe namespaced parameters. |
| "vm.swappiness=0 means no swapping" | `vm.swappiness=0` means the kernel tries very hard to avoid swapping anonymous memory, but will still swap if absolutely necessary to avoid OOM. It does NOT disable the swap device entirely. In kernels before 3.5: swappiness=0 could be fairly aggressive. In kernel 3.5+: swappiness=0 means "never swap unless critically out of memory." To completely disable swap at runtime: `swapoff -a`. For databases (PostgreSQL, MySQL) and JVMs: `vm.swappiness=1` is often recommended over `0` because with `0`, if the system does need to swap, it makes a sudden large swap decision rather than gradual small swaps - which can cause a longer freeze event. Databases typically say: "set swappiness to 1, not 0." |
| "Increasing fs.file-max is enough to raise file descriptor limits" | `fs.file-max` is the SYSTEM-WIDE limit. Each process has its own limit enforced via `ulimit -n` (soft/hard). The per-process limit is typically 1024 by default. Even if `fs.file-max=2097152`: a single process is still limited to 1024 open files. You must ALSO increase the per-process limit: `/etc/security/limits.d/*.conf` for PAM-based sessions, or `LimitNOFILE=` in systemd service units (systemd does NOT read /etc/security/limits.conf for services). For a containerized JVM: both the host fs.file-max AND the container's LimitNOFILE (set via ulimits in Docker or resources.limits in Kubernetes) must be configured. The three limits: system (fs.file-max), process (ulimit -n), and kernel default (fs.nr_open, max per-process FD count). |
| "Kernel sysctl parameters apply to all containers equally" | Sysctl parameters are partially namespaced in Linux. Network namespace params (`net.*`) are per-network-namespace: each container has its own net namespace and its own `net.ipv4.*` values. Setting `net.core.somaxconn` in a container only affects that container. However: vm.* and kernel.* parameters (with few exceptions) are GLOBAL to the host. Setting `vm.swappiness` on the host affects ALL containers. Setting `fs.file-max` on the host is global. Kubernetes distinguishes "safe" sysctls (namespaced, safe to set per-pod: net.ipv4.ip_local_port_range) from "unsafe" sysctls (require explicit allowance in kubelet config, affect the entire host: vm.max_map_count). A pod setting `vm.max_map_count=262144` changes it for the entire node. |

---

### Failure Modes & Diagnosis

**sysctl diagnostic playbook:**
```bash
# === Failure: "Error: Too many open files" ===
# Symptom: application fails with EMFILE or ENFILE

# EMFILE: per-process limit hit
# Check process's current limit:
cat /proc/<PID>/limits | grep "Open files"
# Max open files             1024    1024    files
#                            ^soft   ^hard -> both 1024, too low!

# Count current FDs for process:
ls /proc/<PID>/fd | wc -l
# 1023  <- almost at limit

# Fix per-process (session-based):
ulimit -n 65536   # current session only
# Permanent (PAM):
echo "* soft nofile 65536" >> /etc/security/limits.d/99-nofile.conf
echo "* hard nofile 1048576" >> /etc/security/limits.d/99-nofile.conf

# Fix for systemd services:
systemctl edit my-app.service
# [Service]
# LimitNOFILE=1048576

# ENFILE: system-wide limit hit
cat /proc/sys/fs/file-nr
# 65534 0 65536   <- used=65534, max=65536 -> system at limit!
sysctl -w fs.file-max=2097152

# === Failure: vm.dirty_ratio causing write stalls ===
# Symptom: periodic application hangs lasting seconds

# Check dirty page volume during incident:
watch -n1 "cat /proc/meminfo | grep -E 'Dirty|Writeback|MemFree'"
# Dirty:     52428800 kB   <- 50GB dirty! (with 256GB RAM, 20% = 51GB cap)
# Writeback: 10485760 kB   <- 10GB being written back (storm!)
# MemFree:   0 kB          <- RAM full

# Application is blocked on write():
cat /proc/<PID>/wchan
# balance_dirty_pages_ratelimited   <- blocked by dirty throttling!

# Fix:
sysctl -w vm.dirty_ratio=5
sysctl -w vm.dirty_background_ratio=2
# Now writeback starts at 2% RAM, application blocked only at 5% RAM

# === Failure: inotify limit hit ===
# Symptom: "ENOSPC" from inotify, or tools fail to watch files

# Diagnose:
dmesg | grep inotify
# inotify instance limit reached for uid 1000

sysctl fs.inotify.max_user_watches
# fs.inotify.max_user_watches = 8192

# Count current watches by process:
for pid in $(ls /proc | grep '^[0-9]'); do
    watches=$(cat /proc/$pid/fdinfo/* 2>/dev/null | \
              grep -c "inotify" || echo 0)
    if [ "$watches" -gt 100 ]; then
        echo "$pid ($(cat /proc/$pid/comm)): $watches watches"
    fi
done

# Fix:
sysctl -w fs.inotify.max_user_watches=524288
echo "fs.inotify.max_user_watches=524288" > \
    /etc/sysctl.d/99-inotify.conf

# === Failure: pid_max exhaustion ===
# Symptom: "Resource temporarily unavailable" on fork()
# dmesg shows: "fork: retry PID allocation"

cat /proc/sys/kernel/pid_max    # default 32768
# Count current PIDs:
ls /proc | grep '^[0-9]' | wc -l
# 32750  <- nearly exhausted!

sysctl -w kernel.pid_max=4194304
echo "kernel.pid_max=4194304" > /etc/sysctl.d/99-pid-max.conf
```

---

### Related Keywords

**Foundational:**
LNX-003 (Linux filesystem), LNX-035 (Memory management)

**Builds on this:**
LNX-084 (Network performance), LNX-093 (Performance troubleshooting), LNX-100 (Hardening)

**Related:**
LNX-083 (OOM killer), LNX-035 (Memory management)

---

### Quick Reference Card

| Parameter | Default | Tuning Direction | Why |
|-----------|---------|-----------------|-----|
| `vm.swappiness` | 60 | 1-10 for DB/JVM | Avoid swap for latency-sensitive |
| `vm.dirty_ratio` | 20 | 5-10 | Smaller burst writes, avoid stalls |
| `vm.dirty_background_ratio` | 10 | 2-3 | Earlier background writeback |
| `fs.file-max` | 65536 | 2097152 | High-connection services |
| `fs.inotify.max_user_watches` | 8192 | 524288 | Containers, IDEs |
| `kernel.pid_max` | 32768 | 4194304 | Container-heavy hosts |
| `net.core.somaxconn` | 4096 | 32768-65536 | High connection rate |

**3 things to remember:**
1. `sysctl -w` is runtime only; persist via `/etc/sysctl.d/*.conf` + `sysctl -p`
2. `fs.file-max` is system-wide; also set per-process via `ulimit -n` / `LimitNOFILE=` in systemd units - both are needed
3. `vm.dirty_ratio` (default 20%) on a 256GB RAM server means 51GB dirty pages before app blocking; reduce to 5% to prevent latency spikes

---

### Transferable Wisdom

The sysctl tuning principle - expose knobs for production tuning without
kernel recompilation - is the same as: Spring Boot's `application.properties`,
Java's `-XX:+UseG1GC -Xmx` JVM flags, Kubernetes resource requests/limits.
Configuration externalized from code, changeable at runtime. The dirty page
policy (batch writes, flush later) is the same trade-off as: Kafka producer
`acks=0` (fast writes, no durability), database write-ahead log (WAL),
Elasticsearch `index.refresh_interval=30s` (better indexing throughput, stale
reads). The `vm.overcommit_memory` parameter directly relates to Java heap
allocation: JVMs use `mmap` for large allocations, and with overcommit=0,
allocating 128GB heap on a 128GB server may fail even if only 4GB is used
(virtual address space committed). The inotify watch limit is a recurring
pain point in containerized environments: VS Code Dev Containers, GitHub
Codespaces, and Cloud9 IDEs all hit this limit and document `inotify.max_user_watches`
as a setup requirement. Kernel parameters are visible to eBPF programs via
`bpf_map_lookup_elem` and kernel probes - observability into parameter values
without reading /proc/sys.

---

### The Surprising Truth

The `vm.dirty_ratio` default of 20% was set in an era of spinning hard disks
and RAM measured in gigabytes. On a modern server with 256GB of RAM and NVMe
SSDs: 20% dirty ratio means the kernel will accumulate 51GB of dirty pages
before throttling applications. When this 51GB needs to be flushed: even
NVMe SSDs (capable of 7GB/s) need 7+ seconds to flush it. During that flush:
any application calling `write()` may be blocked for seconds. The solution
has been known since the early 2010s: reduce dirty_ratio to 5-10% on RAM-heavy
servers. Yet the kernel default remains 20% for backward compatibility with
old configurations. The practical impact: production incidents at major companies
that look like "the application froze for 10 seconds every few hours" are
frequently traceable to dirty page writeback storms on servers with large RAM.
MySQL, PostgreSQL, and Elasticsearch all have documentation noting this issue
and recommending reduced dirty ratios. A second surprise: `net.core.somaxconn`
was 128 for decades (since early Linux) and was only raised to 4096 in kernel
5.4 (2019). Many web applications that couldn't handle more than 128 simultaneous
connecting clients in the 2000s were limited by this kernel parameter, not their
application code.

---

### Mastery Checklist

- [ ] Can read and write sysctl parameters at runtime and make them persistent
- [ ] Understands vm.dirty_ratio/dirty_background_ratio and can tune them to prevent write stalls
- [ ] Knows the difference between fs.file-max (system-wide) and ulimit -n/LimitNOFILE (per-process)
- [ ] Can diagnose inotify limit, pid_max exhaustion, and dirty page stall symptoms
- [ ] Understands which sysctl parameters are network-namespace-scoped vs host-global

---

### Think About This

1. A monitoring agent (Datadog, Prometheus node_exporter, Filebeat) is installed
   on a Kubernetes node and starts creating 3000 inotify watches to monitor
   container log files. The default max_user_watches is 8192. With 50 pods on
   the node, each running an app that needs 100 watches, plus the host OS needing
   500 watches: calculate the total watches needed and determine if a limit problem
   will occur. Write the sysctl fix and explain why the Kubernetes pod's sysctl
   setting cannot fix this (it's an unsafe sysctl affecting the host).

2. A Java application server allocates a 200GB heap (`-Xmx200g`) on a server
   with 256GB RAM. After accounting for OS and other processes needing 40GB:
   only 16GB remains. With `vm.overcommit_memory=0` (heuristic mode): will
   Java's `mmap` for 200GB virtual address space succeed? What if you set
   `vm.overcommit_memory=1`? What if you set `vm.overcommit_memory=2` with
   `vm.overcommit_ratio=90`? Explain what each setting means for actual commit
   limit calculation.

3. A high-traffic web server is experiencing periodic 2-second latency spikes.
   `perf trace -e write` shows many processes in the `balance_dirty_pages_ratelimited`
   kernel function during spikes. The server has 512GB RAM with default dirty_ratio.
   Calculate: (a) how many GB of dirty pages trigger application blocking,
   (b) how long it takes NVMe (3GB/s write) to flush that volume, (c) the exact
   sysctl values to reduce this to a maximum 1-second writeback event.

---

### Interview Deep-Dive

**Foundational:**
Q: What is sysctl and how do you make kernel parameter changes persistent across reboots?
A: `sysctl` is both a system call and a userspace utility for reading and writing Linux kernel parameters at runtime. The kernel exposes these parameters as files under `/proc/sys/` - a virtual filesystem where each "file" corresponds to a kernel variable. HOW IT WORKS: Reading `/proc/sys/vm/swappiness` invokes the sysctl handler, reads the current value of the kernel variable `vm_swappiness`, and returns it as ASCII text. Writing invokes the handler, validates the value (type and range checking built into the handler), and updates the kernel variable immediately. RUNTIME CHANGE: `sysctl -w vm.swappiness=10` - takes effect immediately, lost on reboot. Equivalent: `echo 10 > /proc/sys/vm/swappiness`. PERSISTENT CHANGE: Create a file under `/etc/sysctl.d/` (any name ending in `.conf`): `echo "vm.swappiness=10" > /etc/sysctl.d/99-tuning.conf`. Apply immediately: `sysctl -p /etc/sysctl.d/99-tuning.conf`. On reboot: `systemd-sysctl.service` reads all files in `/etc/sysctl.d/` and applies them. IMPORTANT GOTCHA: `ulimit -n` (file descriptor limit per process) is NOT a sysctl parameter. It's controlled separately by `/etc/security/limits.d/` for PAM sessions and `LimitNOFILE=` in systemd service units. `fs.file-max` (sysctl) is the system-wide maximum; ulimit is per-process. Both must be configured for high-FD applications. NAMESPACE: `net.*` parameters are network-namespace scoped (containers can set their own). `vm.*` and `kernel.*` are mostly host-global.

**Expert:**
Q: Explain how vm.dirty_ratio and vm.dirty_background_ratio interact, why incorrect values cause latency spikes, and what values you'd set for a 256GB RAM database server.
A: Linux buffers file writes in the page cache. When an application calls `write()`: data is written to RAM (page cache), the page is marked "dirty" (pending disk flush), and the syscall returns immediately. Actual disk I/O happens asynchronously. TWO THRESHOLDS: `vm.dirty_background_ratio` (default 10%): when dirty pages exceed this % of total RAM, the kernel's writeback threads (kworker/flush threads) begin writing dirty pages to disk asynchronously. Application is NOT blocked. `vm.dirty_ratio` (default 20%): when dirty pages reach this % of RAM, EVERY application calling `write()` is throttled - forced to wait while writeback happens before their write can proceed. This is called `balance_dirty_pages_ratelimited`. LATENCY SPIKE MECHANISM: With 256GB RAM: dirty_background_ratio=10% = 25.6GB threshold. Background writeback starts at 25.6GB but can't keep up. dirty_ratio=20% = 51.2GB threshold. Application writes blocked at 51.2GB. Duration of blocking: 51.2GB / disk_write_speed. Even NVMe at 7GB/s = 7.3 seconds. Application appears "frozen" for 7+ seconds periodically. DATABASE SERVER RECOMMENDATION: `vm.dirty_ratio=5`: blocking threshold at 12.8GB. `vm.dirty_background_ratio=2`: background writeback starts at 5.1GB. With these values: writeback is always active (background always flushing), dirty page buildup is capped at ~12.8GB max, flush at 7GB/s = 1.8 seconds max blocking (if it hits the hard limit, unlikely with early background writeback). Additional parameters: `vm.dirty_expire_centisecs=500` (flush pages dirty more than 5s, prevents very old dirty data). `vm.dirty_writeback_centisecs=100` (writeback check interval: 1s). ALSO: Databases (MySQL, PostgreSQL) typically use `O_DIRECT` for data files (bypass page cache entirely), so dirty_ratio mainly affects WAL/redo log writes. For databases with O_DIRECT: focus on the log write behavior, not data file writes.
