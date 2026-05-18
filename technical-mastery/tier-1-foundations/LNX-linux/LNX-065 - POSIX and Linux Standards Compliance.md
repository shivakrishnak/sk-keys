---
id: LNX-065
title: "POSIX and Linux Standards Compliance"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★☆
depends_on: LNX-001, LNX-004
used_by: LNX-082, LNX-115
related: LNX-004, LNX-001, LNX-082
tags: [POSIX, standards, portability, SUS, feature-test-macros, GNU-extensions, compatibility, IEEE, XSI]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 65
permalink: /technical-mastery/lnx/posix-linux-standards-compliance/
---

## TL;DR

POSIX (Portable Operating System Interface) is an IEEE standard defining
a portable OS interface. Linux is "mostly POSIX compliant" but not
officially certified. Key POSIX syscalls: `open`, `read`, `write`, `fork`,
`exec`, `pipe`, `signal`, `pthreads`. Feature test macros control which
APIs are visible: `#define _POSIX_C_SOURCE 200809L` for POSIX 2008,
`#define _GNU_SOURCE` for GNU extensions. Linux diverges: `epoll` (no POSIX),
`inotify`, `signalfd`, real-time signals. macOS/BSDs: POSIX certified, but
their extensions differ. POSIX-portable code avoids GNU extensions and
`/proc`. `getconf POSIX_VERSION` to query the system.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-065 |
| **Difficulty** | ★★☆ Intermediate |
| **Category** | Linux |
| **Tags** | POSIX, standards, portability, feature test macros, GNU extensions, SUS |
| **Prerequisites** | LNX-001 (Linux intro), LNX-004 (Shell basics) |

---

### The Problem This Solves

**Problem 1**: A C program using `epoll_create1()` compiles and works on
Linux but fails on macOS and FreeBSD. `epoll` is Linux-specific (not POSIX).
The POSIX-portable alternative is `select()` or `poll()`. Understanding
POSIX vs Linux-specific helps you write portable code or consciously
choose Linux-specific APIs for performance.

**Problem 2**: A script uses `grep -P` (Perl regex, GNU grep extension)
and works on Linux but fails on macOS (`grep: invalid option -- 'P'`).
POSIX `grep` only supports BRE (basic regex) and ERE (`-E`). macOS grep
is BSD grep. Understanding POSIX helps write shell scripts that work on
both Linux and macOS.

---

### Textbook Definition

**POSIX (IEEE Std 1003)**: A family of standards specifying OS-level APIs
for portability between Unix-like systems. Defines: shell (sh), utilities
(ls, grep, awk, sed behavior), C library interfaces, process model
(fork/exec), file I/O, threads (pthreads), signals, IPC.

**Single Unix Specification (SUS)**: A superset of POSIX maintained by
The Open Group. macOS, Solaris, HP-UX are officially POSIX/SUS certified.
Linux is NOT officially certified (certification costs money and requires
passing a test suite; Linux is compatible in practice).

**Feature test macros**: C preprocessor macros that control which function
declarations and constants are exposed by system headers. They let you
explicitly declare which standard you're targeting:

| Macro | Exposes |
|-------|---------|
| `_POSIX_C_SOURCE 200809L` | POSIX 2008 (POSIX.1-2008) |
| `_XOPEN_SOURCE 700` | SUSv4 (POSIX + XSI extensions) |
| `_GNU_SOURCE` | Everything: POSIX + GNU + Linux extensions |
| `_DEFAULT_SOURCE` | Default (glibc 2.19+ default features) |

---

### Understand It in 30 Seconds

```bash
# === What POSIX version does this system claim? ===
getconf POSIX_VERSION
# 200809 = POSIX.1-2008 (also known as IEEE 1003.1-2008)

getconf _POSIX_VERSION   # same
getconf LONG_BIT         # 32 or 64 bit
getconf PATH_MAX         # max path length (often 4096)
getconf NAME_MAX         # max filename length (often 255)

# === List available POSIX-defined utilities ===
getconf CS_PATH   # POSIX-defined PATH for mandatory utilities
# /bin:/usr/bin

# === Check if Linux-specific features are used ===
# Scan a C file for Linux-specific calls:
grep -E \
    "epoll|inotify|signalfd|eventfd|timerfd|splice|sendfile|io_uring" \
    myapp.c
# Any matches = Linux-specific, not portable

# POSIX alternatives:
# epoll -> select() or poll()  (POSIX, works everywhere)
# inotify -> FAM (legacy) or kqueue (BSDs) or stat() polling
# sendfile(Linux) -> sendfile(BSD/macOS different signature) or read/write loop

# === Feature test macros in C code ===
# BAD: relies on glibc defaults (not portable):
#include <string.h>
void example() {
    char buf[1024];
    strfcpy(buf, "hello", sizeof(buf));  // GNU extension
}

# GOOD: explicit standard, uses portable alternative:
#define _POSIX_C_SOURCE 200809L
#include <string.h>
void example() {
    char buf[1024];
    strncat(buf, "hello", sizeof(buf) - 1);  // POSIX
}

# GOOD: explicitly opt into GNU extensions when needed:
#define _GNU_SOURCE   // enables: GNU string functions, epoll, etc.
#include <string.h>
#include <sys/epoll.h>
// Now: getline(), epoll_create1(), pipe2(), etc. are available

# === Check if a function is POSIX or extension ===
man 3 getline
# CONFORMING TO section:
# getline(): POSIX.1-2008
# (it's POSIX, added in the 2008 standard)

man 2 epoll_create
# CONFORMING TO section:
# Linux-specific.
# (NOT POSIX - Linux only)

# === Portable vs Linux-specific: common comparison ===
# FILE I/O:
# POSIX: open/read/write/close, mmap, select, poll, pthreads
# Linux: epoll, io_uring, splice, sendfile, O_DIRECT, O_TMPFILE

# SIGNALS:
# POSIX: kill(), sigaction(), sigsuspend(), sigqueue() for RT signals
# Linux: signalfd(), eventfd(), timerfd() (no POSIX equivalent)

# PROCESS:
# POSIX: fork(), exec*(), wait*(), pipe(), socketpair()
# Linux: clone() (fork/thread basis), pidfd_open(), unshare()
```

---

### First Principles

**Why POSIX portability matters:**
```
The Unix portability problem:
  1960s-1970s: many Unix variants (BSD, System V, etc.)
  Each had slightly different APIs:
    BSD: daemon(), strlcpy()
    System V: System V IPC (semget, shmget, msgget)
    POSIX: tried to standardize the intersection
  
  Code written for one Unix: may not compile on another
  Without standards: "write once, test everywhere"

POSIX standardized:
  File I/O: open/read/write/close/lseek/fcntl/stat/unlink
  Processes: fork/exec/wait/exit/getpid/getppid
  Signals: signal/sigaction/kill/sigsuspend
  IPC: pipes, FIFOs, message queues, semaphores, shared memory
  Threads: pthreads (pthread_create/join/mutex/cond)
  Utilities: sh, ls, cp, mv, cat, grep, awk, sed, make, ...
  C library: string.h, stdio.h, stdlib.h, unistd.h standard interfaces

Where Linux diverges from POSIX:
  POSIX requires:  | Linux provides:
  -----------------+----------------------------------
  select()         | also: epoll (Linux-specific)
  sigaction()      | also: signalfd() (Linux-specific)
  mmap()           | also: mremap(), madvise() extensions
  open()           | also: openat(), O_TMPFILE, O_DIRECT
  fork()           | also: clone() with flags (basis for containers)
  dlopen()         | also: dlmopen() (separate namespace)

Linux-specific features used intentionally:
  epoll: O(1) vs O(n) for many fds (critical for high-perf servers)
  io_uring: async I/O with kernel ring buffer (better than aio_*)
  splice/tee: zero-copy data transfer between fds
  signalfd: handle signals in event loop without signal handlers
  cgroups, namespaces: container isolation (no POSIX equivalent)
```

**Feature test macros mechanism:**
```c
/* glibc feature selection header: features.h
   (automatically included by all system headers)
   
   Sets these flags based on your macros:
   __USE_POSIX, __USE_XOPEN, __USE_GNU, etc.
   
   Each function declaration is wrapped:
*/
/* In /usr/include/unistd.h: */
#ifdef __USE_GNU
extern char *get_current_dir_name(void);  /* GNU extension */
#endif

#if defined __USE_XOPEN_EXTENDED || defined __USE_XOPEN2K8
extern ssize_t getline(char **__restrict __lineptr,
                       size_t *__restrict __n,
                       FILE *__restrict __stream);
/* POSIX 2008 (was GNU extension before 2008) */
#endif

/* So with _POSIX_C_SOURCE=200809L: getline is visible */
/* Without any macro: may or may not be visible (default depends on glibc version) */

/* Practical consequence: */
/* BAD - implicit default features: */
#include <stdio.h>
ssize_t getline_wrapper(char **line, size_t *n, FILE *f) {
    return getline(line, n, f);
    /* May work if default includes POSIX2008, may fail on strict C89 */
}

/* GOOD - explicit macro: */
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
ssize_t getline_wrapper(char **line, size_t *n, FILE *f) {
    return getline(line, n, f);
    /* Guaranteed to be visible if libc supports POSIX 2008 */
}
```

---

### Thought Experiment

Writing a portable server:

```c
/* POSIX-portable event loop vs Linux-specific epoll */

/* ====== POSIX-portable (works on Linux, macOS, BSDs) ====== */
#include <poll.h>
#include <unistd.h>

void portable_event_loop(int *fds, int nfds) {
    struct pollfd *pfds = malloc(nfds * sizeof(struct pollfd));
    for (int i = 0; i < nfds; i++) {
        pfds[i].fd = fds[i];
        pfds[i].events = POLLIN;
    }
    
    while (1) {
        int ready = poll(pfds, nfds, -1);  /* POSIX: blocks until event */
        for (int i = 0; i < nfds; i++) {
            if (pfds[i].revents & POLLIN) {
                handle_read(pfds[i].fd);
            }
        }
        /* Performance: poll() scans all nfds on each call: O(n) */
        /* For 1000 fds: 1000 checks per event. For 10000 fds: slow */
    }
}

/* ====== Linux-specific epoll (Linux only) ====== */
#ifdef __linux__
#include <sys/epoll.h>

void linux_event_loop(int *fds, int nfds) {
    int epfd = epoll_create1(EPOLL_CLOEXEC);
    
    struct epoll_event ev = {.events = EPOLLIN};
    for (int i = 0; i < nfds; i++) {
        ev.data.fd = fds[i];
        epoll_ctl(epfd, EPOLL_CTL_ADD, fds[i], &ev);
    }
    
    struct epoll_event events[64];
    while (1) {
        /* Only returns READY fds - O(1) regardless of total fd count */
        int n = epoll_wait(epfd, events, 64, -1);
        for (int i = 0; i < n; i++) {
            handle_read(events[i].data.fd);
        }
    }
}
#endif

/* Portability pattern: conditional compilation */
/* Use POSIX by default, override with Linux-specific for performance */
```

---

### Mental Model / Analogy

```
POSIX = electrical outlet standards

USA: 120V, type A outlets
EU: 230V, type C/F outlets  
UK: 230V, type G outlets

POSIX = the standard charger spec that ALL countries agree on
  (like USB-C becoming universal)

If your device uses the POSIX "plug" (standard API):
  Works in all Unix-like systems: Linux, macOS, Solaris, FreeBSD

Linux-specific extensions = adapters for extra features:
  "turbo charging" (epoll - faster than standard poll)
  "wireless charging" (io_uring - async without syscalls)
  These give you BETTER performance on Linux,
  but DON'T WORK if you plug into macOS without an adapter

Feature test macros = telling the factory
  which outlet standard to include on your device:
  _POSIX_C_SOURCE = "I want standard outlets only"
  _GNU_SOURCE = "I want all available outlet types"
  No macro = "figure it out yourself" (unpredictable)

Official certification = paying the standards body to test and stamp your system:
  macOS pays, gets certified: "Certified POSIX Compliant"
  Linux doesn't pay: compliant in practice but not officially stamped
  Like a restaurant that cooks great food but hasn't paid for the Michelin star
```

---

### Gradual Depth - Five Levels

**Level 1:**
POSIX defines portable OS interfaces. `getconf POSIX_VERSION` = 200809
on modern Linux. Key POSIX C functions: `open`, `read`, `write`, `fork`,
`exec`, `pthread_*`. Feature test macros: `_POSIX_C_SOURCE` vs `_GNU_SOURCE`.
Check man pages' "CONFORMING TO" section for portability info.

**Level 2:**
Shell portability: POSIX `sh` vs bash extensions. `#!/bin/sh` = POSIX shell.
`#!/bin/bash` = bash-specific. Portable shell: no `[[ ]]` (use `[ ]`), no
`${var,,}` (use `tr`), no process substitution `<()`. `shellcheck` tool
for detecting non-portable shell constructs. POSIX vs GNU grep/sed/awk
differences (`-P`, `\+`, `\d` in grep are GNU extensions).

**Level 3:**
XSI (X/Open System Interfaces) extensions: SUSv4 adds more interfaces
(`strfmon`, `regex.h`, System V IPC). POSIX real-time extensions:
`clock_gettime()`, `nanosleep()`, `aio_*` (async I/O), RT signals
(`SIGRTMIN` through `SIGRTMAX`). Linux epoll vs BSD kqueue vs POSIX poll
comparison. `sysconf()` for runtime POSIX feature detection.

**Level 4:**
POSIX thread cancellation and cleanup handlers. POSIX message queues
(`mq_open`, `mq_send`) vs System V message queues. `clock_gettime(CLOCK_MONOTONIC)`:
POSIX monotonic clock for timing (not affected by NTP adjustments vs
`CLOCK_REALTIME`). POSIX shared memory (`shm_open`, `shm_unlink`) vs
System V shared memory (`shmget`, `shmctl`). File descriptor passing
via UNIX domain sockets: POSIX standard but complex.

**Level 5:**
POSIX.1-2024 (the latest revision): what changed. Large file support
(LFS): `_FILE_OFFSET_BITS=64` for files > 2 GB on 32-bit systems.
`O_LARGEFILE` flag. 64-bit clean code. POSIX conformance testing: the
Open Group's VSX-PCTS test suite. Areas of Linux non-compliance:
mandatory file locking (POSIX mandates behavior Linux doesn't guarantee),
`SA_RESETHAND` + signals interaction subtleties. musl libc vs glibc POSIX
compliance differences. Undefined behavior in POSIX: signal safety
(async-signal-safe functions list), `setjmp`/`longjmp` across stack frames.

---

### Code Example

**BAD - non-portable code:**
```c
/* BAD: Linux-specific, will fail on macOS/BSD */
#include <sys/epoll.h>  /* Linux only */
#include <sys/inotify.h>  /* Linux only */
#include <sys/signalfd.h>  /* Linux only */

/* Will not compile on macOS */
int fd = epoll_create1(EPOLL_CLOEXEC);

/* BAD: relies on /proc (Linux only) */
FILE *f = fopen("/proc/self/status", "r");
/* Fails on macOS - /proc does not exist */

/* BAD: GNU-specific string functions without macro: */
#include <string.h>
/* strchrnul, memmem, strdupa - GNU extensions */
/* Fails with strict C99 compilation: -std=c99 */
```

**GOOD - portable code with conditional Linux optimization:**
```c
/* GOOD: Portable I/O multiplexing with Linux optimization */
#include <poll.h>  /* POSIX: available everywhere */

#ifdef __linux__
#include <sys/epoll.h>  /* Linux: faster than poll */
#endif

typedef struct {
    int fd;
    void (*callback)(int fd);
} EventSource;

int create_event_loop(void) {
#ifdef __linux__
    return epoll_create1(EPOLL_CLOEXEC);
#else
    return 0;   /* Use poll() array index as "fd" */
#endif
}

/* GOOD: shell script - POSIX-portable */
#!/bin/sh
# Note: #!/bin/sh not #!/bin/bash

# BAD:
# if [[ "$var" == "hello" ]]; then  # bash-specific [[ ]]
# GOOD:
if [ "$var" = "hello" ]; then     # POSIX [ ] test
    echo "match"
fi

# BAD: 
# arr=(a b c)  # bash arrays, not POSIX sh
# GOOD: use positional parameters or IFS splitting for portability

# BAD: 
# echo ${var,,}   # bash string manipulation
# GOOD:
echo "$var" | tr '[:upper:]' '[:lower:]'   # POSIX tr
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "Linux is POSIX compliant" | Linux is functionally compatible with POSIX in most respects, but it is NOT officially POSIX certified. Official certification requires paying The Open Group fees and passing the VSX-PCTS conformance test suite. macOS (Darwin), AIX, HP-UX, and Solaris are officially certified. Linux vendors (Red Hat, SUSE) have not paid for certification. In practice, Linux passes nearly all POSIX tests and the major deviations are documented. But "POSIX certified" and "POSIX compatible" are different claims. |
| "Using `#!/bin/bash` makes the script more portable" | It's the opposite. `#!/bin/bash` explicitly requires bash, which may not be at that path (on some systems it's `/usr/local/bin/bash`) or may not be installed at all (Alpine Linux, some minimal containers). `#!/bin/sh` is more portable - POSIX mandates `/bin/sh` exist. But `/bin/sh` on different systems is different: Ubuntu/Debian: dash (faster, stricter POSIX); Fedora/RHEL: bash in sh mode; macOS: dash since Catalina. Truly portable scripts: use `#!/bin/sh` AND avoid all bash extensions (test with `bash --posix` or `dash`). |
| "_GNU_SOURCE gives you everything POSIX plus extras" | `_GNU_SOURCE` exposes: POSIX, XSI, BSD, and GNU-specific APIs. It does make writing Linux/GNU programs easier. But it also hides portability problems - code that uses GNU-only functions compiles fine but will fail on musl libc or non-GNU systems. For portable code: use `_POSIX_C_SOURCE 200809L` (strict) or `_XOPEN_SOURCE 700` (POSIX + XSI). For Linux-only code: `_GNU_SOURCE` is fine. The danger is accidentally using GNU extensions when you think you're writing portable code. |
| "POSIX shell and bash are interchangeable" | POSIX shell (as implemented by `dash` or `bash --posix`) has far fewer features than bash. Missing: `[[ ]]` (use `[ ]`), arrays, `${var,,}` case manipulation, process substitution `<()`, brace expansion `{1..5}`, `local` keyword (actually a bash extension, but widely supported), `declare -A` associative arrays. Code that works in bash may fail silently in POSIX sh (some constructs just behave differently, not error). `shellcheck -s sh script.sh` detects non-POSIX constructs. |
| "POSIX pthreads and Linux threads are the same" | Linux implements POSIX pthreads via NPTL (Native POSIX Thread Library). The API is the same (pthread_create, pthread_mutex_*, etc.). But the IMPLEMENTATION differs from older threading models (LinuxThreads, used before 2003). Key Linux behavior that POSIX leaves implementation-defined: thread IDs (`pthread_t`) are opaque and non-portable (Linux uses clone() with different flags). The Linux-specific `gettid()` syscall returns the kernel-level thread ID (different from `getpid()` in a multithreaded process). `pthread_setname_np()` is a GNU extension for naming threads (useful for debugging). |

---

### Failure Modes & Diagnosis

**Shell script portability failures:**
```bash
# Symptom: script works on developer's Linux but fails in CI (Alpine/Docker/macOS)

# Test 1: Run with strict POSIX sh:
dash ./myscript.sh      # dash = strict POSIX sh on Ubuntu
# or:
bash --posix ./myscript.sh  # bash in POSIX-ish mode

# Test 2: shellcheck analysis:
shellcheck -s sh myscript.sh
# SC2039: In POSIX sh, [[ ]] is undefined.
# SC2039: In POSIX sh, string indexing is undefined.
# SC2086: Double quote to prevent globbing and word splitting

# Common failures:

# FAIL: bash array (not POSIX):
arr=(a b c)
echo "${arr[@]}"    # bash-specific

# FIX: use positional parameters or space-separated string:
set -- a b c
echo "$@"    # $@ is POSIX

# FAIL: [[ ]] in sh:
if [[ "$x" =~ ^[0-9]+$ ]]; then   # bash-only

# FIX: use grep or [ ]:
if echo "$x" | grep -qE '^[0-9]+$'; then   # POSIX

# FAIL: source builtin (not POSIX sh):
source /etc/profile

# FIX: use . (dot) - POSIX:
. /etc/profile

# FAIL: $(...) is POSIX, but backtick substitution has quoting differences:
result=$(command)   # POSIX, preferred
result=`command`    # POSIX too, but harder to nest

# FAIL: GNU-specific flags:
grep -P '\d+' file  # -P = Perl regex, GNU grep only
# FIX:
grep -E '[0-9]+' file   # POSIX ERE

sed -i 's/foo/bar/g' file   # -i is GNU (macOS needs: sed -i '' 's/foo/bar/g')
# FIX for cross-platform:
sed -i.bak 's/foo/bar/g' file  # .bak = works on both (macOS requires backup suffix)
```

---

### Related Keywords

**Foundational:**
LNX-001 (Linux overview), LNX-004 (Shell basics)

**Builds on this:**
LNX-082 (Syscall Interface), LNX-115 (POSIX spec and Linux)

**Related:**
LNX-066 (Bash Advanced - where POSIX sh vs bash matters)

---

### Quick Reference Card

| Item | Details |
|------|---------|
| Check POSIX version | `getconf POSIX_VERSION` (200809 = POSIX 2008) |
| POSIX macro | `#define _POSIX_C_SOURCE 200809L` |
| GNU extensions | `#define _GNU_SOURCE` |
| Check portability (man) | See "CONFORMING TO" section |
| Shell check | `shellcheck -s sh script.sh` |
| POSIX shell | `#!/bin/sh` (use `dash` for strict test) |
| Linux-specific APIs | epoll, inotify, signalfd, io_uring, clone() |
| Portable I/O mux | `poll()` (POSIX, works everywhere) |

**3 things to remember:**
1. Linux is POSIX-compatible but NOT officially certified - check man page "CONFORMING TO" to know if an API is POSIX, GNU extension, or Linux-specific
2. `_GNU_SOURCE` exposes everything; `_POSIX_C_SOURCE 200809L` for strict portability
3. `#!/bin/sh` + `shellcheck -s sh` for portable shell scripts; bash-specific: `[[ ]]`, arrays, `${var,,}`

---

### Transferable Wisdom

POSIX portability concepts appear in: Docker Alpine Linux images (uses musl
libc instead of glibc - some GNU extensions are absent: `backtrace()`,
`getopt_long()` behavior differences). Go `syscall` package: carefully
documented which calls are POSIX vs Linux-specific. Rust's `nix` crate:
provides safe wrappers for POSIX syscalls, clearly marks Linux extensions.
The `#ifdef __linux__` / `#ifdef __APPLE__` pattern is how Nginx, Redis,
and other cross-platform servers handle platform differences. CMake's
platform detection for cross-platform builds. Python's `os.fork()` is POSIX
(documented as "Unix-only"), while Windows uses `os.spawn*()`. Java's
`ProcessBuilder` abstracts the fork/exec divide between Unix and Windows.
The principle of "define your portability layer at the boundary" applies to
cloud APIs: write against the common subset (S3-compatible API) and you can
switch from AWS to MinIO to GCS without changing application code.

---

### The Surprising Truth

The "POSIX portable" advantage has largely inverted in the container era.
In 2005, writing POSIX-portable code was important because applications
needed to run on Solaris, HP-UX, AIX, Linux, and macOS. In 2024, almost
all server applications run in Linux containers. The only portability target
that matters for most backend services is "runs on Linux." This means Linux-
specific APIs (epoll, io_uring, inotify, eBPF) are not "vendor lock-in" but
legitimate performance tools. The projects that paid the portability tax most
expensively were the Java application servers: they avoided `epoll` (Linux),
`kqueue` (BSD), and implemented everything in userspace with POSIX `select()` -
until Netty (2008) and later projects started explicitly choosing Linux-specific
I/O for 10x-100x concurrency improvements. Today, io_uring (Linux 5.1+, 2019)
enables async I/O with a fraction of the syscall overhead of `epoll`. The
runtimes that use it (io_uring in Tokio/Rust, Java's Project Loom
exploration, newer Node.js versions) get dramatic throughput improvements
that are simply impossible with POSIX-portable I/O abstractions. The lesson:
POSIX portability is still valuable for desktop tools and embedded systems,
but intentional use of Linux-specific APIs is often the right engineering
choice for server workloads.

---

### Mastery Checklist

- [ ] Understands what POSIX standardizes and where Linux deviates
- [ ] Can identify POSIX vs GNU extension using man page "CONFORMING TO"
- [ ] Knows key feature test macros and when to use each
- [ ] Can write portable shell scripts avoiding bash-specific constructs
- [ ] Understands why Linux-specific APIs (epoll, io_uring) are valuable

---

### Think About This

1. You're writing a high-performance TCP server in C that needs to handle
   100,000 concurrent connections. You have two choices: POSIX `poll()` which
   is portable, or Linux `epoll` which is Linux-only. Explain the algorithmic
   difference (O(n) vs O(1)) and describe how you would structure the code to
   use `epoll` on Linux but fall back to `poll()` on other platforms.

2. A shell script that works on the developer's Ubuntu laptop fails in a Docker
   container based on Alpine Linux with `sh: syntax error: bad substitution`.
   The script uses `${var,,}`. Explain why this fails, what POSIX-portable
   alternative achieves the same result, and what tool you would run to catch
   such issues before deployment.

3. Your team debates whether to write the new CLI tool in C with
   `_GNU_SOURCE` (simpler, richer API) or with `_POSIX_C_SOURCE 200809L`
   (portable). The tool is an internal developer utility for Linux environments.
   Make the case FOR using `_GNU_SOURCE` and against strict POSIX compliance,
   given the actual deployment context.

---

### Interview Deep-Dive

**Foundational:**
Q: What is POSIX, and how does it relate to Linux?
A: POSIX (Portable Operating System Interface) is an IEEE standard (IEEE 1003) that defines a standard API for Unix-like operating systems. It standardizes: the C library interface (open, read, write, fork, exec, etc.), the shell interface (sh syntax, standard utilities like ls, grep, awk, sed), threads (pthreads: pthread_create, mutex, condition variables), signals, IPC (pipes, FIFOs, message queues, semaphores, shared memory), and file system semantics (file permissions, path resolution). The goal: write code once, compile and run on any POSIX-compliant system. Linux is not officially POSIX certified (would require paying The Open Group for certification and passing the conformance test suite) but is functionally compatible with POSIX in almost all practical areas. Official POSIX-certified systems: macOS, Solaris, AIX, HP-UX. In practice, Linux passes the POSIX test suite for most requirements. Key divergences: Linux has many extensions beyond POSIX (epoll, inotify, io_uring, /proc, namespaces, cgroups) that make Linux more powerful but less portable. Linux also has some areas where POSIX behavior is technically not guaranteed (advisory locking semantics). For developers: check man page "CONFORMING TO" sections to distinguish POSIX (portable) from Linux-specific (non-portable). For shell scripts: use `#!/bin/sh` and test with `shellcheck -s sh` to ensure POSIX portability.

**Expert:**
Q: When would you choose epoll over poll() despite epoll being Linux-specific?
A: The choice between POSIX `poll()` and Linux-specific `epoll` is a classic portability vs performance trade-off: `poll()`: O(n) per call (scans all n file descriptors every time to find ready ones). Works on all POSIX systems. For N < 1000 fds: difference is negligible. Above 1000 fds: poll's O(n) scanning starts to dominate. `epoll`: O(1) per event (kernel maintains a separate ready-list, only returns actually-ready fds). Edge-triggered (EPOLLET) mode allows one epoll_wait to serve many connections without re-scanning. Linux-specific: won't compile on macOS (uses kqueue) or Windows. Performance impact at scale: with 10,000 connections where 100 are active at any time, poll() performs 10,000 checks per event cycle. epoll_wait() returns exactly the 100 active fds. This is NOT just a constant-factor difference - it's algorithmic. This is why: Nginx uses epoll on Linux. Node.js uses epoll via libuv. Java NIO uses epoll on Linux via NativeEpollEventLoop (Netty). Redis uses epoll. The pattern for "portable but high-performance": abstract the event loop behind a platform-detection layer: `#ifdef __linux__` -> use epoll; `#ifdef __APPLE__` -> use kqueue (similarly efficient); else -> use poll. `libevent`, `libuv`, `libev` all implement this abstraction. Choose epoll specifically when: (1) targeting Linux servers only (which is most server deployments today), (2) expected concurrency > 1000 connections, (3) performance is a priority. Keep poll() for: tooling that must run on macOS/BSDs, small-scale servers where O(n) is fine, and educational code where clarity matters more than performance.
