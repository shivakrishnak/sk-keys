---
layout: default
title: "Container Runtime Interface (CRI)"
parent: "Containers"
nav_order: 855
permalink: /containers/container-runtime-interface-cri/
number: "0855"
category: Containers
difficulty: ★★★
depends_on: Container, containerd, Kubernetes Architecture, OCI Standard, Docker
used_by: Kubernetes Architecture, kubelet, Pod
related: containerd, Kubernetes Architecture, kubelet, OCI Standard, Container Orchestration
tags:
  - containers
  - kubernetes
  - internals
  - advanced
  - architecture
---

# 855 — Container Runtime Interface (CRI)

⚡ TL;DR — The Container Runtime Interface (CRI) is the gRPC API that decouples Kubernetes from any specific container runtime — kubelet speaks CRI; any compliant runtime (containerd, CRI-O) responds.

| #855 | Category: Containers | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Container, containerd, Kubernetes Architecture, OCI Standard, Docker | |
| **Used by:** | Kubernetes Architecture, kubelet, Pod | |
| **Related:** | containerd, Kubernetes Architecture, kubelet, OCI Standard, Container Orchestration | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
In 2016, Kubernetes uses Docker as its runtime via a custom integration layer called "dockershim" — code embedded in kubelet that speaks Docker's proprietary API. When CoreOS builds rkt, Kubernetes must maintain a separate rkt integration. When Frakti (hypervisor-based runtime) is built, another integration. Each new runtime requires modifying kubelet source code, adding test burden, and coupling Kubernetes releases to runtime releases. By 2016, kubelet has three different runtime integrations with hundreds of lines of runtime-specific code, each maintained by different teams.

**THE BREAKING POINT:**
Tight coupling between the kubelet and container runtimes means: new runtimes require core Kubernetes changes, runtime bugs affect kubelet stability, and the Kubernetes project is forced to maintain vendor-specific code. The Docker integration (dockershim) is particularly problematic: Docker itself is a large, complex system with features irrelevant to Kubernetes, and its release cycle doesn't align with Kubernetes. The Kubernetes team eventually commits to removing dockershim entirely.

**THE INVENTION MOMENT:**
This is exactly why CRI was designed in 2016 (Kubernetes 1.5) — a gRPC-based interface specification that every container runtime must implement, allowing kubelet to communicate with any compliant runtime without modification. Kubernetes talks CRI; the runtime handles the rest.

---

### 📘 Textbook Definition

The **Container Runtime Interface (CRI)** is a plugin interface (defined as a gRPC API) that enables the Kubernetes kubelet to use any container runtime that implements the specification, without requiring changes to kubelet source code. CRI defines two gRPC services: **RuntimeService** (pod sandbox and container lifecycle: RunPodSandbox, CreateContainer, StartContainer, StopContainer, RemoveContainer) and **ImageService** (image management: PullImage, ListImages, RemoveImage). Any runtime that implements CRI (containerd, CRI-O, Kata Containers via shim) can be used by any Kubernetes version that supports CRI, enabling runtime diversity and innovation without coupling to the kubelet codebase.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
CRI is the standard plug socket between Kubernetes and container runtimes — any CRI-compliant runtime plugs in and works.

**One analogy:**
> A power strip has a standard socket (CRI). Any device with a compatible plug (containerd, CRI-O, Kata) connects and receives power (container management). The power strip doesn't care what device is plugged in — it just provides the standard interface. Before CRI, Kubernetes was a custom charger only compatible with one device (Docker) — changing the device meant redesigning the charger.

**One insight:**
CRI's greatest architectural impact was enabling the removal of the Docker daemon from Kubernetes without breaking anything. Because kubelet now communicates via CRI, replacing Docker's dockershim with containerd's CRI plugin was a configuration change, not a code change. Users didn't change their Dockerfiles or images — only the runtime changed underneath.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. kubelet's job: ensure the containers described in pod specs are running on the node.
2. HOW containers are run (which runtime, which isolation mechanism) is orthogonal to WHAT should run.
3. An interface separates policy (what to run) from mechanism (how to run it).

**DERIVED DESIGN:**

**CRI gRPC API (simplified):**

```protobuf
// RuntimeService: pod and container lifecycle
service RuntimeService {
  rpc RunPodSandbox(RunPodSandboxRequest) returns (RunPodSandboxResponse);
  rpc StopPodSandbox(StopPodSandboxRequest) returns (StopPodSandboxResponse);
  rpc RemovePodSandbox(RemovePodSandboxRequest) returns (RemovePodSandboxResponse);
  
  rpc CreateContainer(CreateContainerRequest) returns (CreateContainerResponse);
  rpc StartContainer(StartContainerRequest) returns (StartContainerResponse);
  rpc StopContainer(StopContainerRequest) returns (StopContainerResponse);
  rpc RemoveContainer(RemoveContainerRequest) returns (RemoveContainerResponse);
  
  rpc ExecSync(ExecSyncRequest) returns (ExecSyncResponse);        // kubectl exec
  rpc Exec(ExecRequest) returns (ExecResponse);                    // kubectl exec (stream)
  rpc Attach(AttachRequest) returns (AttachResponse);              // kubectl attach
  rpc PortForward(PortForwardRequest) returns (PortForwardResponse); // port-forward
}

// ImageService: image management
service ImageService {
  rpc PullImage(PullImageRequest) returns (PullImageResponse);
  rpc ListImages(ListImagesRequest) returns (ListImagesResponse);
  rpc RemoveImage(RemoveImageRequest) returns (RemoveImageResponse);
}
```

**Pod sandbox concept:**
CRI introduces the "Pod Sandbox" abstraction — the shared namespace context (network, IPC, UTS) that all containers in a pod share. This maps to: the `pause` container in containerd/Docker implementations, a virtual machine in Kata Containers, a gVisor sandbox context in gVisor.

```
┌──────────────────────────────────────────────────────────┐
│      CRI: Pod Sandbox + Containers                       │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  kubelet: RunPodSandbox(PodSandboxConfig{               │
│    name: "my-pod",                                       │
│    hostname: "my-pod",                                   │
│    linux: { namespaces, cgroups }                        │
│    ...                                                   │
│  })                                                      │
│  → runtime creates: pause container (holds namespaces)   │
│  → returns: PodSandboxId                                 │
│                                                          │
│  kubelet: CreateContainer(PodSandboxId, ContainerConfig{ │
│    name: "nginx",                                        │
│    image: {image: "nginx:1.25"},                         │
│    command: [...], env: [...], mounts: [...]             │
│  })                                                      │
│  → runtime creates container in sandbox's namespaces     │
│  → returns: ContainerId                                  │
│                                                          │
│  kubelet: StartContainer(ContainerId)                    │
│  → runtime executes container process                    │
└──────────────────────────────────────────────────────────┘
```

**CRI implementations:**
- **containerd CRI plugin** (default): containerd 1.3+ includes a built-in CRI plugin at `/run/containerd/containerd.sock`
- **CRI-O**: lightweight CRI implementation designed specifically for Kubernetes (no Docker API surface)
- **Kata Containers shim**: implements CRI, but each sandbox is a microVM (VM isolation)
- **gVisor runsc**: CRI-compatible shim using a userspace kernel for sandboxing

**THE TRADE-OFFS:**

**Gain:** Runtime diversity, kubelet/runtime independence, stable interface, innovation without coordination.

**Cost:** Additional gRPC hop for every container operation. CRI is a translation layer — requires aligned versions between kubelet CRI expectations and runtime implementation. Introduces `crictl` tooling for debugging instead of `docker` commands.

---

### 🧪 Thought Experiment

**SETUP:**
Kubernetes 1.20. You want to run half your pods with standard containerd (fast, lightweight) and the other half with Kata Containers (VM isolation, slower). Without CRI, this is impossible — the runtime is a cluster-level setting.

**WHAT HAPPENS WITHOUT CRI:**
Kubernetes 1.19 (pre-CRI default): dockershim is the only runtime. You cannot mix runtimes per pod. Running any pod with VM isolation requires a completely separate Kubernetes cluster. Operational overhead doubles.

**WHAT HAPPENS WITH CRI (RuntimeClass):**
CRI plus Kubernetes `RuntimeClass` allows per-pod runtime selection:
```yaml
# Pod using default containerd (fast path)
spec:
  runtimeClassName: runc-default
  
# Pod using Kata Containers (VM isolation)
spec:
  runtimeClassName: kata-containers
```
The same kubelet, on the same node, can invoke different CRI handlers for different pods. CRI's abstraction enables multi-runtime nodes.

**THE INSIGHT:**
CRI's abstraction is not just about replacing Docker — it enables runtime *diversity*. The same cluster can run trusted workloads with lightweight namespaces (containerd/runc) and untrusted workloads with VM isolation (Kata), using the RuntimeClass mechanism to select per pod. This is possible only because CRI provides a clean interface between kubelet and the runtime.

---

### 🧠 Mental Model / Analogy

> CRI is like the USB specification. Any USB device (container runtime) that implements the spec connects to any USB port (kubelet). The port doesn't care what's connected — keyboard, mouse, hard drive, camera. It just provides the standardised electrical interface. Before USB (before CRI), each device needed its own custom port in the computer's motherboard — changing your keyboard required opening the computer.

Mapping:
- "USB specification" → CRI gRPC interface
- "USB port (motherboard)" → CRI socket in kubelet
- "USB device" → container runtime (containerd, CRI-O, Kata shim)
- "Keyboard/mouse/camera" → different runtime implementations with different properties
- "Custom port per device" → dockershim (Docker-specific code embedded in kubelet)
- "Plugging in a new device" → adding a new CRI runtime without changing kubelet

Where this analogy breaks down: USB devices are interchangeable for the same function. Container runtimes have different security properties (contained namespaces vs VM isolation) — switching runtimes is not purely transparent.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
CRI is a standard language for Kubernetes to talk to container runtimes. Before CRI, Kubernetes could only speak "Docker." With CRI, Kubernetes speaks a universal language, and any runtime that understands it (containerd, CRI-O, Kata) can be used without changing Kubernetes.

**Level 2 — How to use it (junior developer):**
As a developer, CRI is invisible. Your Dockerfiles, pod specs, and `kubectl` commands work identically regardless of whether the cluster uses containerd or CRI-O. CRI is a platform concern. For debugging, use `crictl` (the CRI-aware command line tool): `crictl ps`, `crictl logs <id>`, `crictl images`. On clusters controlled by containerd, check `/run/containerd/containerd.sock`.

**Level 3 — How it works (mid-level engineer):**
kubelet connects to the CRI socket (UNIX or TCP socket configured via `--container-runtime-endpoint`). kubelet makes gRPC calls: `RunPodSandbox` to create the pod's network/IPC namespace context, `CreateContainer`/`StartContainer` for each container in the pod spec, and `StopContainer`/`RemoveContainer` on pod deletion. `ExecSync`/`Exec` implement `kubectl exec`. `Attach` implements `kubectl attach`. `PortForward` implements `kubectl port-forward`. All runtime-specific code lives on the other side of the CRI socket — kubelet is runtime-agnostic.

**Level 4 — Why it was designed this way (senior/staff):**
CRI's gRPC design was chosen over REST because gRPC provides: bidirectional streaming (required for `kubectl exec` and `kubectl logs`), protobuf serialisation (efficient binary protocol), and service definition as code (the `.proto` file IS the interface contract). The "Pod Sandbox" abstraction in CRI was a generalization that enabled Kata Containers: in Docker/containerd, a sandbox is a `pause` container holding namespaces. In Kata, a sandbox is a virtual machine. In gVisor, a sandbox is a userspace kernel process. The same kubelet control path (`RunPodSandbox`) works for all three because CRI abstracted the sandbox concept without prescribing its implementation. The removal of dockershim (Kubernetes 1.24) was the direct result of CRI making it unnecessary — and the 7-year delay was primarily to give users and vendors time to migrate their tooling from Docker CLI assumptions to CRI-compatible alternatives.

---

### ⚙️ How It Works (Mechanism)

**kubelet → CRI → runtime flow:**
```
┌──────────────────────────────────────────────────────────┐
│           kubelet ↔ CRI ↔ Runtime                        │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  kube-apiserver: pod spec assigned to node               │
│       ↓                                                  │
│  kubelet: receives pod spec                              │
│       ↓                                                  │
│  kubelet → CRI gRPC → ImageService.PullImage()           │
│  (containerd: pull image from registry → content store)  │
│       ↓                                                  │
│  kubelet → CRI gRPC → RuntimeService.RunPodSandbox()     │
│  (containerd: create pause container, configure CNI)     │
│       ↓                                                  │
│  For each init container (in order):                     │
│  kubelet → CRI → CreateContainer()                       │
│  kubelet → CRI → StartContainer()                        │
│  kubelet → CRI → wait for exit 0                         │
│       ↓ (all init containers passed)                     │
│  For each app container:                                 │
│  kubelet → CRI → CreateContainer()                       │
│  kubelet → CRI → StartContainer()                        │
│       ↓                                                  │
│  kubelet: monitors container status via                  │
│  CRI → ContainerStatus() periodically                   │
│  (feeds back to pod status in etcd)                      │
└──────────────────────────────────────────────────────────┘
```

**CRI socket configuration:**
```bash
# Check CRI endpoint on a node
systemctl show kubelet | grep container-runtime
# or
ps aux | grep kubelet | grep container-runtime-endpoint

# Common socket paths:
# containerd: /run/containerd/containerd.sock
# CRI-O: /var/run/crio/crio.sock

# Test CRI with crictl
crictl --runtime-endpoint unix:///run/containerd/containerd.sock ps
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
kubectl apply pod.yaml → API server → etcd → scheduler
  → kubelet: pod spec received
  → CRI: ImageService.PullImage() ← YOU ARE HERE
  → CRI: RuntimeService.RunPodSandbox()
  → CRI: RuntimeService.CreateContainer() (per container)
  → CRI: RuntimeService.StartContainer()
  → kubelet: reports pod Ready via CRI ContainerStatus
  → API server: pod Running in etcd
  → Service endpoints updated
```

**FAILURE PATH:**
```
CRI socket unavailable (containerd crash):
  → kubelet: gRPC dial fails
  → kubelet: logs "Failed to get container runtime status"
  → kubelet: reports node NotReady
  → new pod scheduling blocked (node not ready)
  → existing containers: shim keeps them running (shim model)
  → fix: systemctl restart containerd
  → kubelet reconnects: node Ready again
```

**WHAT CHANGES AT SCALE:**
At 1,000+ pods per node (high-density serverless), CRI gRPC call rate is significant (creation + status polling × 1,000 pods). Batching status checks and efficient streaming protocols become critical. The CRI-V2 proposals address performance at extreme scale. RuntimeClass with multiple CRI handlers per node requires careful scheduling (RuntimeClass-aware scheduling labels nodes by supported runtime).

---

### 💻 Code Example

**Example 1 — crictl: CRI-aware debugging:**
```bash
# List all pods via CRI (equivalent to docker ps for containers)
crictl pods

# List all containers via CRI
crictl ps

# Pull image via CRI
crictl pull nginx:1.25.3

# Get container logs via CRI
crictl logs <container-id>

# Execute command in container via CRI
crictl exec -it <container-id> sh

# Inspect container (OCI spec, mounts, network)
crictl inspect <container-id>

# Check image list
crictl images
```

**Example 2 — Configure kubelet CRI endpoint:**
```yaml
# /var/lib/kubelet/config.yaml
containerRuntimeEndpoint: unix:///run/containerd/containerd.sock
imageServiceEndpoint: unix:///run/containerd/containerd.sock
```

```bash
# Or as kubelet flag
kubelet --container-runtime-endpoint=unix:///run/containerd/containerd.sock
```

**Example 3 — RuntimeClass: per-pod runtime selection:**
```yaml
# Define available runtimes
apiVersion: node.k8s.io/v1
kind: RuntimeClass
metadata:
  name: kata-containers
handler: kata              # maps to containerd RuntimeHandler

---
# Use a specific runtime for a pod
apiVersion: v1
kind: Pod
spec:
  runtimeClassName: kata-containers    # VM-isolated runtime
  containers:
  - name: secure-workload
    image: myapp:latest
```

**Example 4 — Check CRI implementation in use:**
```bash
# Which runtime is the node using?
kubectl get node <node-name> -o jsonpath='{.status.nodeInfo.containerRuntimeVersion}'
# Output example: containerd://1.7.2

# Detailed CRI info
kubectl describe node <node-name> | grep "Runtime Version"
```

---

### ⚖️ Comparison Table

| CRI Implementation | OCI Compliant | VM Isolation | K8s Support | Rootless | Best For |
|---|---|---|---|---|---|
| **containerd** | Yes | Via Kata shim | Yes (default) | Partial | General Kubernetes workloads |
| CRI-O | Yes | Via Kata shim | Yes | Partial | Minimal K8s (OpenShift) |
| Kata Containers shim | Yes | Yes (microVM) | Yes (RuntimeClass) | No | Untrusted/multi-tenant workloads |
| gVisor runsc | Via OCI | Userspace kernel | Yes (RuntimeClass) | Yes | Sandboxed cloud workloads |
| Podman (via CRI) | Yes | No | Via CRI-O | Yes | Single-node CRI compatibility |

How to choose: containerd for default cluster setup (GKE, EKS, AKS all use containerd). CRI-O for OpenShift and minimal K8s deployments. Kata for multi-tenant with strong isolation requirements. gVisor for Google Cloud Run-like sandboxed workloads.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Removing Docker from K8s breaks Docker images" | CRI-based runtimes (containerd) are fully OCI-compliant. All Docker-built images are OCI images and run identically on containerd. Zero image format change needed. |
| "CRI is visible to application developers" | No. CRI is entirely infrastructure. Developers write Dockerfiles and pod YAML; CRI is the hidden mechanism that executes them. Only cluster operators and SREs interact with CRI (via crictl, kubelet config). |
| "All CRI implementations behave identically" | CRI defines the interface; implementations have different properties. containerd and CRI-O both implement CRI but have different feature sets, performance profiles, and operational tooling. |
| "crictl replaces kubectl for Kubernetes management" | crictl is a node-level CRI debugging tool — it directly accesses the CRI socket, bypassing Kubernetes API server. It's for debugging, not management. kubectl remains the management tool. |
| "CRI versions must match between kubelet and runtime" | kubelet and CRI runtime must implement compatible CRI API versions, but they can differ in minor versions. The CRI spec defines compatibility windows. Mismatches cause errors and require compatible version pairing. |

---

### 🚨 Failure Modes & Diagnosis

**CRI socket connection refused (runtime not running)**

**Symptom:**
Pods stuck in `ContainerCreating`. Node shows `NotReady` (briefly) or kubelet logs show CRI connection errors. `kubectl describe pod` shows `"failed to create containerd task"`.

**Root Cause:**
containerd (or CRI-O) is not running, crashed, or its socket is not at the expected path.

**Diagnostic Command / Tool:**
```bash
# Check runtime status on node
systemctl status containerd
systemctl status crio  # if using CRI-O

# Check CRI socket
ls -la /run/containerd/containerd.sock

# Check kubelet CRI connection attempts
journalctl -u kubelet | grep -i "CRI\|container runtime"

# Test CRI connectivity
crictl --runtime-endpoint unix:///run/containerd/containerd.sock version
```

**Fix:**
```bash
systemctl restart containerd
# OR
systemctl restart crio
```

**Prevention:**
Monitor containerd/CRI-O service health. Alert when node goes `NotReady`. Containerd's shim model means running containers survive restarts — only new pod creation is affected.

---

**CRI version mismatch (kubelet/runtime API incompatibility)**

**Symptom:**
After upgrading Kubernetes or containerd independently: `"RuntimeService.Version failed: rpc error: code = Unimplemented"` in kubelet logs.

**Root Cause:**
kubelet expects a newer CRI API version than the runtime implements (or vice versa). Mismatched upgrade path.

**Diagnostic Command / Tool:**
```bash
# Check kubelet version
kubelet --version

# Check containerd CRI version
crictl version
# Shows: RuntimeVersion, RuntimeAPIVersion

# Compare expected vs provided CRI API version
kubectl get node <node> -o jsonpath='{.status.nodeInfo.kubeletVersion}'
```

**Fix:**
Align kubelet and containerd versions according to the Kubernetes compatibility matrix. Upgrade both in coordinated fashion.

**Prevention:**
Follow Kubernetes upgrade documentation. Upgrade containerd and kubelet together. Test on staging nodes before rolling to production.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `containerd` — the primary CRI implementation; understand containerd before CRI
- `Kubernetes Architecture` — CRI is a component of the Kubernetes node architecture
- `OCI Standard` — CRI runtimes are OCI-compliant; understand OCI to understand what CRI operates on

**Builds On This (learn these next):**
- `Kubernetes Architecture` — the full stack: API server → scheduler → kubelet → CRI → runtime
- `kubelet` — kubelet is containerd's CRI client; understanding kubelet shows CRI in context
- `Pod` — the CRI `RunPodSandbox` primitive maps directly to the Kubernetes Pod concept

**Alternatives / Comparisons:**
- `containerd` — implements CRI; the default runtime behind CRI in most clusters
- `Container Orchestration` — orchestration uses CRI as the runtime interface
- `Docker` — Docker was replaced as the Kubernetes runtime because dockershim (pre-CRI) was removed

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ gRPC interface between kubelet and any    │
│              │ CRI-compliant container runtime           │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ kubelet tightly coupled to Docker (one    │
│ SOLVES       │ runtime only) — fragile, vendor-locked    │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Pod Sandbox abstraction: CRI separates    │
│              │ "create namespace context" from           │
│              │ "run container in it" — enabling both     │
│              │ namespace and VM isolation runtimes       │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always active in Kubernetes — transparent │
│              │ to developers, configurable by operators  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Never bypass CRI directly — use kubectl   │
│              │ and crictl only for debugging             │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Runtime flexibility + independence vs     │
│              │ one extra gRPC abstraction layer          │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "CRI is the USB standard for Kubernetes:  │
│              │  any runtime that speaks CRI plugs in"    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ containerd → Kubernetes Architecture →    │
│              │ kubelet → Pod                             │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Kubernetes 1.24 removed dockershim — the embedded code that allowed kubelet to use Docker as a container runtime. Many cloud providers (AWS EKS, Google GKE, Azure AKS) had already migrated their managed clusters to containerd before this date. Analyse: what would have happened to clusters that hadn't migrated when they upgraded to Kubernetes 1.24? What is the impact on running workloads (hint: consider the shim model), and trace the exact upgrade path a production cluster operator must follow to migrate from dockershim to containerd without downtime.

**Q2.** A security team wants to implement a policy: "All pods in the `untrusted` namespace must use Kata Containers (VM isolation); all pods in the `trusted` namespace may use standard containerd." Design the complete implementation: which Kubernetes resources are needed (RuntimeClass, NodeSelector, admission webhook?), how you ensure that pods cannot bypass the namespace-to-runtime binding, what observability you need to detect policy violations, and what operational trade-offs this policy introduces for the teams deploying into each namespace.

