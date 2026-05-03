---
layout: default
title: "Docker vs VM"
parent: "Containers"
nav_order: 840
permalink: /containers/docker-vs-vm/
number: "0840"
category: Containers
difficulty: ★☆☆
depends_on: Container, Docker, Linux Namespaces, Cgroups
used_by: Container Orchestration, Container Security, containerd
related: Container, Linux Namespaces, Cgroups, Docker, Container Security
tags:
  - containers
  - docker
  - foundational
  - architecture
  - mental-model
---

# 840 — Docker vs VM

⚡ TL;DR — VMs virtualise hardware; containers virtualise the OS — containers share the host kernel, making them lighter and faster while providing weaker isolation.

| #840 | Category: Containers | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Container, Docker, Linux Namespaces, Cgroups | |
| **Used by:** | Container Orchestration, Container Security, containerd | |
| **Related:** | Container, Linux Namespaces, Cgroups, Docker, Container Security | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Every engineer deploying software faces a fundamental question: how do I isolate this workload from other workloads on the same machine? The history of this problem has two eras. In the 2000s, Virtual Machines (VMware, Hyper-V, KVM) were the answer — virtualise the entire hardware stack and run a separate OS per workload. In the 2010s, containers (Docker) offered a lighter alternative. But the trade-offs between these approaches are frequently misunderstood — teams either over-isolate (running containers inside VMs inside containers) or under-isolate (treating containers as equivalent to VMs for multi-tenant security).

**THE BREAKING POINT:**
Teams choosing between containers and VMs without understanding the isolation model make wrong security decisions. A multi-tenant platform that isolates tenants with containers alone (when VM-level isolation is required) is a security breach waiting to happen. A team that deploys one VM per microservice because "that's how we always did it" wastes infrastructure budget and slows deployments by an order of magnitude.

**THE INVENTION MOMENT:**
This is exactly why understanding the Docker vs VM distinction is foundational — it defines the isolation boundary, the performance characteristics, and the security model of every infrastructure decision.

---

### 📘 Textbook Definition

A **Virtual Machine (VM)** runs a complete guest operating system on top of a hypervisor, which emulates or directly partitions hardware resources (CPU, memory, disk, network) for each VM. VMs provide hardware-level isolation — guest OS kernels are fully independent of the host. A **Docker container** runs as an isolated process group on the host OS kernel, using Linux Namespaces to provide resource isolation (file system, network, PID, user) and cgroups to enforce resource limits. Containers share the host kernel — there is no guest OS, no hypervisor, and no hardware virtualisation. The key distinction: VMs virtualise hardware; containers virtualise the operating system.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
VMs are like separate apartments in a building; containers are like rooms in a shared apartment.

**One analogy:**
> Imagine a 20-story apartment building. Virtual Machines are like separate apartments: each has its own plumbing, electrical wiring, walls, and door locks — completely independent of every other apartment. Renting one costs more and takes time to set up. Docker containers are like rooms in a shared apartment: they share the plumbing, electricity, and exterior walls, but each has its own door and private space inside. Rooms are cheaper, faster to set up, and easier to move in — but if the shared plumbing breaks, everyone is affected.

**One insight:**
The "shared kernel" property is both containers' greatest advantage (faster, smaller, more efficient) and their greatest limitation (a kernel vulnerability like Dirty COW affects every container on that host, regardless of isolation). For truly untrusted, multi-tenant workloads, VM isolation remains the gold standard.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. VMs provide hardware-level isolation. Each VM has its own kernel, memory address space, and device drivers.
2. Containers provide OS-level isolation. They share the host kernel, use namespaces for logical separation, and cgroups for resource limits.
3. Stronger isolation requires more overhead. You cannot have VM-equivalent isolation at container-equivalent cost.

**DERIVED DESIGN:**

```
┌──────────────────────────────────────────────────────────┐
│      VM Architecture vs Container Architecture           │
├───────────────────────┬──────────────────────────────────┤
│  VIRTUAL MACHINE      │  CONTAINER                       │
├───────────────────────┼──────────────────────────────────┤
│  App                  │  App                             │
│  Guest OS (full)      │  (no guest OS)                   │
│  Guest Kernel         │                                  │
│  ─────────────────    │  Container runtime (namespaces)  │
│  Hypervisor           │  ─────────────────────────────   │
│  Host OS Kernel       │  Host OS Kernel (shared!)        │
│  Physical Hardware    │  Physical Hardware               │
└───────────────────────┴──────────────────────────────────┘
```

**Resource characteristics:**

- **Start time:** VM: 30–60 seconds (boot OS). Container: 50ms–2 seconds (process launch).
- **Memory overhead:** VM: 512MB–2GB for OS kernel and system processes. Container: ~10MB overhead (just the process).
- **Disk size:** VM image: 2–20GB. Container image: 5MB–500MB (no full OS).
- **Density:** One host can run 10–50 VMs. The same host can run 500–1,000+ containers.

**Isolation comparison:**

- **Kernel:** VMs: separate kernel per VM. Containers: shared kernel.
- **User accounts:** VMs: fully separate `/etc/passwd` per VM. Containers: namespace-isolated UIDs.
- **Filesystem:** VMs: separate disk partition. Containers: overlayfs with namespace isolation.
- **Network:** VMs: separate virtual NIC. Containers: network namespace with virtual ethernet pair.
- **Security boundary:** VMs: hypervisor. Containers: kernel namespaces + seccomp + AppArmor/SELinux.

**THE TRADE-OFFS:**

**Gain (containers):** Start in milliseconds, pack densely, share the OS layer reducing storage/memory.

**Cost (containers):** Weaker isolation — a kernel exploit can affect all containers on the host.

---

### 🧪 Thought Experiment

**SETUP:**
A company runs a SaaS platform where customers upload code to execute (think: serverless functions or online code judges). Each execution must be isolated from others.

**WHAT HAPPENS WITH CONTAINERS ONLY:**
Customer A uploads a function. It runs in a container. Customer B exploits a kernel vulnerability in the shared host kernel (e.g., Dirty COW in older kernels, or a recent namespace escape). Because all containers share the kernel, Customer B's exploit affects all other containers on the same host — including Customer A's execution and the host itself. The "isolation" was namespace-level, not kernel-level.

**WHAT HAPPENS WITH VM ISOLATION:**
Each customer's function runs in a micro-VM (AWS Firecracker, gVisor). Each has its own kernel. Customer B's kernel exploit affects only their micro-VM. The host kernel is shielded by the hypervisor. Customer A is unaffected. Recovery: kill the compromised VM, start a fresh one.

**THE INSIGHT:**
The right isolation level depends on the threat model. Containers are excellent for isolating co-operative, trusted workloads from each other (your own microservices). VMs are required for isolating untrusted, adversarial code from other tenants and the host.

---

### 🧠 Mental Model / Analogy

> VMs are bungalow houses; containers are apartments in a building. Houses share the street and city infrastructure (power grid, water mains) but each house has its own walls, roof, and private utilities inside. If one house burns down, the neighbours are unaffected (strong isolation). Apartments share walls, plumbing, and the building's foundation. A flood in the basement affects every apartment (shared kernel risk). Apartments are cheaper per square metre, pack more people onto the same land, and can be set up faster. Choose based on what level of independence from your neighbours you need.

Mapping:
- "House (bungalow)" → Virtual Machine
- "Apartment building" → Docker host
- "Apartment" → Container
- "Building foundation and plumbing" → Host OS kernel
- "Private utilities per house" → Guest OS kernel per VM
- "Flood in basement" → kernel vulnerability affecting all containers

Where this analogy breaks down: a physical apartment fire does spread to neighbours. A container "fire" (compromise) cannot propagate to other containers via namespaces alone — it requires an actual kernel exploit to escape. The isolation is weaker than houses but stronger than the analogy suggests.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A Virtual Machine is a complete fake computer running inside a real computer — it has its own operating system, fake disk, and fake hardware. Docker containers are more like separate drawers in the same desk — they share the desk (operating system) but keep their contents private. Drawers are faster to open and take less space.

**Level 2 — How to use it (junior developer):**
As a developer, the practical differences are: containers start in seconds, VMs in minutes. Container images are megabytes; VM images are gigabytes. You run many more containers per machine. In Kubernetes, you use containers. For legacy applications or full OS control, you use VMs (EC2, Azure VM). Hybrid: Kubernetes nodes are VMs, and containers run inside those VMs — you get both VM isolation (trusted cluster boundary) and container density (efficient workload packing).

**Level 3 — How it works (mid-level engineer):**
VMs use hardware virtualisation: the hypervisor (VMware ESXi, KVM, Hyper-V) intercepts privileged CPU instructions from the guest kernel and emulates or directly partitions hardware. Each VM has its own page table, device drivers, and system call interface. Containers use Linux kernel features: namespaces (pid, net, mnt, uts, ipc, user) provide logical separation, and cgroups limit CPU, memory, and I/O. The container process runs directly on the host kernel — no translation layer. This is why containers start in milliseconds: no OS boot, no bootloader, just `fork/exec` with namespace flags.

**Level 4 — Why it was designed this way (senior/staff):**
Container design was driven by density and developer experience requirements. Cloud operators (Google ran Borg for years before Kubernetes) needed to pack thousands of workloads per machine with sub-second startup times. VMs could not satisfy this. The deliberate trade-off: weaker isolation in exchange for dramatically higher density and speed. Modern mitigation: gVisor (Google) and Kata Containers add a lightweight VM or userspace kernel between the container and the host kernel without the full VM overhead — capturing 80% of container performance with 80% of VM isolation. AWS Firecracker achieves VM-level isolation in 125ms startup time by running minimal kernels (no device drivers, no initrd) — blurring the VM/container line.

---

### ⚙️ How It Works (Mechanism)

**How Docker runs a container (kernel-level view):**

1. `docker run nginx` → Docker daemon calls `fork()`
2. Child process calls `clone()` with namespace flags:
   - `CLONE_NEWPID` → new PID namespace (container sees itself as PID 1)
   - `CLONE_NEWNET` → new network namespace (private IP stack)
   - `CLONE_NEWNS` → new mount namespace (private filesystem view)
   - `CLONE_NEWUTS` → new UTS namespace (custom hostname)
   - `CLONE_NEWIPC` → new IPC namespace (private semaphores, message queues)
3. Child calls `unshare()` to switch to overlayfs root (container's merged filesystem)
4. cgroups are configured: `cpu.cfs_period_us`, `memory.limit_in_bytes` etc.
5. Capabilities are dropped (e.g., `CAP_SYS_ADMIN` removed)
6. `execve("/usr/sbin/nginx", ...)` — the application starts

From nginx's perspective, it is the only process, on a private network, with a custom hostname, and a private filesystem. From the kernel's perspective, it is just a process with special namespace flags.

**How a hypervisor runs a VM:**

1. KVM module creates a VM fd via `ioctl(KVM_CREATE_VM)`
2. Hypervisor allocates guest physical memory (mapped to host virtual memory)
3. Guest kernel is loaded (GRUB boots into Linux)
4. Guest kernel initialises its own memory manager, process scheduler, network stack
5. VM applications call syscalls → guest kernel handles them → hardware access is mediated by hypervisor
6. If the guest kernel issues a privileged instruction (e.g., `VMCALL`), the CPU exits to the hypervisor handler

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW (Container):**
```
docker run → clone() with namespace flags ← YOU ARE HERE
  → cgroups configured
  → overlayfs root mounted
  → container process starts (milliseconds)
  → process exits → container stops → overlayfs cleaned
```

**NORMAL FLOW (VM):**
```
hypervisor allocates VM ← YOU ARE HERE
  → guest kernel boots (seconds to minutes)
  → OS initialises (systemd, network, services)
  → application starts
  → application exits → VM remains running until stopped
```

**WHAT CHANGES AT SCALE:**
At 10,000 containers per cluster, the shared-kernel model means a single kernel patch must be applied to all host nodes simultaneously (rolling node upgrades). In a VM fleet, guest kernel updates can be batched per VM independently. Container density advantages become huge: 100 vm-sized instances hold 1,000 containers each, versus 100 VMs holding 10 VMs each — 10x density difference. This is why cloud providers like AWS built Firecracker: VM security + container density.

---

### 💻 Code Example

**Example 1 — Inspect container isolation (Linux):**
```bash
# Start a container
docker run -d --name test nginx

# Get container PID on host
CPID=$(docker inspect test --format '{{.State.Pid}}')

# View container's namespaces (from host perspective)
ls -la /proc/$CPID/ns/

# Container sees its own PID namespace
docker exec test ps aux   # only sees nginx processes (PID 1, 2...)

# Host sees the true PID
ps aux | grep nginx    # much higher PID (e.g., 12345)
```

**Example 2 — Compare resource overhead:**
```bash
# Container memory overhead
docker run --rm nginx sleep 1 &
# nginx container uses ~10-20MB RSS

# VM equivalent would use ~512MB+ just for the OS

# Container start time
time docker run --rm alpine echo "hello"
# real  0m0.231s

# VM start time
# Typical VM boot: 30-90 seconds
```

**Example 3 — Container isolation limitations:**
```bash
# Containers share the host kernel version
docker run --rm alpine uname -r   # shows HOST kernel version
# e.g., 6.1.0-1-amd64 (the host's kernel, not Alpine's)

# A VM would show the GUEST kernel version
# (completely independent from the host)
```

---

### ⚖️ Comparison Table

| Property | VM | Docker Container | Kata Container | Best For |
|---|---|---|---|---|
| Isolation Level | Hardware (kernel) | OS (namespace) | Hardware (micro-VM) | |
| Start Time | 30–120s | 50ms–2s | 125ms–1s | Speed |
| Memory Overhead | 512MB–2GB | ~10MB | ~50–100MB | Density |
| Image Size | 2–20GB | 5MB–500MB | Same as container | Storage |
| Kernel Updates | Per VM | Per host node | Per VM | Ops flexibility |
| Multi-tenant Safety | Excellent | Poor without hardening | Excellent | Untrusted code |
| **Best For** | **Legacy apps, strong isolation** | **Microservices, CI/CD** | **Serverless, FaaS** | |

How to choose: Use containers for your own trusted workloads (microservices, CI/CD). Use VMs as the cluster node boundary (Kubernetes nodes are VMs). Use Kata/Firecracker/gVisor for multi-tenant workloads where container-level isolation is insufficient.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Containers are just lightweight VMs" | Containers share the host kernel. VMs have a separate kernel. The isolation model is fundamentally different, not just a performance difference. |
| "Docker provides the same security as VMs" | Not equivalent. Container escapes via kernel exploits are real CVEs. Multi-tenant isolation (different customers) should use VMs or hardened containers (gVisor/Kata). |
| "You can run any OS in a Docker container" | You can only run OSes that share the host kernel ABI. You cannot run a Windows container on a Linux kernel natively (Docker Desktop uses a Linux VM on Mac/Windows to solve this). |
| "VMs are always slower than containers" | For long-running workloads, the steady-state performance of a VM is nearly identical to a container. The startup overhead disappears after boot. The difference is in startup time and density. |
| "Containers replace VMs entirely in the cloud" | No. Cloud VMs are still the fundamental unit of cloud compute. Kubernetes nodes run as VMs. Containers run inside those VMs. The layers are complementary, not mutually exclusive. |

---

### 🚨 Failure Modes & Diagnosis

**Container escape via kernel vulnerability**

**Symptom:**
Forensic logs show a container process accessing host filesystem paths (`/proc/1/root`, `/etc/shadow` at host level). Container process has unexpected capabilities.

**Root Cause:**
Container escape via kernel vulnerability (e.g., Dirty COW, runc CVE-2019-5736). Shared kernel means kernel CVEs affect all containers.

**Diagnostic Command / Tool:**
```bash
# Check for processes accessing unexpected namespaces
nsenter -t 1 -m -u -i -n -p -- ls /

# Check container capabilities
docker inspect <container> | jq '.[0].HostConfig.CapAdd'

# Scan for known vulnerable kernel versions
uname -r   # compare against CVE advisories
```

**Fix:**
Patch host kernel immediately. For untrusted workloads, migrate to Kata Containers or gVisor. Enforce `seccomp` profiles and drop all unnecessary capabilities.

**Prevention:**
Never expose privileged containers to untrusted code. Apply kernel patches promptly. Use runtime security tools (Falco) to detect escape attempts.

---

**"Works in VM, breaks in container" (kernel feature mismatch)**

**Symptom:**
Application works in local VM-based environment but fails in container with `operation not permitted` or missing syscalls.

**Root Cause:**
The application relies on system calls or capabilities that are blocked by Docker's default seccomp profile or dropped capabilities.

**Diagnostic Command / Tool:**
```bash
# Check what syscalls the app uses
strace -c <command>

# Check Docker's default seccomp profile
docker info | grep -i seccomp

# Test without seccomp (diagnostic only — NOT for production)
docker run --security-opt seccomp=unconfined myapp
```

**Fix:**
Create a custom seccomp profile that allows exactly the syscalls the application needs. Do not run `--privileged` as the fix.

**Prevention:**
Document required syscalls and capabilities for each container. Enforce least-privilege from the start.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Container` — understand what a container is before comparing it to a VM
- `Linux Namespaces` — the kernel mechanism that provides container isolation
- `Cgroups` — the kernel mechanism that enforces container resource limits

**Builds On This (learn these next):**
- `Container Security` — understanding the isolation model is essential for securing containers correctly
- `Container Orchestration` — orchestrators run containers on VM nodes; the hybrid model in practice
- `containerd` — the runtime implementation that creates the namespace/cgroup isolation

**Alternatives / Comparisons:**
- `Container Security` — hardening containers to approach VM-level security
- `Kubernetes Architecture` — Kubernetes uses both VMs (nodes) and containers (workloads)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ The fundamental distinction between two   │
│              │ virtualisation models                     │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Engineers choose the wrong isolation      │
│ SOLVES       │ model — over-isolating or under-isolating │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ VMs virtualise hardware (own kernel).     │
│              │ Containers virtualise the OS (shared      │
│              │ kernel). Not the same security boundary.  │
├──────────────┼───────────────────────────────────────────┤
│ USE VM WHEN  │ Multi-tenant isolation, adversarial       │
│              │ workloads, legacy OS requirements         │
├──────────────┼───────────────────────────────────────────┤
│ USE CONT.    │ Your own trusted microservices, CI/CD,    │
│ WHEN         │ dev environments, Kubernetes workloads    │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Density + speed vs isolation strength     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Containers are fast drawers;             │
│              │  VMs are separate rooms with a lock"      │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Container Security → Linux Namespaces →   │
│              │ Kata Containers                           │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** AWS Lambda runs customer code in containers (Firecracker micro-VMs) with a startup time of ~125ms — comparable to Docker containers. Based on what you know about VM isolation vs container isolation, why does AWS choose VM-level isolation for Lambda even though AWS controls the code (the Lambda runtime), not the customer? What threat model does VM isolation protect against that container isolation cannot?

**Q2.** Your company runs a Kubernetes cluster where each node is a VM and each pod is a container. You have a security requirement: "tenant A's data must be fully isolated from tenant B." Analyse this architecture at every layer: host hardware → VM hypervisor → VM node → container network → application. At which layers is the isolation strong, at which layers is it incomplete, and what additional controls are required to achieve genuine multi-tenant isolation in Kubernetes?

