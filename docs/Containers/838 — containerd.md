---
layout: default
title: "containerd"
parent: "Containers"
nav_order: 838
permalink: /containers/containerd/
number: "0838"
category: Containers
difficulty: ★★★
depends_on: Docker, Container, Linux Namespaces, Cgroups, OCI Standard
used_by: Container Runtime Interface (CRI), Kubernetes Architecture, kubelet
related: Docker, Container Runtime Interface (CRI), OCI Standard, Podman, Container Orchestration
tags:
  - containers
  - docker
  - internals
  - kubernetes
  - advanced
---

# 838 — containerd

⚡ TL;DR — containerd is the industry-standard container runtime daemon that manages the full container lifecycle — from image pull to running container — without the overhead of the full Docker daemon.

| #838 | Category: Containers | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Docker, Container, Linux Namespaces, Cgroups, OCI Standard | |
| **Used by:** | Container Runtime Interface (CRI), Kubernetes Architecture, kubelet | |
| **Related:** | Docker, Container Runtime Interface (CRI), OCI Standard, Podman, Container Orchestration | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
In 2016, Kubernetes uses the Docker daemon as its container runtime. To run a single container, Kubernetes must talk to `dockerd` (the Docker daemon), which wraps `containerd` (Docker's internal runtime), which calls `runc` (the OCI runtime). The chain is: `kubelet → dockershim → dockerd → containerd → runc`. Three layers of indirection. The Docker daemon runs as root, manages its own networking, volumes, build tooling, and a REST API — none of which Kubernetes needs. When the Docker daemon crashes or restarts, all managed containers are affected. A security vulnerability in any Docker component affects Kubernetes clusters.

**THE BREAKING POINT:**
Kubernetes maintainers need a minimal, stable, auditable runtime that focuses exclusively on what Kubernetes needs: pull images, unpack them, create containers, manage their lifecycle. The full Docker stack is too large, too coupled, and too prone to cascading failures from unrelated features.

**THE INVENTION MOMENT:**
This is exactly why containerd was extracted from Docker in 2017 and donated to the CNCF — a focused, production-grade container runtime that does one thing well: manage containers. It is the "engine" without the "car body." Kubernetes adopted it as the default runtime in 1.24 when dockershim was removed.

---

### 📘 Textbook Definition

**containerd** is an industry-standard, CNCF-graduated container runtime daemon (`containerd`) that manages: image pulling and storage (OCI and Docker image formats), container creation, execution, and lifecycle management (start, pause, resume, stop, delete), snapshotting (layer management for images and containers), low-level execution delegation to an OCI-compliant runtime (default: `runc`), and a content store for immutable blobs (image layers, configs). It exposes a gRPC API and implements the Kubernetes Container Runtime Interface (CRI) via the `cri` plugin. It does NOT manage networking, volumes, or image builds — those are handled by higher-level tools.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
containerd is the container engine underneath Docker and Kubernetes — the part that actually creates and runs containers.

**One analogy:**
> A car has an engine and a body. The body has doors, seats, a dashboard, and air conditioning. The engine is what actually makes the car move. Docker is the full car — body and engine together, designed for developer experience. containerd is just the engine — extracted and optimised for running containers at scale, without the weight of doors and air conditioning that production systems don't need. Kubernetes doesn't need a car dashboard. It needs an engine.

**One insight:**
Most developers think they are using Docker in production — but from Kubernetes 1.24 onward, Kubernetes uses containerd (or CRI-O) directly. Docker images still work perfectly because containerd is fully OCI-compliant. The "removal of Docker" from Kubernetes was actually the removal of the unnecessary outer layers — the engine itself (containerd) was always there underneath Docker.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. A container runtime's core responsibility is: pull image, unpack layers, create a namespaced process group, manage its lifecycle.
2. Resource management (cgroups, namespaces) is the kernel's job — the runtime is the userspace orchestrator that invokes it.
3. Stability of the runtime is more critical than feature richness — a crashed runtime kills all managed containers.

**DERIVED DESIGN:**

containerd is structured as a plugin architecture around a set of core services:

```
┌──────────────────────────────────────────────────────────┐
│              containerd Architecture                     │
├──────────────────────────────────────────────────────────┤
│  Clients                                                 │
│  kubelet (CRI) │ docker (grpc) │ ctr (CLI)               │
│       │              │               │                   │
│       └──────────────┴───────────────┘                   │
│                   containerd gRPC API                    │
├──────────────────────────────────────────────────────────┤
│  Core Services                                           │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │ Image Store │  │  Snapshotter │  │ Content Store  │  │
│  │ (metadata)  │  │  (layers)    │  │ (blobs/SHA256) │  │
│  └─────────────┘  └──────────────┘  └────────────────┘  │
├──────────────────────────────────────────────────────────┤
│  Runtime Plugin                                          │
│  ┌──────────────────────────────────────────────────┐    │
│  │  containerd-shim-runc-v2  (per-container)        │    │
│  │       ↓                                          │    │
│  │  runc (OCI low-level runtime)                    │    │
│  └──────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────┘
```

**Key architectural decisions:**

**Shim model:** containerd spawns a per-container `containerd-shim` process that acts as the container's parent process. If containerd itself restarts, the shim keeps the container alive. This is why containers survive containerd restarts — a critical production property.

**Snapshotter:** Instead of Docker's layered graph driver, containerd uses a pluggable snapshotting interface. The default is overlayfs on Linux. Each snapshot represents a layer's filesystem view. Containers get a read-write layer on top of read-only base snapshots.

**Content store:** All blobs (image layers, configs, manifests) are stored by SHA256 digest. Content is immutable and deduplicated across all images that share a layer.

**THE TRADE-OFFS:**

**Gain:** Minimal footprint, fast startup, stable under Kubernetes load, survivable through daemon restarts.

**Cost:** No built-in image build capability, no Docker Compose support, minimal developer UX. Intended for orchestrator consumption, not direct human use.

---

### 🧪 Thought Experiment

**SETUP:**
Your Kubernetes cluster has 500 pods. The container runtime is the full Docker daemon. During a peak traffic event, the Docker daemon processes a large image build request from a developer (who accidentally logged into a cluster node and ran `docker build`). The build consumes 4GB of RAM and significant CPU.

**WHAT HAPPENS WITHOUT containerd (full Docker daemon):**
The Docker daemon is resource-shared between cluster workloads and the developer's build. Memory pressure triggers OOM events. The daemon's metadata database (bolt.db) becomes a contention point. The daemon pauses container operations briefly. Kubernetes liveness probe timeouts cascade to pod restarts. A developer typo causes a production incident.

**WHAT HAPPENS WITH containerd:**
containerd has no build capability. A developer cannot accidentally run `docker build` on a cluster node using containerd. The runtime exposes only what Kubernetes needs. Build tooling (Kaniko, BuildKit) runs in dedicated containers with resource limits. The cluster runtime surface is minimal and auditable.

**THE INSIGHT:**
Minimalism is a security and stability property. A runtime that cannot build images cannot be exploited through image-build attack vectors. A runtime with a small surface area has fewer failure modes.

---

### 🧠 Mental Model / Analogy

> containerd is like a professional sous chef compared to a home cook. A home cook (Docker) does everything: buys groceries, preps ingredients, cooks, plates, serves, and washes up. Efficient for one person cooking dinner. A professional sous chef (containerd) executes one job with ruthless precision: prep and cook, nothing else. In a restaurant kitchen running 500 orders per night, specialisation and focus are what make the operation work.

Mapping:
- "Home cook" → Docker daemon — full stack, developer-friendly
- "Professional sous chef" → containerd — single-purpose, high-performance
- "Restaurant kitchen (500 orders/night)" → Kubernetes cluster (large scale)
- "Buying groceries" → image building — NOT containerd's job
- "Executing the recipe" → running the container — exactly containerd's job
- "Head chef calling orders" → kubelet sending CRI requests

Where this analogy breaks down: a sous chef doesn't survive independently if the head chef disappears. containerd's shim model means containers survive containerd restarts — a property the analogy doesn't capture.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
containerd is the software that actually runs your containers. When Kubernetes decides to start a container, it's containerd that does the work: downloads the image, unpacks it, and starts the process inside. Most people never interact with containerd directly — Kubernetes uses it automatically.

**Level 2 — How to use it (junior developer):**
On Kubernetes nodes, containerd is managed by the operating system and Kubernetes — you rarely need to touch it. For debugging, use `crictl` (the CRI command-line tool): `crictl ps` (list running containers), `crictl logs <id>` (view logs), `crictl pull <image>` (pull an image). On non-Kubernetes systems, use `ctr` (containerd's native CLI): `ctr images pull docker.io/library/nginx:latest`, `ctr run docker.io/library/nginx:latest my-nginx`.

**Level 3 — How it works (mid-level engineer):**
containerd's lifecycle for a container: (1) kubelet calls `RunPodSandbox` via CRI gRPC → containerd creates a sandbox (pause container with shared namespaces); (2) kubelet calls `CreateContainer` → containerd resolves the image from its content store, creates a snapshot via overlayfs (read-write layer on top of image layers), generates an OCI runtime config.json; (3) kubelet calls `StartContainer` → containerd spawns `containerd-shim-runc-v2` which calls `runc create` then `runc start`; (4) the shim process becomes the container's parent, inheriting stdio and forwarding signals. The shim's decoupling from containerd means `systemctl restart containerd` does not kill running containers.

**Level 4 — Why it was designed this way (senior/staff):**
The shim architecture is the key insight: by interposing a per-container shim between containerd and runc, the runtime achieves two critical properties: (a) daemon-free operation — containers outlive containerd restarts; (b) runtime extensibility — different shims enable different execution environments (runc for Linux containers, `containerd-shim-runhcs-v1` for Windows, `kata-containers` shim for VM-isolated containers) without changing containerd itself. The CRI plugin inlines what was previously a separate `cri-containerd` process, reducing latency and removing an IPC hop. The snapshotting abstraction replaced Docker's graph driver architecture — the graph driver was monolithic and hard to swap; snapshotter plugins allow overlayfs, btrfs, ZFS, or remote snapshotter (stargz for lazy image pulling) to be selected per use case.

---

### ⚙️ How It Works (Mechanism)

**Container creation flow (Kubernetes path):**d

```
┌──────────────────────────────────────────────────────────┐
│       containerd Container Creation Flow                 │
├──────────────────────────────────────────────────────────┤
│  kubelet                                                 │
│    │ CRI gRPC: PullImage(nginx:1.25)                     │
│    ↓                                                     │
│  containerd CRI plugin                                   │
│    → content store: fetch layers by SHA256 digest        │
│    → image metadata DB (bolt): store reference           │
│                                                          │
│    │ CRI gRPC: RunPodSandbox()                           │
│    ↓                                                     │
│  containerd creates pause container                      │
│    → allocates network namespace                         │
│    → CNI plugin configures pod network                   │
│                                                          │
│    │ CRI gRPC: CreateContainer(nginx)                    │
│    ↓                                                     │
│  containerd:                                             │
│    → snapshotter: create r/w layer over image            │
│    → generate OCI config.json (Runtime Spec)             │
│                                                          │
│    │ CRI gRPC: StartContainer()                          │
│    ↓                                                     │
│  containerd spawns: containerd-shim-runc-v2              │
│    → runc create (namespaces, cgroups)                   │
│    → runc start (exec entrypoint)                        │
│    → shim now owns the container process                 │
└──────────────────────────────────────────────────────────┘
```

**Shim survival model:**
```
┌──────────────────────────────────────────────────────────┐
│        Why Containers Survive Daemon Restarts            │
├────────────────────────────────────────────────────────┬─┤
│  containerd daemon       containerd-shim (per container)│ │
│  PID 1234                PID 5678                       │ │
│       │                       │                         │ │
│  manages shim lifecycle  owns container stdio + signals  │ │
│       │                       │                         │ │
│  ← restart (PID changes) shim continues running        │ │
│       │                       │                         │ │
│  reconnects to shim      container still running        │ │
└────────────────────────────────────────────────────────┴─┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
kubectl apply deployment → kube-scheduler → node assignment
  → kubelet receives pod spec
  → kubelet: CRI PullImage → containerd ← YOU ARE HERE
  → containerd: fetch layers from registry → content store
  → containerd: create snapshot (overlayfs)
  → containerd: spawn shim → runc → container process
  → container running → kubelet reports Ready
```

**FAILURE PATH:**
```
containerd image pull fails (registry unreachable):
  → CRI: ImagePullBackOff
  → Pod stuck in Pending/ImagePullBackOff
  → kubelet logs: "failed to pull image"
  → fix: check network policy, registry credentials (imagePullSecret)
```

**WHAT CHANGES AT SCALE:**
At scale (1,000+ nodes), containerd's content store per node stores many image layers. Layer deduplication within a node is automatic (shared base images use the same snapshots). Across nodes, each node independently pulls images — no cross-node sharing by default. Lazy pulling (stargz snapshotter / Nydus) addresses the "image pull bottleneck at scale" by streaming only needed layers on first access rather than pulling the full image before startups.

---

### 💻 Code Example

**Example 1 — Basic containerd operations with ctr:**
```bash
# List running containers (native containerd CLI)
ctr containers ls

# List tasks (running processes)
ctr tasks ls

# Pull an image into containerd content store
ctr images pull docker.io/library/nginx:latest

# Run a container (not Kubernetes — direct ctr usage)
ctr run --rm docker.io/library/nginx:latest test-nginx nginx -g "daemon off;"
```

**Example 2 — CRI operations with crictl (Kubernetes):**
```bash
# List all pods managed by containerd via CRI
crictl pods

# List running containers
crictl ps

# Pull an image through CRI
crictl pull nginx:1.25.3

# View container logs
crictl logs <container-id>

# Inspect container details (OCI config, mounts, etc.)
crictl inspect <container-id>
```

**Example 3 — Diagnose containerd status on a node:**
```bash
# Check containerd service status
systemctl status containerd

# View containerd structured logs
journalctl -u containerd -f

# Check containerd configuration
cat /etc/containerd/config.toml

# List all content in the content store (image layers)
ctr content ls

# Check snapshotters
ctr snapshots ls -s overlayfs
```

**Example 4 — Configure containerd (Kubernetes node, config.toml):**
```toml
# /etc/containerd/config.toml
version = 2

[plugins."io.containerd.grpc.v1.cri"]
  # Set CNI binary and config dirs
  [plugins."io.containerd.grpc.v1.cri".cni]
    bin_dir = "/opt/cni/bin"
    conf_dir = "/etc/cni/net.d"

  # Container runtime: use runc
  [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc]
    runtime_type = "io.containerd.runc.v2"
    [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc.options]
      SystemdCgroup = true   # Use systemd cgroup driver (required for kubeadm)

# Private registry mirror
[plugins."io.containerd.grpc.v1.cri".registry.mirrors."my-registry.example.com"]
  endpoint = ["https://my-registry.example.com"]
```

---

### ⚖️ Comparison Table

| Runtime | Docker API | Kubernetes CRI | Daemonless | VM Isolation | Best For |
|---|---|---|---|---|---|
| **containerd** | Via dockerd | Yes (native) | No (daemon) | Via kata shim | Kubernetes default |
| CRI-O | No | Yes (native) | No (daemon) | Via kata shim | OpenShift / minimal K8s |
| Podman | Yes (compatible) | Via CRI-O | Yes | No | Developer machines, rootless |
| Docker Engine | Yes | Via docker-shim (removed K8s 1.24) | No | No | Developer machines |
| Kata Containers | Via shim | Via shim | No | Yes (VM) | Strong isolation workloads |

How to choose: containerd is the default for most Kubernetes distributions (GKE, EKS, AKS, kubeadm). CRI-O is preferred for OpenShift and minimal setups. Podman is excellent for developer machines and rootless container use cases.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Removing Docker from Kubernetes breaks existing images" | containerd is fully OCI-compliant. All Docker-built images are OCI images and run on containerd without modification. |
| "containerd is a Docker replacement for developers" | containerd is designed for automated consumption by orchestrators (Kubernetes). Its CLI (`ctr`) is low-level and not ergonomic. Developers should use Docker or Podman, not containerd directly. |
| "Restarting containerd kills all running containers" | The shim model ensures containers survive containerd restarts. The shim process persists independently and containerd reconnects on restart. |
| "containerd handles networking" | No. containerd delegates networking to CNI plugins (Calico, Cilium, Flannel) and is responsible only for invoking them at container lifecycle points. |
| "containerd is slower than Docker" | containerd is faster — it is Docker without the overhead of the development-focused outer layers (build, compose, API layer). In benchmarks, pod startup times are lower with containerd than with Docker. |

---

### 🚨 Failure Modes & Diagnosis

**containerd daemon crash (pods appear stuck)**

**Symptom:**
Pods show `ContainerCreating` indefinitely. `kubectl describe pod` shows `FailedCreatePodSandBox`. Node shows `NotReady` briefly then recovers.

**Root Cause:**
containerd daemon crash or OOM kill. Because of the shim model, existing running containers are unaffected, but new container creation fails until containerd restarts.

**Diagnostic Command / Tool:**
```bash
# Check containerd status on node
systemctl status containerd

# View crash logs
journalctl -u containerd --since "10 minutes ago"

# Check if daemon is running
pgrep -a containerd
```

**Fix:**
```bash
# Restart containerd
systemctl restart containerd

# If OOM: check node memory pressure
free -h
kubectl describe node <node-name> | grep -A5 Conditions
```

**Prevention:**
Set appropriate resource limits on containerd's host process. Monitor `/proc/<containerd-pid>/status` for memory growth. Ensure nodes have sufficient memory headroom.

---

**Image pull failures (content store corruption)**

**Symptom:**
`crictl pull` fails with `"failed to pull and unpack image"`. New pods cannot start. Existing pods unaffected.

**Root Cause:**
containerd's content store (typically `/var/lib/containerd/`) has a corrupted blob or interrupted download.

**Diagnostic Command / Tool:**
```bash
# Check content store health
ctr content ls

# Check disk usage of containerd data directory
du -sh /var/lib/containerd/

# Check for incomplete blobs
find /var/lib/containerd/io.containerd.content.v1.content/ingest/ -name "*.lock"
```

**Fix:**
```bash
# Clean up incomplete ingests
ctr content prune --async

# Force re-pull (remove cached image and re-pull)
ctr images remove <image>
ctr images pull <image>
```

**Prevention:**
Monitor disk space on nodes — a full disk interrupts in-progress pulls mid-layer and creates corrupted content store entries.

---

**Slow container startup (large image layers)**

**Symptom:**
Pods take 60–300 seconds to transition from `Pending` to `Running`. Node has sufficient resources. Issue is image pull time.

**Root Cause:**
Container images with large layers (multi-GB ML models, monolithic applications) must be fully pulled before the container can start. Default containerd behaviour: pull fully, then start.

**Diagnostic Command / Tool:**
```bash
# Check image pull time in kubelet logs
journalctl -u kubelet | grep "Pulling image"
journalctl -u kubelet | grep "Successfully pulled"

# Time a manual image pull
time crictl pull <large-image>
```

**Fix:**
Consider lazy image pulling via eStargz (stargz snapshotter) or Nydus — these formats enable container start before all layers are downloaded.

**Prevention:**
Reduce image sizes (distroless, multi-stage builds). Pre-pull images on nodes using DaemonSet pre-pullers or node image pre-provisioning in cloud provider managed node groups.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Docker` — Docker popularised containers; containerd was extracted from Docker; understand Docker before containerd
- `Linux Namespaces` — containerd creates namespaced containers; namespaces are the isolation primitive
- `Cgroups` — containerd enforces resource limits via cgroups; understand cgroups to tune container resources
- `OCI Standard` — containerd fully implements OCI Image and Runtime specs; OCI knowledge explains containerd's behaviour

**Builds On This (learn these next):**
- `Container Runtime Interface (CRI)` — CRI is how Kubernetes talks to containerd; the API layer above containerd
- `Kubernetes Architecture` — understanding containerd explains the full kubelet → CRI → containerd → runc stack
- `kubelet` — kubelet is containerd's primary client in Kubernetes; understanding their interaction is essential for debugging

**Alternatives / Comparisons:**
- `Docker` — Docker is containerd + build tooling + developer UX; containerd is the engine Docker shares
- `Podman` — Podman is a daemonless OCI runtime from Red Hat; competing approach to container execution
- `Container Orchestration` — containerd is the runtime layer; orchestration (Kubernetes) sits above it

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ CNCF-graduated container runtime daemon   │
│              │ managing image + container lifecycle      │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Docker daemon too heavy, coupled, and     │
│ SOLVES       │ over-featured for Kubernetes's needs      │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Shim model: containers survive containerd │
│              │ restarts — critical for production safety │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Every Kubernetes cluster (default since   │
│              │ K8s 1.24 removed dockershim)              │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Developer machines wanting full Docker    │
│              │ experience (builds, Compose, desktop UI)  │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Stability + minimal surface vs developer  │
│              │ ergonomics + ecosystem tooling            │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "containerd is the engine Docker contains │
│              │  — extracted, hardened, and given to K8s" │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ CRI → Kubernetes Architecture → kubelet   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** containerd's shim model ensures that running containers survive a containerd daemon restart. But the shim itself is a process with a PID — what happens if the *node* receives a `SIGKILL` and reboots? Trace what occurs to containers managed by containerd on a node that crashes and restarts, how Kubernetes detects and responds to this, and what changes if the node uses `hostPath` volumes on local storage versus network-attached PersistentVolumes.

**Q2.** Your organisation is evaluating whether to use containerd (the default) or Kata Containers (VM-isolated runtime) for a multi-tenant Kubernetes cluster serving untrusted third-party workloads. Both implement the OCI Runtime Spec. What are the precise security boundaries that containerd's Linux namespace isolation provides versus what Kata's VM isolation provides? At what specific failure modes does namespace isolation become insufficient, and at what operational cost does VM isolation come?

