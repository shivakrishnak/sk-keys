---
layout: default
title: "Container"
parent: "Containers"
nav_order: 821
permalink: /containers/container/
number: "821"
category: Containers
difficulty: ★☆☆
depends_on: "Linux Namespaces, Linux Control Groups"
used_by: "Docker, Kubernetes, Container Registry, Microservices"
tags: #containers, #docker, #linux, #isolation, #virtualization
---

# 821 — Container

`#containers` `#docker` `#linux` `#isolation` `#virtualization`

⚡ TL;DR — A **container** is a lightweight, isolated process running on the host OS kernel, with its own filesystem, network namespace, and process tree — but sharing the host kernel. Faster and lighter than VMs (no guest OS). Docker is the dominant container runtime. The fundamental unit of modern cloud-native deployment.

| #821            | Category: Containers                                  | Difficulty: ★☆☆ |
| :-------------- | :---------------------------------------------------- | :-------------- |
| **Depends on:** | Linux Namespaces, Linux Control Groups                |                 |
| **Used by:**    | Docker, Kubernetes, Container Registry, Microservices |                 |

---

### 📘 Textbook Definition

**Container**: a standard unit of software that packages application code and all its dependencies (libraries, runtime, config) so the application runs reliably across different computing environments. Technically: an isolated user-space process created using Linux kernel features — **namespaces** (isolation of PID, network, mount, IPC, UTS, user) and **control groups (cgroups)** (resource limits: CPU, memory, disk I/O). Containers share the host kernel (unlike VMs, which run a separate guest OS per virtual machine). The container **image** is an immutable, layered filesystem snapshot. The running container is an instance of an image — adding a thin writable layer on top. Key properties: (1) **Isolation** — processes cannot see outside the container namespace; (2) **Portability** — runs consistently on any host with a compatible container runtime (Docker, containerd, CRI-O); (3) **Immutability** — the image is read-only; state is ephemeral (lost on container stop) unless volumes are used; (4) **Resource efficiency** — shares host kernel; starts in milliseconds; much lower overhead than VMs.

---

### 🟢 Simple Definition (Easy)

A container is a box that holds your app and everything it needs to run (Python version, libraries, config). The box is sealed: your app can't accidentally depend on something installed on the host machine. You can ship the same box to development, staging, and production — it behaves identically. Unlike a virtual machine (which includes its own OS), a container shares the host OS kernel — so it starts in milliseconds and uses very little memory.

---

### 🔵 Simple Definition (Elaborated)

Before containers: "works on my machine" was the classic developer problem. App works in dev (Python 3.8, library v1.2), fails in production (Python 3.6, library v1.0). Containers solve this: the image packages the exact Python version and library versions. The container runs the same everywhere. Before VMs solved this too, but VMs carry a full OS (gigabytes, minutes to boot). A container image is megabytes; it starts in milliseconds; 50 containers can run on the same host with minimal overhead.

The killer combination: containers + orchestration (Kubernetes) = self-healing, auto-scaling, declarative deployment of microservices at scale.

---

### 🔩 First Principles Explanation

```
VM vs CONTAINER:

  VIRTUAL MACHINE:
  ┌──────────────────────────────────────────────────────┐
  │ Host Hardware                                        │
  │ ┌────────────────────────────────────────────────┐   │
  │ │ Host OS (Hypervisor Layer)                     │   │
  │ │ ┌─────────────────┐  ┌─────────────────┐       │   │
  │ │ │ VM 1            │  │ VM 2            │       │   │
  │ │ │  Guest OS       │  │  Guest OS       │       │   │
  │ │ │  (Linux 5.4)    │  │  (Ubuntu 22.04) │       │   │
  │ │ │  App A          │  │  App B          │       │   │
  │ │ └─────────────────┘  └─────────────────┘       │   │
  │ └────────────────────────────────────────────────┘   │
  └──────────────────────────────────────────────────────┘

  Each VM: full OS = 512MB-4GB RAM, minutes to boot
  Strong isolation (separate kernels)

  CONTAINER:
  ┌──────────────────────────────────────────────────────┐
  │ Host Hardware                                        │
  │ ┌────────────────────────────────────────────────┐   │
  │ │ Host OS (Linux kernel, shared)                 │   │
  │ │ ┌──────────────┐ ┌──────────────┐ ┌──────────┐ │   │
  │ │ │ Container 1  │ │ Container 2  │ │ Container│ │   │
  │ │ │ [nginx:1.24] │ │ [node:18]    │ │ 3 [java] │ │   │
  │ │ │ namespaces   │ │ namespaces   │ │ cgroups  │ │   │
  │ │ │ cgroups      │ │ cgroups      │ │          │ │   │
  │ │ └──────────────┘ └──────────────┘ └──────────┘ │   │
  │ └────────────────────────────────────────────────┘   │
  └──────────────────────────────────────────────────────┘

  Each container: shared kernel; processes isolated via namespaces
  Image: 50-500MB; starts in milliseconds; 100+ containers per host

LINUX MECHANISMS:

  NAMESPACES (isolation):
  ┌──────────────┬─────────────────────────────────────────────┐
  │ Namespace    │ Isolates                                    │
  ├──────────────┼─────────────────────────────────────────────┤
  │ PID          │ Process IDs (container sees PID 1 for init)│
  │ Network      │ Network interfaces, routing, ports         │
  │ Mount        │ Filesystem mount points                     │
  │ IPC          │ System V IPC, POSIX message queues          │
  │ UTS          │ Hostname, domain name                       │
  │ User         │ User/group IDs (root in container ≠ root)  │
  │ Cgroup       │ Cgroup hierarchy visibility                 │
  └──────────────┴─────────────────────────────────────────────┘

  CGROUPS (resource limits):
  - CPU: limit to N cores or % of host CPU
  - Memory: hard limit (OOM kill if exceeded)
  - Block I/O: limit disk read/write throughput
  - Network: traffic shaping (with tc)

  CONTAINER FILESYSTEM (layered):
  Base image: ubuntu:22.04 (layer 1: 29MB)
  + RUN apt-get install python3    (layer 2: 45MB)
  + COPY app.py /app/              (layer 3: 1MB)
  + RUN pip install -r req.txt     (layer 4: 120MB)
  = Image: 195MB (each layer immutable)

  Running container: image layers (read-only) + writable layer (thin, ephemeral)
  Container A and Container B using same base image: share layer 1 on disk (copy-on-write)

CONTAINER LIFECYCLE:

  docker pull nginx:1.24       ← download image from registry
  docker run -p 8080:80 nginx  ← create + start container
  docker stop <container_id>   ← graceful stop (SIGTERM → wait → SIGKILL)
  docker rm <container_id>     ← remove container (writable layer deleted)

  Image → Container (running) → Container (stopped) → [rm] deleted
```

---

### ❓ Why Does This Exist (Why Before What)

Three pre-container problems: (1) **Environment parity**: apps work in dev but not in prod due to different library versions; (2) **Dependency conflicts**: two apps on the same server need different Python versions — impossible without isolation; (3) **VM overhead**: VMs solve isolation but are heavyweight (gigabytes, slow boot). Containers solve all three: packages exact dependencies (env parity), isolated namespaces (no conflicts), shares host kernel (lightweight). The combination unlocked microservices at scale: run 50+ isolated services on one host, deploy each independently, scale each to N instances.

---

### 🧠 Mental Model / Analogy

> **Shipping containers on a cargo ship**: before standardized shipping containers, cargo was loaded piece by piece — slow, inconsistent, often damaged in transit. The standardized steel shipping container (1956) revolutionized shipping: any crane in any port loads and unloads containers identically; container contents don't care about the ship. Software containers apply the same idea: standardized, sealed unit of software that works identically regardless of the underlying infrastructure ("port" = cloud provider, "ship" = host server, "crane" = container runtime).

---

### ⚙️ How It Works (Mechanism)

```
CONTAINER RUNTIME (containerd / Docker):

  docker run nginx:1.24

  1. Docker daemon receives request
  2. Pull image from registry (if not cached locally)
  3. Create new namespace set (PID, network, mount, IPC, UTS)
  4. Set up cgroup limits (CPU, memory)
  5. Mount image layers (read-only) + new writable layer (overlay2)
  6. Start container entrypoint process in the new namespace
  7. Assign container IP (via veth pair + bridge network)

  Result: nginx process running as PID 1 in its namespace
  From nginx's perspective: it's the only process on the system
  From host's perspective: it's process 8472 in the host PID namespace
```

---

### 🔄 How It Connects (Mini-Map)

```
Need to run isolated, portable, lightweight processes
        │
        ▼
Container ◄── (you are here)
(namespaces + cgroups; layered filesystem; portable unit)
        │
        ├── Docker: the dominant container toolchain
        ├── Docker Image: the immutable blueprint for a container
        ├── Docker Layer: the layered filesystem inside an image
        ├── Kubernetes: orchestrates containers at scale
        └── Microservices: containers as the deployment unit for services
```

---

### 💻 Code Example

```bash
# Basic container lifecycle
docker pull ubuntu:22.04                   # pull image (download layers)
docker run --rm -it ubuntu:22.04 bash     # run interactively; --rm removes on exit

# Run a web server container
docker run -d \                            # -d: detached (background)
  --name my-nginx \
  -p 8080:80 \                            # host:container port mapping
  --memory 256m \                         # cgroup memory limit
  --cpus 0.5 \                            # cgroup CPU limit (half a core)
  nginx:1.24

# Inspect running container
docker ps                                  # list running containers
docker exec -it my-nginx bash             # open shell inside running container
docker logs my-nginx                      # view stdout/stderr
docker stats my-nginx                     # live CPU/memory/net/disk stats

# Container filesystem (writable layer)
docker exec my-nginx touch /tmp/test.txt  # creates in writable layer
docker stop my-nginx
docker rm my-nginx                        # writable layer deleted; /tmp/test.txt gone
```

---

### ⚠️ Common Misconceptions

| Misconception                              | Reality                                                                                                                                                                                                                                                                                          |
| ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Containers are as secure as VMs            | Containers share the host kernel — a kernel exploit can escape the container. VMs have stronger isolation (separate kernels). For multi-tenant untrusted workloads, use VMs or sandboxed containers (gVisor, Kata Containers). For trusted workloads (your own code), containers are sufficient. |
| Stopping a container preserves its state   | The writable layer is deleted when you `docker rm` the container. Data written inside the container is lost. Use **volumes** (`-v /host/path:/container/path`) for persistent data.                                                                                                              |
| Running as root inside a container is safe | Running as root inside a container is still a security risk — if the container is misconfigured or compromised, root access can escape to the host. Always use `USER` directive in Dockerfile and run as non-root.                                                                               |

---

### 🔥 Pitfalls in Production

```
PITFALL: storing data inside a container (no volumes)

  # ❌ Database running in container, data written to /var/lib/postgresql/data
  docker run --name postgres postgres:15
  # Data stored in container's writable layer
  # Container crashes → docker rm → ALL DATA LOST

  # ✅ ALWAYS use volumes for stateful data
  docker run --name postgres \
    -v postgres-data:/var/lib/postgresql/data \  # named volume: persists across restarts
    postgres:15
  # Volume survives container removal; data persists to next container using same volume

PITFALL: running as root (security)

  # ❌ Default: many images run as root
  FROM ubuntu:22.04
  RUN apt-get install myapp
  CMD ["myapp"]   # runs as root ← security risk

  # ✅ Add non-root user
  FROM ubuntu:22.04
  RUN apt-get install myapp && \
      useradd -r -u 1001 appuser
  USER appuser    # all subsequent commands + CMD run as appuser
  CMD ["myapp"]
```

---

### 🔗 Related Keywords

- `Docker` — the dominant container toolchain (build, run, push, pull)
- `Docker Image` — the immutable blueprint; layers of filesystem snapshots
- `Linux Namespaces` — the kernel feature providing container isolation
- `Kubernetes` — orchestrates containers: scheduling, scaling, networking, health
- `Microservices` — containers are the natural deployment unit for microservices

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ CONTAINER = image + writable layer + namespaces + cgroup│
│ IMAGE: immutable layers; shared across containers       │
│ NAMESPACE: isolation (PID, net, mount, user, UTS, IPC)  │
│ CGROUP: resource limits (CPU, memory, disk I/O)         │
├──────────────────────────────────────────────────────────┤
│ vs VM: shares host kernel → faster, lighter, less secure│
│ vs process: isolated → no env leakage, portable         │
│ Rule: stateful data → volumes; run as non-root          │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Containers share the host kernel. This means a container running on a Linux host cannot run Windows binaries, and a Docker Desktop on Mac/Windows actually runs a Linux VM to host the container runtime. What are the implications for cross-platform container builds? When you `docker build` on an Apple M1 (ARM) Mac and push to ECR, will the image run on an x86_64 EC2 instance? What is `docker buildx` and how does multi-platform image building work?

**Q2.** Containers are described as "immutable infrastructure" — you don't patch a running container, you rebuild the image and redeploy. What does this mean for the traditional operations model of SSHing into servers and running `apt-get upgrade`? How does immutable container infrastructure change patching workflows, especially for CVEs discovered in base images (e.g., a critical OpenSSL vulnerability in your `ubuntu:22.04` base)?
