---
layout: default
title: "Docker"
parent: "Containers"
nav_order: 822
permalink: /containers/docker/
number: "822"
category: Containers
difficulty: ★☆☆
depends_on: "Container, Linux Namespaces"
used_by: "Docker Image, Dockerfile, Docker Compose, Container Registry, Kubernetes"
tags: #containers, #docker, #cli, #container-runtime, #devops
---

# 822 — Docker

`#containers` `#docker` `#cli` `#container-runtime` `#devops`

⚡ TL;DR — **Docker** is the dominant container platform: a CLI + daemon for building images, running containers, and pushing/pulling from registries. Docker democratized containers (2013) by making Linux namespaces/cgroups accessible through a simple CLI and Dockerfile format. The foundation of modern container-based CI/CD.

| #822            | Category: Containers                                                     | Difficulty: ★☆☆ |
| :-------------- | :----------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Container, Linux Namespaces                                              |                 |
| **Used by:**    | Docker Image, Dockerfile, Docker Compose, Container Registry, Kubernetes |                 |

---

### 📘 Textbook Definition

**Docker**: an open-source platform for developing, shipping, and running applications in containers. Components: (1) **Docker Engine** — the background daemon (`dockerd`) that manages containers, images, networks, and volumes via a REST API; (2) **Docker CLI** (`docker`) — command-line client that communicates with the daemon; (3) **Docker Hub** — the default public container registry; (4) **Docker Compose** — a tool for defining multi-container applications with a YAML file; (5) **Docker Desktop** — GUI + VM for Mac/Windows (Linux VM hosts the Docker daemon). Docker introduced the concept of the **Dockerfile** (a text file of instructions to build an image), the **layer model** (each Dockerfile instruction = one image layer), and the **container registry** (centralized image distribution). Current architecture: Docker Engine uses **containerd** (CNCF) as the container runtime, which uses **runc** (OCI-compliant) for the actual container creation.

---

### 🟢 Simple Definition (Easy)

Docker is the tool that makes containers practical. It provides: (1) `docker build` — turn a Dockerfile into an image; (2) `docker run` — start a container from an image; (3) `docker push/pull` — share images via a registry. Before Docker (2013), using Linux namespaces and cgroups directly required deep kernel expertise. Docker wrapped them in a simple CLI and the Dockerfile format — making containers accessible to every developer.

---

### 🔵 Simple Definition (Elaborated)

Docker has two personas:

**Docker as development tool**: developers use `docker run` to start a local database, Redis, or any service without installing it on their machine. `docker-compose up` starts a multi-service dev environment (app + database + cache) with one command. Consistent: same as what runs in CI and production.

**Docker as CI/CD tool**: `docker build` in CI creates an immutable artifact (the image) that is promoted from dev → staging → production without modification. "Build once, run anywhere." The image is the deployable unit — tagged, pushed to a registry, pulled in production (or by Kubernetes).

Docker's OCI (Open Container Initiative) standardization means Docker images run on any OCI-compliant runtime: Kubernetes uses containerd/CRI-O (not Docker daemon) to run the same images Docker builds.

---

### 🔩 First Principles Explanation

```
DOCKER ARCHITECTURE:

  Developer machine:
  ┌─────────────────────────────────────────────────────┐
  │ Docker CLI (docker)                                 │
  │    ↕ REST API (Unix socket: /var/run/docker.sock)   │
  │ Docker Daemon (dockerd)                             │
  │    ↕                                                │
  │ containerd (CNCF container runtime)                 │
  │    ↕                                                │
  │ runc (OCI runtime - actual container creation)      │
  │    ↕                                                │
  │ Linux kernel: namespaces + cgroups                  │
  └─────────────────────────────────────────────────────┘

KEY DOCKER COMMANDS:

  IMAGE MANAGEMENT:
  docker pull nginx:1.24             # download image from registry
  docker images                      # list local images
  docker rmi nginx:1.24              # remove image
  docker image prune -a              # remove all unused images

  CONTAINER LIFECYCLE:
  docker run <image>                 # create + start container
  docker run -d <image>              # detached (background)
  docker run --rm <image>            # auto-remove when stopped
  docker run -it <image> bash        # interactive terminal
  docker run -p 8080:80 <image>      # port mapping (host:container)
  docker run -v /host:/container <i> # volume mount
  docker run --name myapp <image>    # named container
  docker run -e KEY=VALUE <image>    # environment variable
  docker run --memory 512m <image>   # memory limit
  docker run --cpus 1.5 <image>      # CPU limit

  docker ps                          # list running containers
  docker ps -a                       # list all containers (including stopped)
  docker stop <id>                   # graceful stop (SIGTERM)
  docker kill <id>                   # immediate kill (SIGKILL)
  docker rm <id>                     # remove stopped container
  docker exec -it <id> bash          # run command in running container
  docker logs <id>                   # view container stdout/stderr
  docker logs -f <id>                # follow (tail -f style)
  docker inspect <id>                # detailed container metadata (JSON)
  docker stats                       # live resource usage (CPU, memory, I/O)

  BUILD:
  docker build -t myapp:1.0 .        # build image from ./Dockerfile
  docker build -t myapp:1.0 -f custom.Dockerfile .
  docker build --no-cache .          # force rebuild (ignore layer cache)

  REGISTRY:
  docker login registry.example.com
  docker tag myapp:1.0 registry.example.com/org/myapp:1.0
  docker push registry.example.com/org/myapp:1.0
  docker pull registry.example.com/org/myapp:1.0

DOCKER NETWORKING:

  Default networks:
  - bridge: default; containers get 172.17.x.x; communicate via Docker DNS
  - host: container shares host network namespace (no isolation; faster)
  - none: no networking

  Custom bridge network (preferred):
  docker network create my-network
  docker run --network my-network --name db postgres:15
  docker run --network my-network --name app myapp:1.0
  # app container can reach db by hostname: postgres://db:5432/

  Port mapping: -p 8080:80
  → traffic to host port 8080 → container port 80
  → container is NOT directly accessible from outside without port mapping

DOCKER VOLUMES:

  Types:
  1. Named volume: docker run -v mydata:/app/data
     Managed by Docker; stored at /var/lib/docker/volumes/
     Persists across container restarts/recreation

  2. Bind mount: docker run -v /host/path:/app/data
     Maps host directory into container
     Used for development (live code reload)

  3. tmpfs: docker run --tmpfs /app/tmp
     In-memory; not persisted; for secrets/temp files

DOCKER IMAGE LAYERS (cache optimization):

  Dockerfile:
  FROM node:18-alpine          ← layer 1: pulled from registry (rarely changes)
  WORKDIR /app
  COPY package*.json ./        ← layer 2: only if package.json changes
  RUN npm ci                   ← layer 3: expensive; cached if layer 2 unchanged
  COPY . .                     ← layer 4: changes every build
  CMD ["node", "server.js"]

  Build order matters for cache:
  ✅ COPY package.json FIRST → RUN npm install → COPY source code
  → npm install only re-runs when package.json changes
  ❌ COPY . . FIRST → npm install every build (source changed = cache miss)
```

---

### ❓ Why Does This Exist (Why Before What)

Before Docker, using Linux containers required deep kernel expertise (LXC, manual namespace/cgroup configuration). Docker packaged these capabilities into a developer-friendly CLI and introduced the Dockerfile — a simple, readable format for defining how to build an image. This democratized containers: any developer could containerize their app in 30 minutes. Docker's influence extends beyond its own tools: it established the OCI image spec and runtime spec (open standards), meaning Docker-built images run on all Kubernetes-compatible runtimes today.

---

### 🧠 Mental Model / Analogy

> **Docker is the standardized shipping container system for software**: before containers (the physical kind), cargo was loaded piece by piece — inconsistent and slow. The steel shipping container standardized everything: any ship, any crane, any port. Docker does the same for software: a Docker image is the standardized container, Docker Hub is the global shipping port, and the Docker CLI is the crane that loads/unloads. `docker build` seals the container; `docker push` ships it to the port; `docker pull + run` unloads and deploys it anywhere.

---

### ⚙️ How It Works (Mechanism)

```
docker run -d -p 8080:80 nginx:1.24

1. CLI sends request to dockerd via Unix socket
2. dockerd checks local image cache: nginx:1.24 present? No → pull
3. Pull: contact Docker Hub → download manifest → download layers
4. containerd creates container spec (OCI spec JSON)
5. runc executes: unshare(CLONE_NEWPID|CLONE_NEWNET|...) → new namespaces
6. overlay2 driver mounts image layers (read-only) + new writable layer
7. veth pair created: container eth0 ↔ host docker0 bridge
8. iptables rules added: host port 8080 → container IP:80
9. nginx process started as PID 1 in container
10. Container ID returned to CLI

Result: nginx running; reachable at localhost:8080 on the host
```

---

### 🔄 How It Connects (Mini-Map)

```
Need to build, run, and distribute containers
        │
        ▼
Docker ◄── (you are here)
(CLI + daemon; build + run + push/pull)
        │
        ├── Container: the concept Docker implements
        ├── Docker Image: the artifact Docker builds and distributes
        ├── Dockerfile: the build instruction file
        ├── Docker Compose: multi-container local dev/test orchestration
        ├── Container Registry: where Docker images are stored and shared
        └── Kubernetes: uses Docker-built images; does not use Docker daemon at runtime
```

---

### 💻 Code Example

```bash
# Complete Docker workflow: build → run → push

# 1. Build image
docker build -t myapp:1.0 .

# 2. Test locally
docker run --rm -p 8080:3000 -e NODE_ENV=production myapp:1.0

# 3. Inspect
docker ps
docker logs <container-id>
docker exec -it <container-id> sh   # debug inside running container

# 4. Tag for registry
docker tag myapp:1.0 registry.example.com/team/myapp:1.0
docker tag myapp:1.0 registry.example.com/team/myapp:latest

# 5. Push to registry
docker login registry.example.com
docker push registry.example.com/team/myapp:1.0
docker push registry.example.com/team/myapp:latest

# 6. Pull and run on another machine / in CI
docker pull registry.example.com/team/myapp:1.0
docker run -d -p 8080:3000 registry.example.com/team/myapp:1.0

# Cleanup
docker stop $(docker ps -q)          # stop all running containers
docker system prune -af              # remove ALL stopped containers + dangling images
```

---

### ⚠️ Common Misconceptions

| Misconception                                 | Reality                                                                                                                                                                                                                                                                                                                     |
| --------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Kubernetes uses Docker                        | Kubernetes deprecated the Docker daemon in K8s 1.20 (removed in 1.24). Kubernetes uses **containerd** or **CRI-O** directly (both OCI-compliant). Docker-built images still run on Kubernetes — the image format is standardized (OCI). Only the runtime changed. `docker build` is still the standard way to build images. |
| Docker is always running as a service         | `dockerd` (Docker daemon) runs as root. This is a security concern — access to the Docker socket (`/var/run/docker.sock`) is effectively root access on the host. Rootless Docker mode and Podman (daemonless, rootless) address this for development use.                                                                  |
| `docker stop` immediately kills the container | `docker stop` sends **SIGTERM** to PID 1 (allowing graceful shutdown) and waits 10 seconds (default timeout). If the process hasn't stopped, it sends **SIGKILL**. Ensure your app handles SIGTERM for graceful shutdown (close DB connections, finish in-flight requests).                                                 |

---

### 🔥 Pitfalls in Production

```
PITFALL: docker.sock mount in container = root access

  # ❌ DANGEROUS: Jenkins/build container mounting docker socket
  docker run -v /var/run/docker.sock:/var/run/docker.sock jenkins/jenkins
  # Any process inside that container can run arbitrary docker commands
  # = equivalent to giving root access to the host

  # ✅ ALTERNATIVES:
  # 1. kaniko: build Docker images inside Kubernetes without docker daemon
  # 2. BuildKit with --rootless
  # 3. Separate build machine with tightly controlled Docker access
  # 4. AWS CodeBuild / Cloud Build (managed build environments)

PITFALL: not setting resource limits → one container starves others

  # ❌ No limits: one container can consume all host CPU/memory
  docker run myapp  # no --memory or --cpus

  # ✅ Always set limits in production
  docker run \
    --memory 512m \          # hard memory limit (OOM kill if exceeded)
    --memory-reservation 256m \  # soft limit (scheduler preference)
    --cpus 1.0 \             # limit to 1 CPU core
    myapp
  # In Kubernetes: resources.limits and resources.requests in Pod spec
```

---

### 🔗 Related Keywords

- `Container` — the concept Docker implements
- `Docker Image` — immutable artifact built by `docker build`
- `Dockerfile` — the build instructions file
- `Docker Compose` — multi-container local orchestration
- `Container Registry` — centralized image storage (Docker Hub, ECR, GCR, ACR)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY DOCKER COMMANDS:                                     │
│ docker build -t name:tag .   ← build image              │
│ docker run -d -p host:cont   ← run container            │
│ docker ps / logs / exec -it  ← manage + debug           │
│ docker push/pull             ← registry I/O             │
│ docker system prune -af      ← cleanup                  │
├──────────────────────────────────────────────────────────┤
│ ARCHITECTURE: CLI → dockerd → containerd → runc → kernel│
│ K8s: uses containerd directly (not dockerd)             │
│ Images: OCI standard → run on any OCI runtime           │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Docker Desktop on Mac runs Linux containers inside a Linux VM (HyperKit or Apple Virtualization Framework). This means there are actually TWO layers of virtualization when running a container on Mac: the Linux VM (hypervisor), then Linux namespaces/cgroups inside the VM. What are the performance implications? Why does file I/O between Mac filesystem and container volumes feel slow? What optimizations (virtiofs, VirtioFS, gRPC-FUSE) attempt to solve this?

**Q2.** The Docker daemon (`dockerd`) runs as root, and the Docker socket is effectively a privilege escalation vector. Rootless Docker and Podman both attempt to solve this. Compare the approaches: rootless Docker (still has a user-level daemon) vs Podman (daemonless — each `podman run` is a direct fork-exec without a daemon). What security guarantees does each provide? What features are unavailable in rootless mode?
