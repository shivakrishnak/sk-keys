---
layout: default
title: "Linux Namespaces"
parent: "Containers"
nav_order: 830
permalink: /containers/linux-namespaces/
number: "830"
category: Containers
difficulty: ★★★
depends_on: "Container, Docker"
used_by: "cgroups, Docker Image, Kubernetes"
tags: #containers, #linux, #namespaces, #isolation, #kernel, #pid-namespace
---

# 830 — Linux Namespaces

`#containers` `#linux` `#namespaces` `#isolation` `#kernel` `#pid-namespace`

⚡ TL;DR — **Linux namespaces** are the kernel mechanism that makes containers possible. A namespace wraps a global system resource so that processes inside the namespace see only their own isolated instance. Docker creates a new set of namespaces (PID, Network, Mount, UTS, IPC, User) per container — that's why the container "thinks" it's alone on the machine. Namespaces ≠ isolation from resource exhaustion (that's cgroups). Namespaces = isolation of identity and visibility.

| #830            | Category: Containers              | Difficulty: ★★★ |
| :-------------- | :-------------------------------- | :-------------- |
| **Depends on:** | Container, Docker                 |                 |
| **Used by:**    | cgroups, Docker Image, Kubernetes |                 |

---

### 📘 Textbook Definition

**Linux namespaces**: a kernel feature (Linux 3.8+, with types added incrementally since 2.4) that partitions kernel resources such that processes in one namespace see a different set of resources than processes in another. Namespace types: **PID** (process IDs — container's PID 1 is the daemon; host sees it as PID 12345); **Network** (eth0, routing tables, iptables rules, port bindings — each container has its own network stack); **Mount** (`/proc/mounts` — container sees only its own mount points; different view of the filesystem); **UTS** (hostname and domain name — container can have a different hostname); **IPC** (System V IPC, POSIX message queues — isolated IPC resources); **User** (UID/GID mapping — container's root (UID 0) maps to an unprivileged host UID); **Cgroup** (view of the cgroup hierarchy); **Time** (per-namespace `clock_realtime` and `clock_monotonic`, Linux 5.6+). Syscalls: `clone(CLONE_NEWPID | CLONE_NEWNET | ...)` creates a new namespace and places the child process in it; `unshare()` dissociates from namespaces; `setns()` joins an existing namespace (how `docker exec` works). Namespaces are represented as files: `/proc/<pid>/ns/<type>` — holding a file descriptor open keeps the namespace alive even if all processes exit.

---

### 🟢 Simple Definition (Easy)

When you run a Docker container, Docker asks the Linux kernel: "give this process a new PID namespace" → the container's process starts as PID 1 (even though the host sees it as PID 12345). Docker also gives it a new network namespace → the container has its own `eth0`, its own IP address. New mount namespace → the container sees its own filesystem (Ubuntu base image), not the host's filesystem. This is all implemented in the Linux kernel — Docker is just a tool that calls kernel APIs to set up these namespaces. Containers are essentially processes with kernel-enforced "tunnel vision."

---

### 🔵 Simple Definition (Elaborated)

Namespaces answer "what can this process SEE?" (visibility isolation):

- **PID namespace**: the container process can't see or signal host processes; can't `kill` the host's nginx
- **Network namespace**: the container has its own network stack; port 80 in the container doesn't conflict with port 80 on the host or in another container
- **Mount namespace**: the container sees a different root filesystem; `ls /` shows the container's OS, not the host's
- **UTS namespace**: `hostname` inside the container returns the container name, not the host's hostname
- **User namespace**: container's root (UID 0) maps to UID 100000 on the host — the container "thinks" it's root but is actually unprivileged on the host (rootless containers)

Namespaces do NOT limit CPU/memory usage — that's **cgroups**. Namespaces + cgroups together = container isolation.

---

### 🔩 First Principles Explanation

{% raw %}
```
NAMESPACE TYPES DEEP DIVE:

1. PID NAMESPACE:
   Without PID namespace: all processes see all PIDs → container could kill host's sshd
   With PID namespace: container has its own PID tree; PID 1 = container's init process

   Host view:    PID 1 (init/systemd) → PID 12345 (container's bash)
   Container view: PID 1 (bash)

   Nested PID namespaces: container can create child PID namespaces
   (Kubernetes: each pod container shares the pod's PID namespace; optional)

   /proc filesystem: kernel shows each PID namespace its own /proc/<pids>

2. NETWORK NAMESPACE:
   Each container gets: separate eth0, lo, iptables, routing table, port bindings

   Host: eth0 (192.168.1.100), docker0 bridge (172.17.0.1)
   Container1: eth0 (172.17.0.2), lo
   Container2: eth0 (172.17.0.3), lo

   Port binding: container listens on :80 within its network namespace
   Docker: creates veth pair (virtual Ethernet cable):
     veth0 (container end, named eth0 in container)
     veth1234 (host end, attached to docker0 bridge)
   docker run -p 8080:80: iptables DNAT rule: host:8080 → container:80

   Network namespaces for pods (Kubernetes):
   All containers in a pod SHARE the same network namespace
   → Same IP, same ports (can't both listen on :80)
   → Communicate via localhost
   The "pause" container holds the network namespace; app containers join it

3. MOUNT NAMESPACE:
   Each container gets its own mount table (view of filesystems)
   Container's root filesystem: overlay filesystem (UnionFS/OverlayFS)

   Lower layers (read-only): Docker image layers (inherited from image)
   Upper layer (read-write): container's writable layer (lost on container stop)

   pivot_root() or chroot(): changes the container's root directory to the image root

   /proc mount in container: separate /proc mounted per PID namespace

4. UTS NAMESPACE (Unix Time-sharing System):
   Isolates hostname and domainname
   docker run --hostname mycontainer ubuntu hostname → "mycontainer"
   Host hostname unchanged
   (Historically for multi-tenant Unix time-sharing systems)

5. IPC NAMESPACE:
   Isolates: System V shared memory (shmget), semaphores, message queues
   POSIX shared memory (/dev/shm)
   → Container can't attach to host's shared memory segments

   Kubernetes pods: containers in a pod share IPC namespace
   → They can communicate via POSIX shared memory

6. USER NAMESPACE (rootless containers):
   Maps UIDs/GIDs between namespace and host

   Container: UID 0 (root)  → Host: UID 100000 (unprivileged)
   Container: UID 1000      → Host: UID 101000

   /etc/subuid: defines the mapping range

   Benefits:
   - Container root can't affect host files owned by real root
   - Process escaping container namespace → unprivileged on host
   - No setuid/capabilities escalation to real root

   Docker: rootless mode uses user namespaces (default in Podman)
   Docker Desktop: user namespaces handled by Linux VM

7. CGROUP NAMESPACE:
   Container sees only its own cgroup tree (not the host's full cgroup hierarchy)
   Prevents container from seeing resource limits of other containers

SYSCALLS:

  clone(2):   create new process + new namespace(s)
  unshare(2): detach current process from namespace(s)
  setns(2):   join an existing namespace (by fd from /proc/<pid>/ns/<type>)

  # docker exec implementation:
  # /proc/<container-PID>/ns/pid  → open fd
  # setns(fd, CLONE_NEWPID)       → join container's PID namespace
  # setns(net_fd, CLONE_NEWNET)   → join container's network namespace
  # exec("bash")                  → start bash in container's namespaces

  # Namespace persistence (even with no processes):
  # bind mount /proc/<pid>/ns/net to /run/netns/mynet
  # → network namespace persists for later use (ip netns attach)

DEMONSTRATION:

  # Create a new network namespace manually:
  sudo ip netns add myns

  # Run a command in the namespace:
  sudo ip netns exec myns ip link show   # shows only lo

  # Create veth pair and attach one end to namespace:
  sudo ip link add veth0 type veth peer name veth1
  sudo ip link set veth1 netns myns

  # This is essentially what Docker does for every container

  # Check container's namespaces:
  CONTAINER_PID=$(docker inspect --format '{{.State.Pid}}' mycontainer)
  ls -la /proc/$CONTAINER_PID/ns/
  # net -> net:[4026532198]   ← unique namespace inode
  # pid -> pid:[4026532201]
  # mnt -> mnt:[4026532199]

  # Enter container's network namespace:
  sudo nsenter -t $CONTAINER_PID --net ip addr
```
{% endraw %}

---

### ❓ Why Does This Exist (Why Before What)

Before namespaces, process isolation required either: (1) separate physical machines (expensive), (2) virtual machines (heavy: full OS per VM, minutes to boot, GB RAM overhead), or (3) chroot (filesystem isolation only, not network/PID). Namespaces provide lightweight isolation at the process level — no full OS, no hardware virtualization, near-zero overhead. The Linux kernel already manages these global resources (PIDs, network stacks, mounts); namespaces are virtualizations of these existing kernel data structures. Result: containers start in milliseconds, use ~10MB overhead (vs ~200MB for a VM), and can run thousands per host.

---

### 🧠 Mental Model / Analogy

> **Namespaces are like one-way mirrors in an apartment building**: each tenant (container) sees only their own apartment (their own PID space, network, filesystem). They can't see into other apartments. But the building manager (host OS kernel) can see into all apartments through the one-way mirror — the host can `ps aux` and see all container processes, `nsenter` to join any namespace, or `docker exec` to enter a container. The tenants don't see the building structure; they think they're in a standalone house. The mirrors (namespaces) create the illusion of isolation without building separate physical buildings (VMs).

---

### ⚙️ How It Works (Mechanism)

```
DOCKER CONTAINER CREATION SEQUENCE:

  docker run ubuntu bash

  1. Docker daemon: clone(CLONE_NEWPID|CLONE_NEWNET|CLONE_NEWNS|CLONE_NEWUTS|CLONE_NEWIPC)
     → new process + new namespaces created

  2. PID namespace: child process is PID 1 in new namespace

  3. Network namespace setup:
     - Create veth pair (veth0 <-> veth12345abc)
     - Move veth0 into container's network namespace (rename to eth0)
     - Attach veth12345abc to docker0 bridge on host
     - Configure IP via DHCP or subnet allocation (172.17.0.x)

  4. Mount namespace setup:
     - Create overlay filesystem: lower=image_layers, upper=new_rw_layer
     - pivot_root into overlay mount
     - Mount /proc, /sys, /dev in the new mount namespace

  5. UTS namespace: set hostname to container ID

  6. cgroup assignment: add PID to container's cgroup (CPU/memory limits)
     (cgroups = separate kernel mechanism from namespaces)

  7. exec("bash"): replace clone child with bash
     → bash runs with new namespaces
     → bash PID is 1 inside the PID namespace

  Teardown (docker stop):
  1. Send SIGTERM to PID 1 in container
  2. Wait grace period (10s default)
  3. SIGKILL if still running
  4. Remove network namespace: delete veth pair, release IP
  5. Remove cgroup
  6. Remove writable overlay layer (container data lost)
```

---

### 🔄 How It Connects (Mini-Map)

```
Need process isolation without full VMs
        │
        ▼
Linux Namespaces ◄── (you are here)
(kernel-level resource partitioning per process)
        │
        ├── Container: a container IS a process with its own set of namespaces
        ├── Docker: tool that calls clone()/setns() to set up namespaces
        ├── cgroups: limits CPU/memory (resource usage); namespaces limit visibility
        ├── OverlayFS: provides isolated filesystem view within mount namespace
        └── Kubernetes: each pod has its own network namespace; containers share it
```

---

### 💻 Code Example

{% raw %}
```bash
# Exploring namespaces with nsenter and unshare (no Docker needed)

# Create an isolated PID + mount + network namespace:
sudo unshare --pid --fork --mount-proc --net bash
# Inside: this bash is PID 1
# ps aux: only shows this bash process
# ip link: only lo (isolated network namespace)
# exit: namespace destroyed

# Explore a running container's namespaces:
CONTAINER_ID=$(docker run -d nginx)
CONTAINER_PID=$(docker inspect --format '{{.State.Pid}}' $CONTAINER_ID)

# See namespace inode numbers:
sudo ls -la /proc/$CONTAINER_PID/ns/

# Enter the container's network namespace (without docker exec):
sudo nsenter -t $CONTAINER_PID --net ip addr
# Shows container's network interfaces (eth0 with its IP)

# Enter ALL namespaces (equivalent to docker exec):
sudo nsenter -t $CONTAINER_PID --all bash

# Demonstrate network namespace isolation:
# On host:
ss -tlnp | grep :80     # nothing (nginx is in container's namespace)

# In container's network namespace:
sudo nsenter -t $CONTAINER_PID --net ss -tlnp
# Shows nginx listening on :80 in the container's network namespace
```
{% endraw %}

---

### ⚠️ Common Misconceptions

| Misconception                                           | Reality                                                                                                                                                                                                                                                                                                                              |
| ------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Namespaces are the same as cgroups                      | Namespaces isolate VISIBILITY (what a process can see: PIDs, network, filesystem). Cgroups limit USAGE (how much CPU/memory a process can consume). Both are needed for container isolation: namespaces prevent a container from seeing other containers' resources; cgroups prevent a container from starving others of CPU/memory. |
| Containers are completely isolated from the host kernel | Containers share the host kernel. A kernel panic caused by a container bug affects the entire host. Kernel exploits (Dirty COW, runc CVEs) in one container can escape to the host. True isolation requires VMs. Container security relies on kernel correctness + seccomp + AppArmor/SELinux to filter dangerous syscalls.          |
| Namespaces are unique to Docker                         | Namespaces are a Linux kernel feature (since ~2002). Docker uses them but you can use them directly with `unshare`, `nsenter`, `ip netns`. Podman, LXC, systemd-nspawn all use Linux namespaces. FreeBSD has Jails (similar concept, different implementation).                                                                      |

---

### 🔥 Pitfalls in Production

```
PITFALL: container escape via privileged mode

  docker run --privileged myapp   ← DANGEROUS: disables namespace isolation
  # --privileged:
  # - mounts host /dev with full device access
  # - grants all Linux capabilities (including SYS_ADMIN, NET_ADMIN)
  # - can mount host filesystem, modify iptables, load kernel modules
  # - a compromised container process = full host compromise

  # FIX: never use --privileged in production
  # Grant specific capabilities only:
  docker run --cap-add NET_ADMIN --cap-drop ALL myapp

  # Or use seccomp + AppArmor profiles to filter syscalls:
  docker run --security-opt seccomp=/etc/docker/seccomp.json myapp

PITFALL: PID 1 problem (SIGTERM not forwarded)

  # Container starts shell script → shell starts java → java is PID 2
  # docker stop sends SIGTERM to PID 1 (the shell)
  # Shell: receives SIGTERM → exits → java gets SIGKILL immediately
  # Java: no graceful shutdown → potential data corruption / connection leak

  # FIX: use exec form in Dockerfile (java becomes PID 1):
  # ❌ CMD ["sh", "-c", "java -jar app.jar"]   ← shell is PID 1
  # ✅ CMD ["java", "-jar", "app.jar"]         ← java is PID 1

  # Or use tini as PID 1 (proper init: forwards signals, reaps zombies):
  ENTRYPOINT ["/usr/bin/tini", "--"]
  CMD ["java", "-jar", "app.jar"]
```

---

### 🔗 Related Keywords

- `Container` — a process with Linux namespaces; namespaces are the implementation mechanism
- `Docker` — tool that calls kernel namespace APIs on your behalf
- `cgroups` — complements namespaces: limits resource USAGE (CPU/memory)
- `OverlayFS` — provides the container's isolated filesystem view within the mount namespace
- `Kubernetes` — pods use network namespaces (shared per pod); each pod has isolated network

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ NAMESPACE TYPES:                                         │
│ PID   → process isolation (container's PID 1)          │
│ NET   → own network stack (eth0, ports, routing)       │
│ MNT   → own filesystem view (OverlayFS root)           │
│ UTS   → own hostname                                    │
│ IPC   → own IPC resources (shared memory, semaphores)  │
│ USER  → UID/GID remapping (rootless containers)        │
│ CGRP  → own cgroup view                                │
├──────────────────────────────────────────────────────────┤
│ SYSCALLS: clone() create | setns() join | unshare() leave│
│ TOOLS: nsenter, unshare, ip netns, /proc/<pid>/ns/      │
│ INSPECT: ls -la /proc/<PID>/ns/                         │
│ Namespaces = visibility | cgroups = resource limits     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Container runtime security relies on namespace isolation, but namespaces are implemented in the kernel — a kernel bug can bypass them. The `runc` container runtime has had multiple CVEs (CVE-2019-5736, CVE-2021-30465) that allowed container escape to the host. Kubernetes response to these: gVisor (Google), Kata Containers (Intel), Firecracker (Amazon). These use VM-based isolation (each pod runs in a lightweight VM) while maintaining a container-like API. Compare the security model and performance trade-offs between: (a) standard runc containers (namespace isolation), (b) gVisor (user-space kernel), (c) Kata Containers (full VM kernel). When would you choose each?

**Q2.** The PID namespace means a container's processes have PID 1 = the main process. In Linux, PID 1 has special responsibilities: it's the parent of all orphaned processes and is responsible for reaping zombie processes. If your container runs a Java app (PID 1) and that app spawns child processes that terminate — without proper init handling, those children become zombies (entries in the process table that can't be cleaned). How does `tini` solve this? How does Kubernetes handle this in pods? What happens to zombie processes if PID 1 doesn't call `waitpid()`?
