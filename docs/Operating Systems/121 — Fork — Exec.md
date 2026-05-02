---
layout: default
title: "Fork — Exec"
parent: "Operating Systems"
nav_order: 121
permalink: /operating-systems/fork-exec/
number: "0121"
category: Operating Systems
difficulty: ★★☆
depends_on: Process, Thread, System Call (syscall), Virtual Memory
used_by: Shell, Process Supervision, Docker
related: COW (Copy-on-Write), execve, waitpid, Zombie Process
tags:
  - os
  - process-management
  - linux
  - fundamentals
---

# 121 — Fork — Exec

⚡ TL;DR — `fork()` creates an exact copy of the current process; `exec()` replaces that copy's image with a new program. Together, they are how Unix spawns every new process.

| #0121           | Category: Operating Systems                            | Difficulty: ★★☆ |
| :-------------- | :----------------------------------------------------- | :-------------- |
| **Depends on:** | Process, Thread, System Call (syscall), Virtual Memory |                 |
| **Used by:**    | Shell, Process Supervision, Docker                     |                 |
| **Related:**    | COW (Copy-on-Write), execve, waitpid, Zombie Process   |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
To run a new program, you need to: set up a new address space, load the executable, configure file descriptors (stdin/stdout/stderr), set environment variables, configure signals — then hand control to main(). How should an OS provide a single syscall for all of this? It would need dozens of parameters. Alternatively, the OS could provide many specialized syscalls — but then the calling program has to orchestrate them, dealing with races and partial failures.

**THE BREAKING POINT:**
The 1970s Unix designers solved this with a two-stage approach: (1) `fork()` copies everything from the parent — you get all the file descriptors, environment, memory — for free, by inheritance. (2) `exec()` replaces the program image — swaps in the new executable while keeping inherited context (file descriptors, pid-based identity). Between fork and exec (the "fork-exec gap"), you can close the right file descriptors, set up pipes, redirect stdin/stdout. This is extraordinarily composable.

**THE INVENTION MOMENT:**
Dennis Ritchie's 1974 UNIX description: "A new process is created by the fork system call. A new process is an exact copy of the calling process... a process may cause the execution of another program via exec." The elegance is that exec() consumes no new resources — it reuses the process slot, address space, and file descriptors (selectively).

---

### 📘 Textbook Definition

**`fork()`** is a Unix system call that creates a new **child process** as an exact copy of the calling (parent) process. After fork(), both parent and child execute independently from the instruction following the fork() call. The return value distinguishes them: 0 is returned to the child; the child's PID is returned to the parent.

**`exec()` family** (`execve`, `execl`, `execlp`, `execle`, `execv`, `execvp`, `execvpe`) replaces the current process's program image with a new executable: code segment, data, heap, and stack are replaced; the PID, file descriptors (unless marked close-on-exec), and environment (optionally) are preserved.

The **fork-exec pattern** is the standard Unix mechanism for spawning a new process running a different program. Modern Linux optimises fork() with **copy-on-write (COW)**: the child's pages are not physically copied — only the page table entries are duplicated, marked read-only. Physical pages are copied only when either process writes to them.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
`fork()` = copy yourself; `exec()` = become someone else. Shell runs ls by: fork (copy shell) then exec (become ls).

**One analogy:**

> Fork is like photocopying your entire desk setup (documents, pens, open books). Exec is then throwing away everything on your desk and replacing it with the materials for a completely different project. The desk (PID, file handles) stays the same; the content (program code, memory) is replaced.

**One insight:**
Between fork and exec, the child has a unique moment: it's a copy of the parent but hasn't yet replaced itself. This window is used for Unix I/O redirection (`dup2(pipe[1], STDOUT_FILENO)` before exec) — an elegant trick that requires no special kernel support for redirection.

---

### 🔩 First Principles Explanation

FORK SEMANTICS:

```c
pid_t pid = fork();
if (pid < 0) {
    // Error
} else if (pid == 0) {
    // CHILD: pid=0, actual PID from getpid()
    // Exact copy of parent's address space (COW)
    // Same open file descriptors (same file table entries)
    // Same environment, signal handlers, current directory
} else {
    // PARENT: pid = child's PID
    // Both continue from here independently
}
```

EXEC SEMANTICS:

```c
// In child after fork:
execvp("ls", argv);  // replaces program image with ls
// If execvp returns, it failed (ENOENT, EACCES, etc.)
// If it succeeds, the line below is NEVER reached
perror("exec failed");
exit(1);
```

COW OPTIMISATION:
Without COW: fork() copies entire address space (could be GBs for a JVM process). With COW: fork() only duplicates page tables (O(number of pages) metadata, not data). A shell forking to run `ls` copies ~100KB of page table entries, not 100MB of JVM heap. When child calls exec(), the COW pages are discarded immediately (exec replaces the entire address space), so the physical copy was never needed.

**THE TRADE-OFFS:**
**Gain:** Composable process creation; pipes and redirections work without OS-level special cases.
**Cost:** Fork in large processes is still slow (page table duplication, TLB flush); COW can cause unexpected latency spikes when copy-on-write pages are written to before exec.

---

### 🧪 Thought Experiment

SHELL PIPE IMPLEMENTATION (`ls | grep .md`):

```
Shell:
1. pipe(pipefd) → creates pipefd[0]=read, pipefd[1]=write
2. fork() → Child1 (will run ls)
   Child1:
     dup2(pipefd[1], STDOUT_FILENO)  // ls stdout → pipe write end
     close(pipefd[0]); close(pipefd[1])  // close originals
     exec("ls")  // ls writes to pipe instead of terminal
3. fork() → Child2 (will run grep)
   Child2:
     dup2(pipefd[0], STDIN_FILENO)   // grep stdin ← pipe read end
     close(pipefd[0]); close(pipefd[1])
     exec("grep", ".md")  // grep reads from pipe
4. close(pipefd[0]); close(pipefd[1]) in parent
5. waitpid(Child1); waitpid(Child2)
```

**THE INSIGHT:**
The fork-exec gap (between fork and exec) is when all I/O plumbing happens. The kernel doesn't need to know about pipes or redirection. The shell manipulates file descriptors using standard syscalls, then calls exec. Exec preserves the file descriptor setup. The result: `ls` outputs to a pipe, `grep` reads from the pipe, with no kernel-level pipe-awareness required.

---

### 🧠 Mental Model / Analogy

> Think of a process as a fully outfitted chef (code + memory + tools). `fork()` is: hire an identical chef — same recipes memorised (code), same ingredients on hand (memory, COW), same knives in hand (file descriptors). `exec()` is: that copied chef forgets all their recipes and learns a completely new cuisine — but keeps the same kitchen (PID, file descriptors).

> The fork-exec gap is the brief moment after hiring the copy before they start the new menu — just enough time to rearrange the kitchen (close/open file descriptors, set up environment).

Where this breaks down: the COW optimisation means the "copied ingredients" (memory pages) aren't physically copied until touched — the copy is a shared illusion until modified.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
When Unix needs to run a new program (like `ls` or `grep`), it does two steps: first it duplicates the currently running process (fork), then the duplicate transforms itself into the new program (exec). This two-step approach gives the new process everything it needs — environment variables, file connections — before replacing itself with the actual program code.

**Level 2 — How to use it (junior developer):**
In Java: `ProcessBuilder` and `Runtime.exec()` use fork-exec under the hood on Linux/macOS. In Python: `subprocess.Popen()` uses fork-exec (or `posix_spawn` on some platforms). You rarely call fork/exec directly in application code. Know it for: understanding how shells work, why forking a large JVM process can be slow (page table duplication), and debugging child process failures (check return value of exec, handle EAGAIN, ENOMEM).

**Level 3 — How it works (mid-level engineer):**
`fork()` (Linux kernel `copy_process()`): duplicates task_struct, mm_struct (page tables), file descriptor table, signal handlers, namespaces. COW: all VMAs (virtual memory areas) are set copy-on-write — their PTEs are marked not-writable. On first write to a COW page: page fault → `do_wp_page()` → allocates new physical page, copies content, updates PTE. `exec()` (`do_execve()` kernel): loads ELF headers, maps segments, sets up stack with argv/envp/auxv, jumps to entry point. All COW mappings are discarded. File descriptors with `FD_CLOEXEC` (`O_CLOEXEC`) are closed. Linux `vfork()`: even lighter — child borrows parent's address space, parent blocked until child calls exec or exit.

**Level 4 — Why it was designed this way (senior/staff):**
The fork-exec split is a design choice that emerged from PDP-7 Unix (1969). It was controversial: MULTICS and later Windows used CreateProcess() (atomic process creation). Linus Torvalds has called fork the "best system call ever". The argument for fork-exec: composability via the fork-exec gap; pipelines, redirections, environment setup, capability dropping — all happen in user space using existing syscalls (dup2, close, setuid), with zero kernel involvement. Arguments against: forking a large process is expensive (page table copy, TLB flush, COW page faults); Node.js's `cluster.fork()`, Ruby's puma web server — all struggle with large heap fork performance. `posix_spawn()` (added to POSIX in 2001) is an attempt to provide atomic fork-exec without the expensive intermediate state; used by some runtimes for this reason.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────────────────┐
│                FORK-EXEC FLOW                           │
├─────────────────────────────────────────────────────────┤
│  BEFORE FORK:                                           │
│  Parent: PID=100, mm=[code|heap|stack], fd=[0,1,2,5]   │
│                                                         │
│  AFTER fork():                                          │
│  Parent: PID=100, fork() returns 101 (child PID)       │
│  Child:  PID=101, fork() returns 0                      │
│    mm = COW copy (same physical pages, marked R/O)      │
│    fd = same (fd[5] still open in both)                 │
│                                                         │
│  FORK-EXEC GAP (child side):                            │
│  Child: close(fd[5])      // don't leak to child        │
│  Child: dup2(pipe_w, 1)   // stdout → pipe              │
│                                                         │
│  AFTER exec("ls"):                                      │
│  Child: PID=101, mm=[ls code|ls heap|ls stack] (NEW)    │
│         COW pages discarded; ls binary loaded           │
│         fd = [0, pipe_w, 2] (fd[5] closed by exec gap  │
│                              or FD_CLOEXEC)             │
│  Parent: PID=100, unchanged, waitpid(101)               │
└─────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

SHELL COMMAND EXECUTION:

```
1. User types: ls -la /tmp

2. Shell: fork()
   → Parent (shell): wait for child
   → Child: (copy of shell)

3. Child: dup2/close (no redirection needed for simple ls -la)

4. Child: execvp("ls", ["-la", "/tmp", NULL])
   Kernel:
   a. Open /bin/ls (ELF binary)
   b. Release COW page tables (free parent's copied mappings)
   c. Load ELF segments (map code RO, data RW, BSS)
   d. Set up stack: ["/tmp", "-la", "ls", NULL] + envp + auxv
   e. Point RIP/PC to ls entry point (_start → main)

5. ls executes: reads /tmp, writes to stdout (fd=1)

6. ls exits: exit(0)
   Kernel: sends SIGCHLD to parent (shell)
   ls process → zombie (task_struct remains, mm freed)

7. Shell: waitpid(child_pid) → collects exit status
   → Zombie cleaned up (task_struct freed)

8. Shell: prompt again
```

---

### 💻 Code Example

Example 1 — Basic fork-exec in C:

```c
#include <unistd.h>
#include <sys/wait.h>
#include <stdio.h>

int main() {
    pid_t pid = fork();
    if (pid < 0) {
        perror("fork"); return 1;
    } else if (pid == 0) {
        // Child
        char *args[] = {"ls", "-la", "/tmp", NULL};
        execvp("ls", args);
        perror("exec");  // Only reached if exec fails
        _exit(1);        // _exit, not exit (avoids flushing parent's stdio)
    } else {
        // Parent
        int status;
        waitpid(pid, &status, 0);
        printf("Child exited with status %d\n", WEXITSTATUS(status));
    }
    return 0;
}
```

Example 2 — Fork-exec with pipe (implementing `ls | wc -l`):

```c
int pipefd[2];
pipe(pipefd);

pid_t ls_pid = fork();
if (ls_pid == 0) {
    close(pipefd[0]);                // close read end in ls
    dup2(pipefd[1], STDOUT_FILENO);  // ls stdout → pipe write
    close(pipefd[1]);
    execlp("ls", "ls", NULL);
    _exit(1);
}

pid_t wc_pid = fork();
if (wc_pid == 0) {
    close(pipefd[1]);                // close write end in wc
    dup2(pipefd[0], STDIN_FILENO);   // wc stdin ← pipe read
    close(pipefd[0]);
    execlp("wc", "wc", "-l", NULL);
    _exit(1);
}

close(pipefd[0]); close(pipefd[1]); // parent closes both
waitpid(ls_pid, NULL, 0);
waitpid(wc_pid, NULL, 0);
```

Example 3 — Java ProcessBuilder (uses fork-exec):

```java
// Java ProcessBuilder → fork-exec under the hood on Linux
ProcessBuilder pb = new ProcessBuilder("ls", "-la", "/tmp");
pb.redirectErrorStream(true);                    // merge stderr into stdout
pb.directory(new File("/tmp"));                  // set working directory

Process p = pb.start();
String output = new String(p.getInputStream().readAllBytes());
int exitCode = p.waitFor();
System.out.println("Output: " + output);
System.out.println("Exit: " + exitCode);
```

---

### ⚖️ Comparison Table

| Mechanism           | Copies Parent?      | New Program?         | Use Case                                |
| ------------------- | ------------------- | -------------------- | --------------------------------------- |
| **fork()**          | Yes (COW)           | No                   | Create child, then modify or exec       |
| **exec()**          | N/A (replaces)      | Yes                  | Replace current program image           |
| **fork() + exec()** | Yes, then discarded | Yes                  | Standard process spawning               |
| **vfork()**         | Shares parent mm    | Yes (must exec/exit) | Legacy, ultra-fast pre-exec             |
| **posix_spawn()**   | No (atomic)         | Yes                  | Efficient on large-heap processes       |
| **clone()** (Linux) | Selective           | No                   | Threads, containers (namespace control) |

---

### ⚠️ Common Misconceptions

| Misconception                               | Reality                                                                            |
| ------------------------------------------- | ---------------------------------------------------------------------------------- |
| "fork() copies all memory immediately"      | COW: physical pages only copied on write; page tables are copied                   |
| "exec() closes all file descriptors"        | Only FDs with FD_CLOEXEC are closed; others are inherited into new program         |
| "fork() is always slow for large processes" | COW makes fork fast; slow only when child writes many pages before exec            |
| "fork() creates a thread"                   | fork creates a PROCESS (separate address space); threads use clone() with CLONE_VM |

---

### 🚨 Failure Modes & Diagnosis

**1. Fork Bomb**

**Symptom:** System becomes unresponsive; `fork failed: Resource temporarily unavailable` (EAGAIN); process count at ulimit max.

**Root Cause:** Process calling fork() in a loop without exec/exit; each child also forks: `:(){ :|:& };:` in bash.

**Prevention:**

```bash
# Set per-user process limit
ulimit -u 1024          # session-level
# /etc/security/limits.conf: add 'user hard nproc 1024'
# Kernel-level: cgroups pids controller
echo 100 > /sys/fs/cgroup/pids/user.slice/pids.max
```

---

**2. File Descriptor Leak Across exec**

**Symptom:** Child process (different program) unexpectedly holds parent's socket/file open; `lsof | grep <port>` shows unexpected process holding socket.

**Root Cause:** Parent opened fd without O_CLOEXEC; fork+exec child inherits fd.

**Fix:**

```c
// Set O_CLOEXEC at open time
int fd = open("file.txt", O_RDONLY | O_CLOEXEC);
// Or set after open:
fcntl(fd, F_SETFD, FD_CLOEXEC);
// Java NIO channels: set by default; FileOutputStream: may not
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Process` — fork creates a new process; need process model first
- `Virtual Memory` — COW relies on virtual memory page mapping
- `System Call (syscall)` — fork/exec are system calls

**Builds On This (learn these next):**

- `COW (Copy-on-Write)` — the optimisation that makes fork cheap for large processes
- `Zombie Process` — what a fork'd child becomes after exit before waitpid()
- `Linux Namespaces` — Docker uses clone() (not fork-exec) to create isolated containers

**Alternatives / Comparisons:**

- `posix_spawn()` — avoids fork overhead for large processes; fewer composability options
- `CreateProcess()` (Windows) — atomic; no fork-exec pattern; separate environment setup API

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ fork(): exact process copy (COW)          │
│              │ exec(): replace image with new program    │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Composable process creation with         │
│ SOLVES       │ inherited file descriptors / environment  │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Fork-exec gap = plumb I/O in user space;  │
│              │ no kernel-level redirection needed        │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Spawning child processes (shells, servers,│
│              │ CI runners), building Unix pipes          │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Large JVM process forks: use posix_spawn  │
│              │ or dedicated process supervisor instead   │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Composability (fork-exec) vs efficiency   │
│              │ (posix_spawn / CreateProcess)             │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "fork() = copy me; exec() = become them"  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ COW → Namespaces → posix_spawn            │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Redis uses fork() for its persistence mechanisms (BGSAVE/BGREWRITEAOF). When Redis calls fork(), the child process gets a COW copy of the entire dataset. If Redis is handling 100k writes/second with a 10GB dataset, and the BGSAVE fork'd child takes 30 seconds to write the RDB file, approximately how many COW page faults occur and what is the memory overhead? Calculate the worst-case scenario (all writes touch different pages, 4KB page size) and explain why Redis documentation warns about memory usage doubling during BGSAVE on a write-heavy system.

**Q2.** Docker containers are created using `clone()` with flags like `CLONE_NEWPID | CLONE_NEWNET | CLONE_NEWMNT | CLONE_NEWUTS` — not `fork()`. Explain: (1) what these namespace flags do, (2) why Docker uses `clone()` rather than `fork() + exec()`, (3) what the OCI runtime spec (`runc`) does between clone() and exec() — specifically how it sets up the container's filesystem (pivot_root), user mappings (uid_map), and cgroup membership — and (4) how `docker exec` (attaching to a running container) works differently from `docker run` (it calls `setns()` rather than `clone()`).
