---
layout: default
title: "ulimit"
parent: "Linux"
nav_order: 152
permalink: /linux/ulimit/
number: "0152"
category: Linux
difficulty: ★★★
depends_on: Process Management, Users and Groups
used_by: Linux Performance Tuning, Linux Security Hardening, Java & JVM Internals
related: /proc File System, Cgroups, Process Management
tags:
  - linux
  - os
  - performance
  - deep-dive
---

# 152 — ulimit

⚡ TL;DR — `ulimit` sets per-process resource limits enforced by the kernel — maximum open file descriptors, stack size, virtual memory, CPU time — preventing any single process from consuming resources that would destabilise the whole system.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A runaway process can open millions of file descriptors until the kernel runs out of file table entries — crashing every other process on the system that tries to open a file. A bug in a program creates an infinite loop writing to a file until the disk is full. A memory leak grows until the OOM killer fires and starts terminating random processes. Without per-process resource limits, a single misbehaving process is a denial-of-service attack on the whole machine.

**THE BREAKING POINT:**
A production web server starts leaking file descriptors under load. Within minutes, it exhausts the system's file descriptor limit. New connections fail with "too many open files". The process itself hits its limit first, but if configured incorrectly, it eventually exhausts the system-wide limit, breaking every other process on the machine.

**THE INVENTION MOMENT:**
This is exactly the problem ulimit solves. `ulimit -n 65536` limits this process to at most 65,536 open files. When it hits 65,536 it gets EMFILE errors — not the whole system. The blast radius is contained.

---

### 📘 Textbook Definition

`ulimit` is a shell built-in command that sets and displays resource limits for the current shell and any processes it spawns. These limits are enforced by the kernel via the `setrlimit()` / `getrlimit()` system calls. Each resource has two limits: the **soft limit** (current effective limit, can be raised up to the hard limit) and the **hard limit** (ceiling; only root can raise it). Limits are inherited by child processes. System-wide defaults are set in `/etc/security/limits.conf` (PAM) or `/etc/systemd/system/<service>.d/` for systemd services.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
ulimit prevents any single process from consuming so many resources that it destabilises the rest of the system.

**One analogy:**

> ulimit is the hotel's policy that each guest can have at most 3 room keys, order room service for at most $500/day, and stay no more than 30 days. These limits protect the hotel from any one guest monopolising its resources. A guest can always ask to raise their limit (soft → hard limit), but the hard limit is the absolute ceiling set by management (root only).

**One insight:**
The most commonly misconfigured limit in production Linux systems is `nofile` (maximum open file descriptors). The default of 1024 is far too low for web servers, databases, or any high-concurrency service. Most "too many open files" production incidents trace back to a forgotten ulimit configuration.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Every limit has a soft value (current) and a hard value (ceiling).
2. A process can raise its soft limit up to the hard limit.
3. Only root can raise the hard limit.
4. Limits are inherited — a child process starts with the same limits as its parent.
5. Setting `ulimit` in a shell only affects that shell and its children.

**DERIVED DESIGN:**
The kernel stores limits in the `rlimit` struct in the `task_struct` (process descriptor). `setrlimit(resource, &rlimit)` is the system call. When a process hits a limit, the kernel returns an error to the specific operation that would have exceeded it:

- File open exceeds `RLIMIT_NOFILE` → `EMFILE` ("too many open files")
- Memory exceeds `RLIMIT_AS` → `ENOMEM`
- CPU time exceeds `RLIMIT_CPU` → `SIGXCPU` signal

The distinction between soft and hard limits allows processes to be conservative by default but self-escalate for legitimate heavy workloads, without requiring root.

**THE TRADE-OFFS:**
**Gain:** Blast radius containment; predictable resource consumption; multi-tenant safety.
**Cost:** Incorrectly set limits cause mysterious failures; limits are inherited, so a misconfigured init system propagates bad limits to all services; limits don't account for shared resources (one process's 65K FDs vs another's 65K FDs both count against the system-wide limit).

---

### 🧪 Thought Experiment

**SETUP:**
A Java application server needs to handle 50,000 concurrent connections. Each connection requires a socket (one FD). The app also opens config files, libraries, log files — roughly 500 FDs of overhead. Total needed: ~50,500 FDs.

**WITHOUT correct ulimit:**
The JVM starts with the system default of 1024 open files. After 524 connections, the OS returns `EMFILE` to every `accept()` call. New connections fail with cryptic errors. The server runs at 1% capacity, appears to be "stuck", and restarts don't help.

**WITH correct ulimit:**

```bash
# In the systemd service file:
LimitNOFILE=65536

# OR before starting the JVM:
ulimit -n 65536
java -jar myserver.jar
```

Now the JVM can open 65,536 FDs — enough for 50K connections plus overhead.

**THE INSIGHT:**
Many production performance issues attributed to "the application is slow" or "the JVM is unstable" are actually resource limit misconfigurations. The symptom (failed connections, slow responses) masks the cause (EMFILE from a default 1024 FD limit).

---

### 🧠 Mental Model / Analogy

> ulimit is like a personal budget set by a company for each employee. Soft limit = current monthly budget (can request an increase up to the max). Hard limit = absolute maximum the company will ever authorise. The finance department (kernel) enforces it — even if you try to overspend, the card is declined (EMFILE/ENOMEM). Budgets are inherited: a new hire on a project inherits the project budget, not a blank slate.

- "Budget categories" → resource types (FDs, memory, CPU)
- "Monthly budget" → soft limit
- "Maximum authorised" → hard limit
- "Finance enforcement" → kernel enforcing at syscall level

Where this analogy breaks down: budgets can be shared between teams; ulimits are strictly per-process — two processes each with a 65K FD limit can both use their full allocation independently (subject to system-wide limits).

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
`ulimit` sets maximum resource quotas for processes — like a speed limiter on a car. Each process has limits on how many files it can open, how much memory it can use, how much CPU time it gets. These limits prevent one misbehaving program from crashing the whole server.

**Level 2 — How to use it (junior developer):**
`ulimit -a` shows all current limits. `ulimit -n` shows the current file descriptor limit. `ulimit -n 65536` increases it. `ulimit -Hn 65536` sets the hard limit. Soft vs hard: `ulimit -Sn` and `ulimit -Hn`. To make permanent: add to `/etc/security/limits.conf` or the systemd service file. Check a running process's limits: `cat /proc/PID/limits`.

**Level 3 — How it works (mid-level engineer):**
ulimits are stored in the kernel's `task_struct.signal->rlim[RLIMIT_*]` array. `getrlimit()`/`setrlimit()` are the corresponding syscalls. PAM reads `/etc/security/limits.conf` at login and calls `setrlimit()` before executing the user's shell. systemd reads `LimitNOFILE=` from service unit files and calls `setrlimit()` before `exec()`-ing the service binary. The JVM itself reads `/proc/self/limits` at startup to calculate the maximum number of threads it can create. Key limits: `RLIMIT_NOFILE` (open FDs), `RLIMIT_NPROC` (process count), `RLIMIT_AS` (virtual memory size), `RLIMIT_STACK` (stack size), `RLIMIT_CORE` (core dump size), `RLIMIT_CPU` (CPU seconds).

**Level 4 — Why it was designed this way (senior/staff):**
The soft/hard split was designed for multi-tenant environments (time-sharing UNIX systems) where users needed flexibility but administrators needed absolute guarantees. The inheritance model is a direct consequence of Linux's `fork()`/`exec()` model — limits are just another attribute in `task_struct` that gets copied on fork. The limitation of process-level limits is that they don't account for shared resources — 100 processes each with `RLIMIT_NOFILE=65536` can collectively open 6.5M FDs, which may exhaust the system-wide limit (`/proc/sys/fs/file-max`). This is why Kubernetes and modern container orchestrators use cgroups v2 for resource limits — cgroups operate on the process tree, not just individual processes.

---

### ⚙️ How It Works (Mechanism)

**ulimit shell built-in:**

```bash
# Show all current limits (soft)
ulimit -a

# Show all (separate soft/hard)
ulimit -aS  # soft
ulimit -aH  # hard

# Key individual limits:
ulimit -n      # nofile: max open file descriptors
ulimit -u      # nproc: max user processes
ulimit -s      # stack: stack size (KB)
ulimit -v      # virtual memory (KB)
ulimit -c      # core dump size (blocks); 0=disabled
ulimit -t      # CPU time (seconds)
ulimit -m      # max resident set size
ulimit -l      # max locked memory (for mlock)
ulimit -i      # pending signals

# Set limits (affects current shell + children)
ulimit -n 65536            # set soft nofile
ulimit -Hn 65536           # set hard nofile
ulimit -Sn 32768           # set soft only

# Enable core dumps
ulimit -c unlimited        # enable core dumps

# Check a running process's limits
cat /proc/$(pidof nginx)/limits
```

**Persistent limit configuration:**

`/etc/security/limits.conf` (PAM, for interactive logins):

```
# Format: domain  type  item  value
# domain: username, @group, *, or %
*        soft    nofile    65536
*        hard    nofile    65536
nginx    soft    nofile    200000
nginx    hard    nofile    200000
@admin   soft    nproc     unlimited

# For Java (needs large stack and many threads)
appuser  soft    stack     8192
appuser  hard    nproc     32768
```

`/etc/security/limits.d/99-production.conf` (preferred — drop-in):

```
# Applied after limits.conf, overrides it
*  -  nofile  65536      # - means both soft and hard
```

**systemd service unit limits:**

```ini
# /etc/systemd/system/myservice.service
[Service]
LimitNOFILE=65536
LimitNPROC=4096
LimitCORE=infinity      # enable core dumps
LimitMEMLOCK=infinity   # for memory-mapped workloads
LimitSTACK=8388608      # 8MB stack
```

**Checking and verifying:**

```bash
# Check system-wide file descriptor limit
cat /proc/sys/fs/file-max

# Check current system-wide FD usage
cat /proc/sys/fs/file-nr
# output: allocated  unused  max

# Check running service limits
systemctl show nginx | grep Limit

# Check process limits directly
cat /proc/$(pidof java)/limits

# Verify after changing limits.conf
# (requires new login/session to take effect)
sudo -u appuser ulimit -a
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
┌────────────────────────────────────────────────┐
│  "Too many open files" — diagnosing + fixing   │
└────────────────────────────────────────────────┘

 Error in app log: "java.io.IOException:
   Too many open files"
       │
       ▼
 Check current limits:
 cat /proc/$(pidof java)/limits | grep files
 → Max open files: 1024 / 1024 (soft/hard)
       │
       ▼
 Count actual open FDs:
 ls /proc/$(pidof java)/fd | wc -l
 → 1019 (approaching limit!)
       │
       ▼
 Confirm: lsof -p $(pidof java) | wc -l
 → 1021 (over limit — new opens failing)
       │
       ▼
 Short-term fix:
 prlimit --nofile=65536 --pid=$(pidof java)
 (change limit of running process - Linux 3.2+)
       │
       ▼
 Permanent fix: add to systemd unit file:
 LimitNOFILE=65536
 systemctl daemon-reload
 systemctl restart myservice
       │
       ▼
 Verify:
 cat /proc/$(pidof java)/limits | grep files
 → Max open files: 65536 / 65536
```

**FAILURE PATH:**
If setting `LimitNOFILE=1000000` in systemd unit but `/proc/sys/fs/file-max` is only 200000, the system-wide limit acts as a ceiling — the per-process limit is honoured but the machine can still run out of FDs. Always check `file-max` and `nr_open` (`/proc/sys/fs/nr_open`) before setting very high nofile limits.

---

### 💻 Code Example

**Example 1 — Pre-startup limit check script:**

```bash
#!/bin/bash
# Validate limits before starting production service
REQUIRED_NOFILE=65536
REQUIRED_NPROC=32768

CURRENT_NOFILE=$(ulimit -n)
CURRENT_NPROC=$(ulimit -u)

check_limit() {
  local name=$1 current=$2 required=$3
  if [ "$current" != "unlimited" ] && \
     [ "$current" -lt "$required" ]; then
    echo "ERROR: $name limit too low:" \
         "current=$current required=$required" >&2
    return 1
  fi
  echo "OK: $name=$current (required: $required)"
}

check_limit "nofile" "$CURRENT_NOFILE" "$REQUIRED_NOFILE" || exit 1
check_limit "nproc"  "$CURRENT_NPROC"  "$REQUIRED_NPROC"  || exit 1

# Check system-wide limit too
FILE_MAX=$(cat /proc/sys/fs/file-max)
if [ "$FILE_MAX" -lt "$REQUIRED_NOFILE" ]; then
  echo "ERROR: system file-max=$FILE_MAX < $REQUIRED_NOFILE" >&2
  exit 1
fi

echo "All limits OK. Starting service..."
exec "$@"
```

**Example 2 — Monitor FD usage (detect leaks):**

```bash
#!/bin/bash
# Alert when process exceeds 80% of FD limit
PID=${1:-$(pidof myservice)}
ALERT_THRESHOLD=80

while true; do
  FD_COUNT=$(ls /proc/$PID/fd 2>/dev/null | wc -l)
  FD_LIMIT=$(cat /proc/$PID/limits 2>/dev/null \
    | awk '/open files/{print $4}')

  if [ -n "$FD_LIMIT" ] && [ "$FD_LIMIT" != "unlimited" ]; then
    PCT=$(( FD_COUNT * 100 / FD_LIMIT ))
    if [ "$PCT" -gt "$ALERT_THRESHOLD" ]; then
      echo "ALERT: PID $PID using $PCT% FDs" \
           "($FD_COUNT/$FD_LIMIT)" | \
        logger -p daemon.warning
    fi
  fi
  sleep 30
done
```

**Example 3 — Change limits of a running process:**

```bash
# prlimit: change resource limits of a running process
# (requires Linux 3.2+, CAP_SYS_RESOURCE or root)

# Show current limits
prlimit --pid $(pidof nginx)

# Increase nofile for running nginx
prlimit --nofile=65536 \
  --pid $(pidof nginx)

# Set specific soft and hard limits
prlimit --nofile=32768:65536 \
  --pid $(pidof myapp)
# Format: soft:hard
```

---

### ⚖️ Comparison Table

| Mechanism           | Scope          | Persists                      | Shared Resources | Kubernetes |
| ------------------- | -------------- | ----------------------------- | ---------------- | ---------- |
| **ulimit / rlimit** | Per-process    | No (shell); Yes (PAM/systemd) | No               | No         |
| **cgroups v1/v2**   | Process tree   | Yes (systemd)                 | Yes (tree-wide)  | Yes        |
| **sysctl file-max** | System-wide    | Yes (/etc/sysctl.conf)        | Yes (all procs)  | Partial    |
| PAM limits.conf     | Per-user login | Yes                           | No               | No         |
| systemd LimitNOFILE | Per-service    | Yes (unit file)               | No               | No         |

How to choose: use ulimit/rlimit for per-process limits; use cgroups for container/pod resource limits; use sysctl for system-wide kernel parameters; prefer systemd `Limit*` directives for production services.

---

### ⚠️ Common Misconceptions

| Misconception                                                         | Reality                                                                                                                                                                         |
| --------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Setting ulimit -n in /etc/profile applies to all services             | PAM limits from `/etc/security/limits.conf` apply to interactive logins; systemd services do NOT inherit PAM limits — they must be set in the unit file                         |
| ulimit applies to all running processes immediately                   | ulimit in a shell affects only that shell and new processes spawned from it; existing processes keep their old limits (use prlimit to change a running process)                 |
| The hard limit is set by the OS and cannot be changed                 | Root can raise the hard limit; the system-wide maximum is `/proc/sys/fs/nr_open` (for nofile) which root can also raise                                                         |
| A service restarted with new limits will inherit them                 | Only true if the service was started by the process that has the new limits; a service started by systemd uses the unit file limits, not the operator's shell limits            |
| cgroups memory limits and ulimit virtual memory limits are equivalent | cgroups limit physical memory (RSS + swap); ulimit RLIMIT_AS limits virtual address space — a process can have 10GB of virtual address space (mmap'd files) with only 100MB RSS |

---

### 🚨 Failure Modes & Diagnosis

**"Too many open files" Despite Raising ulimit**

**Symptom:**
`EMFILE` errors persist in the application after `ulimit -n 65536` is set in the shell.

**Root Cause A:**
The service is managed by systemd and doesn't inherit the shell's limits. Systemd spawns services directly from the init process.

**Root Cause B:**
The soft limit was raised but the hard limit is still low.

**Diagnostic Command:**

```bash
# Check the RUNNING process's actual limits
cat /proc/$(pidof myservice)/limits | grep files
# If this still shows 1024, the shell ulimit had no effect

# Check systemd service limits
systemctl show myservice | grep LimitNOFILE
```

**Fix:**

```ini
# /etc/systemd/system/myservice.service
[Service]
LimitNOFILE=65536
```

Then: `systemctl daemon-reload && systemctl restart myservice`

---

**PAM limits.conf Changes Not Taking Effect**

**Symptom:**
Added `* soft nofile 65536` to `/etc/security/limits.conf` but `ulimit -n` still shows 1024 after login.

**Root Cause:**
PAM `pam_limits` module is not enabled in the service's PAM config, or the system uses a non-login shell that skips PAM.

**Diagnostic Command:**

```bash
# Check if pam_limits is active for SSH
grep pam_limits /etc/pam.d/sshd
grep pam_limits /etc/pam.d/common-session

# Check if limits.d drop-ins are loaded
cat /etc/security/limits.d/*.conf
```

**Fix:**
Ensure `/etc/pam.d/common-session` contains:

```
session required pam_limits.so
```

For non-login services, use systemd `LimitNOFILE` instead.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Process Management` — understanding processes, fork/exec, and process inheritance is required to understand why ulimits are inherited and why shell ulimit changes don't affect already-running services
- `Users and Groups` — PAM limits are applied per-user at login; understanding user/group identity is required for `/etc/security/limits.conf`

**Builds On This (learn these next):**

- `/proc File System` — `/proc/PID/limits` shows the current effective limits for any running process
- `Cgroups` — cgroups extend ulimit-style resource control to process trees (pods, containers), adding memory, CPU, and I/O limits
- `Linux Performance Tuning` — ulimit misconfiguration is a top cause of production performance incidents; proper limit configuration is fundamental to tuning

**Alternatives / Comparisons:**

- `cgroups` — hierarchical resource limits for process trees; more powerful than per-process rlimits; used by Docker and Kubernetes
- `systemd resource controls` — `MemoryLimit`, `CPUQuota`, etc. use cgroups under the hood; preferred over ulimit for system services

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Per-process kernel-enforced resource      │
│              │ limits with soft (current) and hard       │
│              │ (ceiling) values, inherited by children   │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ One runaway process could exhaust system  │
│ SOLVES       │ resources, crashing all other processes   │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ systemd services do NOT inherit PAM/shell │
│              │ limits — must set LimitNOFILE= in unit   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ High-concurrency services need >1024 FDs; │
│              │ configuring resource isolation per service│
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Container resource limits — use cgroups   │
│              │ (Kubernetes limits/requests) instead      │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Per-process isolation vs no accounting    │
│              │ for combined usage of many processes      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Personal budgets for each process —      │
│              │  the kernel declines overspending"        │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ cgroups v2 → systemd resources → seccomp │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A Kubernetes node has 200 pods, each configured with `LimitNOFILE=65536` in their systemd service or via container runtimes. The system-wide `/proc/sys/fs/file-max` is set to its default (roughly 800K on most systems). Describe the exact failure scenario that occurs when pods start approaching their limits simultaneously, calculate the theoretical maximum total FDs these 200 pods could open, compare it to the system-wide limit, and propose what Kubernetes operator configuration would prevent this from becoming a production incident.

**Q2.** A senior engineer tells you "don't set RLIMIT_AS (virtual memory) limits on Java applications". Explain the specific interaction between JVM memory management (heap, metaspace, off-heap, memory-mapped files, JIT code cache) and RLIMIT_AS that makes this advice correct, what happens when RLIMIT_AS is hit by a JVM, and why cgroups memory limits are a safer alternative for constraining JVM memory usage in containerised environments.
