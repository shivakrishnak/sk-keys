---
id: CTR-054
title: "Container Runtime Internals (runc, containerd)"
category: Containers
tier: tier-6-infrastructure-devops
folder: CTR-containers
difficulty: ★★★
depends_on: CTR-018, CTR-010, CTR-021, CTR-046
used_by: CTR-053
related: CTR-051, CTR-054
tags:
  - containers
  - internals
  - deep-dive
  - linux
  - first-principles
status: complete
version: 3
layout: default
parent: "Containers"
grand_parent: "Technical Mastery"
nav_order: 50
permalink: /technical-mastery/ctr/container-runtime-internals-runc-containerd/
---

⚡ TL;DR - A container starts via a two-layer runtime stack: containerd (high-level, manages image and lifecycle) calls runc (low-level, sets up Linux namespaces and cgroups and exec's the process) using the OCI Runtime Specification.

| Metadata        |                                    |     |
| :-------------- | :--------------------------------- | :-- |
| **Depends on:** | CTR-018, CTR-010, CTR-021, CTR-046 |     |
| **Used by:**    | CTR-053                            |     |
| **Related:**    | CTR-051, CTR-054                   |     |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A developer runs `docker run nginx`. Something starts an nginx process.
But what exactly happened between typing the command and the nginx
process existing? Without understanding the runtime stack, the developer
cannot diagnose why a container fails to start, what privileges it
actually has, or why its resource limits are not being enforced.

**THE BREAKING POINT:**
A container runtime CVE is disclosed (CVE-2019-5736: runc container
escape). The CVE description mentions "runc binary overwrite from inside
a container." A team that does not understand that runc is a separate
binary invoked by containerd for each container start cannot assess their
exposure or apply the patch correctly.

**THE INVENTION MOMENT:**
The OCI Runtime Specification was created to standardise what a low-level
container runtime must do: given an OCI bundle (rootfs + config.json),
set up the isolated process. This separated the "what to do" (OCI spec)
from the "how to do it" (runc, gVisor, Kata). The two-layer model (high-
level runtime + low-level runtime) enables runtime pluggability.

**EVOLUTION:**
2013: Docker monolith handles everything. 2015: libcontainer extracted
(later becomes runc). 2016: OCI Runtime Spec 1.0 published; runc becomes
the reference implementation. 2017: containerd extracted from Docker as
a standalone daemon. 2018: containerd 1.0 released; becomes the default
Kubernetes runtime. 2020: containerd-shim-v2 protocol enables the shim
process model for improved isolation and runtime pluggability.

---

### 📘 Textbook Definition

**Container runtime internals** describes the two-layer runtime stack
used by Kubernetes: containerd (the high-level CRI runtime daemon)
manages the container lifecycle (image pull, snapshot, network, storage),
delegates process creation to runc (the OCI-compliant low-level runtime)
via a shim process. runc calls Linux kernel APIs (namespaces, cgroups,
seccomp, capabilities) to isolate the container process, then exec's
the container entrypoint.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
containerd manages the what (image, lifecycle, storage); runc manages
the how (namespaces, cgroups, process exec) via the OCI Runtime Spec.

**One analogy:**

> The runtime stack is like a building contractor chain. Kubernetes is
> the architect (tells containerd what to build). containerd is the
> general contractor (pulls materials, manages the project). runc is
> the specialist subcontractor (sets up the actual construction: walls,
> plumbing, power = namespaces, cgroups, capabilities). The OCI spec
> is the building code (standard rules runc must follow).

**One insight:**
The shim process between containerd and runc is the least-known but most
important component: it keeps the container running even if containerd
restarts, and it is the process that actually owns the container's
stdin/stdout/stderr file descriptors.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **A container is a process with isolation constraints** - it is not
   a separate machine. The isolation is implemented by Linux kernel
   primitives (namespaces, cgroups, seccomp, capabilities).
2. **The OCI Runtime Spec defines the interface between high-level and
   low-level runtimes** - containerd passes an OCI bundle to runc; runc
   uses the `config.json` in the bundle to set up isolation.
3. **The shim process decouples container lifetime from containerd
   lifetime** - the shim holds the container's pipes and reports status
   to containerd; if containerd restarts, containers keep running.
4. **runc is ephemeral** - it runs, sets up the container, exec's the
   process, and exits. The container process is then an orphan adopted
   by the shim.

**DERIVED DESIGN:**
Given invariant 4: runc cannot be the parent of the container process
after startup. The shim fills this role. Given invariant 2: the OCI
spec enables runtime pluggability - any binary implementing the OCI
Runtime Spec can replace runc (gVisor's `runsc`, Kata's `kata-runtime`).

**THE TRADE-OFFS:**

**Gain:** Two-layer model enables runtime pluggability, recovery from
containerd restarts, and clear separation of concerns between image
management and process isolation.

**Cost:** Two-layer model adds latency to container startup (containerd
+ shim + runc startup sequence). Typically 100-300ms for a cold start.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

**Essential:** Image management, process isolation setup, and container
lifecycle management are genuinely distinct concerns.

**Accidental:** The historical Docker monolith tried to handle all three
in one process, creating tight coupling and slow innovation.

---

### 🧪 Thought Experiment

**SETUP:**
containerd is running. A container is running. An engineer restarts the
containerd daemon (for an upgrade).

**WHAT HAPPENS WITHOUT THE SHIM:**
containerd is the parent of all container processes. When containerd
dies, it is reparented to init (PID 1). But without something managing
the container's stdio, network namespace, and exit status, containerd
cannot reconnect to the container on restart. All containers must be
restarted.

**WHAT HAPPENS WITH THE SHIM:**
containerd spawns a shim process per container. The shim is the parent
of the container process and holds its stdio pipes. When containerd
restarts, it reconnects to the existing shims via their Unix sockets.
All containers continue running uninterrupted through containerd restarts.

**THE INSIGHT:**
The shim process is the architectural solution to the daemon-process
coupling problem. It makes containerd restartable without container
downtime - a critical property for container daemon upgrades in
production.

---

### 🧠 Mental Model / Analogy

> The runtime stack is like a construction project management hierarchy.
> Kubernetes is the client (tells you what to build). containerd is the
> project manager (coordinates all work, manages materials). The shim
> is the site supervisor (on-site daily, reports progress, keeps things
> running even when the project manager is temporarily unavailable).
> runc is the specialist crew (does the technical installation work,
> then leaves). The OCI spec is the building code (standards all parties
> must follow).

Element mapping:

- **Client** = Kubernetes Kubelet
- **Project manager** = containerd
- **Site supervisor** = containerd-shim (one per container)
- **Specialist crew** = runc (ephemeral, exits after container starts)
- **Building code** = OCI Runtime Specification

Where this analogy breaks down: in construction, the site supervisor
works for the project manager permanently; in containers, the shim
is relatively autonomous and can outlive containerd restarts.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
When you start a container, two programs work together: one manages
the image and lifecycle (containerd), and one sets up the isolated
process environment (runc). They follow a standard (OCI spec) so either
can be replaced independently.

**Level 2 - How to use it (junior developer):**
You rarely interact with containerd or runc directly - Kubernetes and
Docker abstract them. But when debugging container startup failures,
knowing that `containerd` logs at `/var/log/containerd/containerd.log`
and that runc reads `config.json` from the OCI bundle helps diagnose
issues. The command `ctr containers list` (containerd CLI) shows running
containers at the containerd level.

**Level 3 - How it works (mid-level engineer):**
Container start sequence: (1) Kubelet calls containerd gRPC API (CRI).
(2) containerd pulls image if not cached, creates snapshot (rootfs).
(3) containerd generates `config.json` (OCI bundle) with namespaces,
cgroups, mounts, capabilities, seccomp profile. (4) containerd spawns
a shim process. (5) Shim invokes `runc create` with the OCI bundle.
(6) runc sets up namespaces, cgroups, mounts, and seccomp; calls
`setns`, `clone`, `unshare` system calls. (7) runc calls `runc start`,
which exec's the container entrypoint. (8) runc exits; shim adopts
the container process.

**Level 4 - Why it was designed this way (senior/staff):**
The two-layer model reflects the Single Responsibility Principle at
the infrastructure level. containerd is responsible for "what to run"
(image, storage, networking coordination). runc is responsible for
"how to isolate it" (kernel API calls). The OCI spec is the contract
between them. This separation enabled the runtime ecosystem: gVisor
and Kata can replace runc at the low-level runtime layer without
changing containerd or Kubernetes. The shim model solved the daemon-
restart problem by introducing a lightweight, long-lived process whose
only job is to hold the container's file descriptors and report status.

**Expert Thinking Cues:**

- "If a container fails to start, is the failure in image pull
  (containerd), OCI bundle generation (containerd), or process
  isolation setup (runc)? Which logs reveal each?"
- "For a container escape CVE, which layer is affected? runc (process
  isolation) or containerd (image/snapshot management)?"
- "If containerd is restarted, do containers restart? The shim model
  says no - but verify this matches your version and configuration."

---

### ⚙️ How It Works (Mechanism)

**CONTAINER START SEQUENCE:**

```
Kubelet
  | gRPC CreateContainerRequest
  v
containerd
  | 1. Pull image (if not cached)
  | 2. Create snapshot (rootfs overlay)
  | 3. Generate config.json (OCI bundle)
  | 4. Spawn containerd-shim-runc-v2
  v
containerd-shim-runc-v2
  | 5. Call: runc create --bundle /path/bundle
  v
runc
  | 6. Read config.json
  | 7. clone(CLONE_NEWNS|CLONE_NEWPID|...)
  | 8. mount rootfs, proc, sys, dev
  | 9. setrlimit (cgroup constraints)
  | 10. set capabilities, seccomp filter
  | 11. runc start -> exec entrypoint
  | 12. runc exits
  v
Container process (PID 1 in its namespace)
  ^ parent is shim, not runc
```

**KEY FILES IN AN OCI BUNDLE:**

```
/run/containerd/io.containerd.runtime.v2.task/
  default/
    <container-id>/
      config.json    # OCI Runtime Config
      rootfs/        # Container filesystem
      log.json       # Container stdout/stderr
      shim.sock      # Shim Unix socket
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
kubectl apply -f pod.yaml
  |
  v
Kubelet: CRI call to containerd
  |
  v
containerd: image pull + snapshot
  |         ← YOU ARE HERE
  v
containerd: generate OCI bundle + spawn shim
  |
  v
shim: invoke runc create
  |
  v
runc: namespaces + cgroups + exec
  |
  v
Container process running
shim: alive, holding stdio
runc: exited (ephemeral)
```

**FAILURE PATH:**
runc fails with `permission denied` setting up a namespace (e.g., user
namespace not enabled in kernel). containerd logs the runc error.
Container stays in `ContainerCreating` state. `kubectl describe pod`
shows `failed to create containerd task: ... runc create failed`.

**WHAT CHANGES AT SCALE:**
At scale, containerd manages thousands of concurrent container lifecycle
operations. Snapshot management (overlayfs layers) becomes a performance
bottleneck if the snapshot store is not on fast storage (NVMe SSD).
containerd's `content store` (image layer cache) requires garbage
collection to prevent disk exhaustion.

---

### 💻 Code Example

```bash
# Inspect containerd state directly
# (bypasses Docker/Kubernetes abstractions)

# List all containers known to containerd
ctr --namespace k8s.io containers list

# Inspect a specific container's OCI config
ctr --namespace k8s.io containers info <id> | \
  jq '.Spec'

# View the OCI bundle config.json for a running pod
SANDBOX=$(crictl pods --name mypod -q)
CONTAINER=$(crictl ps --pod $SANDBOX -q)
BUNDLE=$(crictl inspect $CONTAINER | \
  jq -r '.info.runtimeSpec | @json' | \
  python3 -m json.tool | head -30)
echo "$BUNDLE"
```

```bash
# Trace the runc calls made by containerd for a container start
# (requires strace - use in dev/staging only)
strace -p $(pgrep containerd) -e trace=clone,unshare,\
setns -f 2>&1 | grep -E "clone|unshare|setns" | head -20

# View the seccomp profile applied to a running container
cat /proc/$(docker inspect --format='{{.State.Pid}}' \
  <container>)/status | grep Seccomp
# 0 = disabled, 1 = strict, 2 = filter (seccomp-bpf)
```

```bash
# Diagnose container startup failure
# Step 1: Check Kubelet logs
journalctl -u kubelet -n 100 | grep -i "failed\|error"

# Step 2: Check containerd logs
journalctl -u containerd -n 100 | grep -i "failed\|error"

# Step 3: Check runc error (in containerd log)
journalctl -u containerd | grep "runc\|OCI"
```

**How to test / verify correctness:**

```bash
# Verify shim survives containerd restart
# 1. Start a long-running container
kubectl run test --image=nginx

# 2. Note the pod is Running
kubectl get pod test

# 3. Restart containerd on the node
sudo systemctl restart containerd

# 4. Verify pod is still Running (not restarted)
kubectl get pod test
# RESTARTS should still be 0
```

---

### ⚖️ Comparison Table

| Component | Role | Lifetime | Manages |
|---|---|---|---|
| Kubelet | CRI caller | Node lifetime | Pod spec, CRI calls |
| containerd | High-level runtime | Daemon (persistent) | Image, snapshot, shim spawn |
| containerd-shim | Shim process | Container lifetime | stdio, exit status |
| runc | Low-level runtime | Ephemeral (exits after start) | Namespaces, cgroups, exec |
| Container process | Workload | Task-defined | Application logic |

---

### 🔁 Flow / Lifecycle

**CONTAINER LIFECYCLE PHASES:**

**Phase 1 - Image Preparation:** containerd pulls image layers from the
registry into its content store. Overlayfs snapshot created from image
layers as the container rootfs.

**Phase 2 - Bundle Generation:** containerd generates `config.json`
(OCI Runtime Config) encoding: mounts, Linux namespaces, cgroup limits,
capabilities, seccomp profile, environment variables, entrypoint.

**Phase 3 - Shim Spawn + runc Create:** containerd spawns the shim
process. Shim invokes `runc create`, which sets up all namespaces
and mounts but does not yet exec the entrypoint. Container is in
`created` state.

**Phase 4 - runc Start:** containerd signals the shim to call
`runc start`. runc exec's the container entrypoint. runc then exits.
Container process is now running; shim is its parent.

**Phase 5 - Running:** Container process runs. Shim holds stdio and
monitors exit. containerd tracks container state via shim's Unix socket.

**Phase 6 - Exit + Cleanup:** Container process exits. Shim reports
exit code to containerd. containerd performs cleanup: snapshot deletion,
network teardown, resource release. Shim exits.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Restarting containerd restarts all containers" | The shim model ensures containers survive containerd restarts. containerd reconnects to running shims on startup. |
| "runc is always running inside the container" | runc is ephemeral - it sets up the container and exits. The container process is not runc; it is the entrypoint exec'd by runc. |
| "Docker and containerd are the same" | Docker uses containerd as its backend (since Docker 1.11). They share the same underlying runtime, but Docker adds additional features (Compose, BuildKit, Docker CLI) on top. |
| "OCI config.json is user-visible configuration" | config.json is generated by containerd from pod spec, not directly user-editable. It is the internal contract between containerd and runc. |
| "containerd and CRI-O use different low-level runtimes" | Both containerd and CRI-O use runc as the default low-level runtime. They differ in daemon architecture, not in how containers are actually isolated. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: runc OOM Kill During Container Start**
**Symptom:** Container stuck in `ContainerCreating`. `kubectl describe`
shows `OOMKilled`. containerd log shows runc process was OOM killed.

**Root Cause:** The node has insufficient memory to start runc itself
(not the container memory limit). Rare but occurs under extreme node
memory pressure.

**Diagnostic:**

```bash
# Check node memory
kubectl describe node <node> | grep -A 5 Allocatable

# Check OOM events in kernel log
dmesg | grep -i "oom\|killed" | tail -20

# Check containerd log for runc failure
journalctl -u containerd | grep "runc create failed"
```

**Fix:** Cordon and drain the memory-pressured node. Add resource
reservations for system processes (`--kube-reserved`, `--system-reserved`
kubelet flags).

**Prevention:** Set `--kube-reserved` and `--system-reserved` to prevent
Kubernetes from allocating all node memory to pods.

---

**Failure Mode 2: Snapshot Disk Exhaustion**
**Symptom:** New containers fail to start with `no space left on device`
from containerd. Existing containers are unaffected.

**Root Cause:** containerd's overlayfs snapshot store (usually
`/var/lib/containerd`) is full. Old unused snapshots and image layers
accumulate over time without garbage collection.

**Diagnostic:**

```bash
# Check containerd storage
du -sh /var/lib/containerd/

# List unused snapshots (can be garbage collected)
ctr --namespace k8s.io snapshots list | \
  grep -v "sha256" | wc -l

# Check content store size
ctr --namespace k8s.io content ls | \
  awk '{sum += $3} END {print sum " bytes"}'
```

**Fix:** Run containerd garbage collection:
`ctr --namespace k8s.io images prune --all`

**Prevention:** Schedule periodic `crictl rmi --prune` to remove unused
images. Monitor `/var/lib/containerd` disk usage with alerts at 80%.

---

**Failure Mode 3: Container Escape via runc CVE (Security)**
**Symptom:** Post-breach forensics shows host filesystem was accessed
from inside a container. Attacker ran `docker exec` or `kubectl exec`
and wrote to the host runc binary.

**Root Cause:** Unpatched runc (CVE-2019-5736 or similar). An attacker
with exec access to a container can overwrite the runc binary, which
runs as root on the host. Next runc invocation (container start) runs
attacker code as root on the host.

**Diagnostic:**

```bash
# Check runc version (must be >= 1.0.0-rc8 for CVE-2019-5736)
runc --version

# Check if runc binary has been modified
rpm -V runc || dpkg -V runc
# Any output indicates file modification

# Check file integrity
sha256sum /usr/bin/runc
```

**Fix:** Update runc to patched version. Audit for signs of compromise
(unexpected processes, modified binaries, new cron jobs on hosts).

**Prevention:** Keep runc and containerd updated. Enable seccomp and
AppArmor profiles that restrict the container's ability to open host
filesystem paths via `/proc/self/exe`.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[CTR-018 - Linux Namespaces]] - the kernel isolation primitive runc uses
- [[CTR-010 - Cgroups]] - the resource constraint primitive runc uses
- [[CTR-021 - containerd]] - the high-level runtime
- [[CTR-046 - Container Runtime Interface (CRI)]] - the API layer above containerd

**Builds On This (learn these next):**

- [[CTR-053 - Linux Namespace and Cgroup Architecture]] - deeper kernel internals

**Alternatives / Comparisons:**

- [[CTR-051 - Multi-Runtime Container Strategy (containerd, CRI-O)]] - runtime choices
- [[CTR-054 - Container Image Format Design (OCI)]] - the OCI image spec that feeds containerd

---

### 📌 Quick Reference Card

```
┌────────────────────────────────────────────────────┐
│ WHAT IT IS  │ Two-layer runtime: containerd + runc │
│ PROBLEM     │ Opaque container start failures     │
│ KEY INSIGHT │ runc is ephemeral; shim is permanent │
│ USE WHEN    │ Debugging container startup failures │
│ AVOID WHEN  │ N/A - always relevant for diagnosis  │
│ TRADE-OFF   │ Two-layer complexity vs. pluggability│
│ ONE-LINER   │ containerd manages; runc isolates   │
│ NEXT EXPLORE│ CTR-053 Namespace/Cgroup Architecture│
└────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. containerd manages image, snapshot, and lifecycle; runc sets up
   namespaces and cgroups, exec's the process, then exits.
2. The shim process keeps containers alive through containerd restarts -
   restarting containerd does not restart containers.
3. runc CVEs are critical: runc runs as root on the host and sets up
   container isolation - a runc vulnerability can break container boundaries.

**Interview one-liner:**
"A container start calls containerd (image pull, snapshot, OCI bundle),
which spawns a shim that calls runc (namespace + cgroup + exec), then
runc exits; the shim holds the container's stdio and survives containerd
restarts, so upgrading containerd does not restart running containers."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Ephemeral executors and persistent supervisors serve different roles.
runc is an ephemeral executor: it performs a complex setup task and
exits. The shim is a persistent supervisor: it holds state (file
descriptors) and monitors the long-lived process. Separating the setup
executor from the monitoring supervisor enables both to be simpler and
more reliable than a single long-lived setup-and-monitor process.

**Where else this pattern appears:**

- **SSH session handling:** `sshd` spawns a child process per session.
  The child is the session handler (ephemeral for session duration).
  The parent `sshd` continues accepting connections. Same parent/child
  lifecycle separation.
- **Web server worker models:** nginx forks worker processes. The master
  process manages worker lifecycle; workers handle requests and can be
  replaced without restarting the master. containerd/shim mirrors this.
- **Database connection setup:** pg_hba.conf authentication is checked
  by the `postmaster` (containerd equivalent) and a backend process is
  forked to handle the connection (shim equivalent). The postmaster does
  not handle queries directly.

---

### 💡 The Surprising Truth

runc was not written by Docker or any single company. It was extracted
from Docker's `libcontainer` and donated to the OCI as the reference
implementation of the OCI Runtime Specification - which means every
container runtime (containerd, CRI-O, Podman) in production today
defaults to calling the same runc binary to actually start containers.
Google's GKE, Amazon's EKS, and Microsoft's AKS all ultimately call
runc to set up container isolation. Despite this, runc's codebase is
fewer than 50,000 lines of Go - one of the most critical pieces of
infrastructure in the industry, running billions of container instances
daily, maintained by a relatively small group of contributors.

---

### 🧠 Think About This Before We Continue

**Q1 (D - Root Cause):** A container is stuck in `ContainerCreating`
for 10 minutes. `kubectl describe pod` shows the event `failed to create
containerd task: failed to create shim task: OCI runtime create failed:
runc create failed: unable to start container process: error during
container init: error mounting "/dev/sda1" to rootfs at "/data":
mount /dev/sda1:/data (via /proc/self/fd/6), flags: 0x5001: not a
directory`. What is the root cause and where in the startup sequence
did it fail?
*Hint:* The error is in Phase 3 (runc Create, mount setup). The OCI
bundle `config.json` specifies a mount that is invalid. Which Kubernetes
spec field generates mount entries in config.json?

**Q2 (E - First Principles):** Why does runc use `clone(2)` with
`CLONE_NEWNS | CLONE_NEWPID | CLONE_NEWNET | CLONE_NEWUTS |
CLONE_NEWIPC` instead of `fork(2)` to create the container process?
What does each CLONE flag achieve, and why must they all be set in
a single `clone` call?
*Hint:* `fork` creates a child in the same namespaces as the parent.
`clone` with namespace flags creates the child in new namespaces
atomically. What would happen if namespaces were created sequentially
rather than atomically?

**Q3 (A - System Interaction):** A Pod has `terminationGracePeriodSeconds:
30`. When `kubectl delete pod` is issued, the sequence is: Kubernetes
sends SIGTERM to PID 1 in the container, waits 30 seconds, then sends
SIGKILL. Trace this signal delivery from Kubernetes API server through
containerd to the container process. Which component sends the SIGTERM,
and which sends the SIGKILL?
*Hint:* The Kubelet calls the CRI `StopContainer` with a timeout.
containerd calls the shim. The shim sends SIGTERM to the container PID.
After the timeout, Kubelet calls `StopContainer` again with timeout=0,
which triggers SIGKILL. Which component actually sends the signal to
the container process?