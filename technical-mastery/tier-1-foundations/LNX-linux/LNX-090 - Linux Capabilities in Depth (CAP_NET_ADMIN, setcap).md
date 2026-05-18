---
id: LNX-090
title: "Linux Capabilities in Depth (CAP_NET_ADMIN, setcap)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★★
depends_on: LNX-078, LNX-009
used_by: LNX-108, LNX-100
related: LNX-078, LNX-079, LNX-009, LNX-100
tags: [linux-capabilities, cap-net-admin, cap-dac-override, cap-setuid, setcap, capsh, no-new-privs, ambient-capabilities, bounding-set, effective-permitted-inheritable, docker-capabilities, kubernetes-securitycontext, prctl, cap-sys-admin]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 90
permalink: /technical-mastery/lnx/linux-capabilities-in-depth/
---

## TL;DR

Linux capabilities split root privileges into 40+ fine-grained units. Key
dangerous capabilities: **`CAP_DAC_OVERRIDE`** (bypass all file permission
checks - effectively root on file access), **`CAP_SETUID`** (become any user
- full root equivalent), **`CAP_SYS_ADMIN`** (mount, sethostname, 30+ root ops -
informally called "almost root"), **`CAP_NET_ADMIN`** (interface config,
routing, iptables, packet capture). Assign to binary: `setcap cap_net_admin+ep
/usr/sbin/tcpdump`. View: `getcap /usr/sbin/tcpdump`. Thread sets: effective
(active), permitted (can activate), inheritable (passed to child exec).
**Ambient capabilities** (kernel 4.3): capabilities inherited across exec by
non-root processes via `prctl(PR_CAP_AMBIENT_RAISE)`. **No-new-privileges**:
`prctl(PR_SET_NO_NEW_PRIVS)` prevents gaining capabilities via setuid/setcap
binaries - most secure containers use this. Docker default: drops most
capabilities, keeps 14 essential ones.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-090 |
| **Difficulty** | ★★★ Advanced |
| **Category** | Linux |
| **Tags** | capabilities, CAP_NET_ADMIN, CAP_SYS_ADMIN, setcap, capsh, ambient capabilities, no-new-privileges, bounding set, Docker, Kubernetes securityContext |
| **Prerequisites** | LNX-078 (Seccomp and capabilities intro), LNX-009 (File permissions) |

---

### The Problem This Solves

**Problem 1**: `tcpdump` needs raw socket access (normally root-only) but
running `tcpdump` as root on production servers is dangerous (root can do
anything). Without capabilities: security policy forces choice between "no
packet capture" or "full root access." With capabilities: `setcap
cap_net_raw,cap_net_admin+ep /usr/sbin/tcpdump`. Now non-root users can
run tcpdump (packet capture works), but tcpdump cannot modify files, change
passwords, or perform any other root-only operations. Principle of least
privilege: process gets exactly the capabilities it needs, nothing more.

**Problem 2**: A containerized app is running as root (UID 0) for "convenience."
Security team finds that if the container is compromised: attacker has
`CAP_SYS_ADMIN` (can mount host filesystems, change namespaces, escape
container). Fix: drop `CAP_SYS_ADMIN` plus all unnecessary capabilities
in the Docker run command or Kubernetes securityContext. Container runs as
UID 0 but with severely limited capabilities - "root without power."

---

### Textbook Definition

**Linux capabilities**: A mechanism that divides the superuser (root, UID 0)
privilege into distinct units (capabilities). Each capability is independently
assignable to processes and binaries. A process can have some capabilities
without having all of root's powers.

**Capability sets per thread:**
| Set | Purpose |
|-----|---------|
| **Permitted (P)** | Maximum capabilities the thread may ever use |
| **Effective (E)** | Currently active capabilities (checked by kernel) |
| **Inheritable (I)** | Capabilities preserved across `execve()` (for root) |
| **Ambient (A)** | (Kernel 4.3+) Capabilities inherited across exec by non-root |
| **Bounding (B)** | Upper limit: no exec can grant caps beyond bounding set |

**Key capabilities (most dangerous to least):**
| Capability | Power | Risk |
|-----------|-------|------|
| `CAP_SYS_ADMIN` | mount, sethostname, ptrace, keyctl, 30+ ops | Escape container |
| `CAP_SETUID` | Become any UID | Full root equivalent |
| `CAP_DAC_OVERRIDE` | Bypass file permission checks | Read any file |
| `CAP_NET_ADMIN` | Interface config, routing, iptables | Network attack |
| `CAP_SYS_PTRACE` | Trace any process | Read/write any process memory |
| `CAP_NET_RAW` | Raw sockets (tcpdump, ping) | Network sniffing |
| `CAP_CHOWN` | Change file ownership | Escalate ownership |
| `CAP_SETGID` | Change GID arbitrarily | Group escalation |
| `CAP_LINUX_IMMUTABLE` | Set file immutable flag | Block deletion/modification |
| `CAP_NET_BIND_SERVICE` | Bind ports < 1024 | Limited (common use case) |

---

### Understand It in 30 Seconds

```bash
# === Assign capabilities to a binary ===

# tcpdump: needs CAP_NET_RAW (raw sockets) and CAP_NET_ADMIN:
setcap 'cap_net_raw,cap_net_admin+ep' /usr/sbin/tcpdump
# +ep: add to Effective and Permitted sets

# View capabilities on a binary:
getcap /usr/sbin/tcpdump
# /usr/sbin/tcpdump = cap_net_admin,cap_net_raw+ep

# Remove capabilities from a binary:
setcap -r /usr/sbin/tcpdump   # remove all

# Run tcpdump as non-root (works now):
tcpdump -i eth0    # no sudo needed!

# === Inspect process capabilities ===

# View current process capabilities:
capsh --print
# Current: =
# Bounding set =cap_chown,cap_dac_override,...cap_sys_admin,...
# Ambient set =
# Current IAB: ...
# Securebits: 00/0x0/1'b0

# More readable format:
cat /proc/self/status | grep -i cap
# CapInh: 0000000000000000   <- inheritable (hex bitmask)
# CapPrm: 0000001fffffffff   <- permitted
# CapEff: 0000001fffffffff   <- effective
# CapBnd: 0000001fffffffff   <- bounding set
# CapAmb: 0000000000000000   <- ambient

# Decode bitmask (requires libcap or capsh):
capsh --decode=0000001fffffffff
# = cap_chown,cap_dac_override,...,cap_sys_admin,cap_sys_time

# View capabilities of another process:
cat /proc/12345/status | grep Cap

# === Drop capabilities programmatically ===
# In C:
# #include <sys/prctl.h>
# #include <sys/capability.h>
#
# // Drop CAP_NET_ADMIN from effective set:
# cap_t caps = cap_get_proc();
# cap_value_t drop_caps[] = { CAP_NET_ADMIN };
# cap_set_flag(caps, CAP_EFFECTIVE, 1, drop_caps, CAP_CLEAR);
# cap_set_proc(caps);
# cap_free(caps);

# === Docker capabilities ===

# Docker default: drops many caps, adds 14 "essential" ones
# View default caps in a container:
docker run --rm ubuntu capsh --print
# Current: = cap_chown,cap_dac_override,...  <- 14 capabilities

# Drop ALL capabilities (most secure):
docker run --rm --cap-drop ALL ubuntu capsh --print
# Current: =  <- empty!

# Add back only what's needed:
docker run --rm --cap-drop ALL --cap-add NET_BIND_SERVICE nginx
# Has only NET_BIND_SERVICE (to bind port 80)

# Add dangerous capability (avoid in production!):
docker run --rm --cap-add SYS_ADMIN ubuntu capsh --print
# Current: = cap_chown,...,cap_sys_admin,...  <- SYS_ADMIN present!
# This gives container: mount, sethostname, keyctl, namespace changes
# Container breakout is significantly easier!

# === Kubernetes securityContext ===

# Kubernetes security context in pod spec:
cat << 'EOF'
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: app
    securityContext:
      capabilities:
        drop: ["ALL"]           # drop all capabilities
        add: ["NET_BIND_SERVICE"]  # add back only what's needed
      runAsNonRoot: true        # must not run as UID 0
      runAsUser: 1000           # run as UID 1000
      readOnlyRootFilesystem: true  # immutable filesystem
      allowPrivilegeEscalation: false  # = no-new-privileges
EOF

# === No-new-privileges ===

# Set no-new-privileges for current process:
# prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0)
# After this: process cannot gain additional capabilities
# via setuid binaries or setcap binaries

# Docker sets this by default since Docker 1.11:
docker run --security-opt=no-new-privileges nginx

# Verify:
docker run --rm alpine cat /proc/self/status | grep NoNewPrivs
# NoNewPrivs: 1  <- enabled

# === Ambient capabilities (kernel 4.3+) ===
# Allow non-root process to exec another binary with capabilities:

# Problem without ambient:
# Non-root process runs binary with setcap cap_net_raw+p
# Binary exec'd: effective caps drop to 0 (non-root can't keep inherited caps)

# Solution: ambient capabilities
# Parent process (root or cap_setpcap holder):
# prctl(PR_CAP_AMBIENT_RAISE, CAP_NET_RAW, 0, 0, 0);
# Child exec: ambient caps automatically become effective
# Child is non-root but has CAP_NET_RAW!

# systemd supports this:
# [Service]
# User=capture_user
# AmbientCapabilities=CAP_NET_RAW CAP_NET_ADMIN
# CapabilityBoundingSet=CAP_NET_RAW CAP_NET_ADMIN

# === Capability bounding set ===
# Remove cap from bounding set -> can never be gained by any exec:
capsh --drop=cap_net_admin -- -c "capsh --print | grep Bound"
# Bounding set = ... (no cap_net_admin)

# Permanent drop for a process + all children:
prctl(PR_CAPBSET_DROP, CAP_NET_ADMIN, 0, 0, 0)
# Even if running setuid root binary: cannot gain CAP_NET_ADMIN
```

---

### First Principles

**Capability sets and exec() transitions:**
```
Thread capability sets:
  - Permitted (P): maximum caps thread can ever have
  - Effective (E): caps currently checked by kernel
  - Inheritable (I): caps threads want to inherit across exec
  - Ambient (A): caps that automatically transfer across exec (4.3+)
  - Bounding (B): caps that can never be added beyond this set

On exec() (running a new binary):
  Old rules (no ambient):
    new_P = (old_I & file_I) | (file_P & bounding)
    new_E = file_effective ? new_P : {}
    new_I = old_I
  
  Where file capabilities (set via setcap):
    file_P: permitted caps of the binary
    file_I: inheritable caps of the binary
    file_effective: bit, if set E=P after exec
  
  Example: root runs setcap cap_net_raw+ep /usr/sbin/tcpdump
    file_P = {cap_net_raw}, file_effective = true
    
    Non-root exec of tcpdump:
      new_P = ({} & {}) | ({cap_net_raw} & bounding)
           = {cap_net_raw}  (because cap_net_raw in bounding)
      new_E = new_P (file_effective=true) = {cap_net_raw}
    
    Result: non-root tcpdump has CAP_NET_RAW effective!
            Can open raw sockets. No other caps.

Ambient capabilities (kernel 4.3+, for non-root inheritance):
  Problem: a non-root process wants to exec a helper that needs caps
  Old rules: inheritable only works for root processes
  
  Ambient solution:
    Parent (authorized): raise ambient cap
      prctl(PR_CAP_AMBIENT_RAISE, CAP_NET_RAW, ...)
    
    On exec:
      new_P includes ambient caps
      new_E includes ambient caps
      Non-root child has CAP_NET_RAW!
  
  Constraint: ambient cap must be in both permitted AND inheritable
  A process can only raise ambient caps it already has

setuid and capabilities interaction:
  Traditional setuid root (uid 0 in file):
    exec setuid-root-binary:
      Process: UID = 0
      All capabilities: granted (UID 0 = all caps historically)
    
    With CAP_SETUID: can setuid(0)
    
    No-new-privs (PR_SET_NO_NEW_PRIVS):
      Disables setuid and file capabilities on exec
      "This process can never gain capabilities it doesn't already have"
      Even executing setuid root binary: UID stays, no new caps
      Most secure containers use this + restricted initial caps

CAP_NET_ADMIN in depth:
  Allows:
    - Interface configuration: ip link, ifconfig
    - Routing table modification: ip route
    - iptables/nftables rules: iptables -A
    - Packet capture via raw sockets
    - Network namespace configuration
    - ARP cache manipulation
    - Network traffic shaping (tc)
    - Enable/disable promiscuous mode
    - Set MAC addresses
    - Administer IP tunnels
    - BPF filter attachment to network interfaces
  
  Security risk:
    - Capture ALL traffic on host (promiscuous mode on any interface)
    - Modify routing -> redirect traffic to attacker-controlled host
    - Modify iptables -> open firewall holes
    - Create network interfaces -> lateral movement capability
    - Attach eBPF programs to tc -> inspect/modify all packets
  
  Minimum scope: for apps that only need to bind to a privileged port:
    Use CAP_NET_BIND_SERVICE only (much less powerful)
    NOT CAP_NET_ADMIN (which grants much more)

CAP_SYS_ADMIN - the "almost root" capability:
  Originally a catch-all for many operations not categorized elsewhere
  Allows:
    - mount() / umount(): mount filesystems
    - sethostname() / setdomainname()
    - ioctl() for many device types
    - perf_event_open() (with paranoid setting)
    - prctl(PR_SET_SECCOMP) for some modes
    - keyctl() for key management
    - change network namespaces
    - setns(): join any namespace type
    - bpf() syscall operations
  
  Container escape path with CAP_SYS_ADMIN:
    mount -t proc proc /proc  -> see host processes
    setns() -> join host network namespace
    Or: write eBPF program to access host memory
  
  Modern alternative: specific caps split from CAP_SYS_ADMIN:
    CAP_PERFMON (kernel 5.8): perf events
    CAP_BPF (kernel 5.8): BPF operations
    CAP_CHECKPOINT_RESTORE (kernel 5.9): checkpoint/restore

Privilege escalation via capabilities audit:
  1. Find setcap binaries on system:
     find / -type f -executable 2>/dev/null | xargs getcap 2>/dev/null
     # Shows all binaries with capabilities
  
  2. Check for dangerous combinations:
     CAP_SYS_ADMIN: container escape
     CAP_DAC_OVERRIDE: read /etc/shadow (password hashes)
     CAP_NET_ADMIN: capture all traffic
     CAP_SETUID: sudo to root equivalent
  
  3. Audit Docker containers:
     docker inspect <container> | jq '.[0].HostConfig.CapAdd'
     docker inspect <container> | jq '.[0].HostConfig.CapDrop'
```

---

### Thought Experiment

Hardening a containerized application step by step:

```bash
# Initial (bad) state: container running with default Docker caps

# Step 1: Inventory current capabilities:
docker run --rm myapp capsh --print
# Current: = cap_chown,cap_dac_override,cap_fowner,cap_fsetid,
#   cap_kill,cap_setgid,cap_setuid,cap_setpcap,cap_net_bind_service,
#   cap_net_raw,cap_chown,cap_dac_read_search,cap_sys_chroot,
#   cap_mknod,cap_audit_write,cap_setfcap

# Default Docker includes cap_net_raw! Allows packet sniffing
# Includes cap_dac_override! Allows reading any file

# Step 2: Determine what the app actually needs:
# Analyze: what does myapp do?
# - Bind to port 8080: cap_net_bind_service NOT needed (> 1024)
# - Write to /var/log/app: needs write to specific dir, not cap_dac_override
# - Communicate over network: no special caps needed
# - Read its own config: no caps needed
# Conclusion: myapp needs ZERO capabilities!

# Step 3: Drop all capabilities:
docker run --rm \
    --cap-drop ALL \
    --security-opt no-new-privileges \
    --user 1000:1000 \
    --read-only \
    myapp

# Step 4: Check if app still works:
# If it crashes: find what it needs:
docker run --rm \
    --cap-drop ALL \
    --user 1000:1000 \
    --security-opt no-new-privileges \
    myapp 2>&1 | grep -i "permission denied\|operation not permitted"

# If needed: add back ONE capability at a time:
docker run --rm \
    --cap-drop ALL \
    --cap-add NET_BIND_SERVICE \  # app needs port 80 binding
    --user 1000:1000 \
    --security-opt no-new-privileges \
    myapp

# Step 5: Kubernetes securityContext equivalent:
cat << 'EOF' > secure-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: secure-app
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 1000
    seccompProfile:
      type: RuntimeDefault   # enables default seccomp profile
  containers:
  - name: app
    image: myapp:latest
    securityContext:
      allowPrivilegeEscalation: false   # no-new-privileges
      readOnlyRootFilesystem: true
      capabilities:
        drop: ["ALL"]
        add: []   # empty - no capabilities needed
EOF
kubectl apply -f secure-pod.yaml

# Step 6: Verify in Kubernetes:
kubectl exec secure-app -- capsh --print
# Current: =  <- empty capabilities
kubectl exec secure-app -- id
# uid=1000 gid=1000 groups=1000  <- non-root

# Step 7: Audit for privilege escalation paths:
# Check if any binary in the container has setcap:
kubectl exec secure-app -- \
    find / -type f -executable 2>/dev/null | \
    xargs getcap 2>/dev/null
# (should be empty)

# Check if any binary is setuid:
kubectl exec secure-app -- \
    find / -type f -perm /4000 2>/dev/null
# (should be empty in a minimal container)
```

---

### Mental Model / Analogy

```
Linux capabilities = hotel master key system

Traditional Unix (root = UID 0):
  Root = Hotel Manager with ONE master key that opens EVERYTHING:
    Guest rooms (user files), maintenance closets (device files),
    kitchen (system config), safe (passwords), server room (kernel ops)
    One key, all access
  
  Problem: give key to ANY trusted task -> they have ALL access
  Lost/stolen key -> everything compromised

Linux capabilities = specialized keycards:
  Each keycard opens only specific areas:
  
  CAP_NET_ADMIN = "Network operations" keycard:
    Opens: router closet (routing), network switch room (interfaces),
    packet monitoring station (raw sockets)
    Cannot open: guest room files, kitchen, server room
  
  CAP_DAC_OVERRIDE = "Files master" keycard:
    Opens: ANY guest room door regardless of "Do Not Disturb" sign
    (bypasses file permissions for any user's files)
    Very dangerous! Should rarely be issued.
  
  CAP_NET_BIND_SERVICE = "Front door" keycard:
    Only opens: the front door (ports < 1024)
    Cannot open: anything else
    Perfect for web server that needs port 80, nothing else

setcap = "programming a door's keycard requirement":
  setcap cap_net_raw+ep /usr/sbin/tcpdump
  = "Program the tcpdump door to accept cap_net_raw keycard"
  Now anyone with cap_net_raw keycard can use tcpdump

No-new-privileges = "revoked key vault access":
  Normal: staff can access the key vault (setuid binaries) to get new keys
  no-new-privileges: "this staff member cannot access the key vault"
  Even if they find a setuid-root binary: cannot use it to get more keys
  Most secure option for containers

CAP_SYS_ADMIN = "Passmaster keycard":
  This keycard somehow works on 30+ different doors (historically)
  Network namespaces, mounts, kernel operations, device ioctls...
  If attacker gets this card: they can likely escape the building!
  Never issue in containers.

Bounding set = "master list of keys that can exist":
  Even if someone tries to create a new key type not on the master list:
  The key system rejects it
  Docker default bounding: limits what caps are even possible
  If you remove cap_net_admin from bounding:
    No process in the container can EVER have CAP_NET_ADMIN,
    even if they exec a setcap binary
```

---

### Gradual Depth - Five Levels

**Level 1:**
Concept: splitting root privileges into units. `getcap`, `setcap` basics.
Common capabilities: `CAP_NET_BIND_SERVICE` (port < 1024),
`CAP_NET_RAW` (packet capture/ping). Docker `--cap-drop`/`--cap-add`.
Principle of least privilege applied to capabilities.

**Level 2:**
Four thread capability sets: permitted, effective, inheritable, bounding.
`capsh --print` to view current caps. `cat /proc/PID/status | grep Cap`.
`capsh --decode` to decode hex bitmask. `no-new-privileges` (`PR_SET_NO_NEW_PRIVS`).
Kubernetes `securityContext.capabilities`. Common dangerous capabilities
(CAP_SYS_ADMIN, CAP_DAC_OVERRIDE, CAP_SETUID).

**Level 3:**
Capability transitions on exec() (file capabilities: permitted + inheritable
flags). Ambient capabilities (kernel 4.3): `prctl(PR_CAP_AMBIENT_RAISE)`.
Bounding set manipulation and its effects. `setcap` flag notation: `+eip`/`+ep`.
Systemd `AmbientCapabilities=` and `CapabilityBoundingSet=`. Security analysis:
CAP_NET_ADMIN attack surface, CAP_SYS_ADMIN container escape paths.

**Level 4:**
`libcap` API: `cap_get_proc`, `cap_set_proc`, `cap_from_text`. `capng` library
for C. Capability-aware programming: drop all caps at startup, only raise needed.
Container runtime capability enforcement: Docker's libcontainer, containerd's
OCI runtime. seccomp + capabilities: combined defense. AppArmor/SELinux
integration with capabilities (MAC policies layered on top of DAC capabilities).
`pscap` (from libcap-ng) to list process capabilities in human-readable form.
Finding setcap binaries for security auditing.

**Level 5:**
Linux capability implementation in kernel: `struct task_struct.cred`,
`struct cred.cap_*`. `capable()` kernel function for checking capabilities.
`ns_capable()` for namespace-aware capability checks. User namespace
capabilities: a process can have capabilities WITHIN a user namespace
(unprivileged user can have CAP_NET_ADMIN in a network namespace they own,
but not on the host). Container escape via user namespace + capability exploit.
`CLONE_NEWUSER` and its interaction with capabilities. SELinux and capability
enforcement interaction (MAC wins over DAC, but capabilities modify DAC).
Capability locking: `PR_CAP_SETPCAP` for drop-only capability management.
gVisor, kata-containers: how VM-isolation sidesteps Linux capability entirely.

---

### Code Example

**BAD - running processes with excessive capabilities:**
```bash
# BAD 1: Running web server as root (all capabilities):
docker run --rm -p 80:80 nginx
# nginx running as root: has ALL capabilities
# If nginx is compromised: attacker has cap_sys_admin, cap_setuid...
# Container escape is possible via privilege escalation

# BAD 2: Using CAP_DAC_OVERRIDE "for convenience":
setcap cap_dac_override+ep /usr/local/bin/myapp
# Now myapp can read/write ANY file on the system
# If myapp is compromised: /etc/shadow readable (all password hashes!)
# /root/.ssh/: readable
# Any audit log: writable (delete evidence)
# This grants unrestricted file access - effectively root for files

# BAD 3: Adding SYS_ADMIN to container without thought:
docker run --rm --cap-add SYS_ADMIN ubuntu bash
# "I needed it for mounting a tmpfs inside the container"
# But SYS_ADMIN also grants: namespace switching, perf events,
# ptrace of other containers, and many container escape paths

# GOOD: Minimum privilege:
# Instead of SYS_ADMIN for tmpfs: use volume mounts
docker run --rm -v /dev/shm:/dev/shm nginx   # share host tmpfs
# Or: use tmpfs mount without SYS_ADMIN:
docker run --rm --tmpfs /tmp:rw,noexec,nosuid,size=100m nginx
# ^ creates tmpfs without CAP_SYS_ADMIN
```

**GOOD - capability-aware application:**
```c
// capability_drop.c: drop all capabilities except needed ones
#include <stdio.h>
#include <stdlib.h>
#include <sys/capability.h>
#include <sys/prctl.h>
#include <unistd.h>

// Drop all capabilities except those in the keep[] array
int drop_capabilities(cap_value_t *keep, int keep_count) {
    cap_t caps;
    
    // Get current capabilities:
    caps = cap_get_proc();
    if (!caps) return -1;
    
    // Clear ALL capabilities:
    cap_clear(caps);
    
    // Set only the needed capabilities in effective + permitted:
    if (keep_count > 0) {
        cap_set_flag(caps, CAP_EFFECTIVE, keep_count, keep, CAP_SET);
        cap_set_flag(caps, CAP_PERMITTED, keep_count, keep, CAP_SET);
    }
    
    // Apply:
    int ret = cap_set_proc(caps);
    cap_free(caps);
    
    if (ret != 0) return -1;
    
    // Set no-new-privileges: even setuid binaries won't gain caps:
    return prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0);
}

int main() {
    // After startup (reading config, binding ports, etc.):
    // Drop to minimum needed capabilities:
    
    // This app only needs CAP_NET_RAW for raw socket:
    cap_value_t needed[] = { CAP_NET_RAW };
    
    if (drop_capabilities(needed, 1) != 0) {
        perror("Failed to drop capabilities");
        return 1;
    }
    
    printf("Running with reduced capabilities\n");
    
    // Verify:
    cap_t caps = cap_get_proc();
    char *caps_text = cap_to_text(caps, NULL);
    printf("Current caps: %s\n", caps_text);
    // Output: "Current caps: = cap_net_raw+ep"
    cap_free(caps_text);
    cap_free(caps);
    
    // Main application logic here:
    // Any attempt to use other capabilities will fail with EPERM
    
    return 0;
}
// Compile: gcc -o app capability_drop.c -lcap
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "Running as non-root means no capabilities" | Running as a non-root user (UID != 0) means the process CANNOT gain capabilities via the old mechanism (setuid root binaries only grant caps if UID=0). BUT: (1) setcap binaries grant capabilities to ANY user who executes them (the binary has file capabilities). (2) Ambient capabilities (kernel 4.3+) can be inherited by non-root processes. (3) User namespaces: within a user namespace, a non-root user can have ALL capabilities for things within that namespace. A Docker container running as UID 1000 but with `--cap-add NET_ADMIN` has CAP_NET_ADMIN. UID and capabilities are separate mechanisms. Always check both `id` (user) AND `capsh --print` (capabilities) to understand a process's privilege level. |
| "CAP_NET_ADMIN is needed to open a raw socket" | `CAP_NET_RAW` is needed for raw sockets (e.g., `socket(AF_PACKET, SOCK_RAW, ...)` or `socket(AF_INET, SOCK_RAW, IPPROTO_ICMP)` for ping). `CAP_NET_ADMIN` is a DIFFERENT and much more powerful capability: it controls interface configuration, routing tables, iptables rules, and network namespace management. For `tcpdump`: it needs `CAP_NET_RAW` (for raw packet capture) and in some modes `CAP_NET_ADMIN` (for promiscuous mode). For `ping`: only `CAP_NET_RAW`. Many guides incorrectly recommend `CAP_NET_ADMIN` when `CAP_NET_RAW` is sufficient. Always use the most specific, least-powerful capability that satisfies the requirement. |
| "Docker --privileged only adds capabilities" | `docker run --privileged` does much more than just adding all capabilities: (1) Disables the seccomp filter (all syscalls allowed). (2) Disables AppArmor/SELinux confinement. (3) Grants all capabilities (ALL in caps notation). (4) Mounts all host devices in `/dev/` inside the container. (5) Enables mounting arbitrary host filesystems. The result: a privileged container is essentially a root shell on the host. A privileged container can trivially escape: `mount /dev/sda1 /mnt; chroot /mnt; chroot escape`. Never use `--privileged` in production without understanding the full scope of what you're enabling. Use specific `--cap-add` for individual capabilities needed. |
| "Removing a capability from a Docker container prevents it from being used" | `--cap-drop CAP_NET_ADMIN` removes the capability from the container's initial capability set. However: (1) If no-new-privileges is NOT set: a setuid-root binary inside the container exec'd by the process can re-gain capabilities. (2) User namespace capabilities: if the container runs a new user namespace, the root user within that namespace might gain capabilities for namespace-scoped operations. (3) Some kernel versions have capability check bypass vulnerabilities. Defense in depth: combine `--cap-drop ALL` + `--cap-add <needed>` + `--security-opt no-new-privileges` + non-root user (runAsUser: 1000) + seccomp profile. Each layer addresses a different attack surface. No single layer is complete. |

---

### Failure Modes & Diagnosis

**Capability-related failures and security audit:**
```bash
# === Failure: "Operation not permitted" after dropping capabilities ===
# App was working, then security team added cap-drop ALL, app breaks

# Step 1: Identify what capability is missing:
strace -e trace=prctl,socket,open ./myapp 2>&1 | \
    grep "EPERM\|EACCES\|Operation not permitted"
# Example: socket(AF_PACKET, SOCK_RAW, ...) = -1 EPERM
# -> CAP_NET_RAW needed

# Step 2: Check what capabilities the process currently has:
docker run --rm myapp capsh --print
# Current: =  <- empty (cap-drop ALL working)
# Bounding set = ...

# Step 3: Add back minimum needed:
docker run --cap-drop ALL --cap-add NET_RAW myapp
# If still failing: add another cap, repeat

# Step 4: Verify no unnecessary caps remain:
docker run --cap-drop ALL --cap-add NET_RAW myapp capsh --print
# Current: = cap_net_raw+ep  <- only NET_RAW

# === Security audit: find privilege escalation paths ===

# Find all setcap binaries (could grant caps to any user):
find / -not -path /proc -not -path /sys -type f \
    -executable 2>/dev/null | xargs getcap 2>/dev/null
# /usr/sbin/ping = cap_net_raw+ep
# /usr/bin/python3.9 = cap_sys_admin+ep  <- DANGEROUS!
# ^ Python with CAP_SYS_ADMIN: execute arbitrary kernel ops!

# Find all setuid binaries (potential privilege escalation):
find / -not -path /proc -not -path /sys \
    -perm /4000 -type f 2>/dev/null
# /usr/bin/sudo
# /usr/bin/su
# /usr/bin/passwd
# /opt/myapp/helper  <- unexpected setuid binary in app!

# Check if container has escaped CAP_SYS_ADMIN exposure:
docker inspect myapp 2>/dev/null | \
    jq '.[0].HostConfig.CapAdd // "none"'
# If includes "SYS_ADMIN": high security risk

# Audit Kubernetes pods for excessive privileges:
kubectl get pods -A -o json | \
    jq -r '
    .items[] |
    select(
        .spec.containers[].securityContext.capabilities.add != null and
        (.spec.containers[].securityContext.capabilities.add | 
         contains(["SYS_ADMIN", "NET_ADMIN", "DAC_OVERRIDE"]))
    ) |
    "\(.metadata.namespace)/\(.metadata.name): has dangerous caps"'

# Check pods running as root:
kubectl get pods -A -o json | \
    jq -r '
    .items[] |
    select(
        .spec.containers[].securityContext.runAsUser == 0 or
        .spec.securityContext.runAsUser == 0
    ) |
    "\(.metadata.namespace)/\(.metadata.name): running as root!"'

# === Failure: ambient capabilities not working ===
# Non-root service needs CAP_NET_RAW to run tcpdump
# systemd unit with AmbientCapabilities:

cat > /etc/systemd/system/capture.service << 'EOF'
[Unit]
Description=Packet Capture Service

[Service]
User=capture_user
Group=capture_group
AmbientCapabilities=CAP_NET_RAW CAP_NET_ADMIN
CapabilityBoundingSet=CAP_NET_RAW CAP_NET_ADMIN
ExecStart=/usr/sbin/tcpdump -i eth0 -w /var/log/capture.pcap

[Install]
WantedBy=multi-user.target
EOF

# If failing:
# Check kernel version (ambient caps require >= 4.3):
uname -r

# Check if tcpdump binary has file capabilities set:
getcap /usr/sbin/tcpdump
# If no file caps AND user is non-root:
# Need ambient capabilities OR setcap on binary
# Not both (setcap overrides ambient for that binary)
```

---

### Related Keywords

**Foundational:**
LNX-078 (Seccomp and capabilities intro), LNX-009 (File permissions)

**Builds on this:**
LNX-108 (Multi-tenant security architecture), LNX-100 (Linux hardening)

**Related:**
LNX-079 (LSM/AppArmor/SELinux), LNX-009 (Unix permissions)

---

### Quick Reference Card

| Command | Purpose |
|---------|---------|
| `setcap 'cap_net_raw+ep' /usr/bin/prog` | Add capabilities to binary |
| `getcap /usr/bin/prog` | View binary capabilities |
| `capsh --print` | View current process capabilities |
| `cat /proc/PID/status \| grep Cap` | Raw hex capability bitmask |
| `capsh --decode=<hex>` | Decode hex bitmask to readable names |
| `docker run --cap-drop ALL --cap-add X` | Drop all, add specific cap |
| `prctl(PR_SET_NO_NEW_PRIVS, 1, ...)` | Prevent gaining new capabilities |

**3 things to remember:**
1. `CAP_SYS_ADMIN` = "almost root" and enables container escape; avoid in containers; Docker now splits it into `CAP_PERFMON` + `CAP_BPF` for specific needs
2. Three-layer defense for containers: drop ALL caps + add back minimum + `no-new-privileges` + run as non-root (all four together)
3. `CAP_NET_RAW` is for raw sockets (tcpdump/ping); `CAP_NET_ADMIN` is for interface/routing/iptables management - they are different, don't conflate them

---

### Transferable Wisdom

Linux capabilities are the OS-level implementation of the principle of least
privilege - the same design principle behind: AWS IAM roles (specific permissions
vs AdminAccess), Kubernetes RBAC (specific verb/resource pairs vs cluster-admin),
database privilege grants (SELECT on specific table vs superuser). The ambient
capability mechanism (inheritance across exec by non-root) mirrors: AWS role
chaining (pass role to child process), Kubernetes projected service account
tokens (pod gets specific permission for its lifetime). The no-new-privileges
flag maps to AWS SCP (Service Control Policies) - a guardrail that cannot
be bypassed by the workload itself, set by the platform. The bounding set
(absolute maximum) maps to: AWS permission boundaries, Kubernetes PodSecurityPolicy
allowedCapabilities. The pattern "drop ALL then add back minimum" is the same
as: IAM deny-then-allow, firewall whitelist (default deny, explicit allow).
Security auditing for setcap binaries (find / -executable | xargs getcap)
is equivalent to: AWS IAM Access Analyzer (find IAM roles with overly broad
permissions), Kubernetes audit for cluster-admin bindings. Container capabilities
are now assessed by Kubernetes Pod Security Standards (restricted/baseline/
privileged profiles), where "restricted" maps to drop ALL caps + non-root +
no-new-privileges.

---

### The Surprising Truth

`CAP_SYS_ADMIN` is documented with a note in the Linux man page that is
rare for kernel documentation: "This capability is overloaded; see Notes to
kernel developers, below." The "Notes" explain that CAP_SYS_ADMIN was created
as a catch-all for operations that didn't fit other categories, and now covers
30+ distinct privileged operations - from mounting filesystems to setting
host names to loading kernel modules (in some contexts). The kernel developers
themselves acknowledge it should never have been designed this way and have
been splitting it into more specific capabilities (CAP_PERFMON, CAP_BPF,
CAP_CHECKPOINT_RESTORE in kernels 5.8-5.9). However: legacy applications
that check for CAP_SYS_ADMIN cannot be changed without breaking compatibility.
The second surprise: Docker's default capability set (14 capabilities retained
from the original set of ~30) was designed in 2013 and includes `CAP_NET_RAW`
by default. This means every Docker container, by default, can put the NIC in
promiscuous mode and capture traffic from all other containers on the same
host (if they share a bridge network). Most organizations don't know this.
The fix: `--cap-drop NET_RAW` (unless you need tcpdump inside the container).
Kubernetes addressed this with PodSecurityStandards in 1.25, where the
"restricted" profile drops ALL capabilities - but adoption requires explicit
opt-in per namespace.

---

### Mastery Checklist

- [ ] Can use setcap/getcap to assign and inspect binary capabilities
- [ ] Knows the five thread capability sets (permitted, effective, inheritable, ambient, bounding)
- [ ] Understands the security risk of CAP_SYS_ADMIN and CAP_DAC_OVERRIDE in containers
- [ ] Can configure Docker and Kubernetes to run containers with minimum capabilities
- [ ] Knows what no-new-privileges does and why it's important for container security

---

### Think About This

1. Design the capability set for three different microservices in a Kubernetes
   cluster: (a) a Prometheus node_exporter that reads system metrics via /proc
   and /sys, (b) a network diagnostic tool that captures packets on any
   interface, (c) a log aggregator that reads files from /var/log as root and
   forwards them. For each: determine the minimum capabilities needed (if any),
   specify the Kubernetes securityContext YAML, and identify what risks remain
   even with the reduced capability set.

2. Explain the complete privilege escalation path if a containerized service
   has `CAP_SYS_ADMIN`. Assume: container is running as UID 1000 (non-root),
   the only capability is CAP_SYS_ADMIN, no other capabilities. Describe at
   least two distinct container escape techniques using ONLY CAP_SYS_ADMIN
   and no other capabilities. What does this tell you about why CAP_SYS_ADMIN
   should be treated as equivalent to full host root access?

3. A service needs to ping external hosts (ICMP echo requests require raw
   sockets) and bind to port 443 for HTTPS. Currently it runs as root. Provide
   the complete re-design: (a) which specific capabilities are needed and why,
   (b) setcap command for the binary, (c) Docker run command with all security
   flags, (d) Kubernetes pod spec securityContext, (e) what residual risks
   remain even with capabilities properly scoped, and (f) how seccomp profiles
   complement capabilities for defense-in-depth.

---

### Interview Deep-Dive

**Foundational:**
Q: What are Linux capabilities and why are they important for container security?
A: Linux capabilities divide the root (UID 0) privilege into approximately 40 fine-grained units. Traditionally: root = binary superpower (all or nothing). Capabilities = modular powers that can be independently granted or removed. EXAMPLE: A web server that needs to bind to port 80 (traditionally root-only) can be granted just `CAP_NET_BIND_SERVICE` - it can bind to privileged ports but CANNOT read other users' files, change passwords, load kernel modules, or perform any other root operation. CONTAINER RELEVANCE: Containers often run as root internally (UID 0 in the container namespace) but can still have capabilities restricted. Docker's default capability set: retains 14 capabilities considered essential (cap_chown, cap_dac_override, cap_net_raw, etc.) and drops the rest. This provides partial isolation: the container root cannot load kernel modules or mount arbitrary filesystems, but CAN bypass file permissions (cap_dac_override) and create raw sockets (cap_net_raw). HARDENING: For production: `--cap-drop ALL --cap-add <specifically_needed>`. Most microservices need zero capabilities (they don't bind to privileged ports, don't capture packets, don't change file permissions). Kubernetes Pod Security Standards (restricted profile): drops all capabilities, requires runAsNonRoot, requires no-new-privileges. This is the current security baseline. DANGEROUS CAPABILITIES: CAP_SYS_ADMIN covers 30+ operations including mount and namespace manipulation - sufficient for container escape. CAP_DAC_OVERRIDE allows reading /etc/shadow. CAP_SETUID allows becoming any user. CAP_NET_ADMIN allows iptables manipulation and traffic capture. These four should NEVER appear in container capability sets unless absolutely required.

**Expert:**
Q: Explain Linux capability inheritance across exec() and how ambient capabilities (kernel 4.3+) changed this model.
A: ORIGINAL MODEL (pre-ambient): Capability inheritance across exec() is governed by three sets and file capability flags. At exec(): new_Permitted = (old_Inheritable AND file_Inheritable) OR (file_Permitted AND bounding). new_Effective = file_effective_bit ? new_Permitted : empty. new_Inheritable = old_Inheritable. FILE CAPABILITIES: Set with `setcap cap_net_raw+ep /usr/sbin/tcpdump` - this sets file_Permitted and file_effective. When ANY user executes tcpdump: new_Permitted includes cap_net_raw (from file_Permitted), new_Effective = new_Permitted (file_effective=true). Result: any user running tcpdump gets CAP_NET_RAW effective. Problem 1: INHERITANCE FOR NON-ROOT. If a non-root parent process has cap_net_raw in its permitted set and wants to pass it to a child via exec: the child only inherits through the Inheritable set, but the child's new_Permitted requires file_Inheritable to be set on the binary. If the binary doesn't have file_I set: capability not inherited. Old model: capabilities pass through exec only if the binary is explicitly configured. Problem 2: SYSTEMD SERVICES. A non-root service wants to exec a subprocess that needs cap_net_raw. Setting AmbientCapabilities in the systemd unit requires the child binary to have no file capabilities for the ambient to work. AMBIENT CAPABILITIES (kernel 4.3+): Added a 5th set - ambient. Constraints: a capability can only be in ambient if it's in BOTH permitted AND inheritable. At exec with ambient capabilities: new_Permitted includes ambient caps. new_Effective includes ambient caps. Child process is non-root but has the ambient caps effective! PRACTICAL USE: systemd unit: `AmbientCapabilities=CAP_NET_RAW`. Process running as non-root uid 1000: exec of a helper binary that needs cap_net_raw. Without ambient: helper gets no caps (non-root, file has no setcap). With ambient: helper automatically gets cap_net_raw in effective. SECURITY IMPLICATIONS: Ambient capabilities mean a non-privileged user's exec chain can carry capabilities. This is intentional: systemd-managed services can be properly delegated caps without setuid. But it requires careful auditing: if a service with ambient caps is compromised and execs a shell, the shell has the ambient caps.
