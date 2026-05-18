---
id: LNX-115
title: "POSIX Specification and Its Relationship to Linux"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★★
depends_on: LNX-001, LNX-109, LNX-111
used_by: LNX-117, LNX-119
related: LNX-001, LNX-109, LNX-111, LNX-119
tags: [posix, ieee-1003, single-unix-specification, sus, xsi, xopen, unix-standards, portable-operating-system, syscall-interface, glibc, gnu-source, epoll, signalfd, eventfd, inotify, linux-extensions, android-bionic, macos-posix, posix-compliance, pthread, sigaction, fork, exec, pipe, mmap, posix-versioning, c11-standard, autoconf, automake, libc-compatibility, posix-shell, xsi-extensions, bash-posix]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 115
permalink: /technical-mastery/lnx/posix-specification-relationship-to-linux/
---

## TL;DR

POSIX (Portable Operating System Interface, IEEE Std 1003.1) defines the
interface that Unix-compatible operating systems must provide: **system calls**
(open, read, write, close, fork, exec, wait, pipe, mmap), **signals**
(SIGTERM, SIGKILL, SIGCHLD), **POSIX threads** (pthread_create, mutex, cond),
**shell and utilities** (sh, ls, cp), and **file permissions** (rwxrwxrwx bits).
Linux is **NOT officially POSIX certified** (testing and certification cost is
high), but Linux is **POSIX-compatible in practice** - any POSIX-compliant
program runs on Linux. Linux also extends beyond POSIX with Linux-specific
features: **epoll** (scalable I/O: POSIX has only select/poll, epoll handles
millions of fds efficiently), **signalfd/eventfd/timerfd** (unified event
notification), **inotify** (filesystem event monitoring). These extensions are
enabled with `#define _GNU_SOURCE`. POSIX.1-2017 is the current standard.
**Android deviates**: uses Bionic libc (not glibc), missing some POSIX functions,
adds Android-specific APIs. **macOS POSIX**: certified, but case-insensitive
filesystem and different socket options cause subtle portability bugs.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-115 |
| **Difficulty** | ★★★ Advanced |
| **Category** | Linux |
| **Tags** | POSIX, IEEE 1003.1, system calls, portability, glibc, epoll, pthreads, SUS, Unix standards |
| **Prerequisites** | LNX-001 (Linux overview), LNX-111 (kernel architecture) |

---

### The Problem This Solves

**The portability problem**: Without a standard, a program written for Solaris
won't compile on HP-UX won't run on AIX won't run on Linux. Every Unix vendor
in the 1980s had slightly different system calls, different signal semantics,
different threading models. The cost: separate codebases for each platform.
POSIX solved this: write to the POSIX interface, compile on any conforming system.

**The "which Unix is the real Unix?" problem**: AT&T owned the Unix trademark and
sued BSD (USL v. BSDi, 1992). POSIX defined Unix BEHAVIORS without depending on
AT&T's code. Linux implemented POSIX behaviors from scratch (legal Unix-compatible
system). POSIX is the spec; Linux is an implementation of the spec.

---

### Textbook Definition

**POSIX (Portable Operating System Interface)**: IEEE standard (IEEE Std 1003.1)
defining the interface to Unix-compatible operating systems. Core spec: system
calls (open, read, write, close, fork, exec, signal, wait, pipe, mmap, shmget,
pthread_*). Utilities: sh, awk, sed, grep, ls, cp, rm, tar. Specifies: behavior,
not implementation.

**Single Unix Specification (SUS)**: The Open Group's branding for the combined
POSIX + X/Open System Interface (XSI) standard. A system can be "POSIX
conformant" (implements base) or "Unix" (Open Group certified, stricter).

**`_GNU_SOURCE`**: Feature test macro that enables Linux-specific extensions
in glibc header files. Without it: only POSIX-defined functions visible.
With it: epoll, signalfd, eventfd, inotify, timerfd, and other Linux extensions.

---

### Understand It in 30 Seconds

```bash
# === POSIX vs Linux-specific features ===

# POSIX-defined: works on Linux, macOS, FreeBSD, AIX, Solaris
open("/etc/passwd", O_RDONLY)       # POSIX
read(fd, buf, count)                # POSIX
fork()                              # POSIX
exec("/bin/ls", args, env)          # POSIX
pthread_create(&tid, NULL, fn, arg) # POSIX (pthreads)
signal(SIGTERM, handler)            # POSIX
mmap(NULL, len, PROT_READ, MAP_PRIVATE, fd, 0) # POSIX
select(nfds, &readfds, NULL, NULL, &timeout)   # POSIX (I/O multiplexing)

# Linux-specific: NOT in POSIX standard
epoll_create1(EPOLL_CLOEXEC)  # Linux only
epoll_wait(epfd, events, n, -1)     # Linux only
inotify_init1(IN_CLOEXEC)     # Linux only
signalfd(fd, &mask, SFD_CLOEXEC)   # Linux only
eventfd(0, EFD_CLOEXEC)        # Linux only
timerfd_create(CLOCK_MONOTONIC, TFD_CLOEXEC)  # Linux only

# macOS equivalents (different API, same purpose):
# kqueue + kevent    <- macOS equivalent of epoll
# FSEvents or kqueue <- macOS equivalent of inotify
# dispatch_source    <- macOS equivalent of timerfd

# === Enabling Linux extensions ===
# In C code, before any #include:
#define _GNU_SOURCE  // or _POSIX_C_SOURCE 200809L for POSIX-only

# Without _GNU_SOURCE:
cat program.c
# #include <sys/epoll.h>  <- epoll header
# int main() {
#     int epfd = epoll_create1(0);  // won't compile without _GNU_SOURCE!

# Check what _GNU_SOURCE enables:
man 7 feature_test_macros | grep -A 5 "_GNU_SOURCE"
# _GNU_SOURCE: enables _POSIX_C_SOURCE=200809L, _XOPEN_SOURCE=700,
#              _ISOC99_SOURCE, _ISOC11_SOURCE, and all GNU extensions

# === POSIX compliance check ===

# Check POSIX version available at runtime:
getconf _POSIX_VERSION
# 200809    <- POSIX.1-2008 (same as POSIX.1-2017 for most purposes)

getconf _XOPEN_VERSION
# 700       <- SUS/XSI version 7

# Check if specific POSIX option is supported:
getconf _POSIX_THREADS       # POSIX threads supported: 200809
getconf _POSIX_MONOTONIC_CLOCK  # CLOCK_MONOTONIC available: 200809
getconf _POSIX_TIMERS        # POSIX timers: 200809
getconf _POSIX_REALTIME_SIGNALS # RT signals: 200809
# Any value >= 0: supported. -1: not supported.

# === Android Bionic vs glibc differences ===

# On Android (via ADB):
adb shell cat /proc/version
# Linux version 5.15.104-android13-...

adb shell ls /system/lib64/libc.so
# /system/lib64/libc.so  <- Bionic libc (not glibc!)

# Bionic differences from POSIX/glibc:
# 1. No pthread_cancel() (removed in Android for simplicity)
# 2. No locales (locale_t, setlocale - minimal or missing)
# 3. Different pthread_spinlock_t behavior
# 4. No getwd() (use getcwd instead)
# 5. dlopen() differences (Android's dynamic linker has restrictions)
# 6. No /etc/passwd (Android uses different user model)
# 7. strtod/atof: slightly different NaN/Inf handling
```

---

### First Principles

```
THE UNIX STANDARDIZATION HISTORY:

1969-1972: Unix born at Bell Labs (Thompson, Ritchie, Kernighan)
  AT&T Unix: not freely distributable (business unit)
  But: influential, widely taught in universities

1977: BSD Unix (UC Berkeley): takes AT&T Unix, adds improvements
  Bill Joy: wrote vi, csh, TCP/IP stack for BSD
  BSD Unix: freely distributed to universities (mostly)

1980s: Unix fragmentation
  AT&T System V Unix
  BSD 4.3 Unix (Bill Joy, Berkeley)
  SunOS (Sun, based on BSD)
  HP-UX (HP, System V based)
  AIX (IBM, System V based)
  Ultrix (DEC, BSD based)
  XENIX (Microsoft, yes, Microsoft, System V based)
  SCO Unix (also System V)
  Irix (SGI)
  
  Each slightly different:
  AT&T termios vs BSD sg (terminal settings)
  AT&T SysV IPC vs BSD sockets (networking)
  AT&T curses vs BSD curses
  Different signal semantics (AT&T reset signal after delivery; BSD didn't)
  
  Software vendors: had to maintain separate codebases per Unix flavor.
  Development cost: astronomical.

1988: POSIX 1003.1 published (IEEE)
  Goal: define the common interface that ALL Unix systems provide
  Method: survey existing Unices, find intersection, standardize it
  Key contributors: IEEE working group with AT&T, BSD, Sun, HP, IBM, IBM
  
  What they standardized:
  - System calls: open, close, read, write, seek, stat, chmod, chown
  - Process API: fork, exec, wait, waitpid, exit, getpid
  - IPC: pipes (pipe), signals, shared memory (shmget)
  - File system: directory ops (opendir, readdir, closedir)
  - User/group: getuid, getgid, getpwent, getgrent
  - POSIX threads (1003.1c): pthread_create, mutex, condition variables
  - Clock: gettimeofday, clock_gettime (CLOCK_MONOTONIC, CLOCK_REALTIME)
  
  What they did NOT standardize (left as "undefined"):
  - /proc filesystem (Linux-specific, plan9-style on some others)
  - How networking is configured (ifconfig/ip: completely different per OS)
  - Package management (completely different per OS)
  - Init system (SysV init, BSD rc, systemd - not POSIX)

1991: Linux (Torvalds)
  Written to be POSIX-compatible (not to implement AT&T Unix)
  Legal advantage: no AT&T copyright, written from scratch
  Implements POSIX interfaces + Linux extensions
  
1994: USL (Unix System Labs, AT&T) sues BSDi (BSD/OS vendor)
  Claims: BSD Unix contains AT&T copyrighted code
  Resolution (1994): 3 files removed from 4.4BSD, lawsuit settled
  Impact: Linux unaffected (was already rewritten clean)
  POSIX proved its value: Linux didn't need to copy AT&T code
  to provide the same interfaces - POSIX documented the interface

CURRENT POSIX STATUS (POSIX.1-2017):
  Formally: IEEE Std 1003.1-2017 = The Open Group Base Specifications Issue 7
  Also called: SUSv4 (Single Unix Specification v4)
  Latest version: 2018 edition
  
  Combines:
  Base Definitions (XBD): headers, constants, types
  System Interfaces (XSH): functions (open, read, pthread_*, etc.)
  Shell and Utilities (XCU): sh, awk, sed, grep, ls, find, etc.
  Rationale (informative): why decisions were made

WHAT POSIX DOES NOT DEFINE (Linux-specific extensions):

1. epoll:
   POSIX has: select() and poll()
   Problem: select/poll: O(N) scan of all file descriptors per call
   N = 10,000 connections -> 10,000 fd checks per event = slow
   Linux solved with: epoll (event-driven, O(1) per ready fd)
   Similar solutions: kqueue (macOS/FreeBSD), IOCP (Windows)
   POSIX: still only has select/poll (no standardized scalable I/O)
   Consequence: every high-performance event loop uses OS-specific code
   libuv (Node.js): wraps epoll/kqueue/IOCP behind unified API
   
2. signalfd, eventfd, timerfd:
   POSIX signals: asynchronous, unsafe to call most functions in handler
   Linux unified signals into file descriptors:
   signalfd: read signals as structured data (vs. signal handler callbacks)
   eventfd: user-space counter as file descriptor (efficient wakeup)
   timerfd: timer expiration as file descriptor read
   Benefit: all events unified into epoll/select model (everything is a fd)
   Inspired by: Plan 9 "everything is a file" philosophy

3. inotify:
   POSIX has: no standard for filesystem event monitoring
   Linux has: inotify (watch a directory, get events for file changes)
   macOS has: kqueue/FSEvents (different API)
   Windows has: ReadDirectoryChangesW (different API)
   Consequence: tools like watchman, filesystem-event-based build systems
   (webpack --watch, jest --watchAll) use OS-specific code or abstraction

4. Linux namespaces and cgroups:
   Not in POSIX at all
   Container technology that Linux invented
   No POSIX equivalent

THE PORTABILITY SPECTRUM:

Level 1: Maximum portability (POSIX only)
  #define _POSIX_C_SOURCE 200809L (not _GNU_SOURCE)
  Use only: open/read/write/close, fork/exec/wait, select/poll
  Works on: Linux, macOS, FreeBSD, Solaris, AIX, HP-UX
  Missing: epoll (use poll instead), inotify, eventfd
  
Level 2: Linux + macOS (common server + developer platforms)
  Use epoll on Linux, kqueue on macOS (compile-time ifdef)
  Use inotify on Linux, kqueue on macOS (compile-time ifdef)
  Works on: all modern server platforms (Linux) + macOS for development
  
Level 3: Linux-specific (maximum performance)
  Use all Linux extensions freely
  Don't worry about portability
  Works on: Linux only
  Redis approach: Linux-optimized, macOS support "best effort"
```

---

### Thought Experiment

The epoll vs select performance difference - why POSIX standards lag:

```bash
# === Why epoll exists and why POSIX doesn't have it ===

# POSIX-standard: select() for I/O multiplexing
# Works on ALL POSIX systems

# BAD for scale: select() with 10,000 connections:
# 1. Must specify interest set every call:
#    fd_set readfds;
#    FD_ZERO(&readfds);
#    for (int i = 0; i < 10000; i++) FD_SET(fds[i], &readfds); // O(N)!
# 2. Kernel scans ALL fds in readfds: O(N) work per call
# 3. Maximum: typically 1024 fds (FD_SETSIZE = 1024 on many systems)
# 4. Must rebuild fd_set after each call (kernel modifies it)
# Total: O(N^2) for 10,000 connections

# Linux-specific: epoll - O(1) per ready event
# 1. Create once:
#    int epfd = epoll_create1(0);
# 2. Register interest once per connection (not per call):
#    epoll_ctl(epfd, EPOLL_CTL_ADD, client_fd, &event);
# 3. Wait - kernel notifies only READY fds:
#    int n = epoll_wait(epfd, events, MAX_EVENTS, -1);
# 4. Process only ready events: O(ready) not O(total)
# Total: O(1) per ready event, regardless of total connections

# Benchmark: nginx can handle 1M concurrent connections with epoll
# With select: maybe 1,000 before performance collapses

# Why POSIX hasn't standardized epoll:
# 1. POSIX standardizes what ALREADY EXISTS on multiple platforms
# 2. epoll (Linux), kqueue (macOS/FreeBSD), IOCP (Windows) all different
# 3. Standardizing requires consensus from all OS vendors
# 4. Different semantics: epoll level-triggered vs edge-triggered vs kqueue
# 5. Politics: no single "winner" that all agree to standardize

# How portable libraries handle this:
cat libuv_uv.c
# ifdef __linux__
#   include "unix/linux.c"  // uses epoll
# elif defined(__APPLE__)
#   include "unix/kqueue.c" // uses kqueue
# elif defined(__FreeBSD__)
#   include "unix/kqueue.c" // uses kqueue
# endif
# Node.js: this is why Node.js is portable - libuv handles OS differences

# === macOS POSIX gotchas ===

# macOS is officially POSIX certified (Linux is not!)
# But macOS has subtle differences that break Linux code:

# Case-insensitive filesystem (HFS+/APFS default):
touch /tmp/Test.txt
touch /tmp/test.txt   # on macOS: same file! On Linux: different files!
# Bug: code that creates and reads "Config.json" might fail on macOS
# if another file "config.json" already exists

# Verify behavior:
python3 -c "
import os
os.makedirs('/tmp/test_case', exist_ok=True)
with open('/tmp/test_case/Test.txt', 'w') as f: f.write('upper')
with open('/tmp/test_case/test.txt', 'w') as f: f.write('lower')
import glob
files = glob.glob('/tmp/test_case/*.txt')
print(f'Linux: 2 files. macOS: {len(files)} file(s)')
"

# Different socket options:
# macOS: SO_NOSIGPIPE socket option
# Linux: MSG_NOSIGNAL send flag (different mechanism, same purpose)
# Portable code: handle EPIPE/SIGPIPE differently per platform

# Signal behavior:
# SIGPIPE: Linux default: terminate process
# macOS: same default, but different defaults for some signals
# BSD vs Linux socket option semantics: subtle differences
```

---

### Mental Model / Analogy

```
POSIX = USB standard for operating systems

USB standard:
  Defines: connector shape, electrical specs, protocol
  Any USB device: works with any USB port on any computer
  Manufacturer: can add proprietary extensions (USB-C Thunderbolt)
  but must still support standard USB
  
  No vendor owns "USB" - it's a consortium standard
  Legal protection: implement USB, not someone's proprietary interface

POSIX = USB for OS interfaces:
  Defines: system call signatures, return values, error codes
  Any POSIX program: works with any POSIX OS
  OS vendor: can add proprietary extensions (Linux: epoll, Android: Binder)
  but must still support standard POSIX
  
  IEEE owns POSIX - it's a standards body
  Linux: implement POSIX interfaces without using AT&T code
  Legal protection: SCO lawsuit (2003): Linux code was defensible
  because it implemented the documented POSIX interface

USB versions parallel:
  USB 1.0 (1996)   = POSIX.1 (1988): basic interface
  USB 2.0 (2000)   = POSIX.1-2001: threads, real-time clocks, etc.
  USB 3.0 (2008)   = POSIX.1-2008: new async signal safe functions
  USB 4.0 (2019)   = POSIX.1-2017: current version
  Thunderbolt ext. = _GNU_SOURCE: Linux-specific epoll, inotify etc.

"macOS is POSIX certified, Linux is not" explained:
  USB compliance testing: send device to USB Implementers Forum, pay fee
  Certified = passed the test suite
  
  macOS: Apple paid for Unix certification from The Open Group
  Linux: nobody pays for official certification (open source project)
  
  In practice:
  macOS: officially certified Unix, case-insensitive filesystem (POSIX violation?)
  Linux: not certified, but passes more POSIX tests than many certified systems
  
  The certification is a BUSINESS decision, not a technical one.
  "POSIX certified" -> The Open Group certified = expensive and political
  "POSIX compatible" -> runs POSIX programs = practical reality

glibc feature test macros:
  _POSIX_C_SOURCE 200809L  = POSIX.1-2008 only (most portable)
  _XOPEN_SOURCE 700        = SUS/XSI v7 (POSIX + X/Open extensions)
  _GNU_SOURCE              = Everything Linux provides
  
  Think of them as:
  _POSIX_C_SOURCE = "I want the standard USB interface only"
  _XOPEN_SOURCE   = "I want USB + common vendor extensions"
  _GNU_SOURCE     = "I want Thunderbolt (all Linux features)"
```

---

### Gradual Depth - Five Levels

**Level 1:**
What POSIX is (IEEE standard for Unix-compatible OS interface). That Linux
is compatible but not officially certified. The major POSIX system calls (open,
read, write, fork, exec, pthread). Why portability between Linux, macOS, FreeBSD
works. What `_GNU_SOURCE` enables.

**Level 2:**
The POSIX I/O model: select and poll for I/O multiplexing. Why Linux added epoll
(scalability). Key Linux extensions: epoll, inotify, signalfd, eventfd, timerfd.
POSIX threads (pthreads): pthread_create, mutex, condition variables, barriers.
Android's Bionic libc and what it removes/changes. The _POSIX_VERSION getconf check.

**Level 3:**
POSIX.1-2017 structure: XBD, XSH, XCU. The X/Open System Interface (XSI)
extensions. POSIX vs SUS distinction. Signal semantics: POSIX signals, sigaction
vs signal, SA_RESTART for EINTR handling. POSIX async I/O (aio_read/aio_write):
why it's inferior to io_uring. Mandatory vs advisory file locking (POSIX fcntl
locks are advisory). pthread cancelation and why Android removed it.

**Level 4:**
POSIX compliance testing: The Open Group's test suite. Why Linux developers
care about POSIX bug reports. EINTR and the "slow restart" pattern. POSIX clock
types: CLOCK_REALTIME vs CLOCK_MONOTONIC (critical for measuring elapsed time).
POSIX shared memory (shm_open vs old shmget/shmat). Robust mutexes (PTHREAD_
MUTEX_ROBUST): survive process crash while holding mutex. POSIX spawn (posix_spawn):
fork+exec without full address space copy overhead.

**Level 5:**
The Austin Group (POSIX + Single Unix spec maintainer): how new functions get
standardized. Why select(2) has "undefined behavior" for fds > FD_SETSIZE.
The POSIX filesystem hierarchy specification overlap with FHS (Filesystem
Hierarchy Standard). musl libc vs glibc: different POSIX compliance levels.
Alpine Linux uses musl: subtle incompatibilities with glibc-dependent software.
The POSIX message queue (mq_open/mq_send/mq_receive): rarely used but POSIX
standardized. Real-time signals (SIGRTMIN..SIGRTMAX): guaranteed queuing, not
available in POSIX base (XSI extension).

---

### Code Example

**BAD - Linux-only code presented as portable without markers:**
```c
/* BAD: Linux-specific code without portability markers or comments */
/* This will COMPILE on Linux but fail on macOS/FreeBSD */

#include <sys/epoll.h>   /* Linux only! */
#include <sys/inotify.h> /* Linux only! */
#include <sys/eventfd.h> /* Linux only! */

/* This code silently fails on non-Linux systems */
int bad_event_loop(int listen_fd) {
    /* epoll: Linux-specific, not POSIX */
    int epfd = epoll_create1(EPOLL_CLOEXEC);
    struct epoll_event ev = {
        .events = EPOLLIN,
        .data.fd = listen_fd
    };
    epoll_ctl(epfd, EPOLL_CTL_ADD, listen_fd, &ev);
    
    /* No portability documentation, no fallback */
    while (1) {
        struct epoll_event events[64];
        int n = epoll_wait(epfd, events, 64, -1);
        /* process events... */
    }
    return 0;
}
```

```c
/* GOOD: Portable I/O multiplexing with Linux optimization */
/* Works on: Linux (epoll), macOS (kqueue), FreeBSD (kqueue) */
/* Degrades to: poll() on any POSIX system */

#include <unistd.h>   /* POSIX: read, write, close */
#include <fcntl.h>    /* POSIX: open, fcntl, O_* flags */
#include <poll.h>     /* POSIX: poll() - always available */
#include <string.h>
#include <errno.h>

/* PORTABLE: POSIX poll-based event wait */
/* Performance: O(N) per call - acceptable up to ~1000 connections */
int portable_wait_for_event(int *fds, int nfds, int timeout_ms) {
    struct pollfd pfds[1024]; /* or malloc if nfds > 1024 */
    for (int i = 0; i < nfds; i++) {
        pfds[i].fd = fds[i];
        pfds[i].events = POLLIN;
    }
    
    int ret;
    do {
        ret = poll(pfds, nfds, timeout_ms);
    } while (ret == -1 && errno == EINTR); /* retry on signal interrupt */
    /* ^^ POSIX: poll can return EINTR (interrupted by signal) */
    /* always retry unless it's a real error */
    
    return ret;
}

/* LINUX OPTIMIZED: epoll-based (O(1) per ready event) */
/* Enable only on Linux: */
#ifdef __linux__
#include <sys/epoll.h>

int create_epoll_fd(void) {
    return epoll_create1(EPOLL_CLOEXEC);
    /* EPOLL_CLOEXEC: auto-close on exec (POSIX O_CLOEXEC equivalent) */
}

int epoll_add(int epfd, int fd, uint32_t events) {
    struct epoll_event ev;
    ev.events = events;   /* EPOLLIN, EPOLLOUT, EPOLLERR, EPOLLET */
    ev.data.fd = fd;
    return epoll_ctl(epfd, EPOLL_CTL_ADD, fd, &ev);
}
#endif

/* PORTABLE SIGNAL HANDLING: use sigaction, not signal() */
/* signal() behavior: POSIX only specifies it resets to SIG_DFL */
/* sigaction(): portable, reliable, SA_RESTART handles EINTR */

#include <signal.h>

static volatile sig_atomic_t got_sigterm = 0;

void setup_signal_handling(void) {
    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));
    sa.sa_handler = (void (*)(int))({ 
        /* handler: only async-signal-safe functions allowed! */
        /* POSIX: only ~25 functions are async-signal-safe */
        /* write(), _exit(), kill(), signal(), etc. */
        /* NOT: printf, malloc, mutex functions */
    });
    sigemptyset(&sa.sa_mask);   /* don't block additional signals */
    sa.sa_flags = SA_RESTART;   /* restart syscalls interrupted by signal */
    sigaction(SIGTERM, &sa, NULL);  /* POSIX: reliable signal handling */
    sigaction(SIGINT, &sa, NULL);
}

/* POSIX CLOCK USAGE: always use CLOCK_MONOTONIC for elapsed time */
#include <time.h>

double get_elapsed_seconds(struct timespec *start) {
    struct timespec now;
    /* CLOCK_MONOTONIC: not affected by system time changes (NTP, etc.) */
    /* Use for: measuring elapsed time, timeouts, performance measurement */
    /* CLOCK_REALTIME: wall clock, CAN jump (NTP, leap second) */
    /* Never use CLOCK_REALTIME for elapsed time! */
    clock_gettime(CLOCK_MONOTONIC, &now);
    
    return (now.tv_sec - start->tv_sec) +
           (now.tv_nsec - start->tv_nsec) / 1e9;
}
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "Linux is POSIX certified" | Linux is NOT officially certified by The Open Group as a POSIX/Unix system. The Open Group's "Unix" certification requires paying fees, submitting to testing, and ongoing licensing. Linux is maintained by thousands of individuals and the Linux Foundation - there is no legal entity that pays for "Linux" as a product to be certified. In practice: Linux passes most POSIX conformance tests and is POSIX-compatible in all ways that matter for software development. Many Linux programs assume POSIX compliance and they work correctly. The distinction matters in: government procurement (some contracts require "certified Unix"), legal arguments (SCO lawsuit era: "is Linux Unix?"), and academic pedantry. For daily development: "POSIX-compatible Linux" behaves as expected. Ironically: macOS is a certified Unix (Apple pays) but has a case-insensitive default filesystem - a significant behavioral difference from true POSIX filesystem semantics. |
| "POSIX programs are automatically portable across all Unix systems" | POSIX defines interfaces but not ALL behaviors. Subtle differences cause portability issues: (1) Signal semantics: POSIX says signal() behavior is "implementation-defined" after delivery. SA_RESTART flag for sigaction(): needed on Linux, optional on macOS, behavior slightly different. (2) Filesystem semantics: macOS default filesystem (APFS) is case-insensitive. Code that creates "Config.json" and later opens "config.json" works differently on Linux vs macOS. (3) Thread stack size defaults: Linux default ~8MB, macOS 512KB (iOS: 512KB). Code that creates threads without explicit stack sizes may crash on macOS. (4) printf format strings: %q, %Z are Linux/BSD extensions, not POSIX. (5) getaddrinfo/getnameinfo: POSIX, but AI_ADDRCONFIG behavior differs. (6) errno thread safety: POSIX guarantees errno is per-thread, but older code may assume single-threaded errno. True cross-platform POSIX code requires: build system tests (autoconf), careful signal handling, explicit sizes for stack and buffers. |
| "Android is a standard Linux system" | Android uses the Linux kernel but has a significantly different user-space from standard Linux. Key differences: (1) libc: Bionic instead of glibc. Missing: pthread_cancel, full locale support, some glibc extensions. Different threading implementation. (2) No standard FHS layout: /usr, /lib, /bin don't exist in traditional locations. System directories: /system, /vendor, /apex. (3) No shell by default: minimal /system/bin/sh. (4) Different process model: Android apps are Java/Kotlin in the ART runtime (not native processes directly). (5) Security model: SELinux mandatory, no Unix-style root access for apps, capability-based permissions, seccomp filters on all apps. (6) IPC: Binder (not POSIX pipes/sockets/shm for app-to-app IPC). A program compiled for standard Linux (glibc, FHS paths, standard libc) will NOT run on Android without recompilation against Bionic and path adjustments. The Linux kernel underneath: same (GPL v2 kernel), but user space: fundamentally different. |
| "All Linux distributions use glibc" | Most general-purpose Linux distributions use glibc, but several use alternative C libraries: (1) Alpine Linux uses musl libc (a POSIX-compliant, lightweight C library). Alpine is widely used in Docker containers for small image sizes. musl differences from glibc: no `backtrace()`, no `printf_chk`, different behavior for some locale functions, `getaddrinfo()` subtle differences. Code compiled against glibc does NOT run on musl-based Alpine (binary incompatibility). This is why Docker images built on Ubuntu don't work when changed to alpine base. (2) Android: Bionic libc (as described above). (3) Embedded Linux: uclibc-ng (ultra-minimal, missing many GNU extensions). (4) NixOS: can use glibc with patched prefix paths. Consequence for containerized software: if you build on Ubuntu and run on Alpine, glibc-linked binaries fail. Solution: either use static linking (bakes in glibc), use musl for compilation, or use Alpine images that include glibc compatibility layer. |

---

### Failure Modes & Diagnosis

```bash
# === EINTR: the most common POSIX signal portability bug ===

# Bug: code that doesn't handle EINTR (interrupted system call)
# read() can return -1 with errno=EINTR if signal arrives during call
# If you don't retry: your program silently drops data or returns error

# BAD: no EINTR handling
ssize_t bad_read(int fd, void *buf, size_t count) {
    return read(fd, buf, count);  # BAD: may return -1 + EINTR
}

# GOOD: EINTR retry loop (POSIX requirement for robustness)
ssize_t safe_read(int fd, void *buf, size_t count) {
    ssize_t n;
    do {
        n = read(fd, buf, count);
    } while (n == -1 && errno == EINTR);  # retry if interrupted by signal
    return n;
}

# Check if a running process is hitting EINTR frequently:
strace -p 12345 -e trace=read,write 2>&1 | grep EINTR
# read(3, ...) = -1 EINTR (Interrupted system call)
# Frequent EINTR: signals are arriving often (profiling? alarms?)

# === musl vs glibc: Alpine Docker failure ===

# Build on Ubuntu:
FROM ubuntu:22.04 AS build
RUN apt install -y libssl-dev && gcc -o myapp main.c -lssl

# Try to run on Alpine:
FROM alpine:3.18
COPY --from=build /myapp /myapp
RUN /myapp
# sh: /myapp: not found  <- POSIX error for "dynamic library not found"
# Even though the file EXISTS! It's a missing glibc library error.

# Diagnosis:
ldd myapp
# linux-vdso.so.1 (0x...)
# libssl.so.3 => /lib/x86_64-linux-gnu/libssl.so.3
# libcrypto.so.3 => /lib/x86_64-linux-gnu/libcrypto.so.3
# libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6  <- glibc!
# Alpine has musl, not glibc.so.6

# Fix option 1: static link (embed all libraries):
gcc -o myapp main.c -static -lssl -lcrypto
# Larger binary, but no runtime dependencies

# Fix option 2: build on Alpine too:
FROM alpine:3.18 AS build
RUN apk add gcc openssl-dev && gcc -o myapp main.c -lssl

# === POSIX clock pitfall ===

# Bug: using CLOCK_REALTIME for elapsed time measurement
struct timespec start;
clock_gettime(CLOCK_REALTIME, &start);
/* ... operation ... */
struct timespec end;
clock_gettime(CLOCK_REALTIME, &end);
# Difference = end - start
# BUG: NTP update during operation: clock can JUMP BACKWARD!
# Result: negative elapsed time, incorrect timeout

# Fix: always use CLOCK_MONOTONIC for elapsed time:
clock_gettime(CLOCK_MONOTONIC, &start);  # GOOD: never goes backward!
```

---

### Related Keywords

**Foundational:**
LNX-001 (Linux overview), LNX-111 (kernel architecture)

**Builds on this:**
LNX-117 (namespace pattern), LNX-119 (Unix philosophy)

**Related:**
LNX-111 (kernel architecture), LNX-119 (Unix philosophy), LNX-121 (permission models)

---

### Quick Reference Card

| Item | POSIX standard | Linux extension |
|------|---------------|-----------------|
| I/O multiplex | select, poll | epoll |
| File watch | none | inotify |
| Signal as fd | none | signalfd |
| Counter as fd | none | eventfd |
| Timer as fd | none | timerfd |
| C library | POSIX libc | glibc (Linux) |
| Android libc | - | Bionic |
| Alpine libc | musl | - |

**3 things to remember:**
1. Linux is POSIX-compatible (runs POSIX programs correctly) but NOT officially POSIX certified (no fee paid to The Open Group). This is a BUSINESS distinction, not a technical one. macOS IS certified but has case-insensitive filesystem - arguably less POSIX-compliant in practice.
2. `_GNU_SOURCE` enables Linux-specific extensions: epoll, inotify, signalfd, eventfd, timerfd. Without it: only POSIX interfaces visible. ALWAYS use `_GNU_SOURCE` for Linux-only code; use `_POSIX_C_SOURCE 200809L` for portable code.
3. Android uses Bionic libc (not glibc): missing pthread_cancel, different locale support. Alpine uses musl libc: glibc-compiled binaries will NOT run on Alpine (binary incompatibility). CLOCK_MONOTONIC for elapsed time (not CLOCK_REALTIME: NTP can make it jump backward).

---

### Transferable Wisdom

The POSIX standard approach (standardize the common interface, allow
implementation freedom) is the same as: JDBC (Java Database Connectivity):
standardizes SQL interface, allows MySQL/PostgreSQL/Oracle implementations;
JSR (Java Specification Request): standardizes JVM behavior, allows HotSpot/
GraalVM implementations; W3C/WHATWG HTML standards: specify browser behavior,
allow Chrome/Firefox implementations. The Linux "POSIX-compatible but not
certified" status is the same as: many open-source implementations of standards
(Apache's Harmony JVM: POSIX-like for Java, not official), Chrome's JavaScript
V8 (implements ECMAScript spec but adds extensions like V8-specific APIs).
The musl vs glibc portability issue in Alpine containers is the same as: Python
cffi vs ctypes compatibility (different binary interface), .NET Standard vs
.NET Framework (code targeting .NET Standard runs on all; targeting Framework-
specific: Windows only), Node.js LTS vs Current (LTS: guaranteed API stability;
Current: may have breaking changes). The epoll/kqueue/IOCP fragmentation
(three different APIs for scalable I/O on three OS families) is why abstraction
libraries exist: libuv (Node.js), Boost.Asio, Java NIO. This is the standard
abstraction vs performance trade-off: direct OS API = maximum performance,
cross-platform library = portability with some overhead.

---

### The Surprising Truth

POSIX defines that the `signal()` function's behavior after delivery is
"implementation-defined" - meaning each OS can do whatever it wants with the
disposition after a signal fires. This seemingly small ambiguity led to years
of real bugs: on System V Unix (AT&T), `signal()` resets to `SIG_DFL` (default)
after delivery - so a signal handler calling `signal()` to re-install itself
had a race condition (signal could arrive between the reset and reinstall).
BSD Unix kept the handler installed (reliable signals). Linux's default
`signal()` follows the System V behavior (resets handler after delivery).

The fix (standardized in POSIX.1-2001): `sigaction()` with `SA_RESTART` flag.
But the old `signal()` function remained in POSIX for backward compatibility,
with its implementation-defined behavior preserved.

The lesson: standards bodies are extremely reluctant to fix even clearly broken
API behavior if there's existing code that depends on it. The "never break
existing software" constraint applies to standards, not just kernels. Every
"implementation-defined behavior" in a standard is a historical compromise
between competing implementation needs.

---

### Mastery Checklist

- [ ] Understands the distinction between POSIX-certified (macOS: yes) and POSIX-compatible (Linux: yes, but not certified)
- [ ] Knows key Linux extensions beyond POSIX: epoll, inotify, signalfd, eventfd, timerfd
- [ ] Understands when to use `_GNU_SOURCE` vs `_POSIX_C_SOURCE` for include guards
- [ ] Knows Android Bionic and Alpine musl differences from glibc (binary incompatibility)
- [ ] Uses CLOCK_MONOTONIC for elapsed time measurement (not CLOCK_REALTIME)

---

### Think About This

1. POSIX standardized select() and poll() for I/O multiplexing in the 1980s.
   30 years later, every high-performance OS has invented its own solution
   (epoll, kqueue, IOCP) because select/poll don't scale. POSIX still has
   not standardized a scalable alternative. Why? What would it take to get
   epoll, kqueue, and IOCP unified into a POSIX standard? Who controls the
   standards process? What incentives do OS vendors have to standardize vs.
   maintain OS-specific APIs? What would a good cross-platform async I/O
   standard look like given that we now know epoll's event model (file
   descriptor-based)?

2. Alpine Linux's use of musl libc causes frequent Docker production issues:
   binaries compiled against glibc don't run on Alpine. Alpine base images
   are 5MB vs Ubuntu's 70MB. The tradeoff is real: size matters for container
   startup time and image storage. Design a strategy for a team that wants
   Alpine's size benefits but currently builds all code against glibc.
   Options: (1) static linking, (2) multi-stage Docker builds on Alpine,
   (3) distroless images (google/distroless), (4) "slim" Debian/Ubuntu images.
   Analyze the trade-offs. What makes glibc binaries incompatible with musl
   at the binary level (hint: symbol versioning)?

3. Android's Bionic libc removes `pthread_cancel()`. The reason: cancellation
   points are complex, error-prone, and resource-leak-prone in typical Android
   app code. This is a deliberate simplification. Google made a similar decision
   when designing Go's goroutines: no goroutine cancellation function (instead:
   context.Context). Is removing pthread_cancel from Android correct? Analyze:
   What problems does pthread_cancel solve? What problems does it create?
   What does the "context propagation" pattern (Go's context.Context, Java's
   Future.cancel()) provide that pthread_cancel doesn't? Is pthread_cancel in
   POSIX a design mistake that was simply too popular to remove from the standard?

---

### Interview Deep-Dive

**Foundational:**
Q: What is POSIX and why does it matter for Linux development?
A: POSIX IN ONE SENTENCE: POSIX (IEEE Std 1003.1) is the standard defining what functions a Unix-compatible operating system must provide - the contract between the OS and programs written to run on it. WHY IT WAS CREATED: 1980s: dozens of Unix variants (AT&T System V, BSD, SunOS, HP-UX, AIX) each with slightly different APIs. A C program written for SunOS might not compile on HP-UX. POSIX (1988): standardized the interface. Write to POSIX, compile on any conforming Unix. WHAT IT DEFINES: System calls (open/read/write/close/fork/exec/wait/mmap), POSIX threads (pthread_create, mutexes, condition variables), signals (sigaction, kill), file permissions (user/group/other rwx), utilities (sh, awk, sed, grep, ls), clocks (CLOCK_MONOTONIC, CLOCK_REALTIME). WHY LINUX IS POSIX COMPATIBLE: Torvalds wrote Linux to be Unix-compatible (POSIX-compatible) from scratch - legal advantage (no AT&T code, implemented documented interfaces). Programs written for Solaris, macOS, FreeBSD compile and run on Linux with minor changes (or none). WHY LINUX IS NOT CERTIFIED: The Open Group charges fees for "Unix" certification. Linux is developed by thousands of individuals, no single entity pays for certification. Doesn't matter in practice. LINUX EXTENSIONS BEYOND POSIX: epoll (scalable I/O: POSIX only has select/poll, which don't scale past ~1000 connections), inotify (filesystem events: no POSIX equivalent), signalfd/eventfd/timerfd (unify events as file descriptors), namespaces and cgroups (containers: no POSIX equivalent). Enable with: `#define _GNU_SOURCE` before includes. WHY KNOWING THIS MATTERS: Cross-platform code: know which functions are portable (POSIX) vs Linux-only (GNU). Container base images: Alpine uses musl (not glibc), glibc-compiled code won't run. Android uses Bionic, missing some POSIX functions. Every high-performance server framework (nginx, Node.js, Redis) uses Linux-specific extensions and falls back to POSIX on other platforms.

**Expert:**
Q: Explain why epoll exists and why POSIX still only standardizes select() and poll().
A: THE SCALABILITY PROBLEM WITH SELECT/POLL: select() and poll() require the caller to provide the complete set of file descriptors to monitor on EVERY call. select(): O(N) bit scan where N = highest fd number. Max fds: FD_SETSIZE (typically 1024). poll(): O(N) linear scan of pollfd array. Must rebuild array every call. No max fd limit but still O(N). For 10,000 connections: every call to select/poll must scan 10,000 file descriptors, even if only 1 is ready. At 100K events/sec: 10 BILLION fd-state checks per second. Completely unsaleable. THE EPOLL SOLUTION (Linux 2.6, 2002, Davide Libenzi): epoll_create(): create kernel-side interest set (O(1)). epoll_ctl(ADD/MOD/DEL): modify interest set once per connection change (O(1)). epoll_wait(): kernel wakes caller ONLY when something is READY. Returns only ready fds. O(1) for the monitoring, O(ready) for processing. 10,000 connections, 1 active: epoll_wait returns 1 event. select: must scan 10,000. Design: kernel maintains a red-black tree of monitored fds + a list of ready fds. When fd becomes ready (hardware interrupt -> driver -> network stack): kernel adds to ready list. epoll_wait: just returns the ready list. LEVEL-TRIGGERED vs EDGE-TRIGGERED: Level-triggered (default): keep notifying while fd is readable. Edge-triggered (EPOLLET): notify ONCE when fd transitions to readable. ET: higher performance, harder to use correctly (must read until EAGAIN). WHY POSIX HASN'T STANDARDIZED EPOLL: (1) Standards require consensus from multiple OS implementors. epoll (Linux), kqueue (macOS+FreeBSD), IOCP (Windows) have different designs, different event models. (2) kqueue has features epoll doesn't: kernel events (process events, timers, signals all via kqueue). (3) IOCP (Windows completion ports) uses completion model, not readiness model. Incompatible concepts. (4) POSIX standards process is slow: standardizing requires 5+ years of committee work. (5) Vendors benefit from platform-specific APIs (differentiation, developer lock-in). PRACTICAL CONSEQUENCE: Every high-performance event framework has an OS abstraction layer: libuv (Node.js): epoll on Linux, kqueue on macOS, IOCP on Windows. Java NIO: uses platform-specific code via JNI. Netty (Java): same. Boost.Asio (C++): same. The epoll/kqueue/IOCP problem is solved by libraries, not standards.
