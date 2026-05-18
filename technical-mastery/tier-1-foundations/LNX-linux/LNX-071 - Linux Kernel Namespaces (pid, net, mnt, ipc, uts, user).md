---
id: LNX-071
title: "Linux Kernel Namespaces (pid, net, mnt, ipc, uts, user)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★★
depends_on: LNX-004, LNX-022
used_by: LNX-072, LNX-080, LNX-092
related: LNX-072, LNX-080, LNX-092
tags: [namespaces, pid-namespace, net-namespace, mount-namespace, user-namespace, containers, isolation, unshare, nsenter, clone]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 71
permalink: /technical-mastery/lnx/linux-kernel-namespaces/
---

## TL;DR

Linux namespaces are the kernel mechanism that creates **isolated views**
of system resources. Each namespace type wraps one resource domain. The
6+1 types: `pid` (process IDs), `net` (network stack), `mnt` (filesystem
mounts), `ipc` (System V IPC, POSIX mqueues), `uts` (hostname/domainname),
`user` (UID/GID mapping), `cgroup` (cgroup root view). Containers = processes
in multiple namespaces simultaneously. Tools: `unshare` (create new namespaces),
`nsenter` (join existing), `lsns` (list), `/proc/[pid]/ns/` (namespace FDs).
Namespaces provide **isolation**; cgroups provide **resource limits** - together
they make containers.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-071 |
| **Difficulty** | ★★★ Advanced |
| **Category** | Linux |
| **Tags** | namespaces, pid-namespace, net-namespace, containers, isolation, unshare, nsenter |
| **Prerequisites** | LNX-004 (Shell), LNX-022 (Process management) |

---

### The Problem This Solves

**Problem 1**: Two web servers on the same host both want to listen on port
80 with the same process hierarchy. Without namespaces: impossible - port
80 can only be bound once, and PIDs are global. With network namespaces:
each server gets its own virtual network stack with its own port 80. With
PID namespaces: each server sees its own process with PID 1. This is the
exact mechanism Docker uses to run multiple containers on one host.

**Problem 2**: A developer runs an untrusted application and wants to prevent
it from seeing other processes, accessing the network, or reading host files.
User namespaces allow running a process as "root" inside a namespace (full
UID 0 capabilities) while mapping that root to an unprivileged user on the
host. The process thinks it has root; the host sees it as UID 65534 with
no special privileges.

---

### Textbook Definition

**Linux namespaces**: Kernel feature (kernel 3.8+ for user namespaces,
earlier for others) that partitions kernel resources. Each process belongs
to exactly one namespace of each type. By default, all processes share the
initial namespaces. A new namespace is created with `clone(CLONE_NEW*)` or
`unshare(CLONE_NEW*)` syscalls. Child processes inherit parent's namespaces.

**Namespace types:**

| Type | Flag | Isolates | Kernel version |
|------|------|---------|---------------|
| Mount | `CLONE_NEWNS` | Filesystem mount points | 2.4.19 |
| UTS | `CLONE_NEWUTS` | Hostname, domainname | 2.6.19 |
| IPC | `CLONE_NEWIPC` | SysV IPC, POSIX MQs | 2.6.19 |
| PID | `CLONE_NEWPID` | Process IDs | 2.6.24 |
| Network | `CLONE_NEWNET` | Network devices, routing | 2.6.29 |
| User | `CLONE_NEWUSER` | User/group IDs | 3.8 |
| Cgroup | `CLONE_NEWCGROUP` | Cgroup root | 4.6 |

---

### Understand It in 30 Seconds

```bash
# === List all namespaces on the system ===
lsns
# TYPE   NPROCS   PID USER   COMMAND
# net         2   123 root   /sbin/init
# net         1  4321 user   /usr/sbin/nginx   <- different net namespace!

# === Inspect process namespaces ===
ls -la /proc/self/ns/
# lrwxrwxrwx cgroup -> cgroup:[4026531835]
# lrwxrwxrwx ipc    -> ipc:[4026531839]
# lrwxrwxrwx mnt    -> mnt:[4026531840]
# lrwxrwxrwx net    -> net:[4026531992]
# lrwxrwxrwx pid    -> pid:[4026531836]
# lrwxrwxrwx user   -> user:[4026531837]
# lrwxrwxrwx uts    -> uts:[4026531838]
# The inode number in brackets = namespace ID
# Two processes with same inode = same namespace

# === unshare: create process in new namespace(s) ===
# Run shell in new UTS namespace (isolated hostname):
unshare --uts bash
  hostname                    # shows host's hostname
  hostname mycontainer        # change hostname
  hostname                    # mycontainer
  exit                        # back to host
hostname                      # host hostname unchanged!

# Run shell in new PID namespace:
unshare --pid --fork --mount-proc bash
  ps aux        # Only shows processes IN THIS namespace!
  # PID 1 = bash (this process is PID 1 in the new namespace)
  exit

# Create isolated network namespace:
ip netns add testns
ip netns exec testns bash
  ip addr       # only shows loopback (isolated!)
  ip link       # no host interfaces
  exit
ip netns del testns

# === nsenter: join an existing process's namespace ===
# Get Docker container's PID:
docker inspect --format '{{.State.Pid}}' mycontainer  # e.g., 12345

# Enter the container's network namespace from the host:
nsenter --target 12345 --net -- ip addr
# Shows the container's network interfaces from the HOST!
# Useful for debugging: container sees same network view

# Enter ALL namespaces of a container (equivalent to exec):
nsenter --target 12345 --all -- bash

# === How Docker uses namespaces ===
# docker run creates a process with:
# clone(CLONE_NEWPID|CLONE_NEWNET|CLONE_NEWNS|CLONE_NEWIPC|CLONE_NEWUTS|...)
# Inside container: sees pid=1, own network, own mounts
# On host: sees container's actual PID (e.g., 12345), host network

# Verify two processes in different PID namespaces:
cat /proc/12345/status | grep NSpid
# NSpid:    12345    1
# First number: PID in host namespace
# Second number: PID in container's PID namespace (= 1 for container init)
```

---

### First Principles

**How namespaces work under the hood:**
```
Namespace = a kernel data structure representing an isolated resource view

Every process has a pointer to a namespace object for each type:
struct task_struct {
    struct nsproxy *nsproxy;  // pointer to namespace set
}

struct nsproxy {
    struct uts_namespace  *uts_ns;
    struct ipc_namespace  *ipc_ns;
    struct mnt_namespace  *mnt_ns;
    struct pid_namespace  *pid_ns;
    struct net            *net_ns;
    struct cgroup_namespace *cgroup_ns;
}

When process A and B share the same UTS namespace:
  A: task.nsproxy.uts_ns -> namespace_42 (hostname="web01")
  B: task.nsproxy.uts_ns -> namespace_42 (same object, same hostname)
  B: sethostname("web01-new") -> changes namespace_42's hostname
  A: gethostname() -> "web01-new" (sees the change!)

When process C is in a DIFFERENT UTS namespace:
  C: task.nsproxy.uts_ns -> namespace_99 (hostname="container1")
  A: sethostname("changed") -> changes namespace_42, NOT namespace_99
  C: gethostname() -> "container1" (isolated!)

PID namespace translation:
  Host PID namespace contains PID 12345 (container process)
  Container PID namespace: that same process has PID 1
  
  /proc/12345/status shows: "NSpid: 12345 1"
  Multiple PIDs listed: one per namespace level
  (nested namespaces have more levels)
```

**User namespace UID mapping:**
```
Problem: running "root" in a container on a shared host is dangerous
  - Container root = UID 0 = has host root privileges if namespace escapes

User namespaces solve this with UID mapping:
  /proc/[pid]/uid_map: "inside_uid count outside_uid"
  Example: "0 1000 1"
  Means: UID 0 inside namespace = UID 1000 on host, for 1 ID

  Inside container: process runs as UID 0 (root!)
  On host: that process is UID 1000 (unprivileged user)

  Container root cannot: access host files owned by root (UID 0)
  Container root CAN: modify files mapped to UID 1000

Read UID map for a process:
  cat /proc/12345/uid_map
  # 0     100000  65536
  # Container UIDs 0-65535 map to host UIDs 100000-165535
  # Container root (0) = host UID 100000 (unprivileged)

This is "rootless containers" - Docker --user, Podman rootless, runc rootless
```

---

### Thought Experiment

Building a minimal container with just shell commands:

```bash
#!/bin/bash
# Demonstrate: a "container" is just namespaces + cgroups

# Step 1: Create new namespaces (requires root for net/pid namespaces):
# (user namespaces don't require root)
sudo unshare \
    --pid \
    --fork \
    --mount-proc \
    --net \
    --uts \
    --ipc \
    --mount \
    bash << 'CONTAINER'

echo "=== Inside the namespace ==="
echo "Hostname: $(hostname)"
hostname mycontainer   # change hostname (isolated!)
echo "New hostname: $(hostname)"

echo "--- Processes (PID namespace isolated) ---"
ps aux | head -5
# Should only show bash as PID 1 and ps itself

echo "--- Network (network namespace isolated) ---"
ip addr
# Only loopback! No host network interfaces

echo "--- Mounts ---"
# /proc/self/mounts shows mounts in this mount namespace
grep -c . /proc/self/mounts   # count

CONTAINER

echo "=== Back on host ==="
echo "Hostname: $(hostname)"   # unchanged
echo "All processes still visible"
ps aux | wc -l

# Step 2: Compare namespace IDs:
# Our shell: cat /proc/self/ns/uts
# Container process would have a different uts: ID
```

---

### Mental Model / Analogy

```
Namespaces = hotel floors on a skyscraper

Skyscraper = Linux host (one physical machine)
Each floor = one namespace (isolated view of resources)

PID namespace = floor's own room numbering:
  Floor A: rooms 101, 102, 103...
  Floor B: rooms 101, 102, 103... (same numbers, different rooms)
  From the lobby (host): room A101, room B101 (unique addresses)
  Guests on floor A: only see their floor's rooms

Network namespace = floor's own phone system:
  Floor A has phone extension 100 (port 80 in networking terms)
  Floor B also has phone extension 100
  No conflict: different phone systems
  Switchboard (veth pairs, bridges): routes calls between floors

Mount namespace = floor's own map of the building:
  Floor A's map shows: its own storage room + shared lobby
  Floor B's map shows: completely different rooms
  Underlying building (hardware): unchanged
  Each floor thinks it has exclusive access to storage

UTS namespace = floor's nameplate:
  Floor A: nameplate says "webserver-prod"
  Floor B: nameplate says "database-staging"
  Building's real name: server42.datacenter.example.com (unchanged)

User namespace = floor's own key system:
  The "master key" on floor A (UID 0) opens floor A's doors
  That same key on the building level: just a regular tenant key
  Prevents a floor's "master key" from opening building-level doors

nsenter = riding the elevator to another floor:
  nsenter --target 12345 --net
  = get on the elevator, go to process 12345's floor,
    look around their phone system (network namespace)
  You still have your own identity (UID) from your floor
  But you see their network view
```

---

### Gradual Depth - Five Levels

**Level 1:**
What namespaces are: isolated views of kernel resources. The 7 types and
what each isolates. `lsns` to list namespaces. `/proc/[pid]/ns/` to inspect.
`unshare --uts bash` to test UTS isolation. Containers use namespaces.

**Level 2:**
`clone()` and `unshare()` syscalls. `nsenter` for debugging containers.
Network namespace workflow: `ip netns add/exec`. `--pid --fork --mount-proc`
for proper PID namespace. Inheritance: child inherits parent namespaces.
How Docker maps namespaces with `docker inspect`.

**Level 3:**
User namespace UID mapping (`/proc/[pid]/uid_map`). Rootless containers
(Podman, Docker rootless). PID namespace and `/proc` re-mounting. Nested
namespaces (namespaces within namespaces). Namespace persistence via bind
mounts (`/var/run/netns/`). `ip netns` for named network namespaces.

**Level 4:**
Namespace creation in C with `clone()`. Capabilities within user namespaces.
`setns()` syscall (used by `nsenter`). Cgroup namespace isolation (container
sees `/` as cgroup root). Mount namespace and pivot_root vs chroot for
container root filesystem setup. Time namespace (Linux 5.6, per-container
clock offsets). Namespace-aware tools: `ip netns exec`, `unshare`, `nsenter`.

**Level 5:**
Namespace escape vulnerabilities (CVE patterns): privileged process writing
to `/proc/sysrq-trigger`, runc CVE-2019-5736 (overwrite host runc binary
through `/proc/self/exe`). Namespace vs hypervisor isolation (why VMs are
more isolated than containers). Kernel namespaces in security reviews: which
namespaces are created, are user namespaces enabled (`/proc/sys/user/
max_user_namespaces`). Namespace resource limits (`/proc/sys/user/
max_*_namespaces`). `seccomp` and capabilities as defense in depth for
namespace-based isolation.

---

### Code Example

**BAD - namespace mistakes in container tooling:**
```bash
# BAD 1: Running privileged container without namespace isolation:
docker run --privileged myapp
# --privileged: ALL capabilities, host namespaces visible
# Container process can see all host PIDs, mount host FS, etc.
# Use only when genuinely needed (specific devices, kernel modules)

# BAD 2: Using PID namespace without re-mounting /proc:
unshare --pid bash
ps aux   # Shows ALL processes from host's /proc
         # Isolated PID namespace but /proc still shows host!
         # --mount-proc is needed to get proper isolation

# BAD 3: Checking namespace without understanding NSpid:
# "This container process is using PID 1234"
docker exec mycontainer ps aux | grep myapp
# Shows PID 1 (inside container)
# Operator on host tries to kill -9 1 -> kills INIT! (host PID 1)
# Should use docker inspect + NSpid to find HOST PID
```

**GOOD - correct namespace usage:**
```bash
# GOOD 1: Debug container networking from host (read-only):
CONTAINER_PID=$(docker inspect -f '{{.State.Pid}}' mycontainer)
# Enter only network namespace (non-destructive):
nsenter --target "$CONTAINER_PID" --net -- \
    ss -tuln   # show listening ports from container's perspective
nsenter --target "$CONTAINER_PID" --net -- \
    ip route   # container's routing table

# GOOD 2: Proper PID namespace with /proc:
unshare --pid --fork --mount-proc -- bash
ps aux   # Only shows processes in this PID namespace
         # bash is PID 1, ps is PID 2

# GOOD 3: Safe user namespace experiment (no root needed):
unshare --user --map-root-user bash
id       # uid=0(root) inside namespace
whoami   # root (inside namespace)
cat /proc/self/uid_map
# 0  1000  1   <- host UID 1000 = namespace UID 0
touch /tmp/test-$(id -u)   # can write to /tmp (mapped correctly)
mount --bind /tmp /mnt     # FAILS: still constrained by real capabilities

# GOOD 4: Inspect namespace memberships:
# Check if two processes share network namespace:
ls -la /proc/1234/ns/net /proc/5678/ns/net
# If same inode -> same network namespace
# If different inodes -> different network namespaces
```

---

### Comparison Table

| Namespace | Isolates | Created by | Common use |
|-----------|---------|-----------|-----------|
| pid | Process IDs | Container runtime | Container process tree |
| net | Network stack, interfaces, ports | `ip netns`, runc | Container networking |
| mnt | Mount points, filesystem | runc, unshare | Container root FS |
| uts | hostname, domainname | Container runtime | Per-container hostname |
| ipc | SysV SHM, semaphores, POSIX MQ | Container runtime | IPC isolation |
| user | UID/GID | Rootless containers, unshare | Privilege reduction |
| cgroup | Cgroup root view | Container runtime | Hide host cgroup tree |

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "Containers are fully isolated from the host kernel" | Namespaces isolate the VIEW of resources, not the kernel itself. Containers share the host kernel. A kernel exploit exploitable from userspace works from inside a container. This is the fundamental security difference between containers (namespace isolation) and VMs (hypervisor + separate kernel). Container isolation is about resource separation and process isolation, not kernel isolation. Defense in depth: seccomp, AppArmor/SELinux, user namespaces, and dropping capabilities are all necessary additions to namespace isolation. |
| "If container root can't see host processes, it can't affect them" | With default Docker settings, a process running as root inside a container can affect the host in multiple ways: (1) If a volume is mounted, root can write host files (as root = host root in non-rootless mode). (2) `--network=host` removes network isolation. (3) Privileged container can create raw network sockets, load kernel modules. (4) Host `/proc` can be accessible via `/proc/1/root` tricks in some configs. The namespace limits what you CAN SEE, not necessarily what you can AFFECT if you find a path. |
| "Network namespaces are created automatically for each process" | By default, ALL processes share the INITIAL network namespace. A new network namespace is only created explicitly: by a container runtime (runc calls `clone(CLONE_NEWNET)`), by `ip netns add` (creates a named namespace), by `unshare --net`. Two processes on the same host NOT in containers share one network namespace and one network stack. The concept of "each process has its own network namespace" is wrong; the default is shared, and isolation is opt-in. |
| "`nsenter --target PID --net` changes my shell's network permanently" | `nsenter` affects only the process spawned by the command (and its children). Your current shell is unaffected. When the `nsenter` command finishes, you're back to your original namespaces. This is the same as `unshare`: the current process's namespaces are not changed. The `unshare` command calls `unshare(2)` syscall to CHANGE the calling process's namespaces, but `nsenter` forks a new process that joins the target's namespaces. Your shell: still in original namespaces throughout. |

---

### Failure Modes & Diagnosis

**Namespace diagnostics:**
```bash
# Symptom: Container can see host processes
ps aux    # Shows many more processes than expected

# Diagnosis: PID namespace not created or /proc not remounted:
cat /proc/self/status | grep NSpid
# NSpid:  12345    <- only one PID! Process is in host PID namespace
# Should be: NSpid:  12345  1  (host PID, container PID)

ls -la /proc/self/ns/pid   # check PID namespace inode
ls -la /proc/1/ns/pid      # compare to init's PID namespace
# If same inode: process is in host PID namespace (not isolated)

# Symptom: Network namespace not working
ip addr    # shows all host interfaces, not just container ones
ls -la /proc/self/ns/net
ls -la /proc/1/ns/net
# If same: process is in host network namespace

# Symptom: "Operation not permitted" when creating namespaces
unshare --net bash   # Error: Operation not permitted
# Check: does your kernel allow user namespaces?
cat /proc/sys/user/max_user_namespaces   # 0 = disabled
sysctl user.max_user_namespaces          # check
# Fix (if appropriate): 
# sysctl -w user.max_user_namespaces=15000
# Or for net namespaces: requires CAP_SYS_ADMIN (usually root)

# Check capabilities:
capsh --print | grep -E "cap_|Bounding"
# cat /proc/self/status | grep Cap
# Use 'capsh --decode=<hex>' to decode capability bitmask
```

---

### Related Keywords

**Foundational:**
LNX-022 (Process management), LNX-004 (Shell basics)

**Builds on this:**
LNX-072 (cgroups), LNX-080 (Container internals), LNX-092 (Network namespaces and veth)

**Related:**
LNX-078 (Seccomp and capabilities), LNX-079 (LSM/SELinux/AppArmor)

---

### Quick Reference Card

| Command | Purpose |
|---------|---------|
| `lsns` | List all namespaces on system |
| `ls /proc/self/ns/` | List current process's namespaces |
| `unshare --uts bash` | New shell in new UTS namespace |
| `unshare --pid --fork --mount-proc bash` | New shell in new PID namespace |
| `nsenter --target PID --net -- cmd` | Run cmd in process's net namespace |
| `ip netns add NAME` | Create named network namespace |
| `ip netns exec NAME cmd` | Run cmd in named network namespace |
| `cat /proc/PID/status \| grep NSpid` | PID in each namespace level |

**3 things to remember:**
1. 7 namespace types: pid, net, mnt, ipc, uts, user, cgroup - each isolates a different resource domain
2. Namespaces = isolation (what you see); cgroups = limits (how much you can use)
3. `nsenter` to debug containers from the host without exec (enter just the net namespace to run diagnostic tools)

---

### Transferable Wisdom

Namespace concepts transfer directly to: Docker/Podman internals (what
`docker run` does at the kernel level). Kubernetes Pod isolation (each Pod
gets its own network namespace; containers in a Pod SHARE the net namespace,
which is why they can communicate via localhost). Security audits: ask "which
namespaces is this container in?" - missing user namespace = container root
is host root. Network namespaces are also used by: VPN tunnels (create net
namespace, route traffic through it), network testing (test routing without
actual hardware), service meshes (Istio injects a proxy in the same network
namespace as the app Pod). The `unshare` pattern (create isolated env for
testing) is useful for: testing firewall rules, simulating network partitions,
testing how a service behaves as PID 1 (signal handling). Understanding
namespaces makes `nsenter` a powerful debugger: you can enter just the
network namespace of a crashed container and run diagnostics without needing
a shell inside the container image.

---

### The Surprising Truth

The Linux mount namespace (CLONE_NEWNS) was the FIRST namespace type, added
in kernel 2.4.19 in 2002. The flag is literally `CLONE_NEWNS` (New Namespace,
not "New Mount Namespace") because at the time, developers didn't anticipate
that namespaces would become a general mechanism - they thought they were
adding a one-off feature for per-process mount tables. The other 6 types
were added years later (PID namespaces in 2.6.24 in 2008, user namespaces
in 3.8 in 2013). By the time namespaces became the foundation of containers,
the naming inconsistency was permanent - `CLONE_NEWNS` for mounts, but
`CLONE_NEWPID`, `CLONE_NEWNET` etc. for the rest. This is a textbook case
of a feature that was designed for one narrow purpose (per-process mounts
for Bind) and then repurposed as a general isolation primitive - containers
were not explicitly designed into the kernel, they emerged from composing
these primitives.

---

### Mastery Checklist

- [ ] Can explain what each of the 7 namespace types isolates
- [ ] Can use `lsns` and `/proc/[pid]/ns/` to inspect namespace membership
- [ ] Can use `unshare` to create isolated shell environments for testing
- [ ] Can use `nsenter` to debug container networking from the host
- [ ] Understands the difference between namespace isolation and full VM isolation

---

### Think About This

1. Docker containers in the same Pod in Kubernetes share the network namespace
   but have separate mount and PID namespaces. Explain what this means in
   practice: can two containers in a Pod listen on the same port? Can container
   A `kill` a process in container B by PID? Can container A see container B's
   filesystem? Trace each question through the specific namespace type involved.

2. A security team reports that an attacker who gained code execution inside
   a container was able to read `/etc/shadow` from the host. The container
   was running without `--privileged`. What namespace configuration mistake
   could have allowed this? (Hint: consider what user namespace configuration
   means for file ownership.)

3. Design a debugging approach for a production container that is experiencing
   network connectivity issues but has a minimal image (no shell, no tools
   like `netstat` or `ip`). Using only host-level tools and `nsenter`, how
   would you: (a) list what ports the container is listening on, (b) trace
   the routing table, (c) capture packets? Write the exact commands.

---

### Interview Deep-Dive

**Foundational:**
Q: What are Linux namespaces, and what problem do they solve for containers?
A: Linux namespaces are a kernel feature that provides isolated views of specific system resources. Without namespaces, all processes on a Linux host share global resource names: process IDs (PIDs), network interfaces, filesystem mounts, and hostnames are all system-wide. This makes running multiple isolated applications impossible: two services can't both have PID 1, port 80, or hostname "web". Namespaces solve this by creating separate instances of each resource type. Each namespace wraps one resource domain: pid (process IDs), net (network stack: interfaces, routing, ports), mnt (filesystem mount points), uts (hostname, domainname), ipc (System V IPC objects, POSIX message queues), user (UID/GID mappings), cgroup (cgroup hierarchy view). A process belongs to one namespace of each type simultaneously. For containers: the container runtime (runc, containerd) creates new namespaces using the `clone(CLONE_NEWPID|CLONE_NEWNET|...)` syscall, then starts the container's init process inside those new namespaces. Inside the container: PID 1 is the application, it has its own hostname, its own network stack with port 80 free, its own filesystem view. From the host: the container process has a different PID (e.g., 12345), it's visible in the host's process tree, but its resource names are in its own namespaces. KEY LIMITATION: namespaces share the host kernel. A kernel vulnerability exploitable from userspace can be exploited from inside a container. Namespaces provide process/resource isolation, NOT kernel isolation (that requires VMs).

**Expert:**
Q: Explain how user namespaces enable rootless containers and what security properties they provide.
A: User namespaces (CLONE_NEWUSER, kernel 3.8+) allow mapping of UIDs and GIDs between a namespace and the host. The key property: a process can be UID 0 (root) inside a user namespace while being mapped to an unprivileged UID on the host. How it works: when creating a user namespace, you write to `/proc/[pid]/uid_map`: `0 1000 1` means "UID 0 inside this namespace = host UID 1000." The process inside the namespace: sees itself as root, can perform privileged operations within the namespace (mount filesystems in its mount namespace, manipulate UID 0 files within the namespace). The host kernel: enforces that this "root" is actually UID 1000 for all host-level permission checks. Security properties: (1) PRIVILEGE REDUCTION: container root is not host root. If a container process writes to a file as root (namespace UID 0), the file gets host UID 1000 ownership. If a vulnerability allows reading host UID 0 files: the mapped UID 1000 can't read root's files. (2) CAPABILITY SCOPING: within a user namespace, the process gets a full capability set (CAP_SYS_ADMIN, etc.) but only for resources within that namespace. It can mount filesystems within its mount namespace, manipulate network within its net namespace - operations scoped to namespace, not host. (3) NO ROOT DAEMON NEEDED: rootless containers (Podman default, Docker --rootless) create the container entirely within user namespaces, needing no root-owned daemon. The entire container runs as a regular user. LIMITATIONS: some kernel operations require capabilities in the INITIAL namespace (not just a user namespace): loading kernel modules, creating raw sockets, using some device types. Rootless containers can't do these. SECURITY CAVEAT: user namespaces have historically had vulnerabilities (privilege escalation via namespace-local capabilities). Many distributions disable unprivileged user namespace creation by default (`sysctl -w user.max_user_namespaces=0`). Docker rootless and Podman rootless explicitly require user namespaces and appropriate sysctl settings.
