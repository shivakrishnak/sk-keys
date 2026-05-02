---
layout: default
title: "Docker"
parent: "Containers"
nav_order: 822
permalink: /containers/docker/
number: "0822"
category: Containers
difficulty: ★☆☆
depends_on: Container, Linux Namespaces, Cgroups, OCI Standard
used_by: Docker Image, Dockerfile, Docker Compose, Container Registry, Multi-Stage Build
related: Container, Podman, containerd, OCI Standard, Docker vs VM
tags:
  - containers
  - docker
  - devops
  - foundational
  - linux
---

# 822 — Docker

⚡ TL;DR — Docker is the tool that made Linux containers accessible to every developer — packaging, running, and distributing containers with a single command.

| #822 | Category: Containers | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Container, Linux Namespaces, Cgroups, OCI Standard | |
| **Used by:** | Docker Image, Dockerfile, Docker Compose, Container Registry, Multi-Stage Build | |
| **Related:** | Container, Podman, containerd, OCI Standard, Docker vs VM | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Before Docker (2013), Linux containers existed (LXC since 2008) but required intimate Linux kernel knowledge to use: manually configuring namespaces, cgroups, union filesystems, and chroot environments. A developer needing to run an application in isolation wrote dozens of lines of shell script just to set up a basic container. Sharing that "container" with a teammate meant sharing the script AND hoping their Linux version had the same kernel features. Container adoption outside Google-scale infrastructure was essentially zero.

**THE BREAKING POINT:**
Containers were powerful but inaccessible. The complexity barrier prevented adoption. Application packaging, distribution, and runtime management needed a standardised, simple interface.

**THE INVENTION MOMENT:**
This is exactly why Docker was built — a user-friendly abstraction layer over Linux containers. One `Dockerfile` to define the image. One `docker build` to create it. One `docker push` to share it. One `docker run` to execute it anywhere. Docker democratised containers.

---

### 📘 Textbook Definition

**Docker** is an open-source platform for developing, packaging, and running applications in containers. It provides: the **Docker Engine** (a client-server daemon that manages containers on a Linux host), the **Docker CLI** (user interface for all operations), the **Dockerfile** format (declarative image build specification), **Docker Hub** / container registries (image distribution), and **Docker Compose** (multi-container application definition). Docker standardised the OCI image format and container runtime, enabling any OCI-compliant tool to build, distribute, and run containers interchangeably.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Docker is the standard toolbox that turns a Linux application into a portable, self-contained unit anyone can run in one command.

**One analogy:**
> Before Docker, containers were like blueprints for a house — powerful but requiring an architect to read them. Docker is the prefabricated home factory: you describe what you want, Docker builds it, packages it into a transportable unit, and anyone can "unpack and live in it" anywhere that has a Docker installation. Same house, any plot of land.

**One insight:**
Docker's real innovation was not the container technology (Linux had that). It was the **image format** and **registry** — a standard way to package, version, store, and distribute working application environments as portable artifacts. This is what enabled "share a container" to mean the same thing to everyone.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. An application and its dependencies must be packaged together to be truly portable.
2. The package must have a standard format so any receiving system can unpack and run it without bespoke configuration.
3. The build process must be reproducible and describable as code.

**DERIVED DESIGN:**
Docker implements three things that realise these invariants:

**1. Image format (OCI):** A layered, content-addressable archive of filesystem changes. Each `RUN`, `COPY`, `ADD` instruction in a Dockerfile creates a new immutable layer. Layers are shared between images via a content-addressed store (SHA256 digest). `nginx:1.25` and `myapp:latest` may share the same `debian:bookworm` base layer — pulled once, used by many.

**2. Docker Engine (dockerd):** A long-running daemon that: listens to Docker CLI API calls, manages image storage (layer store), delegates container lifecycle to containerd (the OCI container runtime), manages networks and volumes.

**3. Registry protocol:** Push and pull images to/from any OCI-compatible registry (Docker Hub, ECR, ACR, GCR) using a standard HTTP API. Images are identified by `name:tag` and addressable by digest (`sha256:abc123`).

**THE TRADE-OFFS:**
**Gain:** Universal packaging; consistent environments; fast distribution; strong ecosystem (Docker Hub, Compose, BuildKit).
**Cost:** dockerd daemon runs as root (historically a security concern); the daemon is a single point of failure; Podman emerged partly to address rootless and daemonless needs.

---

### 🧪 Thought Experiment

**SETUP:**
An engineer shares a Python application with a colleague. The app uses specific library versions.

**WHAT HAPPENS WITHOUT DOCKER:**
The engineer sends the code and a `requirements.txt`. The colleague's laptop has Python 3.8 (app needs 3.11). They install 3.11 but it conflicts with their system Python. They spend 2 hours with `venv`, `pyenv`, and system library conflicts. The app half-works: one library depends on `libssl 1.1.1` which the colleague's Ubuntu has at version 3.0. Stack trace. Give up.

**WHAT HAPPENS WITH DOCKER:**
The engineer provides a `Dockerfile` and runs `docker build -t myapp .`. Pushes to Docker Hub: `docker push myapp:1.0`. The colleague runs `docker pull myapp:1.0 && docker run myapp:1.0`. The image contains Python 3.11, all libraries, and the exact `libssl` version the app was built with. It runs identically. 30 seconds total.

**THE INSIGHT:**
Docker moves the "it works on my machine" guarantee from the developer's machine to the image. The image IS the machine — everything the app needs, frozen in a portable artifact.

---

### 🧠 Mental Model / Analogy

> Docker is like a Java JVM, but for entire applications. Java's promise was "compile once, run anywhere" — the JVM abstracts away the OS. Docker's promise is "build once, run anywhere" — the container image abstracts away the host environment. Just as a `.jar` file carries all Java bytecode and runs on any JVM, a Docker image carries all application files and runs on any Docker host.

**Mapping:**
- "Java .jar file" → Docker image
- "JVM (Java Virtual Machine)" → Docker Engine + Linux kernel container support
- "java -jar myapp.jar" → `docker run myapp:1.0`
- "Maven Central" → Docker Hub (image registry)
- "pom.xml / build.gradle" → Dockerfile

**Where this analogy breaks down:** A JVM runs Java bytecode, which is a controlled subset of operations; a Docker container runs a full Linux userspace — it can run any process, which is far less controlled from a security perspective.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Docker is a tool that packages a program and all of its requirements into a box. You can give anyone that box and they can run the program, no matter what kind of computer they have, without needing to install anything separately.

**Level 2 — How to use it (junior developer):**
The most common Docker workflow: write a `Dockerfile` defining your application's base image, dependencies, and startup command. Run `docker build -t myapp:1.0 .` to create the image. Run `docker run -p 8080:8080 myapp:1.0` to start a container. Use `docker ps` to see running containers. Use `docker logs myapp` to see output. Use `docker stop myapp` to stop it.

**Level 3 — How it works (mid-level engineer):**
`docker run` goes through this chain: Docker CLI → REST API call to dockerd → dockerd asks containerd to start the container → containerd calls runc to create the namespace-isolated process → runc calls Linux `clone()` → the container process is born with its namespace-isolated view. The image layers are assembled by OverlayFS into a single unified filesystem mount that the container sees as `/`. The container's writable layer is a copy-on-write overlay on top of the read-only image layers. The Docker daemon also manages port forwarding (iptables NAT rules for `-p 8080:80`), DNS (custom Docker DNS server at 127.0.0.11), and volume mounts.

**Level 4 — Why it was designed this way (senior/staff):**
Docker started as a PaaS infrastructure tool at dotCloud and was open-sourced in 2013 with a monolithic architecture (docker CLI + docker daemon did everything). As adoption exploded, the monolith became a liability — the daemon's root requirement was a security surface; the namespace coupling between CLI, daemon, and runtime prevented alternative runtimes. Docker was refactored: the runtime was donated to CNCF as containerd; the image format was standardised as OCI; BuildKit replaced the legacy builder. Today's Docker is a thin client on top of containerd + buildkitd. This decomposition is why you can use containerd directly in Kubernetes without Docker, and why Podman (daemonless, rootless) is a viable drop-in replacement for many workflows.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────────┐
│              DOCKER ARCHITECTURE                         │
├──────────────────────────────────────────────────────────┤
│  CLI                                                     │
│  docker build / run / push / pull                        │
│       ↓ REST API                                         │
├──────────────────────────────────────────────────────────┤
│  DOCKER DAEMON (dockerd)                                 │
│  - Image management (layer store)                       │
│  - Network management (virtual networks, iptables)      │
│  - Volume management                                    │
│  - Container lifecycle (delegated to containerd)        │
│       ↓ gRPC                                            │
├──────────────────────────────────────────────────────────┤
│  containerd                                              │
│  - Image pull / push                                    │
│  - Snapshot management (OverlayFS)                      │
│  - Container creation (delegates to runc)               │
│       ↓ OCI runtime API                                 │
├──────────────────────────────────────────────────────────┤
│  runc                                                    │
│  - Linux clone() with namespace flags                   │
│  - Cgroup assignment                                    │
│  - exec() the container entrypoint                     │
└──────────────────────────────────────────────────────────┘
```

**Image pull:** `docker pull nginx:1.25` → dockerd asks Registry for manifest (layer list + config) → pulls each layer SHA256 that isn't already in local layer store → assembles OverlayFS view.

**Container start:** `docker run nginx:1.25` → containerd creates a snapshot (OverlayFS) of the image layers + writable layer → runc clones new process with namespaces → cgroups configured → container's entrypoint is exec'd.

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Developer writes Dockerfile → docker build → [IMAGE ← YOU ARE HERE]
→ docker push → Registry → CI/CD pulls → docker run on server
→ Container serves traffic
```

**FAILURE PATH:**
```
docker run fails with "image not found" or daemon unavailable
→ check: docker ps (is daemon running?)
→ check: docker pull (can you reach registry?)
→ check: docker inspect image (does it exist locally?)
```

**WHAT CHANGES AT SCALE:**
At thousands of containers across hundreds of hosts, the Docker daemon per-host becomes a management bottleneck. Kubernetes replaces the manual `docker run` workflow with declarative scheduling across the fleet. Container registries must handle thousands of simultaneous pulls — a single deploy event with 100 nodes all pulling a 500 MB layer simultaneously requires a registry with CDN-backed storage or a local pull-through cache (Harbor).

---

### 💻 Code Example

Example 1 — Essential Docker commands:
```bash
# Build an image from Dockerfile in current directory
docker build -t myapp:1.0 .

# Run container: detached, port mapping, name
docker run -d --name my-api -p 8080:3000 myapp:1.0

# List running containers
docker ps

# View container logs (follow mode)
docker logs -f my-api

# Execute a command inside running container (debug shell)
docker exec -it my-api /bin/sh

# Stop and remove container
docker stop my-api && docker rm my-api

# List images
docker images

# Remove unused images (reclaim disk)
docker image prune -a
```

Example 2 — Image tagging and registry push:
```bash
# Tag for registry push
docker tag myapp:1.0 registry.example.com/team/myapp:1.0

# Login and push
docker login registry.example.com
docker push registry.example.com/team/myapp:1.0

# Pull on another host
docker pull registry.example.com/team/myapp:1.0
docker run registry.example.com/team/myapp:1.0
```

Example 3 — Inspect container internals:
```bash
# Full container metadata (JSON)
docker inspect my-api | jq '.[0].NetworkSettings.IPAddress'

# Resource usage (live stats)
docker stats my-api

# Diff: what changed in the container filesystem vs image
docker diff my-api
# A = Added, C = Changed, D = Deleted
```

---

### ⚖️ Comparison Table

| Tool | Daemon | Root Required | Compose | K8s Compatible | OCI |
|---|---|---|---|---|---|
| **Docker** | Yes (dockerd) | Default yes | Yes (Compose v2) | Via containerd | Yes |
| Podman | No (daemonless) | No (rootless) | Yes (Compose) | Yes | Yes |
| containerd | Yes (lightweight) | Yes | No | Yes (native) | Yes |
| nerdctl | Uses containerd | No (rootless) | Yes | Via containerd | Yes |

**How to choose:** Docker is the right choice for developer workflow (Dockerfile, Compose, local dev). In Kubernetes production, Kubernetes uses containerd directly — Docker is not needed on nodes. Use Podman for security-sensitive environments where rootless containers and no daemon are required.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Docker = containers | Docker is a tool that uses Linux containers; containers are the kernel feature. You can have containers without Docker (Podman, containerd). |
| Docker images are stored on the container | Images are stored in the Docker layer store on the host. Containers are running instances of images. Stopping a container does not delete the image. |
| Docker automatically secures your application | Default Docker configurations run as root inside containers and have broad capabilities — you must explicitly harden container security |
| Docker Compose is production-ready | Docker Compose is designed for development and simple deployments. Kubernetes is the production container orchestration platform. |
| docker stop immediately kills the container | `docker stop` sends SIGTERM and waits 10 seconds for graceful shutdown before sending SIGKILL. Applications must handle SIGTERM. |

---

### 🚨 Failure Modes & Diagnosis

**Docker Daemon Not Running**

**Symptom:** `docker: Cannot connect to the Docker daemon. Is the daemon running?`

**Diagnostic Command / Tool:**
```bash
systemctl status docker
# If stopped → systemctl start docker
journalctl -u docker -n 50
# Check recent daemon logs for startup errors
```

**Fix:** Start the daemon with `systemctl start docker`. If daemon fails to start, check for corrupted layer store or disk full: `df -h /var/lib/docker`.

**Prevention:** Configure Docker daemon for automatic restart: `systemctl enable docker`.

---

**No Space Left on Device**

**Symptom:** `docker: Error response from daemon: ... write /var/lib/docker/...: no space left on device`

**Root Cause:** Docker's layer store (`/var/lib/docker`) accumulated old images, stopped containers, and unused volumes.

**Diagnostic Command / Tool:**
```bash
docker system df
# Shows disk usage by images, containers, volumes, build cache
du -sh /var/lib/docker/
```

**Fix:** `docker system prune -a --volumes` removes all unused data. In production, be careful not to remove images being used.

**Prevention:** Schedule `docker system prune` as a cron job. Monitor `/var/lib/docker` disk usage.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Container` — the underlying concept Docker implements
- `Linux Namespaces` — the isolation mechanism Docker uses

**Builds On This (learn these next):**
- `Docker Image` — the portable artifact Docker builds and distributes
- `Dockerfile` — the build specification for creating Docker images
- `Docker Compose` — multi-container application orchestration for local/dev

**Alternatives / Comparisons:**
- `Podman` — daemonless, rootless drop-in alternative to Docker
- `containerd` — the container runtime Docker delegates to; Kubernetes uses directly

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ The tool that packages, distributes, and │
│              │ runs Linux containers with a simple CLI  │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Containers were too complex to use;      │
│ SOLVES       │ no standard image format or registry     │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ The image format + registry is the real  │
│              │ innovation — not the container runtime   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Developer workflow, local dev, CI builds,│
│              │ simple single-host deployments           │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Production at scale — use Kubernetes;   │
│              │ rootless environments — use Podman       │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Simplicity + ecosystem vs daemon         │
│              │ overhead + root requirement              │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The JVM for entire applications —       │
│              │  build once, run anywhere"               │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Docker Image → Dockerfile →              │
│              │ Container Registry                       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A team runs `docker run -v /:/host ubuntu bash` for debugging a production host. Explain exactly what this command does to namespace isolation, what an attacker with shell access to this container could do to the host, and why this command is the equivalent of giving root access to the host machine — even if the Docker daemon is running as root.

**Q2.** Your CI/CD pipeline runs `docker build` for every pull request. On average, each build takes 8 minutes. The team has 50 engineers submitting 5 PRs per day each = 250 builds/day. Build time is 8 minutes due to downloading the base image and installing all npm packages on every build. Design the exact caching strategy that reduces average build time to under 60 seconds without changing the application's Dockerfile structure.

