---
layout: default
title: "Linux Namespaces"
parent: "Linux"
nav_order: 157
permalink: /linux/linux-namespaces/
number: "0157"
category: Linux
difficulty: ★★★
depends_on: Process Management, Linux File System Hierarchy
used_by: Containers, Kubernetes, Docker
related: Cgroups, Kernel Modules, Docker
tags:
  - linux
  - os
  - containers
  - deep-dive
---

# 157 — Linux Namespaces

⚡ TL;DR — Linux namespaces isolate what a process can _see_ — each namespace wraps a different system resource (process IDs, network stack, filesystem mounts, users) so that a process inside sees a private view, separate from the host and other namespaces.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
All processes on a Linux system share the same view of PIDs, network interfaces, filesystem mount points, users, and IPC (inter-process communication) objects. A process can list every other process's PID, see all open ports, and potentially send signals to unrelated processes. Multi-tenancy is impossible without heavy virtual machine overhead — to isolate two customers' workloads you need two separate VMs with separate kernels.

**THE BREAKING POINT:**
A cloud provider wants to run two customers' untrusted code on the same physical machine. Customer A should not be able to see Customer B's processes, connect to B's services, or read B's filesystem. With a shared kernel and no namespaces, this level of isolation requires full VMs — 1-2 seconds to start, gigabytes of overhead per tenant.

**THE INVENTION MOMENT:**
Linux namespaces solve this. A container process lives in its own PID namespace (PIDs start at 1 inside), its own network namespace (its own private network stack and interfaces), its own mount namespace (private filesystem view), and its own user namespace (can appear to be root without being root on the host). This is the kernel mechanism that makes Docker containers possible.

---

### 📘 Textbook Definition

A **Linux namespace** wraps a global system resource so that processes within the namespace have an isolated instance of that resource, invisible to processes outside the namespace. Linux currently implements 8 namespace types:

| Namespace  | Isolates                         | Flag            |
| ---------- | -------------------------------- | --------------- |
| **pid**    | Process IDs                      | CLONE_NEWPID    |
| **net**    | Network stack, interfaces, ports | CLONE_NEWNET    |
| **mnt**    | Filesystem mount points          | CLONE_NEWNS     |
| **uts**    | Hostname, domain name            | CLONE_NEWUTS    |
| **ipc**    | POSIX message queues, semaphores | CLONE_NEWIPC    |
| **user**   | User and group IDs               | CLONE_NEWUSER   |
| **cgroup** | Cgroup root directory            | CLONE_NEWCGROUP |
| **time**   | System time offsets              | CLONE_NEWTIME   |

Namespaces are created via `clone()`, `unshare()`, or `nsenter()` system calls, and are represented as files in `/proc/PID/ns/`.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Namespaces give each container its own private view of the kernel — its own process list, network, filesystem, and hostname — without running a separate kernel.

**One analogy:**

> Namespaces are like a cruise ship's multiple restaurants. Each restaurant (namespace) has its own menu (filesystem), its own staff roster (PID list), its own PA system (UTS/hostname), and its own section of the deck (network). Passengers in Restaurant A can't see Restaurant B's kitchen or hear Restaurant B's announcements — but they're all on the same ship (shared kernel). The restaurants exist by dividing the shared space into isolated zones, not by building separate ships.

**One insight:**
Namespaces isolate _visibility_ (what a process can see), while cgroups limit _resources_ (how much a process can consume). Containers need both. A container without cgroups can see only its own processes but still consume all the host's CPU. A container without namespaces has resource limits but can see all host processes.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Namespaces change what a process can see, not what it can do — permissions still apply.
2. Namespace membership is inherited: child processes inherit the parent's namespaces.
3. A namespace remains alive as long as at least one process references it (or a bind mount holds it open).
4. Namespaces nest: a PID namespace can contain child PID namespaces, each with its own PID 1.

**DERIVED DESIGN:**
Each namespace type is implemented as a kernel object. `clone(CLONE_NEWPID)` creates a new PID namespace and starts the child process as PID 1 within it. The child can see only processes in its PID namespace and its descendants. From outside (host), those processes have normal host PIDs.

`/proc/PID/ns/` contains symlinks for each namespace the process is a member of:

```
/proc/1234/ns/pid     → pid:[4026531836]
/proc/1234/ns/net     → net:[4026532008]
/proc/1234/ns/mnt     → mnt:[4026532010]
```

The inode number after the colon is the namespace ID. Processes in the same namespace share the same inode number. `nsenter -t PID -n -p` joins a process's network and PID namespaces.

**THE TRADE-OFFS:**
**Gain:** Container-level isolation without VM overhead; startup in milliseconds; shared kernel (efficient); namespaces are composable.
**Cost:** Shared kernel = shared vulnerabilities; a kernel exploit from inside a container affects the host; user namespaces have had several privilege escalation CVEs; not a security boundary equivalent to VMs.

---

### 🧪 Thought Experiment

**SETUP:**
Two containers are running on the same host. Container A is running nginx. Container B is running a database. You want to verify that Container B cannot see Container A's process tree.

**WITHOUT NAMESPACES:**
Every process on the system shares one PID namespace. Container B's shell can run `ps aux` and see Container A's nginx processes, their environment variables (sometimes visible via `/proc/PID/environ`), and open file descriptors. Isolation doesn't exist.

**WITH PID NAMESPACE:**

```bash
# Inside Container A:
ps aux
# PID 1: nginx (appears as PID 1 — namespace root)
# PID 15: nginx worker

# Inside Container B:
ps aux
# PID 1: postgres (appears as PID 1 — its own namespace)
# Container B cannot see Container A's processes at all
# The PID namespaces are completely separate
```

From the host:

```bash
ps aux | grep nginx   # Host PID 3420, 3421
ps aux | grep postgres # Host PID 5678
```

The host sees both. Each container sees only its own namespace. This is the isolation that makes containers safe for co-location.

**THE INSIGHT:**
The same process has two identities: its PID inside the namespace (as the container sees it) and its PID on the host (as the kernel tracks it). The container's PID 1 might be host PID 3420. `ps` inside the container shows 1; `/proc` on the host shows 3420.

---

### 🧠 Mental Model / Analogy

> Namespaces are like augmented reality glasses with different reality filters. Each container wears glasses with a different filter: when you look at processes, you see only the ones in your namespace. When you look at the network, you see only your namespace's interfaces. When you look at the filesystem, you see only your namespace's mounts. Everyone is standing in the same room (same kernel) but each sees a different reality — completely isolated views of shared underlying resources.

- "Same room" → shared kernel
- "Reality filter" → namespace
- "Different process lists" → PID namespace
- "Different network views" → net namespace
- "Glasses that can be shared" → two processes in the same namespace see the same reality

Where this analogy breaks down: the analogy suggests complete isolation, but namespaces don't prevent kernel vulnerability exploitation — if someone finds a way to "take off the glasses" (kernel exploit), they see the full shared reality.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Namespaces are the kernel feature that makes containers possible. They give each container its own private view of the system — its own process list, network interfaces, and hostname — without needing a separate operating system. It's like giving each apartment in a building its own private mailbox, doorbell, and address book, even though they share the same building infrastructure.

**Level 2 — How to use it (junior developer):**
See namespaces in use: `ls -la /proc/self/ns/`. Check which namespace a process is in: `ls -la /proc/$(pidof docker)/ns/`. Compare namespaces: if two symlinks point to the same inode, they're in the same namespace. Enter a container's namespace: `nsenter -t <container-PID> -n -- ip addr show` (see the container's network from the host). Create a new network namespace: `ip netns add myns && ip netns exec myns ip link show`.

**Level 3 — How it works (mid-level engineer):**
Namespaces are created with `clone()` (at process creation) or `unshare()` (for an existing process). The kernel stores namespace pointers in `task_struct.nsproxy`. Each `nsproxy` points to the process's current namespace for each type. `fork()` inherits parent namespaces. `clone(CLONE_NEWPID)` creates a new PID namespace; the first process in it gets PID 1. PID namespace nesting: a child PID namespace can see its own processes; the parent namespace can see processes in child namespaces with host PIDs. `/proc/PID/ns/` symlinks persist the namespace even after its last process exits, as long as the fd is held open.

**Level 4 — Why it was designed this way (senior/staff):**
Namespaces were added incrementally: mount namespaces (2002, kernel 2.4.19), UTS+IPC+net+PID (2006-2009), user namespaces (2013, kernel 3.8). User namespaces were the most controversial — they allow unprivileged users to create containers with apparent root inside. This enables rootless containers (no SUID, no capabilities on the runtime) at the cost of a significantly expanded kernel attack surface. The most serious container escapes in recent years (CVE-2019-5736 runc, CVE-2022-0185 filesystem) exploited kernel bugs reachable from within namespaces. The architectural response has been to restrict which namespaces unprivileged users can create (`unprivileged_userns_clone` sysctl).

---

### ⚙️ How It Works (Mechanism)

**Inspecting namespaces:**

```bash
# See current process's namespaces
ls -la /proc/self/ns/

# Compare container and host namespaces
HOST_NET=$(readlink /proc/1/ns/net)
CONTAINER_PID=$(docker inspect --format '{{.State.Pid}}' mycontainer)
CONTAINER_NET=$(readlink /proc/$CONTAINER_PID/ns/net)
echo "Host: $HOST_NET, Container: $CONTAINER_NET"
# Different inodes = different network namespaces

# Find all processes in a specific network namespace
NS_INODE=$(readlink /proc/$CONTAINER_PID/ns/net \
  | grep -oP '\d+')
for pid in /proc/[0-9]*/ns/net; do
  if readlink "$pid" | grep -q "$NS_INODE"; then
    echo "PID: $(dirname $pid | grep -oP '\d+')"
  fi
done
```

**Working with network namespaces:**

```bash
# Create and configure a network namespace
ip netns add myns

# List network namespaces
ip netns list

# Run command inside namespace
ip netns exec myns ip link show
ip netns exec myns ip addr show

# Configure networking for the namespace
# Create veth pair (virtual ethernet cable)
ip link add veth0 type veth peer name veth1
ip link set veth1 netns myns

# Configure host end
ip addr add 192.168.100.1/24 dev veth0
ip link set veth0 up

# Configure namespace end
ip netns exec myns ip addr add \
  192.168.100.2/24 dev veth1
ip netns exec myns ip link set veth1 up
ip netns exec myns ip link set lo up

# Test connectivity
ping 192.168.100.2   # from host to namespace

# Delete namespace
ip netns del myns
```

**Using unshare (create namespaces for testing):**

```bash
# Create new PID and mount namespaces
# (simulates a container-like environment)
unshare --fork --pid --mount-proc bash
# Now inside new PID namespace:
ps aux   # shows only current shell (PID 1)

# New UTS namespace (private hostname)
unshare --uts bash
hostname mycontainer  # only affects this namespace

# New network namespace (no network)
unshare --net bash
ip link show  # only loopback
```

**nsenter (enter existing namespaces):**

```bash
# Enter container's network namespace
# (useful for debugging from host)
CONTAINER_PID=$(docker inspect \
  --format '{{.State.Pid}}' mycontainer)

# Enter all namespaces
nsenter -t $CONTAINER_PID --all -- bash

# Enter only network namespace
nsenter -t $CONTAINER_PID -n -- \
  tcpdump -i eth0  # use host tools in container network
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
┌────────────────────────────────────────────────┐
│  Docker container start: namespace creation    │
└────────────────────────────────────────────────┘

 docker run --rm -it ubuntu bash
       │
       ▼
 containerd creates new namespaces:
 clone(CLONE_NEWPID | CLONE_NEWNET |
       CLONE_NEWNS | CLONE_NEWUTS |
       CLONE_NEWIPC | CLONE_NEWUSER)
       │
       ▼
 runc (OCI runtime):
 ├── PID namespace: bash gets PID 1
 ├── NET namespace: private network stack created
 │   veth pair connects to docker0 bridge
 ├── MNT namespace: overlay filesystem mounted
 │   as root filesystem for container
 ├── UTS namespace: hostname set to container ID
 ├── IPC namespace: private semaphores/queues
 └── USER namespace: UID 0 inside = UID 1000 on host
       │
       ▼
 Container process running:
 bash (container PID 1 = host PID 4532)
 Can see only: its own processes, its net stack,
 its filesystem root, its hostname
       │
       ▼
 docker stop → SIGTERM → namespace cleanup
 When last process exits: namespaces destroyed
```

---

### 💻 Code Example

**Example 1 — Verify container isolation:**

```bash
#!/bin/bash
# Verify that a container is properly namespaced

CONTAINER=${1:-$(docker ps -q | head -1)}
C_PID=$(docker inspect --format '{{.State.Pid}}' \
  "$CONTAINER")

echo "Container: $CONTAINER (host PID: $C_PID)"
echo ""
echo "=== Namespace isolation check ==="

for ns in pid net mnt uts ipc user; do
  HOST_NS=$(readlink /proc/1/ns/$ns)
  C_NS=$(readlink /proc/$C_PID/ns/$ns 2>/dev/null)

  if [ "$HOST_NS" = "$C_NS" ]; then
    echo "WARN: $ns namespace SHARED with host!"
  else
    echo "OK:   $ns namespace isolated"
    echo "      host=$HOST_NS"
    echo "      container=$C_NS"
  fi
done
```

**Example 2 — Enter container namespace for debugging:**

```bash
#!/bin/bash
# Debug a container using host tools (no docker exec needed)
CONTAINER=$1
C_PID=$(docker inspect --format '{{.State.Pid}}' \
  "$CONTAINER")

echo "Entering network namespace of $CONTAINER..."
echo "Running: tcpdump (host tool in container network)"
echo ""

# Run host's tcpdump in the container's network namespace
nsenter -t "$C_PID" -n -- \
  tcpdump -i any -nn -c 100 not port 22
```

---

### ⚖️ Comparison Table

| Isolation Level     | Mechanism         | Startup | Overhead | Kernel Shared        |
| ------------------- | ----------------- | ------- | -------- | -------------------- |
| Process (same user) | Unix permissions  | Instant | None     | Yes                  |
| **Linux Namespace** | clone/unshare     | < 100ms | Minimal  | Yes                  |
| VM (KVM/QEMU)       | Hypervisor        | 1-10s   | ~200MB   | No                   |
| VM (Firecracker)    | microVM           | < 200ms | ~5MB     | No                   |
| gVisor (sandbox)    | User-space kernel | ~500ms  | High     | Yes (syscall filter) |

How to choose: namespaces for standard containers (Docker, Kubernetes); VMs for hard security boundaries between tenants; Firecracker for serverless (fast VMs); gVisor for high-security containers without full VM overhead.

---

### ⚠️ Common Misconceptions

| Misconception                                     | Reality                                                                                                                                        |
| ------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| Namespaces provide complete security isolation    | Namespaces isolate visibility; a kernel vulnerability can escape any namespace; VMs provide a stronger security boundary                       |
| PID 1 inside a container is isolated from SIGTERM | PID 1 in a PID namespace must properly handle SIGTERM — Linux's normal "zombie reaping" is the responsibility of PID 1 in each namespace       |
| Network namespaces prevent all communication      | Processes in different net namespaces can communicate via shared unix sockets if they share the same mount namespace, or via exposed ports     |
| User namespaces make containers as safe as VMs    | User namespaces have historically been a significant source of kernel privilege escalation vulnerabilities                                     |
| Destroying a namespace's last process destroys it | A namespace persists as long as any fd references it — a bind mount of `/proc/PID/ns/net` keeps a namespace alive after its last process exits |

---

### 🚨 Failure Modes & Diagnosis

**Container Can Reach Host Network**

**Symptom:**
A process inside a container can connect to services on the host that should be unreachable.

**Root Cause A:**
Container started with `--network=host` — no network namespace isolation.

**Root Cause B:**
Host service bound to `0.0.0.0` (all interfaces) including the docker bridge interface.

**Diagnostic Command:**

```bash
# Check if container uses host network namespace
docker inspect mycontainer | grep NetworkMode
# "host" = no isolation

# Verify network namespace is separate
C_PID=$(docker inspect --format '{{.State.Pid}}' mycontainer)
readlink /proc/1/ns/net     # host
readlink /proc/$C_PID/ns/net  # container
# If same inode → shared network namespace → no isolation
```

**Fix:**
Remove `--network=host` from container configuration; use proper network segmentation.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Process Management` — process creation (fork/exec/clone), PIDs, and process trees are foundational to understanding PID namespaces
- `Linux File System Hierarchy` — mount namespaces isolate filesystem views; understanding VFS and mount points is required

**Builds On This (learn these next):**

- `Cgroups` — namespaces isolate visibility; cgroups limit resources; containers need both
- `Containers` — Docker and container runtimes use all 8 namespace types as the core isolation primitive
- `Kubernetes` — Kubernetes pod network isolation is implemented using network namespaces, one per pod

**Alternatives / Comparisons:**

- `Cgroups` — resource limits (complementary to namespaces, not an alternative)
- `KVM/QEMU VMs` — hardware virtualisation providing full kernel isolation; stronger security, higher overhead
- `Firecracker` — microVMs that use hardware virtualisation for strong isolation with container-like startup speeds

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ 8 kernel resource wrappers that give each │
│              │ process a private view: PIDs, network,    │
│              │ mounts, hostname, IPC, users              │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Multi-tenant process co-location was      │
│ SOLVES       │ impossible without full VM overhead       │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Namespaces isolate VISIBILITY;            │
│              │ cgroups limit RESOURCES — containers need │
│              │ both. Namespaces ≠ VM security level.    │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Implementing containers; isolating test   │
│              │ processes; debugging with nsenter         │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Hostile multi-tenancy (use VMs/Firecracker│
│              │ for hard security boundaries)             │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Container isolation vs shared kernel;     │
│              │ minimal overhead vs no hardware boundary  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "AR glasses with different reality filters│
│              │ — everyone shares the same kernel room"   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ cgroups → seccomp → gVisor               │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A containerised application needs to run with PID 1 in its PID namespace. Explain the specific responsibility that PID 1 carries in any Linux PID namespace (hint: what happens to zombie processes?), why this causes problems when a shell script is used as the container entrypoint, and how `tini` or `dumb-init` solve this problem — citing the specific system calls involved.

**Q2.** A Kubernetes pod has three containers that must share a network namespace (so they can communicate via localhost) but must each have isolated filesystem namespaces. Describe the exact namespace configuration Kubernetes creates for this pod, explain the role of the "pause" (infra) container, and trace what happens to all three containers' namespaces when the pod is deleted — specifically addressing whether namespace cleanup is atomic or can result in a race condition.
