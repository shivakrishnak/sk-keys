---
id: OSY-043
title: "strace (System Call Tracer)"
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★☆
depends_on: OSY-008, OSY-021
used_by: OSY-079
related: OSY-008, OSY-044, OSY-079
tags:
  - strace
  - tool
  - system-calls
  - tracing
  - debugging
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 43
permalink: /technical-mastery/osy/strace/
---

## TL;DR

`strace` intercepts and records every system call made
by a process. It answers: what files is it opening?
what network connections? why is it slow? why is it
hanging? No code changes required. Essential for
diagnosing black-box processes and unexpected I/O.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-043 |
| **Difficulty** | ★★☆ Working |
| **Category** | Operating Systems |
| **Tags** | strace, system call tracer, diagnosis, tool |
| **Prerequisites** | OSY-008, OSY-021 |

---

### How strace Works

```
strace uses ptrace() syscall to intercept every syscall:
  1. Attach to target process (or start new one)
  2. OS notifies strace before+after each syscall
  3. strace reads syscall args and return values
  4. Logs to stderr in human-readable format
  
Mechanism:
  ptrace(PTRACE_ATTACH, pid) -> OS sends SIGSTOP to target
  ptrace(PTRACE_SYSCALL, pid) -> resume until next syscall
  ptrace(PTRACE_GETREGS, pid) -> read syscall args from registers
  
Performance overhead:
  Every syscall: ~5-10x slower than normal (ptrace intercept)
  Summary mode (-c): less overhead, only counts
  
Note: strace should NOT run continuously in production
  Use for targeted diagnosis sessions only
```

---

### Essential strace Commands

```bash
# Trace a new program from start
strace ls /tmp
# Each line: syscall(args) = return_value

# Attach to running process (by PID)
strace -p $(pgrep java)
# -p: attach to existing process

# Follow child processes (fork/exec)
strace -f java MyApp
# -f: follow children; each line prefixed with PID

# Count syscall frequency (summary mode)
strace -c -p PID
# Run for 30s then Ctrl+C:
# Shows: % time, count, errors per syscall type
# Minimal performance overhead in -c mode

# Filter to specific syscall types
strace -e trace=file java MyApp      # file I/O only
strace -e trace=network java MyApp  # network only
strace -e trace=write,read java ... # read/write only
strace -e trace=open,close java ... # file opens only

# Show timestamps (absolute or relative)
strace -t java MyApp    # absolute time HH:MM:SS
strace -r java MyApp    # relative time since last syscall
strace -T java MyApp    # time spent IN each syscall (blocking time)

# Write output to file (strace output goes to stderr by default)
strace -o /tmp/trace.txt -p PID
```

---

### Reading strace Output

```
# Raw strace output:
openat(AT_FDCWD, "/etc/config.properties", O_RDONLY) = 3
fstat(3, {st_mode=S_IFREG|0644, st_size=1024, ...}) = 0
mmap(NULL, 1024, PROT_READ, MAP_SHARED, fd=3, 0) = 0x7f12345
read(3, "app.port=8080\napp.env=prod\n", 26) = 26
close(3) = 0

# Reading each element:
# openat(dir, path, flags) = fd
#   fd=3: file opened as descriptor 3
# fstat(3, {size=1024}) = 0
#   getting file metadata
# read(3, "content...", count) = bytes_read
#   26 bytes read
# close(3) = 0
#   file descriptor 3 released

# Common return values:
# 0  = success (for most non-data syscalls)
# -1 = error (check: ENOENT=file not found, EACCES=permission denied)
# -1 ENOENT (No such file or directory)
#   -> file path wrong, file deleted, typo in config

# Blocking syscall (strace -T shows duration):
futex(0x7f..., FUTEX_WAIT, 0, NULL) = -1 EAGAIN (Resource temporarily unavailable)
# or:
nanosleep({tv_sec=1, tv_nsec=0}, NULL) = 0  <1.001s>
#                                            ^ time spent = 1 second blocked
```

---

### Practical Diagnosis Patterns

```bash
# PATTERN 1: Why is the app slow at startup?
strace -T -e trace=file java MyApp 2>&1 | head -100
# Look for: many openat() calls with large <duration>
# Long file open = file not in page cache (cold start)

# PATTERN 2: What files is this process opening?
strace -e trace=openat -p PID 2>&1 | grep -v ENOENT
# Filter out "file not found" to see what it finds
# Find unexpected log files, temp files, config paths

# PATTERN 3: Why is the process hanging?
strace -p PID
# See what syscall it's stuck in:
# futex(...) = blocked on a lock (possible deadlock)
# read(fd, ...) = blocked waiting for I/O
# nanosleep = in a sleep loop
# epoll_wait = waiting for events (normal for servers)

# PATTERN 4: Network connections
strace -e trace=network -p PID
# See: connect() calls, socket(), bind(), accept()
# Useful: see what host:port app is connecting to
# strace: connect(3, {sa_family=AF_INET, sin_port=5432 (postgres)...})

# PATTERN 5: Count which syscalls are expensive
strace -c -T -p PID  # run for 60s
# Summary shows: write() at 80% of CPU time?
# -> per-item writes, add buffering
# futex at 60%?
# -> high lock contention, profile locks
```

---

### Java-Specific strace Patterns

```bash
# JVM startup trace (first 100 syscalls at startup)
strace -f -e trace=openat java -jar app.jar 2>&1 | head -200
# See: JVM opens many jar/class files at startup
# Normal: 100-500 file opens during warmup

# Thread creation (how many threads does JVM create?)
strace -f -e trace=clone java -jar app.jar 2>&1 | grep clone | wc -l
# clone() is the Linux thread creation syscall

# Check if JVM is swapping (page faults generating I/O)
strace -e trace=mmap,mprotect -p $(pgrep java) 2>&1 | head -20
# mmap: JVM requesting more virtual memory
# Lots of mmap with MAP_ANON: allocating heap/metaspace

# Thread dump trigger - trace the signal
# (NOT using strace, but related)
kill -3 $(pgrep java)  # triggers SIGQUIT -> JVM thread dump to stderr
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "strace is for debugging application logic bugs" | strace shows OS-level syscalls, not application logic. It reveals: what files are being opened, what network connections are made, what OS operations are slow. Application logic bugs (NullPointerException, wrong algorithm) are not visible in strace |
| "strace is too slow to use in production" | `strace -c -p PID` (summary mode) has minimal overhead and can run briefly in production for diagnosis. Avoid full trace mode (`strace -p PID` without `-c`) in production - it adds 5-10x syscall overhead |

---

### Quick Reference Card

| Command | Purpose |
|---------|---------|
| `strace -c java App` | Syscall frequency summary (lowest overhead) |
| `strace -T -p PID` | Time per syscall (find slow syscalls) |
| `strace -f -p PID` | Trace all threads |
| `strace -e trace=file -p PID` | File operations only |
| `strace -e trace=network -p PID` | Network operations only |
| `strace -o trace.txt -p PID` | Write output to file |
| `strace -p PID` | Attach to running process |
