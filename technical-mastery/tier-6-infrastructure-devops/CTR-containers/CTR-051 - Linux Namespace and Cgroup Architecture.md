---
id: CTR-055
title: Linux Namespace and Cgroup Architecture
category: Containers
tier: tier-6-infrastructure-devops
folder: CTR-containers
difficulty: ★★★
depends_on: CTR-018, CTR-010
used_by: CTR-052
related: CTR-054, CTR-052
tags:
  - containers
  - linux
  - internals
  - deep-dive
  - first-principles
status: complete
version: 3
layout: default
parent: "Containers"
grand_parent: "Technical Mastery"
nav_order: 51
permalink: /technical-mastery/ctr/linux-namespace-and-cgroup-architecture/
---

⚡ TL;DR - Linux namespaces provide process isolation (what a process can see); cgroups provide resource control (how much a process can use). Together, they are the kernel primitives that make containers possible.

| Metadata        |                    |     |
| :-------------- | :----------------- | :-- |
| **Depends on:** | CTR-018, CTR-010   |     |
| **Used by:**    | CTR-052            |     |
| **Related:**    | CTR-054, CTR-052   |     |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Before Linux namespaces, if two processes ran on the same machine, they
shared the same PID space, network stack, filesystem view, and hostname.
Process isolation required separate VMs - expensive, slow to start, and
wasteful of resources. There was no in-kernel mechanism to give a process
a private view of the system without full VM overhead.

**THE BREAKING POINT:**
Running multiple web applications on a single server: app A's dependency
upgrade breaks app B. App A's process can see and signal app B's process.
App A's network listener can conflict with app B's listener on the same
port. App A can exhaust the system's memory, starving app B. Shared
execution environments require heavyweight separation (VMs) or fragile
coordination.

**THE INVENTION MOMENT:**
Linux 3.8 (2013) completed the namespace suite: PID, network, mount,
UTS, IPC, user, and cgroup namespaces. Cgroups v1 (2007) added resource
control. Together they provided the kernel primitives for "lightweight
virtual machines" - what we now call containers. Docker's 2013 launch
was largely the packaging of these existing kernel features into a
developer-friendly tool.

**EVOLUTION:**
2007: Cgroups v1 merged into Linux kernel. 2008: LXC (Linux Containers)
uses namespaces + cgroups for containers. 2013: Linux 3.8 completes
the namespace suite (user namespaces). Docker 1.0 released. 2016:
Cgroups v2 merged (unified hierarchy, improved accounting). 2019: User
namespaces become production-stable. 2022: Cgroups v2 becomes the
default in major distributions (RHEL 9, Ubuntu 22.04). Kubernetes adds
cgroup v2 support. 2023: Rootless containers (using user namespaces)
become production-viable without kernel patches.

---

### 📘 Textbook Definition

**Linux namespaces** are kernel features that partition global system
resources into isolated per-namespace instances. Seven namespace types
exist: PID (process IDs), Network (network stack), Mount (filesystem
tree), UTS (hostname and NIS domain name), IPC (System V IPC, POSIX
message queues), User (user and group IDs), and Cgroup (cgroup root).
**Linux cgroups** (control groups) are a kernel mechanism to limit,
account for, and isolate the resource usage (CPU, memory, I/O, network)
of a collection of processes. Together, namespaces + cgroups implement
container isolation and resource governance.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Namespaces control what a process can see; cgroups control how much
it can consume.

**One analogy:**

> Namespaces are like hotel rooms: each guest (process) has their own
> room with their own view (filesystem), their own phone number (IP
> address), and their own room number (PID 1 in their namespace). Cgroups
> are the hotel's utility meters: each room has a maximum electricity
> (CPU) and water (memory) allowance, enforced by the building systems.

**One insight:**
A container is not a separate OS. It is a set of processes that share
the host kernel but see an isolated view of system resources via
namespaces, and are constrained in resource usage by cgroups. When a
container "escapes", it means the isolation provided by namespaces is
defeated, and the process can access resources outside its namespace.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **Namespaces are per-process** - each process has a namespace
   membership for each namespace type. A process is "in" a PID
   namespace, a network namespace, etc.
2. **Namespaces are hierarchical** - child processes inherit parent
   namespaces. Creating a new namespace creates a new root for that
   resource view.
3. **Cgroups control resource usage, not visibility** - cgroups limit
   how much CPU, memory, and I/O a set of processes can use. They do
   not affect what the processes can see.
4. **Cgroups v2 uses a single unified hierarchy** - unlike cgroups v1
   (separate hierarchy per controller), cgroups v2 has one tree with
   all controllers attached at each node.

**DERIVED DESIGN:**
Given invariant 2: containers are created by calling `clone` with the
appropriate `CLONE_NEW*` flags, which creates the child process in new
namespaces. Given invariant 3: namespace + cgroup must both be configured;
a process isolated by namespaces but without cgroup limits can still
consume all host CPU and memory.

**THE TRADE-OFFS:**

**Gain:** Namespaces + cgroups provide lightweight isolation with near-
zero overhead compared to full VMs. Container startup is milliseconds
vs. VM startup in seconds.

**Cost:** All containers share the host kernel. A kernel vulnerability
can be exploited from any container regardless of namespace isolation.
Namespaces provide visibility isolation, not kernel isolation.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

**Essential:** Seven namespace types exist because seven global system
resources required separate isolation (PID, network, filesystem, etc.).

**Accidental:** Cgroups v1's separate hierarchy per controller (one tree
for CPU, another for memory) created complex interaction effects. Cgroups
v2 unified them.

---

### 🧪 Thought Experiment

**SETUP:**
Two processes run on the same Linux host without any namespace isolation.

**WHAT HAPPENS:**
Process A can see all processes on the host via `/proc`. Process A can
send SIGKILL to process B. Process A can bind to any port. Process A
can mount and unmount filesystems. Process A can read /etc/hosts and
modify it (affecting process B). There is no isolation.

**WHAT HAPPENS WITH NAMESPACES:**
Process A is placed in new PID, network, mount, and UTS namespaces.
From process A's perspective: it is PID 1 in its namespace (sees only
its own descendant processes in /proc). It has its own network interface
and IP address. It has its own /etc/hosts and /etc/hostname. It cannot
see or signal processes in other namespaces. It cannot bind to ports
that are already in use in its own network namespace.

**THE INSIGHT:**
Namespaces create the illusion of a private system for each container.
The kernel maintains the mapping between global resource IDs and
namespace-local IDs. When process A looks up PID 1, the kernel returns
its own PID (the first process in its PID namespace) not the host's
PID 1 (init/systemd).

---

### 🧠 Mental Model / Analogy

> Namespaces are like a magic mirror in a hotel hallway. Each guest who
> looks in the mirror sees a different view of the hotel. Guest A sees
> themselves as the only guest (PID namespace), with their own room
> (filesystem), their own phone network (network namespace). But all
> guests are actually in the same physical building (same kernel). The
> mirror is the kernel's namespace translation layer.

Element mapping:

- **Physical building** = Linux host kernel
- **Magic mirror** = namespace translation layer
- **Guest's unique view** = process's namespace-local view
- **Room** = mount namespace (container filesystem)
- **Phone network** = network namespace
- **Guest number** = PID (namespace-local)
- **Building utilities** = cgroups (CPU, memory limits)

Where this analogy breaks down: a real hotel's walls are physical
barriers; namespace isolation is a kernel-level software boundary that
can be defeated by kernel vulnerabilities.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Linux has built-in features that let programs pretend they are the only
program running (namespaces) and that limit how much CPU and memory
each program can use (cgroups). Docker and Kubernetes use these features
to run multiple isolated containers on one machine.

**Level 2 - How to use it (junior developer):**
You rarely manipulate namespaces or cgroups directly - Docker and
Kubernetes do it for you. But when debugging, `nsenter` lets you enter
a container's namespaces from the host. `cat /proc/<pid>/cgroup` shows
which cgroup a process is in. `cat /sys/fs/cgroup/<cgroup>/memory.current`
shows current memory usage.

**Level 3 - How it works (mid-level engineer):**
When runc creates a container, it calls `clone(CLONE_NEWPID |
CLONE_NEWNET | CLONE_NEWNS | CLONE_NEWUTS | CLONE_NEWIPC)`. The child
process starts in new namespaces. runc then mounts the container
filesystem, writes `hostname`, and sets up the cgroup via the cgroup
filesystem (`/sys/fs/cgroup`). The container process is then exec'd
into the configured environment.

**Level 4 - Why it was designed this way (senior/staff):**
Each namespace type was added independently in the Linux kernel as the
demand arose. PID namespaces (2008) solved process isolation. Network
namespaces (2009) solved network isolation. User namespaces (2013)
solved privilege separation (allowing containers to run as root inside
the namespace without host root privileges). Cgroups v2 (2016) unified
the controller hierarchy to solve the v1 coordination problems (memory
accounting inconsistencies between controllers, difficulty attaching
single processes to multiple v1 hierarchies).

**Expert Thinking Cues:**

- "Is the container running with user namespaces enabled? If not, root
  inside the container is root on the host kernel."
- "Is the cgroup v1 or v2? v2 is required for correct memory accounting
  in Kubernetes QoS classes on modern distributions."
- "Can a process in this container enter another container's namespace
  via /proc/<pid>/ns/*? If the container has CAP_SYS_PTRACE, yes."

---

### ⚙️ How It Works (Mechanism)

**SEVEN NAMESPACE TYPES:**

```
PID   - Process IDs: containers have PID 1
NET   - Network stack: own IP, routes, iptables
MNT   - Mount tree: own filesystem view
UTS   - Hostname and NIS domain name
IPC   - System V IPC, POSIX message queues
USER  - UID/GID mapping (root inside != root outside)
CGROUPNS - Cgroup root (container sees its cgroup root)
```

**CGROUP V2 HIERARCHY:**

```
/sys/fs/cgroup/                  (root cgroup)
  kubepods/
    burstable/
      pod<uuid>/
        <container-id>/
          cpu.max        # CPU limit
          memory.max     # Memory hard limit
          memory.high    # Soft memory limit
          io.max         # Block I/O limit
```

**NAMESPACE SYSTEM CALLS:**

```
clone(CLONE_NEWPID|CLONE_NEWNET|...) - create new
  namespaces
unshare(CLONE_NEWNS)                 - leave current
  namespace
setns(fd, nstype)                    - join existing
  namespace
/proc/<pid>/ns/                      - namespace file
  descriptors
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW (Container Start):**

```
runc: clone() with CLONE_NEW* flags
  |   Child process in new namespaces
  |           ← YOU ARE HERE
  v
runc: pivot_root() - switch to container rootfs
  |
  v
runc: mount proc, sys, dev in new MNT ns
  |
  v
runc: write cgroup limits to cgroup v2 files
  |
  v
runc: set capabilities, seccomp filter
  |
  v
runc: exec() container entrypoint
Container runs with isolated view + resource limits
```

**FAILURE PATH:**
Container process exceeds cgroup memory limit. Kernel OOM killer fires
within the cgroup. Container PID 1 receives SIGKILL. Pod enters
`OOMKilled` state. Without cgroup limits, the process could exhaust
host memory, causing node-level OOM affecting all pods.

**WHAT CHANGES AT SCALE:**
At scale, cgroup accounting overhead accumulates across thousands of
containers. Cgroup v2 reduces this overhead vs. v1. The cgroup hierarchy
must be maintained consistently - stale cgroup directories from deleted
containers accumulate if not cleaned up.

---

### 💻 Code Example

```bash
# Inspect namespaces of a running container
PID=$(docker inspect --format='{{.State.Pid}}' nginx)
ls -la /proc/$PID/ns/
# Each symlink is a namespace the process is in

# Enter a container's network namespace from the host
nsenter --target $PID --net -- ip addr
# Shows the container's network interfaces, not host's

# Enter a container's mount namespace
nsenter --target $PID --mount -- ls /
# Shows the container's filesystem, not host's

# Inspect cgroup membership
cat /proc/$PID/cgroup
# Shows the cgroup hierarchy paths for this process

# Check cgroup v2 memory limits
CGROUP=$(cat /proc/$PID/cgroup | \
  grep "0::" | cut -d: -f3)
cat /sys/fs/cgroup${CGROUP}/memory.max
cat /sys/fs/cgroup${CGROUP}/memory.current

# Check CPU limits (cgroup v2)
cat /sys/fs/cgroup${CGROUP}/cpu.max
# Format: quota period (e.g. 500000 1000000 = 50% of one CPU)
```

```bash
# Create a namespace manually (demo/learning)
# Create a new network namespace
ip netns add mytest
ip netns exec mytest ip addr   # only loopback visible

# Create a process in a new PID namespace
unshare --pid --fork --mount-proc bash
# Inside: ps aux shows only this bash process (PID 1)
```

**How to test / verify correctness:**

```bash
# Verify cgroup limits are applied
kubectl run memtest --image=polinux/stress \
  --limits='memory=128Mi' -- stress --vm 1 \
  --vm-bytes 256M --vm-hang 0

# Check that OOMKill fires (not host OOM)
kubectl describe pod memtest | grep OOMKilled

# Verify namespace isolation
POD=$(kubectl get pod -l app=nginx -o name | head -1)
kubectl exec $POD -- hostname  # container hostname
hostname                        # host hostname - different
```

---

### ⚖️ Comparison Table

| Namespace Type | Isolates | System Call | Container Equivalent |
|---|---|---|---|
| PID | Process IDs | clone(CLONE_NEWPID) | Container PID 1 |
| NET | Network stack | clone(CLONE_NEWNET) | Container IP/ports |
| MNT | Filesystem | clone(CLONE_NEWNS) | Container rootfs |
| UTS | Hostname | clone(CLONE_NEWUTS) | Container hostname |
| IPC | SysV IPC | clone(CLONE_NEWIPC) | Inter-process comms |
| USER | UID/GID | clone(CLONE_NEWUSER) | Rootless containers |
| CGROUP | Cgroup root | clone(CLONE_NEWCGROUP) | Cgroup visibility |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "A container is a mini-VM" | A container is a set of processes with isolated views (namespaces) and resource limits (cgroups). It shares the host kernel. A VM has its own kernel; a container does not. |
| "Root in a container is not dangerous" | Without user namespaces, root (UID 0) inside a container is root on the host kernel. A privileged container can access host devices, load kernel modules, and bypass most namespace isolation. |
| "Cgroups prevent a container from crashing the host" | Cgroups limit CPU and memory but do not protect all resources. A container can still exhaust PIDs (fork bomb), file descriptors, or network connections if `pids.max`, `nofile`, and network limits are not set. |
| "Namespace isolation is equivalent to VM isolation" | A VM has a separate kernel; namespaces share the host kernel. A kernel vulnerability exploitable from inside a namespace can affect the host. VM isolation requires a hypervisor boundary. |
| "Cgroups v1 and v2 are interchangeable" | Cgroups v2 has a unified hierarchy and improved memory accounting. Kubernetes features like memory QoS require cgroups v2. Running mixed v1/v2 on a node causes Kubernetes to use only v1 features. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: OOMKilled - Missing or Misconfigured Cgroup Limit**
**Symptom:** Pod restarts repeatedly with `OOMKilled` status. The
application appears to need less than the configured memory limit.

**Root Cause:** The application has a memory leak. The cgroup memory
limit correctly kills it when it exceeds the limit. The limit may also
be set too low for the actual working set.

**Diagnostic:**

```bash
# Check OOM events
kubectl describe pod <pod> | grep -i oom

# Check actual memory usage over time
kubectl top pod <pod>

# Check cgroup memory events on the node
CGROUP=$(cat /proc/$POD_PID/cgroup | \
  grep "0::" | cut -d: -f3)
cat /sys/fs/cgroup${CGROUP}/memory.events
# Look for oom_kill count
```

**Fix:** Increase memory limit to match actual working set, or fix
the memory leak. Add memory `requests` to ensure the pod is scheduled
on a node with sufficient available memory.

**Prevention:** Set memory `requests` equal to expected steady-state
usage. Set `limits` to peak usage + 20% buffer. Monitor `memory.high`
events (soft limit) before `memory.max` (hard limit + OOMKill) is hit.

---

**Failure Mode 2: PID Exhaustion (fork bomb protection)**
**Symptom:** Pod cannot start new processes. `kubectl exec` hangs.
Application logs show `fork: Resource temporarily unavailable`.

**Root Cause:** The container has exhausted its PID namespace cgroup
limit. A fork bomb, a thread leak, or missing `pids.max` allows PID
exhaustion.

**Diagnostic:**

```bash
# Check PID count inside container
kubectl exec <pod> -- cat /proc/sys/kernel/pid_max
kubectl exec <pod> -- ls /proc | wc -l

# Check cgroup PID limit
CGROUP=$(cat /proc/$POD_PID/cgroup | \
  grep "0::" | cut -d: -f3)
cat /sys/fs/cgroup${CGROUP}/pids.max
cat /sys/fs/cgroup${CGROUP}/pids.current
```

**Fix:** Set `pids.max` in the pod spec (`spec.containers[].resources`
does not expose this directly - requires admission webhook or RuntimeClass
configuration). Kill the leaking process.

**Prevention:** Set Kubernetes `--pod-max-pids` flag. Enable `PodPidsLimit`
admission plugin to enforce PID limits per pod.

---

**Failure Mode 3: Network Namespace Leak (Security)**
**Symptom:** `ip netns list` on the host shows thousands of network
namespaces. Host netfilter/conntrack table is exhausted.

**Root Cause:** Containers are deleted but their network namespaces are
not cleaned up (CNI plugin cleanup bug). Each orphaned namespace retains
netfilter rules and conntrack state.

**Diagnostic:**

```bash
# Count network namespaces on the host
ip netns list | wc -l

# Check for orphaned namespaces (no process in them)
for ns in $(ip netns list | awk '{print $1}'); do
  count=$(ip netns exec $ns ls /proc | wc -l)
  [ "$count" -lt 2 ] && echo "Empty: $ns"
done

# Check conntrack table usage
conntrack -C
cat /proc/sys/net/netfilter/nf_conntrack_max
```

**Fix:** Manually clean orphaned namespaces: `ip netns delete <ns>`.
File a bug against the CNI plugin. Upgrade to patched version.

**Prevention:** Monitor namespace count on nodes. Alert if count exceeds
expected maximum (pods per node * 2). Validate CNI cleanup with chaos
engineering (delete pods rapidly and check namespace count returns to
baseline).

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[CTR-018 - Linux Namespaces]] - namespace concepts overview
- [[CTR-010 - Cgroups]] - cgroup concepts overview

**Builds On This (learn these next):**

- [[CTR-052 - Container Runtime Internals (runc, containerd)]] - how runc uses namespaces/cgroups

**Alternatives / Comparisons:**

- [[CTR-054 - Container Image Format Design (OCI)]] - the image layer (not isolation)
- [[CTR-052 - Container Runtime Internals (runc, containerd)]] - how runc wires it together

---

### 📌 Quick Reference Card

```
┌────────────────────────────────────────────────────┐
│ WHAT IT IS  │ Kernel primitives for containers    │
│ PROBLEM     │ Lightweight isolation without VMs   │
│ KEY INSIGHT │ Namespaces = visibility; cgroups=use│
│ USE WHEN    │ Debugging isolation or resource issues│
│ AVOID WHEN  │ N/A - always active for containers  │
│ TRADE-OFF   │ Lightweight isolation vs. shared    │
│             │ kernel vulnerability surface         │
│ ONE-LINER   │ namespaces see; cgroups limit       │
│ NEXT EXPLORE│ CTR-052 Runtime Internals           │
└────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Seven namespace types provide isolation of visibility; cgroups provide
   resource limits - both are required for container isolation.
2. Root inside a container without user namespaces is root on the host
   kernel - user namespaces are the key to rootless containers.
3. Cgroups v2 (unified hierarchy) is required for correct Kubernetes
   memory QoS - prefer distributions that default to cgroups v2.

**Interview one-liner:**
"Linux containers are processes in new namespaces (PID, NET, MNT, UTS,
IPC, USER) that provide an isolated system view, constrained by cgroups
that limit CPU, memory, and I/O - the two kernel mechanisms together
implement container isolation without a separate kernel."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Visibility isolation (namespaces) and resource isolation (cgroups) are
orthogonal concerns that must both be applied. A process with a private
view but no resource limits can starve all other processes. A process
with resource limits but a shared view can read other processes' data.
Complete isolation requires both dimensions independently satisfied.

**Where else this pattern appears:**

- **Operating system process model:** Processes have separate virtual
  address spaces (visibility isolation) and are scheduled with CPU
  quotas (resource isolation). The OS applies both independently.
- **Database multi-tenancy:** Schema-level isolation (visibility) +
  query-level resource groups (resource limits) together provide tenant
  isolation. Either alone is insufficient.
- **Cloud account IAM:** IAM policies restrict what a user can see
  (visibility); service quotas and budget alerts restrict how much they
  can consume (resource limits). Both are required for multi-tenant
  cloud governance.

---

### 💡 The Surprising Truth

Linux namespaces and cgroups were not designed with containers in mind.
Namespaces were added to Linux between 2002 and 2013 primarily for the
Linux-VServer project (a competing container technology that never became
mainstream). Cgroups were added in 2007 by Google engineers who needed
resource governance for Google's internal workload scheduler (Borg).
Docker's 2013 innovation was not inventing new kernel technology - it
was discovering that packaging these existing, independently developed
kernel features together with a developer-friendly CLI and image format
created something genuinely new: the modern container. The kernel
developers who wrote namespaces and cgroups in the 2000s largely did
not anticipate the container revolution their work would enable.

---

### 🧠 Think About This Before We Continue

**Q1 (E - First Principles):** A container running as UID 1000 inside
a user namespace is mapped to UID 100000 on the host. If the container
writes a file, what UID owns the file on the host filesystem? If the
container is given CAP_CHOWN inside its user namespace, can it change
the ownership of a host file to UID 0? Why or why not?
*Hint:* User namespace UID mapping means the container's UID 1000 maps
to host UID 100000. File ownership uses the host UID in the filesystem.
CAP_CHOWN inside a user namespace is scoped to that namespace's UID
range. What is the boundary of the capability?

**Q2 (D - Root Cause):** A Kubernetes pod has `memory: limits: 512Mi`
but the node is running cgroups v1. The application uses both malloc
(heap memory) and mmap (file-backed memory). The cgroup `memory.limit_in_bytes`
is correctly set to 512Mi. However, the pod's RSS exceeds 512Mi without
triggering OOMKill. How is this possible under cgroups v1?
*Hint:* Cgroups v1 has separate `memory` and `kmem` controllers.
File-backed mmap pages may be accounted differently than heap pages.
Page cache can grow beyond the limit under certain v1 accounting
configurations. How does cgroups v2's unified memory controller fix this?

**Q3 (C - Design Trade-off):** Rootless containers (user namespaces)
allow non-root users to run containers. However, a limitation is that
user namespace containers cannot bind to ports below 1024 (privileged
ports). A web server container needs to listen on port 80. What are
the three approaches to solve this, and what are their security
trade-offs?
*Hint:* Consider: (1) map the container port 80 to a host port >1024
via network namespace port mapping, (2) set the `net.ipv4.ip_unprivileged_port_start`
sysctl to 0 (all ports unprivileged), (3) use `CAP_NET_BIND_SERVICE`
with user namespace ambient capabilities. Which approach is least
privilege?