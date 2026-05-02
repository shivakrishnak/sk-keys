---
layout: default
title: "File Descriptor"
parent: "Operating Systems"
nav_order: 108
permalink: /operating-systems/file-descriptor/
number: "0108"
category: Operating Systems
difficulty: ★★☆
depends_on: Process, System Call (syscall), Virtual Memory
used_by: epoll / kqueue, Blocking I/O, Non-Blocking I/O, Linux Namespaces
related: inode, File Handle, open(), read(), write()
tags:
  - os
  - fundamentals
  - linux
  - internals
---

# 108 — File Descriptor

⚡ TL;DR — A file descriptor (fd) is an integer index into a per-process table of open resources; every I/O operation in Unix happens through one, whether it's a file, socket, pipe, or device.

| #0108           | Category: Operating Systems                                      | Difficulty: ★★☆ |
| :-------------- | :--------------------------------------------------------------- | :-------------- |
| **Depends on:** | Process, System Call (syscall), Virtual Memory                   |                 |
| **Used by:**    | epoll / kqueue, Blocking I/O, Non-Blocking I/O, Linux Namespaces |                 |
| **Related:**    | inode, File Handle, open(), read(), write()                      |                 |

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
Every early OS required programs to pass file names or physical addresses to I/O functions. File names are long strings that require path resolution on every I/O call. Physical addresses require programs to know hardware layout. Concurrent operations on the same file from the same program require coordinating shared state everywhere.

THE BREAKING POINT:
Unix's design goal was that "everything is a file" — regular files, directories, devices, sockets, pipes, and terminals should all use the same read/write interface. But you can't use a pathname as a stable handle: the file could be renamed mid-operation. You can't use physical addresses: they break portability and expose hardware.

THE INVENTION MOMENT:
The solution was to give each process a small integer per open resource. The integer is an opaque handle — it means nothing to user code except "this is my resource." The OS maintains a table mapping integers to open file descriptions. This gave Unix the uniform I/O interface that made "everything is a file" possible.

### 📘 Textbook Definition

A **file descriptor** (fd) is a non-negative integer assigned by the OS to a process when it opens (or creates) a file, socket, pipe, device, or other I/O resource. It serves as an abstract handle: the process passes the fd to system calls (`read`, `write`, `close`, `epoll_ctl`, `sendmsg`, etc.) and the kernel resolves it to the actual OS resource. Each process has its own **file descriptor table** (indexed by fd number) pointing to shared **open file descriptions** (tracking position, flags) which in turn point to **inodes** (actual filesystem entries). Standard streams have fixed fds: 0=stdin, 1=stdout, 2=stderr.

### ⏱️ Understand It in 30 Seconds

**One line:**
A file descriptor is a process-scoped integer that stands for any open I/O resource — the OS resolves it to the real object.

**One analogy:**

> A file descriptor is a cloakroom ticket. You hand your coat (the file) to the cloakroom (OS), receive a number (fd). When you want it back, you show the number. The number is small and easy to carry, but meaningless to anyone else. Two people can receive ticket #5 — each ticket refers to their own coat.

**One insight:**
The level of indirection (process fd table → open file description → inode) allows two critical behaviours: `dup2(fd, 2)` redirects stderr to a file by replacing entry #2 in the fd table, while a `fork()` child shares the parent's open file descriptions through separate fd tables — the file position is shared, but the fd number is independent.

### 🔩 First Principles Explanation

CORE INVARIANTS:

1. An fd is process-scoped and non-negative; 0, 1, 2 are always stdin/stdout/stderr.
2. `open()` always returns the lowest available fd number.
3. Closing an fd releases the slot — subsequent opens may reuse the number.
4. Forked children inherit copies of the parent's fd table (same open file descriptions).

DERIVED DESIGN:
The three-level indirection (fd → open file description → inode) is deliberate:

- **Level 1 (fd table):** Small, per-process, holds flags like `FD_CLOEXEC` (close on exec). Cheap to copy at `fork()`.
- **Level 2 (open file description / struct file):** Per `open()` call, holds file offset, access mode (O_RDONLY/O_WRONLY), non-blocking flag. Shared between duplicated fds and across `fork()`.
- **Level 3 (inode / vnode):** Per filesystem object. Holds size, permissions, data blocks. Shared by all opens of the same file.

This layering means: after `fork()`, parent and child share the same file offset (read by one advances position for the other), which was essential for shell I/O redirection before pipes were invented.

THE TRADE-OFFS:
Gain: Uniform interface for all I/O resources; cheap integer-based reference; composable with all syscalls; epoll/select/poll all work on fds enabling heterogeneous wait sets.
Cost: Finite per-process limit (`ulimit -n`, default 1024 or 65536); fd leaks cause `EMFILE` errors; fds inherited across `exec()` unless `FD_CLOEXEC` set (security risk).

### 🧪 Thought Experiment

SETUP:
A web server forks a child for each request.

WHAT HAPPENS:

```
Parent:
  fd 0 = stdin
  fd 1 = stdout
  fd 2 = stderr
  fd 3 = listening socket
  fd 4 = log file
  fork()

Child (before exec):
  fd 0 = stdin (shared OFD with parent)
  fd 1 = stdout
  fd 2 = stderr
  fd 3 = listening socket (SHOULD BE CLOSED in child)
  fd 4 = log file

  Unless O_CLOEXEC / FD_CLOEXEC set, fd 3 and fd 4
  survive exec() in the child → fd leak
```

THE INSIGHT:
Every `open()` in a library you call, every socket the framework opens, every temporary file — if not marked `O_CLOEXEC`, it leaks into child processes via `exec()`. This is both a resource leak and a security vulnerability (child inherits your database socket).

### 🧠 Mental Model / Analogy

> The three-level fd system is like a building directory:
>
> - Your badge number (fd): unique per person, small, easy to say
> - Directory entry (open file description): translates your badge to your current office location and access level
> - Office (inode): the actual room with the furniture

If you copy your badge (`dup2`), both badges lead to the same office. If the directory entry is "temporary contractor" (file opened with specific position), you and your copy share the same position in the room. If you leave the building and re-join (`close`/`open`), you might get the same badge number but it now points to a different office.

Where the analogy breaks down: in the real fd model, `dup2(fd, 2)` doesn't copy — it atomically replaces what badge #2 means. This is the mechanism that makes shell `2>&1` redirection work.

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
When you open a file in any program, the OS gives you a small number (like 4 or 7) as a token. You use that number for all subsequent reads and writes. It's like a claim ticket at a coat check.

**Level 2 — How to use it (junior developer):**
In Java, `FileInputStream`, `Socket`, and `ServerSocket` all hold fds internally; `close()` releases them. Always close resources in `finally` or use try-with-resources. Use `lsof -p <PID>` to see all fds open in a process. Hard limit is `ulimit -n`; raise it in `/etc/security/limits.conf` for high-connection servers. In Linux, fds are visible in `/proc/<PID>/fd/`.

**Level 3 — How it works (mid-level engineer):**
In the kernel, `open()` calls `do_sys_open()` which allocates a `struct file` (open file description), links it to the inode, and installs it in `current->files->fdt->fd[n]` where n is the lowest free slot. `read(fd, buf, len)` calls `vfs_read()` on `fdt->fd[n]`, which dispatches to the filesystem's `read_iter`. `dup2(oldfd, newfd)` atomically installs `fdt->fd[oldfd]` at `fdt->fd[newfd]` (incrementing refcount). `fork()` calls `dup_fd()` which copies the fd table but increments refcounts on open file descriptions — parent and child share the same `struct file` objects. Closing either doesn't affect the other's access until refcount reaches zero.

**Level 4 — Why it was designed this way (senior/staff):**
The per-process fd table design reflects Unix's process isolation model: each process has its own address space view of its resources, even when they share underlying objects. The `dup2` mechanism was essential to implementing shell I/O redirection without modifying programs: `dup2(file_fd, STDOUT_FILENO)` makes fd 1 point to the file, then any program that writes to stdout (fd 1) writes to the file — zero program changes needed. This composability is the core Unix philosophy: programs don't need to know about redirection. The `FD_CLOEXEC` flag was added later (as a retrofix) because the original design leaked fds into exec'd children — modern code always uses `O_CLOEXEC` in `open()` flags to set this atomically.

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│              FILE DESCRIPTOR LAYERS                    │
├────────────────────────────────────────────────────────┤
│  Process A fd table          Process B fd table        │
│  ┌────────────────┐          ┌────────────────┐        │
│  │ 0 → OFD(stdin) │          │ 0 → OFD(stdin) │        │
│  │ 1 → OFD(stdout)│          │ 1 → OFD(stdout)│        │
│  │ 2 → OFD(stderr)│          │ 2 → OFD(stderr)│        │
│  │ 3 → OFD(file)──┼────────→ inode: /var/log  │        │
│  │ 4 → OFD(sock)  │          │ 3 → OFD(file)──┼──────┐ │
│  └────────────────┘          └────────────────┘      │ │
│          │                                            │ │
│          ↓                                            ↓ │
│    Open File Descriptions (struct file)               │ │
│    [OFD: pos=0, flags=O_RDONLY] ──→ inode(/etc/hosts) │ │
│    [OFD: pos=1024, flags=O_WRONLY] ──────────────────┘ │
└────────────────────────────────────────────────────────┘
```

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW (open/read/close):

```
User: open("/etc/hosts", O_RDONLY)
  → VFS: path lookup → inode lookup
  → Allocate struct file (OFD): pos=0, flags=O_RDONLY, inode ref
  → Install in fd table at lowest free slot: fd 3
  → Return 3 to user

User: read(3, buf, 4096)
  → Kernel: fdt->fd[3] → struct file → inode → filesystem
  → Copy 4096 bytes from page cache to buf
  → Advance struct file pos by 4096

User: close(3)
  → Decrement struct file refcount
  → If refcount == 0: release struct file
  → Remove slot 3 from fd table
```

FAILURE PATH (fd exhaustion):

```
open() returns EMFILE: process has too many fds open
open() returns ENFILE: system-wide limit reached
Fix: raise ulimit -n; audit for fd leaks; ensure close() in finally
```

### 💻 Code Example

Example 1 — fd leak with exec (security issue):

```c
// DANGEROUS: fd 3 inherits into child process
int db_sock = socket(AF_INET, SOCK_STREAM, 0);
connect(db_sock, &server_addr, sizeof(server_addr));
// ... later ...
execve("/bin/user_program", args, envp);
// user_program now has fd 3 = your database socket!

// SAFE: O_CLOEXEC closes on exec automatically
int db_sock = socket(AF_INET, SOCK_STREAM | SOCK_CLOEXEC, 0);
// Or: fcntl(db_sock, F_SETFD, FD_CLOEXEC);
```

Example 2 — shell-style stdout redirection using dup2:

```c
// Redirect stdout to a file (classic shell redirection: program > file.txt)
int fd = open("output.txt", O_WRONLY|O_CREAT|O_TRUNC|O_CLOEXEC, 0644);
if (fd < 0) { perror("open"); exit(1); }

// Make fd 1 (stdout) point to the file
dup2(fd, STDOUT_FILENO);  // atomic: replaces fd[1]
close(fd);  // original fd no longer needed

// Now any write(1, ...) or printf goes to output.txt
printf("This goes to the file\n");
```

Example 3 — Java try-with-resources (correct fd management):

```java
// BAD: fd leaks if exception thrown after open
FileInputStream fis = new FileInputStream("/etc/hosts");
// ... might throw exception before close() ...
fis.close();

// GOOD: try-with-resources guarantees close()
try (FileInputStream fis = new FileInputStream("/etc/hosts");
     FileOutputStream fos = new FileOutputStream("/tmp/out")) {
    byte[] buf = new byte[4096];
    int n;
    while ((n = fis.read(buf)) != -1) {
        fos.write(buf, 0, n);
    }
}  // both fds closed here even if exception thrown
```

Example 4 — Inspecting fds in production:

```bash
# List all open fds for a process
ls -la /proc/<PID>/fd/

# Detailed: what each fd is
lsof -p <PID>

# Count open fds (watch for leaks)
ls /proc/<PID>/fd | wc -l

# Show current fd limits
cat /proc/<PID>/limits | grep "open files"

# System-wide fd count
cat /proc/sys/fs/file-nr
# [allocated fds] [free (kernel reuse)] [max]
```

### ⚖️ Comparison Table

| Concept               | Scope           | Shared after fork?       | Shared after dup?      |
| --------------------- | --------------- | ------------------------ | ---------------------- |
| File descriptor (fd)  | Per process     | No (separate tables)     | No (separate slots)    |
| Open File Description | Per open() call | Yes (shared struct file) | Yes (same struct file) |
| Inode                 | Filesystem      | Yes (same inode)         | Yes (same inode)       |
| File position         | Per OFD         | Yes (shared after fork)  | Yes (shared after dup) |

### ⚠️ Common Misconceptions

| Misconception                                  | Reality                                                                                                                 |
| ---------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| "Each open() of the same file shares position" | Only if fds share the same Open File Description; independent open() calls get separate OFDs with independent positions |
| "close() in parent closes fd in child"         | No — fork() copies fd tables; close() in parent only decrements OFD refcount; child's fd is independent                 |
| "dup2 copies the file descriptor value"        | dup2(3, 5) does NOT make fd 5 = 3 numerically; it makes fd slot 5 point to the same OFD as fd slot 3                    |
| "fd 0/1/2 are always the terminal"             | Only if not redirected; shell redirection replaces them before exec                                                     |
| "Closing one dup'd fd closes all"              | No — each dup'd fd is independent; the underlying OFD is freed only when all duplicates are closed (refcount → 0)       |

### 🚨 Failure Modes & Diagnosis

**1. EMFILE — Too Many Open File Descriptors**

Symptom: Application fails with `java.io.IOException: Too many open files` or C `open()` returns `EMFILE`.

Root Cause: Process has reached its fd limit; usually a fd leak (resource not closed in error path).

Diagnostic:

```bash
# Check current limit vs usage
cat /proc/<PID>/limits | grep "open files"
ls /proc/<PID>/fd | wc -l
lsof -p <PID> | sort -k 9 | uniq -c | sort -rn | head
# Find what type of fd is leaking (sockets, files, pipes)
```

Fix: Add try-with-resources; trace all `open()`/`socket()` to matching `close()`.

Prevention: Instrument code to track fd count in tests. Set `ulimit -n 1048576` for servers that genuinely need many fds.

---

**2. Use-After-Close (fd Reuse Bug)**

Symptom: Writing to a socket corrupts a file (or vice versa); data goes to wrong destination.

Root Cause: Code closes an fd, then uses the old integer believing it's still valid. OS reassigned that integer to a new resource.

Diagnostic:

```bash
strace -e trace=open,close,read,write,socket -p <PID> 2>&1 | grep "fd N"
# Watch for close(N) followed by read(N)/write(N)
```

Fix: Set fd variable to -1 after closing. Check fd before use.

Prevention: Never store raw fd integers in long-lived data structures without lifecycle management.

---

**3. FD Leak Across exec (Security Issue)**

Symptom: Child process inherits sensitive fd (database socket, private key file handle).

Root Cause: `open()` or `socket()` called without `O_CLOEXEC`/`SOCK_CLOEXEC`; fd survives `execve()`.

Diagnostic:

```bash
# After exec, check inherited fds in new process
ls -la /proc/<PID>/fd/
# Compare with expected fds (stdin/stdout/stderr only)
```

Fix: Always use `O_CLOEXEC` on every `open()` and `SOCK_CLOEXEC` on every `socket()`.

Prevention: Audit with `lsof -p <exec'd PID>` in tests. Add `fcntl(fd, F_SETFD, FD_CLOEXEC)` as a belt-and-suspenders measure.

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Process` — each process has its own fd table; fds are per-process
- `System Call (syscall)` — all fd operations (open, read, write, close) are syscalls
- `Virtual Memory` — fd table lives in kernel's per-process memory structures

**Builds On This (learn these next):**

- `epoll / kqueue / io_uring` — register fds to be notified when they are ready for I/O
- `Non-Blocking I/O` — set O_NONBLOCK flag on an fd to make it non-blocking
- `Linux Namespaces` — fd table is per-process/namespace; understanding for container isolation

**Alternatives / Comparisons:**

- `Windows HANDLE` — Windows analog; typed handles rather than int indices
- `Java FileDescriptor` — thin wrapper exposing the OS fd in Java
- `POSIX FILE*` — stdio buffered layer on top of raw fds (fileno() gives the underlying fd)

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Non-negative integer per-process index    │
│              │ into a table of open OS resources         │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Programs need a stable handle to open     │
│ SOLVES       │ resources independent of name/location    │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ 3-level indirection: fd → OFD → inode     │
│              │ enables fork/dup semantics and sharing    │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Any I/O operation on any Unix resource    │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Never avoid — it's the fundamental Unix   │
│              │ I/O abstraction; everything uses fds      │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Uniform interface and composability vs    │
│              │ finite per-process limit and leak risk    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "A small integer is your OS-managed       │
│              │  claim ticket for any open resource"      │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ epoll → Non-Blocking I/O → Linux NS       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** After `fork()`, parent and child share Open File Descriptions — they share the file position. This means if the parent reads 1024 bytes, the child's next read starts at offset 1024. In practice, web servers like Apache's prefork model immediately call `exec()` after fork — which resets the fd table to only fds without `FD_CLOEXEC`. Why was this interaction between fork, exec, and FD_CLOEXEC the correct design even though it requires developers to remember to set the flag? What would the alternative (close-on-fork instead of close-on-exec) break?

**Q2.** Linux 5.9 introduced `pidfd_getfd()` — a syscall that copies an fd from one process into another. Previously, the only ways to transfer an fd between processes were: `fork()` inheritance, `sendmsg()` with `SCM_RIGHTS` over a Unix socket, or `/proc/PID/fd` symlinks. Given that `sendmsg(SCM_RIGHTS)` works, why was `pidfd_getfd()` added as an explicit syscall? What use cases does it enable that `SCM_RIGHTS` cannot?
