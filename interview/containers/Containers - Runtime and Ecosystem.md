---
title: "Containers - Runtime and Ecosystem"
topic: Containers
subtopic: Runtime and Ecosystem
keywords:
  - containerd
  - OCI Standard
  - Podman
  - Container Runtime Interface
  - Init Containers
  - Sidecar Containers
difficulty_range: hard
status: complete
version: 1
---

# containerd

**TL;DR** - containerd is the industry-standard container runtime that manages the complete container lifecycle (image pull, container creation, execution, storage, networking) and serves as the runtime beneath Docker and Kubernetes.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
Docker was a monolith - one binary doing image building, container running, networking, storage, and CLI. Kubernetes needed only the runtime part but was forced to interface with the entire Docker daemon, adding complexity and overhead.

**THE INVENTION MOMENT:**
"This is exactly why containerd was extracted from Docker as a standalone runtime."

**EVOLUTION:**
Docker (monolithic, 2013) -> containerd extracted (2016) -> donated to CNCF (2017) -> Kubernetes deprecates dockershim (1.20, 2020) -> containerd becomes default K8s runtime (1.24, 2022) -> Docker itself runs containerd underneath.

---

### Textbook Definition

containerd is an industry-standard, CNCF-graduated container runtime that manages the complete container lifecycle on a host system - pulling and storing images, executing containers via OCI-compliant runtimes (runc), managing storage and networking, and providing a gRPC API for orchestrators like Kubernetes.

---

### Understand It in 30 Seconds

**One line:**
containerd is the engine under Docker and Kubernetes that actually runs containers.

**One analogy:**

> If Docker is a car with dashboard, steering wheel, and engine, containerd is just the engine. Kubernetes doesn't need the steering wheel (Docker CLI) or dashboard (Docker Compose) - it just needs the engine to run containers.

**One insight:**
When Kubernetes "deprecated Docker," it didn't deprecate containers. It deprecated the Docker daemon as the intermediary. K8s now talks to containerd directly (via CRI), removing one layer of abstraction and reducing overhead.

---

### How It Works

```
Architecture stack:

Docker CLI            kubectl
    |                     |
Docker Daemon         kubelet
    |                     |
containerd <---------  containerd (via CRI)
    |                     |
runc                    runc
    |                     |
Linux kernel            Linux kernel
(namespaces, cgroups)   (namespaces, cgroups)

containerd responsibilities:
  - Image pull and storage (content store)
  - Container creation and lifecycle
  - Task execution (via OCI runtime - runc)
  - Snapshot management (overlay2)
  - Event system
  - Namespace isolation (containerd namespaces)
```

---

### Complete Picture - End-to-End Flow

**NORMAL FLOW:**
kubelet receives pod spec -> calls containerd via CRI gRPC <- YOU ARE HERE -> containerd pulls image -> creates snapshot -> calls runc to set up namespaces/cgroups -> runc forks container process -> containerd monitors lifecycle

**FAILURE PATH:**
Container crashes -> containerd detects exit -> reports to kubelet via CRI events -> kubelet applies restart policy -> containerd starts new container from same image snapshot

---

### Quick Recall

**If you remember only 3 things:**

1. containerd runs under both Docker AND Kubernetes - it's the actual runtime, Docker is the UX layer on top
2. K8s deprecated Docker (the daemon), not containers - it switched to containerd directly via CRI
3. containerd calls runc (OCI runtime) to create the actual container process with namespaces/cgroups

**Interview one-liner:**
"containerd is the CNCF-graduated container runtime that manages the full lifecycle - image pull, snapshot creation, and process execution via runc - serving as the runtime under both Docker and Kubernetes, which is why 'Docker deprecation in K8s' just meant removing the Docker daemon middleman."

---

### The Surprising Truth

Docker still uses containerd internally. When you run `docker run`, the call chain is: Docker CLI -> Docker daemon -> containerd -> runc. Kubernetes removed Docker to talk to containerd directly. The irony: Docker helped build containerd, donated it to CNCF, and then Kubernetes used it to bypass Docker.

---

### Interview Deep-Dive

**Q1: "Kubernetes deprecated Docker." What actually happened and what does it mean for developers?**

_Why they ask:_ Tests ability to separate hype from reality.

**Answer:**
What actually happened:

- Kubernetes removed `dockershim` - a translation layer between kubelet and Docker daemon
- Previously: kubelet -> dockershim -> Docker daemon -> containerd -> runc
- Now: kubelet -> containerd (via CRI) -> runc
- Removed one layer of indirection

What it means for developers: **Nothing**. Docker images are OCI-compliant. They work on containerd, CRI-O, or any OCI runtime. `docker build` still works. Images built with Docker run on Kubernetes. The deprecation affected only the Kubernetes node runtime, not developer tooling.

What it means for operations: Node configuration changed from Docker to containerd. Docker-specific features (docker.sock mounting, Docker-in-Docker for CI) needed migration. Monitoring tools that used Docker API needed updating to containerd/CRI API.

---

---

# OCI Standard

**TL;DR** - The Open Container Initiative (OCI) defines industry standards for container image format, runtime behavior, and distribution, ensuring images built with any tool run on any compliant runtime.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
Docker was the only way to build and run containers. Vendor lock-in: if Docker changed their format, all tooling breaks. No competition, no interoperability, no standard way to run containers without Docker.

**THE INVENTION MOMENT:**
"This is exactly why the OCI standards were created."

**EVOLUTION:**
Docker-only format (2013-2015) -> OCI founded (2015, by Docker, CoreOS, Google, Red Hat) -> OCI Image Spec v1.0 (2017) -> OCI Runtime Spec v1.0 (2017) -> OCI Distribution Spec v1.0 (2021) -> Artifacts (Helm charts, WASM, SBOMs stored as OCI artifacts).

---

### Textbook Definition

The Open Container Initiative (OCI) is a Linux Foundation project that defines three specifications: Image Spec (format for container images), Runtime Spec (how to run a container from an image), and Distribution Spec (how to push/pull images from registries). Compliance ensures portability across tools and runtimes.

---

### Understand It in 30 Seconds

**One line:**
OCI standards ensure containers are interoperable - build with any tool, run on any runtime.

**One analogy:**

> OCI standards are like USB specifications. Any device (image) with the right connector (OCI format) works with any port (runtime). Before USB (OCI), every manufacturer (Docker) had proprietary connectors.

**One insight:**
OCI didn't just standardize containers - it enabled an ecosystem. Podman, Buildah, Skopeo, and kaniko all exist because of OCI standards. Without them, Docker would be the only tool in the container space.

---

### How It Works

```
OCI Specifications:

1. Image Spec:
   manifest.json -> config + ordered layer digests
   config.json   -> env, cmd, entrypoint, etc.
   layers/       -> filesystem tarballs (gzipped)

2. Runtime Spec:
   config.json -> namespaces, cgroups, mounts,
                  process args, capabilities
   runc (reference implementation) reads this
   and creates the container process

3. Distribution Spec:
   Pull: GET /v2/<name>/manifests/<ref>
   Push: PUT /v2/<name>/manifests/<ref>
   Blob: GET /v2/<name>/blobs/<digest>

Key principle: build anywhere, run anywhere
  docker build -> OCI image -> containerd runs
  buildah bud  -> OCI image -> cri-o runs
  kaniko build -> OCI image -> podman runs
```

---

### Quick Recall

**If you remember only 3 things:**

1. Three specs: Image (format), Runtime (execution), Distribution (registry API)
2. OCI ensures portability: images built with Docker/Buildah/kaniko run on containerd/CRI-O/Podman
3. OCI Artifacts extend the standard beyond containers - Helm charts, WASM modules, and SBOMs stored in OCI registries

**Interview one-liner:**
"OCI defines three standards - image format, runtime behavior, and distribution protocol - ensuring container portability across tools and runtimes. I build with any OCI-compliant tool (Docker, Buildah, kaniko) knowing images run on any compliant runtime (containerd, CRI-O, Podman)."

---

### The Surprising Truth

OCI registries can store ANY artifact, not just container images. Helm charts, WASM modules, machine learning models, and SBOMs are increasingly stored as OCI artifacts in container registries. The registry is becoming a universal artifact store, not just a container image store.

---

---

# Podman

**TL;DR** - Podman is a daemonless, rootless container engine CLI-compatible with Docker that runs containers as regular user processes without requiring a root-level background daemon.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
Docker requires a root daemon (dockerd) running permanently. This daemon is a single point of failure, a security risk (root access), and adds complexity (systemd service management).

**THE INVENTION MOMENT:**
"This is exactly why Podman was created."

**EVOLUTION:**
Docker (daemon required, root required, 2013) -> Podman 1.0 (daemonless, rootless, 2019) -> Podman Desktop (Docker Desktop alternative, 2022) -> Podman with Compose support (podman-compose, native compose, 2023+).

---

### Textbook Definition

Podman is an OCI-compliant container engine that manages containers and pods directly as child processes of the Podman command, requiring no background daemon and running rootless by default using user namespaces.

---

### Understand It in 30 Seconds

**One line:**
Podman = Docker without the daemon, rootless by default.

**One analogy:**

> Docker is like a restaurant with a maître d' (daemon) who must be present for anything to happen. Podman is like a self-service cafeteria - you grab your own tray (fork process) without needing anyone's permission.

**One insight:**
`alias docker=podman` works for most use cases. Same CLI, same image format (OCI), same registries. The key difference is architecture: Podman forks containers directly (like systemd starts services), while Docker routes everything through a persistent daemon.

---

### How It Works

```
Architecture comparison:

Docker:
  docker CLI -> Docker daemon (root) -> containerd -> runc
  (daemon is always running, single point of failure)

Podman:
  podman CLI -> conmon (per-container monitor) -> runc
  (no daemon, each container is a child process)
  (rootless by default via user namespaces)

Key differences:
| Feature        | Docker          | Podman         |
|----------------|-----------------|----------------|
| Daemon         | Required (root) | None           |
| Root required  | Yes (default)   | No (rootless)  |
| Socket         | /var/run/docker.sock | None      |
| Systemd        | Yes (service)   | No (or user)   |
| Pod support    | No (Compose)    | Yes (K8s-like) |
| CLI compat     | -               | docker alias   |
```

---

### Code Example

```bash
# Install and use (identical to Docker CLI)
podman run -d --name myapp -p 8080:8080 myapp:1.0
podman ps
podman logs myapp
podman stop myapp

# Rootless by default - no sudo needed
podman run --rm alpine id
# uid=0(root) gid=0(root)  <- inside container
# But on host: running as your user (UID 1000)

# Generate Kubernetes YAML from running container
podman generate kube myapp > myapp.yaml

# Run a Kubernetes pod YAML
podman play kube myapp.yaml
```

---

### Quick Recall

**If you remember only 3 things:**

1. No daemon = no single point of failure, no root daemon attack surface, no docker.sock to mount
2. Rootless by default = container escape lands as unprivileged user (not root)
3. CLI-compatible with Docker (`alias docker=podman`), same OCI images and registries

**Interview one-liner:**
"Podman is Docker-compatible but architecturally superior for security - daemonless (no root background process, no docker.sock attack surface) and rootless by default (user namespaces remap container root to unprivileged host UID), making it the secure-by-default choice for container runtimes."

---

### The Surprising Truth

Podman can generate Kubernetes YAML from running containers (`podman generate kube`) and run Kubernetes pod YAML directly (`podman play kube`). This means you can prototype K8s deployments locally with Podman without installing Kubernetes - bridging local development and cluster deployment with the same tool.

---

---

# Container Runtime Interface

**TL;DR** - CRI is the standard API between Kubernetes kubelet and container runtimes (containerd, CRI-O), enabling Kubernetes to work with any compliant runtime without runtime-specific code.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
Kubernetes had Docker-specific code (dockershim) baked into kubelet. Supporting a new runtime required modifying Kubernetes source code. Every runtime was a special case.

**THE INVENTION MOMENT:**
"This is exactly why CRI was created."

**EVOLUTION:**
Docker-only in K8s (2014-2016) -> CRI introduced (K8s 1.5, 2016) -> dockershim created as CRI adapter for Docker -> CRI-O created for pure CRI runtime (2017) -> dockershim deprecated (K8s 1.20, 2020) -> dockershim removed (K8s 1.24, 2022) -> containerd and CRI-O as standard runtimes.

---

### Textbook Definition

The Container Runtime Interface (CRI) is a gRPC-based plugin API that enables the Kubernetes kubelet to interact with any container runtime that implements the interface, decoupling Kubernetes from specific runtime implementations.

---

### How It Works

```
CRI Architecture:

kubelet
  |
  | gRPC (CRI API)
  |
  +--- containerd (via CRI plugin)
  |        |
  |        +--- runc (OCI)
  |
  +--- CRI-O (native CRI)
           |
           +--- runc, crun, kata (OCI)

CRI API services:
  RuntimeService:
    - RunPodSandbox / StopPodSandbox
    - CreateContainer / StartContainer
    - StopContainer / RemoveContainer
    - ListContainers / ContainerStatus

  ImageService:
    - PullImage / ListImages / RemoveImage
    - ImageStatus / ImageFsInfo
```

---

### Quick Recall

**If you remember only 3 things:**

1. CRI decouples Kubernetes from specific runtimes - kubelet speaks CRI gRPC, any compliant runtime works
2. containerd (CNCF, most popular) and CRI-O (Red Hat, purpose-built for K8s) are the two main CRI implementations
3. CRI enabled Docker's removal from K8s without breaking anything - images and containers work identically

**Interview one-liner:**
"CRI is the gRPC API that decouples Kubernetes from container runtimes - kubelet calls CRI methods like RunPodSandbox and CreateContainer, and any compliant runtime (containerd, CRI-O) implements them, which is how Kubernetes removed Docker dependency without affecting users."

---

---

# Init Containers

**TL;DR** - Init containers are special containers that run to completion before app containers start, used for setup tasks like database migration, config downloading, or dependency waiting.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
Your app container starts before the database is ready. It crash-loops until the database accepts connections. Or your app needs a config file from a remote source, but you don't want curl in the production image.

**THE INVENTION MOMENT:**
"This is exactly why Kubernetes init containers were created."

**EVOLUTION:**
Entrypoint scripts (fragile, bloated images) -> Docker health checks + depends_on (limited) -> Kubernetes init containers (1.6, 2017) -> Sidecar containers (K8s 1.28, 2023, for persistent helpers).

---

### Textbook Definition

Init containers are specialized containers in a Kubernetes pod that run sequentially and must complete successfully before any app containers start. They share the pod's volumes and network but can use different images and have different security contexts.

---

### Understand It in 30 Seconds

**One line:**
Init containers run setup tasks before your app starts.

**One analogy:**

> Init containers are like the opening act at a concert. They perform first, finish, and clear the stage. Only then does the main act (app container) begin. If the opening act fails, the show doesn't start.

**One insight:**
Init containers can use different images than the app. Need `curl` to download config? Use a `curl` image for init, keep your app image distroless. Need database migration? Use a `flyway` image for init, keep your app image clean.

---

### How It Works

```yaml
apiVersion: v1
kind: Pod
spec:
  initContainers:
    # 1. Wait for database to be ready
    - name: wait-for-db
      image: busybox
      command: [
          "sh",
          "-c",
          "until nc -z db-svc 5432; do
          echo waiting for db; sleep 2;
          done",
        ]

    # 2. Run database migration
    - name: migrate
      image: flyway/flyway
      args: ["migrate"]
      volumeMounts:
        - name: migrations
          mountPath: /flyway/sql

    # 3. Download config from vault
    - name: fetch-config
      image: vault:1.15
      command: ["vault", "read", "-format=json", "secret/app"]
      volumeMounts:
        - name: config
          mountPath: /config

  containers:
    # App starts only after ALL init containers succeed
    - name: app
      image: myapp:1.0 # distroless, no curl/tools
      volumeMounts:
        - name: config
          mountPath: /config
          readOnly: true

  volumes:
    - name: migrations
      configMap: { name: db-migrations }
    - name: config
      emptyDir: {}
```

```
Execution flow:
  wait-for-db -> migrate -> fetch-config -> app
  (sequential)  (success)  (success)      (starts)

  If any init container fails:
    pod restarts from first init container
    app container NEVER starts until all pass
```

---

### Quick Recall

**If you remember only 3 things:**

1. Init containers run sequentially and must succeed before app containers start
2. Use them for setup tasks: wait for dependencies, run migrations, download config, set permissions
3. They can use different images - keep your app image minimal and use specialized init images for setup

**Interview one-liner:**
"Init containers run specialized setup tasks sequentially before the app container starts - I use them for dependency readiness checks, database migrations, and secret fetching so the app image stays minimal and distroless while init containers bring the tools needed only at startup."

---

### The Surprising Truth

Init containers re-run on pod restart. If your pod is evicted and rescheduled, ALL init containers run again - including database migrations. This means init containers must be idempotent. A migration that runs twice must produce the same result. Flyway and Liquibase handle this with version tracking, but custom scripts often don't, causing production data corruption.

---

### Interview Deep-Dive

**Q1: When should you use init containers vs startup probes vs entrypoint scripts?**

_Why they ask:_ Tests understanding of Kubernetes startup patterns.

**Answer:**

| Approach          | Use When                                              | Limitation                                    |
| ----------------- | ----------------------------------------------------- | --------------------------------------------- |
| Init container    | Need different image or security context for setup    | Sequential only, delays startup               |
| Startup probe     | App itself needs warm-up time (JVM, ML model loading) | Only delays liveness check, doesn't run tasks |
| Entrypoint script | Simple single-command setup within same image         | Bloats image, mixes concerns                  |

Decision framework:

- **Need curl/wget but app is distroless?** -> Init container (different image)
- **Need to wait for DB?** -> Init container (with retry logic)
- **App takes 60s to start?** -> Startup probe (protects from premature liveness kills)
- **Need to set file permissions?** -> Init container (different security context)
- **Simple env var setup?** -> Entrypoint script (simplest option)

Key principle: init containers for cross-cutting setup concerns, startup probes for application warm-up, entrypoint scripts only for trivial in-image operations.

---

---

# Sidecar Containers

**TL;DR** - Sidecar containers run alongside the main app container in the same pod, sharing network and storage, providing cross-cutting capabilities like logging, proxying, monitoring, or security without modifying the app.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
Every microservice must implement its own logging agent, metrics collector, TLS termination, and service mesh proxy. This cross-cutting logic is duplicated across 50 services in 5 languages.

**THE INVENTION MOMENT:**
"This is exactly why the sidecar pattern was created."

**EVOLUTION:**
Libraries embedded in each service -> Ambassador pattern (2016) -> Sidecar pattern (Kubernetes pods, 2017) -> Envoy as standard sidecar proxy (Istio, 2017) -> Native sidecar containers (K8s 1.28, 2023, with proper lifecycle ordering).

---

### Textbook Definition

A sidecar container is a secondary container within a Kubernetes pod that provides supplementary functionality (logging, proxying, monitoring, security) to the main application container. Sidecars share the pod's network namespace (localhost communication) and can share volumes.

---

### Understand It in 30 Seconds

**One line:**
A sidecar is a helper container that adds capabilities without changing the main app.

**One analogy:**

> A sidecar on a motorcycle. The motorcycle (main container) focuses on driving. The sidecar (sidecar container) carries additional passengers or cargo. They share the same vehicle (pod) and travel together, but each has a distinct purpose.

**One insight:**
Because containers in a pod share the network namespace, the sidecar can listen on localhost. The app sends logs to `localhost:9200`, the sidecar forwards to Elasticsearch. The app doesn't know or care about the log shipping details.

---

### How It Works

```yaml
# Common sidecar patterns:
apiVersion: v1
kind: Pod
spec:
  containers:
    # Main application
    - name: app
      image: myapp:1.0
      ports:
        - containerPort: 8080

    # Sidecar 1: Log shipping
    - name: log-shipper
      image: fluentbit:2.2
      volumeMounts:
        - name: logs
          mountPath: /var/log/app

    # Sidecar 2: Service mesh proxy
    - name: envoy
      image: envoyproxy/envoy:v1.28
      ports:
        - containerPort: 15001

  volumes:
    - name: logs
      emptyDir: {}
```

```
Pod internal communication:
+-------------------------------+
| Pod (shared network namespace)|
|                               |
| +-------+   localhost  +---+  |
| |  App  | -----------> |Envoy |
| |:8080  |             |:15001|
| +-------+             +---+  |
|     |                         |
|     | shared volume           |
|     v                         |
| +----------+                  |
| |Log Shipper|                 |
| | (reads    |                 |
| | /var/log) |                 |
| +----------+                  |
+-------------------------------+
```

---

### Complete Picture - End-to-End Flow

**NORMAL FLOW:**
External request -> Envoy sidecar (mTLS, routing) -> App container (business logic) -> App writes logs to shared volume <- YOU ARE HERE -> Log shipper sidecar reads logs -> forwards to Elasticsearch

**FAILURE PATH:**
Sidecar crashes -> kubelet restarts sidecar -> app continues running (traffic temporarily unproxied) -> sidecar recovers -> traffic proxied again

**WHAT CHANGES AT SCALE:**
At 1000+ pods, sidecar overhead (memory per Envoy: ~50MB) adds up: 50GB just for proxies. Ambient mesh (Istio, 2023) moves proxy to node-level, eliminating per-pod overhead.

---

### Quick Recall

**If you remember only 3 things:**

1. Sidecars share pod's network (localhost) and volumes - enabling transparent interception without app changes
2. Common uses: service mesh proxy (Envoy), log shipping (Fluentbit), secret injection (Vault agent), monitoring
3. K8s 1.28+ native sidecars (`restartPolicy: Always` on init containers) solve the ordering problem - sidecar starts before app and survives app restarts

**Interview one-liner:**
"Sidecars add cross-cutting capabilities to pods without modifying the application - sharing localhost network for transparent proxying (Envoy for mTLS/routing) and shared volumes for log shipping - with K8s 1.28 native sidecars solving the lifecycle ordering problem where sidecars must start before and outlive the main container."

---

### The Surprising Truth

The sidecar pattern is becoming a victim of its own success. Istio's ambient mesh (2023) moves the Envoy proxy from per-pod sidecars to per-node, reducing memory overhead by 90%+ in large clusters. The insight: not every cross-cutting concern needs a per-pod container. Some (like L4 proxying) work better at the node level. Per-pod sidecars remain valuable for L7-aware proxying and application-specific helpers.

---

### Interview Deep-Dive

**Q1: What's the lifecycle ordering problem with sidecars, and how does K8s 1.28 solve it?**

_Why they ask:_ Tests knowledge of a common production issue and its solution.

**Answer:**
The problem: In standard K8s, all containers in a pod start simultaneously and stop together. But sidecars need to:

1. **Start BEFORE** the app (Envoy must be ready before app sends traffic)
2. **Stop AFTER** the app (log shipper must flush remaining logs after app exits)

Before K8s 1.28, workarounds:

- Sleep in app entrypoint waiting for sidecar
- PostStart hooks
- Istio's custom injection with hold-application-until-proxy-starts

K8s 1.28 solution - native sidecar containers:

```yaml
initContainers:
  - name: envoy
    image: envoyproxy/envoy:v1.28
    restartPolicy: Always # <-- makes it a sidecar
    # Starts before app, restarts if crashes,
    # runs until pod terminates
```

This init container with `restartPolicy: Always` starts before the app container (init ordering) but keeps running (not one-shot like normal init). On pod shutdown, app containers stop first, then sidecars get SIGTERM - ensuring proper cleanup ordering.

---

**Q2: A team has 200 microservices and each pod has 3 sidecars (Envoy, Fluentbit, Vault agent). What concerns do you raise?**

_Why they ask:_ Tests ability to identify architectural scaling issues.

**Answer:**
Resource overhead analysis:

- **Envoy**: ~50MB RAM, ~0.1 CPU per pod
- **Fluentbit**: ~30MB RAM, ~0.05 CPU per pod
- **Vault agent**: ~50MB RAM, ~0.05 CPU per pod
- **Total overhead**: 130MB + 0.2 CPU per pod
- **200 services x 3 replicas**: 600 pods x 130MB = 78GB RAM just for sidecars

Concerns:

1. **Cost**: 78GB RAM + 120 vCPU dedicated to sidecars
2. **Startup latency**: 3 sidecars add 5-15s to pod startup
3. **Failure blast radius**: sidecar crash can affect app (depending on pattern)
4. **Observability complexity**: 600 Envoy instances to monitor

Optimization options:

1. **Ambient mesh**: move Envoy to node-level (90% memory savings)
2. **DaemonSet log shipper**: one Fluentbit per node, not per pod
3. **CSI secrets**: replace Vault sidecar with CSI driver (per-node, not per-pod)
4. **Evaluate necessity**: do all 200 services need service mesh? Maybe only 50 external-facing ones

Principle: sidecars are powerful but not free. At scale, per-pod overhead compounds. Move cross-cutting concerns to per-node when the per-pod model becomes too expensive.
