---
layout: default
title: "lsof"
parent: "Linux"
nav_order: 151
permalink: /linux/lsof/
number: "0151"
category: Linux
difficulty: ★★☆
depends_on: /proc File System, Process Management
used_by: Observability & SRE, strace / ltrace, Linux Security Hardening
related: strace / ltrace, /proc File System, Linux Networking (ip, ss, netstat)
tags:
  - linux
  - os
  - debugging
  - intermediate
---

# 151 — lsof

⚡ TL;DR — `lsof` (list open files) shows every file, socket, pipe, and device that every process has open — because in Linux, everything is a file, lsof reveals the complete resource map of a running system.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
"Cannot delete this file — it's in use." By what? Which process? You'd have to stop everything, one service at a time, checking if the file becomes deleteable. Or "Port 8080 is already in use" — which process owns it? `ps aux` shows all processes but not their open files or sockets. Without a tool that maps files to processes, answering "what has this file open?" requires rebooting or guesswork.

**THE BREAKING POINT:**
A disk is filling up. You delete large log files but the disk space doesn't free up. The files no longer appear in `ls` but the disk is still full. This is impossible without understanding Linux file semantics: a deleted file's data remains on disk until all file descriptors pointing to it are closed. Without `lsof`, you can't identify which process still has the deleted file open.

**THE INVENTION MOMENT:**
`lsof +L1` lists all files with a link count less than 1 — deleted files still held open by processes. One command reveals which process has the 50GB deleted log file open. Kill or restart that process → 50GB freed instantly. This specific use case has saved countless engineers from unnecessary disk replacements.

---

### 📘 Textbook Definition

`lsof` (LiSt Open Files) is a diagnostic tool that reads kernel data structures (via `/proc`) to enumerate all open file descriptors across all processes. Because Linux implements "everything is a file" — regular files, directories, sockets (TCP/UDP), pipes, device nodes, shared memory segments, and pseudo-files are all represented as file descriptors — `lsof` provides a unified view of all resources any process has open. It can filter by process, user, file, port, or network connection.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
`lsof` shows every open file and socket for every process — the complete resource inventory of a live Linux system.

**One analogy:**

> `lsof` is a hotel's key card audit log. Every room key (file descriptor) issued to every guest (process) is tracked. You can ask: "Which guest has the master key to room 404?" (which process has `/var/log/app.log` open), "How many rooms does guest 1234 have keys to?" (all FDs for PID 1234), or "Is anyone still in room 303 that was supposed to be checked out?" (deleted file still open).

**One insight:**
In Linux, deleting a file removes its directory entry (the name), not the data. The data persists until the last open file descriptor pointing to it is closed. `lsof +L1` exploits this to find deleted files still consuming disk space — one of the most valuable and surprising uses of lsof.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Every open resource in Linux is a file descriptor pointing to a kernel object.
2. File descriptors are per-process but can refer to shared kernel objects.
3. Deleting a file removes its directory entry; the inode and data blocks persist until link count reaches 0 AND all FDs are closed.
4. `lsof` reads `/proc/PID/fd/`, `/proc/PID/fdinfo/`, `/proc/net/`, and kernel symbol tables to build its picture.

**DERIVED DESIGN:**
For each process, `/proc/PID/fd/` contains a symlink for each open file descriptor, pointing to the actual resource (file path, socket, pipe, device). `lsof` reads these symlinks and `/proc/PID/fdinfo/` for access mode (read/write) and file offset. For sockets, it correlates the inode number in `/proc/PID/fd/` with entries in `/proc/net/tcp`, `/proc/net/udp`, and `/proc/net/unix` to get the address/port information.

**THE TRADE-OFFS:**
**Gain:** Complete cross-process resource inventory; file-to-process mapping; deleted-file detection; network socket inspection.
**Cost:** `lsof` can be slow on systems with many processes (iterates /proc for each); requires root for other users' processes; output can be extremely verbose without filters.

---

### 🧪 Thought Experiment

**SETUP:**
A CI/CD pipeline fails with "no space left on device" during a build. `df -h` shows 100% usage. `du -sh /*` shows only 40GB used but the filesystem is 50GB. Where is the 10GB?

**WITHOUT lsof:**
The 10GB discrepancy is invisible. Files exist in the kernel's view but not in the directory hierarchy. You can't find them with `find`, `du`, or any other file-based tool. The build environment might be left in this state for hours until the daily restart frees the space.

**WITH lsof:**

```bash
# Find all deleted files still open (link count < 1)
lsof +L1 | grep deleted
```

Output:

```
java  1234 build  txt REG  8,1 10737418240 0 /tmp/build_cache (deleted)
```

The Java build tool created a 10GB temp file, then deleted it (to hide it), but kept it open. As long as the JVM runs, that space is consumed. Solution: kill PID 1234 (or wait for build to finish).

**THE INSIGHT:**
"Deleted files still open" is one of the most common causes of mysterious disk space discrepancies in production. Understanding that deletion in Linux is "unlink" (remove name) not "free" (release data) is fundamental, and `lsof +L1` is the tool that exposes it.

---

### 🧠 Mental Model / Analogy

> Think of lsof as the library's borrowing system. Every book (file/socket) currently checked out is in the system. You can query: "Who has book X?" (which process has file open), "What does person Y have checked out?" (all FDs for PID), "Are there books marked for disposal that someone still has?" (deleted files still open).

- "Books" → files, sockets, pipes
- "Checked out" → open file descriptor
- "Marked for disposal but still out" → deleted file with open FD
- "Borrowing system" → lsof reading /proc metadata

Where this analogy breaks down: books in a library have only one copy; Linux file descriptors can have multiple processes holding the same inode open simultaneously, each with independent offset and access mode.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
`lsof` answers "who has what open?" on a Linux system. Every program that has a file open, a network connection active, or a pipe connected appears in lsof's output. It's the inventory checker for everything a running system is currently touching.

**Level 2 — How to use it (junior developer):**
`lsof -p 1234` lists all open files for PID 1234. `lsof /path/to/file` lists processes that have that specific file open. `lsof -i :8080` lists processes using port 8080. `lsof -i TCP` lists all TCP sockets. `lsof -u username` lists all files opened by a user. `lsof +L1` finds deleted files still held open. Combine: `lsof -p $(pidof nginx) -i TCP` shows nginx's TCP connections.

**Level 3 — How it works (mid-level engineer):**
`lsof` iterates `/proc/*/fd/` reading symlinks for each process. It maintains internal tables to avoid re-reading kernel data. For network sockets, the `/proc/PID/fd/N` symlink shows `socket:[inode]`; lsof then searches `/proc/net/tcp`, `/proc/net/tcp6`, `/proc/net/udp`, `/proc/net/unix` for a matching inode to get address and port information. File link count (needed for `+L1`) comes from `stat()` on the file. The `-F` flag produces machine-readable output suitable for scripts. `-r N` makes lsof repeat every N seconds — a poor man's continuous monitor.

**Level 4 — Why it was designed this way (senior/staff):**
`lsof` predates Linux; it was originally written for UNIX systems before `/proc` existed and used `kvm` (kernel virtual memory) access — reading directly from kernel address space, which required knowing exact kernel struct offsets. The Linux port shifted to `/proc`, making it portable across kernel versions. The "everything is a file" design philosophy in Linux is what makes `lsof` so powerful: the same tool that shows regular files also shows sockets, because they're both file descriptors with the same kernel abstraction. This is why `lsof -i TCP` works the same way as `lsof /etc/passwd` — they're both asking "what processes have this file descriptor type open?".

---

### ⚙️ How It Works (Mechanism)

**Essential lsof commands:**

```bash
# All open files (can be very long)
lsof

# Open files for a specific process
lsof -p 1234
lsof -p $(pidof nginx)  # by name

# Files opened by a specific user
lsof -u www-data

# All files opened by root except PID 1
lsof -u root ^-p 1  # ^ excludes PID 1

# Who has a specific file open?
lsof /var/log/app.log
lsof /var/run/app.sock

# What process is using a port?
lsof -i :8080          # any protocol
lsof -i TCP:8080       # TCP only
lsof -i UDP:53         # UDP DNS

# All network connections
lsof -i                # all sockets
lsof -i TCP            # TCP sockets
lsof -i TCP -s TCP:LISTEN  # listening only
lsof -i TCP -s TCP:ESTABLISHED  # active connections

# Deleted files still open (disk space mystery)
lsof +L1               # link count < 1 = deleted

# Files in a directory (and subdirectories)
lsof +D /var/log/      # recursive
lsof +d /var/log/      # non-recursive

# Network sockets for a process
lsof -p $(pidof java) -i

# Continuous monitoring (refresh every 5s)
lsof -r 5 -p $(pidof myapp)

# Machine-readable output for scripting
lsof -F pcn -p 1234
# p=pid, c=command, n=name/address
```

**Understanding lsof output columns:**

```
COMMAND  PID   USER   FD      TYPE  DEVICE SIZE/OFF   NODE NAME
nginx   1234  www    4u      IPv4  12345      0t0    TCP *:80 (LISTEN)
│       │     │      │       │     │          │      │   │   └── state
│       │     │      │       │     │          │      │   └── address:port
│       │     │      │       │     │          │      └── inode
│       │     │      │       │     │          └── file offset
│       │     │      │       │     └── device
│       │     │      │       └── type: REG, DIR, IPv4, IPv6, FIFO, CHR
│       │     │      └── file descriptor + mode: r=read, w=write, u=rdwr
│       │     └── user
│       └── PID
└── command name

FD types: cwd (current working dir), txt (program text), mem (mmap'd)
  0r (stdin/read), 1w (stdout/write), 2w (stderr/write), Xu (file X open r/w)
```

**Common script patterns:**

```bash
# Kill the process holding a port
kill $(lsof -t -i :8080)
# -t: output only PID

# Find process using a specific file
lsof -t /var/log/app.log | xargs kill -HUP
# (useful for logrotate: SIGHUP to reopen log)

# Count open files per process (top 10)
lsof | awk 'NR>1 {count[$2]++}
  END {for (pid in count) print count[pid], pid}' \
  | sort -rn | head -10

# Check if any process has a deleted file open
DELETED=$(lsof +L1 2>/dev/null | grep deleted)
if [ -n "$DELETED" ]; then
  echo "WARNING: deleted files held open:"
  echo "$DELETED" | awk '{print $1, $2, $9, $10}'
fi
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
┌────────────────────────────────────────────────┐
│  DISK FULL: "No space left on device"          │
│  but du shows only 80% usage                  │
└────────────────────────────────────────────────┘

 df -h /          → 100% full (50GB FS, 50GB used)
       │
       ▼
 du -sh /*        → only 40GB in directory tree
       │  10GB unaccounted! Not in any directory
       ▼
 lsof +L1
       │  Lists: java 2345 app 12u REG (deleted) 10GB
       │         /tmp/big_cache (deleted)
       ▼
 File was deleted from /tmp (name removed)
 but java PID 2345 still has fd 12 open
 10GB data still on disk (inode not freed)
       │
       ▼
 kill -15 2345    OR wait for app to close fd
       │
       ▼
 Kernel frees inode + data blocks → 10GB recovered
 df -h → 80% used
```

**FAILURE PATH:**
If lsof shows no deleted files but space still missing, check for directories that are bind-mounted over (`mount | grep bind`) — the underlying filesystem is being counted by df but the contents are hidden by the mount overlay.

---

### 💻 Code Example

**Example 1 — Port conflict resolver:**

```bash
#!/bin/bash
# Find and optionally kill process on a port
PORT=${1:-8080}

echo "Processes using port $PORT:"
PIDS=$(lsof -ti TCP:$PORT -s TCP:LISTEN)

if [ -z "$PIDS" ]; then
  echo "No process found on port $PORT"
  exit 0
fi

lsof -i TCP:$PORT -s TCP:LISTEN -n -P
echo ""
echo "PIDs: $PIDS"

read -p "Kill these processes? [y/N] " answer
if [ "$answer" = "y" ]; then
  echo "$PIDS" | xargs kill -15
  echo "Sent SIGTERM to PIDs: $PIDS"
fi
```

**Example 2 — Open file limit checker:**

```bash
#!/bin/bash
# Check if any process is approaching its FD limit
echo "PID | Command | Open FDs | Limit | % Used"
echo "----+----------+----------+-------+--------"

for pid in /proc/[0-9]*/fd; do
  pid_num=$(echo "$pid" | grep -oP '\d+')
  [ -d "$pid" ] || continue

  fd_count=$(ls "$pid" 2>/dev/null | wc -l)
  limit=$(cat "/proc/$pid_num/limits" 2>/dev/null \
    | grep "open files" | awk '{print $4}')
  cmd=$(cat "/proc/$pid_num/comm" 2>/dev/null)

  [ -z "$limit" ] || [ "$limit" = "unlimited" ] && continue

  if [ "$fd_count" -gt $(( limit * 80 / 100 )) ]; then
    pct=$(( fd_count * 100 / limit ))
    echo "$pid_num | $cmd | $fd_count | $limit | $pct%"
  fi
done 2>/dev/null | sort -t'|' -k5 -rn | head -20
```

**Example 3 — Network connection audit:**

```bash
#!/bin/bash
# Show all external TCP connections with process info
echo "Active external TCP connections:"
lsof -i TCP -s TCP:ESTABLISHED -n -P 2>/dev/null \
  | grep -v '127.0.0.1\|::1\|localhost' \
  | awk 'NR==1 || /ESTABLISHED/'
```

---

### ⚖️ Comparison Table

| Tool         | Scope                | Network Sockets | Deleted Files | Speed    |
| ------------ | -------------------- | --------------- | ------------- | -------- |
| **lsof**     | All process FDs      | Yes             | Yes (+L1)     | Moderate |
| ss           | Sockets only         | Yes             | No            | Fast     |
| netstat      | Sockets + interfaces | Yes             | No            | Slow     |
| fuser        | Specific file/port   | Partial         | No            | Fast     |
| /proc/PID/fd | Single process       | Yes             | Indirect      | Fast     |
| find /proc   | All processes        | Indirect        | No            | Slow     |

How to choose: use `lsof` for cross-process investigation (who has a file/port open); use `ss` for faster socket-only queries; use `fuser` for quick "who has this file open" without lsof overhead.

---

### ⚠️ Common Misconceptions

| Misconception                                | Reality                                                                                                                                    |
| -------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| Deleting a file frees disk space immediately | Deletion removes the directory entry; disk space is freed only when all FDs referencing the inode are closed — use lsof +L1 to find these  |
| lsof -i shows all network activity           | lsof -i shows open sockets; accepted connections on a listening socket each have their own FD — a busy server will show many rows per port |
| lsof output is always accurate               | lsof reads /proc at a point in time; the process landscape changes between reads; lsof output can be stale for rapidly changing processes  |
| You need root to use lsof                    | You can run lsof for your own processes; root is needed to see other users' processes                                                      |
| lsof can show what network data was sent     | lsof shows sockets are open and what state they're in; to see packet content, use tcpdump                                                  |

---

### 🚨 Failure Modes & Diagnosis

**lsof Shows No Process on a Known-Active Port**

**Symptom:**
`ss -tlnp | grep 8080` shows port 8080 is LISTEN but `lsof -i :8080` shows nothing.

**Root Cause:**
lsof is running without root privileges and the process belongs to a different user; or the process is in a container with a separate network namespace.

**Diagnostic Command:**

```bash
# Run with root
sudo lsof -i :8080

# If in container, check host-side network namespaces
ss -tlnp | grep 8080  # shows process ID even without root
# Then: ls -la /proc/<PID>/ns/net to check namespace
```

**Fix:**
Run lsof as root; or use `ss -tlnp` which shows PID without namespace traversal.

---

**`lsof +L1` Shows Empty Output Despite Missing Disk Space**

**Symptom:**
Disk is 100% full; `du` shows 20% less than df; but `lsof +L1` shows nothing.

**Root Cause:**
The missing space is in a different filesystem context — could be a bind mount hiding content, a loopback device, or a snapshot consuming space outside the visible mount point.

**Diagnostic Command:**

```bash
# Check for bind mounts hiding space
findmnt --verify
mount | grep bind

# Check for snapshots (btrfs/lvm)
lvs  # LVM thin pool usage
btrfs filesystem df /mount/point
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `/proc File System` — lsof reads `/proc/PID/fd/` and `/proc/net/` to build its output; understanding procfs explains lsof's capabilities and limitations
- `Process Management` — understanding PIDs, file descriptors, and process lifecycle is required to interpret lsof output

**Builds On This (learn these next):**

- `strace / ltrace` — strace shows each syscall as it happens; lsof shows the accumulated result (what's currently open)
- `Linux Networking (ip, ss, netstat)` — ss provides faster socket-specific queries; lsof provides cross-process file+socket queries
- `Linux Security Hardening` — lsof is used in security audits to identify unexpected open ports and connections

**Alternatives / Comparisons:**

- `fuser` — simpler tool for "who has this specific file or port open"; faster than lsof for single-resource queries
- `ss` — faster socket-only tool using netlink API; preferred over `lsof -i` for pure network queries
- `/proc/PID/fd/` — direct access to open FDs for one process; faster than lsof for single-process inspection

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Tool that lists all open file descriptors │
│              │ (files, sockets, pipes) per process       │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ "Something has this file/port open" —     │
│ SOLVES       │ no unified way to find it without lsof    │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ lsof +L1 finds deleted files still        │
│              │ consuming disk space (link count = 0)     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ "Disk full but du disagrees"; "port in    │
│              │ use — by what?"; post-incident auditing   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Only need socket info — use ss instead    │
│              │ (much faster, uses netlink not /proc)     │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Complete resource inventory vs moderate   │
│              │ speed (iterates all /proc/PID/fd entries) │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The hotel key-card system — shows every  │
│              │  resource currently checked out"          │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ fuser → strace → /proc/PID/fd           │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A long-running Java application creates a new log file every hour and rotates the old ones by deleting them with `File.delete()`. After 48 hours of running, `df` shows the filesystem is 90% full but `du` on the log directory shows only 5%. Without restarting the JVM, describe the exact sequence of steps you would use to: (1) confirm deleted files are the cause, (2) identify the exact FD count and sizes, and (3) resolve the issue without killing the process (hint: some filesystems allow truncating a deleted file via its FD).

**Q2.** In a microservices environment, Service A reports it can't connect to Service B on port 8080 even though Service B "is running". Design a systematic investigation using `lsof`, `ss`, and `ip` that would diagnose each of the following distinct failure scenarios without using any application-level tools: (a) Service B is running but not listening on the expected interface, (b) a zombie process is occupying the port, (c) Service B is in a different network namespace (container).
