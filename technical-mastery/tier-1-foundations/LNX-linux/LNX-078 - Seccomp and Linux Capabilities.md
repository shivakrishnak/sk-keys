---
id: LNX-078
title: "Seccomp and Linux Capabilities"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★★
depends_on: LNX-071, LNX-022
used_by: LNX-079, LNX-080, LNX-108
related: LNX-071, LNX-079, LNX-080
tags: [seccomp, capabilities, CAP_NET_ADMIN, setcap, getcap, prctl, capability-bounding-set, sandbox, container-security, BPF-filter, least-privilege]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 78
permalink: /technical-mastery/lnx/seccomp-linux-capabilities/
---

## TL;DR

**Capabilities** split root privilege into 37 distinct capabilities
(`CAP_NET_BIND_SERVICE`, `CAP_SYS_ADMIN`, `CAP_NET_ADMIN`, etc.). A process
can have specific capabilities without being full root. `setcap` adds capabilities
to binaries (`setcap cap_net_bind_service=ep /usr/bin/myapp`). `getcap`,
`capsh --print`, `/proc/[pid]/status Cap*` to inspect. **Seccomp** (Secure
Computing) restricts which syscalls a process can make. Modes: strict (only
`read`, `write`, `exit`, `sigreturn`) or filter (BPF-based filter of any syscalls).
Docker default seccomp profile blocks ~44 dangerous syscalls. `strace -c`
to find syscalls used. Docker: `--cap-drop=ALL --cap-add=...` and
`--security-opt seccomp=profile.json` for custom policies.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-078 |
| **Difficulty** | ★★★ Advanced |
| **Category** | Linux |
| **Tags** | seccomp, capabilities, CAP_NET_ADMIN, setcap, prctl, BPF filter, container security, least privilege |
| **Prerequisites** | LNX-071 (Namespaces), LNX-022 (Process management) |

---

### The Problem This Solves

**Problem 1**: A web server needs to bind to port 80 (privileged port, <1024).
The old solution: run as root. The risk: if the process has a vulnerability,
attacker gains root. Modern solution: `setcap 'cap_net_bind_service=ep'
/usr/bin/nginx`. Nginx can bind to port 80 without being root, and without
any other root privileges.

**Problem 2**: A container runtime needs defense-in-depth against container
escapes. Even if an attacker achieves code execution inside a container,
they shouldn't be able to: load kernel modules (exploit kernel), create
raw sockets (network attacks), mount filesystems (access host). Seccomp
filters block specific syscalls (`init_module`, `socket(AF_PACKET)`, `mount`)
at the kernel boundary - the attack fails even if the container is compromised.

---

### Textbook Definition

**Linux Capabilities**: Fine-grained privilege decomposition (since kernel
2.2). Splits the traditionally monolithic root (UID=0) into ~37 distinct
privilege units. Each capability can be: PERMITTED (can be enabled), EFFECTIVE
(currently active), INHERITABLE (passed through exec), AMBIENT (preserved
across unprivileged exec), BOUNDING (ceiling - can't exceed this).

**Selected capability list:**
| Capability | What it allows |
|-----------|----------------|
| `CAP_NET_BIND_SERVICE` | Bind to ports < 1024 |
| `CAP_NET_ADMIN` | Interface config, routing, packet filtering |
| `CAP_NET_RAW` | Raw sockets, packet sniffing |
| `CAP_SYS_ADMIN` | Very broad: mount, namespace, ioctl, etc. |
| `CAP_SYS_PTRACE` | ptrace (strace, gdb) another process |
| `CAP_DAC_OVERRIDE` | Bypass file permission checks |
| `CAP_KILL` | Send signals to arbitrary processes |
| `CAP_SETUID` | Set any UID (change identity) |
| `CAP_SYS_CHROOT` | Use chroot() |
| `CAP_SYS_MODULE` | Load/unload kernel modules |

**Seccomp**: Secure Computing Mode. A kernel security mechanism that filters
syscalls using BPF (Berkeley Packet Filter) programs. Mode 1 (strict): only
4 syscalls allowed, rest cause SIGKILL. Mode 2 (filter): BPF program decides
per-syscall: ALLOW, KILL, ERRNO, TRAP.

---

### Understand It in 30 Seconds

```bash
# === Capabilities: inspect and manage ===

# Check your own capabilities:
capsh --print
# Current: = cap_chown,cap_dac_override,...,cap_sys_admin+eip
# Bounding set = cap_chown,...,cap_sys_admin

# Check capabilities of a process:
cat /proc/self/status | grep -i cap
# CapInh: 0000000000000000   <- inheritable
# CapPrm: 0000000000000000   <- permitted
# CapEff: 0000000000000000   <- effective (non-root: 0 = no capabilities)
# CapBnd: 000001ffffffffff   <- bounding (ceiling)
# CapAmb: 0000000000000000   <- ambient

# Decode capability bitmask:
capsh --decode=000001ffffffffff   # shows list of capabilities

# Check capabilities on a file:
getcap /usr/bin/ping
# /usr/bin/ping = cap_net_raw+ep  <- ping has cap_net_raw effective+permitted

# Set file capabilities (need root):
setcap 'cap_net_bind_service=ep' /usr/bin/myapp   # allow binding port < 1024
setcap -r /usr/bin/myapp                           # remove capabilities

# Check what capabilities a user-space process has:
getpcaps <PID>
# PID: = cap_net_bind_service+ep

# === Least-privilege example: nginx on port 80 ===
# Option A: File capability:
setcap 'cap_net_bind_service=ep' /usr/sbin/nginx
# Nginx can bind port 80, runs as nobody/www-data, no root needed

# Option B: Use authbind:
# Option C: Use iptables REDIRECT (root to start, then drop privileges)
# Option D: Use setuid bit (old, avoid - gives full EUID=0)

# === Drop all capabilities in a script ===
# prctl to drop capabilities:
capsh --drop=cap_sys_admin,cap_net_admin -- -c "exec myapp"

# === Docker: capability management ===
# Default Docker: drops most capabilities, keeps minimum set
docker run --cap-drop=ALL --cap-add=NET_BIND_SERVICE nginx
# --cap-drop=ALL: remove ALL default capabilities
# --cap-add=NET_BIND_SERVICE: add only what's needed

# View capabilities inside container:
docker run --rm nginx:latest capsh --print

# === Seccomp: syscall filtering ===
# View current seccomp mode:
cat /proc/self/status | grep Seccomp
# Seccomp: 0  <- 0=no filter, 1=strict, 2=filter mode

# Apply strict seccomp (dangerous - only 4 syscalls allowed!):
# prctl(PR_SET_SECCOMP, SECCOMP_MODE_STRICT);
# Only read(), write(), exit(), sigreturn() allowed
# Everything else: SIGKILL (process killed immediately)

# Docker default seccomp profile:
# Blocks ~44 syscalls including:
# kexec_load, init_module, delete_module (kernel modification)
# ptrace (process tracing from container)
# clone with CLONE_NEWUSER without privileges (user namespace creation)
# open_by_handle_at (can be used to escape chroot)
# perf_event_open, bpf (prevent eBPF from container)

# Use a custom seccomp profile:
docker run --security-opt seccomp=/path/to/profile.json myapp

# Disable seccomp entirely (permissive, for debugging):
docker run --security-opt seccomp=unconfined myapp

# === Find what syscalls your app uses ===
# Use strace to list syscalls:
strace -c -p <PID>   # -c: count syscalls (summary)
# After Ctrl-C:
# % time     seconds  usecs/call     calls    errors syscall
# 43.59    0.001234          12       100           read
# 30.21    0.000856           8       107           write
# ...

# Or: perf trace (lower overhead than strace):
perf trace --summary -p <PID> -- sleep 10
```

---

### First Principles

**Capability sets explained:**
```
Each process has 5 capability sets:

PERMITTED (P): capabilities the process CAN enable
  If a capability is not in Permitted: process can NEVER have it
  (not even by being setuid root, if the bounding set doesn't include it)

EFFECTIVE (E): capabilities currently active (checked on privileged ops)
  A syscall checks Effective: does process have CAP_NET_BIND_SERVICE?
  Process can toggle capabilities between Permitted and Effective
  (using prctl(PR_SET_KEEPCAPS) or capset())

INHERITABLE (I): capabilities that CAN be inherited across execve()
  If CAP_NET_ADMIN is in Inheritable: child exec() can inherit it
  Default: Inheritable is 0 (nothing inherited, must be explicit)

BOUNDING (B): hard ceiling for Permitted
  A capability not in Bounding can NEVER be in Permitted
  Even if binary has setcap cap_sys_admin: if not in Bounding, blocked
  Used to permanently restrict what a process tree can gain

AMBIENT (A): capabilities preserved across unprivileged execve()
  New in kernel 4.3
  Allows passing capabilities to child processes without setuid/setcap
  (older alternative: setuid root binary or setcap on executable)

Inheritance rules on exec():
  New_Permitted  = (Old_Inheritable & File_Inheritable) | (File_Permitted & Old_Bounding)
  New_Effective  = File_Effective ? New_Permitted : (Ambient)
  New_Inheritable = Old_Inheritable
  New_Ambient    = (prctl_set) ? Old_Ambient : 0

Simplified:
  - File capability (+ep) = process inherits it if binary has it
  - Without file cap: capabilities NOT inherited across exec()
  - This is why setuid programs need file capabilities or SETUID bit

Real-world: nginx needs CAP_NET_BIND_SERVICE:
  Binary: setcap 'cap_net_bind_service=+ep' /usr/sbin/nginx
    File_Permitted = cap_net_bind_service
    File_Effective = yes (e flag)
  Process started as non-root:
    New_Permitted = File_Permitted (intersection with bounding) = cap_net_bind_service
    New_Effective = cap_net_bind_service (e flag means yes)
  Result: nginx runs as non-root with cap_net_bind_service effective
```

**Seccomp-BPF mechanism:**
```
Process installs seccomp filter (BPF program) via:
  prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER, &prog);
  or: syscall(SYS_seccomp, SECCOMP_SET_MODE_FILTER, 0, &prog);

On every syscall:
  1. CPU saves registers (syscall number, args)
  2. Kernel checks: is seccomp enabled for this process?
  3. YES: execute the BPF filter program
     BPF program receives: arch, syscall number, args
     BPF program returns one of:
       SECCOMP_RET_ALLOW: proceed normally
       SECCOMP_RET_KILL_PROCESS: kill entire process immediately
       SECCOMP_RET_KILL_THREAD: kill calling thread
       SECCOMP_RET_ERRNO | errno: return error to caller
       SECCOMP_RET_TRAP: send SIGSYS to process
       SECCOMP_RET_TRACE: notify ptrace tracer

Filter example (simplified pseudo-BPF):
  if arch != X86_64: KILL (prevent 32-bit bypass)
  if syscall == sys_kexec_load: ERRNO(EPERM)
  if syscall == sys_init_module: ERRNO(EPERM)
  if syscall == sys_mount: ERRNO(EPERM)
  else: ALLOW

OCI container runtimes (runc, containerd):
  Load seccomp profile from OCI spec (config.json)
  Install the BPF filter for the container init process
  All container processes (children) inherit the filter
  Filter is additive: child processes can only RESTRICT further

Seccomp overhead:
  BPF filter: ~200-300 ns per syscall (JIT-compiled BPF)
  vs no seccomp: 0 ns
  For I/O-bound apps making millions of syscalls: measurable
  For most apps: negligible (<1% CPU)
```

---

### Thought Experiment

Building a minimal capability set for a web application:

```bash
#!/bin/bash
# Security hardening: minimal capabilities for a Java web application

BINARY=/usr/bin/java

# Step 1: What syscalls does our app use?
# Run the app and capture syscall list:
strace -c -f -e trace=all java -jar myapp.jar &
APP_PID=$!
sleep 30
kill $APP_PID

# Step 2: What capabilities does it need?
# Test with minimal capabilities:
docker run \
    --user nobody \
    --cap-drop=ALL \
    --cap-add=NET_BIND_SERVICE \
    myapp

# If startup fails: add capabilities one by one until it works
# Common needs for web apps:
#   NET_BIND_SERVICE: port < 1024 (or use port > 1024, avoids this need)
#   SETUID, SETGID: if dropping privileges after startup
#   DAC_OVERRIDE: if writing to log files with wrong permissions

# Step 3: Create seccomp profile for our app
# Start with Docker's default profile and add/remove as needed:
docker run --security-opt seccomp=/etc/docker/seccomp.json \
    --cap-drop=ALL \
    --cap-add=NET_BIND_SERVICE \
    myapp

# Step 4: Document the final minimal configuration
cat > /etc/docker/myapp-security.json << 'EOF'
{
  "defaultAction": "SCMP_ACT_ERRNO",
  "syscalls": [
    {
      "names": ["read", "write", "open", "close", "fstat", "mmap",
                "mprotect", "munmap", "brk", "socket", "connect",
                "accept", "sendto", "recvfrom", "bind", "listen",
                "getsockname", "getpeername", "setsockopt", "getsockopt",
                "clone", "fork", "execve", "exit", "exit_group",
                "futex", "nanosleep", "getpid", "getuid", "getgid",
                "select", "epoll_wait", "epoll_create1", "epoll_ctl"],
      "action": "SCMP_ACT_ALLOW"
    }
  ]
}
EOF
```

---

### Mental Model / Analogy

```
Capabilities = employee access card system

Old system (UID=0): "Master key holder"
  One person has a key that opens EVERY door in the building
  If that person's key is stolen: complete building compromise
  "Root privilege" = this master key

New system (capabilities): "Role-based access cards"
  Receptionist (web server): card opens front door + meeting rooms
    = CAP_NET_BIND_SERVICE (open port 80) + file access
  Network admin: card opens network equipment room
    = CAP_NET_ADMIN (configure interfaces)
  IT admin: card opens server room
    = CAP_SYS_ADMIN (manage system)
  
  If receptionist's card is compromised:
    Attacker can enter front door and meeting rooms ONLY
    Cannot access server room (no CAP_SYS_ADMIN card)
    Blast radius: limited to receptionist's access level

setcap = issuing access cards to programs (not people):
  setcap 'cap_net_bind_service=ep' /usr/bin/nginx
  = issue a card to nginx that opens port 80 doors ONLY
  nginx runs as non-root, but has the right card for its job

Seccomp = airport security checkpoint

Passengers (processes) must pass through security
Security rules = seccomp filter (BPF program)
  
  Allowed actions (syscalls):
    read, write (board plane = normal operation)
    socket (make phone calls = network allowed)
  
  Blocked actions:
    init_module (bring bomb aboard = load kernel module)
    ptrace (spy on other passengers = trace other processes)
    mount (rearrange the airport = mount filesystems)
  
  When blocked syscall attempted:
    KILL: passenger immediately removed (SIGKILL)
    ERRNO: "Security denied, try again another way" (EPERM)
    TRAP: trigger alarm, security investigates (SIGSYS)

Layers together: capabilities + seccomp = defense in depth
  Capabilities: "here's what roles this process has"
  Seccomp: "here's exactly what it can ask the kernel to do"
  Even if capabilities are correct, seccomp limits blast radius further
```

---

### Gradual Depth - Five Levels

**Level 1:**
Capabilities concept: split root into granular privileges. Common caps:
`cap_net_bind_service`, `cap_net_admin`, `cap_sys_admin`. `getcap`/`setcap`.
Docker `--cap-drop=ALL --cap-add`. Seccomp: restricts syscalls. Docker default
seccomp profile.

**Level 2:**
5 capability sets: Permitted, Effective, Inheritable, Bounding, Ambient.
`/proc/[pid]/status Cap*` fields. `capsh --decode`. Capability inheritance
rules across `exec()`. Seccomp modes: strict vs filter (BPF). `prctl(PR_SET_SECCOMP)`.
`strace -c` to find syscall usage.

**Level 3:**
File capabilities (`+ep`, `+ip`, flags). Ambient capabilities (kernel 4.3).
Seccomp-BPF return values: ALLOW, KILL, ERRNO, TRAP, TRACE. Building custom
seccomp profiles. OCI runtime spec (config.json) capabilities and seccomp
sections. `libseccomp` API for writing seccomp filters in C. Kubernetes
securityContext: `capabilities` and `seccompProfile`.

**Level 4:**
Capability bounding set manipulation (can only reduce, never increase without
root). `PR_CAP_AMBIENT` prctl for ambient capabilities. Capability checking
in kernel: `capable()`, `ns_capable()` (namespace-aware). Seccomp filter
inheritance: child processes inherit parent's filter (additive only, can't
loosen). Performance impact of seccomp BPF on high-syscall-rate applications.
Combining seccomp + capabilities + namespace + AppArmor/SELinux for defense
in depth.

**Level 5:**
Capability-aware privilege escalation paths: capabilities that effectively
give root (`CAP_SYS_ADMIN` -> mount /proc from host, `CAP_NET_ADMIN` ->
ARP spoofing, `CAP_DAC_OVERRIDE` -> overwrite any file). Seccomp escape
techniques (historical CVEs using allowed syscalls). Kernel capabilities
in namespace context: `CAP_NET_ADMIN` in a network namespace = limited to
that namespace's interfaces (not host). `CAP_SYS_ADMIN` vs user namespace:
`CAP_SYS_ADMIN` in a user namespace ≠ full root (only for namespace-scoped ops).
Seccomp + hardware transient execution attacks (Spectre/Meltdown mitigation
via seccomp).

---

### Code Example

**BAD - capability and seccomp mistakes:**
```bash
# BAD 1: Running application as root to bind port 80:
# Dockerfile:
# USER root
# CMD ["./myapp", "--port", "80"]
# 
# If myapp has a vulnerability: attacker gains root shell in container
# With user namespace (non-rootless Docker): root in container = root on host
# -> Complete system compromise

# BAD 2: Using --privileged instead of specific capabilities:
docker run --privileged myapp   # grants ALL capabilities!
# Equivalent to running as root on the host
# Can: mount host filesystem, load kernel modules, access all devices
# Only needed for: hardware device access, specific kernel operations

# BAD 3: Not checking capability requirements before removing all:
docker run --cap-drop=ALL myapp
# App crashes with permission denied on startup
# "That didn't work, let me add everything back":
docker run --cap-drop=ALL --cap-add=ALL myapp   # defeats the purpose

# GOOD 1: Identify minimal capabilities, then enforce:
# Step 1: Run with all caps, trace what's needed:
strace -f -e trace=/ docker run myapp 2>&1 | grep "EPERM"
# Each EPERM = a capability check failing
# OR: test with progressively stripped capabilities

# GOOD 1: Production nginx with minimal capabilities:
docker run \
    --user 1000:1000 \
    --cap-drop=ALL \
    --cap-add=NET_BIND_SERVICE \   # needed if binding port 80
    --security-opt=no-new-privileges \
    --read-only \
    --tmpfs /tmp:size=100m \
    nginx:alpine
# no-new-privileges: prevents gaining privileges via setuid/setcap inside
```

**GOOD - seccomp profile development:**
```bash
# Step 1: Trace syscalls used by the application:
# Method A: strace (high overhead, for development):
strace -c -f -q -- ./myapp 2>&1 | tail -30
# % time     seconds  usecs/call     calls    errors syscall
# Shows which syscalls are used and how often

# Method B: perf trace (lower overhead):
perf trace -a -o /tmp/syscalls.log -- sleep 60 &
# Then: analyze /tmp/syscalls.log

# Method C: eBPF (production-safe, lowest overhead):
bpftrace -e '
tracepoint:raw_syscalls:sys_enter /pid == target_pid/ {
    @[str(args->id)] = count();
}
' | sort > /tmp/syscall_counts.txt

# Step 2: Generate seccomp profile from traced syscalls:
# Install: oci-seccomp-bpf-hook or similar tool
# OR: manually build the allowlist:

cat > myapp-seccomp.json << 'SECCOMP'
{
  "defaultAction": "SCMP_ACT_ERRNO",
  "architectures": ["SCMP_ARCH_X86_64"],
  "syscalls": [
    {
      "names": [
        "accept4", "bind", "brk", "clock_gettime", "clone",
        "close", "connect", "epoll_create1", "epoll_ctl",
        "epoll_wait", "exit", "exit_group", "fcntl", "fstat",
        "futex", "getpid", "gettid", "listen", "mmap", "mprotect",
        "munmap", "nanosleep", "open", "openat", "read", "recvfrom",
        "recvmsg", "rt_sigaction", "rt_sigprocmask", "select",
        "sendmsg", "sendto", "set_robust_list", "setsockopt",
        "shutdown", "socket", "stat", "write", "writev"
      ],
      "action": "SCMP_ACT_ALLOW"
    }
  ]
}
SECCOMP

# Step 3: Apply and test:
docker run --security-opt seccomp=myapp-seccomp.json myapp
# If app fails: check which syscall was blocked (EPERM or SIGSYS)
# Add that syscall to the allowlist and retry

# Kubernetes securityContext with seccomp:
# apiVersion: v1
# kind: Pod
# spec:
#   securityContext:
#     seccompProfile:
#       type: RuntimeDefault   # use container runtime's default profile
#   containers:
#     - name: myapp
#       securityContext:
#         capabilities:
#           drop: ["ALL"]
#           add: ["NET_BIND_SERVICE"]
#         allowPrivilegeEscalation: false
#         readOnlyRootFilesystem: true
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "`CAP_SYS_ADMIN` is just for system administration, not a serious risk" | `CAP_SYS_ADMIN` is the most dangerous capability - it's sometimes called "the new root." It allows: mounting filesystems (including the host filesystem from a container), creating namespaces (can be combined with privilege escalation), making arbitrary ioctl calls to devices, managing cgroups, overriding disk quotas, and many other operations. A container with `CAP_SYS_ADMIN` can: `mount -o bind / /mnt` (mount host root), `nsenter --target 1 --mount` (enter host mount namespace). When security reviewers see `CAP_SYS_ADMIN`, they treat it as equivalent to root for practical purposes. The only accepted use case: when genuinely needed (e.g., FUSE filesystems, specific hardware interactions). |
| "Seccomp filter protects against any attack vector" | Seccomp filters the syscall INTERFACE but cannot protect against attacks using ALLOWED syscalls. A comprehensive seccomp profile allows common syscalls like `mmap`, `write`, `socket`. A vulnerability in an allowed operation (e.g., heap overflow in userspace application code that corrupts memory) is not blocked by seccomp. Seccomp is one layer: it prevents using dangerous kernel features (module loading, raw sockets), not user-space code vulnerabilities. The power of seccomp: prevent PRIVILEGE ESCALATION via kernel bugs (a bug in `kexec_load` can't be exploited if `kexec_load` is seccomp-blocked). Use alongside: capabilities, namespaces, AppArmor/SELinux for complete defense. |
| "File capabilities and setuid are equivalent security models" | They have different security properties. Setuid binary: when executed, process gains EUID=0 (all capabilities, full root). Any bug in the binary = full root compromise. File capability (setcap): process gains ONLY the specific capabilities set in the file, not root. A bug in an nginx binary with only `cap_net_bind_service` gives an attacker `cap_net_bind_service` only - far less dangerous than full root. Prefer file capabilities over setuid whenever possible. `chmod u+s` (setuid) is an all-or-nothing escalation; `setcap` is surgical. |
| "Dropping all capabilities makes a container as secure as a VM" | Capabilities and seccomp improve container isolation significantly, but containers still share the host kernel. Namespace and capability restrictions can potentially be bypassed via kernel vulnerabilities. VMs have a separate kernel (hypervisor boundary) making such escapes require hypervisor vulnerabilities (much rarer and harder). Defense-in-depth approach: capabilities + seccomp + LSM (AppArmor/SELinux) + user namespaces = substantially reduced attack surface. But the fundamental difference remains: containers share a kernel, VMs don't. |

---

### Failure Modes & Diagnosis

**Capability permission issues:**
```bash
# Symptom: "Operation not permitted" when process tries to bind port 80
curl -v http://myapp:80    # connection refused
# Container logs: "bind: permission denied (port 80)"

# Diagnosis 1: Check what capabilities the process has:
docker exec myapp capsh --print
# Or: cat /proc/<pid>/status | grep Cap
# Decode: capsh --decode=$(grep CapEff /proc/<pid>/status | awk '{print $2}')
# If cap_net_bind_service not in CapEff: it's missing

# Fix: add capability at container level:
docker run --cap-add=NET_BIND_SERVICE myapp

# Alternative fix: change app to use port > 1024 (no cap needed):
# Use reverse proxy (nginx/traefik) to forward 80 -> 8080

# Symptom: "Operation not permitted" when running strace inside container
docker exec myapp strace ls
# strace: attach: ptrace(PTRACE_SEIZE, 1, ...): Operation not permitted

# Diagnosis: strace requires CAP_SYS_PTRACE:
docker exec myapp capsh --print | grep ptrace
# Not in capabilities

# Fix for debugging (development only):
docker run --cap-add=SYS_PTRACE myapp

# Symptom: seccomp blocks a necessary syscall
# Error in application: "EPERM" or "Function not implemented"
docker logs myapp | grep -E "EPERM|ENOSYS|not implemented"

# Find which syscall was blocked:
# Enable SIGSYS (sends signal instead of kill):
# In seccomp profile: change "SCMP_ACT_ERRNO" to "SCMP_ACT_TRAP" for testing
# Then: dmesg | grep "audit: type=1326" (seccomp audit log)
# Shows syscall number + process that triggered it
```

---

### Related Keywords

**Foundational:**
LNX-071 (Namespaces), LNX-022 (Process management)

**Builds on this:**
LNX-079 (LSM, SELinux, AppArmor), LNX-080 (Container internals), LNX-108 (Multi-tenant security)

**Related:**
LNX-064 (Audit subsystem), LNX-090 (Linux Capabilities in Depth)

---

### Quick Reference Card

| Command | Purpose |
|---------|---------|
| `getcap /bin/myapp` | Show file capabilities |
| `setcap 'cap_net_bind_service=ep' /bin/myapp` | Set file capability |
| `capsh --print` | Show current process capabilities |
| `capsh --decode=<hex>` | Decode capability bitmask |
| `cat /proc/PID/status \| grep Cap` | Raw capability bitmasks |
| `getpcaps PID` | Capabilities for a PID |
| `docker run --cap-drop=ALL --cap-add=X` | Minimal Docker capabilities |
| `docker run --security-opt seccomp=profile.json` | Custom seccomp |
| `strace -c -f -- cmd` | Find syscalls used by command |

**3 things to remember:**
1. Capabilities split root into granular privileges: `setcap cap_net_bind_service=ep` instead of running as root
2. `CAP_SYS_ADMIN` = effectively root; treat with same caution as root access
3. Seccomp blocks syscalls BEFORE they reach the kernel - defense against kernel exploits, not user-space bugs

---

### Transferable Wisdom

Capability model appears in: Android's capability-based permission system
(apps request specific permissions, granted individually). AWS IAM policies:
same principle - least privilege, grant specific actions only. Kubernetes RBAC:
same design - grant specific verbs on specific resources. The principle of
least privilege is universal across security systems. Seccomp is used in:
Chrome's renderer sandboxing (each tab uses seccomp to restrict syscalls),
VSCode extension sandbox, OpenSSH's privilege separation (sandbox for
cryptographic operations). The syscall-allowlist vs blocklist debate:
allowlist (only permit known-good) is more secure but requires more
maintenance; blocklist (deny known-bad) is easier but misses unknown-bad.
Docker's default seccomp is a blocklist (deny dangerous syscalls); custom
application profiles should use allowlists. Building seccomp profiles from
`strace -c` output is the practical starting point - trace what your app
needs, build an allowlist from that. Platform engineers: Kubernetes Pod
Security Standards (Baseline, Restricted profiles) enforce capabilities and
seccomp requirements at the cluster policy level.

---

### The Surprising Truth

The Linux capability system has a well-known design flaw that has never been
fully fixed: `CAP_SYS_ADMIN` is so broadly defined that it's often called
"the new root." When capabilities were designed in 1999, the goal was to split
root into fine-grained privileges. `CAP_SYS_ADMIN` was intended as a
"miscellaneous system administration" capability for the rare operations that
didn't fit elsewhere. Over the years, new kernel features kept being added
to `CAP_SYS_ADMIN` as a catch-all, making it more powerful than intended.
Today, `CAP_SYS_ADMIN` allows: mounting filesystems (including the host FS
from a container), creating cgroups, manipulating namespaces, loading kernel
modules via `bpf()`, using device IOCTL operations, and more. Any container
with `CAP_SYS_ADMIN` can potentially escape to the host. The Kubernetes
documentation for many features (CSI drivers, certain CNI plugins, debugging
tools) says "requires privileged container" or "requires CAP_SYS_ADMIN" -
making it tempting to grant broadly. The correct response is always to investigate
the SPECIFIC requirement: does the feature truly need `CAP_SYS_ADMIN`, or
does it need a more specific capability or namespace operation? The principle:
treat any request for `CAP_SYS_ADMIN` with the same scrutiny as a request
for root access.

---

### Mastery Checklist

- [ ] Can use `getcap`, `setcap`, `capsh --print` to inspect and modify file/process capabilities
- [ ] Understands the 5 capability sets (Permitted, Effective, Inheritable, Bounding, Ambient)
- [ ] Knows why `CAP_SYS_ADMIN` is dangerous and should be avoided
- [ ] Can use Docker `--cap-drop=ALL --cap-add=specific` for minimal-privilege containers
- [ ] Can use `strace -c` to identify syscalls for seccomp profile development

---

### Think About This

1. A new deployment requires running a container that captures network packets
   for traffic analysis (like Wireshark). The team wants to grant `--privileged`
   for simplicity. Explain what specific capabilities are actually needed
   (`CAP_NET_ADMIN`, `CAP_NET_RAW`, `CAP_SYS_ADMIN`?), which ones are required
   and which aren't, and what the security risks of each are. Write the
   correct `docker run` command with minimal capabilities.

2. Design a security profile for a Java Spring Boot application that: (a) serves
   HTTP on port 8080 (no privileged port needed), (b) makes outbound HTTPS
   connections, (c) writes logs to /var/log/myapp/, (d) reads a config file
   from /etc/myapp/. What capabilities does it need? What syscalls would
   you include in a seccomp allowlist (hint: use strace categories)? Write
   the Kubernetes securityContext YAML.

3. A security audit finds that a container in your cluster has `CAP_SYS_ADMIN`
   and no seccomp profile. The container runs a custom FUSE filesystem.
   Explain why `CAP_SYS_ADMIN` might be genuinely required here (what
   specific operations does FUSE need?), what mitigations you can add to
   reduce risk even with `CAP_SYS_ADMIN`, and when you might accept this
   risk vs. when you should redesign the architecture.

---

### Interview Deep-Dive

**Foundational:**
Q: What are Linux capabilities and why are they preferred over running processes as root?
A: Linux capabilities split the traditionally monolithic "root" privilege (UID=0) into ~37 discrete privilege units, each controlling a specific set of privileged operations. Background: historically, privilege was binary - a process was either unprivileged (UID≠0, restricted) or root (UID=0, unrestricted). This all-or-nothing model violates the principle of least privilege: a web server needs to bind port 80 but doesn't need to load kernel modules, modify routing tables, or overwrite any file. Capabilities solve this: `CAP_NET_BIND_SERVICE` = "can bind ports < 1024." `CAP_NET_ADMIN` = "can configure network interfaces." `CAP_SYS_MODULE` = "can load kernel modules." PRACTICAL EXAMPLE: Running nginx to serve port 80. Without capabilities: must run as root. If nginx has a vulnerability: attacker gains root - full system compromise. With capabilities: `setcap 'cap_net_bind_service=ep' /usr/sbin/nginx`. Nginx runs as www-data (UID 33). Has `cap_net_bind_service` only. Vulnerability gives attacker: UID 33 + cap_net_bind_service = very limited. Cannot: load modules, modify other processes, access arbitrary files. Blast radius reduced dramatically. The 5 capability sets per process: Effective (active), Permitted (can be activated), Inheritable (passed through exec), Bounding (ceiling), Ambient (preserved across unprivileged exec). The rule: check before implementing anything as root - which specific capability do you actually need? `CAP_NET_BIND_SERVICE`, `CAP_SETUID`, `CAP_DAC_OVERRIDE` cover 90% of legitimate use cases without needing full root.

**Expert:**
Q: How does seccomp-BPF work, and how would you create a minimal seccomp profile for a production application?
A: Seccomp-BPF (Secure Computing with BPF filters) is a kernel mechanism that restricts which system calls a process can make. Mechanism: a process installs a BPF program via `prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER, &bpf_prog)`. On every syscall: the BPF program receives the syscall number, arguments, and architecture. It returns a verdict: ALLOW (proceed), KILL (SIGKILL process), ERRNO|N (return error N to caller), TRAP (send SIGSYS). The BPF program is JIT-compiled to native code: ~200-300ns overhead per syscall. Filter inheritance: child processes inherit the parent's filter (additive only - children can only RESTRICT further, not loosen). BUILDING A PROFILE: Step 1: Profile the application. Use `strace -c -f -- ./myapp` (development) or `bpftrace -e 'tracepoint:raw_syscalls:sys_enter /pid==PID/ {@[args->id]=count()}'` (low-overhead). This gives the complete syscall set used. Step 2: Build an allowlist. Start with the traced syscalls. Add commonly needed syscalls: `futex` (threading), `mmap`/`munmap` (memory), `brk` (heap), `read`/`write`, `open`/`close`, `exit_group`. Important: always include `read`, `write`, `exit`/`exit_group` (need them to even fail gracefully). Step 3: Add architecture check. BPF filter should: if (arch != X86_64) return KILL. Prevents 32-bit syscall table bypass (different numbers). Step 4: Handle logging. Use SCMP_ACT_ERRNO (return error) not KILL during development - easier to debug. Switch to KILL for production critical paths. Step 5: Test. Run with `SCMP_ACT_TRAP` to get SIGSYS on blocked calls, log which syscalls are missing from your profile. PRODUCTION CONSIDERATIONS: Docker default profile blocks ~44 dangerous syscalls (kexec_load, init_module, mount, open_by_handle_at). For application-specific profiles: use OCI seccomp spec in Docker/Kubernetes. Kubernetes: `seccompProfile: {type: RuntimeDefault}` uses the container runtime's default (equivalent to Docker's default). `seccompProfile: {type: Localhost, localhostProfile: myprofile.json}` for custom. The allowlist approach (deny everything, allow specific) is more secure than Docker's default blocklist. Trade-off: maintenance overhead (update profile when app adds syscalls) vs security gain (minimal attack surface).
