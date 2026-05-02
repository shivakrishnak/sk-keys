---
layout: default
title: "Container"
parent: "Containers"
nav_order: 821
permalink: /containers/container/
number: "0821"
category: Containers
difficulty: ★☆☆
depends_on: Linux Namespaces, Operating Systems, Virtualization
used_by: Docker, Docker Image, Container Orchestration, Kubernetes Architecture
related: Docker, Docker vs VM, Linux Namespaces, Cgroups, Container Runtime Interface (CRI)
tags:
  - containers
  - docker
  - linux
  - foundational
  - devops
---

# 821 — Container

⚡ TL;DR — A container is an isolated, portable process that packages an application with its dependencies and shares the host OS kernel — lighter than a VM but stronger than a bare process.

| #821 | Category: Containers | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Linux Namespaces, Operating Systems, Virtualization | |
| **Used by:** | Docker, Docker Image, Container Orchestration, Kubernetes Architecture | |
| **Related:** | Docker, Docker vs VM, Linux Namespaces, Cgroups, Container Runtime Interface (CRI) | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A developer writes an application that works perfectly on their laptop (Python 3.11, library version 2.3.1). They deploy it to a server running Python 3.8 and library version 1.9.0. The application crashes. A teammate then installs a conflicting library version for their application on the same server, breaking someone else's app. The sysadmin is called at 2 AM to untangle dependency conflicts. A new microservice needs to be deployed alongside 15 others — each with its own conflicting runtime requirements. Managing all of them on shared servers is a nightmare of version conflicts and invisible dependencies.

**THE BREAKING POINT:**
"It works on my machine" is not a delivery model. Applications need their complete dependency environment to be packaged and transported with them — without using the wasteful overhead of a full virtual machine for each application.

**THE INVENTION MOMENT:**
This is exactly why containers were created — a lightweight, portable unit that packages the application AND its complete runtime environment, isolating it from other processes on the same host using Linux kernel features (namespaces + cgroups), without needing a separate OS per application.

---

### 📘 Textbook Definition

A **container** is a standard unit of software that packages code and all its dependencies — runtime, system tools, system libraries, settings — so that the application runs quickly and reliably from one computing environment to another. Containers use Linux **namespaces** to provide process, network, filesystem, and user isolation, and **cgroups** to enforce resource limits (CPU, memory, I/O). Unlike virtual machines, containers share the host's OS kernel — they are isolated processes, not virtualised machines. This makes them orders of magnitude lighter in startup time (milliseconds), memory overhead (MBs vs GBs), and density (hundreds per host vs tens for VMs).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A container is a portable, isolated process that packages everything an application needs to run — shareable, lightweight, and consistently reproducible.

**One analogy:**
> A container is like a shipping container on a cargo ship. Before containerisation, every dock and ship had different loading systems — goods were loose cargo that had to be manually adapted. The ISO standard shipping container changed everything: any container fits any ship, any truck, any crane. The contents are isolated from each other. You can stack them, move them globally, ship them from factory to customer without unpacking. Software containers do exactly the same: a standard unit that runs on any container-capable host, exactly the same everywhere.

**One insight:**
The key innovation is **sharing the OS kernel** while maintaining **isolation**. A VM duplicates an entire OS for isolation — expensive. A bare process shares everything — no isolation. A container occupies the perfect middle ground: shared kernel, isolated everything-else (filesystem, network, processes, users).

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. A container is a regular Linux process — it has a PID, it runs on the host kernel.
2. Namespace isolation prevents the container from seeing other processes, networks, and filesystems on the host.
3. Cgroups enforce resource constraints — the container cannot take unlimited CPU/memory from the host.

**DERIVED DESIGN:**
The container is constructed by the Linux kernel from three primitives:

**Namespaces (isolation):**
- `PID` namespace: process sees only its own processes (PID 1 = the container's init)
- `NET` namespace: isolated network stack (its own IP, port space)
- `MNT` namespace: isolated filesystem mount tree
- `UTS` namespace: isolated hostname
- `IPC` namespace: isolated IPC (message queues, semaphores)
- `USER` namespace: isolated UID/GID mapping

**Control Groups / cgroups (limits):**
- Limits: `container.cpu.max = 0.5 cores`, `container.memory.limit = 512M`
- Prevents a single container from consuming all host resources

**Union Filesystem / OverlayFS:**
- Container reads a layered filesystem (base OS image + app layers)
- Writes go to a per-container writable layer (ephemeral by default)

**THE TRADE-OFFS:**
**Gain:** Fast startup (ms); low overhead; portable; reproducible; high density on host.
**Cost:** Shares host kernel — a kernel vulnerability affects all containers; weaker isolation than VMs; root inside container = not truly unprivileged without user namespaces.

---

### 🧪 Thought Experiment

**SETUP:**
Two processes run on the same Linux host. Process A runs a web server on port 8080. Process B also tries to bind to port 8080.

**WHAT HAPPENS WITHOUT CONTAINERS:**
Both processes share the network namespace. Port 8080 is already bound by Process A. Process B receives `EADDRINUSE`. Both cannot run simultaneously without one changing its port.

**WHAT HAPPENS WITH CONTAINERS:**
Process A runs in Container A with its own `NET` namespace — port 8080 inside Container A is invisible to Container B's namespace. Process B in Container B also binds to port 8080 in ITS own network namespace. No conflict occurs. Both run simultaneously on the same host. The host maps Container A's port 8080 to host port 8080, and Container B's port 8080 to host port 8081 — the containers are unaware of this external mapping.

**THE INSIGHT:**
Namespace isolation means every container has a completely private view of the system resources it uses. Two containers can think they "own" PID 1, port 8080, and the root filesystem simultaneously. This illusion is constructed by the kernel, not by copying anything.

---

### 🧠 Mental Model / Analogy

> A container is like a private office in a shared co-working building. Each office (container) has its own desk, computer, and key-coded door (namespace isolation). The building's heating, electricity, and internet connection are shared infrastructure (host OS kernel). An occupant cannot wander into another office or steal their power outlet. But if the building's electricity fails (kernel vulnerability), everyone is affected. Compared to buying a separate house for each person (VM), this is far more efficient — same isolation per person, vastly lower cost.

**Mapping:**
- "Co-working building" → host machine with Linux kernel
- "Private office" → container (namespaced process)
- "Building's electricity/internet" → shared OS kernel
- "Key-coded door" → namespace boundary (other processes cannot enter)
- "Occupant's dedicated desk/computer" → container's isolated filesystem + PID space
- "Buying a separate house" → running a full VM for each process

**Where this analogy breaks down:** Offices in buildings can leave their doors open deliberately; containers can also be misconfigured to share namespaces — `--pid=host` or `--network=host` modes remove isolation, just as leaving an office door open removes privacy.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A container is a self-contained box for an application. It includes the app and everything it needs to run. You can move the box to any computer and the app will work exactly the same — because it carries its own environment.

**Level 2 — How to use it (junior developer):**
You run a container with `docker run nginx` — Docker downloads the Nginx image and starts an isolated container. The container has its own network and filesystem. You expose it on a port (`-p 8080:80`) so external traffic reaches it. When you stop the container, it disappears. Persistent data must be stored in volumes (`-v /host/path:/container/path`) to survive container restarts.

**Level 3 — How it works (mid-level engineer):**
When `docker run` starts a container: (1) the container runtime (containerd) calls the OCI runtime runc to create a new process; (2) runc calls Linux's `clone()` syscall with the namespace flags (`CLONE_NEWPID | CLONE_NEWNET | CLONE_NEWNS | ...`); (3) the new process starts in its own isolated namespace; (4) cgroup rules are applied to limit CPU/memory; (5) OverlayFS mounts the image layers as the process's root filesystem; (6) the entrypoint command (`nginx -g "daemon off;"`) is exec'd inside this isolated process.

**Level 4 — Why it was designed this way (senior/staff):**
Containers emerged from the Linux kernel's namespace and cgroup features that were added incrementally from 2002 (namespaces) to 2007 (cgroups). Google ran containers internally (Borg) for years before public container tooling existed. Docker (2013) made this accessible by standardising image format and adding a user-friendly CLI. The OCI (Open Container Initiative) standardised the runtime and image specifications in 2015, preventing Docker from monopolising the ecosystem. The tension containers solved: VMs are slow and wasteful for microservices deployments (30-second boot time, 1 GB overhead per app); bare processes have no isolation and suffer from dependency hell. Containers nail the sweet spot.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────────┐
│  HOST MACHINE (Linux Kernel)                             │
│                                                          │
│  ┌─────────────────────┐  ┌─────────────────────┐       │
│  │  CONTAINER A        │  │  CONTAINER B        │       │
│  │  PID namespace: {1} │  │  PID namespace: {1} │       │
│  │  NET namespace: eth0│  │  NET namespace: eth0│       │
│  │  MNT: / (overlay)   │  │  MNT: / (overlay)   │       │
│  │  cgroup: 0.5 CPU    │  │  cgroup: 0.5 CPU    │       │
│  │  cgroup: 512M RAM   │  │  cgroup: 512M RAM   │       │
│  └─────────────────────┘  └─────────────────────┘       │
│                                                          │
│  Shared: Linux Kernel, hardware drivers, host network   │
└──────────────────────────────────────────────────────────┘

OverlayFS layering:
  Base image layer (nginx:1.25) ──┐
  App layer (conf + html)         ├──► Merged view (container
  Writable layer (ephemeral)   ───┘     sees as single /)
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Developer builds image → pushes to registry
→ Orchestrator (Kubernetes) schedules container
→ kubelet asks containerd to start container
→ containerd calls runc → [CONTAINER starts ← YOU ARE HERE]
→ container serves traffic → liveness probe checked
→ application runs until stopped/crashed
```

**FAILURE PATH:**
```
Container process exits (crash or OOM kill)
→ restart policy triggers → container restarted (new PID)
→ ephemeral filesystem state is lost
→ observable: docker ps shows Restart count > 0
→ persistent data in volumes survives
```

**WHAT CHANGES AT SCALE:**
At hundreds of containers per host, the bottleneck shifts to: kernel namespace table limits (hard limit ~65K PIDs), cgroup overhead for fine-grained limits, and OverlayFS I/O contention when many containers write simultaneously. Container density best practices: limit to 10–30 containers per host core; use volume mounts for write-heavy workloads to avoid OverlayFS overhead.

---

### 💻 Code Example

Example 1 — Run a basic container:
```bash
# Run an nginx container, expose port 8080 on host → 80 in container
docker run -d \
  --name my-nginx \
  -p 8080:80 \
  --memory="512m" \
  --cpus="0.5" \
  nginx:1.25
# -d: detached (background)
# --memory: cgroup memory limit
# --cpus: cgroup CPU limit
```

Example 2 — Inspect container isolation:
```bash
# See the container's isolated process tree
docker exec my-nginx ps aux
# PID 1 = nginx master (container sees only its own PIDs)

# See the container's isolated network
docker exec my-nginx ip addr
# Shows container's own eth0 with private IP (e.g. 172.17.0.2)

# Verify cgroup limits applied
cat /sys/fs/cgroup/memory/docker/$(docker inspect -f '{{.Id}}' my-nginx)/memory.limit_in_bytes
# Output: 536870912 (512 MB in bytes)
```

Example 3 — Run with volume mount (persistent data):
```bash
docker run -d \
  --name my-db \
  -v /host/data/postgres:/var/lib/postgresql/data \
  -e POSTGRES_PASSWORD=secret \
  postgres:16
# /var/lib/postgresql/data in container maps to /host/data/postgres
# Data persists across container restarts and replacements
```

---

### ⚖️ Comparison Table

| Unit | Isolation | Startup | Overhead | Portability | Kernel |
|---|---|---|---|---|---|
| **Container** | Namespace + cgroup | Milliseconds | MBs | High | Shared |
| VM | Full hypervisor | 30–60 seconds | GBs | Medium | Dedicated |
| Bare Process | None | Milliseconds | None | Low | Shared |
| MicroVM (Firecracker) | KVM (lightweight) | ~125 ms | ~5 MB | High | Dedicated |

**How to choose:** Use containers for the vast majority of application workloads — they are the right balance of isolation, portability, and efficiency. Use VMs when you need kernel-level isolation (untrusted multi-tenant workloads) or Windows + Linux on the same host. Use Firecracker MicroVMs when you need near-VM isolation with near-container overhead (AWS Lambda uses this).

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Containers are VMs | Containers share the host kernel; VMs have their own kernel. Containers are isolated processes, not virtualised machines. |
| Root inside a container equals root outside | With user namespaces, root inside a container maps to an unprivileged user outside. Without user namespaces (common default), root inside is effectively root on the host if container escapes occur. |
| Containers are always stateless | Containers can have persistent state via volume mounts. The container process is ephemeral; mounted volumes are not. |
| Containers solve all dependency problems | Containers package user-space dependencies but share the host kernel — kernel version-dependent syscalls can still break across hosts. |
| Containers are always secure | Default Docker configurations have significant security gaps (root by default, capabilities not constrained). Securing containers requires additional hardening. |

---

### 🚨 Failure Modes & Diagnosis

**OOM Kill (Out of Memory)**

**Symptom:** Container exits with exit code 137; application crashes without error in logs.

**Root Cause:** Container's memory usage exceeded the cgroup memory limit. Linux OOM killer terminates the container's PID 1.

**Diagnostic Command / Tool:**
```bash
# Check if container was OOM killed
docker inspect my-app | jq '.[0].State.OOMKilled'
# true → OOM kill occurred

# Check current memory usage
docker stats my-app --no-stream
# MEMUSE column approaching limit → needs increase or app has leak
```

**Fix:** Increase container memory limit (`--memory=1g`) or investigate application memory leak with `docker exec` + heap profiler.

**Prevention:** Set memory limits conservatively above peak usage, monitor with `docker stats`, and add restart policy (`--restart=on-failure:3`).

---

**Container Cannot See Host Files**

**Symptom:** Application inside container cannot read a config file from the host; `FileNotFoundError` in logs.

**Root Cause:** MNT namespace isolation — the container's filesystem is its own overlay; host files are not visible unless explicitly mounted.

**Diagnostic Command / Tool:**
```bash
# Check what mounts are inside the container
docker exec my-app mount | grep "host"
# Empty if no -v volume mounts configured
```

**Fix:** Add a volume mount: `-v /host/path/config.yaml:/app/config.yaml:ro`

**Prevention:** All files the application needs from the host must be explicitly mounted via `-v`. Never assume host filesystem is visible inside containers.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Linux Namespaces` — the kernel feature that provides container isolation
- `Cgroups` — the kernel feature that enforces container resource limits

**Builds On This (learn these next):**
- `Docker` — the tool that makes containers accessible via a user-friendly interface
- `Container Orchestration` — manages containers at scale across many hosts
- `Docker Image` — the portable artifact that defines what a container runs

**Alternatives / Comparisons:**
- `Docker vs VM` — container vs full virtualisation trade-off comparison
- `MicroVM (Firecracker)` — lightweight VM for stronger isolation than containers
- `Podman` — daemonless container runtime alternative to Docker

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Isolated, portable Linux process: shares │
│              │ host kernel, isolated via namespaces     │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Dependency hell + "works on my machine"  │
│ SOLVES       │ + VM overhead for lightweight isolation  │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Shares kernel but isolates everything    │
│              │ else — the best cost/isolation trade-off │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Almost always for application deployment │
│              │ where kernel-level isolation not needed  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Untrusted multi-tenant code (use MicroVM)│
│              │ Windows workload on Linux host           │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Speed + density + portability vs         │
│              │ shared kernel security surface           │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "A shipping container for software —     │
│              │  same box, any dock, identical delivery" │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Docker → Docker Image → Kubernetes       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A container runs with `--pid=host --network=host` flags for a legacy application. An engineer says "these flags are needed for the app to work." Explain exactly what namespace isolation these flags remove, what the specific security implications are (what an attacker with a foothold in this container can now do that they could not in a normal container), and propose an alternative architectural approach that keeps the application working without these flags.

**Q2.** A developer is surprised to find that their containerised Python application runs with root (UID 0) inside the container. The base image is `python:3.12`. They were told "containers are isolated so it doesn't matter." Under what specific conditions does running as root inside a container create a real security risk on the host? Describe the exact container escape vector that this enables and what Dockerfile instruction would prevent it.

