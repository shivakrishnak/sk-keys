---
layout: default
title: "Linux Namespaces"
parent: "Containers"
nav_order: 830
permalink: /containers/linux-namespaces/
number: "0830"
category: Containers
difficulty: ★★★
depends_on: Container, Operating Systems, Linux, Cgroups
used_by: Container, Docker, containerd, Container Security, Container Networking
related: Cgroups, Container, Container Security, Container Networking, containerd
tags:
  - containers
  - linux
  - internals
  - advanced
  - security
---

# 830 — Linux Namespaces

⚡ TL;DR — Linux namespaces are the kernel feature that makes containers possible — each namespace type wraps a global resource, giving a process its own private view of that resource.

| #830 | Category: Containers | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Container, Operating Systems, Linux, Cgroups | |
| **Used by:** | Container, Docker, containerd, Container Security, Container Networking | |
| **Related:** | Cgroups, Container, Container Security, Container Networking, containerd | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Two processes on the same Linux host cannot both think they have PID 1. They cannot both bind to port 80. They cannot both have a `/` root filesystem without seeing each other's files. They cannot both have a hostname `myapp`. All Linux resources — PIDs, network stack, filesystem tree, hostnames, users, IPC objects — are global to the kernel. Any process on the host shares them all.

**THE BREAKING POINT:**
Running multiple isolated applications on the same host requires per-application views of global kernel resources. Before namespaces, the only solution was a full Virtual Machine with its own kernel — heavyweight, slow, and expensive.

**THE INVENTION MOMENT:**
This is exactly why Linux namespaces were created — a kernel mechanism to virtualise global resources at the process level, giving each process (or group of processes) its own isolated view of PIDs, network, filesystem, users, and more.

---

### 📘 Textbook Definition

**Linux namespaces** are a kernel feature that partitions global system resources into independent instances — each namespace wraps a particular type of global resource and makes it appear to processes within the namespace that they have their own isolated copy of that resource. There are eight namespace types: **PID** (process IDs), **NET** (network stack), **MNT** (filesystem mount tree), **UTS** (hostname and domain name), **IPC** (inter-process communication), **USER** (user and group IDs), **Cgroup** (cgroup root), and **Time** (boot and monotonic clocks). A container is implemented by placing a process into a new set of namespaces at creation time using the `clone()` or `unshare()` syscall with appropriate flags.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A Linux namespace makes a process believe it has its own exclusive copy of PID space, network, filesystem, or other global resource — creating the illusion of isolation.

**One analogy:**
> Namespaces are like one-way mirrors in a hotel. Each room has what looks like a window to the outside — but it is actually a mirror. The guest in room 301 sees the same outside view as they would from any window, but they cannot see into other rooms. The hotel (kernel) manages one real outside (the actual hardware and resources). Each room (namespace) provides a private, isolated view. The guest cannot tell they are looking at a mirror, not a real window.

**One insight:**
Namespaces do NOT duplicate resources — they create isolated *views* of them. A PID namespace does not create new hardware or memory for each container. It creates a separate PID numbering space. PID 1 inside the container is just a different PID (e.g., 14825) from the host's perspective. The same process, two different identifiers — one per namespace layer.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Namespaces are created at process creation time with `clone()` flags or post-creation with `unshare()`.
2. Namespaces are reference-counted — they persist as long as at least one process lives inside them.
3. Namespaces are hierarchical for some types (PID, USER) — a parent namespace can see child namespace processes; the inverse is false.

**DERIVED DESIGN:**

**PID Namespace:**
Process IDs inside the namespace start at 1. `PID 1` is the container's init process. The same process has a different PID visible from the host (e.g., host PID 14825 = container PID 1). PID namespaces nest: the host can see all container PIDs; a container cannot see host PIDs.

**NET Namespace:**
Each NET namespace has its own network interfaces, routing table, iptables rules, socket table, and loopback interface. A container's `eth0` is a virtual ethernet (veth) pair whose other end is on the host's bridge (`docker0`). Ports are per-namespace — two containers can each bind to port 8080 independently.

**MNT Namespace:**
Each MNT namespace has its own mount table (list of filesystems and their mount points). A container starts with its image's root filesystem mounted into its own MNT namespace — it cannot see the host's `/etc/` or `/home/`. Bind mounts (`-v host:container`) create entries in the container's mount table pointing at host filesystem paths.

**UTS Namespace:**
Gives the container its own hostname. `gethostname()` inside the container returns the container's name, not the host's.

**USER Namespace:**
Maps container UIDs to host UIDs. UID 0 (root) inside the container maps to an unprivileged UID (e.g., 100000) on the host. This is what enables **rootless containers** — a container running as "root" inside is not root on the host; a namespace escape still lands you as an unprivileged user.

**THE TRADE-OFFS:**
**Gain:** Lightweight, kernel-native isolation; shared kernel (no hardware virtualisation overhead); millisecond container startup.
**Cost:** Shared kernel means a kernel vulnerability affects all containers; without USER namespaces, container root = host root (security risk); namespace configuration errors can break isolation.

---

### 🧪 Thought Experiment

**SETUP:**
Two containers, Container A and Container B, running on the same host. Both need to run a web server on port 80.

**WHAT HAPPENS WITHOUT NETWORK NAMESPACES:**
Both containers share the host's network stack. Container A binds to port 80 (`bind(80)`). Container B attempts to bind to port 80 → `EADDRINUSE`. Only one can run at a time. The other must use a different port. Network configuration is shared globally.

**WHAT HAPPENS WITH NETWORK NAMESPACES:**
Container A is created with a new NET namespace. It gets its own `eth0` with IP `172.17.0.2`. It binds to port 80 in its NET namespace — this binding is invisible to all other namespaces.

Container B is created with a different NET namespace. It gets `eth0` with IP `172.17.0.3`. It binds to port 80 in its NET namespace — also invisible to Container A's namespace.

Host port mapping: iptables DNAT rules map the host's port 8080 → Container A's 172.17.0.2:80, and host's port 8081 → Container B's 172.17.0.3:80.

**THE INSIGHT:**
Each NET namespace is a complete, independent network stack. Multiple containers binding to the same port number is not a conflict at all — they are in completely separate networking universes.

---

### 🧠 Mental Model / Analogy

> Namespaces are like parallel universes for kernel resources. In physics' many-worlds interpretation, different outcomes coexist in separate universes that cannot interact directly. In Linux, different containers coexist in separate namespace universes. PID 1 exists in Container A's universe AND Container B's universe simultaneously — but they are completely different processes. The kernel is the observer that can see all universes (from the host, all container PIDs are visible at their real host PIDs).

**Mapping:**
- "Parallel universe" → namespace instance (one per namespace type per container)
- "PID 1 in each universe" → each container has a process at container-PID 1, but with different host-PIDs
- "Kernel as inter-universe observer" → host namespace sees all container processes at real PIDs

**Where this analogy breaks down:** Parallel universes don't interact; containers CAN be connected at the network level (via veth pairs and bridges) — they just can't see each other's raw kernel resources directly. The isolation is selective, not total.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Namespaces let the Linux kernel show a program its own private view of the computer's resources. The program sees "I own PID 1, port 80, and the whole `/` filesystem" — but it's just a carefully constructed illusion. Other programs have their own same-seeming private views. The kernel manages the real resources underneath.

**Level 2 — How to use it (junior developer):**
You don't manually create namespaces — Docker and Kubernetes do this for you when starting containers. Understanding namespaces helps you debug: `docker exec -it container bash` enters the container's namespaces, so `ps aux` inside shows only the container's processes (PID namespace), `ip addr` shows only container networking (NET namespace), and `hostname` shows the container's hostname (UTS namespace).

**Level 3 — How it works (mid-level engineer):**
Daemon creates container using runc → runc calls `clone(CLONE_NEWPID | CLONE_NEWNET | CLONE_NEWNS | CLONE_NEWUTS | CLONE_NEWIPC | CLONE_NEWUSER)`. The new process starts in all new, empty namespaces. runc then sets up namespace contents: mounts the container image to the MNT namespace, creates a veth pair for the NET namespace, assigns hostname to UTS namespace, writes UID/GID mapping for USER namespace.

`nsenter` allows entering a container's namespaces: `nsenter -t $(docker inspect -f '{{.State.Pid}}' container) --pid --net --mnt bash` — this enters the container's PID, NET, and MNT namespaces, giving you the container's view while running with a different shell process.

**Level 4 — Why it was designed this way (senior/staff):**
PID namespaces (2008), NET namespaces (2009), MNT namespaces (2002), USER namespaces (2013) — they were added incrementally over a decade. This incremental addition is why they are not a single "isolation syscall" but a collection of `CLONE_NEW*` flags. USER namespace was the last to be stable because it is the most security-sensitive: allowing unprivileged users to create fully isolated environments with their own root is powerful but was historically exploitable for privilege escalation. Even today, USER namespaces are restricted by `kernel.unprivileged_userns_clone` sysctl on some distributions. The design trade-off that remains: namespace isolation does not include time (CPU scheduling) — two containers can starve each other on CPU unless cgroups enforce CPU limits. Namespaces provide visibility isolation; cgroups provide resource isolation. Both are required for a secure container.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────────┐
│  LINUX NAMESPACE TYPES                                   │
│                                                          │
│  PID Namespace:                                          │
│  Host:  [PID 1=init] [PID 14825=container_proc]         │
│  Cntr:  [PID 1=container_proc] ← same process, new ID   │
│                                                          │
│  NET Namespace:                                          │
│  Host:  eth0(192.168.1.100), lo, docker0(172.17.0.1)   │
│  Cntr:  eth0(172.17.0.2), lo  ← own stack, own IPs     │
│                                                          │
│  MNT Namespace:                                          │
│  Host:  / → sda1; /home → sdb1                         │
│  Cntr:  / → OverlayFS(image layers) ← own mountpoints  │
│                                                          │
│  UTS Namespace:                                          │
│  Host:  hostname = "prod-server-01"                     │
│  Cntr:  hostname = "webapp-pod-abc12" ← own hostname    │
│                                                          │
│  USER Namespace (rootless containers):                  │
│  Cntr:  UID 0 (root inside) → Host: UID 100000         │
│  ← container root is unprivileged on host              │
└──────────────────────────────────────────────────────────┘
```

**Container creation syscall:**
```c
// runc creates container process with all new namespaces
int pid = clone(container_entrypoint,
                stack_top,
                CLONE_NEWPID  |  // new PID namespace
                CLONE_NEWNET  |  // new network namespace
                CLONE_NEWNS   |  // new mount namespace
                CLONE_NEWUTS  |  // new hostname namespace
                CLONE_NEWIPC  |  // new IPC namespace
                CLONE_NEWUSER |  // new user namespace
                SIGCHLD,
                NULL);
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
docker run nginx → containerd → runc
→ [clone() with namespace flags ← YOU ARE HERE]
→ New process starts, in new namespaces
→ OverlayFS set up in MNT namespace
→ veth pair created for NET namespace
→ cgroups applied for resource limits
→ container appears as isolated environment
```

**FAILURE PATH:**
```
Container escapes namespace isolation (exploit)
→ process gains access to host PID or NET namespace
→ host kernel resources visible/modifiable
→ observable: unexpected host PIDs visible from container
→ detection: seccomp/AppArmor violations in audit log
```

**WHAT CHANGES AT SCALE:**
At 1,000 containers per host, the kernel namespace table grows correspondingly. Each NET namespace has its own iptables rules, routing table, and resource allocations. High container density on a single host can cause: iptables rule complexity (thousands of NAT rules for port mappings), veth pair limit issues, and namespace file descriptor limits. Kubernetes avoids concentrating too many containers per node via resource-based scheduling.

---

### 💻 Code Example

Example 1 — Inspect running container namespaces:
```bash
# Get the container's PID on the host
CONTAINER_PID=$(docker inspect -f '{{.State.Pid}}' my-container)
echo "Container root PID on host: $CONTAINER_PID"

# View all namespaces for the container process
ls -la /proc/$CONTAINER_PID/ns/
# net -> /proc/14825/ns/net  (unique inode = own NET namespace)
# pid -> /proc/14825/ns/pid  (unique inode = own PID namespace)
# mnt -> /proc/14825/ns/mnt  (unique inode = own MNT namespace)

# Compare to host's namespaces
ls -la /proc/1/ns/
# Different inodes = different namespaces (isolated)
```

Example 2 — Enter container namespaces directly (nsenter):
```bash
# Enter container's namespaces as root (bypasses container user)
nsenter -t $(docker inspect -f '{{.State.Pid}}' my-container) \
        --pid --net --mnt -- bash

# Inside this shell:
ps aux     # → sees only container processes (PID NS)
ip addr    # → sees only container network (NET NS)
ls /       # → sees container filesystem (MNT NS)
# But you are in these namespaces with the original shell binary
```

Example 3 — Check if namespaces are properly isolated:
```bash
# From container: verify cannot see host processes
docker exec my-container ps aux | wc -l
# Should be small (only container processes)

# From host: verify can see container process
ps aux | grep -v grep | grep nginx
# Shows nginx with full host PID
```

---

### ⚖️ Comparison Table

| Namespace Type | Isolates | Added (Linux) | Key Use Case |
|---|---|---|---|
| PID | Process IDs | 3.8 (2008) | Independent process trees |
| NET | Network interfaces, ports | 2.6.24 (2009) | Multiple containers on same port |
| MNT | Filesystem mount tree | 2.4.19 (2002) | Container's own root filesystem |
| UTS | Hostname, domain name | 2.6.19 (2006) | Container's own hostname |
| IPC | Message queues, semaphores | 2.6.19 (2006) | IPC isolation |
| USER | User/group IDs | 3.8 (2013) | Rootless containers |
| Cgroup | Cgroup root view | 4.6 (2016) | Cgroup isolation |
| Time | Boot/monotonic clocks | 5.6 (2020) | Per-container time (rare) |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Namespaces consume significant resources | Namespaces are lightweight kernel data structures — a namespace costs kilobytes, not megabytes |
| Root inside a container equals root on the host | Without USER namespaces, yes (dangerous). With USER namespaces mapped to unprivileged host UID, no. |
| Namespaces provide complete isolation | Namespaces isolate VISIBILITY of resources. They do NOT limit resource CONSUMPTION (that is cgroups' job). A container without cgroup limits can exhaust all host CPU/memory. |
| All container runtimes use the same namespaces | Docker default: PID, NET, MNT, UTS, IPC namespaces isolated; USER optionally. Running `docker run --pid=host` removes PID isolation. Always verify namespace flags for custom runtimes. |
| Namespace isolation is sufficient for multi-tenant security | For untrusted workloads, namespaces + cgroups are insufficient — you also need seccomp profiles, AppArmor/SELinux, and ideally kernel isolation (MicroVMs). |

---

### 🚨 Failure Modes & Diagnosis

**Container Sees Host Processes**

**Symptom:** Inside a container, `ps aux` shows all host processes, not just container processes.

**Root Cause:** Container was started with `--pid=host` (shares host PID namespace) or PID namespace isolation was accidentally disabled.

**Diagnostic Command / Tool:**
```bash
# Check which namespaces are shared with host
docker inspect my-container \
  | jq '.[0].HostConfig.PidMode'
# "host" → PID namespace sharing is enabled (dangerous)

# Compare namespace inodes
ls -la /proc/$(docker inspect -f '{{.State.Pid}}' my-container)/ns/pid
ls -la /proc/1/ns/pid
# If same inode → PID namespace shared with host
```

**Fix:** Remove `--pid=host` flag. Restart container without shared host namespace.

**Prevention:** Add OPA/Kyverno policy in Kubernetes: deny pods with `hostPID: true` unless explicitly allowlisted.

---

**Privileged Container Bypasses All Namespaces**

**Symptom:** A `docker run --privileged` container can mount host filesystems, load kernel modules, and directly access host devices.

**Root Cause:** `--privileged` flag disables all namespace isolation AND grants all Linux capabilities — the container is essentially root on the host.

**Diagnostic Command / Tool:**
```bash
# Check if container is privileged
docker inspect my-container | jq '.[0].HostConfig.Privileged'
# true → all namespace isolation is bypassed

# Inside privileged container
mount /dev/sda1 /mnt/host  # Works! Can access host disk
```

**Fix:** Never use `--privileged` in production. Identify the specific capability needed (e.g., `NET_ADMIN`, `SYS_PTRACE`) and grant only that.

**Prevention:** Kubernetes Pod Security Standards (Restricted profile) blocks `privileged: true`. Enable in Kubernetes with `pod-security.kubernetes.io/enforce: restricted` namespace label.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Container` — namespaces are the mechanism that implements containers
- `Operating Systems` — understanding process isolation requires OS fundamentals

**Builds On This (learn these next):**
- `Cgroups` — resource limits (the other half of container isolation alongside namespaces)
- `Container Security` — how namespace misconfigurations create security vulnerabilities

**Alternatives / Comparisons:**
- `Hypervisor/VM` — alternative isolation mechanism using hardware virtualisation (stronger but heavier)
- `MicroVM (Firecracker)` — lightweight KVM VM for stronger isolation than namespaces alone

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Kernel mechanism giving processes private │
│              │ views of PID, NET, FS, hostname, users   │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ All Linux resources are global; multiple │
│ SOLVES       │ isolated apps cannot coexist without it  │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Namespaces isolate VISIBILITY, not usage.│
│              │ Cgroups are needed for resource limits   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always (Docker uses them automatically); │
│              │ check flags — --pid=host disables PID NS │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ --privileged, --pid=host, --net=host:    │
│              │ these remove namespace isolation         │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Lightweight kernel isolation vs shared   │
│              │ kernel attack surface vs full VM         │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "One-way mirrors for kernel resources —  │
│              │  each container sees only its own view"  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Cgroups → Container Security →           │
│              │ Container Networking                     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** The Linux `USER` namespace allows an unprivileged user on the host to create a container where they are "root" (UID 0 inside). This mapping of container UID 0 to host UID 100000 is the basis of rootless containers. Describe the exact attack scenario where a namespace escape from a rootless container (with correct USER namespace mapping) is less dangerous than an escape from a root-privilege container runtime (without USER namespace mapping). What specifically does the attacker land with in each case after the escape?

**Q2.** A security team member proposes that because containers use Linux namespaces and cgroups, they are "just as secure as VMs for multi-tenant hosting." Construct a detailed counter-argument identifying: (1) which specific kernel attack surface is shared between all containers on a host that is NOT shared between VMs, (2) what class of exploit can break namespace isolation, and (3) what architecture would you need to deploy untrusted third-party code safely using containers.

