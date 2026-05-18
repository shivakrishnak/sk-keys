---
id: LNX-007
title: Linux File System Hierarchy (FHS)
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★☆☆
depends_on: LNX-006
used_by: LNX-008, LNX-044
related: LNX-008, LNX-046, LNX-049
tags: [filesystem, FHS, directory-structure, /etc, /var, /proc, /usr]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 7
permalink: /technical-mastery/lnx/file-system-hierarchy/
---

## TL;DR

The Filesystem Hierarchy Standard (FHS) defines where things
live on Linux: /bin for essential binaries, /etc for configs,
/var for variable data (logs), /home for user files, /proc
and /sys for kernel info. Knowing this map means you can find
any file without guessing. When a Java app can't find a config
file or log directory, you'll know exactly where to look.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-007 |
| **Difficulty** | ★☆☆ Foundational |
| **Category** | Linux |
| **Tags** | FHS, filesystem hierarchy, directory structure, Linux directories |
| **Prerequisites** | LNX-006 |

---

### The Problem This Solves

Without a standard filesystem layout, every Unix system was
different: logs might be in /logs, /var/log, or /usr/logs
depending on who configured it. Programs couldn't find each
other, scripts weren't portable. The FHS (Filesystem Hierarchy
Standard) standardized the layout so programs know where to
look for config files, libraries, binaries, and temporary data.

---

### Textbook Definition

The **Filesystem Hierarchy Standard (FHS)** is a reference
describing the conventions for the directory structure of Unix
and Linux operating systems. Maintained by the Linux Foundation.
Current version: 3.0 (2015). Defines the purpose and contents
of each directory under root (/).

---

### Understand It in 30 Seconds

```
/                   Root of everything
├── bin/            Essential binaries (ls, cp, cat, bash)
├── sbin/           System binaries (fdisk, ifconfig, mount)
├── etc/            Configuration files (nginx.conf, hosts)
├── home/           User home directories (/home/alice)
├── root/           Root user's home directory
├── var/            Variable data (logs, caches, databases)
│   ├── log/        Log files (/var/log/syslog)
│   └── lib/        Application data (databases)
├── tmp/            Temporary files (cleared on reboot)
├── usr/            User programs and data
│   ├── bin/        Most installed programs (java, python, git)
│   ├── lib/        Libraries for /usr/bin programs
│   └── local/      Locally installed software (not from package mgr)
├── lib/            Essential libraries (libc, kernel modules)
├── proc/           Virtual: kernel/process info (in memory)
├── sys/            Virtual: hardware/device info (in memory)
├── dev/            Device files (/dev/sda, /dev/null)
├── mnt/            Mount point for temporary mounts
├── opt/            Optional add-on software
└── srv/            Data for services (web root, FTP)
```

---

### First Principles

**Why a hierarchy?**
Early Unix: small disk, few programs. One flat directory worked.
As systems grew: need to organize. Hierarchy (tree structure)
provides natural namespacing. `/etc/nginx/nginx.conf` vs just
`nginx.conf`: context is clear from path.

**The key distinction: static vs variable data:**
```
/bin, /etc, /lib, /usr: relatively static (change during updates)
  -> Can be on read-only filesystem
  -> Can be shared across multiple machines (NFS)
  -> Containers: these come from the image (read-only layers)
  
/var, /tmp, /run: variable data (changes constantly)
  -> Must be writable
  -> Cannot be shared read-only
  -> Containers: these come from writable layers or mounts
```

**The /proc and /sys difference:**
```
Regular files: data stored on disk
/proc, /sys: data generated on-demand by kernel
  cat /proc/meminfo  -> kernel reads physical RAM, generates text
  cat /sys/class/net/eth0/speed -> kernel queries NIC, returns value
  Writing to /proc or /sys: kernel configuration
    echo 1 > /proc/sys/net/ipv4/ip_forward  # enables IP forwarding
```

---

### Thought Experiment

Imagine a large company office building:
- Reception (/) = entry point to everything
- Cafeteria (/usr/bin) = most tools people use daily
- Facilities closet (/sbin) = tools only building staff use
- HR files (/etc) = company policies and configs
- Mailroom (/var) = things that change daily (incoming mail=logs)
- Coat closet (/tmp) = temporary storage, cleared nightly
- Basement (/proc) = hidden monitoring room: real-time data about
  the building (how many people, temperature, power usage) - you
  can read these meters but they don't store files

You always know where to look: got a log? /var/log. Got a config?
/etc. Got a program? /usr/bin or /usr/local/bin.

---

### Mental Model / Analogy

The filesystem hierarchy is like a **city map with districts:**

```
Downtown core (/bin, /sbin):
  Essential services; available even in emergency
  Like: police, fire station (needed in rescue mode)
  
Business district (/usr):
  Most of the software and libraries people actually use
  /usr/bin: shops open for everyone
  /usr/sbin: government offices (admin only)
  /usr/lib: warehouse district (libraries for programs)
  /usr/local: locally-built businesses (not from city plan)
  
Residential area (/home):
  Personal spaces for each user
  Each resident has their own lot: /home/alice, /home/bob
  
City Hall (/etc):
  All the rules and configurations
  /etc/nginx: traffic department config
  /etc/cron.d: scheduled city maintenance
  /etc/hosts: address book
  
Newspaper archive (/var/log):
  Everything that happened, recorded daily
  Grows over time; needs to be cleaned periodically
  
Real-time dashboard (/proc, /sys):
  Live stats about the city: traffic, power, population
  Not stored anywhere; generated on demand
```

---

### Gradual Depth - Five Levels

**Level 1:**
/etc = configs, /var/log = logs, /home = your files,
/tmp = temp files. Start there. That's enough to navigate
most Linux tasks.

**Level 2:**
/usr/bin = installed programs (java, nginx, git).
/usr/local/bin = programs you installed manually.
/proc/$PID = info about a process (look inside it).
/dev/null = black hole (redirect unwanted output here).

**Level 3:**
/etc/systemd/system/ = custom systemd service files.
/var/lib/ = application data (PostgreSQL data, Docker images).
/run/ = runtime data (PID files, sockets) - cleared each boot.
/lib/modules/$(uname -r)/ = kernel modules for current kernel.
Symlinks: /bin -> /usr/bin on modern distros (merger).

**Level 4:**
Container filesystem: layered (overlay filesystem). Base image
provides /usr, /etc, /lib. Writable layer on top for /var, /tmp,
/run. Volumes mount host filesystem at specific container paths.
/proc is namespace-scoped: container's /proc/1 = container init
process, not host's PID 1. /sys/fs/cgroup shows cgroup hierarchy.

**Level 5:**
FHS compliance tradeoffs: NixOS deliberately violates FHS (all
software in /nix/store; symlinks everywhere). Benefit: atomic
updates and rollback. Cost: non-standard paths; some software breaks.
Immutable root filesystems: / is read-only; only /var and /etc
are writable (via overlays). Used in Container-Optimized OS, Flatcar,
Bottlerocket. Prevents runtime tampering of base OS.

---

### Key Directories for Java Engineers

```
Where Java-related files live:

/usr/lib/jvm/           JDK installations (Debian/Ubuntu)
  java-17-openjdk-amd64/
  java-21-openjdk-amd64/

/usr/local/java/        Manual JDK installations
/opt/java/              Alternative manual location

/etc/systemd/system/    Custom service units for your app
  myapp.service

/var/log/               Application logs (if configured here)
  myapp/
    application.log
    error.log

/etc/myapp/             Application config files
  application.properties

/var/lib/myapp/         Application data directory
  data/
  uploads/

/tmp/                   JVM temp files (java.io.tmpdir)
  hsperfdata_user/      JVM performance data
  *.jfr                 JFR recordings

/proc/$PID/             Live info about running JVM
  status                 memory, state, threads
  fd/                    open file descriptors
  maps                   memory mappings
  cmdline                how java was invoked
  environ                environment variables
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "/tmp is for permanent-ish files" | /tmp is cleared on reboot (or periodically by systemd-tmpfiles). Use /var/lib/myapp for persistent data. |
| "/etc is only for system configs" | /etc is for ANY host-specific configuration, including your application config. `/etc/myapp/config.yml` is valid and conventional. |
| "/proc is a regular filesystem" | /proc is a virtual filesystem. Files in /proc don't exist on disk - they're generated by the kernel on read. Writing to some /proc files configures the kernel. |
| "All programs are in /bin or /usr/bin" | On modern distros, /bin is a symlink to /usr/bin. Programs you install from packages: /usr/bin. Manual installs: /usr/local/bin. Corporate software: /opt/company/bin. |
| "/home is where all config goes" | Per-user config goes in /home/user/.config (hidden directories). System-wide config goes in /etc. /home is not for system configs. |

---

### Failure Modes & Diagnosis

**Application writes logs to wrong location:**
```bash
# Java app writes to /tmp/myapp.log (bad: cleared on reboot)
# Should be: /var/log/myapp/myapp.log

# Check where logs actually are:
lsof -p $(pgrep -f myapp.jar) | grep log
# Shows: all open files by the process

# Fix in Spring Boot application.properties:
logging.file.path=/var/log/myapp
```

**Config file not found at startup:**
```bash
# Java app fails: ConfigFileNotFoundException
# Check the FHS-correct locations:
ls /etc/myapp/           # system config
ls $HOME/.myapp/         # user config
ls /opt/myapp/conf/      # vendor-style config

# Check where app is searching:
strace -e openat java -jar app.jar 2>&1 | grep "config\|conf"
# Shows every file open attempt - find the "ENOENT" (not found) ones
```

**Security: /tmp race condition (TOCTOU):**
```bash
# Creating temp files insecurely (vulnerable to symlink attacks):
tmpfile=/tmp/myapp-$RANDOM   # BAD: predictable, race condition

# Secure temp file creation:
tmpfile=$(mktemp /tmp/myapp.XXXXXX)  # atomic, unique, secure
# Or in Java: Files.createTempFile() uses mkstemp internally
```

---

### Related Keywords

**Foundational:**
LNX-006 (Terminal), LNX-008 (Files and Directories)

**Builds on this:**
LNX-044 (/etc Directory), LNX-046 (Filesystem Internals),
LNX-052 (/proc Filesystem), LNX-053 (/sys Filesystem)

**Related:**
LNX-031 (systemd), LNX-039 (Mounting Filesystems)

---

### Quick Reference Card

| Directory | Purpose |
|-----------|---------|
| /bin, /usr/bin | Essential and installed executables |
| /sbin, /usr/sbin | System administration executables |
| /etc | Host-specific configuration |
| /home/user | User personal files |
| /var/log | Log files |
| /var/lib | Application state/data |
| /tmp | Temporary files (cleared on reboot) |
| /proc | Virtual: kernel and process info |
| /sys | Virtual: hardware/device info |
| /dev | Device files |
| /usr/lib/jvm | JDK installations (Debian) |
| /opt | Optional/third-party software |
| /run | Runtime data (PID files, sockets) |

**3 things to remember:**
1. Logs in /var/log, configs in /etc, data in /var/lib
2. /proc and /sys are virtual - not stored on disk
3. Never put persistent data in /tmp - it's cleared on reboot

**Interview angle:**
"Where would you look to find how much memory a Java application
is using in production?" -> /proc/PID/status (VmRSS, VmHeap),
/proc/PID/smaps (detailed memory maps), jstat (JVM-level), or
kubectl top pod (Kubernetes level).

---

### Transferable Wisdom

The FHS **convention over configuration** principle (you know
where things are because of agreed convention) is directly
implemented in Java frameworks: Spring Boot expects
`application.properties` in classpath root or `/etc/app/`;
Maven expects `src/main/java` for sources. Convention reduces
cognitive load.

The **separation of static and variable data** (/ vs /var)
maps to container design: image layers (static) vs mounted
volumes (variable data that persists across container restarts).
This is why Docker volumes mount at /var/lib/myapp not at
/usr/myapp - following FHS even in containers.

---

### The Surprising Truth

On modern Ubuntu and Debian systems, /bin, /sbin, /lib, and
/lib64 are all symlinks to their /usr counterparts (/usr/bin,
/usr/sbin, /usr/lib, /usr/lib64). This "usrmerge" happened
between 2012-2022. The historical reason for separate /bin
(for programs needed before /usr was mounted) is now irrelevant
since modern systems mount /usr at boot. But the convention
persists: scripts still reference /bin/bash and /usr/bin/python
interchangeably.

---

### Mastery Checklist

- [ ] Can navigate to the correct directory for: logs, configs, app data, temp files
- [ ] Can explain why /proc is a virtual filesystem
- [ ] Can find a running Java process's open files via /proc
- [ ] Can explain the difference between /tmp, /var/tmp, and /run
- [ ] Can locate the JDK installation on an Ubuntu server

---

### Think About This

1. Container images typically have a read-only base filesystem.
   When your Java app writes a log file inside the container,
   where does the write actually go? What happens to that log
   data when the container is deleted?

2. The /proc filesystem exposes sensitive information:
   /proc/PID/environ shows all environment variables (including
   secrets injected as env vars). What security implications does
   this have for containerized applications, and how does
   Kubernetes try to mitigate this?

3. NixOS violates the FHS completely - all software lives in
   /nix/store/hash-name-version/. This enables atomic upgrades
   and rollbacks but breaks programs that hardcode paths like
   /usr/lib/libssl.so. What is the general principle that NixOS
   demonstrates, and why haven't more distros adopted it?

**TYPE G:** An application team wants to store their application's
database files in /home/appuser/data, their config in
/home/appuser/config, and their logs in /home/appuser/logs.
They argue "it's simpler and we own that directory." Explain
the problems with this approach from a security, operability,
and backup perspective, and suggest the FHS-correct alternatives.

---

### Interview Deep-Dive

**Foundational:**
Q: Where should a production Linux application store its: log files, config files, and persistent data?
A: Log files: /var/log/appname/ (logrotate manages this). Config files: /etc/appname/ (host-specific configuration). Persistent data (databases, uploads, state): /var/lib/appname/. Temporary scratch space: /tmp or /var/tmp (note: /tmp cleared on reboot; /var/tmp persists). This follows the Filesystem Hierarchy Standard and means operations teams know where to look without app-specific knowledge.

**Intermediate:**
Q: What is /proc, and why is it important for diagnosing a slow Java application?
A: /proc is a virtual filesystem where the kernel exposes process and system information as files. No actual disk storage - data is generated on-read by kernel code. For a Java application: /proc/PID/status shows memory usage (VmRSS, VmHeap), thread count; /proc/PID/fd/ lists all open file descriptors (can reveal unclosed connections causing fd exhaustion); /proc/PID/maps shows virtual memory layout (identify large mmapped regions); /proc/PID/environ shows environment variables (confirm configuration was injected correctly); /proc/meminfo shows system-wide memory state (is the system swapping?).

**Expert:**
Q: Why does a Docker container have its own /proc that shows only the container's processes, even though it's sharing the Linux kernel?
A: Linux PID namespaces (one of the 8 namespace types) create an isolated view of the process tree. When a container is created with a PID namespace, the container's init process (PID 1 in namespace) is actually a high-numbered PID on the host. Inside the container, /proc only shows processes in the same PID namespace. The kernel enforces this: when a process reads /proc, the kernel filters the directory listing to only include PIDs visible to the reading process's PID namespace. This isolation is why running `ps aux` inside a container shows only container processes, not host processes. Network namespaces provide the same isolation for network interfaces, and mount namespaces for filesystems.
