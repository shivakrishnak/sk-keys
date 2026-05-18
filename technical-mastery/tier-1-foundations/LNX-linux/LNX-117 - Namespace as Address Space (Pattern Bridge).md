---
id: LNX-117
title: "Namespace as Address Space (Pattern Bridge)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★★
depends_on: LNX-055, LNX-056, LNX-111
used_by: LNX-118, LNX-119
related: LNX-055, LNX-056, LNX-111, LNX-118, LNX-121
tags: [namespace-pattern, address-space, virtual-memory, pid-namespace, network-namespace, mount-namespace, ipc-namespace, uts-namespace, user-namespace, cgroup-namespace, virtualization-indirection, vma, page-table, virtual-routing, vlan, vrf, multi-tenancy, isolation-via-indirection, private-view-shared-resource, virtual-filesystem, unshare, clone-flags, nsenter, container-internals, pattern-recognition, abstraction-pattern, meta-insight]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 117
permalink: /technical-mastery/lnx/namespace-as-address-space-pattern-bridge/
---

## TL;DR

**Meta-insight**: Linux namespaces are a generalization of the virtual address
space concept. Both provide a **private view of a shared resource** via
**indirection**. Virtual memory: each process has a private view of memory
(VMA table maps virtual addresses to physical pages - the process doesn't see
other processes' memory). Linux namespaces extend this to ALL OS resources:
**PID namespace** = private view of process IDs (container PID 1 maps to host
PID 12345), **network namespace** = private view of network stack (container
eth0 maps to host veth pair), **mount namespace** = private view of filesystem
tree (container /proc maps to namespace-specific /proc). **All share the same
universal pattern**: a private lookup table (mapping virtual -> physical resource)
that the kernel maintains and translates transparently. This pattern also appears
in: **VLAN tagging** (private view of network), **VRF** (virtual routing: private
routing table), **multi-tenant database schemas** (private view of tables),
**VFS layer** (private view of filesystem API). The "virtual" = "private view,
shared physical resource."

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-117 |
| **Difficulty** | ★★★ Advanced (Pattern recognition) |
| **Category** | Linux |
| **Tags** | namespace pattern, address space, virtualization, indirection, container internals, pattern bridge |
| **Prerequisites** | LNX-055 (namespaces), LNX-056 (containers), LNX-111 (kernel architecture) |

---

### The Problem This Solves

**The pattern recognition gap**: Developers learn namespaces for containers and
virtual memory for programming, but rarely see they implement the SAME pattern.
Recognizing the unified pattern provides: (1) deeper intuition about when
namespaces can and cannot isolate (everything that goes through the lookup table
is isolated; things that bypass it aren't), (2) ability to reason about new
"namespace-like" features by analogy, (3) cross-domain transfer of debugging
skills (debugging namespace issues is the same cognitive task as debugging
address space issues).

---

### Textbook Definition

**Virtualization via indirection**: The fundamental technique where a system
interposes a translation layer between a name/identifier and a resource. The
caller uses a "virtual" name; the system translates to the "physical" resource.
Multiple callers can use the same virtual names (e.g., all processes have pid 1)
because each caller has its own translation table.

**Linux namespace**: A kernel feature that wraps a global system resource in an
abstraction so that processes within the namespace appear to have their own
isolated instance of the resource. Implemented as a lookup table in kernel data
structures for each namespace-type.

---

### Understand It in 30 Seconds

```bash
# === Virtual memory = indirection table (page table) ===

# Two processes: both see address 0x7fff12345678 (same virtual address)
# But: they're DIFFERENT physical memory locations!
cat /proc/1/maps | grep "7fff"
# 7fff12340000-7fff12345000 ... [stack]  <- bash's stack

cat /proc/9999/maps | grep "7fff"
# 7fff12340000-7fff12345000 ... [stack]  <- different process's stack
# SAME virtual address, completely different physical page!
# The page table = translation: virtual 0x7fff12345678 -> physical 0x...????

# === PID namespace = indirection table (PID map) ===

# Inside a container: PID 1 = the container's init process
docker exec mycontainer ps aux
# USER  PID  COMMAND
# root    1  /bin/bash          <- PID 1 inside container

# Outside the container: that same process has a DIFFERENT PID
ps aux | grep bash | head -5
# root  12345  /bin/bash   <- SAME process, PID 12345 on host!

# The PID namespace table: container_pid_1 -> host_pid_12345
# The kernel translates transparently when crossing namespace boundaries

# === Network namespace = indirection table (network stack map) ===

# Inside container: eth0 with IP 172.17.0.2
docker exec mycontainer ip addr show eth0
# 2: eth0: <...>
#     inet 172.17.0.2/16

# On host: NO eth0 with that IP, but a veth pair:
ip link show | grep veth
# 5: vethf3a2bc1@if2: <...>  <- host side of the container's eth0

# The network namespace table: container_eth0 -> host_vethf3a2bc1
# Same pattern: virtual device -> physical network path

# === Mount namespace = indirection table (mount table) ===

# Inside container: /proc shows container's processes
docker exec mycontainer ls /proc/ | head -5
# 1        <- PID 1 (the container process)
# 10       <- another container process

# On host: /proc shows ALL processes
ls /proc/ | head -5
# 1        <- host init
# 2        <- kthreadd
# ...
# 12345    <- the container process!

# The mount namespace table: container_/proc -> namespace-specific procfs
# Kernel creates a separate procfs for each PID namespace + mount namespace

# === Create a new namespace and observe ===

# Start a process in a new PID namespace:
sudo unshare --fork --pid --mount-proc bash
# Now inside new namespace:
ps aux
# USER  PID  COMMAND
# root    1  bash    <- this is the first process, so PID 1!
# root   12  ps
# Only 2 processes visible (namespace isolation working!)

# On another terminal: see the real PIDs:
ps aux | grep "unshare\|bash" | head -5
# root  99001  unshare --fork --pid --mount-proc bash
# root  99002  bash
```

---

### First Principles

```
THE CORE ABSTRACTION: PRIVATE VIEW VIA INDIRECTION

Indirection = the core of all virtualization:

Without indirection:
  All processes share one pool of memory
  Process A uses address 0x1000 for stack
  Process B also uses 0x1000 -> COLLISION! DATA CORRUPTION!
  
  All processes share one process table
  Process A is PID 1000
  Process B starts a child, also wants to be PID 1000 -> COLLISION!

With indirection (virtual address space):
  Each process has its own ADDRESS SPACE
  Process A: virtual 0x1000 -> physical 0xABCD (A's physical page)
  Process B: virtual 0x1000 -> physical 0xEF01 (B's physical page)
  Same virtual name, completely different physical resource
  Translation: CPU's MMU (Memory Management Unit) + OS page table

With indirection (PID namespace):
  Each namespace has its own PID TABLE
  Container namespace: virtual PID 1 -> real PID 12345
  Another container:   virtual PID 1 -> real PID 98765
  Both containers: their init is "PID 1" - same name, different process
  Translation: kernel's nsproxy + PID namespace table

WHAT "VIRTUAL" MEANS IN EACH CASE:

Virtual memory:
  Virtual = process-private name for a memory location
  Physical = actual DRAM cell location (or disk block for paged-out)
  Translation: page table (4-level on x86_64: PGD->PUD->PMD->PTE)
  Managed by: OS + MMU hardware
  
PID namespace:
  Virtual = process's ID within its namespace
  Physical = actual kernel task_struct (one per real process)
  Translation: PID namespace number table
  Managed by: kernel PID allocator in namespace context
  
Network namespace:
  Virtual = network device name (eth0, lo, tun0) + routing table + sockets
  Physical = actual NIC hardware + kernel network stack state
  Translation: network namespace struct (net namespace)
  Managed by: kernel network namespace subsystem
  
Mount namespace:
  Virtual = directory tree (/proc, /sys, /dev)
  Physical = underlying filesystem mounts + kernel VFS state
  Translation: mount point table (mnt namespace)
  Managed by: kernel VFS + mount namespace

IPC namespace:
  Virtual = System V IPC keys (semaphores, shared memory, message queues)
  Physical = kernel IPC objects
  Translation: IPC namespace struct
  
UTS namespace:
  Virtual = hostname + domain name
  Physical = (no physical resource: just kernel strings in uts_ns)
  Translation: strings per uts_namespace struct
  
User namespace:
  Virtual = UID/GID (can be 0 = root inside)
  Physical = actual system UID/GID (mapped via uid_map/gid_map)
  Translation: uid/gid mapping tables
  The most powerful namespace: allows non-root to create "root" container

UNIVERSAL PATTERN (all 8 Linux namespaces):
  
  ┌─────────────────────────────────────────────────┐
  │  namespace type   = which resource is virtualized│
  │  lookup table     = virtual -> real mapping      │
  │  kernel reference = which namespace this process │
  │                     belongs to (nsproxy ptr)     │
  │  transparency     = kernel translates on access  │
  └─────────────────────────────────────────────────┘

THE PATTERN IN OTHER DOMAINS:

1. VLAN (Virtual LAN) in networking:
   Same pattern as network namespace!
   VLAN tag (802.1Q): 12-bit virtual network ID
   Physical: same Ethernet cable, same switch
   Switch: inspects VLAN tag, routes to correct virtual segment
   VLAN 100 traffic: isolated from VLAN 200 traffic
   (even though they share physical wire)
   Translation: switch VLAN forwarding table

2. VRF (Virtual Routing and Forwarding):
   Same pattern as network namespace at router level!
   Multiple routing tables in one router
   VRF 1: routes for customer A (10.0.0.0/8 -> port 1)
   VRF 2: routes for customer B (10.0.0.0/8 -> port 2)
   Same destination prefix (10.0.0.0/8) means DIFFERENT ports!
   Translation: VRF table lookup before route lookup

3. Database schemas:
   Same pattern as mount namespace!
   Schema "tenant1": SELECT * FROM users -> tenant1.users
   Schema "tenant2": SELECT * FROM users -> tenant2.users
   Same SQL, same table name, different physical data
   Translation: connection's default schema context

4. VFS (Virtual File System) in Linux:
   Same pattern as mount namespace!
   open("/proc/1/status"): virtual path
   Kernel: consults VFS mount table
   -> This path is in procfs namespace -> procfs_open()
   -> Returns kernel task_struct data as text
   Translation: VFS mount table (dentry cache, superblock)

5. Browser tabs and JS contexts:
   Same pattern as PID/network namespace!
   Tab 1's window.location = "https://example.com"
   Tab 2's window.location = "https://google.com"
   Both are "window.location" - same name, different value
   Translation: JavaScript context isolation (different V8 Isolate)

THE LIMITS OF THE NAMESPACE PATTERN:

Namespaces isolate resources that GO THROUGH the translation table.
They DON'T isolate resources that BYPASS the table.

What namespaces DO isolate:
- PID: process IDs (via kernel PID namespace table)
- Network: network interfaces, routing tables, sockets
- Mount: filesystem paths and mounted filesystems
- UTS: hostname and domainname

What namespaces DON'T isolate (requires cgroups or other mechanisms):
- CPU time: a container can use all CPU (cgroups: cpu.max needed)
- Memory: a container can allocate all RAM (cgroups: memory.max needed)
- Disk bandwidth: a container can saturate I/O (cgroups: io.max needed)
- Kernel shared state: /proc/sys (partially): some sysctl values are
  per-namespace (net.ipv4.*), others are global (kernel.pid_max)

Security implication: namespaces provide ISOLATION (you can't SEE other
containers), cgroups provide LIMITS (you can't USE all resources).
Both are needed for secure, fair multi-tenancy.
```

---

### Thought Experiment

Testing namespace boundaries - what can and cannot cross:

```bash
# === Can a container process send signals to host processes? ===

# Create new PID namespace:
sudo unshare --fork --pid bash

# Inside namespace: try to kill host process
kill -9 9999  # target a host PID
# bash: kill: (9999) - No such process
# CORRECT: PID 9999 doesn't EXIST in this namespace's PID table
# The PID translation only works for processes in this namespace

# But what about the network?
# Create new NETWORK namespace:
sudo unshare --net bash
# Inside namespace:
ip addr
# 1: lo: <LOOPBACK> (only loopback! no eth0)
# Network namespace works: no access to host network interfaces

# BUT: can we access host services via loopback?
# Host runs nginx on 0.0.0.0:80
# Inside our network namespace:
curl http://127.0.0.1:80
# Connection refused
# Correct: 127.0.0.1 in OUR namespace's loopback, doesn't reach host!

# === The user namespace trick (rootless containers) ===

# Normal user: can create user namespace mapping uid=0 inside
unshare --user --map-root-user bash
# Now "inside" namespace:
id
# uid=0(root) gid=0(root)  <- appears as root!

# But outside: real UID is unchanged
echo $UID
# 1000 (regular user on host)

# The uid_map:
cat /proc/self/uid_map
# 0  1000  1  <- "virtual UID 0 maps to real UID 1000, range=1"

# Inside the user namespace: "root" operations allowed
# But: host filesystem still enforces real UID=1000!
# The translation is ONE-WAY in terms of privilege:
# host enforces real UID, namespace sees virtual UID

# Rootless Docker/Podman: uses exactly this technique
# Your containers think they're root (uid=0)
# Host: they're uid=100000 (unmapped sub-UID)
# Files written inside container: owned by 100000 on host

# === Testing the VFS analogy ===

# Each mount namespace has its own view of /proc
# Show PID namespace of shell:
ls -la /proc/self/ns/pid
# lrwxrwxrwx 1 user user 0 May 19 /proc/self/ns/pid -> 'pid:[4026531836]'
# 4026531836 = inode number of this PID namespace

# Create new namespace and check:
sudo unshare --pid --fork --mount-proc bash -c 'ls -la /proc/self/ns/pid'
# lrwxrwxrwx 1 root root 0 May 19 /proc/self/ns/pid -> 'pid:[4026532099]'
# 4026532099 = DIFFERENT namespace (different inode!)
# New namespace created for the unshare process

# List all namespaces of a container:
sudo lsns -p $(pgrep -f "docker run" | head -1)
# NS TYPE     NPROCS   PID USER COMMAND
# 4026531835 cgroup      52     1 root /lib/systemd/systemd
# 4026531836 ipc         50     1 root /lib/systemd/systemd
# 4026532099 mnt          2 12345 root /bin/bash
# 4026532100 uts          2 12345 root /bin/bash
# 4026532101 pid          2 12345 root /bin/bash
# 4026532102 net          2 12345 root /bin/bash
# Each different namespace ID = separate "address space" for that resource
```

---

### Mental Model / Analogy

```
The address space pattern = a passport + country border system

Physical reality = real world resources (memory, processes, network)
Virtual namespace = your local view

Without namespaces/address spaces:
  One global namespace for everything
  Process A named "pid=1" clashes with Process B named "pid=1"
  Like: every country uses the same phone numbers (USA 212-555-1234 vs 
  UK 0207-123-4567 would conflict without country codes)

With namespaces/address spaces:
  Each "country" (namespace) has its OWN numbering system
  USA pid_1 = UK pid_1 = China pid_1 (all "local" to their country)
  Translation: country code = namespace ID
  Border crossing = kernel translation when crossing namespace boundaries

Passport = nsproxy (process's namespace membership card)
  Every process carries: what PID namespace am I in?
                         what network namespace?
                         what mount namespace?
  When process makes a syscall: kernel checks passport, applies translation

Country (namespace) = lookup table
  USA phone book: "1-212-555-1234" -> real person in NYC
  Container PID namespace: "pid 1" -> real task_struct for PID 12345 on host
  
  Different countries: same phone number -> different real people
  Different containers: "pid 1" -> different host processes

Embassies = nsenter (entering another namespace)
  nsenter --target 12345 --pid --net -- bash
  = "enter container 12345's PID and network namespace"
  = "get an embassy visa: see THEIR view of PIDs and network"
  
  Ambassador analogy: you're in USA, you enter French embassy
  Inside embassy: French law applies (French namespace)
  You see French phone numbers (French PID table)

VRF (network) analogy:
  Customer A's routing table: 10.0.0.0/8 -> port 1
  Customer B's routing table: 10.0.0.0/8 -> port 2
  
  Same as PID namespace: "pid 1" means different things in different contexts
  VRF ID = namespace membership of the routing lookup
  Packet arrives with VRF ID -> route lookup in that VRF's table
  
VLAN analogy:
  VLAN 100 members: see each other, can't see VLAN 200
  Container in network namespace: see own eth0, can't see host's eth0
  
  VLAN tag on packet = namespace identifier
  Switch reads tag = kernel reads nsproxy
  Forwards to correct VLAN = kernel uses correct namespace lookup table

The limit of the analogy (where namespaces differ from countries):
  Countries: separate physical resources
  Namespaces: SHARED physical resources, virtual isolation only
  
  A process in a container uses the SAME CPU as host processes
  (no isolation of CPU - cgroups needed!)
  Namespace = virtual isolation (private view)
  Cgroup = physical resource limit (sharing constraint)
```

---

### Gradual Depth - Five Levels

**Level 1:**
What Linux namespaces are and which types exist (PID, network, mount, IPC,
UTS, user, cgroup). That they provide isolation for containers. The connection
to virtual memory: both give processes a private view of a resource. The
`unshare` and `nsenter` commands.

**Level 2:**
PID namespace: init process PID 1 in each namespace. Network namespace: separate
network stack per container. Mount namespace: separate filesystem view. User
namespace: rootless containers via UID mapping. How Docker uses all namespaces
together. The nsproxy structure (process's namespace membership).

**Level 3:**
The kernel implementation: nsproxy struct contains one pointer per namespace type.
When a process is created (clone with CLONE_NEW*): new namespace struct allocated,
process's nsproxy updated. Cross-namespace signal delivery: kernel translates
between namespace PIDs. /proc/PID/ns/ directory: one symlink per namespace type
containing namespace inode. nsenter: fd-based namespace entry.

**Level 4:**
User namespace privilege model: UID 0 inside user_ns != UID 0 outside. Capabilities
are per-namespace: CAP_NET_ADMIN in a network namespace = limited. Nested namespaces
(container in container). Time namespace (kernel 5.6): per-namespace clock offset
(allows different clock values in containers). Namespace lifecycle: namespace dies
when last reference drops (processes die + fd from nsenter closed).

**Level 5:**
The fundamental insight: namespaces virtualize resources but don't prevent resource
COMPETITION (cgroups needed). The exception: user namespace's UID 0 inside container
has REAL privileges for operations within the namespace (can bind to port 80 within
the network namespace, even if the outer UID is 1000). This is the rootless container
model. Seccomp + user_namespace interaction: CAP_SYS_ADMIN in user_ns allows setuid
within the namespace (potential escape vector if combined with kernel bugs). The
difference between namespace ISOLATION and namespace SECURITY: namespaces provide
isolation (can't see other namespace's resources) but not necessarily SECURITY
BOUNDARY (kernel bugs can allow privilege escalation from container namespace).

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "Namespaces isolate CPU and memory too" | Namespaces provide VISIBILITY isolation - a process cannot SEE resources outside its namespace (can't see other PIDs, can't see other network interfaces). But namespaces do NOT limit HOW MUCH of a shared resource a process can USE. A containerized process can consume ALL available CPU and ALL available memory unless cgroups (control groups) are also configured. This is the exact analogy to virtual memory: two processes can use "address 0x1000" without conflict (namespace isolation), but both compete for the same physical DRAM. The "limits" in containers = cgroups (cpu.max, memory.max). The "isolation" in containers = namespaces. Docker run --cpus=2 --memory=512m: those limits are cgroups, not namespaces. --pid, --network=host: those are namespace configurations. Both are needed for proper multi-tenancy. |
| "Containers are virtual machines" | Containers use namespaces + cgroups to provide ISOLATION within the same host kernel. VMs use a hypervisor to run a completely separate kernel instance. The difference: namespace isolation = "same kernel, private view." VM isolation = "separate kernel, hardware virtualization." Security implication: a kernel vulnerability can potentially allow a container to escape to the host (because they share the SAME kernel). A VM kernel vulnerability: isolated within the VM's kernel (hypervisor provides a second security boundary). This is why "defense in depth" for containers requires: namespaces + cgroups + seccomp + AppArmor/SELinux. Each layer provides independent isolation, compensating for the fact that there's no hardware virtualization boundary. |
| "The PID namespace means containers are truly isolated process-wise" | PID namespace provides VISIBILITY isolation (you can't see other containers' PIDs) but not SECURITY isolation. Kernel shared state crosses namespace boundaries: /proc/sys/kernel/pid_max is global (changing it affects all containers). /proc/sys/net.ipv4.ip_local_port_range: per-network-namespace (isolated). Signal isolation: a process in a PID namespace can only see processes in the same namespace, but the KERNEL'S scheduler uses the real (host) PIDs internally. A kernel vulnerability that allows raw task_struct access bypasses namespace isolation. The namespace isolation is "kernel-enforced by convention" - it works correctly for correct kernel code, but kernel bugs can violate the boundary. This is distinct from hypervisor isolation where the hardware enforces the boundary. |
| "User namespaces give containers real root privileges" | User namespaces give a process a VIRTUAL root identity (uid=0 inside the user namespace), but the process's REAL privilege on the host is its mapped UID (e.g., uid=100000). The difference: (1) File access: creating a file as uid=0 inside the user namespace -> the file is owned by uid=100000 on the host (the mapping). Other processes on the host see uid=100000, not uid=0. (2) System operations: within the user namespace, uid=0 can perform operations that require CAP_SYS_ADMIN FOR THAT NAMESPACE (e.g., configure network interfaces within the network namespace). But operations that affect the host system (loading kernel modules, accessing host hardware) still require real root. (3) This is the rootless container mechanism: Docker in rootless mode runs the entire container engine as uid=1000, but containers inside think they're running as root (uid=0 in user namespace mapping to uid=1000+ range on host). |

---

### Failure Modes & Diagnosis

```bash
# === Container can see host processes (PID namespace not set) ===

# Symptom: inside container, 'ps aux' shows ALL host processes
docker run --pid=host ubuntu ps aux | wc -l
# Shows: all host processes (hundreds!)
# Expected: only container processes

# Cause: --pid=host = share host PID namespace (no PID isolation!)
# Docker default: separate PID namespace (isolated)

# Verify namespace isolation:
docker run ubuntu ps aux | wc -l
# Shows: ~3 processes (just the container's processes)

# Check which PID namespace a process is in:
ls -la /proc/$(docker inspect mycontainer --format '{{.State.Pid}}')/ns/pid
# lrwxrwxrwx ... -> 'pid:[4026532099]'  <- unique namespace ID

ls -la /proc/1/ns/pid
# lrwxrwxrwx ... -> 'pid:[4026531836]'  <- DIFFERENT (host namespace)

# === Container can access host filesystem via mount escape ===

# Docker with volume bind mount:
docker run -v /:/host ubuntu ls /host/etc/shadow
# -rw-r----- root shadow /host/etc/shadow
# Oops! Container can see host's /etc/shadow via bind mount

# The mount namespace isolates /proc and /sys within container
# BUT: an explicit bind mount (-v /:host) bypasses the isolation!
# The mount namespace lookup table INCLUDES the bind-mounted paths

# Fix: never bind-mount / (root) into containers
# Use specific directory bind mounts only:
docker run -v /var/data:/data ubuntu ls /data
# Only /var/data visible, not /

# Check all bind mounts:
docker inspect mycontainer | python3 -c "
import json, sys
info = json.load(sys.stdin)[0]
mounts = info['Mounts']
for m in mounts:
    print(f\"Host: {m['Source']} -> Container: {m['Destination']}\")
"
```

---

### Related Keywords

**Foundational:**
LNX-055 (namespaces), LNX-056 (containers), LNX-111 (kernel architecture)

**Builds on this:**
LNX-118 (cgroup limits as SLA), LNX-119 (Unix philosophy), LNX-121 (permission models)

**Related:**
LNX-118 (cgroup limits), LNX-121 (permission models as trust boundaries)

---

### Quick Reference Card

| Namespace | Isolates | Command |
|-----------|----------|---------|
| pid | Process IDs | `unshare --pid` |
| net | Network stack | `unshare --net` |
| mnt | Filesystem tree | `unshare --mount` |
| ipc | SysV IPC | `unshare --ipc` |
| uts | Hostname | `unshare --uts` |
| user | UIDs/GIDs | `unshare --user` |
| cgroup | cgroup view | `unshare --cgroup` |
| time | Clock offset | `unshare --time` |

**3 things to remember:**
1. Namespace = private view of a resource via a lookup table. Same pattern as virtual memory (virtual address -> physical page), VLAN (VLAN tag -> physical segment), VRF (VRF ID -> routing table). All implement: "same name, different resource per context."
2. Namespaces isolate VISIBILITY only (can't SEE other containers' resources). Cgroups limit USAGE (can't USE all CPU/memory). BOTH are needed for secure multi-tenancy. Namespaces without cgroups = noisy neighbor problem.
3. User namespace: uid=0 inside maps to uid=100000 outside (rootless containers). PID namespace: container PID 1 = host PID 12345 (translation table). The kernel translates transparently on every syscall.

---

### Transferable Wisdom

The "private view via indirection" pattern is ubiquitous in computer science.
Virtual memory (per-process address space), DNS (hostname -> IP address, same
pattern: hostname is "virtual", IP is "physical"), NAT (private IP -> public IP,
same pattern: private is "virtual"), container namespaces (virtual resource name ->
host resource), VLAN (virtual LAN membership -> physical switch port rules). The
pattern also appears in software design: dependency injection (interface = virtual,
implementation = physical), abstract factory (virtual factory creates concrete
objects), feature flags (virtual feature state -> real code path). The security
implication is identical in all cases: the virtual layer provides isolation ONLY if
all access goes THROUGH the lookup table. A backdoor that bypasses the table
(raw /proc access from another namespace, a SQL injection that ignores schema context,
a host volume bind mount that skips mount namespace) breaks isolation. Security
principle: enumerate all paths to a resource; namespace/virtual isolation is only
as strong as the completeness of path coverage.

---

### The Surprising Truth

Linux namespaces are implemented with the same fundamental kernel mechanism as
virtual memory: **indirection via kernel-maintained tables**. But while the
virtual memory MMU translation happens in hardware (nanoseconds, completely
transparent), namespace translation happens in software (kernel code, adding a
few nanoseconds per syscall). For syscalls involving process lookups (kill, wait),
the kernel must translate the virtual PID to the real task_struct - this adds
approximately 100-200 nanoseconds per syscall that involves PID lookup across
namespace boundaries.

The historical sequence: virtual memory came first (1960s-1970s), then the kernel
applied the same indirection technique to process IDs, network stacks, and
filesystems (Linux namespaces, 2002-2013). The concept "virtualize a resource by
adding a translation layer" was borrowed from hardware and applied systematically
to OS resources. Containers are the practical application of this insight:
a container runtime sets up appropriate lookup tables (namespace creation) and
resource limits (cgroups) before running an application, giving it a private view
of system resources while sharing the kernel.

---

### Mastery Checklist

- [ ] Can explain the parallel between virtual memory (page table) and PID namespace (PID translation table)
- [ ] Knows all 8 namespace types and what each isolates
- [ ] Understands that namespaces = visibility isolation, cgroups = resource limits (both needed)
- [ ] Can use unshare to create new namespaces and lsns to inspect namespace membership
- [ ] Can identify the pattern in non-Linux contexts: VLAN, VRF, database schemas, JS contexts

---

### Think About This

1. The user namespace allows a non-root user to create a "root" environment.
   This is the mechanism behind rootless Docker and rootless Podman. Analyze
   the security model: inside the user namespace, UID=0 has certain capabilities
   (CAP_NET_ADMIN for the associated network namespace, etc.). What prevents
   a rootless container from being used to escalate to real root on the host?
   The answer involves: the uid mapping (uid=0 inside maps to uid=100000 outside),
   capability restrictions (capabilities don't cross namespace boundaries to parent
   namespaces), and the kernel's enforcement of the mapping. What kernel vulnerabilities
   could break this model? (Hint: search CVE databases for "user namespace privilege
   escalation" and analyze the pattern.)

2. The "virtual view via lookup table" pattern is so universal that you can find
   it in almost every layer of the computing stack. Map out a complete "virtual
   layer stack" for a request from a browser to a database in a Kubernetes pod:
   DNS (hostname -> IP), NAT/DNAT (service IP -> pod IP), Pod network namespace
   (virtual eth0 -> veth pair -> host bridge), container PID namespace (container
   PID -> host PID), Kubernetes service -> endpoints -> pod IP, database connection
   pool (virtual connection -> real socket), SQL schema isolation (table name ->
   schema.table). For each layer: what is the "lookup table"? What happens if the
   table is corrupted? What is the security implication of bypassing each layer?

3. Linux has 8 namespace types. Are there OS resources that SHOULD be namespaced
   but AREN'T yet? Consider: UID/GID visible to user-space programs
   (user namespace partially covers this), /sys/fs/bpf (BPF filesystem -
   namespace-aware?), /dev devices (device namespaces don't fully exist),
   time (time namespace was added in kernel 5.6 - what problem does it solve
   for containers?). Design a new namespace type for an OS resource that
   currently causes container interference problems. What would an "entropy
   namespace" (namespace for /dev/random) look like, and what problem
   would it solve?

---

### Interview Deep-Dive

**Foundational:**
Q: How do Linux namespaces enable container isolation, and what is the difference between namespace isolation and VM isolation?
A: NAMESPACE ISOLATION MECHANISM: Linux namespaces wrap global OS resources in a per-namespace private view. When a container starts: the container runtime (Docker, containerd) calls clone() or unshare() with CLONE_NEWPID, CLONE_NEWNET, CLONE_NEWNS, CLONE_NEWIPC, CLONE_NEWUTS, CLONE_NEWUSER flags. The kernel creates new namespace structs for each type and attaches them to the new process via its nsproxy struct. FROM THIS POINT: when the container process makes syscalls involving those resources, the kernel uses the namespace lookup table to translate between container-view and host reality. WHAT EACH NAMESPACE DOES: PID: container processes see only their own PID space (container init is PID 1, maps to real host PID e.g. 12345). They cannot send signals to host processes (different PID namespace). Network: container has its own network stack - its own eth0, routing table, iptables rules. Host's eth0 is not visible. Mount: container has its own filesystem tree view - /proc shows only container processes, /sys shows container-specific sysfs. UTS: container has its own hostname. IPC: container has its own System V IPC objects. User: container processes can appear as UID=0 while being a high UID on the host. WHAT NAMESPACES DON'T DO: Namespaces provide VISIBILITY isolation, not resource limits. A container can still consume all CPU, all RAM. For resource limits: cgroups (cpu.max, memory.max, io.max). NAMESPACE vs VM: Namespace container: shares the SAME kernel with the host. All containers on the host run on one kernel. Kernel vulnerability: can potentially be exploited by a container to escape to host. VM: each VM runs its OWN kernel. Hypervisor (KVM, Xen, VMware) provides a second security boundary. Kernel vulnerability inside VM: isolated to that VM's kernel (can't reach hypervisor or other VMs). Performance: containers start in milliseconds (no kernel boot), VMs: seconds (kernel boot). Density: containers 10-100x denser than VMs (no per-VM kernel overhead). Security: VMs stronger isolation (hardware boundary). Containers: weaker (software namespace boundary). Defense in depth for containers: namespaces + cgroups + seccomp + AppArmor/SELinux compensates for lack of hardware isolation.

**Expert:**
Q: How does the "virtualization via indirection" pattern unify virtual memory, namespaces, VLAN, and VRF? What are the invariants of this pattern?
A: THE UNIFIED PATTERN: All of these systems implement one concept: "give different clients the same name for different resources by interposing a translation layer." VIRTUAL MEMORY (per-process address space): virtual address -> page table -> physical page. Process A and Process B both use virtual address 0x1000; their page tables map to DIFFERENT physical pages. The invariant: the CPU's MMU checks the page table on every memory access. Nothing bypasses the MMU except explicit kernel operations. LINUX NAMESPACES (per-process resource view): virtual resource ID (container PID 1, virtual eth0) -> kernel namespace lookup table -> real kernel object (task_struct, network device). Every syscall that touches these resources goes through the namespace translation. The invariant: the kernel checks the process's nsproxy on every relevant syscall. VLAN (per-port network isolation): VLAN tag (12-bit ID in 802.1Q header) -> switch forwarding table -> physical port set. Two ports in different VLANs cannot communicate even on the same physical switch. The invariant: every frame is tagged on ingress, forwarded based on VLAN membership. Untagged frames bypass VLAN isolation (the "native VLAN" pitfall). VRF (per-VRF routing): VRF ID (bound to interface or socket) -> VRF routing table -> outgoing interface. Two VRFs can use the same IP prefix (10.0.0.0/8) with different routes. The invariant: routing lookup is always in the VRF-specific table, never the global table. KEY INVARIANTS OF THE PATTERN: (1) Every access to the resource MUST go through the indirection layer. (2) The indirection table is maintained by a trusted authority (kernel for namespaces/VMA, switch OS for VLANs). (3) The virtual name space is COMPLETE: every resource the client can access is in the translation table. (4) Resources outside the client's table are INVISIBLE (not just inaccessible - can't even be named). Violation of invariant 1 = namespace escape: container bind-mounts /, docker cp with root filesystem symlinks, VLAN hopping (untagged native VLAN), SQL injection bypassing schema context. The pattern's power: by understanding the invariant, you can reason about isolation in any domain. "Is there a path to resource X that doesn't go through the translation table?" If yes: isolation is broken. This mental model applies to: OAuth (token lookup table), RBAC (role assignment table), TLS sessions (session ID -> TLS state), everything that claims to provide isolation via virtual namespacing.
