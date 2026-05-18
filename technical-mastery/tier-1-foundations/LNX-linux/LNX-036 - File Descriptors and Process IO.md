---
id: LNX-036
title: "File Descriptors and Process I/O"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★☆
depends_on: LNX-007, LNX-013
used_by: LNX-046, LNX-062, LNX-082
related: LNX-062, LNX-082, OSY-021
tags: [file-descriptor, fd, stdin, stdout, stderr, lsof, ulimit, dup, io-redirection]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 36
permalink: /technical-mastery/lnx/file-descriptors/
---

## TL;DR

Every process has a file descriptor (FD) table: small integers mapping to
open kernel file objects. FD 0=stdin, 1=stdout, 2=stderr (fixed by POSIX).
Opening any file gets the lowest available FD. `lsof -p PID` shows all
open files. `ulimit -n` shows the per-process limit. "Too many open files"
error = FD limit exhausted (either hard limit too low or application FD
leak). Diagnose: `lsof -p PID | wc -l`. Fix: close unused FDs in code,
raise `ulimit -n`, or set `LimitNOFILE` in systemd service.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-036 |
| **Difficulty** | ★★☆ Intermediate |
| **Category** | Linux |
| **Tags** | file descriptor, FD, stdin, stdout, stderr, lsof, ulimit, dup2 |
| **Prerequisites** | LNX-007, LNX-013 |

---

### The Problem This Solves

Production Java application throws `java.io.IOException: Too many open files`
at 3 AM. The application is making database queries and HTTP calls. Without
understanding file descriptors, you'd restart the application and wait for
the problem to recur. With FD knowledge: `lsof -p PID | wc -l` shows
current FD count, `lsof -p PID | grep "can't identify"` shows leaked FDs,
`ulimit -n` shows the limit. The fix: either raise the OS limit or fix the
application code that's not closing connections.

---

### Textbook Definition

**File Descriptor (FD)**: A non-negative integer that serves as a process-local
handle to an open kernel file description. Returned by `open()`, `socket()`,
`pipe()`, and similar syscalls. Passed to `read()`, `write()`, `close()`,
and `ioctl()`. Everything in Linux that a process reads from or writes to
is accessed through file descriptors: regular files, directories, sockets,
pipes, devices, and special files.

**File Description**: A kernel-level object (different from FD) that stores
the file's current offset, flags, and a reference to the file's inode.
Multiple FDs (even in different processes) can refer to the same file
description (via `fork()` or `dup()`).

**Standard streams**: FD 0 (stdin), 1 (stdout), 2 (stderr) are opened by
the shell and inherited by child processes.

---

### Understand It in 30 Seconds

```bash
# Every process has: FD 0 (stdin), 1 (stdout), 2 (stderr)

# See a running process's FDs:
lsof -p $$           # $$ = current shell's PID
ls -la /proc/$$/fd/  # alternative: /proc/PID/fd/ directory

# Example output from lsof -p 1234:
# java  1234  user  0r  CHR  136,0  /dev/pts/0   <- FD 0: stdin (terminal)
# java  1234  user  1w  CHR  136,0  /dev/pts/0   <- FD 1: stdout (terminal)
# java  1234  user  2w  CHR  136,0  /dev/pts/0   <- FD 2: stderr (terminal)
# java  1234  user  5u  IPv4  TCP   localhost:8080->client:49321 <- socket
# java  1234  user  6r  REG  254,1  /opt/myapp/config.yaml      <- file
# java  1234  user  7u  REG  254,1  /tmp/myapp.lock             <- lock file

# Count total FDs for a process:
lsof -p 1234 | wc -l

# Current FD limit for current shell:
ulimit -n           # soft limit (default 1024 on many systems)
ulimit -Hn          # hard limit (usually 65536 or 1048576)

# Raise soft limit temporarily (can go up to hard limit):
ulimit -n 65536

# System-wide limits:
cat /proc/sys/fs/file-max    # max FDs system-wide

# FD leak diagnosis:
# Watch FD count grow for a running process:
watch -n 2 "lsof -p $(pgrep java) | wc -l"
# If count grows continuously: FD leak

# Find what types of FDs a process has open:
lsof -p 1234 | awk '{print $5}' | sort | uniq -c | sort -rn
# Output:
# 342 IPv4     <- sockets (TCP/UDP)
#  15 REG      <- regular files
#   3 CHR      <- character devices (terminal)
#   2 FIFO     <- pipes
```

---

### First Principles

**FD Table structure:**
```
Process (PID 1234) FD Table:
+-----+----------------+------------------------------+
| FD  | File Desc Ptr  | What it points to            |
+-----+----------------+------------------------------+
|  0  | -> fd_entry_A  | /dev/pts/0 (terminal stdin)  |
|  1  | -> fd_entry_A  | /dev/pts/0 (terminal stdout) |
|  2  | -> fd_entry_A  | /dev/pts/0 (terminal stderr) |
|  3  | -> fd_entry_B  | /etc/config.yaml (offset: 0) |
|  4  | -> fd_entry_C  | TCP socket: :8080<->:49321   |
|  5  | (empty)        |                              |
|  6  | -> fd_entry_D  | /tmp/lock.file (offset: 0)   |
+-----+----------------+------------------------------+

Kernel File Description (fd_entry_B):
  - reference count: 1
  - offset: 1024 (current read position in /etc/config.yaml)
  - flags: O_RDONLY
  - inode reference: -> inode for /etc/config.yaml
```

**Key behaviors:**
1. `fork()`: child inherits all parent FDs (same file descriptions -
   shared offset!). This is how stdout pipe works in a shell.
2. `exec()`: by default, all FDs survive exec (unless marked O_CLOEXEC).
   Your web server should set O_CLOEXEC on all FDs to prevent leaks
   to child processes (security best practice).
3. `dup()/dup2()`: creates a new FD pointing to the same file description.
   `dup2(4, 1)` redirects stdout (FD 1) to point to whatever FD 4 points to.
   This is how shell redirection is implemented.

---

### Thought Experiment

How does `echo "hello" > output.txt` work?

```bash
# Shell does this BEFORE exec'ing echo:
# 1. open("output.txt", O_WRONLY|O_CREAT|O_TRUNC) -> fd 5
# 2. dup2(5, 1)   <- make FD 1 (stdout) point to output.txt
# 3. close(5)     <- cleanup the extra FD
# 4. exec("echo", ["echo", "hello"])
# echo then writes to FD 1 (stdout), which now goes to output.txt

# Shell pipe: echo "hello" | grep "hello"
# Shell does:
# 1. pipe(fds) -> fds[0]=read end (fd 3), fds[1]=write end (fd 4)
# 2. fork() -> child1 (runs echo):
#    dup2(4, 1)   <- stdout -> pipe write end
#    close(3), close(4)
#    exec("echo", ...)
# 3. fork() -> child2 (runs grep):
#    dup2(3, 0)   <- stdin -> pipe read end
#    close(3), close(4)
#    exec("grep", ...)
# This is literally how all shell pipes work.
```

---

### Mental Model / Analogy

```
Process = office building
FD table = office's phone extension list (small numbers: 0, 1, 2, 3...)
Kernel file description = actual phone line (knows current state)

Extension 0 (FD 0): "Input line" (someone talking to us = stdin)
Extension 1 (FD 1): "Output line" (we talk out = stdout)
Extension 2 (FD 2): "Emergency line" (errors = stderr)
Extension 3+ : regular lines to files, databases, network

Opening a file = getting a new phone line (assigned next free extension)
Reading from FD = "listen to what's coming through this line"
Writing to FD = "send data through this line"
Closing FD = "hang up this line" (line becomes available for reuse)
FD leak = leaving lines open permanently (they are NEVER hung up)

ulimit -n = "maximum number of extensions in this office"
"Too many open files" = ran out of extension numbers
```

---

### Gradual Depth - Five Levels

**Level 1:**
FD 0=stdin, 1=stdout, 2=stderr. These are always open when your shell
runs. `lsof -p PID` shows all FDs for a process. "Too many open files"
means you've hit the limit. `ulimit -n` tells you what that limit is.

**Level 2:**
Files, sockets, pipes, and devices are all FDs. When you redirect
`>output.txt`, the shell opens the file, dup2's it to FD 1, then execs
the command. `/proc/PID/fd/` lists all open FDs as symlinks to their
targets. FD leak = opening files/sockets but never closing them.

**Level 3:**
`select()`, `poll()`, `epoll()` - event notification works by passing
FD sets to the kernel, which notifies when they're readable/writable.
High-performance servers like nginx use `epoll` to monitor thousands of
socket FDs efficiently. O_CLOEXEC flag: automatically closes FD on exec
(security: don't inherit sensitive FDs to child processes).

**Level 4:**
`sendfile(outfd, infd, ...)`: kernel-level zero-copy file transfer
(avoids user-space buffer). `splice(infd, ..., outfd, ...)`: kernel
pipe between FDs. These are how nginx/sendfile serves static files at
high performance. `inotify_init()` returns an FD that becomes readable
when watched files change (the basis of inotify file watching, used by
systemd, IDEs, and hot-reload servers).

**Level 5:**
`pidfd_open(PID)`: returns an FD representing a process (Linux 5.3+).
Can monitor process state without PID reuse races. `io_uring`: modern
async I/O interface using ring buffers mapped to user space via FDs.
Eliminates syscall overhead for high-throughput I/O. Used by high-
performance servers (io_uring > epoll for many workloads). FDs as a
capability model: in capability-based security, an FD is a capability.
`setns(fd, ...)`: an FD that represents a kernel namespace, allowing
a process to join that namespace.

---

### Code Example

**BAD - FD leak patterns:**
```bash
# BAD 1: Not closing FDs in scripts
while true; do
    cat /proc/cpuinfo > /tmp/cpu.txt
    # /tmp/cpu.txt is opened and closed (cat handles this)
    # But if we use file descriptors directly:
    exec 3< /etc/hosts    # opens FD 3 for reading /etc/hosts
    # ... read some lines ...
    # Forgot to close FD 3!
    # Next iteration: FD 4 opened, then FD 5... FD leak in a loop!
done

# GOOD: always close explicitly opened FDs:
exec 3< /etc/hosts    # open
while IFS= read -r -u3 line; do
    echo "$line"
done
exec 3<&-             # close FD 3 (done with it)
```

**BAD - Java/application FD leak:**
```java
// BAD: opens connection, exception bypasses close()
public void readConfig() throws IOException {
    FileInputStream fis = new FileInputStream("/etc/app.conf");
    // ... if exception thrown here, fis is never closed
    String content = new String(fis.readAllBytes());
    fis.close();  // not reached if exception above!
}

// GOOD: try-with-resources guarantees close():
public void readConfig() throws IOException {
    try (FileInputStream fis = new FileInputStream("/etc/app.conf")) {
        String content = new String(fis.readAllBytes());
        // fis.close() called automatically even on exception
    }
}
```

**Production FD diagnosis:**
```bash
# Application throwing "Too many open files":

# Step 1: Find the PID
PID=$(pgrep -f "myapp.jar")

# Step 2: Check current FD count
echo "Current FD count:"
ls /proc/$PID/fd | wc -l

# Step 3: Check the limit
echo "Soft limit: $(cat /proc/$PID/limits | grep 'open files' | awk '{print $4}')"
echo "Hard limit: $(cat /proc/$PID/limits | grep 'open files' | awk '{print $5}')"

# Step 4: What types of FDs are being leaked?
lsof -p $PID | awk '{print $5}' | sort | uniq -c | sort -rn | head -20

# Step 5: Are sockets the issue? Check connection states:
lsof -p $PID | grep IPv4 | awk '{print $10}' | sort | uniq -c | sort -rn
# High CLOSE_WAIT count = server not closing connections (FD leak in code)
# High TIME_WAIT = normal (OS holding connections briefly after close)

# Raise the limit without restart (for systemd services):
# Edit /etc/systemd/system/myapp.service:
# [Service]
# LimitNOFILE=65536
# Then: systemctl daemon-reload && systemctl restart myapp

# System-wide default for all processes (edit /etc/security/limits.conf):
# * soft nofile 65536
# * hard nofile 65536
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "Files are the only things that are FDs" | FDs represent: regular files, directories, sockets (TCP/UDP), pipes (pipe()), FIFOs (named pipes), character devices (/dev/null, terminals), block devices, inotify instances, timerfd, eventfd, signalfd, pidfd, epoll instances. Essentially EVERYTHING in Linux I/O is an FD. |
| "Closing a file always releases disk space" | Closing an FD removes the file description reference, but the inode (and data) is only freed when ALL hard links to it are removed AND all FDs referencing it are closed. Classic: `rm logfile.log` while the app still has it open - the file appears deleted (`ls` doesn't show it), but disk space isn't freed until the process closes its FD. Use `lsof | grep deleted` to find such files. |
| "ulimit -n 65536 affects all processes" | `ulimit -n` in a shell only affects that shell and its children started AFTER the change. systemd services have their own limits (`LimitNOFILE=` in service file). To set defaults for new login sessions: `/etc/security/limits.conf`. Changes don't apply to already-running processes. |
| "stdin/stdout/stderr must be terminals" | FD 0/1/2 can be anything: a file (when redirected), a pipe (when piped), a socket (for network daemons), or a device (/dev/null). When a daemon starts: it typically closes 0/1/2 and reopens them to /dev/null to detach from the terminal. |
| "fork() doubles the FD count" | fork() creates a new process with a COPY of the parent's FD table. Each FD in the child points to the SAME kernel file descriptions as the parent. The file description reference count increases. If both parent and child have FD 5 open (same underlying file/socket), that's 2 references, not 2 separate file objects. If either process closes FD 5, the other still has access via its FD 5. |

---

### Failure Modes & Diagnosis

**"deleted" file still consuming disk space:**
```bash
# Application log was deleted but disk is still full
df -h /var/log    # shows 99% usage despite empty directory

# Find files open but "deleted":
lsof | grep deleted
# java  1234  ...  /var/log/myapp/app.log (deleted)

# Fix Option 1: truncate the file while it's open (preserves FD):
> /proc/1234/fd/7   # truncate via proc fd symlink (if you know the FD)

# Fix Option 2: restart the application (closes FD, space freed)
systemctl restart myapp

# Fix Option 3: tell the app to reopen log files (if supported):
kill -USR1 1234    # many apps handle SIGUSR1 as "reopen logs"
# Logrotate uses this: rotate file, signal app to reopen
```

---

### Related Keywords

**Foundational:**
LNX-007 (FHS), LNX-013 (Processes)

**Builds on this:**
LNX-062 (Memory Management), LNX-082 (System Call Interface)

**Related:**
OSY-021 (File I/O), LNX-046 (Inodes, VFS)

---

### Quick Reference Card

| Command | Purpose |
|---------|---------|
| `lsof -p PID` | All FDs for process |
| `ls /proc/PID/fd/` | Same via /proc |
| `lsof -p PID \| wc -l` | FD count |
| `lsof \| grep deleted` | Files open but "deleted" |
| `ulimit -n` | Current FD soft limit |
| `ulimit -Hn` | Current FD hard limit |
| `ulimit -n 65536` | Raise FD limit (this shell) |
| `cat /proc/PID/limits` | Process limits |
| `lsof -i :8080` | What's using port 8080 |

**3 things to remember:**
1. FD 0=stdin, 1=stdout, 2=stderr - these are inherited from parent (shell)
2. Disk space isn't freed on `rm` if a process still has the file open - use `lsof | grep deleted`
3. "Too many open files" = `lsof -p PID | wc -l` vs `ulimit -n` to diagnose

---

### Transferable Wisdom

File descriptors are the universal I/O abstraction in Unix/Linux.
Understanding FDs explains: how shell pipes work (pipe + dup2 + fork + exec),
how socket programming works (socket() returns an FD, then read/write),
how `epoll` works (FDs as event sources), how container isolation works
(network namespaces separate socket FDs), how `strace` works (traces all
FD-related syscalls: open, read, write, close, socket, connect).

The "everything is a file" Unix philosophy is the FD model: `inotify_init()`
returns an FD you read events from, `timerfd_create()` returns an FD that
becomes readable when a timer fires, `signalfd()` turns signals into readable
events on an FD. These are unified in epoll: one event loop, multiple FD types.

---

### The Surprising Truth

When you run `nohup myapp &`, the shell doesn't just ignore SIGHUP - it
also redirects FD 0 (stdin) to `/dev/null` and FD 1 (stdout) to
`nohup.out` so the process doesn't fail trying to read/write a closed
terminal. But the REAL reason processes die when you close a terminal isn't
SIGHUP alone - it's that when the terminal closes, any process writing to
the closed FD 1 gets SIGPIPE (broken pipe signal). nohup handles SIGHUP
but NOT SIGPIPE to a closed stdout - which is why `nohup` PLUS redirecting
stdout is the correct pattern. The number of FDs a system can have open
simultaneously is tracked in `/proc/sys/fs/file-nr` - you can watch it
in real time during a load test to see if your system is approaching limits.

---

### Mastery Checklist

- [ ] Can explain what FD 0, 1, and 2 represent
- [ ] Can use lsof -p PID to inspect process file descriptors
- [ ] Can diagnose "Too many open files" errors
- [ ] Can explain how shell redirections use dup2()
- [ ] Can find files that are open but "deleted" and still consuming disk space

---

### Think About This

1. After `java myapp &`, the Java process is running in the background.
   You close the terminal (logout). The Java process's FD 1 (stdout) was
   pointing to the terminal PTY. What happens when the Java process next
   tries to write to stdout? What signal does it receive, and what is the
   default action of that signal?

2. A Java server has been running for days. `df` shows disk is 99% full.
   `ls /var/log/myapp/` shows all log files are small (logrotate deleted
   the old ones). But `du -sh /var/log/` matches `df`. Where is the disk
   usage hiding, and what command would you use to find it?

3. `ulimit -n 65536` in your bash script doesn't seem to take effect
   for your Java service (running via systemd). You've set it in
   `/etc/security/limits.conf`. The service still reports FD limit of 1024.
   Why? Where is the correct place to set the FD limit for systemd services?

---

### Interview Deep-Dive

**Foundational:**
Q: What is a file descriptor and what are file descriptors 0, 1, and 2?
A: A file descriptor (FD) is a non-negative integer that serves as a process's handle to an open file, socket, pipe, or other I/O resource in the kernel. Think of it as an index into the process's table of open "connections" to the OS. FD 0 = stdin (standard input) - default: terminal keyboard. FD 1 = stdout (standard output) - default: terminal screen. FD 2 = stderr (standard error) - default: terminal screen. These three are POSIX standard and are opened for every process before main() runs. Everything the process reads from or writes to goes through FD numbers: when you open a database connection, the OS returns an FD (say, 5). When you write to it: `write(5, data, length)`. When done: `close(5)`. Shell redirection (> file, | pipe, 2>&1) all work by reassigning these FD numbers before exec'ing the child process.

**Intermediate:**
Q: How do you diagnose and fix "Too many open files" in a Java production service?
A: Diagnosis steps: (1) Confirm the error: look in application logs for "Too many open files" or catch IOException with EMFILE errno. (2) Find the PID: `pgrep -f myapp.jar`. (3) Get current FD count: `ls /proc/PID/fd | wc -l`. (4) Get the limit: `cat /proc/PID/limits | grep 'open files'`. If count approaches limit, confirmed. (5) Identify what's leaking: `lsof -p PID | awk '{print $5}' | sort | uniq -c | sort -rn`. High IPv4 count = socket leak. High REG count = file handle leak. (6) Socket leak details: `lsof -p PID | grep IPv4 | awk '{print $10}' | sort | uniq -c` - high CLOSE_WAIT = server-side not closing connections. (7) Fix the limit (short-term): edit `/etc/systemd/system/myapp.service`, add `LimitNOFILE=65536` under [Service], then `systemctl daemon-reload && systemctl restart myapp`. (8) Fix the leak (long-term): ensure all resources use try-with-resources in Java. Audit JDBC connection pooling (pool not returning connections). Audit HTTP client (not closing response bodies). Add FD count monitoring: alert when FD count > 80% of limit.

**Expert:**
Q: Explain how an epoll-based event loop (like Node.js or nginx's worker) uses file descriptors to handle thousands of concurrent connections efficiently.
A: `epoll` is the Linux kernel's scalable I/O event notification mechanism. The setup: (1) `epoll_create1(0)` returns an epoll FD (the "event poll" instance). (2) For each incoming connection: `accept()` returns a socket FD. `epoll_ctl(epfd, EPOLL_CTL_ADD, sockfd, &event)` registers the socket FD with epoll. (3) Event loop: `n = epoll_wait(epfd, events, MAX_EVENTS, timeout)`. This BLOCKS until at least one registered FD is ready for I/O. Returns up to MAX_EVENTS ready FD events. (4) Process only ready FDs - never wasteful polling. Why this scales: `select()` and `poll()` (older alternatives) require passing ALL watched FDs to the kernel every call. With 10,000 connections, each call copies 10,000 FDs. O(n) per call. `epoll_wait()` only returns READY FDs. Registrations are maintained in the kernel's red-black tree. The kernel notifies epoll of I/O events via callbacks in the socket's wait queue. O(1) per event regardless of total connections. Edge-triggered vs level-triggered: level-triggered (default): epoll_wait returns while FD remains readable (keeps returning until you drain the buffer). Edge-triggered (EPOLLET): only notifies on STATE CHANGE (from not-ready to ready). More efficient but requires reading until EAGAIN to avoid starvation. nginx uses edge-triggered epoll. This is why nginx/Node.js can handle 50,000+ concurrent connections on a single thread with modest CPU: they never block on I/O, and epoll's O(1) complexity ensures they efficiently find which FDs need attention.
