---
layout: default
title: "Podman"
parent: "Containers"
nav_order: 848
permalink: /containers/podman/
number: "0848"
category: Containers
difficulty: ★★★
depends_on: Container, Docker, Linux Namespaces, Cgroups, OCI Standard
used_by: Buildah, Container Security, Container Orchestration
related: Docker, containerd, Buildah, Docker BuildKit, Container Security
tags:
  - containers
  - docker
  - security
  - advanced
  - linux
---

# 848 — Podman

⚡ TL;DR — Podman is a daemonless, rootless OCI container engine that runs containers as the current user — eliminating the privileged Docker daemon security risk.

| #848 | Category: Containers | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Container, Docker, Linux Namespaces, Cgroups, OCI Standard | |
| **Used by:** | Buildah, Container Security, Container Orchestration | |
| **Related:** | Docker, containerd, Buildah, Docker BuildKit, Container Security | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
The Docker daemon runs as root on the host. When a developer runs `docker run -v /etc:/etc ubuntu bash` — even accidentally — they get root access to the host's `/etc`. The Docker socket (`/var/run/docker.sock`) is effectively a root shell: anyone who can write to it has root on the host. In CI/CD systems, mounting the Docker socket to build images inside containers (Docker-in-Docker) means every CI job has the potential to escalate to host root. In a shared development server, every user with Docker access has implicit root access.

**THE BREAKING POINT:**
A daemon running as root is a single point of privilege escalation. Any exploit in the Docker daemon — or any misuse of Docker capabilities — provides root on the host. This is not a theoretical concern: it is the reason Kubernetes removed the Docker daemon from its runtime stack and why regulated industries resist Docker on production servers.

**THE INVENTION MOMENT:**
This is exactly why Podman (Pod Manager) was developed by Red Hat — a container engine that is architecturally daemonless and runs containers as the user who invoked it (rootless), using user namespaces to provide full container functionality without any process running as root.

---

### 📘 Textbook Definition

**Podman** is an open-source, OCI-compliant container engine developed by Red Hat that provides a Docker-compatible CLI while being architecturally different in two key ways: it is **daemonless** (no persistent background process — each `podman run` command directly forks a container process via `conmon`) and **rootless** (containers run as the invoking user within a user namespace, using `newuidmap`/`newgidmap` for UID mapping, without requiring root privileges). Podman is fully OCI-compliant, builds and runs OCI images identically to Docker, and ships as the default container tool on RHEL/Fedora/CentOS. It also supports `pod` primitives natively (akin to Kubernetes pods).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Podman is Docker without a daemon running as root — you get the same container functionality, but no privileged always-on daemon listening for commands.

**One analogy:**
> Running Docker is like having a 24/7 security guard who has master keys to the entire building. Every time a tenant needs something (start a container), they ask the guard (daemon). The guard has root access to everything. If someone tricks the guard, they have the keys to the whole building. Podman removes the master-key guard entirely. Each tenant (user) has their own limited key that only works on their own door (containers run as that user). No omnipotent intermediary. No master key to steal.

**One insight:**
The "rootless" property isn't just about not running as root. It's about the blast radius of a container escape. If an attacker escapes a Docker container, they are root on the host. If they escape a Podman rootless container, they are the invoking user — typically a developer with no special privileges. Same container isolation failure; completely different impact.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. No daemon = no long-running privileged process = no persistent attack surface.
2. Rootless containers: the container's root (UID 0 inside) is mapped to the host user's UID (not host root).
3. OCI compliance: same images, same runtime behaviour as Docker.

**DERIVED DESIGN:**

**Daemonless architecture:**
When you run `podman run nginx`: Podman directly calls the OCI runtime (runc or crun) without routing through a daemon. `conmon` (container monitor) is a small C process that acts as the container's parent for signal handling and log collection — it is short-lived and per-container, not a persistent daemon.

```
┌──────────────────────────────────────────────────────────┐
│   Docker Architecture vs Podman Architecture             │
├───────────────────────┬──────────────────────────────────┤
│  DOCKER               │  PODMAN                          │
├───────────────────────┼──────────────────────────────────┤
│  Client: docker CLI   │  Client: podman CLI              │
│      (user space)     │      (user space)                │
│       ↓               │       ↓                          │
│  dockerd (root daemon)│  conmon (per-container, user)    │
│       ↓               │       ↓                          │
│  containerd (root)    │  runc/crun (user namespace)      │
│       ↓               │                                  │
│  runc (root)          │                                  │
│                       │                                  │
│  ATTACK SURFACE:      │  ATTACK SURFACE:                 │
│  Docker socket (root) │  None (no socket, no daemon)     │
└───────────────────────┴──────────────────────────────────┘
```

**Rootless user namespace mapping:**
```
Inside container          Host UID map
  UID 0 (root)    ←→   UID 100000 (unprivileged user range)
  UID 1           ←→   UID 100001
  UID 1000        ←→   UID 101000
```
The container's "root" is UID 100000 on the host — a normal unprivileged user with no special capabilities.

**Pod support:**
Podman natively supports pods — groups of containers sharing network/IPC namespaces, identical to Kubernetes pods. `podman pod create`, `podman pod start` — generating Kubernetes-compatible YAML is built in: `podman generate kube <pod>`.

**THE TRADE-OFFS:**

**Gain:** No privileged daemon, rootless execution, smaller attack surface, Kubernetes-compatible pod semantics.

**Cost:** No built-in container orchestration (use Kubernetes). Some Docker Compose features require `podman-compose`. Rootless containers have limitations (some privileged operations unavailable). Windows/Mac support is more limited than Docker Desktop.

---

### 🧪 Thought Experiment

**SETUP:**
A CI system mounts `/var/run/docker.sock` into CI job containers to allow Docker image builds (common pattern). A malicious library in a build dependency includes:
`import socket; socket.connect('/var/run/docker.sock'); docker_run('root shell')`

**WHAT HAPPENS WITH DOCKER DAEMON:**
The malicious library connects to the Docker socket (running as root). It spawns a privileged container: `docker run --privileged -v /:/host ubuntu chroot /host bash`. This is a full host root shell. The CI server is compromised.

**WHAT HAPPENS WITH PODMAN (ROOTLESS):**
The CI job runs as a non-privileged user. Podman has no daemon and no socket to connect to. The malicious library cannot escalate: it can only do what the current user can do. Even a full container escape gives the attacker the CI user's access — no host root. Blast radius contained.

**THE INSIGHT:**
Rootless containers limit the "blast radius" of a security incident. The security model: "what is the worst an attacker can do if they escape the container?" With Docker: host root. With Podman rootless: current user's privileges. This single property justifies Podman for security-conscious environments.

---

### 🧠 Mental Model / Analogy

> Podman's daemonless design is like replacing a centralised building security control room (Docker daemon) with individual smart locks on each room (per-container processes). The control room has master access to every room — if compromised, every room is at risk. Smart locks have no centralised control: each room works independently, and compromising one lock gives access only to that room.

Mapping:
- "Centralised control room" → Docker daemon (root, persistent, socket-accessible)
- "Smart lock" → conmon + container process (per-user, per-container)
- "Master access" → Docker socket → root shell
- "Compromising one lock → one room only" → escaping one rootless container → current user only
- "No centralised control" → no daemon → no single point of failure

Where this analogy breaks down: smart locks can still be broken physically. Rootless containers can still be escaped via kernel vulnerabilities. The advantage is blast radius, not perfect containment.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Podman is an alternative to Docker that doesn't need a special always-running background service to work. When you run a container with Podman, it's like running any normal program — no special permissions needed. This makes it safer and simpler.

**Level 2 — How to use it (junior developer):**
Podman has an almost identical CLI to Docker. Replace `docker` with `podman` in most commands: `podman pull nginx`, `podman run -d nginx`, `podman ps`, `podman build -t myapp .`. For Docker Compose compatibility: install `podman-compose` or use `podman play kube` with Kubernetes YAML. On RHEL/Fedora/CentOS, Podman is installed by default.

**Level 3 — How it works (mid-level engineer):**
Podman uses `newuidmap` and `newgidmap` to map UIDs between the container and host in rootless mode. The `shadowutils` package provides the `/etc/subuid` and `/etc/subgid` ranges that define which host UIDs are allocated to each user's containers. Storage is managed by `containers/storage` in the user's home directory (`~/.local/share/containers/`). Image pulls use `containers/image` for OCI registry interaction. No socket is required — `podman` is a CLI that directly orchestrates `runc`/`crun` via systemd or direct fork. Podman integrates with systemd for container lifecycle management (`podman generate systemd` creates unit files).

**Level 4 — Why it was designed this way (senior/staff):**
The daemonless design was a deliberate security and simplicity choice. Red Hat's analysis: a persistent daemon running as root is a liability in enterprise environments where root access is audited, restricted, and avoided. The systemd integration was a natural consequence: if there's no daemon to manage containers, systemd (which manages all services on RHEL) should manage containers instead. Podman's pod model (native `podman pod` commands) was designed to produce Kubernetes-compatible YAML directly, enabling a workflow where developers run pods locally with Podman and deploy them to Kubernetes with minimal rewriting. The `podman generate kube` and `podman play kube` commands make this bidirectional. This "local development to production" workflow is Podman's competitive differentiator against Docker Desktop.

---

### ⚙️ How It Works (Mechanism)

**Container start flow (rootless):**
```
┌──────────────────────────────────────────────────────────┐
│          Podman Rootless Container Start                 │
├──────────────────────────────────────────────────────────┤
│  podman run nginx                                        │
│       ↓                                                  │
│  podman CLI: resolves image from local/registry store    │
│       ↓                                                  │
│  OCI spec generated (config.json)                        │
│       ↓                                                  │
│  fork conmon (container monitor, user UID)               │
│       ↓                                                  │
│  conmon: fork runc/crun                                  │
│       ↓                                                  │
│  runc: unshare user namespace                            │
│    → newuidmap: map container UID 0 → host UID 100000    │
│    → unshare net, pid, mnt, uts namespaces               │
│    → setup cgroups (user-delegated cgroup v2)            │
│    → exec container process                              │
│    (container root = host UID 100000, NOT host root)     │
└──────────────────────────────────────────────────────────┘
```

**Rootless storage:**
- Images stored: `~/.local/share/containers/storage/`
- Network (slirp4netns or pasta): user-space network stack replacing root-required operations
- No `/var/run/docker.sock` equivalent by default
- Optional socket: `podman system service --time=0 unix://tmp/podman.sock` (for Docker API compatibility)

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Developer: podman run -d nginx ← YOU ARE HERE
  → Podman: resolve image → pull if needed
  → fork conmon (user process, no root)
  → conmon: fork runc with user namespace mapping
  → container starts as unprivileged process (UID 100000 on host)
  → nginx serves on port 80 (pod network, user-space)
```

**FAILURE PATH:**
```
Rootless limitation: requires port < 1024
  → podman run -p 80:80 nginx
  → Error: permission denied (port 80 requires root on IP stack)
  → Fix: use port >= 1024 in rootless mode
    podman run -p 8080:80 nginx
  → OR: enable rootless port binding: net.ipv4.ip_unprivileged_port_start=80
```

**WHAT CHANGES AT SCALE:**
Podman scales horizontally by design — no daemon bottleneck. At 1,000 concurrent containers on a server (build farms, test runners), Podman's per-process model distributes load naturally; the Docker daemon would be a single bottleneck coordinating all 1,000. For container orchestration at scale, Podman defers to Kubernetes — it is not designed as an orchestrator.

---

### 💻 Code Example

**Example 1 — Basic Podman usage (Docker CLI equivalent):**
```bash
# Pull and run (identical to Docker)
podman pull nginx:1.25
podman run -d --name web -p 8080:80 nginx:1.25
podman ps
podman logs web
podman stop web
podman rm web

# Build an image (identical to Docker)
podman build -t myapp:latest .
```

**Example 2 — Rootless verification:**
```bash
# Run as non-root user
whoami   # Output: alice (UID 1000)

podman run --rm alpine id
# Inside container: uid=0(root) gid=0(root)

# But on the host:
ps aux | grep conmon
# alice    100000  0.0  0.0 ... conmon
# Container "root" is UID 100000 on the host
```

**Example 3 — Pod creation and Kubernetes YAML generation:**
```bash
# Create a pod (like a K8s pod)
podman pod create --name mypod -p 8080:80

# Add containers to the pod
podman run -d --pod mypod --name nginx nginx:1.25
podman run -d --pod mypod --name metrics prom/prometheus

# Generate Kubernetes YAML from running pod
podman generate kube mypod > mypod.yaml

# Deploy the same pod to Kubernetes
kubectl apply -f mypod.yaml
```

**Example 4 — Docker socket compatibility (for tools that need Docker API):**
```bash
# Start Podman's Docker-compatible socket
podman system service --time=0 unix:///tmp/podman.sock &

# Use Docker CLI against Podman socket
DOCKER_HOST=unix:///tmp/podman.sock docker ps
DOCKER_HOST=unix:///tmp/podman.sock docker build -t myapp:latest .
```

---

### ⚖️ Comparison Table

| Feature | Docker | Podman | containerd |
|---|---|---|---|
| Daemon required | Yes (root) | No | Yes (root) |
| Rootless containers | Partial (experimental) | Yes (native) | Via user namespace flags |
| CLI familiarity | Docker CLI | Docker-compatible CLI | `ctr` (low-level) |
| Pod support | Via Compose | Native | Via Kubernetes |
| Kubernetes integration | via dockershim (removed) | `podman play kube` | Native (CRI) |
| Build images | Yes (BuildKit) | Yes (Buildah integration) | No (not a builder) |
| Windows/Mac | Docker Desktop | Podman Desktop (less mature) | No |
| Best For | Developer workstations | Security-conscious envs, RHEL | Kubernetes runtime |

How to choose: Docker for developer workstations where tooling ecosystem matters. Podman for Linux servers, RHEL/Fedora environments, security-sensitive workloads, and teams that want rootless containers. containerd for Kubernetes runtime.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Podman containers are completely isolated from the host" | Rootless improves the isolation model but doesn't eliminate kernel attack surface. A kernel exploit can still escalate from UID 100000 to UID 0 on the host. |
| "Podman is slower than Docker because it's daemonless" | Podman is typically faster for single-container operations (no daemon coordination overhead). For high-frequency container creation, the fork overhead per command is slightly higher than daemon-based systems. |
| "Podman is a drop-in Docker replacement for Kubernetes" | Podman is not a Kubernetes runtime — it doesn't implement CRI. For Kubernetes, use containerd or CRI-O. Podman is for developer workstations and non-Kubernetes container execution. |
| "Rootless means the container can't do anything" | Rootless is about host privilege, not container capability. Inside the container, processes run as root (relative to the user namespace), can install packages, modify files, read/write within their namespace — normal container operations work fine. |
| "You can't run Podman on macOS/Windows without a VM" | `podman machine` creates a lightweight VM (akin to Docker Desktop's VM) to run Linux containers on macOS/Windows. The experience is slightly more manual than Docker Desktop but fully functional. |

---

### 🚨 Failure Modes & Diagnosis

**Rootless network port conflict (ports < 1024)**

**Symptom:**
`podman run -p 80:80 nginx` fails with `permission denied: bind: permission denied`.

**Root Cause:**
Binding to ports < 1024 requires `CAP_NET_BIND_SERVICE` or root access on Linux. Rootless Podman runs as an unprivileged user.

**Diagnostic Command / Tool:**
```bash
sysctl net.ipv4.ip_unprivileged_port_start
# Default: 1024 (ports below this require root)
```

**Fix:**
```bash
# Option 1: Use port >= 1024 (recommended)
podman run -p 8080:80 nginx

# Option 2: Lower unprivileged port limit (system-wide change)
sudo sysctl -w net.ipv4.ip_unprivileged_port_start=80

# Option 3: Use rootful Podman for this specific container
sudo podman run -p 80:80 nginx
```

**Prevention:**
Design applications to use ports >= 1024 internally and rely on load balancers/ingress for ports 80/443.

---

**Rootless storage permission issues**

**Symptom:**
`podman pull` or `podman build` fails with `permission denied` accessing storage. Or different users see different images.

**Root Cause:**
Podman rootless stores images per-user in `~/.local/share/containers/`. Different users have isolated storage. A CI user's images are not visible to other users.

**Diagnostic Command / Tool:**
```bash
# Check storage location
podman info | grep -A3 "graphRoot"

# Check subuid/subgid allocation
grep $(whoami) /etc/subuid /etc/subgid
```

**Fix:**
For shared CI environments, use rootful Podman (`sudo podman`) or configure shared storage as a workaround. Prefer CI-per-user isolated builds.

**Prevention:**
Design CI pipelines to use per-job isolated rootless contexts. Treat Podman storage as user-local, not system-global.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Docker` — Podman is designed as a Docker alternative; understand Docker first
- `Linux Namespaces` — user namespaces are the key mechanism for Podman rootless containers
- `OCI Standard` — Podman is OCI-compliant; images built with Docker run on Podman unchanged

**Builds On This (learn these next):**
- `Buildah` — Podman's companion for building images; both are daemonless and rootless
- `Container Security` — rootless containers dramatically improve the container security model
- `Container Orchestration` — Podman generates Kubernetes YAML, bridging local dev to production

**Alternatives / Comparisons:**
- `Docker` — full-featured container platform with daemon; Docker's counterpart
- `containerd` — Kubernetes runtime (not developer tool); different use case to Podman
- `Docker BuildKit` — Docker's build engine; Podman uses Buildah for the equivalent functionality

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Daemonless, rootless OCI container engine │
│              │ with Docker-compatible CLI                │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Docker daemon runs as root — single point │
│ SOLVES       │ of privilege escalation on the host       │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Container "root" (UID 0 inside) maps to   │
│              │ unprivileged UID on host — escape blast    │
│              │ radius: current user only, not host root  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Linux servers, RHEL/Fedora, security-     │
│              │ sensitive envs, shared build systems      │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Kubernetes runtime (use containerd/CRI-O) │
│              │ or teams needing full Docker Desktop UX   │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Security (no root daemon) vs ecosystem    │
│              │ maturity + Docker Desktop convenience     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Podman: containers run as you, not as    │
│              │  root — because your daemon shouldn't     │
│              │  have master keys to the whole server"    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Buildah → Container Security →            │
│              │ Kubernetes Architecture                   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A company runs a shared CI build server where 20 developers have login access. Half the team uses Docker (with regular Docker daemon); the other half uses Podman (rootless). A malicious insider with a normal developer account runs `podman run --rm -v /:/host alpine chroot /host su -`. Trace step-by-step what happens in the rootless case: which process runs, what UID it has on the host, what the chroot does inside the user namespace, and whether the attacker successfully gains host root access. Contrast with the Docker daemon case.

**Q2.** Your company is evaluating whether to replace Docker with Podman for all developer workstations. Make the case FOR the migration from a security and operational perspective, then make the case AGAINST from a developer experience and tooling ecosystem perspective. Which specific developer workflows are most disrupted by the migration, and what is your recommendation for a phased adoption strategy?

