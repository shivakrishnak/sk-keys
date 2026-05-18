---
id: LNX-116
title: "Linux Security Model Research (LSM Design Theory)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★★
depends_on: LNX-048, LNX-049, LNX-050
used_by: LNX-121
related: LNX-048, LNX-049, LNX-050, LNX-114, LNX-121
tags: [linux-security-modules, lsm, selinux, apparmor, smack, tomoyo, yama, landlock, bpf-lsm, krsi, mac, dac, discretionary-access-control, mandatory-access-control, type-enforcement, mcs, mls, selinux-policy, apparmor-profiles, capabilities, seccomp, seccomp-bpf, ptrace-restriction, privilege-escalation, lsm-stacking, security-hooks, kernel-security, access-control-models, capability-bits, process-isolation, sandboxing, zero-trust, lsm-design, security-policy]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 116
permalink: /technical-mastery/lnx/linux-security-model-research-lsm-design/
---

## TL;DR

The **Linux Security Module (LSM) framework** (kernel 2.6+) provides a hook-based
architecture allowing security policies to be implemented as kernel modules.
LSM hooks: inserted at security-relevant points in kernel code (before operations
that could grant access). Current LSMs (stackable since 4.17): **SELinux** (NSA,
1998; type enforcement: labels on processes+files, policy defines what labeled
process can access labeled file; used in Android, RHEL), **AppArmor** (Canonical;
path-based: profiles per program; simpler than SELinux; used in Ubuntu, Snap),
**Smack** (embedded, Tizen), **TOMOYO** (path-based, learning mode), **Yama**
(ptrace restriction: prevents process A from debugging process B unless parent),
**Landlock** (kernel 5.13+: unprivileged process can restrict ITS OWN future
capabilities - no root required). **BPF LSM** (KRSI, kernel 5.7): write security
policy as eBPF program (flexible, live update, no kernel recompile). The design
choice: hooks over reference monitor = better performance, modularity. MAC vs DAC:
Linux traditional permissions = DAC (owner can change), SELinux = MAC (policy
enforced regardless of ownership). Capabilities: decompose root (37 capabilities).

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-116 |
| **Difficulty** | ★★★ Advanced |
| **Category** | Linux |
| **Tags** | LSM, SELinux, AppArmor, Landlock, BPF LSM, MAC, DAC, capabilities, seccomp, kernel security |
| **Prerequisites** | LNX-048 (SELinux basics), LNX-049 (AppArmor), LNX-050 (capabilities) |

---

### The Problem This Solves

**DAC limitation**: Unix DAC (Discretionary Access Control) - file owner controls
permissions. If a web server process runs as `www-data` (uid=33), and `/etc/passwd`
is readable by all (`-rw-r--r--`), the web server CAN read `/etc/passwd`. If the
web server is compromised: the attacker can read password hashes. DAC gives too
much discretion to file owners; a compromised process has all the permissions
of its user.

**Root problem**: Traditional Unix has a binary: root (uid=0) can do anything,
non-root is restricted. A compromised daemon running as root: game over. MAC
and capabilities: reduce the blast radius of a compromised process by confining
what it can access regardless of UID.

---

### Textbook Definition

**Linux Security Modules (LSM)**: A kernel framework providing hook functions
at security-sensitive operations. Security modules register callbacks at these
hooks to implement security policies. Multiple LSMs can run simultaneously
(stacked) since kernel 4.17.

**Mandatory Access Control (MAC)**: Access control policy enforced by the system,
not discretionary to the resource owner. Even root cannot override MAC policy
(with exceptions like setenforce 0, but that itself requires policy permission).
MAC labels every subject (process) and object (file, socket, IPC) and enforces
a policy defining allowed transitions.

**Discretionary Access Control (DAC)**: Traditional Unix permissions. The resource
owner (or root) can change access permissions at will. Owner decides who has access.

**Linux Capability**: A subset of root's privilege (there are 37 as of kernel 6.x).
Instead of "root can do everything", capabilities decompose root into:
CAP_NET_BIND_SERVICE (bind to ports < 1024), CAP_SYS_ADMIN (broad admin capability),
CAP_NET_RAW (raw socket access), CAP_SYS_PTRACE (ptrace other processes), etc.

---

### Understand It in 30 Seconds

```bash
# === The MAC advantage: contain a compromised nginx ===

# Without MAC (DAC only): nginx runs as www-data (uid=33)
# If nginx has a vulnerability: attacker has www-data privileges
# www-data can: read any file readable by others (world-readable)
# /etc/passwd: -rw-r--r-- (readable by others)
# Attacker: reads /etc/passwd, gets username list, offline crack

# With SELinux (MAC): nginx labeled httpd_t
# Policy: httpd_t can access httpd_sys_content_t (web content)
#         httpd_t CANNOT access shadow_t (shadow password file)
# Even if compromised: attacker CANNOT read /etc/shadow
# Even if www-data can read it at DAC level!

# === Check SELinux status ===

# Is SELinux active?
sestatus
# SELinux status:                 enabled
# SELinuxfs mount:                /sys/fs/selinux
# SELinux mount point:            /sys/fs/selinux
# Loaded policy name:             targeted  <- most common mode
# Current mode:                   enforcing  <- "enforcing"=active, "permissive"=audit-only
# Policy MLS status:              disabled
# Policy deny_unknown status:     allowed

# Get the SELinux context of a process:
ps -Z $(pgrep -x nginx | head -1) 2>/dev/null || ps -eZ | grep nginx
# system_u:system_r:httpd_t:s0    1234 nginx: worker process
# ^label structure: user:role:type:sensitivity
# type "httpd_t" = nginx's security context

# Get the SELinux context of a file:
ls -Z /etc/shadow
# ----------. root root system_u:object_r:shadow_t:s0 /etc/shadow
# type "shadow_t" = shadow password file's security context

# The policy rule that protects this:
sesearch -A -s httpd_t -t shadow_t 2>/dev/null | head -5
# (no output = httpd_t cannot access shadow_t files!)

# === AppArmor: profile-based confinement ===

# Check AppArmor status:
aa-status
# apparmor module is loaded.
# 30 profiles are loaded.
# 30 profiles are in enforce mode.
#    /usr/bin/evince
#    /usr/sbin/cups-browsed
#    ...
#    /usr/sbin/nginx  <- nginx profile exists!

# View nginx's AppArmor profile:
cat /etc/apparmor.d/usr.sbin.nginx | head -30
# # AppArmor profile for nginx
# /usr/sbin/nginx {
#   capability net_bind_service,    # bind to port 80/443
#   capability setuid,              # drop privileges
#   /var/log/nginx/** rw,           # read/write log files
#   /etc/nginx/** r,                # read config
#   /var/www/html/** r,             # read web content
#   deny /etc/shadow r,             # EXPLICIT DENY for shadow!
#   # (but by default: if not allowed, it's denied)
# }

# === Landlock: unprivileged sandboxing (kernel 5.13+) ===

# Landlock: no root required! Process restricts ITSELF
# Example: sandboxed file reading program

# Check Landlock availability:
cat /sys/kernel/security/lsm
# lockdown,capability,yama,apparmor  <- no landlock here
# OR:
# lockdown,capability,yama,landlock  <- landlock available!

# Programmatic Landlock usage (C):
# struct landlock_ruleset_attr attr = {
#     .handled_access_fs = LANDLOCK_ACCESS_FS_READ_FILE |
#                          LANDLOCK_ACCESS_FS_READ_DIR,
# };
# int ruleset_fd = landlock_create_ruleset(&attr, ...);
# # Add allowed path: /var/www/html (read-only)
# landlock_add_rule(ruleset_fd, LANDLOCK_RULE_PATH_BENEATH, ...);
# # RESTRICT: from this point, process can ONLY read /var/www/html
# landlock_restrict_self(ruleset_fd, 0);
# # Now: any attempt to read /etc/shadow: EACCES even if DAC allows it!
```

---

### First Principles

```
THE LSM DESIGN RATIONALE:

Challenge: implement security policies for the Linux kernel
Multiple conflicting requirements:
  1. Performance: security checks on every sensitive operation
     -> must be fast (can't add microseconds to every syscall)
  2. Modularity: different environments need different policies
     SELinux for enterprise, AppArmor for desktop, BPF LSM for custom
  3. Composability: need to run multiple LSMs simultaneously
     Yama (ptrace restriction) + AppArmor + base capabilities
  4. Safety: LSM module bugs should not compromise the kernel

REJECTED APPROACH: Monolithic security model
  "Just add SELinux into the kernel, no abstraction needed"
  Problem: hard to swap, can't combine multiple, not extensible

REJECTED APPROACH: Pure microkernel security server
  Each security decision: IPC to user-space security server
  Problem: performance (IPC overhead), deadlock risk (security check
  during security server startup)

CHOSEN APPROACH: LSM hooks (Linus Torvalds/Greg Kroah-Hartman, 2001)
  Insert "hook" function calls at security-sensitive kernel code points
  Hook calls a function pointer: default = allow (dummy LSM)
  Security module: replace default with custom check
  
  Hook locations (examples):
  inode_permission: before any file access
  file_open: before opening a file
  socket_connect: before connecting a socket
  task_create: before creating a new process (fork)
  mmap_addr: before mapping memory
  bprm_check_security: before executing a program
  ptrace_access_check: before ptrace access
  
  LSM hook call in kernel source:
  (in security/security.c, called from fs/namei.c)
  int security_inode_permission(struct inode *inode, int mask) {
      if (unlikely(IS_PRIVATE(inode)))
          return 0;
      return call_int_hook(inode_permission, 0, inode, mask);
  }
  // call_int_hook: calls ALL registered LSM hooks for this operation
  // if ANY hook returns non-zero: access denied!

LSM STACKING (kernel 4.17+):
  Multiple LSMs can run simultaneously
  Rules: only ONE "major" LSM (SELinux OR AppArmor), multiple "minor" LSMs
  Major LSMs: SELinux, AppArmor, Smack, TOMOYO (full MAC, policy-based)
  Minor LSMs: capabilities (always), Yama, Lockdown (always active)
  BPF LSM: can stack with major LSM
  
  Stack: [Capabilities] -> [Yama] -> [Lockdown] -> [SELinux or AppArmor]
  Access: ALL hooks must approve. Most restrictive wins.

DAC vs MAC INTERACTION:
  Linux access control: DAC FIRST, then MAC
  
  File access (e.g., open /etc/shadow):
  1. DAC check: can uid=33 (www-data) read /etc/shadow?
     /etc/shadow: -rw-r----- root shadow
     www-data is not in shadow group -> DAC DENIES
     (MAC check not even reached)
  
  2. If DAC allowed (e.g., world-readable file):
     MAC check: can httpd_t read shadow_t?
     SELinux policy: no rule allowing this
     MAC DENIES
  
  3. If both DAC and MAC allow: access granted
  
  Result: MAC adds a SECOND layer on top of DAC
  Hardened system: pass BOTH checks. More restrictive overall.

SELinux TYPE ENFORCEMENT (THE CORE MECHANISM):

Every entity has a type label:
  Processes: type = domain (e.g., httpd_t, mysqld_t, sshd_t)
  Files: type = file_type (e.g., httpd_sys_content_t, shadow_t, bin_t)
  Sockets: type = socket_type
  
Policy rules:
  allow httpd_t httpd_sys_content_t:file { read getattr open };
  ^     subject  object                 operation
  
  deny httpd_t shadow_t:file { read };  (no such rule = deny by default!)

Type transitions:
  httpd_t executes /usr/sbin/php-fpm -> process becomes php_fpm_t
  "Type transition" = how domain changes when process exec's a new program
  
  Defined in policy:
  type_transition httpd_t php_fpm_exec_t : process php_fpm_t;
  "When httpd_t execs a file labeled php_fpm_exec_t, the new process is php_fpm_t"

Multi-Category Security (MCS):
  Used in containers and multi-tenant systems
  Two containers: s0:c0,c1 and s0:c2,c3
  Policy: process can only access files with matching categories
  Effect: container A cannot access container B's files
  Even if both run as httpd_t!
  OpenShift/Kubernetes: uses MCS for pod isolation

CAPABILITIES: DECOMPOSING ROOT

Capabilities: fine-grained privilege decomposition
  Traditional: root (uid=0) = all-powerful
  With capabilities: split root into 37 specific abilities

Key capabilities:
  CAP_NET_BIND_SERVICE: bind to privileged ports (< 1024)
    nginx: needs this to bind to port 80/443
    Java app: needs this to bind to port 443 directly
  
  CAP_NET_RAW: create raw sockets (ping, packet capture)
    tcpdump: needs this for packet capture
    vulnerability: can be used for port scanning, spoofing
  
  CAP_SYS_ADMIN: "everything else" (most abused capability)
    mount filesystems, change hostname, configure namespaces
    wide capability: try to avoid granting
  
  CAP_SYS_PTRACE: ptrace other processes
    gdb: needs this for debugging
    strace: needs this for syscall tracing
    security risk: can extract secrets from any process
  
  CAP_DAC_OVERRIDE: bypass DAC file permissions
    Dangerous: allows reading any file regardless of permissions
  
  CAP_SYS_RAWIO: raw hardware access (disk, memory)
    Extremely dangerous: can read/write raw disk sectors

Docker capability defaults:
  Docker drops many dangerous capabilities by default:
  Dropped: CAP_SYS_ADMIN, CAP_SYS_PTRACE, CAP_NET_RAW, CAP_SYS_RAWIO
  Kept: CAP_NET_BIND_SERVICE, CAP_CHOWN, CAP_SETUID, CAP_SETGID, CAP_KILL

Capability operations per process:
  Permitted: maximum capabilities process can have
  Effective: currently active capabilities (subset of permitted)
  Inheritable: passed to exec'd programs
  Ambient: added to permitted on exec (kernel 4.3+)
  Bounding set: limits capabilities for this process and children
  
  nginx startup (as root -> drop to www-data):
  Start as root: CAP_NET_BIND_SERVICE + all caps in permitted
  bind(80): requires CAP_NET_BIND_SERVICE (in effective)
  After bind: drop to www-data: 
    clear all caps except needed
    setuid(www-data)
  Worker process: no capabilities, limited DAC access
```

---

### Thought Experiment

Designing the minimal capability set for a containerized microservice:

```bash
# === Principle of Least Privilege in practice ===

# Scenario: Java Spring Boot app, runs on port 8080, needs DB access
# Default Docker container: runs as root (!) with full capability set

# BAD: Running container as root with all capabilities:
docker run myapp:latest
# ps inside container: uid=0 (root!)
# cap: ALL capabilities enabled
# If app is compromised: attacker has root + all capabilities inside container
# If container escape bug: attacker has root on host!

# BETTER: Run as non-root, drop capabilities:
# Dockerfile:
# FROM amazoncorretto:17-alpine
# RUN addgroup -S app && adduser -S app -G app
# USER app  <- run as non-root

# docker run options:
docker run \
  --user 1001:1001 \          # non-root uid:gid
  --cap-drop ALL \             # drop ALL capabilities first
  --cap-add NET_BIND_SERVICE \ # add only what we need (port 8080: >1024, don't need this!)
  --security-opt no-new-privileges \  # prevent privilege escalation
  myapp:latest

# For port 8080 (>1024): don't even need NET_BIND_SERVICE!
# NET_BIND_SERVICE: only for ports < 1024

# Spring Boot on 8080: zero capabilities needed!
docker run \
  --user 1001:1001 \
  --cap-drop ALL \             # zero capabilities
  --security-opt no-new-privileges \
  --read-only \                # read-only filesystem
  --tmpfs /tmp \               # writable /tmp in memory
  myapp:latest

# Verify capabilities in container:
docker exec myapp_container cat /proc/self/status | grep "^Cap"
# CapInh: 0000000000000000
# CapPrm: 0000000000000000
# CapEff: 0000000000000000  <- zero capabilities!
# CapBnd: 0000000000000000
# CapAmb: 0000000000000000

# === Seccomp: syscall filtering for containers ===

# Default Docker seccomp profile: blocks 44 dangerous syscalls
# Examples blocked:
# reboot, kexec_load, mount, umount2, pivot_root, chroot
# delete_module, init_module, finit_module (kernel module loading)
# perf_event_open (kernel profiling attacks)
# ptrace (unless debugging)

# Custom seccomp profile (allow only needed syscalls):
cat myapp-seccomp.json
# {
#   "defaultAction": "SCMP_ACT_ERRNO",  <- deny by default
#   "architectures": ["SCMP_ARCH_X86_64"],
#   "syscalls": [
#     {"names": ["read","write","close","openat","mmap","mprotect",
#                "brk","munmap","futex","nanosleep","exit_group",
#                "socket","connect","getsockopt","setsockopt","bind",
#                "accept4","recvfrom","sendto","epoll_wait","epoll_ctl",
#                "epoll_create1","clock_gettime"],
#      "action": "SCMP_ACT_ALLOW"}
#   ]
# }
# Allowlist: ONLY the 24 syscalls the app actually uses!
# Any other syscall: ERRNO (permission denied)

docker run \
  --security-opt seccomp=myapp-seccomp.json \
  --cap-drop ALL \
  --user 1001:1001 \
  myapp:latest

# === AppArmor for container profile ===

# AppArmor profile for microservice container:
cat /etc/apparmor.d/myapp {
# /myapp {
#   # Allow execution of Java
#   /usr/bin/java ix,
#   /lib/** rm,
#   /usr/lib/** rm,
#   /opt/app/** r,       # application files (read-only!)
#   /tmp/** rwl,         # temp files
#   
#   # Network: allow TCP outbound (DB connections)
#   network tcp,
#   
#   # Deny shell execution
#   deny /bin/** x,
#   deny /usr/bin/sh x,
#   deny /usr/bin/bash x,
#   
#   # Deny sensitive files
#   deny /etc/shadow r,
#   deny /etc/passwd w,
#   deny /proc/** w,
# }

# Apply and enforce:
apparmor_parser -r -W /etc/apparmor.d/myapp
# Container with AppArmor + seccomp + capabilities:
# - If app exploited: can't exec shell, can't read /etc/shadow
# - Can't load kernel modules (capability + seccomp)
# - Can't escape to filesystem outside allowed paths (AppArmor)
```

---

### Mental Model / Analogy

```
LSM = building security layers in a corporate office

Corporate office building security model:

Layer 1: DAC = Key card access
  Building: anyone can access public lobby
  Keycard: unlocks offices where you are registered
  Discretionary: office manager decides who gets keycard to their area
  Problem: if your keycard is stolen -> attacker can access your areas

Layer 2: MAC (SELinux) = Role-based floor access + biometric
  Security label = badge color + clearance level
  "Red badge" (httpd_t) can only enter "server rooms" (httpd_content)
  Even if someone has a red badge AND your keycard:
  They CANNOT enter "HR vault" (shadow_t) - wrong badge color!
  Policy enforced by security system, not by individual manager
  
  Mandatory = even office manager cannot override badge-color policy
  (Only the security director can change the policy itself)

Layer 3: Capabilities = What equipment you can use
  Traditional: "security manager" can use everything in the building
  Capabilities: split "security manager" role into specific tools
  "Use vault lock": open the vault (CAP_SYS_ADMIN equivalent)
  "Use phone system": make any internal call (CAP_NET_BIND_SERVICE)
  "Interrogate employee": question someone about their actions (CAP_SYS_PTRACE)
  
  nginx engineer: gets keycard + "server room access" + "phone system"
  Doesn't get: "vault lock" or "interrogate employee"
  Even if exploited: attacker can only use the phone, can't open vault

Layer 4: Seccomp = Allowed tools in this room
  Server room: you can only use the servers here
  Seccomp: this process can only call these 24 system calls
  No matter what: cannot call "delete_module" (remove kernel modules)
  Even if attacker is root, has all capabilities:
  seccomp filter: syscall_number=delete_module -> KILL process

Layer 5: Landlock = Self-imposed visitor badge
  Visitor: decides on arrival "I will only visit rooms A, B, C"
  Registers this intent with security desk (no manager needed!)
  Security system: enforces this self-restriction
  Even if visitor WANTS to enter room D later: refused
  "I promised I wouldn't, and the building enforces my promise"
  
  Application: "I'll only read /var/www/html, nothing else"
  landlock_restrict_self(): this process can now only read that path
  Even if someone tricks the app into opening /etc/shadow: EACCES

Stacking layers (defense in depth):
  An attacker who exploits a web server vulnerability:
  
  Without any MAC:
  "I'm www-data! I can read anything www-data can! Including /etc/passwd!"
  
  With all layers:
  DAC: can't read shadow (shadow group restriction)
  SELinux: httpd_t can't read shadow_t (type enforcement)
  AppArmor: nginx profile doesn't allow /etc/shadow
  Capabilities: no CAP_DAC_OVERRIDE (can't bypass DAC)
  Seccomp: can only call the 24 allowed syscalls
  Landlock: app self-restricted to /var/www/html
  
  Result: exploitation = "I can respond to HTTP requests. That's it."
```

---

### Gradual Depth - Five Levels

**Level 1:**
What DAC vs MAC means. SELinux: labels on processes and files, policy defines
access. AppArmor: profiles for programs, defines allowed filesystem access.
Capabilities: root's powers split into 37 pieces. Seccomp: filter which syscalls
a process can make. Why containers need all of these.

**Level 2:**
SELinux modes: enforcing/permissive/disabled. How to read SELinux contexts
(user:role:type:sensitivity). AppArmor profile structure. Docker's default
capability drops. Seccomp's default Docker profile. Yama ptrace restriction.
Landlock basics. BPF LSM concept. How to diagnose SELinux denials with audit2allow.

**Level 3:**
SELinux type enforcement details: allow rules, type transitions, file_contexts.
AppArmor features: ix vs px for child processes, capability rules, network rules.
Linux capability inheritance across fork/exec. Container security: --cap-drop ALL,
--security-opt no-new-privileges. Custom seccomp profiles (allowlist vs denylist).
LSM stacking: which LSMs can coexist.

**Level 4:**
SELinux MCS/MLS: multi-category/multi-level security for container isolation.
AppArmor abstractions: #include <abstractions/base>. Writing BPF LSM programs:
SEC("lsm/file_open") hooks. SELinux policy module development: te files,
fc files, audit2allow workflow. No-new-privileges prctl and its interaction with
seccomp and capabilities. Landlock ruleset design for privilege-constrained
file servers.

**Level 5:**
SELinux labeled networking: packet labels (SECMARK), network peer context,
IPsec with SELinux labels. The LSM hook completeness problem: are all
security-relevant kernel operations covered by LSM hooks? History of missed
operations (network namespaces, certain BPF operations). BPF LSM's advantage
here: can add hooks dynamically. The "confused deputy" attack and how MAC
prevents it. CoW (copy-on-write) and its interaction with MAC (if file
labels change during CoW, policy may be violated). SELinux sandbox vs
process namespaces: which provides stronger isolation and when. SMEP/SMAP
interaction with LSM: hardware enforcement + software enforcement.

---

### Code Example

**BAD - running with unnecessary root and no capability restrictions:**
```bash
# BAD: application running with full root privileges
# If compromised: attacker has god-mode inside and possibly outside

# In Dockerfile:
# FROM openjdk:17
# COPY app.jar /app/app.jar
# (no USER directive - runs as root!)
# ENTRYPOINT ["java", "-jar", "/app/app.jar"]

# BAD: no seccomp, no capability drop, full root
docker run myapp
# ps -Z (inside container): uid=0, all capabilities enabled
# Attacker who exploits RCE: full root, can run arbitrary syscalls
# Can: load kernel module (if --privileged), access /proc/sysrq-trigger
# Can: read /etc/shadow of ALL containers on the host (if shared)
```

```bash
# GOOD: hardened container deployment
# Defense in depth: non-root + capabilities + seccomp + AppArmor + read-only

# Dockerfile (hardened):
# FROM eclipse-temurin:17-jre-alpine
# RUN addgroup -S appgroup && adduser -S appuser -G appgroup
# # Don't write app files as root:
# COPY --chown=appuser:appgroup app.jar /app/app.jar
# # Switch to non-root before running:
# USER appuser
# WORKDIR /app
# EXPOSE 8080  # documentation only
# ENTRYPOINT ["java", "-jar", "app.jar"]

# docker-compose.yml (hardened):
# services:
#   myapp:
#     image: myapp:latest
#     user: "1001:1001"           # explicit non-root user
#     read_only: true             # immutable container filesystem
#     tmpfs:
#       - /tmp                    # writable /tmp in memory
#     cap_drop:
#       - ALL                     # drop ALL capabilities first
#     security_opt:
#       - no-new-privileges:true  # prevent setuid escalation
#       - seccomp:./seccomp.json  # custom syscall allowlist
#       - apparmor:myapp          # AppArmor profile
#     ports:
#       - "8080:8080"
#     volumes:
#       - type: bind
#         source: ./config
#         target: /app/config
#         read_only: true         # config is read-only!

# Verify security posture:
docker exec myapp_container \
  sh -c 'cat /proc/self/status | grep Cap; id'
# uid=1001(appuser) gid=1001(appgroup) groups=1001(appgroup)
# CapPrm: 0000000000000000  # zero capabilities
# CapEff: 0000000000000000  # zero capabilities in effect
# (no output = perfect least privilege)

# Test: verify shadow file inaccessible:
docker exec myapp_container cat /etc/shadow 2>&1
# cat: /etc/shadow: Permission denied  <- DAC: not readable by non-root
# Even if we added a read permission:
docker exec myapp_container bash -c \
  'chmod 644 /etc/shadow && cat /etc/shadow' 2>&1
# bash: /usr/bin/bash: Permission denied  <- seccomp blocks bash exec
# OR: AppArmor denies chmod/read of /etc/shadow
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "SELinux disabled = more compatible, same security" | Disabling SELinux removes an important security layer and is a significant security regression. Common advice ("just disable SELinux if you have issues") is security malpractice. The correct response to SELinux denials: diagnose with `ausearch -m AVC -ts recent`, generate policy with `audit2allow`, add the minimal required rule. SELinux in permissive mode (`setenforce 0`): logs what WOULD be denied without blocking - useful for diagnosing policy issues without breaking production. Common source of SELinux confusion: type_context mismatches after copying files (new files inherit parent directory type if type_transition not defined). Fix: `restorecon -R /path/to/files` (reset file contexts to policy defaults). Understanding: SELinux is a mandatory layer. When properly configured, it stops privilege escalation attacks that bypass normal Unix permissions. The CVE pattern: attacker exploits web app vuln -> gets www-data shell -> without SELinux: can access anything www-data can -> with SELinux httpd_t confinement: limited to httpd_t-allowed resources only. |
| "Capabilities eliminate the need for MAC (SELinux/AppArmor)" | Capabilities and MAC (SELinux/AppArmor) address different attack vectors. Capabilities: reduce what root CAN do (decompose root privilege). MAC: confine any process based on type labels (regardless of UID). The attack scenario capabilities DON'T address: a non-root process (www-data, uid=33) with no capabilities exploiting a vulnerability to read files accessible to www-data. Capabilities don't restrict file ACCESS based on policy - they restrict PRIVILEGE operations. SELinux TYPE ENFORCEMENT restricts: even a process with zero capabilities from accessing files whose SELinux type doesn't match the policy for the process's domain. Example: www-data process with zero capabilities and SELinux domain httpd_t: can ONLY access files labeled httpd_sys_content_t (or other types explicitly allowed in policy). Cannot access shadow_t, cert_t, etc. Capabilities: govern what PRIVILEGES a process has. MAC: governs what RESOURCES any process can access. Defense in depth: BOTH are needed. |
| "AppArmor is weaker than SELinux because it's path-based" | AppArmor is simpler to use than SELinux and has different (not necessarily weaker) security properties. PATH-BASED vs TYPE-BASED difference: AppArmor confines based on filesystem path (/etc/shadow: deny). SELinux confines based on type label (shadow_t: deny for httpd_t). The path-based weakness: if an attacker creates a hard link to /etc/shadow at /tmp/harmless, AppArmor's /etc/shadow rule doesn't apply to the hard link. However: SELinux's type label IS on the inode (not the path), so the hard link still has shadow_t label and is denied. The practical difference: hard link attacks require: write access to the target directory + symlink_restriction bypasses. Most container environments prevent this (read-only root filesystem). AppArmor advantage: much simpler policy writing. SELinux advantage: stronger against hard link / bind mount escapes. Red Hat/RHEL/CentOS/Fedora: use SELinux. Ubuntu/Debian/Canonical: use AppArmor. Neither is "always better" - SELinux is more complex and harder to deploy correctly, AppArmor is more deployable but has some edge cases. Choosing: go with your distribution's default unless you have specific requirements. |
| "Seccomp is redundant if you have AppArmor/SELinux" | Seccomp operates at the syscall level, while AppArmor and SELinux operate at the resource access level. They address different attack surfaces. What seccomp adds that MAC doesn't: (1) SYSCALL FILTERING: seccomp can deny dangerous syscalls entirely (delete_module, ptrace, kexec_load, reboot). Even if a process's SELinux domain allows some sensitive operations, seccomp can deny the underlying syscall that would implement them. (2) ARGUMENT FILTERING: seccomp-bpf can inspect syscall arguments, not just syscall number. Example: allow open() but only with O_RDONLY flag. (3) DIFFERENT GRANULARITY: SELinux/AppArmor work on named objects (files, sockets). Some kernel operations don't have named objects (performance monitoring, kernel module loading). Seccomp: blocks these by syscall. Defense in depth with all three: MACs (SELinux/AppArmor) + seccomp + capabilities = three different security mechanisms that an attacker must bypass independently. CVE-2022-29582 (io_uring privilege escalation): SELinux and AppArmor didn't help because the exploit worked within io_uring's operations. Seccomp with io_uring disabled: would have prevented the attack. |

---

### Failure Modes & Diagnosis

```bash
# === SELinux denial diagnosis ===

# Application fails with "Permission denied" on SELinux system:
# Step 1: Check for SELinux denials in audit log:
ausearch -m AVC -ts recent
# time->Sun May 19 14:30:00 2024
# type=AVC msg=audit(1234567890.123:456):
#   avc:  denied  { read } for
#   pid=12345 comm="nginx" name="shadow" dev="sda1"
#   scontext=system_u:system_r:httpd_t:s0
#   tcontext=system_u:object_r:shadow_t:s0
#   tclass=file permissive=0

# Decode: nginx (httpd_t) tried to READ shadow file (shadow_t)
# Was denied. This is EXPECTED (security working correctly)

# Step 2: Is this a legitimate operation?
# If yes: generate policy rule
audit2allow -a -M mypol 2>&1 | head -20
# Generated file: mypol.pp and mypol.te
# mypol.te contains:
# allow httpd_t shadow_t:file { read };
# WARNING: This grants nginx access to /etc/shadow - THINK BEFORE APPLYING!

# Better: if this is a MISCONFIGURED FILE CONTEXT:
# Application should read /var/lib/myapp/config (not shadow)
# But the file has wrong SELinux label:
ls -Z /var/lib/myapp/config
# unconfined_u:object_r:var_t:s0 /var/lib/myapp/config
# Should be: httpd_sys_content_t (or app-specific type)

# Fix: restore correct context:
restorecon -v /var/lib/myapp/config
# OR: set specific context:
semanage fcontext -a -t httpd_sys_content_t "/var/lib/myapp(/.*)?"
restorecon -R /var/lib/myapp

# === Docker container with seccomp blocking needed syscall ===

# Container fails with "Operation not permitted" for specific operations:
docker run myapp
# java.io.IOException: Failed to create JVM - clock_gettime64 blocked?

# Debug: which syscall is blocked?
docker run --security-opt seccomp=unconfined myapp
# If this works: seccomp is blocking a needed syscall

# Find blocked syscall:
strace -f java -jar app.jar 2>&1 | grep EPERM | head -10
# clock_gettime64(...) = -1 EPERM  <- blocked!
# Modern JVM needs clock_gettime64 (64-bit clock, not in older seccomp profiles)

# Fix: add clock_gettime64 to seccomp allowlist
# (or use updated seccomp profile from Docker 23+)

# === AppArmor blocking legitimate file access ===

dmesg | grep apparmor | grep DENIED | tail -10
# apparmor="DENIED" operation="open"
#   profile="/usr/bin/nginx"
#   name="/var/run/myapp.sock"
#   pid=12345 comm="nginx"
#   requested_mask="rw"
#   denied_mask="rw"
#   fsuid=33 ouid=0

# Fix: edit AppArmor profile:
cat >> /etc/apparmor.d/usr.sbin.nginx << 'EOF'
  /var/run/myapp.sock rw,
EOF
apparmor_parser -r /etc/apparmor.d/usr.sbin.nginx
```

---

### Related Keywords

**Foundational:**
LNX-048 (SELinux), LNX-049 (AppArmor), LNX-050 (capabilities)

**Builds on this:**
LNX-121 (permission models as trust boundaries)

**Related:**
LNX-114 (open problems), LNX-121 (trust boundaries)

---

### Quick Reference Card

| LSM | Type | Key feature | Used in |
|-----|------|-------------|---------|
| SELinux | MAC (type) | Label-based, hardest | RHEL, Android, Fedora |
| AppArmor | MAC (path) | Profile-based, easier | Ubuntu, Debian, Snap |
| Yama | ptrace | Restrict debugging | All (always active) |
| Landlock | MAC (self) | No root needed | Any kernel 5.13+ |
| BPF LSM | MAC (BPF) | Programmable | kernel 5.7+ |
| Capabilities | Privilege | Split root | All |
| Seccomp | Syscall | Filter calls | Containers |

**3 things to remember:**
1. LSM hooks: inserted at security-sensitive points in kernel. ALL LSMs must approve access (most restrictive wins). Stacking: minor LSMs (Yama, capabilities) + one major LSM (SELinux OR AppArmor) + BPF LSM. Access denied = ANY hook returns non-zero.
2. MAC vs DAC: DAC = file owner controls permissions (discretionary). MAC = policy enforced regardless of ownership (mandatory). SELinux denies httpd_t from reading shadow_t even if shadow_t file is world-readable (DAC allows, MAC denies). Docker security: use --cap-drop ALL + seccomp + AppArmor + non-root user.
3. Landlock: process restricts ITSELF, no root required (kernel 5.13+). BPF LSM: write policy as eBPF program (live update, no kernel module). Seccomp adds what MAC misses: syscall-level filtering. Defense in depth: use ALL layers (capabilities + MAC + seccomp + non-root).

---

### Transferable Wisdom

The LSM hook architecture transfers to: Java Security Manager (deprecated in 17:
hooks in JVM at security-sensitive operations), Spring Security method-level
security (@PreAuthorize: hooks before method execution), Kubernetes admission
webhooks (hooks before resource creation), AWS Security Groups + IAM policies
(DAC equivalent: security groups; MAC equivalent: IAM policy enforcement).
The MAC vs DAC distinction maps directly to: RBAC (Role-Based Access Control,
MAC-like: role policy defines access) vs filesystem ACLs (DAC-like: owner
controls access), AWS IAM Policies (MAC: attached by admin, not resource owner)
vs S3 Bucket Policies and ACLs (DAC-like: owner controls). The capability
decomposition pattern is used in: AWS IAM least-privilege (fine-grained actions
instead of admin), OAuth scopes (read:email vs admin:all), Kubernetes RBAC
(specific verbs on specific resources). Seccomp's syscall allowlist pattern
is used in: AWS Lambda function resource policies (specific API actions), firewall
rules (specific ports allowed), browser extensions permissions (specific APIs
declared). Landlock's self-restriction model (process limits its own future
capabilities) is used in: pledge/unveil in OpenBSD (process pledges what it needs
at startup), Capsicum in FreeBSD (capability mode), Android's self-imposed
permission grants.

---

### The Surprising Truth

The Linux Security Module (LSM) framework was nearly not included in the kernel.
Linus Torvalds initially opposed the LSM patch in 2001, arguing that it was
"over-engineered" and that the security features could be added more directly.
The NSA had developed SELinux and was pushing for its inclusion (the context:
post-9/11, US government interest in Linux security was high). The compromise:
the LSM framework itself, providing a generic hook mechanism, was merged - and
SELinux was included as the first LSM.

The irony: Torvalds accepted an abstract hook framework (LSM) over a specific
implementation (SELinux directly) - the opposite of his usual preference for
concrete over abstract. The reason: LSM allowed the kernel to remain agnostic
about which security model was "correct" - instead of mandating SELinux, the
kernel provided the infrastructure for any MAC model. This architectural choice
is why AppArmor, Smack, Tomoyo, and BPF LSM exist - they're all built on LSM hooks.

If the NSA's SELinux had been merged directly (no LSM abstraction), Ubuntu's
AppArmor - which became hugely popular due to its simplicity - would never have
had a path into the kernel. The abstraction enabled diversity.

---

### Mastery Checklist

- [ ] Understands DAC vs MAC distinction and when MAC provides security that DAC cannot
- [ ] Can read SELinux contexts (user:role:type:sensitivity) and diagnose AVC denials
- [ ] Knows Docker security hardening: --cap-drop ALL, --security-opt no-new-privileges, seccomp
- [ ] Understands capability decomposition: what capabilities do (privilege control), when to use them
- [ ] Can explain why defense in depth (capabilities + MAC + seccomp) is needed, not just one layer

---

### Think About This

1. Android uses SELinux in enforcing mode for all apps. Each app has its own
   SELinux domain. The policy defines: what files the system app can access,
   what system calls it can make, what IPC it can use. But: Android apps can
   request permissions that grant them ADDITIONAL SELinux capabilities (e.g.,
   INTERNET permission allows network access). Analyze: this is a hybrid system.
   The SELinux policy is MAC (mandatory) but permissions granted to apps are
   effectively DAC-like (user-controlled). Where does this model break down?
   How does the recent "scoped storage" change (Android 11+) relate to the
   SELinux MAC model? What would a fully MAC-only Android look like?

2. Landlock allows unprivileged processes to restrict themselves. The primary
   use case: a web server that loads a plugin should be able to restrict the
   plugin to accessing only the files the plugin declared it needs. This requires
   the parent process (web server) to apply Landlock BEFORE loading the plugin
   code. Design a plugin API for a web framework that uses Landlock. What
   information must a plugin declare upfront (before loading)? What happens if
   a plugin needs access that wasn't declared (new file pattern)? How does this
   compare to Java's SecurityManager (deprecated) and WebAssembly's capability-
   based security model?

3. The BPF LSM (KRSI, kernel 5.7) allows writing security policies as eBPF
   programs. Traditional LSMs (SELinux, AppArmor) compile policy into kernel
   structures at boot time. BPF LSM: load new security policy at runtime without
   reboot. This is both the feature (flexibility) and the risk (dynamic security
   policy changes). Analyze: what is the threat model for BPF LSM? Who can load
   a BPF LSM program? (Answer: CAP_MAC_ADMIN, typically root). If an attacker
   gains root and loads a BPF LSM policy that allows everything: what protection
   remains? Does this mean BPF LSM is unsuitable for high-security environments?
   How does this compare to the "setenforce 0" SELinux disable - is BPF LSM
   fundamentally safer, less safe, or the same?

---

### Interview Deep-Dive

**Foundational:**
Q: Explain the difference between DAC and MAC, and why containers need MAC (SELinux/AppArmor).
A: DAC (DISCRETIONARY ACCESS CONTROL): The traditional Unix permission model. "Discretionary" means the resource owner controls who can access it. File permissions (-rw-r--r--) are set by the file owner (or root) and can be changed by the owner at will. Example: www-data (uid=33) can read any file that has group=www-data OR other=readable permissions. If /etc/passwd is -rw-r--r-- (world-readable): www-data can read it. The "discretion" is: the root user created the file and chose to make it world-readable - that's their discretionary decision. DAC LIMITATION: A compromised process has all the permissions of its user. www-data is expected to serve web files; it shouldn't access /etc/shadow. But DAC doesn't know about "web server purpose" - it only knows uid=33. MAC (MANDATORY ACCESS CONTROL): Access is controlled by SYSTEM POLICY, not resource owner discretion. SELinux: every process has a TYPE (domain: httpd_t, mysqld_t). Every file has a TYPE (shadow_t, cert_t, httpd_content_t). Policy rule: "httpd_t can read httpd_sys_content_t, period." No rule exists for "httpd_t reading shadow_t" -> DENIED. Even if /etc/shadow is world-readable (DAC allows), SELinux policy denies httpd_t from reading shadow_t files. WHY CONTAINERS NEED MAC: A container escape vulnerability means: the attacker is running code inside the container with the container's process identity (e.g., uid=0 inside, but mapped to uid=100000 on host). Without MAC: the attacker can read/write any file accessible to that uid within the container. With SELinux/AppArmor: the container's process is labeled with a specific type (container_t or a per-container MCS label s0:c123,c456). The policy restricts: container_t can ONLY access container_file_t or files labeled for that container's category range. A container cannot access another container's files even if both run as root inside the container. Kubernetes uses SELinux MCS (Multi-Category Security) exactly for this: each pod gets a unique category range, ensuring pod A's files cannot be accessed by pod B. THIS IS WHY: disabling SELinux on production servers ("it's causing issues") is a security regression. The correct response: diagnose the denial with ausearch, add the minimal required policy rule.

**Expert:**
Q: What is the Linux capability system and how would you design a minimal capability set for a production microservice?
A: THE CAPABILITY SYSTEM: Linux capabilities decompose the traditional binary root/non-root privilege into 37 fine-grained capabilities (as of kernel 6.x). Originally: any process uid=0 (root) can do EVERYTHING. Any process uid!=0: very restricted. The problem: a daemon that needs to bind to port 80 (requires privilege) must run as root OR use capabilities. CAP_NET_BIND_SERVICE: allows binding to ports < 1024, without requiring full root. CAPABILITY SETS: Each process has: Permitted (max caps available), Effective (currently active, subset of permitted), Inheritable (passed through exec), Ambient (added to permitted on exec), Bounding (inherited cap ceiling). The exec-based reduction: when a non-privileged binary is executed, by default: Ambient -> Permitted, Inheritable & Permitted -> Effective. A binary can have file capabilities (setcap): setcap cap_net_bind_service+ep /usr/bin/nginx sets the binary to gain CAP_NET_BIND_SERVICE on exec, even from non-root. DESIGNING MINIMAL CAPS FOR A MICROSERVICE: Spring Boot on port 8080, connects to PostgreSQL. Step 1: port > 1024 -> NO CAP_NET_BIND_SERVICE needed (only for <1024). Step 2: runs as dedicated user -> NO CAP_SETUID needed (don't change uid). Step 3: reads config files, writes logs -> NO special capabilities needed (DAC with proper file ownership). Step 4: TCP connections to DB -> no special capability (regular tcp socket). Conclusion: THIS SERVICE NEEDS ZERO CAPABILITIES. Implementation: Dockerfile USER directive (non-root), docker run --cap-drop ALL. VERIFY: docker exec container cat /proc/self/status | grep Cap -> all zeros. WHEN CAPS ARE NEEDED: ping binary needs CAP_NET_RAW (raw ICMP socket), tcpdump needs CAP_NET_RAW, anything binding to port <1024 needs CAP_NET_BIND_SERVICE, anything that needs to set filesystem ownership needs CAP_CHOWN. THE --CAP-ADD PATTERN: Instead of running as root, use: --cap-drop ALL then --cap-add only_what_needed. More explicit and auditable. The security checklist: (1) Is the container running as non-root? (2) Has --cap-drop ALL been set? (3) What specific caps are added back and why? (4) Is --security-opt no-new-privileges set? (no setuid, no file cap escalation). (5) Is the seccomp profile restricting dangerous syscalls? This checklist = container security baseline for any production environment.
